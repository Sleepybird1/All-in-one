#!/usr/bin/env python3
"""Validate the implemented Mekanism pre-nuclear machine redesign.

The proof covers installed source JSON and single-producer evidence, automatic
owner evidence, encased-machine capability, TFMG-first ingredient contracts,
the Enrichment -> PRC dependency, the sulfuric-acid boundary, state-transfer
disclosure, deterministic no-op patch reporting, an in-memory manifest build,
and KJSGen compilation. Shared project authorities are never written by this
validator.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sqlite3
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_managed_recipe_manifest as manifest_builder
import build_mekanism_pre_nuclear_patch_plan as patch_builder


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
DEFAULT_PLAN = PROJECT / "MEKANISM_PRE_NUCLEAR_MACHINE_CHAIN_AUDIT.plan.json"
DEFAULT_AUTOMATIC_PLAN = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
DEFAULT_AUTOMATIC_SNAPSHOT = PROJECT / "build-current-audit/managed.json"
DEFAULT_CATALOG = WORKSPACE / "outputs/recipe-catalog-current/recipe_catalog.sqlite"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
DEFAULT_PHYSICAL_TIERS = PROJECT / "progression/physical_recipe_tiers.json"
DEFAULT_BRANCH_LAYOUT = PROJECT / "progression/minecolonies_branch_layout.json"
GENERATOR = TOOLS / "generate_managed_recipe_overhaul.py"

BATCH_OUTPUTS = [
    "mekanism:chemical_infuser",
    "mekanism:chemical_oxidizer",
    "mekanism:crusher",
    "mekanism:electrolytic_separator",
    "mekanism:enrichment_chamber",
    "mekanism:osmium_compressor",
    "mekanism:precision_sawmill",
    "mekanism:pressurized_reaction_chamber",
]

BATCH_IDS = {
    "industrial_colonies:mekanism_pre_nuclear/chemical_infuser",
    "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer",
    "industrial_colonies:mekanism_pre_nuclear/crusher",
    "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator",
    "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber",
    "industrial_colonies:mekanism_pre_nuclear/osmium_compressor",
    "industrial_colonies:mekanism_pre_nuclear/precision_sawmill",
    "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber",
}

AUTOMATIC_IDS = {
    "industrial_colonies:auto/mekanism/chemical_infuser",
    "industrial_colonies:auto/mekanism/chemical_oxidizer",
    "industrial_colonies:auto/mekanism/crusher",
    "industrial_colonies:auto/mekanism/electrolytic_separator",
    "industrial_colonies:auto/mekanism/enrichment_chamber",
    "industrial_colonies:auto/mekanism/osmium_compressor",
    "industrial_colonies:auto/mekanism/precision_sawmill",
    "industrial_colonies:auto/mekanism/pressurized_reaction_chamber",
}

SOURCE_IDS = set(BATCH_OUTPUTS)
MEK_DATA_SOURCE_IDS = {
    "mekanism:chemical_infuser",
    "mekanism:chemical_oxidizer",
    "mekanism:pressurized_reaction_chamber",
}

EXPECTED_MACHINES = {
    "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber": "createcasing:railway_press",
    "industrial_colonies:mekanism_pre_nuclear/osmium_compressor": "createcasing:railway_press",
    "industrial_colonies:mekanism_pre_nuclear/crusher": "createcasing:railway_press",
    "industrial_colonies:mekanism_pre_nuclear/precision_sawmill": "createcasing:brass_press",
    "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator": "createcasing:copper_press",
    "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer": "createcasing:railway_press",
    "industrial_colonies:mekanism_pre_nuclear/chemical_infuser": "createcasing:railway_press",
    "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber": "createcasing:railway_press",
}

EXPECTED_NODES = {
    "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber": "CR01 — Modular Machinery",
    "industrial_colonies:mekanism_pre_nuclear/osmium_compressor": "CR01 — Modular Machinery",
    "industrial_colonies:mekanism_pre_nuclear/crusher": "CR01 — Reinforced Systems",
    "industrial_colonies:mekanism_pre_nuclear/precision_sawmill": "CR01 — Reinforced Systems",
    "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator": "CR01 — Electrochemical Engineering",
    "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer": "CR01 — Electrochemical Engineering",
    "industrial_colonies:mekanism_pre_nuclear/chemical_infuser": "CR01 — Electrochemical Engineering",
    "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber": "CR01 — Electrochemical Engineering",
}

EXPECTED_ORDERS = {
    "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber": 300,
    "industrial_colonies:mekanism_pre_nuclear/osmium_compressor": 310,
    "industrial_colonies:mekanism_pre_nuclear/crusher": 320,
    "industrial_colonies:mekanism_pre_nuclear/precision_sawmill": 330,
    "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator": 340,
    "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer": 350,
    "industrial_colonies:mekanism_pre_nuclear/chemical_infuser": 360,
    "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber": 380,
}

EXPECTED_REMOVALS = set(BATCH_OUTPUTS)
PRC_ID = "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber"
ENRICHMENT_ID = "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber"

DOWNSTREAM_FORBIDDEN = {
    "mekanism:hdpe_pellet",
    "mekanism:hdpe_sheet",
    "mekanism:hdpe_rod",
    "mekanism:hdpe_stick",
    "mekanism:substrate",
    "mekanism:pressurized_reaction_chamber",
    "mekanism:sulfuric_acid",
    "tfmg:sulfuric_acid",
}

REBASED_SEED_SHA256 = "297CE846E57E8764A32642B3A3846893533477D289556B1297A1A98DABB07106"
UNCHANGED_ASSIGNMENTS_SHA256 = "329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E"

COUNTED_REF = re.compile(r"^(?P<count>[1-9][0-9]*)x (?P<id>.+)$")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def split_ref(value: str) -> tuple[int, str]:
    match = COUNTED_REF.fullmatch(value)
    if match:
        return int(match.group("count")), match.group("id")
    return 1, value


def ingredient_ref(value: Any, label: str) -> str:
    if not isinstance(value, dict):
        raise ValueError(f"{label} ingredient is not an object")
    if isinstance(value.get("item"), str):
        return value["item"]
    if isinstance(value.get("tag"), str):
        return "#" + value["tag"]
    raise ValueError(f"{label} ingredient has no item or tag")


def source_ingredient_counts(raw: dict[str, Any], label: str) -> Counter[str]:
    if raw.get("type") not in {"minecraft:crafting_shaped", "mekanism:mek_data"}:
        raise ValueError(f"{label} is not a supported shaped source recipe")
    pattern = raw.get("pattern")
    key = raw.get("key")
    if not isinstance(pattern, list) or not isinstance(key, dict):
        raise ValueError(f"{label} has invalid shaped data")
    counts: Counter[str] = Counter()
    for row in pattern:
        if not isinstance(row, str):
            raise ValueError(f"{label} has a non-string pattern row")
        for symbol in row:
            if symbol == " ":
                continue
            if symbol not in key:
                raise ValueError(f"{label} references unknown symbol {symbol!r}")
            counts[ingredient_ref(key[symbol], label)] += 1
    return counts


def source_result(raw: dict[str, Any], label: str) -> tuple[str, int]:
    result = raw.get("result")
    if not isinstance(result, dict) or not isinstance(result.get("id"), str):
        raise ValueError(f"{label} has invalid result data")
    count = result.get("count", 1)
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise ValueError(f"{label} has invalid result count")
    if result.get("components") is not None:
        raise ValueError(f"{label} unexpectedly has literal result components")
    return result["id"], count


def input_refs(contract: dict[str, Any]) -> list[str]:
    values = contract.get("inputs")
    if contract.get("type") != "compacting" or not isinstance(values, list):
        raise ValueError(f"{contract.get('id')} must be a compacting recipe with inputs")
    return [split_ref(str(value))[1] for value in values]


def recipe_output_id(recipe: dict[str, Any]) -> str:
    return patch_builder.output_id(recipe)


def contracts_by_id(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return patch_builder.contracts_by_id(plan)


def find_jar(mods: Path, name: str) -> Path:
    candidate = mods / name
    if not candidate.is_file():
        raise ValueError(f"installed JAR is absent: {candidate}")
    return candidate


def validate_installed_evidence(
    plan: dict[str, Any], catalog: Path, mods: Path, failures: list[str]
) -> None:
    scope = plan.get("scope", {})
    if sha256_file(catalog) != scope.get("recipe_catalog_sha256"):
        failures.append("pinned recipe catalog hash changed")

    jars = plan.get("installed_jars")
    if not isinstance(jars, list) or len(jars) != 1:
        failures.append("installed JAR evidence must contain exactly Mekanism")
        return
    evidence = jars[0]
    if evidence.get("name") != "Mekanism-1.21.1-10.7.19.85.jar":
        failures.append("installed Mekanism JAR name changed")
        return
    jar_path = find_jar(mods, evidence["name"])
    if sha256_file(jar_path) != evidence.get("sha256"):
        failures.append("installed Mekanism JAR hash changed")

    rows = plan.get("source_recipes")
    if not isinstance(rows, list) or {row.get("id") for row in rows} != SOURCE_IDS:
        failures.append("source recipe inventory must contain exactly the eight targets")
        return
    with zipfile.ZipFile(jar_path) as archive:
        for row in rows:
            identity = str(row.get("id"))
            path = str(row.get("path"))
            if row.get("jar") != evidence["name"] or path not in archive.namelist():
                failures.append(f"installed source recipe is absent: {identity}")
                continue
            payload = archive.read(path)
            if sha256_bytes(payload) != row.get("sha256"):
                failures.append(f"installed source JSON hash changed: {identity}")
                continue
            raw = json.loads(payload)
            if raw.get("type") != row.get("type"):
                failures.append(f"installed source recipe type changed: {identity}")
            if raw.get("pattern") != row.get("pattern"):
                failures.append(f"installed source pattern changed: {identity}")
            actual_output, actual_count = source_result(raw, identity)
            if actual_output != row.get("output") or actual_count != row.get("output_count"):
                failures.append(f"installed source result changed: {identity}")
            if source_ingredient_counts(raw, identity) != Counter(
                row.get("stock_ingredient_counts", {})
            ):
                failures.append(f"installed source ingredients changed: {identity}")
            expected_transfer = identity in MEK_DATA_SOURCE_IDS
            if row.get("component_transfer") is not expected_transfer:
                failures.append(f"source component-transfer disclosure changed: {identity}")

    required = plan.get("required_concrete_items")
    if not isinstance(required, list) or len(required) != len(set(required)):
        failures.append("required concrete item inventory must be a unique array")
        return
    machines = plan.get("machine_capability_audit", {}).get("approved_exact_machines", [])
    connection = sqlite3.connect(catalog)
    try:
        found = {
            row[0]
            for row in connection.execute(
                f"select item_id from items where item_id in ({','.join('?' for _ in required)})",
                required,
            )
        }
        if found != set(required):
            failures.append(
                f"concrete recipe items are absent from installed catalog: {sorted(set(required) - found)}"
            )
        found_machines = {
            row[0]
            for row in connection.execute(
                f"select item_id from items where item_id in ({','.join('?' for _ in machines)})",
                machines,
            )
        }
        if found_machines != set(machines):
            failures.append("one or more approved exact encased presses are absent")

        producer_rows = connection.execute(
            f"select item_id, recipe_id from item_recipe_map where role='output' "
            f"and item_id in ({','.join('?' for _ in BATCH_OUTPUTS)})",
            BATCH_OUTPUTS,
        ).fetchall()
        producers: dict[str, list[str]] = {output: [] for output in BATCH_OUTPUTS}
        for output, identity in producer_rows:
            producers[output].append(identity)
        wrong = {
            output: identities
            for output, identities in producers.items()
            if identities != [output]
        }
        if wrong:
            failures.append(f"installed single-producer evidence changed: {wrong}")
    finally:
        connection.close()

    route = plan.get("static_route_audit", {})
    if (
        route.get("producer_count_per_output") != 1
        or route.get("alternate_recipe_ids") != []
        or route.get("loot_trade_or_advancement_producers") != []
    ):
        failures.append("static alternate-route disposition changed")


def validate_automatic_evidence(
    plan: dict[str, Any], automatic_plan: dict[str, Any], automatic_plan_path: Path,
    snapshot_path: Path, failures: list[str],
) -> None:
    scope = plan.get("scope", {})
    if sha256_file(automatic_plan_path) != scope.get("automatic_audit_plan_sha256"):
        failures.append("pinned automatic quality-audit plan hash changed")
    if sha256_file(snapshot_path) != scope.get("automatic_snapshot_sha256"):
        failures.append("pinned automatic managed snapshot hash changed")
        return

    batch = next(
        (
            value
            for value in automatic_plan.get("implementation_batches", [])
            if value.get("id") == "mekanism_pre_nuclear_machine_chain"
        ),
        None,
    )
    if batch is None:
        failures.append("priority-three automatic redesign batch is absent")
        return
    if batch.get("priority") != 3 or batch.get("outputs") != BATCH_OUTPUTS:
        failures.append("priority-three automatic redesign output order changed")
    if set(batch.get("managed_ids", [])) != AUTOMATIC_IDS:
        failures.append("priority-three automatic owner set changed")
    risks = set(batch.get("cycle_risks", []))
    expected_risks = {
        "Enrichment chamber must precede the pressurized reaction chamber and purification line.",
        "Do not use HDPE or a product of the PRC to construct the first PRC.",
        "Sulfuric acid remains TFMG chemical-vat-owned; no machine recipe may create a second acid route.",
    }
    if risks != expected_risks:
        failures.append("priority-three cycle and chemistry risks changed")

    current = plan.get("current_automatic_owners")
    if not isinstance(current, list) or {row.get("managed_id") for row in current} != AUTOMATIC_IDS:
        failures.append("current automatic-owner evidence must contain exactly eight ids")
        return
    if {row.get("output") for row in current} != set(BATCH_OUTPUTS):
        failures.append("current automatic-owner output inventory changed")

    snapshot = load_json(snapshot_path)
    recipes = {
        recipe.get("id"): recipe
        for recipe in snapshot.get("recipes", [])
        if recipe.get("id") in AUTOMATIC_IDS
    }
    if set(recipes) != AUTOMATIC_IDS:
        failures.append("pinned snapshot no longer contains all eight automatic owners")
        return
    for row in current:
        recipe = recipes[row["managed_id"]]
        if recipe.get("type") != "mechanical_crafting":
            failures.append(f"automatic owner is no longer mechanical crafting: {row['managed_id']}")
        if recipe_output_id(recipe) != row.get("output"):
            failures.append(f"automatic owner output changed: {row['managed_id']}")
        if row.get("source_recipe_id") not in recipe.get("remove", []):
            failures.append(f"automatic owner exact source evidence changed: {row['managed_id']}")

    entries = {
        entry.get("managed_id"): entry
        for entry in automatic_plan.get("entries", [])
        if entry.get("managed_id") in AUTOMATIC_IDS
    }
    if set(entries) != AUTOMATIC_IDS or not all(
        entry.get("generic_gate_ring") is True
        and entry.get("classification") == "needs_source_owned_redesign"
        for entry in entries.values()
    ):
        failures.append("automatic audit no longer classifies all eight generic owners for redesign")


def validate_capability_and_assignments(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers_path: Path, branch_layout_path: Path, failures: list[str],
) -> None:
    scope = plan.get("scope", {})
    if scope.get("physical_tiers") != "progression/physical_recipe_tiers.json":
        failures.append("physical tier authority path metadata changed")
        return
    if sha256_file(physical_tiers_path) != scope.get("physical_tiers_sha256"):
        failures.append("physical tier authority hash changed")
        return
    if sha256_file(branch_layout_path) != scope.get("branch_layout_sha256"):
        failures.append("branch layout authority hash changed")
        return
    physical = load_json(physical_tiers_path)
    ranks = {tier.get("id"): tier.get("rank") for tier in physical.get("tiers", [])}
    expected_ranks = {"copper": 1, "brass": 2, "railway": 3, "industrial_iron": 4}
    if any(ranks.get(key) != value for key, value in expected_ranks.items()):
        failures.append("physical manufacturing tier ranks changed")
    if plan.get("machine_capability_audit", {}).get("machine_family_ranks") != expected_ranks:
        failures.append("reviewed machine-family ranks changed")

    branch = load_json(branch_layout_path)
    factory = next(
        (value for value in branch.get("branches", []) if value.get("id") == "factory_engineering"),
        None,
    )
    if factory is None:
        failures.append("factory engineering branch is absent")
    else:
        node_by_label = {value.get("label"): value for value in factory.get("nodes", [])}
        if node_by_label.get("CR01 — Reinforced Systems", {}).get("parent") != "CR01 — Modular Machinery":
            failures.append("Reinforced Systems no longer follows Modular Machinery")
        if "CR01 — Electrochemical Engineering" not in node_by_label:
            failures.append("Electrochemical Engineering is absent from the factory branch")

    try:
        patch_builder.validate_assignment_contract(plan, assignments)
    except patch_builder.PatchPlanError as error:
        failures.append(f"assignment order contract failed: {error}")

    phase_by_node = seed.get("phase_by_node", {})
    for node in set(EXPECTED_NODES.values()):
        if phase_by_node.get(node) != "Mekanized Industry":
            failures.append(f"reviewed node phase changed: {node}")

    prerequisite_ids = {
        "industrial_colonies:electronics/capacitor",
        "industrial_colonies:electronics/circuit_board",
        "industrial_colonies:fluid_infrastructure/steel_chemical_vat",
        "industrial_colonies:mechanical/mechanical_pump",
        "industrial_colonies:mekanism/basic_control_circuit",
        "industrial_colonies:tfmg_heavy_electrical/transformer",
    }
    current = patch_builder.recipes_by_id(seed)
    missing = sorted(prerequisite_ids - set(current))
    if missing:
        failures.append(f"explicit prerequisite owners are absent from seed: {missing}")


def require_inputs(
    contract: dict[str, Any], required: set[str], forbidden: set[str], failures: list[str]
) -> None:
    refs = set(input_refs(contract))
    missing = sorted(required - refs)
    present_forbidden = sorted(forbidden & refs)
    if missing:
        failures.append(f"{contract['id']}: missing required manufactured inputs {missing}")
    if present_forbidden:
        failures.append(f"{contract['id']}: contains forbidden downstream inputs {present_forbidden}")


def validate_dependency_dag(contracts: dict[str, dict[str, Any]], failures: list[str]) -> None:
    graph = {
        identity: set(contract.get("depends_on", [])) & set(contracts)
        for identity, contract in contracts.items()
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> None:
        if identity in visiting:
            failures.append(f"same-batch dependency cycle detected at {identity}")
            return
        if identity in visited:
            return
        visiting.add(identity)
        for dependency in graph[identity]:
            visit(dependency)
        visiting.remove(identity)
        visited.add(identity)

    for identity in graph:
        visit(identity)


def validate_contracts(plan: dict[str, Any], failures: list[str]) -> None:
    contracts = contracts_by_id(plan)
    if set(contracts) != BATCH_IDS:
        failures.append("replacement contract id set drifted")
        return
    if {recipe_output_id(value) for value in contracts.values()} != set(BATCH_OUTPUTS):
        failures.append("replacement contract output set drifted")
    if any(contract.get("type") != "compacting" for contract in contracts.values()):
        failures.append("batch must remain eight exact encased compacting recipes")
    machines = {identity: contract.get("machine") for identity, contract in contracts.items()}
    if machines != EXPECTED_MACHINES:
        failures.append("exact encased machine-role mapping changed")
    nodes = {identity: contract.get("node") for identity, contract in contracts.items()}
    if nodes != EXPECTED_NODES:
        failures.append("reviewed node placement changed")
    if {identity: contract.get("order") for identity, contract in contracts.items()} != EXPECTED_ORDERS:
        failures.append("reviewed recipe order changed")
    if any(contract.get("phase") != "Mekanized Industry" for contract in contracts.values()):
        failures.append("one or more contracts left Mekanized Industry")

    removals = [item for value in contracts.values() for item in value.get("remove", [])]
    if len(removals) != 8 or len(removals) != len(set(removals)):
        failures.append("batch must contain eight unique exact source removals")
    if set(removals) != EXPECTED_REMOVALS:
        failures.append("exact source removal set drifted")
    if any(contract.get("exclusive_output") is not True for contract in contracts.values()):
        failures.append("all eight outputs must remain exclusive source-owned contracts")
    if any(contract.get("output_state") != "fresh_empty" for contract in contracts.values()):
        failures.append("fresh-empty output-state contract changed")

    common = {"tfmg:steel_frame", "mekanism:basic_control_circuit", "tfmg:circuit_board"}
    for contract in contracts.values():
        refs = input_refs(contract)
        require_inputs(contract, common, DOWNSTREAM_FORBIDDEN, failures)
        if any(ref.startswith(("ae2:", "bigreactors:")) for ref in refs):
            failures.append(f"{contract['id']}: jumps to a digital or nuclear technology family")
        for value in contract.get("inputs", []):
            count, ref = split_ref(str(value))
            if count > 1 and ref.startswith("#"):
                failures.append(f"{contract['id']}: counted tag syntax is forbidden")
        if recipe_output_id(contract) in refs:
            failures.append(f"{contract['id']}: recipe consumes its own output")

    require_inputs(
        contracts[ENRICHMENT_ID],
        {"create:precision_mechanism", "tfmg:steel_mechanism", "tfmg:heavy_plate", "mekanism:alloy_infused"},
        set(BATCH_OUTPUTS),
        failures,
    )
    require_inputs(
        contracts["industrial_colonies:mekanism_pre_nuclear/osmium_compressor"],
        {"tfmg:steel_chemical_vat", "create:mechanical_pump", "tfmg:transformer", "tfmg:steel_pipe", "tfmg:heavy_plate"},
        {"mekanism:advanced_control_circuit"},
        failures,
    )
    require_inputs(
        contracts["industrial_colonies:mekanism_pre_nuclear/crusher"],
        {"create:crushing_wheel", "tfmg:steel_mechanism", "tfmg:heavy_plate", "mekanism:alloy_infused"},
        set(),
        failures,
    )
    if input_refs(contracts["industrial_colonies:mekanism_pre_nuclear/crusher"]).count("create:crushing_wheel") != 1:
        failures.append("crusher counted-wheel contract changed")
    crusher_raw = contracts["industrial_colonies:mekanism_pre_nuclear/crusher"].get("inputs", [])
    if "2x create:crushing_wheel" not in crusher_raw:
        failures.append("crusher must retain a matched pair of Create crushing wheels")
    require_inputs(
        contracts["industrial_colonies:mekanism_pre_nuclear/precision_sawmill"],
        {"create:mechanical_saw", "create:precision_mechanism", "tfmg:steel_mechanism", "tfmg:heavy_plate"},
        set(),
        failures,
    )
    require_inputs(
        contracts["industrial_colonies:mekanism_pre_nuclear/electrolytic_separator"],
        {"mekanism:electrolytic_core", "tfmg:steel_chemical_vat", "tfmg:copper_electrode", "tfmg:zinc_electrode", "create:mechanical_pump", "tfmg:transformer"},
        set(),
        failures,
    )
    require_inputs(
        contracts["industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer"],
        {"tfmg:steel_chemical_vat", "mekanism:basic_chemical_tank", "create:encased_fan", "create:mechanical_pump", "tfmg:steel_pipe", "tfmg:capacitor_item"},
        set(),
        failures,
    )
    require_inputs(
        contracts["industrial_colonies:mekanism_pre_nuclear/chemical_infuser"],
        {"tfmg:steel_chemical_vat", "mekanism:basic_chemical_tank", "create:mechanical_pump", "tfmg:steel_pipe", "tfmg:transformer"},
        set(),
        failures,
    )
    infuser_inputs = contracts[
        "industrial_colonies:mekanism_pre_nuclear/chemical_infuser"
    ].get("inputs", [])
    for counted in (
        "2x mekanism:basic_chemical_tank",
        "2x create:mechanical_pump",
        "2x tfmg:steel_pipe",
    ):
        if counted not in infuser_inputs:
            failures.append(f"chemical infuser lost its reviewed dual-feed input {counted}")
    require_inputs(
        contracts[PRC_ID],
        {"mekanism:enrichment_chamber", "tfmg:steel_chemical_vat", "mekanism:dynamic_tank", "mekanism:basic_chemical_tank", "create:mechanical_pump", "tfmg:steel_pipe", "tfmg:transformer", "tfmg:heavy_plate"},
        DOWNSTREAM_FORBIDDEN,
        failures,
    )
    prc_inputs = contracts[PRC_ID].get("inputs", [])
    for counted in (
        "2x mekanism:basic_chemical_tank",
        "2x tfmg:steel_pipe",
        "2x tfmg:heavy_plate",
    ):
        if counted not in prc_inputs:
            failures.append(f"PRC lost its reviewed pressure-body input {counted}")

    output_to_id = {recipe_output_id(value): identity for identity, value in contracts.items()}
    for identity, contract in contracts.items():
        observed = {
            output_to_id[ref]
            for ref in input_refs(contract)
            if ref in output_to_id
        }
        declared = set(contract.get("depends_on", [])) & set(contracts)
        if observed != declared:
            failures.append(
                f"{identity}: same-batch dependency mismatch, observed={sorted(observed)}, declared={sorted(declared)}"
            )
    if set(contracts[PRC_ID].get("depends_on", [])) & set(contracts) != {ENRICHMENT_ID}:
        failures.append("PRC must depend on exactly the reviewed Enrichment owner")
    if EXPECTED_ORDERS[ENRICHMENT_ID] >= EXPECTED_ORDERS[PRC_ID]:
        failures.append("Enrichment order is not before PRC")
    validate_dependency_dag(contracts, failures)

    acid_refs = {
        ref
        for contract in contracts.values()
        for ref in input_refs(contract) + [recipe_output_id(contract)]
        if "sulfuric_acid" in ref
    }
    if acid_refs:
        failures.append(f"machine construction crossed the TFMG sulfuric-acid boundary: {sorted(acid_refs)}")

    state = plan.get("state_transfer_policy", {})
    if set(state.get("mek_data_source_ids", [])) != MEK_DATA_SOURCE_IDS:
        failures.append("mek_data state-transfer source inventory changed")
    if (
        state.get("replacement_behavior") != "fresh_empty_output"
        or state.get("required_constituent_state") != "fresh_empty_unupgraded"
    ):
        failures.append("fresh-empty state-transfer limitation is no longer explicit")
    if not contracts[PRC_ID].get("constituent_state_requirement"):
        failures.append("PRC no longer warns that its constituent machines must be fresh and empty")


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("pre_nuclear_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load managed recipe compiler: {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def card_input_refs(card: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for name, slot in card.get("slots", {}).items():
        if not str(name).startswith("in") or not isinstance(slot, dict):
            continue
        identity = slot.get("id")
        if isinstance(identity, str):
            refs.append(identity)
    return refs


def validate_patch_and_compilation(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    catalog: Path, mods: Path, physical_tiers: Path, failures: list[str],
    *, compile_batch: bool,
) -> None:
    try:
        first = patch_builder.build_patch_plan(plan, seed, assignments, physical_tiers)
        second = patch_builder.build_patch_plan(plan, seed, assignments, physical_tiers)
    except patch_builder.PatchPlanError as error:
        failures.append(f"deterministic patch precondition failed: {error}")
        return
    if first != second:
        failures.append("patch-plan builder is nondeterministic")
        return
    if first.get("mode") != "implemented_source_owned_noop":
        failures.append("patch-plan builder does not report the implemented no-op state")
    if first.get("assignments", {}).get("changes") != []:
        failures.append("patch plan unexpectedly mutates assignments")
    if first.get("seed", {}).get("remove_source_recipe_override_outputs") != []:
        failures.append("patch plan unexpectedly mutates source overrides")

    try:
        staged_seed, staged_assignments = patch_builder.apply_patch_to_copies(
            plan, seed, assignments, physical_tiers
        )
    except patch_builder.PatchPlanError as error:
        failures.append(f"in-memory patch application failed: {error}")
        return
    if staged_assignments != assignments:
        failures.append("in-memory patch changed assignments")
    staged_ids = patch_builder.recipes_by_id(staged_seed)
    if not BATCH_IDS <= set(staged_ids):
        failures.append("in-memory seed is missing one or more reviewed contracts")

    if not compile_batch:
        return
    with tempfile.TemporaryDirectory(prefix="mekanism-pre-nuclear-audit-") as temporary:
        root = Path(temporary)
        seed_path = root / "seed.json"
        assignments_path = root / "assignments.json"
        manifest_path = root / "managed.json"
        compiled_path = root / "compiled.json"
        seed_path.write_text(json.dumps(staged_seed, indent=2, ensure_ascii=False), encoding="utf-8")
        assignments_path.write_text(
            json.dumps(staged_assignments, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        try:
            manifest, report = manifest_builder.build_manifest(
                seed_path,
                assignments_path,
                manifest_builder.DEFAULT_DEPENDENCIES,
                catalog.parent,
                mods,
            )
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
            failures.append(f"in-memory managed manifest rejected the batch: {error}")
            return
        if report.get("fatal_errors", []):
            failures.append(f"in-memory managed manifest reported fatal errors: {report['fatal_errors']}")
            return
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        try:
            compiled = load_generator().compile_manifest(manifest_path, compiled_path)
        except (OSError, ValueError, KeyError, TypeError) as error:
            failures.append(f"KJSGen compiler rejected the batch: {error}")
            return

    managed_ids = {value.get("id") for value in manifest.get("recipes", [])}
    if not BATCH_IDS <= managed_ids:
        failures.append("compiled managed manifest lost one or more reviewed owners")
    if AUTOMATIC_IDS & managed_ids:
        failures.append("one or more generic automatic owners survived explicit replacement")
    cards = [value for value in compiled.get("recipes", []) if value.get("recipeId") in BATCH_IDS]
    if len(cards) != 8:
        failures.append(f"compiled batch recipe-card count drifted: {len(cards)}")
        return
    if Counter(value.get("type") for value in cards) != Counter(
        plan["compiled_contract"]["expected_card_type_counts"]
    ):
        failures.append("compiled batch card type counts drifted")
    machines: Counter[str] = Counter()
    for card in cards:
        slot = card.get("slots", {}).get("__machine_process_compacting", {})
        machines[slot.get("id")] += 1
    if machines != Counter(plan["compiled_contract"]["expected_exact_machine_counts"]):
        failures.append(f"compiled exact-machine counts drifted: {dict(machines)}")

    by_id = {value.get("recipeId"): value for value in cards}
    prc_refs = card_input_refs(by_id[PRC_ID])
    if "mekanism:enrichment_chamber" not in prc_refs:
        failures.append("compiled PRC lost its Enrichment predecessor input")
    if DOWNSTREAM_FORBIDDEN & set(prc_refs):
        failures.append("compiled PRC contains an HDPE, PRC-derived, or sulfuric-acid input")
    if any("sulfuric_acid" in ref for card in cards for ref in card_input_refs(card)):
        failures.append("compiled batch creates a sulfuric-acid construction dependency")

    removals = {
        value.get("recipeId")
        for value in compiled.get("removals", [])
        if value.get("recipeId")
    }
    if not EXPECTED_REMOVALS <= removals:
        failures.append("compiled output is missing one or more exact stock removals")


def validate_plan(
    plan: dict[str, Any], automatic_plan: dict[str, Any], automatic_plan_path: Path,
    automatic_snapshot: Path, catalog: Path, mods: Path, seed: dict[str, Any],
    assignments: dict[str, Any], physical_tiers: Path, branch_layout: Path,
    *, compile_batch: bool = True,
) -> list[str]:
    failures: list[str] = []
    if plan.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        failures.append("status must be implemented_in_seed")
    if plan.get("decision") != "GO_WITH_EIGHT_TFMG_FIRST_ENCASED_MACHINE_CONTRACTS":
        failures.append("audit decision changed")
    expected_scope = {
        "outputs": 8,
        "source_owned_contracts": 8,
        "automatic_owners_retired": 8,
        "exact_recipe_removals": 8,
        "assignment_changes": 0,
        "mek_data_sources_replaced": 3,
    }
    scope = plan.get("scope", {})
    for field, expected in expected_scope.items():
        if scope.get(field) != expected:
            failures.append(f"scope.{field} must be {expected}")
    if scope.get("rebased_seed_sha256") != REBASED_SEED_SHA256:
        failures.append("rebased seed hash changed")
    if scope.get("rebased_assignments_sha256") != UNCHANGED_ASSIGNMENTS_SHA256:
        failures.append("rebased assignment hash changed")
    expected_seed_implementation = {
        "status": "source_owned",
        "authoritative_source": "progression/managed_recipe_overhaul.seed.json",
        "recipe_count": 8,
        "recipe_ids": plan.get("seed_patch_contract", {}).get("append_recipe_ids"),
        "automatic_owners_retired": 8,
        "exact_stock_sources_retired": 8,
        "authoritative_generated_artifacts": "intentionally_not_regenerated_by_batch_owner",
    }
    if plan.get("seed_implementation") != expected_seed_implementation:
        failures.append("seed implementation metadata drifted")
    expected_assignment_implementation = {
        "status": "unchanged",
        "authoritative_source": "progression/machine_node_assignments.json",
        "changes": 0,
        "sha256": UNCHANGED_ASSIGNMENTS_SHA256,
    }
    if plan.get("assignment_implementation") != expected_assignment_implementation:
        failures.append("assignment implementation metadata drifted")
    expected_result = {
        "status": "passed_implemented",
        "source_recipes_verified": 8,
        "static_single_producer_outputs": 8,
        "contracts_compiled": 8,
        "compiled_exact_removals": 8,
        "mek_data_state_transfer_limitations_documented": 3,
        "mutation_tests": 32,
        "shared_progression_files_modified": 1,
    }
    result = plan.get("validation_result", {})
    for field, expected in expected_result.items():
        if result.get(field) != expected:
            failures.append(f"validation_result.{field} must be {expected}")
    expected_counts = {
        "createcasing:brass_press": 1,
        "createcasing:copper_press": 1,
        "createcasing:railway_press": 6,
    }
    if result.get("compiled_machine_counts") != expected_counts:
        failures.append("validation_result.compiled_machine_counts drifted")
    if plan.get("compiled_contract", {}).get("expected_exact_machine_counts") != expected_counts:
        failures.append("compiled_contract exact-machine counts drifted")
    if plan.get("compiled_contract", {}).get("sulfuric_acid_recipe_cards_added") != 0:
        failures.append("compiled contract creates a sulfuric-acid recipe card")

    validate_installed_evidence(plan, catalog, mods, failures)
    validate_automatic_evidence(
        plan, automatic_plan, automatic_plan_path, automatic_snapshot, failures
    )
    validate_capability_and_assignments(
        plan, seed, assignments, physical_tiers, branch_layout, failures
    )
    validate_contracts(plan, failures)
    validate_patch_and_compilation(
        plan, seed, assignments, catalog, mods, physical_tiers, failures,
        compile_batch=compile_batch,
    )
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--automatic-plan", type=Path, default=DEFAULT_AUTOMATIC_PLAN)
    parser.add_argument("--automatic-snapshot", type=Path, default=DEFAULT_AUTOMATIC_SNAPSHOT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--physical-tiers", type=Path, default=DEFAULT_PHYSICAL_TIERS)
    parser.add_argument("--branch-layout", type=Path, default=DEFAULT_BRANCH_LAYOUT)
    parser.add_argument("--no-compile", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        automatic_plan_path = args.automatic_plan.resolve()
        failures = validate_plan(
            load_json(args.plan.resolve()),
            load_json(automatic_plan_path),
            automatic_plan_path,
            args.automatic_snapshot.resolve(),
            args.catalog.resolve(),
            args.mods.resolve(),
            load_json(args.seed.resolve()),
            load_json(args.assignments.resolve()),
            args.physical_tiers.resolve(),
            args.branch_layout.resolve(),
            compile_batch=not args.no_compile,
        )
    except (
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        sqlite3.Error,
        zipfile.BadZipFile,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if failures:
        print(f"Mekanism pre-nuclear machine-chain audit failed ({len(failures)} issue(s)):")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "Mekanism pre-nuclear machine-chain audit passed: 8 installed single-source recipes "
        "verified; 8 generic automatic owners deterministically become 8 TFMG-first exact "
        "encased press recipes (Railway 6, Copper 1, Brass 1); Enrichment physically and "
        "declaratively precedes PRC; no HDPE/PRC-product or sulfuric-acid route is introduced; "
        "and all 3 mek_data state-transfer limitations are explicit."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
