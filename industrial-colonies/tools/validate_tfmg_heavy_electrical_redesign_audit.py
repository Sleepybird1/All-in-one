#!/usr/bin/env python3
"""Validate the implemented TFMG heavy/electrical redesign batch.

The proof covers installed source JSON, item and machine existence, the pinned
automatic-owner evidence, capability order, TFMG-first ingredient choices,
stateful engine-cylinder parity, deterministic implementation reporting, an
in-memory manifest build, and KJSGen compilation. It never edits shared
progression or generated files.
"""

from __future__ import annotations

import argparse
import copy
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
import build_tfmg_heavy_electrical_patch_plan as patch_builder


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
DEFAULT_PLAN = PROJECT / "TFMG_HEAVY_ELECTRICAL_REDESIGN_AUDIT.plan.json"
DEFAULT_AUTOMATIC_PLAN = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
DEFAULT_AUTOMATIC_SNAPSHOT = PROJECT / "build-current-audit/managed.json"
DEFAULT_CATALOG = WORKSPACE / "outputs/recipe-catalog-current/recipe_catalog.sqlite"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
DEFAULT_PHYSICAL_TIERS = PROJECT / "progression/physical_recipe_tiers.json"
GENERATOR = TOOLS / "generate_managed_recipe_overhaul.py"

BATCH_OUTPUTS = [
    "tfmg:centrifuge",
    "tfmg:diesel_engine_cylinder",
    "tfmg:engine_cylinder",
    "tfmg:electrode_holder",
    "tfmg:transformer",
    "tfmg:voltage_observer",
    "createaddition:digital_adapter",
    "createaddition:portable_energy_interface",
]

BATCH_IDS = {
    "industrial_colonies:tfmg_heavy_electrical/centrifuge",
    "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder",
    "industrial_colonies:tfmg_heavy_electrical/engine_cylinder",
    "industrial_colonies:tfmg_heavy_electrical/electrode_holder",
    "industrial_colonies:tfmg_heavy_electrical/transformer",
    "industrial_colonies:tfmg_heavy_electrical/voltage_observer",
    "industrial_colonies:tfmg_heavy_electrical/digital_adapter",
    "industrial_colonies:tfmg_heavy_electrical/portable_energy_interface",
}

AUTOMATIC_IDS = {
    "industrial_colonies:auto/tfmg/centrifuge",
    "industrial_colonies:auto/tfmg/diesel_engine_cylinder",
    "industrial_colonies:auto/tfmg/engine_cylinder",
    "industrial_colonies:auto/tfmg/electrode_holder",
    "industrial_colonies:auto/tfmg/transformer",
    "industrial_colonies:auto/tfmg/voltage_observer",
    "industrial_colonies:auto/createaddition/digital_adapter",
    "industrial_colonies:auto/createaddition/portable_energy_interface",
}

SOURCE_IDS = {
    "tfmg:crafting/materials/centrifuge",
    "tfmg:engine_cylinder",
    "tfmg:engine_cylinder_spark_plug",
    "tfmg:engine_cylinder_gas",
    "tfmg:crafting/materials/electrode_holder",
    "tfmg:crafting/materials/transformer",
    "tfmg:crafting/materials/voltage_observer",
    "createaddition:crafting/digital_adapter",
    "createaddition:crafting/portable_energy_interface",
}

EXPECTED_MACHINES = {
    "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder": "createcasing:railway_press",
    "industrial_colonies:tfmg_heavy_electrical/engine_cylinder": "createcasing:railway_press",
    "industrial_colonies:tfmg_heavy_electrical/electrode_holder": "createcasing:railway_press",
    "industrial_colonies:tfmg_heavy_electrical/portable_energy_interface": "createcasing:copper_press",
    "industrial_colonies:tfmg_heavy_electrical/digital_adapter": "createcasing:brass_press",
    "industrial_colonies:tfmg_heavy_electrical/transformer": "createcasing:copper_press",
    "industrial_colonies:tfmg_heavy_electrical/voltage_observer": "createcasing:copper_press",
}

EXPECTED_NODES = {
    "industrial_colonies:tfmg_heavy_electrical/centrifuge": "CR01 — Chemical Processing",
    "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder": "CR01 — Diesel Engines",
    "industrial_colonies:tfmg_heavy_electrical/engine_cylinder": "CR01 — Diesel Engines",
    "industrial_colonies:tfmg_heavy_electrical/electrode_holder": "CR01 — Electronics Manufacturing",
    "industrial_colonies:tfmg_heavy_electrical/portable_energy_interface": "CR01 — Early Power Cables",
    "industrial_colonies:tfmg_heavy_electrical/digital_adapter": "CR01 — Early Electronics",
    "industrial_colonies:tfmg_heavy_electrical/transformer": "CR01 — Control Electronics",
    "industrial_colonies:tfmg_heavy_electrical/voltage_observer": "CR01 — Control Electronics",
}
EXPECTED_PHASES = {
    "industrial_colonies:tfmg_heavy_electrical/centrifuge": "Steel & Petroleum",
    "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder": "Steel & Petroleum",
    "industrial_colonies:tfmg_heavy_electrical/engine_cylinder": "Steel & Petroleum",
    "industrial_colonies:tfmg_heavy_electrical/electrode_holder": "Electrical Manufacturing",
    "industrial_colonies:tfmg_heavy_electrical/portable_energy_interface": "Electrical Manufacturing",
    "industrial_colonies:tfmg_heavy_electrical/digital_adapter": "Digital Logistics",
    "industrial_colonies:tfmg_heavy_electrical/transformer": "Electrical Manufacturing",
    "industrial_colonies:tfmg_heavy_electrical/voltage_observer": "Electrical Manufacturing",
}

EXPECTED_REMOVALS = {
    "tfmg:crafting/materials/centrifuge",
    "tfmg:engine_cylinder",
    "tfmg:engine_cylinder_spark_plug",
    "tfmg:crafting/materials/electrode_holder",
    "createaddition:crafting/portable_energy_interface",
    "createaddition:crafting/digital_adapter",
    "tfmg:crafting/materials/transformer",
    "tfmg:crafting/materials/voltage_observer",
}

EXPECTED_CENTRIFUGE_PATTERN = [" AFA ", "ARBRA", "FSCSF", "ARBRA", " AFA "]
EXPECTED_DIESEL_COMPONENTS = (
    '[tfmg:fuel_tags={"diesel":"c:diesel"},'
    'tfmg:fuels={"diesel":"fluid.tfmg.diesel"}]'
)
EXPECTED_SPARK_COMPONENTS = (
    '[tfmg:fuel_tags={"gasoline":"c:gasoline","kerosene":"c:kerosene",'
    '"naphtha":"c:naphtha"},tfmg:fuels={"gasoline":"Gasoline",'
    '"kerosene":"Kerosene","naphtha":"Naphtha"}]'
)
EXPECTED_LPG_COMPONENTS = (
    '[tfmg:fuel_tags={"lpg":"c:lpg"},tfmg:fuels={"lpg":"LPG"}]'
)

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
    recipe_type = raw.get("type")
    if recipe_type == "minecraft:crafting_shaped":
        pattern = raw.get("pattern")
        key = raw.get("key")
        if not isinstance(pattern, list) or not isinstance(key, dict):
            raise ValueError(f"{label} has invalid shaped data")
        result: Counter[str] = Counter()
        for row in pattern:
            if not isinstance(row, str):
                raise ValueError(f"{label} has a non-string pattern row")
            for symbol in row:
                if symbol == " ":
                    continue
                if symbol not in key:
                    raise ValueError(f"{label} has an unknown key symbol {symbol!r}")
                result[ingredient_ref(key[symbol], label)] += 1
        return result
    if recipe_type == "minecraft:crafting_shapeless":
        values = raw.get("ingredients")
        if not isinstance(values, list):
            raise ValueError(f"{label} has invalid shapeless data")
        return Counter(ingredient_ref(value, label) for value in values)
    raise ValueError(f"{label} uses unsupported evidence type {recipe_type!r}")


def source_result(raw: dict[str, Any], label: str) -> tuple[str, int, str | None]:
    result = raw.get("result")
    if not isinstance(result, dict) or not isinstance(result.get("id"), str):
        raise ValueError(f"{label} has invalid result data")
    count = result.get("count", 1)
    if not isinstance(count, int) or count < 1:
        raise ValueError(f"{label} has invalid result count")
    components = result.get("components")
    encoded = (
        manifest_builder.component_string(components, label)
        if components is not None
        else None
    )
    return result["id"], count, encoded


def recipe_output_id(recipe: dict[str, Any]) -> str:
    return patch_builder.output_id(recipe)


def contracts_by_id(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return patch_builder.contracts_by_id(plan)


def input_refs(contract: dict[str, Any]) -> list[str]:
    if contract.get("type") == "compacting":
        values = contract.get("inputs", [])
        if not isinstance(values, list):
            raise ValueError(f"{contract.get('id')} inputs must be an array")
        return [split_ref(str(value))[1] for value in values]
    if contract.get("type") == "mechanical_crafting":
        pattern = contract.get("pattern", [])
        key = contract.get("key", {})
        if not isinstance(pattern, list) or not isinstance(key, dict):
            raise ValueError(f"{contract.get('id')} has invalid mechanical data")
        refs: list[str] = []
        for row in pattern:
            for symbol in str(row):
                if symbol != " ":
                    refs.append(split_ref(str(key[symbol]))[1])
        return refs
    raise ValueError(f"{contract.get('id')} uses unsupported type")


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

    jars = plan.get("installed_jars", [])
    if not isinstance(jars, list) or {value.get("name") for value in jars} != {
        "tfmg-1.2.0.jar",
        "createaddition-1.6.0.jar",
    }:
        failures.append("installed JAR evidence must name exactly TFMG and CreateAddition")
        return
    opened: dict[str, zipfile.ZipFile] = {}
    try:
        for evidence in jars:
            name = evidence.get("name")
            path = find_jar(mods, str(name))
            if sha256_file(path) != evidence.get("sha256"):
                failures.append(f"installed JAR hash changed: {name}")
            opened[str(name)] = zipfile.ZipFile(path)

        source_rows = plan.get("source_recipes", [])
        if not isinstance(source_rows, list) or {row.get("id") for row in source_rows} != SOURCE_IDS:
            failures.append("source recipe inventory must contain the eight owners plus LPG parity")
            return
        for row in source_rows:
            identity = str(row.get("id"))
            jar = opened.get(str(row.get("jar")))
            path = str(row.get("path"))
            if jar is None or path not in jar.namelist():
                failures.append(f"installed source recipe is absent: {identity}")
                continue
            payload = jar.read(path)
            if sha256_bytes(payload) != row.get("sha256"):
                failures.append(f"installed source JSON hash changed: {identity}")
                continue
            raw = json.loads(payload)
            if raw.get("type") != row.get("type"):
                failures.append(f"installed source recipe type changed: {identity}")
            actual_output, actual_count, actual_components = source_result(raw, identity)
            if actual_output != row.get("output") or actual_count != row.get("output_count"):
                failures.append(f"installed source result changed: {identity}")
            expected_components = row.get("output_components")
            if actual_components != expected_components:
                failures.append(f"installed source item components changed: {identity}")
            actual_ingredients = source_ingredient_counts(raw, identity)
            expected_ingredients = Counter(row.get("stock_ingredient_counts", {}))
            if actual_ingredients != expected_ingredients:
                failures.append(f"installed source ingredients changed: {identity}")

        gas = next((row for row in source_rows if row.get("id") == "tfmg:engine_cylinder_gas"), {})
        if gas.get("disposition") != "retain_stateful_downstream_variant":
            failures.append("LPG cylinder recipe is not explicitly retained as a downstream variant")
        if gas.get("output_components") != EXPECTED_LPG_COMPONENTS:
            failures.append("LPG cylinder components drifted")
    finally:
        for jar in opened.values():
            jar.close()

    required = plan.get("required_concrete_items", [])
    if not isinstance(required, list) or len(required) != len(set(required)):
        failures.append("required concrete item inventory must be unique")
        return
    catalog_required = [value for value in required if not value.startswith("minecraft:")]
    connection = sqlite3.connect(catalog)
    try:
        found = {
            row[0]
            for row in connection.execute(
                f"select item_id from items where item_id in ({','.join('?' for _ in catalog_required)})",
                catalog_required,
            )
        }
        missing = sorted(set(catalog_required) - found)
        if missing:
            failures.append(f"concrete recipe items are absent from installed catalog: {missing}")
        machines = plan.get("machine_capability_audit", {}).get("approved_exact_machines", [])
        found_machines = {
            row[0]
            for row in connection.execute(
                f"select item_id from items where item_id in ({','.join('?' for _ in machines)})",
                machines,
            )
        }
        if found_machines != set(machines):
            failures.append("one or more approved exact Create Encased machines are absent")
    finally:
        connection.close()


def validate_automatic_evidence(
    plan: dict[str, Any], automatic_plan: dict[str, Any], snapshot_path: Path,
    failures: list[str],
) -> None:
    scope = plan.get("scope", {})
    if sha256_file(snapshot_path) != scope.get("automatic_snapshot_sha256"):
        failures.append("pinned automatic managed snapshot hash changed")
        return
    batches = automatic_plan.get("implementation_batches", [])
    first = next((value for value in batches if value.get("id") == "tfmg_first_heavy_and_electrical"), None)
    if first is None:
        failures.append("priority-one automatic redesign batch is absent")
        return
    if first.get("priority") != 1 or first.get("outputs") != BATCH_OUTPUTS:
        failures.append("priority-one automatic redesign output order changed")
    if set(first.get("managed_ids", [])) != AUTOMATIC_IDS:
        failures.append("priority-one automatic owner set changed")

    current = plan.get("current_automatic_owners", [])
    if not isinstance(current, list) or {row.get("managed_id") for row in current} != AUTOMATIC_IDS:
        failures.append("current automatic-owner evidence must contain exactly eight ids")
        return
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
        identity = row["managed_id"]
        recipe = recipes[identity]
        if recipe.get("type") != "mechanical_crafting":
            failures.append(f"automatic owner is no longer mechanical crafting: {identity}")
        if recipe_output_id(recipe) != row.get("output"):
            failures.append(f"automatic owner output changed: {identity}")
        if row.get("source_recipe_id") not in recipe.get("remove", []):
            failures.append(f"automatic owner source evidence changed: {identity}")

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
        failures.append("automatic quality audit no longer classifies all eight generic owners for redesign")


def validate_capability_order(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers_path: Path, failures: list[str],
) -> None:
    scope = plan.get("scope", {})
    if scope.get("physical_tiers") != "progression/physical_recipe_tiers.json":
        failures.append("physical tier authority path metadata changed")
    if sha256_file(physical_tiers_path) != scope.get("physical_tiers_sha256"):
        failures.append("physical tier authority hash changed")
    physical = load_json(physical_tiers_path)
    gate_policy = physical.get("gate_policy", {})
    if gate_policy.get("minecolonies") is not False or gate_policy.get("ftb_quests") is not False:
        failures.append("physical recipes are no longer the progression authority")

    actual_family_phases = {
        family.get("tier"): family.get("phase")
        for family in seed.get("machine_families", [])
        if family.get("tier") in {"copper", "brass", "railway", "industrial_iron"}
    }
    expected = plan.get("machine_capability_audit", {}).get("machine_family_phases", {})
    if actual_family_phases != expected:
        failures.append(f"Create Encased machine-family phase evidence changed: {actual_family_phases}")

    contracts = contracts_by_id(plan)
    forbidden = set(plan.get("machine_capability_audit", {}).get("forbidden_in_this_batch", []))
    for identity, contract in contracts.items():
        node = contract.get("node")
        phase = contract.get("phase")
        if node != EXPECTED_NODES.get(identity):
            failures.append(f"{identity}: reviewed node placement changed")
        if phase != EXPECTED_PHASES.get(identity):
            failures.append(f"{identity}: reviewed phase placement changed")
        if seed.get("phase_by_node", {}).get(node) != phase:
            failures.append(f"{identity}: node and phase are inconsistent")
        machine = contract.get("machine")
        if machine in forbidden:
            failures.append(f"{identity}: machine environment is downstream of the batch")

    move = plan.get("assignment_patch", {})
    expected_move = {
        "move_output": "tfmg:engine_cylinder",
        "from_node": "CR01 — Early Combusion Engines",
        "to_node": "CR01 — Diesel Engines",
        "insert_after": "tfmg:diesel_engine_cylinder",
    }
    if any(move.get(field) != value for field, value in expected_move.items()):
        failures.append("engine-cylinder assignment patch contract changed")
        return
    source = patch_builder.assignment_unlocks(assignments, str(move.get("from_node")))
    target = patch_builder.assignment_unlocks(assignments, str(move.get("to_node")))
    value = move.get("move_output")
    after = move.get("insert_after")
    if value in source or target.count(value) != 1 or target.count(after) != 1:
        failures.append("engine-cylinder assignment move is not implemented exactly")
    elif target.index(value) != target.index(after) + 1:
        failures.append("engine-cylinder assignment move is not immediately after its diesel predecessor")


def require_inputs(
    contract: dict[str, Any], required: set[str], forbidden: set[str], failures: list[str]
) -> None:
    refs = set(input_refs(contract))
    identity = contract["id"]
    missing = sorted(required - refs)
    present_forbidden = sorted(forbidden & refs)
    if missing:
        failures.append(f"{identity}: missing required TFMG-first inputs {missing}")
    if present_forbidden:
        failures.append(f"{identity}: contains forbidden substitute inputs {present_forbidden}")


def validate_contracts(plan: dict[str, Any], failures: list[str]) -> None:
    contracts = contracts_by_id(plan)
    if set(contracts) != BATCH_IDS:
        failures.append("replacement contract id set drifted")
        return
    if {recipe_output_id(value) for value in contracts.values()} != set(BATCH_OUTPUTS):
        failures.append("replacement contract output set drifted")
    if Counter(value.get("type") for value in contracts.values()) != Counter(
        {"compacting": 7, "mechanical_crafting": 1}
    ):
        failures.append("batch must remain seven exact presses plus one unique 5x5 assembly")

    actual_machines = {
        identity: contract.get("machine")
        for identity, contract in contracts.items()
        if contract.get("type") == "compacting"
    }
    if actual_machines != EXPECTED_MACHINES:
        failures.append("exact machine-role mapping changed")
    if sum(len(value.get("remove", [])) for value in contracts.values()) != 8:
        failures.append("batch must remove exactly eight installed source recipes")
    removals = [item for value in contracts.values() for item in value.get("remove", [])]
    if len(removals) != len(set(removals)):
        failures.append("exact source removals contain duplicates")
    if set(removals) != EXPECTED_REMOVALS:
        failures.append("exact source removal set drifted")
    if "tfmg:engine_cylinder_gas" in removals:
        failures.append("LPG cylinder parity recipe must remain installed")

    centrifuge = contracts["industrial_colonies:tfmg_heavy_electrical/centrifuge"]
    if centrifuge.get("pattern") != EXPECTED_CENTRIFUGE_PATTERN:
        failures.append("centrifuge no longer uses the reviewed radial 5x5 structure")
    if len(set("".join(centrifuge.get("pattern", [])).replace(" ", ""))) < 6:
        failures.append("centrifuge collapsed toward a generic gate-ring recipe")
    if centrifuge.get("machine") is not None:
        failures.append("centrifuge 5x5 assembly must not pretend to have an encased process machine")

    diesel = contracts["industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder"]
    spark = contracts["industrial_colonies:tfmg_heavy_electrical/engine_cylinder"]
    if not isinstance(diesel.get("output"), dict) or diesel["output"].get("components") != EXPECTED_DIESEL_COMPONENTS:
        failures.append("diesel cylinder lost its exact TFMG fuel components")
    if not isinstance(spark.get("output"), dict) or spark["output"].get("components") != EXPECTED_SPARK_COMPONENTS:
        failures.append("spark-ignition cylinder lost its exact TFMG fuel components")
    if spark.get("exclusive_output") is not False:
        failures.append("spark-ignition cylinder must be nonexclusive so LPG conversion survives")
    if spark.get("retained_same_output_recipe") != "tfmg:engine_cylinder_gas":
        failures.append("spark-ignition cylinder does not document retained LPG parity")

    require_inputs(
        contracts["industrial_colonies:tfmg_heavy_electrical/portable_energy_interface"],
        {"tfmg:copper_spool", "tfmg:cable_connector", "create:precision_mechanism"},
        {"createaddition:copper_spool", "createaddition:connector"}, failures,
    )
    require_inputs(
        contracts["industrial_colonies:tfmg_heavy_electrical/digital_adapter"],
        {"computercraft:wired_modem", "tfmg:circuit_board", "tfmg:copper_wire"},
        {"mekanism:basic_control_circuit", "ae2:logic_processor"}, failures,
    )
    require_inputs(
        contracts["industrial_colonies:tfmg_heavy_electrical/transformer"],
        {"tfmg:copper_spool", "tfmg:magnetic_alloy_sheet", "tfmg:steel_casing"},
        {"createaddition:copper_spool", "electroenergetics:transformer"}, failures,
    )
    transformer_refs = input_refs(contracts["industrial_colonies:tfmg_heavy_electrical/transformer"])
    if transformer_refs.count("tfmg:copper_spool") != 2:
        failures.append("transformer must retain matched TFMG primary and secondary spools")
    require_inputs(
        contracts["industrial_colonies:tfmg_heavy_electrical/voltage_observer"],
        {"tfmg:circuit_board", "tfmg:transistor_item", "tfmg:capacitor_item", "tfmg:copper_wire"},
        {"mekanism:basic_control_circuit", "ae2:logic_processor"}, failures,
    )
    require_inputs(
        diesel,
        {"tfmg:cast_iron_frame", "tfmg:steel_mechanism"},
        {"tfmg:diesel_engine_cylinder", "tfmg:engine_cylinder", "tfmg:transformer"}, failures,
    )
    require_inputs(
        spark,
        {"tfmg:diesel_engine_cylinder", "tfmg:spark_plug", "tfmg:copper_wire"},
        {"tfmg:engine_cylinder", "tfmg:transformer"}, failures,
    )

    batch_output_to_id = {recipe_output_id(value): identity for identity, value in contracts.items()}
    for identity, contract in contracts.items():
        refs = input_refs(contract)
        if recipe_output_id(contract) in refs:
            failures.append(f"{identity}: recipe consumes its own output")
        if any(ref.startswith(("mekanism:", "ae2:", "bigreactors:")) for ref in refs):
            failures.append(f"{identity}: recipe jumps to a downstream technology family")
        for value in contract.get("inputs", []):
            count, ref = split_ref(str(value))
            if count > 1 and ref.startswith("#"):
                failures.append(f"{identity}: counted tag syntax is forbidden")
        observed_batch = {
            batch_output_to_id[ref]
            for ref in refs
            if ref in batch_output_to_id
        }
        declared_batch = set(contract.get("depends_on", [])) & set(contracts)
        if observed_batch != declared_batch:
            failures.append(
                f"{identity}: same-batch dependency mismatch, observed={sorted(observed_batch)}, "
                f"declared={sorted(declared_batch)}"
            )


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("tfmg_heavy_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load managed recipe compiler: {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        failures.append("implementation-report builder does not declare the implemented no-op state")
    if first.get("seed", {}).get("append_recipes") != []:
        failures.append("implemented report must not propose appending recipes again")

    try:
        staged_seed, staged_assignments = patch_builder.apply_patch_to_copies(
            plan, seed, assignments, physical_tiers
        )
    except patch_builder.PatchPlanError as error:
        failures.append(f"in-memory patch application failed: {error}")
        return
    staged_ids = patch_builder.recipes_by_id(staged_seed)
    if not BATCH_IDS <= set(staged_ids):
        failures.append("in-memory seed is missing one or more reviewed contracts")
    if "tfmg:engine_cylinder" in staged_seed.get("source_recipe_overrides", {}):
        failures.append("in-memory seed retained the conflicting engine-cylinder source override")
    move = plan["assignment_patch"]
    source = patch_builder.assignment_unlocks(staged_assignments, move["from_node"])
    target = patch_builder.assignment_unlocks(staged_assignments, move["to_node"])
    value = move["move_output"]
    after = move["insert_after"]
    if value in source or target.index(value) != target.index(after) + 1:
        failures.append("in-memory assignment move did not place the spark cylinder after its diesel predecessor")

    if not compile_batch:
        return
    with tempfile.TemporaryDirectory(prefix="tfmg-heavy-electrical-audit-") as temporary:
        root = Path(temporary)
        seed_path = root / "seed.json"
        assignments_path = root / "assignments.json"
        manifest_path = root / "managed.json"
        report_path = root / "report.json"
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
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        fatal = report.get("fatal_errors", [])
        if fatal:
            failures.append(f"in-memory managed manifest reported fatal errors: {fatal}")
            return
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
    expected_types = Counter(plan["compiled_contract"]["expected_card_type_counts"])
    actual_types = Counter(value.get("type") for value in cards)
    if actual_types != expected_types:
        failures.append(f"compiled batch card types drifted: {dict(actual_types)}")
    actual_machines = Counter()
    for card in cards:
        if card.get("type") != "kjsgen:create_compacting":
            continue
        slot = card.get("slots", {}).get("__machine_process_compacting", {})
        actual_machines[slot.get("id")] += 1
    if actual_machines != Counter(plan["compiled_contract"]["expected_exact_machine_counts"]):
        failures.append(f"compiled exact-machine counts drifted: {dict(actual_machines)}")

    by_id = {value.get("recipeId"): value for value in cards}
    diesel_slot = by_id[
        "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder"
    ].get("slots", {}).get("output", {})
    spark_slot = by_id[
        "industrial_colonies:tfmg_heavy_electrical/engine_cylinder"
    ].get("slots", {}).get("output", {})
    if diesel_slot.get("components") != EXPECTED_DIESEL_COMPONENTS:
        failures.append("compiled diesel-cylinder components drifted")
    if spark_slot.get("components") != EXPECTED_SPARK_COMPONENTS:
        failures.append("compiled spark-cylinder components drifted")

    removals = {
        value.get("recipeId")
        for value in compiled.get("removals", [])
        if value.get("recipeId")
    }
    expected_removals = {
        item
        for contract in plan["replacement_contracts"]
        for item in contract.get("remove", [])
    }
    if not expected_removals <= removals:
        failures.append("compiled output is missing one or more exact source removals")
    if "tfmg:engine_cylinder_gas" in removals:
        failures.append("compiled output accidentally removes the retained LPG cylinder recipe")


def validate_plan(
    plan: dict[str, Any], automatic_plan: dict[str, Any], automatic_snapshot: Path,
    catalog: Path, mods: Path, seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers: Path, *, compile_batch: bool = True,
) -> list[str]:
    failures: list[str] = []
    if plan.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        failures.append("status must be implemented_in_seed")
    if plan.get("decision") != "GO_WITH_EIGHT_SOURCE_OWNED_CONTRACTS_AND_RESTORE_LPG_VARIANT":
        failures.append("audit decision changed")
    scope = plan.get("scope", {})
    expected_scope = {
        "outputs": 8,
        "source_owned_contracts": 8,
        "automatic_owners_retired": 8,
        "exact_recipe_removals": 8,
        "stateful_stock_variants_retained": 1,
        "assignment_moves": 1,
    }
    for field, expected in expected_scope.items():
        if scope.get(field) != expected:
            failures.append(f"scope.{field} must be {expected}")
    result = plan.get("validation_result", {})
    expected_result = {
        "status": "passed_implemented",
        "source_recipes_verified": 9,
        "contracts_compiled": 8,
        "compiled_exact_removals": 8,
        "retained_stateful_variants": 1,
        "isolated_manifest_recipes": 385,
        "isolated_automatic_recipes": 164,
        "isolated_compiled_cards": 453,
        "isolated_exact_removals": 738,
        "managed_dependency_warnings": 0,
        "mutation_tests": 33,
        "shared_progression_files_modified": 2,
    }
    for field, expected in expected_result.items():
        if result.get(field) != expected:
            failures.append(f"validation_result.{field} must be {expected}")
    if result.get("compiled_machine_counts") != {
        "createcasing:brass_press": 1,
        "createcasing:copper_press": 3,
        "createcasing:railway_press": 3,
    }:
        failures.append("validation_result.compiled_machine_counts drifted")
    seed_implementation = plan.get("seed_implementation", {})
    if (
        seed_implementation.get("status") != "source_owned"
        or seed_implementation.get("authoritative_source") != "progression/managed_recipe_overhaul.seed.json"
        or seed_implementation.get("recipe_count") != 8
        or seed_implementation.get("recipe_ids") != plan.get("seed_patch_contract", {}).get("append_recipe_ids")
        or seed_implementation.get("automatic_owners_retired") != 8
        or seed_implementation.get("exact_stock_sources_retired") != 8
        or seed_implementation.get("source_recipe_override_removed") != "tfmg:engine_cylinder"
        or seed_implementation.get("retained_stock_recipe") != "tfmg:engine_cylinder_gas"
        or seed_implementation.get("authoritative_generated_artifacts") != "intentionally_not_regenerated_by_batch_owner"
    ):
        failures.append("seed_implementation metadata is incomplete or stale")
    assignment_implementation = plan.get("assignment_implementation", {})
    expected_assignment_implementation = {
        "status": "moved_after_predecessor",
        "authoritative_source": "progression/machine_node_assignments.json",
        "move_output": "tfmg:engine_cylinder",
        "from_node": "CR01 — Early Combusion Engines",
        "to_node": "CR01 — Diesel Engines",
        "insert_after": "tfmg:diesel_engine_cylinder",
        "move_count": 1,
    }
    if assignment_implementation != expected_assignment_implementation:
        failures.append("assignment_implementation metadata is incomplete or stale")
    validate_installed_evidence(plan, catalog, mods, failures)
    validate_automatic_evidence(plan, automatic_plan, automatic_snapshot, failures)
    validate_capability_order(plan, seed, assignments, physical_tiers, failures)
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
    parser.add_argument("--no-compile", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        failures = validate_plan(
            load_json(args.plan.resolve()),
            load_json(args.automatic_plan.resolve()),
            args.automatic_snapshot.resolve(),
            args.catalog.resolve(),
            args.mods.resolve(),
            load_json(args.seed.resolve()),
            load_json(args.assignments.resolve()),
            args.physical_tiers.resolve(),
            compile_batch=not args.no_compile,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, sqlite3.Error, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if failures:
        print(f"TFMG heavy/electrical redesign audit failed ({len(failures)} issue(s)):")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "TFMG heavy/electrical redesign audit passed: 9 installed source recipes verified; "
        "8 generic automatic owners deterministically become 7 exact press recipes plus one "
        "radial 5x5 centrifuge; 8 exact source recipes are removed, the LPG cylinder variant "
        "survives, TFMG state components are preserved, and the assignment DAG is corrected."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
