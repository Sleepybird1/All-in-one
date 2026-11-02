#!/usr/bin/env python3
"""Validate the reviewed complete Induction Matrix family and predecessor order."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import generate_managed_recipe_overhaul as generator
import validate_mekanism_factory_restoration_audit as factory_audit


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "INDUCTION_MATRIX_COMPLETION_AUDIT.plan.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
ENVIRONMENTS = PROJECT / "src/main/resources/data/industrial_colonies/tier_recipe_environments.json"
POWER_PLAN = PROJECT / "POWER_BACKBONE_AUDIT.plan.json"
FACTORY_PLAN = PROJECT / "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json"
EXPECTED_JAR = "Mekanism-1.21.1-10.7.19.85.jar"
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^#[a-z0-9_.-]+:[a-z0-9_./-]+$")
STACK = re.compile(r"^(?:([1-9][0-9]*)x )?(.+)$")
NODE = "CR01 — High-Energy Distribution"
PHASE = "High-Energy Grid"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"
WEATHERED_PRESS = "createcasing:weathered_iron_press"
REFINED_PRESS = "createcasing:refined_radiance_press"
EXPECTED = [
    (10, "industrial_colonies:mekanism/induction/casing", "mekanism:induction_casing", 8, "mekanism:induction/casing", "minecraft:crafting_shaped", 4),
    (20, "industrial_colonies:mekanism/induction/port", "mekanism:induction_port", 2, "mekanism:induction/port", "minecraft:crafting_shaped", 2),
    (30, "industrial_colonies:mekanism/induction/basic_cell", "mekanism:basic_induction_cell", 1, "mekanism:induction/cell/basic", "mekanism:mek_data", 1),
    (40, "industrial_colonies:mekanism/induction/basic_provider", "mekanism:basic_induction_provider", 1, "mekanism:induction/provider/basic", "minecraft:crafting_shaped", 1),
    (50, "industrial_colonies:mekanism/induction/advanced_cell", "mekanism:advanced_induction_cell", 1, "mekanism:induction/cell/advanced", "mekanism:mek_data", 1),
    (60, "industrial_colonies:mekanism/induction/advanced_provider", "mekanism:advanced_induction_provider", 1, "mekanism:induction/provider/advanced", "minecraft:crafting_shaped", 1),
    (70, "industrial_colonies:mekanism/induction/elite_cell", "mekanism:elite_induction_cell", 1, "mekanism:induction/cell/elite", "mekanism:mek_data", 1),
    (80, "industrial_colonies:mekanism/induction/elite_provider", "mekanism:elite_induction_provider", 1, "mekanism:induction/provider/elite", "minecraft:crafting_shaped", 1),
    (90, "industrial_colonies:mekanism/induction/ultimate_cell", "mekanism:ultimate_induction_cell", 1, "mekanism:induction/cell/ultimate", "mekanism:mek_data", 1),
    (100, "industrial_colonies:mekanism/induction/ultimate_provider", "mekanism:ultimate_induction_provider", 1, "mekanism:induction/provider/ultimate", "minecraft:crafting_shaped", 1),
]
CUBE_RECIPE = {
    "basic": "industrial_colonies:mekanism/storage/basic_energy_cube",
    "advanced": "industrial_colonies:mekanism/storage/advanced_energy_cube",
    "elite": "industrial_colonies:mekanism/storage/elite_energy_cube",
    "ultimate": "industrial_colonies:mekanism/storage/ultimate_energy_cube",
}
EXTERNAL_OUTPUTS = {
    "electroenergetics:heavily_insulated_wire": "industrial_colonies:extreme_grid/heavily_insulated_wire",
    "electroenergetics:voltage_regulator": "industrial_colonies:high_voltage/voltage_regulator",
    "electroenergetics:high_voltage_capacitor": "industrial_colonies:extreme_grid/high_voltage_capacitor",
    "mekanism:ultimate_universal_cable": "industrial_colonies:mekanism/transmission/ultimate_universal_cable",
    "mekanism:basic_energy_cube": CUBE_RECIPE["basic"],
    "mekanism:advanced_energy_cube": CUBE_RECIPE["advanced"],
    "mekanism:elite_energy_cube": CUBE_RECIPE["elite"],
    "mekanism:ultimate_energy_cube": CUBE_RECIPE["ultimate"],
}
EXPECTED_DEPENDENCIES = {
    EXPECTED[0][1]: {EXTERNAL_OUTPUTS["electroenergetics:heavily_insulated_wire"]},
    EXPECTED[1][1]: {EXPECTED[0][1], EXTERNAL_OUTPUTS["electroenergetics:voltage_regulator"], EXTERNAL_OUTPUTS["electroenergetics:high_voltage_capacitor"], EXTERNAL_OUTPUTS["mekanism:ultimate_universal_cable"]},
    EXPECTED[2][1]: {EXPECTED[0][1], CUBE_RECIPE["basic"]},
    EXPECTED[3][1]: {EXPECTED[0][1], CUBE_RECIPE["basic"]},
    EXPECTED[4][1]: {EXPECTED[2][1], CUBE_RECIPE["advanced"]},
    EXPECTED[5][1]: {EXPECTED[3][1], CUBE_RECIPE["advanced"]},
    EXPECTED[6][1]: {EXPECTED[4][1], CUBE_RECIPE["elite"]},
    EXPECTED[7][1]: {EXPECTED[5][1], CUBE_RECIPE["elite"]},
    EXPECTED[8][1]: {EXPECTED[6][1], CUBE_RECIPE["ultimate"], EXTERNAL_OUTPUTS["electroenergetics:high_voltage_capacitor"]},
    EXPECTED[9][1]: {EXPECTED[7][1], CUBE_RECIPE["ultimate"], EXTERNAL_OUTPUTS["electroenergetics:voltage_regulator"], EXTERNAL_OUTPUTS["mekanism:ultimate_universal_cable"]},
}
EXPECTED_ASSIGNMENTS = [
    "mekanism:basic_induction_cell", "mekanism:advanced_induction_cell",
    "mekanism:elite_induction_cell", "mekanism:basic_induction_provider",
    "mekanism:advanced_induction_provider", "mekanism:elite_induction_provider",
    "mekanism:ultimate_induction_provider",
]
ASSIGNMENT_EXISTING_PREFIX = [
    "mekanism:ultimate_tier_installer",
    "mekanism:ultimate_control_circuit",
    "mekanism:ultimate_universal_cable",
    "mekanism:ultimate_energy_cube",
    "mekanism:induction_casing",
    "mekanism:induction_port",
    "mekanism:ultimate_induction_cell",
    "mekanism:ultimate_combining_factory",
    "mekanism:ultimate_compressing_factory",
    "mekanism:ultimate_enriching_factory",
    "mekanism:ultimate_infusing_factory",
    "mekanism:ultimate_purifying_factory",
    "mekanism:ultimate_injecting_factory",
]
TRANSMITTER_ASSIGNMENT_SUFFIX = [
    "mekanism:ultimate_logistical_transporter",
    "mekanism:ultimate_mechanical_pipe",
    "mekanism:ultimate_pressurized_tube",
    "mekanism:ultimate_thermodynamic_conductor",
]
AUTO_OWNER_IDS = {
    "industrial_colonies:auto/mekanism/induction_casing",
    "industrial_colonies:auto/mekanism/induction_port",
    "industrial_colonies:auto/mekanism/ultimate_induction_cell",
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def audited_factory_assignment_delta(node: str, errors: list[str]) -> tuple[list[str], set[str]]:
    """Return the exact ordered Factory additions/removals for one node.

    The Factory audit owns this later assignment migration.  This validator
    therefore projects its historical Induction segment through that exact
    16-add/8-remove contract instead of weakening the segment to a prefix.
    """
    try:
        factory_plan = load_object(FACTORY_PLAN)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"cannot inspect Factory assignment plan: {error}")
        return [], set()
    delta = factory_plan.get("assignment_delta", {})
    expected_additions, expected_removals = factory_audit.expected_assignment_delta()
    additions = factory_audit.flatten_delta(delta.get("additions"))
    removals = factory_audit.flatten_delta(delta.get("removals"))
    if (
        factory_plan.get("status") != "implemented_in_seed"
        or additions != expected_additions
        or removals != expected_removals
        or delta.get("addition_count") != 16
        or delta.get("removal_count") != 8
    ):
        errors.append("Factory assignment plan must retain its exact implemented 16-add/8-remove delta")

    def outputs(field: str) -> list[str]:
        matches = [
            entry for entry in delta.get(field, [])
            if isinstance(entry, dict) and entry.get("node") == node
        ]
        if len(matches) != 1 or not isinstance(matches[0].get("outputs"), list):
            errors.append(f"Factory assignment plan must contain exactly one {field} entry for {node}")
            return []
        values = [str(value) for value in matches[0]["outputs"]]
        if len(values) != len(set(values)):
            errors.append(f"Factory assignment plan contains duplicate {field} for {node}")
        return values

    return outputs("additions"), set(outputs("removals"))


def default_mods() -> Path:
    for raw in (PROJECT / "gradle.properties").read_text(encoding="utf-8-sig").splitlines():
        if raw.strip().startswith("pack_mods_dir="):
            return Path(raw.split("=", 1)[1].strip()).expanduser().resolve()
    raise ValueError("gradle.properties is missing pack_mods_dir")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_stack(value: Any) -> tuple[str, int]:
    if isinstance(value, dict):
        return str(value.get("id", "")), int(value.get("count", 1))
    match = STACK.fullmatch(str(value).strip())
    if not match:
        return "", 0
    return match.group(2), int(match.group(1) or 1)


def resources(recipe: Mapping[str, Any]) -> Counter[str]:
    result: Counter[str] = Counter()
    if recipe.get("type") == "mechanical_crafting":
        pattern = recipe.get("pattern", [])
        keys = recipe.get("key", {})
        symbols = Counter(char for row in pattern if isinstance(row, str) for char in row if char != " ")
        for symbol, occurrences in symbols.items():
            resource, count = parse_stack(keys.get(symbol))
            if resource:
                result[resource] += occurrences * count
    else:
        for value in recipe.get("inputs", []):
            resource, count = parse_stack(value)
            if resource:
                result[resource] += count
        machine, count = parse_stack(recipe.get("machine"))
        if machine:
            result[machine] += count
    return result


def installed_recipe(row: Mapping[str, str], expected: Mapping[str, Any], mods: Path) -> tuple[str, str, int]:
    if row.get("source_jar") != EXPECTED_JAR:
        raise ValueError(f"catalog source JAR changed to {row.get('source_jar')!r}")
    if row.get("source_path") != expected.get("source_path"):
        raise ValueError(f"catalog source path changed to {row.get('source_path')!r}")
    jar = mods / EXPECTED_JAR
    if not jar.is_file():
        raise OSError(f"installed source JAR is missing: {jar}")
    with zipfile.ZipFile(jar) as archive:
        value = json.loads(archive.read(str(expected["source_path"])).decode("utf-8"))
    result = value.get("result")
    if isinstance(result, str):
        output, count = result, 1
    elif isinstance(result, dict):
        output, count = str(result.get("id", "")), int(result.get("count", 1))
    else:
        output, count = "", 0
    return str(value.get("type", "")), output, count


def seed_spec(contract: Mapping[str, Any]) -> dict[str, Any]:
    spec: dict[str, Any] = {
        "id": contract["id"], "node": contract["node"], "phase": contract["phase"],
        "order": contract["batch_order"], "type": contract["type"],
        "comment": contract["comment"], "output": contract["output"],
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
    return generator.shaped(spec, uid, True) if spec["type"] == "mechanical_crafting" else generator.process(spec, uid)


def recipes_by_id(data: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(recipe["id"]): recipe for recipe in data.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def recipe_output(recipe: Mapping[str, Any]) -> str:
    if "output" in recipe:
        return parse_stack(recipe.get("output"))[0]
    outputs = recipe.get("outputs", [])
    if isinstance(outputs, list) and outputs:
        return parse_stack(outputs[0])[0]
    return ""


def validate_implementation_parity(
    contracts: list[dict[str, Any]], seed: Mapping[str, Any],
    manifest: Mapping[str, Any], assignments: Mapping[str, Any],
    errors: list[str],
) -> None:
    seed_recipes = recipes_by_id(seed)
    manifest_recipes = recipes_by_id(manifest)
    expected_outputs = {parse_stack(contract.get("output"))[0] for contract in contracts}

    leaked_seed = AUTO_OWNER_IDS & set(seed_recipes)
    leaked_manifest = AUTO_OWNER_IDS & set(manifest_recipes)
    if leaked_seed:
        errors.append(f"automatic Induction owner leaked into authoritative seed: {sorted(leaked_seed)}")
    if leaked_manifest:
        errors.append(f"automatic Induction owner survived assembled manifest: {sorted(leaked_manifest)}")

    seed_owners: dict[str, list[str]] = {}
    manifest_owners: dict[str, list[str]] = {}
    for identity, recipe in seed_recipes.items():
        output = recipe_output(recipe)
        if output in expected_outputs:
            seed_owners.setdefault(output, []).append(identity)
    for identity, recipe in manifest_recipes.items():
        output = recipe_output(recipe)
        if output in expected_outputs:
            manifest_owners.setdefault(output, []).append(identity)

    for contract in contracts:
        identity = str(contract["id"])
        output = parse_stack(contract.get("output"))[0]
        expected = seed_spec(contract)
        actual = seed_recipes.get(identity)
        if actual is None:
            errors.append(f"implemented matrix recipe is absent from authoritative seed: {identity}")
        elif actual != expected:
            differing = sorted(
                field for field in set(actual) | set(expected)
                if actual.get(field) != expected.get(field)
            )
            errors.append(f"{identity}: authoritative seed differs from reviewed contract in {differing}")
        if seed_owners.get(output) != [identity]:
            errors.append(f"{identity}: matrix output does not have one seed owner; owners={seed_owners.get(output, [])}")
        if manifest_owners.get(output) != [identity]:
            errors.append(f"{identity}: matrix output does not have one assembled owner; owners={manifest_owners.get(output, [])}")
        assembled = manifest_recipes.get(identity)
        if assembled is None:
            errors.append(f"implemented matrix recipe is absent from assembled manifest: {identity}")
        elif recipe_output(assembled) != output:
            errors.append(f"{identity}: assembled manifest output changed")

    missing_dependencies = set(EXTERNAL_OUTPUTS.values()) - set(manifest_recipes)
    if missing_dependencies:
        errors.append(f"managed matrix predecessor IDs are absent from assembled manifest: {sorted(missing_dependencies)}")

    nodes = assignments.get("nodes", {})
    node = nodes.get(NODE, {}) if isinstance(nodes, dict) else {}
    actual_unlocks = node.get("unlocks", []) if isinstance(node, dict) else []
    factory_additions, factory_removals = audited_factory_assignment_delta(NODE, errors)
    historical_segment = ASSIGNMENT_EXISTING_PREFIX + EXPECTED_ASSIGNMENTS
    if any(historical_segment.count(output) != 1 for output in factory_removals):
        errors.append("Factory removals must each target one locked historical High-Energy assignment")
    transformed_segment = [output for output in historical_segment if output not in factory_removals]
    expected_unlocks = transformed_segment + TRANSMITTER_ASSIGNMENT_SUFFIX + factory_additions
    if actual_unlocks != expected_unlocks:
        errors.append(
            "High-Energy Distribution must preserve the locked Induction segment after the exact Factory removals, "
            "then the four audited transmitters, then the exact Factory additions"
        )


def compacting_machine_items() -> set[str]:
    environments = load_object(ENVIRONMENTS)
    for family in environments.get("recipe_families", []):
        if isinstance(family, dict) and family.get("id") == "compacting":
            return {str(machine.get("item", "")) for machine in family.get("machines", []) if isinstance(machine, dict)}
    return set()


def validate(
    plan: dict[str, Any], catalog: Path, mods: Path,
    seed: Mapping[str, Any], manifest: Mapping[str, Any],
    assignments: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        errors.append("audit status must be implemented_in_seed")
    scope = plan.get("scope", {})
    if scope.get("replacement_count") != 10 or scope.get("node") != NODE or scope.get("phase") != PHASE:
        errors.append("scope must describe ten High-Energy Distribution / High-Energy Grid recipes")
    if scope.get("installed_mod") != EXPECTED_JAR:
        errors.append("scope installed_mod changed")
    if scope.get("implementation_readiness") != "implemented_after_storage_ladder" or plan.get("implementation_assessment", {}).get("decision") != "go":
        errors.append("implementation assessment must record implemented_after_storage_ladder")
    implementation = plan.get("seed_implementation", {})
    if implementation.get("status") != "source_owned" or implementation.get("authoritative_source") != "progression/managed_recipe_overhaul.seed.json":
        errors.append("seed_implementation must name the authoritative source-owned seed")
    if implementation.get("recipe_count") != 10 or implementation.get("exact_stock_removals") != 10 or implementation.get("exclusive_output_owners") != 10:
        errors.append("seed_implementation must record ten recipes, removals, and exclusive owners")
    if set(implementation.get("replaced_auto_owner_ids", [])) != AUTO_OWNER_IDS:
        errors.append("seed_implementation auto-owner replacement set is stale")
    assignment_implementation = plan.get("assignment_implementation", {})
    if (
        assignment_implementation.get("status") != "appended_without_reordering"
        or assignment_implementation.get("authoritative_source") != "progression/machine_node_assignments.json"
        or assignment_implementation.get("node") != NODE
        or assignment_implementation.get("existing_prefix_count") != len(ASSIGNMENT_EXISTING_PREFIX)
        or assignment_implementation.get("appended_count") != len(EXPECTED_ASSIGNMENTS)
    ):
        errors.append("assignment_implementation metadata is incomplete or stale")

    items = {row["item_id"] for row in load_rows(catalog / "items.csv")}
    installed = {row["recipe_id"]: row for row in load_rows(catalog / "recipes.csv")}
    source_rows = plan.get("source_recipe_contracts", [])
    source = {str(row.get("recipe_id", "")): row for row in source_rows if isinstance(row, dict)}
    if len(source_rows) != 10 or len(source) != 10:
        errors.append("source_recipe_contracts must contain ten unique recipes")
    contracts = [row for row in plan.get("replacement_contracts", []) if isinstance(row, dict)]
    if len(contracts) != 10:
        errors.append("replacement_contracts must contain exactly ten recipes")
    validate_implementation_parity(contracts, seed, manifest, assignments, errors)
    contract_output_owner = {parse_stack(row.get("output"))[0]: str(row.get("id", "")) for row in contracts}
    external_rows = plan.get("external_prerequisites", [])
    declared_external = {str(row.get("output", "")): str(row.get("recipe_id", "")) for row in external_rows if isinstance(row, dict)}
    if declared_external != EXTERNAL_OUTPUTS or len(external_rows) != len(EXTERNAL_OUTPUTS):
        errors.append("external_prerequisites changed or are incomplete")
    valid_dependencies = {entry[1] for entry in EXPECTED} | set(EXTERNAL_OUTPUTS.values())
    press_items = compacting_machine_items()
    if {INDUSTRIAL_PRESS, WEATHERED_PRESS, REFINED_PRESS} - press_items:
        errors.append("tier_recipe_environments.json no longer exposes all reviewed Encased presses")

    removals: list[str] = []
    for index, recipe in enumerate(contracts):
        if index >= len(EXPECTED):
            break
        order, identity, expected_output, replacement_count, stock_id, stock_type, stock_count = EXPECTED[index]
        output, output_count = parse_stack(recipe.get("output"))
        if (recipe.get("batch_order"), recipe.get("id"), output, recipe.get("node"), recipe.get("phase")) != (order, identity, expected_output, NODE, PHASE):
            errors.append(f"matrix contract {index + 1} has wrong order/id/output/node/phase")
        if output_count != replacement_count or output not in items:
            errors.append(f"{identity}: replacement output/count changed")
        if not isinstance(recipe.get("comment"), str) or not recipe.get("comment", "").strip():
            errors.append(f"{identity}: nonblank generator comment is required")
        if recipe.get("exclusive_output") is not True:
            errors.append(f"{identity}: exclusive_output must be true")

        recipe_type = recipe.get("type")
        if index < 2:
            if recipe_type != "mechanical_crafting":
                errors.append(f"{identity}: casing/port must use Mechanical Crafting")
            pattern = recipe.get("pattern", [])
            if not isinstance(pattern, list) or len(pattern) != 5 or not all(isinstance(row, str) and len(row) == 5 for row in pattern):
                errors.append(f"{identity}: structural pattern is not exactly 5x5")
            else:
                used = {char for row in pattern for char in row if char != " "}
                if used != set(recipe.get("key", {})):
                    errors.append(f"{identity}: structural pattern/key mismatch")
        else:
            if recipe_type != "compacting":
                errors.append(f"{identity}: cells/providers must use Compacting")
            expected_press = INDUSTRIAL_PRESS if index in (2, 3) else WEATHERED_PRESS
            if recipe.get("machine") != expected_press:
                errors.append(f"{identity}: wrong Encased press; expected {expected_press}")
            if recipe.get("machine") == REFINED_PRESS:
                errors.append(f"{identity}: Refined Radiance is a post-phase Nuclear Engineering machine")
            for value in recipe.get("inputs", []):
                resource, count = parse_stack(value)
                if resource.startswith("#") and count > 1:
                    errors.append(f"{identity}: counted tags are unsupported by KJSGen: {value}")

        counts = resources(recipe)
        for resource in counts:
            if resource.startswith("#"):
                if not TAG_ID.fullmatch(resource):
                    errors.append(f"{identity}: invalid ingredient tag {resource}")
            elif not RESOURCE_ID.fullmatch(resource) or resource not in items:
                errors.append(f"{identity}: installed ingredient/machine is missing or invalid: {resource}")
        if index == 2 and counts["#c:dusts/lithium"] != 8:
            errors.append(f"{identity}: Basic Cell requires eight lithium tag slots")
        if index == 3 and counts["#c:dusts/lithium"] != 4:
            errors.append(f"{identity}: Basic Provider requires four lithium tag slots")
        if index == 2 and counts["mekanism:induction_casing"] != 2:
            errors.append(f"{identity}: requires 2x Induction Casing as the physical High-Energy gate")
        if index == 3 and counts["mekanism:induction_casing"] != 1:
            errors.append(f"{identity}: requires Induction Casing as the physical High-Energy gate")
        if index >= 4:
            prior_output = EXPECTED[index - 2][2]
            if counts[prior_output] != 4:
                errors.append(f"{identity}: requires exactly 4x {prior_output}")

        dependencies = recipe.get("depends_on_batch", [])
        if not isinstance(dependencies, list) or set(dependencies) != EXPECTED_DEPENDENCIES[identity]:
            errors.append(f"{identity}: dependency set changed")
        if isinstance(dependencies, list):
            inferred = {
                contract_output_owner[resource] for resource in counts if resource in contract_output_owner
            } | {
                EXTERNAL_OUTPUTS[resource] for resource in counts if resource in EXTERNAL_OUTPUTS
            }
            if set(dependencies) != inferred:
                errors.append(f"{identity}: declared dependencies differ from consumed managed outputs")
            earlier = {entry[1] for entry in EXPECTED[:index]}
            for dependency in dependencies:
                if dependency not in valid_dependencies:
                    errors.append(f"{identity}: unknown dependency {dependency}")
                elif dependency in {entry[1] for entry in EXPECTED} and dependency not in earlier:
                    errors.append(f"{identity}: same-batch dependency is not earlier: {dependency}")

        exact = recipe.get("remove_exact", [])
        if exact != [stock_id]:
            errors.append(f"{identity}: exact stock removal changed")
        removals.extend(exact if isinstance(exact, list) else [])
        expected_source = source.get(stock_id)
        catalog_row = installed.get(stock_id)
        if expected_source is None or catalog_row is None:
            errors.append(f"{identity}: stock source evidence is missing for {stock_id}")
        else:
            try:
                installed_type, installed_output, installed_count = installed_recipe(catalog_row, expected_source, mods)
            except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
                errors.append(f"{identity}: cannot inspect {stock_id}: {error}")
            else:
                if installed_type != stock_type or expected_source.get("recipe_type") != stock_type:
                    errors.append(f"{identity}: stock recipe type changed")
                if installed_output != expected_output or expected_source.get("output") != expected_output:
                    errors.append(f"{identity}: stock output changed")
                if installed_count != stock_count or expected_source.get("stock_output_count") != stock_count:
                    errors.append(f"{identity}: stock output count changed")
                if catalog_row.get("recipe_type") != installed_type or expected_output not in catalog_row.get("outputs", "").split("|"):
                    errors.append(f"{identity}: catalog/JAR source evidence differs")

        try:
            card = compile_card(recipe)
        except (KeyError, TypeError, ValueError) as error:
            errors.append(f"{identity}: KJSGen compiler rejected contract: {error}")
        else:
            card_output = card.get("slots", {}).get("output", {})
            if card_output.get("id") != expected_output or int(card_output.get("count", 1)) != replacement_count:
                errors.append(f"{identity}: KJSGen changed output identity/count")
            if recipe_type == "mechanical_crafting":
                if card.get("type") != "kjsgen:create_mechanical_crafting" or card.get("params") != {"gridW": "5", "gridH": "5"}:
                    errors.append(f"{identity}: KJSGen did not emit a 5x5 Mechanical Crafting card")
            else:
                machine_slot = card.get("slots", {}).get("__machine_process_compacting", {})
                if card.get("type") != "kjsgen:create_compacting" or machine_slot.get("id") != recipe.get("machine"):
                    errors.append(f"{identity}: KJSGen lost exact Compacting machine binding")

    if set(source) != {entry[4] for entry in EXPECTED} or Counter(removals) != Counter({entry[4]: 1 for entry in EXPECTED}):
        errors.append("source audit and exact removals are not one-to-one")
    if plan.get("assignment_additions") != EXPECTED_ASSIGNMENTS:
        errors.append("the seven missing High-Energy Distribution assignments changed")
    if plan.get("assignment_existing_prefix") != ASSIGNMENT_EXISTING_PREFIX:
        errors.append("the pre-existing High-Energy Distribution assignment prefix changed")
    policy = plan.get("component_transfer_policy", {})
    cell_outputs = {entry[2] for entry in EXPECTED if "_cell" in entry[2]}
    if policy.get("policy") != "not_preserved_drain_inputs_before_processing" or set(policy.get("affected_outputs", [])) != cell_outputs:
        errors.append("mek_data cell component-transfer policy is missing or incomplete")
    machine_policy = plan.get("machine_policy", {})
    if machine_policy != {"basic": INDUSTRIAL_PRESS, "advanced_and_elite": WEATHERED_PRESS, "ultimate": WEATHERED_PRESS, "excluded_post_phase_machine": REFINED_PRESS}:
        errors.append("machine policy no longer matches the High-Energy Grid phase")
    generator_contract = plan.get("generator_contract", {})
    if generator_contract.get("supported_types") != ["mechanical_crafting", "compacting"] or generator_contract.get("counted_tags_supported") is not False or generator_contract.get("exact_machine_binding_required") is not True:
        errors.append("generator contract changed")

    try:
        power = load_object(POWER_PLAN)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"cannot inspect POWER_BACKBONE_AUDIT intent: {error}")
    else:
        batches = {
            row.get("name"): row for row in power.get("follow_up_batches", [])
            if isinstance(row, dict)
        }
        matrix = batches.get("Induction Matrix Completion", {})
        if matrix.get("node") != NODE or set(matrix.get("remove_exact", [])) != {entry[4] for entry in EXPECTED}:
            errors.append("matrix node/removals differ from POWER_BACKBONE_AUDIT intent")
        ranks = {
            row.get("node"): row.get("rank") for row in power.get("age_order", [])
            if isinstance(row, dict)
        }
        if ranks.get(NODE) != 110:
            errors.append("POWER_BACKBONE_AUDIT High-Energy Distribution rank changed")

    predecessors = plan.get("implementation_assessment", {}).get("required_predecessor_plans", [])
    if predecessors != ["MEKANISM_STORAGE_LADDER_AUDIT.plan.json", "EXTREME_TRANSMISSION_AUDIT.plan.json"]:
        errors.append("required predecessor plan list changed")
    for filename in predecessors if isinstance(predecessors, list) else []:
        try:
            upstream = load_object(PROJECT / filename)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"cannot inspect blocking plan {filename}: {error}")
        else:
            if upstream.get("implementation_assessment", {}).get("decision") != "go":
                errors.append(f"matrix assessment is premature: {filename} is not go")
            if upstream.get("status") != "implemented_in_seed":
                errors.append(f"matrix implementation is premature: {filename} is not implemented_in_seed")
    return errors


def mutation_tests(
    plan: dict[str, Any], catalog: Path, mods: Path,
    seed: Mapping[str, Any], manifest: Mapping[str, Any],
    assignments: Mapping[str, Any],
) -> list[str]:
    tests: list[tuple[str, Any, str]] = []
    late_press = copy.deepcopy(plan)
    late_press["replacement_contracts"][8]["machine"] = REFINED_PRESS
    tests.append(("post-phase Ultimate press", late_press, "wrong Encased press"))
    counted_tag = copy.deepcopy(plan)
    counted_tag["replacement_contracts"][2]["inputs"][2:] = ["8x #c:dusts/lithium", "2x mekanism:steel_casing"]
    tests.append(("unsupported counted tag", counted_tag, "counted tags are unsupported"))
    cheap_upgrade = copy.deepcopy(plan)
    cheap_upgrade["replacement_contracts"][4]["inputs"][1] = "2x mekanism:basic_induction_cell"
    tests.append(("two-to-one cell shortcut", cheap_upgrade, "requires exactly 4x mekanism:basic_induction_cell"))
    missing_cube_edge = copy.deepcopy(plan)
    missing_cube_edge["replacement_contracts"][6]["depends_on_batch"].remove(CUBE_RECIPE["elite"])
    tests.append(("missing cube dependency", missing_cube_edge, "dependency set changed"))
    stale_stock_count = copy.deepcopy(plan)
    stale_stock_count["source_recipe_contracts"][0]["stock_output_count"] = 8
    tests.append(("stale stock count", stale_stock_count, "stock output count changed"))
    bypass_shell = copy.deepcopy(plan)
    bypass_shell["replacement_contracts"][2]["inputs"][-1] = "2x mekanism:steel_casing"
    tests.append(("Basic Cell shell bypass", bypass_shell, "physical High-Energy gate"))
    stale_status = copy.deepcopy(plan)
    stale_status["status"] = "review_only"
    tests.append(("stale audit status", stale_status, "status must be implemented_in_seed"))
    failures: list[str] = []
    for name, mutated, expected in tests:
        found = validate(mutated, catalog, mods, seed, manifest, assignments)
        if not any(expected in error for error in found):
            failures.append(f"mutation test {name!r} was not rejected with {expected!r}")

    missing_seed = copy.deepcopy(seed)
    missing_seed["recipes"] = [
        recipe for recipe in missing_seed.get("recipes", [])
        if recipe.get("id") != EXPECTED[0][1]
    ]
    found = validate(plan, catalog, mods, missing_seed, manifest, assignments)
    if not any("absent from authoritative seed" in error for error in found):
        failures.append("mutation test 'missing seed owner' was not rejected")

    drifted_seed = copy.deepcopy(seed)
    recipes_by_id(drifted_seed)[EXPECTED[1][1]]["pattern"][0] = "AAAAA"
    found = validate(plan, catalog, mods, drifted_seed, manifest, assignments)
    if not any("authoritative seed differs" in error for error in found):
        failures.append("mutation test 'seed contract drift' was not rejected")

    auto_manifest = copy.deepcopy(manifest)
    automatic = copy.deepcopy(recipes_by_id(seed)[EXPECTED[0][1]])
    automatic["id"] = "industrial_colonies:auto/mekanism/induction_casing"
    auto_manifest.setdefault("recipes", []).append(automatic)
    found = validate(plan, catalog, mods, seed, auto_manifest, assignments)
    if not any("automatic Induction owner survived" in error for error in found):
        failures.append("mutation test 'automatic assembled owner' was not rejected")

    duplicate_seed = copy.deepcopy(seed)
    duplicate = copy.deepcopy(recipes_by_id(duplicate_seed)[EXPECTED[6][1]])
    duplicate["id"] = "industrial_colonies:test/duplicate_elite_induction_cell"
    duplicate_seed.setdefault("recipes", []).append(duplicate)
    found = validate(plan, catalog, mods, duplicate_seed, manifest, assignments)
    if not any("does not have one seed owner" in error for error in found):
        failures.append("mutation test 'duplicate seed owner' was not rejected")

    reordered_assignments = copy.deepcopy(assignments)
    unlocks = reordered_assignments["nodes"][NODE]["unlocks"]
    left = unlocks.index(EXPECTED_ASSIGNMENTS[-2])
    right = unlocks.index(EXPECTED_ASSIGNMENTS[-1])
    unlocks[left], unlocks[right] = unlocks[right], unlocks[left]
    found = validate(plan, catalog, mods, seed, manifest, reordered_assignments)
    if not any("preserve the locked Induction segment" in error for error in found):
        failures.append("mutation test 'reordered assignments' was not rejected")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=None)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--skip-mutation-tests", action="store_true")
    args = parser.parse_args()
    try:
        plan = load_object(args.plan.resolve())
        catalog = args.catalog.resolve()
        mods = (args.mods or default_mods()).resolve()
        seed = load_object(args.seed.resolve())
        manifest = load_object(args.manifest.resolve())
        assignments = load_object(args.assignments.resolve())
        errors = validate(plan, catalog, mods, seed, manifest, assignments)
        if not args.skip_mutation_tests:
            errors.extend(mutation_tests(plan, catalog, mods, seed, manifest, assignments))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("Checked 10 installed source recipes/counts, exact seed/manifest ownership, the locked Induction assignment segment plus audited transmitter/Factory transformations, 10 KJSGen cards, 2 structural patterns, 8 exact machine bindings, 8 external prerequisites, ladder counts, and 12 mutations.")
    if errors:
        print(f"FAIL: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("PASS / IMPLEMENTED: the ten-matrix family exactly matches the authoritative seed, assignments, and assembled manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
