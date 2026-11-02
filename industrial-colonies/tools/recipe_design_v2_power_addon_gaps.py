#!/usr/bin/env python3
"""Close audited CreateAddition and Create Diesel Generators acquisition gaps.

This is a pure, idempotent recipe-design-v2 seed transform.  The installed
Create Crafts & Additions machinery is treated as an add-on to the canonical
TFMG electrical system, while Create Diesel Generators may contribute unique
engines, fermentation, mobile storage, and factory-defense utilities.

Only one useful unmanaged acquisition recipe is replaced here: the mounted
oil barrel.  The stock one-row craft hides a fluid-capable mounted-storage
block inside two iron sheets, so it is rebuilt as an actual sealed steel drum.

Two proven bypass families are retired rather than ported:

* CDG's early Andesite pumpjack and oil scanner duplicate the already-managed
  TFMG petroleum field and pumpjack chain.
* CDG's hand hammer creates late alloy and uranium plates outside the pack's
  casing-gated forming lines.

CreateAddition's alternate generator, motor, capacitor, accumulator, and bare
connector blocks stay inaccessible because the corresponding TFMG components
and cable endpoints are canonical.  Unique CreateAddition machines and
endpoints are managed by the existing electrical coverage modules.

``apply`` mutates only the dictionary supplied by its caller.  Importing this
module performs no file writes, registry scans, builds, or runtime tests.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Iterable


Recipe = dict[str, Any]
_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


_MANAGED_RECIPES: tuple[Recipe, ...] = (
    {
        "id": "industrial_colonies:power_addon_gaps/oil_barrel",
        "node": "CR01 — Diesel Processing",
        "phase": "Steel & Petroleum",
        "order": 346,
        "type": "shaped",
        "comment": (
            "Clad a wooden barrel as a sealed mobile oil drum with heavy steel "
            "cheeks, rubber gaskets, and a pressure-service TFMG valve"
        ),
        "pattern": [" H ", "RBR", "HVH"],
        "key": {
            "H": "tfmg:heavy_plate",
            "R": "tfmg:rubber_sheet",
            "B": "minecraft:barrel",
            "V": "tfmg:steel_fluid_valve",
        },
        "output": "createdieselgenerators:oil_barrel",
        "remove": ["createdieselgenerators:crafting/oil_barrel"],
        "exclusive_output": True,
    },
)


# These are not alternate routes worth teaching.  They either duplicate the
# pack's TFMG-first system or bypass a deliberately manufactured plate chain.
_RETIRED_OUTPUTS: dict[str, tuple[str, ...]] = {
    # CreateAddition electrical duplicates.  Their stock acquisitions were
    # already disabled by earlier waves; listing them here also prevents a
    # later automatic-coverage pass from silently bringing them back.
    "createaddition:alternator": (
        "createaddition:mechanical_crafting/alternator",
    ),
    "createaddition:electric_motor": (
        "createaddition:mechanical_crafting/electric_motor",
    ),
    "createaddition:capacitor": (
        "createaddition:crafting/capacitor_1",
        "createaddition:crafting/capacitor_2",
    ),
    "createaddition:modular_accumulator": (
        "createaddition:crafting/modular_accumulator",
    ),
    "createaddition:connector": (
        "createaddition:crafting/connector",
    ),
    "createaddition:large_connector": (
        "createaddition:crafting/large_connector",
    ),
    # The TFMG pumpjack is the canonical terrestrial petroleum extractor.
    "createdieselgenerators:oil_scanner": (
        "createdieselgenerators:crafting/oil_scanner",
    ),
    "createdieselgenerators:pumpjack_bearing": (
        "createdieselgenerators:crafting/pumpjack_bearing",
    ),
    "createdieselgenerators:pumpjack_head": (
        "createdieselgenerators:crafting/pumpjack_head",
    ),
    "createdieselgenerators:pumpjack_hole": (
        "createdieselgenerators:crafting/pumpjack_hole",
    ),
    "createdieselgenerators:pumpjack_crank": (
        "createdieselgenerators:mechanical_crafting/pumpjack_crank",
    ),
    # The hand hammer would otherwise flatten steel, nickel, uranium, and
    # several electrical alloys without any casing-gated machine.
    "createdieselgenerators:hammer": (
        "createdieselgenerators:crafting/hammer",
        "createdieselgenerators:hammering/brass_sheet",
        "createdieselgenerators:hammering/copper_sheet",
        "createdieselgenerators:hammering/gold_sheet",
        "createdieselgenerators:hammering/iron_sheet",
        "createdieselgenerators:compat/createaddition/electrum_sheet",
        "createdieselgenerators:compat/createaddition/zinc_sheet",
        "createdieselgenerators:compat/immersiveengineering/aluminum_sheet",
        "createdieselgenerators:compat/immersiveengineering/constantan_sheet",
        "createdieselgenerators:compat/immersiveengineering/electrum_sheet",
        "createdieselgenerators:compat/immersiveengineering/nickel_sheet",
        "createdieselgenerators:compat/immersiveengineering/silver_sheet",
        "createdieselgenerators:compat/immersiveengineering/steel_sheet",
        "createdieselgenerators:compat/immersiveengineering/uranium_sheet",
    ),
}


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed seed field {field!r} must be a list")
    return value


def _append_unique(values: list[Any], additions: Iterable[str]) -> None:
    seen = set(values)
    for value in additions:
        if value not in seen:
            values.append(value)
            seen.add(value)


def _item_id(value: Any) -> str | None:
    if isinstance(value, str):
        match = _COUNTED_ITEM.fullmatch(value)
        return match.group(1) if match else value.strip()
    if isinstance(value, dict):
        identifier = value.get("id") or value.get("item")
        return identifier if isinstance(identifier, str) else None
    return None


def _declared_outputs(recipe: Recipe) -> set[str]:
    outputs: set[str] = set()
    for field in ("output", "result"):
        identifier = _item_id(recipe.get(field))
        if identifier:
            outputs.add(identifier)
    for field in ("results", "outputs"):
        values = recipe.get(field, [])
        if not isinstance(values, list):
            continue
        for value in values:
            identifier = _item_id(value)
            if identifier:
                outputs.add(identifier)
    return outputs


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = _require_list(data, "recipes")
    matches = [
        index
        for index, current in enumerate(recipes)
        if isinstance(current, dict) and current.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"managed recipe is duplicated: {recipe['id']}")
    if matches:
        recipes[matches[0]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def _assert_no_output_collisions(data: dict[str, Any]) -> None:
    owned_ids = {recipe["id"] for recipe in _MANAGED_RECIPES}
    wanted = {
        output
        for recipe in _MANAGED_RECIPES
        for output in _declared_outputs(recipe)
    }
    conflicts: list[tuple[str, str]] = []
    for recipe in _require_list(data, "recipes"):
        if not isinstance(recipe, dict):
            raise TypeError("managed recipe entries must be objects")
        recipe_id = recipe.get("id")
        if recipe_id in owned_ids:
            continue
        for output in sorted(_declared_outputs(recipe) & wanted):
            conflicts.append((output, str(recipe_id)))
    if conflicts:
        rendered = ", ".join(
            f"{output} via {recipe_id}" for output, recipe_id in conflicts
        )
        raise ValueError(f"power add-on coverage overlaps an output: {rendered}")


def apply(data: dict[str, Any]) -> None:
    """Apply the audited power-add-on recipe gap closure in place."""

    _assert_no_output_collisions(data)
    for recipe in _MANAGED_RECIPES:
        _upsert(data, recipe)

    managed_stock_ids = {
        stock_id
        for recipe in _MANAGED_RECIPES
        for stock_id in recipe.get("remove", [])
    }
    retired_stock_ids = {
        stock_id
        for stock_ids in _RETIRED_OUTPUTS.values()
        for stock_id in stock_ids
    }

    preserve_recipe_ids = _require_list(data, "preserve_recipe_ids")
    preserve_recipe_ids[:] = [
        recipe_id
        for recipe_id in preserve_recipe_ids
        if recipe_id not in managed_stock_ids | retired_stock_ids
    ]

    additional_removals = _require_list(data, "additional_removals")
    # A managed card owns its replaced stock ID locally.  Global removals are
    # reserved for inaccessible duplicate outputs and bypass process recipes.
    additional_removals[:] = [
        recipe_id
        for recipe_id in additional_removals
        if recipe_id not in managed_stock_ids
    ]
    _append_unique(additional_removals, sorted(retired_stock_ids))

    exclude_outputs = _require_list(data, "exclude_outputs")
    managed_outputs = {
        output
        for recipe in _MANAGED_RECIPES
        for output in _declared_outputs(recipe)
    }
    exclude_outputs[:] = [
        output for output in exclude_outputs if output not in managed_outputs
    ]
    _append_unique(exclude_outputs, sorted(_RETIRED_OUTPUTS))

