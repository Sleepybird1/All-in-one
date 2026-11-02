#!/usr/bin/env python3
"""Mutation tests for the final cross-pack loophole-closure validator."""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_cross_pack_progression_loophole_closure as validator


class CrossPackProgressionLoopholeClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = validator.load_json(validator.SEED)
        cls.policies = validator.load_json(validator.POLICIES)
        (
            cls.currency_removals,
            cls.currency_outputs,
            cls.inactive_currency,
        ) = validator.currency_contract()
        cls.exact_removals = validator.seed_removals(cls.seed)
        cls.exact_removals.update(
            validator.canonicalization.parse_removed_recipe_ids(
                validator.SERVER_SCRIPTS
            )
        )
        cls.exact_removals.update(cls.currency_removals)
        cls.protected, cls.protected_counts = validator.protected_outputs(
            cls.seed, cls.policies, cls.currency_outputs
        )
        cls.preserved = {
            str(value)
            for value in cls.seed.get("preserve_recipe_ids", [])
            if isinstance(value, str)
        }
        cls.fixture_root = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.fixture_root.cleanup)
        cls.mods = Path(cls.fixture_root.name) / "mods"
        cls.mods.mkdir()
        cls.source_jar = "fixture.jar"
        (cls.mods / cls.source_jar).touch()

    def policy_failures(
        self,
        *,
        seed=None,
        policies=None,
        protected=None,
        exact_removals=None,
    ) -> list[str]:
        return validator.validate_policy_contracts(
            self.seed if seed is None else seed,
            self.policies if policies is None else policies,
            self.protected if protected is None else protected,
            self.exact_removals if exact_removals is None else exact_removals,
        )

    def fake_row(
        self,
        recipe_id: str,
        output: str,
        *,
        recipe_type: str = "minecraft:crafting_shapeless",
        inputs: str = "minecraft:dirt",
    ) -> dict[str, str]:
        return {
            "recipe_id": recipe_id,
            "namespace": recipe_id.split(":", 1)[0],
            "recipe_type": recipe_type,
            "source_jar": self.source_jar,
            "source_path": f"data/test/recipe/{recipe_id.replace(':', '/')}.json",
            "industrial": "0",
            "outputs": output,
            "inputs": inputs,
            "tags": "",
        }

    def scan(
        self,
        rows,
        protected,
        *,
        exact_removals=None,
        inactive=None,
    ) -> dict:
        return validator.classify_catalog_producers(
            rows,
            self.mods,
            set(protected),
            self.exact_removals if exact_removals is None else exact_removals,
            self.preserved,
            self.inactive_currency if inactive is None else inactive,
        )

    def assert_failure(self, failures: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in failure for failure in failures),
            f"expected failure containing {fragment!r}; got {failures}",
        )

    @staticmethod
    def component(identity: str, returncode: int = 0) -> dict[str, object]:
        return {"id": identity, "purpose": identity, "returncode": returncode}

    def test_01_current_policy_and_catalog_residual_scan_pass(self) -> None:
        self.assertEqual([], self.policy_failures())
        rows = [
            self.fake_row(identity, output)
            for output, identities in validator.ALLOWED_STOCK_PRODUCERS_BY_OUTPUT.items()
            for identity in identities
        ]
        scan = self.scan(rows, validator.ALLOWED_STOCK_PRODUCERS_BY_OUTPUT)
        self.assertEqual({}, scan["unmanaged_residuals"])
        self.assertEqual({}, scan["canonical_survivor_drift"])

    def test_02_fake_printed_silicon_producer_is_rejected(self) -> None:
        row = self.fake_row("test:cheap_silicon_print", "ae2:printed_silicon")
        scan = self.scan([row], {"ae2:printed_silicon"})
        self.assertEqual(
            ["test:cheap_silicon_print"],
            scan["unmanaged_residuals"]["ae2:printed_silicon"],
        )

    def test_03_fake_sulfuric_acid_synthesis_is_rejected(self) -> None:
        row = self.fake_row(
            "test:cheap_acid",
            "tfmg:sulfuric_acid",
            recipe_type="mekanism:chemical_infusing",
        )
        scan = self.scan([row], {"tfmg:sulfuric_acid"})
        self.assertEqual(
            ["test:cheap_acid"],
            scan["unmanaged_residuals"]["tfmg:sulfuric_acid"],
        )

    def test_04_fake_allthemodium_currency_producer_is_rejected(self) -> None:
        row = self.fake_row("test:cheap_allthemodium", "allthemodium:allthemodium_ingot")
        scan = self.scan([row], {"allthemodium:allthemodium_ingot"})
        self.assertEqual(
            ["test:cheap_allthemodium"],
            scan["unmanaged_residuals"]["allthemodium:allthemodium_ingot"],
        )

    def test_05_exact_removal_prevents_a_residual_producer(self) -> None:
        identity = "extendedae:cutter/silicon_print"
        row = self.fake_row(identity, "ae2:printed_silicon")
        scan = self.scan([row], {"ae2:printed_silicon"})
        self.assertEqual(1, scan["classification_counts"]["exactly_removed"])
        removals = set(self.exact_removals)
        removals.remove(identity)
        mutated = self.scan(
            [row], {"ae2:printed_silicon"}, exact_removals=removals
        )
        self.assertEqual(
            [identity], mutated["unmanaged_residuals"]["ae2:printed_silicon"]
        )

    def test_06_retired_digital_miner_removal_is_required(self) -> None:
        removals = set(self.exact_removals)
        removals.remove("mekanism:digital_miner")
        self.assert_failure(
            self.policy_failures(exact_removals=removals),
            "retired technology recipe IDs are not exactly removed",
        )

    def test_07_extendedae_silicon_shortcut_removal_is_required(self) -> None:
        removals = set(self.exact_removals)
        removals.remove("extendedae:cutter/silicon_print")
        self.assert_failure(
            self.policy_failures(exact_removals=removals),
            "ExtendedAE silicon cutting shortcut",
        )

    def test_08_printed_silicon_must_use_tfmg_silicon(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = next(
            value
            for value in seed["recipes"]
            if validator.output_id(value) == "ae2:printed_silicon"
        )
        recipe["inputs"][0] = "ae2:silicon"
        self.assert_failure(
            self.policy_failures(seed=seed),
            "canonical TFMG silicon",
        )

    def test_09_engine_fuel_allowlist_drift_is_rejected(self) -> None:
        policies = copy.deepcopy(self.policies)
        petroleum = next(
            group for group in policies["groups"] if group.get("name") == "petroleum"
        )
        petroleum["cdg_engine_fuel_policy"]["allowed"][
            "createdieselgenerators:biodiesel"
        ] = "c:biodiesel"
        self.assert_failure(
            self.policy_failures(policies=policies),
            "CDG engine canonical fuel allowlist",
        )

    def test_10_sulfuric_acid_tag_drift_is_rejected(self) -> None:
        policies = copy.deepcopy(self.policies)
        sulfur = next(
            group
            for group in policies["groups"]
            if group.get("name") == "sulfur chemistry"
        )
        sulfur["canonical_tags"]["c:sulfuric_acid"] = ["mekanism:sulfuric_acid"]
        self.assert_failure(
            self.policy_failures(policies=policies),
            "TFMG sulfuric-acid canonical fluid contract",
        )

    def test_11_missing_canonical_stock_route_is_rejected(self) -> None:
        output = "tfmg:sulfuric_acid"
        expected = "tfmg:vat_machine_recipe/sulfuric_acid"
        present = self.scan([self.fake_row(expected, output)], {output})
        self.assertNotIn(output, present["canonical_survivor_drift"])
        scan = self.scan([], {output})
        self.assertEqual(
            {"expected": [expected], "observed": []},
            scan["canonical_survivor_drift"][output],
        )

    def test_12_hard_component_failure_sets_failed_status(self) -> None:
        status, blockers = validator.evaluate_release_status(
            [],
            [self.component("nuclear", 1)],
            [self.component("manifest")],
            {"implemented": True},
        )
        self.assertEqual("failed", status)
        self.assertTrue(any("nuclear" in value for value in blockers))

    def test_13_release_freshness_failure_sets_pending_status(self) -> None:
        status, blockers = validator.evaluate_release_status(
            [],
            [self.component("nuclear")],
            [self.component("manifest", 1)],
            {"implemented": True},
        )
        self.assertEqual("pending_big_integration_or_regeneration", status)
        self.assertTrue(any("manifest" in value for value in blockers))

    def test_14_unreleased_big_batch_sets_pending_status(self) -> None:
        status, blockers = validator.evaluate_release_status(
            [],
            [self.component("nuclear")],
            [self.component("manifest")],
            {"implemented": False},
        )
        self.assertEqual("pending_big_integration_or_regeneration", status)
        self.assertTrue(any("Big Reactors" in value for value in blockers))

    def test_15_all_release_gates_green(self) -> None:
        status, blockers = validator.evaluate_release_status(
            [],
            [self.component("nuclear")],
            [self.component("manifest")],
            {"implemented": True},
        )
        self.assertEqual("green", status)
        self.assertEqual([], blockers)

    def test_16_big_release_gate_matches_final_artifact_statuses(self) -> None:
        gate = validator.big_release_gate()
        self.assertEqual("implemented_in_seed", gate["plan_status"])
        self.assertEqual("implemented_in_seed", gate["patch_status"])
        self.assertTrue(gate["implemented"])

    def test_17_report_rendering_is_byte_deterministic(self) -> None:
        report = {
            "status": "green",
            "protected_contract": {
                "unique_protected_outputs": 1,
                "exact_removal_ids": 1,
            },
            "residual_producer_scan": {
                "catalog_rows": 1,
                "installed_source_rows": 1,
                "relevant_installed_rows": 1,
                "unmanaged_residuals": {},
                "classification_counts": {"exactly_removed": 1},
            },
            "component_validators": {
                "authoritative": [self.component("core")],
                "release_freshness": [self.component("release")],
            },
            "release_gate": {"blocking_reasons": []},
        }
        first = validator.render_markdown(report)
        second = validator.render_markdown(copy.deepcopy(report))
        self.assertEqual(first, second)
        self.assertIn("All closure checks are green", first)

    def test_18_component_commands_forward_instance_and_catalog_paths(self) -> None:
        instance = Path(r"Z:\portable\instance")
        catalog = Path(r"Z:\portable\catalog")
        core, release = validator.component_specs(instance, catalog)
        by_id = {value["id"]: value["command"] for value in core + release}
        self.assertIn(str(instance / "mods"), by_id["petroleum_engine_progression"])
        self.assertIn(str(catalog), by_id["tfmg_steelworks"])
        self.assertIn(
            str(catalog / "recipe_catalog.sqlite"),
            by_id["bigreactors_release_integrity"],
        )
        self.assertIn(str(catalog), by_id["managed_manifest_freshness"])


if __name__ == "__main__":
    unittest.main()
