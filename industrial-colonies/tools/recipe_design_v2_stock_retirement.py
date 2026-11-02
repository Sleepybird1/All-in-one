#!/usr/bin/env python3
"""Retire managed recipe cards which add no useful progression behavior.

This module is deliberately side-effect free.  ``apply`` mutates only the
managed seed dictionary supplied by its caller; it never reads or writes the
seed, runs a build, or touches the live pack.

The retirement list is intentionally conservative.  A recipe belongs here
only when it either preserves stock behavior or replaces a well-expressed
stock recipe with cost/shape filler, without adding a meaningful Create
Encased environment or progression rule.  Recipes which merely resemble stock
are left for a real redesign instead of being silently restored.
"""

from __future__ import annotations

from typing import Any


# managed recipe id -> (stock recipe id, output id)
_RETIREMENTS: dict[str, tuple[str, str]] = {
    # This card only broadens vanilla copper ingots to the conventional copper
    # tag.  Its six wires, three ingots, two-hub yield, and crafting process are
    # otherwise the installed TFMG recipe, so the tag-only mirror is not worth
    # owning as a custom progression recipe.
    "industrial_colonies:early_power_cables/copper_cable_hub": (
        "tfmg:crafting/materials/copper_cable_hub",
        "tfmg:copper_cable_hub",
    ),
    # The 5x5 replacement adds cast-iron frame and plate filler around the same
    # refractory outlet concept.  TFMG's compact stock shape already expresses
    # that part correctly with fireproof brick, cast-iron pipe, and a cast-iron
    # block, so the filler-heavy managed card should not survive design v2.
    "industrial_colonies:steelworks/blast_furnace_output": (
        "tfmg:crafting/materials/blast_furnace_output",
        "tfmg:blast_furnace_output",
    ),
    # The managed card repeats Cosmowarp's installed sanding recipe exactly:
    # one raw Moon Crystal -> one Moon Crystal through Create sandpaper
    # polishing.  It has no casing-specific machine lock or changed yield.
    "industrial_colonies:interstellar/moon_crystal_polishing": (
        "cosmowarp:moon_crystal_sanding",
        "cosmowarp:moon_crystal",
    ),
}


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed recipe seed field {field!r} must be a list")
    return value


def _append_unique(values: list[Any], value: str) -> None:
    if value not in values:
        values.append(value)


def _drop_dependency(recipe: dict[str, Any], retired_id: str) -> None:
    dependencies = recipe.get("depends_on")
    if dependencies is None:
        return
    if not isinstance(dependencies, list):
        raise TypeError(
            f"managed recipe {recipe.get('id')!r} has a non-list depends_on field"
        )
    remaining = [dependency for dependency in dependencies if dependency != retired_id]
    if remaining:
        recipe["depends_on"] = remaining
    else:
        recipe.pop("depends_on", None)


def apply(data: dict[str, Any]) -> None:
    """Restore audited stock recipes and remove their redundant managed cards."""

    recipes = _require_list(data, "recipes")
    managed_ids = [recipe.get("id") for recipe in recipes if isinstance(recipe, dict)]
    duplicate_ids = {
        recipe_id for recipe_id in managed_ids if managed_ids.count(recipe_id) > 1
    }
    if duplicate_ids:
        rendered = ", ".join(sorted(str(value) for value in duplicate_ids))
        raise ValueError(f"duplicate managed recipe ids: {rendered}")

    retirement_ids = set(_RETIREMENTS)
    data["recipes"] = [
        recipe
        for recipe in recipes
        if not isinstance(recipe, dict) or recipe.get("id") not in retirement_ids
    ]

    # Managed dependency metadata may point at a retired card.  The restored
    # stock recipe supplies the same intermediate naturally, so no synthetic
    # managed dependency is needed.
    for recipe in data["recipes"]:
        if not isinstance(recipe, dict):
            raise TypeError("managed recipe entries must be objects")
        for retired_id in retirement_ids:
            _drop_dependency(recipe, retired_id)

    additional_removals = _require_list(data, "additional_removals")
    preserve_recipe_ids = _require_list(data, "preserve_recipe_ids")
    exclude_outputs = _require_list(data, "exclude_outputs")

    stock_ids = {stock_id for stock_id, _output_id in _RETIREMENTS.values()}
    additional_removals[:] = [
        recipe_id for recipe_id in additional_removals if recipe_id not in stock_ids
    ]

    for stock_id, output_id in _RETIREMENTS.values():
        _append_unique(preserve_recipe_ids, stock_id)
        # Auto assignment is disabled in design v2, but retaining this guard
        # prevents a future policy change from recreating the retired card.
        _append_unique(exclude_outputs, output_id)
