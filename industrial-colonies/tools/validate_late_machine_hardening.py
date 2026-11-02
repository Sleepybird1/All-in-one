#!/usr/bin/env python3
"""Validate late-machine rebuilds and deliberately deferred teleport logistics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"


HARDENED_OUTPUTS: Mapping[str, str] = {
    "mekanism:basic_energy_cube": "mekanism:energy_cube/basic",
    "mekanism:advanced_energy_cube": "mekanism:energy_cube/advanced",
    "mekanism:elite_energy_cube": "mekanism:energy_cube/elite",
    "mekanism:ultimate_energy_cube": "mekanism:energy_cube/ultimate",
    "bigreactors:basic_turbinecontroller": "bigreactors:turbine/basic/controller",
    "bigreactors:reinforced_turbinecontroller": "bigreactors:turbine/reinforced/controller",
    "bigreactors:fluidizercontroller": "bigreactors:fluidizer/controller",
    "bigreactors:energizercontroller": "bigreactors:energizer/controller",
    "modernfoundry:smeltery_controller": "modernfoundry:smeltery/casting/seared/smeltery_controller",
    "modernfoundry:foundry_controller": "modernfoundry:smeltery/casting/scorched/foundry_controller",
}

# Crusher and Precision Sawmill were subsequently reviewed as part of the
# bounded pre-nuclear machine chain.  They remain physically hardened, but the
# correct construction language is now exact Create Encased compacting rather
# than a generic 5x5 grid.  Keep these two exceptions explicit so this older
# cross-audit cannot silently bless a different machine environment.
ENCASED_COMPACTING_OUTPUTS: Mapping[str, Mapping[str, str]] = {
    "mekanism:crusher": {
        "managed_id": "industrial_colonies:mekanism_pre_nuclear/crusher",
        "stock_id": "mekanism:crusher",
        "machine": "createcasing:railway_press",
    },
    "mekanism:precision_sawmill": {
        "managed_id": "industrial_colonies:mekanism_pre_nuclear/precision_sawmill",
        "stock_id": "mekanism:precision_sawmill",
        "machine": "createcasing:brass_press",
    },
}

# These outputs were subsequently assigned exact source-owned process
# contracts.  They deliberately replace the older blanket "every late block
# is a 5x5 ring" policy: repeatable structure shells and rotors are economical
# press batches, while the SPS port/final instrument use recognizable
# Refined-Radiance sequences.  Controllers remain in HARDENED_OUTPUTS above.
REVIEWED_PROCESS_OUTPUTS: Mapping[str, Mapping[str, Any]] = {
    "mekanism:sps_casing": {
        "managed_id": "industrial_colonies:mekanism_nuclear/sps_casing_batch",
        "type": "compacting",
        "machine": "createcasing:refined_radiance_press",
        "stock_ids": ["mekanism:sps_casing"],
    },
    "mekanism:sps_port": {
        "managed_id": "industrial_colonies:mekanism_nuclear/sps_port",
        "type": "sequenced_assembly",
        "stock_ids": ["mekanism:sps_port"],
    },
    "mekanism:supercharged_coil": {
        "managed_id": "industrial_colonies:mekanism_nuclear/supercharged_coil",
        "type": "compacting",
        "machine": "createcasing:refined_radiance_press",
        "stock_ids": ["mekanism:supercharged_coil"],
    },
    "mekanism:antiprotonic_nucleosynthesizer": {
        "managed_id": "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer",
        "type": "sequenced_assembly",
        "stock_ids": ["mekanism:antiprotonic_nucleosynthesizer"],
    },
    "bigreactors:energizercasing": {
        "managed_id": "industrial_colonies:bigreactors/energizer/casing",
        "type": "compacting",
        "machine": "createcasing:industrial_iron_press",
        "stock_ids": ["bigreactors:energizer/casing"],
    },
    "bigreactors:fluidizercasing": {
        "managed_id": "industrial_colonies:bigreactors/fluidizer/casing",
        "type": "compacting",
        "machine": "createcasing:industrial_iron_press",
        "stock_ids": ["bigreactors:fluidizer/casing"],
    },
    "bigreactors:basic_turbinecasing": {
        "managed_id": "industrial_colonies:bigreactors/basic_turbine/casing",
        "type": "compacting",
        "machine": "createcasing:industrial_iron_press",
        "stock_ids": [
            "bigreactors:turbine/basic/casing",
            "bigreactors:turbine/basic/casing_recycle",
            "bigreactors:turbine/basic/casing_recycle_glass",
        ],
    },
    "bigreactors:basic_turbinerotorbearing": {
        "managed_id": "industrial_colonies:bigreactors/basic_turbine/rotor_bearing",
        "type": "compacting",
        "machine": "createcasing:industrial_iron_press",
        "stock_ids": ["bigreactors:turbine/basic/bearing"],
    },
    "bigreactors:basic_turbinerotorblade": {
        "managed_id": "industrial_colonies:bigreactors/basic_turbine/rotor_blade",
        "type": "compacting",
        "machine": "createcasing:industrial_iron_press",
        "stock_ids": ["bigreactors:turbine/basic/blade"],
    },
    "bigreactors:basic_turbinerotorshaft": {
        "managed_id": "industrial_colonies:bigreactors/basic_turbine/rotor_shaft",
        "type": "compacting",
        "machine": "createcasing:industrial_iron_press",
        "stock_ids": ["bigreactors:turbine/basic/shaft"],
    },
    "bigreactors:reinforced_turbinecasing": {
        "managed_id": "industrial_colonies:bigreactors/reinforced_turbine/casing",
        "type": "compacting",
        "machine": "createcasing:refined_radiance_press",
        "stock_ids": [
            "bigreactors:turbine/reinforced/casing",
            "bigreactors:turbine/reinforced/casing_alt",
            "bigreactors:turbine/reinforced/casing_recycle",
            "bigreactors:turbine/reinforced/casing_recycle_glass",
            "bigreactors:turbine/reinforced/casing_upgrade",
            "bigreactors:turbine/reinforced/casing_upgrade_alt",
        ],
    },
    "bigreactors:reinforced_turbinerotorbearing": {
        "managed_id": "industrial_colonies:bigreactors/reinforced_turbine/rotor_bearing",
        "type": "compacting",
        "machine": "createcasing:refined_radiance_press",
        "stock_ids": [
            "bigreactors:turbine/reinforced/bearing",
            "bigreactors:turbine/reinforced/bearing_alt",
        ],
    },
    "bigreactors:reinforced_turbinerotorblade": {
        "managed_id": "industrial_colonies:bigreactors/reinforced_turbine/rotor_blade",
        "type": "compacting",
        "machine": "createcasing:refined_radiance_press",
        "stock_ids": [
            "bigreactors:turbine/reinforced/blade",
            "bigreactors:turbine/reinforced/blade_alt",
        ],
    },
    "bigreactors:reinforced_turbinerotorshaft": {
        "managed_id": "industrial_colonies:bigreactors/reinforced_turbine/rotor_shaft",
        "type": "compacting",
        "machine": "createcasing:refined_radiance_press",
        "stock_ids": [
            "bigreactors:turbine/reinforced/shaft",
            "bigreactors:turbine/reinforced/shaft_alt",
        ],
    },
}

DEFERRED_RECIPE_IDS = {
    "mekanism:portable_teleporter",
    "mekanism:qio_dashboard",
    "mekanism:qio_drive_array",
    "mekanism:quantum_entangloporter",
    "mekanism:teleporter",
}

DEFERRED_OUTPUTS = {
    "mekanism:portable_teleporter",
    "mekanism:qio_dashboard",
    "mekanism:qio_drive_array",
    "mekanism:quantum_entangloporter",
    "mekanism:teleporter",
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
            result.update(str(value) for value in recipe.get("remove", []) if isinstance(value, str))
    return result


def compiled_removals(compiled: Mapping[str, Any]) -> set[str]:
    return {
        str(entry.get("recipeId"))
        for entry in compiled.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }


def compiled_output_ids(compiled: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for recipe in compiled.get("recipes", []):
        if not isinstance(recipe, dict):
            continue
        slots = recipe.get("slots", {})
        if not isinstance(slots, dict):
            continue
        for key in ("output", "output0", "outItem"):
            slot = slots.get(key)
            if isinstance(slot, dict) and slot.get("kind") == "ITEM" and slot.get("id"):
                result.add(str(slot["id"]))
                break
    return result


def validate_contract(manifest: Mapping[str, Any], compiled: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    by_output: dict[str, list[dict[str, Any]]] = {}
    for raw in manifest.get("recipes", []):
        if not isinstance(raw, dict):
            continue
        by_output.setdefault(output_id(raw), []).append(raw)

    removals = manifest_removals(manifest)
    generated_removals = compiled_removals(compiled)
    for output, stock_id in HARDENED_OUTPUTS.items():
        recipes = by_output.get(output, [])
        if len(recipes) != 1:
            errors.append(f"{output} has {len(recipes)} managed recipes; expected exactly one")
            continue
        recipe = recipes[0]
        pattern = recipe.get("pattern", [])
        if recipe.get("type") != "mechanical_crafting":
            errors.append(f"{output} is not rebuilt with Mechanical Crafting")
        if not isinstance(pattern, list) or len(pattern) != 5 or any(
            not isinstance(row, str) or len(row) != 5 for row in pattern
        ):
            errors.append(f"{output} is not a complete 5x5 construction recipe")
        if stock_id not in removals:
            errors.append(f"{output} does not retire stock recipe {stock_id}")
        if stock_id not in generated_removals:
            errors.append(f"compiled KJSGen project does not remove {stock_id}")

    compiled_by_id = {
        str(recipe.get("recipeId", "")): recipe
        for recipe in compiled.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("recipeId"), str)
    }
    for output, contract in ENCASED_COMPACTING_OUTPUTS.items():
        recipes = by_output.get(output, [])
        if len(recipes) != 1:
            errors.append(f"{output} has {len(recipes)} managed recipes; expected exactly one")
            continue
        recipe = recipes[0]
        managed_id = contract["managed_id"]
        stock_id = contract["stock_id"]
        machine = contract["machine"]
        if recipe.get("id") != managed_id:
            errors.append(f"{output} is not owned by exact reviewed recipe {managed_id}")
        if recipe.get("type") != "compacting":
            errors.append(f"{output} is not rebuilt with exact Create Encased compacting")
        if recipe.get("machine") != machine:
            errors.append(f"{output} escaped reviewed machine environment {machine}")
        if stock_id not in removals:
            errors.append(f"{output} does not retire stock recipe {stock_id}")
        if stock_id not in generated_removals:
            errors.append(f"compiled KJSGen project does not remove {stock_id}")
        card = compiled_by_id.get(managed_id)
        if card is None:
            errors.append(f"compiled KJSGen project is missing reviewed recipe {managed_id}")
            continue
        if card.get("type") != "kjsgen:create_compacting":
            errors.append(f"compiled {managed_id} is not a Create compacting card")
        machine_slot = card.get("slots", {}).get("__machine_process_compacting", {})
        if not isinstance(machine_slot, dict) or machine_slot.get("id") != machine:
            errors.append(f"compiled {managed_id} escaped reviewed machine environment {machine}")

    compiled_type = {
        "compacting": "kjsgen:create_compacting",
        "sequenced_assembly": "kjsgen:create_sequenced_assembly",
    }
    for output, contract in REVIEWED_PROCESS_OUTPUTS.items():
        recipes = by_output.get(output, [])
        if len(recipes) != 1:
            errors.append(f"{output} has {len(recipes)} managed recipes; expected exactly one")
            continue
        recipe = recipes[0]
        managed_id = str(contract["managed_id"])
        recipe_type = str(contract["type"])
        machine = contract.get("machine")
        stock_ids = {str(value) for value in contract.get("stock_ids", [])}
        if recipe.get("id") != managed_id:
            errors.append(f"{output} is not owned by exact reviewed recipe {managed_id}")
        if recipe.get("type") != recipe_type:
            errors.append(f"{output} escaped reviewed {recipe_type} construction")
        if machine is not None and recipe.get("machine") != machine:
            errors.append(f"{output} escaped reviewed machine environment {machine}")
        missing_manifest = sorted(stock_ids - removals)
        if missing_manifest:
            errors.append(f"{output} does not retire stock recipes {missing_manifest}")
        missing_compiled = sorted(stock_ids - generated_removals)
        if missing_compiled:
            errors.append(
                f"compiled KJSGen project does not remove reviewed stock recipes {missing_compiled}"
            )
        card = compiled_by_id.get(managed_id)
        if card is None:
            errors.append(f"compiled KJSGen project is missing reviewed recipe {managed_id}")
            continue
        if card.get("type") != compiled_type[recipe_type]:
            errors.append(f"compiled {managed_id} escaped reviewed {recipe_type} card type")
        if machine is not None:
            machine_slot = card.get("slots", {}).get(
                "__machine_process_compacting", {}
            )
            if not isinstance(machine_slot, dict) or machine_slot.get("id") != machine:
                errors.append(
                    f"compiled {managed_id} escaped reviewed machine environment {machine}"
                )

    for label, values in (
        ("manifest", removals),
        ("compiled KJSGen project", generated_removals),
    ):
        missing = sorted(DEFERRED_RECIPE_IDS - values)
        if missing:
            errors.append(f"{label} is missing deferred teleport/QIO recipe IDs: {missing}")

    leaked_outputs = sorted(DEFERRED_OUTPUTS & compiled_output_ids(compiled))
    if leaked_outputs:
        errors.append(f"deferred teleport/QIO outputs still have managed producers: {leaked_outputs}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--compiled", type=Path, default=DEFAULT_COMPILED)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = validate_contract(
            load_object(args.manifest.resolve()),
            load_object(args.compiled.resolve()),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print(f"FAIL: {len(errors)} late-machine hardening issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {len(HARDENED_OUTPUTS)} controller/non-redundant late machines use managed 5x5 builds, "
        f"{len(ENCASED_COMPACTING_OUTPUTS)} pre-nuclear machines and "
        f"{len(REVIEWED_PROCESS_OUTPUTS)} nuclear/Big Reactors outputs use exact reviewed process contracts, and "
        f"{len(DEFERRED_RECIPE_IDS)} teleport/QIO entry recipes remain deferred."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
