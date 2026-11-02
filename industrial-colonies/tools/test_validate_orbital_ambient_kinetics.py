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

import validate_orbital_ambient_kinetics as validator


class OrbitalAmbientKineticsMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        self.mods = Path(self.temp.name) / "mods"
        self.mods.mkdir(parents=True)
        source = TOOLS.parent
        for relative in validator.REQUIRED_FILES:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)

        source_create = source / "libs" / validator.CREATE_JAR_NAME
        self.create_jar = self.mods / validator.CREATE_JAR_NAME
        with zipfile.ZipFile(source_create) as incoming, zipfile.ZipFile(
            self.create_jar, "w"
        ) as outgoing:
            for contract in validator.TARGETS:
                outgoing.writestr(
                    contract.class_path, incoming.read(contract.class_path)
                )

        self.project_jar = Path(self.temp.name) / "industrial_colonies-test.jar"
        self._write_project_jar()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_project_jar(
        self,
        *,
        drop: str | None = None,
        omit_water_marker: bytes | None = None,
        config_mutator=None,
    ) -> None:
        config = json.loads(
            (self.project / validator.MIXIN_CONFIG).read_text(encoding="utf-8-sig")
        )
        if config_mutator is not None:
            config_mutator(config)
        policy_markers = b"\0".join(
            marker.encode()
            for dimension in validator.DENIED_DIMENSIONS
            for marker in dimension.split(":", 1)
        )
        annotation_markers = b"\0HEAD\0cancellable\0require\0"
        water = (
            b"getGeneratedSpeed()F\0deniesHydro\0setReturnValue"
            + annotation_markers
            + validator.TARGETS[0].class_name.encode()
        )
        if omit_water_marker is not None:
            water = water.replace(omit_water_marker, b"missing")
        entries = {
            validator.PROJECT_JAR_ENTRIES[0]: policy_markers,
            validator.PROJECT_JAR_ENTRIES[1]: water,
            validator.PROJECT_JAR_ENTRIES[2]: (
                b"getGeneratedSpeed()F\0deniesWind\0setReturnValue"
                + annotation_markers
                + validator.TARGETS[1].class_name.encode()
            ),
            validator.PROJECT_JAR_ENTRIES[3]: json.dumps(config).encode(),
            validator.PROJECT_JAR_ENTRIES[4]: (
                self.project.joinpath(validator.MOD_METADATA)
                .read_text(encoding="utf-8-sig")
                .encode()
            ),
        }
        with zipfile.ZipFile(self.project_jar, "w") as archive:
            for name, content in entries.items():
                if name != drop:
                    archive.writestr(name, content)

    def failures(self) -> list[str]:
        return validator.validate(
            self.project, mods=self.mods, project_jar=self.project_jar
        )

    def replace(self, relative: Path, old: str, new: str) -> None:
        path = self.project / relative
        source = path.read_text(encoding="utf-8-sig")
        self.assertIn(old, source)
        path.write_text(source.replace(old, new, 1), encoding="utf-8")

    def replace_in_policy_set(self, field: str, old: str, new: str) -> None:
        """Mutate one named set without matching the shared offworld set first."""
        path = self.project / validator.POLICY
        source = path.read_text(encoding="utf-8-sig")
        start = source.index(f"{field} = Set.of(")
        end = source.index("\n    );", start)
        block = source[start:end]
        self.assertIn(old, block)
        block = block.replace(old, new, 1)
        path.write_text(source[:start] + block + source[end:], encoding="utf-8")

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_water_target_descriptor_is_pinned(self) -> None:
        self.replace(validator.WATER_MIXIN, "getGeneratedSpeed()F", "getGeneratedSpeed()D")
        self.assertTrue(any("exact HEAD contract" in row for row in self.failures()))

    def test_03_wind_target_descriptor_is_pinned(self) -> None:
        self.replace(validator.WIND_MIXIN, "getGeneratedSpeed()F", "getGeneratedSpeed()D")
        self.assertTrue(any("exact HEAD contract" in row for row in self.failures()))

    def test_04_injections_must_be_at_head(self) -> None:
        self.replace(validator.WIND_MIXIN, '@At("HEAD")', '@At("RETURN")')
        self.assertTrue(any("exact HEAD contract" in row for row in self.failures()))

    def test_05_injections_must_be_cancellable(self) -> None:
        self.replace(validator.WATER_MIXIN, "cancellable = true", "cancellable = false")
        self.assertTrue(any("exact HEAD contract" in row for row in self.failures()))

    def test_06_injections_must_require_exactly_one_target(self) -> None:
        self.replace(validator.WATER_MIXIN, "require = 1", "require = 0")
        self.assertTrue(any("exact HEAD contract" in row for row in self.failures()))

    def test_07_each_generator_uses_its_separate_policy(self) -> None:
        self.replace(validator.WIND_MIXIN, "deniesWind", "deniesHydro")
        self.assertTrue(any("exact HEAD contract" in row for row in self.failures()))

    def test_08_each_mixin_must_be_registered_once(self) -> None:
        path = self.project / validator.MIXIN_CONFIG
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        payload["mixins"].remove("WaterWheelBlockEntityMixin")
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("common mixin config" in row for row in self.failures()))

    def test_09_base_generator_mixin_is_forbidden(self) -> None:
        path = (
            self.project
            / "src/main/java/dev/godpc/industrialcolonies/mixin/ForbiddenMixin.java"
        )
        path.write_text(
            "@Mixin(GeneratingKineticBlockEntity.class) class ForbiddenMixin {}\n",
            encoding="utf-8",
        )
        self.assertTrue(any("base Generating" in row for row in self.failures()))

    def test_10_both_explicit_dimension_sets_are_complete(self) -> None:
        for field in ("WIND_DENY_DIMENSIONS", "HYDRO_DENY_DIMENSIONS"):
            self.replace_in_policy_set(
                field,
                'dimension("ad_astra", "glacio_orbit"),',
                'dimension("ad_astra", "glacio_orbit_removed"),',
            )
        failures = self.failures()
        self.assertEqual(
            2,
            sum("exact owned dimension set" in row for row in failures),
            failures,
        )

    def test_11_overworld_can_never_enter_a_deny_set(self) -> None:
        self.replace(
            validator.POLICY,
            'dimension("rocketnautics", "deep_space"),',
            'dimension("minecraft", "overworld"),',
        )
        failures = self.failures()
        self.assertTrue(any("Overworld" in row or "overworld" in row for row in failures))

    def test_12_create_dependency_range_is_fail_closed(self) -> None:
        self.replace(
            validator.MOD_METADATA,
            '[6.0.10,6.0.11)',
            '[6.0.10,)',
        )
        self.assertTrue(any("compatibility range" in row for row in self.failures()))

    def test_13_installed_create_filename_is_exact(self) -> None:
        self.create_jar.rename(self.mods / "create-1.21.1-6.0.11.jar")
        self.assertTrue(any("must be exactly" in row for row in self.failures()))

    def test_14_installed_target_bytecode_hash_is_pinned(self) -> None:
        with zipfile.ZipFile(self.create_jar) as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        contract = validator.TARGETS[0]
        changed = bytearray(entries[contract.class_path])
        changed[-1] ^= 1
        entries[contract.class_path] = bytes(changed)
        with zipfile.ZipFile(self.create_jar, "w") as archive:
            for name, content in entries.items():
                archive.writestr(name, content)
        self.assertTrue(any("target bytecode drifted" in row for row in self.failures()))

    def test_15_pinned_classes_expose_exact_float_methods(self) -> None:
        with zipfile.ZipFile(self.create_jar) as archive:
            for contract in validator.TARGETS:
                parsed = validator.parse_class_file(archive.read(contract.class_path))
                matches = [
                    method
                    for method in parsed.methods
                    if method.name == "getGeneratedSpeed"
                    and method.descriptor == "()F"
                ]
                self.assertEqual(1, len(matches))
                self.assertIn("Code", matches[0].attributes)

    def test_16_candidate_jar_must_contain_both_mixins_and_policy(self) -> None:
        self._write_project_jar(drop=validator.PROJECT_JAR_ENTRIES[2])
        self.assertTrue(any("lacks ambient-kinetic entries" in row for row in self.failures()))

    def test_17_candidate_jar_mixin_bytecode_may_not_be_stale(self) -> None:
        self._write_project_jar(omit_water_marker=b"deniesHydro")
        self.assertTrue(any("lacks marker deniesHydro" in row for row in self.failures()))

    def test_18_candidate_jar_config_must_enable_both_mixins(self) -> None:
        self._write_project_jar(
            config_mutator=lambda config: config["mixins"].remove(
                "WindmillBearingBlockEntityMixin"
            )
        )
        self.assertTrue(any("does not enable Windmill" in row for row in self.failures()))


if __name__ == "__main__":
    unittest.main()
