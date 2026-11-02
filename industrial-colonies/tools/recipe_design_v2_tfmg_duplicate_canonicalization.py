"""Canonicalize duplicate electrical and structural parts onto TFMG.

TFMG is the pack's canonical electrical manufacturing vocabulary.  Electro
Energetics still owns its grid connectors, wire-placement spools, meters,
transformers, switches, and high-voltage equipment, but its duplicate loose
components must not form a cheaper parallel bill of materials.

This late seed transform therefore:

* retires craftability of the duplicate EE capacitor, resistor, accumulator,
  magnet, diode, potentiometer, and stator;
* rewrites managed consumers to the matching TFMG parts;
* keeps the EE copper-wire spool craftable because it is the mod's actual
  wire-placement tool, while replacing it with ``tfmg:copper_spool`` in the
  reviewed recipes where it was only an internal winding;
* preserves access to the unique EE redstone potentiometer, inductor, and
  coloured grid motors through small TFMG-first bridge recipes.

Importing this module has no filesystem side effects.  ``apply`` is
idempotent and mutates only the supplied seed dictionary.
"""

from __future__ import annotations

import re
from collections.abc import MutableMapping
from typing import Any


COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"

_COUNTED_ITEM = re.compile(r"^(\s*\d+x\s+)([^\s]+)(\s*)$")


# Exact duplicate component identities.  EE's copper-wire spool is
# intentionally absent: it is a functional wire-placement spool, not merely a
# duplicate component, and remains obtainable from the dedicated grid line.
CANONICAL_COMPONENTS: dict[str, str] = {
    "electroenergetics:capacitor": "tfmg:capacitor_item",
    "electroenergetics:resistor": "tfmg:resistor",
    "electroenergetics:accumulator": "tfmg:accumulator",
    "electroenergetics:magnet": "tfmg:magnet",
    "electroenergetics:diode": "tfmg:electric_diode",
    "electroenergetics:potentiometer": "tfmg:potentiometer",
    "electroenergetics:stator": "tfmg:stator",
}

# Mekanism's plain casing block duplicates the pack's canonical TFMG frame.
# Keep this separate from the EE component map so the policy stays explicit.
CANONICAL_STRUCTURES: dict[str, str] = {
    "mekanism:steel_casing": "tfmg:steel_frame",
}

DEPRECATED_OUTPUTS = frozenset(CANONICAL_COMPONENTS)
RETIRED_STRUCTURAL_OUTPUTS = frozenset(CANONICAL_STRUCTURES)
RETIRED_MANAGED_OUTPUTS = DEPRECATED_OUTPUTS | RETIRED_STRUCTURAL_OUTPUTS
RETIRED_DEPENDENCY_IDS = frozenset(
    {
        "industrial_colonies:mekanism/steel_casing",
    }
)

DEPRECATED_STOCK_RECIPES = frozenset(
    {
        "electroenergetics:crafting/capacitor",
        "electroenergetics:crafting/resistor",
        "electroenergetics:crafting/accumulator",
        "electroenergetics:crafting/magnet_block",
        "electroenergetics:crafting/diode",
        "electroenergetics:crafting/potentiometer",
        "electroenergetics:crafting/stator",
    }
)


# These managed uses are all internal windings or BOM components.  Do not make
# this a blind global replacement: EE's spool must remain available for its
# actual wire/network gameplay and future spool-state recipes.
GENERIC_SPOOL_BOM_RECIPE_IDS = frozenset(
    {
        "industrial_colonies:grid/alternator_rotor",
        "industrial_colonies:high_voltage/transformer_core",
        "industrial_colonies:high_voltage/miniature_circuit_breaker",
        "industrial_colonies:high_voltage/transformer",
        "industrial_colonies:high_voltage/voltage_regulator",
        "industrial_colonies:extreme_grid/high_voltage_switch",
        "industrial_colonies:mekanism/transmission/basic_thermodynamic_conductor",
    }
)

MOTOR_COLORS = (
    "black",
    "blue",
    "brown",
    "cyan",
    "gray",
    "green",
    "light_blue",
    "light_gray",
    "lime",
    "magenta",
    "orange",
    "pink",
    "purple",
    "red",
    "white",
    "yellow",
)

DIRECT_GRID_MOTOR_RECIPES = tuple(
    f"electroenergetics:crafting/{color}_electric_motor" for color in MOTOR_COLORS
)
GRID_MOTOR_RECOLOR_RECIPES = tuple(
    f"electroenergetics:crafting/{color}_electric_motor_dye" for color in MOTOR_COLORS
)


def _item_id(value: Any) -> str | None:
    if isinstance(value, MutableMapping):
        identifier = value.get("id")
        return identifier if isinstance(identifier, str) else None
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(2) if match else value.strip()


def _replace_stack(value: Any, replacements: dict[str, str]) -> Any:
    """Replace one exact item stack while preserving a simple count prefix."""

    if isinstance(value, str):
        match = _COUNTED_ITEM.fullmatch(value)
        if match:
            replacement = replacements.get(match.group(2))
            return f"{match.group(1)}{replacement}{match.group(3)}" if replacement else value
        return replacements.get(value.strip(), value)
    if isinstance(value, MutableMapping):
        identifier = value.get("id")
        if isinstance(identifier, str) and identifier in replacements:
            value["id"] = replacements[identifier]
        return value
    if isinstance(value, list):
        for index, entry in enumerate(value):
            value[index] = _replace_stack(entry, replacements)
        return value
    return value


def _rewrite_recipe_materials(
    recipe: MutableMapping[str, Any], replacements: dict[str, str]
) -> None:
    """Rewrite only ingredient-bearing fields, never outputs or recipe IDs."""

    for field in (
        "input",
        "transitional",
        "inputs",
        "ingredients",
        "input1",
        "input2",
        "left",
        "right",
        "gas",
        "infusion",
    ):
        if field in recipe:
            recipe[field] = _replace_stack(recipe[field], replacements)

    key = recipe.get("key")
    if isinstance(key, MutableMapping):
        for symbol, value in list(key.items()):
            key[symbol] = _replace_stack(value, replacements)

    steps = recipe.get("steps")
    if isinstance(steps, list):
        for step in steps:
            if isinstance(step, MutableMapping) and "ingredient" in step:
                step["ingredient"] = _replace_stack(step["ingredient"], replacements)


def _retire_duplicate_managed_outputs(data: MutableMapping[str, Any]) -> set[str]:
    """Remove any managed producer for an explicitly retired duplicate."""

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise ValueError("Recipe seed must contain a recipes list")

    transferred_removals: set[str] = set()
    kept: list[dict[str, Any]] = []
    for recipe in recipes:
        if not isinstance(recipe, dict):
            raise ValueError("Recipe seed contains a non-object recipe")
        if _item_id(recipe.get("output")) in RETIRED_MANAGED_OUTPUTS:
            transferred_removals.update(
                value for value in recipe.get("remove", []) if isinstance(value, str)
            )
            continue
        kept.append(recipe)
    data["recipes"] = kept
    return transferred_removals


def _upsert(data: MutableMapping[str, Any], recipe: dict[str, Any]) -> None:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise ValueError("Recipe seed must contain a recipes list")
    matches = [
        index
        for index, existing in enumerate(recipes)
        if isinstance(existing, dict) and existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"Managed recipe is duplicated: {recipe['id']}")
    if matches:
        recipes[matches[0]] = recipe
    else:
        recipes.append(recipe)


def _bridge_recipes() -> list[dict[str, Any]]:
    return [
        {
            "id": "industrial_colonies:tfmg_canonical/redstone_potentiometer",
            "phase": "Electrical Manufacturing",
            "node": "CR01 — Control Electronics",
            "order": 264,
            "type": "shapeless",
            "comment": (
                "Add redstone control to the canonical TFMG Potentiometer; "
                "the unique EE signal-control block remains available without "
                "reintroducing EE's duplicate potentiometer"
            ),
            "inputs": ["tfmg:potentiometer", "minecraft:redstone_torch"],
            "output": "electroenergetics:redstone_potentiometer",
            "remove": ["electroenergetics:crafting/redstone_potentiometer"],
            "exclusive_output": True,
        },
        {
            "id": "industrial_colonies:tfmg_canonical/grid_inductor",
            "phase": "Electrical Manufacturing",
            "node": "CR01 — Grid Engineering",
            "order": 265,
            "type": "shaped",
            "comment": (
                "Build the unique EE grid inductor around the canonical TFMG "
                "copper winding while retaining EE's network terminals"
            ),
            "pattern": [" I ", "CSC", " I "],
            "key": {
                "I": "#c:plates/iron",
                "C": "electroenergetics:connector",
                "S": "tfmg:copper_spool",
            },
            "output": "electroenergetics:inductor",
            "remove": ["electroenergetics:crafting/inductor"],
            "exclusive_output": True,
        },
        {
            "id": "industrial_colonies:tfmg_canonical/grid_motor_adapter",
            "phase": "Electrical Manufacturing",
            "node": "CR01 — Grid Engineering",
            "order": 268,
            "type": "sequenced_assembly",
            "comment": (
                "Adapt one completed canonical TFMG motor to EE's coloured grid "
                "motor interface; the retained dye conversions provide every "
                "colour without sixteen parallel new-motor recipes"
            ),
            "input": "tfmg:electric_motor",
            "transitional": "tfmg:electric_motor",
            "output": "electroenergetics:white_electric_motor",
            "loops": 1,
            "steps": [
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:commutator",
                    "machine": COPPER_DEPLOYER,
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:connector",
                    "machine": COPPER_DEPLOYER,
                },
                {
                    "op": "deploying",
                    "ingredient": "tfmg:copper_wire",
                    "machine": COPPER_DEPLOYER,
                },
                {
                    "op": "deploying",
                    "ingredient": "minecraft:white_dye",
                    "machine": COPPER_DEPLOYER,
                },
                {"op": "pressing", "machine": COPPER_PRESS},
            ],
            "remove": list(DIRECT_GRID_MOTOR_RECIPES),
            "exclusive_output": True,
            "depends_on": ["industrial_colonies:early_electricity/electric_motor"],
        },
    ]


def _normalize_recipe_id_sets(
    data: MutableMapping[str, Any], transferred_removals: set[str]
) -> None:
    recipes = data.get("recipes", [])
    bridge_ids = {recipe["id"] for recipe in _bridge_recipes()}
    bridge_owned_removals = {
        value
        for recipe in recipes
        if isinstance(recipe, dict) and recipe.get("id") in bridge_ids
        for value in recipe.get("remove", [])
        if isinstance(value, str)
    }

    additional = {
        value
        for value in data.get("additional_removals", [])
        if isinstance(value, str)
    }
    additional.update(DEPRECATED_STOCK_RECIPES)
    additional.update(transferred_removals)
    additional.difference_update(bridge_owned_removals)
    data["additional_removals"] = sorted(additional)

    preserved = {
        value
        for value in data.get("preserve_recipe_ids", [])
        if isinstance(value, str)
    }
    preserved.difference_update(DEPRECATED_STOCK_RECIPES)
    preserved.difference_update(transferred_removals)
    preserved.difference_update(bridge_owned_removals)
    preserved.update(GRID_MOTOR_RECOLOR_RECIPES)
    data["preserve_recipe_ids"] = sorted(preserved)

    excluded = {
        value for value in data.get("exclude_outputs", []) if isinstance(value, str)
    }
    excluded.update(RETIRED_MANAGED_OUTPUTS)
    data["exclude_outputs"] = sorted(excluded)


def _assert_closed(data: MutableMapping[str, Any]) -> None:
    recipes = data.get("recipes", [])
    stale_outputs = sorted(
        {
            _item_id(recipe.get("output"))
            for recipe in recipes
            if isinstance(recipe, dict)
            and _item_id(recipe.get("output")) in RETIRED_MANAGED_OUTPUTS
        }
    )
    if stale_outputs:
        raise ValueError(f"Retired duplicate components regained managed outputs: {stale_outputs}")

    material_refs: list[tuple[str, str]] = []
    for recipe in recipes:
        if not isinstance(recipe, MutableMapping):
            continue
        recipe_id = str(recipe.get("id", ""))
        for field in (
            "input",
            "transitional",
            "inputs",
            "ingredients",
            "input1",
            "input2",
            "left",
            "right",
            "gas",
            "infusion",
        ):
            value = recipe.get(field)
            values = value if isinstance(value, list) else [value]
            for entry in values:
                identifier = _item_id(entry)
                if identifier in RETIRED_MANAGED_OUTPUTS:
                    material_refs.append((recipe_id, identifier))
        key = recipe.get("key")
        if isinstance(key, MutableMapping):
            for entry in key.values():
                identifier = _item_id(entry)
                if identifier in RETIRED_MANAGED_OUTPUTS:
                    material_refs.append((recipe_id, identifier))
        for step in recipe.get("steps", []):
            if isinstance(step, MutableMapping):
                identifier = _item_id(step.get("ingredient"))
                if identifier in RETIRED_MANAGED_OUTPUTS:
                    material_refs.append((recipe_id, identifier))
    if material_refs:
        raise ValueError(f"Managed recipes still consume retired duplicate components: {material_refs}")

    stale_dependencies: list[tuple[str, str]] = []
    for recipe in recipes:
        if not isinstance(recipe, MutableMapping):
            continue
        recipe_id = str(recipe.get("id", ""))
        dependencies = recipe.get("depends_on", [])
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if dependency in RETIRED_DEPENDENCY_IDS:
                stale_dependencies.append((recipe_id, dependency))
    if stale_dependencies:
        raise ValueError(
            "Managed recipes still depend on retired duplicate recipes: "
            f"{stale_dependencies}"
        )


def apply(data: MutableMapping[str, Any]) -> None:
    """Apply the TFMG-first duplicate-component policy in memory."""

    transferred_removals = _retire_duplicate_managed_outputs(data)

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise ValueError("Recipe seed must contain a recipes list")
    for recipe in recipes:
        if not isinstance(recipe, MutableMapping):
            raise ValueError("Recipe seed contains a non-object recipe")
        _rewrite_recipe_materials(recipe, CANONICAL_COMPONENTS)
        _rewrite_recipe_materials(recipe, CANONICAL_STRUCTURES)
        dependencies = recipe.get("depends_on")
        if isinstance(dependencies, list):
            recipe["depends_on"] = [
                dependency
                for dependency in dependencies
                if dependency not in RETIRED_DEPENDENCY_IDS
            ]
        if recipe.get("id") in GENERIC_SPOOL_BOM_RECIPE_IDS:
            _rewrite_recipe_materials(
                recipe,
                {"electroenergetics:copper_wire_spool": "tfmg:copper_spool"},
            )

    ingredient_replacements = data.get("ingredient_replacements")
    if not isinstance(ingredient_replacements, MutableMapping):
        raise ValueError("Recipe seed must contain an ingredient_replacements object")
    for source, target in CANONICAL_STRUCTURES.items():
        existing = ingredient_replacements.get(source)
        if existing is not None and existing != target:
            raise ValueError(
                f"Conflicting structural canonicalization for {source}: {existing}"
            )
        ingredient_replacements[source] = target

    for recipe in _bridge_recipes():
        _upsert(data, recipe)

    _normalize_recipe_id_sets(data, transferred_removals)
    _assert_closed(data)
