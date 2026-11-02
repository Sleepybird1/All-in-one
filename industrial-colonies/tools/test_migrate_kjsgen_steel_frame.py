#!/usr/bin/env python3

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

try:
    from tools import migrate_kjsgen_steel_frame as migration
except ModuleNotFoundError:  # Direct execution from the tools directory.
    import migrate_kjsgen_steel_frame as migration  # type: ignore


def card(recipe_id: str, uid: str, *, ingredient: str, output: str) -> dict:
    return {
        "uid": uid,
        "type": "kjsgen:create_mechanical_crafting",
        "recipeId": recipe_id,
        "comment": migration.OLD_ID,
        "replaceRecipe": False,
        "slots": {
            "cell_0_0": {"kind": "ITEM", "id": ingredient},
            "output": {"kind": "ITEM", "id": output},
        },
        "params": {
            "machineReference": migration.OLD_ID,
            "nearMiss": migration.OLD_ID + "_decorative",
        },
    }


def project(name: str, cards: list[dict]) -> dict:
    return {
        "format": 1,
        "name": name,
        "defaultTargetFile": "kjsgen_recipes.js",
        "exportComments": True,
        "reloadOnExport": False,
        "recipes": copy.deepcopy(cards),
        "removals": [{"uid": "removal", "recipeId": migration.OLD_ID}],
    }


def pinned_producer() -> dict:
    recipe = {
        "uid": migration.PINNED_PRODUCER_UID,
        "type": "kjsgen:create_compacting",
        "recipeId": migration.PINNED_PRODUCER_RECIPE_ID,
        "comment": (
            "[High-Energy Grid] Press the foundational Mekanism shell from a TFMG "
            "steel body and frame, osmium rails, inspection glass, rubber isolation, "
            "and Basic control."
        ),
        "replaceRecipe": False,
        "slots": {
            "__machine_process_compacting": {
                "kind": "ITEM",
                "id": "createcasing:industrial_iron_press",
            },
            "in0": {"kind": "ITEM", "id": "tfmg:steel_casing", "count": 2},
            "in1": {"kind": "ITEM", "id": "tfmg:steel_frame", "count": 2},
            "in2": {"kind": "ITEM", "id": "mekanism:ingot_osmium", "count": 2},
            "in3": {"kind": "ITEM", "id": "minecraft:glass", "count": 2},
            "in4": {"kind": "ITEM", "id": "tfmg:rubber_sheet"},
            "in5": {"kind": "ITEM", "id": "mekanism:basic_control_circuit"},
            "output": {"kind": "ITEM", "id": migration.OLD_ID},
        },
        "params": {"heat": "none"},
    }
    assert migration.design_hash(recipe) == migration.PINNED_PRODUCER_HASH
    return recipe


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class SteelFrameMigrationTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, list[Path], Path, dict[str, dict]]:
        statuses = {
            "approved": "approved recipes",
            "rejected": "rejected recipes",
            "maybe": "Deferred",
            "disabled": "disabled recipes",
        }
        cards: dict[str, dict] = {}
        archives: list[Path] = []
        reviews: dict[str, dict] = {}
        for index, (status, project_name) in enumerate(statuses.items()):
            recipe_id = f"industrial_colonies:{status}_machine"
            recipe = card(
                recipe_id,
                f"uid-{status}",
                ingredient=migration.OLD_ID,
                output=f"example:{status}_machine",
            )
            cards[status] = recipe
            reviews[recipe_id] = {
                "uid": recipe["uid"],
                "status": status,
                "reason": status,
                "note": f"preserve {status}",
                "cardSha256": migration.design_hash(recipe),
            }
            archive_cards = [recipe]
            if status == "rejected":
                producer = pinned_producer()
                archive_cards.append(producer)
                reviews[producer["recipeId"]] = {
                    "uid": migration.PINNED_PRODUCER_UID,
                    "status": "rejected",
                    "reason": "manual",
                    "note": migration.PINNED_PRODUCER_NOTE,
                    "cardSha256": migration.PINNED_PRODUCER_HASH,
                }
            archive_path = root / f"{status}.json"
            write_json(archive_path, project(project_name, archive_cards))
            archives.append(archive_path)
        default_path = root / "default.json"
        write_json(default_path, project("default", [*cards.values(), pinned_producer()]))
        ledger_path = root / "default.recipe_reviews.json"
        write_json(
            ledger_path,
            {"schemaVersion": 1, "project": "default", "reviews": reviews},
        )
        write_json(root / migration.BASE_MIGRATION_MANIFEST, {"schemaVersion": 1})
        return default_path, archives, ledger_path, cards

    def test_stages_all_archives_and_preserves_approved_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            default_path, archives, ledger_path, original_cards = self.fixture(root)
            source_bytes = {path: path.read_bytes() for path in [default_path, *archives, ledger_path]}
            output = root / "stage"

            report = migration.stage_migration(default_path, archives, ledger_path, output)

            staged_default = json.loads((output / default_path.name).read_text(encoding="utf-8"))
            staged_ledger = json.loads((output / ledger_path.name).read_text(encoding="utf-8"))
            staged_rejected = json.loads((output / "rejected.json").read_text(encoding="utf-8"))
            staged_disabled = json.loads((output / "disabled.json").read_text(encoding="utf-8"))
            approved = next(
                recipe
                for recipe in staged_default["recipes"]
                if recipe["recipeId"] == "industrial_colonies:approved_machine"
            )
            approved_record = staged_ledger["reviews"][approved["recipeId"]]
            self.assertEqual(migration.NEW_ID, approved["slots"]["cell_0_0"]["id"])
            self.assertEqual("example:approved_machine", approved["slots"]["output"]["id"])
            self.assertEqual("industrial_colonies:approved_machine", approved["recipeId"])
            self.assertEqual("approved", approved_record["status"])
            self.assertEqual("preserve approved", approved_record["note"])
            self.assertEqual(migration.design_hash(approved), approved_record["cardSha256"])
            self.assertNotEqual(
                migration.design_hash(original_cards["approved"]),
                approved_record["cardSha256"],
            )
            self.assertEqual(migration.OLD_ID, approved["comment"])
            self.assertEqual(migration.NEW_ID, approved["params"]["machineReference"])
            self.assertEqual(
                migration.OLD_ID + "_decorative", approved["params"]["nearMiss"]
            )
            self.assertEqual(
                [{"uid": "removal", "recipeId": migration.OLD_ID}],
                staged_default["removals"],
            )
            self.assertEqual(
                {"approved": 1, "disabled": 2, "maybe": 1, "rejected": 1},
                report["reviewStatusCounts"],
            )
            self.assertEqual(
                {"approved": 1, "disabled": 1, "maybe": 1, "rejected": 2},
                report["reviewStatusCountsBefore"],
            )
            producer_record = staged_ledger["reviews"][migration.PINNED_PRODUCER_RECIPE_ID]
            self.assertEqual("disabled", producer_record["status"])
            self.assertEqual("redundant_mechanic", producer_record["reason"])
            self.assertEqual(migration.PINNED_PRODUCER_NOTE, producer_record["note"])
            self.assertEqual(migration.PINNED_PRODUCER_HASH, producer_record["cardSha256"])
            self.assertFalse(
                any(
                    recipe["recipeId"] == migration.PINNED_PRODUCER_RECIPE_ID
                    for recipe in staged_rejected["recipes"]
                )
            )
            disabled_producer = next(
                recipe
                for recipe in staged_disabled["recipes"]
                if recipe["recipeId"] == migration.PINNED_PRODUCER_RECIPE_ID
            )
            self.assertEqual(pinned_producer(), disabled_producer)
            default_producer = next(
                recipe
                for recipe in staged_default["recipes"]
                if recipe["recipeId"] == migration.PINNED_PRODUCER_RECIPE_ID
            )
            self.assertEqual(pinned_producer(), default_producer)
            self.assertEqual(9, report["changedCards"])
            self.assertEqual(8, report["referenceChangedCardSnapshots"])
            self.assertEqual(16, report["replacements"])
            self.assertEqual(4, report["ledgerHashesUpdated"])
            self.assertEqual(5, len(report["changedRecipeIds"]))
            self.assertEqual(9, len(report["changedCardSnapshots"]))
            self.assertEqual(6, len(report["artifacts"]))
            for artifact in report["artifacts"]:
                staged_path = Path(artifact["stagedPath"])
                self.assertEqual(
                    artifact["stagedSha256"],
                    hashlib.sha256(staged_path.read_bytes()).hexdigest(),
                )
            self.assertEqual(
                (root / migration.BASE_MIGRATION_MANIFEST).read_bytes(),
                (output / migration.BASE_MIGRATION_MANIFEST).read_bytes(),
            )
            self.assertIn("baseMigrationManifest", report)
            for path, before in source_bytes.items():
                self.assertEqual(before, path.read_bytes(), f"source was edited: {path}")

            # A second run from identical inputs produces byte-identical project/ledger files.
            second = root / "stage-again"
            migration.stage_migration(default_path, archives, ledger_path, second)
            for path in [default_path, *archives, ledger_path]:
                self.assertEqual(
                    (output / path.name).read_bytes(),
                    (second / path.name).read_bytes(),
                )

    def test_rejects_old_id_as_recipe_output_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bad = card(
                "industrial_colonies:unsafe_output",
                "uid-unsafe",
                ingredient="minecraft:iron_ingot",
                output=migration.OLD_ID,
            )
            default_path = root / "default.json"
            approved_path = root / "approved.json"
            ledger_path = root / "ledger.json"
            write_json(default_path, project("default", [bad]))
            write_json(approved_path, project("approved recipes", [bad]))
            write_json(
                ledger_path,
                {
                    "schemaVersion": 1,
                    "project": "default",
                    "reviews": {
                        bad["recipeId"]: {
                            "uid": bad["uid"],
                            "status": "approved",
                            "reason": "approved",
                            "note": "",
                            "cardSha256": migration.design_hash(bad),
                        }
                    },
                },
            )
            output = root / "stage"
            with self.assertRaisesRegex(migration.MigrationError, "output migration"):
                migration.stage_migration(
                    default_path, [approved_path], ledger_path, output
                )
            self.assertFalse(output.exists())

    def test_rejects_affected_card_when_ledger_hash_has_no_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            default_path, archives, ledger_path, _ = self.fixture(root)
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            record = ledger["reviews"]["industrial_colonies:approved_machine"]
            record["cardSha256"] = "sha256:" + "0" * 64
            # Make the Approved archive agree with the bad ledger only impossible: the
            # strict archive validation must stop before any staged files are written.
            write_json(ledger_path, ledger)
            output = root / "stage"
            with self.assertRaisesRegex(migration.MigrationError, "fingerprint mismatch"):
                migration.stage_migration(default_path, archives, ledger_path, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
