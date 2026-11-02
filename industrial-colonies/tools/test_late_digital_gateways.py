#!/usr/bin/env python3
"""Focused regression tests for the late-digital gateway contract."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_late_digital_gateways import (
    DEFAULT_ASSIGNMENTS,
    DEFAULT_COMPILED,
    DEFAULT_MANIFEST,
    DEFAULT_TAG_SCRIPT,
    PROJECT,
    validate_contract,
)


class LateDigitalGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8-sig"))
        cls.compiled = json.loads(DEFAULT_COMPILED.read_text(encoding="utf-8-sig"))
        cls.assignments = json.loads(DEFAULT_ASSIGNMENTS.read_text(encoding="utf-8-sig"))
        cls.tag_script = DEFAULT_TAG_SCRIPT.read_text(encoding="utf-8-sig")

    def validate(self, manifest=None, compiled=None, assignments=None, tag_script=None):
        return validate_contract(
            PROJECT,
            self.manifest if manifest is None else manifest,
            self.compiled if compiled is None else compiled,
            self.assignments if assignments is None else assignments,
            self.tag_script if tag_script is None else tag_script,
        )

    def test_current_contract_passes(self) -> None:
        self.assertEqual([], self.validate())

    def test_missing_mirror_removal_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        compiled = copy.deepcopy(self.compiled)
        recipe = next(
            value
            for value in manifest["recipes"]
            if value.get("output") == "extendedae:machine_frame"
        )
        recipe["remove"].remove("extendedae:machine_frame_mirror")
        compiled["removals"] = [
            value
            for value in compiled["removals"]
            if value.get("recipeId") != "extendedae:machine_frame_mirror"
        ]
        errors = self.validate(manifest=manifest, compiled=compiled)
        self.assertTrue(any("machine_frame_mirror" in error for error in errors), errors)

    def test_shortened_mega_sequence_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        recipe = next(
            value
            for value in manifest["recipes"]
            if value.get("output") == "megacells:cell_component_1m"
        )
        recipe["loops"] = 0
        errors = self.validate(manifest=manifest)
        self.assertTrue(any("expected 1" in error for error in errors), errors)

    def test_cheap_stress_attunement_key_fails(self) -> None:
        script = self.tag_script + "\nevent.add(stressAttunement, 'create:shaft')\n"
        errors = self.validate(tag_script=script)
        self.assertTrue(any("cheap key" in error for error in errors), errors)

    def test_missing_stress_controller_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        recipe = next(
            value
            for value in manifest["recipes"]
            if value.get("output") == "appliedcreate:me_gearbox"
        )
        step = next(
            value
            for value in recipe["steps"]
            if value.get("ingredient") == "appliedcreate:advanced_stress_processor"
        )
        step["ingredient"] = "minecraft:iron_ingot"
        errors = self.validate(manifest=manifest)
        self.assertTrue(
            any("advanced_stress_processor" in error for error in errors), errors
        )

    def test_missing_node_assignment_fails(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"]["CR01 — Overclocked Processors"]["unlocks"].remove(
            "advanced_ae:reaction_chamber"
        )
        errors = self.validate(assignments=assignments)
        self.assertTrue(any("Overclocked Processors" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
