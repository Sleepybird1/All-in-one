#!/usr/bin/env python3
"""Validate the source-owned TFMG-to-Electro Energetics power backbone."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_PLAN = PROJECT / "POWER_BACKBONE_AUDIT.plan.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"

EARLY_ELECTRICITY = "CR01 — Early Electricity Technology"
EARLY_CABLES = "CR01 — Early Power Cables"
CHEMICAL = "CR01 — Chemical Processing"
GRID = "CR01 — Grid Engineering"

FORBIDDEN_EARLY_FRAGMENTS = (
    "steel",
    "capacitor",
    "circuit",
    "magnet",
    "winding",
    "coated_circuit_board",
)
FORBIDDEN_SIBLING_PREFIXES = (
    "ae2:",
    "advanced_ae:",
    "appmek:",
    "appliedcreate:",
    "extendedae:",
    "megacells:",
    "mekanism:",
)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def output_stack(recipe: Mapping[str, Any]) -> tuple[str, int]:
    value = recipe.get("output")
    if isinstance(value, str):
        parts = value.split(maxsplit=1)
        if len(parts) == 2 and parts[0].endswith("x") and parts[0][:-1].isdigit():
            return parts[1], int(parts[0][:-1])
        return value, 1
    if isinstance(value, dict):
        return str(value.get("id", "")), int(value.get("count", 1))
    return "", 0


def plan_output(recipe: Mapping[str, Any]) -> str:
    output = str(recipe.get("output", ""))
    count = int(recipe.get("output_count", 1))
    return output if count == 1 else f"{count}x {output}"


def ingredient_values(recipe: Mapping[str, Any]) -> set[str]:
    values: set[str] = set()
    key = recipe.get("key", {})
    if isinstance(key, dict):
        values.update(str(value) for value in key.values() if isinstance(value, str))
    for field in ("ingredients", "inputs"):
        ingredients = recipe.get(field, [])
        if isinstance(ingredients, list):
            values.update(str(value) for value in ingredients if isinstance(value, str))
    for field in ("input", "transitional"):
        if isinstance(recipe.get(field), str):
            values.add(str(recipe[field]))
    for step in recipe.get("steps", []):
        if not isinstance(step, dict):
            continue
        for field in ("ingredient", "machine"):
            if isinstance(step.get(field), str):
                values.add(str(step[field]))
    return values


def recipes_by_id(seed: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(recipe.get("id")): recipe
        for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def recipes_by_output(seed: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for recipe in seed.get("recipes", []):
        if isinstance(recipe, dict):
            output, _count = output_stack(recipe)
            result.setdefault(output, []).append(recipe)
    return result


def all_removals(seed: Mapping[str, Any]) -> list[str]:
    result = [
        removal
        for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict)
        for removal in recipe.get("remove", [])
        if isinstance(removal, str)
    ]
    result.extend(
        removal
        for removal in seed.get("additional_removals", [])
        if isinstance(removal, str)
    )
    return result


def exact_fields(plan_recipe: Mapping[str, Any]) -> Iterable[str]:
    yield from ("phase", "type")
    for field in ("pattern", "key", "ingredients", "inputs", "input", "transitional", "loops", "steps"):
        if field in plan_recipe:
            yield field


def validate_contract(
    seed: Mapping[str, Any],
    plan: Mapping[str, Any],
    assignments: Mapping[str, Any],
    manifest: Mapping[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    recipes = recipes_by_id(seed)
    by_output = recipes_by_output(seed)
    removals = all_removals(seed)
    nodes = assignments.get("nodes", {})
    batch = plan.get("recommended_batch", {})
    expected_recipes = batch.get("recipes", [])

    recipe_ids = [
        str(recipe.get("id"))
        for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    ]
    duplicates = sorted({identity for identity in recipe_ids if recipe_ids.count(identity) > 1})
    if duplicates:
        errors.append(f"duplicate source recipe IDs: {duplicates}")

    for expected in expected_recipes:
        identity = str(expected["id"])
        output = str(expected["output"])
        actual = recipes.get(identity)
        if actual is None:
            errors.append(f"missing source-owned recipe: {identity}")
            continue
        owners = by_output.get(output, [])
        if len(owners) != 1 or owners[0].get("id") != identity:
            errors.append(
                f"{output} has {len(owners)} explicit owners; expected only {identity}"
            )
        if str(actual.get("id", "")).startswith("industrial_colonies:auto/"):
            errors.append(f"{output} is still owned by generic auto-generation")
        if actual.get("output") != plan_output(expected):
            errors.append(
                f"{identity} output is {actual.get('output')!r}; expected {plan_output(expected)!r}"
            )
        for field in exact_fields(expected):
            if actual.get(field) != expected.get(field):
                errors.append(f"{identity} changed reviewed field {field}")
        if actual.get("remove") != expected.get("remove_exact"):
            errors.append(f"{identity} does not own its exact reviewed stock removals")
        if actual.get("exclusive_output") is not True:
            errors.append(f"{identity} is not exclusive_output")

        node = str(expected["node"])
        if output not in nodes.get(node, {}).get("unlocks", []):
            errors.append(f"{output} is not assigned to {node}")

        ingredients = ingredient_values(actual)
        if node == EARLY_ELECTRICITY:
            bad = sorted(
                value
                for value in ingredients
                if value.startswith(FORBIDDEN_SIBLING_PREFIXES)
                or any(fragment in value for fragment in FORBIDDEN_EARLY_FRAGMENTS)
            )
            if bad:
                errors.append(f"{identity} has later/sibling early-electricity ingredients: {bad}")
        if node == EARLY_CABLES:
            bad = sorted(
                value
                for value in ingredients
                if value == "tfmg:copper_spool"
                or value in {"createaddition:connector", "createaddition:large_connector"}
                or value.startswith(FORBIDDEN_SIBLING_PREFIXES)
            )
            if bad:
                errors.append(f"{identity} has sibling local-cable ingredients: {bad}")
        if node == GRID:
            bad = sorted(
                value
                for value in ingredients
                if value == "tfmg:copper_spool"
                or value in {"createaddition:connector", "createaddition:large_connector"}
                or value.startswith(FORBIDDEN_SIBLING_PREFIXES)
            )
            if bad:
                errors.append(f"{identity} has non-ancestor grid ingredients: {bad}")

    expected_ids = {str(recipe["id"]) for recipe in expected_recipes}
    if len(expected_ids) != int(batch.get("replacement_count", -1)):
        errors.append("plan replacement_count does not match unique recipe contracts")

    additional = seed.get("additional_removals", [])
    for retirement in batch.get("exact_retirements", []):
        recipe_id = str(retirement["recipe_id"])
        count = additional.count(recipe_id)
        if count != 1:
            errors.append(f"duplicate retirement {recipe_id} appears {count} times; expected once")
        if removals.count(recipe_id) != 1:
            errors.append(f"retirement {recipe_id} has {removals.count(recipe_id)} total owners")
        output = str(retirement["output"])
        if output in by_output:
            errors.append(f"retired duplicate output still has a source recipe: {output}")

    for expected in expected_recipes:
        for removal in expected.get("remove_exact", []):
            if removals.count(removal) != 1:
                errors.append(f"stock recipe {removal} has {removals.count(removal)} removal owners")
            if removal in additional:
                errors.append(f"source-owned stock removal is redundantly broad-listed: {removal}")
        for survivor in expected.get("preserve_exact", []):
            if survivor in removals:
                errors.append(f"safe EE connector reclamation was removed: {survivor}")

    for output in ("tfmg:generator", "tfmg:electric_motor"):
        if output in seed.get("exclude_outputs", []):
            errors.append(
                f"{output} cannot be both source-owned and excluded from manifest generation"
            )

    if manifest is not None:
        manifest_recipes = recipes_by_id(manifest)
        manifest_by_output = recipes_by_output(manifest)
        for expected in expected_recipes:
            identity = str(expected["id"])
            output = str(expected["output"])
            actual = manifest_recipes.get(identity)
            if actual is None:
                errors.append(f"temporary manifest omitted {identity}")
                continue
            if len(manifest_by_output.get(output, [])) != 1:
                errors.append(f"temporary manifest has competing owners for {output}")
            if actual.get("output") != plan_output(expected):
                errors.append(f"temporary manifest changed output for {identity}")
            if actual.get("remove") != expected.get("remove_exact"):
                errors.append(f"temporary manifest changed removals for {identity}")
        manifest_removals = all_removals(manifest)
        for retirement in batch.get("exact_retirements", []):
            recipe_id = str(retirement["recipe_id"])
            if manifest_removals.count(recipe_id) != 1:
                errors.append(f"temporary manifest lost exact retirement {recipe_id}")
        for expected in expected_recipes:
            for survivor in expected.get("preserve_exact", []):
                if survivor in manifest_removals:
                    errors.append(f"temporary manifest removed safe reclamation {survivor}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--manifest", type=Path, help="optional isolated generated manifest")
    args = parser.parse_args()

    seed = load_object(args.seed.resolve())
    plan = load_object(args.plan.resolve())
    assignments = load_object(args.assignments.resolve())
    manifest = load_object(args.manifest.resolve()) if args.manifest else None
    errors = validate_contract(seed, plan, assignments, manifest)

    batch = plan["recommended_batch"]
    print(
        f"Checked {len(batch['recipes'])} source-owned power recipes, "
        f"{len(batch['exact_retirements'])} exact duplicate retirements, and "
        "three preserved connector reclamation IDs."
    )
    if errors:
        print(f"FAIL: {len(errors)} power-backbone issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("PASS: the TFMG-first local-power and Electro Energetics grid backbone is source-owned and topology-safe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
