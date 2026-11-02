#!/usr/bin/env python3
"""Validate the post-Star spaceflight boundary and canonical propellants."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = Path("pack-scripts/server_scripts/industrial_space_entry_deferred.js")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
SAFE_OXYGEN_LOADING_ID = "ad_astra:oxygen_loading/oxygen_from_oxygen_loading_oxygen"
WATER_OXYGEN_SHORTCUT_ID = "ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water"

DEFERRED_RECIPE_IDS = (
    "ad_astra:nasa_workbench",
    "ad_astra:launch_pad",
    "ad_astra:fuel_refinery",
    "ad_astra:refining/fuel_from_refining_oil",
    WATER_OXYGEN_SHORTCUT_ID,
    "ad_astra:nasa_workbench/tier_1_rocket_from_nasa_workbench",
    "ad_astra:nasa_workbench/tier_2_rocket_from_nasa_workbench",
    "ad_astra:nasa_workbench/tier_3_rocket_from_nasa_workbench",
    "ad_astra:nasa_workbench/tier_4_rocket_from_nasa_workbench",
    "ad_astra:space_station/earth_orbit_space_station",
    "ad_astra:space_station/moon_orbit_space_station",
    "ad_astra:space_station/mars_orbit_space_station",
    "ad_astra:space_station/venus_orbit_space_station",
    "ad_astra:space_station/mercury_orbit_space_station",
    "ad_astra:space_station/glacio_orbit_space_station",
    "rocketnautics:hologram_block",
    "rocketnautics:magnetic_stabilizer",
    "rocketnautics:mechanical_crafting/rocket_thruster",
    "rocketnautics:mechanical_crafting/booster_thruster",
    "rocketnautics:crafting/mechanisms/rcs_thruster",
    "rocketnautics:crafting/mechanisms/separator",
    "rocketnautics:crafting/mechanisms/separator_charge",
    "rocketnautics:crafting/mechanisms/separator_shaft",
    "rocketnautics:crafting/mechanisms/vector_thruster",
    "rocketnautics:crafting/equipment/copper_anchor_boots",
    "rocketnautics:crafting/equipment/copper_leg_thrusters",
    "rocketnautics:crafting/equipment/jetpack",
    "rocketnautics:splashing/crushed_raw_titanium",
    "mekanism:chemical_conversion/flint_to_oxygen",
    "simulated:physics_assembler",
    "cosmowarp:crystal_driver",
    "cosmowarp:memory_card",
)
EXPECTED_DEFERRED_COUNT = len(DEFERRED_RECIPE_IDS)

MANAGED_REPLACEMENTS = {
    "cosmowarp:warp_crystal": "cosmowarp:warp_crystal",
    "cosmowarp:warp_drive": "cosmowarp:warp_drive",
}

# The installed sanding recipe already expresses this one-step polishing
# operation exactly.  Keep it source-owned instead of emitting an unchanged
# managed copy; the output remains excluded from automatic management.
PRESERVED_STOCK_ROUTES = {
    "cosmowarp:moon_crystal_sanding": "cosmowarp:moon_crystal",
}

PROTECTED_OUTPUTS = {
    "ad_astra:nasa_workbench",
    "ad_astra:launch_pad",
    "ad_astra:fuel_refinery",
    "ad_astra:fuel",
    "ad_astra:tier_1_rocket",
    "ad_astra:tier_2_rocket",
    "ad_astra:tier_3_rocket",
    "ad_astra:tier_4_rocket",
    "rocketnautics:hologram_block",
    "rocketnautics:magnetic_stabilizer",
    "rocketnautics:rocket_thruster",
    "rocketnautics:booster_thruster",
    "rocketnautics:rcs_thruster",
    "rocketnautics:separator",
    "rocketnautics:separator_charge",
    "rocketnautics:separator_shaft",
    "rocketnautics:vector_thruster",
    "rocketnautics:copper_anchor_boots",
    "rocketnautics:copper_leg_thrusters",
    "rocketnautics:jetpack",
    "simulated:physics_assembler",
    "cosmowarp:crystal_driver",
    "cosmowarp:memory_card",
    "cosmowarp:moon_crystal",
    "cosmowarp:warp_crystal",
    "cosmowarp:warp_drive",
}

TAG_CONTRACTS = {
    Path("src/main/resources/data/ad_astra/tags/fluid/fuel.json"): [
        "tfmg:kerosene",
        "tfmg:flowing_kerosene",
    ],
    Path("src/main/resources/data/rocketnautics/tags/fluid/rocket_fuel.json"): [
        "tfmg:kerosene",
        "tfmg:flowing_kerosene",
    ],
    Path("src/main/resources/data/rocketnautics/tags/fluid/oxidizer.json"): [
        "mekanism:oxygen",
        "mekanism:flowing_oxygen",
    ],
}


def recipe_csv_path(value: Path) -> Path:
    return value / "recipes.csv" if value.is_dir() else value


def split_outputs(value: str) -> set[str]:
    return {part.strip() for part in value.split("|") if part.strip()}


def validate(project: Path, catalog: Path | None = None) -> list[str]:
    failures: list[str] = []
    script_path = project / SCRIPT
    if not script_path.is_file():
        return [f"missing space-entry boundary script: {script_path}"]

    source = script_path.read_text(encoding="utf-8-sig")
    for recipe_id in DEFERRED_RECIPE_IDS:
        if f"'{recipe_id}'" not in source:
            failures.append(f"space-entry boundary is missing exact recipe ID {recipe_id}")
    if f"'{SAFE_OXYGEN_LOADING_ID}'" in source:
        failures.append(
            "safe oxygen-to-oxygen loading pass-through must remain available for "
            "Mekanism-produced oxygen"
        )

    quoted_ids = re.findall(r"'([a-z0-9_.-]+:[a-z0-9_./-]+)'", source)
    expected_ids = set(DEFERRED_RECIPE_IDS)
    if len(quoted_ids) != EXPECTED_DEFERRED_COUNT or set(quoted_ids) != expected_ids:
        missing = sorted(expected_ids - set(quoted_ids))
        unexpected = sorted(set(quoted_ids) - expected_ids)
        duplicates = sorted({value for value in quoted_ids if quoted_ids.count(value) > 1})
        failures.append(
            f"space-entry script must contain exactly the reviewed {EXPECTED_DEFERRED_COUNT}-ID boundary; "
            f"missing={missing}, unexpected={unexpected}, duplicates={duplicates}"
        )

    if not re.search(r"event\.remove\(\{\s*id:\s*id\s*\}\)", source):
        failures.append("space-entry boundary does not remove its exact ID list")
    if re.search(r"event\.remove\(\{\s*(output|mod|type|input)\s*:", source):
        failures.append("space-entry boundary contains a broad recipe removal")
    if "stock Ad Astra space-entry recipes until the spaceflight expansion" not in source:
        failures.append("space-entry runtime acceptance marker drifted")

    manifest_path = project / MANIFEST
    if not manifest_path.is_file():
        failures.append(f"missing managed space-entry replacements: {MANIFEST.as_posix()}")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"invalid managed space-entry replacements: {exc}")
            manifest = {}
        recipes = manifest.get("recipes", []) if isinstance(manifest, dict) else []
        manifest_removals = {
            value
            for value in manifest.get("additional_removals", [])
            if isinstance(value, str)
        }
        for row in recipes:
            if isinstance(row, dict):
                manifest_removals.update(
                    value for value in row.get("remove", []) if isinstance(value, str)
                )
        preserved_ids = {
            value
            for value in manifest.get("preserve_recipe_ids", [])
            if isinstance(value, str)
        }
        for stock_id, output in MANAGED_REPLACEMENTS.items():
            owners = [row for row in recipes if row.get("output") == output]
            if len(owners) != 1:
                failures.append(
                    f"managed space-entry output {output} must have exactly one owner; found {len(owners)}"
                )
                continue
            owner = owners[0]
            if stock_id not in owner.get("remove", []) or owner.get("exclusive_output") is not True:
                failures.append(
                    f"managed space-entry output {output} does not exclusively retire {stock_id}"
                )
        for stock_id, output in PRESERVED_STOCK_ROUTES.items():
            owners = [row for row in recipes if row.get("output") == output]
            if owners:
                failures.append(
                    f"source-owned space-entry output {output} has {len(owners)} redundant managed owner(s)"
                )
            if stock_id not in preserved_ids or stock_id in manifest_removals:
                failures.append(
                    f"source-owned space-entry recipe {stock_id} is not safely preserved"
                )

    for relative, expected_values in TAG_CONTRACTS.items():
        path = project / relative
        if not path.is_file():
            failures.append(f"missing canonical space-fluid tag override: {relative.as_posix()}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"invalid space-fluid tag override {relative.as_posix()}: {exc}")
            continue
        if payload.get("replace") is not True:
            failures.append(f"{relative.as_posix()} must replace the third-party tag")
        if payload.get("values") != expected_values:
            failures.append(
                f"{relative.as_posix()} values drifted: expected {expected_values}, "
                f"found {payload.get('values')}"
            )

    if catalog is not None:
        csv_path = recipe_csv_path(catalog)
        if not csv_path.is_file():
            failures.append(f"missing installed recipe catalog: {csv_path}")
        else:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            by_id = {row.get("recipe_id", ""): row for row in rows}
            reviewed_stock_ids = (
                set(DEFERRED_RECIPE_IDS)
                | set(MANAGED_REPLACEMENTS)
                | set(PRESERVED_STOCK_ROUTES)
            )
            missing_ids = sorted(reviewed_stock_ids - set(by_id))
            if missing_ids:
                failures.append(f"installed catalog is missing deferred stock IDs: {missing_ids}")
            if SAFE_OXYGEN_LOADING_ID not in by_id:
                failures.append(
                    "installed catalog is missing the retained oxygen-to-oxygen loading pass-through: "
                    f"{SAFE_OXYGEN_LOADING_ID}"
                )

            deferred = reviewed_stock_ids
            leaked: list[str] = []
            for row in rows:
                outputs = split_outputs(row.get("outputs", ""))
                if outputs & PROTECTED_OUTPUTS and row.get("recipe_id", "") not in deferred:
                    leaked.append(row.get("recipe_id", ""))
            if leaked:
                failures.append(
                    "installed catalog has undeferred producers for protected space-entry outputs: "
                    f"{sorted(set(leaked))}"
                )

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument(
        "--catalog",
        type=Path,
        help="Recipe catalog directory or recipes.csv from the installed pack.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate(args.project.resolve(), args.catalog.resolve() if args.catalog else None)
    if failures:
        print("FAIL: post-Star space-entry boundary is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        f"PASS: {EXPECTED_DEFERRED_COUNT} exact stock space recipes remain deferred and "
        f"{len(MANAGED_REPLACEMENTS)} Cosmowarp recipes have exclusive managed replacements, "
        f"{len(PRESERVED_STOCK_ROUTES)} unchanged route remains source-owned; "
        "Cosmonautics and Ad Astra use TFMG kerosene; launch oxidizer uses liquid Mekanism oxygen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
