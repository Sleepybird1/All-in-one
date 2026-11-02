#!/usr/bin/env python3
"""Validate the implemented post-Diesel FTB Quests guidance plan.

The native generator consumes this plan through the guidance source's reviewed
extension reference. Validation proves topology, non-gating semantics,
installed item IDs, and exact evidence in the managed manifest, implemented
audit contracts, physical-output contracts, or installed machine recipes.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
DEFAULT_PLAN = PROJECT / "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json"
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_PHYSICAL = PROJECT / "progression" / "physical_recipe_tiers.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
DEFAULT_ITEMS = WORKSPACE / "exports" / "ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt"
DEFAULT_RECIPES = WORKSPACE / "outputs" / "recipe-catalog-current" / "recipes.csv"
DEFAULT_FOUNDATIONS = PROJECT / "progression" / "ftbquests_guidance_campaign.json"
DEFAULT_DUNGEON = PROJECT / "progression" / "ftbquests_dungeon_exploration.json"
DEFAULT_ENDGAME = PROJECT / "progression" / "industrial_megaprojects.json"
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
STACK = re.compile(r"^(?:[1-9][0-9]*x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)$")
EXPECTED_CHAPTERS = {
    "electrical_manufacturing": (7, 17, -80),
    "digital_logistics": (6, 14, -70),
    "mekanized_industry": (8, 22, -60),
    "high_energy_grid": (10, 31, -50),
    "nuclear_engineering": (9, 20, -40),
}
EXPECTED_CURRENT = {
    "factory_foundations": (30, 60),
    "dungeon_exploration": (12, 13),
    "industrial_progression": (3, 3),
}
EXPECTED_ENDGAME = {
    "black_hole": ([], "industrial_colonies:black_hole"),
    "industrial_reserves": (["black_hole"], "industrial_colonies:industrial_reserve_core"),
    "industrial_star": (["industrial_reserves"], "industrial_colonies:industrial_star"),
}
EXPECTED_CHAPTER_TOPOLOGY_SHA256 = "058CF206D2BDE95CB8DFDFB4D274579EBB599B47DA5AD16B8A42B72D5B5ABCA7"
IMPLEMENTED_AUDIT_STATUS = "implemented_in_seed"
FACTORY_AUDIT_STATUSES = {
    "audited_go_not_implemented",
    "audited_go_installer_closure_implemented_recipes_pending",
    IMPLEMENTED_AUDIT_STATUS,
}
REVIEWED_BATCH_STATUSES = {
    "reviewed_patch_plan_not_applied",
    IMPLEMENTED_AUDIT_STATUS,
}
SEMANTIC_REFERENCE_MIGRATIONS = {
    "ae2:controller": {
        "kind": "reviewed_batch_recipe",
        "artifact": "AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:ae2_high_energy/controller",
    },
    "ae2:me_p2p_tunnel": {
        "kind": "reviewed_batch_recipe",
        "artifact": "AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:ae2_high_energy/me_p2p_tunnel",
    },
    "ae2:spatial_anchor": {
        "kind": "reviewed_batch_recipe",
        "artifact": "AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:ae2_high_energy/spatial_anchor",
    },
    "mekanism:isotopic_centrifuge": {
        "kind": "reviewed_batch_recipe",
        "artifact": "MEKANISM_NUCLEAR_CHEMICAL_SPS_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:mekanism_nuclear/isotopic_centrifuge",
    },
    "mekanism:radioactive_waste_barrel": {
        "kind": "reviewed_batch_recipe",
        "artifact": "MEKANISM_NUCLEAR_CHEMICAL_SPS_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:mekanism_nuclear/radioactive_waste_barrel_batch",
    },
    "mekanism:solar_neutron_activator": {
        "kind": "reviewed_batch_recipe",
        "artifact": "MEKANISM_NUCLEAR_CHEMICAL_SPS_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:mekanism_nuclear/solar_neutron_activator",
    },
}
IMPLEMENTED_AUDIT_REFERENCE_MIGRATIONS = {
    "ae2:energy_acceptor": {
        "kind": "audit_recipe",
        "artifact": "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:digital_core/energy_acceptor",
    },
    "ae2:terminal": {
        "kind": "audit_recipe",
        "artifact": "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:digital_core/terminal",
    },
    "ae2:import_bus": {
        "kind": "audit_recipe",
        "artifact": "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:digital_core/import_bus",
    },
    "ae2:molecular_assembler": {
        "kind": "audit_recipe",
        "artifact": "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:digital_core/molecular_assembler",
    },
    "ae2:pattern_provider": {
        "kind": "audit_recipe",
        "artifact": "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:digital_core/pattern_provider",
    },
    "mekanism:enrichment_chamber": {
        "kind": "audit_recipe",
        "artifact": "MEKANISM_PRE_NUCLEAR_MACHINE_CHAIN_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber",
    },
    "mekanism:osmium_compressor": {
        "kind": "audit_recipe",
        "artifact": "MEKANISM_PRE_NUCLEAR_MACHINE_CHAIN_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:mekanism_pre_nuclear/osmium_compressor",
    },
    "mekanism:electrolytic_separator": {
        "kind": "audit_recipe",
        "artifact": "MEKANISM_PRE_NUCLEAR_MACHINE_CHAIN_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator",
    },
    "mekanism:pressurized_reaction_chamber": {
        "kind": "audit_recipe",
        "artifact": "MEKANISM_PRE_NUCLEAR_MACHINE_CHAIN_AUDIT.plan.json",
        "recipe_id": "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber",
    },
}
STOCK_UTILITY_REFERENCE_MIGRATIONS = {
    "ae2:item_storage_cell_4k": {
        "kind": "installed_recipe_with_assignment",
        "artifact": "STOCK_UTILITY_RESTORATION_AUDIT.patch.json",
        "recipe_id": "ae2:network/cells/item_storage_cell_4k",
        "assignment_node": "CR01 — ME System Basics",
    },
    "ae2:16k_crafting_storage": {
        "kind": "installed_recipe_with_assignment",
        "artifact": "STOCK_UTILITY_RESTORATION_AUDIT.patch.json",
        "recipe_id": "ae2:network/crafting/16k_cpu_crafting_storage",
        "assignment_node": "CR01 — Advanced Digital Crafting",
    },
    "ae2:fluix_smart_dense_cable": {
        "kind": "installed_recipe_with_assignment",
        "artifact": "STOCK_UTILITY_RESTORATION_AUDIT.patch.json",
        "recipe_id": "ae2:network/cables/dense_smart_fluix",
        "assignment_node": "CR01 — Enhanced ME System Upgrade",
    },
    "ae2:item_storage_cell_64k": {
        "kind": "installed_recipe_with_assignment",
        "artifact": "STOCK_UTILITY_RESTORATION_AUDIT.patch.json",
        "recipe_id": "ae2:network/cells/item_storage_cell_64k",
        "assignment_node": "CR01 — ME System Advanced",
    },
}
TIER_INSTALLER_REFERENCE_MIGRATIONS = {
    "mekanism:basic_tier_installer": {
        "kind": "managed_recipe",
        "recipe_id": "industrial_colonies:mekanism/tier_installer/basic",
    },
    "mekanism:advanced_tier_installer": {
        "kind": "managed_recipe",
        "recipe_id": "industrial_colonies:mekanism/tier_installer/advanced",
    },
}
NATIVE_ASSIGNMENT_REFERENCE_MIGRATIONS = {
    "tfmg:steel_frame": {
        "kind": "installed_recipe_with_assignment",
        "recipe_id": "tfmg:crafting/materials/steel_frame",
        "assignment_node": "CR01 — Modular Machinery",
    },
}
BIG_REACTOR_AUDIT = "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.plan.json"
BIG_REACTOR_AUDIT_STATUSES = {
    "review_ready_no_shared_mutation",
    IMPLEMENTED_AUDIT_STATUS,
}
BIG_REACTOR_REFERENCE_MIGRATIONS = {
    "bigreactors:basic_reactorcasing": {
        "kind": "managed_recipe",
        "recipe_id": "industrial_colonies:bigreactors/basic_reactor/casing",
    },
    "bigreactors:basic_reactorfuelrod": {
        "kind": "managed_recipe",
        "recipe_id": "industrial_colonies:bigreactors/basic_reactor/fuel_rod",
    },
    "bigreactors:basic_reactorcontrolrod": {
        "kind": "managed_recipe",
        "recipe_id": "industrial_colonies:bigreactors/basic_reactor/control_rod",
    },
    "bigreactors:reprocessorcontroller": {
        "kind": "managed_recipe",
        "recipe_id": "industrial_colonies:bigreactors/reprocessor/controller",
    },
}
BIG_REACTOR_FTB_REWRITES = [
    {
        "path": "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json",
        "json_pointer": "/objective_evidence/bigreactors:basic_reactorcasing/recipe_id",
        "from": "industrial_colonies:auto/bigreactors/basic_reactorcasing",
        "to": "industrial_colonies:bigreactors/basic_reactor/casing",
    },
    {
        "path": "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json",
        "json_pointer": "/objective_evidence/bigreactors:basic_reactorcontrolrod/recipe_id",
        "from": "industrial_colonies:auto/bigreactors/basic_reactorcontrolrod",
        "to": "industrial_colonies:bigreactors/basic_reactor/control_rod",
    },
    {
        "path": "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json",
        "json_pointer": "/objective_evidence/bigreactors:basic_reactorfuelrod/recipe_id",
        "from": "industrial_colonies:auto/bigreactors/basic_reactorfuelrod",
        "to": "industrial_colonies:bigreactors/basic_reactor/fuel_rod",
    },
    {
        "path": "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json",
        "json_pointer": "/objective_evidence/bigreactors:reprocessorcontroller/recipe_id",
        "from": "industrial_colonies:auto/bigreactors/reprocessorcontroller",
        "to": "industrial_colonies:bigreactors/reprocessor/controller",
    },
]


def exact_reference_migrations() -> dict[str, dict[str, str]]:
    return {
        **SEMANTIC_REFERENCE_MIGRATIONS,
        **IMPLEMENTED_AUDIT_REFERENCE_MIGRATIONS,
        **STOCK_UTILITY_REFERENCE_MIGRATIONS,
        **TIER_INSTALLER_REFERENCE_MIGRATIONS,
        **NATIVE_ASSIGNMENT_REFERENCE_MIGRATIONS,
        **BIG_REACTOR_REFERENCE_MIGRATIONS,
    }


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def resource_ids(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, str):
        match = STACK.fullmatch(value.strip())
        if match:
            result.add(match.group(1))
    elif isinstance(value, Mapping):
        for key in ("id", "item", "output"):
            if key in value:
                result.update(resource_ids(value[key]))
    elif isinstance(value, list):
        for child in value:
            result.update(resource_ids(child))
    return result


def recipe_outputs(recipe: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    if "output" in recipe:
        result.update(resource_ids(recipe["output"]))
    if "outputs" in recipe:
        result.update(resource_ids(recipe["outputs"]))
    return result


def walk_dicts(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def parse_registry(path: Path) -> set[str]:
    ids: set[str] = set()
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        value = raw.strip()
        if RESOURCE_ID.fullmatch(value):
            ids.add(value)
    if not ids:
        raise ValueError(f"runtime item export contains no registry IDs: {path}")
    return ids


def installed_recipe_map(path: Path) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            result[str(row.get("recipe_id", ""))] = {
                raw.strip()
                for raw in str(row.get("outputs", "")).split("|")
                if RESOURCE_ID.fullmatch(raw.strip())
            }
    return result


def current_campaign_counts(
    foundations: Mapping[str, Any], dungeon: Mapping[str, Any], endgame: Mapping[str, Any]
) -> dict[str, tuple[int, int]]:
    foundation_quests = foundations.get("chapters", [{}])[0].get("quests", [])
    dungeon_quests = dungeon.get("chapter", {}).get("quests", [])
    endgame_quests = endgame.get("quests", [])
    return {
        "factory_foundations": (
            len(foundation_quests),
            sum(len(quest.get("tasks", [])) for quest in foundation_quests),
        ),
        "dungeon_exploration": (
            len(dungeon_quests),
            sum(len(quest.get("tasks", [])) for quest in dungeon_quests),
        ),
        "industrial_progression": (
            len(endgame_quests),
            sum(len(quest.get("tasks", [])) for quest in endgame_quests),
        ),
    }


def validate_current_sources(
    plan: Mapping[str, Any],
    foundations: Mapping[str, Any],
    dungeon: Mapping[str, Any],
    endgame: Mapping[str, Any],
    errors: list[str],
) -> None:
    actual = current_campaign_counts(foundations, dungeon, endgame)
    require(actual == EXPECTED_CURRENT, f"current FTB campaign counts changed: {actual}", errors)
    snapshot = plan.get("current_campaign_snapshot", {})
    require(snapshot.get("chapter_count") == 3, "snapshot chapter_count must remain 3", errors)
    require(snapshot.get("quest_count") == 45, "snapshot quest_count must remain 45", errors)
    require(snapshot.get("task_count") == 76, "snapshot task_count must remain 76", errors)
    recorded = {
        str(row.get("key")): (int(row.get("quests", -1)), int(row.get("tasks", -1)))
        for row in snapshot.get("chapters", [])
        if isinstance(row, Mapping)
    }
    require(recorded == EXPECTED_CURRENT, f"plan snapshot rows changed: {recorded}", errors)
    foundation_quests = foundations.get("chapters", [{}])[0].get("quests", [])
    last = foundation_quests[-1].get("key") if foundation_quests else None
    require(last == "diesel_engine_commissioning", f"foundation endpoint changed to {last!r}", errors)

    actual_endgame: dict[str, tuple[list[str], str]] = {}
    for quest in endgame.get("quests", []):
        tasks = quest.get("tasks", [])
        item = tasks[0].get("item") if len(tasks) == 1 else ""
        actual_endgame[str(quest.get("key"))] = (list(quest.get("dependencies", [])), str(item))
    require(actual_endgame == EXPECTED_ENDGAME, f"existing endgame chain changed: {actual_endgame}", errors)

    preserved = plan.get("preserved_artifacts", {}).get("existing_endgame_chapter", {})
    require(
        preserved.get("quest_keys") == list(EXPECTED_ENDGAME),
        "plan no longer preserves the three endgame quest keys in order",
        errors,
    )
    preserved_deps = preserved.get("dependencies", {})
    preserved_items = preserved.get("items", [])
    require(
        preserved_deps == {key: value[0] for key, value in EXPECTED_ENDGAME.items()},
        "plan mutates the endgame dependency chain",
        errors,
    )
    require(
        preserved_items == [value[1] for value in EXPECTED_ENDGAME.values()],
        "plan mutates the endgame objective items",
        errors,
    )


def validate_contract(plan: Mapping[str, Any], errors: list[str]) -> None:
    contract = plan.get("campaign_contract", {})
    require(contract.get("guidance_only") is True, "campaign must remain guidance_only", errors)
    require(contract.get("task_types") == ["item"], "only item tasks are permitted", errors)
    for key in (
        "consume_items", "rewards", "recipe_gates", "research_gates", "stages",
        "commands", "checkbox_only_quests",
    ):
        require(contract.get(key) is False, f"campaign contract must keep {key}=false", errors)
    require(
        plan.get("preserved_artifacts", {}).get("chapter_groups_byte_for_byte") is True,
        "chapter_groups.snbt must be preserved byte-for-byte",
        errors,
    )
    require(
        plan.get("generator_implementation", {}).get("status") == "implemented",
        "post-Diesel generator integration must remain implemented",
        errors,
    )


def validate_chapters(plan: Mapping[str, Any], errors: list[str]) -> tuple[set[str], list[str]]:
    chapters = plan.get("chapters", [])
    require(isinstance(chapters, list), "chapters must be an array", errors)
    topology = [
        {
            "key": chapter.get("key"),
            "filename": chapter.get("filename"),
            "order_index": chapter.get("order_index"),
            "entry_dependencies": chapter.get("entry_dependencies", []),
            "quests": [
                {
                    "key": quest.get("key"),
                    "dependencies": quest.get("dependencies", []),
                    "external_dependencies": quest.get("external_dependencies", []),
                    "tasks": quest.get("tasks", []),
                }
                for quest in chapter.get("quests", [])
                if isinstance(quest, Mapping)
            ],
        }
        for chapter in chapters
        if isinstance(chapter, Mapping)
    ]
    topology_sha256 = hashlib.sha256(
        json.dumps(
            topology,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest().upper()
    require(
        topology_sha256 == EXPECTED_CHAPTER_TOPOLOGY_SHA256,
        f"chapter/quest/task topology changed: {topology_sha256}",
        errors,
    )
    chapter_map = {
        str(chapter.get("key")): chapter
        for chapter in chapters
        if isinstance(chapter, Mapping)
    }
    require(set(chapter_map) == set(EXPECTED_CHAPTERS), f"chapter keys changed: {sorted(chapter_map)}", errors)
    require(len(chapter_map) == len(chapters), "chapter keys must be unique", errors)

    existing = {
        "factory_foundations:diesel_engine_commissioning",
        "factory_foundations:first_steel",
    }
    all_new = {
        f"{chapter_key}:{quest.get('key')}"
        for chapter_key, chapter in chapter_map.items()
        for quest in chapter.get("quests", [])
        if isinstance(quest, Mapping)
    }
    known = existing | all_new
    graph: dict[str, set[str]] = {}
    task_items: list[str] = []
    total_quests = 0
    total_tasks = 0

    for chapter_key, (expected_quests, expected_tasks, expected_order) in EXPECTED_CHAPTERS.items():
        chapter = chapter_map.get(chapter_key, {})
        quests = chapter.get("quests", [])
        task_count = sum(len(quest.get("tasks", [])) for quest in quests if isinstance(quest, Mapping))
        require(len(quests) == expected_quests, f"{chapter_key} quest count changed", errors)
        require(task_count == expected_tasks, f"{chapter_key} task count changed", errors)
        require(chapter.get("filename") == chapter_key, f"{chapter_key} filename must match key", errors)
        require(chapter.get("order_index") == expected_order, f"{chapter_key} order_index changed", errors)
        entry_dependencies = chapter.get("entry_dependencies", [])
        require(bool(entry_dependencies), f"{chapter_key} needs an entry dependency", errors)
        for dependency in entry_dependencies:
            require(dependency in known, f"{chapter_key} has unknown entry dependency {dependency}", errors)

        local_keys = [str(quest.get("key")) for quest in quests if isinstance(quest, Mapping)]
        require(len(set(local_keys)) == len(local_keys), f"{chapter_key} repeats a quest key", errors)
        roots = 0
        child_counts: Counter[str] = Counter()
        convergence = False
        for quest in quests:
            if not isinstance(quest, Mapping):
                errors.append(f"{chapter_key} contains a non-object quest")
                continue
            key = str(quest.get("key", ""))
            full_key = f"{chapter_key}:{key}"
            require(bool(key), f"{chapter_key} has a blank quest key", errors)
            require(bool(str(quest.get("title", "")).strip()), f"{full_key} has no title", errors)
            require(bool(str(quest.get("intent", "")).strip()), f"{full_key} has no intent", errors)
            dependencies = list(quest.get("dependencies", []))
            external = list(quest.get("external_dependencies", []))
            if not dependencies:
                roots += 1
            for dependency in dependencies:
                require(dependency in local_keys, f"{full_key} has unknown local dependency {dependency}", errors)
                child_counts[dependency] += 1
            for dependency in external:
                require(dependency in known, f"{full_key} has unknown external dependency {dependency}", errors)
            if len(dependencies) + len(external) >= 2:
                convergence = True
            full_dependencies = {f"{chapter_key}:{dependency}" for dependency in dependencies}
            full_dependencies.update(external)
            if not dependencies:
                full_dependencies.update(entry_dependencies)
            graph[full_key] = full_dependencies

            tasks = quest.get("tasks", [])
            require(bool(tasks), f"{full_key} must have at least one tangible item task", errors)
            seen: set[str] = set()
            for task in tasks:
                if not isinstance(task, Mapping):
                    errors.append(f"{full_key} contains a non-object task")
                    continue
                require(set(task) == {"item", "count"}, f"{full_key} task fields must be item/count only", errors)
                item = str(task.get("item", ""))
                count = task.get("count")
                require(bool(RESOURCE_ID.fullmatch(item)), f"{full_key} has invalid item ID {item!r}", errors)
                require(isinstance(count, int) and not isinstance(count, bool) and count > 0,
                        f"{full_key}/{item} count must be a positive integer", errors)
                require(item not in seen, f"{full_key} repeats item {item}", errors)
                seen.add(item)
                task_items.append(item)
        require(roots >= 1, f"{chapter_key} needs at least one root", errors)
        require(any(count >= 2 for count in child_counts.values()), f"{chapter_key} lacks a branch", errors)
        require(convergence, f"{chapter_key} lacks a convergence quest", errors)
        total_quests += len(quests)
        total_tasks += task_count

    require(total_quests == 40, f"new quest total changed to {total_quests}", errors)
    require(total_tasks == 104, f"new task total changed to {total_tasks}", errors)
    factory_quests = [
        quest
        for quest in chapter_map.get("mekanized_industry", {}).get("quests", [])
        if isinstance(quest, Mapping) and quest.get("key") == "first_basic_factory"
    ]
    require(len(factory_quests) == 1, "first_basic_factory guidance quest is missing", errors)
    if factory_quests:
        factory_quest = factory_quests[0]
        require(
            factory_quest.get("dependencies") == ["base_processing_cluster"],
            "first_basic_factory must follow the base processing cluster",
            errors,
        )
        require(
            factory_quest.get("tasks") == [
                {"item": "mekanism:basic_enriching_factory", "count": 1},
                {"item": "mekanism:enrichment_chamber", "count": 1},
                {"item": "mekanism:basic_tier_installer", "count": 1},
            ],
            "first_basic_factory must observe predecessor, installer, and result",
            errors,
        )
        factory_intent = str(factory_quest.get("intent", "")).lower()
        for phrase in ("right-click", "consumed", "preserves", "disabled", "factory", "energy cube"):
            require(
                phrase in factory_intent,
                f"first_basic_factory guidance lost required phrase {phrase!r}",
                errors,
            )
    totals = plan.get("proposed_totals_after_implementation", {})
    expected_totals = {
        "new_chapters": 5, "new_quests": 40, "new_item_tasks": 104,
        "total_chapters": 8, "total_quests": 85, "total_tasks": 180,
    }
    require(totals == expected_totals, f"recorded implementation totals changed: {totals}", errors)

    state: dict[str, int] = {}

    def visit(node: str, stack: list[str]) -> None:
        current = state.get(node, 0)
        if current == 1:
            errors.append(f"quest dependency cycle: {' -> '.join(stack + [node])}")
            return
        if current == 2 or node not in graph:
            return
        state[node] = 1
        for dependency in graph[node]:
            visit(dependency, stack + [node])
        state[node] = 2

    for node in graph:
        visit(node, [])
    return set(task_items), task_items


def validate_evidence(
    plan: Mapping[str, Any],
    task_items: set[str],
    registry_ids: set[str],
    managed: Mapping[str, Any],
    physical: Mapping[str, Any],
    assignments: Mapping[str, Any],
    installed_recipes: Mapping[str, set[str]],
    errors: list[str],
) -> None:
    evidence = plan.get("objective_evidence", {})
    require(isinstance(evidence, Mapping), "objective_evidence must be an object", errors)
    require(set(evidence) == task_items, "objective_evidence must exactly cover proposed task items", errors)
    managed_by_id = {
        str(recipe.get("id")): recipe
        for recipe in managed.get("recipes", [])
        if isinstance(recipe, Mapping)
    }
    managed_removals = {
        str(recipe_id)
        for recipe in managed.get("recipes", [])
        if isinstance(recipe, Mapping)
        for recipe_id in recipe.get("remove", [])
    } | {
        str(recipe_id) for recipe_id in managed.get("additional_removals", [])
    }
    physical_entries: dict[str, Mapping[str, Any]] = {}
    for group in physical.get("canonical_output_groups", []):
        for entry in group.get("outputs", []):
            if isinstance(entry, Mapping):
                physical_entries[str(entry.get("output"))] = entry
    assignment_nodes = assignments.get("nodes", {})
    audit_cache: dict[str, Mapping[str, Any]] = {}

    for item, expected in exact_reference_migrations().items():
        require(
            evidence.get(item) == expected,
            f"{item}: semantic recipe reference migration drifted",
            errors,
        )
    retired_auto_references = sorted(
        item
        for item, row in evidence.items()
        if isinstance(row, Mapping)
        and str(row.get("recipe_id", "")).startswith(
            "industrial_colonies:auto/"
        )
    )
    require(
        not retired_auto_references,
        f"retired automatic recipe references survive: {retired_auto_references}",
        errors,
    )

    big_audit_path = PROJECT / BIG_REACTOR_AUDIT
    big_audit: Mapping[str, Any] = {}
    require(
        big_audit_path.is_file(),
        f"Big Reactors batch artifact is missing: {BIG_REACTOR_AUDIT}",
        errors,
    )
    if big_audit_path.is_file():
        big_audit = audit_cache.setdefault(BIG_REACTOR_AUDIT, load_object(big_audit_path))
        require(
            big_audit.get("status") in BIG_REACTOR_AUDIT_STATUSES,
            f"Big Reactors batch has unsupported status {big_audit.get('status')!r}",
            errors,
        )
        targets = {
            str(candidate.get("output")): candidate
            for candidate in big_audit.get("targets", [])
            if isinstance(candidate, Mapping)
        }
        for item, expected in BIG_REACTOR_REFERENCE_MIGRATIONS.items():
            target = targets.get(item, {})
            expected_auto = f"industrial_colonies:auto/{item.replace(':', '/', 1)}"
            require(
                target.get("source_owned_id") == expected["recipe_id"]
                and target.get("automatic_managed_id") == expected_auto,
                f"{item}: Big Reactors target mapping drifted",
                errors,
            )
        require(
            big_audit.get("dependency_rewrite_contract", {}).get(
                "ftb_guidance_plan_rewrites"
            ) == BIG_REACTOR_FTB_REWRITES,
            "Big Reactors FTB guidance rewrite inventory drifted",
            errors,
        )

    for item in sorted(task_items):
        require(item in registry_ids, f"objective item is absent from runtime registry: {item}", errors)
        row = evidence.get(item, {})
        kind = row.get("kind") if isinstance(row, Mapping) else None
        recipe_id = str(row.get("recipe_id", "")) if isinstance(row, Mapping) else ""
        if kind == "managed_recipe":
            recipe = managed_by_id.get(recipe_id)
            if item in BIG_REACTOR_REFERENCE_MIGRATIONS:
                if big_audit.get("status") == IMPLEMENTED_AUDIT_STATUS:
                    require(recipe is not None, f"{item}: implemented managed recipe is missing: {recipe_id}", errors)
                    if recipe is not None:
                        require(item in recipe_outputs(recipe), f"{item}: {recipe_id} does not output the item", errors)
            else:
                require(recipe is not None, f"{item}: managed recipe is missing: {recipe_id}", errors)
                if recipe is not None:
                    require(item in recipe_outputs(recipe), f"{item}: {recipe_id} does not output the item", errors)
        elif kind == "reviewed_batch_recipe":
            expected = {
                **SEMANTIC_REFERENCE_MIGRATIONS,
                **BIG_REACTOR_REFERENCE_MIGRATIONS,
            }.get(item)
            require(expected is not None, f"{item}: unapproved reviewed batch reference", errors)
            artifact = str(row.get("artifact", ""))
            artifact_path = PROJECT / artifact
            require(
                expected is not None and artifact == expected.get("artifact"),
                f"{item}: reviewed batch artifact drifted",
                errors,
            )
            require(
                artifact_path.is_file(),
                f"{item}: reviewed batch artifact is missing: {artifact}",
                errors,
            )
            if not artifact_path.is_file():
                continue
            audit = audit_cache.setdefault(artifact, load_object(artifact_path))
            require(
                audit.get("status") in REVIEWED_BATCH_STATUSES,
                f"{item}: reviewed batch has unsupported status {audit.get('status')!r}",
                errors,
            )
            matches = [
                candidate
                for candidate in audit.get("replacement_contracts", [])
                if isinstance(candidate, Mapping) and candidate.get("id") == recipe_id
            ]
            require(
                len(matches) == 1,
                f"{item}: reviewed batch recipe ID is not exact and unique: {recipe_id}",
                errors,
            )
            require(
                bool(matches) and item in recipe_outputs(matches[0]),
                f"{item}: reviewed batch recipe {recipe_id} does not output the item",
                errors,
            )
        elif kind == "audit_recipe":
            expected = IMPLEMENTED_AUDIT_REFERENCE_MIGRATIONS.get(item)
            if expected is not None:
                require(row == expected, f"{item}: implemented audit reference drifted", errors)
            artifact = str(row.get("artifact", ""))
            artifact_path = PROJECT / artifact
            require(artifact_path.is_file(), f"{item}: audit artifact is missing: {artifact}", errors)
            if not artifact_path.is_file():
                continue
            audit = audit_cache.setdefault(artifact, load_object(artifact_path))
            require(
                audit.get("status") == IMPLEMENTED_AUDIT_STATUS,
                f"{item}: audit artifact {artifact} is not implemented_in_seed",
                errors,
            )
            matches = [
                node for node in walk_dicts(audit)
                if node.get("id") == recipe_id or node.get("recipe_id") == recipe_id
            ]
            require(bool(matches), f"{item}: audit recipe ID is missing: {recipe_id}", errors)
            require(
                any(item in recipe_outputs(match) for match in matches),
                f"{item}: audit recipe {recipe_id} does not output the item",
                errors,
            )
            if expected is not None:
                exact_matches = [
                    candidate
                    for candidate in audit.get("replacement_contracts", [])
                    if isinstance(candidate, Mapping) and candidate.get("id") == recipe_id
                ]
                require(
                    len(exact_matches) == 1,
                    f"{item}: implemented audit recipe ID is not exact and unique: {recipe_id}",
                    errors,
                )
        elif kind == "tier_installer_upgrade":
            expected = {
                "kind": "tier_installer_upgrade",
                "artifact": "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json",
                "base_item": "mekanism:enrichment_chamber",
                "installer_item": "mekanism:basic_tier_installer",
                "disabled_direct_recipe": "mekanism:factory/basic/enriching",
                "tier": "basic",
                "process": "enriching",
                "assignment_node": "CR01 — Modular Machinery",
            }
            require(item == "mekanism:basic_enriching_factory", f"{item}: unsupported installer-upgrade objective", errors)
            require(row == expected, f"{item}: Tier Installer upgrade evidence drifted", errors)
            artifact = str(row.get("artifact", ""))
            artifact_path = PROJECT / artifact
            require(artifact_path.is_file(), f"{item}: Factory installer audit is missing: {artifact}", errors)
            if not artifact_path.is_file():
                continue
            audit = audit_cache.setdefault(artifact, load_object(artifact_path))
            require(
                audit.get("schema_version") == 3
                and audit.get("status") == IMPLEMENTED_AUDIT_STATUS
                and audit.get("decision") == "INSTALLER_ONLY_FACTORY_UPGRADES_WITH_DIRECT_RECIPES_DISABLED",
                f"{item}: Factory installer audit is not the implemented installer-only contract",
                errors,
            )
            contract = audit.get("installer_upgrade_contract", {})
            require(
                contract.get("construction_route") == "right_click_immediate_predecessor_with_tier_installer"
                and contract.get("installer_consumed") is True
                and contract.get("direct_factory_recipes_disabled") is True
                and contract.get("managed_factory_recipe_count") == 0,
                f"{item}: Factory installer-only construction contract drifted",
                errors,
            )
            tier_rows = {
                str(value.get("tier")): value
                for value in audit.get("tiers", [])
                if isinstance(value, Mapping)
            }
            process_rows = {
                str(value.get("process")): value
                for value in audit.get("processes", [])
                if isinstance(value, Mapping)
            }
            tier = str(row.get("tier", ""))
            process = str(row.get("process", ""))
            tier_row = tier_rows.get(tier, {})
            process_row = process_rows.get(process, {})
            base_item = str(row.get("base_item", ""))
            installer_item = str(row.get("installer_item", ""))
            direct_recipe = str(row.get("disabled_direct_recipe", ""))
            require(
                item == f"mekanism:{tier}_{process}_factory"
                and process_row.get("base_machine") == base_item
                and tier_row.get("installer") == installer_item,
                f"{item}: Tier Installer predecessor/tier identity changed",
                errors,
            )
            require(
                direct_recipe == f"mekanism:factory/{tier}/{process}"
                and direct_recipe in managed_removals
                and direct_recipe not in set(managed.get("preserve_recipe_ids", [])),
                f"{item}: direct Factory recipe is not exactly disabled",
                errors,
            )
            installer_recipe_id = contract.get("tier_installer_recipe_ids", {}).get(tier)
            installer_recipe = managed_by_id.get(installer_recipe_id)
            require(
                installer_recipe is not None
                and installer_item in recipe_outputs(installer_recipe),
                f"{item}: managed Tier Installer producer is missing",
                errors,
            )
            require(
                not any(item in recipe_outputs(recipe) for recipe in managed_by_id.values()),
                f"{item}: a forbidden direct managed Factory producer survives",
                errors,
            )
            closure = audit.get("installer_bypass_closure", {})
            blacklist_path = PROJECT / str(closure.get("resource_path", ""))
            require(blacklist_path.is_file(), f"{item}: installer blacklist resource is missing", errors)
            if blacklist_path.is_file():
                blacklist = load_object(blacklist_path)
                blocked = set(blacklist.get("values", []))
                require(
                    base_item not in blocked and item not in blocked,
                    f"{item}: Tier Installer runtime path is blocked by the installer blacklist",
                    errors,
                )
            node = str(row.get("assignment_node", ""))
            require(
                item in assignment_nodes.get(node, {}).get("unlocks", []),
                f"{item}: assignment node {node!r} no longer documents the runtime output",
                errors,
            )
        elif kind == "factory_restoration_contract":
            artifact = str(row.get("artifact", ""))
            artifact_path = PROJECT / artifact
            require(
                artifact == "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json"
                and artifact_path.is_file(),
                f"{item}: factory restoration audit artifact is missing: {artifact}",
                errors,
            )
            if not artifact_path.is_file():
                continue
            audit = audit_cache.setdefault(artifact, load_object(artifact_path))
            require(
                audit.get("status") in FACTORY_AUDIT_STATUSES,
                f"{item}: factory restoration audit has unsupported status {audit.get('status')!r}",
                errors,
            )
            tier = str(row.get("tier", ""))
            process = str(row.get("process", ""))
            source_recipe_id = str(row.get("source_recipe_id", ""))
            expected_item = f"mekanism:{tier}_{process}_factory"
            expected_source = f"mekanism:factory/{tier}/{process}"
            expected_recipe = f"industrial_colonies:mekanism/factory/{tier}_{process}"
            require(item == expected_item, f"{item}: factory tier/process identity changed", errors)
            require(source_recipe_id == expected_source, f"{item}: factory source ID changed", errors)
            require(recipe_id == expected_recipe, f"{item}: future managed recipe ID changed", errors)
            require(
                source_recipe_id in audit.get("source_sha256", {}),
                f"{item}: factory audit lacks pinned source evidence {source_recipe_id}",
                errors,
            )
            tier_rows = {
                str(value.get("tier")): value
                for value in audit.get("tiers", [])
                if isinstance(value, Mapping)
            }
            process_rows = {
                str(value.get("process")): value
                for value in audit.get("processes", [])
                if isinstance(value, Mapping)
            }
            require(tier in tier_rows, f"{item}: factory audit lacks tier {tier}", errors)
            require(process in process_rows, f"{item}: factory audit lacks process {process}", errors)
            errors.append(f"{item}: retired direct Factory recipe evidence kind survives")
        elif kind == "physical_output_contract":
            entry = physical_entries.get(item)
            require(entry is not None, f"{item}: physical output contract is missing", errors)
            if entry is not None:
                require(
                    recipe_id in entry.get("recipe_ids", []),
                    f"{item}: physical output contract lost recipe {recipe_id}",
                    errors,
                )
        elif kind == "installed_recipe_with_assignment":
            expected = STOCK_UTILITY_REFERENCE_MIGRATIONS.get(item)
            if expected is not None:
                require(row == expected, f"{item}: stock-utility evidence drifted", errors)
                artifact = str(row.get("artifact", ""))
                artifact_path = PROJECT / artifact
                require(
                    artifact_path.is_file(),
                    f"{item}: stock-utility artifact is missing: {artifact}",
                    errors,
                )
                if artifact_path.is_file():
                    stock_audit = audit_cache.setdefault(artifact, load_object(artifact_path))
                    require(
                        stock_audit.get("status") == "implemented",
                        f"{item}: stock-utility artifact is not implemented",
                        errors,
                    )
                    stock_entries = [
                        candidate
                        for candidate in stock_audit.get("entries", [])
                        if isinstance(candidate, Mapping) and candidate.get("output") == item
                    ]
                    require(
                        len(stock_entries) == 1,
                        f"{item}: stock-utility audit entry is not exact and unique",
                        errors,
                    )
                    if len(stock_entries) == 1:
                        stock_entry = stock_entries[0]
                        require(
                            stock_entry.get("source_recipe_id") == recipe_id
                            and recipe_id in stock_entry.get("exact_source_recipe_ids", [])
                            and stock_entry.get("node") == row.get("assignment_node"),
                            f"{item}: stock-utility source recipe or assignment drifted",
                            errors,
                        )
            native_expected = NATIVE_ASSIGNMENT_REFERENCE_MIGRATIONS.get(item)
            if native_expected is not None:
                require(row == native_expected, f"{item}: native assignment evidence drifted", errors)
            require(recipe_id in installed_recipes, f"{item}: installed recipe is missing: {recipe_id}", errors)
            require(item in installed_recipes.get(recipe_id, set()), f"{item}: installed recipe output changed", errors)
            node = str(row.get("assignment_node", ""))
            unlocks = assignment_nodes.get(node, {}).get("unlocks", [])
            require(item in unlocks, f"{item}: assignment node {node!r} no longer audits the output", errors)
        elif kind == "assignment_runtime_output":
            require(not recipe_id, f"{item}: runtime-only output must not invent a recipe ID", errors)
            node = str(row.get("assignment_node", ""))
            unlocks = assignment_nodes.get(node, {}).get("unlocks", [])
            require(item in unlocks, f"{item}: runtime output is absent from assignment node {node!r}", errors)
        else:
            errors.append(f"{item}: unsupported evidence kind {kind!r}")


def validate_deferrals(plan: Mapping[str, Any], task_items: set[str], errors: list[str]) -> None:
    deferred = plan.get("deferred_unstable_objectives", [])
    ids = {str(row.get("id")) for row in deferred if isinstance(row, Mapping)}
    expected = {
        "allthemodium_pairwise_alloy_objectives",
        "advanced_electronics_convergence_item",
        "typed_p2p_variants",
        "chemical_only_milestones",
    }
    require(ids == expected, f"deferred objective set changed: {sorted(ids)}", errors)
    deferred_items = {
        item
        for row in deferred
        if isinstance(row, Mapping)
        for item in row.get("items", [])
    }
    overlap = sorted(task_items & deferred_items)
    require(not overlap, f"unstable/deferred items leaked into quests: {overlap}", errors)


def validate_plan(
    plan: Mapping[str, Any],
    *,
    registry_ids: set[str],
    managed: Mapping[str, Any],
    physical: Mapping[str, Any],
    assignments: Mapping[str, Any],
    installed_recipes: Mapping[str, set[str]],
    foundations: Mapping[str, Any],
    dungeon: Mapping[str, Any],
    endgame: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    require(plan.get("schema_version") == 1, "schema_version must be 1", errors)
    require(plan.get("status") == "implemented", "status must remain implemented", errors)
    validate_contract(plan, errors)
    validate_current_sources(plan, foundations, dungeon, endgame, errors)
    task_items, _ = validate_chapters(plan, errors)
    validate_evidence(
        plan, task_items, registry_ids, managed, physical, assignments,
        installed_recipes, errors,
    )
    validate_deferrals(plan, task_items, errors)
    return errors


def run_mutation_tests(plan: Mapping[str, Any], context: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []

    def expect(label: str, mutated: Mapping[str, Any], fragment: str) -> None:
        errors = validate_plan(mutated, **context)
        if not any(fragment in error for error in errors):
            failures.append(f"mutation {label!r} was not rejected with {fragment!r}: {errors[:4]}")

    mutated = copy.deepcopy(plan)
    mutated["campaign_contract"]["rewards"] = True
    expect("reward gate", mutated, "rewards=false")

    mutated = copy.deepcopy(plan)
    mutated["chapters"][0]["quests"][0]["dependencies"] = [
        mutated["chapters"][0]["quests"][-1]["key"]
    ]
    expect("dependency cycle", mutated, "dependency cycle")

    mutated = copy.deepcopy(plan)
    original = mutated["chapters"][0]["quests"][0]["tasks"][0]["item"]
    mutated["chapters"][0]["quests"][0]["tasks"][0]["item"] = "industrial_colonies:not_registered"
    mutated["objective_evidence"]["industrial_colonies:not_registered"] = mutated["objective_evidence"].pop(original)
    expect("unknown item", mutated, "absent from runtime registry")

    mutated = copy.deepcopy(plan)
    mutated["chapters"][0]["quests"][0]["tasks"].append(
        {"item": "ae2:item_p2p_tunnel", "count": 1}
    )
    mutated["objective_evidence"]["ae2:item_p2p_tunnel"] = {
        "kind": "managed_recipe", "recipe_id": "industrial_colonies:auto/ae2/item_p2p_tunnel"
    }
    expect("deferred objective", mutated, "deferred items leaked")

    mutated = copy.deepcopy(plan)
    mutated["preserved_artifacts"]["existing_endgame_chapter"]["dependencies"]["industrial_star"] = []
    expect("endgame mutation", mutated, "mutates the endgame dependency chain")

    mutated = copy.deepcopy(plan)
    mutated["objective_evidence"]["ae2:controller"]["recipe_id"] = (
        "industrial_colonies:auto/ae2/controller"
    )
    expect("retired semantic recipe reference", mutated, "semantic recipe reference migration drifted")

    mutated = copy.deepcopy(plan)
    mutated["objective_evidence"]["ae2:energy_acceptor"]["recipe_id"] = (
        "industrial_colonies:auto/ae2/energy_acceptor"
    )
    expect("Digital Core evidence", mutated, "semantic recipe reference migration drifted")

    mutated = copy.deepcopy(plan)
    mutated["objective_evidence"]["mekanism:enrichment_chamber"]["artifact"] = (
        "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json"
    )
    expect("pre-nuclear evidence", mutated, "semantic recipe reference migration drifted")

    mutated = copy.deepcopy(plan)
    mutated["objective_evidence"]["ae2:item_storage_cell_4k"]["assignment_node"] = (
        "CR01 — Wrong Node"
    )
    expect("stock-utility evidence", mutated, "semantic recipe reference migration drifted")

    mutated = copy.deepcopy(plan)
    mutated["objective_evidence"]["bigreactors:basic_reactorcasing"]["recipe_id"] = (
        "industrial_colonies:auto/bigreactors/basic_reactorcasing"
    )
    expect("Big Reactors evidence", mutated, "semantic recipe reference migration drifted")

    mutated = copy.deepcopy(plan)
    mutated["objective_evidence"]["ae2:charger"]["recipe_id"] = (
        "industrial_colonies:auto/ae2/charger"
    )
    expect("global retired auto invariant", mutated, "retired automatic recipe references survive")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--physical", type=Path, default=DEFAULT_PHYSICAL)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--items", type=Path, default=DEFAULT_ITEMS)
    parser.add_argument("--recipes", type=Path, default=DEFAULT_RECIPES)
    parser.add_argument("--foundations", type=Path, default=DEFAULT_FOUNDATIONS)
    parser.add_argument("--dungeon", type=Path, default=DEFAULT_DUNGEON)
    parser.add_argument("--endgame", type=Path, default=DEFAULT_ENDGAME)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        plan = load_object(args.plan.resolve())
        context = {
            "registry_ids": parse_registry(args.items.resolve()),
            "managed": load_object(args.manifest.resolve()),
            "physical": load_object(args.physical.resolve()),
            "assignments": load_object(args.assignments.resolve()),
            "installed_recipes": installed_recipe_map(args.recipes.resolve()),
            "foundations": load_object(args.foundations.resolve()),
            "dungeon": load_object(args.dungeon.resolve()),
            "endgame": load_object(args.endgame.resolve()),
        }
        errors = validate_plan(plan, **context)
        if args.self_test and not errors:
            errors.extend(run_mutation_tests(plan, context))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("FAIL: post-Diesel FTB guidance audit is invalid:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    suffix = " plus eleven mutation checks" if args.self_test else ""
    print(
        "PASS: 5 implemented chapters, 40 quests, and 104 installed/evidenced "
        f"item tasks validated{suffix}; 25 exact migrated evidence references contain "
        "zero retired automatic IDs, and the existing 3-item endgame is unchanged."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
