#!/usr/bin/env python3
"""Validate the implemented Mekanism Universal Cable tail redesign.

The proof covers installed recipe bytes, catalog producers and consumers,
current managed consumers, automatic-owner evidence, TFMG-first manufacturing
semantics, physical machine reachability, exact dependency migration, prior
audit supersession, deterministic implemented-state parity, and an in-memory
KJSGen compile. No shared or deployed file is written.
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
import build_mekanism_universal_cable_tail_patch_plan as patch_builder


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
DEFAULT_PLAN = PROJECT / "MEKANISM_UNIVERSAL_CABLE_TAIL_AUDIT.plan.json"
DEFAULT_PATCH = PROJECT / "MEKANISM_UNIVERSAL_CABLE_TAIL_AUDIT.patch.json"
DEFAULT_AUTOMATIC_PLAN = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
DEFAULT_AUTOMATIC_SNAPSHOT = PROJECT / "build-current-audit/managed.json"
DEFAULT_CATALOG = WORKSPACE / "outputs/recipe-catalog-current/recipe_catalog.sqlite"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
DEFAULT_ENVIRONMENTS = (
    PROJECT
    / "src/main/resources/data/industrial_colonies/tier_recipe_environments.json"
)
DEFAULT_PHYSICAL_TIERS = PROJECT / "progression/physical_recipe_tiers.json"
DEFAULT_FACTORY_PLAN = PROJECT / "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json"
DEFAULT_BLACKLIST = (
    PROJECT
    / "src/main/resources/data/mekanism/tags/block/blacklist/installer_upgradeable.json"
)
DEFAULT_TRANSMITTER_PLAN = PROJECT / "MEKANISM_TRANSMITTER_UPGRADE_AUDIT.plan.json"
DEFAULT_TRANSMITTER_MD = PROJECT / "MEKANISM_TRANSMITTER_UPGRADE_AUDIT.md"
DEFAULT_INDUCTION_PLAN = PROJECT / "INDUCTION_MATRIX_COMPLETION_AUDIT.plan.json"
DEFAULT_INDUCTION_VALIDATOR = PROJECT / "tools/validate_induction_matrix_completion_audit.py"
GENERATOR = TOOLS / "generate_managed_recipe_overhaul.py"

ADVANCED_ID = "industrial_colonies:mekanism/transmission/advanced_universal_cable"
ELITE_ID = "industrial_colonies:mekanism/transmission/elite_universal_cable"
ULTIMATE_ID = "industrial_colonies:mekanism/transmission/ultimate_universal_cable"
BATCH_IDS = {ADVANCED_ID, ELITE_ID, ULTIMATE_ID}

ADVANCED_OUTPUT = "mekanism:advanced_universal_cable"
ELITE_OUTPUT = "mekanism:elite_universal_cable"
ULTIMATE_OUTPUT = "mekanism:ultimate_universal_cable"
BATCH_OUTPUTS = {ADVANCED_OUTPUT, ELITE_OUTPUT, ULTIMATE_OUTPUT}

AUTO_ADVANCED = "industrial_colonies:auto/mekanism/advanced_universal_cable"
AUTO_ELITE = "industrial_colonies:auto/mekanism/elite_universal_cable"
AUTO_ULTIMATE = "industrial_colonies:auto/mekanism/ultimate_universal_cable"
AUTOMATIC_IDS = {AUTO_ADVANCED, AUTO_ELITE, AUTO_ULTIMATE}

SOURCE_IDS = {
    ADVANCED_OUTPUT: "mekanism:transmitter/universal_cable/advanced",
    ELITE_OUTPUT: "mekanism:transmitter/universal_cable/elite",
    ULTIMATE_OUTPUT: "mekanism:transmitter/universal_cable/ultimate",
}
EXPECTED_REMOVALS = set(SOURCE_IDS.values())

EXPECTED_MACHINES = {
    ADVANCED_ID: "createcasing:copper_press",
    ELITE_ID: "createcasing:weathered_iron_press",
    ULTIMATE_ID: "createcasing:weathered_iron_press",
}
EXPECTED_NODES = {
    ADVANCED_ID: "CR01 — Reinforced Systems",
    ELITE_ID: "CR01 — Precision Engineering",
    ULTIMATE_ID: "CR01 — High-Energy Distribution",
}
EXPECTED_PHASES = {
    ADVANCED_ID: "Mekanized Industry",
    ELITE_ID: "High-Energy Grid",
    ULTIMATE_ID: "High-Energy Grid",
}
EXPECTED_ORDERS = {ADVANCED_ID: 10, ELITE_ID: 60, ULTIMATE_ID: 110}
EXPECTED_INPUTS = {
    ADVANCED_ID: [
        "8x mekanism:basic_universal_cable",
        "4x mekanism:alloy_infused",
        "2x mekanism:advanced_control_circuit",
        "4x tfmg:aluminum_wire",
        "2x tfmg:aluminum_cable_hub",
        "4x tfmg:rubber_sheet",
    ],
    ELITE_ID: [
        "8x mekanism:advanced_universal_cable",
        "4x mekanism:alloy_reinforced",
        "2x mekanism:elite_control_circuit",
        "4x tfmg:aluminum_wire",
        "2x tfmg:glass_cable_insulator",
        "2x tfmg:steel_cable_hub",
    ],
    ULTIMATE_ID: [
        "8x mekanism:elite_universal_cable",
        "4x mekanism:alloy_atomic",
        "2x mekanism:ultimate_control_circuit",
        "4x tfmg:aluminum_wire",
        "2x tfmg:glass_cable_insulator",
        "2x tfmg:steel_cable_hub",
        "4x electroenergetics:heavily_insulated_wire",
        "electroenergetics:sulfur_hexafluoride_breaker",
    ],
}
EXPECTED_DEPENDENCIES = {
    ADVANCED_ID: {
        "industrial_colonies:mekanism/transmission/basic_universal_cable",
        "industrial_colonies:mekanism/advanced_control_circuit",
    },
    ELITE_ID: {
        ADVANCED_ID,
        "industrial_colonies:mekanism/elite_control_circuit",
    },
    ULTIMATE_ID: {
        ELITE_ID,
        "industrial_colonies:mekanism/ultimate_control_circuit",
        "industrial_colonies:extreme_grid/heavily_insulated_wire",
        "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker",
    },
}
EXPECTED_OUTPUTS = {
    ADVANCED_ID: ADVANCED_OUTPUT,
    ELITE_ID: ELITE_OUTPUT,
    ULTIMATE_ID: ULTIMATE_OUTPUT,
}
EXPECTED_OLD_TO_NEW = {
    AUTO_ADVANCED: ADVANCED_ID,
    AUTO_ELITE: ELITE_ID,
    AUTO_ULTIMATE: ULTIMATE_ID,
}
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


def recipe_output(recipe: dict[str, Any]) -> tuple[str, int]:
    output = recipe.get("output")
    if isinstance(output, str):
        return split_ref(output)
    if isinstance(output, dict) and isinstance(output.get("id"), str):
        count = output.get("count", 1)
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise ValueError(f"recipe {recipe.get('id')!r} has invalid output count")
        return count, output["id"]
    raise ValueError(f"recipe {recipe.get('id')!r} has no singular output")


def contracts_by_id(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    values = plan.get("replacement_contracts")
    if not isinstance(values, list):
        raise ValueError("replacement_contracts must be an array")
    result: dict[str, dict[str, Any]] = {}
    for value in values:
        if not isinstance(value, dict) or not isinstance(value.get("id"), str):
            raise ValueError("replacement_contracts contains an invalid entry")
        if value["id"] in result:
            raise ValueError(f"duplicate contract {value['id']}")
        result[value["id"]] = value
    return result


def recipes_by_id(seed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    values = seed.get("recipes")
    if not isinstance(values, list):
        raise ValueError("seed recipes must be an array")
    result: dict[str, dict[str, Any]] = {}
    for value in values:
        if not isinstance(value, dict) or not isinstance(value.get("id"), str):
            raise ValueError("seed contains an invalid recipe")
        result[value["id"]] = value
    return result


def ingredient_ref(value: Any, label: str) -> str:
    if not isinstance(value, dict):
        raise ValueError(f"{label} ingredient is not an object")
    if isinstance(value.get("item"), str):
        return value["item"]
    if isinstance(value.get("tag"), str):
        return "#" + value["tag"]
    raise ValueError(f"{label} ingredient has no item or tag")


def source_ingredient_counts(raw: dict[str, Any], label: str) -> Counter[str]:
    if raw.get("type") != "minecraft:crafting_shaped":
        raise ValueError(f"{label} is not a shaped recipe")
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
    return result["id"], count


def find_artifact(mods: Path, name: str) -> Path:
    path = mods / name
    if not path.is_file():
        raise ValueError(f"installed artifact is absent: {path}")
    return path


def validate_installed_sources(
    plan: dict[str, Any], catalog: Path, mods: Path, failures: list[str]
) -> None:
    evidence = plan.get("installed_evidence", {})
    catalog_contract = evidence.get("recipe_catalog", {})
    if catalog_contract.get("path") != "outputs/recipe-catalog-current/recipe_catalog.sqlite":
        failures.append("recipe catalog provenance path changed")
    if sha256_file(catalog) != catalog_contract.get("sha256"):
        failures.append("recipe catalog SHA-256 drifted")

    artifacts = evidence.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 4:
        failures.append("installed artifact inventory must contain four exact files")
        return
    artifact_paths: dict[str, Path] = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("name"), str):
            failures.append("installed artifact entry is invalid")
            continue
        path = find_artifact(mods, artifact["name"])
        artifact_paths[artifact["name"]] = path
        if sha256_file(path) != artifact.get("sha256"):
            failures.append(f"installed artifact SHA-256 drifted: {artifact['name']}")

    source_contracts = evidence.get("source_recipe_contracts")
    if not isinstance(source_contracts, list) or len(source_contracts) != 3:
        failures.append("source recipe inventory must contain three contracts")
        return
    mekanism = artifact_paths.get("Mekanism-1.21.1-10.7.19.85.jar")
    if mekanism is None:
        return
    with zipfile.ZipFile(mekanism) as archive:
        for contract in source_contracts:
            path = contract.get("source_path")
            if not isinstance(path, str):
                failures.append("source recipe contract has no path")
                continue
            try:
                raw_bytes = archive.read(path)
            except KeyError:
                failures.append(f"source recipe is absent from Mekanism JAR: {path}")
                continue
            if sha256_bytes(raw_bytes) != contract.get("source_sha256"):
                failures.append(f"source recipe SHA-256 drifted: {path}")
            raw = json.loads(raw_bytes.decode("utf-8"))
            if raw.get("type") != contract.get("recipe_type"):
                failures.append(f"source recipe type drifted: {path}")
            output, count = source_result(raw, path)
            if (output, count) != (contract.get("output"), contract.get("output_count")):
                failures.append(f"source recipe output drifted: {path}")
            expected_inputs = Counter(contract.get("exact_inputs", {}))
            if source_ingredient_counts(raw, path) != expected_inputs:
                failures.append(f"source recipe inputs drifted: {path}")

    connection = sqlite3.connect(catalog)
    try:
        expected_producers = {
            value["output"]: value["recipe_ids"]
            for value in evidence.get("static_producer_inventory", [])
        }
        if set(expected_producers) != BATCH_OUTPUTS:
            failures.append("static producer output inventory drifted")
        for output in sorted(BATCH_OUTPUTS):
            rows = connection.execute(
                "SELECT recipe_id, count FROM item_recipe_map "
                "WHERE item_id = ? AND role = 'output' ORDER BY recipe_id",
                (output,),
            ).fetchall()
            observed = [row[0] for row in rows]
            if observed != expected_producers.get(output):
                failures.append(
                    f"static producer inventory drifted for {output}: {observed}"
                )
            if any(row[1] != 8.0 for row in rows):
                failures.append(f"static producer output count drifted for {output}")

        expected_consumers = {
            value["input"]: value["recipe_ids"]
            for value in evidence.get("installed_consumer_inventory", [])
        }
        expected_consumer_map = {
            ADVANCED_OUTPUT: [SOURCE_IDS[ELITE_OUTPUT]],
            ELITE_OUTPUT: [SOURCE_IDS[ULTIMATE_OUTPUT]],
            ULTIMATE_OUTPUT: [],
        }
        if expected_consumers != expected_consumer_map:
            failures.append("installed consumer contract changed")
        for item, expected in expected_consumer_map.items():
            rows = connection.execute(
                "SELECT recipe_id FROM item_recipe_map "
                "WHERE item_id = ? AND role = 'input' ORDER BY recipe_id",
                (item,),
            ).fetchall()
            observed = [row[0] for row in rows]
            if observed != expected:
                failures.append(f"installed consumers drifted for {item}: {observed}")

        installed_inputs = evidence.get("installed_manufacturing_inputs")
        if not isinstance(installed_inputs, list) or len(installed_inputs) != 14:
            failures.append("installed manufacturing-input inventory changed")
        else:
            marks = ",".join("?" for _ in installed_inputs)
            rows = connection.execute(
                f"SELECT item_id FROM items WHERE item_id IN ({marks})",
                tuple(installed_inputs),
            ).fetchall()
            observed = {row[0] for row in rows}
            missing = sorted(set(installed_inputs) - observed)
            if missing:
                failures.append(f"reviewed manufacturing inputs are absent: {missing}")

        unavailable = evidence.get("unavailable_conceptual_ids")
        if unavailable != [
            "electroenergetics:extreme_wire",
            "tfmg:sulfur_hexafluoride_bucket",
        ]:
            failures.append("unavailable conceptual-ID inventory changed")
        else:
            marks = ",".join("?" for _ in unavailable)
            rows = connection.execute(
                f"SELECT item_id FROM items WHERE item_id IN ({marks})",
                tuple(unavailable),
            ).fetchall()
            if rows:
                failures.append(f"conceptual IDs unexpectedly became installed: {rows}")
    finally:
        connection.close()


def seed_input_counts(recipe: dict[str, Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    inputs = recipe.get("inputs", [])
    if inputs is None:
        inputs = []
    if not isinstance(inputs, list):
        raise ValueError(f"recipe {recipe.get('id')!r} has non-array inputs")
    for value in inputs:
        if not isinstance(value, str):
            continue
        count, identity = split_ref(value)
        counts[identity] += count
    pattern = recipe.get("pattern")
    key = recipe.get("key")
    if pattern is not None or key is not None:
        if not isinstance(pattern, list) or not isinstance(key, dict):
            raise ValueError(f"recipe {recipe.get('id')!r} has invalid shaped data")
        for row in pattern:
            for symbol in row:
                if symbol == " ":
                    continue
                value = key.get(symbol)
                if isinstance(value, str):
                    _, identity = split_ref(value)
                    counts[identity] += 1
    return counts


def validate_managed_consumers(
    plan: dict[str, Any], seed: dict[str, Any], failures: list[str]
) -> None:
    expected = sorted(
        (
            entry["input"],
            entry["count"],
            entry["owner_recipe_id"],
        )
        for entry in plan.get("installed_evidence", {}).get(
            "managed_seed_consumer_inventory", []
        )
    )
    recipes = recipes_by_id(seed)
    observed: list[tuple[str, int, str]] = []
    for owner, recipe in recipes.items():
        if owner in BATCH_IDS:
            continue
        counts = seed_input_counts(recipe)
        for item in BATCH_OUTPUTS:
            if counts[item]:
                observed.append((item, counts[item], owner))
    if sorted(observed) != expected:
        failures.append(
            f"managed seed consumer inventory drifted: expected {expected}, got {sorted(observed)}"
        )


def validate_automatic_evidence(
    plan: dict[str, Any], automatic_plan: dict[str, Any],
    automatic_snapshot: dict[str, Any], seed: dict[str, Any], failures: list[str]
) -> None:
    evidence = plan.get("automatic_owner_evidence", {})
    batches = [
        value
        for value in automatic_plan.get("implementation_batches", [])
        if value.get("id") == evidence.get("batch_id")
    ]
    if len(batches) != 1:
        failures.append("automatic Universal Cable batch evidence is absent or duplicated")
    else:
        batch = batches[0]
        if set(batch.get("outputs", [])) != BATCH_OUTPUTS:
            failures.append("automatic batch output set drifted")
        if set(batch.get("managed_ids", [])) != AUTOMATIC_IDS:
            failures.append("automatic batch managed-ID set drifted")
        if set(batch.get("installed_recipe_ids", [])) != EXPECTED_REMOVALS:
            failures.append("automatic batch source-ID set drifted")

    entries = {
        value.get("managed_id"): value
        for value in automatic_plan.get("entries", [])
        if value.get("managed_id") in AUTOMATIC_IDS
    }
    if set(entries) != AUTOMATIC_IDS:
        failures.append("automatic entry inventory drifted")
    for identity, entry in entries.items():
        if entry.get("classification") != "needs_source_owned_redesign":
            failures.append(f"automatic entry classification drifted: {identity}")
        if entry.get("generic_gate_ring") is not True:
            failures.append(f"automatic entry no longer records a generic ring: {identity}")

    snapshot = {
        value.get("id"): value
        for value in automatic_snapshot.get("recipes", [])
        if value.get("id") in AUTOMATIC_IDS
    }
    if set(snapshot) != AUTOMATIC_IDS:
        failures.append("automatic managed snapshot lost one or more current owners")
    for identity, recipe in snapshot.items():
        count, output = recipe_output(recipe)
        if count != 8 or output not in BATCH_OUTPUTS:
            failures.append(f"automatic owner output drifted: {identity}")
        if recipe.get("type") != "mechanical_crafting":
            failures.append(f"automatic owner type drifted: {identity}")

    current_seed_ids = set(recipes_by_id(seed))
    if current_seed_ids & AUTOMATIC_IDS:
        failures.append("one or more generator-owned automatic IDs entered the seed")


def input_refs(contract: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for value in contract.get("inputs", []):
        if isinstance(value, str):
            _, identity = split_ref(value)
            refs.append(identity)
    return refs


def validate_contract_dag(
    contracts: dict[str, dict[str, Any]], failures: list[str]
) -> None:
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
        failures.append("source-owned contract ID set drifted")
        return
    if {recipe_output(value)[1] for value in contracts.values()} != BATCH_OUTPUTS:
        failures.append("source-owned output set drifted")
    if any(recipe_output(value)[0] != 8 for value in contracts.values()):
        failures.append("every Universal Cable contract must output exactly eight")
    if any(value.get("type") != "compacting" for value in contracts.values()):
        failures.append("Universal Cable contracts must remain Encased compacting recipes")
    if {key: value.get("machine") for key, value in contracts.items()} != EXPECTED_MACHINES:
        failures.append("exact Encased machine mapping changed")
    if {key: value.get("node") for key, value in contracts.items()} != EXPECTED_NODES:
        failures.append("reviewed node placement changed")
    if {key: value.get("phase") for key, value in contracts.items()} != EXPECTED_PHASES:
        failures.append("reviewed phase placement changed")
    if {key: value.get("order") for key, value in contracts.items()} != EXPECTED_ORDERS:
        failures.append("reviewed recipe order changed")
    if {key: value.get("inputs") for key, value in contracts.items()} != EXPECTED_INPUTS:
        failures.append("reviewed manufacturing bills changed")
    if {
        key: set(value.get("depends_on", [])) for key, value in contracts.items()
    } != EXPECTED_DEPENDENCIES:
        failures.append("reviewed dependency sets changed")

    removals = [value for recipe in contracts.values() for value in recipe.get("remove", [])]
    if len(removals) != 3 or set(removals) != EXPECTED_REMOVALS:
        failures.append("exact stock-removal contract changed")
    if any(recipe.get("exclusive_output") is not True for recipe in contracts.values()):
        failures.append("all three cable outputs must remain exclusive")

    for identity, contract in contracts.items():
        refs = input_refs(contract)
        previous = {
            ADVANCED_ID: "mekanism:basic_universal_cable",
            ELITE_ID: ADVANCED_OUTPUT,
            ULTIMATE_ID: ELITE_OUTPUT,
        }[identity]
        previous_values = [
            value for value in contract.get("inputs", []) if split_ref(value)[1] == previous
        ]
        if previous_values != [f"8x {previous}"]:
            failures.append(f"{identity}: prior run is not preserved as exactly eight")
        if len(set(refs)) < 6:
            failures.append(f"{identity}: manufacturing bill collapsed into a generic ring")
        if any(ref.startswith("#") for ref in refs):
            failures.append(f"{identity}: counted-tag shortcut entered the cable contract")
        if not any(ref.startswith("tfmg:") for ref in refs):
            failures.append(f"{identity}: lost TFMG conductor/insulation ownership")
        if recipe_output(contract)[1] in refs:
            failures.append(f"{identity}: recipe consumes its own output")
        if set(contract.get("depends_on", [])) & AUTOMATIC_IDS:
            failures.append(f"{identity}: retains a retired automatic dependency")

    early_ee = {
        ref
        for identity in (ADVANCED_ID, ELITE_ID)
        for ref in input_refs(contracts[identity])
        if ref.startswith("electroenergetics:") or "sulfur_hexafluoride" in ref
    }
    if early_ee:
        failures.append(f"Advanced or Elite jumped to the protected grid: {sorted(early_ee)}")
    ultimate_ee = {
        ref
        for ref in input_refs(contracts[ULTIMATE_ID])
        if ref.startswith("electroenergetics:")
    }
    expected_ultimate_ee = {
        "electroenergetics:heavily_insulated_wire",
        "electroenergetics:sulfur_hexafluoride_breaker",
    }
    if ultimate_ee != expected_ultimate_ee:
        failures.append("Ultimate protected-grid convergence changed")

    observed_same_batch = {
        identity: {
            dependency
            for dependency in contract.get("depends_on", [])
            if dependency in contracts
        }
        for identity, contract in contracts.items()
    }
    expected_same_batch = {
        ADVANCED_ID: set(), ELITE_ID: {ADVANCED_ID}, ULTIMATE_ID: {ELITE_ID}
    }
    if observed_same_batch != expected_same_batch:
        failures.append("Advanced -> Elite -> Ultimate same-batch ladder changed")
    validate_contract_dag(contracts, failures)


def find_output_owner(seed: dict[str, Any], output: str) -> list[str]:
    owners: list[str] = []
    for recipe in seed.get("recipes", []):
        try:
            _, identity = recipe_output(recipe)
        except ValueError:
            continue
        if identity == output:
            owners.append(recipe["id"])
    return owners


def validate_progression(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    environments: dict[str, Any], physical_tiers: dict[str, Any], catalog: Path,
    failures: list[str],
) -> None:
    placements = plan.get("assignment_contract", {}).get("required_existing_placement", [])
    if plan.get("assignment_contract", {}).get("changes") != []:
        failures.append("Universal Cable assignment contract must remain no-change")
    for placement in placements:
        output = placement.get("output")
        node = placement.get("node")
        owners = [
            label
            for label, value in assignments.get("nodes", {}).items()
            if isinstance(value, dict)
            and isinstance(value.get("unlocks"), list)
            and output in value["unlocks"]
        ]
        if owners != [node]:
            failures.append(f"assignment placement drifted for {output}: {owners}")

    compacting = [
        value for value in environments.get("recipe_families", [])
        if value.get("id") == "compacting"
    ]
    if len(compacting) != 1:
        failures.append("compacting environment family is absent or duplicated")
    else:
        machines = {
            value.get("item"): value.get("tier")
            for value in compacting[0].get("machines", [])
        }
        expected = {
            "createcasing:copper_press": "copper",
            "createcasing:weathered_iron_press": "weathered_iron",
        }
        if {key: machines.get(key) for key in expected} != expected:
            failures.append("reviewed Encased compacting environments drifted")

    tiers = {
        value.get("id"): value.get("rank") for value in physical_tiers.get("tiers", [])
    }
    if tiers.get("copper") != 1 or tiers.get("weathered_iron") != 5:
        failures.append("Copper or Weathered Iron physical tier rank drifted")

    prerequisites = {
        "createcasing:copper_press": "industrial_colonies:manufacturing/copper_press",
        "mekanism:basic_universal_cable": "industrial_colonies:mekanism/transmission/basic_universal_cable",
        "mekanism:advanced_control_circuit": "industrial_colonies:mekanism/advanced_control_circuit",
        "mekanism:elite_control_circuit": "industrial_colonies:mekanism/elite_control_circuit",
        "mekanism:ultimate_control_circuit": "industrial_colonies:mekanism/ultimate_control_circuit",
        "electroenergetics:heavily_insulated_wire": "industrial_colonies:extreme_grid/heavily_insulated_wire",
        "electroenergetics:sulfur_hexafluoride_breaker": "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker",
    }
    for output, owner in prerequisites.items():
        observed = find_output_owner(seed, output)
        if observed != [owner]:
            failures.append(f"physical predecessor owner drifted for {output}: {observed}")

    extreme_ids = {
        "industrial_colonies:extreme_grid/heavily_insulated_wire",
        "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker",
    }
    seed_recipes = recipes_by_id(seed)
    for identity in extreme_ids:
        recipe = seed_recipes.get(identity)
        if recipe is None:
            continue
        if set(recipe.get("depends_on", [])) & BATCH_IDS:
            failures.append(f"extreme-grid predecessor creates a cable cycle: {identity}")
        if set(seed_input_counts(recipe)) & BATCH_OUTPUTS:
            failures.append(f"extreme-grid predecessor consumes a cable target: {identity}")

    connection = sqlite3.connect(catalog)
    try:
        machine_ids = set(EXPECTED_MACHINES.values())
        marks = ",".join("?" for _ in machine_ids)
        rows = connection.execute(
            f"SELECT item_id FROM items WHERE item_id IN ({marks})", tuple(machine_ids)
        ).fetchall()
        if {row[0] for row in rows} != machine_ids:
            failures.append("one or more reviewed Encased press items are not installed")
    finally:
        connection.close()


def pointer_get(root: Any, pointer: str) -> Any:
    value = root
    for part in pointer.lstrip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            value = value[int(part)]
        elif isinstance(value, dict):
            value = value[part]
        else:
            raise ValueError(f"cannot traverse {pointer!r}")
    return value


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def validate_dependency_mapping_and_supersession(
    plan: dict[str, Any], seed: dict[str, Any], induction_plan: dict[str, Any],
    induction_validator: Path, transmitter_plan: dict[str, Any],
    transmitter_md: Path, factory_plan: dict[str, Any], blacklist: dict[str, Any],
    failures: list[str],
) -> None:
    policy = plan.get("dependency_rewrite_contract", {})
    if policy.get("id_map") != EXPECTED_OLD_TO_NEW:
        failures.append("retired automatic-to-source-owned ID map changed")

    seed_recipes = recipes_by_id(seed)
    retired_dependencies = [
        dependency
        for recipe in seed_recipes.values()
        for dependency in recipe.get("depends_on", []) or []
        if dependency in AUTOMATIC_IDS
    ]
    if retired_dependencies:
        failures.append(f"authoritative seed retains retired cable dependencies: {retired_dependencies}")
    for entry in policy.get("authoritative_seed_rewrites", []):
        try:
            observed = pointer_get(seed, entry["json_pointer"])
        except (KeyError, IndexError, ValueError, TypeError) as error:
            failures.append(f"cannot resolve implemented seed dependency pointer: {error}")
            continue
        if observed != entry.get("to") or entry.get("from") not in AUTOMATIC_IDS:
            failures.append(
                f"implemented seed dependency migration drifted at {entry.get('json_pointer')}"
            )

    induction_rewrites = policy.get("induction_audit_plan_rewrites", [])
    if len(induction_rewrites) != 3:
        failures.append("Induction audit plan rewrite inventory must contain three entries")
    for entry in induction_rewrites:
        try:
            observed = pointer_get(induction_plan, entry["json_pointer"])
        except (KeyError, IndexError, ValueError, TypeError) as error:
            failures.append(f"cannot resolve Induction audit pointer: {error}")
            continue
        if observed != entry.get("to") or entry.get("to") != ULTIMATE_ID:
            failures.append(
                f"Induction audit dependency mapping drifted at {entry.get('json_pointer')}"
            )

    validator_rewrites = policy.get("active_validator_rewrites", [])
    if len(validator_rewrites) != 1:
        failures.append("active validator rewrite inventory must contain one entry")
    else:
        entry = validator_rewrites[0]
        text = induction_validator.read_text(encoding="utf-8-sig")
        if text.count(entry.get("from", "")) != 0:
            failures.append("Induction validator retains the retired automatic ID")
        if text.count(entry.get("to", "")) != entry.get("occurrences"):
            failures.append("Induction validator source-owned ID occurrence count drifted")
        if entry.get("to") != ULTIMATE_ID:
            failures.append("Induction validator target ID drifted")

    supersession = plan.get("supersession_contract", {})
    if supersession.get("supersedes_plan") != "MEKANISM_TRANSMITTER_UPGRADE_AUDIT.plan.json":
        failures.append("transmitter-plan supersession target changed")
    if "other twelve transmitter upgrades" not in supersession.get("authority_rule", ""):
        failures.append("supersession no longer preserves the other twelve transmitters")
    preserved = transmitter_plan.get("preserved_universal_managed_ids", [])
    if {value.get("id") for value in preserved} != AUTOMATIC_IDS:
        failures.append("prior preserved-Universal evidence drifted before supersession")
    old_cable_contracts = [
        value
        for value in transmitter_plan.get("replacement_contracts", [])
        if recipe_output(value)[1] in BATCH_OUTPUTS
    ]
    if {value.get("id") for value in old_cable_contracts} != AUTOMATIC_IDS:
        failures.append("prior cable replacement evidence drifted before supersession")
    old_md = normalize_space(transmitter_md.read_text(encoding="utf-8-sig"))
    for statement in supersession.get("stale_markdown_statements", []):
        if normalize_space(statement) not in old_md:
            failures.append(f"superseded transmitter statement is no longer present: {statement}")

    runtime = plan.get("progression_contract", {}).get("runtime_tier_installer_policy", {})
    if runtime.get("blacklist_change") is not False:
        failures.append("Universal Cable integration must not change installer blacklist")
    excluded = set(
        factory_plan.get("installer_bypass_closure", {}).get(
            "excluded_transmitter_blocks", []
        )
    )
    if not BATCH_OUTPUTS <= excluded:
        failures.append("factory runtime audit no longer excludes all cable transmitters")
    blacklist_values = set(blacklist.get("values", []))
    if blacklist_values & BATCH_OUTPUTS:
        failures.append("Universal Cable blocks entered installer_upgradeable blacklist")


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("universal_cable_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load managed recipe compiler: {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_patch_and_compilation(
    plan: dict[str, Any], static_patch: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    catalog: Path, mods: Path, failures: list[str], *, compile_batch: bool,
) -> None:
    try:
        first = patch_builder.build_patch_plan(plan, seed, assignments)
        second = patch_builder.build_patch_plan(plan, seed, assignments)
    except patch_builder.PatchPlanError as error:
        failures.append(f"deterministic patch precondition failed: {error}")
        return
    if first != second:
        failures.append("patch-plan builder is nondeterministic")
        return
    if first != static_patch:
        failures.append("checked-in review patch drifted from deterministic builder output")
    if first.get("status") != "implemented_in_seed":
        failures.append("patch-plan builder lost implemented status")
    if first.get("mode") != "implemented_historical_patch":
        failures.append("patch-plan builder is not an implemented historical record")
    if first.get("assignments", {}).get("changes") != []:
        failures.append("patch plan unexpectedly mutates assignments")
    if first.get("seed", {}).get("remove_source_recipe_override_outputs") != []:
        failures.append("patch plan unexpectedly mutates source overrides")
    if len(first.get("seed", {}).get("exact_dependency_rewrites", [])) != 2:
        failures.append("patch plan lost an authoritative dependency rewrite")

    try:
        staged_seed, staged_assignments = patch_builder.apply_patch_to_copies(
            plan, seed, assignments
        )
    except patch_builder.PatchPlanError as error:
        failures.append(f"in-memory patch application failed: {error}")
        return
    if staged_assignments != assignments:
        failures.append("in-memory patch changed assignments")
    staged_recipes = recipes_by_id(staged_seed)
    if not BATCH_IDS <= set(staged_recipes):
        failures.append("in-memory seed is missing one or more cable contracts")
    old_dependencies = [
        dependency
        for recipe in staged_seed.get("recipes", [])
        for dependency in recipe.get("depends_on", []) or []
        if dependency in AUTOMATIC_IDS
    ]
    if old_dependencies:
        failures.append(f"in-memory seed retains retired dependencies: {old_dependencies}")
    for owner in (
        "industrial_colonies:mekanism/induction/port",
        "industrial_colonies:mekanism/induction/ultimate_provider",
    ):
        dependencies = staged_recipes[owner].get("depends_on", [])
        if ULTIMATE_ID not in dependencies:
            failures.append(f"in-memory seed did not migrate {owner} to new Ultimate owner")

    if not compile_batch:
        return
    with tempfile.TemporaryDirectory(prefix="universal-cable-tail-audit-") as temporary:
        root = Path(temporary)
        seed_path = root / "seed.json"
        assignments_path = root / "assignments.json"
        manifest_path = root / "managed.json"
        compiled_path = root / "compiled.json"
        seed_path.write_text(
            json.dumps(staged_seed, indent=2, ensure_ascii=False), encoding="utf-8"
        )
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
            failures.append(f"in-memory managed manifest rejected cable batch: {error}")
            return
        if report.get("fatal_errors", []):
            failures.append(
                f"in-memory managed manifest reported fatal errors: {report['fatal_errors']}"
            )
            return
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        try:
            compiled = load_generator().compile_manifest(manifest_path, compiled_path)
        except (OSError, ValueError, KeyError, TypeError) as error:
            failures.append(f"KJSGen compiler rejected cable batch: {error}")
            return

    managed_ids = {value.get("id") for value in manifest.get("recipes", [])}
    if not BATCH_IDS <= managed_ids:
        failures.append("compiled managed manifest lost a source-owned cable recipe")
    if managed_ids & AUTOMATIC_IDS:
        failures.append("one or more generic automatic cable owners survived")
    cards = [
        value for value in compiled.get("recipes", [])
        if value.get("recipeId") in BATCH_IDS
    ]
    if len(cards) != 3:
        failures.append(f"compiled cable recipe-card count drifted: {len(cards)}")
        return
    expected_types = Counter(plan.get("compiled_contract", {}).get("expected_card_type_counts", {}))
    if Counter(value.get("type") for value in cards) != expected_types:
        failures.append("compiled cable card-type counts drifted")
    expected_machines = Counter(
        plan.get("compiled_contract", {}).get("expected_exact_machine_counts", {})
    )
    machines: Counter[str] = Counter()
    for card in cards:
        machine = card.get("slots", {}).get("__machine_process_compacting", {}).get("id")
        machines[machine] += 1
        output = card.get("slots", {}).get("output", {})
        if output.get("count", 1) != 8:
            failures.append(f"compiled cable output count drifted: {card.get('recipeId')}")
    if machines != expected_machines:
        failures.append(f"compiled exact-machine counts drifted: {dict(machines)}")
    removals = {
        value.get("recipeId")
        for value in compiled.get("removals", [])
        if value.get("recipeId")
    }
    if not EXPECTED_REMOVALS <= removals:
        failures.append("compiled output is missing an exact stock recipe removal")


def validate_plan(
    plan: dict[str, Any], static_patch: dict[str, Any], automatic_plan: dict[str, Any],
    automatic_snapshot: dict[str, Any], catalog: Path, mods: Path,
    seed: dict[str, Any], assignments: dict[str, Any],
    environments: dict[str, Any], physical_tiers: dict[str, Any],
    induction_plan: dict[str, Any], induction_validator: Path,
    transmitter_plan: dict[str, Any], transmitter_md: Path,
    factory_plan: dict[str, Any], blacklist: dict[str, Any],
    *, compile_batch: bool = True,
) -> list[str]:
    failures: list[str] = []
    if plan.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        failures.append("status must remain implemented_in_seed")
    if plan.get("decision") != "GO_WITH_THREE_TFMG_FIRST_SOURCE_OWNED_CABLE_CONTRACTS":
        failures.append("audit decision changed")
    expected_scope = {
        "outputs": 3,
        "source_owned_contracts": 3,
        "automatic_owners_retired": 3,
        "exact_stock_recipe_removals": 3,
        "output_count_each": 8,
        "assignment_changes": 0,
        "authoritative_seed_dependency_rewrites": 2,
        "active_validator_dependency_rewrites": 1,
    }
    if plan.get("scope") != expected_scope:
        failures.append("reviewed scope counts changed")
    implementation = plan.get("implementation")
    expected_implementation = {
        "base_seed_sha256": "66EF6386BB80B7A9DABF30752570F71E8B0BB87DCD25A0E9CC15474878EBBB36",
        "implemented_seed_sha256": "D34BB136243F77BA8786053F2CD422AB57860D051B90280EE4638144B777A923",
        "unchanged_assignments_sha256": "329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E",
        "recipes_added": 3,
        "seed_dependency_rewrites": 2,
        "assignment_changes": 0,
        "induction_audit_plan_rewrites": 3,
        "induction_validator_rewrites": 1,
        "isolated_result": {
            "managed_recipes": 329,
            "automatic_recipes": 83,
            "compiled_cards": 397,
            "exact_removals": 661,
            "skipped_assigned_outputs": 33,
            "dag_warnings": 0,
        },
    }
    if implementation != expected_implementation:
        failures.append("implementation checkpoint metadata changed")
    expected_result = {
        "status": "passed_implemented",
        "source_recipes_verified": 3,
        "static_single_producer_outputs": 3,
        "installed_consumers_verified": 2,
        "managed_seed_consumers_verified": 4,
        "contracts_compiled": 3,
        "compiled_exact_removals": 3,
        "compiled_machine_counts": {
            "createcasing:copper_press": 1,
            "createcasing:weathered_iron_press": 2,
        },
        "dependency_rewrites_implemented": 2,
        "mutation_tests": 27,
        "shared_progression_files_modified": 1,
    }
    if plan.get("validation_result") != expected_result:
        failures.append("validation_result summary changed")

    validate_installed_sources(plan, catalog, mods, failures)
    validate_managed_consumers(plan, seed, failures)
    validate_automatic_evidence(
        plan, automatic_plan, automatic_snapshot, seed, failures
    )
    validate_contracts(plan, failures)
    validate_progression(
        plan, seed, assignments, environments, physical_tiers, catalog, failures
    )
    validate_dependency_mapping_and_supersession(
        plan,
        seed,
        induction_plan,
        induction_validator,
        transmitter_plan,
        transmitter_md,
        factory_plan,
        blacklist,
        failures,
    )
    validate_patch_and_compilation(
        plan,
        static_patch,
        seed,
        assignments,
        catalog,
        mods,
        failures,
        compile_batch=compile_batch,
    )
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--automatic-plan", type=Path, default=DEFAULT_AUTOMATIC_PLAN)
    parser.add_argument(
        "--automatic-snapshot", type=Path, default=DEFAULT_AUTOMATIC_SNAPSHOT
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--environments", type=Path, default=DEFAULT_ENVIRONMENTS)
    parser.add_argument("--physical-tiers", type=Path, default=DEFAULT_PHYSICAL_TIERS)
    parser.add_argument("--induction-plan", type=Path, default=DEFAULT_INDUCTION_PLAN)
    parser.add_argument(
        "--induction-validator", type=Path, default=DEFAULT_INDUCTION_VALIDATOR
    )
    parser.add_argument("--transmitter-plan", type=Path, default=DEFAULT_TRANSMITTER_PLAN)
    parser.add_argument("--transmitter-md", type=Path, default=DEFAULT_TRANSMITTER_MD)
    parser.add_argument("--factory-plan", type=Path, default=DEFAULT_FACTORY_PLAN)
    parser.add_argument("--blacklist", type=Path, default=DEFAULT_BLACKLIST)
    parser.add_argument("--no-compile", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        failures = validate_plan(
            load_json(args.plan.resolve()),
            load_json(args.patch.resolve()),
            load_json(args.automatic_plan.resolve()),
            load_json(args.automatic_snapshot.resolve()),
            args.catalog.resolve(),
            args.mods.resolve(),
            load_json(args.seed.resolve()),
            load_json(args.assignments.resolve()),
            load_json(args.environments.resolve()),
            load_json(args.physical_tiers.resolve()),
            load_json(args.induction_plan.resolve()),
            args.induction_validator.resolve(),
            load_json(args.transmitter_plan.resolve()),
            args.transmitter_md.resolve(),
            load_json(args.factory_plan.resolve()),
            load_json(args.blacklist.resolve()),
            compile_batch=not args.no_compile,
        )
    except (
        OSError,
        ValueError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
        sqlite3.Error,
        zipfile.BadZipFile,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if failures:
        print(f"Universal Cable tail audit failed ({len(failures)} issue(s)):")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "Universal Cable tail audit passed: 3 exact single-source Mekanism rings "
        "deterministically become 3 TFMG-first Encased compacting contracts, each "
        "preserving an 8-segment run; Advanced remains Copper/Mekanized, only "
        "Ultimate converges the installed protected-wire and SF6-breaker chain, "
        "2 authoritative Induction dependencies use the source-owned Ultimate ID, and the "
        "3 generic automatic owners are absent from the compiled proof."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
