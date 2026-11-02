#!/usr/bin/env python3
"""Preserve the user's live recipe edits as design-v3 reference recipes.

The first two recipes were edited in KJSGen while the design-v2 source was still
being generated.  Keeping them in a late, idempotent transform makes the source
of truth agree with the designs the user approved in-game:

* the TFMG spark-ignition cylinder is a compacted Industrial Iron subassembly;
* the Chunk Controller is a late 5x5 control computer and no longer consumes
  Spatial Anchors.  It instead becomes an ingredient of the Spatial Anchor.

The same late transform also retains the already-deployed Winding Machine.  It
is a real early-electrical progression dependency, not an orphaned stock-copy,
and its exact 5x5 electromechanical layout is already present in the live pack.

The module only mutates an in-memory seed.  It does not write files or touch the
live instance.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]


ENGINE_CYLINDER: Recipe = {
    "id": "industrial_colonies:tfmg_heavy_electrical/engine_cylinder",
    # Industrial Iron is the late machine-building environment in the v3
    # casing hierarchy, so this approved process belongs in High-Energy Grid.
    "phase": "High-Energy Grid",
    "order": 1100,
    "type": "compacting",
    "comment": (
        "Compact a diesel cylinder, spark plug, copper ignition lead, and paired "
        "fasteners into the finished multi-fuel spark-ignition cylinder on the "
        "Industrial Iron machine line."
    ),
    "machine": "createcasing:industrial_iron_press",
    "inputs": [
        "tfmg:diesel_engine_cylinder",
        "tfmg:spark_plug",
        "tfmg:copper_wire",
        "2x tfmg:screw",
    ],
    "output": {
        "kind": "ITEM",
        "id": "tfmg:engine_cylinder",
        "components": (
            '[tfmg:fuel_tags={"gasoline":"c:gasoline",'
            '"kerosene":"c:kerosene","naphtha":"c:naphtha"},'
            'tfmg:fuels={"gasoline":"Gasoline","kerosene":"Kerosene",'
            '"naphtha":"Naphtha"}]'
        ),
    },
    "remove": ["tfmg:engine_cylinder_spark_plug"],
    # TFMG deliberately retains its LPG conversion recipe for this same item.
    "exclusive_output": False,
    "depends_on": [
        "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder",
        "industrial_colonies:tfmg_coverage/spark_plug",
    ],
}


CHUNK_CONTROLLER: Recipe = {
    "id": "industrial_colonies:world_loading/chunk_controller",
    "phase": "High-Energy Grid",
    "order": 220,
    "type": "mechanical_crafting",
    "comment": (
        "Build the world-loading control computer around an Ultimate Energy "
        "Cube, Ultimate Control Circuit, redundant wireless links, atomic "
        "conductors, and a Vibranium field stabilizer.  Spatial Anchors consume "
        "this controller later; the dependency never points backward."
    ),
    "pattern": [
        "AEPEA",
        "EWUWE",
        "PCBCP",
        "EWVWE",
        "AEPEA",
    ],
    "key": {
        "A": "mekanism:alloy_atomic",
        "E": "minecraft:ender_eye",
        "P": "ae2:engineering_processor",
        "W": "computercraft:wireless_modem_advanced",
        "U": "mekanism:ultimate_control_circuit",
        "C": "computercraft:computer_advanced",
        "B": "mekanism:ultimate_energy_cube",
        "V": "allthemodium:vibranium_ingot",
    },
    "output": "advancedperipherals:chunk_controller",
    "remove": ["advancedperipherals:chunk_controller"],
    "exclusive_output": True,
    "depends_on": [
        "industrial_colonies:mekanism/storage/ultimate_energy_cube",
        "industrial_colonies:mekanism/ultimate_control_circuit",
        "industrial_colonies:computercraft/computer/advanced_upgrade",
    ],
}


WINDING_MACHINE: Recipe = {
    "id": "industrial_colonies:heavy_industry/winding_machine",
    "phase": "Electrical Manufacturing",
    "order": 135,
    "type": "mechanical_crafting",
    "comment": (
        "Build the electromechanical Winding Machine without consuming "
        "downstream electronics"
    ),
    "pattern": [
        "SHAHS",
        "SCCCS",
        "HMMMH",
        "SCTCS",
        "SHAHS",
    ],
    "key": {
        "S": "#c:ingots/steel",
        "H": "tfmg:heavy_plate",
        "A": "create:shaft",
        "C": "tfmg:copper_spool",
        "M": "tfmg:heavy_machinery_casing",
        "T": "tfmg:steel_mechanism",
    },
    "output": "tfmg:winding_machine",
    "remove": ["tfmg:crafting/materials/winding_machine"],
    "exclusive_output": True,
}


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


def _release_stock_ownership(data: dict[str, Any], recipes: list[Recipe]) -> None:
    claimed = {
        str(stock)
        for recipe in recipes
        for stock in recipe.get("remove", [])
    }
    additional = _require_list(data, "additional_removals")
    additional[:] = [stock for stock in additional if str(stock) not in claimed]
    preserved = _require_list(data, "preserve_recipe_ids")
    preserved[:] = [stock for stock in preserved if str(stock) not in claimed]


def apply(data: dict[str, Any]) -> None:
    """Apply the approved live references without creating output duplicates."""

    recipes = [ENGINE_CYLINDER, CHUNK_CONTROLLER, WINDING_MACHINE]
    _release_stock_ownership(data, recipes)
    for recipe in recipes:
        _upsert(data, recipe)

    # The approved Industrial Iron binding necessarily moves both consumers of
    # the spark-ignition cylinder with it.  Leaving them before High-Energy Grid
    # would advertise engines before the machine that can form their cylinders.
    consumer_orders = {
        "industrial_colonies:engines/radial_engine": 1110,
        "industrial_colonies:simulated/engine_assembly": 1120,
        "industrial_colonies:simulated/portable_engine": 1130,
    }
    indexed = {
        str(recipe.get("id")): recipe
        for recipe in _require_list(data, "recipes")
        if isinstance(recipe, dict)
    }
    for identity, order in consumer_orders.items():
        recipe = indexed.get(identity)
        if recipe is None:
            raise KeyError(f"approved cylinder consumer is missing: {identity}")
        recipe.pop("node", None)
        recipe["phase"] = "High-Energy Grid"
        recipe["order"] = order
        dependencies = recipe.setdefault("depends_on", [])
        if "industrial_colonies:tfmg_heavy_electrical/engine_cylinder" not in dependencies:
            dependencies.append(
                "industrial_colonies:tfmg_heavy_electrical/engine_cylinder"
            )
