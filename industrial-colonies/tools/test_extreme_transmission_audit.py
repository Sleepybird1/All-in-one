#!/usr/bin/env python3
"""Mutation tests for the Extreme Transmission audit and clean-boundary evidence."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_managed_recipe_manifest as builder  # noqa: E402
from validate_extreme_transmission_audit import (  # noqa: E402
    DEFAULT_CATALOG,
    DEFAULT_PLAN,
    DEFAULT_SEED,
    default_mods,
    validate,
)


class ExtremeTransmissionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads(DEFAULT_PLAN.read_text(encoding="utf-8-sig"))
        cls.seed = json.loads(DEFAULT_SEED.read_text(encoding="utf-8-sig"))
        cls.mods = default_mods()
        cls.manifest, report = builder.build_manifest(
            builder.DEFAULT_SEED,
            builder.DEFAULT_ASSIGNMENTS,
            builder.DEFAULT_DEPENDENCIES,
            builder.default_catalog(),
            cls.mods,
        )
        if report.get("fatal_errors"):
            raise AssertionError(report["fatal_errors"])

    def check(self, plan=None, manifest=None, seed=None):
        return validate(
            self.plan if plan is None else plan,
            DEFAULT_CATALOG,
            self.manifest if manifest is None else manifest,
            self.mods,
            self.seed if seed is None else seed,
        )

    @staticmethod
    def recipe(plan, identity: str):
        for recipe in plan["replacement_contracts"]:
            if recipe.get("id") == identity:
                return recipe
        raise AssertionError(f"missing recipe {identity}")

    def test_current_implementation_is_consistent(self) -> None:
        self.assertEqual([], self.check())

    def test_audit_status_is_locked_to_implemented(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "review_only"
        errors = self.check(plan=plan)
        self.assertTrue(any("status must be implemented_in_seed" in error for error in errors), errors)

    def test_seed_contract_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        for recipe in seed["recipes"]:
            if recipe.get("id") == "industrial_colonies:extreme_grid/ground_rod":
                recipe["machine"] = "createcasing:brass_press"
                break
        else:
            self.fail("authoritative seed is missing the Extreme ground-rod recipe")
        errors = self.check(seed=seed)
        self.assertTrue(any("authoritative seed differs" in error for error in errors), errors)

    def test_missing_seed_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe for recipe in seed["recipes"]
            if recipe.get("id") != "industrial_colonies:extreme_grid/hanging_glass_insulator"
        ]
        errors = self.check(seed=seed)
        self.assertTrue(any("absent from authoritative seed" in error for error in errors), errors)

    def test_retired_legacy_seed_owner_cannot_return(self) -> None:
        seed = copy.deepcopy(self.seed)
        legacy = copy.deepcopy(
            next(
                recipe for recipe in seed["recipes"]
                if recipe.get("id") == "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker"
            )
        )
        legacy["id"] = "industrial_colonies:grid/sulfur_hexafluoride_breaker"
        seed["recipes"].append(legacy)
        errors = self.check(seed=seed)
        self.assertTrue(any("retired legacy Extreme owner" in error for error in errors), errors)

    def test_seed_implementation_metadata_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["seed_implementation"]["recipe_count"] = 7
        errors = self.check(plan=plan)
        self.assertTrue(any("must record eight recipes" in error for error in errors), errors)

    def test_current_transformer_predecessor_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        identity = "industrial_colonies:high_voltage/current_transformer"
        plan["predecessor_recipe_ids"].remove(identity)
        plan["implementation_assessment"]["cleared_predecessors"] = [
            entry for entry in plan["implementation_assessment"]["cleared_predecessors"]
            if entry.get("recipe_id") != identity
        ]
        errors = self.check(plan=plan)
        self.assertTrue(any("seven ordered repaired predecessors" in error for error in errors), errors)

    def test_counted_tag_is_rejected_by_kjsgen_contract(self) -> None:
        plan = copy.deepcopy(self.plan)
        recipe = self.recipe(plan, "industrial_colonies:extreme_grid/glass_insulator_segment")
        recipe["inputs"] = ["4x #c:glass_blocks", "#c:wires/iron", "#c:wires/iron", "tfmg:screw"]
        errors = self.check(plan=plan)
        self.assertTrue(any("counted tags are unsupported" in error for error in errors), errors)

    def test_mekanism_dependent_machine_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, "industrial_colonies:extreme_grid/ground_rod")["machine"] = (
            "createcasing:industrial_iron_press"
        )
        errors = self.check(plan=plan)
        self.assertTrue(any("analog boundary" in error for error in errors), errors)

    def test_stock_output_count_evidence_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["source_recipe_contracts"][0]["output_count"] = 1
        errors = self.check(plan=plan)
        self.assertTrue(any("output count" in error for error in errors), errors)

    def test_replacement_output_count_must_match_stock(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, "industrial_colonies:extreme_grid/heavily_insulated_wire")["output"] = (
            "8x electroenergetics:heavily_insulated_wire"
        )
        errors = self.check(plan=plan)
        self.assertTrue(any("output count" in error for error in errors), errors)

    def test_mechanical_pattern_must_be_five_by_five(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, "industrial_colonies:extreme_grid/high_voltage_switch")["pattern"][0] = "III"
        errors = self.check(plan=plan)
        self.assertTrue(any("not exactly 5x5" in error for error in errors), errors)

    def test_dependency_must_precede_consumer_order(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, "industrial_colonies:extreme_grid/heavily_insulated_wire_spool")[
            "batch_order"
        ] = 5
        errors = self.check(plan=plan)
        self.assertTrue(any("not earlier in batch order" in error for error in errors), errors)

    def test_semantic_transformer_core_cannot_disappear(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, "industrial_colonies:extreme_grid/high_voltage_capacitor")["key"]["T"] = (
            "tfmg:steel_mechanism"
        )
        errors = self.check(plan=plan)
        self.assertTrue(any("missing semantic manufacturing inputs" in error for error in errors), errors)

    def test_direct_mekanism_input_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, "industrial_colonies:extreme_grid/ground_rod")["inputs"][-1] = (
            "mekanism:alloy_reinforced"
        )
        errors = self.check(plan=plan)
        self.assertTrue(any("analog boundary" in error for error in errors), errors)

    def test_stale_boundary_evidence_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["implementation_assessment"]["cleared_predecessors"][0][
            "boundary_violations"
        ] = ["ae2:calculation_processor"]
        errors = self.check(plan=plan)
        self.assertTrue(any("boundary evidence is stale" in error for error in errors), errors)

    def test_every_repaired_predecessor_must_reach_final_breaker(self) -> None:
        plan = copy.deepcopy(self.plan)
        manifest = copy.deepcopy(self.manifest)
        self.recipe(plan, "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker")["key"][
            "T"
        ] = "tfmg:transformer"
        for recipe in manifest["recipes"]:
            if recipe.get("id") == "industrial_colonies:high_voltage/voltage_regulator":
                recipe["inputs"] = [
                    "tfmg:transformer" if value == "electroenergetics:transformer" else value
                    for value in recipe["inputs"]
                ]
                break
        errors = self.check(plan=plan, manifest=manifest)
        self.assertTrue(any("not on the final breaker dependency graph" in error for error in errors), errors)

    def test_glass_insulator_spool_preserve_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["preserve_stock_recipe_ids"] = []
        errors = self.check(plan=plan)
        self.assertTrue(any("sole explicit stock preserve" in error for error in errors), errors)

    def test_go_is_revoked_if_a_predecessor_regresses(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        for recipe in manifest["recipes"]:
            if recipe.get("id") == "industrial_colonies:high_voltage/insulated_wire":
                recipe.setdefault("inputs", []).append("mekanism:advanced_control_circuit")
                break
        else:
            self.fail("fresh manifest is missing repaired insulated-wire recipe")
        errors = self.check(manifest=manifest)
        self.assertTrue(any("boundary evidence is stale" in error for error in errors), errors)

    def test_unsupported_recipe_type_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, "industrial_colonies:extreme_grid/ground_rod")["type"] = "pressing"
        errors = self.check(plan=plan)
        self.assertTrue(any("unsupported recipe type" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
