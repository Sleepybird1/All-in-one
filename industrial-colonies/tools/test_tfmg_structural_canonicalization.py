#!/usr/bin/env python3

from __future__ import annotations

import copy
import unittest

try:
    from tools import recipe_design_v2_tfmg_duplicate_canonicalization as policy
except ModuleNotFoundError:
    import recipe_design_v2_tfmg_duplicate_canonicalization as policy  # type: ignore


class StructuralCanonicalizationTests(unittest.TestCase):
    def test_retires_producer_and_rewrites_consumers_only(self) -> None:
        seed = {
            "recipes": [
                {
                    "id": "industrial_colonies:mekanism/steel_casing",
                    "input": "tfmg:steel_casing",
                    "output": "mekanism:steel_casing",
                    "remove": ["mekanism:steel_casing"],
                },
                {
                    "id": "industrial_colonies:test/sequenced",
                    "input": "2x mekanism:steel_casing",
                    "transitional": {"id": "mekanism:steel_casing", "count": 2},
                    "output": "test:machine",
                    "remove": ["test:machine"],
                    "depends_on": [
                        "industrial_colonies:mekanism/steel_casing",
                        "industrial_colonies:test/other_dependency",
                    ],
                    "steps": [
                        {"op": "deploying", "ingredient": "mekanism:steel_casing"}
                    ],
                },
            ],
            "ingredient_replacements": {},
            "additional_removals": [],
            "preserve_recipe_ids": [],
            "exclude_outputs": [],
        }

        policy.apply(seed)

        recipes = {recipe["id"]: recipe for recipe in seed["recipes"]}
        self.assertNotIn("industrial_colonies:mekanism/steel_casing", recipes)
        consumer = recipes["industrial_colonies:test/sequenced"]
        self.assertEqual("2x tfmg:steel_frame", consumer["input"])
        self.assertEqual("tfmg:steel_frame", consumer["transitional"]["id"])
        self.assertEqual("tfmg:steel_frame", consumer["steps"][0]["ingredient"])
        self.assertEqual(
            ["industrial_colonies:test/other_dependency"],
            consumer["depends_on"],
        )
        self.assertEqual("test:machine", consumer["output"])
        self.assertIn("mekanism:steel_casing", seed["additional_removals"])
        self.assertIn("mekanism:steel_casing", seed["exclude_outputs"])
        self.assertEqual(
            "tfmg:steel_frame",
            seed["ingredient_replacements"]["mekanism:steel_casing"],
        )

        before = copy.deepcopy(seed)
        policy.apply(seed)
        self.assertEqual(before, seed)


if __name__ == "__main__":
    unittest.main()
