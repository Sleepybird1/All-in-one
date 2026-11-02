#!/usr/bin/env python3
"""Retire only ledger-proven orphan cards from a staged KJSGen project.

This is an intentionally one-time, fail-closed migration.  UID membership is
not enough: a staged card is removed only when its complete canonical JSON
value exactly equals the value stored in the source-controlled ledger. A UID
that later becomes active again is preserved only when the ledger, active
managed card, and staged card are all complete canonical matches. Any edited
value, kind mismatch, duplicate, malformed ledger, or ambiguous active overlap
blocks the whole operation before the staged/output file is written.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any
import uuid


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = PROJECT / "progression" / "kjsgen_orphan_retirement_ledger.json"
SCHEMA = "industrial_colonies:kjsgen_orphan_retirement_ledger/v1"
REVIEWED_LEDGER_SHA256 = (
    "caedd22259e9ca1fa7a77b8b018a809721e55ca2cd7ff8a92bdb15a70c52a66e"
)


class SanitizationError(RuntimeError):
    """A malformed input prevented a safe retirement plan."""


class RetirementBlocked(RuntimeError):
    """A semantic conflict blocked the migration without changing its target."""

    def __init__(self, report: dict[str, Any]):
        super().__init__("KJSGen orphan retirement was blocked")
        self.report = report


def normalized_uid(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SanitizationError(f"{label} has no non-empty string UID")
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError) as error:
        raise SanitizationError(f"{label} UID is not a UUID: {value!r}") from error


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise SanitizationError(f"value is not canonical JSON: {error}") from error


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def bytes_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise SanitizationError(f"{label} is not valid UTF-8 JSON: {error}") from error
    if not isinstance(value, dict):
        raise SanitizationError(f"{label} root must be an object")
    return value


def read_json_path(path: Path, label: str) -> tuple[bytes, dict[str, Any]]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise SanitizationError(f"cannot read {label} {path}: {error}") from error
    return raw, parse_json_bytes(raw, label)


def card_array(document: dict[str, Any], kind: str, label: str) -> list[dict[str, Any]]:
    value = document.get(kind)
    if not isinstance(value, list):
        raise SanitizationError(f"{label} has no {kind!r} array")
    result: list[dict[str, Any]] = []
    for index, card in enumerate(value):
        if not isinstance(card, dict):
            raise SanitizationError(f"{label} {kind}[{index}] is not an object")
        normalized_uid(card.get("uid"), f"{label} {kind}[{index}]")
        result.append(card)
    return result


def uid_locations(
    document: dict[str, Any], label: str
) -> dict[str, list[tuple[str, int, dict[str, Any]]]]:
    result: dict[str, list[tuple[str, int, dict[str, Any]]]] = {}
    for kind in ("recipes", "removals"):
        for index, card in enumerate(card_array(document, kind, label)):
            uid = normalized_uid(card.get("uid"), f"{label} {kind}[{index}]")
            result.setdefault(uid, []).append((kind, index, card))
    return result


def validate_ledger(
    ledger: dict[str, Any], label: str
) -> tuple[dict[str, dict[str, dict[str, Any]]], set[str]]:
    if ledger.get("schema") != SCHEMA:
        raise SanitizationError(
            f"{label} schema must be {SCHEMA!r}, got {ledger.get('schema')!r}"
        )
    expected = ledger.get("expectedCounts")
    if not isinstance(expected, dict):
        raise SanitizationError(f"{label} has no expectedCounts object")

    by_kind: dict[str, dict[str, dict[str, Any]]] = {
        "recipes": {},
        "removals": {},
    }
    all_uids: set[str] = set()
    for kind in ("recipes", "removals"):
        entries = ledger.get(kind)
        if not isinstance(entries, list):
            raise SanitizationError(f"{label} has no {kind!r} ledger array")
        if expected.get(kind) != len(entries):
            raise SanitizationError(
                f"{label} {kind} count {len(entries)} does not match "
                f"expectedCounts {expected.get(kind)!r}"
            )
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise SanitizationError(f"{label} {kind}[{index}] is not an object")
            uid_value = entry.get("uid")
            card = entry.get("card")
            digest = entry.get("canonicalSha256")
            uid = normalized_uid(uid_value, f"{label} {kind}[{index}]")
            if uid in all_uids:
                raise SanitizationError(f"{label} repeats ledger UID {uid}")
            if not isinstance(card, dict) or normalized_uid(
                card.get("uid"), f"{label} {kind}[{index}] card"
            ) != uid:
                raise SanitizationError(
                    f"{label} {kind}[{index}] card UID does not equal {uid_value}"
                )
            actual_digest = canonical_sha256(card)
            if digest != actual_digest:
                raise SanitizationError(
                    f"{label} {kind}[{index}] canonical SHA-256 mismatch for {uid}: "
                    f"stored {digest!r}, actual {actual_digest}"
                )
            by_kind[kind][uid] = entry
            all_uids.add(uid)
    return by_kind, all_uids


def basic_report(
    staged_raw: bytes,
    managed_raw: bytes,
    ledger_raw: bytes,
    ledger: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "industrial_colonies:kjsgen_orphan_retirement_audit/v1",
        "status": "planning",
        "inputs": {
            "stagedSha256": bytes_sha256(staged_raw),
            "managedSha256": bytes_sha256(managed_raw),
            "ledgerSha256": bytes_sha256(ledger_raw),
        },
        "ledgerCounts": {
            "recipes": len(ledger.get("recipes", [])),
            "removals": len(ledger.get("removals", [])),
        },
        "retired": {"recipes": [], "removals": []},
        "alreadyAbsent": {"recipes": [], "removals": []},
        "reactivated": {"recipes": [], "removals": []},
        "conflicts": [],
    }


def plan_sanitization(
    staged: dict[str, Any],
    managed: dict[str, Any],
    ledger: dict[str, Any],
    *,
    staged_raw: bytes | None = None,
    managed_raw: bytes | None = None,
    ledger_raw: bytes | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a cleaned copy and audit, or raise ``RetirementBlocked``.

    This function performs no filesystem writes and is the core test seam.
    """

    staged_raw = staged_raw if staged_raw is not None else canonical_bytes(staged)
    managed_raw = managed_raw if managed_raw is not None else canonical_bytes(managed)
    ledger_raw = ledger_raw if ledger_raw is not None else canonical_bytes(ledger)
    ledger_by_kind, ledger_uids = validate_ledger(ledger, "retirement ledger")
    staged_locations = uid_locations(staged, "staged project")
    managed_locations = uid_locations(managed, "current managed project")
    report = basic_report(staged_raw, managed_raw, ledger_raw, ledger)
    report["stagedCountsBefore"] = {
        "recipes": len(staged["recipes"]),
        "removals": len(staged["removals"]),
    }
    report["managedCounts"] = {
        "recipes": len(managed["recipes"]),
        "removals": len(managed["removals"]),
    }

    reactivated_uids: set[str] = set()
    for uid in sorted(ledger_uids.intersection(managed_locations)):
        ledger_kind = next(
            kind for kind in ("recipes", "removals") if uid in ledger_by_kind[kind]
        )
        expected_card = ledger_by_kind[ledger_kind][uid]["card"]
        active_locations = managed_locations[uid]
        staged_matches = staged_locations.get(uid, [])
        exact_reactivation = (
            len(active_locations) == 1
            and active_locations[0][0] == ledger_kind
            and canonical_bytes(active_locations[0][2]) == canonical_bytes(expected_card)
            and len(staged_matches) == 1
            and staged_matches[0][0] == ledger_kind
            and canonical_bytes(staged_matches[0][2]) == canonical_bytes(expected_card)
        )
        if exact_reactivation:
            reactivated_uids.add(uid)
            report["reactivated"][ledger_kind].append(uid)
            continue
        report["conflicts"].append(
            {
                "uid": uid,
                "reason": "ledger UID overlaps the active managed fragment",
                "managedLocations": [
                    {"array": kind, "index": index}
                    for kind, index, _card in active_locations
                ],
                "stagedLocations": [
                    {"array": kind, "index": index}
                    for kind, index, _card in staged_matches
                ],
                "requiredResolution": (
                    "reactivation is allowed only when ledger, active managed, "
                    "and staged complete cards are identical in the same array"
                ),
            }
        )

    for uid, locations in sorted(staged_locations.items()):
        if len(locations) != 1:
            report["conflicts"].append(
                {
                    "uid": uid,
                    "reason": "UID occurs more than once in the staged project",
                    "stagedLocations": [
                        {"array": kind, "index": index}
                        for kind, index, _card in locations
                    ],
                }
            )

    for uid, locations in sorted(managed_locations.items()):
        if len(locations) != 1:
            report["conflicts"].append(
                {
                    "uid": uid,
                    "reason": "UID occurs more than once in the active managed project",
                    "managedLocations": [
                        {"array": kind, "index": index}
                        for kind, index, _card in locations
                    ],
                }
            )

    retire_uids: dict[str, set[str]] = {"recipes": set(), "removals": set()}
    for kind in ("recipes", "removals"):
        for uid, entry in sorted(ledger_by_kind[kind].items()):
            if uid in reactivated_uids:
                continue
            locations = staged_locations.get(uid, [])
            if not locations:
                report["alreadyAbsent"][kind].append(uid)
                continue
            if len(locations) != 1:
                continue
            staged_kind, index, staged_card = locations[0]
            if staged_kind != kind:
                report["conflicts"].append(
                    {
                        "uid": uid,
                        "reason": "ledger UID appears in the wrong staged array",
                        "expectedArray": kind,
                        "actualArray": staged_kind,
                        "index": index,
                    }
                )
                continue
            expected_card = entry["card"]
            if canonical_bytes(staged_card) != canonical_bytes(expected_card):
                report["conflicts"].append(
                    {
                        "uid": uid,
                        "reason": "staged card differs from the ledgered complete card",
                        "array": kind,
                        "index": index,
                        "expectedCanonicalSha256": entry["canonicalSha256"],
                        "actualCanonicalSha256": canonical_sha256(staged_card),
                    }
                )
                continue
            retire_uids[kind].add(uid)

    if report["conflicts"]:
        report["status"] = "blocked"
        report["writePerformed"] = False
        report["stagedSha256After"] = report["inputs"]["stagedSha256"]
        raise RetirementBlocked(report)

    cleaned = copy.deepcopy(staged)
    for kind in ("recipes", "removals"):
        cleaned[kind] = [
            card
            for index, card in enumerate(cleaned[kind])
            if normalized_uid(
                card.get("uid"), f"cleaned staged project {kind}[{index}]"
            ) not in retire_uids[kind]
        ]
        report["retired"][kind] = sorted(retire_uids[kind])
        report["alreadyAbsent"][kind].sort()
        report["reactivated"][kind].sort()

    report["status"] = "clean"
    report["stagedCountsAfter"] = {
        "recipes": len(cleaned["recipes"]),
        "removals": len(cleaned["removals"]),
    }
    report["retiredCounts"] = {
        "recipes": len(report["retired"]["recipes"]),
        "removals": len(report["retired"]["removals"]),
    }
    report["alreadyAbsentCounts"] = {
        "recipes": len(report["alreadyAbsent"]["recipes"]),
        "removals": len(report["alreadyAbsent"]["removals"]),
    }
    report["reactivatedCounts"] = {
        "recipes": len(report["reactivated"]["recipes"]),
        "removals": len(report["reactivated"]["removals"]),
    }
    return cleaned, report


def json_output_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def report_bytes(report: dict[str, Any]) -> bytes:
    return json_output_bytes(report)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", required=True, type=Path)
    parser.add_argument("--managed", required=True, type=Path)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument(
        "--require-reviewed-ledger",
        action="store_true",
        help="fail unless --ledger is the immutable source-reviewed migration ledger",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output project; defaults to an atomic in-place update of --staged",
    )
    parser.add_argument("--report", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    staged_path = args.staged.resolve()
    managed_path = args.managed.resolve()
    ledger_path = args.ledger.resolve()
    output_path = args.output.resolve() if args.output else staged_path
    report_path = args.report.resolve()

    if report_path in {staged_path, output_path, managed_path, ledger_path}:
        print("ERROR: --report must not overwrite an input or output JSON file")
        return 2
    if output_path in {managed_path, ledger_path}:
        print("ERROR: --output must not overwrite the managed fragment or ledger")
        return 2

    try:
        staged_raw, staged = read_json_path(staged_path, "staged project")
        managed_raw, managed = read_json_path(managed_path, "current managed project")
        ledger_raw, ledger = read_json_path(ledger_path, "retirement ledger")
        if args.require_reviewed_ledger:
            actual_ledger_sha256 = bytes_sha256(ledger_raw)
            if actual_ledger_sha256 != REVIEWED_LEDGER_SHA256:
                raise SanitizationError(
                    "retirement ledger is not the immutable reviewed ledger: "
                    f"expected SHA-256 {REVIEWED_LEDGER_SHA256}, "
                    f"found {actual_ledger_sha256}"
                )
        try:
            cleaned, report = plan_sanitization(
                staged,
                managed,
                ledger,
                staged_raw=staged_raw,
                managed_raw=managed_raw,
                ledger_raw=ledger_raw,
            )
        except RetirementBlocked as blocked:
            atomic_write(report_path, report_bytes(blocked.report))
            print(
                f"BLOCKED: {len(blocked.report['conflicts'])} KJSGen orphan "
                f"retirement conflict(s); staged project was not written"
            )
            return 3

        retired_total = sum(report["retiredCounts"].values())
        if retired_total:
            output_raw = json_output_bytes(cleaned)
            atomic_write(output_path, output_raw)
            report["writePerformed"] = True
        elif output_path == staged_path:
            output_raw = staged_raw
            report["writePerformed"] = False
        else:
            # An idempotent copy to a distinct requested output remains byte-exact.
            output_raw = staged_raw
            atomic_write(output_path, output_raw)
            report["writePerformed"] = True
        report["stagedSha256After"] = bytes_sha256(output_raw)
        atomic_write(report_path, report_bytes(report))
        print(
            f"KJSGen orphan retirement clean: removed "
            f"{report['retiredCounts']['recipes']} recipes and "
            f"{report['retiredCounts']['removals']} removals; "
            f"{sum(report['alreadyAbsentCounts'].values())} ledger entries already absent; "
            f"{sum(report['reactivatedCounts'].values())} exact cards active again"
        )
        return 0
    except SanitizationError as error:
        failure = {
            "schema": "industrial_colonies:kjsgen_orphan_retirement_audit/v1",
            "status": "error",
            "writePerformed": False,
            "error": str(error),
        }
        try:
            atomic_write(report_path, report_bytes(failure))
        except OSError:
            pass
        print(f"ERROR: {error}")
        return 2
    except OSError as error:
        print(f"ERROR: filesystem operation failed: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
