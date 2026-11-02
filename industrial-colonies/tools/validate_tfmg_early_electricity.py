#!/usr/bin/env python3
"""Validate the TFMG-default early-electricity construction and retirements."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
EARLY = "CR01 — Early Electricity Technology"
CHEMICAL = "CR01 — Chemical Processing"
STEEL_AGE = "CR01 — The Steel Age"
ELECTRONICS = "CR01 — Electronics Manufacturing"
EARLY_CABLES = "CR01 — Early Power Cables"
ADVANCED_REDSTONE = "CR01 — Advanced Redstone"
SCRIPT = "industrial_early_electricity_construction.js"
GRID_SCRIPT = "industrial_grid_engineering_construction.js"

REPLACEMENTS = {
    "tfmg:generator": (
        EARLY,
        "industrial_colonies:early_electricity/generator",
        "create:mechanical_crafting",
    ),
    "tfmg:electric_motor": (
        EARLY,
        "industrial_colonies:early_electricity/electric_motor",
        "create:mechanical_crafting",
    ),
    "tfmg:accumulator": (
        CHEMICAL,
        "industrial_colonies:chemical_processing/accumulator",
        "minecraft:crafting_shaped",
    ),
    "tfmg:cable_connector": (
        EARLY_CABLES,
        "industrial_colonies:early_power_cables/cable_connector",
        "minecraft:crafting_shaped",
    ),
    "tfmg:cable_tube": (
        CHEMICAL,
        "industrial_colonies:chemical_processing/cable_tube",
        "minecraft:crafting_shaped",
    ),
    "tfmg:copper_cable_hub": (
        EARLY_CABLES,
        "industrial_colonies:early_power_cables/copper_cable_hub",
        "minecraft:crafting_shaped",
    ),
    "createaddition:redstone_relay": (
        EARLY_CABLES,
        "industrial_colonies:early_power_cables/redstone_relay",
        "minecraft:crafting_shaped",
    ),
    "createaddition:small_light_connector": (
        EARLY_CABLES,
        "industrial_colonies:early_power_cables/small_light_connector",
        "minecraft:crafting_shapeless",
    ),
}

TFMG_SOURCES = {
    "tfmg:generator": ("tfmg:sequenced_assembly/generator",),
    "tfmg:electric_motor": ("tfmg:sequenced_assembly/motor",),
    "tfmg:accumulator": (
        "tfmg:crafting/materials/accumulator",
        "tfmg:crafting/materials/accumulatorfrom_lithium",
    ),
    "tfmg:cable_connector": ("tfmg:crafting/materials/cable_connector",),
    "tfmg:cable_tube": ("tfmg:crafting/materials/cable_tube",),
    "tfmg:copper_cable_hub": ("tfmg:crafting/materials/copper_cable_hub",),
}

CREATEADDITION_PORTED_SOURCES = {
    "createaddition:redstone_relay": ("createaddition:crafting/redstone_relay",),
    "createaddition:small_light_connector": (
        "createaddition:crafting/small_light_connector",
    ),
}

SOURCE_RECIPES = {**TFMG_SOURCES, **CREATEADDITION_PORTED_SOURCES}

RETIREMENTS = {
    "createaddition:alternator": (
        "createaddition:mechanical_crafting/alternator",
        "create:mechanical_crafting",
        "tfmg:generator",
        0,
    ),
    "createaddition:electric_motor": (
        "createaddition:mechanical_crafting/electric_motor",
        "create:mechanical_crafting",
        "tfmg:electric_motor",
        0,
    ),
    "createaddition:modular_accumulator": (
        "createaddition:crafting/modular_accumulator",
        "minecraft:crafting_shaped",
        "tfmg:accumulator",
        0,
    ),
    "createaddition:connector": (
        "createaddition:crafting/connector",
        "minecraft:crafting_shapeless",
        "tfmg:cable_connector",
        2,
    ),
    "createaddition:large_connector": (
        "createaddition:crafting/large_connector",
        "minecraft:crafting_shapeless",
        "tfmg:copper_cable_hub",
        0,
    ),
}

# The small light and redstone relay are distinct CreateAddition utilities, not
# duplicate power endpoints. Their source recipes are deliberately ported from
# the retired small connector to the TFMG cable connector.
ALLOWED_RETIRED_CONSUMERS = {
    "createaddition:connector": {
        "data/createaddition/recipe/crafting/redstone_relay.json",
        "data/createaddition/recipe/crafting/small_light_connector.json",
    }
}

FORBIDDEN_EARLY_FRAGMENTS = (
    "steel",
    "cast_iron",
    "winding",
    "capacitor",
    "rubber",
    "aluminum",
    "sulfuric_acid",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def recipe_path(recipe_id: str) -> str:
    namespace, path = recipe_id.split(":", 1)
    return f"data/{namespace}/recipe/{path}.json"


def one_jar(mods: Path, pattern: str) -> Path:
    matches = sorted(mods.glob(pattern))
    if len(matches) != 1:
        raise AssertionError(f"expected one {pattern}, found {len(matches)}")
    return matches[0]


def graph_edges(graph: dict) -> set[tuple[str, str]]:
    labels = {node["id"]: node["label"] for node in graph["nodes"]}
    return {
        (labels[edge["source"]], labels[edge["target"]])
        for edge in graph["edges"]
        if edge["source"] in labels and edge["target"] in labels
    }


def recipe_outputs(recipe: dict) -> set[str]:
    outputs: set[str] = set()
    result = recipe.get("result")
    if isinstance(result, dict):
        value = result.get("id") or result.get("item")
        if isinstance(value, str):
            outputs.add(value)
    for result in recipe.get("results", []):
        if isinstance(result, dict):
            value = result.get("id") or result.get("item")
            if isinstance(value, str):
                outputs.add(value)
    return outputs


def resource_ids(row: dict) -> set[str]:
    return set(row.get("ingredients", [])) | {
        value.removeprefix("#") for value in row.get("foundational_tags", [])
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path, help="Minecraft instance directory")
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--drawio-export", type=Path, required=True)
    args = parser.parse_args()

    project = args.project.resolve()
    instance = args.instance.resolve()
    failures: list[str] = []

    graph = load_json(args.drawio_export.resolve())
    edges = graph_edges(graph)
    required_edges = {
        (ADVANCED_REDSTONE, EARLY),
        (EARLY, STEEL_AGE),
        (EARLY, ELECTRONICS),
        (EARLY, EARLY_CABLES),
    }
    for edge in sorted(required_edges - edges):
        failures.append(f"authoritative Draw.io edge is absent: {edge}")

    script = (
        project / "pack-scripts" / "server_scripts" / SCRIPT
    ).read_text(encoding="utf-8")
    grid_script = (
        project / "pack-scripts" / "server_scripts" / GRID_SCRIPT
    ).read_text(encoding="utf-8")
    dependencies = load_json(project / "tools" / "machine_recipe_dependencies.json")
    rows = {
        row["output"]: row
        for row in dependencies["recipes"]
        if row.get("script") == SCRIPT
    }
    grid_rows = {
        row["output"]: row
        for row in dependencies["recipes"]
        if row.get("script") == GRID_SCRIPT
    }
    assignments = load_json(project / "progression" / "machine_node_assignments.json")
    policies = load_json(project / "tools" / "canonicalization_policies.json")
    overhaul_by_output = {
        policy["machine"]: policy for policy in policies.get("machine_overhauls", [])
    }
    retirement_by_output = {
        policy["machine"]: policy for policy in policies.get("machine_retirements", [])
    }

    for output, (node, recipe_id, recipe_type) in REPLACEMENTS.items():
        if recipe_id not in script:
            failures.append(f"replacement recipe is absent: {recipe_id}")
        row = rows.get(output)
        if row is None:
            failures.append(f"dependency row is absent: {output}")
        elif row.get("node") != node or row.get("recipe_id") != recipe_id:
            failures.append(f"dependency row has wrong node/id: {output}")
        if output not in assignments["nodes"][node]["unlocks"]:
            failures.append(f"{node} assignment is missing: {output}")
        policy = overhaul_by_output.get(output)
        if policy is None:
            failures.append(f"construction policy is absent: {output}")
        elif (
            policy.get("node") != node
            or policy.get("script") != SCRIPT
            or policy.get("replacement_recipe") != recipe_id
            or policy.get("replacement_type") != recipe_type
        ):
            failures.append(f"construction policy is inconsistent: {output}")
        for source in SOURCE_RECIPES[output]:
            if source not in script:
                failures.append(f"source recipe is not removed: {source}")

    # resource_ids intentionally merges exact ingredients and canonical tags;
    # tag substitutions must not smuggle a post-node material into this tier.
    for output in (
        "tfmg:generator",
        "tfmg:electric_motor",
        "tfmg:cable_connector",
        "tfmg:copper_cable_hub",
    ):
        row = rows.get(output, {})
        forbidden = sorted(
            value
            for value in resource_ids(row)
            if any(fragment in value for fragment in FORBIDDEN_EARLY_FRAGMENTS)
        )
        if forbidden:
            failures.append(
                f"{output} has descendant/forbidden inputs: {' | '.join(forbidden)}"
            )

    accumulator_ids = resource_ids(rows.get("tfmg:accumulator", {}))
    for required in ("tfmg:steel_casing", "tfmg:sulfuric_acid_bucket"):
        if required not in accumulator_ids:
            failures.append(f"chemical accumulator is missing required input: {required}")
    for forbidden in ("tfmg:industrial_aluminum_casing", "c:ingots/lithium"):
        if forbidden in accumulator_ids:
            failures.append(f"chemical accumulator retains late input: {forbidden}")

    cable_tube_ids = resource_ids(rows.get("tfmg:cable_tube", {}))
    for required in ("tfmg:rubber_sheet", "c:nuggets/steel", "c:wires/copper"):
        if required not in cable_tube_ids:
            failures.append(f"chemical cable tube is missing required input: {required}")

    for output, (
        source,
        processing_type,
        replacement_type,
        ported_recipe_count,
    ) in RETIREMENTS.items():
        if source not in script:
            failures.append(f"duplicate machine source is not removed: {source}")
        policy = retirement_by_output.get(output)
        if policy is None:
            failures.append(f"machine-retirement policy is absent: {output}")
        elif (
            policy.get("script") != SCRIPT
            or policy.get("source_recipe") != source
            or policy.get("processing_type") != processing_type
            or policy.get("replacement_type") != replacement_type
            or policy.get("ported_recipe_count") != ported_recipe_count
            or policy.get("factories") != []
        ):
            failures.append(f"machine-retirement policy is inconsistent: {output}")

    viewer_cleanup = (
        project
        / "pack-scripts"
        / "client_scripts"
        / "industrial_machine_retirement_viewer_cleanup.js"
    ).read_text(encoding="utf-8")
    for output in RETIREMENTS:
        if output not in viewer_cleanup:
            failures.append(f"retired item remains visible in recipe viewer: {output}")
    for retained in (
        "createaddition:redstone_relay",
        "createaddition:small_light_connector",
    ):
        if retained in viewer_cleanup:
            failures.append(f"specialized utility is incorrectly hidden: {retained}")

    retired_ids = set(RETIREMENTS)
    if retired_ids & set(grid_script.split()):
        failures.append("grid script still contains a retired CreateAddition machine")
    for retired in retired_ids:
        if retired in grid_script:
            failures.append(f"grid script still consumes retired machine: {retired}")
    expected_grid_inputs = {
        "electroenergetics:connector": {
            "tfmg:cable_connector",
            "tfmg:copper_cable_hub",
        },
        "electroenergetics:accumulator": {"tfmg:accumulator"},
        "electroenergetics:alternator_rotor": {"tfmg:generator"},
        "electroenergetics:alternator_brushes": {"tfmg:copper_cable_hub"},
    }
    for output, expected_inputs in expected_grid_inputs.items():
        for expected in expected_inputs:
            if expected not in grid_script:
                failures.append(f"grid script does not consume canonical input: {expected}")
            if expected not in resource_ids(grid_rows.get(output, {})):
                failures.append(
                    f"grid dependency row does not contain: {output} -> {expected}"
                )

    mods = instance / "mods"
    tfmg_jar = one_jar(mods, "tfmg-*.jar")
    createaddition_jar = one_jar(mods, "createaddition-*.jar")
    source_locations = {
        (createaddition_jar.resolve(), recipe_path(values[0]))
        for values in RETIREMENTS.values()
    }
    for recipe_ids, jar in (
        (tuple(source for values in TFMG_SOURCES.values() for source in values), tfmg_jar),
        (
            tuple(
                source
                for values in CREATEADDITION_PORTED_SOURCES.values()
                for source in values
            )
            + tuple(values[0] for values in RETIREMENTS.values()),
            createaddition_jar,
        ),
    ):
        with zipfile.ZipFile(jar) as archive:
            names = set(archive.namelist())
            for source in recipe_ids:
                path = recipe_path(source)
                if path not in names:
                    failures.append(f"installed source recipe is absent: {source}")
                    continue
                recipe = json.loads(archive.read(path).decode("utf-8-sig"))
                expected_outputs = {
                    output
                    for output, sources in SOURCE_RECIPES.items()
                    if source in sources
                } | {
                    output
                    for output, values in RETIREMENTS.items()
                    if source == values[0]
                }
                if not (recipe_outputs(recipe) & expected_outputs):
                    failures.append(f"installed source output changed: {source}")

    # A retirement is only safe while every installed consumer is either absent
    # or one of the two explicitly ported specialized utilities.
    consumers: dict[str, list[str]] = {output: [] for output in RETIREMENTS}
    scanned_recipe_files = 0
    for jar in sorted(mods.glob("*.jar")):
        try:
            with zipfile.ZipFile(jar) as archive:
                for name in archive.namelist():
                    if not name.endswith(".json") or "/recipe/" not in name:
                        continue
                    scanned_recipe_files += 1
                    if (jar.resolve(), name) in source_locations:
                        continue
                    try:
                        text = archive.read(name).decode("utf-8-sig")
                    except (UnicodeDecodeError, KeyError):
                        continue
                    for output in RETIREMENTS:
                        if output in text:
                            consumers[output].append(f"{jar.name}!/{name}")
        except zipfile.BadZipFile:
            continue
    for output, found in consumers.items():
        expected = {
            f"{createaddition_jar.name}!/{path}"
            for path in ALLOWED_RETIRED_CONSUMERS.get(output, set())
        }
        actual = set(found)
        if actual != expected:
            failures.append(
                f"retired-machine consumer set changed for {output}: "
                f"expected {sorted(expected)}, found {sorted(actual)[:5]}"
            )

    print(
        f"Checked {len(REPLACEMENTS)} staged replacements, {len(RETIREMENTS)} "
        f"CreateAddition retirements, {scanned_recipe_files} installed recipe JSONs, "
        f"and {len(graph['edges'])} Draw.io edges."
    )
    if failures:
        print(f"FAIL: {len(failures)} early-electricity issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print(
        "PASS: TFMG owns pre-steel generation, motors, storage inputs, and local "
        "cabling; specialized compatibility utilities are fully ported."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
