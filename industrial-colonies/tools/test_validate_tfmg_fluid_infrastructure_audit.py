#!/usr/bin/env python3
"""Mutation tests for validate_tfmg_fluid_infrastructure_audit.py."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_managed_recipe_manifest as builder
import validate_tfmg_fluid_infrastructure_audit as validator


class TFMGFluidInfrastructureAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.DEFAULT_PLAN)
        cls.seed = validator.load_json(validator.SEED)
        cls.assignments = validator.load_json(validator.ASSIGNMENTS)
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

    def contract(self, plan: dict, suffix: str) -> dict:
        return next(
            value for value in plan["replacement_contracts"] if value["id"].endswith(suffix)
        )

    def test_01_current_implementation_passes(self) -> None:
        self.assertEqual([], self.failures(copy.deepcopy(self.plan)))

    def test_02_installed_source_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["source_recipes"][0]["sha256"] = "0" * 64
        self.assertTrue(any("installed source JSON hash changed" in row for row in self.failures(plan)))

    def test_03_functional_classification_overlap_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["classification"]["retained_stock_outputs"].append("tfmg:cast_iron_pipe")
        self.assertTrue(any("classification overlaps" in row for row in self.failures(plan)))

    def test_04_retained_stock_removal_leak_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "/cast_iron_pipe")
        contract["remove_exact"][0] = "tfmg:crafting/materials/brass_pipe"
        self.assertTrue(any("retained stock recipes leaked" in row for row in self.failures(plan)))

    def test_05_stock_batch_output_nerf_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/industrial_pipe")["output"] = "tfmg:industrial_pipe"
        self.assertTrue(any("stock batch output count is not preserved" in row for row in self.failures(plan)))

    def test_06_counted_tag_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/cast_iron_pipe")["inputs"][0] = "2x #c:plates/cast_iron"
        self.assertTrue(any("counted tag syntax is forbidden" in row for row in self.failures(plan)))

    def test_07_unapproved_machine_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/steel_pipe")["machine"] = "create:mechanical_press"
        self.assertTrue(any("unapproved machine environment" in row for row in self.failures(plan)))

    def test_08_forward_same_batch_dependency_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "/cast_iron_fluid_tank")
        contract["inputs"][-1] = "tfmg:steel_pipe"
        contract["depends_on_batch"] = ["industrial_colonies:fluid_infrastructure/steel_pipe"]
        self.assertTrue(any("same-batch dependency is not earlier" in row for row in self.failures(plan)))

    def test_09_missing_physical_predecessor_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/steel_mechanical_pump")["same_family_predecessor"] = (
            "tfmg:cast_iron_pipe"
        )
        self.assertTrue(any("predecessor is not a physical input" in row for row in self.failures(plan)))

    def test_10_finished_steel_in_presteel_bootstrap_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/cast_iron_mechanical_pump")["inputs"][0] = "tfmg:steel_pipe"
        self.assertTrue(any("presteel contract consumes forbidden material" in row for row in self.failures(plan)))

    def test_11_assignment_addition_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["assignment_contract"]["exact_additions_required"][
            "CR01 — Diesel Processing"
        ][0] = "tfmg:steel_pipe"
        self.assertTrue(any("exact seven assignment additions drifted" in row for row in self.failures(plan)))

    def test_12_current_automatic_owner_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_managed_state"]["replaced_automatic_owners"][0]["output_count"] = 1
        self.assertTrue(any("replaced automatic owner evidence drifted" in row for row in self.failures(plan)))

    def test_13_vat_capability_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["runtime_evidence"]["vat_process_recipes"][0]["allowed_vat_types"] = [
            "tfmg:cast_iron_vat"
        ]
        self.assertTrue(any("installed vat allowed types changed" in row for row in self.failures(plan)))

    def test_14_project_pumpjack_tag_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["runtime_evidence"]["project_industrial_pipe_tag_extension"]["values"] = [
            "tfmg:industrial_pipe"
        ]
        self.assertTrue(any("project industrial-pipe tag extension values changed" in row for row in self.failures(plan)))

    def test_15_compiled_kjsgen_card_type_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["compiled_kjsgen_contract"]["expected_card_type"] = "kjsgen:create_mixing"
        self.assertTrue(any("compiled KJSGen card type drifted" in row for row in self.failures(plan)))

    def test_16_status_must_record_implementation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "review_only"
        self.assertTrue(any("status must be implemented_in_seed" in row for row in self.failures(plan)))

    def test_17_missing_seed_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        identity = "industrial_colonies:fluid_infrastructure/steel_pipe"
        seed["recipes"] = [recipe for recipe in seed["recipes"] if recipe.get("id") != identity]
        self.assertTrue(any("absent from authoritative seed" in row for row in self.failures(seed=seed)))

    def test_18_seed_contract_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        identity = "industrial_colonies:fluid_infrastructure/electric_pump"
        validator.recipes_by_id(seed)[identity]["machine"] = "createcasing:brass_press"
        self.assertTrue(any("authoritative seed differs" in row for row in self.failures(seed=seed)))

    def test_19_replaced_automatic_owner_cannot_survive(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        recipe = copy.deepcopy(validator.recipes_by_id(manifest)[
            "industrial_colonies:fluid_infrastructure/cast_iron_pipe"
        ])
        recipe["id"] = "industrial_colonies:auto/tfmg/cast_iron_pipe"
        manifest["recipes"].append(recipe)
        self.assertTrue(any("replaced automatic owner survived" in row for row in self.failures(manifest=manifest)))

    def test_20_assignment_append_order_is_locked(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"]["CR01 — Chemical Processing"]["unlocks"]
        unlocks[-1], unlocks[-2] = unlocks[-2], unlocks[-1]
        self.assertTrue(any("append reviewed outputs in order" in row for row in self.failures(assignments=assignments)))

    def test_21_post_phase_circuit_cannot_enter_steel_vat(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "/fireproof_chemical_vat")
        contract["inputs"][-2] = "tfmg:circuit_board"
        contract["depends_on_batch"][-1] = "industrial_colonies:electronics/circuit_board"
        self.assertTrue(any("comes from later phase Electrical Manufacturing" in row for row in self.failures(plan)))


if __name__ == "__main__":
    unittest.main()
