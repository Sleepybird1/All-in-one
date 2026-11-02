#!/usr/bin/env python3
"""Validate the mined-metal shutdown and manufactured ATM currency graph."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT.parent / "industrial-audit"
AUDIT_JSON = AUDIT_ROOT / "ALLTHEMODIUM_CURRENCY_ROUTE_AUDIT.json"
AUDIT_MD = AUDIT_ROOT / "ALLTHEMODIUM_CURRENCY_ROUTE_AUDIT.md"
SCRIPT = ROOT / "pack-scripts" / "server_scripts" / "industrial_allthemodium_currency.js"
STAGES = ROOT / "tools" / "additional_recipe_stages.json"
RUNTIME_STAGES = (
    ROOT
    / "build"
    / "generated"
    / "recipeStages"
    / "data"
    / "industrial_colonies"
    / "progression"
    / "recipe_stages.json"
)
MANAGED_MANIFEST = ROOT / "progression" / "managed_recipe_overhaul.json"
COMPILED_MANAGED = ROOT / "pack-kjsgen" / "default.managed.json"
BUILD_GRADLE = ROOT / "build.gradle"
ASSIGNMENTS = ROOT / "progression" / "machine_node_assignments.json"
MODS_TOML = ROOT / "src" / "main" / "templates" / "META-INF" / "neoforge.mods.toml"
MIXINS = ROOT / "src" / "main" / "resources" / "industrial_colonies.mixins.json"
SMITHING_MIXIN = (
    ROOT
    / "src"
    / "main"
    / "java"
    / "dev"
    / "godpc"
    / "industrialcolonies"
    / "mixin"
    / "SmithingMenuMixin.java"
)

EXPECTED_JAR_SHA256 = "870004c1d6fbd0891ff322b9ff9e8d42c6aaa082ace7562e25948f1636b5c6f1"

METALS = {
    "allthemodium": {
        "node": "CR01 — Exotic Metallurgy",
        "forms": {
            "ingot": "allthemodium:allthemodium_ingot",
            "nugget": "allthemodium:allthemodium_nugget",
            "dust": "allthemodium:allthemodium_dust",
            "block": "allthemodium:allthemodium_block",
            "plate": "allthemodium:allthemodium_plate",
            "gear": "allthemodium:allthemodium_gear",
            "rod": "allthemodium:allthemodium_rod",
        },
    },
    "vibranium": {
        "node": "CR01 — Yellorium Refinement",
        "forms": {
            "ingot": "allthemodium:vibranium_ingot",
            "nugget": "allthemodium:vibranium_nugget",
            "dust": "allthemodium:vibranium_dust",
            "block": "allthemodium:vibranium_block",
            "plate": "allthemodium:vibranium_plate",
            "gear": "allthemodium:vibranium_gear",
            "rod": "allthemodium:vibranium_rod",
        },
    },
    "unobtainium": {
        "node": "CR01 — The Nuclear Age",
        "forms": {
            "ingot": "allthemodium:unobtainium_ingot",
            "nugget": "allthemodium:unobtainium_nugget",
            "dust": "allthemodium:unobtainium_dust",
            "block": "allthemodium:unobtainium_block",
            "plate": "allthemodium:unobtainium_plate",
            "gear": "allthemodium:unobtainium_gear",
            "rod": "allthemodium:unobtainium_rod",
        },
    },
}

ALLOYS = {
    "vibranium_allthemodium_alloy": {
        "ingot": "allthemodium:vibranium_allthemodium_alloy_ingot",
        "dust": "allthemodium:vibranium_allthemodium_alloy_dust",
        "block": "allthemodium:vibranium_allthemodium_alloy_block",
    },
    "unobtainium_allthemodium_alloy": {
        "ingot": "allthemodium:unobtainium_allthemodium_alloy_ingot",
        "dust": "allthemodium:unobtainium_allthemodium_alloy_dust",
        "block": "allthemodium:unobtainium_allthemodium_alloy_block",
    },
    "unobtainium_vibranium_alloy": {
        "ingot": "allthemodium:unobtainium_vibranium_alloy_ingot",
        "dust": "allthemodium:unobtainium_vibranium_alloy_dust",
        "block": "allthemodium:unobtainium_vibranium_alloy_block",
    },
}

METAL_ROUTE_SUFFIXES = (
    "synthesis",
    "dust_from_ingot",
    "ingot_from_dust",
    "nuggets_from_ingot",
    "ingot_from_nuggets",
    "block_from_ingots",
    "ingots_from_block",
    "plate",
    "gear",
    "rods",
)
ALLOY_ROUTE_SUFFIXES = (
    "synthesis",
    "dust_from_ingot",
    "ingot_from_dust",
    "block_from_ingots",
    "ingots_from_block",
)
MEKANISM_SUFFIXES = (
    "clump/from_ore",
    "clump/from_raw_block",
    "clump/from_raw_ore",
    "clump/from_shard",
    "crystal/from_slurry",
    "dirty_dust/from_clump",
    "dust/from_dirty_dust",
    "dust/from_ingot",
    "dust/from_ore",
    "dust/from_raw_block",
    "dust/from_raw_ore",
    "shard/from_crystal",
    "shard/from_ore",
    "shard/from_raw_block",
    "shard/from_raw_ore",
    "slurry/clean",
    "slurry/dirty/from_ore",
    "slurry/dirty/from_raw_block",
    "slurry/dirty/from_raw_ore",
)
TCONSTRUCT_TYPES = {
    "tconstruct:alloy",
    "tconstruct:casting_basin",
    "tconstruct:casting_table",
    "tconstruct:material",
    "tconstruct:material_fluid",
    "tconstruct:melting",
}
COMPRESSED_FAMILIES = {
    "allthemodium_block",
    "vibranium_block",
    "unobtainium_block",
    "raw_allthemodium_block",
    "raw_vibranium_block",
    "raw_unobtainium_block",
    "vibranium_allthemodium_alloy_block",
    "unobtainium_allthemodium_alloy_block",
    "unobtainium_vibranium_alloy_block",
}

SMITHING_EQUIPMENT = (
    "axe",
    "boots",
    "chestplate",
    "helmet",
    "hoe",
    "leggings",
    "mace",
    "pickaxe",
    "shovel",
    "sword",
)

WORLDGEN = (
    (
        "remove_allthemodium_overworld.json",
        "data/allthemodium/neoforge/biome_modifier/allthemodium/allthemodium.json",
        "minecraft:deep_dark",
        "allthemodium:allthemodium_ore",
    ),
    (
        "remove_allthemodium_mining_dimension.json",
        "data/allthemodium/neoforge/biome_modifier/allthemodium/dim_ores/ore_allthemodium.json",
        "#allthemodium:mining_features/mining_biomes",
        "allthemodium:allthemodium_mining",
    ),
    (
        "remove_allthemodium_other.json",
        "data/allthemodium/neoforge/biome_modifier/allthemodium/the_other/allthemodium.json",
        "#allthemodium:mining_features/other_features",
        "allthemodium:allthemodium_ore",
    ),
    (
        "remove_vibranium_nether.json",
        "data/allthemodium/neoforge/biome_modifier/allthemodium/vibranium.json",
        "#minecraft:is_nether",
        "allthemodium:vibranium_ore",
    ),
    (
        "remove_vibranium_other.json",
        "data/allthemodium/neoforge/biome_modifier/allthemodium/the_other/vibranium.json",
        "#allthemodium:mining_features/other_features",
        "allthemodium:other_vibranium_ore",
    ),
    (
        "remove_unobtainium_end.json",
        "data/allthemodium/neoforge/biome_modifier/allthemodium/unobtainium.json",
        "minecraft:end_highlands",
        "allthemodium:unobtainium_ore",
    ),
)

LOOT_TABLES = {
    "generic_loot.json": ("generic_loot", 8),
    "hallway_loot.json": ("hallway_loot", 10),
    "library_loot.json": ("library_loot", 12),
    "treasure_room.json": ("treasure_room", 18),
    "treasure_room_loot.json": ("treasure_room_loot", 18),
}


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def literal_strings(source: str, start: str, end: str) -> set[str]:
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), source, re.DOTALL)
    require(match is not None, f"missing source block beginning {start!r}")
    return set(re.findall(r"'([^']+)'", match.group(1)))


def collect_named_values(value: object) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "name" and isinstance(child, str) and ":" in child:
                names.add(child)
            names.update(collect_named_values(child))
    elif isinstance(value, list):
        for child in value:
            names.update(collect_named_values(child))
    return names


def sequence_machine_routing_errors(source: str) -> list[str]:
    """Reject tier-labelled ATM assemblies whose nested steps are still universal."""

    errors: list[str] = []
    try:
        helpers = source[
            source.index("const atmDeploying =") : source.index("ServerEvents.tags('item'")
        ]
        factory = source[source.index("const sequencedElement =") :]
    except ValueError:
        return ["ATM sequenced-assembly helper or factory block is missing"]

    for fragment, message in (
        (
            "type: `industrial_colonies:${tier}_deploying`",
            "ATM deploying helper is not routed to its exact Encased deployer",
        ),
        (
            "type: `industrial_colonies:${tier}_pressing`",
            "ATM pressing helper is not routed to its exact Encased press",
        ),
    ):
        if fragment not in helpers:
            errors.append(message)
    if "type: 'create:deploying'" in helpers or "type: 'create:pressing'" in helpers:
        errors.append("ATM sequenced-assembly helper contains a universal Create step")

    expected_calls = {
        "atmDeploying('weathered_iron'": 6,
        "atmPressing('weathered_iron'": 2,
        "atmDeploying('refined_radiance'": 3,
        "atmPressing('refined_radiance'": 1,
    }
    for fragment, expected in expected_calls.items():
        actual = factory.count(fragment)
        if actual != expected:
            errors.append(
                f"ATM exact-machine step count changed for {fragment}: expected {expected}, found {actual}"
            )
    return errors


def main() -> None:
    require(AUDIT_JSON.is_file() and AUDIT_MD.is_file(), "source currency audit is missing")
    audit = load_json(AUDIT_JSON)
    require(isinstance(audit, dict), "audit JSON root must be an object")
    require(audit.get("allthemodium_jar_sha256") == EXPECTED_JAR_SHA256, "audited ATM JAR hash changed")
    require(audit.get("counts", {}).get("recipes") == 413, "audited recipe census changed")
    require(audit.get("counts", {}).get("active_recipes") == 340, "audited active-recipe census changed")

    jar_path = Path(str(audit.get("allthemodium_jar", "")))
    if jar_path.is_file():
        require(
            hashlib.sha256(jar_path.read_bytes()).hexdigest() == EXPECTED_JAR_SHA256,
            "installed ATM JAR no longer matches the audited binary",
        )

    source = SCRIPT.read_text(encoding="utf-8")
    audit_forms = set(audit["forms"]["items"])
    stock_producer_ids = literal_strings(
        source,
        "const ATM_STOCK_PRODUCER_IDS = [",
        "]\n\nconst ATM_COMPRESSED_FAMILIES",
    )
    require(len(audit_forms) == 59, "audit must contain the expected 59 material/container forms")
    audited_stock_producer_ids = {
        recipe["recipe_id"]
        for recipe in audit["recipes"]
        if recipe.get("conditions_active")
        and recipe.get("source_jar", "").lower().startswith("allthemodium-")
        and not recipe.get("type", "").startswith("mekanism:")
        and set(recipe.get("result_refs") or []) & audit_forms
    }
    require(len(audited_stock_producer_ids) == 54,
            "audit no longer contains the expected 54 active non-Mekanism ATM producers")
    require(stock_producer_ids == audited_stock_producer_ids,
            "exact stock-producer shutdown IDs differ from the audited active recipe census")
    require("ATM_STOCK_PRODUCER_IDS.forEach(id => event.remove({ id: id }))" in source,
            "exact stock-producer recipe IDs are not removed")
    require(not re.search(r"event\.remove\s*\(\s*\{\s*output\s*:", source),
            "output-filter recipe removal is forbidden; use audited exact recipe IDs")

    source_compressed_families = literal_strings(
        source,
        "const ATM_COMPRESSED_FAMILIES = [",
        "]\n\nconst ATM_MEKANISM_PROCESSING_SUFFIXES",
    )
    require(source_compressed_families == COMPRESSED_FAMILIES, "compressed-family shutdown set changed")
    expected_compressed = {
        f"allthecompressed:{family}_{level}x"
        for family in COMPRESSED_FAMILIES
        for level in range(1, 10)
    }
    require(expected_compressed == set(audit["forms"]["compressed_storage_aliases"]),
            "81 audited AllTheCompressed aliases changed")
    require("level <= 9" in source, "all nine compression levels are not removed")
    require("event.remove({ id: `allthecompressed:compress/${family}_${level}x` })" in source,
            "exact AllTheCompressed compression recipe IDs are not removed")
    require("event.remove({ id: `allthecompressed:decompress/${family}_${level}x` })" in source,
            "exact AllTheCompressed decompression recipe IDs are not removed")
    audited_compressed_routes = {
        recipe["recipe_id"]
        for recipe in audit["recipes"]
        if recipe.get("conditions_active")
        and recipe.get("source_jar", "").lower().startswith("allthecompressed-")
    }
    expected_compressed_routes = {
        f"allthecompressed:{direction}/{family}_{level}x"
        for direction in ("compress", "decompress")
        for family in COMPRESSED_FAMILIES
        for level in range(1, 10)
    }
    require(len(expected_compressed_routes) == 162,
            "expected 162 exact ATM compression/decompression route IDs")
    require(audited_compressed_routes == expected_compressed_routes,
            "exact AllTheCompressed shutdown IDs differ from the audited route census")

    source_mek_suffixes = literal_strings(
        source,
        "const ATM_MEKANISM_PROCESSING_SUFFIXES = [",
        "]\n\nconst ATM_TCONSTRUCT_RECIPE_TYPES",
    )
    require(source_mek_suffixes == set(MEKANISM_SUFFIXES), "Mekanism shutdown suffixes changed")
    expected_mek_ids = {
        f"allthemodium:processing/{metal}/{suffix}"
        for metal in METALS
        for suffix in MEKANISM_SUFFIXES
    }
    audited_mek_ids = {
        recipe["recipe_id"]
        for recipe in audit["recipes"]
        if recipe.get("conditions_active")
        and re.match(r"^allthemodium:processing/(allthemodium|vibranium|unobtainium)/", recipe["recipe_id"])
    }
    require(len(expected_mek_ids) == 57, "expected 57 exact Mekanism shutdown IDs")
    require(expected_mek_ids == audited_mek_ids, "exact Mekanism processing shutdown differs from audit")
    require("allthemodium:processing/${metal.id}/${suffix}" in source,
            "exact Mekanism recipe IDs are not removed")

    source_tconstruct = literal_strings(
        source,
        "const ATM_TCONSTRUCT_RECIPE_TYPES = [",
        "]\n\nconst atmRepeatedItems",
    )
    audited_tconstruct_types = {
        recipe["type"]
        for recipe in audit["recipes"]
        if not recipe.get("conditions_active") and "tconstruct" in recipe.get("required_mods", [])
    }
    require(source_tconstruct == TCONSTRUCT_TYPES == audited_tconstruct_types,
            "TConstruct future-proof shutdown differs from the 69 audited conditional recipes")
    require("event.remove({ mod: 'allthemodium', type: type })" in source,
            "TConstruct recipe-type removal is not applied")

    active_acquisition_recipes = []
    all_disabled_results = audit_forms | expected_compressed
    for recipe in audit["recipes"]:
        if not recipe.get("conditions_active"):
            continue
        results = set(recipe.get("result_refs") or [])
        if results & all_disabled_results:
            active_acquisition_recipes.append(recipe["recipe_id"])
    require(len(active_acquisition_recipes) >= 200,
            "audit no longer exposes the expected stock/storage acquisition surface")
    active_sawing_acquisition = {
        recipe["recipe_id"]
        for recipe in audit["recipes"]
        if recipe.get("conditions_active")
        and "saw" in recipe.get("type", "").lower()
        and set(recipe.get("result_refs") or []) & all_disabled_results
    }
    require(not active_sawing_acquisition,
            "audit unexpectedly exposes an active sawing acquisition route")

    expected_stages: dict[str, str] = {}
    for metal, config in METALS.items():
        for suffix in METAL_ROUTE_SUFFIXES:
            expected_stages[f"industrial_colonies:currency/{metal}/{suffix}"] = config["node"]
    for alloy in ALLOYS:
        for suffix in ALLOY_ROUTE_SUFFIXES:
            expected_stages[f"industrial_colonies:currency/{alloy}/{suffix}"] = "CR01 — The Nuclear Age"
    require(len(expected_stages) == 45, "expected 45 exact factory/recycling route IDs")

    stages = load_json(STAGES)
    stage_entries = stages["recipes"]
    all_stage_ids = [entry["recipe_id"] for entry in stage_entries]
    require(len(all_stage_ids) == len(set(all_stage_ids)), "duplicate IDs exist in additional recipe stages")
    actual_stages = {
        entry["recipe_id"]: entry["node"]
        for entry in stage_entries
        if entry["recipe_id"].startswith("industrial_colonies:currency/")
    }
    require(actual_stages == expected_stages, "45 manufactured-currency routes are not exactly staged")

    expected_consumers: dict[str, str] = {
        "allthemodium:allthemodium_apple": "CR01 — Exotic Metallurgy",
        "allthemodium:allthemodium_carrot": "CR01 — Exotic Metallurgy",
        "allthemodium:smithing/vibranium_upgrade_smithing_template": "CR01 — Yellorium Refinement",
        "allthemodium:smithing/unobtainium_upgrade_smithing_template": "CR01 — The Nuclear Age",
        "allthemodium:teleport_pad": "CR01 — Spacial Storage Tech",
    }
    for metal, config in METALS.items():
        for equipment in SMITHING_EQUIPMENT:
            expected_consumers[
                f"allthemodium:smithing/{metal}_{equipment}_smithing"
            ] = config["node"]
    require(len(expected_consumers) == 35, "expected 35 staged stock ATM consumers")
    audited_stock_consumers = {
        recipe["recipe_id"]
        for recipe in audit["recipes"]
        if recipe.get("conditions_active")
        and (
            recipe["recipe_id"].startswith("allthemodium:smithing/")
            or recipe["recipe_id"]
            in {
                "allthemodium:allthemodium_apple",
                "allthemodium:allthemodium_carrot",
                "allthemodium:teleport_pad",
            }
        )
    }
    require(audited_stock_consumers == set(expected_consumers),
            "audited stock ATM consumer set changed")
    actual_consumers = {
        entry["recipe_id"]: entry["node"]
        for entry in stage_entries
        if entry["recipe_id"] in expected_consumers
    }
    require(actual_consumers == expected_consumers,
            "35 legacy stock-consumer provenance entries changed")

    build_source = BUILD_GRADLE.read_text(encoding="utf-8")
    require("mode   : 'physical_recipe_progression'" in build_source,
            "build no longer declares physical recipe progression")
    require("recipes: [:]" in build_source,
            "build no longer emits an empty physical-progression stage map")
    if RUNTIME_STAGES.is_file():
        runtime_stages = load_json(RUNTIME_STAGES)
        require(runtime_stages.get("mode") == "physical_recipe_progression",
                "generated runtime recipe-stage manifest is not in physical progression mode")
        require(runtime_stages.get("recipes") == {},
                "physical progression must not silently reactivate stock-consumer stages")

    physical_retirements = {
        "allthemodium:teleport_pad",
        *(
            f"allthemodium:smithing/{metal}_{equipment}_smithing"
            for metal in METALS
            for equipment in SMITHING_EQUIPMENT
        ),
    }
    require(len(physical_retirements) == 31,
            "expected 30 ATM equipment routes plus the Teleport Pad")
    managed = load_json(MANAGED_MANIFEST)
    compiled = load_json(COMPILED_MANAGED)
    managed_removals = {
        str(value)
        for value in managed.get("additional_removals", [])
        if isinstance(value, str)
    }
    for recipe in managed.get("recipes", []):
        if isinstance(recipe, dict):
            managed_removals.update(
                str(value)
                for value in recipe.get("remove", [])
                if isinstance(value, str)
            )
    compiled_removals = {
        str(entry.get("recipeId"))
        for entry in compiled.get("removals", [])
        if isinstance(entry, dict) and isinstance(entry.get("recipeId"), str)
    }
    require(physical_retirements <= managed_removals,
            "managed manifest does not physically retire all ATM gear/teleport routes")
    require(physical_retirements <= compiled_removals,
            "compiled KJSGen project does not physically retire all ATM gear/teleport routes")

    mixins = load_json(MIXINS)["mixins"]
    require("SmithingMenuMixin" in mixins, "SmithingMenu stage enforcement is not registered")
    smithing_source = SMITHING_MIXIN.read_text(encoding="utf-8")
    for fragment in (
        "RecipeStageGate.canUse(serverPlayer, this.selectedRecipe)",
        "this.resultSlots.setRecipeUsed(null)",
        "this.resultSlots.setItem(0, ItemStack.EMPTY)",
        "method = \"mayPickup\"",
        "callback.setReturnValue(false)",
    ):
        require(fragment in smithing_source, f"SmithingMenu fail-closed guard is missing: {fragment}")
    for metal in METALS:
        require(f"id: '{metal}'" in source, f"KubeJS metal route descriptor is missing: {metal}")
        require(
            f"'industrial_colonies:currency/{metal}/synthesis'" in source,
            f"element synthesis recipe is missing: {metal}",
        )
    for alloy in ALLOYS:
        require(f"id: '{alloy}'" in source, f"KubeJS alloy route descriptor is missing: {alloy}")
    for suffix in set(METAL_ROUTE_SUFFIXES) - {"synthesis"}:
        require(f".id(`${{root}}/{suffix}`)" in source, f"metal route template is missing: {suffix}")
    for suffix in ALLOY_ROUTE_SUFFIXES:
        require(f".id(`${{root}}/{suffix}`)" in source, f"alloy route template is missing: {suffix}")

    factory_source = source[source.index("const sequencedElement ="):]
    routing_errors = sequence_machine_routing_errors(source)
    require(not routing_errors, "; ".join(routing_errors))
    require("type: outerType" in factory_source, "element synthesis does not use a selected tier serializer")
    require("type: 'create:sequenced_assembly'" not in factory_source,
            "element synthesis falls back to native Create sequenced assembly")
    require(factory_source.count("industrial_colonies:weathered_iron_sequenced_assembly") == 2,
            "Allthemodium/Vibranium bootstrap is not exactly Weathered Iron tier")
    require(factory_source.count("industrial_colonies:refined_radiance_sequenced_assembly") == 1,
            "Unobtainium synthesis is not exactly Refined Radiance tier")
    require(factory_source.count("sequencedElement(") == 3,
            "expected exactly three element synthesis calls")
    require("type: 'create:mixing'" in factory_source, "alloy synthesis is not Create mixing")
    require("heat_requirement: 'superheated'" in factory_source, "alloy synthesis is not superheated")
    require("tconstruct:" not in factory_source.lower(), "factory recipes depend on TConstruct")
    require("allthemodium:piglich_heart" not in factory_source, "factory recipes depend on Piglich Hearts")
    require("molten_atm" not in factory_source, "factory recipes depend on dormant alloy fluids")
    require("minecraft:crafting" not in factory_source, "currency route uses a normal crafting recipe")
    require("minecraft:smelting" not in factory_source and "minecraft:blasting" not in factory_source,
            "currency route uses a furnace recipe")
    require("atmRepeatedItems(metal.ingot, 9)" in factory_source, "base block compression is not 9:1")
    require("count: 9, id: metal.ingot" in factory_source, "base block recovery is not 1:9")
    require("atmRepeatedItems(alloy.ingot, 9)" in factory_source, "alloy block compression is not 9:1")
    require("count: 9, id: alloy.ingot" in factory_source, "alloy block recovery is not 1:9")

    assignments = load_json(ASSIGNMENTS)["nodes"]
    for metal, config in METALS.items():
        unlocks = set(assignments[config["node"]]["unlocks"])
        require(set(config["forms"].values()) <= unlocks,
                f"manufactured {metal} forms lack unlock provenance at {config['node']}")
    nuclear_unlocks = set(assignments["CR01 — The Nuclear Age"]["unlocks"])
    for alloy, forms in ALLOYS.items():
        require(set(forms.values()) <= nuclear_unlocks, f"manufactured {alloy} forms lack Nuclear Age provenance")

    resource_root = ROOT / "src" / "main" / "resources"
    own_modifier_root = resource_root / "data" / "industrial_colonies" / "neoforge" / "biome_modifier"
    for own_name, override_rel, biome, feature in WORLDGEN:
        expected = {
            "type": "neoforge:remove_features",
            "biomes": biome,
            "features": feature,
            "step": "underground_ores",
        }
        own = load_json(own_modifier_root / own_name)
        override = load_json(resource_root / override_rel)
        require(own == expected, f"worldgen removal changed: {own_name}")
        require(override == expected, f"authoritative ATM biome modifier override changed: {override_rel}")

    loot_root = resource_root / "data" / "allthemodium" / "loot_table" / "chest"
    forbidden_loot = {
        "allthemodium:allthemodium_nugget",
        "allthemodium:vibranium_nugget",
    }
    audited_currency_loot = {
        Path(route["path"]).name
        for route in audit["nonrecipe_routes"]
        if route.get("kind") == "loot_table"
        and forbidden_loot <= set(route.get("direct_refs") or [])
    }
    require(audited_currency_loot == set(LOOT_TABLES), "five audited currency chest tables changed")
    for filename, (pool_name, max_rolls) in LOOT_TABLES.items():
        loot = load_json(loot_root / filename)
        require(len(loot.get("pools", [])) == 1, f"unexpected pool count in {filename}")
        pool = loot["pools"][0]
        require(pool.get("name") == pool_name, f"pool name changed in {filename}")
        require(pool.get("rolls") == {"min": 1, "max": max_rolls}, f"roll range changed in {filename}")
        names = collect_named_values(loot)
        require(not (names & forbidden_loot), f"dungeon currency remains in {filename}")
        require({"minecraft:book", "minecraft:diamond", "minecraft:emerald", "minecraft:netherite_chestplate"} <= names,
                f"non-currency dungeon rewards were not preserved in {filename}")

    metadata = MODS_TOML.read_text(encoding="utf-8")
    dependency = re.search(
        r'\[\[dependencies\.\$\{mod_id\}\]\]\s+modId="allthemodium"(.*?)(?=\[\[dependencies|\Z)',
        metadata,
        re.DOTALL,
    )
    require(dependency is not None, "Allthemodium is not a required mod dependency")
    require('type="required"' in dependency.group(0) and 'ordering="AFTER"' in dependency.group(0),
            "Allthemodium dependency must be required and ordered AFTER for resource overrides")

    print(
        "Allthemodium currency validation passed: "
        f"{len(active_acquisition_recipes)} audited active producers covered, "
        "57 exact Mekanism routes disabled, 81 compressed aliases disabled, "
        "162 compression/decompression recipes covered, 5 currency loot tables scrubbed, "
        "6 ore-placement paths removed twice, 45 exact Create factory/recycling recipes, "
        "30 stock equipment upgrades and the Teleport Pad physically retired, "
        "0 active sawing acquisitions, 0 TConstruct dependencies."
    )


if __name__ == "__main__":
    main()
