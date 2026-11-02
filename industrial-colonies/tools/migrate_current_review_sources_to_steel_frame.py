#!/usr/bin/env python3
"""Canonicalize current review sources from Mekanism casing to TFMG frame.

This policy migration is intentionally narrower than a text replacement:

* only exact scalar values in recipe input slots and params are rewritten;
* recipe identity, output slots, comments, removals, and review classifications
  are preserved;
* the managed Mekanism steel-casing producer is retired, while the exact stock
  recipe removal remains owned by the reviewed managed source; and
* the rejected producer snapshot remains in the non-historical acceptance as
  review evidence, but cannot become a managed recipe by replaying acceptance.

The immutable ``progression/review-batches`` and orphan-retirement history are
outside this tool's inputs by design.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any, Iterable

try:
    from tools.migrate_kjsgen_steel_frame import (
        MigrationError,
        NEW_ID,
        OLD_ID,
        PINNED_PRODUCER_HASH,
        PINNED_PRODUCER_RECIPE_ID,
        PINNED_PRODUCER_UID,
        design_hash,
        exact_occurrences,
        is_output_slot,
        transform_card,
        validate_card,
    )
except ModuleNotFoundError:  # Direct execution from the tools directory.
    from migrate_kjsgen_steel_frame import (  # type: ignore
        MigrationError,
        NEW_ID,
        OLD_ID,
        PINNED_PRODUCER_HASH,
        PINNED_PRODUCER_RECIPE_ID,
        PINNED_PRODUCER_UID,
        design_hash,
        exact_occurrences,
        is_output_slot,
        transform_card,
        validate_card,
    )


ACCEPTANCE_PRODUCER_HASH = (
    "sha256:203cf5535ea74d3e591a43de70a3c72c7817a528ac235b21228d7ce2b1b2c7f4"
)
VALID_ACCEPTANCE_STATUSES = {"approved", "rejected"}

# These pins describe the current durable sources.  They make the repository
# migration fail closed if a partial or unrelated review corpus is supplied.
EXPECTED_REVIEWED_CONSUMERS = 29
EXPECTED_REVIEWED_REFERENCES = 54
EXPECTED_ACCEPTANCE_CONSUMERS = 48
EXPECTED_ACCEPTANCE_REFERENCES = 87
EXPECTED_ACCEPTANCE_STATUS_COUNTS = {"approved": 141, "rejected": 240}
EXPECTED_AFFECTED_ACCEPTANCE_STATUS_COUNTS = {"approved": 6, "rejected": 42}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise MigrationError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise MigrationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MigrationError(f"{path} must contain a JSON object")
    return value


def encoded(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def atomic_write(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = encoded(document)
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as temporary:
        temporary.write(payload)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def _eligible_old_references(card: dict[str, Any]) -> int:
    return sum(
        exact_occurrences(slot, OLD_ID)
        for slot_name, slot in card["slots"].items()
        if not is_output_slot(str(slot_name))
    ) + exact_occurrences(card["params"], OLD_ID)


def _old_output_references(card: dict[str, Any]) -> int:
    return sum(
        exact_occurrences(slot, OLD_ID)
        for slot_name, slot in card["slots"].items()
        if is_output_slot(str(slot_name))
    )


def _validate_unique_cards(cards: list[Any], label: str) -> list[dict[str, Any]]:
    validated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_uids: set[str] = set()
    for index, raw in enumerate(cards):
        card = validate_card(raw, f"{label}[{index}]")
        if card["recipeId"] in seen_ids:
            raise MigrationError(f"{label} repeats recipe ID {card['recipeId']}")
        if card["uid"] in seen_uids:
            raise MigrationError(f"{label} repeats recipe UID {card['uid']}")
        seen_ids.add(card["recipeId"])
        seen_uids.add(card["uid"])
        validated.append(card)
    return validated


def transform_reviewed_managed(
    source: dict[str, Any], *, enforce_repository_counts: bool = False
) -> tuple[dict[str, Any], dict[str, int]]:
    """Rewrite current managed consumers and retire its redundant producer."""

    if source.get("schema") != 1 or source.get("project") != "default":
        raise MigrationError("reviewed managed source must be schema 1 project default")
    recipes = source.get("recipes")
    removals = source.get("removals")
    retired_uids = source.get("retiredRecipeUids")
    if not isinstance(recipes, list) or not isinstance(removals, list):
        raise MigrationError("reviewed managed source needs recipes and removals arrays")
    if not isinstance(retired_uids, list) or not all(
        isinstance(uid, str) and uid for uid in retired_uids
    ):
        raise MigrationError("reviewed managed source needs a retiredRecipeUids array")
    if len(retired_uids) != len(set(retired_uids)):
        raise MigrationError("reviewed managed source repeats a retired recipe UID")

    stock_removal_count = sum(
        isinstance(removal, dict) and removal.get("recipeId") == OLD_ID
        for removal in removals
    )
    if stock_removal_count != 1:
        raise MigrationError(
            f"reviewed managed source must preserve exactly one {OLD_ID} stock removal"
        )

    cards = _validate_unique_cards(recipes, "reviewed.recipes")
    producer_cards = [
        card for card in cards if card["recipeId"] == PINNED_PRODUCER_RECIPE_ID
    ]
    if len(producer_cards) > 1:
        raise MigrationError("reviewed managed source repeats the retired producer")
    if producer_cards:
        producer = producer_cards[0]
        if producer["uid"] != PINNED_PRODUCER_UID:
            raise MigrationError("reviewed producer UID drifted")
        if design_hash(producer) != PINNED_PRODUCER_HASH:
            raise MigrationError("reviewed producer design drifted")
        if _old_output_references(producer) != 1:
            raise MigrationError("reviewed producer output drifted")
    elif PINNED_PRODUCER_UID not in retired_uids:
        raise MigrationError(
            "reviewed producer is absent without its UID in retiredRecipeUids"
        )

    transformed = copy.deepcopy(source)
    next_cards: list[dict[str, Any]] = []
    changed_consumers = 0
    replacements = 0
    for index, card in enumerate(cards):
        if card["recipeId"] == PINNED_PRODUCER_RECIPE_ID:
            continue
        next_card, count = transform_card(card, f"reviewed.recipes[{index}]")
        next_cards.append(next_card)
        if count:
            changed_consumers += 1
            replacements += count
    transformed["recipes"] = next_cards
    if PINNED_PRODUCER_UID not in transformed["retiredRecipeUids"]:
        transformed["retiredRecipeUids"].append(PINNED_PRODUCER_UID)

    if transformed["removals"] != source["removals"]:
        raise MigrationError("internal error: reviewed removals changed")
    if any(_eligible_old_references(card) for card in next_cards):
        raise MigrationError("internal error: reviewed consumer still uses retired casing")
    if any(_old_output_references(card) for card in next_cards):
        raise MigrationError("managed recipe still produces the retired casing")

    if enforce_repository_counts and producer_cards:
        if changed_consumers != EXPECTED_REVIEWED_CONSUMERS:
            raise MigrationError(
                f"reviewed affected-consumer count drifted: {changed_consumers}"
            )
        if replacements != EXPECTED_REVIEWED_REFERENCES:
            raise MigrationError(f"reviewed replacement count drifted: {replacements}")

    return transformed, {
        "changedConsumers": changed_consumers,
        "replacements": replacements,
        "producerRetired": int(bool(producer_cards)),
    }


def transform_acceptance(
    source: dict[str, Any],
    *,
    enforce_repository_counts: bool = False,
    producer_hash: str = ACCEPTANCE_PRODUCER_HASH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Rewrite frozen card designs while preserving every review classification."""

    if source.get("schemaVersion") != 1 or source.get("project") != "default":
        raise MigrationError("acceptance must be schemaVersion 1 project default")
    entries = source.get("entries")
    if not isinstance(entries, list):
        raise MigrationError("acceptance needs an entries array")

    transformed = copy.deepcopy(source)
    next_entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_uids: set[str] = set()
    status_counts: Counter[str] = Counter()
    affected_status_counts: Counter[str] = Counter()
    changed_consumers = 0
    replacements = 0
    producer_count = 0

    for index, raw_entry in enumerate(entries):
        if not isinstance(raw_entry, dict):
            raise MigrationError(f"acceptance.entries[{index}] must be an object")
        recipe_id = raw_entry.get("recipeId")
        decision = raw_entry.get("decision")
        card = raw_entry.get("card")
        if not isinstance(recipe_id, str) or not recipe_id:
            raise MigrationError(f"acceptance.entries[{index}] has no recipeId")
        if not isinstance(decision, dict):
            raise MigrationError(f"acceptance decision for {recipe_id} is invalid")
        card = validate_card(card, f"acceptance.entries[{index}].card")
        if card["recipeId"] != recipe_id:
            raise MigrationError(f"acceptance card identity mismatch for {recipe_id}")
        if recipe_id in seen_ids or card["uid"] in seen_uids:
            raise MigrationError(f"acceptance repeats recipe identity {recipe_id}")
        seen_ids.add(recipe_id)
        seen_uids.add(card["uid"])
        status = decision.get("status")
        if status not in VALID_ACCEPTANCE_STATUSES:
            raise MigrationError(f"acceptance status is invalid for {recipe_id}")
        status_counts[status] += 1
        if decision.get("uid") != card["uid"]:
            raise MigrationError(f"acceptance UID mismatch for {recipe_id}")
        if decision.get("cardSha256") != design_hash(card):
            raise MigrationError(f"acceptance fingerprint mismatch for {recipe_id}")

        next_entry = copy.deepcopy(raw_entry)
        if recipe_id == PINNED_PRODUCER_RECIPE_ID:
            producer_count += 1
            if card["uid"] != PINNED_PRODUCER_UID:
                raise MigrationError("acceptance producer UID drifted")
            if status != "rejected" or design_hash(card) != producer_hash:
                raise MigrationError("acceptance producer decision/design drifted")
            if _old_output_references(card) != 1:
                raise MigrationError("acceptance producer output drifted")
        else:
            next_card, count = transform_card(
                card, f"acceptance.entries[{index}].card"
            )
            next_entry["card"] = next_card
            if count:
                changed_consumers += 1
                replacements += count
                affected_status_counts[status] += 1
                next_entry["decision"]["cardSha256"] = design_hash(next_card)
        next_entries.append(next_entry)

    if producer_count != 1:
        raise MigrationError("acceptance must retain exactly one rejected producer snapshot")
    transformed["entries"] = next_entries
    expected_top_counts = {
        "reviewed": len(entries),
        "approved": status_counts["approved"],
        "rejected": status_counts["rejected"],
    }
    for field, actual in expected_top_counts.items():
        if source.get(field) != actual:
            raise MigrationError(
                f"acceptance {field} count is stale: {source.get(field)!r} != {actual}"
            )
        if transformed.get(field) != source.get(field):
            raise MigrationError(f"internal error: acceptance {field} changed")

    before_classifications = [
        (
            entry["recipeId"],
            entry["decision"].get("uid"),
            entry["decision"].get("status"),
            entry["decision"].get("reason"),
            entry["decision"].get("note"),
        )
        for entry in entries
    ]
    after_classifications = [
        (
            entry["recipeId"],
            entry["decision"].get("uid"),
            entry["decision"].get("status"),
            entry["decision"].get("reason"),
            entry["decision"].get("note"),
        )
        for entry in next_entries
    ]
    if after_classifications != before_classifications:
        raise MigrationError("internal error: review classifications changed")
    if transformed.get("inputSha256") != source.get("inputSha256"):
        raise MigrationError("internal error: acceptance provenance changed")

    for entry in next_entries:
        card = entry["card"]
        if entry["recipeId"] == PINNED_PRODUCER_RECIPE_ID:
            continue
        if _eligible_old_references(card):
            raise MigrationError("acceptance consumer still uses retired casing")
        if _old_output_references(card):
            raise MigrationError("acceptance non-producer outputs retired casing")
        if entry["decision"]["cardSha256"] != design_hash(card):
            raise MigrationError("internal error: transformed acceptance hash is stale")

    if enforce_repository_counts and changed_consumers:
        if dict(status_counts) != EXPECTED_ACCEPTANCE_STATUS_COUNTS:
            raise MigrationError(f"acceptance status counts drifted: {dict(status_counts)}")
        if changed_consumers != EXPECTED_ACCEPTANCE_CONSUMERS:
            raise MigrationError(
                f"acceptance affected-consumer count drifted: {changed_consumers}"
            )
        if replacements != EXPECTED_ACCEPTANCE_REFERENCES:
            raise MigrationError(
                f"acceptance replacement count drifted: {replacements}"
            )
        if dict(affected_status_counts) != EXPECTED_AFFECTED_ACCEPTANCE_STATUS_COUNTS:
            raise MigrationError(
                "acceptance affected-status counts drifted: "
                f"{dict(affected_status_counts)}"
            )

    return transformed, {
        "changedConsumers": changed_consumers,
        "replacements": replacements,
        "statusCounts": dict(status_counts),
        "affectedStatusCounts": dict(affected_status_counts),
        "producerEvidencePreserved": producer_count,
    }


def transform_sources(
    reviewed: dict[str, Any],
    acceptance: dict[str, Any],
    *,
    enforce_repository_counts: bool = False,
    acceptance_producer_hash: str = ACCEPTANCE_PRODUCER_HASH,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    next_reviewed, reviewed_report = transform_reviewed_managed(
        reviewed, enforce_repository_counts=enforce_repository_counts
    )
    next_acceptance, acceptance_report = transform_acceptance(
        acceptance,
        enforce_repository_counts=enforce_repository_counts,
        producer_hash=acceptance_producer_hash,
    )
    return next_reviewed, next_acceptance, OrderedDict((
        ("schemaVersion", 1),
        ("policy", OrderedDict((("from", OLD_ID), ("to", NEW_ID)))),
        ("reviewedManaged", reviewed_report),
        ("acceptance", acceptance_report),
    ))


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewed", type=Path, required=True)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--output-reviewed", type=Path)
    parser.add_argument("--output-acceptance", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="atomically replace the two inputs (required for intentional source updates)",
    )
    parser.add_argument("--enforce-repository-counts", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    reviewed_path = args.reviewed.resolve()
    acceptance_path = args.acceptance.resolve()
    next_reviewed, next_acceptance, report = transform_sources(
        load_json(reviewed_path),
        load_json(acceptance_path),
        enforce_repository_counts=args.enforce_repository_counts,
    )

    if args.in_place and (args.output_reviewed or args.output_acceptance):
        raise SystemExit("--in-place cannot be combined with explicit output paths")
    if not args.check and not args.in_place and not (
        args.output_reviewed and args.output_acceptance
    ):
        raise SystemExit(
            "refusing an ambiguous write: use --in-place or provide both output paths"
        )
    if bool(args.output_reviewed) != bool(args.output_acceptance):
        raise SystemExit("provide both --output-reviewed and --output-acceptance")

    outputs = (
        (
            args.output_reviewed.resolve()
            if args.output_reviewed
            else reviewed_path,
            next_reviewed,
        ),
        (
            args.output_acceptance.resolve()
            if args.output_acceptance
            else acceptance_path,
            next_acceptance,
        ),
    )
    if args.check:
        stale = [str(path) for path, document in outputs if path.read_bytes() != encoded(document)]
        if stale:
            raise SystemExit("Current review steel-frame sources are stale: " + ", ".join(stale))
    else:
        for path, document in outputs:
            atomic_write(path, document)
        if args.report:
            atomic_write(args.report.resolve(), report)

    print(
        "Current review steel-frame policy is canonical: "
        f"{report['reviewedManaged']['changedConsumers']} managed consumers and "
        f"{report['acceptance']['changedConsumers']} acceptance consumers transformed; "
        f"producer retired={report['reviewedManaged']['producerRetired']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
