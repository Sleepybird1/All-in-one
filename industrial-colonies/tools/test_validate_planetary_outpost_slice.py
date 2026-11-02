#!/usr/bin/env python3
"""Mutation tests for the planetary outpost commissioning slice."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_planetary_outpost_slice as validator


class PlanetaryOutpostSliceMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source = TOOLS.parent
        for relative in (
            validator.SEED,
            validator.ASSIGNMENTS,
            validator.LAYOUT,
            validator.QUESTS,
            validator.DEFERRED,
            validator.COMPILED,
        ):
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, target)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(self.project)

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def recipe(payload: dict, recipe_id: str) -> dict:
        return next(row for row in payload["recipes"] if row["id"] == recipe_id)

    @staticmethod
    def quest(payload: dict, key: str) -> dict:
        return next(row for row in payload["chapter"]["quests"] if row["key"] == key)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_missing_managed_replacement_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: value["recipes"].__setitem__(
                slice(None),
                [
                    row for row in value["recipes"]
                    if row["id"] != "industrial_colonies:planetary/outpost/water_pump"
                ],
            ),
        )
        self.assertTrue(any("water_pump" in failure for failure in self.failures()))

    def test_03_exact_stock_removal_drift_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:planetary/outpost/energizer")["remove"] = ["ad_astra:wrong"]
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("energizer" in failure or "stock-removal" in failure for failure in self.failures()))

    def test_04_broad_removal_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:planetary/outpost/gravity_normalizer")["remove_by_output"] = "ad_astra:gravity_normalizer"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("broad removal" in failure for failure in self.failures()))

    def test_05_solar_batch_must_remain_four_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:planetary/outpost/solar_panel")["output"] = "ad_astra:solar_panel"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("solar" in failure.lower() or "output drifted" in failure for failure in self.failures()))

    def test_06_all_recipes_must_remain_5x5_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:planetary/outpost/water_pump")["pattern"].pop()
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("5x5" in failure or "pattern drifted" in failure for failure in self.failures()))

    def test_07_desh_must_be_physical_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:planetary/outpost/solar_panel")["key"]["D"] = "tfmg:heavy_plate"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("physically contain Desh" in failure for failure in self.failures()))

    def test_08_ostrum_must_be_physical_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:planetary/outpost/nutritional_liquifier")["key"]["O"] = "tfmg:heavy_plate"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("physically contain Ostrum" in failure for failure in self.failures()))

    def test_09_farmer_food_core_is_required_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:planetary/outpost/nutritional_liquifier")["key"]["B"] = "minecraft:bowl"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("Farmer's Delight" in failure for failure in self.failures()))

    def test_10_node_unlock_drift_fails(self) -> None:
        def mutate(value: dict) -> None:
            value["nodes"][validator.NODE]["unlocks"].pop()
        self.mutate_json(validator.ASSIGNMENTS, mutate)
        self.assertTrue(any("unlock assignment drifted" in failure for failure in self.failures()))

    def test_11_martian_service_requires_both_branches_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.quest(value, "martian_service_reserve")["dependencies"] = ["ostrum_metallurgy"]
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("martian_service_reserve" in failure for failure in self.failures()))

    def test_12_full_canteen_advancement_is_required_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.quest(value, "closed_loop_rations")["tasks"].pop()
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("closed_loop_rations" in failure for failure in self.failures()))

    def test_13_quest_reward_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.quest(value, "lunar_utility_array")["rewards"] = [
                {"type": "item", "item": "minecraft:diamond"}
            ]
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("gate or reward" in failure for failure in self.failures()))

    def test_14_quest_consumption_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.quest(value, "martian_service_reserve")["tasks"][0]["consume_items"] = True
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("non-consuming" in failure for failure in self.failures()))

    def test_15_direct_water_oxygen_boundary_fails(self) -> None:
        path = self.project / validator.DEFERRED
        source = path.read_text(encoding="utf-8").replace(
            "    'ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water',\n", ""
        )
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("oxygen_from_oxygen_loading_water" in failure for failure in self.failures()))

    def test_16_cryo_ownership_change_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: value["additional_removals"].append("ad_astra:cryo_freezer"),
        )
        self.assertTrue(any("cryo" in failure.lower() for failure in self.failures()))

    def test_17_preserved_alternate_compiled_output_fails(self) -> None:
        def mutate(value: dict) -> None:
            source = next(
                card
                for card in value["recipes"]
                if card.get("recipeId") == "industrial_colonies:planetary/outpost/solar_panel"
            )
            duplicate = json.loads(json.dumps(source))
            duplicate["recipeId"] = "user:alternate_solar_panel"
            duplicate["uid"] = "alternate-solar-panel"
            value["recipes"].append(duplicate)

        self.mutate_json(validator.COMPILED, mutate)
        failures = validator.validate(
            self.project,
            compiled=self.project / validator.COMPILED,
        )
        self.assertTrue(any("alternate compiled owners" in failure for failure in failures))

    def test_18_missing_full_canteen_archive_evidence_fails(self) -> None:
        mods = Path(self.temp.name) / "mods"
        mods.mkdir()
        with zipfile.ZipFile(mods / "unrelated.jar", "w") as archive:
            archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
        failures = validator.validate(self.project, mods=mods)
        self.assertTrue(any("full_canteen.json" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
