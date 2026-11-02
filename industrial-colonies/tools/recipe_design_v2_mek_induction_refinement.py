"""Refine Mekanism's Induction Matrix cell/provider upgrade ladder.

The seed currently compresses whole machines together, including four prior
cells or providers per upgrade.  This module replaces those eight owned
recipes with one-to-one sequenced upgrades.  Cells receive storage hardware
(lithium, tablets, capacitors, and magnetic containment); providers receive
throughput hardware (cables, transformers, conductors, and protection).

The recipe's existing phase selects the manufacturing environment:
Industrial Iron for Mekanized Industry, Weathered Iron for High-Energy Grid,
and Refined Radiance only for Nuclear Engineering.  The module does not retime
anything, mutate the source seed, or perform filesystem work on import.
"""

from __future__ import annotations

import re
from typing import Any


_COUNTED_ITEM = re.compile(r"^\s*(\d+)x\s+(.+?)\s*$")

_ENVIRONMENT_BY_PHASE = {
    "Mekanized Industry": (
        "createcasing:industrial_iron_deployer",
        "createcasing:industrial_iron_press",
    ),
    "High-Energy Grid": (
        "createcasing:weathered_iron_deployer",
        "createcasing:weathered_iron_press",
    ),
    "Nuclear Engineering": (
        "createcasing:refined_radiance_deployer",
        "createcasing:refined_radiance_press",
    ),
}


def _item_id(value: Any) -> str | None:
    if isinstance(value, dict):
        item_id = value.get("id")
        return item_id if isinstance(item_id, str) else None
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(2) if match else value.strip()


def _item_count(value: Any) -> int:
    if isinstance(value, dict):
        count = value.get("count", 1)
        return int(count) if isinstance(count, int) and not isinstance(count, bool) else 0
    if not isinstance(value, str):
        return 0
    match = _COUNTED_ITEM.fullmatch(value)
    return int(match.group(1)) if match else 1


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _designs() -> list[dict[str, Any]]:
    return [
        {
            "id": "industrial_colonies:mekanism/induction/basic_cell",
            "input": "mekanism:induction_casing",
            "output": "mekanism:basic_induction_cell",
            "comment": (
                "Populate one matrix casing with a drained Basic Cube, lithium "
                "banks, tablet buses, capacitance, and magnetic containment"
            ),
            "ingredients": [
                "mekanism:basic_energy_cube",
                "mekanism:basic_control_circuit",
                "mekanism:alloy_infused",
                "4x tfmg:lithium_charge",
                "2x mekanism:energy_tablet",
                "tfmg:capacitor_item",
                "tfmg:magnetic_alloy_sheet",
            ],
            "depends_on": [
                "industrial_colonies:mekanism/induction/casing",
                "industrial_colonies:mekanism/storage/basic_energy_cube",
                "industrial_colonies:mekanism/basic_control_circuit",
            ],
        },
        {
            "id": "industrial_colonies:mekanism/induction/basic_provider",
            "input": "mekanism:induction_casing",
            "output": "mekanism:basic_induction_provider",
            "comment": (
                "Populate one matrix casing with a drained Basic Cube, control, "
                "paired cable lanes, transformer, hub, and external contacts"
            ),
            "ingredients": [
                "mekanism:basic_energy_cube",
                "mekanism:basic_control_circuit",
                "mekanism:alloy_infused",
                "2x mekanism:basic_universal_cable",
                "tfmg:transformer",
                "tfmg:steel_cable_hub",
                "2x electroenergetics:connector",
            ],
            "depends_on": [
                "industrial_colonies:mekanism/induction/casing",
                "industrial_colonies:mekanism/storage/basic_energy_cube",
                "industrial_colonies:mekanism/basic_control_circuit",
                "industrial_colonies:mekanism/transmission/basic_universal_cable",
                "industrial_colonies:tfmg_heavy_electrical/transformer",
                "industrial_colonies:tfmg_coverage/steel_cable_hub",
                "industrial_colonies:grid/connector",
            ],
        },
        {
            "id": "industrial_colonies:mekanism/induction/advanced_cell",
            "input": "mekanism:basic_induction_cell",
            "output": "mekanism:advanced_induction_cell",
            "comment": (
                "Upgrade one Basic Cell with its drained Advanced Cube, "
                "reinforced control, six fresh lithium banks, and layered buffering"
            ),
            "ingredients": [
                "mekanism:advanced_energy_cube",
                "mekanism:advanced_control_circuit",
                "mekanism:alloy_reinforced",
                "6x tfmg:lithium_charge",
                "2x tfmg:capacitor_item",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            "depends_on": [
                "industrial_colonies:mekanism/induction/basic_cell",
                "industrial_colonies:mekanism/storage/advanced_energy_cube",
                "industrial_colonies:mekanism/advanced_control_circuit",
            ],
        },
        {
            "id": "industrial_colonies:mekanism/induction/advanced_provider",
            "input": "mekanism:basic_induction_provider",
            "output": "mekanism:advanced_induction_provider",
            "comment": (
                "Upgrade one Basic Provider with its drained Advanced Cube, "
                "reinforced routing, twin Advanced lanes, a large coil, and cable hub"
            ),
            "ingredients": [
                "mekanism:advanced_energy_cube",
                "mekanism:advanced_control_circuit",
                "mekanism:alloy_reinforced",
                "2x mekanism:advanced_universal_cable",
                "tfmg:large_coil",
                "tfmg:steel_cable_hub",
                "electroenergetics:connector",
            ],
            "depends_on": [
                "industrial_colonies:mekanism/induction/basic_provider",
                "industrial_colonies:mekanism/storage/advanced_energy_cube",
                "industrial_colonies:mekanism/advanced_control_circuit",
                "industrial_colonies:mekanism/transmission/advanced_universal_cable",
                "industrial_colonies:tfmg_coverage/steel_cable_hub",
                "industrial_colonies:grid/connector",
            ],
        },
        {
            "id": "industrial_colonies:mekanism/induction/elite_cell",
            "input": "mekanism:advanced_induction_cell",
            "output": "mekanism:elite_induction_cell",
            "comment": (
                "Upgrade one Advanced Cell with its drained Elite Cube, atomic "
                "isolation, eight lithium banks, and a four-capacitor buffer"
            ),
            "ingredients": [
                "mekanism:elite_energy_cube",
                "mekanism:elite_control_circuit",
                "mekanism:alloy_atomic",
                "8x tfmg:lithium_charge",
                "4x tfmg:capacitor_item",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            "depends_on": [
                "industrial_colonies:mekanism/induction/advanced_cell",
                "industrial_colonies:mekanism/storage/elite_energy_cube",
                "industrial_colonies:mekanism/elite_control_circuit",
            ],
        },
        {
            "id": "industrial_colonies:mekanism/induction/elite_provider",
            "input": "mekanism:advanced_induction_provider",
            "output": "mekanism:elite_induction_provider",
            "comment": (
                "Upgrade one Advanced Provider with its drained Elite Cube, atomic "
                "routing, twin Elite lanes, metering, regulation, and isolation"
            ),
            "ingredients": [
                "mekanism:elite_energy_cube",
                "mekanism:elite_control_circuit",
                "mekanism:alloy_atomic",
                "2x mekanism:elite_universal_cable",
                "electroenergetics:current_transformer",
                "electroenergetics:voltage_regulator",
                "electroenergetics:high_voltage_switch",
            ],
            "depends_on": [
                "industrial_colonies:mekanism/induction/advanced_provider",
                "industrial_colonies:mekanism/storage/elite_energy_cube",
                "industrial_colonies:mekanism/elite_control_circuit",
                "industrial_colonies:mekanism/transmission/elite_universal_cable",
                "industrial_colonies:high_voltage/current_transformer",
                "industrial_colonies:high_voltage/voltage_regulator",
                "industrial_colonies:extreme_grid/high_voltage_switch",
            ],
        },
        {
            "id": "industrial_colonies:mekanism/induction/ultimate_cell",
            "input": "mekanism:elite_induction_cell",
            "output": "mekanism:ultimate_induction_cell",
            "comment": (
                "Upgrade one Elite Cell with its drained Ultimate Cube, ultimate "
                "control, twelve lithium banks, tablet buses, and HV capacitance"
            ),
            "ingredients": [
                "mekanism:ultimate_energy_cube",
                "mekanism:ultimate_control_circuit",
                "2x mekanism:alloy_atomic",
                "12x tfmg:lithium_charge",
                "4x mekanism:energy_tablet",
                "2x electroenergetics:high_voltage_capacitor",
                "2x tfmg:laminated_magnetic_alloy_block",
            ],
            "depends_on": [
                "industrial_colonies:mekanism/induction/elite_cell",
                "industrial_colonies:mekanism/storage/ultimate_energy_cube",
                "industrial_colonies:mekanism/ultimate_control_circuit",
                "industrial_colonies:extreme_grid/high_voltage_capacitor",
            ],
        },
        {
            "id": "industrial_colonies:mekanism/induction/ultimate_provider",
            "input": "mekanism:elite_induction_provider",
            "output": "mekanism:ultimate_induction_provider",
            "comment": (
                "Upgrade one Elite Provider with its drained Ultimate Cube, "
                "ultimate control, protected HV conductors, SF6 interruption, and buffering"
            ),
            "ingredients": [
                "mekanism:ultimate_energy_cube",
                "mekanism:ultimate_control_circuit",
                "2x mekanism:alloy_atomic",
                "4x electroenergetics:heavily_insulated_wire",
                "electroenergetics:sulfur_hexafluoride_breaker",
                "electroenergetics:high_voltage_capacitor",
                "tfmg:large_coil",
            ],
            "depends_on": [
                "industrial_colonies:mekanism/induction/elite_provider",
                "industrial_colonies:mekanism/storage/ultimate_energy_cube",
                "industrial_colonies:mekanism/ultimate_control_circuit",
                "industrial_colonies:extreme_grid/heavily_insulated_wire",
                "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker",
                "industrial_colonies:extreme_grid/high_voltage_capacitor",
            ],
        },
    ]


def _replace(data: dict[str, Any], design: dict[str, Any]) -> None:
    recipe_id = design["id"]
    matches = [
        index
        for index, recipe in enumerate(data.get("recipes", []))
        if recipe.get("id") == recipe_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {recipe_id}, found {len(matches)}")

    old = data["recipes"][matches[0]]
    output = design["output"]
    if _item_id(old.get("output")) != output or _item_count(old.get("output")) != 1:
        raise ValueError(
            f"{recipe_id} no longer owns exactly one {output}: {old.get('output')!r}"
        )
    if old.get("remove") != [
        {
            "basic_cell": "mekanism:induction/cell/basic",
            "basic_provider": "mekanism:induction/provider/basic",
            "advanced_cell": "mekanism:induction/cell/advanced",
            "advanced_provider": "mekanism:induction/provider/advanced",
            "elite_cell": "mekanism:induction/cell/elite",
            "elite_provider": "mekanism:induction/provider/elite",
            "ultimate_cell": "mekanism:induction/cell/ultimate",
            "ultimate_provider": "mekanism:induction/provider/ultimate",
        }[recipe_id.rsplit("/", 1)[-1]]
    ]:
        raise ValueError(f"{recipe_id} stock removal changed: {old.get('remove')!r}")

    phase = old.get("phase")
    if phase not in _ENVIRONMENT_BY_PHASE:
        raise ValueError(f"{recipe_id} has no induction environment for {phase!r}")
    deployer, press = _ENVIRONMENT_BY_PHASE[phase]

    replacement: dict[str, Any] = {"id": recipe_id}
    for key in ("node", "phase", "order"):
        if key in old:
            replacement[key] = old[key]
    replacement.update(
        {
            "type": "sequenced_assembly",
            "comment": design["comment"],
            "input": design["input"],
            "transitional": design["input"],
            "output": output,
            "loops": 1,
            "steps": [
                _deploy(ingredient, deployer)
                for ingredient in design["ingredients"]
            ]
            + [_press(press)],
            "remove": list(old["remove"]),
            "exclusive_output": old.get("exclusive_output", True),
            "depends_on": list(design["depends_on"]),
        }
    )
    for key in ("if_mod_loaded", "notes"):
        if key in old:
            replacement[key] = old[key]
    data["recipes"][matches[0]] = replacement


def apply(data: dict[str, Any]) -> None:
    """Replace the eight owned induction recipes in the supplied seed."""

    for design in _designs():
        _replace(data, design)

