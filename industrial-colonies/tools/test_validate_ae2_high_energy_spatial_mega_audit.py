#!/usr/bin/env python3
"""Mutation tests for validate_ae2_high_energy_spatial_mega_audit.py."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_ae2_high_energy_spatial_mega_audit as builder
import validate_ae2_high_energy_spatial_mega_audit as validator


class Ae2HighEnergySpatialMegaAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.DEFAULT_PLAN)
        cls.patch = validator.load_json(validator.DEFAULT_PATCH)
        cls.seed = validator.load_json(builder.SEED)
        cls.assignments = validator.load_json(builder.ASSIGNMENTS)
        cls.current = validator.load_json(builder.CURRENT_MANAGED)
        cls.predecessor = validator.load_json(builder.DIGITAL_PREDECESSOR)

    def failures(
        self,
        *,
        plan=None,
        patch=None,
        seed=None,
        assignments=None,
        current=None,
        predecessor=None,
    ) -> list[str]:
        return validator.validate_plan(
            self.plan if plan is None else plan,
            self.patch if patch is None else patch,
            validator.DEFAULT_CATALOG,
            validator.DEFAULT_MODS,
            self.seed if seed is None else seed,
            self.assignments if assignments is None else assignments,
            self.current if current is None else current,
            self.predecessor if predecessor is None else predecessor,
        )

    def contract(self, plan: dict, output: str) -> dict:
        return next(
            recipe
            for recipe in plan["replacement_contracts"]
            if builder.output_id(recipe) == output
        )

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

    def test_04_direct_producer_audit_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["direct_producer_audit"]["ae2:controller"].append("other:controller")
        self.assert_failure(self.failures(plan=plan), "direct producer coverage drifted")

    def test_05_exact_removal_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:controller")["remove"] = []
        self.assert_failure(self.failures(plan=plan), "exact source removal list drifted")

    def test_06_preserve_id_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["preserved_bulk_recipes"].pop()
        self.assert_failure(self.failures(plan=plan), "exact eleven bulk")

    def test_07_preserve_role_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["preserved_bulk_recipes"][0]["preservation_role"] = "mega_unit_closure"
        self.assert_failure(self.failures(plan=plan), "bulk preservation role drifted")

    def test_08_non_recipe_external_bypass_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["non_recipe_acquisition_audit"]["occurrences"][0]["role"] = (
            "external_acquisition_candidate"
        )
        self.assert_failure(self.failures(plan=plan), "non-recipe target occurrence evidence drifted")

    def test_09_unknown_ingredient_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:cell_workbench")["inputs"][0] = "missing:imaginary_terminal"
        self.assert_failure(self.failures(plan=plan), "unknown catalog ingredient item")

    def test_10_counted_tag_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:cell_workbench")["inputs"][2] = "2x #c:chests/wooden"
        self.assert_failure(self.failures(plan=plan), "counted tag syntax is forbidden")

    def test_11_non_tfmg_recipe_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "ae2:export_bus")
        for step in contract["steps"]:
            if step.get("ingredient", "").startswith("tfmg:"):
                step["ingredient"] = "ae2:fluix_crystal"
        self.assert_failure(self.failures(plan=plan), "recipe is not TFMG-first")

    def test_12_generic_mekanism_gate_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:controller")["steps"][0]["ingredient"] = (
            "mekanism:advanced_control_circuit"
        )
        self.assert_failure(self.failures(plan=plan), "forbidden generic Mekanism gate")

    def test_13_wrong_copper_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:export_bus")["steps"][0]["machine"] = (
            "createcasing:brass_deployer"
        )
        self.assert_failure(self.failures(plan=plan), "unapproved copper sequence environment")

    def test_14_wrong_brass_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:cell_workbench")["machine"] = (
            "createcasing:copper_press"
        )
        self.assert_failure(self.failures(plan=plan), "unapproved brass compacting environment")

    def test_15_wrong_industrial_iron_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:spatial_anchor")["machine"] = (
            "createcasing:brass_press"
        )
        self.assert_failure(
            self.failures(plan=plan), "unapproved industrial_iron compacting environment"
        )

    def test_16_generic_gate_pattern_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "megacells:mega_crafting_unit")
        contract["pattern"] = ["ABABA", "BCD B", "A   A", "B   B", "ABABA"]
        contract["key"] = {"A": "tfmg:circuit_board", "B": "ae2:engineering_processor"}
        self.assert_failure(self.failures(plan=plan), "generic shaped/gate-ring manufacturing")

    def test_17_excessive_sequence_loops_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:controller")["loops"] = 3
        self.assert_failure(self.failures(plan=plan), "must use exactly one loop")

    def test_18_transitional_carrier_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:io_port")["transitional"] = "ae2:quartz_glass"
        self.assert_failure(self.failures(plan=plan), "transitional carrier")

    def test_19_pylon_batch_size_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:spatial_pylon")["output"] = "ae2:spatial_pylon"
        self.assert_failure(self.failures(plan=plan), "four-segment factory batch")

    def test_20_spatial_control_dependency_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:spatial_pylon")["depends_on"].remove(
            "industrial_colonies:ae2_high_energy/controller"
        )
        self.assert_failure(self.failures(plan=plan), "predecessor dependency is incomplete")

    def test_21_pylon_physically_requires_p2p(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "ae2:spatial_pylon")
        contract["inputs"] = [
            "ae2:quartz_fiber" if value == "ae2:me_p2p_tunnel" else value
            for value in contract["inputs"]
        ]
        self.assert_failure(self.failures(plan=plan), "physical prerequisite chain is missing")

    def test_22_spatial_io_physically_requires_controller(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "ae2:spatial_io_port")
        for step in contract["steps"]:
            if step.get("ingredient") == "ae2:controller":
                step["ingredient"] = "ae2:smooth_sky_stone_block"
        self.assert_failure(self.failures(plan=plan), "physical prerequisite chain is missing")

    def test_23_anchor_physically_requires_spatial_port(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "ae2:spatial_anchor")
        contract["inputs"][0] = "ae2:io_port"
        self.assert_failure(self.failures(plan=plan), "physical prerequisite chain is missing")

    def test_24_mega_core_requires_accumulation_processor(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "megacells:mega_crafting_unit")
        for step in contract["steps"]:
            if step.get("ingredient") == "megacells:accumulation_processor":
                step["ingredient"] = "ae2:logic_processor"
        self.assert_failure(self.failures(plan=plan), "physical prerequisite chain is missing")

    def test_25_same_batch_cycle_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "ae2:controller")["depends_on"].append(
            "industrial_colonies:ae2_high_energy/spatial_io_port"
        )
        self.assert_failure(self.failures(plan=plan), "same-batch dependency cycle")

    def test_26_plan_assignment_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["assignment_contract"][0]["required_node"] = "CR01 — ME System Advanced"
        self.assert_failure(self.failures(plan=plan), "exact no-edit assignment/phase contract drifted")

    def test_27_live_assignment_duplicate_is_rejected(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"]["CR01 — ME System Advanced"]["unlocks"].append(
            "ae2:cell_workbench"
        )
        self.assert_failure(self.failures(assignments=assignments), "current assignment is not exact and unique")

    def test_28_assignment_phase_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["phase_by_node"]["CR01 — ME System Advanced"] = "Nuclear Engineering"
        self.assert_failure(self.failures(seed=seed), "assigned node no longer maps")

    def test_29_current_automatic_owner_drift_is_rejected(self) -> None:
        current = copy.deepcopy(self.current)
        recipe = next(
            row for row in current["recipes"] if builder.output_id(row) == "ae2:controller"
        )
        recipe["id"] = "industrial_colonies:auto/ae2/not_controller"
        self.assert_failure(self.failures(current=current), "current automatic owner identity drifted")

    def test_30_patch_recipe_parity_is_enforced(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["seed_operations"][0]["recipes"][0]["machine"] = "create:mechanical_press"
        self.assert_failure(self.failures(patch=patch), "patch recipe payload differs")

    def test_31_patch_preserve_union_is_enforced(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["seed_operations"][1]["recipe_ids"].pop()
        self.assert_failure(self.failures(patch=patch), "stock preservation union drifted")

    def test_32_authoritative_seed_owner_is_enforced(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if builder.output_id(recipe) != "ae2:cell_workbench"
        ]
        self.assert_failure(self.failures(seed=seed), "authoritative seed must own the output")

    def test_33_prerequisite_owner_evidence_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["prerequisite_evidence"][0]["observed_managed_owner"] = (
            "industrial_colonies:wrong/terminal"
        )
        self.assert_failure(self.failures(plan=plan), "prerequisite owner/phase evidence drifted")

    def test_34_missing_predecessor_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if builder.output_id(recipe) != "ae2:terminal"
        ]
        predecessor = copy.deepcopy(self.predecessor)
        predecessor["replacement_contracts"] = [
            recipe
            for recipe in predecessor["replacement_contracts"]
            if builder.output_id(recipe) != "ae2:terminal"
        ]
        self.assert_failure(
            self.failures(seed=seed, predecessor=predecessor),
            "required predecessor managed owner is absent",
        )

    def test_35_reverse_dependency_into_first_network_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["dependency_contract"]["digital_predecessor_reverse_dependencies"][0][
            "batch_inputs_consumed"
        ] = ["ae2:controller"]
        self.assert_failure(self.failures(plan=plan), "first ME predecessor was made dependent")

    def test_36_applied_seed_boundary_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["integration_boundary"]["seed_edit_applied"] = False
        self.assert_failure(self.failures(plan=plan), "lost the applied seed edit")


if __name__ == "__main__":
    unittest.main()
