#!/usr/bin/env python3
"""Source-only redesigns for the active rejected BigReactors hardware cohort.

These fifteen cards were rejected specifically as too cheap or as lacking
electronics.  The replacements model real subassemblies: turbine shafts and
governors, resonant energy cores, grid interfaces, metered process ports, and
operator/control consoles.  They intentionally avoid generic expensive-item
rings and retain every recipe's ID/output/removal ownership contract.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

INDUSTRIAL_DEPLOYER = "createcasing:industrial_iron_deployer"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"

BIGREACTORS_REJECTED_IDS = frozenset(
    {
        "industrial_colonies:bigreactors/basic_turbine/controller",
        "industrial_colonies:bigreactors/basic_turbine/rotor_bearing",
        "industrial_colonies:bigreactors/energizer/active_power_port",
        "industrial_colonies:bigreactors/energizer/energy_cell",
        "industrial_colonies:bigreactors/energizer/energy_core",
        "industrial_colonies:bigreactors/energizer/power_port",
        "industrial_colonies:bigreactors/fluidizer/power_port",
        "industrial_colonies:bigreactors/fluidizer/solid_injector",
        "industrial_colonies:bigreactors/reprocessor/collector",
        "industrial_colonies:bigreactors/reprocessor/controller",
        "industrial_colonies:bigreactors/reprocessor/fluid_injector",
        "industrial_colonies:bigreactors/reprocessor/output_port",
        "industrial_colonies:bigreactors/reprocessor/power_port",
        "industrial_colonies:bigreactors/reprocessor/waste_injector",
        "industrial_colonies:nuclear/reinforced_reactor_controller",
    }
)

ELECTRONICS_REJECTION_IDS = frozenset(
    {
        "industrial_colonies:bigreactors/basic_turbine/rotor_bearing",
        "industrial_colonies:bigreactors/reprocessor/controller",
        "industrial_colonies:nuclear/reinforced_reactor_controller",
    }
)

SEQUENCE_FAMILIES = {
    "industrial_colonies:bigreactors/energizer/active_power_port": "radiance",
    "industrial_colonies:bigreactors/energizer/energy_cell": "radiance",
    "industrial_colonies:bigreactors/energizer/energy_core": "radiance",
    "industrial_colonies:bigreactors/energizer/power_port": "radiance",
    "industrial_colonies:bigreactors/fluidizer/power_port": "radiance",
    "industrial_colonies:bigreactors/fluidizer/solid_injector": "industrial",
    "industrial_colonies:bigreactors/reprocessor/collector": "industrial",
    "industrial_colonies:bigreactors/reprocessor/fluid_injector": "industrial",
    "industrial_colonies:bigreactors/reprocessor/output_port": "industrial",
    "industrial_colonies:bigreactors/reprocessor/power_port": "radiance",
    "industrial_colonies:bigreactors/reprocessor/waste_injector": "industrial",
}

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
    "exclusive_output",
}


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _sequence(
    *,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    family: str,
) -> Recipe:
    deployer, press = {
        "industrial": (INDUSTRIAL_DEPLOYER, INDUSTRIAL_PRESS),
        "radiance": (RADIANCE_DEPLOYER, RADIANCE_PRESS),
    }[family]
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "steps": [*(_deploy(item, deployer) for item in ingredients), {"op": "pressing", "machine": press}],
        "loops": 1,
        "output": output,
        "exclusive_output": True,
    }


def _mechanical(*, comment: str, pattern: list[str], key: dict[str, str], output: str) -> Recipe:
    return {
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "exclusive_output": True,
    }


def redesigns() -> dict[str, Recipe]:
    result: dict[str, Recipe] = {
        "industrial_colonies:bigreactors/basic_turbine/controller": _mechanical(
            comment="Build a turbine governor console above its three-section rotor shaft, with a computer/display panel, complementary sensor board, twin generator-transformer banks, and inherited reactor interlock",
            pattern=[" MCM ", "LNEDP", "KSSSK", "TGUGT", " KAK "],
            key={
                "A": "bigreactors:basic_reactorcontroller",
                "C": "computercraft:computer_advanced",
                "D": "tfmg:coated_circuit_board",
                "E": "ae2:engineering_processor",
                "G": "tfmg:generator",
                "K": "bigreactors:basic_turbinecasing",
                "L": "tfmg:plastic_sheet",
                "M": "computercraft:monitor_advanced",
                "N": "tfmg:n_semiconductor",
                "P": "tfmg:p_semiconductor",
                "S": "bigreactors:basic_turbinerotorshaft",
                "T": "tfmg:transformer",
                "U": "mekanism:elite_control_circuit",
            },
            output="bigreactors:basic_turbinecontroller",
        ),
        "industrial_colonies:bigreactors/basic_turbine/rotor_bearing": _mechanical(
            comment="Construct a load-bearing shaft race with heavy cheeks and geared steel drive, then embed a plastic-isolated N/P vibration sensor board and elite overspeed interlock",
            pattern=[" HCH ", "LGNGL", "SMDMS", "LGPGL", " HEH "],
            key={
                "C": "bigreactors:basic_turbinecasing",
                "D": "tfmg:coated_circuit_board",
                "E": "mekanism:elite_control_circuit",
                "G": "create:large_cogwheel",
                "H": "tfmg:heavy_plate",
                "L": "tfmg:plastic_sheet",
                "M": "tfmg:steel_mechanism",
                "N": "tfmg:n_semiconductor",
                "P": "tfmg:p_semiconductor",
                "S": "create:shaft",
            },
            output="bigreactors:basic_turbinerotorbearing",
        ),
        "industrial_colonies:bigreactors/reprocessor/controller": _mechanical(
            comment="Lay out the reprocessor as a visible material-flow console: waste and collection heads over twin chemical-vat lanes, solid output below, inherited reactor safety, and a plastic-isolated N/P digital control shelf",
            pattern=[" NWK ", "LVOVL", "MABAM", "PDUCE", " RQR "],
            key={
                "A": "bigreactors:reprocessorcasing",
                "B": "bigreactors:basic_reactorcontroller",
                "C": "computercraft:computer_advanced",
                "D": "tfmg:coated_circuit_board",
                "E": "ae2:engineering_processor",
                "K": "bigreactors:reprocessorcollector",
                "L": "tfmg:plastic_sheet",
                "M": "computercraft:monitor_advanced",
                "N": "tfmg:n_semiconductor",
                "O": "bigreactors:reprocessoroutputport",
                "P": "tfmg:p_semiconductor",
                "Q": "create:refined_radiance_casing",
                "R": "bigreactors:reprocessorcasing",
                "U": "mekanism:ultimate_control_circuit",
                "V": "tfmg:steel_chemical_vat",
                "W": "bigreactors:reprocessorwasteinjector",
            },
            output="bigreactors:reprocessorcontroller",
        ),
        "industrial_colonies:nuclear/reinforced_reactor_controller": _mechanical(
            comment="Rebuild the basic controller as a reinforced operator console with redundant displays/computer, plastic-isolated complementary sensing, a populated TFMG board, ultimate safety logic, engineering processors, and radiance shielding",
            pattern=[" MCM ", "LNDPL", "RUBUR", "REDER", " RQR "],
            key={
                "B": "bigreactors:basic_reactorcontroller",
                "C": "computercraft:computer_advanced",
                "D": "tfmg:coated_circuit_board",
                "E": "ae2:engineering_processor",
                "L": "tfmg:plastic_sheet",
                "M": "computercraft:monitor_advanced",
                "N": "tfmg:n_semiconductor",
                "P": "tfmg:p_semiconductor",
                "Q": "create:refined_radiance_casing",
                "R": "bigreactors:reinforced_reactorcasing",
                "U": "mekanism:ultimate_control_circuit",
            },
            output="bigreactors:reinforced_reactorcontroller",
        ),
    }

    sequences = {
        "industrial_colonies:bigreactors/energizer/active_power_port": (
            "Instrument the passive Energizer interface with a double grid connector, current transformer, relay, plastic-isolated N/P sensing board, capacitor, and elite transfer governor",
            "bigreactors:energizerpowerport_fe",
            "bigreactors:energizerpowerport_fe_active",
            ["electroenergetics:double_connector", "electroenergetics:current_transformer", "computercraft:redstone_relay", "tfmg:coated_circuit_board", "tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:capacitor_item", "tfmg:plastic_sheet", "mekanism:elite_control_circuit"],
        ),
        "industrial_colonies:bigreactors/energizer/energy_core": (
            "Grow a resonance core around a proven energy buffer using Magentite field material, paired Anglesite optics, complementary semiconductor control, populated TFMG logic, atomic alloy, and radiance confinement",
            "mekanism:advanced_energy_cube",
            "bigreactors:energycore",
            ["bigreactors:magentite_ingot", "bigreactors:anglesite_crystal", "bigreactors:anglesite_crystal", "tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:coated_circuit_board", "ae2:engineering_processor", "mekanism:alloy_atomic", "create:refined_radiance_casing"],
        ),
        "industrial_colonies:bigreactors/energizer/energy_cell": (
            "Sleeve the completed resonance core with paired Benitoite optics, an elite induction buffer, magnetic laminations, plastic-isolated complementary sensing, and radiance shielding",
            "bigreactors:energycore",
            "bigreactors:energizercell",
            ["bigreactors:benitoite_crystal", "bigreactors:benitoite_crystal", "mekanism:elite_induction_cell", "tfmg:magnetic_alloy_ingot", "tfmg:coated_circuit_board", "tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:plastic_sheet", "create:refined_radiance_casing"],
        ),
        "industrial_colonies:bigreactors/energizer/power_port": (
            "Convert an Energizer casing into a buffered grid interface with a transformer, steel cable termination, double connector, capacitor bank, and plastic-isolated complementary control board",
            "bigreactors:energizercasing",
            "bigreactors:energizerpowerport_fe",
            ["tfmg:transformer", "tfmg:steel_cable_hub", "mekanism:advanced_energy_cube", "electroenergetics:double_connector", "tfmg:capacitor_item", "tfmg:coated_circuit_board", "tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:plastic_sheet"],
        ),
        "industrial_colonies:bigreactors/fluidizer/power_port": (
            "Terminate the Fluidizer grid feed through transformer isolation, buffered energy, a steel cable hub, double connector, and plastic-isolated N/P dosing controller",
            "bigreactors:fluidizercasing",
            "bigreactors:fluidizerpowerport",
            ["tfmg:transformer", "mekanism:advanced_energy_cube", "tfmg:steel_cable_hub", "electroenergetics:double_connector", "tfmg:coated_circuit_board", "tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:plastic_sheet", "mekanism:elite_control_circuit"],
        ),
        "industrial_colonies:bigreactors/fluidizer/solid_injector": (
            "Build a metered solids feed from vault storage, a filtered smart chute, powered piston and motor, steel drive mechanism, and protected advanced dosing control",
            "bigreactors:fluidizercasing",
            "bigreactors:fluidizersolidinjector",
            ["create:item_vault", "create:smart_chute", "create:filter", "create:mechanical_piston", "tfmg:electric_motor", "tfmg:steel_mechanism", "tfmg:coated_circuit_board", "tfmg:plastic_sheet", "mekanism:advanced_control_circuit"],
        ),
        "industrial_colonies:bigreactors/reprocessor/collector": (
            "Build bulk product collection around vault storage, paired smart extraction chutes, a filter and logistical sorter, then drive it with a serviceable steel mechanism and motor",
            "bigreactors:reprocessorcasing",
            "bigreactors:reprocessorcollector",
            ["create:item_vault", "create:smart_chute", "create:smart_chute", "create:filter", "mekanism:logistical_sorter", "tfmg:steel_mechanism", "tfmg:electric_motor", "mekanism:advanced_control_circuit"],
        ),
        "industrial_colonies:bigreactors/reprocessor/fluid_injector": (
            "Plumb a pressure-rated reprocessor injector from a chemical vat, powered pump, twin steel feeds, shutoff valve, chemical buffer, smart flow section, and elite metering circuit",
            "bigreactors:reprocessorcasing",
            "bigreactors:reprocessorfluidinjector",
            ["tfmg:steel_chemical_vat", "tfmg:electric_pump", "tfmg:steel_pipe", "tfmg:steel_pipe", "tfmg:steel_fluid_valve", "mekanism:advanced_chemical_tank", "tfmg:steel_smart_fluid_pipe", "mekanism:elite_control_circuit"],
        ),
        "industrial_colonies:bigreactors/reprocessor/output_port": (
            "Build a powered solid-output face around vault storage, filtered smart extraction, a framed steel drive, logistical sorter, and advanced routing control",
            "bigreactors:reprocessorcasing",
            "bigreactors:reprocessoroutputport",
            ["create:item_vault", "create:smart_chute", "create:filter", "tfmg:steel_frame", "tfmg:steel_mechanism", "tfmg:electric_motor", "mekanism:logistical_sorter", "mekanism:advanced_control_circuit"],
        ),
        "industrial_colonies:bigreactors/reprocessor/power_port": (
            "Electrify the reprocessor through transformer isolation, a steel cable hub, buffered energy and double connector, then add a capacitor and plastic-isolated complementary control board",
            "bigreactors:reprocessorcasing",
            "bigreactors:reprocessorpowerport",
            ["tfmg:transformer", "tfmg:steel_cable_hub", "mekanism:energy_tablet", "electroenergetics:double_connector", "tfmg:capacitor_item", "tfmg:coated_circuit_board", "tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:plastic_sheet"],
        ),
        "industrial_colonies:bigreactors/reprocessor/waste_injector": (
            "Build a contained waste feed from a chemical vat, powered pump, isolated steel line and valve, radioactive buffer barrel, smart flow section, and elite interlock",
            "bigreactors:reprocessorcasing",
            "bigreactors:reprocessorwasteinjector",
            ["tfmg:steel_chemical_vat", "tfmg:electric_pump", "tfmg:steel_pipe", "tfmg:steel_fluid_valve", "mekanism:advanced_chemical_tank", "mekanism:radioactive_waste_barrel", "tfmg:steel_smart_fluid_pipe", "mekanism:elite_control_circuit"],
        ),
    }
    for recipe_id, (comment, input_item, output, ingredients) in sequences.items():
        result[recipe_id] = _sequence(
            comment=comment,
            input_item=input_item,
            output=output,
            ingredients=ingredients,
            family=SEQUENCE_FAMILIES[recipe_id],
        )
    if set(result) != BIGREACTORS_REJECTED_IDS:
        missing = sorted(BIGREACTORS_REJECTED_IDS - set(result))
        extra = sorted(set(result) - BIGREACTORS_REJECTED_IDS)
        raise AssertionError(f"internal BigReactors redesign coverage drifted; missing={missing}, extra={extra}")
    return result


def _index(data: dict[str, Any]) -> dict[str, int]:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed seed must contain a recipes list")
    result: dict[str, int] = {}
    for index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict) or not isinstance(recipe.get("id"), str):
            raise TypeError("managed recipes must be objects with string IDs")
        if recipe["id"] in result:
            raise ValueError(f"duplicate managed recipe ID: {recipe['id']}")
        result[recipe["id"]] = index
    return result


def apply(data: dict[str, Any]) -> None:
    indexes = _index(data)
    missing = sorted(BIGREACTORS_REJECTED_IDS - set(indexes))
    if missing:
        raise KeyError(f"expected active rejected BigReactors recipes are missing: {missing}")
    for recipe_id, process in redesigns().items():
        recipe = data["recipes"][indexes[recipe_id]]
        for field in _PROCESS_FIELDS:
            recipe.pop(field, None)
        recipe.update(deepcopy(process))


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    errors: list[str] = []
    if not BIGREACTORS_REJECTED_IDS <= set(indexes):
        errors.append("one or more exact rejected BigReactors recipes are missing")
    for recipe_id in sorted(BIGREACTORS_REJECTED_IDS & set(indexes)):
        recipe = data["recipes"][indexes[recipe_id]]
        text = repr(recipe)
        if "mekanism:steel_casing" in text:
            errors.append(f"{recipe_id} uses retired Mekanism steel casing")
        if recipe.get("type") == "mechanical_crafting":
            pattern = recipe.get("pattern", [])
            if len(pattern) != 5 or any(not isinstance(row, str) or len(row) != 5 for row in pattern):
                errors.append(f"{recipe_id} is not a valid 5x5 mechanical BOM")
            if len(set(recipe.get("key", {}).values())) < 9:
                errors.append(f"{recipe_id} lacks a varied functional BOM")
        elif recipe.get("type") == "sequenced_assembly":
            steps = recipe.get("steps", [])
            deployments = [step for step in steps if step.get("op") == "deploying"]
            if len(deployments) < 8 or len(deployments) > 9:
                errors.append(f"{recipe_id} must use a focused 8-9 part assembly")
            family = SEQUENCE_FAMILIES[recipe_id]
            expected_deployer, expected_press = {
                "industrial": (INDUSTRIAL_DEPLOYER, INDUSTRIAL_PRESS),
                "radiance": (RADIANCE_DEPLOYER, RADIANCE_PRESS),
            }[family]
            if any(step.get("machine") != expected_deployer for step in deployments):
                errors.append(f"{recipe_id} uses the wrong deployer family")
            if not steps or steps[-1] != {"op": "pressing", "machine": expected_press}:
                errors.append(f"{recipe_id} uses the wrong final press family")
        else:
            errors.append(f"{recipe_id} has unsupported redesign type {recipe.get('type')!r}")
        if recipe_id in ELECTRONICS_REJECTION_IDS:
            for required in (
                "tfmg:plastic_sheet",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:coated_circuit_board",
            ):
                if required not in text:
                    errors.append(f"{recipe_id} lacks required electronics {required}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "redesigned": len(BIGREACTORS_REJECTED_IDS),
        "mechanical": 4,
        "sequenced": 11,
        "errors": errors,
    }
