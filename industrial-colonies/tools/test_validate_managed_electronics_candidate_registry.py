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

import validate_managed_electronics_slice as validator


def synthetic_class_with_strings(*values: str) -> bytes:
    """Build the constant-pool prefix needed by the validator fixture."""

    entries: list[bytes] = []
    pool_index = 1
    for value in values:
        encoded = value.encode("utf-8")
        entries.append(b"\x01" + len(encoded).to_bytes(2, "big") + encoded)
        entries.append(b"\x08" + pool_index.to_bytes(2, "big"))
        pool_index += 2
    return (
        b"\xca\xfe\xba\xbe"
        + (0).to_bytes(2, "big")
        + (65).to_bytes(2, "big")
        + (len(entries) + 1).to_bytes(2, "big")
        + b"".join(entries)
    )


class CandidateJarRegistryMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.jar = Path(self.temp.name) / "industrial_colonies-candidate.jar"
        language = {
            "block.industrial_colonies.orbital_flight_computer": "Orbital Flight Computer",
            "item.industrial_colonies.unregistered_widget": "Unregistered Widget",
        }
        with zipfile.ZipFile(self.jar, "w") as archive:
            archive.writestr(
                "dev/godpc/industrialcolonies/IndustrialItems.class",
                synthetic_class_with_strings("orbital_flight_computer"),
            )
            archive.writestr(
                "assets/industrial_colonies/lang/en_us.json",
                json.dumps(language),
            )
            archive.writestr(
                "assets/industrial_colonies/models/item/orbital_flight_computer.json",
                "{}",
            )
            # A model and translation alone must not become registration evidence.
            archive.writestr(
                "assets/industrial_colonies/models/item/unregistered_widget.json",
                "{}",
            )

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def recipe(output: str) -> dict:
        return {
            "recipeId": "industrial_colonies:test/candidate_registry",
            "replaceRecipe": False,
            "slots": {"output": {"kind": "ITEM", "id": output}},
        }

    def test_01_candidate_jar_registered_block_item_passes(self) -> None:
        registry = validator.candidate_jar_registered_project_item_ids(self.jar)
        self.assertIn("industrial_colonies:orbital_flight_computer", registry)
        failures: list[str] = []
        validator.validate_recipe_slots(
            failures,
            [self.recipe("industrial_colonies:orbital_flight_computer")],
            registry,
        )
        self.assertEqual([], failures)

    def test_02_arbitrary_namespace_output_still_fails(self) -> None:
        registry = validator.candidate_jar_registered_project_item_ids(self.jar)
        failures: list[str] = []
        validator.validate_recipe_slots(
            failures,
            [self.recipe("industrial_colonies:totally_arbitrary_output")],
            registry,
        )
        self.assertTrue(any("unregistered item" in failure for failure in failures))

    def test_03_stray_model_and_translation_do_not_whitelist_item(self) -> None:
        registry = validator.candidate_jar_registered_project_item_ids(self.jar)
        self.assertNotIn("industrial_colonies:unregistered_widget", registry)
        failures: list[str] = []
        validator.validate_recipe_slots(
            failures,
            [self.recipe("industrial_colonies:unregistered_widget")],
            registry,
        )
        self.assertTrue(any("unregistered item" in failure for failure in failures))

    def test_04_source_fallback_recognizes_simple_block_items(self) -> None:
        source = Path(self.temp.name) / "IndustrialItems.java"
        source.write_text(
            'ITEMS.registerSimpleBlockItem("registered_block", BLOCK);\n'
            'ITEMS.registerSimpleItem("registered_item");\n',
            encoding="utf-8",
        )
        self.assertEqual(
            {
                "industrial_colonies:registered_block",
                "industrial_colonies:registered_item",
            },
            validator.source_registered_project_item_ids(source),
        )


if __name__ == "__main__":
    unittest.main()
