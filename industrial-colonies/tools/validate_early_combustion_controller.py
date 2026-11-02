#!/usr/bin/env python3
"""Validate the strict-ancestor TFMG early-combustion controller rewrite."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
NODE = "CR01 — Early Combusion Engines"
OIL = "CR01 — Oil processing"
ELECTRONICS = "CR01 — Electronics Manufacturing"
BLAST_FURNACE = "CR01 — Blast Furnace"
SCRIPT = "industrial_oil_field_construction.js"
OUTPUT = "tfmg:engine_controller"
SOURCE = "tfmg:mechanical_crafting/engine_controller"
REPLACEMENT = "industrial_colonies:machine/early_combustion/engine_controller"

EXPECTED_EXACT_INPUTS = {
    "create:brass_casing",
    "tfmg:cast_iron_frame",
    "tfmg:generator",
    "tfmg:pumpjack_crank",
    "create:precision_mechanism",
    "create:shaft",
}
EXPECTED_TAG_INPUTS = {"#c:dusts/redstone", "#c:wires/copper"}
FORBIDDEN_INPUTS = {
    "tfmg:heavy_machinery_casing",
    "tfmg:steel_mechanism",
    "tfmg:rubber_sheet",
    "tfmg:voltmeter",
    "tfmg:circuit_board",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def recipe_path(recipe_id: str) -> str:
    namespace, path = recipe_id.split(":", 1)
    return f"data/{namespace}/recipe/{path}.json"


def ancestors(node: str, incoming: dict[str, set[str]]) -> set[str]:
    found: set[str] = set()
    frontier = list(incoming[node])
    while frontier:
        parent = frontier.pop()
        if parent in found:
            continue
        found.add(parent)
        frontier.extend(incoming[parent])
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path, help="Minecraft instance directory")
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--drawio-export", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    graph = load_json(args.drawio_export.resolve())
    assignments = load_json(project / "progression/machine_node_assignments.json")["nodes"]
    dependencies = load_json(project / "tools/machine_recipe_dependencies.json")["recipes"]
    policies = load_json(project / "tools/canonicalization_policies.json")
    additional = load_json(project / "tools/additional_recipe_stages.json")["recipes"]
    script = (project / "pack-scripts/server_scripts" / SCRIPT).read_text(encoding="utf-8")
    failures: list[str] = []

    id_to_label = {node["id"]: node["label"] for node in graph["nodes"]}
    incoming: dict[str, set[str]] = defaultdict(set)
    edges: set[tuple[str, str]] = set()
    for edge in graph["edges"]:
        source = id_to_label.get(edge["source"])
        target = id_to_label.get(edge["target"])
        if source and target:
            incoming[target].add(source)
            edges.add((source, target))
    lineage = ancestors(NODE, incoming)
    if (OIL, NODE) not in edges:
        failures.append("immutable Oil Processing -> Early Combusion Engines edge is absent")
    if ELECTRONICS in lineage:
        failures.append("immutable graph unexpectedly makes Electronics Manufacturing an ancestor")
    if BLAST_FURNACE in lineage:
        failures.append("immutable graph unexpectedly makes Blast Furnace an ancestor")
    if len(id_to_label) != 77 or len(edges) != 99:
        failures.append(f"immutable topology changed: {len(id_to_label)} nodes/{len(edges)} edges")

    if SOURCE not in script:
        failures.append(f"stock engine-controller recipe is not removed: {SOURCE}")
    if REPLACEMENT not in script or OUTPUT not in script:
        failures.append("replacement engine-controller recipe is absent")
    if "type: 'create:mechanical_crafting'" not in script:
        failures.append("replacement is not Create mechanical crafting")

    rows = [row for row in dependencies if row.get("output") == OUTPUT]
    if len(rows) != 1:
        failures.append(f"expected one dependency row for {OUTPUT}, found {len(rows)}")
        row: dict[str, Any] = {}
    else:
        row = rows[0]
        if row.get("node") != NODE or row.get("script") != SCRIPT:
            failures.append("engine-controller dependency has wrong node/script")
        if row.get("recipe_id") != REPLACEMENT:
            failures.append("engine-controller dependency has wrong replacement ID")
        exact_inputs = set(row.get("ingredients", []))
        tag_inputs = set(row.get("foundational_tags", []))
        if exact_inputs != EXPECTED_EXACT_INPUTS:
            failures.append(
                f"engine-controller exact inputs differ: {sorted(exact_inputs)}"
            )
        if tag_inputs != EXPECTED_TAG_INPUTS:
            failures.append(f"engine-controller tag inputs differ: {sorted(tag_inputs)}")
        forbidden = sorted((exact_inputs | tag_inputs) & FORBIDDEN_INPUTS)
        if forbidden:
            failures.append("engine-controller retains sibling inputs: " + " | ".join(forbidden))

    item_owners: dict[str, set[str]] = defaultdict(set)
    for node, definition in assignments.items():
        for item in definition.get("unlocks", []):
            item_owners[item].add(node)
    allowed_nodes = lineage | {NODE}
    for ingredient in EXPECTED_EXACT_INPUTS:
        owners = item_owners.get(ingredient, set())
        if not owners:
            failures.append(f"exact engine-controller input has no owner: {ingredient}")
        elif not (owners & allowed_nodes):
            failures.append(
                f"engine-controller input is sibling/downstream: {ingredient} -> {sorted(owners)}"
            )
        if ingredient not in script:
            failures.append(f"declared engine-controller input is absent from script: {ingredient}")
    if OUTPUT not in assignments[NODE].get("unlocks", []):
        failures.append(f"{NODE} assignment does not own {OUTPUT}")

    policy_by_output = {
        policy["machine"]: policy for policy in policies.get("machine_overhauls", [])
    }
    policy = policy_by_output.get(OUTPUT)
    if policy is None:
        failures.append("engine-controller overhaul policy is absent")
    elif (
        policy.get("node") != NODE
        or policy.get("script") != SCRIPT
        or policy.get("replacement_recipe") != REPLACEMENT
        or policy.get("replacement_type") != "create:mechanical_crafting"
    ):
        failures.append("engine-controller overhaul policy is inconsistent")

    extra_stages = [
        entry for entry in additional if entry.get("recipe_id") in {SOURCE, REPLACEMENT}
    ]
    if extra_stages:
        failures.append(
            "engine-controller stage must come only from machine dependencies: "
            + json.dumps(extra_stages, ensure_ascii=False)
        )

    tfmg_jars = sorted((args.instance.resolve() / "mods").glob("tfmg-*.jar"))
    if len(tfmg_jars) != 1:
        failures.append(f"expected one installed TFMG jar, found {len(tfmg_jars)}")
        tfmg_jar = None
    else:
        tfmg_jar = tfmg_jars[0]
        with zipfile.ZipFile(tfmg_jar) as archive:
            path = recipe_path(SOURCE)
            if path not in archive.namelist():
                failures.append(f"installed source recipe is absent: {SOURCE}")
            else:
                source = json.loads(archive.read(path).decode("utf-8-sig"))
                result = source.get("result", {})
                if (result.get("id") or result.get("item")) != OUTPUT:
                    failures.append("installed engine-controller source output changed")
                source_text = json.dumps(source)
                for forbidden in FORBIDDEN_INPUTS:
                    if forbidden not in source_text:
                        failures.append(
                            f"installed source no longer demonstrates expected conflict: {forbidden}"
                        )

    report = {
        "drawio_source_sha256": graph.get("source_sha256"),
        "nodes": len(id_to_label),
        "edges": len(edges),
        "node": NODE,
        "lineage": sorted(lineage),
        "source_recipe": SOURCE,
        "replacement_recipe": REPLACEMENT,
        "exact_inputs": sorted(EXPECTED_EXACT_INPUTS),
        "foundational_tags": sorted(EXPECTED_TAG_INPUTS),
        "failures": failures,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"Checked {OUTPUT} against {len(lineage)} strict ancestors and immutable "
        f"{len(id_to_label)}-node/{len(edges)}-edge topology."
    )
    if failures:
        print(f"FAIL: {len(failures)} controller issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: Early Combustion Engines has a reachable mechanical controller path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
