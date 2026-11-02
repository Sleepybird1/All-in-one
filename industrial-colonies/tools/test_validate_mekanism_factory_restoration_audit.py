#!/usr/bin/env python3
"""Focused mutation tests for the implementation-ready Factory audit."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
VALIDATOR = PROJECT / "tools" / "validate_mekanism_factory_restoration_audit.py"
PLAN = PROJECT / "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json"
SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
BLACKLIST_RESOURCE = PROJECT / "src/main/resources/data/mekanism/tags/block/blacklist/installer_upgradeable.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


class FactoryRestorationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load(PLAN)
        cls.seed = load(SEED)
        cls.manifest = load(MANIFEST)
        cls.assignments = load(ASSIGNMENTS)

    @staticmethod
    def is_factory_output(value: Any) -> bool:
        return (
            isinstance(value, str)
            and value.startswith("mekanism:")
            and value.endswith("_factory")
            and any(f"mekanism:{tier}_" in value for tier in ("basic", "advanced", "elite", "ultimate"))
        )

    def manifest_for_seed(self, seed: dict[str, Any]) -> dict[str, Any]:
        """Represent isolated assembler output without touching committed artifacts."""
        result = copy.deepcopy(self.manifest)
        result["recipes"] = [
            recipe
            for recipe in result.get("recipes", [])
            if not self.is_factory_output(recipe.get("output") if isinstance(recipe, dict) else None)
        ]
        result["recipes"].extend(
            copy.deepcopy(recipe)
            for recipe in seed.get("recipes", [])
            if isinstance(recipe, dict) and self.is_factory_output(recipe.get("output"))
        )
        return result

    def run_documents(
        self,
        *,
        plan: dict[str, Any] | None = None,
        seed: dict[str, Any] | None = None,
        manifest: dict[str, Any] | None = None,
        assignments: dict[str, Any] | None = None,
        installer_blacklist: dict[str, Any] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="factory-audit-test-") as raw:
            root = Path(raw)
            paths: dict[str, Path] = {}
            selected_seed = self.seed if seed is None else seed
            selected_manifest = self.manifest_for_seed(selected_seed) if manifest is None else manifest
            documents = {
                "plan": self.plan if plan is None else plan,
                "seed": selected_seed,
                "manifest": selected_manifest,
                "assignments": self.assignments if assignments is None else assignments,
            }
            for name, value in documents.items():
                path = root / f"{name}.json"
                path.write_text(json.dumps(value), encoding="utf-8")
                paths[name] = path
            blacklist_path = BLACKLIST_RESOURCE
            if installer_blacklist is not None:
                blacklist_path = root / "installer_upgradeable.json"
                blacklist_path.write_text(json.dumps(installer_blacklist), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--plan",
                    str(paths["plan"]),
                    "--seed",
                    str(paths["seed"]),
                    "--manifest",
                    str(paths["manifest"]),
                    "--assignments",
                    str(paths["assignments"]),
                    "--installer-blacklist",
                    str(blacklist_path),
                ],
                cwd=PROJECT,
                text=True,
                capture_output=True,
                check=False,
            )

    def assert_rejected(self, result: subprocess.CompletedProcess[str], fragment: str) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(fragment, result.stdout + result.stderr)

    def test_01_current_audit_boundary_passes(self) -> None:
        result = self.run_documents()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_02_missing_tier_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["tiers"].pop()
        self.assert_rejected(self.run_documents(plan=plan), "exactly Basic")

    def test_03_missing_process_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["processes"].pop()
        self.assert_rejected(self.run_documents(plan=plan), "eight non-smelting")

    def test_04_changed_jar_hash_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["installed_mod_sha256"] = "0" * 64
        self.assert_rejected(self.run_documents(plan=plan), "JAR hash changed")

    def test_05_changed_source_hash_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["source_sha256"]["mekanism:factory/basic/combining"] = "0" * 64
        self.assert_rejected(self.run_documents(plan=plan), "installed source hash changed")

    def test_06_missing_source_hash_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        del plan["source_sha256"]["mekanism:factory/basic/smelting"]
        self.assert_rejected(self.run_documents(plan=plan), "exactly all 36")

    def test_07_changed_runtime_class_hash_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["runtime_class_sha256"]["mekanism/common/item/ItemTierInstaller.class"] = "0" * 64
        self.assert_rejected(self.run_documents(plan=plan), "runtime class hash changed")

    def test_08_missing_direct_factory_removal_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].remove("mekanism:factory/basic/smelting")
        self.assert_rejected(self.run_documents(seed=seed), "all 36 direct Factory recipes")

    def test_09_extra_factory_removal_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["additional_removals"].append("mekanism:factory/basic/not_real")
        self.assert_rejected(self.run_documents(seed=seed), "all 36 direct Factory recipes")

    def test_10_smelting_managed_producer_is_rejected(self) -> None:
        manifest = self.manifest_for_seed(self.seed)
        manifest["recipes"].append(
            {
                "id": "industrial_colonies:test/forbidden_smelting_factory",
                "type": "shaped",
                "output": "mekanism:basic_smelting_factory",
            }
        )
        self.assert_rejected(self.run_documents(manifest=manifest), "forbids managed Factory recipe owners")

    def test_11_retirement_set_mutation_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["intentional_retirements"].append("mekanism:factory/basic/smelting")
        self.assert_rejected(self.run_documents(plan=plan), "must not retire any Factory output")

    def test_12_unprotected_player_infuser_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["user_owned_outputs"].remove("mekanism:metallurgic_infuser")
        self.assert_rejected(self.run_documents(seed=seed), "no longer protected")

    def test_13_incomplete_assignment_additions_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["assignment_delta"]["additions"][0]["outputs"].pop()
        self.assert_rejected(self.run_documents(plan=plan), "exact 16 additions")

    def test_14_incomplete_assignment_removals_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["assignment_delta"]["removals"][0]["outputs"].pop()
        self.assert_rejected(self.run_documents(plan=plan), "exact eight chemical-node moves")

    def test_15_wrong_scope_count_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["scope"]["replacement_count"] = 1
        self.assert_rejected(self.run_documents(plan=plan), "scope counts")

    def test_16_wrong_installer_route_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installer_upgrade_contract"]["construction_route"] = "craft_directly"
        self.assert_rejected(self.run_documents(plan=plan), "Tier Installer right-click")

    def test_17_non_consuming_installer_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installer_upgrade_contract"]["installer_consumed"] = False
        self.assert_rejected(self.run_documents(plan=plan), "consume the Tier Installer")

    def test_18_missing_tier_installer_recipe_contract_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        del plan["installer_upgrade_contract"]["tier_installer_recipe_ids"]["basic"]
        self.assert_rejected(self.run_documents(plan=plan), "four managed Tier Installer recipes")

    def test_19_state_transfer_regression_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installer_upgrade_contract"]["state_fields"].remove("inventory")
        self.assert_rejected(self.run_documents(plan=plan), "state-transfer field inventory")

    def test_20_factory_blacklisting_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installer_bypass_closure"]["factory_base_blocks"].append(
            "mekanism:enrichment_chamber"
        )
        self.assert_rejected(self.run_documents(plan=plan), "must not block any Factory predecessor")

    def test_21_energy_cube_blacklist_gap_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installer_bypass_closure"]["energy_cube_blocks"].pop()
        self.assert_rejected(self.run_documents(plan=plan), "exactly the four owned cubes")

    def test_22_transmitter_blacklisting_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installer_bypass_closure"]["energy_cube_blocks"].append("mekanism:advanced_universal_cable")
        self.assert_rejected(self.run_documents(plan=plan), "transmitters must remain excluded")

    def test_23_transmitter_evidence_gap_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["installer_bypass_closure"]["excluded_transmitter_blocks"].pop()
        self.assert_rejected(self.run_documents(plan=plan), "exactly the 20 reviewed")

    def test_24_wrong_concrete_blacklist_resource_is_rejected(self) -> None:
        self.assert_rejected(
            self.run_documents(installer_blacklist={"replace": False, "values": []}),
            "exact four-value contract",
        )

    def test_25_managed_factory_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"].append(
            {
                "id": "industrial_colonies:test/basic_combining_factory",
                "type": "shaped",
                "output": "mekanism:basic_combining_factory",
            }
        )
        self.assert_rejected(self.run_documents(seed=seed), "forbids managed Factory recipe owners")

    def test_26_missing_factory_output_exclusion_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["exclude_outputs"].remove("mekanism:basic_combining_factory")
        self.assert_rejected(self.run_documents(seed=seed), "all 36 Factory outputs")

    def test_27_missing_implemented_assignment_is_rejected(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"]["CR01 — Modular Machinery"]["unlocks"].remove(
            "mekanism:basic_crushing_factory"
        )
        self.assert_rejected(self.run_documents(assignments=assignments), "implemented assignment is missing")

    def test_28_stale_chemical_assignment_is_rejected(self) -> None:
        assignments = copy.deepcopy(self.assignments)
        assignments["nodes"]["CR01 — Modular Machinery"]["unlocks"].append(
            "mekanism:basic_injecting_factory"
        )
        self.assert_rejected(self.run_documents(assignments=assignments), "still contains moved output")


if __name__ == "__main__":
    unittest.main()
