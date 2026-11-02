#!/usr/bin/env python3
"""Static quality audit for the hand-authored recipe-design-v2 seed.

This checker deliberately works on ``managed_recipe_overhaul.seed.json``
before the manifest/compiler stages.  It can also apply one or more pending
recipe modules in memory, which makes a coverage wave reviewable without
writing the seed or touching the live Minecraft instance.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from build_managed_recipe_manifest import normalize_machine_families
from generate_managed_recipe_overhaul import expand_machine_family


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_CATALOG = (
    ROOT.parents[1] / "outputs" / "recipe-catalog-current" / "recipe_catalog.sqlite"
)

RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
COUNTED_ITEM = re.compile(r"^\s*\d+x\s+([a-z0-9_.-]+:[a-z0-9_./-]+)\s*$")

# Fully occupied 5x5 grids are reserved for assemblies whose actual bulk or
# internal density justifies all twenty-five slots.  Any future addition must
# be consciously reviewed here instead of silently reintroducing a gate ring.
JUSTIFIED_FULL_FIVE_BY_FIVE = {
    "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker",
    "industrial_colonies:advanced_ae/reaction_chamber",
    "industrial_colonies:world_loading/chunk_controller",
    "industrial_colonies:mekanism/storage/advanced_energy_cube",
    "industrial_colonies:mekanism/storage/elite_energy_cube",
    "industrial_colonies:mekanism/storage/ultimate_energy_cube",
    # Explicitly reviewed physical machine from the final rejection pass.
    "industrial_colonies:interstellar/warp_drive",
}


def exact_item(value: Any) -> str | None:
    """Return a concrete item ID, ignoring tags, fluids, and chemicals."""

    if isinstance(value, str):
        raw = value.strip()
        if not raw or raw.startswith("#"):
            return None
        counted = COUNTED_ITEM.fullmatch(raw)
        identifier = counted.group(1) if counted else raw
        return identifier if RESOURCE_ID.fullmatch(identifier) else None
    if not isinstance(value, Mapping):
        return None
    kind = str(value.get("kind", "ITEM")).upper()
    if kind != "ITEM":
        return None
    identifier = value.get("id") or value.get("item")
    if not isinstance(identifier, str) or identifier.startswith("#"):
        return None
    return identifier if RESOURCE_ID.fullmatch(identifier) else None


def recipe_outputs(recipe: Mapping[str, Any]) -> list[str]:
    outputs: list[str] = []
    primary = exact_item(recipe.get("output"))
    if primary:
        outputs.append(primary)
    # Older recipe waves use both ``results`` and ``outputs`` for typed result
    # lists.  Treat both as producers so dependency, duplicate-output, and
    # catalog checks cannot silently miss batch recipes such as TFMG
    # capacitors and transistors.
    for field in ("results", "outputs"):
        for result in recipe.get(field, []):
            identifier = exact_item(result)
            if identifier:
                outputs.append(identifier)
    return outputs


def _items_from(value: Any) -> Iterable[str]:
    if isinstance(value, list):
        for entry in value:
            yield from _items_from(entry)
        return
    identifier = exact_item(value)
    if identifier:
        yield identifier


def recipe_inputs(recipe: Mapping[str, Any]) -> list[str]:
    """Collect item prerequisites, including exact processing machines."""

    inputs: list[str] = []
    for field in (
        "input",
        "inputs",
        "ingredients",
        "input1",
        "input2",
        "left",
        "right",
        "gas",
        "infusion",
        "machine",
    ):
        inputs.extend(_items_from(recipe.get(field)))
    key = recipe.get("key")
    if isinstance(key, Mapping):
        for value in key.values():
            inputs.extend(_items_from(value))
    for step in recipe.get("steps", []):
        if not isinstance(step, Mapping):
            continue
        inputs.extend(_items_from(step.get("ingredient")))
        inputs.extend(_items_from(step.get("machine")))
    return inputs


def recipe_material_inputs(recipe: Mapping[str, Any]) -> list[str]:
    """Collect consumed items without treating the selected machine as material.

    Machine selectors describe where a recipe runs; they are not consumed by
    the recipe.  Keeping them out of the ordering check prevents the UI card
    order from conflating a manufacturing environment with a bill-of-material
    prerequisite.
    """

    inputs: list[str] = []
    for field in (
        "input",
        "inputs",
        "ingredients",
        "input1",
        "input2",
        "left",
        "right",
        "gas",
        "infusion",
    ):
        inputs.extend(_items_from(recipe.get(field)))
    key = recipe.get("key")
    if isinstance(key, Mapping):
        for value in key.values():
            inputs.extend(_items_from(value))
    for step in recipe.get("steps", []):
        if isinstance(step, Mapping):
            inputs.extend(_items_from(step.get("ingredient")))
    return inputs


def expanded_recipes(seed: Mapping[str, Any]) -> list[dict[str, Any]]:
    recipes = [dict(recipe) for recipe in seed.get("recipes", [])]
    phases = seed.get("phase_order", [])
    phase_index = {phase: index for index, phase in enumerate(phases)}
    families = normalize_machine_families(seed.get("machine_families", []), phase_index)
    for family in families:
        recipes.extend(dict(recipe) for recipe in expand_machine_family(family))
    return recipes


def canonical_grid_signature(recipe: Mapping[str, Any]) -> tuple[Any, ...] | None:
    if recipe.get("type") not in {"shaped", "mechanical_crafting"}:
        return None
    pattern = recipe.get("pattern")
    key = recipe.get("key")
    if not isinstance(pattern, list) or not isinstance(key, Mapping):
        return None
    canonical = tuple(
        tuple(exact_item(key.get(symbol)) or str(key.get(symbol)) for symbol in row)
        for row in pattern
    )
    return (recipe.get("type"), canonical)


def raw_pattern(recipe: Mapping[str, Any]) -> tuple[str, ...] | None:
    pattern = recipe.get("pattern")
    if recipe.get("type") not in {"shaped", "mechanical_crafting"} or not isinstance(pattern, list):
        return None
    return tuple(str(row) for row in pattern)


def sequence_signature(recipe: Mapping[str, Any]) -> tuple[Any, ...] | None:
    if recipe.get("type") != "sequenced_assembly":
        return None
    steps: list[tuple[Any, ...]] = []
    for step in recipe.get("steps", []):
        if not isinstance(step, Mapping):
            continue
        steps.append(
            (
                step.get("op"),
                exact_item(step.get("ingredient")) or str(step.get("ingredient", "")),
                exact_item(step.get("machine")) or str(step.get("machine", "")),
            )
        )
    return (
        exact_item(recipe.get("input")),
        recipe.get("loops", 1),
        tuple(steps),
    )


def find_cycles(nodes: Iterable[str], outgoing: Mapping[str, set[str]]) -> list[list[str]]:
    color: dict[str, int] = {}
    stack: list[str] = []
    cycles: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for child in sorted(outgoing.get(node, set())):
            state = color.get(child, 0)
            if state == 0:
                visit(child)
            elif state == 1:
                start = stack.index(child)
                body = stack[start:]
                rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
                identity = min(rotations)
                if identity not in seen:
                    seen.add(identity)
                    cycles.append(body + [child])
        stack.pop()
        color[node] = 2

    for node in sorted(nodes):
        if color.get(node, 0) == 0:
            visit(node)
    return cycles


def catalog_sets(path: Path) -> tuple[set[str], set[str]]:
    if not path.is_file():
        return set(), set()
    connection = sqlite3.connect(path)
    try:
        item_ids = {
            row[0]
            for row in connection.execute("SELECT item_id FROM items")
            if isinstance(row[0], str)
        }
        item_ids.update(
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT resource_id FROM recipe_refs "
                "WHERE kind IN ('item', 'item_tag', 'result', 'ingredient')"
            )
            if isinstance(row[0], str) and RESOURCE_ID.fullmatch(row[0])
        )
        recipe_ids = {
            row[0]
            for row in connection.execute("SELECT recipe_id FROM recipes")
            if isinstance(row[0], str)
        }
        return item_ids, recipe_ids
    finally:
        connection.close()


def catalog_output_producers(path: Path) -> dict[str, set[str]]:
    """Return exact stock recipe owners for each concrete catalog output."""

    if not path.is_file():
        return {}
    connection = sqlite3.connect(path)
    try:
        producers: defaultdict[str, set[str]] = defaultdict(set)
        for recipe_id, outputs in connection.execute(
            "SELECT recipe_id, outputs FROM recipes"
        ):
            if not isinstance(recipe_id, str) or not isinstance(outputs, str):
                continue
            for output in outputs.split("|"):
                identifier = output.strip()
                if RESOURCE_ID.fullmatch(identifier):
                    producers[identifier].add(recipe_id)
        return dict(producers)
    finally:
        connection.close()


def grouped_duplicates(values: Iterable[tuple[Any, str]]) -> list[list[str]]:
    groups: defaultdict[Any, list[str]] = defaultdict(list)
    for value, identity in values:
        if value is not None:
            groups[value].append(identity)
    return [identities for identities in groups.values() if len(identities) > 1]


def audit(seed: Mapping[str, Any], catalog: Path) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    phases = seed.get("phase_order", [])
    phase_index = {phase: index for index, phase in enumerate(phases)}
    phase_by_node = seed.get("phase_by_node", {})
    recipes = expanded_recipes(seed)
    explicit_ids = {
        str(recipe.get("id")) for recipe in seed.get("recipes", []) if isinstance(recipe, Mapping)
    }

    identities = [str(recipe.get("id")) for recipe in recipes]
    for identity, count in Counter(identities).items():
        if count > 1:
            errors.append(f"duplicate managed recipe ID: {identity} ({count} copies)")
    by_id = {str(recipe.get("id")): recipe for recipe in recipes}

    for recipe in recipes:
        identity = str(recipe.get("id"))
        phase = recipe.get("phase")
        if phase not in phase_index:
            errors.append(f"{identity}: unknown phase {phase!r}")
        node = recipe.get("node")
        if node is not None and phase_by_node.get(node) != phase:
            errors.append(
                f"{identity}: node/phase mismatch {node!r} maps to "
                f"{phase_by_node.get(node)!r}, recipe uses {phase!r}"
            )
        for dependency in recipe.get("depends_on", []):
            if dependency not in by_id:
                errors.append(f"{identity}: unknown depends_on recipe {dependency}")

        pattern = recipe.get("pattern")
        recipe_type = recipe.get("type")
        if recipe_type == "shaped":
            if (
                not isinstance(pattern, list)
                or len(pattern) != 3
                or any(not isinstance(row, str) or len(row) != 3 for row in pattern)
            ):
                errors.append(f"{identity}: shaped pattern must be explicitly padded to 3x3")
        elif recipe_type == "mechanical_crafting":
            if not isinstance(pattern, list) or not pattern:
                errors.append(f"{identity}: mechanical-crafting pattern must be nonempty")
            elif any(not isinstance(row, str) for row in pattern):
                errors.append(f"{identity}: mechanical-crafting pattern rows must be strings")
            elif len({len(row) for row in pattern}) != 1:
                errors.append(f"{identity}: mechanical-crafting pattern is ragged")
        if recipe_type in {"shaped", "mechanical_crafting"} and isinstance(pattern, list):
            key = recipe.get("key")
            if not isinstance(key, Mapping):
                errors.append(f"{identity}: grid recipe key must be an object")
            elif all(isinstance(row, str) for row in pattern):
                used = {symbol for row in pattern for symbol in row if symbol != " "}
                declared = {str(symbol) for symbol in key}
                if used != declared:
                    errors.append(
                        f"{identity}: pattern/key mismatch; used={sorted(used)}, "
                        f"declared={sorted(declared)}"
                    )

    producers: defaultdict[str, list[str]] = defaultdict(list)
    for recipe in recipes:
        for output in recipe_outputs(recipe):
            producers[output].append(str(recipe.get("id")))
    for output, owners in sorted(producers.items()):
        if len(owners) <= 1:
            continue
        if not all(by_id[owner].get("allow_duplicate_output") is True for owner in owners):
            errors.append(f"duplicate managed output {output}: {owners}")

    removal_owners: defaultdict[str, list[str]] = defaultdict(list)
    for recipe in recipes:
        for removal in recipe.get("remove", []):
            removal_owners[str(removal)].append(str(recipe.get("id")))
    for removal in seed.get("additional_removals", []):
        removal_owners[str(removal)].append("<additional_removals>")
    for removal, owners in sorted(removal_owners.items()):
        if len(owners) > 1:
            errors.append(f"duplicate stock removal {removal}: {owners}")

    preserved = set(seed.get("preserve_recipe_ids", []))
    removal_ids = set(removal_owners)
    for conflict in sorted(preserved & removal_ids):
        errors.append(f"recipe is both preserved and removed: {conflict}")
    managed_outputs = set(producers)
    for conflict in sorted(managed_outputs & set(seed.get("exclude_outputs", []))):
        errors.append(f"managed output is also excluded: {conflict}")
    for conflict in sorted(managed_outputs & set(seed.get("user_owned_outputs", []))):
        errors.append(f"managed output is also user-owned: {conflict}")

    producer_by_item = {
        output: owners[0] for output, owners in producers.items() if len(owners) == 1
    }
    outgoing: defaultdict[str, set[str]] = defaultdict(set)
    inferred_edges = 0
    for consumer, recipe in by_id.items():
        dependencies = set(recipe.get("depends_on", []))
        for ingredient in recipe_inputs(recipe):
            producer = producer_by_item.get(ingredient)
            if producer:
                dependencies.add(producer)
                inferred_edges += 1
        for producer in dependencies:
            if producer == consumer:
                errors.append(f"{consumer}: consumes its own managed output")
                continue
            if producer not in by_id:
                continue
            outgoing[producer].add(consumer)
            producer_phase = by_id[producer].get("phase")
            consumer_phase = recipe.get("phase")
            if producer_phase in phase_index and consumer_phase in phase_index:
                if phase_index[producer_phase] > phase_index[consumer_phase]:
                    errors.append(
                        f"backward phase dependency: {consumer} ({consumer_phase}) uses "
                        f"{producer} ({producer_phase})"
                    )
    cycles = find_cycles(by_id, outgoing)
    for cycle in cycles:
        errors.append("managed ingredient cycle: " + " -> ".join(cycle))

    # KJSGen presents cards in phase/order sequence.  A same-phase consumer
    # must not appear before an exclusive managed material that it consumes.
    # Explicit depends_on edges are also included because they can encode a
    # prerequisite that is not visible as a literal ingredient.
    for consumer, recipe in by_id.items():
        consumer_phase = recipe.get("phase")
        consumer_order = recipe.get("order", 999)
        if isinstance(consumer_order, bool) or not isinstance(consumer_order, (int, float)):
            continue
        prerequisites = set(recipe.get("depends_on", []))
        for ingredient in recipe_material_inputs(recipe):
            producer = producer_by_item.get(ingredient)
            if producer:
                prerequisites.add(producer)
        for producer in sorted(prerequisites):
            if producer == consumer or producer not in by_id:
                continue
            producer_recipe = by_id[producer]
            if producer_recipe.get("exclusive_output") is not True:
                continue
            if producer_recipe.get("phase") != consumer_phase:
                continue
            producer_order = producer_recipe.get("order", 999)
            if isinstance(producer_order, bool) or not isinstance(producer_order, (int, float)):
                continue
            if producer_order >= consumer_order:
                errors.append(
                    f"same-phase recipe-order inversion: {consumer} ({consumer_order}) uses "
                    f"{producer} ({producer_order})"
                )

    exact_grids = grouped_duplicates(
        (canonical_grid_signature(recipe), str(recipe.get("id"))) for recipe in recipes
    )
    for owners in exact_grids:
        warnings.append("identical shaped/mechanical recipe design: " + ", ".join(owners))
    exact_sequences = grouped_duplicates(
        (sequence_signature(recipe), str(recipe.get("id"))) for recipe in recipes
    )
    for owners in exact_sequences:
        warnings.append("identical sequenced-assembly design: " + ", ".join(owners))

    pattern_groups = grouped_duplicates(
        (raw_pattern(recipe), str(recipe.get("id")))
        for recipe in recipes
        if str(recipe.get("id")) in explicit_ids
    )
    repeated_patterns = [owners for owners in pattern_groups if len(owners) > 1]
    full_five = [
        str(recipe.get("id"))
        for recipe in recipes
        if recipe.get("type") == "mechanical_crafting"
        and isinstance(recipe.get("pattern"), list)
        and len(recipe["pattern"]) == 5
        and all(len(str(row)) == 5 and " " not in str(row) for row in recipe["pattern"])
    ]
    unexpected_full_five = sorted(set(full_five) - JUSTIFIED_FULL_FIVE_BY_FIVE)
    missing_reviewed_full_five = sorted(JUSTIFIED_FULL_FIVE_BY_FIVE - set(full_five))
    if unexpected_full_five:
        errors.append(
            "unreviewed fully filled 5x5 grids: " + ", ".join(unexpected_full_five)
        )
    if missing_reviewed_full_five:
        warnings.append(
            "obsolete justified-full-5x5 allowlist entries: "
            + ", ".join(missing_reviewed_full_five)
        )

    direct_factories = sorted(
        str(recipe.get("id"))
        for recipe in recipes
        if any(
            output.startswith("mekanism:")
            and "factory" in output.split(":", 1)[1]
            for output in recipe_outputs(recipe)
        )
    )
    if direct_factories:
        errors.append(
            "direct upgraded Mekanism factory recipes are forbidden; use tier installers: "
            + ", ".join(direct_factories)
        )

    item_ids, stock_recipe_ids = catalog_sets(catalog)
    stock_producers = catalog_output_producers(catalog)
    if stock_producers:
        user_owned_outputs = {
            str(output) for output in seed.get("user_owned_outputs", [])
        }
        material_inputs = {
            ingredient
            for recipe in recipes
            for ingredient in recipe_material_inputs(recipe)
        }
        dead_inputs: list[tuple[str, list[str]]] = []
        for ingredient in sorted(material_inputs - managed_outputs - user_owned_outputs):
            owners = stock_producers.get(ingredient, set())
            if owners and owners <= removal_ids:
                dead_inputs.append((ingredient, sorted(owners)))
        for ingredient, owners in dead_inputs:
            errors.append(
                "managed material input has every catalog recipe producer removed: "
                f"{ingredient} <- {owners}"
            )
    if item_ids:
        used_items = managed_outputs | {
            ingredient for recipe in recipes for ingredient in recipe_inputs(recipe)
        }
        missing_items = sorted(item for item in used_items if item not in item_ids)
        missing_custom = [item for item in missing_items if item.startswith("industrial_colonies:")]
        # The catalog is assembled from mod JAR resources and intentionally is
        # not a complete vanilla registry dump.  Missing Minecraft namespace
        # references therefore are not evidence of a typo.
        missing_external = [
            item
            for item in missing_items
            if not item.startswith(("industrial_colonies:", "minecraft:"))
        ]
        if missing_external:
            errors.append("catalog-missing exact item IDs: " + ", ".join(missing_external))
        if missing_custom:
            warnings.append("catalog-missing custom item IDs: " + ", ".join(missing_custom))
    if stock_recipe_ids:
        unknown_removals = sorted(
            removal
            for removal in removal_ids
            if removal not in stock_recipe_ids and not removal.startswith("industrial_colonies:")
        )
        if unknown_removals:
            warnings.append(
                "stock removals absent from the static catalog: " + ", ".join(unknown_removals)
            )

    type_counts = Counter(str(recipe.get("type")) for recipe in recipes)
    notes.extend(
        [
            f"{len(seed.get('recipes', []))} explicit recipes + "
            f"{len(recipes) - len(seed.get('recipes', []))} generated machine-family recipes",
            "recipe types: " + ", ".join(f"{key}={value}" for key, value in type_counts.most_common()),
            f"{len(producers)} unique managed outputs; {inferred_edges} inferred prerequisite uses",
            f"{len(repeated_patterns)} repeated raw grid patterns; {len(full_five)} fully filled 5x5 grids",
        ]
    )
    if repeated_patterns:
        notes.append(
            "repeated pattern groups: "
            + " | ".join(", ".join(owners) for owners in repeated_patterns)
        )
    if full_five:
        notes.append("fully filled 5x5 grids: " + ", ".join(full_five))
    return errors, warnings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--apply-module",
        action="append",
        default=[],
        help="Import a tools module and call apply(seed) in memory before auditing",
    )
    args = parser.parse_args()

    seed = json.loads(args.seed.resolve().read_text(encoding="utf-8"))
    for module_name in args.apply_module:
        module = importlib.import_module(module_name)
        apply = getattr(module, "apply", None)
        if not callable(apply):
            raise TypeError(f"{module_name} has no callable apply(data)")
        apply(seed)

    errors, warnings, notes = audit(seed, args.catalog.resolve())
    for note in notes:
        print(f"NOTE: {note}")
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"PASS: recipe-design-v2 seed audit ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
