#!/usr/bin/env python3
"""Focused regression tests for powered world-loading progression."""

from __future__ import annotations

import copy
import unittest

import validate_world_loading_progression as validator


class WorldLoadingProgressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = validator.load_object(validator.DEFAULT_MANIFEST)
        cls.compiled = validator.load_object(validator.DEFAULT_COMPILED)
        cls.assignments = validator.load_object(validator.DEFAULT_ASSIGNMENTS)
        cls.config = validator.DEFAULT_CONFIG.read_text(encoding="utf-8-sig")

    def errors(
        self,
        manifest=None,
        compiled=None,
        assignments=None,
        config=None,
        producers=None,
    ) -> list[str]:
        return validator.validate_contract(
            manifest if manifest is not None else self.manifest,
            compiled if compiled is not None else self.compiled,
            assignments if assignments is not None else self.assignments,
            config if config is not None else self.config,
            producers,
        )

    def test_current_contract_passes(self) -> None:
        self.assertEqual([], self.errors())

    def test_missing_crystal_generator_retirement_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["additional_removals"].remove(validator.CRYSTAL_GENERATOR_RECIPE)
        compiled = copy.deepcopy(self.compiled)
        compiled["removals"] = [
            entry
            for entry in compiled["removals"]
            if entry.get("recipeId") != validator.CRYSTAL_GENERATOR_RECIPE
        ]
        errors = self.errors(manifest=manifest, compiled=compiled)
        self.assertTrue(any(validator.CRYSTAL_GENERATOR_RECIPE in error for error in errors))

    def test_small_or_ungated_chunk_controller_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        recipe = next(
            recipe
            for recipe in manifest["recipes"]
            if validator.output_id(recipe) == "advancedperipherals:chunk_controller"
        )
        recipe["pattern"] = ["AEA", "ECE", "AEA"]
        recipe["key"].pop("S")
        errors = self.errors(manifest=manifest)
        self.assertTrue(any("complete 5x5" in error for error in errors))
        self.assertTrue(any("ae2:spatial_anchor" in error for error in errors))

    def test_nonzero_free_force_load_quota_fails(self) -> None:
        config = self.config.replace("max_force_loaded_chunks: 0", "max_force_loaded_chunks: 25")
        self.assertTrue(any("must be 0" in error for error in self.errors(config=config)))

    def test_retired_generator_cannot_return_as_an_unlock(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"][validator.WORLD_LOADING_NODE]["unlocks"].append(
            validator.CRYSTAL_GENERATOR_OUTPUT
        )
        self.assertTrue(
            any("still assigned" in error for error in self.errors(assignments=assignments))
        )

    def test_claims_cannot_be_disabled_as_part_of_gate(self) -> None:
        config = self.config.replace("disable_protection: false", "disable_protection: true")
        config = config.replace("max_claimed_chunks: 500", "max_claimed_chunks: 0")
        errors = self.errors(config=config)
        self.assertTrue(any("disable_protection" in error for error in errors))
        self.assertTrue(any("max_claimed_chunks" in error for error in errors))

    def test_catalog_alternative_producer_fails_closed(self) -> None:
        producers = {
            output: set(recipe_ids)
            for output, recipe_ids in validator.EXPECTED_CATALOG_PRODUCERS.items()
        }
        producers["advancedperipherals:chunk_controller"].add("example:free_chunk_controller")
        self.assertTrue(
            any("catalog producers" in error for error in self.errors(producers=producers))
        )


if __name__ == "__main__":
    unittest.main()
