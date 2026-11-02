#!/usr/bin/env python3
"""Mutation tests for the Mekanism pre-nuclear machine-chain audit."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_mekanism_pre_nuclear_patch_plan as patch_builder
import validate_mekanism_pre_nuclear_machine_chain_audit as validator


class MekanismPreNuclearMachineChainAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.DEFAULT_PLAN)
        cls.automatic_plan = validator.load_json(validator.DEFAULT_AUTOMATIC_PLAN)
        cls.seed = validator.load_json(validator.DEFAULT_SEED)
        cls.assignments = validator.load_json(validator.DEFAULT_ASSIGNMENTS)

    def failures(
        self,
        *,
        plan=None,
        automatic_plan=None,
        seed=None,
        assignments=None,
        compile_batch: bool = False,
    ) -> list[str]:
        try:
            return validator.validate_plan(
                self.plan if plan is None else plan,
                self.automatic_plan if automatic_plan is None else automatic_plan,
                validator.DEFAULT_AUTOMATIC_PLAN,
                validator.DEFAULT_AUTOMATIC_SNAPSHOT,
                validator.DEFAULT_CATALOG,
                validator.DEFAULT_MODS,
                self.seed if seed is None else seed,
                self.assignments if assignments is None else assignments,
                validator.DEFAULT_PHYSICAL_TIERS,
                validator.DEFAULT_BRANCH_LAYOUT,
                compile_batch=compile_batch,
            )
        except (ValueError, KeyError) as error:
            return [str(error)]

    def contract(self, plan: dict, suffix: str) -> dict:
        return next(value for value in plan["replacement_contracts"] if value["id"].endswith(suffix))

    def source(self, plan: dict, identity: str) -> dict:
        return next(value for value in plan["source_recipes"] if value["id"] == identity)

    def assert_rejected(self, failures: list[str], phrase: str) -> None:
        self.assertTrue(any(phrase in value for value in failures), failures)

    def test_01_full_implemented_contract_compiles(self) -> None:
        self.assertEqual([], self.failures(compile_batch=True))

    def test_02_installed_source_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["source_recipes"][0]["sha256"] = "0" * 64
        self.assert_rejected(self.failures(plan=plan), "installed source JSON hash changed")

    def test_03_catalog_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["recipe_catalog_sha256"] = "0" * 64
        self.assert_rejected(self.failures(plan=plan), "recipe catalog hash changed")

    def test_04_priority_batch_order_drift_is_rejected(self) -> None:
        automatic = copy.deepcopy(self.automatic_plan)
        batch = next(
            value
            for value in automatic["implementation_batches"]
            if value["id"] == "mekanism_pre_nuclear_machine_chain"
        )
        batch["outputs"][0], batch["outputs"][1] = batch["outputs"][1], batch["outputs"][0]
        failures = self.failures(automatic_plan=automatic)
        self.assert_rejected(failures, "output order changed")

    def test_05_automatic_owner_inventory_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_automatic_owners"][0]["managed_id"] = "industrial_colonies:auto/mekanism/not_real"
        self.assert_rejected(self.failures(plan=plan), "exactly eight ids")

    def test_06_default_create_press_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/enrichment_chamber")["machine"] = "create:mechanical_press"
        self.assert_rejected(self.failures(plan=plan), "machine-role mapping changed")

    def test_07_downstream_industrial_press_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/chemical_infuser")["machine"] = "createcasing:industrial_iron_press"
        self.assert_rejected(self.failures(plan=plan), "machine-role mapping changed")

    def test_08_precision_sawmill_requires_brass_press(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/precision_sawmill")["machine"] = "createcasing:railway_press"
        self.assert_rejected(self.failures(plan=plan), "machine-role mapping changed")

    def test_09_separator_requires_both_tfmg_electrodes(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/electrolytic_separator")["inputs"].remove("tfmg:zinc_electrode")
        self.assert_rejected(self.failures(plan=plan), "missing required manufactured inputs")

    def test_10_enrichment_requires_tfmg_circuit_board(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/enrichment_chamber")["inputs"].remove("tfmg:circuit_board")
        self.assert_rejected(self.failures(plan=plan), "missing required manufactured inputs")

    def test_11_crusher_requires_matched_crushing_wheels(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/crusher")["inputs"][1] = "create:crushing_wheel"
        self.assert_rejected(self.failures(plan=plan), "matched pair")

    def test_12_osmium_compressor_requires_tfmg_pressure_body(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/osmium_compressor")["inputs"].remove("tfmg:steel_chemical_vat")
        self.assert_rejected(self.failures(plan=plan), "missing required manufactured inputs")

    def test_13_oxidizer_requires_fan_driven_vat(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/chemical_oxidizer")["inputs"].remove("create:encased_fan")
        self.assert_rejected(self.failures(plan=plan), "missing required manufactured inputs")

    def test_14_infuser_requires_dual_feed_hardware(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/chemical_infuser")["inputs"][1] = "mekanism:basic_chemical_tank"
        self.assert_rejected(self.failures(plan=plan), "dual-feed input")

    def test_15_prc_rejects_hdpe_bootstrap(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/pressurized_reaction_chamber")["inputs"].append("mekanism:hdpe_sheet")
        self.assert_rejected(self.failures(plan=plan), "forbidden downstream inputs")

    def test_16_prc_requires_enrichment_predecessor(self) -> None:
        plan = copy.deepcopy(self.plan)
        prc = self.contract(plan, "/pressurized_reaction_chamber")
        prc["inputs"].remove("mekanism:enrichment_chamber")
        prc["depends_on"].remove(validator.ENRICHMENT_ID)
        self.assert_rejected(self.failures(plan=plan), "missing required manufactured inputs")

    def test_17_same_batch_dependency_cycle_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        enrichment = self.contract(plan, "/enrichment_chamber")
        enrichment["inputs"].append("mekanism:pressurized_reaction_chamber")
        enrichment["depends_on"].append(validator.PRC_ID)
        failures = self.failures(plan=plan)
        self.assertTrue(
            any("dependency cycle" in value for value in failures)
            or any("forbidden downstream inputs" in value for value in failures),
            failures,
        )

    def test_18_sulfuric_acid_dependency_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/chemical_oxidizer")["inputs"].append("tfmg:sulfuric_acid")
        failures = self.failures(plan=plan)
        self.assert_rejected(failures, "sulfuric-acid boundary")

    def test_19_mek_data_state_disclosure_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["state_transfer_policy"]["mek_data_source_ids"].remove("mekanism:chemical_infuser")
        self.assert_rejected(self.failures(plan=plan), "state-transfer source inventory changed")

    def test_20_fresh_empty_output_policy_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/pressurized_reaction_chamber")["output_state"] = "transfer_input_state"
        self.assert_rejected(self.failures(plan=plan), "fresh-empty output-state contract changed")

    def test_21_assignment_relative_order_drift_is_rejected(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        unlocks = assignments["nodes"]["CR01 — Electrochemical Engineering"]["unlocks"]
        left = unlocks.index("mekanism:chemical_infuser")
        right = unlocks.index("mekanism:chemical_oxidizer")
        unlocks[left], unlocks[right] = unlocks[right], unlocks[left]
        self.assert_rejected(self.failures(assignments=assignments), "assignment relative order drifted")

    def test_22_duplicate_explicit_output_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"].append(
            {
                "id": "industrial_colonies:test/collision",
                "phase": "Mekanized Industry",
                "type": "shapeless",
                "inputs": ["minecraft:stone"],
                "output": "mekanism:crusher",
                "remove": [],
                "exclusive_output": True,
            }
        )
        self.assert_rejected(self.failures(seed=seed), "implemented output owner set changed")

    def test_23_patch_builder_is_deterministic_and_nonmutating(self) -> None:
        seed_before = copy.deepcopy(self.seed)
        assignments_before = copy.deepcopy(self.assignments)
        first = patch_builder.build_patch_plan(self.plan, self.seed, self.assignments)
        second = patch_builder.build_patch_plan(self.plan, self.seed, self.assignments)
        self.assertEqual(first, second)
        self.assertEqual("implemented_source_owned_noop", first["mode"])
        self.assertEqual([], first["assignments"]["changes"])
        self.assertEqual(seed_before, self.seed)
        self.assertEqual(assignments_before, self.assignments)

    def test_24_exact_source_removal_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/crusher")["remove"] = ["mekanism:not_the_crusher"]
        self.assert_rejected(self.failures(plan=plan), "exact source removal set drifted")

    def test_25_stale_review_status_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "review_ready_no_shared_mutation"
        self.assert_rejected(self.failures(plan=plan), "status must be implemented_in_seed")

    def test_26_missing_implemented_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if recipe.get("id") != validator.ENRICHMENT_ID
        ]
        self.assert_rejected(self.failures(seed=seed), "implemented recipe is absent from seed")

    def test_27_implemented_recipe_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = next(row for row in seed["recipes"] if row.get("id") == validator.PRC_ID)
        recipe["machine"] = "createcasing:brass_press"
        self.assert_rejected(self.failures(seed=seed), "implemented recipe differs from reviewed contract")

    def test_28_seed_implementation_metadata_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["seed_implementation"]["automatic_owners_retired"] = 7
        self.assert_rejected(self.failures(plan=plan), "seed implementation metadata drifted")

    def test_29_rebased_assignment_hash_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["rebased_assignments_sha256"] = "0" * 64
        self.assert_rejected(self.failures(plan=plan), "rebased assignment hash changed")

    def test_30_physical_authority_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["physical_tiers_sha256"] = "0" * 64
        self.assert_rejected(self.failures(plan=plan), "physical tier authority hash changed")

    def test_31_physical_authority_path_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["physical_tiers"] = "progression/not_the_authority.json"
        self.assert_rejected(self.failures(plan=plan), "physical tier authority path metadata changed")

    def test_32_patch_builder_enforces_and_reports_physical_authority(self) -> None:
        patch = patch_builder.build_patch_plan(self.plan, self.seed, self.assignments)
        self.assertEqual(
            {
                "path": "progression/physical_recipe_tiers.json",
                "sha256": "B1A201A9385FA4C218AD74198A8CFABF620B01C401F12C706C41D8883D0E8ED5",
            },
            patch["preconditions"]["physical_tier_authority"],
        )
        plan = copy.deepcopy(self.plan)
        plan["scope"]["physical_tiers_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            patch_builder.PatchPlanError, "physical tier authority hash changed"
        ):
            patch_builder.build_patch_plan(plan, self.seed, self.assignments)

    def test_33_patch_builder_tracks_tfmg_results_and_rejects_alias_conflicts(self) -> None:
        recipe = {
            "id": "industrial_colonies:test/vat",
            "results": [{"kind": "ITEM", "id": "minecraft:clay_ball", "count": 2}],
        }
        self.assertEqual(["minecraft:clay_ball"], patch_builder.output_ids(recipe))
        recipe["outputs"] = [{"kind": "ITEM", "id": "minecraft:brick"}]
        with self.assertRaisesRegex(
            patch_builder.PatchPlanError, "conflicting outputs/results values"
        ):
            patch_builder.output_ids(recipe)


if __name__ == "__main__":
    unittest.main()
