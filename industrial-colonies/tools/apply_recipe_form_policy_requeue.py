#!/usr/bin/env python3
"""Move policy-invalid approvals back to the live KJSGen review queue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_recipe_form_policy import accepted_recipe, runtime_blocks, verdict


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def outputs(card: dict[str, Any]) -> set[str]:
    return {
        str(value.get("id"))
        for key, value in card.get("slots", {}).items()
        if key.startswith("output") and isinstance(value, dict) and value.get("id")
    }


def save(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-root", type=Path, required=True)
    parser.add_argument(
        "--acceptance", type=Path,
        default=ROOT / "progression/recipe_review_acceptance.json",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--audit-active", action="store_true")
    parser.add_argument("--catalog", type=Path)
    args = parser.parse_args()

    acceptance = load(args.acceptance)
    requeue_ids = set(acceptance.get("policyRequeueRecipeIds", []))
    accepted = {
        entry["recipeId"]: entry
        for entry in acceptance.get("entries", [])
        if entry.get("recipeId") in requeue_ids
    }
    requeue_outputs = set().union(
        *(outputs(entry.get("card", {})) for entry in accepted.values())
    ) if accepted else set()

    sync = args.live_root / "kjsgen/industrial_colonies_sync"
    projects = args.live_root / "kjsgen/projects"
    ledger_path = sync / "default.recipe_reviews.json"
    approved_path = projects / "approved_recipes.json"
    rejected_path = projects / "rejected_recipes.json"
    default_path = projects / "default.json"
    ledger = load(ledger_path)
    approved = load(approved_path)
    rejected = load(rejected_path)
    default = load(default_path)

    if args.audit_active:
        if args.catalog is None:
            raise SystemExit("--audit-active requires --catalog")
        blocks = runtime_blocks(args.catalog)
        for card in default.get("recipes", []):
            record = ledger.get("reviews", {}).get(card.get("recipeId"))
            status = record.get("status") if isinstance(record, dict) else "pending"
            result, _ = verdict(
                accepted_recipe({"recipeId": card.get("recipeId"), "card": card}),
                blocks,
            )
            if status == "rejected" or (status == "approved" and result == "requeue"):
                requeue_ids.add(str(card.get("recipeId")))
                requeue_outputs.update(outputs(card))

    queue_cards = [
        card for card in default.get("recipes", [])
        if card.get("recipeId") in requeue_ids or outputs(card) & requeue_outputs
    ]
    queue_ids = {card.get("recipeId") for card in queue_cards}
    queue_uids = {card.get("uid") for card in queue_cards}
    if len(queue_cards) != len(requeue_ids):
        raise SystemExit(
            f"expected {len(requeue_ids)} policy-requeued live cards, found {len(queue_cards)}"
        )

    next_reviews = {
        recipe_id: record
        for recipe_id, record in ledger.get("reviews", {}).items()
        if recipe_id not in requeue_ids
        and recipe_id not in queue_ids
        and record.get("uid") not in queue_uids
    }
    next_approved = [
        card for card in approved.get("recipes", [])
        if card.get("recipeId") not in requeue_ids
        and card.get("recipeId") not in queue_ids
        and card.get("uid") not in queue_uids
        and not (outputs(card) & requeue_outputs)
    ]
    next_rejected = [
        card for card in rejected.get("recipes", [])
        if card.get("recipeId") not in requeue_ids
        and card.get("recipeId") not in queue_ids
        and card.get("uid") not in queue_uids
        and not (outputs(card) & requeue_outputs)
    ]
    changed_reviews = len(ledger.get("reviews", {})) - len(next_reviews)
    changed_approved = len(approved.get("recipes", [])) - len(next_approved)
    changed_rejected = len(rejected.get("recipes", [])) - len(next_rejected)

    if args.check:
        if changed_reviews or changed_approved or changed_rejected:
            raise SystemExit(
                f"policy queue is stale: {changed_reviews} decisions and "
                f"{changed_approved} approved and {changed_rejected} rejected snapshots remain"
            )
    else:
        ledger["reviews"] = next_reviews
        approved["recipes"] = next_approved
        rejected["recipes"] = next_rejected
        save(ledger_path, ledger)
        save(approved_path, approved)
        save(rejected_path, rejected)

    print(
        f"Policy queue contains {len(queue_cards)} cards; removed "
        f"{changed_reviews} active decisions, {changed_approved} approved snapshots, "
        f"and {changed_rejected} rejected snapshots."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
