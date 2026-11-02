#!/usr/bin/env python3
"""Mutation tests for Mercury Expedition and Asteroid Freight."""

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

import validate_mercury_asteroid_slice as validator


class MercuryAsteroidSliceMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        self.source = TOOLS.parent
        for relative in validator.REQUIRED_FILES:
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
    def recipe(payload: dict, recipe_id: str = validator.RECIPE_ID) -> dict:
        return next(row for row in payload["recipes"] if row["id"] == recipe_id)

    @staticmethod
    def quest(payload: dict, key: str) -> dict:
        return next(row for row in payload["chapter"]["quests"] if row["key"] == key)

    def replace(self, relative: Path, old: str, new: str) -> None:
        path = self.project / relative
        path.write_text(path.read_text(encoding="utf-8-sig").replace(old, new), encoding="utf-8")

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_missing_recipe_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: value["recipes"].__setitem__(
                slice(None), [row for row in value["recipes"] if row["id"] != validator.RECIPE_ID]
            ),
        )
        self.assertTrue(any("recipe set" in failure for failure in self.failures()))

    def test_03_recipe_must_remain_5x5_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value)["pattern"].pop())
        self.assertTrue(any("5x5" in failure or "pattern drifted" in failure for failure in self.failures()))

    def test_04_recipe_must_occupy_grid_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value)["pattern"].__setitem__(0, " PUPC"))
        self.assertTrue(any("25 grid cells" in failure or "pattern drifted" in failure for failure in self.failures()))

    def test_05_calorite_ancestry_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value)["key"].__setitem__("P", "minecraft:iron_block"))
        self.assertTrue(any("ancestry" in failure or "key drifted" in failure for failure in self.failures()))

    def test_06_direct_dependency_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value)["depends_on"].pop())
        self.assertTrue(any("depends_on drifted" in failure for failure in self.failures()))

    def test_07_unrelated_removal_fails(self) -> None:
        self.mutate_json(validator.SEED, lambda value: self.recipe(value).__setitem__("remove", ["minecraft:stick"]))
        self.assertTrue(any("unrelated removal" in failure for failure in self.failures()))

    def test_08_compiled_grid_fails(self) -> None:
        def mutate(value: dict) -> None:
            card = next(row for row in value["recipes"] if row["recipeId"] == validator.RECIPE_ID)
            card["params"]["gridW"] = "3"
        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("5x5 grid" in failure for failure in self.failures()))

    def test_09_compiled_ingredient_fails(self) -> None:
        def mutate(value: dict) -> None:
            card = next(row for row in value["recipes"] if row["recipeId"] == validator.RECIPE_ID)
            card["slots"]["cell_0_0"]["id"] = "minecraft:iron_ingot"
        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("ingredient grid" in failure for failure in self.failures()))

    def test_10_registration_fails(self) -> None:
        self.replace(validator.ITEMS_JAVA, '"mercury_navigation_computer"', '"mercury_computer"')
        self.assertTrue(any("registration drifted" in failure for failure in self.failures()))

    def test_11_ship_actor_fails(self) -> None:
        self.replace(validator.MERCURY_BLOCK_ENTITY, "implements BlockEntitySubLevelActor", "")
        self.assertTrue(any("Sable ship actors" in failure for failure in self.failures()))

    def test_12_surface_link_fails(self) -> None:
        self.mutate_json(validator.MERCURY_PLANET, lambda value: value["dimension_data"].__setitem__("linked_dimension", "ad_astra:mercury_orbit"))
        self.assertTrue(any("canonical surface" in failure or "prefab orbit" in failure for failure in self.failures()))

    def test_13_planet_priority_fails(self) -> None:
        self.mutate_json(validator.MERCURY_PLANET, lambda value: value.__setitem__("priority", 0))
        self.assertTrue(any("priority" in failure for failure in self.failures()))

    def test_14_ship_physics_fails(self) -> None:
        self.mutate_json(validator.MERCURY_PHYSICS, lambda value: value["base_gravity"].__setitem__(1, -9.81))
        self.assertTrue(any("ship-physics" in failure for failure in self.failures()))

    def test_15_arrival_reward_fails(self) -> None:
        self.mutate_json(validator.MERCURY_ADVANCEMENT, lambda value: value.__setitem__("rewards", {"experience": 1}))
        self.assertTrue(any("observation-only" in failure for failure in self.failures()))

    def test_16_mercury_dimension_key_fails(self) -> None:
        self.replace(validator.AUTHORIZATION_JAVA, '"ad_astra", "mercury"', '"ad_astra", "mercury_orbit"')
        self.assertTrue(any("descent gate" in failure or "prefab orbit" in failure for failure in self.failures()))

    def test_17_mercury_requires_own_computer_fails(self) -> None:
        self.replace(
            validator.AUTHORIZATION_JAVA,
            "hasRequiredComputer = hasMercuryNavigationComputer(ship)",
            "hasRequiredComputer = hasVenusNavigationComputer(ship)",
        )
        self.assertTrue(any("descent gate" in failure for failure in self.failures()))

    def test_18_later_computer_must_satisfy_venus_fails(self) -> None:
        self.replace(
            validator.AUTHORIZATION_JAVA,
            "hasVenusNavigationComputer(ship)\n                        || hasMercuryNavigationComputer(ship)",
            "hasVenusNavigationComputer(ship)",
        )
        self.assertTrue(any("descent gate" in failure for failure in self.failures()))

    def test_19_offline_state_fails_closed(self) -> None:
        self.replace(validator.AUTHORIZATION_JAVA, "!deepSpace.getOfflinePlayers().isEmpty()", "false")
        self.assertTrue(any("descent gate" in failure for failure in self.failures()))

    def test_20_deep_space_api_fails(self) -> None:
        self.replace(validator.ASTEROID_MIXIN, "DeepSpaceHelper.isDeepSpace(player.level())", "player.getY() > 5000")
        failures = self.failures()
        self.assertTrue(any("deep-space fix" in failure or "height/path" in failure for failure in failures))

    def test_20b_proximity_player_association_fails(self) -> None:
        self.replace(
            validator.AUTHORIZATION_JAVA,
            "Sable.HELPER.getTrackingOrVehicleSubLevel(player)",
            "ships.getFirst()",
        )
        self.assertTrue(any("descent gate" in failure for failure in self.failures()))

    def test_20c_inflated_bounding_box_association_fails(self) -> None:
        path = self.project / validator.AUTHORIZATION_JAVA
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n// ship.boundingBox().toMojang().inflate(10.0)\n",
            encoding="utf-8",
        )
        self.assertTrue(any("proximity-based" in failure for failure in self.failures()))

    def test_21_mixin_registration_fails(self) -> None:
        self.mutate_json(validator.MIXINS_JSON, lambda value: value["mixins"].remove("AsteroidSpawnerMixin"))
        self.assertTrue(any("registration drifted" in failure for failure in self.failures()))

    def test_22_direct_spawner_fails(self) -> None:
        path = self.project / validator.ASTEROID_MIXIN
        path.write_text(path.read_text(encoding="utf-8") + "// spawnAsteroid(\n", encoding="utf-8")
        self.assertTrue(any("direct spawn" in failure or "invented" in failure for failure in self.failures()))

    def test_23_titanium_washing_retirement_fails(self) -> None:
        self.replace(validator.SPACE_BOUNDARY, f"'{validator.TITANIUM_WASHING}'", "'rocketnautics:missing'")
        self.assertTrue(any("titanium washing" in failure for failure in self.failures()))

    def test_24_node_assignment_fails(self) -> None:
        self.mutate_json(validator.ASSIGNMENTS, lambda value: value["nodes"][validator.NODE]["unlocks"].clear())
        self.assertTrue(any("unlock assignment" in failure for failure in self.failures()))

    def test_25_quest_dag_fails(self) -> None:
        self.mutate_json(
            validator.QUESTS,
            lambda value: self.quest(value, "mercury_arrival").__setitem__("dependencies", ["venus_arrival"]),
        )
        self.assertTrue(any("dependency drifted" in failure for failure in self.failures()))

    def test_26_quest_reward_fails(self) -> None:
        self.mutate_json(
            validator.QUESTS,
            lambda value: self.quest(value, "asteroid_titanium").__setitem__("rewards", [{"type": "item", "item": "minecraft:diamond"}]),
        )
        self.assertTrue(any("gate or reward" in failure for failure in self.failures()))

    def test_27_bulk_freight_count_fails(self) -> None:
        self.mutate_json(
            validator.QUESTS,
            lambda value: self.quest(value, "asteroid_bulk_freight")["tasks"][-1].__setitem__("count", 1),
        )
        self.assertTrue(any("task drifted" in failure for failure in self.failures()))

    def test_28_candidate_jar_requires_stage_entries(self) -> None:
        jar = Path(self.temp.name) / "candidate.jar"
        with zipfile.ZipFile(jar, "w") as archive:
            archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
        self.assertTrue(any("candidate JAR" in failure for failure in self.failures(candidate_jar=jar)))


if __name__ == "__main__":
    unittest.main()
