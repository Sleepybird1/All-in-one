#!/usr/bin/env python3
"""Fail closed on Venus authorization, heat protection, and Calorite metallurgy."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import zipfile
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
MIXIN_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/mixin/DeepSpaceInstanceMixin.java")
MIXINS_JSON = Path("src/main/resources/industrial_colonies.mixins.json")
LANG = Path("src/main/resources/assets/industrial_colonies/lang/en_us.json")
MODEL_DIR = Path("src/main/resources/assets/industrial_colonies/models/item")
FEED_TAG = Path("src/main/resources/data/industrial_colonies/tags/item/calorite_crushing_feed.json")
VENUS_PLANET = Path("src/main/resources/data/rocketnautics/universe_planets/venus.json")
VENUS_PHYSICS = Path("src/main/resources/data/industrial_colonies/dimension_physics/ad_astra_venus.json")
VENUS_ADVANCEMENT = Path("src/main/resources/data/industrial_colonies/advancement/planetary/venus_arrival.json")
VENUS_BLOCK = Path("src/main/java/dev/godpc/industrialcolonies/space/VenusNavigationComputerBlock.java")
VENUS_BLOCK_ENTITY = Path("src/main/java/dev/godpc/industrialcolonies/space/VenusNavigationComputerBlockEntity.java")
VENUS_BLOCKSTATE = Path("src/main/resources/assets/industrial_colonies/blockstates/venus_navigation_computer.json")
VENUS_BLOCK_MODEL = Path("src/main/resources/assets/industrial_colonies/models/block/venus_navigation_computer.json")
VENUS_ITEM_MODEL = Path("src/main/resources/assets/industrial_colonies/models/item/venus_navigation_computer.json")
VENUS_BLOCK_LOOT = Path("src/main/resources/data/industrial_colonies/loot_table/blocks/venus_navigation_computer.json")

PHASE = "Planetary Industry"
EXPEDITION_NODE = "CR02 — Venus Expedition"
METALLURGY_NODE = "CR02 — Calorite Metallurgy"
PRESS = "createcasing:refined_radiance_press"

VENUS_NAV = "industrial_colonies:planetary/venus/navigation_computer"
HELMET = "industrial_colonies:planetary/venus/netherite_space_helmet"
SUIT = "industrial_colonies:planetary/venus/netherite_space_suit"
PANTS = "industrial_colonies:planetary/venus/netherite_space_pants"
BOOTS = "industrial_colonies:planetary/venus/netherite_space_boots"
FEED = "industrial_colonies:planetary/calorite/feed_to_grit"
ENRICH = "industrial_colonies:planetary/calorite/grit_to_concentrate"
LEACH = "industrial_colonies:planetary/calorite/concentrate_leaching"
REDUCE = "industrial_colonies:planetary/calorite/leached_compound_reduction"
PLATE = "industrial_colonies:planetary/calorite/plate"

NAV_PATTERN = ["PSWSP", "PEBEP", "GNCNG", "PLZLP", "PIMIP"]
NAV_KEY = {
    "P": "ad_astra:ostrum_plate", "S": "ad_astra:solar_panel",
    "W": "ad_astra:water_pump", "E": "ae2:engineering_processor",
    "B": "tfmg:etched_circuit_board", "G": "ad_astra:gravity_normalizer",
    "N": "simulated:navigation_table", "C": "industrial_colonies:mars_navigation_computer",
    "L": "mekanism:nutritional_liquifier", "Z": "ad_astra:energizer",
    "I": "ad_astra:ostrum_ingot", "M": "computercraft:computer_advanced",
}
OUTPOST_RECIPES = [
    "industrial_colonies:planetary/outpost/solar_panel",
    "industrial_colonies:planetary/outpost/water_pump",
    "industrial_colonies:planetary/outpost/gravity_normalizer",
    "industrial_colonies:planetary/outpost/energizer",
    "industrial_colonies:planetary/outpost/nutritional_liquifier",
]
SUIT_RECIPES = {
    HELMET: ("ad_astra:netherite_space_helmet", "ad_astra:netherite_space_helmet"),
    SUIT: ("ad_astra:netherite_space_suit", "ad_astra:netherite_space_suit"),
    PANTS: ("ad_astra:netherite_space_pants", "ad_astra:netherite_space_pants"),
    BOOTS: ("ad_astra:netherite_space_boots", "ad_astra:netherite_space_boots"),
}
SMELT_REMOVALS = {
    f"ad_astra:{process}/calorite_ingot_from_{process}_{source}"
    for process in ("smelting", "blasting")
    for source in ("deepslate_calorite_ore", "venus_calorite_ore", "raw_calorite")
}
PLATE_REMOVALS = {
    "ad_astra:compressing/calorite_plate_from_compressing_calorite_blocks",
    "ad_astra:compressing/calorite_plate_from_compressing_calorite_ingots",
    "create:pressing/calorite_ingot",
    "immersiveengineering:crafting/plate_calorite_hammering",
    "immersiveengineering:metalpress/plate_calorite",
    "modern_industrialization:compressor/calorite_ingot_to_plate",
    "thermal:machines/press/press_calorite_ingot_to_plate",
}
CRUSH_REMOVALS = {
    "create:crushing/venus_calorite_ore",
    "create:crushing/deepslate_calorite_ore",
    "modern_industrialization:macerator/calorite_ore",
}
EXACT_REMOVALS = {*CRUSH_REMOVALS, *SMELT_REMOVALS, *PLATE_REMOVALS, *(value[1] for value in SUIT_RECIPES.values())}
PACKING_RECIPES = {
    "ad_astra:calorite_block", "ad_astra:calorite_ingot",
    "ad_astra:calorite_ingot_from_calorite_block", "ad_astra:calorite_nugget",
    "ad_astra:raw_calorite", "ad_astra:raw_calorite_block",
}

RECIPES: dict[str, dict[str, Any]] = {
    VENUS_NAV: {
        "node": EXPEDITION_NODE, "phase": PHASE, "order": 210,
        "type": "mechanical_crafting", "pattern": NAV_PATTERN, "key": NAV_KEY,
        "output": "industrial_colonies:venus_navigation_computer",
        "depends_on": OUTPOST_RECIPES,
    },
    HELMET: {"node": EXPEDITION_NODE, "phase": PHASE, "order": 220, "type": "mechanical_crafting", "output": "ad_astra:netherite_space_helmet", "remove": ["ad_astra:netherite_space_helmet"], "exclusive_output": True},
    SUIT: {"node": EXPEDITION_NODE, "phase": PHASE, "order": 230, "type": "mechanical_crafting", "output": "ad_astra:netherite_space_suit", "remove": ["ad_astra:netherite_space_suit"], "exclusive_output": True},
    PANTS: {"node": EXPEDITION_NODE, "phase": PHASE, "order": 240, "type": "mechanical_crafting", "output": "ad_astra:netherite_space_pants", "remove": ["ad_astra:netherite_space_pants"], "exclusive_output": True},
    BOOTS: {"node": EXPEDITION_NODE, "phase": PHASE, "order": 250, "type": "mechanical_crafting", "output": "ad_astra:netherite_space_boots", "remove": ["ad_astra:netherite_space_boots"], "exclusive_output": True},
    FEED: {
        "node": METALLURGY_NODE, "phase": PHASE, "order": 260, "type": "crushing",
        "input": "#industrial_colonies:calorite_crushing_feed",
        "outputs": [{"kind": "ITEM", "id": "industrial_colonies:calorite_grit", "count": 1}],
        "processing_time": 420, "remove": [
            "create:crushing/venus_calorite_ore",
            "create:crushing/deepslate_calorite_ore",
            "modern_industrialization:macerator/calorite_ore",
        ],
        "depends_on": [HELMET, SUIT, PANTS, BOOTS],
    },
    ENRICH: {"node": METALLURGY_NODE, "phase": PHASE, "order": 270, "type": "mekanism_enriching", "input": "industrial_colonies:calorite_grit", "output": "industrial_colonies:calorite_concentrate", "depends_on": [FEED]},
    LEACH: {
        "node": METALLURGY_NODE, "phase": PHASE, "order": 280, "type": "tfmg_vat",
        "ingredients": ["4x industrial_colonies:calorite_concentrate", {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 1000}, {"kind": "FLUID", "id": "minecraft:water", "amount": 1500}],
        "results": [{"kind": "ITEM", "id": "industrial_colonies:calorite_leached_compound", "count": 2}],
        "vat_mode": "firebrick", "machine_mode": "mixing", "heat": "heated", "min_size": 7, "processing_time": 600, "depends_on": [ENRICH],
    },
    REDUCE: {
        "node": METALLURGY_NODE, "phase": PHASE, "order": 290, "type": "tfmg_vat",
        "ingredients": ["industrial_colonies:calorite_leached_compound"],
        "results": [{"kind": "ITEM", "id": "ad_astra:calorite_ingot"}],
        "vat_mode": "firebrick", "machine_mode": "two_electrodes", "heat": "superheated", "min_size": 7, "processing_time": 900,
        "remove": [
            "ad_astra:smelting/calorite_ingot_from_smelting_deepslate_calorite_ore",
            "ad_astra:smelting/calorite_ingot_from_smelting_venus_calorite_ore",
            "ad_astra:smelting/calorite_ingot_from_smelting_raw_calorite",
            "ad_astra:blasting/calorite_ingot_from_blasting_deepslate_calorite_ore",
            "ad_astra:blasting/calorite_ingot_from_blasting_venus_calorite_ore",
            "ad_astra:blasting/calorite_ingot_from_blasting_raw_calorite",
        ], "depends_on": [LEACH],
    },
    PLATE: {
        "node": METALLURGY_NODE, "phase": PHASE, "order": 300, "type": "pressing",
        "machine": PRESS, "input": "ad_astra:calorite_ingot", "output": "ad_astra:calorite_plate",
        "remove": [
            "ad_astra:compressing/calorite_plate_from_compressing_calorite_blocks",
            "ad_astra:compressing/calorite_plate_from_compressing_calorite_ingots",
            "create:pressing/calorite_ingot", "immersiveengineering:crafting/plate_calorite_hammering",
            "immersiveengineering:metalpress/plate_calorite",
            "modern_industrialization:compressor/calorite_ingot_to_plate",
            "thermal:machines/press/press_calorite_ingot_to_plate",
        ],
        "exclusive_output": True, "depends_on": [REDUCE],
    },
}

QUESTS_EXPECTED = {
    "venus_expedition_package": (["closed_loop_rations"], [
        ("item", "industrial_colonies:venus_navigation_computer", 1),
        ("item", "ad_astra:netherite_space_helmet", 1),
        ("item", "ad_astra:netherite_space_suit", 1),
        ("item", "ad_astra:netherite_space_pants", 1),
        ("item", "ad_astra:netherite_space_boots", 1),
    ]),
    "venus_arrival": (["venus_expedition_package"], [("advancement", "industrial_colonies:planetary/venus_arrival", 1)]),
    "calorite_freight": (["venus_arrival"], [("item", "ad_astra:raw_calorite", 64)]),
    "calorite_metallurgy": (["calorite_freight"], [("item", item, 1) for item in (
        "industrial_colonies:calorite_grit", "industrial_colonies:calorite_concentrate",
        "industrial_colonies:calorite_leached_compound", "ad_astra:calorite_ingot", "ad_astra:calorite_plate")]),
}

COSMONAUTICS_JAR_SHA256 = "3FD9DAC868400905A55164D2C9D74ABC2080AE3269CA51E54E1899874945973E"
SABLE_JAR_SHA256 = "DA6C3B66238586603D1DCAA2AFB012D36815FBCE0A2D5938FBB2936701D42279"
AD_ASTRA_JAR_SHA256 = "FAF21D02C71D2D5B5A671A746334ED18A9DDBA79A5A9D9BD95E93A1D9EE9EC86"
PINNED_CLASSES = {
    "cosmonautics-26.08.307.jar": {
        "dev/devce/rocketnautics/content/orbit/universe/UniverseLoader.class": "A7F8D64BE198E7789D75CEEA4C541281F9C7DD379B6E5A51BA23A5E3A0F1E89D",
        "dev/devce/rocketnautics/content/orbit/universe/builder/PlanetDefinitionBuilder.class": "5C27377B31820DC42B5814643CCE0AB58906F6DDF43CC887897C75882CBA4C4E",
        "dev/devce/rocketnautics/content/orbit/universe/builder/SerializableDimensionData.class": "BF7275F3B9893F27338FB0E509469B0FECF4DEE99A66B5A52F0C141A9DF94EDB",
    },
    "sable-neoforge-1.21.1-2.0.3.jar": {
        "dev/ryanhcode/sable/physics/config/dimension_physics/DimensionPhysics.class": "51002CD0E89134DD71D6440912ED1492D56DFBBF6F06C008287ABF1B7E757075",
        "dev/ryanhcode/sable/physics/config/dimension_physics/DimensionPhysicsData$ReloadListener.class": "173D050F7C5969E2B3210A4A72C40C198EF556B97E8D7028B4BBE566728BE2E9",
    },
}
REQUIRED_FILES = (
    SEED, ASSIGNMENTS, QUESTS, NATIVE_CHAPTER, ITEMS_JAVA, BLOCKS_JAVA,
    BLOCK_ENTITIES_JAVA, AUTHORIZATION_JAVA, MIXIN_JAVA, MIXINS_JSON, LANG,
    FEED_TAG, VENUS_PLANET, VENUS_PHYSICS, VENUS_ADVANCEMENT, VENUS_BLOCK,
    VENUS_BLOCK_ENTITY, VENUS_BLOCKSTATE, VENUS_BLOCK_MODEL, VENUS_ITEM_MODEL,
    VENUS_BLOCK_LOOT,
    *(MODEL_DIR / f"{name}.json" for name in ("calorite_grit", "calorite_concentrate", "calorite_leached_compound")),
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def rows(payload: Mapping[str, Any], recipe_id: str) -> list[dict[str, Any]]:
    return [row for row in payload.get("recipes", []) if isinstance(row, dict) and row.get("id") == recipe_id]


def task_signature(task: Mapping[str, Any]) -> tuple[str, str, int]:
    task_type = str(task.get("type", ""))
    target = task.get("item") if task_type == "item" else task.get("advancement")
    return task_type, str(target or ""), int(task.get("count", 1))


def validate_recipe_source(project: Path, failures: list[str]) -> None:
    seed = load_json(project / SEED)
    for node in (EXPEDITION_NODE, METALLURGY_NODE):
        if seed.get("phase_by_node", {}).get(node) != PHASE:
            failures.append(f"{node} is not assigned to Planetary Industry")
    scoped = {
        row.get("id")
        for row in seed.get("recipes", [])
        if str(row.get("id", "")).startswith(("industrial_colonies:planetary/venus/", "industrial_colonies:planetary/calorite/"))
    }
    if scoped != set(RECIPES):
        failures.append("Venus/Calorite managed recipe set is not exactly the ten approved routes")

    all_removals: list[str] = []
    for recipe_id, expected in RECIPES.items():
        found = rows(seed, recipe_id)
        if len(found) != 1:
            failures.append(f"managed seed must contain exactly one {recipe_id}")
            continue
        recipe = found[0]
        for field, value in expected.items():
            if field == "depends_on" and recipe_id in SUIT_RECIPES:
                continue
            if recipe.get(field) != value:
                failures.append(f"{recipe_id} {field} drifted")
        if not str(recipe.get("comment", "")).strip():
            failures.append(f"{recipe_id} lacks a manufacturing rationale")
        if {"remove_by_output", "removeByOutput", "remove_by_mod", "removeByMod", "remove_by_input", "removeByInput"}.intersection(recipe):
            failures.append(f"{recipe_id} contains a broad removal directive")
        if recipe.get("type") == "mechanical_crafting":
            pattern = recipe.get("pattern", [])
            if len(pattern) != 5 or any(len(row) != 5 for row in pattern):
                failures.append(f"{recipe_id} is not an exact 5x5 construction route")
        all_removals.extend(recipe.get("remove", []))
    if len(all_removals) != 20 or len(set(all_removals)) != 20 or set(all_removals) != EXACT_REMOVALS:
        failures.append("Venus/Calorite shortcut retirement is not the exact 20-ID audited set")
    if PACKING_RECIPES.intersection(all_removals + seed.get("additional_removals", [])):
        failures.append("Calorite nugget/ingot/block/raw packing preservation drifted")
    for recipe_id in SUIT_RECIPES:
        recipe = rows(seed, recipe_id)
        if not recipe:
            continue
        values = set(recipe[0].get("key", {}).values())
        if not {"ad_astra:desh_plate", "ad_astra:ostrum_plate"}.issubset(values):
            failures.append(f"{recipe_id} no longer contains both Desh and Ostrum infrastructure")
        if not any(value.startswith("ad_astra:") and value in {
            "ad_astra:vent", "ad_astra:oxygen_sensor", "ad_astra:large_gas_tank",
            "ad_astra:oxygen_gear", "ad_astra:oxygen_distributor", "ad_astra:gas_tank", "ad_astra:fan",
        } for value in values):
            failures.append(f"{recipe_id} no longer contains physical life-support hardware")


def validate_assets(project: Path, failures: list[str]) -> None:
    for path, token in (
        (ITEMS_JAVA, '"venus_navigation_computer"'),
        (BLOCKS_JAVA, '"venus_navigation_computer"'),
        (BLOCK_ENTITIES_JAVA, '"venus_navigation_computer"'),
    ):
        if (project / path).read_text(encoding="utf-8-sig").count(token) != 1:
            failures.append(f"Venus Navigation Computer registration drifted: {path.name}")
    items_java = (project / ITEMS_JAVA).read_text(encoding="utf-8-sig")
    for name in ("calorite_grit", "calorite_concentrate", "calorite_leached_compound"):
        if items_java.count(f'ITEMS.registerSimpleItem("{name}")') != 1:
            failures.append(f"Calorite intermediate registration drifted: {name}")
        model = load_json(project / MODEL_DIR / f"{name}.json")
        expected_texture = {
            "calorite_grit": "ad_astra:item/raw_calorite",
            "calorite_concentrate": "ad_astra:item/calorite_nugget",
            "calorite_leached_compound": "ad_astra:item/calorite_ingot",
        }[name]
        if model != {"parent": "minecraft:item/generated", "textures": {"layer0": expected_texture}}:
            failures.append(f"Calorite intermediate model drifted: {name}")
    expected_files = (
        "src/main/java/dev/godpc/industrialcolonies/space/VenusNavigationComputerBlock.java",
        "src/main/java/dev/godpc/industrialcolonies/space/VenusNavigationComputerBlockEntity.java",
        "src/main/resources/assets/industrial_colonies/blockstates/venus_navigation_computer.json",
        "src/main/resources/assets/industrial_colonies/models/block/venus_navigation_computer.json",
        "src/main/resources/assets/industrial_colonies/models/item/venus_navigation_computer.json",
        "src/main/resources/data/industrial_colonies/loot_table/blocks/venus_navigation_computer.json",
    )
    for relative in expected_files:
        if not (project / relative).is_file():
            failures.append(f"missing Venus Navigation Computer asset: {relative}")
    lang = load_json(project / LANG)
    expected_lang = {
        "block.industrial_colonies.venus_navigation_computer": "Venus Navigation Computer",
        "item.industrial_colonies.calorite_grit": "Calorite Grit",
        "item.industrial_colonies.calorite_concentrate": "Calorite Concentrate",
        "item.industrial_colonies.calorite_leached_compound": "Leached Calorite Compound",
    }
    for key, value in expected_lang.items():
        if lang.get(key) != value:
            failures.append(f"language entry drifted: {key}")
    if load_json(project / FEED_TAG) != {"replace": False, "values": ["#c:ores/calorite", "#c:raw_materials/calorite"]}:
        failures.append("Calorite crushing feed tag drifted")


def validate_destination_data(project: Path, failures: list[str]) -> None:
    planet = load_json(project / VENUS_PLANET)
    required_planet = {
        "parent": "sol", "name": "venus", "acceleration_at_surface": 8.87,
        "priority": 2000,
    }
    for key, value in required_planet.items():
        if planet.get(key) != value:
            failures.append(f"Rocketnautics Venus {key} drifted")
    dimension = planet.get("dimension_data", {})
    expected_dimension = {
        "allowed_transfer": "all", "apply_gravity_correction_to_entities_in_dimension": False,
        "atmosphere_composition": {}, "linked_dimension": "ad_astra:venus",
        "render_universe_in_dimension": False,
    }
    for key, value in expected_dimension.items():
        if dimension.get(key) != value:
            failures.append(f"Rocketnautics Venus dimension_data.{key} drifted")
    if not (2_700_000 <= float(planet.get("radius", 0)) <= 3_100_000):
        failures.append("Rocketnautics Venus radius no longer matches the installed half-scale system")
    physics = load_json(project / VENUS_PHYSICS)
    if physics != {
        "dimension": "ad_astra:venus", "priority": 2000, "universal_drag": 0.0,
        "base_gravity": [0.0, -8.87, 0.0], "base_pressure": 0.0,
        "magnetic_north": [0.0, 0.0, 0.0],
    }:
        failures.append("Sable Venus ship-physics ownership drifted")
    advancement = load_json(project / VENUS_ADVANCEMENT)
    criteria = advancement.get("criteria", {})
    if len(criteria) != 1 or next(iter(criteria.values()), None) != {
        "trigger": "minecraft:changed_dimension", "conditions": {"to": "ad_astra:venus"}
    }:
        failures.append("Venus arrival advancement drifted")
    if "rewards" in advancement or "display" in advancement or advancement.get("sends_telemetry_event") is not False:
        failures.append("Venus arrival advancement is no longer observation-only")


def validate_runtime_gate(project: Path, failures: list[str]) -> None:
    source = (project / AUTHORIZATION_JAVA).read_text(encoding="utf-8-sig")
    required = (
        'ResourceLocation.fromNamespaceAndPath("ad_astra", "mars")',
        'ResourceLocation.fromNamespaceAndPath("ad_astra", "venus")',
        'ResourceLocation.fromNamespaceAndPath("ad_astra", "heat_resistant_armor")',
        "hasRequiredComputer = hasMarsNavigationComputer(ship)",
        "|| hasVenusNavigationComputer(ship)",
        "boundForVenus && !hasFullHeatResistantSuit(player)",
        "stack.is(HEAT_RESISTANT_ARMOR)",
        "stack.canEquip(slot, player)",
        "!deepSpace.getOfflinePlayers().isEmpty()",
        "!deepSpace.getUnloadedSublevels().isEmpty()",
        "players.isEmpty()",
        "ships.isEmpty()",
        "Sable.HELPER.getTrackingOrVehicleSubLevel(player)",
        "!ships.contains(ship)",
    )
    for token in required:
        if token not in source:
            failures.append(f"managed descent gate lost fail-closed token: {token}")
    if "boundingBox()" in source or ".inflate(" in source:
        failures.append("managed descent gate reverted to proximity-based player association")
    for slot in ("EquipmentSlot.HEAD", "EquipmentSlot.CHEST", "EquipmentSlot.LEGS", "EquipmentSlot.FEET"):
        if source.count(slot) != 1:
            failures.append(f"heat-resistant armor slot contract drifted: {slot}")
    mixin = (project / MIXIN_JAVA).read_text(encoding="utf-8-sig")
    if mixin.count("AllowedTransfer;allowToDimension()Z") != 1 or mixin.count("mayDescendToManagedPlanet") != 1:
        failures.append("Cosmonautics sole descent decision injection drifted")
    if "@Inject" in mixin or "CallbackInfo" in mixin:
        failures.append("descent gate introduced unsafe tick cancellation")
    mixins = load_json(project / MIXINS_JSON)
    if mixins.get("mixins", []).count("DeepSpaceInstanceMixin") != 1:
        failures.append("DeepSpaceInstanceMixin registration drifted")


def validate_assignments(project: Path, failures: list[str]) -> None:
    nodes = load_json(project / ASSIGNMENTS).get("nodes", {})
    expected = {
        EXPEDITION_NODE: [
            "industrial_colonies:venus_navigation_computer", "ad_astra:netherite_space_helmet",
            "ad_astra:netherite_space_suit", "ad_astra:netherite_space_pants", "ad_astra:netherite_space_boots",
        ],
        METALLURGY_NODE: [
            "industrial_colonies:calorite_grit", "industrial_colonies:calorite_concentrate",
            "industrial_colonies:calorite_leached_compound", "ad_astra:calorite_ingot", "ad_astra:calorite_plate",
        ],
    }
    for node, unlocks in expected.items():
        if nodes.get(node, {}).get("unlocks") != unlocks:
            failures.append(f"{node} unlock assignment drifted")
        if not str(nodes.get(node, {}).get("role", "")).strip():
            failures.append(f"{node} role is blank")


def validate_quests(project: Path, failures: list[str]) -> None:
    chapter = load_json(project / QUESTS).get("chapter", {})
    quests = chapter.get("quests", [])
    keys = [row.get("key") for row in quests]
    if len(keys) != 29 or keys[10:14] != list(QUESTS_EXPECTED):
        failures.append(
            "Planetary Industry must retain the four Venus/Calorite quests "
            "immediately before the Mercury/asteroid continuation"
        )
    forbidden = {"rewards", "stage", "stages", "command", "commands", "recipe", "recipes"}
    by_key = {row.get("key"): row for row in quests}
    for key, (dependencies, tasks) in QUESTS_EXPECTED.items():
        quest = by_key.get(key, {})
        if quest.get("dependencies") != dependencies:
            failures.append(f"Venus quest dependency drifted: {key}")
        if [task_signature(task) for task in quest.get("tasks", [])] != tasks:
            failures.append(f"Venus quest observation set drifted: {key}")
        if forbidden.intersection(quest) or any(forbidden.intersection(task) for task in quest.get("tasks", [])):
            failures.append(f"Venus quest contains a gate or reward: {key}")
        if any(task.get("consume_items", False) for task in quest.get("tasks", [])):
            failures.append(f"Venus quest consumes observed items: {key}")
    native = load_json(project / NATIVE_CHAPTER)
    generated = native.get("quests", [])
    if len(generated) != 29:
        failures.append("generated Planetary Industry chapter is not the 29-quest topology")
    generated_by_key: dict[str, Mapping[str, Any]] = {}
    for quest in generated:
        tags = quest.get("tags", [])
        quest_keys = [tag.rsplit("/", 1)[-1] for tag in tags if tag.startswith("industrial_colonies:planetary_guidance/") and "/phase/" not in tag]
        if len(quest_keys) == 1:
            generated_by_key[quest_keys[0]] = quest
        if any(field in quest for field in ("rewards", "stage", "stages")):
            failures.append("generated Planetary Industry chapter contains a reward/stage")
        if any(task.get("consume_items", False) for task in quest.get("tasks", [])):
            failures.append("generated Planetary Industry chapter contains a consuming task")
    for key, (_, tasks) in QUESTS_EXPECTED.items():
        quest = generated_by_key.get(key)
        if quest is None:
            failures.append(f"generated Venus quest is missing: {key}")
            continue
        actual = []
        for task in quest.get("tasks", []):
            if task.get("type") == "item":
                actual.append(("item", task.get("item", {}).get("id", ""), int(task.get("count", 1))))
            else:
                actual.append((str(task.get("type", "")), str(task.get("advancement", "")), int(task.get("count", 1))))
        if actual != tasks:
            failures.append(f"generated Venus observations drifted: {key}")


def validate_manifest(path: Path, failures: list[str]) -> None:
    payload = load_json(path)
    for recipe_id, expected in RECIPES.items():
        found = rows(payload, recipe_id)
        if len(found) != 1:
            failures.append(f"assembled manifest must contain exactly one {recipe_id}")
            continue
        for field, value in expected.items():
            if field == "depends_on":
                if not set(value).issubset(found[0].get(field, [])):
                    failures.append(f"assembled {recipe_id} {field} drifted")
            elif found[0].get(field) != value:
                failures.append(f"assembled {recipe_id} {field} drifted")


def validate_compiled(path: Path, failures: list[str]) -> None:
    payload = load_json(path)
    cards = {card.get("recipeId"): card for card in payload.get("recipes", []) if card.get("recipeId") in RECIPES}
    if set(cards) != set(RECIPES):
        failures.append("compiled KJSGen project is missing Venus/Calorite recipes")
        return
    type_map = {
        "mechanical_crafting": "kjsgen:create_mechanical_crafting", "crushing": "kjsgen:create_crushing",
        "mekanism_enriching": "kjsgen:mekanism_enriching", "tfmg_vat": "industrial_colonies:tfmg_chemical_vat",
        "pressing": "kjsgen:create_pressing",
    }
    for recipe_id, expected in RECIPES.items():
        card = cards[recipe_id]
        if card.get("type") != type_map[expected["type"]] or card.get("replaceRecipe") is not False:
            failures.append(f"{recipe_id} compiled type/replacement mode drifted")
    for recipe_id in (VENUS_NAV, *SUIT_RECIPES):
        card = cards[recipe_id]
        if card.get("params") != {"gridW": "5", "gridH": "5"}:
            failures.append(f"{recipe_id} compiled grid is not exact 5x5")
    if len([key for key in cards[VENUS_NAV].get("slots", {}) if key.startswith("cell_")]) != 25:
        failures.append("Venus Navigation Computer no longer fills its exact 5x5 integration grid")
    slots = cards[FEED].get("slots", {})
    if slots.get("input") != {"kind": "ITEM_TAG", "id": "industrial_colonies:calorite_crushing_feed"} or slots.get("output0") != {"kind": "ITEM", "id": "industrial_colonies:calorite_grit", "count": 1}:
        failures.append("compiled Calorite feed is no longer a one-grit route")
    expected_vats = {
        LEACH: {"vatMode": "firebrick", "machineMode": "mixing", "heat": "heated", "minSize": "7", "processingTime": "600"},
        REDUCE: {"vatMode": "firebrick", "machineMode": "two_electrodes", "heat": "superheated", "minSize": "7", "processingTime": "900"},
    }
    for recipe_id, params in expected_vats.items():
        if cards[recipe_id].get("params") != params:
            failures.append(f"{recipe_id} compiled vat parameters drifted")
    leach_slots = cards[LEACH].get("slots", {})
    if (leach_slots.get("ingredients1", {}).get("id"), leach_slots.get("ingredients1", {}).get("amount"), leach_slots.get("ingredients2", {}).get("id"), leach_slots.get("ingredients2", {}).get("amount")) != ("tfmg:sulfuric_acid", 1000, "minecraft:water", 1500):
        failures.append("compiled Calorite acid/water charge drifted")
    if cards[PLATE].get("slots", {}).get("__machine_process_pressing") != {"kind": "ITEM", "id": PRESS}:
        failures.append("Calorite plate is no longer locked to the Refined Radiance press")
    removals = payload.get("removals", [])
    compiled_ids = [entry.get("recipeId") for entry in removals]
    for recipe_id in EXACT_REMOVALS:
        exact = [entry for entry in removals if entry.get("recipeId") == recipe_id]
        if len(exact) != 1 or any(str(exact[0].get(field, "")).strip() for field in ("output", "input", "mod")):
            failures.append(f"compiled exact removal drifted: {recipe_id}")
    if PACKING_RECIPES.intersection(compiled_ids):
        failures.append("compiled removals retire preserved Calorite packing")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    recipes_path = catalog / "recipes.csv"
    items_path = catalog / "items.csv"
    if not recipes_path.is_file() or not items_path.is_file():
        failures.append(f"registry catalog is incomplete: {catalog}")
        return
    with recipes_path.open(encoding="utf-8-sig", newline="") as handle:
        recipes = {row.get("recipe_id", ""): row for row in csv.DictReader(handle)}
    missing = sorted((EXACT_REMOVALS | PACKING_RECIPES) - set(recipes))
    if missing:
        failures.append(f"installed catalog is missing pinned Venus/Calorite recipes: {missing}")
    producer_targets = {"ad_astra:calorite_ingot", "ad_astra:calorite_plate", "c:plates/calorite"}
    extra = []
    for recipe_id, row in recipes.items():
        outputs = {value.strip() for value in str(row.get("outputs", "")).split("|")}
        if outputs.intersection(producer_targets) and recipe_id not in EXACT_REMOVALS | PACKING_RECIPES:
            extra.append(recipe_id)
    if extra:
        failures.append(f"unmanaged finished-Calorite producers remain: {sorted(extra)}")
    # The heat-resistant root tag also contains the Jet Suit family.  A full
    # alternate set must remain post-Calorite so it cannot bypass first Venus
    # landfall even though the helmet itself is only a visor upgrade.
    jet_requirements = {
        "ad_astra:jet_suit": {"ad_astra:calorite_engine", "ad_astra:calorite_tank", "ad_astra:netherite_space_suit"},
        "ad_astra:jet_suit_boots": {"ad_astra:calorite_block", "ad_astra:netherite_space_boots"},
        "ad_astra:jet_suit_pants": {"ad_astra:calorite_block", "ad_astra:netherite_space_pants"},
    }
    for recipe_id, expected_inputs in jet_requirements.items():
        row = recipes.get(recipe_id)
        inputs = {value.strip() for value in str((row or {}).get("inputs", "")).split("|")}
        if not expected_inputs.issubset(inputs):
            failures.append(f"alternate heat-resistant set is no longer post-Calorite: {recipe_id}")
    with items_path.open(encoding="utf-8-sig", newline="") as handle:
        items = {row.get("item_id", "") for row in csv.DictReader(handle)}
    required_items = {
        *NAV_KEY.values(), "ad_astra:raw_calorite", "ad_astra:calorite_ingot", "ad_astra:calorite_plate",
        "ad_astra:venus_calorite_ore", "ad_astra:deepslate_calorite_ore",
        "ad_astra:netherite_space_helmet", "ad_astra:netherite_space_suit",
        "ad_astra:netherite_space_pants", "ad_astra:netherite_space_boots",
    }
    owned = {"industrial_colonies:mars_navigation_computer"}
    if missing_items := sorted(required_items - items - owned):
        failures.append(f"installed registry is missing Venus ingredients: {missing_items}")


def validate_installed_jars(mods: Path, failures: list[str]) -> None:
    pinned_jars = {
        "cosmonautics-26.08.307.jar": COSMONAUTICS_JAR_SHA256,
        "sable-neoforge-1.21.1-2.0.3.jar": SABLE_JAR_SHA256,
        "adastra-1.21.1-1.16.22-neoforge.jar": AD_ASTRA_JAR_SHA256,
    }
    for name, expected_hash in pinned_jars.items():
        path = mods / name
        if not path.is_file():
            failures.append(f"pinned Venus runtime dependency is missing: {name}")
            continue
        if sha256(path.read_bytes()) != expected_hash:
            failures.append(f"pinned Venus runtime dependency hash drifted: {name}")
    for name, classes in PINNED_CLASSES.items():
        path = mods / name
        if not path.is_file():
            continue
        with zipfile.ZipFile(path) as archive:
            for entry, expected_hash in classes.items():
                try:
                    encoded = archive.read(entry)
                except KeyError:
                    failures.append(f"pinned loader class is missing: {name}!/{entry}")
                    continue
                if sha256(encoded) != expected_hash:
                    failures.append(f"pinned loader class hash drifted: {name}!/{entry}")

    ad_astra = mods / "adastra-1.21.1-1.16.22-neoforge.jar"
    if ad_astra.is_file():
        with zipfile.ZipFile(ad_astra) as archive:
            required_entries = {
                "assets/ad_astra/textures/block/calorite_factory_block.png",
                "assets/ad_astra/textures/environment/venus.png",
                "assets/ad_astra/textures/item/calorite_ingot.png",
                "assets/ad_astra/textures/item/calorite_nugget.png",
                "assets/ad_astra/textures/item/raw_calorite.png",
                "data/ad_astra/tags/item/calorite_ores.json",
                "data/ad_astra/tags/item/raw_calorite.json",
                "data/ad_astra/tags/item/raw_calorite_blocks.json",
                "data/c/tags/item/ingots/calorite.json",
                "data/c/tags/item/nuggets/calorite.json",
                "data/c/tags/item/ores/calorite.json",
                "data/c/tags/item/plates/calorite.json",
                "data/c/tags/item/raw_materials/calorite.json",
                "data/c/tags/item/storage_blocks/calorite.json",
            }
            if missing := sorted(required_entries - set(archive.namelist())):
                failures.append(f"installed Ad Astra is missing Calorite assets/tags: {missing}")
            heat = json.loads(archive.read("data/ad_astra/tags/item/heat_resistant_armor.json"))
            suit = json.loads(archive.read("data/ad_astra/tags/item/netherite_space_suit_items.json"))
        if heat != {"values": ["#ad_astra:netherite_space_suit_items"]}:
            failures.append("installed heat-resistant armor root tag drifted")
        required_suit_values = {
            "ad_astra:netherite_space_helmet", "ad_astra:netherite_space_suit",
            "ad_astra:netherite_space_pants", "ad_astra:netherite_space_boots",
            "#ad_astra:jet_suit_items",
        }
        if set(suit.get("values", [])) != required_suit_values:
            failures.append("installed heat-resistant suit member tag drifted")

    forbidden_finished = {
        b"ad_astra:calorite_ingot", b"ad_astra:calorite_plate",
        b"ad_astra:calorite_block", b"ad_astra:calorite_nugget",
        b"ad_astra:netherite_space_helmet", b"ad_astra:netherite_space_suit",
        b"ad_astra:netherite_space_pants", b"ad_astra:netherite_space_boots",
    }
    for jar in sorted(mods.glob("*.jar")):
        if jar.name.startswith("industrial_colonies-"):
            continue
        try:
            with zipfile.ZipFile(jar) as archive:
                for info in archive.infolist():
                    name = info.filename
                    if name.endswith(".json") and "/universe_planets/" in name:
                        try:
                            payload = json.loads(archive.read(info))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
                        if payload.get("name") == "venus":
                            failures.append(f"installed JAR competes for Rocketnautics Venus ownership: {jar.name}!/{name}")
                    elif name.endswith(".json") and "/dimension_physics/" in name:
                        try:
                            payload = json.loads(archive.read(info))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
                        if payload.get("dimension") == "ad_astra:venus":
                            failures.append(f"installed JAR competes for Sable Venus ownership: {jar.name}!/{name}")
                    elif name.endswith(".json") and "/loot_table/" in name and "/loot_table/blocks/" not in name:
                        encoded = archive.read(info)
                        hits = sorted(value.decode() for value in forbidden_finished if value in encoded)
                        if hits:
                            failures.append(f"finished Venus material appears in external loot: {jar.name}!/{name}: {hits}")
                    elif name.endswith(".nbt") and "/structure/" in name:
                        encoded = archive.read(info)
                        try:
                            raw = gzip.decompress(encoded) if encoded.startswith(b"\x1f\x8b") else encoded
                        except (OSError, gzip.BadGzipFile):
                            raw = encoded
                        hits = sorted(value.decode() for value in forbidden_finished if value in raw)
                        if hits:
                            failures.append(f"finished Venus material appears in external structure: {jar.name}!/{name}: {hits}")
        except (OSError, zipfile.BadZipFile):
            continue


def validate_candidate_jar(path: Path, failures: list[str]) -> None:
    required = {
        "dev/godpc/industrialcolonies/space/VenusNavigationComputerBlock.class",
        "dev/godpc/industrialcolonies/space/VenusNavigationComputerBlockEntity.class",
        "dev/godpc/industrialcolonies/space/SpaceflightAuthorization.class",
        "dev/godpc/industrialcolonies/mixin/DeepSpaceInstanceMixin.class",
        "assets/industrial_colonies/blockstates/venus_navigation_computer.json",
        "assets/industrial_colonies/models/block/venus_navigation_computer.json",
        "assets/industrial_colonies/models/item/venus_navigation_computer.json",
        "data/industrial_colonies/loot_table/blocks/venus_navigation_computer.json",
        "data/rocketnautics/universe_planets/venus.json",
        "data/industrial_colonies/dimension_physics/ad_astra_venus.json",
        "data/industrial_colonies/advancement/planetary/venus_arrival.json",
        "data/industrial_colonies/tags/item/calorite_crushing_feed.json",
    }
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as exc:
        failures.append(f"candidate JAR cannot be inspected: {exc}")
        return
    if missing := sorted(required - names):
        failures.append(f"candidate JAR is missing Venus runtime entries: {missing}")


def default_catalog() -> Path:
    return (PROJECT.parents[1] / "outputs" / "recipe-catalog-current").resolve()


def default_mods() -> Path | None:
    properties = (PROJECT / "gradle.properties").read_text(encoding="utf-8-sig")
    match = re.search(r"(?m)^pack_mods_dir=(.+)$", properties)
    return Path(match.group(1).strip()).expanduser().resolve() if match else None


def validate(
    project: Path,
    *,
    manifest: Path | None = None,
    compiled: Path | None = None,
    catalog: Path | None = None,
    mods: Path | None = None,
    candidate_jar: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    missing = [relative.as_posix() for relative in REQUIRED_FILES if not (project / relative).is_file()]
    if missing:
        return [f"missing Venus/Calorite source file: {relative}" for relative in missing]
    validate_recipe_source(project, failures)
    validate_assets(project, failures)
    validate_destination_data(project, failures)
    validate_runtime_gate(project, failures)
    validate_assignments(project, failures)
    validate_quests(project, failures)
    if manifest is not None:
        validate_manifest(manifest, failures)
    if compiled is not None:
        validate_compiled(compiled, failures)
    if catalog is not None:
        validate_catalog(catalog, failures)
    if mods is not None:
        validate_installed_jars(mods, failures)
    if candidate_jar is not None:
        validate_candidate_jar(candidate_jar, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--compiled", type=Path, default=COMPILED)
    parser.add_argument("--catalog", type=Path, default=default_catalog())
    parser.add_argument("--mods", type=Path, default=default_mods())
    parser.add_argument("--jar", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    failures = validate(
        project,
        manifest=(args.manifest if args.manifest.is_absolute() else project / args.manifest).resolve(),
        compiled=(args.compiled if args.compiled.is_absolute() else project / args.compiled).resolve(),
        catalog=args.catalog.resolve(),
        mods=args.mods.resolve() if args.mods else None,
        candidate_jar=args.jar.resolve() if args.jar else None,
    )
    if failures:
        print("FAIL: Venus Expedition and Calorite metallurgy slice is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("PASS: Venus is source-owned with fail-closed ship/suit authorization; ten managed recipes retire 20 exact shortcuts, preserve Calorite packing, and feed four observation-only quests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
