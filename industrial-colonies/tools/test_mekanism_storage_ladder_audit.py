#!/usr/bin/env python3
"""Focused mutation tests for the implemented Mekanism Energy Cube ladder."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_managed_recipe_manifest as builder  # noqa: E402
import validate_mekanism_storage_ladder_audit as validator  # noqa: E402


class MekanismStorageLadderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_object(validator.DEFAULT_PLAN)
        cls.seed = validator.load_object(validator.DEFAULT_SEED)
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

    def check(self, *, plan=None, seed=None, manifest=None):
        return validator.validate(
            self.plan if plan is None else plan,
            validator.DEFAULT_CATALOG,
            self.mods,
            self.seed if seed is None else seed,
            self.manifest if manifest is None else manifest,
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
        duplicate = copy.deepcopy(validator.recipes_by_id(seed)[validator.EXPECTED[2][1]])
        duplicate["id"] = "industrial_colonies:test/duplicate_elite_cube"
        seed["recipes"].append(duplicate)
        self.assertTrue(any("does not have one seed owner" in error for error in self.check(seed=seed)))

    def test_automatic_manifest_owner_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        duplicate = copy.deepcopy(validator.recipes_by_id(manifest)[validator.EXPECTED[0][1]])
        duplicate["id"] = "industrial_colonies:auto/mekanism/basic_energy_cube"
        manifest["recipes"].append(duplicate)
        self.assertTrue(any("automatic Energy Cube owner survived" in error for error in self.check(manifest=manifest)))

    def test_exact_stock_removal_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, validator.EXPECTED[0][1])["remove_exact"] = ["mekanism:energy_cube/advanced"]
        self.assertTrue(any("exact stock removal changed" in error for error in self.check(plan=plan)))

    def test_ultimate_requires_two_elite_cubes(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, validator.EXPECTED[3][1])["pattern"][2] = "EAHBE"
        self.assertTrue(any("requires exactly 2x mekanism:elite_energy_cube" in error for error in self.check(plan=plan)))

    def test_ultimate_requires_extreme_breaker(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, validator.EXPECTED[3][1])["key"]["H"] = "tfmg:heavy_machinery_casing"
        errors = self.check(plan=plan)
        self.assertTrue(any("missing hard tier requirements" in error for error in errors), errors)

    def test_component_transfer_warning_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["component_transfer_policy"]["policy"] = "preserved"
        self.assertTrue(any("component-transfer policy" in error for error in self.check(plan=plan)))

    def test_mechanical_grid_shape_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.recipe(plan, validator.EXPECTED[2][1])["pattern"][0] = "AOE"
        self.assertTrue(any("pattern is not exactly 5x5" in error for error in self.check(plan=plan)))


if __name__ == "__main__":
    unittest.main()
