#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import recipe_design_v4_digital_machine_corrections as redesigns


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "progression" / "managed_recipe_overhaul.seed.json"


class DigitalMachineCorrectionTests(unittest.TestCase):
    def test_current_seed_redesigns_exact_cohort_and_is_idempotent(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        before = {
            recipe["id"]: copy.deepcopy(recipe)
            for recipe in data["recipes"]
            if recipe["id"] in redesigns.REDESIGNED_IDS
        }
        self.assertEqual(redesigns.REDESIGNED_IDS, frozenset(before))

        redesigns.apply(data)
        report = redesigns.audit(data)
        self.assertEqual("PASS", report["status"])
        self.assertEqual(10, report["redesigned"])

        # The durable seed may be either immediately before this module in the
        # pipeline or already regenerated with it.  The semantic audit above is
        # the acceptance contract in both states; do not make the test depend on
        # whether a previous local pipeline run has already persisted the same
        # idempotent design.
        stable = copy.deepcopy(data)
        redesigns.apply(data)
        self.assertEqual(stable, data)

    def test_rejection_contracts_are_complete_and_immutable(self) -> None:
        self.assertEqual(10, len(redesigns.REJECTION_CONTRACTS))
        self.assertEqual(
            redesigns.REDESIGNED_IDS,
            frozenset(redesigns.REJECTION_CONTRACTS),
        )
        for contract in redesigns.REJECTION_CONTRACTS.values():
            self.assertTrue(contract["note"])
            digest = contract["cardSha256"]
            self.assertTrue(digest.startswith("sha256:"))
            self.assertEqual(71, len(digest))

    def test_missing_recipe_fails_closed(self) -> None:
        data = json.loads(SEED.read_text(encoding="utf-8"))
        data["recipes"] = [
            recipe
            for recipe in data["recipes"]
            if recipe["id"] != "industrial_colonies:v3_ae2/spatial_io_port"
        ]
        with self.assertRaises(KeyError):
            redesigns.apply(data)


if __name__ == "__main__":
    unittest.main()
