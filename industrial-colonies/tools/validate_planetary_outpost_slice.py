#!/usr/bin/env python3
"""Validate the bounded Moon/Mars outpost utility commissioning slice."""

from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
SEED = Path("progression/managed_recipe_overhaul.seed.json")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
COMPILED = Path("pack-kjsgen/default.managed.json")
ASSIGNMENTS = Path("progression/machine_node_assignments.json")
LAYOUT = Path("progression/minecolonies_branch_layout.json")
QUESTS = Path("progression/ftbquests_planetary_industry.json")
DEFERRED = Path("pack-scripts/server_scripts/industrial_space_entry_deferred.js")
FULL_CANTEEN_ADVANCEMENT = "data/mekanism/advancement/full_canteen.json"

PHASE = "Planetary Industry"
NODE = "CR02 — Planetary Outpost Utilities"
DESH_PLATE = "industrial_colonies:planetary/desh/plate"
OSTRUM_PLATE = "industrial_colonies:planetary/ostrum/plate"
FORBIDDEN_REMOVAL_FIELDS = {
    "remove_by_output", "removeByOutput", "remove_by_mod", "removeByMod",
    "replace", "replace_recipe", "replaceRecipe",
}

RECIPES: dict[str, dict[str, Any]] = {
    "industrial_colonies:planetary/outpost/solar_panel": {
        "node": NODE,
        "phase": PHASE,
        "order": 160,
        "type": "mechanical_crafting",
        "pattern": ["PPPPP", "PDPDP", "CTETC", "PDPDP", "PPPPP"],
        "key": {
            "P": "ad_astra:photovoltaic_etrium_cell",
            "D": "ad_astra:desh_plate",
            "C": "mekanism:ultimate_universal_cable",
            "T": "tfmg:transformer",
            "E": "ae2:engineering_processor",
        },
        "output": "4x ad_astra:solar_panel",
        "remove": ["ad_astra:solar_panel"],
        "exclusive_output": True,
        "depends_on": [DESH_PLATE],
    },
    "industrial_colonies:planetary/outpost/water_pump": {
        "node": NODE,
        "phase": PHASE,
        "order": 170,
        "type": "mechanical_crafting",
        "pattern": ["DPUPD", "DSTSD", "PVGVP", "DSTSD", "DPUPD"],
        "key": {
            "D": "ad_astra:desh_plate",
            "P": "tfmg:electric_pump",
            "U": "mekanism:elite_control_circuit",
            "S": "tfmg:steel_pipe",
            "T": "tfmg:steel_fluid_tank",
            "V": "tfmg:steel_fluid_valve",
            "G": "ad_astra:gas_tank",
        },
        "output": "ad_astra:water_pump",
        "remove": ["ad_astra:water_pump"],
        "exclusive_output": True,
        "depends_on": [DESH_PLATE, "industrial_colonies:space/life_support/gas_tank"],
    },
    "industrial_colonies:planetary/outpost/gravity_normalizer": {
        "node": NODE,
        "phase": PHASE,
        "order": 180,
        "type": "mechanical_crafting",
        "pattern": ["DCWCD", "DTEED", "WUQUW", "DTEED", "DCWCD"],
        "key": {
            "D": "ad_astra:desh_plate",
            "C": "ad_astra:etrionic_capacitor",
            "W": "mekanism:ultimate_universal_cable",
            "T": "tfmg:transformer",
            "E": "ae2:engineering_processor",
            "U": "mekanism:ultimate_control_circuit",
            "Q": "mekanism:ultimate_energy_cube",
        },
        "output": "ad_astra:gravity_normalizer",
        "remove": ["ad_astra:gravity_normalizer"],
        "exclusive_output": True,
        "depends_on": [DESH_PLATE],
    },
    "industrial_colonies:planetary/outpost/energizer": {
        "node": NODE,
        "phase": PHASE,
        "order": 190,
        "type": "mechanical_crafting",
        "pattern": ["OBTBO", "OCECO", "TQUQT", "OCECO", "OBTBO"],
        "key": {
            "O": "ad_astra:ostrum_plate",
            "B": "ad_astra:ostrum_block",
            "T": "tfmg:transformer",
            "C": "ad_astra:etrionic_capacitor",
            "E": "ae2:engineering_processor",
            "Q": "mekanism:ultimate_energy_cube",
            "U": "mekanism:ultimate_control_circuit",
        },
        "output": "ad_astra:energizer",
        "remove": ["ad_astra:energizer"],
        "exclusive_output": True,
        "depends_on": [OSTRUM_PLATE],
    },
    "industrial_colonies:planetary/outpost/nutritional_liquifier": {
        "node": NODE,
        "phase": PHASE,
        "order": 200,
        "type": "mechanical_crafting",
        "pattern": ["OPEPO", "OFUFO", "TCBCT", "OFUFO", "OPEPO"],
        "key": {
            "O": "ad_astra:ostrum_plate",
            "P": "tfmg:electric_pump",
            "E": "ae2:engineering_processor",
            "F": "tfmg:steel_fluid_valve",
            "U": "mekanism:elite_control_circuit",
            "T": "tfmg:etched_circuit_board",
            "C": "tfmg:steel_frame",
            "B": "farmersdelight:cooking_pot",
        },
        "output": "mekanism:nutritional_liquifier",
        "remove": ["mekanism:nutritional_liquifier"],
        "exclusive_output": True,
        "depends_on": [OSTRUM_PLATE],
    },
}

NODE_UNLOCKS = [
    "ad_astra:solar_panel",
    "ad_astra:water_pump",
    "ad_astra:gravity_normalizer",
    "ad_astra:energizer",
    "mekanism:nutritional_liquifier",
]

STOCK: dict[str, dict[str, Any]] = {
    "ad_astra:solar_panel": {
        "type": "minecraft:crafting_shaped",
        "path": "data/ad_astra/recipe/solar_panel.json",
        "output": "ad_astra:solar_panel",
        "count": 1,
    },
    "ad_astra:water_pump": {
        "type": "minecraft:crafting_shaped",
        "path": "data/ad_astra/recipe/water_pump.json",
        "output": "ad_astra:water_pump",
        "count": 1,
    },
    "ad_astra:gravity_normalizer": {
        "type": "minecraft:crafting_shaped",
        "path": "data/ad_astra/recipe/gravity_normalizer.json",
        "output": "ad_astra:gravity_normalizer",
        "count": 1,
    },
    "ad_astra:energizer": {
        "type": "minecraft:crafting_shaped",
        "path": "data/ad_astra/recipe/energizer.json",
        "output": "ad_astra:energizer",
        "count": 1,
    },
    "mekanism:nutritional_liquifier": {
        "type": "minecraft:crafting_shaped",
        "path": "data/mekanism/recipe/nutritional_liquifier.json",
        "output": "mekanism:nutritional_liquifier",
        "count": 1,
    },
}

QUESTS_EXPECTED: dict[str, dict[str, Any]] = {
    "lunar_utility_array": {
        "dependencies": ["desh_metallurgy"],
        "tasks": [
            {"type": "item", "item": "ad_astra:solar_panel", "count": 4},
            {"type": "item", "item": "ad_astra:water_pump", "count": 1},
            {"type": "item", "item": "ad_astra:gravity_normalizer", "count": 1},
        ],
    },
    "martian_service_reserve": {
        "dependencies": ["ostrum_metallurgy", "lunar_utility_array"],
        "tasks": [
            {"type": "item", "item": "ad_astra:energizer", "count": 1},
            {"type": "item", "item": "mekanism:ultimate_energy_cube", "count": 1},
            {"type": "item", "item": "mekanism:ultimate_universal_cable", "count": 16},
        ],
    },
    "closed_loop_rations": {
        "dependencies": ["martian_service_reserve"],
        "tasks": [
            {"type": "item", "item": "mekanism:nutritional_liquifier", "count": 1},
            {"type": "item", "item": "mekanism:canteen", "count": 4},
            {"type": "advancement", "advancement": "mekanism:full_canteen", "criterion": ""},
        ],
    },
}

DEFERRED_BOUNDARIES = (
    "ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water",
    "mekanism:chemical_conversion/flint_to_oxygen",
    "ad_astra:nasa_workbench/tier_2_rocket_from_nasa_workbench",
    "ad_astra:nasa_workbench/tier_3_rocket_from_nasa_workbench",
    "ad_astra:nasa_workbench/tier_4_rocket_from_nasa_workbench",
    "ad_astra:space_station/venus_orbit_space_station",
    "ad_astra:space_station/mercury_orbit_space_station",
    "ad_astra:space_station/glacio_orbit_space_station",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def output_id(value: Any) -> str:
    match = re.fullmatch(r"(?:(\d+)x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)", str(value or "").strip())
    return match.group(2) if match else str(value or "").strip()


def output_count(value: Any) -> int:
    match = re.fullmatch(r"(?:(\d+)x\s+)?[a-z0-9_.-]+:[a-z0-9_./-]+", str(value or "").strip())
    return int(match.group(1) or 1) if match else 0


def rows(payload: dict[str, Any], recipe_id: str) -> list[dict[str, Any]]:
    return [row for row in payload.get("recipes", []) if row.get("id") == recipe_id]


def has_ancestor(
    recipe_id: str,
    ancestor: str,
    recipes: dict[str, dict[str, Any]],
    seen: set[str] | None = None,
) -> bool:
    if recipe_id == ancestor:
        return True
    seen = set() if seen is None else seen
    if recipe_id in seen:
        return False
    seen.add(recipe_id)
    return any(
        has_ancestor(str(parent), ancestor, recipes, seen.copy())
        for parent in recipes.get(recipe_id, {}).get("depends_on", [])
    )


def slot(value: str) -> dict[str, Any]:
    result: dict[str, Any] = {"kind": "ITEM", "id": output_id(value)}
    count = output_count(value)
    if count > 1:
        result["count"] = count
    return result


def expected_slots(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slots: dict[str, dict[str, Any]] = {}
    for row_index, pattern_row in enumerate(spec["pattern"]):
        for column_index, symbol in enumerate(pattern_row):
            if symbol != " ":
                slots[f"cell_{row_index}_{column_index}"] = slot(spec["key"][symbol])
    slots["output"] = slot(spec["output"])
    return slots


def validate_payload(path: Path, compiled: bool, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing {'compiled' if compiled else 'assembled'} outpost data: {path}")
        return
    payload = load_json(path)
    if not compiled:
        for recipe_id, expected in RECIPES.items():
            found = rows(payload, recipe_id)
            if len(found) != 1:
                failures.append(f"assembled manifest must contain exactly one {recipe_id}")
                continue
            for field, value in expected.items():
                if field not in {"exclusive_output", "depends_on"} and found[0].get(field) != value:
                    failures.append(f"assembled {recipe_id} {field} drifted")
            if not set(expected["depends_on"]).issubset(found[0].get("depends_on", [])):
                failures.append(f"assembled {recipe_id} dependency route drifted")
        return

    cards = payload.get("recipes", [])
    removals = payload.get("removals", [])
    for recipe_id, expected in RECIPES.items():
        found = [card for card in cards if card.get("recipeId") == recipe_id]
        if len(found) != 1:
            failures.append(f"compiled KJSGen project must contain exactly one {recipe_id}")
            continue
        card = found[0]
        if card.get("type") != "kjsgen:create_mechanical_crafting" or card.get("params") != {"gridW": "5", "gridH": "5"}:
            failures.append(f"{recipe_id} compiled type or 5x5 parameters drifted")
        if card.get("slots") != expected_slots(expected):
            failures.append(f"{recipe_id} compiled slots drifted")
        if card.get("replaceRecipe") is not False:
            failures.append(f"{recipe_id} unexpectedly replaces recipes by output")
        target_output = output_id(expected["output"])
        output_owners = [
            candidate
            for candidate in cards
            if str(candidate.get("slots", {}).get("output", {}).get("id", ""))
            == target_output
        ]
        if len(output_owners) != 1 or output_owners[0].get("recipeId") != recipe_id:
            owner_ids = sorted(str(candidate.get("recipeId", "")) for candidate in output_owners)
            failures.append(
                f"exclusive outpost output {target_output} has alternate compiled owners: {owner_ids}"
            )
    for stock_id in STOCK:
        exact = [entry for entry in removals if entry.get("recipeId") == stock_id]
        if len(exact) != 1:
            failures.append(f"compiled project must remove stock {stock_id} exactly once")
        elif any(str(exact[0].get(field, "")).strip() for field in ("output", "input", "mod")):
            failures.append(f"compiled removal for {stock_id} is broader than its exact ID")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    directory = catalog if catalog.is_dir() else catalog.parent
    items_path = directory / "items.csv"
    recipes_path = directory / "recipes.csv"
    refs_path = directory / "recipe_refs.csv"
    if not all(path.is_file() for path in (items_path, recipes_path, refs_path)):
        failures.append(f"catalog must provide items.csv, recipes.csv, and recipe_refs.csv: {catalog}")
        return
    with items_path.open(encoding="utf-8-sig", newline="") as handle:
        item_ids = {row.get("item_id", "") for row in csv.DictReader(handle)}
    with recipes_path.open(encoding="utf-8-sig", newline="") as handle:
        stock_rows = {row.get("recipe_id", ""): row for row in csv.DictReader(handle)}
    with refs_path.open(encoding="utf-8-sig", newline="") as handle:
        refs = list(csv.DictReader(handle))
    used = {
        output_id(value)
        for spec in RECIPES.values()
        for value in [spec["output"], *spec["key"].values()]
    }
    missing = sorted(used - item_ids)
    if missing:
        failures.append(f"installed registry catalog is missing outpost IDs: {missing}")
    for stock_id, expected in STOCK.items():
        row = stock_rows.get(stock_id)
        if not row:
            failures.append(f"installed catalog is missing stock recipe {stock_id}")
            continue
        if row.get("recipe_type") != expected["type"] or row.get("source_path") != expected["path"]:
            failures.append(f"stock recipe type/path drifted: {stock_id}")
        if output_id(row.get("outputs", "")) != expected["output"]:
            failures.append(f"stock recipe output drifted: {stock_id}")
        counts = [
            int(float(ref["count"]))
            for ref in refs
            if ref.get("recipe_id") == stock_id
            and ref.get("role") == "output"
            and ref.get("count")
        ]
        if counts != [expected["count"]]:
            failures.append(f"stock recipe output count drifted: {stock_id}: {counts}")


def validate_quests(project: Path, failures: list[str]) -> None:
    payload = load_json(project / QUESTS)
    quest_rows = payload.get("chapter", {}).get("quests", [])
    by_key = {row.get("key", ""): row for row in quest_rows}
    if len(quest_rows) != 29:
        failures.append("Planetary Industry must contain exactly twenty-nine quests through interstellar escape")
    keys = [row.get("key") for row in quest_rows]
    if keys[7:10] != list(QUESTS_EXPECTED):
        failures.append("outpost observation quest order drifted")
    forbidden = {"rewards", "stage", "stages", "command", "commands", "recipe", "recipes"}
    for key, expected in QUESTS_EXPECTED.items():
        quest = by_key.get(key, {})
        if quest.get("dependencies") != expected["dependencies"]:
            failures.append(f"outpost quest dependency drifted: {key}")
        if quest.get("tasks") != expected["tasks"]:
            failures.append(f"outpost quest observation set drifted: {key}")
        if forbidden.intersection(quest):
            failures.append(f"outpost quest contains a gate or reward: {key}")
        if any(task.get("consume_items", False) for task in quest.get("tasks", [])):
            failures.append(f"outpost quest is not non-consuming: {key}")
    full_canteen = QUESTS_EXPECTED["closed_loop_rations"]["tasks"][-1]
    if full_canteen != {
        "type": "advancement", "advancement": "mekanism:full_canteen", "criterion": ""
    }:
        failures.append("closed-loop ration throughput is not pinned to Mekanism's full-canteen advancement")


def validate_full_canteen_advancement(mods: Path, failures: list[str]) -> None:
    if not mods.is_dir():
        failures.append(f"installed mod directory is missing: {mods}")
        return
    owners: list[str] = []
    for jar_path in sorted(mods.glob("*.jar")):
        try:
            with zipfile.ZipFile(jar_path) as archive:
                if FULL_CANTEEN_ADVANCEMENT not in archive.namelist():
                    continue
                payload = json.loads(archive.read(FULL_CANTEEN_ADVANCEMENT).decode("utf-8-sig"))
                if not isinstance(payload, dict) or not isinstance(payload.get("criteria"), dict):
                    failures.append(
                        f"installed full-canteen advancement is malformed: {jar_path.name}"
                    )
                owners.append(jar_path.name)
        except (OSError, zipfile.BadZipFile):
            continue
    if len(owners) != 1:
        failures.append(
            f"installed {FULL_CANTEEN_ADVANCEMENT} must have exactly one archive owner; found {owners}"
        )


def validate(
    project: Path,
    catalog: Path | None = None,
    manifest: Path | None = None,
    compiled: Path | None = None,
    mods: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    for relative in (SEED, ASSIGNMENTS, LAYOUT, QUESTS, DEFERRED):
        if not (project / relative).is_file():
            failures.append(f"missing planetary outpost source file: {relative.as_posix()}")
    if failures:
        return failures

    seed = load_json(project / SEED)
    by_id = {row.get("id", ""): row for row in seed.get("recipes", [])}
    for recipe_id, expected in RECIPES.items():
        found = rows(seed, recipe_id)
        if len(found) != 1:
            failures.append(f"managed seed must contain exactly one {recipe_id}")
            continue
        recipe = found[0]
        for field, value in expected.items():
            if recipe.get(field) != value:
                failures.append(f"{recipe_id} {field} drifted")
        if not str(recipe.get("comment", "")).strip():
            failures.append(f"{recipe_id} has no construction rationale")
        if FORBIDDEN_REMOVAL_FIELDS.intersection(recipe):
            failures.append(f"{recipe_id} contains a broad removal directive")
        if len(recipe.get("pattern", [])) != 5 or any(len(row) != 5 for row in recipe.get("pattern", [])):
            failures.append(f"{recipe_id} is not a 5x5 Mechanical Crafting build")

    scope_rows = [
        row for row in seed.get("recipes", [])
        if str(row.get("id", "")).startswith("industrial_colonies:planetary/outpost/")
    ]
    if {row.get("id") for row in scope_rows} != set(RECIPES):
        failures.append("planetary outpost slice is not exactly the five approved replacements")
    removals = [stock for spec in RECIPES.values() for stock in spec["remove"]]
    if set(removals) != set(STOCK) or len(removals) != 5:
        failures.append("outpost stock-removal set is not the exact five approved IDs")
    if output_count(RECIPES["industrial_colonies:planetary/outpost/solar_panel"]["output"]) != 4:
        failures.append("solar infrastructure recipe must output exactly four panels")

    desh_recipes = (
        "industrial_colonies:planetary/outpost/solar_panel",
        "industrial_colonies:planetary/outpost/water_pump",
        "industrial_colonies:planetary/outpost/gravity_normalizer",
    )
    for recipe_id in desh_recipes:
        recipe = by_id.get(recipe_id, {})
        if "ad_astra:desh_plate" not in recipe.get("key", {}).values():
            failures.append(f"{recipe_id} does not physically contain Desh plate")
        if not has_ancestor(recipe_id, DESH_PLATE, by_id):
            failures.append(f"{recipe_id} is not downstream of the Desh plate line")
    for recipe_id in (
        "industrial_colonies:planetary/outpost/energizer",
        "industrial_colonies:planetary/outpost/nutritional_liquifier",
    ):
        recipe = by_id.get(recipe_id, {})
        if "ad_astra:ostrum_plate" not in recipe.get("key", {}).values():
            failures.append(f"{recipe_id} does not physically contain Ostrum plate")
        if not has_ancestor(recipe_id, OSTRUM_PLATE, by_id):
            failures.append(f"{recipe_id} is not downstream of the Ostrum plate line")
    nutrition_items = set(
        by_id.get("industrial_colonies:planetary/outpost/nutritional_liquifier", {})
        .get("key", {})
        .values()
    )
    if "farmersdelight:cooking_pot" not in nutrition_items:
        failures.append("Nutritional Liquifier lost its meaningful Farmer's Delight food-processing core")

    assignments = load_json(project / ASSIGNMENTS).get("nodes", {})
    if seed.get("phase_by_node", {}).get(NODE) != PHASE:
        failures.append(f"{NODE} is not assigned to {PHASE}")
    if assignments.get(NODE, {}).get("unlocks") != NODE_UNLOCKS:
        failures.append(f"{NODE} unlock assignment drifted")
    if not str(assignments.get(NODE, {}).get("role", "")).strip():
        failures.append(f"{NODE} role is blank")
    if NODE in (project / LAYOUT).read_text(encoding="utf-8-sig"):
        failures.append("immutable MineColonies layout was expanded with the outpost node")

    deferred = (project / DEFERRED).read_text(encoding="utf-8-sig")
    for boundary in DEFERRED_BOUNDARIES:
        if deferred.count(f"'{boundary}'") != 1:
            failures.append(f"deferred space boundary changed: {boundary}")
    forbidden_new_outputs = {
        "ad_astra:cryo_freezer", "ad_astra:tier_2_rocket", "ad_astra:tier_3_rocket",
        "ad_astra:tier_4_rocket", "cosmowarp:warp_drive",
    }
    if forbidden_new_outputs.intersection(output_id(row.get("output")) for row in scope_rows):
        failures.append("outpost slice activated cryo, rocket, or warp output")
    if "ad_astra:cryo_freezer" in seed.get("additional_removals", []):
        failures.append("outpost slice changed cryo-fuel recipe ownership")

    validate_quests(project, failures)
    if catalog is not None:
        validate_catalog(catalog, failures)
    if manifest is not None:
        validate_payload(manifest, False, failures)
    if compiled is not None:
        validate_payload(compiled, True, failures)
    if mods is not None:
        validate_full_canteen_advancement(mods, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    parser.add_argument(
        "--mods",
        type=Path,
        default=Path.home() / "curseforge/minecraft/Instances/All in one/mods",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate(
        args.project.resolve(),
        args.catalog.resolve() if args.catalog else None,
        args.manifest.resolve() if args.manifest else None,
        args.compiled.resolve() if args.compiled else None,
        args.mods.resolve() if args.mods else None,
    )
    if failures:
        print("FAIL: planetary outpost commissioning slice is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("PASS: five exact 5x5 recipes and three observation-only quests commission Moon/Mars outpost utilities without expanding the destination boundary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
