"""Curated ComputerCraft and colony-network manufacturing coverage.

The base CC computers, monitors, turtles, modems, printer, disk drive, speaker,
and relay are already owned by the main recipe redesign.  This wave covers the
remaining functional network/storage devices and the useful Advanced
Peripherals/Colony4CC integrations without claiming decorative variants.

Two installed items are deliberately left alone:

* ``advancedperipherals:computer_tool`` describes itself as a currently useless
  wrench in the installed language file.
* ``advancedperipherals:rs_bridge`` has no usable backend because Refined
  Storage is not installed in this pack.

The special ``computercraft:disk`` recipe is also preserved because it is the
state-aware disk recolouring/reset recipe.  Only the sixteen paper-and-dye disk
manufacturing shortcuts are replaced.  Colony4CC's two MineColonies crafter
recipes for RGB charges remain valid alternatives so their colony research
still matters; the managed sequence is a bulk industrial route, not a bypass
that deletes the colony path.

``apply`` is idempotent and mutates only the supplied seed dictionary.  Importing
this module has no filesystem or runtime side effects.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


Recipe = dict[str, Any]

COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    recipe_id: str,
    phase: str,
    node: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    remove: Iterable[str] = (),
    deployer: str = BRASS_DEPLOYER,
    press: str = BRASS_PRESS,
    allow_stock_alternative: bool = False,
) -> Recipe:
    removals = list(remove)
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
        "loops": 1,
        "steps": [_deploy(item, deployer) for item in ingredients]
        + [_press(press)],
        "remove": removals,
    }
    if removals:
        recipe["exclusive_output"] = True
    if allow_stock_alternative:
        recipe["allow_stock_alternative"] = True
    return recipe


def _mechanical(
    *,
    recipe_id: str,
    phase: str,
    node: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    remove: Iterable[str],
) -> Recipe:
    removals = list(remove)
    return {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": removals,
        "exclusive_output": True,
    }


def _computercraft_storage_recipes() -> list[Recipe]:
    return [
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/magnetic_floppy_batch",
            phase="Digital Logistics",
            node="CR01 — Early Electronics",
            order=70,
            comment=(
                "Laminate paper around a magnetic recording sheet, copper data "
                "traces, and a small TFMG controller to manufacture two reusable "
                "floppy disks; CC's state-aware recolouring recipe remains intact"
            ),
            input_item="minecraft:paper",
            output="2x computercraft:disk",
            ingredients=[
                "tfmg:magnetic_alloy_sheet",
                "tfmg:copper_wire",
                "tfmg:circuit_board",
                "create:copper_sheet",
            ],
            remove=[f"computercraft:disk_{index}" for index in range(1, 17)],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
    ]


def _colony_network_recipes() -> list[Recipe]:
    return [
        _mechanical(
            recipe_id="industrial_colonies:computer_network_coverage/colony_peripheral",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=260,
            comment=(
                "Lay out the colony banner, clipboard, resource ledger, build "
                "instrument, dual control boards, and a full wired modem as an "
                "actual colony operations console"
            ),
            pattern=[
                "BCS",
                "RMR",
                " T ",
            ],
            key={
                "B": "minecolonies:colony_banner",
                "C": "minecolonies:clipboard",
                "S": "minecolonies:resourcescroll",
                "R": "tfmg:circuit_board",
                "M": "computercraft:wired_modem_full",
                "T": "structurize:sceptergold",
            },
            output="colony4cc:colony_peripheral",
            remove=["colony4cc:colony_peripheral"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/colony_wireless_normal",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=261,
            comment=(
                "Convert the wired colony console into a field upgrade by fitting "
                "the normal radio, an insulated antenna lead, rechargeable lithium "
                "power, and the adhesive interface used by pocket computers"
            ),
            input_item="colony4cc:colony_peripheral",
            output="colony4cc:colony_wireless_normal",
            ingredients=[
                "computercraft:wireless_modem_normal",
                "tfmg:copper_wire",
                "tfmg:lithium_charge",
                "#c:slime_balls",
            ],
            remove=["colony4cc:colony_wireless_normal"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/colony_wireless_advanced",
            phase="High-Energy Grid",
            node="CR01 — Advanced Perhipherals",
            order=65,
            comment=(
                "Retune the colonial field upgrade for ender-range service with an "
                "advanced modem, fluix coupling pearl, large radio coil, calculation "
                "control, and a fresh bonded pocket interface"
            ),
            input_item="colony4cc:colony_wireless_normal",
            output="colony4cc:colony_wireless_advanced",
            ingredients=[
                "computercraft:wireless_modem_advanced",
                "ae2:fluix_pearl",
                "tfmg:large_coil",
                "ae2:calculation_processor",
                "#c:slime_balls",
            ],
            remove=["colony4cc:colony_wireless_advanced"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/rgb_hologram_charge_batch",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=262,
            comment=(
                "Build eight rechargeable hologram charges by layering red, green, "
                "and blue emitters over glowstone, then adding switching powder and "
                "a TFMG capacitor; MineColonies crafter routes remain available"
            ),
            input_item="minecraft:glowstone_dust",
            output="8x colony4cc:rgb_charge",
            ingredients=[
                "minecraft:red_dye",
                "minecraft:green_dye",
                "minecraft:blue_dye",
                "minecraft:redstone",
                "tfmg:capacitor_item",
            ],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
            allow_stock_alternative=True,
        ),
    ]


def _advanced_peripheral_recipes() -> list[Recipe]:
    node = "CR01 — Advanced Perhipherals"
    phase = "High-Energy Grid"
    return [
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/chat_box",
            phase=phase,
            node=node,
            order=70,
            comment=(
                "Turn the shared peripheral chassis into a bidirectional chat "
                "terminal with an acoustic transducer, local radio, display link, "
                "and a dedicated message-control board"
            ),
            input_item="advancedperipherals:peripheral_casing",
            output="advancedperipherals:chat_box",
            ingredients=[
                "computercraft:speaker",
                "computercraft:wireless_modem_normal",
                "create:display_link",
                "tfmg:circuit_board",
                "create:golden_sheet",
            ],
            remove=["advancedperipherals:chat_box"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/environment_detector",
            phase=phase,
            node=node,
            order=80,
            comment=(
                "Instrument the common peripheral chassis with daylight, time, "
                "heading, vibration, and block-state sensors so one programmed unit "
                "can report the surrounding environment"
            ),
            input_item="advancedperipherals:peripheral_casing",
            output="advancedperipherals:environment_detector",
            ingredients=[
                "minecraft:daylight_detector",
                "minecraft:clock",
                "minecraft:compass",
                "minecraft:sculk_sensor",
                "create:content_observer",
            ],
            remove=["advancedperipherals:environment_detector"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/geo_scanner",
            phase=phase,
            node=node,
            order=90,
            comment=(
                "Build a subsurface scanner around a driven probe, compass stage, "
                "magnetic excitation coil, certus transducer, and smart return sensor"
            ),
            input_item="advancedperipherals:peripheral_casing",
            output="advancedperipherals:geo_scanner",
            ingredients=[
                "create:mechanical_drill",
                "minecraft:compass",
                "tfmg:large_coil",
                "ae2:certus_quartz_crystal",
                "create:content_observer",
            ],
            remove=["advancedperipherals:geo_scanner"],
        ),
        _mechanical(
            recipe_id="industrial_colonies:computer_network_coverage/memory_card",
            phase=phase,
            node=node,
            order=100,
            comment=(
                "Form a slim credential card around a real 1k memory component, "
                "paired TFMG control boards, gold contacts, and a copper backplate"
            ),
            pattern=[
                " G ",
                "CMC",
                " P ",
            ],
            key={
                "G": "create:golden_sheet",
                "C": "tfmg:circuit_board",
                "M": "ae2:cell_component_1k",
                "P": "create:copper_sheet",
            },
            output="advancedperipherals:memory_card",
            remove=["advancedperipherals:memory_card"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/nbt_storage",
            phase=phase,
            node=node,
            order=110,
            comment=(
                "Convert a peripheral chassis into structured-data storage with "
                "paired identity cards, a 1k memory bank, calculation logic, and a "
                "full wired network interface"
            ),
            input_item="advancedperipherals:peripheral_casing",
            output="advancedperipherals:nbt_storage",
            ingredients=[
                "2x advancedperipherals:memory_card",
                "ae2:cell_component_1k",
                "ae2:calculation_processor",
                "computercraft:wired_modem_full",
                "tfmg:capacitor_item",
            ],
            remove=["advancedperipherals:nbt_storage"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/player_detector",
            phase=phase,
            node=node,
            order=120,
            comment=(
                "Calibrate a presence array from a sculk pickup, echo reference, "
                "ender locator, compass stage, and wired telemetry interface"
            ),
            input_item="advancedperipherals:peripheral_casing",
            output="advancedperipherals:player_detector",
            ingredients=[
                "minecraft:sculk_sensor",
                "minecraft:echo_shard",
                "minecraft:ender_eye",
                "minecraft:compass",
                "computercraft:wired_modem_full",
            ],
            remove=["advancedperipherals:player_detector"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/weak_automata_core",
            phase=phase,
            node=node,
            order=130,
            comment=(
                "Assemble the first turtle automata core from a mechanical arm, "
                "electric drive, soul lantern, brewing interface, controller board, "
                "and precision motion package"
            ),
            input_item="advancedperipherals:peripheral_casing",
            output="advancedperipherals:weak_automata_core",
            ingredients=[
                "create:mechanical_arm",
                "tfmg:electric_motor",
                "minecraft:soul_lantern",
                "minecraft:brewing_stand",
                "tfmg:circuit_board",
                "create:precision_mechanism",
            ],
            remove=["advancedperipherals:weak_automata_core"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/overpowered_weak_automata_core",
            phase=phase,
            node=node,
            order=140,
            comment=(
                "Reinforce the weak automata core around a nether-star power source "
                "with stress scheduling, magnetic shielding, local capacitance, and "
                "a precision actuator governor"
            ),
            input_item="advancedperipherals:weak_automata_core",
            output="advancedperipherals:overpowered_weak_automata_core",
            ingredients=[
                "minecraft:nether_star",
                "appliedcreate:advanced_stress_processor",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:capacitor_item",
                "create:precision_mechanism",
            ],
            remove=["advancedperipherals:overpowered_weak_automata_core"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/overpowered_husbandry_automata_core",
            phase=phase,
            node=node,
            order=150,
            comment=(
                "Upgrade the earned husbandry core with star power, a gentle "
                "mechanical manipulator, electric drive, feed recognizer, biological "
                "control board, and a buffered actuator supply"
            ),
            input_item="advancedperipherals:husbandry_automata_core",
            output="advancedperipherals:overpowered_husbandry_automata_core",
            ingredients=[
                "minecraft:nether_star",
                "create:mechanical_arm",
                "tfmg:electric_motor",
                "minecraft:golden_carrot",
                "tfmg:circuit_board",
                "tfmg:capacitor_item",
            ],
            remove=["advancedperipherals:overpowered_husbandry_automata_core"],
        ),
        _sequence(
            recipe_id="industrial_colonies:computer_network_coverage/overpowered_end_automata_core",
            phase=phase,
            node=node,
            order=160,
            comment=(
                "Upgrade the earned end automata core with star power, an ender-range "
                "modem, paired locator optics, fluix coupling, a tuned radio coil, and "
                "stress-stable teleport control"
            ),
            input_item="advancedperipherals:end_automata_core",
            output="advancedperipherals:overpowered_end_automata_core",
            ingredients=[
                "minecraft:nether_star",
                "computercraft:wireless_modem_advanced",
                "minecraft:ender_eye",
                "ae2:fluix_pearl",
                "tfmg:large_coil",
                "appliedcreate:advanced_stress_processor",
            ],
            remove=["advancedperipherals:overpowered_end_automata_core"],
        ),
    ]


def _output_item(output: Any) -> str | None:
    if isinstance(output, dict):
        identifier = output.get("id") or output.get("item")
        return identifier if isinstance(identifier, str) and ":" in identifier else None
    if not isinstance(output, str):
        return None
    value = output.strip()
    if "x " in value and value.split("x ", 1)[0].isdigit():
        value = value.split("x ", 1)[1]
    return value if ":" in value else None


def _recipe_set() -> list[Recipe]:
    recipes = [
        *_computercraft_storage_recipes(),
        *_colony_network_recipes(),
        *_advanced_peripheral_recipes(),
    ]
    ids = [recipe["id"] for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise ValueError("computer/network coverage defines duplicate recipe IDs")

    outputs = [_output_item(recipe.get("output")) for recipe in recipes]
    if None in outputs or len(outputs) != len(set(outputs)):
        raise ValueError("computer/network coverage defines invalid or duplicate outputs")

    removals = [
        stock_id for recipe in recipes for stock_id in recipe.get("remove", [])
    ]
    if len(removals) != len(set(removals)):
        raise ValueError("computer/network coverage claims a stock recipe twice")
    return recipes


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed seed field {field!r} must be a list")
    return value


def _assert_unclaimed(data: dict[str, Any], recipes: Iterable[Recipe]) -> None:
    recipes = list(recipes)
    managed_ids = {recipe["id"] for recipe in recipes}
    outputs = {_output_item(recipe.get("output")) for recipe in recipes}
    outputs.discard(None)
    removals = {
        stock_id for recipe in recipes for stock_id in recipe.get("remove", [])
    }

    for existing in _require_list(data, "recipes"):
        if not isinstance(existing, dict):
            raise TypeError("managed recipe entries must be objects")
        if existing.get("id") in managed_ids:
            continue
        existing_output = _output_item(existing.get("output"))
        if existing_output in outputs:
            raise ValueError(
                f"computer/network output {existing_output} is already managed by "
                f"{existing.get('id')}"
            )
        overlap = removals.intersection(existing.get("remove", []))
        if overlap:
            raise ValueError(
                "computer/network stock IDs are already claimed by "
                f"{existing.get('id')}: {sorted(overlap)}"
            )


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = _require_list(data, "recipes")
    matches = [
        index
        for index, existing in enumerate(recipes)
        if isinstance(existing, dict) and existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"duplicate managed recipe before upsert: {recipe['id']}")
    if matches:
        recipes[matches[0]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def apply(data: dict[str, Any]) -> None:
    """Add the audited computer/network coverage wave to ``data`` in place."""

    recipes = _recipe_set()
    _assert_unclaimed(data, recipes)

    claimed_stock_ids = {
        stock_id for recipe in recipes for stock_id in recipe.get("remove", [])
    }
    additional_removals = _require_list(data, "additional_removals")
    additional_removals[:] = [
        recipe_id
        for recipe_id in additional_removals
        if recipe_id not in claimed_stock_ids
    ]
    preserve_recipe_ids = _require_list(data, "preserve_recipe_ids")
    preserve_recipe_ids[:] = [
        recipe_id
        for recipe_id in preserve_recipe_ids
        if recipe_id not in claimed_stock_ids
    ]

    exclude_outputs = _require_list(data, "exclude_outputs")
    managed_outputs = {
        output
        for recipe in recipes
        if (output := _output_item(recipe.get("output"))) is not None
    }
    exclude_outputs[:] = [
        output for output in exclude_outputs if output not in managed_outputs
    ]

    for recipe in recipes:
        _upsert(data, recipe)
