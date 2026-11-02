#!/usr/bin/env python3
"""Validate the reviewed Extreme Power Transmission repair and its clean analog boundary."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import generate_managed_recipe_overhaul as generator


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "EXTREME_TRANSMISSION_AUDIT.plan.json"
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^#[a-z0-9_.-]+:[a-z0-9_./-]+$")
STACK = re.compile(r"^(?:([1-9][0-9]*)x )?(.+)$")
BANNED_PREFIXES = ("ae2:", "appliedcreate:", "extendedae:", "megacells:", "mekanism:")
BANNED_MACHINE_PREFIXES = (
    "createcasing:industrial_iron_",
    "createcasing:weathered_iron_",
    "createcasing:refined_radiance_",
)
EXPECTED_MACHINE = "createcasing:railway_press"
FINAL_ID = "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker"
RETIRED_LEGACY_ID = "industrial_colonies:grid/sulfur_hexafluoride_breaker"
FINAL_DEPENDENCIES = {
    "industrial_colonies:extreme_grid/heavily_insulated_wire_spool",
    "industrial_colonies:extreme_grid/hanging_glass_insulator",
    "industrial_colonies:extreme_grid/ground_rod",
    "industrial_colonies:extreme_grid/high_voltage_switch",
    "industrial_colonies:extreme_grid/high_voltage_capacitor",
}
SEMANTIC_REQUIREMENTS: dict[str, set[str]] = {
    "industrial_colonies:extreme_grid/glass_insulator_segment": {
        "#c:glass_blocks", "#c:wires/iron", "tfmg:screw",
    },
    "industrial_colonies:extreme_grid/heavily_insulated_wire": {
        "electroenergetics:insulated_wire", "tfmg:rubber_sheet", "tfmg:plastic_sheet",
    },
    "industrial_colonies:extreme_grid/heavily_insulated_wire_spool": {
        "electroenergetics:empty_spool", "electroenergetics:heavily_insulated_wire", "tfmg:steel_mechanism",
    },
    "industrial_colonies:extreme_grid/hanging_glass_insulator": {
        "electroenergetics:glass_insulator_segment", "tfmg:screw", "#c:plates/steel",
    },
    "industrial_colonies:extreme_grid/ground_rod": {
        "tfmg:copper_electrode", "electroenergetics:connector", "tfmg:copper_wire", "tfmg:screw",
    },
    "industrial_colonies:extreme_grid/high_voltage_switch": {
        "electroenergetics:insulator", "tfmg:steel_casing",
        "electroenergetics:miniature_circuit_breaker",
        "electroenergetics:heavily_insulated_wire_spool",
    },
    "industrial_colonies:extreme_grid/high_voltage_capacitor": {
        "tfmg:steel_casing", "electroenergetics:heavily_insulated_wire",
        "electroenergetics:capacitor", "electroenergetics:transformer_core",
    },
    FINAL_ID: {
        "electroenergetics:hanging_glass_insulator", "electroenergetics:ground_rod",
        "electroenergetics:heavily_insulated_wire_spool",
        "electroenergetics:high_voltage_switch", "electroenergetics:high_voltage_capacitor",
        "tfmg:heavy_machinery_casing", "electroenergetics:transformer",
        "electroenergetics:voltage_regulator", "electroenergetics:transformer_oil_bucket",
    },
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


def ingredient_refs(recipe: Mapping[str, Any]) -> Iterable[tuple[str, str]]:
    for symbol, value in recipe.get("key", {}).items():
        yield f"key.{symbol}", parse_stack(value)[0]
    for field in ("inputs", "ingredients"):
        for index, value in enumerate(recipe.get(field, [])):
            yield f"{field}[{index}]", parse_stack(value)[0]
    for field in ("input", "transitional", "machine"):
        if recipe.get(field):
            yield field, parse_stack(recipe[field])[0]
    for index, step in enumerate(recipe.get("steps", [])):
        if not isinstance(step, dict):
            continue
        for field in ("ingredient", "machine"):
            if step.get(field):
                yield f"steps[{index}].{field}", parse_stack(step[field])[0]


def resource_set(recipe: Mapping[str, Any]) -> set[str]:
    return {resource for _field, resource in ingredient_refs(recipe) if resource}


def boundary_violations(recipe: Mapping[str, Any]) -> set[str]:
    return {
        resource for resource in resource_set(recipe)
        if resource.startswith(BANNED_PREFIXES) or resource.startswith(BANNED_MACHINE_PREFIXES)
    }


def recipes_by_id(data: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(recipe["id"]): recipe for recipe in data.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def primary_output(recipe: Mapping[str, Any]) -> tuple[str, int]:
    if "output" in recipe:
        return parse_stack(recipe.get("output"))
    outputs = recipe.get("outputs", [])
    if isinstance(outputs, list) and outputs:
        return parse_stack(outputs[0])
    return "", 0


def recipes_by_output(data: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for identity, recipe in recipes_by_id(data).items():
        output, _count = primary_output(recipe)
        if output:
            result[output] = identity
    return result


def validate_pattern(recipe: Mapping[str, Any], errors: list[str]) -> None:
    identity = str(recipe.get("id"))
    pattern = recipe.get("pattern")
    if not isinstance(pattern, list) or len(pattern) != 5 or not all(
        isinstance(row, str) and len(row) == 5 for row in pattern
    ):
        errors.append(f"{identity}: Mechanical Crafting pattern is not exactly 5x5")
        return
    used = {char for row in pattern for char in row if char != " "}
    keys = set(recipe.get("key", {}))
    if used != keys:
        errors.append(f"{identity}: pattern/key mismatch used={sorted(used)} keys={sorted(keys)}")


def installed_recipe(row: Mapping[str, str], mods: Path) -> tuple[str, str, int]:
    jar = mods / row["source_jar"]
    if not jar.is_file():
        raise OSError(f"installed source JAR is missing: {jar}")
    with zipfile.ZipFile(jar) as archive:
        value = json.loads(archive.read(row["source_path"]).decode("utf-8"))
    result = value.get("result")
    if isinstance(result, str):
        output, count = result, 1
    elif isinstance(result, dict):
        output, count = str(result.get("id", "")), int(result.get("count", 1))
    else:
        output, count = "", 0
    return str(value.get("type", "")), output, count


def seed_spec(contract: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": contract["id"], "phase": contract["phase"],
        "order": contract["batch_order"], "type": contract["type"],
        "comment": contract["comment"], "output": contract["output"],
        "remove": contract["remove_exact"], "exclusive_output": contract["exclusive_output"],
        "depends_on": contract.get("depends_on_batch", []),
    }
    for field in ("machine", "inputs", "pattern", "key"):
        if field in contract:
            result[field] = contract[field]
    return result


def compile_card(contract: Mapping[str, Any]) -> dict[str, Any]:
    spec = seed_spec(contract)
    uid = generator.stable_uid("recipe", str(spec["id"]))
    if spec["type"] == "compacting":
        return generator.process(spec, uid)
    if spec["type"] == "mechanical_crafting":
        return generator.shaped(spec, uid, True)
    raise ValueError(f"unsupported reviewed recipe type: {spec['type']!r}")


def validate_seed_parity(
    contracts: list[dict[str, Any]], seed: Mapping[str, Any], errors: list[str]
) -> None:
    seed_recipes = recipes_by_id(seed)
    if RETIRED_LEGACY_ID in seed_recipes:
        errors.append(f"retired legacy Extreme owner is still present in seed: {RETIRED_LEGACY_ID}")

    owners_by_output: dict[str, list[str]] = {}
    for identity, recipe in seed_recipes.items():
        output, _count = primary_output(recipe)
        if output:
            owners_by_output.setdefault(output, []).append(identity)

    for contract in contracts:
        identity = str(contract.get("id", ""))
        actual = seed_recipes.get(identity)
        if actual is None:
            errors.append(f"implemented Extreme recipe is absent from authoritative seed: {identity}")
            continue
        expected = seed_spec(contract)
        if actual != expected:
            differing = sorted(
                field for field in set(actual) | set(expected)
                if actual.get(field) != expected.get(field)
            )
            errors.append(f"{identity}: authoritative seed differs from reviewed contract in {differing}")
        output, _count = parse_stack(contract.get("output"))
        if owners_by_output.get(output) != [identity]:
            errors.append(
                f"{identity}: reviewed output does not have exactly one authoritative seed owner; "
                f"owners={owners_by_output.get(output, [])}"
            )


def combined_dependencies(
    contracts: list[dict[str, Any]], manifest: Mapping[str, Any]
) -> dict[str, set[str]]:
    manifest_recipes = recipes_by_id(manifest)
    contract_ids = {str(contract["id"]) for contract in contracts}
    output_owner = recipes_by_output(manifest)
    output_owner.update({parse_stack(c.get("output"))[0]: str(c["id"]) for c in contracts})
    graph: dict[str, set[str]] = {}
    for contract in contracts:
        identity = str(contract["id"])
        graph[identity] = set(contract.get("depends_on_batch", []))
        graph[identity].update(
            output_owner[resource] for resource in resource_set(contract)
            if resource in output_owner and output_owner[resource] != identity
        )
    for identity, recipe in manifest_recipes.items():
        if identity in contract_ids:
            continue
        graph[identity] = {
            output_owner[resource] for resource in resource_set(recipe)
            if resource in output_owner and output_owner[resource] != identity
        }
    return graph


def reachable(graph: Mapping[str, set[str]], root: str) -> set[str]:
    result: set[str] = set()
    pending = [root]
    while pending:
        identity = pending.pop()
        if identity in result:
            continue
        result.add(identity)
        pending.extend(graph.get(identity, set()) - result)
    return result


def validate(
    plan: dict[str, Any], catalog: Path, manifest: Mapping[str, Any], mods: Path,
    seed: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        errors.append("audit status must be implemented_in_seed")
    assessment = plan.get("implementation_assessment", {})
    if assessment.get("decision") != "go":
        errors.append("implementation assessment must be go after predecessor repair")
    if plan.get("scope", {}).get("implementation_readiness") != "go":
        errors.append("scope implementation_readiness must be go")
    if assessment.get("unblock_condition_satisfied") is not True:
        errors.append("unblock_condition_satisfied must be true")
    implementation = plan.get("seed_implementation", {})
    if implementation.get("status") != "source_owned":
        errors.append("seed_implementation status must be source_owned")
    if implementation.get("authoritative_source") != "progression/managed_recipe_overhaul.seed.json":
        errors.append("seed_implementation authoritative source is stale")
    if implementation.get("recipe_count") != 8 or implementation.get("exact_stock_removals") != 8:
        errors.append("seed_implementation must record eight recipes and eight exact removals")
    if implementation.get("retired_legacy_id") != RETIRED_LEGACY_ID:
        errors.append("seed_implementation retired legacy ID is stale")

    items = {row["item_id"] for row in load_rows(catalog / "items.csv")}
    source = {row["recipe_id"]: row for row in load_rows(catalog / "recipes.csv")}
    source_contracts = plan.get("source_recipe_contracts", [])
    expected_sources = {
        str(row["recipe_id"]): row for row in source_contracts if isinstance(row, dict)
    }
    if len(expected_sources) != 8 or len(source_contracts) != 8:
        errors.append("source_recipe_contracts must contain eight unique recipes")
    contracts = [row for row in plan.get("replacement_contracts", []) if isinstance(row, dict)]
    if plan.get("scope", {}).get("replacement_count") != len(contracts) or len(contracts) != 8:
        errors.append("scope and replacement_contracts must describe exactly eight recipes")
    validate_seed_parity(contracts, seed, errors)

    seen_ids: set[str] = set()
    seen_outputs: set[str] = set()
    orders: dict[str, int] = {}
    contract_ids = {str(row.get("id", "")) for row in contracts}
    contract_output_owner = {
        parse_stack(row.get("output"))[0]: str(row.get("id", "")) for row in contracts
    }

    for recipe in contracts:
        identity = str(recipe.get("id", ""))
        output, output_count = parse_stack(recipe.get("output"))
        if not RESOURCE_ID.fullmatch(identity) or identity in seen_ids:
            errors.append(f"invalid or duplicate replacement ID: {identity!r}")
        seen_ids.add(identity)
        if output not in items or output in seen_outputs:
            errors.append(f"missing or duplicate output: {output!r}")
        seen_outputs.add(output)
        if recipe.get("node") != "CR01 — Extreme Power Transmission":
            errors.append(f"{identity}: wrong node")
        if recipe.get("phase") != "High-Energy Grid":
            errors.append(f"{identity}: wrong phase")
        if recipe.get("exclusive_output") is not True:
            errors.append(f"{identity}: exclusive_output must be true")
        order = recipe.get("batch_order")
        if not isinstance(order, int) or isinstance(order, bool):
            errors.append(f"{identity}: batch_order is not an integer")
        else:
            orders[identity] = order

        if recipe.get("type") == "mechanical_crafting":
            validate_pattern(recipe, errors)
        elif recipe.get("type") == "compacting":
            if recipe.get("machine") != EXPECTED_MACHINE:
                errors.append(f"{identity}: compacting is not locked to the Railway press")
        else:
            errors.append(f"{identity}: unsupported recipe type {recipe.get('type')!r}")

        removals = recipe.get("remove_exact", [])
        if not isinstance(removals, list) or len(removals) != 1:
            errors.append(f"{identity}: expected one exact stock removal")
        for removal in removals if isinstance(removals, list) else []:
            expected = expected_sources.get(removal)
            installed = source.get(removal)
            if expected is None:
                errors.append(f"{identity}: removal is not source-audited: {removal}")
            elif installed is None:
                errors.append(f"{identity}: installed stock recipe disappeared: {removal}")
            else:
                try:
                    installed_type, installed_output, installed_count = installed_recipe(installed, mods)
                except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
                    errors.append(f"{identity}: cannot read installed stock recipe {removal}: {error}")
                else:
                    if installed_type != expected.get("recipe_type"):
                        errors.append(f"{identity}: installed type changed for {removal}")
                    if installed_output != output or expected.get("output") != output:
                        errors.append(f"{identity}: installed output changed for {removal}")
                    if installed_count != output_count or expected.get("output_count") != output_count:
                        errors.append(
                            f"{identity}: output count {output_count} does not match installed count {installed_count}"
                        )

        refs = resource_set(recipe)
        missing_semantics = sorted(SEMANTIC_REQUIREMENTS.get(identity, set()) - refs)
        if missing_semantics:
            errors.append(f"{identity}: missing semantic manufacturing inputs {missing_semantics}")
        for field, resource in ingredient_refs(recipe):
            if not resource:
                errors.append(f"{identity}: could not parse {field}")
                continue
            if resource.startswith("#"):
                if not TAG_ID.fullmatch(resource):
                    errors.append(f"{identity}: invalid tag in {field}: {resource}")
            elif not RESOURCE_ID.fullmatch(resource):
                errors.append(f"{identity}: invalid resource in {field}: {resource}")
            elif resource not in items:
                errors.append(f"{identity}: missing installed item in {field}: {resource}")
            if resource.startswith(BANNED_PREFIXES) or resource.startswith(BANNED_MACHINE_PREFIXES):
                errors.append(f"{identity}: cross-branch ingredient/machine violates analog boundary: {resource}")

        for value in recipe.get("inputs", []):
            resource, count = parse_stack(value)
            if count > 1 and resource.startswith("#"):
                errors.append(f"{identity}: counted tags are unsupported by KJSGen: {value}")

        dependencies = recipe.get("depends_on_batch", [])
        if not isinstance(dependencies, list):
            errors.append(f"{identity}: depends_on_batch must be a list")
            dependencies = []
        inferred = {
            contract_output_owner[resource] for resource in refs if resource in contract_output_owner
        }
        if set(dependencies) != inferred:
            errors.append(
                f"{identity}: same-batch dependencies differ from ingredients; declared={sorted(dependencies)} inferred={sorted(inferred)}"
            )
        for dependency in dependencies:
            if dependency not in contract_ids:
                errors.append(f"{identity}: unknown same-batch dependency {dependency}")
            elif identity in orders and dependency in orders and orders[dependency] >= orders[identity]:
                errors.append(f"{identity}: dependency {dependency} is not earlier in batch order")

        try:
            card = compile_card(recipe)
        except (KeyError, TypeError, ValueError) as error:
            errors.append(f"{identity}: KJSGen compiler rejected reviewed contract: {error}")
        else:
            card_output = card.get("slots", {}).get("output", {})
            if card_output.get("id") != output or int(card_output.get("count", 1)) != output_count:
                errors.append(f"{identity}: KJSGen card changed output identity/count")

    order_values = list(orders.values())
    if order_values != sorted(order_values) or len(set(order_values)) != len(order_values):
        errors.append("batch_order values are not strictly increasing and unique")
    all_removals = [
        removal for recipe in contracts for removal in recipe.get("remove_exact", [])
        if isinstance(removal, str)
    ]
    if set(expected_sources) != set(all_removals) or any(
        count != 1 for count in Counter(all_removals).values()
    ):
        errors.append("source recipe audit and exact removals are not one-to-one")

    by_id = {str(row["id"]): row for row in contracts}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> None:
        if identity in visiting:
            errors.append(f"same-batch dependency cycle at {identity}")
            return
        if identity in visited or identity not in by_id:
            return
        visiting.add(identity)
        for dependency in by_id[identity].get("depends_on_batch", []):
            visit(dependency)
        visiting.remove(identity)
        visited.add(identity)

    for identity in by_id:
        visit(identity)
    if set(by_id.get(FINAL_ID, {}).get("depends_on_batch", [])) != FINAL_DEPENDENCIES:
        errors.append("SF6 breaker does not converge every reviewed protected-grid subsystem")

    preserved = set(plan.get("preserve_stock_recipe_ids", []))
    if preserved != {"electroenergetics:crafting/glass_insulator_spool"}:
        errors.append("glass_insulator_spool must be the sole explicit stock preserve in this batch")
    for identity in preserved:
        if identity not in source:
            errors.append(f"preserved installed recipe disappeared: {identity}")
        if identity in all_removals:
            errors.append(f"preserved installed recipe is also removed: {identity}")

    manifest_recipes = recipes_by_id(manifest)
    repaired = assessment.get("cleared_predecessors", [])
    blocker_ids = [str(row.get("recipe_id", "")) for row in repaired if isinstance(row, dict)]
    predecessors = plan.get("predecessor_recipe_ids", [])
    if blocker_ids != predecessors or len(blocker_ids) != 7:
        errors.append("predecessor_recipe_ids must exactly match seven ordered repaired predecessors")
    for blocker in repaired:
        identity = str(blocker.get("recipe_id", ""))
        current = manifest_recipes.get(identity)
        if current is None:
            errors.append(f"recorded repaired predecessor is absent from current manifest: {identity}")
            continue
        actual_output, _count = primary_output(current)
        if actual_output != blocker.get("output"):
            errors.append(f"recorded predecessor output is stale for {identity}")
        actual_violations = boundary_violations(current)
        declared_violations = set(blocker.get("boundary_violations", []))
        if declared_violations:
            errors.append(f"repaired predecessor still declares boundary violations for {identity}")
        if actual_violations != declared_violations:
            errors.append(
                f"recorded boundary evidence is stale for {identity}; declared={sorted(declared_violations)} actual={sorted(actual_violations)}"
            )

    graph = combined_dependencies(contracts, manifest)
    missing_predecessor_edges = sorted(set(predecessors) - reachable(graph, FINAL_ID))
    if missing_predecessor_edges:
        errors.append(
            f"repaired predecessors are not on the final breaker dependency graph: {missing_predecessor_edges}"
        )

    generator_contract = plan.get("generator_contract", {})
    if generator_contract.get("supported_types") != ["compacting", "mechanical_crafting"]:
        errors.append("generator_contract supported_types is stale")
    if generator_contract.get("counted_tags_supported") is not False:
        errors.append("generator_contract must record that counted tags are unsupported")
    if generator_contract.get("exact_machine") != EXPECTED_MACHINE:
        errors.append("generator_contract exact_machine is not the Railway press")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--mods", type=Path, default=None)
    args = parser.parse_args()
    try:
        plan = load_object(args.plan.resolve())
        manifest = load_object(args.manifest.resolve())
        seed = load_object(args.seed.resolve())
        errors = validate(
            plan, args.catalog.resolve(), manifest, (args.mods or default_mods()).resolve(), seed
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(
        "Checked eight stock recipes and output counts, eight KJSGen cards, the analog batch DAG, "
        "one preserved stock route, seven repaired predecessor boundary contracts, and exact seed parity."
    )
    if errors:
        print(f"FAIL: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("PASS: audit evidence and reviewed cards are internally consistent.")
    print("IMPLEMENTED: the eight Extreme Transmission contracts exactly match the authoritative seed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
