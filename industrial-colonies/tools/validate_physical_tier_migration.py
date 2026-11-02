#!/usr/bin/env python3
"""Validate manufacturing-environment and complexity progression.

The retired script-scanning validator expected recipes in hand-written KubeJS
files and therefore rejected the current managed KJSGen architecture. This
version validates the real authority: the expanded managed manifest plus its
compiled KJSGen project. It proves that casing families form a forward upgrade
chain, important processes use their intended physical machines, and advanced
machine construction retains reviewed mechanical-crafting dimensions.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from validate_physical_progression import load_object, recipe_ingredients, run_core_validation


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"
DEFAULT_REPORT = PROJECT / "build" / "reports" / "physical-tier-migration-validation.json"

FAMILY_CHAIN = [
    ("copper", "native Create", "Steam & Brass", "create:electron_tube", "create:shaft"),
    ("brass", "Copper", "Electrical Manufacturing", "tfmg:circuit_board", "create:precision_mechanism"),
    ("railway", "Brass", "Electrical Manufacturing", "tfmg:circuit_board", "tfmg:steel_mechanism"),
    ("industrial_iron", "Railway", "Mekanized Industry", "mekanism:basic_control_circuit", "tfmg:electric_motor"),
    ("weathered_iron", "Industrial Iron", "High-Energy Grid", "mekanism:advanced_control_circuit", "ae2:calculation_processor"),
    ("refined_radiance", "Weathered Iron", "Nuclear Engineering", "mekanism:elite_control_circuit", "ae2:engineering_processor"),
]

MACHINE_ROUTES = {
    "industrial_colonies:electronics/coated_circuit_board": (
        "deploying",
        "createcasing:copper_deployer",
    ),
    "industrial_colonies:electronics/printed_silicon": (
        "compacting",
        "createcasing:brass_press",
    ),
    "industrial_colonies:electronics/stress_circuit_board": (
        "pressing",
        "createcasing:copper_press",
    ),
    "industrial_colonies:electronics/advanced_stress_circuit_board": (
        "compacting",
        "createcasing:brass_press",
    ),
    "industrial_colonies:mekanism/advanced_control_circuit": (
        "compacting",
        "createcasing:industrial_iron_press",
    ),
    "industrial_colonies:mekanism/elite_control_circuit": (
        "compacting",
        "createcasing:weathered_iron_press",
    ),
    "industrial_colonies:mekanism/ultimate_control_circuit": (
        "compacting",
        "createcasing:weathered_iron_press",
    ),
    "industrial_colonies:nuclear/chromatic_compound": (
        "mixing",
        "createcasing:weathered_iron_mixer",
    ),
    "industrial_colonies:nuclear/refined_radiance": (
        "compacting",
        "createcasing:weathered_iron_press",
    ),
    "industrial_colonies:nuclear/refined_radiance_casing": (
        "deploying",
        "createcasing:weathered_iron_deployer",
    ),
}

# These two propellant-handling components are intentionally compact assemblies
# inside the otherwise-large Mechanical Crafting program. Pin both identity and
# dimensions so this cannot become a general escape from the 5x5 floor.
COMPACT_MECHANICAL_RECIPES = {
    "industrial_colonies:space/propulsion/hose_anchor": (3, 3),
    "industrial_colonies:space/propulsion/engine_pipes": (5, 3),
}


def validate_tier_contract(
    manifest: Mapping[str, Any], specs: Sequence[Mapping[str, Any]]
) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    families = manifest.get("machine_families", [])
    if not isinstance(families, list):
        return ["manifest.machine_families must be an array"], {}

    actual_chain = [
        (
            family.get("tier"),
            family.get("source_tier"),
            family.get("phase"),
            family.get("control"),
            family.get("drive"),
        )
        for family in families
        if isinstance(family, dict)
    ]
    if actual_chain != FAMILY_CHAIN:
        errors.append(
            "manufacturing family chain changed; "
            f"expected={FAMILY_CHAIN}, found={actual_chain}"
        )

    expanded = {str(recipe.get("id", "")): recipe for recipe in specs}
    family_counts: Counter[str] = Counter()
    for family in families:
        if not isinstance(family, dict):
            continue
        tier = str(family.get("tier", ""))
        entries = family.get("recipes", [])
        source_items = family.get("source_items", {})
        if not isinstance(entries, list) or len(entries) < 10:
            errors.append(f"manufacturing family {tier} has fewer than 10 functional upgrades")
            continue
        if not isinstance(source_items, dict):
            errors.append(f"manufacturing family {tier} has no source-item map")
            continue
        seen_kinds: set[str] = set()
        family_ingredients: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"manufacturing family {tier} contains a non-object recipe")
                continue
            kind = str(entry.get("kind", ""))
            if kind in seen_kinds:
                errors.append(f"manufacturing family {tier} repeats machine kind {kind}")
            seen_kinds.add(kind)
            if kind not in source_items and not entry.get("base"):
                errors.append(f"manufacturing family {tier}/{kind} has no prior machine input")
            output = str(entry.get("output", ""))
            if not output.startswith(f"createcasing:{tier}_"):
                errors.append(f"manufacturing family {tier}/{kind} has wrong output {output}")
            if not entry.get("remove"):
                errors.append(f"manufacturing family {tier}/{kind} has no exact stock removal")

            recipe_id = str(
                entry.get("id", f"industrial_colonies:manufacturing/{tier}/{kind}")
            )
            recipe = expanded.get(recipe_id)
            if recipe is None:
                errors.append(f"expanded manufacturing recipe is missing: {recipe_id}")
                continue
            family_counts[tier] += 1
            ingredients = recipe_ingredients(recipe)
            family_ingredients.update(ingredients)
            required = {
                str(family.get("casing", "")),
                str(family.get("plate", "")),
                str(family.get("drive", "")),
                str(entry.get("base") or source_items.get(kind, "")),
            }
            missing = sorted(value for value in required if value and value not in ingredients)
            if missing:
                errors.append(f"{recipe_id} is missing family upgrade inputs {missing}")
        control = str(family.get("control", ""))
        if control and control not in family_ingredients:
            errors.append(f"manufacturing family {tier} never consumes its control component {control}")

    # Complex machine construction is deliberately large. Variable-height
    # recipes are supported above the 5x5 industrial floor, with two exact,
    # reviewed propellant-handling component exceptions.
    mechanical_count = 0
    dimension_counts: Counter[str] = Counter()
    for recipe in specs:
        if recipe.get("type") != "mechanical_crafting":
            continue
        mechanical_count += 1
        pattern = recipe.get("pattern", [])
        if not isinstance(pattern, list) or not pattern:
            errors.append(f"{recipe.get('id')} has no mechanical-crafting pattern")
            continue
        height = len(pattern)
        width = max((len(row) for row in pattern if isinstance(row, str)), default=0)
        dimension_counts[f"{width}x{height}"] += 1
        compact_dimensions = COMPACT_MECHANICAL_RECIPES.get(str(recipe.get("id", "")))
        if compact_dimensions is not None:
            if (
                (width, height) != compact_dimensions
                or any(not isinstance(row, str) or len(row) != width for row in pattern)
            ):
                errors.append(
                    f"{recipe.get('id')} changed its reviewed compact grid from "
                    f"{compact_dimensions[0]}x{compact_dimensions[1]} to {width}x{height}"
                )
            continue
        if width < 5 or height < 5 or any(not isinstance(row, str) or len(row) != width for row in pattern):
            errors.append(
                f"{recipe.get('id')} escaped the large-grid contract with {width}x{height}"
            )
    if mechanical_count < 100:
        errors.append(f"only {mechanical_count} managed large-grid recipes remain")

    for recipe_id, (recipe_type, machine) in MACHINE_ROUTES.items():
        recipe = expanded.get(recipe_id)
        if recipe is None:
            errors.append(f"machine-routed milestone is missing: {recipe_id}")
            continue
        if recipe.get("type") != recipe_type or recipe.get("machine") != machine:
            errors.append(
                f"{recipe_id} route changed; expected {recipe_type} on {machine}, "
                f"found {recipe.get('type')} on {recipe.get('machine')}"
            )

    board = expanded.get("industrial_colonies:electronics/circuit_board", {})
    for index, step in enumerate(board.get("steps", []) if isinstance(board, dict) else []):
        if not isinstance(step, dict) or step.get("op") != "deploying":
            errors.append(f"TFMG circuit-board sequence step {index} is not deploying")
        elif step.get("machine") != "createcasing:copper_deployer":
            errors.append(f"TFMG circuit-board step {index} escaped the Copper Deployer")

    stats = {
        "machine_families": len(families),
        "family_upgrade_recipes": sum(family_counts.values()),
        "large_mechanical_recipes": mechanical_count,
        **{f"mechanical_{key}": value for key, value in sorted(dimension_counts.items())},
    }
    return errors, stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_COMPILED)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    stats: dict[str, int] = {}
    try:
        manifest = load_object(args.manifest.resolve())
        compiled = load_object(args.output.resolve())
        specs, core_errors, core_warnings, removal_count = run_core_validation(
            manifest, compiled
        )
        errors.extend(f"managed core: {error}" for error in core_errors)
        warnings.extend(f"managed core: {warning}" for warning in core_warnings)
        contract_errors, stats = validate_tier_contract(manifest, specs)
        errors.extend(contract_errors)
        stats["expanded_managed_recipes"] = len(specs)
        stats["exact_recipe_removals"] = removal_count
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, ImportError) as exc:
        errors.append(str(exc))

    report = {
        "schema_version": 2,
        "authority": "managed_recipe_manufacturing_environments",
        "status": "pass" if not errors else "fail",
        "manifest": str(args.manifest.resolve()),
        "compiled_project": str(args.output.resolve()),
        "statistics": stats,
        "warnings": warnings,
        "errors": errors,
    }
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if errors:
        print(f"FAIL: {len(errors)} manufacturing-tier issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        print(f"Report: {report_path}")
        return 1
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    print(
        "PASS: managed manufacturing tiers progress from Copper through Refined "
        f"Radiance ({stats.get('family_upgrade_recipes', 0)} family upgrades, "
        f"{stats.get('large_mechanical_recipes', 0)} large-grid recipes)."
    )
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
