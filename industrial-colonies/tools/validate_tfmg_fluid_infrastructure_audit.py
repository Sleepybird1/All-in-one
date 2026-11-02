#!/usr/bin/env python3
"""Validate the implemented TFMG fluid-infrastructure manufacturing batch.

This proves installed TFMG evidence, exact seed/manifest ownership, additive
assignment parity, casing-philosophy routing, phase reachability, the retained
stock boundary, and the acyclic twelve-card KJSGen implementation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import zipfile
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "TFMG_FLUID_INFRASTRUCTURE_AUDIT.plan.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
MANAGED = PROJECT / "progression/managed_recipe_overhaul.json"
ENVIRONMENTS = PROJECT / "src/main/resources/data/industrial_colonies/tier_recipe_environments.json"
PROJECT_PIPE_TAG = PROJECT / "src/main/resources/data/tfmg/tags/block/industrial_pipe.json"
PACK_SCRIPTS = PROJECT / "pack-scripts"
GENERATOR = PROJECT / "tools/generate_managed_recipe_overhaul.py"

RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^#[a-z0-9_.-]+:[a-z0-9_./-]+$")
COUNTED_REF = re.compile(r"^(?:(\d+)x\s+)?(.+)$")

EXPECTED_MACHINE_BY_ID = {
    "industrial_colonies:fluid_infrastructure/cast_iron_pipe": "create:mechanical_press",
    "industrial_colonies:fluid_infrastructure/cast_iron_fluid_tank": "create:mechanical_press",
    "industrial_colonies:fluid_infrastructure/cast_iron_mechanical_pump": "create:mechanical_press",
    "industrial_colonies:fluid_infrastructure/cast_iron_chemical_vat": "createcasing:brass_press",
    "industrial_colonies:fluid_infrastructure/steel_pipe": "createcasing:brass_press",
    "industrial_colonies:fluid_infrastructure/steel_fluid_tank": "createcasing:brass_press",
    "industrial_colonies:fluid_infrastructure/steel_mechanical_pump": "createcasing:brass_press",
    "industrial_colonies:fluid_infrastructure/steel_chemical_vat": "createcasing:brass_press",
    "industrial_colonies:fluid_infrastructure/industrial_pipe": "createcasing:brass_press",
    "industrial_colonies:fluid_infrastructure/fireproof_chemical_vat": "createcasing:brass_press",
    "industrial_colonies:fluid_infrastructure/aluminum_pipe": "createcasing:brass_press",
    "industrial_colonies:fluid_infrastructure/electric_pump": "createcasing:copper_press",
}
EXTERNAL_OUTPUT_OWNERS = {
    "tfmg:fireproof_bricks": "industrial_colonies:steelworks/fireproof_bricks",
    "tfmg:circuit_board": "industrial_colonies:electronics/circuit_board",
}
REPLACED_AUTO_EVIDENCE = [
    {"output": "tfmg:cast_iron_pipe", "managed_id": "industrial_colonies:auto/tfmg/cast_iron_pipe", "type": "mechanical_crafting", "output_count": 4, "remove_exact": ["tfmg:crafting/materials/cast_iron_pipe", "tfmg:crafting/materials/cast_iron_pipe_vertical"]},
    {"output": "tfmg:cast_iron_fluid_tank", "managed_id": "industrial_colonies:auto/tfmg/cast_iron_fluid_tank", "type": "mechanical_crafting", "output_count": 1, "remove_exact": ["tfmg:crafting/materials/cast_iron_fluid_tank"]},
    {"output": "tfmg:cast_iron_mechanical_pump", "managed_id": "industrial_colonies:auto/tfmg/cast_iron_mechanical_pump", "type": "mechanical_crafting", "output_count": 1, "remove_exact": ["tfmg:crafting/materials/cast_iron_mechanical_pump"]},
    {"output": "tfmg:cast_iron_chemical_vat", "managed_id": "industrial_colonies:auto/tfmg/cast_iron_chemical_vat", "type": "mechanical_crafting", "output_count": 1, "remove_exact": ["tfmg:crafting/materials/cast_iron_chemical_vat"]},
    {"output": "tfmg:steel_chemical_vat", "managed_id": "industrial_colonies:auto/tfmg/steel_chemical_vat", "type": "mechanical_crafting", "output_count": 2, "remove_exact": ["tfmg:crafting/materials/steel_chemical_vat"]},
]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def split_ref(value: str) -> tuple[int, str]:
    match = COUNTED_REF.fullmatch(value.strip())
    if match is None:
        raise ValueError(f"invalid counted reference: {value!r}")
    return int(match.group(1) or 1), match.group(2)


def recipe_outputs(row: dict[str, str]) -> set[str]:
    return {part.strip() for part in row.get("outputs", "").split("|") if part.strip()}


def catalog_item_ids(catalog: Path) -> set[str]:
    """Include vanilla inputs evidenced by mod recipes but absent from items.csv."""
    items = {row["item_id"] for row in load_rows(catalog / "items.csv")}
    for row in load_rows(catalog / "recipe_refs.csv"):
        if row.get("kind") == "item" and RESOURCE_ID.fullmatch(row.get("resource_id", "")):
            items.add(row["resource_id"])
    return items


def catalog_tag_ids(catalog: Path) -> set[str]:
    return {
        f"#{row['resource_id']}"
        for row in load_rows(catalog / "recipe_refs.csv")
        if row.get("kind") == "tag" and RESOURCE_ID.fullmatch(row.get("resource_id", ""))
    }


def raw_recipe_result(document: dict[str, Any]) -> tuple[str, int]:
    result = document.get("result")
    if not isinstance(result, dict) or not isinstance(result.get("id"), str):
        raise ValueError("audited recipe does not have one object result")
    count = result.get("count", 1)
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise ValueError("audited recipe has an invalid result count")
    return result["id"], count


def managed_output(recipe: dict[str, Any]) -> tuple[str, int]:
    output = recipe.get("output")
    if isinstance(output, str):
        return split_ref(output)[1], split_ref(output)[0]
    if isinstance(output, dict) and isinstance(output.get("id"), str):
        count = output.get("count", 1)
        return output["id"], count if isinstance(count, int) and not isinstance(count, bool) else 1
    raise ValueError(f"{recipe.get('id')}: unsupported managed output")


def recipes_by_id(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(recipe["id"]): recipe
        for recipe in document.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def seed_spec(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": contract["id"],
        "node": contract["node"],
        "phase": contract["phase"],
        "order": contract["batch_order"],
        "type": contract["type"],
        "comment": contract["comment"],
        "machine": contract["machine"],
        "inputs": contract["inputs"],
        "output": contract["output"],
        "remove": contract["remove_exact"],
        "exclusive_output": contract["exclusive_output"],
        "depends_on": contract.get("depends_on_batch", []),
    }


def collect_environment_items(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        item = value.get("item")
        if isinstance(item, str):
            found.add(item)
        for child in value.values():
            found.update(collect_environment_items(child))
    elif isinstance(value, list):
        for child in value:
            found.update(collect_environment_items(child))
    return found


def collect_strings(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str):
        found.add(value)
    elif isinstance(value, dict):
        for child in value.values():
            found.update(collect_strings(child))
    elif isinstance(value, list):
        for child in value:
            found.update(collect_strings(child))
    return found


def find_tfmg_jar(mods: Path) -> Path:
    matches = sorted(mods.glob("tfmg-*.jar"))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one TFMG JAR in {mods}, found {len(matches)}")
    return matches[0]


def validate_installed_evidence(
    plan: dict[str, Any], catalog: Path, mods: Path, failures: list[str]
) -> tuple[set[str], set[str], set[str], set[str]]:
    source_recipes = plan.get("source_recipes", [])
    if not isinstance(source_recipes, list) or len(source_recipes) != 33:
        failures.append("audit must lock exactly 33 installed stock recipe IDs")
        source_recipes = source_recipes if isinstance(source_recipes, list) else []
    rows = {row["recipe_id"]: row for row in load_rows(catalog / "recipes.csv")}
    jar = find_tfmg_jar(mods)
    scope = plan.get("scope", {})
    jar_hash = hashlib.sha256(jar.read_bytes()).hexdigest().upper()
    if jar.name != scope.get("installed_mod"):
        failures.append(f"installed TFMG JAR changed: {jar.name}")
    if jar_hash != scope.get("installed_mod_sha256"):
        failures.append(f"installed TFMG JAR hash changed: {jar_hash}")

    source_ids: set[str] = set()
    source_outputs: set[str] = set()
    proposed_ids: set[str] = set()
    retained_ids: set[str] = set()
    with zipfile.ZipFile(jar) as archive:
        names = set(archive.namelist())
        for source in source_recipes:
            identity = str(source.get("id", ""))
            path = str(source.get("path", ""))
            output = str(source.get("output", ""))
            classification = source.get("classification")
            if identity in source_ids:
                failures.append(f"duplicate installed source recipe ID: {identity}")
            source_ids.add(identity)
            source_outputs.add(output)
            if classification == "proposed_source_owned":
                proposed_ids.add(identity)
            elif classification == "retained_stock_redundant_variant":
                retained_ids.add(identity)
            else:
                failures.append(f"{identity}: invalid source classification {classification!r}")
            row = rows.get(identity)
            if row is None:
                failures.append(f"installed source recipe is absent from catalog: {identity}")
                continue
            if row.get("source_jar") != jar.name or row.get("source_path") != path:
                failures.append(f"{identity}: catalog JAR/path drifted")
            if row.get("recipe_type") != source.get("type"):
                failures.append(f"{identity}: catalog recipe type drifted")
            if output not in recipe_outputs(row):
                failures.append(f"{identity}: catalog no longer reports output {output}")
            if path not in names:
                failures.append(f"{identity}: installed source path is absent: {path}")
                continue
            raw = archive.read(path)
            digest = hashlib.sha256(raw).hexdigest().upper()
            if digest != source.get("sha256"):
                failures.append(f"{identity}: installed source JSON hash changed: {digest}")
            document = json.loads(raw)
            if document.get("type") != source.get("type"):
                failures.append(f"{identity}: installed source recipe type changed")
            try:
                actual_output, actual_count = raw_recipe_result(document)
            except ValueError as error:
                failures.append(f"{identity}: {error}")
            else:
                if actual_output != output or actual_count != source.get("output_count"):
                    failures.append(
                        f"{identity}: installed output/count changed to {actual_count}x {actual_output}"
                    )

        runtime = plan.get("runtime_evidence", {})
        classes = runtime.get("classes", [])
        if not isinstance(classes, list) or len(classes) != 12:
            failures.append("runtime evidence must lock exactly 12 functional TFMG classes")
        for evidence in classes if isinstance(classes, list) else []:
            path = str(evidence.get("path", ""))
            if path not in names:
                failures.append(f"runtime class is absent from installed TFMG JAR: {path}")
                continue
            digest = hashlib.sha256(archive.read(path)).hexdigest().upper()
            if digest != evidence.get("sha256"):
                failures.append(f"runtime class hash changed: {path} -> {digest}")

        installed_tag = runtime.get("installed_industrial_pipe_tag", {})
        path = str(installed_tag.get("path", ""))
        if path not in names:
            failures.append(f"installed industrial-pipe tag is absent: {path}")
        else:
            raw = archive.read(path)
            if hashlib.sha256(raw).hexdigest().upper() != installed_tag.get("sha256"):
                failures.append("installed industrial-pipe tag hash changed")
            document = json.loads(raw)
            if document.get("values") != installed_tag.get("values"):
                failures.append("installed industrial-pipe tag values changed")

        processes = runtime.get("vat_process_recipes", [])
        if not isinstance(processes, list) or len(processes) != 10:
            failures.append("runtime evidence must lock exactly ten installed vat processes")
        for evidence in processes if isinstance(processes, list) else []:
            path = str(evidence.get("path", ""))
            if path not in names:
                failures.append(f"installed vat process is absent: {path}")
                continue
            raw = archive.read(path)
            digest = hashlib.sha256(raw).hexdigest().upper()
            if digest != evidence.get("sha256"):
                failures.append(f"installed vat-process hash changed: {path} -> {digest}")
            document = json.loads(raw)
            if document.get("type") != "tfmg:vat_machine_recipe":
                failures.append(f"installed vat process type changed: {path}")
            if document.get("allowed_vat_types") != evidence.get("allowed_vat_types"):
                failures.append(f"installed vat allowed types changed: {path}")
            if document.get("heat_requirement", "none") != evidence.get("heat_requirement"):
                failures.append(f"installed vat heat requirement changed: {path}")
            if document.get("min_size", 1) != evidence.get("min_size"):
                failures.append(f"installed vat minimum size changed: {path}")

    extension = plan.get("runtime_evidence", {}).get("project_industrial_pipe_tag_extension", {})
    if PROJECT_PIPE_TAG.as_posix().endswith(str(extension.get("path", "")).replace("\\", "/")) is False:
        failures.append("project industrial-pipe tag path drifted")
    if not PROJECT_PIPE_TAG.is_file():
        failures.append("project industrial-pipe tag extension is absent")
    else:
        raw = PROJECT_PIPE_TAG.read_bytes()
        if hashlib.sha256(raw).hexdigest().upper() != extension.get("sha256"):
            failures.append("project industrial-pipe tag extension hash changed")
        document = json.loads(raw)
        if document.get("replace", False) != extension.get("replace"):
            failures.append("project industrial-pipe tag replacement behavior changed")
        if document.get("values") != extension.get("values"):
            failures.append("project industrial-pipe tag extension values changed")

    return source_ids, source_outputs, proposed_ids, retained_ids


def validate_classification(
    plan: dict[str, Any], source_outputs: set[str], proposed_ids: set[str], retained_ids: set[str], failures: list[str]
) -> tuple[set[str], set[str]]:
    classification = plan.get("classification", {})
    proposed = set(classification.get("proposed_source_owned_outputs", []))
    retained = set(classification.get("retained_stock_outputs", []))
    if len(proposed) != 12:
        failures.append("functional classification must select exactly 12 canonical source-owned outputs")
    if len(retained) != 16:
        failures.append("functional classification must retain exactly 16 stock variant outputs")
    if proposed & retained:
        failures.append(f"functional classification overlaps: {sorted(proposed & retained)}")
    if proposed | retained != source_outputs:
        failures.append("the proposed/retained output partition does not cover all 28 functional outputs")
    if classification.get("deferred_outputs") != [] or classification.get("disabled_outputs") != []:
        failures.append("this bounded audit must not defer or disable functional installed variants")
    proposed_source_outputs = {
        str(source.get("output"))
        for source in plan.get("source_recipes", [])
        if source.get("id") in proposed_ids
    }
    retained_source_outputs = {
        str(source.get("output"))
        for source in plan.get("source_recipes", [])
        if source.get("id") in retained_ids
    }
    if proposed != proposed_source_outputs:
        failures.append("proposed output classification disagrees with per-source classification")
    if retained != retained_source_outputs:
        failures.append("retained output classification disagrees with per-source classification")
    return proposed, retained


def validate_current_state(
    plan: dict[str, Any], proposed: set[str], seed: dict[str, Any],
    manifest: dict[str, Any], failures: list[str],
) -> None:
    state = plan.get("current_managed_state", {})
    automatic = state.get("replaced_automatic_owners", [])
    if not isinstance(automatic, list) or len(automatic) != 5:
        failures.append("implementation evidence must lock exactly five replaced automatic owners")
        automatic = automatic if isinstance(automatic, list) else []
    if automatic != REPLACED_AUTO_EVIDENCE:
        failures.append("replaced automatic owner evidence drifted")
    seed_by_id = recipes_by_id(seed)
    manifest_by_id = recipes_by_id(manifest)
    contracts = [row for row in plan.get("replacement_contracts", []) if isinstance(row, dict)]
    contracts_by_output = {managed_output(seed_spec(row))[0]: row for row in contracts}

    seed_owners: dict[str, list[str]] = {}
    manifest_owners: dict[str, list[str]] = {}
    for identity, recipe in seed_by_id.items():
        try:
            output, _ = managed_output(recipe)
        except ValueError:
            continue
        if output in proposed:
            seed_owners.setdefault(output, []).append(identity)
    for identity, recipe in manifest_by_id.items():
        try:
            output, _ = managed_output(recipe)
        except ValueError:
            continue
        if output in proposed:
            manifest_owners.setdefault(output, []).append(identity)

    expected_outputs: set[str] = set()
    for expected in automatic:
        identity = str(expected.get("managed_id", ""))
        output = str(expected.get("output", ""))
        expected_outputs.add(output)
        if identity in seed_by_id or identity in manifest_by_id:
            failures.append(f"replaced automatic owner survived implementation: {identity}")
    if expected_outputs != {
        "tfmg:cast_iron_pipe",
        "tfmg:cast_iron_fluid_tank",
        "tfmg:cast_iron_mechanical_pump",
        "tfmg:cast_iron_chemical_vat",
        "tfmg:steel_chemical_vat",
    }:
        failures.append("the exact five audited automatic-owner outputs drifted")

    for output in proposed:
        contract = contracts_by_output.get(output)
        if contract is None:
            failures.append(f"implemented output has no reviewed contract: {output}")
            continue
        identity = str(contract.get("id", ""))
        actual = seed_by_id.get(identity)
        expected = seed_spec(contract)
        if actual is None:
            failures.append(f"implemented fluid recipe is absent from authoritative seed: {identity}")
        elif actual != expected:
            differing = sorted(
                field for field in set(actual) | set(expected)
                if actual.get(field) != expected.get(field)
            )
            failures.append(f"{identity}: authoritative seed differs from reviewed contract in {differing}")
        if seed_owners.get(output) != [identity]:
            failures.append(f"{identity}: output does not have one seed owner; owners={seed_owners.get(output, [])}")
        if manifest_owners.get(output) != [identity]:
            failures.append(f"{identity}: output does not have one assembled owner; owners={manifest_owners.get(output, [])}")
    expected_source_ids = [str(row.get("id", "")) for row in contracts]
    if state.get("source_owned_output_owners") != expected_source_ids:
        failures.append("current state must record the twelve source-owned recipe IDs in order")

    script_hits: list[str] = []
    if PACK_SCRIPTS.is_dir():
        for path in sorted(PACK_SCRIPTS.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
                continue
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if any(output in text for output in proposed):
                script_hits.append(path.relative_to(PROJECT).as_posix())
    if script_hits:
        failures.append(f"focused pack scripts unexpectedly mention proposed outputs: {script_hits}")
    if state.get("focused_script_output_owners") != []:
        failures.append("plan must record zero focused-script output owners")

    implementation = plan.get("seed_implementation", {})
    expected_auto_ids = {str(row.get("managed_id", "")) for row in automatic}
    if (
        implementation.get("status") != "source_owned"
        or implementation.get("authoritative_source") != "progression/managed_recipe_overhaul.seed.json"
        or implementation.get("recipe_count") != 12
        or implementation.get("exact_stock_removals") != 15
        or implementation.get("exclusive_output_owners") != 12
        or set(implementation.get("replaced_automatic_owner_ids", [])) != expected_auto_ids
        or implementation.get("generated_artifacts") != "intentionally_not_regenerated"
    ):
        failures.append("seed_implementation metadata is incomplete or stale")


def validate_assignments_and_machine(
    plan: dict[str, Any], catalog: Path, seed: dict[str, Any],
    assignments_document: dict[str, Any], failures: list[str],
) -> None:
    assignments = assignments_document.get("nodes", assignments_document)
    contract = plan.get("assignment_contract", {})
    already = contract.get("already_assigned", {})
    additions = contract.get("exact_additions_required", {})
    addition_count = sum(len(values) for values in additions.values()) if isinstance(additions, dict) else -1
    if addition_count != 7 or contract.get("addition_count") != 7:
        failures.append("assignment contract must contain exactly seven additions")
    expected_already = {
        "CR01 — The Steel Age": [
            "tfmg:cast_iron_pipe",
            "tfmg:cast_iron_fluid_tank",
            "tfmg:cast_iron_mechanical_pump",
        ],
        "CR01 — Chemical Processing": [
            "tfmg:cast_iron_chemical_vat",
            "tfmg:steel_chemical_vat",
        ],
    }
    expected_additions = {
        "CR01 — Chemical Processing": [
            "tfmg:steel_pipe",
            "tfmg:steel_fluid_tank",
            "tfmg:steel_mechanical_pump",
        ],
        "CR01 — Advanced Electronics Manufacturing": ["tfmg:electric_pump"],
        "CR01 — Diesel Processing": ["tfmg:industrial_pipe"],
        "CR01 — Advanced Alloy Mixing": ["tfmg:fireproof_chemical_vat"],
        "CR01 — Heavy Diesel Engines": ["tfmg:aluminum_pipe"],
    }
    if already != expected_already:
        failures.append("the exact current assignment inventory drifted")
    if additions != expected_additions:
        failures.append("the exact seven assignment additions drifted")
    for node, outputs in already.items():
        actual = set(assignments.get(node, {}).get("unlocks", []))
        missing = set(outputs) - actual
        if missing:
            failures.append(f"current assignment drifted for {node}: missing {sorted(missing)}")
    prefixes = contract.get("existing_prefixes", {})
    expected_prefixes = {
        "CR01 — Chemical Processing": ["tfmg:cast_iron_chemical_vat", "tfmg:steel_chemical_vat", "tfmg:centrifuge", "tfmg:sulfuric_acid_bucket", "tfmg:rubber_sheet", "tfmg:cable_tube", "tfmg:accumulator"],
        "CR01 — Advanced Electronics Manufacturing": ["tfmg:etched_circuit_board", "tfmg:coated_circuit_board", "tfmg:industrial_mixer"],
        "CR01 — Diesel Processing": ["tfmg:steel_distillation_controller", "tfmg:steel_distillation_output", "tfmg:diesel_bucket"],
        "CR01 — Advanced Alloy Mixing": ["createmetallurgy:industrial_crucible", "createmetallurgy:foundry_basin", "createmetallurgy:foundry_lid", "createmetallurgy:foundry_mixer", "bigreactors:yellorium"],
        "CR01 — Heavy Diesel Engines": ["createdieselgenerators:large_diesel_engine", "createdieselgenerators:huge_diesel_engine", "createdieselgenerators:engine_turbocharger", "tfmg:turbine_engine"],
    }
    if prefixes != expected_prefixes:
        failures.append("assignment existing-prefix evidence drifted")
    for node, outputs in additions.items():
        actual = assignments.get(node, {}).get("unlocks", [])
        expected = prefixes.get(node, []) + outputs
        if actual[:len(expected)] != expected:
            failures.append(f"{node}: assignments must preserve the existing prefix and append reviewed outputs in order")
    if (
        contract.get("status") != "appended_without_reordering"
        or contract.get("authoritative_source") != "progression/machine_node_assignments.json"
    ):
        failures.append("assignment implementation metadata is incomplete or stale")

    phase_by_node = seed.get("phase_by_node", {})
    for recipe in plan.get("replacement_contracts", []):
        node = str(recipe.get("node", ""))
        if phase_by_node.get(node) != recipe.get("phase"):
            failures.append(f"{recipe.get('id')}: node/phase mapping drifted for {node}")

    approved = plan.get("approved_machine_environments", [])
    expected_approved = ["create:mechanical_press", "createcasing:copper_press", "createcasing:brass_press"]
    if approved != expected_approved:
        failures.append("approved fluid-infrastructure machine environments changed")
    reachability = plan.get("machine_reachability", {})
    items = catalog_item_ids(catalog)
    environments = collect_environment_items(load_json(ENVIRONMENTS))
    if set(expected_approved) - items or set(expected_approved) - environments:
        failures.append("one or more approved presses are not concrete installed compacting environments")
    output_owners: dict[str, list[dict[str, Any]]] = {}
    for recipe in seed.get("recipes", []):
        if isinstance(recipe, dict):
            try:
                output, _ = managed_output(recipe)
            except ValueError:
                continue
            output_owners.setdefault(output, []).append(recipe)
    expected_reachability = {
        "create:mechanical_press": ("Mechanical Foundations", "industrial_colonies:mechanical/mechanical_press", "basic mechanical cast-iron bootstrap"),
        "createcasing:copper_press": ("Steam & Brass", "industrial_colonies:manufacturing/copper_press", "electrical and conductive assemblies"),
        "createcasing:brass_press": ("Steam & Brass", "industrial_colonies:manufacturing/brass_press", "precision pressure assemblies before the heavy press is reachable"),
    }
    for item, (phase, identity, role) in expected_reachability.items():
        evidence = reachability.get(item, {})
        owners = output_owners.get(item, [])
        if len(owners) != 1 or owners[0].get("id") != identity or owners[0].get("phase") != phase:
            failures.append(f"{item}: source recipe/phase reachability drifted")
        if evidence != {
            "phase": phase,
            "source_owned_recipe": identity,
            "installed_item": True,
            "environment_family": "compacting",
            "manufacturing_role": role,
        }:
            failures.append(f"{item}: machine reachability evidence drifted")

    expected_heavy = [
        ("createcasing:railway_press", "Electrical Manufacturing", "railway"),
        ("createcasing:industrial_iron_press", "Mekanized Industry", "industrial_iron"),
        ("createcasing:weathered_iron_press", "High-Energy Grid", "weathered_iron"),
    ]
    deferred = plan.get("deferred_heavy_machine_environments", [])
    if [
        (row.get("item"), row.get("phase"), row.get("machine_family_tier"))
        for row in deferred if isinstance(row, dict)
    ] != expected_heavy:
        failures.append("deferred heavy-industrial press evidence drifted")
    families = {
        str(row.get("tier", "")): str(row.get("phase", ""))
        for row in seed.get("machine_families", []) if isinstance(row, dict)
    }
    for item, phase, tier in expected_heavy:
        if item not in items or item not in environments or families.get(tier) != phase:
            failures.append(f"{item}: installed heavy-industrial phase evidence drifted")

    phase_rank = {phase: index for index, phase in enumerate(seed.get("phase_order", []))}
    for recipe in plan.get("replacement_contracts", []):
        identity = str(recipe.get("id", ""))
        machine = str(recipe.get("machine", ""))
        if machine != EXPECTED_MACHINE_BY_ID.get(identity):
            failures.append(f"{identity}: exact casing-philosophy machine routing changed")
        machine_phase = reachability.get(machine, {}).get("phase")
        recipe_phase = recipe.get("phase")
        if machine_phase not in phase_rank or recipe_phase not in phase_rank or phase_rank[machine_phase] > phase_rank[recipe_phase]:
            failures.append(f"{identity}: machine environment is not phase-reachable")
        if machine in {item for item, _, _ in expected_heavy}:
            failures.append(f"{identity}: later heavy-industrial press creates a phase bypass")


def validate_downstream_consumers(
    plan: dict[str, Any], seed: dict[str, Any], failures: list[str]
) -> None:
    by_id = {
        str(recipe.get("id")): recipe
        for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict) and recipe.get("id")
    }
    consumers = plan.get("downstream_source_owned_consumers", [])
    if not isinstance(consumers, list) or len(consumers) != 5:
        failures.append("downstream evidence must lock exactly five source-owned consumers")
        return
    for evidence in consumers:
        identity = str(evidence.get("id", ""))
        recipe = by_id.get(identity)
        if recipe is None:
            failures.append(f"downstream source-owned consumer is absent: {identity}")
            continue
        strings = collect_strings(recipe)
        missing = set(evidence.get("requires", [])) - strings
        if missing:
            failures.append(f"{identity}: downstream fluid-infrastructure inputs drifted: {sorted(missing)}")


def contract_refs(contract: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for index, value in enumerate(contract.get("inputs", [])):
        yield f"inputs[{index}]", str(value)
    machine = contract.get("machine")
    if machine:
        yield "machine", str(machine)


def validate_contracts(
    plan: dict[str, Any], catalog: Path, seed: dict[str, Any], proposed_ids: set[str],
    proposed: set[str], retained_ids: set[str], failures: list[str]
) -> None:
    contracts = plan.get("replacement_contracts", [])
    if not isinstance(contracts, list) or len(contracts) != 12:
        failures.append("fluid-infrastructure repair must contain exactly twelve contracts")
        return
    items = catalog_item_ids(catalog)
    environments = collect_environment_items(load_json(ENVIRONMENTS))
    approved_machines = set(plan.get("approved_machine_environments", []))
    allowed_tags = set(plan.get("ingredient_policy", {}).get("allowed_tags", []))
    installed_tags = catalog_tag_ids(catalog)
    missing_tags = allowed_tags - installed_tags
    if missing_tags:
        failures.append(f"audited ingredient tags have no installed recipe evidence: {sorted(missing_tags)}")
    forbidden = tuple(plan.get("ingredient_policy", {}).get("steel_age_forbidden_fragments", []))
    source_counts: dict[str, set[int]] = {}
    for source in plan.get("source_recipes", []):
        source_counts.setdefault(str(source.get("output")), set()).add(int(source.get("output_count", 1)))

    ids: set[str] = set()
    output_to_id: dict[str, str] = {}
    order_by_id: dict[str, int] = {}
    phase_by_id: dict[str, str] = {}
    previous = -1
    actual_removals: list[str] = []
    for contract in contracts:
        identity = str(contract.get("id", ""))
        if not RESOURCE_ID.fullmatch(identity) or not identity.startswith("industrial_colonies:fluid_infrastructure/"):
            failures.append(f"invalid fluid-infrastructure contract ID: {identity!r}")
        if identity in ids:
            failures.append(f"duplicate fluid-infrastructure contract ID: {identity}")
        ids.add(identity)
        order = contract.get("batch_order")
        if not isinstance(order, int) or isinstance(order, bool) or order <= previous:
            failures.append(f"{identity}: batch_order must be strictly increasing")
        else:
            order_by_id[identity] = order
            previous = order
        phase_by_id[identity] = str(contract.get("phase", ""))
        try:
            output_count, output = split_ref(str(contract.get("output", "")))
        except ValueError as error:
            failures.append(f"{identity}: {error}")
            continue
        if output in output_to_id:
            failures.append(f"duplicate proposed output owner: {output}")
        output_to_id[output] = identity
        if output not in items:
            failures.append(f"{identity}: output is absent from installed item catalog: {output}")
        if source_counts.get(output) != {output_count}:
            failures.append(f"{identity}: stock batch output count is not preserved")
        removals = contract.get("remove_exact", [])
        if not isinstance(removals, list) or not removals:
            failures.append(f"{identity}: must retire one or more exact installed source IDs")
            removals = []
        actual_removals.extend(str(value) for value in removals)
        expected = {
            str(source.get("id"))
            for source in plan.get("source_recipes", [])
            if source.get("output") == output and source.get("classification") == "proposed_source_owned"
        }
        if set(removals) != expected or len(removals) != len(expected):
            failures.append(f"{identity}: exact stock removals drifted for {output}")
        if contract.get("exclusive_output") is not True:
            failures.append(f"{identity}: proposed output ownership must be exclusive")
        if contract.get("type") != "compacting":
            failures.append(f"{identity}: bounded repair must use compacting")
        if contract.get("machine") != EXPECTED_MACHINE_BY_ID.get(identity):
            failures.append(f"{identity}: unapproved machine environment: {contract.get('machine')}")
        inputs = contract.get("inputs", [])
        if not isinstance(inputs, list) or not 1 <= len(inputs) <= 9:
            failures.append(f"{identity}: compacting must have 1-9 explicit physical slots")

    if set(output_to_id) != proposed:
        failures.append("the twelve canonical outputs and replacement contracts are not one-to-one")
    if set(actual_removals) != proposed_ids or len(actual_removals) != 15:
        failures.append("the fifteen exact installed source removals are incomplete, duplicate, or broadened")
    leaked = set(actual_removals) & retained_ids
    if leaked:
        failures.append(f"retained stock recipes leaked into the removal set: {sorted(leaked)}")

    phase_order = {
        phase: index for index, phase in enumerate(seed.get("phase_order", []))
    }
    managed_output_phase: dict[str, str] = {}
    for managed_recipe in seed.get("recipes", []):
        if not isinstance(managed_recipe, dict):
            continue
        try:
            managed_item, _ = managed_output(managed_recipe)
        except ValueError:
            continue
        managed_output_phase[managed_item] = str(managed_recipe.get("phase", ""))
    presteel_ids: set[str] = set()
    for contract in contracts:
        identity = str(contract.get("id", ""))
        role = str(contract.get("bootstrap_role", ""))
        if role == "presteel_required":
            presteel_ids.add(identity)
        elif role not in {
            "post_first_steel_chemical",
            "post_first_steel_refinery",
            "post_first_steel_high_temperature",
            "post_first_steel_turbomachinery",
            "cross_branch_electrical_upgrade",
        }:
            failures.append(f"{identity}: unknown bootstrap role {role!r}")
        declared = set(contract.get("depends_on_batch", []))
        observed: set[str] = set()
        for field, raw in contract_refs(contract):
            try:
                count, ref = split_ref(raw)
            except ValueError as error:
                failures.append(f"{identity}: {error}")
                continue
            if count > 1 and ref.startswith("#"):
                failures.append(f"{identity}: counted tag syntax is forbidden; repeat physical tag slots")
            if field == "machine":
                if ref not in approved_machines or ref not in environments or ref not in items:
                    failures.append(f"{identity}: machine environment is not approved/concrete: {ref}")
                continue
            if ref.startswith("#"):
                if not TAG_ID.fullmatch(ref) or ref not in allowed_tags:
                    failures.append(f"{identity}: ingredient tag is outside the audited physical set: {ref}")
            elif not RESOURCE_ID.fullmatch(ref) or ref not in items:
                failures.append(f"{identity}: concrete ingredient is absent/invalid in {field}: {ref}")
            if ref in output_to_id:
                dependency = output_to_id[ref]
                observed.add(dependency)
                if order_by_id.get(dependency, sys.maxsize) >= order_by_id.get(identity, -1):
                    failures.append(f"{identity}: same-batch dependency is not earlier: {dependency}")
                if phase_order.get(phase_by_id.get(dependency, ""), sys.maxsize) > phase_order.get(
                    phase_by_id.get(identity, ""), -1
                ):
                    failures.append(f"{identity}: same-batch dependency comes from a later phase: {dependency}")
            if ref in EXTERNAL_OUTPUT_OWNERS:
                observed.add(EXTERNAL_OUTPUT_OWNERS[ref])
            ingredient_phase = managed_output_phase.get(ref)
            if ingredient_phase is not None and phase_order.get(ingredient_phase, sys.maxsize) > phase_order.get(
                phase_by_id.get(identity, ""), -1
            ):
                failures.append(f"{identity}: managed input {ref} comes from later phase {ingredient_phase}")
            if role == "presteel_required" and any(fragment in ref for fragment in forbidden):
                failures.append(f"{identity}: presteel contract consumes forbidden material: {ref}")
        if declared != observed:
            failures.append(
                f"{identity}: depends_on_batch mismatch, observed={sorted(observed)}, declared={sorted(declared)}"
            )
        unknown = declared - ids - set(EXTERNAL_OUTPUT_OWNERS.values())
        if unknown:
            failures.append(f"{identity}: unknown same-batch dependencies: {sorted(unknown)}")
        predecessor = contract.get("same_family_predecessor")
        input_refs = {split_ref(str(value))[1] for value in contract.get("inputs", [])}
        if predecessor is not None:
            if predecessor not in input_refs:
                failures.append(f"{identity}: same-family predecessor is not a physical input")
            predecessor_id = output_to_id.get(str(predecessor))
            if predecessor_id is None or predecessor_id not in declared:
                failures.append(f"{identity}: same-family predecessor is not a declared earlier dependency")
        elif identity.endswith(("/steel_pipe", "/aluminum_pipe")) and not contract.get("predecessor_exception"):
            failures.append(f"{identity}: direct material forming must document its predecessor exception")

    expected_presteel = {
        "industrial_colonies:fluid_infrastructure/cast_iron_pipe",
        "industrial_colonies:fluid_infrastructure/cast_iron_fluid_tank",
        "industrial_colonies:fluid_infrastructure/cast_iron_mechanical_pump",
    }
    if presteel_ids != expected_presteel:
        failures.append("presteel bootstrap must be exactly the cast-iron pipe/tank/mechanical-pump trio")
    steel_pipe = next((value for value in contracts if value.get("id", "").endswith("/steel_pipe")), {})
    aluminum_pipe = next((value for value in contracts if value.get("id", "").endswith("/aluminum_pipe")), {})
    if any("cast_iron_pipe" in str(value) for value in steel_pipe.get("inputs", [])):
        failures.append("steel pipe recipe creates an invalid cast-iron-to-steel conversion shortcut")
    if any("pipe" in str(value) and not str(value).startswith("#c:") for value in aluminum_pipe.get("inputs", [])):
        failures.append("aluminum pipe recipe creates an invalid earlier-pipe conversion shortcut")


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("fluid_audit_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load managed recipe compiler: {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_compilation(
    plan: dict[str, Any], seed: dict[str, Any], failures: list[str]
) -> None:
    recipes = []
    for contract in plan.get("replacement_contracts", []):
        recipes.append(
            {
                "id": contract.get("id"),
                "phase": contract.get("phase"),
                "order": contract.get("batch_order"),
                "type": contract.get("type"),
                "comment": "Audited TFMG fluid-infrastructure manufacturing contract",
                "machine": contract.get("machine"),
                "inputs": contract.get("inputs"),
                "output": contract.get("output"),
                "remove": contract.get("remove_exact"),
                "exclusive_output": contract.get("exclusive_output"),
            }
        )
    manifest = {
        "schema_version": 1,
        "project": "tfmg-fluid-infrastructure-audit",
        "phase_order": seed.get("phase_order", []),
        "recipes": recipes,
        "machine_families": [],
        "additional_removals": [],
        "retired_recipe_uids": [],
        "retired_removal_uids": [],
    }
    compiler = load_generator()
    with tempfile.TemporaryDirectory(prefix="tfmg-fluid-audit-") as temporary:
        root = Path(temporary)
        manifest_path = root / "audit.json"
        output_path = root / "compiled.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        try:
            compiled = compiler.compile_manifest(manifest_path, output_path)
        except (KeyError, TypeError, ValueError) as error:
            failures.append(f"KJSGen compiler rejected the twelve audit contracts: {error}")
            return
    contract = plan.get("compiled_kjsgen_contract", {})
    cards = compiled.get("recipes", [])
    removals = compiled.get("removals", [])
    if len(cards) != contract.get("expected_recipe_cards"):
        failures.append(f"compiled KJSGen recipe-card count drifted: {len(cards)}")
    if len(removals) != contract.get("expected_removal_cards"):
        failures.append(f"compiled KJSGen removal-card count drifted: {len(removals)}")
    expected_type = contract.get("expected_card_type")
    if {card.get("type") for card in cards} != {expected_type}:
        failures.append(f"compiled KJSGen card type drifted: {sorted({card.get('type') for card in cards})}")
    expected_ids = {value.get("id") for value in plan.get("replacement_contracts", [])}
    if {card.get("recipeId") for card in cards} != expected_ids:
        failures.append("compiled KJSGen recipe IDs do not match the twelve contracts")
    machine_counts = Counter(
        card.get("slots", {}).get("__machine_process_compacting", {}).get("id")
        for card in cards
    )
    if machine_counts != Counter(contract.get("expected_machine_counts", {})):
        failures.append(f"compiled KJSGen exact-machine distribution drifted: {dict(machine_counts)}")
    expected_removals = {
        identity
        for value in plan.get("replacement_contracts", [])
        for identity in value.get("remove_exact", [])
    }
    if {value.get("recipeId") for value in removals} != expected_removals:
        failures.append("compiled KJSGen exact-removal cards drifted")


def validate_plan(
    plan: dict[str, Any], catalog: Path, mods: Path, seed: dict[str, Any],
    manifest: dict[str, Any], assignments: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    if plan.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        failures.append("audit status must be implemented_in_seed")
    if plan.get("decision") != "GO_WITH_TWELVE_CONTRACT_CANONICAL_REPAIR":
        failures.append("audit decision must remain GO_WITH_TWELVE_CONTRACT_CANONICAL_REPAIR")
    scope = plan.get("scope", {})
    expected_scope = {
        "functional_outputs": 28,
        "installed_stock_recipes": 33,
        "proposed_outputs": 12,
        "proposed_exact_removals": 15,
        "retained_stock_outputs": 16,
        "replaced_automatic_owners": 5,
        "current_source_owned_owners": 12,
    }
    for field, expected in expected_scope.items():
        if scope.get(field) != expected:
            failures.append(f"scope.{field} must be {expected}")

    source_ids, source_outputs, proposed_ids, retained_ids = validate_installed_evidence(
        plan, catalog, mods, failures
    )
    if len(source_ids) != 33 or len(source_outputs) != 28:
        failures.append("installed audit inventory must resolve to 33 recipes and 28 functional outputs")
    proposed, _ = validate_classification(plan, source_outputs, proposed_ids, retained_ids, failures)
    validate_current_state(plan, proposed, seed, manifest, failures)
    validate_assignments_and_machine(plan, catalog, seed, assignments, failures)
    validate_downstream_consumers(plan, seed, failures)
    validate_contracts(plan, catalog, seed, proposed_ids, proposed, retained_ids, failures)
    validate_compilation(plan, seed, failures)

    compiled = plan.get("compiled_kjsgen_contract", {})
    if compiled.get("status") != "passed":
        failures.append("compiled KJSGen contract must record the passing focused proof")
    result = plan.get("validation_result", {})
    expected_result = {
        "functional_outputs": 28,
        "stock_recipes": 33,
        "proposed_contracts": 12,
        "exact_removals": 15,
        "retained_stock_outputs": 16,
        "assignment_additions": 7,
        "steel_age_forbidden_inputs": 0,
        "compiled_recipe_cards": 12,
        "compiled_removal_cards": 15,
        "mutation_tests": 21,
        "focused_unit_tests": 21,
        "isolated_manifest_recipes": 353,
        "isolated_automatic_recipes": 172,
        "isolated_compiled_recipe_cards": 421,
        "isolated_exact_removals": 739,
        "managed_dependency_edges": 922,
        "managed_dependency_warnings": 0,
        "physical_progression": "passed",
        "early_manufacturing_regression": "passed",
        "steelworks_regression": "passed",
        "petroleum_regression": "passed",
        "transmission_foundation_regression": "passed",
        "transmitter_upgrade_regression": "passed",
    }
    for field, expected in expected_result.items():
        if result.get(field) != expected:
            failures.append(f"validation_result.{field} must be {expected}")
    if result.get("status") != "passed":
        failures.append("validation result must record the passing focused audit")
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--seed", type=Path, default=SEED)
    parser.add_argument("--manifest", type=Path, default=MANAGED)
    parser.add_argument("--assignments", type=Path, default=ASSIGNMENTS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = load_json(args.plan)
        seed = load_json(args.seed.resolve())
        manifest = load_json(args.manifest.resolve())
        assignments = load_json(args.assignments.resolve())
        failures = validate_plan(
            plan, args.catalog.resolve(), args.mods.resolve(), seed, manifest, assignments
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if failures:
        print(f"TFMG fluid-infrastructure audit failed ({len(failures)} issue(s)):")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "TFMG fluid-infrastructure audit passed: 28 functional outputs / 33 exact stock "
        "recipes classified, 12 source-owned contracts / 15 removals compile across 3 native, "
        "8 Brass, and 1 Copper exact-machine cards; 16 equivalent variants remain stock, "
        "five automatic owners are retired, seven assignments are appended, and the DAG is clean."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
