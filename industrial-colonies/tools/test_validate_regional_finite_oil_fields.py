#!/usr/bin/env python3
"""Mutation tests for the finite regional-oil contract."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
VALIDATOR = PROJECT / "tools/validate_regional_finite_oil_fields.py"
INSTANCE = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one")


class RegionalFiniteOilTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name) / "project"
        for relative in ("src/main/java", "src/main/resources", "pack-scripts"):
            source = PROJECT / relative
            destination = self.project / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--project",
                str(self.project),
                "--instance",
                str(INSTANCE),
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def replace(self, relative: str, before: str, after: str) -> None:
        path = self.project / relative
        content = path.read_text(encoding="utf-8")
        self.assertIn(before, content)
        path.write_text(content.replace(before, after, 1), encoding="utf-8")

    def test_current_contract_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_bottomless_cdg_oil_hook_fails(self) -> None:
        self.replace(
            "pack-scripts/server_scripts/industrial_petroleum_canonicalization.js",
            "return 0",
            "return 1000000",
        )
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("independent chunk-oil reserve", result.stderr)

    def test_mountain_oil_weight_fails(self) -> None:
        self.replace(
            "src/main/resources/data/industrial_colonies/geology/oil.json",
            '"mountain_highland": 0.0',
            '"mountain_highland": 2.5',
        )
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing hard oil veto", result.stderr)

    def test_cross_region_well_radius_fails(self) -> None:
        self.replace(
            "src/main/resources/data/industrial_colonies/geology/oil.json",
            '"radius_max_blocks": 80',
            '"radius_max_blocks": 250',
        )
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("regional ownership margin", result.stderr)

    def test_offshore_exclusion_fails(self) -> None:
        self.replace(
            "src/main/resources/data/industrial_colonies/neoforge/biome_modifier/add_regional_oil_fields.json",
            '"#minecraft:is_overworld"',
            '"#industrial_colonies:oil_bearing_biomes"',
        )
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("excludes offshore", result.stderr)

    def test_unregistered_reservoir_mixin_fails(self) -> None:
        self.replace(
            "src/main/resources/industrial_colonies.mixins.json",
            '    "TFMGPumpjackFiniteReservoirMixin",\n',
            "",
        )
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("mixin is not registered", result.stderr)

    def test_missing_exact_cdg_retirement_fails(self) -> None:
        self.replace(
            "pack-scripts/server_scripts/industrial_petroleum_canonicalization.js",
            "  'createdieselgenerators:crafting/oil_scanner',\n",
            "",
        )
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("oil_scanner", result.stderr)


if __name__ == "__main__":
    unittest.main()
