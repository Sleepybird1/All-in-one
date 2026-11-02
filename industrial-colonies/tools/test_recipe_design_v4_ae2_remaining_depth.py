#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import generate_managed_recipe_overhaul as generator
import recipe_design_v4_ae2_remaining_depth as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class RemainingAe2DepthTests(unittest.TestCase):
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
        self.assertEqual(21, report["redesigned"])
        self.assertEqual(6, report["brass_line"])
        self.assertEqual(12, report["railway_line"])
        self.assertEqual(2, report["radiance_line"])
        self.assertEqual(1, report["mechanical_5x5"])
        self.assertEqual(20, report["unique_sequence_boms"])

        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_every_redesign_compiles_in_memory(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        for recipe_id in sorted(redesigns.REDESIGNED_IDS):
            recipe = recipes[recipe_id]
            uid = generator.stable_uid("recipe", recipe_id)
            if recipe["type"] == "mechanical_crafting":
                card = generator.shaped(recipe, uid, True)
            else:
                card = generator.sequenced(recipe, uid)
            self.assertEqual(recipe_id, card["recipeId"])

    def test_review_contracts_are_complete_and_exact(self) -> None:
        self.assertEqual(21, len(redesigns.REJECTION_CONTRACTS))
        self.assertEqual(
            redesigns.REDESIGNED_IDS,
            frozenset(redesigns.REJECTION_CONTRACTS),
        )
        too_cheap = 0
        for contract in redesigns.REJECTION_CONTRACTS.values():
            digest = contract["cardSha256"]
            self.assertTrue(contract["note"])
            self.assertTrue(digest.startswith("sha256:"))
            self.assertEqual(71, len(digest))
            too_cheap += contract["note"] == redesigns.TOO_CHEAP_NOTE
        self.assertEqual(18, too_cheap)
        self.assertEqual(
            "cost and jmore electronics",
            redesigns.REJECTION_CONTRACTS[
                "industrial_colonies:v3_ae2/cell_component_4k"
            ]["note"],
        )
        self.assertIn(
            "wooden barrels",
            redesigns.REJECTION_CONTRACTS["industrial_colonies:v3_ae2/drive"][
                "note"
            ],
        )
        self.assertIn(
            "5x5 grid",
            redesigns.REJECTION_CONTRACTS[
                "industrial_colonies:v3_ae2/spatial_anchor"
            ]["note"],
        )

    def test_drive_anchor_and_storage_ladders_keep_physical_contracts(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}

        drive = recipes["industrial_colonies:v3_ae2/drive"]
        self.assertEqual("tfmg:steel_frame", drive["input"])
        self.assertNotIn("barrel", repr(drive).lower())

        anchor = recipes["industrial_colonies:v3_ae2/spatial_anchor"]
        self.assertEqual("mechanical_crafting", anchor["type"])
        self.assertEqual(5, len(anchor["pattern"]))
        self.assertTrue(all(len(row) == 5 for row in anchor["pattern"]))
        self.assertEqual("A", anchor["pattern"][2][2])
        self.assertNotIn("steps", anchor)

        expected_inputs = {
            "industrial_colonies:digital_storage/ae2_crafting_storage_16k": "ae2:4k_crafting_storage",
            "industrial_colonies:digital_storage/ae2_crafting_storage_64k": "ae2:16k_crafting_storage",
            "industrial_colonies:v3_ae2/fluid_storage_cell_64k": "ae2:fluid_storage_cell_16k",
            "industrial_colonies:v3_ae2/fluid_storage_cell_256k": "ae2:fluid_storage_cell_64k",
            "industrial_colonies:v3_ae2/item_storage_cell_256k": "ae2:item_storage_cell_64k",
        }
        for recipe_id, prior in expected_inputs.items():
            self.assertEqual(prior, recipes[recipe_id]["input"])

    def test_missing_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"] != "industrial_colonies:v3_ae2/spatial_anchor"
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)


if __name__ == "__main__":
    unittest.main()
