#!/usr/bin/env python3
"""Validate the physical post-Star authorization gate for block-built ships."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
RECIPE_ID = "industrial_colonies:space/orbital_flight_computer"
OUTPUT = "industrial_colonies:orbital_flight_computer"
INDUSTRIAL_STAR = "industrial_colonies:industrial_star"
NODE = "CR02 — Orbital Guidance"
PHASE = "Orbital Engineering"
PATTERN = ["VUTUN", "QECEQ", "TCSCT", "QECEQ", "AUTUA"]
KEY = {
    "V": "allthemodium:vibranium_allthemodium_alloy_ingot",
    "N": "allthemodium:unobtainium_vibranium_alloy_ingot",
    "A": "allthemodium:unobtainium_allthemodium_alloy_ingot",
    "U": "mekanism:ultimate_control_circuit",
    "Q": "mekanism:ultimate_energy_cube",
    "T": "tfmg:circuit_board",
    "E": "ae2:engineering_processor",
    "C": "computercraft:computer_advanced",
    "S": INDUSTRIAL_STAR,
}

MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/SpaceTransitionHandlerMixin.java")
AUTHORIZATION = Path("src/main/java/dev/godpc/industrialcolonies/space/SpaceflightAuthorization.java")
BLOCK_ENTITY = Path("src/main/java/dev/godpc/industrialcolonies/space/OrbitalFlightComputerBlockEntity.java")
BLOCKS = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlocks.java")
BLOCK_ENTITIES = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlockEntities.java")
ITEMS = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java")
MIXIN_CONFIG = Path("src/main/resources/industrial_colonies.mixins.json")
SEED = Path("progression/managed_recipe_overhaul.seed.json")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
ASSIGNMENTS = Path("progression/machine_node_assignments.json")
KJSGEN = Path("pack-kjsgen/default.reviewed.managed.json")

REQUIRED_FILES = (
    MIXIN,
    AUTHORIZATION,
    BLOCK_ENTITY,
    BLOCKS,
    BLOCK_ENTITIES,
    ITEMS,
    MIXIN_CONFIG,
    SEED,
    MANIFEST,
    ASSIGNMENTS,
    KJSGEN,
    Path("build.gradle"),
    Path("src/main/templates/META-INF/neoforge.mods.toml"),
    Path("src/main/resources/assets/industrial_colonies/lang/en_us.json"),
    Path("src/main/resources/assets/industrial_colonies/blockstates/orbital_flight_computer.json"),
    Path("src/main/resources/assets/industrial_colonies/models/block/orbital_flight_computer.json"),
    Path("src/main/resources/assets/industrial_colonies/models/item/orbital_flight_computer.json"),
    Path("src/main/resources/data/industrial_colonies/loot_table/blocks/orbital_flight_computer.json"),
)

PROJECT_JAR_ENTRIES = (
    "dev/godpc/industrialcolonies/mixin/SpaceTransitionHandlerMixin.class",
    "dev/godpc/industrialcolonies/space/OrbitalFlightComputerBlock.class",
    "dev/godpc/industrialcolonies/space/OrbitalFlightComputerBlockEntity.class",
    "industrial_colonies.mixins.json",
    "assets/industrial_colonies/lang/en_us.json",
    "assets/industrial_colonies/blockstates/orbital_flight_computer.json",
    "assets/industrial_colonies/models/block/orbital_flight_computer.json",
    "assets/industrial_colonies/models/item/orbital_flight_computer.json",
    "data/industrial_colonies/loot_table/blocks/orbital_flight_computer.json",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def exactly_one_recipe(payload: dict, recipe_id: str) -> dict | None:
    rows = [row for row in payload.get("recipes", []) if row.get("id") == recipe_id]
    return rows[0] if len(rows) == 1 else None


def expected_reviewed_slots() -> dict[str, dict[str, str]]:
    slots: dict[str, dict[str, str]] = {}
    for row_index, row in enumerate(PATTERN):
        for column_index, symbol in enumerate(row):
            if symbol == " ":
                continue
            slots[f"cell_{row_index}_{column_index}"] = {
                "kind": "ITEM",
                "id": KEY[symbol],
            }
    slots["output"] = {"kind": "ITEM", "id": OUTPUT}
    return slots


def validate_bytecode(mods: Path, failures: list[str]) -> None:
    jars = sorted(mods.glob("cosmonautics-*.jar"))
    if len(jars) != 1:
        failures.append(f"expected one installed Cosmonautics JAR, found {len(jars)}")
        return
    class_path = "dev/devce/rocketnautics/content/physics/SpaceTransitionHandler.class"
    try:
        with zipfile.ZipFile(jars[0]) as archive:
            bytecode = archive.read(class_path)
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect installed SpaceTransitionHandler: {exc}")
        return
    for sentinel in (b"lambda$init$2", b"allowToSpace", b"ship"):
        if sentinel not in bytecode:
            failures.append(
                f"installed SpaceTransitionHandler lost bytecode sentinel {sentinel.decode()}"
            )


def validate_project_jar(project_jar: Path, failures: list[str]) -> None:
    if not project_jar.is_file():
        failures.append(f"missing deployment candidate JAR: {project_jar}")
        return
    try:
        with zipfile.ZipFile(project_jar) as archive:
            names = set(archive.namelist())
            missing = sorted(set(PROJECT_JAR_ENTRIES) - names)
            if missing:
                failures.append(f"deployment candidate JAR lacks orbital gate entries: {missing}")
                return
            mixin_config = json.loads(archive.read("industrial_colonies.mixins.json"))
            language = json.loads(
                archive.read("assets/industrial_colonies/lang/en_us.json")
            )
    except (OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
        failures.append(f"cannot inspect deployment candidate JAR: {exc}")
        return
    if mixin_config.get("mixins", []).count("SpaceTransitionHandlerMixin") != 1:
        failures.append("deployment candidate JAR does not enable SpaceTransitionHandlerMixin")
    if language.get("block.industrial_colonies.orbital_flight_computer") != (
        "Orbital Flight Computer"
    ):
        failures.append("deployment candidate JAR lacks the flight-computer language asset")


def validate(
    project: Path,
    mods: Path | None = None,
    project_jar: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        if not (project / relative).is_file():
            failures.append(f"missing orbital gate file: {relative.as_posix()}")
    if failures:
        return failures

    mixin = (project / MIXIN).read_text(encoding="utf-8-sig")
    required_mixin_fragments = (
        'targets = "dev.devce.rocketnautics.content.physics.SpaceTransitionHandler"',
        'method = "lambda$init$2(Ldev/ryanhcode/sable/sublevel/system/SubLevelPhysicsSystem;D)V"',
        'target = "Ldev/devce/rocketnautics/api/orbit/AllowedTransfer;allowToSpace()Z"',
        'require = 1',
        '@Local(name = "ship") ServerSubLevel ship',
        'dimensionAllowsSpace && SpaceflightAuthorization.hasOrbitalFlightComputer(ship)',
    )
    for fragment in required_mixin_fragments:
        if fragment not in mixin:
            failures.append(f"orbital transition mixin contract drifted: {fragment}")

    authorization = (project / AUTHORIZATION).read_text(encoding="utf-8-sig")
    for fragment in (
        "ship.getPlot().getBlockEntityActors()",
        "actor instanceof OrbitalFlightComputerBlockEntity",
        "!computer.isRemoved()",
        "return false;",
    ):
        if fragment not in authorization:
            failures.append(f"flight authorization no longer fails closed: {fragment}")

    block_entity = (project / BLOCK_ENTITY).read_text(encoding="utf-8-sig")
    if "implements BlockEntitySubLevelActor" not in block_entity:
        failures.append("Orbital Flight Computer is no longer indexed as a Sable ship actor")

    registrations = "\n".join(
        (project / path).read_text(encoding="utf-8-sig")
        for path in (BLOCKS, BLOCK_ENTITIES, ITEMS)
    )
    if registrations.count('"orbital_flight_computer"') != 3:
        failures.append("Orbital Flight Computer block/item/block-entity registration drifted")

    mixin_config = load_json(project / MIXIN_CONFIG)
    if mixin_config.get("mixins", []).count("SpaceTransitionHandlerMixin") != 1:
        failures.append("SpaceTransitionHandlerMixin must occur exactly once in the mixin config")

    seed = load_json(project / SEED)
    recipe = exactly_one_recipe(seed, RECIPE_ID)
    if recipe is None:
        failures.append("source seed must contain exactly one Orbital Flight Computer recipe")
    else:
        expected = {
            "node": NODE,
            "phase": PHASE,
            "type": "mechanical_crafting",
            "output": OUTPUT,
            "exclusive_output": True,
        }
        for key, value in expected.items():
            if recipe.get(key) != value:
                failures.append(f"Orbital Flight Computer recipe {key} drifted")
        if recipe.get("key", {}).get("S") != INDUSTRIAL_STAR:
            failures.append("Orbital Flight Computer recipe key drifted")
        pattern = recipe.get("pattern")
        if not isinstance(pattern, list) or len(pattern) != 5 or any(
            not isinstance(row, str) or len(row) != 5 for row in pattern
        ):
            failures.append("Orbital Flight Computer source recipe is not a 5x5 grid")

    assignments = load_json(project / ASSIGNMENTS).get("nodes", {})
    if assignments.get(NODE, {}).get("unlocks") != [OUTPUT]:
        failures.append("Orbital Guidance assignment must unlock only the flight computer")

    manifest_recipe = exactly_one_recipe(load_json(project / MANIFEST), RECIPE_ID)
    if manifest_recipe is None:
        failures.append("compiled recipe manifest is missing the Orbital Flight Computer")

    cards = [
        card
        for card in load_json(project / KJSGEN).get("recipes", [])
        if card.get("recipeId") == RECIPE_ID
    ]
    if len(cards) != 1:
        failures.append("KubeJS Gen project must contain exactly one flight-computer card")
    else:
        card = cards[0]
        if card.get("type") != "kjsgen:create_mechanical_crafting":
            failures.append("flight-computer project card is not Mechanical Crafting")
        if card.get("params") != {"gridW": "5", "gridH": "5"}:
            failures.append("flight-computer project card is not 5x5")
        if card.get("slots", {}).get("output", {}).get("id") != OUTPUT:
            failures.append("flight-computer project card output drifted")
        if card.get("slots") != expected_reviewed_slots():
            failures.append("flight-computer reviewed recipe pattern/key drifted")

    build = (project / "build.gradle").read_text(encoding="utf-8-sig")
    for fragment in (
        "sable-neoforge-*.jar",
        "sable-companion-common-1.21.1-1.6.0.jar",
        "extractSableCompanionApi",
    ):
        if fragment not in build:
            failures.append(f"Sable compile dependency contract drifted: {fragment}")

    metadata = (project / "src/main/templates/META-INF/neoforge.mods.toml").read_text(
        encoding="utf-8-sig"
    )
    for dependency in ('modId="sable"', 'modId="rocketnautics"'):
        if dependency not in metadata:
            failures.append(f"missing runtime orbital dependency: {dependency}")

    language = load_json(project / "src/main/resources/assets/industrial_colonies/lang/en_us.json")
    if language.get("block.industrial_colonies.orbital_flight_computer") != "Orbital Flight Computer":
        failures.append("Orbital Flight Computer language entry drifted")

    if mods is not None:
        validate_bytecode(mods, failures)
    if project_jar is not None:
        validate_project_jar(project_jar, failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--mods", type=Path)
    parser.add_argument(
        "--project-jar",
        type=Path,
        help="Built deployment candidate JAR whose classes and assets must contain the gate.",
    )
    args = parser.parse_args()
    failures = validate(
        args.project.resolve(),
        args.mods.resolve() if args.mods else None,
        args.project_jar.resolve() if args.project_jar else None,
    )
    if failures:
        print("FAIL: Orbital Flight Computer gate is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "PASS: the post-Star Orbital Flight Computer is a 5x5 KubeJS Gen recipe and "
        "fails closed aboard Sable ships before Cosmonautics teleports them to orbit."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
