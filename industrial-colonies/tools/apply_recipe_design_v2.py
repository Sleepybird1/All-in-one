#!/usr/bin/env python3
"""Apply the hand-authored, manufacturing-first recipe redesign.

This migration deliberately edits only recipes whose process, ingredients, or
shape differ from stock.  It is idempotent so later recipe-design waves can be
added here without reintroducing retired template recipes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import recipe_design_v2_digital
import recipe_design_v2_digital_storage_gaps
import recipe_design_v2_ae2_coverage
import recipe_design_v2_appliedcreate_coverage
import recipe_design_v2_big_cannons_coverage
import recipe_design_v2_compacting_cleanup
import recipe_design_v2_computer_network_coverage
import recipe_design_v2_create_addon_coverage
import recipe_design_v2_create_connected_expansion
import recipe_design_v2_create_core
import recipe_design_v2_createcasing_coverage
import recipe_design_v2_dependency_order_cleanup
import recipe_design_v2_enchantment_industry_coverage
import recipe_design_v2_high_energy
import recipe_design_v2_interstellar_component_gap
import recipe_design_v2_electroenergetics_functional_gaps
import recipe_design_v2_late_grids
import recipe_design_v2_lowheat
import recipe_design_v2_mechanical
import recipe_design_v2_mek_induction_refinement
import recipe_design_v2_mekanism
import recipe_design_v2_mek_bigreactors_coverage
import recipe_design_v2_mek_components_tools
import recipe_design_v2_metallurgy_functional_gaps
import recipe_design_v2_mekanism_utility_gaps
import recipe_design_v2_power_addon_gaps
import recipe_design_v2_process_corrections
import recipe_design_v2_shape_refinement
import recipe_design_v2_simulated_coverage
import recipe_design_v2_specialized_create_gaps
import recipe_design_v2_stock_retirement
import recipe_design_v2_space_coverage
import recipe_design_v2_space_hardware_gaps
import recipe_design_v2_tfmg
import recipe_design_v2_tfmg_component_gaps
import recipe_design_v2_tfmg_core_components
import recipe_design_v2_tfmg_coverage
import recipe_design_v2_tfmg_duplicate_canonicalization
import recipe_design_v2_tfmg_electrical
import recipe_design_v2_tfmg_remaining_hardware
import recipe_design_v3_user_references
import recipe_design_v3_computercraft
import recipe_design_v3_ae2_mega
import recipe_design_v3_createcasing_progression
import recipe_design_v3_mekanism
import recipe_design_v3_phase_alignment
import recipe_design_v3_progression_bootstrap
import recipe_design_v3_storage_cells
import recipe_design_v3_structural_compacting
import recipe_design_v4_rejected_redesigns
import recipe_design_v4_electronics_primitives
import recipe_design_v4_machine_family_corrections
import recipe_design_v4_digital_machine_corrections
import recipe_design_v4_ae2_electronics_depth
import recipe_design_v4_stress_storage_depth
import recipe_design_v4_mega_storage_depth
import recipe_design_v4_space_electronics
import recipe_design_v4_space_hardware_depth
import recipe_design_v4_bigreactors_rejected
import recipe_design_v4_ae2_remaining_depth
import recipe_design_v4_manufacturing_rejects
import recipe_design_v4_manual_rejections
import recipe_design_v5_pumpjack_manufacturing
import recipe_design_v5_digital_transmission
import recipe_design_v5_nuclear_hardware
import recipe_design_v6_review_20260904
import recipe_design_v7_review_20260904


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


def load_seed() -> dict[str, Any]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def recipe_index(data: dict[str, Any]) -> dict[str, int]:
    return {recipe["id"]: index for index, recipe in enumerate(data["recipes"])}


def managed_item_id(value: Any) -> str | None:
    """Return the item identifier from a managed item stack declaration."""

    if isinstance(value, str):
        raw = value.strip()
        if not raw or raw.startswith("#"):
            return None
        parts = raw.split()
        if len(parts) == 2 and parts[0].endswith("x") and parts[0][:-1].isdigit():
            raw = parts[1]
        return raw if ":" in raw else None
    if isinstance(value, dict):
        if str(value.get("kind", "ITEM")).upper() != "ITEM":
            return None
        identifier = value.get("id") or value.get("item")
        return identifier if isinstance(identifier, str) and ":" in identifier else None
    return None


def managed_recipe_outputs(recipe: dict[str, Any]) -> set[str]:
    outputs: set[str] = set()
    if identifier := managed_item_id(recipe.get("output")):
        outputs.add(identifier)
    for field in ("results", "outputs"):
        values = recipe.get(field, [])
        if not isinstance(values, list):
            values = [values]
        for value in values:
            if identifier := managed_item_id(value):
                outputs.add(identifier)
    return outputs


def replace_recipe(data: dict[str, Any], recipe_id: str, body: dict[str, Any]) -> None:
    indexes = recipe_index(data)
    if recipe_id not in indexes:
        # A later design wave can intentionally replace a v2 card with a new,
        # better-named authoritative card.  On subsequent runs the v2 pass is
        # still executed first, so treat the missing legacy ID as already
        # migrated only when its exact requested output is still owned.  Any
        # genuinely missing output continues to fail closed.
        wanted_outputs = managed_recipe_outputs(body)
        if wanted_outputs and any(
            wanted_outputs.intersection(managed_recipe_outputs(recipe))
            for recipe in data["recipes"]
        ):
            return
        raise KeyError(f"Expected managed recipe is missing: {recipe_id}")
    old = data["recipes"][indexes[recipe_id]]
    replacement: dict[str, Any] = {"id": recipe_id}
    for key in ("node", "phase", "order"):
        if key in old:
            replacement[key] = old[key]
    replacement.update(body)
    for key in ("remove", "exclusive_output", "if_mod_loaded", "depends_on"):
        if key not in replacement and key in old:
            replacement[key] = old[key]
    data["recipes"][indexes[recipe_id]] = replacement


def upsert_recipe(data: dict[str, Any], recipe: dict[str, Any]) -> None:
    indexes = recipe_index(data)
    if recipe["id"] in indexes:
        data["recipes"][indexes[recipe["id"]]] = recipe
    else:
        data["recipes"].append(recipe)


def deploy(ingredient: str, machine: str = "createcasing:brass_deployer") -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def press(machine: str = "createcasing:brass_press") -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def sequence(
    *,
    recipe_type: str,
    comment: str,
    input_item: str,
    transitional: str,
    output: Any,
    steps: list[dict[str, Any]],
    loops: int = 1,
    remove: list[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": recipe_type,
        "comment": comment,
        "input": input_item,
        "transitional": transitional,
        "output": output,
        "loops": loops,
        "steps": steps,
        "exclusive_output": True,
    }
    if remove is not None:
        result["remove"] = remove
    return result


def redesign_semiconductor_line(data: dict[str, Any]) -> None:
    semiconductor_recipes = [
        {
            "id": "industrial_colonies:electronics/n_semiconductor",
            "phase": "Electrical Manufacturing",
            "order": 20,
            "type": "tfmg_vat",
            "comment": "Dope a four-piece silicon batch with sulfur in a heated steel Chemical Vat; this is the N-type wafer line, not a basin-mixing shortcut",
            "ingredients": [
                "3x tfmg:silicon_ingot",
                "tfmg:sulfur_dust",
                {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 250},
            ],
            "results": [{"kind": "ITEM", "id": "tfmg:n_semiconductor", "count": 4}],
            "vat_mode": "steel",
            "machine_mode": "mixing",
            "heat": "heated",
            "min_size": 3,
            "processing_time": 300,
            "remove": ["tfmg:mixing/n_semiconductor"],
            "exclusive_output": True,
        },
        {
            "id": "industrial_colonies:electronics/p_semiconductor",
            "phase": "Electrical Manufacturing",
            "order": 21,
            "type": "tfmg_vat",
            "comment": "Dope a four-piece silicon batch with aluminum in a heated steel Chemical Vat; this is the separate P-type wafer line",
            "ingredients": [
                "3x tfmg:silicon_ingot",
                {"kind": "ITEM_TAG", "id": "c:ingots/aluminum"},
                {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 250},
            ],
            "results": [{"kind": "ITEM", "id": "tfmg:p_semiconductor", "count": 4}],
            "vat_mode": "steel",
            "machine_mode": "mixing",
            "heat": "heated",
            "min_size": 3,
            "processing_time": 300,
            "remove": ["tfmg:mixing/p_semiconductor"],
            "exclusive_output": True,
        },
    ]
    for recipe in semiconductor_recipes:
        upsert_recipe(data, recipe)


def redesign_processor_lines(data: dict[str, Any]) -> None:
    replace_recipe(
        data,
        "industrial_colonies:electronics/stress_processor",
        sequence(
            recipe_type="sequenced_assembly",
            comment="Populate the Copper-made stress board on the Brass electronics line, then press the finished processor package",
            input_item="appliedcreate:stress_circuit_board",
            transitional="appliedcreate:stress_circuit_board",
            output="appliedcreate:stress_processor",
            steps=[
                deploy("ae2:printed_silicon"),
                deploy("tfmg:transistor_item"),
                deploy("tfmg:capacitor_item"),
                deploy("create:cinder_flour"),
                deploy("tfmg:copper_wire"),
                press(),
            ],
            remove=[
                "appliedcreate:inscriber/stress_processor",
                "appliedcreate:crystal_assembler/stress_processor",
            ],
        ),
    )
    replace_recipe(
        data,
        "industrial_colonies:electronics/advanced_stress_processor",
        sequence(
            recipe_type="sequenced_assembly",
            comment="Mount the prior stress processor onto an advanced board with magnetic shielding and Brass-line control logic",
            input_item="appliedcreate:advanced_stress_circuit_board",
            transitional="appliedcreate:advanced_stress_circuit_board",
            output="appliedcreate:advanced_stress_processor",
            steps=[
                deploy("appliedcreate:stress_processor"),
                deploy("ae2:logic_processor"),
                deploy("tfmg:magnetic_alloy_sheet"),
                deploy("tfmg:capacitor_item"),
                deploy("create:cinder_flour"),
                press(),
            ],
            remove=[
                "appliedcreate:inscriber/advanced_stress_processor",
                "appliedcreate:crystal_assembler/advanced_stress_processor",
            ],
        ),
    )

    ae_processors = {
        "industrial_colonies:ae2/logic_processor": sequence(
            recipe_type="sequenced_assembly",
            comment="Build the logic processor on a TFMG board with a balanced semiconductor pair and a Brass package press",
            input_item="tfmg:circuit_board",
            transitional="createappliedkinetics:incomplete_logic_processor",
            output="ae2:logic_processor",
            steps=[
                deploy("ae2:printed_logic_processor"),
                deploy("ae2:printed_silicon"),
                deploy("tfmg:n_semiconductor"),
                deploy("tfmg:p_semiconductor"),
                deploy("minecraft:redstone"),
                press(),
            ],
            remove=["ae2:inscriber/logic_processor", "extendedae:assembler/logic_processor"],
        ),
        "industrial_colonies:ae2/calculation_processor": sequence(
            recipe_type="sequenced_assembly",
            comment="Build the calculation processor as a fluix-timed signal package on the same Brass semiconductor line",
            input_item="tfmg:circuit_board",
            transitional="createappliedkinetics:incomplete_calculation_processor",
            output="ae2:calculation_processor",
            steps=[
                deploy("ae2:printed_calculation_processor"),
                deploy("ae2:printed_silicon"),
                deploy("tfmg:capacitor_item"),
                deploy("#c:dusts/fluix"),
                deploy("tfmg:transistor_item"),
                press(),
            ],
            remove=[
                "ae2:inscriber/calculation_processor",
                "extendedae:assembler/calculation_processor",
            ],
        ),
        "industrial_colonies:ae2/engineering_processor": sequence(
            recipe_type="sequenced_assembly",
            comment="Build the engineering processor as a magnetically shielded high-current package, still fabricated on the Brass electronics line",
            input_item="tfmg:circuit_board",
            transitional="createappliedkinetics:incomplete_engineering_processor",
            output="ae2:engineering_processor",
            steps=[
                deploy("ae2:printed_engineering_processor"),
                deploy("ae2:printed_silicon"),
                deploy("tfmg:transistor_item"),
                deploy("tfmg:capacitor_item"),
                deploy("tfmg:magnetic_alloy_sheet"),
                deploy("tfmg:nickel_sheet"),
                press(),
            ],
            remove=[
                "ae2:inscriber/engineering_processor",
                "extendedae:assembler/engineering_processor",
            ],
        ),
    }
    for recipe_id, body in ae_processors.items():
        replace_recipe(data, recipe_id, body)

    replace_recipe(
        data,
        "industrial_colonies:digital/accumulation_processor",
        sequence(
            recipe_type="sequenced_assembly",
            comment="Package accumulation logic with TFMG board layers, lithium-backed capacitors, fluix timing, and magnetic shielding",
            input_item="megacells:printed_accumulation_processor",
            transitional="megacells:printed_accumulation_processor",
            output="megacells:accumulation_processor",
            steps=[
                deploy("tfmg:coated_circuit_board"),
                deploy("ae2:printed_silicon"),
                deploy("tfmg:capacitor_item"),
                deploy("tfmg:capacitor_item"),
                deploy("tfmg:lithium_charge"),
                deploy("#c:dusts/fluix"),
                deploy("tfmg:magnetic_alloy_sheet"),
                press(),
            ],
            remove=[
                "megacells:inscriber/accumulation_processor",
                "extendedae:assembler/accumulation_processor",
            ],
        ),
    )
    replace_recipe(
        data,
        "industrial_colonies:megacells/cell_component_1m",
        sequence(
            recipe_type="sequenced_assembly",
            comment="Stack exactly four 256k matrices into a protected 1M memory module with dedicated accumulation logic and insulation",
            input_item="ae2:cell_component_256k",
            transitional="industrial_colonies:unfinished_mega_cell_component_1m",
            output="megacells:cell_component_1m",
            steps=[
                deploy("ae2:cell_component_256k"),
                deploy("ae2:cell_component_256k"),
                deploy("ae2:cell_component_256k"),
                deploy("megacells:accumulation_processor"),
                deploy("megacells:accumulation_processor"),
                deploy("ae2:quartz_vibrant_glass"),
                deploy("ae2:sky_dust"),
                deploy("tfmg:plastic_sheet"),
                deploy("tfmg:magnetic_alloy_sheet"),
                press(),
            ],
            remove=["megacells:cells/cell_component_1m"],
        ),
    )


def redesign_mekanism_circuits(data: dict[str, Any]) -> None:
    replacements = {
        "industrial_colonies:mekanism/advanced_control_circuit": sequence(
            recipe_type="sequenced_assembly",
            comment="Upgrade basic control logic with two infused-alloy conductor layers and discrete TFMG electronics on the Brass line",
            input_item="mekanism:basic_control_circuit",
            transitional="mekanism:basic_control_circuit",
            output="mekanism:advanced_control_circuit",
            steps=[
                deploy("mekanism:alloy_infused"),
                deploy("mekanism:alloy_infused"),
                deploy("tfmg:capacitor_item"),
                deploy("tfmg:transistor_item"),
                deploy("tfmg:magnetic_alloy_sheet"),
                press(),
            ],
            remove=[
                "mekanism:control_circuit/advanced",
                "mekanism:control_circuit/infused_advanced",
            ],
        ),
        "industrial_colonies:mekanism/elite_control_circuit": sequence(
            recipe_type="sequenced_assembly",
            comment="Upgrade an advanced circuit with reinforced conductor layers and calculation logic on the Brass electronics line",
            input_item="mekanism:advanced_control_circuit",
            transitional="mekanism:advanced_control_circuit",
            output="mekanism:elite_control_circuit",
            steps=[
                deploy("mekanism:alloy_reinforced"),
                deploy("mekanism:alloy_reinforced"),
                deploy("ae2:calculation_processor"),
                deploy("tfmg:capacitor_item"),
                deploy("tfmg:magnetic_alloy_sheet"),
                press(),
            ],
            remove=["mekanism:control_circuit/elite", "mekanism:control_circuit/infused_elite"],
        ),
        "industrial_colonies:mekanism/ultimate_control_circuit": sequence(
            recipe_type="sequenced_assembly",
            comment="Upgrade elite control logic with atomic conductors, engineering logic, and an advanced stress processor before final Brass packaging",
            input_item="mekanism:elite_control_circuit",
            transitional="mekanism:elite_control_circuit",
            output="mekanism:ultimate_control_circuit",
            steps=[
                deploy("mekanism:alloy_atomic"),
                deploy("mekanism:alloy_atomic"),
                deploy("ae2:engineering_processor"),
                deploy("appliedcreate:advanced_stress_processor"),
                deploy("tfmg:magnetic_alloy_sheet"),
                press(),
            ],
            remove=[
                "mekanism:control_circuit/ultimate",
                "mekanism:control_circuit/infused_ultimate",
            ],
        ),
    }
    for recipe_id, body in replacements.items():
        replace_recipe(data, recipe_id, body)


def redesign_factory_upgrades(data: dict[str, Any]) -> None:
    data["recipes"] = [
        recipe
        for recipe in data["recipes"]
        if not recipe["id"].startswith("industrial_colonies:mekanism/factory/")
    ]

    installers = [
        {
            "id": "industrial_colonies:mekanism/tier_installer/basic",
            "node": "CR01 — Modular Machinery",
            "phase": "Mekanized Industry",
            "order": 100,
            **sequence(
                recipe_type="sequenced_assembly",
                comment="Turn a steel mechanism into the first reusable factory-upgrade module with a TFMG control board and serviceable logic",
                input_item="tfmg:steel_mechanism",
                transitional="tfmg:steel_mechanism",
                output="mekanism:basic_tier_installer",
                steps=[
                    deploy("tfmg:circuit_board"),
                    deploy("mekanism:basic_control_circuit"),
                    deploy("minecraft:redstone"),
                    deploy("minecraft:redstone"),
                    deploy("create:iron_sheet"),
                    press(),
                ],
                remove=["mekanism:tier_installer/basic"],
            ),
        },
        {
            "id": "industrial_colonies:mekanism/tier_installer/advanced",
            "node": "CR01 — Modular Machinery",
            "phase": "Mekanized Industry",
            "order": 101,
            **sequence(
                recipe_type="sequenced_assembly",
                comment="Refit the basic installer with advanced control logic, osmium structure, and magnetic shielding",
                input_item="mekanism:basic_tier_installer",
                transitional="mekanism:basic_tier_installer",
                output="mekanism:advanced_tier_installer",
                steps=[
                    deploy("mekanism:advanced_control_circuit"),
                    deploy("mekanism:alloy_infused"),
                    deploy("mekanism:alloy_infused"),
                    deploy("mekanism:ingot_osmium"),
                    deploy("tfmg:magnetic_alloy_sheet"),
                    press(),
                ],
                remove=["mekanism:tier_installer/advanced"],
            ),
        },
        {
            "id": "industrial_colonies:mekanism/tier_installer/elite",
            "node": "CR01 — Precision Engineering",
            "phase": "High-Energy Grid",
            "order": 102,
            **sequence(
                recipe_type="sequenced_assembly",
                comment="Refit the advanced installer with elite logic, reinforced conductors, and a dedicated capacitor package",
                input_item="mekanism:advanced_tier_installer",
                transitional="mekanism:advanced_tier_installer",
                output="mekanism:elite_tier_installer",
                steps=[
                    deploy("mekanism:elite_control_circuit"),
                    deploy("mekanism:alloy_reinforced"),
                    deploy("mekanism:alloy_reinforced"),
                    deploy("create:golden_sheet"),
                    deploy("tfmg:capacitor_item"),
                    press(),
                ],
                remove=["mekanism:tier_installer/elite"],
            ),
        },
        {
            "id": "industrial_colonies:mekanism/tier_installer/ultimate",
            "node": "CR01 — Precision Engineering",
            "phase": "High-Energy Grid",
            "order": 103,
            **sequence(
                recipe_type="sequenced_assembly",
                comment="Complete the ultimate installer with atomic conductors, refined obsidian, and advanced stress-control hardware",
                input_item="mekanism:elite_tier_installer",
                transitional="mekanism:elite_tier_installer",
                output="mekanism:ultimate_tier_installer",
                steps=[
                    deploy("mekanism:ultimate_control_circuit"),
                    deploy("mekanism:alloy_atomic"),
                    deploy("mekanism:alloy_atomic"),
                    deploy("mekanism:ingot_refined_obsidian"),
                    deploy("appliedcreate:advanced_stress_processor"),
                    press(),
                ],
                remove=["mekanism:tier_installer/ultimate"],
            ),
        },
    ]
    for recipe in installers:
        upsert_recipe(data, recipe)

    installer_stock = {
        "mekanism:tier_installer/basic",
        "mekanism:tier_installer/advanced",
        "mekanism:tier_installer/elite",
        "mekanism:tier_installer/ultimate",
    }
    data["preserve_recipe_ids"] = [
        recipe_id
        for recipe_id in data.get("preserve_recipe_ids", [])
        if recipe_id not in installer_stock
    ]

    factory_stock = {
        f"mekanism:factory/{tier}/{process}"
        for tier in ("basic", "advanced", "elite", "ultimate")
        for process in (
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
    }
    data["additional_removals"] = sorted(
        set(data.get("additional_removals", [])) | factory_stock
    )


def retire_automatic_dependencies(data: dict[str, Any]) -> None:
    """Stock items are no longer represented by managed auto-recipe cards."""

    for recipe in data["recipes"]:
        if "depends_on" not in recipe:
            continue
        dependencies = [
            dependency
            for dependency in recipe["depends_on"]
            if not dependency.startswith("industrial_colonies:auto/")
        ]
        if dependencies:
            recipe["depends_on"] = dependencies
        else:
            recipe.pop("depends_on", None)


def retire_managed_output_exclusions(data: dict[str, Any]) -> None:
    """An explicit redesign cannot also be marked as excluded from management."""

    managed_outputs: set[str] = set()
    for recipe in data["recipes"]:
        output = recipe.get("output")
        if isinstance(output, str):
            value = output.split("x ", 1)[1] if "x " in output and output.split("x ", 1)[0].isdigit() else output
            managed_outputs.add(value)
        elif isinstance(output, dict) and isinstance(output.get("id"), str):
            managed_outputs.add(output["id"])
        for result in recipe.get("results", []):
            if isinstance(result, dict) and isinstance(result.get("id"), str):
                managed_outputs.add(result["id"])

    data["exclude_outputs"] = [
        output
        for output in data.get("exclude_outputs", [])
        if output not in managed_outputs
    ]


def retire_owned_additional_removals(data: dict[str, Any]) -> None:
    """Keep every exact stock removal under one authoritative owner."""

    recipe_owned = {
        removal
        for recipe in data["recipes"]
        for removal in recipe.get("remove", [])
    }
    for family in data.get("machine_families", []):
        for entry in family.get("recipes", []):
            recipe_owned.update(entry.get("remove", []))
    data["additional_removals"] = [
        removal
        for removal in data.get("additional_removals", [])
        if removal not in recipe_owned
    ]


def main() -> None:
    data = load_seed()
    data["auto_assignments"] = False
    data.setdefault("auto_policy", {})["auto_assignments"] = False
    if data.get("source_recipe_overrides"):
        raise ValueError("source_recipe_overrides must stay empty when automatic stock copying is off")

    # The v2 block is the one-time foundation migration.  Once any v3 card is
    # present, the seed already contains that complete foundation and rerunning
    # its coverage builders would try to reclaim intentionally superseded
    # outputs under obsolete IDs.  V3 itself remains fully rerunnable below.
    v3_migrated = any(
        str(recipe.get("id", "")).startswith("industrial_colonies:v3_")
        for recipe in data.get("recipes", [])
    )
    if not v3_migrated:
        redesign_semiconductor_line(data)
        redesign_processor_lines(data)
        redesign_mekanism_circuits(data)
        redesign_factory_upgrades(data)
        recipe_design_v2_compacting_cleanup.apply(data)
        recipe_design_v2_create_core.apply(data)
        recipe_design_v2_create_addon_coverage.apply(data)
        recipe_design_v2_create_connected_expansion.apply(data)
        recipe_design_v2_specialized_create_gaps.apply(data)
        recipe_design_v2_enchantment_industry_coverage.apply(data)
        recipe_design_v2_createcasing_coverage.apply(data)
        recipe_design_v2_tfmg_core_components.apply(data)
        recipe_design_v2_simulated_coverage.apply(data)
        recipe_design_v2_digital.apply(data)
        recipe_design_v2_ae2_coverage.apply(data)
        recipe_design_v2_computer_network_coverage.apply(data)
        recipe_design_v2_high_energy.apply(data)
        recipe_design_v2_late_grids.apply(data)
        recipe_design_v2_lowheat.apply(data)
        recipe_design_v2_mechanical.apply(data)
        recipe_design_v2_mekanism.apply(data)
        recipe_design_v2_mek_bigreactors_coverage.apply(data)
        recipe_design_v2_big_cannons_coverage.apply(data)
        recipe_design_v2_stock_retirement.apply(data)
        recipe_design_v2_space_coverage.apply(data)
        recipe_design_v2_space_hardware_gaps.apply(data)
        recipe_design_v2_interstellar_component_gap.apply(data)
        recipe_design_v2_tfmg.apply(data)
        recipe_design_v2_metallurgy_functional_gaps.apply(data)
        recipe_design_v2_tfmg_coverage.apply(data)
        recipe_design_v2_tfmg_remaining_hardware.apply(data)
        recipe_design_v2_power_addon_gaps.apply(data)
        recipe_design_v2_tfmg_electrical.apply(data)
        recipe_design_v2_tfmg_component_gaps.apply(data)
        recipe_design_v2_appliedcreate_coverage.apply(data)
        recipe_design_v2_digital_storage_gaps.apply(data)
        recipe_design_v2_shape_refinement.apply(data)
        recipe_design_v2_process_corrections.apply(data)
        recipe_design_v2_mek_components_tools.apply(data)
        recipe_design_v2_mek_induction_refinement.apply(data)
        recipe_design_v2_mekanism_utility_gaps.apply(data)
        recipe_design_v2_electroenergetics_functional_gaps.apply(data)
        recipe_design_v2_tfmg_duplicate_canonicalization.apply(data)
        recipe_design_v2_dependency_order_cleanup.apply(data)
    # Design-v3 intentionally changes several manufacturing environments and
    # therefore runs after the legacy same-phase order fixer.  Each v3 module
    # carries explicit reviewed ordering, then receives one final TFMG-first
    # ingredient canonicalization pass.
    recipe_design_v3_createcasing_progression.apply(data)
    recipe_design_v3_ae2_mega.apply(data)
    recipe_design_v3_storage_cells.apply(data)
    recipe_design_v3_mekanism.apply(data)
    recipe_design_v3_user_references.apply(data)
    recipe_design_v3_computercraft.apply(data)
    recipe_design_v3_structural_compacting.apply(data)
    recipe_design_v3_progression_bootstrap.apply(data)
    recipe_design_v4_rejected_redesigns.apply(data)
    recipe_design_v4_electronics_primitives.apply(data)
    recipe_design_v4_machine_family_corrections.apply(data)
    recipe_design_v4_digital_machine_corrections.apply(data)
    recipe_design_v4_ae2_electronics_depth.apply(data)
    recipe_design_v4_stress_storage_depth.apply(data)
    recipe_design_v4_mega_storage_depth.apply(data)
    recipe_design_v4_space_electronics.apply(data)
    recipe_design_v4_space_hardware_depth.apply(data)
    recipe_design_v4_bigreactors_rejected.apply(data)
    recipe_design_v4_ae2_remaining_depth.apply(data)
    recipe_design_v4_manufacturing_rejects.apply(data)
    recipe_design_v4_manual_rejections.apply(data)
    recipe_design_v5_pumpjack_manufacturing.apply(data)
    recipe_design_v5_digital_transmission.apply(data)
    recipe_design_v5_nuclear_hardware.apply(data)
    recipe_design_v6_review_20260904.apply(data)
    recipe_design_v6_review_20260904.audit(data)
    recipe_design_v2_tfmg_duplicate_canonicalization.apply(data)
    recipe_design_v3_phase_alignment.apply(data)
    # Canonicalization intentionally recreates a few stock-compatibility cards;
    # reapply the final player-review decision so "restore default" wins.
    recipe_design_v6_review_20260904.apply(data)
    recipe_design_v6_review_20260904.audit(data)
    retire_automatic_dependencies(data)
    retire_managed_output_exclusions(data)
    retire_owned_additional_removals(data)

    recipe_design_v7_review_20260904.apply(data)

    SEED_PATH.write_text(
        # Canonical key ordering keeps generated output byte-stable even when
        # a recipe module builds an equivalent nested grid map from a set.
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
