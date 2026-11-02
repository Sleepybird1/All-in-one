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

import validate_planetary_freight_gates as validator


class PlanetaryFreightGateMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source = TOOLS.parent
        for relative in validator.REQUIRED_FILES:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)
        self.project_jar = Path(self.temp.name) / "industrial-colonies-test.jar"
        resources = source / "src/main/resources"
        with zipfile.ZipFile(self.project_jar, "w") as archive:
            for entry in validator.PROJECT_JAR_ENTRIES:
                resource = resources / entry
                if resource.is_file():
                    archive.write(resource, entry)
                elif entry.endswith("industrial_colonies.mixins.json"):
                    archive.write(source / validator.MIXIN_CONFIG, entry)
                else:
                    archive.writestr(
                        entry,
                        (
                            b"allowToDimension()Z require mayDescendToManagedPlanet"
                            if entry.endswith("DeepSpaceInstanceMixin.class")
                            else b"synthetic mutation-test class"
                        ),
                    )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(self.project, project_jar=self.project_jar)

    def replace(self, relative: Path, old: str, new: str) -> None:
        path = self.project / relative
        path.write_text(
            path.read_text(encoding="utf-8-sig").replace(old, new),
            encoding="utf-8",
        )

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def drop_jar_entry(self, target: str) -> None:
        with zipfile.ZipFile(self.project_jar) as archive:
            entries = {
                name: archive.read(name)
                for name in archive.namelist()
                if name != target
            }
        with zipfile.ZipFile(self.project_jar, "w") as archive:
            for name, payload in entries.items():
                archive.writestr(name, payload)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_permission_hook_is_exact(self) -> None:
        self.replace(validator.MIXIN, "allowToDimension()Z", "allowFromDimension()Z")
        self.assertTrue(any("mixin contract" in value for value in self.failures()))

    def test_03_exit_hook_is_forbidden(self) -> None:
        self.replace(
            validator.MIXIN,
            "allowToDimension()Z",
            "exitDeepSpace allowToDimension()Z",
        )
        self.assertTrue(any("unsafe hook" in value for value in self.failures()))

    def test_04_mars_key_is_pinned(self) -> None:
        self.replace(validator.AUTHORIZATION, '"mars"', '"venus"')
        self.assertTrue(any("authorization contract" in value for value in self.failures()))

    def test_05_offline_state_must_fail_closed(self) -> None:
        self.replace(
            validator.AUTHORIZATION,
            "deepSpace.getOfflinePlayers().isEmpty()",
            "true",
        )
        self.assertTrue(any("authorization contract" in value for value in self.failures()))

    def test_06_unloaded_state_must_fail_closed(self) -> None:
        self.replace(
            validator.AUTHORIZATION,
            "deepSpace.getUnloadedSublevels().isEmpty()",
            "true",
        )
        self.assertTrue(any("authorization contract" in value for value in self.failures()))

    def test_07_every_occupied_ship_is_checked(self) -> None:
        self.replace(
            validator.AUTHORIZATION,
            "hasMarsNavigationComputer(ship)",
            "hasOrbitalFlightComputer(ship)",
        )
        self.assertTrue(any("authorization contract" in value for value in self.failures()))

    def test_07b_player_must_be_associated_with_a_loaded_ship(self) -> None:
        self.replace(
            validator.AUTHORIZATION,
            "Sable.HELPER.getTrackingOrVehicleSubLevel(player)",
            "null",
        )
        self.assertTrue(any("authorization contract" in value for value in self.failures()))

    def test_08_computer_must_be_sable_actor(self) -> None:
        self.replace(
            validator.MARS_BLOCK_ENTITY,
            "implements BlockEntitySubLevelActor",
            "",
        )
        self.assertTrue(any("Sable actor" in value for value in self.failures()))

    def test_09_ender_chest_event_must_cancel(self) -> None:
        self.replace(validator.ENDER_GATE, "event.setCanceled(true)", "")
        self.assertTrue(any("Ender Chest gate" in value for value in self.failures()))

    def test_10_dimension_transfer_must_close_inherited_menu(self) -> None:
        self.replace(validator.ENDER_GATE, "PlayerChangedDimensionEvent", "PlayerEvent")
        self.assertTrue(any("Ender Chest gate" in value for value in self.failures()))

    def test_11_global_non_overworld_gate_is_rejected(self) -> None:
        self.replace(
            validator.ENDER_GATE,
            "private static void onRightClickBlock",
            "// dimension() != Level.OVERWORLD\n    private static void onRightClickBlock",
        )
        self.assertTrue(any("unrelated" in value for value in self.failures()))

    def test_12_offworld_set_is_exact(self) -> None:
        self.replace(validator.DIMENSION_POLICY, '"moon_orbit"', '"luna_orbit"')
        self.assertTrue(any("dimension set" in value for value in self.failures()))

    def test_13_mixin_must_be_enabled_once(self) -> None:
        self.mutate_json(
            validator.MIXIN_CONFIG,
            lambda payload: payload["mixins"].remove("DeepSpaceInstanceMixin"),
        )
        self.assertTrue(any("exactly once" in value for value in self.failures()))

    def test_14_raw_cosmonautics_classpath_is_forbidden(self) -> None:
        self.replace(
            validator.BUILD,
            "'createmetallurgy-*.jar',",
            "'createmetallurgy-*.jar',\n            'cosmonautics-26.08.307.jar',",
        )
        self.assertTrue(any("raw Cosmonautics" in value for value in self.failures()))

    def test_15_candidate_jar_must_include_computer_assets(self) -> None:
        self.drop_jar_entry(
            "assets/industrial_colonies/models/block/mars_navigation_computer.json"
        )
        self.assertTrue(any("candidate JAR" in value for value in self.failures()))

    def test_16_candidate_jar_must_enable_mixin(self) -> None:
        with zipfile.ZipFile(self.project_jar) as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        payload = json.loads(entries["industrial_colonies.mixins.json"])
        payload["mixins"].remove("DeepSpaceInstanceMixin")
        entries["industrial_colonies.mixins.json"] = json.dumps(payload).encode()
        with zipfile.ZipFile(self.project_jar, "w") as archive:
            for name, content in entries.items():
                archive.writestr(name, content)
        self.assertTrue(any("candidate JAR" in value for value in self.failures()))


if __name__ == "__main__":
    unittest.main()
