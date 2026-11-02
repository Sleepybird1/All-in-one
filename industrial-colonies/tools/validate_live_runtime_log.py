#!/usr/bin/env python3
"""Validate an Industrial Colonies integrated-server acceptance launch.

The checker is intentionally read-only: it never changes the live instance.
Expected owned scripts, physical-progression stage count, and FTB Quests guidance
count are derived from the current project. Extra user-authored KubeJS server
scripts are allowed, but every project-owned script must be present in the most
recent KubeJS load block, recipe-event listener exceptions remain fatal, and
the most recent recipe-event summary must report zero failed recipes.

``latest.log`` supplies recipe, quest, and world-join evidence. ``debug.log``
supplies the exact Mixin application records needed to prove that the finite
TFMG reservoir, Dungeon Crawl worn-loot, Orbital Flight Computer transition,
managed Mars/Venus/Mercury descent gate, canonical deep-space asteroid
eligibility, and dimension-scoped water/wind suppression injections reached
their installed targets, rather than merely existing in source or in the
companion JAR.

JEI Uses/U-key markers require client interaction and therefore remain
diagnostic during unattended validation. Pass ``--require-jei-probes`` when
running the explicit interactive UI acceptance pass.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one")
DEFAULT_REPORT = PROJECT_ROOT.parent / "industrial-audit" / "LIVE_RUNTIME_ACCEPTANCE.json"

# These are the focused policies that remain active in the stock-recipe
# baseline. Stock-retention no-op scripts are covered by the owned-script load
# check and deliberately do not need individual execution markers here.
FOCUSED_POLICY_MESSAGES = {
    "physical_progression_mode": "Industrial Colonies loaded in physical recipe progression mode",
    "allthemodium_currency": "Manufactured ATM currencies loaded",
    "black_hole_megaproject": "Registered the staged 9x-compressed Black Hole megaproject recipe",
    "cast_iron_canonicalization": "Canonical TFMG cast iron loaded",
    "copper_wire_canonicalization": "Canonical TFMG copper wire loaded",
    "lead_canonicalization": "Canonical TFMG lead loaded",
    "petroleum_canonicalization": "Canonical TFMG petroleum loaded",
    "steel_canonicalization": "Canonical TFMG steel loaded",
    "sulfur_canonicalization": "Canonical TFMG sulfur chemistry loaded",
    "enriched_uranium_fuel": "Enriched Uranium Fuel loaded",
    "actinide_waste_bridge": "Canonical actinide waste bridge loaded",
    "yellorium_refinement": "Manufactured Yellorium alloy and refinement loaded",
    "yellorium_to_uranium_boundary": "Yellorium-to-uranium boundary loaded",
    "metallurgy_casting_repair": "Repaired 9 Create Metallurgy tag-output casting recipes",
    "megacells_repair": "Repaired the MEGA Radioactive Chemical Storage Cell",
    "space_entry_deferred": "stock Ad Astra space-entry recipes until the spaceflight expansion",
}

REPAIRED_RECIPE_IDS = (
    "createmetallurgy:casting_in_table/tin/nugget",
    "createmetallurgy:casting_in_basin/tin/block",
    "createmetallurgy:casting_in_table/tin/ingot",
    "createmetallurgy:casting_in_table/bronze/nugget",
    "createmetallurgy:casting_in_basin/bronze/block",
    "createmetallurgy:casting_in_table/bronze/ingot",
    "createmetallurgy:casting_in_table/osmium/nugget",
    "createmetallurgy:casting_in_basin/osmium/block",
    "createmetallurgy:casting_in_table/osmium/ingot",
    "megacells:cells/standard/radioactive_chemical_cell",
)

REPAIRED_COLONY4CC_CRAFTER_RECIPE_IDS = (
    "colony4cc:rgb_charge1",
    "colony4cc:rgb_charge2",
)

RETIRED_BROKEN_THIRD_PARTY_RECIPE_IDS = (
    "cbc_at:cutting/rocket_pod_breech_cast_mould",
    "cbc_at:cutting/rocket_pod_rail_cast_mould",
    "cbc_at:cutting/twin_autocannon_barrel_cast_mould",
    "create_factory:caramel_apple",
    "create_factory:caramel_roll",
    "create_factory:caramel_waffle",
    "supplementaries:integration/ash_bricks_salvaging_fd",
    "supplementaries:integration/lapis_bricks_salvaging_fd",
    "supplementaries:integration/quiver_fd",
)

SERVER_SCRIPT_SUMMARY_RE = re.compile(
    r"Loaded\s+(\d+)/(\d+)\s+KubeJS server scripts.*?with\s+"
    r"(\d+)\s+errors?\s+and\s+(\d+)\s+warnings?",
    flags=re.IGNORECASE,
)
SERVER_SCRIPT_LOAD_RE = re.compile(
    r"Loaded script server_scripts:(.+?\.js)\s+in\s+",
    flags=re.IGNORECASE,
)
KUBEJS_LISTENER_ERROR_RE = re.compile(
    r"^.*?\[KubeJS\s+(?:Server|Startup|Client)/\]:\s*"
    r".*?\bError in '([^']+)'\s*:\s*(.+)$",
    flags=re.IGNORECASE | re.MULTILINE,
)
KUBEJS_RECIPE_SUMMARY_RE = re.compile(
    r"Added\s+(\d+)\s+recipes?,\s+removed\s+(\d+)\s+recipes?,\s+"
    r"modified\s+(\d+)\s+recipes?,\s+with\s+(\d+)\s+failed\s+recipes?",
    flags=re.IGNORECASE,
)

JEI_USES_PROBE_RE = re.compile(
    r"IC_JEI_USES_PROBE\s+machine=(\S+)\s+status=(\S+)\s+"
    r"pre_runtime_bound=(\d+)\s+bound=(\d+)\s+supplier_input=(\d+)\s+"
    r"supplier_catalyst=(\d+)\s+focus_input_bound=(\d+)\s+"
    r"focus_catalyst_bound=(\d+)\s+categories_input=(\d+)\s+"
    r"categories_catalyst=(\d+)\s+focus_input_total=(\d+)\s+"
    r"focus_input_unbound=(\d+)\s+focus_input_other_machine=(\d+)\s+"
    r"bound_outputs=(\S+)\s+mechanical_native_expected=(\d+)\s+"
    r"mechanical_native_focused=(\d+)\s+mechanical_native_missing=(\d+)\s+"
    r"mechanical_bound_visible=(\d+)\s+mechanical_status=(\S+)",
    flags=re.IGNORECASE,
)

JEI_EXACT_U_FILTER_RE = re.compile(
    r"IC_JEI_EXACT_U_FILTER\s+machine=(\S+)\s+status=(\S+)\s+"
    r"roles_before=(\S+)\s+roles_after=(\S+)",
    flags=re.IGNORECASE,
)

OWNED_RUNTIME_MIXINS = {
    "finite_tfmg_oil_reservoir": {
        "mixin": "TFMGPumpjackFiniteReservoirMixin",
        "target": (
            "com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base."
            "PumpjackBaseBlockEntity"
        ),
    },
    "dungeon_crawl_worn_equipment": {
        "mixin": "DungeonCrawlRandomItemsMixin",
        "target": "xiroc.dungeoncrawl.dungeon.treasure.RandomItems",
    },
    "orbital_flight_computer_transition": {
        "mixin": "SpaceTransitionHandlerMixin",
        "target": "dev.devce.rocketnautics.content.physics.SpaceTransitionHandler",
    },
    "mars_navigation_computer_descent": {
        "mixin": "DeepSpaceInstanceMixin",
        "target": "dev.devce.rocketnautics.content.orbit.DeepSpaceInstance",
    },
    "deep_space_asteroid_eligibility": {
        "mixin": "AsteroidSpawnerMixin",
        "target": "dev.devce.rocketnautics.content.physics.AsteroidSpawner",
    },
    "station_oxygen_distributor_state": {
        "mixin": "OxygenDistributorBlockEntityMixin",
        "target": (
            "earth.terrarium.adastra.common.blockentities.machines."
            "OxygenDistributorBlockEntity"
        ),
    },
    "station_breathing_boundary": {
        "mixin": "GlobalSpacePhysicsHandlerMixin",
        "target": "dev.devce.rocketnautics.content.physics.GlobalSpacePhysicsHandler",
    },
    "station_whole_userdata_transfer": {
        "mixin": "SubLevelWarperUserDataMixin",
        "target": "dev.egg.SubLevelWarper",
    },
    "interstellar_source_removal_boundary": {
        "mixin": "SableRemovalBoundaryMixin",
        "target": "dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer",
    },
    "reinforced_reactor_plutonium_boundary": {
        "mixin": "ReactorSolidAccessPortEntityMixin",
        "target": (
            "it.zerono.mods.extremereactors.gamecontent.multiblock.reactor.part."
            "ReactorSolidAccessPortEntity"
        ),
    },
    "signed_interstellar_warp_boundary": {
        "mixin": "CosmowarpWarpDriveMixin",
        "target": "dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity",
    },
    "interstellar_packet_sender_boundary": {
        "mixin": "CosmowarpNetworkingMixin",
        "target": "dev.waco0311.cosmowarp.network.ModNetworking",
    },
    "interstellar_menu_open_boundary": {
        "mixin": "CosmowarpWarpDriveBlockMixin",
        "target": "dev.waco0311.cosmowarp.block.WarpDriveBlock",
    },
    "interstellar_menu_validity_boundary": {
        "mixin": "CosmowarpWarpDriveMenuMixin",
        "target": "dev.waco0311.cosmowarp.menu.WarpDriveMenu",
    },
    "interstellar_menu_click_boundary": {
        "mixin": "CosmowarpWarpDriveClickMixin",
        "target": "net.minecraft.world.inventory.AbstractContainerMenu",
    },
    "interstellar_crystal_owner_boundary": {
        "mixin": "CosmowarpCrystalSlotOwnerMixin",
        "target": "dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity$1",
    },
    "interstellar_crystal_capability_boundary": {
        "mixin": "CosmowarpCrystalSlotFreezeMixin",
        "target": "net.neoforged.neoforge.items.ItemStackHandler",
    },
    "interstellar_capability_wrapper_boundary": {
        "mixin": "CosmowarpCapabilityMixin",
        "target": "dev.waco0311.cosmowarp.Cosmonauticswarpdrive",
    },
    "orbital_ambient_hydro": {
        "mixin": "WaterWheelBlockEntityMixin",
        "target": (
            "com.simibubi.create.content.kinetics.waterwheel."
            "WaterWheelBlockEntity"
        ),
    },
    "orbital_ambient_wind": {
        "mixin": "WindmillBearingBlockEntityMixin",
        "target": (
            "com.simibubi.create.content.contraptions.bearing."
            "WindmillBearingBlockEntity"
        ),
    },
}

# A successful resource reload normally stays silent. These identifiers are
# therefore negative assurances: a decoder/reload error naming any of them is
# pack-owned and fatal, while unrelated stock-mod loot/data warnings remain
# outside this acceptance boundary.
OWNED_RUNTIME_RESOURCE_IDS = (
    "industrial_colonies:regional_oil_field",
    "industrial_colonies:add_regional_oil_fields",
    "industrial_colonies:remove_tfmg_global_oil_deposits",
    "rocketnautics:venus",
    "industrial_colonies:ad_astra_venus",
    "industrial_colonies:planetary/venus_arrival",
    "rocketnautics:mercury",
    "industrial_colonies:ad_astra_mercury",
    "industrial_colonies:planetary/mercury_arrival",
    "industrial_colonies:calorite_crushing_feed",
    "rocketnautics:proxima_centauri",
    "rocketnautics:glacio",
    "industrial_colonies:ad_astra_glacio",
    "industrial_colonies:planetary/glacio_arrival",
    "industrial_colonies:ad_astra_moon_crystal_ore",
    "industrial_colonies:add_ad_astra_moon_crystal_ore",
    "dungeonnowloading:chests/labyrinth/rewards/gears",
    "dungeonnowloading:chests/temple_of_duality/equipment/normal_puzzle",
    "dungeonnowloading:chests/temple_of_duality/equipment/hard_puzzle",
    "dungeonnowloading:chests/temple_of_duality/equipment/hard_combat",
    "dungeonnowloading:chests/temple_of_duality/equipment/normal_combat",
    "betterdungeons:zombie_dungeon/chests/common",
    "betterdungeons:zombie_dungeon/chests/special",
    "betterdungeons:zombie_dungeon/chests/tombstone",
)

MIXIN_FAILURE_MARKERS = (
    "mixin apply failed",
    "mixinapplyerror",
    "invalidinjectionexception",
    "injectionerror",
    "critical injection failure",
    "no class def found error",
    "noclassdeffounderror",
)

RESOURCE_FAILURE_MARKERS = (
    "error parsing",
    "parsing error",
    "failed to parse",
    "couldn't parse",
    "could not parse",
    "couldn't load",
    "could not load",
    "failed to load",
    "invalid data",
)


def load_expected_stage_count(project: Path) -> int:
    candidates = (
        project
        / "build/generated/recipeStages/data/industrial_colonies/progression/recipe_stages.json",
        project
        / "build/resources/main/data/industrial_colonies/progression/recipe_stages.json",
    )
    for path in candidates:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            recipes = data.get("recipes")
            if not isinstance(recipes, dict):
                raise ValueError(f"recipe-stage manifest has no recipes object: {path}")
            return len(recipes)
    raise FileNotFoundError("build the project before validating its runtime log")


def load_expected_quest_topology(project: Path) -> dict[str, int]:
    """Read the non-gating factory, dungeon, endgame, orbital, and planetary authorities.

    The MineColonies branch layout is not an FTB Quests chapter and must never
    be used to infer this count.
    """

    endgame_path = project / "progression/industrial_megaprojects.json"
    endgame = json.loads(endgame_path.read_text(encoding="utf-8"))
    endgame_quests = endgame.get("quests")
    if not isinstance(endgame_quests, list) or not endgame_quests:
        raise ValueError(f"megaproject config contains no quests list: {endgame_path}")

    campaign_path = project / "progression/ftbquests_guidance_campaign.json"
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    chapters = campaign.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise ValueError(f"guidance campaign contains no chapters: {campaign_path}")
    guidance_count = 0
    for chapter in chapters:
        quests = chapter.get("quests") if isinstance(chapter, dict) else None
        if not isinstance(quests, list) or not quests:
            raise ValueError(f"guidance campaign chapter contains no quests: {campaign_path}")
        guidance_count += len(quests)
    extension = campaign.get("chapter_extension")
    extension_chapter_count = 0
    if extension is not None:
        if not isinstance(extension, dict) or extension.get("status") != "implemented":
            raise ValueError(f"guidance campaign extension is not implemented: {campaign_path}")
        extension_path = Path(str(extension.get("path", "")))
        if not extension_path.is_absolute():
            extension_path = (campaign_path.parent / extension_path).resolve()
        extension_plan = json.loads(extension_path.read_text(encoding="utf-8-sig"))
        if extension_plan.get("status") != "implemented":
            raise ValueError(f"guidance campaign extension plan is not implemented: {extension_path}")
        extension_chapters = extension_plan.get("chapters")
        expected_keys = extension.get("chapter_keys")
        if (
            not isinstance(extension_chapters, list)
            or not isinstance(expected_keys, list)
            or [chapter.get("key") for chapter in extension_chapters] != expected_keys
        ):
            raise ValueError(f"guidance campaign extension chapter set changed: {extension_path}")
        for chapter in extension_chapters:
            quests = chapter.get("quests") if isinstance(chapter, dict) else None
            if not isinstance(quests, list) or not quests:
                raise ValueError(f"guidance extension chapter contains no quests: {extension_path}")
            guidance_count += len(quests)
        extension_chapter_count = len(extension_chapters)
    dungeon_path = project / "progression/ftbquests_dungeon_exploration.json"
    dungeon = json.loads(dungeon_path.read_text(encoding="utf-8"))
    dungeon_chapter = dungeon.get("chapter")
    dungeon_quests = dungeon_chapter.get("quests") if isinstance(dungeon_chapter, dict) else None
    if not isinstance(dungeon_quests, list) or not dungeon_quests:
        raise ValueError(f"dungeon campaign contains no chapter quests: {dungeon_path}")

    orbital_path = project / "progression/ftbquests_orbital_engineering.json"
    orbital = json.loads(orbital_path.read_text(encoding="utf-8"))
    orbital_chapter = orbital.get("chapter")
    orbital_quests = (
        orbital_chapter.get("quests") if isinstance(orbital_chapter, dict) else None
    )
    if not isinstance(orbital_quests, list) or not orbital_quests:
        raise ValueError(f"orbital campaign contains no chapter quests: {orbital_path}")

    planetary_path = project / "progression/ftbquests_planetary_industry.json"
    planetary = json.loads(planetary_path.read_text(encoding="utf-8"))
    planetary_chapter = planetary.get("chapter")
    planetary_quests = (
        planetary_chapter.get("quests") if isinstance(planetary_chapter, dict) else None
    )
    if not isinstance(planetary_quests, list) or not planetary_quests:
        raise ValueError(
            f"planetary campaign contains no chapter quests: {planetary_path}"
        )

    return {
        "chapters": len(chapters) + extension_chapter_count + 4,
        "quests": (
            guidance_count
            + len(dungeon_quests)
            + len(endgame_quests)
            + len(orbital_quests)
            + len(planetary_quests)
        ),
        "reward_tables": 0,
    }


def load_expected_quest_count(project: Path) -> int:
    """Compatibility helper retained for focused callers and tests."""

    return load_expected_quest_topology(project)["quests"]


def load_owned_server_scripts(project: Path) -> list[str]:
    root = project / "pack-scripts/server_scripts"
    if not root.is_dir():
        raise FileNotFoundError(root)
    scripts = sorted(path.relative_to(root).as_posix() for path in root.rglob("*.js"))
    if not scripts:
        raise ValueError(f"no owned KubeJS server scripts found in {root}")
    return scripts


def latest_match(pattern: str, text: str) -> re.Match[str] | None:
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
    return matches[-1] if matches else None


def parse_latest_server_script_load(text: str) -> dict[str, Any] | None:
    """Parse script names belonging to the most recent KubeJS load summary."""

    summaries = list(SERVER_SCRIPT_SUMMARY_RE.finditer(text))
    if not summaries:
        return None
    summary = summaries[-1]
    block_start = summaries[-2].end() if len(summaries) > 1 else 0
    block = text[block_start : summary.start()]
    script_names = sorted(set(SERVER_SCRIPT_LOAD_RE.findall(block)))
    loaded, total, errors, warnings = map(int, summary.groups())
    return {
        "loaded": loaded,
        "total": total,
        "errors": errors,
        "warnings": warnings,
        "script_names": script_names,
    }


def parse_ftb_quest_evidence(text: str) -> dict[str, Any]:
    server_match = latest_match(
        r"\[FTB Quests/\]:\s+Loaded\s+(\d+)\s+chapter groups?,\s+"
        r"(\d+)\s+chapters?,\s+(\d+)\s+quests?,\s+(\d+)\s+reward tables?",
        text,
    )
    client_match = latest_match(
        r"\[FTB Quests/\]:\s+Read\s+(\d+)\s+bytes,\s+(\d+)\s+objects",
        text,
    )
    evidence: dict[str, Any] = {"server": None, "client_sync": None}
    if server_match:
        groups, chapters, quests, reward_tables = map(int, server_match.groups())
        evidence["server"] = {
            "chapter_groups": groups,
            "chapters": chapters,
            "quests": quests,
            "reward_tables": reward_tables,
        }
    if client_match:
        bytes_read, objects = map(int, client_match.groups())
        # The object count is a network serialization detail, not a quest
        # count. Record it as corroborating evidence without applying the old
        # and brittle 2 + (quests * 2) formula.
        evidence["client_sync"] = {"bytes": bytes_read, "objects": objects}
    return evidence


def parse_owned_mixin_evidence(debug_text: str) -> dict[str, dict[str, Any]]:
    """Find exact successful application records for critical owned Mixins."""

    evidence: dict[str, dict[str, Any]] = {}
    for name, contract in OWNED_RUNTIME_MIXINS.items():
        mixin = contract["mixin"]
        target = contract["target"]
        pattern = re.compile(
            rf"Mixing\s+{re.escape(mixin)}\s+from\s+"
            rf"industrial_colonies\.mixins\.json\s+into\s+{re.escape(target)}"
            rf"(?=[ \t]*$)",
            flags=re.IGNORECASE | re.MULTILINE,
        )
        matches = list(pattern.finditer(debug_text))
        match = matches[-1] if matches else None
        evidence[name] = {
            "applied": match is not None,
            "mixin": mixin,
            "target": target,
            "line": (
                debug_text.count("\n", 0, match.start()) + 1 if match is not None else None
            ),
        }
    return evidence


def find_owned_mixin_failures(text: str) -> list[dict[str, Any]]:
    """Return only failure lines attributable to this companion's Mixins."""

    owned_tokens = ("industrial_colonies.mixins.json",) + tuple(
        contract["mixin"].lower() for contract in OWNED_RUNTIME_MIXINS.values()
    )
    failures: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if not any(token in lowered for token in owned_tokens):
            continue
        if not any(marker in lowered for marker in MIXIN_FAILURE_MARKERS):
            continue
        failures.append({"line": line_number, "message": line.strip()})
    return failures


def evaluate_owned_mixin_runtime(
    debug_text: str, combined_runtime_text: str
) -> dict[str, Any]:
    """Require every critical owned Mixin on its exact installed target."""

    evidence = parse_owned_mixin_evidence(debug_text)
    failures = find_owned_mixin_failures(combined_runtime_text)
    return {
        "pass": all(row["applied"] for row in evidence.values()) and not failures,
        "evidence": evidence,
        "failures": failures,
    }


def find_owned_resource_reload_errors(text: str) -> list[dict[str, Any]]:
    """Return decoder/reload failures for the owned oil and dungeon resources."""

    errors: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        resource_id = next(
            (resource for resource in OWNED_RUNTIME_RESOURCE_IDS if resource in lowered),
            None,
        )
        if resource_id is None:
            continue
        if not any(marker in lowered for marker in RESOURCE_FAILURE_MARKERS):
            continue
        errors.append(
            {"line": line_number, "resource": resource_id, "message": line.strip()}
        )
    return errors


def parse_kubejs_listener_errors(text: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for match in KUBEJS_LISTENER_ERROR_RE.finditer(text):
        errors.append(
            {
                "event": match.group(1),
                "message": match.group(2).strip(),
                "line": text.count("\n", 0, match.start()) + 1,
            }
        )
    return errors


def parse_latest_kubejs_recipe_summary(text: str) -> dict[str, int] | None:
    """Parse the latest ServerEvents.recipes result, including failures.

    KubeJS can load every script with zero syntax errors and still reject an
    individual recipe constructor later in the recipe event. Only the latest
    summary belongs to the active reload epoch.
    """

    matches = list(KUBEJS_RECIPE_SUMMARY_RE.finditer(text))
    if not matches:
        return None
    added, removed, modified, failed = map(int, matches[-1].groups())
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "failed": failed,
    }


def find_colony4cc_crafter_recipe_rejections(text: str) -> list[str]:
    """Find MineColonies rejections for the two repaired Colony4CC recipes."""

    return [
        recipe_id
        for recipe_id in REPAIRED_COLONY4CC_CRAFTER_RECIPE_IDS
        if re.search(
            rf"Error parsing crafterrecipe\s+{re.escape(recipe_id)}(?:\s|$)",
            text,
            flags=re.IGNORECASE,
        )
    ]


def find_retired_third_party_recipe_rejections(text: str) -> list[str]:
    """Find final RecipeManager errors for exact broken recipes retired by the pack.

    KubeJS may still log a nonfatal codec fallback while indexing a source
    recipe before exact removals run. The acceptance boundary is that the final
    RecipeManager no longer rejects and retains those recipes.
    """

    return [
        recipe_id
        for recipe_id in RETIRED_BROKEN_THIRD_PARTY_RECIPE_IDS
        if re.search(
            rf"(?:Error parsing recipe|Parsing error loading recipe)\s+"
            rf"{re.escape(recipe_id)}(?:\s|:)",
            text,
            flags=re.IGNORECASE,
        )
    ]


def is_acceptable_kubejs_recipe_summary(evidence: dict[str, int] | None) -> bool:
    """Require explicit proof that the active recipe reload rejected nothing."""

    return bool(evidence and evidence["failed"] == 0)


def parse_latest_jei_uses_probe(text: str) -> dict[str, Any] | None:
    """Parse the most recent exact-machine JEI focus-index acceptance marker.

    Deliberately require the v2 suffix. The original probe counted only bound
    matches inside known bound recipe types, so it could not detect an
    unrelated recipe leaking into the global Uses lookup.
    """

    matches = list(JEI_USES_PROBE_RE.finditer(text))
    if not matches:
        return None
    match = matches[-1]
    values = list(match.groups())
    return {
        "machine": values[0],
        "status": values[1].upper(),
        "pre_runtime_bound": int(values[2]),
        "bound": int(values[3]),
        "supplier_input": int(values[4]),
        "supplier_catalyst": int(values[5]),
        "focus_input_bound": int(values[6]),
        "focus_catalyst_bound": int(values[7]),
        "categories_input": int(values[8]),
        "categories_catalyst": int(values[9]),
        "focus_input_total": int(values[10]),
        "focus_input_unbound": int(values[11]),
        "focus_input_other_machine": int(values[12]),
        "bound_outputs": sorted(filter(None, values[13].split(","))),
        "mechanical_native_expected": int(values[14]),
        "mechanical_native_focused": int(values[15]),
        "mechanical_native_missing": int(values[16]),
        "mechanical_bound_visible": int(values[17]),
        "mechanical_status": values[18].upper(),
    }


def parse_latest_jei_exact_u_filter(text: str) -> dict[str, Any] | None:
    """Parse proof that the actual Copper Press Uses action was rewritten."""

    matches = list(JEI_EXACT_U_FILTER_RE.finditer(text))
    if not matches:
        return None
    machine, status, roles_before, roles_after = matches[-1].groups()
    return {
        "machine": machine,
        "status": status.upper(),
        "roles_before": roles_before.upper().split(","),
        "roles_after": roles_after.upper().split(","),
    }


def is_acceptable_jei_uses_probe(evidence: dict[str, Any] | None) -> bool:
    """Require dynamic, exclusive parity for every current Copper Press binding."""

    return bool(
        evidence
        and evidence["machine"] == "createcasing:copper_press"
        and evidence["status"] == "PASS"
        and evidence["bound"] > 0
        and evidence["pre_runtime_bound"] == evidence["bound"]
        and evidence["supplier_input"] == evidence["bound"]
        and evidence["supplier_catalyst"] == evidence["bound"]
        and evidence["focus_input_total"] == evidence["bound"]
        and evidence["focus_input_bound"] == evidence["bound"]
        and evidence["focus_catalyst_bound"] == evidence["bound"]
        and evidence["focus_input_unbound"] == 0
        and evidence["focus_input_other_machine"] == 0
        and evidence["categories_input"] > 0
        and bool(evidence["bound_outputs"])
        and evidence["mechanical_status"] == "PASS"
        and evidence["mechanical_native_expected"] > 0
        and evidence["mechanical_native_focused"]
        == evidence["mechanical_native_expected"]
        and evidence["mechanical_native_missing"] == 0
    )


def is_acceptable_jei_exact_u_filter(evidence: dict[str, Any] | None) -> bool:
    """Require proof that the real Copper Press U path became INPUT-only."""

    return bool(
        evidence
        and evidence["machine"] == "createcasing:copper_press"
        and evidence["status"] == "APPLIED"
        and evidence["roles_before"] == ["INPUT", "CATALYST"]
        and evidence["roles_after"] == ["INPUT"]
    )


def gate_optional_runtime_probe(observed_pass: bool, required: bool) -> bool:
    """Keep interactive UI evidence outside unattended core acceptance."""

    return observed_pass if required else True


def focused_policy_evidence(text: str) -> dict[str, dict[str, object]]:
    """Return the required runtime marker evidence for every focused owner."""

    return {
        name: {"pass": message in text, "required_message": message}
        for name, message in FOCUSED_POLICY_MESSAGES.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--project", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--world", default="Industrial Colonies Runtime Test")
    parser.add_argument(
        "--require-jei-probes",
        action="store_true",
        help=(
            "Require the interactive Copper Press JEI Uses/U-key markers. "
            "They are recorded but non-gating during unattended core acceptance by default."
        ),
    )
    args = parser.parse_args()

    project = args.project.resolve()
    pack = args.pack.resolve()
    log_path = pack / "logs/latest.log"
    if not log_path.is_file():
        raise FileNotFoundError(log_path)
    text = log_path.read_text(encoding="utf-8", errors="replace")
    debug_log_path = pack / "logs/debug.log"
    if not debug_log_path.is_file():
        raise FileNotFoundError(debug_log_path)
    debug_text = debug_log_path.read_text(encoding="utf-8", errors="replace")
    combined_runtime_text = text + "\n" + debug_text

    expected_owned_scripts = load_owned_server_scripts(project)
    expected_owned_set = set(expected_owned_scripts)
    expected_stage_count = load_expected_stage_count(project)
    expected_quest_topology = load_expected_quest_topology(project)
    expected_quest_count = expected_quest_topology["quests"]

    checks: dict[str, dict[str, object]] = {}

    script_actual = parse_latest_server_script_load(text)
    loaded_script_set = set(script_actual["script_names"]) if script_actual else set()
    missing_owned_scripts = sorted(expected_owned_set - loaded_script_set)
    additional_scripts = sorted(loaded_script_set - expected_owned_set)
    script_pass = bool(
        script_actual
        and script_actual["loaded"] == script_actual["total"]
        and script_actual["total"] >= len(expected_owned_scripts)
        and script_actual["errors"] == 0
        and script_actual["warnings"] == 0
        and not missing_owned_scripts
    )
    checks["kubejs_server_scripts"] = {
        "pass": script_pass,
        "expected_owned_count": len(expected_owned_scripts),
        "missing_owned_scripts": missing_owned_scripts,
        "additional_user_scripts": additional_scripts,
        "actual": script_actual,
    }

    stage_match = latest_match(r"Loaded\s+(\d+)\s+shared recipe-stage mappings", text)
    actual_stage_count = int(stage_match.group(1)) if stage_match else None
    if expected_stage_count == 0:
        stage_pass = actual_stage_count in (None, 0)
        stage_evidence = "marker absent (valid for zero mappings)" if stage_match is None else "zero marker"
    else:
        stage_pass = actual_stage_count == expected_stage_count
        stage_evidence = "counted marker" if stage_match else "marker absent"
    checks["shared_recipe_stages"] = {
        "pass": stage_pass,
        "expected": expected_stage_count,
        "actual": actual_stage_count,
        "evidence": stage_evidence,
    }

    checks.update(focused_policy_evidence(text))

    listener_errors = parse_kubejs_listener_errors(text)
    checks["kubejs_listener_exceptions"] = {
        "pass": not listener_errors,
        "count": len(listener_errors),
        "errors": listener_errors,
    }

    recipe_summary = parse_latest_kubejs_recipe_summary(text)
    checks["kubejs_recipe_construction"] = {
        "pass": is_acceptable_kubejs_recipe_summary(recipe_summary),
        "required_failed_count": 0,
        "evidence": recipe_summary,
    }

    repaired_rejections = [
        recipe_id
        for recipe_id in REPAIRED_RECIPE_IDS
        if re.search(
            rf"Parsing error loading recipe\s+{re.escape(recipe_id)}(?:\s|:)",
            text,
            flags=re.IGNORECASE,
        )
    ]
    checks["repaired_recipe_rejections"] = {
        "pass": not repaired_rejections,
        "unexpected_rejections": repaired_rejections,
    }

    colony4cc_rejections = find_colony4cc_crafter_recipe_rejections(text)
    checks["colony4cc_crafter_recipe_compat"] = {
        "pass": not colony4cc_rejections,
        "unexpected_rejections": colony4cc_rejections,
    }

    third_party_rejections = find_retired_third_party_recipe_rejections(text)
    checks["retired_broken_third_party_recipes"] = {
        "pass": not third_party_rejections,
        "unexpected_rejections": third_party_rejections,
    }

    bcl_conflict = bool(
        re.search(
            r"betterchunkloading.*(?:InvalidInjectionException|Mixin apply .* failed)|"
            r"InvalidInjectionException.*betterchunkloading",
            text,
            flags=re.IGNORECASE,
        )
    )
    checks["betterchunkloading_c2me_conflict"] = {
        "pass": not bcl_conflict,
        "conflict_found": bcl_conflict,
    }

    checks["critical_owned_mixins_applied"] = evaluate_owned_mixin_runtime(
        debug_text, combined_runtime_text
    )

    owned_resource_errors = find_owned_resource_reload_errors(combined_runtime_text)
    checks["oil_and_dungeon_resources_decoded"] = {
        "pass": not owned_resource_errors,
        "expected_silent_resources": list(OWNED_RUNTIME_RESOURCE_IDS),
        "errors": owned_resource_errors,
    }

    ftb_evidence = parse_ftb_quest_evidence(text)
    ftb_server = ftb_evidence["server"]
    ftb_pass = bool(
        ftb_server
        and ftb_server["chapter_groups"] >= 1
        and ftb_server["chapters"] == expected_quest_topology["chapters"]
        and ftb_server["quests"] == expected_quest_count
        and ftb_server["reward_tables"] == expected_quest_topology["reward_tables"]
        and ftb_evidence["client_sync"]
        and ftb_evidence["client_sync"]["bytes"] > 0
        and ftb_evidence["client_sync"]["objects"] > 0
    )
    checks["ftb_quests_loaded"] = {
        "pass": ftb_pass,
        "expected": expected_quest_topology,
        "requires_client_sync": True,
        "evidence": ftb_evidence,
    }

    fresh_world_started = args.world in text and "joined the game" in text
    checks["fresh_world_join"] = {
        "pass": fresh_world_started,
        "world": args.world,
    }

    jei_probe = parse_latest_jei_uses_probe(text)
    jei_probe_pass = is_acceptable_jei_uses_probe(jei_probe)
    checks["jei_exact_machine_uses"] = {
        "pass": gate_optional_runtime_probe(jei_probe_pass, args.require_jei_probes),
        "required": args.require_jei_probes,
        "observed_pass": jei_probe_pass,
        "expected_machine": "createcasing:copper_press",
        "expected_policy": "dynamic exact-binding parity",
        "focus_role": "INPUT",
        "requires_zero_unbound_or_other_machine_leaks": True,
        "evidence": jei_probe,
    }

    jei_filter = parse_latest_jei_exact_u_filter(text)
    jei_filter_pass = is_acceptable_jei_exact_u_filter(jei_filter)
    checks["jei_exact_u_ui_path"] = {
        "pass": gate_optional_runtime_probe(jei_filter_pass, args.require_jei_probes),
        "required": args.require_jei_probes,
        "observed_pass": jei_filter_pass,
        "expected_machine": "createcasing:copper_press",
        "expected_roles_before": ["INPUT", "CATALYST"],
        "expected_roles_after": ["INPUT"],
        "evidence": jei_filter,
    }

    all_passed = all(bool(check["pass"]) for check in checks.values())
    report = {
        "schema": 11,
        "log": str(log_path),
        "debug_log": str(debug_log_path),
        "project": str(project),
        "architecture": "stock_recipe_baseline",
        "expected_owned_server_scripts": expected_owned_scripts,
        "expected_recipe_stage_mappings": expected_stage_count,
        "expected_ftb_quests": expected_quest_topology,
        "interactive_jei_probes_required": args.require_jei_probes,
        "checks": checks,
        "pass": all_passed,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    for name, check in checks.items():
        print(f"{'PASS' if check['pass'] else 'FAIL'} {name}")
    print(f"{'PASS' if all_passed else 'FAIL'} runtime acceptance")
    print(f"report: {args.report.resolve()}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
