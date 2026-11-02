#!/usr/bin/env python3
"""Redesign the rejected orbital-control and outpost-electronics cohort.

These twelve IDs are exact active cards from the player's completed second
review pass.  Every card carried the same request for plastic, semiconductors,
and real circuit components.  This module answers that request as one coherent
hardware family: sensors and a satellite establish navigation, life-support
hardware keeps a habitat alive, a docking collar joins ships to the station,
and the same electronics language carries into the rover and planetary
utility machines.

The designs deliberately keep each block's physical identity.  A pump remains
a vertical fluid machine, an airlock remains an open doorway, a docking collar
keeps an open transfer throat, and sensors are populated as compact sequenced
assemblies.  Electronics are functional subassemblies rather than a perimeter
of generic expensive items.

``apply`` is source-only and idempotent.  It does not alter the review ledger,
mark a recipe approved, regenerate KJSGen projects, deploy, or touch the live
pack.  A changed card fingerprint is expected to return to Pending through the
separate review-reconciliation workflow.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

REFINED_RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
REFINED_RADIANCE_PRESS = "createcasing:refined_radiance_press"

REJECTION_NOTE = (
    "Needs more electronics: plastic, semiconductors, and circuit components."
)

# The reviewed hashes freeze the exact cards this module is allowed to answer.
# They are evidence, not an instruction to carry their rejected design forward.
REJECTION_CONTRACTS = {
    "industrial_colonies:planetary/outpost/energizer": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:0655e723297084c6ba88c60986f74ce4aab6d980fd4c8ee03d88e73ad88de2c8"
        ),
    },
    "industrial_colonies:planetary/outpost/gravity_normalizer": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:d105b80c6a8f31e5edae8f4605976508c1fb7a979c66384732d104518517c12f"
        ),
    },
    "industrial_colonies:planetary/outpost/water_pump": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:0e907d5aa3d79d41e1f9bef307b3755d8455203cd7197b3cc7ee399b60a679a4"
        ),
    },
    "industrial_colonies:space_coverage/compressor": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:4c0415a964527875554c277bb84ea7973635d9c230b629ce42b8fe2b36bdd92b"
        ),
    },
    "industrial_colonies:space_coverage/tier_1_rover": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:b3b98d75cd8344285378e2878d7c86de74f2ec3a00b3efc4896571fdb87a2b1c"
        ),
    },
    "industrial_colonies:space/dockyard/docking_connector": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:91a979543537cbe64404729b22bfe6264a93e801e29fc7849ba77d48851ebaae"
        ),
    },
    "industrial_colonies:space/life_support/airlock": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:e713c0cff9de823f363c2e0d9f68146f6791719e65c3c4eb8f1d0ba7bd57a4b3"
        ),
    },
    "industrial_colonies:space/life_support/oxygen_distributor": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:428da10e430fa14e8f297666fcd75eb564022a7c20fdf5c7f4e65d8977055375"
        ),
    },
    "industrial_colonies:space/life_support/oxygen_gear": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:3a44b0172d82cc4ead6009ce9b6ef8039bd3da96ed3165c85bd9dbec93b6f2d0"
        ),
    },
    "industrial_colonies:space/navigation/gimbal_sensor": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:8f7e1c8bad23b4b603259d62edbcbbe718b9378e990943cc504c0d44b69cb9a0"
        ),
    },
    "industrial_colonies:space/navigation/optical_sensor": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:2879bf734d6ddca78ac5e98a9bde38912f6401ff3eb380ce21c1aad346a2437c"
        ),
    },
    "industrial_colonies:space/navigation/sputnik": {
        "note": REJECTION_NOTE,
        "cardSha256": (
            "sha256:025740cd3aae959c84a3316d5c80d67af1b0971da34a639d28c5b397c52f3fa4"
        ),
    },
}

REDESIGNED_IDS = frozenset(REJECTION_CONTRACTS)

SEQUENCE_IDS = frozenset(
    {
        "industrial_colonies:space/life_support/oxygen_gear",
        "industrial_colonies:space/navigation/gimbal_sensor",
        "industrial_colonies:space/navigation/optical_sensor",
    }
)

GRID_IDS = REDESIGNED_IDS - SEQUENCE_IDS

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


def _deploy(ingredient: str) -> Recipe:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": REFINED_RADIANCE_DEPLOYER,
    }


def _press() -> Recipe:
    return {"op": "pressing", "machine": REFINED_RADIANCE_PRESS}


def _sequence(
    *,
    comment: str,
    input_item: str,
    ingredients: list[str],
    output: str,
) -> Recipe:
    if not 5 <= len(ingredients) <= 7:
        raise ValueError("orbital electronics sequences require 5-7 deployments")
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "steps": [*(_deploy(item) for item in ingredients), _press()],
        "loops": 1,
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
        raise ValueError("orbital-control grids must be explicit 5x5 silhouettes")
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
        "industrial_colonies:space/navigation/gimbal_sensor": _sequence(
            comment=(
                "Calibrate the gyroscopic core with a magnetic reference vane and "
                "TFMG potentiometer, then install a coated control board, calculation "
                "processor, discrete transistor, plastic isolation, and steel frame"
            ),
            input_item="simulated:gyroscopic_mechanism",
            ingredients=[
                "tfmg:magnetic_alloy_sheet",
                "tfmg:potentiometer",
                "tfmg:coated_circuit_board",
                "ae2:calculation_processor",
                "tfmg:transistor_item",
                "tfmg:plastic_sheet",
                "tfmg:steel_frame",
            ],
            output="simulated:gimbal_sensor",
        ),
        "industrial_colonies:space/navigation/optical_sensor": _sequence(
            comment=(
                "Populate a steel optical bench with an aluminum light baffle, "
                "amethyst objective, tinted-glass filter, TFMG transistor amplifier, "
                "etched sensor board, calculation processor, and plastic isolation"
            ),
            input_item="tfmg:steel_frame",
            ingredients=[
                "tfmg:aluminum_sheet",
                "minecraft:amethyst_shard",
                "minecraft:tinted_glass",
                "tfmg:transistor_item",
                "tfmg:etched_circuit_board",
                "ae2:calculation_processor",
                "tfmg:plastic_sheet",
            ],
            output="simulated:optical_sensor",
        ),
        "industrial_colonies:space/life_support/oxygen_gear": _sequence(
            comment=(
                "Turn a tested gas tank into a personal regulator by fitting a steel "
                "valve, electric metering pump, rubber harness, plastic manifold, "
                "coated TFMG controller, and transistor flow switch"
            ),
            input_item="ad_astra:gas_tank",
            ingredients=[
                "tfmg:steel_fluid_valve",
                "tfmg:electric_pump",
                "tfmg:rubber_sheet",
                "tfmg:plastic_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
            ],
            output="ad_astra:oxygen_gear",
        ),
        "industrial_colonies:space/navigation/sputnik": _grid(
            comment=(
                "Build Sputnik as a sensor cross: optical, gimbal, and velocity heads "
                "surround its navigation table; steel spars and aluminum skin carry "
                "the antenna, while a plastic-isolated etched board, engineering "
                "processor, and capacitor form the avionics deck"
            ),
            pattern=[" AOA ", "F G F", "LBNEL", "F V F", "APCPA"],
            key={
                "A": "tfmg:aluminum_sheet",
                "O": "simulated:optical_sensor",
                "F": "tfmg:steel_frame",
                "G": "simulated:gimbal_sensor",
                "L": "minecraft:lightning_rod",
                "B": "tfmg:etched_circuit_board",
                "N": "simulated:navigation_table",
                "E": "ae2:engineering_processor",
                "V": "simulated:velocity_sensor",
                "P": "tfmg:plastic_sheet",
                "C": "tfmg:capacitor_item",
            },
            output="rocketnautics:sputnik",
        ),
        "industrial_colonies:space/dockyard/docking_connector": _grid(
            comment=(
                "Keep the docking throat open while mounting item, fluid, energy, and "
                "wired-data interfaces at its cardinal points; the lower actuator bay "
                "adds a plastic-isolated TFMG board, capacitor, motor, cable, and "
                "ultimate interlock controller"
            ),
            pattern=["F I F", "P   E", "F D F", "LABML", "HCUCH"],
            key={
                "F": "tfmg:steel_frame",
                "I": "create:portable_storage_interface",
                "P": "create:portable_fluid_interface",
                "E": "createaddition:portable_energy_interface",
                "D": "computercraft:wired_modem",
                "L": "tfmg:plastic_sheet",
                "A": "tfmg:capacitor_item",
                "B": "tfmg:coated_circuit_board",
                "M": "tfmg:electric_motor",
                "H": "tfmg:heavy_plate",
                "C": "computercraft:cable",
                "U": "mekanism:ultimate_control_circuit",
            },
            output="2x simulated:docking_connector",
        ),
        "industrial_colonies:space/life_support/airlock": _grid(
            comment=(
                "Construct a paired pressure doorway instead of an ingredient ring: "
                "heavy doors sit inside rubber-sealed steel uprights, with an oxygen "
                "sensor and advanced computer above a plastic-isolated control board, "
                "capacitor bank, and motorized latch"
            ),
            pattern=[" HHH ", "RFCSR", "HT TH", "RFPBR", "HAMAH"],
            key={
                "H": "tfmg:heavy_plate",
                "R": "tfmg:rubber_sheet",
                "F": "tfmg:steel_frame",
                "C": "computercraft:computer_advanced",
                "S": "ad_astra:oxygen_sensor",
                "T": "tfmg:heavy_plated_door",
                "P": "tfmg:plastic_sheet",
                "B": "tfmg:coated_circuit_board",
                "A": "tfmg:capacitor_item",
                "M": "tfmg:electric_motor",
            },
            output="2x ad_astra:airlock",
        ),
        "industrial_colonies:space/life_support/oxygen_distributor": _grid(
            comment=(
                "Build a real life-support manifold: paired fans feed a valved loader "
                "between large gas tanks, oxygen gear samples the outlet, and a TFMG "
                "etched board, capacitor, transistor, plastic insulation, advanced "
                "computer, and energy cube supervise the powered base"
            ),
            pattern=[" FVF ", "GPLTG", " OBO ", "FCXCF", " HUH "],
            key={
                "F": "ad_astra:fan",
                "V": "tfmg:steel_fluid_valve",
                "G": "ad_astra:large_gas_tank",
                "P": "tfmg:plastic_sheet",
                "L": "ad_astra:oxygen_loader",
                "T": "computercraft:computer_advanced",
                "O": "ad_astra:oxygen_gear",
                "B": "tfmg:etched_circuit_board",
                "C": "tfmg:capacitor_item",
                "X": "tfmg:transistor_item",
                "H": "tfmg:heavy_plate",
                "U": "mekanism:ultimate_energy_cube",
            },
            output="ad_astra:oxygen_distributor",
        ),
        "industrial_colonies:space_coverage/compressor": _grid(
            comment=(
                "Build the orbital compressor around opposed pistons, a TFMG motor, "
                "steel gearing and pressure pipe; the service bay adds a plastic "
                "insulator, capacitor, coated controller, advanced control circuit, "
                "and steel-frame feet instead of unrelated perimeter filler"
            ),
            pattern=["P   P", "HCMCH", "HSGSH", "HLAUH", "F B F"],
            key={
                "P": "minecraft:piston",
                "H": "ad_astra:steel_panel",
                "C": "tfmg:steel_cogwheel",
                "M": "tfmg:electric_motor",
                "S": "tfmg:steel_mechanism",
                "G": "tfmg:steel_pipe",
                "L": "tfmg:plastic_sheet",
                "A": "tfmg:capacitor_item",
                "U": "mekanism:advanced_control_circuit",
                "F": "tfmg:steel_frame",
                "B": "tfmg:coated_circuit_board",
            },
            output="ad_astra:compressor",
        ),
        "industrial_colonies:space_coverage/tier_1_rover": _grid(
            comment=(
                "Assemble a recognizable four-wheel Desh rover: computer, radio, and "
                "navigation table fill the cab; a capacitor, etched board, and "
                "calculation processor form the avionics shelf; plastic-isolated tank "
                "and energy storage ride in the steel chassis ahead of the engine"
            ),
            pattern=[" CNR ", "BLAKE", "FPGPF", "W Q W", " W W "],
            key={
                "C": "computercraft:computer_advanced",
                "N": "simulated:navigation_table",
                "R": "ad_astra:radio",
                "B": "ad_astra:desh_plate",
                "L": "tfmg:etched_circuit_board",
                "A": "tfmg:capacitor_item",
                "K": "ae2:calculation_processor",
                "E": "ad_astra:desh_engine",
                "F": "tfmg:steel_frame",
                "P": "tfmg:plastic_sheet",
                "G": "ad_astra:desh_tank",
                "W": "ad_astra:wheel",
                "Q": "mekanism:advanced_energy_cube",
            },
            output="ad_astra:tier_1_rover",
        ),
        "industrial_colonies:planetary/outpost/water_pump": _grid(
            comment=(
                "Raise a Desh pump tower from a fluid tank and valved steel intake to "
                "an electric pump head; a plastic-isolated coated board, paired "
                "capacitors, and elite controller meter the column from inside rather "
                "than decorating its perimeter"
            ),
            pattern=["  E  ", "DACAD", "DLULD", "DSVSD", "DDTDD"],
            key={
                "E": "tfmg:electric_pump",
                "D": "ad_astra:desh_plate",
                "A": "tfmg:capacitor_item",
                "C": "tfmg:coated_circuit_board",
                "L": "tfmg:plastic_sheet",
                "U": "mekanism:elite_control_circuit",
                "S": "tfmg:steel_pipe",
                "V": "tfmg:steel_fluid_valve",
                "T": "tfmg:steel_fluid_tank",
            },
            output="ad_astra:water_pump",
        ),
        "industrial_colonies:planetary/outpost/gravity_normalizer": _grid(
            comment=(
                "Form twin Desh field arches around electromagnetic coils and an "
                "ultimate energy cube; transformers feed the cable bridge while a "
                "plastic-isolated etched board, transistor, capacitor, engineering "
                "processor, and ultimate controller close the field-control rack"
            ),
            pattern=["T E T", "DFPFD", "DWQWD", "DFXFD", " CUG "],
            key={
                "T": "tfmg:transformer",
                "E": "ae2:engineering_processor",
                "D": "ad_astra:desh_plate",
                "F": "tfmg:electromagnetic_coil",
                "P": "tfmg:plastic_sheet",
                "W": "mekanism:ultimate_universal_cable",
                "Q": "mekanism:ultimate_energy_cube",
                "X": "tfmg:transistor_item",
                "C": "tfmg:capacitor_item",
                "U": "mekanism:ultimate_control_circuit",
                "G": "tfmg:etched_circuit_board",
            },
            output="ad_astra:gravity_normalizer",
        ),
        "industrial_colonies:planetary/outpost/energizer": _grid(
            comment=(
                "Keep the charging bay open between Ostrum posts: an ultimate energy "
                "cube feeds the overhead transformer and engineering processor, while "
                "plastic standoffs, capacitors, copper bus wire, an etched TFMG board, "
                "and ultimate controller instrument the interlocked base"
            ),
            pattern=[" CET ", "OPQPO", "O   O", "OWGWO", "BBUBB"],
            key={
                "C": "tfmg:capacitor_item",
                "E": "ae2:engineering_processor",
                "T": "tfmg:transformer",
                "O": "ad_astra:ostrum_plate",
                "P": "tfmg:plastic_sheet",
                "Q": "mekanism:ultimate_energy_cube",
                "W": "tfmg:copper_wire",
                "G": "tfmg:etched_circuit_board",
                "B": "ad_astra:ostrum_block",
                "U": "mekanism:ultimate_control_circuit",
            },
            output="ad_astra:energizer",
        ),
    }


def apply(data: dict[str, Any]) -> None:
    designs = _designs()
    if set(designs) != set(REDESIGNED_IDS):
        raise ValueError("space-electronics design table no longer matches contracts")
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
    if not pattern:
        return False
    return (
        all(char != " " for char in pattern[0])
        and all(char != " " for char in pattern[-1])
        and all(row[0] != " " and row[-1] != " " for row in pattern)
    )


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    errors: list[str] = []
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        errors.append(f"missing space-electronics redesigns: {missing}")

    recipes = data.get("recipes", [])
    functional_signatures = {
        "industrial_colonies:space/navigation/gimbal_sensor": {
            "simulated:gyroscopic_mechanism",
            "tfmg:potentiometer",
            "tfmg:magnetic_alloy_sheet",
        },
        "industrial_colonies:space/navigation/optical_sensor": {
            "minecraft:amethyst_shard",
            "minecraft:tinted_glass",
        },
        "industrial_colonies:space/navigation/sputnik": {
            "simulated:optical_sensor",
            "simulated:gimbal_sensor",
            "simulated:velocity_sensor",
            "simulated:navigation_table",
        },
        "industrial_colonies:space/dockyard/docking_connector": {
            "create:portable_storage_interface",
            "create:portable_fluid_interface",
            "createaddition:portable_energy_interface",
            "computercraft:wired_modem",
        },
        "industrial_colonies:space/life_support/airlock": {
            "tfmg:heavy_plated_door",
            "ad_astra:oxygen_sensor",
        },
        "industrial_colonies:space/life_support/oxygen_distributor": {
            "ad_astra:oxygen_loader",
            "ad_astra:large_gas_tank",
            "ad_astra:fan",
        },
        "industrial_colonies:space/life_support/oxygen_gear": {
            "ad_astra:gas_tank",
            "tfmg:steel_fluid_valve",
            "tfmg:electric_pump",
        },
        "industrial_colonies:space_coverage/compressor": {
            "minecraft:piston",
            "tfmg:electric_motor",
            "tfmg:steel_pipe",
        },
        "industrial_colonies:space_coverage/tier_1_rover": {
            "ad_astra:desh_engine",
            "ad_astra:desh_tank",
            "ad_astra:wheel",
            "simulated:navigation_table",
        },
        "industrial_colonies:planetary/outpost/water_pump": {
            "tfmg:electric_pump",
            "tfmg:steel_fluid_tank",
            "tfmg:steel_fluid_valve",
        },
        "industrial_colonies:planetary/outpost/gravity_normalizer": {
            "tfmg:electromagnetic_coil",
            "tfmg:transformer",
            "mekanism:ultimate_energy_cube",
        },
        "industrial_colonies:planetary/outpost/energizer": {
            "tfmg:transformer",
            "mekanism:ultimate_energy_cube",
            "ad_astra:ostrum_block",
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
        if "tfmg:plastic_sheet" not in ingredients:
            errors.append(f"{recipe_id} has no plastic insulation")
        if not (semiconductor_parts & ingredients):
            errors.append(f"{recipe_id} has no discrete semiconductor component")
        if not (circuit_parts & ingredients):
            errors.append(f"{recipe_id} has no TFMG/processor circuit component")
        missing_signatures = functional_signatures[recipe_id] - ingredients
        if missing_signatures:
            errors.append(
                f"{recipe_id} lost functional hardware {sorted(missing_signatures)}"
            )
        if "mekanism:steel_casing" in ingredients:
            errors.append(f"{recipe_id} restored Mekanism steel casing")

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
        frozen_pattern = tuple(pattern)
        if frozen_pattern in patterns:
            errors.append(
                f"{recipe_id} copied the shape from {patterns[frozen_pattern]}"
            )
        patterns[frozen_pattern] = recipe_id

    for recipe_id in sorted(SEQUENCE_IDS):
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not Sequenced Assembly")
            continue
        steps = recipe.get("steps", [])
        if not 6 <= len(steps) <= 8:
            errors.append(f"{recipe_id} has unjustified sequence length {len(steps)}")
        expected_machines = {
            REFINED_RADIANCE_DEPLOYER,
            REFINED_RADIANCE_PRESS,
        }
        machines = {
            step.get("machine")
            for step in steps
            if isinstance(step, dict) and isinstance(step.get("machine"), str)
        }
        if machines != expected_machines:
            errors.append(f"{recipe_id} escaped the Refined Radiance line")
        if not steps or steps[-1] != _press():
            errors.append(f"{recipe_id} does not finish with the line press")
        if recipe.get("loops") != 1:
            errors.append(f"{recipe_id} has an unjustified repeated loop")

    if errors:
        raise ValueError(
            "Space-electronics rejection audit failed: " + " | ".join(errors)
        )
    return {
        "status": "PASS",
        "redesigned": len(REDESIGNED_IDS),
        "mechanical_crafting": len(GRID_IDS),
        "sequenced_assembly": len(SEQUENCE_IDS),
        "review_state": "pending_after_reconciliation",
    }
