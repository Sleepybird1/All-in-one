#!/usr/bin/env python3
"""Conservatively retire proven stock-copy recipe cards.

The current catalog-to-seed audit found no additional safe retirements.  The
four exact process/ingredient matches all add intentional Create Encased
machine locks, and the sole same-material (but reordered) match deliberately
routes transformer work through separate Copper and Railway environments.

``_RETIREMENTS`` therefore remains empty.  Keeping the generic, idempotent
retirement implementation here makes the negative audit explicit and gives a
safe home for a future catalog-proven stock copy without weakening any of the
intentional manufacturing locks documented below.
"""

from __future__ import annotations

from typing import Any


# managed recipe id -> (exact stock recipe id, output id)
#
# Do not populate this table from visual similarity alone.  A candidate must
# match the installed stock recipe's meaningful process, ingredient counts,
# output count, and lack any intentional casing lock, canonicalization, or
# batch-size change.
_RETIREMENTS: dict[str, tuple[str, str]] = {}


# Evidence from the 2026-09-01 static catalog comparison.  These are not
# retirement candidates: their stock-equivalent material/process bodies are
# intentionally owned to select a specific manufacturing environment.
AUDITED_INTENTIONAL_SOURCE_MATCHES: dict[str, str] = {
    "industrial_colonies:electronics/capacitor": (
        "Preserves TFMG's material sequence while locking every deployment to "
        "the Copper electronics line."
    ),
    "industrial_colonies:electronics/circuit_board": (
        "Preserves TFMG's populated-board sequence while locking component "
        "placement to Copper deployers."
    ),
    "industrial_colonies:big_cannons/recoil_spring": (
        "Preserves the installed forming sequence while requiring the Railway "
        "heavy press."
    ),
    "industrial_colonies:tfmg_core/heavy_plate": (
        "Preserves the three reductions while using the Brass bootstrap press "
        "needed before Railway machinery exists."
    ),
    "industrial_colonies:high_voltage/transformer_core": (
        "Uses the stock material totals but assigns winding to Copper deployers, "
        "lamination to Railway deployers, and final closure to the Railway press."
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
    """Apply only catalog-proven stock-copy retirements, idempotently."""

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
        # Keep auto-assignment from recreating a card for the stock-restored
        # output if automated policy is enabled in a later design pass.
        _append_unique(exclude_outputs, output_id)
