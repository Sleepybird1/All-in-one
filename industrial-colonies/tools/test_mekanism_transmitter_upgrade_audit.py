#!/usr/bin/env python3
"""Focused mutation tests for the implemented Mekanism transmitter ladders."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_managed_recipe_manifest as builder  # noqa: E402
import validate_mekanism_transmitter_upgrade_audit as validator  # noqa: E402


class MekanismTransmitterUpgradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_object(validator.DEFAULT_PLAN)
        cls.seed = validator.load_object(validator.DEFAULT_SEED)
        cls.assignments = validator.load_object(validator.DEFAULT_ASSIGNMENTS)
        cls.mods = validator.default_mods()
        cls.manifest, report = builder.build_manifest(
            builder.DEFAULT_SEED,
            builder.DEFAULT_ASSIGNMENTS,
            builder.DEFAULT_DEPENDENCIES,
            builder.default_catalog(),
            cls.mods,
        )
        if report.get("fatal_errors"):
            raise AssertionError(report["fatal_errors"])

    def check(self, *, plan=None, seed=None, manifest=None, assignments=None):
        return validator.validate(
            self.plan if plan is None else plan,
            validator.DEFAULT_CATALOG,
            self.manifest if manifest is None else manifest,
            self.mods,
            self.seed if seed is None else seed,
            self.assignments if assignments is None else assignments,
        )

    @staticmethod
    def recipe(data, identity: str):
        for recipe in data["replacement_contracts"]:
            if recipe.get("id") == identity:
                return recipe
        raise AssertionError(f"missing reviewed recipe {identity}")

    def test_current_implementation_passes(self) -> None:
        self.assertEqual([], self.check())

    def test_status_is_implemented(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "review_only"
        self.assertTrue(any("status must be implemented_in_seed" in error for error in self.check(plan=plan)))

    def test_missing_non_universal_seed_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        identity = validator.managed_id("advanced", "logistical_transporter")
        seed["recipes"] = [recipe for recipe in seed["recipes"] if recipe.get("id") != identity]
        self.assertTrue(any("absent from authoritative seed" in error for error in self.check(seed=seed)))

    def test_non_universal_seed_field_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        identity = validator.managed_id("elite", "mechanical_pipe")
        validator.recipes_by_id(seed)[identity]["machine"] = validator.PRESS["advanced"]
        self.assertTrue(any("authoritative seed differs" in error for error in self.check(seed=seed)))

    def test_duplicate_non_universal_owner_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        identity = validator.managed_id("ultimate", "pressurized_tube")
        duplicate = copy.deepcopy(validator.recipes_by_id(manifest)[identity])
        duplicate["id"] = "industrial_colonies:test/duplicate_ultimate_pressurized_tube"
        manifest["recipes"].append(duplicate)
        self.assertTrue(any("does not have one assembled owner" in error for error in self.check(manifest=manifest)))

    def test_retired_automatic_universal_route_cannot_return(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"].append(validator.seed_spec(self.plan["replacement_contracts"][0]))
        self.assertTrue(any("retired automatic Universal Cable ID survived" in error for error in self.check(seed=seed)))

    def test_source_owned_universal_manifest_id_is_required(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        identity = validator.source_universal_id("elite")
        manifest["recipes"] = [recipe for recipe in manifest["recipes"] if recipe.get("id") != identity]
        self.assertTrue(any("source-owned Universal Cable managed ID is absent" in error for error in self.check(manifest=manifest)))

    def test_basic_route_remains_untouched(self) -> None:
        seed = copy.deepcopy(self.seed)
        identity = validator.basic_recipe("mechanical_pipe")
        validator.recipes_by_id(seed)[identity]["output"] = "4x mekanism:basic_mechanical_pipe"
        self.assertTrue(any("authoritative Basic seed route changed" in error for error in self.check(seed=seed)))

    def test_assignment_append_order_is_locked(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"][validator.NODE["ultimate"]]["unlocks"]
        left = unlocks.index(validator.item_id("ultimate", "logistical_transporter"))
        right = unlocks.index(validator.item_id("ultimate", "mechanical_pipe"))
        unlocks[left], unlocks[right] = unlocks[right], unlocks[left]
        self.assertTrue(any("preserve the locked transmitter sequence" in error for error in self.check(assignments=assignments)))

    def test_factory_suffix_order_is_locked(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"][validator.NODE["elite"]]["unlocks"]
        unlocks[-1], unlocks[-2] = unlocks[-2], unlocks[-1]
        self.assertTrue(any("exact Factory additions" in error for error in self.check(assignments=assignments)))

    def test_moved_chemical_factory_cannot_return_to_prefix(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"][validator.NODE["advanced"]]["unlocks"]
        unlocks.insert(-2, "mekanism:advanced_purifying_factory")
        self.assertTrue(any("exact Factory removals" in error for error in self.check(assignments=assignments)))

    def test_exact_stock_removal_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        identity = validator.managed_id("advanced", "mechanical_pipe")
        self.recipe(plan, identity)["remove_exact"] = [validator.stock_id("advanced", "pressurized_tube")]
        self.assertTrue(any("exact stock removal changed" in error for error in self.check(plan=plan)))

    def test_output_count_is_eight(self) -> None:
        plan = copy.deepcopy(self.plan)
        identity = validator.managed_id("elite", "logistical_transporter")
        self.recipe(plan, identity)["output"] = "7x mekanism:elite_logistical_transporter"
        self.assertTrue(any("output must be eight" in error for error in self.check(plan=plan)))

    def test_exact_press_binding_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        identity = validator.managed_id("ultimate", "thermodynamic_conductor")
        self.recipe(plan, identity)["machine"] = validator.REFINED_PRESS
        self.assertTrue(any("wrong Encased press" in error for error in self.check(plan=plan)))

    def test_dependency_chain_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        identity = validator.managed_id("ultimate", "mechanical_pipe")
        self.recipe(plan, identity)["depends_on_batch"].remove(
            validator.managed_id("elite", "mechanical_pipe")
        )
        self.assertTrue(any("dependency set changed" in error for error in self.check(plan=plan)))

    def test_family_specific_infrastructure_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        identity = validator.managed_id("ultimate", "logistical_transporter")
        recipe = self.recipe(plan, identity)
        recipe["inputs"] = [value for value in recipe["inputs"] if value != "create:redstone_requester"]
        self.assertTrue(any("missing family-specific infrastructure" in error for error in self.check(plan=plan)))

    def test_preserved_universal_evidence_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["preserved_universal_managed_ids"][2]["output_count"] = 1
        self.assertTrue(any("preserved Universal Cable evidence changed" in error for error in self.check(plan=plan)))


if __name__ == "__main__":
    unittest.main()
