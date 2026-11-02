#!/usr/bin/env python3
"""Build the implemented AE2 high-energy, spatial, and MEGA-core redesign batch.

The builder reads the pinned recipe catalog, installed JARs, current generated
manifest, authoritative seed, assignments, and reviewed predecessor batch. It
only writes the three batch-owned review artifacts. After the reviewed patch
has been integrated, it deterministically rebuilds the evidence and historical
applied-patch record; it never edits shared progression JSON, generated
recipes, quests, deployment files, the live pack, or immutable Draw.io source.
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
DEFAULT_PLAN = PROJECT / "AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.plan.json"
DEFAULT_PATCH = PROJECT / "AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.patch.json"
DEFAULT_MARKDOWN = PROJECT / "AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.md"
SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
CURRENT_MANAGED = PROJECT / "build-current-audit/managed.json"
AUTOMATIC_AUDIT = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
DIGITAL_PREDECESSOR = PROJECT / "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json"
REBASED_BASE_FILES = {
    "progression/managed_recipe_overhaul.seed.json":
        "FEAFDF1383C840D750AA93D45F17A28DBEEA8E6B8FFDE0C9995177FA0873BAB3",
    "progression/machine_node_assignments.json":
        "329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E",
}
AE2_IMPLEMENTATION_SEED_SHA256 = (
    "0C02CC3AF93E25F0A820D018A152C52385CBA4868958F65D91AC2409BBCD942C"
)

BATCH_ID = "ae2_high_energy_spatial_and_mega_core"
BATCH_OUTPUTS = (
    "ae2:cell_workbench",
    "ae2:controller",
    "ae2:export_bus",
    "ae2:io_port",
    "ae2:me_p2p_tunnel",
    "ae2:spatial_anchor",
    "ae2:spatial_io_port",
    "ae2:spatial_pylon",
    "megacells:mega_crafting_unit",
)

SOURCE_REMOVALS: dict[str, tuple[str, ...]] = {
    "ae2:cell_workbench": ("ae2:network/blocks/cell_workbench",),
    "ae2:controller": ("ae2:network/blocks/controller",),
    "ae2:export_bus": ("ae2:network/parts/export_bus",),
    "ae2:io_port": ("ae2:network/blocks/io_port",),
    "ae2:me_p2p_tunnel": ("ae2:network/parts/tunnels_me",),
    "ae2:spatial_anchor": ("ae2:network/blocks/spatial_anchor",),
    "ae2:spatial_io_port": ("ae2:network/blocks/spatial_io_port",),
    "ae2:spatial_pylon": ("ae2:network/blocks/spatial_io_pylon",),
    "megacells:mega_crafting_unit": ("megacells:crafting/mega_crafting_unit",),
}

PRESERVE_RECIPE_IDS = (
    "ae2:network/cables/glass_fluix",
    "ae2:network/cables/glass_fluix_clean",
    "ae2:network/cables/smart_fluix",
    "ae2:network/cables/smart_fluix_clean",
    "megacells:crafting/1m_crafting_storage",
    "megacells:crafting/4m_crafting_storage",
    "megacells:crafting/16m_crafting_storage",
    "megacells:crafting/64m_crafting_storage",
    "megacells:crafting/256m_crafting_storage",
    "megacells:crafting/mega_crafting_accelerator",
    "megacells:crafting/mega_crafting_monitor",
)

AUTO_OWNERS = {
    output: f"industrial_colonies:auto/{output.replace(':', '/', 1)}"
    for output in BATCH_OUTPUTS
}

ASSIGNMENT_BY_OUTPUT = {
    "ae2:cell_workbench": "CR01 — Enhanced ME System Upgrade",
    "ae2:controller": "CR01 — ME System Advanced",
    "ae2:export_bus": "CR01 — Advanced ME BUS Technology",
    "ae2:io_port": "CR01 — Enhanced ME System Upgrade",
    "ae2:me_p2p_tunnel": "CR01 — P2P Tunneling Technology",
    "ae2:spatial_anchor": "CR01 — World Loading Technology",
    "ae2:spatial_io_port": "CR01 — Spacial Storage Tech",
    "ae2:spatial_pylon": "CR01 — Spacial Storage Tech",
    "megacells:mega_crafting_unit": "CR01 — Enhanced ME Crafting Upgrade",
}

PHASE_BY_OUTPUT = {output: "High-Energy Grid" for output in BATCH_OUTPUTS}

PREREQUISITE_OWNER_IDS = OrderedDict(
    (
        ("ae2:terminal", "industrial_colonies:digital_core/terminal"),
        ("ae2:interface", "industrial_colonies:digital_core/interface"),
        ("ae2:energy_acceptor", "industrial_colonies:digital_core/energy_acceptor"),
        ("ae2:drive", "industrial_colonies:digital/storage_drive"),
        ("ae2:crafting_unit", "industrial_colonies:digital/crafting_unit"),
        ("ae2:calculation_processor", "industrial_colonies:ae2/calculation_processor"),
        ("ae2:engineering_processor", "industrial_colonies:ae2/engineering_processor"),
        ("megacells:accumulation_processor", "industrial_colonies:digital/accumulation_processor"),
        ("tfmg:transformer", "industrial_colonies:tfmg_heavy_electrical/transformer"),
    )
)

FORBIDDEN_GATE_INPUTS = {
    "mekanism:basic_control_circuit",
    "mekanism:advanced_control_circuit",
    "mekanism:elite_control_circuit",
    "mekanism:ultimate_control_circuit",
    "mekanism:alloy_infused",
    "mekanism:alloy_reinforced",
    "mekanism:alloy_atomic",
}

CONTROL_OUTPUTS = ("ae2:controller", "ae2:io_port", "ae2:me_p2p_tunnel")
SPATIAL_OUTPUTS = ("ae2:spatial_pylon", "ae2:spatial_io_port", "ae2:spatial_anchor")


def output_id_from_ref(value: str) -> str:
    parts = value.split("x ", 1)
    return parts[1] if len(parts) == 2 and parts[0].isdigit() else value


def compacting(
    identity: str,
    output: str,
    order: int,
    machine: str,
    inputs: list[str],
    comment: str,
    *,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": identity,
        "node": ASSIGNMENT_BY_OUTPUT[output_id_from_ref(output)],
        "phase": PHASE_BY_OUTPUT[output_id_from_ref(output)],
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": inputs,
        "output": output,
        "remove": list(SOURCE_REMOVALS[output_id_from_ref(output)]),
        "exclusive_output": True,
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
    normalized = output_id_from_ref(output)
    return {
        "id": identity,
        "node": ASSIGNMENT_BY_OUTPUT[normalized],
        "phase": PHASE_BY_OUTPUT[normalized],
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "loops": 1,
        "steps": steps,
        "output": output,
        "remove": list(SOURCE_REMOVALS[normalized]),
        "exclusive_output": True,
        "depends_on": depends_on or [],
    }


PROPOSALS: tuple[dict[str, Any], ...] = (
    compacting(
        "industrial_colonies:ae2_high_energy/cell_workbench",
        "ae2:cell_workbench",
        160,
        "createcasing:brass_press",
        [
            "ae2:terminal",
            "ae2:calculation_processor",
            "#c:chests/wooden",
            "#minecraft:wool",
            "tfmg:circuit_board",
            "tfmg:plastic_sheet",
            "create:precision_mechanism",
        ],
        "Press the existing ME terminal, configurable storage, padding, and TFMG control electronics into a dedicated cell-programming bench.",
        depends_on=["industrial_colonies:digital_core/terminal"],
    ),
    sequence(
        "industrial_colonies:ae2_high_energy/controller",
        "ae2:controller",
        170,
        "ae2:energy_acceptor",
        "brass",
        [
            "ae2:smooth_sky_stone_block",
            "ae2:engineering_processor",
            "tfmg:transformer",
            "ae2:fluix_crystal",
        ],
        "Upgrade the proven ME power-entry block with an engineering processor, TFMG transformer, fluix bus, and sky-stone enclosure.",
        depends_on=[
            "industrial_colonies:digital_core/energy_acceptor",
            "industrial_colonies:ae2/engineering_processor",
            "industrial_colonies:tfmg_heavy_electrical/transformer",
        ],
    ),
    sequence(
        "industrial_colonies:ae2_high_energy/export_bus",
        "ae2:export_bus",
        180,
        "minecraft:piston",
        "copper",
        ["tfmg:circuit_board", "ae2:formation_core", "tfmg:copper_wire"],
        "Instrument a piston with a TFMG board, formation core, and copper signal lead to form the outbound counterpart to the import bus.",
    ),
    sequence(
        "industrial_colonies:ae2_high_energy/io_port",
        "ae2:io_port",
        190,
        "ae2:drive",
        "brass",
        [
            "ae2:interface",
            "ae2:logic_processor",
            "tfmg:circuit_board",
            "ae2:fluix_glass_cable",
        ],
        "Convert an established ME drive into a controlled cell-transfer station with an interface, logic, TFMG control board, and fluix link.",
        depends_on=[
            "industrial_colonies:digital/storage_drive",
            "industrial_colonies:digital_core/interface",
        ],
    ),
    sequence(
        "industrial_colonies:ae2_high_energy/me_p2p_tunnel",
        "ae2:me_p2p_tunnel",
        200,
        "ae2:quartz_fiber",
        "brass",
        [
            "ae2:engineering_processor",
            "tfmg:circuit_board",
            "tfmg:copper_wire",
            "ae2:fluix_crystal",
        ],
        "Populate a quartz-fiber carrier with engineering control, TFMG electronics, copper telemetry, and a fluix endpoint.",
        depends_on=["industrial_colonies:ae2/engineering_processor"],
    ),
    compacting(
        "industrial_colonies:ae2_high_energy/spatial_pylon_batch",
        "4x ae2:spatial_pylon",
        210,
        "createcasing:industrial_iron_press",
        [
            "4x ae2:quartz_glass",
            "2x ae2:fluix_glass_cable",
            "ae2:me_p2p_tunnel",
            "tfmg:transformer",
            "tfmg:steel_casing",
            "ae2:calculation_processor",
        ],
        "Press a routed P2P endpoint, transformer, fluix conductors, and structural glass into four repeatable spatial-field frame segments.",
        depends_on=[
            "industrial_colonies:ae2_high_energy/controller",
            "industrial_colonies:ae2_high_energy/io_port",
            "industrial_colonies:ae2_high_energy/me_p2p_tunnel",
        ],
    ),
    sequence(
        "industrial_colonies:ae2_high_energy/spatial_io_port",
        "ae2:spatial_io_port",
        220,
        "ae2:io_port",
        "industrial_iron",
        [
            "ae2:controller",
            "ae2:me_p2p_tunnel",
            "ae2:engineering_processor",
            "tfmg:steel_casing",
            "ae2:spatial_cell_component_2",
        ],
        "Upgrade a proven IO port with channel control, P2P routing, an engineering processor, a TFMG steel frame, and the first spatial matrix.",
        depends_on=[
            "industrial_colonies:ae2_high_energy/controller",
            "industrial_colonies:ae2_high_energy/io_port",
            "industrial_colonies:ae2_high_energy/me_p2p_tunnel",
        ],
    ),
    compacting(
        "industrial_colonies:ae2_high_energy/spatial_anchor",
        "ae2:spatial_anchor",
        230,
        "createcasing:industrial_iron_press",
        [
            "ae2:spatial_io_port",
            "4x ae2:spatial_pylon",
            "ae2:spatial_cell_component_128",
            "tfmg:transformer",
            "ae2:engineering_processor",
            "tfmg:steel_casing",
        ],
        "Compress a complete spatial IO gateway, field segments, a 128-cubed matrix, and redundant TFMG power/control hardware into the world-loading anchor.",
        depends_on=[
            "industrial_colonies:ae2_high_energy/spatial_io_port",
            "industrial_colonies:ae2_high_energy/spatial_pylon_batch",
        ],
    ),
    sequence(
        "industrial_colonies:ae2_high_energy/mega_crafting_unit",
        "megacells:mega_crafting_unit",
        240,
        "ae2:crafting_unit",
        "industrial_iron",
        [
            "megacells:accumulation_processor",
            "ae2:engineering_processor",
            "ae2:fluix_smart_cable",
            "tfmg:transformer",
            "tfmg:circuit_board",
        ],
        "Scale the standard crafting unit with accumulation and engineering processors, smart fluix bandwidth, and a transformer-backed TFMG control plane.",
        depends_on=[
            "industrial_colonies:digital/crafting_unit",
            "industrial_colonies:digital/accumulation_processor",
            "industrial_colonies:tfmg_heavy_electrical/transformer",
        ],
    ),
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
        return output_id_from_ref(output)
    if isinstance(output, dict) and isinstance(output.get("id"), str):
        return output["id"]
    return ""


def split_refs(value: str) -> set[str]:
    return {part.strip() for part in value.split("|") if part.strip()}


def recipe_inputs(recipe: dict[str, Any]) -> list[str]:
    if recipe.get("type") == "compacting":
        return list(recipe.get("inputs", []))
    values = [recipe.get("input", "")]
    values.extend(
        step["ingredient"]
        for step in recipe.get("steps", [])
        if step.get("op") == "deploying" and isinstance(step.get("ingredient"), str)
    )
    return [value for value in values if value]


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


def find_assignment_nodes(assignments: dict[str, Any], output: str) -> list[str]:
    return sorted(
        name
        for name, value in assignments.get("nodes", {}).items()
        if isinstance(value, dict) and output in value.get("unlocks", [])
    )


def scan_non_recipe_occurrences(mods: Path) -> tuple[int, list[dict[str, str]]]:
    """Find target references in data JSON outside recipes and documentation.

    This distinguishes ordinary self-drop loot tables from external acquisition
    sources. Advancements, models, language, and tags are descriptive/indexing
    data and cannot grant the item, so they are intentionally excluded.
    """

    occurrences: list[dict[str, str]] = []
    jar_count = 0
    for jar in sorted(mods.glob("*.jar"), key=lambda path: path.name.lower()):
        try:
            with zipfile.ZipFile(jar) as archive:
                jar_count += 1
                for path in archive.namelist():
                    lower = path.lower()
                    if not lower.endswith(".json"):
                        continue
                    if any(
                        marker in lower
                        for marker in (
                            "/recipe/",
                            "/recipes/",
                            "/advancement/",
                            "/advancements/",
                            "/model/",
                            "/models/",
                            "/lang/",
                            "/tag/",
                            "/tags/",
                        )
                    ):
                        continue
                    try:
                        text = archive.read(path).decode("utf-8")
                    except (KeyError, UnicodeDecodeError):
                        continue
                    for target in BATCH_OUTPUTS:
                        if target not in text:
                            continue
                        namespace, item = target.split(":", 1)
                        self_drop_path = f"data/{namespace}/loot_table/blocks/{item}.json"
                        role = (
                            "self_drop_block_loot"
                            if path == self_drop_path
                            else "external_acquisition_candidate"
                        )
                        occurrences.append(
                            {
                                "source_jar": jar.name,
                                "source_path": path,
                                "target": target,
                                "role": role,
                            }
                        )
        except zipfile.BadZipFile:
            continue
    return jar_count, sorted(
        occurrences,
        key=lambda row: (row["target"], row["source_jar"], row["source_path"]),
    )


def find_owner(recipes: list[dict[str, Any]], output: str) -> dict[str, Any] | None:
    for recipe in recipes:
        if isinstance(recipe, dict) and output_id(recipe) == output:
            return recipe
    return None


def prerequisite_evidence(
    seed: dict[str, Any], predecessor: dict[str, Any]
) -> list[dict[str, Any]]:
    seed_recipes = [entry for entry in seed.get("recipes", []) if isinstance(entry, dict)]
    predecessor_recipes = [
        entry for entry in predecessor.get("replacement_contracts", []) if isinstance(entry, dict)
    ]
    result: list[dict[str, Any]] = []
    for output, expected_id in PREREQUISITE_OWNER_IDS.items():
        owner = find_owner(seed_recipes, output)
        source = "authoritative_seed"
        if owner is None:
            owner = find_owner(predecessor_recipes, output)
            source = "reviewed_digital_predecessor"
        result.append(
            {
                "output": output,
                "expected_managed_owner": expected_id,
                "observed_managed_owner": owner.get("id") if owner else None,
                "phase": owner.get("phase") if owner else None,
                "order": owner.get("order") if owner else None,
                "evidence_source": source if owner else "missing",
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
    predecessor = load_json(DIGITAL_PREDECESSOR)

    batch = next(
        entry
        for entry in auto_audit.get("implementation_batches", [])
        if entry.get("id") == BATCH_ID
    )
    jar_hashes: dict[str, str] = {}
    removed_ids = [identity for output in BATCH_OUTPUTS for identity in SOURCE_REMOVALS[output]]
    removed_evidence = [
        source_evidence(identity, rows_by_id, mods, jar_hashes) for identity in removed_ids
    ]
    preserved_evidence = [
        {
            **source_evidence(identity, rows_by_id, mods, jar_hashes),
            "preservation_role": (
                "bulk_cable_or_color_cleanup"
                if identity.startswith("ae2:network/cables/")
                else "mega_unit_closure"
            ),
        }
        for identity in PRESERVE_RECIPE_IDS
    ]

    producers_by_output = OrderedDict(
        (
            output,
            sorted(
                row["recipe_id"]
                for row in rows
                if output in split_refs(row["outputs"])
            ),
        )
        for output in BATCH_OUTPUTS
    )

    downstream_rows = sorted(
        (
            row
            for row in rows
            if split_refs(row["inputs"]).intersection(BATCH_OUTPUTS)
        ),
        key=lambda row: row["recipe_id"],
    )
    downstream_evidence: list[dict[str, Any]] = []
    for row in downstream_rows:
        identity = row["recipe_id"]
        if identity in removed_ids:
            role = "same_batch_replaced"
        elif identity in PRESERVE_RECIPE_IDS:
            role = "preserved_bulk_closure"
        else:
            role = "downstream_not_owned_by_batch"
        downstream_evidence.append(
            {**source_evidence(identity, rows_by_id, mods, jar_hashes), "role": role}
        )

    jar_count, non_recipe_occurrences = scan_non_recipe_occurrences(mods)
    for occurrence in non_recipe_occurrences:
        jar = mods / occurrence["source_jar"]
        jar_hashes.setdefault(jar.name, digest_path(jar))

    current_by_output = {
        output_id(recipe): recipe
        for recipe in current.get("recipes", [])
        if isinstance(recipe, dict) and output_id(recipe) in BATCH_OUTPUTS
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
            "required_phase": PHASE_BY_OUTPUT[output],
            "current_nodes": find_assignment_nodes(assignments, output),
            "patch_action": "none",
        }
        for output in BATCH_OUTPUTS
    ]

    predecessor_reverse_dependencies = [
        {
            "predecessor_output": output_id(recipe),
            "batch_inputs_consumed": sorted(
                {
                    output_id_from_ref(value)
                    for value in recipe_inputs(recipe)
                    if output_id_from_ref(value) in BATCH_OUTPUTS
                }
            ),
        }
        for recipe in predecessor.get("replacement_contracts", [])
        if isinstance(recipe, dict)
    ]

    proposal_copy = json.loads(json.dumps(PROPOSALS))
    plan: dict[str, Any] = {
        "schema_version": 1,
        "status": "implemented_in_seed",
        "batch_id": BATCH_ID,
        "priority": 5,
        "audited_on": "2026-08-31",
        "scope": {
            "catalog": str(catalog),
            "catalog_recipes_sha256": digest_path(catalog / "recipes.csv"),
            "mods_directory": str(mods),
            "installed_jar_sha256": OrderedDict(sorted(jar_hashes.items())),
            "installed_jars_scanned_for_non_recipe_acquisition": jar_count,
            "seed": str(SEED.relative_to(PROJECT)).replace("\\", "/"),
            "seed_sha256": AE2_IMPLEMENTATION_SEED_SHA256,
            "assignments": str(ASSIGNMENTS.relative_to(PROJECT)).replace("\\", "/"),
            "assignments_sha256": digest_path(ASSIGNMENTS),
            "current_managed_snapshot": str(CURRENT_MANAGED.relative_to(PROJECT)).replace("\\", "/"),
            "current_managed_sha256": digest_path(CURRENT_MANAGED),
            "digital_predecessor": str(DIGITAL_PREDECESSOR.relative_to(PROJECT)).replace("\\", "/"),
            "digital_predecessor_sha256": digest_path(DIGITAL_PREDECESSOR),
        },
        "decision": {
            "replace_exactly_9_outputs": list(BATCH_OUTPUTS),
            "manufacturing_philosophy": "TFMG-first Copper bus fabrication, Brass network control, and Industrial-Iron spatial/MEGA frames",
            "all_targets_remain_phase": "High-Energy Grid",
            "first_me_network_remains_phase": "Digital Logistics",
            "spatial_control_predecessors": list(CONTROL_OUTPUTS),
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
        "direct_producer_audit": producers_by_output,
        "removed_installed_recipes": removed_evidence,
        "preserved_bulk_recipes": preserved_evidence,
        "downstream_consumer_audit": downstream_evidence,
        "non_recipe_acquisition_audit": {
            "occurrences": non_recipe_occurrences,
            "external_acquisition_candidates": [
                entry
                for entry in non_recipe_occurrences
                if entry["role"] == "external_acquisition_candidate"
            ],
            "finding": "Only ordinary self-drop block loot tables reference target blocks; no external loot or structure acquisition path was found.",
        },
        "prerequisite_evidence": prerequisite_evidence(seed, predecessor),
        "replacement_contracts": proposal_copy,
        "assignment_contract": assignment_snapshot,
        "dependency_contract": {
            "control_outputs_before_spatial": list(CONTROL_OUTPUTS),
            "spatial_outputs": list(SPATIAL_OUTPUTS),
            "pylon_batch_size": 4,
            "spatial_io_physically_consumes": [
                "ae2:io_port",
                "ae2:controller",
                "ae2:me_p2p_tunnel",
            ],
            "spatial_anchor_physically_consumes": [
                "ae2:spatial_io_port",
                "ae2:spatial_pylon",
            ],
            "digital_predecessor_reverse_dependencies": predecessor_reverse_dependencies,
            "forbidden_gate_inputs": sorted(FORBIDDEN_GATE_INPUTS),
        },
        "current_managed_state": {
            "replaced_automatic_owners": current_auto,
            "expected_retired_ids_after_rebuild": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
        },
        "implementation": {
            "status": "source_owned",
            "authoritative_source": "progression/managed_recipe_overhaul.seed.json",
            "source_recipe_count": 9,
            "source_recipe_ids": [recipe["id"] for recipe in proposal_copy],
            "preserved_stock_recipe_count": len(PRESERVE_RECIPE_IDS),
            "exact_stock_recipe_removals": len(removed_ids),
            "automatic_owners_retired_on_rebuild": 9,
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

    preserve_ids = sorted(PRESERVE_RECIPE_IDS)
    patch: dict[str, Any] = {
        "schema_version": 1,
        "status": "applied_to_authoritative_seed",
        "batch_id": BATCH_ID,
        "base_files": REBASED_BASE_FILES,
        "preconditions": {
            "explicit_seed_owners_for_outputs": 0,
            "exact_outputs": list(BATCH_OUTPUTS),
            "exact_current_auto_owners": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
            "required_predecessor_managed_ids": list(PREREQUISITE_OWNER_IDS.values()),
        },
        "seed_operations": [
            {
                "op": "append_recipe_specs_after_output_ownership_assertion",
                "recipes": proposal_copy,
            },
            {"op": "union_preserve_recipe_ids", "recipe_ids": preserve_ids},
        ],
        "assignment_operations": [],
        "assignment_assertions": assignment_snapshot,
        "expected_rebuild_effects": {
            "retire_automatic_managed_ids": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
            "compile_exact_managed_ids": [recipe["id"] for recipe in proposal_copy],
            "remove_exact_installed_recipe_ids": removed_ids,
            "retain_exact_installed_recipe_ids": preserve_ids,
        },
        "deferred_actions": [
            "Rebuild the managed manifest and KJSGen output under the root integration owner.",
            "Run all manifest, reachability, JEI exact-machine, and runtime acceptance validators.",
        ],
    }
    return plan, patch, render_markdown(plan, patch)


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
        "# AE2 High-Energy, Spatial, and MEGA Core audit",
        "",
        "Status: **implemented in the authoritative seed**. The nine reviewed contracts and eleven stock-recipe preservation IDs are source-owned; assignments were intentionally unchanged. Generated recipes, quests, deployment/live files, and Draw.io were not edited by this batch.",
        "",
        "## Outcome",
        "",
        "All nine priority outputs receive recognizable manufacturing contracts instead of the generic A/B 5×5 ring. The export bus uses the Copper electronics line; network control and configuration hardware use Brass; spatial field hardware and the MEGA crafting core use Industrial-Iron heavy assembly. Every contract contains a real TFMG component.",
        "",
        "The first ME network remains in Digital Logistics. These upgrades stay in High-Energy Grid and consume earlier terminal/interface/energy-acceptor infrastructure rather than becoming prerequisites of it.",
        "",
        "## Exact replacement contracts",
        "",
        "| Order | Output / managed ID | Existing node and phase | Process | Physical inputs | Exact removal |",
        "|---:|---|---|---|---|---|",
    ]
    for recipe in sorted(plan["replacement_contracts"], key=lambda row: row["order"]):
        removals = "<br>".join(f"`{value}`" for value in recipe["remove"])
        lines.append(
            f"| {recipe['order']} | `{recipe['output']}`<br>`{recipe['id']}` | "
            f"{recipe['node']}<br>{recipe['phase']} | `{recipe['type']}`<br>{format_machine(recipe)} | "
            f"{format_inputs(recipe)} | {removals} |"
        )
    lines.extend(
        [
            "",
            "Sequences use one loop and finish in their casing-specific press. The four-output pylon compacting batch keeps a large spatial frame buildable at factory scale; it is not a one-off 5×5 craft per segment.",
            "",
            "## Dependency shape",
            "",
            "- The cell workbench consumes the earlier terminal; the controller upgrades the earlier energy acceptor; the IO port upgrades the earlier drive and interface.",
            "- Controller, IO port, and ME P2P tunnel are ordered before all spatial contracts. The spatial IO port physically consumes all three, and the pylon batch physically consumes the P2P endpoint.",
            "- The spatial anchor consumes a completed spatial IO port plus four pylons, so neither world loading nor the anchor can bypass the spatial control chain.",
            "- The MEGA crafting unit upgrades the stock-managed AE crafting unit and consumes the accumulation processor, engineering processor, smart cable, TFMG transformer, and TFMG circuit board.",
            "- No recipe in this batch consumes a Mekanism control circuit or alloy gate.",
            "",
            "## Installed producers and acquisition bypass audit",
            "",
            "Each target has exactly one installed data-recipe producer, and those nine exact IDs are the only removals proposed by this batch:",
            "",
            "| Output | Installed recipe | Type | JAR / path |",
            "|---|---|---|---|",
        ]
    )
    by_output = {
        source["catalog_outputs"][0]: source for source in plan["removed_installed_recipes"]
    }
    for output in BATCH_OUTPUTS:
        source = by_output[output]
        lines.append(
            f"| `{output}` | `{source['id']}` | `{source['recipe_type']}` | "
            f"`{source['source_jar']}`<br>`{source['source_path']}` |"
        )
    occurrences = plan["non_recipe_acquisition_audit"]["occurrences"]
    lines.extend(
        [
            "",
            f"All {plan['scope']['installed_jars_scanned_for_non_recipe_acquisition']} installed JARs were scanned for target references outside recipes and descriptive data. The {len(occurrences)} findings are ordinary target-block self-drop loot tables; no external loot-table or structure acquisition candidate was found.",
            "",
            "## Bulk recipes deliberately preserved",
            "",
            "Eleven stock recipes remain available because their difficult prerequisite already carries progression: four fluix cable/color-cleanup routes and seven shapeless MEGA crafting-unit closures. This avoids demanding a unique 5×5 craft for every cable or storage/monitor/accelerator closure.",
            "",
            "| Role | Exact recipe ID | Type |",
            "|---|---|---|",
        ]
    )
    for source in plan["preserved_bulk_recipes"]:
        lines.append(
            f"| `{source['preservation_role']}` | `{source['id']}` | `{source['recipe_type']}` |"
        )
    lines.extend(
        [
            "",
            "All other downstream recipes are audited but not frozen by this batch; they remain eligible for their own source-owned redesign instead of being silently blessed forever.",
            "",
            "## Assignment and phase contract",
            "",
            "Every target already appears exactly once in the intended node, and each node maps to High-Energy Grid. No assignment edit is proposed.",
            "",
            "| Output | Existing node | Phase | Patch action |",
            "|---|---|---|---|",
        ]
    )
    for entry in plan["assignment_contract"]:
        lines.append(
            f"| `{entry['output']}` | {entry['required_node']} | {entry['required_phase']} | `{entry['patch_action']}` |"
        )
    lines.extend(
        [
            "",
            "The existing `Spacial Storage Tech` spelling is preserved because this read-only batch has no assignment-renaming ownership.",
            "",
            "## Current automatic owners retired by integration",
            "",
            "Adding these nine explicit owners will suppress the current generic automatic IDs on rebuild:",
            "",
        ]
    )
    lines.extend(f"- `{identity}`" for identity in patch["preconditions"]["exact_current_auto_owners"])
    lines.extend(
        [
            "",
            "## Integration boundary",
            "",
            "`AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.patch.json` is the applied historical patch record. It locks the released Foundry base hashes, carries the nine exact recipe specs, unions the eleven intentional stock preserves, and records no assignment changes.",
            "",
            "## Validation",
            "",
            "```powershell",
            "python tools/build_ae2_high_energy_spatial_mega_audit.py --check",
            "python tools/validate_ae2_high_energy_spatial_mega_audit.py",
            "python tools/test_validate_ae2_high_energy_spatial_mega_audit.py",
            "```",
            "",
            "The validator locks installed source hashes, direct-producer coverage, non-recipe acquisition evidence, exact removals/preserves, TFMG-first machine routing, physical dependency order, same-batch acyclicity, predecessor availability, phase/assignment parity, current automatic-owner retirement intent, patch parity, and deterministic regeneration.",
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
        drift = [
            str(path)
            for path, text in expected.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != text
        ]
        if drift:
            print("AE2 high-energy/spatial/MEGA artifacts drifted:")
            for path in drift:
                print(f"- {path}")
            return 1
        print("AE2 high-energy/spatial/MEGA artifacts are deterministic and current.")
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
