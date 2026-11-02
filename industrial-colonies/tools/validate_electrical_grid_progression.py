#!/usr/bin/env python3
"""Validate the first Electro Energetics grid-construction progression slice."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
GRID = "CR01 — Grid Engineering"
HIGH_VOLTAGE = "CR01 — High-Voltage Systems"
EXTREME = "CR01 — Extreme Power Transmission"
HIGH_ENERGY = "CR01 — High-Energy Distribution"
SCRIPT = "industrial_grid_engineering_construction.js"

REPLACEMENTS = {
    "electroenergetics:empty_spool": "industrial_colonies:grid/empty_spool",
    "electroenergetics:connector": "industrial_colonies:grid/connector",
    "electroenergetics:copper_wire_spool": (
        "industrial_colonies:grid/copper_wire_spool"
    ),
    "electroenergetics:accumulator": "industrial_colonies:grid/accumulator",
    "electroenergetics:alternator_rotor": (
        "industrial_colonies:grid/alternator_rotor"
    ),
    "electroenergetics:alternator_brushes": (
        "industrial_colonies:grid/alternator_brushes"
    ),
    "electroenergetics:resistor": "industrial_colonies:grid/resistor",
}

SOURCE_RECIPES = {
    output: f"electroenergetics:crafting/{output.split(':', 1)[1]}"
    for output in REPLACEMENTS
}

REPLACEMENT_TYPES = {
    "electroenergetics:accumulator": "create:mechanical_crafting",
    "electroenergetics:alternator_rotor": "create:mechanical_crafting",
    "electroenergetics:alternator_brushes": "create:sequenced_assembly",
}

CONNECTOR_CONVERSIONS = {
    "electroenergetics:crafting/connector_from_double",
    "electroenergetics:crafting/connector_from_triple",
    "electroenergetics:crafting/connector_from_quad",
}


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


def toml_integer(text: str, key: str) -> int:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*(\d+)\s*$", text)
    if not match:
        raise AssertionError(f"missing config key: {key}")
    return int(match.group(1))


def require_fragments(data: str, label: str, fragments: tuple[str, ...], failures: list[str]):
    for fragment in fragments:
        if fragment not in data:
            failures.append(f"{label} no longer contains audit evidence: {fragment}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--drawio-export", type=Path, required=True)
    args = parser.parse_args()

    project = args.project.resolve()
    instance = args.instance.resolve()
    failures: list[str] = []

    graph = load_json(args.drawio_export.resolve())
    edges = graph_edges(graph)
    required_edges = {
        ("CR01 — Early Power Cables", GRID),
        ("CR01 — Chemical Processing", GRID),
        (GRID, HIGH_VOLTAGE),
        (HIGH_VOLTAGE, EXTREME),
        (EXTREME, HIGH_ENERGY),
    }
    for edge in sorted(required_edges - edges):
        failures.append(f"authoritative Draw.io edge is absent: {edge}")

    script = (
        project / "pack-scripts" / "server_scripts" / SCRIPT
    ).read_text(encoding="utf-8")
    dependencies = load_json(project / "tools" / "machine_recipe_dependencies.json")
    rows = {
        row["output"]: row
        for row in dependencies["recipes"]
        if row.get("script") == SCRIPT
    }
    policies = load_json(project / "tools" / "canonicalization_policies.json")
    policy_by_output = {
        policy["machine"]: policy for policy in policies.get("machine_overhauls", [])
    }
    assignments = load_json(project / "progression" / "machine_node_assignments.json")
    grid_unlocks = set(assignments["nodes"][GRID]["unlocks"])

    for output, replacement in REPLACEMENTS.items():
        source = SOURCE_RECIPES[output]
        if source not in script:
            failures.append(f"source recipe is not removed: {source}")
        if replacement not in script:
            failures.append(f"replacement recipe is absent: {replacement}")
        row = rows.get(output)
        if row is None:
            failures.append(f"dependency row is absent: {output}")
        elif row.get("node") != GRID or row.get("recipe_id") != replacement:
            failures.append(f"dependency row has wrong node/id: {output}")
        if output not in grid_unlocks:
            failures.append(f"Grid Engineering assignment is missing: {output}")
        policy = policy_by_output.get(output)
        expected_type = REPLACEMENT_TYPES.get(output, "minecraft:crafting_shaped")
        if policy is None:
            failures.append(f"construction policy is absent: {output}")
        elif (
            policy.get("node") != GRID
            or policy.get("script") != SCRIPT
            or policy.get("replacement_recipe") != replacement
            or policy.get("replacement_type") != expected_type
        ):
            failures.append(f"construction policy is inconsistent: {output}")

    connector_policy = policy_by_output.get("electroenergetics:connector", {})
    if set(connector_policy.get("allowed_surviving_source_recipes", [])) != CONNECTOR_CONVERSIONS:
        failures.append("connector reclamation recipes are not the exact allowed survivor set")

    createaddition_config = (
        instance / "config" / "createaddition-common.toml"
    ).read_text(encoding="utf-8")
    electro_config = (
        instance / "config" / "electroenergetics-server.toml"
    ).read_text(encoding="utf-8")
    local_lengths = (
        toml_integer(createaddition_config, "small_connector_wire_length"),
        toml_integer(createaddition_config, "large_connector_wire_length"),
    )
    grid_length = toml_integer(electro_config, "wireLength")
    if local_lengths != (16, 32):
        failures.append(f"Create Crafts & Additions local lengths changed: {local_lengths}")
    if grid_length != 128:
        failures.append(f"Electro Energetics utility-grid length changed: {grid_length}")

    mods = instance / "mods"
    electro_jar = one_jar(mods, "electroenergetics-*.jar")
    tfmg_jar = one_jar(mods, "tfmg-*.jar")
    mekanism_jar = one_jar(mods, "Mekanism-*.jar")

    with zipfile.ZipFile(electro_jar) as archive:
        names = set(archive.namelist())
        for output, source in SOURCE_RECIPES.items():
            path = recipe_path(source)
            if path not in names:
                failures.append(f"Electro Energetics source recipe is absent: {source}")
                continue
            recipe = json.loads(archive.read(path).decode("utf-8-sig"))
            result = recipe.get("result", {})
            if (result.get("id") or result.get("item")) != output:
                failures.append(f"Electro Energetics source output changed: {source}")

    with zipfile.ZipFile(tfmg_jar) as archive:
        generator = archive.read(
            "data/tfmg/recipe/sequenced_assembly/generator.json"
        ).decode("utf-8-sig")
        motor = archive.read(
            "data/tfmg/recipe/sequenced_assembly/motor.json"
        ).decode("utf-8-sig")
        accumulator = archive.read(
            "data/tfmg/recipe/crafting/materials/accumulator.json"
        ).decode("utf-8-sig")
        cable_tube = archive.read(
            "data/tfmg/recipe/crafting/materials/cable_tube.json"
        ).decode("utf-8-sig")
        rubber = archive.read(
            "data/tfmg/recipe/vat_machine_recipe/rubber.json"
        ).decode("utf-8-sig")
    require_fragments(
        generator,
        "TFMG generator",
        ("tfmg:capacitor_item", "c:plates/steel", "tfmg:winding", "tfmg:steel_mechanism"),
        failures,
    )
    require_fragments(
        motor,
        "TFMG electric motor",
        ("tfmg:winding", "tfmg:steel_mechanism"),
        failures,
    )
    require_fragments(
        accumulator,
        "TFMG accumulator",
        ("tfmg:sulfuric_acid_bucket", "tfmg:industrial_aluminum_casing"),
        failures,
    )
    require_fragments(cable_tube, "TFMG cable tube", ("tfmg:rubber_sheet",), failures)
    require_fragments(
        rubber,
        "TFMG rubber",
        ("tfmg:sulfur_dust", "tfmg:heavy_oil", "tfmg:steel_vat"),
        failures,
    )

    with zipfile.ZipFile(mekanism_jar) as archive:
        basic_cable = archive.read(
            "data/mekanism/recipe/transmitter/universal_cable/basic.json"
        ).decode("utf-8-sig")
    require_fragments(
        basic_cable,
        "Mekanism basic universal cable",
        ("c:dusts/redstone", "c:ingots/steel", "mekanism:basic_universal_cable"),
        failures,
    )

    print(
        f"Checked {len(REPLACEMENTS)} Grid Engineering replacements, "
        f"four installed electrical stacks, and {len(graph['edges'])} Draw.io edges."
    )
    print(
        f"Observed local wire spans {local_lengths[0]}/{local_lengths[1]} blocks "
        f"and Electro Energetics grid span {grid_length} blocks."
    )
    if failures:
        print(f"FAIL: {len(failures)} electrical progression issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: the first utility-grid slice matches the authoritative progression.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
