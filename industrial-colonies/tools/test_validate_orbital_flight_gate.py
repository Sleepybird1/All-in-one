#!/usr/bin/env python3

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

import validate_orbital_flight_gate as validator


class OrbitalFlightGateMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source = TOOLS.parent
        for relative in validator.REQUIRED_FILES:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)
        self.project_jar = Path(self.temp.name) / "industrial_colonies-test.jar"
        source_resources = source / "src" / "main" / "resources"
        with zipfile.ZipFile(self.project_jar, "w") as archive:
            for entry in validator.PROJECT_JAR_ENTRIES:
                resource = source_resources / entry
                if resource.is_file():
                    archive.write(resource, entry)
                else:
                    archive.writestr(entry, b"synthetic mutation-test class")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(self.project, project_jar=self.project_jar)

    def drop_jar_entry(self, entry_to_drop: str) -> None:
        with zipfile.ZipFile(self.project_jar, "r") as archive:
            entries = {
                entry: archive.read(entry)
                for entry in archive.namelist()
                if entry != entry_to_drop
            }
        with zipfile.ZipFile(self.project_jar, "w") as archive:
            for entry, content in entries.items():
                archive.writestr(entry, content)

    def replace(self, relative: Path, old: str, new: str) -> None:
        path = self.project / relative
        path.write_text(path.read_text(encoding="utf-8-sig").replace(old, new), encoding="utf-8")

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_mixin_must_target_preteleport_permission_check(self) -> None:
        self.replace(validator.MIXIN, "allowToSpace()Z", "allowFromSpace()Z")
        self.assertTrue(any("mixin contract" in value for value in self.failures()))

    def test_03_synthetic_method_signature_is_pinned(self) -> None:
        self.replace(validator.MIXIN, "lambda$init$2", "lambda$init$3")
        self.assertTrue(any("mixin contract" in value for value in self.failures()))

    def test_04_ship_local_is_pinned(self) -> None:
        self.replace(validator.MIXIN, '@Local(name = "ship")', '@Local(name = "craft")')
        self.assertTrue(any("mixin contract" in value for value in self.failures()))

    def test_05_block_entity_must_be_sable_actor(self) -> None:
        self.replace(validator.BLOCK_ENTITY, "implements BlockEntitySubLevelActor", "")
        self.assertTrue(any("Sable ship actor" in value for value in self.failures()))

    def test_06_authorization_must_fail_closed(self) -> None:
        self.replace(validator.AUTHORIZATION, "return false;", "return true;")
        self.assertTrue(any("fails closed" in value for value in self.failures()))

    def test_07_recipe_must_consume_industrial_star(self) -> None:
        def mutate(payload):
            recipe = next(row for row in payload["recipes"] if row.get("id") == validator.RECIPE_ID)
            recipe["key"]["S"] = "minecraft:nether_star"

        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("recipe key drifted" in value for value in self.failures()))

    def test_08_project_card_must_exist(self) -> None:
        self.mutate_json(
            validator.KJSGEN,
            lambda payload: payload.__setitem__(
                "recipes",
                [row for row in payload["recipes"] if row.get("recipeId") != validator.RECIPE_ID],
            ),
        )
        self.assertTrue(any("project must contain" in value for value in self.failures()))

    def test_09_mixin_config_must_enable_gate(self) -> None:
        self.mutate_json(
            validator.MIXIN_CONFIG,
            lambda payload: payload["mixins"].remove("SpaceTransitionHandlerMixin"),
        )
        self.assertTrue(any("mixin config" in value for value in self.failures()))

    def test_08b_reviewed_recipe_must_keep_the_approved_star_core(self) -> None:
        def mutate(payload):
            card = next(
                row for row in payload["recipes"] if row.get("recipeId") == validator.RECIPE_ID
            )
            card["slots"]["cell_2_2"]["id"] = "minecraft:nether_star"

        self.mutate_json(validator.KJSGEN, mutate)
        self.assertTrue(
            any("reviewed recipe pattern/key drifted" in value for value in self.failures())
        )

    def test_10_deployment_jar_must_contain_flight_computer_assets(self) -> None:
        self.drop_jar_entry(
            "assets/industrial_colonies/models/block/orbital_flight_computer.json"
        )
        self.assertTrue(any("deployment candidate JAR" in value for value in self.failures()))

    def test_11_deployment_jar_must_contain_transition_mixin(self) -> None:
        self.drop_jar_entry(
            "dev/godpc/industrialcolonies/mixin/SpaceTransitionHandlerMixin.class"
        )
        self.assertTrue(any("deployment candidate JAR" in value for value in self.failures()))


if __name__ == "__main__":
    unittest.main()
