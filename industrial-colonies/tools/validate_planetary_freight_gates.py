#!/usr/bin/env python3
"""Validate the Mars route computer and offworld Ender Chest freight gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
COSMONAUTICS_JAR = "cosmonautics-26.08.307.jar"
DEEP_SPACE_CLASS = (
    "dev/devce/rocketnautics/content/orbit/DeepSpaceInstance.class"
)
DEEP_SPACE_SHA256 = (
    "4E08E479D7BF7A53FA22B9D857A4C1BE37B34D813506C0AD7E3BDE312B72ED9C"
)
MIXIN = Path(
    "src/main/java/dev/godpc/industrialcolonies/mixin/DeepSpaceInstanceMixin.java"
)
AUTHORIZATION = Path(
    "src/main/java/dev/godpc/industrialcolonies/space/SpaceflightAuthorization.java"
)
ENDER_GATE = Path(
    "src/main/java/dev/godpc/industrialcolonies/space/OffworldEnderChestGate.java"
)
DIMENSION_POLICY = Path(
    "src/main/java/dev/godpc/industrialcolonies/space/AmbientKineticPolicy.java"
)
MARS_BLOCK = Path(
    "src/main/java/dev/godpc/industrialcolonies/space/MarsNavigationComputerBlock.java"
)
MARS_BLOCK_ENTITY = Path(
    "src/main/java/dev/godpc/industrialcolonies/space/MarsNavigationComputerBlockEntity.java"
)
MIXIN_CONFIG = Path("src/main/resources/industrial_colonies.mixins.json")
LANG = Path("src/main/resources/assets/industrial_colonies/lang/en_us.json")
BLOCKS = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlocks.java")
BLOCK_ENTITIES = Path(
    "src/main/java/dev/godpc/industrialcolonies/IndustrialBlockEntities.java"
)
ITEMS = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java")
ENTRYPOINT = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialColonies.java")
BUILD = Path("build.gradle")

DENIED_DIMENSIONS = (
    "rocketnautics:deep_space",
    "ad_astra:earth_orbit",
    "ad_astra:moon",
    "ad_astra:moon_orbit",
    "ad_astra:mars",
    "ad_astra:mars_orbit",
    "ad_astra:mercury",
    "ad_astra:mercury_orbit",
    "ad_astra:venus",
    "ad_astra:venus_orbit",
    "ad_astra:glacio",
    "ad_astra:glacio_orbit",
    "rocketnautics:moon",
    "rocketnautics_addon:mars",
)

RESOURCE_FILES = (
    Path("src/main/resources/assets/industrial_colonies/blockstates/mars_navigation_computer.json"),
    Path("src/main/resources/assets/industrial_colonies/models/block/mars_navigation_computer.json"),
    Path("src/main/resources/assets/industrial_colonies/models/item/mars_navigation_computer.json"),
    Path("src/main/resources/data/industrial_colonies/loot_table/blocks/mars_navigation_computer.json"),
)
REQUIRED_FILES = (
    MIXIN,
    AUTHORIZATION,
    ENDER_GATE,
    DIMENSION_POLICY,
    MARS_BLOCK,
    MARS_BLOCK_ENTITY,
    MIXIN_CONFIG,
    LANG,
    BLOCKS,
    BLOCK_ENTITIES,
    ITEMS,
    ENTRYPOINT,
    BUILD,
    *RESOURCE_FILES,
)
PROJECT_JAR_ENTRIES = (
    "dev/godpc/industrialcolonies/mixin/DeepSpaceInstanceMixin.class",
    "dev/godpc/industrialcolonies/space/SpaceflightAuthorization.class",
    "dev/godpc/industrialcolonies/space/OffworldEnderChestGate.class",
    "dev/godpc/industrialcolonies/space/MarsNavigationComputerBlock.class",
    "dev/godpc/industrialcolonies/space/MarsNavigationComputerBlockEntity.class",
    "industrial_colonies.mixins.json",
    "assets/industrial_colonies/lang/en_us.json",
    "assets/industrial_colonies/blockstates/mars_navigation_computer.json",
    "assets/industrial_colonies/models/block/mars_navigation_computer.json",
    "assets/industrial_colonies/models/item/mars_navigation_computer.json",
    "data/industrial_colonies/loot_table/blocks/mars_navigation_computer.json",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def policy_dimensions(source: str) -> list[str] | None:
    match = re.search(
        r"\bMANAGED_OFFWORLD_DIMENSIONS\s*=\s*Set\.of\((.*?)\n\s*\);",
        source,
        flags=re.DOTALL,
    )
    if match is None:
        return None
    return [
        f"{namespace}:{path}"
        for namespace, path in re.findall(
            r'dimension\("([a-z0-9_.-]+)",\s*"([a-z0-9_./-]+)"\)',
            match.group(1),
        )
    ]


def validate_installed_cosmonautics(mods: Path, failures: list[str]) -> None:
    jars = sorted(mods.glob("cosmonautics-*.jar"))
    expected = mods / COSMONAUTICS_JAR
    if jars != [expected]:
        failures.append(
            f"Cosmonautics target must be exactly {COSMONAUTICS_JAR}; "
            f"found {[path.name for path in jars]}"
        )
        return
    try:
        with zipfile.ZipFile(expected) as archive:
            bytecode = archive.read(DEEP_SPACE_CLASS)
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect installed DeepSpaceInstance: {exc}")
        return
    digest = hashlib.sha256(bytecode).hexdigest().upper()
    if digest != DEEP_SPACE_SHA256:
        failures.append(f"installed DeepSpaceInstance bytecode drifted: {digest}")
    for marker in (
        b"tick",
        b"allowToDimension",
        b"exitDeepSpace",
        b"isProcessingRetirement",
        b"lastOrbiting",
        b"collectOnlinePlayers",
        b"collectLoadedSublevels",
        b"getOfflinePlayers",
        b"getUnloadedSublevels",
    ):
        if marker not in bytecode:
            failures.append(
                f"installed DeepSpaceInstance lost sentinel {marker.decode()}"
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
                failures.append(
                    f"deployment candidate JAR lacks planetary freight entries: {missing}"
                )
                return
            mixins = json.loads(archive.read("industrial_colonies.mixins.json"))
            language = json.loads(
                archive.read("assets/industrial_colonies/lang/en_us.json")
            )
            mixin_bytecode = archive.read(PROJECT_JAR_ENTRIES[0])
    except (OSError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect deployment candidate JAR: {exc}")
        return
    if mixins.get("mixins", []).count("DeepSpaceInstanceMixin") != 1:
        failures.append("candidate JAR does not enable DeepSpaceInstanceMixin once")
    if language.get("block.industrial_colonies.mars_navigation_computer") != (
        "Mars Navigation Computer"
    ):
        failures.append("candidate JAR lacks Mars Navigation Computer language")
    for marker in (b"allowToDimension()Z", b"require", b"mayDescendToManagedPlanet"):
        if marker not in mixin_bytecode:
            failures.append(
                f"candidate Mars mixin bytecode lacks marker {marker.decode()}"
            )


def validate(
    project: Path,
    mods: Path | None = None,
    project_jar: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        if not (project / relative).is_file():
            failures.append(f"missing planetary freight file: {relative.as_posix()}")
    if failures:
        return failures

    mixin = (project / MIXIN).read_text(encoding="utf-8-sig")
    for fragment in (
        "@Mixin(value = DeepSpaceInstance.class, remap = false)",
        'method = "tick(Lnet/minecraft/server/MinecraftServer;)V"',
        "AllowedTransfer;allowToDimension()Z",
        "require = 1",
        "@Shadow",
        "private CubePlanet lastOrbiting;",
        "dimensionAllowsTransfer",
        "SpaceflightAuthorization.mayDescendToManagedPlanet",
    ):
        if fragment not in mixin:
            failures.append(f"Mars descent mixin contract drifted: {fragment}")
    for forbidden in ("@Pseudo", "exitDeepSpace", "cancellable = true", "@Inject"):
        if forbidden in mixin:
            failures.append(f"Mars descent mixin uses unsafe hook: {forbidden}")

    authorization = (project / AUTHORIZATION).read_text(encoding="utf-8-sig")
    for fragment in (
        'ResourceLocation.fromNamespaceAndPath("ad_astra", "mars")',
        "destination.linkedDimension().key()",
        "deepSpace.getOfflinePlayers().isEmpty()",
        "deepSpace.getUnloadedSublevels().isEmpty()",
        "deepSpace.collectOnlinePlayers(server, players::add)",
        "deepSpace.collectLoadedSublevels(server",
        "Sable.HELPER.getTrackingOrVehicleSubLevel(player)",
        "!(associated instanceof ServerSubLevel ship)",
        "|| ship.isRemoved()",
        "|| !ships.contains(ship)",
        "hasMarsNavigationComputer(ship)",
        "actor instanceof MarsNavigationComputerBlockEntity",
        "!computer.isRemoved()",
    ):
        if fragment not in authorization:
            failures.append(f"Mars authorization contract drifted: {fragment}")

    ender_gate = (project / ENDER_GATE).read_text(encoding="utf-8-sig")
    for fragment in (
        "PlayerInteractEvent.RightClickBlock",
        ".is(Blocks.ENDER_CHEST)",
        "AmbientKineticPolicy.isManagedOffworld",
        "event.setCancellationResult(InteractionResult.FAIL)",
        "event.setCanceled(true)",
        "PlayerChangedDimensionEvent",
        "PlayerContainerEvent.Open",
        "menu.getContainer() == player.getEnderChestInventory()",
        "player.closeContainer()",
    ):
        if fragment not in ender_gate:
            failures.append(f"offworld Ender Chest gate drifted: {fragment}")
    if "dimension() != Level.OVERWORLD" in ender_gate:
        failures.append("Ender Chest gate may not disable unrelated non-space dimensions")

    policy = (project / DIMENSION_POLICY).read_text(encoding="utf-8-sig")
    if policy_dimensions(policy) != list(DENIED_DIMENSIONS):
        failures.append("managed offworld dimension set drifted")
    if 'dimension("minecraft", "overworld")' in policy:
        failures.append("Overworld must remain outside the offworld freight boundary")

    if "implements BlockEntitySubLevelActor" not in (
        project / MARS_BLOCK_ENTITY
    ).read_text(encoding="utf-8-sig"):
        failures.append("Mars Navigation Computer is no longer a Sable actor")

    registrations = "\n".join(
        (project / path).read_text(encoding="utf-8-sig")
        for path in (BLOCKS, BLOCK_ENTITIES, ITEMS)
    )
    if registrations.count('"mars_navigation_computer"') != 3:
        failures.append("Mars Navigation Computer block/item/entity registration drifted")
    entrypoint = (project / ENTRYPOINT).read_text(encoding="utf-8-sig")
    if "OffworldEnderChestGate.register();" not in entrypoint:
        failures.append("offworld Ender Chest event listeners are not registered")

    config = load_json(project / MIXIN_CONFIG)
    if config.get("mixins", []).count("DeepSpaceInstanceMixin") != 1:
        failures.append("DeepSpaceInstanceMixin must occur exactly once")
    language = load_json(project / LANG)
    if language.get("block.industrial_colonies.mars_navigation_computer") != (
        "Mars Navigation Computer"
    ):
        failures.append("Mars Navigation Computer language entry drifted")

    build = (project / BUILD).read_text(encoding="utf-8-sig")
    for fragment in (
        "cosmonautics-26.08.307.jar",
        "extractCosmonauticsGateApi",
        "exclude 'META-INF/services/**'",
        "compileOnly files(generatedCosmonauticsApi.get().asFile)",
    ):
        if fragment not in build:
            failures.append(f"sanitized Cosmonautics compile contract drifted: {fragment}")
    if "'cosmonautics-26.08.307.jar'," in build:
        failures.append("raw Cosmonautics JAR may not be placed on javac classpath")

    if mods is not None:
        validate_installed_cosmonautics(mods, failures)
    if project_jar is not None:
        validate_project_jar(project_jar, failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--mods", type=Path)
    parser.add_argument("--project-jar", type=Path)
    args = parser.parse_args()
    failures = validate(
        args.project.resolve(),
        args.mods.resolve() if args.mods else None,
        args.project_jar.resolve() if args.project_jar else None,
    )
    if failures:
        print("FAIL: planetary freight gates are invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "PASS: canonical Mars descent requires a physical Desh route computer "
        "on every occupied loaded ship, and Ender Chests remain terrestrial-only."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
