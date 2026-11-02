#!/usr/bin/env python3
"""Mutation tests for the capstone actinide-reachability boundary."""

from __future__ import annotations

import copy
import json
import unittest
from collections import defaultdict

import validate_capstone_reachability as validator


class CapstoneReachabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.project = validator.PROJECT_ROOT
        cls.catalog = validator.DEFAULT_CATALOG
        cls.mods = validator.DEFAULT_MODS
        scripts = cls.project / "pack-scripts" / "server_scripts"
        cls.bridge = (scripts / validator.BRIDGE_SCRIPT).read_text(encoding="utf-8-sig")
        cls.black = (scripts / "industrial_black_hole_megaproject.js").read_text(
            encoding="utf-8-sig"
        )
        cls.reserve = (scripts / "industrial_reserve_core_megaproject.js").read_text(
            encoding="utf-8-sig"
        )
        cls.star = (scripts / "industrial_star_megaproject.js").read_text(
            encoding="utf-8-sig"
        )
        cls.quests = validator.read_json(
            cls.project / "progression" / "industrial_megaprojects.json"
        )

        recipes = validator.read_csv(cls.catalog / "recipes.csv")
        cls.recipes_by_id = defaultdict(list)
        for row in recipes:
            cls.recipes_by_id[row["recipe_id"]].append(row)
        cls.refs = validator.read_csv(cls.catalog / "recipe_refs.csv")
        cls.raw = {
            recipe_id: validator.load_raw_recipe(cls.recipes_by_id[recipe_id][0], cls.mods)
            for recipe_id in validator.STOCK_ROUTE_IDS
        }
        cls.removals = validator.project_removal_ids(cls.project)

    @staticmethod
    def assert_failure(errors: list[str], fragment: str) -> None:
        if not any(fragment in error for error in errors):
            raise AssertionError(f"expected failure containing {fragment!r}; got {errors}")

    def test_01_current_installed_route_passes(self) -> None:
        errors, report = validator.validate(self.project, self.catalog, self.mods)
        self.assertEqual([], errors)
        self.assertEqual(512, report["reserve_core_plutonium_pellets"])
        self.assertEqual(5120, report["minimum_blutonium_ingots_for_reserve_core"])
        self.assertFalse(report["mekanism_generators_installed"])

    def test_02_mekanism_generators_presence_changes_contract(self) -> None:
        errors = validator.validate_mod_contract({"mekanism", "mekanismgenerators"})
        self.assert_failure(errors, "Generators is installed")

    def test_03_base_mekanism_is_required(self) -> None:
        self.assert_failure(validator.validate_mod_contract(set()), "base Mekanism")

    def test_04_bridge_recipe_type_is_exact(self) -> None:
        mutated = self.bridge.replace("mekanism:dissolution", "mekanism:centrifuging")
        self.assert_failure(validator.validate_bridge_text(mutated), "dissolution type")

    def test_05_bridge_acid_amount_is_exact(self) -> None:
        mutated = self.bridge.replace("amount: 1, chemical", "amount: 2, chemical")
        self.assert_failure(validator.validate_bridge_text(mutated), "one unit")

    def test_06_bridge_blutonium_count_is_exact(self) -> None:
        mutated = self.bridge.replace("count: 1, item", "count: 2, item")
        self.assert_failure(validator.validate_bridge_text(mutated), "one Blutonium")

    def test_07_bridge_waste_yield_is_exact(self) -> None:
        mutated = self.bridge.replace("amount: 1000, id", "amount: 100, id")
        self.assert_failure(validator.validate_bridge_text(mutated), "1000 units")

    def test_08_bridge_per_tick_usage_is_required(self) -> None:
        mutated = self.bridge.replace("per_tick_usage: true", "per_tick_usage: false")
        self.assert_failure(validator.validate_bridge_text(mutated), "per-tick")

    def test_09_second_bridge_recipe_is_rejected(self) -> None:
        mutated = self.bridge.replace("  console.info", "  event.custom({type: 'x:y'}).id('x:y')\n  console.info")
        self.assert_failure(validator.validate_bridge_text(mutated), "exactly one custom")

    def test_10_broad_removal_cannot_hide_in_bridge(self) -> None:
        mutated = self.bridge.replace(
            "  console.info",
            "  event.remove({ output: 'mekanism:pellet_plutonium' })\n  console.info",
        )
        self.assert_failure(validator.validate_bridge_text(mutated), "broad or unrelated")

    def test_11_current_stock_payloads_and_references_pass(self) -> None:
        self.assertEqual(
            [],
            validator.validate_stock_contract(
                self.recipes_by_id, self.refs, self.raw, self.removals
            ),
        )

    def test_12_missing_stock_waste_to_plutonium_recipe_fails(self) -> None:
        recipes = copy.deepcopy(self.recipes_by_id)
        recipes[validator.PLUTONIUM_RECIPE] = []
        self.assert_failure(
            validator.validate_stock_contract(recipes, self.refs, self.raw, self.removals),
            "must contain exactly one retained",
        )

    def test_13_missing_stock_plutonium_pellet_recipe_fails(self) -> None:
        recipes = copy.deepcopy(self.recipes_by_id)
        recipes[validator.PELLET_RECIPE] = []
        self.assert_failure(
            validator.validate_stock_contract(recipes, self.refs, self.raw, self.removals),
            validator.PELLET_RECIPE,
        )

    def test_14_stock_payload_drift_fails(self) -> None:
        raw = copy.deepcopy(self.raw)
        raw[validator.PLUTONIUM_RECIPE]["input"]["amount"] = 100
        self.assert_failure(
            validator.validate_stock_contract(
                self.recipes_by_id, self.refs, raw, self.removals
            ),
            "payload changed",
        )

    def test_15_exact_removal_of_stock_route_fails(self) -> None:
        removals = set(self.removals) | {validator.PELLET_RECIPE}
        self.assert_failure(
            validator.validate_stock_contract(
                self.recipes_by_id, self.refs, self.raw, removals
            ),
            "exactly removed",
        )

    def test_16_scripted_exact_removal_of_stock_route_is_detected(self) -> None:
        observed = validator.scripted_stock_removals(
            [
                "ServerEvents.recipes(event => event.remove({ id: "
                "'mekanism:processing/lategame/plutonium' }))"
            ]
        )
        self.assertEqual({validator.PLUTONIUM_RECIPE}, observed)

    def test_17_conflicting_catalog_waste_source_fails(self) -> None:
        refs = copy.deepcopy(self.refs)
        refs.append(
            {
                "recipe_id": "test:cheap_waste",
                "role": "output",
                "kind": "chemical",
                "resource_id": validator.NUCLEAR_WASTE,
                "count": "1000.0",
            }
        )
        self.assert_failure(
            validator.validate_stock_contract(
                self.recipes_by_id, refs, self.raw, self.removals
            ),
            "conflicting installed",
        )

    def test_18_second_scripted_waste_source_fails(self) -> None:
        errors = validator.validate_scripted_waste_sources(
            {
                validator.BRIDGE_SCRIPT: self.bridge,
                "cheap_waste.js": (
                    "ServerEvents.recipes(event => event.custom({"
                    "output: {amount: 1000, id: 'mekanism:nuclear_waste'}"
                    "}).id('test:cheap_waste'))"
                ),
            }
        )
        self.assert_failure(errors, "conflicting scripted")

    def test_19_current_capstone_chain_passes(self) -> None:
        self.assertEqual(
            [],
            validator.validate_capstone_texts(
                self.black, self.reserve, self.star, self.quests
            ),
        )

    def test_20_reserve_core_loop_count_is_exact(self) -> None:
        mutated = self.reserve.replace("loops: 512", "loops: 511")
        self.assert_failure(
            validator.validate_capstone_texts(
                self.black, mutated, self.star, self.quests
            ),
            "512",
        )

    def test_21_reserve_core_requires_plutonium_each_loop(self) -> None:
        mutated = self.reserve.replace(
            "mekanism:pellet_plutonium", "mekanism:pellet_polonium"
        )
        self.assert_failure(
            validator.validate_capstone_texts(
                self.black, mutated, self.star, self.quests
            ),
            "one Plutonium Pellet",
        )

    def test_22_star_requires_black_hole(self) -> None:
        mutated = self.star.replace(validator.BLACK_HOLE, "minecraft:stone")
        self.assert_failure(
            validator.validate_capstone_texts(
                self.black, self.reserve, mutated, self.quests
            ),
            "Black Hole",
        )

    def test_23_star_requires_reserve_core(self) -> None:
        mutated = self.star.replace(validator.RESERVE_CORE, "minecraft:dirt")
        self.assert_failure(
            validator.validate_capstone_texts(
                self.black, self.reserve, mutated, self.quests
            ),
            "Reserve Core",
        )

    def test_24_guidance_dependency_chain_is_exact(self) -> None:
        quests = copy.deepcopy(self.quests)
        next(row for row in quests["quests"] if row["key"] == "industrial_star")[
            "dependencies"
        ] = ["black_hole"]
        self.assert_failure(
            validator.validate_capstone_texts(
                self.black, self.reserve, self.star, quests
            ),
            "dependency chain",
        )

    def test_25_reserve_core_native_deployer_fallback_fails(self) -> None:
        mutated = self.reserve.replace(
            "industrial_colonies:creative_deploying", "create:deploying", 1
        )
        self.assert_failure(
            validator.validate_capstone_texts(
                self.black, mutated, self.star, self.quests
            ),
            "exact nested machine",
        )

    def test_26_reserve_core_native_press_fallback_fails(self) -> None:
        mutated = self.reserve.replace(
            "industrial_colonies:creative_pressing", "create:pressing", 1
        )
        self.assert_failure(
            validator.validate_capstone_texts(
                self.black, mutated, self.star, self.quests
            ),
            "exact nested machine",
        )

    def test_27_reserve_core_native_spout_fallback_fails(self) -> None:
        mutated = self.reserve.replace(
            "industrial_colonies:brass_filling", "create:filling", 1
        )
        self.assert_failure(
            validator.validate_capstone_texts(
                self.black, mutated, self.star, self.quests
            ),
            "exact nested machine",
        )


if __name__ == "__main__":
    unittest.main()
