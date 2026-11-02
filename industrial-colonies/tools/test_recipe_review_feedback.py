#!/usr/bin/env python3

from __future__ import annotations

import copy
import unittest

import recipe_review_feedback as feedback


def card(recipe_id: str = "industrial_colonies:test") -> dict:
    return {
        "uid": "ignored-uid",
        "type": "kjsgen:create_mechanical_crafting",
        "recipeId": recipe_id,
        "comment": "ignored comment",
        "replaceRecipe": False,
        "slots": {
            "cell_0_0": {"kind": "ITEM", "id": "minecraft:iron_ingot"},
            "output": {"kind": "ITEM", "id": "minecraft:iron_block"},
        },
        "params": {"gridW": "1", "gridH": "1"},
    }


def sidecar(recipe: dict, **changes) -> dict:
    record = {
        "uid": "visible-card-uid",
        "status": "approved",
        "reason": "approved",
        "note": "looks good",
        "cardSha256": feedback.design_hash(recipe),
    }
    record.update(changes)
    return {
        "schemaVersion": 1,
        "project": "default",
        "reviews": {recipe["recipeId"]: record},
    }


class RecipeReviewFeedbackTests(unittest.TestCase):
    def test_matching_review_is_effectively_approved(self) -> None:
        recipe = card()
        report = feedback.build_report(sidecar(recipe), {"recipes": [recipe]})
        self.assertEqual("approved", report["reviews"][0]["effectiveStatus"])
        self.assertEqual(1, report["counts"]["approved"])

    def test_shape_change_makes_old_approval_stale(self) -> None:
        visible = card()
        managed = copy.deepcopy(visible)
        managed["slots"]["cell_0_0"]["id"] = "minecraft:copper_ingot"
        report = feedback.build_report(sidecar(visible), {"recipes": [managed]})
        self.assertTrue(report["reviews"][0]["stale"])
        self.assertEqual("pending", report["reviews"][0]["effectiveStatus"])

    def test_comment_and_uid_do_not_change_design_hash(self) -> None:
        first = card()
        second = copy.deepcopy(first)
        second["uid"] = "different"
        second["comment"] = "different"
        self.assertEqual(feedback.design_hash(first), feedback.design_hash(second))

    def test_unknown_review_is_reported_without_failure(self) -> None:
        reviewed = card("industrial_colonies:retired")
        managed = card("industrial_colonies:active")
        report = feedback.build_report(sidecar(reviewed), {"recipes": [managed]})
        self.assertTrue(report["reviews"][0]["unknown"])
        self.assertEqual(1, report["counts"]["unknown"])

    def test_malformed_digest_is_rejected(self) -> None:
        recipe = card()
        malformed = sidecar(recipe, cardSha256="bad")
        with self.assertRaisesRegex(feedback.FeedbackError, "cardSha256"):
            feedback.build_report(malformed, {"recipes": [recipe]})

    def test_rows_are_sorted_by_recipe_id(self) -> None:
        a = card("industrial_colonies:a")
        b = card("industrial_colonies:b")
        reviews = sidecar(b)
        reviews["reviews"][a["recipeId"]] = sidecar(a)["reviews"][a["recipeId"]]
        report = feedback.build_report(reviews, {"recipes": [b, a]})
        self.assertEqual(
            ["industrial_colonies:a", "industrial_colonies:b"],
            [row["recipeId"] for row in report["reviews"]],
        )


if __name__ == "__main__":
    unittest.main()
