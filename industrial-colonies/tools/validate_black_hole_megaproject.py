#!/usr/bin/env python3
"""Validate the renewable-bulk Black Hole and final Industrial Star contract."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JAR = PROJECT_ROOT / "downloads" / "allthecompressed-1.21.1-4.4.0.jar"
DEFAULT_REPORT = (
    PROJECT_ROOT.parent
    / "industrial-audit"
    / "megaprojects"
    / "black_hole_validation.json"
)

OUTPUT_ITEM = "industrial_colonies:black_hole"
RECIPE_ID = "industrial_colonies:megaproject/black_hole"
FINAL_ITEM = "industrial_colonies:industrial_star"
FINAL_RECIPE_ID = "industrial_colonies:megaproject/industrial_star"
RESERVE_CORE = "industrial_colonies:industrial_reserve_core"
UNFINISHED_RESERVE_CORE = "industrial_colonies:unfinished_industrial_reserve_core"
RESERVE_RECIPE_ID = "industrial_colonies:megaproject/industrial_reserve_core"
PATTERN = ["CSG", "DBK", "LOP"]
INGREDIENTS = {
    "C": "allthecompressed:cobblestone_9x",
    "S": "allthecompressed:stone_9x",
    "G": "allthecompressed:gravel_9x",
    "D": "allthecompressed:dirt_9x",
    "B": "allthecompressed:basalt_9x",
    "K": "allthecompressed:blackstone_9x",
    "L": "allthecompressed:oak_log_9x",
    "O": "allthecompressed:sand_9x",
    "P": "allthecompressed:oak_planks_9x",
}
BASE_ITEMS = {
    "cobblestone": "minecraft:cobblestone",
    "stone": "minecraft:stone",
    "gravel": "minecraft:gravel",
    "dirt": "minecraft:dirt",
    "basalt": "minecraft:basalt",
    "blackstone": "minecraft:blackstone",
    "oak_log": "minecraft:oak_log",
    "sand": "minecraft:sand",
    "oak_planks": "minecraft:oak_planks",
}
STAR_PATTERN = ["  A  ", " VAV ", "UBHBU", " VCV ", "  A  "]
STAR_INGREDIENTS = {
    "A": "allthemodium:vibranium_allthemodium_alloy_ingot",
    "V": "allthemodium:unobtainium_vibranium_alloy_ingot",
    "U": "allthemodium:unobtainium_allthemodium_alloy_ingot",
    "B": "mekanism:ultimate_control_circuit",
    "H": OUTPUT_ITEM,
    "C": RESERVE_CORE,
}
RESERVE_LOOPS = 512
HDPE_PER_LOOP = 8
PLUTONIUM_PER_LOOP = 1
ACID_BUCKETS_PER_LOOP = 2
DIESEL_BUCKETS_PER_LOOP = 10
FORBIDDEN_VALUABLE_WORDS = {
    "gold",
    "iron",
    "diamond",
    "emerald",
    "netherite",
    "allthemodium",
    "vibranium",
    "unobtainium",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_recipe(script: str) -> tuple[list[str], dict[str, str]]:
    shaped_match = re.search(
        r"event\.shaped\(\s*Item\.of\('industrial_colonies:black_hole'\)\s*,"
        r"\s*\[([^]]+)\]\s*,\s*\{([^}]+)\}",
        script,
        flags=re.DOTALL,
    )
    require(shaped_match is not None, "Black Hole must use one normal event.shaped recipe")
    pattern = re.findall(r"'([^']+)'", shaped_match.group(1))
    pairs = re.findall(r"([A-Z])\s*:\s*'([^']+)'", shaped_match.group(2))
    return pattern, dict(pairs)


def parse_star_recipe(script: str) -> tuple[list[str], dict[str, str]]:
    pattern_match = re.search(
        r"pattern\s*:\s*\[([^]]+)\]",
        script,
        flags=re.DOTALL,
    )
    require(pattern_match is not None, "Industrial Star mechanical-crafting pattern is missing")
    pattern = re.findall(r"'([^']*)'", pattern_match.group(1))
    pairs = re.findall(r"([A-Z])\s*:\s*\{\s*item\s*:\s*'([^']+)'\s*\}", script)
    return pattern, dict(pairs)


def reserve_machine_routing_errors(script: str) -> list[str]:
    """Reject a Creative-labelled Reserve Core whose inner steps run universally."""

    errors: list[str] = []
    expected_types = {
        "industrial_colonies:creative_deploying": 1,
        "industrial_colonies:creative_pressing": 1,
        # Create Encased has no Creative Spout. Brass is its strongest exact
        # filling machine and keeps every nested operation physically bound.
        "industrial_colonies:brass_filling": 1,
    }
    for recipe_type, expected in expected_types.items():
        actual = script.count(f"type: '{recipe_type}'")
        if actual != expected:
            errors.append(
                f"Reserve Core exact nested type {recipe_type} expected {expected}, found {actual}"
            )
    for recipe_type in ("create:deploying", "create:pressing", "create:filling"):
        if f"type: '{recipe_type}'" in script:
            errors.append(f"Reserve Core contains universal nested step {recipe_type}")
    return errors


def validate(project: Path, compressed_jar: Path) -> dict[str, Any]:
    script_path = project / "pack-scripts" / "server_scripts" / "industrial_black_hole_megaproject.js"
    script = script_path.read_text(encoding="utf-8-sig")
    pattern, ingredients = parse_recipe(script)
    require(pattern == PATTERN, f"Black Hole pattern changed: {pattern}")
    require(ingredients == INGREDIENTS, f"Black Hole ingredient map changed: {ingredients}")
    require(script.count("event.shaped(") == 1, "Black Hole script must define exactly one shaped recipe")
    require(f".id('{RECIPE_ID}')" in script, "Black Hole recipe ID is missing or changed")
    require(len(set(ingredients.values())) == 9, "all nine Black Hole ingredients must be unique")
    require(
        all(item.endswith("_9x") for item in ingredients.values()),
        "every Black Hole ingredient must be a highest-tier 9x compressed block",
    )
    require(
        not any(word in item for item in ingredients.values() for word in FORBIDDEN_VALUABLE_WORDS),
        "Black Hole recipe contains a forbidden valuable metal or gem",
    )

    star_script_path = project / "pack-scripts" / "server_scripts" / "industrial_star_megaproject.js"
    star_script = star_script_path.read_text(encoding="utf-8-sig")
    star_pattern, star_ingredients = parse_star_recipe(star_script)
    require(star_pattern == STAR_PATTERN, f"Industrial Star pattern changed: {star_pattern}")
    require(
        star_ingredients == STAR_INGREDIENTS,
        f"Industrial Star ingredient map changed: {star_ingredients}",
    )
    require(
        star_script.count("type: 'industrial_colonies:creative_mechanical_crafting'") == 1,
        "Industrial Star must have exactly one Creative-tier mechanical-crafting recipe",
    )
    require("event.shaped(" not in star_script, "Industrial Star must not be a normal 3x3 recipe")
    require(f".id('{FINAL_RECIPE_ID}')" in star_script, "Industrial Star recipe ID changed")

    reserve_script_path = (
        project / "pack-scripts" / "server_scripts" / "industrial_reserve_core_megaproject.js"
    )
    reserve_script = reserve_script_path.read_text(encoding="utf-8-sig")
    routing_errors = reserve_machine_routing_errors(reserve_script)
    require(not routing_errors, "; ".join(routing_errors))
    loops_match = re.search(r"loops\s*:\s*(\d+)", reserve_script)
    require(loops_match is not None, "Reserve Core loop count is missing")
    reserve_loops = int(loops_match.group(1))
    require(reserve_loops == RESERVE_LOOPS, f"Reserve Core loop count changed: {reserve_loops}")
    inner_loop_counts = [int(value) for value in re.findall(r"index\s*<\s*(\d+)", reserve_script)]
    require(
        inner_loop_counts == [HDPE_PER_LOOP, ACID_BUCKETS_PER_LOOP, DIESEL_BUCKETS_PER_LOOP],
        f"Reserve Core per-loop input counts changed: {inner_loop_counts}",
    )
    require(
        "sequence.push(deploying('mekanism:pellet_plutonium'))" in reserve_script,
        "Reserve Core plutonium deployment is missing",
    )
    require(
        "sequence.push(filling('tfmg:sulfuric_acid'))" in reserve_script,
        "Reserve Core acid filling is missing",
    )
    require(
        "sequence.push(filling('tfmg:diesel'))" in reserve_script,
        "Reserve Core diesel filling is missing",
    )
    require(
        "ingredient: { item: 'mekanism:ultimate_control_circuit' }" in reserve_script,
        "Reserve Core seed item changed",
    )
    require(
        reserve_script.count("type: 'industrial_colonies:creative_sequenced_assembly'") == 1,
        "Reserve Core must have exactly one Creative-tier sequenced-assembly recipe",
    )
    require(f"id: '{RESERVE_CORE}'" in reserve_script, "Reserve Core output is missing")
    require(
        f".id('{RESERVE_RECIPE_ID}')" in reserve_script,
        "Reserve Core recipe ID changed",
    )

    require(compressed_jar.is_file(), f"AllTheCompressed jar is missing: {compressed_jar}")
    with zipfile.ZipFile(compressed_jar) as archive:
        entries = set(archive.namelist())
        for item in ingredients.values():
            namespace, path = item.split(":", 1)
            require(
                f"assets/{namespace}/models/item/{path}.json" in entries,
                f"Black Hole ingredient does not exist in the installed AllTheCompressed version: {item}",
            )
            base_name = path.removesuffix("_9x")
            require(base_name in BASE_ITEMS, f"Black Hole ingredient is not an approved renewable family: {item}")
            for level in range(1, 10):
                recipe_path = f"data/{namespace}/recipe/compress/{base_name}_{level}x.json"
                require(recipe_path in entries, f"compression tier {level} is missing for {item}")
                recipe = json.loads(archive.read(recipe_path).decode("utf-8-sig"))
                expected_input = (
                    BASE_ITEMS[base_name]
                    if level == 1
                    else f"allthecompressed:{base_name}_{level - 1}x"
                )
                require(
                    recipe.get("pattern") == ["###", "###", "###"],
                    f"compression tier {level} is not a full 3x3 for {base_name}",
                )
                require(
                    recipe.get("key", {}).get("#", {}).get("item") == expected_input,
                    f"compression tier {level} has an unexpected input for {base_name}",
                )
                require(
                    recipe.get("result") == {
                        "count": 1,
                        "id": f"allthecompressed:{base_name}_{level}x",
                    },
                    f"compression tier {level} has an unexpected output for {base_name}",
                )

    item_source = (
        project / "src" / "main" / "java" / "dev" / "godpc" / "industrialcolonies" / "IndustrialItems.java"
    ).read_text(encoding="utf-8-sig")
    require('"black_hole"' in item_source, "custom Black Hole item is not registered")
    require('"unfinished_industrial_reserve_core"' in item_source, "unfinished Reserve Core is not registered")
    require('"industrial_reserve_core"' in item_source, "Industrial Reserve Core is not registered")
    require('"industrial_star"' in item_source, "custom Industrial Star item is not registered")
    require("stacksTo(1)" in item_source, "Black Hole must be non-stackable")
    require("fireResistant()" in item_source, "Black Hole must be fire resistant")
    require(
        (project / "src" / "main" / "resources" / "assets" / "industrial_colonies" / "models" / "item" / "black_hole.json").is_file(),
        "Black Hole item model is missing",
    )
    require(
        (project / "src" / "main" / "resources" / "assets" / "industrial_colonies" / "models" / "item" / "industrial_star.json").is_file(),
        "Industrial Star item model is missing",
    )
    for model_name in ("unfinished_industrial_reserve_core", "industrial_reserve_core"):
        require(
            (project / "src" / "main" / "resources" / "assets" / "industrial_colonies" / "models" / "item" / f"{model_name}.json").is_file(),
            f"{model_name} item model is missing",
        )
    language = load_json(
        project / "src" / "main" / "resources" / "assets" / "industrial_colonies" / "lang" / "en_us.json"
    )
    require(language.get("item.industrial_colonies.black_hole") == "Black Hole", "Black Hole name is missing")
    require(
        language.get("item.industrial_colonies.industrial_star") == "Industrial Star",
        "Industrial Star name is missing",
    )
    require(
        language.get("item.industrial_colonies.industrial_reserve_core") == "Industrial Reserve Core",
        "Industrial Reserve Core name is missing",
    )

    quest_config = load_json(project / "progression" / "industrial_megaprojects.json")
    require(
        quest_config.get("chapter", {}).get("title") == "Industrial Endgame",
        "megaprojects must use the non-gating Industrial Endgame chapter",
    )
    require(
        quest_config.get("chapter", {}).get("filename") == "industrial_progression",
        "Industrial Endgame must retain the legacy chapter filename for safe replacement",
    )
    quests = {quest["key"]: quest for quest in quest_config["quests"]}
    require(
        list(quests) == ["black_hole", "industrial_reserves", "industrial_star"],
        f"Industrial Endgame must contain exactly three quests, found {list(quests)}",
    )
    require(
        quests["black_hole"]["dependencies"] == [],
        "Black Hole must be the root endgame objective",
    )
    black_hole_description = quests["black_hole"]["description"]
    require(
        any("3,486,784,401" in line for line in black_hole_description),
        "Black Hole quest must disclose the exact nine-stream material scale",
    )
    require(
        quests["black_hole"]["tasks"] == [{"type": "item", "item": OUTPUT_ITEM, "count": 1}],
        "Black Hole completion task changed",
    )
    require(
        quests["industrial_reserves"]["tasks"]
        == [{"type": "item", "item": RESERVE_CORE, "count": 1}],
        "Industrial Reserves must require the physically manufactured Reserve Core",
    )
    require(
        quests["industrial_reserves"]["dependencies"] == ["black_hole"],
        "Industrial Reserve Core must follow the Black Hole objective",
    )
    reserve_description = quests["industrial_reserves"]["description"]
    require(
        any(
            "1,024,000" in line
            and "5,120,000" in line
            and "4,096" in line
            and "512" in line
            for line in reserve_description
        ),
        "Industrial Reserve Core quest must disclose all exact production totals",
    )
    require(
        quests["industrial_star"]["dependencies"] == ["industrial_reserves"],
        "Industrial Star must follow the Industrial Reserve Core",
    )
    require(
        quests["industrial_star"]["tasks"] == [{"type": "item", "item": FINAL_ITEM, "count": 1}],
        "Industrial Star completion task changed",
    )
    for key, quest in quests.items():
        require(
            len(quest.get("tasks", [])) == 1
            and quest["tasks"][0].get("type") == "item",
            f"{key} must contain exactly one item-observation task",
        )
        require(
            not {"research_dependencies", "stage", "team_stage", "rewards"}.intersection(quest),
            f"{key} contains a legacy progression gate or reward",
        )

    return {
        "status": "PASS",
        "output_item": OUTPUT_ITEM,
        "final_item": FINAL_ITEM,
        "recipe_id": RECIPE_ID,
        "crafting_grid": PATTERN,
        "ingredient_count": 9,
        "ingredients": ingredients,
        "all_ingredients_unique": True,
        "all_ingredients_are_9x": True,
        "verified_compression_recipes": 81,
        "base_blocks_per_9x_item": 9 ** 9,
        "total_base_blocks_across_nine_streams": 9 * (9 ** 9),
        "valuable_ingot_or_gem_count": 0,
        "final_recipe_id": FINAL_RECIPE_ID,
        "final_recipe_ingredients": star_ingredients,
        "all_three_alloy_families_used": True,
        "reserve_core_item": RESERVE_CORE,
        "reserve_core_recipe_id": RESERVE_RECIPE_ID,
        "reserve_core_loops": reserve_loops,
        "reserve_core_totals": {
            "mekanism:hdpe_pellet": reserve_loops * HDPE_PER_LOOP,
            "mekanism:pellet_plutonium": reserve_loops * PLUTONIUM_PER_LOOP,
            "tfmg:sulfuric_acid_mb": reserve_loops * ACID_BUCKETS_PER_LOOP * 1000,
            "tfmg:diesel_mb": reserve_loops * DIESEL_BUCKETS_PER_LOOP * 1000,
        },
        "allthecompressed_jar": str(compressed_jar),
        "progression_gate": "physical_recipe_inputs_only",
        "quest_chapter": "Industrial Endgame",
        "quest_stage_tasks": 0,
        "quest_rewards": 0,
        "black_hole_is_component": True,
        "endgame_quest_count": 3,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--allthecompressed-jar", type=Path, default=DEFAULT_JAR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate(args.project.resolve(), args.allthecompressed_jar.resolve())
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "PASS: Black Hole is the renewable-mass component, the 512-loop Reserve "
        "Core physically consumes the factory reserves, and the 5x5 Industrial Star "
        "is the separate final artifact."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
