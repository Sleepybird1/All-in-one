#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import recipe_design_v4_space_electronics as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class SpaceElectronicsRedesignTests(unittest.TestCase):
    def test_current_seed_redesigns_exact_cohort_and_is_idempotent(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        before_unrelated = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] not in redesigns.REDESIGNED_IDS
        }
        present = {
            recipe["id"]
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.REDESIGNED_IDS
        }
        self.assertEqual(redesigns.REDESIGNED_IDS, frozenset(present))

        redesigns.apply(data)
        report = redesigns.audit(data)
        self.assertEqual("PASS", report["status"])
        self.assertEqual(12, report["redesigned"])
        self.assertEqual(9, report["mechanical_crafting"])
        self.assertEqual(3, report["sequenced_assembly"])

        after_unrelated = {
            recipe["id"]: recipe
            for recipe in data["recipes"]
            if recipe["id"] not in redesigns.REDESIGNED_IDS
        }
        self.assertEqual(before_unrelated, after_unrelated)

        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_rejection_contracts_are_exact_and_frozen(self) -> None:
        self.assertEqual(12, len(redesigns.REJECTION_CONTRACTS))
        self.assertEqual(
            redesigns.REDESIGNED_IDS,
            frozenset(redesigns.REJECTION_CONTRACTS),
        )
        for contract in redesigns.REJECTION_CONTRACTS.values():
            self.assertEqual(redesigns.REJECTION_NOTE, contract["note"])
            digest = contract["cardSha256"]
            self.assertTrue(digest.startswith("sha256:"))
            self.assertEqual(71, len(digest))

    def test_missing_active_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"]
            != "industrial_colonies:space/navigation/optical_sensor"
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)

    def test_audit_rejects_perimeter_ring_regression(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        by_id = {recipe["id"]: recipe for recipe in data["recipes"]}

        airlock = by_id["industrial_colonies:space/life_support/airlock"]
        airlock["pattern"] = ["HHHHH", "HFCSH", "HT TH", "HFPBH", "HAMRH"]
        with self.assertRaisesRegex(ValueError, "rejected perimeter ring"):
            redesigns.audit(data)

    def test_audit_rejects_generic_non_electronic_regression(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        by_id = {recipe["id"]: recipe for recipe in data["recipes"]}

        gimbal = by_id["industrial_colonies:space/navigation/gimbal_sensor"]
        gimbal["steps"] = [
            step
            for step in gimbal["steps"]
            if step.get("ingredient")
            not in {
                "tfmg:plastic_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
            }
        ]
        with self.assertRaisesRegex(ValueError, "plastic insulation"):
            redesigns.audit(data)


if __name__ == "__main__":
    unittest.main()
