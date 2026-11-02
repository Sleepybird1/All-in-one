"""Align managed recipe phases and display order after the v3 redesign passes.

Recipe waves are intentionally authored in small, understandable modules.  A
later wave can, however, move a machine or component farther into progression
without also moving every recipe that consumes it.  This in-memory post-pass
derives exact dependencies from the finished manifest and makes those moves
deterministically:

* every exact managed item output has one and only one owner;
* exact item inputs, shaped/mechanical grid keys, sequence ingredients, and
  selected machine blocks become inferred producer dependencies;
* explicit ``depends_on`` recipe IDs (or managed output item IDs) are included;
* consumers are promoted until no dependency is in a later phase; and
* cards in each phase receive a deterministic topological order in increments
  of ten.

Tags are deliberately not resolved here.  A tag can contain many stock items
and therefore cannot prove a dependency on one managed producer.  Fluids and
chemicals are likewise excluded: this pass aligns managed *item* manufacturing
and does not attempt to replace the pack's chemistry reachability audits.

``apply`` mutates only the supplied seed object.  It performs no file or live
instance I/O and is idempotent: applying it again leaves the manifest exactly
unchanged.
"""

from __future__ import annotations

from collections import defaultdict
import heapq
import re
from typing import Any, Iterable, Iterator, Mapping, MutableMapping


Recipe = MutableMapping[str, Any]


ESTABLISHED_PHASE_ORDER: tuple[str, ...] = (
    "Mechanical Foundations",
    "Steam & Brass",
    "Steel & Petroleum",
    "Electrical Manufacturing",
    "Digital Logistics",
    "Mekanized Industry",
    "High-Energy Grid",
    "Nuclear Engineering",
    "Post-Nuclear Megaprojects",
    "Orbital Engineering",
    "Planetary Industry",
    "Outer System Industry",
    "Interstellar Escape",
)


_ITEM_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
_COUNTED_ITEM = re.compile(
    r"^\s*(?:\d+\s*x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)\s*$"
)
_VAT_MACHINE_BY_MODE = {
    "cast_iron": "tfmg:cast_iron_chemical_vat",
    "steel": "tfmg:steel_chemical_vat",
    "firebrick": "tfmg:fireproof_chemical_vat",
}


def _phase_name(value: Any) -> str | None:
    """Read a phase name from one common ordered-phase declaration."""

    if isinstance(value, str):
        name = value.strip()
        return name or None
    if isinstance(value, Mapping):
        for field in ("name", "phase", "id", "label"):
            candidate = value.get(field)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    return None


def _phase_order(data: Mapping[str, Any]) -> tuple[str, ...]:
    """Return the manifest's explicit order or the established pack order.

    ``phase_order`` is the current seed schema.  ``phases`` is accepted for
    forward/backward compatibility and can be either an ordered array or an
    insertion-ordered object.  An explicitly present but malformed declaration
    fails closed rather than silently changing progression.
    """

    source: Any = None
    source_name = ""
    if "phase_order" in data:
        source = data.get("phase_order")
        source_name = "phase_order"
    elif "phases" in data:
        source = data.get("phases")
        source_name = "phases"

    if source is None:
        return ESTABLISHED_PHASE_ORDER

    names: list[str] = []
    if isinstance(source, Mapping):
        # Phase metadata maps are ordered by their phase-name keys in the JSON
        # seed.  A list is still preferred when the schema provides one.
        names = [str(key).strip() for key in source if str(key).strip()]
    elif isinstance(source, (list, tuple)):
        for entry in source:
            name = _phase_name(entry)
            if name is None:
                raise ValueError(
                    f"{source_name} contains an invalid phase declaration: {entry!r}"
                )
            names.append(name)
    else:
        raise ValueError(f"{source_name} must be an ordered array or object")

    if not names:
        raise ValueError(f"{source_name} does not declare any phases")
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"duplicate phases in {source_name}: {duplicates}")
    return tuple(names)


def _item_id(value: Any) -> str | None:
    """Return one exact item ID from a managed stack declaration."""

    if isinstance(value, str):
        raw = value.strip()
        if not raw or raw.startswith("#"):
            return None
        match = _COUNTED_ITEM.fullmatch(raw)
        return match.group(1) if match else None

    if not isinstance(value, Mapping):
        return None

    kind = str(value.get("kind", "ITEM")).upper()
    if kind != "ITEM":
        return None
    identifier = value.get("id", value.get("item"))
    if not isinstance(identifier, str):
        return None
    identifier = identifier.strip()
    if identifier.startswith("#") or not _ITEM_ID.fullmatch(identifier):
        return None
    return identifier


def _items_in(value: Any) -> Iterator[str]:
    """Recursively read exact item stacks from a declared slot container."""

    if isinstance(value, str):
        identifier = _item_id(value)
        if identifier is not None:
            yield identifier
        return

    if isinstance(value, Mapping):
        # A slot-like object is atomic.  In particular, never recurse into the
        # ``id`` of a FLUID/CHEMICAL/TAG slot and accidentally treat it as item.
        if any(field in value for field in ("kind", "id", "item", "tag")):
            identifier = _item_id(value)
            if identifier is not None:
                yield identifier
            return
        for nested in value.values():
            yield from _items_in(nested)
        return

    if isinstance(value, (list, tuple, set)):
        for nested in value:
            yield from _items_in(nested)


def recipe_output_items(recipe: Mapping[str, Any]) -> frozenset[str]:
    """Extract exact item outputs from ``output``, ``results``, and ``outputs``."""

    found: set[str] = set()
    for field in ("output", "results", "outputs"):
        if field in recipe:
            found.update(_items_in(recipe[field]))
    return frozenset(found)


def recipe_input_items(recipe: Mapping[str, Any]) -> frozenset[str]:
    """Extract exact managed-item dependency candidates from one recipe.

    The selected Create Encased machine is a physical progression dependency,
    both for normal machine recipes and for each sequenced-assembly operation.
    """

    found: set[str] = set()
    for field in ("input", "inputs", "ingredients", "key", "machine"):
        if field in recipe:
            found.update(_items_in(recipe[field]))

    grid = recipe.get("grid")
    if isinstance(grid, Mapping) and "key" in grid:
        found.update(_items_in(grid["key"]))

    steps = recipe.get("steps", ())
    if isinstance(steps, (list, tuple)):
        for step in steps:
            if not isinstance(step, Mapping):
                continue
            for field in ("ingredient", "machine"):
                if field in step:
                    found.update(_items_in(step[field]))

    # KJSGen's TFMG Chemical Vat card stores its required multiblock class as a
    # mode rather than an item slot.  Resolve that selector to the physical vat
    # so semiconductor and planetary chemistry cannot precede their vessel.
    vat_mode = recipe.get("vat_mode")
    if isinstance(vat_mode, str):
        machine_item = _VAT_MACHINE_BY_MODE.get(vat_mode.strip().lower())
        if machine_item is not None:
            found.add(machine_item)
    return frozenset(found)


def _recipes(data: Mapping[str, Any]) -> list[Recipe]:
    rows = data.get("recipes")
    if not isinstance(rows, list):
        raise ValueError("managed recipe seed must define a recipes array")
    if any(not isinstance(row, MutableMapping) for row in rows):
        raise ValueError("every managed recipe must be an object")
    return rows  # type: ignore[return-value]


def _recipe_index(recipes: Iterable[Recipe]) -> dict[str, Recipe]:
    by_id: dict[str, Recipe] = {}
    duplicates: set[str] = set()
    missing: list[int] = []
    for index, recipe in enumerate(recipes):
        recipe_id = recipe.get("id")
        if not isinstance(recipe_id, str) or not recipe_id.strip():
            missing.append(index)
            continue
        recipe_id = recipe_id.strip()
        if recipe_id in by_id:
            duplicates.add(recipe_id)
        by_id[recipe_id] = recipe
    if missing:
        raise ValueError(f"managed recipes missing IDs at indexes: {missing[:20]}")
    if duplicates:
        raise ValueError(f"duplicate managed recipe IDs: {sorted(duplicates)}")
    return by_id


def _output_owners(recipes: Iterable[Recipe]) -> dict[str, str]:
    claims: dict[str, list[str]] = defaultdict(list)
    for recipe in recipes:
        recipe_id = str(recipe["id"])
        for output in recipe_output_items(recipe):
            claims[output].append(recipe_id)

    duplicates = {
        output: sorted(owners)
        for output, owners in claims.items()
        if len(owners) > 1
    }
    if duplicates:
        details = "; ".join(
            f"{output} <- {', '.join(owners)}"
            for output, owners in sorted(duplicates.items())
        )
        raise ValueError(f"duplicate exact managed output owners: {details}")
    return {output: owners[0] for output, owners in claims.items()}


def _explicit_dependency_tokens(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        token = value.strip()
        if token:
            yield token
        return
    if isinstance(value, Mapping):
        for field in ("recipe", "recipe_id", "id", "output", "item"):
            token = value.get(field)
            if isinstance(token, str) and token.strip():
                yield token.strip()
                return
        return
    if isinstance(value, (list, tuple, set)):
        for nested in value:
            yield from _explicit_dependency_tokens(nested)


def _dependency_graph(
    recipes: Iterable[Recipe],
    by_id: Mapping[str, Recipe],
    owners: Mapping[str, str],
) -> tuple[dict[str, set[str]], set[tuple[str, str]], set[tuple[str, str]], list[dict[str, str]]]:
    """Return predecessor sets plus inferred/explicit edge diagnostics."""

    predecessors: dict[str, set[str]] = {recipe_id: set() for recipe_id in by_id}
    inferred_edges: set[tuple[str, str]] = set()
    explicit_edges: set[tuple[str, str]] = set()
    unresolved: list[dict[str, str]] = []

    for recipe in recipes:
        consumer = str(recipe["id"])
        for item in recipe_input_items(recipe):
            producer = owners.get(item)
            if producer is not None:
                predecessors[consumer].add(producer)
                inferred_edges.add((producer, consumer))

        for token in _explicit_dependency_tokens(recipe.get("depends_on", ())):
            producer = token if token in by_id else None
            if producer is None:
                item = _item_id(token)
                if item is not None:
                    producer = owners.get(item)
            if producer is None:
                unresolved.append({"consumer": consumer, "dependency": token})
                continue
            predecessors[consumer].add(producer)
            explicit_edges.add((producer, consumer))

    unresolved.sort(key=lambda row: (row["consumer"], row["dependency"]))
    return predecessors, inferred_edges, explicit_edges, unresolved


def _validate_phases(
    recipes: Iterable[Recipe],
    phases: tuple[str, ...],
    phase_by_node: Mapping[str, Any],
) -> None:
    known = set(phases)
    unknown_recipes: list[str] = []
    for recipe in recipes:
        phase = recipe.get("phase")
        if not isinstance(phase, str) or phase not in known:
            unknown_recipes.append(f"{recipe.get('id', '<missing>')}={phase!r}")
    unknown_nodes = sorted(
        f"{node}={phase!r}"
        for node, phase in phase_by_node.items()
        if phase not in known
    )
    if unknown_recipes or unknown_nodes:
        details: list[str] = []
        if unknown_recipes:
            details.append("recipes: " + ", ".join(sorted(unknown_recipes)[:40]))
        if unknown_nodes:
            details.append("phase_by_node: " + ", ".join(unknown_nodes[:40]))
        raise ValueError("unknown managed progression phases; " + "; ".join(details))


def _old_order_key(recipe: Mapping[str, Any]) -> tuple[float, str]:
    """Return an input-state-independent tie breaker for topological sorting.

    Individual design modules intentionally restore their authored ``order``
    whenever they upsert a card, while untouched legacy cards retain the last
    aligned value.  Reusing that mixed state here makes the serialized manifest
    drift on every full generator run even though its dependency graph is
    unchanged.  Recipe IDs are stable design identities, so they are the only
    safe tie breaker between otherwise independent cards.
    """

    return 0.0, str(recipe["id"])


def _find_cycle(
    nodes: set[str],
    successors: Mapping[str, set[str]],
    key_by_id: Mapping[str, tuple[float, str]],
) -> list[str]:
    """Return one deterministic directed cycle from a failed phase sort."""

    state: dict[str, int] = {}
    stack: list[str] = []
    stack_index: dict[str, int] = {}

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack_index[node] = len(stack)
        stack.append(node)
        for child in sorted(successors.get(node, ()), key=key_by_id.__getitem__):
            if child not in nodes:
                continue
            if state.get(child, 0) == 0:
                found = visit(child)
                if found is not None:
                    return found
            elif state.get(child) == 1:
                return stack[stack_index[child] :] + [child]
        stack.pop()
        stack_index.pop(node, None)
        state[node] = 2
        return None

    for node in sorted(nodes, key=key_by_id.__getitem__):
        if state.get(node, 0) == 0:
            found = visit(node)
            if found is not None:
                return found
    return []


def _topological_phase_order(
    phase: str,
    members: list[str],
    predecessors: Mapping[str, set[str]],
    by_id: Mapping[str, Recipe],
) -> list[str]:
    member_set = set(members)
    key_by_id = {recipe_id: _old_order_key(by_id[recipe_id]) for recipe_id in members}
    indegree = {recipe_id: 0 for recipe_id in members}
    successors: dict[str, set[str]] = {recipe_id: set() for recipe_id in members}
    for consumer in members:
        for producer in predecessors[consumer]:
            if producer not in member_set:
                continue
            if consumer not in successors[producer]:
                successors[producer].add(consumer)
                indegree[consumer] += 1

    ready: list[tuple[tuple[float, str], str]] = [
        (key_by_id[recipe_id], recipe_id)
        for recipe_id in members
        if indegree[recipe_id] == 0
    ]
    heapq.heapify(ready)
    ordered: list[str] = []
    while ready:
        _, recipe_id = heapq.heappop(ready)
        ordered.append(recipe_id)
        for consumer in sorted(successors[recipe_id], key=key_by_id.__getitem__):
            indegree[consumer] -= 1
            if indegree[consumer] == 0:
                heapq.heappush(ready, (key_by_id[consumer], consumer))

    if len(ordered) != len(members):
        remaining = {recipe_id for recipe_id in members if indegree[recipe_id] > 0}
        cycle = _find_cycle(remaining, successors, key_by_id)
        rendered = " -> ".join(cycle) if cycle else ", ".join(sorted(remaining))
        raise ValueError(f"managed recipe dependency cycle in {phase}: {rendered}")
    return ordered


def apply(data: dict[str, Any]) -> dict[str, Any]:
    """Promote dependent recipes and assign deterministic within-phase order."""

    recipes = _recipes(data)
    by_id = _recipe_index(recipes)
    owners = _output_owners(recipes)
    phases = _phase_order(data)
    phase_rank = {phase: index for index, phase in enumerate(phases)}
    node_map_raw = data.get("phase_by_node", {})
    if node_map_raw is None:
        node_map_raw = {}
    if not isinstance(node_map_raw, Mapping):
        raise ValueError("phase_by_node must be an object when present")
    phase_by_node: Mapping[str, Any] = node_map_raw
    _validate_phases(recipes, phases, phase_by_node)

    predecessors, inferred_edges, explicit_edges, unresolved = _dependency_graph(
        recipes, by_id, owners
    )

    original_phase = {recipe_id: str(recipe["phase"]) for recipe_id, recipe in by_id.items()}
    removed_nodes: list[dict[str, str]] = []
    changed = True
    while changed:
        changed = False
        for consumer in sorted(by_id):
            recipe = by_id[consumer]
            current_phase = str(recipe["phase"])
            current_rank = phase_rank[current_phase]
            required_rank = max(
                (phase_rank[str(by_id[producer]["phase"])] for producer in predecessors[consumer]),
                default=current_rank,
            )
            if required_rank <= current_rank:
                continue
            new_phase = phases[required_rank]
            recipe["phase"] = new_phase
            node = recipe.get("node")
            if isinstance(node, str):
                node_phase = phase_by_node.get(node)
                if node_phase is not None and node_phase != new_phase:
                    recipe.pop("node", None)
                    removed_nodes.append(
                        {"id": consumer, "node": node, "node_phase": str(node_phase)}
                    )
            changed = True

    # A dependency can never remain in a later phase after the fixed point.
    violations = sorted(
        (producer, consumer)
        for consumer, producer_ids in predecessors.items()
        for producer in producer_ids
        if phase_rank[str(by_id[producer]["phase"])]
        > phase_rank[str(by_id[consumer]["phase"])]
    )
    if violations:
        raise AssertionError(f"phase alignment failed to converge: {violations[:20]}")

    previous_orders = {recipe_id: recipe.get("order") for recipe_id, recipe in by_id.items()}
    phase_counts: dict[str, int] = {}
    for phase in phases:
        members = [
            recipe_id
            for recipe_id, recipe in by_id.items()
            if recipe.get("phase") == phase
        ]
        phase_counts[phase] = len(members)
        ordered = _topological_phase_order(phase, members, predecessors, by_id)
        for position, recipe_id in enumerate(ordered, start=1):
            by_id[recipe_id]["order"] = position * 10

    promotions = [
        {
            "id": recipe_id,
            "from": original_phase[recipe_id],
            "to": str(by_id[recipe_id]["phase"]),
        }
        for recipe_id in sorted(by_id)
        if original_phase[recipe_id] != by_id[recipe_id]["phase"]
    ]
    reordered = sorted(
        recipe_id
        for recipe_id, recipe in by_id.items()
        if previous_orders[recipe_id] != recipe.get("order")
    )

    all_edges = inferred_edges | explicit_edges
    return {
        "status": "PASS",
        "recipe_count": len(recipes),
        "managed_item_output_count": len(owners),
        "dependency_edge_count": len(all_edges),
        "inferred_dependency_edge_count": len(inferred_edges),
        "explicit_dependency_edge_count": len(explicit_edges),
        "unresolved_explicit_dependency_count": len(unresolved),
        "unresolved_explicit_dependencies": unresolved,
        "promoted_recipe_count": len(promotions),
        "promotions": promotions,
        "removed_stale_node_count": len(removed_nodes),
        "removed_stale_nodes": sorted(removed_nodes, key=lambda row: row["id"]),
        "reordered_recipe_count": len(reordered),
        "reordered_recipe_ids": reordered,
        "phase_recipe_counts": phase_counts,
    }
