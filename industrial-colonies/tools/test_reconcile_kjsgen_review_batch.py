#!/usr/bin/env python3

from __future__ import annotations

import copy
import unittest

from tools.reconcile_kjsgen_review_batch import design_hash, reconcile
from tools.apply_recipe_review_acceptance import reconcile_from_acceptance


def card(uid: str, recipe_id: str, output: str, ingredient: str = "minecraft:iron_ingot"):
    return {
        "uid": uid,
        "type": "kjsgen:shaped",
        "recipeId": recipe_id,
        "comment": "[Test] Test card",
        "replaceRecipe": False,
        "slots": {
            "in0": {"kind": "ITEM", "id": ingredient},
            "output": {"kind": "ITEM", "id": output},
        },
        "params": {},
    }


def removal(uid: str, recipe_id: str):
    return {"uid": uid, "output": "", "input": "", "mod": "", "recipeId": recipe_id}


class ReconcileTests(unittest.TestCase):
    def test_preserves_approval_and_builds_only_new_or_redesigned_queue(self):
        approved = card("a", "test:approved_old", "test:approved_output")
        rejected_unchanged = card("b", "test:rejected_same", "test:rejected_same_output")
        rejected_changed = card("c", "test:rejected_changed", "test:rejected_changed_output")
        rejected_renamed = card("d", "test:rejected_renamed", "test:rejected_renamed_output")
        live = {
            "format": 1,
            "name": "default",
            "defaultTargetFile": "kjsgen_recipes.js",
            "exportComments": True,
            "reloadOnExport": True,
            "recipes": [approved, rejected_unchanged, rejected_changed, rejected_renamed],
            "removals": [
                removal("r-old", "test:crafting/approved_output"),
            ],
        }
        baseline = {
            "schema": 1,
            "project": "default",
            "recipes": copy.deepcopy(live["recipes"]),
            "removals": copy.deepcopy(live["removals"]),
            "retiredRecipeUids": [],
            "retiredRemovalUids": [],
        }
        approved_project = {
            "format": 1,
            "name": "approved recipes",
            "defaultTargetFile": "approved_recipes.js",
            "exportComments": True,
            "reloadOnExport": False,
            "recipes": [copy.deepcopy(approved), card("extra", "test:extra", "test:extra_output")],
            "removals": [],
        }
        reviews = {
            "schemaVersion": 1,
            "project": "default",
            "reviews": {
                approved["recipeId"]: {
                    "uid": approved["uid"], "status": "approved", "reason": "approved",
                    "note": "", "cardSha256": design_hash(approved),
                },
                rejected_unchanged["recipeId"]: {
                    "uid": rejected_unchanged["uid"], "status": "rejected", "reason": "manual",
                    "note": "no", "cardSha256": design_hash(rejected_unchanged),
                },
                rejected_changed["recipeId"]: {
                    "uid": rejected_changed["uid"], "status": "rejected", "reason": "manual",
                    "note": "change", "cardSha256": design_hash(rejected_changed),
                },
                rejected_renamed["recipeId"]: {
                    "uid": rejected_renamed["uid"], "status": "rejected", "reason": "manual",
                    "note": "change", "cardSha256": design_hash(rejected_renamed),
                },
            },
        }
        approved_alias = card("s-a", "test:approved_new_name", "test:approved_output", "minecraft:diamond")
        unchanged_source = copy.deepcopy(rejected_unchanged)
        changed_source = card("c", "test:rejected_changed", "test:rejected_changed_output", "minecraft:gold_ingot")
        renamed_changed = card("s-d", "test:rejected_renamed_v2", "test:rejected_renamed_output", "minecraft:copper_ingot")
        new_source = card("e", "test:new", "test:new_output")
        source = {
            "schema": 1,
            "project": "default",
            "recipes": [approved_alias, unchanged_source, changed_source, renamed_changed, new_source],
            "removals": [removal("r-new", "test:crafting/new_output")],
            "retiredRecipeUids": [],
            "retiredRemovalUids": [],
        }
        manifest = {
            "recipes": [
                {"id": "test:approved_new_name", "remove": []},
                {"id": "test:rejected_same", "remove": ["test:crafting/rejected_same_output"]},
                {"id": "test:rejected_changed", "remove": []},
                {"id": "test:rejected_renamed_v2", "remove": []},
                {"id": "test:new", "remove": ["test:crafting/new_output"]},
            ],
            "additional_removals": [],
        }
        source["removals"].append(
            removal("r-rejected", "test:crafting/rejected_same_output")
        )

        result = reconcile(live, baseline, approved_project, reviews, source, manifest)
        ids = [entry["recipeId"] for entry in result["managed"]["recipes"]]
        self.assertEqual(
            ids,
            ["test:rejected_changed", "test:rejected_renamed_v2", "test:new", "test:approved_old"],
        )
        self.assertNotIn("test:approved_new_name", ids)
        self.assertNotIn("test:rejected_same", ids)
        self.assertEqual(result["report"]["nextPending"], 3)
        self.assertEqual(result["report"]["nextManaged"], 4)
        self.assertEqual(result["report"]["archiveExtrasRemoved"], ["test:extra"])
        self.assertEqual(
            [entry["recipeId"] for entry in result["approved_project"]["recipes"]],
            ["test:approved_old"],
        )
        self.assertIn("test:crafting/approved_output", {
            entry["recipeId"] for entry in result["managed"]["removals"]
        })
        self.assertNotIn("test:crafting/rejected_same_output", {
            entry["recipeId"] for entry in result["managed"]["removals"]
        })
        self.assertEqual(result["project"]["recipes"], result["baseline"]["recipes"])
        self.assertEqual(result["acceptance"]["reviewed"], 4)
        self.assertEqual(
            [entry["recipeId"] for entry in result["acceptance"]["entries"]],
            [
                "test:approved_old",
                "test:rejected_same",
                "test:rejected_changed",
                "test:rejected_renamed",
            ],
        )
        self.assertEqual(
            [entry["id"] for entry in result["ownership_manifest"]["recipes"]],
            [
                "test:rejected_changed",
                "test:rejected_renamed_v2",
                "test:new",
                "test:approved_old",
            ],
        )
        removed_predecessor = card(
            "removed-predecessor",
            "test:removed_predecessor",
            "test:removed_predecessor_output",
        )
        previous_reviewed = copy.deepcopy(result["managed"])
        previous_reviewed["recipes"].append(removed_predecessor)
        with_predecessor = reconcile(
            live,
            baseline,
            approved_project,
            reviews,
            source,
            manifest,
            previous_reviewed,
        )
        self.assertIn(
            removed_predecessor["uid"],
            with_predecessor["managed"]["retiredRecipeUids"],
        )
        self.assertEqual(
            1, with_predecessor["report"]["predecessorRecipeUidsRetired"]
        )
        replay = reconcile_from_acceptance(
            result["acceptance"], result["managed"], source, manifest
        )
        self.assertEqual(replay["managed"], result["managed"])
        self.assertEqual(
            replay["ownership_manifest"], result["ownership_manifest"]
        )


if __name__ == "__main__":
    unittest.main()
