#!/usr/bin/env python3
"""Mutation tests for the stock utility restoration contract."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import validate_stock_utility_restoration_audit as validator


ROOT = Path(__file__).resolve().parents[1]


class StockUtilityRestorationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads(
            (ROOT / "STOCK_UTILITY_RESTORATION_AUDIT.patch.json").read_text(encoding="utf-8")
        )
        cls.audit = json.loads(
            (ROOT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json").read_text(encoding="utf-8")
        )
        assignments = json.loads(
            (ROOT / "progression" / "machine_node_assignments.json").read_text(encoding="utf-8")
        )
        cls.assignments = validator.assigned_outputs(assignments)
        cls.catalog = validator.catalog_recipe_ids(validator.DEFAULT_CATALOG)

    def parity_errors(self, plan: dict, *, catalog: set[str] | None = None,
                      assignments: set[str] | None = None) -> list[str]:
        return validator.validate_plan_parity(
            plan,
            self.audit,
            self.catalog if catalog is None else catalog,
            self.assignments if assignments is None else assignments,
        )

    def test_implemented_patch_matches_audit_catalog_and_assignments(self) -> None:
        self.assertEqual(self.parity_errors(self.plan), [])
        self.assertEqual(self.plan["status"], "implemented")
        self.assertEqual(len(self.plan["outputs_to_exclude"]), 56)
        self.assertEqual(len(self.plan["recipe_ids_to_preserve"]), 77)

    def test_implementation_metadata_matches_checkpoint(self) -> None:
        self.assertEqual(validator.validate_implementation_metadata(self.plan), [])

    def test_changed_implementation_checkpoint_fails_closed(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["implementation"]["implemented_seed_sha256"] = "0" * 64
        self.assertTrue(validator.validate_implementation_metadata(plan))

    def test_missing_output_fails_closed(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["outputs_to_exclude"].pop()
        self.assertTrue(self.parity_errors(plan))

    def test_missing_source_recipe_fails_closed(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["recipe_ids_to_preserve"].pop()
        self.assertTrue(self.parity_errors(plan))

    def test_wrong_automatic_owner_fails_closed(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["automatic_managed_ids_to_retire"][0] = "industrial_colonies:auto/wrong"
        self.assertTrue(self.parity_errors(plan))

    def test_missing_catalog_recipe_fails_closed(self) -> None:
        recipe_id = self.plan["recipe_ids_to_preserve"][0]
        catalog = set(self.catalog)
        catalog.remove(recipe_id)
        self.assertTrue(self.parity_errors(self.plan, catalog=catalog))

    def test_missing_assignment_fails_closed(self) -> None:
        output = self.plan["outputs_to_exclude"][0]
        assignments = set(self.assignments)
        assignments.remove(output)
        self.assertTrue(self.parity_errors(self.plan, assignments=assignments))

    def implementation_fixture(self) -> tuple[dict, dict, dict]:
        seed = {
            "exclude_outputs": list(self.plan["outputs_to_exclude"]),
            "preserve_recipe_ids": list(self.plan["recipe_ids_to_preserve"]),
            "recipes": [],
            "machine_families": [],
        }
        manifest = {
            "recipes": [],
            "additional_removals": [],
            "preserve_recipe_ids": list(self.plan["recipe_ids_to_preserve"]),
        }
        compiled = {"recipes": [], "removals": []}
        return seed, manifest, compiled

    def test_implemented_fixture_passes(self) -> None:
        seed, manifest, compiled = self.implementation_fixture()
        self.assertEqual(
            validator.validate_implementation(self.plan, seed, manifest, compiled), []
        )

    def test_surviving_automatic_owner_fails_closed(self) -> None:
        seed, manifest, compiled = self.implementation_fixture()
        manifest["recipes"].append({"id": self.plan["automatic_managed_ids_to_retire"][0]})
        self.assertTrue(validator.validate_implementation(self.plan, seed, manifest, compiled))

    def test_preserved_recipe_removal_fails_closed(self) -> None:
        seed, manifest, compiled = self.implementation_fixture()
        manifest["recipes"].append(
            {"id": "industrial_colonies:test", "remove": [self.plan["recipe_ids_to_preserve"][0]]}
        )
        self.assertTrue(validator.validate_implementation(self.plan, seed, manifest, compiled))

    def test_duplicate_seed_union_entry_fails_closed(self) -> None:
        seed, manifest, compiled = self.implementation_fixture()
        seed["exclude_outputs"].append(seed["exclude_outputs"][0])
        errors = validator.validate_implementation(self.plan, seed, manifest, compiled)
        self.assertTrue(any("duplicates" in error for error in errors), errors)

    def test_compiled_managed_owner_fails_closed(self) -> None:
        seed, manifest, compiled = self.implementation_fixture()
        compiled["recipes"].append(
            {
                "recipeId": self.plan["automatic_managed_ids_to_retire"][0],
                "slots": {
                    "output": {
                        "kind": "ITEM",
                        "id": self.plan["outputs_to_exclude"][0],
                    }
                },
            }
        )
        errors = validator.validate_implementation(self.plan, seed, manifest, compiled)
        self.assertTrue(any("compiled KJSGen still claims" in error for error in errors), errors)

    def test_compiled_preserve_removal_fails_closed(self) -> None:
        seed, manifest, compiled = self.implementation_fixture()
        compiled["removals"].append({"recipeId": self.plan["recipe_ids_to_preserve"][0]})
        errors = validator.validate_implementation(self.plan, seed, manifest, compiled)
        self.assertTrue(any("compiled KJSGen still removes" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
