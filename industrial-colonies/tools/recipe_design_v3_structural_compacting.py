#!/usr/bin/env python3
"""Replace literal material-border grids with physical compacting jobs.

Rigid containment panels and dense capacitor bodies are exactly the work a
press-and-basin line should perform.  They should not occupy a 5x5 grid merely
to draw the outline of the block being produced.  This module converts the
three reviewed offenders while preserving their batch economics and stock
recipe retirement.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]


RECIPES: list[Recipe] = [
    {
        "id": "industrial_colonies:extreme_grid/high_voltage_capacitor",
        "phase": "High-Energy Grid",
        "order": 70,
        "type": "compacting",
        "comment": (
            "Compress a real bank of TFMG capacitors and lithium charge around "
            "a transformer core, then armor and magnetically shield the finished "
            "high-voltage storage body on the Railway electrical press."
        ),
        "machine": "createcasing:railway_press",
        "inputs": [
            "8x tfmg:capacitor_item",
            "2x tfmg:lithium_charge",
            "4x electroenergetics:heavily_insulated_wire",
            "electroenergetics:transformer_core",
            "tfmg:steel_casing",
            "tfmg:magnetic_alloy_sheet",
        ],
        "output": "electroenergetics:high_voltage_capacitor",
        "remove": ["electroenergetics:crafting/high_voltage_capacitor"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:extreme_grid/heavily_insulated_wire"
        ],
    },
    {
        "id": "industrial_colonies:bigreactors/basic_reactor/casing",
        "node": "CR01 — Containment Engineering",
        "phase": "Nuclear Engineering",
        "order": 300,
        "type": "compacting",
        "comment": (
            "Press eight graphite-lined reactor wall panels from TFMG heavy "
            "plate, fireproof brick, structural steel casing, and graphite.  "
            "Containment is a bulk fabrication job, not an electronics border."
        ),
        "machine": "createcasing:refined_radiance_press",
        "inputs": [
            "8x tfmg:heavy_plate",
            "4x tfmg:fireproof_bricks",
            "4x bigreactors:graphite_ingot",
            "4x tfmg:steel_casing",
        ],
        "output": "8x bigreactors:basic_reactorcasing",
        "remove": [
            "bigreactors:reactor/basic/casing",
            "bigreactors:reactor/basic/casing_recycle",
            "bigreactors:reactor/basic/casing_recycle_glass",
        ],
        "exclusive_output": True,
    },
    {
        "id": "industrial_colonies:bigreactors/reinforced_reactor/casing",
        "node": "CR01 — Advanced Nuclear Fuel",
        "phase": "Nuclear Engineering",
        "order": 600,
        "type": "compacting",
        "comment": (
            "Repress eight basic panels with lead shielding, refined-obsidian "
            "liner, Blutonium qualification material, and Vibranium reinforcement "
            "to produce eight late-reactor containment panels."
        ),
        "machine": "createcasing:refined_radiance_press",
        "inputs": [
            "8x bigreactors:basic_reactorcasing",
            "8x tfmg:lead_sheet",
            "8x mekanism:ingot_refined_obsidian",
            "2x bigreactors:blutonium_ingot",
            "2x allthemodium:vibranium_plate",
        ],
        "output": "8x bigreactors:reinforced_reactorcasing",
        "remove": [
            "bigreactors:reactor/reinforced/casing",
            "bigreactors:reactor/reinforced/casing_alt",
            "bigreactors:reactor/reinforced/casing_recycle",
            "bigreactors:reactor/reinforced/casing_recycle_glass",
            "bigreactors:reactor/reinforced/casing_upgrade",
            "bigreactors:reactor/reinforced/casing_upgrade_alt",
        ],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:bigreactors/basic_reactor/casing",
            "industrial_colonies:bigreactors/reprocessor/controller",
        ],
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
    claimed = {
        str(stock)
        for recipe in RECIPES
        for stock in recipe.get("remove", [])
    }
    additional = _require_list(data, "additional_removals")
    additional[:] = [stock for stock in additional if str(stock) not in claimed]
    preserved = _require_list(data, "preserve_recipe_ids")
    preserved[:] = [stock for stock in preserved if str(stock) not in claimed]
    for recipe in RECIPES:
        _upsert(data, recipe)

