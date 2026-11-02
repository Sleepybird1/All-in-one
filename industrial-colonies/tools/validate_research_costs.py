from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


EXPECTED_NODES = 77
EXPECTED_EDGES = 99
MAX_BRANCH_DEPTH = 6
MIN_COST_ENTRIES = 1
MAX_COST_ENTRIES = 3
MIN_COST_COUNT = 1
MAX_COST_COUNT = 16

ERA_COUNT_CEILINGS = (
    ("Introduction", 0, 5, 16),
    ("Industrial foundations", 6, 10, 12),
    ("Integrated and advanced factories", 11, 19, 8),
    ("Nuclear fuel cycle", 20, 99, 12),
)
EXPECTED_ERA_CEILINGS = {
    "depth_0_to_5": 16,
    "depth_6_to_10": 12,
    "depth_11_to_19": 8,
    "depth_20_plus": 12,
}

CURRENCY_GATES = {
    "allthemodium:allthemodium_plate": "CR01 — Exotic Metallurgy",
    "allthemodium:vibranium_plate": "CR01 — Yellorium Refinement",
    "allthemodium:unobtainium_ingot": "CR01 — The Nuclear Age",
    "allthemodium:vibranium_allthemodium_alloy_ingot": "CR01 — The Nuclear Age",
    "allthemodium:unobtainium_allthemodium_alloy_ingot": "CR01 — The Nuclear Age",
    "allthemodium:unobtainium_vibranium_alloy_ingot": "CR01 — The Nuclear Age",
}

# The recipe catalog records Mekanism Rotary recipes as chemical/fluid IDs. These
# aliases identify the registered filled-bucket items a player can obtain only
# after running those staged phase-conversion recipes.
STAGED_RECIPE_OUTPUT_ALIASES = {
    "mekanism:rotary/uranium_oxide": {"mekanism:uranium_oxide_bucket"},
    "mekanism:rotary/uranium_hexafluoride": {"mekanism:uranium_hexafluoride_bucket"},
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"^CR\d+\s*(?:--|—)\s*", "", normalized, flags=re.IGNORECASE)
    normalized = normalized.replace("don't", "dont").replace("don’t", "dont")
    return re.sub(r"[^a-zA-Z0-9]+", "_", normalized).strip("_").lower()


def discover_minecraft_client() -> Path | None:
    home = Path.home()
    candidates = [
        home / "curseforge" / "minecraft" / "Install" / "versions" / "1.21.1" / "1.21.1.jar",
        home / "curseforge" / "minecraft" / "Install" / "libraries" / "net" / "minecraft" / "client" / "1.21.1" / "client-1.21.1-official.jar",
        home / ".minecraft" / "versions" / "1.21.1" / "1.21.1.jar",
    ]
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def read_catalog(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["item_id"]: row for row in csv.DictReader(handle)}


def read_recipe_outputs(path: Path) -> dict[str, set[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            row["recipe_id"]: {
                token.strip()
                for token in row.get("outputs", "").split("|")
                if token.strip()
            }
            for row in csv.DictReader(handle)
        }


def era_count_ceiling(depth: int) -> tuple[str, int]:
    for name, minimum, maximum, ceiling in ERA_COUNT_CEILINGS:
        if minimum <= depth <= maximum:
            return name, ceiling
    raise ValueError(f"No research-cost ceiling configured for logical depth {depth}")


def escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate all Industrial Colonies University research costs and generated MineColonies JSON."
    )
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--drawio-export", type=Path)
    parser.add_argument("--catalog-items", type=Path)
    parser.add_argument("--catalog-recipes", type=Path)
    parser.add_argument("--minecraft-client-jar", type=Path)
    parser.add_argument("--generated-root", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--audit", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    audit_root = project.parent / "industrial-audit"
    drawio_path = (args.drawio_export or audit_root / "drawio-export" / "drawio_tree.json").resolve()
    catalog_path = (
        args.catalog_items or project.parent.parent / "outputs" / "recipe-catalog-current" / "items.csv"
    ).resolve()
    recipe_catalog_path = (
        args.catalog_recipes or catalog_path.parent / "recipes.csv"
    ).resolve()
    minecraft_jar = (args.minecraft_client_jar.resolve() if args.minecraft_client_jar else discover_minecraft_client())
    generated_root = (args.generated_root or project / "src" / "generated" / "resources").resolve()
    report_path = (args.report or audit_root / "MINECOLONIES_RESEARCH_COST_VALIDATION.json").resolve()
    audit_path = (args.audit or audit_root / "MINECOLONIES_RESEARCH_COST_AUDIT.md").resolve()

    failures: list[str] = []
    if not drawio_path.is_file():
        failures.append(f"Missing Draw.io export: {drawio_path}")
    if not catalog_path.is_file():
        failures.append(f"Missing model-backed item catalog: {catalog_path}")
    if not recipe_catalog_path.is_file():
        failures.append(f"Missing recipe catalog for circular-cost validation: {recipe_catalog_path}")
    if minecraft_jar is None or not minecraft_jar.is_file():
        failures.append("Could not locate a Minecraft 1.21.1 client JAR for vanilla item-model validation")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    graph = load(drawio_path)
    assignments = load(project / "progression" / "machine_node_assignments.json")["nodes"]
    layout = load(project / "progression" / "minecolonies_branch_layout.json")
    cost_config = load(project / "progression" / "research_costs.json")
    cost_nodes = cost_config["nodes"]
    vanilla_baseline = set(cost_config.get("vanilla_baseline_items", []))
    catalog = read_catalog(catalog_path)
    project_item_models: set[str] = set()
    for resource_root in (
        project / "src" / "main" / "resources",
        project / "src" / "generated" / "resources",
    ):
        for model in resource_root.glob("assets/*/models/item/*.json"):
            namespace = model.parents[2].name
            item_path = model.relative_to(model.parents[0]).with_suffix("").as_posix()
            project_item_models.add(f"{namespace}:{item_path}")
    recipe_outputs = read_recipe_outputs(recipe_catalog_path)
    additional_recipe_stages = load(project / "tools" / "additional_recipe_stages.json")["recipes"]

    configured_ceilings = cost_config.get("design_rules", {}).get("era_count_ceilings")
    if configured_ceilings != EXPECTED_ERA_CEILINGS:
        failures.append(
            f"research_costs.json era ceilings changed: {configured_ceilings} != {EXPECTED_ERA_CEILINGS}"
        )

    id_to_label = {node["id"]: node["label"] for node in graph["nodes"]}
    graph_labels = set(id_to_label.values())
    incoming: dict[str, set[str]] = defaultdict(set)
    for label in graph_labels:
        incoming[label] = set()
    graph_edges: set[tuple[str, str]] = set()
    for edge in graph["edges"]:
        source = id_to_label.get(edge["source"])
        target = id_to_label.get(edge["target"])
        if source is None or target is None:
            failures.append(f"Unresolved Draw.io edge: {edge}")
            continue
        incoming[target].add(source)
        graph_edges.add((source, target))

    if len(graph_labels) != EXPECTED_NODES:
        failures.append(f"Draw.io node count changed: {len(graph_labels)} != {EXPECTED_NODES}")
    if len(graph_edges) != EXPECTED_EDGES:
        failures.append(f"Draw.io edge count changed: {len(graph_edges)} != {EXPECTED_EDGES}")
    for label in sorted(graph_labels - set(cost_nodes)):
        failures.append(f"Missing research cost definition: {label}")
    for label in sorted(set(cost_nodes) - graph_labels):
        failures.append(f"Research cost definition is not a Draw.io node: {label}")

    visiting: set[str] = set()
    ancestor_cache: dict[str, set[str]] = {}
    global_depths: dict[str, int] = {}

    def ancestors(label: str) -> set[str]:
        if label in ancestor_cache:
            return ancestor_cache[label]
        if label in visiting:
            failures.append(f"Draw.io dependency cycle reaches {label}")
            return set()
        visiting.add(label)
        result: set[str] = set()
        for parent in incoming[label]:
            result.add(parent)
            result.update(ancestors(parent))
        visiting.remove(label)
        ancestor_cache[label] = result
        return result

    def global_depth(label: str) -> int:
        if label in global_depths:
            return global_depths[label]
        parents = incoming[label]
        result = 0 if not parents else 1 + max(global_depth(parent) for parent in parents)
        global_depths[label] = result
        return result

    for label in graph_labels:
        ancestors(label)
        global_depth(label)

    for gate in sorted(set(CURRENCY_GATES.values()) - graph_labels):
        failures.append(f"Currency gate is not a Draw.io research node: {gate}")

    staged_item_nodes: dict[str, set[str]] = defaultdict(set)
    staged_item_recipes: dict[tuple[str, str], set[str]] = defaultdict(set)
    for stage_entry in additional_recipe_stages:
        recipe_id = stage_entry.get("recipe_id")
        stage_node = stage_entry.get("node")
        if not isinstance(recipe_id, str) or not isinstance(stage_node, str):
            failures.append(f"Malformed additional recipe-stage entry: {stage_entry}")
            continue
        if stage_node not in graph_labels:
            failures.append(f"Additional recipe stage uses a non-Draw.io node: {recipe_id} -> {stage_node}")
            continue
        outputs = set(recipe_outputs.get(recipe_id, set()))
        outputs.update(STAGED_RECIPE_OUTPUT_ALIASES.get(recipe_id, set()))
        for item in outputs:
            staged_item_nodes[item].add(stage_node)
            staged_item_recipes[(item, stage_node)].add(recipe_id)

    item_unlock_nodes: dict[str, set[str]] = defaultdict(set)
    for label, assignment in assignments.items():
        unlock_types = assignment.get("unlock_types", {})
        for item in assignment.get("unlocks", []):
            if unlock_types.get(item, "item") in {"item", "vanilla_item"}:
                item_unlock_nodes[item].add(label)

    vanilla_models: set[str] = set()
    with zipfile.ZipFile(minecraft_jar) as archive:
        archive_names = set(archive.namelist())
        for item in vanilla_baseline:
            namespace, path = item.split(":", 1)
            model_path = f"assets/{namespace}/models/item/{path}.json"
            if model_path in archive_names:
                vanilla_models.add(item)
            else:
                failures.append(f"Vanilla baseline item lacks 1.21.1 item-model evidence: {item}")

    resource_ids: dict[str, str] = {}
    layout_entries: dict[str, dict[str, Any]] = {}
    branch_depths: dict[str, int] = {}
    branch_nodes: dict[str, set[str]] = defaultdict(set)
    for branch in layout["branches"]:
        branch_id = branch["id"]
        for entry in branch["nodes"]:
            label = entry["label"]
            if label in layout_entries:
                failures.append(f"Node appears more than once in MineColonies branch layout: {label}")
            layout_entries[label] = {**entry, "branch": branch_id}
            branch_nodes[branch_id].add(label)
            resource_ids[label] = f"industrial_colonies:{branch_id}/{slug(label)}"
    for label in sorted(graph_labels - set(layout_entries)):
        failures.append(f"Draw.io node missing from MineColonies branch layout: {label}")
    for label in sorted(set(layout_entries) - graph_labels):
        failures.append(f"MineColonies branch-layout node absent from Draw.io: {label}")

    branch_visiting: set[str] = set()

    def branch_depth(label: str) -> int:
        if label in branch_depths:
            return branch_depths[label]
        if label in branch_visiting:
            failures.append(f"MineColonies local-parent cycle reaches {label}")
            return MAX_BRANCH_DEPTH + 1
        branch_visiting.add(label)
        parent = layout_entries[label].get("parent")
        result = 1 if not parent else branch_depth(parent) + 1
        branch_visiting.remove(label)
        branch_depths[label] = result
        return result

    for label in graph_labels & set(layout_entries):
        depth = branch_depth(label)
        if depth > MAX_BRANCH_DEPTH:
            failures.append(f"MineColonies branch depth exceeds {MAX_BRANCH_DEPTH}: {label} = {depth}")

    per_node: dict[str, dict[str, Any]] = {}
    unique_cost_items: set[str] = set()
    total_cost_entries = 0
    model_backed_entries = 0
    vanilla_entries = 0
    cross_nodes = 0
    fully_supported_cross_nodes = 0
    currency_usage: dict[str, list[str]] = defaultdict(list)
    staged_cost_entries_checked = 0

    for label in sorted(graph_labels):
        entry = cost_nodes.get(label, {})
        costs = entry.get("costs", [])
        if not MIN_COST_ENTRIES <= len(costs) <= MAX_COST_ENTRIES:
            failures.append(
                f"Research must have {MIN_COST_ENTRIES}-{MAX_COST_ENTRIES} cost entries: {label} has {len(costs)}"
            )
        if not isinstance(entry.get("rationale"), str) or not entry.get("rationale", "").strip():
            failures.append(f"Research cost lacks a rationale: {label}")

        seen_items: set[str] = set()
        cost_evidence: list[dict[str, Any]] = []
        direct_support: dict[str, set[str]] = {parent: set() for parent in incoming[label]}
        for cost in costs:
            total_cost_entries += 1
            if set(cost) != {"item", "count"}:
                failures.append(f"Cost must use exact MineColonies item/count keys for {label}: {cost}")
            item = cost.get("item")
            count = cost.get("count")
            if not isinstance(item, str) or not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", item):
                failures.append(f"Invalid cost item identifier for {label}: {item}")
                continue
            if item in seen_items:
                failures.append(f"Duplicate cost item for {label}: {item}")
            seen_items.add(item)
            unique_cost_items.add(item)
            if not isinstance(count, int) or isinstance(count, bool) or not MIN_COST_COUNT <= count <= MAX_COST_COUNT:
                failures.append(
                    f"Cost count outside designed {MIN_COST_COUNT}-{MAX_COST_COUNT} curve for {label}: {item} x{count}"
                )
            _, count_ceiling = era_count_ceiling(global_depths[label])
            if isinstance(count, int) and not isinstance(count, bool) and count > count_ceiling:
                failures.append(
                    f"Cost count exceeds logical-era ceiling {count_ceiling} at depth {global_depths[label]} "
                    f"for {label}: {item} x{count}"
                )

            if item.startswith("allthemodium:"):
                gate = CURRENCY_GATES.get(item)
                if gate is None:
                    failures.append(f"Unclassified Allthemodium-family research currency for {label}: {item}")
                elif gate not in ancestors(label):
                    failures.append(
                        f"Currency appears before its strict Draw.io gate for {label}: {item}; gate={gate}"
                    )
                else:
                    currency_usage[item].append(label)

            staged_nodes = staged_item_nodes.get(item, set())
            if staged_nodes:
                staged_cost_entries_checked += 1
            if label in staged_nodes:
                recipes = sorted(staged_item_recipes[(item, label)])
                failures.append(
                    f"Same-node recipe/cost circular lock for {label}: {item} is produced by staged recipe(s) {recipes}"
                )

            evidence_kind = ""
            eligible_owners: set[str] = set()
            if item.startswith("minecraft:"):
                if label not in {node for node in graph_labels if not incoming[node]}:
                    failures.append(f"Vanilla baseline costs are restricted to graph roots: {label} uses {item}")
                if item not in vanilla_baseline:
                    failures.append(f"Unapproved vanilla baseline cost for {label}: {item}")
                if item not in vanilla_models:
                    failures.append(f"No Minecraft 1.21.1 item-model proof for {label}: {item}")
                vanilla_entries += 1
                evidence_kind = "Minecraft 1.21.1 item model"
            else:
                catalog_row = catalog.get(item)
                if item in project_item_models:
                    model_backed_entries += 1
                elif catalog_row is None:
                    failures.append(f"Cost item absent from current model-backed catalog for {label}: {item}")
                elif "item_model" not in {token.strip() for token in catalog_row.get("evidence", "").split("|")}:
                    failures.append(
                        f"Cost item has no item-model evidence in current catalog for {label}: {item} "
                        f"({catalog_row.get('evidence', '')})"
                    )
                else:
                    model_backed_entries += 1
                owners = item_unlock_nodes.get(item, set())
                eligible_owners = owners & ancestors(label)
                if not owners:
                    failures.append(f"No research unlock provenance for cost item used by {label}: {item}")
                elif not eligible_owners:
                    failures.append(
                        f"Cost item is not obtainable from a strict ancestor of {label}: {item}; "
                        f"unlock nodes={sorted(owners)}"
                    )
                evidence_kind = ", ".join(sorted(eligible_owners)) or "UNPROVEN"
                for parent in incoming[label]:
                    parent_lineage = ancestors(parent) | {parent}
                    if eligible_owners & parent_lineage:
                        direct_support[parent].add(item)

            cost_evidence.append(
                {
                    "item": item,
                    "count": count,
                    "availability_evidence": evidence_kind,
                    "eligible_unlock_nodes": sorted(eligible_owners),
                }
            )

        if len(incoming[label]) > 1:
            cross_nodes += 1
            unsupported = sorted(parent for parent, items in direct_support.items() if not items)
            if unsupported:
                failures.append(
                    f"Cross-prerequisite research cost does not represent every incoming branch for {label}: {unsupported}"
                )
            else:
                fully_supported_cross_nodes += 1

        per_node[label] = {
            "global_depth": global_depths[label],
            "branch": layout_entries.get(label, {}).get("branch"),
            "branch_depth": branch_depths.get(label),
            "direct_prerequisites": sorted(incoming[label]),
            "rationale": entry.get("rationale", ""),
            "costs": cost_evidence,
            "direct_prerequisite_cost_support": {
                parent: sorted(items) for parent, items in sorted(direct_support.items())
            },
        }

    generated_edges: set[tuple[str, str]] = set()
    resource_to_label = {resource: label for label, resource in resource_ids.items()}
    generated_node_files: list[Path] = []
    generated_cost_shape_ok = 0
    expected_node_paths: set[Path] = set()
    research_root = generated_root / "data" / "industrial_colonies" / "researches"
    for resource_id in resource_ids.values():
        namespace, relative = resource_id.split(":", 1)
        expected_node_paths.add(generated_root / "data" / namespace / "researches" / f"{relative}.json")
    actual_node_paths = {
        path.resolve()
        for path in research_root.glob("*/*.json")
        if path.is_file()
    }
    expected_node_paths = {path.resolve() for path in expected_node_paths}
    for path in sorted(expected_node_paths - actual_node_paths):
        failures.append(f"Expected generated research node file is absent: {path}")
    for path in sorted(actual_node_paths - expected_node_paths):
        failures.append(f"Unexpected generated research node file exceeds exact 77-node coverage: {path}")
    for label, resource_id in resource_ids.items():
        namespace, relative = resource_id.split(":", 1)
        node_path = generated_root / "data" / namespace / "researches" / f"{relative}.json"
        if not node_path.is_file():
            failures.append(f"Missing generated research JSON for {label}: {node_path}")
            continue
        generated_node_files.append(node_path)
        research = load(node_path)
        expected_costs = cost_nodes.get(label, {}).get("costs", [])
        actual_costs = research.get("costs")
        if actual_costs != expected_costs:
            failures.append(f"Generated costs do not match research_costs.json for {label}")
        elif all(set(cost) == {"item", "count"} for cost in actual_costs):
            generated_cost_shape_ok += 1
        if research.get("researchLevel") != branch_depths.get(label):
            failures.append(
                f"Generated researchLevel mismatch for {label}: "
                f"{research.get('researchLevel')} != {branch_depths.get(label)}"
            )
        parent_resource = research.get("parentResearch")
        if parent_resource:
            parent_label = resource_to_label.get(parent_resource)
            if parent_label is None:
                failures.append(f"Unknown generated parentResearch for {label}: {parent_resource}")
            else:
                generated_edges.add((parent_label, label))
        for requirement in research.get("requirements", []):
            if requirement.get("type") != "minecolonies:research":
                continue
            prerequisite_resource = requirement.get("research")
            prerequisite_label = resource_to_label.get(prerequisite_resource)
            if prerequisite_label is None:
                failures.append(f"Unknown generated research requirement for {label}: {prerequisite_resource}")
            else:
                generated_edges.add((prerequisite_label, label))

    for edge in sorted(graph_edges - generated_edges):
        failures.append(f"Draw.io edge missing from generated MineColonies data: {edge[0]} -> {edge[1]}")
    for edge in sorted(generated_edges - graph_edges):
        failures.append(f"Generated MineColonies edge absent from Draw.io: {edge[0]} -> {edge[1]}")

    referenced_catalog_items = sorted(item for item in unique_cost_items if not item.startswith("minecraft:"))
    missing_baseline_use = sorted(vanilla_baseline - unique_cost_items)
    if missing_baseline_use:
        failures.append(f"Unused vanilla baseline allowlist entries: {missing_baseline_use}")

    for item in sorted(set(CURRENCY_GATES) - unique_cost_items):
        failures.append(f"Required manufactured research currency is unused: {item}")

    curve: list[dict[str, Any]] = []
    for name, minimum, maximum, ceiling in ERA_COUNT_CEILINGS:
        labels = [label for label in graph_labels if minimum <= global_depths[label] <= maximum]
        counts = [
            cost["count"]
            for label in labels
            for cost in cost_nodes.get(label, {}).get("costs", [])
            if isinstance(cost.get("count"), int)
        ]
        curve.append(
            {
                "band": name,
                "depth_range": f"{minimum}-{maximum if maximum < 99 else 'end'}",
                "nodes": len(labels),
                "cost_entries": len(counts),
                "minimum_entry_count": min(counts, default=0),
                "maximum_entry_count": max(counts, default=0),
                "average_entry_count": round(sum(counts) / len(counts), 2) if counts else 0,
                "validated_ceiling": ceiling,
            }
        )

    report = {
        "drawio_source": graph.get("source"),
        "drawio_source_sha256": graph.get("source_sha256"),
        "drawio_nodes": len(graph_labels),
        "drawio_edges": len(graph_edges),
        "minecolonies_branches": 1,
        "minecolonies_branch": f"industrial_colonies:{layout['tree']['id']}",
        "minecolonies_branch_name": layout["tree"]["name"],
        "stable_resource_path_sections": len(layout["branches"]),
        "maximum_minecolonies_branch_depth": max(branch_depths.values(), default=0),
        "costed_nodes": len(cost_nodes),
        "total_cost_entries": total_cost_entries,
        "unique_cost_items": len(unique_cost_items),
        "modded_cost_entries_with_item_model_evidence": model_backed_entries,
        "vanilla_cost_entries_with_1_21_1_item_model_evidence": vanilla_entries,
        "cross_prerequisite_nodes": cross_nodes,
        "cross_prerequisite_nodes_with_all_branches_represented": fully_supported_cross_nodes,
        "generated_research_files_checked": len(generated_node_files),
        "generated_files_with_exact_item_count_cost_shape": generated_cost_shape_ok,
        "catalog_items_source": str(catalog_path),
        "catalog_items_loaded": len(catalog),
        "project_item_models_loaded": len(project_item_models),
        "minecraft_client_jar": str(minecraft_jar),
        "recipe_catalog_source": str(recipe_catalog_path),
        "referenced_modded_cost_items": referenced_catalog_items,
        "currency_gates": CURRENCY_GATES,
        "currency_usage": {item: labels for item, labels in sorted(currency_usage.items())},
        "staged_cost_entries_checked_for_same_node_cycles": staged_cost_entries_checked,
        "same_node_recipe_cost_cycles": 0 if not any("Same-node recipe/cost" in failure for failure in failures) else None,
        "cost_curve": curve,
        "nodes": per_node,
        "failures": failures,
    }
    write_json(report_path, report)

    audit_lines = [
        "# MineColonies University Research Cost Audit",
        "",
        "## Result",
        "",
        (
            f"Validated **{len(cost_nodes)} costed nodes**, **{total_cost_entries} item/count entries**, "
            f"**{len(graph_edges)} dependency edges**, and a maximum native branch depth of "
            f"**{max(branch_depths.values(), default=0)}**. "
            f"Status: **{'PASS' if not failures else 'FAIL'}**."
        ),
        "",
        "Each modded item below has current catalog or project-source `item_model` evidence and an unlock provenance from a strict "
        "Draw.io ancestor. Vanilla root materials were verified directly against the Minecraft 1.21.1 client JAR. "
            "Every convergence node with multiple incoming prerequisites has at least one cost backed by each incoming "
            "branch. All six manufactured ATM-family currencies are ancestry-gated, and staged recipe outputs were "
            "checked for same-node cost cycles. Generated research JSON was checked for MineColonies' exact "
            "`costs: [{item, count}]` shape.",
        "",
        "## Cost curve",
        "",
        "| Progression band | Global depths | Nodes | Entries | Entry-count range | Average entry count |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for band in curve:
        audit_lines.append(
            f"| {band['band']} | {band['depth_range']} | {band['nodes']} | {band['cost_entries']} | "
            f"{band['minimum_entry_count']}–{band['maximum_entry_count']} (cap {band['validated_ceiling']}) | "
            f"{band['average_entry_count']} |"
        )
    audit_lines.extend(
        [
            "",
            "The curve caps early proofs at 16, industrial-foundation proofs at 12, integrated/advanced proofs at 8, "
            "and nuclear proofs at 12. Difficulty comes from prerequisite factory complexity and manufactured currency, "
            "not multi-stack University sinks.",
            "",
            "## Per-node availability proof",
            "",
            "| Node | Global depth | Direct prerequisites | Costs | Strict-ancestor or vanilla proof |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for label in sorted(per_node, key=lambda value: (global_depths[value], value)):
        data = per_node[label]
        prerequisite_text = "; ".join(data["direct_prerequisites"]) or "Graph root"
        cost_text = "; ".join(f"{cost['count']}× `{cost['item']}`" for cost in data["costs"])
        proof_text = "; ".join(
            f"`{cost['item']}` ← {cost['availability_evidence']}" for cost in data["costs"]
        )
        audit_lines.append(
            f"| {escape_table(label)} | {data['global_depth']} | {escape_table(prerequisite_text)} | "
            f"{escape_table(cost_text)} | {escape_table(proof_text)} |"
        )
    if failures:
        audit_lines.extend(["", "## Failures", ""] + [f"- {failure}" for failure in failures])
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    print(
        f"Checked {len(cost_nodes)} costed nodes / {total_cost_entries} entries / "
        f"{len(graph_edges)} edges at MineColonies depth {max(branch_depths.values(), default=0)}."
    )
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print(
        f"PASS: {model_backed_entries} modded entries have item-model evidence, "
        f"{vanilla_entries} vanilla entries have Minecraft 1.21.1 model evidence, and all "
        f"{cross_nodes} convergence nodes represent every incoming prerequisite branch."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
