#!/usr/bin/env python3
"""Mutation tests for the orbital navigation, dockyard, and station slice."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_orbital_dockyard_slice as validator


class OrbitalDockyardSliceMutationTests(unittest.TestCase):
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
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def recipe(payload: dict, recipe_id: str) -> dict:
        return next(row for row in payload["recipes"] if row["id"] == recipe_id)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_missing_managed_replacement_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: value["recipes"].__setitem__(
                slice(None),
                [row for row in value["recipes"] if row["id"] != "industrial_colonies:space/navigation/velocity_sensor"],
            ),
        )
        self.assertTrue(any("velocity_sensor" in failure for failure in self.failures()))

    def test_03_exact_stock_removal_drift_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:space/navigation/navigation_table")["remove"] = ["simulated:wrong"]
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("navigation_table" in failure or "stock-removal" in failure for failure in self.failures()))

    def test_04_broad_removal_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:space/navigation/optical_sensor")["remove_by_output"] = "simulated:optical_sensor"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("broad removal" in failure for failure in self.failures()))

    def test_05_docking_item_channel_must_be_portable_interface(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:space/dockyard/docking_connector")["key"]["I"] = "create:smart_chute"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("item channel" in failure or "docking_connector" in failure for failure in self.failures()))

    def test_06_docking_fluid_channel_must_be_portable_interface(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:space/dockyard/docking_connector")["key"]["P"] = "tfmg:steel_pipe"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("fluid channel" in failure or "docking_connector" in failure for failure in self.failures()))

    def test_07_docking_pair_output_is_pinned(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:space/dockyard/docking_connector")["output"] = "simulated:docking_connector"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("matched-pair" in failure or "output drifted" in failure for failure in self.failures()))

    def test_08_offworld_desh_in_first_fluid_duct_fails(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:space/station/fluid_pipe_duct")["inputs"][1] = "8x ad_astra:desh_fluid_pipe"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("off-world Desh" in failure for failure in self.failures()))

    def test_09_orbital_construction_ancestry_is_required(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, "industrial_colonies:space/navigation/velocity_sensor")["depends_on"] = []
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("downstream of Orbital Construction" in failure for failure in self.failures()))

    def test_10_node_unlock_drift_fails(self) -> None:
        def mutate(value: dict) -> None:
            value["nodes"][validator.NAVIGATION_NODE]["unlocks"].pop()
        self.mutate_json(validator.ASSIGNMENTS, mutate)
        self.assertTrue(any("unlock assignment drifted" in failure for failure in self.failures()))

    def test_11_second_sputnik_removal_owner_fails(self) -> None:
        path = self.project / validator.DEFERRED
        source = path.read_text(encoding="utf-8")
        source = source.replace(
            "  const deferredCosmonauticsRecipes = [\n",
            "  const deferredCosmonauticsRecipes = [\n    'rocketnautics:sputnik',\n",
        )
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("second removal owner" in failure for failure in self.failures()))

    def test_12_prefab_station_boundary_must_remain_unchanged(self) -> None:
        path = self.project / validator.DEFERRED
        source = path.read_text(encoding="utf-8").replace(
            "    'ad_astra:space_station/earth_orbit_space_station',\n", ""
        )
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("prefab station boundary" in failure for failure in self.failures()))

    def test_13_quest_reward_fails(self) -> None:
        def mutate(value: dict) -> None:
            quest = next(row for row in value["chapter"]["quests"] if row["key"] == "docking_connector")
            quest["rewards"] = [{"type": "item", "item": "minecraft:diamond"}]
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("gate or reward" in failure for failure in self.failures()))

    def test_14_quest_consumption_fails(self) -> None:
        def mutate(value: dict) -> None:
            quest = next(row for row in value["chapter"]["quests"] if row["key"] == "station_materials")
            quest["tasks"][0]["consume_items"] = True
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("non-consuming" in failure for failure in self.failures()))


if __name__ == "__main__":
    unittest.main()
