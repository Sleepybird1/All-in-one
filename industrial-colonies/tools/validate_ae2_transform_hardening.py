#!/usr/bin/env python3
"""Validate AE2/AppMek forward-transform retirement without losing disassembly.

The pack's storage cells and crafting CPUs are rebuilt as managed recipes.
AE2's custom forward-upgrade serializers can otherwise bypass those factory
recipes even after the ordinary crafting recipes have been replaced.  This
contract deliberately targets exact recipe IDs and keeps every dismantling
route available so filled cells and crafting blocks remain recoverable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"

CELL_TIERS = ("1k", "4k", "16k", "64k", "256k")
AE2_CELL_FAMILIES = (
    "fluid_storage_cell",
    "item_storage_cell",
    "portable_fluid_cell",
    "portable_item_cell",
)
APPMEK_CELL_FAMILIES = (
    "chemical_storage_cell",
    "portable_chemical_cell",
)


def forward_cell_upgrade_ids() -> set[str]:
    result: set[str] = set()
    for namespace, families in (
        ("ae2", AE2_CELL_FAMILIES),
        ("appmek", APPMEK_CELL_FAMILIES),
    ):
        for family in families:
            for source_index, source in enumerate(CELL_TIERS[:-1]):
                for target in CELL_TIERS[source_index + 1 :]:
                    result.add(f"{namespace}:upgrade/{family}_{source}_to_{target}")
    return result


FORWARD_CELL_UPGRADES = forward_cell_upgrade_ids()
FORWARD_CRAFTING_UNIT_TRANSFORMS = {
    "ae2:crafting_unit_upgrade/1k_crafting_storage",
    "ae2:crafting_unit_upgrade/4k_crafting_storage",
    "ae2:crafting_unit_upgrade/16k_crafting_storage",
    "ae2:crafting_unit_upgrade/64k_crafting_storage",
    "ae2:crafting_unit_upgrade/256k_crafting_storage",
    "ae2:crafting_unit_upgrade/crafting_accelerator",
    "ae2:crafting_unit_upgrade/crafting_monitor",
}
PROCESSOR_ACCELERATOR_ROUTES = {
    "extendedae:assembler/logic_processor",
    "extendedae:assembler/calculation_processor",
    "extendedae:assembler/engineering_processor",
    "extendedae:cutter/logic_processor",
    "extendedae:cutter/calculation_processor",
    "extendedae:cutter/engineering_processor",
    "appliedcreate:crystal_assembler/stress_processor",
    "appliedcreate:crystal_assembler/advanced_stress_processor",
}
REQUIRED_EXACT_REMOVALS = (
    FORWARD_CELL_UPGRADES
    | FORWARD_CRAFTING_UNIT_TRANSFORMS
    | PROCESSOR_ACCELERATOR_ROUTES
)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def manifest_removals(manifest: Mapping[str, Any]) -> set[str]:
    removals = {
        str(value)
        for value in manifest.get("additional_removals", [])
        if isinstance(value, str)
    }
    for recipe in manifest.get("recipes", []):
        if isinstance(recipe, dict):
            removals.update(
                str(value)
                for value in recipe.get("remove", [])
                if isinstance(value, str)
            )
    for family in manifest.get("machine_families", []):
        if not isinstance(family, dict):
            continue
        for recipe in family.get("recipes", []):
            if isinstance(recipe, dict):
                removals.update(
                    str(value)
                    for value in recipe.get("remove", [])
                    if isinstance(value, str)
                )
    return removals


def compiled_removals(compiled: Mapping[str, Any]) -> set[str]:
    return {
        str(entry.get("recipeId"))
        for entry in compiled.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }


def is_disassembly_recipe(recipe_id: str) -> bool:
    return (
        recipe_id.startswith("ae2:cell_upgrade/")
        or recipe_id.startswith("appmek:cell_upgrade/")
        or (
            recipe_id.startswith("megacells:crafting/")
            and recipe_id.endswith("_disassembly")
        )
    )


def validate_contract(
    manifest: Mapping[str, Any], compiled: Mapping[str, Any]
) -> list[str]:
    errors: list[str] = []
    manifest_ids = manifest_removals(manifest)
    compiled_ids = compiled_removals(compiled)

    for label, removal_ids in (
        ("manifest", manifest_ids),
        ("compiled KJSGen project", compiled_ids),
    ):
        missing = sorted(REQUIRED_EXACT_REMOVALS - removal_ids)
        if missing:
            errors.append(f"{label} is missing exact AE2/AppMek bypass removals: {missing}")
        protected = sorted(recipe_id for recipe_id in removal_ids if is_disassembly_recipe(recipe_id))
        if protected:
            errors.append(f"{label} removes protected disassembly recipes: {protected}")

    if len(FORWARD_CELL_UPGRADES) != 60:
        errors.append(
            f"forward cell-upgrade contract generated {len(FORWARD_CELL_UPGRADES)} IDs; expected 60"
        )
    if len(FORWARD_CRAFTING_UNIT_TRANSFORMS) != 7:
        errors.append("forward crafting-unit transform contract no longer contains 7 IDs")
    if len(PROCESSOR_ACCELERATOR_ROUTES) != 8:
        errors.append("processor accelerator contract no longer contains 8 IDs")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--compiled", type=Path, default=DEFAULT_COMPILED)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = load_object(args.manifest.resolve())
        compiled = load_object(args.compiled.resolve())
        errors = validate_contract(manifest, compiled)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors = [str(exc)]

    if errors:
        print(f"FAIL: {len(errors)} AE2/AppMek transform-hardening issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(
        "PASS: retired 60 forward cell upgrades, 7 forward crafting-unit transforms, "
        "and 8 processor accelerators while preserving disassembly."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
