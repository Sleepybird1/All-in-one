#!/usr/bin/env python3
"""Validate native FTB Quests factory, exploration, orbital, and planetary guidance.

Validation covers deterministic source/output parity, dependency topology,
installed item/structure/advancement IDs, tangible production paths,
non-consuming item tasks, the absence of rewards/gates/commands, and
preservation of the original three endgame quest IDs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable, Mapping

from generate_ftbquests_native import (
    ENDGAME_FILENAME,
    DESTINATION_SPECIFIC_PATTERN,
    EXPLORATION_FILENAME,
    EXPLORATION_GUIDANCE_TAG,
    EXPECTED_ENDGAME_DEPENDENCIES,
    EXPECTED_ENDGAME_ITEMS,
    EXPECTED_ENDGAME_KEYS,
    EXPECTED_ORBITAL_DEPENDENCIES,
    EXPECTED_ORBITAL_ITEMS,
    EXPECTED_ORBITAL_KEYS,
    EXPECTED_ORBITAL_TASK_ITEMS,
    EXPECTED_ORBITAL_TASK_COUNTS,
    EXPECTED_PLANETARY_KEYS,
    EXPECTED_PLANETARY_DEPENDENCIES,
    EXPECTED_PLANETARY_TASKS,
    ORBITAL_FILENAME,
    ORBITAL_GUIDANCE_TAG,
    PLANETARY_FILENAME,
    PLANETARY_GUIDANCE_TAG,
    PHYSICAL_GUIDANCE_TAG,
    build_artifacts,
    stable_code,
    validate_endgame_source,
    validate_exploration_source,
    validate_guidance_source,
    validate_orbital_source,
    validate_planetary_source,
)
from validate_ftb_post_diesel_guidance_audit import (
    installed_recipe_map as post_diesel_installed_recipe_map,
    validate_plan as validate_post_diesel_plan,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parents[1]
DEFAULT_GUIDANCE_SOURCE = PROJECT_ROOT / "progression" / "ftbquests_guidance_campaign.json"
DEFAULT_EXPLORATION_SOURCE = PROJECT_ROOT / "progression" / "ftbquests_dungeon_exploration.json"
DEFAULT_ENDGAME_SOURCE = PROJECT_ROOT / "progression" / "industrial_megaprojects.json"
DEFAULT_ORBITAL_SOURCE = PROJECT_ROOT / "progression" / "ftbquests_orbital_engineering.json"
DEFAULT_PLANETARY_SOURCE = PROJECT_ROOT / "progression" / "ftbquests_planetary_industry.json"
DEFAULT_QUEST_ROOT = PROJECT_ROOT / "pack-config-overrides" / "ftbquests" / "quests"
DEFAULT_MANIFEST = PROJECT_ROOT.parent / "industrial-audit" / "ftb-quests-layout" / "native_quest_manifest.json"
DEFAULT_REPORT = PROJECT_ROOT.parent / "industrial-audit" / "ftb-quests-layout" / "native_quest_validation.json"
DEFAULT_ITEM_CATALOG = WORKSPACE_ROOT / "exports" / "ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt"
DEFAULT_RECIPE_CATALOG = WORKSPACE_ROOT / "outputs" / "recipe-catalog-current"
DEFAULT_INSTANCE = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one")

EXPECTED_ENDGAME_CHAPTER_ID = "5EAE8C019077D7EF"
EXPECTED_ENDGAME_QUEST_IDS = {
    "black_hole": "4B66DE417E679AE6",
    "industrial_reserves": "3373AEB6F841A026",
    "industrial_star": "00C5B9DFDCC5F502",
}
EXPECTED_ENDGAME_TASK_IDS = {
    "black_hole": "20E484AA707D9B02",
    "industrial_reserves": "151350606F0AEA63",
    "industrial_star": "7E7DE00B68C29219",
}
EXPECTED_CHAPTER_GROUPS_SHA256 = (
    "DCEFA23F7441409DB799365BAC250DC2418800A7B7468B15984C2C866F0CB4CD"
)
EXPECTED_FILES = {
    "chapter_groups.snbt",
    "chapters/factory_foundations.snbt",
    "chapters/dungeon_exploration.snbt",
    "chapters/electrical_manufacturing.snbt",
    "chapters/digital_logistics.snbt",
    "chapters/mekanized_industry.snbt",
    "chapters/high_energy_grid.snbt",
    "chapters/nuclear_engineering.snbt",
    "chapters/industrial_progression.snbt",
    "chapters/orbital_engineering.snbt",
    "chapters/planetary_industry.snbt",
    "data.snbt",
    "lang/en_us.snbt",
}
INSTALLED_STRUCTURE_PATHS = {
    "betterdungeons:small_dungeon": (
        "YungsBetterDungeons-1.21.1-NeoForge-5.1.4.jar",
        "data/betterdungeons/worldgen/structure/small_dungeon.json",
    ),
    "betterdungeons:skeleton_dungeon": (
        "YungsBetterDungeons-1.21.1-NeoForge-5.1.4.jar",
        "data/betterdungeons/worldgen/structure/skeleton_dungeon.json",
    ),
    "betterdungeons:spider_dungeon": (
        "YungsBetterDungeons-1.21.1-NeoForge-5.1.4.jar",
        "data/betterdungeons/worldgen/structure/spider_dungeon.json",
    ),
    "betterdungeons:zombie_dungeon": (
        "YungsBetterDungeons-1.21.1-NeoForge-5.1.4.jar",
        "data/betterdungeons/worldgen/structure/zombie_dungeon.json",
    ),
    "betterdungeons:small_nether_dungeon": (
        "YungsBetterDungeons-1.21.1-NeoForge-5.1.4.jar",
        "data/betterdungeons/worldgen/structure/small_nether_dungeon.json",
    ),
    "dungeoncrawl:dungeon": (
        "DungeonCrawl-NeoForge-1.21-2.3.17.jar",
        "data/dungeoncrawl/worldgen/structure/dungeon.json",
    ),
    "dungeonnowloading:labyrinth": (
        "dungeonnowloading-neoforge-1.21.1-2.11.3.jar",
        "data/dungeonnowloading/worldgen/structure/labyrinth.json",
    ),
    "dungeonnowloading:temple_of_duality": (
        "dungeonnowloading-neoforge-1.21.1-2.11.3.jar",
        "data/dungeonnowloading/worldgen/structure/temple_of_duality.json",
    ),
}
INSTALLED_ADVANCEMENT_PATHS = {
    "betterdungeons:all_dungeons": (
        "YungsBetterDungeons-1.21.1-NeoForge-5.1.4.jar",
        "data/betterdungeons/advancement/all_dungeons.json",
    ),
}
NATIVE_TASK_CLASSES = {
    "dev/ftb/mods/ftbquests/quest/task/StructureTask.class",
    "dev/ftb/mods/ftbquests/quest/task/AdvancementTask.class",
}
EXPLORATION_LOOT_ITEMS = {
    "minecraft:stone_pickaxe": (
        "DungeonCrawl-NeoForge-1.21-2.3.17.jar",
        "data/dungeoncrawl/treasure/stage_1.json",
    )
}
# The static recipe catalog is intentionally built from installed mod JARs and
# therefore omits Mojang's data recipes. Shield is the only task item here that
# relies on an unchanged vanilla crafting recipe rather than a catalogued mod
# or managed producer.
VANILLA_RECIPE_ITEMS = {"minecraft:shield"}
MINED_WORLDGEN_ITEMS = {
    "ad_astra:glacio_ice_shard_ore": (
        "adastra-1.21.1-1.16.22-neoforge.jar",
        "data/ad_astra/loot_table/blocks/glacio_ice_shard_ore.json",
    ),
    "ad_astra:mercury_iron_ore": (
        "adastra-1.21.1-1.16.22-neoforge.jar",
        "data/ad_astra/loot_table/blocks/mercury_iron_ore.json",
    ),
    "rocketnautics:titanium_ore": (
        "cosmonautics-26.08.307.jar",
        "data/rocketnautics/loot_table/blocks/titanium_ore.json",
    ),
}
FORBIDDEN_KEYS = {
    "command",
    "gamestage",
    "research_dependencies",
    "rewards",
    "stage",
    "team_stage",
}
SCRIPTED_PRODUCERS = {
    "industrial_colonies:crude_flint_pickaxe": "industrial_primitive_tool_progression.js",
    "modernfoundry:part_builder": "industrial_primitive_tool_progression.js",
    "modernfoundry:tinker_station": "industrial_primitive_tool_progression.js",
    "industrial_colonies:black_hole": "industrial_black_hole_megaproject.js",
    "industrial_colonies:industrial_reserve_core": "industrial_reserve_core_megaproject.js",
    "industrial_colonies:industrial_star": "industrial_star_megaproject.js",
}
FLUID_SAMPLE_ITEMS = {
    "tfmg:crude_oil_bucket": "tfmg:crude_oil",
    "tfmg:diesel_bucket": "tfmg:diesel",
}
PROJECT_RUNTIME_PRODUCERS = {
    "industrial_colonies:gas_giant_condensate_bucket": (
        "src/main/java/dev/godpc/industrialcolonies/space/station/AtmosphericScoopBlockEntity.java",
        "IndustrialFluids.GAS_GIANT_CONDENSATE",
    ),
}
INTERACTION_TRANSFORMS = {
    # Create converts the crafted empty burner by using it on a Blaze; the
    # captured form intentionally has no JSON crafting recipe of its own.
    "create:blaze_burner": "create:empty_blaze_burner",
}
PROJECT_SOURCE_ITEMS = {
    "industrial_colonies:orbital_flight_computer": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/orbital_flight_computer.json",
    ),
    "industrial_colonies:mars_navigation_computer": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/mars_navigation_computer.json",
    ),
    "industrial_colonies:venus_navigation_computer": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/venus_navigation_computer.json",
    ),
    "industrial_colonies:mercury_navigation_computer": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/mercury_navigation_computer.json",
    ),
    "industrial_colonies:station_services_controller": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/station_services_controller.json",
    ),
    "industrial_colonies:atmospheric_scoop": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/atmospheric_scoop.json",
    ),
    "industrial_colonies:gas_giant_condensate_bucket": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/gas_giant_condensate_bucket.json",
    ),
    "industrial_colonies:warp_charge_precursor": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/warp_charge_precursor.json",
    ),
    "industrial_colonies:interstellar_navigation_computer": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/interstellar_navigation_computer.json",
    ),
    "industrial_colonies:interstellar_warp_charge": (
        "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
        "src/main/resources/assets/industrial_colonies/models/item/interstellar_warp_charge.json",
    ),
    **{
        f"industrial_colonies:{name}": (
            "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java",
            f"src/main/resources/assets/industrial_colonies/models/item/{name}.json",
        )
        for name in (
            "desh_grit", "desh_concentrate", "desh_leached_compound",
            "ostrum_grit", "ostrum_concentrate", "ostrum_leached_compound",
            "calorite_grit", "calorite_concentrate", "calorite_leached_compound",
        )
    },
}
ORBITAL_COMPONENT_MODELS = {
    "rocketnautics:thruster_mount": "assets/rocketnautics/models/item/thruster_mount.json",
    "rocketnautics:engine_pipes": "assets/rocketnautics/models/item/engine_pipes.json",
    "rocketnautics:engine_nozzle": "assets/rocketnautics/models/item/engine_nozzle.json",
    "rocketnautics:hose_anchor": "assets/rocketnautics/models/item/hose_anchor.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def walk_json(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def parse_registry_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    pattern = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        value = raw.strip()
        if pattern.fullmatch(value):
            ids.add(value)
    if not ids:
        raise ValueError(f"runtime item catalog contains no registry IDs: {path}")
    return ids


def normalize_item_id(value: Any) -> str | None:
    if isinstance(value, str):
        candidate = value.strip().lstrip("#")
        candidate = re.sub(r"^\d+x\s+", "", candidate)
        return candidate if ":" in candidate else None
    if isinstance(value, dict):
        candidate = value.get("id")
        return str(candidate).lstrip("#") if candidate else None
    return None


def managed_output_ids(project: Path) -> set[str]:
    outputs: set[str] = set()
    for relative in (
        "progression/managed_recipe_overhaul.json",
        "progression/managed_recipe_overhaul.seed.json",
    ):
        manifest = load_json(project / relative)
        for recipe in manifest.get("recipes", []):
            if not isinstance(recipe, dict):
                continue
            values: list[Any] = []
            if "output" in recipe:
                values.append(recipe["output"])
            if isinstance(recipe.get("outputs"), list):
                values.extend(recipe["outputs"])
            if isinstance(recipe.get("results"), list):
                values.extend(recipe["results"])
            for value in values:
                item = normalize_item_id(value)
                if item:
                    outputs.add(item)
    return outputs


def static_output_ids(recipe_catalog: Path) -> set[str]:
    recipes_csv = recipe_catalog / "recipes.csv" if recipe_catalog.is_dir() else recipe_catalog
    outputs: set[str] = set()
    with recipes_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            for raw in str(row.get("outputs", "")).split("|"):
                item = normalize_item_id(raw)
                if item:
                    outputs.add(item)
    if not outputs:
        raise ValueError(f"static recipe catalog contains no outputs: {recipes_csv}")
    return outputs


def validate_project_source_items(project: Path, errors: list[str]) -> set[str]:
    """Resolve new project-owned items before a refreshed runtime export exists."""
    resolved: set[str] = set()
    for item, (registration_relative, model_relative) in PROJECT_SOURCE_ITEMS.items():
        registration = project / registration_relative
        model = project / model_relative
        path = item.split(":", 1)[1]
        if not registration.is_file():
            errors.append(f"project item {item} lacks registration source {registration_relative}")
            continue
        if f'"{path}"' not in registration.read_text(encoding="utf-8-sig"):
            errors.append(f"project item {item} is absent from {registration_relative}")
            continue
        if not model.is_file():
            errors.append(f"project item {item} lacks item model {model_relative}")
            continue
        resolved.add(item)
    return resolved


def validate_installed_orbital_ids(
    orbital: Mapping[str, Any], instance: Path, errors: list[str]
) -> None:
    """Prove every Rocketnautics component is a real installed item model."""
    observed = {
        str(task["item"])
        for quest in orbital["chapter"]["quests"]
        for task in quest["tasks"]
        if task["type"] == "item"
    }
    expected = {
        item
        for items in EXPECTED_ORBITAL_TASK_ITEMS.values()
        for item in items
    }
    require(observed == expected, f"orbital observation item set changed: {sorted(observed)}", errors)
    jars = sorted((instance / "mods").glob("cosmonautics-*.jar"))
    if len(jars) != 1:
        errors.append(f"expected one installed Cosmonautics JAR, found {len(jars)}")
        return
    try:
        with zipfile.ZipFile(jars[0]) as archive:
            names = set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"cannot inspect installed Cosmonautics JAR {jars[0]}: {exc}")
        return
    for item, model_path in ORBITAL_COMPONENT_MODELS.items():
        require(
            model_path in names,
            f"installed Cosmonautics JAR does not define {item} at {model_path}",
            errors,
        )


def validate_installed_planetary_extraction_ids(
    planetary: Mapping[str, Any], instance: Path, errors: list[str]
) -> None:
    """Pin mined offworld observations to their installed block loot tables."""
    observed = {
        str(task["item"])
        for quest in planetary["chapter"]["quests"]
        for task in quest["tasks"]
        if task["type"] == "item"
    }
    mods_dir = instance / "mods"
    for item, (jar_name, archive_path) in MINED_WORLDGEN_ITEMS.items():
        require(item in observed, f"planetary source lost mined observation {item}", errors)
        jar_path = mods_dir / jar_name
        if not jar_path.is_file():
            errors.append(f"missing installed extraction JAR {jar_path}")
            continue
        try:
            with zipfile.ZipFile(jar_path) as archive:
                names = set(archive.namelist())
        except (OSError, zipfile.BadZipFile) as exc:
            errors.append(f"cannot inspect installed extraction JAR {jar_path}: {exc}")
            continue
        require(
            archive_path in names,
            f"installed JAR {jar_name} does not define mined block {item} at {archive_path}",
            errors,
        )


def validate_installed_exploration_ids(
    exploration: Mapping[str, Any], instance: Path, errors: list[str]
) -> None:
    """Resolve every native task ID to the installed archive that defines it."""
    mods_dir = instance / "mods"
    archive_names: dict[str, set[str]] = {}

    def names(jar_name: str) -> set[str]:
        if jar_name in archive_names:
            return archive_names[jar_name]
        jar_path = mods_dir / jar_name
        if not jar_path.is_file():
            errors.append(f"missing installed exploration JAR {jar_path}")
            archive_names[jar_name] = set()
            return archive_names[jar_name]
        try:
            with zipfile.ZipFile(jar_path) as archive:
                archive_names[jar_name] = set(archive.namelist())
        except (OSError, zipfile.BadZipFile) as exc:
            errors.append(f"cannot inspect installed exploration JAR {jar_path}: {exc}")
            archive_names[jar_name] = set()
        return archive_names[jar_name]

    structure_ids: set[str] = set()
    advancement_ids: set[str] = set()
    item_ids: set[str] = set()
    for quest in exploration["chapter"]["quests"]:
        for task in quest["tasks"]:
            if task["type"] == "structure":
                structure_ids.add(str(task["structure"]))
            elif task["type"] == "advancement":
                advancement_ids.add(str(task["advancement"]))
            elif task["type"] == "item":
                item_ids.add(str(task["item"]))

    require(
        structure_ids == set(INSTALLED_STRUCTURE_PATHS),
        f"exploration structure IDs changed: {sorted(structure_ids)}",
        errors,
    )
    for identifier in sorted(structure_ids):
        evidence = INSTALLED_STRUCTURE_PATHS.get(identifier)
        if evidence is None:
            continue
        jar_name, archive_path = evidence
        require(
            archive_path in names(jar_name),
            f"installed JAR {jar_name} does not define structure {identifier} at {archive_path}",
            errors,
        )

    require(
        advancement_ids == set(INSTALLED_ADVANCEMENT_PATHS),
        f"exploration advancement IDs changed: {sorted(advancement_ids)}",
        errors,
    )
    for identifier in sorted(advancement_ids):
        evidence = INSTALLED_ADVANCEMENT_PATHS.get(identifier)
        if evidence is None:
            continue
        jar_name, archive_path = evidence
        require(
            archive_path in names(jar_name),
            f"installed JAR {jar_name} does not define advancement {identifier} at {archive_path}",
            errors,
        )

    ftb_jar = "ftb-quests-neoforge-2101.1.34.jar"
    ftb_names = names(ftb_jar)
    for task_class in sorted(NATIVE_TASK_CLASSES):
        require(
            task_class in ftb_names,
            f"installed FTB Quests JAR lacks native task class {task_class}",
            errors,
        )

    for item, (jar_name, archive_path) in EXPLORATION_LOOT_ITEMS.items():
        require(item in item_ids, f"exploration source lost loot observation {item}", errors)
        jar_path = mods_dir / jar_name
        if archive_path not in names(jar_name):
            errors.append(f"installed JAR {jar_name} lacks loot evidence {archive_path}")
            continue
        try:
            with zipfile.ZipFile(jar_path) as archive:
                payload = archive.read(archive_path).decode("utf-8", errors="replace")
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            errors.append(f"cannot read {archive_path} from {jar_name}: {exc}")
            continue
        require(
            item in payload,
            f"installed Dungeon Crawl stage-1 treasure no longer contains {item}",
            errors,
        )


def validate_production_paths(
    project: Path,
    guidance: Mapping[str, Any],
    exploration: Mapping[str, Any],
    endgame: Mapping[str, Any],
    orbital: Mapping[str, Any],
    planetary: Mapping[str, Any],
    registry_ids: set[str],
    static_outputs: set[str],
    managed_outputs: set[str],
    audited_outputs: set[str],
    errors: list[str],
) -> dict[str, int]:
    script_root = project / "pack-scripts" / "server_scripts"
    scripted_text: dict[str, str] = {}
    for item, filename in SCRIPTED_PRODUCERS.items():
        path = script_root / filename
        if not path.is_file():
            errors.append(f"quest task {item} depends on missing producer script {filename}")
            continue
        text = scripted_text.setdefault(filename, path.read_text(encoding="utf-8-sig"))
        if item not in text:
            errors.append(f"producer script {filename} does not mention quest task item {item}")

    task_items: list[str] = []
    icons: list[str] = []
    for chapter in guidance.get("chapters", []):
        for quest in chapter.get("quests", []):
            icons.append(str(quest.get("icon", "")))
            task_items.extend(
                str(task.get("item", ""))
                for task in quest.get("tasks", [])
                if task.get("type") == "item"
            )
    for quest in exploration.get("chapter", {}).get("quests", []):
        icons.append(str(quest.get("icon", "")))
        task_items.extend(
            str(task.get("item", ""))
            for task in quest.get("tasks", [])
            if task.get("type") == "item"
        )
    for quest in endgame.get("quests", []):
        icons.append(str(quest.get("icon", "")))
        task_items.extend(
            str(task.get("item", ""))
            for task in quest.get("tasks", [])
            if task.get("type") == "item"
        )
    for quest in orbital.get("chapter", {}).get("quests", []):
        icons.append(str(quest.get("icon", "")))
        task_items.extend(
            str(task.get("item", ""))
            for task in quest.get("tasks", [])
            if task.get("type") == "item"
        )
    for quest in planetary.get("chapter", {}).get("quests", []):
        icons.append(str(quest.get("icon", "")))
        task_items.extend(
            str(task.get("item", ""))
            for task in quest.get("tasks", [])
            if task.get("type") == "item"
        )

    project_source_items = validate_project_source_items(project, errors)
    for item in sorted(set(task_items + icons)):
        if item not in registry_ids and item not in project_source_items:
            errors.append(f"quest references an item absent from the installed registry catalog: {item}")

    producer_classes = {
        "post_diesel_audit": 0,
        "managed": 0,
        "stock": 0,
        "script": 0,
        "project_runtime": 0,
        "fluid_sample": 0,
        "interaction_transform": 0,
        "structure_loot": 0,
        "vanilla_recipe": 0,
        "worldgen_drop": 0,
    }
    for item in sorted(set(task_items)):
        if item in audited_outputs:
            producer_classes["post_diesel_audit"] += 1
        elif item in managed_outputs:
            producer_classes["managed"] += 1
        elif item in SCRIPTED_PRODUCERS:
            producer_classes["script"] += 1
        elif item in PROJECT_RUNTIME_PRODUCERS:
            source_relative, evidence_token = PROJECT_RUNTIME_PRODUCERS[item]
            source = project / source_relative
            if not source.is_file() or evidence_token not in source.read_text(encoding="utf-8-sig"):
                errors.append(
                    f"project runtime task {item} lacks producer evidence {source_relative}:{evidence_token}"
                )
            producer_classes["project_runtime"] += 1
        elif item in FLUID_SAMPLE_ITEMS:
            fluid = FLUID_SAMPLE_ITEMS[item]
            if fluid not in registry_ids:
                errors.append(f"fluid sample {item} has no installed canonical fluid {fluid}")
            petroleum_script = script_root / "industrial_petroleum_canonicalization.js"
            if not petroleum_script.is_file() or fluid not in petroleum_script.read_text(encoding="utf-8-sig"):
                errors.append(f"fluid sample {item} is not backed by canonical petroleum script {fluid}")
            producer_classes["fluid_sample"] += 1
        elif item in INTERACTION_TRANSFORMS:
            precursor = INTERACTION_TRANSFORMS[item]
            if precursor not in registry_ids or precursor not in static_outputs:
                errors.append(
                    f"interaction-produced task {item} has no craftable installed precursor {precursor}"
                )
            producer_classes["interaction_transform"] += 1
        elif item in EXPLORATION_LOOT_ITEMS:
            producer_classes["structure_loot"] += 1
        elif item in VANILLA_RECIPE_ITEMS:
            producer_classes["vanilla_recipe"] += 1
        elif item in MINED_WORLDGEN_ITEMS:
            producer_classes["worldgen_drop"] += 1
        elif item in static_outputs:
            producer_classes["stock"] += 1
        else:
            errors.append(
                "quest task has no audited, managed, stock, scripted, fluid-sample, interaction, "
                f"structure-loot, worldgen-drop, or vanilla-recipe production path: {item}"
            )
    return producer_classes


def validate(
    *,
    project: Path,
    guidance_source: Path,
    endgame_source: Path,
    quest_root: Path,
    manifest_path: Path,
    item_catalog: Path,
    recipe_catalog: Path,
    errors: list[str],
    exploration_source: Path = DEFAULT_EXPLORATION_SOURCE,
    orbital_source: Path = DEFAULT_ORBITAL_SOURCE,
    planetary_source: Path = DEFAULT_PLANETARY_SOURCE,
    instance: Path = DEFAULT_INSTANCE,
) -> dict[str, Any]:
    guidance = validate_guidance_source(guidance_source)
    exploration = validate_exploration_source(exploration_source)
    endgame = validate_endgame_source(endgame_source)
    orbital = validate_orbital_source(orbital_source)
    planetary = validate_planetary_source(planetary_source)
    expected_artifacts, expected_manifest = build_artifacts(
        guidance_source,
        endgame_source,
        quest_root,
        exploration_source,
        orbital_source,
        planetary_source,
    )

    files = {
        path.relative_to(quest_root).as_posix()
        for path in quest_root.rglob("*.snbt")
    }
    require(files == EXPECTED_FILES, (
        f"quest file set mismatch; expected={sorted(EXPECTED_FILES)}, found={sorted(files)}"
    ), errors)
    parsed: dict[str, Any] = {}
    for relative in sorted(files):
        try:
            parsed[relative] = load_json(quest_root / relative)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid strict JSON/SNBT in {relative}: {exc}")
    for relative, expected in expected_artifacts.items():
        require(parsed.get(relative) == expected, f"generated artifact differs from source: {relative}", errors)

    data = parsed.get("data.snbt", {})
    require(data.get("version") == 13, "FTB data version must be 13", errors)
    require(data.get("default_consume_items") is False, "item tasks must not consume by default", errors)
    require(data.get("default_reward_team") is False, "quest rewards must remain disabled", errors)
    require(data.get("suppress_all_autoclaiming") is True, "autoclaiming must remain suppressed", errors)
    require(parsed.get("chapter_groups.snbt") == {"chapter_groups": []}, "chapter groups must remain empty", errors)
    chapter_groups_path = quest_root / "chapter_groups.snbt"
    if chapter_groups_path.is_file():
        chapter_groups_sha256 = hashlib.sha256(chapter_groups_path.read_bytes()).hexdigest().upper()
        require(
            chapter_groups_sha256 == EXPECTED_CHAPTER_GROUPS_SHA256,
            "chapter_groups.snbt bytes changed",
            errors,
        )

    generated_chapters = {
        relative.removeprefix("chapters/").removesuffix(".snbt"): value
        for relative, value in parsed.items()
        if relative.startswith("chapters/")
    }
    guidance_chapter = generated_chapters.get("factory_foundations", {})
    exploration_chapter = generated_chapters.get(EXPLORATION_FILENAME, {})
    endgame_chapter = generated_chapters.get(ENDGAME_FILENAME, {})
    orbital_chapter = generated_chapters.get(ORBITAL_FILENAME, {})
    planetary_chapter = generated_chapters.get(PLANETARY_FILENAME, {})
    require(len(guidance_chapter.get("quests", [])) == 30, "Factory Foundations must contain 30 quests", errors)
    require(
        len(exploration_chapter.get("quests", [])) == 12,
        "Dungeon Expeditions must contain 12 quests",
        errors,
    )
    expected_later_chapter_counts = {
        "electrical_manufacturing": 7,
        "digital_logistics": 6,
        "mekanized_industry": 8,
        "high_energy_grid": 10,
        "nuclear_engineering": 9,
    }
    for filename, expected_count in expected_later_chapter_counts.items():
        require(
            len(generated_chapters.get(filename, {}).get("quests", [])) == expected_count,
            f"{filename} must contain {expected_count} quests",
            errors,
        )
    require(len(endgame_chapter.get("quests", [])) == 3, "Industrial Endgame must contain 3 quests", errors)
    require(
        len(orbital_chapter.get("quests", [])) == len(EXPECTED_ORBITAL_KEYS),
        f"Orbital Engineering must contain {len(EXPECTED_ORBITAL_KEYS)} quests",
        errors,
    )
    require(
        len(planetary_chapter.get("quests", [])) == len(EXPECTED_PLANETARY_KEYS),
        f"Planetary Industry must contain {len(EXPECTED_PLANETARY_KEYS)} quests",
        errors,
    )

    for relative, value in parsed.items():
        for child in walk_json(value):
            if isinstance(child, dict):
                forbidden = FORBIDDEN_KEYS.intersection(child)
                require(not forbidden, f"{relative} contains forbidden keys {sorted(forbidden)}", errors)
                task_type = child.get("type")
                if task_type in {"item", "structure", "advancement"}:
                    if task_type == "item":
                        require("item" in child, f"{relative} item task lacks an item", errors)
                        require(
                            child.get("consume_items", False) is False,
                            f"{relative} consumes a task item",
                            errors,
                        )
                    elif task_type == "structure":
                        require(
                            isinstance(child.get("structure"), str),
                            f"{relative} structure task lacks a structure ID",
                            errors,
                        )
                    else:
                        require(
                            isinstance(child.get("advancement"), str)
                            and child.get("criterion") == "",
                            f"{relative} advancement task must observe a complete advancement",
                            errors,
                        )
            elif isinstance(child, str):
                lowered = child.lower()
                require("minecolonies" not in lowered, f"{relative} contains legacy MineColonies research text", errors)
                require("recipe unlock" not in lowered, f"{relative} claims to unlock recipes", errors)

    require(stable_code("chapter", ENDGAME_FILENAME) == EXPECTED_ENDGAME_CHAPTER_ID, "endgame chapter ID salt changed", errors)
    require(endgame_chapter.get("id") == EXPECTED_ENDGAME_CHAPTER_ID, "generated endgame chapter ID changed", errors)
    generated_endgame = {quest.get("id"): quest for quest in endgame_chapter.get("quests", [])}
    for key in EXPECTED_ENDGAME_KEYS:
        quest_id = EXPECTED_ENDGAME_QUEST_IDS[key]
        require(stable_code("megaproject_quest", f"{ENDGAME_FILENAME}/{key}") == quest_id, f"{key} deterministic ID changed", errors)
        quest = generated_endgame.get(quest_id, {})
        dependencies = [EXPECTED_ENDGAME_QUEST_IDS[value] for value in EXPECTED_ENDGAME_DEPENDENCIES[key]]
        require(quest.get("dependencies") == dependencies, f"{key} capstone dependency chain changed", errors)
        expected_task = {
            "id": EXPECTED_ENDGAME_TASK_IDS[key],
            "type": "item",
            "item": {"id": EXPECTED_ENDGAME_ITEMS[key]},
            "count": 1,
        }
        require(quest.get("tasks") == [expected_task], f"{key} capstone item task changed", errors)

    require(
        orbital_chapter.get("id") == stable_code("chapter", ORBITAL_FILENAME),
        "Orbital Engineering chapter ID changed",
        errors,
    )
    generated_orbital = {
        str(quest.get("id", "")): quest
        for quest in orbital_chapter.get("quests", [])
    }
    translations = parsed.get("lang/en_us.snbt", {})
    for source_quest in orbital["chapter"]["quests"]:
        key = str(source_quest["key"])
        quest_id = stable_code("orbital_quest", f"{ORBITAL_FILENAME}/{key}")
        generated = generated_orbital.get(quest_id, {})
        dependency_ids = [
            (
                EXPECTED_ENDGAME_QUEST_IDS[dependency.split(":", 1)[1]]
                if ":" in dependency
                else stable_code(
                    "orbital_quest", f"{ORBITAL_FILENAME}/{dependency}"
                )
            )
            for dependency in EXPECTED_ORBITAL_DEPENDENCIES[key]
        ]
        require(
            generated.get("dependencies") == dependency_ids,
            f"orbital/{key} generated dependencies changed",
            errors,
        )
        tags = generated.get("tags", [])
        require(
            ORBITAL_GUIDANCE_TAG in tags
            and f"{ORBITAL_GUIDANCE_TAG}/{key}" in tags,
            f"orbital/{key} lost orbital-guidance tags",
            errors,
        )
        expected_tasks = [
            {
                "id": stable_code(
                    "orbital_task", f"{ORBITAL_FILENAME}/{key}/{index}/item"
                ),
                "type": "item",
                "item": {"id": item},
                "count": count,
            }
            for index, (item, count) in enumerate(
                zip(
                    EXPECTED_ORBITAL_TASK_ITEMS[key],
                    EXPECTED_ORBITAL_TASK_COUNTS[key],
                    strict=True,
                )
            )
        ]
        require(
            generated.get("tasks") == expected_tasks,
            f"orbital/{key} generated item observation changed",
            errors,
        )
        localized = json.dumps(
            [
                translations.get(f"quest.{quest_id}.title"),
                translations.get(f"quest.{quest_id}.quest_subtitle"),
                translations.get(f"quest.{quest_id}.quest_desc"),
            ],
            ensure_ascii=False,
        )
        require(
            DESTINATION_SPECIFIC_PATTERN.search(localized) is None,
            f"orbital/{key} generated text contains a destination-specific objective",
            errors,
        )
    flight_id = stable_code(
        "orbital_quest", f"{ORBITAL_FILENAME}/orbital_flight_computer"
    )
    require(
        generated_orbital.get(flight_id, {}).get("dependencies")
        == [EXPECTED_ENDGAME_QUEST_IDS["industrial_star"]],
        "Industrial Star must point directly to the Orbital Flight Computer",
        errors,
    )

    require(
        planetary_chapter.get("id") == stable_code("chapter", PLANETARY_FILENAME),
        "Planetary Industry chapter ID changed",
        errors,
    )
    generated_planetary = {
        str(quest.get("id", "")): quest
        for quest in planetary_chapter.get("quests", [])
    }
    for source_quest in planetary["chapter"]["quests"]:
        key = str(source_quest["key"])
        quest_id = stable_code(
            "planetary_quest", f"{PLANETARY_FILENAME}/{key}"
        )
        generated = generated_planetary.get(quest_id, {})
        dependency_ids = [
            (
                stable_code(
                    "orbital_quest",
                    f"{ORBITAL_FILENAME}/{dependency.split(':', 1)[1]}",
                )
                if ":" in dependency
                else stable_code(
                    "planetary_quest", f"{PLANETARY_FILENAME}/{dependency}"
                )
            )
            for dependency in EXPECTED_PLANETARY_DEPENDENCIES[key]
        ]
        require(
            generated.get("dependencies") == dependency_ids,
            f"planetary/{key} generated dependencies changed",
            errors,
        )
        tags = generated.get("tags", [])
        require(
            PLANETARY_GUIDANCE_TAG in tags
            and f"{PLANETARY_GUIDANCE_TAG}/{key}" in tags,
            f"planetary/{key} lost planetary-guidance tags",
            errors,
        )
        expected_tasks: list[dict[str, Any]] = []
        for index, task in enumerate(EXPECTED_PLANETARY_TASKS[key]):
            task_type = str(task["type"])
            expected: dict[str, Any] = {
                "id": stable_code(
                    "planetary_task",
                    f"{PLANETARY_FILENAME}/{key}/{index}/{task_type}",
                ),
                "type": task_type,
            }
            if task_type == "item":
                expected["item"] = {"id": str(task["item"])}
                expected["count"] = int(task.get("count", 1))
            else:
                expected["advancement"] = str(task["advancement"])
                expected["criterion"] = str(task.get("criterion", ""))
            expected_tasks.append(expected)
        require(
            generated.get("tasks") == expected_tasks,
            f"planetary/{key} generated observations changed",
            errors,
        )

    guidance_quests = guidance["chapters"][0]["quests"]
    guidance_by_key = {str(quest["key"]): quest for quest in guidance_quests}
    required_physical_dependencies = {
        # These are real recipe/material requirements, not arbitrary visual
        # locks. They prevent the guide from asking for brass/precision parts
        # before the factory can physically manufacture them.
        "steam_power": {"blaze_heating", "liquid_handling", "rotational_power"},
        "automated_assembly": {"brass_production", "material_handling"},
        "precision_assembly": {"automated_assembly"},
        "brass_logistics": {"precision_assembly", "bulk_storage"},
        "mechanical_crafting": {"brass_production", "steam_power"},
        "crushing_line": {"mechanical_crafting", "mechanical_processing"},
        "blast_furnace": {"coal_coke", "mechanical_crafting"},
        "distillation_column": {"crude_oil", "first_steel"},
        "diesel_engine_commissioning": {"diesel_fuel", "engine_fabrication"},
    }
    for key, required_dependencies in required_physical_dependencies.items():
        actual_dependencies = set(guidance_by_key.get(key, {}).get("dependencies", []))
        require(
            required_dependencies.issubset(actual_dependencies),
            f"guidance/{key} lost physical dependencies {sorted(required_dependencies - actual_dependencies)}",
            errors,
        )
    generated_guidance = guidance_chapter.get("quests", [])
    generated_by_id = {str(quest.get("id", "")): quest for quest in generated_guidance}
    for source_quest in guidance_quests:
        key = str(source_quest["key"])
        quest_id = stable_code("guidance_quest", f"factory_foundations/{key}")
        generated = generated_by_id.get(quest_id, {})
        tags = generated.get("tags", [])
        require(PHYSICAL_GUIDANCE_TAG in tags, f"guidance/{key} lost physical-guidance tag", errors)
        require(f"{PHYSICAL_GUIDANCE_TAG}/{key}" in tags, f"guidance/{key} lost stable key tag", errors)

    # The five post-Diesel chapters use the same deterministic guidance IDs,
    # with explicit cross-chapter edges resolved against the complete graph.
    all_guidance_ids = {
        f"{chapter['filename']}:{quest['key']}": stable_code(
            "guidance_quest", f"{chapter['filename']}/{quest['key']}"
        )
        for chapter in guidance["chapters"]
        for quest in chapter["quests"]
    }
    for source_chapter in guidance["chapters"][1:]:
        filename = str(source_chapter["filename"])
        generated_quests = {
            str(quest.get("id", "")): quest
            for quest in generated_chapters.get(filename, {}).get("quests", [])
        }
        for source_quest in source_chapter["quests"]:
            key = str(source_quest["key"])
            quest_id = all_guidance_ids[f"{filename}:{key}"]
            generated = generated_quests.get(quest_id, {})
            dependency_ids = [
                all_guidance_ids[
                    dependency if ":" in dependency else f"{filename}:{dependency}"
                ]
                for dependency in source_quest["dependencies"]
            ]
            require(
                generated.get("dependencies") == dependency_ids,
                f"guidance/{filename}:{key} generated dependencies changed",
                errors,
            )
            tags = generated.get("tags", [])
            require(
                PHYSICAL_GUIDANCE_TAG in tags
                and f"{PHYSICAL_GUIDANCE_TAG}/{key}" in tags,
                f"guidance/{filename}:{key} lost physical-guidance tags",
                errors,
            )
            expected_tasks = [
                {
                    "id": stable_code(
                        "guidance_task", f"{filename}/{key}/{index}/item"
                    ),
                    "type": "item",
                    "item": {"id": str(task["item"])},
                    "count": int(task.get("count", 1)),
                }
                for index, task in enumerate(source_quest["tasks"])
            ]
            require(
                generated.get("tasks") == expected_tasks,
                f"guidance/{filename}:{key} generated item tasks changed",
                errors,
            )
    network_sources = [
        quest
        for chapter in guidance["chapters"]
        if chapter["filename"] == "high_energy_grid"
        for quest in chapter["quests"]
        if quest["key"] == "physical_network_upgrade"
    ]
    require(len(network_sources) == 1, "physical_network_upgrade quest is missing", errors)
    if network_sources:
        require(
            network_sources[0]["tasks"] == [
                {
                    "type": "item",
                    "item": "mekanism:ultimate_logistical_transporter",
                    "count": 8,
                }
            ],
            "physical_network_upgrade must observe eight Ultimate Logistical Transporters",
            errors,
        )
    final_source = guidance_quests[-1]
    require(final_source.get("key") == "diesel_engine_commissioning", "campaign endpoint changed", errors)
    require(final_source.get("dependencies") == ["diesel_fuel", "engine_fabrication"], "diesel commissioning must converge fuel and engine branches", errors)
    final_items = {task["item"] for task in final_source.get("tasks", [])}
    require({"tfmg:regular_engine", "tfmg:diesel_engine_cylinder", "tfmg:diesel_bucket", "create:shaft"}.issubset(final_items), "diesel commissioning kit is incomplete", errors)

    exploration_quests = exploration["chapter"]["quests"]
    generated_exploration = {
        str(quest.get("id", "")): quest
        for quest in exploration_chapter.get("quests", [])
    }
    require(
        exploration_chapter.get("id") == stable_code("chapter", EXPLORATION_FILENAME),
        "Dungeon Expeditions chapter ID changed",
        errors,
    )
    translations = parsed.get("lang/en_us.snbt", {})
    for source_quest in exploration_quests:
        key = str(source_quest["key"])
        quest_id = stable_code(
            "exploration_quest", f"{EXPLORATION_FILENAME}/{key}"
        )
        generated = generated_exploration.get(quest_id, {})
        dependency_ids = [
            stable_code(
                "exploration_quest", f"{EXPLORATION_FILENAME}/{dependency}"
            )
            for dependency in source_quest["dependencies"]
        ]
        require(
            generated.get("dependencies") == dependency_ids,
            f"exploration/{key} generated dependencies changed",
            errors,
        )
        tags = generated.get("tags", [])
        require(
            EXPLORATION_GUIDANCE_TAG in tags,
            f"exploration/{key} lost exploration-guidance tag",
            errors,
        )
        require(
            f"{EXPLORATION_GUIDANCE_TAG}/{key}" in tags,
            f"exploration/{key} lost stable key tag",
            errors,
        )
        expected_tasks: list[dict[str, Any]] = []
        for index, task in enumerate(source_quest["tasks"]):
            task_type = str(task["type"])
            expected_task: dict[str, Any] = {
                "id": stable_code(
                    "exploration_task",
                    f"{EXPLORATION_FILENAME}/{key}/{index}/{task_type}",
                ),
                "type": task_type,
            }
            if task_type == "item":
                expected_task["item"] = {"id": str(task["item"])}
                expected_task["count"] = int(task.get("count", 1))
            elif task_type == "structure":
                expected_task["structure"] = str(task["structure"])
            else:
                expected_task["advancement"] = str(task["advancement"])
                expected_task["criterion"] = str(task.get("criterion", ""))
            expected_tasks.append(expected_task)
        require(
            generated.get("tasks") == expected_tasks,
            f"exploration/{key} generated native tasks changed",
            errors,
        )
        localized = json.dumps(
            [
                translations.get(f"quest.{quest_id}.title"),
                translations.get(f"quest.{quest_id}.quest_subtitle"),
                translations.get(f"quest.{quest_id}.quest_desc"),
            ],
            ensure_ascii=False,
        ).lower()
        require(
            "apotheosis" not in localized
            and re.search(r"\bboss(?:es)?\b", localized) is None,
            f"exploration/{key} generated text contains excluded objective language",
            errors,
        )

    validate_installed_exploration_ids(exploration, instance.resolve(), errors)
    validate_installed_orbital_ids(orbital, instance.resolve(), errors)
    validate_installed_planetary_extraction_ids(planetary, instance.resolve(), errors)

    registry_ids = parse_registry_ids(item_catalog)
    extension_plan_path = Path(str(guidance["_chapter_extension_source"]))
    extension_plan = load_json(extension_plan_path)
    managed_document = load_json(project / "progression" / "managed_recipe_overhaul.json")
    physical_document = load_json(project / "progression" / "physical_recipe_tiers.json")
    assignments_document = load_json(project / "progression" / "machine_node_assignments.json")
    recipe_csv = recipe_catalog / "recipes.csv" if recipe_catalog.is_dir() else recipe_catalog
    post_diesel_errors = validate_post_diesel_plan(
        extension_plan,
        registry_ids=registry_ids,
        managed=managed_document,
        physical=physical_document,
        assignments=assignments_document,
        installed_recipes=post_diesel_installed_recipe_map(recipe_csv),
        foundations=load_json(guidance_source),
        dungeon=load_json(exploration_source),
        endgame=load_json(endgame_source),
    )
    errors.extend(f"post-Diesel source: {error}" for error in post_diesel_errors)
    audited_outputs = set(extension_plan.get("objective_evidence", {}))
    producer_classes = validate_production_paths(
        project,
        guidance,
        exploration,
        endgame,
        orbital,
        planetary,
        registry_ids,
        static_output_ids(recipe_catalog),
        managed_output_ids(project),
        audited_outputs,
        errors,
    )

    manifest = load_json(manifest_path)
    require(manifest == expected_manifest, "generated native quest manifest differs from sources", errors)
    expected_stats = {
        "chapter_count": 10,
        "quest_count": 124,
        "guidance_quest_count": 70,
        "exploration_quest_count": 12,
        "endgame_quest_count": 3,
        "orbital_quest_count": 10,
        "planetary_quest_count": 29,
        "dependency_count": 170,
        "item_task_count": 240,
        "structure_task_count": 8,
        "advancement_task_count": 7,
        "total_task_count": 255,
        "stage_task_count": 0,
        "reward_count": 0,
    }
    require(manifest.get("statistics") == expected_stats, f"quest statistics changed: {manifest.get('statistics')}", errors)
    authority = manifest.get("authority", {})
    for key in (
        "ftbquests_completion_grants_progression",
        "items_consumed",
        "rewards_emitted",
        "stage_tasks_emitted",
        "recipe_unlocks_emitted",
    ):
        require(authority.get(key) is False, f"manifest authority unexpectedly enables {key}", errors)

    return {
        "chapter_count": 10,
        "quest_count": 124,
        "guidance_quest_count": 70,
        "exploration_quest_count": 12,
        "endgame_quest_count": 3,
        "orbital_quest_count": 10,
        "planetary_quest_count": 29,
        "item_task_count": 240,
        "structure_task_count": 8,
        "advancement_task_count": 7,
        "total_task_count": 255,
        "dependency_count": expected_stats["dependency_count"],
        "reward_count": 0,
        "stage_task_count": 0,
        "producer_classes": producer_classes,
        "files": sorted(files),
        "endgame_ids": {
            "chapter": EXPECTED_ENDGAME_CHAPTER_ID,
            "quests": EXPECTED_ENDGAME_QUEST_IDS,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--campaign-source", type=Path, default=DEFAULT_GUIDANCE_SOURCE)
    parser.add_argument(
        "--exploration-source", type=Path, default=DEFAULT_EXPLORATION_SOURCE
    )
    parser.add_argument("--endgame-source", type=Path, default=DEFAULT_ENDGAME_SOURCE)
    parser.add_argument("--orbital-source", type=Path, default=DEFAULT_ORBITAL_SOURCE)
    parser.add_argument("--planetary-source", type=Path, default=DEFAULT_PLANETARY_SOURCE)
    parser.add_argument("--quest-root", type=Path, default=DEFAULT_QUEST_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--item-catalog", type=Path, default=DEFAULT_ITEM_CATALOG)
    parser.add_argument("--recipe-catalog", type=Path, default=DEFAULT_RECIPE_CATALOG)
    parser.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
    parser.add_argument("--source", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--graph", type=Path, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    guidance_source = args.campaign_source.resolve() if args.campaign_source != DEFAULT_GUIDANCE_SOURCE else project / "progression" / "ftbquests_guidance_campaign.json"
    exploration_source = (
        args.exploration_source.resolve()
        if args.exploration_source != DEFAULT_EXPLORATION_SOURCE
        else project / "progression" / "ftbquests_dungeon_exploration.json"
    )
    endgame_source = args.source.resolve() if args.source is not None else (
        args.endgame_source.resolve() if args.endgame_source != DEFAULT_ENDGAME_SOURCE else project / "progression" / "industrial_megaprojects.json"
    )
    orbital_source = (
        args.orbital_source.resolve()
        if args.orbital_source != DEFAULT_ORBITAL_SOURCE
        else project / "progression" / "ftbquests_orbital_engineering.json"
    )
    planetary_source = (
        args.planetary_source.resolve()
        if args.planetary_source != DEFAULT_PLANETARY_SOURCE
        else project / "progression" / "ftbquests_planetary_industry.json"
    )
    quest_root = args.quest_root.resolve() if args.quest_root != DEFAULT_QUEST_ROOT else project / "pack-config-overrides" / "ftbquests" / "quests"
    errors: list[str] = []
    try:
        details = validate(
            project=project,
            guidance_source=guidance_source,
            endgame_source=endgame_source,
            quest_root=quest_root,
            manifest_path=args.manifest.resolve(),
            item_catalog=args.item_catalog.resolve(),
            recipe_catalog=args.recipe_catalog.resolve(),
            errors=errors,
            exploration_source=exploration_source,
            orbital_source=orbital_source,
            planetary_source=planetary_source,
            instance=args.instance.resolve(),
        )
    except (OSError, csv.Error, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
        details = {}
    report = {
        "schema_version": 3,
        "status": "pass" if not errors else "fail",
        "mode": "physical_progression_guidance_campaign",
        "details": details,
        "errors": errors,
    }
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        print("FTB Quests validation FAILED:")
        for error in errors:
            print(f"- {error}")
        print(f"Report: {report_path}")
        return 1
    print(
        "FTB Quests validation passed: 70 physical-guidance quests across six "
        "factory chapters, 12 optional Dungeon Expeditions quests, the preserved "
        "3-quest capstone, 10 post-Star Orbital Engineering quests, and 29 "
        "Planetary Industry quests; 241 item, 8 structure, and 7 advancement "
        "tasks; 0 stage tasks and 0 rewards."
    )
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
