#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_orbital_life_support_slice as validator


class OrbitalLifeSupportSliceMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source_project = TOOLS.parent
        for relative in (
            validator.SEED,
            validator.MANIFEST,
            validator.COMPILED,
            validator.ASSIGNMENTS,
            validator.DEFERRED,
        ):
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_project / relative, target)

        source_catalog = source_project.parents[1] / "outputs" / "recipe-catalog-current"
        self.catalog = Path(self.temp.name) / "catalog"
        self.catalog.mkdir()
        required_items = {
            validator.output_id(value)
            for expected in validator.LIFE_SUPPORT_RECIPES.values()
            for value in [expected["output"], *expected["key"].values()]
            if not validator.output_id(value).startswith("minecraft:")
        }
        with (source_catalog / "items.csv").open(
            "r", encoding="utf-8-sig", newline=""
        ) as handle:
            item_rows = list(csv.DictReader(handle))
        with (self.catalog / "items.csv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=item_rows[0].keys())
            writer.writeheader()
            writer.writerows(row for row in item_rows if row["item_id"] in required_items)

        required_recipes = set(validator.STOCK_RECIPES) | set(
            validator.OXYGEN_ROUTE_RECIPES
        )
        with (source_catalog / "recipes.csv").open(
            "r", encoding="utf-8-sig", newline=""
        ) as handle:
            recipe_rows = list(csv.DictReader(handle))
        with (self.catalog / "recipes.csv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=recipe_rows[0].keys())
            writer.writeheader()
            writer.writerows(
                row for row in recipe_rows if row["recipe_id"] in required_recipes
            )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(
            self.project,
            catalog=self.catalog,
            manifest=self.project / validator.MANIFEST,
            compiled=self.project / validator.COMPILED,
        )

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def recipe(payload: dict, recipe_id: str) -> dict:
        return next(row for row in payload["recipes"] if row.get("id") == recipe_id)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_all_nine_source_recipes_are_required(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/oxygen_loader"
        self.mutate_json(
            validator.SEED,
            lambda payload: payload.__setitem__(
                "recipes",
                [row for row in payload["recipes"] if row.get("id") != recipe_id],
            ),
        )
        self.assertTrue(any(recipe_id in failure for failure in self.failures()))

    def test_03_exact_stock_removal_is_pinned(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/gas_tank"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__(
                "remove", ["ad_astra:oxygen_gear"]
            ),
        )
        self.assertTrue(any("remove drifted" in failure for failure in self.failures()))

    def test_04_pressure_branch_must_reach_thruster_mount(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/fan"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__("depends_on", []),
        )
        self.assertTrue(any("not downstream" in failure for failure in self.failures()))

    def test_05_tfmg_electric_motor_is_pinned(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/fan"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id)["key"].__setitem__(
                "M", "createaddition:electric_motor"
            ),
        )
        self.assertTrue(any("key drifted" in failure for failure in self.failures()))

    def test_06_distributor_join_dependencies_are_pinned(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/oxygen_distributor"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__(
                "depends_on", ["industrial_colonies:space/life_support/oxygen_loader"]
            ),
        )
        self.assertTrue(any("depends_on drifted" in failure for failure in self.failures()))

    def test_07_safe_oxygen_pass_through_cannot_be_redeferred(self) -> None:
        path = self.project / validator.DEFERRED
        source = path.read_text(encoding="utf-8-sig")
        source = source.replace(
            f"    '{validator.WATER_OXYGEN_SHORTCUT}',\n",
            f"    '{validator.SAFE_OXYGEN_LOADING}',\n"
            f"    '{validator.WATER_OXYGEN_SHORTCUT}',\n",
        )
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("pass-through was re-deferred" in failure for failure in self.failures()))

    def test_08_direct_water_loading_must_remain_deferred(self) -> None:
        path = self.project / validator.DEFERRED
        path.write_text(
            path.read_text(encoding="utf-8-sig").replace(
                f"    '{validator.WATER_OXYGEN_SHORTCUT}',\n", ""
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("water-to-oxygen shortcut" in failure for failure in self.failures()))

    def test_09_node_assignment_cannot_drift(self) -> None:
        self.mutate_json(
            validator.ASSIGNMENTS,
            lambda payload: payload["nodes"]["CR02 — Pressure Hardware"][
                "unlocks"
            ].remove("ad_astra:oxygen_gear"),
        )
        self.assertTrue(any("unlock assignment drifted" in failure for failure in self.failures()))

    def test_10_assembled_manifest_must_keep_life_support_recipe(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/vent"
        self.mutate_json(
            validator.MANIFEST,
            lambda payload: payload.__setitem__(
                "recipes",
                [row for row in payload["recipes"] if row.get("id") != recipe_id],
            ),
        )
        self.assertTrue(any("assembled manifest must contain" in failure for failure in self.failures()))

    def test_11_compiled_card_slots_are_pinned(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/airlock"

        def mutate(payload: dict) -> None:
            card = next(
                row for row in payload["recipes"] if row.get("recipeId") == recipe_id
            )
            card["slots"]["output"]["count"] = 64

        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("KJSGen slots drifted" in failure for failure in self.failures()))

    def test_12_stock_source_path_is_pinned(self) -> None:
        path = self.catalog / "recipes.csv"
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        next(row for row in rows if row["recipe_id"] == "ad_astra:oxygen_sensor")[
            "source_path"
        ] = "data/ad_astra/recipe/moved_sensor.json"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        self.assertTrue(any("source path drifted" in failure for failure in self.failures()))

    def test_13_all_recipes_remain_five_by_five(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/oxygen_gear"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__(
                "pattern", ["RPR", "VCV", "QEQ"]
            ),
        )
        self.assertTrue(any("5x5 mechanical assembly" in failure for failure in self.failures()))

    def test_14_broad_removal_metadata_is_rejected(self) -> None:
        recipe_id = "industrial_colonies:space/life_support/oxygen_sensor"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__(
                "remove_by_output", "ad_astra:oxygen_sensor"
            ),
        )
        self.assertTrue(any("broad removal directive" in failure for failure in self.failures()))


if __name__ == "__main__":
    unittest.main()
