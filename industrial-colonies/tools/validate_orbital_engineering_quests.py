#!/usr/bin/env python3
"""Validate the non-gating post-Star Orbital Engineering quest chapter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from generate_ftbquests_native import (
    DEFAULT_ENDGAME_SOURCE,
    DEFAULT_EXPLORATION_SOURCE,
    DEFAULT_GUIDANCE_SOURCE,
    DEFAULT_MANIFEST,
    DEFAULT_ORBITAL_SOURCE,
    DEFAULT_OUTPUT,
    DESTINATION_SPECIFIC_PATTERN,
    EXPECTED_ENDGAME_KEYS,
    EXPECTED_ORBITAL_DEPENDENCIES,
    EXPECTED_ORBITAL_ITEMS,
    EXPECTED_ORBITAL_KEYS,
    EXPECTED_ORBITAL_TASK_ITEMS,
    EXPECTED_ORBITAL_TASK_COUNTS,
    ORBITAL_FILENAME,
    ORBITAL_GUIDANCE_TAG,
    build_artifacts,
    file_sha256,
    stable_code,
    validate_orbital_source,
)
from validate_ftbquests_native import (
    DEFAULT_INSTANCE,
    DEFAULT_ITEM_CATALOG,
    FORBIDDEN_KEYS,
    managed_output_ids,
    normalize_item_id,
    parse_registry_ids,
    validate_installed_orbital_ids,
    validate_project_source_items,
    walk_json,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORBITAL_RECIPE_IDS = {
    "orbital_flight_computer": "industrial_colonies:space/orbital_flight_computer",
    "hose_anchor": "industrial_colonies:space/propulsion/hose_anchor",
    "engine_pipes": "industrial_colonies:space/propulsion/engine_pipes",
    "engine_nozzle": "industrial_colonies:space/propulsion/engine_nozzle",
    "thruster_mount": "industrial_colonies:space/propulsion/thruster_mount",
    "physics_assembler": "industrial_colonies:space/construction/physics_assembler",
}
ORBITAL_RECIPE_DEPENDENCIES = {
    "orbital_flight_computer": [],
    "hose_anchor": [ORBITAL_RECIPE_IDS["orbital_flight_computer"]],
    "engine_pipes": [ORBITAL_RECIPE_IDS["hose_anchor"]],
    "engine_nozzle": [ORBITAL_RECIPE_IDS["engine_pipes"]],
    "thruster_mount": [
        ORBITAL_RECIPE_IDS["orbital_flight_computer"],
        ORBITAL_RECIPE_IDS["hose_anchor"],
        ORBITAL_RECIPE_IDS["engine_pipes"],
        ORBITAL_RECIPE_IDS["engine_nozzle"],
    ],
    "physics_assembler": [
        "industrial_colonies:space/construction/contraption_diagram"
    ],
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(
    *,
    project: Path,
    source: Path,
    quest_root: Path,
    manifest_path: Path,
    item_catalog: Path,
    instance: Path,
) -> list[str]:
    errors: list[str] = []
    try:
        orbital = validate_orbital_source(source)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return [str(exc)]

    guidance_source = project / "progression" / DEFAULT_GUIDANCE_SOURCE.name
    exploration_source = project / "progression" / DEFAULT_EXPLORATION_SOURCE.name
    endgame_source = project / "progression" / DEFAULT_ENDGAME_SOURCE.name
    try:
        artifacts, expected_manifest = build_artifacts(
            guidance_source,
            endgame_source,
            quest_root,
            exploration_source,
            source,
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return [str(exc)]

    chapter_relative = f"chapters/{ORBITAL_FILENAME}.snbt"
    chapter_path = quest_root / chapter_relative
    if not chapter_path.is_file():
        errors.append(f"generated Orbital Engineering chapter is missing: {chapter_path}")
        generated_chapter: dict[str, Any] = {}
    else:
        generated_chapter = load_json(chapter_path)
        require(
            generated_chapter == artifacts[chapter_relative],
            "generated Orbital Engineering chapter differs from its source",
            errors,
        )

    lang_path = quest_root / "lang" / "en_us.snbt"
    translations = load_json(lang_path) if lang_path.is_file() else {}
    expected_translations = artifacts["lang/en_us.snbt"]
    require(
        translations.get(
            f"chapter.{stable_code('chapter', ORBITAL_FILENAME)}.title"
        )
        == expected_translations.get(
            f"chapter.{stable_code('chapter', ORBITAL_FILENAME)}.title"
        ),
        "Orbital Engineering chapter localization is stale",
        errors,
    )

    generated_by_id = {
        str(quest.get("id", "")): quest
        for quest in generated_chapter.get("quests", [])
        if isinstance(quest, dict)
    }
    endgame_ids = {
        key: stable_code("megaproject_quest", f"industrial_progression/{key}")
        for key in EXPECTED_ENDGAME_KEYS
    }
    for source_quest in orbital["chapter"]["quests"]:
        key = str(source_quest["key"])
        quest_id = stable_code("orbital_quest", f"{ORBITAL_FILENAME}/{key}")
        generated = generated_by_id.get(quest_id, {})
        expected_dependencies = [
            (
                endgame_ids[dependency.split(":", 1)[1]]
                if ":" in dependency
                else stable_code(
                    "orbital_quest", f"{ORBITAL_FILENAME}/{dependency}"
                )
            )
            for dependency in EXPECTED_ORBITAL_DEPENDENCIES[key]
        ]
        require(
            generated.get("dependencies") == expected_dependencies,
            f"orbital/{key} generated dependency edge changed",
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
            f"orbital/{key} is not the expected item observation set",
            errors,
        )
        tags = generated.get("tags", [])
        require(
            ORBITAL_GUIDANCE_TAG in tags
            and f"{ORBITAL_GUIDANCE_TAG}/{key}" in tags,
            f"orbital/{key} lost its manual-guidance tags",
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
            f"orbital/{key} generated a destination-specific objective",
            errors,
        )

    flight_id = stable_code(
        "orbital_quest", f"{ORBITAL_FILENAME}/orbital_flight_computer"
    )
    require(
        generated_by_id.get(flight_id, {}).get("dependencies")
        == [endgame_ids["industrial_star"]],
        "the visible Industrial Star -> Orbital Flight Computer edge is missing",
        errors,
    )
    route_keys = [
        "orbital_flight_computer",
        "hose_anchor",
        "engine_pipes",
        "engine_nozzle",
        "thruster_mount",
    ]
    expected_parent_ids = [
        endgame_ids["industrial_star"],
        stable_code("orbital_quest", f"{ORBITAL_FILENAME}/orbital_flight_computer"),
        stable_code("orbital_quest", f"{ORBITAL_FILENAME}/hose_anchor"),
        stable_code("orbital_quest", f"{ORBITAL_FILENAME}/engine_pipes"),
        stable_code("orbital_quest", f"{ORBITAL_FILENAME}/engine_nozzle"),
    ]
    actual_parent_ids = [
        generated_by_id.get(
            stable_code("orbital_quest", f"{ORBITAL_FILENAME}/{key}"), {}
        ).get("dependencies", [None])[0]
        for key in route_keys
    ]
    require(
        actual_parent_ids == expected_parent_ids,
        "the modular propulsion quests no longer follow hose -> pipes -> nozzle -> mount",
        errors,
    )

    for child in walk_json(generated_chapter):
        if not isinstance(child, dict):
            continue
        forbidden = FORBIDDEN_KEYS.intersection(child)
        require(
            not forbidden,
            f"generated orbital chapter contains gate/reward fields {sorted(forbidden)}",
            errors,
        )
        if child.get("type") == "item":
            require(
                child.get("consume_items", False) is False,
                "generated orbital item task consumes its observed hardware",
                errors,
            )

    try:
        manifest = load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read generated native quest manifest: {exc}")
        manifest = {}
    expected_orbital_quests = [
        quest
        for quest in expected_manifest["quests"]
        if quest["chapter"] == ORBITAL_FILENAME
    ]
    manifest_orbital_quests = [
        quest
        for quest in manifest.get("quests", [])
        if isinstance(quest, dict) and quest.get("chapter") == ORBITAL_FILENAME
    ]
    require(
        manifest_orbital_quests == expected_orbital_quests,
        "generated manifest Orbital Engineering entries differ from source",
        errors,
    )
    orbital_sources = [
        entry
        for entry in manifest.get("sources", [])
        if isinstance(entry, dict) and entry.get("kind") == "orbital"
    ]
    require(
        len(orbital_sources) == 1
        and orbital_sources[0].get("sha256") == file_sha256(source),
        "generated manifest lacks the current orbital source fingerprint",
        errors,
    )
    authority = manifest.get("authority", {})
    for key in (
        "ftbquests_completion_grants_progression",
        "items_consumed",
        "rewards_emitted",
        "stage_tasks_emitted",
        "recipe_unlocks_emitted",
    ):
        require(
            authority.get(key) is False,
            f"generated manifest unexpectedly enables {key}",
            errors,
        )

    registry_ids = parse_registry_ids(item_catalog)
    project_items = validate_project_source_items(project, errors)
    for item in {
        item
        for items in EXPECTED_ORBITAL_TASK_ITEMS.values()
        for item in items
    }:
        require(
            item in registry_ids or item in project_items,
            f"orbital guidance item is not registered or source-registered: {item}",
            errors,
        )
    require(
        EXPECTED_ORBITAL_ITEMS["orbital_flight_computer"]
        in managed_output_ids(project),
        "Orbital Flight Computer has no managed physical recipe",
        errors,
    )
    managed = load_json(project / "progression" / "managed_recipe_overhaul.json")
    managed_by_id = {
        str(recipe.get("id", "")): recipe
        for recipe in managed.get("recipes", [])
        if isinstance(recipe, dict)
    }
    for key, recipe_id in ORBITAL_RECIPE_IDS.items():
        recipe = managed_by_id.get(recipe_id, {})
        require(bool(recipe), f"managed orbital recipe is missing: {recipe_id}", errors)
        require(
            normalize_item_id(recipe.get("output")) == EXPECTED_ORBITAL_ITEMS[key],
            f"managed orbital recipe output changed: {recipe_id}",
            errors,
        )
        require(
            recipe.get("type") == "mechanical_crafting",
            f"managed orbital recipe is not Mechanical Crafting: {recipe_id}",
            errors,
        )
        require(
            set(ORBITAL_RECIPE_DEPENDENCIES[key]).issubset(
                set(recipe.get("depends_on", []))
            ),
            f"managed orbital recipe lost its required dependency route: {recipe_id}",
            errors,
        )
        if key == "orbital_flight_computer":
            require(
                "industrial_colonies:industrial_star"
                in json.dumps(recipe.get("key", {})),
                "Orbital Flight Computer recipe no longer consumes the Industrial Star",
                errors,
            )
    validate_installed_orbital_ids(orbital, instance, errors)
    return errors


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--source", type=Path, default=DEFAULT_ORBITAL_SOURCE)
    parser.add_argument("--quest-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--item-catalog", type=Path, default=DEFAULT_ITEM_CATALOG)
    parser.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    project = args.project.resolve()
    source = (
        args.source.resolve()
        if args.source != DEFAULT_ORBITAL_SOURCE
        else project / "progression" / "ftbquests_orbital_engineering.json"
    )
    quest_root = (
        args.quest_root.resolve()
        if args.quest_root != DEFAULT_OUTPUT
        else project / "pack-config-overrides" / "ftbquests" / "quests"
    )
    errors = validate(
        project=project,
        source=source,
        quest_root=quest_root,
        manifest_path=args.manifest.resolve(),
        item_catalog=args.item_catalog.resolve(),
        instance=args.instance.resolve(),
    )
    if errors:
        print("Orbital Engineering quest validation FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Orbital Engineering quest validation passed: Industrial Star -> Orbital "
        "Flight Computer -> hose -> pipes -> nozzle -> mount, habitat readiness, "
        "ground-side Physics Assembler, navigation, four-channel docking, and "
        "station-material observations; 0 rewards, "
        "0 stage/research gates, and 0 destination-specific objectives."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
