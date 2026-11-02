#!/usr/bin/env python3
"""Focused mutation tests for managed/script ownership conflict policy."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import validate_managed_script_conflicts as validator


ROOT = Path(__file__).resolve().parents[1]


class CompiledOutputSlotTests(unittest.TestCase):
    def test_standard_output_slot_is_discovered(self) -> None:
        errors: list[str] = []
        owners = validator.compiled_outputs(
            [
                {
                    "recipeId": "industrial_colonies:test/standard",
                    "slots": {
                        "output": {"kind": "ITEM", "id": "minecraft:iron_ingot"}
                    },
                }
            ],
            errors,
        )
        self.assertEqual([], errors)
        self.assertEqual(
            ["industrial_colonies:test/standard"], owners["minecraft:iron_ingot"]
        )

    def test_tfmg_vat_results_slot_is_discovered(self) -> None:
        errors: list[str] = []
        owners = validator.compiled_outputs(
            [
                {
                    "recipeId": "industrial_colonies:test/chemical_vat",
                    "slots": {
                        "results0": {
                            "kind": "ITEM",
                            "id": "industrial_colonies:test_concentrate",
                        }
                    },
                }
            ],
            errors,
        )
        self.assertEqual([], errors)
        self.assertEqual(
            ["industrial_colonies:test/chemical_vat"],
            owners["industrial_colonies:test_concentrate"],
        )

    def test_recipe_without_item_output_fails_closed(self) -> None:
        errors: list[str] = []
        owners = validator.compiled_outputs(
            [
                {
                    "recipeId": "industrial_colonies:test/no_item_output",
                    "slots": {
                        "results0": {
                            "kind": "FLUID",
                            "id": "minecraft:water",
                        }
                    },
                }
            ],
            errors,
        )
        self.assertEqual({}, dict(owners))
        self.assertEqual(
            [
                "compiled recipe industrial_colonies:test/no_item_output has no item output slot"
            ],
            errors,
        )


class TierInstallerRestorationConflictTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.restoration = json.loads(
            (ROOT / "STOCK_UTILITY_RESTORATION_AUDIT.patch.json").read_text(
                encoding="utf-8"
            )
        )

    def fixture(self) -> tuple[dict, dict, dict, dict]:
        seed = {
            "exclude_outputs": sorted(validator.TIER_INSTALLERS),
            "preserve_recipe_ids": sorted(validator.TIER_INSTALLER_RECIPES),
        }
        manifest = {"preserve_recipe_ids": sorted(validator.TIER_INSTALLER_RECIPES)}
        assignments = {
            "nodes": {
                str(contract["node"]): {"unlocks": [output]}
                for output, contract in validator.TIER_INSTALLER_RESTORATION.items()
            }
        }
        return copy.deepcopy(self.restoration), seed, manifest, assignments

    def failures(
        self,
        *,
        restoration: dict | None = None,
        seed: dict | None = None,
        manifest: dict | None = None,
        assignments: dict | None = None,
        managed_outputs: set[str] | None = None,
        managed_ids: set[str] | None = None,
        removal_ids: set[str] | None = None,
        additional_removals: set[str] | None = None,
    ) -> list[str]:
        base_restoration, base_seed, base_manifest, base_assignments = self.fixture()
        return validator.validate_tier_installer_restoration(
            restoration if restoration is not None else base_restoration,
            seed if seed is not None else base_seed,
            manifest if manifest is not None else base_manifest,
            assignments if assignments is not None else base_assignments,
            managed_outputs if managed_outputs is not None else set(),
            managed_ids if managed_ids is not None else set(),
            removal_ids if removal_ids is not None else set(),
            additional_removals if additional_removals is not None else set(),
        )

    def test_reviewed_stock_restoration_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_unknown_installer_fails_closed(self) -> None:
        restoration, _, _, _ = self.fixture()
        restoration["outputs_to_exclude"].append("mekanism:mythic_tier_installer")
        restoration["recipe_ids_to_preserve"].append("mekanism:tier_installer/mythic")
        restoration["automatic_managed_ids_to_retire"].append(
            "industrial_colonies:auto/mekanism/mythic_tier_installer"
        )
        restoration["entries"].append(
            {
                "output": "mekanism:mythic_tier_installer",
                "automatic_managed_id": (
                    "industrial_colonies:auto/mekanism/mythic_tier_installer"
                ),
                "node": "CR01 — Unknown",
                "source_recipe_id": "mekanism:tier_installer/mythic",
                "exact_source_recipe_ids": ["mekanism:tier_installer/mythic"],
                "rationale": validator.TIER_INSTALLER_POLICY,
            }
        )
        self.assertTrue(self.failures(restoration=restoration))

    def test_missing_installer_entry_fails_closed(self) -> None:
        restoration, _, _, _ = self.fixture()
        restoration["entries"] = [
            row
            for row in restoration["entries"]
            if row.get("output") != "mekanism:basic_tier_installer"
        ]
        self.assertTrue(self.failures(restoration=restoration))

    def test_removed_stock_recipe_fails_closed(self) -> None:
        self.assertTrue(
            self.failures(removal_ids={"mekanism:tier_installer/advanced"})
        )

    def test_bare_stock_recipe_removal_fails_closed(self) -> None:
        self.assertTrue(
            self.failures(additional_removals={"mekanism:tier_installer/elite"})
        )

    def test_policy_rationale_drift_fails_closed(self) -> None:
        restoration, _, _, _ = self.fixture()
        row = next(
            row
            for row in restoration["entries"]
            if row.get("output") == "mekanism:ultimate_tier_installer"
        )
        row["rationale"] = "Manage this installer again."
        self.assertTrue(self.failures(restoration=restoration))

    def test_unimplemented_restoration_fails_closed(self) -> None:
        restoration, _, _, _ = self.fixture()
        restoration["status"] = "planned"
        self.assertTrue(self.failures(restoration=restoration))

    def test_recipe_id_drift_fails_closed(self) -> None:
        restoration, _, _, _ = self.fixture()
        row = next(
            row
            for row in restoration["entries"]
            if row.get("output") == "mekanism:advanced_tier_installer"
        )
        row["source_recipe_id"] = "mekanism:tier_installer/basic"
        row["exact_source_recipe_ids"] = ["mekanism:tier_installer/basic"]
        self.assertTrue(self.failures(restoration=restoration))

    def test_node_drift_fails_closed(self) -> None:
        restoration, _, _, _ = self.fixture()
        row = next(
            row
            for row in restoration["entries"]
            if row.get("output") == "mekanism:elite_tier_installer"
        )
        row["node"] = "CR01 — Wrong Node"
        self.assertTrue(self.failures(restoration=restoration))

    def test_missing_seed_exclusion_fails_closed(self) -> None:
        _, seed, _, _ = self.fixture()
        seed["exclude_outputs"].remove("mekanism:basic_tier_installer")
        self.assertTrue(self.failures(seed=seed))

    def test_missing_seed_preserve_fails_closed(self) -> None:
        _, seed, _, _ = self.fixture()
        seed["preserve_recipe_ids"].remove("mekanism:tier_installer/ultimate")
        self.assertTrue(self.failures(seed=seed))

    def test_missing_manifest_preserve_fails_closed(self) -> None:
        _, _, manifest, _ = self.fixture()
        manifest["preserve_recipe_ids"].remove("mekanism:tier_installer/elite")
        self.assertTrue(self.failures(manifest=manifest))

    def test_managed_card_for_restored_output_fails_closed(self) -> None:
        self.assertTrue(
            self.failures(managed_outputs={"mekanism:advanced_tier_installer"})
        )

    def test_surviving_automatic_owner_fails_closed(self) -> None:
        self.assertTrue(
            self.failures(
                managed_ids={
                    "industrial_colonies:auto/mekanism/advanced_tier_installer"
                }
            )
        )

    def test_assignment_node_drift_fails_closed(self) -> None:
        _, _, _, assignments = self.fixture()
        assignments["nodes"]["CR01 — Wrong Node"] = {
            "unlocks": ["mekanism:basic_tier_installer"]
        }
        self.assertTrue(self.failures(assignments=assignments))


if __name__ == "__main__":
    unittest.main()
