#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import recipe_design_v4_ae2_electronics_depth as electronics


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class Ae2ElectronicsDepthTests(unittest.TestCase):
    def load(self) -> dict:
        return json.loads(SEED.read_text(encoding="utf-8"))

    def test_all_fifteen_contracts_are_preserved_and_idempotent(self) -> None:
        data = self.load()
        before = {
            recipe["id"]: {
                key: copy.deepcopy(recipe.get(key))
                for key in ("id", "input", "transitional", "output", "remove")
            }
            for recipe in data["recipes"]
            if recipe["id"] in electronics.TARGET_IDS
        }
        self.assertEqual(electronics.TARGET_IDS, set(before))

        electronics.apply(data)
        report = electronics.audit(data)
        self.assertEqual("PASS", report["status"])
        self.assertEqual(15, report["redesigned"])
        self.assertEqual(15, report["unique_boms"])

        after = {recipe["id"]: recipe for recipe in data["recipes"]}
        for recipe_id, contract in before.items():
            self.assertEqual(
                contract,
                {
                    key: copy.deepcopy(after[recipe_id].get(key))
                    for key in ("id", "input", "transitional", "output", "remove")
                },
            )

        stable = copy.deepcopy(data)
        electronics.apply(data)
        self.assertEqual(stable, data)

    def test_every_recipe_has_a_distinct_electronics_package(self) -> None:
        data = self.load()
        electronics.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        boms = []
        for recipe_id in sorted(electronics.TARGET_IDS):
            recipe = recipes[recipe_id]
            deployed = tuple(step["ingredient"] for step in recipe["steps"][:-1])
            self.assertGreaterEqual(len(deployed), 8)
            self.assertLessEqual(len(deployed), 11)
            self.assertEqual("pressing", recipe["steps"][-1]["op"])
            boms.append(deployed)
        self.assertEqual(len(boms), len(set(boms)))

    def test_missing_target_fails_closed(self) -> None:
        data = self.load()
        missing = sorted(electronics.TARGET_IDS)[0]
        data["recipes"] = [recipe for recipe in data["recipes"] if recipe["id"] != missing]
        with self.assertRaises(KeyError):
            electronics.apply(data)


if __name__ == "__main__":
    unittest.main()

