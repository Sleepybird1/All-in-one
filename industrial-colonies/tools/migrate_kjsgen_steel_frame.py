#!/usr/bin/env python3
"""Stage the KJSGen Mekanism-steel-casing to TFMG-steel-frame migration.

This is deliberately an offline, out-of-place transformer.  It accepts the
canonical Default project, every review archive, and the matching review
ledger, validates their cross-file invariants, then writes a complete staged
copy to a new directory.  Inputs are never edited.

Only exact scalar references inside recipe ``slots`` and ``params`` are
eligible.  Recipe IDs, UIDs, comments, removals, and output slots are never
rewritten.  Encountering the retired ID in an output slot is a hard error.
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
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


OLD_ID = "mekanism:steel_casing"
NEW_ID = "tfmg:steel_frame"
DESIGN_FIELDS = ("type", "recipeId", "slots", "params")
HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
OUTPUT_SLOT_PATTERN = re.compile(r"(?:output|results?)\d*\Z", re.IGNORECASE)
OUTPUT_SLOT_NAMES = {"outitem", "outfluid", "returned_tool"}
VALID_STATUSES = {"approved", "rejected", "maybe", "disabled", "pending"}
REPORT_NAME = "steel_frame_transform_report.json"
BASE_MIGRATION_MANIFEST = "migration_manifest.json"

# The sole output producer is handled by an exact, user-reviewed retirement
# policy.  Any drift in any of these pins makes the migration stop.
PINNED_PRODUCER_RECIPE_ID = "industrial_colonies:mekanism/steel_casing"
PINNED_PRODUCER_UID = "8b681ccc-c90f-5613-887a-e8caf83fe732"
PINNED_PRODUCER_NOTE = (
    "TFMG steel frame should have this recipe but this item should be disabled"
    "(It redundant having multiple frames)"
)
PINNED_PRODUCER_HASH = (
    "sha256:99283eda7ded594483531bd23865b372731925a06457c96dae2cc3f833edf5d3"
)


class MigrationError(ValueError):
    """Raised when the migration cannot be proven safe."""


@dataclass(frozen=True)
class CardRef:
    project_name: str
    source_name: str
    archive_status: str | None
    before: dict[str, Any]
    after: dict[str, Any]
    replacements: int

    @property
    def recipe_id(self) -> str:
        return self.before["recipeId"]

    @property
    def uid(self) -> str:
        return self.before["uid"]


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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def design_hash(card: dict[str, Any]) -> str:
    """Match KjsGenRecipeReviewStore.cardSha256 exactly."""

    design = {
        field: card.get(field, {} if field in {"slots", "params"} else "")
        for field in DESIGN_FIELDS
    }
    canonical = json.dumps(
        design,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def normalized_project_name(value: str) -> str:
    return " ".join(value.replace("_", " ").lower().split())


def archive_status(project_name: str) -> str | None:
    normalized = normalized_project_name(project_name)
    return {
        "approved recipes": "approved",
        "rejected recipes": "rejected",
        "maybe recipes": "maybe",
        "deferred": "maybe",
        "deferred recipes": "maybe",
        "disabled recipes": "disabled",
    }.get(normalized)


def is_output_slot(name: str) -> bool:
    return bool(OUTPUT_SLOT_PATTERN.fullmatch(name)) or name.lower() in OUTPUT_SLOT_NAMES


def exact_occurrences(value: Any, target: str) -> int:
    if isinstance(value, str):
        return int(value == target)
    if isinstance(value, list):
        return sum(exact_occurrences(element, target) for element in value)
    if isinstance(value, dict):
        return sum(exact_occurrences(element, target) for element in value.values())
    return 0


def replace_exact(value: Any, old: str, new: str) -> tuple[Any, int]:
    if isinstance(value, str):
        return (new, 1) if value == old else (value, 0)
    if isinstance(value, list):
        changed: list[Any] = []
        replacements = 0
        for element in value:
            next_value, count = replace_exact(element, old, new)
            changed.append(next_value)
            replacements += count
        return changed, replacements
    if isinstance(value, dict):
        changed_dict: dict[str, Any] = {}
        replacements = 0
        for key, element in value.items():
            next_value, count = replace_exact(element, old, new)
            changed_dict[key] = next_value
            replacements += count
        return changed_dict, replacements
    return value, 0


def validate_card(raw: Any, label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise MigrationError(f"{label} must be an object")
    for field in ("uid", "type", "recipeId"):
        if not isinstance(raw.get(field), str) or not raw[field]:
            raise MigrationError(f"{label} has no {field}")
    for field in ("slots", "params"):
        if not isinstance(raw.get(field), dict):
            raise MigrationError(f"{label} has no {field} object")
    return raw


def transform_card(card: dict[str, Any], label: str) -> tuple[dict[str, Any], int]:
    slots = card["slots"]
    for slot_name, slot in slots.items():
        if is_output_slot(str(slot_name)) and exact_occurrences(slot, OLD_ID):
            if (
                card["recipeId"] == PINNED_PRODUCER_RECIPE_ID
                and card["uid"] == PINNED_PRODUCER_UID
            ):
                # The exact card and decision are pinned and validated later.  Its
                # producer snapshot is retired, not rewritten into a second recipe.
                return copy.deepcopy(card), 0
            raise MigrationError(
                f"{label} produces {OLD_ID} in output slot {slot_name!r}; "
                "output migration is intentionally unsupported"
            )

    transformed = copy.deepcopy(card)
    replacements = 0
    next_slots: dict[str, Any] = {}
    for slot_name, slot in slots.items():
        if is_output_slot(str(slot_name)):
            next_slots[slot_name] = copy.deepcopy(slot)
            continue
        next_slot, count = replace_exact(slot, OLD_ID, NEW_ID)
        next_slots[slot_name] = next_slot
        replacements += count
    transformed["slots"] = next_slots
    transformed["params"], param_count = replace_exact(card["params"], OLD_ID, NEW_ID)
    replacements += param_count

    if transformed["recipeId"] != card["recipeId"] or transformed["uid"] != card["uid"]:
        raise MigrationError(f"internal error: {label} changed recipe identity")
    for slot_name, before_slot in slots.items():
        if is_output_slot(str(slot_name)) and transformed["slots"][slot_name] != before_slot:
            raise MigrationError(f"internal error: {label} changed output slot {slot_name!r}")
    remaining = sum(
        exact_occurrences(slot, OLD_ID)
        for slot_name, slot in transformed["slots"].items()
        if not is_output_slot(str(slot_name))
    ) + exact_occurrences(transformed["params"], OLD_ID)
    if remaining:
        raise MigrationError(f"internal error: {label} retains {remaining} eligible references")
    return transformed, replacements


def validate_project(
    document: dict[str, Any],
    label: str,
    *,
    expect_default: bool,
) -> tuple[str, str | None, list[dict[str, Any]]]:
    name = document.get("name")
    if not isinstance(name, str) or not name.strip():
        raise MigrationError(f"{label} has no project name")
    normalized = normalized_project_name(name)
    status = archive_status(name)
    if expect_default:
        if normalized != "default":
            raise MigrationError(f"{label} must be the Default project, found {name!r}")
    elif status is None:
        raise MigrationError(f"{label} has unsupported review archive name {name!r}")

    recipes = document.get("recipes")
    removals = document.get("removals")
    if not isinstance(recipes, list):
        raise MigrationError(f"{label} must contain a recipes array")
    if not isinstance(removals, list):
        raise MigrationError(f"{label} must contain a removals array")

    seen_ids: set[str] = set()
    seen_uids: set[str] = set()
    cards: list[dict[str, Any]] = []
    for index, raw in enumerate(recipes):
        card = validate_card(raw, f"{label}.recipes[{index}]")
        if card["recipeId"] in seen_ids:
            raise MigrationError(f"{label} repeats recipe ID {card['recipeId']}")
        if card["uid"] in seen_uids:
            raise MigrationError(f"{label} repeats recipe UID {card['uid']}")
        seen_ids.add(card["recipeId"])
        seen_uids.add(card["uid"])
        cards.append(card)
    return name, status, cards


def validate_ledger(document: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    if document.get("schemaVersion") != 1:
        raise MigrationError(f"{label} must use schemaVersion 1")
    if normalized_project_name(str(document.get("project", ""))) != "default":
        raise MigrationError(f"{label} must belong to project default")
    reviews = document.get("reviews")
    if not isinstance(reviews, dict):
        raise MigrationError(f"{label} must contain a reviews object")
    for recipe_id, record in reviews.items():
        if not isinstance(recipe_id, str) or not recipe_id or not isinstance(record, dict):
            raise MigrationError(f"{label} contains an invalid review entry")
        if not isinstance(record.get("uid"), str) or not record["uid"]:
            raise MigrationError(f"review {recipe_id} has no UID")
        if record.get("status") not in VALID_STATUSES:
            raise MigrationError(f"review {recipe_id} has invalid status {record.get('status')!r}")
        digest = record.get("cardSha256")
        if not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest):
            raise MigrationError(f"review {recipe_id} has invalid cardSha256")
    return reviews


def transform_documents(
    default_document: dict[str, Any],
    archive_documents: list[dict[str, Any]],
    ledger_document: dict[str, Any],
    *,
    default_source_name: str = "default.json",
    archive_source_names: list[str] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Transform validated in-memory documents and return staged copies plus a report."""

    archive_source_names = archive_source_names or [
        f"archive-{index}.json" for index in range(len(archive_documents))
    ]
    if len(archive_source_names) != len(archive_documents):
        raise MigrationError("archive source-name count does not match archive document count")

    project_specs: list[tuple[dict[str, Any], str, bool]] = [
        (default_document, default_source_name, True)
    ] + [
        (document, source_name, False)
        for document, source_name in zip(archive_documents, archive_source_names)
    ]

    transformed_documents: list[dict[str, Any]] = []
    card_refs: list[CardRef] = []
    archive_by_status: dict[str, list[CardRef]] = {}
    seen_archive_statuses: set[str] = set()
    archive_document_index: dict[str, int] = {}

    for document, source_name, expect_default in project_specs:
        name, status, cards = validate_project(
            document, source_name, expect_default=expect_default
        )
        if status is not None:
            if status in seen_archive_statuses:
                raise MigrationError(
                    f"multiple archives represent status {status!r}; provide exactly one"
                )
            seen_archive_statuses.add(status)
            archive_document_index[status] = len(transformed_documents)

        transformed_document = copy.deepcopy(document)
        next_cards: list[dict[str, Any]] = []
        for index, card in enumerate(cards):
            transformed_card, replacements = transform_card(
                card, f"{source_name}.recipes[{index}]"
            )
            next_cards.append(transformed_card)
            ref = CardRef(
                project_name=name,
                source_name=source_name,
                archive_status=status,
                before=card,
                after=transformed_card,
                replacements=replacements,
            )
            card_refs.append(ref)
            if status is not None:
                archive_by_status.setdefault(status, []).append(ref)
        transformed_document["recipes"] = next_cards
        transformed_documents.append(transformed_document)

        if transformed_document.get("removals") != document.get("removals"):
            raise MigrationError(f"internal error: {source_name} removals changed")

    reviews = validate_ledger(ledger_document, "review ledger")
    statuses_present = {
        record["status"] for record in reviews.values() if record["status"] != "pending"
    }
    missing_archives = sorted(statuses_present - seen_archive_statuses)
    if missing_archives:
        raise MigrationError(
            "missing review archive(s) for ledger status: " + ", ".join(missing_archives)
        )

    candidates_by_key: dict[tuple[str, str], list[CardRef]] = {}
    for ref in card_refs:
        candidates_by_key.setdefault((ref.recipe_id, ref.uid), []).append(ref)

    # Every archive is a materialized ledger decision, not an independent recipe source.
    for status, refs in archive_by_status.items():
        for ref in refs:
            record = reviews.get(ref.recipe_id)
            if record is None:
                raise MigrationError(
                    f"archive {ref.source_name} card {ref.recipe_id} has no ledger decision"
                )
            if record["status"] != status:
                raise MigrationError(
                    f"archive {ref.source_name} card {ref.recipe_id} represents {status}, "
                    f"but ledger status is {record['status']}"
                )
            if record["uid"] != ref.uid:
                raise MigrationError(f"archive UID mismatch for {ref.recipe_id}")
            if record["cardSha256"] != design_hash(ref.before):
                raise MigrationError(f"archive fingerprint mismatch for {ref.recipe_id}")

    producer_record = reviews.get(PINNED_PRODUCER_RECIPE_ID)
    if producer_record is None:
        raise MigrationError("pinned Mekanism steel-casing producer has no ledger decision")
    producer_expected = {
        "uid": PINNED_PRODUCER_UID,
        "status": "rejected",
        "reason": "manual",
        "note": PINNED_PRODUCER_NOTE,
        "cardSha256": PINNED_PRODUCER_HASH,
    }
    for field, expected in producer_expected.items():
        if producer_record.get(field) != expected:
            raise MigrationError(
                f"pinned producer ledger {field} drifted: expected {expected!r}, "
                f"found {producer_record.get(field)!r}"
            )
    producer_refs = [
        ref
        for ref in card_refs
        if ref.recipe_id == PINNED_PRODUCER_RECIPE_ID
        and ref.uid == PINNED_PRODUCER_UID
    ]
    default_producers = [ref for ref in producer_refs if ref.archive_status is None]
    rejected_producers = [ref for ref in producer_refs if ref.archive_status == "rejected"]
    other_producers = [
        ref
        for ref in producer_refs
        if ref.archive_status not in {None, "rejected"}
    ]
    if len(default_producers) != 1 or len(rejected_producers) != 1 or other_producers:
        raise MigrationError(
            "pinned producer must appear exactly once in Default and Rejected only"
        )
    if default_producers[0].before != rejected_producers[0].before:
        raise MigrationError("pinned producer Default and Rejected snapshots differ")
    if design_hash(default_producers[0].before) != PINNED_PRODUCER_HASH:
        raise MigrationError("pinned producer card fingerprint drifted")
    producer_output_occurrences = sum(
        exact_occurrences(slot, OLD_ID)
        for slot_name, slot in default_producers[0].before["slots"].items()
        if is_output_slot(str(slot_name))
    )
    producer_input_occurrences = sum(
        exact_occurrences(slot, OLD_ID)
        for slot_name, slot in default_producers[0].before["slots"].items()
        if not is_output_slot(str(slot_name))
    ) + exact_occurrences(default_producers[0].before["params"], OLD_ID)
    if producer_output_occurrences != 1 or producer_input_occurrences != 0:
        raise MigrationError(
            "pinned producer must contain exactly one old-ID output and no old-ID inputs"
        )

    transformed_ledger = copy.deepcopy(ledger_document)
    next_reviews = transformed_ledger["reviews"]
    updated_reviews: list[dict[str, Any]] = []
    statuses_before = Counter(record["status"] for record in reviews.values())

    for recipe_id, record in reviews.items():
        key = (recipe_id, record["uid"])
        candidates = candidates_by_key.get(key, [])
        matching = [ref for ref in candidates if design_hash(ref.before) == record["cardSha256"]]
        affected_candidates = [ref for ref in candidates if ref.replacements]
        if affected_candidates and not matching:
            raise MigrationError(
                f"review {recipe_id} has affected cards but its reviewed fingerprint is not "
                "represented by Default or the supplied archive"
            )
        affected_matching = [ref for ref in matching if ref.replacements]
        if not affected_matching:
            continue
        next_hashes = {design_hash(ref.after) for ref in affected_matching}
        if len(next_hashes) != 1:
            raise MigrationError(
                f"review {recipe_id} resolves to conflicting transformed fingerprints"
            )
        old_hash = record["cardSha256"]
        new_hash = next_hashes.pop()
        before_without_hash = copy.deepcopy(record)
        before_without_hash.pop("cardSha256", None)
        next_reviews[recipe_id]["cardSha256"] = new_hash
        after_without_hash = copy.deepcopy(next_reviews[recipe_id])
        after_without_hash.pop("cardSha256", None)
        if before_without_hash != after_without_hash:
            raise MigrationError(f"internal error: review metadata changed for {recipe_id}")
        updated_reviews.append(
            {
                "recipeId": recipe_id,
                "uid": record["uid"],
                "status": record["status"],
                "oldCardSha256": old_hash,
                "newCardSha256": new_hash,
            }
        )

    # Apply the one explicitly reviewed semantic transition.  The producer card
    # remains byte-for-byte the same in Default; its archive snapshot moves from
    # Rejected to Disabled, which prevents export while retaining audit history.
    rejected_document = transformed_documents[archive_document_index["rejected"]]
    disabled_document = transformed_documents[archive_document_index["disabled"]]
    rejected_before_count = len(rejected_document["recipes"])
    disabled_before_count = len(disabled_document["recipes"])
    rejected_document["recipes"] = [
        card
        for card in rejected_document["recipes"]
        if not (
            card["recipeId"] == PINNED_PRODUCER_RECIPE_ID
            and card["uid"] == PINNED_PRODUCER_UID
        )
    ]
    if len(rejected_document["recipes"]) != rejected_before_count - 1:
        raise MigrationError("failed to remove exactly one pinned producer from Rejected")
    if any(
        card["recipeId"] == PINNED_PRODUCER_RECIPE_ID
        or card["uid"] == PINNED_PRODUCER_UID
        for card in disabled_document["recipes"]
    ):
        raise MigrationError("Disabled already contains the pinned producer identity")
    disabled_document["recipes"].append(copy.deepcopy(rejected_producers[0].after))
    if len(disabled_document["recipes"]) != disabled_before_count + 1:
        raise MigrationError("failed to append exactly one pinned producer to Disabled")
    next_reviews[PINNED_PRODUCER_RECIPE_ID]["status"] = "disabled"
    next_reviews[PINNED_PRODUCER_RECIPE_ID]["reason"] = "redundant_mechanic"
    if next_reviews[PINNED_PRODUCER_RECIPE_ID]["note"] != PINNED_PRODUCER_NOTE:
        raise MigrationError("internal error: pinned producer note changed")
    if next_reviews[PINNED_PRODUCER_RECIPE_ID]["cardSha256"] != PINNED_PRODUCER_HASH:
        raise MigrationError("internal error: pinned producer fingerprint changed")

    statuses_after = Counter(record["status"] for record in next_reviews.values())
    expected_statuses_after = statuses_before.copy()
    expected_statuses_after["rejected"] -= 1
    expected_statuses_after["disabled"] += 1
    if expected_statuses_after["rejected"] == 0:
        del expected_statuses_after["rejected"]
    if statuses_after != expected_statuses_after:
        raise MigrationError(
            "internal error: review status counts changed beyond the pinned transition"
        )

    # Revalidate every transformed archive against the transformed ledger,
    # including the Rejected -> Disabled producer move.
    for status, document_index in archive_document_index.items():
        seen_ids: set[str] = set()
        seen_uids: set[str] = set()
        for card in transformed_documents[document_index]["recipes"]:
            recipe_id = card["recipeId"]
            uid = card["uid"]
            if recipe_id in seen_ids or uid in seen_uids:
                raise MigrationError(f"transformed {status} archive contains duplicates")
            seen_ids.add(recipe_id)
            seen_uids.add(uid)
            record = next_reviews.get(recipe_id)
            if record is None or record["status"] != status or record["uid"] != uid:
                raise MigrationError(
                    f"transformed {status} archive decision mismatch for {recipe_id}"
                )
            if record["cardSha256"] != design_hash(card):
                raise MigrationError(
                    f"transformed archive fingerprint mismatch for {recipe_id}"
                )

    changed_refs = [ref for ref in card_refs if ref.replacements]
    status_before_by_id = {
        recipe_id: record["status"] for recipe_id, record in reviews.items()
    }
    status_after_by_id = {
        recipe_id: record["status"] for recipe_id, record in next_reviews.items()
    }
    changed_card_snapshots = [
        {
            "changeType": "reference_replacement",
            "sourceName": ref.source_name,
            "project": ref.project_name,
            "recipeId": ref.recipe_id,
            "uid": ref.uid,
            "ledgerStatusBefore": status_before_by_id.get(ref.recipe_id),
            "ledgerStatusAfter": status_after_by_id.get(ref.recipe_id),
            "replacements": ref.replacements,
            "oldCardSha256": design_hash(ref.before),
            "newCardSha256": design_hash(ref.after),
        }
        for ref in changed_refs
    ]
    changed_card_snapshots.append(
        {
            "changeType": "archive_transition",
            "sourceName": rejected_producers[0].source_name,
            "destinationProject": disabled_document["name"],
            "project": rejected_producers[0].project_name,
            "recipeId": PINNED_PRODUCER_RECIPE_ID,
            "uid": PINNED_PRODUCER_UID,
            "ledgerStatusBefore": "rejected",
            "ledgerStatusAfter": "disabled",
            "reasonBefore": "manual",
            "reasonAfter": "redundant_mechanic",
            "replacements": 0,
            "oldCardSha256": PINNED_PRODUCER_HASH,
            "newCardSha256": PINNED_PRODUCER_HASH,
        }
    )
    changed_card_snapshots.sort(
        key=lambda row: (row["recipeId"], row["changeType"], row["sourceName"])
    )
    all_changed_recipe_ids = sorted(
        {ref.recipe_id for ref in changed_refs} | {PINNED_PRODUCER_RECIPE_ID}
    )
    report = {
        "schemaVersion": 1,
        "operation": "replace_mekanism_steel_casing_with_tfmg_steel_frame",
        "oldId": OLD_ID,
        "newId": NEW_ID,
        "projects": [
            {
                "sourceName": source_name,
                "project": transformed["name"],
                "recipeCountBefore": len(original["recipes"]),
                "recipeCountAfter": len(transformed["recipes"]),
                "changedCards": sum(
                    1 for ref in card_refs if ref.source_name == source_name and ref.replacements
                ),
                "replacements": sum(
                    ref.replacements
                    for ref in card_refs
                    if ref.source_name == source_name
                ),
            }
            for transformed, (original, source_name, _) in zip(
                transformed_documents, project_specs
            )
        ],
        "changedCards": len(changed_card_snapshots),
        "referenceChangedCardSnapshots": len(changed_refs),
        "replacements": sum(ref.replacements for ref in changed_refs),
        "changedRecipeIds": all_changed_recipe_ids,
        "referenceChangedRecipeIds": sorted({ref.recipe_id for ref in changed_refs}),
        "changedCardSnapshots": changed_card_snapshots,
        "ledgerHashesUpdated": len(updated_reviews),
        "updatedReviews": sorted(updated_reviews, key=lambda row: row["recipeId"]),
        "reviewTransitions": [
            {
                "recipeId": PINNED_PRODUCER_RECIPE_ID,
                "uid": PINNED_PRODUCER_UID,
                "statusBefore": "rejected",
                "statusAfter": "disabled",
                "reasonBefore": "manual",
                "reasonAfter": "redundant_mechanic",
                "note": PINNED_PRODUCER_NOTE,
                "cardSha256": PINNED_PRODUCER_HASH,
                "sourceArchive": rejected_document["name"],
                "destinationArchive": disabled_document["name"],
            }
        ],
        "reviewStatusCountsBefore": dict(sorted(statuses_before.items())),
        "reviewStatusCounts": dict(sorted(statuses_after.items())),
    }
    return (
        transformed_documents[0],
        transformed_documents[1:],
        transformed_ledger,
        report,
    )


def stage_migration(
    default_path: Path,
    archive_paths: list[Path],
    ledger_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    paths = [default_path, *archive_paths, ledger_path]
    resolved_paths = [path.resolve() for path in paths]
    for path in resolved_paths:
        if not path.is_file():
            raise MigrationError(f"input file does not exist: {path}")
    basenames = [path.name.lower() for path in resolved_paths]
    if len(basenames) != len(set(basenames)):
        raise MigrationError("input basenames must be unique for out-of-place staging")

    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise MigrationError(f"output directory already exists: {output_dir}")
    if any(output_dir == path.parent for path in resolved_paths):
        raise MigrationError("output directory may not be an input directory")

    default_document = load_json(resolved_paths[0])
    archive_documents = [load_json(path) for path in resolved_paths[1:-1]]
    ledger_document = load_json(resolved_paths[-1])
    default_after, archives_after, ledger_after, report = transform_documents(
        default_document,
        archive_documents,
        ledger_document,
        default_source_name=resolved_paths[0].name,
        archive_source_names=[path.name for path in resolved_paths[1:-1]],
    )
    input_rows = [
        {"fileName": path.name, "path": str(path), "sha256": file_sha256(path)}
        for path in resolved_paths
    ]
    report["inputs"] = input_rows

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=str(output_dir.parent))
    )
    try:
        documents = [default_after, *archives_after, ledger_after]
        for source, document in zip(resolved_paths, documents):
            (temporary / source.name).write_bytes(encoded(document))
        report["artifacts"] = [
            {
                "fileName": source.name,
                "inputPath": str(source),
                "inputSha256": input_row["sha256"],
                "stagedPath": str(output_dir / source.name),
                "stagedSha256": file_sha256(temporary / source.name),
            }
            for source, input_row in zip(resolved_paths, input_rows)
        ]

        source_parents = {path.parent for path in resolved_paths}
        base_manifest = None
        if len(source_parents) == 1:
            candidate = next(iter(source_parents)) / BASE_MIGRATION_MANIFEST
            if candidate.is_file() and candidate.resolve() not in resolved_paths:
                base_manifest = candidate.resolve()
                shutil.copyfile(base_manifest, temporary / BASE_MIGRATION_MANIFEST)
                report["baseMigrationManifest"] = {
                    "inputPath": str(base_manifest),
                    "inputSha256": file_sha256(base_manifest),
                    "stagedPath": str(output_dir / BASE_MIGRATION_MANIFEST),
                    "stagedSha256": file_sha256(temporary / BASE_MIGRATION_MANIFEST),
                }
        (temporary / REPORT_NAME).write_bytes(encoded(report))
        os.replace(temporary, output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return report


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--default", type=Path, required=True, help="Default KJSGen JSON")
    parser.add_argument(
        "--archive",
        type=Path,
        action="append",
        default=[],
        help="Review archive JSON; repeat for Approved/Rejected/Deferred/Disabled",
    )
    parser.add_argument("--ledger", type=Path, required=True, help="Review ledger JSON")
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="New, non-existing directory that receives the staged copies",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    report = stage_migration(args.default, args.archive, args.ledger, args.output_dir)
    print(
        "Staged TFMG steel-frame migration: "
        f"{report['changedCards']} card snapshots, "
        f"{report['replacements']} exact references, "
        f"{report['ledgerHashesUpdated']} ledger fingerprints updated."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MigrationError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
