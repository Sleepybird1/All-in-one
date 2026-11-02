#!/usr/bin/env python3
"""Source-only redesigns for the final rejected manufacturing cohort.

The batch replaces cheap placeholder recipes with recognizable functional
assemblies: wired control hardware, five distinct Railway machine BOMs,
pressure-compacted pumpjack pivots, a heavy isotope centrifuge, and a
structurally compacted TFMG machinery casing.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"

MANUFACTURING_REJECT_IDS = frozenset(
    {
        "industrial_colonies:create_addons/fuse_holder_batch",
        "industrial_colonies:create_addons/sturdy_whisk",
        "industrial_colonies:create_core/mechanical_arm",
        "industrial_colonies:create_core/rotation_speed_controller",
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_mixer",
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part",
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_part",
        "industrial_colonies:manufacturing/railway/deployer",
        "industrial_colonies:manufacturing/railway/depot",
        "industrial_colonies:manufacturing/railway/mixer",
        "industrial_colonies:manufacturing/railway/press",
        "industrial_colonies:mekanism/advanced_control_circuit",
        "industrial_colonies:mekanism_nuclear/isotopic_centrifuge",
        "industrial_colonies:tfmg_core/heavy_machinery_casing",
        "industrial_colonies:v3_createcasing/railway_saw",
    }
)

RAILWAY_ELECTRONICS_IDS = frozenset(
    {
        "industrial_colonies:manufacturing/railway/deployer",
        "industrial_colonies:manufacturing/railway/depot",
        "industrial_colonies:manufacturing/railway/mixer",
        "industrial_colonies:manufacturing/railway/press",
        "industrial_colonies:v3_createcasing/railway_saw",
    }
)

PUMP_COMPACTING_IDS = frozenset(
    {
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part",
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_part",
    }
)

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
    ingredients: list[str],
    output: str,
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


def _mechanical(*, comment: str, pattern: list[str], key: dict[str, str], output: str) -> Recipe:
    return {
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "exclusive_output": True,
    }


def _compacting(*, comment: str, inputs: list[str], output: str) -> Recipe:
    return {
        "type": "compacting",
        "comment": comment,
        "inputs": inputs,
        "machine": RAILWAY_PRESS,
        "heat": "none",
        "output": output,
        "exclusive_output": True,
    }


def redesigns() -> dict[str, Recipe]:
    result: dict[str, Recipe] = {
        "industrial_colonies:create_addons/fuse_holder_batch": _sequence(
            comment="Populate two panel fuse beds with paired ceramic barriers, plastic covers, twin copper leads, replaceable grid contacts, and a shared porcelain line insulator",
            input_item="electroenergetics:electrical_panel",
            ingredients=["tfmg:fireproof_bricks", "tfmg:fireproof_bricks", "tfmg:plastic_sheet", "tfmg:copper_wire", "tfmg:copper_wire", "electroenergetics:connector", "electroenergetics:connector", "electroenergetics:insulator"],
            output="2x electroenergetics:fuse_holder",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:create_addons/sturdy_whisk": _sequence(
            comment="Rebuild a standard whisk around a serviceable steel drive, three sturdy-sheet tine groups, a heavy hub plate, and a bolted shaft collar",
            input_item="create:whisk",
            ingredients=["create:sturdy_sheet", "create:sturdy_sheet", "create:sturdy_sheet", "tfmg:steel_mechanism", "tfmg:heavy_plate", "create:shaft", "tfmg:screw"],
            output="createmetallurgy:sturdy_whisk",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:create_core/mechanical_arm": _sequence(
            comment="Manufacture the Mechanical Arm from its Brass hand, geared elbow and shaft, belt drive, powered motor, item filter, tube control, populated board, and pressed Brass shell",
            input_item="create:brass_hand",
            ingredients=["create:precision_mechanism", "create:shaft", "create:belt_connector", "tfmg:electric_motor", "create:filter", "create:electron_tube", "tfmg:coated_circuit_board", "create:brass_sheet"],
            output="create:mechanical_arm",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:create_core/rotation_speed_controller": _sequence(
            comment="Build a closed-loop Brass governor around its large driven gear, shaft and precision mechanism, then pair speed/stress feedback with tube logic, comparator control, and a pressed cover",
            input_item="create:brass_casing",
            ingredients=["create:large_cogwheel", "create:shaft", "create:precision_mechanism", "create:speedometer", "create:stressometer", "create:electron_tube", "minecraft:comparator", "create:brass_sheet"],
            output="create:rotation_speed_controller",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_mixer": _sequence(
            comment="Refit the proven industrial mixer with a complete foundry basin, sturdy whisk, twin refractory linings, powered steel drive, copper thermal jacket, and heavy Railway closure",
            input_item="tfmg:industrial_mixer",
            ingredients=["createmetallurgy:foundry_basin", "createmetallurgy:sturdy_whisk", "createmetallurgy:refractory_mortar", "createmetallurgy:refractory_mortar", "tfmg:electric_motor", "tfmg:steel_mechanism", "create:copper_casing", "tfmg:heavy_plate"],
            output="createmetallurgy:foundry_mixer",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_part": _compacting(
            comment="Pressure-forge a matched small walking-beam pivot pair from cast-iron stock around a steel load spine, heavy bearing cheek, and rebar pin",
            inputs=["4x tfmg:cast_iron_ingot", "tfmg:steel_ingot", "tfmg:heavy_plate", "tfmg:rebar"],
            output="2x tfmg:pumpjack_hammer_part",
        ),
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part": _compacting(
            comment="Pressure-forge one large pumpjack walking-beam pivot from a full cast-iron charge, paired heavy bearing cheeks, steel load block, and twin rebar pins",
            inputs=["8x tfmg:cast_iron_ingot", "2x tfmg:heavy_plate", "tfmg:steel_block", "2x tfmg:rebar"],
            output="tfmg:large_pumpjack_hammer_part",
        ),
        "industrial_colonies:tfmg_core/heavy_machinery_casing": _compacting(
            comment="Pressure-close a serviceable TFMG steel shell around a structural frame with four heavy armor plates, paired rebar ribs, and a full bolted seam",
            inputs=["tfmg:steel_casing", "tfmg:steel_frame", "4x tfmg:heavy_plate", "2x tfmg:rebar", "8x tfmg:screw"],
            output="tfmg:heavy_machinery_casing",
        ),
        "industrial_colonies:mekanism/advanced_control_circuit": _sequence(
            comment="Upgrade basic Mekanism logic with twin infused-alloy buses, a plastic-isolated TFMG board, complementary semiconductor stage, discrete capacitor/transistor pair, and magnetic shielding",
            input_item="mekanism:basic_control_circuit",
            ingredients=["mekanism:alloy_infused", "mekanism:alloy_infused", "tfmg:coated_circuit_board", "tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:capacitor_item", "tfmg:transistor_item", "tfmg:plastic_sheet", "tfmg:magnetic_alloy_sheet"],
            output="mekanism:advanced_control_circuit",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:mekanism_nuclear/isotopic_centrifuge": _mechanical(
            comment="Build the isotope separator as a restrained five-stage rotor tower with magnetic bearings, paired chemical buffers, titanium armor, TFMG frame and transformer base, plus plastic-isolated complementary high-speed control",
            pattern=[" THT ", "RMRMR", "CLDQC", "NEUEN", "FWXWF"],
            key={
                "C": "mekanism:advanced_chemical_tank",
                "D": "tfmg:coated_circuit_board",
                "E": "ae2:engineering_processor",
                "F": "tfmg:steel_frame",
                "H": "tfmg:heavy_plate",
                "L": "tfmg:plastic_sheet",
                "M": "tfmg:laminated_magnetic_alloy_block",
                "N": "tfmg:n_semiconductor",
                "Q": "tfmg:p_semiconductor",
                "R": "tfmg:rotor",
                "T": "rocketnautics:titanium_alloy_sheet",
                "U": "mekanism:ultimate_control_circuit",
                "W": "tfmg:transformer",
                "X": "tfmg:centrifuge",
            },
            output="mekanism:isotopic_centrifuge",
        ),
    }

    railway = {
        "industrial_colonies:manufacturing/railway/deployer": (
            "Fabricate a Railway deployer as a powered articulated hand over the Brass core, with heavy arm plate, motor, complementary sensor board, plastic isolation, Railway shell, and framed base",
            ["  HT", "MNH ", "LDQB", "FCFF"],
            {"B": "createcasing:brass_deployer", "C": "create:railway_casing", "D": "tfmg:coated_circuit_board", "F": "tfmg:steel_frame", "H": "create:brass_hand", "L": "tfmg:plastic_sheet", "M": "tfmg:electric_motor", "N": "tfmg:n_semiconductor", "Q": "tfmg:p_semiconductor", "T": "tfmg:heavy_plate"},
            "createcasing:railway_deployer",
        ),
        "industrial_colonies:manufacturing/railway/depot": (
            "Fabricate a Railway depot as a heavy receiving table over paired observers, with complementary routing electronics, plastic insulation, a populated board, Brass depot core, and framed base",
            ["TTTT", "COOC", "LNDQ", "FFBF"],
            {"B": "createcasing:brass_depot", "C": "create:railway_casing", "D": "tfmg:coated_circuit_board", "F": "tfmg:steel_frame", "L": "tfmg:plastic_sheet", "N": "tfmg:n_semiconductor", "O": "create:content_observer", "Q": "tfmg:p_semiconductor", "T": "tfmg:heavy_plate"},
            "createcasing:railway_depot",
        ),
        "industrial_colonies:manufacturing/railway/mixer": (
            "Fabricate a Railway mixer as a powered overhead drive above complementary load sensing, a protected routing board, Brass mixer core, sturdy whisk, steel mechanism, and framed base",
            [" MTT", "CNQC", "LDB ", "FWSF"],
            {"B": "createcasing:brass_mixer", "C": "create:railway_casing", "D": "tfmg:coated_circuit_board", "F": "tfmg:steel_frame", "L": "tfmg:plastic_sheet", "M": "tfmg:electric_motor", "N": "tfmg:n_semiconductor", "Q": "tfmg:p_semiconductor", "S": "tfmg:steel_mechanism", "T": "tfmg:heavy_plate", "W": "createmetallurgy:sturdy_whisk"},
            "createcasing:railway_mixer",
        ),
        "industrial_colonies:manufacturing/railway/press": (
            "Fabricate a Railway press as a heavy four-plate crown over twin powered columns, complementary force sensing, protected control board, Brass press core, Railway shell, and framed bed",
            ["TTTT", "MNM ", "LDQB", "FCFF"],
            {"B": "createcasing:brass_press", "C": "create:railway_casing", "D": "tfmg:coated_circuit_board", "F": "tfmg:steel_frame", "L": "tfmg:plastic_sheet", "M": "tfmg:electric_motor", "N": "tfmg:n_semiconductor", "Q": "tfmg:p_semiconductor", "T": "tfmg:heavy_plate"},
            "createcasing:railway_press",
        ),
        "industrial_colonies:v3_createcasing/railway_saw": (
            "Fabricate a Railway saw as a heavy guarded blade drive with twin motors, geared spindle, complementary speed sensing, protected control board, Brass saw core, Railway shell, and framed base",
            [" TT ", "MGQM", "LND ", "FCBF"],
            {"B": "createcasing:brass_mechanical_saw", "C": "create:railway_casing", "D": "tfmg:coated_circuit_board", "F": "tfmg:steel_frame", "G": "create:large_cogwheel", "L": "tfmg:plastic_sheet", "M": "tfmg:electric_motor", "N": "tfmg:n_semiconductor", "Q": "tfmg:p_semiconductor", "T": "tfmg:heavy_plate"},
            "createcasing:railway_mechanical_saw",
        ),
    }
    for recipe_id, (comment, pattern, key, output) in railway.items():
        result[recipe_id] = _mechanical(
            comment=comment, pattern=pattern, key=key, output=output
        )
    if set(result) != MANUFACTURING_REJECT_IDS:
        missing = sorted(MANUFACTURING_REJECT_IDS - set(result))
        extra = sorted(set(result) - MANUFACTURING_REJECT_IDS)
        raise AssertionError(f"internal manufacturing redesign coverage drifted; missing={missing}, extra={extra}")
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
    missing = sorted(MANUFACTURING_REJECT_IDS - set(indexes))
    if missing:
        raise KeyError(f"expected active rejected manufacturing recipes are missing: {missing}")
    for recipe_id, process in redesigns().items():
        recipe = data["recipes"][indexes[recipe_id]]
        for field in _PROCESS_FIELDS:
            recipe.pop(field, None)
        recipe.update(deepcopy(process))


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    errors: list[str] = []
    for recipe_id in sorted(MANUFACTURING_REJECT_IDS):
        if recipe_id not in indexes:
            errors.append(f"missing exact rejected recipe {recipe_id}")
            continue
        recipe = data["recipes"][indexes[recipe_id]]
        if "mekanism:steel_casing" in repr(recipe):
            errors.append(f"{recipe_id} uses retired Mekanism steel casing")
    for recipe_id in sorted(PUMP_COMPACTING_IDS):
        recipe = data["recipes"][indexes[recipe_id]]
        if recipe.get("type") != "compacting" or recipe.get("machine") != RAILWAY_PRESS:
            errors.append(f"{recipe_id} is not Railway compacting")
        if "tfmg:cast_iron_ingot" not in recipe.get("inputs", []):
            # Counted ingredients use a prefix; inspect the complete list below.
            if not any("tfmg:cast_iron_ingot" in value for value in recipe.get("inputs", [])):
                errors.append(f"{recipe_id} lacks cast-iron forging stock")
    for recipe_id in sorted(RAILWAY_ELECTRONICS_IDS):
        recipe = data["recipes"][indexes[recipe_id]]
        if recipe.get("type") != "mechanical_crafting":
            errors.append(f"{recipe_id} is not a mechanical BOM")
        pattern = recipe.get("pattern", [])
        if len(pattern) != 4 or any(not isinstance(row, str) or len(row) != 4 for row in pattern):
            errors.append(f"{recipe_id} is not a valid 4x4 BOM")
        values = set(recipe.get("key", {}).values())
        for required in ("tfmg:plastic_sheet", "tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:coated_circuit_board", "tfmg:steel_frame"):
            if required not in values:
                errors.append(f"{recipe_id} lacks required Railway component {required}")
        if "tfmg:steel_casing" in values:
            errors.append(f"{recipe_id} uses a casing ring instead of a frame")
    centrifuge = data["recipes"][indexes["industrial_colonies:mekanism_nuclear/isotopic_centrifuge"]]
    if centrifuge.get("type") != "mechanical_crafting" or len(centrifuge.get("pattern", [])) != 5:
        errors.append("isotopic centrifuge is not a heavy 5x5 machine BOM")
    heavy = data["recipes"][indexes["industrial_colonies:tfmg_core/heavy_machinery_casing"]]
    if heavy.get("type") != "compacting" or heavy.get("machine") != RAILWAY_PRESS:
        errors.append("heavy machinery casing is not pressure-compacted on Railway machinery")
    return {
        "status": "PASS" if not errors else "FAIL",
        "redesigned": len(MANUFACTURING_REJECT_IDS),
        "railway_electronics": len(RAILWAY_ELECTRONICS_IDS),
        "pump_compacting": len(PUMP_COMPACTING_IDS),
        "errors": errors,
    }
