#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import recipe_design_v4_space_hardware_depth as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class SpaceHardwareDepthTests(unittest.TestCase):
    def test_all_twenty_active_rejects_redesign_and_are_idempotent(self) -> None:
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
        self.assertEqual(20, report["redesigned"])
        self.assertEqual(6, report["too_cheap"])
        self.assertEqual(14, report["needs_electronics"])
        self.assertEqual(7, report["mechanical_crafting"])
        self.assertEqual(13, report["sequenced_assembly"])

        after_unrelated = {
            recipe["id"]: recipe
            for recipe in data["recipes"]
            if recipe["id"] not in redesigns.REDESIGNED_IDS
        }
        self.assertEqual(before_unrelated, after_unrelated)

        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_contracts_preserve_exact_second_pass_notes_and_hash_shape(self) -> None:
        self.assertEqual(20, len(redesigns.REJECTION_CONTRACTS))
        self.assertEqual(6, len(redesigns.TOO_CHEAP_IDS))
        self.assertEqual(14, len(redesigns.NEEDS_ELECTRONICS_IDS))
        self.assertEqual(
            redesigns.REDESIGNED_IDS,
            frozenset(redesigns.REJECTION_CONTRACTS),
        )
        for recipe_id, contract in redesigns.REJECTION_CONTRACTS.items():
            expected_note = (
                redesigns.TOO_CHEAP_NOTE
                if recipe_id in redesigns.TOO_CHEAP_IDS
                else redesigns.ELECTRONICS_NOTE
            )
            self.assertEqual(expected_note, contract["note"])
            digest = contract["cardSha256"]
            self.assertTrue(digest.startswith("sha256:"))
            self.assertEqual(71, len(digest))

    def test_missing_active_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"] != "industrial_colonies:space_coverage/crystal_driver"
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)

    def test_audit_rejects_electronics_and_planetary_ladder_regressions(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        by_id = {recipe["id"]: recipe for recipe in data["recipes"]}

        rcs = by_id["industrial_colonies:space_coverage/rcs_thruster"]
        rcs["steps"] = [
            step
            for step in rcs["steps"]
            if step.get("ingredient")
            not in {
                "tfmg:plastic_sheet",
                "tfmg:coated_circuit_board",
                "tfmg:transistor_item",
            }
        ]
        with self.assertRaisesRegex(ValueError, "plastic insulation"):
            redesigns.audit(data)

        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        by_id = {recipe["id"]: recipe for recipe in data["recipes"]}
        by_id["industrial_colonies:space_hardware/ostrum_engine"]["input"] = (
            "ad_astra:steel_engine"
        )
        with self.assertRaisesRegex(ValueError, "planetary engine upgrade ladder"):
            redesigns.audit(data)

    def test_audit_rejects_perimeter_ring_regression(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        by_id = {recipe["id"]: recipe for recipe in data["recipes"]}
        nozzle = by_id["industrial_colonies:space/propulsion/engine_nozzle"]
        nozzle["pattern"] = ["TTTTT", "HPVPH", "HLBLH", "HCMCH", "PPPPP"]
        with self.assertRaisesRegex(ValueError, "rejected perimeter ring"):
            redesigns.audit(data)


if __name__ == "__main__":
    unittest.main()

