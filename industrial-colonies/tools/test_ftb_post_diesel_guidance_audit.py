#!/usr/bin/env python3
"""Focused mutation tests for the implemented post-Diesel quest campaign."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_ftb_post_diesel_guidance_audit as validator  # noqa: E402


class PostDieselGuidanceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_object(validator.DEFAULT_PLAN)
        cls.context = {
            "registry_ids": validator.parse_registry(validator.DEFAULT_ITEMS),
            "managed": validator.load_object(validator.DEFAULT_MANIFEST),
            "physical": validator.load_object(validator.DEFAULT_PHYSICAL),
            "assignments": validator.load_object(validator.DEFAULT_ASSIGNMENTS),
            "installed_recipes": validator.installed_recipe_map(validator.DEFAULT_RECIPES),
            "foundations": validator.load_object(validator.DEFAULT_FOUNDATIONS),
            "dungeon": validator.load_object(validator.DEFAULT_DUNGEON),
            "endgame": validator.load_object(validator.DEFAULT_ENDGAME),
        }

    def errors(self, plan: dict) -> list[str]:
        return validator.validate_plan(plan, **self.context)

    def assert_rejected(self, plan: dict, fragment: str) -> None:
        errors = self.errors(plan)
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected rejection containing {fragment!r}; got {errors[:6]}",
        )

    def test_reviewed_plan_passes(self) -> None:
        self.assertEqual([], self.errors(self.plan))

    def test_reward_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["campaign_contract"]["rewards"] = True
        self.assert_rejected(plan, "rewards=false")

    def test_cycle_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["chapters"][0]["quests"][0]["dependencies"] = [
            plan["chapters"][0]["quests"][-1]["key"]
        ]
        self.assert_rejected(plan, "dependency cycle")

    def test_task_order_topology_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        quest = next(
            quest
            for chapter in plan["chapters"]
            for quest in chapter["quests"]
            if len(quest["tasks"]) > 1
        )
        quest["tasks"] = list(reversed(quest["tasks"]))
        self.assert_rejected(plan, "chapter/quest/task topology changed")

    def test_unknown_item_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        old = plan["chapters"][0]["quests"][0]["tasks"][0]["item"]
        new = "industrial_colonies:not_registered"
        plan["chapters"][0]["quests"][0]["tasks"][0]["item"] = new
        plan["objective_evidence"][new] = plan["objective_evidence"].pop(old)
        self.assert_rejected(plan, "absent from runtime registry")

    def test_deferred_p2p_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        item = "ae2:item_p2p_tunnel"
        plan["chapters"][0]["quests"][0]["tasks"].append({"item": item, "count": 1})
        plan["objective_evidence"][item] = {
            "kind": "managed_recipe",
            "recipe_id": "industrial_colonies:auto/ae2/item_p2p_tunnel",
        }
        self.assert_rejected(plan, "deferred items leaked")

    def test_endgame_dependency_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["preserved_artifacts"]["existing_endgame_chapter"]["dependencies"][
            "industrial_star"
        ] = []
        self.assert_rejected(plan, "mutates the endgame dependency chain")

    def test_factory_drain_guidance_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        chapter = next(row for row in plan["chapters"] if row["key"] == "mekanized_industry")
        quest = next(row for row in chapter["quests"] if row["key"] == "first_basic_factory")
        quest["intent"] = "Build the first Basic Factory."
        self.assert_rejected(plan, "lost required phrase")

    def test_factory_installer_evidence_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["objective_evidence"]["mekanism:basic_enriching_factory"]["base_item"] = (
            "mekanism:crusher"
        )
        self.assert_rejected(plan, "Tier Installer upgrade evidence drifted")

    def test_managed_tier_installer_reference_migrations_are_locked(self) -> None:
        for item in validator.TIER_INSTALLER_REFERENCE_MIGRATIONS:
            with self.subTest(item=item):
                plan = copy.deepcopy(self.plan)
                plan["objective_evidence"][item]["recipe_id"] = "mekanism:tier_installer/basic"
                self.assert_rejected(plan, "semantic recipe reference migration drifted")

    def test_all_six_semantic_reference_migrations_are_locked(self) -> None:
        for item, expected in validator.SEMANTIC_REFERENCE_MIGRATIONS.items():
            with self.subTest(item=item):
                plan = copy.deepcopy(self.plan)
                plan["objective_evidence"][item]["recipe_id"] = (
                    f"industrial_colonies:auto/{item.replace(':', '/', 1)}"
                )
                self.assert_rejected(plan, "semantic recipe reference migration drifted")

    def test_reviewed_batch_artifact_mapping_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["objective_evidence"]["mekanism:isotopic_centrifuge"]["artifact"] = (
            "AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.plan.json"
        )
        self.assert_rejected(plan, "semantic recipe reference migration drifted")

    def test_digital_core_reference_migrations_are_locked(self) -> None:
        for item in validator.IMPLEMENTED_AUDIT_REFERENCE_MIGRATIONS:
            if not item.startswith("ae2:"):
                continue
            with self.subTest(item=item):
                plan = copy.deepcopy(self.plan)
                plan["objective_evidence"][item]["recipe_id"] = (
                    f"industrial_colonies:auto/{item.replace(':', '/', 1)}"
                )
                self.assert_rejected(plan, "semantic recipe reference migration drifted")

    def test_pre_nuclear_reference_migrations_are_locked(self) -> None:
        for item in validator.IMPLEMENTED_AUDIT_REFERENCE_MIGRATIONS:
            if not item.startswith("mekanism:"):
                continue
            with self.subTest(item=item):
                plan = copy.deepcopy(self.plan)
                plan["objective_evidence"][item]["artifact"] = (
                    "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json"
                )
                self.assert_rejected(plan, "semantic recipe reference migration drifted")

    def test_stock_utility_reference_migrations_are_locked(self) -> None:
        for item in validator.STOCK_UTILITY_REFERENCE_MIGRATIONS:
            with self.subTest(item=item):
                plan = copy.deepcopy(self.plan)
                plan["objective_evidence"][item]["assignment_node"] = "CR01 — Wrong Node"
                self.assert_rejected(plan, "semantic recipe reference migration drifted")

    def test_big_reactor_reference_migrations_are_locked(self) -> None:
        for item in validator.BIG_REACTOR_REFERENCE_MIGRATIONS:
            with self.subTest(item=item):
                plan = copy.deepcopy(self.plan)
                plan["objective_evidence"][item]["recipe_id"] = (
                    f"industrial_colonies:auto/{item.replace(':', '/', 1)}"
                )
                self.assert_rejected(plan, "semantic recipe reference migration drifted")

    def test_any_retired_automatic_evidence_reference_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["objective_evidence"]["ae2:charger"]["recipe_id"] = (
            "industrial_colonies:auto/ae2/charger"
        )
        self.assert_rejected(plan, "retired automatic recipe references survive")


if __name__ == "__main__":
    unittest.main()
