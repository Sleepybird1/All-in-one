#!/usr/bin/env python3
"""Validate the implemented Digital Core and Peripherals source batch."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_digital_core_peripherals_audit as builder
import generate_managed_recipe_overhaul as compiler


PROJECT = builder.PROJECT
DEFAULT_PLAN = builder.DEFAULT_PLAN
DEFAULT_PATCH = builder.DEFAULT_PATCH
DEFAULT_MARKDOWN = builder.DEFAULT_MARKDOWN
DEFAULT_CATALOG = builder.DEFAULT_CATALOG
DEFAULT_MODS = builder.DEFAULT_MODS
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
COUNTED_REF = re.compile(r"^(?:(\d+)x\s+)?(.+)$")

EXPECTED_TYPE_BY_OUTPUT = {
    "ae2:energy_acceptor": "compacting",
    "ae2:item_cell_housing": "compacting",
    "ae2:terminal": "sequenced_assembly",
    "ae2:import_bus": "sequenced_assembly",
    "ae2:interface": "sequenced_assembly",
    "ae2:molecular_assembler": "compacting",
    "appmek:chemical_cell_housing": "compacting",
    "ae2:pattern_provider": "sequenced_assembly",
    "advancedperipherals:peripheral_casing": "sequenced_assembly",
    "advancedperipherals:block_reader": "compacting",
    "advancedperipherals:energy_detector": "compacting",
    "advancedperipherals:inventory_manager": "compacting",
    "advancedperipherals:colony_integrator": "compacting",
    "advancedperipherals:me_bridge": "compacting",
}

COPPER_OUTPUTS = {
    "ae2:energy_acceptor",
    "ae2:item_cell_housing",
    "ae2:import_bus",
    "appmek:chemical_cell_housing",
}
BRASS_OUTPUTS = set(builder.BATCH_OUTPUTS) - COPPER_OUTPUTS


def load_json(path: Path) -> dict[str, Any]:
    return builder.load_json(path)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def contract_by_output(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        builder.output_id(recipe): recipe
        for recipe in plan.get("replacement_contracts", [])
        if isinstance(recipe, dict)
    }


def normalized_ref(value: str) -> str:
    match = COUNTED_REF.fullmatch(value)
    return match.group(2) if match else value


def catalog_ids(catalog: Path) -> tuple[set[str], set[str]]:
    items = {row["item_id"] for row in load_rows(catalog / "items.csv")}
    tags: set[str] = set()
    for row in load_rows(catalog / "recipe_refs.csv"):
        identity = row.get("resource_id", "")
        if not RESOURCE_ID.fullmatch(identity):
            continue
        if row.get("kind") == "item":
            items.add(identity)
        elif row.get("kind") == "tag":
            tags.add(f"#{identity}")
    return items, tags


def validate_source_evidence(
    plan: dict[str, Any], catalog: Path, mods: Path, failures: list[str]
) -> tuple[set[str], set[str]]:
    rows = load_rows(catalog / "recipes.csv")
    rows_by_id = {row["recipe_id"]: row for row in rows}
    expected_removed = [
        identity
        for output in builder.BATCH_OUTPUTS
        for identity in builder.SOURCE_REMOVALS[output]
    ]
    sources = plan.get("removed_installed_recipes", [])
    actual_removed = [source.get("id") for source in sources if isinstance(source, dict)]
    if actual_removed != expected_removed:
        failures.append("exact 17 installed removal IDs drifted")

    removed_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            failures.append("installed removal evidence contains a non-object")
            continue
        identity = str(source.get("id", ""))
        if identity in removed_ids:
            failures.append(f"duplicate installed removal evidence: {identity}")
        removed_ids.add(identity)
        row = rows_by_id.get(identity)
        if row is None:
            failures.append(f"installed removal recipe is absent from catalog: {identity}")
            continue
        for field, key in (
            ("recipe_type", "recipe_type"),
            ("source_jar", "source_jar"),
            ("source_path", "source_path"),
        ):
            if source.get(field) != row.get(key):
                failures.append(f"{identity}: installed source {field} drifted")
        jar = mods / row["source_jar"]
        try:
            with zipfile.ZipFile(jar) as archive:
                raw = archive.read(row["source_path"])
        except (FileNotFoundError, KeyError, zipfile.BadZipFile) as error:
            failures.append(f"{identity}: cannot read installed source: {error}")
            continue
        if source.get("source_sha256") != digest_bytes(raw):
            failures.append(f"{identity}: installed source JSON hash changed")
        document = json.loads(raw)
        if document.get("type") != source.get("raw_type"):
            failures.append(f"{identity}: installed raw recipe type changed")
        if source.get("catalog_outputs") != sorted(builder.split_refs(row["outputs"])):
            failures.append(f"{identity}: catalog output evidence drifted")
        if source.get("catalog_inputs") != sorted(builder.split_refs(row["inputs"])):
            failures.append(f"{identity}: catalog input evidence drifted")

    housing_outputs = {"ae2:item_cell_housing", "appmek:chemical_cell_housing"}
    expected_preserved: dict[str, str] = {}
    for row in rows:
        outputs = builder.split_refs(row["outputs"])
        inputs = builder.split_refs(row["inputs"])
        if row["recipe_type"] == "ae2:storage_cell_disassembly" and outputs.intersection(
            housing_outputs
        ):
            expected_preserved[row["recipe_id"]] = "housing_recovery"
        elif inputs.intersection(housing_outputs) and row["recipe_type"] != "ae2:storage_cell_disassembly":
            expected_preserved[row["recipe_id"]] = "cell_closure"

    preserved = plan.get("preserved_cell_recipes", [])
    actual_preserved = {
        str(source.get("id", "")): str(source.get("preservation_role", ""))
        for source in preserved
        if isinstance(source, dict)
    }
    if actual_preserved != expected_preserved:
        failures.append("exact stock cell closure/recovery preservation set drifted")
    if removed_ids.intersection(actual_preserved):
        failures.append("preserved stock cell recipe leaked into exact removals")

    for source in preserved:
        if not isinstance(source, dict):
            failures.append("preserved cell evidence contains a non-object")
            continue
        identity = str(source.get("id", ""))
        row = rows_by_id.get(identity)
        if row is None:
            failures.append(f"preserved stock recipe is absent from catalog: {identity}")
            continue
        role = source.get("preservation_role")
        inputs = builder.split_refs(row["inputs"])
        outputs = builder.split_refs(row["outputs"])
        if role == "cell_closure" and not inputs.intersection(housing_outputs):
            failures.append(f"{identity}: cell closure no longer consumes a housing")
        if role == "housing_recovery" and not outputs.intersection(housing_outputs):
            failures.append(f"{identity}: disassembly no longer recovers a housing")
        jar = mods / row["source_jar"]
        try:
            with zipfile.ZipFile(jar) as archive:
                raw = archive.read(row["source_path"])
        except (FileNotFoundError, KeyError, zipfile.BadZipFile) as error:
            failures.append(f"{identity}: cannot read preserved source: {error}")
            continue
        if source.get("source_sha256") != digest_bytes(raw):
            failures.append(f"{identity}: preserved source JSON hash changed")
    return removed_ids, set(actual_preserved)


def validate_contracts(
    plan: dict[str, Any], catalog: Path, failures: list[str]
) -> dict[str, dict[str, Any]]:
    contracts = plan.get("replacement_contracts", [])
    if not isinstance(contracts, list) or len(contracts) != 14:
        failures.append("batch must contain exactly 14 replacement contracts")
        contracts = contracts if isinstance(contracts, list) else []
    by_output = contract_by_output(plan)
    if set(by_output) != set(builder.BATCH_OUTPUTS) or len(by_output) != len(contracts):
        failures.append("replacement contracts must own each exact batch output once")

    item_ids, tag_ids = catalog_ids(catalog)
    seen_ids: set[str] = set()
    for output, recipe in by_output.items():
        identity = str(recipe.get("id", ""))
        if identity in seen_ids or not RESOURCE_ID.fullmatch(identity):
            failures.append(f"blank, invalid, or duplicate managed recipe ID: {identity!r}")
        seen_ids.add(identity)
        if recipe.get("node") != builder.ASSIGNMENT_BY_OUTPUT.get(output):
            failures.append(f"{output}: node assignment drifted")
        if recipe.get("phase") != builder.PHASE_BY_OUTPUT.get(output):
            failures.append(f"{output}: phase assignment drifted")
        if recipe.get("type") != EXPECTED_TYPE_BY_OUTPUT.get(output):
            failures.append(f"{output}: manufacturing process type drifted")
        if recipe.get("remove") != list(builder.SOURCE_REMOVALS.get(output, ())):
            failures.append(f"{output}: exact source removal list drifted")
        if output in {"ae2:item_cell_housing", "appmek:chemical_cell_housing"}:
            if recipe.get("exclusive_output") is not False:
                failures.append(f"{output}: reusable housing must retain stock recovery outputs")
        elif recipe.get("exclusive_output") is not True:
            failures.append(f"{output}: direct manufactured output lost exclusive ownership")
        if "pattern" in recipe or "key" in recipe or recipe.get("type") == "mechanical_crafting":
            failures.append(f"{output}: generic shaped/gate-ring manufacturing is forbidden")

        refs = builder.recipe_inputs(recipe)
        if not any(normalized_ref(value).startswith("tfmg:") for value in refs):
            failures.append(f"{output}: recipe is not TFMG-first")
        for value in refs:
            match = COUNTED_REF.fullmatch(value)
            if not match:
                failures.append(f"{output}: invalid ingredient reference {value!r}")
                continue
            count, normalized = match.groups()
            if count and normalized.startswith("#"):
                failures.append(f"{output}: counted tag syntax is forbidden")
            if normalized.startswith("#"):
                if normalized not in tag_ids:
                    failures.append(f"{output}: unknown catalog ingredient tag {normalized}")
            elif normalized not in item_ids:
                failures.append(f"{output}: unknown catalog ingredient item {normalized}")

        family = "copper" if output in COPPER_OUTPUTS else "brass"
        if recipe.get("type") == "compacting":
            expected_machine = f"createcasing:{family}_press"
            if recipe.get("machine") != expected_machine:
                failures.append(f"{output}: unapproved {family} manufacturing environment")
            if not 4 <= len(recipe.get("inputs", [])) <= 8:
                failures.append(f"{output}: compacting must use 4-8 physical inputs")
            try:
                card = compiler.process(recipe, compiler.stable_uid("recipe", identity))
            except (KeyError, TypeError, ValueError) as error:
                failures.append(f"{output}: KJSGen compacting compilation failed: {error}")
            else:
                if card.get("type") != "kjsgen:create_compacting":
                    failures.append(f"{output}: compiled card type drifted")
        elif recipe.get("type") == "sequenced_assembly":
            if recipe.get("loops") != 1:
                failures.append(f"{output}: sequenced assembly must use exactly one loop")
            steps = recipe.get("steps", [])
            if not isinstance(steps, list) or not 4 <= len(steps) <= 5:
                failures.append(f"{output}: sequenced assembly must use 4-5 operations")
                steps = steps if isinstance(steps, list) else []
            for step in steps:
                if step.get("op") == "deploying":
                    expected_machine = f"createcasing:{family}_deployer"
                elif step.get("op") == "pressing":
                    expected_machine = f"createcasing:{family}_press"
                else:
                    failures.append(f"{output}: unsupported or meaningless sequence operation")
                    continue
                if step.get("machine") != expected_machine:
                    failures.append(f"{output}: unapproved {family} sequence environment")
            if not steps or steps[-1].get("op") != "pressing":
                failures.append(f"{output}: sequence must finish with casing-specific pressing")
            try:
                card = compiler.sequenced(recipe, compiler.stable_uid("recipe", identity))
            except (KeyError, TypeError, ValueError) as error:
                failures.append(f"{output}: KJSGen sequence compilation failed: {error}")
            else:
                if card.get("type") != "kjsgen:create_sequenced_assembly":
                    failures.append(f"{output}: compiled card type drifted")

    for output in builder.FIRST_ME_OUTPUTS:
        recipe = by_output.get(output, {})
        refs = set(builder.recipe_inputs(recipe)) if recipe else set()
        forbidden = refs.intersection(builder.FORBIDDEN_FIRST_ME_INPUTS)
        if forbidden:
            failures.append(f"{output}: first ME network consumes forbidden Mekanism gate {sorted(forbidden)}")
        if refs.intersection({"ae2:calculation_processor", "ae2:engineering_processor"}):
            failures.append(f"{output}: first ME network consumes a later processor tier")

    casing_id = "industrial_colonies:digital_core/peripheral_casing"
    casing = by_output.get("advancedperipherals:peripheral_casing", {})
    for output in (
        value
        for value in builder.BATCH_OUTPUTS
        if value.startswith("advancedperipherals:")
        and value != "advancedperipherals:peripheral_casing"
    ):
        recipe = by_output.get(output, {})
        if "advancedperipherals:peripheral_casing" not in builder.recipe_inputs(recipe):
            failures.append(f"{output}: peripheral casing is not a physical prerequisite")
        if casing_id not in recipe.get("depends_on", []):
            failures.append(f"{output}: peripheral casing dependency is not explicit")
        if recipe.get("phase") == casing.get("phase") and recipe.get("order", 0) <= casing.get("order", 0):
            failures.append(f"{output}: peripheral casing does not precede device order")

    interface_id = "industrial_colonies:digital_core/interface"
    for output in ("ae2:pattern_provider", "advancedperipherals:me_bridge"):
        recipe = by_output.get(output, {})
        if "ae2:interface" not in builder.recipe_inputs(recipe):
            failures.append(f"{output}: AE2 interface is not a physical prerequisite")
        if interface_id not in recipe.get("depends_on", []):
            failures.append(f"{output}: AE2 interface dependency is not explicit")

    ids = {recipe.get("id"): recipe for recipe in contracts if isinstance(recipe, dict)}
    graph: dict[str, set[str]] = {str(identity): set() for identity in ids}
    for identity, recipe in ids.items():
        for dependency in recipe.get("depends_on", []):
            if dependency.startswith("industrial_colonies:digital_core/"):
                if dependency not in ids:
                    failures.append(f"{identity}: unknown same-batch dependency {dependency}")
                else:
                    graph[str(identity)].add(dependency)
                    dependency_output = builder.output_id(ids[dependency])
                    if dependency_output not in builder.recipe_inputs(recipe):
                        failures.append(f"{identity}: dependency is not a physical input")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> None:
        if identity in visiting:
            failures.append(f"same-batch dependency cycle reaches {identity}")
            return
        if identity in visited:
            return
        visiting.add(identity)
        for dependency in graph.get(identity, set()):
            visit(dependency)
        visiting.remove(identity)
        visited.add(identity)

    for identity in graph:
        visit(identity)
    return by_output


def validate_prerequisites(plan: dict[str, Any], seed: dict[str, Any], failures: list[str]) -> None:
    evidence = plan.get("prerequisite_evidence", [])
    by_output = {entry.get("output"): entry for entry in evidence if isinstance(entry, dict)}
    if set(by_output) != set(builder.PREREQUISITE_OUTPUTS):
        failures.append("exact five prerequisite capabilities drifted")
    seed_by_output = {
        builder.output_id(recipe): recipe
        for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict)
    }
    for output in builder.PREREQUISITE_OUTPUTS[:-1]:
        owner = seed_by_output.get(output)
        if owner is None:
            failures.append(f"prerequisite has no authoritative seed owner: {output}")
            continue
        if by_output.get(output, {}).get("managed_owner") != owner.get("id"):
            failures.append(f"{output}: prerequisite owner evidence drifted")
        if by_output.get(output, {}).get("phase") != owner.get("phase"):
            failures.append(f"{output}: prerequisite phase evidence drifted")
    modem = by_output.get("computercraft:wired_modem_full", {})
    wired_owner = seed_by_output.get("computercraft:wired_modem")
    if modem.get("recipe_id") != "computercraft:wired_modem_full_from":
        failures.append("wired modem full closure recipe evidence drifted")
    if modem.get("inputs") != ["computercraft:wired_modem"]:
        failures.append("wired modem full closure no longer uses the managed modem")
    if modem.get("managed_component_owner") != (wired_owner or {}).get("id"):
        failures.append("wired modem component owner evidence drifted")


def validate_tfmg_power_dependencies(
    plan: dict[str, Any], seed: dict[str, Any], failures: list[str]
) -> None:
    seed_by_output = {
        builder.output_id(recipe): recipe
        for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict)
    }
    expected = {
        "tfmg:transformer": (
            "industrial_colonies:tfmg_heavy_electrical/transformer",
            "ae2:energy_acceptor",
        ),
        "tfmg:voltage_observer": (
            "industrial_colonies:tfmg_heavy_electrical/voltage_observer",
            "advancedperipherals:energy_detector",
        ),
    }
    contracts = contract_by_output(plan)
    phase_order = seed.get("phase_order", [])
    if not isinstance(phase_order, list):
        failures.append("seed phase order is not an array")
        return
    rank = {phase: index for index, phase in enumerate(phase_order)}
    for dependency, (owner_id, consumer_output) in expected.items():
        owner = seed_by_output.get(dependency)
        consumer = contracts.get(consumer_output, {})
        if owner is None or owner.get("id") != owner_id:
            failures.append(f"{dependency}: required Heavy/Electrical source owner drifted")
            continue
        if dependency not in builder.recipe_inputs(consumer):
            failures.append(f"{consumer_output}: required TFMG power dependency is not physical")
        owner_phase = owner.get("phase")
        consumer_phase = consumer.get("phase")
        if owner_phase not in rank or consumer_phase not in rank or rank[owner_phase] > rank[consumer_phase]:
            failures.append(f"{dependency}: owner phase does not precede its Digital Core consumer")


def validate_assignments(
    plan: dict[str, Any], assignments: dict[str, Any], failures: list[str]
) -> None:
    expected = [
        {
            "output": output,
            "required_node": builder.ASSIGNMENT_BY_OUTPUT[output],
            "current_nodes": [builder.ASSIGNMENT_BY_OUTPUT[output]],
            "patch_action": "none",
        }
        for output in builder.BATCH_OUTPUTS
    ]
    if plan.get("assignment_contract") != expected:
        failures.append("exact no-edit assignment contract drifted")
    for output in builder.BATCH_OUTPUTS:
        nodes = builder.find_assignment_nodes(assignments, output)
        if nodes != [builder.ASSIGNMENT_BY_OUTPUT[output]]:
            failures.append(f"{output}: current assignment is not exact and unique: {nodes}")


def validate_managed_state(
    plan: dict[str, Any],
    seed: dict[str, Any],
    managed: dict[str, Any],
    failures: list[str],
    *,
    implemented_manifest: bool,
) -> None:
    contracts = contract_by_output(plan)
    seed_recipes = [recipe for recipe in seed.get("recipes", []) if isinstance(recipe, dict)]
    seed_by_id = {recipe.get("id"): recipe for recipe in seed_recipes}
    for output, contract in contracts.items():
        identity = contract.get("id")
        if seed_by_id.get(identity) != contract:
            failures.append(f"{output}: authoritative seed recipe differs from reviewed contract")
        owners = [
            recipe.get("id") for recipe in seed_recipes if builder.output_id(recipe) == output
        ]
        if owners != [identity]:
            failures.append(f"{output}: authoritative seed owner set is not exact: {owners}")

    preserved_ids = {
        source.get("id")
        for source in plan.get("preserved_cell_recipes", [])
        if isinstance(source, dict)
    }
    seed_preserved = seed.get("preserve_recipe_ids", [])
    if not isinstance(seed_preserved, list) or not preserved_ids.issubset(seed_preserved):
        missing = sorted(preserved_ids - set(seed_preserved if isinstance(seed_preserved, list) else []))
        failures.append(f"authoritative seed is missing stock cell preservation IDs: {missing}")

    current_by_output = {
        builder.output_id(recipe): recipe
        for recipe in managed.get("recipes", [])
        if isinstance(recipe, dict) and builder.output_id(recipe) in builder.BATCH_OUTPUTS
    }
    if implemented_manifest:
        managed_ids = {
            recipe.get("id")
            for recipe in managed.get("recipes", [])
            if isinstance(recipe, dict)
        }
        leaked_auto = sorted(set(builder.AUTO_OWNERS.values()).intersection(managed_ids))
        if leaked_auto:
            failures.append(f"isolated rebuild retained automatic owners: {leaked_auto}")
        for output, contract in contracts.items():
            recipe = current_by_output.get(output)
            if recipe is None or recipe.get("id") != contract.get("id"):
                failures.append(f"{output}: isolated rebuild lacks the exact source-owned recipe")
                continue
            if recipe.get("remove") != contract.get("remove"):
                failures.append(f"{output}: isolated rebuild removal contract drifted")
        expected_removals = {
            identity
            for output in builder.BATCH_OUTPUTS
            for identity in builder.SOURCE_REMOVALS[output]
        }
        compiled_removals = {
            identity
            for recipe in current_by_output.values()
            for identity in recipe.get("remove", [])
        }
        if compiled_removals != expected_removals:
            failures.append("isolated rebuild does not compile the exact 17 removals")
        managed_preserved = managed.get("preserve_recipe_ids", [])
        if not isinstance(managed_preserved, list) or not preserved_ids.issubset(managed_preserved):
            failures.append("isolated rebuild lost one or more stock cell preservation IDs")
        return

    # The checked-in managed snapshot is deliberately the pre-integration evidence.
    expected_state = plan.get("current_managed_state", {}).get("replaced_automatic_owners", [])
    state_by_output = {
        entry.get("output"): entry for entry in expected_state if isinstance(entry, dict)
    }
    if set(state_by_output) != set(builder.BATCH_OUTPUTS):
        failures.append("current automatic owner evidence does not cover 14 outputs")
    for output in builder.BATCH_OUTPUTS:
        recipe = current_by_output.get(output)
        entry = state_by_output.get(output, {})
        if recipe is None:
            failures.append(f"current automatic managed owner is absent: {output}")
            continue
        if recipe.get("id") != builder.AUTO_OWNERS[output] or entry.get("id") != recipe.get("id"):
            failures.append(f"{output}: current automatic owner identity drifted")
        if recipe.get("type") != "mechanical_crafting" or entry.get("type") != recipe.get("type"):
            failures.append(f"{output}: retired automatic owner is no longer the generic mechanical card")
        if entry.get("remove") != recipe.get("remove") or entry.get("depends_on") != recipe.get("depends_on"):
            failures.append(f"{output}: current automatic owner evidence drifted")
        pattern = recipe.get("pattern", [])
        if not isinstance(pattern, list) or "ABABA" not in pattern:
            failures.append(f"{output}: expected generic A/B gate-ring evidence changed")
    retired = plan.get("current_managed_state", {}).get("expected_retired_ids_after_rebuild")
    if retired != [builder.AUTO_OWNERS[output] for output in builder.BATCH_OUTPUTS]:
        failures.append("expected automatic retirement list drifted")


def validate_patch(
    plan: dict[str, Any], patch: dict[str, Any], preserved: set[str], failures: list[str]
) -> None:
    if patch.get("status") != "applied_to_authoritative_seed":
        failures.append("patch status must be applied_to_authoritative_seed")
    if patch.get("batch_id") != "digital_core_and_peripherals":
        failures.append("patch batch identity drifted")
    expected_bases = plan.get("implementation", {}).get("rebased_base_files")
    if patch.get("base_files") != expected_bases:
        failures.append("patch shared-file base hashes drifted")
    operations = patch.get("seed_operations", [])
    if not isinstance(operations, list) or len(operations) != 2:
        failures.append("patch must contain exactly append and preserve-union operations")
        operations = operations if isinstance(operations, list) else []
    append = next((op for op in operations if op.get("op") == "append_recipe_specs_after_output_ownership_assertion"), None)
    preserve = next((op for op in operations if op.get("op") == "union_preserve_recipe_ids"), None)
    if append is None or append.get("recipes") != plan.get("replacement_contracts"):
        failures.append("patch recipe payload differs from reviewed contracts")
    if preserve is None or preserve.get("recipe_ids") != sorted(preserved):
        failures.append("patch exact stock preservation union drifted")
    if patch.get("assignment_operations") != []:
        failures.append("assignment patch must remain empty")
    if patch.get("assignment_assertions") != plan.get("assignment_contract"):
        failures.append("assignment assertions differ from reviewed contract")
    effects = patch.get("expected_rebuild_effects", {})
    if effects.get("retire_automatic_managed_ids") != [
        builder.AUTO_OWNERS[output] for output in builder.BATCH_OUTPUTS
    ]:
        failures.append("patch automatic retirement effect drifted")
    if effects.get("compile_exact_managed_ids") != [
        recipe["id"] for recipe in plan.get("replacement_contracts", [])
    ]:
        failures.append("patch compiled managed ID list drifted")


def validate_plan(
    plan: dict[str, Any],
    patch: dict[str, Any],
    catalog: Path,
    mods: Path,
    seed: dict[str, Any],
    assignments: dict[str, Any],
    current: dict[str, Any],
    *,
    implemented_manifest: bool = False,
    check_determinism: bool = False,
    markdown_text: str | None = None,
) -> list[str]:
    failures: list[str] = []
    if plan.get("status") != "implemented_in_seed":
        failures.append("plan status must be implemented_in_seed")
    if plan.get("batch_id") != "digital_core_and_peripherals" or plan.get("priority") != 2:
        failures.append("priority batch identity drifted")
    decision = plan.get("decision", {})
    if decision.get("replace_exactly_14_outputs") != list(builder.BATCH_OUTPUTS):
        failures.append("exact batch output order drifted")
    if decision.get("forbid_generic_gate_rings") is not True:
        failures.append("generic gate-ring prohibition was removed")
    if decision.get("shared_files_modified") is not True:
        failures.append("implemented shared-file state was lost")
    implementation = plan.get("implementation", {})
    expected_implementation = {
        "status": "source_owned",
        "authoritative_source": "progression/managed_recipe_overhaul.seed.json",
        "source_recipe_count": 14,
        "source_recipe_ids": [recipe["id"] for recipe in plan.get("replacement_contracts", [])],
        "preserved_stock_recipe_count": 44,
        "exact_stock_recipe_removals": 17,
        "automatic_owners_retired_on_rebuild": 14,
        "assignment_changes": 0,
        "authoritative_generated_artifacts": "intentionally_not_regenerated_by_batch_owner",
        "rebased_base_files": builder.REBASED_BASE_FILES,
    }
    if implementation != expected_implementation:
        failures.append("implementation metadata drifted")
    boundary = plan.get("integration_boundary", {})
    if any(
        boundary.get(key) is not False
        for key in (
            "generated_output_edit_authorized",
            "quest_edit_authorized",
            "deploy_or_live_edit_authorized",
            "drawio_edit_authorized",
        )
    ):
        failures.append("integration boundary improperly authorizes a shared mutation")
    if boundary.get("seed_edit_applied") is not True:
        failures.append("integration boundary lost the applied seed edit")
    if boundary.get("assignment_edit_required") is not False:
        failures.append("assignment edit must remain unnecessary")

    scope = plan.get("scope", {})
    for label, path, key in (
        ("catalog", catalog / "recipes.csv", "catalog_recipes_sha256"),
        ("assignments", builder.ASSIGNMENTS, "assignments_sha256"),
        ("current managed", builder.CURRENT_MANAGED, "current_managed_sha256"),
    ):
        if scope.get(key) != digest_path(path):
            failures.append(f"{label} base hash changed")
    if scope.get("seed_sha256") != builder.DIGITAL_CORE_IMPLEMENTATION_SEED_SHA256:
        failures.append("Digital Core implementation seed checkpoint changed")
    jar_hashes = scope.get("installed_jar_sha256", {})
    for name, expected in jar_hashes.items() if isinstance(jar_hashes, dict) else []:
        jar = mods / name
        if not jar.is_file() or digest_path(jar) != expected:
            failures.append(f"installed JAR hash changed: {name}")

    _, preserved = validate_source_evidence(plan, catalog, mods, failures)
    validate_contracts(plan, catalog, failures)
    validate_prerequisites(plan, seed, failures)
    validate_tfmg_power_dependencies(plan, seed, failures)
    validate_assignments(plan, assignments, failures)
    validate_managed_state(
        plan,
        seed,
        current,
        failures,
        implemented_manifest=implemented_manifest,
    )
    validate_patch(plan, patch, preserved, failures)

    if check_determinism:
        expected_plan, expected_patch, expected_markdown = builder.build_documents(catalog, mods)
        if plan != expected_plan:
            failures.append("plan differs from deterministic builder output")
        if patch != expected_patch:
            failures.append("patch differs from deterministic builder output")
        if markdown_text is not None and markdown_text != expected_markdown:
            failures.append("Markdown differs from deterministic builder output")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument(
        "--managed",
        type=Path,
        help="Optional isolated rebuilt manifest; proves automatic-owner retirement and compiled removals.",
    )
    args = parser.parse_args()
    plan = load_json(args.plan)
    patch = load_json(args.patch)
    failures = validate_plan(
        plan,
        patch,
        args.catalog,
        args.mods,
        load_json(builder.SEED),
        load_json(builder.ASSIGNMENTS),
        load_json(args.managed) if args.managed else load_json(builder.CURRENT_MANAGED),
        implemented_manifest=args.managed is not None,
        check_determinism=True,
        markdown_text=args.markdown.read_text(encoding="utf-8"),
    )
    if failures:
        print("Digital Core and Peripherals audit FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Digital Core and Peripherals audit passed.")
    print("- 14 exact TFMG-first replacement contracts")
    print("- 17 exact installed recipe removals")
    print("- 44 stock cell closure/recovery recipes preserved")
    print("- Copper/Brass routing, dependency order, assignments, and patch parity verified")
    if args.managed:
        print("- isolated rebuild retires all 14 automatic owners and compiles all 17 removals")
    else:
        print("- deterministic regeneration and pre-integration automatic-owner evidence verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
