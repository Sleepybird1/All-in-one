#!/usr/bin/env python3
"""Close the final manually reviewed recipe cohort without live-pack I/O."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import recipe_design_v5_digital_transmission as digital
import recipe_design_v5_nuclear_hardware as nuclear
import recipe_design_v5_pumpjack_manufacturing as manufacturing


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"
ACCEPTANCE = ROOT / "progression" / "recipe_review_acceptance.json"
REPORT = ROOT / "progression" / "recipe_review_reconciliation_report.json"
REVIEWED = ROOT / "pack-kjsgen" / "default.reviewed.managed.json"

DEFAULT_RECIPE_IDS = frozenset(
    {
        "industrial_colonies:mechanical/mechanical_press",
        "industrial_colonies:mechanical/mechanical_pump",
        "industrial_colonies:brass/deployer",
        "industrial_colonies:brass/mechanical_crafter",
        "industrial_colonies:steam/steam_engine",
        "industrial_colonies:fluid_infrastructure/cast_iron_pipe",
        "industrial_colonies:grid/empty_spool",
    }
)

REDESIGNED_REJECTION_IDS = frozenset().union(
    manufacturing.TARGET_IDS,
    digital.REDESIGNED_IDS,
    nuclear.REDESIGNED_IDS,
)

RETIRED_REJECTION_IDS = digital.PRIMARY_RETIRED_IDS
ORIGINAL_REMAINING_REJECTIONS = frozenset().union(
    DEFAULT_RECIPE_IDS,
    REDESIGNED_REJECTION_IDS,
    RETIRED_REJECTION_IDS,
)


class RemainingRejectionResolutionTests(unittest.TestCase):
    def test_exact_final_cohort_has_one_disjoint_resolution_each(self) -> None:
        groups = (
            DEFAULT_RECIPE_IDS,
            REDESIGNED_REJECTION_IDS,
            RETIRED_REJECTION_IDS,
        )
        self.assertEqual([7, 25, 3], [len(group) for group in groups])
        self.assertEqual(35, len(ORIGINAL_REMAINING_REJECTIONS))
        for index, left in enumerate(groups):
            for right in groups[index + 1 :]:
                self.assertFalse(left & right, left & right)

    def test_every_resolution_is_bound_to_an_actual_rejected_review(self) -> None:
        acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8-sig"))
        decisions = {
            entry["recipeId"]: entry["decision"]
            for entry in acceptance["entries"]
            if entry["recipeId"] in ORIGINAL_REMAINING_REJECTIONS
        }
        self.assertEqual(ORIGINAL_REMAINING_REJECTIONS, frozenset(decisions))
        for recipe_id, decision in decisions.items():
            self.assertEqual("rejected", decision["status"], recipe_id)
            expected_reason = "default_recipe" if recipe_id in DEFAULT_RECIPE_IDS else "manual"
            self.assertEqual(expected_reason, decision["reason"], recipe_id)

    def test_seed_contains_redesigns_and_proves_every_retirement(self) -> None:
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        recipe_ids = {recipe["id"] for recipe in seed["recipes"]}
        self.assertTrue(REDESIGNED_REJECTION_IDS <= recipe_ids)
        self.assertTrue(manufacturing.SUPPORT_IDS <= recipe_ids)
        self.assertTrue(digital.RETIRED_IDS.isdisjoint(recipe_ids))
        self.assertTrue(DEFAULT_RECIPE_IDS <= recipe_ids)

        for recipe_id, (stock_id, output_id) in digital.RETIREMENTS.items():
            self.assertIn(stock_id, seed["additional_removals"], recipe_id)
            self.assertIn(output_id, seed["exclude_outputs"], recipe_id)
            self.assertNotIn(stock_id, seed["preserve_recipe_ids"], recipe_id)

    def test_reconciliation_leaves_only_the_seven_default_cards_unchanged(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        classifications = report["sourceClassifications"]
        self.assertEqual(
            DEFAULT_RECIPE_IDS,
            frozenset(classifications["rejected_source_unchanged"]),
        )
        self.assertTrue(
            REDESIGNED_REJECTION_IDS
            <= set(classifications["rejected_source_redesigned"])
        )
        all_classified = set().union(*map(set, classifications.values()))
        self.assertTrue(digital.RETIRED_IDS.isdisjoint(all_classified))
        self.assertEqual(0, report["nextUnmanaged"])
        reviewed = json.loads(REVIEWED.read_text(encoding="utf-8"))
        self.assertEqual(len(reviewed["recipes"]), report["nextManaged"])

    def test_reviewed_project_exposes_redesigns_but_not_defaults_or_retirements(self) -> None:
        reviewed = json.loads(REVIEWED.read_text(encoding="utf-8"))
        recipe_ids = {recipe["recipeId"] for recipe in reviewed["recipes"]}
        self.assertTrue(REDESIGNED_REJECTION_IDS <= recipe_ids)
        self.assertTrue(DEFAULT_RECIPE_IDS.isdisjoint(recipe_ids))
        self.assertTrue(digital.RETIRED_IDS.isdisjoint(recipe_ids))


if __name__ == "__main__":
    unittest.main()
