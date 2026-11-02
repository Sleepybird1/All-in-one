#!/usr/bin/env python3
"""Deepen fourteen exact active MEGA storage/crafting rejections.

Every selected review has the immutable note ``Too cheap — make it more
complex.``  The redesign compounds prior tiers instead of rebuilding each
block from the same cheap shell.  Memory components, item cells, and crafting
storage each have a distinct physical role, with TFMG power/containment and a
Railway-to-Refined-Radiance manufacturing transition at the 256M endpoint.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"

REJECTION_NOTE = "Too cheap — make it more complex."

REVIEWED_HASHES = {
    "industrial_colonies:v3_ae2/mega_cell_component_4m": (
        "sha256:0f297e0f2854bcdf7287a13708473b582d8a2751913d2f27fee6c84682cb8508"
    ),
    "industrial_colonies:v3_ae2/mega_cell_component_16m": (
        "sha256:28ebbc0163a14ff63fb0c3d2cc5a6c846196f585bcd3b57e8296a8488763b326"
    ),
    "industrial_colonies:v3_ae2/mega_cell_component_64m": (
        "sha256:29992e1ac90b68c26f2a27c16a9549e26b0fc3656759cb67d80b9e72056a0cb8"
    ),
    "industrial_colonies:v3_ae2/mega_cell_component_256m": (
        "sha256:e5877045be48ff351dedc230f5a63f5078270e89409192a5e780dbe68f51315c"
    ),
    "industrial_colonies:v3_ae2/mega_crafting_storage_1m": (
        "sha256:c2c3ac84c8bb667363e65866c321165739e7ef1212d76c7c98c1f56856ac782b"
    ),
    "industrial_colonies:v3_ae2/mega_crafting_storage_4m": (
        "sha256:3c67da69a101b2bbd4cee9ecc2ee040e3258df52f51465733b79d2c03736a9b1"
    ),
    "industrial_colonies:v3_ae2/mega_crafting_storage_16m": (
        "sha256:aed00f372a80f596c260cfd51f1d1632b4d24c5cc2f04c7db5c04b5050220011"
    ),
    "industrial_colonies:v3_ae2/mega_crafting_storage_64m": (
        "sha256:47c51c22ca903f7d13a5087cbb167b51895d938a31a9860337f147b9ce85e16b"
    ),
    "industrial_colonies:v3_ae2/mega_crafting_storage_256m": (
        "sha256:dd9c6e929e56a6005761330cd5c7bc1a337f5160b0e81c57c1815a6c92187ca1"
    ),
    "industrial_colonies:v3_ae2/mega_item_cell_housing": (
        "sha256:ef2aada10798b6fe6029718690e73969c9206b5c98d627373da0e1581b149481"
    ),
    "industrial_colonies:v3_ae2/mega_item_storage_cell_1m": (
        "sha256:0ec18d36fe1fdcca4a7a2ea5ecd6213c914ec7c0f5c8ab1749370266aba51e21"
    ),
    "industrial_colonies:v3_ae2/mega_item_storage_cell_4m": (
        "sha256:e0d9451fa15e0f3431740ab8c85a10cf2719cd5cd12f0056381d5492d47b4ae5"
    ),
    "industrial_colonies:v3_ae2/mega_item_storage_cell_64m": (
        "sha256:b7e9b508643ae327c0aafe1103b1cf08bbbd4e95eb8d2293be98631946417006"
    ),
    "industrial_colonies:v3_ae2/mega_item_storage_cell_256m": (
        "sha256:446db53d589328c2c5735ba29c253d444675cd705d78f2471ca1bb5becb6fa76"
    ),
}

REDESIGNED_IDS = frozenset(REVIEWED_HASHES)
COMPONENT_IDS = frozenset(
    recipe_id for recipe_id in REDESIGNED_IDS if "mega_cell_component_" in recipe_id
)
CRAFTING_IDS = frozenset(
    recipe_id for recipe_id in REDESIGNED_IDS if "mega_crafting_storage_" in recipe_id
)
ITEM_CELL_IDS = frozenset(
    recipe_id for recipe_id in REDESIGNED_IDS if "mega_item_storage_cell_" in recipe_id
)
HOUSING_ID = "industrial_colonies:v3_ae2/mega_item_cell_housing"

_PROCESS_FIELDS = {
    "type",
    "comment",
    "pattern",
    "key",
    "inputs",
    "input",
    "held",
    "machine",
    "transitional",
    "steps",
    "loops",
    "ingredients",
    "results",
    "outputs",
    "output",
    "returned_tool",
    "keep_held",
    "heat",
    "processing_time",
    "vat_mode",
    "machine_mode",
    "min_size",
    "infusion",
    "chemical",
    "fluid",
    "fluid_input",
}


def _index(data: dict[str, Any]) -> dict[str, int]:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed seed must contain a recipes list")
    result: dict[str, int] = {}
    for index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict) or not isinstance(recipe.get("id"), str):
            raise TypeError("managed recipes must be objects with string IDs")
        recipe_id = recipe["id"]
        if recipe_id in result:
            raise ValueError(f"duplicate managed recipe ID: {recipe_id}")
        result[recipe_id] = index
    return result


def _replace(data: dict[str, Any], recipe_id: str, process: Recipe) -> None:
    indexes = _index(data)
    if recipe_id not in indexes:
        raise KeyError(f"expected active MEGA storage rejection is missing: {recipe_id}")
    recipe = data["recipes"][indexes[recipe_id]]
    for field in _PROCESS_FIELDS:
        recipe.pop(field, None)
    recipe.update(deepcopy(process))


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    comment: str,
    input_item: str,
    ingredients: list[str],
    output: str,
    radiance: bool = False,
) -> Recipe:
    deployer = RADIANCE_DEPLOYER if radiance else RAILWAY_DEPLOYER
    press = RADIANCE_PRESS if radiance else RAILWAY_PRESS
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "steps": [*(_deploy(item, deployer) for item in ingredients), _press(press)],
        "loops": 1,
        "output": output,
        "exclusive_output": True,
    }


def _designs() -> dict[str, Recipe]:
    return {
        HOUSING_ID: _sequence(
            comment=(
                "Convert a standard item-cell shell into a Train-rated MEGA housing by "
                "installing a Railway casing, TFMG steel frame, transformer, magnetic "
                "shield, plastic dielectric, vibrant face, and dense fluix service bus"
            ),
            input_item="ae2:item_cell_housing",
            ingredients=[
                "create:railway_casing",
                "tfmg:steel_frame",
                "tfmg:transformer",
                "tfmg:magnetic_alloy_sheet",
                "2x tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
                "ae2:fluix_smart_dense_cable",
            ],
            output="megacells:mega_item_cell_housing",
        ),
        "industrial_colonies:v3_ae2/mega_cell_component_4m": _sequence(
            comment=(
                "Bond four 1M planes through accumulation and concurrent scheduling, a "
                "2-cubed spatial map, dense fluix bus, TFMG transformer and laminated "
                "shield, then key the first enlarged matrix with Allthemodium"
            ),
            input_item="megacells:cell_component_1m",
            ingredients=[
                "3x megacells:cell_component_1m",
                "megacells:accumulation_processor",
                "extendedae:concurrent_processor",
                "ae2:spatial_cell_component_2",
                "ae2:fluix_smart_dense_cable",
                "tfmg:transformer",
                "tfmg:laminated_magnetic_alloy_block",
                "allthemodium:allthemodium_plate",
            ],
            output="megacells:cell_component_4m",
        ),
        "industrial_colonies:v3_ae2/mega_cell_component_16m": _sequence(
            comment=(
                "Stack four 4M planes under concurrent and advanced stress control, "
                "map them through a 16-cubed address core, and brace the assembly with "
                "cobalt, TFMG power isolation, plastic dielectric, and Vibranium"
            ),
            input_item="megacells:cell_component_4m",
            ingredients=[
                "3x megacells:cell_component_4m",
                "extendedae:concurrent_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:spatial_cell_component_16",
                "modernfoundry:cobalt_reinforcement",
                "tfmg:transformer",
                "2x tfmg:plastic_sheet",
                "allthemodium:vibranium_plate",
            ],
            output="megacells:cell_component_16m",
        ),
        "industrial_colonies:v3_ae2/mega_cell_component_64m": _sequence(
            comment=(
                "Coordinate four 16M planes through redundant accumulation and quantum "
                "logic, full spatial addressing, matter isolation, TFMG magnetic and "
                "lithium containment, and an Unobtainium field bus"
            ),
            input_item="megacells:cell_component_16m",
            ingredients=[
                "3x megacells:cell_component_16m",
                "2x megacells:accumulation_processor",
                "advanced_ae:quantum_processor",
                "ae2:spatial_cell_component_128",
                "ae2:matter_ball",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:lithium_charge",
                "allthemodium:unobtainium_plate",
            ],
            output="megacells:cell_component_64m",
        ),
        "industrial_colonies:v3_ae2/mega_cell_component_256m": _sequence(
            comment=(
                "Finish the 256M matrix from four 64M planes with redundant accumulation "
                "and quantum control, doubled spatial and matter isolation, ultimate "
                "supervision, TFMG shielding, exotic alloy contacts, and Radiance casing"
            ),
            input_item="megacells:cell_component_64m",
            ingredients=[
                "3x megacells:cell_component_64m",
                "2x megacells:accumulation_processor",
                "advanced_ae:quantum_processor",
                "2x ae2:spatial_cell_component_128",
                "2x ae2:matter_ball",
                "mekanism:ultimate_control_circuit",
                "tfmg:laminated_magnetic_alloy_block",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
                "create:refined_radiance_casing",
            ],
            output="megacells:cell_component_256m",
            radiance=True,
        ),
        "industrial_colonies:v3_ae2/mega_crafting_storage_1m": _sequence(
            comment=(
                "Populate the MEGA crafting chassis with its 1M plane, accumulation and "
                "concurrent scheduling, a dense fluix backplane, TFMG isolated power and "
                "capacitor bank, plastic dielectric, and vibrant service face"
            ),
            input_item="megacells:mega_crafting_unit",
            ingredients=[
                "megacells:cell_component_1m",
                "megacells:accumulation_processor",
                "extendedae:concurrent_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:transformer",
                "2x tfmg:capacitor_item",
                "tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            output="megacells:1m_crafting_storage",
        ),
        "industrial_colonies:v3_ae2/mega_crafting_storage_4m": _sequence(
            comment=(
                "Upgrade the 1M crafting block with a 4M plane, concurrent and engineering "
                "logic, dense fluix service, TFMG magnetic and lithium buffering, a "
                "vibrant face, and an Allthemodium scheduling bus"
            ),
            input_item="megacells:1m_crafting_storage",
            ingredients=[
                "megacells:cell_component_4m",
                "extendedae:concurrent_processor",
                "ae2:engineering_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:lithium_charge",
                "ae2:quartz_vibrant_glass",
                "allthemodium:allthemodium_plate",
            ],
            output="megacells:4m_crafting_storage",
        ),
        "industrial_colonies:v3_ae2/mega_crafting_storage_16m": _sequence(
            comment=(
                "Upgrade the 4M scheduler with a 16M plane, concurrent and advanced "
                "stress control, 16-cubed addressing, TFMG transformer and capacitor "
                "bank, plastic isolation, and a Vibranium scheduling bus"
            ),
            input_item="megacells:4m_crafting_storage",
            ingredients=[
                "megacells:cell_component_16m",
                "extendedae:concurrent_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:spatial_cell_component_16",
                "tfmg:transformer",
                "2x tfmg:capacitor_item",
                "2x tfmg:plastic_sheet",
                "allthemodium:vibranium_plate",
            ],
            output="megacells:16m_crafting_storage",
        ),
        "industrial_colonies:v3_ae2/mega_crafting_storage_64m": _sequence(
            comment=(
                "Upgrade the 16M scheduler with a 64M plane, quantum control, full "
                "spatial mapping, matter isolation, a dense fluix backplane, TFMG "
                "magnetic and transformer containment, and an Unobtainium bus"
            ),
            input_item="megacells:16m_crafting_storage",
            ingredients=[
                "megacells:cell_component_64m",
                "advanced_ae:quantum_processor",
                "ae2:spatial_cell_component_128",
                "ae2:matter_ball",
                "ae2:fluix_smart_dense_cable",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:transformer",
                "allthemodium:unobtainium_plate",
            ],
            output="megacells:64m_crafting_storage",
        ),
        "industrial_colonies:v3_ae2/mega_crafting_storage_256m": _sequence(
            comment=(
                "Finish the crafting array by adding a 256M plane, quantum and ultimate "
                "scheduling, doubled spatial and matter isolation, dense fluix service, "
                "TFMG isolated power, exotic alloy contacts, and a Radiance enclosure"
            ),
            input_item="megacells:64m_crafting_storage",
            ingredients=[
                "megacells:cell_component_256m",
                "advanced_ae:quantum_processor",
                "mekanism:ultimate_control_circuit",
                "2x ae2:spatial_cell_component_128",
                "2x ae2:matter_ball",
                "ae2:fluix_smart_dense_cable",
                "tfmg:transformer",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
                "create:refined_radiance_casing",
            ],
            output="megacells:256m_crafting_storage",
            radiance=True,
        ),
        "industrial_colonies:v3_ae2/mega_item_storage_cell_1m": _sequence(
            comment=(
                "Populate the MEGA item housing with its 1M plane, accumulation control, "
                "a complementary TFMG semiconductor junction, plastic dielectric, lithium "
                "buffering, magnetic shield, capacitor, and dense fluix item bus"
            ),
            input_item="megacells:mega_item_cell_housing",
            ingredients=[
                "megacells:cell_component_1m",
                "megacells:accumulation_processor",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:plastic_sheet",
                "tfmg:lithium_charge",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:capacitor_item",
                "ae2:fluix_smart_dense_cable",
            ],
            output="megacells:item_storage_cell_1m",
        ),
        "industrial_colonies:v3_ae2/mega_item_storage_cell_4m": _sequence(
            comment=(
                "Upgrade the 1M item cell with its 4M plane, concurrent indexing, dense "
                "fluix service, TFMG lithium and laminated shielding, plastic isolation, "
                "a capacitor bank, and an Allthemodium item bus"
            ),
            input_item="megacells:item_storage_cell_1m",
            ingredients=[
                "megacells:cell_component_4m",
                "extendedae:concurrent_processor",
                "ae2:fluix_smart_dense_cable",
                "2x tfmg:lithium_charge",
                "tfmg:laminated_magnetic_alloy_block",
                "2x tfmg:plastic_sheet",
                "2x tfmg:capacitor_item",
                "allthemodium:allthemodium_plate",
            ],
            output="megacells:item_storage_cell_4m",
        ),
        "industrial_colonies:v3_ae2/mega_item_storage_cell_64m": _sequence(
            comment=(
                "Upgrade the existing 16M item cell with its 64M plane, quantum indexing, "
                "full spatial service, TFMG lithium and magnetic containment, dense fluix "
                "routing, matter isolation, and an Unobtainium item bus"
            ),
            input_item="megacells:item_storage_cell_16m",
            ingredients=[
                "megacells:cell_component_64m",
                "advanced_ae:quantum_processor",
                "ae2:spatial_cell_component_128",
                "3x tfmg:lithium_charge",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:fluix_smart_dense_cable",
                "ae2:matter_ball",
                "allthemodium:unobtainium_plate",
            ],
            output="megacells:item_storage_cell_64m",
        ),
        "industrial_colonies:v3_ae2/mega_item_storage_cell_256m": _sequence(
            comment=(
                "Finish the item-cell ladder by upgrading the 64M cell with a 256M plane, "
                "quantum and ultimate indexing, TFMG lithium and magnetic containment, "
                "dense fluix service, exotic alloy contacts, and a Radiance enclosure"
            ),
            input_item="megacells:item_storage_cell_64m",
            ingredients=[
                "megacells:cell_component_256m",
                "advanced_ae:quantum_processor",
                "mekanism:ultimate_control_circuit",
                "4x tfmg:lithium_charge",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:fluix_smart_dense_cable",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
                "create:refined_radiance_casing",
            ],
            output="megacells:item_storage_cell_256m",
            radiance=True,
        ),
    }


def apply(data: dict[str, Any]) -> None:
    designs = _designs()
    if set(designs) != set(REDESIGNED_IDS):
        raise ValueError("MEGA storage design table no longer matches rejected cohort")
    indexes = _index(data)
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        raise KeyError(f"expected active MEGA storage rejections are missing: {missing}")
    for recipe_id, process in designs.items():
        _replace(data, recipe_id, process)
    audit(data)


def _ingredients(recipe: Recipe) -> list[str]:
    return [
        step["ingredient"]
        for step in recipe.get("steps", [])
        if isinstance(step, dict) and step.get("op") == "deploying"
    ]


def _machines(recipe: Recipe) -> set[str]:
    return {
        step["machine"]
        for step in recipe.get("steps", [])
        if isinstance(step, dict) and isinstance(step.get("machine"), str)
    }


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    recipes = data.get("recipes", [])
    errors: list[str] = []
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        errors.append(f"missing MEGA storage redesigns: {missing}")

    radiance_ids = {
        "industrial_colonies:v3_ae2/mega_cell_component_256m",
        "industrial_colonies:v3_ae2/mega_crafting_storage_256m",
        "industrial_colonies:v3_ae2/mega_item_storage_cell_256m",
    }
    fingerprints: set[frozenset[str]] = set()
    for recipe_id in sorted(REDESIGNED_IDS.intersection(indexes)):
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not Sequenced Assembly")
            continue
        steps = recipe.get("steps", [])
        if not 8 <= len(steps) <= 10:
            errors.append(f"{recipe_id} has unsupported sequence depth {len(steps)}")
        expected = (
            {RADIANCE_DEPLOYER, RADIANCE_PRESS}
            if recipe_id in radiance_ids
            else {RAILWAY_DEPLOYER, RAILWAY_PRESS}
        )
        if _machines(recipe) != expected:
            errors.append(f"{recipe_id} escaped its reviewed high-tier machine family")
        expected_press = RADIANCE_PRESS if recipe_id in radiance_ids else RAILWAY_PRESS
        if not steps or steps[-1] != _press(expected_press):
            errors.append(f"{recipe_id} does not finish with its tier press")
        parts = _ingredients(recipe)
        if not any("tfmg:" in part for part in parts):
            errors.append(f"{recipe_id} lacks functional TFMG electronics/containment")
        fingerprint = frozenset(parts)
        if fingerprint in fingerprints:
            errors.append(f"{recipe_id} duplicates another MEGA tier BOM")
        fingerprints.add(fingerprint)

    component_ladder = {
        "4m": "1m",
        "16m": "4m",
        "64m": "16m",
        "256m": "64m",
    }
    for tier, prior in component_ladder.items():
        recipe_id = f"industrial_colonies:v3_ae2/mega_cell_component_{tier}"
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        prior_item = f"megacells:cell_component_{prior}"
        if recipe.get("input") != prior_item:
            errors.append(f"{recipe_id} no longer uses the prior component as its base")
        if f"3x {prior_item}" not in _ingredients(recipe):
            errors.append(f"{recipe_id} no longer bonds four prior-tier planes")

    crafting_ladder = {
        "1m": "megacells:mega_crafting_unit",
        "4m": "megacells:1m_crafting_storage",
        "16m": "megacells:4m_crafting_storage",
        "64m": "megacells:16m_crafting_storage",
        "256m": "megacells:64m_crafting_storage",
    }
    for tier, base in crafting_ladder.items():
        recipe_id = f"industrial_colonies:v3_ae2/mega_crafting_storage_{tier}"
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("input") != base:
            errors.append(f"{recipe_id} no longer compounds its prior crafting tier")
        if f"megacells:cell_component_{tier}" not in _ingredients(recipe):
            errors.append(f"{recipe_id} lacks its matching MEGA memory plane")

    item_cell_ladder = {
        "1m": "megacells:mega_item_cell_housing",
        "4m": "megacells:item_storage_cell_1m",
        "64m": "megacells:item_storage_cell_16m",
        "256m": "megacells:item_storage_cell_64m",
    }
    for tier, base in item_cell_ladder.items():
        recipe_id = f"industrial_colonies:v3_ae2/mega_item_storage_cell_{tier}"
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("input") != base:
            errors.append(f"{recipe_id} no longer compounds its prior available item cell")
        if f"megacells:cell_component_{tier}" not in _ingredients(recipe):
            errors.append(f"{recipe_id} lacks its matching MEGA memory plane")

    exotic_by_tier = {
        "4m": "allthemodium:allthemodium_plate",
        "16m": "allthemodium:vibranium_plate",
        "64m": "allthemodium:unobtainium_plate",
        "256m": "allthemodium:unobtainium_vibranium_alloy_ingot",
    }
    for tier, exotic in exotic_by_tier.items():
        selected = [
            recipe_id
            for recipe_id in REDESIGNED_IDS
            if recipe_id.endswith("_" + tier)
        ]
        for recipe_id in selected:
            if recipe_id in indexes and exotic not in _ingredients(recipes[indexes[recipe_id]]):
                errors.append(f"{recipe_id} lacks staged conductor {exotic}")

    for recipe_id in sorted(REDESIGNED_IDS):
        if recipe_id.endswith(("_64m", "_256m")) and recipe_id in indexes:
            if "advanced_ae:quantum_processor" not in _ingredients(recipes[indexes[recipe_id]]):
                errors.append(f"{recipe_id} lacks quantum control")

    if errors:
        raise ValueError("MEGA storage rejection audit failed: " + " | ".join(errors))
    return {
        "status": "PASS",
        "redesigned": len(REDESIGNED_IDS),
        "components": len(COMPONENT_IDS),
        "crafting_storage": len(CRAFTING_IDS),
        "item_cells": len(ITEM_CELL_IDS),
        "housings": 1,
        "railway_line": len(REDESIGNED_IDS) - len(radiance_ids),
        "radiance_line": len(radiance_ids),
    }
