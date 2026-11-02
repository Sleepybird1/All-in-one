#!/usr/bin/env python3

from __future__ import annotations

import copy
import unittest

try:
    from tools import migrate_current_review_sources_to_steel_frame as migration
    from tools.migrate_kjsgen_steel_frame import design_hash
except ModuleNotFoundError:  # Direct execution from the tools directory.
    import migrate_current_review_sources_to_steel_frame as migration  # type: ignore
    from migrate_kjsgen_steel_frame import design_hash  # type: ignore


def consumer(recipe_id: str, uid: str, output: str) -> dict:
    return {
        "uid": uid,
        "type": "kjsgen:create_sequenced_assembly",
        "recipeId": recipe_id,
        "comment": f"historical text may mention {migration.OLD_ID}",
        "replaceRecipe": False,
        "slots": {
            "input": {"kind": "ITEM", "id": migration.OLD_ID},
            "transitional": {"kind": "ITEM", "id": migration.OLD_ID},
            "output0": {"kind": "ITEM", "id": output},
        },
        "params": {
            "nested": {"ingredient": migration.OLD_ID},
            "nearMiss": migration.OLD_ID + "_decorative",
        },
    }


def managed_producer() -> dict:
    card = {
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
    assert design_hash(card) == migration.PINNED_PRODUCER_HASH
    return card


def acceptance_producer() -> dict:
    card = {
        "uid": migration.PINNED_PRODUCER_UID,
        "type": "kjsgen:create_mechanical_crafting",
        "recipeId": migration.PINNED_PRODUCER_RECIPE_ID,
        "comment": "[Mekanized Industry] Original rejected casing design",
        "replaceRecipe": False,
        "slots": {
            "cell_0_0": {"kind": "ITEM", "id": "tfmg:steel_casing"},
            "output": {"kind": "ITEM", "id": migration.OLD_ID},
        },
        "params": {"gridW": "1", "gridH": "1"},
    }
    # Tests pass this compact fixture's exact hash into the same pinned-producer
    # safety contract without reproducing the enormous real historical card.
    return card


def decision(card: dict, status: str, reason: str, note: str) -> dict:
    return {
        "uid": card["uid"],
        "status": status,
        "reason": reason,
        "note": note,
        "cardSha256": design_hash(card),
    }


class CurrentReviewSourceMigrationTests(unittest.TestCase):
    def fixture(self) -> tuple[dict, dict, dict, dict, dict]:
        approved = consumer("industrial_colonies:approved", "uid-approved", "example:a")
        rejected = consumer("industrial_colonies:rejected", "uid-rejected", "example:r")
        producer = acceptance_producer()
        reviewed = {
            "schema": 1,
            "project": "default",
            "recipes": [copy.deepcopy(approved), managed_producer()],
            "removals": [{"uid": "remove-stock", "recipeId": migration.OLD_ID}],
            "retiredRecipeUids": ["already-retired"],
            "retiredRemovalUids": [],
        }
        acceptance = {
            "schemaVersion": 1,
            "project": "default",
            "reviewed": 3,
            "approved": 1,
            "rejected": 2,
            "entries": [
                {
                    "recipeId": approved["recipeId"],
                    "decision": decision(approved, "approved", "approved", "keep approval"),
                    "card": copy.deepcopy(approved),
                },
                {
                    "recipeId": rejected["recipeId"],
                    "decision": decision(rejected, "rejected", "manual", "keep rejection"),
                    "card": copy.deepcopy(rejected),
                },
                {
                    "recipeId": producer["recipeId"],
                    "decision": decision(
                        producer, "rejected", "manual", "retired producer evidence"
                    ),
                    "card": copy.deepcopy(producer),
                },
            ],
            "inputSha256": {"liveProject": "historical-provenance"},
        }
        return reviewed, acceptance, approved, rejected, producer

    def test_preserves_classifications_and_retires_only_managed_producer(self) -> None:
        reviewed, acceptance, approved, rejected, producer = self.fixture()
        original_acceptance = copy.deepcopy(acceptance)
        next_reviewed, next_acceptance, report = migration.transform_sources(
            reviewed,
            acceptance,
            acceptance_producer_hash=design_hash(producer),
        )

        self.assertEqual(1, len(next_reviewed["recipes"]))
        managed_card = next_reviewed["recipes"][0]
        self.assertEqual(approved["recipeId"], managed_card["recipeId"])
        self.assertEqual(migration.NEW_ID, managed_card["slots"]["input"]["id"])
        self.assertEqual(migration.NEW_ID, managed_card["slots"]["transitional"]["id"])
        self.assertEqual("example:a", managed_card["slots"]["output0"]["id"])
        self.assertEqual(migration.NEW_ID, managed_card["params"]["nested"]["ingredient"])
        self.assertEqual(
            migration.OLD_ID + "_decorative", managed_card["params"]["nearMiss"]
        )
        self.assertEqual(approved["comment"], managed_card["comment"])
        self.assertEqual(
            [{"uid": "remove-stock", "recipeId": migration.OLD_ID}],
            next_reviewed["removals"],
        )
        self.assertEqual(
            ["already-retired", migration.PINNED_PRODUCER_UID],
            next_reviewed["retiredRecipeUids"],
        )

        before_classes = [
            (
                entry["recipeId"],
                entry["decision"]["status"],
                entry["decision"]["reason"],
                entry["decision"]["note"],
            )
            for entry in original_acceptance["entries"]
        ]
        after_classes = [
            (
                entry["recipeId"],
                entry["decision"]["status"],
                entry["decision"]["reason"],
                entry["decision"]["note"],
            )
            for entry in next_acceptance["entries"]
        ]
        self.assertEqual(before_classes, after_classes)
        self.assertEqual(original_acceptance["inputSha256"], next_acceptance["inputSha256"])
        for entry in next_acceptance["entries"][:2]:
            self.assertEqual(design_hash(entry["card"]), entry["decision"]["cardSha256"])
            self.assertEqual(migration.NEW_ID, entry["card"]["slots"]["input"]["id"])
        self.assertEqual(original_acceptance["entries"][2], next_acceptance["entries"][2])
        self.assertEqual("approved", next_acceptance["entries"][0]["decision"]["status"])
        self.assertEqual("rejected", next_acceptance["entries"][1]["decision"]["status"])
        self.assertEqual(1, report["reviewedManaged"]["producerRetired"])
        self.assertEqual(1, report["reviewedManaged"]["changedConsumers"])
        self.assertEqual(2, report["acceptance"]["changedConsumers"])

        # Canonical outputs are idempotent and keep the retired UID unique.
        again_reviewed, again_acceptance, again_report = migration.transform_sources(
            next_reviewed,
            next_acceptance,
            acceptance_producer_hash=design_hash(producer),
        )
        self.assertEqual(next_reviewed, again_reviewed)
        self.assertEqual(next_acceptance, again_acceptance)
        self.assertEqual(0, again_report["reviewedManaged"]["producerRetired"])
        self.assertEqual(0, again_report["acceptance"]["changedConsumers"])

    def test_rejects_unmanaged_old_output(self) -> None:
        reviewed, acceptance, _, _, producer = self.fixture()
        unsafe = consumer(
            "industrial_colonies:unsafe", "uid-unsafe", migration.OLD_ID
        )
        reviewed["recipes"].insert(0, unsafe)
        with self.assertRaisesRegex(migration.MigrationError, "output migration"):
            migration.transform_sources(
                reviewed,
                acceptance,
                acceptance_producer_hash=design_hash(producer),
            )

    def test_rejects_stale_acceptance_fingerprint(self) -> None:
        reviewed, acceptance, _, _, producer = self.fixture()
        acceptance["entries"][0]["decision"]["cardSha256"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(migration.MigrationError, "fingerprint mismatch"):
            migration.transform_sources(
                reviewed,
                acceptance,
                acceptance_producer_hash=design_hash(producer),
            )


if __name__ == "__main__":
    unittest.main()
