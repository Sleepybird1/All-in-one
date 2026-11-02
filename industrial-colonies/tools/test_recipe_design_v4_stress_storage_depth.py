#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import generate_managed_recipe_overhaul as generator
import recipe_design_v4_stress_storage_depth as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class StressStorageDepthTests(unittest.TestCase):
    def test_exact_cohort_audits_and_is_idempotent(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        present = {
            recipe["id"]
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.REDESIGNED_IDS
        }
        self.assertEqual(redesigns.REDESIGNED_IDS, frozenset(present))

        redesigns.apply(data)
        report = redesigns.audit(data)
        self.assertEqual("PASS", report["status"])
        self.assertEqual(13, report["redesigned"])
        self.assertEqual(8, report["components"])
        self.assertEqual(5, report["cells"])

        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_all_cards_compile_in_memory(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        for recipe_id in sorted(redesigns.REDESIGNED_IDS):
            card = generator.sequenced(
                recipes[recipe_id],
                generator.stable_uid("recipe", recipe_id),
            )
            self.assertEqual(recipe_id, card["recipeId"])

    def test_reviewed_contract_is_exact_too_cheap_note(self) -> None:
        self.assertEqual(13, len(redesigns.REVIEWED_HASHES))
        self.assertEqual(redesigns.REDESIGNED_IDS, frozenset(redesigns.REVIEWED_HASHES))
        self.assertEqual("Too cheap — make it more complex.", redesigns.REJECTION_NOTE)
        for digest in redesigns.REVIEWED_HASHES.values():
            self.assertTrue(digest.startswith("sha256:"))
            self.assertEqual(71, len(digest))

    def test_missing_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"]
            != "industrial_colonies:appliedcreate/stress_storage_component_64m"
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)


if __name__ == "__main__":
    unittest.main()
