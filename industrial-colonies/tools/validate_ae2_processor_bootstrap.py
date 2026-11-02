from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


PROCESSOR_RECIPES = {
    "industrial_colonies:ae2/fabrication/logic_processor": (
        "industrial_colonies:brass_sequenced_assembly",
        "ae2:logic_processor",
        2,
        {"tfmg:circuit_board", "create:precision_mechanism", "ae2:printed_silicon"},
    ),
    "industrial_colonies:ae2/fabrication/calculation_processor": (
        "industrial_colonies:weathered_iron_sequenced_assembly",
        "ae2:calculation_processor",
        2,
        {"ae2:logic_processor", "tfmg:coated_circuit_board", "create:weathered_iron_block"},
    ),
    "industrial_colonies:ae2/fabrication/engineering_processor": (
        "industrial_colonies:weathered_iron_sequenced_assembly",
        "ae2:engineering_processor",
        3,
        {"ae2:calculation_processor", "tfmg:etched_circuit_board", "mekanism:advanced_control_circuit"},
    ),
}

RETIRED_ROUTES = {
    "ae2:network/blocks/inscribers",
    "ae2:inscriber/logic_processor",
    "ae2:inscriber/calculation_processor",
    "ae2:inscriber/engineering_processor",
    "extendedae:assembler/logic_processor",
    "extendedae:assembler/calculation_processor",
    "extendedae:assembler/engineering_processor",
    "extendedae:cutter/logic_processor",
    "extendedae:cutter/calculation_processor",
    "extendedae:cutter/engineering_processor",
}


def one_jar(mods: Path, pattern: str) -> Path:
    matches = sorted(mods.glob(pattern))
    if len(matches) != 1:
        raise AssertionError(f"Expected exactly one {pattern!r} JAR, found {len(matches)}")
    return matches[0]


def jar_json(jar: Path, entry: str) -> Any:
    with zipfile.ZipFile(jar) as archive:
        return json.loads(archive.read(entry).decode("utf-8-sig"))


def resource_ids(node: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key in {"item", "id"} and isinstance(value, str) and ":" in value:
                found.add(value)
            else:
                found.update(resource_ids(value))
    elif isinstance(node, list):
        for value in node:
            found.update(resource_ids(value))
    return found


def result_id(data: dict[str, Any]) -> str | None:
    result = data.get("result")
    if isinstance(result, dict):
        return result.get("id")
    results = data.get("results")
    if isinstance(results, list) and len(results) == 1 and isinstance(results[0], dict):
        return results[0].get("id")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the physical AE2 processor and ME bootstrap progression."
    )
    parser.add_argument(
        "--project", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--node", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    node = args.node or (Path(shutil.which("node")) if shutil.which("node") else None)
    failures: list[str] = []
    if node is None or not node.is_file():
        print("FAIL: Node.js executable is required", file=sys.stderr)
        return 1

    override = (
        project / "pack-config-overrides" / "createappliedkinetics-common.toml"
    ).read_text(encoding="utf-8-sig")
    if "overwrite_ae2_recipes = false" not in override:
        failures.append("Create Applied Kinetics overwrite must remain false")

    capture = subprocess.run(
        [
            str(node),
            str(project / "tools" / "capture_kubejs_runtime.mjs"),
            str(project / "pack-scripts" / "server_scripts"),
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    captured = json.loads(capture.stdout)
    for error in captured.get("errors", []):
        failures.append(f"KubeJS capture error: {error}")

    additions = {
        operation["recipe_id"]: operation["data"]
        for operation in captured.get("operations", [])
        if operation.get("domain") == "recipe" and operation.get("action") == "add"
    }
    removals = {
        operation.get("filter", {}).get("id")
        for operation in captured.get("operations", [])
        if operation.get("domain") == "recipe" and operation.get("action") == "remove"
    }

    missing_retirements = RETIRED_ROUTES - removals
    if missing_retirements:
        failures.append(f"Missing retired processor routes: {sorted(missing_retirements)}")

    inscriber = additions.get("industrial_colonies:ae2/fabrication/inscriber")
    if not inscriber:
        failures.append("Missing physical Inscriber recipe")
    else:
        if inscriber.get("type") != "industrial_colonies:brass_mechanical_crafting":
            failures.append("Inscriber is not Brass-tier Mechanical Crafting")
        pattern = inscriber.get("pattern", [])
        if len(pattern) != 5 or any(not isinstance(row, str) or len(row) != 5 for row in pattern):
            failures.append("Inscriber recipe is not an exact 5x5 pattern")
        required = {"create:brass_casing", "tfmg:circuit_board", "create:precision_mechanism"}
        if not required <= resource_ids(inscriber):
            failures.append("Inscriber recipe lacks Brass chassis/electronics dependencies")

    for recipe_id, (recipe_type, output, loops, required) in PROCESSOR_RECIPES.items():
        recipe = additions.get(recipe_id)
        if not recipe:
            failures.append(f"Missing physical processor recipe {recipe_id}")
            continue
        if recipe.get("type") != recipe_type:
            failures.append(f"{recipe_id} has type {recipe.get('type')!r}, expected {recipe_type}")
        if recipe.get("loops") != loops:
            failures.append(f"{recipe_id} has {recipe.get('loops')} loops, expected {loops}")
        if result_id(recipe) != output:
            failures.append(f"{recipe_id} does not produce {output}")
        missing = required - resource_ids(recipe)
        if missing:
            failures.append(f"{recipe_id} lacks physical dependencies: {sorted(missing)}")

    me_drive = additions.get("industrial_colonies:ae2/me_system_basics/drive")
    if not me_drive or me_drive.get("type") != "industrial_colonies:industrial_iron_mechanical_crafting":
        failures.append("ME Drive is not an Industrial Iron tiered recipe")
    elif len(me_drive.get("pattern", [])) != 5 or any(len(row) != 5 for row in me_drive["pattern"]):
        failures.append("ME Drive recipe is not 5x5")
    elif not {"computercraft:computer_normal", "ae2:logic_processor", "tfmg:circuit_board"} <= resource_ids(me_drive):
        failures.append("ME Drive does not converge programmable control, AE logic, and a TFMG PCB")

    cell = additions.get("industrial_colonies:ae2/me_system_basics/item_storage_cell_4k")
    if not cell or cell.get("type") != "industrial_colonies:industrial_iron_sequenced_assembly":
        failures.append("4k cell is not an Industrial Iron sequenced assembly")
    elif cell.get("loops", 0) < 3:
        failures.append("4k cell must run at least three assembly loops")

    mods = args.pack_root.resolve() / "mods"
    ae2 = one_jar(mods, "appliedenergistics2-*.jar")
    for name in ("silicon_print", "logic_processor_print", "calculation_processor_print", "engineering_processor_print"):
        recipe = jar_json(ae2, f"data/ae2/recipe/inscriber/{name}.json")
        if recipe.get("type") != "ae2:inscriber":
            failures.append(f"Native printed-circuit seed {name} is no longer an Inscriber recipe")

    main_class = (
        project / "src/main/java/dev/godpc/industrialcolonies/IndustrialColonies.java"
    ).read_text(encoding="utf-8-sig")
    if "ResearchStageSynchronizer.register()" in main_class or "RecipeStageGate.register()" in main_class:
        failures.append("Research/stage registration is still active")

    print(
        "Checked the 5x5 Inscriber, three tiered processor lines, the physical ME bootstrap, "
        f"{len(RETIRED_ROUTES)} retired shortcuts, and four native printed-circuit seeds."
    )
    if failures:
        print(f"FAIL: {len(failures)} AE2 physical-progression issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: AE2 processors and ME storage are physically gated without research stages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
