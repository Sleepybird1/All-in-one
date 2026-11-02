#!/usr/bin/env python3
"""Mutation tests for validate_high_voltage_repair_audit.py."""

from __future__ import annotations

import copy
import unittest

import validate_high_voltage_repair_audit as validator


class HighVoltageRepairAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validator.load_json(validator.DEFAULT_PLAN)
        cls.seed = validator.load_json(validator.DEFAULT_SEED)

    def failures(self, plan: dict) -> list[str]:
        return validator.validate_plan(plan, validator.DEFAULT_CATALOG, validator.DEFAULT_MODS)

    def test_current_plan_passes(self) -> None:
        self.assertEqual([], self.failures(copy.deepcopy(self.plan)))

    def test_current_seed_implementation_passes(self) -> None:
        self.assertEqual(
            [],
            validator.validate_seed_implementation(
                copy.deepcopy(self.plan), copy.deepcopy(self.seed)
            ),
        )

    def test_forbidden_mekanism_ingredient_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][1]["inputs"][1] = "mekanism:alloy_reinforced"
        failures = self.failures(plan)
        self.assertTrue(any("forbidden digital/cross-branch ingredient" in row for row in failures))

    def test_forward_same_batch_dependency_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][2]["steps"][0]["ingredient"] = (
            "electroenergetics:voltage_regulator"
        )
        plan["replacement_contracts"][2]["depends_on_batch"] = [
            "industrial_colonies:high_voltage/voltage_regulator"
        ]
        failures = self.failures(plan)
        self.assertTrue(any("same-batch dependency is not earlier" in row for row in failures))

    def test_extreme_removal_cannot_leak_into_analog_contract(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][0]["remove_exact"].append(
            "electroenergetics:crafting/heavily_insulated_wire"
        )
        failures = self.failures(plan)
        self.assertTrue(any("must retire exactly its one audited source recipe" in row for row in failures))
        self.assertTrue(any("Extreme Power Transmission removal leaked" in row for row in failures))

    def test_installed_source_hash_drift_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["source_recipes"][0]["sha256"] = "0" * 64
        failures = self.failures(plan)
        self.assertTrue(any("installed source JSON hash changed" in row for row in failures))

    def test_unapproved_machine_environment_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][0]["machine"] = "create:mechanical_press"
        failures = self.failures(plan)
        self.assertTrue(any("unapproved machine environment" in row for row in failures))

    def test_counted_tag_codec_form_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["replacement_contracts"][1]["inputs"][0] = "8x #c:wires/copper"
        failures = self.failures(plan)
        self.assertTrue(any("counted tag syntax is not supported by KJSGen" in row for row in failures))

    def test_missing_seed_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"] = [
            recipe
            for recipe in seed["recipes"]
            if recipe.get("id") != "industrial_colonies:high_voltage/transformer"
        ]
        failures = validator.validate_seed_implementation(copy.deepcopy(self.plan), seed)
        self.assertTrue(any("expected exactly one authoritative seed recipe" in row for row in failures))

    def test_duplicate_seed_output_owner_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"].append(
            {
                "id": "industrial_colonies:test/duplicate_transformer",
                "phase": "High-Energy Grid",
                "order": 999,
                "type": "shapeless",
                "ingredients": ["minecraft:dirt"],
                "output": "electroenergetics:transformer",
            }
        )
        failures = validator.validate_seed_implementation(copy.deepcopy(self.plan), seed)
        self.assertTrue(any("has seed owners" in row for row in failures))

    def test_seed_removal_broadening_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        recipe = next(
            value
            for value in seed["recipes"]
            if value.get("id") == "industrial_colonies:high_voltage/insulated_wire"
        )
        recipe["remove"].append("electroenergetics:crafting/transformer")
        failures = validator.validate_seed_implementation(copy.deepcopy(self.plan), seed)
        self.assertTrue(any("seed removal is not its one exact approved stock recipe" in row for row in failures))

    def test_craftable_transitional_is_rejected(self) -> None:
        seed = copy.deepcopy(self.seed)
        seed["recipes"].append(
            {
                "id": "industrial_colonies:test/incomplete_core_leak",
                "phase": "High-Energy Grid",
                "order": 999,
                "type": "shapeless",
                "ingredients": ["minecraft:dirt"],
                "output": "electroenergetics:incomplete_transformer_core",
            }
        )
        failures = validator.validate_seed_implementation(copy.deepcopy(self.plan), seed)
        self.assertTrue(any("craftable transitional leaked" in row for row in failures))


if __name__ == "__main__":
    unittest.main()
