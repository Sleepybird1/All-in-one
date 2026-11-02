from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid


TOOLS = Path(__file__).resolve().parent
PROJECT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import sanitize_kjsgen_orphans as sanitizer  # noqa: E402


LEDGER_PATH = PROJECT / "progression" / "kjsgen_orphan_retirement_ledger.json"
LIVE_PATH = (
    Path.home()
    / "curseforge"
    / "minecraft"
    / "Instances"
    / "All in one"
    / "kjsgen"
    / "projects"
    / "default.json"
)
BASELINE_PATH = (
    Path.home()
    / "curseforge"
    / "minecraft"
    / "Instances"
    / "All in one"
    / "kjsgen"
    / "industrial_colonies_sync"
    / "default.managed.baseline.json"
)
MANAGED_PATH = PROJECT / "pack-kjsgen" / "default.managed.json"


def fixture_uid(label: str) -> str:
    try:
        return str(uuid.UUID(label))
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"industrial-colonies-test:{label}"))


def recipe(uid: str, recipe_id: str | None = None) -> dict:
    value = {
        "uid": fixture_uid(uid),
        "type": "kjsgen:shaped",
        "slots": {
            "in0": {"kind": "ITEM", "id": "minecraft:iron_ingot"},
            "output": {"kind": "ITEM", "id": "minecraft:piston"},
        },
        "params": {},
    }
    if recipe_id is not None:
        value.update(
            {
                "recipeId": recipe_id,
                "replaceRecipe": False,
                "comment": "fixture",
            }
        )
    return value


def removal(uid: str) -> dict:
    return {
        "uid": fixture_uid(uid),
        "output": "minecraft:piston",
        "input": "minecraft:iron_ingot",
        "mod": "Minecraft",
        "recipeId": "minecraft:piston",
    }


def project(recipes: list[dict], removals: list[dict]) -> dict:
    return {
        "format": 1,
        "name": "fixture",
        "defaultTargetFile": "kjsgen_recipes.js",
        "futureMetadata": {"preserve": [1, 2, 3]},
        "recipes": recipes,
        "removals": removals,
    }


def entry(card: dict) -> dict:
    return {
        "uid": card["uid"],
        "canonicalSha256": sanitizer.canonical_sha256(card),
        "identity": {"fixture": True},
        "evidence": {"ownershipRule": "fixture"},
        "card": copy.deepcopy(card),
    }


def ledger(recipes: list[dict], removals: list[dict]) -> dict:
    return {
        "schema": sanitizer.SCHEMA,
        "canonicalization": "test",
        "expectedCounts": {"recipes": len(recipes), "removals": len(removals)},
        "recipes": [entry(card) for card in recipes],
        "removals": [entry(card) for card in removals],
    }


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class SanitizationPlanTests(unittest.TestCase):
    def test_exact_cards_are_deleted_and_unrelated_user_content_is_preserved(self) -> None:
        retired_recipe = recipe("retired-recipe", "industrial_colonies:old")
        retired_removal = removal("retired-removal")
        user_card = recipe("user-card")
        unrelated = recipe("unrelated", "some_pack:custom")
        staged = project(
            [user_card, retired_recipe, unrelated],
            [retired_removal, removal("unrelated-removal")],
        )

        cleaned, report = sanitizer.plan_sanitization(
            staged,
            project([], []),
            ledger([retired_recipe], [retired_removal]),
        )

        self.assertEqual([user_card, unrelated], cleaned["recipes"])
        self.assertEqual([removal("unrelated-removal")], cleaned["removals"])
        self.assertEqual(staged["futureMetadata"], cleaned["futureMetadata"])
        self.assertEqual(
            {"recipes": 1, "removals": 1}, report["retiredCounts"]
        )

    def test_edited_card_blocks_whole_plan(self) -> None:
        original = recipe("retired", "industrial_colonies:old")
        edited = copy.deepcopy(original)
        edited["slots"]["in0"]["id"] = "minecraft:diamond"
        staged = project([edited], [])

        with self.assertRaises(sanitizer.RetirementBlocked) as caught:
            sanitizer.plan_sanitization(
                staged, project([], []), ledger([original], [])
            )

        self.assertEqual("blocked", caught.exception.report["status"])
        self.assertIn("differs", caught.exception.report["conflicts"][0]["reason"])
        self.assertEqual("minecraft:diamond", staged["recipes"][0]["slots"]["in0"]["id"])

    def test_active_managed_overlap_blocks_when_staged_card_is_absent(self) -> None:
        original = recipe("active-again", "industrial_colonies:old")
        with self.assertRaises(sanitizer.RetirementBlocked) as caught:
            sanitizer.plan_sanitization(
                project([], []), project([original], []), ledger([original], [])
            )
        reasons = [item["reason"] for item in caught.exception.report["conflicts"]]
        self.assertIn("ledger UID overlaps the active managed fragment", reasons)

    def test_exact_active_reactivation_is_preserved_instead_of_retired(self) -> None:
        active = removal("active-again")
        staged = project([recipe("user")], [active])
        cleaned, report = sanitizer.plan_sanitization(
            staged,
            project([], [active]),
            ledger([], [active]),
        )
        self.assertEqual(staged, cleaned)
        self.assertEqual(
            {"recipes": 0, "removals": 0}, report["retiredCounts"]
        )
        self.assertEqual(
            {"recipes": 0, "removals": 1}, report["reactivatedCounts"]
        )

    def test_exact_active_recipe_reactivation_is_preserved_instead_of_retired(self) -> None:
        active = recipe("active-recipe", "industrial_colonies:active")
        staged = project([active, recipe("user")], [])
        cleaned, report = sanitizer.plan_sanitization(
            staged,
            project([active], []),
            ledger([active], []),
        )
        self.assertEqual(staged, cleaned)
        self.assertEqual(
            {"recipes": 0, "removals": 0}, report["retiredCounts"]
        )
        self.assertEqual(
            {"recipes": 1, "removals": 0}, report["reactivatedCounts"]
        )

    def test_missing_ledger_entries_are_idempotent(self) -> None:
        old_recipe = recipe("already-gone", "industrial_colonies:old")
        old_removal = removal("also-gone")
        staged = project([recipe("user")], [])
        cleaned, report = sanitizer.plan_sanitization(
            staged,
            project([], []),
            ledger([old_recipe], [old_removal]),
        )
        self.assertEqual(staged, cleaned)
        self.assertEqual(
            {"recipes": 0, "removals": 0}, report["retiredCounts"]
        )
        self.assertEqual(
            {"recipes": 1, "removals": 1}, report["alreadyAbsentCounts"]
        )

    def test_kind_mismatch_blocks(self) -> None:
        old_recipe = recipe("shared-uid", "industrial_colonies:old")
        wrong_kind = removal("shared-uid")
        with self.assertRaises(sanitizer.RetirementBlocked) as caught:
            sanitizer.plan_sanitization(
                project([], [wrong_kind]),
                project([], []),
                ledger([old_recipe], []),
            )
        self.assertTrue(
            any(
                item["reason"] == "ledger UID appears in the wrong staged array"
                for item in caught.exception.report["conflicts"]
            )
        )

    def test_uppercase_only_uid_edit_blocks_instead_of_appearing_absent(self) -> None:
        original = recipe("case-edited", "industrial_colonies:old")
        edited = copy.deepcopy(original)
        edited["uid"] = edited["uid"].upper()
        with self.assertRaises(sanitizer.RetirementBlocked) as caught:
            sanitizer.plan_sanitization(
                project([edited], []), project([], []), ledger([original], [])
            )
        self.assertTrue(
            any(
                item["reason"] == "staged card differs from the ledgered complete card"
                for item in caught.exception.report["conflicts"]
            )
        )

    def test_invalid_staged_uid_is_rejected(self) -> None:
        invalid = recipe("invalid")
        invalid["uid"] = "not-a-uuid"
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.plan_sanitization(
                project([invalid], []), project([], []), ledger([], [])
            )

    def test_differently_cased_duplicate_ledger_uid_blocks(self) -> None:
        original = recipe("case-duplicate", "industrial_colonies:old")
        duplicate = copy.deepcopy(original)
        duplicate["uid"] = duplicate["uid"].upper()
        with self.assertRaises(sanitizer.RetirementBlocked) as caught:
            sanitizer.plan_sanitization(
                project([original, duplicate], []),
                project([], []),
                ledger([original], []),
            )
        self.assertTrue(
            any(
                item["reason"] == "UID occurs more than once in the staged project"
                for item in caught.exception.report["conflicts"]
            )
        )

    def test_uppercase_active_managed_overlap_blocks(self) -> None:
        original = recipe("case-active", "industrial_colonies:old")
        active = copy.deepcopy(original)
        active["uid"] = active["uid"].upper()
        with self.assertRaises(sanitizer.RetirementBlocked) as caught:
            sanitizer.plan_sanitization(
                project([], []), project([active], []), ledger([original], [])
            )
        self.assertTrue(
            any(
                item["reason"] == "ledger UID overlaps the active managed fragment"
                for item in caught.exception.report["conflicts"]
            )
        )

    def test_unrelated_cross_kind_case_collision_blocks(self) -> None:
        shared = fixture_uid("unrelated-cross-kind")
        unrelated_recipe = recipe(shared, "example:recipe")
        unrelated_removal = removal(shared.upper())
        with self.assertRaises(sanitizer.RetirementBlocked) as caught:
            sanitizer.plan_sanitization(
                project([unrelated_recipe], [unrelated_removal]),
                project([], []),
                ledger([], []),
            )
        self.assertTrue(
            any(
                item["reason"] == "UID occurs more than once in the staged project"
                for item in caught.exception.report["conflicts"]
            )
        )

    def test_tampered_ledger_digest_is_rejected(self) -> None:
        old_recipe = recipe("old", "industrial_colonies:old")
        bad_ledger = ledger([old_recipe], [])
        bad_ledger["recipes"][0]["canonicalSha256"] = "0" * 64
        with self.assertRaises(sanitizer.SanitizationError):
            sanitizer.plan_sanitization(
                project([old_recipe], []), project([], []), bad_ledger
            )


class SanitizationCliTests(unittest.TestCase):
    def run_cli(
        self,
        root: Path,
        staged_value: dict,
        managed_value: dict,
        ledger_value: dict,
        extra_args: list[str] | None = None,
    ):
        staged_path = root / "staged.json"
        managed_path = root / "managed.json"
        ledger_path = root / "ledger.json"
        report_path = root / "audit.json"
        write_json(staged_path, staged_value)
        write_json(managed_path, managed_value)
        write_json(ledger_path, ledger_value)
        staged_bytes_before = staged_path.read_bytes()
        arguments = [
                sys.executable,
                str(TOOLS / "sanitize_kjsgen_orphans.py"),
                "--staged",
                str(staged_path),
                "--managed",
                str(managed_path),
                "--ledger",
                str(ledger_path),
                "--report",
                str(report_path),
            ]
        arguments.extend(extra_args or [])
        result = subprocess.run(
            arguments,
            text=True,
            capture_output=True,
            check=False,
        )
        return result, staged_path, report_path, staged_bytes_before

    def test_reviewed_ledger_flag_rejects_any_other_ledger_bytes(self) -> None:
        user = recipe("user")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result, staged_path, report_path, staged_bytes_before = self.run_cli(
                root,
                project([user], []),
                project([], []),
                ledger([], []),
                ["--require-reviewed-ledger"],
            )
            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertEqual(staged_bytes_before, staged_path.read_bytes())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("error", report["status"])
            self.assertIn("immutable reviewed ledger", report["error"])

    def test_edited_conflict_does_not_write_staged_file(self) -> None:
        original = recipe("old", "industrial_colonies:old")
        edited = copy.deepcopy(original)
        edited["params"]["loops"] = 999
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result, staged_path, report_path, staged_bytes_before = self.run_cli(
                root, project([edited], []), project([], []), ledger([original], [])
            )
            self.assertEqual(3, result.returncode, result.stdout + result.stderr)
            self.assertEqual(staged_bytes_before, staged_path.read_bytes())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("blocked", report["status"])
            self.assertFalse(report["writePerformed"])

    def test_second_in_place_run_is_byte_exact_noop(self) -> None:
        old = recipe("old", "industrial_colonies:old")
        user = recipe("user")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result, staged_path, report_path, _staged_bytes_before = self.run_cli(
                root, project([user, old], []), project([], []), ledger([old], [])
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            first_bytes = staged_path.read_bytes()
            result = subprocess.run(
                [
                    sys.executable,
                    str(TOOLS / "sanitize_kjsgen_orphans.py"),
                    "--staged",
                    str(staged_path),
                    "--managed",
                    str(root / "managed.json"),
                    "--ledger",
                    str(root / "ledger.json"),
                    "--report",
                    str(report_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(first_bytes, staged_path.read_bytes())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertFalse(report["writePerformed"])
            self.assertEqual(1, report["alreadyAbsentCounts"]["recipes"])

    def test_incomplete_active_overlap_cli_does_not_write_staged_file(self) -> None:
        active = recipe("active-again", "industrial_colonies:old")
        user = recipe("user")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result, staged_path, report_path, staged_bytes_before = self.run_cli(
                root,
                project([user], []),
                project([active], []),
                ledger([active], []),
            )
            self.assertEqual(3, result.returncode, result.stdout + result.stderr)
            self.assertEqual(staged_bytes_before, staged_path.read_bytes())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertFalse(report["writePerformed"])
            self.assertTrue(
                any("active managed" in item["reason"] for item in report["conflicts"])
            )


class SourceControlledLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))

    def test_ledger_has_exact_proven_counts_and_complete_card_hashes(self) -> None:
        self.assertEqual(
            sanitizer.REVIEWED_LEDGER_SHA256,
            hashlib.sha256(LEDGER_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(223, len(self.ledger["recipes"]))
        self.assertEqual(104, len(self.ledger["removals"]))
        self.assertEqual(
            {"recipes": 223, "removals": 104}, self.ledger["expectedCounts"]
        )
        all_uids: set[str] = set()
        for kind in ("recipes", "removals"):
            for value in self.ledger[kind]:
                self.assertNotIn(value["uid"], all_uids)
                all_uids.add(value["uid"])
                self.assertEqual(value["uid"], value["card"]["uid"])
                self.assertEqual(
                    sanitizer.canonical_sha256(value["card"]),
                    value["canonicalSha256"],
                )
                self.assertIn("ownershipRule", value["evidence"])
        self.assertTrue(
            all(
                value["card"]["recipeId"].startswith("industrial_colonies:")
                for value in self.ledger["recipes"]
            )
        )

    def test_seven_recipe_id_null_user_cards_are_outside_ledger(self) -> None:
        excluded = self.ledger["provenance"]["excludedUserRecipeCards"]
        self.assertEqual(7, excluded["count"])
        ledger_uids = {
            value["uid"]
            for kind in ("recipes", "removals")
            for value in self.ledger[kind]
        }
        self.assertTrue(set(excluded["uids"]).isdisjoint(ledger_uids))

    def test_current_live_evidence_matches_ledger_when_pack_is_available(self) -> None:
        if not (LIVE_PATH.is_file() and BASELINE_PATH.is_file() and MANAGED_PATH.is_file()):
            self.skipTest("the All in one live evidence set is not available")
        live_raw = LIVE_PATH.read_bytes()
        live = json.loads(live_raw.decode("utf-8-sig"))
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8-sig"))
        managed = json.loads(MANAGED_PATH.read_text(encoding="utf-8-sig"))
        live_by_kind = {
            kind: {value["uid"]: value for value in live[kind]}
            for kind in ("recipes", "removals")
        }
        baseline_locations: dict[str, list[tuple[str, dict]]] = {}
        for kind in ("recipes", "removals"):
            for card in baseline[kind]:
                baseline_locations.setdefault(card["uid"], []).append((kind, card))
        managed_locations: dict[str, list[tuple[str, dict]]] = {}
        for kind in ("recipes", "removals"):
            for card in managed[kind]:
                managed_locations.setdefault(card["uid"], []).append((kind, card))
        ledger_uids: set[str] = set()
        present_ledger_uids: set[str] = set()
        for kind in ("recipes", "removals"):
            for value in self.ledger[kind]:
                uid = value["uid"]
                ledger_uids.add(uid)
                # A transactional deployment may encounter the prior live
                # baseline before its exact ledger-proven orphans have been
                # retired. Any overlap is safe only when both the complete card
                # and its recipe/removal array still match the reviewed ledger.
                baseline_matches = baseline_locations.get(uid, [])
                if baseline_matches:
                    self.assertEqual(1, len(baseline_matches))
                    baseline_kind, baseline_card = baseline_matches[0]
                    self.assertEqual(kind, baseline_kind)
                    self.assertEqual(value["card"], baseline_card)
                # A card may subsequently be restored to the current managed
                # source; that is a safe reactivation only when its complete
                # card and array remain complete canonical-card matches.
                active_locations = managed_locations.get(uid, [])
                if active_locations:
                    self.assertEqual(1, len(active_locations))
                    active_kind, active_card = active_locations[0]
                    self.assertEqual(kind, active_kind)
                    self.assertEqual(value["card"], active_card)
                if uid in live_by_kind[kind]:
                    present_ledger_uids.add(uid)
                    self.assertEqual(value["card"], live_by_kind[kind][uid])
        excluded = self.ledger["provenance"]["excludedUserRecipeCards"]["uids"]
        for uid in excluded:
            self.assertNotIn(uid, ledger_uids)
            if uid in live_by_kind["recipes"]:
                self.assertIsNone(live_by_kind["recipes"][uid].get("recipeId"))

        # Against the immutable capture named in provenance, every ledger card
        # and all seven exclusions must be present.  After the one-time
        # migration, a different live hash is expected; any remaining card is
        # still required to be exact, while absent cards demonstrate
        # idempotence rather than test drift.
        captured_hash = self.ledger["provenance"]["liveProject"]["sha256"]
        if hashlib.sha256(live_raw).hexdigest() == captured_hash:
            self.assertEqual(327, len(present_ledger_uids))
            self.assertTrue(set(excluded).issubset(live_by_kind["recipes"]))


if __name__ == "__main__":
    unittest.main()
