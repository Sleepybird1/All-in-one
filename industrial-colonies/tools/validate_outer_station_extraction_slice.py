#!/usr/bin/env python3
"""Fail closed on commissioned station services and gas-giant extraction."""

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
SEED = Path("progression/managed_recipe_overhaul.seed.json")
MANIFEST = Path("progression/managed_recipe_overhaul.json")
COMPILED = Path("pack-kjsgen/default.managed.json")
ASSIGNMENTS = Path("progression/machine_node_assignments.json")
QUESTS = Path("progression/ftbquests_planetary_industry.json")
NATIVE_CHAPTER = Path("pack-config-overrides/ftbquests/quests/chapters/planetary_industry.snbt")

MAIN_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialColonies.java")
FLUIDS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialFluids.java")
BLOCKS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlocks.java")
ITEMS_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java")
BLOCK_ENTITIES_JAVA = Path("src/main/java/dev/godpc/industrialcolonies/IndustrialBlockEntities.java")
STATION_ROLE = Path("src/main/java/dev/godpc/industrialcolonies/space/station/StationRole.java")
STATION_METADATA = Path("src/main/java/dev/godpc/industrialcolonies/space/station/StationMetadata.java")
OXYGEN_ACCESS = Path("src/main/java/dev/godpc/industrialcolonies/space/station/OxygenDistributorAccess.java")
LIFE_SUPPORT = Path("src/main/java/dev/godpc/industrialcolonies/space/station/StationLifeSupport.java")
ORBIT_VERIFIER = Path("src/main/java/dev/godpc/industrialcolonies/space/station/GasGiantOrbitVerifier.java")
CONTROLLER_BLOCK = Path("src/main/java/dev/godpc/industrialcolonies/space/station/StationServicesControllerBlock.java")
CONTROLLER_BE = Path("src/main/java/dev/godpc/industrialcolonies/space/station/StationServicesControllerBlockEntity.java")
SCOOP_BLOCK = Path("src/main/java/dev/godpc/industrialcolonies/space/station/AtmosphericScoopBlock.java")
SCOOP_BE = Path("src/main/java/dev/godpc/industrialcolonies/space/station/AtmosphericScoopBlockEntity.java")
OXYGEN_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/OxygenDistributorBlockEntityMixin.java")
BREATH_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/GlobalSpacePhysicsHandlerMixin.java")
WARPER_MIXIN = Path("src/main/java/dev/godpc/industrialcolonies/mixin/SubLevelWarperUserDataMixin.java")
MIXINS_JSON = Path("src/main/resources/industrial_colonies.mixins.json")
LANG = Path("src/main/resources/assets/industrial_colonies/lang/en_us.json")

NODE = "CR02 — Outer Station Extraction"
PHASE = "Outer System Industry"
RECIPE_IDS = [
    "industrial_colonies:outer_station/station_services_controller",
    "industrial_colonies:outer_station/atmospheric_scoop",
    "industrial_colonies:outer_station/warp_charge_precursor",
]
RECIPES: dict[str, dict[str, Any]] = {
    RECIPE_IDS[0]: {
        "node": NODE,
        "phase": PHASE,
        "order": 320,
        "type": "mechanical_crafting",
        "pattern": ["CTCTC", "HUOUH", "TEAET", "HUMUH", "CTGTC"],
        "key": {
            "C": "ad_astra:calorite_plate",
            "T": "rocketnautics:titanium_ingot",
            "H": "tfmg:heavy_machinery_casing",
            "U": "mekanism:ultimate_control_circuit",
            "O": "ad_astra:oxygen_distributor",
            "E": "mekanism:ultimate_energy_cube",
            "A": "computercraft:computer_advanced",
            "M": "industrial_colonies:mercury_navigation_computer",
            "G": "ad_astra:gravity_normalizer",
        },
        "output": "industrial_colonies:station_services_controller",
        "depends_on": [
            "industrial_colonies:planetary/mercury/navigation_computer",
            "industrial_colonies:space/life_support/oxygen_distributor",
            "industrial_colonies:planetary/outpost/gravity_normalizer",
            "industrial_colonies:mekanism/storage/ultimate_energy_cube",
            "industrial_colonies:mekanism/ultimate_control_circuit",
        ],
    },
    RECIPE_IDS[1]: {
        "node": NODE,
        "phase": PHASE,
        "order": 330,
        "type": "mechanical_crafting",
        "pattern": ["TCGCT", "PFUFP", "EASAE", "PHNHP", "TCGCT"],
        "key": {
            "T": "rocketnautics:titanium_block",
            "C": "ad_astra:calorite_plate",
            "G": "ad_astra:large_gas_tank",
            "P": "tfmg:industrial_pipe",
            "F": "ad_astra:fan",
            "U": "mekanism:ultimate_control_circuit",
            "E": "tfmg:electric_pump",
            "A": "computercraft:computer_advanced",
            "S": "industrial_colonies:station_services_controller",
            "H": "tfmg:heavy_machinery_casing",
            "N": "rocketnautics:engine_nozzle",
        },
        "output": "industrial_colonies:atmospheric_scoop",
        "depends_on": [
            "industrial_colonies:outer_station/station_services_controller",
            "industrial_colonies:space/propulsion/engine_nozzle",
            "industrial_colonies:space/life_support/fan",
            "industrial_colonies:space/life_support/large_gas_tank",
            "industrial_colonies:fluid_infrastructure/electric_pump",
        ],
    },
    RECIPE_IDS[2]: {
        "node": NODE,
        "phase": PHASE,
        "order": 340,
        "type": "mechanical_crafting",
        "pattern": ["BTBTB", "MCUCM", "BESEB", "MCWCM", "BTBTB"],
        "key": {
            "B": "industrial_colonies:gas_giant_condensate_bucket",
            "T": "rocketnautics:titanium_block",
            "M": "ad_astra:mercury_iron_ore",
            "C": "ad_astra:calorite_block",
            "U": "mekanism:ultimate_control_circuit",
            "E": "ae2:engineering_processor",
            "S": "industrial_colonies:industrial_star",
            "W": "cosmowarp:moon_crystal",
        },
        "output": "industrial_colonies:warp_charge_precursor",
        "depends_on": [
            "industrial_colonies:outer_station/atmospheric_scoop",
            "industrial_colonies:space/orbital_flight_computer",
        ],
    },
}

UNLOCKS = [
    "industrial_colonies:station_services_controller",
    "industrial_colonies:atmospheric_scoop",
    "industrial_colonies:gas_giant_condensate_bucket",
    "cosmowarp:moon_crystal",
    "industrial_colonies:warp_charge_precursor",
]
QUESTS_EXPECTED = {
    "outer_station_services": (
        ["asteroid_bulk_freight"],
        [("item", "industrial_colonies:station_services_controller", 1)],
    ),
    "gas_giant_extraction": (
        ["outer_station_services"],
        [("item", "industrial_colonies:atmospheric_scoop", 1)],
    ),
    "gas_giant_condensate_return": (
        ["gas_giant_extraction"],
        [("item", "industrial_colonies:gas_giant_condensate_bucket", 8)],
    ),
    "warp_charge_precursor": (
        ["gas_giant_condensate_return"],
        [("item", "industrial_colonies:warp_charge_precursor", 1)],
    ),
}

ASSETS = (
    Path("src/main/resources/assets/industrial_colonies/blockstates/station_services_controller.json"),
    Path("src/main/resources/assets/industrial_colonies/blockstates/atmospheric_scoop.json"),
    Path("src/main/resources/assets/industrial_colonies/models/block/station_services_controller.json"),
    Path("src/main/resources/assets/industrial_colonies/models/block/atmospheric_scoop.json"),
    Path("src/main/resources/assets/industrial_colonies/models/item/station_services_controller.json"),
    Path("src/main/resources/assets/industrial_colonies/models/item/atmospheric_scoop.json"),
    Path("src/main/resources/assets/industrial_colonies/models/item/gas_giant_condensate_bucket.json"),
    Path("src/main/resources/assets/industrial_colonies/models/item/warp_charge_precursor.json"),
    Path("src/main/resources/data/industrial_colonies/loot_table/blocks/station_services_controller.json"),
    Path("src/main/resources/data/industrial_colonies/loot_table/blocks/atmospheric_scoop.json"),
)
REQUIRED_FILES = (
    SEED, MANIFEST, COMPILED, ASSIGNMENTS, QUESTS, NATIVE_CHAPTER,
    MAIN_JAVA, FLUIDS_JAVA, BLOCKS_JAVA, ITEMS_JAVA, BLOCK_ENTITIES_JAVA,
    STATION_ROLE, STATION_METADATA, OXYGEN_ACCESS, LIFE_SUPPORT, ORBIT_VERIFIER,
    CONTROLLER_BLOCK, CONTROLLER_BE, SCOOP_BLOCK, SCOOP_BE, OXYGEN_MIXIN,
    BREATH_MIXIN, WARPER_MIXIN, MIXINS_JSON, LANG, *ASSETS,
)

CANDIDATE_ENTRIES = {
    "dev/godpc/industrialcolonies/IndustrialFluids.class",
    "dev/godpc/industrialcolonies/IndustrialBlocks.class",
    "dev/godpc/industrialcolonies/IndustrialItems.class",
    "dev/godpc/industrialcolonies/IndustrialBlockEntities.class",
    "dev/godpc/industrialcolonies/space/station/StationRole.class",
    "dev/godpc/industrialcolonies/space/station/StationMetadata.class",
    "dev/godpc/industrialcolonies/space/station/OxygenDistributorAccess.class",
    "dev/godpc/industrialcolonies/space/station/StationLifeSupport.class",
    "dev/godpc/industrialcolonies/space/station/GasGiantOrbitVerifier.class",
    "dev/godpc/industrialcolonies/space/station/StationServicesControllerBlock.class",
    "dev/godpc/industrialcolonies/space/station/StationServicesControllerBlockEntity.class",
    "dev/godpc/industrialcolonies/space/station/AtmosphericScoopBlock.class",
    "dev/godpc/industrialcolonies/space/station/AtmosphericScoopBlockEntity.class",
    "dev/godpc/industrialcolonies/mixin/OxygenDistributorBlockEntityMixin.class",
    "dev/godpc/industrialcolonies/mixin/GlobalSpacePhysicsHandlerMixin.class",
    "dev/godpc/industrialcolonies/mixin/SubLevelWarperUserDataMixin.class",
    "industrial_colonies.mixins.json",
    *{path.as_posix().removeprefix("src/main/resources/") for path in ASSETS},
}

DEPENDENCY_PINS = {
    "cosmonautics-26.08.307.jar": (
        "3FD9DAC868400905A55164D2C9D74ABC2080AE3269CA51E54E1899874945973E",
        {
            "dev/egg/SubLevelWarper.class": "6A575CE4EB0843E43B902F1E0D2C8D8EF7E72D48C25B12D2B8659FCDC0F41DAE",
            "dev/devce/rocketnautics/content/orbit/DeepSpaceData.class": "38B9A5B4CC0BF2918B539DD41FCD33EA2008431F9FFEC6051E25096038D020A1",
            "dev/devce/rocketnautics/content/orbit/universe/CubePlanet.class": "B50743580D27720E5DFB51BF34F9D86F4AC4E1AC72F977AA03525797CDE32B67",
            "dev/devce/rocketnautics/content/physics/GlobalSpacePhysicsHandler.class": "17DF02652B2E98E8A67F4138D7EB2AEEAF6559FBD5C849D178FAB15BBFD899F7",
        },
    ),
    "adastra-1.21.1-1.16.22-neoforge.jar": (
        "FAF21D02C71D2D5B5A671A746334ED18A9DDBA79A5A9D9BD95E93A1D9EE9EC86",
        {
            "earth/terrarium/adastra/common/blockentities/machines/OxygenDistributorBlockEntity.class":
                "8D7871022D292566AF364EB401BFB9BA9ED6C839D52EF2649B2085FF74E62F40",
        },
    ),
    "sable-neoforge-1.21.1-2.0.3.jar": (
        "DA6C3B66238586603D1DCAA2AFB012D36815FBCE0A2D5938FBB2936701D42279",
        {
            "dev/ryanhcode/sable/api/SubLevelHelper.class":
                "B1CD7AAF392320ECD08CADF385634E3C9E16BBD0082A1A25FBF7AE9B828D6B7B",
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
    target = task.get("item") if kind == "item" else task.get("advancement")
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
            failures.append(f"{label} lost fail-closed token: {token}")


def validate_recipes(project: Path, manifest: Path, compiled: Path, failures: list[str]) -> None:
    seed = load_json(project / SEED)
    if seed.get("phase_by_node", {}).get(NODE) != PHASE:
        failures.append("Outer Station Extraction phase assignment drifted")
    scoped = [
        row for row in seed.get("recipes", [])
        if str(row.get("id", "")).startswith("industrial_colonies:outer_station/")
    ]
    if [row.get("id") for row in scoped] != RECIPE_IDS:
        failures.append("outer-station managed recipe set/order drifted")
        return
    manifest_rows = {
        row.get("id"): row for row in load_json(manifest).get("recipes", [])
        if row.get("id") in RECIPES
    }
    compiled_payload = load_json(compiled)
    for row in scoped:
        recipe_id = str(row["id"])
        expected = RECIPES[recipe_id]
        for field, value in expected.items():
            if row.get(field) != value:
                failures.append(f"outer-station recipe {recipe_id} {field} drifted")
        if not str(row.get("comment", "")).strip():
            failures.append(f"outer-station recipe {recipe_id} lacks a manufacturing rationale")
        if "remove" in row or any(str(key).startswith("remove_") for key in row):
            failures.append(f"outer-station recipe {recipe_id} introduced a removal")
        assembled = manifest_rows.get(recipe_id)
        if assembled is None:
            failures.append(f"assembled manifest lost outer-station recipe {recipe_id}")
        else:
            for field, value in expected.items():
                if field == "depends_on":
                    if not set(value).issubset(set(assembled.get(field, []))):
                        failures.append(f"assembled outer-station recipe {recipe_id} lost ancestry")
                elif assembled.get(field) != value:
                    failures.append(f"assembled outer-station recipe {recipe_id} {field} drifted")
            if assembled.get("remove") != []:
                failures.append(f"assembled outer-station recipe {recipe_id} introduced a removal")
        cards = [
            card for card in compiled_payload.get("recipes", [])
            if card.get("recipeId") == recipe_id
        ]
        if len(cards) != 1:
            failures.append(f"compiled project must contain one outer-station card {recipe_id}")
            continue
        card = cards[0]
        if card.get("type") != "kjsgen:create_mechanical_crafting":
            failures.append(f"compiled outer-station card {recipe_id} is not Mechanical Crafting")
        if card.get("params") != {"gridW": "5", "gridH": "5"}:
            failures.append(f"compiled outer-station card {recipe_id} is not exactly 5x5")
        if card.get("slots", {}).get("output") != {"kind": "ITEM", "id": expected["output"]}:
            failures.append(f"compiled outer-station card {recipe_id} output drifted")
        expected_inputs = Counter(
            expected["key"][symbol]
            for pattern_row in expected["pattern"]
            for symbol in pattern_row
        )
        actual_inputs = Counter(
            slot.get("id")
            for name, slot in card.get("slots", {}).items()
            if name.startswith("cell_") and isinstance(slot, dict)
        )
        if actual_inputs != expected_inputs:
            failures.append(f"compiled outer-station card {recipe_id} ingredient grid drifted")
    if any(row.get("recipeId") in RECIPES for row in compiled_payload.get("removals", [])):
        failures.append("compiled project removes an outer-station recipe")
    precursor = scoped[-1]
    if precursor.get("key", {}).get("W") != "cosmowarp:moon_crystal":
        failures.append("warp precursor lost its non-authoritative Moon Crystal ancestry")
    if "cosmowarp:warp_crystal" in json.dumps(precursor):
        failures.append("warp precursor became circular with the later signed Warp Crystal")


def validate_assignments_and_quests(project: Path, failures: list[str]) -> None:
    node = load_json(project / ASSIGNMENTS).get("nodes", {}).get(NODE, {})
    if node.get("icon") != "industrial_colonies:atmospheric_scoop" or node.get("unlocks") != UNLOCKS:
        failures.append("Outer Station Extraction node unlock assignment drifted")
    if not str(node.get("role", "")).strip():
        failures.append("Outer Station Extraction node role is blank")

    chapter = load_json(project / QUESTS).get("chapter", {})
    quests = chapter.get("quests", [])
    keys = [row.get("key") for row in quests]
    if len(keys) != 29 or keys[18:22] != list(QUESTS_EXPECTED):
        failures.append("Planetary Industry must retain four outer-station observations before interstellar escape")
    forbidden = {
        "rewards", "stage", "stages", "team_stage", "command", "commands",
        "recipe", "recipes", "consume_items", "research_dependencies",
    }
    by_key = {row.get("key"): row for row in quests}
    for key, (dependencies, tasks) in QUESTS_EXPECTED.items():
        quest = by_key.get(key, {})
        if quest.get("dependencies") != dependencies:
            failures.append(f"outer-station quest dependency drifted: {key}")
        if [task_signature(task) for task in quest.get("tasks", [])] != tasks:
            failures.append(f"outer-station quest task drifted: {key}")
        if forbidden.intersection(quest) or any(forbidden.intersection(task) for task in quest.get("tasks", [])):
            failures.append(f"outer-station quest contains a gate, reward, or consumption: {key}")
        text = json.dumps(quest.get("description", []), ensure_ascii=False).lower()
        if ("consume nothing" not in text and "consumes nothing" not in text) or "no recipe" not in text or "no destination" not in text:
            failures.append(f"outer-station quest lost its observation-only boundary: {key}")
    native = load_json(project / NATIVE_CHAPTER)
    if len(native.get("quests", [])) != 29:
        failures.append("generated Planetary Industry chapter is not the 29-quest topology")
    native_text = json.dumps(native, ensure_ascii=False)
    for item in UNLOCKS:
        if item not in native_text:
            failures.append(f"generated Planetary Industry chapter lost {item}")


def validate_registries_and_assets(project: Path, failures: list[str]) -> None:
    main = (project / MAIN_JAVA).read_text(encoding="utf-8-sig")
    if main.count("IndustrialFluids.register(modEventBus);") != 1:
        failures.append("gas-giant fluid register is not attached exactly once")
    fluids = (project / FLUIDS_JAVA).read_text(encoding="utf-8-sig")
    require_tokens(
        fluids,
        (
            'FLUID_TYPES.register("gas_giant_condensate"',
            'FLUIDS.register(\n                    "gas_giant_condensate"',
            'FLUIDS.register(\n                    "flowing_gas_giant_condensate"',
            ".bucket(IndustrialItems.GAS_GIANT_CONDENSATE_BUCKET)",
            ".block(IndustrialBlocks.GAS_GIANT_CONDENSATE)",
            ".canConvertToSource(false)",
        ),
        "gas-giant fluid registry",
        failures,
    )
    blocks = (project / BLOCKS_JAVA).read_text(encoding="utf-8-sig")
    items = (project / ITEMS_JAVA).read_text(encoding="utf-8-sig")
    block_entities = (project / BLOCK_ENTITIES_JAVA).read_text(encoding="utf-8-sig")
    for name in ("station_services_controller", "atmospheric_scoop", "gas_giant_condensate"):
        if blocks.count(f'"{name}"') != 1:
            failures.append(f"Stage13 block registration drifted: {name}")
    for name in (
        "station_services_controller", "atmospheric_scoop",
        "gas_giant_condensate_bucket", "warp_charge_precursor",
    ):
        if items.count(f'"{name}"') != 1:
            failures.append(f"Stage13 item registration drifted: {name}")
    for name in ("station_services_controller", "atmospheric_scoop"):
        if block_entities.count(f'"{name}"') != 1:
            failures.append(f"Stage13 block-entity registration drifted: {name}")
    for token in (
        "Capabilities.EnergyStorage.BLOCK", "Capabilities.FluidHandler.BLOCK",
        "STATION_SERVICES_CONTROLLER.get()", "ATMOSPHERIC_SCOOP.get()",
    ):
        if token not in block_entities:
            failures.append(f"Stage13 capability registration lost {token}")
    if block_entities.count("Capabilities.EnergyStorage.BLOCK") != 2:
        failures.append("Stage13 energy capability registration count drifted")
    if block_entities.count("Capabilities.FluidHandler.BLOCK") != 2:
        failures.append("Stage13 fluid capability registration count drifted")
    for relative in ASSETS:
        try:
            load_json(project / relative)
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"invalid Stage13 resource {relative.as_posix()}: {exc}")
    language = load_json(project / LANG)
    for key in (
        "block.industrial_colonies.station_services_controller",
        "block.industrial_colonies.atmospheric_scoop",
        "fluid.industrial_colonies.gas_giant_condensate",
        "item.industrial_colonies.gas_giant_condensate_bucket",
        "item.industrial_colonies.warp_charge_precursor",
    ):
        if not str(language.get(key, "")).strip():
            failures.append(f"Stage13 localization is missing: {key}")


def validate_metadata_and_services(project: Path, failures: list[str]) -> None:
    role = (project / STATION_ROLE).read_text(encoding="utf-8-sig")
    if "SHIP," not in role or "STATION;" not in role:
        failures.append("station role enum must retain SHIP and STATION")
    metadata = (project / STATION_METADATA).read_text(encoding="utf-8-sig")
    require_tokens(
        metadata,
        (
            'ROOT_KEY = "industrial_colonies:station"', "SCHEMA = 1",
            '"role"', '"commissioned"', '"owner"', '"team"', '"controller"',
            '"commissioned_at"', '"services_heartbeat"', '"life_support_heartbeat"',
            "root.contains(ROOT_KEY, Tag.TAG_COMPOUND)", "root.contains(ROOT_KEY)",
            "existing.copy()", "StationRole.STATION", "StationRole.SHIP",
            "FTBTeamsAPI.api()", "relativePosition(subLevel, controllerPosition)",
            "return new StationMetadata(\n                role,",
        ),
        "station metadata",
        failures,
    )
    if "root = new CompoundTag()" in metadata and "existing == null" not in metadata:
        failures.append("station metadata overwrites the whole Sable user-data root")

    controller = (project / CONTROLLER_BE).read_text(encoding="utf-8-sig")
    controller_block = (project / CONTROLLER_BLOCK).read_text(encoding="utf-8-sig")
    require_tokens(
        controller_block,
        (
            "public void onRemove(", "!level.isClientSide",
            "!state.is(newState.getBlock())", "level.getBlockEntity(pos)",
            "controller.decommissionForBlockRemoval()",
            "super.onRemove(state, level, pos, newState, movedByPiston)",
        ),
        "station controller block-removal lifecycle",
        failures,
    )
    tick = method_slice(controller, "private void tickServer()", "private void fail(")
    if "metadata.role() != StationRole.STATION" in tick:
        failures.append("SHIP role cannot commission station services")
    require_tokens(
        controller,
        (
            "implements BlockEntitySubLevelActor", '"tfmg", "cooling_fluid"',
            "ENERGY_PER_TICK = 4_096", "COOLANT_PER_TICK = 1",
            "COMMISSIONING_TICKS = 600", "StationLifeSupport.hasLiveCoverage(station, worldPosition)",
            "IFluidHandler.FluidAction.SIMULATE", "IFluidHandler.FluidAction.EXECUTE",
            "energy.receiveEnergy(energyDebit, false)", "coolant.fill(coolantDebit",
            "metadata.commissioned(gameTime).write(station)", "metadata.heartbeat(gameTime).write(station)",
            "metadata.equals(current)", "station.getPlot().getLoadedChunks()",
            "Sable.HELPER.getContaining(controller) != station", "age <= 1L",
            "matching.hasServiceResources()", "lastSuccessfulServiceTick = Long.MIN_VALUE",
            "void decommissionForBlockRemoval()", "public void setRemoved()",
            "metadata.decommissioned().write(station)",
            "instanceof IntTag energyTag", "energyTag.getAsInt() <= ENERGY_CAPACITY",
            "loadValidatedTank(", "loaded.getAmount() <= capacity", "validator.test(loaded)",
            'tag.get("CommissioningProgress") instanceof IntTag progressTag',
            "progressTag.getAsInt() < COMMISSIONING_TICKS",
            "VALID_STATUSES.contains(loadedStatus)",
        ),
        "station services controller",
        failures,
    )
    if "readFromNBT" in controller:
        failures.append("controller persistence bypasses validation with FluidTank.readFromNBT")
    if controller.count("IFluidHandler.FluidAction.SIMULATE") != 2:
        failures.append("station services controller resource SIMULATE checks drifted")
    unload = method_slice(controller, "public void setRemoved()", "protected void saveAdditional(")
    if ("decommissioned()" in unload
            or "decommissionForBlockRemoval()" in unload
            or "commissioningProgress = 0" in unload
            or 'status = "removed"' in unload):
        failures.append("normal controller unload destroys durable commissioning state")

    scoop = (project / SCOOP_BE).read_text(encoding="utf-8-sig")
    require_tokens(
        scoop,
        (
            "implements BlockEntitySubLevelActor", "metadata.role() != StationRole.STATION",
            "StationServicesControllerBlockEntity.isLiveFor(station, metadata)",
            "StationLifeSupport.hasLiveCoverage(station, worldPosition)",
            "GasGiantOrbitVerifier.isInExtractionBand(station)",
            "ENERGY_PER_TICK = 8_192", "COOLANT_PER_TICK = 4",
            "CONDENSATE_PER_CYCLE = 1_000", "CYCLE_TICKS = 400",
            "IFluidHandler.FluidAction.SIMULATE", "IFluidHandler.FluidAction.EXECUTE",
            "energy.receiveEnergy(energyDebit, false)", "coolant.fill(coolantDebit",
            "IndustrialFluids.GAS_GIANT_CONDENSATE.get()", "progress = 0",
            "energyTag.getAsInt() <= ENERGY_CAPACITY", "loadValidatedTank(",
            'tag.get("Progress") instanceof net.minecraft.nbt.IntTag progressTag',
            "progressTag.getAsInt() < CYCLE_TICKS", "VALID_STATUSES.contains(loadedStatus)",
        ),
        "atmospheric scoop",
        failures,
    )
    if "readFromNBT" in scoop or "Items.WATER_BUCKET" in scoop:
        failures.append("scoop persistence/coolant validation is bypassable")
    combined = controller + scoop
    for token in ("teleportTo(", "changeDimension(", "performCommand("):
        if token in combined:
            failures.append(f"Stage13 machine invented out-of-scope movement/commands: {token}")


def validate_life_support_and_orbit(project: Path, failures: list[str]) -> None:
    life = (project / LIFE_SUPPORT).read_text(encoding="utf-8-sig")
    entity = method_slice(
        life,
        "public static boolean hasLiveCoverage(LivingEntity entity)",
        "/** Checks a plot-space block",
    )
    block = method_slice(life, "public static boolean hasLiveCoverage(ServerSubLevel subLevel")
    require_tokens(
        entity,
        (
            "DEEP_SPACE.equals(entity.level().dimension())",
            "Sable.HELPER.getTrackingOrVehicleSubLevel(entity)",
            "subLevel.getLevel() != entity.level()",
            "logicalPose().transformPositionInverse(entity.getEyePosition())",
            "StationServicesControllerBlockEntity.isLiveFor(subLevel, metadata)",
        ),
        "deep-space breathing coverage",
        failures,
    )
    require_tokens(
        block,
        (
            "subLevel.getPlot().getLoadedChunks()",
            "Sable.HELPER.getContaining(blockEntity) != subLevel",
            "industrialColonies$isLive()", "industrialColonies$lastVerifiedTick()",
            "covered.contains(plotPosition)",
        ),
        "same-sublevel distributor coverage",
        failures,
    )
    if "DEEP_SPACE.equals" in block:
        failures.append("surface SHIP services incorrectly require the deep-space dimension")
    for token in ("trackingPlayers", "boundingBox()", ".inflate(", "OxygenApi"):
        if token in life:
            failures.append(f"life-support identity reverted to an unsafe shortcut: {token}")

    orbit = (project / ORBIT_VERIFIER).read_text(encoding="utf-8-sig")
    require_tokens(
        orbit,
        (
            'GAS_GIANT_FRAME = "gas_giant"', "MIN_EXTRACTION_ALTITUDE = 250_000.0D",
            "MAX_EXTRACTION_ALTITUDE = 2_500_000.0D", "DeepSpaceData.getInstance(",
            "getInstanceForPos(", "station.logicalPose().position()",
            "(int) pose.x()", "(int) pose.z()",
            "position.getFrame() != gasGiant.orekitFrame()", "DeepSpaceHelper.isSphereShape()",
            "getRotationAtTime(position.getLocalUniverseTime())", ".applyInverseTo(",
            "position.getPosition(gasGiant.orekitFrame())",
            "Math.max(0.0D, Math.abs(bodyPosition.getX()) - gasGiant.radius())",
            "Math.max(0.0D, Math.abs(bodyPosition.getY()) - gasGiant.radius())",
            "Math.max(0.0D, Math.abs(bodyPosition.getZ()) - gasGiant.radius())",
            "Math.sqrt(dx * dx + dy * dy + dz * dz)", "Double.isFinite(altitude)",
        ),
        "gas-giant CUBE-shell verifier",
        failures,
    )
    if "getNorm() - gasGiant.radius()" in orbit:
        failures.append("gas-giant verifier reverted to spherical altitude math")
    if "Math.floor(pose.x())" in orbit or "Math.floor(pose.z())" in orbit:
        failures.append("gas-giant instance lookup no longer matches installed cast semantics")

    oxygen = (project / OXYGEN_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(
        oxygen,
        (
            "private Set<BlockPos> lastDistributedBlocks", '@Invoker("calculateFluidPerTick")',
            '@Invoker("canCraftDistribution")', "at = @At(\"TAIL\")", "require = 1",
            "isLit()", "canFunction()", "distributedBlocksCount() > 0",
            "industrialColonies$canCraftDistribution(fluidPerTick)",
            'method = "onRemoved()V"',
        ),
        "Ad Astra oxygen bridge",
        failures,
    )
    live_query = method_slice(
        oxygen,
        "public boolean industrialColonies$isLive()",
        "public long industrialColonies$lastVerifiedTick()",
    )
    require_tokens(
        live_query,
        (
            "industrialColonies$live", "isLit()", "canFunction()",
            "distributedBlocksCount() > 0", "!lastDistributedBlocks.isEmpty()",
            "industrialColonies$calculateFluidPerTick()",
            "industrialColonies$canCraftDistribution(fluidPerTick)",
        ),
        "live oxygen revalidation",
        failures,
    )
    breath = (project / BREATH_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(
        breath,
        (
            "@ModifyExpressionValue",
            'method = "onLivingBreathe(Lnet/neoforged/neoforge/event/entity/living/LivingBreatheEvent;)V"',
            'target = "Ljava/util/EnumSet;contains(Ljava/lang/Object;)Z"',
            "require = 1", "drowning && !StationLifeSupport.hasLiveCoverage(event.getEntity())",
        ),
        "Cosmonautics breathing hook",
        failures,
    )
    if "@Inject" in breath or "LivingBreatheEvent.LOWEST" in breath:
        failures.append("breathing override is not limited to Cosmonautics' DROWNING expression")
    warper = (project / WARPER_MIXIN).read_text(encoding="utf-8-sig")
    require_tokens(
        warper,
        (
            "@ModifyExpressionValue", "WarpSubLevels(", "allocateNewSubLevel(",
            "require = 1", "source.getUserDataTag()", "destination.setUserDataTag(sourceData.copy())",
        ),
        "Sable user-data warp preservation",
        failures,
    )
    if "StationMetadata.ROOT_KEY" in warper or 'getCompound("industrial_colonies:station")' in warper:
        failures.append("warper copies only Industrial Colonies metadata instead of the whole user-data root")
    mixins = load_json(project / MIXINS_JSON).get("mixins", [])
    for name in (
        "OxygenDistributorBlockEntityMixin",
        "GlobalSpacePhysicsHandlerMixin",
        "SubLevelWarperUserDataMixin",
    ):
        if mixins.count(name) != 1:
            failures.append(f"Stage13 mixin registration drifted: {name}")


def validate_catalog(catalog: Path, failures: list[str]) -> None:
    csv_path = catalog / "recipes.csv" if catalog.is_dir() else catalog
    if not csv_path.is_file():
        failures.append(f"missing installed recipe catalog: {csv_path}")
        return
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    offenders = [
        row.get("recipe_id", "") for row in rows
        if "industrial_colonies:gas_giant_condensate_bucket" in str(row.get("outputs", ""))
    ]
    if offenders:
        failures.append(f"condensate bucket has a recipe bypass instead of station extraction: {offenders}")


def validate_installed(mods: Path, failures: list[str]) -> None:
    for name, (expected_jar_hash, classes) in DEPENDENCY_PINS.items():
        jar = mods / name
        if not jar.is_file():
            failures.append(f"missing pinned Stage13 dependency: {name}")
            continue
        if sha256(jar.read_bytes()) != expected_jar_hash:
            failures.append(f"installed Stage13 dependency hash drifted: {name}")
        try:
            with zipfile.ZipFile(jar) as archive:
                names = set(archive.namelist())
                for entry, expected_hash in classes.items():
                    if entry not in names:
                        failures.append(f"installed Stage13 dependency lacks class: {name}!/{entry}")
                    elif sha256(archive.read(entry)) != expected_hash:
                        failures.append(f"installed Stage13 dependency class drifted: {name}!/{entry}")
        except (OSError, zipfile.BadZipFile) as exc:
            failures.append(f"cannot inspect installed Stage13 dependency {jar}: {exc}")


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
        failures.append(f"candidate JAR lacks outer-station implementation entries: {missing}")


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
            failures.append(f"missing Stage13 source artifact: {relative.as_posix()}")
    if failures:
        return failures
    manifest_path = manifest.resolve() if manifest else project / MANIFEST
    compiled_path = compiled.resolve() if compiled else project / COMPILED
    validate_recipes(project, manifest_path, compiled_path, failures)
    validate_assignments_and_quests(project, failures)
    validate_registries_and_assets(project, failures)
    validate_metadata_and_services(project, failures)
    validate_life_support_and_orbit(project, failures)
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
        print("Outer-station extraction validation FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "Outer-station extraction validation passed: commissioned SHIP/STATION services, "
        "exact oxygen coverage, CUBE-shell gas extraction, physical condensate return, "
        "three 5x5 recipes, and four observation-only quests are intact."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
