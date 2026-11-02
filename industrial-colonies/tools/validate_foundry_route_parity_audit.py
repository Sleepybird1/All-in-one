#!/usr/bin/env python3
"""Validate route evidence and the TFMG-gated foundry endpoint redesign."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_foundry_route_parity_audit as builder


PROJECT = builder.PROJECT
PLAN = PROJECT / "FOUNDRY_ROUTE_PARITY_AUDIT.plan.json"
PATCH = PROJECT / "FOUNDRY_ROUTE_PARITY_AUDIT.patch.json"


def normalized_ref(value: str) -> str:
    head, separator, tail = value.partition("x ")
    return tail.strip() if separator and head.strip().isdigit() else value


def assigned_nodes(assignments: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for node_id, node in assignments.get("nodes", {}).items():
        if not isinstance(node, dict):
            continue
        for output in node.get("unlocks", []):
            if isinstance(output, str):
                result[output] = node_id
    return result


def recipe_inputs(recipe: dict[str, Any]) -> set[str]:
    values: list[str] = []
    if isinstance(recipe.get("input"), str):
        values.append(recipe["input"])
    values.extend(value for value in recipe.get("inputs", []) if isinstance(value, str))
    for step in recipe.get("steps", []):
        if isinstance(step, dict) and isinstance(step.get("ingredient"), str):
            values.append(step["ingredient"])
    return {normalized_ref(value) for value in values}


def validate_review(
    plan: dict[str, Any],
    patch: dict[str, Any],
    automatic: dict[str, Any],
    rows: list[dict[str, str]],
    item_ids: set[str],
    assignments: dict[str, Any],
    canonicalization_text: str,
) -> list[str]:
    failures: list[str] = []
    expected_outputs = list(builder.CANDIDATE_OUTPUTS)
    expected_recipes = [
        recipe_id
        for output in builder.CANDIDATE_OUTPUTS
        for recipe_id in builder.STOCK_RECIPE_IDS[output]
    ]
    expected_owners = [
        builder.AUTOMATIC_OWNER_IDS[output] for output in builder.CANDIDATE_OUTPUTS
    ]
    by_id = {row["recipe_id"]: row for row in rows}

    if plan.get("schema_version") != 1 or plan.get("batch_id") != "foundry_route_parity":
        failures.append("plan identity or schema drifted")
    if plan.get("status") != "implemented":
        failures.append("plan status must remain implemented")
    if patch.get("status") != "implemented" or patch.get("mode") != "implemented_historical_patch":
        failures.append("patch status/mode must remain implemented historical evidence")
    if plan.get("implementation") != builder.IMPLEMENTATION or patch.get("implementation") != builder.IMPLEMENTATION:
        failures.append("implemented checkpoint metadata drifted")
    if plan.get("decision") != "RETAIN_FUNCTIONAL_FOUNDRIES_WITH_TFMG_GATED_ENDPOINTS":
        failures.append("reviewed foundry decision drifted")
    if plan.get("candidate_outputs") != expected_outputs:
        failures.append("candidate output order/coverage drifted")

    automatic_entries = {
        row.get("output"): row
        for row in automatic.get("entries", [])
        if isinstance(row, dict) and row.get("output") in builder.CANDIDATE_OUTPUTS
    }
    if set(automatic_entries) != set(builder.CANDIDATE_OUTPUTS):
        failures.append("automatic audit no longer contains all eight candidates")
    old = plan.get("old_automatic_classification", {})
    for output in builder.CANDIDATE_OUTPUTS:
        source = automatic_entries.get(output, {})
        evidence = old.get(output, {}) if isinstance(old, dict) else {}
        if source.get("classification") != "redundant_should_retire":
            failures.append(f"{output}: original tentative classification drifted")
        if evidence.get("managed_id") != builder.AUTOMATIC_OWNER_IDS[output]:
            failures.append(f"{output}: automatic-owner evidence drifted")
        if evidence.get("classification") != source.get("classification"):
            failures.append(f"{output}: prior classification evidence drifted")

    direct_producers = {
        output: sorted(
            row["recipe_id"]
            for row in rows
            if output in builder.split_refs(row.get("outputs", ""))
        )
        for output in builder.CANDIDATE_OUTPUTS
    }
    for output in builder.CANDIDATE_OUTPUTS:
        if direct_producers[output] != sorted(builder.STOCK_RECIPE_IDS[output]):
            failures.append(f"{output}: installed direct producers changed")

    sources = plan.get("installed_stock_producers", [])
    if [entry.get("id") for entry in sources if isinstance(entry, dict)] != expected_recipes:
        failures.append("installed stock producer evidence drifted")
    for source in sources:
        if not isinstance(source, dict):
            failures.append("stock source evidence contains a non-object")
            continue
        row = by_id.get(str(source.get("id", "")))
        if row is None:
            failures.append(f"missing installed source recipe: {source.get('id')}")
            continue
        for field in ("recipe_type", "source_jar", "source_path"):
            if source.get(field) != row.get(field):
                failures.append(f"{source.get('id')}: source {field} drifted")
        if source.get("inputs") != sorted(builder.split_refs(row.get("inputs", ""))):
            failures.append(f"{source.get('id')}: source input evidence drifted")

    expected_evidence = builder.route_evidence(rows)
    if plan.get("route_evidence") != expected_evidence:
        failures.append("catalog route evidence drifted")
    else:
        cm = expected_evidence["create_metallurgy"]
        tfmg = expected_evidence["tfmg"]
        modern = expected_evidence["modernfoundry"]
        if tfmg["casting_recipe_count"] >= cm["casting_and_alloy_recipe_count"]:
            failures.append("Create Metallurgy parity-failure proof no longer holds")
        if tfmg["casting_recipe_count"] >= modern["table_basin_route_recipe_count"]:
            failures.append("Modern Foundry parity-failure proof no longer holds")
        if cm["exclusive_output_reference_count"] <= 0 or modern["exclusive_output_reference_count"] <= 0:
            failures.append("unique foundry route evidence vanished")

    proposals = plan.get("replacement_contracts", [])
    if proposals != list(builder.PROPOSALS):
        failures.append("eight reviewed replacement contracts drifted")
    if patch.get("recipes_to_append") != proposals:
        failures.append("patch recipes diverged from reviewed contracts")
    if plan.get("exact_stock_removals") != expected_recipes or patch.get("exact_stock_removals") != expected_recipes:
        failures.append("exact nine stock removals drifted")
    if plan.get("automatic_managed_ids_to_retire") != expected_owners or patch.get("automatic_managed_ids_to_retire") != expected_owners:
        failures.append("eight automatic-owner retirements drifted")
    if plan.get("assignment_edits") != [] or patch.get("assignment_edits") != []:
        failures.append("foundry batch must not edit assignments")
    if patch.get("decision") != plan.get("decision"):
        failures.append("patch decision diverged from plan")

    outputs = [builder.output_id(recipe.get("output")) for recipe in proposals if isinstance(recipe, dict)]
    if len(outputs) != len(expected_outputs) or set(outputs) != set(expected_outputs):
        failures.append("replacement contracts do not own each output exactly once")
    if sum(recipe.get("type") == "compacting" for recipe in proposals) != 7:
        failures.append("foundry redesign must contain seven compacting contracts")
    if sum(recipe.get("type") == "sequenced_assembly" for recipe in proposals) != 1:
        failures.append("foundry redesign must contain one sequenced assembly")
    for recipe in proposals:
        if not isinstance(recipe, dict):
            failures.append("replacement contract contains a non-object")
            continue
        output = builder.output_id(recipe.get("output"))
        if recipe.get("node") != builder.ASSIGNMENT_BY_OUTPUT[output]:
            failures.append(f"{output}: reviewed node drifted")
        if recipe.get("phase") != "Steel & Petroleum":
            failures.append(f"{output}: phase drifted")
        if recipe.get("remove") != list(builder.STOCK_RECIPE_IDS[output]):
            failures.append(f"{output}: exact removal ownership drifted")
        if recipe.get("exclusive_output") is not True:
            failures.append(f"{output}: exclusive output protection disappeared")
        if recipe.get("type") == "compacting" and recipe.get("machine") != "createcasing:industrial_iron_press":
            failures.append(f"{output}: compacting left the Industrial-Iron press")
        for value in recipe_inputs(recipe):
            if not value.startswith("#") and value not in item_ids:
                failures.append(f"{output}: ingredient is absent from the installed catalog: {value}")
        if recipe.get("type") == "sequenced_assembly":
            machines = {
                step.get("machine")
                for step in recipe.get("steps", [])
                if isinstance(step, dict)
            }
            if machines != {
                "createcasing:industrial_iron_deployer",
                "createcasing:industrial_iron_press",
            }:
                failures.append(f"{output}: sequence left the Industrial-Iron line")

    proposal_by_output = {builder.output_id(recipe["output"]): recipe for recipe in proposals}
    required_gate_inputs = {
        "createmetallurgy:casting_table": {"tfmg:casting_basin", "tfmg:fireproof_bricks"},
        "createmetallurgy:casting_basin": {"tfmg:casting_basin", "tfmg:fireproof_bricks", "tfmg:cast_iron_frame"},
        "createmetallurgy:foundry_basin": {"tfmg:fireproof_bricks", "tfmg:steel_mechanism"},
        "createmetallurgy:foundry_lid": {"tfmg:fireproof_bricks", "tfmg:steel_mechanism"},
        "createmetallurgy:foundry_mixer": {"tfmg:industrial_mixer", "tfmg:steel_mechanism"},
        "modernfoundry:scorched_basin": {"createmetallurgy:casting_basin", "tfmg:steel_mechanism"},
        "modernfoundry:scorched_drain": {"tfmg:steel_pipe", "tfmg:steel_fluid_tank"},
        "modernfoundry:scorched_table": {"createmetallurgy:casting_table", "tfmg:heavy_plate"},
    }
    for output, required in required_gate_inputs.items():
        actual = recipe_inputs(proposal_by_output.get(output, {}))
        if not required <= actual:
            failures.append(f"{output}: TFMG-first physical gates weakened: {sorted(required - actual)}")

    proposal_ids = {
        str(recipe.get("id")): recipe
        for recipe in proposals
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> None:
        if identity in visited:
            return
        if identity in visiting:
            failures.append(f"same-batch foundry dependency cycle reaches {identity}")
            return
        visiting.add(identity)
        for dependency in proposal_ids[identity].get("depends_on", []):
            if dependency in proposal_ids:
                visit(dependency)
        visiting.remove(identity)
        visited.add(identity)

    for identity in proposal_ids:
        visit(identity)

    producers_by_output: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        for output in builder.split_refs(row.get("outputs", "")):
            producers_by_output.setdefault(output, []).append(row)
    candidate_set = set(builder.CANDIDATE_OUTPUTS)
    for recipe in proposals:
        output = builder.output_id(recipe["output"])
        for ingredient in recipe_inputs(recipe):
            producers = producers_by_output.get(ingredient, [])
            if producers and all(
                builder.split_refs(row.get("inputs", "")) & candidate_set
                for row in producers
            ):
                failures.append(
                    f"{output}: every catalog producer for {ingredient} consumes a candidate endpoint"
                )

    actual_assignments = assigned_nodes(assignments)
    for output, node in builder.ASSIGNMENT_BY_OUTPUT.items():
        if actual_assignments.get(output) != node:
            failures.append(f"{output}: assignment drifted from {node}")

    for marker in (
        "'c:ingots/steel': ['tfmg:steel_ingot']",
        "createmetallurgy:casting_in_table/steel/ingot",
        "industrial_colonies:steel/create_metallurgy_ingot_casting",
    ):
        if marker not in canonicalization_text:
            failures.append(f"steel canonicalization boundary disappeared: {marker}")
    return failures


def validate_implementation(
    plan: dict[str, Any],
    patch: dict[str, Any],
    seed: dict[str, Any],
    manifest: dict[str, Any],
    compiled: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []
    if patch.get("status") != "implemented":
        failures.append("implemented plan requires implemented patch status")
    proposals = plan["replacement_contracts"]
    seed_by_id = {
        row.get("id"): row
        for row in seed.get("recipes", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    for proposal in proposals:
        if seed_by_id.get(proposal["id"]) != proposal:
            failures.append(f"implemented seed contract drifted: {proposal['id']}")
    manifest_rows = [row for row in manifest.get("recipes", []) if isinstance(row, dict)]
    manifest_ids = {str(row.get("id")) for row in manifest_rows}
    manifest_by_id = {str(row.get("id")): row for row in manifest_rows}
    for proposal in proposals:
        actual = manifest_by_id.get(proposal["id"])
        if actual is None:
            failures.append(f"implemented manifest contract is absent: {proposal['id']}")
            continue
        for field in ("node", "phase", "order", "type", "machine", "input", "transitional", "loops", "steps", "inputs", "output", "remove", "exclusive_output"):
            if field in proposal and actual.get(field) != proposal.get(field):
                failures.append(f"implemented manifest field drifted: {proposal['id']} {field}")
    for output in builder.CANDIDATE_OUTPUTS:
        owners = [
            row for row in manifest_rows
            if isinstance(row.get("output"), (str, dict))
            and builder.output_id(row["output"]) == output
        ]
        if len(owners) != 1 or owners[0].get("id") not in {row["id"] for row in proposals}:
            failures.append(f"{output}: manifest must retain exactly one reviewed owner")
    surviving = sorted(set(plan["automatic_managed_ids_to_retire"]) & manifest_ids)
    if surviving:
        failures.append(f"automatic foundry owners survived rebuild: {surviving}")
    removals = {
        str(recipe_id)
        for row in manifest_rows
        for recipe_id in row.get("remove", [])
    } | {str(value) for value in manifest.get("additional_removals", [])}
    missing = sorted(set(plan["exact_stock_removals"]) - removals)
    if missing:
        failures.append(f"exact foundry stock removals failed to compile: {missing}")
    preserved = sorted(set(plan["exact_stock_removals"]) & set(seed.get("preserve_recipe_ids", [])))
    if preserved:
        failures.append(f"foundry stock removals conflict with preserve list: {preserved}")
    if compiled is not None:
        cards = [
            row for row in compiled.get("recipes", [])
            if isinstance(row, dict) and row.get("recipeId") in {proposal["id"] for proposal in proposals}
        ]
        if len(cards) != 8:
            failures.append(f"compiled foundry card count drifted: {len(cards)}")
        type_counts = {
            kind: sum(card.get("type") == kind for card in cards)
            for kind in ("kjsgen:create_compacting", "kjsgen:create_sequenced_assembly")
        }
        if type_counts != {
            "kjsgen:create_compacting": 7,
            "kjsgen:create_sequenced_assembly": 1,
        }:
            failures.append(f"compiled foundry card types drifted: {type_counts}")
        for card in cards:
            slots = card.get("slots", {})
            if card.get("type") == "kjsgen:create_compacting":
                if slots.get("__machine_process_compacting", {}).get("id") != "createcasing:industrial_iron_press":
                    failures.append(f"compiled compacting machine drifted: {card.get('recipeId')}")
            elif card.get("recipeId") == "industrial_colonies:foundry_routes/create_metallurgy_foundry_mixer":
                deployers = [
                    value.get("id") for key, value in slots.items()
                    if key.startswith("__machine_step_") and key.endswith("_deploying") and isinstance(value, dict)
                ]
                presses = [
                    value.get("id") for key, value in slots.items()
                    if key.startswith("__machine_step_") and key.endswith("_pressing") and isinstance(value, dict)
                ]
                if deployers != ["createcasing:industrial_iron_deployer"] * 4 or presses != ["createcasing:industrial_iron_press"]:
                    failures.append("compiled foundry mixer left the exact Industrial-Iron sequence")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--catalog", type=Path, default=builder.DEFAULT_CATALOG)
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    plan = builder.load_json(project / PLAN.name)
    patch = builder.load_json(project / PATCH.name)
    automatic = builder.load_json(project / builder.AUTOMATIC_AUDIT.name)
    rows = builder.load_rows(args.catalog.resolve() / "recipes.csv")
    item_ids = {
        row["item_id"]
        for row in builder.load_rows(args.catalog.resolve() / "items.csv")
    }
    assignments = builder.load_json(project / "progression/machine_node_assignments.json")
    canonicalization = (
        project / "pack-scripts/server_scripts/industrial_steel_canonicalization.js"
    ).read_text(encoding="utf-8")
    failures = validate_review(
        plan,
        patch,
        automatic,
        rows,
        item_ids,
        assignments,
        canonicalization,
    )
    seed_path = args.seed.resolve() if args.seed else project / "progression/managed_recipe_overhaul.seed.json"
    manifest_path = args.manifest.resolve() if args.manifest else project / "progression/managed_recipe_overhaul.json"
    compiled_path = args.compiled.resolve() if args.compiled else project / "pack-kjsgen/default.managed.json"
    failures.extend(
        validate_implementation(
            plan,
            patch,
            builder.load_json(seed_path),
            builder.load_json(manifest_path),
            builder.load_json(compiled_path),
        )
    )
    if failures:
        print("FAIL: foundry route-parity redesign", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    evidence = plan["route_evidence"]
    print("Foundry route-parity redesign passed.")
    print(
        f"- Create Metallurgy: {evidence['create_metallurgy']['casting_and_alloy_recipe_count']} "
        f"casting/alloy recipes; {evidence['create_metallurgy']['exclusive_output_reference_count']} exclusive references"
    )
    print(
        f"- Modern Foundry: {evidence['modernfoundry']['table_basin_route_recipe_count']} "
        f"table/basin routes; {evidence['modernfoundry']['exclusive_output_reference_count']} exclusive references"
    )
    print("- 8 TFMG-gated replacements, 9 exact removals, 0 subsystem deletions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
