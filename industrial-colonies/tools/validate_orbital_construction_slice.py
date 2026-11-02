#!/usr/bin/env python3
"""Validate the source-owned orbital construction and Sable assembly slice."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
SEED = Path("progression/managed_recipe_overhaul.seed.json")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
COMPILED = Path("pack-kjsgen/default.managed.json")
ASSIGNMENTS = Path("progression/machine_node_assignments.json")
LAYOUT = Path("progression/minecolonies_branch_layout.json")
DEFERRED = Path("pack-scripts/server_scripts/industrial_space_entry_deferred.js")
ITEMS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java")
LANG = Path("src/main/resources/assets/industrial_colonies/lang/en_us.json")

PHASE = "Orbital Engineering"
NODE = "CR02 — Orbital Construction"
MACHINE = "createcasing:refined_radiance_deployer"
OFC_RECIPE = "industrial_colonies:space/orbital_flight_computer"
MOUNT_RECIPE = "industrial_colonies:space/propulsion/thruster_mount"
AIRLOCK_RECIPE = "industrial_colonies:space/life_support/airlock"
DIAGRAM_STOCK_ID = "simulated:contraption_diagram"
ASSEMBLER_STOCK_ID = "simulated:physics_assembler"
NESTED_SOURCE_JAR = (
    "create-aeronautics-bundled-1.21.1-1.3.0.jar!/META-INF/jarjar/"
    "dev.simulated_team.simulated.simulated-neoforge-1.21.1-1.3.0.jar"
)

CONSTRUCTION_RECIPES: dict[str, dict[str, Any]] = {
    "industrial_colonies:space/construction/guidance_certified_plan": {
        "node": NODE,
        "phase": PHASE,
        "order": 240,
        "type": "deploying",
        "machine": MACHINE,
        "input": "ae2:blank_pattern",
        "held": "industrial_colonies:orbital_flight_computer",
        "keep_held": True,
        "output": "industrial_colonies:guidance_certified_plan",
        "exclusive_output": True,
        "depends_on": [OFC_RECIPE],
    },
    "industrial_colonies:space/construction/propulsion_certified_plan": {
        "node": NODE,
        "phase": PHASE,
        "order": 250,
        "type": "deploying",
        "machine": MACHINE,
        "input": "industrial_colonies:guidance_certified_plan",
        "held": "rocketnautics:thruster_mount",
        "keep_held": True,
        "output": "industrial_colonies:propulsion_certified_plan",
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/construction/guidance_certified_plan",
            MOUNT_RECIPE,
        ],
    },
    "industrial_colonies:space/construction/contraption_diagram": {
        "node": NODE,
        "phase": PHASE,
        "order": 260,
        "type": "deploying",
        "machine": MACHINE,
        "input": "industrial_colonies:propulsion_certified_plan",
        "held": "ad_astra:airlock",
        "keep_held": True,
        "output": DIAGRAM_STOCK_ID,
        "remove": [DIAGRAM_STOCK_ID],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/construction/propulsion_certified_plan",
            AIRLOCK_RECIPE,
        ],
    },
    "industrial_colonies:space/construction/physics_assembler": {
        "node": NODE,
        "phase": PHASE,
        "order": 270,
        "type": "mechanical_crafting",
        "pattern": ["HMPMH", "FBVBF", "UCDCU", "FBVBF", "HMPMH"],
        "key": {
            "H": "tfmg:heavy_plate",
            "M": "tfmg:electric_motor",
            "P": "create:mechanical_piston",
            "F": "tfmg:steel_frame",
            "B": "tfmg:circuit_board",
            "V": "ad_astra:vent",
            "U": "mekanism:ultimate_control_circuit",
            "C": "computercraft:computer_advanced",
            "D": DIAGRAM_STOCK_ID,
        },
        "output": ASSEMBLER_STOCK_ID,
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:space/construction/contraption_diagram"
        ],
    },
}

NODE_UNLOCKS = [
    "industrial_colonies:guidance_certified_plan",
    "industrial_colonies:propulsion_certified_plan",
    DIAGRAM_STOCK_ID,
    ASSEMBLER_STOCK_ID,
]
PLAN_ASSETS = {
    "guidance_certified_plan": "Guidance-Certified Construction Plan",
    "propulsion_certified_plan": "Propulsion-Certified Construction Plan",
}
STOCK_RECIPES = {
    DIAGRAM_STOCK_ID: {
        "recipe_type": "minecraft:crafting_shapeless",
        "source_path": "data/simulated/recipe/contraption_diagram.json",
        "outputs": {DIAGRAM_STOCK_ID},
        "inputs": {"minecraft:paper", ASSEMBLER_STOCK_ID},
    },
    ASSEMBLER_STOCK_ID: {
        "recipe_type": "minecraft:crafting_shaped",
        "source_path": "data/simulated/recipe/physics_assembler.json",
        "outputs": {ASSEMBLER_STOCK_ID},
        "inputs": {
            "create:andesite_alloy",
            "create:andesite_casing",
            "minecraft:lever",
        },
    },
}
RETAINED_CATALYSTS = {
    "industrial_colonies:orbital_flight_computer",
    "rocketnautics:thruster_mount",
    "ad_astra:airlock",
}
FORBIDDEN_REMOVAL_FIELDS = {
    "remove_by_output",
    "removeByOutput",
    "remove_by_mod",
    "removeByMod",
    "replace",
    "replace_recipe",
    "replaceRecipe",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def output_id(value: Any) -> str:
    text = str(value or "").strip()
    match = re.fullmatch(
        r"(?:(?:\d+(?:\.\d+)?)x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)", text
    )
    return match.group(1) if match else text


def split_ids(value: Any) -> set[str]:
    return {output_id(part) for part in str(value or "").split("|") if part.strip()}


def recipe_rows(payload: dict[str, Any], recipe_id: str) -> list[dict[str, Any]]:
    return [row for row in payload.get("recipes", []) if row.get("id") == recipe_id]


def has_ancestor(
    recipe_id: str,
    ancestor: str,
    recipes: dict[str, dict[str, Any]],
    seen: set[str] | None = None,
) -> bool:
    if recipe_id == ancestor:
        return True
    seen = set() if seen is None else seen
    if recipe_id in seen:
        return False
    seen.add(recipe_id)
    return any(
        has_ancestor(str(parent), ancestor, recipes, seen.copy())
        for parent in recipes.get(recipe_id, {}).get("depends_on", [])
    )


def catalog_paths(catalog: Path) -> tuple[Path, Path]:
    if catalog.is_dir():
        return catalog / "items.csv", catalog / "recipes.csv"
    return catalog.parent / "items.csv", catalog


def item_slot(item: str) -> dict[str, Any]:
    return {"kind": "ITEM", "id": output_id(item)}


def mechanical_slots(expected: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slots: dict[str, dict[str, Any]] = {}
    for row_index, pattern_row in enumerate(expected["pattern"]):
        for column_index, character in enumerate(pattern_row):
            if character != " ":
                slots[f"cell_{row_index}_{column_index}"] = item_slot(
                    expected["key"][character]
                )
    slots["output"] = item_slot(expected["output"])
    return slots


def deploying_slots(expected: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "__machine_process_deploying": item_slot(expected["machine"]),
        "input": item_slot(expected["input"]),
        "held": item_slot(expected["held"]),
        "output": item_slot(expected["output"]),
    }


def validate_manifest(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing assembled construction manifest: {path}")
        return
    payload = load_json(path)
    for recipe_id, expected in CONSTRUCTION_RECIPES.items():
        found = recipe_rows(payload, recipe_id)
        if len(found) != 1:
            failures.append(f"assembled manifest must contain exactly one {recipe_id}")
            continue
        recipe = found[0]
        for field, value in expected.items():
            if field not in {"depends_on", "exclusive_output"} and recipe.get(field) != value:
                failures.append(f"assembled {recipe_id} {field} drifted")
        missing = sorted(set(expected["depends_on"]) - set(recipe.get("depends_on", [])))
        if missing:
            failures.append(f"assembled {recipe_id} lost dependencies: {missing}")


def validate_compiled(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing KJSGen construction project: {path}")
        return
    payload = load_json(path)
    cards = payload.get("recipes", [])
    for recipe_id, expected in CONSTRUCTION_RECIPES.items():
        found = [card for card in cards if card.get("recipeId") == recipe_id]
        if len(found) != 1:
            failures.append(f"KJSGen project must contain exactly one construction card {recipe_id}")
            continue
        card = found[0]
        if card.get("replaceRecipe") is not False:
            failures.append(f"{recipe_id} unexpectedly replaces recipes by output")
        if expected["type"] == "deploying":
            if card.get("type") != "kjsgen:create_deploying":
                failures.append(f"{recipe_id} KJSGen card is not Create Deploying")
            if card.get("params") != {"keepHeldItem": "true"}:
                failures.append(f"{recipe_id} did not compile its retained catalyst")
            if card.get("slots") != deploying_slots(expected):
                failures.append(f"{recipe_id} KJSGen deploying slots drifted")
        else:
            if card.get("type") != "kjsgen:create_mechanical_crafting":
                failures.append(f"{recipe_id} KJSGen card is not Mechanical Crafting")
            if card.get("params") != {"gridW": "5", "gridH": "5"}:
                failures.append(f"{recipe_id} KJSGen grid dimensions drifted")
            if card.get("slots") != mechanical_slots(expected):
                failures.append(f"{recipe_id} KJSGen mechanical slots drifted")

    removals = payload.get("removals", [])
    exact = [row for row in removals if row.get("recipeId") == DIAGRAM_STOCK_ID]
    if len(exact) != 1:
        failures.append("KJSGen removals must retire stock contraption_diagram exactly once")
    elif any(str(exact[0].get(field, "")).strip() for field in ("output", "input", "mod")):
        failures.append("contraption_diagram removal is broader than its exact stock ID")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    items_path, recipes_path = catalog_paths(catalog)
    if not items_path.is_file() or not recipes_path.is_file():
        failures.append(f"catalog must provide items.csv and recipes.csv: {catalog}")
        return
    with items_path.open("r", encoding="utf-8-sig", newline="") as handle:
        items = {row.get("item_id", "") for row in csv.DictReader(handle)}
    with recipes_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row.get("recipe_id", ""): row for row in rows}

    external_items = {
        output_id(value)
        for expected in CONSTRUCTION_RECIPES.values()
        for value in [
            expected.get("output"),
            expected.get("input"),
            expected.get("held"),
            *expected.get("key", {}).values(),
            expected.get("machine"),
        ]
        if value and not output_id(value).startswith("industrial_colonies:")
    }
    missing_items = sorted(external_items - items)
    if missing_items:
        failures.append(f"installed item catalog is missing construction IDs: {missing_items}")

    for recipe_id, expected in STOCK_RECIPES.items():
        row = by_id.get(recipe_id)
        if row is None:
            failures.append(f"installed catalog is missing nested stock recipe {recipe_id}")
            continue
        for field in ("recipe_type", "source_path"):
            if row.get(field) != expected[field]:
                failures.append(f"stock {recipe_id} {field} drifted")
        if row.get("source_jar") != NESTED_SOURCE_JAR:
            failures.append(f"stock {recipe_id} nested source JAR drifted")
        for field in ("outputs", "inputs"):
            if split_ids(row.get(field)) != expected[field]:
                failures.append(f"stock {recipe_id} {field} drifted")


def validate_assets(project: Path, failures: list[str]) -> None:
    java = (project / ITEMS_JAVA).read_text(encoding="utf-8-sig")
    lang = load_json(project / LANG)
    for path, title in PLAN_ASSETS.items():
        if java.count(f'"{path}"') != 1:
            failures.append(f"custom construction plan registration drifted: {path}")
        model_path = (
            project
            / "src/main/resources/assets/industrial_colonies/models/item"
            / f"{path}.json"
        )
        if not model_path.is_file():
            failures.append(f"custom construction plan model is missing: {path}")
        else:
            model = load_json(model_path)
            if model.get("parent") != "minecraft:item/generated" or not str(
                model.get("textures", {}).get("layer0", "")
            ).strip():
                failures.append(f"custom construction plan model drifted: {path}")
        if lang.get(f"item.industrial_colonies.{path}") != title:
            failures.append(f"custom construction plan language entry drifted: {path}")


def validate(
    project: Path,
    catalog: Path | None = None,
    manifest: Path | None = None,
    compiled: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    for relative in (SEED, ASSIGNMENTS, LAYOUT, DEFERRED, ITEMS_JAVA, LANG):
        if not (project / relative).is_file():
            failures.append(f"missing orbital construction source file: {relative.as_posix()}")
    if failures:
        return failures

    seed = load_json(project / SEED)
    rows = seed.get("recipes", [])
    by_id = {row.get("id", ""): row for row in rows}
    for recipe_id, expected in CONSTRUCTION_RECIPES.items():
        found = recipe_rows(seed, recipe_id)
        if len(found) != 1:
            failures.append(f"managed seed must contain exactly one {recipe_id}")
            continue
        recipe = found[0]
        for field, value in expected.items():
            if recipe.get(field) != value:
                failures.append(f"{recipe_id} {field} drifted")
        if not str(recipe.get("comment", "")).strip():
            failures.append(f"{recipe_id} has no manufacturing rationale")
        if set(recipe).intersection(FORBIDDEN_REMOVAL_FIELDS):
            failures.append(f"{recipe_id} contains a broad removal directive")
        required_ancestors = {
            "industrial_colonies:space/construction/guidance_certified_plan": (
                OFC_RECIPE,
            ),
            "industrial_colonies:space/construction/propulsion_certified_plan": (
                OFC_RECIPE,
                MOUNT_RECIPE,
            ),
            "industrial_colonies:space/construction/contraption_diagram": (
                OFC_RECIPE,
                MOUNT_RECIPE,
                AIRLOCK_RECIPE,
            ),
            "industrial_colonies:space/construction/physics_assembler": (
                OFC_RECIPE,
                MOUNT_RECIPE,
                AIRLOCK_RECIPE,
            ),
        }[recipe_id]
        for ancestor in required_ancestors:
            if not has_ancestor(recipe_id, ancestor, by_id):
                failures.append(f"{recipe_id} is not downstream of {ancestor}")

    deploying = [
        by_id[recipe_id]
        for recipe_id, expected in CONSTRUCTION_RECIPES.items()
        if expected["type"] == "deploying" and recipe_id in by_id
    ]
    if {row.get("held") for row in deploying} != RETAINED_CATALYSTS:
        failures.append("construction certification catalyst set drifted")
    if any(row.get("machine") != MACHINE or row.get("keep_held") is not True for row in deploying):
        failures.append("all three certification passes must retain their exact-machine catalyst")

    assembler = by_id.get("industrial_colonies:space/construction/physics_assembler", {})
    assembler_ingredients = {output_id(value) for value in assembler.get("key", {}).values()}
    if RETAINED_CATALYSTS.intersection(assembler_ingredients):
        failures.append("Physics Assembler recipe consumes a retained onboard certification fixture")
    if len(assembler.get("pattern", [])) != 5 or any(
        len(row) != 5 for row in assembler.get("pattern", [])
    ):
        failures.append("Physics Assembler is not an exact 5x5 mechanical assembly")

    diagram = by_id.get("industrial_colonies:space/construction/contraption_diagram", {})
    if diagram.get("remove") != [DIAGRAM_STOCK_ID]:
        failures.append("stock contraption_diagram is not retired by exact ID only")
    managed_outputs = [output_id(row.get("output")) for row in rows]
    for unlock in NODE_UNLOCKS:
        if managed_outputs.count(unlock) != 1:
            failures.append(f"managed seed must own construction output exactly once: {unlock}")

    if seed.get("phase_by_node", {}).get(NODE) != PHASE:
        failures.append(f"{NODE} is not assigned to {PHASE}")
    assignment = load_json(project / ASSIGNMENTS).get("nodes", {}).get(NODE, {})
    if assignment.get("unlocks") != NODE_UNLOCKS:
        failures.append(f"{NODE} unlock assignment drifted")
    if assignment.get("icon") != ASSEMBLER_STOCK_ID or not str(assignment.get("role", "")).strip():
        failures.append(f"{NODE} role or icon drifted")
    if NODE in (project / LAYOUT).read_text(encoding="utf-8-sig"):
        failures.append("immutable MineColonies layout was expanded with Orbital Construction")

    deferred = (project / DEFERRED).read_text(encoding="utf-8-sig")
    if deferred.count(f"'{ASSEMBLER_STOCK_ID}'") != 1:
        failures.append("stock Physics Assembler must remain exactly deferred")
    if deferred.count(f"'{DIAGRAM_STOCK_ID}'") != 0:
        failures.append("authored contraption_diagram must not remain in the deferred boundary")
    if re.search(r"event\.remove\(\{\s*(output|mod|type|input)\s*:", deferred):
        failures.append("space boundary contains a broad recipe removal")

    validate_assets(project, failures)
    if catalog is not None:
        validate_catalog(catalog, failures)
    if manifest is not None:
        validate_manifest(manifest, failures)
    if compiled is not None:
        validate_compiled(compiled, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate(
        args.project.resolve(),
        args.catalog.resolve() if args.catalog else None,
        args.manifest.resolve() if args.manifest else None,
        args.compiled.resolve() if args.compiled else None,
    )
    if failures:
        print("FAIL: orbital construction slice is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "PASS: three retained exact-machine certification passes produce the sole "
        "Contraption Diagram route, and its 5x5 Physics Assembler remains a "
        "ground-side machine downstream of propulsion and habitat readiness."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
