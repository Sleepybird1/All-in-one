#!/usr/bin/env python3
"""Focused mutation tests for the implemented Induction Matrix family."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_managed_recipe_manifest as builder  # noqa: E402
import validate_induction_matrix_completion_audit as validator  # noqa: E402


class InductionMatrixCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_object(validator.DEFAULT_PLAN)
        cls.seed = validator.load_object(validator.DEFAULT_SEED)
        cls.assignments = validator.load_object(validator.DEFAULT_ASSIGNMENTS)
        cls.mods = validator.default_mods()
        cls.manifest, report = builder.build_manifest(
            builder.DEFAULT_SEED,
            builder.DEFAULT_ASSIGNMENTS,
            builder.DEFAULT_DEPENDENCIES,
            builder.default_catalog(),
            cls.mods,
        )
        if report.get("fatal_errors"):
            raise AssertionError(report["fatal_errors"])

    def check(self, *, plan=None, seed=None, manifest=None, assignments=None):
        return validator.validate(
            self.plan if plan is None else plan,
            validator.DEFAULT_CATALOG,
            self.mods,
            self.seed if seed is None else seed,
            self.manifest if manifest is None else manifest,
            self.assignments if assignments is None else assignments,
        )

    @staticmethod
    def recipe(data, identity: str):
        for recipe in data["replacement_contracts"]:
            if recipe.get("id") == identity:
                return recipe
        raise AssertionError(f"missing reviewed recipe {identity}")

    def test_current_implementation_passes(self) -> None:
        self.assertEqual([], self.check())

    def test_status_is_implemented(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "review_only"
        self.assertTrue(any("status must be implemented_in_seed" in error for error in self.check(plan=plan)))

    def test_missing_seed_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe for recipe in seed["recipes"]
            if recipe.get("id") != validator.EXPECTED[0][1]
        ]
        self.assertTrue(any("absent from authoritative seed" in error for error in self.check(seed=seed)))

    def test_seed_field_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        validator.recipes_by_id(seed)[validator.EXPECTED[1][1]]["pattern"][0] = "AAAAA"
        self.assertTrue(any("authoritative seed differs" in error for error in self.check(seed=seed)))

    def test_duplicate_seed_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        duplicate = copy.deepcopy(validator.recipes_by_id(seed)[validator.EXPECTED[6][1]])
        duplicate["id"] = "industrial_colonies:test/duplicate_elite_induction_cell"
        seed["recipes"].append(duplicate)
        self.assertTrue(any("does not have one seed owner" in error for error in self.check(seed=seed)))

    def test_automatic_manifest_owner_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        duplicate = copy.deepcopy(validator.recipes_by_id(manifest)[validator.EXPECTED[0][1]])
        duplicate["id"] = "industrial_colonies:auto/mekanism/induction_casing"
        manifest["recipes"].append(duplicate)
        self.assertTrue(any("automatic Induction owner survived" in error for error in self.check(manifest=manifest)))

    def test_exact_stock_removal_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, validator.EXPECTED[4][1])["remove_exact"] = ["mekanism:induction/cell/basic"]
        self.assertTrue(any("exact stock removal changed" in error for error in self.check(plan=plan)))

    def test_casing_output_count_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, validator.EXPECTED[0][1])["output"] = "4x mekanism:induction_casing"
        self.assertTrue(any("replacement output/count changed" in error for error in self.check(plan=plan)))

    def test_exact_press_binding_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, validator.EXPECTED[8][1])["machine"] = validator.REFINED_PRESS
        self.assertTrue(any("wrong Encased press" in error for error in self.check(plan=plan)))

    def test_dependency_id_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, validator.EXPECTED[9][1])["depends_on_batch"].remove(
            validator.EXTERNAL_OUTPUTS["electroenergetics:voltage_regulator"]
        )
        self.assertTrue(any("dependency set changed" in error for error in self.check(plan=plan)))

    def test_assignment_append_order_is_locked(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"][validator.NODE]["unlocks"]
        left = unlocks.index(validator.EXPECTED_ASSIGNMENTS[-2])
        right = unlocks.index(validator.EXPECTED_ASSIGNMENTS[-1])
        unlocks[left], unlocks[right] = unlocks[right], unlocks[left]
        self.assertTrue(any("preserve the locked Induction segment" in error for error in self.check(assignments=assignments)))

    def test_assignment_existing_prefix_is_locked(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"][validator.NODE]["unlocks"][0] = "mekanism:basic_tier_installer"
        self.assertTrue(any("preserve the locked Induction segment" in error for error in self.check(assignments=assignments)))

    def test_transmitter_later_segment_is_exact(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"][validator.NODE]["unlocks"]
        left = unlocks.index(validator.TRANSMITTER_ASSIGNMENT_SUFFIX[0])
        right = unlocks.index(validator.TRANSMITTER_ASSIGNMENT_SUFFIX[1])
        unlocks[left], unlocks[right] = unlocks[right], unlocks[left]
        self.assertTrue(any("four audited transmitters" in error for error in self.check(assignments=assignments)))

    def test_factory_later_segment_is_exact(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"][validator.NODE]["unlocks"]
        unlocks[-1], unlocks[-2] = unlocks[-2], unlocks[-1]
        self.assertTrue(any("exact Factory additions" in error for error in self.check(assignments=assignments)))


if __name__ == "__main__":
    unittest.main()
