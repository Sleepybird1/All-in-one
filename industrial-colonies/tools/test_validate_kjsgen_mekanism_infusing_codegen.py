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

import validate_kjsgen_mekanism_infusing_codegen as validator


class MekanismInfusingCodegenMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source = TOOLS.parent
        for relative in (validator.JAVA, validator.PROJECT, validator.KJSGEN_JAR):
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(self.project)

    def replace_java(self, old: str, new: str) -> None:
        path = self.project / validator.JAVA
        source = path.read_text(encoding="utf-8")
        self.assertIn(old, source)
        path.write_text(source.replace(old, new, 1), encoding="utf-8")

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_explicit_recipe_id_is_mandatory(self) -> None:
        self.replace_java(
            '}).id(" + JsUtil.quote(recipeId) + ")"',
            '})"',
        )
        self.assertTrue(any("missing" in row and ".id" in row for row in self.failures()))

    def test_03_recipe_id_must_come_from_card(self) -> None:
        self.replace_java(
            'KjsGenIntegration.requireRecipeId(recipe, "Mekanism metallurgic infusing")',
            '"industrial_colonies:fixed"',
        )
        self.assertTrue(any("requireRecipeId" in row for row in self.failures()))

    def test_04_positional_constructor_is_rejected(self) -> None:
        self.replace_java(
            "event.custom({ type: 'mekanism:metallurgic_infusing'",
            "event.recipes.mekanism.metallurgic_infusing",
        )
        failures = self.failures()
        self.assertTrue(any("positional" in row for row in failures))

    def test_05_upstream_layout_drift_is_detected(self) -> None:
        jar = self.project / validator.KJSGEN_JAR
        with zipfile.ZipFile(jar) as incoming:
            entries = {name: incoming.read(name) for name in incoming.namelist()}
        payload = json.loads(entries[validator.LAYOUT])
        for parameter in payload["parameters"]:
            if parameter["key"] == "__template":
                parameter["default"] = "event.custom({})"
        entries[validator.LAYOUT] = json.dumps(payload).encode()
        with zipfile.ZipFile(jar, "w") as outgoing:
            for name, content in entries.items():
                outgoing.writestr(name, content)
        self.assertTrue(any("four-argument" in row for row in self.failures()))

    def test_06_component_bearing_fixture_is_rejected(self) -> None:
        path = self.project / validator.PROJECT
        payload = json.loads(path.read_text(encoding="utf-8"))
        recipe = next(
            card
            for card in payload["recipes"]
            if card.get("type") == "kjsgen:mekanism_metallurgic_infusing"
        )
        recipe["slots"]["output"]["components"] = "[minecraft:custom_name='bad']"
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.assertTrue(any("uses components" in row for row in self.failures()))


if __name__ == "__main__":
    unittest.main()
