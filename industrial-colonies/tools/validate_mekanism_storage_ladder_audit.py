#!/usr/bin/env python3
"""Validate the reviewed Mekanism Energy Cube ladder and predecessor order."""

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


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "MEKANISM_STORAGE_LADDER_AUDIT.plan.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
EXTREME_PLAN = PROJECT / "EXTREME_TRANSMISSION_AUDIT.plan.json"
POWER_PLAN = PROJECT / "POWER_BACKBONE_AUDIT.plan.json"
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^#[a-z0-9_.-]+:[a-z0-9_./-]+$")
STACK = re.compile(r"^(?:([1-9][0-9]*)x )?(.+)$")
EXPECTED_JAR = "Mekanism-1.21.1-10.7.19.85.jar"
EXTERNAL_BREAKER = "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker"
AUTO_OWNER_IDS = {
    "industrial_colonies:auto/mekanism/basic_energy_cube",
    "industrial_colonies:auto/mekanism/advanced_energy_cube",
    "industrial_colonies:auto/mekanism/elite_energy_cube",
    "industrial_colonies:auto/mekanism/ultimate_energy_cube",
}
EXPECTED = [
    (10, "industrial_colonies:mekanism/storage/basic_energy_cube", "mekanism:basic_energy_cube", "CR01 — Reinforced Systems", "Mekanized Industry", "mekanism:energy_cube/basic"),
    (20, "industrial_colonies:mekanism/storage/advanced_energy_cube", "mekanism:advanced_energy_cube", "CR01 — Reinforced Systems", "Mekanized Industry", "mekanism:energy_cube/advanced"),
    (30, "industrial_colonies:mekanism/storage/elite_energy_cube", "mekanism:elite_energy_cube", "CR01 — Precision Engineering", "High-Energy Grid", "mekanism:energy_cube/elite"),
    (40, "industrial_colonies:mekanism/storage/ultimate_energy_cube", "mekanism:ultimate_energy_cube", "CR01 — High-Energy Distribution", "High-Energy Grid", "mekanism:energy_cube/ultimate"),
]
EXPECTED_DEPENDENCIES = {
    EXPECTED[0][1]: set(),
    EXPECTED[1][1]: {EXPECTED[0][1]},
    EXPECTED[2][1]: {EXPECTED[1][1]},
    EXPECTED[3][1]: {EXPECTED[2][1], EXTERNAL_BREAKER},
}
EXPECTED_PRIOR_COUNTS = {
    EXPECTED[0][1]: ("electroenergetics:accumulator", 1),
    EXPECTED[1][1]: ("mekanism:basic_energy_cube", 1),
    EXPECTED[2][1]: ("mekanism:advanced_energy_cube", 1),
    EXPECTED[3][1]: ("mekanism:elite_energy_cube", 2),
}
HARD_REQUIREMENTS = {
    EXPECTED[0][1]: {"electroenergetics:accumulator", "mekanism:basic_control_circuit", "tfmg:steel_frame"},
    EXPECTED[1][1]: {"mekanism:basic_energy_cube", "mekanism:advanced_control_circuit", "mekanism:alloy_reinforced"},
    EXPECTED[2][1]: {"mekanism:advanced_energy_cube", "mekanism:elite_control_circuit", "mekanism:alloy_atomic"},
    EXPECTED[3][1]: {"mekanism:elite_energy_cube", "mekanism:ultimate_control_circuit", "tfmg:circuit_board", "electroenergetics:sulfur_hexafluoride_breaker"},
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


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


def ingredient_counts(recipe: Mapping[str, Any]) -> Counter[str]:
    result: Counter[str] = Counter()
    pattern = recipe.get("pattern", [])
    keys = recipe.get("key", {})
    if not isinstance(pattern, list) or not isinstance(keys, dict):
        return result
    symbols = Counter(char for row in pattern if isinstance(row, str) for char in row if char != " ")
    for symbol, occurrences in symbols.items():
        resource, count = parse_stack(keys.get(symbol))
        if resource:
            result[resource] += occurrences * count
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
    return {
        "id": contract["id"], "phase": contract["phase"],
        "order": contract["batch_order"], "type": contract["type"],
        "comment": contract["comment"], "pattern": contract["pattern"],
        "key": contract["key"], "output": contract["output"],
        "remove": contract["remove_exact"],
        "exclusive_output": contract["exclusive_output"],
        "depends_on": contract.get("depends_on_batch", []),
    }


def compile_card(contract: Mapping[str, Any]) -> dict[str, Any]:
    spec = seed_spec(contract)
    return generator.shaped(spec, generator.stable_uid("recipe", str(spec["id"])), True)


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


def validate_seed_and_manifest_parity(
    contracts: list[dict[str, Any]], seed: Mapping[str, Any],
    manifest: Mapping[str, Any], errors: list[str],
) -> None:
    seed_recipes = recipes_by_id(seed)
    manifest_recipes = recipes_by_id(manifest)
    expected_outputs = {parse_stack(contract.get("output"))[0] for contract in contracts}

    if AUTO_OWNER_IDS & set(seed_recipes):
        errors.append(f"automatic Energy Cube owner leaked into authoritative seed: {sorted(AUTO_OWNER_IDS & set(seed_recipes))}")
    if AUTO_OWNER_IDS & set(manifest_recipes):
        errors.append(f"automatic Energy Cube owner survived assembled manifest: {sorted(AUTO_OWNER_IDS & set(manifest_recipes))}")

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
        actual = seed_recipes.get(identity)
        expected = seed_spec(contract)
        if actual is None:
            errors.append(f"implemented cube recipe is absent from authoritative seed: {identity}")
        elif actual != expected:
            differing = sorted(
                field for field in set(actual) | set(expected)
                if actual.get(field) != expected.get(field)
            )
            errors.append(f"{identity}: authoritative seed differs from reviewed contract in {differing}")
        if seed_owners.get(output) != [identity]:
            errors.append(f"{identity}: cube output does not have one seed owner; owners={seed_owners.get(output, [])}")
        if manifest_owners.get(output) != [identity]:
            errors.append(f"{identity}: cube output does not have one assembled owner; owners={manifest_owners.get(output, [])}")
        assembled = manifest_recipes.get(identity)
        if assembled is None:
            errors.append(f"implemented cube recipe is absent from assembled manifest: {identity}")
        elif recipe_output(assembled) != output:
            errors.append(f"{identity}: assembled manifest output changed")

    if EXTERNAL_BREAKER not in seed_recipes or EXTERNAL_BREAKER not in manifest_recipes:
        errors.append("source-owned Extreme SF6-breaker predecessor is missing from seed or assembled manifest")


def validate(
    plan: dict[str, Any], catalog: Path, mods: Path,
    seed: Mapping[str, Any], manifest: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        errors.append("audit status must be implemented_in_seed")
    if plan.get("scope", {}).get("replacement_count") != 4:
        errors.append("scope must declare exactly four cube replacements")
    if plan.get("scope", {}).get("installed_mod") != EXPECTED_JAR:
        errors.append("scope installed_mod changed")
    if plan.get("scope", {}).get("implementation_readiness") != "implemented_after_extreme_transmission":
        errors.append("scope must record implemented_after_extreme_transmission readiness")
    assessment = plan.get("implementation_assessment", {})
    if assessment.get("decision") != "go" or assessment.get("required_predecessor_recipe_id") != EXTERNAL_BREAKER:
        errors.append("implementation assessment must be go with the SF6-breaker predecessor")
    if assessment.get("required_predecessor_plan") != EXTREME_PLAN.name:
        errors.append("implementation assessment must name the Extreme Transmission plan")
    implementation = plan.get("seed_implementation", {})
    if implementation.get("status") != "source_owned":
        errors.append("seed_implementation status must be source_owned")
    if implementation.get("authoritative_source") != "progression/managed_recipe_overhaul.seed.json":
        errors.append("seed_implementation authoritative source is stale")
    if implementation.get("recipe_count") != 4 or implementation.get("exact_stock_removals") != 4:
        errors.append("seed_implementation must record four recipes and four exact removals")
    if set(implementation.get("replaced_auto_owner_ids", [])) != AUTO_OWNER_IDS:
        errors.append("seed_implementation auto-owner replacement set is stale")

    items = {row["item_id"] for row in load_rows(catalog / "items.csv")}
    installed = {row["recipe_id"]: row for row in load_rows(catalog / "recipes.csv")}
    source_rows = plan.get("source_recipe_contracts", [])
    source = {str(row.get("recipe_id", "")): row for row in source_rows if isinstance(row, dict)}
    if len(source_rows) != 4 or len(source) != 4:
        errors.append("source_recipe_contracts must contain four unique recipes")

    contracts = [row for row in plan.get("replacement_contracts", []) if isinstance(row, dict)]
    if len(contracts) != 4:
        errors.append("replacement_contracts must contain exactly four recipes")
    validate_seed_and_manifest_parity(contracts, seed, manifest, errors)
    removals: list[str] = []
    seen_outputs: set[str] = set()

    for index, recipe in enumerate(contracts):
        if index >= len(EXPECTED):
            break
        order, identity, expected_output, node, phase, stock_id = EXPECTED[index]
        output, output_count = parse_stack(recipe.get("output"))
        if (recipe.get("batch_order"), recipe.get("id"), output, recipe.get("node"), recipe.get("phase")) != (order, identity, expected_output, node, phase):
            errors.append(f"ladder contract {index + 1} has wrong order/id/output/node/phase")
        if output_count != 1 or output in seen_outputs or output not in items:
            errors.append(f"{identity}: output must be one unique installed cube")
        seen_outputs.add(output)
        if recipe.get("type") != "mechanical_crafting":
            errors.append(f"{identity}: cube recipe must use Mechanical Crafting")
        if not isinstance(recipe.get("comment"), str) or not recipe.get("comment", "").strip():
            errors.append(f"{identity}: nonblank generator comment is required")
        pattern = recipe.get("pattern", [])
        if not isinstance(pattern, list) or len(pattern) != 5 or not all(isinstance(row, str) and len(row) == 5 for row in pattern):
            errors.append(f"{identity}: pattern is not exactly 5x5")
        else:
            used = {char for row in pattern for char in row if char != " "}
            if used != set(recipe.get("key", {})):
                errors.append(f"{identity}: pattern/key symbols differ")

        counts = ingredient_counts(recipe)
        for resource in counts:
            if resource.startswith("#"):
                if not TAG_ID.fullmatch(resource):
                    errors.append(f"{identity}: invalid ingredient tag {resource}")
            elif not RESOURCE_ID.fullmatch(resource) or resource not in items:
                errors.append(f"{identity}: installed ingredient is missing or invalid: {resource}")
        missing = HARD_REQUIREMENTS[identity] - set(counts)
        if missing:
            errors.append(f"{identity}: missing hard tier requirements {sorted(missing)}")
        prior_item, prior_count = EXPECTED_PRIOR_COUNTS[identity]
        if counts[prior_item] != prior_count:
            errors.append(f"{identity}: requires exactly {prior_count}x {prior_item}")
        if identity == EXPECTED[3][1] and counts["tfmg:circuit_board"] == 0:
            errors.append("Ultimate Cube must use completed TFMG circuit board")
        if "tfmg:coated_circuit_board" in counts:
            errors.append(f"{identity}: coated board is an unfinished backward-tier ingredient")
        if any(resource.startswith(("ae2:", "appliedcreate:", "extendedae:")) for resource in counts):
            errors.append(f"{identity}: unrelated digital-storage processor entered the cube ladder")

        dependencies = recipe.get("depends_on_batch", [])
        if not isinstance(dependencies, list) or set(dependencies) != EXPECTED_DEPENDENCIES[identity]:
            errors.append(f"{identity}: dependency set changed")
        earlier = {entry[1] for entry in EXPECTED[:index]}
        for dependency in set(dependencies) if isinstance(dependencies, list) else set():
            if dependency != EXTERNAL_BREAKER and dependency not in earlier:
                errors.append(f"{identity}: dependency is not an earlier cube: {dependency}")

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
                if installed_type != expected_source.get("recipe_type") or installed_type != "mekanism:mek_data":
                    errors.append(f"{identity}: stock recipe type changed")
                if installed_output != expected_output or expected_source.get("output") != expected_output:
                    errors.append(f"{identity}: stock output changed")
                if installed_count != 1 or expected_source.get("stock_output_count") != 1:
                    errors.append(f"{identity}: stock output count changed")
                if catalog_row.get("recipe_type") != installed_type or expected_output not in catalog_row.get("outputs", "").split("|"):
                    errors.append(f"{identity}: catalog/JAR source evidence differs")
        if recipe.get("exclusive_output") is not True:
            errors.append(f"{identity}: exclusive_output must be true")
        try:
            card = compile_card(recipe)
        except (KeyError, TypeError, ValueError) as error:
            errors.append(f"{identity}: KJSGen compiler rejected contract: {error}")
        else:
            card_output = card.get("slots", {}).get("output", {})
            if card.get("type") != "kjsgen:create_mechanical_crafting" or card.get("params") != {"gridW": "5", "gridH": "5"}:
                errors.append(f"{identity}: KJSGen did not emit a 5x5 Mechanical Crafting card")
            if card_output.get("id") != expected_output or int(card_output.get("count", 1)) != 1:
                errors.append(f"{identity}: KJSGen changed output identity/count")

    if set(source) != {entry[5] for entry in EXPECTED} or Counter(removals) != Counter({entry[5]: 1 for entry in EXPECTED}):
        errors.append("source audit and exact removals are not one-to-one")
    hard = plan.get("hard_requirements", {})
    for key, expected in zip(("basic_requires", "advanced_requires", "elite_requires", "ultimate_requires"), EXPECTED):
        if set(hard.get(key, [])) != HARD_REQUIREMENTS[expected[1]]:
            errors.append(f"hard_requirements.{key} changed")

    policy = plan.get("component_transfer_policy", {})
    if policy.get("policy") != "not_preserved_drain_inputs_before_processing" or set(policy.get("affected_outputs", [])) != {entry[2] for entry in EXPECTED}:
        errors.append("mek_data component-transfer policy is missing or incomplete")
    generator_contract = plan.get("generator_contract", {})
    if generator_contract.get("supported_types") != ["mechanical_crafting"] or generator_contract.get("reviewed_grid") != "5x5":
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
        storage = batches.get("Mekanism Storage Ladder", {})
        if storage.get("replacement_recipe_ids") != [entry[1] for entry in EXPECTED]:
            errors.append("cube IDs differ from POWER_BACKBONE_AUDIT intent")
        if set(storage.get("remove_exact", [])) != {entry[5] for entry in EXPECTED}:
            errors.append("cube removals differ from POWER_BACKBONE_AUDIT intent")
        ranks = {
            row.get("node"): row.get("rank") for row in power.get("age_order", [])
            if isinstance(row, dict)
        }
        if [ranks.get(name) for name in ("CR01 — Reinforced Systems", "CR01 — Precision Engineering", "CR01 — High-Energy Distribution")] != [90, 100, 110]:
            errors.append("POWER_BACKBONE_AUDIT cube-node order changed")

    try:
        extreme = load_object(EXTREME_PLAN)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"cannot inspect blocking Extreme Transmission plan: {error}")
    else:
        extreme_ids = {row.get("id") for row in extreme.get("replacement_contracts", []) if isinstance(row, dict)}
        if EXTERNAL_BREAKER not in extreme_ids:
            errors.append("blocking SF6-breaker recipe ID is absent from Extreme Transmission plan")
        if extreme.get("status") != "implemented_in_seed" or extreme.get("implementation_assessment", {}).get("decision") != "go":
            errors.append("cube implementation is premature: Extreme Transmission is not implemented/go")
    return errors


def mutation_tests(
    plan: dict[str, Any], catalog: Path, mods: Path,
    seed: Mapping[str, Any], manifest: Mapping[str, Any],
) -> list[str]:
    tests: list[tuple[str, Any, str]] = []
    wrong_board = copy.deepcopy(plan)
    wrong_board["replacement_contracts"][3]["key"]["U"] = "tfmg:coated_circuit_board"
    tests.append(("unfinished Ultimate board", wrong_board, "Ultimate Cube must use completed TFMG circuit board"))
    wrong_count = copy.deepcopy(plan)
    wrong_count["replacement_contracts"][3]["pattern"][2] = "EAHBE"
    tests.append(("lost second Elite Cube", wrong_count, "requires exactly 2x mekanism:elite_energy_cube"))
    missing_dependency = copy.deepcopy(plan)
    missing_dependency["replacement_contracts"][3]["depends_on_batch"].pop()
    tests.append(("lost convergence dependency", missing_dependency, "dependency set changed"))
    wrong_source_count = copy.deepcopy(plan)
    wrong_source_count["source_recipe_contracts"][0]["stock_output_count"] = 2
    tests.append(("stale stock count", wrong_source_count, "stock output count changed"))
    wrong_status = copy.deepcopy(plan)
    wrong_status["status"] = "review_only"
    tests.append(("stale audit status", wrong_status, "status must be implemented_in_seed"))
    failures: list[str] = []
    for name, mutated, expected in tests:
        found = validate(mutated, catalog, mods, seed, manifest)
        if not any(expected in error for error in found):
            failures.append(f"mutation test {name!r} was not rejected with {expected!r}")

    missing_seed = copy.deepcopy(seed)
    missing_seed["recipes"] = [
        recipe for recipe in missing_seed.get("recipes", [])
        if recipe.get("id") != EXPECTED[0][1]
    ]
    found = validate(plan, catalog, mods, missing_seed, manifest)
    if not any("absent from authoritative seed" in error for error in found):
        failures.append("mutation test 'missing seed owner' was not rejected")

    drifted_seed = copy.deepcopy(seed)
    for recipe in drifted_seed.get("recipes", []):
        if recipe.get("id") == EXPECTED[1][1]:
            recipe["pattern"][0] = "AAAAA"
            break
    found = validate(plan, catalog, mods, drifted_seed, manifest)
    if not any("authoritative seed differs" in error for error in found):
        failures.append("mutation test 'seed contract drift' was not rejected")

    auto_manifest = copy.deepcopy(manifest)
    auto_recipe = copy.deepcopy(recipes_by_id(auto_manifest)[EXPECTED[0][1]])
    auto_recipe["id"] = "industrial_colonies:auto/mekanism/basic_energy_cube"
    auto_manifest.setdefault("recipes", []).append(auto_recipe)
    found = validate(plan, catalog, mods, seed, auto_manifest)
    if not any("automatic Energy Cube owner survived" in error for error in found):
        failures.append("mutation test 'automatic assembled owner' was not rejected")

    duplicate_seed = copy.deepcopy(seed)
    duplicate = copy.deepcopy(recipes_by_id(duplicate_seed)[EXPECTED[2][1]])
    duplicate["id"] = "industrial_colonies:test/duplicate_elite_energy_cube"
    duplicate_seed.setdefault("recipes", []).append(duplicate)
    found = validate(plan, catalog, mods, duplicate_seed, manifest)
    if not any("does not have one seed owner" in error for error in found):
        failures.append("mutation test 'duplicate seed owner' was not rejected")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=None)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--skip-mutation-tests", action="store_true")
    args = parser.parse_args()
    try:
        plan = load_object(args.plan.resolve())
        catalog = args.catalog.resolve()
        mods = (args.mods or default_mods()).resolve()
        seed = load_object(args.seed.resolve())
        manifest = load_object(args.manifest.resolve())
        errors = validate(plan, catalog, mods, seed, manifest)
        if not args.skip_mutation_tests:
            errors.extend(mutation_tests(plan, catalog, mods, seed, manifest))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("Checked 4 installed stock recipes/counts, 4 exact 5x5 KJSGen cards, seed/manifest ownership, ladder semantics, component policy, dependency order, and focused mutations.")
    if errors:
        print(f"FAIL: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("PASS / IMPLEMENTED: the four Energy Cube contracts exactly match the authoritative seed and assembled manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
