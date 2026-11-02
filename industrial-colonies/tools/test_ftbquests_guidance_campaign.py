#!/usr/bin/env python3
"""Focused regression tests for the native FTB Quests guidance campaign."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from generate_ftbquests_native import (
    generate,
    validate_exploration_source,
    validate_guidance_source,
)
from validate_ftbquests_native import (
    DEFAULT_ENDGAME_SOURCE,
    DEFAULT_EXPLORATION_SOURCE,
    DEFAULT_GUIDANCE_SOURCE,
    DEFAULT_ITEM_CATALOG,
    DEFAULT_MANIFEST,
    DEFAULT_QUEST_ROOT,
    DEFAULT_RECIPE_CATALOG,
    EXPECTED_ENDGAME_CHAPTER_ID,
    EXPECTED_ENDGAME_QUEST_IDS,
    PROJECT_ROOT,
    validate,
)


class FtbQuestsGuidanceCampaignTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.guidance = json.loads(DEFAULT_GUIDANCE_SOURCE.read_text(encoding="utf-8"))
        self.exploration = json.loads(
            DEFAULT_EXPLORATION_SOURCE.read_text(encoding="utf-8")
        )

    def write_guidance(self, root: Path, value: dict) -> Path:
        value = copy.deepcopy(value)
        if "chapter_extension" in value:
            value["chapter_extension"]["path"] = str(
                PROJECT_ROOT / "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json"
            )
        path = root / "guidance.json"
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def write_exploration(self, root: Path, value: dict) -> Path:
        path = root / "exploration.json"
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def test_current_campaign_passes_full_validation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            output = root / "quests"
            manifest = root / "manifest.json"
            generate(DEFAULT_GUIDANCE_SOURCE, DEFAULT_ENDGAME_SOURCE, output, manifest)
            errors: list[str] = []
            details = validate(
                project=PROJECT_ROOT,
                guidance_source=DEFAULT_GUIDANCE_SOURCE,
                endgame_source=DEFAULT_ENDGAME_SOURCE,
                quest_root=output,
                manifest_path=manifest,
                item_catalog=DEFAULT_ITEM_CATALOG,
                recipe_catalog=DEFAULT_RECIPE_CATALOG,
                errors=errors,
            )
        self.assertEqual([], errors)
        self.assertEqual(70, details["guidance_quest_count"])
        self.assertEqual(12, details["exploration_quest_count"])
        self.assertEqual(10, details["orbital_quest_count"])
        self.assertEqual(29, details["planetary_quest_count"])
        self.assertEqual(124, details["quest_count"])
        self.assertEqual(241, details["item_task_count"])
        self.assertEqual(8, details["structure_task_count"])
        self.assertEqual(7, details["advancement_task_count"])
        self.assertEqual(256, details["total_task_count"])
        self.assertEqual(170, details["dependency_count"])

    def test_post_diesel_chapters_and_network_observation_are_present(self) -> None:
        validated = validate_guidance_source(DEFAULT_GUIDANCE_SOURCE)
        counts = {
            chapter["filename"]: len(chapter["quests"])
            for chapter in validated["chapters"]
        }
        self.assertEqual(
            {
                "factory_foundations": 30,
                "electrical_manufacturing": 7,
                "digital_logistics": 6,
                "mekanized_industry": 8,
                "high_energy_grid": 10,
                "nuclear_engineering": 9,
            },
            counts,
        )
        high_energy = next(
            chapter
            for chapter in validated["chapters"]
            if chapter["filename"] == "high_energy_grid"
        )
        network = next(
            quest
            for quest in high_energy["quests"]
            if quest["key"] == "physical_network_upgrade"
        )
        self.assertEqual(
            [{"type": "item", "item": "mekanism:ultimate_logistical_transporter", "count": 8}],
            network["tasks"],
        )
        self.assertIn("mekanized_industry:basic_transmitter_suite", network["dependencies"])
        mekanized = next(
            chapter
            for chapter in validated["chapters"]
            if chapter["filename"] == "mekanized_industry"
        )
        first_factory = next(
            quest for quest in mekanized["quests"] if quest["key"] == "first_basic_factory"
        )
        self.assertEqual(
            [
                {"type": "item", "item": "mekanism:basic_enriching_factory", "count": 1},
                {"type": "item", "item": "mekanism:enrichment_chamber", "count": 1},
                {"type": "item", "item": "mekanism:basic_tier_installer", "count": 1},
            ],
            first_factory["tasks"],
        )
        description = first_factory["description"][0].lower()
        self.assertIn("right-click", description)
        self.assertIn("installer is consumed", description)
        self.assertIn("preserves", description)
        self.assertIn("direct factory recipes are disabled", description)

    def test_exploration_chapter_uses_exact_native_task_mix(self) -> None:
        chapter = json.loads(
            (
                DEFAULT_QUEST_ROOT / "chapters" / "dungeon_exploration.snbt"
            ).read_text(encoding="utf-8")
        )
        task_types = [
            task["type"]
            for quest in chapter["quests"]
            for task in quest["tasks"]
        ]
        self.assertEqual(12, len(chapter["quests"]))
        self.assertEqual(4, task_types.count("item"))
        self.assertEqual(8, task_types.count("structure"))
        self.assertEqual(1, task_types.count("advancement"))
        self.assertTrue(all(not quest.get("rewards") for quest in chapter["quests"]))

    def test_first_blast_furnace_guidance_uses_only_presteel_structure(self) -> None:
        quest = next(
            quest
            for quest in self.guidance["chapters"][0]["quests"]
            if quest.get("key") == "blast_furnace"
        )
        tasks = {task["item"]: task["count"] for task in quest["tasks"]}
        self.assertEqual(16, tasks.get("tfmg:fireproof_bricks"))
        self.assertEqual(8, tasks.get("tfmg:fireproof_brick_reinforcement"))
        self.assertNotIn("tfmg:blast_furnace_reinforcement", tasks)

    def test_unknown_exploration_structure_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.exploration)
        mutated["chapter"]["quests"][1]["tasks"][0]["structure"] = (
            "missing_mod:imaginary_dungeon"
        )
        with tempfile.TemporaryDirectory() as raw:
            source = self.write_exploration(Path(raw), mutated)
            with self.assertRaisesRegex(ValueError, "observation tasks changed"):
                validate_exploration_source(source)

    def test_boss_and_apotheosis_exploration_objectives_are_rejected(self) -> None:
        for excluded in ("Defeat the boss.", "Acquire an Apotheosis affix."):
            mutated = copy.deepcopy(self.exploration)
            mutated["chapter"]["quests"][0]["description"].append(excluded)
            with tempfile.TemporaryDirectory() as raw:
                source = self.write_exploration(Path(raw), mutated)
                with self.assertRaisesRegex(ValueError, "must not contain"):
                    validate_exploration_source(source)

    def test_original_capstone_ids_are_preserved(self) -> None:
        chapter = json.loads(
            (DEFAULT_QUEST_ROOT / "chapters" / "industrial_progression.snbt").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(EXPECTED_ENDGAME_CHAPTER_ID, chapter["id"])
        self.assertEqual(
            list(EXPECTED_ENDGAME_QUEST_IDS.values()),
            [quest["id"] for quest in chapter["quests"]],
        )

    def test_checkbox_reward_and_consumption_fields_are_rejected(self) -> None:
        mutations = []
        checkbox = copy.deepcopy(self.guidance)
        checkbox["chapters"][0]["quests"][0]["tasks"][0]["type"] = "checkmark"
        mutations.append(checkbox)
        reward = copy.deepcopy(self.guidance)
        reward["chapters"][0]["quests"][0]["rewards"] = [
            {"type": "item", "item": "minecraft:diamond"}
        ]
        mutations.append(reward)
        consume = copy.deepcopy(self.guidance)
        consume["chapters"][0]["quests"][0]["tasks"][0]["consume_items"] = True
        mutations.append(consume)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for index, mutation in enumerate(mutations):
                with self.subTest(index=index):
                    source = self.write_guidance(root, mutation)
                    with self.assertRaises(ValueError):
                        validate_guidance_source(source)

    def test_dependency_cycle_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.guidance)
        quests = mutated["chapters"][0]["quests"]
        quests[0]["dependencies"] = [quests[-1]["key"]]
        with tempfile.TemporaryDirectory() as raw:
            source = self.write_guidance(Path(raw), mutated)
            with self.assertRaisesRegex(ValueError, "dependency cycle"):
                validate_guidance_source(source)

    def test_unregistered_task_item_fails_production_validation(self) -> None:
        mutated = copy.deepcopy(self.guidance)
        mutated["chapters"][0]["quests"][0]["tasks"][0]["item"] = (
            "missing_mod:imaginary_pickaxe"
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = self.write_guidance(root, mutated)
            output = root / "quests"
            manifest = root / "manifest.json"
            generate(source, DEFAULT_ENDGAME_SOURCE, output, manifest)
            errors: list[str] = []
            validate(
                project=PROJECT_ROOT,
                guidance_source=source,
                endgame_source=DEFAULT_ENDGAME_SOURCE,
                quest_root=output,
                manifest_path=manifest,
                item_catalog=DEFAULT_ITEM_CATALOG,
                recipe_catalog=DEFAULT_RECIPE_CATALOG,
                errors=errors,
            )
            self.assertTrue(
                any("absent from the installed registry" in error for error in errors),
                errors,
            )
            self.assertTrue(
                any("no audited, managed, stock" in error for error in errors),
                errors,
            )

    def test_deployer_cannot_be_guided_before_brass(self) -> None:
        mutated = copy.deepcopy(self.guidance)
        deployer = next(
            quest
            for quest in mutated["chapters"][0]["quests"]
            if quest["key"] == "automated_assembly"
        )
        deployer["dependencies"] = ["material_handling"]
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = self.write_guidance(root, mutated)
            output = root / "quests"
            manifest = root / "manifest.json"
            generate(source, DEFAULT_ENDGAME_SOURCE, output, manifest)
            errors: list[str] = []
            validate(
                project=PROJECT_ROOT,
                guidance_source=source,
                endgame_source=DEFAULT_ENDGAME_SOURCE,
                quest_root=output,
                manifest_path=manifest,
                item_catalog=DEFAULT_ITEM_CATALOG,
                recipe_catalog=DEFAULT_RECIPE_CATALOG,
                errors=errors,
            )
            self.assertTrue(
                any("automated_assembly lost physical dependencies" in error for error in errors),
                errors,
            )


if __name__ == "__main__":
    unittest.main()
