#!/usr/bin/env python3
"""Read KJSGen's in-game recipe-review sidecar deterministically.

The Minecraft UI reviews the exact visual card that is currently on screen.
This tool compares that reviewed snapshot with the source-managed KJSGen card,
so a decision made against an older live card cannot silently approve a newer
recipe design.  It is intentionally read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 2
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
VALID_STATUSES = {"approved", "rejected", "pending", "deferred", "disabled"}
DESIGN_FIELDS = ("type", "recipeId", "slots", "params")


class FeedbackError(ValueError):
    """Raised when a sidecar or managed fragment is structurally invalid."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FeedbackError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise FeedbackError(f"invalid JSON in {path}: {exc}") from exc


def design_payload(card: dict[str, Any]) -> dict[str, Any]:
    """Return the exact semantic subset hashed by the in-game review UI."""

    return {field: card.get(field, {} if field in {"slots", "params"} else "")
            for field in DESIGN_FIELDS}


def design_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(
        design_payload(card),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _managed_by_id(document: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(document, dict) or not isinstance(document.get("recipes"), list):
        raise FeedbackError("managed fragment must contain a recipes array")
    result: dict[str, dict[str, Any]] = {}
    for index, card in enumerate(document["recipes"]):
        if not isinstance(card, dict):
            raise FeedbackError(f"managed recipes[{index}] must be an object")
        recipe_id = card.get("recipeId")
        if not isinstance(recipe_id, str) or not recipe_id:
            raise FeedbackError(f"managed recipes[{index}] has no recipeId")
        if recipe_id in result:
            raise FeedbackError(f"duplicate managed recipeId: {recipe_id}")
        result[recipe_id] = card
    return result


def _review_entries(document: Any) -> tuple[str, dict[str, dict[str, Any]]]:
    if not isinstance(document, dict):
        raise FeedbackError("review sidecar must be an object")
    if document.get("schemaVersion") not in {1, SCHEMA_VERSION}:
        raise FeedbackError(
            f"review sidecar schemaVersion must be 1 or {SCHEMA_VERSION}"
        )
    project = document.get("project")
    if not isinstance(project, str) or not project:
        raise FeedbackError("review sidecar project must be a non-empty string")
    reviews = document.get("reviews")
    if not isinstance(reviews, dict):
        raise FeedbackError("review sidecar reviews must be an object")

    validated: dict[str, dict[str, Any]] = {}
    for recipe_id, record in reviews.items():
        if not isinstance(recipe_id, str) or not recipe_id:
            raise FeedbackError("review keys must be non-empty recipe IDs")
        if not isinstance(record, dict):
            raise FeedbackError(f"review {recipe_id} must be an object")
        status = record.get("status")
        if status not in VALID_STATUSES:
            raise FeedbackError(
                f"review {recipe_id} has invalid status {status!r}"
            )
        for field in ("uid", "reason", "note", "cardSha256"):
            if not isinstance(record.get(field, ""), str):
                raise FeedbackError(f"review {recipe_id} field {field} must be text")
        digest = record.get("cardSha256", "")
        if not HASH_RE.fullmatch(digest):
            raise FeedbackError(f"review {recipe_id} has invalid cardSha256")
        validated[recipe_id] = record
    return project, validated


def build_report(
    review_document: Any,
    managed_document: Any,
) -> dict[str, Any]:
    project, reviews = _review_entries(review_document)
    managed = _managed_by_id(managed_document)
    rows: list[dict[str, Any]] = []
    counts = {
        "approved": 0,
        "rejected": 0,
        "pending": 0,
        "deferred": 0,
        "disabled": 0,
        "stale": 0,
        "unknown": 0,
    }

    for recipe_id in sorted(reviews):
        record = reviews[recipe_id]
        card = managed.get(recipe_id)
        expected = design_hash(card) if card is not None else None
        unknown = card is None
        stale = not unknown and record["cardSha256"] != expected
        effective = "pending" if unknown or stale else record["status"]
        if unknown:
            counts["unknown"] += 1
        elif stale:
            counts["stale"] += 1
        else:
            counts[effective] += 1
        rows.append({
            "recipeId": recipe_id,
            "uid": record.get("uid", ""),
            "recordedStatus": record["status"],
            "effectiveStatus": effective,
            "reason": record.get("reason", ""),
            "note": record.get("note", ""),
            "stale": stale,
            "unknown": unknown,
            "cardSha256": record["cardSha256"],
            "managedCardSha256": expected,
        })

    counts["unreviewed"] = max(0, len(managed) - len(set(managed) & set(reviews)))
    counts["managed"] = len(managed)
    counts["recorded"] = len(reviews)
    return {"schemaVersion": SCHEMA_VERSION, "project": project,
            "counts": counts, "reviews": rows}


def _print_table(report: dict[str, Any]) -> None:
    counts = report["counts"]
    print(
        "Recipe reviews: "
        f"{counts['approved']} approved, {counts['rejected']} rejected, "
        f"{counts['deferred']} deferred, {counts['disabled']} disabled, "
        f"{counts['stale']} stale, {counts['unknown']} unknown, "
        f"{counts['unreviewed']} unreviewed / {counts['managed']} managed"
    )
    for row in report["reviews"]:
        note = row["note"].replace("\r", " ").replace("\n", " ").strip()
        detail = f" [{row['reason']}]" if row["reason"] else ""
        if note:
            detail += f" — {note}"
        print(
            f"{row['effectiveStatus'].upper():8} {row['recipeId']}"
            f"{detail}"
            + (" (changed since review)" if row["stale"] else "")
            + (" (not in managed source)" if row["unknown"] else "")
        )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare in-game KJSGen review feedback with managed cards"
    )
    parser.add_argument("--reviews", type=Path, required=True,
                        help="default.recipe_reviews.json written by Minecraft")
    parser.add_argument(
        "--managed", type=Path,
        default=Path(__file__).resolve().parents[1] / "pack-kjsgen" / "default.managed.json",
        help="generated managed KJSGen fragment",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(_load_json(args.reviews), _load_json(args.managed))
    except FeedbackError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        _print_table(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
