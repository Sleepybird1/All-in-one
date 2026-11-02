#!/usr/bin/env python3
"""Generate deterministic, non-gating factory, exploration, and orbital guidance.

The generated book contains a physical-progression campaign from primitive
tools through electrical, digital, Mekanism, high-energy, and nuclear factory
work, plus the pre-existing three-item endgame capstone chain, an optional
dungeon-expedition chapter, and a compact post-Star orbital-engineering guide.
Tasks observe items, exact structures, or installed advancements. No rewards,
stage tasks, recipe locks, commands, or item consumption are emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GUIDANCE_SOURCE = PROJECT_ROOT / "progression" / "ftbquests_guidance_campaign.json"
DEFAULT_EXPLORATION_SOURCE = PROJECT_ROOT / "progression" / "ftbquests_dungeon_exploration.json"
DEFAULT_ENDGAME_SOURCE = PROJECT_ROOT / "progression" / "industrial_megaprojects.json"
DEFAULT_ORBITAL_SOURCE = PROJECT_ROOT / "progression" / "ftbquests_orbital_engineering.json"
DEFAULT_PLANETARY_SOURCE = PROJECT_ROOT / "progression" / "ftbquests_planetary_industry.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "pack-config-overrides" / "ftbquests" / "quests"
DEFAULT_MANIFEST = PROJECT_ROOT.parent / "industrial-audit" / "ftb-quests-layout" / "native_quest_manifest.json"

SCHEMA_VERSION = 3
FTB_QUESTS_FILE_VERSION = 13
ID_SALT = "industrial_colonies/ftbquests/native/v1"
FILE_TRANSLATION_ID = "0000000000000001"
ENDGAME_FILENAME = "industrial_progression"
ENDGAME_TITLE = "Industrial Endgame"
ENDGAME_GUIDANCE_TAG = "industrial_colonies:endgame_guidance"
PHYSICAL_GUIDANCE_TAG = "industrial_colonies:physical_guidance"
EXPLORATION_GUIDANCE_TAG = "industrial_colonies:exploration_guidance"
EXPLORATION_FILENAME = "dungeon_exploration"
EXPLORATION_TITLE = "Dungeon Expeditions"
ORBITAL_FILENAME = "orbital_engineering"
ORBITAL_TITLE = "Orbital Engineering"
ORBITAL_GUIDANCE_TAG = "industrial_colonies:orbital_guidance"
PLANETARY_FILENAME = "planetary_industry"
PLANETARY_TITLE = "Planetary Industry"
PLANETARY_GUIDANCE_TAG = "industrial_colonies:planetary_guidance"
ORBITAL_OBSERVATION_BOUNDARY = (
    "This quest only observes the finished hardware; it consumes nothing and "
    "unlocks no recipe, research, stage, or destination."
)
EXPECTED_ORBITAL_PHASES = [
    "Orbital Authorization",
    "Modular Propulsion",
    "Habitat Readiness",
    "Orbital Construction",
    "Orbital Navigation",
    "Dockyard Interfaces",
    "Station Fabrication",
]
EXPECTED_ORBITAL_KEYS = [
    "orbital_flight_computer",
    "thruster_mount",
    "engine_pipes",
    "engine_nozzle",
    "hose_anchor",
    "habitat_life_support",
    "physics_assembler",
    "navigation_suite",
    "docking_connector",
    "station_materials",
]
EXPECTED_ORBITAL_DEPENDENCIES = {
    "orbital_flight_computer": ["industrial_progression:industrial_star"],
    "hose_anchor": ["orbital_flight_computer"],
    "engine_pipes": ["hose_anchor"],
    "engine_nozzle": ["engine_pipes"],
    "thruster_mount": ["engine_nozzle"],
    "habitat_life_support": ["thruster_mount"],
    "physics_assembler": ["thruster_mount", "habitat_life_support"],
    "navigation_suite": ["physics_assembler"],
    "docking_connector": ["navigation_suite"],
    "station_materials": ["docking_connector"],
}
EXPECTED_ORBITAL_ITEMS = {
    "orbital_flight_computer": "industrial_colonies:orbital_flight_computer",
    "thruster_mount": "rocketnautics:thruster_mount",
    "engine_pipes": "rocketnautics:engine_pipes",
    "engine_nozzle": "rocketnautics:engine_nozzle",
    "hose_anchor": "rocketnautics:hose_anchor",
    "habitat_life_support": "ad_astra:airlock",
    "physics_assembler": "simulated:physics_assembler",
    "navigation_suite": "simulated:navigation_table",
    "docking_connector": "simulated:docking_connector",
    "station_materials": "ad_astra:steel_plating",
}
EXPECTED_ORBITAL_TASK_ITEMS = {
    key: [item] for key, item in EXPECTED_ORBITAL_ITEMS.items()
}
EXPECTED_ORBITAL_TASK_ITEMS["habitat_life_support"] = [
    "ad_astra:oxygen_distributor",
    "ad_astra:oxygen_sensor",
    "ad_astra:vent",
    "ad_astra:airlock",
]
EXPECTED_ORBITAL_TASK_ITEMS["navigation_suite"] = [
    "simulated:velocity_sensor",
    "simulated:gimbal_sensor",
    "simulated:optical_sensor",
    "simulated:navigation_table",
    "rocketnautics:sputnik",
]
EXPECTED_ORBITAL_TASK_ITEMS["station_materials"] = [
    "ad_astra:steel_plating",
    "ad_astra:steel_panel",
    "ad_astra:cable_duct",
    "ad_astra:fluid_pipe_duct",
]
EXPECTED_ORBITAL_TASK_COUNTS = {
    key: [1] * len(items) for key, items in EXPECTED_ORBITAL_TASK_ITEMS.items()
}
EXPECTED_ORBITAL_TASK_COUNTS["docking_connector"] = [6]
EXPECTED_ORBITAL_TASK_COUNTS["station_materials"] = [128, 32, 16, 16]
EXPECTED_ORBITAL_QUEST_PHASES = {
    "orbital_flight_computer": "Orbital Authorization",
    "thruster_mount": "Modular Propulsion",
    "engine_pipes": "Modular Propulsion",
    "engine_nozzle": "Modular Propulsion",
    "hose_anchor": "Modular Propulsion",
    "habitat_life_support": "Habitat Readiness",
    "physics_assembler": "Orbital Construction",
    "navigation_suite": "Orbital Navigation",
    "docking_connector": "Dockyard Interfaces",
    "station_materials": "Station Fabrication",
}
EXPECTED_PLANETARY_KEYS = [
    "moon_arrival",
    "desh_freight",
    "desh_metallurgy",
    "mars_navigation_computer",
    "mars_arrival",
    "ostrum_freight",
    "ostrum_metallurgy",
    "lunar_utility_array",
    "martian_service_reserve",
    "closed_loop_rations",
    "venus_expedition_package",
    "venus_arrival",
    "calorite_freight",
    "calorite_metallurgy",
    "mercury_arrival",
    "mercury_iron_sample",
    "asteroid_titanium",
    "asteroid_bulk_freight",
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
EXPECTED_PLANETARY_PHASES = [
    "Lunar Survey",
    "Lunar Freight",
    "Lunar Refining",
    "Mars Navigation",
    "Martian Survey",
    "Martian Freight",
    "Martian Refining",
    "Lunar Utilities",
    "Martian Services",
    "Closed-Loop Rations",
    "Venus Expedition",
    "Venus Survey",
    "Venusian Freight",
    "Venusian Refining",
    "Mercury Survey",
    "Mercury Freight",
    "Asteroid Prospecting",
    "Asteroid Freight",
    "Station Commissioning",
    "Gas-Giant Extraction",
    "Physical Condensate Return",
    "Interstellar Preparation",
    "Interstellar Materials",
    "Interstellar Navigation",
    "Interstellar Navigation",
    "Interstellar Propulsion",
    "Interstellar Propulsion",
    "Beyond Sol",
    "Beyond Sol",
]
EXPECTED_PLANETARY_DEPENDENCIES = {
    "moon_arrival": ["orbital_engineering:station_materials"],
    "desh_freight": ["moon_arrival"],
    "desh_metallurgy": ["desh_freight"],
    "mars_navigation_computer": ["desh_metallurgy"],
    "mars_arrival": ["mars_navigation_computer"],
    "ostrum_freight": ["mars_arrival"],
    "ostrum_metallurgy": ["ostrum_freight"],
    "lunar_utility_array": ["desh_metallurgy"],
    "martian_service_reserve": ["ostrum_metallurgy", "lunar_utility_array"],
    "closed_loop_rations": ["martian_service_reserve"],
    "venus_expedition_package": ["closed_loop_rations"],
    "venus_arrival": ["venus_expedition_package"],
    "calorite_freight": ["venus_arrival"],
    "calorite_metallurgy": ["calorite_freight"],
    "mercury_arrival": ["calorite_metallurgy"],
    "mercury_iron_sample": ["mercury_arrival"],
    "asteroid_titanium": ["mercury_iron_sample"],
    "asteroid_bulk_freight": ["asteroid_titanium"],
    "outer_station_services": ["asteroid_bulk_freight"],
    "gas_giant_extraction": ["outer_station_services"],
    "gas_giant_condensate_return": ["gas_giant_extraction"],
    "warp_charge_precursor": ["gas_giant_condensate_return"],
    "moon_crystal_stockpile": ["warp_charge_precursor"],
    "interstellar_navigation": ["moon_crystal_stockpile"],
    "signed_route_crystal": ["interstellar_navigation"],
    "warp_drive_core": ["signed_route_crystal"],
    "interstellar_warp_charge": ["warp_drive_core"],
    "glacio_arrival": ["interstellar_warp_charge"],
    "escaped_sol": ["glacio_arrival"],
}
EXPECTED_PLANETARY_TASKS = {
    "moon_arrival": [{
        "type": "advancement",
        "advancement": "industrial_colonies:planetary/moon_arrival",
        "criterion": "",
    }],
    "desh_freight": [{"type": "item", "item": "ad_astra:raw_desh", "count": 64}],
    "desh_metallurgy": [
        {"type": "item", "item": "industrial_colonies:desh_grit", "count": 1},
        {"type": "item", "item": "industrial_colonies:desh_concentrate", "count": 1},
        {"type": "item", "item": "industrial_colonies:desh_leached_compound", "count": 1},
        {"type": "item", "item": "ad_astra:desh_ingot", "count": 1},
        {"type": "item", "item": "ad_astra:desh_plate", "count": 1},
    ],
    "mars_navigation_computer": [{
        "type": "item",
        "item": "industrial_colonies:mars_navigation_computer",
        "count": 1,
    }],
    "mars_arrival": [{
        "type": "advancement",
        "advancement": "industrial_colonies:planetary/mars_arrival",
        "criterion": "",
    }],
    "ostrum_freight": [{"type": "item", "item": "ad_astra:raw_ostrum", "count": 64}],
    "ostrum_metallurgy": [
        {"type": "item", "item": "industrial_colonies:ostrum_grit", "count": 1},
        {"type": "item", "item": "industrial_colonies:ostrum_concentrate", "count": 1},
        {"type": "item", "item": "industrial_colonies:ostrum_leached_compound", "count": 1},
        {"type": "item", "item": "ad_astra:ostrum_ingot", "count": 1},
        {"type": "item", "item": "ad_astra:ostrum_plate", "count": 1},
    ],
    "lunar_utility_array": [
        {"type": "item", "item": "ad_astra:solar_panel", "count": 4},
        {"type": "item", "item": "ad_astra:water_pump", "count": 1},
        {"type": "item", "item": "ad_astra:gravity_normalizer", "count": 1},
    ],
    "martian_service_reserve": [
        {"type": "item", "item": "ad_astra:energizer", "count": 1},
        {"type": "item", "item": "mekanism:ultimate_energy_cube", "count": 1},
        {"type": "item", "item": "mekanism:ultimate_universal_cable", "count": 16},
    ],
    "closed_loop_rations": [
        {"type": "item", "item": "mekanism:nutritional_liquifier", "count": 1},
        {"type": "item", "item": "mekanism:canteen", "count": 4},
        {
            "type": "advancement",
            "advancement": "mekanism:full_canteen",
            "criterion": "",
        },
    ],
    "venus_expedition_package": [
        {"type": "item", "item": "industrial_colonies:venus_navigation_computer", "count": 1},
        {"type": "item", "item": "ad_astra:netherite_space_helmet", "count": 1},
        {"type": "item", "item": "ad_astra:netherite_space_suit", "count": 1},
        {"type": "item", "item": "ad_astra:netherite_space_pants", "count": 1},
        {"type": "item", "item": "ad_astra:netherite_space_boots", "count": 1},
    ],
    "venus_arrival": [{
        "type": "advancement",
        "advancement": "industrial_colonies:planetary/venus_arrival",
        "criterion": "",
    }],
    "calorite_freight": [{"type": "item", "item": "ad_astra:raw_calorite", "count": 64}],
    "calorite_metallurgy": [
        {"type": "item", "item": "industrial_colonies:calorite_grit", "count": 1},
        {"type": "item", "item": "industrial_colonies:calorite_concentrate", "count": 1},
        {"type": "item", "item": "industrial_colonies:calorite_leached_compound", "count": 1},
        {"type": "item", "item": "ad_astra:calorite_ingot", "count": 1},
        {"type": "item", "item": "ad_astra:calorite_plate", "count": 1},
    ],
    "mercury_arrival": [{
        "type": "advancement",
        "advancement": "industrial_colonies:planetary/mercury_arrival",
        "criterion": "",
    }],
    "mercury_iron_sample": [
        {"type": "item", "item": "ad_astra:mercury_iron_ore", "count": 1},
    ],
    "asteroid_titanium": [
        {"type": "item", "item": "rocketnautics:titanium_ore", "count": 1},
    ],
    "asteroid_bulk_freight": [
        {"type": "item", "item": "minecraft:coal_ore", "count": 64},
        {"type": "item", "item": "minecraft:iron_ore", "count": 64},
        {"type": "item", "item": "minecraft:copper_ore", "count": 64},
        {"type": "item", "item": "minecraft:gold_ore", "count": 32},
        {"type": "item", "item": "rocketnautics:titanium_ore", "count": 32},
    ],
    "outer_station_services": [{
        "type": "item",
        "item": "industrial_colonies:station_services_controller",
        "count": 1,
    }],
    "gas_giant_extraction": [{
        "type": "item",
        "item": "industrial_colonies:atmospheric_scoop",
        "count": 1,
    }],
    "gas_giant_condensate_return": [{
        "type": "item",
        "item": "industrial_colonies:gas_giant_condensate_bucket",
        "count": 8,
    }],
    "warp_charge_precursor": [{
        "type": "item",
        "item": "industrial_colonies:warp_charge_precursor",
        "count": 1,
    }],
    "moon_crystal_stockpile": [{
        "type": "item",
        "item": "cosmowarp:moon_crystal",
        "count": 8,
    }],
    "interstellar_navigation": [{
        "type": "item",
        "item": "industrial_colonies:interstellar_navigation_computer",
        "count": 1,
    }],
    "signed_route_crystal": [{
        "type": "item",
        "item": "cosmowarp:warp_crystal",
        "count": 1,
    }],
    "warp_drive_core": [{
        "type": "item",
        "item": "cosmowarp:warp_drive",
        "count": 1,
    }],
    "interstellar_warp_charge": [{
        "type": "item",
        "item": "industrial_colonies:interstellar_warp_charge",
        "count": 1,
    }],
    "glacio_arrival": [{
        "type": "advancement",
        "advancement": "industrial_colonies:planetary/glacio_arrival",
        "criterion": "",
    }],
    "escaped_sol": [{
        "type": "item",
        "item": "ad_astra:glacio_ice_shard_ore",
        "count": 1,
    }],
}
DESTINATION_SPECIFIC_PATTERN = re.compile(
    r"\b(?:moon|mars|mercury|venus|glacio)\b", re.IGNORECASE
)
EXPECTED_ENDGAME_KEYS = ["black_hole", "industrial_reserves", "industrial_star"]
EXPECTED_ENDGAME_DEPENDENCIES = {
    "black_hole": [],
    "industrial_reserves": ["black_hole"],
    "industrial_star": ["industrial_reserves"],
}
EXPECTED_ENDGAME_ITEMS = {
    "black_hole": "industrial_colonies:black_hole",
    "industrial_reserves": "industrial_colonies:industrial_reserve_core",
    "industrial_star": "industrial_colonies:industrial_star",
}
EXPECTED_GUIDANCE_PHASES = [
    "Primitive Start",
    "Mechanical Foundations",
    "Steam & Brass",
    "Steel & Petroleum",
]
EXPECTED_POST_DIESEL_CHAPTERS = [
    ("electrical_manufacturing", "Electrical Manufacturing", -80, 7, 17),
    ("digital_logistics", "Digital Logistics", -70, 6, 14),
    ("mekanized_industry", "Mekanized Industry", -60, 8, 22),
    ("high_energy_grid", "High-Energy Grid", -50, 10, 31),
    ("nuclear_engineering", "Nuclear Engineering", -40, 9, 20),
]
EXPECTED_POST_DIESEL_KEYS = [value[0] for value in EXPECTED_POST_DIESEL_CHAPTERS]
EXPECTED_ALL_GUIDANCE_PHASES = EXPECTED_GUIDANCE_PHASES + [
    value[1] for value in EXPECTED_POST_DIESEL_CHAPTERS
]
POST_DIESEL_BOUNDARY = (
    "This is a non-consuming observation task: keep the hardware in your factory; "
    "the recipe and machine chain remain the only progression authority."
)
EXPECTED_EXPLORATION_PHASES = [
    "Field Readiness",
    "Overworld Dungeons",
    "Deep Descent",
    "Rare Expeditions",
    "Nether Expedition",
]
EXPECTED_EXPLORATION_KEYS = [
    "field_lighting",
    "small_dungeon",
    "skeleton_dungeon",
    "spider_dungeon",
    "zombie_dungeon",
    "better_dungeons_survey",
    "dungeon_crawl_entrance",
    "salvaged_stone_pickaxe",
    "expedition_kit",
    "labyrinth_recon",
    "temple_recon",
    "small_nether_dungeon",
]
EXPECTED_EXPLORATION_DEPENDENCIES = {
    "field_lighting": [],
    "small_dungeon": ["field_lighting"],
    "skeleton_dungeon": ["field_lighting"],
    "spider_dungeon": ["field_lighting"],
    "zombie_dungeon": ["field_lighting"],
    "better_dungeons_survey": [
        "small_dungeon", "skeleton_dungeon", "spider_dungeon", "zombie_dungeon"
    ],
    "dungeon_crawl_entrance": ["field_lighting"],
    "salvaged_stone_pickaxe": ["dungeon_crawl_entrance"],
    "expedition_kit": ["field_lighting"],
    "labyrinth_recon": ["expedition_kit"],
    "temple_recon": ["expedition_kit"],
    "small_nether_dungeon": ["better_dungeons_survey"],
}
EXPECTED_EXPLORATION_TASKS = {
    "field_lighting": [{"type": "item", "item": "minecraft:torch", "count": 16}],
    "small_dungeon": [
        {"type": "structure", "structure": "betterdungeons:small_dungeon"}
    ],
    "skeleton_dungeon": [
        {"type": "structure", "structure": "betterdungeons:skeleton_dungeon"}
    ],
    "spider_dungeon": [
        {"type": "structure", "structure": "betterdungeons:spider_dungeon"}
    ],
    "zombie_dungeon": [
        {"type": "structure", "structure": "betterdungeons:zombie_dungeon"}
    ],
    "better_dungeons_survey": [
        {
            "type": "advancement",
            "advancement": "betterdungeons:all_dungeons",
            "criterion": "",
        }
    ],
    "dungeon_crawl_entrance": [
        {"type": "structure", "structure": "dungeoncrawl:dungeon"}
    ],
    "salvaged_stone_pickaxe": [
        {"type": "item", "item": "minecraft:stone_pickaxe", "count": 1}
    ],
    "expedition_kit": [
        {"type": "item", "item": "minecraft:shield", "count": 1},
        {"type": "item", "item": "minecraft:water_bucket", "count": 1},
    ],
    "labyrinth_recon": [
        {"type": "structure", "structure": "dungeonnowloading:labyrinth"}
    ],
    "temple_recon": [
        {"type": "structure", "structure": "dungeonnowloading:temple_of_duality"}
    ],
    "small_nether_dungeon": [
        {"type": "structure", "structure": "betterdungeons:small_nether_dungeon"}
    ],
}
FORBIDDEN_QUEST_FIELDS = {
    "command", "gamestage", "research_dependencies", "rewards", "stage", "team_stage"
}
FORBIDDEN_EXPLORATION_IDS = {
    "dungeonnowloading:chaotic_hexahedron",
    "dungeonnowloading:catalyzed_redstone",
    "dungeonnowloading:combustion_cell",
    "dungeonnowloading:labyrinth_trophy",
    "dungeonnowloading:temple_of_duality_trophy",
    "dungeonnowloading:story/labyrinth/awaken_chaos_spawner",
    "dungeonnowloading:story/labyrinth/obtain_chaotic_hexahedron",
    "dungeonnowloading:story/temple_of_duality/awaken_fairkeepers",
    "dungeonnowloading:story/temple_of_duality/obtain_catalyzed_redstone",
    "dungeonnowloading:story/temple_of_duality/obtain_combustion_cell",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def json_text(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def write_json_snbt(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_text(value), encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_code(kind: str, key: str) -> str:
    digest = hashlib.sha256(f"{ID_SALT}/{kind}/{key}".encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") & 0x7FFF_FFFF_FFFF_FFFF
    if value <= 1:
        value += 2
    return f"{value:016X}"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def require_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} must be non-empty")
    return text


def require_text_lines(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    return [require_text(line, label) for line in value]


def validate_item_tasks(tasks: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(tasks, list) or not tasks:
        raise ValueError(f"{label} must contain at least one item task")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(tasks):
        if not isinstance(raw, dict) or raw.get("type") != "item":
            raise ValueError(f"{label} task {index} must use type 'item'")
        unexpected = set(raw) - {"type", "item", "count"}
        if unexpected:
            raise ValueError(
                f"{label} task {index} contains unsupported fields {sorted(unexpected)}"
            )
        item = require_text(raw.get("item"), f"{label} task {index} item")
        if not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", item):
            raise ValueError(f"{label} task {index} has invalid item ID {item!r}")
        count = raw.get("count", 1)
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError(f"{label} task {index} count must be a positive integer")
        if item in seen:
            raise ValueError(f"{label} repeats item task {item}")
        seen.add(item)
        result.append({"type": "item", "item": item, "count": count})
    return result


def validate_exploration_tasks(tasks: Any, label: str) -> list[dict[str, Any]]:
    """Validate the deliberately small native-task vocabulary used for expeditions."""
    if not isinstance(tasks, list) or not tasks:
        raise ValueError(f"{label} must contain at least one observation task")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    registry_id_pattern = re.compile(r"[a-z0-9_.-]+:[a-z0-9_./-]+")
    for index, raw in enumerate(tasks):
        if not isinstance(raw, dict):
            raise ValueError(f"{label} task {index} must be an object")
        task_type = raw.get("type")
        if task_type == "item":
            unexpected = set(raw) - {"type", "item", "count"}
            item = require_text(raw.get("item"), f"{label} task {index} item")
            if not registry_id_pattern.fullmatch(item):
                raise ValueError(f"{label} task {index} has invalid item ID {item!r}")
            count = raw.get("count", 1)
            if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                raise ValueError(f"{label} task {index} count must be a positive integer")
            normalized = {"type": "item", "item": item, "count": count}
            identity = f"item:{item}"
        elif task_type == "structure":
            unexpected = set(raw) - {"type", "structure"}
            structure = require_text(
                raw.get("structure"), f"{label} task {index} structure"
            )
            if not registry_id_pattern.fullmatch(structure):
                raise ValueError(
                    f"{label} task {index} has invalid structure ID {structure!r}"
                )
            normalized = {"type": "structure", "structure": structure}
            identity = f"structure:{structure}"
        elif task_type == "advancement":
            unexpected = set(raw) - {"type", "advancement", "criterion"}
            advancement = require_text(
                raw.get("advancement"), f"{label} task {index} advancement"
            )
            if not registry_id_pattern.fullmatch(advancement):
                raise ValueError(
                    f"{label} task {index} has invalid advancement ID {advancement!r}"
                )
            criterion = raw.get("criterion", "")
            if not isinstance(criterion, str):
                raise ValueError(f"{label} task {index} criterion must be a string")
            normalized = {
                "type": "advancement",
                "advancement": advancement,
                "criterion": criterion,
            }
            identity = f"advancement:{advancement}:{criterion}"
        else:
            raise ValueError(
                f"{label} task {index} uses unsupported type {task_type!r}; "
                "only item, structure, and advancement are permitted"
            )
        if unexpected:
            raise ValueError(
                f"{label} task {index} contains unsupported fields {sorted(unexpected)}"
            )
        if identity in seen:
            raise ValueError(f"{label} repeats observation task {identity}")
        seen.add(identity)
        result.append(normalized)
    return result


def validate_dependency_graph(quests: list[dict[str, Any]], label: str) -> None:
    keys = [str(quest["key"]) for quest in quests]
    known = set(keys)
    if len(known) != len(keys):
        raise ValueError(f"{label} contains duplicate quest keys")
    graph: dict[str, list[str]] = {}
    for quest in quests:
        key = str(quest["key"])
        dependencies = quest["dependencies"]
        unknown = [dependency for dependency in dependencies if dependency not in known]
        if unknown:
            raise ValueError(f"{label}/{key} has unknown dependencies: {unknown}")
        if key in dependencies:
            raise ValueError(f"{label}/{key} depends on itself")
        graph[key] = dependencies
    state: dict[str, int] = {}

    def visit(key: str, stack: list[str]) -> None:
        current = state.get(key, 0)
        if current == 1:
            raise ValueError(f"{label} dependency cycle: {' -> '.join(stack + [key])}")
        if current == 2:
            return
        state[key] = 1
        for dependency in graph[key]:
            visit(dependency, stack + [key])
        state[key] = 2

    for key in keys:
        visit(key, [])


def validate_guidance_dependency_graph(chapters: list[dict[str, Any]]) -> None:
    """Validate local and cross-chapter guidance dependencies as one DAG."""
    graph: dict[str, list[str]] = {}
    for chapter in chapters:
        filename = str(chapter["filename"])
        for quest in chapter["quests"]:
            full_key = f"{filename}:{quest['key']}"
            if full_key in graph:
                raise ValueError(f"guidance contains duplicate quest key {full_key}")
            graph[full_key] = [
                dependency if ":" in dependency else f"{filename}:{dependency}"
                for dependency in quest["dependencies"]
            ]
    for full_key, dependencies in graph.items():
        unknown = [dependency for dependency in dependencies if dependency not in graph]
        if unknown:
            raise ValueError(f"guidance/{full_key} has unknown dependencies: {unknown}")
        if full_key in dependencies:
            raise ValueError(f"guidance/{full_key} depends on itself")
    state: dict[str, int] = {}

    def visit(key: str, stack: list[str]) -> None:
        current = state.get(key, 0)
        if current == 1:
            raise ValueError(f"guidance dependency cycle: {' -> '.join(stack + [key])}")
        if current == 2:
            return
        state[key] = 1
        for dependency in graph[key]:
            visit(dependency, stack + [key])
        state[key] = 2

    for key in graph:
        visit(key, [])
    roots = [key for key, dependencies in graph.items() if not dependencies]
    if roots != ["factory_foundations:crude_flint_pickaxe"]:
        raise ValueError(
            "the complete physical-guidance campaign must retain crude_flint_pickaxe "
            f"as its only root; found {roots}"
        )


def validate_guidance_chapter(
    chapter: dict[str, Any], allowed_phases: list[str]
) -> dict[str, Any]:
    filename = require_text(chapter.get("filename"), "guidance chapter filename")
    if chapter.get("key") != filename or not re.fullmatch(r"[a-z0-9_]+", filename):
        raise ValueError(f"guidance chapter key/filename mismatch: {filename!r}")
    require_text(chapter.get("title"), f"{filename} title")
    require_text_lines(chapter.get("subtitle"), f"{filename} subtitle")
    order_index = chapter.get("order_index")
    if isinstance(order_index, bool) or not isinstance(order_index, int):
        raise ValueError(f"{filename} order_index must be an integer")
    raw_quests = chapter.get("quests")
    if not isinstance(raw_quests, list) or not raw_quests:
        raise ValueError(f"{filename} must contain quests")
    quests: list[dict[str, Any]] = []
    phase_sequence: list[str] = []
    for raw in raw_quests:
        if not isinstance(raw, dict):
            raise ValueError(f"{filename} quests must be objects")
        key = require_text(raw.get("key"), f"{filename} quest key")
        if not re.fullmatch(r"[a-z0-9_]+", key):
            raise ValueError(f"invalid guidance quest key: {filename}:{key!r}")
        phase = require_text(raw.get("phase"), f"guidance/{filename}:{key} phase")
        if phase not in allowed_phases:
            raise ValueError(f"guidance/{filename}:{key} uses unknown phase {phase!r}")
        if not phase_sequence or phase_sequence[-1] != phase:
            phase_sequence.append(phase)
        dependencies = raw.get("dependencies")
        if (
            not isinstance(dependencies, list)
            or any(not isinstance(value, str) for value in dependencies)
            or len(set(dependencies)) != len(dependencies)
        ):
            raise ValueError(
                f"guidance/{filename}:{key} dependencies must be a non-repeating string list"
            )
        for coordinate in ("x", "y"):
            value = raw.get(coordinate)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"guidance/{filename}:{key} requires a numeric {coordinate} coordinate"
                )
        icon = require_text(raw.get("icon"), f"guidance/{filename}:{key} icon")
        if not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", icon):
            raise ValueError(f"guidance/{filename}:{key} has invalid icon {icon!r}")
        forbidden = FORBIDDEN_QUEST_FIELDS.intersection(raw)
        if forbidden:
            raise ValueError(
                f"guidance/{filename}:{key} contains forbidden fields {sorted(forbidden)}"
            )
        quest = dict(raw)
        quest["title"] = require_text(raw.get("title"), f"guidance/{filename}:{key} title")
        quest["subtitle"] = require_text(
            raw.get("subtitle"), f"guidance/{filename}:{key} subtitle"
        )
        quest["description"] = require_text_lines(
            raw.get("description"), f"guidance/{filename}:{key} description"
        )
        quest["tasks"] = validate_item_tasks(
            raw.get("tasks"), f"guidance/{filename}:{key}"
        )
        quests.append(quest)
    if phase_sequence != allowed_phases:
        raise ValueError(
            f"{filename} phases must appear once in order {allowed_phases}; found {phase_sequence}"
        )
    return dict(chapter, quests=quests)


def expand_post_diesel_chapters(
    source: Path, extension: Any
) -> tuple[list[dict[str, Any]], Path]:
    if not isinstance(extension, dict) or extension.get("status") != "implemented":
        raise ValueError("guidance chapter_extension must be an implemented object")
    if extension.get("chapter_keys") != EXPECTED_POST_DIESEL_KEYS:
        raise ValueError(
            f"guidance chapter_extension keys must remain {EXPECTED_POST_DIESEL_KEYS}"
        )
    extension_path = Path(require_text(extension.get("path"), "chapter_extension path"))
    if not extension_path.is_absolute():
        extension_path = (source.parent / extension_path).resolve()
    plan = load_json(extension_path)
    if (
        not isinstance(plan, dict)
        or plan.get("schema_version") != 1
        or plan.get("status") != "implemented"
        or plan.get("plan_id") != "ftb_post_diesel_guidance_campaign"
    ):
        raise ValueError("post-Diesel guidance plan must be the implemented schema-1 audit plan")
    raw_chapters = plan.get("chapters")
    if not isinstance(raw_chapters, list) or [c.get("key") for c in raw_chapters] != EXPECTED_POST_DIESEL_KEYS:
        raise ValueError("post-Diesel guidance plan chapter order changed")
    expected_by_key = {value[0]: value for value in EXPECTED_POST_DIESEL_CHAPTERS}
    chapters: list[dict[str, Any]] = []
    quest_total = 0
    task_total = 0
    for raw_chapter in raw_chapters:
        if not isinstance(raw_chapter, dict):
            raise ValueError("post-Diesel chapters must be objects")
        key = str(raw_chapter["key"])
        _, phase, order_index, expected_quests, expected_tasks = expected_by_key[key]
        if raw_chapter.get("filename") != key or raw_chapter.get("order_index") != order_index:
            raise ValueError(f"post-Diesel chapter identity/order changed: {key}")
        entry_dependencies = raw_chapter.get("entry_dependencies")
        if not isinstance(entry_dependencies, list) or not entry_dependencies:
            raise ValueError(f"post-Diesel/{key} requires entry_dependencies")
        quests: list[dict[str, Any]] = []
        for raw_quest in raw_chapter.get("quests", []):
            if not isinstance(raw_quest, dict):
                raise ValueError(f"post-Diesel/{key} quests must be objects")
            local_dependencies = raw_quest.get("dependencies")
            external_dependencies = raw_quest.get("external_dependencies", [])
            if not isinstance(local_dependencies, list) or not isinstance(external_dependencies, list):
                raise ValueError(f"post-Diesel/{key}:{raw_quest.get('key')} dependencies must be lists")
            dependencies = list(local_dependencies)
            if not local_dependencies:
                dependencies.extend(entry_dependencies)
            dependencies.extend(external_dependencies)
            dependencies = list(dict.fromkeys(dependencies))
            tasks = [
                {"type": "item", "item": task["item"], "count": task.get("count", 1)}
                for task in raw_quest.get("tasks", [])
                if isinstance(task, dict)
            ]
            intent = require_text(
                raw_quest.get("intent"), f"post-Diesel/{key}:{raw_quest.get('key')} intent"
            )
            quests.append({
                "key": raw_quest.get("key"),
                "phase": phase,
                "title": raw_quest.get("title"),
                "subtitle": intent,
                "description": [intent, POST_DIESEL_BOUNDARY],
                "x": raw_quest.get("x"),
                "y": raw_quest.get("y"),
                "icon": tasks[0]["item"] if tasks else "minecraft:barrier",
                "dependencies": dependencies,
                "tasks": tasks,
            })
        chapter = {
            "key": key,
            "filename": key,
            "title": raw_chapter.get("title"),
            "subtitle": [
                f"Continue the physical factory campaign through {phase}.",
                "Quests observe installed hardware without consuming it or granting progression.",
            ],
            "order_index": order_index,
            "quests": quests,
        }
        validated = validate_guidance_chapter(chapter, [phase])
        found_tasks = sum(len(quest["tasks"]) for quest in validated["quests"])
        if len(validated["quests"]) != expected_quests or found_tasks != expected_tasks:
            raise ValueError(
                f"post-Diesel/{key} must contain {expected_quests} quests/{expected_tasks} tasks; "
                f"found {len(validated['quests'])}/{found_tasks}"
            )
        chapters.append(validated)
        quest_total += len(validated["quests"])
        task_total += found_tasks
    if (quest_total, task_total) != (40, 104):
        raise ValueError(
            f"post-Diesel guidance totals must remain 40 quests/104 tasks; found {quest_total}/{task_total}"
        )
    totals = plan.get("proposed_totals_after_implementation", {})
    if totals.get("total_chapters") != 8 or totals.get("total_quests") != 85 or totals.get("total_tasks") != 180:
        raise ValueError("post-Diesel plan total contract changed")
    return chapters, extension_path


def validate_guidance_source(source: Path) -> dict[str, Any]:
    config = load_json(source)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("ftbquests_guidance_campaign.json must use schema_version 1")
    campaign = config.get("campaign")
    if not isinstance(campaign, dict):
        raise ValueError("guidance campaign metadata must be an object")
    require_text(campaign.get("file_title"), "campaign file_title")
    require_text(campaign.get("purpose"), "campaign purpose")
    require_text_lines(campaign.get("verification_boundary"), "campaign verification_boundary")
    chapters = config.get("chapters")
    if not isinstance(chapters, list) or len(chapters) != 1:
        raise ValueError("the hand-authored guidance source must retain one Foundation chapter")
    foundation = chapters[0]
    if not isinstance(foundation, dict):
        raise ValueError("guidance Foundation chapter must be an object")
    if foundation.get("filename") != "factory_foundations" or foundation.get("key") != "factory_foundations":
        raise ValueError("the guidance chapter key and filename must remain factory_foundations")
    validated_foundation = validate_guidance_chapter(foundation, EXPECTED_GUIDANCE_PHASES)
    quests = validated_foundation["quests"]
    if len(quests) != 30 or quests[-1]["key"] != "diesel_engine_commissioning":
        raise ValueError("Factory Foundations must retain 30 quests ending at diesel_engine_commissioning")
    validate_dependency_graph(quests, "factory_foundations")
    if sum(not quest["dependencies"] for quest in quests) != 1:
        raise ValueError("Factory Foundations must have exactly one root quest")
    if not any(len(quest["dependencies"]) > 1 for quest in quests):
        raise ValueError("Factory Foundations must retain dependency convergence")
    dependent_counts = {str(quest["key"]): 0 for quest in quests}
    for quest in quests:
        for dependency in quest["dependencies"]:
            dependent_counts[dependency] += 1
    if not any(count > 1 for count in dependent_counts.values()):
        raise ValueError("Factory Foundations must retain a real branch")
    post_diesel, extension_path = expand_post_diesel_chapters(
        source, config.get("chapter_extension")
    )
    validated_chapters = [validated_foundation, *post_diesel]
    validate_guidance_dependency_graph(validated_chapters)
    phase_order = [
        phase
        for chapter in validated_chapters
        for phase in dict.fromkeys(quest["phase"] for quest in chapter["quests"])
    ]
    if phase_order != EXPECTED_ALL_GUIDANCE_PHASES:
        raise ValueError(
            f"complete guidance phase order changed: expected {EXPECTED_ALL_GUIDANCE_PHASES}; "
            f"found {phase_order}"
        )
    validated = dict(config)
    validated["chapters"] = validated_chapters
    validated["_chapter_extension_source"] = str(extension_path)
    return validated


def validate_exploration_source(source: Path) -> dict[str, Any]:
    config = load_json(source)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("ftbquests_dungeon_exploration.json must use schema_version 1")
    campaign = config.get("campaign")
    if not isinstance(campaign, dict):
        raise ValueError("exploration campaign metadata must be an object")
    require_text(campaign.get("purpose"), "exploration campaign purpose")
    require_text_lines(
        campaign.get("verification_boundary"),
        "exploration campaign verification_boundary",
    )
    chapter = config.get("chapter")
    if not isinstance(chapter, dict):
        raise ValueError("exploration chapter must be an object")
    filename = require_text(chapter.get("filename"), "exploration chapter filename")
    if (
        filename != EXPLORATION_FILENAME
        or chapter.get("key") != filename
        or chapter.get("title") != EXPLORATION_TITLE
    ):
        raise ValueError(
            "exploration chapter key, filename, and title must remain "
            f"{EXPLORATION_FILENAME!r}, {EXPLORATION_FILENAME!r}, and "
            f"{EXPLORATION_TITLE!r}"
        )
    require_text_lines(chapter.get("subtitle"), "exploration chapter subtitle")
    if chapter.get("order_index") != -90:
        raise ValueError("exploration chapter order_index must remain -90")
    raw_quests = chapter.get("quests")
    if not isinstance(raw_quests, list):
        raise ValueError("exploration chapter quests must be a list")
    keys = [str(raw.get("key", "")) for raw in raw_quests if isinstance(raw, dict)]
    if keys != EXPECTED_EXPLORATION_KEYS:
        raise ValueError(
            "exploration quest keys/order must remain "
            f"{EXPECTED_EXPLORATION_KEYS}; found {keys}"
        )

    quests: list[dict[str, Any]] = []
    phase_sequence: list[str] = []
    for raw in raw_quests:
        if not isinstance(raw, dict):
            raise ValueError("exploration quests must be objects")
        key = str(raw["key"])
        forbidden = FORBIDDEN_QUEST_FIELDS.intersection(raw)
        if forbidden:
            raise ValueError(
                f"exploration/{key} contains forbidden fields {sorted(forbidden)}"
            )
        phase = require_text(raw.get("phase"), f"exploration/{key} phase")
        if phase not in EXPECTED_EXPLORATION_PHASES:
            raise ValueError(f"exploration/{key} uses unknown phase {phase!r}")
        if not phase_sequence or phase_sequence[-1] != phase:
            phase_sequence.append(phase)
        dependencies = raw.get("dependencies")
        if (
            not isinstance(dependencies, list)
            or any(not isinstance(value, str) for value in dependencies)
            or len(set(dependencies)) != len(dependencies)
        ):
            raise ValueError(
                f"exploration/{key} dependencies must be a non-repeating string list"
            )
        if dependencies != EXPECTED_EXPLORATION_DEPENDENCIES[key]:
            raise ValueError(f"exploration/{key} dependencies changed")
        for coordinate in ("x", "y"):
            value = raw.get(coordinate)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"exploration/{key} requires a numeric {coordinate} coordinate"
                )
        icon = require_text(raw.get("icon"), f"exploration/{key} icon")
        if not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", icon):
            raise ValueError(f"exploration/{key} has invalid icon {icon!r}")
        quest = dict(raw)
        quest["title"] = require_text(raw.get("title"), f"exploration/{key} title")
        quest["subtitle"] = require_text(
            raw.get("subtitle"), f"exploration/{key} subtitle"
        )
        quest["description"] = require_text_lines(
            raw.get("description"), f"exploration/{key} description"
        )
        quest["tasks"] = validate_exploration_tasks(
            raw.get("tasks"), f"exploration/{key}"
        )
        if quest["tasks"] != EXPECTED_EXPLORATION_TASKS[key]:
            raise ValueError(f"exploration/{key} observation tasks changed")
        quest_text = json.dumps(
            {
                "title": quest["title"],
                "subtitle": quest["subtitle"],
                "description": quest["description"],
                "icon": icon,
                "tasks": quest["tasks"],
            },
            ensure_ascii=False,
        ).lower()
        if "apotheosis" in quest_text or re.search(r"\bboss(?:es)?\b", quest_text):
            raise ValueError(
                f"exploration/{key} must not contain Apotheosis or boss objectives"
            )
        quest_ids = {
            str(task.get("item") or task.get("structure") or task.get("advancement"))
            for task in quest["tasks"]
        }
        forbidden_ids = quest_ids.intersection(FORBIDDEN_EXPLORATION_IDS)
        if forbidden_ids:
            raise ValueError(
                f"exploration/{key} uses forbidden encounter IDs {sorted(forbidden_ids)}"
            )
        quests.append(quest)

    if phase_sequence != EXPECTED_EXPLORATION_PHASES:
        raise ValueError(
            "exploration phases must appear once in route order "
            f"{EXPECTED_EXPLORATION_PHASES}; found {phase_sequence}"
        )
    validate_dependency_graph(quests, filename)
    roots = [quest["key"] for quest in quests if not quest["dependencies"]]
    if roots != ["field_lighting"]:
        raise ValueError("exploration campaign must have field_lighting as its only root")
    dependent_counts = {str(quest["key"]): 0 for quest in quests}
    for quest in quests:
        for dependency in quest["dependencies"]:
            dependent_counts[dependency] += 1
    if max(dependent_counts.values(), default=0) < 2:
        raise ValueError("exploration campaign must retain its optional branches")
    if dependent_counts["salvaged_stone_pickaxe"] != 0:
        raise ValueError("random stone-pickaxe salvage must remain a dead-end observation")
    task_types = {
        str(quest["key"]): {str(task["type"]) for task in quest["tasks"]}
        for quest in quests
    }
    for quest in quests:
        if "structure" not in task_types[str(quest["key"])]:
            continue
        structure_dependencies = [
            dependency
            for dependency in quest["dependencies"]
            if "structure" in task_types[dependency]
        ]
        if structure_dependencies:
            raise ValueError(
                f"exploration/{quest['key']} cannot be hidden behind non-retroactive "
                f"structure tasks {structure_dependencies}"
            )
    validated = dict(config)
    validated["chapter"] = dict(chapter, quests=quests)
    return validated


def validate_orbital_source(source: Path) -> dict[str, Any]:
    """Validate the compact post-Star manual without turning it into a gate."""
    config = load_json(source)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("ftbquests_orbital_engineering.json must use schema_version 1")
    unexpected_top = set(config) - {"schema_version", "campaign", "chapter"}
    if unexpected_top:
        raise ValueError(
            f"orbital source contains unsupported top-level fields {sorted(unexpected_top)}"
        )
    campaign = config.get("campaign")
    if not isinstance(campaign, dict):
        raise ValueError("orbital campaign metadata must be an object")
    unexpected_campaign = set(campaign) - {"purpose", "verification_boundary"}
    if unexpected_campaign:
        raise ValueError(
            "orbital campaign contains unsupported metadata fields "
            f"{sorted(unexpected_campaign)}"
        )
    require_text(campaign.get("purpose"), "orbital campaign purpose")
    require_text_lines(
        campaign.get("verification_boundary"),
        "orbital campaign verification_boundary",
    )

    chapter = config.get("chapter")
    if not isinstance(chapter, dict):
        raise ValueError("orbital chapter must be an object")
    unexpected_chapter = set(chapter) - {
        "key", "filename", "title", "subtitle", "order_index", "quests"
    }
    if unexpected_chapter:
        raise ValueError(
            f"orbital chapter contains unsupported fields {sorted(unexpected_chapter)}"
        )
    if (
        chapter.get("key") != ORBITAL_FILENAME
        or chapter.get("filename") != ORBITAL_FILENAME
        or chapter.get("title") != ORBITAL_TITLE
    ):
        raise ValueError(
            "orbital chapter key, filename, and title must remain "
            f"{ORBITAL_FILENAME!r}, {ORBITAL_FILENAME!r}, and {ORBITAL_TITLE!r}"
        )
    require_text_lines(chapter.get("subtitle"), "orbital chapter subtitle")
    if chapter.get("order_index") != 10:
        raise ValueError("orbital chapter order_index must remain 10")
    raw_quests = chapter.get("quests")
    if not isinstance(raw_quests, list):
        raise ValueError("orbital chapter quests must be a list")
    keys = [str(raw.get("key", "")) for raw in raw_quests if isinstance(raw, dict)]
    if keys != EXPECTED_ORBITAL_KEYS:
        raise ValueError(
            f"orbital quest keys/order must remain {EXPECTED_ORBITAL_KEYS}; found {keys}"
        )

    allowed_quest_fields = {
        "key", "phase", "title", "subtitle", "description", "x", "y",
        "icon", "dependencies", "tasks",
    }
    quests: list[dict[str, Any]] = []
    phase_sequence: list[str] = []
    for raw in raw_quests:
        if not isinstance(raw, dict):
            raise ValueError("orbital quests must be objects")
        key = str(raw["key"])
        unexpected = set(raw) - allowed_quest_fields
        if unexpected:
            raise ValueError(
                f"orbital/{key} contains unsupported fields {sorted(unexpected)}"
            )
        forbidden = FORBIDDEN_QUEST_FIELDS.intersection(raw)
        if forbidden:
            raise ValueError(
                f"orbital/{key} contains forbidden fields {sorted(forbidden)}"
            )
        phase = require_text(raw.get("phase"), f"orbital/{key} phase")
        expected_phase = EXPECTED_ORBITAL_QUEST_PHASES[key]
        if phase != expected_phase:
            raise ValueError(
                f"orbital/{key} phase must remain {expected_phase!r}; found {phase!r}"
            )
        if not phase_sequence or phase_sequence[-1] != phase:
            phase_sequence.append(phase)
        dependencies = raw.get("dependencies")
        if dependencies != EXPECTED_ORBITAL_DEPENDENCIES[key]:
            raise ValueError(f"orbital/{key} dependencies changed")
        for coordinate in ("x", "y"):
            value = raw.get(coordinate)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"orbital/{key} requires a numeric {coordinate} coordinate")
        quest = dict(raw)
        quest["title"] = require_text(raw.get("title"), f"orbital/{key} title")
        quest["subtitle"] = require_text(raw.get("subtitle"), f"orbital/{key} subtitle")
        quest["description"] = require_text_lines(
            raw.get("description"), f"orbital/{key} description"
        )
        if ORBITAL_OBSERVATION_BOUNDARY not in quest["description"]:
            raise ValueError(f"orbital/{key} lost the non-gating observation boundary")
        quest["tasks"] = validate_item_tasks(raw.get("tasks"), f"orbital/{key}")
        expected_item = EXPECTED_ORBITAL_ITEMS[key]
        expected_task = [
            {"type": "item", "item": item, "count": count}
            for item, count in zip(
                EXPECTED_ORBITAL_TASK_ITEMS[key],
                EXPECTED_ORBITAL_TASK_COUNTS[key],
                strict=True,
            )
        ]
        if quest["tasks"] != expected_task:
            raise ValueError(f"orbital/{key} observation item changed")
        icon = require_text(raw.get("icon"), f"orbital/{key} icon")
        if icon != expected_item:
            raise ValueError(f"orbital/{key} icon must match its observed hardware")
        quest_text = json.dumps(
            {
                "title": quest["title"],
                "subtitle": quest["subtitle"],
                "description": quest["description"],
                "icon": icon,
            },
            ensure_ascii=False,
        )
        if DESTINATION_SPECIFIC_PATTERN.search(quest_text):
            raise ValueError(
                f"orbital/{key} contains a destination-specific objective reserved for later"
            )
        quests.append(quest)
    if phase_sequence != EXPECTED_ORBITAL_PHASES:
        raise ValueError(
            "orbital phases must appear once in route order "
            f"{EXPECTED_ORBITAL_PHASES}; found {phase_sequence}"
        )
    expected_route = [
        "industrial_progression:industrial_star",
        "orbital_flight_computer",
        "hose_anchor",
        "engine_pipes",
        "engine_nozzle",
    ]
    quest_by_key = {str(quest["key"]): quest for quest in quests}
    actual_route = [
        quest_by_key[key]["dependencies"][0]
        for key in (
            "orbital_flight_computer",
            "hose_anchor",
            "engine_pipes",
            "engine_nozzle",
            "thruster_mount",
        )
    ]
    if actual_route != expected_route:
        raise ValueError(
            f"orbital hardware route must follow physical manufacturing order {expected_route}"
        )
    validated = dict(config)
    validated["chapter"] = dict(chapter, quests=quests)
    return validated


def validate_planetary_source(source: Path) -> dict[str, Any]:
    """Validate destination observations without turning them into travel gates."""
    config = load_json(source)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("ftbquests_planetary_industry.json must use schema_version 1")
    if set(config) != {"schema_version", "campaign", "chapter"}:
        raise ValueError("planetary source contains unsupported top-level fields")
    campaign = config.get("campaign")
    if not isinstance(campaign, dict) or set(campaign) != {"purpose", "verification_boundary"}:
        raise ValueError("planetary campaign metadata fields changed")
    require_text(campaign.get("purpose"), "planetary campaign purpose")
    require_text_lines(
        campaign.get("verification_boundary"),
        "planetary campaign verification_boundary",
    )
    chapter = config.get("chapter")
    if not isinstance(chapter, dict):
        raise ValueError("planetary chapter must be an object")
    allowed_chapter_fields = {
        "key", "filename", "title", "subtitle", "order_index", "quests",
    }
    if set(chapter) - allowed_chapter_fields:
        raise ValueError("planetary chapter contains unsupported fields")
    if (
        chapter.get("key") != PLANETARY_FILENAME
        or chapter.get("filename") != PLANETARY_FILENAME
        or chapter.get("title") != PLANETARY_TITLE
        or chapter.get("order_index") != 20
    ):
        raise ValueError("Planetary Industry chapter identity/order changed")
    require_text_lines(chapter.get("subtitle"), "planetary chapter subtitle")
    raw_quests = chapter.get("quests")
    if not isinstance(raw_quests, list):
        raise ValueError("planetary chapter quests must be a list")
    keys = [str(raw.get("key", "")) for raw in raw_quests if isinstance(raw, dict)]
    if keys != EXPECTED_PLANETARY_KEYS:
        raise ValueError(
            f"planetary quest keys/order must remain {EXPECTED_PLANETARY_KEYS}; found {keys}"
        )
    allowed_fields = {
        "key", "phase", "title", "subtitle", "description", "x", "y",
        "icon", "dependencies", "tasks",
    }
    quests: list[dict[str, Any]] = []
    phases: list[str] = []
    for raw in raw_quests:
        if not isinstance(raw, dict):
            raise ValueError("planetary quests must be objects")
        key = str(raw["key"])
        unexpected = set(raw) - allowed_fields
        forbidden = FORBIDDEN_QUEST_FIELDS.intersection(raw)
        if unexpected or forbidden:
            raise ValueError(
                f"planetary/{key} contains unsupported fields {sorted(unexpected | forbidden)}"
            )
        phase = require_text(raw.get("phase"), f"planetary/{key} phase")
        phases.append(phase)
        if raw.get("dependencies") != EXPECTED_PLANETARY_DEPENDENCIES[key]:
            raise ValueError(f"planetary/{key} dependencies changed")
        for coordinate in ("x", "y"):
            value = raw.get(coordinate)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"planetary/{key} requires numeric {coordinate}")
        quest = dict(raw)
        quest["title"] = require_text(raw.get("title"), f"planetary/{key} title")
        quest["subtitle"] = require_text(raw.get("subtitle"), f"planetary/{key} subtitle")
        quest["description"] = require_text_lines(
            raw.get("description"), f"planetary/{key} description"
        )
        icon = require_text(raw.get("icon"), f"planetary/{key} icon")
        if not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", icon):
            raise ValueError(f"planetary/{key} has invalid icon {icon!r}")
        quest["tasks"] = validate_exploration_tasks(
            raw.get("tasks"), f"planetary/{key}"
        )
        if quest["tasks"] != EXPECTED_PLANETARY_TASKS[key]:
            raise ValueError(f"planetary/{key} observation tasks changed")
        if any(task["type"] not in {"item", "advancement"} for task in quest["tasks"]):
            raise ValueError(f"planetary/{key} may only observe items or advancements")
        text = json.dumps(quest["description"], ensure_ascii=False).lower()
        observes_without_consumption = any(
            phrase in text for phrase in ("consume nothing", "consumes nothing")
        )
        if not observes_without_consumption or (
            "no destination" not in text and "no recipe" not in text
        ):
            raise ValueError(f"planetary/{key} lost the non-gating observation boundary")
        quests.append(quest)
    if phases != EXPECTED_PLANETARY_PHASES:
        raise ValueError(
            f"planetary phases must remain {EXPECTED_PLANETARY_PHASES}; found {phases}"
        )
    local_keys = set(EXPECTED_PLANETARY_KEYS)
    for quest in quests:
        for dependency in quest["dependencies"]:
            if ":" not in dependency and dependency not in local_keys:
                raise ValueError(
                    f"planetary/{quest['key']} has unknown dependency {dependency}"
                )
    validated = dict(config)
    validated["chapter"] = dict(chapter, quests=quests)
    return validated


def validate_endgame_source(source: Path) -> dict[str, Any]:
    config = load_json(source)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("industrial_megaprojects.json must use schema_version 1")
    chapter = config.get("chapter", {})
    if chapter.get("filename") != ENDGAME_FILENAME:
        raise ValueError(f"endgame chapter filename must remain {ENDGAME_FILENAME!r}")
    if chapter.get("title") != ENDGAME_TITLE:
        raise ValueError(f"endgame chapter title must remain {ENDGAME_TITLE!r}")
    require_text_lines(chapter.get("subtitle"), "endgame chapter subtitle")
    quests = config.get("quests")
    if not isinstance(quests, list):
        raise ValueError("endgame quests must be a list")
    keys = [str(quest.get("key", "")) for quest in quests if isinstance(quest, dict)]
    if keys != EXPECTED_ENDGAME_KEYS:
        raise ValueError(f"endgame quest keys/order must remain {EXPECTED_ENDGAME_KEYS}, found {keys}")
    for raw in quests:
        key = str(raw["key"])
        if raw.get("dependencies") != EXPECTED_ENDGAME_DEPENDENCIES[key]:
            raise ValueError(f"endgame/{key} dependencies changed")
        tasks = validate_item_tasks(raw.get("tasks"), f"endgame/{key}")
        if tasks != [{"type": "item", "item": EXPECTED_ENDGAME_ITEMS[key], "count": 1}]:
            raise ValueError(f"endgame/{key} item task changed")
        for field in ("title", "subtitle", "icon"):
            require_text(raw.get(field), f"endgame/{key} {field}")
        require_text_lines(raw.get("description"), f"endgame/{key} description")
        if not isinstance(raw.get("x"), (int, float)) or not isinstance(raw.get("y"), (int, float)):
            raise ValueError(f"endgame/{key} requires numeric coordinates")
        forbidden = FORBIDDEN_QUEST_FIELDS.intersection(raw)
        if forbidden:
            raise ValueError(f"endgame/{key} contains forbidden fields {sorted(forbidden)}")
    return config


def add_chapter(
    *, chapter_config: dict[str, Any], quest_kind: str, task_kind: str,
    tag_root: str, translations: dict[str, Any], used_ids: dict[str, str],
    global_quest_ids: dict[str, str] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    filename = str(chapter_config["filename"])
    chapter_id = stable_code("chapter", filename)
    previous = used_ids.setdefault(chapter_id, f"chapter:{filename}")
    if previous != f"chapter:{filename}":
        raise ValueError(f"deterministic FTB ID collision: {chapter_id}: {previous}")
    translations[f"chapter.{chapter_id}.title"] = str(chapter_config["title"])
    translations[f"chapter.{chapter_id}.chapter_subtitle"] = list(chapter_config["subtitle"])
    quest_configs = chapter_config["quests"]
    quest_id_by_key = {
        str(quest["key"]): stable_code(quest_kind, f"{filename}/{quest['key']}")
        for quest in quest_configs
    }
    quests: list[dict[str, Any]] = []
    manifest_quests: list[dict[str, Any]] = []
    for quest_config in quest_configs:
        key = str(quest_config["key"])
        quest_id = quest_id_by_key[key]
        previous = used_ids.setdefault(quest_id, f"quest:{filename}/{key}")
        if previous != f"quest:{filename}/{key}":
            raise ValueError(f"deterministic FTB ID collision: {quest_id}: {previous}")
        tasks: list[dict[str, Any]] = []
        task_ids: list[str] = []
        for index, task_config in enumerate(quest_config["tasks"]):
            task_type = str(task_config["type"])
            task_id = stable_code(task_kind, f"{filename}/{key}/{index}/{task_type}")
            previous = used_ids.setdefault(task_id, f"task:{filename}/{key}/{index}")
            if previous != f"task:{filename}/{key}/{index}":
                raise ValueError(f"deterministic FTB ID collision: {task_id}: {previous}")
            task_ids.append(task_id)
            if task_type == "item":
                tasks.append({
                    "id": task_id, "type": "item",
                    "item": {"id": str(task_config["item"])},
                    "count": int(task_config.get("count", 1)),
                })
            elif task_type == "structure":
                tasks.append({
                    "id": task_id, "type": "structure",
                    "structure": str(task_config["structure"]),
                })
            elif task_type == "advancement":
                tasks.append({
                    "id": task_id, "type": "advancement",
                    "advancement": str(task_config["advancement"]),
                    "criterion": str(task_config.get("criterion", "")),
                })
            else:  # All source validators reject this before generation.
                raise ValueError(
                    f"{filename}/{key} task {index} has unsupported type {task_type!r}"
                )
        dependency_ids: list[str] = []
        for value in quest_config["dependencies"]:
            if ":" in value:
                if global_quest_ids is None or value not in global_quest_ids:
                    raise ValueError(f"{filename}/{key} has unresolved cross-chapter dependency {value}")
                dependency_ids.append(global_quest_ids[value])
            else:
                dependency_ids.append(quest_id_by_key[value])
        tags = [tag_root, f"{tag_root}/{key}"]
        phase = quest_config.get("phase")
        if phase:
            tags.insert(1, f"{tag_root}/phase/{slug(str(phase))}")
        quests.append({
            "id": quest_id, "x": float(quest_config["x"]), "y": float(quest_config["y"]),
            "icon": {"id": str(quest_config["icon"])}, "disable_toast": True,
            "tags": tags, "dependencies": dependency_ids, "tasks": tasks,
        })
        translations[f"quest.{quest_id}.title"] = str(quest_config["title"])
        translations[f"quest.{quest_id}.quest_subtitle"] = str(quest_config["subtitle"])
        translations[f"quest.{quest_id}.quest_desc"] = list(quest_config["description"])
        manifest_entry: dict[str, Any] = {
            "chapter": filename, "key": key, "phase": phase, "quest_id": quest_id,
            "task_ids": task_ids,
            "items": [
                {"id": str(task["item"]), "count": int(task.get("count", 1))}
                for task in quest_config["tasks"]
                if task["type"] == "item"
            ],
            "dependency_keys": list(quest_config["dependencies"]),
            "dependencies": dependency_ids,
        }
        structures = [
            str(task["structure"])
            for task in quest_config["tasks"]
            if task["type"] == "structure"
        ]
        advancements = [
            {
                "id": str(task["advancement"]),
                "criterion": str(task.get("criterion", "")),
            }
            for task in quest_config["tasks"]
            if task["type"] == "advancement"
        ]
        if structures:
            manifest_entry["structures"] = structures
        if advancements:
            manifest_entry["advancements"] = advancements
        manifest_quests.append(manifest_entry)
    chapter = {
        "id": chapter_id, "group": "", "order_index": int(chapter_config["order_index"]),
        "filename": filename, "default_quest_shape": "rsquare", "default_quest_size": 1.0,
        "default_hide_dependency_lines": False, "progression_mode": "default",
        "quests": quests, "quest_links": [], "images": [],
    }
    return chapter, manifest_quests


def build_artifacts(
    guidance_source: Path,
    endgame_source: Path,
    output: Path,
    exploration_source: Path = DEFAULT_EXPLORATION_SOURCE,
    orbital_source: Path = DEFAULT_ORBITAL_SOURCE,
    planetary_source: Path = DEFAULT_PLANETARY_SOURCE,
) -> tuple[dict[str, Any], dict[str, Any]]:
    guidance = validate_guidance_source(guidance_source)
    exploration = validate_exploration_source(exploration_source)
    endgame = validate_endgame_source(endgame_source)
    orbital = validate_orbital_source(orbital_source)
    planetary = validate_planetary_source(planetary_source)
    guidance_configs = guidance["chapters"]
    exploration_config = exploration["chapter"]
    orbital_config = orbital["chapter"]
    planetary_config = planetary["chapter"]
    translations: dict[str, Any] = {
        f"file.{FILE_TRANSLATION_ID}.title": str(guidance["campaign"]["file_title"])
    }
    used_ids: dict[str, str] = {}
    guidance_global_ids = {
        f"{chapter['filename']}:{quest['key']}": stable_code(
            "guidance_quest", f"{chapter['filename']}/{quest['key']}"
        )
        for chapter in guidance_configs
        for quest in chapter["quests"]
    }
    guidance_chapters: list[dict[str, Any]] = []
    guidance_quests: list[dict[str, Any]] = []
    for guidance_config in guidance_configs:
        guidance_chapter, chapter_quests = add_chapter(
            chapter_config=guidance_config,
            quest_kind="guidance_quest",
            task_kind="guidance_task",
            tag_root=PHYSICAL_GUIDANCE_TAG,
            translations=translations,
            used_ids=used_ids,
            global_quest_ids=guidance_global_ids,
        )
        guidance_chapters.append(guidance_chapter)
        guidance_quests.extend(chapter_quests)
    exploration_chapter, exploration_quests = add_chapter(
        chapter_config=exploration_config,
        quest_kind="exploration_quest",
        task_kind="exploration_task",
        tag_root=EXPLORATION_GUIDANCE_TAG,
        translations=translations,
        used_ids=used_ids,
    )
    # Keep the previously shipped endgame chapter's order as well as every ID,
    # task, and dependency. The new guidance chapter sorts before it at -100.
    endgame_config = {**endgame["chapter"], "order_index": 0, "quests": endgame["quests"]}
    endgame_chapter, endgame_quests = add_chapter(
        chapter_config=endgame_config, quest_kind="megaproject_quest", task_kind="megaproject_task",
        tag_root=ENDGAME_GUIDANCE_TAG, translations=translations, used_ids=used_ids,
    )
    endgame_global_ids = {
        f"{ENDGAME_FILENAME}:{key}": stable_code(
            "megaproject_quest", f"{ENDGAME_FILENAME}/{key}"
        )
        for key in EXPECTED_ENDGAME_KEYS
    }
    orbital_chapter, orbital_quests = add_chapter(
        chapter_config=orbital_config,
        quest_kind="orbital_quest",
        task_kind="orbital_task",
        tag_root=ORBITAL_GUIDANCE_TAG,
        translations=translations,
        used_ids=used_ids,
        global_quest_ids=endgame_global_ids,
    )
    orbital_global_ids = {
        f"{ORBITAL_FILENAME}:{key}": stable_code(
            "orbital_quest", f"{ORBITAL_FILENAME}/{key}"
        )
        for key in EXPECTED_ORBITAL_KEYS
    }
    planetary_chapter, planetary_quests = add_chapter(
        chapter_config=planetary_config,
        quest_kind="planetary_quest",
        task_kind="planetary_task",
        tag_root=PLANETARY_GUIDANCE_TAG,
        translations=translations,
        used_ids=used_ids,
        global_quest_ids=orbital_global_ids,
    )
    # Keep Dungeon Expeditions between Factory Foundations and the five later
    # factory chapters. Its -90 order and optional graph remain unchanged.
    chapters = [
        guidance_chapters[0],
        exploration_chapter,
        *guidance_chapters[1:],
        endgame_chapter,
        orbital_chapter,
        planetary_chapter,
    ]
    manifest_quests = (
        guidance_quests + exploration_quests + endgame_quests + orbital_quests
        + planetary_quests
    )
    data_snbt = {
        "version": FTB_QUESTS_FILE_VERSION,
        "default_reward_team": False,
        "default_consume_items": False,
        "default_autoclaim_rewards": "disabled",
        "default_quest_shape": "rsquare",
        "default_quest_disable_jei": False,
        "emergency_items_cooldown": 300,
        "drop_loot_crates": False,
        "disable_gui": False,
        "grid_scale": 0.5,
        "pause_game": False,
        "lock_message": "",
        "progression_mode": "linear",
        "detection_delay": 20,
        "show_lock_icons": True,
        "drop_book_on_death": False,
        "hide_excluded_quests": False,
        "fallback_locale": "en_us",
        "verify_on_load": True,
        "suppress_all_autoclaiming": True,
    }
    artifacts: dict[str, Any] = {
        "data.snbt": data_snbt,
        "chapter_groups.snbt": {"chapter_groups": []},
        "lang/en_us.snbt": translations,
    }
    for chapter in chapters:
        artifacts[f"chapters/{chapter['filename']}.snbt"] = chapter
    statistics = {
        "chapter_count": len(chapters),
        "quest_count": sum(len(chapter["quests"]) for chapter in chapters),
        "guidance_quest_count": sum(len(chapter["quests"]) for chapter in guidance_chapters),
        "exploration_quest_count": len(exploration_chapter["quests"]),
        "endgame_quest_count": len(endgame_chapter["quests"]),
        "orbital_quest_count": len(orbital_chapter["quests"]),
        "planetary_quest_count": len(planetary_chapter["quests"]),
        "dependency_count": sum(
            len(quest["dependencies"]) for chapter in chapters for quest in chapter["quests"]
        ),
        "item_task_count": sum(
            task["type"] == "item"
            for chapter in chapters for quest in chapter["quests"] for task in quest["tasks"]
        ),
        "structure_task_count": sum(
            task["type"] == "structure"
            for chapter in chapters for quest in chapter["quests"] for task in quest["tasks"]
        ),
        "advancement_task_count": sum(
            task["type"] == "advancement"
            for chapter in chapters for quest in chapter["quests"] for task in quest["tasks"]
        ),
        "total_task_count": sum(
            len(quest["tasks"])
            for chapter in chapters for quest in chapter["quests"]
        ),
        "stage_task_count": 0,
        "reward_count": 0,
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "mode": "physical_progression_guidance_campaign",
        "sources": [
            {"kind": "guidance", "path": str(guidance_source), "sha256": file_sha256(guidance_source)},
            {
                "kind": "guidance_extension",
                "path": guidance["_chapter_extension_source"],
                "sha256": file_sha256(Path(guidance["_chapter_extension_source"])),
            },
            {
                "kind": "exploration",
                "path": str(exploration_source),
                "sha256": file_sha256(exploration_source),
            },
            {"kind": "endgame", "path": str(endgame_source), "sha256": file_sha256(endgame_source)},
            {"kind": "orbital", "path": str(orbital_source), "sha256": file_sha256(orbital_source)},
            {"kind": "planetary", "path": str(planetary_source), "sha256": file_sha256(planetary_source)},
        ],
        "native_quest_root": str(output),
        "chapters": [
            {
                "id": str(chapter["id"]), "filename": str(chapter["filename"]),
                "title": str({
                    **{str(value["filename"]): str(value["title"]) for value in guidance_configs},
                    str(exploration_config["filename"]): str(exploration_config["title"]),
                    ENDGAME_FILENAME: ENDGAME_TITLE,
                    str(orbital_config["filename"]): str(orbital_config["title"]),
                    str(planetary_config["filename"]): str(planetary_config["title"]),
                }[str(chapter["filename"])]),
                "order_index": int(chapter["order_index"]), "quest_count": len(chapter["quests"]),
            }
            for chapter in chapters
        ],
        "authority": {
            "progression": "physical recipe inputs and machines",
            "ftbquests_completion_grants_progression": False,
            "items_consumed": False,
            "rewards_emitted": False,
            "stage_tasks_emitted": False,
            "recipe_unlocks_emitted": False,
        },
        "endgame_identity": {
            "chapter_id": stable_code("chapter", ENDGAME_FILENAME),
            "quest_ids": {
                key: stable_code("megaproject_quest", f"{ENDGAME_FILENAME}/{key}")
                for key in EXPECTED_ENDGAME_KEYS
            },
        },
        "statistics": statistics,
        "quests": manifest_quests,
    }
    return artifacts, manifest


def generate(
    guidance_source: Path,
    endgame_source: Path,
    output: Path,
    manifest_path: Path,
    exploration_source: Path = DEFAULT_EXPLORATION_SOURCE,
    orbital_source: Path = DEFAULT_ORBITAL_SOURCE,
    planetary_source: Path = DEFAULT_PLANETARY_SOURCE,
) -> dict[str, Any]:
    artifacts, manifest = build_artifacts(
        guidance_source, endgame_source, output, exploration_source, orbital_source,
        planetary_source,
    )
    for relative, value in artifacts.items():
        write_json_snbt(output / relative, value)
    write_json_snbt(manifest_path, manifest)
    stale_split_chapter = output / "chapters" / "industrial_megaprojects.snbt"
    if stale_split_chapter.is_file():
        stale_split_chapter.unlink()
    return manifest


def check_current(
    guidance_source: Path,
    endgame_source: Path,
    output: Path,
    manifest_path: Path,
    exploration_source: Path = DEFAULT_EXPLORATION_SOURCE,
    orbital_source: Path = DEFAULT_ORBITAL_SOURCE,
    planetary_source: Path = DEFAULT_PLANETARY_SOURCE,
) -> list[str]:
    artifacts, manifest = build_artifacts(
        guidance_source, endgame_source, output, exploration_source, orbital_source,
        planetary_source,
    )
    errors: list[str] = []
    found = {
        path.relative_to(output).as_posix() for path in output.rglob("*.snbt")
    } if output.is_dir() else set()
    if found != set(artifacts):
        errors.append(
            f"generated FTB Quest file set is stale; expected={sorted(artifacts)}, found={sorted(found)}"
        )
    for relative, value in artifacts.items():
        path = output / relative
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != json_text(value):
            errors.append(f"generated FTB Quest artifact is stale: {path}")
    if not manifest_path.is_file() or manifest_path.read_text(encoding="utf-8-sig") != json_text(manifest):
        errors.append(f"generated FTB Quest manifest is stale: {manifest_path}")
    return errors


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--campaign-source", type=Path, default=DEFAULT_GUIDANCE_SOURCE)
    parser.add_argument(
        "--exploration-source", type=Path, default=DEFAULT_EXPLORATION_SOURCE
    )
    parser.add_argument("--endgame-source", type=Path, default=DEFAULT_ENDGAME_SOURCE)
    parser.add_argument("--orbital-source", type=Path, default=DEFAULT_ORBITAL_SOURCE)
    parser.add_argument("--planetary-source", type=Path, default=DEFAULT_PLANETARY_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--graph", type=Path, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    project = args.project.resolve()
    guidance_source = (
        args.campaign_source.resolve() if args.campaign_source != DEFAULT_GUIDANCE_SOURCE
        else project / "progression" / "ftbquests_guidance_campaign.json"
    )
    exploration_source = (
        args.exploration_source.resolve()
        if args.exploration_source != DEFAULT_EXPLORATION_SOURCE
        else project / "progression" / "ftbquests_dungeon_exploration.json"
    )
    endgame_source = (
        args.source.resolve() if args.source is not None
        else (
            args.endgame_source.resolve() if args.endgame_source != DEFAULT_ENDGAME_SOURCE
            else project / "progression" / "industrial_megaprojects.json"
        )
    )
    orbital_source = (
        args.orbital_source.resolve()
        if args.orbital_source != DEFAULT_ORBITAL_SOURCE
        else project / "progression" / "ftbquests_orbital_engineering.json"
    )
    planetary_source = (
        args.planetary_source.resolve()
        if args.planetary_source != DEFAULT_PLANETARY_SOURCE
        else project / "progression" / "ftbquests_planetary_industry.json"
    )
    output = args.output.resolve() if args.output != DEFAULT_OUTPUT else project / "pack-config-overrides" / "ftbquests" / "quests"
    manifest_path = args.manifest.resolve()
    try:
        if args.check:
            errors = check_current(
                guidance_source,
                endgame_source,
                output,
                manifest_path,
                exploration_source,
                orbital_source,
                planetary_source,
            )
            if errors:
                print("FTB Quests generated artifacts are stale:")
                for error in errors:
                    print(f"- {error}")
                return 1
            _, manifest = build_artifacts(
                guidance_source,
                endgame_source,
                output,
                exploration_source,
                orbital_source,
                planetary_source,
            )
            stats = manifest["statistics"]
            print(
                f"FTB Quests generated artifacts are current: {stats['chapter_count']} chapters, "
                f"{stats['quest_count']} quests, {stats['total_task_count']} typed tasks."
            )
            return 0
        manifest = generate(
            guidance_source,
            endgame_source,
            output,
            manifest_path,
            exploration_source,
            orbital_source,
            planetary_source,
        )
    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"FTB Quests generation FAILED: {exc}")
        return 1
    stats = manifest["statistics"]
    print(
        f"Generated {stats['chapter_count']} chapters with {stats['quest_count']} non-gating quests, "
        f"{stats['item_task_count']} item tasks, {stats['structure_task_count']} structure tasks, "
        f"{stats['advancement_task_count']} advancement task, "
        f"{stats['dependency_count']} visual dependencies, "
        "0 stage tasks, and 0 rewards."
    )
    print(f"Quest root: {output}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
