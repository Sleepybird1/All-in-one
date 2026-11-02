#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import recipe_design_v5_digital_transmission as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"
ACCEPTANCE = ROOT / "progression" / "recipe_review_acceptance.json"


class DigitalTransmissionV5Tests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(SEED.read_text(encoding="utf-8"))

    def test_exact_manual_rejection_contracts(self) -> None:
        acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8-sig"))
        decisions = {
            entry["recipeId"]: entry["decision"]
            for entry in acceptance["entries"]
            if entry["recipeId"] in redesigns.REVIEW_DECISION_IDS
        }
        self.assertEqual(redesigns.REVIEW_DECISION_IDS, frozenset(decisions))
        self.assertEqual(15, len(redesigns.REJECTION_CONTRACTS))
        for recipe_id, contract in redesigns.REJECTION_CONTRACTS.items():
            decision = decisions[recipe_id]
            self.assertEqual("rejected", decision["status"], recipe_id)
            self.assertEqual(contract["note"], decision["note"], recipe_id)
            self.assertEqual(contract["cardSha256"], decision["cardSha256"], recipe_id)

    def test_apply_is_scoped_audited_and_idempotent(self) -> None:
        data = self.data()
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"]
            not in (redesigns.REVIEW_DECISION_IDS | redesigns.SUPPORT_REDESIGN_IDS)
        }
        redesigns.apply(data)
        report = redesigns.audit(data)
        self.assertEqual(
            {
                "status": "PASS",
                "review_decisions": 15,
                "redesigned": 9,
                "retired": 6,
                "support_redesigns": 9,
                "digital_sequences": 6,
                "transmission_compacting": 3,
            },
            report,
        )
        after = {recipe["id"]: recipe for recipe in data["recipes"]}
        for recipe_id, recipe in before.items():
            expected = copy.deepcopy(recipe)
            if "depends_on" in expected:
                remaining = [
                    dependency
                    for dependency in expected["depends_on"]
                    if dependency not in redesigns.RETIRED_IDS
                ]
                if remaining:
                    expected["depends_on"] = remaining
                else:
                    expected.pop("depends_on")
            self.assertEqual(expected, after[recipe_id], recipe_id)
        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_digital_routes_are_complex_unique_sequences_without_rings(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        signatures = set()
        expected_families = {
            "industrial_colonies:digital_core/import_bus": (
                redesigns.COPPER_DEPLOYER,
                redesigns.COPPER_PRESS,
            ),
            "industrial_colonies:ae2_high_energy/export_bus": (
                redesigns.COPPER_DEPLOYER,
                redesigns.COPPER_PRESS,
            ),
            "industrial_colonies:digital_core/interface": (
                redesigns.BRASS_DEPLOYER,
                redesigns.BRASS_PRESS,
            ),
            "industrial_colonies:digital_core/pattern_provider": (
                redesigns.BRASS_DEPLOYER,
                redesigns.BRASS_PRESS,
            ),
            "industrial_colonies:ae2_high_energy/me_p2p_tunnel": (
                redesigns.BRASS_DEPLOYER,
                redesigns.BRASS_PRESS,
            ),
            "industrial_colonies:ae2_high_energy/mega_crafting_unit": (
                redesigns.RAILWAY_DEPLOYER,
                redesigns.RAILWAY_PRESS,
            ),
        }
        for recipe_id, (deployer, press) in expected_families.items():
            recipe = recipes[recipe_id]
            self.assertEqual("sequenced_assembly", recipe["type"])
            self.assertNotIn("pattern", recipe)
            self.assertNotIn("key", recipe)
            deployments = [step for step in recipe["steps"] if step["op"] == "deploying"]
            self.assertGreaterEqual(len(deployments), 7, recipe_id)
            self.assertTrue(all(step["machine"] == deployer for step in deployments))
            self.assertEqual({"op": "pressing", "machine": press}, recipe["steps"][-1])
            signature = tuple(step["ingredient"] for step in deployments)
            self.assertNotIn(signature, signatures, recipe_id)
            signatures.add(signature)
            self.assertIn("tfmg:", repr(recipe))
            self.assertIn("ae2:", repr(recipe))

        mega = recipes["industrial_colonies:ae2_high_energy/mega_crafting_unit"]
        for component in (
            "megacells:accumulation_processor",
            "ae2:crafting_accelerator",
            "ae2:pattern_provider",
            "ae2:fluix_smart_dense_cable",
            "tfmg:transformer",
            "mekanism:elite_control_circuit",
        ):
            self.assertIn(component, repr(mega))

    def test_useful_basic_transmitters_are_casing_locked_compacting_batches(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        expected = {
            "industrial_colonies:mekanism/transmission/basic_logistical_transporter": (
                redesigns.WEATHERED_PRESS,
                "create:chute",
            ),
            "industrial_colonies:mekanism/transmission/basic_pressurized_tube": (
                redesigns.WEATHERED_PRESS,
                "tfmg:steel_fluid_valve",
            ),
            "industrial_colonies:mekanism/transmission/basic_universal_cable": (
                redesigns.COPPER_PRESS,
                "tfmg:copper_wire",
            ),
        }
        for recipe_id, (machine, signature) in expected.items():
            recipe = recipes[recipe_id]
            self.assertEqual("compacting", recipe["type"])
            self.assertEqual(machine, recipe["machine"])
            self.assertNotIn("pattern", recipe)
            self.assertNotIn("key", recipe)
            self.assertIn(signature, repr(recipe))
            self.assertEqual(8, recipe["output"]["count"])

    def test_redundant_transmitters_are_retired_but_stock_stays_disabled(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        self.assertTrue(redesigns.RETIRED_IDS.isdisjoint(recipes))
        for recipe_id, (stock_id, output_id) in redesigns.RETIREMENTS.items():
            self.assertIn(stock_id, data["additional_removals"], recipe_id)
            self.assertIn(output_id, data["exclude_outputs"], recipe_id)
            self.assertNotIn(stock_id, data["preserve_recipe_ids"], recipe_id)
            for recipe in data["recipes"]:
                self.assertNotIn(recipe_id, recipe.get("depends_on", []))

    def test_disabled_transmission_consumers_use_create_first_grid_hardware(self) -> None:
        data = self.data()
        redesigns.apply(data)
        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}

        elite_pipe = recipes[redesigns.ELITE_MECHANICAL_PIPE_ID]
        self.assertEqual("compacting", elite_pipe["type"])
        self.assertEqual(redesigns.INDUSTRIAL_PRESS, elite_pipe["machine"])
        self.assertEqual(8, elite_pipe["output"]["count"])
        self.assertIn("tfmg:steel_smart_fluid_pipe", repr(elite_pipe))

        for recipe_id, replacements in redesigns.SUPPORT_ITEM_REPLACEMENTS.items():
            recipe = recipes[recipe_id]
            text = repr(recipe)
            for old, new in replacements.items():
                self.assertNotIn(old, text, recipe_id)
                self.assertIn(new, text, recipe_id)

        retired_outputs = {output for _, output in redesigns.RETIREMENTS.values()}
        for recipe in data["recipes"]:
            inputs = {
                key: recipe[key]
                for key in (
                    "input",
                    "inputs",
                    "held",
                    "key",
                    "ingredients",
                    "steps",
                    "machine",
                    "transitional",
                )
                if key in recipe
            }
            rendered = repr(inputs)
            self.assertFalse(
                any(output in rendered for output in retired_outputs), recipe["id"]
            )

    def test_missing_active_target_or_unproven_retirement_fails_closed(self) -> None:
        data = self.data()
        active = sorted(redesigns.REDESIGNED_IDS)[0]
        data["recipes"] = [recipe for recipe in data["recipes"] if recipe["id"] != active]
        with self.assertRaises(KeyError):
            redesigns.apply(data)

        data = self.data()
        retired = sorted(redesigns.RETIRED_IDS)[0]
        stock_id, output_id = redesigns.RETIREMENTS[retired]
        data["recipes"] = [recipe for recipe in data["recipes"] if recipe["id"] != retired]
        data["additional_removals"] = [
            value for value in data["additional_removals"] if value != stock_id
        ]
        data["exclude_outputs"] = [
            value for value in data["exclude_outputs"] if value != output_id
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)


if __name__ == "__main__":
    unittest.main()
