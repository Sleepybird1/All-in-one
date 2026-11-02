#!/usr/bin/env python3
"""Validate the implemented AE2 high-energy, spatial, and MEGA-core batch."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_ae2_high_energy_spatial_mega_audit as builder
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
    "ae2:cell_workbench": "compacting",
    "ae2:controller": "sequenced_assembly",
    "ae2:export_bus": "sequenced_assembly",
    "ae2:io_port": "sequenced_assembly",
    "ae2:me_p2p_tunnel": "sequenced_assembly",
    "ae2:spatial_anchor": "compacting",
    "ae2:spatial_io_port": "sequenced_assembly",
    "ae2:spatial_pylon": "compacting",
    "megacells:mega_crafting_unit": "sequenced_assembly",
}

FAMILY_BY_OUTPUT = {
    "ae2:export_bus": "copper",
    "ae2:cell_workbench": "brass",
    "ae2:controller": "brass",
    "ae2:io_port": "brass",
    "ae2:me_p2p_tunnel": "brass",
    "ae2:spatial_anchor": "industrial_iron",
    "ae2:spatial_io_port": "industrial_iron",
    "ae2:spatial_pylon": "industrial_iron",
    "megacells:mega_crafting_unit": "industrial_iron",
}

CONTROL_MANAGED_IDS = {
    "ae2:controller": "industrial_colonies:ae2_high_energy/controller",
    "ae2:io_port": "industrial_colonies:ae2_high_energy/io_port",
    "ae2:me_p2p_tunnel": "industrial_colonies:ae2_high_energy/me_p2p_tunnel",
}


def load_json(path: Path) -> dict[str, Any]:
    return builder.load_json(path)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def normalized_ref(value: str) -> str:
    match = COUNTED_REF.fullmatch(value)
    return match.group(2) if match else value


def contract_by_output(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        builder.output_id(recipe): recipe
        for recipe in plan.get("replacement_contracts", [])
        if isinstance(recipe, dict)
    }


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


@lru_cache(maxsize=4)
def cached_non_recipe_scan(mods_text: str) -> tuple[int, tuple[str, ...]]:
    count, occurrences = builder.scan_non_recipe_occurrences(Path(mods_text))
    return count, tuple(json.dumps(row, sort_keys=True) for row in occurrences)


def validate_source_evidence(
    plan: dict[str, Any], catalog: Path, mods: Path, failures: list[str]
) -> set[str]:
    rows = load_rows(catalog / "recipes.csv")
    rows_by_id = {row["recipe_id"]: row for row in rows}
    expected_removed = [
        identity
        for output in builder.BATCH_OUTPUTS
        for identity in builder.SOURCE_REMOVALS[output]
    ]

    expected_producers = {
        output: sorted(
            row["recipe_id"] for row in rows if output in builder.split_refs(row["outputs"])
        )
        for output in builder.BATCH_OUTPUTS
    }
    if plan.get("direct_producer_audit") != expected_producers:
        failures.append("direct producer coverage drifted or an alternate producer appeared")
    for output in builder.BATCH_OUTPUTS:
        if expected_producers[output] != list(builder.SOURCE_REMOVALS[output]):
            failures.append(f"{output}: installed alternate producer bypass exists")

    sources = plan.get("removed_installed_recipes", [])
    actual_removed = [source.get("id") for source in sources if isinstance(source, dict)]
    if actual_removed != expected_removed:
        failures.append("exact nine installed removal IDs drifted")
    for source in sources:
        if not isinstance(source, dict):
            failures.append("installed removal evidence contains a non-object")
            continue
        identity = str(source.get("id", ""))
        row = rows_by_id.get(identity)
        if row is None:
            failures.append(f"installed removal recipe is absent from catalog: {identity}")
            continue
        for field in ("recipe_type", "source_jar", "source_path"):
            if source.get(field) != row.get(field):
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
        if source.get("raw_type") != document.get("type"):
            failures.append(f"{identity}: installed raw recipe type changed")
        if source.get("catalog_inputs") != sorted(builder.split_refs(row["inputs"])):
            failures.append(f"{identity}: catalog input evidence drifted")
        if source.get("catalog_outputs") != sorted(builder.split_refs(row["outputs"])):
            failures.append(f"{identity}: catalog output evidence drifted")

    preserved = plan.get("preserved_bulk_recipes", [])
    preserved_ids = [source.get("id") for source in preserved if isinstance(source, dict)]
    if preserved_ids != list(builder.PRESERVE_RECIPE_IDS):
        failures.append("exact eleven bulk cable/MEGA preservation IDs drifted")
    for source in preserved:
        if not isinstance(source, dict):
            failures.append("preserved bulk evidence contains a non-object")
            continue
        identity = str(source.get("id", ""))
        row = rows_by_id.get(identity)
        expected_role = (
            "bulk_cable_or_color_cleanup"
            if identity.startswith("ae2:network/cables/")
            else "mega_unit_closure"
        )
        if source.get("preservation_role") != expected_role:
            failures.append(f"{identity}: bulk preservation role drifted")
        if row is None:
            failures.append(f"preserved bulk recipe is absent from catalog: {identity}")
            continue
        jar = mods / row["source_jar"]
        try:
            with zipfile.ZipFile(jar) as archive:
                raw = archive.read(row["source_path"])
        except (FileNotFoundError, KeyError, zipfile.BadZipFile) as error:
            failures.append(f"{identity}: cannot read preserved source: {error}")
            continue
        if source.get("source_sha256") != digest_bytes(raw):
            failures.append(f"{identity}: preserved source JSON hash changed")
        inputs = builder.split_refs(row["inputs"])
        if expected_role == "mega_unit_closure" and "megacells:mega_crafting_unit" not in inputs:
            failures.append(f"{identity}: preserved MEGA closure no longer consumes the hard unit")
        if expected_role == "bulk_cable_or_color_cleanup" and not (
            inputs.intersection({"ae2:quartz_fiber", "ae2:fluix_glass_cable", "ae2:fluix_covered_cable", "ae2:fluix_smart_cable"})
        ):
            failures.append(f"{identity}: preserved cable route lost its bulk precursor")

    expected_downstream = sorted(
        (
            row
            for row in rows
            if builder.split_refs(row["inputs"]).intersection(builder.BATCH_OUTPUTS)
        ),
        key=lambda row: row["recipe_id"],
    )
    downstream = plan.get("downstream_consumer_audit", [])
    if [entry.get("id") for entry in downstream if isinstance(entry, dict)] != [
        row["recipe_id"] for row in expected_downstream
    ]:
        failures.append("downstream consumer audit coverage drifted")
    for entry in downstream:
        if not isinstance(entry, dict):
            failures.append("downstream consumer evidence contains a non-object")
            continue
        identity = entry.get("id")
        expected_role = (
            "same_batch_replaced"
            if identity in expected_removed
            else "preserved_bulk_closure"
            if identity in builder.PRESERVE_RECIPE_IDS
            else "downstream_not_owned_by_batch"
        )
        if entry.get("role") != expected_role:
            failures.append(f"{identity}: downstream ownership classification drifted")

    scan_count, serialized = cached_non_recipe_scan(str(mods.resolve()))
    occurrences = [json.loads(value) for value in serialized]
    evidence = plan.get("non_recipe_acquisition_audit", {})
    if plan.get("scope", {}).get("installed_jars_scanned_for_non_recipe_acquisition") != scan_count:
        failures.append("installed JAR scan coverage count drifted")
    if evidence.get("occurrences") != occurrences:
        failures.append("non-recipe target occurrence evidence drifted")
    external = [row for row in occurrences if row.get("role") == "external_acquisition_candidate"]
    if evidence.get("external_acquisition_candidates") != external:
        failures.append("external acquisition candidate evidence drifted")
    if external:
        failures.append("non-recipe external acquisition bypass exists")
    if any(row.get("role") != "self_drop_block_loot" for row in occurrences):
        failures.append("non-recipe target occurrence is not an ordinary self-drop")
    return set(preserved_ids)


def validate_contracts(
    plan: dict[str, Any], catalog: Path, failures: list[str]
) -> dict[str, dict[str, Any]]:
    contracts = plan.get("replacement_contracts", [])
    if not isinstance(contracts, list) or len(contracts) != 9:
        failures.append("batch must contain exactly nine replacement contracts")
        contracts = contracts if isinstance(contracts, list) else []
    by_output = contract_by_output(plan)
    if set(by_output) != set(builder.BATCH_OUTPUTS) or len(by_output) != len(contracts):
        failures.append("replacement contracts must own every exact batch output once")

    item_ids, tag_ids = catalog_ids(catalog)
    seen_ids: set[str] = set()
    for output, recipe in by_output.items():
        identity = str(recipe.get("id", ""))
        if identity in seen_ids or not RESOURCE_ID.fullmatch(identity):
            failures.append(f"blank, invalid, or duplicate managed recipe ID: {identity!r}")
        seen_ids.add(identity)
        if recipe.get("node") != builder.ASSIGNMENT_BY_OUTPUT.get(output):
            failures.append(f"{output}: node assignment drifted")
        if recipe.get("phase") != "High-Energy Grid":
            failures.append(f"{output}: must remain in High-Energy Grid")
        if recipe.get("type") != EXPECTED_TYPE_BY_OUTPUT.get(output):
            failures.append(f"{output}: manufacturing process type drifted")
        if recipe.get("remove") != list(builder.SOURCE_REMOVALS.get(output, ())):
            failures.append(f"{output}: exact source removal list drifted")
        if recipe.get("exclusive_output") is not True:
            failures.append(f"{output}: replacement lost exclusive direct ownership")
        if "pattern" in recipe or "key" in recipe or recipe.get("type") == "mechanical_crafting":
            failures.append(f"{output}: generic shaped/gate-ring manufacturing is forbidden")
        if builder.output_id(recipe) != output:
            failures.append(f"{output}: counted output normalization drifted")

        refs = builder.recipe_inputs(recipe)
        normalized_refs = [normalized_ref(value) for value in refs]
        if not any(value.startswith("tfmg:") for value in normalized_refs):
            failures.append(f"{output}: recipe is not TFMG-first")
        forbidden = set(normalized_refs).intersection(builder.FORBIDDEN_GATE_INPUTS)
        if forbidden:
            failures.append(f"{output}: recipe consumes forbidden generic Mekanism gate {sorted(forbidden)}")
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

        family = FAMILY_BY_OUTPUT[output]
        if recipe.get("type") == "compacting":
            if recipe.get("machine") != f"createcasing:{family}_press":
                failures.append(f"{output}: unapproved {family} compacting environment")
            if not 5 <= len(recipe.get("inputs", [])) <= 8:
                failures.append(f"{output}: compacting must use 5-8 physical inputs")
            try:
                card = compiler.process(recipe, compiler.stable_uid("recipe", identity))
            except (KeyError, TypeError, ValueError) as error:
                failures.append(f"{output}: KJSGen compacting compilation failed: {error}")
            else:
                if card.get("type") != "kjsgen:create_compacting":
                    failures.append(f"{output}: compiled compacting card type drifted")
        elif recipe.get("type") == "sequenced_assembly":
            if recipe.get("loops") != 1:
                failures.append(f"{output}: sequenced assembly must use exactly one loop")
            if recipe.get("transitional") != recipe.get("input"):
                failures.append(f"{output}: transitional carrier must remain the physical input")
            steps = recipe.get("steps", [])
            if not isinstance(steps, list) or not 4 <= len(steps) <= 6:
                failures.append(f"{output}: sequenced assembly must use 4-6 operations")
                steps = steps if isinstance(steps, list) else []
            for step in steps:
                if step.get("op") == "deploying":
                    expected_machine = f"createcasing:{family}_deployer"
                elif step.get("op") == "pressing":
                    expected_machine = f"createcasing:{family}_press"
                else:
                    failures.append(f"{output}: unsupported sequence operation")
                    continue
                if step.get("machine") != expected_machine:
                    failures.append(f"{output}: unapproved {family} sequence environment")
            if not steps or steps[-1].get("op") != "pressing":
                failures.append(f"{output}: sequence must finish with casing-specific pressing")
            if sum(step.get("op") == "pressing" for step in steps) != 1:
                failures.append(f"{output}: sequence must contain exactly one press operation")
            try:
                card = compiler.sequenced(recipe, compiler.stable_uid("recipe", identity))
            except (KeyError, TypeError, ValueError) as error:
                failures.append(f"{output}: KJSGen sequence compilation failed: {error}")
            else:
                if card.get("type") != "kjsgen:create_sequenced_assembly":
                    failures.append(f"{output}: compiled sequence card type drifted")

    pylon = by_output.get("ae2:spatial_pylon", {})
    if pylon.get("output") != "4x ae2:spatial_pylon":
        failures.append("spatial pylon must remain a four-segment factory batch")
    return by_output


def validate_dependencies(
    plan: dict[str, Any], by_output: dict[str, dict[str, Any]], failures: list[str]
) -> None:
    contracts = [entry for entry in plan.get("replacement_contracts", []) if isinstance(entry, dict)]
    ids = {str(recipe.get("id")): recipe for recipe in contracts}
    graph: dict[str, set[str]] = {identity: set() for identity in ids}
    for identity, recipe in ids.items():
        for dependency in recipe.get("depends_on", []):
            if dependency.startswith("industrial_colonies:ae2_high_energy/"):
                if dependency not in ids:
                    failures.append(f"{identity}: unknown same-batch dependency {dependency}")
                else:
                    graph[identity].add(dependency)

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

    control_ids = set(CONTROL_MANAGED_IDS.values())
    control_orders = [by_output.get(output, {}).get("order", 9999) for output in builder.CONTROL_OUTPUTS]
    for output in builder.SPATIAL_OUTPUTS:
        recipe = by_output.get(output, {})
        if recipe.get("order", -1) <= max(control_orders):
            failures.append(f"{output}: spatial hardware is ordered before controller/IO/P2P")
        if output in {"ae2:spatial_pylon", "ae2:spatial_io_port"} and not control_ids.issubset(
            set(recipe.get("depends_on", []))
        ):
            failures.append(f"{output}: controller/IO/P2P predecessor dependency is incomplete")

    def inputs(output: str) -> set[str]:
        return {normalized_ref(value) for value in builder.recipe_inputs(by_output.get(output, {}))}

    physical_requirements = {
        "ae2:cell_workbench": {"ae2:terminal"},
        "ae2:controller": {"ae2:energy_acceptor", "tfmg:transformer"},
        "ae2:io_port": {"ae2:drive", "ae2:interface"},
        "ae2:me_p2p_tunnel": {"ae2:engineering_processor", "tfmg:circuit_board"},
        "ae2:spatial_pylon": {"ae2:me_p2p_tunnel", "tfmg:transformer"},
        "ae2:spatial_io_port": {"ae2:io_port", "ae2:controller", "ae2:me_p2p_tunnel"},
        "ae2:spatial_anchor": {"ae2:spatial_io_port", "ae2:spatial_pylon"},
        "megacells:mega_crafting_unit": {
            "ae2:crafting_unit",
            "megacells:accumulation_processor",
            "tfmg:transformer",
        },
    }
    for output, required in physical_requirements.items():
        missing = required - inputs(output)
        if missing:
            failures.append(f"{output}: physical prerequisite chain is missing {sorted(missing)}")

    anchor_deps = set(by_output.get("ae2:spatial_anchor", {}).get("depends_on", []))
    if not {
        "industrial_colonies:ae2_high_energy/spatial_io_port",
        "industrial_colonies:ae2_high_energy/spatial_pylon_batch",
    }.issubset(anchor_deps):
        failures.append("spatial anchor dependency chain is incomplete")

    contract = plan.get("dependency_contract", {})
    if contract.get("control_outputs_before_spatial") != list(builder.CONTROL_OUTPUTS):
        failures.append("control-before-spatial contract drifted")
    if contract.get("spatial_outputs") != list(builder.SPATIAL_OUTPUTS):
        failures.append("exact spatial output contract drifted")
    if contract.get("pylon_batch_size") != 4:
        failures.append("pylon batch-size contract drifted")
    if contract.get("forbidden_gate_inputs") != sorted(builder.FORBIDDEN_GATE_INPUTS):
        failures.append("forbidden generic gate contract drifted")
    reverse = contract.get("digital_predecessor_reverse_dependencies", [])
    if not isinstance(reverse, list) or any(entry.get("batch_inputs_consumed") for entry in reverse):
        failures.append("first ME predecessor was made dependent on this high-energy batch")


def validate_prerequisites(
    plan: dict[str, Any], seed: dict[str, Any], predecessor: dict[str, Any], failures: list[str]
) -> None:
    expected = builder.prerequisite_evidence(seed, predecessor)
    if plan.get("prerequisite_evidence") != expected:
        failures.append("prerequisite owner/phase evidence drifted")
    phase_order = seed.get("phase_order", [])
    phase_index = {phase: index for index, phase in enumerate(phase_order)}
    target_index = phase_index.get("High-Energy Grid", -1)
    for entry in expected:
        output = entry["output"]
        if entry.get("observed_managed_owner") != entry.get("expected_managed_owner"):
            failures.append(f"{output}: required predecessor managed owner is absent")
        phase = entry.get("phase")
        if phase not in phase_index or phase_index[phase] > target_index:
            failures.append(f"{output}: prerequisite occurs after High-Energy Grid")
    digital_outputs = {"ae2:terminal", "ae2:interface", "ae2:energy_acceptor", "ae2:drive", "ae2:crafting_unit"}
    for entry in expected:
        if entry["output"] in digital_outputs and entry.get("phase") != "Digital Logistics":
            failures.append(f"{entry['output']}: first-network predecessor left Digital Logistics")
    for entry in expected:
        if entry["output"] == "tfmg:transformer" and entry.get("phase") != "Electrical Manufacturing":
            failures.append("TFMG transformer prerequisite left Electrical Manufacturing")


def validate_assignments(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any], failures: list[str]
) -> None:
    expected = [
        {
            "output": output,
            "required_node": builder.ASSIGNMENT_BY_OUTPUT[output],
            "required_phase": "High-Energy Grid",
            "current_nodes": [builder.ASSIGNMENT_BY_OUTPUT[output]],
            "patch_action": "none",
        }
        for output in builder.BATCH_OUTPUTS
    ]
    if plan.get("assignment_contract") != expected:
        failures.append("exact no-edit assignment/phase contract drifted")
    phase_by_node = seed.get("phase_by_node", {})
    for output in builder.BATCH_OUTPUTS:
        node = builder.ASSIGNMENT_BY_OUTPUT[output]
        nodes = builder.find_assignment_nodes(assignments, output)
        if nodes != [node]:
            failures.append(f"{output}: current assignment is not exact and unique: {nodes}")
        if phase_by_node.get(node) != "High-Energy Grid":
            failures.append(f"{output}: assigned node no longer maps to High-Energy Grid")


def validate_current_state(
    plan: dict[str, Any], seed: dict[str, Any], current: dict[str, Any], failures: list[str]
) -> None:
    explicit_by_output: dict[str, list[dict[str, Any]]] = {
        output: [] for output in builder.BATCH_OUTPUTS
    }
    for recipe in seed.get("recipes", []):
        if not isinstance(recipe, dict):
            continue
        output = builder.output_id(recipe)
        if output in explicit_by_output:
            explicit_by_output[output].append(recipe)
    contracts = contract_by_output(plan)
    for output in builder.BATCH_OUTPUTS:
        owners = explicit_by_output[output]
        if len(owners) != 1:
            failures.append(f"{output}: authoritative seed must own the output exactly once")
        elif owners[0] != contracts.get(output):
            failures.append(f"{output}: authoritative seed recipe payload drifted")
    preserved = seed.get("preserve_recipe_ids", [])
    if not isinstance(preserved, list) or not set(builder.PRESERVE_RECIPE_IDS).issubset(preserved):
        failures.append("authoritative seed lost an AE2/MEGA stock preservation ID")
    current_by_output = {
        builder.output_id(recipe): recipe
        for recipe in current.get("recipes", [])
        if isinstance(recipe, dict) and builder.output_id(recipe) in builder.BATCH_OUTPUTS
    }
    expected_state = plan.get("current_managed_state", {}).get("replaced_automatic_owners", [])
    state_by_output = {
        entry.get("output"): entry for entry in expected_state if isinstance(entry, dict)
    }
    if set(state_by_output) != set(builder.BATCH_OUTPUTS):
        failures.append("current automatic owner evidence does not cover nine outputs")
    for output in builder.BATCH_OUTPUTS:
        recipe = current_by_output.get(output)
        entry = state_by_output.get(output, {})
        if recipe is None:
            failures.append(f"current automatic managed owner is absent: {output}")
            continue
        if recipe.get("id") != builder.AUTO_OWNERS[output] or entry.get("id") != recipe.get("id"):
            failures.append(f"{output}: current automatic owner identity drifted")
        if recipe.get("type") != "mechanical_crafting" or entry.get("type") != recipe.get("type"):
            failures.append(f"{output}: retired automatic owner is no longer a generic mechanical card")
        if entry.get("remove") != recipe.get("remove") or entry.get("depends_on") != recipe.get("depends_on"):
            failures.append(f"{output}: current automatic owner evidence drifted")
        if "ABABA" not in recipe.get("pattern", []):
            failures.append(f"{output}: expected generic A/B gate-ring evidence changed")
    retired = plan.get("current_managed_state", {}).get("expected_retired_ids_after_rebuild")
    if retired != [builder.AUTO_OWNERS[output] for output in builder.BATCH_OUTPUTS]:
        failures.append("expected automatic retirement list drifted")


def validate_patch(
    plan: dict[str, Any], patch: dict[str, Any], preserved: set[str], failures: list[str]
) -> None:
    if patch.get("status") != "applied_to_authoritative_seed":
        failures.append("patch status must be applied_to_authoritative_seed")
    if patch.get("batch_id") != builder.BATCH_ID:
        failures.append("patch batch identity drifted")
    expected_bases = plan.get("implementation", {}).get("rebased_base_files")
    if patch.get("base_files") != expected_bases:
        failures.append("patch shared-file base hashes drifted")
    operations = patch.get("seed_operations", [])
    if not isinstance(operations, list) or len(operations) != 2:
        failures.append("patch must contain exactly append and preserve-union operations")
        operations = operations if isinstance(operations, list) else []
    append = next(
        (op for op in operations if op.get("op") == "append_recipe_specs_after_output_ownership_assertion"),
        None,
    )
    preserve = next((op for op in operations if op.get("op") == "union_preserve_recipe_ids"), None)
    if append is None or append.get("recipes") != plan.get("replacement_contracts"):
        failures.append("patch recipe payload differs from reviewed contracts")
    if preserve is None or preserve.get("recipe_ids") != sorted(preserved):
        failures.append("patch exact stock preservation union drifted")
    if patch.get("assignment_operations") != []:
        failures.append("assignment patch must remain empty")
    if patch.get("assignment_assertions") != plan.get("assignment_contract"):
        failures.append("assignment assertions differ from reviewed contract")
    preconditions = patch.get("preconditions", {})
    if preconditions.get("exact_outputs") != list(builder.BATCH_OUTPUTS):
        failures.append("patch exact-output precondition drifted")
    if preconditions.get("required_predecessor_managed_ids") != list(
        builder.PREREQUISITE_OWNER_IDS.values()
    ):
        failures.append("patch predecessor-owner precondition drifted")
    effects = patch.get("expected_rebuild_effects", {})
    if effects.get("retire_automatic_managed_ids") != [
        builder.AUTO_OWNERS[output] for output in builder.BATCH_OUTPUTS
    ]:
        failures.append("patch automatic retirement effect drifted")
    if effects.get("compile_exact_managed_ids") != [
        recipe["id"] for recipe in plan.get("replacement_contracts", [])
    ]:
        failures.append("patch compiled managed ID list drifted")
    expected_removed = [
        identity
        for output in builder.BATCH_OUTPUTS
        for identity in builder.SOURCE_REMOVALS[output]
    ]
    if effects.get("remove_exact_installed_recipe_ids") != expected_removed:
        failures.append("patch exact installed removal effect drifted")


def validate_plan(
    plan: dict[str, Any],
    patch: dict[str, Any],
    catalog: Path,
    mods: Path,
    seed: dict[str, Any],
    assignments: dict[str, Any],
    current: dict[str, Any],
    predecessor: dict[str, Any],
    *,
    check_determinism: bool = False,
    markdown_text: str | None = None,
) -> list[str]:
    failures: list[str] = []
    if plan.get("status") != "implemented_in_seed":
        failures.append("plan status must remain implemented_in_seed")
    if plan.get("batch_id") != builder.BATCH_ID or plan.get("priority") != 5:
        failures.append("priority batch identity drifted")
    decision = plan.get("decision", {})
    if decision.get("replace_exactly_9_outputs") != list(builder.BATCH_OUTPUTS):
        failures.append("exact batch output order drifted")
    if decision.get("all_targets_remain_phase") != "High-Energy Grid":
        failures.append("target phase decision drifted")
    if decision.get("first_me_network_remains_phase") != "Digital Logistics":
        failures.append("first ME network phase decision drifted")
    if decision.get("forbid_generic_gate_rings") is not True:
        failures.append("generic gate-ring prohibition was removed")
    if decision.get("shared_files_modified") is not True:
        failures.append("implemented shared-file state was lost")
    implementation = plan.get("implementation", {})
    expected_implementation = {
        "status": "source_owned",
        "authoritative_source": "progression/managed_recipe_overhaul.seed.json",
        "source_recipe_count": 9,
        "source_recipe_ids": [recipe["id"] for recipe in plan.get("replacement_contracts", [])],
        "preserved_stock_recipe_count": 11,
        "exact_stock_recipe_removals": 9,
        "automatic_owners_retired_on_rebuild": 9,
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
        ("digital predecessor", builder.DIGITAL_PREDECESSOR, "digital_predecessor_sha256"),
    ):
        if scope.get(key) != digest_path(path):
            failures.append(f"{label} base hash changed")
    if scope.get("seed_sha256") != builder.AE2_IMPLEMENTATION_SEED_SHA256:
        failures.append("AE2 implementation seed checkpoint changed")
    jar_hashes = scope.get("installed_jar_sha256", {})
    for name, expected in jar_hashes.items() if isinstance(jar_hashes, dict) else []:
        jar = mods / name
        if not jar.is_file() or digest_path(jar) != expected:
            failures.append(f"installed JAR hash changed: {name}")

    auto_batch = next(
        entry
        for entry in load_json(builder.AUTOMATIC_AUDIT).get("implementation_batches", [])
        if entry.get("id") == builder.BATCH_ID
    )
    expected_auto_contract = {
        key: auto_batch.get(key)
        for key in (
            "outputs",
            "prerequisite_outputs",
            "recommended_environments",
            "cycle_risks",
            "managed_ids",
            "installed_recipe_ids",
        )
    }
    if plan.get("automatic_audit_contract") != expected_auto_contract:
        failures.append("automatic quality-audit batch contract drifted")

    preserved = validate_source_evidence(plan, catalog, mods, failures)
    by_output = validate_contracts(plan, catalog, failures)
    validate_dependencies(plan, by_output, failures)
    validate_prerequisites(plan, seed, predecessor, failures)
    validate_assignments(plan, seed, assignments, failures)
    validate_current_state(plan, seed, current, failures)
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
        load_json(builder.CURRENT_MANAGED),
        load_json(builder.DIGITAL_PREDECESSOR),
        check_determinism=True,
        markdown_text=args.markdown.read_text(encoding="utf-8"),
    )
    if failures:
        print("AE2 high-energy/spatial/MEGA audit FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("AE2 high-energy/spatial/MEGA audit passed.")
    print("- 9 exact TFMG-first replacement contracts")
    print("- 9 exact installed recipe removals; no alternate producer/acquisition bypass")
    print("- 11 bulk cable and MEGA closure recipes intentionally preserved")
    print("- Copper/Brass/Industrial-Iron routing and physical spatial dependency order verified")
    print("- deterministic regeneration and authoritative seed ownership verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
