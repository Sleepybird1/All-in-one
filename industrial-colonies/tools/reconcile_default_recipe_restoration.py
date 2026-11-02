#!/usr/bin/env python3
"""Retire the 160 frozen default-restoration cards from current review state."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from collections import OrderedDict
from pathlib import Path
from typing import Any

from build_managed_recipe_manifest import normalize_default_restoration_policy
from reconcile_kjsgen_review_batch import design_hash


PROJECT = Path(__file__).resolve().parents[1]
POLICY = PROJECT / "progression/default_recipe_restoration_policy.json"
SOURCE = PROJECT / "pack-kjsgen/default.reviewed.managed.json"
OWNERSHIP = PROJECT / "progression/reviewed_ownership_manifest.json"
REPORT = PROJECT / "progression/default_recipe_restoration_report.json"
OUTPUT_SLOT = re.compile(r"^(?:output|results?)\d*$")


class ReconcileError(ValueError):
    """Raised rather than guessing when current review state is ambiguous."""


def load(path: Path) -> OrderedDict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=OrderedDict)
    except (OSError, json.JSONDecodeError) as error:
        raise ReconcileError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ReconcileError(f"{path} must contain an object")
    return value


def require_array(document: dict[str, Any], key: str, label: str) -> list[Any]:
    value = document.get(key)
    if not isinstance(value, list):
        raise ReconcileError(f"{label} must contain a {key} array")
    return value


def indexed(values: list[Any], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(values):
        if not isinstance(value, dict) or not isinstance(value.get(key), str):
            raise ReconcileError(f"{label} entry {index} has no {key}")
        identity = value[key]
        if identity in result:
            raise ReconcileError(f"{label} duplicates {identity}")
        result[identity] = value
    return result


def card_outputs(card: dict[str, Any]) -> list[str]:
    slots = card.get("slots")
    if not isinstance(slots, dict):
        raise ReconcileError(f"recipe {card.get('recipeId')} has no slots object")
    outputs: list[str] = []
    for slot, stack in slots.items():
        if OUTPUT_SLOT.fullmatch(slot) and isinstance(stack, dict):
            if stack.get("kind") == "ITEM" and isinstance(stack.get("id"), str):
                outputs.append(stack["id"])
    return sorted(set(outputs))


def canonical_sha(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def encoded(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def reconcile(
    policy_path: Path, source_path: Path, ownership_path: Path
) -> tuple[OrderedDict[str, Any], OrderedDict[str, Any], OrderedDict[str, Any]]:
    policy_document = load(policy_path)
    try:
        policy = normalize_default_restoration_policy(policy_path, policy_document)
    except Exception as error:
        raise ReconcileError(str(error)) from error
    source = load(source_path)
    ownership = load(ownership_path)
    recipes = require_array(source, "recipes", "reviewed source")
    removals = require_array(source, "removals", "reviewed source")
    owned_recipes = require_array(ownership, "recipes", "reviewed ownership")
    recipe_by_id = indexed(recipes, "recipeId", "reviewed recipes")
    removal_by_id = indexed(removals, "recipeId", "reviewed removals")
    ownership_by_id = indexed(owned_recipes, "id", "reviewed ownership recipes")
    if set(recipe_by_id) != set(ownership_by_id):
        missing = sorted(set(recipe_by_id) - set(ownership_by_id))
        extra = sorted(set(ownership_by_id) - set(recipe_by_id))
        raise ReconcileError(
            f"reviewed source/ownership recipe parity failed; missing={missing}, extra={extra}"
        )

    policy_recipe_ids = set(policy["recipe_ids"])
    policy_removal_ids = set(policy["removal_ids"])
    policy_recipe_uids = {entry["uid"] for entry in policy["entries"]}
    policy_removal_uids = {
        removal["uid"]
        for entry in policy["entries"]
        for removal in entry["ownedRemovals"]
    }
    retired_recipe_uids = require_array(source, "retiredRecipeUids", "reviewed source")
    retired_removal_uids = require_array(source, "retiredRemovalUids", "reviewed source")
    present_recipes = policy_recipe_ids & set(recipe_by_id)
    present_removals = policy_removal_ids & set(removal_by_id)
    owned_present = policy_recipe_ids & set(ownership_by_id)
    fully_pending = (
        present_recipes == policy_recipe_ids
        and present_removals == policy_removal_ids
        and owned_present == policy_recipe_ids
        and not (policy_recipe_uids & set(retired_recipe_uids))
        and not (policy_removal_uids & set(retired_removal_uids))
    )
    fully_applied = (
        not present_recipes
        and not present_removals
        and not owned_present
        and policy_recipe_uids <= set(retired_recipe_uids)
        and policy_removal_uids <= set(retired_removal_uids)
    )
    if not fully_pending and not fully_applied:
        raise ReconcileError(
            "default restoration is partially applied or fingerprint state is ambiguous: "
            f"recipes={len(present_recipes)}/160, removals={len(present_removals)}/178, "
            f"ownership={len(owned_present)}/160"
        )

    if fully_applied:
        report = OrderedDict(
            (
                ("schemaVersion", 1),
                ("status", "already_applied"),
                ("policySha256", policy["sha256"]),
                ("retiredRecipes", 160),
                ("restoredRemovals", 178),
            )
        )
        return source, ownership, report

    for entry in policy["entries"]:
        recipe_id = entry["recipeId"]
        card = recipe_by_id[recipe_id]
        if card.get("uid") != entry["uid"] or design_hash(card) != entry["cardSha256"]:
            raise ReconcileError(f"reviewed card fingerprint mismatch for {recipe_id}")
        if card_outputs(card) != entry["outputs"]:
            raise ReconcileError(f"reviewed card output mismatch for {recipe_id}")
        for removal in entry["ownedRemovals"]:
            current = removal_by_id[removal["recipeId"]]
            if current.get("uid") != removal["uid"]:
                raise ReconcileError(
                    f"reviewed removal UID mismatch for {removal['recipeId']}"
                )

    surviving_recipes = [card for card in recipes if card["recipeId"] not in policy_recipe_ids]
    surviving_removals = [
        removal for removal in removals if removal["recipeId"] not in policy_removal_ids
    ]
    surviving_ownership = [
        entry for entry in owned_recipes if entry["id"] not in policy_recipe_ids
    ]
    next_source = copy.deepcopy(source)
    next_source["recipes"] = surviving_recipes
    next_source["removals"] = surviving_removals
    next_source["retiredRecipeUids"] = list(retired_recipe_uids) + sorted(policy_recipe_uids)
    next_source["retiredRemovalUids"] = list(retired_removal_uids) + sorted(policy_removal_uids)
    next_ownership = copy.deepcopy(ownership)
    next_ownership["recipes"] = surviving_ownership
    report = OrderedDict(
        (
            ("schemaVersion", 1),
            ("status", "applied"),
            ("policy", policy["path"]),
            ("policySha256", policy["sha256"]),
            (
                "before",
                OrderedDict(
                    (
                        ("sourceSha256", file_sha(source_path)),
                        ("ownershipSha256", file_sha(ownership_path)),
                        ("recipes", len(recipes)),
                        ("removals", len(removals)),
                        ("ownershipRecipes", len(owned_recipes)),
                    )
                ),
            ),
            (
                "after",
                OrderedDict(
                    (
                        ("recipes", len(surviving_recipes)),
                        ("removals", len(surviving_removals)),
                        ("ownershipRecipes", len(surviving_ownership)),
                    )
                ),
            ),
            ("retiredRecipes", len(policy_recipe_ids)),
            ("restoredRemovals", len(policy_removal_ids)),
            ("recipeIds", sorted(policy_recipe_ids)),
            ("removalIds", sorted(policy_removal_ids)),
            (
                "noUnrelatedChangesProof",
                OrderedDict(
                    (
                        ("survivingRecipeCount", len(surviving_recipes)),
                        ("survivingRecipeSha256", canonical_sha(surviving_recipes)),
                        ("survivingRemovalCount", len(surviving_removals)),
                        ("survivingRemovalSha256", canonical_sha(surviving_removals)),
                        ("survivingOwnershipCount", len(surviving_ownership)),
                        ("survivingOwnershipSha256", canonical_sha(surviving_ownership)),
                    )
                ),
            ),
        )
    )
    return next_source, next_ownership, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=POLICY)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--ownership", type=Path, default=OWNERSHIP)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args()
    try:
        source, ownership, report = reconcile(
            args.policy.resolve(), args.source.resolve(), args.ownership.resolve()
        )
    except ReconcileError as error:
        print(f"default restoration reconciliation failed: {error}")
        return 2
    if not args.check and report["status"] == "applied":
        atomic_write(args.source.resolve(), encoded(source))
        atomic_write(args.ownership.resolve(), encoded(ownership))
        report["after"]["sourceSha256"] = file_sha(args.source.resolve())
        report["after"]["ownershipSha256"] = file_sha(args.ownership.resolve())
        atomic_write(args.report.resolve(), encoded(report))
    print(
        f"Default restoration {report['status']}: "
        f"{report['retiredRecipes']} recipes, {report['restoredRemovals']} removals."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
