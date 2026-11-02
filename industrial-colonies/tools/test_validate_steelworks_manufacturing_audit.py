#!/usr/bin/env python3
"""Mutation tests for validate_steelworks_manufacturing_audit.py."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_managed_recipe_manifest as builder
import validate_steelworks_manufacturing_audit as validator


class SteelworksManufacturingAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.DEFAULT_PLAN)
        cls.seed = validator.load_json(validator.DEFAULT_SEED)
        cls.assignments = validator.load_json(validator.DEFAULT_ASSIGNMENTS)
        cls.manifest, report = builder.build_manifest(
            builder.DEFAULT_SEED,
            builder.DEFAULT_ASSIGNMENTS,
            builder.DEFAULT_DEPENDENCIES,
            builder.default_catalog(),
            validator.DEFAULT_MODS,
        )
        if report.get("fatal_errors"):
            raise AssertionError(report["fatal_errors"])

    def failures(self, plan=None, seed=None, manifest=None, assignments=None) -> list[str]:
        return validator.validate_plan(
            self.plan if plan is None else plan,
            validator.DEFAULT_CATALOG,
            validator.DEFAULT_MODS,
            self.seed if seed is None else seed,
            self.manifest if manifest is None else manifest,
            self.assignments if assignments is None else assignments,
        )

    def test_current_implementation_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_installed_source_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["source_recipes"][0]["sha256"] = "0" * 64
        failures = self.failures(plan)
        self.assertTrue(any("installed source JSON hash changed" in row for row in failures))

    def test_regular_wall_tag_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["runtime_evidence"]["block_tags"][0]["values"] = ["tfmg:blast_furnace_hatch"]
        failures = self.failures(plan)
        self.assertTrue(any("runtime block-tag values changed" in row for row in failures))

    def test_current_automatic_owner_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_managed_owners"][0]["output_count"] = 1
        failures = self.failures(plan)
        self.assertTrue(any("retired automatic output/count evidence drifted" in row for row in failures))

    def test_required_assignment_addition_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["currently_unmanaged_required_outputs"][0]["required_assignment_node"] = (
            "CR01 — The Steel Age"
        )
        failures = self.failures(plan)
        self.assertTrue(any("assignment additions" in row for row in failures))

    def test_finished_steel_in_required_bootstrap_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = next(
            value
            for value in plan["replacement_contracts"]
            if value["id"] == "industrial_colonies:steelworks/blast_furnace_hatch"
        )
        contract["inputs"][0] = "tfmg:heavy_plate"
        failures = self.failures(plan)
        self.assertTrue(any("bootstrap-required contract consumes forbidden steel input" in row for row in failures))

    def test_reinforcement_cannot_become_bootstrap_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = next(
            value
            for value in plan["replacement_contracts"]
            if value["id"] == "industrial_colonies:steelworks/blast_furnace_reinforcement"
        )
        contract["bootstrap_role"] = "required"
        failures = self.failures(plan)
        self.assertTrue(any("bootstrap-required contract consumes forbidden steel input" in row for row in failures))
        self.assertTrue(any("only post-first-steel contract" in row for row in failures))

    def test_reinforcement_cannot_enter_regular_capability(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["capability_dag"]["regular_blast_furnace_operational"]["requires_contracts"].append(
            "industrial_colonies:steelworks/blast_furnace_reinforcement"
        )
        failures = self.failures(plan)
        self.assertTrue(any("leaked into regular furnace bootstrap" in row for row in failures))

    def test_forward_same_batch_dependency_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = next(
            value
            for value in plan["replacement_contracts"]
            if value["id"] == "industrial_colonies:steelworks/fireproof_bricks"
        )
        contract["inputs"][0] = "tfmg:blast_furnace_output"
        contract["depends_on_batch"] = ["industrial_colonies:steelworks/blast_furnace_output"]
        failures = self.failures(plan)
        self.assertTrue(any("same-batch dependency is not earlier" in row for row in failures))

    def test_removal_broadening_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][0]["remove_exact"].append(
            "tfmg:crafting/materials/blast_stove"
        )
        failures = self.failures(plan)
        self.assertTrue(any("must retire exactly its one audited source recipe" in row for row in failures))

    def test_stock_batch_output_nerf_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = next(
            value
            for value in plan["replacement_contracts"]
            if value["id"] == "industrial_colonies:steelworks/coke_oven"
        )
        contract["output"] = "tfmg:coke_oven"
        failures = self.failures(plan)
        self.assertTrue(any("stock batch output count is not preserved" in row for row in failures))

    def test_unapproved_machine_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = next(
            value
            for value in plan["replacement_contracts"]
            if value["id"] == "industrial_colonies:steelworks/blast_furnace_hatch"
        )
        contract["machine"] = "create:mechanical_press"
        failures = self.failures(plan)
        self.assertTrue(any("unapproved machine environment" in row for row in failures))

    def test_non_rectangular_mechanical_layout_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = next(
            value
            for value in plan["replacement_contracts"]
            if value["id"] == "industrial_colonies:steelworks/blast_furnace_output"
        )
        contract["pattern"][0] = "FBPB"
        failures = self.failures(plan)
        self.assertTrue(any("exact 5x5 layout" in row for row in failures))

    def test_status_must_record_implementation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "review_only"
        failures = self.failures(plan=plan)
        self.assertTrue(any("status must be implemented_in_seed" in row for row in failures))

    def test_missing_seed_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe for recipe in seed["recipes"]
            if recipe.get("id") != "industrial_colonies:steelworks/coke_oven"
        ]
        failures = self.failures(seed=seed)
        self.assertTrue(any("absent from authoritative seed" in row for row in failures))

    def test_seed_contract_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = validator.recipes_by_id(seed)["industrial_colonies:steelworks/blast_furnace_output"]
        recipe["pattern"][0] = "FFFFF"
        failures = self.failures(seed=seed)
        self.assertTrue(any("authoritative seed differs" in row for row in failures))

    def test_retired_automatic_manifest_owner_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        duplicate = copy.deepcopy(
            validator.recipes_by_id(self.seed)["industrial_colonies:steelworks/coke_oven"]
        )
        duplicate["id"] = "industrial_colonies:auto/tfmg/coke_oven"
        manifest["recipes"].append(duplicate)
        failures = self.failures(manifest=manifest)
        self.assertTrue(any("retired Steelworks automatic owner survived" in row for row in failures))

    def test_assignment_append_order_is_rejected(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"]["CR01 — Blast Furnace"]["unlocks"]
        unlocks[-1], unlocks[-2] = unlocks[-2], unlocks[-1]
        failures = self.failures(assignments=assignments)
        self.assertTrue(any("append the two structural additions in order" in row for row in failures))


if __name__ == "__main__":
    unittest.main()
