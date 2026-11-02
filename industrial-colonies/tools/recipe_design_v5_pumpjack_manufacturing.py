#!/usr/bin/env python3
"""Isolated v5 redesigns for the remaining pumpjack/manufacturing rejects.

This module is the final source-side correction pass for these recipes.  It
mutates only the in-memory seed passed to :func:`apply`; the top-level recipe
builder decides when to persist that seed.

The recipes follow the player's manual review notes:

* the Pumpjack Base is a compact 4 x 5 mechanical build;
* pumpjack wear parts move onto the Weathered-Iron manufacturing tier;
* the small connector is pressure-fitted by the Weathered-Iron Press;
* Brass Press and Deployer are real Copper-line sequenced upgrades; and
* the Winding Machine is reduced from a filled 5 x 5 material border to a
  readable 4 x 4 spindle, winding bed, gearbox, and frame.

Every grid is a functional silhouette.  None uses a filled perimeter, a
Mekanism Steel Casing, or repeated Precision Mechanisms as generic difficulty.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
WEATHERED_PRESS = "createcasing:weathered_iron_press"
WEATHERED_GEARBOX = "createcasing:weathered_iron_gearbox"
WEATHERED_STRUCTURE = "create:weathered_iron_block"


REVIEW_NOTES: dict[str, str] = {
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head": (
        "should require rusted iron machines. Mechanical Crafting should do."
    ),
    "industrial_colonies:machine/oil_processing/pumpjack_base": (
        "just compact it and make it a 4x5 recipe"
    ),
    "industrial_colonies:machine/oil_processing/pumpjack_hammer": (
        "very close but its missing a few items"
    ),
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_head": (
        "should require rusted iron machines. Mechanical Crafting should do."
    ),
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector": (
        "should require rusted iron machines. Mechanical Crafting should do."
    ),
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_connector": (
        "should require rusted iron machines mechanical compacting should do."
    ),
    "industrial_colonies:manufacturing/brass_deployer": "too cheap",
    "industrial_colonies:manufacturing/brass_press": "too cheap",
    "industrial_colonies:heavy_industry/winding_machine": (
        "good but maybe a little to complex for a winding machine? idk what it does though."
    ),
}

TARGET_IDS = frozenset(REVIEW_NOTES)

# These two rejected pivot recipes were redesigned in v4, but the umbrella
# Pumpjack review explicitly requires the Weathered-Iron tier for *all* jack
# items.  They are support corrections here so the new connectors do not
# depend on Railway-tier parts and accidentally move petroleum after Digital.
SUPPORT_IDS = frozenset(
    {
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part",
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_part",
    }
)

ALL_REDESIGNED_IDS = TARGET_IDS | SUPPORT_IDS

PUMPJACK_IDS = frozenset(
    recipe_id
    for recipe_id in ALL_REDESIGNED_IDS
    if recipe_id.startswith("industrial_colonies:machine/oil_processing/")
)

BRASS_MACHINE_IDS = frozenset(
    {
        "industrial_colonies:manufacturing/brass_deployer",
        "industrial_colonies:manufacturing/brass_press",
    }
)

COMPACTING_PUMPJACK_IDS = SUPPORT_IDS | {
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_connector"
}

MECHANICAL_PUMPJACK_IDS = frozenset(PUMPJACK_IDS - COMPACTING_PUMPJACK_IDS)

EXPECTED_OUTPUTS = {
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part": (
        "tfmg:large_pumpjack_hammer_part"
    ),
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_part": (
        "2x tfmg:pumpjack_hammer_part"
    ),
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head": (
        "tfmg:large_pumpjack_hammer_head"
    ),
    "industrial_colonies:machine/oil_processing/pumpjack_base": "tfmg:pumpjack_base",
    "industrial_colonies:machine/oil_processing/pumpjack_hammer": "tfmg:pumpjack_hammer",
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_head": (
        "tfmg:pumpjack_hammer_head"
    ),
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector": (
        "tfmg:large_pumpjack_hammer_connector"
    ),
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_connector": (
        "tfmg:pumpjack_hammer_connector"
    ),
    "industrial_colonies:manufacturing/brass_deployer": "createcasing:brass_deployer",
    "industrial_colonies:manufacturing/brass_press": "createcasing:brass_press",
    "industrial_colonies:heavy_industry/winding_machine": "tfmg:winding_machine",
}

PUMPJACK_ORDER = {
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head": 130,
    "industrial_colonies:machine/oil_processing/pumpjack_base": 150,
    "industrial_colonies:machine/oil_processing/pumpjack_hammer": 170,
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_head": 180,
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part": 190,
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector": 200,
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_part": 210,
    "industrial_colonies:machine/oil_processing/pumpjack_hammer_connector": 220,
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


def _mechanical(
    *, comment: str, pattern: list[str], key: dict[str, str], output: str
) -> Recipe:
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
        "machine": WEATHERED_PRESS,
        "heat": "none",
        "output": output,
        "exclusive_output": True,
    }


def _deploy(ingredient: str) -> Recipe:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": COPPER_DEPLOYER,
    }


def _copper_sequence(
    *, comment: str, input_item: str, ingredients: list[str], output: str
) -> Recipe:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "steps": [
            *(_deploy(ingredient) for ingredient in ingredients),
            {"op": "pressing", "machine": COPPER_PRESS},
        ],
        "loops": 1,
        "output": output,
        "exclusive_output": True,
    }


def redesigns() -> dict[str, Recipe]:
    result: dict[str, Recipe] = {
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part": _compacting(
            comment=(
                "Pressure-forge one large walking-beam pivot from a full cast-iron "
                "charge around paired heavy bearing cheeks, a steel load block, and "
                "twin rebar pins on the Weathered-Iron line"
            ),
            inputs=[
                "8x tfmg:cast_iron_ingot",
                "2x tfmg:heavy_plate",
                "tfmg:steel_block",
                "2x tfmg:rebar",
                "4x tfmg:screw",
            ],
            output="tfmg:large_pumpjack_hammer_part",
        ),
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_part": _compacting(
            comment=(
                "Pressure-forge a matched pair of small walking-beam pivots from cast "
                "iron around a steel load spine, heavy bearing cheeks, rebar pins, and "
                "service screws on the Weathered-Iron line"
            ),
            inputs=[
                "4x tfmg:cast_iron_ingot",
                "tfmg:steel_ingot",
                "2x tfmg:heavy_plate",
                "2x tfmg:rebar",
                "4x tfmg:screw",
            ],
            output="2x tfmg:pumpjack_hammer_part",
        ),
        "industrial_colonies:machine/oil_processing/pumpjack_base": _mechanical(
            comment=(
                "Build the compact 4-by-5 oilfield base around twin cast-iron pumps, "
                "one service tank, paired pipe rails, a Brass control housing, a single "
                "precision drive, a Weathered-Iron gearbox, framed bed, and rebar feet"
            ),
            pattern=[
                " M M",
                "ITBI",
                "IPGI",
                "IFFI",
                "FRRF",
            ],
            key={
                "B": "create:brass_casing",
                "F": "tfmg:cast_iron_frame",
                "G": WEATHERED_GEARBOX,
                "I": "tfmg:cast_iron_pipe",
                "M": "tfmg:cast_iron_mechanical_pump",
                "P": "create:precision_mechanism",
                "R": "tfmg:rebar",
                "T": "tfmg:cast_iron_fluid_tank",
            },
            output="tfmg:pumpjack_base",
        ),
        "industrial_colonies:machine/oil_processing/pumpjack_hammer": _mechanical(
            comment=(
                "Fabricate the walking beam as a cast-iron truss over its pivot part, "
                "heavy wear cap, Weathered-Iron drive gearbox, through-shaft, and framed "
                "hanger; these are the few functional parts missing from the prior beam"
            ),
            pattern=[
                " IHI ",
                "ITPTI",
                "TTGTT",
                "  A  ",
                "  F  ",
            ],
            key={
                "A": "create:shaft",
                "F": "tfmg:cast_iron_frame",
                "G": WEATHERED_GEARBOX,
                "H": "tfmg:heavy_plate",
                "I": "tfmg:cast_iron_ingot",
                "P": "tfmg:pumpjack_hammer_part",
                "T": "tfmg:cast_iron_truss",
            },
            output="tfmg:pumpjack_hammer",
        ),
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_head": _mechanical(
            comment=(
                "Mechanically laminate the compact walking-beam head as a cast-iron "
                "shell around a corrosion-resistant Weathered-Iron core, heavy wear "
                "cheeks, and twin rebar tie rods"
            ),
            pattern=[
                " PP ",
                "PBBP",
                " HWH",
                " RR ",
            ],
            key={
                "B": "tfmg:cast_iron_block",
                "H": "tfmg:heavy_plate",
                "P": "tfmg:cast_iron_sheet",
                "R": "tfmg:rebar",
                "W": WEATHERED_STRUCTURE,
            },
            output="tfmg:pumpjack_hammer_head",
        ),
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head": _mechanical(
            comment=(
                "Mechanically laminate the high-inertia head from a broad cast-iron "
                "block and sheet shell around a Weathered-Iron core, full heavy wear "
                "rail, and separated rebar anchors"
            ),
            pattern=[
                " PPP ",
                "PBBBP",
                "BBWBB",
                "HHHHH",
                " R R ",
            ],
            key={
                "B": "tfmg:cast_iron_block",
                "H": "tfmg:heavy_plate",
                "P": "tfmg:cast_iron_sheet",
                "R": "tfmg:rebar",
                "W": WEATHERED_STRUCTURE,
            },
            output="tfmg:large_pumpjack_hammer_head",
        ),
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_connector": _compacting(
            comment=(
                "Pressure-fit paired Brass lugs around the small walking-beam pivot, "
                "then close its rebar pin and service screws in the Weathered-Iron Press"
            ),
            inputs=[
                "tfmg:pumpjack_hammer_part",
                "2x create:brass_sheet",
                "tfmg:rebar",
                "2x tfmg:screw",
            ],
            output="tfmg:pumpjack_hammer_connector",
        ),
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector": _mechanical(
            comment=(
                "Build the large pivot yoke around its hammer part with paired Brass "
                "lugs, rebar pins, heavy cheeks, Weathered-Iron saddle, and exposed "
                "service fasteners"
            ),
            pattern=[
                " BB  ",
                "R L R",
                " HWH ",
                " S S ",
            ],
            key={
                "B": "create:brass_sheet",
                "H": "tfmg:heavy_plate",
                "L": "tfmg:large_pumpjack_hammer_part",
                "R": "tfmg:rebar",
                "S": "tfmg:screw",
                "W": WEATHERED_STRUCTURE,
            },
            output="tfmg:large_pumpjack_hammer_connector",
        ),
        "industrial_colonies:manufacturing/brass_deployer": _copper_sequence(
            comment=(
                "Upgrade the complete Copper Deployer into a precision Brass workcell "
                "with its Brass shell and hand, one precision transmission, powered "
                "actuator, populated control board, transistor, tube, and insulation"
            ),
            input_item="createcasing:copper_deployer",
            ingredients=[
                "create:brass_casing",
                "create:brass_hand",
                "create:precision_mechanism",
                "tfmg:electric_motor",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
                "create:electron_tube",
                "tfmg:plastic_sheet",
            ],
            output="createcasing:brass_deployer",
        ),
        "industrial_colonies:manufacturing/brass_press": _copper_sequence(
            comment=(
                "Upgrade the complete Copper Press into a precision Brass workcell with "
                "its Brass shell, heavy ram plate, one precision transmission, powered "
                "drive, capacitor bank, populated control board, tube, and insulation"
            ),
            input_item="createcasing:copper_press",
            ingredients=[
                "create:brass_casing",
                "tfmg:heavy_plate",
                "create:precision_mechanism",
                "tfmg:electric_motor",
                "tfmg:capacitor_item",
                "tfmg:coated_circuit_board",
                "create:electron_tube",
                "tfmg:plastic_sheet",
            ],
            output="createcasing:brass_press",
        ),
        "industrial_colonies:heavy_industry/winding_machine": _mechanical(
            comment=(
                "Build the Winding Machine as a compact spindle frame: two shafts and "
                "Copper feed spools over one steel drive, one heavy casing, guarded "
                "cheeks, and four serviceable frame feet—without downstream electronics"
            ),
            pattern=[
                " FAF",
                "CAGC",
                "HMAH",
                " F F",
            ],
            key={
                "A": "create:shaft",
                "C": "tfmg:copper_spool",
                "F": "tfmg:steel_frame",
                "G": "tfmg:steel_mechanism",
                "H": "tfmg:heavy_plate",
                "M": "tfmg:heavy_machinery_casing",
            },
            output="tfmg:winding_machine",
        ),
    }

    if set(result) != ALL_REDESIGNED_IDS:
        missing = sorted(ALL_REDESIGNED_IDS - set(result))
        extra = sorted(set(result) - ALL_REDESIGNED_IDS)
        raise AssertionError(
            f"internal v5 redesign coverage drifted; missing={missing}, extra={extra}"
        )
    for recipe_id, order in PUMPJACK_ORDER.items():
        result[recipe_id]["phase"] = "Steel & Petroleum"
        result[recipe_id]["order"] = order
    for recipe_id, recipe in result.items():
        if recipe.get("output") != EXPECTED_OUTPUTS[recipe_id]:
            raise AssertionError(f"v5 redesign changed output identity: {recipe_id}")
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


def _filled_perimeter(pattern: list[str]) -> bool:
    if len(pattern) < 2 or not pattern or not pattern[0]:
        return False
    width = len(pattern[0])
    if any(not isinstance(row, str) or len(row) != width for row in pattern):
        return False
    return (
        all(character != " " for character in pattern[0])
        and all(character != " " for character in pattern[-1])
        and all(row[0] != " " and row[-1] != " " for row in pattern)
    )


def apply(data: dict[str, Any]) -> None:
    """Apply only the nine v5 proposals to an in-memory managed seed."""

    indexes = _index(data)
    missing = sorted(ALL_REDESIGNED_IDS - set(indexes))
    if missing:
        raise KeyError(f"expected active v5 rejection targets are missing: {missing}")
    for recipe_id, process in redesigns().items():
        recipe = data["recipes"][indexes[recipe_id]]
        for field in _PROCESS_FIELDS:
            recipe.pop(field, None)
        recipe.update(deepcopy(process))


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    errors: list[str] = []
    for recipe_id in sorted(ALL_REDESIGNED_IDS):
        if recipe_id not in indexes:
            errors.append(f"missing exact v5 redesign target {recipe_id}")
            continue
        recipe = data["recipes"][indexes[recipe_id]]
        if recipe.get("output") != EXPECTED_OUTPUTS[recipe_id]:
            errors.append(f"{recipe_id} changed output identity")
        text = repr(recipe)
        if "mekanism:steel_casing" in text:
            errors.append(f"{recipe_id} uses retired Mekanism Steel Casing")
        if text.count("create:precision_mechanism") > 1:
            errors.append(f"{recipe_id} repeats Precision Mechanisms as generic cost")
        pattern = recipe.get("pattern")
        if isinstance(pattern, list) and _filled_perimeter(pattern):
            errors.append(f"{recipe_id} fell back to a filled perimeter ring")

    if PUMPJACK_IDS <= set(indexes):
        base = data["recipes"][indexes["industrial_colonies:machine/oil_processing/pumpjack_base"]]
        if base.get("type") != "mechanical_crafting" or len(base.get("pattern", [])) != 5:
            errors.append("pumpjack base is not mechanical crafting with five rows")
        if any(len(row) != 4 for row in base.get("pattern", [])):
            errors.append("pumpjack base is not the requested compact 4-by-5 grid")

        small_connector = data["recipes"][
            indexes["industrial_colonies:machine/oil_processing/pumpjack_hammer_connector"]
        ]
        if (
            small_connector.get("type") != "compacting"
            or small_connector.get("machine") != WEATHERED_PRESS
        ):
            errors.append("small pumpjack connector is not Weathered-Iron compacting")

        for recipe_id in sorted(MECHANICAL_PUMPJACK_IDS):
            recipe = data["recipes"][indexes[recipe_id]]
            if recipe.get("type") != "mechanical_crafting":
                errors.append(f"{recipe_id} is not the requested mechanical build")

        weathered_markers = {WEATHERED_PRESS, WEATHERED_GEARBOX, WEATHERED_STRUCTURE}
        for recipe_id in sorted(PUMPJACK_IDS):
            recipe = data["recipes"][indexes[recipe_id]]
            if recipe.get("phase") != "Steel & Petroleum":
                errors.append(f"{recipe_id} escaped the Steel & Petroleum phase")
            if not any(marker in repr(recipe) for marker in weathered_markers):
                errors.append(f"{recipe_id} does not require the Weathered-Iron tier")

    for recipe_id in sorted(BRASS_MACHINE_IDS):
        if recipe_id not in indexes:
            continue
        recipe = data["recipes"][indexes[recipe_id]]
        deployments = [
            step for step in recipe.get("steps", []) if step.get("op") == "deploying"
        ]
        if recipe.get("type") != "sequenced_assembly" or len(deployments) != 8:
            errors.append(f"{recipe_id} is not an eight-component precision upgrade")
        if any(step.get("machine") != COPPER_DEPLOYER for step in deployments):
            errors.append(f"{recipe_id} left the Copper Deployer line")
        if recipe.get("steps", [])[-1:] != [{"op": "pressing", "machine": COPPER_PRESS}]:
            errors.append(f"{recipe_id} is not sealed by the Copper Press")
        ingredients = [step.get("ingredient") for step in deployments]
        if len(ingredients) != len(set(ingredients)):
            errors.append(f"{recipe_id} repeats filler deployments")

    winding_id = "industrial_colonies:heavy_industry/winding_machine"
    if winding_id in indexes:
        winding = data["recipes"][indexes[winding_id]]
        pattern = winding.get("pattern", [])
        occupied = sum(character != " " for row in pattern for character in row)
        if (
            winding.get("type") != "mechanical_crafting"
            or len(pattern) != 4
            or any(len(row) != 4 for row in pattern)
        ):
            errors.append("winding machine is not the simplified 4-by-4 mechanical build")
        if occupied > 14:
            errors.append("winding machine remains excessively dense")
        if "tfmg:electric_motor" in repr(winding):
            errors.append("winding machine consumes a downstream electric motor")

    return {
        "status": "PASS" if not errors else "FAIL",
        "reviewed_redesigns": len(TARGET_IDS),
        "support_corrections": len(SUPPORT_IDS),
        "redesigned": len(ALL_REDESIGNED_IDS),
        "pumpjack": len(PUMPJACK_IDS),
        "brass_sequences": len(BRASS_MACHINE_IDS),
        "errors": errors,
    }
