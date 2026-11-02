#!/usr/bin/env python3
"""Validate the five source-owned processing-component progression closures.

The validator is intentionally seed-first because the committed assembled
manifest and KJSGen project may lag while several recipe batches are being
authored in parallel.  Optional manifest, compiled-project, and static-catalog
checks are available for temporary-output validation.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"

COUNTED_ITEM = re.compile(r"^(\d+)x\s+([a-z0-9_.-]+:[a-z0-9_./-]+)$")


def sequence_step(operation: str, machine: str, ingredient: str | None = None) -> dict[str, str]:
    result = {"op": operation, "machine": machine}
    if ingredient is not None:
        result["ingredient"] = ingredient
    return result


CONTRACTS: Mapping[str, Mapping[str, Any]] = {
    "tfmg:empty_spool": {
        "id": "industrial_colonies:electronics_manufacturing/empty_spool",
        "phase": "Electrical Manufacturing",
        "order": 5,
        "type": "cutting",
        "input": "tfmg:hardened_planks",
        "machine": "createcasing:copper_mechanical_saw",
        "output_count": 1,
        "remove": {"tfmg:empty_spool_from_hardened_planks_stonecutting"},
    },
    "megacells:accumulation_processor": {
        "id": "industrial_colonies:digital/accumulation_processor",
        "phase": "High-Energy Grid",
        "order": 69,
        "type": "sequenced_assembly",
        "input": "megacells:printed_accumulation_processor",
        "transitional": "megacells:printed_accumulation_processor",
        "loops": 2,
        "output_count": 1,
        "steps": [
            sequence_step("deploying", "createcasing:copper_deployer", "tfmg:coated_circuit_board"),
            sequence_step("deploying", "createcasing:copper_deployer", "ae2:printed_silicon"),
            sequence_step("deploying", "createcasing:copper_deployer", "tfmg:capacitor_item"),
            sequence_step("deploying", "createcasing:copper_deployer", "#c:dusts/fluix"),
            sequence_step("pressing", "createcasing:brass_press"),
        ],
        "remove": {
            "megacells:inscriber/accumulation_processor",
            "extendedae:assembler/accumulation_processor",
        },
    },
    "electroenergetics:transformer_core_lamination": {
        "id": "industrial_colonies:high_voltage/transformer_core_lamination",
        "phase": "High-Energy Grid",
        "order": 62,
        "type": "pressing",
        "input": "#c:plates/steel",
        # The later High-Voltage Repair audit deliberately moved the analog
        # grid family onto the Railway line.  Keep this earlier closure check
        # synchronized with that implemented, more-specific contract.
        "machine": "createcasing:railway_press",
        "output_count": 2,
        "remove": {"electroenergetics:stonecutting/transformer_core_lamination"},
    },
    "electroenergetics:transformer_core": {
        "id": "industrial_colonies:high_voltage/transformer_core",
        "phase": "High-Energy Grid",
        "order": 64,
        "type": "sequenced_assembly",
        "input": "electroenergetics:transformer_core_lamination",
        "transitional": "electroenergetics:incomplete_transformer_core",
        "loops": 1,
        "output_count": 1,
        "steps": [
            sequence_step(
                "deploying",
                "createcasing:railway_deployer",
                "electroenergetics:transformer_core_lamination",
            ),
            sequence_step(
                "deploying",
                "createcasing:railway_deployer",
                "electroenergetics:transformer_core_lamination",
            ),
            sequence_step(
                "deploying",
                "createcasing:railway_deployer",
                "electroenergetics:transformer_core_lamination",
            ),
            sequence_step(
                "deploying", "createcasing:copper_deployer", "electroenergetics:copper_wire_spool"
            ),
            sequence_step(
                "deploying", "createcasing:copper_deployer", "electroenergetics:copper_wire_spool"
            ),
            sequence_step("pressing", "createcasing:railway_press"),
        ],
        "remove": {"electroenergetics:sequenced_assembly/transformer_core"},
    },
    "electroenergetics:miniature_circuit_breaker": {
        "id": "industrial_colonies:high_voltage/miniature_circuit_breaker",
        "phase": "High-Energy Grid",
        "order": 65,
        "type": "sequenced_assembly",
        "input": "#minecraft:terracotta",
        "transitional": "electroenergetics:incomplete_miniature_circuit_breaker",
        "loops": 1,
        "output_count": 1,
        "steps": [
            sequence_step(
                "deploying", "createcasing:railway_deployer", "electroenergetics:resistor"
            ),
            sequence_step(
                "deploying", "createcasing:railway_deployer", "electroenergetics:connector"
            ),
            sequence_step(
                "deploying", "createcasing:copper_deployer", "electroenergetics:insulated_wire"
            ),
            sequence_step(
                "deploying", "createcasing:copper_deployer", "electroenergetics:copper_wire_spool"
            ),
            sequence_step(
                "deploying", "createcasing:brass_deployer", "create:precision_mechanism"
            ),
            sequence_step("pressing", "createcasing:brass_press"),
        ],
        "remove": {"electroenergetics:sequenced_assembly/miniature_circuit_breaker"},
    },
}

EXPECTED_COMPILED_TYPES = {
    "cutting": "kjsgen:create_cutting",
    "pressing": "kjsgen:create_pressing",
    "sequenced_assembly": "kjsgen:create_sequenced_assembly",
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def item_value(value: Any) -> tuple[str, int] | None:
    if isinstance(value, str):
        matched = COUNTED_ITEM.fullmatch(value)
        if matched:
            return matched.group(2), int(matched.group(1))
        return value, 1
    if isinstance(value, dict) and value.get("kind", "ITEM") == "ITEM":
        item_id = value.get("id")
        count = value.get("count", 1)
        if isinstance(item_id, str) and isinstance(count, int) and not isinstance(count, bool):
            return item_id, count
    return None


def output_values(recipe: Mapping[str, Any]) -> list[tuple[str, int]]:
    raw = recipe.get("outputs")
    if not isinstance(raw, list):
        raw = [recipe.get("output")]
    return [parsed for value in raw if (parsed := item_value(value)) is not None]


def recipes_for_output(data: Mapping[str, Any], output: str) -> list[Mapping[str, Any]]:
    return [
        recipe
        for recipe in data.get("recipes", [])
        if isinstance(recipe, dict) and any(item_id == output for item_id, _ in output_values(recipe))
    ]


def validate_source_contract(data: Mapping[str, Any], label: str = "seed") -> list[str]:
    errors: list[str] = []
    for output, contract in CONTRACTS.items():
        candidates = recipes_for_output(data, output)
        if len(candidates) != 1:
            errors.append(f"{label}: {output} has {len(candidates)} recipes; expected exactly one")
            continue
        recipe = candidates[0]
        for field in ("id", "phase", "order", "type", "input"):
            if recipe.get(field) != contract[field]:
                errors.append(
                    f"{label}: {output} {field} is {recipe.get(field)!r}; expected {contract[field]!r}"
                )
        if recipe.get("exclusive_output") is not True:
            errors.append(f"{label}: {output} is not exclusive_output")
        actual_remove = {
            str(value) for value in recipe.get("remove", []) if isinstance(value, str)
        }
        if actual_remove != contract["remove"]:
            errors.append(
                f"{label}: {output} removal set is {sorted(actual_remove)}; "
                f"expected exactly {sorted(contract['remove'])}"
            )
        actual_outputs = [entry for entry in output_values(recipe) if entry[0] == output]
        if actual_outputs != [(output, contract["output_count"])]:
            errors.append(
                f"{label}: {output} output declaration is {actual_outputs}; "
                f"expected count {contract['output_count']}"
            )
        if contract["type"] == "sequenced_assembly":
            for field in ("transitional", "loops"):
                if recipe.get(field) != contract[field]:
                    errors.append(
                        f"{label}: {output} {field} is {recipe.get(field)!r}; "
                        f"expected {contract[field]!r}"
                    )
            if recipe.get("steps") != contract["steps"]:
                errors.append(f"{label}: {output} sequence operations or exact machines changed")
            transitional = recipe.get("transitional")
            if isinstance(transitional, str) and transitional.startswith("industrial_colonies:"):
                errors.append(
                    f"{label}: {output} invents custom transitional {transitional}; "
                    "this slice must use closed installed workpieces"
                )
        elif recipe.get("machine") != contract["machine"]:
            errors.append(
                f"{label}: {output} machine is {recipe.get('machine')!r}; "
                f"expected {contract['machine']}"
            )
    return errors


def compiled_output_values(recipe: Mapping[str, Any]) -> list[tuple[str, int]]:
    slots = recipe.get("slots", {})
    if not isinstance(slots, dict):
        return []
    return [
        parsed
        for key, value in slots.items()
        if (key.startswith("output") or key == "outItem")
        and (parsed := item_value(value)) is not None
    ]


def validate_compiled_contract(data: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    cards = [recipe for recipe in data.get("recipes", []) if isinstance(recipe, dict)]
    removals = {
        str(entry.get("recipeId"))
        for entry in data.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }
    for output, contract in CONTRACTS.items():
        candidates = [card for card in cards if card.get("recipeId") == contract["id"]]
        if len(candidates) != 1:
            errors.append(
                f"compiled: {contract['id']} has {len(candidates)} cards; expected exactly one"
            )
        else:
            card = candidates[0]
            expected_type = EXPECTED_COMPILED_TYPES[contract["type"]]
            if card.get("type") != expected_type:
                errors.append(
                    f"compiled: {contract['id']} type is {card.get('type')!r}; expected {expected_type}"
                )
            actual_outputs = [entry for entry in compiled_output_values(card) if entry[0] == output]
            if actual_outputs != [(output, contract["output_count"])]:
                errors.append(
                    f"compiled: {contract['id']} output declaration is {actual_outputs}; "
                    f"expected {output} x{contract['output_count']}"
                )
            if contract["type"] == "sequenced_assembly":
                params = card.get("params", {})
                if not isinstance(params, dict) or params.get("loops") != str(contract["loops"]):
                    errors.append(f"compiled: {contract['id']} loop count does not match source")
        producers = [card for card in cards if any(item == output for item, _ in compiled_output_values(card))]
        if len(producers) != 1:
            errors.append(f"compiled: {output} has {len(producers)} managed producers; expected one")
        missing_removals = sorted(contract["remove"] - removals)
        if missing_removals:
            errors.append(f"compiled: {output} is missing exact removals {missing_removals}")
    return errors


def expected_concrete_items() -> set[str]:
    result: set[str] = set(CONTRACTS)
    for contract in CONTRACTS.values():
        for field in ("input", "machine", "transitional"):
            value = contract.get(field)
            if isinstance(value, str) and not value.startswith("#"):
                result.add(value)
        for step in contract.get("steps", []):
            for field in ("ingredient", "machine"):
                value = step.get(field)
                if isinstance(value, str) and not value.startswith("#"):
                    result.add(value)
    return result


def load_catalog(catalog: Path) -> tuple[dict[str, set[str]], set[str], set[str]]:
    map_path = catalog / "item_recipe_map.csv"
    items_path = catalog / "items.csv"
    recipes_path = catalog / "recipes.csv"
    for path in (map_path, items_path, recipes_path):
        if not path.is_file():
            raise ValueError(f"catalog is missing {path.name}: {catalog}")
    producers = {output: set() for output in CONTRACTS}
    with map_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            output = str(row.get("item_id", ""))
            if output in producers and row.get("role") == "output" and row.get("recipe_id"):
                producers[output].add(str(row["recipe_id"]))
    with items_path.open("r", encoding="utf-8-sig", newline="") as handle:
        items = {str(row.get("item_id")) for row in csv.DictReader(handle) if row.get("item_id")}
    with recipes_path.open("r", encoding="utf-8-sig", newline="") as handle:
        recipe_ids = {
            str(row.get("recipe_id")) for row in csv.DictReader(handle) if row.get("recipe_id")
        }
    return producers, items, recipe_ids


def validate_catalog_contract(
    producers: Mapping[str, set[str]], items: set[str], recipe_ids: set[str]
) -> list[str]:
    errors: list[str] = []
    for output, contract in CONTRACTS.items():
        expected = set(contract["remove"])
        actual = set(producers.get(output, set()))
        if actual != expected:
            errors.append(
                f"catalog: producers for {output} are {sorted(actual)}; expected {sorted(expected)}"
            )
        missing_recipe_ids = sorted(expected - recipe_ids)
        if missing_recipe_ids:
            errors.append(f"catalog: exact stock recipe IDs are absent: {missing_recipe_ids}")
    missing_items = sorted(expected_concrete_items() - items)
    if missing_items:
        errors.append(f"catalog: required concrete item or machine IDs are absent: {missing_items}")
    return errors


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--manifest", type=Path, help="optional freshly assembled manifest")
    parser.add_argument("--compiled", type=Path, help="optional freshly compiled KJSGen project")
    parser.add_argument("--catalog", type=Path, help="optional static recipe catalog directory")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        errors = validate_source_contract(load_object(args.seed.resolve()), "seed")
        if args.manifest:
            errors.extend(validate_source_contract(load_object(args.manifest.resolve()), "manifest"))
        if args.compiled:
            errors.extend(validate_compiled_contract(load_object(args.compiled.resolve())))
        if args.catalog:
            errors.extend(validate_catalog_contract(*load_catalog(args.catalog.resolve())))
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print(f"FAIL: {len(errors)} processing-component hardening issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(
        "PASS: five skipped processing components have exact stock-route retirements, "
        "TFMG/Create Encased-first manufacturing, moderate loops, and closed transitionals."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
