#!/usr/bin/env python3
"""Validate the first Mekanism transmission tier and infinite-cell retirement.

The five basic transmitters are intentionally bulk components rather than
late-game machines.  Their managed recipes therefore keep the stock yield of
eight, but require the earlier TFMG factory, Create handling/plumbing, Electro
Energetics grid, and first Mekanism infusion capabilities.  ExtendedAE's two
infinite source cells are retired because they would erase the pack's bulk
resource and fluid-production goals.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current" / "recipes.csv"

TARGET_NODE = "CR01 — Modular Machinery"
TARGET_PHASE = "Mekanized Industry"

TRANSMITTER_RECIPES: Mapping[str, Mapping[str, Any]] = {
    "mekanism:basic_universal_cable": {
        "managed": "industrial_colonies:mekanism/transmission/basic_universal_cable",
        "stock": "mekanism:transmitter/universal_cable/basic",
        "order": 20,
        "pattern": ["RTR", "CAC", "RTR"],
        "key": {
            "R": "tfmg:rubber_sheet",
            "T": "tfmg:cable_tube",
            "C": "electroenergetics:connector",
            "A": "mekanism:alloy_infused",
        },
    },
    "mekanism:basic_logistical_transporter": {
        "managed": "industrial_colonies:mekanism/transmission/basic_logistical_transporter",
        "stock": "mekanism:transmitter/logistical_transporter/basic",
        "order": 21,
        "pattern": ["DCD", "SAM", "DCD"],
        "key": {
            "D": "create:depot",
            "C": "create:chute",
            "S": "tfmg:steel_mechanism",
            "A": "mekanism:alloy_infused",
            "M": "mekanism:basic_control_circuit",
        },
    },
    "mekanism:basic_mechanical_pipe": {
        "managed": "industrial_colonies:mekanism/transmission/basic_mechanical_pipe",
        "stock": "mekanism:transmitter/mechanical_pipe/basic",
        "order": 22,
        "pattern": ["PCP", "SAM", "PCP"],
        "key": {
            "P": "tfmg:cast_iron_pipe",
            "C": "create:fluid_pipe",
            "S": "tfmg:steel_mechanism",
            "A": "mekanism:alloy_infused",
            "M": "create:mechanical_pump",
        },
    },
    "mekanism:basic_pressurized_tube": {
        "managed": "industrial_colonies:mekanism/transmission/basic_pressurized_tube",
        "stock": "mekanism:transmitter/pressurized_tube/basic",
        "order": 23,
        "pattern": ["GSG", "RAR", "GSG"],
        "key": {
            "G": "#c:glass_blocks/cheap",
            "S": "tfmg:steel_casing",
            "R": "tfmg:rubber_sheet",
            "A": "mekanism:alloy_infused",
        },
    },
    "mekanism:basic_thermodynamic_conductor": {
        "managed": "industrial_colonies:mekanism/transmission/basic_thermodynamic_conductor",
        "stock": "mekanism:transmitter/thermodynamic_conductor/basic",
        "order": 24,
        "pattern": ["PCP", "SAS", "PCP"],
        "key": {
            "P": "#c:plates/copper",
            "C": "electroenergetics:copper_wire_spool",
            "S": "tfmg:cast_iron_pipe",
            "A": "mekanism:alloy_infused",
        },
    },
}

INFINITE_CELL_RETIREMENTS: Mapping[str, str] = {
    "extendedae:cobblestone_cell": "extendedae:infinity_cobblestone_cell",
    "extendedae:water_cell": "extendedae:infinity_water_cell",
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def output_id(recipe: Mapping[str, Any]) -> str:
    value = recipe.get("output")
    if isinstance(value, str):
        match = re.fullmatch(r"\s*\d+x\s+(.+?)\s*", value)
        return match.group(1) if match else value.strip()
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return str(value["id"])
    return ""


def output_count(recipe: Mapping[str, Any]) -> int:
    value = recipe.get("output")
    if isinstance(value, dict):
        count = value.get("count", 1)
        return count if isinstance(count, int) and not isinstance(count, bool) else -1
    if isinstance(value, str):
        match = re.fullmatch(r"\s*(\d+)x\s+.+?\s*", value)
        return int(match.group(1)) if match else 1
    return -1


def manifest_removals(manifest: Mapping[str, Any]) -> set[str]:
    result = {
        str(value)
        for value in manifest.get("additional_removals", [])
        if isinstance(value, str)
    }
    for recipe in manifest.get("recipes", []):
        if isinstance(recipe, dict):
            result.update(
                str(value) for value in recipe.get("remove", []) if isinstance(value, str)
            )
    return result


def compiled_removals(compiled: Mapping[str, Any]) -> set[str]:
    return {
        str(entry.get("recipeId"))
        for entry in compiled.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }


def assigned_nodes(assignments: Mapping[str, Any]) -> dict[str, set[str]]:
    owners: dict[str, set[str]] = {}
    nodes = assignments.get("nodes", {})
    if not isinstance(nodes, dict):
        return owners
    for node_name, node in nodes.items():
        if not isinstance(node_name, str) or not isinstance(node, dict):
            continue
        for item in node.get("unlocks", []):
            if isinstance(item, str):
                owners.setdefault(item, set()).add(node_name)
    return owners


def expected_slots(policy: Mapping[str, Any]) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    key = policy["key"]
    for row, text in enumerate(policy["pattern"]):
        for column, symbol in enumerate(text):
            if symbol == " ":
                continue
            value = str(key[symbol])
            kind = "ITEM_TAG" if value.startswith("#") else "ITEM"
            result[f"in{row * 3 + column}"] = (kind, value.removeprefix("#"))
    return result


def catalog_producers(path: Path) -> dict[str, set[str]]:
    outputs = set(TRANSMITTER_RECIPES) | set(INFINITE_CELL_RETIREMENTS.values())
    found = {output: set() for output in outputs}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            produced = {
                value.strip() for value in str(row.get("outputs", "")).split("|") if value.strip()
            }
            for output in outputs & produced:
                recipe_id = str(row.get("recipe_id", "")).strip()
                if recipe_id:
                    found[output].add(recipe_id)
    return found


def _missing(label: str, expected: Iterable[str], actual: set[str]) -> list[str]:
    return [f"{label} is missing exact removal {value}" for value in sorted(set(expected) - actual)]


def validate_contract(
    seed: Mapping[str, Any],
    manifest: Mapping[str, Any],
    compiled: Mapping[str, Any],
    assignments: Mapping[str, Any],
    producers: Mapping[str, set[str]] | None = None,
) -> list[str]:
    errors: list[str] = []
    recipes = [value for value in manifest.get("recipes", []) if isinstance(value, dict)]
    manifest_by_output: dict[str, list[Mapping[str, Any]]] = {}
    for recipe in recipes:
        manifest_by_output.setdefault(output_id(recipe), []).append(recipe)
    compiled_by_id = {
        str(recipe.get("recipeId")): recipe
        for recipe in compiled.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("recipeId"), str)
    }

    owners = assigned_nodes(assignments)
    phase_order = seed.get("phase_order", [])
    phase_by_node = seed.get("phase_by_node", {})
    phase_index = {
        phase: index for index, phase in enumerate(phase_order) if isinstance(phase, str)
    }
    target_index = phase_index.get(TARGET_PHASE)
    if target_index is None or not isinstance(phase_by_node, dict):
        errors.append("seed phase policy does not define the Mekanized Industry target")

    stock_ids = {str(policy["stock"]) for policy in TRANSMITTER_RECIPES.values()}
    retirement_ids = set(INFINITE_CELL_RETIREMENTS)
    manifest_removed = manifest_removals(manifest)
    generated_removed = compiled_removals(compiled)
    errors.extend(_missing("managed manifest", stock_ids | retirement_ids, manifest_removed))
    errors.extend(_missing("compiled KJSGen project", stock_ids | retirement_ids, generated_removed))

    for output, policy in TRANSMITTER_RECIPES.items():
        if owners.get(output) != {TARGET_NODE}:
            errors.append(
                f"{output} assignment changed: {sorted(owners.get(output, set()))} != [{TARGET_NODE!r}]"
            )
        matches = manifest_by_output.get(output, [])
        if len(matches) != 1:
            errors.append(f"{output} has {len(matches)} managed producers; expected exactly one")
            continue
        recipe = matches[0]
        recipe_id = str(policy["managed"])
        if recipe.get("id") != recipe_id:
            errors.append(f"{output} managed ID changed: {recipe.get('id')!r} != {recipe_id!r}")
        if recipe.get("phase") != TARGET_PHASE or recipe.get("order") != policy["order"]:
            errors.append(f"{recipe_id} phase/order changed")
        if recipe.get("type") != "shaped":
            errors.append(f"{recipe_id} must remain a bulk-friendly 3x3 shaped recipe")
        if recipe.get("pattern") != policy["pattern"] or recipe.get("key") != policy["key"]:
            errors.append(f"{recipe_id} deliberate cross-mod construction pattern changed")
        if output_count(recipe) != 8:
            errors.append(f"{recipe_id} must produce eight network segments")
        if recipe.get("remove") != [policy["stock"]] or recipe.get("exclusive_output") is not True:
            errors.append(f"{recipe_id} no longer exactly replaces {policy['stock']}")

        if target_index is not None and isinstance(phase_by_node, dict):
            actual_key = recipe.get("key", {})
            for value in actual_key.values() if isinstance(actual_key, dict) else ():
                ingredient = str(value)
                if ingredient.startswith("#") or ingredient.startswith("minecraft:"):
                    continue
                ingredient_owners = owners.get(ingredient, set())
                available = [
                    node
                    for node in ingredient_owners
                    if phase_index.get(phase_by_node.get(node, ""), 10**6) <= target_index
                ]
                if not available:
                    errors.append(
                        f"{recipe_id} ingredient {ingredient} is not assigned to an earlier/current phase"
                    )

        compiled_recipe = compiled_by_id.get(recipe_id)
        if not isinstance(compiled_recipe, dict):
            errors.append(f"compiled KJSGen project is missing {recipe_id}")
            continue
        if compiled_recipe.get("type") != "kjsgen:shaped":
            errors.append(f"compiled {recipe_id} is not a shaped recipe")
        slots = compiled_recipe.get("slots", {})
        if not isinstance(slots, dict):
            errors.append(f"compiled {recipe_id} has no slot map")
            continue
        expected = expected_slots(policy)
        for slot_name, (kind, identifier) in expected.items():
            slot = slots.get(slot_name)
            if not isinstance(slot, dict) or (slot.get("kind"), slot.get("id")) != (
                kind,
                identifier,
            ):
                errors.append(f"compiled {recipe_id} changed slot {slot_name}")
        out = slots.get("output")
        if not isinstance(out, dict) or out.get("id") != output or out.get("count") != 8:
            errors.append(f"compiled {recipe_id} does not emit 8x {output}")

    retired_outputs = set(INFINITE_CELL_RETIREMENTS.values())
    leaked = sorted(retired_outputs & set(manifest_by_output))
    if leaked:
        errors.append(f"managed manifest reintroduces retired infinite cells: {leaked}")
    compiled_outputs = {
        str(slot.get("id"))
        for recipe in compiled.get("recipes", [])
        if isinstance(recipe, dict)
        for slots in [recipe.get("slots", {})]
        if isinstance(slots, dict)
        for slot in [slots.get("output")]
        if isinstance(slot, dict) and slot.get("kind") == "ITEM" and slot.get("id")
    }
    leaked = sorted(retired_outputs & compiled_outputs)
    if leaked:
        errors.append(f"compiled KJSGen project reintroduces retired infinite cells: {leaked}")

    for removal in compiled.get("removals", []):
        if not isinstance(removal, dict) or removal.get("recipeId") not in stock_ids | retirement_ids:
            continue
        broad = {field: removal.get(field) for field in ("output", "input", "mod") if removal.get(field)}
        if broad:
            errors.append(f"exact removal {removal.get('recipeId')} has broad filters: {broad}")

    if producers is not None:
        for output, policy in TRANSMITTER_RECIPES.items():
            expected = {str(policy["stock"])}
            if producers.get(output, set()) != expected:
                errors.append(
                    f"installed catalog producers for {output} changed: "
                    f"{sorted(producers.get(output, set()))} != {sorted(expected)}"
                )
        for recipe_id, output in INFINITE_CELL_RETIREMENTS.items():
            if recipe_id not in producers.get(output, set()):
                errors.append(f"installed catalog no longer maps {recipe_id} to {output}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--compiled", type=Path, default=DEFAULT_COMPILED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = validate_contract(
            load_object(args.seed.resolve()),
            load_object(args.manifest.resolve()),
            load_object(args.compiled.resolve()),
            load_object(args.assignments.resolve()),
            catalog_producers(args.catalog.resolve()),
        )
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print(f"FAIL: {len(errors)} Mekanism transmission issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {len(TRANSMITTER_RECIPES)} basic transmitter families have dependency-safe "
        f"eight-segment recipes and {len(INFINITE_CELL_RETIREMENTS)} infinite-cell recipes are retired."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
