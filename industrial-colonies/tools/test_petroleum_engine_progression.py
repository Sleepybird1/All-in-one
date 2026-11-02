#!/usr/bin/env python3
"""Focused mutation tests for the petroleum and engine seed contract."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_petroleum_engine_progression import (
    DEFAULT_ASSIGNMENTS,
    DEFAULT_SEED,
    validate_contract,
)


class PetroleumEngineProgressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = json.loads(DEFAULT_SEED.read_text(encoding="utf-8-sig"))
        cls.assignments = json.loads(DEFAULT_ASSIGNMENTS.read_text(encoding="utf-8-sig"))

    def validate(self, seed=None, assignments=None):
        return validate_contract(
            self.seed if seed is None else seed,
            self.assignments if assignments is None else assignments,
        )

    @staticmethod
    def recipe(seed, output: str):
        for recipe in seed["recipes"]:
            value = recipe.get("output")
            if isinstance(value, str) and (value == output or value.endswith(f"x {output}")):
                return recipe
            if isinstance(value, dict) and value.get("id") == output:
                return recipe
        raise AssertionError(f"missing recipe for {output}")

    def test_current_source_contract_passes(self) -> None:
        self.assertEqual([], self.validate())

    def test_first_diesel_rejects_digital_shortcut(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "createdieselgenerators:diesel_engine")
        recipe["key"]["C"] = "ae2:engineering_processor"
        errors = self.validate(seed=seed)
        self.assertTrue(any("digital prerequisites" in error for error in errors), errors)

    def test_oil_field_rejects_blast_furnace_material(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "tfmg:surface_scanner")
        recipe["key"]["F"] = "tfmg:steel_frame"
        errors = self.validate(seed=seed)
        self.assertTrue(any("parallel Blast Furnace" in error for error in errors), errors)

    def test_generic_auto_ring_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "tfmg:pumpjack_base")
        recipe["pattern"][0] = "ABABA"
        recipe["pattern"][-1] = "ABABA"
        errors = self.validate(seed=seed)
        self.assertTrue(any("generic ABABA" in error for error in errors), errors)

    def test_stock_removal_must_remain_exact(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "tfmg:steel_distillation_controller")
        recipe["remove"] = ["tfmg:crafting/materials/steel_distillation_output"]
        errors = self.validate(seed=seed)
        self.assertTrue(any("does not remove exactly" in error for error in errors), errors)

    def test_existing_engine_controller_is_preserved(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "tfmg:engine_controller")
        recipe["pattern"][0] = "RRRRR"
        errors = self.validate(seed=seed)
        self.assertTrue(any("engine_controller changed field pattern" in error for error in errors), errors)

    def test_large_diesel_retains_tfmg_large_engine_core(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "createdieselgenerators:large_diesel_engine")
        recipe["key"]["L"] = "minecraft:iron_block"
        errors = self.validate(seed=seed)
        self.assertTrue(any("large_diesel_engine ingredient contract" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
