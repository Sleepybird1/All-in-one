#!/usr/bin/env python3
"""Mutation tests for the implemented Universal Cable tail package."""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_mekanism_universal_cable_tail_audit as audit
import build_mekanism_universal_cable_tail_patch_plan as patch_builder


class UniversalCableTailMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = audit.load_json(audit.DEFAULT_PLAN)
        cls.static_patch = audit.load_json(audit.DEFAULT_PATCH)
        cls.automatic_plan = audit.load_json(audit.DEFAULT_AUTOMATIC_PLAN)
        cls.automatic_snapshot = audit.load_json(audit.DEFAULT_AUTOMATIC_SNAPSHOT)
        cls.seed = audit.load_json(audit.DEFAULT_SEED)
        cls.assignments = audit.load_json(audit.DEFAULT_ASSIGNMENTS)
        cls.environments = audit.load_json(audit.DEFAULT_ENVIRONMENTS)
        cls.physical_tiers = audit.load_json(audit.DEFAULT_PHYSICAL_TIERS)
        cls.induction_plan = audit.load_json(audit.DEFAULT_INDUCTION_PLAN)
        cls.transmitter_plan = audit.load_json(audit.DEFAULT_TRANSMITTER_PLAN)
        cls.factory_plan = audit.load_json(audit.DEFAULT_FACTORY_PLAN)
        cls.blacklist = audit.load_json(audit.DEFAULT_BLACKLIST)

    def validate(
        self,
        *,
        plan=None,
        static_patch=None,
        automatic_plan=None,
        automatic_snapshot=None,
        seed=None,
        assignments=None,
        environments=None,
        physical_tiers=None,
        induction_plan=None,
        induction_validator=None,
        transmitter_plan=None,
        transmitter_md=None,
        factory_plan=None,
        blacklist=None,
    ) -> list[str]:
        return audit.validate_plan(
            copy.deepcopy(self.plan if plan is None else plan),
            copy.deepcopy(
                self.static_patch if static_patch is None else static_patch
            ),
            copy.deepcopy(
                self.automatic_plan if automatic_plan is None else automatic_plan
            ),
            copy.deepcopy(
                self.automatic_snapshot
                if automatic_snapshot is None
                else automatic_snapshot
            ),
            audit.DEFAULT_CATALOG,
            audit.DEFAULT_MODS,
            copy.deepcopy(self.seed if seed is None else seed),
            copy.deepcopy(self.assignments if assignments is None else assignments),
            copy.deepcopy(self.environments if environments is None else environments),
            copy.deepcopy(
                self.physical_tiers if physical_tiers is None else physical_tiers
            ),
            copy.deepcopy(
                self.induction_plan if induction_plan is None else induction_plan
            ),
            audit.DEFAULT_INDUCTION_VALIDATOR
            if induction_validator is None
            else induction_validator,
            copy.deepcopy(
                self.transmitter_plan if transmitter_plan is None else transmitter_plan
            ),
            audit.DEFAULT_TRANSMITTER_MD if transmitter_md is None else transmitter_md,
            copy.deepcopy(self.factory_plan if factory_plan is None else factory_plan),
            copy.deepcopy(self.blacklist if blacklist is None else blacklist),
            compile_batch=False,
        )

    def rejected(self, **kwargs) -> None:
        try:
            failures = self.validate(**kwargs)
        except (KeyError, IndexError, TypeError, ValueError):
            return
        self.assertTrue(failures, "mutation was not rejected")

    def test_01_schema_version_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["schema_version"] = 2
        self.rejected(plan=plan)

    def test_02_status_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "review_ready_no_shared_mutation"
        self.rejected(plan=plan)

    def test_03_decision_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["decision"] = "KEEP_AUTOMATIC"
        self.rejected(plan=plan)

    def test_04_scope_count_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["output_count_each"] = 1
        self.rejected(plan=plan)

    def test_05_validation_summary_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["validation_result"]["contracts_compiled"] = 2
        self.rejected(plan=plan)

    def test_06_catalog_hash_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installed_evidence"]["recipe_catalog"]["sha256"] = "0" * 64
        self.rejected(plan=plan)

    def test_07_artifact_hash_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installed_evidence"]["artifacts"][0]["sha256"] = "0" * 64
        self.rejected(plan=plan)

    def test_08_source_recipe_hash_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installed_evidence"]["source_recipe_contracts"][1][
            "source_sha256"
        ] = "0" * 64
        self.rejected(plan=plan)

    def test_09_source_input_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        source = plan["installed_evidence"]["source_recipe_contracts"][0]
        source["exact_inputs"]["mekanism:basic_universal_cable"] = 7
        self.rejected(plan=plan)

    def test_10_static_producer_inventory_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installed_evidence"]["static_producer_inventory"][2][
            "recipe_ids"
        ] = []
        self.rejected(plan=plan)

    def test_11_installed_consumer_inventory_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installed_evidence"]["installed_consumer_inventory"][0][
            "recipe_ids"
        ] = []
        self.rejected(plan=plan)

    def test_12_managed_consumer_inventory_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installed_evidence"]["managed_seed_consumer_inventory"][2][
            "count"
        ] = 3
        self.rejected(plan=plan)

    def test_13_unavailable_id_resolution_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installed_evidence"]["unavailable_conceptual_ids"].pop()
        self.rejected(plan=plan)

    def test_14_automatic_batch_identity_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["automatic_owner_evidence"]["batch_id"] = "wrong_batch"
        self.rejected(plan=plan)

    def test_15_source_owned_recipe_id_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][0]["id"] += "_wrong"
        self.rejected(plan=plan)

    def test_16_machine_binding_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][0]["machine"] = "create:mechanical_press"
        self.rejected(plan=plan)

    def test_17_output_count_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][1]["output"] = (
            "7x mekanism:elite_universal_cable"
        )
        self.rejected(plan=plan)

    def test_18_manufacturing_bill_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][2]["inputs"].remove(
            "4x tfmg:aluminum_wire"
        )
        self.rejected(plan=plan)

    def test_19_exact_removal_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][0]["remove"] = [
            "mekanism:transmitter/universal_cable/elite"
        ]
        self.rejected(plan=plan)

    def test_20_ladder_dependency_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][1]["depends_on"][0] = audit.AUTO_ADVANCED
        self.rejected(plan=plan)

    def test_21_assignment_placement_mutation(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"]["CR01 — Precision Engineering"]["unlocks"].remove(
            audit.ELITE_OUTPUT
        )
        self.rejected(assignments=assignments)

    def test_22_dependency_id_map_mutation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["dependency_rewrite_contract"]["id_map"][audit.AUTO_ULTIMATE] = (
            audit.AUTO_ULTIMATE
        )
        self.rejected(plan=plan)

    def test_23_seed_dependency_occurrence_mutation(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipes = {value["id"]: value for value in seed["recipes"]}
        dependencies = recipes[
            "industrial_colonies:mekanism/induction/port"
        ]["depends_on"]
        dependencies[dependencies.index(audit.ULTIMATE_ID)] = audit.AUTO_ULTIMATE
        self.rejected(seed=seed)

    def test_24_induction_validator_reference_mutation(self) -> None:
        source = audit.DEFAULT_INDUCTION_VALIDATOR.read_text(encoding="utf-8-sig")
        changed = source.replace(audit.ULTIMATE_ID, audit.AUTO_ULTIMATE)
        with tempfile.TemporaryDirectory(prefix="universal-cable-mutation-") as root:
            path = Path(root) / "validate_induction_matrix_completion_audit.py"
            path.write_text(changed, encoding="utf-8")
            self.rejected(induction_validator=path)

    def test_25_missing_implemented_owner_fails_closed(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe for recipe in seed["recipes"] if recipe.get("id") != audit.ADVANCED_ID
        ]
        self.rejected(seed=seed)

    def test_26_implemented_recipe_drift_fails_closed(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = next(value for value in seed["recipes"] if value.get("id") == audit.ELITE_ID)
        recipe["inputs"][1] = "3x mekanism:alloy_reinforced"
        self.rejected(seed=seed)

    def test_27_induction_plan_retired_id_fails_closed(self) -> None:
        induction_plan = copy.deepcopy(self.induction_plan)
        induction_plan["external_prerequisites"][3]["recipe_id"] = audit.AUTO_ULTIMATE
        self.rejected(induction_plan=induction_plan)

    def test_28_patch_builder_tracks_tfmg_results_and_rejects_alias_conflicts(self) -> None:
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
