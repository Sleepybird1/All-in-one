#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_space_destination_bridge as validator


class SpaceDestinationBridgeMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source_project = TOOLS.parent
        resources = [
            *validator.UNIVERSE_CONTRACTS,
            *validator.PHYSICS_CONTRACTS,
            *(Path(value) for value in validator.INTERSTELLAR_UNIVERSE_RESOURCES),
            *(Path(value) for value in validator.INTERSTELLAR_PHYSICS_RESOURCES),
            validator.MOD_METADATA,
        ]
        for relative in resources:
            source = source_project / relative
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8-sig"), encoding="utf-8")

        self.mods = Path(self.temp.name) / "mods"
        self.mods.mkdir(parents=True)
        self.ad_astra_jar = self.mods / "adastra-1.21.1-1.16.22-neoforge.jar"
        self.write_ad_astra_jar(
            {
                validator.texture_jar_entry(
                    contract["planet_texture"]["texture"]
                )
                for contract in validator.UNIVERSE_CONTRACTS.values()
            }
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(self.project, self.mods)

    def write_ad_astra_jar(self, entries: set[str]) -> None:
        with zipfile.ZipFile(self.ad_astra_jar, "w") as archive:
            for entry in sorted(entries):
                archive.writestr(entry, b"test texture")

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_stock_rocketnautics_moon_link_fails(self) -> None:
        self.mutate_json(
            validator.MOON_UNIVERSE,
            lambda value: value["dimension_data"].__setitem__(
                "linked_dimension", "rocketnautics:moon"
            ),
        )
        self.assertTrue(any("unreviewed survival destination link" in value for value in self.failures()))

    def test_03_addon_mars_link_fails(self) -> None:
        self.mutate_json(
            validator.MARS_UNIVERSE,
            lambda value: value["dimension_data"].__setitem__(
                "linked_dimension", "rocketnautics_addon:mars"
            ),
        )
        self.assertTrue(any("unreviewed survival destination link" in value for value in self.failures()))

    def test_04_player_gravity_correction_must_stay_disabled(self) -> None:
        self.mutate_json(
            validator.MOON_UNIVERSE,
            lambda value: value["dimension_data"].__setitem__(
                "apply_gravity_correction_to_entities_in_dimension", True
            ),
        )
        self.assertTrue(any("exact destination contract" in value for value in self.failures()))

    def test_05_rocketnautics_atmosphere_damage_fails(self) -> None:
        self.mutate_json(
            validator.MARS_UNIVERSE,
            lambda value: value["dimension_data"].__setitem__(
                "atmosphere_composition", {"21000": ["low_density", "drowning"]}
            ),
        )
        self.assertTrue(any("exact destination contract" in value for value in self.failures()))

    def test_06_universe_rendering_and_time_control_must_stay_with_ad_astra(self) -> None:
        def mutate(value) -> None:
            value["dimension_data"]["render_universe_in_dimension"] = True
            value["dimension_data"]["dimension_day_time_controller_name"] = "sol"

        self.mutate_json(validator.MOON_UNIVERSE, mutate)
        self.assertTrue(any("exact destination contract" in value for value in self.failures()))

    def test_07_ship_gravity_must_match_ad_astra(self) -> None:
        self.mutate_json(
            validator.MARS_PHYSICS,
            lambda value: value.__setitem__("base_gravity", [0.0, -3.7, 0.0]),
        )
        self.assertTrue(any("exact ship-physics contract" in value for value in self.failures()))

    def test_07b_mercury_surface_link_is_pinned_without_orbit(self) -> None:
        self.mutate_json(
            validator.MERCURY_UNIVERSE,
            lambda value: value["dimension_data"].__setitem__(
                "linked_dimension", "ad_astra:mercury_orbit"
            ),
        )
        failures = self.failures()
        self.assertTrue(any("unreviewed survival destination link" in value for value in failures))

    def test_08_ship_physics_must_target_ad_astra_dimension(self) -> None:
        self.mutate_json(
            validator.MOON_PHYSICS,
            lambda value: value.__setitem__("dimension", "rocketnautics:moon"),
        )
        self.assertTrue(any("exact ship-physics contract" in value for value in self.failures()))

    def test_09_duplicate_survival_link_fails_closed(self) -> None:
        duplicate = (
            self.project
            / validator.DATA_ROOT
            / "industrial_colonies"
            / "universe_planets"
            / "duplicate_moon.json"
        )
        duplicate.parent.mkdir(parents=True, exist_ok=True)
        duplicate.write_text(
            json.dumps(
                {
                    "name": "duplicate_moon",
                    "dimension_data": {"linked_dimension": "ad_astra:moon"},
                }
            ),
            encoding="utf-8",
        )
        failures = self.failures()
        self.assertTrue(any("duplicate/noncanonical survival link" in value for value in failures))
        self.assertTrue(any("duplicate survival link" in value for value in failures))

    def test_10_unowned_glacio_activation_fails_closed(self) -> None:
        glacio = (
            self.project
            / validator.DATA_ROOT
            / "industrial_colonies"
            / "universe_planets"
            / "glacio.json"
        )
        glacio.parent.mkdir(parents=True, exist_ok=True)
        glacio.write_text(
            json.dumps(
                {
                    "name": "glacio",
                    "dimension_data": {"linked_dimension": "ad_astra:glacio"},
                }
            ),
            encoding="utf-8",
        )
        failures = self.failures()
        self.assertTrue(any("Glacio/warp destination activation" in value for value in failures))

    def test_11_unowned_warp_activation_fails_closed(self) -> None:
        warp = (
            self.project
            / validator.DATA_ROOT
            / "industrial_colonies"
            / "universe_planets"
            / "cosmowarp_route.json"
        )
        warp.parent.mkdir(parents=True, exist_ok=True)
        warp.write_text(
            json.dumps(
                {
                    "name": "warp_route",
                    "dimension_data": {"linked_dimension": "cosmowarp:deep_space"},
                }
            ),
            encoding="utf-8",
        )
        self.assertTrue(
            any("Glacio/warp destination activation" in value for value in self.failures())
        )

    def test_12_required_ad_astra_dependency_is_pinned(self) -> None:
        path = self.project / validator.MOD_METADATA
        source = path.read_text(encoding="utf-8")
        source = source.replace('modId="ad_astra"', 'modId="ad_astra_missing"')
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("exactly one required ad_astra dependency" in value for value in self.failures()))

    def test_13_selected_texture_must_exist_in_installed_ad_astra_jar(self) -> None:
        self.write_ad_astra_jar(
            {validator.texture_jar_entry("ad_astra:textures/environment/moon.png")}
        )
        self.assertTrue(any("mars.png is missing" in value for value in self.failures()))

    def test_14_venus_ship_gravity_is_pinned(self) -> None:
        self.mutate_json(
            validator.VENUS_PHYSICS,
            lambda value: value.__setitem__("base_gravity", [0.0, -11.0, 0.0]),
        )
        self.assertTrue(any("exact ship-physics contract" in value for value in self.failures()))


if __name__ == "__main__":
    unittest.main()
