#!/usr/bin/env python3
"""Validate the source-owned petroleum extraction, refining, and engine slice.

The legacy oil-field script is intentionally only a migration marker.  These
recipes must therefore live in the managed-recipe seed, remove only their
installed stock recipe IDs, and compile without the generic ABABA phase ring.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
PUMPJACK_PIPE_TAG = (
    PROJECT / "src" / "main" / "resources" / "data" / "tfmg" / "tags" / "block" / "industrial_pipe.json"
)

OIL_NODE = "CR01 — Oil processing"
EARLY_ENGINE_NODE = "CR01 — Early Combusion Engines"
DISTILLATION_NODE = "CR01 — Diesel Processing"
DIESEL_NODE = "CR01 — Diesel Engines"
HEAVY_DIESEL_NODE = "CR01 — Heavy Diesel Engines"
RADIAL_NODE = "CR01 — Radial Engines"


def spec(
    recipe_id: str,
    recipe_type: str,
    removal: str,
    count: int,
    node: str,
    grid: int,
    ingredients: set[str],
) -> dict[str, Any]:
    return {
        "id": recipe_id,
        "type": recipe_type,
        "remove": removal,
        "count": count,
        "node": node,
        "grid": grid,
        "ingredients": ingredients,
    }


EXPECTED: Mapping[str, Mapping[str, Any]] = {
    "tfmg:surface_scanner": spec(
        "industrial_colonies:machine/oil_processing/surface_scanner",
        "shaped",
        "tfmg:crafting/materials/surface_scanner",
        1,
        OIL_NODE,
        3,
        {
            "create:content_observer",
            "create:precision_mechanism",
            "create:brass_casing",
            "tfmg:cast_iron_frame",
        },
    ),
    "tfmg:pumpjack_base": spec(
        "industrial_colonies:machine/oil_processing/pumpjack_base",
        "mechanical_crafting",
        "tfmg:crafting/materials/pumpjack_base",
        1,
        OIL_NODE,
        5,
        {
            "#c:strings",
            "tfmg:cast_iron_mechanical_pump",
            "tfmg:cast_iron_fluid_tank",
            "tfmg:cast_iron_pipe",
            "create:brass_casing",
            "create:precision_mechanism",
        },
    ),
    "tfmg:pumpjack_crank": spec(
        "industrial_colonies:machine/oil_processing/pumpjack_crank",
        "mechanical_crafting",
        "tfmg:crafting/materials/pumpjack_crank",
        1,
        OIL_NODE,
        5,
        {
            "#c:strings",
            "tfmg:cast_iron_truss",
            "create:precision_mechanism",
            "create:shaft",
            "create:brass_casing",
        },
    ),
    "tfmg:pumpjack_hammer": spec(
        "industrial_colonies:machine/oil_processing/pumpjack_hammer",
        "mechanical_crafting",
        "tfmg:crafting/materials/pumpjack_hammer",
        1,
        OIL_NODE,
        5,
        {
            "tfmg:cast_iron_ingot",
            "tfmg:cast_iron_frame",
            "tfmg:cast_iron_truss",
            "create:brass_casing",
        },
    ),
    "tfmg:pumpjack_hammer_part": spec(
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_part",
        "shaped",
        "tfmg:pumpjack_hammer_part_from_storage_blocks_steel_stonecutting",
        2,
        OIL_NODE,
        3,
        {"tfmg:cast_iron_block"},
    ),
    "tfmg:large_pumpjack_hammer_part": spec(
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part",
        "shaped",
        "tfmg:large_pumpjack_hammer_part_from_storage_blocks_steel_stonecutting",
        2,
        OIL_NODE,
        3,
        {"tfmg:cast_iron_block"},
    ),
    "tfmg:pumpjack_hammer_connector": spec(
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_connector",
        "shaped",
        "tfmg:crafting/materials/pumpjack_hammer_connector",
        1,
        OIL_NODE,
        3,
        {"create:brass_ingot", "tfmg:pumpjack_hammer_part"},
    ),
    "tfmg:large_pumpjack_hammer_connector": spec(
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector",
        "shaped",
        "tfmg:crafting/materials/large_pumpjack_hammer_connector",
        1,
        OIL_NODE,
        3,
        {"create:brass_ingot", "tfmg:large_pumpjack_hammer_part"},
    ),
    "tfmg:pumpjack_hammer_head": spec(
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_head",
        "shaped",
        "tfmg:crafting/materials/pumpjack_hammer_head",
        1,
        OIL_NODE,
        3,
        {"tfmg:cast_iron_block", "tfmg:cast_iron_sheet"},
    ),
    "tfmg:large_pumpjack_hammer_head": spec(
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head",
        "shaped",
        "tfmg:crafting/materials/large_pumpjack_hammer_head",
        1,
        OIL_NODE,
        3,
        {"tfmg:cast_iron_block", "tfmg:cast_iron_sheet"},
    ),
    "tfmg:oil_hammer": spec(
        "industrial_colonies:machine/oil_processing/oil_hammer",
        "shaped",
        "tfmg:crafting/materials/oil_hammer",
        1,
        OIL_NODE,
        3,
        {"tfmg:cast_iron_ingot", "create:brass_ingot", "#c:rods/wooden"},
    ),
    "tfmg:oil_can": spec(
        "industrial_colonies:machine/oil_processing/oil_can",
        "shaped",
        "tfmg:crafting/materials/oil_can",
        1,
        OIL_NODE,
        3,
        {"tfmg:cast_iron_nugget", "create:brass_ingot"},
    ),
    "tfmg:steel_distillation_controller": spec(
        "industrial_colonies:petroleum/steel_distillation_controller",
        "mechanical_crafting",
        "tfmg:crafting/materials/steel_distillation_controller",
        1,
        DISTILLATION_NODE,
        5,
        {
            "#c:plates/lead",
            "tfmg:industrial_pipe",
            "create:electron_tube",
            "minecraft:compass",
            "tfmg:steel_mechanism",
            "tfmg:heavy_machinery_casing",
            "tfmg:steel_fluid_tank",
        },
    ),
    "tfmg:steel_distillation_output": spec(
        "industrial_colonies:petroleum/steel_distillation_output",
        "mechanical_crafting",
        "tfmg:crafting/materials/steel_distillation_output",
        1,
        DISTILLATION_NODE,
        5,
        {
            "tfmg:steel_pipe",
            "tfmg:steel_fluid_tank",
            "tfmg:industrial_pipe",
            "tfmg:heavy_machinery_casing",
        },
    ),
    "tfmg:regular_engine": spec(
        "industrial_colonies:engines/regular_engine",
        "mechanical_crafting",
        "tfmg:crafting/materials/regular_engine",
        2,
        EARLY_ENGINE_NODE,
        5,
        {
            "tfmg:heavy_plate",
            "tfmg:simple_engine_cylinder",
            "create:shaft",
            "tfmg:engine_gearbox",
            "tfmg:heavy_machinery_casing",
            "tfmg:steel_mechanism",
            "create:precision_mechanism",
        },
    ),
    "createdieselgenerators:diesel_engine": spec(
        "industrial_colonies:engines/diesel_engine",
        "mechanical_crafting",
        "createdieselgenerators:crafting/diesel_engine",
        1,
        DIESEL_NODE,
        5,
        {
            "tfmg:heavy_plate",
            "tfmg:diesel_engine_cylinder",
            "createdieselgenerators:engine_piston",
            "tfmg:steel_mechanism",
            "create:precision_mechanism",
            "tfmg:regular_engine",
            "tfmg:steel_fluid_tank",
            "create:brass_casing",
        },
    ),
    "createdieselgenerators:engine_turbocharger": spec(
        "industrial_colonies:engines/engine_turbocharger",
        "mechanical_crafting",
        "createdieselgenerators:crafting/engine_turbocharger",
        1,
        HEAVY_DIESEL_NODE,
        5,
        {
            "tfmg:aluminum_pipe",
            "tfmg:heavy_plate",
            "tfmg:turbine_blade",
            "create:propeller",
            "tfmg:steel_pipe",
            "tfmg:steel_mechanism",
            "create:shaft",
        },
    ),
    "createdieselgenerators:large_diesel_engine": spec(
        "industrial_colonies:engines/large_diesel_engine",
        "mechanical_crafting",
        "createdieselgenerators:crafting/large_diesel_engine",
        1,
        HEAVY_DIESEL_NODE,
        5,
        {
            "tfmg:heavy_plate",
            "createdieselgenerators:diesel_engine",
            "tfmg:steel_mechanism",
            "tfmg:heavy_machinery_casing",
            "tfmg:engine_gearbox",
            "tfmg:steel_fluid_tank",
            "tfmg:large_engine",
        },
    ),
    "tfmg:turbine_engine": spec(
        "industrial_colonies:engines/turbine_engine",
        "mechanical_crafting",
        "tfmg:crafting/materials/turbine_engine",
        2,
        HEAVY_DIESEL_NODE,
        5,
        {
            "tfmg:aluminum_pipe",
            "tfmg:heavy_plate",
            "tfmg:turbine_blade",
            "createdieselgenerators:engine_turbocharger",
            "create:propeller",
            "tfmg:heavy_machinery_casing",
            "tfmg:engine_gearbox",
        },
    ),
    "createdieselgenerators:huge_diesel_engine": spec(
        "industrial_colonies:engines/huge_diesel_engine",
        "mechanical_crafting",
        "createdieselgenerators:crafting/huge_diesel_engine",
        1,
        HEAVY_DIESEL_NODE,
        5,
        {
            "tfmg:heavy_plate",
            "createdieselgenerators:large_diesel_engine",
            "createdieselgenerators:engine_turbocharger",
            "tfmg:heavy_machinery_casing",
            "tfmg:turbine_engine",
            "tfmg:steel_fluid_tank",
            "tfmg:large_engine",
        },
    ),
    "tfmg:radial_engine": spec(
        "industrial_colonies:engines/radial_engine",
        "mechanical_crafting",
        "tfmg:crafting/materials/radial_engine",
        1,
        RADIAL_NODE,
        5,
        {
            "tfmg:engine_cylinder",
            "tfmg:heavy_plate",
            "tfmg:steel_mechanism",
            "create:shaft",
            "tfmg:engine_gearbox",
        },
    ),
}

OIL_OUTPUTS = {output for output, value in EXPECTED.items() if value["node"] == OIL_NODE}
PRE_STEEL_FORBIDDEN_FRAGMENTS = (
    "steel",
    "heavy_machinery_casing",
    "heavy_plate",
    "rebar",
    "aluminum",
    "industrial_pipe",
)
DIGITAL_PREFIXES = (
    "ae2:",
    "advanced_ae:",
    "appliedcreate:",
    "appmek:",
    "computercraft:",
    "extendedae:",
    "megacells:",
    "mekanism:",
)

PRESERVED: Mapping[str, Mapping[str, Any]] = {
    "tfmg:engine_controller": {
        "id": "industrial_colonies:engines/electronic_engine_controller",
        "type": "mechanical_crafting",
        "pattern": ["RWPWR", "VZSZV", "WCTCW", "VMSMV", "RWPWR"],
        "key": {"R": "tfmg:rubber_sheet", "W": "#c:wires/copper", "P": "tfmg:capacitor_item", "V": "tfmg:voltmeter", "Z": "tfmg:circuit_board", "S": "create:shaft", "C": "tfmg:heavy_machinery_casing", "T": "tfmg:transistor_item", "M": "tfmg:steel_mechanism"},
        "remove": ["tfmg:mechanical_crafting/engine_controller"],
    },
    "tfmg:simple_large_engine": {
        "id": "industrial_colonies:engines/simple_large_engine",
        "type": "mechanical_crafting",
        "pattern": ["CCCCC", "COOOC", "COMOC", "COSOC", "HHHHH"],
        "key": {"C": "#c:ingots/cast_iron", "O": "#c:plates/steel", "M": "create:precision_mechanism", "S": "tfmg:steel_mechanism", "H": "tfmg:heavy_plate"},
        "remove": ["tfmg:mechanical_crafting/simple_large_engine"],
    },
    "tfmg:large_engine": {
        "id": "industrial_colonies:engines/large_engine",
        "type": "mechanical_crafting",
        "pattern": ["  O  ", "  B  ", " AOA ", "HSCSH", "HSTSH", "HHHHH"],
        "key": {"A": "#c:plates/aluminum", "B": "#c:ingots/aluminum", "O": "#c:ingots/steel", "S": "tfmg:steel_mechanism", "C": "tfmg:heavy_machinery_casing", "T": "tfmg:steel_fluid_tank", "H": "tfmg:heavy_plate"},
        "remove": ["tfmg:mechanical_crafting/large_engine"],
    },
}


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


def ingredient_set(recipe: Mapping[str, Any]) -> set[str]:
    values = recipe.get("key", {})
    if not isinstance(values, dict):
        return set()
    result: set[str] = set()
    for value in values.values():
        if isinstance(value, str):
            result.add(value)
        elif isinstance(value, dict) and isinstance(value.get("id"), str):
            prefix = "#" if str(value.get("kind", "")).upper().endswith("_TAG") else ""
            result.add(prefix + value["id"].lstrip("#"))
    return result


def recipes_by_output(data: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for raw in data.get("recipes", []):
        if isinstance(raw, dict):
            output, _count = output_stack(raw)
            result.setdefault(output, []).append(raw)
    return result


def validate_contract(
    seed: Mapping[str, Any],
    assignments: Mapping[str, Any],
    manifest: Mapping[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    by_output = recipes_by_output(seed)
    nodes = assignments.get("nodes", {})

    for output, contract in EXPECTED.items():
        recipes = by_output.get(output, [])
        if len(recipes) != 1:
            errors.append(f"{output} has {len(recipes)} explicit seed recipes; expected one")
            continue
        recipe = recipes[0]
        if recipe.get("id") != contract["id"]:
            errors.append(f"{output} uses recipe ID {recipe.get('id')!r}; expected {contract['id']!r}")
        if str(recipe.get("id", "")).startswith("industrial_colonies:auto/"):
            errors.append(f"{output} is still owned by the generic auto generator")
        if recipe.get("type") != contract["type"]:
            errors.append(f"{output} uses {recipe.get('type')!r}; expected {contract['type']!r}")
        if recipe.get("phase") != "Steel & Petroleum":
            errors.append(f"{output} is assigned to the wrong manufacturing phase")
        if recipe.get("remove") != [contract["remove"]]:
            errors.append(f"{output} does not remove exactly {contract['remove']}")
        if recipe.get("exclusive_output") is not True:
            errors.append(f"{output} is not marked exclusive_output")
        _actual_output, actual_count = output_stack(recipe)
        if actual_count != contract["count"]:
            errors.append(f"{output} yields {actual_count}; expected {contract['count']}")

        pattern = recipe.get("pattern")
        grid = contract["grid"]
        if not isinstance(pattern, list) or len(pattern) != grid or any(
            not isinstance(row, str) or len(row) != grid for row in pattern
        ):
            errors.append(f"{output} is not an explicit {grid}x{grid} layout")
        elif grid == 5 and pattern[0] == "ABABA" and pattern[-1] == "ABABA":
            errors.append(f"{output} fell back to the generic ABABA phase ring")

        actual_ingredients = ingredient_set(recipe)
        if actual_ingredients != contract["ingredients"]:
            errors.append(
                f"{output} ingredient contract differs: actual={sorted(actual_ingredients)}"
            )
        used = {
            character
            for row in pattern or []
            if isinstance(row, str)
            for character in row
            if character != " "
        }
        keys = set(recipe.get("key", {})) if isinstance(recipe.get("key"), dict) else set()
        if used != keys:
            errors.append(f"{output} has a pattern/key mismatch: used={sorted(used)} keys={sorted(keys)}")

        unlocks = set(nodes.get(contract["node"], {}).get("unlocks", []))
        if output not in unlocks:
            errors.append(f"{contract['node']} does not own {output}")

    for output in OIL_OUTPUTS:
        recipe = by_output.get(output, [{}])[0]
        forbidden = sorted(
            ingredient
            for ingredient in ingredient_set(recipe)
            if any(fragment in ingredient for fragment in PRE_STEEL_FORBIDDEN_FRAGMENTS)
        )
        if forbidden:
            errors.append(f"{output} crosses the parallel Blast Furnace branch: {forbidden}")

    first_diesel = by_output.get("createdieselgenerators:diesel_engine", [{}])[0]
    diesel_inputs = ingredient_set(first_diesel)
    digital = sorted(
        value
        for value in diesel_inputs
        if value.startswith(DIGITAL_PREFIXES)
        or any(token in value for token in ("circuit", "processor", "computer"))
    )
    if digital:
        errors.append(f"first diesel engine has digital prerequisites: {digital}")
    for required in {"tfmg:diesel_engine_cylinder", "tfmg:regular_engine"}:
        if required not in diesel_inputs:
            errors.append(f"first diesel engine does not consume canonical TFMG component {required}")

    for output, expected in PRESERVED.items():
        recipes = by_output.get(output, [])
        if len(recipes) != 1:
            errors.append(f"preserved gateway {output} has {len(recipes)} seed recipes")
            continue
        actual = recipes[0]
        for field, value in expected.items():
            if actual.get(field) != value:
                errors.append(f"preserved gateway {output} changed field {field}")

    if not PUMPJACK_PIPE_TAG.is_file():
        errors.append("companion data pack does not extend TFMG's functional pumpjack pipe tag")
    else:
        pipe_tag = load_object(PUMPJACK_PIPE_TAG)
        if pipe_tag.get("replace") is True or "tfmg:cast_iron_pipe" not in pipe_tag.get("values", []):
            errors.append("TFMG pumpjack pipe tag does not merge the pre-steel cast-iron pipe")

    all_removals = [
        removal
        for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict)
        for removal in recipe.get("remove", [])
        if isinstance(removal, str)
    ]
    for removal in (value["remove"] for value in EXPECTED.values()):
        if all_removals.count(removal) != 1:
            errors.append(f"stock removal {removal} appears {all_removals.count(removal)} times")
        if removal in seed.get("additional_removals", []):
            errors.append(f"stock removal {removal} is redundantly broad-listed")

    if manifest is not None:
        manifest_by_output = recipes_by_output(manifest)
        for output, contract in EXPECTED.items():
            recipes = manifest_by_output.get(output, [])
            if len(recipes) != 1:
                errors.append(f"compiled manifest has {len(recipes)} recipes for {output}")
                continue
            recipe = recipes[0]
            if recipe.get("id") != contract["id"]:
                errors.append(f"compiled manifest did not retain source-owned ID for {output}")
            if recipe.get("remove") != [contract["remove"]]:
                errors.append(f"compiled manifest changed exact removal for {output}")
            if output_stack(recipe)[1] != contract["count"]:
                errors.append(f"compiled manifest changed output count for {output}")

    return errors


def default_mods() -> Path:
    for line in (PROJECT / "gradle.properties").read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("pack_mods_dir="):
            return Path(line.split("=", 1)[1]).expanduser()
    raise ValueError("gradle.properties has no pack_mods_dir")


def validate_installed_sources(mods: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checked: list[str] = []
    jars: dict[str, Path] = {}
    for namespace, glob in {
        "tfmg": "tfmg-*.jar",
        "createdieselgenerators": "createdieselgenerators-*.jar",
    }.items():
        candidates = sorted(mods.glob(glob))
        if len(candidates) != 1:
            errors.append(f"expected one installed {namespace} jar, found {len(candidates)}")
        else:
            jars[namespace] = candidates[0]

    archives: dict[str, zipfile.ZipFile] = {}
    try:
        for namespace, path in jars.items():
            archives[namespace] = zipfile.ZipFile(path)
        for output, contract in EXPECTED.items():
            recipe_id = str(contract["remove"])
            namespace, recipe_path = recipe_id.split(":", 1)
            archive = archives.get(namespace)
            if archive is None:
                continue
            path = f"data/{namespace}/recipe/{recipe_path}.json"
            if path not in archive.namelist():
                errors.append(f"installed stock recipe is absent: {recipe_id}")
                continue
            value = json.loads(archive.read(path).decode("utf-8-sig"))
            result = value.get("result", {})
            actual_output = result.get("id") or result.get("item")
            actual_count = int(result.get("count", 1))
            if actual_output != output:
                errors.append(f"{recipe_id} now outputs {actual_output!r}, expected {output}")
            if actual_count != contract["count"]:
                errors.append(
                    f"{recipe_id} stock count is {actual_count}, authored count is {contract['count']}"
                )
            checked.append(recipe_id)
    finally:
        for archive in archives.values():
            archive.close()
    return errors, checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--mods", type=Path, default=None)
    parser.add_argument("--manifest", type=Path, help="optional freshly built manifest parity check")
    args = parser.parse_args()

    seed = load_object(args.seed.resolve())
    assignments = load_object(args.assignments.resolve())
    manifest = load_object(args.manifest.resolve()) if args.manifest else None
    errors = validate_contract(seed, assignments, manifest)
    source_errors, checked = validate_installed_sources((args.mods or default_mods()).resolve())
    errors.extend(source_errors)

    print(
        f"Checked {len(EXPECTED)} source-owned petroleum recipes, "
        f"{len(PRESERVED)} preserved engine gateways, and {len(checked)} installed stock recipes."
    )
    if errors:
        print(f"FAIL: {len(errors)} petroleum progression issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("PASS: TFMG-first petroleum extraction, refining, and engine construction are coherent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
