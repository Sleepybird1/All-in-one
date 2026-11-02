#!/usr/bin/env python3
"""Resolve the rejected TFMG/Copper electronics primitive recipes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"

REDESIGNED_IDS = frozenset(
    {
        "industrial_colonies:electronics/coated_circuit_board",
        "industrial_colonies:electronics/capacitor",
        "industrial_colonies:electronics/transistor",
        "industrial_colonies:electronics/rotor",
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
        raise KeyError(f"expected rejected electronics recipe is missing: {recipe_id}")
    recipe = data["recipes"][indexes[recipe_id]]
    for field in _PROCESS_FIELDS:
        recipe.pop(field, None)
    recipe.update(deepcopy(process))


def _deploy(ingredient: str) -> Recipe:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": COPPER_DEPLOYER,
    }


def _press() -> Recipe:
    return {"op": "pressing", "machine": COPPER_PRESS}


def _sequence(
    *,
    comment: str,
    input_item: str,
    transitional: str,
    ingredients: list[str],
    output: str | None = None,
    outputs: list[Recipe] | None = None,
    loops: int = 1,
) -> Recipe:
    process: Recipe = {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional,
        "steps": [*(_deploy(item) for item in ingredients), _press()],
        "loops": loops,
        "exclusive_output": True,
    }
    if output is not None:
        process["output"] = output
    if outputs is not None:
        process["outputs"] = outputs
    return process


def apply(data: dict[str, Any]) -> None:
    designs = {
        "industrial_colonies:electronics/coated_circuit_board": _sequence(
            comment=(
                "Laminate a blank TFMG board with plastic dielectric, a gold contact "
                "plane, and copper edge traces before the Copper press seals the coating"
            ),
            input_item="tfmg:empty_circuit_board",
            transitional="tfmg:empty_circuit_board",
            ingredients=[
                "tfmg:plastic_sheet",
                "create:golden_sheet",
                "tfmg:copper_wire",
            ],
            output="tfmg:coated_circuit_board",
        ),
        "industrial_colonies:electronics/capacitor": _sequence(
            comment=(
                "Stack aluminum foil around a paper dielectric inside a plastic carrier, "
                "attach copper leads, then Copper-press a balanced batch of four capacitors"
            ),
            input_item="tfmg:plastic_sheet",
            transitional="tfmg:unfinished_capacitor",
            ingredients=[
                "tfmg:aluminum_sheet",
                "minecraft:paper",
                "tfmg:aluminum_sheet",
                "tfmg:copper_wire",
            ],
            outputs=[{"kind": "ITEM", "id": "tfmg:capacitor_item", "count": 4}],
        ),
        "industrial_colonies:electronics/transistor": _sequence(
            comment=(
                "Package one complementary N/P semiconductor junction with copper leads "
                "and a redstone gate inside a plastic carrier, then press four transistors"
            ),
            input_item="tfmg:plastic_sheet",
            transitional="tfmg:unfinished_transistor",
            ingredients=[
                "tfmg:copper_wire",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "minecraft:redstone",
            ],
            outputs=[{"kind": "ITEM", "id": "tfmg:transistor_item", "count": 4}],
        ),
        "industrial_colonies:electronics/rotor": _sequence(
            comment=(
                "Build two balanced electromechanical layers around the shaft: aluminum "
                "end plates, copper windings, an electromagnetic coil, laminated magnetic "
                "steel, and keyed screws, each layer sealed by the Copper press"
            ),
            input_item="create:shaft",
            transitional="create:shaft",
            ingredients=[
                "tfmg:aluminum_sheet",
                "tfmg:copper_wire",
                "tfmg:electromagnetic_coil",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:screw",
            ],
            output="tfmg:rotor",
            loops=2,
        ),
    }
    for recipe_id, process in designs.items():
        _replace(data, recipe_id, process)
    audit(data)


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    errors: list[str] = []
    if missing:
        errors.append(f"missing electronics redesigns: {missing}")
    recipes = data.get("recipes", [])
    for recipe_id in sorted(REDESIGNED_IDS.intersection(indexes)):
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not sequenced assembly")
        machines = {
            step.get("machine")
            for step in recipe.get("steps", [])
            if isinstance(step, dict) and step.get("machine")
        }
        if machines != {COPPER_DEPLOYER, COPPER_PRESS}:
            errors.append(f"{recipe_id} escapes the Copper electronics line")
        if not recipe.get("steps") or recipe["steps"][-1] != _press():
            errors.append(f"{recipe_id} does not finish with Copper pressing")
    capacitor = recipes[indexes["industrial_colonies:electronics/capacitor"]]
    transistor = recipes[indexes["industrial_colonies:electronics/transistor"]]
    if capacitor.get("outputs") != [
        {"kind": "ITEM", "id": "tfmg:capacitor_item", "count": 4}
    ]:
        errors.append("capacitor batch is not four")
    if transistor.get("outputs") != [
        {"kind": "ITEM", "id": "tfmg:transistor_item", "count": 4}
    ]:
        errors.append("transistor batch is not four")
    semiconductor_steps = [
        step.get("ingredient")
        for step in transistor.get("steps", [])
        if isinstance(step, dict)
        and str(step.get("ingredient", "")).endswith("_semiconductor")
    ]
    if semiconductor_steps != ["tfmg:n_semiconductor", "tfmg:p_semiconductor"]:
        errors.append("transistor does not use exactly one complementary semiconductor pair")
    rotor = recipes[indexes["industrial_colonies:electronics/rotor"]]
    if rotor.get("loops") != 2 or "tfmg:copper_wire" not in repr(rotor):
        errors.append("rotor lacks its two-layer copper winding")
    if errors:
        raise ValueError("Electronics primitive redesign audit failed: " + " | ".join(errors))
    return {"status": "PASS", "redesigned": len(REDESIGNED_IDS)}

