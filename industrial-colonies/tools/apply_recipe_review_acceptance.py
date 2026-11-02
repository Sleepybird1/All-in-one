#!/usr/bin/env python3
"""Rebuild the clean managed recipe batch from a frozen review acceptance."""

from __future__ import annotations

import argparse
import copy
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable

try:
    from tools.reconcile_kjsgen_review_batch import (
        ReconcileError,
        atomic_write_json,
        design_hash,
        file_sha256,
        load_json,
        reconcile,
    )
except ModuleNotFoundError:  # Direct execution from the tools directory.
    from reconcile_kjsgen_review_batch import (  # type: ignore
        ReconcileError,
        atomic_write_json,
        design_hash,
        file_sha256,
        load_json,
        reconcile,
    )


def frozen_review_documents(
    acceptance: dict[str, Any], previous_reviewed: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if acceptance.get("schemaVersion") != 1:
        raise ReconcileError("review acceptance must use schemaVersion 1")
    entries = acceptance.get("entries")
    if not isinstance(entries, list):
        raise ReconcileError("review acceptance entries must be an array")

    cards: list[dict[str, Any]] = []
    approved_cards: list[dict[str, Any]] = []
    reviews: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ReconcileError(f"acceptance entry {index} must be an object")
        recipe_id = entry.get("recipeId")
        card = entry.get("card")
        decision = entry.get("decision")
        if not isinstance(recipe_id, str) or not recipe_id:
            raise ReconcileError(f"acceptance entry {index} has no recipe ID")
        if not isinstance(card, dict) or card.get("recipeId") != recipe_id:
            raise ReconcileError(f"acceptance card does not match {recipe_id}")
        if not isinstance(decision, dict):
            raise ReconcileError(f"acceptance decision for {recipe_id} is invalid")
        if recipe_id in reviews:
            raise ReconcileError(f"acceptance repeats recipe ID {recipe_id}")
        if decision.get("uid") != card.get("uid"):
            raise ReconcileError(f"acceptance UID mismatch for {recipe_id}")
        if decision.get("cardSha256") != design_hash(card):
            raise ReconcileError(f"acceptance fingerprint mismatch for {recipe_id}")
        if decision.get("status") not in {"approved", "rejected"}:
            raise ReconcileError(f"acceptance status is invalid for {recipe_id}")
        cards.append(copy.deepcopy(card))
        reviews[recipe_id] = copy.deepcopy(decision)
        if decision["status"] == "approved":
            approved_cards.append(copy.deepcopy(card))

    expected = {
        "reviewed": len(entries),
        "approved": len(approved_cards),
        "rejected": len(entries) - len(approved_cards),
    }
    for field, actual in expected.items():
        if acceptance.get(field) != actual:
            raise ReconcileError(
                f"acceptance {field} count is stale: expected {actual}, "
                f"found {acceptance.get(field)!r}"
            )

    live = OrderedDict((
        ("format", 1),
        ("name", str(acceptance.get("project", "default"))),
        ("defaultTargetFile", "kjsgen_recipes.js"),
        ("exportComments", True),
        ("reloadOnExport", True),
        ("recipes", cards),
        ("removals", copy.deepcopy(previous_reviewed.get("removals", []))),
    ))
    approved = OrderedDict((
        ("format", 1),
        ("name", "approved recipes"),
        ("defaultTargetFile", "approved_recipes.js"),
        ("exportComments", True),
        ("reloadOnExport", False),
        ("recipes", approved_cards),
        ("removals", []),
    ))
    ledger = OrderedDict((
        ("schemaVersion", 1),
        ("project", str(acceptance.get("project", "default"))),
        ("reviews", reviews),
    ))
    return live, approved, ledger


def reconcile_from_acceptance(
    acceptance: dict[str, Any],
    previous_reviewed: dict[str, Any],
    next_managed: dict[str, Any],
    next_manifest: dict[str, Any],
) -> dict[str, Any]:
    live, approved, ledger = frozen_review_documents(acceptance, previous_reviewed)
    policy_requeue = acceptance.get("policyRequeueRecipeIds", [])
    if not isinstance(policy_requeue, list) or any(
        not isinstance(recipe_id, str) or not recipe_id for recipe_id in policy_requeue
    ):
        raise ReconcileError("policyRequeueRecipeIds must be an array of recipe IDs")
    if len(set(policy_requeue)) != len(policy_requeue):
        raise ReconcileError("policyRequeueRecipeIds repeats a recipe ID")
    accepted_by_id = {
        entry["recipeId"]: entry
        for entry in acceptance.get("entries", [])
    }
    for recipe_id in policy_requeue:
        entry = accepted_by_id.get(recipe_id)
        if entry is None or entry.get("decision", {}).get("status") != "approved":
            raise ReconcileError(
                f"policy requeue must reference an approved acceptance: {recipe_id}"
            )
    requeue_set = set(policy_requeue)
    approved["recipes"] = [
        card for card in approved.get("recipes", [])
        if card.get("recipeId") not in requeue_set
    ]
    for recipe_id in requeue_set:
        ledger["reviews"].pop(recipe_id, None)
    # A formerly approved card can be absent from the raw source because the
    # approval itself was its durable owner.  Keep such a card visible in the
    # queue instead of silently deleting it when the policy invalidates that
    # approval.
    next_managed = copy.deepcopy(next_managed)
    source_ids = {
        card.get("recipeId") for card in next_managed.get("recipes", [])
        if isinstance(card, dict)
    }
    for recipe_id in policy_requeue:
        if recipe_id not in source_ids:
            next_managed.setdefault("recipes", []).append(
                copy.deepcopy(accepted_by_id[recipe_id]["card"])
            )
    return reconcile(
        live,
        previous_reviewed,
        approved,
        ledger,
        next_managed,
        next_manifest,
    )


def encoded(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--previous-reviewed", type=Path, required=True)
    parser.add_argument("--next-managed", type=Path, required=True)
    parser.add_argument("--next-manifest", type=Path, required=True)
    parser.add_argument("--output-reviewed", type=Path, required=True)
    parser.add_argument("--output-ownership-manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    paths = OrderedDict((
        ("acceptance", args.acceptance.resolve()),
        ("previousReviewed", args.previous_reviewed.resolve()),
        ("nextManagedSource", args.next_managed.resolve()),
        ("nextManifest", args.next_manifest.resolve()),
    ))
    result = reconcile_from_acceptance(
        load_json(paths["acceptance"]),
        load_json(paths["previousReviewed"]),
        load_json(paths["nextManagedSource"]),
        load_json(paths["nextManifest"]),
    )
    result["report"]["acceptanceInputSha256"] = OrderedDict(
        (label, file_sha256(path)) for label, path in paths.items()
    )

    output_reviewed = args.output_reviewed.resolve()
    output_ownership = args.output_ownership_manifest.resolve()
    if args.check:
        mismatches: list[str] = []
        for path, key in (
            (output_reviewed, "managed"),
            (output_ownership, "ownership_manifest"),
        ):
            if not path.is_file() or path.read_bytes() != encoded(result[key]):
                mismatches.append(str(path))
        if mismatches:
            raise SystemExit(
                "Reviewed recipe artifacts are stale; regenerate: "
                + ", ".join(mismatches)
            )
    else:
        atomic_write_json(output_reviewed, result["managed"])
        atomic_write_json(output_ownership, result["ownership_manifest"])
        if args.report is not None:
            atomic_write_json(args.report.resolve(), result["report"])
    counts = result["report"]
    print(
        f"Acceptance reconciliation is current: {counts['approved']} approved, "
        f"{counts['nextPending']} pending, {counts['nextManaged']} managed, "
        f"{counts['nextUnmanaged']} unmanaged."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
