#!/usr/bin/env python3
"""Deepen the explicitly rejected AE2 electronics assemblies.

The second review pass marked these fifteen cards "Needs more electronics".
This transform keeps each item's physical core and its established machine tier,
then adds a distinct serviceable backplane, dielectric, semiconductor stage, and
control package.  It does not surround blocks with generic expensive trim.
"""

from __future__ import annotations

from typing import Any


Recipe = dict[str, Any]


SPECS: dict[str, dict[str, Any]] = {
    "industrial_colonies:ae2_coverage/crafting_monitor": {
        "machine": "brass",
        "ingredients": (
            "ae2:storage_monitor",
            "create:display_board",
            "ae2:calculation_processor",
            "tfmg:coated_circuit_board",
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:transistor_item",
            "ae2:quartz_vibrant_glass",
        ),
        "comment": (
            "Instrument the crafting-unit chassis with a real display, calculation "
            "controller, coated backplane, plastic dielectric, transistor switch, "
            "semiconductor driver, and protected service window."
        ),
    },
    "industrial_colonies:ae2_coverage/wireless_access_point": {
        "machine": "brass",
        "ingredients": (
            "tfmg:large_coil",
            "ae2:fluix_smart_cable",
            "ae2:calculation_processor",
            "tfmg:coated_circuit_board",
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:capacitor_item",
            "tfmg:copper_wire",
        ),
        "comment": (
            "Build the wireless station as an antenna coil over a fluix backbone, "
            "with calculation control, complementary RF stages, local capacitance, "
            "a coated routing board, and insulated copper feed."
        ),
    },
    "industrial_colonies:digital_core/molecular_assembler": {
        "machine": "brass",
        "ingredients": (
            "2x ae2:quartz_glass",
            "ae2:annihilation_core",
            "ae2:formation_core",
            "create:precision_mechanism",
            "ae2:calculation_processor",
            "tfmg:coated_circuit_board",
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
        ),
        "comment": (
            "Enclose a real crafting bed between matter-transfer cores and quartz "
            "walls, then install a precision drive, calculation controller, coated "
            "backplane, dielectric liner, and complementary switching pair."
        ),
    },
    "industrial_colonies:digital_storage/ae2_crafting_storage_256k": {
        "machine": "weathered_iron",
        "ingredients": (
            "ae2:cell_component_256k",
            "megacells:accumulation_processor",
            "ae2:spatial_cell_component_128",
            "ae2:matter_ball",
            "tfmg:coated_circuit_board",
            "2x tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:lithium_block",
            "ae2:quartz_vibrant_glass",
        ),
        "comment": (
            "Finish the 256k crafting store around its memory and spatial planes, "
            "adding accumulation control, a coated address backplane, complementary "
            "drivers, plastic isolation, bulk lithium buffering, and a vibrant face."
        ),
    },
    "industrial_colonies:extendedae_coverage/concurrent_processor": {
        "machine": "brass",
        "ingredients": (
            "ae2:printed_silicon",
            "tfmg:coated_circuit_board",
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "2x tfmg:transistor_item",
            "2x tfmg:capacitor_item",
            "appliedcreate:advanced_stress_processor",
            "ae2:fluix_dust",
        ),
        "comment": (
            "Package the concurrent print over a coated board with silicon timing, "
            "complementary logic, paired switching and buffering stages, dielectric "
            "encapsulation, stress scheduling, and a fluix clock path."
        ),
    },
    "industrial_colonies:v3_ae2/cell_component_256k": {
        "machine": "railway",
        "ingredients": (
            "3x ae2:cell_component_64k",
            "megacells:accumulation_processor",
            "ae2:spatial_cell_component_2",
            "ae2:matter_ball",
            "tfmg:coated_circuit_board",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "2x tfmg:plastic_sheet",
            "tfmg:lithium_block",
            "tfmg:laminated_magnetic_alloy_block",
            "ae2:quartz_vibrant_glass",
        ),
        "comment": (
            "Combine four 64k planes behind accumulation and spatial addressing, "
            "then add a coated backplane, complementary drivers, matter isolation, "
            "bulk lithium, laminated shielding, and a vibrant inspection face."
        ),
    },
    "industrial_colonies:v3_ae2/condenser": {
        "machine": "weathered_iron",
        "ingredients": (
            "ae2:annihilation_core",
            "ae2:formation_core",
            "ae2:engineering_processor",
            "ae2:energy_acceptor",
            "tfmg:coated_circuit_board",
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "2x tfmg:capacitor_item",
            "ae2:quartz_vibrant_glass",
        ),
        "comment": (
            "Instrument the pressure tank with opposed matter cores, engineering "
            "control and power entry, then add a coated control board, complementary "
            "valve drivers, dielectric lining, capacitor bank, and observation face."
        ),
    },
    "industrial_colonies:v3_ae2/controller": {
        "machine": "weathered_iron",
        "ingredients": (
            "ae2:smooth_sky_stone_block",
            "ae2:engineering_processor",
            "tfmg:transformer",
            "ae2:fluix_smart_dense_cable",
            "tfmg:steel_frame",
            "tfmg:coated_circuit_board",
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:magnetic_alloy_sheet",
        ),
        "comment": (
            "Turn the Energy Acceptor into a framed network controller with sky-stone "
            "shielding, dense fluix routing, transformed power, engineering logic, a "
            "coated backplane, complementary drivers, and insulated magnetic closure."
        ),
    },
    "industrial_colonies:v3_ae2/fluid_storage_cell_4k": {
        "machine": "brass",
        "ingredients": (
            "ae2:cell_component_4k",
            "create:fluid_pipe",
            "create:fluid_valve",
            "tfmg:rubber_sheet",
            "tfmg:plastic_sheet",
            "tfmg:coated_circuit_board",
            "tfmg:n_semiconductor",
            "tfmg:capacitor_item",
            "ae2:quartz_glass",
        ),
        "comment": (
            "Plumb the 4k fluid plane through a metered valve, then fit rubber and "
            "plastic seals, a coated sensor board, semiconductor valve driver, local "
            "buffer capacitor, and a quartz service face."
        ),
    },
    "industrial_colonies:v3_ae2/fluix_dense_smart_cable_batch": {
        "machine": "railway",
        "ingredients": (
            "15x ae2:fluix_smart_cable",
            "4x create:golden_sheet",
            "2x tfmg:coated_circuit_board",
            "ae2:calculation_processor",
            "4x tfmg:plastic_sheet",
            "2x tfmg:n_semiconductor",
            "2x tfmg:p_semiconductor",
            "2x tfmg:transistor_item",
            "2x tfmg:capacitor_item",
        ),
        "comment": (
            "Bundle sixteen smart channels behind gold contacts and paired coated "
            "routing boards, with calculation control, complementary line drivers, "
            "switching and buffer banks, and a thick plastic dielectric."
        ),
    },
    "industrial_colonies:v3_ae2/item_storage_cell_4k": {
        "machine": "brass",
        "ingredients": (
            "ae2:cell_component_4k",
            "ae2:logic_processor",
            "ae2:fluix_smart_cable",
            "tfmg:coated_circuit_board",
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:capacitor_item",
            "ae2:quartz_glass",
        ),
        "comment": (
            "Fit the 4k plane into its item housing with indexed logic and a smart "
            "fluix lead, then install a coated board, transistor driver, dielectric, "
            "buffer capacitor, and quartz service face."
        ),
    },
    "industrial_colonies:v3_ae2/item_storage_cell_16k": {
        "machine": "brass",
        "ingredients": (
            "ae2:cell_component_16k",
            "ae2:logic_processor",
            "ae2:fluix_smart_cable",
            "tfmg:coated_circuit_board",
            "2x tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:transistor_item",
            "ae2:quartz_vibrant_glass",
        ),
        "comment": (
            "Fit the 16k plane behind indexed logic and a smart fluix lead, adding a "
            "coated routing board, complementary address drivers, transistor gate, "
            "double dielectric liner, and vibrant service face."
        ),
    },
    "industrial_colonies:v3_ae2/item_storage_cell_64k": {
        "machine": "railway",
        "ingredients": (
            "ae2:cell_component_64k",
            "ae2:engineering_processor",
            "ae2:fluix_smart_cable",
            "tfmg:coated_circuit_board",
            "2x tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:magnetic_alloy_sheet",
            "tfmg:lithium_charge",
            "ae2:quartz_vibrant_glass",
        ),
        "comment": (
            "Package the 64k plane with engineering control and a smart bus, then add "
            "a coated address board, complementary drivers, doubled dielectric, "
            "magnetic shielding, lithium buffer, and vibrant service face."
        ),
    },
    "industrial_colonies:v3_ae2/mega_cell_component_1m": {
        "machine": "railway",
        "ingredients": (
            "3x ae2:cell_component_256k",
            "2x megacells:accumulation_processor",
            "appliedcreate:advanced_stress_processor",
            "tfmg:coated_circuit_board",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "ae2:quartz_vibrant_glass",
            "2x tfmg:plastic_sheet",
            "tfmg:magnetic_alloy_sheet",
            "tfmg:lithium_block",
        ),
        "comment": (
            "Combine four 256k planes under dual accumulation and stress scheduling, "
            "then fit a coated backplane, complementary drivers, dielectric package, "
            "magnetic shield, bulk lithium, and a vibrant inspection face."
        ),
    },
    "industrial_colonies:v3_ae2/quantum_processor": {
        "machine": "refined_radiance",
        "ingredients": (
            "ae2:printed_silicon",
            "tfmg:coated_circuit_board",
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "2x megacells:accumulation_processor",
            "appliedcreate:advanced_stress_processor",
            "electroenergetics:high_voltage_capacitor",
            "tfmg:transistor_item",
            "modernfoundry:cobalt_reinforcement",
            "allthemodium:allthemodium_ingot",
        ),
        "comment": (
            "Package two quantum processors over printed silicon and a coated board, "
            "with complementary logic, dielectric isolation, dual accumulation, "
            "stress timing, high-voltage buffering, cobalt cooling, and an ATM contact."
        ),
    },
}


TARGET_IDS = frozenset(SPECS)

_MACHINES = {
    "brass": ("createcasing:brass_deployer", "createcasing:brass_press"),
    "railway": ("createcasing:railway_deployer", "createcasing:railway_press"),
    "weathered_iron": (
        "createcasing:weathered_iron_deployer",
        "createcasing:weathered_iron_press",
    ),
    "refined_radiance": (
        "createcasing:refined_radiance_deployer",
        "createcasing:refined_radiance_press",
    ),
}

_PLASTIC = {"tfmg:plastic_sheet", "mekanism:hdpe_sheet"}
_SEMICONDUCTORS = {"tfmg:n_semiconductor", "tfmg:p_semiconductor"}
_CIRCUIT_COMPONENTS = {
    "tfmg:coated_circuit_board",
    "tfmg:circuit_board",
    "tfmg:capacitor_item",
    "tfmg:transistor_item",
    "tfmg:resistor",
}


def _plain_id(value: str) -> str:
    parts = value.split(maxsplit=1)
    if len(parts) == 2 and parts[0].endswith("x") and parts[0][:-1].isdigit():
        return parts[1]
    return value


def _index(data: dict[str, Any]) -> dict[str, Recipe]:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed seed must contain a recipes list")
    result: dict[str, Recipe] = {}
    for recipe in recipes:
        if not isinstance(recipe, dict) or not isinstance(recipe.get("id"), str):
            raise TypeError("managed recipes must be objects with string IDs")
        recipe_id = recipe["id"]
        if recipe_id in result:
            raise ValueError(f"duplicate managed recipe ID: {recipe_id}")
        result[recipe_id] = recipe
    return result


def apply(data: dict[str, Any]) -> None:
    recipes = _index(data)
    missing = sorted(TARGET_IDS.difference(recipes))
    if missing:
        raise KeyError(f"expected rejected AE2 electronics recipes are missing: {missing}")

    for recipe_id, spec in SPECS.items():
        recipe = recipes[recipe_id]
        if recipe.get("type") != "sequenced_assembly":
            raise ValueError(f"{recipe_id} is no longer a sequenced assembly")
        deployer, press = _MACHINES[spec["machine"]]
        recipe["comment"] = spec["comment"]
        recipe["loops"] = 1
        recipe["steps"] = [
            {"op": "deploying", "ingredient": item, "machine": deployer}
            for item in spec["ingredients"]
        ] + [{"op": "pressing", "machine": press}]

    audit(data)


def audit(data: dict[str, Any]) -> dict[str, Any]:
    recipes = _index(data)
    errors: list[str] = []
    boms: set[tuple[str, ...]] = set()
    for recipe_id, spec in SPECS.items():
        recipe = recipes.get(recipe_id)
        if recipe is None:
            errors.append(f"missing electronics redesign {recipe_id}")
            continue
        deployer, press = _MACHINES[spec["machine"]]
        steps = recipe.get("steps", [])
        deployed = tuple(
            step.get("ingredient")
            for step in steps
            if isinstance(step, dict) and step.get("op") == "deploying"
        )
        if deployed != spec["ingredients"]:
            errors.append(f"{recipe_id} electronics BOM drifted")
        if not steps or steps[-1] != {"op": "pressing", "machine": press}:
            errors.append(f"{recipe_id} lost its final {spec['machine']} press closure")
        if any(
            step.get("machine") != deployer
            for step in steps[:-1]
            if isinstance(step, dict)
        ):
            errors.append(f"{recipe_id} uses the wrong electronics deployer")
        plain = {_plain_id(item) for item in deployed if isinstance(item, str)}
        if not plain.intersection(_PLASTIC):
            errors.append(f"{recipe_id} has no dielectric/plastic package")
        if not plain.intersection(_SEMICONDUCTORS):
            errors.append(f"{recipe_id} has no semiconductor stage")
        if not plain.intersection(_CIRCUIT_COMPONENTS):
            errors.append(f"{recipe_id} has no serviceable circuit component")
        if not 8 <= len(deployed) <= 11:
            errors.append(f"{recipe_id} has an inappropriate electronics sequence length")
        if deployed in boms:
            errors.append(f"{recipe_id} reuses another rejected electronics BOM")
        boms.add(deployed)
    if errors:
        raise ValueError("AE2 electronics-depth audit failed: " + " | ".join(errors))
    return {
        "status": "PASS",
        "redesigned": len(TARGET_IDS),
        "unique_boms": len(boms),
    }
