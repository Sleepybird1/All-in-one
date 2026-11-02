#!/usr/bin/env python3
"""Validate the read-only Big Reactors bulk/controller redesign package."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import re
import sqlite3
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_bigreactors_bulk_structures_audit as audit_builder
import build_managed_recipe_manifest as manifest_builder


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
DEFAULT_PLAN = PROJECT / "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.plan.json"
DEFAULT_PATCH = PROJECT / "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.patch.json"
DEFAULT_AUTOMATIC = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
DEFAULT_CATALOG = WORKSPACE / "outputs/recipe-catalog-current/recipe_catalog.sqlite"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
DEFAULT_FTB = PROJECT / "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json"
DEFAULT_PHYSICAL = PROJECT / "progression/physical_recipe_tiers.json"
DEFAULT_RESTORATION = PROJECT / "STOCK_UTILITY_RESTORATION_AUDIT.patch.json"
DEFAULT_ENVIRONMENTS = (
    PROJECT / "src/main/resources/data/industrial_colonies/tier_recipe_environments.json"
)
DEFAULT_NUCLEAR_QUEST = (
    PROJECT / "pack-config-overrides/ftbquests/quests/chapters/nuclear_engineering.snbt"
)
DEFAULT_COMPUTERCRAFT_DOC = PROJECT / "COMPUTERCRAFT_REACTOR_FACTORY_PROGRESSION.md"
GENERATOR = TOOLS / "generate_managed_recipe_overhaul.py"

EXPECTED_SCOPE = {
    "outputs": 27,
    "source_owned_contracts": 27,
    "automatic_owners_retired": 27,
    "installed_recipe_producers_removed_exactly": 49,
    "compacting_contracts": 22,
    "controller_mechanical_crafting_contracts": 5,
    "assignment_changes": 0,
    "source_recipe_overrides_retired": 2,
    "ftb_guidance_id_rewrites": 4,
    "physical_tier_id_rewrites": 1,
}
EXPECTED_TYPE_COUNTS = Counter({"compacting": 22, "mechanical_crafting": 5})
EXPECTED_COMPILED_TYPE_COUNTS = Counter(
    {"kjsgen:create_compacting": 22, "kjsgen:create_mechanical_crafting": 5}
)
EXPECTED_MACHINE_COUNTS = Counter(
    {
        audit_builder.INDUSTRIAL: 9,
        audit_builder.WEATHERED: 6,
        audit_builder.RADIANT: 7,
    }
)
EXPECTED_CONTROLLER_COUNTS = {
    "industrial_colonies:bigreactors/basic_turbine/controller": (1, 4),
    "industrial_colonies:bigreactors/energizer/controller": (1, 4),
    "industrial_colonies:bigreactors/fluidizer/controller": (1, 4),
    "industrial_colonies:bigreactors/reprocessor/controller": (2, 4),
    "industrial_colonies:bigreactors/reinforced_turbine/controller": (2, 4),
}
EXPECTED_FTB_MAP = {
    "bigreactors:basic_reactorcasing": "industrial_colonies:bigreactors/basic_reactor/casing",
    "bigreactors:basic_reactorfuelrod": "industrial_colonies:bigreactors/basic_reactor/fuel_rod",
    "bigreactors:basic_reactorcontrolrod": "industrial_colonies:bigreactors/basic_reactor/control_rod",
    "bigreactors:reprocessorcontroller": "industrial_colonies:bigreactors/reprocessor/controller",
}
EXPECTED_OUTPUT_COUNTS = {
    "bigreactors:basic_reactorcasing": 8,
    "bigreactors:basic_reactorcontrolrod": 2,
    "bigreactors:basic_reactorfuelrod": 4,
    "bigreactors:basic_turbinecasing": 8,
    "bigreactors:basic_turbinerotorblade": 4,
    "bigreactors:basic_turbinerotorshaft": 4,
    "bigreactors:energizercasing": 8,
    "bigreactors:fluidizercasing": 8,
    "bigreactors:reinforced_reactorcasing": 8,
    "bigreactors:reinforced_reactorcontrolrod": 2,
    "bigreactors:reinforced_reactorfuelrod": 4,
    "bigreactors:reinforced_turbinecasing": 8,
    "bigreactors:reinforced_turbinerotorblade": 4,
    "bigreactors:reinforced_turbinerotorshaft": 4,
    "bigreactors:reprocessorcasing": 8,
}
CONTROLLER_OUTPUTS = {
    "bigreactors:basic_turbinecontroller",
    "bigreactors:energizercontroller",
    "bigreactors:fluidizercontroller",
    "bigreactors:reprocessorcontroller",
    "bigreactors:reinforced_turbinecontroller",
}
PRECRITICAL_OUTPUTS = {
    "bigreactors:basic_reactorcasing",
    "bigreactors:basic_reactorcontrolrod",
    "bigreactors:basic_reactorfuelrod",
    "bigreactors:energizercasing",
    "bigreactors:energizercontroller",
    "bigreactors:fluidizercasing",
    "bigreactors:fluidizercontroller",
}
FUEL_PROCESSING_OUTPUTS = {
    "bigreactors:energizercasing",
    "bigreactors:energizercontroller",
    "bigreactors:fluidizercasing",
    "bigreactors:fluidizercontroller",
}
ADVANCED_OUTPUTS = {
    "bigreactors:reinforced_reactorcasing",
    "bigreactors:reinforced_reactorcontrolrod",
    "bigreactors:reinforced_reactorfuelrod",
    "bigreactors:reinforced_turbinecasing",
    "bigreactors:reinforced_turbinecontroller",
    "bigreactors:reinforced_turbinerotorbearing",
    "bigreactors:reinforced_turbinerotorblade",
    "bigreactors:reinforced_turbinerotorshaft",
}
FORBIDDEN_PRECRITICAL_FRAGMENTS = (
    "cyanite",
    "blutonium",
    "magentite",
    "plutonium",
    "nuclear_waste",
    "spent_nuclear_waste",
    "fissile_fuel",
    "reprocessor",
    "reinforced_",
)
GENERIC_RING = ["ABABA", "BCDCB", "ADEDA", "BCDCB", "ABABA"]


def load_json(path: Path) -> dict[str, Any]:
    return audit_builder.load_json(path)


def output_of(recipe: dict[str, Any]) -> tuple[int, str]:
    return audit_builder.output_of(recipe)


def recipe_ingredients(recipe: dict[str, Any]) -> Counter[str]:
    values: Counter[str] = Counter()
    if recipe.get("type") == "compacting":
        for raw in recipe.get("inputs", []):
            count, identity = audit_builder.split_stack(raw)
            values[identity] += count
    elif recipe.get("type") == "mechanical_crafting":
        pattern = recipe.get("pattern", [])
        key = recipe.get("key", {})
        for row in pattern:
            for symbol in row:
                if symbol != " ":
                    values[key[symbol]] += 1
    return values


def recipes_by_id(seed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for recipe in seed.get("recipes", []):
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str):
            result[recipe["id"]] = recipe
    return result


def contracts_by_output(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    values = plan.get("replacement_contracts", [])
    if not isinstance(values, list):
        return {}
    result = {}
    for recipe in values:
        try:
            output = output_of(recipe)[1]
        except (ValueError, KeyError, TypeError):
            continue
        result[output] = recipe
    return result


def pointer_get(root: Any, pointer: str) -> Any:
    value = root
    for part in pointer.lstrip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            value = value[int(part)]
        else:
            value = value[part]
    return value


def validate_metadata(plan: dict[str, Any], patch: dict[str, Any], failures: list[str]) -> None:
    if plan.get("schema_version") != 1:
        failures.append("plan schema_version must be 1")
    if plan.get("status") not in {
        "review_ready_no_shared_mutation",
        "implemented_in_seed",
    }:
        failures.append("plan status is neither review-ready nor implemented")
    if plan.get("decision") != "GO_WITH_27_SOURCE_OWNED_TFMG_FIRST_NUCLEAR_CONTRACTS":
        failures.append("review decision changed")
    if plan.get("scope") != EXPECTED_SCOPE:
        failures.append("review scope counts changed")
    expected_validation = {
        "compiled_contracts": 27,
        "compiled_type_counts": {"compacting": 22, "mechanical_crafting": 5},
        "compiled_machine_counts": {
            audit_builder.INDUSTRIAL: 9,
            audit_builder.WEATHERED: 6,
            audit_builder.RADIANT: 7,
        },
        "exact_removals": 49,
        "static_single_owner_outputs": 27,
        "nonrecipe_self_drop_loot_tables": 27,
        "preserved_utility_removals": 0,
        "mutation_tests": 36,
    }
    if plan.get("validation_expectations") != expected_validation:
        failures.append("validation expectation summary changed")
    if patch.get("plan_id") != plan.get("plan_id"):
        failures.append("patch plan_id no longer matches audit plan")
    if patch.get("mode") != "declarative_seed_patch":
        failures.append("patch mode changed")
    if patch.get("assignments") != {"changes": []}:
        failures.append("patch unexpectedly changes assignments")
    seed_patch = patch.get("seed", {})
    if seed_patch.get("remove_source_recipe_override_outputs") != [
        "bigreactors:basic_reactorfuelrod",
        "bigreactors:reinforced_reactorfuelrod",
    ]:
        failures.append("patch must retire exactly the two fuel-rod source overrides")
    if seed_patch.get("additional_removals") != []:
        failures.append("patch unexpectedly adds broad removals")
    if seed_patch.get("authoritative_dependency_rewrites") != []:
        failures.append("patch unexpectedly rewrites current seed dependencies")
    try:
        expected_patch = audit_builder.build_patch(plan)
    except (ValueError, KeyError, TypeError) as error:
        failures.append(f"cannot derive deterministic static patch: {error}")
    else:
        if patch != expected_patch:
            failures.append("static patch no longer matches its reviewed plan")


def validate_determinism(
    plan: dict[str, Any],
    patch: dict[str, Any],
    catalog: Path,
    mods: Path,
    automatic: dict[str, Any],
    seed: dict[str, Any],
    assignments: dict[str, Any],
    ftb: dict[str, Any],
    physical: dict[str, Any],
    restoration: dict[str, Any],
    failures: list[str],
) -> None:
    try:
        rebuilt = audit_builder.build_plan(
            catalog,
            mods,
            automatic,
            seed,
            assignments,
            ftb,
            physical,
            restoration,
        )
        rebuilt_again = audit_builder.build_plan(
            catalog,
            mods,
            automatic,
            seed,
            assignments,
            ftb,
            physical,
            restoration,
        )
    except (OSError, ValueError, sqlite3.Error, zipfile.BadZipFile) as error:
        failures.append(f"deterministic audit rebuild failed: {error}")
        return
    if rebuilt != rebuilt_again:
        failures.append("audit builder is nondeterministic")
    if rebuilt != plan:
        failures.append("checked-in plan drifted from deterministic installed-source audit")
    try:
        rebuilt_patch = audit_builder.build_patch(plan)
    except (ValueError, KeyError, TypeError) as error:
        failures.append(f"deterministic patch build failed: {error}")
        return
    if rebuilt_patch != patch:
        failures.append("checked-in patch drifted from deterministic builder output")


def validate_source_and_loot(
    plan: dict[str, Any], mods: Path, failures: list[str]
) -> None:
    removals: set[str] = set()
    targets = plan.get("targets", [])
    if len(targets) != 27:
        failures.append("target inventory must contain 27 entries")
        return
    for target in targets:
        output = target.get("output")
        producers = target.get("installed_producers", [])
        if not producers:
            failures.append(f"target has no installed producers: {output}")
            continue
        for producer in producers:
            recipe_id = producer.get("recipe_id")
            if recipe_id in removals:
                failures.append(f"installed producer is claimed twice: {recipe_id}")
            removals.add(recipe_id)
            jar = mods / producer.get("source_jar", "")
            path = producer.get("source_path")
            try:
                with zipfile.ZipFile(jar) as archive:
                    document = json.loads(archive.read(path))
            except (OSError, KeyError, ValueError, zipfile.BadZipFile) as error:
                failures.append(f"cannot read installed source recipe {recipe_id}: {error}")
                continue
            text = json.dumps(document, separators=(",", ":"))
            if output not in text:
                failures.append(f"installed source recipe no longer emits {output}: {recipe_id}")

        evidence = target.get("nonrecipe_acquisition", {})
        expected = (
            f"{audit_builder.EXTREME_REACTORS_JAR}!/data/bigreactors/loot_table/blocks/"
            f"{output.split(':', 1)[1]}.json"
        )
        if evidence.get("block_loot_table") != expected:
            failures.append(f"self-block loot evidence drifted for {output}")
            continue
        jar_name, path = expected.split("!/", 1)
        try:
            with zipfile.ZipFile(mods / jar_name) as archive:
                loot = json.loads(archive.read(path))
        except (OSError, KeyError, ValueError, zipfile.BadZipFile) as error:
            failures.append(f"cannot read self-block loot for {output}: {error}")
            continue
        if loot.get("type") != "minecraft:block":
            failures.append(f"loot table is not block recovery for {output}")
        entries = [
            entry
            for pool in loot.get("pools", [])
            for entry in pool.get("entries", [])
            if isinstance(entry, dict) and entry.get("type") == "minecraft:item"
        ]
        if [entry.get("name") for entry in entries] != [output]:
            failures.append(f"loot table grants something other than self for {output}")
        conditions = [
            condition.get("condition")
            for pool in loot.get("pools", [])
            for condition in pool.get("conditions", [])
            if isinstance(condition, dict)
        ]
        if "minecraft:survives_explosion" not in conditions:
            failures.append(f"self-block loot lost survives_explosion for {output}")
    if len(removals) != 49:
        failures.append(f"installed source removal union must be 49, got {len(removals)}")


def validate_contracts(plan: dict[str, Any], failures: list[str]) -> None:
    contracts = plan.get("replacement_contracts", [])
    if len(contracts) != 27:
        failures.append("replacement contract count must be 27")
        return
    ids = [recipe.get("id") for recipe in contracts]
    outputs = [output_of(recipe)[1] for recipe in contracts]
    if len(set(ids)) != 27:
        failures.append("replacement contract IDs are not unique")
    if len(set(outputs)) != 27:
        failures.append("replacement outputs are not unique")
    if Counter(recipe.get("type") for recipe in contracts) != EXPECTED_TYPE_COUNTS:
        failures.append("recipe type counts changed")
    machines = Counter(
        recipe.get("machine") for recipe in contracts if recipe.get("machine")
    )
    if machines != EXPECTED_MACHINE_COUNTS:
        failures.append(f"Encased press counts changed: {dict(machines)}")

    targets = {entry.get("output"): entry for entry in plan.get("targets", [])}
    removal_union: set[str] = set()
    for recipe in contracts:
        count, output = output_of(recipe)
        expected_count = EXPECTED_OUTPUT_COUNTS.get(output, 1)
        if count != expected_count:
            failures.append(
                f"economical output count changed for {output}: {count} != {expected_count}"
            )
        expected_removals = [
            entry.get("recipe_id")
            for entry in targets.get(output, {}).get("installed_producers", [])
        ]
        if recipe.get("remove") != expected_removals:
            failures.append(f"exact installed removals drifted for {output}")
        removal_union.update(recipe.get("remove", []))
        ingredients = recipe_ingredients(recipe)
        if not any(identity.startswith("tfmg:") for identity in ingredients):
            failures.append(f"contract is no longer TFMG-first: {recipe.get('id')}")
        if any("sulfuric_acid" in identity for identity in ingredients):
            failures.append(f"construction contract consumes sulfuric acid: {recipe.get('id')}")
        if recipe.get("pattern") == GENERIC_RING:
            failures.append(f"generic A/B gate ring returned: {recipe.get('id')}")
        if recipe.get("type") == "mechanical_crafting":
            pattern = recipe.get("pattern", [])
            if len(pattern) != 5 or any(len(row) != 5 for row in pattern):
                failures.append(f"controller is not a deliberate 5x5 chassis: {recipe.get('id')}")
            if ingredients["create:refined_radiance_casing"] < 4:
                failures.append(f"controller lost its Radiant shell: {recipe.get('id')}")

    if len(removal_union) != 49:
        failures.append(f"contract removal union must be 49, got {len(removal_union)}")
    protected = set(
        plan.get("stock_utility_preservation", {}).get(
            "restoration_audit_protected_recipe_ids", []
        )
    )
    if removal_union & protected:
        failures.append("contract removals collide with protected utility recipes")
    for target in plan.get("targets", []):
        for consumer in target.get("preserved_installed_consumers", []):
            if consumer.get("recipe_id") in removal_union:
                failures.append(
                    f"stock casing utility was removed: {consumer.get('recipe_id')}"
                )


def validate_controller_instrumentation(
    plan: dict[str, Any], seed: dict[str, Any], failures: list[str]
) -> None:
    by_id = {recipe["id"]: recipe for recipe in plan.get("replacement_contracts", [])}
    for identity, (computers, monitors) in EXPECTED_CONTROLLER_COUNTS.items():
        recipe = by_id.get(identity)
        if recipe is None:
            failures.append(f"controller contract disappeared: {identity}")
            continue
        ingredients = recipe_ingredients(recipe)
        if ingredients["computercraft:computer_advanced"] != computers:
            failures.append(f"ComputerCraft computer count changed for {identity}")
        if ingredients["computercraft:monitor_advanced"] != monitors:
            failures.append(f"ComputerCraft monitor count changed for {identity}")
        if ingredients["ae2:engineering_processor"] < 1:
            failures.append(f"AE diagnostics disappeared from {identity}")
        if not any(
            ingredient in ingredients
            for ingredient in (
                "mekanism:elite_control_circuit",
                "mekanism:ultimate_control_circuit",
            )
        ):
            failures.append(f"Mekanism control hardware disappeared from {identity}")
        if not any(value.startswith("tfmg:") for value in ingredients):
            failures.append(f"TFMG control hardware disappeared from {identity}")

    seed_by_id = recipes_by_id(seed)
    existing = {
        "industrial_colonies:nuclear/basic_reactor_controller": (2, 4),
        "industrial_colonies:nuclear/reinforced_reactor_controller": (2, 4),
    }
    for identity, (computers, monitors) in existing.items():
        recipe = seed_by_id.get(identity)
        if recipe is None:
            failures.append(f"existing reactor controller recipe disappeared: {identity}")
            continue
        ingredients = recipe_ingredients(recipe)
        if ingredients["computercraft:computer_advanced"] != computers:
            failures.append(f"existing reactor controller computer count drifted: {identity}")
        if ingredients["computercraft:monitor_advanced"] != monitors:
            failures.append(f"existing reactor controller monitor count drifted: {identity}")
        if ingredients["ae2:engineering_processor"] < 1:
            failures.append(f"existing reactor controller lost AE diagnostics: {identity}")
        if not any(
            ingredient in ingredients
            for ingredient in (
                "mekanism:elite_control_circuit",
                "mekanism:ultimate_control_circuit",
            )
        ):
            failures.append(f"existing reactor controller lost digital control: {identity}")


def validate_progression(plan: dict[str, Any], failures: list[str]) -> None:
    by_output = contracts_by_output(plan)
    for output in PRECRITICAL_OUTPUTS:
        recipe = by_output.get(output)
        if recipe is None:
            failures.append(f"precritical output disappeared: {output}")
            continue
        ingredients = recipe_ingredients(recipe)
        forbidden = sorted(
            identity
            for identity in ingredients
            if any(fragment in identity for fragment in FORBIDDEN_PRECRITICAL_FRAGMENTS)
        )
        if forbidden:
            failures.append(f"precritical bootstrap ingredient in {output}: {forbidden}")
    basic_fuel = recipe_ingredients(by_output["bigreactors:basic_reactorfuelrod"])
    if basic_fuel["mekanism:ingot_uranium"] != 4:
        failures.append("basic fuel rods no longer consume four canonical Mekanism uranium ingots")
    if any("yellorium" in identity for identity in basic_fuel):
        failures.append("basic fuel rod regained a Yellorium shortcut")
    for output in FUEL_PROCESSING_OUTPUTS:
        ingredients = recipe_ingredients(by_output[output])
        forbidden = [
            value
            for value in ingredients
            if any(
                fragment in value
                for fragment in ("yellorium", "uranium", "cyanite", "blutonium", "plutonium")
            )
        ]
        if forbidden:
            failures.append(f"Energizer/Fluidizer consumes a fuel product it may enable: {output}")
    for output in ("bigreactors:basic_turbinecasing", "bigreactors:reprocessorcasing"):
        if recipe_ingredients(by_output[output])["bigreactors:cyanite_ingot"] < 1:
            failures.append(f"post-reactor physical Cyanite proof disappeared from {output}")
    for output in (
        "bigreactors:reinforced_reactorcasing",
        "bigreactors:reinforced_turbinecasing",
    ):
        ingredients = recipe_ingredients(by_output[output])
        for required in (
            "mekanism:pellet_plutonium",
            "bigreactors:blutonium_ingot",
            "bigreactors:reprocessorcasing",
        ):
            if ingredients[required] < 1:
                failures.append(f"advanced convergence lost {required}: {output}")

    owner = {output: recipe["id"] for output, recipe in by_output.items()}
    graph: dict[str, set[str]] = {recipe["id"]: set() for recipe in by_output.values()}
    reverse_output = {recipe["id"]: output for output, recipe in by_output.items()}
    for output, recipe in by_output.items():
        for ingredient in recipe_ingredients(recipe):
            if ingredient in owner:
                graph[recipe["id"]].add(owner[ingredient])
        graph[recipe["id"]].update(
            value
            for value in recipe.get("depends_on", [])
            if value in graph
        )
    indegree = {node: len(edges) for node, edges in graph.items()}
    dependents: dict[str, set[str]] = defaultdict(set)
    for node, edges in graph.items():
        for edge in edges:
            dependents[edge].add(node)
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    visited = []
    while queue:
        node = queue.popleft()
        visited.append(node)
        for dependent in sorted(dependents[node]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)
    if len(visited) != len(graph):
        failures.append("replacement contracts contain an internal dependency cycle")

    advanced_anchors = {
        owner[output]
        for output in (
            "bigreactors:reinforced_reactorcasing",
            "bigreactors:reinforced_turbinecasing",
        )
        if output in owner
    }
    for output in ADVANCED_OUTPUTS:
        if output not in owner:
            failures.append(f"advanced output disappeared from dependency graph: {output}")
            continue
        start = owner[output]
        closure: set[str] = set()
        pending = [start]
        while pending:
            node = pending.pop()
            if node in closure:
                continue
            closure.add(node)
            pending.extend(graph[node])
        if not closure & advanced_anchors:
            failures.append(f"advanced output no longer inherits a Plutonium casing gate: {output}")


def validate_environment_and_items(
    plan: dict[str, Any],
    environments: dict[str, Any],
    catalog: Path,
    failures: list[str],
) -> None:
    machines = {
        machine.get("item")
        for family in environments.get("recipe_families", [])
        if family.get("id") == "compacting"
        for machine in family.get("machines", [])
    }
    if not set(EXPECTED_MACHINE_COUNTS) <= machines:
        failures.append("one or more reviewed Encased presses left the compacting environment")
    exact_items = {
        identity
        for recipe in plan.get("replacement_contracts", [])
        for identity in recipe_ingredients(recipe)
        if not identity.startswith("#") and not identity.startswith("minecraft:")
    } | set(EXPECTED_MACHINE_COUNTS)
    connection = sqlite3.connect(catalog)
    try:
        marks = ",".join("?" for _ in exact_items)
        rows = connection.execute(
            f"SELECT item_id FROM items WHERE item_id IN ({marks})",
            tuple(sorted(exact_items)),
        ).fetchall()
    finally:
        connection.close()
    missing = sorted(exact_items - {row[0] for row in rows})
    if missing:
        failures.append(f"reviewed exact ingredients/machines are not installed: {missing}")


def validate_external_rewrites(
    plan: dict[str, Any],
    ftb: dict[str, Any],
    physical: dict[str, Any],
    computercraft_doc: Path,
    failures: list[str],
) -> None:
    contract = plan.get("dependency_rewrite_contract", {})
    ftb_rewrites = contract.get("ftb_guidance_plan_rewrites", [])
    if len(ftb_rewrites) != 4:
        failures.append("FTB guidance rewrite inventory must contain four entries")
    observed_map = {}
    for entry in ftb_rewrites:
        try:
            observed = pointer_get(ftb, entry["json_pointer"])
        except (KeyError, IndexError, TypeError, ValueError) as error:
            failures.append(f"cannot resolve FTB guidance pointer: {error}")
            continue
        if observed not in {entry.get("from"), entry.get("to")}:
            failures.append(f"FTB guidance pointer is neither pre- nor post-migration: {entry}")
        output = entry["json_pointer"].split("/objective_evidence/", 1)[-1].split("/", 1)[0]
        output = output.replace("~1", "/").replace("~0", "~")
        observed_map[output] = entry.get("to")
    if observed_map != EXPECTED_FTB_MAP:
        failures.append(f"four stable FTB mappings changed: {observed_map}")

    physical_rewrites = contract.get("physical_tier_plan_rewrites", [])
    if len(physical_rewrites) != 1:
        failures.append("physical-tier rewrite inventory must contain one entry")
    else:
        entry = physical_rewrites[0]
        try:
            observed = pointer_get(physical, entry["json_pointer"])
        except (KeyError, IndexError, TypeError, ValueError) as error:
            failures.append(f"cannot resolve physical-tier pointer: {error}")
        else:
            if observed not in {entry.get("from"), entry.get("to")}:
                failures.append("physical-tier reprocessor ID is neither pre- nor post-migration")

    docs = contract.get("documentation_rewrites", [])
    if len(docs) != 1:
        failures.append("controller documentation rewrite inventory must contain one entry")
    else:
        entry = docs[0]
        text = computercraft_doc.read_text(encoding="utf-8-sig")
        old_count = text.count(entry.get("from", ""))
        new_count = text.count(entry.get("to", ""))
        if sorted((old_count, new_count)) != [0, entry.get("occurrences")]:
            failures.append("controller documentation is neither exact pre- nor post-migration")


def apply_patch_to_copies(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    staged_seed = copy.deepcopy(seed)
    staged_assignments = copy.deepcopy(assignments)
    seed_recipes = staged_seed.get("recipes")
    if not isinstance(seed_recipes, list):
        raise ValueError("seed recipes must be an array")
    existing = {recipe.get("id") for recipe in seed_recipes if isinstance(recipe, dict)}
    append = audit_builder.build_patch(plan)["seed"]["append_recipes"]
    source_overrides = staged_seed.get("source_recipe_overrides")
    if not isinstance(source_overrides, dict):
        raise ValueError("seed source_recipe_overrides must be an object")
    for output in plan["seed_patch_contract"][
        "remove_source_recipe_override_outputs"
    ]:
        source_overrides.pop(output, None)
    collisions = [recipe["id"] for recipe in append if recipe["id"] in existing]
    if collisions:
        implemented = plan.get("status") == "implemented_in_seed"
        if not implemented:
            raise ValueError(f"review append collides with current seed: {collisions}")
        current = recipes_by_id(staged_seed)
        for recipe in append:
            if current.get(recipe["id"]) != recipe:
                raise ValueError(f"implemented recipe drifted: {recipe['id']}")
    else:
        seed_recipes.extend(copy.deepcopy(append))
    return staged_seed, staged_assignments


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("bigreactors_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load compiler: {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_compilation(
    plan: dict[str, Any],
    seed: dict[str, Any],
    assignments: dict[str, Any],
    catalog: Path,
    mods: Path,
    failures: list[str],
) -> None:
    try:
        staged_seed, staged_assignments = apply_patch_to_copies(plan, seed, assignments)
    except (ValueError, KeyError, TypeError) as error:
        failures.append(f"in-memory patch application failed: {error}")
        return
    if staged_assignments != assignments:
        failures.append("in-memory patch changed assignments")
    with tempfile.TemporaryDirectory(prefix="bigreactors-bulk-audit-") as temporary:
        root = Path(temporary)
        seed_path = root / "seed.json"
        assignments_path = root / "assignments.json"
        manifest_path = root / "managed.json"
        compiled_path = root / "compiled.json"
        seed_path.write_text(json.dumps(staged_seed, indent=2), encoding="utf-8")
        assignments_path.write_text(json.dumps(staged_assignments, indent=2), encoding="utf-8")
        try:
            manifest, report = manifest_builder.build_manifest(
                seed_path,
                assignments_path,
                manifest_builder.DEFAULT_DEPENDENCIES,
                catalog.parent,
                mods,
            )
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
            failures.append(f"managed manifest rejected in-memory Big Reactors batch: {error}")
            return
        if report.get("fatal_errors", []):
            failures.append(f"managed manifest fatal errors: {report['fatal_errors']}")
            return
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        try:
            compiled = load_generator().compile_manifest(manifest_path, compiled_path)
        except (OSError, ValueError, KeyError, TypeError) as error:
            failures.append(f"KJSGen compiler rejected in-memory Big Reactors batch: {error}")
            return

    contract_ids = {recipe["id"] for recipe in plan["replacement_contracts"]}
    automatic_ids = set(plan["automatic_to_source_owned_ids"])
    managed_ids = {recipe.get("id") for recipe in manifest.get("recipes", [])}
    if not contract_ids <= managed_ids:
        failures.append("managed manifest lost one or more source-owned Big Reactors contracts")
    if automatic_ids & managed_ids:
        failures.append("one or more generic automatic Big Reactors owners survived")
    cards = [
        recipe
        for recipe in compiled.get("recipes", [])
        if recipe.get("recipeId") in contract_ids
    ]
    if len(cards) != 27:
        failures.append(f"compiled Big Reactors recipe-card count drifted: {len(cards)}")
        return
    if Counter(recipe.get("type") for recipe in cards) != EXPECTED_COMPILED_TYPE_COUNTS:
        failures.append("compiled Big Reactors card type counts changed")
    machine_counts: Counter[str] = Counter()
    expected_outputs = {
        recipe["id"]: output_of(recipe) for recipe in plan["replacement_contracts"]
    }
    for card in cards:
        identity = card.get("recipeId")
        if card.get("type") == "kjsgen:create_compacting":
            machine = card.get("slots", {}).get("__machine_process_compacting", {}).get("id")
            machine_counts[machine] += 1
        expected_count, expected_output = expected_outputs[identity]
        output = card.get("slots", {}).get("output", {})
        if output.get("id") != expected_output or output.get("count", 1) != expected_count:
            failures.append(f"compiled output drifted for {identity}")
    if machine_counts != EXPECTED_MACHINE_COUNTS:
        failures.append(f"compiled exact-machine counts changed: {dict(machine_counts)}")
    compiled_removals = {
        removal.get("recipeId")
        for removal in compiled.get("removals", [])
        if removal.get("recipeId")
    }
    expected_removals = {
        identity
        for recipe in plan["replacement_contracts"]
        for identity in recipe.get("remove", [])
    }
    missing = sorted(expected_removals - compiled_removals)
    if missing:
        failures.append(f"compiled project is missing exact source removals: {missing}")
    protected = set(
        plan["stock_utility_preservation"]["restoration_audit_protected_recipe_ids"]
    )
    bad = sorted(protected & compiled_removals)
    if bad:
        failures.append(f"compiled project removes preserved stock utilities: {bad}")


def validate_plan(
    plan: dict[str, Any],
    patch: dict[str, Any],
    automatic: dict[str, Any],
    catalog: Path,
    mods: Path,
    seed: dict[str, Any],
    assignments: dict[str, Any],
    ftb: dict[str, Any],
    physical: dict[str, Any],
    restoration: dict[str, Any],
    environments: dict[str, Any],
    nuclear_quest: Path,
    computercraft_doc: Path,
    *,
    deep_artifacts: bool = True,
    compile_batch: bool = True,
) -> list[str]:
    failures: list[str] = []
    validate_metadata(plan, patch, failures)
    if deep_artifacts:
        validate_determinism(
            plan,
            patch,
            catalog,
            mods,
            automatic,
            seed,
            assignments,
            ftb,
            physical,
            restoration,
            failures,
        )
        validate_source_and_loot(plan, mods, failures)
    validate_contracts(plan, failures)
    validate_controller_instrumentation(plan, seed, failures)
    validate_progression(plan, failures)
    validate_environment_and_items(plan, environments, catalog, failures)
    validate_external_rewrites(plan, ftb, physical, computercraft_doc, failures)

    quest_text = nuclear_quest.read_text(encoding="utf-8-sig")
    if re.search(r'(^|\s)"?rewards"?\s*:', quest_text):
        failures.append("nuclear guidance chapter contains item rewards and needs acquisition review")
    if compile_batch:
        validate_compilation(plan, seed, assignments, catalog, mods, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--automatic", type=Path, default=DEFAULT_AUTOMATIC)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--ftb", type=Path, default=DEFAULT_FTB)
    parser.add_argument("--physical", type=Path, default=DEFAULT_PHYSICAL)
    parser.add_argument("--restoration", type=Path, default=DEFAULT_RESTORATION)
    parser.add_argument("--environments", type=Path, default=DEFAULT_ENVIRONMENTS)
    parser.add_argument("--nuclear-quest", type=Path, default=DEFAULT_NUCLEAR_QUEST)
    parser.add_argument("--computercraft-doc", type=Path, default=DEFAULT_COMPUTERCRAFT_DOC)
    parser.add_argument("--no-deep-artifacts", action="store_true")
    parser.add_argument("--no-compile", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        failures = validate_plan(
            load_json(args.plan.resolve()),
            load_json(args.patch.resolve()),
            load_json(args.automatic.resolve()),
            args.catalog.resolve(),
            args.mods.resolve(),
            load_json(args.seed.resolve()),
            load_json(args.assignments.resolve()),
            load_json(args.ftb.resolve()),
            load_json(args.physical.resolve()),
            load_json(args.restoration.resolve()),
            load_json(args.environments.resolve()),
            args.nuclear_quest.resolve(),
            args.computercraft_doc.resolve(),
            deep_artifacts=not args.no_deep_artifacts,
            compile_batch=not args.no_compile,
        )
    except (
        OSError,
        ValueError,
        KeyError,
        IndexError,
        TypeError,
        json.JSONDecodeError,
        sqlite3.Error,
        zipfile.BadZipFile,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if failures:
        print(f"Big Reactors bulk/controller audit failed ({len(failures)} issue(s)):")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "Big Reactors bulk/controller audit passed: 27 source-owned TFMG-first "
        "contracts replace 27 generic automatic owners; 49 installed producers "
        "are removed exactly, casing/fuel/rotor batches preserve economical "
        "yields, five controllers carry ComputerCraft/AE/Mekanism/TFMG control "
        "hardware, Cyanite and Blutonium-Plutonium gates are acyclic, self-block "
        "loot is recovery-only, and stock utility ports/glass/adapters survive."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
