#!/usr/bin/env python3
"""Validate the source-owned first post-Star modular propulsion slice."""

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
DEFERRED = Path("pack-scripts/server_scripts/industrial_space_entry_deferred.js")

PHASE = "Orbital Engineering"
FLIGHT_RECIPE = "industrial_colonies:space/orbital_flight_computer"
FLIGHT_OUTPUT = "industrial_colonies:orbital_flight_computer"
STAR = "industrial_colonies:industrial_star"

PROPULSION_RECIPES: dict[str, dict[str, Any]] = {
    "industrial_colonies:space/propulsion/hose_anchor": {
        "node": "CR02 — Propellant Handling",
        "phase": PHASE,
        "order": 110,
        "type": "mechanical_crafting",
        "pattern": ["HVH", "PCP", "HEH"],
        "key": {
            "H": "tfmg:heavy_plate",
            "V": "tfmg:steel_fluid_valve",
            "P": "tfmg:industrial_pipe",
            "C": "mekanism:ultimate_control_circuit",
            "E": "tfmg:electric_pump",
        },
        "output": "2x rocketnautics:hose_anchor",
        "exclusive_output": True,
        "depends_on": [FLIGHT_RECIPE],
    },
    "industrial_colonies:space/propulsion/engine_pipes": {
        "node": "CR02 — Propellant Handling",
        "phase": PHASE,
        "order": 120,
        "type": "mechanical_crafting",
        "pattern": ["SIPIS", "VHCHV", "SIPIS"],
        "key": {
            "S": "tfmg:steel_pipe",
            "I": "tfmg:industrial_pipe",
            "P": "tfmg:electric_pump",
            "V": "tfmg:steel_fluid_valve",
            "H": "rocketnautics:hose_anchor",
            "C": "tfmg:circuit_board",
        },
        "output": "8x rocketnautics:engine_pipes",
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/propulsion/hose_anchor"],
    },
    "industrial_colonies:space/propulsion/engine_nozzle": {
        "node": "CR02 — Modular Propulsion",
        "phase": PHASE,
        "order": 130,
        "type": "mechanical_crafting",
        "pattern": ["  A  ", " AHA ", "ATHTA", " HPH ", "  S  "],
        "key": {
            "A": "mekanism:alloy_atomic",
            "H": "tfmg:heavy_plate",
            "T": "rocketnautics:titanium_alloy_sheet",
            "P": "rocketnautics:engine_pipes",
            "S": "tfmg:steel_mechanism",
        },
        "output": "2x rocketnautics:engine_nozzle",
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:space/propulsion/engine_pipes"],
    },
    "industrial_colonies:space/propulsion/thruster_mount": {
        "node": "CR02 — Modular Propulsion",
        "phase": PHASE,
        "order": 140,
        "type": "mechanical_crafting",
        "pattern": ["FHTHF", "MBCBM", "PAUAP", "MBEBM", "FHNHF"],
        "key": {
            "F": "tfmg:steel_frame",
            "H": "tfmg:heavy_plate",
            "T": "tfmg:transformer",
            "M": "tfmg:steel_mechanism",
            "B": "tfmg:circuit_board",
            "C": "computercraft:computer_advanced",
            "P": "rocketnautics:engine_pipes",
            "A": "ae2:engineering_processor",
            "U": "mekanism:ultimate_control_circuit",
            "E": "rocketnautics:engine_nozzle",
            "N": "rocketnautics:hose_anchor",
        },
        "output": "rocketnautics:thruster_mount",
        "exclusive_output": True,
        "depends_on": [
            FLIGHT_RECIPE,
            "industrial_colonies:space/propulsion/hose_anchor",
            "industrial_colonies:space/propulsion/engine_pipes",
            "industrial_colonies:space/propulsion/engine_nozzle",
        ],
    },
}

NODE_UNLOCKS = {
    "CR02 — Propellant Handling": [
        "rocketnautics:hose_anchor",
        "rocketnautics:engine_pipes",
    ],
    "CR02 — Modular Propulsion": [
        "rocketnautics:engine_nozzle",
        "rocketnautics:thruster_mount",
    ],
}

RECIPELESS_OUTPUTS = {
    "rocketnautics:hose_anchor",
    "rocketnautics:engine_pipes",
    "rocketnautics:engine_nozzle",
    "rocketnautics:thruster_mount",
}

PHYSICAL_COMPONENT_INPUTS = {
    "industrial_colonies:space/propulsion/engine_pipes": {"rocketnautics:hose_anchor"},
    "industrial_colonies:space/propulsion/engine_nozzle": {"rocketnautics:engine_pipes"},
    "industrial_colonies:space/propulsion/thruster_mount": {
        "rocketnautics:hose_anchor",
        "rocketnautics:engine_pipes",
        "rocketnautics:engine_nozzle",
    },
}

EXACT_STOCK_DEFERRALS = {
    "rocketnautics:mechanical_crafting/rocket_thruster",
    "rocketnautics:mechanical_crafting/booster_thruster",
    "rocketnautics:crafting/equipment/jetpack",
    "simulated:physics_assembler",
}

FORBIDDEN_MANAGED_OUTPUTS = {
    "rocketnautics:rocket_thruster",
    "rocketnautics:booster_thruster",
    "rocketnautics:jetpack",
}

REMOVAL_FIELDS = {
    "remove",
    "removals",
    "remove_by_output",
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


def recipe_rows(payload: dict[str, Any], recipe_id: str) -> list[dict[str, Any]]:
    return [row for row in payload.get("recipes", []) if row.get("id") == recipe_id]


def all_key_items(recipe: dict[str, Any]) -> set[str]:
    return {output_id(value) for value in recipe.get("key", {}).values()}


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
    recipe = recipes.get(recipe_id, {})
    return any(
        has_ancestor(str(parent), ancestor, recipes, seen.copy())
        for parent in recipe.get("depends_on", [])
    )


def catalog_paths(catalog: Path) -> tuple[Path, Path]:
    if catalog.is_dir():
        return catalog / "items.csv", catalog / "recipes.csv"
    return catalog.parent / "items.csv", catalog


def validate_manifest(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing assembled propulsion manifest: {path}")
        return
    payload = load_json(path)
    for recipe_id, expected in PROPULSION_RECIPES.items():
        found = recipe_rows(payload, recipe_id)
        if len(found) != 1:
            failures.append(f"assembled manifest must contain exactly one {recipe_id}")
            continue
        recipe = found[0]
        for field, value in expected.items():
            if field in {"exclusive_output", "depends_on"}:
                continue
            if recipe.get(field) != value:
                failures.append(f"assembled {recipe_id} {field} drifted")
        expected_dependencies = set(expected["depends_on"])
        actual_dependencies = set(recipe.get("depends_on", []))
        if not expected_dependencies.issubset(actual_dependencies):
            failures.append(
                f"assembled {recipe_id} lost explicit orbital dependencies: "
                f"{sorted(expected_dependencies - actual_dependencies)}"
            )
        if "exclusive_output" in recipe:
            failures.append(
                f"assembled {recipe_id} retained exclusive_output despite having no stock route"
            )
        if recipe.get("remove", []) != []:
            failures.append(f"assembled {recipe_id} gained exact source removals")
        present_removal_fields = sorted((REMOVAL_FIELDS - {"remove"}).intersection(recipe))
        if present_removal_fields:
            failures.append(
                f"assembled {recipe_id} contains removal metadata: {present_removal_fields}"
            )


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


def validate_compiled_cards(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing KJSGen propulsion project: {path}")
        return
    payload = load_json(path)
    cards = payload.get("recipes", [])
    for recipe_id, expected in PROPULSION_RECIPES.items():
        found = [card for card in cards if card.get("recipeId") == recipe_id]
        if len(found) != 1:
            failures.append(f"KJSGen project must contain exactly one propulsion card {recipe_id}")
            continue
        card = found[0]
        expected_params = {
            "gridW": str(len(expected["pattern"][0])),
            "gridH": str(len(expected["pattern"])),
        }
        if card.get("type") != "kjsgen:create_mechanical_crafting":
            failures.append(f"{recipe_id} KJSGen card is not Mechanical Crafting")
        if card.get("replaceRecipe") is not False:
            failures.append(f"{recipe_id} KJSGen card unexpectedly replaces a stock recipe")
        if card.get("params") != expected_params:
            failures.append(f"{recipe_id} KJSGen grid dimensions drifted")
        if card.get("slots") != expected_card_slots(expected):
            failures.append(f"{recipe_id} KJSGen slots drifted")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    items_path, recipes_path = catalog_paths(catalog)
    if not items_path.is_file() or not recipes_path.is_file():
        failures.append(
            f"catalog must provide items.csv and recipes.csv: {items_path}, {recipes_path}"
        )
        return

    with items_path.open("r", encoding="utf-8-sig", newline="") as handle:
        item_rows = list(csv.DictReader(handle))
    with recipes_path.open("r", encoding="utf-8-sig", newline="") as handle:
        source_recipes = list(csv.DictReader(handle))

    items = {row.get("item_id", ""): row for row in item_rows}
    all_ingredients = {
        output_id(value)
        for expected in PROPULSION_RECIPES.values()
        for value in expected["key"].values()
    }
    missing_items = sorted((RECIPELESS_OUTPUTS | all_ingredients) - set(items))
    if missing_items:
        failures.append(f"installed item catalog is missing propulsion IDs: {missing_items}")

    for item_id in sorted(RECIPELESS_OUTPUTS):
        row = items.get(item_id)
        if row is None:
            continue
        if row.get("produced_by_recipes") != "0":
            failures.append(f"{item_id} is no longer recipe-less in the installed catalog")
        if "cosmonautics-" not in row.get("source_jars", ""):
            failures.append(f"{item_id} is no longer owned by the installed Cosmonautics JAR")

    unexpected_routes: list[str] = []
    for row in source_recipes:
        outputs = {output_id(value) for value in row.get("outputs", "").split("|")}
        if outputs & RECIPELESS_OUTPUTS:
            unexpected_routes.append(row.get("recipe_id", ""))
    if unexpected_routes:
        failures.append(
            "recipe-less propulsion outputs gained stock source routes: "
            f"{sorted(set(unexpected_routes))}"
        )

    by_id = {row.get("recipe_id", ""): row for row in source_recipes}
    missing_deferrals = sorted(EXACT_STOCK_DEFERRALS - set(by_id))
    if missing_deferrals:
        failures.append(f"installed catalog is missing stock deferral IDs: {missing_deferrals}")
    assembler = by_id.get("simulated:physics_assembler")
    if assembler is not None:
        if assembler.get("recipe_type") != "minecraft:crafting_shaped":
            failures.append("simulated:physics_assembler recipe type drifted")
        if output_id(assembler.get("outputs")) != "simulated:physics_assembler":
            failures.append("simulated:physics_assembler output drifted")
        expected_nested = (
            "create-aeronautics-bundled-1.21.1-1.3.0.jar!/META-INF/jarjar/"
            "dev.simulated_team.simulated.simulated-neoforge-1.21.1-1.3.0.jar"
        )
        if assembler.get("source_jar") != expected_nested:
            failures.append("simulated:physics_assembler nested source JAR drifted")


def validate(
    project: Path,
    catalog: Path | None = None,
    manifest: Path | None = None,
    compiled: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    required = (SEED, ASSIGNMENTS, LAYOUT, DEFERRED)
    for relative in required:
        if not (project / relative).is_file():
            failures.append(f"missing orbital propulsion source file: {relative.as_posix()}")
    if failures:
        return failures

    seed = load_json(project / SEED)
    rows = seed.get("recipes", [])
    by_id = {row.get("id", ""): row for row in rows}
    if len(by_id) != len(rows):
        failures.append("managed seed contains duplicate or blank recipe IDs")

    flight_rows = recipe_rows(seed, FLIGHT_RECIPE)
    if len(flight_rows) != 1:
        failures.append("managed seed must contain exactly one Orbital Flight Computer recipe")
    else:
        flight = flight_rows[0]
        if output_id(flight.get("output")) != FLIGHT_OUTPUT:
            failures.append("Orbital Flight Computer output drifted")
        if STAR not in {output_id(value) for value in flight.get("key", {}).values()}:
            failures.append("Orbital Flight Computer no longer physically consumes the Industrial Star")

    for recipe_id, expected in PROPULSION_RECIPES.items():
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
        present_removal_fields = sorted(REMOVAL_FIELDS.intersection(recipe))
        if present_removal_fields:
            failures.append(
                f"{recipe_id} invents removal metadata for a recipe-less output: "
                f"{present_removal_fields}"
            )
        if not has_ancestor(recipe_id, FLIGHT_RECIPE, by_id):
            failures.append(f"{recipe_id} is not downstream of the Orbital Flight Computer")

    output_owners: dict[str, list[str]] = {}
    for row in rows:
        output_owners.setdefault(output_id(row.get("output")), []).append(row.get("id", ""))
    for item_id in sorted(RECIPELESS_OUTPUTS):
        owners = output_owners.get(item_id, [])
        if len(owners) != 1:
            failures.append(f"managed seed must own {item_id} exactly once, found {owners}")

    for recipe_id, required_items in PHYSICAL_COMPONENT_INPUTS.items():
        actual = all_key_items(by_id.get(recipe_id, {}))
        missing = sorted(required_items - actual)
        if missing:
            failures.append(f"{recipe_id} lost physical propulsion subassemblies: {missing}")

    for row in rows:
        if output_id(row.get("output")) in FORBIDDEN_MANAGED_OUTPUTS:
            failures.append(
                f"simple ship bootstrap remains disabled, but managed seed produces {row.get('output')}"
            )

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

    layout_source = (project / LAYOUT).read_text(encoding="utf-8-sig")
    for node in {"CR02 — Orbital Guidance", *NODE_UNLOCKS}:
        if node in layout_source:
            failures.append(f"immutable MineColonies layout was expanded with managed-only node {node}")

    deferred_source = (project / DEFERRED).read_text(encoding="utf-8-sig")
    for recipe_id in sorted(EXACT_STOCK_DEFERRALS):
        if deferred_source.count(f"'{recipe_id}'") != 1:
            failures.append(f"space boundary must defer exact recipe ID once: {recipe_id}")
    simulated_ids = set(re.findall(r"'((?:simulated):[a-z0-9_./-]+)'", deferred_source))
    if simulated_ids != {"simulated:physics_assembler"}:
        failures.append(f"Simulated deferral scope is not exact: {sorted(simulated_ids)}")
    if re.search(r"event\.remove\(\{\s*(output|mod|type|input)\s*:", deferred_source):
        failures.append("space boundary contains a broad recipe removal")

    if catalog is not None:
        validate_catalog(catalog, failures)
    if manifest is not None:
        validate_manifest(manifest, failures)
    if compiled is not None:
        validate_compiled_cards(compiled, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument(
        "--catalog",
        type=Path,
        help="Fresh installed recipe catalog directory or recipes.csv (optional).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Assembled managed-recipe manifest to verify (optional).",
    )
    parser.add_argument(
        "--compiled",
        type=Path,
        help="Managed or merged KJSGen project whose four propulsion cards must survive (optional).",
    )
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
        print("FAIL: first post-Star modular propulsion slice is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "PASS: four recipe-less Cosmonautics propulsion parts are source-owned across "
        "two Orbital Engineering assignments, form a physical component chain downstream "
        "of the Industrial Star flight computer, and leave simple propulsion plus the "
        "stock physics assembler exactly deferred."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
