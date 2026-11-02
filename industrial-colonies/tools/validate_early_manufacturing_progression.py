#!/usr/bin/env python3
"""Validate the implemented primitive-to-Brass manufacturing spine."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_PLAN = PROJECT / "EARLY_MANUFACTURING_AUDIT.plan.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"

STEAM_PHASE = "Steam & Brass"
REPHASED_NODES = {
    "CR01 — Advanced Redstone",
    "CR01 — Advanced Mechanical Technology",
    "CR01 — Early Crushing Technology",
}
DAYLIGHT_RECIPES = {
    "modernfoundry:common/glass/vanilla/daylight_detector",
    "minecraft:daylight_detector",
}
SHEETS = {
    "create:iron_sheet",
    "create:copper_sheet",
    "create:golden_sheet",
    "create:brass_sheet",
}
EXISTING_ENCASED_CONTRACTS: dict[str, dict[str, Any]] = {
    "industrial_colonies:manufacturing/copper_press": {
        "phase": STEAM_PHASE,
        "order": 10,
        "type": "shaped",
        "pattern": ["CSC", "AMA", "GKG"],
        "key": {"C": "create:copper_sheet", "S": "create:shaft", "A": "create:andesite_alloy", "M": "create:mechanical_press", "G": "create:cogwheel", "K": "create:copper_casing"},
        "output": "createcasing:copper_press",
        "remove": ["createcasing:crafting/press/copper"],
        "exclusive_output": True,
    },
    "industrial_colonies:manufacturing/copper_deployer": {
        "phase": STEAM_PHASE,
        "order": 11,
        "type": "shaped",
        "pattern": ["CEC", "ADA", "SKS"],
        "key": {"C": "create:copper_sheet", "E": "create:electron_tube", "A": "create:andesite_alloy", "D": "create:deployer", "S": "create:shaft", "K": "create:copper_casing"},
        "output": "createcasing:copper_deployer",
        "remove": ["createcasing:crafting/deployer/copper"],
        "exclusive_output": True,
    },
    "industrial_colonies:manufacturing/brass_press": {
        "phase": STEAM_PHASE,
        "order": 20,
        "type": "shaped",
        "pattern": ["BMB", "EPE", "GKG"],
        "key": {"B": "create:brass_sheet", "M": "create:precision_mechanism", "E": "create:electron_tube", "P": "createcasing:copper_press", "G": "create:cogwheel", "K": "create:brass_casing"},
        "output": "createcasing:brass_press",
        "remove": ["createcasing:crafting/press/brass"],
        "exclusive_output": True,
    },
    "industrial_colonies:manufacturing/brass_deployer": {
        "phase": STEAM_PHASE,
        "order": 21,
        "type": "shaped",
        "pattern": ["BEB", "MDM", "GKG"],
        "key": {"B": "create:brass_sheet", "E": "create:electron_tube", "M": "create:precision_mechanism", "D": "createcasing:copper_deployer", "G": "create:cogwheel", "K": "create:brass_casing"},
        "output": "createcasing:brass_deployer",
        "remove": ["createcasing:crafting/deployer/brass"],
        "exclusive_output": True,
    },
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def output_stack(value: Any) -> tuple[str, int]:
    if isinstance(value, str):
        parts = value.split(maxsplit=1)
        if len(parts) == 2 and parts[0].endswith("x") and parts[0][:-1].isdigit():
            return parts[1], int(parts[0][:-1])
        return value, 1
    if isinstance(value, dict):
        return str(value.get("id", "")), int(value.get("count", 1))
    return "", 0


def recipes_by_id(data: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(recipe["id"]): recipe
        for recipe in data.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def recipes_by_output(data: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for recipe in data.get("recipes", []):
        if not isinstance(recipe, dict):
            continue
        output, _count = output_stack(recipe.get("output"))
        result.setdefault(output, []).append(recipe)
    return result


def all_removals(data: Mapping[str, Any]) -> list[str]:
    removals = [
        removal
        for recipe in data.get("recipes", [])
        if isinstance(recipe, dict)
        for removal in recipe.get("remove", [])
        if isinstance(removal, str)
    ]
    removals.extend(
        removal
        for removal in data.get("additional_removals", [])
        if isinstance(removal, str)
    )
    return removals


def ingredient_values(recipe: Mapping[str, Any]) -> set[str]:
    values = {
        str(value)
        for value in recipe.get("key", {}).values()
        if isinstance(value, str)
    }
    values.update(
        str(value)
        for field in ("inputs", "ingredients")
        for value in recipe.get(field, [])
        if isinstance(value, str)
    )
    return values


def output_to_node(assignments: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for node, entry in assignments.get("nodes", {}).items():
        if isinstance(entry, dict):
            for output in entry.get("unlocks", []):
                if isinstance(output, str):
                    result[output] = str(node)
    return result


def validate_capability_graph(errors: list[str]) -> None:
    edges = {
        "mechanical_press": set(),
        "mechanical_pump": {"mechanical_press"},
        "steam_engine": {"mechanical_pump"},
        "heated_brass": {"mechanical_press"},
        "deployer": {"heated_brass"},
        "mechanical_crafter": {"heated_brass"},
        "precision_mechanism": {"deployer"},
        "crushing_wheel": {"mechanical_crafter"},
        "track": {"deployer", "mechanical_press"},
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"early manufacturing capability graph contains a cycle at {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for parent in edges[node]:
            visit(parent)
        visiting.remove(node)
        visited.add(node)

    for node in edges:
        visit(node)


def validate_contract(
    seed: Mapping[str, Any],
    plan: Mapping[str, Any],
    assignments: Mapping[str, Any],
    manifest: Mapping[str, Any] | None = None,
    catalog_recipe_ids: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    batch = plan.get("implementation_batch", {})
    expected_recipes = batch.get("bounded_recipe_replacements", [])
    source_recipes = recipes_by_id(seed)
    source_by_output = recipes_by_output(seed)
    source_removals = all_removals(seed)
    source_removal_counts = Counter(source_removals)

    if plan.get("status") != "implemented_in_seed":
        errors.append("audit status is not implemented_in_seed")
    if len(expected_recipes) != 5:
        errors.append(f"implementation plan has {len(expected_recipes)} recipes; expected 5")
    if len(batch.get("exact_retirements", [])) != 4:
        errors.append("implementation plan must contain exactly four hammering retirements")

    for expected in expected_recipes:
        identity = str(expected["recipe_id"])
        actual = source_recipes.get(identity)
        if actual is None:
            errors.append(f"missing reviewed early recipe {identity}")
            continue
        output, count = output_stack(actual.get("output"))
        expected_output, expected_count = output_stack(expected.get("output"))
        owners = source_by_output.get(expected_output, [])
        if len(owners) != 1 or owners[0].get("id") != identity:
            errors.append(f"{expected_output} does not have exactly one explicit owner: {identity}")
        for field in ("phase", "order", "type", "pattern", "key"):
            if actual.get(field) != expected.get(field):
                errors.append(f"{identity} changed reviewed field {field}")
        if (output, count) != (expected_output, expected_count):
            errors.append(f"{identity} changed reviewed output/count")
        if actual.get("remove") != expected.get("remove_exact"):
            errors.append(f"{identity} changed its exact stock removal")
        if actual.get("exclusive_output") is not True:
            errors.append(f"{identity} is not exclusive_output")
        if actual.get("depends_on", []) != expected.get("depends_on", []):
            errors.append(f"{identity} changed reviewed capability dependencies")
        for removal in expected.get("remove_exact", []):
            if source_removal_counts[removal] != 1:
                errors.append(f"{removal} has {source_removal_counts[removal]} removal owners")

    press = source_recipes.get("industrial_colonies:mechanical/mechanical_press", {})
    if ingredient_values(press) & SHEETS:
        errors.append("Mechanical Press circularly requires a sheet")
    for identity in (
        "industrial_colonies:brass/deployer",
        "industrial_colonies:brass/mechanical_crafter",
    ):
        if "create:precision_mechanism" in ingredient_values(source_recipes.get(identity, {})):
            errors.append(f"{identity} circularly requires a Precision Mechanism")

    additional = seed.get("additional_removals", [])
    for retirement in batch.get("exact_retirements", []):
        if additional.count(retirement) != 1:
            errors.append(f"hammering retirement {retirement} must occur exactly once")
        if source_removal_counts[retirement] != 1:
            errors.append(f"hammering retirement {retirement} has multiple removal owners")

    phases = seed.get("phase_by_node", {})
    for node in REPHASED_NODES:
        if phases.get(node) != STEAM_PHASE:
            errors.append(f"{node} is not mapped to {STEAM_PHASE}")
    assigned = output_to_node(assignments)
    for output in batch.get("assignment_rephase", {}).get("outputs", []):
        node = assigned.get(output)
        if node is None or phases.get(node) != STEAM_PHASE:
            errors.append(f"{output} is not assigned through a Steam & Brass node")

    excluded = set(seed.get("exclude_outputs", []))
    unmanaged = set(batch.get("leave_stock_unmanaged", []))
    missing_unmanaged = sorted(unmanaged - excluded)
    if missing_unmanaged:
        errors.append(f"stock outputs are still eligible for auto ownership: {missing_unmanaged}")
    target_outputs = {output_stack(recipe.get("output"))[0] for recipe in expected_recipes}
    conflicting_exclusions = sorted(target_outputs & excluded)
    if conflicting_exclusions:
        errors.append(f"explicit early outputs are also excluded: {conflicting_exclusions}")

    required_preserves = set(batch.get("must_preserve_installed_recipes", []))
    preserved = set(seed.get("preserve_recipe_ids", []))
    missing_preserves = sorted(required_preserves - preserved)
    if missing_preserves:
        errors.append(f"required installed recipe preserves are missing: {missing_preserves}")
    preserve_conflicts = sorted(preserved & set(source_removals))
    if preserve_conflicts:
        errors.append(f"preserved installed recipes are also removed: {preserve_conflicts}")
    if DAYLIGHT_RECIPES & set(source_removals):
        errors.append("a stock Daylight Detector route is removed")

    for identity, expected in EXISTING_ENCASED_CONTRACTS.items():
        actual = source_recipes.get(identity)
        if actual is None:
            errors.append(f"existing Encased upgrade is missing: {identity}")
            continue
        for field, value in expected.items():
            if actual.get(field) != value:
                errors.append(f"existing Encased upgrade changed: {identity}.{field}")

    if catalog_recipe_ids is not None:
        required_catalog_ids = set(plan.get("id_validation", {}).get("catalog_recipe_ids_validated", []))
        missing_catalog_ids = sorted(required_catalog_ids - catalog_recipe_ids)
        if missing_catalog_ids:
            errors.append(f"installed recipe catalog no longer resolves: {missing_catalog_ids}")

    validate_capability_graph(errors)

    if manifest is not None:
        manifest_recipes = recipes_by_id(manifest)
        manifest_by_output = recipes_by_output(manifest)
        manifest_removals = all_removals(manifest)
        manifest_removal_counts = Counter(manifest_removals)
        if set(manifest.get("preserve_recipe_ids", [])) != preserved:
            errors.append("isolated manifest does not carry the source preserve policy")
        for expected in expected_recipes:
            identity = str(expected["recipe_id"])
            output, _count = output_stack(expected.get("output"))
            actual = manifest_recipes.get(identity)
            if actual is None:
                errors.append(f"isolated manifest omitted {identity}")
                continue
            if len(manifest_by_output.get(output, [])) != 1:
                errors.append(f"isolated manifest has competing owners for {output}")
            if actual.get("remove") != expected.get("remove_exact"):
                errors.append(f"isolated manifest changed exact removals for {identity}")
        for output in unmanaged:
            if output in manifest_by_output:
                errors.append(f"isolated manifest still auto-manages stock output {output}")
        for retirement in batch.get("exact_retirements", []):
            if manifest_removal_counts[retirement] != 1:
                errors.append(f"isolated manifest lost exact retirement {retirement}")
        manifest_preserve_conflicts = sorted(preserved & set(manifest_removals))
        if manifest_preserve_conflicts:
            errors.append(
                f"isolated manifest removes preserved recipes: {manifest_preserve_conflicts}"
            )
        if DAYLIGHT_RECIPES & set(manifest_removals):
            errors.append("isolated manifest removes a stock Daylight Detector route")
        for output in batch.get("assignment_rephase", {}).get("outputs", []):
            for owner in manifest_by_output.get(output, []):
                if owner.get("phase") != STEAM_PHASE:
                    errors.append(f"isolated manifest classified {output} before Steam & Brass")

    return errors


def catalog_ids(path: Path) -> set[str]:
    with (path / "recipes.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["recipe_id"] for row in csv.DictReader(handle)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--manifest", type=Path, help="optional isolated generated manifest")
    args = parser.parse_args()

    try:
        seed = load_object(args.seed.resolve())
        plan = load_object(args.plan.resolve())
        assignments = load_object(args.assignments.resolve())
        manifest = load_object(args.manifest.resolve()) if args.manifest else None
        errors = validate_contract(
            seed,
            plan,
            assignments,
            manifest,
            catalog_ids(args.catalog.resolve()),
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(
        "Checked five early manufacturing recipes, four exact hammering retirements, "
        "24 installed preserves, eight rephased outputs, and four existing Encased upgrades."
    )
    if errors:
        print(f"FAIL: {len(errors)} early-manufacturing issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("PASS: the primitive-to-Brass manufacturing spine is explicit, acyclic, and preservation-safe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
