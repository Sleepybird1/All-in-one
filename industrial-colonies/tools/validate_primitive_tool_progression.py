#!/usr/bin/env python3
"""Static contract checks for the Primitive Age tool entry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java"
SCRIPT = ROOT / "pack-scripts/server_scripts/industrial_primitive_tool_progression.js"
MODEL = ROOT / "src/main/resources/assets/industrial_colonies/models/item/crude_flint_pickaxe.json"
TAG = ROOT / "src/main/resources/data/minecraft/tags/item/pickaxes.json"
LANG = ROOT / "src/main/resources/assets/industrial_colonies/lang/en_us.json"
MANIFEST = ROOT / "progression/managed_recipe_overhaul.json"
COMPILED = ROOT / "pack-kjsgen/default.managed.json"

ALTERNATE_STANDALONE_TOOL_RECIPES = {
    *(f"ae2:tools/certus_quartz_{kind}" for kind in ("axe", "hoe", "pickaxe", "sword")),
    "ae2:tools/certus_quartz_spade",
    *(f"ae2:tools/fluix_{kind}" for kind in ("axe", "hoe", "pickaxe", "shovel", "sword")),
    *(f"ae2:tools/nether_quartz_{kind}" for kind in ("axe", "hoe", "pickaxe", "sword")),
    "ae2:tools/nether_quartz_spade",
    *(
        f"tfmg:crafting/materials/{material}_{kind}"
        for material in ("aluminum", "lead", "steel")
        for kind in ("axe", "hoe", "pickaxe", "shovel", "sword")
    ),
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    for path in (ITEMS, SCRIPT, MODEL, TAG, LANG, MANIFEST, COMPILED):
        require(path.is_file(), f"missing {path.relative_to(ROOT)}", errors)
    if errors:
        return fail(errors)

    items = ITEMS.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    tag = json.loads(TAG.read_text(encoding="utf-8"))
    lang = json.loads(LANG.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    compiled = json.loads(COMPILED.read_text(encoding="utf-8-sig"))

    for token in (
        '"crude_flint_pickaxe"',
        "new SimpleTier(",
        "BlockTags.INCORRECT_FOR_STONE_TOOL",
        "48,",
        "2.5F,",
        "Ingredient.of(Items.FLINT)",
        "new PickaxeItem(",
    ):
        require(token in items, f"primitive item registration lacks {token!r}", errors)

    for material in ("wooden", "stone", "iron", "golden", "diamond"):
        require(material in script, f"tool-removal list lacks {material}", errors)
    for kind in ("pickaxe", "axe", "shovel", "hoe", "sword"):
        require(kind in script, f"tool-removal list lacks {kind}", errors)
    for token in (
        "minecraft:netherite_${kind}_smithing",
        "BlockEvents.broken(id, event => event.player.give('minecraft:stick'))",
        "'minecraft:stick_from_bamboo_item'",
        "quark:tweaks/crafting/utility/misc/easy_sticks",
        "quark:tweaks/crafting/utility/misc/easy_sticks_bamboo",
        "quark:tweaks/crafting/utility/better_stone_tools/${kind}",
        "apotheosis:smithing/upgrade_stone_${kind}_to_iron_${kind}",
        "apotheosis:smithing/upgrade_iron_${kind}_to_golden_${kind}",
        "apotheosis:smithing/upgrade_golden_${kind}_to_diamond_${kind}",
        "industrial_colonies:primitive/crude_flint_pickaxe",
        "modernfoundry:tables/part_builder",
        "modernfoundry:tables/tinker_station",
        "industrial_colonies:primitive/copper_part_builder",
        "industrial_colonies:primitive/copper_tinker_station",
        "type: 'hilt:crafting_shaped_retextured'",
        "w: { tag: 'modernfoundry:planklike' }",
        "pattern: ['pp', 'w ']",
        "pattern: ['ppp', 'w w', 'w w']",
        "texture: 'w'",
        "'FFF'",
        "'minecraft:flint'",
        "'minecraft:stick'",
    ):
        require(token in script, f"primitive recipe script lacks {token!r}", errors)

    require("    'minecraft:stick'," not in script, "native plank stick recipe must remain available", errors)

    require("minecraft:copper_ingot" not in script, "starting stations must not require the first cast copper ingot", errors)

    for leaf in (
        "oak", "spruce", "birch", "jungle", "acacia", "dark_oak",
        "mangrove", "cherry", "azalea", "flowering_azalea",
    ):
        require(f"minecraft:{leaf}_leaves" in script, f"leaf-stick fallback lacks {leaf}", errors)

    require(model.get("parent") == "minecraft:item/handheld", "pickaxe model is not handheld", errors)
    require(
        model.get("textures", {}).get("layer0") == "minecraft:item/stone_pickaxe",
        "temporary crude pickaxe texture reference changed",
        errors,
    )
    require(tag.get("replace") is False, "pickaxes tag must merge, not replace", errors)
    require(
        "industrial_colonies:crude_flint_pickaxe" in tag.get("values", []),
        "crude pickaxe is absent from minecraft:pickaxes",
        errors,
    )
    require(
        lang.get("item.industrial_colonies.crude_flint_pickaxe") == "Crude Flint Pickaxe",
        "missing crude pickaxe translation",
        errors,
    )

    manifest_removals = {
        str(value)
        for value in manifest.get("additional_removals", [])
        if isinstance(value, str)
    }
    compiled_removals = {
        str(entry.get("recipeId"))
        for entry in compiled.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }
    for label, removals in (
        ("managed manifest", manifest_removals),
        ("compiled KJSGen project", compiled_removals),
    ):
        missing = sorted(ALTERNATE_STANDALONE_TOOL_RECIPES - removals)
        require(
            not missing,
            f"{label} leaves AE2/TFMG standalone tool shortcuts: {missing}",
            errors,
        )

    if errors:
        return fail(errors)
    print(
        "PASS: Primitive Age owns a low-durability stone-harvest flint pickaxe, "
        "removes ordinary vanilla and 30 AE2/TFMG standalone tool recipes, and "
        "closes Quark's stick shortcut."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("FAIL: Primitive Age tool progression")
    for error in errors:
        print(f" - {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
