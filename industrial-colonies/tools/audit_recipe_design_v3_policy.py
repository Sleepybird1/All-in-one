#!/usr/bin/env python3
"""Strict, read-only policy audit for the recipe-design-v3 managed seed.

This audit is deliberately independent of the recipe generators.  It reads a
seed, optionally applies explicitly requested transforms in memory, invokes the
complete recipe-design-v2 structural/graph audit, and then enforces the v3
design decisions that are easy to regress while recipes are being rewritten.

The script never writes the seed, catalog, project, or live Minecraft instance.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import audit_recipe_design_v2_seed as v2


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_CATALOG = (
    ROOT.parents[1] / "outputs" / "recipe-catalog-current" / "recipe_catalog.sqlite"
)

INDUSTRIAL_DEPLOYER = "createcasing:industrial_iron_deployer"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"

FACTORY_PROCESSES = (
    "combining",
    "compressing",
    "crushing",
    "enriching",
    "infusing",
    "injecting",
    "purifying",
    "sawing",
    "smelting",
)
FACTORY_TIERS = ("basic", "advanced", "elite", "ultimate")
FACTORY_STOCK_IDS = frozenset(
    f"mekanism:factory/{tier}/{process}"
    for tier in FACTORY_TIERS
    for process in FACTORY_PROCESSES
)
FACTORY_OUTPUTS = frozenset(
    f"mekanism:{tier}_{process}_factory"
    for tier in FACTORY_TIERS
    for process in FACTORY_PROCESSES
)

# These are the process machines specifically claimed by recipe-design-v3.
# Treating this as an explicit contract is safer than guessing from every item
# in the Mekanism namespace (which also contains parts, tanks, and cables).
MEKANISM_PROCESS_MACHINE_IDS = frozenset(
    {
        "industrial_colonies:mekanism/combiner",
        "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber",
        "industrial_colonies:mekanism_pre_nuclear/osmium_compressor",
        "industrial_colonies:mekanism_pre_nuclear/crusher",
        "industrial_colonies:mekanism_pre_nuclear/precision_sawmill",
        "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator",
        "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer",
        "industrial_colonies:mekanism_pre_nuclear/chemical_infuser",
        "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber",
        "industrial_colonies:mekanism_pre_nuclear/modification_station",
        "industrial_colonies:mekanism_pre_nuclear/pigment_extractor",
        "industrial_colonies:mekanism_pre_nuclear/pigment_mixer",
        "industrial_colonies:mekanism_pre_nuclear/painting_machine",
        "industrial_colonies:planetary/outpost/nutritional_liquifier",
        "industrial_colonies:mekanism_pre_nuclear/seismic_vibrator",
    }
)
MEKANISM_INSTALLER_IDS = (
    "industrial_colonies:mekanism/tier_installer/basic",
    "industrial_colonies:mekanism/tier_installer/advanced",
    "industrial_colonies:mekanism/tier_installer/elite",
    "industrial_colonies:mekanism/tier_installer/ultimate",
)
LATE_TRANSMISSION_IDS = frozenset(
    f"industrial_colonies:mekanism/transmission/{tier}_{family}"
    for tier in ("elite", "ultimate")
    for family in (
        "logistical_transporter",
        "mechanical_pipe",
        "pressurized_tube",
        "thermodynamic_conductor",
        "universal_cable",
    )
)

REVIEW_RETIRED_LATE_TRANSMISSION = {
    "industrial_colonies:mekanism/transmission/elite_universal_cable": (
        "mekanism:transmitter/universal_cable/elite",
        "mekanism:elite_universal_cable",
    ),
    "industrial_colonies:mekanism/transmission/ultimate_mechanical_pipe": (
        "mekanism:transmitter/mechanical_pipe/ultimate",
        "mekanism:ultimate_mechanical_pipe",
    ),
    "industrial_colonies:mekanism/transmission/ultimate_universal_cable": (
        "mekanism:transmitter/universal_cable/ultimate",
        "mekanism:ultimate_universal_cable",
    ),
}

SPATIAL_ANCHOR = "ae2:spatial_anchor"
CHUNK_CONTROLLER = "advancedperipherals:chunk_controller"
SPATIAL_CORE = "ae2:spatial_cell_component_128"
ENGINE_CYLINDER = "tfmg:engine_cylinder"
ULTIMATE_ENERGY_CUBE = "mekanism:ultimate_energy_cube"

# Only these established recipes may use a 5x5 grid without another policy
# decision.  Quantum Crafter is evaluated separately and is admitted only when
# its grid passes the physical-diversity test below.
APPROVED_FIVE_BY_FIVE = frozenset(
    {
        "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker",
        "industrial_colonies:mekanism/storage/advanced_energy_cube",
        "industrial_colonies:mekanism/storage/elite_energy_cube",
        "industrial_colonies:mekanism/storage/ultimate_energy_cube",
        "industrial_colonies:advanced_ae/reaction_chamber",
        "industrial_colonies:world_loading/chunk_controller",
        "industrial_colonies:interstellar/warp_drive",
    }
)
QUANTUM_CRAFTER_ID = "industrial_colonies:v3_ae2/quantum_crafter"

# These border-heavy grids are consciously retained.  The comments here make
# the exception reviewable: this is not a generic escape hatch for ring recipes.
RING_GRID_ALLOWLIST = {
    # Energy Cubes are literal dense battery packs; their outer material shell
    # and increasingly populated center are the one approved ring progression.
    "industrial_colonies:mekanism/storage/advanced_energy_cube": "dense battery shell",
    "industrial_colonies:mekanism/storage/elite_energy_cube": "dense battery shell",
    "industrial_colonies:mekanism/storage/ultimate_energy_cube": "dense battery shell",
    # These three full assemblies were individually approved as recognizable
    # electrical/reactor/control hardware rather than generic material gates.
    "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker": "reviewed breaker body",
    "industrial_colonies:advanced_ae/reaction_chamber": "reviewed reaction machine",
    "industrial_colonies:world_loading/chunk_controller": "reviewed controller computer",
    # Exact, physically legible low-tier silhouettes.  These are not generic
    # "put expensive things around the old recipe" gates: every entry depicts
    # a spool, laminated mass, duct, vessel, frame, magazine, or drive path and
    # is required to retain its explanatory managed-recipe comment.
    "industrial_colonies:grid/copper_wire_spool": "wire wound around its spool",
    "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head": "laminated hammer mass",
    "industrial_colonies:engines/turbine_engine": "turbine duct and blade silhouette",
    "industrial_colonies:heavy_industry/scorched_alloyer": "refractory vessel around mixer",
    "industrial_colonies:space/life_support/airlock": "sealed double-door silhouette",
    "industrial_colonies:create_core/basin": "open-topped folded vessel",
    "industrial_colonies:create_core/empty_blaze_burner": "open capture cage",
    "industrial_colonies:create_core/fluid_tank_batch": "hollow tank shells",
    "industrial_colonies:create_core/chain_conveyor_batch": "opposed sprocket and chain paths",
    "industrial_colonies:diesel_generators_coverage/canister": "hollow valved canister",
    "industrial_colonies:create_core/gantry_shaft_batch": "long rail and shaft laminate",
    "industrial_colonies:create_core/item_vault_batch": "vault shell around barrel interiors",
    "industrial_colonies:create_addons/item_silo": "vertical bin around vault body",
    "industrial_colonies:big_cannons/autocannon_ammo_container": "open ammunition well",
    "industrial_colonies:big_cannons/heavy_autocannon_ammo_box": "plated magazine body",
    "industrial_colonies:create_connected/cross_connector": "four-way visible load path",
}

# Finished machines generally belong in a meaningful sequence or physical
# mechanical grid.  These are the two exact machine-like compacting exceptions
# approved during review; each still must carry an explanatory recipe comment.
REVIEWED_COMPACTING_MACHINE_EXCEPTIONS = {
    "modernfoundry:seared_melter": "rigid foundry vessel compacted as a single body",
    "tfmg:engine_cylinder": "approved Industrial Iron cylinder subassembly",
}

# Exact simple/bulk parts whose names do not carry a conventional part suffix.
# Keeping this list exact makes a newly compacted ``*_block`` or ``*_tank`` fail
# closed instead of accidentally permitting a finished machine with that name.
REVIEWED_COMPACTING_PART_EXCEPTIONS = {
    "bigreactors:basic_turbinerotorblade": "bulk turbine blade pressing",
    "bigreactors:basic_turbinerotorshaft": "bulk turbine shaft pressing",
    "bigreactors:reinforced_turbinerotorblade": "reinforced blade pressing",
    "bigreactors:reinforced_turbinerotorshaft": "reinforced shaft pressing",
    "mekanism:thermal_evaporation_block": "batch structural evaporation wall",
    "mekanism:dynamic_tank": "batch structural tank wall",
    "ad_astra:wheel": "paired rover wheel forming",
    "create_connected:brass_chute": "batch sheet-metal chute forming",
    "tfmg:pumpjack_hammer_part": "pressure-forged small walking-beam pivot batch",
    "tfmg:large_pumpjack_hammer_part": "pressure-forged large walking-beam pivot",
    "tfmg:large_pumpjack_hammer_connector": "pressure-forged large walking-beam connector",
    "tfmg:pumpjack_hammer_head": "pressure-forged pumpjack wear head",
    "tfmg:large_pumpjack_hammer_head": "pressure-forged large pumpjack wear head",
    "tfmg:pumpjack_hammer_connector": "pressure-fitted walking-beam pivot connector",
}

# Concrete fallback used only if the catalog is unavailable.  With a catalog,
# whole-processor Inscriber routes are discovered from recipe type and output.
KNOWN_WHOLE_PROCESSOR_INSCRIBER_IDS = frozenset(
    {
        "ae2:inscriber/logic_processor",
        "ae2:inscriber/calculation_processor",
        "ae2:inscriber/engineering_processor",
        "appliedcreate:inscriber/stress_processor",
        "appliedcreate:inscriber/advanced_stress_processor",
        "megacells:inscriber/accumulation_processor",
        "extendedae:inscriber/concurrent_process",
        "advanced_ae:quantum_processor",
    }
)

COUNT_PREFIX = re.compile(r"^\s*(\d+)x\s+")


def _recipe_id(recipe: Mapping[str, Any]) -> str:
    return str(recipe.get("id", "<missing-id>"))


def _output_count(value: Any, expected_item: str) -> int | None:
    """Return the exact count when *value* produces *expected_item*."""

    if isinstance(value, str):
        item = v2.exact_item(value)
        if item != expected_item:
            return None
        match = COUNT_PREFIX.match(value)
        return int(match.group(1)) if match else 1
    if not isinstance(value, Mapping) or v2.exact_item(value) != expected_item:
        return None
    for field in ("count", "amount"):
        count = value.get(field)
        if isinstance(count, int) and not isinstance(count, bool):
            return count
    return 1


def _managed_producers(
    recipes: Iterable[Mapping[str, Any]], output: str
) -> list[Mapping[str, Any]]:
    return [recipe for recipe in recipes if output in v2.recipe_outputs(recipe)]


def _all_removal_owners(
    seed: Mapping[str, Any], recipes: Iterable[Mapping[str, Any]]
) -> dict[str, list[str]]:
    owners: defaultdict[str, list[str]] = defaultdict(list)
    for recipe in recipes:
        for stock_id in recipe.get("remove", []):
            owners[str(stock_id)].append(_recipe_id(recipe))
    for stock_id in seed.get("additional_removals", []):
        owners[str(stock_id)].append("<additional_removals>")
    return dict(owners)


def _material_token(value: Any) -> str:
    exact = v2.exact_item(value)
    if exact:
        return exact
    if isinstance(value, str):
        return COUNT_PREFIX.sub("", value.strip())
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _grid_tokens(recipe: Mapping[str, Any]) -> list[list[str | None]] | None:
    if recipe.get("type") not in {"shaped", "mechanical_crafting"}:
        return None
    pattern = recipe.get("pattern")
    key = recipe.get("key")
    if not isinstance(pattern, list) or not pattern or not isinstance(key, Mapping):
        return None
    if not all(isinstance(row, str) for row in pattern):
        return None
    widths = {len(row) for row in pattern}
    if len(widths) != 1:
        return None
    return [
        [None if symbol == " " else _material_token(key.get(symbol)) for symbol in row]
        for row in pattern
    ]


def _quantum_grid_is_physically_diverse(recipe: Mapping[str, Any]) -> bool:
    """Require a populated, multi-part machine rather than a material frame."""

    grid = _grid_tokens(recipe)
    if grid is None or len(grid) != 5 or any(len(row) != 5 for row in grid):
        return False
    occupied = [token for row in grid for token in row if token]
    interior = [grid[y][x] for y in range(1, 4) for x in range(1, 4) if grid[y][x]]
    counts = Counter(occupied)
    comment = str(recipe.get("comment", "")).strip()
    return (
        len(occupied) >= 17
        and len(counts) >= 7
        and max(counts.values(), default=25) <= 8
        and grid[2][2] is not None
        and len(set(interior)) >= 5
        and len(comment) >= 80
    )


def _is_low_diversity_border(recipe: Mapping[str, Any]) -> bool:
    grid = _grid_tokens(recipe)
    if grid is None:
        return False
    height = len(grid)
    width = len(grid[0]) if grid else 0
    if height < 3 or width < 3:
        return False
    border = [
        grid[y][x]
        for y in range(height)
        for x in range(width)
        if y in {0, height - 1} or x in {0, width - 1}
    ]
    occupied = [token for token in border if token]
    if len(occupied) * 8 < len(border) * 7:  # fewer than 87.5% occupied
        return False
    counts = Counter(occupied)
    return len(counts) <= 2 or max(counts.values(), default=0) * 8 >= len(occupied) * 5


def _is_finished_storage_cell(output: str) -> bool:
    if ":" not in output:
        return False
    namespace, path = output.split(":", 1)
    return (
        namespace in {"ae2", "megacells", "appliedcreate"}
        and "storage_cell_" in path
        and "housing" not in path
        and "component" not in path
    )


def _is_allowed_compacted_part(output: str) -> bool:
    """Classify reviewed bulk/rigid/pressed parts, never finished AE cells."""

    if _is_finished_storage_cell(output):
        return False
    if output in REVIEWED_COMPACTING_MACHINE_EXCEPTIONS:
        return True
    if output in REVIEWED_COMPACTING_PART_EXCEPTIONS:
        return True
    if output == "create:refined_radiance":
        return True
    if ":" not in output:
        return False
    path = output.split(":", 1)[1]
    pressed_electronics = (
        path.startswith("printed_")
        or "circuit_board" in path
        or "semiconductor" in path
        or path.endswith(("capacitor", "transistor", "resistor", "memory_card"))
        or output == "computercraft:monitor_normal"
    )
    if pressed_electronics:
        return True
    structural_markers = (
        "casing",
        "housing",
        "_panel",
        "_plating",
        "_sheet",
        "_plate",
        "_wire",
        "_cable",
        "_pipe",
        "_tube",
        "_conductor",
        "_transporter",
        "_insulator",
        "_segment",
        "_rod",
        "_brick",
        "_bricks",
        "_reinforcement",
        "_duct",
        "_glass",
        "_blade",
        "_shaft",
        "_wheel",
        "_piston",
        "_charge",
        "_basin",
        "_table",
        "_drain",
        "_lid",
        "_plug",
        "_cylinder",
    )
    return any(marker in path for marker in structural_markers)


def _looks_like_finished_machine(output: str) -> bool:
    if ":" not in output:
        return False
    path = output.split(":", 1)[1]
    suffixes = (
        "anchor",
        "controller",
        "computer",
        "terminal",
        "drive",
        "monitor",
        "printer",
        "inscriber",
        "assembler",
        "assemblicator",
        "crafter",
        "chamber",
        "separator",
        "oxidizer",
        "infuser",
        "compressor",
        "crusher",
        "sawmill",
        "smelter",
        "liquifier",
        "vibrator",
        "miner",
        "mixer",
        "generator",
        "reactor",
        "turbine",
        "heater",
        "station",
        "teleporter",
        "deployer",
        "press",
        "pump",
        "furnace",
        "centrifuge",
        "evaporator",
        "melter",
    )
    return path.endswith(suffixes)


def _whole_processor_inscriber_ids(catalog: Path) -> set[str]:
    if not catalog.is_file():
        return set(KNOWN_WHOLE_PROCESSOR_INSCRIBER_IDS)
    connection = sqlite3.connect(catalog)
    try:
        discovered: set[str] = set()
        for recipe_id, outputs, recipe_type in connection.execute(
            "SELECT recipe_id, outputs, recipe_type FROM recipes "
            "WHERE recipe_type = 'ae2:inscriber' OR recipe_id LIKE '%inscriber/%'"
        ):
            if not isinstance(recipe_id, str) or not isinstance(outputs, str):
                continue
            for raw_output in outputs.split("|"):
                output = raw_output.strip()
                if ":" not in output:
                    continue
                path = output.split(":", 1)[1]
                if (
                    path.endswith("processor")
                    and not path.startswith("printed_")
                    and "processor_press" not in path
                ):
                    discovered.add(recipe_id)
        return discovered or set(KNOWN_WHOLE_PROCESSOR_INSCRIBER_IDS)
    finally:
        connection.close()


def _catalog_factory_ids(catalog: Path) -> set[str]:
    if not catalog.is_file():
        return set()
    connection = sqlite3.connect(catalog)
    try:
        return {
            row[0]
            for row in connection.execute(
                "SELECT recipe_id FROM recipes WHERE recipe_id LIKE 'mekanism:factory/%'"
            )
            if isinstance(row[0], str)
        }
    finally:
        connection.close()


def _run_v2_regression(
    seed: Mapping[str, Any], catalog: Path, quantum_full_and_approved: bool
) -> tuple[list[str], list[str], list[str]]:
    """Invoke v2 while preserving its global reviewed-grid configuration."""

    original = set(v2.JUSTIFIED_FULL_FIVE_BY_FIVE)
    reviewed = set(APPROVED_FIVE_BY_FIVE)
    # Quantum Crafter is currently a partially open 5x5, but include it here
    # if it ever becomes full after passing the same physical-diversity test.
    if quantum_full_and_approved:
        reviewed.add(QUANTUM_CRAFTER_ID)
    v2.JUSTIFIED_FULL_FIVE_BY_FIVE.clear()
    v2.JUSTIFIED_FULL_FIVE_BY_FIVE.update(reviewed)
    try:
        return v2.audit(seed, catalog)
    finally:
        v2.JUSTIFIED_FULL_FIVE_BY_FIVE.clear()
        v2.JUSTIFIED_FULL_FIVE_BY_FIVE.update(original)


def audit(
    seed: Mapping[str, Any], catalog: Path
) -> tuple[list[str], list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    counts: Counter[str] = Counter()
    recipes = v2.expanded_recipes(seed)
    by_id = {_recipe_id(recipe): recipe for recipe in recipes}
    removal_owners = _all_removal_owners(seed, recipes)
    removals = set(removal_owners)
    preserved = {str(value) for value in seed.get("preserve_recipe_ids", [])}
    excluded_outputs = {str(value) for value in seed.get("exclude_outputs", [])}

    quantum_recipe = by_id.get(QUANTUM_CRAFTER_ID)
    quantum_approved = bool(
        quantum_recipe and _quantum_grid_is_physically_diverse(quantum_recipe)
    )
    quantum_grid = _grid_tokens(quantum_recipe) if quantum_recipe else None
    quantum_full = bool(
        quantum_grid
        and len(quantum_grid) == 5
        and all(len(row) == 5 and all(row) for row in quantum_grid)
    )
    v2_errors, v2_warnings, v2_notes = _run_v2_regression(
        seed, catalog, quantum_approved and quantum_full
    )
    counts["v2_regression_groups"] = 1
    counts["v2_errors"] = len(v2_errors)
    counts["v2_warnings"] = len(v2_warnings)
    errors.extend(f"v2 regression: {error}" for error in v2_errors)
    warnings.extend(f"v2 regression: {warning}" for warning in v2_warnings)
    notes.extend(f"v2: {note}" for note in v2_notes)

    # No direct Factory block has a managed producer.  Every exact stock route
    # is retired and every Factory output remains excluded from auto ownership.
    managed_outputs = {
        output for recipe in recipes for output in v2.recipe_outputs(recipe)
    }
    direct_factories = sorted(FACTORY_OUTPUTS & managed_outputs)
    if direct_factories:
        errors.append("direct Mekanism Factory outputs are managed: " + ", ".join(direct_factories))
    missing_factory_removals = sorted(FACTORY_STOCK_IDS - removals)
    if missing_factory_removals:
        errors.append("stock Mekanism Factory recipes not retired: " + ", ".join(missing_factory_removals))
    factory_preservation_conflicts = sorted(FACTORY_STOCK_IDS & preserved)
    if factory_preservation_conflicts:
        errors.append("Factory stock recipes are also preserved: " + ", ".join(factory_preservation_conflicts))
    missing_factory_exclusions = sorted(FACTORY_OUTPUTS - excluded_outputs)
    if missing_factory_exclusions:
        errors.append("Factory outputs absent from exclude_outputs: " + ", ".join(missing_factory_exclusions))
    catalog_factories = _catalog_factory_ids(catalog)
    if catalog_factories and catalog_factories != set(FACTORY_STOCK_IDS):
        errors.append(
            "catalog Factory contract changed; missing="
            f"{sorted(FACTORY_STOCK_IDS - catalog_factories)}, extra="
            f"{sorted(catalog_factories - FACTORY_STOCK_IDS)}"
        )
    counts["factory_stock_routes_checked"] = len(FACTORY_STOCK_IDS)
    counts["factory_outputs_checked"] = len(FACTORY_OUTPUTS)

    # The claimed process machines are machines even when their BOM contains
    # electronics: they must run as Industrial Iron assembly lines.
    for recipe_id in sorted(MEKANISM_PROCESS_MACHINE_IDS):
        recipe = by_id.get(recipe_id)
        if recipe is None:
            errors.append(f"missing v3 Mekanism process machine: {recipe_id}")
            continue
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id}: process machine must be sequenced_assembly, not {recipe.get('type')!r}")
            continue
        deploying = [
            step
            for step in recipe.get("steps", [])
            if isinstance(step, Mapping) and step.get("op") == "deploying"
        ]
        pressing = [
            step
            for step in recipe.get("steps", [])
            if isinstance(step, Mapping) and step.get("op") == "pressing"
        ]
        wrong_deployers = sorted(
            {str(step.get("machine")) for step in deploying if step.get("machine") != INDUSTRIAL_DEPLOYER}
        )
        wrong_presses = sorted(
            {str(step.get("machine")) for step in pressing if step.get("machine") != INDUSTRIAL_PRESS}
        )
        if not deploying or wrong_deployers:
            errors.append(f"{recipe_id}: deployments are not exclusively Industrial Iron: {wrong_deployers}")
        if not pressing or wrong_presses:
            errors.append(f"{recipe_id}: pressing is not exclusively Industrial Iron: {wrong_presses}")
        steps = recipe.get("steps", [])
        if not steps or not isinstance(steps[-1], Mapping) or steps[-1].get("op") != "pressing" or steps[-1].get("machine") != INDUSTRIAL_PRESS:
            errors.append(f"{recipe_id}: Industrial Iron press must close the sequence")
    counts["mekanism_process_machines_checked"] = len(MEKANISM_PROCESS_MACHINE_IDS)

    # Factory service cards and the late transmitter ladder may never regress
    # from Industrial Iron back to the earlier Weathered line.
    for recipe_id in (*MEKANISM_INSTALLER_IDS, *sorted(LATE_TRANSMISSION_IDS)):
        recipe = by_id.get(recipe_id)
        if recipe is None:
            retirement = REVIEW_RETIRED_LATE_TRANSMISSION.get(recipe_id)
            if retirement is not None:
                stock_id, output_id = retirement
                if stock_id in removals and output_id in excluded_outputs:
                    continue
            errors.append(f"missing monotonic Mekanism tier recipe: {recipe_id}")
            continue
        machines = {
            str(step.get("machine"))
            for step in recipe.get("steps", [])
            if isinstance(step, Mapping) and step.get("machine")
        }
        if recipe.get("machine"):
            machines.add(str(recipe["machine"]))
        if not machines or not machines.issubset({INDUSTRIAL_DEPLOYER, INDUSTRIAL_PRESS}):
            errors.append(f"{recipe_id}: late Mekanism tier regressed from Industrial Iron: {sorted(machines)}")
    counts["mekanism_monotonic_tier_recipes_checked"] = len(MEKANISM_INSTALLER_IDS) + len(LATE_TRANSMISSION_IDS)

    # Bootstrap selectors hidden behind process modes are explicit policy
    # contracts: silicon/refractory hardware must precede Railway, the Steel
    # Vat must precede its semiconductor recipes, and nuclear fabrication must
    # advance Industrial -> Refined Radiance without stepping backward.
    selector_contracts = {
        "industrial_colonies:steelworks/fireproof_bricks": "create:mechanical_press",
        "industrial_colonies:steelworks/fireproof_brick_reinforcement": "create:mechanical_press",
        "industrial_colonies:steelworks/blast_furnace_reinforcement": "create:mechanical_press",
        "industrial_colonies:nuclear/chromatic_compound": "createcasing:industrial_iron_mixer",
        "industrial_colonies:nuclear/refined_radiance": INDUSTRIAL_PRESS,
        "industrial_colonies:bigreactors/reprocessor/casing": "createcasing:refined_radiance_press",
        "industrial_colonies:mekanism/induction/casing": INDUSTRIAL_PRESS,
    }
    for recipe_id, expected_machine in selector_contracts.items():
        recipe = by_id.get(recipe_id)
        if recipe is None:
            errors.append(f"missing manufacturing-selector contract: {recipe_id}")
        elif recipe.get("machine") != expected_machine:
            errors.append(f"{recipe_id}: expected {expected_machine}, found {recipe.get('machine')}")
    for recipe_id in (
        "industrial_colonies:steelworks/blast_stove",
        "industrial_colonies:steelworks/blast_furnace_hatch",
    ):
        recipe = by_id.get(recipe_id)
        if recipe is None or recipe.get("phase") != "Steel & Petroleum":
            errors.append(f"{recipe_id}: silicon-furnace bootstrap is not in Steel & Petroleum")
    steel_vat = by_id.get("industrial_colonies:fluid_infrastructure/steel_chemical_vat")
    if steel_vat is None:
        errors.append("Steel Chemical Vat recipe is missing")
    else:
        vat_machines = {
            str(step.get("machine"))
            for step in steel_vat.get("steps", [])
            if isinstance(step, Mapping) and step.get("machine")
        }
        if steel_vat.get("type") != "sequenced_assembly" or vat_machines != {
            "createcasing:copper_deployer",
            "createcasing:copper_press",
        }:
            errors.append("Steel Chemical Vat is not a Copper-line sequenced assembly")
        for semiconductor_id in (
            "industrial_colonies:electronics/n_semiconductor",
            "industrial_colonies:electronics/p_semiconductor",
        ):
            semiconductor = by_id.get(semiconductor_id)
            if semiconductor is None:
                errors.append(f"missing semiconductor vat recipe: {semiconductor_id}")
            elif semiconductor.get("phase") == steel_vat.get("phase") and int(semiconductor.get("order", 0)) <= int(steel_vat.get("order", 0)):
                errors.append(f"{semiconductor_id}: semiconductor is ordered before its Steel Chemical Vat")
    counts["hidden_machine_selector_contracts_checked"] = len(selector_contracts) + 5

    # Complete storage cells are populated electronic products.  Housings and
    # cell components may be compacted, but the completed AE family may not.
    storage_cells_checked = 0
    for recipe in recipes:
        if recipe.get("type") not in {"compacting", "create_compacting"}:
            continue
        for output in v2.recipe_outputs(recipe):
            if _is_finished_storage_cell(output):
                storage_cells_checked += 1
                errors.append(
                    f"{_recipe_id(recipe)}: completed storage cell {output} may not be compacting"
                )
    counts["compacted_finished_storage_cells"] = storage_cells_checked

    # Spatial Anchor is downstream of the controller and 128^3 spatial core;
    # the controller must never consume an Anchor and form a cycle.
    anchor_producers = _managed_producers(recipes, SPATIAL_ANCHOR)
    if len(anchor_producers) != 1:
        errors.append(f"Spatial Anchor needs exactly one managed producer, found {len(anchor_producers)}")
    else:
        anchor = anchor_producers[0]
        ingredients = set(v2.recipe_material_inputs(anchor))
        pattern = anchor.get("pattern", [])
        if (
            anchor.get("type") != "mechanical_crafting"
            or not isinstance(pattern, list)
            or len(pattern) != 5
            or any(not isinstance(row, str) or len(row) != 5 for row in pattern)
        ):
            errors.append(f"{_recipe_id(anchor)}: Spatial Anchor must retain its reviewed physical 5x5 field-device BOM")
        if len(set(anchor.get("key", {}).values())) < 9:
            errors.append(f"{_recipe_id(anchor)}: Spatial Anchor lacks a varied field-device BOM")
        for required in (CHUNK_CONTROLLER, SPATIAL_CORE, "ae2:spatial_pylon", "ae2:spatial_io_port"):
            if required not in ingredients:
                errors.append(f"{_recipe_id(anchor)}: Spatial Anchor is missing {required}")
    controller_producers = _managed_producers(recipes, CHUNK_CONTROLLER)
    if len(controller_producers) != 1:
        errors.append(f"Chunk Controller needs exactly one managed producer, found {len(controller_producers)}")
    else:
        controller_inputs = set(v2.recipe_material_inputs(controller_producers[0]))
        if SPATIAL_ANCHOR in controller_inputs:
            errors.append(f"{_recipe_id(controller_producers[0])}: Chunk Controller consumes Spatial Anchor")
    counts["spatial_boundary_recipes_checked"] = len(anchor_producers) + len(controller_producers)

    cylinder_producers = _managed_producers(recipes, ENGINE_CYLINDER)
    if len(cylinder_producers) != 1:
        errors.append(f"Engine Cylinder needs exactly one managed producer, found {len(cylinder_producers)}")
    else:
        cylinder = cylinder_producers[0]
        if cylinder.get("type") not in {"compacting", "create_compacting"}:
            errors.append(f"{_recipe_id(cylinder)}: Engine Cylinder must be compacting")
        if cylinder.get("machine") != INDUSTRIAL_PRESS:
            errors.append(f"{_recipe_id(cylinder)}: Engine Cylinder must use {INDUSTRIAL_PRESS}")
    counts["engine_cylinder_recipes_checked"] = len(cylinder_producers)

    cube_producers = _managed_producers(recipes, ULTIMATE_ENERGY_CUBE)
    if len(cube_producers) != 1:
        errors.append(f"Ultimate Energy Cube needs exactly one managed producer, found {len(cube_producers)}")
    else:
        count = _output_count(cube_producers[0].get("output"), ULTIMATE_ENERGY_CUBE)
        if count != 2:
            errors.append(f"{_recipe_id(cube_producers[0])}: Ultimate Energy Cube output count is {count}, expected 2")
    counts["ultimate_energy_cube_recipes_checked"] = len(cube_producers)

    # Fully occupied 5x5 grids need explicit approval.  Sparse 5x5 silhouettes
    # remain legal, while Quantum Crafter is additionally conditional: it must
    # stay a recognizably populated machine with a detailed comment.
    five_by_five: list[str] = []
    full_five_by_five: list[str] = []
    for recipe in recipes:
        grid = _grid_tokens(recipe)
        if grid is None or len(grid) != 5 or any(len(row) != 5 for row in grid):
            continue
        recipe_id = _recipe_id(recipe)
        five_by_five.append(recipe_id)
        if recipe_id == QUANTUM_CRAFTER_ID:
            if not _quantum_grid_is_physically_diverse(recipe):
                errors.append(f"{recipe_id}: Quantum Crafter 5x5 is not physically diverse")
            continue
        is_full = all(all(row) for row in grid)
        if is_full:
            full_five_by_five.append(recipe_id)
        if is_full and recipe_id not in APPROVED_FIVE_BY_FIVE:
            errors.append(f"{recipe_id}: unapproved 5x5 grid")
    counts["five_by_five_grids_checked"] = len(five_by_five)
    counts["fully_filled_five_by_five_grids_checked"] = len(full_five_by_five)

    low_diversity_borders = 0
    for recipe in recipes:
        if not _is_low_diversity_border(recipe):
            continue
        low_diversity_borders += 1
        recipe_id = _recipe_id(recipe)
        if recipe_id in RING_GRID_ALLOWLIST:
            if len(str(recipe.get("comment", "")).strip()) < 40:
                errors.append(f"{recipe_id}: reviewed ring exception lacks an explanatory comment")
            continue
        errors.append(f"{recipe_id}: low-diversity material-border/ring grid is not approved")
    counts["low_diversity_borders_checked"] = low_diversity_borders

    # Whole processors may not leak back through the Inscriber.  Printed
    # wafers and reusable presses are intentionally not part of this set.
    whole_processor_routes = _whole_processor_inscriber_ids(catalog)
    for stock_id in sorted(whole_processor_routes):
        if stock_id not in removals:
            errors.append(f"whole-processor Inscriber route remains enabled: {stock_id}")
        if stock_id in preserved:
            errors.append(f"whole-processor Inscriber route is preserved: {stock_id}")
    counts["whole_processor_inscriber_routes_checked"] = len(whole_processor_routes)

    compacting_recipes = 0
    compacting_outputs = 0
    for recipe in recipes:
        if recipe.get("type") not in {"compacting", "create_compacting"}:
            continue
        compacting_recipes += 1
        for output in v2.recipe_outputs(recipe):
            compacting_outputs += 1
            if _is_finished_storage_cell(output):
                continue  # already reported by the stronger storage-cell rule
            if output in REVIEWED_COMPACTING_MACHINE_EXCEPTIONS:
                if len(str(recipe.get("comment", "")).strip()) < 40:
                    errors.append(f"{_recipe_id(recipe)}: compacting exception {output} lacks an explanatory comment")
                continue
            if _is_allowed_compacted_part(output):
                continue
            if _looks_like_finished_machine(output):
                errors.append(f"{_recipe_id(recipe)}: complex finished machine {output} may not be compacting")
            else:
                # Unknown compacting products fail closed.  Adding a new bulk
                # part is easy, but it must receive an explicit classifier or
                # exact reviewed exception instead of silently hiding a machine.
                errors.append(f"{_recipe_id(recipe)}: unclassified compacting output requires review: {output}")
    counts["compacting_recipes_checked"] = compacting_recipes
    counts["compacting_outputs_checked"] = compacting_outputs

    # Make the v2 ownership/graph coverage visible in the summary instead of
    # relying only on its individual diagnostic strings.
    counts["managed_recipes_checked"] = len(recipes)
    counts["removal_ids_checked"] = len(removal_owners)
    counts["duplicate_removal_owner_groups"] = sum(
        1 for owners in removal_owners.values() if len(owners) > 1
    )
    output_owners: defaultdict[str, list[str]] = defaultdict(list)
    for recipe in recipes:
        for output in v2.recipe_outputs(recipe):
            output_owners[output].append(_recipe_id(recipe))
    counts["managed_outputs_checked"] = len(output_owners)
    counts["duplicate_output_groups"] = sum(
        1 for owners in output_owners.values() if len(owners) > 1
    )

    notes.append(
        "v3 policy scope: "
        f"recipes={len(recipes)}, outputs={len(output_owners)}, "
        f"removals={len(removal_owners)}, compacting={compacting_recipes}, "
        f"5x5={len(five_by_five)}"
    )
    notes.append(
        "v3 focused contracts: "
        f"factories={len(FACTORY_STOCK_IDS)}, process_machines={len(MEKANISM_PROCESS_MACHINE_IDS)}, "
        f"whole_processor_inscriber_routes={len(whole_processor_routes)}, "
        f"quantum_crafter_approved={quantum_approved}"
    )
    return errors, warnings, notes, dict(counts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--apply-module",
        action="append",
        default=[],
        help="Import a tools module and call apply(seed) in memory before auditing",
    )
    args = parser.parse_args()

    seed_path = args.seed.resolve()
    catalog_path = args.catalog.resolve()
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    for module_name in args.apply_module:
        module = importlib.import_module(module_name)
        apply = getattr(module, "apply", None)
        if not callable(apply):
            raise TypeError(f"{module_name} has no callable apply(data)")
        apply(seed)

    errors, warnings, notes, counts = audit(seed, catalog_path)
    print(f"NOTE: files_checked=1 seed={seed_path}")
    print(f"NOTE: catalog={'present' if catalog_path.is_file() else 'absent'} path={catalog_path}")
    for note in notes:
        print(f"NOTE: {note}")
    print(
        "NOTE: check_counts="
        + ", ".join(f"{name}={value}" for name, value in sorted(counts.items()))
    )
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"FAIL: recipe-design-v3 policy audit; files=1, "
            f"recipes={counts.get('managed_recipes_checked', 0)}, "
            f"errors={len(errors)}, warnings={len(warnings)}",
            file=sys.stderr,
        )
        return 1
    print(
        f"PASS: recipe-design-v3 policy audit; files=1, "
        f"recipes={counts.get('managed_recipes_checked', 0)}, "
        f"warnings={len(warnings)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
