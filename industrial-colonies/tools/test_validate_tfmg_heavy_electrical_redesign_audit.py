#!/usr/bin/env python3
"""Mutation tests for the TFMG heavy/electrical redesign audit."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_tfmg_heavy_electrical_patch_plan as patch_builder
import validate_tfmg_heavy_electrical_redesign_audit as validator


class TFMGHeavyElectricalRedesignAuditTests(unittest.TestCase):
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
                validator.DEFAULT_AUTOMATIC_SNAPSHOT,
                validator.DEFAULT_CATALOG,
                validator.DEFAULT_MODS,
                self.seed if seed is None else seed,
                self.assignments if assignments is None else assignments,
                validator.DEFAULT_PHYSICAL_TIERS,
                compile_batch=compile_batch,
            )
        except (ValueError, KeyError) as error:
            return [str(error)]

    def contract(self, plan: dict, suffix: str) -> dict:
        return next(value for value in plan["replacement_contracts"] if value["id"].endswith(suffix))

    def source(self, plan: dict, identity: str) -> dict:
        return next(value for value in plan["source_recipes"] if value["id"] == identity)

    def test_01_full_review_contract_compiles(self) -> None:
        self.assertEqual([], self.failures(compile_batch=True))

    def test_02_installed_source_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["source_recipes"][0]["sha256"] = "0" * 64
        self.assertTrue(any("installed source JSON hash changed" in row for row in self.failures(plan=plan)))

    def test_03_catalog_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["recipe_catalog_sha256"] = "0" * 64
        self.assertTrue(any("recipe catalog hash changed" in row for row in self.failures(plan=plan)))

    def test_04_priority_batch_order_drift_is_rejected(self) -> None:
        automatic = copy.deepcopy(self.automatic_plan)
        batch = next(value for value in automatic["implementation_batches"] if value["priority"] == 1)
        batch["outputs"][0], batch["outputs"][1] = batch["outputs"][1], batch["outputs"][0]
        self.assertTrue(any("output order changed" in row for row in self.failures(automatic_plan=automatic)))

    def test_05_automatic_owner_inventory_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_automatic_owners"][0]["managed_id"] = "industrial_colonies:auto/tfmg/not_real"
        self.assertTrue(any("exactly eight ids" in row for row in self.failures(plan=plan)))

    def test_06_generic_centrifuge_gate_ring_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/centrifuge")["pattern"] = [
            "ABABA", "BFCFB", "AFSFA", "BFCFB", "ABABA"
        ]
        self.assertTrue(any("radial 5x5" in row for row in self.failures(plan=plan)))

    def test_07_downstream_industrial_iron_press_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/diesel_engine_cylinder")["machine"] = "createcasing:industrial_iron_press"
        failures = self.failures(plan=plan)
        self.assertTrue(any("downstream of the batch" in row for row in failures))
        self.assertTrue(any("machine-role mapping changed" in row for row in failures))

    def test_08_createaddition_spool_substitution_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        contract = self.contract(plan, "/portable_energy_interface")
        contract["inputs"][2] = "createaddition:copper_spool"
        failures = self.failures(plan=plan)
        self.assertTrue(any("missing required TFMG-first inputs" in row for row in failures))
        self.assertTrue(any("forbidden substitute" in row for row in failures))

    def test_09_digital_adapter_without_tfmg_board_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/digital_adapter")["inputs"][1] = "ae2:logic_processor"
        failures = self.failures(plan=plan)
        self.assertTrue(any("missing required TFMG-first inputs" in row for row in failures))
        self.assertTrue(any("downstream technology family" in row for row in failures))

    def test_10_transformer_requires_two_tfmg_spools(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/transformer")["inputs"][-1] = "tfmg:copper_wire"
        self.assertTrue(any("primary and secondary spools" in row for row in self.failures(plan=plan)))

    def test_11_voltage_observer_requires_populated_tfmg_board(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/voltage_observer")["inputs"].remove("tfmg:circuit_board")
        self.assertTrue(any("missing required TFMG-first inputs" in row for row in self.failures(plan=plan)))

    def test_12_diesel_item_components_are_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/diesel_engine_cylinder")["output"]["components"] = "[minecraft:custom_data={}]"
        self.assertTrue(any("diesel cylinder lost" in row for row in self.failures(plan=plan)))

    def test_13_spark_item_components_are_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/engine_cylinder")["output"]["components"] = validator.EXPECTED_DIESEL_COMPONENTS
        self.assertTrue(any("spark-ignition cylinder lost" in row for row in self.failures(plan=plan)))

    def test_14_lpg_variant_cannot_be_removed(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/engine_cylinder")["remove"].append("tfmg:engine_cylinder_gas")
        self.assertTrue(any("LPG cylinder parity recipe" in row for row in self.failures(plan=plan)))

    def test_15_spark_owner_must_be_nonexclusive(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/engine_cylinder")["exclusive_output"] = True
        self.assertTrue(any("must be nonexclusive" in row for row in self.failures(plan=plan)))

    def test_16_counted_tag_syntax_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/diesel_engine_cylinder")["inputs"][-1] = "2x #c:nuggets/steel"
        self.assertTrue(any("counted tag syntax is forbidden" in row for row in self.failures(plan=plan)))

    def test_17_engine_cycle_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/diesel_engine_cylinder")["inputs"][0] = "tfmg:engine_cylinder"
        failures = self.failures(plan=plan)
        self.assertTrue(any("recipe consumes its own output" in row for row in failures) or any("same-batch dependency mismatch" in row for row in failures))

    def test_18_assignment_anchor_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["assignment_patch"]["insert_after"] = "tfmg:large_engine"
        self.assertTrue(any("assignment patch contract changed" in row for row in self.failures(plan=plan)))

    def test_19_reintroduced_engine_source_override_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["source_recipe_overrides"]["tfmg:engine_cylinder"] = "tfmg:engine_cylinder_spark_plug"
        self.assertTrue(any("restored the removed engine-cylinder source override" in row for row in self.failures(seed=seed)))

    def test_20_assignment_source_drift_is_rejected(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"]["CR01 — Diesel Engines"]["unlocks"].remove("tfmg:engine_cylinder")
        assignments["nodes"]["CR01 — Early Combusion Engines"]["unlocks"].insert(0, "tfmg:engine_cylinder")
        self.assertTrue(any("assignment move" in row or "old node" in row for row in self.failures(assignments=assignments)))

    def test_21_lpg_source_disposition_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.source(plan, "tfmg:engine_cylinder_gas")["disposition"] = "replace"
        self.assertTrue(any("downstream variant" in row for row in self.failures(plan=plan)))

    def test_22_patch_builder_is_deterministic_and_nonmutating(self) -> None:
        seed_before = copy.deepcopy(self.seed)
        assignments_before = copy.deepcopy(self.assignments)
        first = patch_builder.build_patch_plan(self.plan, self.seed, self.assignments)
        second = patch_builder.build_patch_plan(self.plan, self.seed, self.assignments)
        self.assertEqual(first, second)
        self.assertEqual("implemented_source_owned_noop", first["mode"])
        self.assertEqual(seed_before, self.seed)
        self.assertEqual(assignments_before, self.assignments)

    def test_23_engine_cylinder_cannot_move_before_aluminum_processing(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/engine_cylinder")["node"] = "CR01 — Early Combusion Engines"
        self.assertTrue(any("reviewed node placement changed" in row for row in self.failures(plan=plan)))

    def test_24_exact_source_removal_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/transformer")["remove"] = ["tfmg:crafting/materials/not_transformer"]
        self.assertTrue(any("exact source removal set drifted" in row for row in self.failures(plan=plan)))

    def test_25_digital_adapter_cannot_move_before_wired_modem(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "/digital_adapter")["phase"] = "Electrical Manufacturing"
        self.assertTrue(any("reviewed phase placement changed" in row for row in self.failures(plan=plan)))

    def test_26_missing_implemented_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe for recipe in seed["recipes"]
            if recipe.get("id") != "industrial_colonies:tfmg_heavy_electrical/centrifuge"
        ]
        self.assertTrue(any("implemented recipe is absent" in row for row in self.failures(seed=seed)))

    def test_27_implemented_recipe_drift_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = next(
            value for value in seed["recipes"]
            if value.get("id") == "industrial_colonies:tfmg_heavy_electrical/transformer"
        )
        recipe["machine"] = "createcasing:brass_press"
        self.assertTrue(any("implemented recipe differs" in row for row in self.failures(seed=seed)))

    def test_28_duplicate_implemented_output_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        duplicate = copy.deepcopy(next(
            value for value in seed["recipes"]
            if value.get("id") == "industrial_colonies:tfmg_heavy_electrical/electrode_holder"
        ))
        duplicate["id"] = "industrial_colonies:test/duplicate_electrode_holder"
        seed["recipes"].append(duplicate)
        self.assertTrue(any("implemented output owner set changed" in row for row in self.failures(seed=seed)))

    def test_29_status_cannot_return_to_review_only(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "review_ready_no_shared_mutation"
        self.assertTrue(any("status must be implemented_in_seed" in row for row in self.failures(plan=plan)))

    def test_30_implementation_metadata_is_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["seed_implementation"]["automatic_owners_retired"] = 7
        self.assertTrue(any("seed_implementation metadata" in row for row in self.failures(plan=plan)))

    def test_31_physical_authority_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["physical_tiers_sha256"] = "0" * 64
        self.assertTrue(any(
            "physical tier authority hash changed" in row
            for row in self.failures(plan=plan)
        ))

    def test_32_physical_authority_path_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["physical_tiers"] = "progression/not_the_authority.json"
        self.assertTrue(any(
            "physical tier authority path metadata changed" in row
            for row in self.failures(plan=plan)
        ))

    def test_33_patch_builder_enforces_and_reports_physical_authority(self) -> None:
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

    def test_34_patch_builder_tracks_tfmg_results_and_rejects_alias_conflicts(self) -> None:
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
