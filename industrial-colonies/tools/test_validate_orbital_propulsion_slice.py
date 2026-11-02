#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_orbital_propulsion_slice as validator


class OrbitalPropulsionSliceMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        source = TOOLS.parent
        for relative in (
            validator.SEED,
            validator.MANIFEST,
            validator.COMPILED,
            validator.ASSIGNMENTS,
            validator.LAYOUT,
            validator.DEFERRED,
        ):
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self) -> list[str]:
        return validator.validate(
            self.project,
            manifest=self.project / validator.MANIFEST,
            compiled=self.project / validator.COMPILED,
        )

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def recipe(self, payload: dict, recipe_id: str) -> dict:
        return next(row for row in payload["recipes"] if row.get("id") == recipe_id)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_all_four_source_recipes_are_required(self) -> None:
        recipe_id = "industrial_colonies:space/propulsion/engine_nozzle"
        self.mutate_json(
            validator.SEED,
            lambda payload: payload.__setitem__(
                "recipes",
                [row for row in payload["recipes"] if row.get("id") != recipe_id],
            ),
        )
        self.assertTrue(any(recipe_id in failure for failure in self.failures()))

    def test_03_recipe_less_outputs_must_not_invent_removals(self) -> None:
        recipe_id = "industrial_colonies:space/propulsion/hose_anchor"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__(
                "remove", ["rocketnautics:imaginary/hose_anchor"]
            ),
        )
        self.assertTrue(any("invents removal metadata" in failure for failure in self.failures()))

    def test_04_dependency_chain_must_reach_flight_computer(self) -> None:
        recipe_id = "industrial_colonies:space/propulsion/hose_anchor"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id).__setitem__("depends_on", []),
        )
        self.assertTrue(any("not downstream" in failure for failure in self.failures()))

    def test_05_engine_nozzle_must_consume_engine_pipes(self) -> None:
        recipe_id = "industrial_colonies:space/propulsion/engine_nozzle"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id)["key"].__setitem__(
                "P", "tfmg:steel_pipe"
            ),
        )
        self.assertTrue(
            any("lost physical propulsion subassemblies" in failure for failure in self.failures())
        )

    def test_06_cross_mod_thruster_controller_is_pinned(self) -> None:
        recipe_id = "industrial_colonies:space/propulsion/thruster_mount"
        self.mutate_json(
            validator.SEED,
            lambda payload: self.recipe(payload, recipe_id)["key"].__setitem__(
                "C", "minecraft:comparator"
            ),
        )
        self.assertTrue(any("key drifted" in failure for failure in self.failures()))

    def test_07_assignment_must_not_collapse_into_guidance(self) -> None:
        self.mutate_json(
            validator.ASSIGNMENTS,
            lambda payload: payload["nodes"].pop("CR02 — Modular Propulsion"),
        )
        self.assertTrue(any("unlock assignment drifted" in failure for failure in self.failures()))

    def test_08_simple_thruster_must_remain_disabled(self) -> None:
        def mutate(payload: dict) -> None:
            payload["recipes"].append(
                {
                    "id": "industrial_colonies:space/simple_thruster_bypass",
                    "node": "CR02 — Modular Propulsion",
                    "phase": validator.PHASE,
                    "type": "shapeless",
                    "comment": "mutation",
                    "inputs": ["minecraft:stick"],
                    "output": "rocketnautics:rocket_thruster",
                }
            )

        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("simple ship bootstrap" in failure for failure in self.failures()))

    def test_09_physics_assembler_exact_deferral_is_required(self) -> None:
        path = self.project / validator.DEFERRED
        path.write_text(
            path.read_text(encoding="utf-8-sig").replace(
                "    'simulated:physics_assembler'\n",
                "",
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("physics_assembler" in failure for failure in self.failures()))

    def test_10_broad_simulated_removal_is_rejected(self) -> None:
        path = self.project / validator.DEFERRED
        path.write_text(
            path.read_text(encoding="utf-8-sig")
            + "\nevent.remove({ mod: 'simulated' })\n",
            encoding="utf-8",
        )
        self.assertTrue(any("broad recipe removal" in failure for failure in self.failures()))

    def test_11_immutable_minecolonies_layout_stays_untouched(self) -> None:
        path = self.project / validator.LAYOUT
        path.write_text(
            path.read_text(encoding="utf-8-sig") + "\nCR02 — Modular Propulsion\n",
            encoding="utf-8",
        )
        self.assertTrue(any("immutable MineColonies layout" in failure for failure in self.failures()))

    def test_12_assembled_manifest_must_keep_all_four_recipes(self) -> None:
        recipe_id = "industrial_colonies:space/propulsion/engine_pipes"
        self.mutate_json(
            validator.MANIFEST,
            lambda payload: payload.__setitem__(
                "recipes",
                [row for row in payload["recipes"] if row.get("id") != recipe_id],
            ),
        )
        self.assertTrue(
            any("assembled manifest must contain" in failure for failure in self.failures())
        )

    def test_13_merged_project_must_keep_all_four_cards(self) -> None:
        recipe_id = "industrial_colonies:space/propulsion/thruster_mount"
        self.mutate_json(
            validator.COMPILED,
            lambda payload: payload.__setitem__(
                "recipes",
                [row for row in payload["recipes"] if row.get("recipeId") != recipe_id],
            ),
        )
        self.assertTrue(
            any("KJSGen project must contain" in failure for failure in self.failures())
        )

    def test_14_compiled_card_slots_are_pinned(self) -> None:
        recipe_id = "industrial_colonies:space/propulsion/hose_anchor"

        def mutate(payload: dict) -> None:
            card = next(
                row for row in payload["recipes"] if row.get("recipeId") == recipe_id
            )
            card["slots"]["output"]["count"] = 64

        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("KJSGen slots drifted" in failure for failure in self.failures()))


if __name__ == "__main__":
    unittest.main()
