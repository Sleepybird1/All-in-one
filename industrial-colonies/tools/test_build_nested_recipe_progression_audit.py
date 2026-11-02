#!/usr/bin/env python3
"""Focused invariants for the nested-recipe progression audit."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_nested_recipe_progression_audit as audit


class NestedRecipeProgressionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = audit.build_report(audit.DEFAULT_CATALOG, audit.DEFAULT_CROSS_PACK, audit.DEFAULT_DEFERRAL)

    def test_current_report_is_green(self) -> None:
        self.assertEqual(self.report["status"], "green")
        self.assertEqual(self.report["scope"]["nested_recipe_count"], 125)
        self.assertEqual(self.report["scope"]["other_nested_recipe_count"], 124)

    def test_physics_assembler_is_the_single_critical_boundary(self) -> None:
        critical = [row for row in self.report["recipes"] if row["disposition"] == "critical_space_boundary"]
        self.assertEqual([row["recipe_id"] for row in critical], [audit.PHYSICS_ASSEMBLER])
        self.assertTrue(self.report["boundary_result"]["critical_recipe_exactly_deferred"])
        self.assertTrue(self.report["boundary_result"]["critical_installed_row_matches"])

    def test_cross_pack_protected_outputs_remain_closed(self) -> None:
        self.assertEqual(self.report["boundary_result"]["cross_pack_unmanaged_protected_output_producers"], 0)

    def test_every_nested_row_has_a_disposition_and_source_chain(self) -> None:
        for row in self.report["recipes"]:
            self.assertTrue(row["disposition"])
            self.assertIn("!/", row["source_jar"])

    def test_drifted_artifact_would_not_equal_current_report(self) -> None:
        mutated = copy.deepcopy(self.report)
        mutated["scope"]["nested_recipe_count"] -= 1
        self.assertNotEqual(mutated, self.report)


if __name__ == "__main__":
    unittest.main()
