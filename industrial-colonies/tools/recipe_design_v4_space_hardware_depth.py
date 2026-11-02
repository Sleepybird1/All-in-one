#!/usr/bin/env python3
"""Deepen the remaining rejected spacecraft and life-support hardware.

This source-only cohort covers every active second-pass rejection in the
remaining space-hardware list.  Six cards were rejected as too cheap and
fourteen explicitly requested plastic, semiconductors, and circuit components.
The redesigned routes form one physical progression:

* pressure hardware and oxygen controls establish survivable habitats;
* mount, nozzle, RCS, staging, vectoring, and booster parts form a propulsion
  system instead of sharing a generic expensive bill of materials;
* Desh, Ostrum, and Calorite engines retain a real planetary upgrade ladder;
* EVA hardware and photovoltaic cells use compact production sequences; and
* warp memory and the crystal driver remain genuinely interstellar machines.

``apply`` is deterministic and idempotent.  It mutates only these managed
source cards and never edits review state, generated KJSGen projects, or the
live pack.  Reconciliation is responsible for returning changed cards to
Pending; this module never auto-approves them.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

REFINED_RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
REFINED_RADIANCE_PRESS = "createcasing:refined_radiance_press"
COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"

TOO_CHEAP_NOTE = "Too cheap — make it more complex."
ELECTRONICS_NOTE = (
    "Needs more electronics: plastic, semiconductors, and circuit components."
)

REJECTION_CONTRACTS = {
    "industrial_colonies:space/life_support/large_gas_tank": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": (
            "sha256:1d9cbcc153c883dfe6e81a393eacd61543a4c246246ef6f2cb84df3909c78fcc"
        ),
    },
    "industrial_colonies:space/life_support/oxygen_loader": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": (
            "sha256:56432e7d8d4cc6291147dac573f26f44c9d5a2aae9ae4b9a611f3205d8f1e4d7"
        ),
    },
    "industrial_colonies:space/life_support/oxygen_sensor": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": (
            "sha256:99baaf6b7cd3d17a2ab053f394eba54ee2f79d59a84079bb4b3d55affc86f784"
        ),
    },
    "industrial_colonies:space/propulsion/engine_nozzle": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:137c580dc875a15a0bcebac6b2b96eca57c24e0bce0d7040fe50e1eb38f91226"
        ),
    },
    "industrial_colonies:space/propulsion/thruster_mount": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": (
            "sha256:f23dbe7790035fbd46b31d187ec59594654a326df34c9d156fb5343e381b57bc"
        ),
    },
    "industrial_colonies:space_coverage/booster_thruster": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:d209f4e5f3f601ef62142b3863969f8d7bbf84cf69278cede2899204f5dfc755"
        ),
    },
    "industrial_colonies:space_coverage/crystal_driver": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": (
            "sha256:fccd759e0cd49a76001a2dc89bde684ba758a9974f037f3190c0e8bfa7e93985"
        ),
    },
    "industrial_colonies:space_coverage/desh_engine": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:664debbe2fce60196495984c8f9ca5ef1c8fa55325f868ba4145372d0d27ead3"
        ),
    },
    "industrial_colonies:space_coverage/gyroscopic_propeller_bearing": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:2b3edf6260882b029cd34ab980f97631333b377ed853a367d9cd0729b02419c4"
        ),
    },
    "industrial_colonies:space_coverage/magnetic_stabilizer": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:b76a8fcdf3e6e4020dbc2a0a70a9cd4ea65338ae91ed3955b13394bb218f23ae"
        ),
    },
    "industrial_colonies:space_coverage/rcs_thruster": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:e5e7d1da7a194e74619fd8a1f26909157ae9c06667e6f0deb1b6e65acca4ca28"
        ),
    },
    "industrial_colonies:space_coverage/rocket_thruster": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:3065f95f39b585185548f46a26d86233566e5e739f2284ba3affc917492c7cbf"
        ),
    },
    "industrial_colonies:space_coverage/separator": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:211f83470387d051a74dbffd6b4a07cc7030a136b02fbb7f0ef2be81a031f9f3"
        ),
    },
    "industrial_colonies:space_coverage/vector_thruster": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:97894b084a2844b666b6c4a7451273b40c7c306561e098a895685fb0a9cb68ae"
        ),
    },
    "industrial_colonies:space_coverage/warp_memory_card": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": (
            "sha256:df585e6fc1432f4e58898b5ac52f4fb04cc41ce62f63d96df6a02504ece3ad92"
        ),
    },
    "industrial_colonies:space_hardware/calorite_engine": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:cdaa7f82654d7fe86774e7f7e058d62cbe60c5c7fc97a72b8c93ee8365e54eff"
        ),
    },
    "industrial_colonies:space_hardware/copper_anchor_boots": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:31f7f4b9ba98ae15149ca6ea200f1952c3381d83fddff7943fcb03dfecc68e97"
        ),
    },
    "industrial_colonies:space_hardware/copper_leg_thrusters": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:18f44b9e83e3f55abe9551e3391dc2f541f1191613bdbe20a5980b948f73c9ab"
        ),
    },
    "industrial_colonies:space_hardware/ostrum_engine": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:636c9565bf337d0db3d7a9a524b1528cc1025583b1399c43ba1d27dcb8d275a4"
        ),
    },
    "industrial_colonies:space_hardware/photovoltaic_etrium_cell": {
        "note": ELECTRONICS_NOTE,
        "cardSha256": (
            "sha256:6062854d188e487d3502c033c339e686f2ac0144e9a3f98b859e91bdafd74f9c"
        ),
    },
}

REDESIGNED_IDS = frozenset(REJECTION_CONTRACTS)
TOO_CHEAP_IDS = frozenset(
    recipe_id
    for recipe_id, contract in REJECTION_CONTRACTS.items()
    if contract["note"] == TOO_CHEAP_NOTE
)
NEEDS_ELECTRONICS_IDS = REDESIGNED_IDS - TOO_CHEAP_IDS

GRID_IDS = frozenset(
    {
        "industrial_colonies:space/life_support/large_gas_tank",
        "industrial_colonies:space/life_support/oxygen_loader",
        "industrial_colonies:space/propulsion/engine_nozzle",
        "industrial_colonies:space/propulsion/thruster_mount",
        "industrial_colonies:space_coverage/booster_thruster",
        "industrial_colonies:space_coverage/crystal_driver",
        "industrial_colonies:space_coverage/gyroscopic_propeller_bearing",
    }
)
SEQUENCE_IDS = REDESIGNED_IDS - GRID_IDS

COPPER_SEQUENCE_IDS = frozenset(
    {
        "industrial_colonies:space_hardware/copper_anchor_boots",
        "industrial_colonies:space_hardware/copper_leg_thrusters",
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
        raise KeyError(f"expected active rejected recipe is missing: {recipe_id}")
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
    deployer: str = REFINED_RADIANCE_DEPLOYER,
    press: str = REFINED_RADIANCE_PRESS,
    loops: int = 1,
) -> Recipe:
    if not 6 <= len(ingredients) <= 7:
        raise ValueError("space-hardware sequences require six or seven deployments")
    if loops not in {1, 2}:
        raise ValueError("space-hardware sequences allow one or two justified loops")
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "steps": [*(_deploy(item, deployer) for item in ingredients), _press(press)],
        "loops": loops,
        "output": output,
        "exclusive_output": True,
    }


def _grid(
    *,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
) -> Recipe:
    if len(pattern) != 5 or any(len(row) != 5 for row in pattern):
        raise ValueError("large space hardware requires an explicit 5x5 silhouette")
    used = set("".join(pattern)) - {" "}
    if used != set(key):
        raise ValueError(
            f"grid symbols do not match key: used={sorted(used)}, key={sorted(key)}"
        )
    return {
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "exclusive_output": True,
    }


def _designs() -> dict[str, Recipe]:
    return {
        "industrial_colonies:space/life_support/large_gas_tank": _grid(
            comment=(
                "Stack two tested gas tanks in a heavy pressure tower: a steel valve "
                "and smart manifold join the vessels, plastic standoffs isolate them, "
                "and a coated TFMG board plus capacitor supervise the ultimate "
                "chemical-tank base"
            ),
            pattern=["  V  ", " HPH ", "HLGLH", "H G H", "FBUCF"],
            key={
                "V": "tfmg:steel_fluid_valve",
                "H": "tfmg:heavy_plate",
                "P": "tfmg:steel_smart_fluid_pipe",
                "L": "tfmg:plastic_sheet",
                "G": "ad_astra:gas_tank",
                "F": "tfmg:steel_frame",
                "B": "tfmg:coated_circuit_board",
                "U": "mekanism:ultimate_chemical_tank",
                "C": "tfmg:capacitor_item",
            },
            output="ad_astra:large_gas_tank",
        ),
        "industrial_colonies:space/life_support/oxygen_loader": _grid(
            comment=(
                "Raise a real oxygen-loading tower: fan and smart-pipe header feed a "
                "valved rotary condenser, paired gas tanks flank the electric pump, "
                "and a plastic-isolated etched board, capacitors, and advanced "
                "controller regulate the heavy base"
            ),
            pattern=["  F  ", " PVP ", "H L H", "TBEAT", "HCUCH"],
            key={
                "F": "ad_astra:fan",
                "P": "tfmg:steel_smart_fluid_pipe",
                "V": "tfmg:steel_fluid_valve",
                "H": "tfmg:heavy_plate",
                "L": "mekanism:rotary_condensentrator",
                "T": "ad_astra:gas_tank",
                "B": "tfmg:etched_circuit_board",
                "E": "tfmg:electric_pump",
                "A": "tfmg:plastic_sheet",
                "C": "tfmg:capacitor_item",
                "U": "mekanism:advanced_control_circuit",
            },
            output="ad_astra:oxygen_loader",
        ),
        "industrial_colonies:space/propulsion/engine_nozzle": _grid(
            comment=(
                "Form two actively monitored titanium nozzle throats around a valved "
                "engine-pipe manifold; a plastic-isolated etched board and paired "
                "capacitors instrument the steel load mechanism before the two outlet "
                "pipes are attached"
            ),
            pattern=[" T T ", "HPVPH", " LBL ", "HCMCH", " P P "],
            key={
                "T": "rocketnautics:titanium_alloy_sheet",
                "H": "tfmg:heavy_plate",
                "P": "rocketnautics:engine_pipes",
                "V": "tfmg:steel_fluid_valve",
                "L": "tfmg:plastic_sheet",
                "B": "tfmg:etched_circuit_board",
                "C": "tfmg:capacitor_item",
                "M": "tfmg:steel_mechanism",
            },
            output="2x rocketnautics:engine_nozzle",
        ),
        "industrial_colonies:space/propulsion/thruster_mount": _grid(
            comment=(
                "Build a load-bearing U-frame beneath a transformer and advanced "
                "computer: plastic standoffs and a capacitor isolate the etched "
                "controller, while engine pipes, hose anchor, nozzle, steel mechanism, "
                "and ultimate interlock occupy their physical service bays"
            ),
            pattern=[" TCB ", "FPLPF", "H R H", "F E F", "FUNMF"],
            key={
                "T": "tfmg:transformer",
                "C": "computercraft:computer_advanced",
                "B": "tfmg:etched_circuit_board",
                "F": "tfmg:steel_frame",
                "P": "tfmg:plastic_sheet",
                "L": "tfmg:capacitor_item",
                "H": "tfmg:heavy_plate",
                "R": "rocketnautics:engine_pipes",
                "E": "rocketnautics:engine_nozzle",
                "U": "mekanism:ultimate_control_circuit",
                "N": "rocketnautics:hose_anchor",
                "M": "tfmg:steel_mechanism",
            },
            output="rocketnautics:thruster_mount",
        ),
        "industrial_colonies:space_coverage/booster_thruster": _grid(
            comment=(
                "Stack the booster down its true centerline: valve, feed pipes, tank, "
                "titanium casing, completed rocket thruster, and terminal nozzle; a "
                "plastic-isolated etched controller with paired capacitors occupies "
                "the side instrumentation bay"
            ),
            pattern=["  V  ", "HPBPH", "HCTCH", "LARAL", "H N H"],
            key={
                "V": "tfmg:steel_fluid_valve",
                "H": "tfmg:heavy_plate",
                "P": "rocketnautics:engine_pipes",
                "B": "tfmg:etched_circuit_board",
                "C": "tfmg:steel_fluid_tank",
                "T": "rocketnautics:titanium_casing",
                "L": "tfmg:plastic_sheet",
                "A": "tfmg:capacitor_item",
                "R": "rocketnautics:rocket_thruster",
                "N": "rocketnautics:titanium_nozzle",
            },
            output="rocketnautics:booster_thruster",
        ),
        "industrial_colonies:space_coverage/gyroscopic_propeller_bearing": _grid(
            comment=(
                "Build the bearing as a vertical attitude stack: gimbal references "
                "sit above plastic-isolated capacitor control, opposed magnetic "
                "stabilizers flank the etched board, and a TFMG motor drives the "
                "mechanical bearing through steel-frame supports"
            ),
            pattern=[" GSG ", "FPCPF", "FMBMF", "F E F", "  R  "],
            key={
                "G": "simulated:gyroscopic_mechanism",
                "S": "simulated:gimbal_sensor",
                "F": "tfmg:steel_frame",
                "P": "tfmg:plastic_sheet",
                "C": "tfmg:capacitor_item",
                "M": "rocketnautics:magnetic_stabilizer",
                "B": "tfmg:etched_circuit_board",
                "E": "tfmg:electric_motor",
                "R": "create:mechanical_bearing",
            },
            output="aeronautics:gyroscopic_propeller_bearing",
        ),
        "industrial_colonies:space_coverage/crystal_driver": _grid(
            comment=(
                "Build the interstellar field driver as a layered control core: "
                "magnetic stabilizers hold the entangled anchor above the warp crystal, "
                "Moon Crystals and encoded memory flank the navigation computer, and "
                "TFMG electronics, plastic isolation, titanium, late alloy, and "
                "ultimate control close the power stage"
            ),
            pattern=[" GQG ", "TPWPT", "MCNCM", "REXER", " AUA "],
            key={
                "G": "rocketnautics:magnetic_stabilizer",
                "Q": "ae2:quantum_entangled_singularity",
                "T": "tfmg:transformer",
                "P": "tfmg:plastic_sheet",
                "W": "cosmowarp:warp_crystal",
                "M": "cosmowarp:moon_crystal",
                "C": "cosmowarp:memory_card",
                "N": "industrial_colonies:interstellar_navigation_computer",
                "R": "rocketnautics:titanium_alloy_sheet",
                "E": "tfmg:etched_circuit_board",
                "X": "tfmg:capacitor_item",
                "A": "allthemodium:unobtainium_vibranium_alloy_ingot",
                "U": "mekanism:ultimate_control_circuit",
            },
            output="cosmowarp:crystal_driver",
        ),
        "industrial_colonies:space/life_support/oxygen_sensor": _sequence(
            comment=(
                "Turn tinted glass into a calibrated oxygen sampling head with a fan, "
                "rubber seal, plastic flow channel, coated TFMG board, transistor "
                "amplifier, capacitor filter, and calculation processor"
            ),
            input_item="minecraft:tinted_glass",
            ingredients=[
                "ad_astra:fan",
                "tfmg:rubber_sheet",
                "tfmg:plastic_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "ae2:calculation_processor",
            ],
            output="ad_astra:oxygen_sensor",
        ),
        "industrial_colonies:space_coverage/desh_engine": _sequence(
            comment=(
                "Refit the steel engine for lunar service with Desh hot-section plate, "
                "a circulation fan, electromagnetic drive, plastic wiring isolation, "
                "coated TFMG controller, transistor ignition, and elite supervision"
            ),
            input_item="ad_astra:steel_engine",
            ingredients=[
                "ad_astra:desh_plate",
                "ad_astra:fan",
                "tfmg:electromagnetic_coil",
                "tfmg:plastic_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
                "mekanism:elite_control_circuit",
            ],
            output="ad_astra:desh_engine",
        ),
        "industrial_colonies:space_coverage/magnetic_stabilizer": _sequence(
            comment=(
                "Instrument the titanium stabilizer shell with opposed TFMG field "
                "coils, a gyroscopic reference, calculation processor, etched field "
                "board, transistor driver, and plastic isolation"
            ),
            input_item="rocketnautics:titanium_casing",
            ingredients=[
                "tfmg:electromagnetic_coil",
                "simulated:gyroscopic_mechanism",
                "tfmg:electromagnetic_coil",
                "ae2:calculation_processor",
                "tfmg:etched_circuit_board",
                "tfmg:transistor_item",
                "tfmg:plastic_sheet",
            ],
            output="rocketnautics:magnetic_stabilizer",
        ),
        "industrial_colonies:space_coverage/rcs_thruster": _sequence(
            comment=(
                "Convert a copper nozzle into a closed-loop attitude jet with a hose "
                "anchor, electric metering pump, TFMG potentiometer, coated controller, "
                "transistor valve driver, plastic insulation, and titanium heat shield"
            ),
            input_item="rocketnautics:copper_nozzle",
            ingredients=[
                "rocketnautics:hose_anchor",
                "tfmg:electric_pump",
                "tfmg:potentiometer",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
                "tfmg:plastic_sheet",
                "rocketnautics:titanium_alloy_sheet",
            ],
            output="rocketnautics:rcs_thruster",
        ),
        "industrial_colonies:space_coverage/rocket_thruster": _sequence(
            comment=(
                "Populate the completed mount with its nozzle, cycle pipes, TFMG "
                "electric turbopump and steel timing mechanism, then install an etched "
                "controller, capacitor buffer, and plastic wiring barrier"
            ),
            input_item="rocketnautics:thruster_mount",
            ingredients=[
                "rocketnautics:engine_nozzle",
                "rocketnautics:engine_pipes",
                "tfmg:electric_pump",
                "tfmg:steel_mechanism",
                "tfmg:etched_circuit_board",
                "tfmg:capacitor_item",
                "tfmg:plastic_sheet",
            ],
            output="rocketnautics:rocket_thruster",
        ),
        "industrial_colonies:space_coverage/separator": _sequence(
            comment=(
                "Build the staging plane around a controllable clutch by installing "
                "opposed separator charges and titanium break sheets, then add a "
                "plastic-isolated coated controller and transistor firing switch"
            ),
            input_item="create:clutch",
            ingredients=[
                "rocketnautics:separator_charge",
                "rocketnautics:titanium_alloy_sheet",
                "rocketnautics:separator_charge",
                "rocketnautics:titanium_alloy_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
                "tfmg:plastic_sheet",
            ],
            output="rocketnautics:separator",
        ),
        "industrial_colonies:space_coverage/vector_thruster": _sequence(
            comment=(
                "Give the rocket thruster a closed-loop vector stage with a gimbal "
                "sensor, gyroscopic reference, TFMG motor, calculation processor, "
                "coated control board, capacitor buffer, and plastic pivot isolation"
            ),
            input_item="rocketnautics:rocket_thruster",
            ingredients=[
                "simulated:gimbal_sensor",
                "simulated:gyroscopic_mechanism",
                "tfmg:electric_motor",
                "ae2:calculation_processor",
                "tfmg:coated_circuit_board",
                "tfmg:capacitor_item",
                "tfmg:plastic_sheet",
            ],
            output="rocketnautics:vector_thruster",
        ),
        "industrial_colonies:space_coverage/warp_memory_card": _sequence(
            comment=(
                "Encode a blank ME pattern as interstellar route memory by installing "
                "an etched TFMG controller, engineering processor, transistor and "
                "capacitor signal stages, Moon Crystal reference, plastic dielectric, "
                "and titanium radiation shield"
            ),
            input_item="ae2:blank_pattern",
            ingredients=[
                "tfmg:etched_circuit_board",
                "ae2:engineering_processor",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "cosmowarp:moon_crystal",
                "tfmg:plastic_sheet",
                "rocketnautics:titanium_sheet",
            ],
            output="cosmowarp:memory_card",
        ),
        "industrial_colonies:space_hardware/ostrum_engine": _sequence(
            comment=(
                "Upgrade the lunar engine with Ostrum hot-section plate, a fresh fan, "
                "magnetic bracing, plastic harness, etched TFMG control board, "
                "capacitor ignition buffer, and ultimate supervision"
            ),
            input_item="ad_astra:desh_engine",
            ingredients=[
                "ad_astra:ostrum_plate",
                "ad_astra:fan",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:plastic_sheet",
                "tfmg:etched_circuit_board",
                "tfmg:capacitor_item",
                "mekanism:ultimate_control_circuit",
            ],
            output="ad_astra:ostrum_engine",
        ),
        "industrial_colonies:space_hardware/calorite_engine": _sequence(
            comment=(
                "Rebuild the Martian engine's final hot section with Calorite plate, "
                "titanium nozzle, TFMG turbine blade, magnetic stabilizer, plastic "
                "isolation, etched flight board, and capacitor pulse stage"
            ),
            input_item="ad_astra:ostrum_engine",
            ingredients=[
                "ad_astra:calorite_plate",
                "rocketnautics:titanium_nozzle",
                "tfmg:turbine_blade",
                "rocketnautics:magnetic_stabilizer",
                "tfmg:plastic_sheet",
                "tfmg:etched_circuit_board",
                "tfmg:capacitor_item",
            ],
            output="ad_astra:calorite_engine",
        ),
        "industrial_colonies:space_hardware/copper_anchor_boots": _sequence(
            comment=(
                "Laminate iron boots with rubber soles, magnetic anchors, titanium "
                "reinforcement and copper grounding, then add a plastic-isolated "
                "coated board and transistor field switch on the Copper line"
            ),
            input_item="minecraft:iron_boots",
            ingredients=[
                "tfmg:rubber_sheet",
                "tfmg:magnetic_alloy_sheet",
                "rocketnautics:titanium_alloy_sheet",
                "create:copper_sheet",
                "tfmg:plastic_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
            ],
            output="rocketnautics:copper_anchor_boots",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:space_hardware/copper_leg_thrusters": _sequence(
            comment=(
                "Fit iron leggings with paired copper nozzles, a hose anchor, and TFMG "
                "metering pump, then close the harness around a plastic-isolated coated "
                "controller and transistor valve driver on the Copper line"
            ),
            input_item="minecraft:iron_leggings",
            ingredients=[
                "rocketnautics:copper_nozzle",
                "rocketnautics:hose_anchor",
                "tfmg:electric_pump",
                "rocketnautics:copper_nozzle",
                "tfmg:plastic_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
            ],
            output="rocketnautics:copper_leg_thrusters",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:space_hardware/photovoltaic_etrium_cell": _sequence(
            comment=(
                "Print two photovoltaic wafers from TFMG silicon by laying copper "
                "collection traces, transistor switching, a coated control strip, "
                "plastic dielectric, Desh backing, and blue-glass cover in two loops"
            ),
            input_item="tfmg:silicon_ingot",
            ingredients=[
                "tfmg:copper_wire",
                "tfmg:transistor_item",
                "tfmg:coated_circuit_board",
                "tfmg:plastic_sheet",
                "ad_astra:desh_plate",
                "minecraft:blue_stained_glass",
            ],
            output="2x ad_astra:photovoltaic_etrium_cell",
            loops=2,
        ),
    }


def apply(data: dict[str, Any]) -> None:
    designs = _designs()
    if set(designs) != set(REDESIGNED_IDS):
        raise ValueError("space-hardware design table no longer matches contracts")
    indexes = _index(data)
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        raise KeyError(f"expected active rejected recipes are missing: {missing}")
    for recipe_id, process in designs.items():
        _replace(data, recipe_id, process)
    audit(data)


def _sequence_ingredients(recipe: Recipe) -> list[str]:
    return [
        step["ingredient"]
        for step in recipe.get("steps", [])
        if isinstance(step, dict) and step.get("op") == "deploying"
    ]


def _all_ingredients(recipe: Recipe) -> set[str]:
    if recipe.get("type") == "mechanical_crafting":
        return set(recipe.get("key", {}).values())
    return set(_sequence_ingredients(recipe)) | {str(recipe.get("input", ""))}


def _is_filled_perimeter(pattern: list[str]) -> bool:
    return bool(pattern) and (
        all(char != " " for char in pattern[0])
        and all(char != " " for char in pattern[-1])
        and all(row[0] != " " and row[-1] != " " for row in pattern)
    )


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    errors: list[str] = []
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        errors.append(f"missing space-hardware redesigns: {missing}")
    recipes = data.get("recipes", [])

    functional_signatures = {
        "industrial_colonies:space/life_support/large_gas_tank": {
            "ad_astra:gas_tank",
            "mekanism:ultimate_chemical_tank",
            "tfmg:steel_fluid_valve",
        },
        "industrial_colonies:space/life_support/oxygen_loader": {
            "ad_astra:fan",
            "mekanism:rotary_condensentrator",
            "tfmg:electric_pump",
            "ad_astra:gas_tank",
        },
        "industrial_colonies:space/life_support/oxygen_sensor": {
            "minecraft:tinted_glass",
            "ad_astra:fan",
        },
        "industrial_colonies:space/propulsion/engine_nozzle": {
            "rocketnautics:engine_pipes",
            "rocketnautics:titanium_alloy_sheet",
            "tfmg:steel_fluid_valve",
        },
        "industrial_colonies:space/propulsion/thruster_mount": {
            "rocketnautics:engine_nozzle",
            "rocketnautics:engine_pipes",
            "rocketnautics:hose_anchor",
        },
        "industrial_colonies:space_coverage/booster_thruster": {
            "rocketnautics:rocket_thruster",
            "rocketnautics:titanium_nozzle",
            "tfmg:steel_fluid_tank",
        },
        "industrial_colonies:space_coverage/crystal_driver": {
            "cosmowarp:warp_crystal",
            "cosmowarp:memory_card",
            "industrial_colonies:interstellar_navigation_computer",
            "allthemodium:unobtainium_vibranium_alloy_ingot",
        },
        "industrial_colonies:space_coverage/desh_engine": {
            "ad_astra:steel_engine",
            "ad_astra:desh_plate",
            "tfmg:electromagnetic_coil",
        },
        "industrial_colonies:space_coverage/gyroscopic_propeller_bearing": {
            "create:mechanical_bearing",
            "simulated:gimbal_sensor",
            "rocketnautics:magnetic_stabilizer",
        },
        "industrial_colonies:space_coverage/magnetic_stabilizer": {
            "rocketnautics:titanium_casing",
            "tfmg:electromagnetic_coil",
            "simulated:gyroscopic_mechanism",
        },
        "industrial_colonies:space_coverage/rcs_thruster": {
            "rocketnautics:copper_nozzle",
            "rocketnautics:hose_anchor",
            "tfmg:electric_pump",
        },
        "industrial_colonies:space_coverage/rocket_thruster": {
            "rocketnautics:thruster_mount",
            "rocketnautics:engine_nozzle",
            "tfmg:electric_pump",
        },
        "industrial_colonies:space_coverage/separator": {
            "create:clutch",
            "rocketnautics:separator_charge",
            "rocketnautics:titanium_alloy_sheet",
        },
        "industrial_colonies:space_coverage/vector_thruster": {
            "rocketnautics:rocket_thruster",
            "simulated:gimbal_sensor",
            "tfmg:electric_motor",
        },
        "industrial_colonies:space_coverage/warp_memory_card": {
            "ae2:blank_pattern",
            "cosmowarp:moon_crystal",
            "rocketnautics:titanium_sheet",
        },
        "industrial_colonies:space_hardware/calorite_engine": {
            "ad_astra:ostrum_engine",
            "ad_astra:calorite_plate",
            "rocketnautics:magnetic_stabilizer",
        },
        "industrial_colonies:space_hardware/copper_anchor_boots": {
            "minecraft:iron_boots",
            "tfmg:magnetic_alloy_sheet",
            "tfmg:rubber_sheet",
        },
        "industrial_colonies:space_hardware/copper_leg_thrusters": {
            "minecraft:iron_leggings",
            "rocketnautics:copper_nozzle",
            "rocketnautics:hose_anchor",
        },
        "industrial_colonies:space_hardware/ostrum_engine": {
            "ad_astra:desh_engine",
            "ad_astra:ostrum_plate",
            "tfmg:magnetic_alloy_sheet",
        },
        "industrial_colonies:space_hardware/photovoltaic_etrium_cell": {
            "tfmg:silicon_ingot",
            "ad_astra:desh_plate",
            "minecraft:blue_stained_glass",
        },
    }

    semiconductor_parts = {"tfmg:capacitor_item", "tfmg:transistor_item"}
    circuit_parts = {
        "tfmg:coated_circuit_board",
        "tfmg:etched_circuit_board",
        "ae2:calculation_processor",
        "ae2:engineering_processor",
    }

    ingredient_sets: dict[frozenset[str], str] = {}
    for recipe_id in sorted(REDESIGNED_IDS):
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        ingredients = _all_ingredients(recipe)
        missing_parts = functional_signatures[recipe_id] - ingredients
        if missing_parts:
            errors.append(
                f"{recipe_id} lost functional hardware {sorted(missing_parts)}"
            )
        if "mekanism:steel_casing" in ingredients:
            errors.append(f"{recipe_id} restored Mekanism steel casing")

        # The explicit electronics-note cohort must contain all three requested
        # categories.  The too-cheap cohort is validated separately for depth.
        if recipe_id in NEEDS_ELECTRONICS_IDS:
            if "tfmg:plastic_sheet" not in ingredients:
                errors.append(f"{recipe_id} has no plastic insulation")
            if not (semiconductor_parts & ingredients):
                errors.append(f"{recipe_id} has no discrete semiconductor")
            if not (circuit_parts & ingredients):
                errors.append(f"{recipe_id} has no circuit board or processor")
        if recipe_id in TOO_CHEAP_IDS and len(ingredients) < 8:
            errors.append(f"{recipe_id} remains too cheap and shallow")

        signature = frozenset(ingredients)
        if signature in ingredient_sets:
            errors.append(
                f"{recipe_id} copied the BOM from {ingredient_sets[signature]}"
            )
        ingredient_sets[signature] = recipe_id

    patterns: dict[tuple[str, ...], str] = {}
    for recipe_id in sorted(GRID_IDS):
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "mechanical_crafting":
            errors.append(f"{recipe_id} is not Mechanical Crafting")
            continue
        pattern = recipe.get("pattern")
        key = recipe.get("key")
        if not isinstance(pattern, list) or len(pattern) != 5:
            errors.append(f"{recipe_id} is not a 5-row physical silhouette")
            continue
        if any(not isinstance(row, str) or len(row) != 5 for row in pattern):
            errors.append(f"{recipe_id} has a malformed 5x5 grid")
            continue
        used = set("".join(pattern)) - {" "}
        if not isinstance(key, dict) or used != set(key):
            errors.append(f"{recipe_id} has stale or unused grid keys")
        occupied = sum(char != " " for row in pattern for char in row)
        if occupied < 14:
            errors.append(f"{recipe_id} became an arbitrarily sparse grid")
        if _is_filled_perimeter(pattern):
            errors.append(f"{recipe_id} became a rejected perimeter ring")
        frozen = tuple(pattern)
        if frozen in patterns:
            errors.append(f"{recipe_id} copied the shape from {patterns[frozen]}")
        patterns[frozen] = recipe_id

    for recipe_id in sorted(SEQUENCE_IDS):
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not Sequenced Assembly")
            continue
        steps = recipe.get("steps", [])
        if not 7 <= len(steps) <= 8:
            errors.append(f"{recipe_id} has unjustified sequence length {len(steps)}")
        if recipe_id in COPPER_SEQUENCE_IDS:
            expected_machines = {COPPER_DEPLOYER, COPPER_PRESS}
            expected_press = _press(COPPER_PRESS)
        else:
            expected_machines = {
                REFINED_RADIANCE_DEPLOYER,
                REFINED_RADIANCE_PRESS,
            }
            expected_press = _press(REFINED_RADIANCE_PRESS)
        machines = {
            step.get("machine")
            for step in steps
            if isinstance(step, dict) and isinstance(step.get("machine"), str)
        }
        if machines != expected_machines:
            errors.append(f"{recipe_id} escaped its manufacturing line")
        if not steps or steps[-1] != expected_press:
            errors.append(f"{recipe_id} does not finish with its line press")
        expected_loops = (
            2
            if recipe_id
            == "industrial_colonies:space_hardware/photovoltaic_etrium_cell"
            else 1
        )
        if recipe.get("loops") != expected_loops:
            errors.append(f"{recipe_id} has an unjustified loop count")

    # The engine ladder must advance through planetary materials in order.
    engine_ladder = [
        (
            "industrial_colonies:space_coverage/desh_engine",
            "ad_astra:steel_engine",
            "ad_astra:desh_plate",
        ),
        (
            "industrial_colonies:space_hardware/ostrum_engine",
            "ad_astra:desh_engine",
            "ad_astra:ostrum_plate",
        ),
        (
            "industrial_colonies:space_hardware/calorite_engine",
            "ad_astra:ostrum_engine",
            "ad_astra:calorite_plate",
        ),
    ]
    for recipe_id, expected_input, planetary_plate in engine_ladder:
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("input") != expected_input:
            errors.append(f"{recipe_id} broke the planetary engine upgrade ladder")
        if planetary_plate not in _sequence_ingredients(recipe):
            errors.append(f"{recipe_id} lost its planetary hot-section material")

    if errors:
        raise ValueError(
            "Space-hardware rejection audit failed: " + " | ".join(errors)
        )
    return {
        "status": "PASS",
        "redesigned": len(REDESIGNED_IDS),
        "too_cheap": len(TOO_CHEAP_IDS),
        "needs_electronics": len(NEEDS_ELECTRONICS_IDS),
        "mechanical_crafting": len(GRID_IDS),
        "sequenced_assembly": len(SEQUENCE_IDS),
        "review_state": "pending_after_reconciliation",
    }

