#!/usr/bin/env python3
"""Mutation tests for exact-machine routing in hand-authored endgame sequences."""

from __future__ import annotations

import unittest

import validate_allthemodium_currency as currency_validator
import validate_black_hole_megaproject as megaproject_validator


class TieredMegaprojectSequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        scripts = currency_validator.ROOT / "pack-scripts" / "server_scripts"
        cls.currency = (scripts / "industrial_allthemodium_currency.js").read_text(
            encoding="utf-8-sig"
        )
        cls.reserve = (scripts / "industrial_reserve_core_megaproject.js").read_text(
            encoding="utf-8-sig"
        )

    def test_current_machine_bound_sequences_pass(self) -> None:
        self.assertEqual([], currency_validator.sequence_machine_routing_errors(self.currency))
        self.assertEqual([], megaproject_validator.reserve_machine_routing_errors(self.reserve))

    def test_currency_native_deployer_fallback_is_rejected(self) -> None:
        mutated = self.currency.replace(
            "type: `industrial_colonies:${tier}_deploying`",
            "type: 'create:deploying'",
            1,
        )
        self.assertTrue(currency_validator.sequence_machine_routing_errors(mutated))

    def test_currency_native_press_fallback_is_rejected(self) -> None:
        mutated = self.currency.replace(
            "type: `industrial_colonies:${tier}_pressing`",
            "type: 'create:pressing'",
            1,
        )
        self.assertTrue(currency_validator.sequence_machine_routing_errors(mutated))

    def test_currency_wrong_tier_is_rejected(self) -> None:
        mutated = self.currency.replace(
            "atmDeploying('refined_radiance'",
            "atmDeploying('weathered_iron'",
            1,
        )
        self.assertTrue(currency_validator.sequence_machine_routing_errors(mutated))

    def test_reserve_native_deployer_fallback_is_rejected(self) -> None:
        mutated = self.reserve.replace(
            "industrial_colonies:creative_deploying", "create:deploying", 1
        )
        self.assertTrue(megaproject_validator.reserve_machine_routing_errors(mutated))

    def test_reserve_native_press_fallback_is_rejected(self) -> None:
        mutated = self.reserve.replace(
            "industrial_colonies:creative_pressing", "create:pressing", 1
        )
        self.assertTrue(megaproject_validator.reserve_machine_routing_errors(mutated))

    def test_reserve_native_spout_fallback_is_rejected(self) -> None:
        mutated = self.reserve.replace(
            "industrial_colonies:brass_filling", "create:filling", 1
        )
        self.assertTrue(megaproject_validator.reserve_machine_routing_errors(mutated))


if __name__ == "__main__":
    unittest.main()
