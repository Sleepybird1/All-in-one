#!/usr/bin/env python3
"""Validate retirement of pointless automatic gate rings while keeping stock utilities."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from validate_ae2_transform_hardening import validate_contract as validate_ae2_transforms
from validate_mekanism_factory_restoration_audit import expected_blacklist


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current" / "recipes.csv"
PLAN_PATH = PROJECT / "STOCK_UTILITY_RESTORATION_AUDIT.patch.json"
AUDIT_PATH = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
SEED_PATH = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
ASSIGNMENTS_PATH = PROJECT / "progression" / "machine_node_assignments.json"
MANIFEST_PATH = PROJECT / "progression" / "managed_recipe_overhaul.json"
COMPILED_PATH = PROJECT / "pack-kjsgen" / "default.managed.json"
FACTORY_PLAN_PATH = PROJECT / "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json"
INSTALLER_BLACKLIST_PATH = (
    PROJECT
    / "src/main/resources/data/mekanism/tags/block/blacklist/installer_upgradeable.json"
)

BASE_SEED_SHA256 = "DC13B038A7C4EFA07A4BB12EB0F5A1B95595F41C228B74B34EBB979B3D989494"
IMPLEMENTED_SEED_SHA256 = "66EF6386BB80B7A9DABF30752570F71E8B0BB87DCD25A0E9CC15474878EBBB36"
UNCHANGED_ASSIGNMENTS_SHA256 = "329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E"
TIER_INSTALLER_RECIPES = {
    "mekanism:tier_installer/basic",
    "mekanism:tier_installer/advanced",
    "mekanism:tier_installer/elite",
    "mekanism:tier_installer/ultimate",
}
URANIUM_UTILITY_RECIPES = {
    "create:splashing/mekanism/crushed_raw_uranium",
    "mekanism:processing/uranium/nugget/from_ingot",
    "mekanism:processing/uranium/raw_storage_blocks/from_raw",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def catalog_recipe_ids(path: Path) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {row["recipe_id"] for row in csv.DictReader(handle)}


def assigned_outputs(assignments: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for node in assignments.get("nodes", {}).values():
        if isinstance(node, dict):
            result.update(value for value in node.get("unlocks", []) if isinstance(value, str))
    return result


def expected_from_audit(audit: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    rows = [
        row
        for row in audit.get("entries", [])
        if isinstance(row, dict) and row.get("classification") == "runtime_artifact_leave_stock"
    ]
    outputs = {str(row["output"]) for row in rows}
    recipes = {
        str(recipe_id)
        for row in rows
        for recipe_id in row.get("exact_removals", [])
    }
    owners = {str(row["managed_id"]) for row in rows}
    return outputs, recipes, owners


def validate_plan_parity(
    plan: dict[str, Any],
    audit: dict[str, Any],
    installed_recipe_ids: set[str],
    assignment_outputs: set[str],
) -> list[str]:
    errors: list[str] = []
    expected_outputs, expected_recipes, expected_owners = expected_from_audit(audit)
    outputs = set(plan.get("outputs_to_exclude", []))
    recipes = set(plan.get("recipe_ids_to_preserve", []))
    owners = set(plan.get("automatic_managed_ids_to_retire", []))
    entries = plan.get("entries", [])

    if plan.get("schema_version") != 1:
        errors.append("patch plan schema_version must be 1")
    if plan.get("batch_id") != "stock_utility_restoration":
        errors.append("patch plan batch_id is incorrect")
    if plan.get("status") != "implemented":
        errors.append("patch plan status must be implemented")
    if outputs != expected_outputs:
        errors.append("outputs_to_exclude does not exactly match the automatic-audit classification")
    if recipes != expected_recipes:
        errors.append("recipe_ids_to_preserve does not exactly match all audited source producers")
    if owners != expected_owners:
        errors.append("automatic_managed_ids_to_retire does not exactly match the audited owners")
    if len(entries) != len(expected_outputs):
        errors.append("patch-plan entry count does not match the audited output count")
    else:
        entry_outputs = {
            str(entry.get("output")) for entry in entries if isinstance(entry, dict)
        }
        if entry_outputs != expected_outputs:
            errors.append("patch-plan entries do not cover each audited output exactly once")

    missing_catalog = sorted(recipes - installed_recipe_ids)
    if missing_catalog:
        errors.append(f"audited source recipes are missing from the pinned catalog: {missing_catalog}")
    missing_assignments = sorted(outputs - assignment_outputs)
    if missing_assignments:
        errors.append(f"utility outputs lost their documentation assignments: {missing_assignments}")
    return errors


def validate_implementation_metadata(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "base_seed_sha256": BASE_SEED_SHA256,
        "implemented_seed_sha256": IMPLEMENTED_SEED_SHA256,
        "unchanged_assignments_sha256": UNCHANGED_ASSIGNMENTS_SHA256,
        "exclude_outputs_added": 56,
        "preserve_recipe_ids_added": 65,
        "preserve_recipe_ids_already_present": 12,
        "replacement_recipes_added": 0,
        "assignment_changes": 0,
    }
    implementation = plan.get("implementation")
    if not isinstance(implementation, dict):
        return ["implemented patch plan is missing implementation metadata"]
    for key, value in expected.items():
        if implementation.get(key) != value:
            errors.append(f"implementation metadata {key} changed")
    isolated = implementation.get("isolated_result")
    expected_isolated = {
        "managed_recipes": 329,
        "automatic_recipes": 86,
        "compiled_cards": 397,
        "exact_removals": 661,
        "skipped_assigned_outputs": 33,
        "dag_warnings": 0,
    }
    if isolated != expected_isolated:
        errors.append("isolated implementation result changed")
    return errors


def output_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value.split("x ", 1)[-1].strip()
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return value["id"]
    return None


def compiled_output_ids(compiled: dict[str, Any]) -> set[str]:
    results: set[str] = set()
    for card in compiled.get("recipes", []):
        if not isinstance(card, dict):
            continue
        slots = card.get("slots")
        if not isinstance(slots, dict):
            continue
        for key in ("output", "output0", "outItem"):
            slot = slots.get(key)
            if isinstance(slot, dict) and isinstance(slot.get("id"), str):
                results.add(str(slot["id"]))
                break
    return results


def compiled_removals(compiled: dict[str, Any]) -> set[str]:
    return {
        str(entry["recipeId"])
        for entry in compiled.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }


def validate_implementation(
    plan: dict[str, Any], seed: dict[str, Any], manifest: dict[str, Any],
    compiled: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    outputs = set(plan.get("outputs_to_exclude", []))
    recipes = set(plan.get("recipe_ids_to_preserve", []))
    owners = set(plan.get("automatic_managed_ids_to_retire", []))
    seed_excluded = set(seed.get("exclude_outputs", []))
    seed_preserved = set(seed.get("preserve_recipe_ids", []))

    if len(seed.get("exclude_outputs", [])) != len(seed_excluded):
        errors.append("seed exclude_outputs contains duplicates")
    if len(seed.get("preserve_recipe_ids", [])) != len(seed_preserved):
        errors.append("seed preserve_recipe_ids contains duplicates")

    if not outputs <= seed_excluded:
        errors.append(f"seed is missing excluded utility outputs: {sorted(outputs - seed_excluded)}")
    if not recipes <= seed_preserved:
        errors.append(f"seed is missing preserved stock recipes: {sorted(recipes - seed_preserved)}")

    explicit_outputs = {
        result
        for spec in seed.get("recipes", [])
        if isinstance(spec, dict)
        for value in (
            spec.get("output"),
            *(spec.get("outputs", []) if isinstance(spec.get("outputs"), list) else []),
        )
        if (result := output_id(value)) is not None
    }
    family_outputs = {
        str(entry["output"])
        for family in seed.get("machine_families", [])
        if isinstance(family, dict)
        for entry in family.get("recipes", [])
        if isinstance(entry, dict) and isinstance(entry.get("output"), str)
    }
    claimed = sorted(outputs & (explicit_outputs | family_outputs))
    if claimed:
        errors.append(f"restored stock outputs are still claimed by explicit/family owners: {claimed}")

    manifest_recipes = [row for row in manifest.get("recipes", []) if isinstance(row, dict)]
    surviving_owners = sorted(
        owners & {str(row.get("id")) for row in manifest_recipes if row.get("id")}
    )
    if surviving_owners:
        errors.append(f"automatic utility owners survived rebuild: {surviving_owners}")
    removed_ids = {
        str(recipe_id)
        for row in manifest_recipes
        for recipe_id in row.get("remove", [])
    } | {str(value) for value in manifest.get("additional_removals", [])}
    removed_preserves = sorted(recipes & removed_ids)
    if removed_preserves:
        errors.append(f"preserved stock utility recipes are still removed: {removed_preserves}")
    if not recipes <= set(manifest.get("preserve_recipe_ids", [])):
        errors.append("assembled manifest does not retain the complete stock-utility preserve set")
    if compiled is not None:
        compiled_claims = sorted(outputs & compiled_output_ids(compiled))
        if compiled_claims:
            errors.append(f"compiled KJSGen still claims restored stock outputs: {compiled_claims}")
        compiled_removed_preserves = sorted(recipes & compiled_removals(compiled))
        if compiled_removed_preserves:
            errors.append(
                "compiled KJSGen still removes preserved stock utility recipes: "
                f"{compiled_removed_preserves}"
            )
    return errors


def validate_cross_policy_safety(
    project: Path, plan: dict[str, Any], manifest: dict[str, Any], compiled: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    preserves = set(plan.get("recipe_ids_to_preserve", []))
    outputs = set(plan.get("outputs_to_exclude", []))

    if not TIER_INSTALLER_RECIPES <= preserves:
        errors.append("the four exact tier-installer utility recipes are not all preserved")
    if preserves & {
        recipe for recipe in preserves if "uranium" in recipe
    } != URANIUM_UTILITY_RECIPES:
        errors.append("uranium restoration escaped the three reviewed packing/washing utility routes")

    factory_plan = load_json(project / FACTORY_PLAN_PATH.name)
    factory_blacklist, cube_blacklist, excluded_transmitters = expected_blacklist(factory_plan)
    required_blacklist = factory_blacklist | cube_blacklist
    blacklist = load_json(project / INSTALLER_BLACKLIST_PATH.relative_to(PROJECT))
    values = blacklist.get("values")
    if (
        blacklist.get("replace") is not False
        or not isinstance(values, list)
        or len(values) != 49
        or len(values) != len(set(values))
        or set(values) != required_blacklist
        or set(values) & excluded_transmitters
    ):
        errors.append("the exact 49-block Factory/Energy Cube installer blacklist changed")

    factory_outputs = {
        f"mekanism:{tier}_{process}_factory"
        for tier in ("basic", "advanced", "elite", "ultimate")
        for process in (
            "combining", "compressing", "crushing", "enriching", "infusing",
            "injecting", "purifying", "sawing", "smelting",
        )
    }
    if outputs & factory_outputs:
        errors.append("stock-utility restoration wrongly excludes a managed Mekanism Factory")

    errors.extend(f"AE2/AppMek transform safety: {error}" for error in validate_ae2_transforms(manifest, compiled))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--assignments", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    plan = load_json((args.plan or project / PLAN_PATH.name).resolve())
    audit = load_json((args.audit or project / AUDIT_PATH.name).resolve())
    seed = load_json((args.seed or project / "progression" / SEED_PATH.name).resolve())
    assignments = load_json(
        (args.assignments or project / "progression" / ASSIGNMENTS_PATH.name).resolve()
    )
    manifest = load_json(
        (args.manifest or project / "progression" / MANIFEST_PATH.name).resolve()
    )
    compiled = load_json(
        (args.compiled or project / "pack-kjsgen" / COMPILED_PATH.name).resolve()
    )
    errors = validate_plan_parity(
        plan,
        audit,
        catalog_recipe_ids(args.catalog.resolve()),
        assigned_outputs(assignments),
    )
    errors.extend(validate_implementation_metadata(plan))
    errors.extend(validate_implementation(plan, seed, manifest, compiled))
    errors.extend(validate_cross_policy_safety(project, plan, manifest, compiled))

    if errors:
        print("FAIL: stock utility restoration audit", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    outputs = len(plan["outputs_to_exclude"])
    recipes = len(plan["recipe_ids_to_preserve"])
    print(
        f"PASS: implemented restoration keeps {outputs} stock utility outputs through "
        f"{recipes} exact installed recipe IDs without deleting their assignments."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
