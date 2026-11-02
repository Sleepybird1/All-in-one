#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import recipe_design_v4_manufacturing_rejects as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression/managed_recipe_overhaul.seed.json"
LEDGER = ROOT / "build/staging-steel-frame-migration-20260902-v2/default.recipe_reviews.json"
DEPLOYED = ROOT / "build/staging-steel-frame-migration-20260902-v2/default.json"


class ManufacturingRejectedRedesignTests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(SEED.read_text(encoding="utf-8"))

    def test_exact_ids_are_active_rejections_with_matching_notes(self) -> None:
        reviews = json.loads(LEDGER.read_text(encoding="utf-8"))["reviews"]
        deployed = {
            card["recipeId"]
            for card in json.loads(DEPLOYED.read_text(encoding="utf-8"))["recipes"]
        }
        self.assertEqual(15, len(redesigns.MANUFACTURING_REJECT_IDS))
        for recipe_id in redesigns.MANUFACTURING_REJECT_IDS:
            self.assertIn(recipe_id, deployed)
            self.assertEqual("rejected", reviews[recipe_id]["status"])
            self.assertEqual("manual", reviews[recipe_id]["reason"])
            note = reviews[recipe_id]["note"].lower()
            if recipe_id in redesigns.PUMP_COMPACTING_IDS:
                self.assertIn("compacting", note)
            elif recipe_id in redesigns.RAILWAY_ELECTRONICS_IDS or recipe_id in {
                "industrial_colonies:mekanism/advanced_control_circuit",
                "industrial_colonies:mekanism_nuclear/isotopic_centrifuge",
            }:
                self.assertIn("electronics", note)
            elif recipe_id == "industrial_colonies:tfmg_core/heavy_machinery_casing":
                self.assertIn("wrong machine", note)
            elif recipe_id == "industrial_colonies:create_addons/sturdy_whisk":
                self.assertIn("expensive", note)
            else:
                self.assertIn("cheap", note)

    def test_apply_preserves_contract_and_is_idempotent(self) -> None:
        data = self.data()
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.MANUFACTURING_REJECT_IDS
        }
        self.assertEqual(redesigns.MANUFACTURING_REJECT_IDS, frozenset(before))
        redesigns.apply(data)
        report = redesigns.audit(data)
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertEqual(15, report["redesigned"])
        after = {
            recipe["id"]: recipe
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.MANUFACTURING_REJECT_IDS
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

    def test_pumpjack_pivots_are_sensible_compacting_not_cutting(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        for recipe_id in redesigns.PUMP_COMPACTING_IDS:
            recipe = recipes[recipe_id]
            self.assertEqual("compacting", recipe["type"])
            self.assertEqual(redesigns.RAILWAY_PRESS, recipe["machine"])
            self.assertEqual("none", recipe["heat"])
            text = repr(recipe["inputs"])
            self.assertIn("tfmg:cast_iron_ingot", text)
            self.assertIn("tfmg:heavy_plate", text)
            self.assertIn("tfmg:rebar", text)
            self.assertNotIn("tfmg:cast_iron_block", text)
        small = recipes["industrial_colonies:machine/oil_processing/pumpjack_hammer_part"]
        large = recipes["industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part"]
        self.assertIn("4x tfmg:cast_iron_ingot", small["inputs"])
        self.assertIn("8x tfmg:cast_iron_ingot", large["inputs"])

    def test_railway_machines_have_unique_functional_electronic_boms(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        patterns = set()
        required = {
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:coated_circuit_board",
            "tfmg:steel_frame",
        }
        for recipe_id in redesigns.RAILWAY_ELECTRONICS_IDS:
            recipe = recipes[recipe_id]
            self.assertEqual("mechanical_crafting", recipe["type"])
            self.assertEqual(4, len(recipe["pattern"]))
            self.assertTrue(all(len(row) == 4 for row in recipe["pattern"]))
            self.assertNotIn(tuple(recipe["pattern"]), patterns)
            patterns.add(tuple(recipe["pattern"]))
            values = set(recipe["key"].values())
            self.assertTrue(required <= values, recipe_id)
            self.assertNotIn("tfmg:steel_casing", values)
            self.assertGreaterEqual(len(values), 9)

    def test_control_circuit_and_centrifuge_have_real_electronics(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        circuit = recipes["industrial_colonies:mekanism/advanced_control_circuit"]
        circuit_text = repr(circuit)
        self.assertEqual("sequenced_assembly", circuit["type"])
        self.assertEqual(9, len([step for step in circuit["steps"] if step["op"] == "deploying"]))
        centrifuge = recipes["industrial_colonies:mekanism_nuclear/isotopic_centrifuge"]
        self.assertEqual("mechanical_crafting", centrifuge["type"])
        self.assertEqual(5, len(centrifuge["pattern"]))
        self.assertGreaterEqual(len(set(centrifuge["key"].values())), 12)
        for required in (
            "tfmg:plastic_sheet",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:coated_circuit_board",
        ):
            self.assertIn(required, circuit_text)
            self.assertIn(required, centrifuge["key"].values())

    def test_brass_governor_does_not_pull_later_electrical_materials_backward(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipe = next(
            recipe
            for recipe in data["recipes"]
            if recipe["id"] == "industrial_colonies:create_core/rotation_speed_controller"
        )
        ingredients = {
            step["ingredient"] for step in recipe["steps"] if step["op"] == "deploying"
        }
        self.assertIn("create:speedometer", ingredients)
        self.assertIn("create:stressometer", ingredients)
        self.assertIn("minecraft:comparator", ingredients)
        self.assertFalse(any(ingredient.startswith("tfmg:") for ingredient in ingredients))

    def test_heavy_casing_is_costed_structural_compacting(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipe = next(
            recipe
            for recipe in data["recipes"]
            if recipe["id"] == "industrial_colonies:tfmg_core/heavy_machinery_casing"
        )
        self.assertEqual("compacting", recipe["type"])
        self.assertEqual(redesigns.RAILWAY_PRESS, recipe["machine"])
        self.assertEqual(
            {
                "tfmg:steel_casing",
                "tfmg:steel_frame",
                "4x tfmg:heavy_plate",
                "2x tfmg:rebar",
                "8x tfmg:screw",
            },
            set(recipe["inputs"]),
        )

    def test_missing_exact_recipe_fails_closed(self) -> None:
        data = self.data()
        missing = sorted(redesigns.MANUFACTURING_REJECT_IDS)[0]
        data["recipes"] = [recipe for recipe in data["recipes"] if recipe["id"] != missing]
        with self.assertRaises(KeyError):
            redesigns.apply(data)


if __name__ == "__main__":
    unittest.main()
