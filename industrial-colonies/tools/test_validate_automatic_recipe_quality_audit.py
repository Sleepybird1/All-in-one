#!/usr/bin/env python3
"""Mutation tests for validate_automatic_recipe_quality_audit.py."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_automatic_recipe_quality_audit as validator


class AutomaticRecipeQualityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.DEFAULT_PLAN)
        cls.managed = validator.load_json(validator.DEFAULT_MANAGED)
        cls.report = validator.load_json(validator.DEFAULT_REPORT)
        cls.markdown = validator.DEFAULT_MARKDOWN.read_text(encoding="utf-8")

    def failures(
        self,
        plan=None,
        managed=None,
        report=None,
        managed_hash=validator.EXPECTED_MANAGED_SHA256,
        report_hash=validator.EXPECTED_REPORT_SHA256,
        markdown=None,
    ) -> list[str]:
        return validator.validate_plan(
            self.plan if plan is None else plan,
            self.managed if managed is None else managed,
            self.report if report is None else report,
            managed_hash,
            report_hash,
            self.markdown if markdown is None else markdown,
        )

    def test_current_audit_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_managed_snapshot_hash_drift_is_rejected(self) -> None:
        failures = self.failures(managed_hash="0" * 64)
        self.assertTrue(any("managed snapshot SHA-256 changed" in row for row in failures))

    def test_report_snapshot_hash_drift_is_rejected(self) -> None:
        failures = self.failures(report_hash="0" * 64)
        self.assertTrue(any("report snapshot SHA-256 changed" in row for row in failures))

    def test_missing_entry_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["entries"].pop()
        failures = self.failures(plan=plan)
        self.assertTrue(any("plan entry coverage differs" in row for row in failures))

    def test_duplicate_entry_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["entries"].append(copy.deepcopy(plan["entries"][0]))
        failures = self.failures(plan=plan)
        self.assertTrue(any("duplicate plan entry" in row for row in failures))

    def test_classification_swap_is_rejected_even_if_totals_are_preserved(self) -> None:
        plan = copy.deepcopy(self.plan)
        acceptable = next(
            row for row in plan["entries"]
            if row["classification"] == "acceptable_stock_derived_utility"
        )
        leave_stock = next(
            row for row in plan["entries"]
            if row["classification"] == "runtime_artifact_leave_stock"
        )
        acceptable["classification"], leave_stock["classification"] = (
            leave_stock["classification"], acceptable["classification"]
        )
        acceptable["disposition"], leave_stock["disposition"] = (
            leave_stock["disposition"], acceptable["disposition"]
        )
        failures = self.failures(plan=plan)
        self.assertTrue(any("exact ID-by-ID classification decisions changed" in row for row in failures))

    def test_gate_ring_cannot_be_accepted(self) -> None:
        plan = copy.deepcopy(self.plan)
        ring = next(
            row for row in plan["entries"]
            if row["generic_gate_ring"]
            and row["classification"] == "needs_source_owned_redesign"
        )
        ring["classification"] = "acceptable_stock_derived_utility"
        ring["disposition"] = "keep_automatic_exact_stock"
        failures = self.failures(plan=plan)
        self.assertTrue(any("generic gate rings cannot be accepted" in row for row in failures))

    def test_source_recipe_mapping_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["entries"][0]["source_recipe_id"] = "minecraft:imaginary"
        failures = self.failures(plan=plan)
        self.assertTrue(any("source_recipe_id does not match" in row for row in failures))

    def test_disposition_must_match_classification(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["entries"][0]["disposition"] = "replace_with_source_owned_contract"
        failures = self.failures(plan=plan)
        self.assertTrue(any("disposition does not match classification" in row for row in failures))

    def test_gate_ring_evidence_drift_is_rejected(self) -> None:
        managed = copy.deepcopy(self.managed)
        recipe = next(
            row for row in managed["recipes"]
            if row.get("id") == "industrial_colonies:auto/ae2/terminal"
        )
        recipe["pattern"][0] = "AAAAA"
        failures = self.failures(managed=managed)
        self.assertTrue(any("generic_gate_ring does not match" in row for row in failures))
        self.assertTrue(any("gate-ring count must remain 145" in row for row in failures))

    def test_report_source_type_drift_is_rejected(self) -> None:
        report = copy.deepcopy(self.report)
        row = next(
            value for value in report["generated"]
            if value.get("managed_recipe") == "industrial_colonies:auto/mekanism/chemical_infuser"
        )
        row["source_type"] = "minecraft:crafting_shaped"
        failures = self.failures(report=report)
        self.assertTrue(any("source_type does not match" in value for value in failures))
        self.assertTrue(any("source-type evidence drifted" in value for value in failures))

    def test_missing_batch_output_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        batch = plan["implementation_batches"][0]
        batch["outputs"].pop()
        batch["managed_ids"].pop()
        batch["installed_recipe_ids"].pop()
        failures = self.failures(plan=plan)
        self.assertTrue(any("batch signature changed" in row for row in failures))
        self.assertTrue(any("must cover every redesign exactly once" in row for row in failures))

    def test_duplicate_batch_owner_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        first = plan["implementation_batches"][0]
        second = plan["implementation_batches"][1]
        second["outputs"][0] = first["outputs"][0]
        second["managed_ids"][0] = first["managed_ids"][0]
        second["installed_recipe_ids"][0] = first["installed_recipe_ids"][0]
        failures = self.failures(plan=plan)
        self.assertTrue(any("more than one implementation batch" in row for row in failures))

    def test_batch_source_id_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["implementation_batches"][0]["installed_recipe_ids"][0] = "tfmg:wrong"
        failures = self.failures(plan=plan)
        self.assertTrue(any("output/source mapping drifted" in row for row in failures))

    def test_cycle_risk_documentation_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["implementation_batches"][2]["cycle_risks"] = []
        failures = self.failures(plan=plan)
        self.assertTrue(any("at least three cycle risks" in row for row in failures))

    def test_phase_count_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["phase_counts"]["Digital Logistics"]["needs_source_owned_redesign"] += 1
        failures = self.failures(plan=plan)
        self.assertTrue(any("phase_counts do not match" in row for row in failures))

    def test_non_foundry_retirement_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        target = next(
            row for row in plan["entries"]
            if row["classification"] == "redundant_should_retire"
        )
        target["output"] = "tfmg:centrifuge"
        failures = self.failures(plan=plan)
        self.assertTrue(any("only the eight audited duplicate foundry" in row for row in failures))

    def test_markdown_summary_is_validated(self) -> None:
        markdown = self.markdown.replace("145 of 146", "145/146")
        failures = self.failures(markdown=markdown)
        self.assertTrue(any("missing required summary fragment" in row for row in failures))


if __name__ == "__main__":
    unittest.main()
