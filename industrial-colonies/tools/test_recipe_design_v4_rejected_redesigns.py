#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import recipe_design_v4_rejected_redesigns as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class RejectedRecipeRedesignTests(unittest.TestCase):
    def test_current_seed_redesigns_and_is_idempotent(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.PROCESSOR_REDESIGN_IDS
        }

        redesigns.apply(data)
        report = redesigns.audit(data)
        self.assertEqual("PASS", report["status"])
        self.assertEqual(16, report["redesigned"])
        self.assertEqual(8, report["processor_redesigns"])
        self.assertEqual(8, report["induction_redesigns"])

        after = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.PROCESSOR_REDESIGN_IDS
        }
        self.assertEqual(set(before), set(after))

        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_induction_ladder_is_meaningful_5x5_and_preserves_contract(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.INDUCTION_REDESIGN_IDS
        }
        self.assertEqual(redesigns.INDUCTION_REDESIGN_IDS, frozenset(before))
        self.assertTrue(
            all(
                recipe.get("type") in {"sequenced_assembly", "mechanical_crafting"}
                for recipe in before.values()
            )
        )

        redesigns.apply(data)
        report = redesigns.audit(data)
        self.assertEqual("PASS", report["status"])
        self.assertEqual(8, report["mechanical_induction_parts"])

        after = {
            recipe["id"]: recipe
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.INDUCTION_REDESIGN_IDS
        }
        patterns = set()
        for recipe_id in sorted(redesigns.INDUCTION_REDESIGN_IDS):
            old = before[recipe_id]
            new = after[recipe_id]
            if old.get("type") == "sequenced_assembly":
                self.assertNotEqual(old, new)
            for field in ("id", "node", "phase", "order", "depends_on", "remove"):
                self.assertEqual(old.get(field), new.get(field), (recipe_id, field))
            self.assertEqual(old["output"], new["output"])
            self.assertEqual("mechanical_crafting", new["type"])
            self.assertEqual(5, len(new["pattern"]))
            self.assertTrue(all(len(row) == 5 for row in new["pattern"]))
            self.assertNotIn(tuple(new["pattern"]), patterns)
            patterns.add(tuple(new["pattern"]))
            ingredients = set(new["key"].values())
            self.assertIn("tfmg:steel_frame", ingredients)
            self.assertNotIn("mekanism:steel_casing", ingredients)
            self.assertTrue(new["exclusive_output"])

    def test_legacy_induction_fingerprint_inputs_are_replaced(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        target_id = redesigns.INDUCTION_CELL_IDS["basic"]
        target = next(recipe for recipe in data["recipes"] if recipe["id"] == target_id)
        for field in redesigns._PROCESS_FIELDS:
            target.pop(field, None)
        target.update(
            {
                "type": "sequenced_assembly",
                "input": "mekanism:induction_casing",
                "transitional": "mekanism:induction_casing",
                "steps": [
                    {
                        "op": "deploying",
                        "ingredient": "mekanism:basic_energy_cube",
                        "machine": "createcasing:weathered_iron_deployer",
                    },
                    {"op": "pressing", "machine": "createcasing:weathered_iron_press"},
                ],
                "loops": 1,
                "output": "mekanism:basic_induction_cell",
                "exclusive_output": True,
            }
        )
        legacy_process = {
            field: copy.deepcopy(target.get(field))
            for field in redesigns._PROCESS_FIELDS
            if field in target
        }

        redesigns.apply(data)
        redesigned = next(recipe for recipe in data["recipes"] if recipe["id"] == target_id)
        redesigned_process = {
            field: copy.deepcopy(redesigned.get(field))
            for field in redesigns._PROCESS_FIELDS
            if field in redesigned
        }
        self.assertNotEqual(legacy_process, redesigned_process)
        self.assertEqual("mechanical_crafting", redesigned["type"])

    def test_missing_induction_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"] != redesigns.INDUCTION_CELL_IDS["basic"]
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)

    def test_missing_rejected_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"] != "industrial_colonies:ae2/logic_processor"
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)


if __name__ == "__main__":
    unittest.main()
