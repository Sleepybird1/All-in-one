#!/usr/bin/env python3
"""Validate the authored late-digital and Applied Create kinetic gateways.

The target mods ship several compact recipes that collapse remote kinetic
transport, ExtendedAE processing, AdvancedAE reactions, and MEGA storage into
ordinary 3x3 crafting.  This contract keeps those features available while
requiring the pack's TFMG-first electronics and exact Create manufacturing
environments.  It also verifies that stress P2P attunement is keyed by the
finished ME Gearbox instead of an early shaft or cog.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
DEFAULT_TAG_SCRIPT = (
    PROJECT / "pack-scripts" / "server_scripts" / "industrial_appliedcreate_kinetic_network.js"
)

EXPECTED: Mapping[str, Mapping[str, Any]] = {
    "appliedcreate:kinetic_energy_acceptor": {
        "type": "sequenced_assembly",
        "stock": {"appliedcreate:kinetic_energy_acceptor"},
        "ingredients": {
            "ae2:energy_acceptor",
            "ae2:fluix_smart_dense_cable",
            "appliedcreate:advanced_stress_processor",
            "create:gearbox",
            "tfmg:electric_motor",
            "tfmg:generator",
            "tfmg:steel_frame",
            "tfmg:transformer",
        },
        "loops": 1,
        "transitional": "ae2:energy_acceptor",
        "machines": {
            "createcasing:weathered_iron_deployer",
            "createcasing:weathered_iron_press",
        },
    },
    "appliedcreate:stress_storage_component_1k": {
        "type": "sequenced_assembly",
        "stock": {"appliedcreate:stress_storage_component_1k"},
        "ingredients": {
            "ae2:cell_component_4k",
            "appliedcreate:stress_processor",
            "tfmg:capacitor_item",
            "tfmg:copper_wire",
            "tfmg:magnetic_alloy_sheet",
        },
        "loops": 2,
        "transitional": "industrial_colonies:unfinished_stress_storage_component",
        "machines": {
            "createcasing:brass_deployer",
            "createcasing:brass_press",
        },
    },
    "appliedcreate:me_gearbox": {
        "type": "sequenced_assembly",
        "stock": {"appliedcreate:me_gearbox"},
        "ingredients": {
            "ae2:fluix_smart_dense_cable",
            "ae2:me_p2p_tunnel",
            "appliedcreate:advanced_stress_processor",
            "create:gearbox",
            "create:railway_casing",
            "tfmg:electric_motor",
            "tfmg:magnetic_alloy_sheet",
            "tfmg:steel_frame",
        },
        "loops": 1,
        "transitional": "create:gearbox",
        "machines": {
            "createcasing:railway_deployer",
            "createcasing:railway_press",
        },
    },
    "extendedae:machine_frame": {
        "type": "mechanical_crafting",
        "stock": {"extendedae:machine_frame", "extendedae:machine_frame_mirror"},
        "ingredients": {
            "ae2:fluix_smart_cable",
            "appliedcreate:advanced_stress_processor",
            "extendedae:entro_ingot",
            "tfmg:steel_casing",
            "tfmg:steel_mechanism",
        },
        "grid_size": 3,
    },
    "extendedae:crystal_assembler": {
        "type": "mechanical_crafting",
        "stock": {"extendedae:crystal_assembler"},
        "ingredients": {
            "ae2:crafting_terminal",
            "ae2:engineering_processor",
            "ae2:sky_stone_tank",
            "create:mechanical_arm",
            "extendedae:machine_frame",
        },
        "grid_size": 3,
    },
    "advanced_ae:reaction_chamber": {
        "type": "mechanical_crafting",
        "stock": {"advanced_ae:reactionchamber"},
        "ingredients": {
            "ae2:condenser",
            "ae2:engineering_processor",
            "ae2:vibration_chamber",
            "extendedae:machine_frame",
            "mekanism:pressurized_reaction_chamber",
            "tfmg:heavy_machinery_casing",
        },
        "grid_size": 5,
    },
    "megacells:cell_component_1m": {
        "type": "sequenced_assembly",
        "stock": {"megacells:cells/cell_component_1m"},
        "ingredients": {
            "ae2:cell_component_256k",
            "ae2:cell_component_256k",
            "ae2:quartz_vibrant_glass",
            "ae2:sky_dust",
            "appliedcreate:advanced_stress_processor",
            "megacells:accumulation_processor",
            "tfmg:lithium_block",
            "tfmg:magnetic_alloy_sheet",
            "tfmg:plastic_sheet",
        },
        "loops": 1,
        "transitional": "ae2:cell_component_256k",
        "machines": {
            "createcasing:railway_deployer",
            "createcasing:railway_press",
        },
    },
}

EXPECTED_ASSIGNMENTS = {
    "CR01 — P2P Tunneling Technology": {
        "appliedcreate:kinetic_energy_acceptor",
        "appliedcreate:stress_storage_component_1k",
        "appliedcreate:me_gearbox",
    },
    "CR01 — Enhanced ME System Upgrade": {
        "extendedae:machine_frame",
        "extendedae:crystal_assembler",
    },
    "CR01 — Overclocked Processors": {
        "advanced_ae:reaction_chamber",
        "megacells:cell_component_1m",
    },
}

TRANSITIONAL_REGISTRATIONS = {
    "unfinished_stress_storage_component": "unfinished_stress_storage_component.json",
    "unfinished_mega_cell_component_1m": "unfinished_mega_cell_component_1m.json",
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def output_id(recipe: Mapping[str, Any]) -> str:
    output = recipe.get("output")
    if isinstance(output, str):
        parts = output.split(maxsplit=1)
        return parts[1] if len(parts) == 2 and parts[0].endswith("x") else output
    if isinstance(output, dict):
        return str(output.get("id", ""))
    outputs = recipe.get("outputs")
    if isinstance(outputs, list) and len(outputs) == 1 and isinstance(outputs[0], dict):
        return str(outputs[0].get("id", ""))
    return ""


def resource_id(value: Any) -> str:
    if isinstance(value, str):
        value = value.lstrip("#")
        parts = value.split(maxsplit=1)
        return parts[1] if len(parts) == 2 and parts[0].endswith("x") else value
    if isinstance(value, dict):
        return str(value.get("id", "")).lstrip("#")
    return ""


def ingredients(recipe: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for value in recipe.get("key", {}).values():
        result.add(resource_id(value))
    for field in ("input", "held"):
        if field in recipe:
            result.add(resource_id(recipe[field]))
    for value in recipe.get("inputs", []):
        result.add(resource_id(value))
    for step in recipe.get("steps", []):
        if isinstance(step, dict) and "ingredient" in step:
            result.add(resource_id(step["ingredient"]))
    result.discard("")
    return result


def manifest_removals(manifest: Mapping[str, Any]) -> set[str]:
    result = {
        str(value)
        for value in manifest.get("additional_removals", [])
        if isinstance(value, str)
    }
    for recipe in manifest.get("recipes", []):
        if isinstance(recipe, dict):
            result.update(
                str(value)
                for value in recipe.get("remove", [])
                if isinstance(value, str)
            )
    return result


def compiled_removals(compiled: Mapping[str, Any]) -> set[str]:
    return {
        str(entry.get("recipeId"))
        for entry in compiled.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }


def compiled_output(recipe: Mapping[str, Any]) -> str:
    slots = recipe.get("slots", {})
    if not isinstance(slots, dict):
        return ""
    for key in ("output", "output0", "outItem"):
        value = slots.get(key)
        if isinstance(value, dict) and value.get("kind") == "ITEM":
            return str(value.get("id", ""))
    return ""


def validate_contract(
    project: Path,
    manifest: Mapping[str, Any],
    compiled: Mapping[str, Any],
    assignments: Mapping[str, Any],
    tag_script: str,
) -> list[str]:
    errors: list[str] = []
    by_output: dict[str, list[dict[str, Any]]] = {}
    for raw in manifest.get("recipes", []):
        if isinstance(raw, dict):
            by_output.setdefault(output_id(raw), []).append(raw)

    all_stock_ids: set[str] = set()
    for output, contract in EXPECTED.items():
        all_stock_ids.update(contract["stock"])
        recipes = by_output.get(output, [])
        if len(recipes) != 1:
            errors.append(f"{output} has {len(recipes)} managed recipes; expected exactly one")
            continue
        recipe = recipes[0]
        if recipe.get("type") != contract["type"]:
            errors.append(
                f"{output} uses {recipe.get('type')!r}; expected {contract['type']!r}"
            )
        actual_ingredients = ingredients(recipe)
        missing = sorted(set(contract["ingredients"]) - actual_ingredients)
        if missing:
            errors.append(f"{output} is missing authored gateway ingredients: {missing}")
        if recipe.get("type") == "mechanical_crafting":
            pattern = recipe.get("pattern")
            grid_size = int(contract.get("grid_size", 5))
            if not isinstance(pattern, list) or len(pattern) != grid_size or any(
                not isinstance(row, str) or len(row) != grid_size for row in pattern
            ):
                errors.append(
                    f"{output} is not its reviewed {grid_size}x{grid_size} construction recipe"
                )
            if len(recipe.get("key", {})) < 6:
                errors.append(f"{output} collapsed to a formulaic low-variety grid")
        else:
            if recipe.get("loops") != contract["loops"]:
                errors.append(
                    f"{output} uses {recipe.get('loops')} loops; expected {contract['loops']}"
                )
            if recipe.get("transitional") != contract["transitional"]:
                errors.append(f"{output} lost its closed transitional item")
            machines = {
                str(step.get("machine", ""))
                for step in recipe.get("steps", [])
                if isinstance(step, dict)
            }
            expected_machines = set(contract.get("machines", set()))
            if machines != expected_machines:
                errors.append(
                    f"{output} uses machines {sorted(machines)}; "
                    f"expected {sorted(expected_machines)}"
                )

    for label, removals in (
        ("manifest", manifest_removals(manifest)),
        ("compiled KJSGen project", compiled_removals(compiled)),
    ):
        missing = sorted(all_stock_ids - removals)
        if missing:
            errors.append(f"{label} is missing exact late-digital removals: {missing}")

    compiled_by_output: dict[str, list[dict[str, Any]]] = {}
    for raw in compiled.get("recipes", []):
        if isinstance(raw, dict):
            compiled_by_output.setdefault(compiled_output(raw), []).append(raw)
    for output, contract in EXPECTED.items():
        recipes = compiled_by_output.get(output, [])
        if len(recipes) != 1:
            errors.append(
                f"compiled KJSGen project has {len(recipes)} managed producers for {output}"
            )
            continue
        expected_type = (
            "kjsgen:create_mechanical_crafting"
            if contract["type"] == "mechanical_crafting"
            else "kjsgen:create_sequenced_assembly"
        )
        if recipes[0].get("type") != expected_type:
            errors.append(f"compiled {output} lost its authored recipe environment")

    nodes = assignments.get("nodes", {})
    for node, expected_outputs in EXPECTED_ASSIGNMENTS.items():
        actual = set(nodes.get(node, {}).get("unlocks", []))
        missing = sorted(expected_outputs - actual)
        if missing:
            errors.append(f"{node} is missing late-digital assignments: {missing}")

    attunement = "appliedcreate:p2p_attunements/stress_p2p_tunnel"
    if f"event.removeAll(stressAttunement)" not in tag_script or attunement not in tag_script:
        errors.append("stress P2P attunement tag is not cleared before replacement")
    if "event.add(stressAttunement, 'appliedcreate:me_gearbox')" not in tag_script:
        errors.append("stress P2P attunement is not keyed by appliedcreate:me_gearbox")
    for cheap_key in (
        "'create:shaft'",
        "'create:cogwheel'",
        "'create:large_cogwheel'",
        "'create:gearbox'",
        "'create:hand_crank'",
    ):
        if cheap_key in tag_script:
            errors.append(f"stress P2P attunement still exposes cheap key {cheap_key}")

    item_source = (
        project / "src" / "main" / "java" / "dev" / "godpc" / "industrialcolonies" / "IndustrialItems.java"
    )
    models = project / "src" / "main" / "resources" / "assets" / "industrial_colonies" / "models" / "item"
    lang = project / "src" / "main" / "resources" / "assets" / "industrial_colonies" / "lang" / "en_us.json"
    try:
        item_text = item_source.read_text(encoding="utf-8-sig")
        language = load_object(lang)
        for item_id, model_name in TRANSITIONAL_REGISTRATIONS.items():
            if f'"{item_id}"' not in item_text:
                errors.append(f"custom transitional item is not registered: {item_id}")
            if not (models / model_name).is_file():
                errors.append(f"custom transitional item has no model: {model_name}")
            if f"item.industrial_colonies.{item_id}" not in language:
                errors.append(f"custom transitional item has no language entry: {item_id}")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"cannot validate custom transitional resources: {exc}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--compiled", type=Path, default=DEFAULT_COMPILED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--tag-script", type=Path, default=DEFAULT_TAG_SCRIPT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = validate_contract(
            PROJECT,
            load_object(args.manifest.resolve()),
            load_object(args.compiled.resolve()),
            load_object(args.assignments.resolve()),
            args.tag_script.resolve().read_text(encoding="utf-8-sig"),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print(f"FAIL: {len(errors)} late-digital gateway issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(
        "PASS: 7 late-digital outputs use authored high-energy manufacturing; "
        "8 stock recipes are retired and stress P2P attunement requires the ME Gearbox."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
