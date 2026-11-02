#!/usr/bin/env python3

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_managed_recipe_manifest.py")
SPEC = importlib.util.spec_from_file_location("managed_manifest_builder", SCRIPT)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)

GENERATOR_SCRIPT = Path(__file__).with_name("generate_managed_recipe_overhaul.py")
GENERATOR_SPEC = importlib.util.spec_from_file_location("managed_manifest_generator", GENERATOR_SCRIPT)
assert GENERATOR_SPEC and GENERATOR_SPEC.loader
generator = importlib.util.module_from_spec(GENERATOR_SPEC)
sys.modules[GENERATOR_SPEC.name] = generator
GENERATOR_SPEC.loader.exec_module(generator)


class ManagedManifestBuilderTest(unittest.TestCase):
    def test_tfmg_vat_results_and_ingredients_are_manifest_visible(self) -> None:
        spec = {
            "ingredients": [
                "2x industrial_colonies:desh_concentrate",
                {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 250},
            ],
            "results": [
                {
                    "kind": "ITEM",
                    "id": "industrial_colonies:desh_leached_compound",
                    "count": 2,
                }
            ],
        }
        self.assertEqual(
            ["industrial_colonies:desh_leached_compound"],
            builder.extract_recipe_outputs(spec, "TFMG vat fixture"),
        )
        self.assertEqual(
            {"industrial_colonies:desh_concentrate"},
            builder.extract_recipe_ingredients(spec),
        )

    def test_component_conversion_and_slot_safety(self) -> None:
        self.assertEqual(
            '[test:a=1,test:z={"diesel":"c:diesel"}]',
            builder.component_string(
                {"test:z": {"diesel": "c:diesel"}, "test:a": 1}, "result"
            ),
        )
        self.assertEqual(
            '[test:a=1,test:z={"diesel":"c:diesel"}]',
            generator.slot(
                {
                    "kind": "ITEM",
                    "id": "test:component_output",
                    "components": '[test:a=1,test:z={"diesel":"c:diesel"}]',
                },
                output=True,
            )["components"],
        )
        with self.assertRaises(ValueError):
            generator.slot(
                {
                    "kind": "ITEM",
                    "id": "test:component_output",
                    "components": "[test:a={broken]",
                },
                output=True,
            )

    def test_auto_recipe_gate_replacement_removals_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog = root / "catalog"
            mods = root / "mods"
            catalog.mkdir()
            mods.mkdir()
            seed = root / "seed.json"
            assignments = root / "assignments.json"
            dependencies = root / "dependencies.json"

            recipes = {
                "data/test/recipe/machine.json": {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["OCO", " C ", "OCO"],
                    "key": {
                        "O": {"item": "minecraft:iron_ingot"},
                        "C": {"item": "test:old_circuit"},
                    },
                    "result": {"id": "test:machine", "count": 2},
                },
                "data/test/recipe/machine_pressing.json": {
                    "type": "create:pressing",
                    "ingredients": [{"item": "test:old_circuit"}],
                    "results": [{"item": "test:machine"}],
                },
                "data/test/recipe/sequenced_side_effect.json": {
                    "type": "create:sequenced_assembly",
                    "ingredient": {"item": "minecraft:gold_ingot"},
                    "transitional_item": {"id": "test:incomplete"},
                    "sequence": [],
                    "results": [
                        {"id": "test:primary_product"},
                        {"chance": 0.1, "id": "test:machine"},
                    ],
                },
                "data/test/recipe/gate.json": {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["I"],
                    "key": {"I": {"item": "minecraft:gold_ingot"}},
                    "result": {"id": "test:gate"},
                },
                "data/test/recipe/no_craft.json": {
                    "type": "create:mixing",
                    "ingredients": [{"item": "minecraft:stone"}],
                    "results": [{"item": "test:no_craft"}],
                },
                "data/test/recipe/mek_machine.json": {
                    "type": "mekanism:mek_data",
                    "pattern": ["ICI", "III", " I "],
                    "key": {
                        "I": {"item": "minecraft:iron_ingot"},
                        "C": {"item": "test:old_circuit"},
                    },
                    "result": {"id": "test:mek_machine"},
                },
                "data/test/recipe/retired_factory.json": {
                    "type": "mekanism:mek_data",
                    "pattern": ["III", "ICI", "III"],
                    "key": {
                        "I": {"item": "minecraft:iron_ingot"},
                        "C": {"item": "test:old_circuit"},
                    },
                    "result": {"id": "test:retired_factory"},
                },
                "data/test/recipe/component_output.json": {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["I"],
                    "key": {"I": {"item": "minecraft:iron_ingot"}},
                    "result": {
                        "id": "test:component_output",
                        "count": 2,
                        "components": {
                            "test:amount": 1000,
                            "test:fuels": {"diesel": "c:diesel"},
                        },
                    },
                },
            }
            with zipfile.ZipFile(mods / "test.jar", "w") as archive:
                for path, recipe in recipes.items():
                    archive.writestr(path, json.dumps(recipe))

            recipe_rows = [
                ("test:machine", "minecraft:crafting_shaped", "data/test/recipe/machine.json"),
                ("test:machine_pressing", "create:pressing", "data/test/recipe/machine_pressing.json"),
                ("test:sequenced_side_effect", "create:sequenced_assembly", "data/test/recipe/sequenced_side_effect.json"),
                ("test:gate", "minecraft:crafting_shaped", "data/test/recipe/gate.json"),
                ("test:no_craft", "create:mixing", "data/test/recipe/no_craft.json"),
                ("test:mek_machine", "mekanism:mek_data", "data/test/recipe/mek_machine.json"),
                ("test:retired_factory", "mekanism:mek_data", "data/test/recipe/retired_factory.json"),
                ("test:component_output", "minecraft:crafting_shaped", "data/test/recipe/component_output.json"),
            ]
            with (catalog / "recipes.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["recipe_id", "recipe_type", "source_jar", "source_path"],
                )
                writer.writeheader()
                for recipe_id, recipe_type, source_path in recipe_rows:
                    writer.writerow(
                        {
                            "recipe_id": recipe_id,
                            "recipe_type": recipe_type,
                            "source_jar": "test.jar",
                            "source_path": source_path,
                        }
                    )
            with (catalog / "recipe_refs.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["recipe_id", "source_jar", "role", "kind", "resource_id"],
                )
                writer.writeheader()
                for recipe_id, _recipe_type, _source_path in recipe_rows:
                    output = (
                        "test:machine"
                        if recipe_id
                        in {"test:machine", "test:machine_pressing", "test:sequenced_side_effect"}
                        else recipe_id
                    )
                    writer.writerow(
                        {
                            "recipe_id": recipe_id,
                            "source_jar": "test.jar",
                            "role": "output",
                            "kind": "item",
                            "resource_id": output,
                        }
                    )

            seed.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project": "default",
                        "phase_order": ["Early", "Late"],
                        "phase_by_node": {"Early node": "Early", "Late node": "Late"},
                        "recipes": [
                            {
                                "id": "industrial_colonies:manual/component",
                                "phase": "Early",
                                "type": "shaped",
                                "comment": "Manual component",
                                "pattern": [" I ", " I ", "   "],
                                "key": {"I": "minecraft:iron_ingot"},
                                "output": "test:component",
                                "remove": [],
                            },
                            {
                                "id": "industrial_colonies:manual/disabled",
                                "phase": "Early",
                                "type": "shaped",
                                "comment": "Disabled optional integration",
                                "pattern": [" I ", "   ", "   "],
                                "key": {"I": "minecraft:iron_ingot"},
                                "output": "test:disabled",
                                "remove": ["test:disabled_stock"],
                            }
                        ],
                        "disabled_recipe_ids": [
                            "industrial_colonies:manual/disabled"
                        ],
                        "machine_families": [
                            {
                                "tier": "copper",
                                "source_tier": "andesite",
                                "phase": "Late",
                                "casing": "create:copper_casing",
                                "plate": "#c:plates/copper",
                                "control": "test:component",
                                "drive": "create:precision_mechanism",
                                "source_items": {
                                    "fan": "create:encased_fan",
                                    "automatic_clutch": "createcasing:andesite_automatic_clutch",
                                },
                                "kinds": ["fan", "automatic_clutch"],
                            }
                        ],
                        "exclude_outputs": [],
                        "user_owned_outputs": [],
                        "ingredient_replacements": {"test:old_circuit": "test:component"},
                        "source_recipe_overrides": {"test:machine": "test:machine"},
                        "preserve_recipe_ids": ["test:machine_pressing"],
                        "auto_assignments": True,
                        "auto_policy": {
                            "mechanical_from_phase": "Late",
                            "phase_gates": {"Late": [{"kind": "ITEM", "id": "test:gate"}]},
                        },
                        "additional_removals": ["test:retired_factory"],
                        "retired_recipe_uids": [],
                        "retired_removal_uids": [],
                    }
                ),
                encoding="utf-8",
            )
            assignments.write_text(
                json.dumps(
                    {
                        "nodes": {
                            "Early node": {
                                "unlocks": [
                                    "test:component",
                                    "test:mek_machine",
                                    "test:component_output",
                                ]
                            },
                            "Late node": {
                                "unlocks": [
                                    "test:gate",
                                    "test:machine",
                                    "test:no_craft",
                                    "test:retired_factory",
                                ]
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            dependencies.write_text(
                json.dumps(
                    {
                        "recipes": [
                            {
                                "output": "test:machine",
                                "node": "Late node",
                                "ingredients": ["test:component"],
                                "foundational_tags": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            manifest, report = builder.build_manifest(
                seed, assignments, dependencies, catalog, mods
            )
            by_output = {
                builder.exact_slot_item(recipe["output"]): recipe
                for recipe in manifest["recipes"]
            }
            machine = by_output["test:machine"]
            self.assertEqual("mechanical_crafting", machine["type"])
            self.assertEqual("2x test:machine", machine["output"])
            self.assertEqual(5, len(machine["pattern"]))
            self.assertTrue(all(len(row) == 5 for row in machine["pattern"]))
            self.assertEqual(
                ["test:machine"],
                machine["remove"],
            )
            self.assertEqual(["test:machine_pressing"], manifest["preserve_recipe_ids"])
            self.assertEqual(
                [
                    {
                        "output": "test:machine",
                        "managed_recipe": "industrial_colonies:auto/test/machine",
                        "recipe_id": "test:machine_pressing",
                    }
                ],
                report["preserved_removals"],
            )
            self.assertEqual(
                [
                    "industrial_colonies:auto/test/gate",
                    "industrial_colonies:manual/component",
                ],
                machine["depends_on"],
            )
            self.assertNotIn("test:sequenced_side_effect", machine["remove"])
            self.assertEqual("shaped", by_output["test:gate"]["type"])
            self.assertEqual("shaped", by_output["test:mek_machine"]["type"])
            self.assertEqual(
                {
                    "kind": "ITEM",
                    "id": "test:component_output",
                    "count": 2,
                    "components": '[test:amount=1000,test:fuels={"diesel":"c:diesel"}]',
                },
                by_output["test:component_output"]["output"],
            )
            self.assertNotIn("test:retired_factory", by_output)
            self.assertNotIn("test:disabled", by_output)
            self.assertEqual(
                ["industrial_colonies:manual/disabled"],
                manifest["disabled_recipe_ids"],
            )
            self.assertEqual(
                ["industrial_colonies:manual/disabled"],
                report["disabled_recipes"],
            )
            self.assertEqual(1, report["counts"]["disabled_explicit"])
            self.assertEqual(["test:retired_factory"], manifest["additional_removals"])
            self.assertEqual(["   ", "   ", "   "], [row.replace("I", " ") for row in by_output["test:gate"]["pattern"]])
            family_recipes = manifest["machine_families"][0]["recipes"]
            self.assertEqual("createcasing:copper_encased_fan", family_recipes[0]["output"])
            self.assertEqual(
                ["createcasing:crafting/encased_fan/copper"], family_recipes[0]["remove"]
            )
            self.assertEqual(
                ["createcasing:crafting/auto_clutch/copper"], family_recipes[1]["remove"]
            )
            skipped = {entry["output"]: entry["reason"] for entry in report["skipped"]}
            self.assertEqual("processing_only", skipped["test:no_craft"])
            ignored = {entry["output"]: entry["reason"] for entry in report["ignored"]}
            self.assertEqual("retired_output", ignored["test:retired_factory"])
            self.assertEqual("ok_with_skips", report["status"])
            choices = {entry["output"]: entry["selection"] for entry in report["source_choices"]}
            self.assertEqual("seed_override", choices["test:machine"])

            conflicting_manifest = root / "conflicting-manifest.json"
            conflicting = json.loads(json.dumps(manifest))
            conflicting["additional_removals"].append("test:machine_pressing")
            conflicting_manifest.write_text(json.dumps(conflicting), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "preserved installed recipes are also removed"):
                generator.compile_manifest(conflicting_manifest, root / "compiled.json")


if __name__ == "__main__":
    unittest.main()
