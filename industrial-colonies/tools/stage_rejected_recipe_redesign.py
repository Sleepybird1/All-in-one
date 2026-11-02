#!/usr/bin/env python3
"""Stage one rejected KJSGen recipe redesign back into the Pending queue.

This tool never edits an input and has no deployment mode.  It accepts the
complete Default/review-archive topology, ledger, current reviewed managed
source, frozen acceptance, optional requeue history, and one separately
authored redesign.  Only after every invariant passes does it atomically
publish a new staging directory.

Pending is represented exactly as the mod represents it at runtime: the
redesigned card remains in Default, while its ledger decision and rejected
archive snapshot are removed.  The original rejection decision and full card
snapshot are appended to a separate durable history artifact because the
runtime ledger intentionally supports decisions only, not a ``pending``
status or append-only history.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections import Counter, OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from tools.reconcile_kjsgen_review_batch import (
        ReconcileError,
        design_hash,
        output_tokens,
        validate_card,
    )
except ModuleNotFoundError:  # Direct execution from the tools directory.
    from reconcile_kjsgen_review_batch import (  # type: ignore
        ReconcileError,
        design_hash,
        output_tokens,
        validate_card,
    )


HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
STATUS_TO_ARCHIVE = OrderedDict((
    ("approved", "approved"),
    ("rejected", "rejected"),
    ("maybe", "deferred"),
    ("disabled", "disabled"),
))
EXPECTED_PROJECT_NAMES = {
    "default": "default",
    "approved": "approved recipes",
    "rejected": "rejected recipes",
    "deferred": "deferred",
    "disabled": "disabled recipes",
}
OUTPUT_FILENAMES = OrderedDict((
    ("default", "default.json"),
    ("approved", "approved_recipes.json"),
    ("rejected", "rejected_recipes.json"),
    ("deferred", "Deferred.json"),
    ("disabled", "disabled_recipes.json"),
    ("ledger", "default.recipe_reviews.json"),
    ("reviewedManaged", "default.reviewed.managed.json"),
    ("acceptance", "recipe_review_acceptance.json"),
    ("history", "rejected_recipe_requeue_history.json"),
))
REPORT_FILENAME = "requeue_report.json"
MANIFEST_FILENAME = "requeue_manifest.json"


class RequeueError(ReconcileError):
    """Raised when a rejected card cannot be safely returned to Pending."""


@dataclass(frozen=True)
class ProjectIndex:
    label: str
    document: dict[str, Any]
    cards: list[dict[str, Any]]
    by_id: dict[str, dict[str, Any]]
    by_uid: dict[str, dict[str, Any]]


def decode_json(payload: bytes, path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8-sig"),
            object_pairs_hook=OrderedDict,
        )
    except UnicodeDecodeError as exc:
        raise RequeueError(f"invalid UTF-8 in {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RequeueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RequeueError(f"{path} must contain a JSON object")
    return value


def load_json(path: Path, *, required: bool = True) -> dict[str, Any] | None:
    if not path.is_file():
        if required:
            raise RequeueError(f"missing required input: {path}")
        return None
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise RequeueError(f"cannot read {path}: {exc}") from exc
    return decode_json(payload, path)


def encoded(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def normalized_name(value: str) -> str:
    return " ".join(value.replace("_", " ").lower().split())


def project_index(
    document: dict[str, Any], label: str, expected_name: str
) -> ProjectIndex:
    name = document.get("name")
    if not isinstance(name, str) or normalized_name(name) != expected_name:
        raise RequeueError(
            f"{label} project name mismatch: expected {expected_name!r}, found {name!r}"
        )
    recipes = document.get("recipes")
    removals = document.get("removals")
    if not isinstance(recipes, list) or not isinstance(removals, list):
        raise RequeueError(f"{label} project needs recipes and removals arrays")
    cards: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    by_uid: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(recipes):
        card = validate_card(raw, f"{label}.recipes[{index}]")
        recipe_id = card["recipeId"]
        uid = card["uid"]
        if recipe_id in by_id:
            raise RequeueError(f"duplicate recipe ID in {label}: {recipe_id}")
        if uid in by_uid:
            raise RequeueError(f"duplicate recipe UID in {label}: {uid}")
        cards.append(card)
        by_id[recipe_id] = card
        by_uid[uid] = card
    return ProjectIndex(label, document, cards, by_id, by_uid)


def validate_ledger(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if document.get("schemaVersion") != 1 or document.get("project") != "default":
        raise RequeueError("review ledger must be schemaVersion 1 for project default")
    reviews = document.get("reviews")
    if not isinstance(reviews, dict):
        raise RequeueError("review ledger needs a reviews object")
    result: dict[str, dict[str, Any]] = {}
    seen_uids: dict[str, str] = {}
    for recipe_id, raw in reviews.items():
        if not isinstance(recipe_id, str) or not recipe_id or not isinstance(raw, dict):
            raise RequeueError("review ledger entries must map IDs to objects")
        uid = raw.get("uid")
        status = raw.get("status")
        reason = raw.get("reason")
        note = raw.get("note", "")
        digest = raw.get("cardSha256")
        if not isinstance(uid, str) or not uid:
            raise RequeueError(f"review {recipe_id} has no UID")
        if uid in seen_uids and seen_uids[uid] != recipe_id:
            raise RequeueError(
                f"review UID {uid} belongs to both {seen_uids[uid]} and {recipe_id}"
            )
        seen_uids[uid] = recipe_id
        if status not in STATUS_TO_ARCHIVE:
            raise RequeueError(f"review {recipe_id} has unsupported status {status!r}")
        if not isinstance(reason, str) or not reason:
            raise RequeueError(f"review {recipe_id} has no reason")
        if status == "approved" and reason != "approved":
            raise RequeueError(f"approved review {recipe_id} has reason {reason!r}")
        if status == "maybe" and reason != "maybe":
            raise RequeueError(f"deferred review {recipe_id} has reason {reason!r}")
        if not isinstance(note, str):
            raise RequeueError(f"review {recipe_id} note must be text")
        if not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest):
            raise RequeueError(f"review {recipe_id} has an invalid cardSha256")
        result[recipe_id] = raw
    return result


def validate_project_topology(
    projects: Mapping[str, ProjectIndex],
    reviews: Mapping[str, dict[str, Any]],
) -> None:
    """Validate exact Default-to-one-archive mirrors and reject collisions.

    A reviewed card is intentionally present in Default and exactly one status
    archive.  That exact mirror is the only allowed cross-project duplicate.
    The same ID with another UID/design, the same UID with another ID, or any
    ID/UID in two archives is rejected.
    """

    default = projects["default"]
    archive_labels = tuple(STATUS_TO_ARCHIVE.values())

    id_owners: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    uid_owners: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for label, project in projects.items():
        for card in project.cards:
            id_owners.setdefault(card["recipeId"], []).append((label, card))
            uid_owners.setdefault(card["uid"], []).append((label, card))

    for recipe_id, owners in id_owners.items():
        identities = {(card["uid"], design_hash(card)) for _, card in owners}
        if len(identities) != 1:
            raise RequeueError(
                f"recipe ID collision across projects for {recipe_id}: "
                + ", ".join(label for label, _ in owners)
            )
        archive_owners = [label for label, _ in owners if label in archive_labels]
        if len(archive_owners) > 1:
            raise RequeueError(
                f"recipe ID {recipe_id} appears in multiple archives: {archive_owners}"
            )
        # Legacy/orphan review snapshots can intentionally remain in one archive
        # after their card has left Default.  They are immutable review evidence,
        # not a second active queue entry.  They still must have exactly one
        # matching ledger decision (validated below), and can never appear in two
        # archives.  When Default also owns the ID, only an exact mirror is valid.

    for uid, owners in uid_owners.items():
        recipe_ids = {card["recipeId"] for _, card in owners}
        if len(recipe_ids) != 1:
            raise RequeueError(
                f"recipe UID collision across projects for {uid}: {sorted(recipe_ids)}"
            )
        archive_owners = [label for label, _ in owners if label in archive_labels]
        if len(archive_owners) > 1:
            raise RequeueError(
                f"recipe UID {uid} appears in multiple archives: {archive_owners}"
            )

    for recipe_id, record in reviews.items():
        expected_archive = STATUS_TO_ARCHIVE[record["status"]]
        snapshot = projects[expected_archive].by_id.get(recipe_id)
        if snapshot is None:
            raise RequeueError(
                f"{record['status']} review has no {expected_archive} snapshot: {recipe_id}"
            )
        if snapshot["uid"] != record["uid"] or design_hash(snapshot) != record["cardSha256"]:
            raise RequeueError(f"archive snapshot is stale for {recipe_id}")
        default_card = default.by_id.get(recipe_id)
        if default_card is not None:
            if default_card["uid"] != record["uid"]:
                raise RequeueError(f"ledger UID does not match Default for {recipe_id}")
            if design_hash(default_card) != record["cardSha256"]:
                raise RequeueError(
                    f"ledger fingerprint does not match Default for {recipe_id}"
                )

    for archive_label in archive_labels:
        expected_status = next(
            status for status, label in STATUS_TO_ARCHIVE.items() if label == archive_label
        )
        for card in projects[archive_label].cards:
            record = reviews.get(card["recipeId"])
            if record is None:
                raise RequeueError(
                    f"{archive_label} snapshot has no ledger decision: {card['recipeId']}"
                )
            if record["status"] != expected_status:
                raise RequeueError(
                    f"{archive_label} snapshot status mismatch for {card['recipeId']}"
                )


def validate_acceptance(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if document.get("schemaVersion") != 1 or document.get("project") != "default":
        raise RequeueError("acceptance must be schemaVersion 1 for project default")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise RequeueError("acceptance needs an entries array")
    by_id: dict[str, dict[str, Any]] = {}
    statuses: Counter[str] = Counter()
    seen_uids: dict[str, str] = {}
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise RequeueError(f"acceptance.entries[{index}] must be an object")
        recipe_id = raw.get("recipeId")
        decision = raw.get("decision")
        card = validate_card(raw.get("card"), f"acceptance.entries[{index}].card")
        if not isinstance(recipe_id, str) or not recipe_id or card["recipeId"] != recipe_id:
            raise RequeueError(f"acceptance entry {index} has mismatched identity")
        if recipe_id in by_id:
            raise RequeueError(f"acceptance repeats recipe ID {recipe_id}")
        if card["uid"] in seen_uids and seen_uids[card["uid"]] != recipe_id:
            raise RequeueError(f"acceptance repeats recipe UID {card['uid']}")
        seen_uids[card["uid"]] = recipe_id
        if not isinstance(decision, dict):
            raise RequeueError(f"acceptance decision is invalid for {recipe_id}")
        status = decision.get("status")
        if status not in {"approved", "rejected"}:
            raise RequeueError(f"acceptance status is invalid for {recipe_id}")
        statuses[status] += 1
        if decision.get("uid") != card["uid"]:
            raise RequeueError(f"acceptance UID mismatch for {recipe_id}")
        if decision.get("cardSha256") != design_hash(card):
            raise RequeueError(f"acceptance fingerprint mismatch for {recipe_id}")
        by_id[recipe_id] = raw
    expected = {
        "reviewed": len(entries),
        "approved": statuses["approved"],
        "rejected": statuses["rejected"],
    }
    for field, count in expected.items():
        if document.get(field) != count:
            raise RequeueError(
                f"acceptance {field} count is stale: {document.get(field)!r} != {count}"
            )
    return by_id


def validate_history(document: dict[str, Any]) -> list[dict[str, Any]]:
    if document.get("schemaVersion") != 1 or document.get("project") != "default":
        raise RequeueError("requeue history must be schemaVersion 1 for project default")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise RequeueError("requeue history needs an entries array")
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise RequeueError(f"requeue history entry {index} must be an object")
        recipe_id = entry.get("recipeId")
        uid = entry.get("uid")
        entry_txid = entry.get("transactionId")
        transition = entry.get("transition")
        decision = entry.get("originalDecision")
        original_hash = entry.get("originalCardSha256")
        redesigned_hash = entry.get("redesignedCardSha256")
        if not isinstance(entry_txid, str) or not HASH_PATTERN.fullmatch(entry_txid):
            raise RequeueError(f"requeue history entry {index} has invalid transactionId")
        if entry_txid in seen:
            raise RequeueError(f"requeue history repeats transaction {entry_txid}")
        seen.add(entry_txid)
        if not isinstance(recipe_id, str) or not recipe_id:
            raise RequeueError(f"requeue history entry {index} has no recipeId")
        if not isinstance(uid, str) or not uid:
            raise RequeueError(f"requeue history entry {index} has no UID")
        if transition != {"from": "rejected", "to": "pending"}:
            raise RequeueError(f"requeue history entry {index} has invalid transition")
        if not isinstance(decision, dict):
            raise RequeueError(f"requeue history entry {index} has no original decision")
        if decision.get("status") != "rejected" or decision.get("uid") != uid:
            raise RequeueError(
                f"requeue history entry {index} does not preserve a Rejected decision"
            )
        if not isinstance(decision.get("reason"), str) or not decision["reason"]:
            raise RequeueError(f"requeue history entry {index} has no rejection reason")
        if not isinstance(decision.get("note", ""), str):
            raise RequeueError(f"requeue history entry {index} has an invalid note")
        if not isinstance(original_hash, str) or not HASH_PATTERN.fullmatch(original_hash):
            raise RequeueError(f"requeue history entry {index} has invalid original hash")
        if not isinstance(redesigned_hash, str) or not HASH_PATTERN.fullmatch(redesigned_hash):
            raise RequeueError(f"requeue history entry {index} has invalid redesign hash")
        if original_hash == redesigned_hash:
            raise RequeueError(f"requeue history entry {index} has no design change")
        original = validate_card(
            entry.get("originalRejectedCard"),
            f"requeue history entry {index} original card",
        )
        redesigned = validate_card(
            entry.get("redesignedPendingCard"),
            f"requeue history entry {index} redesigned card",
        )
        if (
            original["recipeId"] != recipe_id
            or redesigned["recipeId"] != recipe_id
            or original["uid"] != uid
            or redesigned["uid"] != uid
        ):
            raise RequeueError(f"requeue history entry {index} identity drifted")
        if design_hash(original) != original_hash:
            raise RequeueError(f"requeue history entry {index} original hash drifted")
        if design_hash(redesigned) != redesigned_hash:
            raise RequeueError(f"requeue history entry {index} redesign hash drifted")
        if decision.get("cardSha256") != original_hash:
            raise RequeueError(f"requeue history entry {index} decision hash drifted")
        if output_tokens(original) != output_tokens(redesigned):
            raise RequeueError(f"requeue history entry {index} output identity drifted")
        expected_transaction = transaction_id(
            recipe_id, uid, original_hash, redesigned_hash, decision
        )
        if entry_txid != expected_transaction:
            raise RequeueError(f"requeue history entry {index} transaction hash drifted")
    return entries


def empty_history() -> OrderedDict[str, Any]:
    return OrderedDict((
        ("schemaVersion", 1),
        ("project", "default"),
        ("entries", []),
    ))


def load_redesign(document: dict[str, Any], recipe_id: str) -> dict[str, Any]:
    if isinstance(document.get("recipes"), list):
        matches = [
            raw for raw in document["recipes"]
            if isinstance(raw, dict) and raw.get("recipeId") == recipe_id
        ]
        if len(matches) != 1:
            raise RequeueError(
                f"redesign source must contain exactly one {recipe_id} card"
            )
        raw = matches[0]
    else:
        raw = document
    return copy.deepcopy(validate_card(raw, "redesign card"))


def validate_reviewed_managed(document: dict[str, Any]) -> ProjectIndex:
    if document.get("schema") != 1 or document.get("project") != "default":
        raise RequeueError("reviewed managed source must be schema 1 project default")
    if not isinstance(document.get("retiredRecipeUids"), list):
        raise RequeueError("reviewed managed source needs retiredRecipeUids")
    if not isinstance(document.get("retiredRemovalUids"), list):
        raise RequeueError("reviewed managed source needs retiredRemovalUids")
    synthetic = copy.deepcopy(document)
    synthetic["name"] = "default"
    return project_index(synthetic, "reviewed managed", "default")


def validate_reviewed_project_identities(
    projects: Mapping[str, ProjectIndex], reviewed: ProjectIndex
) -> None:
    """Reject conflicting ID/UID reuse between review projects and source.

    A managed-source card and its review snapshot are two roles for one recipe,
    so matching ID+UID ownership is allowed.  Reusing either identifier for a
    different recipe is never allowed.  Fingerprints are intentionally checked
    only for the target later: other source cards can already be valid pending
    redesigns and must pass through this single-target transaction unchanged.
    """

    project_ids: dict[str, str] = {}
    project_uids: dict[str, str] = {}
    for project in projects.values():
        for card in project.cards:
            project_ids.setdefault(card["recipeId"], card["uid"])
            project_uids.setdefault(card["uid"], card["recipeId"])
    for card in reviewed.cards:
        expected_uid = project_ids.get(card["recipeId"])
        if expected_uid is not None and expected_uid != card["uid"]:
            raise RequeueError(
                f"reviewed managed source recipe ID {card['recipeId']} reuses "
                f"UID {card['uid']} instead of {expected_uid}"
            )
        expected_id = project_uids.get(card["uid"])
        if expected_id is not None and expected_id != card["recipeId"]:
            raise RequeueError(
                f"reviewed managed source recipe UID {card['uid']} belongs to "
                f"both {expected_id} and {card['recipeId']}"
            )


def insert_in_default_order(
    reviewed_cards: list[dict[str, Any]],
    redesigned: dict[str, Any],
    default_cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Insert a formerly absent source card without scrambling source order."""

    default_positions = {
        card["recipeId"]: index for index, card in enumerate(default_cards)
    }
    target_position = default_positions[redesigned["recipeId"]]
    insertion = len(reviewed_cards)
    for index, card in enumerate(reviewed_cards):
        position = default_positions.get(card["recipeId"])
        if position is not None and position > target_position:
            insertion = index
            break
    result = copy.deepcopy(reviewed_cards)
    result.insert(insertion, copy.deepcopy(redesigned))
    return result


def transaction_id(
    recipe_id: str,
    uid: str,
    original_hash: str,
    redesigned_hash: str,
    decision: dict[str, Any],
) -> str:
    payload = OrderedDict((
        ("recipeId", recipe_id),
        ("uid", uid),
        ("originalCardSha256", original_hash),
        ("redesignedCardSha256", redesigned_hash),
        ("originalDecision", decision),
    ))
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def transform_documents(
    projects: Mapping[str, dict[str, Any]],
    ledger: dict[str, Any],
    reviewed_managed: dict[str, Any],
    acceptance: dict[str, Any],
    history: dict[str, Any],
    redesign_document: dict[str, Any],
    recipe_id: str,
) -> tuple[OrderedDict[str, dict[str, Any]], OrderedDict[str, Any]]:
    if not recipe_id:
        raise RequeueError("recipe ID must not be blank")
    indexes = OrderedDict(
        (
            label,
            project_index(projects[label], label, EXPECTED_PROJECT_NAMES[label]),
        )
        for label in EXPECTED_PROJECT_NAMES
    )
    reviews = validate_ledger(ledger)
    validate_project_topology(indexes, reviews)
    acceptance_by_id = validate_acceptance(acceptance)
    history_entries = validate_history(history)
    reviewed_index = validate_reviewed_managed(reviewed_managed)
    validate_reviewed_project_identities(indexes, reviewed_index)

    original = indexes["default"].by_id.get(recipe_id)
    rejected_snapshot = indexes["rejected"].by_id.get(recipe_id)
    decision = reviews.get(recipe_id)
    if original is None or rejected_snapshot is None or decision is None:
        raise RequeueError(
            f"target must exist in Default, Rejected, and ledger: {recipe_id}"
        )
    if decision["status"] != "rejected":
        raise RequeueError(
            f"target is not Rejected: {recipe_id} has status {decision['status']!r}"
        )
    if original["uid"] != rejected_snapshot["uid"] or original["uid"] != decision["uid"]:
        raise RequeueError(f"target UID topology is inconsistent: {recipe_id}")
    original_hash = design_hash(original)
    if original_hash != design_hash(rejected_snapshot) or original_hash != decision["cardSha256"]:
        raise RequeueError(f"target rejection snapshots are inconsistent: {recipe_id}")

    redesigned = load_redesign(redesign_document, recipe_id)
    if redesigned["recipeId"] != recipe_id:
        raise RequeueError("redesign changed recipe ID")
    if redesigned["uid"] != original["uid"]:
        raise RequeueError("redesign changed recipe UID")
    redesigned_hash = design_hash(redesigned)
    if redesigned_hash == original_hash:
        raise RequeueError(
            "redesign fingerprint is unchanged; comment/metadata edits cannot requeue a rejection"
        )
    if output_tokens(redesigned) != output_tokens(original):
        raise RequeueError("redesign changed the concrete recipe output identity")

    reviewed_source_card = reviewed_index.by_id.get(recipe_id)
    if reviewed_source_card is not None:
        if reviewed_source_card["uid"] != original["uid"]:
            raise RequeueError("reviewed managed source target UID is inconsistent")
        if design_hash(reviewed_source_card) != original_hash:
            raise RequeueError(
                "reviewed managed source target no longer matches the rejected design"
            )
    conflicting_uid = reviewed_index.by_uid.get(original["uid"])
    if conflicting_uid is not None and conflicting_uid["recipeId"] != recipe_id:
        raise RequeueError("reviewed managed source reuses the target UID")
    acceptance_entry = acceptance_by_id.get(recipe_id)
    if acceptance_entry is not None:
        if acceptance_entry["decision"]["status"] != "rejected":
            raise RequeueError(
                "frozen acceptance records the target as Approved; refusing to requeue"
            )
        if acceptance_entry["decision"]["uid"] != original["uid"]:
            raise RequeueError("frozen acceptance target UID is inconsistent")

    txid = transaction_id(
        recipe_id, original["uid"], original_hash, redesigned_hash, decision
    )
    if any(entry.get("transactionId") == txid for entry in history_entries):
        raise RequeueError(f"requeue transaction already exists: {txid}")

    next_projects = OrderedDict(
        (label, copy.deepcopy(index.document)) for label, index in indexes.items()
    )
    next_default_cards = copy.deepcopy(indexes["default"].cards)
    target_default_index = next(
        index for index, card in enumerate(next_default_cards)
        if card["recipeId"] == recipe_id
    )
    next_default_cards[target_default_index] = copy.deepcopy(redesigned)
    next_projects["default"]["recipes"] = next_default_cards
    next_projects["rejected"]["recipes"] = [
        copy.deepcopy(card)
        for card in indexes["rejected"].cards
        if card["recipeId"] != recipe_id
    ]

    next_ledger = copy.deepcopy(ledger)
    del next_ledger["reviews"][recipe_id]

    next_reviewed = copy.deepcopy(reviewed_managed)
    if reviewed_source_card is not None:
        next_reviewed["recipes"] = [
            copy.deepcopy(redesigned)
            if card["recipeId"] == recipe_id else copy.deepcopy(card)
            for card in reviewed_index.cards
        ]
    else:
        next_reviewed["recipes"] = insert_in_default_order(
            reviewed_index.cards, redesigned, next_default_cards
        )
    next_reviewed["retiredRecipeUids"] = [
        uid for uid in next_reviewed["retiredRecipeUids"] if uid != original["uid"]
    ]

    history_entry = OrderedDict((
        ("transactionId", txid),
        ("recipeId", recipe_id),
        ("uid", original["uid"]),
        ("transition", OrderedDict((("from", "rejected"), ("to", "pending")))),
        ("originalDecision", copy.deepcopy(decision)),
        ("originalCardSha256", original_hash),
        ("redesignedCardSha256", redesigned_hash),
        ("originalRejectedCard", copy.deepcopy(rejected_snapshot)),
        ("redesignedPendingCard", copy.deepcopy(redesigned)),
    ))
    next_history = copy.deepcopy(history)
    next_history["entries"].append(history_entry)

    outputs: OrderedDict[str, dict[str, Any]] = OrderedDict((
        ("default", next_projects["default"]),
        ("approved", next_projects["approved"]),
        ("rejected", next_projects["rejected"]),
        ("deferred", next_projects["deferred"]),
        ("disabled", next_projects["disabled"]),
        ("ledger", next_ledger),
        ("reviewedManaged", next_reviewed),
        ("acceptance", copy.deepcopy(acceptance)),
        ("history", next_history),
    ))

    next_indexes = OrderedDict(
        (
            label,
            project_index(outputs[label], label, EXPECTED_PROJECT_NAMES[label]),
        )
        for label in EXPECTED_PROJECT_NAMES
    )
    next_reviews = validate_ledger(next_ledger)
    validate_project_topology(next_indexes, next_reviews)
    validate_acceptance(outputs["acceptance"])
    validate_history(next_history)
    next_reviewed_index = validate_reviewed_managed(next_reviewed)
    validate_reviewed_project_identities(next_indexes, next_reviewed_index)

    if recipe_id in next_reviews:
        raise RequeueError("internal error: target still has a ledger decision")
    if recipe_id not in next_indexes["default"].by_id:
        raise RequeueError("internal error: target disappeared from Default")
    for archive_label in STATUS_TO_ARCHIVE.values():
        if recipe_id in next_indexes[archive_label].by_id:
            raise RequeueError(
                f"internal error: Pending target remains in {archive_label} archive"
            )
    if recipe_id not in next_reviewed_index.by_id:
        raise RequeueError("internal error: redesign missing from reviewed managed source")
    if design_hash(next_reviewed_index.by_id[recipe_id]) != redesigned_hash:
        raise RequeueError("internal error: reviewed managed redesign hash drifted")
    if original["uid"] in next_reviewed.get("retiredRecipeUids", []):
        raise RequeueError("internal error: active redesigned UID remains retired")
    if outputs["acceptance"] != acceptance:
        raise RequeueError("internal error: frozen acceptance changed")
    for label in ("approved", "deferred", "disabled"):
        if outputs[label] != projects[label]:
            raise RequeueError(f"internal error: unrelated {label} archive changed")
    for label in EXPECTED_PROJECT_NAMES:
        if outputs[label].get("removals") != projects[label].get("removals"):
            raise RequeueError(f"internal error: {label} removals changed")
    if next_projects["rejected"].get("removals") != projects["rejected"].get("removals"):
        raise RequeueError("internal error: rejected removals changed")

    report = OrderedDict((
        ("schemaVersion", 1),
        ("operation", "rejected_recipe_redesign_requeue"),
        ("transactionId", txid),
        ("recipeId", recipe_id),
        ("uid", original["uid"]),
        ("transition", OrderedDict((("from", "rejected"), ("to", "pending")))),
        ("originalDecision", copy.deepcopy(decision)),
        ("originalCardSha256", original_hash),
        ("redesignedCardSha256", redesigned_hash),
        ("designFingerprintChanged", True),
        ("reviewedManagedAction", "replaced" if reviewed_source_card else "inserted"),
        ("acceptanceHistory", OrderedDict((
            ("preservedUnchanged", True),
            ("containsTarget", acceptance_entry is not None),
            (
                "matchesCurrentRejectedFingerprint",
                acceptance_entry is not None
                and acceptance_entry["decision"]["cardSha256"] == original_hash,
            ),
        ))),
        ("historyEntriesBefore", len(history_entries)),
        ("historyEntriesAfter", len(next_history["entries"])),
        ("projectRecipeCounts", OrderedDict(
            (
                label,
                OrderedDict((
                    ("before", len(indexes[label].cards)),
                    ("after", len(next_indexes[label].cards)),
                )),
            )
            for label in EXPECTED_PROJECT_NAMES
        )),
        ("reviewCounts", OrderedDict((
            ("before", dict(Counter(record["status"] for record in reviews.values()))),
            ("after", dict(Counter(record["status"] for record in next_reviews.values()))),
        ))),
        ("invariants", OrderedDict((
            ("neverAutoApproved", True),
            ("targetHasNoLedgerDecision", True),
            ("targetAbsentFromEveryReviewArchive", True),
            ("originalRejectionPreservedInHistory", True),
            ("onlyExactDefaultArchiveMirrorsMayShareIdsOrUids", True),
            ("allInputArtifactsRemainUntouched", True),
            ("stagingOnly", True),
        ))),
    ))
    return outputs, report


def write_new_staging_directory(
    output_directory: Path,
    outputs: Mapping[str, dict[str, Any]],
    report: dict[str, Any],
    input_snapshots: Mapping[str, tuple[Path | None, bytes | None]],
) -> dict[str, Any]:
    output_directory = output_directory.resolve()
    if output_directory.exists():
        raise RequeueError(f"staging output already exists: {output_directory}")
    input_resolved = {
        path.resolve()
        for path, _ in input_snapshots.values()
        if path is not None
    }
    if output_directory in input_resolved:
        raise RequeueError("staging output cannot replace an input file")

    parent = output_directory.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_directory.name}.", dir=parent))
    try:
        artifact_bytes: OrderedDict[str, bytes] = OrderedDict(
            (label, encoded(document)) for label, document in outputs.items()
        )
        report_bytes = encoded(report)
        for label, payload in artifact_bytes.items():
            path = temporary / OUTPUT_FILENAMES[label]
            path.write_bytes(payload)
        (temporary / REPORT_FILENAME).write_bytes(report_bytes)

        input_artifacts: OrderedDict[str, Any] = OrderedDict()
        for label, (path, payload) in input_snapshots.items():
            if path is None or payload is None:
                missing = OrderedDict((("exists", False),))
                if path is not None:
                    missing["path"] = str(path.resolve())
                input_artifacts[label] = missing
            else:
                resolved = path.resolve()
                input_artifacts[label] = OrderedDict((
                    ("exists", True),
                    ("path", str(resolved)),
                    ("sha256", sha256_bytes(payload)),
                    ("size", len(payload)),
                ))

        output_artifacts: OrderedDict[str, Any] = OrderedDict()
        for label, payload in artifact_bytes.items():
            output_artifacts[label] = OrderedDict((
                ("file", OUTPUT_FILENAMES[label]),
                ("sha256", sha256_bytes(payload)),
                ("size", len(payload)),
            ))
        output_artifacts["report"] = OrderedDict((
            ("file", REPORT_FILENAME),
            ("sha256", sha256_bytes(report_bytes)),
            ("size", len(report_bytes)),
        ))

        manifest = OrderedDict((
            ("schemaVersion", 1),
            ("operation", "rejected_recipe_redesign_requeue"),
            ("transactionId", report["transactionId"]),
            ("recipeId", report["recipeId"]),
            ("uid", report["uid"]),
            ("stagingOnly", True),
            ("inputArtifacts", input_artifacts),
            ("outputArtifacts", output_artifacts),
            ("invariants", copy.deepcopy(report["invariants"])),
        ))
        (temporary / MANIFEST_FILENAME).write_bytes(encoded(manifest))

        # Re-read every completed artifact before exposing the staging directory.
        for artifact in output_artifacts.values():
            path = temporary / artifact["file"]
            if file_sha256(path) != artifact["sha256"]:
                raise RequeueError(f"staged hash verification failed: {path}")
            if path.stat().st_size != artifact["size"]:
                raise RequeueError(f"staged size verification failed: {path}")
        os.replace(temporary, output_directory)
        return manifest
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def stage_requeue(
    *,
    project_paths: Mapping[str, Path],
    ledger_path: Path,
    reviewed_managed_path: Path,
    acceptance_path: Path,
    redesign_path: Path,
    recipe_id: str,
    output_directory: Path,
    history_path: Path | None = None,
) -> dict[str, Any]:
    required_paths: OrderedDict[str, Path | None] = OrderedDict(
        (label, project_paths[label]) for label in EXPECTED_PROJECT_NAMES
    )
    required_paths["ledger"] = ledger_path
    required_paths["reviewedManaged"] = reviewed_managed_path
    required_paths["acceptance"] = acceptance_path
    required_paths["history"] = history_path
    all_paths = copy.copy(required_paths)
    all_paths["redesign"] = redesign_path
    declared_inputs = [path.resolve() for path in all_paths.values() if path is not None]
    if len(declared_inputs) != len(set(declared_inputs)):
        raise RequeueError("every workflow input path must be distinct")

    optional_labels = {"history"}
    input_snapshots: OrderedDict[str, tuple[Path | None, bytes | None]] = OrderedDict()
    for label, path in all_paths.items():
        if path is None:
            if label not in optional_labels:
                raise RequeueError(f"missing path for required input: {label}")
            input_snapshots[label] = (None, None)
            continue
        resolved = path.resolve()
        if not resolved.is_file():
            if label not in optional_labels:
                raise RequeueError(f"missing required input: {resolved}")
            input_snapshots[label] = (resolved, None)
            continue
        try:
            payload = resolved.read_bytes()
        except OSError as exc:
            raise RequeueError(f"cannot read {resolved}: {exc}") from exc
        input_snapshots[label] = (resolved, payload)

    def snapshot_document(label: str) -> dict[str, Any]:
        path, payload = input_snapshots[label]
        if path is None or payload is None:
            raise RequeueError(f"missing required input snapshot: {label}")
        return decode_json(payload, path)

    projects = OrderedDict(
        (label, snapshot_document(label)) for label in EXPECTED_PROJECT_NAMES
    )
    ledger = snapshot_document("ledger")
    reviewed = snapshot_document("reviewedManaged")
    acceptance = snapshot_document("acceptance")
    redesign = snapshot_document("redesign")
    history_path_snapshot, history_payload = input_snapshots["history"]
    history = (
        decode_json(history_payload, history_path_snapshot)
        if history_path_snapshot is not None and history_payload is not None
        else empty_history()
    )
    outputs, report = transform_documents(
        projects, ledger, reviewed, acceptance, history, redesign, recipe_id
    )
    manifest = write_new_staging_directory(
        output_directory,
        outputs,
        report,
        input_snapshots,
    )
    try:
        for path, payload in input_snapshots.values():
            if path is None:
                continue
            if payload is None:
                if path.exists():
                    raise RequeueError(f"optional input appeared during staging: {path}")
            elif not path.is_file() or path.read_bytes() != payload:
                raise RequeueError(f"input changed during staging: {path}")
    except Exception:
        shutil.rmtree(output_directory.resolve(), ignore_errors=True)
        raise
    return manifest


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--default", type=Path, required=True)
    parser.add_argument("--approved", type=Path, required=True)
    parser.add_argument("--rejected", type=Path, required=True)
    parser.add_argument("--deferred", type=Path, required=True)
    parser.add_argument("--disabled", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--reviewed-managed", type=Path, required=True)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--history", type=Path)
    parser.add_argument("--redesign", type=Path, required=True)
    parser.add_argument("--recipe-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = stage_requeue(
        project_paths=OrderedDict((
            ("default", args.default),
            ("approved", args.approved),
            ("rejected", args.rejected),
            ("deferred", args.deferred),
            ("disabled", args.disabled),
        )),
        ledger_path=args.ledger,
        reviewed_managed_path=args.reviewed_managed,
        acceptance_path=args.acceptance,
        redesign_path=args.redesign,
        recipe_id=args.recipe_id,
        output_directory=args.output_dir,
        history_path=args.history,
    )
    print(
        "Rejected redesign staged as Pending without approval: "
        f"{manifest['recipeId']} ({manifest['transactionId']}). "
        f"Stage: {args.output_dir.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
