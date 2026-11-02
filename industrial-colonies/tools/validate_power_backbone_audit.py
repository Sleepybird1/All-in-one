#!/usr/bin/env python3
"""Validate the review-only power-backbone audit against installed catalog data."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "POWER_BACKBONE_AUDIT.plan.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^#[a-z0-9_.-]+:[a-z0-9_./-]+$")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def recipe_outputs(row: dict[str, str]) -> set[str]:
    return {part.strip() for part in row.get("outputs", "").split("|") if part.strip()}


def concrete_refs(recipe: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for symbol, value in recipe.get("key", {}).items():
        yield f"key.{symbol}", str(value)
    for field in ("ingredients", "inputs"):
        for index, value in enumerate(recipe.get(field, [])):
            yield f"{field}[{index}]", str(value)
    for field in ("input", "transitional"):
        if recipe.get(field):
            yield field, str(recipe[field])
    for index, step in enumerate(recipe.get("steps", [])):
        if step.get("ingredient"):
            yield f"steps[{index}].ingredient", str(step["ingredient"])
        if step.get("machine"):
            yield f"steps[{index}].machine", str(step["machine"])


def validate_pattern(recipe: dict[str, Any], failures: list[str]) -> None:
    pattern = recipe.get("pattern")
    if pattern is None:
        return
    if not isinstance(pattern, list) or not pattern or not all(isinstance(row, str) for row in pattern):
        failures.append(f"{recipe.get('id')}: pattern must be a nonempty string array")
        return
    widths = {len(row) for row in pattern}
    if len(widths) != 1:
        failures.append(f"{recipe.get('id')}: pattern rows are not rectangular: {sorted(widths)}")
    keys = set(recipe.get("key", {}))
    used = {char for row in pattern for char in row if char != " "}
    missing = sorted(used - keys)
    unused = sorted(keys - used)
    if missing:
        failures.append(f"{recipe.get('id')}: pattern symbols have no key: {missing}")
    if unused:
        failures.append(f"{recipe.get('id')}: key symbols are unused: {unused}")


def validate_plan(plan: dict[str, Any], catalog: Path, mods: Path) -> list[str]:
    failures: list[str] = []
    if plan.get("schema_version") != 1:
        failures.append("plan schema_version must be 1")
    if plan.get("status") not in {"review_only", "implemented_in_seed"}:
        failures.append("plan status must be review_only or implemented_in_seed")

    item_rows = load_rows(catalog / "items.csv")
    recipe_rows = load_rows(catalog / "recipes.csv")
    items = {row["item_id"] for row in item_rows}
    recipes = {row["recipe_id"]: row for row in recipe_rows}
    jar_names = {path.name for path in mods.glob("*.jar")}

    if any(item.startswith("immersiveengineering:") for item in items):
        failures.append("catalog unexpectedly contains immersiveengineering items; the absence finding is stale")
    if any(name.lower().startswith("immersiveengineering") for name in jar_names):
        failures.append("Immersive Engineering is now installed; rebuild and repeat this audit before integration")

    for entry in plan.get("installed_mods", []):
        if entry.get("status") == "not_installed":
            continue
        jar = entry.get("jar")
        if jar and jar not in jar_names:
            failures.append(f"installed-mod evidence is missing JAR: {jar}")

    batch = plan.get("recommended_batch", {})
    batch_recipes = batch.get("recipes", [])
    if batch.get("replacement_count") != len(batch_recipes):
        failures.append("recommended_batch replacement_count does not match recipes")
    if batch.get("exact_retirement_count") != len(batch.get("exact_retirements", [])):
        failures.append("recommended_batch exact_retirement_count does not match exact_retirements")

    seen_ids: set[str] = set()
    seen_outputs: set[str] = set()
    previous_order = -1
    assignments = load_json(PROJECT / "progression" / "machine_node_assignments.json").get("nodes", {})
    if not assignments:
        # The project currently stores the node map at the top level.
        assignments = load_json(PROJECT / "progression" / "machine_node_assignments.json")

    for recipe in batch_recipes:
        identity = str(recipe.get("id", ""))
        output = str(recipe.get("output", ""))
        order = recipe.get("batch_order")
        if not RESOURCE_ID.fullmatch(identity):
            failures.append(f"invalid replacement recipe ID: {identity!r}")
        if identity in seen_ids:
            failures.append(f"duplicate replacement recipe ID: {identity}")
        seen_ids.add(identity)
        if output in seen_outputs:
            failures.append(f"duplicate recommended output owner: {output}")
        seen_outputs.add(output)
        if output not in items:
            failures.append(f"{identity}: output is absent from items.csv: {output}")
        if not isinstance(order, int) or order <= previous_order:
            failures.append(f"{identity}: batch_order must be strictly increasing")
        elif isinstance(order, int):
            previous_order = order

        node = str(recipe.get("node", ""))
        node_entry = assignments.get(node, {}) if isinstance(assignments, dict) else {}
        if output not in node_entry.get("unlocks", []):
            failures.append(f"{identity}: {output} is not assigned to {node}")

        validate_pattern(recipe, failures)
        for field, value in concrete_refs(recipe):
            if value.startswith("#"):
                if not TAG_ID.fullmatch(value):
                    failures.append(f"{identity}: invalid tag in {field}: {value}")
            elif not RESOURCE_ID.fullmatch(value):
                failures.append(f"{identity}: invalid item ID in {field}: {value}")
            elif value not in items:
                failures.append(f"{identity}: item in {field} is absent from items.csv: {value}")

        removals = recipe.get("remove_exact", [])
        if not removals:
            failures.append(f"{identity}: source-owned replacement has no exact stock removal")
        for removal in removals:
            if removal not in recipes:
                failures.append(f"{identity}: exact stock recipe is absent: {removal}")
            elif output not in recipe_outputs(recipes[removal]):
                failures.append(
                    f"{identity}: stock recipe {removal} does not catalog {output} as an output"
                )
        for survivor in recipe.get("preserve_exact", []):
            if survivor not in recipes:
                failures.append(f"{identity}: preserved recipe is absent: {survivor}")
            elif output not in recipe_outputs(recipes[survivor]):
                failures.append(
                    f"{identity}: preserved recipe {survivor} does not catalog {output} as an output"
                )
            if survivor in removals:
                failures.append(f"{identity}: preserved recipe is also removed: {survivor}")

    for retirement in batch.get("exact_retirements", []):
        recipe_id = str(retirement.get("recipe_id", ""))
        output = str(retirement.get("output", ""))
        replacement = str(retirement.get("canonical_replacement", ""))
        if recipe_id not in recipes:
            failures.append(f"retirement recipe is absent: {recipe_id}")
        elif output not in recipe_outputs(recipes[recipe_id]):
            failures.append(f"retirement {recipe_id} does not catalog {output} as an output")
        if output not in items:
            failures.append(f"retirement output is absent from items.csv: {output}")
        if replacement not in items:
            failures.append(f"canonical replacement is absent from items.csv: {replacement}")

    for follow_up in plan.get("follow_up_batches", []):
        for identity in follow_up.get("replacement_recipe_ids", []):
            if not RESOURCE_ID.fullmatch(identity):
                failures.append(f"invalid follow-up replacement recipe ID: {identity!r}")
        for removal in follow_up.get("remove_exact", []):
            if removal not in recipes:
                failures.append(
                    f"{follow_up.get('name', 'follow-up')}: exact installed recipe is absent: {removal}"
                )

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = load_json(args.plan)
        failures = validate_plan(plan, args.catalog, args.mods)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if failures:
        print(f"Power-backbone audit validation failed ({len(failures)} issue(s)):" )
        for failure in failures:
            print(f"- {failure}")
        return 1

    batch = plan["recommended_batch"]
    follow_up_removals = sum(len(entry.get("remove_exact", [])) for entry in plan["follow_up_batches"])
    print(
        "Power-backbone audit validation passed: "
        f"{len(batch['recipes'])} replacement contracts, "
        f"{len(batch['exact_retirements'])} exact retirements, "
        f"{follow_up_removals} installed follow-up recipe IDs, and all concrete item/machine IDs resolved."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
