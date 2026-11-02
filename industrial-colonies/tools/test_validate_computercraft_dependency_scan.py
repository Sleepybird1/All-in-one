#!/usr/bin/env python3
"""Mutation tests for exact ComputerCraft dependency-scan warning policy."""

from __future__ import annotations

import unittest

from validate_computercraft_reactor_progression import (
    KNOWN_THIRD_PARTY_MALFORMED_RESOURCES,
    classify_dependency_scan_errors,
)


class ComputerCraftDependencyScanTests(unittest.TestCase):
    def known_rows(self):
        return [
            {"jar": jar, "path": path, "error": prefix + " test location"}
            for (jar, path), prefix in KNOWN_THIRD_PARTY_MALFORMED_RESOURCES.items()
        ]

    def test_exact_reviewed_third_party_rows_are_nonfatal(self) -> None:
        failures, warnings, evidence = classify_dependency_scan_errors(self.known_rows())
        self.assertEqual([], failures)
        self.assertEqual(3, len(warnings))
        self.assertEqual(3, len(evidence))

    def test_unknown_third_party_resource_is_fatal(self) -> None:
        failures, _, _ = classify_dependency_scan_errors(
            [{"jar": "other.jar", "path": "data/other/recipe/bad.json", "error": "bad"}]
        )
        self.assertTrue(any("unreviewed" in value for value in failures), failures)

    def test_project_owned_resource_is_always_fatal(self) -> None:
        failures, _, _ = classify_dependency_scan_errors(
            [{"jar": "industrial-colonies-0.4.0.jar", "path": "data/industrial_colonies/recipe/bad.json", "error": "bad"}]
        )
        self.assertTrue(any("project-owned" in value for value in failures), failures)

    def test_known_path_with_new_error_class_requires_review(self) -> None:
        row = self.known_rows()[0]
        row["error"] = "Permission denied"
        failures, _, _ = classify_dependency_scan_errors([row])
        self.assertTrue(any("unreviewed" in value for value in failures), failures)


if __name__ == "__main__":
    unittest.main()
