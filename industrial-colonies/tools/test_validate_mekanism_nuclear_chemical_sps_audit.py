#!/usr/bin/env python3
"""Mutation tests for the Mekanism nuclear chemistry/SPS audit."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_mekanism_nuclear_chemical_sps_audit as builder
import validate_mekanism_nuclear_chemical_sps_audit as validator


class MekanismNuclearChemicalSpsAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.DEFAULT_PLAN)
        cls.patch = validator.load_json(validator.DEFAULT_PATCH)
        cls.seed = validator.load_json(builder.SEED)
        cls.assignments = validator.load_json(builder.ASSIGNMENTS)
        cls.current = validator.load_json(builder.CURRENT_MANAGED)

    def failures(
        self,
        *,
        plan=None,
        patch=None,
        seed=None,
        assignments=None,
        current=None,
    ) -> list[str]:
        return validator.validate_plan(
            self.plan if plan is None else plan,
            self.patch if patch is None else patch,
            validator.DEFAULT_CATALOG,
            validator.DEFAULT_MODS,
            self.seed if seed is None else seed,
            self.assignments if assignments is None else assignments,
            self.current if current is None else current,
        )

    def contract(self, plan: dict, output: str) -> dict:
        return next(
            recipe
            for recipe in plan["replacement_contracts"]
            if builder.output_id(recipe) == output
        )

    def assert_failure(self, failures: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in failure for failure in failures),
            f"expected failure containing {fragment!r}; got {failures}",
        )

    def test_01_current_artifacts_pass(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_builder_is_byte_deterministic(self) -> None:
        plan, patch, markdown = builder.build_documents(
            validator.DEFAULT_CATALOG, validator.DEFAULT_MODS
        )
        self.assertEqual(self.plan, plan)
        self.assertEqual(self.patch, patch)
        self.assertEqual(validator.DEFAULT_MARKDOWN.read_text(encoding="utf-8"), markdown)

    def test_03_target_source_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["removed_installed_recipes"][0]["source_sha256"] = "0" * 64
        self.assert_failure(self.failures(plan=plan), "installed source JSON hash changed")

    def test_04_target_producer_audit_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["direct_producer_audit"]["mekanism:sps_casing"].append("other:sps_casing")
        self.assert_failure(self.failures(plan=plan), "direct target producer coverage drifted")

    def test_05_bypass_candidate_disposition_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["chain_bypass_audit"]["candidates"][0]["disposition"] = "exact_remove"
        self.assert_failure(self.failures(plan=plan), "bypass disposition drifted")

    def test_06_sensitive_survivor_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["chain_bypass_audit"]["active_survivors_after_exact_removals"][
            "mekanism:pellet_antimatter"
        ] = []
        self.assert_failure(self.failures(plan=plan), "post-removal sensitive survivor set drifted")

    def test_07_nonrecipe_external_acquisition_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["non_recipe_acquisition_audit"]["occurrences"][0]["role"] = (
            "external_acquisition_candidate"
        )
        self.assert_failure(self.failures(plan=plan), "non-recipe acquisition evidence drifted")

    def test_08_exact_target_removal_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:chemical_washer")["remove"] = []
        self.assert_failure(self.failures(plan=plan), "exact source removal list drifted")

    def test_09_unknown_ingredient_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:chemical_washer")["inputs"][0] = "missing:imaginary_vat"
        self.assert_failure(self.failures(plan=plan), "unknown catalog ingredient item")

    def test_10_non_tfmg_contract_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:chemical_dissolution_chamber")
        contract["inputs"] = [
            "mekanism:steel_casing" if validator.normalized_ref(value).startswith("tfmg:") else value
            for value in contract["inputs"]
        ]
        self.assert_failure(self.failures(plan=plan), "recipe is not TFMG-first")

    def test_11_sulfuric_acid_construction_input_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:chemical_washer")["inputs"][0] = (
            "tfmg:sulfuric_acid_bucket"
        )
        self.assert_failure(self.failures(plan=plan), "machine construction consumes sulfuric acid")

    def test_12_wrong_industrial_iron_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:chemical_dissolution_chamber")["machine"] = (
            "createcasing:railway_press"
        )
        self.assert_failure(self.failures(plan=plan), "unapproved industrial_iron compacting")

    def test_13_wrong_refined_radiance_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:isotopic_centrifuge")
        contract["steps"][0]["machine"] = "createcasing:industrial_iron_deployer"
        self.assert_failure(self.failures(plan=plan), "unapproved refined_radiance sequence")

    def test_14_generic_5x5_pattern_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:sps_casing")
        contract["pattern"] = ["ABABA", "BABAB", "ABXBA", "BABAB", "ABABA"]
        contract["key"] = {"A": "tfmg:heavy_plate", "B": "mekanism:pellet_polonium"}
        self.assert_failure(self.failures(plan=plan), "generic 5x5 gate-ring")

    def test_15_excessive_sequence_loops_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:sps_port")["loops"] = 3
        self.assert_failure(self.failures(plan=plan), "exactly one loop")

    def test_16_transitional_carrier_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:purification_chamber")["transitional"] = (
            "mekanism:steel_casing"
        )
        self.assert_failure(self.failures(plan=plan), "transitional carrier")

    def test_17_excessive_sequence_steps_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:solar_neutron_activator")
        contract["steps"].insert(
            -1,
            {
                "op": "deploying",
                "ingredient": "tfmg:circuit_board",
                "machine": "createcasing:refined_radiance_deployer",
            },
        )
        self.assert_failure(self.failures(plan=plan), "5-6 moderate operations")

    def test_18_sps_casing_batch_size_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:sps_casing")["output"] = "mekanism:sps_casing"
        self.assert_failure(self.failures(plan=plan), "four-segment factory batch")

    def test_19_waste_barrel_batch_size_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:radioactive_waste_barrel")["output"] = (
            "mekanism:radioactive_waste_barrel"
        )
        self.assert_failure(self.failures(plan=plan), "two-vessel batch")

    def test_20_purification_requires_enrichment_chamber(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:purification_chamber")
        contract["input"] = "mekanism:steel_casing"
        contract["transitional"] = "mekanism:steel_casing"
        self.assert_failure(self.failures(plan=plan), "physical manufacturing role is missing")

    def test_21_injection_requires_purification_chamber(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:chemical_injection_chamber")
        contract["input"] = "mekanism:steel_casing"
        contract["transitional"] = "mekanism:steel_casing"
        self.assert_failure(self.failures(plan=plan), "physical manufacturing role is missing")

    def test_22_slurry_dependency_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:chemical_washer")["depends_on"].remove(
            "industrial_colonies:mekanism_nuclear/chemical_dissolution_chamber"
        )
        self.assert_failure(self.failures(plan=plan), "forward dependency contract is incomplete")

    def test_23_slurry_machines_must_coexist(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:chemical_washer")["inputs"][0] = (
            "mekanism:chemical_dissolution_chamber"
        )
        self.assert_failure(self.failures(plan=plan), "destroys another required slurry-line machine")

    def test_24_isotopic_fissile_bootstrap_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:isotopic_centrifuge")
        contract["steps"][0]["ingredient"] = "mekanism:fissile_fuel"
        self.assert_failure(self.failures(plan=plan), "pre-SPS construction has nuclear bootstrap")

    def test_25_solar_polonium_bootstrap_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:solar_neutron_activator")
        contract["steps"][0]["ingredient"] = "mekanism:pellet_polonium"
        self.assert_failure(self.failures(plan=plan), "pre-SPS construction has nuclear bootstrap")

    def test_26_sps_casing_requires_both_actinides(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:sps_casing")
        contract["inputs"] = [
            "mekanism:hdpe_sheet" if validator.normalized_ref(value) == "mekanism:pellet_plutonium" else value
            for value in contract["inputs"]
        ]
        self.assert_failure(self.failures(plan=plan), "physical manufacturing role is missing")

    def test_27_sps_port_requires_casing(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:sps_port")
        contract["input"] = "mekanism:steel_casing"
        contract["transitional"] = "mekanism:steel_casing"
        self.assert_failure(self.failures(plan=plan), "physical manufacturing role is missing")

    def test_28_supercharged_coil_requires_casing(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:supercharged_coil")
        contract["inputs"] = [
            "mekanism:steel_casing" if value == "mekanism:sps_casing" else value
            for value in contract["inputs"]
        ]
        self.assert_failure(self.failures(plan=plan), "physical manufacturing role is missing")

    def test_29_nucleosynthesizer_requires_antimatter(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "mekanism:antiprotonic_nucleosynthesizer")
        for step in contract["steps"]:
            if step.get("ingredient") == "mekanism:pellet_antimatter":
                step["ingredient"] = "mekanism:alloy_atomic"
        self.assert_failure(self.failures(plan=plan), "physical manufacturing role is missing")

    def test_30_nucleosynthesizer_requires_both_sps_components(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:antiprotonic_nucleosynthesizer")["depends_on"].remove(
            "industrial_colonies:mekanism_nuclear/supercharged_coil"
        )
        self.assert_failure(self.failures(plan=plan), "forward dependency contract is incomplete")

    def test_31_same_batch_cycle_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "mekanism:sps_casing")["depends_on"].append(
            "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer"
        )
        self.assert_failure(self.failures(plan=plan), "same-batch dependency cycle")

    def test_32_mek_data_state_contract_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["dependency_contract"]["mek_data_outputs_are_fresh_empty"].pop()
        self.assert_failure(self.failures(plan=plan), "mek_data fresh-empty")

    def test_33_prerequisite_owner_evidence_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["prerequisite_evidence"][0]["observed_managed_owner"] = "wrong:owner"
        self.assert_failure(self.failures(plan=plan), "prerequisite managed owner drifted")

    def test_34_missing_prerequisite_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if builder.output_id(recipe) != "mekanism:chemical_infuser"
        ]
        self.assert_failure(self.failures(seed=seed), "required predecessor managed owner is absent")

    def test_35_assignment_duplicate_is_rejected(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"]["CR01 \u2014 The Nuclear Age"]["unlocks"].append(
            "mekanism:purification_chamber"
        )
        self.assert_failure(self.failures(assignments=assignments), "current assignment is not exact and unique")

    def test_36_assignment_phase_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["phase_by_node"]["CR01 \u2014 Chemical Separation"] = "High-Energy Grid"
        self.assert_failure(self.failures(seed=seed), "assigned node no longer maps")

    def test_37_authoritative_seed_owner_is_enforced(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if builder.output_id(recipe) != "mekanism:antiprotonic_nucleosynthesizer"
        ]
        self.assert_failure(self.failures(seed=seed), "authoritative seed must own the output")

    def test_38_current_automatic_owner_drift_is_rejected(self) -> None:
        current = copy.deepcopy(self.current)
        recipe = next(
            row
            for row in current["recipes"]
            if builder.output_id(row) == "mekanism:sps_port"
        )
        recipe["id"] = "industrial_colonies:auto/mekanism/not_sps_port"
        self.assert_failure(self.failures(current=current), "current automatic owner identity drifted")

    def test_39_patch_recipe_parity_is_enforced(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["seed_operations"][0]["recipes"][0]["order"] = 999
        self.assert_failure(self.failures(patch=patch), "patch recipe payload differs")

    def test_40_patch_extra_removal_operation_is_rejected(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["seed_operations"].append(
            {"op": "union_additional_removals_exact_ids", "recipe_ids": ["other:shortcut"]}
        )
        self.assert_failure(self.failures(patch=patch), "exact-removal operation count drifted")

    def test_41_forward_route_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["canonical_chemistry_boundary"]["forward_route"][0:2] = list(
            reversed(plan["canonical_chemistry_boundary"]["forward_route"][0:2])
        )
        self.assert_failure(self.failures(plan=plan), "canonical forward uranium")

    def test_42_applied_seed_boundary_is_enforced(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["integration_boundary"]["seed_edit_applied"] = False
        self.assert_failure(self.failures(plan=plan), "lost the applied seed edit")

    def test_43_absent_bypass_candidate_cannot_claim_catalog_evidence(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["chain_bypass_audit"]["candidates"][0]["catalog_present"] = True
        self.assert_failure(self.failures(plan=plan), "claims catalog presence")

    def test_44_antimatter_storage_recovery_must_remain_lossless(self) -> None:
        plan = copy.deepcopy(self.plan)
        recovery = next(
            row
            for row in plan["chain_bypass_audit"]["antimatter_storage_recovery_closure"]
            if row["id"] == "allthecompressed:decompress/antimatter_block"
        )
        recovery["raw_recipe"]["result"]["count"] = 10
        self.assert_failure(self.failures(plan=plan), "storage recovery raw recipe drifted")


if __name__ == "__main__":
    unittest.main()
