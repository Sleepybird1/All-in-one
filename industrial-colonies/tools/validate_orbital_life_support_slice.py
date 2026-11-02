#!/usr/bin/env python3
"""Validate the source-owned first orbital pressure and life-support slice."""

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
DEFERRED = Path("pack-scripts/server_scripts/industrial_space_entry_deferred.js")

PHASE = "Orbital Engineering"
ENTRY_RECIPE = "industrial_colonies:space/propulsion/thruster_mount"
SAFE_OXYGEN_LOADING = "ad_astra:oxygen_loading/oxygen_from_oxygen_loading_oxygen"
WATER_OXYGEN_SHORTCUT = "ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water"

LIFE_SUPPORT_RECIPES: dict[str, dict[str, Any]] = {
    "industrial_colonies:space/life_support/fan": {
        "node": "CR02 — Pressure Hardware",
        "phase": PHASE,
        "order": 150,
        "type": "mechanical_crafting",
        "pattern": ["  P  ", " HPH ", "PFMFP", " HPH ", "  C  "],
        "key": {
            "P": "create:propeller",
            "H": "tfmg:heavy_plate",
            "F": "tfmg:steel_frame",
            "M": "tfmg:electric_motor",
            "C": "tfmg:circuit_board",
        },
        "output": "2x ad_astra:fan",
        "remove": ["ad_astra:fan"],
        "exclusive_output": True,
        "depends_on": [ENTRY_RECIPE],
    },
    "industrial_colonies:space/life_support/gas_tank": {
        "node": "CR02 — Pressure Hardware",
        "phase": PHASE,
        "order": 160,
        "type": "mechanical_crafting",
        "pattern": [" RVR ", "RHPHR", "VPTPV", "RHPHR", " RVR "],
        "key": {
            "R": "tfmg:rubber_sheet",
            "V": "tfmg:steel_fluid_valve",
            "H": "tfmg:heavy_plate",
            "P": "tfmg:steel_pipe",
            "T": "mekanism:elite_chemical_tank",
        },
        "output": "2x ad_astra:gas_tank",
        "remove": ["ad_astra:gas_tank"],
        "exclusive_output": True,
        "depends_on": [ENTRY_RECIPE],
    },
    "industrial_colonies:space/life_support/large_gas_tank": {
        "node": "CR02 — Pressure Hardware",
        "phase": PHASE,
        "order": 170,
        "type": "mechanical_crafting",
        "pattern": [" HPH ", "HGTGH", "PTUTP", "HGTGH", " HPH "],
        "key": {
            "H": "tfmg:heavy_plate",
            "P": "tfmg:steel_pipe",
            "G": "ad_astra:gas_tank",
            "T": "tfmg:steel_fluid_valve",
            "U": "mekanism:ultimate_chemical_tank",
        },
        "output": "ad_astra:large_gas_tank",
        "remove": ["ad_astra:large_gas_tank"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/life_support/gas_tank"],
    },
    "industrial_colonies:space/life_support/oxygen_gear": {
        "node": "CR02 — Pressure Hardware",
        "phase": PHASE,
        "order": 180,
        "type": "mechanical_crafting",
        "pattern": [" RPR ", "RVCVR", "PQEQP", "RVCVR", " RPR "],
        "key": {
            "R": "tfmg:rubber_sheet",
            "P": "tfmg:plastic_sheet",
            "V": "tfmg:steel_fluid_valve",
            "C": "tfmg:circuit_board",
            "Q": "mekanism:ultimate_control_circuit",
            "E": "tfmg:electric_pump",
        },
        "output": "ad_astra:oxygen_gear",
        "remove": ["ad_astra:oxygen_gear"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/life_support/gas_tank"],
    },
    "industrial_colonies:space/life_support/oxygen_loader": {
        "node": "CR02 — Habitat Life Support",
        "phase": PHASE,
        "order": 190,
        "type": "mechanical_crafting",
        "pattern": ["FPCPF", "HVTVH", "GELEG", "HVTVH", "FPCPF"],
        "key": {
            "F": "ad_astra:fan",
            "P": "tfmg:steel_pipe",
            "C": "tfmg:circuit_board",
            "H": "tfmg:heavy_plate",
            "V": "tfmg:steel_fluid_valve",
            "T": "tfmg:plastic_sheet",
            "G": "ad_astra:gas_tank",
            "E": "tfmg:electric_pump",
            "L": "mekanism:rotary_condensentrator",
        },
        "output": "ad_astra:oxygen_loader",
        "remove": ["ad_astra:oxygen_loader"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/life_support/fan",
            "industrial_colonies:space/life_support/gas_tank",
        ],
    },
    "industrial_colonies:space/life_support/oxygen_distributor": {
        "node": "CR02 — Habitat Life Support",
        "phase": PHASE,
        "order": 200,
        "type": "mechanical_crafting",
        "pattern": ["FVEVF", "HCTCH", "GLOLG", "HCUCH", "FVEVF"],
        "key": {
            "F": "ad_astra:fan",
            "V": "tfmg:steel_fluid_valve",
            "E": "ae2:engineering_processor",
            "H": "tfmg:heavy_plate",
            "C": "tfmg:circuit_board",
            "T": "computercraft:computer_advanced",
            "G": "ad_astra:large_gas_tank",
            "L": "ad_astra:oxygen_loader",
            "O": "ad_astra:oxygen_gear",
            "U": "mekanism:ultimate_energy_cube",
        },
        "output": "ad_astra:oxygen_distributor",
        "remove": ["ad_astra:oxygen_distributor"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/life_support/fan",
            "industrial_colonies:space/life_support/large_gas_tank",
            "industrial_colonies:space/life_support/oxygen_gear",
            "industrial_colonies:space/life_support/oxygen_loader",
        ],
    },
    "industrial_colonies:space/life_support/oxygen_sensor": {
        "node": "CR02 — Habitat Life Support",
        "phase": PHASE,
        "order": 210,
        "type": "mechanical_crafting",
        "pattern": ["  G  ", " PCP ", "GMEAG", " PFP ", "  R  "],
        "key": {
            "G": "minecraft:tinted_glass",
            "P": "tfmg:plastic_sheet",
            "C": "tfmg:circuit_board",
            "M": "computercraft:monitor_advanced",
            "E": "ae2:calculation_processor",
            "A": "mekanism:ultimate_control_circuit",
            "F": "ad_astra:fan",
            "R": "tfmg:rubber_sheet",
        },
        "output": "ad_astra:oxygen_sensor",
        "remove": ["ad_astra:oxygen_sensor"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/life_support/oxygen_distributor"],
    },
    "industrial_colonies:space/life_support/vent": {
        "node": "CR02 — Habitat Life Support",
        "phase": PHASE,
        "order": 220,
        "type": "mechanical_crafting",
        "pattern": [" HPH ", "PRRRP", "HPPPH", "PRRRP", " HPH "],
        "key": {
            "H": "tfmg:heavy_plate",
            "P": "tfmg:steel_pipe",
            "R": "tfmg:rubber_sheet",
        },
        "output": "16x ad_astra:vent",
        "remove": ["ad_astra:vent"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/life_support/oxygen_distributor"],
    },
    "industrial_colonies:space/life_support/airlock": {
        "node": "CR02 — Habitat Life Support",
        "phase": PHASE,
        "order": 230,
        "type": "mechanical_crafting",
        "pattern": ["RHHHR", "HFSFH", "HTCTH", "HFSFH", "RHHHR"],
        "key": {
            "R": "tfmg:rubber_sheet",
            "H": "tfmg:heavy_plate",
            "F": "tfmg:steel_frame",
            "S": "ad_astra:oxygen_sensor",
            "T": "tfmg:heavy_plated_door",
            "C": "computercraft:computer_advanced",
        },
        "output": "2x ad_astra:airlock",
        "remove": ["ad_astra:airlock"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/life_support/oxygen_sensor",
            "industrial_colonies:space/life_support/vent",
        ],
    },
}

NODE_UNLOCKS = {
    "CR02 — Pressure Hardware": [
        "ad_astra:fan",
        "ad_astra:gas_tank",
        "ad_astra:large_gas_tank",
        "ad_astra:oxygen_gear",
    ],
    "CR02 — Habitat Life Support": [
        "ad_astra:oxygen_loader",
        "ad_astra:oxygen_distributor",
        "ad_astra:oxygen_sensor",
        "ad_astra:vent",
        "ad_astra:airlock",
    ],
}

STOCK_RECIPES = {
    "ad_astra:fan": ("ad_astra:fan", "data/ad_astra/recipe/fan.json"),
    "ad_astra:gas_tank": ("ad_astra:gas_tank", "data/ad_astra/recipe/gas_tank.json"),
    "ad_astra:large_gas_tank": (
        "ad_astra:large_gas_tank",
        "data/ad_astra/recipe/large_gas_tank.json",
    ),
    "ad_astra:oxygen_gear": (
        "ad_astra:oxygen_gear",
        "data/ad_astra/recipe/oxygen_gear.json",
    ),
    "ad_astra:oxygen_loader": (
        "ad_astra:oxygen_loader",
        "data/ad_astra/recipe/oxygen_loader.json",
    ),
    "ad_astra:oxygen_distributor": (
        "ad_astra:oxygen_distributor",
        "data/ad_astra/recipe/oxygen_distributor.json",
    ),
    "ad_astra:oxygen_sensor": (
        "ad_astra:oxygen_sensor",
        "data/ad_astra/recipe/oxygen_sensor.json",
    ),
    "ad_astra:vent": ("ad_astra:vent", "data/ad_astra/recipe/vent.json"),
    "ad_astra:airlock": ("ad_astra:airlock", "data/ad_astra/recipe/airlock.json"),
}

OXYGEN_ROUTE_RECIPES = {
    "mekanism:separator/water": {
        "recipe_type": "mekanism:separating",
        "source_path": "data/mekanism/recipe/separator/water.json",
        "outputs": {"mekanism:hydrogen", "mekanism:oxygen"},
        "tags": {"minecraft:water"},
    },
    "mekanism:rotary/oxygen": {
        "recipe_type": "mekanism:rotary",
        "source_path": "data/mekanism/recipe/rotary/oxygen.json",
        "outputs": {"mekanism:oxygen"},
        "inputs": {"mekanism:oxygen"},
        "tags": {"c:oxygen"},
    },
    SAFE_OXYGEN_LOADING: {
        "recipe_type": "ad_astra:oxygen_loading",
        "source_path": (
            "data/ad_astra/recipe/oxygen_loading/"
            "oxygen_from_oxygen_loading_oxygen.json"
        ),
        "outputs": {"ad_astra:oxygen"},
        "tags": {"ad_astra:oxygen"},
    },
    WATER_OXYGEN_SHORTCUT: {
        "recipe_type": "ad_astra:oxygen_loading",
        "source_path": (
            "data/ad_astra/recipe/oxygen_loading/"
            "oxygen_from_oxygen_loading_water.json"
        ),
        "outputs": {"ad_astra:oxygen"},
        "tags": {"minecraft:water"},
    },
}

FORBIDDEN_REMOVAL_FIELDS = {
    "remove_by_output",
    "removeByOutput",
    "remove_by_mod",
    "removeByMod",
    "replace",
    "replace_recipe",
    "replaceRecipe",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def output_id(value: Any) -> str:
    text = str(value or "").strip()
    match = re.fullmatch(r"(?:(\d+(?:\.\d+)?)x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)", text)
    return match.group(2) if match else text


def split_ids(value: str) -> set[str]:
    return {output_id(part) for part in str(value or "").split("|") if part.strip()}


def recipe_rows(payload: dict[str, Any], recipe_id: str) -> list[dict[str, Any]]:
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


def catalog_paths(catalog: Path) -> tuple[Path, Path]:
    if catalog.is_dir():
        return catalog / "items.csv", catalog / "recipes.csv"
    return catalog.parent / "items.csv", catalog


def expected_card_slots(expected: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slots: dict[str, dict[str, Any]] = {}
    for row_index, pattern_row in enumerate(expected["pattern"]):
        for column_index, character in enumerate(pattern_row):
            if character == " ":
                continue
            slots[f"cell_{row_index}_{column_index}"] = {
                "kind": "ITEM",
                "id": output_id(expected["key"][character]),
            }
    output_text = str(expected["output"])
    count_match = re.fullmatch(
        r"(?:(\d+)x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)", output_text
    )
    if count_match is None:
        raise ValueError(f"cannot derive compiled output slot from {output_text!r}")
    output_slot: dict[str, Any] = {"kind": "ITEM", "id": count_match.group(2)}
    if count_match.group(1) is not None:
        output_slot["count"] = int(count_match.group(1))
    slots["output"] = output_slot
    return slots


def validate_manifest(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing assembled life-support manifest: {path}")
        return
    payload = load_json(path)
    for recipe_id, expected in LIFE_SUPPORT_RECIPES.items():
        found = recipe_rows(payload, recipe_id)
        if len(found) != 1:
            failures.append(f"assembled manifest must contain exactly one {recipe_id}")
            continue
        recipe = found[0]
        for field, value in expected.items():
            if field == "depends_on":
                continue
            if recipe.get(field) != value:
                failures.append(f"assembled {recipe_id} {field} drifted")
        missing_dependencies = sorted(
            set(expected["depends_on"]) - set(recipe.get("depends_on", []))
        )
        if missing_dependencies:
            failures.append(
                f"assembled {recipe_id} lost life-support dependencies: {missing_dependencies}"
            )


def validate_compiled(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing KJSGen life-support project: {path}")
        return
    payload = load_json(path)
    cards = payload.get("recipes", [])
    removals = payload.get("removals", [])
    for recipe_id, expected in LIFE_SUPPORT_RECIPES.items():
        found = [card for card in cards if card.get("recipeId") == recipe_id]
        if len(found) != 1:
            failures.append(f"KJSGen project must contain exactly one life-support card {recipe_id}")
            continue
        card = found[0]
        if card.get("type") != "kjsgen:create_mechanical_crafting":
            failures.append(f"{recipe_id} KJSGen card is not Mechanical Crafting")
        if card.get("replaceRecipe") is not False:
            failures.append(f"{recipe_id} KJSGen card unexpectedly replaces by output")
        if card.get("params") != {"gridW": "5", "gridH": "5"}:
            failures.append(f"{recipe_id} KJSGen grid dimensions drifted")
        if card.get("slots") != expected_card_slots(expected):
            failures.append(f"{recipe_id} KJSGen slots drifted")

        stock_id = expected["remove"][0]
        exact_removals = [row for row in removals if row.get("recipeId") == stock_id]
        if len(exact_removals) != 1:
            failures.append(f"KJSGen removals must contain exact stock ID once: {stock_id}")
        elif any(
            str(exact_removals[0].get(field, "")).strip()
            for field in ("output", "input", "mod")
        ):
            failures.append(f"KJSGen removal for {stock_id} is broader than its exact ID")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    items_path, recipes_path = catalog_paths(catalog)
    if not items_path.is_file() or not recipes_path.is_file():
        failures.append(
            f"catalog must provide items.csv and recipes.csv: {items_path}, {recipes_path}"
        )
        return

    with items_path.open("r", encoding="utf-8-sig", newline="") as handle:
        items = {row.get("item_id", ""): row for row in csv.DictReader(handle)}
    with recipes_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row.get("recipe_id", ""): row for row in rows}

    required_items = {
        output_id(value)
        for expected in LIFE_SUPPORT_RECIPES.values()
        for value in [expected["output"], *expected["key"].values()]
        if not output_id(value).startswith("minecraft:")
    }
    missing_items = sorted(required_items - set(items))
    if missing_items:
        failures.append(f"installed item catalog is missing life-support IDs: {missing_items}")

    for recipe_id, (stock_output, source_path) in STOCK_RECIPES.items():
        row = by_id.get(recipe_id)
        if row is None:
            failures.append(f"installed catalog is missing stock life-support recipe {recipe_id}")
            continue
        if row.get("recipe_type") != "minecraft:crafting_shaped":
            failures.append(f"stock {recipe_id} recipe type drifted")
        if row.get("source_path") != source_path:
            failures.append(f"stock {recipe_id} source path drifted")
        if split_ids(row.get("outputs", "")) != {stock_output}:
            failures.append(f"stock {recipe_id} output drifted")

        producers = {
            candidate.get("recipe_id", "")
            for candidate in rows
            if stock_output in split_ids(candidate.get("outputs", ""))
        }
        if producers != {recipe_id}:
            failures.append(
                f"stock output {stock_output} has unowned producer routes: {sorted(producers)}"
            )

    for recipe_id, expected in OXYGEN_ROUTE_RECIPES.items():
        row = by_id.get(recipe_id)
        if row is None:
            failures.append(f"installed catalog is missing oxygen-route recipe {recipe_id}")
            continue
        for field in ("recipe_type", "source_path"):
            if row.get(field) != expected[field]:
                failures.append(f"oxygen route {recipe_id} {field} drifted")
        for field in ("outputs", "inputs", "tags"):
            if field in expected and split_ids(row.get(field, "")) != expected[field]:
                failures.append(f"oxygen route {recipe_id} {field} drifted")


def validate(
    project: Path,
    catalog: Path | None = None,
    manifest: Path | None = None,
    compiled: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    for relative in (SEED, ASSIGNMENTS, DEFERRED):
        if not (project / relative).is_file():
            failures.append(f"missing orbital life-support source file: {relative.as_posix()}")
    if failures:
        return failures

    seed = load_json(project / SEED)
    rows = seed.get("recipes", [])
    by_id = {row.get("id", ""): row for row in rows}
    if len(by_id) != len(rows):
        failures.append("managed seed contains duplicate or blank recipe IDs")
    if ENTRY_RECIPE not in by_id:
        failures.append(f"managed seed is missing post-Star entry recipe {ENTRY_RECIPE}")

    for recipe_id, expected in LIFE_SUPPORT_RECIPES.items():
        found = recipe_rows(seed, recipe_id)
        if len(found) != 1:
            failures.append(f"managed seed must contain exactly one {recipe_id}")
            continue
        recipe = found[0]
        for field, value in expected.items():
            if recipe.get(field) != value:
                failures.append(f"{recipe_id} {field} drifted")
        if not str(recipe.get("comment", "")).strip():
            failures.append(f"{recipe_id} has no manufacturing rationale")
        if set(recipe).intersection(FORBIDDEN_REMOVAL_FIELDS):
            failures.append(f"{recipe_id} contains a broad removal directive")
        if len(recipe.get("pattern", [])) != 5 or any(
            len(row) != 5 for row in recipe.get("pattern", [])
        ):
            failures.append(f"{recipe_id} is not a 5x5 mechanical assembly")
        if not any(output_id(value).startswith("tfmg:") for value in recipe.get("key", {}).values()):
            failures.append(f"{recipe_id} lost its TFMG-first manufacturing identity")
        if not has_ancestor(recipe_id, ENTRY_RECIPE, by_id):
            failures.append(f"{recipe_id} is not downstream of the thruster mount")

    managed_owners: dict[str, list[str]] = {}
    for row in rows:
        managed_owners.setdefault(output_id(row.get("output")), []).append(row.get("id", ""))
    for expected in LIFE_SUPPORT_RECIPES.values():
        item_id = output_id(expected["output"])
        owners = managed_owners.get(item_id, [])
        if len(owners) != 1:
            failures.append(f"managed seed must own {item_id} exactly once, found {owners}")

    phase_by_node = seed.get("phase_by_node", {})
    for node in NODE_UNLOCKS:
        if phase_by_node.get(node) != PHASE:
            failures.append(f"{node} is not assigned to {PHASE}")

    assignments = load_json(project / ASSIGNMENTS).get("nodes", {})
    for node, unlocks in NODE_UNLOCKS.items():
        assignment = assignments.get(node, {})
        if assignment.get("unlocks") != unlocks:
            failures.append(f"{node} unlock assignment drifted")
        if not str(assignment.get("role", "")).strip():
            failures.append(f"{node} has no assignment role")

    deferred_source = (project / DEFERRED).read_text(encoding="utf-8-sig")
    if deferred_source.count(f"'{SAFE_OXYGEN_LOADING}'") != 0:
        failures.append("safe oxygen-to-oxygen Ad Astra loading pass-through was re-deferred")
    if deferred_source.count(f"'{WATER_OXYGEN_SHORTCUT}'") != 1:
        failures.append("direct Ad Astra water-to-oxygen shortcut must remain exactly deferred")
    if re.search(r"event\.remove\(\{\s*(output|mod|type|input)\s*:", deferred_source):
        failures.append("space boundary contains a broad recipe removal")

    if catalog is not None:
        validate_catalog(catalog, failures)
    if manifest is not None:
        validate_manifest(manifest, failures)
    if compiled is not None:
        validate_compiled(compiled, failures)
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
        print("FAIL: first orbital pressure and life-support slice is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "PASS: nine exact-stock Ad Astra pressure/life-support outputs are source-owned "
        "as 5x5 assemblies across two post-thruster branches; Mekanism oxygen can use "
        "the retained oxygen pass-through while direct water loading remains deferred."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
