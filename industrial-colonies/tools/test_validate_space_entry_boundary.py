#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_space_entry_boundary as validator


class SpaceEntryBoundaryMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source_project = TOOLS.parent
        for relative in [validator.SCRIPT, validator.MANIFEST, *validator.TAG_CONTRACTS]:
            source = source_project / relative
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8-sig"), encoding="utf-8")

        self.catalog = Path(self.temp.name) / "recipes.csv"
        with self.catalog.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["recipe_id", "namespace", "recipe_type", "source_jar", "source_path", "industrial", "outputs", "inputs", "tags"],
            )
            writer.writeheader()
            for recipe_id in (
                *validator.DEFERRED_RECIPE_IDS,
                *validator.MANAGED_REPLACEMENTS,
                *validator.PRESERVED_STOCK_ROUTES,
            ):
                output = (
                    validator.MANAGED_REPLACEMENTS.get(recipe_id)
                    or validator.PRESERVED_STOCK_ROUTES.get(recipe_id)
                    or next(
                        (
                            value
                            for value in validator.PROTECTED_OUTPUTS
                            if value.endswith(recipe_id.rsplit("/", 1)[-1])
                        ),
                        "minecraft:air",
                    )
                )
                writer.writerow({"recipe_id": recipe_id, "outputs": output})
            writer.writerow(
                {
                    "recipe_id": validator.SAFE_OXYGEN_LOADING_ID,
                    "outputs": "minecraft:air",
                }
            )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(self.project, self.catalog)

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_missing_exact_recipe_id_fails(self) -> None:
        path = self.project / validator.SCRIPT
        path.write_text(path.read_text(encoding="utf-8").replace("    'cosmowarp:memory_card'\n", ""), encoding="utf-8")
        self.assertTrue(any("cosmowarp:memory_card" in value for value in self.failures()))

    def test_03_broad_output_removal_fails(self) -> None:
        path = self.project / validator.SCRIPT
        path.write_text(path.read_text(encoding="utf-8") + "\nevent.remove({ output: 'ad_astra:tier_1_rocket' })\n", encoding="utf-8")
        self.assertTrue(any("broad recipe removal" in value for value in self.failures()))

    def test_04_rocket_fuel_must_replace_stock_tag(self) -> None:
        relative = Path("src/main/resources/data/rocketnautics/tags/fluid/rocket_fuel.json")
        self.mutate_json(relative, lambda value: value.__setitem__("replace", False))
        self.assertTrue(any("must replace" in value for value in self.failures()))

    def test_05_lava_rocket_fuel_fails(self) -> None:
        relative = Path("src/main/resources/data/rocketnautics/tags/fluid/rocket_fuel.json")
        self.mutate_json(relative, lambda value: value["values"].append("minecraft:lava"))
        self.assertTrue(any("values drifted" in value for value in self.failures()))

    def test_06_water_oxidizer_fails(self) -> None:
        relative = Path("src/main/resources/data/rocketnautics/tags/fluid/oxidizer.json")
        self.mutate_json(relative, lambda value: value["values"].append("minecraft:water"))
        self.assertTrue(any("values drifted" in value for value in self.failures()))

    def test_10_ad_astra_oxygen_bypasses_rotary_condensation(self) -> None:
        relative = Path("src/main/resources/data/rocketnautics/tags/fluid/oxidizer.json")
        self.mutate_json(relative, lambda value: value["values"].append("ad_astra:oxygen"))
        self.assertTrue(any("values drifted" in value for value in self.failures()))

    def test_07_generic_ad_astra_fuel_tag_fails(self) -> None:
        relative = Path("src/main/resources/data/ad_astra/tags/fluid/fuel.json")
        self.mutate_json(relative, lambda value: value["values"].append("#c:diesel"))
        self.assertTrue(any("values drifted" in value for value in self.failures()))

    def test_08_undeferred_duplicate_producer_fails(self) -> None:
        with self.catalog.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["other:shortcut", "other", "minecraft:crafting_shaped", "", "", "0", "cosmowarp:warp_drive", "", ""])
        self.assertTrue(any("undeferred producers" in value for value in self.failures()))

    def test_09_missing_installed_recipe_id_fails(self) -> None:
        with self.catalog.open("r", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        with self.catalog.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(row for row in rows if row["recipe_id"] != "rocketnautics:hologram_block")
        self.assertTrue(any("missing deferred stock IDs" in value for value in self.failures()))

    def test_11_physics_assembler_must_remain_exactly_deferred(self) -> None:
        path = self.project / validator.SCRIPT
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "    'simulated:physics_assembler'\n",
                "",
            ),
            encoding="utf-8",
        )
        self.assertTrue(
            any("simulated:physics_assembler" in value for value in self.failures())
        )

    def test_12_unreviewed_exact_recipe_id_fails_closed(self) -> None:
        path = self.project / validator.SCRIPT
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n// 'ad_astra:unreviewed_space_shortcut'\n",
            encoding="utf-8",
        )
        self.assertTrue(
            any(
                f"reviewed {validator.EXPECTED_DEFERRED_COUNT}-ID boundary" in value
                for value in self.failures()
            )
        )

    def test_13_safe_oxygen_loading_pass_through_must_not_be_deferred(self) -> None:
        path = self.project / validator.SCRIPT
        source = path.read_text(encoding="utf-8")
        source = source.replace(
            "    'ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water',\n",
            "    'ad_astra:oxygen_loading/oxygen_from_oxygen_loading_oxygen',\n"
            "    'ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water',\n",
        )
        path.write_text(source, encoding="utf-8")
        self.assertTrue(
            any("safe oxygen-to-oxygen loading pass-through" in value for value in self.failures())
        )

    def test_14_water_oxygen_shortcut_must_remain_deferred(self) -> None:
        path = self.project / validator.SCRIPT
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "    'ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water',\n",
                "",
            ),
            encoding="utf-8",
        )
        self.assertTrue(any(validator.WATER_OXYGEN_SHORTCUT_ID in value for value in self.failures()))

    def test_15_warp_drive_requires_exclusive_managed_replacement(self) -> None:
        path = self.project / validator.MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        owner = next(
            row for row in payload["recipes"]
            if row.get("output") == "cosmowarp:warp_drive"
        )
        owner["exclusive_output"] = False
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("warp_drive" in value for value in self.failures()))


if __name__ == "__main__":
    unittest.main()
