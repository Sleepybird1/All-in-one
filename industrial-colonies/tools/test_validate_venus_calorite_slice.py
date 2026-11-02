#!/usr/bin/env python3
"""Mutation tests for the Venus Expedition and Calorite metallurgy boundary."""

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

import validate_venus_calorite_slice as validator


class VenusCaloriteSliceMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        self.source = TOOLS.parent
        for relative in (*validator.REQUIRED_FILES, validator.MANIFEST, validator.COMPILED):
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source / relative, target)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self, **kwargs) -> list[str]:
        return validator.validate(self.project, **kwargs)

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def recipe(payload: dict, recipe_id: str) -> dict:
        return next(row for row in payload["recipes"] if row["id"] == recipe_id)

    @staticmethod
    def quest(payload: dict, key: str) -> dict:
        return next(row for row in payload["chapter"]["quests"] if row["key"] == key)

    def replace(self, relative: Path, old: str, new: str) -> None:
        path = self.project / relative
        path.write_text(path.read_text(encoding="utf-8-sig").replace(old, new), encoding="utf-8")

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_missing_route_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: value["recipes"].__setitem__(slice(None), [row for row in value["recipes"] if row["id"] != validator.FEED]))
        self.assertTrue(any("Calorite" in failure or validator.FEED in failure for failure in self.failures()))

    def test_03_venus_navigation_pattern_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.VENUS_NAV)["pattern"].pop())
        self.assertTrue(any("5x5" in failure or "pattern drifted" in failure for failure in self.failures()))

    def test_04_navigation_requires_every_outpost_utility(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.VENUS_NAV)["depends_on"].pop())
        self.assertTrue(any("depends_on drifted" in failure for failure in self.failures()))

    def test_05_suit_recipe_must_remain_5x5(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.HELMET)["pattern"].pop())
        self.assertTrue(any("5x5" in failure for failure in self.failures()))

    def test_06_suit_requires_both_offworld_metals(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.SUIT)["key"].__setitem__("D", "tfmg:heavy_plate"))
        self.assertTrue(any("both Desh and Ostrum" in failure for failure in self.failures()))

    def test_07_suit_requires_life_support(self) -> None:
        def mutate(value: dict) -> None:
            row = self.recipe(value, validator.HELMET)
            row["key"]["V"] = "create:brass_sheet"
            row["key"]["S"] = "create:electron_tube"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("life-support hardware" in failure for failure in self.failures()))

    def test_08_exact_removal_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.PLATE)["remove"].pop())
        self.assertTrue(any("shortcut retirement" in failure or "remove drifted" in failure for failure in self.failures()))

    def test_09_broad_removal_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.FEED).__setitem__("remove_by_output", "ad_astra:raw_calorite"))
        self.assertTrue(any("broad removal" in failure for failure in self.failures()))

    def test_10_packing_removal_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: value["additional_removals"].append("ad_astra:calorite_block"))
        self.assertTrue(any("packing preservation" in failure for failure in self.failures()))

    def test_11_acid_charge_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.LEACH)["ingredients"][1].__setitem__("amount", 500))
        self.assertTrue(any("ingredients drifted" in failure for failure in self.failures()))

    def test_12_superheated_reduction_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.REDUCE).__setitem__("heat", "heated"))
        self.assertTrue(any("heat drifted" in failure for failure in self.failures()))

    def test_13_refined_radiance_press_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value, validator.PLATE).__setitem__("machine", "create:mechanical_press"))
        self.assertTrue(any("machine drifted" in failure for failure in self.failures()))

    def test_14_feed_tag_fails(self) -> None:
        self.mutate_json(validator.FEED_TAG, lambda value: value["values"].pop())
        self.assertTrue(any("feed tag" in failure for failure in self.failures()))

    def test_15_planet_link_fails(self) -> None:
        self.mutate_json(validator.VENUS_PLANET, lambda value: value["dimension_data"].__setitem__("linked_dimension", "ad_astra:mercury"))
        self.assertTrue(any("linked_dimension" in failure for failure in self.failures()))

    def test_16_surface_pressure_ownership_fails(self) -> None:
        self.mutate_json(validator.VENUS_PHYSICS, lambda value: value.__setitem__("base_pressure", 1.0))
        self.assertTrue(any("ship-physics" in failure for failure in self.failures()))

    def test_17_venus_key_fails(self) -> None:
        self.replace(validator.AUTHORIZATION_JAVA, '"ad_astra", "venus"', '"ad_astra", "mercury"')
        self.assertTrue(any("managed descent gate" in failure for failure in self.failures()))

    def test_18_heat_tag_fails(self) -> None:
        self.replace(validator.AUTHORIZATION_JAVA, '"ad_astra", "heat_resistant_armor"', '"ad_astra", "space_suit_items"')
        self.assertTrue(any("managed descent gate" in failure for failure in self.failures()))

    def test_19_venus_computer_must_satisfy_mars(self) -> None:
        self.replace(
            validator.AUTHORIZATION_JAVA,
            "|| hasVenusNavigationComputer(ship)",
            "",
        )
        self.assertTrue(any("managed descent gate" in failure for failure in self.failures()))

    def test_20_offline_state_must_fail_closed(self) -> None:
        self.replace(validator.AUTHORIZATION_JAVA, "!deepSpace.getOfflinePlayers().isEmpty()", "false")
        self.assertTrue(any("managed descent gate" in failure for failure in self.failures()))

    def test_21_correct_slot_check_is_required(self) -> None:
        self.replace(validator.AUTHORIZATION_JAVA, "stack.canEquip(slot, player)", "true")
        self.assertTrue(any("managed descent gate" in failure for failure in self.failures()))

    def test_22_quest_dag_fails(self) -> None:
        self.mutate_json(validator.QUESTS, lambda value: self.quest(value, "venus_arrival").__setitem__("dependencies", ["closed_loop_rations"]))
        self.assertTrue(any("venus_arrival" in failure for failure in self.failures()))

    def test_23_quest_reward_fails(self) -> None:
        self.mutate_json(validator.QUESTS, lambda value: self.quest(value, "calorite_freight").__setitem__("rewards", [{"type": "item", "item": "minecraft:diamond"}]))
        self.assertTrue(any("gate or reward" in failure for failure in self.failures()))

    def test_24_arrival_advancement_reward_fails(self) -> None:
        self.mutate_json(validator.VENUS_ADVANCEMENT, lambda value: value.__setitem__("rewards", {"experience": 1}))
        self.assertTrue(any("observation-only" in failure for failure in self.failures()))

    def test_25_node_assignment_fails(self) -> None:
        self.mutate_json(validator.ASSIGNMENTS, lambda value: value["nodes"][validator.METALLURGY_NODE]["unlocks"].pop())
        self.assertTrue(any("unlock assignment drifted" in failure for failure in self.failures()))

    def test_26_compiled_exact_removal_fails(self) -> None:
        def mutate(value: dict) -> None:
            value["removals"] = [row for row in value["removals"] if row.get("recipeId") != "immersiveengineering:metalpress/plate_calorite"]
        self.mutate_json(validator.COMPILED, mutate)
        failures = self.failures(compiled=self.project / validator.COMPILED)
        self.assertTrue(any("compiled exact removal" in failure for failure in failures))

    def test_27_external_loot_bypass_fails(self) -> None:
        mods = Path(self.temp.name) / "mods"
        mods.mkdir()
        with zipfile.ZipFile(mods / "bad.jar", "w") as archive:
            archive.writestr("data/bad/loot_table/chests/test.json", '{"name":"ad_astra:calorite_ingot"}')
        self.assertTrue(any("external loot" in failure for failure in self.failures(mods=mods)))

    def test_28_external_structure_bypass_fails(self) -> None:
        mods = Path(self.temp.name) / "mods"
        mods.mkdir()
        with zipfile.ZipFile(mods / "bad.jar", "w") as archive:
            archive.writestr("data/bad/structure/test.nbt", b"ad_astra:calorite_block")
        self.assertTrue(any("external structure" in failure for failure in self.failures(mods=mods)))

    def test_29_candidate_jar_must_include_venus_data(self) -> None:
        jar = Path(self.temp.name) / "candidate.jar"
        with zipfile.ZipFile(jar, "w") as archive:
            archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
        self.assertTrue(any("candidate JAR" in failure for failure in self.failures(candidate_jar=jar)))


if __name__ == "__main__":
    unittest.main()
