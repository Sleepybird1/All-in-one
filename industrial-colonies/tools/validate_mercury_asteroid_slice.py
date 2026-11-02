#!/usr/bin/env python3
"""Fail closed on Mercury authorization and deep-space asteroid freight."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT = Path(__file__).resolve().parents[1]
SEED = Path("progression/managed_recipe_overhaul.seed.json")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
COMPILED = Path("pack-kjsgen/default.managed.json")
ASSIGNMENTS = Path("progression/machine_node_assignments.json")
QUESTS = Path("progression/ftbquests_planetary_industry.json")
NATIVE_CHAPTER = Path("pack-config-overrides/ftbquests/quests/chapters/planetary_industry.snbt")
ITEMS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java")
BLOCKS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlocks.java")
BLOCK_ENTITIES_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlockEntities.java")
AUTHORIZATION_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/space/SpaceflightAuthorization.java")
ASTEROID_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/AsteroidSpawnerMixin.java")
MIXINS_JSON = Path("src/main/resources/industrial_colonies.mixins.json")
LANG = Path("src/main/resources/assets/industrial_colonies/lang/en_us.json")
SPACE_BOUNDARY = Path("pack-scripts/server_scripts/industrial_space_entry_deferred.js")
MERCURY_PLANET = Path("src/main/resources/data/rocketnautics/universe_planets/mercury.json")
MERCURY_PHYSICS = Path("src/main/resources/data/industrial_colonies/dimension_physics/ad_astra_mercury.json")
MERCURY_ADVANCEMENT = Path("src/main/resources/data/industrial_colonies/advancement/planetary/mercury_arrival.json")
MERCURY_BLOCK = Path("src/main/java/dev/godpc/industrialcolonies/space/MercuryNavigationComputerBlock.java")
MERCURY_BLOCK_ENTITY = Path("src/main/java/dev/godpc/industrialcolonies/space/MercuryNavigationComputerBlockEntity.java")
MERCURY_BLOCKSTATE = Path("src/main/resources/assets/industrial_colonies/blockstates/mercury_navigation_computer.json")
MERCURY_BLOCK_MODEL = Path("src/main/resources/assets/industrial_colonies/models/block/mercury_navigation_computer.json")
MERCURY_ITEM_MODEL = Path("src/main/resources/assets/industrial_colonies/models/item/mercury_navigation_computer.json")
MERCURY_BLOCK_LOOT = Path("src/main/resources/data/industrial_colonies/loot_table/blocks/mercury_navigation_computer.json")

PHASE = "Planetary Industry"
NODE = "CR02 — Mercury Expedition"
RECIPE_ID = "industrial_colonies:planetary/mercury/navigation_computer"
OUTPUT = "industrial_colonies:mercury_navigation_computer"
TITANIUM_WASHING = "rocketnautics:splashing/crushed_raw_titanium"
PATTERN = ["CPUPC", "CEBEC", "SNVNS", "CEMEC", "CPUPC"]
KEY = {
    "C": "ad_astra:calorite_plate",
    "P": "ad_astra:calorite_block",
    "U": "mekanism:ultimate_control_circuit",
    "E": "ae2:engineering_processor",
    "B": "tfmg:etched_circuit_board",
    "S": "rocketnautics:sputnik",
    "N": "simulated:navigation_table",
    "V": "industrial_colonies:venus_navigation_computer",
    "M": "computercraft:computer_advanced",
}
DEPENDENCIES = [
    "industrial_colonies:planetary/calorite/plate",
    "industrial_colonies:planetary/venus/navigation_computer",
    "industrial_colonies:space/navigation/sputnik",
]
EXPECTED_RECIPE = {
    "node": NODE,
    "phase": PHASE,
    "order": 310,
    "type": "mechanical_crafting",
    "pattern": PATTERN,
    "key": KEY,
    "output": OUTPUT,
    "depends_on": DEPENDENCIES,
}
QUESTS_EXPECTED = {
    "mercury_arrival": (
        ["calorite_metallurgy"],
        [("advancement", "industrial_colonies:planetary/mercury_arrival", 1)],
    ),
    "mercury_iron_sample": (
        ["mercury_arrival"],
        [("item", "ad_astra:mercury_iron_ore", 1)],
    ),
    "asteroid_titanium": (
        ["mercury_iron_sample"],
        [("item", "rocketnautics:titanium_ore", 1)],
    ),
    "asteroid_bulk_freight": (
        ["asteroid_titanium"],
        [
            ("item", "minecraft:coal_ore", 64),
            ("item", "minecraft:iron_ore", 64),
            ("item", "minecraft:copper_ore", 64),
            ("item", "minecraft:gold_ore", 32),
            ("item", "rocketnautics:titanium_ore", 32),
        ],
    ),
}

COSMONAUTICS_JAR = "cosmonautics-26.08.307.jar"
COSMONAUTICS_SHA256 = "3FD9DAC868400905A55164D2C9D74ABC2080AE3269CA51E54E1899874945973E"
AD_ASTRA_JAR = "adastra-1.21.1-1.16.22-neoforge.jar"
AD_ASTRA_SHA256 = "FAF21D02C71D2D5B5A671A746334ED18A9DDBA79A5A9D9BD95E93A1D9EE9EC86"
PINNED_CLASSES = {
    "dev/devce/rocketnautics/content/physics/AsteroidSpawner.class":
        "F2044F4B058E1FF3FE8DAA994CEB205F59A089D8D03DC227EFCBFFC1B1F2E075",
    "dev/devce/rocketnautics/api/orbit/DeepSpaceHelper.class":
        "326F89DFA57EF425E24E0B701A0B5061FB95FA37518F1557E7B1B0AED1C9BC5B",
}
COSMONAUTICS_ENTRIES = {
    *PINNED_CLASSES,
    "data/rocketnautics/dimension/deep_space.json",
    "assets/rocketnautics/models/item/titanium_ore.json",
    "data/rocketnautics/loot_table/blocks/titanium_ore.json",
    "data/rocketnautics/recipe/crushing/titanium_ore.json",
    "data/rocketnautics/recipe/splashing/crushed_raw_titanium.json",
}
AD_ASTRA_ENTRIES = {
    "data/ad_astra/dimension/mercury.json",
    "data/ad_astra/dimension/mercury_orbit.json",
    "assets/ad_astra/models/item/mercury_iron_ore.json",
    "data/ad_astra/loot_table/blocks/mercury_iron_ore.json",
    "data/create/recipe/crushing/mercury_iron_ore.json",
}
CANDIDATE_ENTRIES = {
    "dev/godpc/industrialcolonies/IndustrialBlocks.class",
    "dev/godpc/industrialcolonies/IndustrialItems.class",
    "dev/godpc/industrialcolonies/IndustrialBlockEntities.class",
    "dev/godpc/industrialcolonies/space/SpaceflightAuthorization.class",
    "dev/godpc/industrialcolonies/space/MercuryNavigationComputerBlock.class",
    "dev/godpc/industrialcolonies/space/MercuryNavigationComputerBlockEntity.class",
    "dev/godpc/industrialcolonies/mixin/AsteroidSpawnerMixin.class",
    "industrial_colonies.mixins.json",
    "data/rocketnautics/universe_planets/mercury.json",
    "data/industrial_colonies/dimension_physics/ad_astra_mercury.json",
    "data/industrial_colonies/advancement/planetary/mercury_arrival.json",
    "assets/industrial_colonies/blockstates/mercury_navigation_computer.json",
    "assets/industrial_colonies/models/block/mercury_navigation_computer.json",
    "assets/industrial_colonies/models/item/mercury_navigation_computer.json",
    "data/industrial_colonies/loot_table/blocks/mercury_navigation_computer.json",
}
REQUIRED_FILES = (
    SEED, MANIFEST, COMPILED, ASSIGNMENTS, QUESTS, NATIVE_CHAPTER,
    ITEMS_JAVA, BLOCKS_JAVA, BLOCK_ENTITIES_JAVA, AUTHORIZATION_JAVA,
    ASTEROID_MIXIN, MIXINS_JSON, LANG, SPACE_BOUNDARY, MERCURY_PLANET,
    MERCURY_PHYSICS, MERCURY_ADVANCEMENT, MERCURY_BLOCK,
    MERCURY_BLOCK_ENTITY, MERCURY_BLOCKSTATE, MERCURY_BLOCK_MODEL,
    MERCURY_ITEM_MODEL, MERCURY_BLOCK_LOOT,
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def rows(payload: Mapping[str, Any], recipe_id: str) -> list[dict[str, Any]]:
    return [
        row for row in payload.get("recipes", [])
        if isinstance(row, dict) and row.get("id") == recipe_id
    ]


def task_signature(task: Mapping[str, Any]) -> tuple[str, str, int]:
    kind = str(task.get("type", ""))
    target = task.get("item") if kind == "item" else task.get("advancement")
    return kind, str(target or ""), int(task.get("count", 1))


def walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate_recipe(project: Path, manifest: Path, compiled: Path, failures: list[str]) -> None:
    seed = load_json(project / SEED)
    if seed.get("phase_by_node", {}).get(NODE) != PHASE:
        failures.append("Mercury Expedition is not assigned to Planetary Industry")
    scoped = [
        row for row in seed.get("recipes", [])
        if str(row.get("id", "")).startswith("industrial_colonies:planetary/mercury/")
    ]
    if [row.get("id") for row in scoped] != [RECIPE_ID]:
        failures.append("Mercury managed recipe set is not exactly the one approved route")
        return
    recipe = scoped[0]
    for field, value in EXPECTED_RECIPE.items():
        if recipe.get(field) != value:
            failures.append(f"Mercury navigation recipe {field} drifted")
    if not str(recipe.get("comment", "")).strip():
        failures.append("Mercury navigation recipe lacks a manufacturing rationale")
    if len(recipe.get("pattern", [])) != 5 or any(len(row) != 5 for row in recipe.get("pattern", [])):
        failures.append("Mercury navigation recipe is not an exact 5x5 construction route")
    if any(" " in row for row in recipe.get("pattern", [])):
        failures.append("Mercury navigation recipe no longer occupies all 25 grid cells")
    if "remove" in recipe or any(key.startswith("remove_") for key in recipe):
        failures.append("Mercury navigation recipe introduced an unrelated removal")

    values = set(recipe.get("key", {}).values())
    ancestry = {
        "ad_astra:calorite_plate", "ad_astra:calorite_block",
        "industrial_colonies:venus_navigation_computer",
        "rocketnautics:sputnik", "simulated:navigation_table",
        "mekanism:ultimate_control_circuit", "ae2:engineering_processor",
        "tfmg:etched_circuit_board", "computercraft:computer_advanced",
    }
    if not ancestry.issubset(values):
        failures.append("Mercury navigation recipe lost Calorite, navigation, or factory ancestry")

    manifest_payload = load_json(manifest)
    found = rows(manifest_payload, RECIPE_ID)
    if len(found) != 1:
        failures.append("assembled manifest must contain exactly one Mercury navigation route")
    else:
        assembled = found[0]
        for field, value in EXPECTED_RECIPE.items():
            if field == "depends_on":
                if not set(value).issubset(set(assembled.get(field, []))):
                    failures.append("assembled Mercury route lost reviewed dependency ancestry")
            elif assembled.get(field) != value:
                failures.append(f"assembled Mercury navigation route {field} drifted")
        if assembled.get("remove") != []:
            failures.append("assembled Mercury navigation route introduced a removal")

    compiled_payload = load_json(compiled)
    cards = [row for row in compiled_payload.get("recipes", []) if row.get("recipeId") == RECIPE_ID]
    if len(cards) != 1:
        failures.append("compiled KJSGen project must contain exactly one Mercury navigation card")
    else:
        card = cards[0]
        if card.get("type") != "kjsgen:create_mechanical_crafting":
            failures.append("compiled Mercury navigation card is not Mechanical Crafting")
        if card.get("params") != {"gridW": "5", "gridH": "5"}:
            failures.append("compiled Mercury navigation card is not a 5x5 grid")
        if card.get("slots", {}).get("output") != {"kind": "ITEM", "id": OUTPUT}:
            failures.append("compiled Mercury navigation output drifted")
        expected_inputs = Counter(KEY[symbol] for row in PATTERN for symbol in row)
        actual_inputs = Counter(
            slot.get("id") for name, slot in card.get("slots", {}).items()
            if name.startswith("cell_") and isinstance(slot, dict)
        )
        if actual_inputs != expected_inputs:
            failures.append("compiled Mercury navigation ingredient grid drifted")
    if any(row.get("recipeId") == RECIPE_ID for row in compiled_payload.get("removals", [])):
        failures.append("compiled project removes its own Mercury navigation recipe")


def validate_assets(project: Path, failures: list[str]) -> None:
    for path in (ITEMS_JAVA, BLOCKS_JAVA, BLOCK_ENTITIES_JAVA):
        source = (project / path).read_text(encoding="utf-8-sig")
        if source.count('"mercury_navigation_computer"') != 1:
            failures.append(f"Mercury Navigation Computer registration drifted: {path.name}")
    block = (project / MERCURY_BLOCK).read_text(encoding="utf-8-sig")
    entity = (project / MERCURY_BLOCK_ENTITY).read_text(encoding="utf-8-sig")
    if "MercuryNavigationComputerBlockEntity" not in block:
        failures.append("Mercury block no longer creates its marker block entity")
    if "implements BlockEntitySubLevelActor" not in entity:
        failures.append("Mercury block entity no longer participates in Sable ship actors")
    lang = load_json(project / LANG)
    if lang.get("block.industrial_colonies.mercury_navigation_computer") != "Mercury Navigation Computer":
        failures.append("Mercury Navigation Computer language entry drifted")
    expected_json = {
        MERCURY_BLOCKSTATE: {"variants": {"": {"model": "industrial_colonies:block/mercury_navigation_computer"}}},
        MERCURY_ITEM_MODEL: {"parent": "industrial_colonies:block/mercury_navigation_computer"},
    }
    for path, expected in expected_json.items():
        if load_json(project / path) != expected:
            failures.append(f"Mercury Navigation Computer asset drifted: {path.name}")
    loot_text = (project / MERCURY_BLOCK_LOOT).read_text(encoding="utf-8-sig")
    if loot_text.count(OUTPUT) != 1:
        failures.append("Mercury Navigation Computer does not self-drop exactly once")


def validate_destination(project: Path, failures: list[str]) -> None:
    planet = load_json(project / MERCURY_PLANET)
    for key, expected in {
        "parent": "sol", "name": "mercury", "acceleration_at_surface": 3.7,
        "priority": 2000, "radius": 1219850.0,
    }.items():
        if planet.get(key) != expected:
            failures.append(f"Rocketnautics Mercury {key} drifted")
    dimension = planet.get("dimension_data", {})
    if dimension.get("linked_dimension") != "ad_astra:mercury":
        failures.append("Rocketnautics Mercury no longer links only to the canonical surface")
    if "mercury_orbit" in json.dumps(planet):
        failures.append("Rocketnautics Mercury must not link Ad Astra's prefab orbit dimension")
    for key, expected in {
        "allowed_transfer": "all",
        "apply_gravity_correction_to_entities_in_dimension": False,
        "render_universe_in_dimension": False,
    }.items():
        if dimension.get(key) != expected:
            failures.append(f"Rocketnautics Mercury dimension_data.{key} drifted")
    physics = load_json(project / MERCURY_PHYSICS)
    if physics != {
        "dimension": "ad_astra:mercury", "priority": 2000,
        "universal_drag": 0.0, "base_gravity": [0.0, -3.7, 0.0],
        "base_pressure": 0.0, "magnetic_north": [0.0, 0.0, 0.0],
    }:
        failures.append("Sable Mercury ship-physics ownership drifted")
    advancement = load_json(project / MERCURY_ADVANCEMENT)
    criterion = next(iter(advancement.get("criteria", {}).values()), None)
    if len(advancement.get("criteria", {})) != 1 or criterion != {
        "trigger": "minecraft:changed_dimension", "conditions": {"to": "ad_astra:mercury"}
    }:
        failures.append("Mercury arrival advancement drifted")
    if "rewards" in advancement or "display" in advancement or advancement.get("sends_telemetry_event") is not False:
        failures.append("Mercury arrival advancement is no longer observation-only")


def validate_runtime(project: Path, failures: list[str]) -> None:
    source = (project / AUTHORIZATION_JAVA).read_text(encoding="utf-8-sig")
    required = (
        'ResourceLocation.fromNamespaceAndPath("ad_astra", "mercury")',
        "boolean boundForMercury = MERCURY.equals(destinationKey)",
        "if (!boundForMars && !boundForVenus && !boundForMercury)",
        "if (boundForMercury)",
        "hasRequiredComputer = hasMercuryNavigationComputer(ship)",
        "hasVenusNavigationComputer(ship)\n                        || hasMercuryNavigationComputer(ship)",
        "hasMarsNavigationComputer(ship)\n                        || hasVenusNavigationComputer(ship)\n                        || hasMercuryNavigationComputer(ship)",
        "boundForVenus && !hasFullHeatResistantSuit(player)",
        "!deepSpace.getOfflinePlayers().isEmpty()",
        "!deepSpace.getUnloadedSublevels().isEmpty()",
        "players.isEmpty()", "ships.isEmpty()",
        "Sable.HELPER.getTrackingOrVehicleSubLevel(player)",
        "if (!(associated instanceof ServerSubLevel ship)",
        "ship.isRemoved()", "!ships.contains(ship)",
    )
    for token in required:
        if token not in source:
            failures.append(f"Mercury descent gate lost fail-closed token: {token}")
    if "mercury_orbit" in source:
        failures.append("Mercury descent authorization incorrectly owns the prefab orbit")
    if ".boundingBox()" in source or ".inflate(" in source:
        failures.append("Mercury descent gate reintroduced proximity-based player association")

    mixin = (project / ASTEROID_MIXIN).read_text(encoding="utf-8-sig")
    for token in (
        "@Mixin(value = AsteroidSpawner.class, remap = false)",
        "@ModifyVariable(",
        'method = "onPlayerTick(Lnet/neoforged/neoforge/event/tick/PlayerTickEvent$Post;)V"',
        'at = @At("STORE")', "ordinal = 0", "require = 1",
        "DeepSpaceHelper.isDeepSpace(player.level())", "return false",
    ):
        if token not in mixin:
            failures.append(f"asteroid deep-space fix lost fail-closed token: {token}")
    if "getY(" in mixin or '"space"' in mixin or "spawnAsteroid(" in mixin:
        failures.append("asteroid fix reintroduced height/path heuristics or direct spawning")
    mixins = load_json(project / MIXINS_JSON).get("mixins", [])
    if mixins.count("AsteroidSpawnerMixin") != 1:
        failures.append("AsteroidSpawnerMixin registration drifted")
    all_java = "\n".join(
        path.read_text(encoding="utf-8-sig", errors="replace")
        for path in (project / "src/main/java").rglob("*.java")
    )
    if "AsteroidCommand" in all_java or "spawnAsteroid(" in all_java:
        failures.append("Stage 12 invented an asteroid command, locator, claim, or direct spawner")

    boundary = (project / SPACE_BOUNDARY).read_text(encoding="utf-8-sig")
    if boundary.count(f"'{TITANIUM_WASHING}'") != 1:
        failures.append("titanium washing-to-Netherite shortcut removal drifted")
    if not re.search(r"event\.remove\(\{\s*id:\s*id\s*\}\)", boundary):
        failures.append("space boundary no longer removes its reviewed exact IDs")
    if re.search(r"event\.remove\(\{\s*(output|mod|type|input)\s*:", boundary):
        failures.append("space boundary contains a broad removal")


def validate_assignments(project: Path, failures: list[str]) -> None:
    node = load_json(project / ASSIGNMENTS).get("nodes", {}).get(NODE, {})
    if node.get("unlocks") != [OUTPUT] or node.get("icon") != OUTPUT:
        failures.append("Mercury Expedition unlock assignment drifted")
    if not str(node.get("role", "")).strip():
        failures.append("Mercury Expedition role is blank")


def validate_quests(project: Path, failures: list[str]) -> None:
    chapter = load_json(project / QUESTS).get("chapter", {})
    quests = chapter.get("quests", [])
    keys = [row.get("key") for row in quests]
    if len(keys) != 29 or keys[14:18] != list(QUESTS_EXPECTED):
        failures.append("Planetary Industry must retain the four Mercury/asteroid quests before outer-station extraction")
    forbidden = {"rewards", "stage", "stages", "command", "commands", "recipe", "recipes", "consume_items"}
    by_key = {row.get("key"): row for row in quests}
    for key, (dependencies, tasks) in QUESTS_EXPECTED.items():
        quest = by_key.get(key, {})
        if quest.get("dependencies") != dependencies:
            failures.append(f"Mercury/asteroid quest dependency drifted: {key}")
        if [task_signature(task) for task in quest.get("tasks", [])] != tasks:
            failures.append(f"Mercury/asteroid quest task drifted: {key}")
        if forbidden.intersection(quest):
            failures.append(f"Mercury/asteroid quest contains a gate or reward: {key}")
        text = json.dumps(quest.get("description", []), ensure_ascii=False).lower()
        if "consume nothing" not in text and "consumes nothing" not in text:
            failures.append(f"Mercury/asteroid quest lost non-consuming guidance: {key}")
    native = load_json(project / NATIVE_CHAPTER)
    if len(native.get("quests", [])) != 29:
        failures.append("generated Planetary Industry chapter is not the expected 29 quests")
    native_text = json.dumps(native, ensure_ascii=False)
    for token in (
        "industrial_colonies:planetary/mercury_arrival",
        "ad_astra:mercury_iron_ore", "rocketnautics:titanium_ore",
    ):
        if token not in native_text:
            failures.append(f"generated Planetary Industry chapter lost {token}")


def find_single_jar(mods: Path, name: str, failures: list[str]) -> Path | None:
    matches = list(mods.glob(name))
    if len(matches) != 1:
        failures.append(f"expected one installed {name}, found {len(matches)}")
        return None
    return matches[0]


def validate_installed(mods: Path, failures: list[str]) -> None:
    cosmo = find_single_jar(mods, COSMONAUTICS_JAR, failures)
    ad_astra = find_single_jar(mods, AD_ASTRA_JAR, failures)
    for jar, expected_hash, required in (
        (cosmo, COSMONAUTICS_SHA256, COSMONAUTICS_ENTRIES),
        (ad_astra, AD_ASTRA_SHA256, AD_ASTRA_ENTRIES),
    ):
        if jar is None:
            continue
        if sha256(jar.read_bytes()) != expected_hash:
            failures.append(f"installed dependency hash drifted: {jar.name}")
        try:
            with zipfile.ZipFile(jar) as archive:
                names = set(archive.namelist())
                missing = sorted(required - names)
                if missing:
                    failures.append(f"{jar.name} lacks required Mercury/asteroid entries: {missing}")
                if jar.name == COSMONAUTICS_JAR:
                    for entry, expected in PINNED_CLASSES.items():
                        if entry in names and sha256(archive.read(entry)) != expected:
                            failures.append(f"installed Cosmonautics class drifted: {entry}")
                    asteroid = archive.read("dev/devce/rocketnautics/content/physics/AsteroidSpawner.class")
                    helper = archive.read("dev/devce/rocketnautics/api/orbit/DeepSpaceHelper.class")
                    for token in (b"space",):
                        if token not in asteroid:
                            failures.append(f"installed AsteroidSpawner bytecode lost audited token {token!r}")
                    for token in (b"isDeepSpace",):
                        if token not in helper:
                            failures.append(f"installed DeepSpaceHelper bytecode lost API token {token!r}")
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            failures.append(f"cannot inspect installed dependency {jar}: {exc}")

    owners: list[str] = []
    for jar in sorted(mods.glob("*.jar")):
        try:
            with zipfile.ZipFile(jar) as archive:
                for name in archive.namelist():
                    if "/universe_planets/" not in name or not name.endswith(".json"):
                        continue
                    try:
                        payload = json.loads(archive.read(name).decode("utf-8-sig"))
                    except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
                        continue
                    if payload.get("dimension_data", {}).get("linked_dimension") == "ad_astra:mercury":
                        owners.append(f"{jar.name}!/{name}")
        except (OSError, zipfile.BadZipFile):
            continue
    if owners:
        failures.append(f"installed JARs already own the canonical Mercury link: {owners}")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    csv_path = catalog / "recipes.csv" if catalog.is_dir() else catalog
    if not csv_path.is_file():
        failures.append(f"missing installed recipe catalog: {csv_path}")
        return
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        by_id = {row.get("recipe_id", ""): row for row in csv.DictReader(handle)}
    required = {
        "create:crushing/mercury_iron_ore",
        "rocketnautics:crushing/titanium_ore",
        TITANIUM_WASHING,
    }
    missing = sorted(required - set(by_id))
    if missing:
        failures.append(f"installed catalog lacks Mercury/asteroid recipes: {missing}")
    washing = by_id.get(TITANIUM_WASHING, {})
    if "minecraft:netherite_scrap" not in str(washing.get("outputs", "")):
        failures.append("installed titanium washing recipe no longer contains the audited Netherite shortcut")


def validate_candidate(candidate: Path, failures: list[str]) -> None:
    if not candidate.is_file():
        failures.append(f"candidate JAR is missing: {candidate}")
        return
    try:
        with zipfile.ZipFile(candidate) as archive:
            names = set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect candidate JAR {candidate}: {exc}")
        return
    missing = sorted(CANDIDATE_ENTRIES - names)
    if missing:
        failures.append(f"candidate JAR lacks Mercury/asteroid implementation entries: {missing}")


def validate(
    project: Path,
    *,
    manifest: Path | None = None,
    compiled: Path | None = None,
    catalog: Path | None = None,
    mods: Path | None = None,
    candidate_jar: Path | None = None,
) -> list[str]:
    project = project.resolve()
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        if not (project / relative).is_file():
            failures.append(f"missing Stage 12 source artifact: {relative.as_posix()}")
    if failures:
        return failures
    manifest_path = manifest.resolve() if manifest else project / MANIFEST
    compiled_path = compiled.resolve() if compiled else project / COMPILED
    validate_recipe(project, manifest_path, compiled_path, failures)
    validate_assets(project, failures)
    validate_destination(project, failures)
    validate_runtime(project, failures)
    validate_assignments(project, failures)
    validate_quests(project, failures)
    if catalog is not None:
        validate_catalog(catalog.resolve(), failures)
    if mods is not None:
        validate_installed(mods.resolve(), failures)
    if candidate_jar is not None:
        validate_candidate(candidate_jar.resolve(), failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--mods", type=Path)
    parser.add_argument("--jar", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate(
        args.project,
        manifest=args.manifest,
        compiled=args.compiled,
        catalog=args.catalog,
        mods=args.mods,
        candidate_jar=args.jar,
    )
    if failures:
        print("FAIL: Mercury Expedition and Asteroid Freight slice is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "PASS: one 5x5 Mercury computer, one canonical surface bridge, "
        "fail-closed physical descent, exact deep-space asteroid eligibility, "
        "the titanium-washing retirement, and four observation-only quests are intact."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
