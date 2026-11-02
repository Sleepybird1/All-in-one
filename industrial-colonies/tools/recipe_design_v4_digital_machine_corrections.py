#!/usr/bin/env python3
"""Resolve a bounded second-pass cohort of digital-machine rejections.

The ten recipe IDs below were exact, active rejected cards in the deployed
Default project.  ``REJECTION_CONTRACTS`` freezes the user's note and the
reviewed design hash so later work cannot silently reinterpret which decision
this source module addresses.  The module itself only edits managed source; it
does not mutate review ledgers, projects, acceptance files, or the live pack.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"

REJECTION_CONTRACTS = {
    "industrial_colonies:computer_network_coverage/memory_card": {
        "note": (
            "Wrong machine. Suggested Recipe type alternative(s): Crafting, "
            "Mechanical Crafting, Sequenced Assembly."
        ),
        "cardSha256": (
            "sha256:3b0f3d3fa65b238ffc69202a35e6c7d9a462aa4a6b430c96cb9cbff16d63687a"
        ),
    },
    "industrial_colonies:computercraft/monitor/normal": {
        "note": "Wrong machine. Suggested Recipe type alternative(s): Mechanical Crafting.",
        "cardSha256": (
            "sha256:ac0a1522f906e74eefebc3046db8b32c01d390b139dda9c6c194f28d7fb6fa16"
        ),
    },
    "industrial_colonies:create_addons/tri_polar_energy_meter": {
        "note": "The materials and shape do not fit what this machine does.",
        "cardSha256": (
            "sha256:cdc2c7cf0ceaf9afe9e2e539a7c8e907baa6adf917c25b95274569e40f5deba0"
        ),
    },
    "industrial_colonies:mekanism/laser/tractor_beam": {
        "note": (
            "Wrong machine. Suggested Machine family alternative(s): Copper, "
            "Brass, Railway."
        ),
        "cardSha256": (
            "sha256:1c061b704e0bbe10153c7ada4d5f59e8bb736b87d841cfd0d671447bbc93d79f"
        ),
    },
    "industrial_colonies:mekanism_components/teleportation_core": {
        "note": "wrong machine type and cost",
        "cardSha256": (
            "sha256:73236d782fbd193be6db901e6182424525d5a3eda349d6c22a05cf40b2ca4dd1"
        ),
    },
    "industrial_colonies:mekanism_components/upgrade_filter": {
        "note": (
            "Wrong machine. Suggested Machine family alternative(s): Copper, "
            "Brass, Railway."
        ),
        "cardSha256": (
            "sha256:141245e59d9d75b597499d9dfa62b5a7c134a2fe2aeb07e656995aa3d45a4a55"
        ),
    },
    "industrial_colonies:mekanism_components/upgrade_muffling": {
        "note": (
            "Wrong machine. Suggested Machine family alternative(s): Copper, "
            "Brass, Railway."
        ),
        "cardSha256": (
            "sha256:4b9260853d6f981d5b0fbad268eee736f9c7e0e86684ec09efe8b4abc6dad2b6"
        ),
    },
    "industrial_colonies:mekanism_components/upgrade_stone_generator": {
        "note": (
            "Wrong machine. Suggested Machine family alternative(s): Copper, "
            "Brass, Railway."
        ),
        "cardSha256": (
            "sha256:c74c533e64607eb502ff2c416b6982ce978e2c70b10bd813cd26ebe735a429f6"
        ),
    },
    "industrial_colonies:v3_ae2/item_storage_cell_1k": {
        "note": "Wrong machine. Suggested Machine family alternative(s): Copper.",
        "cardSha256": (
            "sha256:5f24c3d9eb3fe8267dff36a64db8549604fed85e6409b4781fa2d43eec8d7452"
        ),
    },
    "industrial_colonies:v3_ae2/spatial_io_port": {
        "note": (
            "Wrong machine. Suggested Machine family alternative(s): Copper, "
            "Brass, Railway."
        ),
        "cardSha256": (
            "sha256:11e8f791a99d0492277a3c0cf7f9e42d8afaddda2bc06e5eeb53af1f858d676a"
        ),
    },
}

REDESIGNED_IDS = frozenset(REJECTION_CONTRACTS)

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
    transitional: str,
    ingredients: list[str],
    output: Any,
    deployer: str,
    press: str,
) -> Recipe:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional,
        "steps": [*(_deploy(item, deployer) for item in ingredients), _press(press)],
        "loops": 1,
        "output": output,
        "exclusive_output": True,
    }


def _designs() -> dict[str, Recipe]:
    return {
        "industrial_colonies:computercraft/monitor/normal": {
            "type": "mechanical_crafting",
            "comment": (
                "Build two rectangular monitor panels: a thin Brass bezel surrounds "
                "rose-quartz pixels and display drivers, while a plastic service panel "
                "and TFMG copper bus close the lower edge"
            ),
            "pattern": [
                "BRRB",
                "RDDR",
                "RDDR",
                "BPCB",
            ],
            "key": {
                "B": "create:brass_sheet",
                "R": "create:polished_rose_quartz",
                "D": "create:display_board",
                "P": "tfmg:plastic_sheet",
                "C": "tfmg:copper_wire",
            },
            "output": {"kind": "ITEM", "id": "computercraft:monitor_normal", "count": 2},
            "exclusive_output": True,
        },
        "industrial_colonies:computer_network_coverage/memory_card": _sequence(
            comment=(
                "Laminate an AE 1k memory die, a TFMG coated controller board, gold "
                "contacts, copper data traces, and a magnetic stripe into a plastic card"
            ),
            input_item="tfmg:plastic_sheet",
            transitional="tfmg:plastic_sheet",
            ingredients=[
                "tfmg:magnetic_alloy_sheet",
                "ae2:cell_component_1k",
                "tfmg:coated_circuit_board",
                "tfmg:copper_wire",
                "create:golden_sheet",
            ],
            output="advancedperipherals:memory_card",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:create_addons/tri_polar_energy_meter": _sequence(
            comment=(
                "Convert the proven energy meter to true three-pole measurement by "
                "installing one current transformer per pole, a triple terminal, a "
                "copper sensing winding, an isolated transformer, and supervisory logic"
            ),
            input_item="electroenergetics:energy_meter",
            transitional="electroenergetics:energy_meter",
            ingredients=[
                "electroenergetics:triple_connector",
                "electroenergetics:current_transformer",
                "electroenergetics:current_transformer",
                "electroenergetics:current_transformer",
                "tfmg:copper_spool",
                "tfmg:transformer",
                "mekanism:advanced_control_circuit",
            ],
            output="electroenergetics:tri_polar_energy_meter",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:mekanism/laser/tractor_beam": _sequence(
            comment=(
                "Turn a laser amplifier into an item-capture beamline with a magnetic "
                "field yoke and coil, teleport focus, buffered chest, routed transporter, "
                "and ultimate beam-control logic"
            ),
            input_item="mekanism:laser_amplifier",
            transitional="mekanism:laser_amplifier",
            ingredients=[
                "tfmg:magnetic_alloy_sheet",
                "tfmg:electromagnetic_coil",
                "mekanism:teleportation_core",
                "mekanism:personal_chest",
                "mekanism:advanced_logistical_transporter",
                "mekanism:ultimate_control_circuit",
            ],
            output="mekanism:laser_tractor_beam",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:mekanism_components/teleportation_core": _sequence(
            comment=(
                "Stabilize an Ender Pearl with one atomic containment layer, a TFMG "
                "magnetic yoke and field coil, diamond focus, elite control, and plastic "
                "insulation; Railway precision replaces the former overbuilt tooling"
            ),
            input_item="minecraft:ender_pearl",
            transitional="minecraft:ender_pearl",
            ingredients=[
                "mekanism:alloy_atomic",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:electromagnetic_coil",
                "minecraft:diamond",
                "mekanism:elite_control_circuit",
                "tfmg:plastic_sheet",
            ],
            output="mekanism:teleportation_core",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:mekanism_components/upgrade_filter": _sequence(
            comment=(
                "Populate the module base with a real Create filter, a TFMG coated "
                "control board, chemical-safe plastic, and an infused actuator"
            ),
            input_item="mekanism:module_base",
            transitional="mekanism:module_base",
            ingredients=[
                "create:filter",
                "tfmg:coated_circuit_board",
                "tfmg:plastic_sheet",
                "mekanism:alloy_infused",
            ],
            output="mekanism:upgrade_filter",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:mekanism_components/upgrade_muffling": _sequence(
            comment=(
                "Wrap the module base in wool, TFMG rubber damping, and a plastic shell, "
                "then lock the quiet cartridge with infused alloy"
            ),
            input_item="mekanism:module_base",
            transitional="mekanism:module_base",
            ingredients=[
                "2x minecraft:white_wool",
                "2x tfmg:rubber_sheet",
                "tfmg:plastic_sheet",
                "mekanism:alloy_infused",
            ],
            output="mekanism:upgrade_muffling",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:mekanism_components/upgrade_stone_generator": _sequence(
            comment=(
                "Build isolated water and lava feeds around a refractory separator, "
                "TFMG steel conduit, plastic cartridge shell, and process controller"
            ),
            input_item="mekanism:module_base",
            transitional="mekanism:module_base",
            ingredients=[
                "minecraft:water_bucket",
                "minecraft:lava_bucket",
                "tfmg:fireproof_brick_reinforcement",
                "tfmg:steel_pipe",
                "tfmg:plastic_sheet",
                "mekanism:advanced_control_circuit",
            ],
            output="mekanism:upgrade_stone_generator",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:v3_ae2/item_storage_cell_1k": _sequence(
            comment=(
                "Use the Copper electronics line to install a 1k memory plane, logic "
                "index, TFMG copper bus, rubber insulation, and quartz service face in "
                "the item-cell housing"
            ),
            input_item="ae2:item_cell_housing",
            transitional="ae2:item_cell_housing",
            ingredients=[
                "ae2:cell_component_1k",
                "ae2:logic_processor",
                "tfmg:copper_wire",
                "tfmg:rubber_sheet",
                "ae2:quartz_glass",
            ],
            output="ae2:item_storage_cell_1k",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:v3_ae2/spatial_io_port": _sequence(
            comment=(
                "Rebuild the IO Port as a Railway-precision field gateway with an ME "
                "controller, P2P endpoint, 2-cubed spatial core, engineering logic, "
                "isolated power, TFMG steel frame, and plastic insulation"
            ),
            input_item="ae2:io_port",
            transitional="ae2:io_port",
            ingredients=[
                "ae2:controller",
                "ae2:me_p2p_tunnel",
                "ae2:spatial_cell_component_2",
                "ae2:engineering_processor",
                "tfmg:transformer",
                "tfmg:steel_frame",
                "tfmg:plastic_sheet",
            ],
            output="ae2:spatial_io_port",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
    }


def apply(data: dict[str, Any]) -> None:
    designs = _designs()
    if set(designs) != set(REDESIGNED_IDS):
        raise ValueError("digital-machine design table no longer matches rejection contracts")
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


def _sequence_machines(recipe: Recipe) -> set[str]:
    return {
        step["machine"]
        for step in recipe.get("steps", [])
        if isinstance(step, dict) and isinstance(step.get("machine"), str)
    }


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    errors: list[str] = []
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        errors.append(f"missing digital-machine redesigns: {missing}")
    recipes = data.get("recipes", [])

    monitor_id = "industrial_colonies:computercraft/monitor/normal"
    if monitor_id in indexes:
        monitor = recipes[indexes[monitor_id]]
        pattern = monitor.get("pattern")
        if monitor.get("type") != "mechanical_crafting":
            errors.append("normal monitor is not Mechanical Crafting")
        if pattern != ["BRRB", "RDDR", "RDDR", "BPCB"]:
            errors.append("normal monitor lost its dense rectangular display silhouette")
        if not isinstance(pattern, list) or any(" " in row for row in pattern):
            errors.append("normal monitor became a sparse grid")

    expected_family = {
        "industrial_colonies:computer_network_coverage/memory_card": {
            BRASS_DEPLOYER,
            BRASS_PRESS,
        },
        "industrial_colonies:create_addons/tri_polar_energy_meter": {
            RAILWAY_DEPLOYER,
            RAILWAY_PRESS,
        },
        "industrial_colonies:mekanism/laser/tractor_beam": {
            RAILWAY_DEPLOYER,
            RAILWAY_PRESS,
        },
        "industrial_colonies:mekanism_components/teleportation_core": {
            RAILWAY_DEPLOYER,
            RAILWAY_PRESS,
        },
        "industrial_colonies:mekanism_components/upgrade_filter": {
            COPPER_DEPLOYER,
            COPPER_PRESS,
        },
        "industrial_colonies:mekanism_components/upgrade_muffling": {
            COPPER_DEPLOYER,
            COPPER_PRESS,
        },
        "industrial_colonies:mekanism_components/upgrade_stone_generator": {
            COPPER_DEPLOYER,
            COPPER_PRESS,
        },
        "industrial_colonies:v3_ae2/item_storage_cell_1k": {
            COPPER_DEPLOYER,
            COPPER_PRESS,
        },
        "industrial_colonies:v3_ae2/spatial_io_port": {
            RAILWAY_DEPLOYER,
            RAILWAY_PRESS,
        },
    }
    for recipe_id, machines in expected_family.items():
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not Sequenced Assembly")
            continue
        steps = recipe.get("steps", [])
        if not 5 <= len(steps) <= 8:
            errors.append(f"{recipe_id} has an unjustified sequence length {len(steps)}")
        if _sequence_machines(recipe) != machines:
            errors.append(f"{recipe_id} escaped its reviewed machine family")
        if not steps or steps[-1] != _press(next(m for m in machines if m.endswith("_press"))):
            errors.append(f"{recipe_id} does not finish with its family press")

    if "industrial_colonies:create_addons/tri_polar_energy_meter" in indexes:
        meter = recipes[indexes["industrial_colonies:create_addons/tri_polar_energy_meter"]]
        meter_parts = _sequence_ingredients(meter)
        if meter_parts.count("electroenergetics:current_transformer") != 3:
            errors.append("tri-polar meter does not measure all three poles")
        for part in ("electroenergetics:triple_connector", "tfmg:copper_spool", "tfmg:transformer"):
            if part not in meter_parts:
                errors.append(f"tri-polar meter is missing functional part {part}")

    if "industrial_colonies:mekanism_components/teleportation_core" in indexes:
        core = recipes[indexes["industrial_colonies:mekanism_components/teleportation_core"]]
        core_parts = _sequence_ingredients(core)
        if core_parts.count("mekanism:alloy_atomic") != 1:
            errors.append("teleportation core restored the rejected doubled atomic cost")
        if "mekanism:ultimate_control_circuit" in core_parts:
            errors.append("teleportation core restored the rejected ultimate-circuit cost")
        for part in ("tfmg:electromagnetic_coil", "tfmg:magnetic_alloy_sheet"):
            if part not in core_parts:
                errors.append(f"teleportation core is missing field component {part}")

    if "industrial_colonies:mekanism/laser/tractor_beam" in indexes:
        beam = recipes[indexes["industrial_colonies:mekanism/laser/tractor_beam"]]
        beam_parts = _sequence_ingredients(beam)
        for part in ("mekanism:teleportation_core", "tfmg:electromagnetic_coil", "mekanism:personal_chest"):
            if part not in beam_parts:
                errors.append(f"tractor beam is missing functional part {part}")

    unique_upgrade_parts = {
        "industrial_colonies:mekanism_components/upgrade_filter": "create:filter",
        "industrial_colonies:mekanism_components/upgrade_muffling": "tfmg:rubber_sheet",
        "industrial_colonies:mekanism_components/upgrade_stone_generator": (
            "tfmg:fireproof_brick_reinforcement"
        ),
    }
    for recipe_id, signature in unique_upgrade_parts.items():
        if recipe_id in indexes and not any(
            ingredient == signature or ingredient.endswith(" " + signature)
            for ingredient in _sequence_ingredients(recipes[indexes[recipe_id]])
        ):
            errors.append(f"{recipe_id} lost its functional identity")

    if errors:
        raise ValueError("Digital-machine rejection audit failed: " + " | ".join(errors))
    return {
        "status": "PASS",
        "redesigned": len(REDESIGNED_IDS),
        "mechanical_crafting": 1,
        "sequenced_assembly": len(REDESIGNED_IDS) - 1,
        "copper_line": 4,
        "brass_line": 1,
        "railway_line": 4,
    }
