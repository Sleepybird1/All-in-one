#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import recipe_design_v4_machine_family_corrections as corrections


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class MachineFamilyCorrectionTests(unittest.TestCase):
    def test_all_reviewed_machine_families_change_and_are_idempotent(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        corrections.apply(data)
        self.assertEqual("PASS", corrections.audit(data)["status"])
        after = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in corrections.CORRECTED_IDS
        }
        self.assertEqual(corrections.CORRECTED_IDS, set(after))
        for recipe_id in corrections.DEFAULT_CREATE_IDS:
            recipe = after[recipe_id]
            self.assertNotIn("railway", recipe["input"])
            self.assertEqual("Steel & Petroleum", recipe["phase"])
            self.assertIn("create:iron_sheet", repr(recipe))
            self.assertNotIn("tfmg:steel_sheet", repr(recipe))
        self.assertNotIn("tfmg:steel_sheet", data["exclude_outputs"])
        heavy_plate = after["industrial_colonies:tfmg_core/heavy_plate"]
        self.assertTrue(
            all(
                step.get("machine") == "createcasing:weathered_iron_press"
                for step in heavy_plate["steps"]
            )
        )
        stable = copy.deepcopy(data)
        corrections.apply(data)
        self.assertEqual(stable, data)

    def test_missing_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"] != "industrial_colonies:tfmg_core/heavy_plate"
        ]
        with self.assertRaises(KeyError):
            corrections.apply(data)


if __name__ == "__main__":
    unittest.main()
