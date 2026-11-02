#!/usr/bin/env python3
"""Finish the manually rejected Nuclear Engineering hardware recipes.

The user liked the physical intent of these machines, but rejected their
manufacturing tier or cost.  Structural shells and rotor pieces therefore use
focused Refined Radiance compacting batches, while the endgame
Nucleosynthesizer becomes a recognizable accelerator/control assembly.  The
recipes deliberately avoid decorative perimeter rings and retain their exact
stock-removal ownership.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

INDUSTRIAL_DEPLOYER = "createcasing:industrial_iron_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"

REDESIGNED_IDS = frozenset(
    {
        "industrial_colonies:bigreactors/energizer/casing",
        "industrial_colonies:bigreactors/fluidizer/casing",
        "industrial_colonies:bigreactors/basic_turbine/casing",
        "industrial_colonies:bigreactors/basic_turbine/rotor_blade",
        "industrial_colonies:bigreactors/basic_turbine/rotor_shaft",
        "industrial_colonies:nuclear/refined_radiance_casing",
        "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer",
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


def _compacting(*, comment: str, inputs: list[str], output: str) -> Recipe:
    return {
        "type": "compacting",
        "comment": comment,
        "inputs": inputs,
        "machine": RADIANCE_PRESS,
        "output": output,
        "exclusive_output": True,
    }


def _deploy(ingredient: str) -> Recipe:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": RADIANCE_DEPLOYER,
    }


def redesigns() -> dict[str, Recipe]:
    result = {
        "industrial_colonies:bigreactors/energizer/casing": _compacting(
            comment=(
                "Compress eight Energizer shell segments from radiance field lining, "
                "steel frames and plate, transformer windings, induction buffering, "
                "capacitors, and a high-current cable termination."
            ),
            inputs=[
                "2x create:refined_radiance_casing",
                "4x tfmg:steel_frame",
                "8x tfmg:heavy_plate",
                "4x tfmg:transformer",
                "2x mekanism:elite_induction_cell",
                "4x tfmg:capacitor_item",
                "2x tfmg:steel_cable_hub",
            ],
            output="8x bigreactors:energizercasing",
        ),
        "industrial_colonies:bigreactors/fluidizer/casing": _compacting(
            comment=(
                "Pressure-form eight Fluidizer shell segments around paired chemical "
                "vats, pumped steel manifolds, service valves, radiance lining, and "
                "a load-bearing steel frame."
            ),
            inputs=[
                "2x create:refined_radiance_casing",
                "4x tfmg:steel_frame",
                "8x tfmg:heavy_plate",
                "2x tfmg:steel_chemical_vat",
                "4x tfmg:steel_pipe",
                "2x tfmg:electric_pump",
                "2x mekanism:dynamic_valve",
            ],
            output="8x bigreactors:fluidizercasing",
        ),
        "industrial_colonies:bigreactors/basic_turbine/casing": _compacting(
            comment=(
                "Laminate eight turbine-generator shell segments from Cyanite field "
                "metal, radiance lining, framed heavy plate, generator windings, and "
                "transformer isolation after first reactor waste."
            ),
            inputs=[
                "2x create:refined_radiance_casing",
                "4x tfmg:steel_frame",
                "8x tfmg:heavy_plate",
                "4x bigreactors:cyanite_ingot",
                "2x tfmg:generator",
                "2x tfmg:large_coil",
                "2x tfmg:transformer",
            ],
            output="8x bigreactors:basic_turbinecasing",
        ),
        "industrial_colonies:bigreactors/basic_turbine/rotor_blade": _compacting(
            comment=(
                "Stamp four balanced turbine blades from Cyanite-alloy cores, tapered "
                "aluminum skins, heavy steel roots, and matched drive mechanisms."
            ),
            inputs=[
                "4x bigreactors:cyanite_ingot",
                "8x tfmg:aluminum_sheet",
                "4x tfmg:heavy_plate",
                "4x tfmg:steel_mechanism",
                "2x tfmg:magnetic_alloy_ingot",
            ],
            output="4x bigreactors:basic_turbinerotorblade",
        ),
        "industrial_colonies:bigreactors/basic_turbine/rotor_shaft": _compacting(
            comment=(
                "Key four rotor-shaft modules around concentric Create shafts and steel "
                "tube, then lock them with Cyanite bearings, magnetic laminations, and "
                "serviceable drive mechanisms."
            ),
            inputs=[
                "8x create:shaft",
                "4x tfmg:steel_pipe",
                "4x tfmg:steel_mechanism",
                "4x bigreactors:cyanite_ingot",
                "4x tfmg:magnetic_alloy_ingot",
                "2x tfmg:heavy_plate",
            ],
            output="4x bigreactors:basic_turbinerotorshaft",
        ),
        "industrial_colonies:nuclear/refined_radiance_casing": {
            "type": "deploying",
            "comment": (
                "Bond Refined Radiance directly onto an Industrial Iron block on the "
                "Industrial Iron line; the new casing cannot require its own machines."
            ),
            "input": "create:industrial_iron_block",
            "held": "create:refined_radiance",
            "machine": INDUSTRIAL_DEPLOYER,
            "output": "create:refined_radiance_casing",
        },
        "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer": {
            "type": "sequenced_assembly",
            "comment": (
                "Turn a radiance-lined accelerator body into the final nucleosynthesis "
                "instrument with SPS injection, antimatter and polonium targets, quantum "
                "timing, accumulated control logic, grid isolation, and a late-alloy "
                "containment spine."
            ),
            "input": "create:refined_radiance_casing",
            "transitional": "create:refined_radiance_casing",
            "steps": [
                _deploy("mekanism:sps_port"),
                _deploy("mekanism:supercharged_coil"),
                _deploy("mekanism:pellet_antimatter"),
                _deploy("mekanism:pellet_polonium"),
                _deploy("mekanism:ultimate_control_circuit"),
                _deploy("megacells:accumulation_processor"),
                _deploy("ae2:quantum_entangled_singularity"),
                _deploy("tfmg:transformer"),
                _deploy("allthemodium:unobtainium_vibranium_alloy_ingot"),
                {"op": "pressing", "machine": RADIANCE_PRESS},
            ],
            "loops": 1,
            "output": "mekanism:antiprotonic_nucleosynthesizer",
            "exclusive_output": True,
        },
    }
    if set(result) != REDESIGNED_IDS:
        raise AssertionError("internal nuclear-hardware redesign coverage drifted")
    return result


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


def apply(data: dict[str, Any]) -> None:
    indexes = _index(data)
    missing = sorted(REDESIGNED_IDS - set(indexes))
    if missing:
        raise KeyError(f"expected manually rejected nuclear recipes are missing: {missing}")
    for recipe_id, process in redesigns().items():
        recipe = data["recipes"][indexes[recipe_id]]
        for field in _PROCESS_FIELDS:
            recipe.pop(field, None)
        recipe.update(deepcopy(process))
    report = audit(data)
    if report["errors"]:
        raise ValueError("nuclear-hardware redesign audit failed: " + "; ".join(report["errors"]))


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    errors: list[str] = []
    if not REDESIGNED_IDS <= set(indexes):
        errors.append("one or more manually rejected nuclear recipes are missing")
    for recipe_id in sorted(REDESIGNED_IDS & set(indexes)):
        recipe = data["recipes"][indexes[recipe_id]]
        text = repr(recipe)
        if "mekanism:steel_casing" in text or "tfmg:steel_sheet" in text:
            errors.append(f"{recipe_id} uses a retired structural ingredient")
        if recipe_id == "industrial_colonies:nuclear/refined_radiance_casing":
            if recipe.get("input") != "create:industrial_iron_block":
                errors.append("Refined Radiance casing no longer starts from Industrial Iron")
            if recipe.get("machine") != INDUSTRIAL_DEPLOYER:
                errors.append("Refined Radiance casing is not made on the Industrial Iron line")
        elif recipe_id.endswith("antiprotonic_nucleosynthesizer"):
            steps = recipe.get("steps", [])
            deployments = [step for step in steps if step.get("op") == "deploying"]
            if len(deployments) != 9:
                errors.append("Nucleosynthesizer must retain nine functional assembly stages")
            if any(step.get("machine") != RADIANCE_DEPLOYER for step in deployments):
                errors.append("Nucleosynthesizer uses the wrong deployer family")
            if not steps or steps[-1] != {"op": "pressing", "machine": RADIANCE_PRESS}:
                errors.append("Nucleosynthesizer uses the wrong closing press")
            for required in (
                "mekanism:pellet_antimatter",
                "mekanism:pellet_polonium",
                "ae2:quantum_entangled_singularity",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
            ):
                if required not in text:
                    errors.append(f"Nucleosynthesizer lacks {required}")
        else:
            if recipe.get("type") != "compacting" or recipe.get("machine") != RADIANCE_PRESS:
                errors.append(f"{recipe_id} is not a Refined Radiance compacting batch")
            inputs = recipe.get("inputs", [])
            if not isinstance(inputs, list) or len(inputs) < 5:
                errors.append(f"{recipe_id} lacks a focused physical BOM")
    return {
        "status": "PASS" if not errors else "FAIL",
        "redesigned": len(REDESIGNED_IDS),
        "compacting": 5,
        "deploying": 1,
        "sequenced_assembly": 1,
        "errors": errors,
    }

