#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import recipe_design_v5_nuclear_hardware as nuclear


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class NuclearHardwareRedesignTests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(SEED.read_text(encoding="utf-8"))

    def recipes(self, data: dict) -> dict[str, dict]:
        return {recipe["id"]: recipe for recipe in data["recipes"]}

    def test_apply_preserves_recipe_identity_and_is_idempotent(self) -> None:
        data = self.data()
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in nuclear.REDESIGNED_IDS
        }
        self.assertEqual(nuclear.REDESIGNED_IDS, frozenset(before))

        nuclear.apply(data)
        report = nuclear.audit(data)
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertEqual(7, report["redesigned"])
        self.assertEqual(5, report["compacting"])
        self.assertEqual(1, report["deploying"])
        self.assertEqual(1, report["sequenced_assembly"])

        after = self.recipes(data)
        for recipe_id, old in before.items():
            new = after[recipe_id]
            for field in ("id", "node", "phase", "order", "depends_on", "remove"):
                self.assertEqual(old.get(field), new.get(field), (recipe_id, field))
            self.assertEqual(old["output"], new["output"], recipe_id)

        stable = copy.deepcopy(data)
        nuclear.apply(data)
        self.assertEqual(stable, data)

    def test_structural_parts_are_focused_radiance_compacting_batches(self) -> None:
        data = self.data()
        nuclear.apply(data)
        recipes = self.recipes(data)
        structural_ids = nuclear.REDESIGNED_IDS - {
            "industrial_colonies:nuclear/refined_radiance_casing",
            "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer",
        }
        for recipe_id in structural_ids:
            recipe = recipes[recipe_id]
            self.assertEqual("compacting", recipe["type"], recipe_id)
            self.assertEqual(nuclear.RADIANCE_PRESS, recipe["machine"], recipe_id)
            self.assertGreaterEqual(len(recipe["inputs"]), 5, recipe_id)
            self.assertNotIn("mekanism:steel_casing", repr(recipe), recipe_id)
            self.assertNotIn("tfmg:steel_sheet", repr(recipe), recipe_id)

        self.assertIn("tfmg:steel_chemical_vat", repr(recipes["industrial_colonies:bigreactors/fluidizer/casing"]))
        self.assertIn("tfmg:generator", repr(recipes["industrial_colonies:bigreactors/basic_turbine/casing"]))
        self.assertIn("tfmg:aluminum_sheet", repr(recipes["industrial_colonies:bigreactors/basic_turbine/rotor_blade"]))
        self.assertIn("create:shaft", repr(recipes["industrial_colonies:bigreactors/basic_turbine/rotor_shaft"]))

    def test_radiance_casing_does_not_require_its_own_machine_family(self) -> None:
        data = self.data()
        nuclear.apply(data)
        recipe = self.recipes(data)["industrial_colonies:nuclear/refined_radiance_casing"]
        self.assertEqual("deploying", recipe["type"])
        self.assertEqual("create:industrial_iron_block", recipe["input"])
        self.assertEqual("create:refined_radiance", recipe["held"])
        self.assertEqual(nuclear.INDUSTRIAL_DEPLOYER, recipe["machine"])

    def test_nucleosynthesizer_is_a_late_accelerator_control_sequence(self) -> None:
        data = self.data()
        nuclear.apply(data)
        recipe = self.recipes(data)[
            "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer"
        ]
        deployments = [step for step in recipe["steps"] if step["op"] == "deploying"]
        self.assertEqual(9, len(deployments))
        self.assertTrue(all(step["machine"] == nuclear.RADIANCE_DEPLOYER for step in deployments))
        self.assertEqual(
            {"op": "pressing", "machine": nuclear.RADIANCE_PRESS},
            recipe["steps"][-1],
        )
        for ingredient in (
            "mekanism:sps_port",
            "mekanism:supercharged_coil",
            "mekanism:pellet_antimatter",
            "mekanism:pellet_polonium",
            "mekanism:ultimate_control_circuit",
            "megacells:accumulation_processor",
            "ae2:quantum_entangled_singularity",
            "tfmg:transformer",
            "allthemodium:unobtainium_vibranium_alloy_ingot",
        ):
            self.assertIn(ingredient, repr(recipe))

    def test_audit_detects_machine_and_bill_of_material_drift(self) -> None:
        data = self.data()
        nuclear.apply(data)
        recipes = self.recipes(data)
        recipes["industrial_colonies:nuclear/refined_radiance_casing"]["machine"] = (
            nuclear.RADIANCE_DEPLOYER
        )
        self.assertEqual("FAIL", nuclear.audit(data)["status"])

        data = self.data()
        nuclear.apply(data)
        recipe = self.recipes(data)[
            "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer"
        ]
        recipe["steps"] = [
            step
            for step in recipe["steps"]
            if step.get("ingredient") != "mekanism:pellet_antimatter"
        ]
        self.assertEqual("FAIL", nuclear.audit(data)["status"])

    def test_missing_recipe_fails_closed(self) -> None:
        data = self.data()
        missing = sorted(nuclear.REDESIGNED_IDS)[0]
        data["recipes"] = [recipe for recipe in data["recipes"] if recipe["id"] != missing]
        with self.assertRaises(KeyError):
            nuclear.apply(data)


if __name__ == "__main__":
    unittest.main()
