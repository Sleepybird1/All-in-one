#!/usr/bin/env python3
"""Add non-Apotheosis Create Enchantment Industry manufacturing coverage.

The installed 2.4.2 JAR exposes two distinct feature groups.  Gem cutting,
the Infuser, adjustable bookshelves, the Ender Woven Bag, and affix machinery
live in explicit Apotheosis/Apothic Enchanting integration packages.  This
module deliberately leaves those outputs and their recipes untouched.

The recipes below cover the independent liquid-XP enchanting workshop:
blank and super templates, the handbook, Blaze Enchanter, Blaze Forger, and
the continuously automated Classic Blaze Enchanter.  They use recognizable
Brass precision-line sequences and one compact handbook shape; there are no
5x5 rings, decorative intermediates, or XP-storage conversion recipes.
"""

from __future__ import annotations

import re
from typing import Any


BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"


# Functional, but explicitly outside this recipe slice because their classes
# and installed recipes are coupled to Apotheosis or Apothic Enchanting.
APOTHEOSIS_COUPLED_OUTPUTS = frozenset(
    {
        "create_enchantment_industry:affix_augmentor",
        "create_enchantment_industry:apotheotic_affix_template",
        "create_enchantment_industry:apotheotic_essence_bucket",
        "create_enchantment_industry:brass_affix_template",
        "create_enchantment_industry:brass_bookshelf",
        "create_enchantment_industry:creative_bookshelf",
        "create_enchantment_industry:crystal_affix_template",
        "create_enchantment_industry:crystal_essence_bucket",
        "create_enchantment_industry:ender_woven_bag",
        "create_enchantment_industry:gem_cutter",
        "create_enchantment_industry:infused_dragon_breath_bucket",
        "create_enchantment_industry:infuser",
    }
)


# These reversible storage/food/transitional items remain stock.  None is a
# machine gate in this coverage wave.
UTILITY_LOOP_OUTPUTS = frozenset(
    {
        "create_enchantment_industry:experience_cake",
        "create_enchantment_industry:experience_cake_base",
        "create_enchantment_industry:experience_cake_slice",
        "create_enchantment_industry:super_experience_block",
        "create_enchantment_industry:super_experience_nugget",
    }
)


TRANSITIONAL_OUTPUTS = frozenset(
    {
        "create_enchantment_industry:grindstone_drain",
        "create_enchantment_industry:incomplete_brass_bookshelf",
    }
)


COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    if isinstance(value, str):
        raw = value.strip()
        counted = COUNTED_ITEM.fullmatch(raw)
        return counted.group(1) if counted else raw
    if isinstance(value, dict):
        identifier = value.get("id") or value.get("item")
        return identifier if isinstance(identifier, str) else None
    return None


def _deploy(ingredient: str) -> dict[str, str]:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": BRASS_DEPLOYER,
    }


def _press() -> dict[str, str]:
    return {"op": "pressing", "machine": BRASS_PRESS}


def _sequence(
    *,
    recipe_id: str,
    phase: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    remove: str,
    loops: int = 1,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": loops,
        "steps": [_deploy(ingredient) for ingredient in ingredients] + [_press()],
        "remove": [remove],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = depends_on
    return recipe


def _recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            recipe_id="industrial_colonies:enchantment_industry/enchanting_template",
            phase="Steam & Brass",
            order=700,
            comment=(
                "Laminate two layers of lapis and condensed experience into paper, "
                "then Brass-press a reusable blank enchanting record"
            ),
            input_item="minecraft:paper",
            output="create_enchantment_industry:enchanting_template",
            ingredients=["minecraft:lapis_lazuli", "create:experience_nugget"],
            loops=2,
            remove="create_enchantment_industry:pressing/enchanting_template",
        ),
        {
            "id": "industrial_colonies:enchantment_industry/blazes_enchanting_handbook",
            "phase": "Steam & Brass",
            "order": 710,
            "type": "shaped",
            "comment": (
                "Bind a blaze-resistant operating manual around an experience vial, "
                "lapis notation, and the dungeon-sourced Blaze Upgrade template"
            ),
            "pattern": ["SES", "LBL", " T "],
            "key": {
                "S": "create:sturdy_sheet",
                "E": "minecraft:experience_bottle",
                "L": "minecraft:lapis_lazuli",
                "B": "minecraft:book",
                "T": "create_dragons_plus:blaze_upgrade_smithing_template",
            },
            "output": "create_enchantment_industry:blazes_enchanting_handbook",
            "remove": [
                "create_enchantment_industry:crafting/blazes_enchanting_handbook"
            ],
            "exclusive_output": True,
        },
        _sequence(
            recipe_id="industrial_colonies:enchantment_industry/blaze_enchanter",
            phase="Steam & Brass",
            order=720,
            comment=(
                "Convert an Enchanting Table into a liquid-XP production machine by "
                "installing its Blaze heat source, upgrade die, Spout inlet, and "
                "precision level controller"
            ),
            input_item="minecraft:enchanting_table",
            output="create_enchantment_industry:blaze_enchanter",
            ingredients=[
                "create:blaze_burner",
                "create_dragons_plus:blaze_upgrade_smithing_template",
                "create:spout",
                "create:precision_mechanism",
            ],
            remove="create_enchantment_industry:smithing/blaze_enchanter",
        ),
        _sequence(
            recipe_id="industrial_colonies:enchantment_industry/blaze_forger",
            phase="Steam & Brass",
            order=730,
            comment=(
                "Rebuild an Anvil as a liquid-XP forging station around a captured "
                "Blaze, the upgrade die, a complete Mechanical Press ram, and a "
                "sturdy heat shield"
            ),
            input_item="minecraft:anvil",
            output="create_enchantment_industry:blaze_forger",
            ingredients=[
                "create:blaze_burner",
                "create_dragons_plus:blaze_upgrade_smithing_template",
                "create:mechanical_press",
                "create:sturdy_sheet",
            ],
            remove="create_enchantment_industry:smithing/blaze_forger",
        ),
        _sequence(
            recipe_id="industrial_colonies:enchantment_industry/super_enchanting_template",
            phase="Digital Logistics",
            order=540,
            comment=(
                "Upgrade a blank template with an Ancient City Echo Shard, a full "
                "experience reservoir, a lapis matrix, and a sturdy backing before "
                "the final Brass precision press"
            ),
            input_item="create_enchantment_industry:enchanting_template",
            output="create_enchantment_industry:super_enchanting_template",
            ingredients=[
                "minecraft:echo_shard",
                "create:experience_block",
                "minecraft:lapis_block",
                "create:sturdy_sheet",
            ],
            remove="create_enchantment_industry:pressing/super_enchanting_template",
            depends_on=[
                "industrial_colonies:enchantment_industry/enchanting_template"
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:enchantment_industry/classic_blaze_enchanter",
            phase="Digital Logistics",
            order=550,
            comment=(
                "Upgrade the manual Blaze Enchanter for continuous template-driven "
                "work with its handbook, a Mechanical Arm, a populated TFMG board, "
                "and a kinetic Stress Processor"
            ),
            input_item="create_enchantment_industry:blaze_enchanter",
            output="create_enchantment_industry:classic_blaze_enchanter",
            ingredients=[
                "create_enchantment_industry:blazes_enchanting_handbook",
                "create:mechanical_arm",
                "tfmg:circuit_board",
                "appliedcreate:stress_processor",
            ],
            remove="create_enchantment_industry:smithing/classic_blaze_enchanter",
            depends_on=[
                "industrial_colonies:enchantment_industry/blaze_enchanter",
                "industrial_colonies:enchantment_industry/blazes_enchanting_handbook",
                "industrial_colonies:electronics/stress_processor",
            ],
        ),
    ]


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed recipe seed field {field!r} must be a list")
    return value


def _assert_unclaimed(data: dict[str, Any], additions: list[dict[str, Any]]) -> None:
    addition_ids = {recipe["id"] for recipe in additions}
    wanted_outputs = {
        _item_id(recipe.get("output")): recipe["id"] for recipe in additions
    }
    wanted_removals = {
        removal: recipe["id"]
        for recipe in additions
        for removal in recipe.get("remove", [])
    }

    forbidden = (
        APOTHEOSIS_COUPLED_OUTPUTS | UTILITY_LOOP_OUTPUTS | TRANSITIONAL_OUTPUTS
    ).intersection(output for output in wanted_outputs if output is not None)
    if forbidden:
        raise ValueError(
            "Enchantment Industry coverage claimed excluded outputs: "
            + ", ".join(sorted(forbidden))
        )

    for existing in _require_list(data, "recipes"):
        if not isinstance(existing, dict):
            raise TypeError("managed recipe entries must be objects")
        if existing.get("id") in addition_ids:
            continue
        output = _item_id(existing.get("output"))
        if output in wanted_outputs:
            raise ValueError(
                f"{wanted_outputs[output]} cannot claim {output}; "
                f"it is already managed by {existing.get('id')}"
            )
        for removal in existing.get("remove", []):
            if removal in wanted_removals:
                raise ValueError(
                    f"{wanted_removals[removal]} cannot remove {removal}; "
                    f"it is already owned by {existing.get('id')}"
                )

    removal_conflicts = set(wanted_removals).intersection(
        _require_list(data, "additional_removals")
    )
    if removal_conflicts:
        raise ValueError(
            "Enchantment Industry stock removals are already globally claimed: "
            + ", ".join(sorted(removal_conflicts))
        )

    preserve_conflicts = set(wanted_removals).intersection(
        _require_list(data, "preserve_recipe_ids")
    )
    if preserve_conflicts:
        raise ValueError(
            "Enchantment Industry coverage cannot remove preserved recipes: "
            + ", ".join(sorted(preserve_conflicts))
        )

    output_conflicts = set(wanted_outputs).intersection(
        _require_list(data, "exclude_outputs")
    )
    if output_conflicts:
        raise ValueError(
            "Enchantment Industry outputs are excluded from managed coverage: "
            + ", ".join(sorted(str(value) for value in output_conflicts))
        )


def _upsert(data: dict[str, Any], recipe: dict[str, Any]) -> None:
    recipes = _require_list(data, "recipes")
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


def apply(data: dict[str, Any]) -> None:
    """Apply curated, non-Apotheosis CEI recipes without filesystem access."""

    additions = _recipes()
    _assert_unclaimed(data, additions)
    for recipe in additions:
        _upsert(data, recipe)
