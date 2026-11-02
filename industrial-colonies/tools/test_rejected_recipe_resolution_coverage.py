#!/usr/bin/env python3
"""Regression proof that every active second-pass rejection has an owner."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import recipe_design_v3_mekanism as mekanism_v3
import recipe_design_v4_ae2_electronics_depth as ae2_depth
import recipe_design_v4_ae2_remaining_depth as ae2_remaining
import recipe_design_v4_bigreactors_rejected as bigreactors
import recipe_design_v4_digital_machine_corrections as digital
import recipe_design_v4_electronics_primitives as primitives
import recipe_design_v4_machine_family_corrections as machine_families
import recipe_design_v4_manual_rejections as manual
import recipe_design_v4_manufacturing_rejects as manufacturing
import recipe_design_v4_mega_storage_depth as mega
import recipe_design_v4_rejected_redesigns as initial
import recipe_design_v4_space_electronics as space_electronics
import recipe_design_v4_space_hardware_depth as space_hardware
import recipe_design_v4_stress_storage_depth as stress


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "build" / "staging-review-migration-20260902-v3"
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"
RESTORATION_POLICY = ROOT / "progression" / "default_recipe_restoration_policy.json"

DIRECT_DECISION_IDS = set().union(
    initial.PROCESSOR_REDESIGN_IDS | initial.INDUCTION_REDESIGN_IDS,
    primitives.REDESIGNED_IDS,
    machine_families.CORRECTED_IDS,
    digital.REDESIGNED_IDS,
    ae2_depth.TARGET_IDS,
    stress.REDESIGNED_IDS,
    mega.REDESIGNED_IDS,
    space_electronics.REDESIGNED_IDS,
    bigreactors.BIGREACTORS_REJECTED_IDS,
    space_hardware.REDESIGNED_IDS,
    ae2_remaining.REDESIGNED_IDS,
    manufacturing.MANUFACTURING_REJECT_IDS,
    manual.REVIEW_DECISION_IDS,
)

# These six recipes were reworked as prerequisite/support corrections while
# resolving the active rejection set, but were not themselves rejected cards.
SUPPORT_CORRECTION_IDS = {
    "industrial_colonies:ae2/printed_calculation_processor",
    "industrial_colonies:ae2/printed_engineering_processor",
    "industrial_colonies:ae2/printed_logic_processor",
    "industrial_colonies:electronics/capacitor",
    "industrial_colonies:electronics/coated_circuit_board",
    "industrial_colonies:electronics/transistor",
}

STEEL_FRAME_REJECTION_IDS = {
    "industrial_colonies:mekanism/combiner",
    "industrial_colonies:mekanism_utility/resistive_heater",
    "industrial_colonies:planetary/outpost/nutritional_liquifier",
}


class RejectedRecipeResolutionCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = json.loads(
            (SNAPSHOT / "default.recipe_reviews.json").read_text(encoding="utf-8")
        )["reviews"]
        deployed = json.loads((SNAPSHOT / "default.json").read_text(encoding="utf-8"))
        deployed_ids = {card["recipeId"] for card in deployed["recipes"]}
        cls.active_rejected = {
            recipe_id
            for recipe_id in deployed_ids
            if cls.ledger.get(recipe_id, {}).get("status") == "rejected"
        }
        cls.seed = json.loads(SEED.read_text(encoding="utf-8"))
        cls.restoration = json.loads(RESTORATION_POLICY.read_text(encoding="utf-8"))

    def test_snapshot_contains_the_complete_343_card_rejection_set(self) -> None:
        self.assertEqual(343, len(self.active_rejected))

    def test_direct_modules_cover_179_rejections_plus_six_support_corrections(self) -> None:
        self.assertEqual(185, len(DIRECT_DECISION_IDS))
        self.assertEqual(SUPPORT_CORRECTION_IDS, DIRECT_DECISION_IDS - self.active_rejected)
        self.assertEqual(179, len(DIRECT_DECISION_IDS & self.active_rejected))

    def test_all_rejections_are_partitioned_by_one_resolution_policy(self) -> None:
        direct = DIRECT_DECISION_IDS & self.active_rejected
        restored = {entry["recipeId"] for entry in self.restoration["entries"]}
        retired = {mekanism_v3.RETIRED_STEEL_CASING_RECIPE_ID}
        groups = (direct, restored, STEEL_FRAME_REJECTION_IDS, retired)
        self.assertEqual([179, 160, 3, 1], [len(group) for group in groups])
        for index, left in enumerate(groups):
            for right in groups[index + 1 :]:
                self.assertFalse(left & right, left & right)
        self.assertEqual(self.active_rejected, set().union(*groups))

    def test_three_global_steel_policy_cards_are_actually_corrected(self) -> None:
        recipes = {recipe["id"]: recipe for recipe in self.seed["recipes"]}
        for recipe_id in STEEL_FRAME_REJECTION_IDS:
            self.assertIn(recipe_id, recipes)
            text = repr(recipes[recipe_id])
            self.assertIn("tfmg:steel_frame", text, recipe_id)
            self.assertNotIn("mekanism:steel_casing", text, recipe_id)

    def test_redundant_mekanism_steel_casing_and_invalid_sheet_are_absent(self) -> None:
        recipes = {recipe["id"]: recipe for recipe in self.seed["recipes"]}
        self.assertNotIn(mekanism_v3.RETIRED_STEEL_CASING_RECIPE_ID, recipes)
        self.assertNotIn("tfmg:steel_sheet", repr(self.seed))


if __name__ == "__main__":
    unittest.main()

