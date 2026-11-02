#!/usr/bin/env python3
"""Mutation tests for the five processing-component progression closures."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_processing_component_hardening as validator


class ProcessingComponentHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = validator.load_object(validator.DEFAULT_SEED)

    @staticmethod
    def recipe(seed, output: str):
        recipes = validator.recipes_for_output(seed, output)
        if len(recipes) != 1:
            raise AssertionError(f"expected one recipe for {output}, got {len(recipes)}")
        return recipes[0]

    def validate(self, seed=None) -> list[str]:
        return validator.validate_source_contract(self.seed if seed is None else seed)

    def test_current_source_contract_passes(self) -> None:
        self.assertEqual([], self.validate())

    def test_empty_spool_cannot_fall_back_to_generic_cutting(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "tfmg:empty_spool")
        recipe["machine"] = "create:mechanical_saw"
        recipe["remove"] = []
        errors = self.validate(seed)
        self.assertTrue(any("copper_mechanical_saw" in error for error in errors), errors)
        self.assertTrue(any("removal set" in error for error in errors), errors)

    def test_accumulation_processor_requires_tfmg_board_and_exact_stock_closure(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "megacells:accumulation_processor")
        recipe["steps"][0]["ingredient"] = "minecraft:redstone"
        recipe["remove"] = ["megacells:inscriber/accumulation_processor"]
        errors = self.validate(seed)
        self.assertTrue(any("sequence operations" in error for error in errors), errors)
        self.assertTrue(any("extendedae:assembler/accumulation_processor" in error for error in errors), errors)

    def test_accumulation_processor_cannot_invent_an_open_transitional(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "megacells:accumulation_processor")
        recipe["transitional"] = "industrial_colonies:unfinished_accumulation_processor"
        errors = self.validate(seed)
        self.assertTrue(any("custom transitional" in error for error in errors), errors)

    def test_transformer_lamination_must_be_steel_and_railway_pressed(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "electroenergetics:transformer_core_lamination")
        recipe["input"] = "#c:plates/iron"
        recipe["machine"] = "create:mechanical_press"
        errors = self.validate(seed)
        self.assertTrue(any("#c:plates/steel" in error for error in errors), errors)
        self.assertTrue(any("railway_press" in error for error in errors), errors)

    def test_transformer_core_keeps_four_laminations_and_two_windings(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "electroenergetics:transformer_core")
        recipe["steps"].pop(1)
        recipe["steps"][3]["ingredient"] = "electroenergetics:wire_spool"
        errors = self.validate(seed)
        self.assertTrue(any("sequence operations" in error for error in errors), errors)

    def test_breaker_cannot_drop_analog_protection_or_brass_press(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = self.recipe(seed, "electroenergetics:miniature_circuit_breaker")
        recipe["steps"][2]["ingredient"] = "minecraft:redstone"
        recipe["steps"][-1]["machine"] = "createcasing:copper_press"
        errors = self.validate(seed)
        self.assertTrue(any("sequence operations" in error for error in errors), errors)

    def test_catalog_alternative_stock_producer_fails_closed(self) -> None:
        producers = {
            output: set(contract["remove"])
            for output, contract in validator.CONTRACTS.items()
        }
        producers["tfmg:empty_spool"].add("example:cheap_empty_spool")
        items = validator.expected_concrete_items()
        recipe_ids = {
            recipe_id
            for contract in validator.CONTRACTS.values()
            for recipe_id in contract["remove"]
        }
        errors = validator.validate_catalog_contract(producers, items, recipe_ids)
        self.assertTrue(any("example:cheap_empty_spool" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
