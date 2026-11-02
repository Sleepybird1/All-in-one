#!/usr/bin/env python3
"""Focused tests for the v3 TFMG steel-frame canonicalization policy."""

from __future__ import annotations

from copy import deepcopy
import unittest

import recipe_design_v3_mekanism as v3


class SteelFramePolicyTests(unittest.TestCase):
    def test_approved_consumer_is_canonicalized_without_losing_approval(self) -> None:
        data = {
            "recipes": [
                {
                    "id": v3.RETIRED_STEEL_CASING_RECIPE_ID,
                    "type": "compacting",
                    "inputs": ["2x tfmg:steel_frame"],
                    "output": v3.RETIRED_STEEL_CASING,
                    "remove": [v3.RETIRED_STEEL_CASING, "mekanism:legacy_casing"],
                },
                {
                    "id": "industrial_colonies:test/approved_consumer",
                    "review_status": "approved",
                    "input": v3.RETIRED_STEEL_CASING,
                    "transitional": {"id": v3.RETIRED_STEEL_CASING, "count": 1},
                    "inputs": [
                        f"4x {v3.RETIRED_STEEL_CASING}",
                        {"item": v3.RETIRED_STEEL_CASING, "count": 2},
                    ],
                    "key": {"S": v3.RETIRED_STEEL_CASING, "K": "minecraft:stone"},
                    "steps": [
                        {
                            "op": "deploying",
                            "ingredient": f"2x {v3.RETIRED_STEEL_CASING}",
                        }
                    ],
                    "depends_on": [
                        v3.RETIRED_STEEL_CASING_RECIPE_ID,
                        "industrial_colonies:test/kept_dependency",
                    ],
                    "output": "mekanism:test_machine",
                },
            ],
            "additional_removals": ["minecraft:stick"],
            "preserve_recipe_ids": [
                v3.RETIRED_STEEL_CASING,
                "industrial_colonies:test/kept_recipe",
            ],
            "exclude_outputs": [],
            "ingredient_replacements": {},
        }

        v3._retire_steel_casing(data)
        v3._canonicalize_steel_frame_consumers(data)

        self.assertEqual(len(data["recipes"]), 1)
        recipe = data["recipes"][0]
        self.assertEqual(recipe["review_status"], "approved")
        self.assertEqual(recipe["input"], v3.CANONICAL_STEEL_FRAME)
        self.assertEqual(recipe["transitional"]["id"], v3.CANONICAL_STEEL_FRAME)
        self.assertEqual(recipe["inputs"][0], "4x tfmg:steel_frame")
        self.assertEqual(recipe["inputs"][1]["item"], v3.CANONICAL_STEEL_FRAME)
        self.assertEqual(recipe["key"]["S"], v3.CANONICAL_STEEL_FRAME)
        self.assertEqual(recipe["steps"][0]["ingredient"], "2x tfmg:steel_frame")
        self.assertEqual(
            recipe["depends_on"], ["industrial_colonies:test/kept_dependency"]
        )
        self.assertEqual(recipe["output"], "mekanism:test_machine")

        self.assertIn(v3.RETIRED_STEEL_CASING, data["additional_removals"])
        self.assertIn("mekanism:legacy_casing", data["additional_removals"])
        self.assertNotIn(v3.RETIRED_STEEL_CASING, data["preserve_recipe_ids"])
        self.assertIn("industrial_colonies:test/kept_recipe", data["preserve_recipe_ids"])
        self.assertIn(v3.RETIRED_STEEL_CASING, data["exclude_outputs"])
        self.assertEqual(
            data["ingredient_replacements"][v3.RETIRED_STEEL_CASING],
            v3.CANONICAL_STEEL_FRAME,
        )

        first_pass = deepcopy(data)
        v3._retire_steel_casing(data)
        v3._canonicalize_steel_frame_consumers(data)
        self.assertEqual(data, first_pass)

    def test_rigid_batches_no_longer_expect_a_steel_casing_producer(self) -> None:
        data = {
            "recipes": [
                {
                    "id": "industrial_colonies:mekanism/induction/casing",
                    "type": "shaped",
                    "output": "mekanism:induction_casing",
                },
                {
                    "id": "industrial_colonies:mekanism_nuclear/sps_casing_batch",
                    "type": "shaped",
                    "output": "mekanism:sps_casing",
                },
            ]
        }

        v3._rigid_casing_batches(data)

        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        self.assertNotIn(v3.RETIRED_STEEL_CASING_RECIPE_ID, v3.RIGID_CASING_IDS)
        self.assertEqual(set(recipes), set(v3.RIGID_CASING_IDS))
        induction = recipes["industrial_colonies:mekanism/induction/casing"]
        self.assertIn("4x tfmg:steel_frame", induction["inputs"])
        self.assertNotIn("4x mekanism:steel_casing", induction["inputs"])

    def test_basic_tier_installer_preserves_reviewed_frame_free_sequence(self) -> None:
        data = {"recipes": [{"id": recipe_id} for recipe_id in v3.INSTALLER_IDS]}

        v3._tier_installers(data)

        recipes = {recipe["id"]: recipe for recipe in data["recipes"]}
        basic = recipes["industrial_colonies:mekanism/tier_installer/basic"]
        deploying_ingredients = [
            step["ingredient"]
            for step in basic["steps"]
            if step["op"] == "deploying"
        ]
        self.assertNotIn(v3.CANONICAL_STEEL_FRAME, deploying_ingredients)
        self.assertEqual(len(basic["steps"]), 8)
        self.assertEqual(
            basic["steps"][-1],
            {"op": "pressing", "machine": v3.INDUSTRIAL_PRESS},
        )

    def test_redundant_process_machines_retire_but_stock_ids_stay_disabled(self) -> None:
        data = {
            "recipes": [
                {
                    "id": recipe_id,
                    "output": output,
                    "remove": [output],
                }
                for recipe_id, output in v3.RETIRED_PROCESS_MACHINE_RECIPES.items()
            ]
            + [
                {
                    "id": "industrial_colonies:test/kept_machine",
                    "output": "mekanism:crusher",
                }
            ],
            "additional_removals": [],
            "preserve_recipe_ids": list(v3.RETIRED_PROCESS_MACHINE_OUTPUTS),
            "exclude_outputs": [],
        }

        v3._retire_redundant_process_machines(data)

        self.assertEqual(
            [recipe["id"] for recipe in data["recipes"]],
            ["industrial_colonies:test/kept_machine"],
        )
        self.assertTrue(
            v3.RETIRED_PROCESS_MACHINE_OUTPUTS.issubset(data["additional_removals"])
        )
        self.assertTrue(
            v3.RETIRED_PROCESS_MACHINE_OUTPUTS.issubset(data["exclude_outputs"])
        )
        self.assertTrue(
            v3.RETIRED_PROCESS_MACHINE_OUTPUTS.isdisjoint(data["preserve_recipe_ids"])
        )

        first_pass = deepcopy(data)
        v3._retire_redundant_process_machines(data)
        self.assertEqual(data, first_pass)


if __name__ == "__main__":
    unittest.main()
