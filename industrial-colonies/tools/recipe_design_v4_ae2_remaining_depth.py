#!/usr/bin/env python3
"""Redesign the final active AE2/ExtendedAE digital-depth rejection cohort.

The twenty-one cards in this module are tied to exact immutable second-pass
review contracts.  The common complaint was insufficient manufacturing depth,
with three precise exceptions: the 4k component needed more electronics, the
ME Drive must not start from a wooden barrel, and the Spatial Anchor must regain
its meaningful 5x5 assembly.  Each ladder compounds prior hardware and moves
from Brass electronics through Railway infrastructure to Radiance quantum work.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"

TOO_CHEAP_NOTE = "Too cheap — make it more complex."

REJECTION_CONTRACTS: dict[str, dict[str, str]] = {
    "industrial_colonies:ae2_coverage/crafting_accelerator": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:928b6552820d3c44a40f7cd740a287c17ad4eebe9e2b7fb51f94aa7d1b0dee2c",
    },
    "industrial_colonies:digital_storage/ae2_crafting_storage_4k": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:90ca197115fd7806fbaabfc19fcce137e7177cb3f62ad9e66e60dcfd416a5a48",
    },
    "industrial_colonies:digital_storage/ae2_crafting_storage_16k": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:b04394ea759e7f7ac59e4690e1dd893094cb65aa60b12b0b0202972fc930814c",
    },
    "industrial_colonies:digital_storage/ae2_crafting_storage_64k": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:2edad134019ba2cb44b6d6e0af97682ef96a1fd0ced9196c1172077aa58d1e70",
    },
    "industrial_colonies:extendedae_coverage/ex_drive": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:820d6005097f326897adb2f9ab0b512c77aafa4b5f08ff588b4fbbc5d615e568",
    },
    "industrial_colonies:extendedae_coverage/ex_molecular_assembler": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:32af7e0fb842d41add75911b88b5ece12b0647509ab7e8c26c3c3b2d1f904704",
    },
    "industrial_colonies:extendedae_coverage/ingredient_buffer": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:393a6f1b4148c570c4b8af50f478c02b49473b6e05c2651afbd80c5697ae5a0b",
    },
    "industrial_colonies:extendedae_coverage/wireless_hub": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:a227a7284da6389276b26a64e32ccb7d9697f90678f7e2d63bfc132272382c6a",
    },
    "industrial_colonies:v3_ae2/cell_component_4k": {
        "note": "cost and jmore electronics",
        "cardSha256": "sha256:79ac3b0363ec9f4c4b9570950bfe60b934a492150ee6be0ea9d291f533b58821",
    },
    "industrial_colonies:v3_ae2/cell_component_16k": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:b079ec24374a6e812cf8a1bd16d705e54bf3aeb85c0855222fc08e2595be391b",
    },
    "industrial_colonies:v3_ae2/drive": {
        "note": "Thats good but not sure about the wooden barrels",
        "cardSha256": "sha256:473334f8d9fab18b378a6381824f0e778e9ad2a2863ad9fd07e70e38c399972d",
    },
    "industrial_colonies:v3_ae2/fluid_storage_cell_64k": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:6406eadd3810276068d089a1fde1eddf9529d975c3d94ef98fdb0039c89a5176",
    },
    "industrial_colonies:v3_ae2/fluid_storage_cell_256k": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:5432405c8b55f384f472e5033c7c76d7e7c3f7bb2c15c5774cd2858f9f967ac4",
    },
    "industrial_colonies:v3_ae2/item_storage_cell_256k": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:cd0374523ec2eb7edfe5228d8032b813ac9e357ffba83b7fa2d7c76f5891047e",
    },
    "industrial_colonies:v3_ae2/mega_crafting_monitor": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:6c16d6deffbeddcf6991c7aafec0ae31dc3cdce03a355afa287a429769fca0bb",
    },
    "industrial_colonies:v3_ae2/mega_fluid_cell_housing": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:92db490cb20a101df24c6a7004b052bf152fac5f05fb53b6f9349fb26f102a43",
    },
    "industrial_colonies:v3_ae2/mega_pattern_provider": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:f4766b92c6a41f1918e63f288002265616fa0dbf9ee0f994e45b64950eb17faf",
    },
    "industrial_colonies:v3_ae2/quantum_accelerator": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:e895bd28d9ab33c5a987bfc8ca87cca4075e069fa76f6299b1476cd801df8e86",
    },
    "industrial_colonies:v3_ae2/quantum_core": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:347a469cd4787602e8fe23455ccf33e11d24c61701d4a36938193674809b09dc",
    },
    "industrial_colonies:v3_ae2/spatial_anchor": {
        "note": "Had an original recipe with a 5x5 grid. Where did that go?",
        "cardSha256": "sha256:61e7c91fae9e8befd7bc34bbac162173eeb47a39e5b8ca32b226592fce50b496",
    },
    "industrial_colonies:v3_ae2/spatial_pylon_batch": {
        "note": TOO_CHEAP_NOTE,
        "cardSha256": "sha256:f7460e96389721cce5114ea92f926e82720f62688e290677016df7bd78e1f6ac",
    },
}

REDESIGNED_IDS = frozenset(REJECTION_CONTRACTS)

BRASS_IDS = frozenset(
    {
        "industrial_colonies:ae2_coverage/crafting_accelerator",
        "industrial_colonies:digital_storage/ae2_crafting_storage_4k",
        "industrial_colonies:digital_storage/ae2_crafting_storage_16k",
        "industrial_colonies:v3_ae2/cell_component_4k",
        "industrial_colonies:v3_ae2/cell_component_16k",
        "industrial_colonies:v3_ae2/drive",
    }
)
RAILWAY_IDS = frozenset(
    {
        "industrial_colonies:digital_storage/ae2_crafting_storage_64k",
        "industrial_colonies:extendedae_coverage/ex_drive",
        "industrial_colonies:extendedae_coverage/ex_molecular_assembler",
        "industrial_colonies:extendedae_coverage/ingredient_buffer",
        "industrial_colonies:extendedae_coverage/wireless_hub",
        "industrial_colonies:v3_ae2/fluid_storage_cell_64k",
        "industrial_colonies:v3_ae2/fluid_storage_cell_256k",
        "industrial_colonies:v3_ae2/item_storage_cell_256k",
        "industrial_colonies:v3_ae2/mega_crafting_monitor",
        "industrial_colonies:v3_ae2/mega_fluid_cell_housing",
        "industrial_colonies:v3_ae2/mega_pattern_provider",
        "industrial_colonies:v3_ae2/spatial_pylon_batch",
    }
)
RADIANCE_IDS = frozenset(
    {
        "industrial_colonies:v3_ae2/quantum_accelerator",
        "industrial_colonies:v3_ae2/quantum_core",
    }
)
SPATIAL_ANCHOR_ID = "industrial_colonies:v3_ae2/spatial_anchor"

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
        raise KeyError(f"expected active AE2 rejection is missing: {recipe_id}")
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
    family: str,
) -> Recipe:
    machines = {
        "brass": (BRASS_DEPLOYER, BRASS_PRESS),
        "railway": (RAILWAY_DEPLOYER, RAILWAY_PRESS),
        "radiance": (RADIANCE_DEPLOYER, RADIANCE_PRESS),
    }
    deployer, press = machines[family]
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "steps": [*(_deploy(item, deployer) for item in ingredients), _press(press)],
        "loops": 1,
        "output": output,
        "exclusive_output": True,
    }


def _designs() -> dict[str, Recipe]:
    return {
        "industrial_colonies:ae2_coverage/crafting_accelerator": _sequence(
            comment=(
                "Turn the Crafting Unit into a parallel compute lane with calculation "
                "and stress scheduling, paired TFMG motors and capacitors, a coated "
                "controller, magnetic timing shield, smart bus, and insulated mechanism"
            ),
            input_item="ae2:crafting_unit",
            ingredients=[
                "ae2:calculation_processor",
                "appliedcreate:advanced_stress_processor",
                "2x tfmg:electric_motor",
                "2x tfmg:capacitor_item",
                "tfmg:coated_circuit_board",
                "tfmg:magnetic_alloy_sheet",
                "ae2:fluix_smart_cable",
                "create:precision_mechanism",
                "tfmg:plastic_sheet",
            ],
            output="ae2:crafting_accelerator",
            family="brass",
        ),
        "industrial_colonies:digital_storage/ae2_crafting_storage_4k": _sequence(
            comment=(
                "Populate a Crafting Unit with a 4k plane, calculation and stress "
                "control, a coated TFMG backplane, smart bus, semiconductor driver, "
                "local buffer, dielectric liner, and visible service face"
            ),
            input_item="ae2:crafting_unit",
            ingredients=[
                "ae2:cell_component_4k",
                "ae2:calculation_processor",
                "appliedcreate:stress_processor",
                "tfmg:coated_circuit_board",
                "ae2:fluix_smart_cable",
                "tfmg:n_semiconductor",
                "tfmg:capacitor_item",
                "tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            output="ae2:4k_crafting_storage",
            family="brass",
        ),
        "industrial_colonies:digital_storage/ae2_crafting_storage_16k": _sequence(
            comment=(
                "Upgrade the 4k scheduler in place with a 16k plane, calculation and "
                "advanced stress control, complementary TFMG drivers, dense fluix bus, "
                "buffer bank, magnetic shield, and dielectric package"
            ),
            input_item="ae2:4k_crafting_storage",
            ingredients=[
                "ae2:cell_component_16k",
                "ae2:calculation_processor",
                "appliedcreate:advanced_stress_processor",
                "tfmg:coated_circuit_board",
                "ae2:fluix_smart_dense_cable",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:capacitor_item",
                "tfmg:magnetic_alloy_sheet",
                "2x tfmg:plastic_sheet",
            ],
            output="ae2:16k_crafting_storage",
            family="brass",
        ),
        "industrial_colonies:digital_storage/ae2_crafting_storage_64k": _sequence(
            comment=(
                "Rebuild the 16k scheduler for a 64k plane with concurrent and "
                "engineering control, stress timing, a dense backplane, TFMG isolated "
                "power, laminated shielding, lithium buffering, and a service face"
            ),
            input_item="ae2:16k_crafting_storage",
            ingredients=[
                "ae2:cell_component_64k",
                "extendedae:concurrent_processor",
                "ae2:engineering_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:transformer",
                "tfmg:laminated_magnetic_alloy_block",
                "2x tfmg:lithium_charge",
                "2x tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            output="ae2:64k_crafting_storage",
            family="railway",
        ),
        "industrial_colonies:extendedae_coverage/ex_drive": _sequence(
            comment=(
                "Expand the standard Drive into a Train-scale cell rack with concurrent "
                "addressing, doubled capacity and speed firmware, four fresh trays, a "
                "dense bus, TFMG controller and transformer, steel spine, and enclosure"
            ),
            input_item="ae2:drive",
            ingredients=[
                "extendedae:concurrent_processor",
                "2x ae2:capacity_card",
                "2x ae2:speed_card",
                "4x ae2:item_cell_housing",
                "ae2:fluix_smart_dense_cable",
                "tfmg:coated_circuit_board",
                "tfmg:transformer",
                "tfmg:steel_frame",
                "create:railway_casing",
                "2x tfmg:plastic_sheet",
            ],
            output="extendedae:ex_drive",
            family="railway",
        ),
        "industrial_colonies:extendedae_coverage/ex_molecular_assembler": _sequence(
            comment=(
                "Refit the assembler as a high-throughput production cell with "
                "concurrent, engineering, and stress scheduling, paired TFMG drives "
                "and buffers, speed/crafting firmware, precision motion, and isolation"
            ),
            input_item="ae2:molecular_assembler",
            ingredients=[
                "extendedae:concurrent_processor",
                "ae2:engineering_processor",
                "appliedcreate:advanced_stress_processor",
                "2x tfmg:electric_motor",
                "2x tfmg:capacitor_item",
                "ae2:speed_card",
                "ae2:crafting_card",
                "create:precision_mechanism",
                "tfmg:transformer",
                "create:railway_casing",
            ],
            output="extendedae:ex_molecular_assembler",
            family="railway",
        ),
        "industrial_colonies:extendedae_coverage/ingredient_buffer": _sequence(
            comment=(
                "Equip the ExtendedAE frame as a buffered ingredient reservoir with a "
                "16k cell bay, bidirectional matter cores, capacity firmware, dense bus, "
                "and a serviceable TFMG controller, dielectric, and buffer supply"
            ),
            input_item="extendedae:machine_frame",
            ingredients=[
                "ae2:item_cell_housing",
                "ae2:cell_component_16k",
                "ae2:annihilation_core",
                "ae2:formation_core",
                "ae2:capacity_card",
                "ae2:fluix_smart_dense_cable",
                "tfmg:coated_circuit_board",
                "2x tfmg:plastic_sheet",
                "2x tfmg:capacitor_item",
                "create:railway_casing",
            ],
            output="extendedae:ingredient_buffer",
            family="railway",
        ),
        "industrial_colonies:extendedae_coverage/wireless_hub": _sequence(
            comment=(
                "Commission the wireless connector as a powered network hub with an "
                "access point, dense energy reserve, concurrent routing, a large TFMG "
                "antenna coil, isolated transformer, buffer bank, and dense data trunk"
            ),
            input_item="extendedae:wireless_connect",
            ingredients=[
                "ae2:wireless_access_point",
                "ae2:dense_energy_cell",
                "extendedae:concurrent_processor",
                "tfmg:large_coil",
                "tfmg:transformer",
                "2x tfmg:capacitor_item",
                "ae2:calculation_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:steel_frame",
                "create:railway_casing",
            ],
            output="extendedae:wireless_hub",
            family="railway",
        ),
        "industrial_colonies:v3_ae2/cell_component_4k": _sequence(
            comment=(
                "Bond four 1k dies behind calculation logic and a coated TFMG board, "
                "then add complementary semiconductor address drivers, paired buffers, "
                "a copper bus, dielectric laminate, and visible data face"
            ),
            input_item="ae2:cell_component_1k",
            ingredients=[
                "3x ae2:cell_component_1k",
                "ae2:calculation_processor",
                "tfmg:coated_circuit_board",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:capacitor_item",
                "2x tfmg:copper_wire",
                "2x tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            output="ae2:cell_component_4k",
            family="brass",
        ),
        "industrial_colonies:v3_ae2/cell_component_16k": _sequence(
            comment=(
                "Bond four 4k planes through calculation and advanced stress control, "
                "a coated backplane, complementary TFMG gates, paired capacitors, lithium "
                "buffering, magnetic shielding, and a doubled dielectric package"
            ),
            input_item="ae2:cell_component_4k",
            ingredients=[
                "3x ae2:cell_component_4k",
                "ae2:calculation_processor",
                "appliedcreate:advanced_stress_processor",
                "tfmg:coated_circuit_board",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:capacitor_item",
                "tfmg:lithium_charge",
                "tfmg:magnetic_alloy_sheet",
                "2x tfmg:plastic_sheet",
            ],
            output="ae2:cell_component_16k",
            family="brass",
        ),
        "industrial_colonies:v3_ae2/drive": _sequence(
            comment=(
                "Build the ME Drive on a welded TFMG steel frame rather than a timber "
                "cabinet, then install its Brass enclosure, four literal cell trays, smart "
                "bus, logic controller, coated board, copper traces, and insulated face"
            ),
            input_item="tfmg:steel_frame",
            ingredients=[
                "create:brass_casing",
                "4x ae2:item_cell_housing",
                "ae2:fluix_smart_cable",
                "ae2:logic_processor",
                "tfmg:coated_circuit_board",
                "2x tfmg:copper_wire",
                "2x tfmg:plastic_sheet",
                "tfmg:capacitor_item",
                "ae2:quartz_vibrant_glass",
            ],
            output="ae2:drive",
            family="brass",
        ),
        "industrial_colonies:v3_ae2/fluid_storage_cell_64k": _sequence(
            comment=(
                "Upgrade the 16k fluid cell in place with a 64k plane, engineering "
                "control, metered plastic plumbing, doubled seals and lithium reserve, "
                "magnetic containment, dense service bus, and vibrant inspection face"
            ),
            input_item="ae2:fluid_storage_cell_16k",
            ingredients=[
                "ae2:cell_component_64k",
                "ae2:engineering_processor",
                "tfmg:plastic_pipe",
                "tfmg:plastic_fluid_valve",
                "2x tfmg:rubber_sheet",
                "2x tfmg:lithium_charge",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:fluix_smart_dense_cable",
                "ae2:quartz_vibrant_glass",
            ],
            output="ae2:fluid_storage_cell_64k",
            family="railway",
        ),
        "industrial_colonies:v3_ae2/fluid_storage_cell_256k": _sequence(
            comment=(
                "Rebuild the 64k fluid cell around a 256k plane with engineering control, "
                "steel manifold and valve, redundant seals, lithium buffering, laminated "
                "containment, transformer isolation, dense service, and a visible face"
            ),
            input_item="ae2:fluid_storage_cell_64k",
            ingredients=[
                "ae2:cell_component_256k",
                "ae2:engineering_processor",
                "tfmg:steel_pipe",
                "tfmg:steel_fluid_valve",
                "2x tfmg:rubber_sheet",
                "3x tfmg:lithium_charge",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:transformer",
                "ae2:fluix_smart_dense_cable",
                "ae2:quartz_vibrant_glass",
            ],
            output="ae2:fluid_storage_cell_256k",
            family="railway",
        ),
        "industrial_colonies:v3_ae2/item_storage_cell_256k": _sequence(
            comment=(
                "Upgrade the 64k item cell in place with its 256k plane, engineering "
                "indexing, dense data service, a coated TFMG address board, dielectric "
                "liner, lithium reserve, magnetic shield, capacity firmware, and face"
            ),
            input_item="ae2:item_storage_cell_64k",
            ingredients=[
                "ae2:cell_component_256k",
                "ae2:engineering_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:coated_circuit_board",
                "2x tfmg:plastic_sheet",
                "2x tfmg:lithium_charge",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:capacity_card",
                "ae2:quartz_vibrant_glass",
            ],
            output="ae2:item_storage_cell_256k",
            family="railway",
        ),
        "industrial_colonies:v3_ae2/mega_crafting_monitor": _sequence(
            comment=(
                "Instrument the MEGA Crafting Unit with a storage display, concurrent "
                "controller, paired display boards, dense data trunk, coated TFMG board, "
                "calculation logic, isolated power, dielectric face, and Train enclosure"
            ),
            input_item="megacells:mega_crafting_unit",
            ingredients=[
                "ae2:storage_monitor",
                "extendedae:concurrent_processor",
                "2x create:display_board",
                "ae2:fluix_smart_dense_cable",
                "tfmg:coated_circuit_board",
                "ae2:calculation_processor",
                "tfmg:transformer",
                "2x tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
                "create:railway_casing",
            ],
            output="megacells:mega_crafting_monitor",
            family="railway",
        ),
        "industrial_colonies:v3_ae2/mega_fluid_cell_housing": _sequence(
            comment=(
                "Convert the standard fluid shell into a Train-rated MEGA vessel with "
                "Railway casing and TFMG steel spine, a real tank chamber and manifold, "
                "metering valve, seals, isolated power, dielectric, and service face"
            ),
            input_item="ae2:fluid_cell_housing",
            ingredients=[
                "create:railway_casing",
                "tfmg:steel_frame",
                "create:fluid_tank",
                "tfmg:steel_pipe",
                "tfmg:steel_fluid_valve",
                "2x tfmg:rubber_sheet",
                "tfmg:transformer",
                "2x tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
                "ae2:fluix_smart_dense_cable",
            ],
            output="megacells:mega_fluid_cell_housing",
            family="railway",
        ),
        "industrial_colonies:v3_ae2/mega_pattern_provider": _sequence(
            comment=(
                "Expand the Pattern Provider into a Train-scale dispatcher with "
                "accumulation, concurrent, engineering and stress scheduling, dense "
                "service, crafting firmware, TFMG isolation, dielectric, and enclosure"
            ),
            input_item="ae2:pattern_provider",
            ingredients=[
                "megacells:accumulation_processor",
                "extendedae:concurrent_processor",
                "ae2:engineering_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:fluix_smart_dense_cable",
                "ae2:crafting_card",
                "tfmg:transformer",
                "2x tfmg:plastic_sheet",
                "create:railway_casing",
                "ae2:quartz_vibrant_glass",
            ],
            output="megacells:mega_pattern_provider",
            family="railway",
        ),
        "industrial_colonies:v3_ae2/quantum_accelerator": _sequence(
            comment=(
                "Turn the Quantum Unit into a parallel accelerator with dual quantum "
                "logic, concurrent/stress/accumulation scheduling, paired TFMG drives, "
                "high-voltage distribution, cobalt cooling, and a Vibranium field bus"
            ),
            input_item="advanced_ae:quantum_unit",
            ingredients=[
                "2x advanced_ae:quantum_processor",
                "extendedae:concurrent_processor",
                "appliedcreate:advanced_stress_processor",
                "megacells:accumulation_processor",
                "2x tfmg:electric_motor",
                "electroenergetics:high_voltage_capacitor",
                "tfmg:transformer",
                "tfmg:heavy_cable_hub",
                "modernfoundry:cobalt_reinforcement",
                "allthemodium:vibranium_plate",
                "create:refined_radiance_casing",
            ],
            output="advanced_ae:quantum_accelerator",
            family="radiance",
        ),
        "industrial_colonies:v3_ae2/quantum_core": _sequence(
            comment=(
                "Finish the Quantum Core around its storage matrix with a complete "
                "accelerator and compute unit, redundant quantum logic, singularity "
                "clock, matter isolation, ultimate control, TFMG shielding, and field bus"
            ),
            input_item="advanced_ae:quantum_storage_component",
            ingredients=[
                "advanced_ae:quantum_accelerator",
                "advanced_ae:quantum_unit",
                "2x advanced_ae:quantum_processor",
                "advanced_ae:shattered_singularity",
                "2x ae2:matter_ball",
                "mekanism:ultimate_control_circuit",
                "tfmg:transformer",
                "tfmg:laminated_magnetic_alloy_block",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
                "create:refined_radiance_casing",
            ],
            output="advanced_ae:quantum_core",
            family="radiance",
        ),
        SPATIAL_ANCHOR_ID: {
            "type": "mechanical_crafting",
            "comment": (
                "Recreate the Spatial Anchor as a full 5x5 field device: four pylons "
                "and a welded steel enclosure surround the 128-cubed core, twin IO "
                "gateways, Chunk Controller, redundant logic, transformer, and field bus"
            ),
            "pattern": [
                "PFSFP",
                " ICI ",
                "FEAEF",
                " VTV ",
                "PFLFP",
            ],
            "key": {
                "P": "ae2:spatial_pylon",
                "F": "tfmg:steel_frame",
                "S": "ae2:spatial_cell_component_128",
                "I": "ae2:spatial_io_port",
                "C": "advancedperipherals:chunk_controller",
                "E": "ae2:engineering_processor",
                "A": "appliedcreate:advanced_stress_processor",
                "V": "allthemodium:vibranium_plate",
                "T": "tfmg:transformer",
                "L": "tfmg:plastic_sheet",
            },
            "output": "ae2:spatial_anchor",
            "exclusive_output": True,
        },
        "industrial_colonies:v3_ae2/spatial_pylon_batch": _sequence(
            comment=(
                "Build four matched field pylons from four quartz frames and insulated "
                "fluix conductors, then install a routed P2P endpoint, engineering control, "
                "TFMG transformer and steel spine, brackets, and Train enclosure"
            ),
            input_item="ae2:quartz_glass",
            ingredients=[
                "3x ae2:quartz_glass",
                "4x tfmg:glass_cable_insulator",
                "4x ae2:fluix_glass_cable",
                "ae2:me_p2p_tunnel",
                "ae2:engineering_processor",
                "tfmg:transformer",
                "tfmg:steel_frame",
                "4x create:metal_bracket",
                "create:railway_casing",
            ],
            output="4x ae2:spatial_pylon",
            family="railway",
        ),
    }


def apply(data: dict[str, Any]) -> None:
    designs = _designs()
    if set(designs) != set(REDESIGNED_IDS):
        raise ValueError("remaining AE2 design table no longer matches rejected cohort")
    indexes = _index(data)
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        raise KeyError(f"expected active AE2 rejections are missing: {missing}")
    for recipe_id, process in designs.items():
        _replace(data, recipe_id, process)
    audit(data)


def _ingredients(recipe: Recipe) -> list[str]:
    return [
        step["ingredient"]
        for step in recipe.get("steps", [])
        if isinstance(step, dict) and step.get("op") == "deploying"
    ]


def _machines(recipe: Recipe) -> set[str]:
    return {
        step["machine"]
        for step in recipe.get("steps", [])
        if isinstance(step, dict) and isinstance(step.get("machine"), str)
    }


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    recipes = data.get("recipes", [])
    errors: list[str] = []
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        errors.append(f"missing remaining AE2 redesigns: {missing}")

    expected_machines = {
        **{recipe_id: {BRASS_DEPLOYER, BRASS_PRESS} for recipe_id in BRASS_IDS},
        **{recipe_id: {RAILWAY_DEPLOYER, RAILWAY_PRESS} for recipe_id in RAILWAY_IDS},
        **{recipe_id: {RADIANCE_DEPLOYER, RADIANCE_PRESS} for recipe_id in RADIANCE_IDS},
    }
    fingerprints: set[tuple[str, tuple[str, ...]]] = set()
    for recipe_id, machines in sorted(expected_machines.items()):
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not Sequenced Assembly")
            continue
        steps = recipe.get("steps", [])
        minimum, maximum = (11, 12) if recipe_id in RADIANCE_IDS else (10, 11)
        if not minimum <= len(steps) <= maximum:
            errors.append(f"{recipe_id} has unsupported sequence depth {len(steps)}")
        if _machines(recipe) != machines:
            errors.append(f"{recipe_id} escaped its assigned manufacturing family")
        expected_press = (
            RADIANCE_PRESS
            if recipe_id in RADIANCE_IDS
            else RAILWAY_PRESS
            if recipe_id in RAILWAY_IDS
            else BRASS_PRESS
        )
        if not steps or steps[-1] != _press(expected_press):
            errors.append(f"{recipe_id} lacks its final tier press closure")
        parts = _ingredients(recipe)
        if not any("tfmg:" in part for part in parts):
            errors.append(f"{recipe_id} lacks functional TFMG hardware")
        fingerprint = (str(recipe.get("input")), tuple(parts))
        if fingerprint in fingerprints:
            errors.append(f"{recipe_id} duplicates another digital manufacturing BOM")
        fingerprints.add(fingerprint)
        if "barrel" in repr(recipe).lower():
            errors.append(f"{recipe_id} still contains a wooden barrel")

    ladder_inputs = {
        "industrial_colonies:digital_storage/ae2_crafting_storage_16k": "ae2:4k_crafting_storage",
        "industrial_colonies:digital_storage/ae2_crafting_storage_64k": "ae2:16k_crafting_storage",
        "industrial_colonies:v3_ae2/cell_component_4k": "ae2:cell_component_1k",
        "industrial_colonies:v3_ae2/cell_component_16k": "ae2:cell_component_4k",
        "industrial_colonies:v3_ae2/fluid_storage_cell_64k": "ae2:fluid_storage_cell_16k",
        "industrial_colonies:v3_ae2/fluid_storage_cell_256k": "ae2:fluid_storage_cell_64k",
        "industrial_colonies:v3_ae2/item_storage_cell_256k": "ae2:item_storage_cell_64k",
    }
    for recipe_id, prior in ladder_inputs.items():
        if recipe_id in indexes and recipes[indexes[recipe_id]].get("input") != prior:
            errors.append(f"{recipe_id} no longer compounds prior tier {prior}")

    drive_id = "industrial_colonies:v3_ae2/drive"
    if drive_id in indexes:
        drive = recipes[indexes[drive_id]]
        if drive.get("input") != "tfmg:steel_frame":
            errors.append("ME Drive is not built on the approved steel frame enclosure")
        drive_parts = _ingredients(drive)
        for required in ("create:brass_casing", "4x ae2:item_cell_housing"):
            if required not in drive_parts:
                errors.append(f"ME Drive lacks physical enclosure component {required}")

    mega_housing_id = "industrial_colonies:v3_ae2/mega_fluid_cell_housing"
    if mega_housing_id in indexes:
        housing = recipes[indexes[mega_housing_id]]
        if housing.get("type") != "sequenced_assembly":
            errors.append("MEGA fluid housing fell back to compacting")
        for required in ("create:fluid_tank", "tfmg:steel_fluid_valve"):
            if required not in _ingredients(housing):
                errors.append(f"MEGA fluid housing lacks {required}")

    if SPATIAL_ANCHOR_ID in indexes:
        anchor = recipes[indexes[SPATIAL_ANCHOR_ID]]
        expected_pattern = ["PFSFP", " ICI ", "FEAEF", " VTV ", "PFLFP"]
        if anchor.get("type") != "mechanical_crafting":
            errors.append("Spatial Anchor did not regain Mechanical Crafting")
        if anchor.get("pattern") != expected_pattern:
            errors.append("Spatial Anchor no longer uses its deliberate 5x5 field-device shape")
        if any(len(row) != 5 for row in anchor.get("pattern", [])):
            errors.append("Spatial Anchor grid is not exactly 5x5")
        occupied = sum(character != " " for row in anchor.get("pattern", []) for character in row)
        if occupied != 21:
            errors.append(f"Spatial Anchor 5x5 has unexpected occupied-cell count {occupied}")
        if anchor.get("pattern", ["", "", ""])[2][2] != "A":
            errors.append("Spatial Anchor has no active control at the center of its 5x5")
        if anchor.get("key", {}).get("C") != "advancedperipherals:chunk_controller":
            errors.append("Spatial Anchor lost the user-designed Chunk Controller core")
        if "steps" in anchor or "machine" in anchor or "input" in anchor:
            errors.append("Spatial Anchor still carries stale sequence fields")

    pylon_id = "industrial_colonies:v3_ae2/spatial_pylon_batch"
    if pylon_id in indexes:
        pylon = recipes[indexes[pylon_id]]
        if pylon.get("output") != "4x ae2:spatial_pylon":
            errors.append("Spatial pylon line no longer returns a matched batch of four")
        for required in ("4x tfmg:glass_cable_insulator", "4x create:metal_bracket"):
            if required not in _ingredients(pylon):
                errors.append(f"Spatial pylon batch lacks physical part {required}")

    if errors:
        raise ValueError("remaining AE2 rejection audit failed: " + " | ".join(errors))
    return {
        "status": "PASS",
        "redesigned": len(REDESIGNED_IDS),
        "brass_line": len(BRASS_IDS),
        "railway_line": len(RAILWAY_IDS),
        "radiance_line": len(RADIANCE_IDS),
        "mechanical_5x5": 1,
        "unique_sequence_boms": len(fingerprints),
    }
