#!/usr/bin/env python3
"""Validate the source-owned orbital navigation, dockyard, and station slice."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
SEED = Path("progression/managed_recipe_overhaul.seed.json")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
COMPILED = Path("pack-kjsgen/default.managed.json")
ASSIGNMENTS = Path("progression/machine_node_assignments.json")
LAYOUT = Path("progression/minecolonies_branch_layout.json")
QUESTS = Path("progression/ftbquests_orbital_engineering.json")
DEFERRED = Path("pack-scripts/server_scripts/industrial_space_entry_deferred.js")

PHASE = "Orbital Engineering"
PRESS = "createcasing:refined_radiance_press"
CONSTRUCTION_RECIPE = "industrial_colonies:space/construction/physics_assembler"
NAVIGATION_NODE = "CR02 — Orbital Navigation"
DOCKYARD_NODE = "CR02 — Dockyard Interfaces"
STATION_NODE = "CR02 — Station Fabrication"
NODES = (NAVIGATION_NODE, DOCKYARD_NODE, STATION_NODE)
VANILLA_ITEMS = {"minecraft:amethyst_shard", "minecraft:lightning_rod"}
FORBIDDEN_REMOVAL_FIELDS = {
    "remove_by_output", "removeByOutput", "remove_by_mod", "removeByMod",
    "replace", "replace_recipe", "replaceRecipe",
}

RECIPES: dict[str, dict[str, Any]] = {
    "industrial_colonies:space/navigation/velocity_sensor": {
        "node": NAVIGATION_NODE, "phase": PHASE, "order": 280,
        "type": "compacting", "machine": PRESS,
        "inputs": [
            "2x tfmg:steel_casing", "2x tfmg:electric_motor",
            "simulated:gyroscopic_mechanism", "tfmg:circuit_board",
            "tfmg:voltmeter", "ae2:calculation_processor",
        ],
        "output": "simulated:velocity_sensor",
        "remove": ["simulated:velocity_sensor"], "exclusive_output": True,
        "depends_on": [CONSTRUCTION_RECIPE],
    },
    "industrial_colonies:space/navigation/gimbal_sensor": {
        "node": NAVIGATION_NODE, "phase": PHASE, "order": 290,
        "type": "compacting", "machine": PRESS,
        "inputs": [
            "2x tfmg:steel_casing", "2x tfmg:magnetic_alloy_sheet",
            "simulated:gyroscopic_mechanism", "tfmg:potentiometer",
            "tfmg:circuit_board", "ae2:logic_processor",
        ],
        "output": "simulated:gimbal_sensor",
        "remove": ["simulated:gimbal_sensor"], "exclusive_output": True,
        "depends_on": [CONSTRUCTION_RECIPE],
    },
    "industrial_colonies:space/navigation/optical_sensor": {
        "node": NAVIGATION_NODE, "phase": PHASE, "order": 300,
        "type": "compacting", "machine": PRESS,
        "inputs": [
            "2x tfmg:steel_casing", "4x tfmg:aluminum_sheet",
            "2x minecraft:amethyst_shard", "2x tfmg:transistor_item",
            "tfmg:circuit_board", "ae2:calculation_processor",
        ],
        "output": "simulated:optical_sensor",
        "remove": ["simulated:optical_sensor"], "exclusive_output": True,
        "depends_on": [CONSTRUCTION_RECIPE],
    },
    "industrial_colonies:space/navigation/navigation_table": {
        "node": NAVIGATION_NODE, "phase": PHASE, "order": 310,
        "type": "mechanical_crafting",
        "pattern": ["HMCUH", "FBEBF", "OVGVO", "FBEBF", "HMCUH"],
        "key": {
            "H": "tfmg:heavy_plate", "M": "computercraft:monitor_advanced",
            "C": "computercraft:computer_advanced",
            "U": "mekanism:ultimate_control_circuit", "F": "tfmg:steel_frame",
            "B": "tfmg:circuit_board", "E": "ae2:engineering_processor",
            "O": "simulated:optical_sensor", "V": "simulated:velocity_sensor",
            "G": "simulated:gimbal_sensor",
        },
        "output": "simulated:navigation_table",
        "remove": ["simulated:navigation_table"], "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/navigation/velocity_sensor",
            "industrial_colonies:space/navigation/gimbal_sensor",
            "industrial_colonies:space/navigation/optical_sensor",
        ],
    },
    "industrial_colonies:space/navigation/sputnik": {
        "node": NAVIGATION_NODE, "phase": PHASE, "order": 320,
        "type": "mechanical_crafting",
        "pattern": ["ALLLA", "FOCGF", "LCNCL", "FVCVF", "ALLLA"],
        "key": {
            "A": "tfmg:aluminum_sheet", "L": "minecraft:lightning_rod",
            "F": "tfmg:steel_frame", "O": "simulated:optical_sensor",
            "C": "tfmg:circuit_board", "G": "simulated:gimbal_sensor",
            "N": "simulated:navigation_table", "V": "simulated:velocity_sensor",
        },
        "output": "rocketnautics:sputnik", "remove": ["rocketnautics:sputnik"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/navigation/navigation_table"],
    },
    "industrial_colonies:space/dockyard/docking_connector": {
        "node": DOCKYARD_NODE, "phase": PHASE, "order": 330,
        "type": "mechanical_crafting",
        "pattern": ["HIEDH", "FPCPF", "MNUNM", "FPCPF", "HIEDH"],
        "key": {
            "H": "tfmg:heavy_plate", "I": "create:portable_storage_interface",
            "E": "createaddition:portable_energy_interface",
            "D": "computercraft:wired_modem", "F": "tfmg:steel_frame",
            "P": "create:portable_fluid_interface", "C": "computercraft:cable",
            "M": "tfmg:electric_motor", "N": "simulated:navigation_table",
            "U": "mekanism:ultimate_control_circuit",
        },
        "output": "2x simulated:docking_connector",
        "remove": ["simulated:mechanical_crafting/docking_connector"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/navigation/sputnik"],
    },
    "industrial_colonies:space/station/steel_plating": {
        "node": STATION_NODE, "phase": PHASE, "order": 340,
        "type": "compacting", "machine": PRESS,
        "inputs": [
            "8x tfmg:heavy_plate", "4x tfmg:steel_frame",
            "8x tfmg:aluminum_sheet", "4x tfmg:fireproof_bricks",
            "4x tfmg:screw",
        ],
        "output": "32x ad_astra:steel_plating",
        "remove": ["ad_astra:steel_plating"], "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/dockyard/docking_connector"],
    },
    "industrial_colonies:space/station/steel_panel": {
        "node": STATION_NODE, "phase": PHASE, "order": 350,
        "type": "compacting", "machine": PRESS,
        "inputs": [
            "16x ad_astra:steel_plating", "8x tfmg:aluminum_sheet",
            "4x tfmg:cable_tube", "2x tfmg:circuit_board", "4x tfmg:screw",
        ],
        "output": "32x ad_astra:steel_panel", "remove": ["ad_astra:steel_panel"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/station/steel_plating"],
    },
    "industrial_colonies:space/station/cable_duct": {
        "node": STATION_NODE, "phase": PHASE, "order": 360,
        "type": "compacting", "machine": PRESS,
        "inputs": [
            "8x ad_astra:steel_plating", "4x tfmg:steel_cable_hub",
            "8x tfmg:cable_tube", "8x ad_astra:steel_cable",
            "8x computercraft:cable",
        ],
        "output": "16x ad_astra:cable_duct", "remove": ["ad_astra:cable_duct"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/station/steel_plating",
            "industrial_colonies:space/dockyard/docking_connector",
        ],
    },
    "industrial_colonies:space/station/fluid_pipe_duct": {
        "node": STATION_NODE, "phase": PHASE, "order": 370,
        "type": "compacting", "machine": PRESS,
        "inputs": [
            "8x ad_astra:steel_plating", "8x tfmg:steel_pipe",
            "2x tfmg:steel_fluid_tank", "4x tfmg:electric_pump", "4x tfmg:screw",
        ],
        "output": "16x ad_astra:fluid_pipe_duct",
        "remove": ["ad_astra:fluid_pipe_duct"], "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/station/steel_plating",
            "industrial_colonies:space/dockyard/docking_connector",
        ],
    },
}

NODE_UNLOCKS = {
    NAVIGATION_NODE: [
        "simulated:velocity_sensor", "simulated:gimbal_sensor",
        "simulated:optical_sensor", "simulated:navigation_table",
        "rocketnautics:sputnik",
    ],
    DOCKYARD_NODE: ["simulated:docking_connector"],
    STATION_NODE: [
        "ad_astra:steel_plating", "ad_astra:steel_panel",
        "ad_astra:cable_duct", "ad_astra:fluid_pipe_duct",
    ],
}

STOCK: dict[str, dict[str, Any]] = {
    "simulated:navigation_table": {"type": "minecraft:crafting_shaped", "path": "data/simulated/recipe/navigation_table.json", "output": "simulated:navigation_table", "count": 1},
    "simulated:velocity_sensor": {"type": "minecraft:crafting_shaped", "path": "data/simulated/recipe/velocity_sensor.json", "output": "simulated:velocity_sensor", "count": 1},
    "simulated:gimbal_sensor": {"type": "minecraft:crafting_shaped", "path": "data/simulated/recipe/gimbal_sensor.json", "output": "simulated:gimbal_sensor", "count": 1},
    "simulated:optical_sensor": {"type": "minecraft:crafting_shaped", "path": "data/simulated/recipe/optical_sensor.json", "output": "simulated:optical_sensor", "count": 1},
    "rocketnautics:sputnik": {"type": "minecraft:crafting_shaped", "path": "data/rocketnautics/recipe/sputnik.json", "output": "rocketnautics:sputnik", "count": 1},
    "simulated:mechanical_crafting/docking_connector": {"type": "create:mechanical_crafting", "path": "data/simulated/recipe/mechanical_crafting/docking_connector.json", "output": "simulated:docking_connector", "count": 2},
    "ad_astra:steel_plating": {"type": "minecraft:crafting_shaped", "path": "data/ad_astra/recipe/steel_plating.json", "output": "ad_astra:steel_plating", "count": 64},
    "ad_astra:steel_panel": {"type": "minecraft:crafting_shaped", "path": "data/ad_astra/recipe/steel_panel.json", "output": "ad_astra:steel_panel", "count": 64},
    "ad_astra:cable_duct": {"type": "minecraft:crafting_shaped", "path": "data/ad_astra/recipe/cable_duct.json", "output": "ad_astra:cable_duct", "count": 2},
    "ad_astra:fluid_pipe_duct": {"type": "minecraft:crafting_shaped", "path": "data/ad_astra/recipe/fluid_pipe_duct.json", "output": "ad_astra:fluid_pipe_duct", "count": 2},
}

QUESTS_EXPECTED = {
    "navigation_suite": {
        "dependencies": ["physics_assembler"],
        "items": [
            ("simulated:velocity_sensor", 1), ("simulated:gimbal_sensor", 1),
            ("simulated:optical_sensor", 1), ("simulated:navigation_table", 1),
            ("rocketnautics:sputnik", 1),
        ],
    },
    "docking_connector": {
        "dependencies": ["navigation_suite"],
        "items": [("simulated:docking_connector", 6)],
    },
    "station_materials": {
        "dependencies": ["docking_connector"],
        "items": [
            ("ad_astra:steel_plating", 128), ("ad_astra:steel_panel", 32),
            ("ad_astra:cable_duct", 16), ("ad_astra:fluid_pipe_duct", 16),
        ],
    },
}


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


def has_ancestor(recipe_id: str, ancestor: str, recipes: dict[str, dict[str, Any]], seen: set[str] | None = None) -> bool:
    if recipe_id == ancestor:
        return True
    seen = set() if seen is None else seen
    if recipe_id in seen:
        return False
    seen.add(recipe_id)
    return any(has_ancestor(str(parent), ancestor, recipes, seen.copy()) for parent in recipes.get(recipe_id, {}).get("depends_on", []))


def slot(value: str) -> dict[str, Any]:
    result: dict[str, Any] = {"kind": "ITEM", "id": output_id(value)}
    count = output_count(value)
    if count > 1:
        result["count"] = count
    return result


def expected_slots(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slots: dict[str, dict[str, Any]] = {}
    if spec["type"] == "compacting":
        slots["__machine_process_compacting"] = slot(spec["machine"])
        for index, value in enumerate(spec["inputs"]):
            slots[f"in{index}"] = slot(value)
    else:
        for row_index, pattern_row in enumerate(spec["pattern"]):
            for column_index, symbol in enumerate(pattern_row):
                if symbol != " ":
                    slots[f"cell_{row_index}_{column_index}"] = slot(spec["key"][symbol])
    slots["output"] = slot(spec["output"])
    return slots


def validate_payload(path: Path, compiled: bool, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing {'compiled' if compiled else 'assembled'} dockyard data: {path}")
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
        expected_type = "kjsgen:create_compacting" if expected["type"] == "compacting" else "kjsgen:create_mechanical_crafting"
        expected_params = {"heat": "none"} if expected["type"] == "compacting" else {"gridW": "5", "gridH": "5"}
        if card.get("type") != expected_type or card.get("params") != expected_params:
            failures.append(f"{recipe_id} compiled type or parameters drifted")
        if card.get("slots") != expected_slots(expected):
            failures.append(f"{recipe_id} compiled slots drifted")
        if card.get("replaceRecipe") is not False:
            failures.append(f"{recipe_id} unexpectedly replaces recipes by output")
    for stock_id in STOCK:
        exact = [entry for entry in removals if entry.get("recipeId") == stock_id]
        if len(exact) != 1:
            failures.append(f"compiled project must remove stock {stock_id} exactly once")
        elif any(str(exact[0].get(field, "")).strip() for field in ("output", "input", "mod")):
            failures.append(f"compiled removal for {stock_id} is broader than its exact ID")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    directory = catalog if catalog.is_dir() else catalog.parent
    items_path, recipes_path = directory / "items.csv", directory / "recipes.csv"
    if not items_path.is_file() or not recipes_path.is_file():
        failures.append(f"catalog must provide items.csv and recipes.csv: {catalog}")
        return
    with items_path.open(encoding="utf-8-sig", newline="") as handle:
        item_ids = {row.get("item_id", "") for row in csv.DictReader(handle)}
    with recipes_path.open(encoding="utf-8-sig", newline="") as handle:
        stock_rows = {row.get("recipe_id", ""): row for row in csv.DictReader(handle)}
    used = {
        output_id(value)
        for spec in RECIPES.values()
        for value in [spec.get("output"), spec.get("machine"), *spec.get("inputs", []), *spec.get("key", {}).values()]
        if value
    }
    missing = sorted(used - item_ids - VANILLA_ITEMS)
    if missing:
        failures.append(f"installed registry catalog is missing dockyard IDs: {missing}")
    for stock_id, expected in STOCK.items():
        row = stock_rows.get(stock_id)
        if not row:
            failures.append(f"installed catalog is missing stock recipe {stock_id}")
            continue
        if row.get("recipe_type") != expected["type"] or row.get("source_path") != expected["path"]:
            failures.append(f"stock recipe type/path drifted: {stock_id}")
        if output_id(row.get("outputs", "")) != expected["output"]:
            failures.append(f"stock recipe output drifted: {stock_id}")
        # Exact output counts are pinned from recipe_refs.csv below.
    refs_path = directory / "recipe_refs.csv"
    with refs_path.open(encoding="utf-8-sig", newline="") as handle:
        refs = list(csv.DictReader(handle))
    for stock_id, expected in STOCK.items():
        counts = [
            int(float(row["count"]))
            for row in refs
            if row.get("recipe_id") == stock_id and row.get("role") == "output" and row.get("count")
        ]
        if counts != [expected["count"]]:
            failures.append(f"stock recipe output count drifted: {stock_id}: {counts}")


def validate_quests(project: Path, failures: list[str]) -> None:
    payload = load_json(project / QUESTS)
    quest_rows = payload.get("chapter", {}).get("quests", [])
    by_key = {row.get("key", ""): row for row in quest_rows}
    if [key for key in by_key if key in QUESTS_EXPECTED] != list(QUESTS_EXPECTED):
        failures.append("dockyard observation quest order drifted")
    forbidden = {"rewards", "stage", "stages", "command", "commands", "recipe", "recipes"}
    for key, expected in QUESTS_EXPECTED.items():
        quest = by_key.get(key, {})
        if quest.get("dependencies") != expected["dependencies"]:
            failures.append(f"orbital quest dependency drifted: {key}")
        items = [(task.get("item"), task.get("count", 1)) for task in quest.get("tasks", [])]
        if items != expected["items"]:
            failures.append(f"orbital quest observation set drifted: {key}")
        if forbidden.intersection(quest):
            failures.append(f"orbital quest contains a gate or reward: {key}")
        if any(task.get("type") != "item" or not isinstance(task.get("count", 1), int) or task.get("count", 1) < 1 or task.get("consume_items", False) for task in quest.get("tasks", [])):
            failures.append(f"orbital quest is not a non-consuming item observation: {key}")


def validate(project: Path, catalog: Path | None = None, manifest: Path | None = None, compiled: Path | None = None) -> list[str]:
    failures: list[str] = []
    for relative in (SEED, ASSIGNMENTS, LAYOUT, QUESTS, DEFERRED):
        if not (project / relative).is_file():
            failures.append(f"missing orbital dockyard source file: {relative.as_posix()}")
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
            failures.append(f"{recipe_id} has no manufacturing rationale")
        if FORBIDDEN_REMOVAL_FIELDS.intersection(recipe):
            failures.append(f"{recipe_id} contains a broad removal directive")
        if not has_ancestor(recipe_id, CONSTRUCTION_RECIPE, by_id):
            failures.append(f"{recipe_id} is not downstream of Orbital Construction")

    scope_rows = [row for row in seed.get("recipes", []) if str(row.get("id", "")).startswith(("industrial_colonies:space/navigation/", "industrial_colonies:space/dockyard/", "industrial_colonies:space/station/"))]
    if {row.get("id") for row in scope_rows} != set(RECIPES):
        failures.append("orbital dockyard slice is not exactly the ten approved managed replacements")
    removals = [stock for spec in RECIPES.values() for stock in spec["remove"]]
    if set(removals) != set(STOCK) or len(removals) != 10:
        failures.append("orbital dockyard stock-removal set is not the exact ten approved IDs")
    if output_count(RECIPES["industrial_colonies:space/dockyard/docking_connector"]["output"]) != 2:
        failures.append("Docking Connector replacement must preserve its matched-pair output")
    fluid_inputs = by_id.get(
        "industrial_colonies:space/station/fluid_pipe_duct", {}
    ).get("inputs", [])
    if any("desh" in value for value in fluid_inputs):
        failures.append("first station fluid duct must not require off-world Desh")

    assignments = load_json(project / ASSIGNMENTS).get("nodes", {})
    for node, unlocks in NODE_UNLOCKS.items():
        if seed.get("phase_by_node", {}).get(node) != PHASE:
            failures.append(f"{node} is not assigned to {PHASE}")
        if assignments.get(node, {}).get("unlocks") != unlocks:
            failures.append(f"{node} unlock assignment drifted")
        if not str(assignments.get(node, {}).get("role", "")).strip():
            failures.append(f"{node} role is blank")
        if node in (project / LAYOUT).read_text(encoding="utf-8-sig"):
            failures.append(f"immutable MineColonies layout was expanded with {node}")

    docking_items = set(RECIPES["industrial_colonies:space/dockyard/docking_connector"]["key"].values())
    channels = {
        "item": "create:portable_storage_interface",
        "fluid": "create:portable_fluid_interface",
        "fe": "createaddition:portable_energy_interface",
        "data": "computercraft:wired_modem",
    }
    for channel, item in channels.items():
        if item not in docking_items:
            failures.append(f"Docking Connector lost its {channel} channel: {item}")

    deferred = (project / DEFERRED).read_text(encoding="utf-8-sig")
    if deferred.count("'rocketnautics:sputnik'") != 0:
        failures.append("stock Sputnik still has a second removal owner in the deferred boundary")
    if deferred.count("'ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water'") != 1:
        failures.append("water-to-oxygen shortcut boundary changed")
    for station_id in (
        "ad_astra:space_station/earth_orbit_space_station",
        "ad_astra:space_station/moon_orbit_space_station",
        "ad_astra:space_station/mars_orbit_space_station",
        "ad_astra:space_station/venus_orbit_space_station",
        "ad_astra:space_station/mercury_orbit_space_station",
        "ad_astra:space_station/glacio_orbit_space_station",
    ):
        if deferred.count(f"'{station_id}'") != 1:
            failures.append(f"prefab station boundary changed: {station_id}")
    for quantum_id in ("ae2:network/blocks/quantum_link", "ae2:network/blocks/quantum_ring"):
        if seed.get("additional_removals", []).count(quantum_id) != 1:
            failures.append(f"AE2 quantum bridge retirement changed: {quantum_id}")

    validate_quests(project, failures)
    if catalog is not None:
        validate_catalog(catalog, failures)
    if manifest is not None:
        validate_payload(manifest, False, failures)
    if compiled is not None:
        validate_payload(compiled, True, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate(
        args.project.resolve(),
        args.catalog.resolve() if args.catalog else None,
        args.manifest.resolve() if args.manifest else None,
        args.compiled.resolve() if args.compiled else None,
    )
    if failures:
        print("FAIL: orbital dockyard and station slice is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("PASS: ten exact managed replacements establish post-construction navigation, four-channel docking, and 16-to-32-item station-fabrication batches with observation-only guidance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
