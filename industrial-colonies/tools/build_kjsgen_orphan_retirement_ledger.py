#!/usr/bin/env python3
"""Build the one-time KJSGen orphan-retirement ownership ledger.

The builder is deliberately stricter than a normal cleanup script.  A live
recipe card is source-owned only when all of the following are true:

* its UID is absent from both the last deployed managed baseline and the
  current managed fragment;
* its recipe ID is in the ``industrial_colonies`` namespace; and
* its complete canonical JSON value exactly matches a card in a backed-up
  managed baseline.

Removal cards have no owner namespace, so they require the same complete-card
match in a backed-up managed baseline.  One removal predates the managed
sidecar; that UID and its complete value are pinned below and must be present,
unchanged, in every supplied historical project snapshot.  Nothing else may
use that exception.

The resulting ledger contains the complete card as well as its SHA-256.  This
lets the retirement sanitizer prove equality rather than trusting a UID alone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "industrial_colonies:kjsgen_orphan_retirement_ledger/v1"
EXPECTED_RECIPE_COUNT = 223
EXPECTED_REMOVAL_COUNT = 104

LEGACY_PRE_SIDECAR_REMOVAL = {
    "uid": "3c59e41a-4be2-40c1-9f18-c31cc13a6483",
    "output": "ae2:printed_silicon",
    "input": "ae2:silicon",
    "mod": "Applied Energistics",
    "recipeId": "",
}


class EvidenceError(RuntimeError):
    """Raised when the evidence is insufficient or internally inconsistent."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"cannot read JSON evidence {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvidenceError(f"JSON evidence {path} is not an object")
    return value


def cards(document: dict[str, Any], kind: str, source: Path) -> list[dict[str, Any]]:
    value = document.get(kind)
    if not isinstance(value, list):
        raise EvidenceError(f"{source} has no {kind!r} array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, card in enumerate(value):
        if not isinstance(card, dict):
            raise EvidenceError(f"{source} {kind}[{index}] is not an object")
        uid = card.get("uid")
        if not isinstance(uid, str) or not uid:
            raise EvidenceError(f"{source} {kind}[{index}] has no non-empty UID")
        if uid in seen:
            raise EvidenceError(f"{source} repeats {kind} UID {uid}")
        seen.add(uid)
        result.append(card)
    return result


def artifact_record(path: Path, label: str, document: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": label,
        "sha256": file_sha256(path),
        "recipeCount": len(cards(document, "recipes", path)),
        "removalCount": len(cards(document, "removals", path)),
    }


def evidence_ref(
    label: str,
    path: Path,
    index: int,
    kind: str,
) -> dict[str, Any]:
    return {
        "artifact": label,
        "artifactSha256": file_sha256(path),
        "array": kind,
        "index": index,
    }


def output_identity(card: dict[str, Any]) -> list[str]:
    slots = card.get("slots")
    if not isinstance(slots, dict):
        return []
    values: set[str] = set()
    for key, slot in slots.items():
        if not str(key).startswith("output") or not isinstance(slot, dict):
            continue
        identifier = slot.get("id")
        if isinstance(identifier, str) and identifier:
            values.add(identifier)
    return sorted(values)


def recipe_identity(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "recipeId": card.get("recipeId"),
        "type": card.get("type"),
        "outputs": output_identity(card),
        "comment": card.get("comment"),
    }


def removal_identity(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "recipeId": card.get("recipeId"),
        "output": card.get("output"),
        "input": card.get("input"),
        "mod": card.get("mod"),
    }


def indexed_history(
    artifacts: Iterable[tuple[str, Path, dict[str, Any]]],
    kind: str,
) -> dict[str, list[tuple[str, Path, int, dict[str, Any]]]]:
    result: dict[str, list[tuple[str, Path, int, dict[str, Any]]]] = {}
    for label, path, document in artifacts:
        for index, card in enumerate(cards(document, kind, path)):
            result.setdefault(card["uid"], []).append((label, path, index, card))
    return result


def managed_evidence(
    card: dict[str, Any],
    history: dict[str, list[tuple[str, Path, int, dict[str, Any]]]],
    kind: str,
) -> dict[str, Any] | None:
    exact = [
        entry
        for entry in history.get(card["uid"], [])
        if canonical_bytes(entry[3]) == canonical_bytes(card)
    ]
    if not exact:
        return None
    first = exact[0]
    last = exact[-1]
    evidence: dict[str, Any] = {
        "ownershipRule": "exact_full_card_match_in_historical_managed_baseline",
        "exactMatchCount": len(exact),
        "firstExactMatch": evidence_ref(first[0], first[1], first[2], kind),
    }
    if last[:3] != first[:3]:
        evidence["lastExactMatch"] = evidence_ref(last[0], last[1], last[2], kind)
    return evidence


def ledger_entry(
    card: dict[str, Any],
    identity: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "uid": card["uid"],
        "canonicalSha256": canonical_sha256(card),
        "identity": identity,
        "evidence": evidence,
        "card": card,
    }


def project_history_files(history_root: Path) -> list[Path]:
    return sorted(
        history_root.glob(
            "deployment-*/overwritten/kjsgen/projects/default.json"
        ),
        key=lambda path: path.as_posix(),
    )


def managed_history_files(history_root: Path) -> list[Path]:
    return sorted(
        history_root.glob(
            "deployment-*/overwritten/kjsgen/industrial_colonies_sync/"
            "default.managed.baseline.json"
        ),
        key=lambda path: path.as_posix(),
    )


def build_ledger(
    live_path: Path,
    baseline_path: Path,
    managed_path: Path,
    history_root: Path,
) -> dict[str, Any]:
    live = read_json(live_path)
    baseline = read_json(baseline_path)
    managed = read_json(managed_path)

    historical_paths = managed_history_files(history_root)
    if not historical_paths:
        raise EvidenceError(f"no historical managed baselines found below {history_root}")
    historical_artifacts: list[tuple[str, Path, dict[str, Any]]] = []
    for path in historical_paths:
        label = path.relative_to(history_root).as_posix()
        historical_artifacts.append((label, path, read_json(path)))

    active_recipe_uids = {
        card["uid"]
        for document, source in ((baseline, baseline_path), (managed, managed_path))
        for card in cards(document, "recipes", source)
    }
    active_removal_uids = {
        card["uid"]
        for document, source in ((baseline, baseline_path), (managed, managed_path))
        for card in cards(document, "removals", source)
    }

    recipe_history = indexed_history(historical_artifacts, "recipes")
    removal_history = indexed_history(historical_artifacts, "removals")

    recipe_entries: list[dict[str, Any]] = []
    excluded_user_uids: list[str] = []
    unexpected_recipe_orphans: list[str] = []
    for card in cards(live, "recipes", live_path):
        if card["uid"] in active_recipe_uids:
            continue
        recipe_id = card.get("recipeId")
        if recipe_id is None:
            excluded_user_uids.append(card["uid"])
            continue
        if not isinstance(recipe_id, str) or not recipe_id.startswith(
            "industrial_colonies:"
        ):
            unexpected_recipe_orphans.append(
                f"{card['uid']} ({recipe_id!r}: not source namespace)"
            )
            continue
        evidence = managed_evidence(card, recipe_history, "recipes")
        if evidence is None:
            unexpected_recipe_orphans.append(
                f"{card['uid']} ({recipe_id}: no exact managed-baseline match)"
            )
            continue
        recipe_entries.append(ledger_entry(card, recipe_identity(card), evidence))

    if unexpected_recipe_orphans:
        raise EvidenceError(
            "unowned non-user recipe orphan(s): " + "; ".join(unexpected_recipe_orphans)
        )

    removal_entries: list[dict[str, Any]] = []
    unexpected_removal_orphans: list[str] = []

    project_paths = project_history_files(history_root)
    legacy_matches: list[tuple[str, Path, int]] = []
    if project_paths:
        for path in project_paths:
            document = read_json(path)
            label = path.relative_to(history_root).as_posix()
            matching = [
                (index, card)
                for index, card in enumerate(cards(document, "removals", path))
                if card.get("uid") == LEGACY_PRE_SIDECAR_REMOVAL["uid"]
            ]
            if len(matching) != 1 or canonical_bytes(matching[0][1]) != canonical_bytes(
                LEGACY_PRE_SIDECAR_REMOVAL
            ):
                raise EvidenceError(
                    "the pinned pre-sidecar removal is absent or edited in " + label
                )
            legacy_matches.append((label, path, matching[0][0]))

    for card in cards(live, "removals", live_path):
        if card["uid"] in active_removal_uids:
            continue
        evidence = managed_evidence(card, removal_history, "removals")
        if evidence is None and card["uid"] == LEGACY_PRE_SIDECAR_REMOVAL["uid"]:
            if canonical_bytes(card) != canonical_bytes(LEGACY_PRE_SIDECAR_REMOVAL):
                unexpected_removal_orphans.append(
                    f"{card['uid']} (pinned pre-sidecar value was edited)"
                )
                continue
            if not legacy_matches:
                unexpected_removal_orphans.append(
                    f"{card['uid']} (no historical project continuity evidence)"
                )
                continue
            first = legacy_matches[0]
            last = legacy_matches[-1]
            evidence = {
                "ownershipRule": "pinned_legacy_pre_sidecar_source_removal",
                "exactMatchCount": len(legacy_matches),
                "firstExactMatch": evidence_ref(
                    first[0], first[1], first[2], "removals"
                ),
                "lastExactMatch": evidence_ref(
                    last[0], last[1], last[2], "removals"
                ),
                "note": (
                    "This exact removal predates the managed-baseline sidecar and "
                    "is the sole explicitly pinned legacy exception."
                ),
            }
        if evidence is None:
            unexpected_removal_orphans.append(
                f"{card['uid']} ({card.get('recipeId')!r}: no ownership evidence)"
            )
            continue
        removal_entries.append(ledger_entry(card, removal_identity(card), evidence))

    if unexpected_removal_orphans:
        raise EvidenceError(
            "unowned removal orphan(s): " + "; ".join(unexpected_removal_orphans)
        )

    recipe_entries.sort(key=lambda entry: entry["uid"])
    removal_entries.sort(key=lambda entry: entry["uid"])
    excluded_user_uids.sort()

    if len(recipe_entries) != EXPECTED_RECIPE_COUNT:
        raise EvidenceError(
            f"recipe retirement count is {len(recipe_entries)}, expected "
            f"{EXPECTED_RECIPE_COUNT}"
        )
    if len(removal_entries) != EXPECTED_REMOVAL_COUNT:
        raise EvidenceError(
            f"removal retirement count is {len(removal_entries)}, expected "
            f"{EXPECTED_REMOVAL_COUNT}"
        )
    if len(excluded_user_uids) != 7:
        raise EvidenceError(
            f"excluded recipeId-null user-card count is {len(excluded_user_uids)}, expected 7"
        )

    history_index = [
        artifact_record(path, label, document)
        for label, path, document in historical_artifacts
    ]

    return {
        "schema": SCHEMA,
        "canonicalization": (
            "UTF-8 JSON; object keys sorted lexicographically; compact separators; "
            "array order and scalar types preserved; NaN forbidden"
        ),
        "policy": {
            "recipeOwnership": (
                "inactive UID + industrial_colonies recipeId + exact complete-card "
                "match in a historical managed baseline"
            ),
            "removalOwnership": (
                "inactive UID + exact complete-card match in a historical managed "
                "baseline; one value-pinned pre-sidecar exception"
            ),
            "retirementGuard": (
                "the sanitizer must reject active-UID overlap or any complete-card drift"
            ),
        },
        "expectedCounts": {
            "recipes": EXPECTED_RECIPE_COUNT,
            "removals": EXPECTED_REMOVAL_COUNT,
        },
        "provenance": {
            "liveProject": artifact_record(live_path, "live-project-snapshot", live),
            "deployedManagedBaseline": artifact_record(
                baseline_path, "deployed-managed-baseline", baseline
            ),
            "currentManagedSource": artifact_record(
                managed_path, "current-managed-source", managed
            ),
            "historicalManagedBaselines": history_index,
            "excludedUserRecipeCards": {
                "reason": "recipeId is null and no managed ownership evidence exists",
                "count": len(excluded_user_uids),
                "uids": excluded_user_uids,
            },
        },
        "recipes": recipe_entries,
        "removals": removal_entries,
    }


def rendered(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--managed", required=True, type=Path)
    parser.add_argument("--history-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        ledger = build_ledger(
            args.live.resolve(),
            args.baseline.resolve(),
            args.managed.resolve(),
            args.history_root.resolve(),
        )
        expected = rendered(ledger)
        output = args.output.resolve()
        if args.check:
            if not output.is_file() or output.read_bytes() != expected:
                raise EvidenceError(f"retirement ledger is stale: {output}")
            print(
                f"KJSGen orphan-retirement ledger is current: "
                f"{len(ledger['recipes'])} recipes, {len(ledger['removals'])} removals"
            )
            return 0
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(expected)
        print(
            f"Wrote {output}: {len(ledger['recipes'])} recipes, "
            f"{len(ledger['removals'])} removals"
        )
        return 0
    except EvidenceError as error:
        print(f"ERROR: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
