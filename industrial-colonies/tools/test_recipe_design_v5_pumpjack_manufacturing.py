#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_managed_recipe_overhaul as compiler
import recipe_design_v5_pumpjack_manufacturing as v5


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"
ACCEPTANCE = ROOT / "progression" / "recipe_review_acceptance.json"


class PumpjackManufacturingV5Tests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(SEED.read_text(encoding="utf-8"))

    def redesigned(self) -> dict[str, dict]:
        data = self.data()
        v5.apply(data)
        return {
            recipe["id"]: recipe
            for recipe in data["recipes"]
            if recipe["id"] in v5.ALL_REDESIGNED_IDS
        }

    def test_exact_manual_rejections_and_notes_are_bound(self) -> None:
        entries = {
            entry["recipeId"]: entry
            for entry in json.loads(ACCEPTANCE.read_text(encoding="utf-8"))["entries"]
        }
        self.assertEqual(9, len(v5.TARGET_IDS))
        self.assertEqual(2, len(v5.SUPPORT_IDS))
        self.assertEqual(v5.ALL_REDESIGNED_IDS, frozenset(v5.EXPECTED_OUTPUTS))
        for recipe_id, expected_note in v5.REVIEW_NOTES.items():
            self.assertIn(recipe_id, entries)
            decision = entries[recipe_id]["decision"]
            self.assertEqual("rejected", decision["status"], recipe_id)
            self.assertEqual("manual", decision["reason"], recipe_id)
            self.assertEqual(expected_note, decision["note"], recipe_id)

    def test_apply_preserves_identity_metadata_and_is_idempotent(self) -> None:
        data = self.data()
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in v5.ALL_REDESIGNED_IDS
        }
        self.assertEqual(v5.ALL_REDESIGNED_IDS, frozenset(before))
        v5.apply(data)
        report = v5.audit(data)
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertEqual(9, report["reviewed_redesigns"])
        self.assertEqual(2, report["support_corrections"])
        self.assertEqual(11, report["redesigned"])
        self.assertEqual(8, report["pumpjack"])
        self.assertEqual(2, report["brass_sequences"])
        after = {recipe["id"]: recipe for recipe in data["recipes"]}
        for recipe_id, old in before.items():
            new = after[recipe_id]
            for field in ("id", "node", "depends_on", "remove"):
                self.assertEqual(old.get(field), new.get(field), (recipe_id, field))
            if recipe_id in v5.PUMPJACK_IDS:
                self.assertEqual("Steel & Petroleum", new["phase"], recipe_id)
                self.assertEqual(v5.PUMPJACK_ORDER[recipe_id], new["order"], recipe_id)
            else:
                for field in ("phase", "order"):
                    self.assertEqual(old.get(field), new.get(field), (recipe_id, field))
            self.assertEqual(old["output"], new["output"], recipe_id)
            self.assertTrue(new["exclusive_output"])
        stable = copy.deepcopy(data)
        v5.apply(data)
        self.assertEqual(stable, data)

    def test_pumpjack_base_is_a_compact_physical_4_by_5_build(self) -> None:
        recipe = self.redesigned()[
            "industrial_colonies:machine/oil_processing/pumpjack_base"
        ]
        self.assertEqual("mechanical_crafting", recipe["type"])
        self.assertEqual([" M M", "ITBI", "IPGI", "IFFI", "FRRF"], recipe["pattern"])
        self.assertEqual(5, len(recipe["pattern"]))
        self.assertTrue(all(len(row) == 4 for row in recipe["pattern"]))
        self.assertEqual(v5.WEATHERED_GEARBOX, recipe["key"]["G"])
        for relevant in (
            "tfmg:cast_iron_mechanical_pump",
            "tfmg:cast_iron_fluid_tank",
            "tfmg:cast_iron_pipe",
            "tfmg:cast_iron_frame",
            "tfmg:rebar",
        ):
            self.assertIn(relevant, recipe["key"].values())

    def test_pumpjack_parts_use_the_requested_weathered_processes(self) -> None:
        recipes = self.redesigned()
        small = recipes[
            "industrial_colonies:machine/oil_processing/pumpjack_hammer_connector"
        ]
        self.assertEqual("compacting", small["type"])
        self.assertEqual(v5.WEATHERED_PRESS, small["machine"])
        self.assertEqual(
            {
                "tfmg:pumpjack_hammer_part",
                "2x create:brass_sheet",
                "tfmg:rebar",
                "2x tfmg:screw",
            },
            set(small["inputs"]),
        )
        for recipe_id in v5.MECHANICAL_PUMPJACK_IDS:
            self.assertEqual("mechanical_crafting", recipes[recipe_id]["type"], recipe_id)
        large_connector = recipes[
            "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector"
        ]
        self.assertEqual([" BB  ", "R L R", " HWH ", " S S "], large_connector["pattern"])
        self.assertIn("tfmg:large_pumpjack_hammer_part", large_connector["key"].values())
        self.assertIn(v5.WEATHERED_STRUCTURE, large_connector["key"].values())

        for recipe_id in v5.SUPPORT_IDS:
            part = recipes[recipe_id]
            self.assertEqual("compacting", part["type"])
            self.assertEqual(v5.WEATHERED_PRESS, part["machine"])
            self.assertEqual("Steel & Petroleum", part["phase"])
            self.assertIn("tfmg:heavy_plate", repr(part))
            self.assertIn("tfmg:rebar", repr(part))
            self.assertIn("tfmg:screw", repr(part))

        for recipe_id in v5.PUMPJACK_IDS:
            self.assertEqual("Steel & Petroleum", recipes[recipe_id]["phase"], recipe_id)

    def test_hammer_redesign_adds_only_functional_missing_hardware(self) -> None:
        recipe = self.redesigned()[
            "industrial_colonies:machine/oil_processing/pumpjack_hammer"
        ]
        self.assertEqual([" IHI ", "ITPTI", "TTGTT", "  A  ", "  F  "], recipe["pattern"])
        values = set(recipe["key"].values())
        for required in (
            "tfmg:pumpjack_hammer_part",
            "tfmg:heavy_plate",
            "create:shaft",
            "tfmg:cast_iron_frame",
            v5.WEATHERED_GEARBOX,
        ):
            self.assertIn(required, values)
        self.assertNotIn("mekanism:steel_casing", values)
        self.assertNotIn("create:precision_mechanism", values)

    def test_heads_are_distinct_mechanical_laminations_not_shaped_shortcuts(self) -> None:
        recipes = self.redesigned()
        small = recipes[
            "industrial_colonies:machine/oil_processing/pumpjack_hammer_head"
        ]
        large = recipes[
            "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head"
        ]
        self.assertEqual("mechanical_crafting", small["type"])
        self.assertEqual("mechanical_crafting", large["type"])
        self.assertEqual(4, len(small["pattern"]))
        self.assertEqual(5, len(large["pattern"]))
        self.assertNotEqual(tuple(small["pattern"]), tuple(large["pattern"]))
        for recipe in (small, large):
            values = set(recipe["key"].values())
            self.assertIn(v5.WEATHERED_STRUCTURE, values)
            self.assertIn("tfmg:cast_iron_block", values)
            self.assertIn("tfmg:cast_iron_sheet", values)
            self.assertIn("tfmg:heavy_plate", values)
            self.assertIn("tfmg:rebar", values)

    def test_brass_machines_are_copper_line_precision_sequences(self) -> None:
        recipes = self.redesigned()
        expected_inputs = {
            "industrial_colonies:manufacturing/brass_deployer": (
                "createcasing:copper_deployer",
                "create:brass_hand",
            ),
            "industrial_colonies:manufacturing/brass_press": (
                "createcasing:copper_press",
                "tfmg:heavy_plate",
            ),
        }
        ingredient_sets = []
        for recipe_id, (input_item, role_part) in expected_inputs.items():
            recipe = recipes[recipe_id]
            self.assertEqual("sequenced_assembly", recipe["type"])
            self.assertEqual(input_item, recipe["input"])
            self.assertEqual(input_item, recipe["transitional"])
            deployments = [step for step in recipe["steps"] if step["op"] == "deploying"]
            self.assertEqual(8, len(deployments))
            self.assertTrue(all(step["machine"] == v5.COPPER_DEPLOYER for step in deployments))
            self.assertEqual(
                {"op": "pressing", "machine": v5.COPPER_PRESS},
                recipe["steps"][-1],
            )
            ingredients = [step["ingredient"] for step in deployments]
            self.assertEqual(len(ingredients), len(set(ingredients)))
            self.assertEqual(1, ingredients.count("create:precision_mechanism"))
            self.assertIn(role_part, ingredients)
            for common in (
                "create:brass_casing",
                "tfmg:electric_motor",
                "tfmg:coated_circuit_board",
                "create:electron_tube",
                "tfmg:plastic_sheet",
            ):
                self.assertIn(common, ingredients)
            ingredient_sets.append(tuple(ingredients))
        self.assertNotEqual(*ingredient_sets)

    def test_winding_machine_is_simplified_without_a_progression_cycle(self) -> None:
        recipe = self.redesigned()["industrial_colonies:heavy_industry/winding_machine"]
        self.assertEqual("mechanical_crafting", recipe["type"])
        self.assertEqual([" FAF", "CAGC", "HMAH", " F F"], recipe["pattern"])
        self.assertEqual(4, len(recipe["pattern"]))
        self.assertTrue(all(len(row) == 4 for row in recipe["pattern"]))
        self.assertLessEqual(
            sum(character != " " for row in recipe["pattern"] for character in row),
            14,
        )
        self.assertEqual(
            {
                "create:shaft",
                "tfmg:copper_spool",
                "tfmg:steel_frame",
                "tfmg:steel_mechanism",
                "tfmg:heavy_plate",
                "tfmg:heavy_machinery_casing",
            },
            set(recipe["key"].values()),
        )
        self.assertNotIn("tfmg:electric_motor", repr(recipe))

    def test_every_proposal_compiles_through_the_current_kjsgen_schema(self) -> None:
        recipes = self.redesigned()
        for recipe_id, recipe in recipes.items():
            uid = compiler.stable_uid("recipe", recipe_id)
            if recipe["type"] == "mechanical_crafting":
                card = compiler.shaped(recipe, uid, mechanical=True)
                self.assertEqual("kjsgen:create_mechanical_crafting", card["type"])
            elif recipe["type"] == "compacting":
                card = compiler.process(recipe, uid)
                self.assertEqual("kjsgen:create_compacting", card["type"])
                self.assertEqual(
                    v5.WEATHERED_PRESS,
                    card["slots"]["__machine_process_compacting"]["id"],
                )
            elif recipe["type"] == "sequenced_assembly":
                card = compiler.sequenced(recipe, uid)
                self.assertEqual("kjsgen:create_sequenced_assembly", card["type"])
            else:
                self.fail(f"unsupported v5 proposal type for {recipe_id}: {recipe['type']}")
            self.assertEqual(recipe_id, card["recipeId"])
            output_slot = (
                card["slots"]["output"]
                if "output" in card["slots"]
                else card["slots"]["output0"]
            )
            expected = v5.EXPECTED_OUTPUTS[recipe_id]
            if "x " in expected:
                count_text, expected_id = expected.split("x ", 1)
                expected_count = int(count_text)
            else:
                expected_id, expected_count = expected, 1
            self.assertEqual(expected_id, output_slot["id"])
            self.assertEqual(expected_count, output_slot.get("count", 1))

    def test_no_perimeter_rings_or_generic_hard_item_spam(self) -> None:
        for recipe_id, recipe in self.redesigned().items():
            pattern = recipe.get("pattern")
            if pattern:
                self.assertFalse(v5._filled_perimeter(pattern), recipe_id)
            text = repr(recipe)
            self.assertNotIn("mekanism:steel_casing", text, recipe_id)
            self.assertLessEqual(text.count("create:precision_mechanism"), 1, recipe_id)

    def test_missing_exact_recipe_fails_closed(self) -> None:
        data = self.data()
        missing = sorted(v5.ALL_REDESIGNED_IDS)[0]
        data["recipes"] = [recipe for recipe in data["recipes"] if recipe["id"] != missing]
        with self.assertRaises(KeyError):
            v5.apply(data)


if __name__ == "__main__":
    unittest.main()
