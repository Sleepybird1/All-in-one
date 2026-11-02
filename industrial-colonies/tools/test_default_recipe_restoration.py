#!/usr/bin/env python3
"""Focused regression tests for exact reviewed default restoration."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_managed_recipe_manifest as builder


PROJECT = Path(__file__).resolve().parents[1]
POLICY = PROJECT / "progression/default_recipe_restoration_policy.json"
SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
DEPENDENCIES = PROJECT / "tools/machine_recipe_dependencies.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def removal_ids(manifest: dict) -> set[str]:
    result = set(manifest.get("additional_removals", []))
    for recipe in manifest["recipes"]:
        result.update(recipe.get("remove", []))
    for family in manifest["machine_families"]:
        for recipe in family["recipes"]:
            result.update(recipe.get("remove", []))
    return result


class DefaultRecipeRestorationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        document = load(POLICY)
        cls.policy = builder.normalize_default_restoration_policy(POLICY, document)
        cls.catalog = builder.default_catalog().resolve()
        cls.mods = builder.default_mods().resolve()

    def build(self, seed: Path) -> tuple[dict, dict]:
        return builder.build_manifest(
            seed,
            ASSIGNMENTS,
            DEPENDENCIES,
            self.catalog,
            self.mods,
        )

    def test_frozen_policy_has_exact_active_counts(self) -> None:
        self.assertTrue(self.policy["active"])
        self.assertEqual(160, len(self.policy["recipe_ids"]))
        self.assertEqual(160, len(self.policy["outputs"]))
        self.assertEqual(178, len(self.policy["removal_ids"]))
        self.assertEqual(
            {"default_recipe": 14, "restore_default_recipe": 146},
            dict(self.policy["reason_counts"]),
        )

    def test_policy_build_changes_only_exact_recipes_and_removals(self) -> None:
        seed = load(SEED)
        baseline_seed = copy.deepcopy(seed)
        baseline_seed.pop("default_restoration_policy")
        with tempfile.TemporaryDirectory(dir=PROJECT / "build") as directory:
            baseline_path = Path(directory) / "baseline.seed.json"
            write(baseline_path, baseline_seed)
            baseline, _ = self.build(baseline_path)
            restored, report = self.build(SEED)

        baseline_recipes = {recipe["id"]: recipe for recipe in baseline["recipes"]}
        restored_recipes = {recipe["id"]: recipe for recipe in restored["recipes"]}
        removed_recipe_ids = set(baseline_recipes) - set(restored_recipes)
        self.assertEqual(set(self.policy["recipe_ids"]), removed_recipe_ids)
        self.assertFalse(set(restored_recipes) - set(baseline_recipes))
        for recipe_id in restored_recipes:
            expected = copy.deepcopy(baseline_recipes[recipe_id])
            dependencies = [
                dependency
                for dependency in expected.get("depends_on", [])
                if dependency not in set(self.policy["recipe_ids"])
            ]
            if dependencies:
                expected["depends_on"] = dependencies
            else:
                expected.pop("depends_on", None)
            self.assertEqual(expected, restored_recipes[recipe_id])

        baseline_removals = removal_ids(baseline)
        restored_removals = removal_ids(restored)
        self.assertEqual(
            set(self.policy["removal_ids"]), baseline_removals - restored_removals
        )
        self.assertFalse(restored_removals - baseline_removals)
        self.assertTrue(set(self.policy["removal_ids"]) <= set(restored["preserve_recipe_ids"]))
        managed_outputs = {
            output
            for recipe in restored["recipes"]
            for output in builder.extract_recipe_outputs(recipe, recipe["id"])
        }
        self.assertFalse(managed_outputs & set(self.policy["outputs"]))
        self.assertEqual(160, report["counts"]["retired_default_recipes"])
        self.assertEqual(178, report["counts"]["restored_default_removals"])
        self.assertEqual(
            len(baseline_recipes) - len(self.policy["recipe_ids"]),
            report["counts"]["managed_recipes"],
        )

    def test_shared_removal_ambiguity_fails_closed(self) -> None:
        seed = load(SEED)
        retired_ids = set(self.policy["recipe_ids"])
        surviving = next(recipe for recipe in seed["recipes"] if recipe["id"] not in retired_ids)
        shared = self.policy["removal_ids"][0]
        surviving.setdefault("remove", []).append(shared)
        with tempfile.TemporaryDirectory(dir=PROJECT / "build") as directory:
            seed_path = Path(directory) / "shared.seed.json"
            write(seed_path, seed)
            with self.assertRaisesRegex(
                builder.ManifestBuildError, "surviving owners"
            ):
                self.build(seed_path)

    def test_output_drift_fails_closed(self) -> None:
        seed = load(SEED)
        policy = load(POLICY)
        policy["entries"][0]["outputs"] = ["minecraft:barrier"]
        with tempfile.TemporaryDirectory(dir=PROJECT / "build") as directory:
            temporary = Path(directory)
            policy_path = temporary / "policy.json"
            seed_path = temporary / "seed.json"
            write(policy_path, policy)
            seed["default_restoration_policy"] = policy_path.relative_to(PROJECT).as_posix()
            write(seed_path, seed)
            with self.assertRaisesRegex(
                builder.ManifestBuildError, "output fingerprint drifted"
            ):
                self.build(seed_path)


if __name__ == "__main__":
    unittest.main()
