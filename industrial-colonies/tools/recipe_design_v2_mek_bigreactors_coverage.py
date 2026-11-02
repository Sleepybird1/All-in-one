#!/usr/bin/env python3
"""Close important Mekanism and Big Reactors stock-recipe bypasses.

This is a side-effect-free recipe-design module.  ``apply(data)`` mutates only
the supplied managed-recipe dictionary; it does not read or write the seed,
run generators, build the mod, or touch the live pack.

The scope is intentionally selective:

* direct tiered factory recipes remain absent (factories stay installer-only);
* cheap but powerful factory augments receive recognizable component lines;
* Mekanism's thermal and laser infrastructure receives physical assemblies;
* Energizer and Fluidizer internals/ports stop being casing-plus-vanilla rings;
* ordinary glass, access-port conversions, taps, and other sensible structural
  utilities remain stock recipes.

All item and recipe identifiers below were taken from the installed
Mekanism 10.7.19.85 and Extreme Reactors 2.4.28 jars.
"""

from __future__ import annotations

import re
from typing import Any


Recipe = dict[str, Any]


COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
INDUSTRIAL_DEPLOYER = "createcasing:industrial_iron_deployer"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"
WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _base_output(output: object) -> str | None:
    """Return the item id from the managed ``count x item`` output syntax."""

    if not isinstance(output, str):
        return None
    return re.sub(r"^\d+x\s+", "", output)


def _sequence(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    stock_id: str,
    steps: list[Recipe],
    depends_on: list[str] | None = None,
) -> Recipe:
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        # These components do not need one-off unfinished Java items.  The
        # installed generator supports the base item as its own transitional
        # carrier, as already used elsewhere in recipe design v2.
        "transitional": input_item,
        "output": output,
        "loops": 1,
        "steps": steps,
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
    depends_on: list[str] | None = None,
) -> Recipe:
    if not pattern:
        raise ValueError(f"mechanical grid is empty: {recipe_id}")
    width = len(pattern[0])
    if len(pattern) > 5 or width > 5:
        raise ValueError(f"mechanical grid exceeds 5x5: {recipe_id}")
    if any(len(row) != width for row in pattern):
        raise ValueError(f"mechanical grid is not rectangular: {recipe_id}")
    used = set("".join(pattern)) - {" "}
    if used != set(key):
        raise ValueError(
            f"mechanical grid symbols do not match key for {recipe_id}: "
            f"used={sorted(used)}, key={sorted(key)}"
        )
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "mechanical_crafting",
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
) -> Recipe:
    return {
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


def _recipes() -> list[Recipe]:
    recipes: list[Recipe] = [
        # --------------------------------------------------------------
        # Mekanism factory augments.  These are compact modules, so each is
        # manufactured on an electronics line rather than a large 5x5 grid.
        # --------------------------------------------------------------
        _sequence(
            recipe_id="industrial_colonies:mekanism/upgrade/speed",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=700,
            comment=(
                "Populate a TFMG board with a balanced motor/rotor pair, an "
                "osmium timing mass, and an infused drive controller."
            ),
            input_item="tfmg:circuit_board",
            output="mekanism:upgrade_speed",
            stock_id="mekanism:upgrade/speed",
            steps=[
                _deploy("tfmg:electric_motor", COPPER_DEPLOYER),
                _deploy("tfmg:rotor", COPPER_DEPLOYER),
                _deploy("mekanism:dust_osmium", COPPER_DEPLOYER),
                _deploy("mekanism:alloy_infused", COPPER_DEPLOYER),
                _deploy("mekanism:basic_control_circuit", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism/upgrade/energy",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=710,
            comment=(
                "Build the energy augment as a lithium-buffered TFMG power "
                "board instead of recoloring the same stock upgrade pattern."
            ),
            input_item="tfmg:circuit_board",
            output="mekanism:upgrade_energy",
            stock_id="mekanism:upgrade/energy",
            steps=[
                _deploy("tfmg:lithium_charge", COPPER_DEPLOYER),
                _deploy("tfmg:capacitor_item", COPPER_DEPLOYER),
                _deploy("mekanism:energy_tablet", COPPER_DEPLOYER),
                _deploy("mekanism:alloy_infused", COPPER_DEPLOYER),
                _deploy("tfmg:copper_wire", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism/upgrade/chemical",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=720,
            comment=(
                "Equip a protected control board with a metering tank, TFMG "
                "valve, chemical-safe plastic, and its own process controller."
            ),
            input_item="tfmg:circuit_board",
            output="mekanism:upgrade_chemical",
            stock_id="mekanism:upgrade/chemical",
            steps=[
                _deploy("mekanism:basic_chemical_tank", COPPER_DEPLOYER),
                _deploy("tfmg:steel_fluid_valve", COPPER_DEPLOYER),
                _deploy("tfmg:plastic_sheet", COPPER_DEPLOYER),
                _deploy("mekanism:alloy_infused", COPPER_DEPLOYER),
                _deploy("mekanism:basic_control_circuit", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism/upgrade/anchor",
            node="CR01 — World Loading Technology",
            phase="High-Energy Grid",
            order=730,
            comment=(
                "Calibrate a late spatial anchor around a teleportation core, "
                "AE spatial lattice, magnetic alloy, and engineering governor."
            ),
            input_item="mekanism:advanced_control_circuit",
            output="mekanism:upgrade_anchor",
            stock_id="mekanism:upgrade/anchor",
            steps=[
                _deploy("mekanism:teleportation_core", WEATHERED_DEPLOYER),
                _deploy("ae2:spatial_pylon", WEATHERED_DEPLOYER),
                _deploy("tfmg:magnetic_alloy_ingot", WEATHERED_DEPLOYER),
                _deploy("mekanism:alloy_reinforced", WEATHERED_DEPLOYER),
                _deploy("ae2:engineering_processor", WEATHERED_DEPLOYER),
                _press(WEATHERED_PRESS),
            ],
        ),

        # --------------------------------------------------------------
        # Mekanism electrochemical and thermal infrastructure.
        # --------------------------------------------------------------
        _grid(
            recipe_id="industrial_colonies:mekanism/electric_pump",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=740,
            comment=(
                "Build a vertical powered pump from a real Create pump and "
                "TFMG valve, motor, steel body, controller, and osmium foot."
            ),
            pattern=[" B ", "VPV", "MSC", "OOO"],
            key={
                "B": "minecraft:bucket",
                "V": "tfmg:steel_fluid_valve",
                "P": "create:mechanical_pump",
                "M": "tfmg:electric_motor",
                "S": "mekanism:steel_casing",
                "C": "mekanism:basic_control_circuit",
                "O": "mekanism:ingot_osmium",
            },
            output="mekanism:electric_pump",
            stock_id="mekanism:electric_pump",
        ),
        _compacting(
            recipe_id="industrial_colonies:mekanism/thermal_evaporation/block_batch",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=750,
            comment=(
                "Roll copper heat faces, heavy plate, pipe, and refractory "
                "lining into an economical eight-block evaporation tower batch."
            ),
            machine=INDUSTRIAL_PRESS,
            inputs=[
                "4x tfmg:steel_casing",
                "8x create:copper_sheet",
                "4x tfmg:heavy_plate",
                "4x tfmg:steel_pipe",
                "2x tfmg:fireproof_bricks",
            ],
            output="8x mekanism:thermal_evaporation_block",
            stock_id="mekanism:thermal_evaporation/block",
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism/thermal_evaporation/controller",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=760,
            comment=(
                "Instrument an evaporation shell with a TFMG process vat, pump, "
                "solar sensor, capacitor, sight glass, and advanced controller."
            ),
            input_item="mekanism:thermal_evaporation_block",
            output="mekanism:thermal_evaporation_controller",
            stock_id="mekanism:thermal_evaporation/controller",
            steps=[
                _deploy("tfmg:steel_chemical_vat", INDUSTRIAL_DEPLOYER),
                _deploy("mekanism:electric_pump", INDUSTRIAL_DEPLOYER),
                _deploy("minecraft:daylight_detector", INDUSTRIAL_DEPLOYER),
                _deploy("tfmg:capacitor_item", INDUSTRIAL_DEPLOYER),
                _deploy("#c:glass_panes", INDUSTRIAL_DEPLOYER),
                _deploy("mekanism:advanced_control_circuit", INDUSTRIAL_DEPLOYER),
                _press(INDUSTRIAL_PRESS),
            ],
            depends_on=[
                "industrial_colonies:mekanism/thermal_evaporation/block_batch",
                "industrial_colonies:mekanism/electric_pump",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism/thermal_evaporation/valve",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=770,
            comment=(
                "Convert one tower shell into a service valve with TFMG flow "
                "hardware, a steel manifold, and an advanced metering circuit."
            ),
            input_item="mekanism:thermal_evaporation_block",
            output="mekanism:thermal_evaporation_valve",
            stock_id="mekanism:thermal_evaporation/valve",
            steps=[
                _deploy("tfmg:steel_fluid_valve", INDUSTRIAL_DEPLOYER),
                _deploy("tfmg:steel_pipe", INDUSTRIAL_DEPLOYER),
                _deploy("create:mechanical_pump", INDUSTRIAL_DEPLOYER),
                _deploy("mekanism:advanced_control_circuit", INDUSTRIAL_DEPLOYER),
                _deploy("tfmg:heavy_plate", INDUSTRIAL_DEPLOYER),
                _press(INDUSTRIAL_PRESS),
            ],
            depends_on=["industrial_colonies:mekanism/thermal_evaporation/block_batch"],
        ),
        _compacting(
            recipe_id="industrial_colonies:mekanism/boiler/casing_batch",
            node="CR01 — High-Energy Distribution",
            phase="High-Energy Grid",
            order=780,
            comment=(
                "Pressure-form steel shells, heavy plate, pipe, and fireproof "
                "brick into eight reusable boiler casing sections."
            ),
            machine=RAILWAY_PRESS,
            inputs=[
                "4x tfmg:steel_casing",
                "8x tfmg:heavy_plate",
                "4x tfmg:steel_pipe",
                "4x tfmg:fireproof_bricks",
                "2x tfmg:steel_mechanism",
            ],
            output="8x mekanism:boiler_casing",
            stock_id="mekanism:boiler_casing",
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism/boiler/valve",
            node="CR01 — High-Energy Distribution",
            phase="High-Energy Grid",
            order=790,
            comment=(
                "Machine a boiler service port from a TFMG valve, pump, steel "
                "manifold, and an advanced safety controller."
            ),
            input_item="mekanism:boiler_casing",
            output="2x mekanism:boiler_valve",
            stock_id="mekanism:boiler_valve",
            steps=[
                _deploy("tfmg:steel_fluid_valve", RAILWAY_DEPLOYER),
                _deploy("tfmg:electric_pump", RAILWAY_DEPLOYER),
                _deploy("tfmg:steel_pipe", RAILWAY_DEPLOYER),
                _deploy("mekanism:advanced_control_circuit", RAILWAY_DEPLOYER),
                _deploy("tfmg:heavy_plate", RAILWAY_DEPLOYER),
                _press(RAILWAY_PRESS),
            ],
            depends_on=["industrial_colonies:mekanism/boiler/casing_batch"],
        ),
        _grid(
            recipe_id="industrial_colonies:mekanism/boiler/pressure_disperser",
            node="CR01 — High-Energy Distribution",
            phase="High-Energy Grid",
            order=800,
            comment=(
                "Lay out an open steam-distribution grate from heavy perimeter "
                "plate, iron vents, a crossed pipe manifold, and infused bracing."
            ),
            pattern=["HBBH", "PVVP", "AAAA", "HBBH"],
            key={
                "H": "tfmg:heavy_plate",
                "B": "minecraft:iron_bars",
                "P": "tfmg:steel_pipe",
                "V": "tfmg:steel_fluid_valve",
                "A": "mekanism:alloy_infused",
            },
            output="mekanism:pressure_disperser",
            stock_id="mekanism:pressure_disperser",
            depends_on=["industrial_colonies:mekanism/boiler/casing_batch"],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism/boiler/superheating_element",
            node="CR01 — High-Energy Distribution",
            phase="High-Energy Grid",
            order=810,
            comment=(
                "Wind and insulate a steel heating body with a transformer, "
                "resistor, capacitor, copper conductor, and reinforced alloy."
            ),
            input_item="mekanism:steel_casing",
            output="mekanism:superheating_element",
            stock_id="mekanism:superheating_element",
            steps=[
                _deploy("tfmg:transformer", RAILWAY_DEPLOYER),
                _deploy("tfmg:resistor", RAILWAY_DEPLOYER),
                _deploy("tfmg:capacitor_item", RAILWAY_DEPLOYER),
                _deploy("tfmg:copper_wire", RAILWAY_DEPLOYER),
                _deploy("mekanism:alloy_reinforced", RAILWAY_DEPLOYER),
                _deploy("tfmg:fireproof_bricks", RAILWAY_DEPLOYER),
                _press(RAILWAY_PRESS),
            ],
            depends_on=["industrial_colonies:mekanism/boiler/casing_batch"],
        ),

        # --------------------------------------------------------------
        # Mekanism coherent-energy hardware.
        # --------------------------------------------------------------
        _sequence(
            recipe_id="industrial_colonies:mekanism/laser/emitter",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=820,
            comment=(
                "Align a high-energy emitter inside a steel body with its tablet, "
                "magnetic focusing alloy, diamond optic, and local controller."
            ),
            input_item="mekanism:steel_casing",
            output="mekanism:laser",
            stock_id="mekanism:laser",
            steps=[
                _deploy("mekanism:energy_tablet", WEATHERED_DEPLOYER),
                _deploy("tfmg:magnetic_alloy_ingot", WEATHERED_DEPLOYER),
                _deploy("mekanism:alloy_reinforced", WEATHERED_DEPLOYER),
                _deploy("minecraft:diamond", WEATHERED_DEPLOYER),
                _deploy("mekanism:advanced_control_circuit", WEATHERED_DEPLOYER),
                _deploy("tfmg:capacitor_item", WEATHERED_DEPLOYER),
                _press(WEATHERED_PRESS),
            ],
        ),
        _grid(
            recipe_id="industrial_colonies:mekanism/laser/amplifier",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=830,
            comment=(
                "Build an asymmetric beam amplifier around a real laser, "
                "advanced energy buffer, capacitor bank, optic, and laminated magnetic exit."
            ),
            pattern=["HHHD", "CEEG", "CBA ", "HHHD"],
            key={
                "H": "tfmg:heavy_plate",
                "D": "minecraft:diamond",
                "C": "tfmg:capacitor_item",
                "E": "mekanism:energy_tablet",
                "G": "tfmg:laminated_magnetic_alloy_block",
                "B": "mekanism:advanced_energy_cube",
                "A": "mekanism:laser",
            },
            output="mekanism:laser_amplifier",
            stock_id="mekanism:laser_amplifier",
            depends_on=["industrial_colonies:mekanism/laser/emitter"],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism/laser/tractor_beam",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=840,
            comment=(
                "Turn the amplifier into a captured-item beamline with personal "
                "storage, routed logistics, a teleport core, and ultimate control."
            ),
            input_item="mekanism:laser_amplifier",
            output="mekanism:laser_tractor_beam",
            stock_id="mekanism:laser_tractor_beam",
            steps=[
                _deploy("mekanism:personal_chest", WEATHERED_DEPLOYER),
                _deploy("mekanism:advanced_logistical_transporter", WEATHERED_DEPLOYER),
                _deploy("mekanism:teleportation_core", WEATHERED_DEPLOYER),
                _deploy("mekanism:ultimate_control_circuit", WEATHERED_DEPLOYER),
                _deploy("tfmg:magnetic_alloy_ingot", WEATHERED_DEPLOYER),
                _press(WEATHERED_PRESS),
            ],
            depends_on=["industrial_colonies:mekanism/laser/amplifier"],
        ),

        # --------------------------------------------------------------
        # Extreme Reactors Energizer internals and interfaces.  The casing and
        # controller already have managed recipes; these are the remaining
        # functional blocks whose installed recipes are vanilla-material rings.
        # --------------------------------------------------------------
        _sequence(
            recipe_id="industrial_colonies:bigreactors/energizer/energy_core",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=420,
            comment=(
                "Grow an Energizer resonance core around a proven Mekanism "
                "buffer, Magentite seed, Anglesite optics, and engineering control."
            ),
            input_item="mekanism:advanced_energy_cube",
            output="bigreactors:energycore",
            stock_id="bigreactors:energizer/energycore",
            steps=[
                _deploy("bigreactors:magentite_ingot", RADIANCE_DEPLOYER),
                _deploy("bigreactors:anglesite_crystal", RADIANCE_DEPLOYER),
                _deploy("bigreactors:anglesite_crystal", RADIANCE_DEPLOYER),
                _deploy("minecraft:ender_eye", RADIANCE_DEPLOYER),
                _deploy("mekanism:alloy_atomic", RADIANCE_DEPLOYER),
                _deploy("ae2:engineering_processor", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/energizer/casing"],
        ),
        _sequence(
            recipe_id="industrial_colonies:bigreactors/energizer/energy_cell",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=430,
            comment=(
                "Sleeve a completed resonance core in paired Benitoite optics, "
                "an induction buffer, magnetic laminations, and radiance shielding."
            ),
            input_item="bigreactors:energycore",
            output="bigreactors:energizercell",
            stock_id="bigreactors:energizer/energizercell",
            steps=[
                _deploy("bigreactors:benitoite_crystal", RADIANCE_DEPLOYER),
                _deploy("bigreactors:benitoite_crystal", RADIANCE_DEPLOYER),
                _deploy("mekanism:elite_induction_cell", RADIANCE_DEPLOYER),
                _deploy("tfmg:magnetic_alloy_ingot", RADIANCE_DEPLOYER),
                _deploy("create:refined_radiance_casing", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/energizer/energy_core"],
        ),
        _sequence(
            recipe_id="industrial_colonies:bigreactors/energizer/charging_port",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=440,
            comment=(
                "Convert an Energizer shell into a controlled charging face with "
                "an induction port, tablet, capacitor, transformer, and interlock."
            ),
            input_item="bigreactors:energizercasing",
            output="bigreactors:energizerchargingport_fe",
            stock_id="bigreactors:energizer/chargingport_fe",
            steps=[
                _deploy("mekanism:induction_port", RADIANCE_DEPLOYER),
                _deploy("mekanism:energy_tablet", RADIANCE_DEPLOYER),
                _deploy("tfmg:capacitor_item", RADIANCE_DEPLOYER),
                _deploy("tfmg:transformer", RADIANCE_DEPLOYER),
                _deploy("mekanism:elite_control_circuit", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/energizer/casing"],
        ),
        _sequence(
            recipe_id="industrial_colonies:bigreactors/energizer/computer_port",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=450,
            comment=(
                "Network an Energizer casing with a wired modem, redstone relay, "
                "engineering processor, protected leads, and elite interface logic."
            ),
            input_item="bigreactors:energizercasing",
            output="bigreactors:energizercomputerport",
            stock_id="bigreactors:energizer/computerport",
            steps=[
                _deploy("computercraft:wired_modem", RADIANCE_DEPLOYER),
                _deploy("computercraft:redstone_relay", RADIANCE_DEPLOYER),
                _deploy("ae2:engineering_processor", RADIANCE_DEPLOYER),
                _deploy("tfmg:copper_wire", RADIANCE_DEPLOYER),
                _deploy("mekanism:elite_control_circuit", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/energizer/casing"],
        ),
        _sequence(
            recipe_id="industrial_colonies:bigreactors/energizer/power_port",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=460,
            comment=(
                "Build the passive grid interface from an advanced energy cube, "
                "TFMG transformer/cable hub, connector, and local capacitor."
            ),
            input_item="bigreactors:energizercasing",
            output="bigreactors:energizerpowerport_fe",
            stock_id="bigreactors:energizer/powerport_fe",
            steps=[
                _deploy("mekanism:advanced_energy_cube", RADIANCE_DEPLOYER),
                _deploy("tfmg:transformer", RADIANCE_DEPLOYER),
                _deploy("tfmg:steel_cable_hub", RADIANCE_DEPLOYER),
                _deploy("electroenergetics:connector", RADIANCE_DEPLOYER),
                _deploy("tfmg:capacitor_item", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/energizer/casing"],
        ),
        _sequence(
            recipe_id="industrial_colonies:bigreactors/energizer/active_power_port",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=470,
            comment=(
                "Instrument the passive power interface for active transfer with "
                "a double connector, current transformer, relay, and elite governor."
            ),
            input_item="bigreactors:energizerpowerport_fe",
            output="bigreactors:energizerpowerport_fe_active",
            stock_id="bigreactors:energizer/powerport_fe_active",
            steps=[
                _deploy("electroenergetics:double_connector", RADIANCE_DEPLOYER),
                _deploy("electroenergetics:current_transformer", RADIANCE_DEPLOYER),
                _deploy("computercraft:redstone_relay", RADIANCE_DEPLOYER),
                _deploy("mekanism:elite_control_circuit", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/energizer/power_port"],
        ),

        # --------------------------------------------------------------
        # Extreme Reactors Fluidizer interfaces.  Glass remains the sensible
        # stock casing conversion; the process-bearing ports do not.
        # --------------------------------------------------------------
        _sequence(
            recipe_id="industrial_colonies:bigreactors/fluidizer/fluid_injector",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=480,
            comment=(
                "Assemble the fluid feed from a TFMG electric pump, chemical vat, "
                "metering valve, Mekanism tank, and advanced process control."
            ),
            input_item="bigreactors:fluidizercasing",
            output="bigreactors:fluidizerfluidinjector",
            stock_id="bigreactors:fluidizer/fluidinjector",
            steps=[
                _deploy("tfmg:electric_pump", RADIANCE_DEPLOYER),
                _deploy("tfmg:steel_chemical_vat", RADIANCE_DEPLOYER),
                _deploy("tfmg:steel_fluid_valve", RADIANCE_DEPLOYER),
                _deploy("mekanism:advanced_chemical_tank", RADIANCE_DEPLOYER),
                _deploy("mekanism:advanced_control_circuit", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/fluidizer/casing"],
        ),
        _sequence(
            recipe_id="industrial_colonies:bigreactors/fluidizer/solid_injector",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=490,
            comment=(
                "Fit a Fluidizer shell with a vault-fed smart chute, powered "
                "piston, steel feed mechanism, and advanced dosing controller."
            ),
            input_item="bigreactors:fluidizercasing",
            output="bigreactors:fluidizersolidinjector",
            stock_id="bigreactors:fluidizer/solidinjector",
            steps=[
                _deploy("create:item_vault", RADIANCE_DEPLOYER),
                _deploy("create:smart_chute", RADIANCE_DEPLOYER),
                _deploy("create:mechanical_piston", RADIANCE_DEPLOYER),
                _deploy("tfmg:steel_mechanism", RADIANCE_DEPLOYER),
                _deploy("mekanism:advanced_control_circuit", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/fluidizer/casing"],
        ),
        _sequence(
            recipe_id="industrial_colonies:bigreactors/fluidizer/output_port",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=500,
            comment=(
                "Build a controlled product outlet from a storage vault, smart "
                "chute, ME storage bus, steel mechanism, and advanced circuit."
            ),
            input_item="bigreactors:fluidizercasing",
            output="bigreactors:fluidizeroutputport",
            stock_id="bigreactors:fluidizer/outputport",
            steps=[
                _deploy("create:item_vault", RADIANCE_DEPLOYER),
                _deploy("create:smart_chute", RADIANCE_DEPLOYER),
                _deploy("ae2:storage_bus", RADIANCE_DEPLOYER),
                _deploy("tfmg:steel_mechanism", RADIANCE_DEPLOYER),
                _deploy("mekanism:advanced_control_circuit", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/fluidizer/casing"],
        ),
        _sequence(
            recipe_id="industrial_colonies:bigreactors/fluidizer/power_port",
            node="CR01 — First Criticality",
            phase="Nuclear Engineering",
            order=510,
            comment=(
                "Terminate the Fluidizer grid feed through a transformer, energy "
                "buffer, steel cable hub, connector, and elite safety circuit."
            ),
            input_item="bigreactors:fluidizercasing",
            output="bigreactors:fluidizerpowerport",
            stock_id="bigreactors:fluidizer/powerport",
            steps=[
                _deploy("tfmg:transformer", RADIANCE_DEPLOYER),
                _deploy("mekanism:advanced_energy_cube", RADIANCE_DEPLOYER),
                _deploy("tfmg:steel_cable_hub", RADIANCE_DEPLOYER),
                _deploy("electroenergetics:connector", RADIANCE_DEPLOYER),
                _deploy("mekanism:elite_control_circuit", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
            depends_on=["industrial_colonies:bigreactors/fluidizer/casing"],
        ),
    ]
    return recipes


# Public, review-friendly exact coverage.  This is derived from the recipe
# declarations so the documentation cannot drift from the executable module.
COVERAGE: dict[str, tuple[str, ...]] = {
    _base_output(recipe["output"]): tuple(recipe["remove"])
    for recipe in _recipes()
    if _base_output(recipe["output"]) is not None
}


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed recipe seed must contain a recipes list")

    recipe_id = recipe["id"]
    output = _base_output(recipe["output"])
    matches = [index for index, value in enumerate(recipes) if value.get("id") == recipe_id]
    if len(matches) > 1:
        raise ValueError(f"duplicate managed recipe id: {recipe_id}")

    # Never silently steal an output from another hand-authored module.  This
    # also guards against accidental overlap with user-owned recipes.
    conflicting = [
        value.get("id")
        for value in recipes
        if value.get("id") != recipe_id and _base_output(value.get("output")) == output
    ]
    if conflicting:
        raise ValueError(
            f"managed output {output} is already owned by {sorted(str(v) for v in conflicting)}"
        )

    if matches:
        recipes[matches[0]] = recipe
    else:
        recipes.append(recipe)


def apply(data: dict[str, Any]) -> None:
    """Apply all 25 audited recipes idempotently to ``data`` in place."""

    planned = _recipes()
    if len(planned) != 25:
        raise AssertionError(f"coverage drifted from 25 recipes to {len(planned)}")
    if len({recipe["id"] for recipe in planned}) != len(planned):
        raise ValueError("coverage module contains duplicate managed recipe ids")
    if any("factory" in str(recipe.get("output")) for recipe in planned):
        raise AssertionError("direct factory crafting must stay installer-only")

    user_owned = set(data.get("user_owned_outputs", []))
    overlap = sorted(output for output in COVERAGE if output in user_owned)
    if overlap:
        raise ValueError(f"coverage overlaps user-owned recipe outputs: {overlap}")

    for recipe in planned:
        _upsert(data, recipe)

    preserve = data.setdefault("preserve_recipe_ids", [])
    if not isinstance(preserve, list):
        raise TypeError("preserve_recipe_ids must be a list")
    owned_stock_ids = {stock_id for ids in COVERAGE.values() for stock_id in ids}
    preserve[:] = [recipe_id for recipe_id in preserve if recipe_id not in owned_stock_ids]

    excluded = data.setdefault("exclude_outputs", [])
    if not isinstance(excluded, list):
        raise TypeError("exclude_outputs must be a list")
    for output in COVERAGE:
        if output not in excluded:
            excluded.append(output)
