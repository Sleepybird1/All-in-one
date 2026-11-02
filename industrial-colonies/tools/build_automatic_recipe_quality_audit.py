#!/usr/bin/env python3
"""Build the read-only quality audit for the automatic recipe snapshot.

This script reads only build-current-audit/managed.json and report.json.  It
does not rebuild the manifest and never touches the seed, assignments, quests,
generated shared artifacts, deployment files, the live pack, or Draw.io.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
SNAPSHOT = PROJECT / "build-current-audit"
MANAGED = SNAPSHOT / "managed.json"
REPORT = SNAPSHOT / "report.json"
PLAN = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
MARKDOWN = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.md"

ACCEPTABLE = {
    "industrial_colonies:auto/create/andesite_funnel",
    "industrial_colonies:auto/create/belt_connector",
    "industrial_colonies:auto/create/cart_assembler",
    "industrial_colonies:auto/create/chute",
    "industrial_colonies:auto/create/depot",
    "industrial_colonies:auto/create/hose_pulley",
    "industrial_colonies:auto/create/item_drain",
    "industrial_colonies:auto/create/item_vault",
    "industrial_colonies:auto/create/packager",
    "industrial_colonies:auto/create/portable_fluid_interface",
    "industrial_colonies:auto/create/portable_storage_interface",
    "industrial_colonies:auto/create/spout",
    "industrial_colonies:auto/create/content_observer",
    "industrial_colonies:auto/create/controls",
    "industrial_colonies:auto/create/crushing_wheel",
    "industrial_colonies:auto/create/mechanical_arm",
    "industrial_colonies:auto/create/pulse_extender",
    "industrial_colonies:auto/create/pulse_repeater",
    "industrial_colonies:auto/create/rotation_speed_controller",
    "industrial_colonies:auto/create/schedule",
    "industrial_colonies:auto/create/steam_whistle",
    "industrial_colonies:auto/create/stockpile_switch",
    "industrial_colonies:auto/create/track_observer",
    "industrial_colonies:auto/create/track_signal",
    "industrial_colonies:auto/create/track_station",
    "industrial_colonies:auto/tfmg/cast_iron_frame",
    "industrial_colonies:auto/tfmg/copper_spool",
}

REDUNDANT = {
    "industrial_colonies:auto/createmetallurgy/casting_basin",
    "industrial_colonies:auto/createmetallurgy/casting_table",
    "industrial_colonies:auto/createmetallurgy/foundry_basin",
    "industrial_colonies:auto/createmetallurgy/foundry_lid",
    "industrial_colonies:auto/createmetallurgy/foundry_mixer",
    "industrial_colonies:auto/modernfoundry/scorched_basin",
    "industrial_colonies:auto/modernfoundry/scorched_drain",
    "industrial_colonies:auto/modernfoundry/scorched_table",
}

LEAVE_STOCK = {
    "industrial_colonies:auto/tfmg/cast_iron_truss",
    "industrial_colonies:auto/tfmg/coal_coke",
    "industrial_colonies:auto/electroenergetics/double_connector",
    "industrial_colonies:auto/electroenergetics/quad_connector",
    "industrial_colonies:auto/electroenergetics/triple_connector",
    "industrial_colonies:auto/ae2/1k_crafting_storage",
    "industrial_colonies:auto/ae2/fluix_glass_cable",
    "industrial_colonies:auto/ae2/item_storage_cell_1k",
    "industrial_colonies:auto/ae2/item_storage_cell_4k",
    "industrial_colonies:auto/ae2/storage_bus",
    "industrial_colonies:auto/appmek/chemical_storage_cell_1k",
    "industrial_colonies:auto/appmek/chemical_storage_cell_4k",
    "industrial_colonies:auto/ae2/16k_crafting_storage",
    "industrial_colonies:auto/ae2/4k_crafting_storage",
    "industrial_colonies:auto/appmek/chemical_storage_cell_16k",
    "industrial_colonies:auto/appmek/chemical_storage_cell_64k",
    "industrial_colonies:auto/mekanism/advanced_tier_installer",
    "industrial_colonies:auto/mekanism/basic_tier_installer",
    "industrial_colonies:auto/mekanism/hdpe_rod",
    "industrial_colonies:auto/mekanism/hdpe_stick",
    "industrial_colonies:auto/ae2/cable_interface",
    "industrial_colonies:auto/ae2/crafting_card",
    "industrial_colonies:auto/ae2/dense_energy_cell",
    "industrial_colonies:auto/ae2/fluid_storage_cell_256k",
    "industrial_colonies:auto/ae2/fluix_smart_cable",
    "industrial_colonies:auto/ae2/fluix_smart_dense_cable",
    "industrial_colonies:auto/ae2/item_storage_cell_16k",
    "industrial_colonies:auto/ae2/item_storage_cell_256k",
    "industrial_colonies:auto/ae2/item_storage_cell_64k",
    "industrial_colonies:auto/ae2/spatial_storage_cell_128",
    "industrial_colonies:auto/ae2/spatial_storage_cell_16",
    "industrial_colonies:auto/ae2/spatial_storage_cell_2",
    "industrial_colonies:auto/megacells/1m_crafting_storage",
    "industrial_colonies:auto/megacells/4m_crafting_storage",
    "industrial_colonies:auto/megacells/mega_crafting_accelerator",
    "industrial_colonies:auto/megacells/mega_pattern_provider",
    "industrial_colonies:auto/mekanism/elite_tier_installer",
    "industrial_colonies:auto/mekanism/hdpe_elytra",
    "industrial_colonies:auto/mekanism/ultimate_tier_installer",
    "industrial_colonies:auto/bigreactors/basic_reactorglass",
    "industrial_colonies:auto/bigreactors/basic_reactorsolidaccessport",
    "industrial_colonies:auto/bigreactors/reinforced_reactorchargingportfe",
    "industrial_colonies:auto/bigreactors/reinforced_reactorfluidaccessport",
    "industrial_colonies:auto/bigreactors/reinforced_reactorfluidport_forge_active",
    "industrial_colonies:auto/bigreactors/reinforced_reactorfluidport_forge_passive",
    "industrial_colonies:auto/bigreactors/reinforced_reactorfluidport_mekanism_passive",
    "industrial_colonies:auto/bigreactors/reinforced_reactorglass",
    "industrial_colonies:auto/bigreactors/reinforced_reactorpowertapfe_active",
    "industrial_colonies:auto/bigreactors/reinforced_reactorpowertapfe_passive",
    "industrial_colonies:auto/bigreactors/reinforced_reactorredstoneport",
    "industrial_colonies:auto/bigreactors/reinforced_reactorsolidaccessport",
    "industrial_colonies:auto/bigreactors/reprocessorglass",
    "industrial_colonies:auto/bigreactors/yellorium_block",
    "industrial_colonies:auto/er2create/reinforced_reactordisplaysource",
    "industrial_colonies:auto/mekanism/block_raw_uranium",
    "industrial_colonies:auto/mekanism/nugget_uranium",
}

BATCHES = [
    {
        "id": "tfmg_first_heavy_and_electrical",
        "priority": 1,
        "outputs": [
            "tfmg:centrifuge",
            "tfmg:diesel_engine_cylinder",
            "tfmg:engine_cylinder",
            "tfmg:electrode_holder",
            "tfmg:transformer",
            "tfmg:voltage_observer",
            "createaddition:digital_adapter",
            "createaddition:portable_energy_interface",
        ],
        "prerequisite_outputs": [
            "tfmg:cast_iron_frame",
            "tfmg:copper_spool",
            "tfmg:steel_casing",
            "tfmg:circuit_board",
            "tfmg:transistor_item",
            "tfmg:capacitor_item",
            "create:precision_mechanism",
        ],
        "recommended_environments": {
            "heavy_rotating_and_engine_parts": "createcasing:industrial_iron_press/deployer",
            "electrical_windings_and_observation": "createcasing:copper_press/deployer",
            "precision_adapters": "createcasing:brass_press/deployer",
        },
        "cycle_risks": [
            "Do not require a transformer, centrifuge, finished engine, or refined fuel to manufacture its own prerequisite subassembly.",
            "Keep the cast-iron and first-steel bootstrap earlier than industrial-iron-environment recipes.",
            "The portable energy interface must not become a prerequisite of the copper spool or base connector that it consumes.",
        ],
    },
    {
        "id": "digital_core_and_peripherals",
        "priority": 2,
        "outputs": [
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
        ],
        "prerequisite_outputs": [
            "tfmg:circuit_board",
            "ae2:logic_processor",
            "ae2:calculation_processor",
            "ae2:engineering_processor",
            "computercraft:wired_modem_full",
        ],
        "recommended_environments": {
            "board_and_bus_assembly": "createcasing:copper_deployer/press",
            "precision_terminal_and_interface_assembly": "createcasing:brass_deployer/press",
        },
        "cycle_risks": [
            "Peripheral casing must precede all six Advanced Peripherals devices.",
            "AE2 interface must precede the ME bridge; item and chemical housings must precede their stock-preserved cell closures.",
            "Do not require Mekanism advanced circuits for the first usable ME network; digital logistics must exist before the nuclear tier.",
        ],
    },
    {
        "id": "mekanism_pre_nuclear_machine_chain",
        "priority": 3,
        "outputs": [
            "mekanism:chemical_infuser",
            "mekanism:chemical_oxidizer",
            "mekanism:crusher",
            "mekanism:electrolytic_separator",
            "mekanism:enrichment_chamber",
            "mekanism:osmium_compressor",
            "mekanism:precision_sawmill",
            "mekanism:pressurized_reaction_chamber",
        ],
        "prerequisite_outputs": [
            "tfmg:circuit_board",
            "tfmg:steel_casing",
            "tfmg:steel_chemical_vat",
            "tfmg:transformer",
            "mekanism:basic_control_circuit",
            "create:mechanical_pump",
        ],
        "recommended_environments": {
            "electrochemical_controls": "createcasing:copper_deployer/press",
            "pressure_and_process_frames": "createcasing:industrial_iron_press/deployer",
            "precision_sawmill": "createcasing:brass_deployer/press",
        },
        "cycle_risks": [
            "Enrichment chamber must precede the pressurized reaction chamber and purification line.",
            "Do not use HDPE or a product of the PRC to construct the first PRC.",
            "Sulfuric acid remains TFMG chemical-vat-owned; no machine recipe may create a second acid route.",
        ],
    },
    {
        "id": "mekanism_universal_cable_tail",
        "priority": 4,
        "outputs": [
            "mekanism:advanced_universal_cable",
            "mekanism:elite_universal_cable",
            "mekanism:ultimate_universal_cable",
        ],
        "prerequisite_outputs": [
            "mekanism:basic_universal_cable",
            "tfmg:copper_spool",
            "electroenergetics:extreme_wire",
            "tfmg:sulfur_hexafluoride_bucket",
        ],
        "recommended_environments": {
            "conductor_lamination": "createcasing:copper_press",
            "high_voltage_insulation": "createcasing:industrial_iron_deployer",
        },
        "cycle_risks": [
            "Keep the basic cable reachable before the first upgraded-cable recipe.",
            "Only the Ultimate convergence may require the Extreme wire and SF6 contract; applying both to Advanced would jump directly to the late grid.",
            "The tier-installer runtime blacklist must cover the managed cable ladder or recipes remain bypassable.",
        ],
    },
    {
        "id": "ae2_high_energy_spatial_and_mega_core",
        "priority": 5,
        "outputs": [
            "ae2:cell_workbench",
            "ae2:controller",
            "ae2:export_bus",
            "ae2:io_port",
            "ae2:me_p2p_tunnel",
            "ae2:spatial_anchor",
            "ae2:spatial_io_port",
            "ae2:spatial_pylon",
            "megacells:mega_crafting_unit",
        ],
        "prerequisite_outputs": [
            "ae2:interface",
            "ae2:terminal",
            "ae2:engineering_processor",
            "ae2:calculation_processor",
            "megacells:accumulation_processor",
            "tfmg:transformer",
        ],
        "recommended_environments": {
            "network_control_hardware": "createcasing:brass_deployer/press",
            "high_energy_and_spatial_frames": "createcasing:industrial_iron_press/deployer",
        },
        "cycle_risks": [
            "Controller, IO port, and P2P must not depend on spatial hardware.",
            "Move spatial transport and the mega core to Nuclear Engineering or Post-Nuclear Megaprojects without moving the first ME network with them.",
            "Keep bulk cell closures stock-preserved so factory scaling does not require one 5x5 craft per cell.",
        ],
    },
    {
        "id": "mekanism_nuclear_chemical_and_sps",
        "priority": 6,
        "outputs": [
            "mekanism:antiprotonic_nucleosynthesizer",
            "mekanism:chemical_crystallizer",
            "mekanism:chemical_dissolution_chamber",
            "mekanism:chemical_injection_chamber",
            "mekanism:chemical_washer",
            "mekanism:isotopic_centrifuge",
            "mekanism:purification_chamber",
            "mekanism:radioactive_waste_barrel",
            "mekanism:solar_neutron_activator",
            "mekanism:sps_casing",
            "mekanism:sps_port",
            "mekanism:supercharged_coil",
        ],
        "prerequisite_outputs": [
            "mekanism:enrichment_chamber",
            "mekanism:chemical_infuser",
            "mekanism:ultimate_control_circuit",
            "tfmg:steel_chemical_vat",
            "tfmg:transformer",
            "ae2:engineering_processor",
        ],
        "recommended_environments": {
            "chemical_pressure_equipment": "createcasing:industrial_iron_press/deployer",
            "nuclear_instrumentation": "createcasing:refined_radiance_press/deployer",
        },
        "cycle_risks": [
            "Purification, dissolution, washing, crystallization, and injection must form a forward uranium-processing path, not mutually require later machines.",
            "The first usable uranium input must exist before any reactor or SPS product is required.",
            "SPS casing must precede SPS port and supercharged coil; antimatter may only appear after an operational SPS path.",
        ],
    },
    {
        "id": "bigreactors_bulk_structures_and_controllers",
        "priority": 7,
        "outputs": [
            "bigreactors:basic_reactorcasing",
            "bigreactors:basic_reactorcontrolrod",
            "bigreactors:basic_reactorfuelrod",
            "bigreactors:basic_turbinecasing",
            "bigreactors:basic_turbinecontroller",
            "bigreactors:basic_turbinerotorbearing",
            "bigreactors:basic_turbinerotorblade",
            "bigreactors:basic_turbinerotorshaft",
            "bigreactors:energizercasing",
            "bigreactors:energizercontroller",
            "bigreactors:fluidizercasing",
            "bigreactors:fluidizercontroller",
            "bigreactors:reinforced_reactorcasing",
            "bigreactors:reinforced_reactorcontrolrod",
            "bigreactors:reinforced_reactorfuelrod",
            "bigreactors:reinforced_turbinecasing",
            "bigreactors:reinforced_turbinecontroller",
            "bigreactors:reinforced_turbinerotorbearing",
            "bigreactors:reinforced_turbinerotorblade",
            "bigreactors:reinforced_turbinerotorshaft",
            "bigreactors:reprocessorcasing",
            "bigreactors:reprocessorcollector",
            "bigreactors:reprocessorcontroller",
            "bigreactors:reprocessorfluidinjector",
            "bigreactors:reprocessoroutputport",
            "bigreactors:reprocessorpowerport",
            "bigreactors:reprocessorwasteinjector",
        ],
        "prerequisite_outputs": [
            "tfmg:heavy_plate",
            "tfmg:steel_casing",
            "tfmg:transformer",
            "computercraft:computer_advanced",
            "computercraft:monitor_advanced",
            "mekanism:ingot_uranium",
        ],
        "recommended_environments": {
            "bulk_casing_and_rotors": "createcasing:industrial_iron_press/deployer",
            "controllers_and_safety_instrumentation": "createcasing:brass_deployer plus ComputerCraft subassemblies",
        },
        "cycle_risks": [
            "Basic reactor structures cannot consume cyanite, plutonium, reactor waste, or any material produced only after the first reactor runs.",
            "Bulk casings and rotor parts should be batched from reusable heavy subcomponents; do not charge full control electronics for every wall block.",
            "Energizer and fluidizer recipes cannot require the fuel product they enable, and reinforced-tier parts must remain downstream of the basic tier.",
        ],
    },
]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def is_gate_ring(recipe: dict[str, Any]) -> bool:
    pattern = recipe.get("pattern")
    return bool(
        recipe.get("type") == "mechanical_crafting"
        and isinstance(pattern, list)
        and len(pattern) == 5
        and pattern[0] == "ABABA"
        and pattern[4] == "ABABA"
        and all(isinstance(row, str) and len(row) == 5 for row in pattern)
        and pattern[1][0] == pattern[1][4] == "B"
        and pattern[2][0] == pattern[2][4] == "A"
        and pattern[3][0] == pattern[3][4] == "B"
    )


def classification(managed_id: str) -> str:
    if managed_id in ACCEPTABLE:
        return "acceptable_stock_derived_utility"
    if managed_id in REDUNDANT:
        return "redundant_should_retire"
    if managed_id in LEAVE_STOCK:
        return "runtime_artifact_leave_stock"
    return "needs_source_owned_redesign"


def rationale(managed_id: str, output: str, category: str, source_type: str) -> str:
    if managed_id.endswith("/create/crushing_wheel"):
        return "Installed Create mechanical-crafting layout is already a legible machine recipe and is the snapshot's only non-generic automatic 5x5 layout."
    if managed_id.endswith("/tfmg/cast_iron_frame"):
        return "Canonical TFMG material conversion yields four reusable cast-iron frames at stock scale without an injected gate ring."
    if managed_id.endswith("/tfmg/copper_spool"):
        return "Canonical TFMG-first bulk electrical component; the stock wire winding already depends on the source-owned empty spool."
    if category == "acceptable_stock_derived_utility":
        return "Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring."
    if category == "redundant_should_retire":
        family = "Create Metallurgy" if "/createmetallurgy/" in managed_id else "Modern Foundry"
        return f"{family} duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route."
    if category == "runtime_artifact_leave_stock":
        if "tier_installer" in output:
            return "Tier installer is a general runtime utility; preserve its exact stock recipe and enforce managed factory/cube/transmitter ladders with the Mekanism installer blacklist."
        if any(token in output for token in ("storage_cell", "crafting_storage", "cable", "connector")):
            return "Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring."
        if output in {"mekanism:block_raw_uranium", "mekanism:nugget_uranium", "bigreactors:yellorium_block", "tfmg:coal_coke"}:
            return "Reversible material packing/unpacking is a utility conversion, not a progression gate; preserve the exact stock recipe and audit the underlying material-production path separately."
        if source_type == "mekanism:mek_data":
            return "Runtime-generated utility recipe should remain runtime-owned; do not clone it into a generic mechanical-crafting wrapper."
        return "Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated."
    if output.startswith("tfmg:") or output.startswith("createaddition:"):
        return "Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies."
    if output.startswith("ae2:") or output.startswith("appmek:") or output.startswith("advancedperipherals:") or output.startswith("megacells:"):
        return "Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear."
    if output.startswith("mekanism:"):
        return "Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design."
    if output.startswith("bigreactors:"):
        return "Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate."
    return "Automatic gate-ring conversion does not express the output's function; replace it with an explicit source-owned manufacturing contract."


def disposition(category: str) -> str:
    return {
        "acceptable_stock_derived_utility": "keep_automatic_exact_stock",
        "needs_source_owned_redesign": "replace_with_source_owned_contract",
        "redundant_should_retire": "retire_output_after_route_parity_check",
        "runtime_artifact_leave_stock": "retire_automatic_owner_preserve_exact_source",
    }[category]


def main() -> None:
    managed = load_json(MANAGED)
    report = load_json(REPORT)
    managed_auto = {
        recipe["id"]: recipe
        for recipe in managed.get("recipes", [])
        if isinstance(recipe, dict)
        and isinstance(recipe.get("id"), str)
        and recipe["id"].startswith("industrial_colonies:auto/")
    }
    generated_auto = {
        row["managed_recipe"]: row
        for row in report.get("generated", [])
        if isinstance(row, dict)
        and isinstance(row.get("managed_recipe"), str)
        and row["managed_recipe"].startswith("industrial_colonies:auto/")
    }
    if set(managed_auto) != set(generated_auto):
        raise ValueError("managed/report automatic owner sets differ")
    if not (ACCEPTABLE | REDUNDANT | LEAVE_STOCK) <= set(managed_auto):
        missing = (ACCEPTABLE | REDUNDANT | LEAVE_STOCK) - set(managed_auto)
        raise ValueError(f"classification IDs absent from snapshot: {sorted(missing)}")

    entries: list[dict[str, Any]] = []
    output_to_entry: dict[str, dict[str, Any]] = {}
    for managed_id, recipe in managed_auto.items():
        source = generated_auto[managed_id]
        category = classification(managed_id)
        entry = {
            "managed_id": managed_id,
            "output": source["output"],
            "managed_output": recipe.get("output"),
            "phase": source["phase"],
            "node": source["node"],
            "source_recipe_id": source["source_recipe"],
            "source_type": source["source_type"],
            "managed_type": recipe.get("type"),
            "exact_removals": source.get("removals", []),
            "stock_ingredients": source.get("stock_ingredients", []),
            "managed_dependencies": source.get("depends_on", []),
            "generic_gate_ring": is_gate_ring(recipe),
            "classification": category,
            "disposition": disposition(category),
            "rationale": rationale(
                managed_id, str(source["output"]), category, str(source["source_type"])
            ),
        }
        entries.append(entry)
        output_to_entry[str(source["output"])] = entry

    for batch in BATCHES:
        batch["managed_ids"] = [output_to_entry[value]["managed_id"] for value in batch["outputs"]]
        batch["installed_recipe_ids"] = [
            output_to_entry[value]["source_recipe_id"] for value in batch["outputs"]
        ]

    entries.sort(key=lambda row: (managed["phase_order"].index(row["phase"]), row["managed_id"]))
    counts = Counter(row["classification"] for row in entries)
    phase_counts: dict[str, dict[str, int]] = {}
    for phase in managed["phase_order"]:
        selected = [row for row in entries if row["phase"] == phase]
        phase_counts[phase] = dict(sorted(Counter(row["classification"] for row in selected).items()))

    plan = {
        "schema_version": 1,
        "status": "read_only_quality_audit_complete",
        "plan_id": "automatic_managed_recipe_quality",
        "audited_on": "2026-08-31",
        "decision": "KEEP_27_REDESIGN_81_RETIRE_8_LEAVE_STOCK_56",
        "scope": {
            "snapshot_directory": "build-current-audit",
            "managed_file": "build-current-audit/managed.json",
            "managed_sha256": sha256(MANAGED),
            "report_file": "build-current-audit/report.json",
            "report_sha256": sha256(REPORT),
            "automatic_owner_count": len(entries),
            "automatic_mechanical_crafting_count": sum(
                row["managed_type"] == "mechanical_crafting" for row in entries
            ),
            "generic_gate_ring_count": sum(row["generic_gate_ring"] for row in entries),
            "source_type_counts": dict(
                sorted(Counter(row["source_type"] for row in entries).items())
            ),
        },
        "principles": [
            "Difficulty belongs in reusable manufactured subcomponents and capability order, not in identical gate rings pasted around every output.",
            "TFMG owns overlapping fuels, electronics, pressure chemistry, and heavy industrial materials unless an audited unique function requires another system.",
            "Copper environments make electrical parts, Brass environments make precision/digital parts, and Industrial Iron environments make pressure/heavy components.",
            "The first useful Create, TFMG, Mekanism, ComputerCraft, and AE2 capabilities must exist before late nuclear construction; spatial and mega-scale extensions may move later.",
            "Bulk closures, reversible storage forms, visual variants, and compatibility adapters inherit progression from their hard prerequisite and stay stock-scalable.",
        ],
        "classification_counts": dict(sorted(counts.items())),
        "phase_counts": phase_counts,
        "implementation_batches": BATCHES,
        "entries": entries,
    }
    PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    MARKDOWN.write_text(render_markdown(plan), encoding="utf-8")


def render_markdown(plan: dict[str, Any]) -> str:
    entries = plan["entries"]
    counts = plan["classification_counts"]
    labels = {
        "acceptable_stock_derived_utility": "Acceptable stock-derived / utility",
        "needs_source_owned_redesign": "Needs source-owned redesign",
        "redundant_should_retire": "Redundant / should retire",
        "runtime_artifact_leave_stock": "Runtime artifact / leave stock",
    }
    lines = [
        "# Automatic Recipe Quality Audit",
        "",
        "Status: **read-only audit complete**. This document audits the pinned `build-current-audit` snapshot only. It does not authorize or perform seed, assignment, generated-artifact, quest, deployment, live-pack, or Draw.io edits.",
        "",
        "## Outcome",
        "",
        f"The snapshot contains **{plan['scope']['automatic_owner_count']}** automatic recipe owners. Exactly **{plan['scope']['generic_gate_ring_count']} of {plan['scope']['automatic_mechanical_crafting_count']}** automatic Mechanical Crafting recipes use the same generated `A/B` perimeter. The one exception is Create's installed Crushing Wheel layout. That makes the problem structural: the converter is expressing phase gates, not manufacturing logic.",
        "",
        "| Disposition | Count | Meaning |",
        "|---|---:|---|",
        f"| Acceptable stock-derived / utility | {counts['acceptable_stock_derived_utility']} | Keep the automatic exact-stock owner. |",
        f"| Needs source-owned redesign | {counts['needs_source_owned_redesign']} | Replace the generated owner with an explicit recipe contract. |",
        f"| Redundant / should retire | {counts['redundant_should_retire']} | Disable the duplicate output only after route-parity proof. |",
        f"| Runtime artifact / leave stock | {counts['runtime_artifact_leave_stock']} | Retire the automatic owner and preserve its exact installed recipe. |",
        "",
        "The **81 redesigns are the actual content backlog**. The 56 leave-stock items are not freebies: their prerequisite processors, housings, casings, conductors, or machines carry the progression cost once those reusable chains are fixed.",
        "",
        "## Rules used",
        "",
    ]
    lines.extend(f"- {rule}" for rule in plan["principles"])
    lines += ["", "## Priority implementation batches", ""]
    for batch in plan["implementation_batches"]:
        lines += [
            f"### {batch['priority']}. `{batch['id']}`",
            "",
            "Outputs and installed source recipe IDs:",
            "",
            "| Output | Installed recipe ID |",
            "|---|---|",
        ]
        for output, recipe_id in zip(batch["outputs"], batch["installed_recipe_ids"]):
            lines.append(f"| `{output}` | `{recipe_id}` |")
        lines += ["", "Prerequisite capabilities:", ""]
        lines.extend(f"- `{value}`" for value in batch["prerequisite_outputs"])
        lines += ["", "Recommended encased roles:", ""]
        lines.extend(
            f"- `{role}` → `{machine}`"
            for role, machine in batch["recommended_environments"].items()
        )
        lines += ["", "Cycle risks:", ""]
        lines.extend(f"- {risk}" for risk in batch["cycle_risks"])
        lines.append("")

    lines += [
        "## Redundant systems",
        "",
        "The eight duplicate foundry endpoints are retirement candidates, not immediate deletions. Before retiring them, prove that every unique cast, alloy, and mold route they enable has a TFMG-first canonical path. This prevents the cure from creating a new dead end.",
        "",
        "## Complete ID-by-ID classification",
        "",
    ]
    for category in labels:
        selected = [row for row in entries if row["classification"] == category]
        lines += [
            f"### {labels[category]} ({len(selected)})",
            "",
            "| Output | Installed recipe ID | Phase | Decision basis |",
            "|---|---|---|---|",
        ]
        for row in selected:
            reason = row["rationale"].replace("|", "\\|")
            lines.append(
                f"| `{row['output']}` | `{row['source_recipe_id']}` | {row['phase']} | {reason} |"
            )
        lines.append("")

    lines += [
        "## Validation boundary",
        "",
        f"The audit is pinned to SHA-256 `{plan['scope']['managed_sha256']}` for `managed.json` and `{plan['scope']['report_sha256']}` for `report.json`. If either snapshot changes, regenerate and review this audit instead of silently carrying classifications forward.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
