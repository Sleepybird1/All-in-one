#!/usr/bin/env python3
"""Build a clean KJSGen review batch from final in-game decisions.

The completed review ledger is authoritative.  Exact approved snapshots are
retained, unchanged rejected designs are omitted, and genuinely new or revised
source cards become the next pending queue.  Matching is deliberately both by
recipe ID and by concrete output so a renamed recipe cannot silently replace
an approved design or resurrect an unchanged rejected design.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Iterable


OUTPUT_SLOT = re.compile(r"^(?:output|results?)\d*$")
VALID_REVIEW_STATUSES = {"approved", "rejected"}
DESIGN_FIELDS = ("type", "recipeId", "slots", "params")
SEMANTIC_FIELDS = ("type", "slots", "params")


class ReconcileError(ValueError):
    """Raised when review inputs cannot be reconciled without ambiguity."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"),
                           object_pairs_hook=OrderedDict)
    except OSError as exc:
        raise ReconcileError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ReconcileError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReconcileError(f"{path} must contain a JSON object")
    return value


def canonical_hash(card: dict[str, Any], fields: tuple[str, ...]) -> str:
    payload = {
        field: card.get(field, {} if field in {"slots", "params"} else "")
        for field in fields
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def design_hash(card: dict[str, Any]) -> str:
    return canonical_hash(card, DESIGN_FIELDS)


def semantic_hash(card: dict[str, Any]) -> str:
    """Hash manufacturing semantics while ignoring a recipe-ID-only rename."""

    return canonical_hash(card, SEMANTIC_FIELDS)


def require_array(document: dict[str, Any], key: str, label: str) -> list[Any]:
    value = document.get(key)
    if not isinstance(value, list):
        raise ReconcileError(f"{label} must contain a {key} array")
    return value


def validate_card(card: Any, label: str, *, allow_blank_id: bool = False) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise ReconcileError(f"{label} must be an object")
    uid = card.get("uid")
    recipe_id = card.get("recipeId")
    if not isinstance(uid, str) or not uid:
        raise ReconcileError(f"{label} has no UID")
    if not allow_blank_id and (not isinstance(recipe_id, str) or not recipe_id):
        raise ReconcileError(f"{label} has no recipe ID")
    if not isinstance(card.get("type"), str) or not card["type"]:
        raise ReconcileError(f"{label} has no recipe type")
    if not isinstance(card.get("slots"), dict):
        raise ReconcileError(f"{label} has no slots object")
    if not isinstance(card.get("params"), dict):
        raise ReconcileError(f"{label} has no params object")
    return card


def indexed_cards(document: dict[str, Any], label: str) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    cards: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    seen_uids: set[str] = set()
    for index, raw in enumerate(require_array(document, "recipes", label)):
        card = validate_card(raw, f"{label}.recipes[{index}]")
        recipe_id = card["recipeId"]
        uid = card["uid"]
        if recipe_id in by_id:
            raise ReconcileError(f"duplicate recipe ID in {label}: {recipe_id}")
        if uid in seen_uids:
            raise ReconcileError(f"duplicate recipe UID in {label}: {uid}")
        by_id[recipe_id] = card
        seen_uids.add(uid)
        cards.append(card)
    return cards, by_id


def output_tokens(card: dict[str, Any]) -> frozenset[str]:
    result: set[str] = set()
    for name, slot in card.get("slots", {}).items():
        if not (OUTPUT_SLOT.fullmatch(str(name)) or name in {"outItem", "outFluid"}):
            continue
        if not isinstance(slot, dict):
            continue
        kind = slot.get("kind")
        identifier = slot.get("id")
        if kind in {"ITEM", "FLUID", "CHEMICAL"} and isinstance(identifier, str) and identifier:
            result.add(f"{kind}:{identifier}")
    if not result:
        raise ReconcileError(f"recipe {card.get('recipeId')} has no concrete output slot")
    return frozenset(result)


def review_records(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if document.get("schemaVersion") != 1 or document.get("project") != "default":
        raise ReconcileError("review ledger must be schemaVersion 1 for project default")
    raw_reviews = document.get("reviews")
    if not isinstance(raw_reviews, dict):
        raise ReconcileError("review ledger must contain a reviews object")
    result: dict[str, dict[str, Any]] = {}
    for recipe_id, record in raw_reviews.items():
        if not isinstance(recipe_id, str) or not recipe_id or not isinstance(record, dict):
            raise ReconcileError("review entries must map nonblank recipe IDs to objects")
        if record.get("status") not in VALID_REVIEW_STATUSES:
            raise ReconcileError(
                f"review {recipe_id} has unsupported status {record.get('status')!r}"
            )
        if not isinstance(record.get("uid"), str) or not record["uid"]:
            raise ReconcileError(f"review {recipe_id} has no UID")
        digest = record.get("cardSha256")
        if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ReconcileError(f"review {recipe_id} has an invalid design hash")
        result[recipe_id] = record
    return result


def removal_index(removals: list[Any], label: str) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    ordered: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    seen_uids: set[str] = set()
    for index, raw in enumerate(removals):
        if not isinstance(raw, dict):
            raise ReconcileError(f"{label}[{index}] must be an object")
        uid = raw.get("uid")
        recipe_id = raw.get("recipeId")
        if not isinstance(uid, str) or not uid:
            raise ReconcileError(f"{label}[{index}] has no UID")
        if not isinstance(recipe_id, str) or not recipe_id:
            raise ReconcileError(f"{label}[{index}] has no recipe ID")
        if recipe_id in by_id:
            raise ReconcileError(f"duplicate removal recipe ID in {label}: {recipe_id}")
        if uid in seen_uids:
            raise ReconcileError(f"duplicate removal UID in {label}: {uid}")
        ordered.append(raw)
        by_id[recipe_id] = raw
        seen_uids.add(uid)
    return ordered, by_id


def removal_covers_output(removal_id: str, token: str) -> bool:
    kind, output_id = token.split(":", 1)
    if kind != "ITEM" or ":" not in output_id or ":" not in removal_id:
        return False
    output_namespace, output_path = output_id.split(":", 1)
    removal_namespace, removal_path = removal_id.split(":", 1)
    return (
        output_namespace == removal_namespace
        and removal_path.rsplit("/", 1)[-1] == output_path.rsplit("/", 1)[-1]
    )


def unique_strings(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw)
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def removable_ids_owned_only_by_rejected(
    manifest: dict[str, Any], rejected_recipe_ids: set[str]
) -> set[str]:
    """Return exact removals with no owner outside unchanged rejected cards."""

    recipes = require_array(manifest, "recipes", "next manifest")
    owners: dict[str, set[str]] = defaultdict(set)
    for index, raw in enumerate(recipes):
        if not isinstance(raw, dict):
            raise ReconcileError(f"next manifest recipes[{index}] must be an object")
        recipe_id = raw.get("id")
        removals = raw.get("remove", [])
        if not isinstance(recipe_id, str) or not recipe_id:
            raise ReconcileError(f"next manifest recipes[{index}] has no ID")
        if not isinstance(removals, list):
            raise ReconcileError(f"next manifest recipe {recipe_id} remove must be an array")
        for removal_id in removals:
            if not isinstance(removal_id, str) or not removal_id:
                raise ReconcileError(f"next manifest recipe {recipe_id} has an invalid removal")
            owners[removal_id].add(recipe_id)
    additional = manifest.get("additional_removals", [])
    if not isinstance(additional, list):
        raise ReconcileError("next manifest additional_removals must be an array")
    for removal_id in additional:
        if not isinstance(removal_id, str) or not removal_id:
            raise ReconcileError("next manifest contains an invalid additional removal")
        owners[removal_id].add("<additional_removals>")
    return {
        removal_id
        for removal_id, removal_owners in owners.items()
        if removal_owners and removal_owners.issubset(rejected_recipe_ids)
    }


def reconcile(
    live_project: dict[str, Any],
    old_baseline: dict[str, Any],
    approved_project: dict[str, Any],
    ledger: dict[str, Any],
    next_managed: dict[str, Any],
    next_manifest: dict[str, Any],
    previous_reviewed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    live_entries = require_array(live_project, "recipes", "live project")
    live_recipe_document = copy.deepcopy(live_project)
    live_recipe_document["recipes"] = []
    draft_cards: list[dict[str, Any]] = []
    for index, raw in enumerate(live_entries):
        if not isinstance(raw, dict):
            raise ReconcileError(f"live project.recipes[{index}] must be an object")
        if not raw.get("recipeId"):
            if not raw.get("uid"):
                raise ReconcileError(
                    f"live project.recipes[{index}] has neither a recipe ID nor a UID"
                )
            draft_cards.append(copy.deepcopy(raw))
            continue
        live_recipe_document["recipes"].append(raw)
    live_cards, live_by_id = indexed_cards(live_recipe_document, "live project")
    approved_cards, approved_archive_by_id = indexed_cards(
        approved_project, "approved project"
    )
    source_cards, _ = indexed_cards(next_managed, "next managed source")
    reviews = review_records(ledger)

    reviewed_cards: dict[str, dict[str, Any]] = {}
    approved_by_id: dict[str, dict[str, Any]] = {}
    rejected_by_id: dict[str, dict[str, Any]] = {}
    for recipe_id, record in reviews.items():
        live_card = live_by_id.get(recipe_id)
        if live_card is None:
            raise ReconcileError(f"reviewed recipe is missing from live project: {recipe_id}")
        if live_card["uid"] != record["uid"]:
            raise ReconcileError(f"review UID no longer matches live card: {recipe_id}")
        if design_hash(live_card) != record["cardSha256"]:
            raise ReconcileError(f"reviewed live card changed after its decision: {recipe_id}")
        reviewed_cards[recipe_id] = live_card
        if record["status"] == "approved":
            snapshot = approved_archive_by_id.get(recipe_id)
            if snapshot is None:
                raise ReconcileError(f"approved snapshot is missing: {recipe_id}")
            if snapshot["uid"] != record["uid"] or design_hash(snapshot) != record["cardSha256"]:
                raise ReconcileError(f"approved snapshot is stale or mismatched: {recipe_id}")
            approved_by_id[recipe_id] = copy.deepcopy(snapshot)
        else:
            rejected_by_id[recipe_id] = live_card

    archive_extras = [card["recipeId"] for card in approved_cards
                      if card["recipeId"] not in approved_by_id]

    approved_outputs: dict[str, str] = {}
    rejected_outputs: dict[str, str] = {}
    for recipe_id, card in approved_by_id.items():
        for token in output_tokens(card):
            previous = approved_outputs.setdefault(token, recipe_id)
            if previous != recipe_id:
                raise ReconcileError(
                    f"approved recipes {previous} and {recipe_id} share output {token}"
                )
    for recipe_id, card in rejected_by_id.items():
        for token in output_tokens(card):
            previous = rejected_outputs.setdefault(token, recipe_id)
            if previous != recipe_id:
                raise ReconcileError(
                    f"rejected recipes {previous} and {recipe_id} share output {token}"
                )
            if token in approved_outputs:
                raise ReconcileError(
                    f"approved {approved_outputs[token]} and rejected {recipe_id} share output {token}"
                )

    pending_cards: list[dict[str, Any]] = []
    classifications: dict[str, list[str]] = defaultdict(list)
    for card in source_cards:
        recipe_id = card["recipeId"]
        tokens = output_tokens(card)
        approved_matches = {
            approved_by_id[recipe_id]["recipeId"]
            for _ in [0]
            if recipe_id in approved_by_id
        }
        approved_matches.update(
            approved_outputs[token] for token in tokens if token in approved_outputs
        )
        if approved_matches:
            if len(approved_matches) != 1:
                raise ReconcileError(
                    f"source recipe {recipe_id} ambiguously matches approvals {sorted(approved_matches)}"
                )
            approved_id = next(iter(approved_matches))
            exact = recipe_id == approved_id and design_hash(card) == design_hash(
                approved_by_id[approved_id]
            )
            key = "approved_source_exact" if exact else "approved_source_superseded"
            classifications[key].append(recipe_id)
            continue

        rejected_matches = {recipe_id} if recipe_id in rejected_by_id else set()
        rejected_matches.update(
            rejected_outputs[token] for token in tokens if token in rejected_outputs
        )
        if rejected_matches:
            if len(rejected_matches) != 1:
                raise ReconcileError(
                    f"source recipe {recipe_id} ambiguously matches rejections {sorted(rejected_matches)}"
                )
            rejected_id = next(iter(rejected_matches))
            rejected_card = rejected_by_id[rejected_id]
            unchanged = (
                recipe_id == rejected_id
                and design_hash(card) == design_hash(rejected_card)
            ) or (
                recipe_id != rejected_id
                and semantic_hash(card) == semantic_hash(rejected_card)
            )
            if unchanged:
                classifications["rejected_source_unchanged"].append(recipe_id)
                continue
            classifications["rejected_source_redesigned"].append(recipe_id)
        else:
            classifications["new_source"].append(recipe_id)
        pending_cards.append(copy.deepcopy(card))

    selected_cards = pending_cards + [copy.deepcopy(card) for card in approved_by_id.values()]
    selected_ids: set[str] = set()
    selected_uids: set[str] = set()
    selected_outputs: dict[str, str] = {}
    for card in selected_cards:
        recipe_id = card["recipeId"]
        uid = card["uid"]
        if recipe_id in selected_ids:
            raise ReconcileError(f"reconciled project duplicates recipe ID {recipe_id}")
        if uid in selected_uids:
            raise ReconcileError(f"reconciled project duplicates recipe UID {uid}")
        selected_ids.add(recipe_id)
        selected_uids.add(uid)
        for token in output_tokens(card):
            previous = selected_outputs.setdefault(token, recipe_id)
            if previous != recipe_id:
                raise ReconcileError(
                    f"reconciled recipes {previous} and {recipe_id} share output {token}"
                )

    review_ui_counts = OrderedDict((
        ("approved", 0),
        ("rejected", 0),
        ("stale", 0),
        ("unreviewed", 0),
    ))
    for card in selected_cards:
        record = reviews.get(card["recipeId"])
        if record is None:
            review_ui_counts["unreviewed"] += 1
        elif design_hash(card) != record["cardSha256"]:
            review_ui_counts["stale"] += 1
        else:
            review_ui_counts[record["status"]] += 1
    if review_ui_counts["rejected"]:
        raise ReconcileError(
            "reconciled project still contains an unchanged rejected design"
        )

    source_removals, source_removals_by_id = removal_index(
        require_array(next_managed, "removals", "next managed source"),
        "next managed source removals",
    )
    unchanged_rejected_ids = set(classifications.get("rejected_source_unchanged", []))
    dropped_removal_ids = removable_ids_owned_only_by_rejected(
        next_manifest, unchanged_rejected_ids
    )
    source_removals = [
        removal for removal in source_removals
        if removal["recipeId"] not in dropped_removal_ids
    ]
    source_removals_by_id = {
        removal_id: removal
        for removal_id, removal in source_removals_by_id.items()
        if removal_id not in dropped_removal_ids
    }
    old_baseline_removals, _ = removal_index(
        require_array(old_baseline, "removals", "old baseline"),
        "old baseline removals",
    )
    selected_removals = [copy.deepcopy(removal) for removal in source_removals]
    selected_removal_ids = set(source_removals_by_id)
    retained_legacy_removals: list[str] = []
    for approved_card in approved_by_id.values():
        for token in output_tokens(approved_card):
            if any(removal_covers_output(removal_id, token)
                   for removal_id in selected_removal_ids):
                continue
            candidates = [
                removal for removal in old_baseline_removals
                if removal["recipeId"] not in selected_removal_ids
                and removal_covers_output(removal["recipeId"], token)
            ]
            for removal in candidates:
                selected_removals.append(copy.deepcopy(removal))
                selected_removal_ids.add(removal["recipeId"])
                retained_legacy_removals.append(removal["recipeId"])

    selected_removal_uids = {removal["uid"] for removal in selected_removals}
    if len(selected_removal_uids) != len(selected_removals):
        raise ReconcileError("reconciled removals contain duplicate UIDs")

    old_baseline_recipe_uids = [
        str(card.get("uid"))
        for card in require_array(old_baseline, "recipes", "old baseline")
        if isinstance(card, dict) and card.get("uid")
    ]
    old_baseline_removal_uids = [
        str(removal.get("uid"))
        for removal in require_array(old_baseline, "removals", "old baseline")
        if isinstance(removal, dict) and removal.get("uid")
    ]
    predecessor_recipe_uids = (
        [
            str(card.get("uid"))
            for card in require_array(
                previous_reviewed, "recipes", "previous reviewed batch"
            )
            if isinstance(card, dict) and card.get("uid")
        ]
        if previous_reviewed is not None
        else []
    )
    predecessor_removal_uids = (
        [
            str(removal.get("uid"))
            for removal in require_array(
                previous_reviewed, "removals", "previous reviewed batch"
            )
            if isinstance(removal, dict) and removal.get("uid")
        ]
        if previous_reviewed is not None
        else []
    )
    retired_recipe_uids = unique_strings([
        *next_managed.get("retiredRecipeUids", []),
        *old_baseline.get("retiredRecipeUids", []),
        *old_baseline_recipe_uids,
        *predecessor_recipe_uids,
    ])
    retired_recipe_uids = [uid for uid in retired_recipe_uids if uid not in selected_uids]
    retired_removal_uids = unique_strings([
        *next_managed.get("retiredRemovalUids", []),
        *old_baseline.get("retiredRemovalUids", []),
        *old_baseline_removal_uids,
        *predecessor_removal_uids,
    ])
    retired_removal_uids = [
        uid for uid in retired_removal_uids if uid not in selected_removal_uids
    ]

    managed = OrderedDict((
        ("schema", 1),
        ("project", "default"),
        ("recipes", selected_cards),
        ("removals", selected_removals),
        ("retiredRecipeUids", retired_recipe_uids),
        ("retiredRemovalUids", retired_removal_uids),
    ))
    project = copy.deepcopy(live_project)
    project["recipes"] = copy.deepcopy(selected_cards)
    project["removals"] = copy.deepcopy(selected_removals)
    clean_approved = copy.deepcopy(approved_project)
    clean_approved["recipes"] = [copy.deepcopy(card) for card in approved_by_id.values()]
    clean_approved["removals"] = []

    acceptance_entries: list[OrderedDict[str, Any]] = []
    for recipe_id, record in reviews.items():
        acceptance_entries.append(OrderedDict((
            ("recipeId", recipe_id),
            ("decision", copy.deepcopy(record)),
            ("card", copy.deepcopy(reviewed_cards[recipe_id])),
        )))
    acceptance = OrderedDict((
        ("schemaVersion", 1),
        ("project", "default"),
        ("reviewed", len(acceptance_entries)),
        ("approved", len(approved_by_id)),
        ("rejected", len(rejected_by_id)),
        ("entries", acceptance_entries),
    ))
    ownership_manifest = OrderedDict((
        ("schemaVersion", 1),
        ("project", "default"),
        ("recipes", [
            OrderedDict((("id", card["recipeId"]), ("exclusive_output", True)))
            for card in selected_cards
            if any(token.startswith("ITEM:") for token in output_tokens(card))
        ]),
    ))

    report = OrderedDict((
        ("schema", 1),
        ("reviewed", len(reviews)),
        ("approved", len(approved_by_id)),
        ("rejected", len(rejected_by_id)),
        ("archiveExtrasRemoved", archive_extras),
        ("oldLiveRecipesRemoved", len(live_entries) - len(approved_by_id)),
        ("draftsRemoved", len(draft_cards)),
        ("sourceRecipes", len(source_cards)),
        ("nextPending", len(pending_cards)),
        ("nextManaged", len(selected_cards)),
        ("nextUnmanaged", 0),
        ("reviewUiCounts", review_ui_counts),
        ("sourceClassificationCounts", OrderedDict(
            (key, len(classifications.get(key, [])))
            for key in (
                "approved_source_exact",
                "approved_source_superseded",
                "rejected_source_unchanged",
                "rejected_source_redesigned",
                "new_source",
            )
        )),
        ("sourceClassifications", OrderedDict(
            (key, classifications.get(key, []))
            for key in (
                "approved_source_exact",
                "approved_source_superseded",
                "rejected_source_unchanged",
                "rejected_source_redesigned",
                "new_source",
            )
        )),
        ("retainedLegacyRemovals", retained_legacy_removals),
        ("droppedUnchangedRejectedRemovals", sorted(dropped_removal_ids)),
        ("nextRemovals", len(selected_removals)),
        ("retiredRecipeUids", len(retired_recipe_uids)),
        ("retiredRemovalUids", len(retired_removal_uids)),
        ("predecessorRecipeUidsRetired", len([
            uid for uid in predecessor_recipe_uids if uid not in selected_uids
        ])),
        ("predecessorRemovalUidsRetired", len([
            uid for uid in predecessor_removal_uids
            if uid not in selected_removal_uids
        ])),
    ))
    return {
        "project": project,
        "baseline": copy.deepcopy(managed),
        "managed": managed,
        "approved_project": clean_approved,
        "acceptance": acceptance,
        "ownership_manifest": ownership_manifest,
        "report": report,
    }


def atomic_write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-project", type=Path, required=True)
    parser.add_argument("--old-baseline", type=Path, required=True)
    parser.add_argument("--approved-project", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, required=True)
    parser.add_argument("--next-managed", type=Path, required=True)
    parser.add_argument("--next-manifest", type=Path, required=True)
    parser.add_argument(
        "--previous-reviewed",
        type=Path,
        help="previous deployed reviewed batch whose removed UIDs must be retired",
    )
    parser.add_argument("--output-project", type=Path, required=True)
    parser.add_argument("--output-baseline", type=Path, required=True)
    parser.add_argument("--output-approved-project", type=Path, required=True)
    parser.add_argument("--output-managed", type=Path, required=True)
    parser.add_argument("--output-acceptance", type=Path, required=True)
    parser.add_argument("--output-ownership-manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    input_paths = OrderedDict((
        ("liveProject", args.live_project.resolve()),
        ("oldBaseline", args.old_baseline.resolve()),
        ("approvedProject", args.approved_project.resolve()),
        ("reviewLedger", args.reviews.resolve()),
        ("nextManagedSource", args.next_managed.resolve()),
        ("nextManifest", args.next_manifest.resolve()),
    ))
    if args.previous_reviewed is not None:
        input_paths["previousReviewed"] = args.previous_reviewed.resolve()
    result = reconcile(
        load_json(input_paths["liveProject"]),
        load_json(input_paths["oldBaseline"]),
        load_json(input_paths["approvedProject"]),
        load_json(input_paths["reviewLedger"]),
        load_json(input_paths["nextManagedSource"]),
        load_json(input_paths["nextManifest"]),
        load_json(input_paths["previousReviewed"])
        if "previousReviewed" in input_paths
        else None,
    )
    input_hashes = OrderedDict(
        (label, file_sha256(path)) for label, path in input_paths.items()
    )
    result["report"]["inputSha256"] = copy.deepcopy(input_hashes)
    result["acceptance"]["inputSha256"] = copy.deepcopy(input_hashes)
    for path, key in (
        (args.output_project, "project"),
        (args.output_baseline, "baseline"),
        (args.output_approved_project, "approved_project"),
        (args.output_managed, "managed"),
        (args.output_acceptance, "acceptance"),
        (args.output_ownership_manifest, "ownership_manifest"),
        (args.report, "report"),
    ):
        atomic_write_json(path.resolve(), result[key])
    counts = result["report"]
    print(
        f"Reconciled {counts['approved']} approved recipes and "
        f"{counts['nextPending']} pending recipes into "
        f"{counts['nextManaged']} managed cards with zero unmanaged cards."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
