#!/usr/bin/env python3
"""Validate exact retirement of confirmed progression-bypass recipes.

This contract is intentionally narrow.  It does not remove whole namespaces or
machine categories; it names only routes whose live behavior directly defeats
the current physical factory, logistics, chemistry, tool, or exploration
progression.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"

EQUIPMENT = (
    "axe",
    "boots",
    "chestplate",
    "helmet",
    "hoe",
    "leggings",
    "mace",
    "pickaxe",
    "shovel",
    "sword",
)
ATM_METALS = ("allthemodium", "vibranium", "unobtainium")

ATM_EQUIPMENT_RECIPE_IDS = {
    f"allthemodium:smithing/{metal}_{equipment}_smithing"
    for metal in ATM_METALS
    for equipment in EQUIPMENT
}
ATM_EQUIPMENT_OUTPUTS = {
    f"allthemodium:{metal}_{equipment}"
    for metal in ATM_METALS
    for equipment in EQUIPMENT
}

SECURITYCRAFT_MINE_PATHS = {
    "ancient_debris_mine",
    "blast_furnace_mine",
    "coal_mine",
    "cobbled_deepslate_mine",
    "cobblestone_mine",
    "copper_mine",
    "deepslate_coal_mine",
    "deepslate_copper_mine",
    "deepslate_diamond_mine",
    "deepslate_emerald_mine",
    "deepslate_gold_mine",
    "deepslate_iron_mine",
    "deepslate_lapis_mine",
    "deepslate_mine",
    "deepslate_redstone_mine",
    "diamond_mine",
    "dirt_mine",
    "emerald_mine",
    "end_stone_mine",
    "furnace_mine",
    "gilded_blackstone_mine",
    "gold_mine",
    "gravel_mine",
    "iron_mine",
    "lapis_mine",
    "mine",
    "nether_gold_mine",
    "netherrack_mine",
    "quartz_mine",
    "redstone_mine",
    "remote_access_mine",
    "sand_mine",
    "smoker_mine",
    "stone_mine",
    "suspicious_gravel_mine",
    "suspicious_sand_mine",
    "track_mine",
}
SECURITYCRAFT_MINE_RECIPE_IDS = {
    f"securitycraft:{path}" for path in SECURITYCRAFT_MINE_PATHS
}
SECURITYCRAFT_MINE_OUTPUTS = set(SECURITYCRAFT_MINE_RECIPE_IDS)

AE2_QUANTUM_RECIPE_IDS = {
    "ae2:network/blocks/quantum_link",
    "ae2:network/blocks/quantum_ring",
    "ae2:transform/entangled_singularity",
    "ae2:transform/entangled_singularity_from_pearl",
}
AE2_QUANTUM_OUTPUTS = {
    "ae2:quantum_link",
    "ae2:quantum_ring",
}
REQUIRED_MANUFACTURED_QUANTUM_OUTPUTS = {"ae2:quantum_entangled_singularity"}

# The cheap explosion transforms remain retired with the bridge blocks, but
# the paired singularity is now manufactured late as an Interstellar Escape
# component.  Treating the component itself as a forbidden output made the
# navigation computer, route crystal, crystal driver, and Warp Drive
# unreachable even though none of them restores AE2 teleportation.

MEKANISM_RETIRED_RECIPE_IDS = {
    "mekanism:atomic_disassembler",
    "mekanism:digital_miner",
    "mekanism:energized_smelter",
    "mekanism:factory/advanced/smelting",
    "mekanism:factory/basic/smelting",
    "mekanism:factory/elite/smelting",
    "mekanism:factory/ultimate/smelting",
    "mekanism:formulaic_assemblicator",
    "mekanism:free_runners",
    "mekanism:free_runners_armored",
    "mekanism:jetpack",
    "mekanism:jetpack_armored",
    "mekanism:meka_tool",
}
MEKANISM_RETIRED_OUTPUTS = {
    "mekanism:advanced_smelting_factory",
    "mekanism:basic_smelting_factory",
    "mekanism:digital_miner",
    "mekanism:elite_smelting_factory",
    "mekanism:energized_smelter",
    "mekanism:formulaic_assemblicator",
    "mekanism:jetpack_armored",
    "mekanism:meka_tool",
    "mekanism:ultimate_smelting_factory",
}

# These four mobility/tool outputs are no longer deleted outright.  Their
# cheap stock recipe IDs remain in MEKANISM_RETIRED_RECIPE_IDS, while the
# managed overhaul restores them as staged physical assemblies.  This keeps
# tool progression meaningful without turning the equipment into dead content.
REQUIRED_HARDENED_MEKANISM_OUTPUTS = {
    "mekanism:atomic_disassembler",
    "mekanism:free_runners",
    "mekanism:free_runners_armored",
    "mekanism:jetpack",
}

EXACT_RECIPE_RETIREMENTS = (
    ATM_EQUIPMENT_RECIPE_IDS
    | SECURITYCRAFT_MINE_RECIPE_IDS
    | AE2_QUANTUM_RECIPE_IDS
    | MEKANISM_RETIRED_RECIPE_IDS
    | {"allthemodium:teleport_pad"}
)

NO_MANAGED_PRODUCER_OUTPUTS = (
    ATM_EQUIPMENT_OUTPUTS
    | SECURITYCRAFT_MINE_OUTPUTS
    | AE2_QUANTUM_OUTPUTS
    | MEKANISM_RETIRED_OUTPUTS
    | {"allthemodium:teleport_pad"}
)

# These are the intended industrial alternatives.  Removing them would turn an
# exact bypass closure into an accidental dead end.
PROTECTED_FACTORY_ROUTES = {
    "create_ultimate_factory:compacting_coalblock",
    "create_ultimate_factory:crushing_netherite",
    "mekanism:processing/lategame/antimatter_pellet/from_gas",
    "mekanism:processing/lategame/polonium_pellet/from_reaction",
    "mekanism:rotary/superheated_sodium",
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def manifest_removals(manifest: Mapping[str, Any]) -> set[str]:
    removals = {
        str(value)
        for value in manifest.get("additional_removals", [])
        if isinstance(value, str)
    }
    for recipe in manifest.get("recipes", []):
        if isinstance(recipe, dict):
            removals.update(
                str(value) for value in recipe.get("remove", []) if isinstance(value, str)
            )
    return removals


def compiled_removals(compiled: Mapping[str, Any]) -> set[str]:
    return {
        str(entry.get("recipeId"))
        for entry in compiled.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }


def manifest_output_ids(manifest: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for recipe in manifest.get("recipes", []):
        if not isinstance(recipe, dict):
            continue
        output = recipe.get("output")
        if isinstance(output, str):
            parts = output.split(maxsplit=1)
            result.add(parts[1] if len(parts) == 2 and parts[0].endswith("x") else output)
        elif isinstance(output, dict) and isinstance(output.get("id"), str):
            result.add(str(output["id"]))
    return result


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


def assignment_outputs(assignments: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    nodes = assignments.get("nodes", {})
    if not isinstance(nodes, dict):
        return result
    for node in nodes.values():
        if isinstance(node, dict):
            result.update(
                str(value) for value in node.get("unlocks", []) if isinstance(value, str)
            )
    return result


def missing(label: str, expected: Iterable[str], actual: set[str]) -> list[str]:
    values = sorted(set(expected) - actual)
    return [f"{label} is missing exact recipe removal {value}" for value in values]


def validate_contract(
    manifest: Mapping[str, Any],
    compiled: Mapping[str, Any],
    assignments: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    manifest_removed = manifest_removals(manifest)
    compiled_removed = compiled_removals(compiled)
    errors.extend(missing("managed manifest", EXACT_RECIPE_RETIREMENTS, manifest_removed))
    errors.extend(missing("compiled KJSGen project", EXACT_RECIPE_RETIREMENTS, compiled_removed))

    for label, outputs in (
        ("managed manifest", manifest_output_ids(manifest)),
        ("compiled KJSGen project", compiled_output_ids(compiled)),
        ("machine-node assignments", assignment_outputs(assignments)),
    ):
        leaked = sorted(NO_MANAGED_PRODUCER_OUTPUTS & outputs)
        if leaked:
            errors.append(f"{label} still exposes retired outputs: {leaked}")

    for label, outputs in (
        ("managed manifest", manifest_output_ids(manifest)),
        ("compiled KJSGen project", compiled_output_ids(compiled)),
    ):
        absent = sorted(REQUIRED_MANUFACTURED_QUANTUM_OUTPUTS - outputs)
        if absent:
            errors.append(
                f"{label} is missing the controlled late quantum component: {absent}"
            )
        absent = sorted(REQUIRED_HARDENED_MEKANISM_OUTPUTS - outputs)
        if absent:
            errors.append(
                f"{label} is missing hardened Mekanism equipment: {absent}"
            )

    for label, removals in (
        ("managed manifest", manifest_removed),
        ("compiled KJSGen project", compiled_removed),
    ):
        overremoved = sorted(PROTECTED_FACTORY_ROUTES & removals)
        if overremoved:
            errors.append(f"{label} removes protected industrial alternatives: {overremoved}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--compiled", type=Path, default=DEFAULT_COMPILED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = validate_contract(
            load_object(args.manifest.resolve()),
            load_object(args.compiled.resolve()),
            load_object(args.assignments.resolve()),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print(f"FAIL: {len(errors)} progression-bypass retirement issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {len(EXACT_RECIPE_RETIREMENTS)} confirmed bypass recipes are retired "
        f"without removing {len(PROTECTED_FACTORY_ROUTES)} protected industrial routes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
