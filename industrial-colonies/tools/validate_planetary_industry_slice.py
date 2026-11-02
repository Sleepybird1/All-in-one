#!/usr/bin/env python3
"""Fail closed on the Moon Desh / Mars Ostrum physical-industry slice."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable, Mapping

import build_planetary_structure_overrides as structure_builder
import validate_mercury_asteroid_slice as mercury_validator
import validate_planetary_outpost_slice as outpost_validator
import validate_venus_calorite_slice as venus_validator


PROJECT = Path(__file__).resolve().parents[1]
SEED = Path("progression/managed_recipe_overhaul.seed.json")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
COMPILED = Path("pack-kjsgen/default.managed.json")
ASSIGNMENTS = Path("progression/machine_node_assignments.json")
QUESTS = Path("progression/ftbquests_planetary_industry.json")
NATIVE_CHAPTER = Path("pack-config-overrides/ftbquests/quests/chapters/planetary_industry.snbt")
ITEMS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java")
LANG = Path("src/main/resources/assets/industrial_colonies/lang/en_us.json")
MODEL_DIR = Path("src/main/resources/assets/industrial_colonies/models/item")
DESH_FEED_TAG = Path("src/main/resources/data/industrial_colonies/tags/item/desh_crushing_feed.json")
OSTRUM_FEED_TAG = Path("src/main/resources/data/industrial_colonies/tags/item/ostrum_crushing_feed.json")
MOON_LOOT = (
    Path("src/main/resources/data/ad_astra/loot_table/chests/village/moon/blacksmith.json"),
    Path("src/main/resources/data/ad_astra/loot_table/chests/village/moon/house.json"),
)
ADVANCEMENTS = {
    "moon_arrival": (Path("src/main/resources/data/industrial_colonies/advancement/planetary/moon_arrival.json"), "ad_astra:moon"),
    "mars_arrival": (Path("src/main/resources/data/industrial_colonies/advancement/planetary/mars_arrival.json"), "ad_astra:mars"),
}
STRUCTURE_RESOURCES = tuple(
    Path("src/main/resources") / spec.entry
    for spec in structure_builder.STRUCTURE_OVERRIDES
)

PHASE = "Planetary Industry"
LUNAR_NODE = "CR02 — Lunar Metallurgy"
NAVIGATION_NODE = "CR02 — Mars Navigation"
MARTIAN_NODE = "CR02 — Martian Metallurgy"
NODES = (LUNAR_NODE, NAVIGATION_NODE, MARTIAN_NODE)
PRESS = "createcasing:refined_radiance_press"
CUSTOM_ITEMS = (
    "desh_grit", "desh_concentrate", "desh_leached_compound",
    "ostrum_grit", "ostrum_concentrate", "ostrum_leached_compound",
)
CUSTOM_ITEM_IDS = {f"industrial_colonies:{name}" for name in CUSTOM_ITEMS}
LANG_EXPECTED = {
    "item.industrial_colonies.desh_grit": "Desh Grit",
    "item.industrial_colonies.desh_concentrate": "Desh Concentrate",
    "item.industrial_colonies.desh_leached_compound": "Leached Desh Compound",
    "item.industrial_colonies.ostrum_grit": "Ostrum Grit",
    "item.industrial_colonies.ostrum_concentrate": "Ostrum Concentrate",
    "item.industrial_colonies.ostrum_leached_compound": "Leached Ostrum Compound",
    "block.industrial_colonies.mars_navigation_computer": "Mars Navigation Computer",
}
MODEL_TEXTURES = {
    "desh_grit": "ad_astra:item/raw_desh",
    "desh_concentrate": "ad_astra:item/desh_nugget",
    "desh_leached_compound": "ad_astra:item/desh_ingot",
    "ostrum_grit": "ad_astra:item/raw_ostrum",
    "ostrum_concentrate": "ad_astra:item/ostrum_nugget",
    "ostrum_leached_compound": "ad_astra:item/ostrum_ingot",
}
FEED_TAGS = {
    DESH_FEED_TAG: [
        "#c:ores/desh", "#c:raw_materials/desh",
        "rocketnautics_addon:mars_desh_ore", "rocketnautics_addon:raw_desh",
    ],
    OSTRUM_FEED_TAG: ["#c:ores/ostrum", "#c:raw_materials/ostrum"],
}

DESH_FEED = "industrial_colonies:planetary/desh/feed_to_grit"
DESH_ENRICH = "industrial_colonies:planetary/desh/grit_to_concentrate"
DESH_LEACH = "industrial_colonies:planetary/desh/concentrate_leaching"
DESH_REDUCE = "industrial_colonies:planetary/desh/leached_compound_reduction"
DESH_PLATE = "industrial_colonies:planetary/desh/plate"
MARS_NAV = "industrial_colonies:planetary/navigation/mars_navigation_computer"
OSTRUM_FEED = "industrial_colonies:planetary/ostrum/feed_to_grit"
OSTRUM_ENRICH = "industrial_colonies:planetary/ostrum/grit_to_concentrate"
OSTRUM_LEACH = "industrial_colonies:planetary/ostrum/concentrate_leaching"
OSTRUM_REDUCE = "industrial_colonies:planetary/ostrum/leached_compound_reduction"
OSTRUM_PLATE = "industrial_colonies:planetary/ostrum/plate"

RECIPE_FIELDS: dict[str, dict[str, Any]] = {
    DESH_FEED: {
        "node": LUNAR_NODE, "phase": PHASE, "order": 10, "type": "crushing",
        "input": "#industrial_colonies:desh_crushing_feed",
        "outputs": [{"kind": "ITEM", "id": "industrial_colonies:desh_grit", "count": 1}],
        "processing_time": 300,
        "remove": [
            "create:crushing/moon_desh_ore", "create:crushing/deepslate_desh_ore",
            "modern_industrialization:macerator/desh_ore",
        ],
        "depends_on": ["industrial_colonies:space/station/fluid_pipe_duct"],
    },
    DESH_ENRICH: {
        "node": LUNAR_NODE, "phase": PHASE, "order": 50, "type": "mekanism_enriching",
        "input": "industrial_colonies:desh_grit", "output": "industrial_colonies:desh_concentrate",
        "depends_on": [DESH_FEED],
    },
    DESH_LEACH: {
        "node": LUNAR_NODE, "phase": PHASE, "order": 60, "type": "tfmg_vat",
        "ingredients": [
            "2x industrial_colonies:desh_concentrate",
            {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 250},
            {"kind": "FLUID", "id": "minecraft:water", "amount": 750},
        ],
        "results": [{"kind": "ITEM", "id": "industrial_colonies:desh_leached_compound", "count": 2}],
        "vat_mode": "steel", "machine_mode": "mixing", "heat": "none",
        "min_size": 3, "processing_time": 200, "depends_on": [DESH_ENRICH],
    },
    DESH_REDUCE: {
        "node": LUNAR_NODE, "phase": PHASE, "order": 70, "type": "tfmg_vat",
        "ingredients": ["industrial_colonies:desh_leached_compound"],
        "results": [{"kind": "ITEM", "id": "ad_astra:desh_ingot"}],
        "vat_mode": "steel", "machine_mode": "two_electrodes", "heat": "heated",
        "min_size": 3, "processing_time": 300,
        "remove": [
            "ad_astra:smelting/desh_ingot_from_smelting_deepslate_desh_ore",
            "ad_astra:smelting/desh_ingot_from_smelting_moon_desh_ore",
            "ad_astra:smelting/desh_ingot_from_smelting_raw_desh",
            "ad_astra:blasting/desh_ingot_from_blasting_deepslate_desh_ore",
            "ad_astra:blasting/desh_ingot_from_blasting_moon_desh_ore",
            "ad_astra:blasting/desh_ingot_from_blasting_raw_desh",
            "rocketnautics_addon:mars_desh_ore_from_blasting",
            "rocketnautics_addon:mars_desh_ore_from_smelting",
            "rocketnautics_addon:raw_desh_from_blasting",
            "rocketnautics_addon:raw_desh_from_smelting",
        ],
        "depends_on": [DESH_LEACH],
    },
    DESH_PLATE: {
        "node": LUNAR_NODE, "phase": PHASE, "order": 80, "type": "pressing",
        "machine": PRESS, "input": "ad_astra:desh_ingot", "output": "ad_astra:desh_plate",
        "remove": [
            "ad_astra:compressing/desh_plate_from_compressing_desh_blocks",
            "ad_astra:compressing/desh_plate_from_compressing_desh_ingots",
            "create:pressing/desh_ingot",
            "immersiveengineering:crafting/plate_desh_hammering",
            "immersiveengineering:metalpress/plate_desh",
            "modern_industrialization:compressor/desh_ingot_to_plate",
            "thermal:machines/press/press_desh_ingot_to_plate",
        ],
        "exclusive_output": True, "depends_on": [DESH_REDUCE],
    },
    MARS_NAV: {
        "node": NAVIGATION_NODE, "phase": PHASE, "order": 90, "type": "mechanical_crafting",
        "pattern": ["PIAIP", "PEBEP", "CCNCC", "PEOEP", "PIMIP"],
        "key": {
            "P": "ad_astra:desh_plate", "I": "ad_astra:desh_ingot",
            "A": "computercraft:monitor_advanced", "E": "ae2:engineering_processor",
            "B": "tfmg:etched_circuit_board", "C": "tfmg:circuit_board",
            "N": "simulated:navigation_table", "O": "industrial_colonies:orbital_flight_computer",
            "M": "computercraft:computer_advanced",
        },
        "output": "industrial_colonies:mars_navigation_computer", "depends_on": [DESH_PLATE],
    },
    OSTRUM_FEED: {
        "node": MARTIAN_NODE, "phase": PHASE, "order": 100, "type": "crushing",
        "input": "#industrial_colonies:ostrum_crushing_feed",
        "outputs": [{"kind": "ITEM", "id": "industrial_colonies:ostrum_grit", "count": 1}],
        "processing_time": 360,
        "remove": [
            "create:crushing/mars_ostrum_ore", "create:crushing/deepslate_ostrum_ore",
            "modern_industrialization:macerator/ostrum_ore",
        ],
        "depends_on": [MARS_NAV],
    },
    OSTRUM_ENRICH: {
        "node": MARTIAN_NODE, "phase": PHASE, "order": 120, "type": "mekanism_enriching",
        "input": "industrial_colonies:ostrum_grit", "output": "industrial_colonies:ostrum_concentrate",
        "depends_on": [OSTRUM_FEED],
    },
    OSTRUM_LEACH: {
        "node": MARTIAN_NODE, "phase": PHASE, "order": 130, "type": "tfmg_vat",
        "ingredients": [
            "2x industrial_colonies:ostrum_concentrate",
            {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 500},
            {"kind": "FLUID", "id": "minecraft:water", "amount": 1000},
        ],
        "results": [{"kind": "ITEM", "id": "industrial_colonies:ostrum_leached_compound", "count": 2}],
        "vat_mode": "firebrick", "machine_mode": "mixing", "heat": "none",
        "min_size": 5, "processing_time": 400, "depends_on": [OSTRUM_ENRICH],
    },
    OSTRUM_REDUCE: {
        "node": MARTIAN_NODE, "phase": PHASE, "order": 140, "type": "tfmg_vat",
        "ingredients": ["industrial_colonies:ostrum_leached_compound"],
        "results": [{"kind": "ITEM", "id": "ad_astra:ostrum_ingot"}],
        "vat_mode": "firebrick", "machine_mode": "two_electrodes", "heat": "heated",
        "min_size": 5, "processing_time": 600,
        "remove": [
            "ad_astra:smelting/ostrum_ingot_from_smelting_deepslate_ostrum_ore",
            "ad_astra:smelting/ostrum_ingot_from_smelting_mars_ostrum_ore",
            "ad_astra:smelting/ostrum_ingot_from_smelting_raw_ostrum",
            "ad_astra:blasting/ostrum_ingot_from_blasting_deepslate_ostrum_ore",
            "ad_astra:blasting/ostrum_ingot_from_blasting_mars_ostrum_ore",
            "ad_astra:blasting/ostrum_ingot_from_blasting_raw_ostrum",
        ],
        "depends_on": [OSTRUM_LEACH],
    },
    OSTRUM_PLATE: {
        "node": MARTIAN_NODE, "phase": PHASE, "order": 150, "type": "pressing",
        "machine": PRESS, "input": "ad_astra:ostrum_ingot", "output": "ad_astra:ostrum_plate",
        "remove": [
            "ad_astra:compressing/ostrum_plate_from_compressing_ostrum_blocks",
            "ad_astra:compressing/ostrum_plate_from_compressing_ostrum_ingots",
            "create:pressing/ostrum_ingot",
            "immersiveengineering:crafting/plate_ostrum_hammering",
            "immersiveengineering:metalpress/plate_ostrum",
            "modern_industrialization:compressor/ostrum_ingot_to_plate",
            "thermal:machines/press/press_ostrum_ingot_to_plate",
        ],
        "exclusive_output": True, "depends_on": [OSTRUM_REDUCE],
    },
}

EXACT_REMOVALS = {
    "create:crushing/moon_desh_ore", "create:crushing/deepslate_desh_ore",
    "create:crushing/mars_ostrum_ore", "create:crushing/deepslate_ostrum_ore",
    "modern_industrialization:macerator/desh_ore", "modern_industrialization:macerator/ostrum_ore",
    *{
        f"ad_astra:{process}/{metal}_ingot_from_{process}_{source}"
        for metal, sources in (
            ("desh", ("deepslate_desh_ore", "moon_desh_ore", "raw_desh")),
            ("ostrum", ("deepslate_ostrum_ore", "mars_ostrum_ore", "raw_ostrum")),
        )
        for process in ("smelting", "blasting")
        for source in sources
    },
    "rocketnautics_addon:mars_desh_ore_from_blasting",
    "rocketnautics_addon:mars_desh_ore_from_smelting",
    "rocketnautics_addon:raw_desh_from_blasting",
    "rocketnautics_addon:raw_desh_from_smelting",
    *{
        recipe
        for metal in ("desh", "ostrum")
        for recipe in (
            f"ad_astra:compressing/{metal}_plate_from_compressing_{metal}_blocks",
            f"ad_astra:compressing/{metal}_plate_from_compressing_{metal}_ingots",
            f"create:pressing/{metal}_ingot",
            f"immersiveengineering:crafting/plate_{metal}_hammering",
            f"immersiveengineering:metalpress/plate_{metal}",
            f"modern_industrialization:compressor/{metal}_ingot_to_plate",
            f"thermal:machines/press/press_{metal}_ingot_to_plate",
        )
    },
}
PACKING_RECIPES = {
    *{
        f"ad_astra:{name}"
        for name in (
            "desh_block", "desh_ingot", "desh_ingot_from_desh_block", "desh_nugget",
            "raw_desh", "raw_desh_block", "ostrum_block", "ostrum_ingot",
            "ostrum_ingot_from_ostrum_block", "ostrum_nugget", "raw_ostrum", "raw_ostrum_block",
        )
    },
    "rocketnautics_addon:desh_ingot_from_shapeless_desh_ingot_0",
    "rocketnautics_addon:desh_nugget_from_shapeless_desh_nugget_0",
}
FORBIDDEN_REMOVAL_FIELDS = {
    "remove_by_output", "removeByOutput", "remove_by_mod", "removeByMod",
    "remove_by_input", "removeByInput", "replace", "replace_recipe", "replaceRecipe",
}

NODE_UNLOCKS = {
    LUNAR_NODE: [
        "industrial_colonies:desh_grit", "industrial_colonies:desh_concentrate",
        "industrial_colonies:desh_leached_compound", "ad_astra:desh_ingot", "ad_astra:desh_plate",
    ],
    NAVIGATION_NODE: ["industrial_colonies:mars_navigation_computer"],
    MARTIAN_NODE: [
        "industrial_colonies:ostrum_grit", "industrial_colonies:ostrum_concentrate",
        "industrial_colonies:ostrum_leached_compound", "ad_astra:ostrum_ingot", "ad_astra:ostrum_plate",
    ],
}
QUEST_EXPECTED = {
    "moon_arrival": (["orbital_engineering:station_materials"], [("advancement", "industrial_colonies:planetary/moon_arrival", 1)]),
    "desh_freight": (["moon_arrival"], [("item", "ad_astra:raw_desh", 64)]),
    "desh_metallurgy": (["desh_freight"], [("item", item, 1) for item in (
        "industrial_colonies:desh_grit", "industrial_colonies:desh_concentrate",
        "industrial_colonies:desh_leached_compound", "ad_astra:desh_ingot", "ad_astra:desh_plate")]),
    "mars_navigation_computer": (["desh_metallurgy"], [("item", "industrial_colonies:mars_navigation_computer", 1)]),
    "mars_arrival": (["mars_navigation_computer"], [("advancement", "industrial_colonies:planetary/mars_arrival", 1)]),
    "ostrum_freight": (["mars_arrival"], [("item", "ad_astra:raw_ostrum", 64)]),
    "ostrum_metallurgy": (["ostrum_freight"], [("item", item, 1) for item in (
        "industrial_colonies:ostrum_grit", "industrial_colonies:ostrum_concentrate",
        "industrial_colonies:ostrum_leached_compound", "ad_astra:ostrum_ingot", "ad_astra:ostrum_plate")]),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows(payload: Mapping[str, Any], recipe_id: str) -> list[dict[str, Any]]:
    return [row for row in payload.get("recipes", []) if isinstance(row, dict) and row.get("id") == recipe_id]


def walk_names(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "name" and isinstance(child, str):
                yield child
            yield from walk_names(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_names(child)


def task_signature(task: Mapping[str, Any]) -> tuple[str, str, int]:
    task_type = str(task.get("type", ""))
    target = task.get("item") if task_type == "item" else task.get("advancement")
    return task_type, str(target or ""), int(task.get("count", 1))


def validate_recipe_source(project: Path, failures: list[str]) -> None:
    seed = load_json(project / SEED)
    if PHASE not in seed.get("phase_order", []):
        failures.append("Planetary Industry phase is absent")
    else:
        phase_order = seed["phase_order"]
        if phase_order.index(PHASE) != phase_order.index("Orbital Engineering") + 1:
            failures.append("Planetary Industry must immediately follow Orbital Engineering")
    for node in NODES:
        if seed.get("phase_by_node", {}).get(node) != PHASE:
            failures.append(f"{node} is not assigned to Planetary Industry")

    expected_planetary_ids = (
        set(RECIPE_FIELDS)
        | set(outpost_validator.RECIPES)
        | set(venus_validator.RECIPES)
        | {mercury_validator.RECIPE_ID}
    )
    scoped = [row for row in seed.get("recipes", []) if str(row.get("id", "")).startswith("industrial_colonies:planetary/")]
    if {row.get("id") for row in scoped} != expected_planetary_ids or len(scoped) != len(expected_planetary_ids):
        failures.append("planetary managed recipe set is not exactly the approved Moon/Mars, outpost, Venus/Calorite, and Mercury recipes")
    all_removals: list[str] = []
    for recipe_id, expected in RECIPE_FIELDS.items():
        found = rows(seed, recipe_id)
        if len(found) != 1:
            failures.append(f"managed seed must contain exactly one {recipe_id}")
            continue
        recipe = found[0]
        for field, expected_value in expected.items():
            if recipe.get(field) != expected_value:
                failures.append(f"{recipe_id} {field} drifted")
        if not str(recipe.get("comment", "")).strip():
            failures.append(f"{recipe_id} lacks a manufacturing rationale")
        if FORBIDDEN_REMOVAL_FIELDS.intersection(recipe):
            failures.append(f"{recipe_id} contains a broad removal directive")
        all_removals.extend(recipe.get("remove", []))
    if len(all_removals) != 36 or len(set(all_removals)) != 36 or set(all_removals) != EXACT_REMOVALS:
        failures.append("planetary shortcut retirement is not the exact 36-ID audited set")
    if PACKING_RECIPES.intersection(all_removals + seed.get("additional_removals", [])):
        failures.append("ingot/nugget/block/raw-block packing preservation drifted")
    for recipe_id in (DESH_REDUCE, OSTRUM_REDUCE):
        recipe = rows(seed, recipe_id)
        if recipe and recipe[0].get("exclusive_output"):
            failures.append(f"{recipe_id} must preserve canonical packing producers")


def validate_tags_and_assets(project: Path, failures: list[str]) -> None:
    for relative, values in FEED_TAGS.items():
        payload = load_json(project / relative)
        if payload != {"replace": False, "values": values}:
            failures.append(f"planetary crushing feed tag drifted: {relative.name}")
    java = (project / ITEMS_JAVA).read_text(encoding="utf-8-sig")
    for name in CUSTOM_ITEMS:
        if java.count(f'ITEMS.registerSimpleItem("{name}")') != 1:
            failures.append(f"custom metallurgy item registration drifted: {name}")
    if java.count('ITEMS.registerSimpleBlockItem(\n                    "mars_navigation_computer"') != 1:
        failures.append("Mars Navigation Computer block-item registration drifted")
    lang = load_json(project / LANG)
    for key, value in LANG_EXPECTED.items():
        if lang.get(key) != value:
            failures.append(f"language entry drifted: {key}")
    for name, texture in MODEL_TEXTURES.items():
        model = load_json(project / MODEL_DIR / f"{name}.json")
        if model != {"parent": "minecraft:item/generated", "textures": {"layer0": texture}}:
            failures.append(f"external-texture item model drifted: {name}")


def validate_assignments(project: Path, failures: list[str]) -> None:
    nodes = load_json(project / ASSIGNMENTS).get("nodes", {})
    for node, unlocks in NODE_UNLOCKS.items():
        if nodes.get(node, {}).get("unlocks") != unlocks:
            failures.append(f"{node} unlock assignment drifted")
        if not str(nodes.get(node, {}).get("role", "")).strip():
            failures.append(f"{node} role is blank")


def validate_loot(project: Path, failures: list[str]) -> None:
    for relative in MOON_LOOT:
        payload = load_json(project / relative)
        names = list(walk_names(payload))
        non_vanilla = [name for name in names if not name.startswith("minecraft:")]
        if non_vanilla != ["ad_astra:raw_desh"]:
            failures.append(f"Moon village loot may contain only modest raw Desh plus vanilla loot: {relative.name}")
            continue
        raw_entries = [entry for pool in payload.get("pools", []) for entry in pool.get("entries", []) if entry.get("name") == "ad_astra:raw_desh"]
        if len(raw_entries) != 1:
            failures.append(f"Moon village loot must contain exactly one raw Desh entry: {relative.name}")
            continue
        count_functions = [fn for fn in raw_entries[0].get("functions", []) if fn.get("function") == "minecraft:set_count"]
        maximum = count_functions[0].get("count", {}).get("max") if len(count_functions) == 1 else None
        if not isinstance(maximum, (int, float)) or maximum > 3:
            failures.append(f"Moon village raw Desh quantity is not modest: {relative.name}")


def validate_advancements(project: Path, failures: list[str]) -> None:
    for key, (relative, dimension) in ADVANCEMENTS.items():
        payload = load_json(project / relative)
        criteria = payload.get("criteria", {})
        if len(criteria) != 1:
            failures.append(f"{key} advancement must have exactly one criterion")
            continue
        criterion = next(iter(criteria.values()))
        if criterion != {"trigger": "minecraft:changed_dimension", "conditions": {"to": dimension}}:
            failures.append(f"{key} changed-dimension observation drifted")
        if "rewards" in payload or "display" in payload or payload.get("sends_telemetry_event") is not False:
            failures.append(f"{key} advancement is no longer a no-reward observation")


def validate_structure_overrides(
    project: Path, mods: Path | None, failures: list[str]
) -> None:
    expected_from_source: dict[str, bytes] = {}
    if mods is not None:
        try:
            built = structure_builder.build(mods)
            expected_from_source = {
                spec.entry: built[spec.output]
                for spec in structure_builder.STRUCTURE_OVERRIDES
            }
        except (OSError, ValueError, gzip.BadGzipFile, zipfile.BadZipFile, KeyError) as exc:
            failures.append(f"pinned Ad Astra structure source validation failed: {exc}")
    for spec in structure_builder.STRUCTURE_OVERRIDES:
        relative = Path("src/main/resources") / spec.entry
        encoded = (project / relative).read_bytes()
        if structure_builder.sha256(encoded) != spec.output_compressed_sha256:
            failures.append(f"generated structure override encoding hash drifted: {spec.entry}")
        try:
            raw = gzip.decompress(encoded)
        except (OSError, gzip.BadGzipFile) as exc:
            failures.append(
                f"generated structure override is not valid compressed NBT: {spec.entry}: {exc}"
            )
            continue
        if structure_builder.sha256(raw) != spec.output_raw_sha256:
            failures.append(f"generated structure override content hash drifted: {spec.entry}")
        if raw.count(spec.old) != 0 or raw.count(spec.new) != spec.existing_new_count + 1:
            failures.append(f"structure palette bypass replacement drifted: {spec.entry}")
        if expected_from_source and expected_from_source.get(spec.entry) != encoded:
            failures.append(f"structure override is stale against pinned source JAR: {spec.entry}")


def validate_quests(project: Path, failures: list[str]) -> None:
    payload = load_json(project / QUESTS)
    chapter = payload.get("chapter", {})
    quest_rows = chapter.get("quests", [])
    if chapter.get("key") != "planetary_industry" or chapter.get("order_index") != 20:
        failures.append("Planetary Industry chapter identity/order drifted")
    expected_quest_order = [
        *QUEST_EXPECTED,
        *outpost_validator.QUESTS_EXPECTED,
        *venus_validator.QUESTS_EXPECTED,
        *mercury_validator.QUESTS_EXPECTED,
        "outer_station_services",
        "gas_giant_extraction",
        "gas_giant_condensate_return",
        "warp_charge_precursor",
        "moon_crystal_stockpile",
        "interstellar_navigation",
        "signed_route_crystal",
        "warp_drive_core",
        "interstellar_warp_charge",
        "glacio_arrival",
        "escaped_sol",
    ]
    if [row.get("key") for row in quest_rows] != expected_quest_order:
        failures.append("Planetary Industry quest order drifted")
    forbidden = {"rewards", "stage", "stages", "command", "commands", "recipe", "recipes"}
    for quest in quest_rows:
        key = quest.get("key", "")
        if key not in QUEST_EXPECTED:
            continue
        dependencies, tasks = QUEST_EXPECTED[key]
        if quest.get("dependencies") != dependencies:
            failures.append(f"planetary quest dependency drifted: {key}")
        if [task_signature(task) for task in quest.get("tasks", [])] != tasks:
            failures.append(f"planetary quest observation set drifted: {key}")
        if forbidden.intersection(quest) or any(forbidden.intersection(task) for task in quest.get("tasks", [])):
            failures.append(f"planetary quest contains a gate or reward: {key}")
        if any(task.get("consume_items", False) for task in quest.get("tasks", [])):
            failures.append(f"planetary quest consumes observed items: {key}")
    native = load_json(project / NATIVE_CHAPTER)
    generated = native.get("quests", [])
    if native.get("filename") != "planetary_industry" or native.get("order_index") != 20 or len(generated) != len(expected_quest_order):
        failures.append("generated Planetary Industry chapter is stale")
    generated_by_key = {}
    for quest in generated:
        tags = quest.get("tags", [])
        keys = [tag.rsplit("/", 1)[-1] for tag in tags if tag.startswith("industrial_colonies:planetary_guidance/") and "/phase/" not in tag]
        if len(keys) == 1:
            generated_by_key[keys[0]] = quest
        if any(field in quest for field in ("rewards", "stage", "stages")):
            failures.append("generated Planetary Industry chapter contains a reward/stage")
        if any(task.get("consume_items", False) for task in quest.get("tasks", [])):
            failures.append("generated Planetary Industry chapter contains a consuming task")
    for key, (_, expected_tasks) in QUEST_EXPECTED.items():
        quest = generated_by_key.get(key)
        if quest is None:
            failures.append(f"generated Planetary Industry quest is missing: {key}")
            continue
        actual = []
        for task in quest.get("tasks", []):
            if task.get("type") == "item":
                actual.append(("item", task.get("item", {}).get("id", ""), int(task.get("count", 1))))
            else:
                actual.append((str(task.get("type", "")), str(task.get("advancement", "")), int(task.get("count", 1))))
        if actual != expected_tasks:
            failures.append(f"generated Planetary Industry observations drifted: {key}")


def validate_compiled(path: Path, failures: list[str]) -> None:
    payload = load_json(path)
    cards = {card.get("recipeId"): card for card in payload.get("recipes", []) if card.get("recipeId") in RECIPE_FIELDS}
    if set(cards) != set(RECIPE_FIELDS):
        failures.append("compiled KJSGen project is missing planetary recipes")
        return
    type_map = {
        "crushing": "kjsgen:create_crushing", "mekanism_enriching": "kjsgen:mekanism_enriching",
        "tfmg_vat": "industrial_colonies:tfmg_chemical_vat", "pressing": "kjsgen:create_pressing",
        "mechanical_crafting": "kjsgen:create_mechanical_crafting",
    }
    for recipe_id, expected in RECIPE_FIELDS.items():
        card = cards[recipe_id]
        if card.get("type") != type_map[expected["type"]] or card.get("replaceRecipe") is not False:
            failures.append(f"{recipe_id} compiled type/replacement mode drifted")
    for recipe_id, tag, grit in (
        (DESH_FEED, "industrial_colonies:desh_crushing_feed", "industrial_colonies:desh_grit"),
        (OSTRUM_FEED, "industrial_colonies:ostrum_crushing_feed", "industrial_colonies:ostrum_grit"),
    ):
        slots = cards[recipe_id].get("slots", {})
        if slots.get("input") != {"kind": "ITEM_TAG", "id": tag} or slots.get("output0") != {"kind": "ITEM", "id": grit, "count": 1}:
            failures.append(f"{recipe_id} compiled one-grit feed contract drifted")
    vat_contracts = {
        DESH_LEACH: ({"vatMode": "steel", "machineMode": "mixing", "heat": "none", "minSize": "3", "processingTime": "200"}, 250, 750),
        DESH_REDUCE: ({"vatMode": "steel", "machineMode": "two_electrodes", "heat": "heated", "minSize": "3", "processingTime": "300"}, None, None),
        OSTRUM_LEACH: ({"vatMode": "firebrick", "machineMode": "mixing", "heat": "none", "minSize": "5", "processingTime": "400"}, 500, 1000),
        OSTRUM_REDUCE: ({"vatMode": "firebrick", "machineMode": "two_electrodes", "heat": "heated", "minSize": "5", "processingTime": "600"}, None, None),
    }
    for recipe_id, (params, acid, water) in vat_contracts.items():
        card = cards[recipe_id]
        if card.get("params") != params:
            failures.append(f"{recipe_id} compiled vat parameters drifted")
        slots = card.get("slots", {})
        if acid is not None and (slots.get("ingredients1", {}).get("id"), slots.get("ingredients1", {}).get("amount"), slots.get("ingredients2", {}).get("id"), slots.get("ingredients2", {}).get("amount")) != ("tfmg:sulfuric_acid", acid, "minecraft:water", water):
            failures.append(f"{recipe_id} compiled acid/water charge drifted")
    for recipe_id in (DESH_PLATE, OSTRUM_PLATE):
        if cards[recipe_id].get("slots", {}).get("__machine_process_pressing") != {"kind": "ITEM", "id": PRESS}:
            failures.append(f"{recipe_id} is no longer locked to the Refined Radiance press")
    if cards[MARS_NAV].get("params") != {"gridW": "5", "gridH": "5"} or len([key for key in cards[MARS_NAV].get("slots", {}) if key.startswith("cell_")]) != 25:
        failures.append("Mars Navigation Computer is no longer an exact 5x5 assembly")
    removals = payload.get("removals", [])
    compiled_ids = [entry.get("recipeId") for entry in removals]
    for recipe_id in EXACT_REMOVALS:
        exact = [entry for entry in removals if entry.get("recipeId") == recipe_id]
        if len(exact) != 1 or any(str(exact[0].get(field, "")).strip() for field in ("output", "input", "mod")):
            failures.append(f"compiled exact removal drifted: {recipe_id}")
    if PACKING_RECIPES.intersection(compiled_ids):
        failures.append("compiled KJSGen removals retire a preserved packing recipe")


def validate_manifest(path: Path, failures: list[str]) -> None:
    payload = load_json(path)
    for recipe_id, expected in RECIPE_FIELDS.items():
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


def validate_catalog(catalog: Path, mods: Path | None, failures: list[str]) -> None:
    recipes_path = catalog / "recipes.csv"
    items_path = catalog / "items.csv"
    if not recipes_path.is_file() or not items_path.is_file():
        failures.append(f"registry catalog is incomplete: {catalog}")
        return
    with recipes_path.open(encoding="utf-8-sig", newline="") as handle:
        recipes = {row.get("recipe_id", ""): row for row in csv.DictReader(handle)}
    missing_recipes = sorted((EXACT_REMOVALS | PACKING_RECIPES) - set(recipes))
    if missing_recipes:
        failures.append(f"installed catalog is missing pinned planetary stock recipes: {missing_recipes}")
    with items_path.open(encoding="utf-8-sig", newline="") as handle:
        items = {row.get("item_id", "") for row in csv.DictReader(handle)}
    expected_items = {
        "rocketnautics_addon:mars_desh_ore", "rocketnautics_addon:raw_desh",
        "ad_astra:raw_desh", "ad_astra:raw_ostrum", "ad_astra:desh_ingot", "ad_astra:desh_plate",
        "ad_astra:ostrum_ingot", "ad_astra:ostrum_plate", PRESS,
        "computercraft:monitor_advanced", "computercraft:computer_advanced",
        "ae2:engineering_processor", "tfmg:etched_circuit_board", "tfmg:circuit_board",
        "simulated:navigation_table", "industrial_colonies:orbital_flight_computer",
    }
    missing_items = sorted(expected_items - items - {"industrial_colonies:orbital_flight_computer"})
    if missing_items:
        failures.append(f"installed item registry is missing planetary ingredients: {missing_items}")
    if mods is not None:
        jar_name = recipes.get("ad_astra:desh_ingot", {}).get("source_jar", "")
        jar = mods / jar_name
        if not jar.is_file():
            failures.append(f"Ad Astra texture source JAR is missing: {jar}")
        else:
            with zipfile.ZipFile(jar) as archive:
                names = set(archive.namelist())
            for texture in MODEL_TEXTURES.values():
                texture_path = f"assets/{texture.replace(':', '/textures/')}.png"
                if texture_path not in names:
                    failures.append(f"external model texture is absent from installed Ad Astra JAR: {texture}")


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
) -> list[str]:
    failures: list[str] = []
    required = (
        SEED, ASSIGNMENTS, QUESTS, NATIVE_CHAPTER, ITEMS_JAVA, LANG,
        DESH_FEED_TAG, OSTRUM_FEED_TAG, *MOON_LOOT,
        *(relative for relative, _ in ADVANCEMENTS.values()),
        *STRUCTURE_RESOURCES,
        *(MODEL_DIR / f"{name}.json" for name in CUSTOM_ITEMS),
    )
    missing = [relative.as_posix() for relative in required if not (project / relative).is_file()]
    if missing:
        return [f"missing Planetary Industry source file: {relative}" for relative in missing]
    validate_recipe_source(project, failures)
    validate_tags_and_assets(project, failures)
    validate_assignments(project, failures)
    validate_loot(project, failures)
    validate_advancements(project, failures)
    validate_structure_overrides(project, mods, failures)
    validate_quests(project, failures)
    if manifest is not None:
        validate_manifest(manifest, failures)
    if compiled is not None:
        validate_compiled(compiled, failures)
    if catalog is not None:
        validate_catalog(catalog, mods, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--compiled", type=Path, default=COMPILED)
    parser.add_argument("--catalog", type=Path, default=default_catalog())
    parser.add_argument("--mods", type=Path, default=default_mods())
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
    )
    if failures:
        print("FAIL: Planetary Industry physical metallurgy slice is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("PASS: 11 managed planetary recipes retire 36 audited shortcuts; Desh and Ostrum retain packing, one-grit feed, TFMG vat, Refined Radiance plate, hard Moon loot, and observation-only quest contracts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
