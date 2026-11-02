#!/usr/bin/env python3
"""Focused regression tests for the managed physical-progression contracts."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from generate_managed_recipe_overhaul import expand_manifest
from validate_ae2_transform_hardening import (
    FORWARD_CELL_UPGRADES,
    validate_contract as validate_ae2_transform_contract,
)
from validate_late_machine_hardening import (
    DEFERRED_RECIPE_IDS,
    validate_contract as validate_late_machine_contract,
)
from validate_mekanism_transmission_foundation import (
    INFINITE_CELL_RETIREMENTS,
    validate_contract as validate_transmission_contract,
)
from validate_progression_bypass_retirement import (
    EXACT_RECIPE_RETIREMENTS,
    PROTECTED_FACTORY_ROUTES,
    validate_contract as validate_bypass_retirement_contract,
)
from validate_physical_progression import PROJECT, validate_managed_physical_contract
from validate_physical_tier_migration import validate_tier_contract


MANIFEST_PATH = PROJECT / "progression" / "managed_recipe_overhaul.json"
COMPILED_PATH = PROJECT / "pack-kjsgen" / "default.managed.json"
SEED_PATH = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
ASSIGNMENTS_PATH = PROJECT / "progression" / "machine_node_assignments.json"


class PhysicalProgressionValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = json.loads(SEED_PATH.read_text(encoding="utf-8-sig"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
        cls.compiled = json.loads(COMPILED_PATH.read_text(encoding="utf-8-sig"))
        cls.assignments = json.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8-sig"))
        cls.specs = expand_manifest(cls.manifest)

    def test_current_contract_passes(self) -> None:
        self.assertEqual(
            [],
            validate_managed_physical_contract(PROJECT, self.manifest, self.specs),
        )
        errors, _ = validate_tier_contract(self.manifest, self.specs)
        self.assertEqual([], errors)
        self.assertEqual(
            [], validate_ae2_transform_contract(self.manifest, self.compiled)
        )
        self.assertEqual(
            [], validate_late_machine_contract(self.manifest, self.compiled)
        )
        self.assertEqual(
            [],
            validate_transmission_contract(
                self.seed, self.manifest, self.compiled, self.assignments
            ),
        )
        assignments = self.assignments
        self.assertEqual(
            [],
            validate_bypass_retirement_contract(
                self.manifest, self.compiled, assignments
            ),
        )

    def test_missing_forward_cell_upgrade_removal_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        compiled = copy.deepcopy(self.compiled)
        recipe_id = sorted(FORWARD_CELL_UPGRADES)[0]
        manifest["additional_removals"].remove(recipe_id)
        compiled["removals"] = [
            entry
            for entry in compiled["removals"]
            if entry.get("recipeId") != recipe_id
        ]
        errors = validate_ae2_transform_contract(manifest, compiled)
        self.assertTrue(any(recipe_id in error for error in errors), errors)

    def test_removing_cell_disassembly_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        compiled = copy.deepcopy(self.compiled)
        recipe_id = "ae2:cell_upgrade/item_storage_cell_4k"
        manifest["additional_removals"].append(recipe_id)
        compiled["removals"].append({"recipeId": recipe_id})
        errors = validate_ae2_transform_contract(manifest, compiled)
        self.assertTrue(any("protected disassembly" in error for error in errors), errors)

    def test_missing_deferred_teleporter_removal_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        compiled = copy.deepcopy(self.compiled)
        recipe_id = sorted(DEFERRED_RECIPE_IDS)[0]
        manifest["additional_removals"].remove(recipe_id)
        compiled["removals"] = [
            entry
            for entry in compiled["removals"]
            if entry.get("recipeId") != recipe_id
        ]
        errors = validate_late_machine_contract(manifest, compiled)
        self.assertTrue(any(recipe_id in error for error in errors), errors)

    def test_wrong_pre_nuclear_encased_machine_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        recipe = next(
            value
            for value in manifest["recipes"]
            if value.get("id")
            == "industrial_colonies:mekanism_pre_nuclear/precision_sawmill"
        )
        recipe["machine"] = "create:mechanical_press"
        errors = validate_late_machine_contract(manifest, self.compiled)
        self.assertTrue(
            any("precision_sawmill escaped reviewed machine environment" in error for error in errors),
            errors,
        )

    def test_pre_nuclear_machine_cannot_revert_to_generic_5x5(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        recipe = next(
            value
            for value in manifest["recipes"]
            if value.get("id") == "industrial_colonies:mekanism_pre_nuclear/crusher"
        )
        recipe["type"] = "mechanical_crafting"
        errors = validate_late_machine_contract(manifest, self.compiled)
        self.assertTrue(
            any("crusher is not rebuilt with exact Create Encased compacting" in error for error in errors),
            errors,
        )

    def test_wrong_printed_silicon_machine_fails(self) -> None:
        specs = copy.deepcopy(self.specs)
        recipe = next(
            value
            for value in specs
            if value["id"] == "industrial_colonies:electronics/printed_silicon"
        )
        recipe["machine"] = "create:mechanical_press"
        errors = validate_managed_physical_contract(PROJECT, self.manifest, specs)
        self.assertTrue(any("printed silicon" in error for error in errors), errors)

    def test_retired_mekanism_steel_casing_producer_fails(self) -> None:
        specs = copy.deepcopy(self.specs)
        specs.append(
            {
                "id": "industrial_colonies:test/retired_steel_casing",
                "phase": "Mekanized Industry",
                "type": "shaped",
                "output": "mekanism:steel_casing",
                "pattern": ["S"],
                "key": {"S": "tfmg:steel_frame"},
            }
        )
        errors = validate_managed_physical_contract(PROJECT, self.manifest, specs)
        self.assertTrue(any("still has managed producer" in error for error in errors), errors)

    def test_retired_mekanism_steel_casing_consumer_fails(self) -> None:
        specs = copy.deepcopy(self.specs)
        recipe = next(
            value
            for value in specs
            if "tfmg:steel_frame" in json.dumps(value, sort_keys=True)
        )
        recipe.setdefault("inputs", []).append("mekanism:steel_casing")
        errors = validate_managed_physical_contract(PROJECT, self.manifest, specs)
        self.assertTrue(any("still consume retired" in error for error in errors), errors)

    def test_missing_retired_mekanism_steel_casing_removal_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["additional_removals"].remove("mekanism:steel_casing")
        errors = validate_managed_physical_contract(PROJECT, manifest, self.specs)
        self.assertTrue(any("stock recipe is not exactly removed" in error for error in errors), errors)

    def test_missing_progression_bypass_removal_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        compiled = copy.deepcopy(self.compiled)
        assignments = json.loads(
            (PROJECT / "progression" / "machine_node_assignments.json").read_text(
                encoding="utf-8-sig"
            )
        )
        recipe_id = sorted(EXACT_RECIPE_RETIREMENTS)[0]
        manifest["additional_removals"].remove(recipe_id)
        compiled["removals"] = [
            entry
            for entry in compiled["removals"]
            if entry.get("recipeId") != recipe_id
        ]
        errors = validate_bypass_retirement_contract(
            manifest, compiled, assignments
        )
        self.assertTrue(any(recipe_id in error for error in errors), errors)

    def test_removing_protected_factory_route_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        compiled = copy.deepcopy(self.compiled)
        assignments = json.loads(
            (PROJECT / "progression" / "machine_node_assignments.json").read_text(
                encoding="utf-8-sig"
            )
        )
        recipe_id = sorted(PROTECTED_FACTORY_ROUTES)[0]
        manifest["additional_removals"].append(recipe_id)
        compiled["removals"].append({"recipeId": recipe_id})
        errors = validate_bypass_retirement_contract(
            manifest, compiled, assignments
        )
        self.assertTrue(any("protected industrial" in error for error in errors), errors)

    def test_missing_infinite_cell_retirement_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        compiled = copy.deepcopy(self.compiled)
        recipe_id = sorted(INFINITE_CELL_RETIREMENTS)[0]
        manifest["additional_removals"].remove(recipe_id)
        compiled["removals"] = [
            entry
            for entry in compiled["removals"]
            if entry.get("recipeId") != recipe_id
        ]
        errors = validate_transmission_contract(
            self.seed, manifest, compiled, self.assignments
        )
        self.assertTrue(any(recipe_id in error for error in errors), errors)

    def test_future_transmitter_ingredient_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        recipe = next(
            value
            for value in manifest["recipes"]
            if value.get("id")
            == "industrial_colonies:mekanism/transmission/basic_universal_cable"
        )
        recipe["key"]["A"] = "mekanism:elite_control_circuit"
        errors = validate_transmission_contract(
            self.seed, manifest, self.compiled, self.assignments
        )
        self.assertTrue(
            any("not assigned to an earlier/current phase" in error for error in errors),
            errors,
        )

    def test_broken_family_order_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["machine_families"][4]["source_tier"] = "Copper"
        errors, _ = validate_tier_contract(manifest, self.specs)
        self.assertTrue(any("family chain changed" in error for error in errors), errors)

    def test_broad_scorched_alloyer_removal_fails(self) -> None:
        specs = copy.deepcopy(self.specs)
        recipe = next(
            value
            for value in specs
            if value["id"] == "industrial_colonies:heavy_industry/scorched_alloyer"
        )
        recipe["remove"] = ["modernfoundry:smeltery/scorched/alloyer", "modernfoundry:*"]
        errors = validate_managed_physical_contract(PROJECT, self.manifest, specs)
        self.assertTrue(any("Alloyer" in error for error in errors), errors)

    def test_small_mechanical_grid_fails(self) -> None:
        specs = copy.deepcopy(self.specs)
        recipe = next(value for value in specs if value.get("type") == "mechanical_crafting")
        recipe["pattern"] = ["AAA", "ABA", "AAA"]
        errors, _ = validate_tier_contract(self.manifest, specs)
        self.assertTrue(any("large-grid contract" in error for error in errors), errors)

    def test_reviewed_orbital_compact_grid_drift_fails(self) -> None:
        specs = copy.deepcopy(self.specs)
        recipe = next(
            value
            for value in specs
            if value.get("id")
            == "industrial_colonies:space/propulsion/hose_anchor"
        )
        recipe["pattern"] = ["HVH", "PCP"]
        errors, _ = validate_tier_contract(self.manifest, specs)
        self.assertTrue(
            any("changed its reviewed compact grid" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
