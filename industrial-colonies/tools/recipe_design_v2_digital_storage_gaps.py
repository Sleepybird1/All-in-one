"""Close the remaining weak AE-family autocrafting acquisition routes.

This wave is intentionally narrow.  It replaces the stock shapeless
``crafting unit + storage component`` conversions with readable hardware
integration passes, does the same for the MEGA crafting-storage ladder, and
turns ExtendedAE's assembler-matrix shell into an actual manufactured frame.

The following routes are deliberately preserved:

* AE2 storage-component recursion and cell/housing assembly;
* ExtendedAE Crystal Assembler recipes for its specialized matrix cores and
  extended machines;
* AdvancedAE's quantum multithreader/storage recipes, whose stock inputs
  already use the managed quantum components; and
* AppliedCreate/Create Applied Kinetics routes already covered by the focused
  stress-storage module.

Importing this module has no filesystem effects.  ``apply`` is idempotent and
mutates only the supplied seed dictionary.
"""

from __future__ import annotations

import re
from typing import Any


BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"

DIGITAL = "Digital Logistics"
MEKANIZED = "Mekanized Industry"
HIGH_ENERGY = "High-Energy Grid"

BASIC_CRAFTING_NODE = "CR01 — ME System Basics"
ADVANCED_CRAFTING_NODE = "CR01 — Advanced Digital Crafting"
ENHANCED_CRAFTING_NODE = "CR01 — Enhanced ME Crafting Upgrade"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    if isinstance(value, dict):
        item_id = value.get("id")
        return item_id if isinstance(item_id, str) else None
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
    output: str,
    ingredients: list[str],
    remove: str,
    deployer: str,
    press: str,
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
        "transitional": input_item,
        "output": output,
        "loops": 1,
        "steps": [_deploy(item, deployer) for item in ingredients]
        + [_press(press)],
        "remove": [remove],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _mechanical(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    remove: str,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    widths = {len(row) for row in pattern}
    if len(widths) != 1:
        raise ValueError(f"{recipe_id} has a ragged mechanical-crafting grid")
    used = {symbol for row in pattern for symbol in row if symbol != " "}
    if used != set(key):
        raise ValueError(
            f"{recipe_id} pattern/key mismatch: used={sorted(used)}, "
            f"key={sorted(key)}"
        )
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": [remove],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _ae2_crafting_storage() -> list[dict[str, Any]]:
    return [
        _sequence(
            "industrial_colonies:digital_storage/ae2_crafting_storage_1k",
            phase=DIGITAL,
            node=BASIC_CRAFTING_NODE,
            order=120,
            comment=(
                "Populate a crafting-unit chassis with its first memory plane, "
                "a TFMG control board, buffered copper traces, and a quartz face"
            ),
            input_item="ae2:crafting_unit",
            output="ae2:1k_crafting_storage",
            ingredients=[
                "ae2:cell_component_1k",
                "tfmg:circuit_board",
                "tfmg:copper_wire",
                "tfmg:capacitor_item",
                "ae2:quartz_glass",
            ],
            remove="ae2:network/crafting/1k_cpu_crafting_storage",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            depends_on=["industrial_colonies:digital/crafting_unit"],
        ),
        _sequence(
            "industrial_colonies:digital_storage/ae2_crafting_storage_4k",
            phase=MEKANIZED,
            node=ADVANCED_CRAFTING_NODE,
            order=120,
            comment=(
                "Address the 4k memory plane through calculation logic, then "
                "add a smart fluix bus and plastic dielectric before pressing"
            ),
            input_item="ae2:crafting_unit",
            output="ae2:4k_crafting_storage",
            ingredients=[
                "ae2:cell_component_4k",
                "ae2:calculation_processor",
                "ae2:fluix_smart_cable",
                "tfmg:plastic_sheet",
                "tfmg:capacitor_item",
            ],
            remove="ae2:network/crafting/4k_cpu_crafting_storage",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            depends_on=[
                "industrial_colonies:digital/crafting_unit",
                "industrial_colonies:ae2/calculation_processor",
            ],
        ),
        _sequence(
            "industrial_colonies:digital_storage/ae2_crafting_storage_16k",
            phase=MEKANIZED,
            node=ADVANCED_CRAFTING_NODE,
            order=121,
            comment=(
                "Integrate the 16k plane with stress-aware scheduling, paired "
                "local buffers, and a shielded vibrant-glass service face"
            ),
            input_item="ae2:crafting_unit",
            output="ae2:16k_crafting_storage",
            ingredients=[
                "ae2:cell_component_16k",
                "appliedcreate:advanced_stress_processor",
                "2x tfmg:capacitor_item",
                "tfmg:magnetic_alloy_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            remove="ae2:network/crafting/16k_cpu_crafting_storage",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            depends_on=[
                "industrial_colonies:digital/crafting_unit",
                "industrial_colonies:electronics/advanced_stress_processor",
            ],
        ),
        _sequence(
            "industrial_colonies:digital_storage/ae2_crafting_storage_64k",
            phase=HIGH_ENERGY,
            node=ENHANCED_CRAFTING_NODE,
            order=340,
            comment=(
                "Route the 64k plane over a dense fluix backplane with "
                "concurrent control and laminated magnetic containment"
            ),
            input_item="ae2:crafting_unit",
            output="ae2:64k_crafting_storage",
            ingredients=[
                "ae2:cell_component_64k",
                "extendedae:concurrent_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:capacitor_item",
            ],
            remove="ae2:network/crafting/64k_cpu_crafting_storage",
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            depends_on=[
                "industrial_colonies:digital/crafting_unit",
                "industrial_colonies:extendedae_coverage/concurrent_processor",
            ],
        ),
        _sequence(
            "industrial_colonies:digital_storage/ae2_crafting_storage_256k",
            phase=HIGH_ENERGY,
            node=ENHANCED_CRAFTING_NODE,
            order=341,
            comment=(
                "Finish the 256k crafting store with accumulation telemetry, "
                "full spatial addressing, matter isolation, and a vibrant face"
            ),
            input_item="ae2:crafting_unit",
            output="ae2:256k_crafting_storage",
            ingredients=[
                "ae2:cell_component_256k",
                "megacells:accumulation_processor",
                "ae2:spatial_cell_component_128",
                "ae2:matter_ball",
                "ae2:quartz_vibrant_glass",
            ],
            remove="ae2:network/crafting/256k_cpu_crafting_storage",
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            depends_on=[
                "industrial_colonies:digital/crafting_unit",
                "industrial_colonies:digital/accumulation_processor",
            ],
        ),
    ]


def _assembler_matrix_shell() -> list[dict[str, Any]]:
    return [
        _mechanical(
            "industrial_colonies:digital_storage/assembler_matrix_frame_batch",
            phase=HIGH_ENERGY,
            node=ENHANCED_CRAFTING_NODE,
            order=360,
            comment=(
                "Build four load-bearing assembler frames around one Extended "
                "machine spine with sturdy corners, magnetic rails, and a dense bus"
            ),
            pattern=["S S", "MFM", "SDS"],
            key={
                "S": "create:sturdy_sheet",
                "M": "tfmg:magnetic_alloy_sheet",
                "F": "extendedae:machine_frame",
                "D": "ae2:fluix_smart_dense_cable",
            },
            output="4x extendedae:assembler_matrix_frame",
            remove="extendedae:assembler_matrix_frame",
            depends_on=["industrial_colonies:extendedae/machine_frame"],
        ),
        _sequence(
            "industrial_colonies:digital_storage/assembler_matrix_wall_batch",
            phase=HIGH_ENERGY,
            node=ENHANCED_CRAFTING_NODE,
            order=361,
            comment=(
                "Skin an assembler frame as two service walls with sturdy "
                "panels, vibrant windows, buffered control, and a dense data trunk"
            ),
            input_item="extendedae:assembler_matrix_frame",
            output="2x extendedae:assembler_matrix_wall",
            ingredients=[
                "4x create:sturdy_sheet",
                "2x ae2:quartz_vibrant_glass",
                "tfmg:circuit_board",
                "tfmg:capacitor_item",
                "ae2:fluix_smart_dense_cable",
            ],
            remove="extendedae:assembler_matrix_wall",
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            depends_on=[
                "industrial_colonies:digital_storage/assembler_matrix_frame_batch"
            ],
        ),
        _sequence(
            "industrial_colonies:digital_storage/assembler_matrix_glass_batch",
            phase=HIGH_ENERGY,
            node=ENHANCED_CRAFTING_NODE,
            order=362,
            comment=(
                "Seal an assembler frame into two observation blocks with "
                "vibrant quartz, plastic dielectric, and a smart fluix seam"
            ),
            input_item="extendedae:assembler_matrix_frame",
            output="2x extendedae:assembler_matrix_glass",
            ingredients=[
                "8x ae2:quartz_vibrant_glass",
                "2x tfmg:plastic_sheet",
                "ae2:fluix_smart_cable",
                "tfmg:copper_wire",
            ],
            remove="extendedae:assembler_matrix_glass",
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            depends_on=[
                "industrial_colonies:digital_storage/assembler_matrix_frame_batch"
            ],
        ),
    ]


def _mega_crafting_storage() -> list[dict[str, Any]]:
    tiers = [
        (
            "1m",
            380,
            [
                "megacells:cell_component_1m",
                "megacells:accumulation_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:capacitor_item",
                "tfmg:magnetic_alloy_sheet",
            ],
            "Build the first MEGA crafting store around an accumulation-controlled 1M memory plane and a buffered dense bus",
            [
                "industrial_colonies:ae2_high_energy/mega_crafting_unit",
                "industrial_colonies:megacells/cell_component_1m",
            ],
        ),
        (
            "4m",
            381,
            [
                "megacells:cell_component_4m",
                "extendedae:concurrent_processor",
                "ae2:speed_card",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:quartz_vibrant_glass",
            ],
            "Schedule the 4M plane concurrently, then add speed control and laminated containment to the MEGA chassis",
            [
                "industrial_colonies:ae2_high_energy/mega_crafting_unit",
                "industrial_colonies:megacells_coverage/cell_component_4m",
            ],
        ),
        (
            "16m",
            382,
            [
                "megacells:cell_component_16m",
                "appliedcreate:advanced_stress_processor",
                "ae2:spatial_cell_component_2",
                "tfmg:transformer",
                "tfmg:capacitor_item",
            ],
            "Fit the 16M plane with stress scheduling, local spatial addressing, and its own transformer-backed power buffer",
            [
                "industrial_colonies:ae2_high_energy/mega_crafting_unit",
                "industrial_colonies:megacells_coverage/cell_component_16m",
            ],
        ),
        (
            "64m",
            383,
            [
                "megacells:cell_component_64m",
                "extendedae:concurrent_processor",
                "ae2:spatial_cell_component_16",
                "ae2:matter_ball",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            "Bind the 64M memory plane to a 16-cubed address map with concurrent control and matter-isolated shielding",
            [
                "industrial_colonies:ae2_high_energy/mega_crafting_unit",
                "industrial_colonies:megacells_coverage/cell_component_64m",
            ],
        ),
        (
            "256m",
            384,
            [
                "megacells:cell_component_256m",
                "megacells:accumulation_processor",
                "ae2:spatial_cell_component_128",
                "2x ae2:matter_ball",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            "Complete the 256M crafting store with full-scale spatial addressing, accumulation telemetry, and double matter isolation",
            [
                "industrial_colonies:ae2_high_energy/mega_crafting_unit",
                "industrial_colonies:megacells_coverage/cell_component_256m",
            ],
        ),
    ]

    recipes = [
        _sequence(
            f"industrial_colonies:digital_storage/mega_crafting_storage_{tier}",
            phase=HIGH_ENERGY,
            node=ENHANCED_CRAFTING_NODE,
            order=order,
            comment=comment,
            input_item="megacells:mega_crafting_unit",
            output=f"megacells:{tier}_crafting_storage",
            ingredients=ingredients,
            remove=f"megacells:crafting/{tier}_crafting_storage",
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            depends_on=depends_on,
        )
        for tier, order, ingredients, comment, depends_on in tiers
    ]
    recipes.append(
        _sequence(
            "industrial_colonies:digital_storage/mega_crafting_monitor",
            phase=HIGH_ENERGY,
            node=ENHANCED_CRAFTING_NODE,
            order=385,
            comment=(
                "Instrument the MEGA crafting chassis with a storage display, "
                "concurrent telemetry, a Create display bus, and local buffering"
            ),
            input_item="megacells:mega_crafting_unit",
            output="megacells:mega_crafting_monitor",
            ingredients=[
                "ae2:storage_monitor",
                "extendedae:concurrent_processor",
                "create:display_board",
                "tfmg:circuit_board",
                "tfmg:capacitor_item",
            ],
            remove="megacells:crafting/mega_crafting_monitor",
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            depends_on=[
                "industrial_colonies:ae2_high_energy/mega_crafting_unit",
                "industrial_colonies:extendedae_coverage/concurrent_processor",
            ],
        )
    )
    return recipes


def _recipes() -> list[dict[str, Any]]:
    recipes = [
        *_ae2_crafting_storage(),
        *_assembler_matrix_shell(),
        *_mega_crafting_storage(),
    ]
    ids = [recipe["id"] for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise ValueError("Digital-storage coverage defines duplicate recipe IDs")
    return recipes


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
                f"{wanted_outputs[output]} cannot claim {output}; it is already "
                f"managed by {existing.get('id')}"
            )
        overlap = set(existing.get("remove", [])).intersection(wanted_removals)
        if overlap:
            raise ValueError(
                f"Digital-storage stock IDs are already claimed by "
                f"{existing.get('id')}: {sorted(overlap)}"
            )

    additional = set(data.get("additional_removals", []))
    overlap = sorted(additional.intersection(wanted_removals))
    if overlap:
        raise ValueError(
            f"Digital-storage removals are already globally claimed: {overlap}"
        )

    preserved = set(data.get("preserve_recipe_ids", []))
    overlap = sorted(preserved.intersection(wanted_removals))
    if overlap:
        raise ValueError(
            f"Digital-storage coverage cannot remove preserved recipes: {overlap}"
        )


def _upsert(data: dict[str, Any], recipe: dict[str, Any]) -> None:
    matches = [
        index
        for index, existing in enumerate(data.get("recipes", []))
        if existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"Managed recipe is duplicated: {recipe['id']}")
    if matches:
        data["recipes"][matches[0]] = recipe
    else:
        data.setdefault("recipes", []).append(recipe)


def apply(data: dict[str, Any]) -> None:
    """Apply the curated autocrafting/storage gap wave in place."""

    additions = _recipes()
    claimed_stock_ids = {
        stock_id for recipe in additions for stock_id in recipe.get("remove", [])
    }
    managed_outputs = {
        output
        for recipe in additions
        if (output := _item_id(recipe.get("output"))) is not None
    }
    # Earlier inventory passes preserve stock recipes until a focused design
    # explicitly owns them.  Promote those entries from ``preserve`` (or a
    # bare removal) before the conflict audit; another managed recipe remains
    # a hard conflict and is still rejected by ``_assert_unclaimed``.
    data["additional_removals"] = [
        stock_id
        for stock_id in data.get("additional_removals", [])
        if stock_id not in claimed_stock_ids
    ]
    data["preserve_recipe_ids"] = [
        stock_id
        for stock_id in data.get("preserve_recipe_ids", [])
        if stock_id not in claimed_stock_ids
    ]
    data["exclude_outputs"] = [
        output
        for output in data.get("exclude_outputs", [])
        if output not in managed_outputs
    ]
    _assert_unclaimed(data, additions)

    for recipe in additions:
        _upsert(data, recipe)
