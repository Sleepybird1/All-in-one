#!/usr/bin/env python3
"""Manufacturing-first mechanical-grid redesigns for recipe design v2.

This module only mutates the supplied manifest dictionary.  It deliberately
keeps each recipe's progression and removal metadata while replacing the
recipe-specific mechanical-crafting body.
"""

from __future__ import annotations

from typing import Any


RecipeBody = dict[str, Any]


# Fields owned by the recipe implementation rather than its progression or
# conditional metadata.  Removing all known body variants keeps apply()
# idempotent even if a target was temporarily migrated to another recipe type.
_BODY_FIELDS = {
    "type",
    "comment",
    "pattern",
    "key",
    "output",
    "input",
    "transitional",
    "loops",
    "steps",
    "ingredients",
    "results",
    "result",
    "machine",
    "machine_mode",
    "vat_mode",
    "heat",
    "min_size",
    "processing_time",
}


def _mechanical(
    *,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: Any,
) -> RecipeBody:
    if not pattern:
        raise ValueError("Mechanical pattern must be non-empty")
    width = len(pattern[0])
    if any(len(row) != width for row in pattern):
        raise ValueError(f"Mechanical pattern must be non-empty and rectangular: {pattern!r}")
    return {
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
    }


_REPLACEMENTS: dict[str, RecipeBody] = {
    "industrial_colonies:ae2/charger": _mechanical(
        comment="Build an open Copper charging throat over a TFMG generator and capacitor instead of filling an unrelated 5x5 grid",
        pattern=[
            "S S",
            "WGW",
            "SCS",
        ],
        key={
            "S": "create:copper_sheet",
            "W": "tfmg:copper_wire",
            "G": "tfmg:generator",
            "C": "tfmg:capacitor_item",
        },
        output="ae2:charger",
    ),
    "industrial_colonies:ae2/inscriber": _mechanical(
        comment="Mount a piston ram and Brass electronics controller over an inherited Brass press bed",
        pattern=[
            " P ",
            "BDB",
            "CRC",
        ],
        key={
            "P": "minecraft:piston",
            "B": "create:brass_sheet",
            "D": "tfmg:circuit_board",
            "C": "create:brass_casing",
            "R": "createcasing:brass_press",
        },
        output="ae2:inscriber",
    ),
    "industrial_colonies:digital/crafting_unit": _mechanical(
        comment="Assemble the autocrafting CPU as an iron-enclosed stress processor, logic pair, fluix bus, and TFMG backplane",
        pattern=[
            "IPI",
            "LFL",
            "ICI",
        ],
        key={
            "I": "create:iron_sheet",
            "P": "appliedcreate:stress_processor",
            "L": "ae2:logic_processor",
            "F": "ae2:fluix_glass_cable",
            "C": "tfmg:circuit_board",
        },
        output="ae2:crafting_unit",
    ),
    "industrial_colonies:digital/storage_drive": _mechanical(
        comment="Build an open four-bay ME Drive with literal cell trays and a fluix-controlled digital backplane",
        pattern=[
            "ISCI",
            "H  H",
            "H  H",
            "IFPI",
        ],
        key={
            "I": "create:iron_sheet",
            "S": "appliedcreate:advanced_stress_processor",
            "C": "tfmg:circuit_board",
            "H": "ae2:item_cell_housing",
            "F": "ae2:fluix_glass_cable",
            "P": "ae2:logic_processor",
        },
        output="ae2:drive",
    ),
    "industrial_colonies:digital/pattern_encoding_terminal": _mechanical(
        comment="Upgrade the Crafting Terminal with a vibrant-glass display, calculation pair, control board, and fluix network link",
        pattern=[
            "QDQ",
            "PTP",
            "CFC",
        ],
        key={
            "Q": "ae2:quartz_vibrant_glass",
            "D": "create:display_board",
            "P": "ae2:calculation_processor",
            "T": "ae2:crafting_terminal",
            "C": "tfmg:circuit_board",
            "F": "ae2:fluix_glass_cable",
        },
        output="ae2:pattern_encoding_terminal",
    ),
    "industrial_colonies:computercraft/computer/normal": _mechanical(
        comment="Layer a display, manufactured logic board, wiring, and plastic insulation inside a Brass computer chassis",
        pattern=[
            "SDS",
            "BLC",
            "SPS",
        ],
        key={
            "S": "create:brass_sheet",
            "D": "create:display_board",
            "B": "tfmg:circuit_board",
            "L": "ae2:logic_processor",
            "C": "tfmg:copper_wire",
            "P": "tfmg:plastic_sheet",
        },
        output="computercraft:computer_normal",
    ),
    "industrial_colonies:computercraft/monitor/normal": _mechanical(
        comment="Fabricate a matched monitor pair as quartz pixels, display-driver boards, and a shared Brass controller frame",
        pattern=[
            "QQQ",
            "DDD",
            "SCS",
        ],
        key={
            "Q": "create:polished_rose_quartz",
            "D": "create:display_board",
            "S": "create:brass_sheet",
            "C": "tfmg:circuit_board",
        },
        output={"kind": "ITEM", "id": "computercraft:monitor_normal", "count": 2},
    ),
    "industrial_colonies:computercraft/io/disk_drive": _mechanical(
        comment="Build a disk drive around a motorized spindle, removable-media depot, and dedicated logic controller",
        pattern=[
            "SMS",
            "IDI",
            "BCB",
        ],
        key={
            "S": "create:brass_sheet",
            "M": "tfmg:electric_motor",
            "I": "create:iron_sheet",
            "D": "create:depot",
            "B": "tfmg:circuit_board",
            "C": "ae2:logic_processor",
        },
        output="computercraft:disk_drive",
    ),
    "industrial_colonies:computercraft/io/printer": _mechanical(
        comment="Arrange a moving print carriage above its paper depot, paired controls, and ink reservoir",
        pattern=[
            "SPS",
            "CMC",
            "SIS",
        ],
        key={
            "S": "create:brass_sheet",
            "P": "create:mechanical_piston",
            "C": "tfmg:circuit_board",
            "M": "create:depot",
            "I": "minecraft:ink_sac",
        },
        output="computercraft:printer",
    ),
    "industrial_colonies:computercraft/mobile/pocket_computer": _mechanical(
        comment="Miniaturize a desktop computer, display, and wireless modem into a gold-clad portable terminal",
        pattern=[
            "GQG",
            "WCM",
            "GBG",
        ],
        key={
            "G": "create:golden_sheet",
            "Q": "ae2:quartz_vibrant_glass",
            "W": "computercraft:wireless_modem_normal",
            "C": "computercraft:computer_normal",
            "M": "computercraft:monitor_normal",
            "B": "tfmg:etched_circuit_board",
        },
        output="computercraft:pocket_computer_normal",
    ),
    "industrial_colonies:computercraft/mobile/turtle": _mechanical(
        comment="Construct the Turtle as a programmable robot with a tool arm, twin electric drives, and a cargo bay",
        pattern=[
            "SDS",
            "MCM",
            "SAS",
        ],
        key={
            "S": "create:brass_sheet",
            "D": "create:deployer",
            "M": "tfmg:electric_motor",
            "C": "computercraft:computer_normal",
            "A": "minecraft:barrel",
        },
        output="computercraft:turtle_normal",
    ),
    "industrial_colonies:mekanism/steel_casing": _mechanical(
        comment="Integrate a TFMG steel shell with osmium rails, visible glass, and a first-generation Mekanism controller",
        pattern=[
            "SOS",
            "GBG",
            "SOS",
        ],
        key={
            "S": "tfmg:steel_casing",
            "O": "mekanism:ingot_osmium",
            "G": "minecraft:glass",
            "B": "mekanism:basic_control_circuit",
        },
        output="mekanism:steel_casing",
    ),
    "industrial_colonies:mekanism/combiner": _mechanical(
        comment="Integrate the prior Industrial Iron press as the Combiner head above its reinforced control and machine frame",
        pattern=[
            "HPH",
            "ACA",
            "HSH",
        ],
        key={
            "H": "tfmg:heavy_plate",
            "P": "createcasing:industrial_iron_press",
            "A": "mekanism:alloy_reinforced",
            "C": "mekanism:advanced_control_circuit",
            "S": "mekanism:steel_casing",
        },
        output="mekanism:combiner",
    ),
    "industrial_colonies:mekanism/storage/basic_energy_cube": _mechanical(
        comment="Package lithium cells and energy tablets around the completed Electro Energetics accumulator and a basic controller",
        pattern=[
            "LTL",
            "EGE",
            "LCL",
        ],
        key={
            "L": "tfmg:lithium_charge",
            "T": "tfmg:copper_wire",
            "E": "mekanism:energy_tablet",
            "G": "electroenergetics:accumulator",
            "C": "mekanism:basic_control_circuit",
        },
        output="mekanism:basic_energy_cube",
    ),
    "industrial_colonies:mekanism/storage/advanced_energy_cube": _mechanical(
        comment="Rehouse the Basic Energy Cube in a lithium-backed reinforced osmium enclosure with advanced control",
        pattern=[
            "OAO",
            "LBL",
            "OCO",
        ],
        key={
            "O": "mekanism:ingot_osmium",
            "A": "mekanism:alloy_reinforced",
            "L": "tfmg:lithium_charge",
            "B": "mekanism:basic_energy_cube",
            "C": "mekanism:advanced_control_circuit",
        },
        output="mekanism:advanced_energy_cube",
    ),
    "industrial_colonies:mekanism/storage/elite_energy_cube": _mechanical(
        comment="Upgrade the Advanced Cube with gold bus plates, atomic isolation, fresh lithium cells, and elite control",
        pattern=[
            "GAG",
            "LBL",
            "GCG",
        ],
        key={
            "G": "create:golden_sheet",
            "A": "mekanism:alloy_atomic",
            "L": "tfmg:lithium_charge",
            "B": "mekanism:advanced_energy_cube",
            "C": "mekanism:elite_control_circuit",
        },
        output="mekanism:elite_energy_cube",
    ),
    "industrial_colonies:mekanism/storage/ultimate_energy_cube": _mechanical(
        comment="Protect the Elite Cube with diamond insulation, fresh lithium cells, ultimate control, and the completed SF6 breaker",
        pattern=[
            "DHD",
            "LBL",
            "DCD",
        ],
        key={
            "D": "minecraft:diamond",
            "H": "electroenergetics:sulfur_hexafluoride_breaker",
            "L": "tfmg:lithium_charge",
            "B": "mekanism:elite_energy_cube",
            "C": "mekanism:ultimate_control_circuit",
        },
        output="mekanism:ultimate_energy_cube",
    ),
    "industrial_colonies:mekanism/induction/casing": _mechanical(
        comment="Fabricate eight induction shell sections as a hollow heavy frame around an insulated high-energy bus",
        pattern=[
            "SHHHS",
            "H W H",
            "H M H",
            "H W H",
            "SHHHS",
        ],
        key={
            "S": "mekanism:steel_casing",
            "H": "tfmg:heavy_plate",
            "W": "electroenergetics:heavily_insulated_wire",
            "M": "tfmg:heavy_machinery_casing",
        },
        output="8x mekanism:induction_casing",
    ),
    "industrial_colonies:mekanism/induction/port": _mechanical(
        comment="Build a matched port pair by enclosing an ultimate cable and controller between voltage regulation and capacitance",
        pattern=[
            "CUC",
            "VRV",
            "CHC",
        ],
        key={
            "C": "mekanism:induction_casing",
            "U": "mekanism:ultimate_universal_cable",
            "V": "electroenergetics:voltage_regulator",
            "R": "mekanism:ultimate_control_circuit",
            "H": "electroenergetics:high_voltage_capacitor",
        },
        output="2x mekanism:induction_port",
    ),
}


def apply(data: dict[str, Any]) -> None:
    """Apply all mechanical-grid replacements to ``data`` in place.

    Every expected target must exist exactly once.  Only recipe-body fields are
    removed, so node, phase, order, removal, exclusivity, dependency, and
    conditional metadata survive unchanged.
    """

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("Managed recipe data must contain a recipes list")

    positions: dict[str, list[int]] = {}
    for index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict) or "id" not in recipe:
            continue
        positions.setdefault(recipe["id"], []).append(index)

    missing = sorted(recipe_id for recipe_id in _REPLACEMENTS if recipe_id not in positions)
    duplicated = sorted(
        recipe_id for recipe_id in _REPLACEMENTS if len(positions.get(recipe_id, [])) > 1
    )
    if missing or duplicated:
        details: list[str] = []
        if missing:
            details.append(f"missing={missing}")
        if duplicated:
            details.append(f"duplicated={duplicated}")
        raise AssertionError("Mechanical recipe targets do not match seed: " + "; ".join(details))

    for recipe_id, body in _REPLACEMENTS.items():
        recipe = recipes[positions[recipe_id][0]]
        for field in _BODY_FIELDS:
            recipe.pop(field, None)
        recipe.update(body)
