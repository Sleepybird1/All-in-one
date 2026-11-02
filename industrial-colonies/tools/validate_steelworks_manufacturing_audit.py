#!/usr/bin/env python3
"""Validate the source-owned TFMG Steelworks manufacturing implementation.

This validator proves the installed TFMG source recipes and runtime resources,
the retired automatic owners, the Steel Age/Blast Furnace topology, and the
bootstrap safety of the implemented seven-contract repair. It does not mutate the
authoritative seed, generated recipes, quests, deployment, or the live pack.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import zipfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Mapping

import generate_managed_recipe_overhaul as generator


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "STEELWORKS_MANUFACTURING_AUDIT.plan.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
BRANCH_LAYOUT = PROJECT / "progression/minecolonies_branch_layout.json"
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_MANIFEST = PROJECT / "progression/managed_recipe_overhaul.json"
ENVIRONMENTS = PROJECT / "src/main/resources/data/industrial_colonies/tier_recipe_environments.json"

RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^#[a-z0-9_.-]+:[a-z0-9_./-]+$")
COUNTED_REF = re.compile(r"^(?:(\d+)x\s+)?(.+)$")
AUTO_OWNER_IDS = {
    "industrial_colonies:auto/tfmg/coke_oven",
    "industrial_colonies:auto/tfmg/blast_stove",
    "industrial_colonies:auto/tfmg/blast_furnace_hatch",
    "industrial_colonies:auto/tfmg/blast_furnace_output",
    "industrial_colonies:auto/tfmg/blast_furnace_reinforcement",
}
ASSIGNMENT_PREFIX = [
    "tfmg:blast_stove",
    "tfmg:blast_furnace_reinforcement",
    "tfmg:blast_furnace_hatch",
    "tfmg:blast_furnace_output",
    "tfmg:steel_ingot",
    "tfmg:steel_casing",
    "tfmg:steel_mechanism",
]
ASSIGNMENT_ADDITIONS = [
    "tfmg:fireproof_bricks",
    "tfmg:fireproof_brick_reinforcement",
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


def raw_recipe_result(document: dict[str, Any]) -> tuple[str, int]:
    result = document.get("result")
    if not isinstance(result, dict) or not isinstance(result.get("id"), str):
        raise ValueError("audited crafting recipe does not have one object result")
    count = result.get("count", 1)
    if not isinstance(count, int) or count < 1:
        raise ValueError("audited crafting recipe has an invalid result count")
    return result["id"], count


def managed_output(recipe: dict[str, Any]) -> tuple[str, int]:
    output = recipe.get("output")
    if isinstance(output, str):
        return split_ref(output)[1], split_ref(output)[0]
    if isinstance(output, dict) and isinstance(output.get("id"), str):
        count = output.get("count", 1)
        return output["id"], count if isinstance(count, int) else 1
    raise ValueError(f"{recipe.get('id')}: unsupported managed output")


def seed_spec(contract: Mapping[str, Any]) -> dict[str, Any]:
    spec: dict[str, Any] = {
        "id": contract["id"],
        "node": contract["node"],
        "phase": contract["phase"],
        "order": contract["batch_order"],
        "type": contract["type"],
        "comment": contract["comment"],
        "output": contract["output"],
        "remove": contract["remove_exact"],
        "exclusive_output": contract["exclusive_output"],
        "depends_on": contract.get("depends_on_batch", []),
    }
    for field in ("pattern", "key", "machine", "inputs"):
        if field in contract:
            spec[field] = contract[field]
    return spec


def compile_card(contract: Mapping[str, Any]) -> dict[str, Any]:
    spec = seed_spec(contract)
    uid = generator.stable_uid("recipe", str(spec["id"]))
    if spec["type"] == "mechanical_crafting":
        return generator.shaped(spec, uid, True)
    return generator.process(spec, uid)


def recipes_by_id(document: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(recipe["id"]): recipe
        for recipe in document.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def contract_refs(contract: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for index, value in enumerate(contract.get("inputs", [])):
        yield f"inputs[{index}]", str(value)
    for symbol, value in contract.get("key", {}).items():
        yield f"key.{symbol}", str(value)
    if contract.get("machine"):
        yield "machine", str(contract["machine"])


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


def validate_pattern(contract: dict[str, Any], failures: list[str]) -> None:
    pattern = contract.get("pattern")
    identity = str(contract.get("id", ""))
    if contract.get("type") != "mechanical_crafting":
        if pattern is not None:
            failures.append(f"{identity}: only mechanical crafting may declare a pattern")
        return
    if not isinstance(pattern, list) or len(pattern) != 5 or not all(isinstance(row, str) for row in pattern):
        failures.append(f"{identity}: steelworks mechanical crafting must use five string rows")
        return
    if {len(row) for row in pattern} != {5}:
        failures.append(f"{identity}: steelworks mechanical crafting must be an exact 5x5 layout")
    used = {symbol for row in pattern for symbol in row if symbol != " "}
    keys = set(contract.get("key", {}))
    if used != keys:
        failures.append(
            f"{identity}: pattern/key mismatch, missing={sorted(used - keys)}, unused={sorted(keys - used)}"
        )


def find_tfmg_jar(mods: Path) -> Path:
    matches = sorted(mods.glob("tfmg-*.jar"))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one TFMG JAR in {mods}, found {len(matches)}")
    return matches[0]


def find_branch_node(layout: dict[str, Any], branch_id: str, label: str) -> dict[str, Any] | None:
    for branch in layout.get("branches", []):
        if branch.get("id") != branch_id:
            continue
        for node in branch.get("nodes", []):
            if node.get("label") == label:
                return node
    return None


def validate_installed_evidence(
    plan: dict[str, Any], catalog: Path, mods: Path, failures: list[str]
) -> tuple[set[str], set[str]]:
    scope = plan.get("scope", {})
    source_recipes = plan.get("source_recipes", [])
    recipe_rows = load_rows(catalog / "recipes.csv")
    catalog_by_id = {row["recipe_id"]: row for row in recipe_rows}
    jar = find_tfmg_jar(mods)
    jar_hash = hashlib.sha256(jar.read_bytes()).hexdigest().upper()
    if jar.name != scope.get("installed_mod"):
        failures.append(f"installed TFMG JAR changed: {jar.name}")
    if jar_hash != scope.get("installed_mod_sha256"):
        failures.append(f"installed TFMG JAR hash changed: {jar_hash}")

    source_ids: set[str] = set()
    source_outputs: set[str] = set()
    with zipfile.ZipFile(jar) as archive:
        names = set(archive.namelist())
        for source in source_recipes:
            identity = str(source.get("id", ""))
            path = str(source.get("path", ""))
            output = str(source.get("output", ""))
            source_ids.add(identity)
            source_outputs.add(output)
            row = catalog_by_id.get(identity)
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
        for evidence in runtime.get("classes", []):
            path = str(evidence.get("path", ""))
            if path not in names:
                failures.append(f"runtime class is absent from installed TFMG JAR: {path}")
                continue
            digest = hashlib.sha256(archive.read(path)).hexdigest().upper()
            if digest != evidence.get("sha256"):
                failures.append(f"runtime class hash changed: {path} -> {digest}")

        for evidence in runtime.get("static_resources", []):
            path = str(evidence.get("path", ""))
            if path not in names:
                failures.append(f"runtime static resource is absent from installed TFMG JAR: {path}")
                continue
            raw = archive.read(path)
            digest = hashlib.sha256(raw).hexdigest().upper()
            if digest != evidence.get("sha256"):
                failures.append(f"runtime static-resource hash changed: {path} -> {digest}")
            contains_item = evidence.get("contains_item")
            if contains_item and str(contains_item).encode("utf-8") not in raw:
                failures.append(f"runtime static resource no longer contains {contains_item}: {path}")

        tag_evidence = runtime.get("block_tags", []) + runtime.get("process_tags", [])
        for evidence in tag_evidence:
            path = str(evidence.get("path", ""))
            if path not in names:
                failures.append(f"runtime block tag is absent from installed TFMG JAR: {path}")
                continue
            raw = archive.read(path)
            digest = hashlib.sha256(raw).hexdigest().upper()
            if digest != evidence.get("sha256"):
                failures.append(f"runtime block-tag hash changed: {path} -> {digest}")
            document = json.loads(raw)
            if document.get("values") != evidence.get("values"):
                failures.append(f"runtime block-tag values changed: {path}")

    retained_ids: set[str] = set()
    for process in plan.get("runtime_evidence", {}).get("retained_processes", []):
        identity = str(process.get("id", ""))
        retained_ids.add(identity)
        row = catalog_by_id.get(identity)
        if row is None:
            failures.append(f"retained process is absent from catalog: {identity}")
            continue
        path = str(process.get("path", ""))
        if row.get("source_path") != path or row.get("recipe_type") != process.get("type"):
            failures.append(f"{identity}: retained process catalog path/type drifted")
        source_jar = mods / row.get("source_jar", "")
        if not source_jar.is_file():
            failures.append(f"{identity}: retained process source JAR is absent: {source_jar.name}")
            continue
        with zipfile.ZipFile(source_jar) as archive:
            try:
                raw = archive.read(path)
            except KeyError:
                failures.append(f"{identity}: retained process path is absent from {source_jar.name}")
                continue
        digest = hashlib.sha256(raw).hexdigest().upper()
        if digest != process.get("sha256"):
            failures.append(f"{identity}: retained process JSON hash changed: {digest}")
        document = json.loads(raw)
        if document.get("type") != process.get("type"):
            failures.append(f"{identity}: retained process type changed")

    return source_ids, source_outputs


def validate_topology(
    plan: dict[str, Any], seed: Mapping[str, Any], failures: list[str]
) -> None:
    topology = plan.get("node_topology", {})
    branch_id = str(topology.get("branch", ""))
    steel = topology.get("steel_age", {})
    blast = topology.get("blast_furnace", {})
    layout = load_json(BRANCH_LAYOUT)
    steel_node = find_branch_node(layout, branch_id, str(steel.get("label", "")))
    blast_node = find_branch_node(layout, branch_id, str(blast.get("label", "")))
    if steel_node is None or steel_node.get("parent") is not None:
        failures.append("Steel Age topology drifted from the root of steel_and_metallurgy")
    if blast_node is None or blast_node.get("parent") != steel.get("label"):
        failures.append("Blast Furnace topology is no longer a direct Steel Age child")
    phase_by_node = seed.get("phase_by_node", {})
    for node in (steel, blast):
        label = str(node.get("label", ""))
        if phase_by_node.get(label) != node.get("phase"):
            failures.append(f"phase mapping drifted for {label}")


def validate_implementation_owners(
    plan: dict[str, Any], seed: Mapping[str, Any], manifest: Mapping[str, Any],
    failures: list[str],
) -> None:
    contracts = [row for row in plan.get("replacement_contracts", []) if isinstance(row, dict)]
    seed_recipes = recipes_by_id(seed)
    manifest_recipes = recipes_by_id(manifest)
    explicit_ids = {str(contract.get("id", "")) for contract in contracts}
    expected_outputs = {split_ref(str(contract.get("output", "")))[1] for contract in contracts}

    snapshot = [row for row in plan.get("current_managed_owners", []) if isinstance(row, dict)]
    snapshot_ids = {str(row.get("managed_id", "")) for row in snapshot}
    if len(snapshot) != 5 or snapshot_ids != AUTO_OWNER_IDS:
        failures.append("the five retired automatic-owner evidence rows changed")
    for row in snapshot:
        output = str(row.get("output", ""))
        matching = [contract for contract in contracts if split_ref(str(contract.get("output", "")))[1] == output]
        if len(matching) != 1:
            failures.append(f"retired automatic owner output is not represented exactly once: {output}")
            continue
        contract = matching[0]
        if split_ref(str(contract["output"]))[0] != row.get("output_count"):
            failures.append(f"{row.get('managed_id')}: retired automatic output/count evidence drifted")
        if contract.get("remove_exact") != row.get("remove_exact"):
            failures.append(f"{row.get('managed_id')}: retired automatic exact-removal evidence drifted")

    leaked_seed = AUTO_OWNER_IDS & set(seed_recipes)
    leaked_manifest = AUTO_OWNER_IDS & set(manifest_recipes)
    if leaked_seed:
        failures.append(f"retired Steelworks automatic owner leaked into seed: {sorted(leaked_seed)}")
    if leaked_manifest:
        failures.append(f"retired Steelworks automatic owner survived assembled manifest: {sorted(leaked_manifest)}")

    seed_owners: dict[str, list[str]] = {}
    manifest_owners: dict[str, list[str]] = {}
    for identity, recipe in seed_recipes.items():
        try:
            output, _ = managed_output(recipe)
        except ValueError:
            continue
        if output in expected_outputs:
            seed_owners.setdefault(output, []).append(identity)
    for identity, recipe in manifest_recipes.items():
        try:
            output, _ = managed_output(recipe)
        except ValueError:
            continue
        if output in expected_outputs:
            manifest_owners.setdefault(output, []).append(identity)

    for contract in contracts:
        identity = str(contract["id"])
        output_count, output = split_ref(str(contract["output"]))
        expected = seed_spec(contract)
        actual = seed_recipes.get(identity)
        if actual is None:
            failures.append(f"implemented Steelworks recipe is absent from authoritative seed: {identity}")
        elif actual != expected:
            differing = sorted(
                field for field in set(actual) | set(expected)
                if actual.get(field) != expected.get(field)
            )
            failures.append(f"{identity}: authoritative seed differs from reviewed contract in {differing}")
        if seed_owners.get(output) != [identity]:
            failures.append(f"{identity}: Steelworks output does not have one seed owner; owners={seed_owners.get(output, [])}")
        if manifest_owners.get(output) != [identity]:
            failures.append(f"{identity}: Steelworks output does not have one assembled owner; owners={manifest_owners.get(output, [])}")
        assembled = manifest_recipes.get(identity)
        if assembled is None:
            failures.append(f"implemented Steelworks recipe is absent from assembled manifest: {identity}")
        else:
            assembled_output, assembled_count = managed_output(assembled)
            if (assembled_output, assembled_count) != (output, output_count):
                failures.append(f"{identity}: assembled output identity/count changed")
        try:
            card = compile_card(contract)
        except (KeyError, TypeError, ValueError) as error:
            failures.append(f"{identity}: KJSGen compiler rejected reviewed contract: {error}")
        else:
            card_output = card.get("slots", {}).get("output", {})
            if card_output.get("id") != output or int(card_output.get("count", 1)) != output_count:
                failures.append(f"{identity}: KJSGen changed output identity/count")
            if contract.get("type") == "mechanical_crafting":
                if card.get("type") != "kjsgen:create_mechanical_crafting" or card.get("params") != {"gridW": "5", "gridH": "5"}:
                    failures.append(f"{identity}: KJSGen did not emit exact 5x5 Mechanical Crafting")
            else:
                machine = card.get("slots", {}).get("__machine_process_compacting", {}).get("id")
                if card.get("type") != "kjsgen:create_compacting" or machine != contract.get("machine"):
                    failures.append(f"{identity}: KJSGen lost exact Brass Press binding")

    implementation = plan.get("seed_implementation", {})
    if (
        implementation.get("status") != "source_owned"
        or implementation.get("authoritative_source") != "progression/managed_recipe_overhaul.seed.json"
        or implementation.get("recipe_count") != 7
        or implementation.get("exact_stock_removals") != 7
        or implementation.get("exclusive_output_owners") != 7
        or set(implementation.get("replaced_auto_owner_ids", [])) != AUTO_OWNER_IDS
    ):
        failures.append("Steelworks seed_implementation metadata is incomplete or stale")
    if explicit_ids != {f"industrial_colonies:steelworks/{name}" for name in (
        "coke_oven", "fireproof_bricks", "fireproof_brick_reinforcement",
        "blast_stove", "blast_furnace_hatch", "blast_furnace_output",
        "blast_furnace_reinforcement",
    )}:
        failures.append("implemented Steelworks source-owner ID set changed")


def validate_assignments(
    plan: dict[str, Any], document: Mapping[str, Any], failures: list[str]
) -> None:
    assignments = document.get("nodes", document)
    steel_unlocks = set(assignments.get("CR01 — The Steel Age", {}).get("unlocks", []))
    blast_unlocks = assignments.get("CR01 — Blast Furnace", {}).get("unlocks", [])
    if "tfmg:coke_oven" not in steel_unlocks:
        failures.append("coke oven is no longer assigned to The Steel Age")
    expected_unlocks = ASSIGNMENT_PREFIX + ASSIGNMENT_ADDITIONS
    if blast_unlocks != expected_unlocks:
        failures.append("Blast Furnace assignments must preserve the seven existing entries and append the two structural additions in order")
    evidence_additions = {
        str(entry.get("output", ""))
        for entry in plan.get("currently_unmanaged_required_outputs", [])
        if entry.get("required_assignment_node") == "CR01 — Blast Furnace"
    }
    if evidence_additions != set(ASSIGNMENT_ADDITIONS):
        failures.append("audited Blast Furnace assignment additions are not the two proven regular structures")
    if plan.get("assignment_existing_prefix") != ASSIGNMENT_PREFIX:
        failures.append("recorded Blast Furnace assignment prefix changed")
    if plan.get("assignment_additions") != ASSIGNMENT_ADDITIONS:
        failures.append("recorded Blast Furnace assignment additions changed")
    implementation = plan.get("assignment_implementation", {})
    if (
        implementation.get("status") != "appended_without_reordering"
        or implementation.get("authoritative_source") != "progression/machine_node_assignments.json"
        or implementation.get("node") != "CR01 — Blast Furnace"
        or implementation.get("existing_prefix_count") != len(ASSIGNMENT_PREFIX)
        or implementation.get("appended_count") != len(ASSIGNMENT_ADDITIONS)
    ):
        failures.append("Steelworks assignment_implementation metadata is incomplete or stale")


def validate_contracts(
    plan: dict[str, Any], catalog: Path, source_ids: set[str], source_outputs: set[str], failures: list[str]
) -> None:
    contracts = plan.get("replacement_contracts", [])
    if len(contracts) != 7:
        failures.append("steelworks repair must contain exactly seven replacement contracts")
        return
    items = {row["item_id"] for row in load_rows(catalog / "items.csv")}
    environments = collect_environment_items(load_json(ENVIRONMENTS))
    approved_machines = set(plan.get("approved_machine_environments", []))
    ingredient_policy = plan.get("ingredient_policy", {})
    approved_concrete = set(ingredient_policy.get("presteel_foundations", []))
    approved_tags = set(ingredient_policy.get("presteel_tags", []))
    poststeel = set(ingredient_policy.get("post_first_steel_only", []))
    forbidden_fragments = tuple(str(value) for value in ingredient_policy.get("forbidden_bootstrap_fragments", []))

    ids: set[str] = set()
    output_to_contract: dict[str, str] = {}
    output_counts: dict[str, int] = {}
    order_by_id: dict[str, int] = {}
    source_count_by_output = {
        str(source.get("output")): int(source.get("output_count", 1))
        for source in plan.get("source_recipes", [])
    }
    previous_order = -1
    for contract in contracts:
        identity = str(contract.get("id", ""))
        if not RESOURCE_ID.fullmatch(identity) or not identity.startswith("industrial_colonies:steelworks/"):
            failures.append(f"invalid steelworks replacement ID: {identity!r}")
        if identity in ids:
            failures.append(f"duplicate steelworks replacement ID: {identity}")
        ids.add(identity)
        order = contract.get("batch_order")
        if not isinstance(order, int) or order <= previous_order:
            failures.append(f"{identity}: batch_order must be strictly increasing")
        else:
            order_by_id[identity] = order
            previous_order = order
        try:
            output_count, output = split_ref(str(contract.get("output", "")))
        except ValueError as error:
            failures.append(f"{identity}: {error}")
            continue
        if output in output_to_contract:
            failures.append(f"duplicate steelworks output owner: {output}")
        output_to_contract[output] = identity
        output_counts[output] = output_count
        if output not in items:
            failures.append(f"{identity}: output is absent from items.csv: {output}")
        if output_count != source_count_by_output.get(output):
            failures.append(f"{identity}: stock batch output count is not preserved")
        removals = contract.get("remove_exact", [])
        if len(removals) != 1 or removals[0] not in source_ids:
            failures.append(f"{identity}: must retire exactly its one audited source recipe")
        if contract.get("exclusive_output") is not True:
            failures.append(f"{identity}: replacement output ownership must be exclusive")
        if contract.get("phase") != "Steel & Petroleum":
            failures.append(f"{identity}: phase must remain Steel & Petroleum")
        validate_pattern(contract, failures)

    if set(output_to_contract) != source_outputs:
        failures.append("the seven installed source outputs and replacement outputs are not one-to-one")
    actual_removals = {value for contract in contracts for value in contract.get("remove_exact", [])}
    if actual_removals != source_ids or len(actual_removals) != 7:
        failures.append("the seven exact installed source removals are incomplete or broadened")

    required_ids: set[str] = set()
    optional_ids: set[str] = set()
    for contract in contracts:
        identity = str(contract.get("id", ""))
        role = contract.get("bootstrap_role")
        if role == "required":
            required_ids.add(identity)
        elif role == "post_first_steel_optional_upgrade":
            optional_ids.add(identity)
        else:
            failures.append(f"{identity}: unknown bootstrap role {role!r}")

        declared = set(contract.get("depends_on_batch", []))
        observed: set[str] = set()
        for field, raw_ref in contract_refs(contract):
            try:
                count, ref = split_ref(raw_ref)
            except ValueError as error:
                failures.append(f"{identity}: {error}")
                continue
            if count > 1 and ref.startswith("#"):
                failures.append(f"{identity}: counted tag syntax is not supported; repeat tag slots")
            if field == "machine":
                if ref not in approved_machines:
                    failures.append(f"{identity}: unapproved machine environment: {ref}")
                if ref not in environments or ref not in items:
                    failures.append(f"{identity}: machine environment is not concrete: {ref}")
                continue
            if ref.startswith("#"):
                if not TAG_ID.fullmatch(ref) or ref not in approved_tags | poststeel:
                    failures.append(f"{identity}: ingredient tag is outside the approved steelworks set: {ref}")
            else:
                if not RESOURCE_ID.fullmatch(ref) or ref not in items:
                    failures.append(f"{identity}: concrete ingredient is absent/invalid in {field}: {ref}")
                if ref not in approved_concrete | set(output_to_contract) | poststeel:
                    failures.append(f"{identity}: ingredient is outside the approved steelworks set: {ref}")
            if ref in output_to_contract:
                dependency = output_to_contract[ref]
                observed.add(dependency)
                if order_by_id.get(dependency, sys.maxsize) >= order_by_id.get(identity, -1):
                    failures.append(f"{identity}: same-batch dependency is not earlier: {dependency}")
            if role == "required" and any(fragment in ref for fragment in forbidden_fragments):
                failures.append(f"{identity}: bootstrap-required contract consumes forbidden steel input: {ref}")
            if role == "post_first_steel_optional_upgrade" and ref in poststeel:
                pass
        if declared != observed:
            failures.append(
                f"{identity}: depends_on_batch mismatch, observed={sorted(observed)}, declared={sorted(declared)}"
            )
        for dependency in declared:
            if dependency not in ids:
                failures.append(f"{identity}: unknown same-batch dependency: {dependency}")

        if contract.get("type") == "compacting":
            if contract.get("machine") != "createcasing:brass_press":
                failures.append(f"{identity}: compacting must use the approved Brass Press line")
            inputs = contract.get("inputs", [])
            if not isinstance(inputs, list) or not 1 <= len(inputs) <= 9:
                failures.append(f"{identity}: compacting must have 1-9 explicit input slots")

    if len(required_ids) != 6 or len(optional_ids) != 1:
        failures.append("steelworks bootstrap split must be six required contracts and one optional upgrade")
    reinforcement_id = "industrial_colonies:steelworks/blast_furnace_reinforcement"
    if optional_ids != {reinforcement_id}:
        failures.append("blast-furnace reinforcement must be the only post-first-steel contract")
    reinforcement = next((value for value in contracts if value.get("id") == reinforcement_id), {})
    if reinforcement.get("requires_capability") != "regular_blast_furnace_operational":
        failures.append("reinforcement upgrade must explicitly require the regular furnace capability")
    used_poststeel = {
        split_ref(ref)[1]
        for field, ref in contract_refs(reinforcement)
        if field != "machine" and split_ref(ref)[1] in poststeel
    }
    if used_poststeel != poststeel:
        failures.append("optional reinforcement must be the sole declared steel/heavy-plate consumer")

    dag = plan.get("capability_dag", {})
    regular = dag.get("regular_blast_furnace_operational", {})
    if set(regular.get("requires_contracts", [])) != required_ids:
        failures.append("regular blast-furnace capability must require exactly the six bootstrap-safe contracts")
    if reinforcement_id in set(regular.get("requires_contracts", [])):
        failures.append("post-first-steel reinforcement leaked into regular furnace bootstrap")
    expected_processes = {
        "tfmg:coking/coal",
        "create:crushing/coal_coke",
        "tfmg:hot_blast/hot_air",
        "tfmg:industrial_blasting/steel",
        "tfmg:casting/steel",
    }
    if set(regular.get("retained_processes", [])) != expected_processes:
        failures.append("regular blast-furnace retained process chain drifted")
    if regular.get("produces") != "tfmg:steel_ingot":
        failures.append("regular blast-furnace capability no longer terminates in TFMG steel")
    upgrade = dag.get("reinforced_blast_furnace_upgrade", {})
    if upgrade.get("requires_capability") != "regular_blast_furnace_operational":
        failures.append("reinforced furnace upgrade no longer follows the regular capability")
    if upgrade.get("requires_contract") != reinforcement_id:
        failures.append("reinforced furnace upgrade contract drifted")


def validate_plan(
    plan: dict[str, Any], catalog: Path, mods: Path,
    seed: Mapping[str, Any], manifest: Mapping[str, Any],
    assignments: Mapping[str, Any],
) -> list[str]:
    failures: list[str] = []
    if plan.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        failures.append("audit status must be implemented_in_seed")
    if plan.get("decision") != "GO_WITH_SEVEN_CONTRACT_REPAIR":
        failures.append("audit decision must remain GO_WITH_SEVEN_CONTRACT_REPAIR")
    scope = plan.get("scope", {})
    if scope.get("source_recipe_count") != 7 or scope.get("replacement_contract_count") != 7:
        failures.append("scope must declare exactly seven source and replacement contracts")
    if scope.get("phase") != "Steel & Petroleum":
        failures.append("steelworks audit phase drifted")

    source_ids, source_outputs = validate_installed_evidence(plan, catalog, mods, failures)
    validate_topology(plan, seed, failures)
    validate_implementation_owners(plan, seed, manifest, failures)
    validate_assignments(plan, assignments, failures)
    validate_contracts(plan, catalog, source_ids, source_outputs, failures)

    result = plan.get("validation_result", {})
    expected_counts = {
        "source_recipes": 7,
        "strictly_required_extra_outputs": 2,
        "replaced_automatic_owners": 5,
        "implemented_contracts": 7,
        "bootstrap_steel_inputs": 0,
        "preserved_batch_outputs": 7,
        "assignment_additions": 2,
    }
    for field, expected in expected_counts.items():
        if result.get(field) != expected:
            failures.append(f"validation_result.{field} must be {expected}")
    if result.get("status") != "passed":
        failures.append("validation result must record the passing focused audit")
    if result.get("mutation_tests") != 18:
        failures.append("validation_result.mutation_tests must record the 18 focused tests")
    isolated_counts = {
        "isolated_manifest_recipes": 334,
        "isolated_automatic_recipes": 177,
        "isolated_compiled_recipe_cards": 402,
        "isolated_exact_removals": 718,
        "managed_dependency_edges": 862,
        "managed_dependency_warnings": 0,
    }
    for field, expected in isolated_counts.items():
        if result.get(field) != expected:
            failures.append(f"validation_result.{field} must be {expected}")
    for field in (
        "physical_progression",
        "early_manufacturing_regression",
        "high_voltage_regression",
        "extreme_transmission_regression",
        "storage_ladder_regression",
        "induction_matrix_regression",
    ):
        if result.get(field) != "passed":
            failures.append(f"validation_result.{field} must record passed")

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = load_json(args.plan)
        seed = load_json(args.seed)
        manifest = load_json(args.manifest)
        assignments = load_json(args.assignments)
        failures = validate_plan(
            plan, args.catalog.resolve(), args.mods.resolve(), seed, manifest, assignments
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if failures:
        print(f"TFMG Steelworks manufacturing audit failed ({len(failures)} issue(s)):")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "TFMG Steelworks manufacturing audit passed: 7 exact installed source recipes, "
        "2 runtime-proven regular structure outputs, 5 retired automatic owners, 7 "
        "acyclic replacement contracts, 6 steel-free bootstrap contracts, 1 optional "
        "post-first-steel reinforcement upgrade, exact seed/manifest ownership, 2 appended "
        "Blast Furnace assignments, and the canonical TFMG coke/hot-blast/industrial-"
        "blasting/casting chain retained."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
