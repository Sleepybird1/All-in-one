#!/usr/bin/env python3
"""Manufacturing-process redesign for the remaining ComputerCraft devices.

The network cable, modem, speaker, relay, and advanced upgrade recipes already
express their function and were explicitly liked by the user, so this wave does
not rewrite them.  It replaces the remaining direct 3x3 device grids with
lamination or staged assembly:

* Copper compacting laminates display and credential-card electronics;
* Brass assembly manufactures computers, media hardware, and printers;
* Railway assembly builds the mobile Turtle as a genuine factory robot.

The recipes use semiconductors and capacitors where they represent actual logic
electronics, but do not paste the same expensive border around every device.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

COPPER_PRESS = "createcasing:copper_press"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    recipe_id: str,
    order: int,
    comment: str,
    input_item: str,
    ingredients: list[str],
    deployer: str,
    press: str,
    output: str,
    stock_id: str,
    depends_on: list[str] | None = None,
) -> Recipe:
    recipe: Recipe = {
        "id": recipe_id,
        "phase": "Digital Logistics",
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": 1,
        "steps": [_deploy(item, deployer) for item in ingredients]
        + [_press(press)],
        "remove": [stock_id],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _recipes() -> list[Recipe]:
    return [
        _sequence(
            recipe_id="industrial_colonies:computercraft/computer/normal",
            order=43,
            comment=(
                "Populate a TFMG board with complementary semiconductors, a "
                "capacitor bank, real logic, display control, insulated wiring, "
                "and a Brass chassis before the computer is closed and pressed."
            ),
            input_item="tfmg:circuit_board",
            ingredients=[
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:capacitor_item",
                "ae2:logic_processor",
                "create:display_board",
                "tfmg:copper_wire",
                "tfmg:plastic_sheet",
                "create:brass_casing",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            output="computercraft:computer_normal",
            stock_id="computercraft:computer_normal",
        ),
        {
            "id": "industrial_colonies:computercraft/monitor/normal",
            "phase": "Digital Logistics",
            "order": 44,
            "type": "compacting",
            "comment": (
                "Laminate two monitor panels from rose-quartz pixels, paired "
                "display drivers, a shared copper signal harness, plastic backing, "
                "and a thin Brass frame."
            ),
            "machine": COPPER_PRESS,
            "inputs": [
                "3x create:polished_rose_quartz",
                "2x create:display_board",
                "tfmg:copper_wire",
                "2x tfmg:plastic_sheet",
                "2x create:brass_sheet",
            ],
            "output": {
                "kind": "ITEM",
                "id": "computercraft:monitor_normal",
                "count": 2,
            },
            "remove": ["computercraft:monitor_normal"],
            "exclusive_output": True,
        },
        _sequence(
            recipe_id="industrial_colonies:computercraft/io/disk_drive",
            order=45,
            comment=(
                "Turn a Depot into a removable-media drive by installing its "
                "motorized spindle, iron head rails, media logic, copper harness, "
                "plastic isolation, and Brass enclosure."
            ),
            input_item="create:depot",
            ingredients=[
                "tfmg:electric_motor",
                "2x create:iron_sheet",
                "tfmg:circuit_board",
                "ae2:logic_processor",
                "tfmg:copper_wire",
                "tfmg:plastic_sheet",
                "create:brass_casing",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            output="computercraft:disk_drive",
            stock_id="computercraft:disk_drive",
            depends_on=["industrial_colonies:computercraft/computer/normal"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computercraft/io/printer",
            order=46,
            comment=(
                "Fit a Depot with a piston-driven print carriage, ink feed, "
                "dedicated control board, display driver, wiring, and a washable "
                "plastic-lined Brass shell."
            ),
            input_item="create:depot",
            ingredients=[
                "create:mechanical_piston",
                "minecraft:ink_sac",
                "tfmg:circuit_board",
                "create:display_board",
                "tfmg:copper_wire",
                "tfmg:plastic_sheet",
                "create:brass_casing",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            output="computercraft:printer",
            stock_id="computercraft:printer",
        ),
        _sequence(
            recipe_id="industrial_colonies:computercraft/mobile/pocket_computer",
            order=49,
            comment=(
                "Miniaturize the manufactured desktop around a matched monitor, "
                "wireless modem, etched interposer, lithium reserve, vibrant-glass "
                "screen, plastic insulation, and gold cladding."
            ),
            input_item="computercraft:computer_normal",
            ingredients=[
                "computercraft:monitor_normal",
                "computercraft:wireless_modem_normal",
                "tfmg:etched_circuit_board",
                "tfmg:lithium_charge",
                "ae2:quartz_vibrant_glass",
                "tfmg:plastic_sheet",
                "2x create:golden_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            output="computercraft:pocket_computer_normal",
            stock_id="computercraft:pocket_computer_normal",
            depends_on=[
                "industrial_colonies:computercraft/computer/normal",
                "industrial_colonies:computercraft/monitor/normal",
                "industrial_colonies:computercraft/network/wireless_modem",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:computercraft/mobile/turtle",
            order=50,
            comment=(
                "Build the Turtle as a Railway-line factory robot: a manufactured "
                "computer receives a cargo bay, articulated tool arm, twin electric "
                "drives, stress controller, steel transmission, and armored shell."
            ),
            input_item="computercraft:computer_normal",
            ingredients=[
                "minecraft:barrel",
                "create:deployer",
                "2x tfmg:electric_motor",
                "appliedcreate:stress_processor",
                "tfmg:steel_mechanism",
                "create:brass_casing",
                "2x tfmg:plastic_sheet",
            ],
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
            output="computercraft:turtle_normal",
            stock_id="computercraft:turtle_normal",
            depends_on=["industrial_colonies:computercraft/computer/normal"],
        ),
        {
            "id": "industrial_colonies:computer_network_coverage/memory_card",
            "phase": "High-Energy Grid",
            "order": 100,
            "type": "compacting",
            "comment": (
                "Laminate two reusable credential cards from a real 1k memory "
                "component, etched controller, gold contacts, magnetic backing, "
                "and plastic insulation on the Railway electronics press."
            ),
            "machine": RAILWAY_PRESS,
            "inputs": [
                "ae2:cell_component_1k",
                "tfmg:etched_circuit_board",
                "2x create:golden_sheet",
                "tfmg:magnetic_alloy_sheet",
                "2x tfmg:plastic_sheet",
            ],
            "output": {
                "kind": "ITEM",
                "id": "advancedperipherals:memory_card",
                "count": 2,
            },
            "remove": ["advancedperipherals:memory_card"],
            "exclusive_output": True,
        },
    ]


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed seed field {field!r} must be a list")
    return value


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = _require_list(data, "recipes")
    matches = [
        index
        for index, existing in enumerate(recipes)
        if isinstance(existing, dict) and existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"duplicate managed recipe before v3 upsert: {recipe['id']}")
    if matches:
        recipes[matches[0]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def apply(data: dict[str, Any]) -> None:
    """Replace direct device grids while preserving the approved network line."""

    recipes = _recipes()
    claimed = {
        str(stock)
        for recipe in recipes
        for stock in recipe.get("remove", [])
    }
    additional = _require_list(data, "additional_removals")
    additional[:] = [stock for stock in additional if str(stock) not in claimed]
    preserved = _require_list(data, "preserve_recipe_ids")
    preserved[:] = [stock for stock in preserved if str(stock) not in claimed]
    for recipe in recipes:
        _upsert(data, recipe)
