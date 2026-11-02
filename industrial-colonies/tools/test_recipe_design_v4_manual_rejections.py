#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import recipe_design_v4_manual_rejections as manual


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"
LEDGER = ROOT / "build" / "staging-steel-frame-migration-20260902-v2" / "default.recipe_reviews.json"


class ManualRejectionRedesignTests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(SEED.read_text(encoding="utf-8"))

    def test_exact_review_decisions_and_notes(self) -> None:
        reviews = json.loads(LEDGER.read_text(encoding="utf-8"))["reviews"]
        self.assertEqual(12, len(manual.REVIEW_DECISION_IDS))
        for recipe_id in manual.REVIEW_DECISION_IDS:
            self.assertEqual("rejected", reviews[recipe_id]["status"], recipe_id)
        self.assertEqual(
            "Keep the original recipe.",
            reviews[manual.STEEL_MECHANISM_MANAGED_ID]["note"],
        )

    def test_apply_preserves_redesign_identity_and_restores_stock(self) -> None:
        data = self.data()
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in manual.REDESIGNED_IDS
        }
        self.assertEqual(manual.REDESIGNED_IDS, frozenset(before))
        manual.apply(data)
        report = manual.audit(data)
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertEqual(11, report["redesigned"])
        self.assertEqual(1, report["restored_default"])
        self.assertEqual(12, report["review_decisions"])
        after = {recipe["id"]: recipe for recipe in data["recipes"]}
        for recipe_id, old in before.items():
            new = after[recipe_id]
            for field in ("id", "node", "phase", "order", "depends_on", "remove"):
                self.assertEqual(old.get(field), new.get(field), (recipe_id, field))
            self.assertEqual(old["output"], new["output"], recipe_id)
            self.assertTrue(new["exclusive_output"])
        self.assertNotIn(manual.STEEL_MECHANISM_MANAGED_ID, after)
        self.assertIn(manual.STEEL_MECHANISM_STOCK_ID, data["preserve_recipe_ids"])

    def test_specific_rejection_corrections(self) -> None:
        data = self.data()
        manual.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}

        drill = recipes["industrial_colonies:big_cannons/cannon_drill"]
        self.assertEqual("mechanical_crafting", drill["type"])
        self.assertEqual(["  D  ", " PTP ", " SCS ", " GEG ", "HHHHH"], drill["pattern"])

        welder = recipes["industrial_colonies:big_cannons/cannon_welder"]
        self.assertEqual("mechanical_crafting", welder["type"])
        self.assertIn("tfmg:propane_bucket", welder["key"].values())
        self.assertIn("tfmg:steel_fluid_tank", welder["key"].values())
        self.assertEqual([" B  ", "VPT ", "FWH ", "HHHH"], welder["pattern"])
        self.assertNotIn("tfmg:steel_sheet", repr(welder))

        control = recipes["industrial_colonies:bigreactors/basic_reactor/control_rod"]
        self.assertEqual("create:refined_radiance", control["key"]["R"])

        enchanter = recipes["industrial_colonies:enchantment_industry/classic_blaze_enchanter"]
        self.assertEqual("mechanical_crafting", enchanter["type"])
        for value in (
            "create_enchantment_industry:blaze_enchanter",
            "create_enchantment_industry:blazes_enchanting_handbook",
            "create_enchantment_industry:experience_lantern",
            "create:mechanical_arm",
            "appliedcreate:stress_processor",
        ):
            self.assertIn(value, enchanter["key"].values())

        huge = recipes["industrial_colonies:engines/huge_diesel_engine"]
        self.assertNotIn("tfmg:turbine_engine", huge["key"].values())
        self.assertIn("tfmg:crankshaft", huge["key"].values())
        self.assertIn("tfmg:engine_controller", huge["key"].values())

        warp = recipes["industrial_colonies:interstellar/warp_drive"]
        self.assertEqual(12, len(set(warp["key"].values())))
        for value in ("cosmowarp:crystal_driver", "cosmowarp:warp_crystal", "cosmowarp:memory_card"):
            self.assertIn(value, warp["key"].values())

        fan = recipes["industrial_colonies:manufacturing/refined_radiance/fan"]
        deployments = [step for step in fan["steps"] if step["op"] == "deploying"]
        self.assertEqual(6, len(deployments))
        self.assertTrue(all(step["machine"] == manual.INDUSTRIAL_DEPLOYER for step in deployments))
        self.assertEqual({"op": "pressing", "machine": manual.INDUSTRIAL_PRESS}, fan["steps"][-1])
        self.assertNotIn("allthemodium:vibranium_allthemodium_alloy_ingot", repr(fan))

        runners = recipes["industrial_colonies:mekanism_tools/armored_free_runners"]
        self.assertEqual("mechanical_crafting", runners["type"])
        self.assertEqual(["C   C", "H   H", "A F A", "D   D", "R   R"], runners["pattern"])

        radiance = recipes["industrial_colonies:nuclear/refined_radiance"]
        self.assertEqual("compacting", radiance["type"])
        self.assertEqual(6, len(radiance["inputs"]))
        self.assertEqual({"count": 2, "id": "create:refined_radiance", "kind": "ITEM"}, radiance["output"])

        altitude = recipes["industrial_colonies:simulated/altitude_sensor"]
        self.assertEqual("sequenced_assembly", altitude["type"])
        self.assertEqual(7, len([step for step in altitude["steps"] if step["op"] == "deploying"]))
        self.assertTrue(all(
            step["machine"] == manual.COPPER_DEPLOYER
            for step in altitude["steps"]
            if step["op"] == "deploying"
        ))

        coupling = recipes["industrial_colonies:simulated/rope_coupling_batch"]
        self.assertEqual("sequenced_assembly", coupling["type"])
        self.assertEqual("simulated:rope_connector", coupling["input"])
        self.assertEqual("2x simulated:rope_coupling", coupling["output"])
        self.assertIn("tfmg:heavy_plate", repr(coupling))
        self.assertNotIn("tfmg:steel_sheet", repr(coupling))

    def test_stock_restoration_cleans_every_suppression_surface(self) -> None:
        data = self.data()
        data["additional_removals"].append(manual.STEEL_MECHANISM_STOCK_ID)
        data["recipes"][0].setdefault("remove", []).append(manual.STEEL_MECHANISM_STOCK_ID)
        data["recipes"][0].setdefault("depends_on", []).append(manual.STEEL_MECHANISM_MANAGED_ID)
        manual.apply(data)
        self.assertEqual("PASS", manual.audit(data)["status"])
        self.assertNotIn(manual.STEEL_MECHANISM_STOCK_ID, data["additional_removals"])
        for recipe in data["recipes"]:
            self.assertNotIn(manual.STEEL_MECHANISM_STOCK_ID, recipe.get("remove", []))
            self.assertNotIn(manual.STEEL_MECHANISM_MANAGED_ID, recipe.get("depends_on", []))

    def test_apply_is_idempotent_after_stock_recipe_is_already_restored(self) -> None:
        data = self.data()
        manual.apply(data)
        stable = copy.deepcopy(data)
        manual.apply(data)
        self.assertEqual(stable, data)

    def test_missing_redesign_target_fails_closed(self) -> None:
        data = self.data()
        missing = sorted(manual.REDESIGNED_IDS)[0]
        data["recipes"] = [recipe for recipe in data["recipes"] if recipe["id"] != missing]
        with self.assertRaises(KeyError):
            manual.apply(data)


if __name__ == "__main__":
    unittest.main()
