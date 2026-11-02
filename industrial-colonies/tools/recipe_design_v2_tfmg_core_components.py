"""Lock TFMG's core manufactured parts to their intended factory lines.

The stock Heavy Plate and Steel Mechanism designs are already strong.  This
module preserves their material logic and ratios while assigning the Brass
precision line that bootstraps Railway tooling.  It also turns the extremely
cheap heavy-casing application and handheld multimeter craft into recognizable
structural and electrical assemblies.  Stock recipes that already express a real process
(winding, polarizing, vat chemistry, casting, and the industrial machines
themselves) are deliberately left alone.

Importing this module has no filesystem side effects.  ``apply`` is
idempotent and mutates only the supplied seed dictionary.
"""

from __future__ import annotations

import re
from typing import Any


RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    if isinstance(value, dict):
        identifier = value.get("id")
        return identifier if isinstance(identifier, str) else None
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(1) if match else value.strip()


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _sequence(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    input_item: str,
    transitional: str,
    output: str,
    steps: list[dict[str, str]],
    remove: list[str],
    loops: int = 1,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional,
        "output": output,
        "loops": loops,
        "steps": steps,
        "remove": remove,
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = depends_on
    return recipe


def _recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            "industrial_colonies:tfmg_core/heavy_plate",
            phase="Steel & Petroleum",
            node="CR01 — The Steel Age",
            order=10,
            comment=(
                "Forge one steel ingot through three reductions on the proven "
                "Brass precision press; this bootstraps the Heavy Plate needed "
                "to construct the later Railway heavy-industrial line"
            ),
            input_item="#c:ingots/steel",
            transitional="tfmg:unprocessed_heavy_plate",
            output="tfmg:heavy_plate",
            steps=[
                _press(BRASS_PRESS),
                _press(BRASS_PRESS),
                _press(BRASS_PRESS),
            ],
            remove=["tfmg:sequenced_assembly/heavy_plate"],
        ),
        _sequence(
            "industrial_colonies:tfmg_core/steel_mechanism",
            phase="Steel & Petroleum",
            node="CR01 — The Steel Age",
            order=20,
            comment=(
                "Build TFMG's serviceable Steel Mechanism over two matching "
                "Brass precision-line passes of gears, nickel bearing plate, "
                "lead backing, screws, and the reusable screwdriver; this is "
                "the second bootstrap component for Railway machinery"
            ),
            input_item="tfmg:heavy_plate",
            transitional="tfmg:unfinished_steel_mechanism",
            output="tfmg:steel_mechanism",
            loops=2,
            steps=[
                _deploy("tfmg:steel_cogwheel", BRASS_DEPLOYER),
                _deploy("tfmg:nickel_sheet", BRASS_DEPLOYER),
                _deploy("tfmg:large_steel_cogwheel", BRASS_DEPLOYER),
                _deploy("tfmg:lead_sheet", BRASS_DEPLOYER),
                _deploy("tfmg:screw", BRASS_DEPLOYER),
                _deploy("tfmg:screwdriver", BRASS_DEPLOYER),
            ],
            remove=["tfmg:sequenced_assembly/steel_mechanism"],
            depends_on=["industrial_colonies:tfmg_core/heavy_plate"],
        ),
        _sequence(
            "industrial_colonies:tfmg_core/heavy_machinery_casing",
            phase="Steel & Petroleum",
            node="CR01 — The Steel Age",
            order=30,
            comment=(
                "Reinforce a serviceable Steel Casing with paired Heavy Plates, "
                "internal rebar, and bolted closure instead of applying one "
                "ordinary steel plate by hand"
            ),
            input_item="tfmg:steel_casing",
            transitional="tfmg:steel_casing",
            output="tfmg:heavy_machinery_casing",
            steps=[
                _deploy("2x tfmg:heavy_plate", RAILWAY_DEPLOYER),
                _deploy("tfmg:rebar", RAILWAY_DEPLOYER),
                _deploy("2x tfmg:screw", RAILWAY_DEPLOYER),
                _press(RAILWAY_PRESS),
            ],
            remove=["tfmg:item_application/heavy_machinery_casing"],
            depends_on=["industrial_colonies:tfmg_core/heavy_plate"],
        ),
        _sequence(
            "industrial_colonies:tfmg_core/multimeter",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=40,
            comment=(
                "Turn the analog Voltmeter into a real diagnostic instrument "
                "with a TFMG board, resistor, transistor, capacitor, insulated "
                "test lead, and protected display on the Copper electronics line"
            ),
            input_item="tfmg:voltmeter",
            transitional="tfmg:voltmeter",
            output="tfmg:multimeter",
            steps=[
                _deploy("tfmg:circuit_board", COPPER_DEPLOYER),
                _deploy("tfmg:resistor", COPPER_DEPLOYER),
                _deploy("tfmg:transistor_item", COPPER_DEPLOYER),
                _deploy("tfmg:capacitor_item", COPPER_DEPLOYER),
                _deploy("tfmg:copper_wire", COPPER_DEPLOYER),
                _deploy("minecraft:glass_pane", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
            remove=["tfmg:crafting/materials/multimeter"],
            depends_on=[
                "industrial_colonies:electronics/capacitor",
                "industrial_colonies:electronics/transistor",
                "industrial_colonies:electronics/circuit_board",
            ],
        ),
    ]


def _assert_unclaimed(data: dict[str, Any], additions: list[dict[str, Any]]) -> None:
    addition_ids = {recipe["id"] for recipe in additions}
    wanted_outputs = {
        _item_id(recipe["output"]): recipe["id"]
        for recipe in additions
        if _item_id(recipe.get("output")) is not None
    }
    wanted_removals = {
        removal: recipe["id"]
        for recipe in additions
        for removal in recipe.get("remove", [])
    }

    for existing in data.get("recipes", []):
        if existing.get("id") in addition_ids:
            continue
        output = _item_id(existing.get("output"))
        if output in wanted_outputs:
            raise ValueError(
                f"{wanted_outputs[output]} cannot claim {output}; "
                f"it is already managed by {existing.get('id')}"
            )
        for field in ("outputs", "results"):
            for result in existing.get(field, []):
                output = _item_id(result)
                if output in wanted_outputs:
                    raise ValueError(
                        f"{wanted_outputs[output]} cannot claim {output}; "
                        f"it is already managed by {existing.get('id')}"
                    )
        for removal in existing.get("remove", []):
            if removal in wanted_removals:
                raise ValueError(
                    f"{wanted_removals[removal]} cannot remove {removal}; "
                    f"it is already owned by {existing.get('id')}"
                )

    additional_removals = set(data.get("additional_removals", []))
    overlap = sorted(additional_removals.intersection(wanted_removals))
    if overlap:
        raise ValueError(f"TFMG core removals are already globally claimed: {overlap}")

    preserved = set(data.get("preserve_recipe_ids", []))
    overlap = sorted(preserved.intersection(wanted_removals))
    if overlap:
        raise ValueError(f"TFMG core coverage cannot remove preserved recipes: {overlap}")


def _upsert(data: dict[str, Any], recipe: dict[str, Any]) -> None:
    matches = [
        index
        for index, existing in enumerate(data["recipes"])
        if existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"Managed recipe is duplicated: {recipe['id']}")
    if matches:
        data["recipes"][matches[0]] = recipe
    else:
        data["recipes"].append(recipe)


def apply(data: dict[str, Any]) -> None:
    """Apply the curated TFMG core-component routes in memory."""

    additions = _recipes()
    _assert_unclaimed(data, additions)
    for recipe in additions:
        _upsert(data, recipe)
