#!/usr/bin/env python3
"""Validate the read-only dungeon exploration audit against installed artifacts."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "DUNGEON_EXPLORATION_AUDIT.plan.json"
DEFAULT_INSTANCE = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one")
DEFAULT_REGISTRY = (
    ROOT.parents[1] / "exports" / "ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt"
)

RESOURCE_ID = re.compile(r"[a-z0-9_.-]+:[a-z0-9_./-]+")
FORBIDDEN_QUEST_FIELDS = {
    "command",
    "consume_items",
    "gamestage",
    "research_dependencies",
    "rewards",
    "stage",
    "team_stage",
}
FORBIDDEN_CONTENT = {
    "dungeonnowloading:chaotic_hexahedron",
    "dungeonnowloading:catalyzed_redstone",
    "dungeonnowloading:combustion_cell",
    "dungeonnowloading:labyrinth_trophy",
    "dungeonnowloading:temple_of_duality_trophy",
    "dungeonnowloading:story/labyrinth/awaken_chaos_spawner",
    "dungeonnowloading:story/labyrinth/obtain_chaotic_hexahedron",
    "dungeonnowloading:story/temple_of_duality/awaken_fairkeepers",
    "dungeonnowloading:story/temple_of_duality/obtain_catalyzed_redstone",
    "dungeonnowloading:story/temple_of_duality/obtain_combustion_cell",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def read_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path} is not a JSON object")
        return {}
    return value


def validate_dependency_graph(quests: list[dict[str, Any]], errors: list[str]) -> None:
    keys = [str(quest.get("key", "")) for quest in quests]
    known = set(keys)
    require(len(keys) == len(known), "proposed chapter repeats a quest key", errors)
    require(all(re.fullmatch(r"[a-z0-9_]+", key) for key in keys), "invalid quest key", errors)
    graph: dict[str, list[str]] = {}
    for quest in quests:
        key = str(quest.get("key", ""))
        dependencies = quest.get("dependencies")
        require(isinstance(dependencies, list), f"{key} dependencies are not a list", errors)
        if not isinstance(dependencies, list):
            dependencies = []
        unknown = [value for value in dependencies if value not in known]
        require(not unknown, f"{key} has unknown dependencies {unknown}", errors)
        require(key not in dependencies, f"{key} depends on itself", errors)
        require(
            len(dependencies) == len(set(dependencies)),
            f"{key} repeats a dependency",
            errors,
        )
        graph[key] = [str(value) for value in dependencies]

    state: dict[str, int] = {}

    def visit(key: str, stack: list[str]) -> None:
        if state.get(key) == 1:
            errors.append(f"dependency cycle: {' -> '.join(stack + [key])}")
            return
        if state.get(key) == 2:
            return
        state[key] = 1
        for dependency in graph.get(key, []):
            visit(dependency, stack + [key])
        state[key] = 2

    for key in keys:
        visit(key, [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()

    errors: list[str] = []
    plan = read_json(args.plan.resolve(), errors)
    if not plan:
        return fail(errors)
    require(plan.get("schema_version") == 1, "unsupported audit-plan schema", errors)

    mods_dir = args.instance.resolve() / "mods"
    archives: dict[str, set[str]] = {}

    def archive_names(jar_name: str) -> set[str]:
        if jar_name in archives:
            return archives[jar_name]
        path = mods_dir / jar_name
        if not path.is_file():
            errors.append(f"missing installed JAR {jar_name}")
            archives[jar_name] = set()
            return archives[jar_name]
        try:
            with zipfile.ZipFile(path) as archive:
                archives[jar_name] = set(archive.namelist())
        except (OSError, zipfile.BadZipFile) as exc:
            errors.append(f"cannot inspect installed JAR {jar_name}: {exc}")
            archives[jar_name] = set()
        return archives[jar_name]

    installed = plan.get("installed_mods", [])
    require(isinstance(installed, list) and len(installed) == 4, "expected four core installed mods", errors)
    if isinstance(installed, list):
        for mod in installed:
            if not isinstance(mod, dict):
                errors.append("installed_mods contains a non-object")
                continue
            jar = str(mod.get("jar", ""))
            names = archive_names(jar)
            for entry in mod.get("evidence_paths", []):
                require(entry in names, f"{jar} lacks evidence path {entry}", errors)

    structures = plan.get("validated_structures", [])
    require(isinstance(structures, list) and len(structures) == 8, "expected eight structures", errors)
    structure_ids: set[str] = set()
    if isinstance(structures, list):
        for structure in structures:
            if not isinstance(structure, dict):
                errors.append("validated_structures contains a non-object")
                continue
            identifier = str(structure.get("id", ""))
            require(bool(RESOURCE_ID.fullmatch(identifier)), f"invalid structure ID {identifier!r}", errors)
            require(identifier not in structure_ids, f"duplicate structure ID {identifier}", errors)
            structure_ids.add(identifier)
            jar = str(structure.get("jar", ""))
            names = archive_names(jar)
            for field in ("path", "structure_set_path"):
                entry = str(structure.get(field, ""))
                require(entry in names, f"{jar} lacks {field} {entry}", errors)
            spacing = structure.get("spacing_chunks")
            separation = structure.get("separation_chunks")
            require(
                isinstance(spacing, int) and isinstance(separation, int) and spacing > separation > 0,
                f"invalid placement distances for {identifier}",
                errors,
            )

    advancements = plan.get("validated_advancements", [])
    require(isinstance(advancements, list) and len(advancements) == 3, "expected three advancements", errors)
    advancement_ids: set[str] = set()
    if isinstance(advancements, list):
        for advancement in advancements:
            if not isinstance(advancement, dict):
                errors.append("validated_advancements contains a non-object")
                continue
            identifier = str(advancement.get("id", ""))
            advancement_ids.add(identifier)
            require(bool(RESOURCE_ID.fullmatch(identifier)), f"invalid advancement ID {identifier!r}", errors)
            jar = str(advancement.get("jar", ""))
            path = str(advancement.get("path", ""))
            require(path in archive_names(jar), f"{jar} lacks advancement {path}", errors)

    controls = plan.get("loot_controls", {})
    overrides = controls.get("exact_overrides", []) if isinstance(controls, dict) else []
    require(len(overrides) == 8, "expected eight exact loot overrides", errors)
    require(controls.get("exact_override_count") == len(overrides), "loot override count is stale", errors)
    for override in overrides:
        project_path = ROOT / str(override.get("project_path", ""))
        require(project_path.is_file(), f"missing project loot override {project_path}", errors)
        if project_path.is_file():
            read_json(project_path, errors)
        jar = str(override.get("upstream_jar", ""))
        upstream = str(override.get("upstream_path", ""))
        require(upstream in archive_names(jar), f"{jar} lacks upstream loot table {upstream}", errors)

    mixin = controls.get("dungeon_crawl_dynamic_control", {}) if isinstance(controls, dict) else {}
    mixin_source = ROOT / str(mixin.get("mixin_source", ""))
    require(mixin_source.is_file(), f"missing Dungeon Crawl mixin {mixin_source}", errors)
    require(mixin.get("affected_chest_table_count") == 7, "Dungeon Crawl dynamic table count changed", errors)

    boundary = plan.get("apotheosis_boundary", {})
    apo_jar = str(boundary.get("jar", "")) if isinstance(boundary, dict) else ""
    apo_names = archive_names(apo_jar)
    for evidence in boundary.get("evidence", []) if isinstance(boundary, dict) else []:
        path = str(evidence.get("path", ""))
        require(path in apo_names, f"{apo_jar} lacks global-loot evidence {path}", errors)

    registry_path = args.registry.resolve()
    require(registry_path.is_file(), f"missing runtime registry export {registry_path}", errors)
    registry_lines = set()
    if registry_path.is_file():
        registry_lines = {
            line.strip()
            for line in registry_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
            if RESOURCE_ID.fullmatch(line.strip())
        }

    chapter = plan.get("proposed_guidance_chapter", {})
    quests = chapter.get("quests", []) if isinstance(chapter, dict) else []
    require(isinstance(quests, list) and len(quests) == 12, "expected twelve proposed quests", errors)
    typed_counts = {"item": 0, "structure": 0, "advancement": 0}
    quest_task_types: dict[str, set[str]] = {}
    quest_blob = json.dumps(quests, sort_keys=True).lower()
    require("apotheosis:" not in quest_blob, "proposed quest content references Apotheosis", errors)
    for forbidden in FORBIDDEN_CONTENT:
        require(forbidden not in quest_blob, f"proposed quest content references excluded ID {forbidden}", errors)

    if isinstance(quests, list):
        validate_dependency_graph(quests, errors)
        for quest in quests:
            if not isinstance(quest, dict):
                errors.append("proposed quests contains a non-object")
                continue
            key = str(quest.get("key", ""))
            forbidden_fields = FORBIDDEN_QUEST_FIELDS.intersection(quest)
            require(not forbidden_fields, f"{key} has forbidden fields {sorted(forbidden_fields)}", errors)
            icon = str(quest.get("icon", ""))
            require(icon in registry_lines, f"quest {key} icon {icon} is absent from registry export", errors)
            tasks = quest.get("tasks", [])
            require(isinstance(tasks, list) and tasks, f"quest {key} has no tasks", errors)
            quest_task_types[key] = set()
            if not isinstance(tasks, list):
                continue
            for task in tasks:
                if not isinstance(task, dict):
                    errors.append(f"quest {key} contains a non-object task")
                    continue
                task_type = str(task.get("type", ""))
                require(task_type in typed_counts, f"quest {key} has unsupported task type {task_type}", errors)
                if task_type not in typed_counts:
                    continue
                typed_counts[task_type] += 1
                quest_task_types[key].add(task_type)
                require(not FORBIDDEN_QUEST_FIELDS.intersection(task), f"quest {key} task has forbidden fields", errors)
                if task_type == "item":
                    item = str(task.get("item", ""))
                    require(item in registry_lines, f"task item {item} is absent from registry export", errors)
                    count = task.get("count", 1)
                    require(isinstance(count, int) and not isinstance(count, bool) and count > 0, f"invalid item count for {key}", errors)
                elif task_type == "structure":
                    identifier = str(task.get("structure", ""))
                    require(identifier in structure_ids, f"task references unvalidated structure {identifier}", errors)
                elif task_type == "advancement":
                    identifier = str(task.get("advancement", ""))
                    require(identifier in advancement_ids, f"task references unvalidated advancement {identifier}", errors)
                    require(task.get("criterion") == "", f"quest {key} must check the complete advancement", errors)

    stats = chapter.get("statistics", {}) if isinstance(chapter, dict) else {}
    require(typed_counts == {"item": 4, "structure": 8, "advancement": 1}, f"unexpected task counts {typed_counts}", errors)
    require(stats.get("quest_count") == len(quests), "proposed quest count statistic is stale", errors)
    dependency_count = sum(
        len(quest.get("dependencies", []))
        for quest in quests
        if isinstance(quest, dict) and isinstance(quest.get("dependencies"), list)
    )
    require(stats.get("dependency_count") == dependency_count, "dependency statistic is stale", errors)
    require(stats.get("item_task_count") == typed_counts["item"], "item-task statistic is stale", errors)
    require(stats.get("structure_task_count") == typed_counts["structure"], "structure-task statistic is stale", errors)
    require(stats.get("advancement_task_count") == typed_counts["advancement"], "advancement-task statistic is stale", errors)
    require(stats.get("total_task_count") == sum(typed_counts.values()), "total-task statistic is stale", errors)
    roots = [quest for quest in quests if isinstance(quest, dict) and not quest.get("dependencies")]
    require(len(roots) == 1 and roots[0].get("key") == "field_lighting", "chapter must have field_lighting as its only root", errors)

    # StructureTask does not backfill on login. Do not put a structure visit
    # behind another structure visit; the player must not be forced to re-enter.
    by_key = {str(quest.get("key", "")): quest for quest in quests if isinstance(quest, dict)}
    for key, types in quest_task_types.items():
        if "structure" not in types:
            continue
        for dependency in by_key[key].get("dependencies", []):
            require(
                "structure" not in quest_task_types.get(str(dependency), set()),
                f"structure quest {key} is improperly chained behind structure quest {dependency}",
                errors,
            )
    require(
        all("salvaged_stone_pickaxe" not in quest.get("dependencies", []) for quest in quests if isinstance(quest, dict)),
        "random salvaged-tool quest gates another quest",
        errors,
    )

    current = plan.get("current_generator_snapshot", {})
    expected = plan.get("expected_generated_totals_after_implementation", {})
    require(
        expected.get("quest_count") == current.get("total_quests") + stats.get("quest_count", 0),
        "expected generated quest total is inconsistent",
        errors,
    )
    require(
        expected.get("item_task_count") == current.get("item_tasks") + typed_counts["item"],
        "expected generated item-task total is inconsistent",
        errors,
    )
    require(expected.get("structure_task_count") == 8, "expected structure-task total is inconsistent", errors)
    require(expected.get("advancement_task_count") == 1, "expected advancement-task total is inconsistent", errors)
    require(expected.get("reward_count") == 0, "proposed campaign must emit no rewards", errors)
    require(expected.get("stage_task_count") == 0, "proposed campaign must emit no stage tasks", errors)
    require(expected.get("recipe_unlock_count") == 0, "proposed campaign must unlock no recipes", errors)
    require(expected.get("endgame_quest_ids_changed") is False, "endgame IDs must be preserved", errors)

    if errors:
        return fail(errors)
    print(
        "PASS: dungeon exploration audit references 8 installed structures, 3 installed "
        "advancements, 8 exact loot overrides, and a 12-quest/13-task non-gating plan "
        "with 0 rewards, 0 consuming tasks, and no excluded content."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("FAIL: dungeon exploration audit")
    for error in errors:
        print(f" - {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
