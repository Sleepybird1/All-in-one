#!/usr/bin/env python3
"""Curated space-industry coverage for recipe design v2.

The installed space stack contains several useful machines whose stock recipes
are either intentionally deferred by the pack or much cheaper than the Earth
factory campaign which precedes them.  This module supplies authored routes for
thirty functional outputs without enabling prefab Ad Astra rockets or stations.

The manufacturing language is deliberately physical:

* Refined Radiance lines assemble compact avionics, valves, thrusters, tanks,
  and off-world electronics.
* Railway lines form terrestrial pressure shells, engines, and running gear.
* Mechanical Crafting is reserved for machines large enough to have a visible
  body: furnaces, boosters, rovers, cryogenic plants, and warp hardware.

``apply`` is a pure, idempotent dictionary transform.  It performs no registry
scan, file write, generation, build, deployment, or runtime test.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Iterable


Recipe = dict[str, Any]


def _deploy(ingredient: str, casing: str) -> Recipe:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": f"createcasing:{casing}_deployer",
    }


def _press(casing: str) -> Recipe:
    return {"op": "pressing", "machine": f"createcasing:{casing}_press"}


def _sequence(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    casing: str,
    stock_id: str,
    depends_on: list[str] | None = None,
    loops: int = 1,
) -> Recipe:
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": loops,
        "steps": [_deploy(ingredient, casing) for ingredient in ingredients]
        + [_press(casing)],
        "remove": [stock_id],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _grid(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    stock_id: str,
    recipe_type: str = "mechanical_crafting",
    depends_on: list[str] | None = None,
) -> Recipe:
    if recipe_type not in {"shaped", "mechanical_crafting"}:
        raise ValueError(f"unsupported grid type: {recipe_type}")
    if not pattern:
        raise ValueError(f"empty grid: {recipe_id}")
    width = len(pattern[0])
    if len(pattern) > 5 or width > 5:
        raise ValueError(f"grid exceeds 5x5: {recipe_id}")
    if any(len(row) != width for row in pattern):
        raise ValueError(f"non-rectangular grid: {recipe_id}")
    used = set("".join(pattern)) - {" "}
    if used != set(key):
        raise ValueError(
            f"grid symbols do not match key for {recipe_id}: "
            f"used={sorted(used)}, key={sorted(key)}"
        )
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": recipe_type,
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": [stock_id],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _compacting(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    machine: str,
    inputs: list[str],
    output: str,
    stock_id: str,
    depends_on: list[str] | None = None,
) -> Recipe:
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": inputs,
        "output": output,
        "remove": [stock_id],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _rocketnautics_recipes() -> list[Recipe]:
    return [
        _sequence(
            recipe_id="industrial_colonies:space_coverage/rcs_thruster",
            node="CR02 — Modular Propulsion",
            phase="Orbital Engineering",
            order=141,
            comment=(
                "Instrument a compact copper nozzle with a propellant anchor, "
                "metering pump, etched controller, and titanium heat shield"
            ),
            input_item="rocketnautics:copper_nozzle",
            output="rocketnautics:rcs_thruster",
            ingredients=[
                "rocketnautics:hose_anchor",
                "tfmg:electric_pump",
                "tfmg:etched_circuit_board",
                "rocketnautics:titanium_alloy_sheet",
            ],
            casing="refined_radiance",
            stock_id="rocketnautics:crafting/mechanisms/rcs_thruster",
            depends_on=["industrial_colonies:space/propulsion/hose_anchor"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/rocket_thruster",
            node="CR02 — Modular Propulsion",
            phase="Orbital Engineering",
            order=142,
            comment=(
                "Populate the manufactured thruster mount with a nozzle, cycle "
                "pipes, electric turbopump, steel mechanism, and control circuit"
            ),
            input_item="rocketnautics:thruster_mount",
            output="rocketnautics:rocket_thruster",
            ingredients=[
                "rocketnautics:engine_nozzle",
                "rocketnautics:engine_pipes",
                "tfmg:electric_pump",
                "tfmg:steel_mechanism",
                "mekanism:advanced_control_circuit",
            ],
            casing="refined_radiance",
            stock_id="rocketnautics:mechanical_crafting/rocket_thruster",
            depends_on=[
                "industrial_colonies:space/propulsion/engine_nozzle",
                "industrial_colonies:space/propulsion/engine_pipes",
                "industrial_colonies:space/propulsion/thruster_mount",
            ],
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/booster_thruster",
            node="CR02 — Modular Propulsion",
            phase="Orbital Engineering",
            order=143,
            comment=(
                "Build a tall booster around a completed rocket thruster with "
                "pressure plumbing, resilient casing, tankage, and a second nozzle"
            ),
            pattern=["  V  ", " HPH ", "HTRTH", " HCH ", "  N  "],
            key={
                "V": "tfmg:steel_fluid_valve",
                "H": "tfmg:heavy_plate",
                "P": "rocketnautics:engine_pipes",
                "T": "rocketnautics:titanium_casing",
                "R": "rocketnautics:rocket_thruster",
                "C": "tfmg:steel_fluid_tank",
                "N": "rocketnautics:titanium_nozzle",
            },
            output="rocketnautics:booster_thruster",
            stock_id="rocketnautics:mechanical_crafting/booster_thruster",
            depends_on=["industrial_colonies:space_coverage/rocket_thruster"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/vector_thruster",
            node="CR02 — Modular Propulsion",
            phase="Orbital Engineering",
            order=144,
            comment=(
                "Fit a rocket thruster with a motorized gimbal, gyroscopic "
                "reference, calculation logic, and titanium pivot shroud"
            ),
            input_item="rocketnautics:rocket_thruster",
            output="rocketnautics:vector_thruster",
            ingredients=[
                "simulated:gimbal_sensor",
                "simulated:gyroscopic_mechanism",
                "tfmg:electric_motor",
                "ae2:calculation_processor",
                "rocketnautics:titanium_alloy_sheet",
            ],
            casing="refined_radiance",
            stock_id="rocketnautics:crafting/mechanisms/vector_thruster",
            depends_on=[
                "industrial_colonies:space_coverage/rocket_thruster",
                "industrial_colonies:space/navigation/gimbal_sensor",
            ],
        ),
        _compacting(
            recipe_id="industrial_colonies:space_coverage/separator_charge",
            node="CR02 — Modular Propulsion",
            phase="Orbital Engineering",
            order=145,
            comment=(
                "Seal two redundant staging charges in plastic, titanium, and "
                "electrically supervised energetic cartridges"
            ),
            machine="createcasing:refined_radiance_press",
            inputs=[
                "4x minecraft:gunpowder",
                "2x tfmg:plastic_sheet",
                "tfmg:copper_wire",
                "mekanism:advanced_control_circuit",
                "rocketnautics:titanium_alloy_sheet",
            ],
            output="2x rocketnautics:separator_charge",
            stock_id="rocketnautics:crafting/mechanisms/separator_charge",
            depends_on=["industrial_colonies:space/propulsion/thruster_mount"],
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/separator",
            node="CR02 — Modular Propulsion",
            phase="Orbital Engineering",
            order=146,
            comment=(
                "Seat opposed staging charges around a controllable clutch in a "
                "titanium break plane"
            ),
            pattern=[" C ", "TLT", " C "],
            key={
                "C": "rocketnautics:separator_charge",
                "T": "rocketnautics:titanium_alloy_sheet",
                "L": "create:clutch",
            },
            output="rocketnautics:separator",
            stock_id="rocketnautics:crafting/mechanisms/separator",
            recipe_type="shaped",
            depends_on=["industrial_colonies:space_coverage/separator_charge"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/separator_shaft",
            node="CR02 — Modular Propulsion",
            phase="Orbital Engineering",
            order=147,
            comment=(
                "Sleeve a Create shaft with the staged separator, magnetic "
                "reinforcement, steel timing hardware, and service fasteners"
            ),
            input_item="create:shaft",
            output="rocketnautics:separator_shaft",
            ingredients=[
                "rocketnautics:separator",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:steel_mechanism",
                "tfmg:screw",
            ],
            casing="refined_radiance",
            stock_id="rocketnautics:crafting/mechanisms/separator_shaft",
            depends_on=["industrial_colonies:space_coverage/separator"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/magnetic_stabilizer",
            node="CR02 — Orbital Guidance",
            phase="Orbital Engineering",
            order=101,
            comment=(
                "Wind opposed field coils into a resilient casing around a "
                "gyroscopic reference, calculation processor, and magnetic shell"
            ),
            input_item="rocketnautics:titanium_casing",
            output="rocketnautics:magnetic_stabilizer",
            ingredients=[
                "tfmg:electromagnetic_coil",
                "simulated:gyroscopic_mechanism",
                "tfmg:electromagnetic_coil",
                "ae2:calculation_processor",
                "tfmg:magnetic_alloy_sheet",
            ],
            casing="refined_radiance",
            stock_id="rocketnautics:magnetic_stabilizer",
            depends_on=["industrial_colonies:space/orbital_flight_computer"],
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/hologram_table",
            node="CR02 — Orbital Navigation",
            phase="Orbital Engineering",
            order=321,
            comment=(
                "Build the hologram table as an optical console over a physical "
                "navigation table, advanced host computer, and titanium pedestal"
            ),
            pattern=[" A A ", "GMNMG", " ECE ", " TTT "],
            key={
                "A": "minecraft:amethyst_shard",
                "G": "minecraft:tinted_glass",
                "M": "ae2:monitor",
                "N": "simulated:navigation_table",
                "E": "tfmg:etched_circuit_board",
                "C": "computercraft:computer_advanced",
                "T": "rocketnautics:titanium_alloy_sheet",
            },
            output="rocketnautics:hologram_block",
            stock_id="rocketnautics:hologram_block",
            depends_on=["industrial_colonies:space/navigation/navigation_table"],
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/cosmonautics_jetpack",
            node="CR02 — Habitat Life Support",
            phase="Orbital Engineering",
            order=231,
            comment=(
                "Build an EVA propulsion harness around a Netherite backtank, "
                "oxygen regulator, paired titanium nozzles, and flexible restraints"
            ),
            pattern=[" C ", " O ", "RBR", "N N", " T "],
            key={
                "C": "mekanism:advanced_control_circuit",
                "O": "ad_astra:oxygen_gear",
                "R": "tfmg:rubber_sheet",
                "B": "create:netherite_backtank",
                "N": "rocketnautics:titanium_nozzle",
                "T": "rocketnautics:titanium_alloy_sheet",
            },
            output="rocketnautics:jetpack",
            stock_id="rocketnautics:crafting/equipment/jetpack",
            depends_on=["industrial_colonies:space/life_support/oxygen_gear"],
        ),
    ]


def _ad_astra_recipes() -> list[Recipe]:
    return [
        _grid(
            recipe_id="industrial_colonies:space_coverage/compressor",
            node="CR02 — Station Fabrication",
            phase="Orbital Engineering",
            order=371,
            comment=(
                "Build a four-piston pressure press around a motor, geared drive, "
                "steel mechanism, and through-pipe in a heavy frame"
            ),
            pattern=[" P P ", "HCMCH", "HSGSH", " P P "],
            key={
                "P": "minecraft:piston",
                "H": "ad_astra:steel_panel",
                "C": "tfmg:steel_cogwheel",
                "M": "tfmg:electric_motor",
                "S": "tfmg:steel_mechanism",
                "G": "tfmg:steel_pipe",
            },
            output="ad_astra:compressor",
            stock_id="ad_astra:compressor",
            depends_on=["industrial_colonies:space/station/steel_panel"],
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/etrionic_blast_furnace",
            node="CR02 — Station Fabrication",
            phase="Orbital Engineering",
            order=372,
            comment=(
                "Stack refractory brick, a blast stove, resistive heat, pressure "
                "hardware, and supervised pumping into an orbital-grade furnace"
            ),
            pattern=[" FBF ", "H R H", "H C H", " EPE "],
            key={
                "F": "tfmg:fireproof_bricks",
                "B": "tfmg:blast_stove",
                "H": "tfmg:heavy_machinery_casing",
                "R": "mekanism:resistive_heater",
                "C": "ad_astra:compressor",
                "E": "tfmg:electric_pump",
                "P": "minecraft:blast_furnace",
            },
            output="ad_astra:etrionic_blast_furnace",
            stock_id="ad_astra:etrionic_blast_furnace",
            depends_on=["industrial_colonies:space_coverage/compressor"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/radio",
            node="CR02 — Orbital Guidance",
            phase="Orbital Engineering",
            order=102,
            comment=(
                "Populate an etched TFMG board with a long-range modem, signal "
                "processor, capacitor, antenna lead, and titanium enclosure"
            ),
            input_item="tfmg:etched_circuit_board",
            output="ad_astra:radio",
            ingredients=[
                "computercraft:wireless_modem_advanced",
                "ae2:calculation_processor",
                "tfmg:capacitor_item",
                "tfmg:aluminum_wire",
                "rocketnautics:titanium_sheet",
            ],
            casing="refined_radiance",
            stock_id="ad_astra:radio",
            depends_on=["industrial_colonies:space/orbital_flight_computer"],
        ),
        _compacting(
            recipe_id="industrial_colonies:space_coverage/steel_cable",
            node="CR02 — Station Fabrication",
            phase="Orbital Engineering",
            order=373,
            comment=(
                "Laminate a sixteen-cable station run from TFMG copper conductor, "
                "rubber insulation, and a thin heavy-steel protective jacket"
            ),
            machine="createcasing:copper_press",
            inputs=[
                "16x tfmg:copper_wire",
                "4x tfmg:rubber_sheet",
                "2x tfmg:heavy_plate",
            ],
            output="16x ad_astra:steel_cable",
            stock_id="ad_astra:steel_cable",
        ),
        _compacting(
            recipe_id="industrial_colonies:space_coverage/desh_cable",
            node="CR02 — Lunar Metallurgy",
            phase="Planetary Industry",
            order=81,
            comment=(
                "Re-jacket one station cable batch in conductive Desh plates and "
                "radiation-resistant plastic without discarding its copper core"
            ),
            machine="createcasing:refined_radiance_press",
            inputs=[
                "16x ad_astra:steel_cable",
                "4x ad_astra:desh_plate",
                "2x tfmg:plastic_sheet",
            ],
            output="16x ad_astra:desh_cable",
            stock_id="ad_astra:desh_cable",
            depends_on=[
                "industrial_colonies:space_coverage/steel_cable",
                "industrial_colonies:planetary/desh/plate",
            ],
        ),
        _compacting(
            recipe_id="industrial_colonies:space_coverage/desh_fluid_pipe",
            node="CR02 — Lunar Metallurgy",
            phase="Planetary Industry",
            order=82,
            comment=(
                "Form sixteen vacuum-service pipes from TFMG steel tubes, Desh "
                "outer shells, glass inspection liners, and rubber seals"
            ),
            machine="createcasing:refined_radiance_press",
            inputs=[
                "16x tfmg:steel_pipe",
                "4x ad_astra:desh_plate",
                "4x minecraft:glass",
                "2x tfmg:rubber_sheet",
            ],
            output="16x ad_astra:desh_fluid_pipe",
            stock_id="ad_astra:desh_fluid_pipe",
            depends_on=["industrial_colonies:planetary/desh/plate"],
        ),
        _compacting(
            recipe_id="industrial_colonies:space_coverage/ostrum_fluid_pipe",
            node="CR02 — Martian Metallurgy",
            phase="Planetary Industry",
            order=151,
            comment=(
                "Upgrade a complete Desh pipe run with Ostrum pressure shells, "
                "magnetic reinforcement, and new service seals"
            ),
            machine="createcasing:refined_radiance_press",
            inputs=[
                "16x ad_astra:desh_fluid_pipe",
                "4x ad_astra:ostrum_plate",
                "2x tfmg:magnetic_alloy_sheet",
                "2x tfmg:rubber_sheet",
            ],
            output="16x ad_astra:ostrum_fluid_pipe",
            stock_id="ad_astra:ostrum_fluid_pipe",
            depends_on=[
                "industrial_colonies:space_coverage/desh_fluid_pipe",
                "industrial_colonies:planetary/ostrum/plate",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/steel_tank",
            node="CR02 — Pressure Hardware",
            phase="Orbital Engineering",
            order=181,
            comment=(
                "Turn a basic gas tank into a serviceable steel pressure vessel "
                "with heavy cheeks, a pipe neck, elastomer seal, and fastener"
            ),
            input_item="ad_astra:gas_tank",
            output="ad_astra:steel_tank",
            ingredients=[
                "tfmg:heavy_plate",
                "tfmg:steel_pipe",
                "tfmg:rubber_sheet",
                "tfmg:screw",
            ],
            casing="railway",
            stock_id="ad_astra:steel_tank",
            depends_on=["industrial_colonies:space/life_support/gas_tank"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/desh_tank",
            node="CR02 — Lunar Metallurgy",
            phase="Planetary Industry",
            order=83,
            comment=(
                "Overwrap the steel pressure vessel with two formed Desh layers, "
                "a renewed rubber seal, and a titanium service neck"
            ),
            input_item="ad_astra:steel_tank",
            output="ad_astra:desh_tank",
            ingredients=[
                "ad_astra:desh_plate",
                "tfmg:rubber_sheet",
                "ad_astra:desh_plate",
                "rocketnautics:titanium_sheet",
            ],
            casing="refined_radiance",
            stock_id="ad_astra:desh_tank",
            depends_on=[
                "industrial_colonies:space_coverage/steel_tank",
                "industrial_colonies:planetary/desh/plate",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/ostrum_tank",
            node="CR02 — Martian Metallurgy",
            phase="Planetary Industry",
            order=152,
            comment=(
                "Refit the lunar tank with dual Ostrum shells, magnetic bracing, "
                "and a fresh high-pressure seal"
            ),
            input_item="ad_astra:desh_tank",
            output="ad_astra:ostrum_tank",
            ingredients=[
                "ad_astra:ostrum_plate",
                "tfmg:magnetic_alloy_sheet",
                "ad_astra:ostrum_plate",
                "tfmg:rubber_sheet",
            ],
            casing="refined_radiance",
            stock_id="ad_astra:ostrum_tank",
            depends_on=[
                "industrial_colonies:space_coverage/desh_tank",
                "industrial_colonies:planetary/ostrum/plate",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/calorite_tank",
            node="CR02 — Calorite Metallurgy",
            phase="Planetary Industry",
            order=301,
            comment=(
                "Apply two Calorite thermal shells, a plastic isolation layer, "
                "and titanium-alloy service armor to the Ostrum pressure vessel"
            ),
            input_item="ad_astra:ostrum_tank",
            output="ad_astra:calorite_tank",
            ingredients=[
                "ad_astra:calorite_plate",
                "tfmg:plastic_sheet",
                "ad_astra:calorite_plate",
                "rocketnautics:titanium_alloy_sheet",
            ],
            casing="refined_radiance",
            stock_id="ad_astra:calorite_tank",
            depends_on=[
                "industrial_colonies:space_coverage/ostrum_tank",
                "industrial_colonies:planetary/calorite/plate",
            ],
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/engine_frame",
            node="CR02 — Station Fabrication",
            phase="Orbital Engineering",
            order=374,
            comment=(
                "Brace a TFMG steel frame with crossed rods, heavy thrust plates, "
                "and a central service mechanism"
            ),
            pattern=["RHR", "FSF", "RHR"],
            key={
                "R": "ad_astra:steel_rod",
                "H": "ad_astra:steel_panel",
                "F": "tfmg:steel_frame",
                "S": "tfmg:steel_mechanism",
            },
            output="ad_astra:engine_frame",
            stock_id="ad_astra:engine_frame",
            recipe_type="shaped",
            depends_on=["industrial_colonies:space/station/steel_panel"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/steel_engine",
            node="CR02 — Station Fabrication",
            phase="Orbital Engineering",
            order=375,
            comment=(
                "Populate the engine frame with circulation, rotor, stator, fuel "
                "pump, and a geared steel power section"
            ),
            input_item="ad_astra:engine_frame",
            output="ad_astra:steel_engine",
            ingredients=[
                "ad_astra:fan",
                "tfmg:rotor",
                "tfmg:stator",
                "tfmg:electric_pump",
                "tfmg:steel_mechanism",
            ],
            casing="railway",
            stock_id="ad_astra:steel_engine",
            depends_on=[
                "industrial_colonies:space_coverage/engine_frame",
                "industrial_colonies:space/life_support/fan",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/desh_engine",
            node="CR02 — Lunar Metallurgy",
            phase="Planetary Industry",
            order=84,
            comment=(
                "Refit the steel engine with a Desh hot section, duplicated fan, "
                "electromagnetic drive, and elite supervision"
            ),
            input_item="ad_astra:steel_engine",
            output="ad_astra:desh_engine",
            ingredients=[
                "ad_astra:desh_plate",
                "ad_astra:fan",
                "tfmg:electromagnetic_coil",
                "mekanism:elite_control_circuit",
                "ad_astra:desh_plate",
            ],
            casing="refined_radiance",
            stock_id="ad_astra:desh_engine",
            depends_on=[
                "industrial_colonies:space_coverage/steel_engine",
                "industrial_colonies:planetary/desh/plate",
            ],
        ),
        _compacting(
            recipe_id="industrial_colonies:space_coverage/rover_wheel_pair",
            node="CR02 — Planetary Outpost Utilities",
            phase="Planetary Industry",
            order=201,
            comment=(
                "Mold two rover wheels around geared steel hubs with layered TFMG "
                "rubber and magnetic traction reinforcement"
            ),
            machine="createcasing:railway_press",
            inputs=[
                "2x tfmg:steel_cogwheel",
                "8x tfmg:rubber_sheet",
                "2x tfmg:magnetic_alloy_sheet",
            ],
            output="2x ad_astra:wheel",
            stock_id="ad_astra:wheel",
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/tier_1_rover",
            node="CR02 — Planetary Outpost Utilities",
            phase="Planetary Industry",
            order=202,
            comment=(
                "Assemble a four-wheel Desh rover with a steel chassis, pressure "
                "tank, completed engine, radio, navigation console, and host computer"
            ),
            pattern=[" C N ", "RBBBE", " FGF ", "W   W", " W W "],
            key={
                "C": "computercraft:computer_advanced",
                "N": "simulated:navigation_table",
                "R": "ad_astra:radio",
                "B": "ad_astra:desh_plate",
                "E": "ad_astra:desh_engine",
                "F": "tfmg:steel_frame",
                "G": "ad_astra:desh_tank",
                "W": "ad_astra:wheel",
            },
            output="ad_astra:tier_1_rover",
            stock_id="ad_astra:tier_1_rover",
            depends_on=[
                "industrial_colonies:space_coverage/radio",
                "industrial_colonies:space_coverage/desh_engine",
                "industrial_colonies:space_coverage/desh_tank",
                "industrial_colonies:space_coverage/rover_wheel_pair",
                "industrial_colonies:space/navigation/navigation_table",
            ],
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/cryo_freezer",
            node="CR02 — Outer Station Extraction",
            phase="Outer System Industry",
            order=350,
            comment=(
                "Build a deep-space cryogenic plant around blue-ice cold media, "
                "Calorite pressure storage, condensation, pumping, power, and shielding"
            ),
            pattern=[" CIC ", "TPRPT", " FEF ", " HCH ", " TTT "],
            key={
                "C": "ad_astra:calorite_plate",
                "I": "minecraft:blue_ice",
                "T": "rocketnautics:titanium_alloy_sheet",
                "P": "tfmg:electric_pump",
                "R": "mekanism:rotary_condensentrator",
                "F": "ad_astra:calorite_tank",
                "E": "mekanism:advanced_energy_cube",
                "H": "tfmg:heavy_machinery_casing",
            },
            output="ad_astra:cryo_freezer",
            stock_id="ad_astra:cryo_freezer",
            depends_on=[
                "industrial_colonies:space_coverage/calorite_tank",
                "industrial_colonies:outer_station/station_services_controller",
            ],
        ),
    ]


def _flight_and_warp_recipes() -> list[Recipe]:
    return [
        _grid(
            recipe_id="industrial_colonies:space_coverage/gyroscopic_propeller_bearing",
            node="CR02 — Orbital Navigation",
            phase="Orbital Engineering",
            order=322,
            comment=(
                "Stack a brass propeller bearing under opposed gimbal sensors, a "
                "gyroscopic reference, magnetic stabilizer, and motorized drive"
            ),
            pattern=[" G ", "SCS", " M ", " B ", " E "],
            key={
                "G": "simulated:gyroscopic_mechanism",
                "S": "simulated:gimbal_sensor",
                "C": "create:brass_casing",
                "M": "rocketnautics:magnetic_stabilizer",
                "B": "create:mechanical_bearing",
                "E": "tfmg:electric_motor",
            },
            output="aeronautics:gyroscopic_propeller_bearing",
            stock_id="aeronautics:gyroscopic_propeller_bearing",
            depends_on=[
                "industrial_colonies:space_coverage/magnetic_stabilizer",
                "industrial_colonies:space/navigation/gimbal_sensor",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_coverage/warp_memory_card",
            node="CR02 — Interstellar Escape",
            phase="Interstellar Escape",
            order=371,
            comment=(
                "Encode a blank ME pattern with an etched controller, engineering "
                "processor, Moon Crystal reference, and titanium data shield"
            ),
            input_item="ae2:blank_pattern",
            output="cosmowarp:memory_card",
            ingredients=[
                "tfmg:etched_circuit_board",
                "ae2:engineering_processor",
                "cosmowarp:moon_crystal",
                "rocketnautics:titanium_sheet",
            ],
            casing="refined_radiance",
            stock_id="cosmowarp:memory_card",
            depends_on=["industrial_colonies:interstellar/navigation_computer"],
        ),
        _grid(
            recipe_id="industrial_colonies:space_coverage/crystal_driver",
            node="CR02 — Interstellar Escape",
            phase="Interstellar Escape",
            order=375,
            comment=(
                "Build the warp-field driver as a diamond lattice around the signed "
                "crystal, encoded memory, magnetic stabilizers, quantum anchor, "
                "ultimate control, transformer, and one true late-game alloy core"
            ),
            pattern=["  W  ", " AQA ", "MGCGM", " ATUA", "  V  "],
            key={
                "W": "cosmowarp:warp_crystal",
                "A": "rocketnautics:titanium_alloy_sheet",
                "Q": "ae2:quantum_entangled_singularity",
                "M": "cosmowarp:moon_crystal",
                "G": "rocketnautics:magnetic_stabilizer",
                "C": "cosmowarp:memory_card",
                "T": "tfmg:transformer",
                "U": "mekanism:ultimate_control_circuit",
                "V": "allthemodium:unobtainium_vibranium_alloy_ingot",
            },
            output="cosmowarp:crystal_driver",
            stock_id="cosmowarp:crystal_driver",
            depends_on=[
                "industrial_colonies:interstellar/unsigned_route_crystal",
                "industrial_colonies:space_coverage/warp_memory_card",
                "industrial_colonies:space_coverage/magnetic_stabilizer",
            ],
        ),
    ]


def _output_item(output: Any) -> str | None:
    if not isinstance(output, str):
        return None
    value = output.strip()
    value = re.sub(r"^\d+x\s+", "", value)
    return value if ":" in value else None


def _recipe_set() -> list[Recipe]:
    recipes = [
        *_rocketnautics_recipes(),
        *_ad_astra_recipes(),
        *_flight_and_warp_recipes(),
    ]
    ids = [recipe["id"] for recipe in recipes]
    outputs = [_output_item(recipe["output"]) for recipe in recipes]
    removals = [stock for recipe in recipes for stock in recipe["remove"]]
    if len(ids) != len(set(ids)):
        raise ValueError("space coverage defines duplicate managed recipe IDs")
    if len(outputs) != len(set(outputs)):
        raise ValueError("space coverage defines duplicate managed outputs")
    if len(removals) != len(set(removals)):
        raise ValueError("space coverage defines duplicate stock removals")
    return recipes


def _declared_outputs(recipe: Recipe) -> set[str]:
    output = _output_item(recipe.get("output"))
    return {output} if output else set()


def _assert_unclaimed(data: dict[str, Any], recipes: Iterable[Recipe]) -> None:
    recipes = list(recipes)
    owned_ids = {recipe["id"] for recipe in recipes}
    wanted_outputs = {
        output for recipe in recipes for output in _declared_outputs(recipe)
    }
    wanted_removals = {
        stock for recipe in recipes for stock in recipe.get("remove", [])
    }
    for existing in data.get("recipes", []):
        if not isinstance(existing, dict):
            raise TypeError("managed recipe entries must be objects")
        if existing.get("id") in owned_ids:
            continue
        overlap = wanted_outputs & _declared_outputs(existing)
        if overlap:
            raise ValueError(
                "space coverage output is already managed by "
                f"{existing.get('id')}: {sorted(overlap)}"
            )
        removal_overlap = wanted_removals & set(existing.get("remove", []))
        if removal_overlap:
            raise ValueError(
                "space coverage stock ID is already claimed by "
                f"{existing.get('id')}: {sorted(removal_overlap)}"
            )


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = data.setdefault("recipes", [])
    matches = [
        index
        for index, existing in enumerate(recipes)
        if isinstance(existing, dict) and existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"managed recipe is duplicated: {recipe['id']}")
    if matches:
        recipes[matches[0]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def apply(data: dict[str, Any]) -> None:
    """Add the curated space-machine coverage wave to ``data`` in place."""

    recipes = _recipe_set()
    _assert_unclaimed(data, recipes)

    claimed_stock_ids = {
        stock for recipe in recipes for stock in recipe.get("remove", [])
    }
    managed_outputs = {
        output for recipe in recipes for output in _declared_outputs(recipe)
    }
    data["preserve_recipe_ids"] = [
        stock
        for stock in data.get("preserve_recipe_ids", [])
        if stock not in claimed_stock_ids
    ]
    data["additional_removals"] = [
        stock
        for stock in data.get("additional_removals", [])
        if stock not in claimed_stock_ids
    ]
    data["exclude_outputs"] = [
        output
        for output in data.get("exclude_outputs", [])
        if output not in managed_outputs
    ]

    for recipe in recipes:
        _upsert(data, recipe)
