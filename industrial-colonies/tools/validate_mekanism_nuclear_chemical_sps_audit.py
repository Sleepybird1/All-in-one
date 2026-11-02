#!/usr/bin/env python3
"""Validate the read-only Mekanism nuclear chemistry/SPS patch plan."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_mekanism_nuclear_chemical_sps_audit as builder
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
    "mekanism:purification_chamber": "sequenced_assembly",
    "mekanism:chemical_injection_chamber": "sequenced_assembly",
    "mekanism:chemical_dissolution_chamber": "compacting",
    "mekanism:chemical_washer": "compacting",
    "mekanism:chemical_crystallizer": "sequenced_assembly",
    "mekanism:isotopic_centrifuge": "sequenced_assembly",
    "mekanism:radioactive_waste_barrel": "compacting",
    "mekanism:solar_neutron_activator": "sequenced_assembly",
    "mekanism:sps_casing": "compacting",
    "mekanism:sps_port": "sequenced_assembly",
    "mekanism:supercharged_coil": "compacting",
    "mekanism:antiprotonic_nucleosynthesizer": "sequenced_assembly",
}

FAMILY_BY_OUTPUT = {
    "mekanism:purification_chamber": "industrial_iron",
    "mekanism:chemical_injection_chamber": "industrial_iron",
    "mekanism:chemical_dissolution_chamber": "industrial_iron",
    "mekanism:chemical_washer": "industrial_iron",
    "mekanism:chemical_crystallizer": "industrial_iron",
    "mekanism:isotopic_centrifuge": "refined_radiance",
    "mekanism:radioactive_waste_barrel": "industrial_iron",
    "mekanism:solar_neutron_activator": "refined_radiance",
    "mekanism:sps_casing": "refined_radiance",
    "mekanism:sps_port": "refined_radiance",
    "mekanism:supercharged_coil": "refined_radiance",
    "mekanism:antiprotonic_nucleosynthesizer": "refined_radiance",
}

EXPECTED_MEK_DATA_OUTPUTS = {
    "mekanism:chemical_dissolution_chamber",
    "mekanism:chemical_injection_chamber",
    "mekanism:chemical_washer",
    "mekanism:isotopic_centrifuge",
    "mekanism:purification_chamber",
}

EXPECTED_ACTIVE_SENSITIVE_SURVIVORS = {
    "mekanism:pellet_polonium": [
        "mekanism:processing/lategame/polonium_pellet/from_reaction"
    ],
    "mekanism:pellet_antimatter": [
        "allthecompressed:decompress/antimatter_block",
        "mekanism:processing/lategame/antimatter_pellet/from_gas"
    ],
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


def contracts_by_output(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
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


def source_document(
    identity: str,
    rows_by_id: dict[str, dict[str, str]],
    mods: Path,
) -> tuple[dict[str, str], bytes, dict[str, Any]]:
    row = rows_by_id[identity]
    with zipfile.ZipFile(mods / row["source_jar"]) as archive:
        raw = archive.read(row["source_path"])
    return row, raw, json.loads(raw)


@lru_cache(maxsize=4)
def cached_non_recipe_scan(mods_text: str) -> tuple[int, tuple[str, ...]]:
    count, occurrences = builder.scan_non_recipe_occurrences(Path(mods_text))
    return count, tuple(json.dumps(row, sort_keys=True) for row in occurrences)


def validate_source_evidence(
    plan: dict[str, Any],
    catalog: Path,
    mods: Path,
    seed: dict[str, Any],
    failures: list[str],
) -> None:
    rows = load_rows(catalog / "recipes.csv")
    rows_by_id = {row["recipe_id"]: row for row in rows}
    expected_removals = [
        identity
        for output in builder.BATCH_OUTPUTS
        for identity in builder.SOURCE_REMOVALS[output]
    ]
    expected_producers = {
        output: sorted(
            row["recipe_id"]
            for row in rows
            if output in builder.split_refs(row["outputs"])
        )
        for output in builder.BATCH_OUTPUTS
    }
    if plan.get("direct_producer_audit") != expected_producers:
        failures.append("direct target producer coverage drifted")
    for output in builder.BATCH_OUTPUTS:
        if expected_producers[output] != list(builder.SOURCE_REMOVALS[output]):
            failures.append(f"{output}: alternate target producer exists")
        for identity in expected_producers[output]:
            row = rows_by_id[identity]
            if not (mods / row["source_jar"]).is_file():
                failures.append(f"{output}: catalog producer source JAR is not installed")

    sources = plan.get("removed_installed_recipes", [])
    if [row.get("id") for row in sources if isinstance(row, dict)] != expected_removals:
        failures.append("exact twelve target source removals drifted")
    for source in sources:
        if not isinstance(source, dict):
            failures.append("target source evidence contains a non-object")
            continue
        identity = str(source.get("id", ""))
        if identity not in rows_by_id:
            failures.append(f"target source is absent from catalog: {identity}")
            continue
        try:
            row, raw, document = source_document(identity, rows_by_id, mods)
        except (FileNotFoundError, KeyError, zipfile.BadZipFile) as error:
            failures.append(f"{identity}: cannot read active source: {error}")
            continue
        for field in ("recipe_type", "source_jar", "source_path"):
            if source.get(field) != row.get(field):
                failures.append(f"{identity}: source {field} drifted")
        if source.get("source_present") is not True:
            failures.append(f"{identity}: active target source mislabeled absent")
        if source.get("source_sha256") != digest_bytes(raw):
            failures.append(f"{identity}: installed source JSON hash changed")
        if source.get("raw_recipe") != document:
            failures.append(f"{identity}: raw source recipe evidence drifted")
        if source.get("catalog_inputs") != sorted(builder.split_refs(row["inputs"])):
            failures.append(f"{identity}: catalog input evidence drifted")
        if source.get("catalog_outputs") != sorted(builder.split_refs(row["outputs"])):
            failures.append(f"{identity}: catalog output evidence drifted")

    audit = plan.get("chain_bypass_audit", {})
    expected_catalog: dict[str, list[str]] = {}
    expected_active: dict[str, list[str]] = {}
    for output in EXPECTED_ACTIVE_SENSITIVE_SURVIVORS:
        identities = sorted(
            row["recipe_id"]
            for row in rows
            if output in builder.split_refs(row["outputs"])
        )
        expected_catalog[output] = identities
        expected_active[output] = [
            identity
            for identity in identities
            if (mods / rows_by_id[identity]["source_jar"]).is_file()
        ]
    if audit.get("sensitive_catalog_producers") != expected_catalog:
        failures.append("sensitive catalog producer coverage drifted")
    if audit.get("sensitive_active_producers_before_exact_removals") != expected_active:
        failures.append("active sensitive producer coverage drifted")

    candidate_by_id = {
        row.get("id"): row
        for row in audit.get("candidates", [])
        if isinstance(row, dict)
    }
    if list(candidate_by_id) != list(builder.CHAIN_BYPASS_CANDIDATES):
        failures.append("exact bypass candidate evidence drifted")
    expected_active_removals: list[str] = []
    for identity in builder.CHAIN_BYPASS_CANDIDATES:
        evidence = candidate_by_id.get(identity, {})
        row = rows_by_id.get(identity)
        if row is None:
            if evidence.get("catalog_present") is not False:
                failures.append(f"{identity}: absent bypass candidate claims catalog presence")
            if evidence.get("source_present") is not False:
                failures.append(f"{identity}: absent bypass candidate claims installed source")
            if evidence.get("disposition") != "absent_from_catalog_no_patch":
                failures.append(f"{identity}: bypass disposition drifted")
            if any(
                evidence.get(field) is not None
                for field in (
                    "recipe_type",
                    "source_jar",
                    "source_path",
                    "source_sha256",
                    "raw_type",
                    "raw_recipe",
                )
            ):
                failures.append(f"{identity}: absent bypass candidate claims source evidence")
            if evidence.get("catalog_inputs") != [] or evidence.get("catalog_outputs") != []:
                failures.append(f"{identity}: absent bypass candidate claims catalog references")
            continue
        if evidence.get("catalog_present") is not True:
            failures.append(f"{identity}: catalog bypass candidate claims catalog absence")
        present = (mods / row["source_jar"]).is_file()
        if evidence.get("source_present") is not present:
            failures.append(f"{identity}: installed/inactive bypass classification drifted")
        expected_disposition = "exact_remove" if present else "inactive_catalog_only_no_patch"
        if evidence.get("disposition") != expected_disposition:
            failures.append(f"{identity}: bypass disposition drifted")
        if present:
            expected_active_removals.append(identity)
            try:
                _, raw, document = source_document(identity, rows_by_id, mods)
            except (FileNotFoundError, KeyError, zipfile.BadZipFile) as error:
                failures.append(f"{identity}: cannot read active bypass source: {error}")
            else:
                if evidence.get("source_sha256") != digest_bytes(raw):
                    failures.append(f"{identity}: active bypass source hash changed")
                if evidence.get("raw_recipe") != document:
                    failures.append(f"{identity}: active bypass raw recipe evidence drifted")
        elif evidence.get("source_sha256") is not None or evidence.get("raw_recipe") is not None:
            failures.append(f"{identity}: inactive catalog source claims readable source data")
    if audit.get("exact_active_removals") != expected_active_removals:
        failures.append("exact active bypass removal list drifted")
    storage_evidence = audit.get("antimatter_storage_recovery_closure", [])
    if [row.get("id") for row in storage_evidence if isinstance(row, dict)] != list(
        builder.ANTIMATTER_STORAGE_RECOVERY_RECIPES
    ):
        failures.append("antimatter storage recovery closure coverage drifted")
    for evidence in storage_evidence:
        if not isinstance(evidence, dict):
            failures.append("antimatter storage recovery evidence contains a non-object")
            continue
        identity = str(evidence.get("id", ""))
        try:
            row, raw, document = source_document(identity, rows_by_id, mods)
        except (FileNotFoundError, KeyError, zipfile.BadZipFile) as error:
            failures.append(f"{identity}: cannot read antimatter storage recovery source: {error}")
            continue
        if evidence.get("source_present") is not True:
            failures.append(f"{identity}: antimatter storage recovery source mislabeled absent")
        if evidence.get("source_sha256") != digest_bytes(raw):
            failures.append(f"{identity}: antimatter storage recovery source hash changed")
        if evidence.get("raw_recipe") != document:
            failures.append(f"{identity}: antimatter storage recovery raw recipe drifted")
        if evidence.get("catalog_inputs") != sorted(builder.split_refs(row["inputs"])):
            failures.append(f"{identity}: antimatter storage recovery catalog inputs drifted")
        if evidence.get("catalog_outputs") != sorted(builder.split_refs(row["outputs"])):
            failures.append(f"{identity}: antimatter storage recovery catalog outputs drifted")
    storage_by_id = {
        row.get("id"): row.get("raw_recipe", {})
        for row in storage_evidence
        if isinstance(row, dict)
    }
    compress = storage_by_id.get("allthecompressed:compress/antimatter_block", {})
    decompress = storage_by_id.get("allthecompressed:decompress/antimatter_block", {})
    if not (
        compress.get("type") == "minecraft:crafting_shaped"
        and compress.get("pattern") == ["###", "###", "###"]
        and compress.get("key") == {"#": {"item": "mekanism:pellet_antimatter"}}
        and compress.get("result")
        == {"count": 1, "id": "allthecompressed:antimatter_block"}
    ):
        failures.append("antimatter storage compression is not an exact nine-pellet closure")
    if not (
        decompress.get("type") == "minecraft:crafting_shapeless"
        and decompress.get("ingredients")
        == [{"item": "allthecompressed:antimatter_block"}]
        and decompress.get("result") == {"count": 9, "id": "mekanism:pellet_antimatter"}
    ):
        failures.append("antimatter storage recovery is not an exact nine-pellet closure")
    expected_survivors = {
        output: [identity for identity in identities if identity not in expected_active_removals]
        for output, identities in expected_active.items()
    }
    if audit.get("active_survivors_after_exact_removals") != expected_survivors:
        failures.append("post-removal sensitive survivor set drifted")
    if expected_survivors != EXPECTED_ACTIVE_SENSITIVE_SURVIVORS:
        failures.append("active Polonium/Antimatter route is not the intended Mekanism path")

    stock = plan.get("stock_processing_prerequisites", [])
    if [row.get("id") for row in stock if isinstance(row, dict)] != list(
        builder.STOCK_PREREQUISITE_RECIPE_IDS
    ):
        failures.append("stock processing prerequisite coverage drifted")
    for evidence in stock:
        if not isinstance(evidence, dict):
            failures.append("stock prerequisite evidence contains a non-object")
            continue
        identity = str(evidence.get("id", ""))
        try:
            row, raw, document = source_document(identity, rows_by_id, mods)
        except (FileNotFoundError, KeyError, zipfile.BadZipFile) as error:
            failures.append(f"{identity}: cannot read stock prerequisite source: {error}")
            continue
        if evidence.get("source_present") is not True:
            failures.append(f"{identity}: stock prerequisite is mislabeled absent")
        if evidence.get("source_sha256") != digest_bytes(raw):
            failures.append(f"{identity}: stock prerequisite source hash changed")
        if evidence.get("raw_recipe") != document or evidence.get("source_path") != row["source_path"]:
            failures.append(f"{identity}: stock prerequisite evidence drifted")

    seed_recipes = [row for row in seed.get("recipes", []) if isinstance(row, dict)]
    seed_owner_by_output = {builder.output_id(row): row.get("id") for row in seed_recipes}
    downstream_rows = sorted(
        (
            row
            for row in rows
            if builder.split_refs(row["inputs"]).intersection(builder.BATCH_OUTPUTS)
        ),
        key=lambda row: row["recipe_id"],
    )
    downstream = plan.get("downstream_consumer_audit", [])
    if [row.get("id") for row in downstream if isinstance(row, dict)] != [
        row["recipe_id"] for row in downstream_rows
    ]:
        failures.append("downstream consumer coverage drifted")
    for evidence, row in zip(downstream, downstream_rows):
        outputs = sorted(builder.split_refs(row["outputs"]))
        expected_role = (
            "same_batch_replaced"
            if row["recipe_id"] in expected_removals
            else "shared_seed_managed_closure"
            if any(output in seed_owner_by_output for output in outputs)
            else "downstream_not_owned_by_batch"
        )
        if evidence.get("role") != expected_role:
            failures.append(f"{row['recipe_id']}: downstream ownership classification drifted")
        expected_owner = next(
            (seed_owner_by_output[output] for output in outputs if output in seed_owner_by_output),
            None,
        )
        if evidence.get("observed_shared_seed_owner") != expected_owner:
            failures.append(f"{row['recipe_id']}: downstream shared owner evidence drifted")

    count, serialized = cached_non_recipe_scan(str(mods.resolve()))
    occurrences = [json.loads(value) for value in serialized]
    acquisition = plan.get("non_recipe_acquisition_audit", {})
    if plan.get("scope", {}).get("installed_jars_scanned_for_non_recipe_acquisition") != count:
        failures.append("installed JAR acquisition scan coverage drifted")
    if acquisition.get("occurrences") != occurrences:
        failures.append("non-recipe acquisition evidence drifted")
    external = [row for row in occurrences if row.get("role") == "external_acquisition_candidate"]
    if acquisition.get("external_acquisition_candidates") != external:
        failures.append("external acquisition candidate evidence drifted")
    if external:
        failures.append("external target acquisition bypass exists")
    if any(row.get("role") != "self_drop_block_loot" for row in occurrences):
        failures.append("non-recipe target occurrence is not an ordinary self-drop")


def validate_contracts(
    plan: dict[str, Any], catalog: Path, failures: list[str]
) -> dict[str, dict[str, Any]]:
    contracts = plan.get("replacement_contracts", [])
    if not isinstance(contracts, list) or len(contracts) != 12:
        failures.append("batch must contain exactly twelve replacement contracts")
        contracts = contracts if isinstance(contracts, list) else []
    by_output = contracts_by_output(plan)
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
        if recipe.get("phase") != "Nuclear Engineering":
            failures.append(f"{output}: must remain in Nuclear Engineering")
        if recipe.get("type") != EXPECTED_TYPE_BY_OUTPUT.get(output):
            failures.append(f"{output}: manufacturing process type drifted")
        if recipe.get("remove") != list(builder.SOURCE_REMOVALS.get(output, ())):
            failures.append(f"{output}: exact source removal list drifted")
        if recipe.get("exclusive_output") is not True:
            failures.append(f"{output}: replacement lost exclusive direct ownership")
        if "pattern" in recipe or "key" in recipe or recipe.get("type") == "mechanical_crafting":
            failures.append(f"{output}: generic 5x5 gate-ring manufacturing is forbidden")
        if builder.output_id(recipe) != output:
            failures.append(f"{output}: counted output normalization drifted")

        refs = builder.recipe_inputs(recipe)
        normalized = [normalized_ref(value) for value in refs]
        if not any(value.startswith("tfmg:") for value in normalized):
            failures.append(f"{output}: recipe is not TFMG-first")
        acid = set(normalized).intersection(builder.ACID_REFS)
        if acid:
            failures.append(f"{output}: machine construction consumes sulfuric acid {sorted(acid)}")
        for value in refs:
            match = COUNTED_REF.fullmatch(value)
            if not match:
                failures.append(f"{output}: invalid ingredient reference {value!r}")
                continue
            count, ingredient = match.groups()
            if count and ingredient.startswith("#"):
                failures.append(f"{output}: counted tag syntax is forbidden")
            if ingredient.startswith("#"):
                if ingredient not in tag_ids:
                    failures.append(f"{output}: unknown catalog ingredient tag {ingredient}")
            elif ingredient not in item_ids:
                failures.append(f"{output}: unknown catalog ingredient item {ingredient}")

        family = FAMILY_BY_OUTPUT[output]
        if recipe.get("type") == "compacting":
            if recipe.get("machine") != f"createcasing:{family}_press":
                failures.append(f"{output}: unapproved {family} compacting environment")
            if not 6 <= len(recipe.get("inputs", [])) <= 8:
                failures.append(f"{output}: compacting must use 6-8 physical inputs")
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
            if not isinstance(steps, list) or not 5 <= len(steps) <= 6:
                failures.append(f"{output}: sequence must use 5-6 moderate operations")
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

    if by_output.get("mekanism:sps_casing", {}).get("output") != "4x mekanism:sps_casing":
        failures.append("SPS casing must remain a four-segment factory batch")
    if by_output.get("mekanism:radioactive_waste_barrel", {}).get("output") != (
        "2x mekanism:radioactive_waste_barrel"
    ):
        failures.append("radioactive waste barrel must remain a two-vessel batch")
    return by_output


def validate_dependencies(
    plan: dict[str, Any], by_output: dict[str, dict[str, Any]], failures: list[str]
) -> None:
    contracts = [row for row in plan.get("replacement_contracts", []) if isinstance(row, dict)]
    ids = {str(row.get("id")): row for row in contracts}
    graph: dict[str, set[str]] = {identity: set() for identity in ids}
    for identity, recipe in ids.items():
        for dependency in recipe.get("depends_on", []):
            if dependency.startswith("industrial_colonies:mekanism_nuclear/"):
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

    def inputs(output: str) -> set[str]:
        return {normalized_ref(value) for value in builder.recipe_inputs(by_output.get(output, {}))}

    physical_requirements = {
        "mekanism:purification_chamber": {"mekanism:enrichment_chamber", "tfmg:steel_chemical_vat"},
        "mekanism:chemical_injection_chamber": {"mekanism:purification_chamber", "mekanism:basic_chemical_tank"},
        "mekanism:chemical_dissolution_chamber": {"tfmg:steel_chemical_vat", "mekanism:ultimate_control_circuit", "ae2:engineering_processor"},
        "mekanism:chemical_washer": {"mekanism:basic_fluid_tank", "mekanism:basic_chemical_tank", "tfmg:steel_fluid_tank"},
        "mekanism:chemical_crystallizer": {"mekanism:fluorite_gem", "mekanism:ingot_refined_obsidian", "tfmg:steel_chemical_vat"},
        "mekanism:isotopic_centrifuge": {"tfmg:centrifuge", "mekanism:ultimate_control_circuit", "tfmg:transformer"},
        "mekanism:radioactive_waste_barrel": {"tfmg:fireproof_chemical_vat", "mekanism:ingot_lead"},
        "mekanism:solar_neutron_activator": {"mekanism:hdpe_sheet", "tfmg:steel_chemical_vat", "tfmg:transformer"},
        "mekanism:sps_casing": {"mekanism:pellet_polonium", "mekanism:pellet_plutonium", "tfmg:transformer"},
        "mekanism:sps_port": {"mekanism:sps_casing", "mekanism:ultimate_control_circuit", "tfmg:circuit_board"},
        "mekanism:supercharged_coil": {"mekanism:sps_casing", "mekanism:laser", "mekanism:pellet_polonium", "tfmg:capacitor_item"},
        "mekanism:antiprotonic_nucleosynthesizer": {"mekanism:sps_port", "mekanism:supercharged_coil", "mekanism:pellet_antimatter"},
    }
    for output, required in physical_requirements.items():
        missing = required - inputs(output)
        if missing:
            failures.append(f"{output}: physical manufacturing role is missing {sorted(missing)}")

    dependency_requirements = {
        "mekanism:chemical_injection_chamber": {"industrial_colonies:mekanism_nuclear/purification_chamber"},
        "mekanism:chemical_washer": {"industrial_colonies:mekanism_nuclear/chemical_dissolution_chamber"},
        "mekanism:chemical_crystallizer": {"industrial_colonies:mekanism_nuclear/chemical_washer"},
        "mekanism:solar_neutron_activator": {"industrial_colonies:mekanism_nuclear/radioactive_waste_barrel_batch"},
        "mekanism:sps_casing": {
            "industrial_colonies:mekanism_nuclear/solar_neutron_activator",
            "industrial_colonies:mekanism_nuclear/isotopic_centrifuge",
        },
        "mekanism:sps_port": {"industrial_colonies:mekanism_nuclear/sps_casing_batch"},
        "mekanism:supercharged_coil": {"industrial_colonies:mekanism_nuclear/sps_casing_batch"},
        "mekanism:antiprotonic_nucleosynthesizer": {
            "industrial_colonies:mekanism_nuclear/sps_port",
            "industrial_colonies:mekanism_nuclear/supercharged_coil",
        },
    }
    for output, required in dependency_requirements.items():
        actual = set(by_output.get(output, {}).get("depends_on", []))
        if not required.issubset(actual):
            failures.append(f"{output}: forward dependency contract is incomplete")

    order = {output: by_output.get(output, {}).get("order", -1) for output in builder.BATCH_OUTPUTS}
    required_order = (
        "mekanism:purification_chamber",
        "mekanism:chemical_injection_chamber",
        "mekanism:chemical_dissolution_chamber",
        "mekanism:chemical_washer",
        "mekanism:chemical_crystallizer",
        "mekanism:isotopic_centrifuge",
        "mekanism:radioactive_waste_barrel",
        "mekanism:solar_neutron_activator",
        "mekanism:sps_casing",
        "mekanism:sps_port",
        "mekanism:supercharged_coil",
        "mekanism:antiprotonic_nucleosynthesizer",
    )
    if [order[output] for output in required_order] != sorted(order[output] for output in required_order):
        failures.append("chemical/actinide/SPS order is no longer forward")

    for output in (*builder.CHEMICAL_OUTPUTS, *builder.ACTINIDE_OUTPUTS):
        bootstrap = inputs(output).intersection(builder.NUCLEAR_OR_REVERSE_BOOTSTRAP_INPUTS)
        if bootstrap:
            failures.append(f"{output}: pre-SPS construction has nuclear bootstrap inputs {sorted(bootstrap)}")
    casing_forbidden = inputs("mekanism:sps_casing").intersection(
        builder.NUCLEAR_OR_REVERSE_BOOTSTRAP_INPUTS
        - {"mekanism:pellet_polonium", "mekanism:pellet_plutonium"}
    )
    if casing_forbidden:
        failures.append(f"SPS casing consumes a reverse/bootstrap material {sorted(casing_forbidden)}")
    coil_forbidden = inputs("mekanism:supercharged_coil").intersection(
        builder.NUCLEAR_OR_REVERSE_BOOTSTRAP_INPUTS - {"mekanism:pellet_polonium"}
    )
    if coil_forbidden:
        failures.append(f"supercharged coil consumes a reverse/bootstrap material {sorted(coil_forbidden)}")
    anti_forbidden = inputs("mekanism:antiprotonic_nucleosynthesizer").intersection(
        builder.NUCLEAR_OR_REVERSE_BOOTSTRAP_INPUTS - {"mekanism:pellet_antimatter"}
    )
    if anti_forbidden:
        failures.append(f"nucleosynthesizer consumes an unintended nuclear precursor {sorted(anti_forbidden)}")

    slurry_machine_items = {
        "mekanism:chemical_dissolution_chamber",
        "mekanism:chemical_washer",
        "mekanism:chemical_crystallizer",
    }
    for output in slurry_machine_items:
        consumed_other = inputs(output).intersection(slurry_machine_items - {output})
        if consumed_other:
            failures.append(f"{output}: destroys another required slurry-line machine {sorted(consumed_other)}")

    expected_mek_data = set(plan.get("dependency_contract", {}).get("mek_data_outputs_are_fresh_empty", []))
    if expected_mek_data != EXPECTED_MEK_DATA_OUTPUTS:
        failures.append("mek_data fresh-empty state-transfer contract drifted")


def validate_prerequisites(
    plan: dict[str, Any], seed: dict[str, Any], failures: list[str]
) -> None:
    recipes = [row for row in seed.get("recipes", []) if isinstance(row, dict)]
    owner_by_output = {builder.output_id(row): row for row in recipes}
    evidence = plan.get("prerequisite_evidence", [])
    expected_outputs = list(builder.PREREQUISITE_OWNER_IDS)
    if [row.get("output") for row in evidence if isinstance(row, dict)] != expected_outputs:
        failures.append("managed prerequisite evidence coverage drifted")
    phase_order = seed.get("phase_order", [])
    nuclear_index = phase_order.index("Nuclear Engineering") if "Nuclear Engineering" in phase_order else -1
    for row in evidence:
        if not isinstance(row, dict):
            failures.append("managed prerequisite evidence contains a non-object")
            continue
        output = row.get("output")
        owner = owner_by_output.get(output)
        expected_id = builder.PREREQUISITE_OWNER_IDS.get(output)
        if owner is None:
            failures.append(f"required predecessor managed owner is absent: {output}")
            continue
        if owner.get("id") != expected_id or row.get("observed_managed_owner") != expected_id:
            failures.append(f"{output}: prerequisite managed owner drifted")
        if row.get("phase") != owner.get("phase") or row.get("order") != owner.get("order"):
            failures.append(f"{output}: prerequisite phase/order evidence drifted")
        if owner.get("phase") not in phase_order or phase_order.index(owner.get("phase")) > nuclear_index:
            failures.append(f"{output}: prerequisite no longer precedes Nuclear Engineering")


def validate_assignments(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any], failures: list[str]
) -> None:
    expected = []
    for output in builder.BATCH_OUTPUTS:
        expected.append(
            {
                "output": output,
                "required_node": builder.ASSIGNMENT_BY_OUTPUT[output],
                "required_phase": "Nuclear Engineering",
                "current_nodes": builder.find_assignment_nodes(assignments, output),
                "patch_action": "none",
            }
        )
    if plan.get("assignment_contract") != expected:
        failures.append("exact no-edit assignment contract drifted")
    for row in expected:
        output = row["output"]
        if row["current_nodes"] != [row["required_node"]]:
            failures.append(f"{output}: current assignment is not exact and unique")
        if seed.get("phase_by_node", {}).get(row["required_node"]) != "Nuclear Engineering":
            failures.append(f"{output}: assigned node no longer maps to Nuclear Engineering")


def validate_current_state(
    plan: dict[str, Any], seed: dict[str, Any], current: dict[str, Any], failures: list[str]
) -> None:
    seed_by_output: dict[str, list[dict[str, Any]]] = {
        output: [] for output in builder.BATCH_OUTPUTS
    }
    for row in seed.get("recipes", []):
        if not isinstance(row, dict):
            continue
        output = builder.output_id(row)
        if output in seed_by_output:
            seed_by_output[output].append(row)
    contracts = contracts_by_output(plan)
    for output in builder.BATCH_OUTPUTS:
        owners = seed_by_output[output]
        if len(owners) != 1:
            failures.append(f"{output}: authoritative seed must own the output exactly once")
        elif owners[0] != contracts.get(output):
            failures.append(f"{output}: authoritative seed recipe payload drifted")
    current_by_output = {
        builder.output_id(row): row
        for row in current.get("recipes", [])
        if isinstance(row, dict) and builder.output_id(row) in builder.BATCH_OUTPUTS
    }
    expected = []
    for output in builder.BATCH_OUTPUTS:
        row = current_by_output.get(output, {})
        expected.append(
            {
                "output": output,
                "id": row.get("id"),
                "phase": row.get("phase"),
                "type": row.get("type"),
                "remove": row.get("remove", []),
            }
        )
        if row.get("id") != builder.AUTO_OWNERS[output]:
            failures.append(f"{output}: current automatic owner identity drifted")
        if row.get("phase") != "Nuclear Engineering" or row.get("type") != "mechanical_crafting":
            failures.append(f"{output}: current automatic owner phase/type drifted")
        if row.get("remove") != list(builder.SOURCE_REMOVALS[output]):
            failures.append(f"{output}: current automatic owner removal drifted")
    state = plan.get("current_managed_state", {})
    if state.get("replaced_automatic_owners") != expected:
        failures.append("current automatic-owner evidence drifted")
    if state.get("expected_retired_ids_after_rebuild") != [
        builder.AUTO_OWNERS[output] for output in builder.BATCH_OUTPUTS
    ]:
        failures.append("automatic-owner retirement list drifted")


def validate_chemistry_boundary(plan: dict[str, Any], failures: list[str]) -> None:
    boundary = plan.get("canonical_chemistry_boundary", {})
    sulfur = builder.SULFUR_SCRIPT.read_text(encoding="utf-8")
    uranium = builder.URANIUM_SCRIPT.read_text(encoding="utf-8")
    if boundary.get("sulfur_required_tokens") != list(builder.SULFUR_REQUIRED_TOKENS):
        failures.append("sulfur boundary token contract drifted")
    if boundary.get("uranium_required_tokens") != list(builder.URANIUM_REQUIRED_TOKENS):
        failures.append("uranium boundary token contract drifted")
    for token in builder.SULFUR_REQUIRED_TOKENS:
        if token not in sulfur:
            failures.append(f"sulfur canonicalization token missing: {token}")
    for token in builder.URANIUM_REQUIRED_TOKENS:
        if token not in uranium:
            failures.append(f"uranium boundary token missing: {token}")
    if boundary.get("construction_recipe_acid_refs") != []:
        failures.append("machine-construction batch contains sulfuric-acid references")
    expected_route = [
        "industrial_colonies:yellorium_compound",
        "mekanism:raw_uranium",
        "mekanism:dust_uranium",
        "mekanism:ingot_uranium",
        "mekanism:yellow_cake_uranium",
        "mekanism:uranium_oxide",
        "mekanism:uranium_hexafluoride",
        "mekanism:fissile_fuel",
        "mekanism:nuclear_waste",
        "mekanism:polonium",
        "mekanism:pellet_polonium",
        "mekanism:sps_casing",
        "mekanism:sps_port",
        "mekanism:supercharged_coil",
        "mekanism:antimatter",
        "mekanism:pellet_antimatter",
        "mekanism:antiprotonic_nucleosynthesizer",
    ]
    if boundary.get("forward_route") != expected_route:
        failures.append("canonical forward uranium/actinide/SPS route drifted")


def validate_patch(plan: dict[str, Any], patch: dict[str, Any], failures: list[str]) -> None:
    if patch.get("status") != "applied_to_authoritative_seed" or patch.get("batch_id") != builder.BATCH_ID:
        failures.append("patch identity/status drifted")
    if patch.get("base_files") != plan.get("implementation", {}).get("rebased_base_files"):
        failures.append("patch base-file hashes drifted")
    operations = patch.get("seed_operations", [])
    if not operations or operations[0].get("op") != "append_recipe_specs_after_output_ownership_assertion":
        failures.append("patch append operation is absent")
    elif operations[0].get("recipes") != plan.get("replacement_contracts"):
        failures.append("patch recipe payload differs from reviewed contracts")
    expected_bypass = plan.get("chain_bypass_audit", {}).get("exact_active_removals", [])
    expected_operations = 2 if expected_bypass else 1
    if len(operations) != expected_operations:
        failures.append("patch exact-removal operation count drifted")
    if expected_bypass:
        if operations[1] != {
            "op": "union_additional_removals_exact_ids",
            "recipe_ids": expected_bypass,
        }:
            failures.append("patch exact active bypass removal payload drifted")
    if patch.get("assignment_operations") != []:
        failures.append("patch improperly edits assignments")
    preconditions = patch.get("preconditions", {})
    if preconditions.get("exact_outputs") != list(builder.BATCH_OUTPUTS):
        failures.append("patch exact output precondition drifted")
    if preconditions.get("exact_current_auto_owners") != [
        builder.AUTO_OWNERS[output] for output in builder.BATCH_OUTPUTS
    ]:
        failures.append("patch automatic-owner precondition drifted")
    if preconditions.get("exact_installed_bypass_recipe_ids") != expected_bypass:
        failures.append("patch active bypass precondition drifted")
    expected_removals = [
        identity
        for output in builder.BATCH_OUTPUTS
        for identity in builder.SOURCE_REMOVALS[output]
    ] + expected_bypass
    effects = patch.get("expected_rebuild_effects", {})
    if effects.get("remove_exact_installed_recipe_ids") != expected_removals:
        failures.append("patch exact installed removal effect drifted")
    if effects.get("preserve_recipe_ids_added") != []:
        failures.append("patch improperly adds stock preservation")


def validate_plan(
    plan: dict[str, Any],
    patch: dict[str, Any],
    catalog: Path,
    mods: Path,
    seed: dict[str, Any],
    assignments: dict[str, Any],
    current: dict[str, Any],
    *,
    check_determinism: bool = False,
    markdown_text: str | None = None,
) -> list[str]:
    failures: list[str] = []
    if plan.get("status") != "implemented_in_seed":
        failures.append("plan status must remain implemented_in_seed")
    if plan.get("batch_id") != builder.BATCH_ID or plan.get("priority") != 6:
        failures.append("priority batch identity drifted")
    decision = plan.get("decision", {})
    if decision.get("replace_exactly_12_outputs") != list(builder.BATCH_OUTPUTS):
        failures.append("exact twelve-output batch order drifted")
    if decision.get("all_targets_remain_phase") != "Nuclear Engineering":
        failures.append("target phase decision drifted")
    if decision.get("sulfuric_acid_synthesis_owner") != "tfmg:vat_machine_recipe/sulfuric_acid":
        failures.append("sulfuric acid synthesis owner decision drifted")
    if decision.get("approved_acid_phase_bridge") != "industrial_colonies:sulfur/tfmg_acid_rotary_bridge":
        failures.append("approved sulfuric acid bridge decision drifted")
    if decision.get("assignment_changes") != 0 or decision.get("shared_files_modified") is not True:
        failures.append("implemented decision boundary drifted")
    implementation = plan.get("implementation", {})
    expected_implementation = {
        "status": "source_owned",
        "authoritative_source": "progression/managed_recipe_overhaul.seed.json",
        "source_recipe_count": 12,
        "source_recipe_ids": [recipe["id"] for recipe in plan.get("replacement_contracts", [])],
        "exact_stock_recipe_removals": 12 + len(decision.get("exact_chain_bypass_removals", [])),
        "active_bypass_removals": decision.get("exact_chain_bypass_removals", []),
        "automatic_owners_retired_on_rebuild": 12,
        "assignment_changes": 0,
        "authoritative_generated_artifacts": "intentionally_not_regenerated_by_batch_owner",
        "rebased_base_files": builder.REBASED_BASE_FILES,
    }
    if implementation != expected_implementation:
        failures.append("implementation metadata drifted")
    integration = plan.get("integration_boundary", {})
    for key in (
        "generated_output_edit_authorized",
        "quest_edit_authorized",
        "deploy_or_live_edit_authorized",
        "drawio_edit_authorized",
    ):
        if integration.get(key) is not False:
            failures.append(f"integration boundary improperly authorizes {key}")
    if integration.get("seed_edit_applied") is not True:
        failures.append("integration boundary lost the applied seed edit")
    if integration.get("assignment_edit_required") is not False:
        failures.append("assignment edit must remain unnecessary")

    scope = plan.get("scope", {})
    for label, path, key in (
        ("catalog", catalog / "recipes.csv", "catalog_recipes_sha256"),
        ("assignments", builder.ASSIGNMENTS, "assignments_sha256"),
        ("current managed", builder.CURRENT_MANAGED, "current_managed_sha256"),
        ("sulfur canonicalization", builder.SULFUR_SCRIPT, "sulfur_canonicalization_sha256"),
        ("uranium boundary", builder.URANIUM_SCRIPT, "uranium_boundary_sha256"),
        ("chemistry validator", builder.CHEMISTRY_VALIDATOR, "chemistry_validator_sha256"),
    ):
        if scope.get(key) != digest_path(path):
            failures.append(f"{label} base hash changed")
    if scope.get("seed_sha256") != builder.NUCLEAR_IMPLEMENTATION_SEED_SHA256:
        failures.append("nuclear implementation seed checkpoint changed")
    jar_hashes = scope.get("installed_jar_sha256", {})
    for name, expected in jar_hashes.items() if isinstance(jar_hashes, dict) else []:
        jar = mods / name
        if not jar.is_file() or digest_path(jar) != expected:
            failures.append(f"installed JAR hash changed: {name}")

    automatic = load_json(builder.AUTOMATIC_AUDIT)
    batch = next(
        row
        for row in automatic.get("implementation_batches", [])
        if row.get("id") == builder.BATCH_ID
    )
    expected_auto = {
        key: batch.get(key)
        for key in (
            "outputs",
            "prerequisite_outputs",
            "recommended_environments",
            "cycle_risks",
            "managed_ids",
            "installed_recipe_ids",
        )
    }
    if plan.get("automatic_audit_contract") != expected_auto:
        failures.append("automatic quality-audit batch contract drifted")

    validate_source_evidence(plan, catalog, mods, seed, failures)
    by_output = validate_contracts(plan, catalog, failures)
    validate_dependencies(plan, by_output, failures)
    validate_prerequisites(plan, seed, failures)
    validate_assignments(plan, seed, assignments, failures)
    validate_current_state(plan, seed, current, failures)
    validate_chemistry_boundary(plan, failures)
    validate_patch(plan, patch, failures)

    if check_determinism:
        expected_plan, expected_patch, expected_markdown = builder.build_documents(catalog, mods)
        if plan != expected_plan:
            failures.append("plan differs from deterministic builder output")
        if patch != expected_patch:
            failures.append("patch differs from deterministic builder output")
        if markdown_text is not None and markdown_text != expected_markdown:
            failures.append("Markdown differs from deterministic builder output")
    return failures


def run_full_chemistry_validator(mods: Path) -> tuple[bool, str]:
    process = subprocess.run(
        [
            sys.executable,
            str(builder.CHEMISTRY_VALIDATOR),
            str(mods.parent),
            "--project",
            str(PROJECT),
        ],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (process.stdout + process.stderr).strip()
    return process.returncode == 0, output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--skip-full-chemistry-validator", action="store_true")
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
        check_determinism=True,
        markdown_text=args.markdown.read_text(encoding="utf-8"),
    )
    chemistry_output = ""
    if not args.skip_full_chemistry_validator:
        chemistry_ok, chemistry_output = run_full_chemistry_validator(args.mods)
        if not chemistry_ok:
            failures.append("full nuclear chemistry boundary validator failed")
    if failures:
        print("Mekanism nuclear chemistry/SPS audit FAILED:")
        for failure in failures:
            print(f"- {failure}")
        if chemistry_output:
            print(chemistry_output)
        return 1
    print("Mekanism nuclear chemistry/SPS audit passed.")
    print("- 12 exact TFMG-first replacement contracts")
    print("- 12 exact active source removals; inactive/absent bypasses classified")
    print("- All The Compressed antimatter block verified as a lossless storage closure")
    print("- Industrial-Iron chemical line and Refined-Radiance nuclear/SPS line verified")
    print("- Yellorium -> uranium -> actinide -> SPS -> antimatter direction verified")
    print("- deterministic regeneration and authoritative seed ownership verified")
    if chemistry_output:
        print(chemistry_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
