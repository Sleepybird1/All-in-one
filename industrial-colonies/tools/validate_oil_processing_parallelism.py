#!/usr/bin/env python3
"""Focused static checks for the pre-steel TFMG oil-field construction slice."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
NODE = "CR01 — Oil processing"
STEEL_AGE = "CR01 — The Steel Age"
BLAST_FURNACE = "CR01 — Blast Furnace"
SCRIPT = "industrial_oil_field_construction.js"

SOURCE_RECIPES = {
    "tfmg:surface_scanner": "tfmg:crafting/materials/surface_scanner",
    "tfmg:pumpjack_base": "tfmg:crafting/materials/pumpjack_base",
    "tfmg:pumpjack_crank": "tfmg:crafting/materials/pumpjack_crank",
    "tfmg:pumpjack_hammer": "tfmg:crafting/materials/pumpjack_hammer",
    "tfmg:pumpjack_hammer_part": (
        "tfmg:pumpjack_hammer_part_from_storage_blocks_steel_stonecutting"
    ),
    "tfmg:large_pumpjack_hammer_part": (
        "tfmg:large_pumpjack_hammer_part_from_storage_blocks_steel_stonecutting"
    ),
    "tfmg:pumpjack_hammer_connector": (
        "tfmg:crafting/materials/pumpjack_hammer_connector"
    ),
    "tfmg:large_pumpjack_hammer_connector": (
        "tfmg:crafting/materials/large_pumpjack_hammer_connector"
    ),
    "tfmg:pumpjack_hammer_head": "tfmg:crafting/materials/pumpjack_hammer_head",
    "tfmg:large_pumpjack_hammer_head": (
        "tfmg:crafting/materials/large_pumpjack_hammer_head"
    ),
    "tfmg:oil_hammer": "tfmg:crafting/materials/oil_hammer",
    "tfmg:oil_can": "tfmg:crafting/materials/oil_can",
}

REPLACEMENTS = {
    output: f"industrial_colonies:machine/oil_processing/{output.split(':', 1)[1]}"
    for output in SOURCE_RECIPES
}

PRE_STEEL_COMPONENTS = {
    "tfmg:cast_iron_ingot",
    "tfmg:cast_iron_nugget",
    "tfmg:cast_iron_sheet",
    "tfmg:cast_iron_block",
    "tfmg:cast_iron_frame",
    "tfmg:cast_iron_truss",
    "tfmg:cast_iron_pipe",
    "tfmg:cast_iron_fluid_tank",
    "tfmg:cast_iron_mechanical_pump",
}

FORBIDDEN_RECIPE_INPUT_FRAGMENTS = (
    "steel",
    "heavy_machinery_casing",
    "heavy_plate",
    "rebar",
    "aluminum",
    "industrial_pipe",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def recipe_path(recipe_id: str) -> str:
    namespace, path = recipe_id.split(":", 1)
    return f"data/{namespace}/recipe/{path}.json"


def find_tfmg_jar(instance: Path) -> Path:
    candidates = sorted((instance / "mods").glob("tfmg-*.jar"))
    if len(candidates) != 1:
        raise AssertionError(
            f"expected exactly one TFMG jar in {instance / 'mods'}, found {len(candidates)}"
        )
    return candidates[0]


def graph_edges(graph: dict) -> set[tuple[str, str]]:
    labels = {node["id"]: node["label"] for node in graph["nodes"]}
    return {
        (labels[edge["source"]], labels[edge["target"]])
        for edge in graph["edges"]
        if edge["source"] in labels and edge["target"] in labels
    }


def has_path(edges: set[tuple[str, str]], start: str, target: str) -> bool:
    outgoing: dict[str, set[str]] = {}
    for source, destination in edges:
        outgoing.setdefault(source, set()).add(destination)
    seen: set[str] = set()
    frontier = [start]
    while frontier:
        current = frontier.pop()
        if current == target:
            return True
        if current in seen:
            continue
        seen.add(current)
        frontier.extend(outgoing.get(current, set()))
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path, help="Minecraft instance directory")
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--drawio-export", type=Path, required=True)
    args = parser.parse_args()

    project = args.project.resolve()
    failures: list[str] = []

    graph = load_json(args.drawio_export.resolve())
    edges = graph_edges(graph)
    for required in ((STEEL_AGE, NODE), (STEEL_AGE, BLAST_FURNACE)):
        if required not in edges:
            failures.append(f"Draw.io is missing required parallel edge: {required}")
    if has_path(edges, BLAST_FURNACE, NODE):
        failures.append("Draw.io makes Oil Processing depend on Blast Furnace")

    script_path = project / "pack-scripts" / "server_scripts" / SCRIPT
    script = script_path.read_text(encoding="utf-8")
    if "event.add('tfmg:industrial_pipe', 'tfmg:cast_iron_pipe')" not in script:
        failures.append("cast-iron pipe is not added to TFMG's pumpjack pipe tag")
    recipe_body = script.split("const shaped =", 1)[-1]
    body_ids = re.findall(r"['\"]([a-z0-9_.-]+:[a-z0-9_./-]+)['\"]", recipe_body)
    forbidden_body_ids = sorted(
        resource_id
        for resource_id in set(body_ids)
        if any(fragment in resource_id for fragment in FORBIDDEN_RECIPE_INPUT_FRAGMENTS)
    )
    if forbidden_body_ids:
        failures.append(
            "pre-steel replacement body contains forbidden resources: "
            + " | ".join(forbidden_body_ids)
        )

    dependencies = load_json(project / "tools" / "machine_recipe_dependencies.json")
    rows = {
        row["output"]: row
        for row in dependencies["recipes"]
        if row.get("script") == SCRIPT
    }
    assignments = load_json(project / "progression" / "machine_node_assignments.json")
    oil_unlocks = set(assignments["nodes"][NODE]["unlocks"])
    steel_age_unlocks = set(assignments["nodes"][STEEL_AGE]["unlocks"])

    for output, source_recipe in SOURCE_RECIPES.items():
        if source_recipe not in script:
            failures.append(f"source recipe is not removed: {source_recipe}")
        replacement = REPLACEMENTS[output]
        if replacement not in script:
            failures.append(f"replacement recipe is absent: {replacement}")
        row = rows.get(output)
        if row is None:
            failures.append(f"dependency manifest is missing: {output}")
            continue
        if row.get("node") != NODE or row.get("recipe_id") != replacement:
            failures.append(f"dependency manifest has wrong node/id: {output}")
        forbidden_inputs = sorted(
            ingredient
            for ingredient in row.get("ingredients", [])
            if any(fragment in ingredient for fragment in FORBIDDEN_RECIPE_INPUT_FRAGMENTS)
        )
        if forbidden_inputs:
            failures.append(
                f"{output} has post-Blast-Furnace ingredients: {' | '.join(forbidden_inputs)}"
            )
        if output not in oil_unlocks:
            failures.append(f"Oil Processing assignment is missing output: {output}")

    missing_components = sorted(PRE_STEEL_COMPONENTS - steel_age_unlocks)
    if missing_components:
        failures.append(
            "The Steel Age assignment is missing pre-steel components: "
            + " | ".join(missing_components)
        )

    policies = load_json(project / "tools" / "canonicalization_policies.json")
    policy_by_output = {
        policy["machine"]: policy for policy in policies.get("machine_overhauls", [])
    }
    for output, replacement in REPLACEMENTS.items():
        policy = policy_by_output.get(output)
        if policy is None:
            failures.append(f"construction-overhaul policy is missing: {output}")
        elif (
            policy.get("node") != NODE
            or policy.get("script") != SCRIPT
            or policy.get("replacement_recipe") != replacement
            or policy.get("replacement_type") != "minecraft:crafting_shaped"
        ):
            failures.append(f"construction-overhaul policy is inconsistent: {output}")

    tfmg_jar = find_tfmg_jar(args.instance.resolve())
    with zipfile.ZipFile(tfmg_jar) as archive:
        names = set(archive.namelist())
        for output, source_recipe in SOURCE_RECIPES.items():
            path = recipe_path(source_recipe)
            if path not in names:
                failures.append(f"TFMG source recipe is absent: {source_recipe}")
                continue
            recipe = json.loads(archive.read(path).decode("utf-8-sig"))
            result = recipe.get("result", {})
            actual_output = result.get("id") or result.get("item")
            if actual_output != output:
                failures.append(
                    f"TFMG source output mismatch for {source_recipe}: {actual_output!r}"
                )
        pipe_tag_path = "data/tfmg/tags/block/industrial_pipe.json"
        if pipe_tag_path not in names:
            failures.append("TFMG industrial_pipe block tag is absent")

    print(
        f"Checked {len(SOURCE_RECIPES)} oil-field replacements against "
        f"{tfmg_jar.name} and {len(graph['edges'])} authoritative Draw.io edges."
    )
    if failures:
        print(f"FAIL: {len(failures)} oil-parallelism issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print(
        "PASS: Oil Processing is steel-free, fully mapped, and parallel to Blast Furnace."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
