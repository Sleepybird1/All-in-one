#!/usr/bin/env python3
"""Refine oversized recipe silhouettes without touching the source seed.

The first recipe-design pass established the correct progression ownership but
left several unrelated large machines with the same rounded 5x5 ingredient
body.  This module keeps large, visibly assembled equipment in Mechanical
Crafting while drawing the machine that is actually being built.  Six outputs
which are individual pieces of equipment or process media are moved out of the
5x5 grid and onto the Refined Radiance precision line.

``apply`` performs an in-memory, idempotent dictionary transform.  Every target
must already exist exactly once: this module deliberately cannot create a
second recipe, output claim, or stock-removal owner by accident.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]


_RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
_RADIANCE_PRESS = "createcasing:refined_radiance_press"
_RAILWAY_DEPLOYER = "createcasing:railway_deployer"
_RAILWAY_PRESS = "createcasing:railway_press"

_PROCESS_FIELDS = {
    "type",
    "pattern",
    "key",
    "input",
    "transitional",
    "loops",
    "steps",
    "machine",
    "inputs",
}

_PRESERVED_FIELDS = (
    "id",
    "node",
    "phase",
    "order",
    "output",
    "remove",
    "exclusive_output",
)


def _grid(
    *,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    add_depends_on: list[str] | None = None,
) -> Recipe:
    if len(pattern) != 5 or any(len(row) != 5 for row in pattern):
        raise ValueError(f"refined Mechanical Crafting grid is not 5x5: {pattern}")
    used = set("".join(pattern)) - {" "}
    if used != set(key):
        raise ValueError(
            "refined grid symbols do not match its key: "
            f"used={sorted(used)}, key={sorted(key)}"
        )
    body: Recipe = {
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": list(pattern),
        "key": dict(key),
    }
    if add_depends_on:
        body["_add_depends_on"] = list(add_depends_on)
    return body


def _sequence(
    *,
    comment: str,
    input_item: str,
    ingredients: list[str],
    add_depends_on: list[str] | None = None,
    deployer: str = _RADIANCE_DEPLOYER,
    press: str = _RADIANCE_PRESS,
) -> Recipe:
    body: Recipe = {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "loops": 1,
        "steps": [
            {
                "op": "deploying",
                "ingredient": ingredient,
                "machine": deployer,
            }
            for ingredient in ingredients
        ]
        + [{"op": "pressing", "machine": press}],
    }
    if add_depends_on:
        body["_add_depends_on"] = list(add_depends_on)
    return body


_GRID_REFINEMENTS: dict[str, Recipe] = {
    "industrial_colonies:electronics/polarizer": _grid(
        comment=(
            "Wind a sparse copper solenoid around the steel field core, brace it "
            "with resistor-capacitor rails, and terminate it beneath the voltmeter."
        ),
        pattern=["  V  ", " CWC ", "BRSRB", " CWC ", " BWB "],
        key={
            "B": "#c:plates/brass",
            "W": "tfmg:copper_wire",
            "V": "tfmg:voltmeter",
            "C": "tfmg:capacitor_item",
            "R": "tfmg:resistor",
            "S": "tfmg:steel_casing",
        },
    ),
    "industrial_colonies:grid/alternator_rotor": _grid(
        comment=(
            "Form a circular copper winding disk around a cast-iron hub, a central "
            "shaft, and the generator field package."
        ),
        pattern=["  W  ", " WIW ", "WMSMW", " WAW ", "  W  "],
        key={
            "A": "tfmg:generator",
            "I": "tfmg:cast_iron_ingot",
            "M": "tfmg:steel_mechanism",
            "S": "create:shaft",
            "W": "electroenergetics:copper_wire_spool",
        },
    ),
    "industrial_colonies:extreme_grid/high_voltage_switch": _grid(
        comment=(
            "Build an open disconnect switch with two porcelain terminals, an "
            "asymmetric insulated blade, breaker pivot, and steel pedestal."
        ),
        pattern=[" I I ", " H C ", "  HMW", " C B ", " SSS "],
        key={
            "I": "electroenergetics:insulator",
            "S": "tfmg:steel_casing",
            "H": "electroenergetics:heavily_insulated_wire",
            "C": "electroenergetics:connector",
            "W": "electroenergetics:copper_wire_spool",
            "M": "electroenergetics:miniature_circuit_breaker",
            "B": "electroenergetics:heavily_insulated_wire_spool",
        },
    ),
    "industrial_colonies:high_voltage/transformer": _grid(
        comment=(
            "Raise twin winding columns beneath paired high-voltage terminals, "
            "surround the oil-cooled core, and seat both accumulator banks on steel."
        ),
        pattern=[" D D ", " W W ", "W C W", " IOI ", "SACAS"],
        key={
            "D": "electroenergetics:double_connector",
            "S": "tfmg:steel_casing",
            "W": "electroenergetics:copper_wire_spool",
            "O": "electroenergetics:transformer_oil_bucket",
            "A": "electroenergetics:accumulator",
            "C": "electroenergetics:transformer_core",
            "I": "electroenergetics:insulated_wire",
        },
    ),
    "industrial_colonies:world_loading/dimensional_stabilizer": _grid(
        comment=(
            "Arrange four spatial anchors as an open cross around the computer and "
            "energy core, with atomic corners and refined-obsidian field braces."
        ),
        pattern=["A S A", "R P R", "SCECS", "R S R", "A U A"],
        key={
            "A": "mekanism:alloy_atomic",
            "R": "#c:ingots/refined_obsidian",
            "U": "mekanism:ultimate_control_circuit",
            "P": "ae2:engineering_processor",
            "S": "ae2:spatial_anchor",
            "C": "computercraft:computer_advanced",
            "E": "mekanism:ultimate_energy_cube",
        },
    ),
    "industrial_colonies:bigreactors/fluidizer/controller": _grid(
        comment=(
            "Build a three-vat vertical process column with paired circulation "
            "pumps, a monitor crown, controller face, and chemical manifold bed."
        ),
        pattern=["  M  ", " PVP ", " RVR ", " PVP ", "UCEAU"],
        key={
            "R": "create:refined_radiance_casing",
            "M": "computercraft:monitor_advanced",
            "V": "tfmg:steel_chemical_vat",
            "P": "tfmg:electric_pump",
            "C": "computercraft:computer_advanced",
            "U": "mekanism:elite_control_circuit",
            "A": "bigreactors:fluidizercasing",
            "E": "ae2:engineering_processor",
        },
    ),
    "industrial_colonies:bigreactors/basic_turbine/controller": _grid(
        comment=(
            "Lay a three-section turbine shaft between casing cheeks, couple it to "
            "the transformer-generator pair, and mount the governor on its pedestal."
        ),
        pattern=[" M M ", " T G ", "KSSSK", " ECUE", " KAK "],
        key={
            "M": "computercraft:monitor_advanced",
            "T": "tfmg:transformer",
            "G": "tfmg:generator",
            "K": "bigreactors:basic_turbinecasing",
            "S": "bigreactors:basic_turbinerotorshaft",
            "E": "ae2:engineering_processor",
            "C": "computercraft:computer_advanced",
            "U": "mekanism:elite_control_circuit",
            "A": "bigreactors:basic_reactorcontroller",
        },
        add_depends_on=["industrial_colonies:bigreactors/basic_turbine/rotor_shaft"],
    ),
    "industrial_colonies:bigreactors/reinforced_turbine/controller": _grid(
        comment=(
            "Bridge a reinforced rotor rail over the inherited basic governor and "
            "reprocessor controller, then lock it to an ultimate-interlocked base."
        ),
        pattern=[" M M ", " TST ", "RBPCR", " U U ", "AAAAA"],
        key={
            "M": "computercraft:monitor_advanced",
            "T": "tfmg:transformer",
            "S": "bigreactors:reinforced_turbinerotorshaft",
            "R": "create:refined_radiance_casing",
            "B": "bigreactors:basic_turbinecontroller",
            "P": "bigreactors:reprocessorcontroller",
            "C": "computercraft:computer_advanced",
            "U": "mekanism:ultimate_control_circuit",
            "A": "bigreactors:reinforced_turbinecasing",
        },
        add_depends_on=[
            "industrial_colonies:bigreactors/reinforced_turbine/rotor_shaft"
        ],
    ),
    "industrial_colonies:space/propulsion/engine_nozzle": _grid(
        comment=(
            "Form two broad titanium throats that taper through a shared pressure "
            "manifold into a pair of reinforced engine-pipe outlets."
        ),
        pattern=["A   A", "HT TH", " HPH ", "  S  ", " P P "],
        key={
            "A": "mekanism:alloy_atomic",
            "H": "tfmg:heavy_plate",
            "T": "rocketnautics:titanium_alloy_sheet",
            "P": "rocketnautics:engine_pipes",
            "S": "tfmg:steel_mechanism",
        },
    ),
    "industrial_colonies:space/propulsion/thruster_mount": _grid(
        comment=(
            "Raise a U-shaped load frame under the control crown, pass fuel and "
            "data interfaces through the middle, and seat the nozzle on a full bed."
        ),
        pattern=[" TCB ", "F   F", "H P H", "F E F", "FUMNF"],
        key={
            "F": "tfmg:steel_frame",
            "T": "tfmg:transformer",
            "H": "tfmg:heavy_plate",
            "M": "tfmg:steel_mechanism",
            "C": "tfmg:circuit_board",
            "B": "computercraft:computer_advanced",
            "P": "rocketnautics:engine_pipes",
            "U": "mekanism:ultimate_control_circuit",
            "E": "rocketnautics:engine_nozzle",
            "N": "rocketnautics:hose_anchor",
        },
    ),
    "industrial_colonies:space_coverage/booster_thruster": _grid(
        comment=(
            "Stack valve, feed pipe, pressure tank, completed thruster, and nozzle "
            "down a tall rocket centerline with titanium-casing fins."
        ),
        pattern=["  V  ", " HPH ", "HCTCH", "H R H", "H N H"],
        key={
            "V": "tfmg:steel_fluid_valve",
            "H": "tfmg:heavy_plate",
            "P": "rocketnautics:engine_pipes",
            "T": "rocketnautics:titanium_casing",
            "R": "rocketnautics:rocket_thruster",
            "C": "tfmg:steel_fluid_tank",
            "N": "rocketnautics:titanium_nozzle",
        },
    ),
    "industrial_colonies:space/life_support/fan": _grid(
        comment=(
            "Balance a circular propeller ring around the electric motor, support "
            "the rotor on a steel frame, and wire the lower control quadrant."
        ),
        pattern=[" P P ", "P H P", "F M F", "P C P", " P P "],
        key={
            "P": "create:propeller",
            "H": "tfmg:heavy_plate",
            "F": "tfmg:steel_frame",
            "M": "tfmg:electric_motor",
            "C": "tfmg:circuit_board",
        },
    ),
    "industrial_colonies:space/life_support/gas_tank": _grid(
        comment=(
            "Curve a rubber-lined heavy shell around the chemical tank, cap it "
            "with a valve neck, and draw the outlet through the bottom pipe."
        ),
        pattern=["  V  ", " RHR ", " HTH ", " RHR ", "  P  "],
        key={
            "V": "tfmg:steel_fluid_valve",
            "R": "tfmg:rubber_sheet",
            "H": "tfmg:heavy_plate",
            "T": "mekanism:elite_chemical_tank",
            "P": "tfmg:steel_pipe",
        },
    ),
    "industrial_colonies:space/life_support/oxygen_loader": _grid(
        comment=(
            "Raise a loader tower from the heavy bed: fan intake, pipe-and-control "
            "header, valve chamber, then tank and electric transfer pump."
        ),
        pattern=["  F  ", " PCV ", "H L H", " T E ", " HHH "],
        key={
            "F": "ad_astra:fan",
            "H": "tfmg:heavy_plate",
            "P": "tfmg:steel_pipe",
            "C": "tfmg:circuit_board",
            "V": "tfmg:steel_fluid_valve",
            "L": "mekanism:rotary_condensentrator",
            "T": "ad_astra:gas_tank",
            "E": "tfmg:electric_pump",
        },
    ),
    "industrial_colonies:space/life_support/oxygen_distributor": _grid(
        comment=(
            "Build a hub-and-spoke oxygen manifold around the completed loader, "
            "with tank wings, perimeter fans, computer control, and a powered base."
        ),
        pattern=[" FVF ", "G L G", " OCO ", " FTF ", " HUH "],
        key={
            "F": "ad_astra:fan",
            "V": "tfmg:steel_fluid_valve",
            "H": "tfmg:heavy_plate",
            "C": "tfmg:circuit_board",
            "O": "ad_astra:oxygen_gear",
            "G": "ad_astra:large_gas_tank",
            "L": "ad_astra:oxygen_loader",
            "T": "computercraft:computer_advanced",
            "U": "mekanism:ultimate_energy_cube",
        },
    ),
    "industrial_colonies:space/construction/physics_assembler": _grid(
        comment=(
            "Build an inverted-U fabrication gantry with a piston crown, motor "
            "carriages, open work bay, and diagram-driven controller bed."
        ),
        pattern=["F P F", "HM MH", "F   F", "F V F", "BUDCB"],
        key={
            "F": "tfmg:steel_frame",
            "P": "create:mechanical_piston",
            "H": "tfmg:heavy_plate",
            "M": "tfmg:electric_motor",
            "V": "ad_astra:vent",
            "B": "tfmg:circuit_board",
            "U": "mekanism:ultimate_control_circuit",
            "C": "computercraft:computer_advanced",
            "D": "simulated:contraption_diagram",
        },
    ),
    "industrial_colonies:space/dockyard/docking_connector": _grid(
        comment=(
            "Leave the center of the docking collar open while placing item, fluid, "
            "energy, and data interfaces at the cardinal points over its actuator."
        ),
        pattern=["F I F", "P   E", "F D F", "  M  ", "HCUCH"],
        key={
            "H": "tfmg:heavy_plate",
            "I": "create:portable_storage_interface",
            "F": "tfmg:steel_frame",
            "P": "create:portable_fluid_interface",
            "C": "computercraft:cable",
            "E": "createaddition:portable_energy_interface",
            "D": "computercraft:wired_modem",
            "U": "mekanism:ultimate_control_circuit",
            "M": "tfmg:electric_motor",
        },
    ),
    "industrial_colonies:planetary/outpost/gravity_normalizer": _grid(
        comment=(
            "Raise twin Desh field-coil arches around the energy cube, bridge them "
            "with transformers, and close the field through the control base."
        ),
        pattern=[" T T ", "DC CD", "DWQWD", "DC CD", " EUE "],
        key={
            "T": "tfmg:transformer",
            "D": "ad_astra:desh_plate",
            "C": "ad_astra:etrionic_capacitor",
            "W": "mekanism:ultimate_universal_cable",
            "Q": "mekanism:ultimate_energy_cube",
            "E": "ae2:engineering_processor",
            "U": "mekanism:ultimate_control_circuit",
        },
    ),
    "industrial_colonies:planetary/outpost/energizer": _grid(
        comment=(
            "Span capacitor and transformer hardware across two Ostrum charging "
            "posts, leave the work bay open, and seat it on an interlocked block bed."
        ),
        pattern=[" CTC ", "O Q O", "O   O", "O E O", "BBUBB"],
        key={
            "O": "ad_astra:ostrum_plate",
            "C": "ad_astra:etrionic_capacitor",
            "Q": "mekanism:ultimate_energy_cube",
            "T": "tfmg:transformer",
            "E": "ae2:engineering_processor",
            "U": "mekanism:ultimate_control_circuit",
            "B": "ad_astra:ostrum_block",
        },
    ),
    "industrial_colonies:planetary/mercury/navigation_computer": _grid(
        comment=(
            "Assemble a telemetry workstation beneath the Sputnik crown, with the "
            "navigation table centered between etched backplanes and prior guidance."
        ),
        pattern=[" S U ", " B E ", "C N C", "B V B", "CPMPC"],
        key={
            "S": "rocketnautics:sputnik",
            "U": "mekanism:ultimate_control_circuit",
            "C": "ad_astra:calorite_plate",
            "E": "ae2:engineering_processor",
            "B": "tfmg:etched_circuit_board",
            "N": "simulated:navigation_table",
            "V": "industrial_colonies:venus_navigation_computer",
            "P": "ad_astra:calorite_block",
            "M": "computercraft:computer_advanced",
        },
    ),
    "industrial_colonies:petroleum/steel_distillation_controller": _grid(
        comment=(
            "Raise a visible three-stage distillation column between side pipe and "
            "lead manifolds, then place the mechanism and compass control face below."
        ),
        pattern=["  E  ", " PTP ", "L T L", "P H P", " MCM "],
        key={
            "L": "#c:plates/lead",
            "P": "tfmg:industrial_pipe",
            "E": "create:electron_tube",
            "C": "minecraft:compass",
            "M": "tfmg:steel_mechanism",
            "H": "tfmg:heavy_machinery_casing",
            "T": "tfmg:steel_fluid_tank",
        },
    ),
    "industrial_colonies:tfmg_heavy_electrical/centrifuge": _grid(
        comment=(
            "Form a round barred rotor cage around the central shaft, hold it in "
            "cast-iron bearings, and leave a service opening above the precision drive."
        ),
        pattern=[" AFA ", "AR RA", "F S F", "A   A", " BCB "],
        key={
            "A": "tfmg:aluminum_bars",
            "B": "create:precision_mechanism",
            "C": "tfmg:steel_casing",
            "F": "tfmg:cast_iron_frame",
            "R": "create:large_cogwheel",
            "S": "create:shaft",
        },
    ),
}


_SEQUENCE_REFINEMENTS: dict[str, Recipe] = {
    "industrial_colonies:petroleum/steel_distillation_output": _sequence(
        comment=(
            "Turn one heavy casing into a dedicated refinery outlet by installing "
            "one pressure tank, one steel feed, one industrial manifold, and its valve."
        ),
        input_item="tfmg:heavy_machinery_casing",
        ingredients=[
            "tfmg:steel_fluid_tank",
            "tfmg:steel_pipe",
            "tfmg:industrial_pipe",
            "tfmg:steel_fluid_valve",
        ],
        deployer=_RAILWAY_DEPLOYER,
        press=_RAILWAY_PRESS,
    ),
    "industrial_colonies:planetary/venus/netherite_space_helmet": _sequence(
        comment=(
            "Pressure-fit the Netherite helmet with a Desh thermal liner, doubled "
            "Ostrum shell, visor, oxygen sensor, and exhaust vent before final pressing."
        ),
        input_item="minecraft:netherite_helmet",
        ingredients=[
            "ad_astra:desh_plate",
            "2x ad_astra:ostrum_plate",
            "minecraft:tinted_glass",
            "ad_astra:oxygen_sensor",
            "ad_astra:vent",
        ],
    ),
    "industrial_colonies:planetary/venus/netherite_space_suit": _sequence(
        comment=(
            "Install the complete oxygen train into a Netherite chestplate, route "
            "power and pressure services, then close the Desh-Ostrum pressure shell."
        ),
        input_item="minecraft:netherite_chestplate",
        ingredients=[
            "ad_astra:oxygen_gear",
            "ad_astra:large_gas_tank",
            "ad_astra:oxygen_distributor",
            "tfmg:steel_fluid_valve",
            "ad_astra:etrionic_capacitor",
            "mekanism:ultimate_universal_cable",
            "ad_astra:desh_plate",
            "2x ad_astra:ostrum_plate",
        ],
    ),
    "industrial_colonies:planetary/venus/netherite_space_pants": _sequence(
        comment=(
            "Line Netherite leggings with Desh, form the doubled Ostrum pressure "
            "shell, and install paired gas cells, valve, and suit-power cable."
        ),
        input_item="minecraft:netherite_leggings",
        ingredients=[
            "ad_astra:desh_plate",
            "2x ad_astra:ostrum_plate",
            "2x ad_astra:gas_tank",
            "tfmg:steel_fluid_valve",
            "mekanism:ultimate_universal_cable",
        ],
    ),
    "industrial_colonies:planetary/venus/netherite_space_boots": _sequence(
        comment=(
            "Line Netherite boots with Desh, close doubled Ostrum shells, and fit "
            "their gas cell, pressure valve, circulation fan, and rubber seals."
        ),
        input_item="minecraft:netherite_boots",
        ingredients=[
            "ad_astra:desh_plate",
            "2x ad_astra:ostrum_plate",
            "ad_astra:gas_tank",
            "tfmg:steel_fluid_valve",
            "ad_astra:fan",
            "tfmg:rubber_sheet",
        ],
    ),
    "industrial_colonies:interstellar/unsigned_route_crystal": _sequence(
        comment=(
            "Reference a Moon Crystal against a quantum singularity, shield it in "
            "Calorite and titanium, encode the route card, and press in star authority."
        ),
        input_item="cosmowarp:moon_crystal",
        ingredients=[
            "ae2:quantum_entangled_singularity",
            "ad_astra:calorite_plate",
            "rocketnautics:titanium_alloy_sheet",
            "industrial_colonies:industrial_star",
            "cosmowarp:memory_card",
            "mekanism:ultimate_control_circuit",
        ],
        add_depends_on=["industrial_colonies:space_coverage/warp_memory_card"],
    ),
    "industrial_colonies:outer_station/warp_charge_precursor": _sequence(
        comment=(
            "Meter all eight returned condensate canisters into a Mercury-seeded "
            "core, then add titanium-Calorite containment, twin Moon-Crystal field "
            "media, star authority, and an ultimate interlock before final pressing."
        ),
        input_item="industrial_colonies:gas_giant_condensate_bucket",
        ingredients=[
            "7x industrial_colonies:gas_giant_condensate_bucket",
            "ad_astra:mercury_iron_ore",
            "rocketnautics:titanium_alloy_sheet",
            "ad_astra:calorite_block",
            "2x cosmowarp:moon_crystal",
            "industrial_colonies:industrial_star",
            "mekanism:ultimate_control_circuit",
        ],
    ),
}


def _replace_existing(data: dict[str, Any], recipe_id: str, body: Recipe) -> None:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise ValueError("recipe-design seed has no recipes list")
    matches = [
        index for index, recipe in enumerate(recipes) if recipe.get("id") == recipe_id
    ]
    if len(matches) != 1:
        raise ValueError(
            f"shape-refinement target must exist exactly once: {recipe_id} "
            f"(found {len(matches)})"
        )

    index = matches[0]
    original = recipes[index]
    preserved = {
        field: (field in original, deepcopy(original.get(field)))
        for field in _PRESERVED_FIELDS
    }
    old_depends = list(original.get("depends_on", []))

    replacement = deepcopy(original)
    for field in _PROCESS_FIELDS:
        replacement.pop(field, None)

    process_body = deepcopy(body)
    additions = process_body.pop("_add_depends_on", [])
    replacement.update(process_body)
    if old_depends or additions:
        replacement["depends_on"] = list(old_depends)
        for dependency in additions:
            if dependency not in replacement["depends_on"]:
                replacement["depends_on"].append(dependency)
    else:
        replacement.pop("depends_on", None)

    for field, (was_present, value) in preserved.items():
        if (field in replacement) != was_present or replacement.get(field) != value:
            raise AssertionError(f"shape refinement changed preserved field {field}: {recipe_id}")
    if replacement.get("output") != original.get("output"):
        raise AssertionError(f"shape refinement changed output scale: {recipe_id}")

    recipes[index] = replacement


def apply(data: dict[str, Any]) -> None:
    """Apply all 29 in-memory shape refinements; perform no filesystem I/O."""

    overlap = set(_GRID_REFINEMENTS).intersection(_SEQUENCE_REFINEMENTS)
    if overlap:
        raise ValueError(f"shape-refinement targets overlap: {sorted(overlap)}")
    for recipe_id, body in _GRID_REFINEMENTS.items():
        _replace_existing(data, recipe_id, body)
    for recipe_id, body in _SEQUENCE_REFINEMENTS.items():
        _replace_existing(data, recipe_id, body)
