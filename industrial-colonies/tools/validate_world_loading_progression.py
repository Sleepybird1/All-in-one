#!/usr/bin/env python3
"""Validate powered world-loading progression and FTB Chunks pack defaults.

The contract is deliberately narrow: retire AE2's free-power generator, rebuild
the two installed chunk-loading devices behind late-grid infrastructure, and
leave ordinary FTB Chunks claiming intact while its free force-load quota is 0.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
DEFAULT_CONFIG = PROJECT / "pack-config-overrides" / "ftbchunks-world.snbt"

WORLD_LOADING_NODE = "CR01 — World Loading Technology"
CRYSTAL_GENERATOR_RECIPE = "ae2:network/crystal_resonance_generator"
CRYSTAL_GENERATOR_OUTPUT = "ae2:crystal_resonance_generator"

HARDENED: Mapping[str, Mapping[str, Any]] = {
    "advancedperipherals:chunk_controller": {
        "managed_id": "industrial_colonies:world_loading/chunk_controller",
        "stock_id": "advancedperipherals:chunk_controller",
        "required": {
            "ae2:engineering_processor",
            "ae2:spatial_anchor",
            "computercraft:computer_advanced",
            "computercraft:wireless_modem_advanced",
            "mekanism:ultimate_energy_cube",
        },
    },
    "mekanism:dimensional_stabilizer": {
        "managed_id": "industrial_colonies:world_loading/dimensional_stabilizer",
        "stock_id": "mekanism:dimensional_stabilizer",
        "required": {
            "ae2:engineering_processor",
            "ae2:spatial_anchor",
            "computercraft:computer_advanced",
            "mekanism:ultimate_control_circuit",
            "mekanism:ultimate_energy_cube",
        },
    },
}

EXPECTED_NODE_OUTPUTS = {
    "ae2:spatial_anchor",
    *HARDENED.keys(),
}

EXPECTED_CATALOG_PRODUCERS = {
    CRYSTAL_GENERATOR_OUTPUT: {CRYSTAL_GENERATOR_RECIPE},
    **{
        output: {str(contract["stock_id"])}
        for output, contract in HARDENED.items()
    },
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def output_id(recipe: Mapping[str, Any]) -> str:
    value = recipe.get("output")
    if isinstance(value, str):
        parts = value.split(maxsplit=1)
        return parts[1] if len(parts) == 2 and parts[0].endswith("x") else value
    if isinstance(value, dict):
        return str(value.get("id", ""))
    return ""


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


def compiled_output_id(recipe: Mapping[str, Any]) -> str:
    slots = recipe.get("slots", {})
    if not isinstance(slots, dict):
        return ""
    for key in ("output", "output0", "outItem"):
        slot = slots.get(key)
        if isinstance(slot, dict) and slot.get("kind") == "ITEM" and slot.get("id"):
            return str(slot["id"])
    return ""


def used_ingredients(recipe: Mapping[str, Any]) -> set[str]:
    pattern = recipe.get("pattern", [])
    key = recipe.get("key", {})
    if not isinstance(pattern, list) or not isinstance(key, dict):
        return set()
    used_symbols = {
        symbol
        for row in pattern
        if isinstance(row, str)
        for symbol in row
        if not symbol.isspace()
    }
    result: set[str] = set()
    for symbol in used_symbols:
        value = key.get(symbol)
        if isinstance(value, str):
            result.add(value)
        elif isinstance(value, dict) and isinstance(value.get("id"), str):
            result.add(str(value["id"]))
    return result


def snbt_scalar(text: str, key: str) -> str | None:
    uncommented = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    matches = re.findall(
        rf"(?m)^\s*{re.escape(key)}\s*:\s*([^\s,}}]+)\s*,?\s*$",
        uncommented,
    )
    if len(matches) != 1:
        return None
    return matches[0].strip().strip('"')


def load_catalog_producers(catalog: Path) -> dict[str, set[str]]:
    source = catalog / "item_recipe_map.csv"
    if not source.is_file():
        raise ValueError(f"catalog is missing item_recipe_map.csv: {catalog}")
    wanted = set(EXPECTED_CATALOG_PRODUCERS)
    producers = {output: set() for output in wanted}
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            output = str(row.get("item_id", ""))
            if output in wanted and row.get("role") == "output":
                recipe_id = str(row.get("recipe_id", ""))
                if recipe_id:
                    producers[output].add(recipe_id)
    return producers


def validate_contract(
    manifest: Mapping[str, Any],
    compiled: Mapping[str, Any],
    assignments: Mapping[str, Any],
    config_text: str,
    catalog_producers: Mapping[str, set[str]] | None = None,
) -> list[str]:
    errors: list[str] = []
    by_output: dict[str, list[Mapping[str, Any]]] = {}
    for recipe in manifest.get("recipes", []):
        if isinstance(recipe, dict):
            by_output.setdefault(output_id(recipe), []).append(recipe)
    compiled_by_output: dict[str, list[Mapping[str, Any]]] = {}
    for recipe in compiled.get("recipes", []):
        if isinstance(recipe, dict):
            compiled_by_output.setdefault(compiled_output_id(recipe), []).append(recipe)

    manifest_removed = manifest_removals(manifest)
    compiled_removed = compiled_removals(compiled)
    for output, contract in HARDENED.items():
        recipes = by_output.get(output, [])
        if len(recipes) != 1:
            errors.append(f"{output} has {len(recipes)} managed recipes; expected exactly one")
        else:
            recipe = recipes[0]
            if recipe.get("id") != contract["managed_id"]:
                errors.append(
                    f"{output} uses managed ID {recipe.get('id')!r}; "
                    f"expected {contract['managed_id']}"
                )
            if recipe.get("phase") != "High-Energy Grid":
                errors.append(f"{output} is not assigned to the High-Energy Grid phase")
            if recipe.get("type") != "mechanical_crafting":
                errors.append(f"{output} is not rebuilt with Mechanical Crafting")
            pattern = recipe.get("pattern", [])
            if not isinstance(pattern, list) or len(pattern) != 5 or any(
                not isinstance(row, str) or len(row) != 5 for row in pattern
            ):
                errors.append(f"{output} is not a complete 5x5 construction recipe")
            if recipe.get("exclusive_output") is not True:
                errors.append(f"{output} is not marked exclusive_output")
            missing = sorted(set(contract["required"]) - used_ingredients(recipe))
            if missing:
                errors.append(f"{output} is missing physical gate ingredients: {missing}")

        stock_id = str(contract["stock_id"])
        if stock_id not in manifest_removed:
            errors.append(f"managed manifest does not remove stock recipe {stock_id}")
        if stock_id not in compiled_removed:
            errors.append(f"compiled KJSGen project does not remove stock recipe {stock_id}")
        compiled_recipes = compiled_by_output.get(output, [])
        if len(compiled_recipes) != 1:
            errors.append(
                f"compiled KJSGen project has {len(compiled_recipes)} producers for {output}; "
                "expected exactly one"
            )

    for label, removals in (
        ("managed manifest", manifest_removed),
        ("compiled KJSGen project", compiled_removed),
    ):
        if CRYSTAL_GENERATOR_RECIPE not in removals:
            errors.append(f"{label} does not retire {CRYSTAL_GENERATOR_RECIPE}")
    if by_output.get(CRYSTAL_GENERATOR_OUTPUT):
        errors.append(f"managed manifest still produces retired {CRYSTAL_GENERATOR_OUTPUT}")
    if compiled_by_output.get(CRYSTAL_GENERATOR_OUTPUT):
        errors.append(f"compiled KJSGen project still produces retired {CRYSTAL_GENERATOR_OUTPUT}")

    nodes = assignments.get("nodes", {})
    node = nodes.get(WORLD_LOADING_NODE, {}) if isinstance(nodes, dict) else {}
    unlocks = {
        str(value)
        for value in node.get("unlocks", [])
        if isinstance(value, str)
    } if isinstance(node, dict) else set()
    if unlocks != EXPECTED_NODE_OUTPUTS:
        errors.append(
            f"{WORLD_LOADING_NODE} unlocks {sorted(unlocks)}; "
            f"expected {sorted(EXPECTED_NODE_OUTPUTS)}"
        )
    assigned_outputs = {
        str(value)
        for candidate in nodes.values()
        if isinstance(candidate, dict)
        for value in candidate.get("unlocks", [])
        if isinstance(value, str)
    } if isinstance(nodes, dict) else set()
    if CRYSTAL_GENERATOR_OUTPUT in assigned_outputs:
        errors.append(
            f"retired {CRYSTAL_GENERATOR_OUTPUT} is still assigned to a progression node"
        )

    if snbt_scalar(config_text, "disable_protection") != "false":
        errors.append("FTB Chunks disable_protection must remain false so claims still protect land")
    claimed = snbt_scalar(config_text, "max_claimed_chunks")
    try:
        claimed_limit = int(claimed) if claimed is not None else 0
    except ValueError:
        claimed_limit = 0
    if claimed_limit <= 0:
        errors.append("FTB Chunks max_claimed_chunks must remain positive")
    if snbt_scalar(config_text, "max_force_loaded_chunks") != "0":
        errors.append("FTB Chunks max_force_loaded_chunks must be 0")
    if snbt_scalar(config_text, "force_load_mode") != "default":
        errors.append("FTB Chunks force_load_mode must remain default")
    if snbt_scalar(config_text, "hard_team_force_limit") != "0":
        errors.append(
            "FTB Chunks hard_team_force_limit must remain 0; in this codec 0 means no extra "
            "hard cap, while max_force_loaded_chunks supplies the zero quota"
        )

    if catalog_producers is not None:
        for output, expected in EXPECTED_CATALOG_PRODUCERS.items():
            actual = set(catalog_producers.get(output, set()))
            if actual != expected:
                errors.append(
                    f"catalog producers for {output} are {sorted(actual)}; "
                    f"expected {sorted(expected)}"
                )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--compiled", type=Path, default=DEFAULT_COMPILED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--catalog", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        catalog_producers = (
            load_catalog_producers(args.catalog.resolve()) if args.catalog else None
        )
        errors = validate_contract(
            load_object(args.manifest.resolve()),
            load_object(args.compiled.resolve()),
            load_object(args.assignments.resolve()),
            args.config.resolve().read_text(encoding="utf-8-sig"),
            catalog_producers,
        )
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print(f"FAIL: {len(errors)} world-loading progression issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(
        "PASS: AE2 free power is retired, both installed chunk loaders use powered "
        "5x5 builds, and FTB Chunks preserves claims with a zero force-load quota."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
