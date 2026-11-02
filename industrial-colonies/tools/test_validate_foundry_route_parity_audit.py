#!/usr/bin/env python3
"""Mutation tests for the TFMG-gated foundry redesign."""

from __future__ import annotations

import copy
import unittest

import build_foundry_route_parity_audit as builder
import validate_foundry_route_parity_audit as validator


class FoundryRouteParityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = builder.load_json(builder.DEFAULT_PLAN)
        cls.patch = builder.load_json(builder.DEFAULT_PATCH)
        cls.automatic = builder.load_json(builder.AUTOMATIC_AUDIT)
        cls.rows = builder.load_rows(builder.DEFAULT_CATALOG / "recipes.csv")
        cls.item_ids = {
            row["item_id"]
            for row in builder.load_rows(builder.DEFAULT_CATALOG / "items.csv")
        }
        cls.assignments = builder.load_json(
            builder.PROJECT / "progression/machine_node_assignments.json"
        )
        cls.canonicalization = (
            builder.PROJECT
            / "pack-scripts/server_scripts/industrial_steel_canonicalization.js"
        ).read_text(encoding="utf-8")

    def failures(
        self,
        plan=None,
        patch=None,
        automatic=None,
        rows=None,
        item_ids=None,
        assignments=None,
        canonicalization=None,
    ):
        return validator.validate_review(
            copy.deepcopy(plan if plan is not None else self.plan),
            copy.deepcopy(patch if patch is not None else self.patch),
            copy.deepcopy(automatic if automatic is not None else self.automatic),
            copy.deepcopy(rows if rows is not None else self.rows),
            copy.deepcopy(item_ids if item_ids is not None else self.item_ids),
            copy.deepcopy(assignments if assignments is not None else self.assignments),
            canonicalization
            if canonicalization is not None
            else self.canonicalization,
        )

    @staticmethod
    def contract(plan, output):
        return next(
            row
            for row in plan["replacement_contracts"]
            if builder.output_id(row["output"]) == output
        )

    def test_reviewed_artifacts_pass(self) -> None:
        self.assertEqual([], self.failures())

    def test_rejects_subsystem_retirement_decision(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["decision"] = "RETIRE_DUPLICATES"
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_stock_restoration_decision(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["decision"] = "RETAIN_STOCK_FUNCTIONAL_FOUNDRIES"
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_missing_candidate(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["candidate_outputs"].pop()
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_missing_contract(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"].pop()
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_patch_recipe_drift(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["recipes_to_append"][0]["inputs"].pop()
        self.assertTrue(self.failures(patch=patch))

    def test_rejects_missing_stock_removal(self) -> None:
        patch = copy.deepcopy(self.patch)
        patch["exact_stock_removals"].pop()
        self.assertTrue(self.failures(patch=patch))

    def test_rejects_assignment_edit(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["assignment_edits"] = ["forbidden"]
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_wrong_press(self) -> None:
        plan = copy.deepcopy(self.plan)
        self.contract(plan, "createmetallurgy:casting_basin")["machine"] = (
            "create:mechanical_press"
        )
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_wrong_deployer(self) -> None:
        plan = copy.deepcopy(self.plan)
        recipe = self.contract(plan, "createmetallurgy:foundry_mixer")
        recipe["steps"][0]["machine"] = "create:deployer"
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_missing_tfmg_casting_precursor(self) -> None:
        plan = copy.deepcopy(self.plan)
        recipe = self.contract(plan, "createmetallurgy:casting_table")
        recipe["inputs"][0] = "create:basin"
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_mixer_without_tfmg_industrial_mixer(self) -> None:
        plan = copy.deepcopy(self.plan)
        recipe = self.contract(plan, "createmetallurgy:foundry_mixer")
        recipe["input"] = "create:mechanical_mixer"
        recipe["transitional"] = "create:mechanical_mixer"
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_scorched_basin_without_prior_casting_line(self) -> None:
        plan = copy.deepcopy(self.plan)
        recipe = self.contract(plan, "modernfoundry:scorched_basin")
        recipe["inputs"][0] = "create:basin"
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_drain_without_tfmg_pipe(self) -> None:
        plan = copy.deepcopy(self.plan)
        recipe = self.contract(plan, "modernfoundry:scorched_drain")
        recipe["inputs"] = [
            value for value in recipe["inputs"] if "tfmg:steel_pipe" not in value
        ]
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_missing_installed_ingredient(self) -> None:
        plan = copy.deepcopy(self.plan)
        recipe = self.contract(plan, "modernfoundry:scorched_table")
        recipe["inputs"].append("example:not_installed")
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_missing_assignment(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        target = builder.CANDIDATE_OUTPUTS[0]
        for node in assignments.get("nodes", {}).values():
            if isinstance(node, dict):
                node["unlocks"] = [
                    value for value in node.get("unlocks", []) if value != target
                ]
        self.assertTrue(self.failures(assignments=assignments))

    def test_rejects_route_evidence_drift(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["route_evidence"]["tfmg"]["casting_recipe_count"] = 5000
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_new_direct_producer(self) -> None:
        rows = copy.deepcopy(self.rows)
        fake = copy.deepcopy(rows[0])
        fake["recipe_id"] = "example:foundry_bypass"
        fake["outputs"] = builder.CANDIDATE_OUTPUTS[0]
        rows.append(fake)
        self.assertTrue(self.failures(rows=rows))

    def test_rejects_missing_steel_canonicalization(self) -> None:
        text = self.canonicalization.replace(
            "industrial_colonies:steel/create_metallurgy_ingot_casting", "missing"
        )
        self.assertTrue(self.failures(canonicalization=text))

    def test_rejects_same_batch_dependency_cycle(self) -> None:
        plan = copy.deepcopy(self.plan)
        table = self.contract(plan, "createmetallurgy:casting_table")
        basin = self.contract(plan, "createmetallurgy:casting_basin")
        table["depends_on"].append(basin["id"])
        basin["depends_on"].append(table["id"])
        self.assertTrue(self.failures(plan=plan))

    def test_rejects_ingredient_with_only_candidate_dependent_producer(self) -> None:
        plan = copy.deepcopy(self.plan)
        recipe = self.contract(plan, "createmetallurgy:casting_table")
        recipe["inputs"].append("example:cyclic_part")
        item_ids = set(self.item_ids)
        item_ids.add("example:cyclic_part")
        rows = copy.deepcopy(self.rows)
        fake = copy.deepcopy(rows[0])
        fake["recipe_id"] = "example:cyclic_part"
        fake["outputs"] = "example:cyclic_part"
        fake["inputs"] = "createmetallurgy:casting_table"
        rows.append(fake)
        self.assertTrue(self.failures(plan=plan, rows=rows, item_ids=item_ids))

    def test_implementation_rejects_surviving_auto_owner(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "implemented"
        patch = copy.deepcopy(self.patch)
        patch["status"] = "implemented"
        seed = {"recipes": copy.deepcopy(plan["replacement_contracts"]), "preserve_recipe_ids": []}
        manifest = {
            "recipes": [
                *copy.deepcopy(plan["replacement_contracts"]),
                {"id": plan["automatic_managed_ids_to_retire"][0], "remove": []},
            ],
            "additional_removals": [],
        }
        self.assertTrue(validator.validate_implementation(plan, patch, seed, manifest))

    def test_implementation_accepts_clean_replacement(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["status"] = "implemented"
        patch = copy.deepcopy(self.patch)
        patch["status"] = "implemented"
        seed = {"recipes": copy.deepcopy(plan["replacement_contracts"]), "preserve_recipe_ids": []}
        manifest = {
            "recipes": copy.deepcopy(plan["replacement_contracts"]),
            "additional_removals": [],
        }
        self.assertEqual([], validator.validate_implementation(plan, patch, seed, manifest))


if __name__ == "__main__":
    unittest.main()
