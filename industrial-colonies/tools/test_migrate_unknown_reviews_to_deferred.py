#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

try:
    from tools import migrate_unknown_reviews_to_deferred as migration
except ModuleNotFoundError:
    import migrate_unknown_reviews_to_deferred as migration  # type: ignore


def card(recipe_id: str, number: int) -> dict:
    return {
        "uid": f"uid-{number:04d}",
        "type": "kjsgen:shaped",
        "recipeId": recipe_id,
        "comment": f"card {number}",
        "replaceRecipe": False,
        "slots": {
            "input": {"kind": "ITEM", "id": "minecraft:iron_ingot"},
            "output": {"kind": "ITEM", "id": f"test:output_{number}"},
        },
        "params": {},
    }


def project(name: str, cards: list[dict]) -> dict:
    return {
        "format": 1,
        "name": name,
        "defaultTargetFile": "kjsgen_recipes",
        "exportComments": True,
        "reloadOnExport": False,
        "recipes": copy.deepcopy(cards),
        "removals": [],
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class DeferredMigrationTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, dict[str, bytes], list[str], list[str]]:
        pack = root / "pack"
        projects = pack / "kjsgen" / "projects"
        sync = pack / "kjsgen" / "industrial_colonies_sync"
        counter = 0
        archives: dict[str, list[dict]] = {
            "approved": [],
            "rejected": [],
            "maybe": [],
            "disabled": [],
        }
        reviews: dict[str, dict] = {}

        def add(status: str, recipe_id: str, note: str = "test") -> None:
            nonlocal counter
            counter += 1
            value = card(recipe_id, counter)
            archives[status].append(value)
            reviews[recipe_id] = {
                "uid": value["uid"],
                "status": status,
                "reason": "maybe" if status == "maybe" else "manual",
                "note": note,
                "cardSha256": migration.card_sha256(value),
            }

        for index in range(309):
            add("approved", f"test:approved_{index:03d}")
        candidate_ids = sorted(migration.DEFERRED_RECIPE_IDS)
        add("rejected", "test:rejected_before")
        for recipe_id in candidate_ids:
            add("rejected", recipe_id, "Idk what that is")
        for index in range(440):
            add("rejected", f"test:rejected_{index:03d}")
        for index in range(125):
            add("maybe", f"test:deferred_{index:03d}")
        for index in range(11):
            add("disabled", f"test:disabled_{index:03d}")

        all_cards = [
            *archives["approved"],
            *archives["rejected"],
            *archives["maybe"],
            *archives["disabled"],
        ]
        paths = {
            "default": projects / "default.json",
            "approved": projects / "approved_recipes.json",
            "rejected": projects / "rejected_recipes.json",
            "maybe": projects / "maybe_recipes.json",
            "disabled": projects / "disabled_recipes.json",
            "ledger": sync / "default.recipe_reviews.json",
        }
        write_json(paths["default"], project("default", all_cards))
        write_json(paths["approved"], project("approved recipes", archives["approved"]))
        write_json(paths["rejected"], project("rejected recipes", archives["rejected"]))
        write_json(paths["maybe"], project("maybe recipes", archives["maybe"]))
        write_json(paths["disabled"], project("disabled recipes", archives["disabled"]))
        write_json(
            paths["ledger"],
            {"schemaVersion": 1, "project": "default", "reviews": reviews},
        )
        original = {name: path.read_bytes() for name, path in paths.items()}
        original_maybe_order = [value["recipeId"] for value in archives["maybe"]]
        moved_order = [
            value["recipeId"]
            for value in archives["rejected"]
            if value["recipeId"] in migration.DEFERRED_RECIPE_IDS
        ]
        return pack, original, original_maybe_order, moved_order

    def test_preserves_order_and_moves_exact_curated_set(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack, original, original_maybe_order, moved_order = self.fixture(root)
            stage = root / "stage"

            manifest = migration.migrate(pack, stage)

            ledger = migration.load_json(stage / "default.recipe_reviews.json")
            rejected = migration.load_json(stage / "rejected_recipes.json")
            deferred = migration.load_json(stage / "Deferred.json")
            self.assertEqual(
                {"approved": 309, "rejected": 441, "maybe": 151, "disabled": 11},
                manifest["outputCounts"],
            )
            self.assertEqual("Deferred", deferred["name"])
            self.assertEqual(
                original_maybe_order + moved_order,
                [value["recipeId"] for value in deferred["recipes"]],
            )
            self.assertEqual(441, len(rejected["recipes"]))
            for recipe_id in migration.DEFERRED_RECIPE_IDS:
                record = ledger["reviews"][recipe_id]
                self.assertEqual("maybe", record["status"])
                self.assertEqual("maybe", record["reason"])
                self.assertEqual("Idk what that is", record["note"])
            self.assertEqual(26, len(manifest["candidateRecords"]))
            self.assertEqual(6, len(manifest["outputFiles"]))

            source_paths = {
                "default": pack / "kjsgen/projects/default.json",
                "approved": pack / "kjsgen/projects/approved_recipes.json",
                "rejected": pack / "kjsgen/projects/rejected_recipes.json",
                "maybe": pack / "kjsgen/projects/maybe_recipes.json",
                "disabled": pack / "kjsgen/projects/disabled_recipes.json",
                "ledger": pack / "kjsgen/industrial_colonies_sync/default.recipe_reviews.json",
            }
            for name, path in source_paths.items():
                self.assertEqual(original[name], path.read_bytes(), f"source changed: {name}")

    def test_fails_closed_when_a_curated_decision_changed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack, _, _, _ = self.fixture(root)
            ledger_path = pack / "kjsgen/industrial_colonies_sync/default.recipe_reviews.json"
            ledger = migration.load_json(ledger_path)
            recipe_id = sorted(migration.DEFERRED_RECIPE_IDS)[0]
            ledger["reviews"][recipe_id]["reason"] = "ring_of_items"
            write_json(ledger_path, ledger)

            with self.assertRaisesRegex(migration.MigrationError, "no longer rejected/manual"):
                migration.migrate(pack, root / "stage")
            self.assertFalse((root / "stage").exists())


if __name__ == "__main__":
    unittest.main()
