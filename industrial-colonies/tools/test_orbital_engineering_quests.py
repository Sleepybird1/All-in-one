#!/usr/bin/env python3
"""Mutation tests for the non-gating Orbital Engineering quest chapter."""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from generate_ftbquests_native import (
    DEFAULT_MANIFEST,
    DEFAULT_ORBITAL_SOURCE,
    DEFAULT_OUTPUT,
    EXPECTED_ORBITAL_KEYS,
    ORBITAL_FILENAME,
    stable_code,
    validate_orbital_source,
)
from validate_ftbquests_native import DEFAULT_INSTANCE, DEFAULT_ITEM_CATALOG
from validate_orbital_engineering_quests import PROJECT_ROOT, validate


class OrbitalEngineeringQuestTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.source = json.loads(
            DEFAULT_ORBITAL_SOURCE.read_text(encoding="utf-8")
        )

    def write_source(self, root: Path, value: dict) -> Path:
        path = root / "orbital.json"
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def test_current_source_has_exact_post_star_route(self) -> None:
        chapter = validate_orbital_source(DEFAULT_ORBITAL_SOURCE)["chapter"]
        self.assertEqual(EXPECTED_ORBITAL_KEYS, [quest["key"] for quest in chapter["quests"]])
        self.assertEqual(
            ["industrial_progression:industrial_star"],
            chapter["quests"][0]["dependencies"],
        )
        by_key = {quest["key"]: quest for quest in chapter["quests"]}
        self.assertEqual(
            {
                "hose_anchor": ["orbital_flight_computer"],
                "engine_pipes": ["hose_anchor"],
                "engine_nozzle": ["engine_pipes"],
                "thruster_mount": ["engine_nozzle"],
                "habitat_life_support": ["thruster_mount"],
                "physics_assembler": ["thruster_mount", "habitat_life_support"],
                "navigation_suite": ["physics_assembler"],
                "docking_connector": ["navigation_suite"],
                "station_materials": ["docking_connector"],
            },
            {
                key: by_key[key]["dependencies"]
                for key in (
                    "hose_anchor",
                    "engine_pipes",
                    "engine_nozzle",
                    "thruster_mount",
                    "habitat_life_support",
                    "physics_assembler",
                    "navigation_suite",
                    "docking_connector",
                    "station_materials",
                )
            },
        )
        self.assertEqual(
            [
                "ad_astra:oxygen_distributor",
                "ad_astra:oxygen_sensor",
                "ad_astra:vent",
                "ad_astra:airlock",
            ],
            [task["item"] for task in by_key["habitat_life_support"]["tasks"]],
        )
        self.assertEqual(
            [
                "simulated:velocity_sensor",
                "simulated:gimbal_sensor",
                "simulated:optical_sensor",
                "simulated:navigation_table",
                "rocketnautics:sputnik",
            ],
            [task["item"] for task in by_key["navigation_suite"]["tasks"]],
        )
        self.assertEqual(
            [
                "ad_astra:steel_plating",
                "ad_astra:steel_panel",
                "ad_astra:cable_duct",
                "ad_astra:fluid_pipe_duct",
            ],
            [task["item"] for task in by_key["station_materials"]["tasks"]],
        )
        self.assertEqual([6], [task["count"] for task in by_key["docking_connector"]["tasks"]])
        self.assertEqual(
            [128, 32, 16, 16],
            [task["count"] for task in by_key["station_materials"]["tasks"]],
        )

    def test_current_generated_chapter_passes_focused_validation(self) -> None:
        errors = validate(
            project=PROJECT_ROOT,
            source=DEFAULT_ORBITAL_SOURCE,
            quest_root=DEFAULT_OUTPUT,
            manifest_path=DEFAULT_MANIFEST,
            item_catalog=DEFAULT_ITEM_CATALOG,
            instance=DEFAULT_INSTANCE,
        )
        self.assertEqual([], errors)

    def test_entry_dependency_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.source)
        mutated["chapter"]["quests"][0]["dependencies"] = []
        with tempfile.TemporaryDirectory() as raw:
            source = self.write_source(Path(raw), mutated)
            with self.assertRaisesRegex(ValueError, "dependencies changed"):
                validate_orbital_source(source)

    def test_wrong_component_item_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.source)
        mutated["chapter"]["quests"][2]["tasks"][0]["item"] = (
            "rocketnautics:rocket_thruster"
        )
        with tempfile.TemporaryDirectory() as raw:
            source = self.write_source(Path(raw), mutated)
            with self.assertRaisesRegex(ValueError, "observation item changed"):
                validate_orbital_source(source)

    def test_reward_and_consumption_mutations_are_rejected(self) -> None:
        reward = copy.deepcopy(self.source)
        reward["chapter"]["quests"][0]["rewards"] = [
            {"type": "item", "item": "minecraft:diamond"}
        ]
        consume = copy.deepcopy(self.source)
        consume["chapter"]["quests"][0]["tasks"][0]["consume_items"] = True
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for index, mutation in enumerate((reward, consume)):
                with self.subTest(index=index):
                    source = self.write_source(root, mutation)
                    with self.assertRaisesRegex(ValueError, "unsupported fields"):
                        validate_orbital_source(source)

    def test_destination_specific_objective_is_rejected(self) -> None:
        for destination in ("Moon", "Mars", "ad_astra:moon"):
            mutated = copy.deepcopy(self.source)
            mutated["chapter"]["quests"][1]["description"][0] += (
                f" Travel to {destination}."
            )
            with tempfile.TemporaryDirectory() as raw:
                source = self.write_source(Path(raw), mutated)
                with self.assertRaisesRegex(ValueError, "destination-specific"):
                    validate_orbital_source(source)

    def test_generated_dependency_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            quest_root = root / "quests"
            shutil.copytree(DEFAULT_OUTPUT, quest_root)
            manifest = root / "manifest.json"
            shutil.copy2(DEFAULT_MANIFEST, manifest)
            chapter_path = quest_root / "chapters" / f"{ORBITAL_FILENAME}.snbt"
            chapter = json.loads(chapter_path.read_text(encoding="utf-8"))
            flight_id = stable_code(
                "orbital_quest", f"{ORBITAL_FILENAME}/orbital_flight_computer"
            )
            thruster_id = stable_code(
                "orbital_quest", f"{ORBITAL_FILENAME}/thruster_mount"
            )
            thruster = next(quest for quest in chapter["quests"] if quest["id"] == thruster_id)
            thruster["dependencies"] = [flight_id, "7FFFFFFFFFFFFFFE"]
            chapter_path.write_text(
                json.dumps(chapter, indent=2) + "\n", encoding="utf-8"
            )
            errors = validate(
                project=PROJECT_ROOT,
                source=DEFAULT_ORBITAL_SOURCE,
                quest_root=quest_root,
                manifest_path=manifest,
                item_catalog=DEFAULT_ITEM_CATALOG,
                instance=DEFAULT_INSTANCE,
            )
        self.assertTrue(
            any("generated dependency edge changed" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
