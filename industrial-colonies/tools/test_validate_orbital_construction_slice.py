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

import validate_orbital_construction_slice as validator


class OrbitalConstructionSliceMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source_project = TOOLS.parent
        copied = (
            validator.SEED,
            validator.MANIFEST,
            validator.COMPILED,
            validator.ASSIGNMENTS,
            validator.LAYOUT,
            validator.DEFERRED,
            validator.ITEMS_JAVA,
            validator.LANG,
        )
        for relative in copied:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_project / relative, target)
        for plan in validator.PLAN_ASSETS:
            relative = Path(
                f"src/main/resources/assets/industrial_colonies/models/item/{plan}.json"
            )
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_project / relative, target)

        source_catalog = source_project.parents[1] / "outputs" / "recipe-catalog-current"
        self.catalog = Path(self.temp.name) / "catalog"
        self.catalog.mkdir()
        external_items = {
            validator.output_id(value)
            for expected in validator.CONSTRUCTION_RECIPES.values()
            for value in [
                expected.get("output"),
                expected.get("input"),
                expected.get("held"),
                *expected.get("key", {}).values(),
                expected.get("machine"),
            ]
            if value
            and not validator.output_id(value).startswith("industrial_colonies:")
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
            writer.writerows(row for row in item_rows if row["item_id"] in external_items)
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
                row for row in recipe_rows if row["recipe_id"] in validator.STOCK_RECIPES
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

    def test_02_retained_catalyst_is_required(self) -> None:
        recipe_id = "industrial_colonies:space/construction/guidance_certified_plan"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__("keep_held", False),
        )
        self.assertTrue(any("keep_held drifted" in failure for failure in self.failures()))

    def test_03_exact_refined_radiance_deployer_is_required(self) -> None:
        recipe_id = "industrial_colonies:space/construction/propulsion_certified_plan"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__(
                "machine", "create:deployer"
            ),
        )
        self.assertTrue(any("machine drifted" in failure for failure in self.failures()))

    def test_04_diagram_exact_stock_removal_is_required(self) -> None:
        recipe_id = "industrial_colonies:space/construction/contraption_diagram"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).pop("remove"),
        )
        self.assertTrue(any("contraption_diagram" in failure for failure in self.failures()))

    def test_05_assembler_cannot_consume_onboard_fixture(self) -> None:
        recipe_id = "industrial_colonies:space/construction/physics_assembler"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id)["key"].__setitem__(
                "C", "ad_astra:airlock"
            ),
        )
        self.assertTrue(any("retained onboard" in failure for failure in self.failures()))

    def test_06_airlock_dependency_is_required(self) -> None:
        recipe_id = "industrial_colonies:space/construction/contraption_diagram"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__(
                "depends_on",
                ["industrial_colonies:space/construction/propulsion_certified_plan"],
            ),
        )
        self.assertTrue(any("depends_on drifted" in failure for failure in self.failures()))

    def test_07_assembler_remains_five_by_five(self) -> None:
        recipe_id = "industrial_colonies:space/construction/physics_assembler"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__(
                "pattern", ["HMP", "FBD", "UCU"]
            ),
        )
        self.assertTrue(any("5x5" in failure for failure in self.failures()))

    def test_08_node_assignment_is_pinned(self) -> None:
        self.mutate_json(
            validator.ASSIGNMENTS,
            lambda payload: payload["nodes"][validator.NODE]["unlocks"].remove(
                validator.DIAGRAM_STOCK_ID
            ),
        )
        self.assertTrue(any("unlock assignment drifted" in failure for failure in self.failures()))

    def test_09_diagram_must_not_join_deferred_boundary(self) -> None:
        path = self.project / validator.DEFERRED
        path.write_text(
            path.read_text(encoding="utf-8-sig")
            + f"\n// mutation\nconst deferredDiagram = '{validator.DIAGRAM_STOCK_ID}'\n",
            encoding="utf-8",
        )
        self.assertTrue(any("must not remain" in failure for failure in self.failures()))

    def test_10_custom_plan_registration_is_required(self) -> None:
        path = self.project / validator.ITEMS_JAVA
        path.write_text(
            path.read_text(encoding="utf-8-sig").replace(
                '"guidance_certified_plan"', '"missing_guidance_plan"'
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("registration drifted" in failure for failure in self.failures()))

    def test_11_compiled_keep_held_parameter_is_pinned(self) -> None:
        recipe_id = "industrial_colonies:space/construction/guidance_certified_plan"

        def mutate(payload: dict) -> None:
            card = next(row for row in payload["recipes"] if row.get("recipeId") == recipe_id)
            card["params"]["keepHeldItem"] = "false"

        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("retained catalyst" in failure for failure in self.failures()))

    def test_12_stock_nested_source_path_is_pinned(self) -> None:
        path = self.catalog / "recipes.csv"
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        next(row for row in rows if row["recipe_id"] == validator.DIAGRAM_STOCK_ID)[
            "source_path"
        ] = "data/simulated/recipe/moved.json"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        self.assertTrue(any("source_path drifted" in failure for failure in self.failures()))

    def test_13_compiled_exact_removal_is_required(self) -> None:
        self.mutate_json(
            validator.COMPILED,
            lambda payload: payload.__setitem__(
                "removals",
                [
                    row
                    for row in payload["removals"]
                    if row.get("recipeId") != validator.DIAGRAM_STOCK_ID
                ],
            ),
        )
        self.assertTrue(any("retire stock" in failure for failure in self.failures()))


if __name__ == "__main__":
    unittest.main()
