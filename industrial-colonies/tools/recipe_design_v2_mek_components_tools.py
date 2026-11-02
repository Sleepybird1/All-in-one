#!/usr/bin/env python3
"""Curated Mekanism component, tank, augment, and personal-tool routes.

This wave fills functional gaps around the already-authored Mekanism machine
chain.  It deliberately does not claim the user-owned Energy Tablet, any direct
upgraded factory, cosmetic gear, creative item, or module-installation recipe.

The manufacturing language follows the pack's casing roles:

* Brass builds compact module substrates.
* Industrial Iron builds Mekanism electrochemistry, sealed tanks, and augments.
* Weathered Iron aligns atomic, teleportation, and armored personal equipment.
* Wearable tools use compact 4x4 silhouettes rather than ingredient rings.

``apply`` is a pure, idempotent in-memory transform.  It performs no catalog
scan, file write, generation, deployment, or runtime action.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Iterable


Recipe = dict[str, Any]


BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
INDUSTRIAL_DEPLOYER = "createcasing:industrial_iron_deployer"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"
WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    recipe_id: str,
    node: str,
    phase: str,
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
    depends_on: list[str] | None = None,
) -> Recipe:
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": list(inputs),
        "output": output,
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
    if not pattern or len(pattern) > 4:
        raise ValueError(f"personal-equipment grid must be 3x3 or 4x4: {recipe_id}")
    width = len(pattern[0])
    if width not in {3, 4} or len(pattern) not in {3, 4}:
        raise ValueError(f"personal-equipment grid must be 3x3 or 4x4: {recipe_id}")
    if any(len(row) != width for row in pattern):
        raise ValueError(f"non-rectangular personal-equipment grid: {recipe_id}")
    used = set("".join(pattern)) - {" "}
    if used != set(key):
        raise ValueError(
            f"grid symbols do not match key for {recipe_id}: "
            f"used={sorted(used)}, key={sorted(key)}"
        )
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": list(pattern),
        "key": dict(key),
        "output": output,
        "remove": [stock_id],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _recipes() -> list[Recipe]:
    recipes = [
        # Compact electronics and electrochemical cores.
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/module_base",
            node="CR01 — Modular Machinery",
            phase="Mekanized Industry",
            order=600,
            comment=(
                "Laminate two reusable module substrates from HDPE, an etched TFMG "
                "backplane, osmium contacts, magnetic shielding, and a lithium buffer."
            ),
            input_item="mekanism:hdpe_sheet",
            ingredients=[
                "tfmg:etched_circuit_board",
                "mekanism:ingot_osmium",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:lithium_charge",
                "mekanism:alloy_infused",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            output="2x mekanism:module_base",
            stock_id="mekanism:module_base",
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/electrolytic_core",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=330,
            comment=(
                "Build an electrolytic stack on an osmium powder bed with iron and "
                "gold electrodes, infused separators, a magnetic coil, and capacitor."
            ),
            input_item="mekanism:dust_osmium",
            ingredients=[
                "mekanism:dust_iron",
                "mekanism:dust_gold",
                "2x mekanism:alloy_infused",
                "tfmg:electromagnetic_coil",
                "tfmg:capacitor_item",
                "tfmg:plastic_sheet",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:electrolytic_core",
            stock_id="mekanism:electrolytic_core",
        ),

        # TFMG vessels become the canonical shells for Mekanism storage.
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/basic_fluid_tank",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=610,
            comment=(
                "Convert a TFMG steel vessel into the basic Mek fluid tank with "
                "osmium reinforcement, rubber seals, a plastic valve, and level control."
            ),
            input_item="tfmg:steel_fluid_tank",
            ingredients=[
                "2x mekanism:ingot_osmium",
                "2x tfmg:rubber_sheet",
                "tfmg:plastic_fluid_valve",
                "mekanism:basic_control_circuit",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:basic_fluid_tank",
            stock_id="mekanism:fluid_tank/basic",
            depends_on=["industrial_colonies:mekanism/basic_control_circuit"],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/basic_chemical_tank",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=620,
            comment=(
                "Refit a TFMG tank for gases and chemicals using osmium armor, a "
                "pressurized-tube manifold, plastic liner, rubber seals, and controller."
            ),
            input_item="tfmg:steel_fluid_tank",
            ingredients=[
                "2x mekanism:ingot_osmium",
                "mekanism:basic_pressurized_tube",
                "2x tfmg:plastic_sheet",
                "2x tfmg:rubber_sheet",
                "mekanism:basic_control_circuit",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:basic_chemical_tank",
            stock_id="mekanism:chemical_tank/basic",
            depends_on=["industrial_colonies:mekanism/basic_control_circuit"],
        ),
        _compacting(
            recipe_id="industrial_colonies:mekanism_components/dynamic_tank_batch",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=630,
            comment=(
                "Pressure-form four modular reservoir sections from one real tank, "
                "heavy plate, steel manifold pipe, osmium ribs, and a rubber gasket."
            ),
            machine=INDUSTRIAL_PRESS,
            inputs=[
                "tfmg:steel_fluid_tank",
                "4x tfmg:heavy_plate",
                "2x tfmg:steel_pipe",
                "2x mekanism:ingot_osmium",
                "tfmg:rubber_sheet",
            ],
            output="4x mekanism:dynamic_tank",
            stock_id="mekanism:dynamic_tank",
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/dynamic_valve_batch",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=640,
            comment=(
                "Split a reservoir section into two controlled service ports with "
                "TFMG valves, an industrial manifold, reinforced seals, and control."
            ),
            input_item="mekanism:dynamic_tank",
            ingredients=[
                "2x tfmg:steel_fluid_valve",
                "tfmg:industrial_pipe",
                "2x tfmg:rubber_sheet",
                "mekanism:advanced_control_circuit",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="2x mekanism:dynamic_valve",
            stock_id="mekanism:dynamic_valve",
            depends_on=[
                "industrial_colonies:mekanism_components/dynamic_tank_batch",
                "industrial_colonies:mekanism/advanced_control_circuit",
            ],
        ),
        _compacting(
            recipe_id="industrial_colonies:mekanism_components/structural_glass_batch",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=650,
            comment=(
                "Bond four framed observation panels with rubber and plastic seals "
                "plus infused-alloy corner locks for pressure-rated multiblocks."
            ),
            machine=INDUSTRIAL_PRESS,
            inputs=[
                "4x minecraft:glass",
                "4x tfmg:steel_frame",
                "4x tfmg:rubber_sheet",
                "2x tfmg:plastic_sheet",
                "2x mekanism:alloy_infused",
            ],
            output="4x mekanism:structural_glass",
            stock_id="mekanism:structural_glass",
        ),

        # Hand tools and paired wearable silhouettes.
        _sequence(
            recipe_id="industrial_colonies:mekanism_tools/configurator",
            node="CR01 — Modular Machinery",
            phase="Mekanized Industry",
            order=660,
            comment=(
                "Turn a steel mechanism into a powered service wand with an osmium "
                "probe, Energy Tablet, basic controller, and insulated grip."
            ),
            input_item="tfmg:steel_mechanism",
            ingredients=[
                "mekanism:ingot_osmium",
                "mekanism:energy_tablet",
                "mekanism:basic_control_circuit",
                "tfmg:rubber_sheet",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:configurator",
            stock_id="mekanism:configurator",
            depends_on=["industrial_colonies:mekanism/basic_control_circuit"],
        ),
        _grid(
            recipe_id="industrial_colonies:mekanism_tools/jetpack",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=670,
            comment=(
                "Build a twin-column pressure pack with chemical tanks, TFMG turbine "
                "thrusters, valves, lithium ignition buffers, and a rubber harness."
            ),
            pattern=["RCCR", "FTTF", "VLLV", "E  E"],
            key={
                "R": "tfmg:rubber_sheet",
                "C": "mekanism:basic_control_circuit",
                "F": "tfmg:steel_frame",
                "T": "mekanism:basic_chemical_tank",
                "V": "tfmg:steel_fluid_valve",
                "L": "tfmg:lithium_charge",
                "E": "tfmg:turbine_engine",
            },
            output="mekanism:jetpack",
            stock_id="mekanism:jetpack",
            depends_on=[
                "industrial_colonies:mekanism_components/basic_chemical_tank",
                "industrial_colonies:mekanism/basic_control_circuit",
                "industrial_colonies:engines/turbine_engine",
            ],
        ),
        _grid(
            recipe_id="industrial_colonies:mekanism_tools/free_runners",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=680,
            comment=(
                "Assemble mirrored powered boots: controller and motor columns over "
                "paired Energy Tablets, lithium buffers, rubber soles, and osmium feet."
            ),
            pattern=["C  C", "M  M", "ELLE", "RORO"],
            key={
                "C": "mekanism:basic_control_circuit",
                "M": "tfmg:electric_motor",
                "E": "mekanism:energy_tablet",
                "L": "tfmg:lithium_charge",
                "R": "tfmg:rubber_sheet",
                "O": "mekanism:ingot_osmium",
            },
            output="mekanism:free_runners",
            stock_id="mekanism:free_runners",
            depends_on=["industrial_colonies:mekanism/basic_control_circuit"],
        ),

        # Functional augments omitted by the first Mekanism coverage wave.
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/upgrade_filter",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=730,
            comment=(
                "Populate a module substrate with a real Create filter, etched logic, "
                "chemical-safe plastic, and an infused actuator."
            ),
            input_item="mekanism:module_base",
            ingredients=[
                "create:filter",
                "tfmg:etched_circuit_board",
                "tfmg:plastic_sheet",
                "mekanism:alloy_infused",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:upgrade_filter",
            stock_id="mekanism:upgrade/filter",
            depends_on=["industrial_colonies:mekanism_components/module_base"],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/upgrade_muffling",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=740,
            comment=(
                "Layer wool, rubber, and plastic acoustic isolation around a module "
                "substrate and lock the cartridge with infused alloy."
            ),
            input_item="mekanism:module_base",
            ingredients=[
                "4x minecraft:white_wool",
                "2x tfmg:rubber_sheet",
                "tfmg:plastic_sheet",
                "mekanism:alloy_infused",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:upgrade_muffling",
            stock_id="mekanism:upgrade/muffling",
            depends_on=["industrial_colonies:mekanism_components/module_base"],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/upgrade_stone_generator",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=750,
            comment=(
                "Build a sealed cobble-generation cartridge with metered water and "
                "lava feeds, refractory separation, plastic housing, and process logic."
            ),
            input_item="mekanism:module_base",
            ingredients=[
                "minecraft:water_bucket",
                "minecraft:lava_bucket",
                "tfmg:fireproof_brick_reinforcement",
                "tfmg:plastic_sheet",
                "mekanism:advanced_control_circuit",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:upgrade_stone_generator",
            stock_id="mekanism:upgrade/stone_generator",
            depends_on=[
                "industrial_colonies:mekanism_components/module_base",
                "industrial_colonies:steelworks/fireproof_brick_reinforcement",
                "industrial_colonies:mekanism/advanced_control_circuit",
            ],
        ),

        # High-energy field hardware and personal equipment.
        _sequence(
            recipe_id="industrial_colonies:mekanism_components/teleportation_core",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=700,
            comment=(
                "Align an Ender Pearl inside doubled atomic and magnetic field shells, "
                "then add an electromagnetic coil, diamond optic, and ultimate control."
            ),
            input_item="minecraft:ender_pearl",
            ingredients=[
                "2x mekanism:alloy_atomic",
                "2x tfmg:magnetic_alloy_sheet",
                "tfmg:electromagnetic_coil",
                "minecraft:diamond",
                "mekanism:ultimate_control_circuit",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            output="mekanism:teleportation_core",
            stock_id="mekanism:teleportation_core",
            depends_on=["industrial_colonies:mekanism/ultimate_control_circuit"],
        ),
        _grid(
            recipe_id="industrial_colonies:mekanism_tools/atomic_disassembler",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=720,
            comment=(
                "Shape a cobalt-and-atomic cutting head above a magnetic drive, "
                "ultimate controller, Energy Tablet, osmium neck, and obsidian grip."
            ),
            pattern=["ACCA", " MUT", "  O ", "  H "],
            key={
                "A": "mekanism:alloy_atomic",
                "C": "modernfoundry:cobalt_ingot",
                "M": "tfmg:electromagnetic_coil",
                "U": "mekanism:ultimate_control_circuit",
                "T": "mekanism:energy_tablet",
                "O": "mekanism:ingot_osmium",
                "H": "mekanism:ingot_refined_obsidian",
            },
            output="mekanism:atomic_disassembler",
            stock_id="mekanism:atomic_disassembler",
            depends_on=["industrial_colonies:mekanism/ultimate_control_circuit"],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_tools/armored_free_runners",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=730,
            comment=(
                "Upgrade the completed runners with cobalt impact shells, heavy plate, "
                "diamond wear faces, atomic bracing, and replaceable rubber soles."
            ),
            input_item="mekanism:free_runners",
            ingredients=[
                "2x modernfoundry:cobalt_ingot",
                "2x tfmg:heavy_plate",
                "2x mekanism:dust_diamond",
                "mekanism:alloy_atomic",
                "2x tfmg:rubber_sheet",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            output="mekanism:free_runners_armored",
            stock_id="mekanism:free_runners_armored",
            depends_on=["industrial_colonies:mekanism_tools/free_runners"],
        ),
    ]
    ids = [recipe["id"] for recipe in recipes]
    outputs = [_output_item(recipe["output"]) for recipe in recipes]
    removals = [stock for recipe in recipes for stock in recipe["remove"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Mekanism component/tool wave defines duplicate recipe IDs")
    if len(outputs) != len(set(outputs)):
        raise ValueError("Mekanism component/tool wave defines duplicate outputs")
    if len(removals) != len(set(removals)):
        raise ValueError("Mekanism component/tool wave claims a stock recipe twice")
    if "mekanism:energy_tablet" in outputs:
        raise AssertionError("the user-owned Energy Tablet must not be claimed")
    if any("factory" in (output or "") for output in outputs):
        raise AssertionError("direct upgraded factories are outside this wave")
    return recipes


def _output_item(value: Any) -> str | None:
    if isinstance(value, str):
        return re.sub(r"^\d+x\s+", "", value)
    if isinstance(value, dict):
        item = value.get("item") or value.get("id")
        return item if isinstance(item, str) else None
    return None


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed seed field {field!r} must be a list")
    return value


def _assert_unclaimed(data: dict[str, Any], additions: Iterable[Recipe]) -> None:
    additions = list(additions)
    addition_ids = {recipe["id"] for recipe in additions}
    wanted_outputs = {
        output
        for recipe in additions
        if (output := _output_item(recipe.get("output"))) is not None
    }
    wanted_removals = {
        stock for recipe in additions for stock in recipe.get("remove", [])
    }

    owned = wanted_outputs.intersection(_require_list(data, "user_owned_outputs"))
    if owned:
        raise ValueError(f"Mekanism wave cannot claim user-owned outputs: {sorted(owned)}")

    for existing in _require_list(data, "recipes"):
        if not isinstance(existing, dict):
            raise TypeError("managed recipe entries must be objects")
        if existing.get("id") in addition_ids:
            continue
        output = _output_item(existing.get("output"))
        if output in wanted_outputs:
            raise ValueError(
                f"Mekanism component/tool output {output} is already managed by "
                f"{existing.get('id')}"
            )
        overlap = wanted_removals.intersection(existing.get("remove", []))
        if overlap:
            raise ValueError(
                "Mekanism component/tool stock IDs are already claimed by "
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
    """Add sixteen curated Mekanism component/tool recipes in memory."""

    # Planetary freight must not collapse into a pocket teleport shortcut.
    # Retire the briefly-managed card as well as Mekanism's stock acquisition
    # recipe while leaving the teleportation core available as a late
    # manufactured component for non-transport uses.
    retired_id = "industrial_colonies:mekanism_tools/portable_teleporter"
    managed = _require_list(data, "recipes")
    managed[:] = [
        recipe
        for recipe in managed
        if not (isinstance(recipe, dict) and recipe.get("id") == retired_id)
    ]
    additional_removals = _require_list(data, "additional_removals")
    if "mekanism:portable_teleporter" not in additional_removals:
        additional_removals.append("mekanism:portable_teleporter")

    recipes = _recipes()
    _assert_unclaimed(data, recipes)

    claimed_stock_ids = {
        stock for recipe in recipes for stock in recipe.get("remove", [])
    }
    additional_removals[:] = [
        stock for stock in additional_removals if stock not in claimed_stock_ids
    ]
    preserve_recipe_ids = _require_list(data, "preserve_recipe_ids")
    preserve_recipe_ids[:] = [
        stock for stock in preserve_recipe_ids if stock not in claimed_stock_ids
    ]

    managed_outputs = {
        output
        for recipe in recipes
        if (output := _output_item(recipe.get("output"))) is not None
    }
    exclude_outputs = _require_list(data, "exclude_outputs")
    exclude_outputs[:] = [
        output for output in exclude_outputs if output not in managed_outputs
    ]

    for recipe in recipes:
        _upsert(data, recipe)
