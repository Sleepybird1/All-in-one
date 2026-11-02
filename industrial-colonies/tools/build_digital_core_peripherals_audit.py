#!/usr/bin/env python3
"""Build the implemented Digital Core and Peripherals replacement batch.

The builder inspects the pinned recipe catalog, installed mod JARs, current
automatic managed snapshot, authoritative seed, and assignment file.  It only
writes the three batch-owned review artifacts named below; it never edits the
seed, assignments, generated KJSGen output, quests, deployment files, live
instance, or immutable Draw.io source.  After integration it deterministically
rebuilds the batch-owned evidence and the historical applied-patch record.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from collections import OrderedDict
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_PLAN = PROJECT / "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json"
DEFAULT_PATCH = PROJECT / "DIGITAL_CORE_PERIPHERALS_AUDIT.patch.json"
DEFAULT_MARKDOWN = PROJECT / "DIGITAL_CORE_PERIPHERALS_AUDIT.md"
SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
CURRENT_MANAGED = PROJECT / "build-current-audit/managed.json"
AUTOMATIC_AUDIT = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
REBASED_BASE_FILES = {
    "progression/managed_recipe_overhaul.seed.json":
        "EAF091CDE06E97E531F6BBC69C4B688B1E0A3C159177EC5008183BBAC21AD56A",
    "progression/machine_node_assignments.json":
        "329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E",
}
DIGITAL_CORE_IMPLEMENTATION_SEED_SHA256 = (
    "297CE846E57E8764A32642B3A3846893533477D289556B1297A1A98DABB07106"
)


BATCH_OUTPUTS = (
    "ae2:energy_acceptor",
    "ae2:import_bus",
    "ae2:interface",
    "ae2:item_cell_housing",
    "ae2:molecular_assembler",
    "ae2:terminal",
    "appmek:chemical_cell_housing",
    "ae2:pattern_provider",
    "advancedperipherals:peripheral_casing",
    "advancedperipherals:block_reader",
    "advancedperipherals:colony_integrator",
    "advancedperipherals:energy_detector",
    "advancedperipherals:inventory_manager",
    "advancedperipherals:me_bridge",
)

SOURCE_REMOVALS: dict[str, tuple[str, ...]] = {
    "ae2:energy_acceptor": (
        "ae2:network/blocks/energy_energy_acceptor",
        "ae2:network/blocks/energy_energy_acceptor_alt",
    ),
    "ae2:import_bus": ("ae2:network/parts/import_bus",),
    "ae2:interface": (
        "ae2:network/blocks/interfaces_interface",
        "ae2:network/blocks/interfaces_interface_alt",
    ),
    "ae2:item_cell_housing": ("ae2:network/cells/item_cell_housing",),
    "ae2:molecular_assembler": ("ae2:network/crafting/molecular_assembler",),
    "ae2:terminal": ("ae2:network/parts/terminals",),
    "appmek:chemical_cell_housing": ("appmek:chemical_cell_housing",),
    "ae2:pattern_provider": (
        "ae2:network/blocks/pattern_providers_interface",
        "ae2:network/blocks/pattern_providers_interface_alt",
    ),
    "advancedperipherals:peripheral_casing": ("advancedperipherals:peripheral_casing",),
    "advancedperipherals:block_reader": ("advancedperipherals:block_reader",),
    "advancedperipherals:colony_integrator": ("advancedperipherals:colony_integrator",),
    "advancedperipherals:energy_detector": ("advancedperipherals:energy_detector",),
    "advancedperipherals:inventory_manager": ("advancedperipherals:inventory_manager",),
    "advancedperipherals:me_bridge": ("advancedperipherals:me_bridge",),
}

AUTO_OWNERS = {
    output: f"industrial_colonies:auto/{output.replace(':', '/', 1)}" for output in BATCH_OUTPUTS
}

ASSIGNMENT_BY_OUTPUT = {
    "ae2:energy_acceptor": "CR01 — ME System Basics",
    "ae2:terminal": "CR01 — ME System Basics",
    "ae2:item_cell_housing": "CR01 — ME System Basics",
    "ae2:import_bus": "CR01 — Early ME BUS Technology",
    "ae2:interface": "CR01 — Early ME BUS Technology",
    "ae2:molecular_assembler": "CR01 — Early Digital Crafting",
    "appmek:chemical_cell_housing": "CR01 — Early Digital Chemical Storage",
    "ae2:pattern_provider": "CR01 — Advanced Digital Crafting",
    "advancedperipherals:peripheral_casing": "CR01 — Advanced Perhipherals",
    "advancedperipherals:block_reader": "CR01 — Advanced Perhipherals",
    "advancedperipherals:colony_integrator": "CR01 — Advanced Perhipherals",
    "advancedperipherals:energy_detector": "CR01 — Advanced Perhipherals",
    "advancedperipherals:inventory_manager": "CR01 — Advanced Perhipherals",
    "advancedperipherals:me_bridge": "CR01 — Advanced Perhipherals",
}

PHASE_BY_OUTPUT = {
    output: (
        "Mekanized Industry"
        if output == "ae2:pattern_provider"
        else "High-Energy Grid"
        if output.startswith("advancedperipherals:")
        else "Digital Logistics"
    )
    for output in BATCH_OUTPUTS
}


def compacting(
    identity: str,
    output: str,
    order: int,
    machine: str,
    inputs: list[str],
    comment: str,
    *,
    depends_on: list[str] | None = None,
    exclusive: bool = True,
) -> dict[str, Any]:
    return {
        "id": identity,
        "node": ASSIGNMENT_BY_OUTPUT[output],
        "phase": PHASE_BY_OUTPUT[output],
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": inputs,
        "output": output,
        "remove": list(SOURCE_REMOVALS[output]),
        "exclusive_output": exclusive,
        "depends_on": depends_on or [],
    }


def sequence(
    identity: str,
    output: str,
    order: int,
    input_item: str,
    machine_family: str,
    ingredients: list[str],
    comment: str,
    *,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    deployer = f"createcasing:{machine_family}_deployer"
    press = f"createcasing:{machine_family}_press"
    steps = [
        {"op": "deploying", "ingredient": ingredient, "machine": deployer}
        for ingredient in ingredients
    ]
    steps.append({"op": "pressing", "machine": press})
    return {
        "id": identity,
        "node": ASSIGNMENT_BY_OUTPUT[output],
        "phase": PHASE_BY_OUTPUT[output],
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "loops": 1,
        "steps": steps,
        "output": output,
        "remove": list(SOURCE_REMOVALS[output]),
        "exclusive_output": True,
        "depends_on": depends_on or [],
    }


PROPOSALS: tuple[dict[str, Any], ...] = (
    compacting(
        "industrial_colonies:digital_core/energy_acceptor",
        "ae2:energy_acceptor",
        10,
        "createcasing:copper_press",
        [
            "ae2:quartz_glass",
            "ae2:quartz_glass",
            "tfmg:copper_wire",
            "tfmg:copper_wire",
            "tfmg:transformer",
            "tfmg:circuit_board",
            "ae2:fluix_crystal",
        ],
        "Press a TFMG transformer, copper conductors, and control board into an insulated AE power-entry module.",
    ),
    compacting(
        "industrial_colonies:digital_core/item_cell_housing",
        "ae2:item_cell_housing",
        20,
        "createcasing:copper_press",
        [
            "ae2:quartz_glass",
            "ae2:quartz_glass",
            "tfmg:plastic_sheet",
            "tfmg:plastic_sheet",
            "tfmg:copper_wire",
            "tfmg:circuit_board",
        ],
        "Laminate quartz glass, TFMG insulation, conductor, and a board into a reusable item-cell shell.",
        exclusive=False,
    ),
    sequence(
        "industrial_colonies:digital_core/terminal",
        "ae2:terminal",
        30,
        "ae2:semi_dark_monitor",
        "brass",
        [
            "tfmg:circuit_board",
            "ae2:logic_processor",
            "ae2:formation_core",
            "ae2:annihilation_core",
        ],
        "Populate an illuminated panel with TFMG control electronics and both AE matter-transfer cores.",
    ),
    sequence(
        "industrial_colonies:digital_core/import_bus",
        "ae2:import_bus",
        40,
        "minecraft:piston",
        "copper",
        ["tfmg:circuit_board", "ae2:annihilation_core", "tfmg:copper_wire"],
        "Instrument a piston with a TFMG board, annihilation core, and copper signal lead on the bus line.",
    ),
    sequence(
        "industrial_colonies:digital_core/interface",
        "ae2:interface",
        50,
        "ae2:quartz_glass",
        "brass",
        [
            "tfmg:circuit_board",
            "ae2:logic_processor",
            "ae2:annihilation_core",
            "ae2:formation_core",
        ],
        "Build the reusable ME interface around glass, TFMG control electronics, logic, and paired transfer cores.",
    ),
    compacting(
        "industrial_colonies:digital_core/molecular_assembler",
        "ae2:molecular_assembler",
        60,
        "createcasing:brass_press",
        [
            "minecraft:crafting_table",
            "ae2:quartz_glass",
            "ae2:quartz_glass",
            "ae2:annihilation_core",
            "ae2:formation_core",
            "create:precision_mechanism",
            "tfmg:circuit_board",
        ],
        "Enclose a precision crafting mechanism between paired AE cores and a TFMG-controlled quartz chamber.",
    ),
    compacting(
        "industrial_colonies:digital_core/chemical_cell_housing",
        "appmek:chemical_cell_housing",
        70,
        "createcasing:copper_press",
        [
            "ae2:quartz_glass",
            "ae2:quartz_glass",
            "tfmg:plastic_sheet",
            "tfmg:plastic_sheet",
            "#c:ingots/osmium",
            "#c:ingots/osmium",
            "tfmg:copper_wire",
            "tfmg:circuit_board",
        ],
        "Press an osmium chemical liner, TFMG insulation, conductor, and board into a reusable chemical-cell shell.",
        exclusive=False,
    ),
    sequence(
        "industrial_colonies:digital_core/pattern_provider",
        "ae2:pattern_provider",
        10,
        "ae2:interface",
        "brass",
        [
            "minecraft:crafting_table",
            "ae2:calculation_processor",
            "tfmg:circuit_board",
            "create:precision_mechanism",
        ],
        "Upgrade the proven ME interface with calculation, pattern execution, and TFMG control hardware.",
        depends_on=["industrial_colonies:digital_core/interface"],
    ),
    sequence(
        "industrial_colonies:digital_core/peripheral_casing",
        "advancedperipherals:peripheral_casing",
        10,
        "tfmg:steel_casing",
        "brass",
        [
            "tfmg:circuit_board",
            "computercraft:wired_modem_full",
            "ae2:engineering_processor",
            "tfmg:plastic_sheet",
        ],
        "Turn a TFMG steel enclosure into the common modem, processor, and insulated carrier for every advanced peripheral.",
    ),
    compacting(
        "industrial_colonies:digital_core/block_reader",
        "advancedperipherals:block_reader",
        20,
        "createcasing:brass_press",
        [
            "advancedperipherals:peripheral_casing",
            "computercraft:wired_modem_full",
            "minecraft:observer",
            "create:content_observer",
            "tfmg:circuit_board",
            "ae2:calculation_processor",
        ],
        "Fit the common casing with paired observers, a wired modem, and calculation electronics for block telemetry.",
        depends_on=["industrial_colonies:digital_core/peripheral_casing"],
    ),
    compacting(
        "industrial_colonies:digital_core/energy_detector",
        "advancedperipherals:energy_detector",
        30,
        "createcasing:brass_press",
        [
            "advancedperipherals:peripheral_casing",
            "tfmg:voltage_observer",
            "tfmg:copper_wire",
            "minecraft:comparator",
            "tfmg:circuit_board",
            "ae2:calculation_processor",
        ],
        "Combine TFMG voltage sensing and copper telemetry with calculation electronics in the common casing.",
        depends_on=["industrial_colonies:digital_core/peripheral_casing"],
    ),
    compacting(
        "industrial_colonies:digital_core/inventory_manager",
        "advancedperipherals:inventory_manager",
        40,
        "createcasing:brass_press",
        [
            "advancedperipherals:peripheral_casing",
            "computercraft:wired_modem_full",
            "minecraft:hopper",
            "#c:chests",
            "create:content_observer",
            "tfmg:circuit_board",
            "ae2:calculation_processor",
        ],
        "Combine physical inventory I/O, content sensing, a modem, and TFMG calculation control in the common casing.",
        depends_on=["industrial_colonies:digital_core/peripheral_casing"],
    ),
    compacting(
        "industrial_colonies:digital_core/colony_integrator",
        "advancedperipherals:colony_integrator",
        50,
        "createcasing:brass_press",
        [
            "advancedperipherals:peripheral_casing",
            "computercraft:wired_modem_full",
            "minecolonies:blockminecoloniesrack",
            "minecolonies:build_goggles",
            "structurize:sceptergold",
            "tfmg:circuit_board",
        ],
        "Bind MineColonies planning, rack, and builder tooling to the common TFMG-controlled peripheral platform.",
        depends_on=["industrial_colonies:digital_core/peripheral_casing"],
    ),
    compacting(
        "industrial_colonies:digital_core/me_bridge",
        "advancedperipherals:me_bridge",
        60,
        "createcasing:brass_press",
        [
            "advancedperipherals:peripheral_casing",
            "ae2:interface",
            "ae2:fluix_block",
            "ae2:fluix_block",
            "computercraft:wired_modem_full",
            "tfmg:circuit_board",
            "ae2:engineering_processor",
        ],
        "Bridge the proven ME interface into the common modem platform with fluix bandwidth and engineering control.",
        depends_on=[
            "industrial_colonies:digital_core/peripheral_casing",
            "industrial_colonies:digital_core/interface",
        ],
    ),
)

FIRST_ME_OUTPUTS = tuple(
    output for output in BATCH_OUTPUTS if PHASE_BY_OUTPUT[output] == "Digital Logistics"
)
PREREQUISITE_OUTPUTS = (
    "tfmg:circuit_board",
    "ae2:logic_processor",
    "ae2:calculation_processor",
    "ae2:engineering_processor",
    "computercraft:wired_modem_full",
)
FORBIDDEN_FIRST_ME_INPUTS = (
    "mekanism:basic_control_circuit",
    "mekanism:advanced_control_circuit",
    "mekanism:elite_control_circuit",
    "mekanism:ultimate_control_circuit",
    "mekanism:alloy_infused",
    "mekanism:alloy_reinforced",
    "mekanism:alloy_atomic",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def output_id(recipe: dict[str, Any]) -> str:
    output = recipe.get("output")
    if isinstance(output, str):
        parts = output.split("x ", 1)
        return parts[1] if len(parts) == 2 and parts[0].isdigit() else output
    if isinstance(output, dict) and isinstance(output.get("id"), str):
        return output["id"]
    return ""


def split_refs(value: str) -> set[str]:
    return {part.strip() for part in value.split("|") if part.strip()}


def source_evidence(
    recipe_id: str,
    rows_by_id: dict[str, dict[str, str]],
    mods: Path,
    jar_hashes: dict[str, str],
) -> dict[str, Any]:
    row = rows_by_id.get(recipe_id)
    if row is None:
        raise ValueError(f"catalog is missing installed recipe {recipe_id}")
    jar = mods / row["source_jar"]
    if not jar.is_file():
        raise ValueError(f"installed source JAR is missing: {jar}")
    jar_hashes.setdefault(jar.name, digest_path(jar))
    with zipfile.ZipFile(jar) as archive:
        raw = archive.read(row["source_path"])
    document = json.loads(raw)
    return {
        "id": recipe_id,
        "recipe_type": row["recipe_type"],
        "source_jar": row["source_jar"],
        "source_path": row["source_path"],
        "source_sha256": digest_bytes(raw),
        "catalog_outputs": sorted(split_refs(row["outputs"])),
        "catalog_inputs": sorted(split_refs(row["inputs"])),
        "raw_type": document.get("type"),
    }


def recipe_inputs(recipe: dict[str, Any]) -> list[str]:
    if recipe.get("type") == "compacting":
        return list(recipe["inputs"])
    values = [recipe["input"]]
    values.extend(
        step["ingredient"] for step in recipe["steps"] if step.get("op") == "deploying"
    )
    return values


def find_assignment_nodes(assignments: dict[str, Any], output: str) -> list[str]:
    nodes = assignments.get("nodes", {})
    return sorted(
        name
        for name, value in nodes.items()
        if isinstance(value, dict) and output in value.get("unlocks", [])
    )


def prerequisite_evidence(seed: dict[str, Any], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    seed_by_output = {output_id(recipe): recipe for recipe in seed.get("recipes", [])}
    result: list[dict[str, Any]] = []
    for output in PREREQUISITE_OUTPUTS:
        if output == "computercraft:wired_modem_full":
            row = next(row for row in rows if row["recipe_id"] == "computercraft:wired_modem_full_from")
            owner = seed_by_output.get("computercraft:wired_modem")
            result.append(
                {
                    "output": output,
                    "kind": "stock_closure_over_managed_component",
                    "recipe_id": row["recipe_id"],
                    "inputs": sorted(split_refs(row["inputs"])),
                    "managed_component_owner": owner.get("id") if owner else None,
                }
            )
        else:
            owner = seed_by_output.get(output)
            result.append(
                {
                    "output": output,
                    "kind": "authoritative_seed_owner",
                    "managed_owner": owner.get("id") if owner else None,
                    "phase": owner.get("phase") if owner else None,
                    "order": owner.get("order") if owner else None,
                }
            )
    return result


def build_documents(catalog: Path, mods: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    rows = load_rows(catalog / "recipes.csv")
    rows_by_id = {row["recipe_id"]: row for row in rows}
    seed = load_json(SEED)
    assignments = load_json(ASSIGNMENTS)
    current = load_json(CURRENT_MANAGED)
    auto_audit = load_json(AUTOMATIC_AUDIT)

    batch = next(
        entry
        for entry in auto_audit.get("implementation_batches", [])
        if entry.get("id") == "digital_core_and_peripherals"
    )
    jar_hashes: dict[str, str] = {}
    removed_ids = [identity for output in BATCH_OUTPUTS for identity in SOURCE_REMOVALS[output]]
    removed_evidence = [
        source_evidence(identity, rows_by_id, mods, jar_hashes) for identity in removed_ids
    ]

    housing_outputs = {"ae2:item_cell_housing", "appmek:chemical_cell_housing"}
    recovery_rows = sorted(
        (
            row
            for row in rows
            if row["recipe_type"] == "ae2:storage_cell_disassembly"
            and split_refs(row["outputs"]).intersection(housing_outputs)
        ),
        key=lambda row: row["recipe_id"],
    )
    closure_rows = sorted(
        (
            row
            for row in rows
            if split_refs(row["inputs"]).intersection(housing_outputs)
            and row["recipe_type"] != "ae2:storage_cell_disassembly"
        ),
        key=lambda row: row["recipe_id"],
    )
    preserved_evidence = [
        {
            **source_evidence(row["recipe_id"], rows_by_id, mods, jar_hashes),
            "preservation_role": "housing_recovery"
            if row["recipe_type"] == "ae2:storage_cell_disassembly"
            else "cell_closure",
        }
        for row in [*recovery_rows, *closure_rows]
    ]

    current_by_output = {
        output_id(recipe): recipe
        for recipe in current.get("recipes", [])
        if output_id(recipe) in BATCH_OUTPUTS
    }
    current_auto = [
        {
            "output": output,
            "id": current_by_output.get(output, {}).get("id"),
            "phase": current_by_output.get(output, {}).get("phase"),
            "type": current_by_output.get(output, {}).get("type"),
            "remove": current_by_output.get(output, {}).get("remove", []),
            "depends_on": current_by_output.get(output, {}).get("depends_on", []),
        }
        for output in BATCH_OUTPUTS
    ]

    assignment_snapshot = [
        {
            "output": output,
            "required_node": ASSIGNMENT_BY_OUTPUT[output],
            "current_nodes": find_assignment_nodes(assignments, output),
            "patch_action": "none",
        }
        for output in BATCH_OUTPUTS
    ]

    proposal_copy = json.loads(json.dumps(PROPOSALS))
    preserve_ids = [entry["id"] for entry in preserved_evidence]
    plan: dict[str, Any] = {
        "schema_version": 1,
        "status": "implemented_in_seed",
        "batch_id": "digital_core_and_peripherals",
        "priority": 2,
        "audited_on": "2026-08-31",
        "scope": {
            "catalog": str(catalog),
            "catalog_recipes_sha256": digest_path(catalog / "recipes.csv"),
            "mods_directory": str(mods),
            "installed_jar_sha256": OrderedDict(sorted(jar_hashes.items())),
            "seed": str(SEED.relative_to(PROJECT)).replace("\\", "/"),
            "seed_sha256": DIGITAL_CORE_IMPLEMENTATION_SEED_SHA256,
            "assignments": str(ASSIGNMENTS.relative_to(PROJECT)).replace("\\", "/"),
            "assignments_sha256": digest_path(ASSIGNMENTS),
            "current_managed_snapshot": str(CURRENT_MANAGED.relative_to(PROJECT)).replace("\\", "/"),
            "current_managed_sha256": digest_path(CURRENT_MANAGED),
        },
        "decision": {
            "replace_exactly_14_outputs": list(BATCH_OUTPUTS),
            "manufacturing_philosophy": "TFMG-first electronics assembled in Copper and Brass Create Encased environments",
            "forbid_generic_gate_rings": True,
            "shared_files_modified": True,
        },
        "automatic_audit_contract": {
            "outputs": batch.get("outputs"),
            "prerequisite_outputs": batch.get("prerequisite_outputs"),
            "recommended_environments": batch.get("recommended_environments"),
            "cycle_risks": batch.get("cycle_risks"),
            "managed_ids": batch.get("managed_ids"),
            "installed_recipe_ids": batch.get("installed_recipe_ids"),
        },
        "removed_installed_recipes": removed_evidence,
        "preserved_cell_recipes": preserved_evidence,
        "prerequisite_evidence": prerequisite_evidence(seed, rows),
        "replacement_contracts": proposal_copy,
        "assignment_contract": assignment_snapshot,
        "dependency_contract": {
            "first_me_outputs": list(FIRST_ME_OUTPUTS),
            "forbidden_first_me_inputs": list(FORBIDDEN_FIRST_ME_INPUTS),
            "peripheral_casing_precedes": [
                output
                for output in BATCH_OUTPUTS
                if output.startswith("advancedperipherals:")
                and output != "advancedperipherals:peripheral_casing"
            ],
            "interface_precedes": [
                "ae2:pattern_provider",
                "advancedperipherals:me_bridge",
            ],
            "housing_precedes_stock_closures": {
                "ae2:item_cell_housing": sorted(
                    row["recipe_id"]
                    for row in closure_rows
                    if "ae2:item_cell_housing" in split_refs(row["inputs"])
                ),
                "appmek:chemical_cell_housing": sorted(
                    row["recipe_id"]
                    for row in closure_rows
                    if "appmek:chemical_cell_housing" in split_refs(row["inputs"])
                ),
            },
        },
        "current_managed_state": {
            "replaced_automatic_owners": current_auto,
            "expected_retired_ids_after_rebuild": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
        },
        "implementation": {
            "status": "source_owned",
            "authoritative_source": "progression/managed_recipe_overhaul.seed.json",
            "source_recipe_count": 14,
            "source_recipe_ids": [recipe["id"] for recipe in proposal_copy],
            "preserved_stock_recipe_count": len(preserve_ids),
            "exact_stock_recipe_removals": len(removed_ids),
            "automatic_owners_retired_on_rebuild": 14,
            "assignment_changes": 0,
            "authoritative_generated_artifacts": "intentionally_not_regenerated_by_batch_owner",
            "rebased_base_files": REBASED_BASE_FILES,
        },
        "integration_boundary": {
            "seed_edit_applied": True,
            "assignment_edit_required": False,
            "generated_output_edit_authorized": False,
            "quest_edit_authorized": False,
            "deploy_or_live_edit_authorized": False,
            "drawio_edit_authorized": False,
        },
    }

    patch: dict[str, Any] = {
        "schema_version": 1,
        "status": "applied_to_authoritative_seed",
        "batch_id": plan["batch_id"],
        "base_files": REBASED_BASE_FILES,
        "preconditions": {
            "explicit_seed_owners_for_outputs": 0,
            "exact_outputs": list(BATCH_OUTPUTS),
            "exact_current_auto_owners": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
        },
        "seed_operations": [
            {
                "op": "append_recipe_specs_after_output_ownership_assertion",
                "recipes": proposal_copy,
            },
            {
                "op": "union_preserve_recipe_ids",
                "recipe_ids": sorted(preserve_ids),
            },
        ],
        "assignment_operations": [],
        "assignment_assertions": assignment_snapshot,
        "expected_rebuild_effects": {
            "retire_automatic_managed_ids": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
            "compile_exact_managed_ids": [recipe["id"] for recipe in proposal_copy],
            "retain_exact_installed_recipe_ids": sorted(preserve_ids),
            "remove_exact_installed_recipe_ids": removed_ids,
        },
        "deferred_actions": [
            "Regenerate authoritative managed/KJSGen artifacts only under the root integration owner.",
            "Deploy and run a fresh runtime acceptance pass only under explicit live-pack ownership.",
        ],
    }
    markdown = render_markdown(plan, patch)
    return plan, patch, markdown


def format_inputs(recipe: dict[str, Any]) -> str:
    return "<br>".join(f"`{value}`" for value in recipe_inputs(recipe))


def format_machine(recipe: dict[str, Any]) -> str:
    if recipe["type"] == "compacting":
        return f"`{recipe['machine']}`"
    machines: list[str] = []
    for step in recipe["steps"]:
        machine = step["machine"]
        if machine not in machines:
            machines.append(machine)
    return " → ".join(f"`{machine}`" for machine in machines)


def render_markdown(plan: dict[str, Any], patch: dict[str, Any]) -> str:
    lines = [
        "# Digital Core and Peripherals audit",
        "",
        "Status: **implemented in the authoritative seed**. The 14 reviewed contracts and 44 stock-cell preservation IDs are source-owned; assignments were intentionally unchanged. Authoritative generated recipes, quests, deployment/live files, and Draw.io were not edited by this batch.",
        "",
        "## Outcome",
        "",
        "All 14 priority-batch outputs have exact replacement contracts. The generic 5×5 A/B gate rings are replaced by recognizable component assembly: four Copper-line recipes for power, bus, and housings; ten Brass-line recipes for terminals, interfaces, crafting hardware, and peripherals. Every contract uses a real TFMG electronic or structural component, while the first usable ME network contains no Mekanism control circuit or alloy gate.",
        "",
        "## Exact replacement contracts",
        "",
        "| Order | Output / managed ID | Node and phase | Process | Physical inputs | Exact removals |",
        "|---:|---|---|---|---|---|",
    ]
    phase_rank = {"Digital Logistics": 0, "Mekanized Industry": 1, "High-Energy Grid": 2}
    for recipe in sorted(
        plan["replacement_contracts"], key=lambda row: (phase_rank[row["phase"]], row["order"])
    ):
        removals = "<br>".join(f"`{value}`" for value in recipe["remove"])
        lines.append(
            f"| {recipe['order']} | `{recipe['output']}`<br>`{recipe['id']}` | "
            f"{recipe['node']}<br>{recipe['phase']} | `{recipe['type']}`<br>{format_machine(recipe)} | "
            f"{format_inputs(recipe)} | {removals} |"
        )
    lines.extend(
        [
            "",
            "Every sequenced assembly uses one loop and four or five meaningful operations. No shaped or mechanical-crafting recipe in this batch uses a decorative generic gate ring.",
            "",
            "## Dependency order",
            "",
            "- `advancedperipherals:peripheral_casing` is manufactured first and is a physical input plus explicit dependency of all five downstream Advanced Peripherals devices.",
            "- `ae2:interface` is manufactured in Digital Logistics. It is a physical input of the later `ae2:pattern_provider` upgrade and `advancedperipherals:me_bridge`.",
            "- `ae2:item_cell_housing` and `appmek:chemical_cell_housing` are manufactured before the preserved stock closure recipes that combine them with cell components.",
            "- Digital Logistics uses `tfmg:circuit_board` and, where appropriate, `ae2:logic_processor`; it does not consume any Mekanism control circuit or infused/reinforced/atomic alloy.",
            "- `ae2:calculation_processor` enters only at Mekanized Industry or later. `ae2:engineering_processor` enters only in the High-Energy peripheral platform.",
            "",
            "## Assignment contract",
            "",
            "No assignment edit is proposed because every output already appears exactly once under its intended node.",
            "",
            "| Output | Required existing node | Patch action |",
            "|---|---|---|",
        ]
    )
    for entry in plan["assignment_contract"]:
        lines.append(
            f"| `{entry['output']}` | {entry['required_node']} | `{entry['patch_action']}` |"
        )
    lines.extend(
        [
            "",
            "The existing node spelling `CR01 — Advanced Perhipherals` is preserved because this batch has no ownership to rename shared progression data.",
            "",
            "## Installed source audit and removals",
            "",
            "The 17 IDs below are the only installed recipes removed by this patch. The three AE block/part conversion recipes are included because leaving them would bypass the new energy acceptor, interface, or pattern-provider manufacturing route.",
            "",
            "| Recipe ID | Type | Installed JAR / path | Catalog outputs |",
            "|---|---|---|---|",
        ]
    )
    for source in plan["removed_installed_recipes"]:
        outputs = ", ".join(f"`{value}`" for value in source["catalog_outputs"])
        lines.append(
            f"| `{source['id']}` | `{source['recipe_type']}` | `{source['source_jar']}`<br>`{source['source_path']}` | {outputs} |"
        )
    lines.extend(
        [
            "",
            "## Stock cell recipes explicitly preserved",
            "",
            "Housing recovery/disassembly and cell closure remain stock. This preserves AE2/AppMek's reversible cell behavior while ensuring the manufactured housing is the prerequisite shell.",
            "",
            "| Role | Exact recipe ID | Type |",
            "|---|---|---|",
        ]
    )
    for source in plan["preserved_cell_recipes"]:
        lines.append(
            f"| `{source['preservation_role']}` | `{source['id']}` | `{source['recipe_type']}` |"
        )
    lines.extend(
        [
            "",
            "## Automatic owners retired by integration",
            "",
            "The pre-integration generated snapshot contained one automatic 5×5 owner for every batch output. The reviewed explicit seed owners suppress these 14 automatic IDs in an isolated rebuild:",
            "",
        ]
    )
    lines.extend(f"- `{identity}`" for identity in patch["preconditions"]["exact_current_auto_owners"])
    lines.extend(
        [
            "",
            "## Integration boundary",
            "",
            "`DIGITAL_CORE_PERIPHERALS_AUDIT.patch.json` is the applied historical patch record. It is rebased to the released Heavy/Electrical source hashes, carries the unchanged 14 reviewed recipe specs and 44-ID preservation union, and records that no assignment edit was made. The audit validator checks the implemented seed against those immutable payloads.",
            "",
            "## Validation",
            "",
            "Run:",
            "",
            "```powershell",
            "python tools/build_digital_core_peripherals_audit.py --check",
            "python tools/validate_digital_core_peripherals_audit.py",
            "python tools/test_validate_digital_core_peripherals_audit.py",
            "```",
            "",
            "The validator checks installed JAR and recipe hashes, catalog identity, exact output/removal coverage, all 44 preserved closures and recoveries in the seed, prerequisite and TFMG transformer/voltage-observer ownership, Copper/Brass routing, phase gates, same-batch acyclicity, exact assignment parity, applied-patch parity, and deterministic regeneration. With `--managed` pointed at an isolated rebuild, it also proves all 14 automatic owners retired and all 17 removals compiled. Mutation tests prove each major invariant fails closed.",
            "",
        ]
    )
    return "\n".join(lines)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    plan, patch, markdown = build_documents(args.catalog, args.mods)
    expected = {
        args.plan: json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
        args.patch: json.dumps(patch, indent=2, ensure_ascii=False) + "\n",
        args.markdown: markdown,
    }
    if args.check:
        drift = [str(path) for path, text in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != text]
        if drift:
            print("Digital Core and Peripherals artifacts drifted:")
            for path in drift:
                print(f"- {path}")
            return 1
        print("Digital Core and Peripherals artifacts are deterministic and current.")
        return 0
    write_json(args.plan, plan)
    write_json(args.patch, patch)
    args.markdown.write_text(markdown, encoding="utf-8")
    print(f"Wrote {args.plan}")
    print(f"Wrote {args.patch}")
    print(f"Wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
