#!/usr/bin/env python3
"""Validate the source-owned Analog High-Voltage Repair implementation.

The validator reads the installed Electro Energetics JAR, the static catalog,
project topology, and authoritative recipe seed. It never writes the recipe
seed, generated output, live pack, quests, or deployment artifacts.
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
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "HIGH_VOLTAGE_REPAIR_AUDIT.plan.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
ENVIRONMENTS = PROJECT / "src/main/resources/data/industrial_colonies/tier_recipe_environments.json"
POWER_PLAN = PROJECT / "POWER_BACKBONE_AUDIT.plan.json"
EXTREME_PLAN = PROJECT / "EXTREME_TRANSMISSION_AUDIT.plan.json"

RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^#[a-z0-9_.-]+:[a-z0-9_./-]+$")
COUNTED_REF = re.compile(r"^(?:(\d+)x\s+)?(.+)$")


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


def contract_output(contract: dict[str, Any]) -> str:
    if contract.get("output"):
        return split_ref(str(contract["output"]))[1]
    outputs = contract.get("outputs", [])
    if len(outputs) != 1 or not isinstance(outputs[0], dict):
        raise ValueError(f"{contract.get('id')}: expected exactly one output contract")
    return str(outputs[0].get("id", ""))


def contract_refs(contract: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for field in ("input", "transitional", "returned_tool"):
        if contract.get(field):
            yield field, str(contract[field])
    for index, value in enumerate(contract.get("inputs", [])):
        yield f"inputs[{index}]", str(value)
    for symbol, value in contract.get("key", {}).items():
        yield f"key.{symbol}", str(value)
    if contract.get("machine"):
        yield "machine", str(contract["machine"])
    for index, step in enumerate(contract.get("steps", [])):
        if step.get("ingredient"):
            yield f"steps[{index}].ingredient", str(step["ingredient"])
        if step.get("machine"):
            yield f"steps[{index}].machine", str(step["machine"])


def validate_pattern(contract: dict[str, Any], failures: list[str]) -> None:
    pattern = contract.get("pattern")
    if pattern is None:
        return
    identity = contract.get("id")
    if not isinstance(pattern, list) or not pattern or not all(isinstance(row, str) for row in pattern):
        failures.append(f"{identity}: pattern must be a nonempty string array")
        return
    widths = {len(row) for row in pattern}
    if len(widths) != 1:
        failures.append(f"{identity}: pattern rows are not rectangular: {sorted(widths)}")
    if contract.get("type") == "mechanical_crafting" and (len(pattern) < 4 or max(widths) < 4):
        failures.append(f"{identity}: high-voltage machine is not a large mechanical-crafting layout")
    used = {char for row in pattern for char in row if char != " "}
    keys = set(contract.get("key", {}))
    if used != keys:
        failures.append(
            f"{identity}: pattern/key mismatch, missing={sorted(used - keys)}, unused={sorted(keys - used)}"
        )


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


def raw_recipe_output_ids(document: dict[str, Any]) -> set[str]:
    outputs: set[str] = set()
    result = document.get("result")
    if isinstance(result, dict) and isinstance(result.get("id"), str):
        outputs.add(result["id"])
    for result in document.get("results", []):
        if isinstance(result, dict) and isinstance(result.get("id"), str):
            outputs.add(result["id"])
    return outputs


def seed_output_ids(recipe: dict[str, Any]) -> set[str]:
    outputs: set[str] = set()
    if recipe.get("output"):
        value = recipe["output"]
        if isinstance(value, str):
            outputs.add(split_ref(value)[1])
        elif isinstance(value, dict) and isinstance(value.get("id"), str):
            outputs.add(value["id"])
    for value in recipe.get("outputs", []):
        if isinstance(value, dict) and isinstance(value.get("id"), str):
            outputs.add(value["id"])
    return outputs


def validate_seed_implementation(plan: dict[str, Any], seed: dict[str, Any]) -> list[str]:
    """Check that the authoritative seed implements exactly the seven contracts."""

    failures: list[str] = []
    contracts = plan.get("replacement_contracts", [])
    implementation = plan.get("seed_implementation", {})
    if implementation.get("status") != "source_owned":
        failures.append("seed implementation status must be source_owned")
    if implementation.get("authoritative_source") != "progression/managed_recipe_overhaul.seed.json":
        failures.append("seed implementation authority path drifted")
    if implementation.get("generated_artifacts") != "intentionally_not_regenerated":
        failures.append("generated-artifact migration state must remain explicit")
    if implementation.get("recipe_count") != 7:
        failures.append("seed implementation must declare exactly seven recipes")

    recipes = [recipe for recipe in seed.get("recipes", []) if isinstance(recipe, dict)]
    recipes_by_id: dict[str, list[dict[str, Any]]] = {}
    output_owners: dict[str, list[str]] = {}
    for recipe in recipes:
        identity = recipe.get("id")
        if isinstance(identity, str):
            recipes_by_id.setdefault(identity, []).append(recipe)
            for output in seed_output_ids(recipe):
                output_owners.setdefault(output, []).append(identity)

    seed_orders = implementation.get("seed_orders", {})
    expected_ids = {str(contract.get("id", "")) for contract in contracts}
    if set(seed_orders) != expected_ids:
        failures.append("seed order map must cover exactly the seven replacement IDs")

    expected_removals: set[str] = set()
    expected_transitionals: set[str] = set()
    for contract in contracts:
        identity = str(contract.get("id", ""))
        matches = recipes_by_id.get(identity, [])
        if len(matches) != 1:
            failures.append(f"{identity}: expected exactly one authoritative seed recipe, found {len(matches)}")
            continue
        recipe = matches[0]
        if recipe.get("order") != seed_orders.get(identity):
            failures.append(
                f"{identity}: seed order drifted, expected {seed_orders.get(identity)}, got {recipe.get('order')}"
            )
        for field in (
            "phase",
            "type",
            "machine",
            "input",
            "inputs",
            "outputs",
            "output",
            "transitional",
            "loops",
            "steps",
            "pattern",
            "key",
            "exclusive_output",
        ):
            if recipe.get(field) != contract.get(field):
                failures.append(f"{identity}: seed field {field!r} does not match the approved contract")
        removals = recipe.get("remove", [])
        approved_removals = contract.get("remove_exact", [])
        if removals != approved_removals:
            failures.append(f"{identity}: seed removal is not its one exact approved stock recipe")
        expected_removals.update(str(value) for value in approved_removals)
        transitional = recipe.get("transitional")
        if isinstance(transitional, str):
            expected_transitionals.add(transitional)

        try:
            output = contract_output(contract)
        except ValueError as error:
            failures.append(str(error))
            continue
        owners = output_owners.get(output, [])
        if owners != [identity]:
            failures.append(f"{identity}: output {output} has seed owners {owners}, expected only this recipe")

    actual_removals = {
        str(removal)
        for identity in expected_ids
        for recipe in recipes_by_id.get(identity, [])
        for removal in recipe.get("remove", [])
    }
    if actual_removals != expected_removals or len(actual_removals) != 7:
        failures.append("authoritative seed must contain exactly the seven approved stock removals")
    if implementation.get("exact_stock_removals") != 7:
        failures.append("seed implementation exact-stock-removal count must be 7")
    if implementation.get("exclusive_output_owners") != 7:
        failures.append("seed implementation exclusive-output-owner count must be 7")

    declared_transitionals = set(implementation.get("closed_transitionals", []))
    if declared_transitionals != expected_transitionals:
        failures.append("closed transitional set does not match the two implemented sequences")
    for transitional in expected_transitionals:
        if output_owners.get(transitional):
            failures.append(f"craftable transitional leaked into seed ownership: {transitional}")

    follow_up_ids = set(
        plan.get("extreme_transmission_follow_up", {}).get("replacement_recipe_ids", [])
    )
    present_follow_up = follow_up_ids & set(recipes_by_id)
    if present_follow_up != follow_up_ids:
        failures.append(
            "separately implemented Extreme Transmission seed IDs are incomplete: "
            f"{sorted(follow_up_ids - present_follow_up)}"
        )

    return failures


def find_ee_jar(mods: Path) -> Path:
    matches = sorted(mods.glob("electroenergetics-*.jar"))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one Electro Energetics JAR in {mods}, found {len(matches)}")
    return matches[0]


def validate_plan(plan: dict[str, Any], catalog: Path, mods: Path) -> list[str]:
    failures: list[str] = []
    if plan.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        failures.append("audit status must be implemented_in_seed")

    scope = plan.get("scope", {})
    contracts = plan.get("replacement_contracts", [])
    sources = plan.get("source_recipes", [])
    if scope.get("replacement_count") != 7 or len(contracts) != 7 or len(sources) != 7:
        failures.append("the Analog High-Voltage Repair must contain exactly seven source/replace contracts")
    if scope.get("extreme_transmission_in_scope") is not False:
        failures.append("Extreme Power Transmission must remain outside this batch")

    item_rows = load_rows(catalog / "items.csv")
    recipe_rows = load_rows(catalog / "recipes.csv")
    items = {row["item_id"] for row in item_rows}
    catalog_recipes = {row["recipe_id"]: row for row in recipe_rows}
    assignments_document = load_json(ASSIGNMENTS)
    assignments = assignments_document.get("nodes", assignments_document)
    environment_items = collect_environment_items(load_json(ENVIRONMENTS))
    approved_machines = set(plan.get("approved_machine_environments", []))
    forbidden_namespaces = set(plan.get("ingredient_policy", {}).get("forbidden_namespaces", []))
    completed = set(plan.get("ingredient_policy", {}).get("completed_grid_components", []))
    foundations = set(plan.get("ingredient_policy", {}).get("earlier_factory_foundations", []))
    allowed_tags = set(plan.get("ingredient_policy", {}).get("allowed_tags", []))

    jar = find_ee_jar(mods)
    actual_jar_hash = hashlib.sha256(jar.read_bytes()).hexdigest().upper()
    if jar.name != scope.get("installed_mod"):
        failures.append(f"installed Electro Energetics JAR changed: {jar.name}")
    if actual_jar_hash != scope.get("installed_mod_sha256"):
        failures.append(f"installed Electro Energetics JAR hash changed: {actual_jar_hash}")

    source_ids: set[str] = set()
    with zipfile.ZipFile(jar) as archive:
        archive_names = set(archive.namelist())
        for source in sources:
            identity = str(source.get("id", ""))
            path = str(source.get("path", ""))
            source_ids.add(identity)
            if identity not in catalog_recipes:
                failures.append(f"installed source recipe is absent from catalog: {identity}")
                continue
            row = catalog_recipes[identity]
            if row.get("source_jar") != jar.name or row.get("source_path") != path:
                failures.append(f"{identity}: catalog JAR/path drifted")
            if row.get("recipe_type") != source.get("type"):
                failures.append(f"{identity}: catalog recipe type drifted")
            output = str(source.get("output", ""))
            if output not in recipe_outputs(row):
                failures.append(f"{identity}: catalog no longer reports output {output}")
            if path not in archive_names:
                failures.append(f"{identity}: JAR entry is absent: {path}")
                continue
            raw = archive.read(path)
            digest = hashlib.sha256(raw).hexdigest().upper()
            if digest != source.get("sha256"):
                failures.append(f"{identity}: installed source JSON hash changed: {digest}")
            document = json.loads(raw)
            if document.get("type") != source.get("type"):
                failures.append(f"{identity}: JAR recipe type does not match plan")
            if output not in raw_recipe_output_ids(document):
                failures.append(f"{identity}: JAR recipe no longer outputs {output}")
            transitional = source.get("transitional")
            if transitional and document.get("transitional_item", {}).get("id") != transitional:
                failures.append(f"{identity}: transitional item changed")

    contract_ids: set[str] = set()
    contract_outputs: dict[str, str] = {}
    order_by_id: dict[str, int] = {}
    previous_order = -1
    for contract in contracts:
        identity = str(contract.get("id", ""))
        try:
            output = contract_output(contract)
        except ValueError as error:
            failures.append(str(error))
            continue
        order = contract.get("batch_order")
        if not RESOURCE_ID.fullmatch(identity) or not identity.startswith("industrial_colonies:high_voltage/"):
            failures.append(f"invalid high-voltage replacement ID: {identity!r}")
        if identity in contract_ids:
            failures.append(f"duplicate replacement ID: {identity}")
        contract_ids.add(identity)
        if output in contract_outputs:
            failures.append(f"duplicate replacement output owner: {output}")
        contract_outputs[output] = identity
        if not isinstance(order, int) or order <= previous_order:
            failures.append(f"{identity}: batch_order must be strictly increasing")
        else:
            previous_order = order
            order_by_id[identity] = order
        if output not in items:
            failures.append(f"{identity}: output is absent from items.csv: {output}")
        node = str(contract.get("node", ""))
        if output not in assignments.get(node, {}).get("unlocks", []):
            failures.append(f"{identity}: {output} is not assigned to {node}")
        removals = contract.get("remove_exact", [])
        if len(removals) != 1 or removals[0] not in source_ids:
            failures.append(f"{identity}: must retire exactly its one audited source recipe")
        elif output not in recipe_outputs(catalog_recipes[removals[0]]):
            failures.append(f"{identity}: removal does not produce {output}")
        if contract.get("exclusive_output") is not True:
            failures.append(f"{identity}: source ownership must be exclusive")
        validate_pattern(contract, failures)

    produced_items = set(contract_outputs)
    for contract in contracts:
        identity = str(contract.get("id", ""))
        if identity not in order_by_id:
            continue
        declared_dependencies = set(contract.get("depends_on_batch", []))
        observed_dependencies: set[str] = set()
        for field, raw_value in contract_refs(contract):
            try:
                count, value = split_ref(raw_value)
            except ValueError as error:
                failures.append(f"{identity}: {error}")
                continue
            if count > 1 and value.startswith("#"):
                failures.append(
                    f"{identity}: counted tag syntax is not supported by KJSGen in {field}; "
                    "repeat the tag slot instead"
                )
            if field == "transitional":
                if value not in items:
                    failures.append(f"{identity}: transitional item is absent: {value}")
                continue
            is_machine = field == "machine" or field.endswith(".machine")
            if is_machine:
                if value not in approved_machines:
                    failures.append(f"{identity}: unapproved machine environment in {field}: {value}")
                if value not in environment_items or value not in items:
                    failures.append(f"{identity}: machine environment is not concrete: {value}")
                continue
            if value.startswith("#"):
                if not TAG_ID.fullmatch(value) or value not in allowed_tags:
                    failures.append(f"{identity}: unapproved tag in {field}: {value}")
                continue
            if not RESOURCE_ID.fullmatch(value) or value not in items:
                failures.append(f"{identity}: concrete ingredient is absent/invalid in {field}: {value}")
                continue
            namespace = value.split(":", 1)[0]
            if namespace in forbidden_namespaces:
                failures.append(f"{identity}: forbidden digital/cross-branch ingredient in {field}: {value}")
            if value in produced_items:
                dependency_id = contract_outputs[value]
                observed_dependencies.add(dependency_id)
                if order_by_id.get(dependency_id, sys.maxsize) >= order_by_id[identity]:
                    failures.append(f"{identity}: same-batch dependency is not earlier: {dependency_id}")
            elif value not in completed and value not in foundations:
                failures.append(f"{identity}: ingredient is outside the approved parent/foundation set: {value}")
        if observed_dependencies != declared_dependencies:
            failures.append(
                f"{identity}: depends_on_batch mismatch, observed={sorted(observed_dependencies)}, "
                f"declared={sorted(declared_dependencies)}"
            )
        for dependency in declared_dependencies:
            if dependency not in contract_ids:
                failures.append(f"{identity}: unknown batch dependency: {dependency}")

        recipe_type = contract.get("type")
        if recipe_type in {"pressing", "compacting"}:
            machine = str(contract.get("machine", ""))
            if not machine.endswith("_press"):
                failures.append(f"{identity}: {recipe_type} must use an encased press")
        if recipe_type == "sequenced_assembly":
            steps = contract.get("steps", [])
            if contract.get("loops") != 1 or not 3 <= len(steps) <= 7:
                failures.append(f"{identity}: sequence must be one moderate 3-7 operation loop")
            for step in steps:
                op = step.get("op")
                machine = str(step.get("machine", ""))
                if op == "deploying" and not machine.endswith("_deployer"):
                    failures.append(f"{identity}: deploying step is not bound to an encased deployer")
                if op == "pressing" and not machine.endswith("_press"):
                    failures.append(f"{identity}: pressing step is not bound to an encased press")

    expected_outputs = {str(source.get("output")) for source in sources}
    if set(contract_outputs) != expected_outputs:
        failures.append("source outputs and replacement outputs are not one-to-one")
    expected_removals = source_ids
    actual_removals = {
        removal
        for contract in contracts
        for removal in contract.get("remove_exact", [])
    }
    if actual_removals != expected_removals:
        failures.append("the seven exact installed source removals are incomplete or broadened")

    follow_up = plan.get("extreme_transmission_follow_up", {})
    if follow_up.get("status") != "implemented_separate_batch":
        failures.append("Extreme Power Transmission is not recorded as a separate implemented batch")
    follow_up_removals = set(follow_up.get("remove_exact", []))
    if follow_up_removals & actual_removals:
        failures.append("Extreme Power Transmission removal leaked into the analog source contract")
    power_plan = load_json(POWER_PLAN)
    upstream_deferred = next(
        (entry for entry in power_plan.get("follow_up_batches", []) if entry.get("name") == "Extreme Transmission Repair"),
        None,
    )
    if upstream_deferred is None or follow_up_removals != set(upstream_deferred.get("remove_exact", [])):
        failures.append("Extreme Transmission follow-up exact-ID set drifted from POWER_BACKBONE_AUDIT.plan.json")
    extreme_plan = load_json(EXTREME_PLAN)
    if extreme_plan.get("status") != "implemented_in_seed":
        failures.append("EXTREME_TRANSMISSION_AUDIT.plan.json is not implemented_in_seed")
    extreme_contracts = {
        str(contract.get("id")): set(contract.get("remove_exact", []))
        for contract in extreme_plan.get("replacement_contracts", [])
        if isinstance(contract, dict)
    }
    follow_up_ids = set(follow_up.get("replacement_recipe_ids", []))
    if not follow_up_ids <= set(extreme_contracts):
        failures.append("High-Voltage follow-up IDs drifted from the implemented Extreme plan")
    extreme_removals = {
        removal for identity in follow_up_ids for removal in extreme_contracts.get(identity, set())
    }
    if extreme_removals != follow_up_removals:
        failures.append("High-Voltage follow-up removals drifted from the implemented Extreme plan")

    seed = load_json(DEFAULT_SEED)
    failures.extend(validate_seed_implementation(plan, seed))
    seed_by_id = {recipe.get("id"): recipe for recipe in seed.get("recipes", []) if isinstance(recipe, dict)}
    for ownership in plan.get("seed_ownership", []):
        owner = ownership.get("managed_id")
        output = ownership.get("output")
        if owner not in seed_by_id:
            failures.append(f"authoritative seed owner is absent: {owner}")
        elif output not in seed_output_ids(seed_by_id[owner]):
            failures.append(f"authoritative seed owner {owner} no longer produces {output}")

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = load_json(args.plan)
        failures = validate_plan(plan, args.catalog.resolve(), args.mods.resolve())
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if failures:
        print(f"Analog High-Voltage Repair audit failed ({len(failures)} issue(s)):")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Analog High-Voltage Repair implementation passed: 7 exact installed EE source "
        "recipes, 7 exclusive seed owners/removals, an acyclic 10-70 ingredient order, "
        "6 verified Create Encased machine environments, 2 closed transitionals, no "
        "digital/Mekanism dependency, and the separate Extreme Transmission follow-up intact."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
