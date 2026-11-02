#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import recipe_design_v4_bigreactors_rejected as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression/managed_recipe_overhaul.seed.json"
LEDGER = ROOT / "build/staging-steel-frame-migration-20260902-v2/default.recipe_reviews.json"
DEPLOYED = ROOT / "build/staging-steel-frame-migration-20260902-v2/default.json"


class BigReactorsRejectedRedesignTests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(SEED.read_text(encoding="utf-8"))

    def test_exact_active_review_cohort(self) -> None:
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))["reviews"]
        deployed_ids = {
            card["recipeId"]
            for card in json.loads(DEPLOYED.read_text(encoding="utf-8"))["recipes"]
        }
        exact_notes = {
            "Too cheap — make it more complex.",
            "Needs more electronics: plastic, semiconductors, and circuit components.",
        }
        derived = {
            recipe_id
            for recipe_id, decision in ledger.items()
            if recipe_id in deployed_ids
            and decision.get("status") == "rejected"
            and decision.get("note") in exact_notes
            and (
                recipe_id.startswith("industrial_colonies:bigreactors/basic_turbine/")
                or recipe_id.startswith("industrial_colonies:bigreactors/energizer/")
                or recipe_id.startswith("industrial_colonies:bigreactors/fluidizer/")
                or recipe_id.startswith("industrial_colonies:bigreactors/reprocessor/")
                or recipe_id == "industrial_colonies:nuclear/reinforced_reactor_controller"
            )
        }
        self.assertEqual(redesigns.BIGREACTORS_REJECTED_IDS, frozenset(derived))
        self.assertEqual(15, len(derived))

    def test_apply_preserves_identity_and_ownership_and_is_idempotent(self) -> None:
        data = self.data()
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.BIGREACTORS_REJECTED_IDS
        }
        self.assertEqual(redesigns.BIGREACTORS_REJECTED_IDS, frozenset(before))
        redesigns.apply(data)
        report = redesigns.audit(data)
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertEqual(15, report["redesigned"])
        self.assertEqual(4, report["mechanical"])
        self.assertEqual(11, report["sequenced"])
        after = {
            recipe["id"]: recipe
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.BIGREACTORS_REJECTED_IDS
        }
        for recipe_id, old in before.items():
            new = after[recipe_id]
            for field in ("id", "node", "phase", "order", "depends_on", "remove"):
                self.assertEqual(old.get(field), new.get(field), (recipe_id, field))
            self.assertEqual(old["output"], new["output"], recipe_id)
            self.assertTrue(new["exclusive_output"])
        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_mechanical_cards_are_bom_shapes_not_expensive_rings(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        mechanical = [
            recipes[recipe_id]
            for recipe_id in redesigns.BIGREACTORS_REJECTED_IDS
            if recipes[recipe_id]["type"] == "mechanical_crafting"
        ]
        self.assertEqual(4, len(mechanical))
        outer_positions = [
            *((0, column) for column in range(5)),
            *((4, column) for column in range(5)),
            *((row, 0) for row in range(1, 4)),
            *((row, 4) for row in range(1, 4)),
        ]
        for recipe in mechanical:
            pattern = recipe["pattern"]
            self.assertEqual(5, len(pattern))
            self.assertTrue(all(len(row) == 5 for row in pattern))
            outer = [pattern[row][column] for row, column in outer_positions if pattern[row][column] != " "]
            self.assertGreaterEqual(len(set(outer)), 5, recipe["id"])
            self.assertGreaterEqual(len(set(recipe["key"].values())), 9, recipe["id"])
            self.assertNotIn("mekanism:steel_casing", recipe["key"].values())

    def test_sequences_use_relevant_machine_family_and_focused_complexity(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        for recipe_id, family in redesigns.SEQUENCE_FAMILIES.items():
            recipe = recipes[recipe_id]
            self.assertEqual("sequenced_assembly", recipe["type"])
            deployments = [step for step in recipe["steps"] if step["op"] == "deploying"]
            self.assertIn(len(deployments), {8, 9}, recipe_id)
            expected_deployer, expected_press = {
                "industrial": (redesigns.INDUSTRIAL_DEPLOYER, redesigns.INDUSTRIAL_PRESS),
                "radiance": (redesigns.RADIANCE_DEPLOYER, redesigns.RADIANCE_PRESS),
            }[family]
            self.assertTrue(all(step["machine"] == expected_deployer for step in deployments))
            self.assertEqual(
                {"op": "pressing", "machine": expected_press}, recipe["steps"][-1]
            )
            self.assertNotIn("mekanism:steel_casing", repr(recipe))

    def test_electronics_rejections_get_complete_electronics_bom(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        required = {
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:coated_circuit_board",
        }
        for recipe_id in redesigns.ELECTRONICS_REJECTION_IDS:
            text = repr(recipes[recipe_id])
            self.assertTrue(all(item in text for item in required), recipe_id)

    def test_missing_exact_recipe_fails_closed(self) -> None:
        data = self.data()
        missing = sorted(redesigns.BIGREACTORS_REJECTED_IDS)[0]
        data["recipes"] = [recipe for recipe in data["recipes"] if recipe["id"] != missing]
        with self.assertRaises(KeyError):
            redesigns.apply(data)


if __name__ == "__main__":
    unittest.main()
