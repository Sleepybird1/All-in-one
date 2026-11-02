#!/usr/bin/env python3
"""Give Create Low-Heated a manufactured early-game burner.

The installed recipe is three loose Andesite Alloy pieces.  That makes the
block cheaper than the mechanical processing line it augments and does not
describe a burner.  This pass installs a compact masonry firebox, an iron heat
spreader, and Andesite mounting brackets without turning an early utility into
a late precision assembly.
"""

from __future__ import annotations

from typing import Any


RECIPE_ID = "industrial_colonies:create_lowheated/basic_burner"
OUTPUT = "createlowheated:basic_burner"
STOCK_RECIPE = "createlowheated:basic_burner"


def _recipe() -> dict[str, Any]:
    return {
        "id": RECIPE_ID,
        "node": "CR01 — Mechanical Technology",
        "phase": "Mechanical Foundations",
        "order": 130,
        "type": "shaped",
        "comment": (
            "Build the first controlled heat source as a brick-lined campfire "
            "with Andesite mounting cheeks and an iron-sheet heat spreader"
        ),
        "pattern": [
            " S ",
            "ACA",
            "BBB",
        ],
        "key": {
            "S": "create:iron_sheet",
            "A": "create:andesite_alloy",
            "C": "minecraft:campfire",
            "B": "minecraft:bricks",
        },
        "output": OUTPUT,
        "remove": [STOCK_RECIPE],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:mechanical/mechanical_press"],
    }


def apply(data: dict[str, Any]) -> None:
    """Upsert the single source-owned Low-Heated recipe in place."""

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("Managed recipe data must contain a recipes list")

    matches = [
        index
        for index, recipe in enumerate(recipes)
        if isinstance(recipe, dict) and recipe.get("id") == RECIPE_ID
    ]
    if len(matches) > 1:
        raise ValueError(f"Managed recipe is duplicated: {RECIPE_ID}")

    replacement = _recipe()
    if matches:
        recipes[matches[0]] = replacement
    else:
        recipes.append(replacement)

    data["exclude_outputs"] = [
        item for item in data.get("exclude_outputs", []) if item != OUTPUT
    ]
    data["preserve_recipe_ids"] = [
        recipe_id
        for recipe_id in data.get("preserve_recipe_ids", [])
        if recipe_id != STOCK_RECIPE
    ]
