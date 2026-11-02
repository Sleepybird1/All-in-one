#!/usr/bin/env python3
"""Mutation tests for the source-owned power-backbone contract."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_power_backbone_progression import (  # noqa: E402
    DEFAULT_ASSIGNMENTS,
    DEFAULT_PLAN,
    DEFAULT_SEED,
    validate_contract,
)


class PowerBackboneProgressionTests(unittest.TestCase):
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

    def test_missing_source_recipe_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if recipe.get("id") != "industrial_colonies:early_electricity/generator"
        ]
        errors = self.validate(seed=seed)
        self.assertTrue(any("missing source-owned recipe" in error for error in errors), errors)

    def test_reviewed_output_count_is_locked(self) -> None:
        seed = copy.deepcopy(self.seed)
        self.recipe(seed, "industrial_colonies:grid/empty_spool")["output"] = (
            "8x electroenergetics:empty_spool"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("output is" in error for error in errors), errors)

    def test_exact_stock_removal_is_locked(self) -> None:
        seed = copy.deepcopy(self.seed)
        self.recipe(seed, "industrial_colonies:chemical_processing/accumulator")["remove"] = [
            "tfmg:crafting/materials/accumulator"
        ]
        errors = self.validate(seed=seed)
        self.assertTrue(any("exact reviewed stock removals" in error for error in errors), errors)

    def test_early_generator_rejects_mekanism_gate(self) -> None:
        seed = copy.deepcopy(self.seed)
        self.recipe(seed, "industrial_colonies:early_electricity/generator")["key"]["W"] = (
            "mekanism:advanced_control_circuit"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("later/sibling early-electricity" in error for error in errors), errors)

    def test_grid_rejects_sibling_copper_spool_gate(self) -> None:
        seed = copy.deepcopy(self.seed)
        self.recipe(seed, "industrial_colonies:grid/resistor")["key"]["T"] = "tfmg:copper_spool"
        errors = self.validate(seed=seed)
        self.assertTrue(any("non-ancestor grid ingredients" in error for error in errors), errors)

    def test_connector_reclamation_must_survive(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].append(
            "electroenergetics:crafting/connector_from_double"
        )
        errors = self.validate(seed=seed)
        self.assertTrue(any("safe EE connector reclamation" in error for error in errors), errors)

    def test_duplicate_retirement_must_be_owned_once(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].append("createaddition:crafting/connector")
        errors = self.validate(seed=seed)
        self.assertTrue(any("duplicate retirement" in error for error in errors), errors)

    def test_missing_retirement_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].remove("createaddition:crafting/modular_accumulator")
        errors = self.validate(seed=seed)
        self.assertTrue(any("modular_accumulator" in error for error in errors), errors)

    def test_encased_machine_routing_is_locked(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "industrial_colonies:grid/alternator_brushes")
        recipe["steps"][-1]["machine"] = "create:mechanical_press"
        errors = self.validate(seed=seed)
        self.assertTrue(any("changed reviewed field steps" in error for error in errors), errors)

    def test_source_owned_generator_cannot_remain_excluded(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["exclude_outputs"].append("tfmg:generator")
        errors = self.validate(seed=seed)
        self.assertTrue(any("both source-owned and excluded" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
