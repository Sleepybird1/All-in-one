#!/usr/bin/env python3
"""Resolve the final one-off recipe-review rejections.

This cohort intentionally stays separate from the broad family passes because
each card has a different, very specific review instruction.  Eleven recipes
receive a purpose-built process or BOM.  The twelfth decision restores TFMG's
native Steel Mechanism recipe by retiring our managed replacement and every
exact removal that could suppress the stock recipe.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
INDUSTRIAL_DEPLOYER = "createcasing:industrial_iron_deployer"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"

STEEL_MECHANISM_MANAGED_ID = "industrial_colonies:tfmg_core/steel_mechanism"
STEEL_MECHANISM_STOCK_ID = "tfmg:sequenced_assembly/steel_mechanism"

REDESIGNED_IDS = frozenset(
    {
        "industrial_colonies:big_cannons/cannon_drill",
        "industrial_colonies:big_cannons/cannon_welder",
        "industrial_colonies:bigreactors/basic_reactor/control_rod",
        "industrial_colonies:enchantment_industry/classic_blaze_enchanter",
        "industrial_colonies:engines/huge_diesel_engine",
        "industrial_colonies:interstellar/warp_drive",
        "industrial_colonies:manufacturing/refined_radiance/fan",
        "industrial_colonies:mekanism_tools/armored_free_runners",
        "industrial_colonies:nuclear/refined_radiance",
        "industrial_colonies:simulated/altitude_sensor",
        "industrial_colonies:simulated/rope_coupling_batch",
    }
)

REVIEW_DECISION_IDS = REDESIGNED_IDS | {STEEL_MECHANISM_MANAGED_ID}

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


def _mechanical(*, comment: str, pattern: list[str], key: dict[str, str], output: Any) -> Recipe:
    return {
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "exclusive_output": True,
    }


def _sequence(
    *,
    comment: str,
    input_item: str,
    output: Any,
    ingredients: list[str],
    deployer: str,
    press: str,
) -> Recipe:
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


def redesigns() -> dict[str, Recipe]:
    result = {
        "industrial_colonies:big_cannons/cannon_drill": _mechanical(
            comment="Build the cannon borer as a supported feed carriage: Railway drill head and extension spindle above a heavy casing, geared electric drive, coolant pipes, service screws, and a full wear-plate bed",
            pattern=["  D  ", " PTP ", " SCS ", " GEG ", "HHHHH"],
            key={
                "C": "tfmg:heavy_machinery_casing",
                "D": "createcasing:railway_mechanical_drill",
                "E": "tfmg:electric_motor",
                "G": "tfmg:large_steel_cogwheel",
                "H": "tfmg:heavy_plate",
                "P": "tfmg:steel_pipe",
                "S": "tfmg:screw",
                "T": "create:piston_extension_pole",
            },
            output="createbigcannons:cannon_drill",
        ),
        "industrial_colonies:big_cannons/cannon_welder": _mechanical(
            comment="Lay out the mobile pressure welder as a Blaze torch over a valved steel lance and pressure tank, with propane feed, copper ignition lead, heat shield, and a broad TFMG Heavy-Plate skid",
            pattern=[" B  ", "VPT ", "FWH ", "HHHH"],
            key={
                "B": "create:blaze_burner",
                "F": "tfmg:propane_bucket",
                "H": "tfmg:heavy_plate",
                "P": "tfmg:steel_pipe",
                "T": "tfmg:steel_fluid_tank",
                "V": "tfmg:brass_fluid_valve",
                "W": "tfmg:copper_wire",
            },
            output="createbigcannons:cannon_welder",
        ),
        "industrial_colonies:bigreactors/basic_reactor/control_rod": _mechanical(
            comment="Assemble two reactor control-rod heads as Refined Radiance-shielded piston actuators over transistor metering, serviceable steel drives, heavy guide plates, and containment feet",
            pattern=["RPR", "T T", "M M", "H H", "C C"],
            key={
                "C": "bigreactors:basic_reactorcasing",
                "H": "tfmg:heavy_plate",
                "M": "tfmg:steel_mechanism",
                "P": "minecraft:piston",
                "R": "create:refined_radiance",
                "T": "tfmg:transistor_item",
            },
            output="2x bigreactors:basic_reactorcontrolrod",
        ),
        "industrial_colonies:enchantment_industry/classic_blaze_enchanter": _mechanical(
            comment="Build the automated enchanter as a handbook-guided workstation: Mechanical Arm and experience lantern above the original Blaze Enchanter, twin precision drives, Stress Processor control, and a rigid Brass base",
            pattern=[" H  ", "ALS ", "PBP ", "CCCC"],
            key={
                "A": "create:mechanical_arm",
                "B": "create_enchantment_industry:blaze_enchanter",
                "C": "create:brass_casing",
                "H": "create_enchantment_industry:blazes_enchanting_handbook",
                "L": "create_enchantment_industry:experience_lantern",
                "P": "create:precision_mechanism",
                "S": "appliedcreate:stress_processor",
            },
            output="create_enchantment_industry:classic_blaze_enchanter",
        ),
        "industrial_colonies:engines/huge_diesel_engine": _mechanical(
            comment="Construct the huge diesel generator as two complete large diesel sets around a synchronized TFMG engine controller and crankshaft, with turbocharged piston banks, fuel tanks, gearbox, and a full heavy bed; no turbine hardware is used",
            pattern=["T C T", "P L P", "D K D", "F G F", "HHHHH"],
            key={
                "C": "tfmg:engine_controller",
                "D": "createdieselgenerators:large_diesel_engine",
                "F": "tfmg:steel_fluid_tank",
                "G": "tfmg:engine_gearbox",
                "H": "tfmg:heavy_plate",
                "K": "tfmg:crankshaft",
                "L": "tfmg:large_engine",
                "P": "createdieselgenerators:engine_piston",
                "T": "createdieselgenerators:engine_turbocharger",
            },
            output="createdieselgenerators:huge_diesel_engine",
        ),
        "industrial_colonies:interstellar/warp_drive": _mechanical(
            comment="Assemble the reusable Warp Drive as a deliberate field-engine cross-section: paired Crystal Drivers and signed Warp Crystals around ultimate storage and quantum anchors, with Calorite focusing, heavy containment, duplicate route memory, navigation authority, and the Industrial Star core",
            pattern=["TWHWT", "EQUQE", "CRMRC", "EHDHE", "TXIXT"],
            key={
                "C": "ad_astra:calorite_plate",
                "D": "industrial_colonies:interstellar_navigation_computer",
                "E": "mekanism:ultimate_energy_cube",
                "H": "tfmg:heavy_machinery_casing",
                "I": "industrial_colonies:industrial_star",
                "M": "cosmowarp:moon_crystal",
                "Q": "ae2:quantum_entangled_singularity",
                "R": "cosmowarp:warp_crystal",
                "T": "rocketnautics:titanium_casing",
                "U": "mekanism:ultimate_control_circuit",
                "W": "cosmowarp:crystal_driver",
                "X": "cosmowarp:memory_card",
            },
            output="cosmowarp:warp_drive",
        ),
        "industrial_colonies:manufacturing/refined_radiance/fan": _sequence(
            comment="Upgrade the complete Industrial Iron fan without rebuilding its inherited rotor: add Radiance casing and field material, atomic bracing, high-voltage starting capacitance, magnetic laminations, and an elite speed interlock before the Industrial press seals it",
            input_item="createcasing:industrial_iron_encased_fan",
            output="createcasing:refined_radiance_encased_fan",
            ingredients=[
                "create:refined_radiance_casing",
                "create:refined_radiance",
                "mekanism:alloy_atomic",
                "electroenergetics:high_voltage_capacitor",
                "tfmg:magnetic_alloy_sheet",
                "mekanism:elite_control_circuit",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
        ),
        "industrial_colonies:mekanism_tools/armored_free_runners": _mechanical(
            comment="Armor the completed Free Runners as a matched boot silhouette: cobalt impact caps, heavy ankle guards, atomic side braces, diamond wear faces, and replaceable rubber soles",
            pattern=["C   C", "H   H", "A F A", "D   D", "R   R"],
            key={
                "A": "mekanism:alloy_atomic",
                "C": "modernfoundry:cobalt_ingot",
                "D": "minecraft:diamond",
                "F": "mekanism:free_runners",
                "H": "tfmg:heavy_plate",
                "R": "tfmg:rubber_sheet",
            },
            output="mekanism:free_runners_armored",
        ),
        "industrial_colonies:nuclear/refined_radiance": {
            "type": "compacting",
            "comment": "Compress a serious two-unit Radiance charge from four Chromatic Compound, paired Yellorium field dopants, engineering logic, atomic lattice alloy, a high-voltage energy reservoir, and an Allthemodium stabilizer",
            "inputs": [
                "4x create:chromatic_compound",
                "2x bigreactors:yellorium_ingot",
                "ae2:engineering_processor",
                "mekanism:alloy_atomic",
                "electroenergetics:high_voltage_capacitor",
                "allthemodium:allthemodium_ingot",
            ],
            "machine": INDUSTRIAL_PRESS,
            "output": {"count": 2, "id": "create:refined_radiance", "kind": "ITEM"},
            "exclusive_output": True,
        },
        "industrial_colonies:simulated/altitude_sensor": _sequence(
            comment="Instrument a sealed Copper barometric body with a glass reference chamber, paper diaphragm, compass movement, electron-tube pickup, copper lead, Redstone Link telemetry, and precision gearing",
            input_item="create:copper_casing",
            output="simulated:altitude_sensor",
            ingredients=[
                "minecraft:glass_bottle",
                "minecraft:paper",
                "minecraft:compass",
                "create:electron_tube",
                "tfmg:copper_wire",
                "create:redstone_link",
                "create:precision_mechanism",
            ],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:simulated/rope_coupling_batch": _sequence(
            comment="Pair two finished rope eyes around a through-shaft, wrap the swivel in a TFMG Heavy Plate, secure it with paired service screws, and Railway-press a matched pair of load-rated couplings",
            input_item="simulated:rope_connector",
            output="2x simulated:rope_coupling",
            ingredients=[
                "simulated:rope_connector",
                "create:shaft",
                "tfmg:heavy_plate",
                "2x tfmg:screw",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
    }
    if set(result) != REDESIGNED_IDS:
        missing = sorted(REDESIGNED_IDS - set(result))
        extra = sorted(set(result) - REDESIGNED_IDS)
        raise AssertionError(f"manual rejection coverage drifted; missing={missing}, extra={extra}")
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


def _remove_stock_suppression(data: dict[str, Any]) -> None:
    """Retire our Steel Mechanism override and preserve TFMG's native recipe."""

    data["recipes"] = [
        recipe
        for recipe in data["recipes"]
        if recipe.get("id") != STEEL_MECHANISM_MANAGED_ID
    ]

    containers = [*data.get("recipes", [])]
    for family in data.get("machine_families", []):
        containers.extend(family.get("recipes", []))
    for recipe in containers:
        removals = recipe.get("remove")
        if isinstance(removals, list):
            recipe["remove"] = [value for value in removals if value != STEEL_MECHANISM_STOCK_ID]
        dependencies = recipe.get("depends_on")
        if isinstance(dependencies, list):
            filtered = [value for value in dependencies if value != STEEL_MECHANISM_MANAGED_ID]
            if filtered:
                recipe["depends_on"] = filtered
            else:
                recipe.pop("depends_on", None)

    data["additional_removals"] = [
        value
        for value in data.get("additional_removals", [])
        if value != STEEL_MECHANISM_STOCK_ID
    ]
    data["disabled_recipe_ids"] = [
        value
        for value in data.get("disabled_recipe_ids", [])
        if value != STEEL_MECHANISM_MANAGED_ID
    ]
    preserved = data.setdefault("preserve_recipe_ids", [])
    if not isinstance(preserved, list):
        raise TypeError("preserve_recipe_ids must be a list")
    if STEEL_MECHANISM_STOCK_ID not in preserved:
        preserved.append(STEEL_MECHANISM_STOCK_ID)
    preserved.sort()


def apply(data: dict[str, Any]) -> None:
    indexes = _index(data)
    missing = sorted(REDESIGNED_IDS - set(indexes))
    if missing:
        raise KeyError(f"expected active one-off rejected recipes are missing: {missing}")
    for recipe_id, process in redesigns().items():
        recipe = data["recipes"][indexes[recipe_id]]
        for field in _PROCESS_FIELDS:
            recipe.pop(field, None)
        recipe.update(deepcopy(process))
    _remove_stock_suppression(data)


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    errors: list[str] = []
    if not REDESIGNED_IDS <= set(indexes):
        errors.append("one or more redesigned one-off recipes are missing")
    if STEEL_MECHANISM_MANAGED_ID in indexes:
        errors.append("managed Steel Mechanism replacement was not retired")
    if STEEL_MECHANISM_STOCK_ID not in data.get("preserve_recipe_ids", []):
        errors.append("TFMG's stock Steel Mechanism recipe is not explicitly preserved")
    if STEEL_MECHANISM_STOCK_ID in data.get("additional_removals", []):
        errors.append("TFMG's stock Steel Mechanism recipe remains additionally removed")

    all_recipes = [*data.get("recipes", [])]
    for family in data.get("machine_families", []):
        all_recipes.extend(family.get("recipes", []))
    for recipe in all_recipes:
        recipe_id = recipe.get("id", "<missing>")
        if STEEL_MECHANISM_STOCK_ID in recipe.get("remove", []):
            errors.append(f"{recipe_id} still suppresses the stock Steel Mechanism recipe")
        if STEEL_MECHANISM_MANAGED_ID in recipe.get("depends_on", []):
            errors.append(f"{recipe_id} still depends on the retired managed Steel Mechanism recipe")

    if REDESIGNED_IDS <= set(indexes):
        recipes = {recipe_id: data["recipes"][indexes[recipe_id]] for recipe_id in REDESIGNED_IDS}
        if recipes["industrial_colonies:big_cannons/cannon_drill"].get("type") != "mechanical_crafting":
            errors.append("cannon drill is not mechanically crafted as a physical boring carriage")
        if recipes["industrial_colonies:big_cannons/cannon_welder"].get("type") != "mechanical_crafting":
            errors.append("cannon welder is not mechanically crafted as a pressure-welder chassis")
        if "create:refined_radiance" not in repr(recipes["industrial_colonies:bigreactors/basic_reactor/control_rod"]):
            errors.append("basic reactor control rod lacks Refined Radiance tier material")
        huge = repr(recipes["industrial_colonies:engines/huge_diesel_engine"])
        if "tfmg:turbine_engine" in huge or "tfmg:turbine_blade" in huge:
            errors.append("huge diesel generator still contains turbine hardware")
        warp = repr(recipes["industrial_colonies:interstellar/warp_drive"])
        for required in ("cosmowarp:crystal_driver", "cosmowarp:warp_crystal", "cosmowarp:memory_card"):
            if required not in warp:
                errors.append(f"warp drive lacks {required}")
        fan = recipes["industrial_colonies:manufacturing/refined_radiance/fan"]
        fan_deployments = [step for step in fan.get("steps", []) if step.get("op") == "deploying"]
        if len(fan_deployments) != 6:
            errors.append("Refined Radiance fan was not reduced to six focused upgrades")
        radiance = repr(recipes["industrial_colonies:nuclear/refined_radiance"])
        for required in (
            "mekanism:alloy_atomic",
            "electroenergetics:high_voltage_capacitor",
            "allthemodium:allthemodium_ingot",
        ):
            if required not in radiance:
                errors.append(f"Refined Radiance synthesis lacks {required}")
        altitude = recipes["industrial_colonies:simulated/altitude_sensor"]
        if altitude.get("type") != "sequenced_assembly" or len(altitude.get("steps", [])) != 8:
            errors.append("altitude sensor is not a complete seven-component instrument assembly")
        coupling = recipes["industrial_colonies:simulated/rope_coupling_batch"]
        if coupling.get("type") != "sequenced_assembly" or coupling.get("output") != "2x simulated:rope_coupling":
            errors.append("rope coupling is not a paired Railway swivel assembly")

    return {
        "status": "PASS" if not errors else "FAIL",
        "redesigned": len(REDESIGNED_IDS),
        "restored_default": 1,
        "review_decisions": len(REVIEW_DECISION_IDS),
        "errors": errors,
    }
