#!/usr/bin/env python3
"""Validate the reachable, pre-steel TFMG electronics progression slice."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = "industrial_electronics_progression.js"
ELECTRONICS = "CR01 — Electronics Manufacturing"
EARLY = "CR01 — Early Circuitry"
ADVANCED = "CR01 — Advanced Electronics Manufacturing"

EXPECTED_STAGES = {
    "industrial_colonies:electronics_manufacturing/empty_spool": ELECTRONICS,
    "tfmg:copper_spool": ELECTRONICS,
    "tfmg:copper_electrode_from_storage_blocks_copper_stonecutting": ELECTRONICS,
    "tfmg:zinc_electrode_from_storage_blocks_zinc_stonecutting": ELECTRONICS,
    "industrial_colonies:electronics_manufacturing/winding_machine": ELECTRONICS,
    "industrial_colonies:electronics_manufacturing/voltmeter": ELECTRONICS,
    "industrial_colonies:electronics_manufacturing/polarizer": ELECTRONICS,
    "industrial_colonies:electronics_manufacturing/electrode_holder": ELECTRONICS,
    "industrial_colonies:early_circuitry/unfinished_resistor": EARLY,
    "industrial_colonies:early_circuitry/resistor": EARLY,
    "industrial_colonies:early_circuitry/capacitor": EARLY,
    "industrial_colonies:early_circuitry/transistor": EARLY,
    "industrial_colonies:early_circuitry/empty_circuit_board": EARLY,
    "industrial_colonies:early_circuitry/circuit_board": EARLY,
    "tfmg:deploying/coated_circuit_board": ADVANCED,
    "industrial_colonies:advanced_electronics/electrically_etched_circuit_board": ADVANCED,
    "industrial_colonies:advanced_electronics/industrial_mixer": ADVANCED,
}

EXPECTED_UNLOCKS = {
    ELECTRONICS: {
        "tfmg:empty_spool",
        "tfmg:copper_spool",
        "tfmg:winding_machine",
        "tfmg:voltmeter",
        "tfmg:polarizer",
        "tfmg:electrode_holder",
        "tfmg:copper_electrode",
        "tfmg:zinc_electrode",
    },
    EARLY: {
        "tfmg:resistor",
        "tfmg:capacitor_item",
        "tfmg:transistor_item",
        "tfmg:empty_circuit_board",
        "tfmg:circuit_board",
    },
    ADVANCED: {
        "tfmg:etched_circuit_board",
        "tfmg:coated_circuit_board",
        "tfmg:industrial_mixer",
    },
}

EXPECTED_SOURCE_REMOVALS = {
    "tfmg:empty_spool_from_hardened_planks_stonecutting",
    "tfmg:crafting/materials/winding_machine",
    "tfmg:crafting/materials/polarizer",
    "tfmg:crafting/materials/electrode_holder",
    "tfmg:crafting/materials/voltmeter",
    "tfmg:crafting/materials/empty_circuit_board",
    "tfmg:crafting/materials/unfinished_resistor",
    "tfmg:crafting/materials/unfinished_resistorfrom_slime",
    "tfmg:winding/resistor",
    "tfmg:sequenced_assembly/capacitor",
    "tfmg:sequenced_assembly/transistor",
    "tfmg:sequenced_assembly/unfinished_circuit_board",
    "tfmg:vat_machine_recipe/etched_circuit_board",
    "tfmg:crafting/materials/industrial_mixer",
}

RETAINED_STOCK_RECIPES = {
    "tfmg:copper_spool",
    "tfmg:copper_electrode_from_storage_blocks_copper_stonecutting",
    "tfmg:zinc_electrode_from_storage_blocks_zinc_stonecutting",
    "tfmg:deploying/coated_circuit_board",
}

FORBIDDEN_REPLACEMENT_INPUTS = {
    "tfmg:steel_ingot",
    "tfmg:steel_casing",
    "tfmg:steel_mechanism",
    "tfmg:heavy_machinery_casing",
    "tfmg:plastic_sheet",
    "tfmg:silicon_ingot",
    "tfmg:n_semiconductor",
    "tfmg:p_semiconductor",
    "tfmg:constantan_spool",
    "tfmg:sulfuric_acid",
    "tfmg:sulfuric_acid_bucket",
    "tfmg:magnet",
    "c:ingots/steel",
    "c:nuggets/steel",
    "c:plates/steel",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def recipe_path(recipe_id: str) -> str:
    namespace, path = recipe_id.split(":", 1)
    return f"data/{namespace}/recipe/{path}.json"


def one_jar(mods: Path, pattern: str) -> Path:
    matches = sorted(mods.glob(pattern))
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one {pattern}, found {len(matches)}")
    return matches[0]


def recipe_outputs(recipe: dict[str, Any]) -> set[str]:
    outputs: set[str] = set()
    result = recipe.get("result")
    if isinstance(result, dict):
        value = result.get("id") or result.get("item")
        if isinstance(value, str):
            outputs.add(value)
    for result in recipe.get("results", []):
        if isinstance(result, dict):
            value = result.get("id") or result.get("item")
            if isinstance(value, str):
                outputs.add(value)
    return outputs


def ancestors(node: str, incoming: dict[str, set[str]]) -> set[str]:
    found: set[str] = set()
    frontier = list(incoming[node])
    while frontier:
        parent = frontier.pop()
        if parent in found:
            continue
        found.add(parent)
        frontier.extend(incoming[parent])
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path, help="Minecraft instance directory")
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--drawio-export", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    graph = load_json(args.drawio_export.resolve())
    assignments = load_json(project / "progression/machine_node_assignments.json")["nodes"]
    costs = load_json(project / "progression/research_costs.json")["nodes"]
    dependencies = load_json(project / "tools/machine_recipe_dependencies.json")["recipes"]
    additional = load_json(project / "tools/additional_recipe_stages.json")["recipes"]
    policies = load_json(project / "tools/canonicalization_policies.json")
    script = (project / "pack-scripts/server_scripts" / SCRIPT).read_text(encoding="utf-8")
    failures: list[str] = []

    labels = {node["id"]: node["label"] for node in graph["nodes"]}
    incoming: dict[str, set[str]] = defaultdict(set)
    edges: set[tuple[str, str]] = set()
    for edge in graph["edges"]:
        source = labels.get(edge["source"])
        target = labels.get(edge["target"])
        if source and target:
            incoming[target].add(source)
            edges.add((source, target))
    expected_edges = {
        ("CR01 — Early Electricity Technology", ELECTRONICS),
        (ELECTRONICS, EARLY),
        (EARLY, ADVANCED),
        (ADVANCED, "CR01 — Advanced Circuitry"),
    }
    for edge in sorted(expected_edges - edges):
        failures.append(f"immutable electronics edge is absent: {edge}")
    if len(labels) != 77 or len(edges) != 99:
        failures.append(f"immutable topology changed: {len(labels)} nodes / {len(edges)} edges")

    for node, expected in EXPECTED_UNLOCKS.items():
        actual = set(assignments[node].get("unlocks", []))
        missing = sorted(expected - actual)
        if missing:
            failures.append(f"{node} is missing unlocks: {' | '.join(missing)}")

    # All research costs in this slice must be produced by strict ancestors.
    item_owners: dict[str, set[str]] = defaultdict(set)
    for node, definition in assignments.items():
        for item in definition.get("unlocks", []):
            item_owners[item].add(node)
    for node in (ELECTRONICS, EARLY, ADVANCED, "CR01 — Advanced Circuitry"):
        allowed = ancestors(node, incoming)
        for cost in costs[node]["costs"]:
            item = cost["item"]
            owners = item_owners.get(item, set())
            if owners and not (owners & allowed):
                failures.append(f"same-node/downstream electronics cost: {node} -> {item}")

    for recipe_id in sorted(EXPECTED_SOURCE_REMOVALS):
        if recipe_id not in script:
            failures.append(f"stock electronics recipe is not removed: {recipe_id}")
    for recipe_id in sorted(EXPECTED_STAGES):
        if recipe_id.startswith("industrial_colonies:") and recipe_id not in script:
            failures.append(f"replacement recipe is absent from {SCRIPT}: {recipe_id}")
    for forbidden in sorted(FORBIDDEN_REPLACEMENT_INPUTS):
        # Stock IDs are confined to the removal list; scan only the recipe body.
        body = script.split("removedElectronicsRecipes.forEach", 1)[-1]
        if f"'{forbidden}'" in body:
            failures.append(f"replacement electronics path uses forbidden input: {forbidden}")

    if "type: 'tfmg:polarizing'" not in script:
        failures.append("advanced board replacement is not a TFMG polarizing recipe")
    if "industrial_colonies:electronics_manufacturing/voltmeter" not in script:
        failures.append("magnet-free voltmeter bootstrap recipe is absent")
    if "tfmg:vat_machine_recipe/sulfuric_acid" in script:
        failures.append("electronics script duplicates or alters sulfuric-acid synthesis")

    stage_entries = [*dependencies, *additional]
    stages: dict[str, set[str]] = defaultdict(set)
    for entry in stage_entries:
        stages[entry["recipe_id"]].add(entry["node"])
    for recipe_id, node in EXPECTED_STAGES.items():
        if stages.get(recipe_id) != {node}:
            failures.append(
                f"electronics recipe has missing/conflicting stage: {recipe_id} -> "
                f"{sorted(stages.get(recipe_id, set()))}, expected {node}"
            )

    dependency_by_output = {row["output"]: row for row in dependencies}
    overhaul_by_machine = {
        row["machine"]: row for row in policies.get("machine_overhauls", [])
    }
    for output in (
        "tfmg:winding_machine",
        "tfmg:voltmeter",
        "tfmg:polarizer",
        "tfmg:electrode_holder",
        "tfmg:industrial_mixer",
    ):
        dependency = dependency_by_output.get(output)
        policy = overhaul_by_machine.get(output)
        if dependency is None or policy is None:
            failures.append(f"machine dependency/policy is absent: {output}")
            continue
        if dependency["node"] != policy["node"]:
            failures.append(f"machine dependency/policy node differs: {output}")
        if dependency["recipe_id"] != policy["replacement_recipe"]:
            failures.append(f"machine dependency/policy recipe differs: {output}")

    component_policies = policies.get("electronics_component_overhauls", [])
    component_sources = {
        source
        for policy in component_policies
        for source in policy.get("source_recipes", [])
    }
    missing_policy_sources = sorted(EXPECTED_SOURCE_REMOVALS - component_sources - {
        "tfmg:crafting/materials/winding_machine",
        "tfmg:crafting/materials/polarizer",
        "tfmg:crafting/materials/electrode_holder",
        "tfmg:crafting/materials/voltmeter",
        "tfmg:crafting/materials/industrial_mixer",
    })
    if missing_policy_sources:
        failures.append(
            "electronics component policy omits sources: " + " | ".join(missing_policy_sources)
        )

    tfmg_jar = one_jar(args.instance.resolve() / "mods", "tfmg-*.jar")
    with zipfile.ZipFile(tfmg_jar) as archive:
        names = set(archive.namelist())
        for recipe_id in sorted(EXPECTED_SOURCE_REMOVALS | RETAINED_STOCK_RECIPES):
            path = recipe_path(recipe_id)
            if path not in names:
                failures.append(f"installed TFMG source recipe is absent: {recipe_id}")
        # Prove the removed acid etch really was the sulfuric-acid dependency.
        acid_etch_path = recipe_path("tfmg:vat_machine_recipe/etched_circuit_board")
        if acid_etch_path in names:
            acid_etch = json.loads(archive.read(acid_etch_path).decode("utf-8-sig"))
            if acid_etch.get("type") != "tfmg:vat_machine_recipe":
                failures.append("installed etched-board source is no longer a vat recipe")
            if "tfmg:sulfuric_acid" not in json.dumps(acid_etch):
                failures.append("installed etched-board source no longer documents the acid conflict")
            if "tfmg:etched_circuit_board" not in recipe_outputs(acid_etch):
                failures.append("installed etched-board source output changed")

    report = {
        "drawio_source_sha256": graph.get("source_sha256"),
        "nodes": len(labels),
        "edges": len(edges),
        "script": SCRIPT,
        "expected_stage_mappings": len(EXPECTED_STAGES),
        "removed_stock_recipes": len(EXPECTED_SOURCE_REMOVALS),
        "component_overhaul_policies": len(component_policies),
        "failures": failures,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"Checked {len(EXPECTED_STAGES)} electronics stages, "
        f"{len(EXPECTED_SOURCE_REMOVALS)} stock replacements, and immutable "
        f"{len(labels)}-node/{len(edges)}-edge topology."
    )
    if failures:
        print(f"FAIL: {len(failures)} electronics progression issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: TFMG electronics is reachable without steel, plastic, silicon, magnets, or acid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
