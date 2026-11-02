"""AE2, MEGA Cells, Applied Create, and Advanced AE recipe redesign (v3).

This pass deliberately targets the physical-manufacturing problems called out
in the live KubeJSGen review:

* cable bandwidth is a cheap, balanced batch ladder instead of a 5x5 ring;
* terminals and drive hardware are assembled from recognizable subassemblies;
* cell components are populated boards, while finished cells are pressure-
  sealed housings (a justified use of compacting);
* MEGA compute and storage hardware uses the Train/Railway production line;
* the Spatial Anchor consumes the user-owned Chunk Controller and the real
  128-cubed spatial core, without using an Industrial Iron compacting recipe;
* quantum hardware is a Refined Radiance / exotic-alloy endgame line.

``apply`` mutates only the supplied seed dictionary and is idempotent.  The
module never reads or writes the live KubeJSGen project.  It is intentionally
kept separate from the v2 driver so the root integration can place it after
all v2 AE-family coverage modules.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable


COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"
WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"

DIGITAL = "Digital Logistics"
MEKANIZED = "Mekanized Industry"
HIGH_ENERGY = "High-Energy Grid"
NUCLEAR = "Nuclear Engineering"

ME_NODE = "CR01 — ME System Basics"
STORAGE_NODE = "CR01 — Advanced ME Storage"
CRAFTING_NODE = "CR01 — Enhanced ME Crafting Upgrade"
MID_CRAFTING_NODE = "CR01 — Advanced Digital Crafting"
MID_STORAGE_NODE = "CR01 — Improved Digital Chemical Storage"
SPATIAL_NODE = "CR01 — Spacial Storage Tech"
WORLD_NODE = "CR01 — World Loading Technology"
QUANTUM_NODE = "CR01 — Overclocked Processors"


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _as_list(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _sequence(
    slug: str,
    *,
    recipe_id: str | None = None,
    phase: str,
    node: str | None,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    deployer: str,
    press: str,
    remove: str | Iterable[str] | None = None,
    loops: int = 1,
    depends_on: Iterable[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": recipe_id or f"industrial_colonies:v3_ae2/{slug}",
        "phase": phase,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": loops,
        "steps": [_deploy(item, deployer) for item in ingredients]
        + [_press(press)],
        "remove": _as_list(remove),
        "exclusive_output": True,
    }
    if node is not None:
        result["node"] = node
    dependencies = list(depends_on or [])
    if dependencies:
        result["depends_on"] = dependencies
    return result


def _compacting(
    slug: str,
    *,
    phase: str,
    node: str | None,
    order: int,
    comment: str,
    machine: str,
    inputs: list[str],
    output: str,
    remove: str | Iterable[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": f"industrial_colonies:v3_ae2/{slug}",
        "phase": phase,
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": inputs,
        "output": output,
        "remove": _as_list(remove),
        "exclusive_output": True,
    }
    if node is not None:
        result["node"] = node
    return result


def _mechanical(
    slug: str,
    *,
    phase: str,
    node: str | None,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    remove: str | Iterable[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": f"industrial_colonies:v3_ae2/{slug}",
        "phase": phase,
        "order": order,
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": _as_list(remove),
        "exclusive_output": True,
    }
    if node is not None:
        result["node"] = node
    return result


def _cable_recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            "fluix_glass_cable_batch",
            phase=DIGITAL,
            node=ME_NODE,
            order=20,
            comment=(
                "Laminate a copper signal strand between quartz glass, fluix "
                "conductor, and plastic insulation; one pass yields eight "
                "practical starter cables"
            ),
            input_item="tfmg:copper_wire",
            output="8x ae2:fluix_glass_cable",
            ingredients=[
                "2x ae2:quartz_glass",
                "ae2:fluix_crystal",
                "tfmg:plastic_sheet",
            ],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
            remove=[
                "ae2:network/cables/glass_fluix",
                "ae2:network/cables/glass_fluix_clean",
            ],
        ),
        _sequence(
            "fluix_smart_cable_batch",
            phase=DIGITAL,
            node=ME_NODE,
            order=31,
            comment=(
                "Instrument four glass cables as one monitored run with logic, "
                "a TFMG transistor, a shield wire, and a plastic data jacket"
            ),
            input_item="ae2:fluix_glass_cable",
            output="4x ae2:fluix_smart_cable",
            ingredients=[
                "3x ae2:fluix_glass_cable",
                "ae2:logic_processor",
                "tfmg:transistor_item",
                "tfmg:copper_wire",
                "tfmg:plastic_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove=[
                "ae2:network/cables/smart_fluix",
                "ae2:network/cables/smart_fluix_clean",
            ],
        ),
        _sequence(
            "fluix_dense_smart_cable_batch",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=26,
            comment=(
                "Bundle sixteen monitored channels behind gold contacts, "
                "coated routing boards, calculation control, and a thick "
                "plastic dielectric; the expensive pass returns all sixteen"
            ),
            input_item="ae2:fluix_smart_cable",
            output="16x ae2:fluix_smart_dense_cable",
            ingredients=[
                "15x ae2:fluix_smart_cable",
                "4x create:golden_sheet",
                "2x tfmg:coated_circuit_board",
                "ae2:calculation_processor",
                "4x tfmg:plastic_sheet",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove=[
                "ae2:network/cables/dense_smart_fluix",
                "ae2:network/cables/dense_smart_fluix_clean",
                "ae2:network/cables/dense_smart_from_smart",
            ],
        ),
    ]


def _electronics_and_machine_recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            "stress_circuit_board",
            phase=DIGITAL,
            node=ME_NODE,
            order=11,
            comment=(
                "Build the Andesite stress board after default Create by "
                "laminating an Andesite sheet with an etched TFMG board, "
                "copper traces, and a plastic dielectric"
            ),
            input_item="createcasing:andesite_sheet",
            output="appliedcreate:stress_circuit_board",
            ingredients=[
                "tfmg:etched_circuit_board",
                "tfmg:copper_wire",
                "tfmg:plastic_sheet",
                "create:cinder_flour",
            ],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
            remove="appliedcreate:stress_circuit_board",
        ),
        _sequence(
            "advanced_stress_circuit_board",
            phase=DIGITAL,
            node=ME_NODE,
            order=24,
            comment=(
                "Turn the Andesite stress board into a Brass multilayer board "
                "with coated routing, semiconductor junctions, and magnetic "
                "clock shielding"
            ),
            input_item="appliedcreate:stress_circuit_board",
            output="appliedcreate:advanced_stress_circuit_board",
            ingredients=[
                "create:brass_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:magnetic_alloy_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="appliedcreate:advanced_stress_circuit_board",
        ),
        _sequence(
            "charger",
            phase=DIGITAL,
            node=ME_NODE,
            order=34,
            comment=(
                "Build a real charging throat around a Copper casing with an "
                "electromagnetic coil, local generator, capacitor, wiring, and "
                "a quartz service window"
            ),
            input_item="create:copper_casing",
            output="ae2:charger",
            ingredients=[
                "tfmg:electromagnetic_coil",
                "tfmg:generator",
                "tfmg:capacitor_item",
                "2x tfmg:copper_wire",
                "ae2:quartz_glass",
            ],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
            remove="ae2:network/blocks/crystal_processing_charger",
        ),
        _sequence(
            "inscriber",
            phase=DIGITAL,
            node=ME_NODE,
            order=35,
            comment=(
                "Assemble the Inscriber as a Brass precision stamping station; "
                "whole processors remain exclusive to the encased assembly line"
            ),
            input_item="minecraft:piston",
            output="ae2:inscriber",
            ingredients=[
                "create:brass_casing",
                "create:precision_mechanism",
                "tfmg:circuit_board",
                "tfmg:electric_motor",
                "ae2:quartz_glass",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="ae2:network/blocks/inscribers",
        ),
        _sequence(
            "crafting_unit",
            phase=DIGITAL,
            node=ME_NODE,
            order=40,
            comment=(
                "Convert a literal crafting table into an ME compute chassis "
                "with a Brass shell, smart bus, logic and stress control, "
                "board backplane, and plastic insulation"
            ),
            input_item="minecraft:crafting_table",
            output="ae2:crafting_unit",
            ingredients=[
                "create:brass_casing",
                "ae2:fluix_smart_cable",
                "ae2:logic_processor",
                "appliedcreate:stress_processor",
                "tfmg:circuit_board",
                "tfmg:plastic_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="ae2:network/crafting/cpu_crafting_unit",
        ),
        _sequence(
            "drive",
            phase=DIGITAL,
            node=ME_NODE,
            order=45,
            comment=(
                "Machine a barrel into an ME Drive by installing four literal "
                "cell trays, a smart backplane, calculation logic, a coated "
                "controller board, tin solder bus, and an insulated Brass enclosure"
            ),
            input_item="minecraft:barrel",
            output="ae2:drive",
            ingredients=[
                "4x ae2:item_cell_housing",
                "ae2:fluix_smart_cable",
                "ae2:logic_processor",
                "tfmg:coated_circuit_board",
                "2x mekanism:ingot_tin",
                "tfmg:plastic_sheet",
                "create:brass_casing",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="ae2:network/blocks/storage_drive",
        ),
        _sequence(
            "terminal",
            phase=DIGITAL,
            node=ME_NODE,
            order=82,
            comment=(
                "Populate an illuminated panel with a smart lead, logic "
                "controller, paired matter-transfer cores, and a plastic face"
            ),
            input_item="ae2:semi_dark_monitor",
            output="ae2:terminal",
            ingredients=[
                "ae2:fluix_smart_cable",
                "ae2:logic_processor",
                "ae2:annihilation_core",
                "ae2:formation_core",
                "tfmg:plastic_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="ae2:network/parts/terminals",
        ),
        _sequence(
            "crafting_terminal",
            phase=MEKANIZED,
            node=MID_CRAFTING_NODE,
            order=70,
            comment=(
                "Upgrade the ME Terminal with a real crafting grid, "
                "calculation processor, blank-pattern buffer, and stress-aware "
                "input controller"
            ),
            input_item="ae2:terminal",
            output="ae2:crafting_terminal",
            ingredients=[
                "minecraft:crafting_table",
                "ae2:calculation_processor",
                "ae2:blank_pattern",
                "appliedcreate:stress_processor",
                "tfmg:plastic_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="ae2:network/parts/terminals_crafting",
        ),
        _sequence(
            "pattern_access_terminal",
            phase=MEKANIZED,
            node=MID_CRAFTING_NODE,
            order=73,
            comment=(
                "Give the terminal direct pattern inventory access through a "
                "provider, capacity controller, smart bus, and logic board"
            ),
            input_item="ae2:terminal",
            output="ae2:pattern_access_terminal",
            ingredients=[
                "ae2:pattern_provider",
                "ae2:capacity_card",
                "ae2:fluix_smart_cable",
                "ae2:logic_processor",
                "tfmg:coated_circuit_board",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="ae2:network/parts/terminals_pattern_access",
        ),
        _sequence(
            "pattern_encoding_terminal",
            phase=MEKANIZED,
            node=MID_CRAFTING_NODE,
            order=74,
            comment=(
                "Add a pattern writer to the crafting terminal with a blank "
                "pattern, calculation processor, coated controller board, "
                "smart cable, and a dedicated display board"
            ),
            input_item="ae2:crafting_terminal",
            output="ae2:pattern_encoding_terminal",
            ingredients=[
                "ae2:blank_pattern",
                "ae2:calculation_processor",
                "tfmg:coated_circuit_board",
                "ae2:fluix_smart_cable",
                "create:display_board",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="ae2:network/parts/terminals_pattern_encoding",
        ),
        _sequence(
            "accumulation_processor",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=72,
            comment=(
                "Fabricate an accumulation processor as a long Brass-line "
                "memory-wafer pass: multilayer board, printed silicon, both "
                "semiconductor junctions, dense capacitance, lithium backing, "
                "stress scheduling, fluix timing, dielectric, and shielding"
            ),
            input_item="megacells:printed_accumulation_processor",
            output="megacells:accumulation_processor",
            ingredients=[
                "tfmg:coated_circuit_board",
                "ae2:printed_silicon",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:capacitor_item",
                "tfmg:lithium_charge",
                "appliedcreate:advanced_stress_processor",
                "ae2:fluix_dust",
                "tfmg:plastic_sheet",
                "tfmg:magnetic_alloy_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove=[
                "megacells:inscriber/accumulation_processor",
                "extendedae:assembler/accumulation_processor",
            ],
        ),
        _sequence(
            "kinetic_energy_acceptor",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=112,
            comment=(
                "Build the kinetic-to-ME converter as a Weathered Iron machine "
                "body with generator, motor, gearbox, transformer, stress "
                "control, dense bus, and a steel load frame"
            ),
            input_item="ae2:energy_acceptor",
            output="appliedcreate:kinetic_energy_acceptor",
            ingredients=[
                "tfmg:generator",
                "tfmg:electric_motor",
                "create:gearbox",
                "tfmg:transformer",
                "appliedcreate:advanced_stress_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:steel_frame",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            remove="appliedcreate:kinetic_energy_acceptor",
        ),
        _sequence(
            "me_gearbox",
            recipe_id="industrial_colonies:appliedcreate/me_gearbox",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=205,
            comment=(
                "Turn a physical gearbox into an ME stress router with P2P "
                "addressing, dense monitored bandwidth, advanced stress logic, "
                "magnetic shielding, motor timing, and a Train-rated frame"
            ),
            input_item="create:gearbox",
            output="appliedcreate:me_gearbox",
            ingredients=[
                "ae2:me_p2p_tunnel",
                "ae2:fluix_smart_dense_cable",
                "appliedcreate:advanced_stress_processor",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:electric_motor",
                "tfmg:steel_frame",
                "create:railway_casing",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove="appliedcreate:me_gearbox",
        ),
        _sequence(
            "cell_workbench",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=116,
            comment=(
                "Build the cell workbench from a real crafting bench, a cell "
                "tray, terminal, calculation controller, smart lead, and "
                "precision adjustment mechanism"
            ),
            input_item="minecraft:crafting_table",
            output="ae2:cell_workbench",
            ingredients=[
                "ae2:item_cell_housing",
                "ae2:terminal",
                "ae2:calculation_processor",
                "ae2:fluix_smart_cable",
                "create:precision_mechanism",
                "tfmg:plastic_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove="ae2:network/blocks/cell_workbench",
        ),
        _sequence(
            "controller",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=118,
            comment=(
                "Upgrade the Energy Acceptor into a controller machine with a "
                "sky-stone shell, engineering processor, transformer, dense "
                "smart bus, and magnetic field frame"
            ),
            input_item="ae2:energy_acceptor",
            output="ae2:controller",
            ingredients=[
                "ae2:smooth_sky_stone_block",
                "ae2:engineering_processor",
                "tfmg:transformer",
                "ae2:fluix_smart_dense_cable",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:steel_frame",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            remove="ae2:network/blocks/controller",
        ),
        _sequence(
            "io_port",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=120,
            comment=(
                "Refit the ME Drive into a bulk IO machine with an interface, "
                "opposed transfer cores, engineering control, a dense bus, "
                "motorized trays, and a steel service frame"
            ),
            input_item="ae2:drive",
            output="ae2:io_port",
            ingredients=[
                "ae2:interface",
                "ae2:annihilation_core",
                "ae2:formation_core",
                "ae2:engineering_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:electric_motor",
                "tfmg:steel_frame",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            remove="ae2:network/blocks/io_port",
        ),
        _sequence(
            "condenser",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=122,
            comment=(
                "Instrument a pressure-rated steel tank as the Matter "
                "Condenser with opposed transfer cores, engineering control, "
                "power entry, vibrant observation glass, and local capacitance"
            ),
            input_item="tfmg:steel_fluid_tank",
            output="ae2:condenser",
            ingredients=[
                "ae2:annihilation_core",
                "ae2:formation_core",
                "ae2:engineering_processor",
                "ae2:energy_acceptor",
                "ae2:quartz_vibrant_glass",
                "tfmg:capacitor_item",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            remove="ae2:network/blocks/io_condenser",
        ),
        _sequence(
            "spatial_pylon_batch",
            phase=HIGH_ENERGY,
            node=SPATIAL_NODE,
            order=210,
            comment=(
                "Assemble four field pylons as a Train-line batch from quartz "
                "frames, fluix conductors, a routed P2P endpoint, transformer, "
                "steel spine, and calculation controller"
            ),
            input_item="ae2:quartz_glass",
            output="4x ae2:spatial_pylon",
            ingredients=[
                "3x ae2:quartz_glass",
                "4x ae2:fluix_glass_cable",
                "ae2:me_p2p_tunnel",
                "tfmg:transformer",
                "tfmg:steel_frame",
                "ae2:calculation_processor",
                "create:railway_casing",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove="ae2:network/blocks/spatial_io_pylon",
        ),
        _sequence(
            "spatial_io_port",
            phase=HIGH_ENERGY,
            node=SPATIAL_NODE,
            order=214,
            comment=(
                "Convert the IO Port into a field gateway with an ME "
                "controller, P2P endpoint, 2-cubed spatial core, engineering "
                "logic, isolated power, and a Weathered machine frame"
            ),
            input_item="ae2:io_port",
            output="ae2:spatial_io_port",
            ingredients=[
                "ae2:controller",
                "ae2:me_p2p_tunnel",
                "ae2:spatial_cell_component_2",
                "ae2:engineering_processor",
                "tfmg:transformer",
                "tfmg:steel_frame",
                "tfmg:plastic_sheet",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            remove="ae2:network/blocks/spatial_io_port",
        ),
        _sequence(
            "spatial_anchor",
            phase=HIGH_ENERGY,
            node=WORLD_NODE,
            order=235,
            comment=(
                "Commission the user-designed Chunk Controller as a Spatial "
                "Anchor by adding the complete IO gateway, 128-cubed spatial "
                "core, four field pylons, redundant power/control, Vibranium "
                "stabilization, and an insulated Railway electronics enclosure"
            ),
            input_item="advancedperipherals:chunk_controller",
            output="ae2:spatial_anchor",
            ingredients=[
                "ae2:spatial_io_port",
                "ae2:spatial_cell_component_128",
                "4x ae2:spatial_pylon",
                "ae2:engineering_processor",
                "appliedcreate:advanced_stress_processor",
                "tfmg:transformer",
                "allthemodium:vibranium_ingot",
                "tfmg:plastic_sheet",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove="ae2:network/blocks/spatial_anchor",
            depends_on=[
                "industrial_colonies:world_loading/chunk_controller",
                "industrial_colonies:v3_ae2/spatial_pylon_batch",
                "industrial_colonies:v3_ae2/spatial_io_port",
            ],
        ),
        _sequence(
            "mega_crafting_unit",
            recipe_id="industrial_colonies:ae2_high_energy/mega_crafting_unit",
            phase=HIGH_ENERGY,
            node=CRAFTING_NODE,
            order=240,
            comment=(
                "Scale the standard crafting unit with accumulation and "
                "engineering processors, smart fluix bandwidth, and a "
                "transformer-backed TFMG control plane."
            ),
            input_item="ae2:crafting_unit",
            output="megacells:mega_crafting_unit",
            ingredients=[
                "megacells:accumulation_processor",
                "ae2:engineering_processor",
                "ae2:fluix_smart_cable",
                "tfmg:transformer",
                "tfmg:circuit_board",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove="megacells:crafting/mega_crafting_unit",
        ),
    ]


AE_TIERS = ("1k", "4k", "16k", "64k", "256k")
MEGA_TIERS = ("1m", "4m", "16m", "64m", "256m")


def _ae_storage_recipes() -> list[dict[str, Any]]:
    recipes: list[dict[str, Any]] = []
    component_specs = [
        (
            "1k",
            DIGITAL,
            41,
            "tfmg:coated_circuit_board",
            [
                "ae2:certus_quartz_crystal",
                "ae2:printed_silicon",
                "ae2:logic_processor",
                "ae2:fluix_dust",
                "tfmg:capacitor_item",
                "tfmg:plastic_sheet",
            ],
            BRASS_DEPLOYER,
            BRASS_PRESS,
            "Populate the first 1k memory board with quartz memory, silicon addressing, logic, fluix timing, capacitance, and insulation",
        ),
        (
            "4k",
            MEKANIZED,
            40,
            "ae2:cell_component_1k",
            [
                "3x ae2:cell_component_1k",
                "ae2:calculation_processor",
                "tfmg:transistor_item",
                "tfmg:copper_wire",
                "tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            BRASS_DEPLOYER,
            BRASS_PRESS,
            "Bond four 1k planes behind a calculation controller, transistor switch, wired backplane, dielectric, and vibrant data face",
        ),
        (
            "16k",
            MEKANIZED,
            42,
            "ae2:cell_component_4k",
            [
                "3x ae2:cell_component_4k",
                "appliedcreate:stress_processor",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:capacitor_item",
                "tfmg:lithium_charge",
                "tfmg:magnetic_alloy_sheet",
            ],
            BRASS_DEPLOYER,
            BRASS_PRESS,
            "Stack four 4k planes with stress scheduling, paired semiconductor gates, lithium-backed buffering, and magnetic shielding",
        ),
        (
            "64k",
            HIGH_ENERGY,
            86,
            "ae2:cell_component_16k",
            [
                "3x ae2:cell_component_16k",
                "appliedcreate:advanced_stress_processor",
                "megacells:accumulation_processor",
                "tfmg:laminated_magnetic_alloy_block",
                "2x tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            RAILWAY_DEPLOYER,
            RAILWAY_PRESS,
            "Combine four 16k planes on the Train line with advanced stress scheduling, accumulation control, laminated shielding, and an insulated face",
        ),
        (
            "256k",
            HIGH_ENERGY,
            88,
            "ae2:cell_component_64k",
            [
                "3x ae2:cell_component_64k",
                "megacells:accumulation_processor",
                "ae2:spatial_cell_component_2",
                "ae2:matter_ball",
                "tfmg:lithium_block",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:quartz_vibrant_glass",
            ],
            RAILWAY_DEPLOYER,
            RAILWAY_PRESS,
            "Finish the 256k plane from four 64k matrices with spatial addressing, matter isolation, bulk lithium buffering, and laminated containment",
        ),
    ]
    for tier, phase, order, base, ingredients, deployer, press, comment in component_specs:
        node = (
            ME_NODE
            if phase == DIGITAL
            else MID_STORAGE_NODE
            if phase == MEKANIZED
            else STORAGE_NODE
        )
        recipes.append(
            _sequence(
                f"cell_component_{tier}",
                phase=phase,
                node=node,
                order=order,
                comment=comment,
                input_item=base,
                output=f"ae2:cell_component_{tier}",
                ingredients=ingredients,
                deployer=deployer,
                press=press,
                remove=f"ae2:network/cells/item_storage_components_cell_{tier}_part",
            )
        )

    recipes.append(
        _compacting(
            "fluid_cell_housing",
            phase=DIGITAL,
            node=ME_NODE,
            order=21,
            comment=(
                "Pressure-seal quartz glass, copper fluid fittings, rubber, "
                "plastic, and a monitoring board into a reusable fluid-cell shell"
            ),
            machine=COPPER_PRESS,
            inputs=[
                "2x ae2:quartz_glass",
                "create:fluid_pipe",
                "tfmg:rubber_sheet",
                "tfmg:plastic_sheet",
                "tfmg:circuit_board",
            ],
            output="ae2:fluid_cell_housing",
            remove="ae2:network/cells/fluid_cell_housing",
        )
    )

    for index, tier in enumerate(AE_TIERS):
        phase = DIGITAL if index == 0 else MEKANIZED if index < 3 else HIGH_ENERGY
        node = (
            ME_NODE
            if phase == DIGITAL
            else MID_STORAGE_NODE
            if phase == MEKANIZED
            else STORAGE_NODE
        )
        machine = BRASS_PRESS if index < 3 else RAILWAY_PRESS
        extra = (
            ["tfmg:rubber_sheet", "ae2:quartz_glass", "tfmg:copper_wire"]
            if index == 0
            else ["tfmg:plastic_sheet", "ae2:quartz_glass", "tfmg:capacitor_item"]
            if index == 1
            else ["tfmg:plastic_sheet", "ae2:quartz_vibrant_glass", "tfmg:capacitor_item"]
            if index == 2
            else ["2x tfmg:plastic_sheet", "tfmg:magnetic_alloy_sheet", "tfmg:capacitor_item"]
            if index == 3
            else ["2x tfmg:plastic_sheet", "tfmg:laminated_magnetic_alloy_block", "tfmg:lithium_charge", "ae2:quartz_vibrant_glass"]
        )
        for family, housing, stock_prefix, identity in (
            ("item", "ae2:item_cell_housing", "item_storage_cell", "item indexing"),
            ("fluid", "ae2:fluid_cell_housing", "fluid_storage_cell", "sealed fluid indexing"),
        ):
            cell_order = (
                90 + (index - 3) * 2 + (1 if family == "fluid" else 0)
                if phase == HIGH_ENERGY
                else 50 + index * 2 + (1 if family == "fluid" else 0)
            )
            recipes.append(
                _compacting(
                    f"{family}_storage_cell_{tier}",
                    phase=phase,
                    node=node,
                    order=cell_order,
                    comment=(
                        f"Pressure-seal the {tier} memory component inside its "
                        f"{family} housing with {identity}, dielectric, and a service face"
                    ),
                    machine=machine,
                    inputs=[housing, f"ae2:cell_component_{tier}", *extra],
                    output=f"ae2:{family}_storage_cell_{tier}",
                    remove=[
                        f"ae2:network/cells/{stock_prefix}_{tier}",
                        f"ae2:network/cells/{stock_prefix}_{tier}_storage",
                    ],
                )
            )
    return recipes


def _mega_storage_recipes() -> list[dict[str, Any]]:
    recipes: list[dict[str, Any]] = []
    component_specs = [
        (
            "1m",
            "ae2:cell_component_256k",
            [
                "3x ae2:cell_component_256k",
                "2x megacells:accumulation_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:quartz_vibrant_glass",
                "ae2:sky_dust",
                "2x tfmg:plastic_sheet",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:lithium_block",
            ],
            "Build the first MEGA plane from four 256k matrices with dual accumulation control, stress scheduling, sky-stone addressing, dielectric, shielding, and bulk lithium",
        ),
        (
            "4m",
            "megacells:cell_component_1m",
            [
                "3x megacells:cell_component_1m",
                "megacells:accumulation_processor",
                "extendedae:concurrent_processor",
                "ae2:spatial_cell_component_2",
                "tfmg:laminated_magnetic_alloy_block",
                "allthemodium:allthemodium_ingot",
            ],
            "Bond four 1M planes with concurrent accumulation, spatial addressing, laminated shielding, and the first Allthemodium bus",
        ),
        (
            "16m",
            "megacells:cell_component_4m",
            [
                "3x megacells:cell_component_4m",
                "extendedae:concurrent_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:spatial_cell_component_16",
                "modernfoundry:cobalt_reinforcement",
                "2x tfmg:plastic_sheet",
            ],
            "Stack four 4M planes with concurrent stress control, 16-cubed addressing, cobalt reinforcement, and a double dielectric",
        ),
        (
            "64m",
            "megacells:cell_component_16m",
            [
                "3x megacells:cell_component_16m",
                "2x megacells:accumulation_processor",
                "ae2:spatial_cell_component_128",
                "ae2:matter_ball",
                "tfmg:laminated_magnetic_alloy_block",
                "allthemodium:vibranium_ingot",
            ],
            "Address four 16M planes through dual accumulation control, full spatial mapping, matter isolation, laminated containment, and a Vibranium bus",
        ),
        (
            "256m",
            "megacells:cell_component_64m",
            [
                "3x megacells:cell_component_64m",
                "2x megacells:accumulation_processor",
                "ae2:spatial_cell_component_128",
                "2x ae2:matter_ball",
                "mekanism:ultimate_control_circuit",
                "allthemodium:vibranium_allthemodium_alloy_ingot",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            "Complete the 256M matrix from four 64M planes with redundant accumulation, full spatial maps, matter isolation, ultimate control, and an exotic-alloy bus",
        ),
    ]
    for index, (tier, base, ingredients, comment) in enumerate(component_specs):
        recipes.append(
            _sequence(
                f"mega_cell_component_{tier}",
                phase=HIGH_ENERGY,
                node=STORAGE_NODE,
                order=300 + index,
                comment=comment,
                input_item=base,
                output=f"megacells:cell_component_{tier}",
                ingredients=ingredients,
                deployer=RAILWAY_DEPLOYER,
                press=RAILWAY_PRESS,
                remove=f"megacells:cells/cell_component_{tier}",
            )
        )

    recipes.extend(
        [
            _compacting(
                "mega_item_cell_housing",
                phase=HIGH_ENERGY,
                node=STORAGE_NODE,
                order=310,
                comment=(
                    "Press a standard item-cell shell into a Train-rated MEGA "
                    "housing with casing, steel frame, vibrant face, magnetic "
                    "shield, and thick plastic insulation"
                ),
                machine=RAILWAY_PRESS,
                inputs=[
                    "ae2:item_cell_housing",
                    "create:railway_casing",
                    "tfmg:steel_frame",
                    "ae2:quartz_vibrant_glass",
                    "tfmg:magnetic_alloy_sheet",
                    "2x tfmg:plastic_sheet",
                ],
                output="megacells:mega_item_cell_housing",
                remove="megacells:cells/mega_item_cell_housing",
            ),
            _compacting(
                "mega_fluid_cell_housing",
                phase=HIGH_ENERGY,
                node=STORAGE_NODE,
                order=311,
                comment=(
                    "Press a fluid-cell shell into a Train-rated MEGA tank "
                    "housing with structural casing, fluid chamber, vibrant "
                    "service face, and a double plastic seal"
                ),
                machine=RAILWAY_PRESS,
                inputs=[
                    "ae2:fluid_cell_housing",
                    "create:railway_casing",
                    "tfmg:steel_frame",
                    "create:fluid_tank",
                    "ae2:quartz_vibrant_glass",
                    "2x tfmg:plastic_sheet",
                ],
                output="megacells:mega_fluid_cell_housing",
                remove="megacells:cells/mega_fluid_cell_housing",
            ),
        ]
    )

    for index, tier in enumerate(MEGA_TIERS):
        seals = (
            ["2x tfmg:plastic_sheet", "tfmg:capacitor_item", "ae2:quartz_vibrant_glass"]
            if index == 0
            else ["2x tfmg:plastic_sheet", "tfmg:magnetic_alloy_sheet", "ae2:quartz_vibrant_glass"]
            if index == 1
            else ["3x tfmg:plastic_sheet", "tfmg:laminated_magnetic_alloy_block", "tfmg:lithium_charge"]
            if index == 2
            else ["3x tfmg:plastic_sheet", "tfmg:laminated_magnetic_alloy_block", "ae2:matter_ball"]
            if index == 3
            else ["4x tfmg:plastic_sheet", "2x ae2:matter_ball", "allthemodium:vibranium_allthemodium_alloy_ingot"]
        )
        for family, housing in (
            ("item", "megacells:mega_item_cell_housing"),
            ("fluid", "megacells:mega_fluid_cell_housing"),
        ):
            recipes.append(
                _compacting(
                    f"mega_{family}_storage_cell_{tier}",
                    phase=HIGH_ENERGY,
                    node=STORAGE_NODE,
                    order=320 + index * 2 + (1 if family == "fluid" else 0),
                    comment=(
                        f"Pressure-seal the {tier} MEGA matrix inside its "
                        f"Train-rated {family} housing with tier-appropriate "
                        "dielectric, shielding, and service contacts"
                    ),
                    machine=RAILWAY_PRESS,
                    inputs=[housing, f"megacells:cell_component_{tier}", *seals],
                    output=f"megacells:{family}_storage_cell_{tier}",
                    remove=[
                        f"megacells:cells/standard/{family}_storage_cell_{tier}",
                        f"megacells:cells/standard/{family}_storage_cell_{tier}_with_housing",
                    ],
                )
            )
    return recipes


def _mega_compute_recipes() -> list[dict[str, Any]]:
    recipes = [
        _sequence(
            "mega_interface",
            phase=HIGH_ENERGY,
            node=CRAFTING_NODE,
            order=340,
            comment=(
                "Scale the ME Interface on the Train line with accumulation "
                "and concurrent routing, dense bandwidth, capacity control, "
                "an insulated backplane, and structural casing"
            ),
            input_item="ae2:interface",
            output="megacells:mega_interface",
            ingredients=[
                "megacells:accumulation_processor",
                "extendedae:concurrent_processor",
                "ae2:fluix_smart_dense_cable",
                "ae2:capacity_card",
                "tfmg:coated_circuit_board",
                "tfmg:plastic_sheet",
                "create:railway_casing",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove="megacells:network/mega_interface",
        ),
        _sequence(
            "mega_pattern_provider",
            phase=HIGH_ENERGY,
            node=CRAFTING_NODE,
            order=341,
            comment=(
                "Turn a Pattern Provider into a Train-scale dispatcher with "
                "accumulation memory, concurrent scheduling, engineering "
                "control, dense cable, crafting firmware, and an insulated frame"
            ),
            input_item="ae2:pattern_provider",
            output="megacells:mega_pattern_provider",
            ingredients=[
                "megacells:accumulation_processor",
                "extendedae:concurrent_processor",
                "ae2:engineering_processor",
                "ae2:fluix_smart_dense_cable",
                "ae2:crafting_card",
                "tfmg:plastic_sheet",
                "create:railway_casing",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove="megacells:network/mega_pattern_provider",
        ),
        _sequence(
            "mega_crafting_accelerator",
            phase=HIGH_ENERGY,
            node=CRAFTING_NODE,
            order=342,
            comment=(
                "Populate a MEGA Crafting Unit as a co-processor with "
                "concurrent, stress, and engineering control, paired motors, "
                "local capacitance, and magnetic clock shielding"
            ),
            input_item="megacells:mega_crafting_unit",
            output="megacells:mega_crafting_accelerator",
            ingredients=[
                "extendedae:concurrent_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:engineering_processor",
                "2x tfmg:electric_motor",
                "2x tfmg:capacitor_item",
                "tfmg:magnetic_alloy_sheet",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove="megacells:crafting/mega_crafting_accelerator",
        ),
        _sequence(
            "mega_crafting_monitor",
            phase=HIGH_ENERGY,
            node=CRAFTING_NODE,
            order=343,
            comment=(
                "Instrument a MEGA Crafting Unit with a storage monitor, "
                "concurrent display controller, display board, dense data lead, "
                "coated backplane, and plastic face"
            ),
            input_item="megacells:mega_crafting_unit",
            output="megacells:mega_crafting_monitor",
            ingredients=[
                "ae2:storage_monitor",
                "extendedae:concurrent_processor",
                "create:display_board",
                "ae2:fluix_smart_dense_cable",
                "tfmg:coated_circuit_board",
                "tfmg:plastic_sheet",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            remove="megacells:crafting/mega_crafting_monitor",
        ),
    ]

    extras = [
        ["megacells:accumulation_processor", "ae2:fluix_smart_dense_cable", "tfmg:capacitor_item", "tfmg:plastic_sheet", "ae2:quartz_vibrant_glass"],
        ["extendedae:concurrent_processor", "ae2:fluix_smart_dense_cable", "tfmg:magnetic_alloy_sheet", "tfmg:plastic_sheet", "ae2:quartz_vibrant_glass"],
        ["appliedcreate:advanced_stress_processor", "ae2:spatial_cell_component_2", "tfmg:transformer", "2x tfmg:plastic_sheet", "tfmg:capacitor_item"],
        ["extendedae:concurrent_processor", "ae2:spatial_cell_component_16", "ae2:matter_ball", "tfmg:laminated_magnetic_alloy_block", "allthemodium:allthemodium_ingot"],
        ["megacells:accumulation_processor", "ae2:spatial_cell_component_128", "2x ae2:matter_ball", "mekanism:ultimate_control_circuit", "allthemodium:vibranium_allthemodium_alloy_ingot"],
    ]
    for index, tier in enumerate(MEGA_TIERS):
        recipes.append(
            _sequence(
                f"mega_crafting_storage_{tier}",
                phase=HIGH_ENERGY,
                node=CRAFTING_NODE,
                order=350 + index,
                comment=(
                    f"Install the {tier} MEGA memory plane into the Train-built "
                    "crafting chassis with tier-specific scheduling, spatial "
                    "addressing, dielectric, shielding, and service control"
                ),
                input_item="megacells:mega_crafting_unit",
                output=f"megacells:{tier}_crafting_storage",
                ingredients=[f"megacells:cell_component_{tier}", *extras[index]],
                deployer=RAILWAY_DEPLOYER,
                press=RAILWAY_PRESS,
                remove=f"megacells:crafting/{tier}_crafting_storage",
            )
        )
    return recipes


def _advanced_ae_recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            "quantum_processor",
            phase=NUCLEAR,
            node=None,
            order=560,
            comment=(
                "Fabricate two quantum processors on the Refined Radiance line "
                "from the printed circuit, silicon, both semiconductor types, "
                "accumulation and stress control, high-voltage capacitance, "
                "cobalt heat spreading, and an Allthemodium contact"
            ),
            input_item="advanced_ae:printed_quantum_processor",
            output="2x advanced_ae:quantum_processor",
            ingredients=[
                "ae2:printed_silicon",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "megacells:accumulation_processor",
                "appliedcreate:advanced_stress_processor",
                "electroenergetics:high_voltage_capacitor",
                "modernfoundry:cobalt_reinforcement",
                "allthemodium:allthemodium_ingot",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove=[
                "advanced_ae:quantum_processor",
                "advanced_ae:quantum_processor_eae",
            ],
        ),
        _sequence(
            "quantum_storage_component",
            phase=NUCLEAR,
            node=None,
            order=561,
            comment=(
                "Rebuild the 256M matrix as a quantum storage core with quantum "
                "logic, full spatial addressing, alloy plates, a shattered "
                "singularity, Vibranium containment, and a plastic dielectric"
            ),
            input_item="megacells:cell_component_256m",
            output="advanced_ae:quantum_storage_component",
            ingredients=[
                "advanced_ae:quantum_processor",
                "ae2:spatial_cell_component_128",
                "2x advanced_ae:quantum_alloy_plate",
                "advanced_ae:shattered_singularity",
                "allthemodium:vibranium_ingot",
                "2x tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove="advanced_ae:quantum_storage_component",
        ),
        _sequence(
            "quantum_unit",
            phase=NUCLEAR,
            node=None,
            order=562,
            comment=(
                "Upgrade the Train-built MEGA chassis with quantum and "
                "concurrent processors, singularity clock, quantum-alloy shell, "
                "exotic bus, Radiant casing, and laminated containment"
            ),
            input_item="megacells:mega_crafting_unit",
            output="advanced_ae:quantum_unit",
            ingredients=[
                "2x advanced_ae:quantum_processor",
                "extendedae:concurrent_processor",
                "advanced_ae:shattered_singularity",
                "2x advanced_ae:quantum_alloy_plate",
                "allthemodium:vibranium_allthemodium_alloy_ingot",
                "create:refined_radiance_casing",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove=["advanced_ae:eaequantumunit", "advanced_ae:quantumunit"],
        ),
        _sequence(
            "quantum_accelerator",
            phase=NUCLEAR,
            node=None,
            order=563,
            comment=(
                "Turn the Quantum Unit into a parallel accelerator with dual "
                "quantum logic, concurrent and stress schedulers, accumulation "
                "memory, paired motors, high-voltage buffering, and cobalt cooling"
            ),
            input_item="advanced_ae:quantum_unit",
            output="advanced_ae:quantum_accelerator",
            ingredients=[
                "2x advanced_ae:quantum_processor",
                "extendedae:concurrent_processor",
                "appliedcreate:advanced_stress_processor",
                "megacells:accumulation_processor",
                "2x tfmg:electric_motor",
                "electroenergetics:high_voltage_capacitor",
                "modernfoundry:cobalt_reinforcement",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove=["advanced_ae:eaequantumaccel", "advanced_ae:quantumaccel"],
        ),
        _sequence(
            "quantum_core",
            phase=NUCLEAR,
            node=None,
            order=564,
            comment=(
                "Assemble the Quantum Core around the storage matrix, complete "
                "accelerator and compute unit, redundant quantum processors, "
                "singularity clock, matter isolation, and an Unobtainium-"
                "Vibranium containment bus"
            ),
            input_item="advanced_ae:quantum_storage_component",
            output="advanced_ae:quantum_core",
            ingredients=[
                "advanced_ae:quantum_accelerator",
                "advanced_ae:quantum_unit",
                "2x advanced_ae:quantum_processor",
                "advanced_ae:shattered_singularity",
                "2x ae2:matter_ball",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
                "create:refined_radiance_casing",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove="advanced_ae:quantumcore",
        ),
        _mechanical(
            "quantum_crafter",
            phase=NUCLEAR,
            node=None,
            order=565,
            comment=(
                "Build the full five-by-five quantum compute tower as a "
                "recognizable physical machine: structural glass shell, alloy "
                "bus, processor banks, core, accelerator, unit, assembler, "
                "provider, Radiant base, and exotic side conductors"
            ),
            pattern=[
                " VQV ",
                "QPCPQ",
                "GAMAG",
                "QPUQP",
                " RRR ",
            ],
            key={
                "V": "advanced_ae:quantum_structure",
                "Q": "advanced_ae:quantum_alloy_plate",
                "G": "allthemodium:vibranium_allthemodium_alloy_ingot",
                "P": "advanced_ae:quantum_processor",
                "C": "advanced_ae:quantum_core",
                "A": "advanced_ae:quantum_accelerator",
                "M": "extendedae:ex_molecular_assembler",
                "U": "advanced_ae:quantum_unit",
                "R": "create:refined_radiance_casing",
            },
            output="advanced_ae:quantum_crafter",
            remove="advanced_ae:quantumcrafter",
        ),
    ]


# These current v2 outputs were individually reviewed and intentionally left
# alone.  Their recipes already express a recognizable physical operation;
# retaining them avoids churn merely for the sake of recipe count.
INTENTIONALLY_PRESERVED = {
    "ae2:printed_silicon": "TFMG silicon is compacted against the reusable AE silicon press.",
    "ae2:printed_logic_processor": "The Brass press stamps the appropriate material against a reusable mold.",
    "ae2:printed_calculation_processor": "The Brass press stamps the appropriate material against a reusable mold.",
    "ae2:printed_engineering_processor": "The Brass press stamps the appropriate material against a reusable mold.",
    "ae2:logic_processor": "A populated TFMG board sequence; whole-processor Inscriber routes are removed.",
    "ae2:calculation_processor": "A populated TFMG board sequence; whole-processor Inscriber routes are removed.",
    "ae2:engineering_processor": "A populated TFMG board sequence; whole-processor Inscriber routes are removed.",
    "appliedcreate:stress_processor": "The sequence already populates a dedicated stress circuit board.",
    "appliedcreate:advanced_stress_processor": "The sequence already builds on the prior processor and Brass board.",
    "ae2:energy_acceptor": "Copper-line transformer, conductor, board, and fluix assembly is coherent.",
    "ae2:item_cell_housing": "Compacting is justified as pressure-laminating a rigid reusable shell.",
    "ae2:import_bus": "Copper actuator sequence has a clear extraction function.",
    "ae2:export_bus": "Copper actuator sequence has a clear insertion function.",
    "ae2:interface": "Bidirectional matter cores are installed into a quartz service enclosure.",
    "ae2:molecular_assembler": "A crafting table becomes a machine through a recognizable precision sequence.",
    "ae2:pattern_provider": "Provider firmware and precision motion are installed into an Interface.",
    "ae2:me_p2p_tunnel": "The sequence turns quartz fiber into a routed engineering endpoint.",
    "ae2:annihilation_core": "A batch electronics sequence yields paired extraction cores.",
    "ae2:formation_core": "A batch electronics sequence yields paired placement cores.",
    "ae2:energy_cell": "Copper-line lithium and magnetic battery construction is coherent.",
    "ae2:dense_energy_cell": "The denser lithium bank builds directly from the prior energy cell.",
    "ae2:crafting_accelerator": "Compute, stress, motion, capacitance, and shielding all match its function.",
    "ae2:crafting_monitor": "Display and calculation hardware are installed into a Crafting Unit.",
    "ae2:wireless_access_point": "A receiver becomes an amplified station through coil and cable hardware.",
    "megacells:mega_energy_cell": "A dense cell becomes a transformer-coupled bulk lithium bank.",
    "advanced_ae:reaction_chamber": "The existing full 5x5 machine silhouette is one of the approved reference recipes.",
    "ae2:quantum_entangled_singularity": "The late Refined Radiance sequence closes a real dependency dead end.",
}

# The existing v2 crafting-storage and stress-storage recipes are already the
# exact process split requested by the user: components are populated in
# sequences, then finished cells are compacted into rigid housings.  Record the
# audit decision explicitly instead of rewriting their BOMs for novelty.
for _tier in AE_TIERS:
    INTENTIONALLY_PRESERVED[f"ae2:{_tier}_crafting_storage"] = (
        "A tier-specific memory component is installed into the prior Crafting Unit through a manufactured sequence."
    )
for _tier in (*AE_TIERS, *MEGA_TIERS):
    INTENTIONALLY_PRESERVED[f"appliedcreate:stress_storage_component_{_tier}"] = (
        "The stress-memory ladder is a tiered populated-board sequence with distinct control and shielding materials."
    )
    INTENTIONALLY_PRESERVED[f"appliedcreate:stress_storage_cell_{_tier}"] = (
        "Compacting is justified here as pressure-sealing the finished stress component into its rigid housing."
    )


# Stock recipes outside the managed-output set were also reviewed by family.
# These categories remain stock because they are reversible utility/form
# conversions or already inherit the newly managed expensive components.
STOCK_FAMILIES_PRESERVED = {
    "AE2 coloured/covered cable conversions": (
        "Dyeing, cleaning, covering, and recolouring do not create bandwidth or bypass the managed Fluix cable ladder."
    ),
    "AE2 storage-cell disassembly": (
        "Disassembly only returns the already-manufactured component and housing; it is a recovery path, not a producer bypass."
    ),
    "AE2 portable cell conversions": (
        "Portable variants consume finished managed cells and energy hardware, so they inherit the full storage cost."
    ),
    "AE2 cards, facades, and part/block forms": (
        "Utility cards and reversible placement-form conversions do not replace processors, cables, or memory production."
    ),
    "MEGA chemical/experience/mana/source/soul cells": (
        "Addon-specific cells consume the newly managed MEGA components and housings; their identity conversion remains stock."
    ),
    "Applied Create pattern providers and P2P parts": (
        "Their stock recipes already consume managed AE2/Applied Create electronics and do not skip a manufacturing tier."
    ),
    "Advanced AE cards, buses, and wearable upgrades": (
        "These downstream utilities inherit quantum processors or managed AE hardware; the pass reserves Radiance fabrication for the quantum computer itself."
    ),
    "Decorative AE2/MEGA/Advanced AE blocks": (
        "Pure material-form and decorative conversions are intentionally outside factory progression."
    ),
}


def replacements() -> list[dict[str, Any]]:
    """Return a fresh, deterministic list of v3 AE-family definitions."""

    result = [
        *_cable_recipes(),
        *_electronics_and_machine_recipes(),
        *_ae_storage_recipes(),
        *_mega_storage_recipes(),
        *_mega_compute_recipes(),
        *_advanced_ae_recipes(),
        _compacting(
            "andesite_stress_cell_housing",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=332,
            comment=(
                "Pressure-laminate the AE item-cell shell with Andesite frame "
                "plates, quartz windows, rubber seal, and cinder packing"
            ),
            machine=BRASS_PRESS,
            inputs=[
                "ae2:item_cell_housing",
                "4x create:andesite_alloy",
                "2x ae2:quartz_glass",
                "tfmg:rubber_sheet",
                "create:cinder_flour",
            ],
            output="appliedcreate:andesite_stress_cell_housing",
            remove="appliedcreate:andesite_stress_cell_housing",
        ),
        _compacting(
            "brass_stress_cell_housing",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=333,
            comment=(
                "Pressure-refit the Andesite stress shell with Brass plates, "
                "vibrant windows, magnetic shielding, and a plastic dielectric"
            ),
            machine=RAILWAY_PRESS,
            inputs=[
                "appliedcreate:andesite_stress_cell_housing",
                "4x create:brass_sheet",
                "2x ae2:quartz_vibrant_glass",
                "2x tfmg:magnetic_alloy_sheet",
                "tfmg:plastic_sheet",
            ],
            output="appliedcreate:brass_stress_cell_housing",
            remove="appliedcreate:brass_stress_cell_housing",
        ),
    ]
    outputs = [_item_id(recipe["output"]) for recipe in result]
    if len(outputs) != len(set(outputs)):
        duplicates = sorted({item for item in outputs if outputs.count(item) > 1})
        raise ValueError(f"duplicate v3 AE-family outputs: {duplicates}")
    return result


COUNT_PREFIX = re.compile(r"^\s*\d+(?:\.\d+)?x\s+")


def _item_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = COUNT_PREFIX.sub("", value.strip())
    if not value or value.startswith("#") or ":" not in value:
        return None
    return value


def _merge_unique(*values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for group in values:
        for value in group:
            if value not in seen:
                seen.add(value)
                result.append(value)
    return result


def apply(data: dict[str, Any]) -> None:
    """Replace claimed outputs without touching unrelated recipe definitions."""

    additions = replacements()
    claimed = {_item_id(recipe["output"]) for recipe in additions}
    recipe_ids = {recipe["id"] for recipe in additions}
    new_id_by_output = {
        _item_id(recipe["output"]): recipe["id"] for recipe in additions
    }
    old_removals: dict[str, list[str]] = {item: [] for item in claimed if item}
    dependency_redirects: dict[str, str] = {}

    survivors: list[dict[str, Any]] = []
    for recipe in data.get("recipes", []):
        output = _item_id(recipe.get("output"))
        if output in claimed or recipe.get("id") in recipe_ids:
            old_id = recipe.get("id")
            new_id = new_id_by_output.get(output)
            if isinstance(old_id, str) and isinstance(new_id, str):
                dependency_redirects[old_id] = new_id
            if output in old_removals:
                old_removals[output] = _merge_unique(
                    old_removals[output], _as_list(recipe.get("remove"))
                )
            continue
        survivors.append(recipe)

    for recipe in additions:
        output = _item_id(recipe["output"])
        recipe["remove"] = _merge_unique(
            _as_list(recipe.get("remove")), old_removals.get(output, [])
        )
    data["recipes"] = [*survivors, *additions]

    # Recipes outside this module may explicitly depend on v2 IDs for outputs
    # now owned here.  Redirect those links by output identity so the module
    # remains composable instead of leaving dangling dependency metadata.
    for recipe in data["recipes"]:
        dependencies = _as_list(recipe.get("depends_on"))
        if dependencies:
            recipe["depends_on"] = _merge_unique(
                [dependency_redirects.get(entry, entry) for entry in dependencies]
            )

    # Several stock cable/cell routes were intentionally preserved in v2.
    # This pass now owns them, so remove only the exact preservation conflicts
    # and only the claimed output exclusions; unrelated policy remains intact.
    removal_ids = {
        entry for recipe in additions for entry in recipe.get("remove", [])
    }
    data["preserve_recipe_ids"] = [
        entry
        for entry in data.get("preserve_recipe_ids", [])
        if entry not in removal_ids
    ]
    data["exclude_outputs"] = [
        entry for entry in data.get("exclude_outputs", []) if entry not in claimed
    ]

    final_outputs = [
        _item_id(recipe.get("output")) for recipe in data.get("recipes", [])
    ]
    for output in claimed:
        if output and final_outputs.count(output) != 1:
            raise ValueError(
                f"v3 AE-family output {output} appears "
                f"{final_outputs.count(output)} times after replacement"
            )


def _recipe_resources(recipe: dict[str, Any]) -> set[str]:
    values: list[Any] = [
        recipe.get("input"),
        recipe.get("transitional"),
        recipe.get("output"),
        recipe.get("machine"),
    ]
    values.extend(recipe.get("inputs", []))
    values.extend(recipe.get("key", {}).values())
    for step in recipe.get("steps", []):
        values.extend([step.get("ingredient"), step.get("machine")])
    return {item for value in values if (item := _item_id(value)) is not None}


def validate_catalog(catalog_sqlite: str | Path) -> dict[str, Any]:
    """Validate every concrete item and stock-removal ID against the catalog."""

    database = Path(catalog_sqlite)
    if not database.is_file():
        raise FileNotFoundError(database)
    recipes = replacements()
    resources = sorted(set().union(*(_recipe_resources(r) for r in recipes)))
    removals = sorted({entry for r in recipes for entry in r.get("remove", [])})
    with sqlite3.connect(database) as connection:
        known_items = {
            row[0]
            for row in connection.execute(
                f"SELECT item_id FROM items WHERE item_id IN ({','.join('?' for _ in resources)})",
                resources,
            )
        }
        # The generated ``items`` table intentionally omits some vanilla
        # registries.  Concrete vanilla ingredients are nevertheless proven
        # by their recipe-reference rows, so include that evidence rather than
        # weakening validation with a blanket minecraft-namespace exemption.
        known_items.update(
            row[0]
            for row in connection.execute(
                f"SELECT DISTINCT resource_id FROM recipe_refs WHERE resource_id IN ({','.join('?' for _ in resources)})",
                resources,
            )
        )
        known_recipes = {
            row[0]
            for row in connection.execute(
                f"SELECT recipe_id FROM recipes WHERE recipe_id IN ({','.join('?' for _ in removals)})",
                removals,
            )
        }
    missing_items = sorted(set(resources) - known_items)
    # Some addon serializers expose valid alternate recipe IDs only at runtime;
    # report them without weakening the concrete-item assertion.
    missing_removals = sorted(set(removals) - known_recipes)
    if missing_items:
        raise ValueError(f"v3 AE-family recipes reference missing items: {missing_items}")
    return {
        "replacement_count": len(recipes),
        "resource_count": len(resources),
        "missing_items": missing_items,
        "missing_removal_ids": missing_removals,
        "preserved_count": len(INTENTIONALLY_PRESERVED),
        "preserved_stock_family_count": len(STOCK_FAMILIES_PRESERVED),
    }


__all__ = [
    "INTENTIONALLY_PRESERVED",
    "STOCK_FAMILIES_PRESERVED",
    "apply",
    "replacements",
    "validate_catalog",
]
