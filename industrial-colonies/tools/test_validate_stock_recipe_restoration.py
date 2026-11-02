#!/usr/bin/env python3
"""Regression tests for stock recipe restoration and focused tag authority."""

from __future__ import annotations

import unittest

import validate_stock_recipe_restoration as validator


class StockRecipeRestorationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.name = "industrial_appliedcreate_kinetic_network.js"
        cls.script = (
            validator.PROJECT_ROOT
            / "pack-scripts"
            / "server_scripts"
            / cls.name
        ).read_text(encoding="utf-8-sig")
        cls.actinide_name = "industrial_nuclear_actinides_01.js"
        cls.actinide_script = (
            validator.PROJECT_ROOT
            / "pack-scripts"
            / "server_scripts"
            / cls.actinide_name
        ).read_text(encoding="utf-8-sig")

    def test_current_project_passes(self) -> None:
        self.assertEqual([], validator.validate_project(validator.PROJECT_ROOT))

    def test_exact_focused_tag_policy_passes(self) -> None:
        self.assertEqual([], validator.validate_script_authority(self.name, self.script))

    def test_unknown_filename_does_not_inherit_tag_exception(self) -> None:
        errors = validator.validate_script_authority("unknown.js", self.script)
        self.assertTrue(any("outside" in error for error in errors), errors)

    def test_recipe_event_cannot_hide_under_tag_exception(self) -> None:
        errors = validator.validate_script_authority(
            self.name, self.script + "\nServerEvents.recipes(event => event.remove({id: 'x:y'}))\n"
        )
        self.assertTrue(any("no recipe event" in error for error in errors), errors)

    def test_cheap_attunement_key_fails(self) -> None:
        errors = validator.validate_script_authority(
            self.name,
            self.script.replace("'appliedcreate:me_gearbox'", "'create:shaft'"),
        )
        self.assertTrue(any("ME Gearbox" in error or "forbidden" in error for error in errors), errors)

    def test_second_tag_addition_fails(self) -> None:
        errors = validator.validate_script_authority(
            self.name, self.script.replace("  event.add", "  event.add(stressAttunement, 'ae2:fluix_block')\n  event.add")
        )
        self.assertTrue(any("add only" in error for error in errors), errors)

    def test_wrong_tag_identity_fails(self) -> None:
        errors = validator.validate_script_authority(
            self.name,
            self.script.replace(
                "appliedcreate:p2p_attunements/stress_p2p_tunnel",
                "appliedcreate:p2p_attunements/other",
            ),
        )
        self.assertTrue(any("tag identity" in error for error in errors), errors)

    def test_exact_actinide_bridge_is_an_active_focused_owner(self) -> None:
        self.assertNotIn(self.actinide_name, validator.RESTORATION_MARKERS)
        self.assertIn(self.actinide_name, validator.ALLOWED_MUTATION_SCRIPTS)
        self.assertEqual(
            [],
            validator.validate_script_authority(
                self.actinide_name, self.actinide_script
            ),
        )

    def test_actinide_authority_does_not_transfer_to_unknown_filename(self) -> None:
        errors = validator.validate_script_authority(
            "unknown_actinide.js", self.actinide_script
        )
        self.assertTrue(any("outside" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
