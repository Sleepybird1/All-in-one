#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path

from tools.reconcile_kjsgen_review_batch import design_hash
from tools.stage_rejected_recipe_redesign import (
    MANIFEST_FILENAME,
    OUTPUT_FILENAMES,
    REPORT_FILENAME,
    RequeueError,
    encoded,
    file_sha256,
    stage_requeue,
    transaction_id,
)


TARGET_ID = "test:target_machine"
TARGET_UID = "uid-target-machine"


def card(
    uid: str,
    recipe_id: str,
    output: str,
    ingredient: str = "minecraft:iron_ingot",
) -> dict:
    return {
        "uid": uid,
        "type": "kjsgen:shaped",
        "recipeId": recipe_id,
        "comment": "[Synthetic] Review workflow fixture",
        "replaceRecipe": False,
        "slots": {
            "in0": {"kind": "ITEM", "id": ingredient},
            "output": {"kind": "ITEM", "id": output},
        },
        "params": {"width": 1, "height": 1},
    }


def project(name: str, recipes: list[dict]) -> dict:
    return {
        "format": 1,
        "name": name,
        "defaultTargetFile": "synthetic.js",
        "exportComments": True,
        "reloadOnExport": False,
        "recipes": copy.deepcopy(recipes),
        "removals": [],
    }


def review(card_value: dict, status: str, reason: str, note: str = "") -> dict:
    return {
        "uid": card_value["uid"],
        "status": status,
        "reason": reason,
        "note": note,
        "cardSha256": design_hash(card_value),
    }


def acceptance_entry(card_value: dict, status: str, note: str = "") -> dict:
    return {
        "recipeId": card_value["recipeId"],
        "decision": {
            "uid": card_value["uid"],
            "status": status,
            "reason": status,
            "note": note,
            "cardSha256": design_hash(card_value),
        },
        "card": copy.deepcopy(card_value),
    }


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class SyntheticCorpus:
    def __init__(
        self,
        root: Path,
        *,
        reviewed_contains_target: bool = True,
        acceptance_target_status: str = "rejected",
    ) -> None:
        self.root = root
        self.target = card(
            TARGET_UID,
            TARGET_ID,
            "test:target_machine_output",
        )
        self.approved = card(
            "uid-approved", "test:approved", "test:approved_output"
        )
        self.deferred = card(
            "uid-deferred", "test:deferred", "test:deferred_output"
        )
        self.disabled = card(
            "uid-disabled", "test:disabled", "test:disabled_output"
        )
        # This legacy rejection deliberately has a ledger/archive record but no
        # Default card.  The real corpus contains this kind of immutable orphan
        # evidence, and staging must preserve it without treating it as active.
        self.legacy_orphan = card(
            "uid-legacy-orphan",
            "test:legacy_orphan",
            "test:legacy_orphan_output",
        )
        self.redesign = copy.deepcopy(self.target)
        self.redesign["slots"]["in0"]["id"] = "minecraft:steel_ingot"
        self.redesign["comment"] = "[Synthetic] Genuinely redesigned"

        self.projects = OrderedDict((
            (
                "default",
                project(
                    "default",
                    [self.target, self.approved, self.deferred, self.disabled],
                ),
            ),
            ("approved", project("approved recipes", [self.approved])),
            (
                "rejected",
                project("rejected recipes", [self.target, self.legacy_orphan]),
            ),
            ("deferred", project("Deferred", [self.deferred])),
            ("disabled", project("disabled recipes", [self.disabled])),
        ))
        self.ledger = {
            "schemaVersion": 1,
            "project": "default",
            "reviews": OrderedDict((
                (
                    TARGET_ID,
                    review(
                        self.target,
                        "rejected",
                        "manual",
                        "The original rejection note must survive.",
                    ),
                ),
                (
                    self.approved["recipeId"],
                    review(self.approved, "approved", "approved"),
                ),
                (
                    self.deferred["recipeId"],
                    review(self.deferred, "maybe", "maybe", "Revisit later."),
                ),
                (
                    self.disabled["recipeId"],
                    review(self.disabled, "disabled", "redundant", "Do not craft."),
                ),
                (
                    self.legacy_orphan["recipeId"],
                    review(self.legacy_orphan, "rejected", "manual", "Historical."),
                ),
            )),
        }
        reviewed_cards = [self.approved]
        if reviewed_contains_target:
            reviewed_cards.insert(0, self.target)
        self.reviewed = {
            "schema": 1,
            "project": "default",
            "recipes": copy.deepcopy(reviewed_cards),
            "removals": [],
            "retiredRecipeUids": (
                [] if reviewed_contains_target else [TARGET_UID, "other-retired"]
            ),
            "retiredRemovalUids": [],
        }
        entries = [
            acceptance_entry(
                self.target,
                acceptance_target_status,
                "Frozen first-pass rejection.",
            ),
            acceptance_entry(self.approved, "approved"),
        ]
        status_counts = {
            status: sum(
                entry["decision"]["status"] == status for entry in entries
            )
            for status in ("approved", "rejected")
        }
        self.acceptance = {
            "schemaVersion": 1,
            "project": "default",
            "reviewed": len(entries),
            "approved": status_counts["approved"],
            "rejected": status_counts["rejected"],
            "entries": entries,
        }
        self.paths = OrderedDict(
            (label, root / f"input-{label}.json") for label in self.projects
        )
        self.ledger_path = root / "input-ledger.json"
        self.reviewed_path = root / "input-reviewed-managed.json"
        self.acceptance_path = root / "input-acceptance.json"
        self.history_path = root / "input-history-does-not-exist.json"
        self.redesign_path = root / "separately-authored-redesign.json"
        self.output_path = root / "staged-output"
        for label, document in self.projects.items():
            self.paths[label].write_bytes(encoded(document))
        self.ledger_path.write_bytes(encoded(self.ledger))
        self.reviewed_path.write_bytes(encoded(self.reviewed))
        self.acceptance_path.write_bytes(encoded(self.acceptance))
        self.redesign_path.write_bytes(encoded(self.redesign))

    def run(self) -> dict:
        return stage_requeue(
            project_paths=self.paths,
            ledger_path=self.ledger_path,
            reviewed_managed_path=self.reviewed_path,
            acceptance_path=self.acceptance_path,
            redesign_path=self.redesign_path,
            recipe_id=TARGET_ID,
            output_directory=self.output_path,
            history_path=self.history_path,
        )

    def source_bytes(self) -> dict[Path, bytes]:
        paths = list(self.paths.values()) + [
            self.ledger_path,
            self.reviewed_path,
            self.acceptance_path,
            self.redesign_path,
        ]
        return {path: path.read_bytes() for path in paths}


class RejectedRedesignRequeueTests(unittest.TestCase):
    def test_changed_rejection_stages_as_pending_and_preserves_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = SyntheticCorpus(Path(temporary))
            before = corpus.source_bytes()

            manifest = corpus.run()

            self.assertEqual(before, corpus.source_bytes())
            self.assertFalse(corpus.history_path.exists())
            self.assertTrue(corpus.output_path.is_dir())
            default = read_json(corpus.output_path / OUTPUT_FILENAMES["default"])
            rejected = read_json(corpus.output_path / OUTPUT_FILENAMES["rejected"])
            ledger = read_json(corpus.output_path / OUTPUT_FILENAMES["ledger"])
            reviewed = read_json(
                corpus.output_path / OUTPUT_FILENAMES["reviewedManaged"]
            )
            acceptance = read_json(
                corpus.output_path / OUTPUT_FILENAMES["acceptance"]
            )
            history = read_json(corpus.output_path / OUTPUT_FILENAMES["history"])
            report = read_json(corpus.output_path / REPORT_FILENAME)

            staged_target = next(
                value for value in default["recipes"] if value["recipeId"] == TARGET_ID
            )
            self.assertEqual(design_hash(staged_target), design_hash(corpus.redesign))
            self.assertNotIn(
                TARGET_ID, {value["recipeId"] for value in rejected["recipes"]}
            )
            self.assertIn(
                corpus.legacy_orphan["recipeId"],
                {value["recipeId"] for value in rejected["recipes"]},
            )
            self.assertNotIn(TARGET_ID, ledger["reviews"])
            for label in ("approved", "deferred", "disabled"):
                archive = read_json(corpus.output_path / OUTPUT_FILENAMES[label])
                self.assertNotIn(
                    TARGET_ID, {value["recipeId"] for value in archive["recipes"]}
                )

            reviewed_target = next(
                value
                for value in reviewed["recipes"]
                if value["recipeId"] == TARGET_ID
            )
            self.assertEqual(design_hash(reviewed_target), design_hash(corpus.redesign))
            self.assertNotIn(TARGET_UID, reviewed["retiredRecipeUids"])
            self.assertEqual(acceptance, corpus.acceptance)
            self.assertEqual(len(history["entries"]), 1)
            event = history["entries"][0]
            self.assertEqual(
                event["originalDecision"]["note"],
                "The original rejection note must survive.",
            )
            self.assertEqual(event["originalRejectedCard"], corpus.target)
            self.assertEqual(event["redesignedPendingCard"], corpus.redesign)
            self.assertEqual(event["transition"], {"from": "rejected", "to": "pending"})
            self.assertTrue(report["invariants"]["neverAutoApproved"])
            self.assertTrue(report["designFingerprintChanged"])
            self.assertEqual(manifest["transactionId"], event["transactionId"])
            self.assertFalse(manifest["inputArtifacts"]["history"]["exists"])
            for artifact in manifest["outputArtifacts"].values():
                artifact_path = corpus.output_path / artifact["file"]
                self.assertEqual(file_sha256(artifact_path), artifact["sha256"])
                self.assertEqual(artifact_path.stat().st_size, artifact["size"])
            self.assertTrue((corpus.output_path / MANIFEST_FILENAME).is_file())
            with self.assertRaisesRegex(RequeueError, "already exists"):
                corpus.run()

    def test_comment_only_change_fails_closed_without_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = SyntheticCorpus(Path(temporary))
            unchanged = copy.deepcopy(corpus.target)
            unchanged["comment"] = "This metadata edit must not count as a redesign."
            corpus.redesign_path.write_bytes(encoded(unchanged))

            with self.assertRaisesRegex(RequeueError, "fingerprint is unchanged"):
                corpus.run()

            self.assertFalse(corpus.output_path.exists())

    def test_cross_archive_uid_collision_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = SyntheticCorpus(Path(temporary))
            collision = card(
                TARGET_UID,
                "test:different_recipe_same_uid",
                "test:different_output",
            )
            approved = read_json(corpus.paths["approved"])
            approved["recipes"].append(collision)
            corpus.paths["approved"].write_bytes(encoded(approved))

            with self.assertRaisesRegex(RequeueError, "UID collision across projects"):
                corpus.run()

            self.assertFalse(corpus.output_path.exists())

    def test_same_id_cannot_exist_in_two_status_archives(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = SyntheticCorpus(Path(temporary))
            approved = read_json(corpus.paths["approved"])
            approved["recipes"].append(copy.deepcopy(corpus.target))
            corpus.paths["approved"].write_bytes(encoded(approved))

            with self.assertRaisesRegex(RequeueError, "multiple archives"):
                corpus.run()

            self.assertFalse(corpus.output_path.exists())

    def test_identity_or_output_drift_fails_closed(self) -> None:
        cases = (
            ("uid", "different-uid", "changed recipe UID"),
            (
                "output",
                "test:different_machine_output",
                "changed the concrete recipe output identity",
            ),
        )
        for field, value, expected in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                corpus = SyntheticCorpus(Path(temporary))
                redesign = copy.deepcopy(corpus.redesign)
                if field == "uid":
                    redesign["uid"] = value
                else:
                    redesign["slots"]["output"]["id"] = value
                corpus.redesign_path.write_bytes(encoded(redesign))

                with self.assertRaisesRegex(RequeueError, expected):
                    corpus.run()

                self.assertFalse(corpus.output_path.exists())

    def test_absent_reviewed_target_is_inserted_and_unretired(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = SyntheticCorpus(
                Path(temporary), reviewed_contains_target=False
            )

            corpus.run()

            reviewed = read_json(
                corpus.output_path / OUTPUT_FILENAMES["reviewedManaged"]
            )
            self.assertIn(
                TARGET_ID, {value["recipeId"] for value in reviewed["recipes"]}
            )
            self.assertNotIn(TARGET_UID, reviewed["retiredRecipeUids"])
            self.assertIn("other-retired", reviewed["retiredRecipeUids"])
            report = read_json(corpus.output_path / REPORT_FILENAME)
            self.assertEqual(report["reviewedManagedAction"], "inserted")

    def test_selects_exact_target_from_full_redesign_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = SyntheticCorpus(Path(temporary))
            full_source = {
                "schema": 1,
                "project": "default",
                "recipes": [copy.deepcopy(corpus.approved), corpus.redesign],
                "removals": [],
                "retiredRecipeUids": [],
                "retiredRemovalUids": [],
            }
            corpus.redesign_path.write_bytes(encoded(full_source))

            corpus.run()

            default = read_json(corpus.output_path / OUTPUT_FILENAMES["default"])
            target = next(
                value for value in default["recipes"] if value["recipeId"] == TARGET_ID
            )
            self.assertEqual(design_hash(target), design_hash(corpus.redesign))

    def test_existing_append_only_history_is_retained(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = SyntheticCorpus(Path(temporary))
            prior_original = card(
                "uid-prior", "test:prior", "test:prior_output"
            )
            prior_redesign = card(
                "uid-prior",
                "test:prior",
                "test:prior_output",
                "minecraft:copper_ingot",
            )
            prior_decision = review(
                prior_original, "rejected", "manual", "Earlier rejection."
            )
            prior_original_hash = design_hash(prior_original)
            prior_redesign_hash = design_hash(prior_redesign)
            prior = {
                "transactionId": transaction_id(
                    "test:prior",
                    "uid-prior",
                    prior_original_hash,
                    prior_redesign_hash,
                    prior_decision,
                ),
                "recipeId": "test:prior",
                "uid": "uid-prior",
                "transition": {"from": "rejected", "to": "pending"},
                "originalDecision": prior_decision,
                "originalCardSha256": prior_original_hash,
                "redesignedCardSha256": prior_redesign_hash,
                "originalRejectedCard": prior_original,
                "redesignedPendingCard": prior_redesign,
            }
            corpus.history_path.write_bytes(encoded({
                "schemaVersion": 1,
                "project": "default",
                "entries": [prior],
            }))

            corpus.run()

            history = read_json(corpus.output_path / OUTPUT_FILENAMES["history"])
            self.assertEqual(history["entries"][0], prior)
            self.assertEqual(len(history["entries"]), 2)
            self.assertEqual(history["entries"][1]["recipeId"], TARGET_ID)

    def test_frozen_approved_target_cannot_be_requeued(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = SyntheticCorpus(
                Path(temporary), acceptance_target_status="approved"
            )

            with self.assertRaisesRegex(RequeueError, "records the target as Approved"):
                corpus.run()

            self.assertFalse(corpus.output_path.exists())


if __name__ == "__main__":
    unittest.main()
