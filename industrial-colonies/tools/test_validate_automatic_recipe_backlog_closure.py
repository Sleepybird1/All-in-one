#!/usr/bin/env python3
"""Mutation tests for the immutable 172-owner automatic-backlog proof."""

from __future__ import annotations

import copy
import unittest

import validate_automatic_recipe_backlog_closure as validator


class AutomaticRecipeBacklogClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.PLAN)
        cls.audit = validator.load_json(validator.AUDIT)
        cls.seed = validator.load_json(validator.SEED)
        cls.manifest = validator.load_json(validator.MANIFEST)
        cls.artifacts = validator.load_artifacts(cls.plan)

    def evaluate(self, plan=None, audit=None, seed=None, manifest=None, artifacts=None):
        return validator.evaluate(
            copy.deepcopy(self.plan if plan is None else plan),
            copy.deepcopy(self.audit if audit is None else audit),
            copy.deepcopy(self.seed if seed is None else seed),
            copy.deepcopy(self.manifest if manifest is None else manifest),
            copy.deepcopy(self.artifacts if artifacts is None else artifacts),
        )

    def closed_fixture(self):
        plan = copy.deepcopy(self.plan)
        audit = copy.deepcopy(self.audit)
        artifacts = copy.deepcopy(self.artifacts)
        plan["status"] = "closed_authoritative_manifest"

        recipes = []
        removals: set[str] = set()
        for entry in audit["entries"]:
            if entry["classification"] == "acceptable_stock_derived_utility":
                recipes.append(
                    {
                        "id": entry["managed_id"],
                        "output": {"kind": "ITEM", "id": entry["output"]},
                        "remove": [],
                    }
                )

        source_contracts = []
        for batch in plan["redesign_batches"]:
            artifact = artifacts[batch["artifact"]]
            artifact["status"] = batch["closure_status"]
            for contract in artifact["replacement_contracts"]:
                source_contracts.append(copy.deepcopy(contract))
                removals.update(contract.get("remove", []))

        foundry_artifact = artifacts[plan["foundry_contract"]["artifact"]]
        for contract in foundry_artifact["replacement_contracts"]:
            source_contracts.append(copy.deepcopy(contract))
            removals.update(contract.get("remove", []))

        stock_artifact = artifacts[plan["leave_stock_contract"]["artifact"]]
        seed = {
            "recipes": copy.deepcopy(source_contracts),
            "exclude_outputs": list(stock_artifact["outputs_to_exclude"]),
            "preserve_recipe_ids": list(stock_artifact["recipe_ids_to_preserve"]),
            "machine_families": [],
        }
        manifest = {
            "recipes": [*recipes, *copy.deepcopy(source_contracts)],
            "additional_removals": sorted(removals),
        }
        return plan, audit, seed, manifest, artifacts

    @staticmethod
    def first_entry(audit, classification):
        return next(
            row for row in audit["entries"] if row["classification"] == classification
        )

    @staticmethod
    def recipe(value, identity):
        return next(row for row in value["recipes"] if row["id"] == identity)

    def test_current_project_is_structurally_valid(self) -> None:
        failures, _open, summary = self.evaluate()
        self.assertEqual([], failures)
        self.assertEqual(172, summary["immutable_entries"])

    def test_synthetic_final_authoritative_state_is_closed(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        failures, open_items, summary = self.evaluate(
            plan, audit, seed, manifest, artifacts
        )
        self.assertEqual([], failures)
        self.assertEqual([], open_items)
        self.assertEqual(27, summary["manifest_automatic_ids"])
        self.assertEqual(81, summary["redesign_closed"])
        self.assertEqual(8, summary["foundry_closed"])
        self.assertEqual(56, summary["leave_stock_closed"])

    def test_rejects_unclassified_automatic_owner(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        manifest["recipes"].append(
            {"id": "industrial_colonies:auto/example/unreviewed", "output": "minecraft:stone"}
        )
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("unclassified automatic" in value for value in failures))

    def test_rejects_missing_approved_automatic_owner(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        entry = self.first_entry(audit, "acceptable_stock_derived_utility")
        manifest["recipes"] = [row for row in manifest["recipes"] if row["id"] != entry["managed_id"]]
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("approved automatic owner disappeared" in value for value in failures))

    def test_rejects_approved_automatic_output_drift(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        entry = self.first_entry(audit, "acceptable_stock_derived_utility")
        self.recipe(manifest, entry["managed_id"])["output"] = "minecraft:stone"
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("approved automatic owner output drifted" in value for value in failures))

    def test_rejects_duplicate_manifest_recipe_id(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        manifest["recipes"].append(copy.deepcopy(manifest["recipes"][0]))
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("manifest repeats recipe IDs" in value for value in failures))

    def test_rejects_missing_redesign_contract(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        artifact = artifacts[plan["redesign_batches"][0]["artifact"]]
        artifact["replacement_contracts"].pop()
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("replacement output coverage drifted" in value for value in failures))

    def test_rejects_unsupported_batch_status(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        artifact = artifacts[plan["redesign_batches"][-1]["artifact"]]
        artifact["status"] = "invented_status"
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("unsupported artifact status" in value for value in failures))

    def test_rejects_batch_artifact_mapping_drift(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["redesign_batches"][0]["artifact"] = plan["redesign_batches"][1]["artifact"]
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("batch mapping drifted" in value for value in failures))

    def test_rejects_retained_exception_plan_drift(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["retained_same_output_exception"]["retained_recipe_id"] = "tfmg:not_real"
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("retained same-output exception drifted" in value for value in failures))

    def test_rejects_removing_retained_engine_state_transfer(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        heavy = artifacts["TFMG_HEAVY_ELECTRICAL_REDESIGN_AUDIT.plan.json"]
        contract = next(
            row for row in heavy["replacement_contracts"]
            if validator.resource_id(row["output"]) == "tfmg:engine_cylinder"
        )
        contract["remove"].append("tfmg:engine_cylinder_gas")
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("retained same-output recipe is also removed" in value for value in failures))

    def test_rejects_a_second_retained_source_exception(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        heavy = artifacts["TFMG_HEAVY_ELECTRICAL_REDESIGN_AUDIT.plan.json"]
        contract = next(
            row for row in heavy["replacement_contracts"]
            if validator.resource_id(row["output"]) == "tfmg:centrifuge"
        )
        contract["retained_same_output_recipe"] = contract["remove"][0]
        contract["remove"] = contract["remove"][1:]
        contract["exclusive_output"] = False
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("one exact retained source" in value for value in failures))

    def test_reintroduced_redesign_automatic_owner_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "needs_source_owned_redesign")
        manifest["recipes"].append(
            {"id": entry["managed_id"], "output": {"kind": "ITEM", "id": entry["output"]}}
        )
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_missing_redesign_source_owner_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "needs_source_owned_redesign")
        owner = next(
            contract["id"]
            for artifact in artifacts.values()
            for contract in artifact.get("replacement_contracts", [])
            if validator.resource_id(contract.get("output")) == entry["output"]
        )
        manifest["recipes"] = [row for row in manifest["recipes"] if row["id"] != owner]
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_missing_redesign_stock_removal_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "needs_source_owned_redesign")
        removed = entry["exact_removals"][0]
        manifest["additional_removals"].remove(removed)
        owner = next(
            contract["id"]
            for artifact in artifacts.values()
            for contract in artifact.get("replacement_contracts", [])
            if validator.resource_id(contract.get("output")) == entry["output"]
        )
        self.recipe(manifest, owner)["remove"].remove(removed)
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_removed_redesign_source_owned_recipe_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "needs_source_owned_redesign")
        owner = next(
            contract["id"]
            for artifact in artifacts.values()
            for contract in artifact.get("replacement_contracts", [])
            if validator.resource_id(contract.get("output")) == entry["output"]
        )
        manifest["additional_removals"].append(owner)
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_reintroduced_foundry_automatic_owner_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "redundant_should_retire")
        manifest["recipes"].append(
            {"id": entry["managed_id"], "output": {"kind": "ITEM", "id": entry["output"]}}
        )
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_missing_foundry_stock_removal_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "redundant_should_retire")
        removed = entry["exact_removals"][0]
        manifest["additional_removals"].remove(removed)
        foundry = artifacts["FOUNDRY_ROUTE_PARITY_AUDIT.plan.json"]
        owner = next(
            contract["id"]
            for contract in foundry["replacement_contracts"]
            if validator.resource_id(contract.get("output")) == entry["output"]
        )
        self.recipe(manifest, owner)["remove"].remove(removed)
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_removed_foundry_source_owned_recipe_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "redundant_should_retire")
        foundry = artifacts["FOUNDRY_ROUTE_PARITY_AUDIT.plan.json"]
        owner = next(
            contract["id"]
            for contract in foundry["replacement_contracts"]
            if validator.resource_id(contract.get("output")) == entry["output"]
        )
        manifest["additional_removals"].append(owner)
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_missing_leave_stock_exclusion_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "runtime_artifact_leave_stock")
        seed["exclude_outputs"].remove(entry["output"])
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_missing_leave_stock_preserve_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "runtime_artifact_leave_stock")
        seed["preserve_recipe_ids"].remove(entry["exact_removals"][0])
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_removed_leave_stock_source_is_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        entry = self.first_entry(audit, "runtime_artifact_leave_stock")
        manifest["additional_removals"].append(entry["exact_removals"][0])
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertTrue(any(entry["output"] in value for value in open_items))

    def test_rejects_leave_stock_source_owned_managed_owner(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        entry = self.first_entry(audit, "runtime_artifact_leave_stock")
        owner = {
            "id": "industrial_colonies:test/forbidden_stock_owner",
            "output": {"kind": "ITEM", "id": entry["output"]},
        }
        seed["recipes"].append(copy.deepcopy(owner))
        manifest["recipes"].append(copy.deepcopy(owner))
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("leave-stock output has" in value for value in failures))

    def test_rejects_closed_status_when_real_items_are_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        entry = self.first_entry(audit, "needs_source_owned_redesign")
        owner = next(
            contract["id"]
            for artifact in artifacts.values()
            for contract in artifact.get("replacement_contracts", [])
            if validator.resource_id(contract.get("output")) == entry["output"]
        )
        manifest["recipes"] = [row for row in manifest["recipes"] if row["id"] != owner]
        failures, _open, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertTrue(any("claims closed" in value for value in failures))

    def test_unpromoted_plan_status_keeps_completed_proof_open(self) -> None:
        plan, audit, seed, manifest, artifacts = self.closed_fixture()
        plan["status"] = "proof_ready_pending_final_authoritative_manifest"
        failures, open_items, _summary = self.evaluate(plan, audit, seed, manifest, artifacts)
        self.assertEqual([], failures)
        self.assertEqual(["closure plan status has not been promoted to closed"], open_items)

    def test_rejects_immutable_classification_drift_without_crashing(self) -> None:
        audit = copy.deepcopy(self.audit)
        audit["entries"][0]["classification"] = "needs_source_owned_redesign"
        failures, _open, _summary = self.evaluate(audit=audit)
        self.assertTrue(any("classification counts drifted" in value for value in failures))


if __name__ == "__main__":
    unittest.main()
