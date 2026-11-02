#!/usr/bin/env python3
"""Mutation tests for the primitive-to-Brass manufacturing contract."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_early_manufacturing_progression import (  # noqa: E402
    DEFAULT_ASSIGNMENTS,
    DEFAULT_PLAN,
    DEFAULT_SEED,
    validate_contract,
)


class EarlyManufacturingProgressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = json.loads(DEFAULT_SEED.read_text(encoding="utf-8-sig"))
        cls.plan = json.loads(DEFAULT_PLAN.read_text(encoding="utf-8-sig"))
        cls.assignments = json.loads(DEFAULT_ASSIGNMENTS.read_text(encoding="utf-8-sig"))

    def validate(self, seed=None, plan=None, manifest=None):
        return validate_contract(
            self.seed if seed is None else seed,
            self.plan if plan is None else plan,
            self.assignments,
            manifest,
        )

    @staticmethod
    def recipe(seed, identity: str):
        for recipe in seed["recipes"]:
            if recipe.get("id") == identity:
                return recipe
        raise AssertionError(f"missing recipe {identity}")

    def test_current_source_contract_passes(self) -> None:
        self.assertEqual([], self.validate())

    def test_missing_reviewed_recipe_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if recipe.get("id") != "industrial_colonies:mechanical/mechanical_pump"
        ]
        errors = self.validate(seed=seed)
        self.assertTrue(any("missing reviewed early recipe" in error for error in errors), errors)

    def test_press_cannot_require_a_sheet(self) -> None:
        seed = copy.deepcopy(self.seed)
        self.recipe(seed, "industrial_colonies:mechanical/mechanical_press")["key"]["I"] = (
            "create:iron_sheet"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("circularly requires a sheet" in error for error in errors), errors)

    def test_exact_stock_removal_is_locked(self) -> None:
        seed = copy.deepcopy(self.seed)
        self.recipe(seed, "industrial_colonies:steam/steam_engine")["remove"] = []
        errors = self.validate(seed=seed)
        self.assertTrue(any("changed its exact stock removal" in error for error in errors), errors)

    def test_missing_hammering_retirement_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].remove(
            "createdieselgenerators:hammering/copper_sheet"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("copper_sheet" in error for error in errors), errors)

    def test_duplicate_hammering_retirement_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].append(
            "createdieselgenerators:hammering/brass_sheet"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("brass_sheet" in error for error in errors), errors)

    def test_required_preserve_cannot_be_removed(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["preserve_recipe_ids"].remove("create:crafting/appliances/schedule_clear")
        errors = self.validate(seed=seed)
        self.assertTrue(any("preserves are missing" in error for error in errors), errors)

    def test_preserve_and_removal_conflict_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].append("create:deploying/cogwheel")
        errors = self.validate(seed=seed)
        self.assertTrue(any("also removed" in error for error in errors), errors)

    def test_stock_foundation_cannot_return_to_auto_ownership(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["exclude_outputs"].remove("create:shaft")
        errors = self.validate(seed=seed)
        self.assertTrue(any("eligible for auto ownership" in error for error in errors), errors)

    def test_brass_capability_node_cannot_revert_to_mechanical_phase(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["phase_by_node"]["CR01 — Advanced Mechanical Technology"] = (
            "Mechanical Foundations"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("Advanced Mechanical Technology" in error for error in errors), errors)

    def test_native_deployer_cannot_require_precision_mechanism(self) -> None:
        seed = copy.deepcopy(self.seed)
        self.recipe(seed, "industrial_colonies:brass/deployer")["key"]["B"] = (
            "create:precision_mechanism"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("circularly requires a Precision Mechanism" in error for error in errors), errors)

    def test_existing_encased_upgrade_is_locked(self) -> None:
        seed = copy.deepcopy(self.seed)
        self.recipe(seed, "industrial_colonies:manufacturing/copper_press")["pattern"][0] = (
            "CMC"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("existing Encased upgrade changed" in error for error in errors), errors)

    def test_isolated_manifest_must_carry_preserve_policy(self) -> None:
        manifest = copy.deepcopy(self.seed)
        manifest["preserve_recipe_ids"] = []
        errors = self.validate(manifest=manifest)
        self.assertTrue(any("does not carry" in error for error in errors), errors)

    def test_isolated_manifest_cannot_remove_schedule_clear(self) -> None:
        manifest = copy.deepcopy(self.seed)
        manifest["additional_removals"].append("create:crafting/appliances/schedule_clear")
        errors = self.validate(manifest=manifest)
        self.assertTrue(any("isolated manifest removes preserved" in error for error in errors), errors)

    def test_daylight_routes_must_survive(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].append("minecraft:daylight_detector")
        errors = self.validate(seed=seed)
        self.assertTrue(any("Daylight Detector" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
