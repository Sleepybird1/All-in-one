#!/usr/bin/env python3
"""Focused mutation tests for merged KJSGen ownership validation."""

from __future__ import annotations

import copy
import unittest
import uuid

import validate_staged_kjsgen_project as validator


def fixture_uid(label: str) -> str:
    try:
        return str(uuid.UUID(label))
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"industrial-colonies-staged:{label}"))


def card(uid: str, recipe_id: str | None, output: str | None) -> dict:
    value = {
        "uid": fixture_uid(uid),
        "type": "kjsgen:shaped",
        "slots": {},
        "params": {},
    }
    if recipe_id is not None:
        value["recipeId"] = recipe_id
    if output is not None:
        value["slots"]["output"] = {"kind": "ITEM", "id": output}
    return value


def removal(uid: str, recipe_id: str | None) -> dict:
    value = {"uid": fixture_uid(uid), "output": "", "input": "", "mod": ""}
    if recipe_id is not None:
        value["recipeId"] = recipe_id
    return value


class StagedProjectValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.managed_card = card(
            "managed-card", "industrial_colonies:test/machine", "example:machine"
        )
        self.managed_removal = removal("managed-removal", "example:machine")
        self.managed = {
            "recipes": [self.managed_card],
            "removals": [self.managed_removal],
        }
        self.manifest = {
            "recipes": [
                {
                    "id": "industrial_colonies:test/machine",
                    "exclusive_output": True,
                }
            ]
        }

    def failures(self, staged: dict) -> list[str]:
        errors, _ = validator.validate(self.managed, staged, self.manifest)
        return errors

    def test_unfinished_user_drafts_are_preserved(self) -> None:
        staged = copy.deepcopy(self.managed)
        staged["recipes"].append(card("user-draft", None, None))
        self.assertEqual([], self.failures(staged))

    def test_unrelated_user_recipe_is_preserved(self) -> None:
        staged = copy.deepcopy(self.managed)
        staged["recipes"].append(card("user-card", None, "example:user_widget"))
        self.assertEqual([], self.failures(staged))

    def test_edited_active_managed_card_fails_closed(self) -> None:
        staged = copy.deepcopy(self.managed)
        staged["recipes"][0]["comment"] = "edited"
        self.assertTrue(self.failures(staged))

    def test_missing_active_managed_removal_fails_closed(self) -> None:
        staged = copy.deepcopy(self.managed)
        staged["removals"] = []
        self.assertTrue(self.failures(staged))

    def test_user_card_cannot_duplicate_exclusive_output(self) -> None:
        staged = copy.deepcopy(self.managed)
        staged["recipes"].append(card("user-card", None, "example:machine"))
        self.assertTrue(self.failures(staged))

    def test_user_card_cannot_duplicate_managed_recipe_id(self) -> None:
        staged = copy.deepcopy(self.managed)
        staged["recipes"].append(
            card("user-card", "industrial_colonies:test/machine", "example:other")
        )
        self.assertTrue(self.failures(staged))

    def test_vat_results_slot_is_protected(self) -> None:
        managed = copy.deepcopy(self.managed)
        managed["recipes"][0]["slots"] = {
            "results0": {"kind": "ITEM", "id": "example:machine"}
        }
        staged = copy.deepcopy(managed)
        errors, _ = validator.validate(managed, staged, self.manifest)
        self.assertEqual([], errors)

    def test_duplicate_exact_removal_fails_closed(self) -> None:
        staged = copy.deepcopy(self.managed)
        staged["removals"].append(removal("user-removal", "example:machine"))
        self.assertTrue(self.failures(staged))

    def test_cross_kind_uid_collision_fails_closed(self) -> None:
        staged = copy.deepcopy(self.managed)
        shared = staged["recipes"][0]["uid"]
        staged["removals"][0]["uid"] = shared.upper()
        self.assertTrue(self.failures(staged))

    def test_case_only_managed_uid_edit_fails_closed(self) -> None:
        staged = copy.deepcopy(self.managed)
        staged["recipes"][0]["uid"] = staged["recipes"][0]["uid"].upper()
        self.assertTrue(self.failures(staged))

    def test_invalid_user_uid_fails_closed(self) -> None:
        staged = copy.deepcopy(self.managed)
        invalid = card("invalid-user", None, "example:user_widget")
        invalid["uid"] = "not-a-uuid"
        staged["recipes"].append(invalid)
        self.assertTrue(self.failures(staged))


if __name__ == "__main__":
    unittest.main()
