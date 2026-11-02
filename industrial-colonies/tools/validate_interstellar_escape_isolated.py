#!/usr/bin/env python3
"""Validate the complete deployable Stage 14 interstellar-escape contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]

SIGNED_ROUTE = Path("src/main/java/dev/godpc/industrialcolonies/space/SignedInterstellarRoute.java")
POLICY = Path("src/main/java/dev/godpc/industrialcolonies/space/InterstellarWarpPolicy.java")
TRANSACTION = Path("src/main/java/dev/godpc/industrialcolonies/space/InterstellarWarpTransaction.java")
REMOVAL_SCOPE = Path("src/main/java/dev/godpc/industrialcolonies/space/InterstellarWarpRemovalScope.java")
COMPUTER_BLOCK = Path("src/main/java/dev/godpc/industrialcolonies/space/InterstellarNavigationComputerBlock.java")
COMPUTER_BE = Path("src/main/java/dev/godpc/industrialcolonies/space/InterstellarNavigationComputerBlockEntity.java")
INITIATOR_SCOPE = Path("src/main/java/dev/godpc/industrialcolonies/space/InterstellarWarpInitiatorScope.java")
CRYSTAL_SLOT_ACCESS = Path("src/main/java/dev/godpc/industrialcolonies/space/WarpDriveCrystalSlotAccess.java")
FROZEN_CRYSTAL_HANDLER = Path("src/main/java/dev/godpc/industrialcolonies/space/FrozenWarpCrystalItemHandler.java")
WARP_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveMixin.java")
NETWORKING_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/CosmowarpNetworkingMixin.java")
WARP_BLOCK_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveBlockMixin.java")
WARP_MENU_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveMenuMixin.java")
WARP_CLICK_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveClickMixin.java")
CRYSTAL_OWNER_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/CosmowarpCrystalSlotOwnerMixin.java")
CRYSTAL_FREEZE_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/CosmowarpCrystalSlotFreezeMixin.java")
CAPABILITY_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/CosmowarpCapabilityMixin.java")
SABLE_REMOVAL_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/SableRemovalBoundaryMixin.java")
DEEP_SPACE_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/DeepSpaceInstanceMixin.java")
SPACEFLIGHT_AUTHORIZATION = Path("src/main/java/dev/godpc/industrialcolonies/space/SpaceflightAuthorization.java")
MAIN_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialColonies.java")
ITEMS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java")
BLOCKS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlocks.java")
BLOCK_ENTITIES_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlockEntities.java")
MIXINS_JSON = Path("src/main/resources/industrial_colonies.mixins.json")
BUILD_GRADLE = Path("build.gradle")
MODS_TOML = Path("src/main/templates/META-INF/neoforge.mods.toml")
LANG = Path("src/main/resources/assets/industrial_colonies/lang/en_us.json")
SEED = Path("progression/managed_recipe_overhaul.seed.json")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
COMPILED = Path("pack-kjsgen/default.managed.json")
ASSIGNMENTS = Path("progression/machine_node_assignments.json")
QUESTS = Path("progression/ftbquests_planetary_industry.json")
NATIVE_CHAPTER = Path("pack-config-overrides/ftbquests/quests/chapters/planetary_industry.snbt")
SPACE_BOUNDARY = Path("pack-scripts/server_scripts/industrial_space_entry_deferred.js")
PROXIMA = Path("src/main/resources/data/rocketnautics/universe_planets/proxima_centauri.json")
GLACIO = Path("src/main/resources/data/rocketnautics/universe_planets/glacio.json")
PHYSICS = Path("src/main/resources/data/industrial_colonies/dimension_physics/ad_astra_glacio.json")
CONFIGURED_ORE = Path("src/main/resources/data/industrial_colonies/worldgen/configured_feature/ad_astra_moon_crystal_ore.json")
PLACED_ORE = Path("src/main/resources/data/industrial_colonies/worldgen/placed_feature/ad_astra_moon_crystal_ore.json")
BIOME_MODIFIER = Path("src/main/resources/data/industrial_colonies/neoforge/biome_modifier/add_ad_astra_moon_crystal_ore.json")
ARRIVAL = Path("src/main/resources/data/industrial_colonies/advancement/planetary/glacio_arrival.json")
BLOCKSTATE = Path("src/main/resources/assets/industrial_colonies/blockstates/interstellar_navigation_computer.json")
BLOCK_MODEL = Path("src/main/resources/assets/industrial_colonies/models/block/interstellar_navigation_computer.json")
ITEM_MODEL = Path("src/main/resources/assets/industrial_colonies/models/item/interstellar_navigation_computer.json")
CHARGE_MODEL = Path("src/main/resources/assets/industrial_colonies/models/item/interstellar_warp_charge.json")
LOOT = Path("src/main/resources/data/industrial_colonies/loot_table/blocks/interstellar_navigation_computer.json")

REQUIRED_FILES = (
    SIGNED_ROUTE, POLICY, TRANSACTION, REMOVAL_SCOPE, COMPUTER_BLOCK, COMPUTER_BE, INITIATOR_SCOPE,
    CRYSTAL_SLOT_ACCESS, FROZEN_CRYSTAL_HANDLER,
    WARP_MIXIN, NETWORKING_MIXIN, WARP_BLOCK_MIXIN, WARP_MENU_MIXIN,
    WARP_CLICK_MIXIN, CRYSTAL_OWNER_MIXIN, CRYSTAL_FREEZE_MIXIN, CAPABILITY_MIXIN,
    SABLE_REMOVAL_MIXIN,
    DEEP_SPACE_MIXIN, SPACEFLIGHT_AUTHORIZATION, MAIN_JAVA,
    ITEMS_JAVA, BLOCKS_JAVA,
    BLOCK_ENTITIES_JAVA, MIXINS_JSON, BUILD_GRADLE, MODS_TOML, LANG, SEED, MANIFEST,
    COMPILED, ASSIGNMENTS, QUESTS, NATIVE_CHAPTER, SPACE_BOUNDARY,
    PROXIMA, GLACIO, PHYSICS, CONFIGURED_ORE, PLACED_ORE, BIOME_MODIFIER,
    ARRIVAL, BLOCKSTATE, BLOCK_MODEL, ITEM_MODEL, CHARGE_MODEL, LOOT,
)

OUTER_NODE = "CR02 — Outer Station Extraction"
OUTER_PHASE = "Outer System Industry"
INTERSTELLAR_NODE = "CR02 — Interstellar Escape"
INTERSTELLAR_PHASE = "Interstellar Escape"

RECIPE_IDS = [
    "industrial_colonies:interstellar/moon_crystal_polishing",
    "industrial_colonies:interstellar/navigation_computer",
    "industrial_colonies:interstellar/unsigned_route_crystal",
    "industrial_colonies:interstellar/warp_drive",
    "industrial_colonies:interstellar/warp_charge",
]
MANAGED_STOCK_REMOVALS = [
    "cosmowarp:moon_crystal_sanding",
    "cosmowarp:warp_crystal",
    "cosmowarp:warp_drive",
]
CATALOG_STOCK_RECIPES = {
    "cosmowarp:moon_crystal_sanding": {
        "recipe_type": "create:sandpaper_polishing",
        "source_jar": "cosmowarp-1.0.1.jar",
        "source_path": "data/cosmowarp/recipe/moon_crystal_sanding.json",
        "outputs": "cosmowarp:moon_crystal",
        "inputs": "cosmowarp:raw_moon_crystal",
    },
    "cosmowarp:warp_crystal": {
        "recipe_type": "minecraft:crafting_shaped",
        "source_jar": "cosmowarp-1.0.1.jar",
        "source_path": "data/cosmowarp/recipe/warp_crystal.json",
        "outputs": "cosmowarp:warp_crystal",
        "inputs": "cosmowarp:moon_crystal | rocketnautics:titanium_alloy_sheet",
    },
    "cosmowarp:warp_drive": {
        "recipe_type": "minecraft:crafting_shaped",
        "source_jar": "cosmowarp-1.0.1.jar",
        "source_path": "data/cosmowarp/recipe/warp_drive.json",
        "outputs": "cosmowarp:warp_drive",
        "inputs": "create:electron_tube | create:precision_mechanism | rocketnautics:titanium_casing",
    },
}
RECIPES: dict[str, dict[str, Any]] = {
    RECIPE_IDS[0]: {
        "node": OUTER_NODE,
        "phase": OUTER_PHASE,
        "order": 335,
        "type": "sandpaper_polishing",
        "input": "cosmowarp:raw_moon_crystal",
        "output": "cosmowarp:moon_crystal",
        "remove": ["cosmowarp:moon_crystal_sanding"],
        "exclusive_output": True,
    },
    RECIPE_IDS[1]: {
        "node": INTERSTELLAR_NODE,
        "phase": INTERSTELLAR_PHASE,
        "order": 360,
        "type": "mechanical_crafting",
        "pattern": ["CTQTC", "WAEAW", "QUSUQ", "WMRCW", "CTQTC"],
        "key": {
            "C": "ad_astra:calorite_plate",
            "T": "rocketnautics:titanium_alloy_sheet",
            "Q": "ae2:quantum_entangled_singularity",
            "W": "cosmowarp:moon_crystal",
            "A": "ae2:engineering_processor",
            "E": "mekanism:pellet_antimatter",
            "U": "mekanism:ultimate_control_circuit",
            "S": "industrial_colonies:station_services_controller",
            "M": "industrial_colonies:mercury_navigation_computer",
            "R": "computercraft:computer_advanced",
        },
        "output": "industrial_colonies:interstellar_navigation_computer",
        "depends_on": [
            "industrial_colonies:interstellar/moon_crystal_polishing",
            "industrial_colonies:outer_station/station_services_controller",
            "industrial_colonies:planetary/mercury/navigation_computer",
            "industrial_colonies:planetary/calorite/plate",
            "industrial_colonies:mekanism/ultimate_control_circuit",
        ],
    },
    RECIPE_IDS[2]: {
        "node": INTERSTELLAR_NODE,
        "phase": INTERSTELLAR_PHASE,
        "order": 370,
        "type": "mechanical_crafting",
        "pattern": ["TCTCT", "MQPQM", "CESEC", "MQNQM", "TCTCT"],
        "key": {
            "T": "rocketnautics:titanium_alloy_sheet",
            "C": "ad_astra:calorite_plate",
            "M": "cosmowarp:moon_crystal",
            "Q": "ae2:quantum_entangled_singularity",
            "P": "computercraft:computer_advanced",
            "E": "ae2:engineering_processor",
            "S": "industrial_colonies:industrial_star",
            "N": "mekanism:ultimate_control_circuit",
        },
        "output": "cosmowarp:warp_crystal",
        "remove": ["cosmowarp:warp_crystal"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:interstellar/moon_crystal_polishing",
            "industrial_colonies:planetary/calorite/plate",
            "industrial_colonies:space/orbital_flight_computer",
            "industrial_colonies:mekanism/ultimate_control_circuit",
        ],
    },
    RECIPE_IDS[3]: {
        "node": INTERSTELLAR_NODE,
        "phase": INTERSTELLAR_PHASE,
        "order": 380,
        "type": "mechanical_crafting",
        "pattern": ["TCHCT", "EUQUE", "HMDMH", "EQIQE", "TCHCT"],
        "key": {
            "T": "rocketnautics:titanium_casing",
            "C": "ad_astra:calorite_plate",
            "H": "tfmg:heavy_machinery_casing",
            "E": "mekanism:ultimate_energy_cube",
            "U": "mekanism:ultimate_control_circuit",
            "Q": "ae2:quantum_entangled_singularity",
            "M": "cosmowarp:moon_crystal",
            "D": "industrial_colonies:interstellar_navigation_computer",
            "I": "industrial_colonies:industrial_star",
        },
        "output": "cosmowarp:warp_drive",
        "remove": ["cosmowarp:warp_drive"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:interstellar/navigation_computer",
            "industrial_colonies:interstellar/moon_crystal_polishing",
            "industrial_colonies:mekanism/storage/ultimate_energy_cube",
            "industrial_colonies:mekanism/ultimate_control_circuit",
            "industrial_colonies:space/orbital_flight_computer",
        ],
    },
    RECIPE_IDS[4]: {
        "node": INTERSTELLAR_NODE,
        "phase": INTERSTELLAR_PHASE,
        "order": 390,
        "type": "sequenced_assembly",
        "input": "industrial_colonies:warp_charge_precursor",
        "transitional": "industrial_colonies:warp_charge_precursor",
        "output": "industrial_colonies:interstellar_warp_charge",
        "loops": 2,
        "steps": [
            {
                "op": "deploying",
                "ingredient": "cosmowarp:moon_crystal",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "rocketnautics:titanium_alloy_sheet",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "ad_astra:calorite_plate",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "mekanism:pellet_antimatter",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {"op": "pressing", "machine": "createcasing:refined_radiance_press"},
        ],
        "depends_on": [
            "industrial_colonies:outer_station/warp_charge_precursor",
            "industrial_colonies:interstellar/moon_crystal_polishing",
            "industrial_colonies:planetary/calorite/plate",
        ],
    },
}

OUTER_UNLOCKS = [
    "industrial_colonies:station_services_controller",
    "industrial_colonies:atmospheric_scoop",
    "industrial_colonies:gas_giant_condensate_bucket",
    "cosmowarp:moon_crystal",
    "industrial_colonies:warp_charge_precursor",
]
INTERSTELLAR_UNLOCKS = [
    "industrial_colonies:interstellar_navigation_computer",
    "cosmowarp:warp_crystal",
    "cosmowarp:warp_drive",
    "industrial_colonies:interstellar_warp_charge",
]

QUESTS_EXPECTED: dict[str, tuple[list[str], list[tuple[str, str, int]]]] = {
    "moon_crystal_stockpile": (
        ["warp_charge_precursor"],
        [("item", "cosmowarp:moon_crystal", 8)],
    ),
    "interstellar_navigation": (
        ["moon_crystal_stockpile"],
        [("item", "industrial_colonies:interstellar_navigation_computer", 1)],
    ),
    "signed_route_crystal": (
        ["interstellar_navigation"],
        [("item", "cosmowarp:warp_crystal", 1)],
    ),
    "warp_drive_core": (
        ["signed_route_crystal"],
        [("item", "cosmowarp:warp_drive", 1)],
    ),
    "interstellar_warp_charge": (
        ["warp_drive_core"],
        [("item", "industrial_colonies:interstellar_warp_charge", 1)],
    ),
    "glacio_arrival": (
        ["interstellar_warp_charge"],
        [("advancement", "industrial_colonies:planetary/glacio_arrival", 1)],
    ),
    "escaped_sol": (
        ["glacio_arrival"],
        [("item", "ad_astra:glacio_ice_shard_ore", 1)],
    ),
}

NATIVE_IDS = {
    "moon_crystal_stockpile": ("5A20D956586D084C", "5097C068C5C78806"),
    "interstellar_navigation": ("7F343A19CA0F7D0F", "51A2667238E1A0FE"),
    "signed_route_crystal": ("22EED3587C45B99C", "02EBB4B5B3C37DD7"),
    "warp_drive_core": ("58E1E15C513AB5E2", "02FD66CA23C5B3ED"),
    "interstellar_warp_charge": ("0D19C8883588B8E3", "6BB22E0D80607FE8"),
    "glacio_arrival": ("0FABE65FFACB1AD8", "7C0F76A27B868A68"),
    "escaped_sol": ("7B0B71BC10C43F7A", "38880055D73F264B"),
}

CANDIDATE_ENTRIES = {
    "dev/godpc/industrialcolonies/IndustrialColonies.class",
    "dev/godpc/industrialcolonies/IndustrialItems.class",
    "dev/godpc/industrialcolonies/IndustrialBlocks.class",
    "dev/godpc/industrialcolonies/IndustrialBlockEntities.class",
    "dev/godpc/industrialcolonies/space/SpaceflightAuthorization.class",
    "dev/godpc/industrialcolonies/space/SignedInterstellarRoute.class",
    "dev/godpc/industrialcolonies/space/SignedInterstellarRoute$Route.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpPolicy.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpPolicy$PendingAuthorization.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpPolicy$ChargeLocation.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpPolicy$VesselState.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpPolicy$VesselIdentity.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpPolicy$Authorization.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpTransaction.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpTransaction$PlayerSnapshot.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpRemovalScope.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpRemovalScope$State.class",
    "dev/godpc/industrialcolonies/space/InterstellarNavigationComputerBlock.class",
    "dev/godpc/industrialcolonies/space/InterstellarNavigationComputerBlockEntity.class",
    "dev/godpc/industrialcolonies/space/InterstellarWarpInitiatorScope.class",
    "dev/godpc/industrialcolonies/space/WarpDriveCrystalSlotAccess.class",
    "dev/godpc/industrialcolonies/space/FrozenWarpCrystalItemHandler.class",
    "dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveMixin.class",
    "dev/godpc/industrialcolonies/mixin/CosmowarpNetworkingMixin.class",
    "dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveBlockMixin.class",
    "dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveMenuMixin.class",
    "dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveClickMixin.class",
    "dev/godpc/industrialcolonies/mixin/CosmowarpCrystalSlotOwnerMixin.class",
    "dev/godpc/industrialcolonies/mixin/CosmowarpCrystalSlotFreezeMixin.class",
    "dev/godpc/industrialcolonies/mixin/CosmowarpCapabilityMixin.class",
    "dev/godpc/industrialcolonies/mixin/SableRemovalBoundaryMixin.class",
    "dev/godpc/industrialcolonies/mixin/DeepSpaceInstanceMixin.class",
    "dev/godpc/industrialcolonies/mixin/SubLevelWarperUserDataMixin.class",
    "industrial_colonies.mixins.json",
    "META-INF/neoforge.mods.toml",
    "data/rocketnautics/universe_planets/proxima_centauri.json",
    "data/rocketnautics/universe_planets/glacio.json",
    "data/industrial_colonies/dimension_physics/ad_astra_glacio.json",
    "data/industrial_colonies/worldgen/configured_feature/ad_astra_moon_crystal_ore.json",
    "data/industrial_colonies/worldgen/placed_feature/ad_astra_moon_crystal_ore.json",
    "data/industrial_colonies/neoforge/biome_modifier/add_ad_astra_moon_crystal_ore.json",
    "data/industrial_colonies/advancement/planetary/glacio_arrival.json",
    "data/industrial_colonies/loot_table/blocks/interstellar_navigation_computer.json",
    "assets/industrial_colonies/blockstates/interstellar_navigation_computer.json",
    "assets/industrial_colonies/models/block/interstellar_navigation_computer.json",
    "assets/industrial_colonies/models/item/interstellar_navigation_computer.json",
    "assets/industrial_colonies/models/item/interstellar_warp_charge.json",
    "assets/industrial_colonies/lang/en_us.json",
}

CANDIDATE_RESOURCE_SOURCES = {
    "industrial_colonies.mixins.json": MIXINS_JSON,
    "data/rocketnautics/universe_planets/proxima_centauri.json": PROXIMA,
    "data/rocketnautics/universe_planets/glacio.json": GLACIO,
    "data/industrial_colonies/dimension_physics/ad_astra_glacio.json": PHYSICS,
    "data/industrial_colonies/worldgen/configured_feature/ad_astra_moon_crystal_ore.json":
        CONFIGURED_ORE,
    "data/industrial_colonies/worldgen/placed_feature/ad_astra_moon_crystal_ore.json":
        PLACED_ORE,
    "data/industrial_colonies/neoforge/biome_modifier/add_ad_astra_moon_crystal_ore.json":
        BIOME_MODIFIER,
    "data/industrial_colonies/advancement/planetary/glacio_arrival.json": ARRIVAL,
    "data/industrial_colonies/loot_table/blocks/interstellar_navigation_computer.json": LOOT,
    "assets/industrial_colonies/blockstates/interstellar_navigation_computer.json": BLOCKSTATE,
    "assets/industrial_colonies/models/block/interstellar_navigation_computer.json": BLOCK_MODEL,
    "assets/industrial_colonies/models/item/interstellar_navigation_computer.json": ITEM_MODEL,
    "assets/industrial_colonies/models/item/interstellar_warp_charge.json": CHARGE_MODEL,
    "assets/industrial_colonies/lang/en_us.json": LANG,
}

SOURCE_COSMOWARP_DEPENDENCY = '''[[dependencies.${mod_id}]]
    modId="cosmowarp"
    type="required"
    reason="Provides the bytecode-pinned Warp Drive and route components used by the signed interstellar transaction."
    versionRange="[1.0.1,1.0.2)"
    ordering="AFTER"
    side="BOTH"'''

CANDIDATE_COSMOWARP_DEPENDENCY = '''[[dependencies.industrial_colonies]]
    modId="cosmowarp"
    type="required"
    reason="Provides the bytecode-pinned Warp Drive and route components used by the signed interstellar transaction."
    versionRange="[1.0.1,1.0.2)"
    ordering="AFTER"
    side="BOTH"'''

SOURCE_SPACE_DEPENDENCIES = (
    '''[[dependencies.${mod_id}]]
    modId="sable"
    type="required"
    reason="Indexes the Orbital Flight Computer aboard block-built moving spacecraft."
    versionRange="[2.0.3,2.1.0)"
    ordering="AFTER"
    side="BOTH"''',
    '''[[dependencies.${mod_id}]]
    modId="rocketnautics"
    type="required"
    reason="The first orbital transition requires a source-owned post-Star flight computer."
    versionRange="[26.08.307,26.09.0)"
    ordering="AFTER"
    side="BOTH"''',
    '''[[dependencies.${mod_id}]]
    modId="ad_astra"
    type="required"
    reason="Provides the canonical Moon and Mars surface dimensions used by the Rocketnautics destination bridge."
    versionRange="[1.16.22,1.17.0)"
    ordering="AFTER"
    side="BOTH"''',
    SOURCE_COSMOWARP_DEPENDENCY,
)
CANDIDATE_SPACE_DEPENDENCIES = tuple(
    block.replace("[[dependencies.${mod_id}]]", "[[dependencies.industrial_colonies]]")
    for block in SOURCE_SPACE_DEPENDENCIES
)

CANDIDATE_CLASS_MARKERS: dict[str, tuple[bytes, ...]] = {
    "dev/godpc/industrialcolonies/mixin/DeepSpaceInstanceMixin.class": (
        b"tick(Lnet/minecraft/server/MinecraftServer;)V",
        b"Ldev/devce/rocketnautics/api/orbit/AllowedTransfer;allowToDimension()Z",
        b"mayDescendToManagedPlanet",
        b"lastOrbiting",
    ),
    "dev/godpc/industrialcolonies/mixin/CosmowarpWarpDriveMixin.class": (
        b"beginWarp",
        b"executeWarp",
        b"authorizeStart",
        b"authorizeExecute",
        b"InterstellarWarpTransaction",
        b"chargingTargetId",
    ),
    "dev/godpc/industrialcolonies/mixin/CosmowarpNetworkingMixin.class": (
        b"lambda$handleSimpleAction$0",
        b"beginWarp",
        b"registerHere",
        b"setSelectedId",
        b"renamePoint",
        b"InterstellarWarpInitiatorScope",
    ),
    "dev/godpc/industrialcolonies/mixin/CosmowarpCapabilityMixin.class": (
        b"lambda$registerCapabilities$1",
        b"FrozenWarpCrystalItemHandler",
        b"WarpDriveBlockEntity",
    ),
    "dev/godpc/industrialcolonies/space/FrozenWarpCrystalItemHandler.class": (
        b"getStackInSlot",
        b"insertItem",
        b"extractItem",
        b"isCharging",
    ),
    "dev/godpc/industrialcolonies/space/SignedInterstellarRoute.class": (
        b"sol_glacio_v1",
        b"3075d9ba54e0d5aff1fcd3d799e9a3906df93fcc5f68ffa019db07d19f4903ec",
        b"ad_astra",
        b"glacio",
    ),
    "dev/godpc/industrialcolonies/space/InterstellarWarpTransaction.class": (
        b"WarpSubLevel",
        b"InterstellarWarpRemovalScope",
        b"Interstellar warp destination snapshot failed; no copy was attempted",
        b"Interstellar warp copy failed; cleanup safety assessment follows",
        b"Interstellar warp source identity could not be verified; cleanup is unsafe",
        b"sourceRemovalStarted",
        b"clear",
        b"rollbackNewDestinations",
        b"restorePlayers",
        b"cleanupFailures",
    ),
    "dev/godpc/industrialcolonies/space/InterstellarWarpRemovalScope.class": (
        b"ThreadLocal",
        b"begin",
        b"markRemovalStarted",
        b"sourceRemovalStarted",
        b"clear",
    ),
    "dev/godpc/industrialcolonies/mixin/SableRemovalBoundaryMixin.class": (
        b"removeSubLevel(IILdev/ryanhcode/sable/sublevel/storage/SubLevelRemovalReason;)V",
        b"getSubLevel",
        b"markRemovalStarted",
    ),
}

DEPENDENCY_PINS: dict[str, tuple[str, dict[str, str]]] = {
    "cosmowarp-1.0.1.jar": (
        "FCAEAD3D8D1FB7C21D9F8243B5305F3B8E0FCD6F90D25FEC0AED3EE46C8AC1BC",
        {
            "dev/waco0311/cosmowarp/block/entity/WarpDriveBlockEntity.class":
                "65E67791A2035B1AA12E649F60E894416659E152D45DE9F1D65DD1B891AF29C3",
            "dev/waco0311/cosmowarp/Cosmonauticswarpdrive.class":
                "65A76251BA81FE178BFF5AD159DD0BF76F77E7AD8041704E014C425EDC5D71EA",
            "dev/waco0311/cosmowarp/block/entity/WarpDriveBlockEntity$1.class":
                "6233D0DF43F78C1D3FA47FD90F36D5834F0F7DA54E03B2E005653B7ACE61B055",
            "dev/waco0311/cosmowarp/block/WarpDriveBlock.class":
                "08513334076335A19F2383FD5D4BC3C54A40A154B1B78FCF64E040A38CABC111",
            "dev/waco0311/cosmowarp/block/entity/WarpDriveBlockEntity$WarpResult.class":
                "D360B55B8DC2FF1BBD6AF3FD8AC810B05554FC3F1E8728BB0F3307EB846ABEF3",
            "dev/waco0311/cosmowarp/menu/WarpDriveMenu.class":
                "8E97D6BE0D7F20691B8D3ABDA60E0319CDB9BDB67DF97B67E544757944904914",
            "dev/waco0311/cosmowarp/data/WarpPoint.class":
                "59B14360A0E42E8A3E0664A27D3E6A9D55FF6799B89C0AB94DF27394CACCA7BA",
            "dev/waco0311/cosmowarp/registry/ModDataComponents.class":
                "AADC2501E97204C7352FB1C03F38240E463574D78BAD0BC4C75EDE45B53B82D0",
            "dev/waco0311/cosmowarp/registry/ModItems.class":
                "8427FA66718DD6800241D62174D78125588FEC867F88949D6F5116BD93947F7A",
            "dev/waco0311/cosmowarp/network/ModNetworking.class":
                "BB509424CB0E45C25C552C77CA55EC97A65E8A7A666419FABEE102B1B52E8FAA",
            "data/cosmowarp/recipe/moon_crystal_sanding.json":
                "467E982D78C31458D20EBA2DC0C04FCFC068269513ACFAF584DFD931E45B8C49",
            "data/cosmowarp/recipe/warp_crystal.json":
                "CA881460571A3FF6A6B7E54882312D361E216F4CF76F49465570899D6578EE9C",
            "data/cosmowarp/recipe/warp_drive.json":
                "2EC7AEC65797256A5C63A7201FBEAD623B8CDEB457F47715A425D9F860EBAFCA",
            "data/cosmowarp/worldgen/configured_feature/moon_crystal_ore.json":
                "60126E2C80203EF96C04A323CAED2CE438AA18AADEE3ADBF4592C6A79F065423",
            "data/cosmowarp/worldgen/placed_feature/moon_crystal_ore.json":
                "27D3A64F3E0C5F1473A131B9B2B66880486561F2D709FB89A6977665240B4D11",
            "data/cosmowarp/neoforge/biome_modifier/add_moon_crystal_ore.json":
                "15E56B3DE38FE1E6AF3554C9948F134FAE3E18ED537DBD2322A47970E7FCA78F",
            "assets/cosmowarp/textures/block/warp_drive.png":
                "EC9DAB98D246A4CD69E0E803AA63B706A53C0D761B7B7D1852038CA4D2688528",
            "assets/cosmowarp/textures/item/moon_crystal.png":
                "7C10D169A1944CEA2DB13BFE6ACEB28D809D8CE5168DDB637D53786A81B60773",
        },
    ),
    "cosmonautics-26.08.307.jar": (
        "3FD9DAC868400905A55164D2C9D74ABC2080AE3269CA51E54E1899874945973E",
        {
            "dev/egg/SubLevelWarper.class":
                "6A575CE4EB0843E43B902F1E0D2C8D8EF7E72D48C25B12D2B8659FCDC0F41DAE",
            "dev/devce/rocketnautics/content/orbit/DeepSpaceData.class":
                "38B9A5B4CC0BF2918B539DD41FCD33EA2008431F9FFEC6051E25096038D020A1",
            "dev/devce/rocketnautics/content/orbit/DeepSpaceInstance.class":
                "4E08E479D7BF7A53FA22B9D857A4C1BE37B34D813506C0AD7E3BDE312B72ED9C",
            "dev/devce/rocketnautics/api/orbit/AllowedTransfer.class":
                "4FB67547F82AA1BC4E7F4BDEE7A2877F7AC60EF1C0964FA66BFE5BF6140AEF65",
            "dev/devce/rocketnautics/content/orbit/universe/CubePlanet.class":
                "B50743580D27720E5DFB51BF34F9D86F4AC4E1AC72F977AA03525797CDE32B67",
        },
    ),
    "adastra-1.21.1-1.16.22-neoforge.jar": (
        "FAF21D02C71D2D5B5A671A746334ED18A9DDBA79A5A9D9BD95E93A1D9EE9EC86",
        {
            "data/ad_astra/tags/item/freeze_resistant_armor.json":
                "7211404DABA5AA1B65A357A3C777597B7344A5BDD03EF5EFF6486CD802C68141",
            "data/ad_astra/dimension/glacio.json":
                "0C04D70611E616F254BF7211E1E825DAFC8D8908781CF6DA85DB116C4FEBE1AA",
            "data/ad_astra/dimension/glacio_orbit.json":
                "0E870891E4E78354B2F4B12EC7B8577354600BFBC7CAA7057B99E0B5F7AC7254",
            "data/ad_astra/worldgen/biome/lunar_wastelands.json":
                "CB3FE6BC9CD685B414E941BAFBAEA4838991469F0D7100E96A6A41433606CAAF",
            "assets/ad_astra/models/item/glacio_ice_shard_ore.json":
                "2775EFBFB402F0FCBBFEB692E0AB0062CF39FDF3BE30B12040A71829450A4E1A",
        },
    ),
    "sable-neoforge-1.21.1-2.0.3.jar": (
        "DA6C3B66238586603D1DCAA2AFB012D36815FBCE0A2D5938FBB2936701D42279",
        {
            "dev/ryanhcode/sable/api/SubLevelHelper.class":
                "B1CD7AAF392320ECD08CADF385634E3C9E16BBD0082A1A25FBF7AE9B828D6B7B",
            "dev/ryanhcode/sable/api/block/BlockEntitySubLevelActor.class":
                "034DEEFC3FDEB1E938244032FB0609B6B0953D8156C35E4DE9CE203617B47B97",
            "dev/ryanhcode/sable/sublevel/SubLevel.class":
                "160AA58D14AE277470FC6B6AFE85A6FC2A57899F97A2E37D9433D8522BBDF677",
            "dev/ryanhcode/sable/sublevel/storage/SubLevelRemovalReason.class":
                "EEDFD022C1EC7EF3D92EE7385B200D4F34C6C2DE52D729F740DD7A901B549B3C",
            "dev/ryanhcode/sable/api/sublevel/ServerSubLevelContainer.class":
                "DD0D2D8C6D3727C6584FB56A889D26F74E547D651FD3B1B71413D3A41034CA30",
            "dev/ryanhcode/sable/sublevel/ServerSubLevel.class":
                "033EFF21106F748C94B4DC51426A450398392A2E896A9BA7095A7CE4270B9119",
        },
    ),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def task_signature(task: Mapping[str, Any]) -> tuple[str, str, int]:
    kind = str(task.get("type", ""))
    target: Any = task.get("item") if kind == "item" else task.get("advancement")
    if isinstance(target, Mapping):
        target = target.get("id")
    return kind, str(target or ""), int(task.get("count", 1))


def method_slice(source: str, start: str, end: str | None = None) -> str:
    index = source.find(start)
    if index < 0:
        return ""
    if end is None:
        return source[index:]
    stop = source.find(end, index + len(start))
    return source[index:] if stop < 0 else source[index:stop]


def require_tokens(source: str, tokens: tuple[str, ...], label: str, failures: list[str]) -> None:
    for token in tokens:
        if token not in source:
            failures.append(f"{label} lost required fail-closed token: {token}")


def validate_destinations(project: Path, failures: list[str]) -> None:
    proxima = load_json(project / PROXIMA)
    if proxima.get("parent") != "root" or proxima.get("name") != "proxima_centauri":
        failures.append("Proxima must remain a unique root-owned star body")
    if proxima.get("priority") != 2000 or proxima.get("planet_extras") != {"is_star": True}:
        failures.append("Proxima priority or star identity drifted")
    if proxima.get("position", {}).get("type") != "fixed":
        failures.append("Proxima is no longer a unique fixed interstellar body")

    glacio = load_json(project / GLACIO)
    expected = {
        "parent": "proxima_centauri",
        "name": "glacio",
        "priority": 2000,
        "acceleration_at_surface": 3.721,
        "radius": 2700000.0,
    }
    for key, value in expected.items():
        if glacio.get(key) != value:
            failures.append(f"Glacio {key} drifted")
    dimension = glacio.get("dimension_data", {})
    if dimension.get("linked_dimension") != "ad_astra:glacio":
        failures.append("Glacio must link only the canonical Ad Astra surface")
    if "glacio_orbit" in json.dumps(glacio):
        failures.append("Glacio must never link the prefab orbit dimension")
    owners = []
    for path in (project / "src/main/resources/data/rocketnautics/universe_planets").glob("*.json"):
        payload = load_json(path)
        if payload.get("dimension_data", {}).get("linked_dimension") == "ad_astra:glacio":
            owners.append(path.name)
    if owners != ["glacio.json"]:
        failures.append(f"ad_astra:glacio body ownership is not singular: {owners}")

    physics = load_json(project / PHYSICS)
    if physics != {
        "dimension": "ad_astra:glacio",
        "priority": 2000,
        "universal_drag": 0.0,
        "base_gravity": [0.0, -3.721, 0.0],
        "base_pressure": 0.0,
        "magnetic_north": [0.0, 0.0, 0.0],
    }:
        failures.append("exact Glacio Sable physics drifted")


def validate_moon_generation(project: Path, failures: list[str]) -> None:
    configured = load_json(project / CONFIGURED_ORE)
    targets = configured.get("config", {}).get("targets", [])
    expected_target = {
        "target": {"predicate_type": "minecraft:block_match", "block": "ad_astra:moon_stone"},
        "state": {"Name": "cosmowarp:moon_crystal_ore"},
    }
    if configured.get("type") != "minecraft:ore" or targets != [expected_target]:
        failures.append("Moon Crystal generation must replace only Ad Astra moon stone")
    if configured.get("config", {}).get("size") != 3:
        failures.append("Moon Crystal vein size drifted")
    placed = load_json(project / PLACED_ORE)
    if placed.get("feature") != "industrial_colonies:ad_astra_moon_crystal_ore":
        failures.append("placed Moon Crystal feature no longer owns its source namespace")
    placement_types = [row.get("type") for row in placed.get("placement", [])]
    if placement_types != [
        "minecraft:count", "minecraft:in_square", "minecraft:height_range", "minecraft:biome"
    ] or placed.get("placement", [{}])[0].get("count") != 6:
        failures.append("Moon Crystal placement semantics drifted")
    modifier = load_json(project / BIOME_MODIFIER)
    if modifier != {
        "type": "neoforge:add_features",
        "biomes": "ad_astra:lunar_wastelands",
        "features": "industrial_colonies:ad_astra_moon_crystal_ore",
        "step": "underground_ores",
    }:
        failures.append("Moon Crystal biome modifier no longer targets canonical Ad Astra Moon")
    forbidden = project / "src/main/resources/data/cosmowarp/worldgen/configured_feature/moon_crystal_ore.json"
    if forbidden.exists():
        failures.append("source overrides Cosmowarp's stock Rocketnautics Moon feature")


def validate_route_and_policy(project: Path, failures: list[str]) -> None:
    route = (project / SIGNED_ROUTE).read_text(encoding="utf-8-sig")
    require_tokens(route, (
        'ROUTE_ID = "sol_glacio_v1"',
        '"3075d9ba54e0d5aff1fcd3d799e9a3906df93fcc5f68ffa019db07d19f4903ec"',
        'UUID.fromString("2d85acb9-5567-5292-9bb1-8420dc590f3a")',
        'UUID.fromString("c27cc553-9d70-5170-ab7c-2af238ed19b3")',
        'new BlockPos(0, 256, 0)',
        'List.of(SOL_POINT, GLACIO_POINT)',
        'if (!EXACT_POINT_SET.equals(points))',
        'expectedCustomData().equals(customData.copyTag())',
        'SOL_DIMENSION.equals(source) && GLACIO_POINT_ID.equals(selected.get())',
        'GLACIO_DIMENSION.equals(source) && SOL_POINT_ID.equals(selected.get())',
    ), "signed route", failures)
    if "glacio_orbit" in route or "newlyRegistered" in route:
        failures.append("signed route accepts prefab orbit or arbitrary stock registration")

    policy = (project / POLICY).read_text(encoding="utf-8-sig")
    require_tokens(policy, (
        '"industrial_colonies", "interstellar_warp_charge"',
        'ResourceLocation.fromNamespaceAndPath("ad_astra", "freeze_resistant_armor")',
        'stack.shrink(1)',
        'expected.targetPoint().equals(stockChargingTarget)',
        'Optional<VesselState> state = inspectVessel(drive, route.orElse(null))',
        'ServerPlayer initiator',
        'if (initiator == null)',
        'player -> player == initiator',
        'public static boolean mayMutateRoute(',
        'if (!mayUseWarpDriveMenu(drive, initiator))',
        'public static boolean mayUseWarpDriveMenu(',
        'drive.isCharging()',
        'return isLiveShipOperator(drive, initiator)',
        'private static boolean isLiveShipOperator(',
        'level.getBlockEntity(drive.getBlockPos()) != drive',
        '!metadata.isAuthorized(initiator)',
        'occupied != ship',
        'noneMatch(entity -> entity == initiator)',
        'return warpDrives == 1 && containsThisDrive',
        'Optional<VesselState> current = inspectVessel(drive, route)',
        'chain.size() != 1',
        'if (route != null && !destinationIsClear(origin, route, level))',
        'sourceLevel.getServer().getLevel(',
        'route.target().dimension()',
        'BlockPos target = route.target().pos()',
        'BoundingBox3d translatedBounds = origin.boundingBox().move(',
        'target.getX() + 0.5D - sourceCenter.x()',
        'target.getY() + 0.5D - sourceCenter.y()',
        'target.getZ() + 0.5D - sourceCenter.z()',
        'destinationContainer.queryIntersecting(translatedBounds).iterator().hasNext()',
        '!ship.getPlot().getContraptions().isEmpty()',
        'metadata.role() != StationRole.SHIP',
        'StationServicesControllerBlockEntity.isLiveFor(ship, metadata)',
        'warpDrives != 1',
        'found == drive',
        'actor instanceof InterstellarNavigationComputerBlockEntity',
        'player.isPassenger()',
        'player.isVehicle()',
        'stack.canEquip(slot, player)',
        'AABB candidateBox = stockCandidateBox(origin)',
        'physicalEntities.stream().anyMatch(entity -> !(entity instanceof ServerPlayer))',
        'physicalCandidates.stream().map(ServerPlayer::getUUID).toList()',
        'ship.getUniqueId()',
        'MAX_PERSISTED_OCCUPANTS = 256',
        'tag.contains("schema", Tag.TAG_INT)',
        'tag.contains("route_signature", Tag.TAG_STRING)',
        'tag.contains("source_dimension", Tag.TAG_STRING)',
        'tag.contains("inbound_to_glacio", Tag.TAG_BYTE)',
        'tag.contains("charge_consumed", Tag.TAG_BYTE)',
        'occupantTags.isEmpty()',
        'occupantTags.size() > MAX_PERSISTED_OCCUPANTS',
        'identityTags.size() != 1',
        'identities.size() == 1',
        'hasUniqueValues(occupants)',
        'hasUniqueSubLevels(identities)',
    ), "interstellar policy", failures)
    live_operator = method_slice(
        policy,
        "private static boolean isLiveShipOperator(",
        "/** Consumes one charge only after stock beginWarp has returned SUCCESS. */",
    )
    require_tokens(live_operator, (
        "metadata.role() != StationRole.SHIP",
        "StationServicesControllerBlockEntity.isLiveFor(ship, metadata)",
        "actor instanceof InterstellarNavigationComputerBlockEntity",
        "return warpDrives == 1 && containsThisDrive",
    ), "route-independent live ship operator", failures)
    inspect_vessel = method_slice(
        policy,
        "private static Optional<VesselState> inspectVessel(",
        "private static boolean destinationIsClear(",
    )
    require_tokens(inspect_vessel, (
        "metadata.role() != StationRole.SHIP",
        "StationServicesControllerBlockEntity.isLiveFor(ship, metadata)",
        "actor instanceof InterstellarNavigationComputerBlockEntity",
        "warpDrives != 1",
        "containsThisDrive",
    ), "begin/execute vessel inspection", failures)
    if "hasMatchingController" in policy or "!metadata.hasFreshServices(" in policy:
        failures.append("policy trusts a stale heartbeat or redundant controller helper")


def validate_transaction_and_mixin(project: Path, failures: list[str]) -> None:
    transaction = (project / TRANSACTION).read_text(encoding="utf-8-sig")
    require_tokens(transaction, (
        'blockEntity.saveWithFullMetadata(source.getLevel().registryAccess())',
        'source.getUserDataTag().copy()',
        'Set<UUID> destinationBefore = new HashSet<>()',
        'for (ServerSubLevel existing : destinationContainer.getAllSubLevels())',
        '"Interstellar warp destination snapshot failed; no copy was attempted"',
        'if (!InterstellarWarpRemovalScope.begin(source))',
        'SubLevelWarper.WarpSubLevel(source, destinationLevel, target)',
        '"Interstellar warp copy failed; cleanup safety assessment follows"',
        'boolean sourcePristine = false',
        'if (!InterstellarWarpRemovalScope.sourceRemovalStarted(source))',
        'sourcePristine = !source.isRemoved()\n                                '
        '&& sourceContainer.getSubLevel(source.getUniqueId()) == source',
        'catch (RuntimeException | LinkageError probeFailure)',
        '"Interstellar warp source identity could not be verified; "',
        'if (sourcePristine)',
        'sourceContainer.getSubLevel(source.getUniqueId()) == source',
        'List<Throwable> cleanupFailures = new ArrayList<>()',
        'rollbackNewDestinations(\n                            destinationContainer, destinationBefore, cleanupFailures)',
        'restorePlayers(players, cleanupFailures)',
        'for (Throwable cleanupFailure : cleanupFailures)',
        'candidates = new ArrayList<>(destination.getAllSubLevels())',
        'cleanupFailures.add(failure)',
        'for (PlayerSnapshot snapshot : snapshots)',
        'snapshot.player().teleportTo(',
        'destination.removeSubLevel(candidate, SubLevelRemovalReason.REMOVED)',
        '"Interstellar warp destination rollback and crew restoration are "',
        '+ "unsafe because destructive source removal began or source "',
        '} finally {\n            InterstellarWarpRemovalScope.clear(source);\n        }',
        'The consumed charge is never refunded',
    ), "warp transaction", failures)
    if transaction.count("SubLevelWarper.WarpSubLevel(") != 1:
        failures.append("transaction must invoke the stock copy exactly once")
    if transaction.count("InterstellarWarpRemovalScope.begin(source)") != 1:
        failures.append("transaction must open exactly one removal scope")

    destination_snapshot = transaction.find("Set<UUID> destinationBefore = new HashSet<>()")
    destination_try = transaction.find("try {", destination_snapshot)
    destination_loop = transaction.find(
        "for (ServerSubLevel existing : destinationContainer.getAllSubLevels())",
        destination_try,
    )
    destination_catch = transaction.find(
        "} catch (RuntimeException | LinkageError error) {",
        destination_loop,
    )
    destination_failure_log = transaction.find(
        "Interstellar warp destination snapshot failed; no copy was attempted",
        destination_catch,
    )
    destination_failure_return = transaction.find("return 0;", destination_failure_log)
    scope_begin = transaction.find("InterstellarWarpRemovalScope.begin(source)")
    warp_call = transaction.find("SubLevelWarper.WarpSubLevel(", scope_begin)
    if not (
        0 <= destination_snapshot < destination_try < destination_loop
        < destination_catch < destination_failure_log < destination_failure_return
        < scope_begin < warp_call
    ):
        failures.append(
            "destination inventory must be snapshotted under a fail-closed guard before "
            "the removal scope and stock copy")

    copy_catch = transaction.find(
        "} catch (RuntimeException | LinkageError error) {",
        warp_call,
    )
    copy_failure_log = transaction.find(
        "Interstellar warp copy failed; cleanup safety assessment follows",
        copy_catch,
    )
    pristine_false = transaction.find("boolean sourcePristine = false", copy_failure_log)
    marker_gate = transaction.find(
        "if (!InterstellarWarpRemovalScope.sourceRemovalStarted(source))",
        pristine_false,
    )
    probe_try = transaction.find("try {", marker_gate)
    probe_assignment = transaction.find("sourcePristine = !source.isRemoved()", probe_try)
    probe_catch = transaction.find(
        "} catch (RuntimeException | LinkageError probeFailure) {",
        probe_assignment,
    )
    probe_failure_log = transaction.find(
        "Interstellar warp source identity could not be verified; ",
        probe_catch,
    )
    pristine_guard = transaction.find("if (sourcePristine) {", probe_failure_log)
    rollback = transaction.find("rollbackNewDestinations(", pristine_guard)
    restore = transaction.find("restorePlayers(", rollback)
    pristine_else = transaction.find("} else {", restore)
    finally_clear = transaction.find(
        "} finally {\n            InterstellarWarpRemovalScope.clear(source);\n        }",
        pristine_else,
    )
    if not (
        0 <= scope_begin < warp_call < copy_catch < copy_failure_log < pristine_false
        < marker_gate < probe_try < probe_assignment < probe_catch < probe_failure_log
        < pristine_guard < rollback < restore < pristine_else < finally_clear
    ):
        failures.append(
            "copy failure must be logged first, source identity must be probed fail closed, "
            "rollback must remain inside the proven-pristine branch, and the scope must "
            "clear in finally")
    probe_failure_block = (
        transaction[probe_catch:pristine_guard]
        if 0 <= probe_catch < pristine_guard
        else ""
    )
    if transaction.count("sourcePristine =") != 2 or "sourcePristine =" in probe_failure_block:
        failures.append(
            "source identity probe failure must leave sourcePristine false and suppress rollback")
    if transaction.count("rollbackNewDestinations(") != 2:
        # One guarded call plus the helper declaration are expected.
        failures.append("destination rollback call/declaration count drifted")

    removal_scope = (project / REMOVAL_SCOPE).read_text(encoding="utf-8-sig")
    require_tokens(removal_scope, (
        "private static final ThreadLocal<State> CURRENT = new ThreadLocal<>()",
        "if (source == null || CURRENT.get() != null)",
        "CURRENT.set(new State(source))",
        "if (state != null && candidate == state.source)",
        "state.removalStarted = true",
        "return state == null || state.source != source || state.removalStarted",
        "if (state != null && state.source == source)",
        "CURRENT.remove()",
        "private static final class State",
        "private final ServerSubLevel source",
    ), "fail-closed interstellar removal scope", failures)

    removal_mixin = (project / SABLE_REMOVAL_MIXIN).read_text(encoding="utf-8-sig")
    remove_target = (
        'method = "removeSubLevel(IILdev/ryanhcode/sable/sublevel/storage/"\n'
        '                    + "SubLevelRemovalReason;)V"'
    )
    require_tokens(removal_mixin, (
        "@Mixin(value = ServerSubLevelContainer.class, remap = false)",
        remove_target,
        'at = @At("HEAD")',
        "require = 1",
        ".getSubLevel(plotX, plotZ)",
        "InterstellarWarpRemovalScope.markRemovalStarted(candidate)",
    ), "exact Sable destructive-removal boundary", failures)
    if removal_mixin.count(remove_target) != 1:
        failures.append("Sable removeSubLevel HEAD target is not singular")

    mixin = (project / WARP_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(mixin, (
        'method = "beginWarp()Ldev/waco0311/cosmowarp/block/entity/"',
        'InterstellarWarpPolicy.authorizeStart(\n                        drive, InterstellarWarpInitiatorScope.current())',
        'consumeAfterSuccessfulBegin(pending)',
        'method = "executeWarp()V"',
        'InterstellarWarpPolicy.authorizeExecute(',
        'chargingTargetId))',
        '@Redirect(',
        'InterstellarWarpTransaction.warp(',
        'industrialColonies$warpCopySucceeded = moved == 1',
        'ordinal = 1',
        'if (!industrialColonies$warpCopySucceeded)',
        'chargeTicksRemaining > 0 && industrialColonies$activeAuthorization != null',
        'Authorization.fromTag(',
        'industrialColonies$activeAuthorization == null',
        'chargeTicksRemaining = 0',
        'chargingTargetId = null',
        'chargingEffectPlayers = List.of()',
        'broadcastWarpEffectToPlayers(',
        'drive.setChanged()',
        'level.sendBlockUpdated(',
    ), "warp-drive mixin", failures)
    if "WARP_PERFORMED" in mixin or "WarpPerformed" in mixin:
        failures.append("custom gate must never synthesize the stock success advancement")


def validate_assets_and_arrival(project: Path, failures: list[str]) -> None:
    entity = (project / COMPUTER_BE).read_text(encoding="utf-8-sig")
    block = (project / COMPUTER_BLOCK).read_text(encoding="utf-8-sig")
    if "implements BlockEntitySubLevelActor" not in entity:
        failures.append("Interstellar Navigation Computer is not a physical Sable actor")
    if "new InterstellarNavigationComputerBlockEntity(pos, state)" not in block:
        failures.append("Interstellar Navigation Computer no longer creates its block entity")
    if load_json(project / BLOCKSTATE) != {
        "variants": {"": {"model": "industrial_colonies:block/interstellar_navigation_computer"}}
    }:
        failures.append("Interstellar Navigation Computer blockstate drifted")
    if load_json(project / ITEM_MODEL) != {
        "parent": "industrial_colonies:block/interstellar_navigation_computer"
    }:
        failures.append("Interstellar Navigation Computer item model drifted")
    if (project / LOOT).read_text(encoding="utf-8-sig").count(
            "industrial_colonies:interstellar_navigation_computer") != 1:
        failures.append("Interstellar Navigation Computer does not self-drop exactly once")
    if load_json(project / CHARGE_MODEL).get("textures", {}).get("layer0") != "cosmowarp:item/moon_crystal":
        failures.append("Interstellar Warp Charge model drifted")
    arrival = load_json(project / ARRIVAL)
    criterion = next(iter(arrival.get("criteria", {}).values()), None)
    if len(arrival.get("criteria", {})) != 1 or criterion != {
        "trigger": "minecraft:changed_dimension",
        "conditions": {"to": "ad_astra:glacio"},
    }:
        failures.append("Glacio arrival advancement drifted")
    if "rewards" in arrival or "display" in arrival or arrival.get("sends_telemetry_event") is not False:
        failures.append("Glacio arrival advancement is not observation-only")


def expected_mechanical_slots(recipe: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    key = recipe["key"]
    slots = {
        f"cell_{row_index}_{column_index}": {
            "kind": "ITEM",
            "id": key[symbol],
        }
        for row_index, pattern_row in enumerate(recipe["pattern"])
        for column_index, symbol in enumerate(pattern_row)
    }
    slots["output"] = {"kind": "ITEM", "id": str(recipe["output"])}
    return slots


def expected_sequence_slots(recipe: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    slots: dict[str, dict[str, str]] = {
        "input": {"kind": "ITEM", "id": str(recipe["input"])},
        "transitional": {"kind": "ITEM", "id": str(recipe["transitional"])},
        "output0": {"kind": "ITEM", "id": str(recipe["output"])},
    }
    for index, step in enumerate(recipe["steps"]):
        operation = str(step["op"])
        ingredient = step.get("ingredient")
        if ingredient is not None:
            slots[f"seqItem{index}"] = {"kind": "ITEM", "id": str(ingredient)}
        slots[f"__machine_step_{index}_{operation}"] = {
            "kind": "ITEM",
            "id": str(step["machine"]),
        }
    return slots


def validate_recipes_and_topology(
    project: Path,
    manifest: Path,
    compiled: Path,
    failures: list[str],
) -> None:
    seed = load_json(project / SEED)
    phases = seed.get("phase_order", [])
    if phases[-2:] != [OUTER_PHASE, INTERSTELLAR_PHASE]:
        failures.append("Stage14 phase spine must end with Outer System Industry then Interstellar Escape")
    phase_by_node = seed.get("phase_by_node", {})
    if phase_by_node.get(OUTER_NODE) != OUTER_PHASE:
        failures.append("Outer Station node/phase ownership drifted")
    if phase_by_node.get(INTERSTELLAR_NODE) != INTERSTELLAR_PHASE:
        failures.append("Interstellar node/phase ownership drifted")

    scoped = [
        row for row in seed.get("recipes", [])
        if str(row.get("id", "")).startswith("industrial_colonies:interstellar/")
    ]
    if [row.get("id") for row in scoped] != RECIPE_IDS:
        failures.append("Stage14 must retain exactly the five reviewed recipe routes in order")
        return

    manifest_rows = {
        row.get("id"): row
        for row in load_json(manifest).get("recipes", [])
        if row.get("id") in RECIPES
    }
    compiled_payload = load_json(compiled)
    cards_by_id: dict[str, list[dict[str, Any]]] = {
        recipe_id: [
            row for row in compiled_payload.get("recipes", [])
            if row.get("recipeId") == recipe_id
        ]
        for recipe_id in RECIPE_IDS
    }

    for row in scoped:
        recipe_id = str(row["id"])
        expected = RECIPES[recipe_id]
        for field, value in expected.items():
            if row.get(field) != value:
                failures.append(f"Stage14 seed recipe {recipe_id} {field} drifted")
        if not str(row.get("comment", "")).strip():
            failures.append(f"Stage14 seed recipe {recipe_id} lacks a manufacturing rationale")

        assembled = manifest_rows.get(recipe_id)
        if assembled is None:
            failures.append(f"assembled manifest lost Stage14 recipe {recipe_id}")
        else:
            for field, value in expected.items():
                if field == "depends_on":
                    if not set(value).issubset(set(assembled.get(field, []))):
                        failures.append(f"assembled Stage14 recipe {recipe_id} lost ancestry")
                elif assembled.get(field) != value:
                    failures.append(f"assembled Stage14 recipe {recipe_id} {field} drifted")
            if assembled.get("remove", []) != expected.get("remove", []):
                failures.append(f"assembled Stage14 recipe {recipe_id} removal ownership drifted")

        cards = cards_by_id[recipe_id]
        if len(cards) != 1:
            failures.append(f"compiled project must contain one Stage14 card {recipe_id}")
            continue
        card = cards[0]
        recipe_type = expected["type"]
        if recipe_type == "mechanical_crafting":
            if card.get("type") != "kjsgen:create_mechanical_crafting":
                failures.append(f"compiled Stage14 card {recipe_id} is not Mechanical Crafting")
            if card.get("params") != {"gridW": "5", "gridH": "5"}:
                failures.append(f"compiled Stage14 card {recipe_id} is not exactly 5x5")
            if card.get("slots") != expected_mechanical_slots(expected):
                failures.append(f"compiled Stage14 card {recipe_id} grid or output drifted")
        elif recipe_type == "sandpaper_polishing":
            if card.get("type") != "kjsgen:create_sandpaper_polishing":
                failures.append("compiled Moon Crystal route is not Sandpaper Polishing")
            if card.get("slots") != {
                "input": {"kind": "ITEM", "id": expected["input"]},
                "output": {"kind": "ITEM", "id": expected["output"]},
            } or card.get("params") != {}:
                failures.append("compiled Moon Crystal polishing slots drifted")
        elif recipe_type == "sequenced_assembly":
            if card.get("type") != "kjsgen:create_sequenced_assembly":
                failures.append("compiled Warp Charge route is not Sequenced Assembly")
            expected_params = {
                "loops": "2",
                "__seqLen": "5",
                "seq0": "deploying",
                "seq1": "deploying",
                "seq2": "deploying",
                "seq3": "deploying",
                "seq4": "pressing",
            }
            if card.get("slots") != expected_sequence_slots(expected):
                failures.append("compiled Warp Charge assembly slots or machines drifted")
            if card.get("params") != expected_params:
                failures.append("compiled Warp Charge assembly order or loop count drifted")

    removal_rows = [
        row for row in compiled_payload.get("removals", [])
        if row.get("recipeId") in MANAGED_STOCK_REMOVALS
    ]
    removal_counts = Counter(row.get("recipeId") for row in removal_rows)
    if removal_counts != Counter(MANAGED_STOCK_REMOVALS):
        failures.append("Stage14 managed stock-removal ownership is not exact")
    for row in removal_rows:
        if any(row.get(field) != "" for field in ("output", "input", "mod")):
            failures.append(f"Stage14 removal is broader than exact recipe ID: {row.get('recipeId')}")

    target_outputs = {expected["output"]: recipe_id for recipe_id, expected in RECIPES.items()}
    output_owners: dict[str, list[str]] = {target: [] for target in target_outputs}
    for card in compiled_payload.get("recipes", []):
        slots = card.get("slots", {})
        for name, slot in slots.items():
            if not str(name).startswith("output") or not isinstance(slot, Mapping):
                continue
            target = slot.get("id")
            if target in output_owners:
                output_owners[str(target)].append(str(card.get("recipeId", "")))
    for output, owner in target_outputs.items():
        if output_owners[output] != [owner]:
            failures.append(f"Stage14 output {output} has non-exclusive compiled owners: {output_owners[output]}")

    unsigned = next(row for row in scoped if row["id"] == RECIPE_IDS[2])
    unsigned_card = cards_by_id[RECIPE_IDS[2]][0] if len(cards_by_id[RECIPE_IDS[2]]) == 1 else {}
    serialized_unsigned = json.dumps({"seed": unsigned, "card": unsigned_card}, sort_keys=True)
    if not isinstance(unsigned.get("output"), str):
        failures.append("authored Warp Crystal output must remain a plain unsigned item ID")
    if any(token in serialized_unsigned for token in (
        "components", "component_patch", "industrial_colonies:interstellar_route",
        "3075d9ba54e0d5aff1fcd3d799e9a3906df93fcc5f68ffa019db07d19f4903ec",
    )):
        failures.append("authored Warp Crystal recipe illegally embeds signing authority")

    assignments = load_json(project / ASSIGNMENTS).get("nodes", {})
    outer = assignments.get(OUTER_NODE, {})
    interstellar = assignments.get(INTERSTELLAR_NODE, {})
    if outer.get("unlocks") != OUTER_UNLOCKS:
        failures.append("Outer Station unlock topology lost pre-precursor Moon Crystal polishing")
    if interstellar.get("unlocks") != INTERSTELLAR_UNLOCKS:
        failures.append("Interstellar Escape unlock topology drifted")
    if interstellar.get("icon") != "industrial_colonies:interstellar_navigation_computer":
        failures.append("Interstellar Escape node icon drifted")

    precursor = next(
        (
            row for row in seed.get("recipes", [])
            if row.get("id") == "industrial_colonies:outer_station/warp_charge_precursor"
        ),
        None,
    )
    polish = scoped[0]
    if (
        precursor is None
        or precursor.get("node") != OUTER_NODE
        or precursor.get("phase") != OUTER_PHASE
        or precursor.get("key", {}).get("W") != "cosmowarp:moon_crystal"
        or int(polish.get("order", 9999)) >= int(precursor.get("order", -1))
    ):
        failures.append("Moon Crystal polishing no longer honestly precedes the Stage13 warp precursor")

    boundary = (project / SPACE_BOUNDARY).read_text(encoding="utf-8-sig")
    for recipe_id in MANAGED_STOCK_REMOVALS:
        if recipe_id in boundary:
            failures.append(f"managed Stage14 removal is duplicated by deferred script: {recipe_id}")
    for recipe_id in ("cosmowarp:crystal_driver", "cosmowarp:memory_card"):
        if boundary.count(f"'{recipe_id}'") != 1:
            failures.append(f"deferred non-authoritative Cosmowarp recipe ownership drifted: {recipe_id}")


def validate_central_registration_and_signer(project: Path, failures: list[str]) -> None:
    main = (project / MAIN_JAVA).read_text(encoding="utf-8-sig")
    for token in (
        "IndustrialBlocks.register(modEventBus);",
        "IndustrialItems.register(modEventBus);",
        "IndustrialBlockEntities.register(modEventBus);",
    ):
        if main.count(token) != 1:
            failures.append(f"central deferred registry attachment drifted: {token}")

    items = (project / ITEMS_JAVA).read_text(encoding="utf-8-sig")
    blocks = (project / BLOCKS_JAVA).read_text(encoding="utf-8-sig")
    block_entities = (project / BLOCK_ENTITIES_JAVA).read_text(encoding="utf-8-sig")
    require_tokens(items, (
        "DeferredItem<BlockItem> INTERSTELLAR_NAVIGATION_COMPUTER",
        'ITEMS.registerSimpleBlockItem(\n                    "interstellar_navigation_computer",',
        "IndustrialBlocks.INTERSTELLAR_NAVIGATION_COMPUTER",
        "DeferredItem<Item> INTERSTELLAR_WARP_CHARGE",
        'ITEMS.registerSimpleItem(\n                    "interstellar_warp_charge",',
        "new Item.Properties().stacksTo(1).fireResistant().rarity(Rarity.EPIC)",
        "DeferredItem<Item> WARP_CHARGE_PRECURSOR",
        'ITEMS.registerSimpleItem(\n                    "warp_charge_precursor",',
    ), "Stage14 item registry", failures)
    if items.count('"interstellar_navigation_computer"') != 1:
        failures.append("Interstellar Navigation Computer item registration is not singular")
    if items.count('"interstellar_warp_charge"') != 1:
        failures.append("Interstellar Warp Charge item registration is not singular")
    require_tokens(blocks, (
        "DeferredBlock<Block> INTERSTELLAR_NAVIGATION_COMPUTER",
        'BLOCKS.registerBlock(\n                    "interstellar_navigation_computer",',
        "InterstellarNavigationComputerBlock::new",
    ), "Stage14 block registry", failures)
    if blocks.count('"interstellar_navigation_computer"') != 1:
        failures.append("Interstellar Navigation Computer block registration is not singular")
    require_tokens(block_entities, (
        "BlockEntityType<InterstellarNavigationComputerBlockEntity>",
        'INTERSTELLAR_NAVIGATION_COMPUTER = BLOCK_ENTITIES.register(\n                    "interstellar_navigation_computer",',
        "InterstellarNavigationComputerBlockEntity::new",
        "IndustrialBlocks.INTERSTELLAR_NAVIGATION_COMPUTER.get()",
    ), "Stage14 block-entity registry", failures)
    if block_entities.count('"interstellar_navigation_computer"') != 1:
        failures.append("Interstellar Navigation Computer block-entity registration is not singular")

    mixins = load_json(project / MIXINS_JSON).get("mixins", [])
    stage14_mixins = (
        "CosmowarpWarpDriveMixin",
        "CosmowarpNetworkingMixin",
        "CosmowarpWarpDriveBlockMixin",
        "CosmowarpWarpDriveMenuMixin",
        "CosmowarpWarpDriveClickMixin",
        "CosmowarpCrystalSlotOwnerMixin",
        "CosmowarpCrystalSlotFreezeMixin",
        "CosmowarpCapabilityMixin",
        "DeepSpaceInstanceMixin",
        "SubLevelWarperUserDataMixin",
        "SableRemovalBoundaryMixin",
    )
    for name in stage14_mixins:
        if mixins.count(name) != 1:
            failures.append(f"{name} central registration drifted")

    gradle = (project / BUILD_GRADLE).read_text(encoding="utf-8-sig")
    if gradle.count('def cosmowarpJar = file("${pack_mods_dir}/cosmowarp-1.0.1.jar")') != 1:
        failures.append("exact Cosmowarp compile-only dependency pin drifted")
    if gradle.count("compileOnly files(cosmowarpJar)") != 1:
        failures.append("Cosmowarp is no longer exposed exactly once as compile-only")
    require_tokens(gradle, (
        'def sableJar = file("${pack_mods_dir}/sable-neoforge-1.21.1-2.0.3.jar")',
        "def bundledSableCompanionPath = 'META-INF/jarjar/sable-companion-common-1.21.1-1.6.0.jar'",
        "def generatedSableCompanionApi = layout.buildDirectory.file(",
        "def extractSableCompanionApi = tasks.register('extractSableCompanionApi')",
        "compileOnly files(generatedSableCompanionApi.get().asFile)",
        'def cosmonauticsJar = file("${pack_mods_dir}/cosmonautics-26.08.307.jar")',
        "def extractCosmonauticsGateApi = tasks.register('extractCosmonauticsGateApi', Jar)",
        "exclude 'META-INF/services/**'",
        "exclude 'META-INF/*.SF'",
        "exclude 'META-INF/*.RSA'",
        "exclude 'META-INF/*.DSA'",
        "compileOnly files(generatedCosmonauticsApi.get().asFile)",
        "dependsOn(extractCreatePonderApi, extractSableCompanionApi, extractCosmonauticsGateApi)",
    ), "exact Sable/Cosmonautics compile-only API extraction", failures)
    forbidden_dependency_forms = (
        "implementation files(cosmowarpJar)",
        "runtimeOnly files(cosmowarpJar)",
        "localRuntime files(cosmowarpJar)",
    )
    if any(token in gradle for token in forbidden_dependency_forms):
        failures.append("Cosmowarp dependency is bundled or runtime-owned by the candidate mod")

    mods_toml = (project / MODS_TOML).read_text(encoding="utf-8-sig")
    for dependency in SOURCE_SPACE_DEPENDENCIES:
        if mods_toml.count(dependency) != 1:
            mod_id = dependency.split('modId="', 1)[1].split('"', 1)[0]
            failures.append(f"exact required {mod_id} runtime dependency metadata drifted")

    scope = (project / INITIATOR_SCOPE).read_text(encoding="utf-8-sig")
    require_tokens(scope, (
        "private static final ThreadLocal<ServerPlayer> CURRENT = new ThreadLocal<>()",
        "if (CURRENT.get() != null)",
        'throw new IllegalStateException("nested interstellar warp initiator scope")',
        "CURRENT.set(initiator)",
        "return operation.get()",
        "finally",
        "CURRENT.remove()",
    ), "exact warp initiator scope", failures)

    networking = (project / NETWORKING_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(networking, (
        "@Mixin(value = ModNetworking.class, remap = false)",
        'lambda$handleSimpleAction$0(Lnet/neoforged/neoforge/network/handling/',
        'lambda$handleSelect$1(Lnet/neoforged/neoforge/network/handling/',
        'lambda$handleRename$2(Lnet/neoforged/neoforge/network/handling/',
        'WarpDriveBlockEntity;beginWarp()Ldev/waco0311/cosmowarp/',
        'WarpDriveBlockEntity;registerHere()Z',
        'WarpDriveBlockEntity;setSelectedId(Ljava/util/UUID;)V',
        'WarpDriveBlockEntity;renamePoint(Ljava/util/UUID;',
        "if (!(context.player() instanceof ServerPlayer initiator))",
        "InterstellarWarpInitiatorScope.callAs(",
        "InterstellarWarpPolicy.mayMutateRoute(drive, initiator)",
        "require = 1",
    ), "exact Cosmowarp server-network gate", failures)
    if networking.count("@WrapOperation(") != 4:
        failures.append("Cosmowarp server-network gate must wrap START, REGISTER, SELECT, and RENAME exactly once")

    warp_block = (project / WARP_BLOCK_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(warp_block, (
        "@Mixin(value = WarpDriveBlock.class, remap = false)",
        'method = "useWithoutItem(Lnet/minecraft/world/level/block/state/BlockState;"',
        'at = @At("HEAD")',
        "cancellable = true",
        "require = 1",
        "level.getBlockEntity(pos) instanceof WarpDriveBlockEntity drive",
        "InterstellarWarpPolicy.mayUseWarpDriveMenu(drive, serverPlayer)",
        "callback.setReturnValue(InteractionResult.FAIL)",
    ), "physical Warp Drive menu-open gate", failures)

    warp_menu = (project / WARP_MENU_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(warp_menu, (
        "@Mixin(value = WarpDriveMenu.class, remap = false)",
        'method = "stillValid(Lnet/minecraft/world/entity/player/Player;)Z"',
        'at = @At("RETURN")',
        "cancellable = true",
        "require = 1",
        "callback.getReturnValue()",
        "InterstellarWarpPolicy.mayUseWarpDriveMenu(",
    ), "live Warp Drive menu gate", failures)

    warp_click = (project / WARP_CLICK_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(warp_click, (
        "@Mixin(AbstractContainerMenu.class)",
        'method = "clicked(IILnet/minecraft/world/inventory/ClickType;"',
        'at = @At("HEAD")',
        "cancellable = true",
        "require = 1",
        "(Object) this instanceof WarpDriveMenu menu",
        "InterstellarWarpPolicy.mayUseWarpDriveMenu(",
        "callback.cancel()",
    ), "server-authoritative Warp Drive click gate", failures)

    crystal_access = (project / CRYSTAL_SLOT_ACCESS).read_text(encoding="utf-8-sig")
    require_tokens(crystal_access, (
        "public interface WarpDriveCrystalSlotAccess",
        "WarpDriveBlockEntity industrialColonies$owner()",
    ), "private crystal-slot owner boundary", failures)

    crystal_owner = (project / CRYSTAL_OWNER_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(crystal_owner, (
        'targets = "dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity$1"',
        "remap = false",
        "implements WarpDriveCrystalSlotAccess",
        "@Shadow",
        "@Final",
        "private WarpDriveBlockEntity this$0",
        "return this$0",
    ), "exact private crystal-handler owner mixin", failures)

    crystal_freeze = (project / CRYSTAL_FREEZE_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(crystal_freeze, (
        "@Mixin(value = ItemStackHandler.class, remap = false)",
        'method = "insertItem(ILnet/minecraft/world/item/ItemStack;Z)"',
        'method = "extractItem(IIZ)Lnet/minecraft/world/item/ItemStack;"',
        'method = "setStackInSlot(ILnet/minecraft/world/item/ItemStack;)V"',
        'at = @At("HEAD")',
        "cancellable = true",
        "require = 1",
        "callback.setReturnValue(stack)",
        "callback.setReturnValue(ItemStack.EMPTY)",
        "callback.cancel()",
        "(Object) this instanceof WarpDriveCrystalSlotAccess access",
        "access.industrialColonies$owner().isCharging()",
    ), "cached-capability crystal freeze", failures)
    if crystal_freeze.count("@Inject(") != 3:
        failures.append("crystal slot must freeze insert, extract, and direct set exactly once")

    frozen_handler = (project / FROZEN_CRYSTAL_HANDLER).read_text(encoding="utf-8-sig")
    require_tokens(frozen_handler, (
        "public final class FrozenWarpCrystalItemHandler implements IItemHandler",
        "private final WarpDriveBlockEntity drive",
        "private final IItemHandler delegate",
        "return delegate.getStackInSlot(slot).copy()",
        "return drive.isCharging()\n                ? stack\n                : delegate.insertItem(slot, stack, simulate)",
        "return drive.isCharging()\n                ? ItemStack.EMPTY\n                : delegate.extractItem(slot, amount, simulate)",
    ), "non-modifiable dynamic crystal capability", failures)

    capability = (project / CAPABILITY_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(capability, (
        "@Mixin(value = Cosmonauticswarpdrive.class, remap = false)",
        "@ModifyReturnValue(",
        'method = "lambda$registerCapabilities$1(Ldev/waco0311/cosmowarp/block/"',
        'entity/WarpDriveBlockEntity;Lnet/minecraft/core/Direction;)"',
        'Lnet/neoforged/neoforge/items/IItemHandler;"',
        'at = @At("RETURN")',
        "require = 1",
        "@Local(argsOnly = true) WarpDriveBlockEntity drive",
        "return new FrozenWarpCrystalItemHandler(drive, original)",
    ), "exact dynamic crystal-capability wrapper", failures)

    block = (project / COMPUTER_BLOCK).read_text(encoding="utf-8-sig")
    require_tokens(block, (
        "if (!stack.is(dev.waco0311.cosmowarp.registry.ModItems.WARP_CRYSTAL.get()))",
        "return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;",
        "if (!level.isClientSide)",
        "SignedInterstellarRoute.signForDimension(stack, level.dimension())",
        "return ItemInteractionResult.FAIL;",
        "return ItemInteractionResult.SUCCESS;",
    ), "physical route signer", failures)
    if "stack.shrink(" in block or "stack.consume(" in block:
        failures.append("physical route signer consumes the reusable Warp Crystal")
    all_java = "\n".join(
        path.read_text(encoding="utf-8-sig", errors="replace")
        for path in (project / "src/main/java").rglob("*.java")
    )
    if all_java.count("SignedInterstellarRoute.signForDimension(") != 1:
        failures.append("route signing authority exists anywhere except the physical computer interaction")

    lang = load_json(project / LANG)
    if lang.get("block.industrial_colonies.interstellar_navigation_computer") != (
        "Interstellar Navigation Computer"
    ):
        failures.append("Interstellar Navigation Computer language registration drifted")
    if lang.get("item.industrial_colonies.interstellar_warp_charge") != "Interstellar Warp Charge":
        failures.append("Interstellar Warp Charge language registration drifted")
    if lang.get("message.industrial_colonies.interstellar_route.signed") != (
        "Signed the exact Sol–Glacio route and selected the opposite endpoint."
    ):
        failures.append("exact route-signing confirmation drifted")
    if lang.get("message.industrial_colonies.interstellar_route.invalid_dimension") != (
        "This route can only be signed at Sol or Glacio."
    ):
        failures.append("invalid-dimension signer message drifted")


def validate_ordinary_glacio_denial(project: Path, failures: list[str]) -> None:
    source = (project / SPACEFLIGHT_AUTHORIZATION).read_text(encoding="utf-8-sig")
    require_tokens(source, (
        'ResourceLocation.fromNamespaceAndPath("ad_astra", "glacio")',
    ), "ordinary Glacio destination key", failures)
    method = method_slice(
        source,
        "public static boolean mayDescendToManagedPlanet(",
        "private static boolean hasFullHeatResistantSuit(",
    )
    require_tokens(method, (
        "if (GLACIO.equals(destinationKey)) {\n            return false;\n        }",
        "boolean boundForMars = MARS.equals(destinationKey)",
    ), "ordinary Glacio descent denial", failures)
    denial = method.find("if (GLACIO.equals(destinationKey))")
    earlier_route_logic = method.find("boolean boundForMars")
    if denial < 0 or earlier_route_logic < 0 or denial >= earlier_route_logic:
        failures.append("ordinary Glacio descent is not denied unconditionally before prior-route logic")
    if method.count("if (GLACIO.equals(destinationKey))") != 1:
        failures.append("ordinary Glacio descent denial is not singular")
    if "glacio_orbit" in source:
        failures.append("ordinary descent authorization references the forbidden prefab Glacio orbit")

    mixin = (project / DEEP_SPACE_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(mixin, (
        "@Mixin(value = DeepSpaceInstance.class, remap = false)",
        'method = "tick(Lnet/minecraft/server/MinecraftServer;)V"',
        'target = "Ldev/devce/rocketnautics/api/orbit/AllowedTransfer;allowToDimension()Z"',
        "require = 1",
        "return dimensionAllowsTransfer",
        "&& SpaceflightAuthorization.mayDescendToManagedPlanet(",
        "lastOrbiting,",
        "(DeepSpaceInstance) (Object) this",
    ), "ordinary descent authorization hook", failures)


def validate_final_quests(project: Path, failures: list[str]) -> None:
    expected_keys = list(QUESTS_EXPECTED)
    source_chapter = load_json(project / QUESTS).get("chapter", {})
    source_quests = source_chapter.get("quests", [])
    source_keys = [row.get("key") for row in source_quests]
    if len(source_keys) != 29 or source_keys[22:29] != expected_keys:
        failures.append("Planetary Industry must end with the exact seven Stage14 observations in 29 quests")
    source_by_key = {row.get("key"): row for row in source_quests}
    forbidden = {
        "rewards", "reward", "stage", "stages", "team_stage", "command", "commands",
        "recipe", "recipes", "consume_items", "consume", "research_dependencies",
        "teleport", "dimension", "structure", "structure_id",
    }
    for key, (dependencies, tasks) in QUESTS_EXPECTED.items():
        quest = source_by_key.get(key, {})
        if quest.get("dependencies") != dependencies:
            failures.append(f"Stage14 quest dependency drifted: {key}")
        if [task_signature(task) for task in quest.get("tasks", [])] != tasks:
            failures.append(f"Stage14 quest task drifted: {key}")
        if forbidden.intersection(quest):
            failures.append(f"Stage14 quest contains authority, reward, or consumption: {key}")
        if any(forbidden.intersection(task) for task in quest.get("tasks", [])):
            failures.append(f"Stage14 quest task contains authority, reward, or consumption: {key}")
        text = json.dumps(quest.get("description", []), ensure_ascii=False).lower()
        if "consumes nothing" not in text or "recipe" not in text or "destination" not in text:
            failures.append(f"Stage14 quest lost its observation-only explanation: {key}")

    native = load_json(project / NATIVE_CHAPTER)
    native_quests = native.get("quests", [])
    native_task_count = sum(len(row.get("tasks", [])) for row in native_quests)
    if native.get("id") != "39D9D81E433A3293" or len(native_quests) != 29 or native_task_count != 55:
        failures.append("generated Planetary Industry chapter identity/count is not exactly 29 quests and 55 tasks")
        return

    tag_prefix = "industrial_colonies:planetary_guidance/"

    def native_key(quest: Mapping[str, Any]) -> str | None:
        tags = set(str(tag) for tag in quest.get("tags", []))
        for key in source_keys:
            if f"{tag_prefix}{key}" in tags:
                return str(key)
        return None

    native_keys = [native_key(row) for row in native_quests]
    if native_keys[22:29] != expected_keys:
        failures.append("native Planetary Industry chapter lost the seven final Stage14 quests")
    id_to_key = {
        str(row.get("id")): key
        for row, key in zip(native_quests, native_keys)
        if key is not None
    }
    native_by_key = {key: row for row, key in zip(native_quests, native_keys) if key is not None}
    for key, (dependencies, tasks) in QUESTS_EXPECTED.items():
        quest = native_by_key.get(key, {})
        expected_quest_id, expected_task_id = NATIVE_IDS[key]
        task_ids = [str(task.get("id")) for task in quest.get("tasks", [])]
        if str(quest.get("id")) != expected_quest_id or task_ids != [expected_task_id]:
            failures.append(f"native Stage14 deterministic quest/task identity drifted: {key}")
        dependency_keys = [id_to_key.get(str(value)) for value in quest.get("dependencies", [])]
        if dependency_keys != dependencies:
            failures.append(f"native Stage14 quest dependency drifted: {key}")
        if [task_signature(task) for task in quest.get("tasks", [])] != tasks:
            failures.append(f"native Stage14 quest task drifted: {key}")
        if forbidden.intersection(quest):
            failures.append(f"native Stage14 quest contains authority, reward, or consumption: {key}")
        if any(forbidden.intersection(task) for task in quest.get("tasks", [])):
            failures.append(f"native Stage14 task contains authority, reward, or consumption: {key}")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    recipes_csv = catalog / "recipes.csv" if catalog.is_dir() else catalog
    if not recipes_csv.is_file():
        failures.append(f"Stage14 recipe catalog is missing recipes.csv: {recipes_csv}")
        return
    with recipes_csv.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_id: dict[str, list[dict[str, str]]] = {
        recipe_id: [row for row in rows if row.get("recipe_id") == recipe_id]
        for recipe_id in CATALOG_STOCK_RECIPES
    }
    for recipe_id, expected in CATALOG_STOCK_RECIPES.items():
        matches = by_id[recipe_id]
        if len(matches) != 1:
            failures.append(f"installed catalog stock recipe ownership drifted: {recipe_id}")
            continue
        for field, value in expected.items():
            if matches[0].get(field) != value:
                failures.append(f"installed catalog stock recipe {recipe_id} {field} drifted")

    expected_owner_by_output = {
        expected["outputs"]: recipe_id
        for recipe_id, expected in CATALOG_STOCK_RECIPES.items()
    }
    for output, owner in expected_owner_by_output.items():
        producers = sorted(
            row.get("recipe_id", "")
            for row in rows
            if output in {
                value.strip() for value in row.get("outputs", "").split("|") if value.strip()
            }
        )
        if producers != [owner]:
            failures.append(f"installed catalog output {output} has unexpected producers: {producers}")


def validate_installed(mods: Path, failures: list[str]) -> None:
    family_patterns = {
        "cosmowarp-1.0.1.jar": "cosmowarp-*.jar",
        "cosmonautics-26.08.307.jar": "cosmonautics-*.jar",
        "adastra-1.21.1-1.16.22-neoforge.jar": "adastra-*.jar",
        "sable-neoforge-1.21.1-2.0.3.jar": "sable-neoforge-*.jar",
    }
    for name, pattern in family_patterns.items():
        found = sorted(path.name for path in mods.glob(pattern))
        if found != [name]:
            failures.append(f"installed Stage14 dependency set for {pattern} drifted: {found}")

    for name, (expected_jar_hash, entries) in DEPENDENCY_PINS.items():
        jar = mods / name
        if not jar.is_file():
            failures.append(f"missing pinned Stage14 dependency: {name}")
            continue
        if sha256(jar.read_bytes()) != expected_jar_hash:
            failures.append(f"installed Stage14 dependency hash drifted: {name}")
        try:
            with zipfile.ZipFile(jar) as archive:
                names = set(archive.namelist())
                for entry, expected_hash in entries.items():
                    if entry not in names:
                        failures.append(f"installed Stage14 dependency lacks entry: {name}!/{entry}")
                    elif sha256(archive.read(entry)) != expected_hash:
                        failures.append(f"installed Stage14 dependency entry drifted: {name}!/{entry}")
        except (OSError, zipfile.BadZipFile) as exc:
            failures.append(f"cannot inspect installed Stage14 dependency {jar}: {exc}")

    owners: list[str] = []
    for jar in sorted(mods.glob("*.jar")):
        try:
            with zipfile.ZipFile(jar) as archive:
                for entry in archive.namelist():
                    if "/universe_planets/" not in entry or not entry.endswith(".json"):
                        continue
                    try:
                        payload = json.loads(archive.read(entry).decode("utf-8-sig"))
                    except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
                        continue
                    if payload.get("dimension_data", {}).get("linked_dimension") == "ad_astra:glacio":
                        owners.append(f"{jar.name}!/{entry}")
        except (OSError, zipfile.BadZipFile):
            continue
    if owners:
        failures.append(f"installed JARs already own canonical Glacio before source bridge: {owners}")


def validate_candidate(project: Path, candidate: Path, failures: list[str]) -> None:
    if not candidate.is_file():
        failures.append(f"candidate JAR is missing: {candidate}")
        return
    try:
        with zipfile.ZipFile(candidate) as archive:
            names = set(archive.namelist())
            missing = sorted(CANDIDATE_ENTRIES - names)
            if missing:
                failures.append(f"candidate JAR lacks Stage14 implementation entries/assets: {missing}")
            if "META-INF/neoforge.mods.toml" in names:
                metadata = archive.read("META-INF/neoforge.mods.toml").decode(
                    "utf-8-sig", errors="replace")
                for dependency in CANDIDATE_SPACE_DEPENDENCIES:
                    if metadata.count(dependency) != 1:
                        mod_id = dependency.split('modId="', 1)[1].split('"', 1)[0]
                        failures.append(
                            f"candidate JAR lacks the exact required {mod_id} runtime dependency")
            for entry, source in CANDIDATE_RESOURCE_SOURCES.items():
                if entry in names and archive.read(entry) != (project / source).read_bytes():
                    failures.append(f"candidate JAR Stage14 asset differs from source: {entry}")
            for entry, markers in CANDIDATE_CLASS_MARKERS.items():
                if entry not in names:
                    continue
                bytecode = archive.read(entry)
                missing_markers = [
                    marker.decode("ascii", errors="replace")
                    for marker in markers if marker not in bytecode
                ]
                if missing_markers:
                    failures.append(
                        f"candidate JAR Stage14 class lacks reviewed bytecode markers: "
                        f"{entry}: {missing_markers}")
            forbidden_prefixes = (
                "dev/waco0311/cosmowarp/",
                "dev/egg/",
                "dev/devce/rocketnautics/",
                "dev/ryanhcode/sable/",
                "earth/terrarium/adastra/",
            )
            shaded = sorted(
                name for name in names
                if any(name.startswith(prefix) for prefix in forbidden_prefixes)
            )
            if shaded:
                failures.append(f"candidate JAR improperly bundles installed dependency classes: {shaded[:8]}")
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect candidate JAR {candidate}: {exc}")


def collect_failures(
    project: Path = PROJECT,
    *,
    manifest: Path | None = None,
    compiled: Path | None = None,
    catalog: Path | None = None,
    mods: Path | None = None,
    candidate_jar: Path | None = None,
) -> list[str]:
    project = project.resolve()
    failures: list[str] = []
    for path in REQUIRED_FILES:
        if not (project / path).is_file():
            failures.append(f"missing deployable Stage14 file: {path.as_posix()}")
    if failures:
        return failures
    manifest_path = manifest.resolve() if manifest else project / MANIFEST
    compiled_path = compiled.resolve() if compiled else project / COMPILED
    validate_destinations(project, failures)
    validate_moon_generation(project, failures)
    validate_route_and_policy(project, failures)
    validate_transaction_and_mixin(project, failures)
    validate_assets_and_arrival(project, failures)
    validate_recipes_and_topology(project, manifest_path, compiled_path, failures)
    validate_central_registration_and_signer(project, failures)
    validate_ordinary_glacio_denial(project, failures)
    validate_final_quests(project, failures)
    if catalog is not None:
        validate_catalog(catalog.resolve(), failures)
    if mods is not None:
        validate_installed(mods.resolve(), failures)
    if candidate_jar is not None:
        validate_candidate(project, candidate_jar.resolve(), failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    parser.add_argument("--mods", type=Path)
    parser.add_argument("--jar", type=Path)
    args = parser.parse_args()
    failures = collect_failures(
        args.project,
        manifest=args.manifest,
        compiled=args.compiled,
        catalog=args.catalog,
        mods=args.mods,
        candidate_jar=args.jar,
    )
    if failures:
        print(f"FAIL: deployable interstellar escape validation found {len(failures)} issue(s)")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "PASS: deployable interstellar escape boundary is exact and fail closed: "
        f"{len(RECIPE_IDS)} routes, {len(MANAGED_STOCK_REMOVALS)} exact removals, "
        f"{len(QUESTS_EXPECTED)} observation-only quests, {len(DEPENDENCY_PINS)} pinned dependencies, "
        f"and {len(CANDIDATE_ENTRIES)} required candidate-JAR entries/assets."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
