#!/usr/bin/env python3
"""Repair hidden manufacturing-environment inversions in the v3 progression.

The ordinary dependency graph sees exact item inputs and selected Create
machines, but two important runtime requirements are implicit:

* TFMG semiconductor vat recipes select the Steel Chemical Vat by ``vat_mode``;
* TFMG silicon needs the Industrial Blast Furnace, whose refractory structure
  must exist before Railway tooling and digital electronics.

This late, idempotent pass keeps that bootstrap on default Create/Copper
tooling, then corrects three late-tier machine selectors found during the
named-recipe review.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

STEEL = "Steel & Petroleum"
ELECTRICAL = "Electrical Manufacturing"


BOOTSTRAP_RECIPES: tuple[Recipe, ...] = (
    {
        "id": "industrial_colonies:steelworks/fireproof_bricks",
        "phase": STEEL,
        "order": 40,
        "type": "compacting",
        "comment": (
            "Use the default Create press to compact four fired refractory "
            "bricks into the first TFMG blast-furnace wall block.  This is a "
            "steel/silicon bootstrap, not a Railway-era upgrade."
        ),
        "machine": "create:mechanical_press",
        "inputs": [
            "tfmg:fireproof_brick",
            "tfmg:fireproof_brick",
            "tfmg:fireproof_brick",
            "tfmg:fireproof_brick",
        ],
        "output": "tfmg:fireproof_bricks",
        "remove": ["tfmg:crafting/materials/fireproof_bricks"],
        "exclusive_output": True,
    },
    {
        "id": "industrial_colonies:steelworks/fireproof_brick_reinforcement",
        "phase": STEEL,
        "order": 50,
        "type": "compacting",
        "comment": (
            "Compact six refractory wall blocks into six load-bearing supports "
            "on the default Create press so the Industrial Blast Furnace can "
            "produce electronics-grade silicon before Railway machinery."
        ),
        "machine": "create:mechanical_press",
        "inputs": ["tfmg:fireproof_bricks"] * 6,
        "output": "6x tfmg:fireproof_brick_reinforcement",
        "remove": ["tfmg:crafting/materials/fireproof_brick_reinforcement"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:steelworks/fireproof_bricks"],
    },
    {
        "id": "industrial_colonies:steelworks/blast_furnace_reinforcement",
        "phase": STEEL,
        "order": 80,
        "type": "compacting",
        "comment": (
            "After the first steel heat, compact steel, Heavy Plates, and "
            "refractory wall blocks into four Industrial Blast Furnace supports "
            "without requiring the later Railway press."
        ),
        "machine": "create:mechanical_press",
        "inputs": [
            "#c:ingots/steel",
            "#c:ingots/steel",
            "#c:ingots/steel",
            "tfmg:heavy_plate",
            "tfmg:heavy_plate",
            "tfmg:heavy_plate",
            "tfmg:fireproof_bricks",
            "tfmg:fireproof_bricks",
            "tfmg:fireproof_bricks",
        ],
        "output": "4x tfmg:blast_furnace_reinforcement",
        "remove": ["tfmg:crafting/materials/blast_furnace_reinforcement"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:steelworks/fireproof_bricks"],
    },
    {
        "id": "industrial_colonies:fluid_infrastructure/steel_chemical_vat",
        "phase": ELECTRICAL,
        "order": 20,
        "type": "sequenced_assembly",
        "comment": (
            "Upgrade the proven Cast-Iron Chemical Vat with TFMG steel, nickel "
            "lining, a pressure valve, redundant cast-iron service piping, "
            "rubber sealing, and extra tank volume on the Copper electronics line."
        ),
        "input": "tfmg:cast_iron_chemical_vat",
        "transitional": "tfmg:cast_iron_chemical_vat",
        "output": "tfmg:steel_chemical_vat",
        "loops": 1,
        "steps": [
            {
                "op": "deploying",
                "ingredient": "2x tfmg:steel_ingot",
                "machine": "createcasing:copper_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "2x tfmg:nickel_sheet",
                "machine": "createcasing:copper_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "tfmg:cast_iron_fluid_valve",
                "machine": "createcasing:copper_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "2x tfmg:cast_iron_pipe",
                "machine": "createcasing:copper_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "tfmg:rubber_sheet",
                "machine": "createcasing:copper_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "tfmg:cast_iron_fluid_tank",
                "machine": "createcasing:copper_deployer",
            },
            {"op": "pressing", "machine": "createcasing:copper_press"},
        ],
        "remove": ["tfmg:crafting/materials/steel_chemical_vat"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:fluid_infrastructure/cast_iron_chemical_vat",
            "industrial_colonies:steelworks/fireproof_bricks",
        ],
    },
)


def _recipes(data: dict[str, Any]) -> list[Recipe]:
    recipes = data.get("recipes")
    if not isinstance(recipes, list) or any(not isinstance(row, dict) for row in recipes):
        raise TypeError("managed seed recipes must be an array of objects")
    return recipes


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = _recipes(data)
    matches = [index for index, row in enumerate(recipes) if row.get("id") == recipe["id"]]
    if len(matches) != 1:
        raise ValueError(
            f"bootstrap recipe must have exactly one existing owner: {recipe['id']} "
            f"(found {len(matches)})"
        )
    recipes[matches[0]] = deepcopy(recipe)


def _patch_existing(data: dict[str, Any]) -> None:
    by_id = {str(recipe.get("id")): recipe for recipe in _recipes(data)}

    # These two physical structure pieces do not select an encased machine;
    # reset their persisted post-alignment phase so the full silicon furnace is
    # available with the refractory bootstrap above.
    for recipe_id in (
        "industrial_colonies:steelworks/blast_stove",
        "industrial_colonies:steelworks/blast_furnace_hatch",
    ):
        recipe = by_id.get(recipe_id)
        if recipe is None:
            raise KeyError(f"TFMG blast-furnace bootstrap recipe is missing: {recipe_id}")
        recipe.pop("node", None)
        recipe["phase"] = STEEL

    selector_patches = {
        "industrial_colonies:nuclear/chromatic_compound": (
            "createcasing:industrial_iron_mixer",
            "Superheat exotic minerals, Yellorium, and grid electronics into "
            "Chromatic Compound in the Industrial Iron mixer that precedes the "
            "Refined Radiance family.",
        ),
        "industrial_colonies:nuclear/refined_radiance": (
            "createcasing:industrial_iron_press",
            "Compress Chromatic Compound, Yellorium alloy, and engineering logic "
            "into Refined Radiance on the immediately preceding Industrial Iron line.",
        ),
        "industrial_colonies:bigreactors/reprocessor/casing": (
            "createcasing:refined_radiance_press",
            "Pressure-seal eight Cyanite-handling reprocessor wall segments on "
            "the nuclear Refined Radiance containment line.",
        ),
    }
    for recipe_id, (machine, comment) in selector_patches.items():
        recipe = by_id.get(recipe_id)
        if recipe is None:
            raise KeyError(f"late selector correction target is missing: {recipe_id}")
        recipe["machine"] = machine
        recipe["comment"] = comment


def audit(data: dict[str, Any]) -> dict[str, Any]:
    by_id = {str(recipe.get("id")): recipe for recipe in _recipes(data)}
    errors: list[str] = []
    expected_machines = {
        "industrial_colonies:steelworks/fireproof_bricks": "create:mechanical_press",
        "industrial_colonies:steelworks/fireproof_brick_reinforcement": "create:mechanical_press",
        "industrial_colonies:steelworks/blast_furnace_reinforcement": "create:mechanical_press",
        "industrial_colonies:nuclear/chromatic_compound": "createcasing:industrial_iron_mixer",
        "industrial_colonies:nuclear/refined_radiance": "createcasing:industrial_iron_press",
        "industrial_colonies:bigreactors/reprocessor/casing": "createcasing:refined_radiance_press",
    }
    for recipe_id, machine in expected_machines.items():
        if by_id.get(recipe_id, {}).get("machine") != machine:
            errors.append(f"{recipe_id} is not bound to {machine}")
    vat = by_id.get("industrial_colonies:fluid_infrastructure/steel_chemical_vat", {})
    vat_machines = {
        step.get("machine")
        for step in vat.get("steps", [])
        if isinstance(step, dict) and step.get("machine")
    }
    if vat.get("type") != "sequenced_assembly" or vat_machines != {
        "createcasing:copper_deployer",
        "createcasing:copper_press",
    }:
        errors.append("Steel Chemical Vat is not a Copper-line sequenced assembly")
    for recipe_id in (
        "industrial_colonies:steelworks/blast_stove",
        "industrial_colonies:steelworks/blast_furnace_hatch",
    ):
        if by_id.get(recipe_id, {}).get("phase") != STEEL:
            errors.append(f"{recipe_id} is not in the Steel bootstrap phase")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors}


def apply(data: dict[str, Any]) -> None:
    for recipe in BOOTSTRAP_RECIPES:
        _upsert(data, recipe)
    _patch_existing(data)
    report = audit(data)
    if report["status"] != "PASS":
        raise AssertionError("v3 progression bootstrap failed: " + "; ".join(report["errors"]))

