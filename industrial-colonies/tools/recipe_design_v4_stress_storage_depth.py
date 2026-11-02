#!/usr/bin/env python3
"""Deepen the explicitly rejected Applied Create stress-storage ladder.

This cohort contains only exact active second-pass rejections whose immutable
note is ``Too cheap — make it more complex.``  It deliberately leaves the
approved 1k design, the unselected 16k/64k/256k cells, and the post-nuclear
256m endpoint untouched.  Complexity comes from a cumulative memory ladder,
recognizable kinetic instrumentation, tier-specific processors, TFMG field
hardware, and staged exotic conductors rather than loops or generic shells.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"

REJECTION_NOTE = "Too cheap — make it more complex."

REVIEWED_HASHES = {
    "industrial_colonies:appliedcreate/stress_storage_cell_4k": (
        "sha256:854fd4e9011b3462a48f0a6ce3b175787e930147c90b752facd6d343224ebf22"
    ),
    "industrial_colonies:appliedcreate/stress_storage_cell_1m": (
        "sha256:48c578980b3fb2da8bf698842e8e0c7c28484ba37126840371ca7040c0fb9b6a"
    ),
    "industrial_colonies:appliedcreate/stress_storage_cell_4m": (
        "sha256:5e56e0bd1b7e90fe859fac00b673a4666ea32bf73e81eece3abdff5e36089f72"
    ),
    "industrial_colonies:appliedcreate/stress_storage_cell_16m": (
        "sha256:0df6b5b26a4edc730e0f71ce57e56ae897b9c4e2451a2597b7a251fad290237a"
    ),
    "industrial_colonies:appliedcreate/stress_storage_cell_64m": (
        "sha256:645723853bfc5e4a442d5825e7b2b55267d9abb2b12012bf758b8e5b0ae7d2d2"
    ),
    "industrial_colonies:appliedcreate/stress_storage_component_4k": (
        "sha256:0320b9b0cda4325bcef86596e21912f0e370fb46f3da50c4344f5a8b78f964d3"
    ),
    "industrial_colonies:appliedcreate/stress_storage_component_16k": (
        "sha256:d447d625d85bc280e02796977636e96482b83e4f35ca3a882e2df1afda027c32"
    ),
    "industrial_colonies:appliedcreate/stress_storage_component_64k": (
        "sha256:6ac8d51bd1a7464178163d87f230f0f9761b4af8d115e10256d9252b7a1094dc"
    ),
    "industrial_colonies:appliedcreate/stress_storage_component_256k": (
        "sha256:f0f0752d5ea9de64d70ebd1e8910ed3234540bfe4166999a2e2450b6aaa64506"
    ),
    "industrial_colonies:appliedcreate/stress_storage_component_1m": (
        "sha256:2fa916cbcd7a850eeacdcd9579ceb321a700447781aadf57502da1b95372b763"
    ),
    "industrial_colonies:appliedcreate/stress_storage_component_4m": (
        "sha256:75b9132331a5d5b95f1ea28e11371021bc51c9c5870e2ddb39fc8d860a1fd3d2"
    ),
    "industrial_colonies:appliedcreate/stress_storage_component_16m": (
        "sha256:99bff3592e065aa4578236d68293f24cbccdcbe2fa3089b1058011e64ff22fbe"
    ),
    "industrial_colonies:appliedcreate/stress_storage_component_64m": (
        "sha256:8b55f3ef6f8a91e736fffda9fac65622f3b1351913c17725ef3b4531ec2ded50"
    ),
}

REDESIGNED_IDS = frozenset(REVIEWED_HASHES)

COMPONENT_IDS = frozenset(
    recipe_id for recipe_id in REDESIGNED_IDS if "stress_storage_component_" in recipe_id
)
CELL_IDS = REDESIGNED_IDS - COMPONENT_IDS

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
        raise KeyError(f"expected active Too-cheap rejection is missing: {recipe_id}")
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
    transitional: str,
    ingredients: list[str],
    output: str,
    deployer: str,
    press: str,
    depends_on: list[str] | None = None,
) -> Recipe:
    recipe: Recipe = {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional,
        "steps": [*(_deploy(item, deployer) for item in ingredients), _press(press)],
        "loops": 1,
        "output": output,
        "exclusive_output": True,
    }
    if depends_on is not None:
        recipe["depends_on"] = depends_on
    return recipe


def _designs() -> dict[str, Recipe]:
    unfinished = "industrial_colonies:unfinished_stress_storage_component"
    return {
        "industrial_colonies:appliedcreate/stress_storage_component_4k": _sequence(
            comment=(
                "Expand the approved 1k stress matrix with a real 4k memory plane, "
                "stress feedback, wound TFMG copper buffering, paired capacitors, and "
                "a vibrant quartz service face"
            ),
            input_item="appliedcreate:stress_storage_component_1k",
            transitional=unfinished,
            ingredients=[
                "ae2:cell_component_4k",
                "appliedcreate:stress_processor",
                "create:stressometer",
                "tfmg:copper_spool",
                "2x tfmg:capacitor_item",
                "ae2:quartz_vibrant_glass",
            ],
            output="appliedcreate:stress_storage_component_4k",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_component_16k": _sequence(
            comment=(
                "Index a 16k memory plane through a precision geartrain and logic "
                "processor, then shield its stress controller with TFMG magnetic alloy, "
                "plastic dielectric, and vibrant quartz"
            ),
            input_item="appliedcreate:stress_storage_component_4k",
            transitional=unfinished,
            ingredients=[
                "ae2:cell_component_16k",
                "appliedcreate:stress_processor",
                "create:precision_mechanism",
                "ae2:logic_processor",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            output="appliedcreate:stress_storage_component_16k",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_component_64k": _sequence(
            comment=(
                "Move the 64k matrix onto the Railway electronics line with advanced "
                "stress control, calculation logic, governed rotation, capacitor banks, "
                "laminated magnetic shielding, and a TFMG lithium reserve"
            ),
            input_item="appliedcreate:stress_storage_component_16k",
            transitional=unfinished,
            ingredients=[
                "ae2:cell_component_64k",
                "appliedcreate:advanced_stress_processor",
                "ae2:calculation_processor",
                "create:rotation_speed_controller",
                "2x tfmg:capacitor_item",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:lithium_charge",
            ],
            output="appliedcreate:stress_storage_component_64k",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_component_256k": _sequence(
            comment=(
                "Address the 256k plane with accumulation logic, an advanced stress "
                "controller, a kinetic bridge and governor, then isolate the larger "
                "matrix behind laminated shielding, lithium backup, and vibrant quartz"
            ),
            input_item="appliedcreate:stress_storage_component_64k",
            transitional=unfinished,
            ingredients=[
                "ae2:cell_component_256k",
                "appliedcreate:advanced_stress_processor",
                "megacells:accumulation_processor",
                "create_connected:kinetic_bridge",
                "create:rotation_speed_controller",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:lithium_charge",
                "ae2:quartz_vibrant_glass",
            ],
            output="appliedcreate:stress_storage_component_256k",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_component_1m": _sequence(
            comment=(
                "Couple the first MEGA memory plane to advanced stress and accumulation "
                "logic, a kinetic bridge, 2-cubed spatial addressing, isolated TFMG "
                "power, magnetic containment, and lithium ride-through"
            ),
            input_item="appliedcreate:stress_storage_component_256k",
            transitional=unfinished,
            ingredients=[
                "megacells:cell_component_1m",
                "appliedcreate:advanced_stress_processor",
                "megacells:accumulation_processor",
                "create_connected:kinetic_bridge",
                "ae2:spatial_cell_component_2",
                "tfmg:transformer",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:lithium_charge",
            ],
            output="appliedcreate:stress_storage_component_1m",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_component_4m": _sequence(
            comment=(
                "Bind the 4M MEGA plane to advanced stress and accumulation control, "
                "spatial addressing, kinetic acceptance, matter isolation, Refined "
                "Radiance contacts, and an Allthemodium conductor plate"
            ),
            input_item="appliedcreate:stress_storage_component_1m",
            transitional=unfinished,
            ingredients=[
                "megacells:cell_component_4m",
                "appliedcreate:advanced_stress_processor",
                "megacells:accumulation_processor",
                "ae2:spatial_cell_component_2",
                "appliedcreate:kinetic_energy_acceptor",
                "ae2:matter_ball",
                "create:refined_radiance",
                "tfmg:laminated_magnetic_alloy_block",
                "allthemodium:allthemodium_plate",
            ],
            output="appliedcreate:stress_storage_component_4m",
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_component_16m": _sequence(
            comment=(
                "Schedule the 16M MEGA plane through concurrent stress control and a "
                "16-cubed spatial map, then couple the kinetic acceptor through a "
                "Vibranium field plate and doubled Radiance contacts"
            ),
            input_item="appliedcreate:stress_storage_component_4m",
            transitional=unfinished,
            ingredients=[
                "megacells:cell_component_16m",
                "appliedcreate:advanced_stress_processor",
                "extendedae:concurrent_processor",
                "ae2:spatial_cell_component_16",
                "appliedcreate:kinetic_energy_acceptor",
                "tfmg:transformer",
                "allthemodium:vibranium_plate",
                "2x create:refined_radiance",
            ],
            output="appliedcreate:stress_storage_component_16m",
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_component_64m": _sequence(
            comment=(
                "Coordinate the 64M MEGA plane with quantum stress logic and full-scale "
                "spatial addressing, then route its kinetic acceptor through a dense "
                "fluix bus, Unobtainium field plate, and Radiance enclosure"
            ),
            input_item="appliedcreate:stress_storage_component_16m",
            transitional=unfinished,
            ingredients=[
                "megacells:cell_component_64m",
                "appliedcreate:advanced_stress_processor",
                "advanced_ae:quantum_processor",
                "ae2:spatial_cell_component_128",
                "appliedcreate:kinetic_energy_acceptor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:laminated_magnetic_alloy_block",
                "allthemodium:unobtainium_plate",
                "create:refined_radiance_casing",
            ],
            output="appliedcreate:stress_storage_component_64m",
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            depends_on=[
                "industrial_colonies:appliedcreate/stress_storage_component_16m",
                "industrial_colonies:v3_ae2/mega_cell_component_64m",
                "industrial_colonies:v3_ae2/quantum_processor",
            ],
        ),
        "industrial_colonies:appliedcreate/stress_storage_cell_4k": _sequence(
            comment=(
                "Instrument the 4k matrix inside its Andesite housing with a cogged "
                "precision load path, dedicated stress processor and meter, TFMG copper "
                "winding, and rubber vibration isolation"
            ),
            input_item="appliedcreate:andesite_stress_cell_housing",
            transitional="appliedcreate:andesite_stress_cell_housing",
            ingredients=[
                "appliedcreate:stress_storage_component_4k",
                "create:cogwheel",
                "create:precision_mechanism",
                "appliedcreate:stress_processor",
                "create:stressometer",
                "tfmg:copper_spool",
                "tfmg:rubber_sheet",
            ],
            output="appliedcreate:stress_storage_cell_4k",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_cell_1m": _sequence(
            comment=(
                "Install the 1M stress matrix in its Brass housing with a kinetic bridge "
                "and acceptor, advanced stress control, governed rotation, TFMG magnetic "
                "bracing, lithium ride-through, and a vibrant service face"
            ),
            input_item="appliedcreate:brass_stress_cell_housing",
            transitional="appliedcreate:brass_stress_cell_housing",
            ingredients=[
                "appliedcreate:stress_storage_component_1m",
                "create_connected:kinetic_bridge",
                "appliedcreate:kinetic_energy_acceptor",
                "appliedcreate:advanced_stress_processor",
                "create:rotation_speed_controller",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:lithium_charge",
                "ae2:quartz_vibrant_glass",
            ],
            output="appliedcreate:stress_storage_cell_1m",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_cell_4m": _sequence(
            comment=(
                "Close the 4M matrix into its Brass housing around a bridged kinetic "
                "acceptor and governor, then add advanced stress logic, a Radiance shell, "
                "Allthemodium load plate, and TFMG plastic isolation"
            ),
            input_item="appliedcreate:brass_stress_cell_housing",
            transitional="appliedcreate:brass_stress_cell_housing",
            ingredients=[
                "appliedcreate:stress_storage_component_4m",
                "create_connected:kinetic_bridge",
                "appliedcreate:kinetic_energy_acceptor",
                "appliedcreate:advanced_stress_processor",
                "create:rotation_speed_controller",
                "create:refined_radiance_casing",
                "allthemodium:allthemodium_plate",
                "tfmg:plastic_sheet",
            ],
            output="appliedcreate:stress_storage_cell_4m",
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_cell_16m": _sequence(
            comment=(
                "Enclose the 16M matrix around a bridged kinetic acceptor and governor, "
                "then stabilize advanced stress control with a Radiance shell, Vibranium "
                "load plate, and matter-isolation layer"
            ),
            input_item="appliedcreate:brass_stress_cell_housing",
            transitional="appliedcreate:brass_stress_cell_housing",
            ingredients=[
                "appliedcreate:stress_storage_component_16m",
                "create_connected:kinetic_bridge",
                "appliedcreate:kinetic_energy_acceptor",
                "appliedcreate:advanced_stress_processor",
                "create:rotation_speed_controller",
                "create:refined_radiance_casing",
                "tfmg:laminated_magnetic_alloy_block",
                "allthemodium:vibranium_plate",
                "ae2:matter_ball",
            ],
            output="appliedcreate:stress_storage_cell_16m",
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
        ),
        "industrial_colonies:appliedcreate/stress_storage_cell_64m": _sequence(
            comment=(
                "Finish the 64M enclosure with a bridged kinetic acceptor and governor, "
                "advanced stress control, Radiance shell, dense fluix service bus, "
                "TFMG power isolation, and an Unobtainium load plate"
            ),
            input_item="appliedcreate:brass_stress_cell_housing",
            transitional="appliedcreate:brass_stress_cell_housing",
            ingredients=[
                "appliedcreate:stress_storage_component_64m",
                "create_connected:kinetic_bridge",
                "appliedcreate:kinetic_energy_acceptor",
                "appliedcreate:advanced_stress_processor",
                "create:rotation_speed_controller",
                "create:refined_radiance_casing",
                "ae2:fluix_smart_dense_cable",
                "tfmg:transformer",
                "allthemodium:unobtainium_plate",
            ],
            output="appliedcreate:stress_storage_cell_64m",
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
        ),
    }


def apply(data: dict[str, Any]) -> None:
    designs = _designs()
    if set(designs) != set(REDESIGNED_IDS):
        raise ValueError("stress-storage design table no longer matches rejected cohort")
    indexes = _index(data)
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        raise KeyError(f"expected active Too-cheap rejections are missing: {missing}")
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
        errors.append(f"missing stress-storage redesigns: {missing}")

    brass_ids = {
        "industrial_colonies:appliedcreate/stress_storage_component_4k",
        "industrial_colonies:appliedcreate/stress_storage_component_16k",
        "industrial_colonies:appliedcreate/stress_storage_cell_4k",
    }
    railway_ids = {
        "industrial_colonies:appliedcreate/stress_storage_component_64k",
        "industrial_colonies:appliedcreate/stress_storage_component_256k",
        "industrial_colonies:appliedcreate/stress_storage_component_1m",
        "industrial_colonies:appliedcreate/stress_storage_cell_1m",
    }
    radiance_ids = set(REDESIGNED_IDS) - brass_ids - railway_ids
    family_machines = {
        **{recipe_id: {BRASS_DEPLOYER, BRASS_PRESS} for recipe_id in brass_ids},
        **{recipe_id: {RAILWAY_DEPLOYER, RAILWAY_PRESS} for recipe_id in railway_ids},
        **{recipe_id: {RADIANCE_DEPLOYER, RADIANCE_PRESS} for recipe_id in radiance_ids},
    }
    bom_fingerprints: set[frozenset[str]] = set()
    for recipe_id in sorted(REDESIGNED_IDS.intersection(indexes)):
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not Sequenced Assembly")
            continue
        steps = recipe.get("steps", [])
        if not 7 <= len(steps) <= 10:
            errors.append(f"{recipe_id} has unsupported sequence depth {len(steps)}")
        expected_machines = family_machines[recipe_id]
        if _machines(recipe) != expected_machines:
            errors.append(f"{recipe_id} escaped its tier manufacturing family")
        expected_press = next(machine for machine in expected_machines if machine.endswith("_press"))
        if not steps or steps[-1] != _press(expected_press):
            errors.append(f"{recipe_id} does not finish with its tier press")
        parts = _ingredients(recipe)
        if not any("tfmg:" in part for part in parts):
            errors.append(f"{recipe_id} lacks a functional TFMG part")
        fingerprint = frozenset(parts)
        if fingerprint in bom_fingerprints:
            errors.append(f"{recipe_id} duplicates another tier BOM")
        bom_fingerprints.add(fingerprint)

    component_ladder = {
        "4k": ("appliedcreate:stress_storage_component_1k", "ae2:cell_component_4k"),
        "16k": ("appliedcreate:stress_storage_component_4k", "ae2:cell_component_16k"),
        "64k": ("appliedcreate:stress_storage_component_16k", "ae2:cell_component_64k"),
        "256k": ("appliedcreate:stress_storage_component_64k", "ae2:cell_component_256k"),
        "1m": ("appliedcreate:stress_storage_component_256k", "megacells:cell_component_1m"),
        "4m": ("appliedcreate:stress_storage_component_1m", "megacells:cell_component_4m"),
        "16m": ("appliedcreate:stress_storage_component_4m", "megacells:cell_component_16m"),
        "64m": ("appliedcreate:stress_storage_component_16m", "megacells:cell_component_64m"),
    }
    for tier, (prior, memory_plane) in component_ladder.items():
        recipe_id = f"industrial_colonies:appliedcreate/stress_storage_component_{tier}"
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("input") != prior:
            errors.append(f"{recipe_id} no longer compounds the prior tier")
        if memory_plane not in _ingredients(recipe):
            errors.append(f"{recipe_id} lacks its {tier} memory plane")

    cell_housings = {
        "4k": "appliedcreate:andesite_stress_cell_housing",
        "1m": "appliedcreate:brass_stress_cell_housing",
        "4m": "appliedcreate:brass_stress_cell_housing",
        "16m": "appliedcreate:brass_stress_cell_housing",
        "64m": "appliedcreate:brass_stress_cell_housing",
    }
    for tier, housing in cell_housings.items():
        recipe_id = f"industrial_colonies:appliedcreate/stress_storage_cell_{tier}"
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        parts = _ingredients(recipe)
        if recipe.get("input") != housing:
            errors.append(f"{recipe_id} lost its tier housing")
        if f"appliedcreate:stress_storage_component_{tier}" not in parts:
            errors.append(f"{recipe_id} lacks its matching stress matrix")
        for kinetic_part in (
            "appliedcreate:kinetic_energy_acceptor",
            "appliedcreate:advanced_stress_processor",
        ):
            if tier != "4k" and kinetic_part not in parts:
                errors.append(f"{recipe_id} lacks high-tier kinetic part {kinetic_part}")

    exotic_by_tier = {
        "4m": "allthemodium:allthemodium_plate",
        "16m": "allthemodium:vibranium_plate",
        "64m": "allthemodium:unobtainium_plate",
    }
    for tier, exotic in exotic_by_tier.items():
        for stem in ("component", "cell"):
            recipe_id = f"industrial_colonies:appliedcreate/stress_storage_{stem}_{tier}"
            if recipe_id in indexes and exotic not in _ingredients(recipes[indexes[recipe_id]]):
                errors.append(f"{recipe_id} lacks its staged exotic conductor {exotic}")

    processor_by_tier = {
        "4m": "megacells:accumulation_processor",
        "16m": "extendedae:concurrent_processor",
        "64m": "advanced_ae:quantum_processor",
    }
    for tier, processor in processor_by_tier.items():
        recipe_id = f"industrial_colonies:appliedcreate/stress_storage_component_{tier}"
        if recipe_id in indexes and processor not in _ingredients(recipes[indexes[recipe_id]]):
            errors.append(f"{recipe_id} lacks its tier processor {processor}")

    if errors:
        raise ValueError("Stress-storage rejection audit failed: " + " | ".join(errors))
    return {
        "status": "PASS",
        "redesigned": len(REDESIGNED_IDS),
        "components": len(COMPONENT_IDS),
        "cells": len(CELL_IDS),
        "brass_line": len(brass_ids),
        "railway_line": len(railway_ids),
        "radiance_line": len(radiance_ids),
    }
