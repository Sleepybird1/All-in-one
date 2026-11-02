#!/usr/bin/env python3
"""Mutation tests for validate_digital_core_peripherals_audit.py."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_digital_core_peripherals_audit as builder
import validate_digital_core_peripherals_audit as validator


class DigitalCorePeripheralsAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.DEFAULT_PLAN)
        cls.patch = validator.load_json(validator.DEFAULT_PATCH)
        cls.seed = validator.load_json(builder.SEED)
        cls.assignments = validator.load_json(builder.ASSIGNMENTS)
        cls.current = validator.load_json(builder.CURRENT_MANAGED)

    def failures(
        self,
        *,
        plan=None,
        patch=None,
        seed=None,
        assignments=None,
        current=None,
        implemented_manifest=False,
    ) -> list[str]:
        return validator.validate_plan(
            self.plan if plan is None else plan,
            self.patch if patch is None else patch,
            validator.DEFAULT_CATALOG,
            validator.DEFAULT_MODS,
            self.seed if seed is None else seed,
            self.assignments if assignments is None else assignments,
            self.current if current is None else current,
            implemented_manifest=implemented_manifest,
        )

    def contract(self, plan: dict, output: str) -> dict:
        return next(recipe for recipe in plan["replacement_contracts"] if recipe["output"] == output)

    def assert_failure(self, failures: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in failure for failure in failures),
            f"expected failure containing {fragment!r}; got {failures}",
        )

    def test_01_current_artifacts_pass(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_builder_is_byte_deterministic(self) -> None:
        plan, patch, markdown = builder.build_documents(
            validator.DEFAULT_CATALOG, validator.DEFAULT_MODS
        )
        self.assertEqual(self.plan, plan)
        self.assertEqual(self.patch, patch)
        self.assertEqual(validator.DEFAULT_MARKDOWN.read_text(encoding="utf-8"), markdown)

    def test_03_installed_source_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["removed_installed_recipes"][0]["source_sha256"] = "0" * 64
        self.assert_failure(self.failures(plan=plan), "installed source JSON hash changed")

    def test_04_exact_removal_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:interface")["remove"].pop()
        self.assert_failure(self.failures(plan=plan), "exact source removal list drifted")

    def test_05_preserved_cell_role_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["preserved_cell_recipes"][0]["preservation_role"] = "cell_closure"
        self.assert_failure(
            self.failures(plan=plan), "exact stock cell closure/recovery preservation set drifted"
        )

    def test_06_unknown_ingredient_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:energy_acceptor")["inputs"][0] = "missing:imaginary_board"
        self.assert_failure(self.failures(plan=plan), "unknown catalog ingredient item")

    def test_07_counted_tag_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "appmek:chemical_cell_housing")["inputs"][4] = (
            "2x #c:ingots/osmium"
        )
        self.assert_failure(self.failures(plan=plan), "counted tag syntax is forbidden")

    def test_08_non_tfmg_recipe_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "ae2:energy_acceptor")
        contract["inputs"] = [
            "ae2:quartz_glass" if value.startswith("tfmg:") else value
            for value in contract["inputs"]
        ]
        self.assert_failure(self.failures(plan=plan), "recipe is not TFMG-first")

    def test_09_mekanism_gate_in_first_me_network_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:energy_acceptor")["inputs"][0] = (
            "mekanism:advanced_control_circuit"
        )
        self.assert_failure(
            self.failures(plan=plan), "first ME network consumes forbidden Mekanism gate"
        )

    def test_10_later_processor_in_first_me_network_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:terminal")["steps"][1]["ingredient"] = (
            "ae2:engineering_processor"
        )
        self.assert_failure(
            self.failures(plan=plan), "first ME network consumes a later processor tier"
        )

    def test_11_wrong_copper_press_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:item_cell_housing")["machine"] = "createcasing:brass_press"
        self.assert_failure(self.failures(plan=plan), "unapproved copper manufacturing environment")

    def test_12_wrong_brass_sequence_machine_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:terminal")["steps"][0]["machine"] = (
            "createcasing:copper_deployer"
        )
        self.assert_failure(self.failures(plan=plan), "unapproved brass sequence environment")

    def test_13_generic_gate_pattern_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "ae2:molecular_assembler")
        contract["pattern"] = ["ABABA", "BCDCB", "ADEDA", "BCDCB", "ABABA"]
        contract["key"] = {"A": "tfmg:circuit_board", "B": "ae2:logic_processor"}
        self.assert_failure(self.failures(plan=plan), "generic shaped/gate-ring manufacturing")

    def test_14_excessive_sequence_loops_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:interface")["loops"] = 4
        self.assert_failure(self.failures(plan=plan), "must use exactly one loop")

    def test_15_peripheral_casing_physical_input_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "advancedperipherals:block_reader")["inputs"][0] = (
            "tfmg:steel_casing"
        )
        self.assert_failure(self.failures(plan=plan), "peripheral casing is not a physical prerequisite")

    def test_16_peripheral_casing_dependency_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "advancedperipherals:energy_detector")["depends_on"] = []
        self.assert_failure(self.failures(plan=plan), "peripheral casing dependency is not explicit")

    def test_17_peripheral_casing_order_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "advancedperipherals:inventory_manager")["order"] = 5
        self.assert_failure(self.failures(plan=plan), "peripheral casing does not precede device order")

    def test_18_me_bridge_requires_physical_interface(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "advancedperipherals:me_bridge")
        contract["inputs"][1] = "ae2:fluix_block"
        self.assert_failure(self.failures(plan=plan), "AE2 interface is not a physical prerequisite")

    def test_19_pattern_provider_requires_interface_dependency(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:pattern_provider")["depends_on"] = []
        self.assert_failure(self.failures(plan=plan), "AE2 interface dependency is not explicit")

    def test_20_same_batch_cycle_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        interface = self.contract(plan, "ae2:interface")
        interface["depends_on"] = ["industrial_colonies:digital_core/pattern_provider"]
        interface["steps"][0]["ingredient"] = "ae2:pattern_provider"
        self.assert_failure(self.failures(plan=plan), "same-batch dependency cycle")

    def test_21_housing_recovery_exclusivity_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:item_cell_housing")["exclusive_output"] = True
        self.assert_failure(self.failures(plan=plan), "must retain stock recovery outputs")

    def test_22_plan_assignment_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["assignment_contract"][0]["required_node"] = "CR01 — Advanced ME Storage"
        self.assert_failure(self.failures(plan=plan), "exact no-edit assignment contract drifted")

    def test_23_live_assignment_duplicate_is_rejected(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"]["CR01 — Advanced ME Storage"]["unlocks"].append(
            "ae2:energy_acceptor"
        )
        self.assert_failure(self.failures(assignments=assignments), "current assignment is not exact and unique")

    def test_24_patch_recipe_parity_is_enforced(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["seed_operations"][0]["recipes"][0]["machine"] = "create:mechanical_press"
        self.assert_failure(self.failures(patch=patch), "patch recipe payload differs")

    def test_25_patch_preserve_union_is_enforced(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["seed_operations"][1]["recipe_ids"].pop()
        self.assert_failure(self.failures(patch=patch), "stock preservation union drifted")

    def test_26_missing_implemented_seed_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if recipe.get("id") != "industrial_colonies:digital_core/energy_acceptor"
        ]
        self.assert_failure(self.failures(seed=seed), "authoritative seed recipe differs")

    def test_27_current_automatic_owner_drift_is_rejected(self) -> None:
        current = copy.deepcopy(self.current)
        recipe = next(
            row for row in current["recipes"] if builder.output_id(row) == "ae2:energy_acceptor"
        )
        recipe["id"] = "industrial_colonies:auto/ae2/not_energy_acceptor"
        self.assert_failure(self.failures(current=current), "current automatic owner identity drifted")

    def test_28_prerequisite_owner_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        entry = next(
            row for row in plan["prerequisite_evidence"] if row["output"] == "ae2:logic_processor"
        )
        entry["managed_owner"] = "industrial_colonies:wrong/logic_processor"
        self.assert_failure(self.failures(plan=plan), "prerequisite owner evidence drifted")

    def test_29_applied_seed_boundary_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["integration_boundary"]["seed_edit_applied"] = False
        self.assert_failure(self.failures(plan=plan), "lost the applied seed edit")

    def test_30_implemented_manifest_passes(self) -> None:
        self.assertEqual(
            [],
            self.failures(current=self.seed, implemented_manifest=True),
        )

    def test_31_seed_preservation_loss_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["preserve_recipe_ids"].remove("ae2:network/cells/item_storage_cell_1k_storage")
        self.assert_failure(
            self.failures(seed=seed), "authoritative seed is missing stock cell preservation IDs"
        )

    def test_32_transformer_owner_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        owner = next(recipe for recipe in seed["recipes"] if recipe.get("output") == "tfmg:transformer")
        owner["id"] = "industrial_colonies:wrong/transformer"
        self.assert_failure(self.failures(seed=seed), "required Heavy/Electrical source owner drifted")

    def test_33_voltage_observer_must_be_physical(self) -> None:
        plan = copy.deepcopy(self.plan)
        detector = self.contract(plan, "advancedperipherals:energy_detector")
        detector["inputs"][1] = "tfmg:copper_wire"
        self.assert_failure(
            self.failures(plan=plan), "required TFMG power dependency is not physical"
        )

    def test_34_implemented_manifest_rejects_automatic_survivor(self) -> None:
        managed = copy.deepcopy(self.seed)
        managed["recipes"].append(
            {
                "id": "industrial_colonies:auto/ae2/energy_acceptor",
                "type": "mechanical_crafting",
                "output": "minecraft:stone",
            }
        )
        self.assert_failure(
            self.failures(current=managed, implemented_manifest=True),
            "isolated rebuild retained automatic owners",
        )

    def test_35_implemented_manifest_rejects_removal_drift(self) -> None:
        managed = copy.deepcopy(self.seed)
        recipe = next(
            row
            for row in managed["recipes"]
            if row.get("id") == "industrial_colonies:digital_core/interface"
        )
        recipe["remove"].pop()
        self.assert_failure(
            self.failures(current=managed, implemented_manifest=True),
            "isolated rebuild removal contract drifted",
        )

    def test_36_rebased_patch_hash_is_enforced(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["base_files"]["progression/managed_recipe_overhaul.seed.json"] = "0" * 64
        self.assert_failure(self.failures(patch=patch), "patch shared-file base hashes drifted")


if __name__ == "__main__":
    unittest.main()
