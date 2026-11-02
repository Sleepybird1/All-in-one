#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import recipe_design_v4_electronics_primitives as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class ElectronicsPrimitiveRedesignTests(unittest.TestCase):
    def test_current_seed_redesigns_and_is_idempotent(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        self.assertEqual("PASS", redesigns.audit(data)["status"])
        after = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.REDESIGNED_IDS
        }
        self.assertEqual(redesigns.REDESIGNED_IDS, set(after))
        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_missing_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"] != "industrial_colonies:electronics/capacitor"
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)


if __name__ == "__main__":
    unittest.main()
