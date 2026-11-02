#!/usr/bin/env python3
"""Mutation tests for the Moon Desh / Mars Ostrum industry contract."""

from __future__ import annotations

import json
import gzip
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_planetary_industry_slice as validator


class PlanetaryIndustryMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source = TOOLS.parent
        relatives = (
            validator.SEED, validator.MANIFEST, validator.COMPILED,
            validator.ASSIGNMENTS, validator.QUESTS, validator.NATIVE_CHAPTER,
            validator.ITEMS_JAVA, validator.LANG,
            validator.DESH_FEED_TAG, validator.OSTRUM_FEED_TAG,
            *validator.MOON_LOOT,
            *(relative for relative, _ in validator.ADVANCEMENTS.values()),
            *validator.STRUCTURE_RESOURCES,
            *(validator.MODEL_DIR / f"{name}.json" for name in validator.CUSTOM_ITEMS),
        )
        for relative in relatives:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, target)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(
            self.project,
            manifest=self.project / validator.MANIFEST,
            compiled=self.project / validator.COMPILED,
        )

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def recipe(payload: dict, recipe_id: str) -> dict:
        return next(row for row in payload["recipes"] if row["id"] == recipe_id)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_one_grit_yield_is_pinned(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, validator.DESH_FEED)["outputs"][0]["count"] = 2
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("feed_to_grit" in failure and "outputs" in failure for failure in self.failures()))

    def test_03_raw_feed_tag_cannot_be_dropped(self) -> None:
        self.mutate_json(
            validator.DESH_FEED_TAG,
            lambda value: value["values"].remove("#c:raw_materials/desh"),
        )
        self.assertTrue(any("crushing feed tag" in failure for failure in self.failures()))

    def test_04_rocketnautics_feed_cannot_be_dropped(self) -> None:
        self.mutate_json(
            validator.DESH_FEED_TAG,
            lambda value: value["values"].remove("rocketnautics_addon:mars_desh_ore"),
        )
        self.assertTrue(any("crushing feed tag" in failure for failure in self.failures()))

    def test_05_exact_shortcut_removal_is_required(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, validator.DESH_REDUCE)["remove"].pop()
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("36-ID" in failure for failure in self.failures()))

    def test_06_broad_removal_fails(self) -> None:
        def safe_mutate(value: dict) -> None:
            self.recipe(value, validator.DESH_PLATE)["remove_by_output"] = "ad_astra:desh_plate"
        self.mutate_json(validator.SEED, safe_mutate)
        self.assertTrue(any("broad removal" in failure for failure in self.failures()))

    def test_07_packing_recipe_must_survive(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: value["additional_removals"].append("ad_astra:desh_block"),
        )
        self.assertTrue(any("packing preservation" in failure for failure in self.failures()))

    def test_08_desh_acid_charge_is_pinned(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, validator.DESH_LEACH)["ingredients"][1]["amount"] = 100
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("concentrate_leaching ingredients drifted" in failure for failure in self.failures()))

    def test_09_ostrum_requires_firebrick_vat(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, validator.OSTRUM_LEACH)["vat_mode"] = "steel"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("vat_mode drifted" in failure for failure in self.failures()))

    def test_10_reduction_requires_heated_two_electrodes(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, validator.OSTRUM_REDUCE)["machine_mode"] = "mixing"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("machine_mode drifted" in failure for failure in self.failures()))

    def test_11_plate_requires_refined_radiance_press(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, validator.DESH_PLATE)["machine"] = "create:mechanical_press"
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("machine drifted" in failure for failure in self.failures()))

    def test_12_mars_navigation_remains_exact_5x5(self) -> None:
        def mutate(value: dict) -> None:
            self.recipe(value, validator.MARS_NAV)["pattern"].pop()
        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("pattern drifted" in failure for failure in self.failures()))

    def test_13_custom_item_registration_is_required(self) -> None:
        path = self.project / validator.ITEMS_JAVA
        source = path.read_text(encoding="utf-8-sig").replace(
            'ITEMS.registerSimpleItem("desh_grit")', 'ITEMS.registerSimpleItem("missing_desh_grit")'
        )
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("item registration drifted: desh_grit" in failure for failure in self.failures()))

    def test_14_external_model_texture_is_pinned(self) -> None:
        self.mutate_json(
            validator.MODEL_DIR / "ostrum_concentrate.json",
            lambda value: value["textures"].__setitem__("layer0", "minecraft:item/diamond"),
        )
        self.assertTrue(any("external-texture item model drifted" in failure for failure in self.failures()))

    def test_15_node_unlocks_are_pinned(self) -> None:
        def mutate(value: dict) -> None:
            value["nodes"][validator.MARTIAN_NODE]["unlocks"].pop()
        self.mutate_json(validator.ASSIGNMENTS, mutate)
        self.assertTrue(any("unlock assignment drifted" in failure for failure in self.failures()))

    def test_16_moon_loot_cannot_grant_manufactured_hardware(self) -> None:
        def mutate(value: dict) -> None:
            value["pools"][0]["entries"].append({"type": "minecraft:item", "name": "ad_astra:launch_pad"})
        self.mutate_json(validator.MOON_LOOT[0], mutate)
        self.assertTrue(any("only modest raw Desh" in failure for failure in self.failures()))

    def test_17_moon_loot_raw_desh_quantity_is_bounded(self) -> None:
        def mutate(value: dict) -> None:
            value["pools"][0]["entries"][0]["functions"][0]["count"]["max"] = 64.0
        self.mutate_json(validator.MOON_LOOT[1], mutate)
        self.assertTrue(any("quantity is not modest" in failure for failure in self.failures()))

    def test_18_arrival_advancement_cannot_reward(self) -> None:
        self.mutate_json(
            validator.ADVANCEMENTS["moon_arrival"][0],
            lambda value: value.__setitem__("rewards", {"experience": 10}),
        )
        self.assertTrue(any("no-reward observation" in failure for failure in self.failures()))

    def test_19_freight_quantity_is_pinned(self) -> None:
        def mutate(value: dict) -> None:
            quest = next(row for row in value["chapter"]["quests"] if row["key"] == "ostrum_freight")
            quest["tasks"][0]["count"] = 1
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("observation set drifted: ostrum_freight" in failure for failure in self.failures()))

    def test_20_quest_consumption_fails(self) -> None:
        def mutate(value: dict) -> None:
            quest = next(row for row in value["chapter"]["quests"] if row["key"] == "desh_metallurgy")
            quest["tasks"][0]["consume_items"] = True
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("consumes observed items" in failure for failure in self.failures()))

    def test_21_quest_reward_fails(self) -> None:
        def mutate(value: dict) -> None:
            quest = next(row for row in value["chapter"]["quests"] if row["key"] == "mars_navigation_computer")
            quest["rewards"] = [{"type": "item", "item": "minecraft:diamond"}]
        self.mutate_json(validator.QUESTS, mutate)
        self.assertTrue(any("gate or reward" in failure for failure in self.failures()))

    def test_22_generated_chapter_staleness_fails(self) -> None:
        self.mutate_json(
            validator.NATIVE_CHAPTER,
            lambda value: value["quests"].pop(),
        )
        self.assertTrue(any("generated Planetary Industry" in failure for failure in self.failures()))

    def test_23_compiled_one_grit_contract_is_pinned(self) -> None:
        def mutate(value: dict) -> None:
            card = next(row for row in value["recipes"] if row["recipeId"] == validator.OSTRUM_FEED)
            card["slots"]["output0"]["count"] = 2
        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("compiled one-grit feed contract" in failure for failure in self.failures()))

    def test_24_compiled_packing_removal_fails(self) -> None:
        def mutate(value: dict) -> None:
            value["removals"].append({"recipeId": "ad_astra:ostrum_block", "output": "", "input": "", "mod": ""})
        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("preserved packing recipe" in failure for failure in self.failures()))

    def test_25_finished_metal_block_in_structure_fails(self) -> None:
        spec = validator.structure_builder.STRUCTURE_OVERRIDES[0]
        relative = Path("src/main/resources") / spec.entry
        path = self.project / relative
        raw = gzip.decompress(path.read_bytes())
        raw = raw.replace(spec.new, spec.old, 1)
        path.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
        failures = self.failures()
        self.assertTrue(any("structure palette bypass" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
