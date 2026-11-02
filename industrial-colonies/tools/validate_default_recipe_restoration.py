#!/usr/bin/env python3
"""Validate the frozen 160-card default-restoration policy and final state."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from build_managed_recipe_manifest import (
    extract_recipe_outputs,
    normalize_default_restoration_policy,
)
from generate_managed_recipe_overhaul import expand_manifest
from reconcile_kjsgen_review_batch import design_hash


PROJECT = Path(__file__).resolve().parents[1]
POLICY = PROJECT / "progression/default_recipe_restoration_policy.json"
SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
MANIFEST = PROJECT / "progression/managed_recipe_overhaul.json"
COMPILED = PROJECT / "pack-kjsgen/default.managed.json"
REVIEWED = PROJECT / "pack-kjsgen/default.reviewed.managed.json"
OWNERSHIP = PROJECT / "progression/reviewed_ownership_manifest.json"
REPORT = PROJECT / "progression/default_recipe_restoration_report.json"


class ValidationError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must contain an object")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_sha(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def by_id(values: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(values, list):
        raise ValidationError(f"{label} must be an array")
    result: dict[str, dict[str, Any]] = {}
    for value in values:
        if not isinstance(value, dict) or not isinstance(value.get(key), str):
            raise ValidationError(f"{label} contains an invalid entry")
        if value[key] in result:
            raise ValidationError(f"{label} duplicates {value[key]}")
        result[value[key]] = value
    return result


def validate() -> None:
    policy_document = load(POLICY)
    policy = normalize_default_restoration_policy(POLICY, policy_document)
    entries = {entry["recipeId"]: entry for entry in policy["entries"]}
    evidence = policy_document.get("evidence")
    if not isinstance(evidence, dict):
        raise ValidationError("policy has no evidence object")
    for label in ("reviewLedger", "deployedReviewProject"):
        record = evidence.get(label)
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise ValidationError(f"policy evidence {label} is malformed")
        path = PROJECT / record["path"]
        if sha(path) != record.get("sha256"):
            raise ValidationError(f"immutable evidence hash drifted for {label}")

    ledger_record = evidence["reviewLedger"]
    deployed_record = evidence["deployedReviewProject"]
    ledger = load(PROJECT / ledger_record["path"])
    deployed = load(PROJECT / deployed_record["path"])
    deployed_cards = by_id(deployed.get("recipes"), "recipeId", "deployed recipes")
    deployed_removals = by_id(deployed.get("removals"), "recipeId", "deployed removals")
    reviews = ledger.get("reviews")
    if not isinstance(reviews, dict):
        raise ValidationError("ledger reviews are malformed")
    active = {
        recipe_id: decision
        for recipe_id, decision in reviews.items()
        if isinstance(decision, dict)
        and decision.get("reason") in {"restore_default_recipe", "default_recipe"}
        and recipe_id in deployed_cards
    }
    if set(active) != set(entries):
        raise ValidationError("frozen recipe IDs no longer match active deployed decisions")
    if Counter(value["reason"] for value in active.values()) != Counter(
        {"restore_default_recipe": 146, "default_recipe": 14}
    ):
        raise ValidationError("active reason counts drifted")
    for recipe_id, entry in entries.items():
        card = deployed_cards[recipe_id]
        if card.get("uid") != entry["uid"] or design_hash(card) != entry["cardSha256"]:
            raise ValidationError(f"deployed card fingerprint drifted for {recipe_id}")
        for removal in entry["ownedRemovals"]:
            if deployed_removals.get(removal["recipeId"], {}).get("uid") != removal["uid"]:
                raise ValidationError(f"deployed removal fingerprint drifted for {removal['recipeId']}")

    seed = load(SEED)
    seed_recipes = by_id(seed.get("recipes"), "id", "seed recipes")
    selected_ownership = [
        {
            "id": recipe_id,
            "outputs": sorted(extract_recipe_outputs(seed_recipes[recipe_id], recipe_id)),
            "remove": sorted(seed_recipes[recipe_id].get("remove", [])),
        }
        for recipe_id in sorted(entries)
    ]
    seed_evidence = evidence.get("selectedSeedOwnership", {})
    if canonical_sha(selected_ownership) != seed_evidence.get("sha256"):
        raise ValidationError("selected seed output/removal ownership fingerprints drifted")
    for recipe_id, entry in entries.items():
        spec = seed_recipes[recipe_id]
        if sorted(extract_recipe_outputs(spec, recipe_id)) != entry["outputs"]:
            raise ValidationError(f"seed outputs drifted for {recipe_id}")
        if sorted(spec.get("remove", [])) != sorted(
            removal["recipeId"] for removal in entry["ownedRemovals"]
        ):
            raise ValidationError(f"seed removal ownership drifted for {recipe_id}")

    manifest = load(MANIFEST)
    manifest_specs = expand_manifest(manifest)
    manifest_ids = {recipe["id"] for recipe in manifest_specs}
    if manifest_ids & set(entries):
        raise ValidationError("retired default recipes remain in the managed manifest")
    if not set(policy["removal_ids"]) <= set(manifest.get("preserve_recipe_ids", [])):
        raise ValidationError("restored stock removals are not preserved")
    compiled = load(COMPILED)
    compiled_recipe_ids = {card["recipeId"] for card in compiled.get("recipes", [])}
    if compiled_recipe_ids & set(entries):
        raise ValidationError("retired default cards remain compiled")
    compiled_removal_ids = {card["recipeId"] for card in compiled.get("removals", [])}
    if compiled_removal_ids & set(policy["removal_ids"]):
        raise ValidationError("restored stock removals remain compiled")
    expected_removal_ids = set(manifest.get("additional_removals", []))
    for spec in manifest_specs:
        expected_removal_ids.update(spec.get("remove", []))
    if compiled_recipe_ids != manifest_ids:
        raise ValidationError("compiled recipe IDs differ from the assembled manifest")
    if compiled_removal_ids != expected_removal_ids:
        raise ValidationError("compiled removal IDs differ from the assembled manifest")

    reviewed = load(REVIEWED)
    ownership = load(OWNERSHIP)
    if {card["recipeId"] for card in reviewed.get("recipes", [])} & set(entries):
        raise ValidationError("retired recipes remain in current reviewed source")
    if {card["recipeId"] for card in reviewed.get("removals", [])} & set(policy["removal_ids"]):
        raise ValidationError("restored removals remain in current reviewed source")
    if {entry["id"] for entry in ownership.get("recipes", [])} & set(entries):
        raise ValidationError("retired recipes remain in reviewed ownership")
    if not {entry["uid"] for entry in entries.values()} <= set(reviewed.get("retiredRecipeUids", [])):
        raise ValidationError("retired recipe UID ledger is incomplete")
    if not {
        removal["uid"] for entry in entries.values() for removal in entry["ownedRemovals"]
    } <= set(reviewed.get("retiredRemovalUids", [])):
        raise ValidationError("retired removal UID ledger is incomplete")
    reviewed_ids = {card["recipeId"] for card in reviewed.get("recipes", [])}
    ownership_ids = {entry["id"] for entry in ownership.get("recipes", [])}
    if reviewed_ids != ownership_ids:
        raise ValidationError("current reviewed source/ownership recipe IDs differ")

    report = load(REPORT)
    if report.get("retiredRecipes") != 160 or report.get("restoredRemovals") != 178:
        raise ValidationError("reconciliation report counts drifted")
    reviewed_before = evidence.get("reviewedSourceBeforeRetirement", {})
    if report.get("before", {}).get("sourceSha256") != reviewed_before.get("sha256"):
        raise ValidationError("reconciliation did not start from the frozen reviewed source")
    if report.get("before", {}).get("recipes") != 815 or report.get("before", {}).get("removals") != 1227:
        raise ValidationError("reconciliation before-counts drifted from 815/1227")
    proof = report.get("noUnrelatedChangesProof", {})
    if (
        proof.get("survivingRecipeCount") != 655
        or proof.get("survivingRemovalCount") != 1049
        or proof.get("survivingOwnershipCount") != 655
    ):
        raise ValidationError("no-unrelated-change proof counts drifted")
    # The reconciliation report freezes the exact post-restoration snapshot.
    # Later normal review reconciliation may legitimately revise surviving
    # rejected cards.  Re-check byte identity only while the current files are
    # still that frozen snapshot; policy-ID absence/retired UID checks above
    # remain mandatory forever and prevent resurrection.
    if sha(REVIEWED) == report.get("after", {}).get("sourceSha256"):
        if canonical_sha(reviewed["recipes"]) != proof.get("survivingRecipeSha256"):
            raise ValidationError("frozen surviving reviewed recipes differ from proof")
        if canonical_sha(reviewed["removals"]) != proof.get("survivingRemovalSha256"):
            raise ValidationError("frozen surviving reviewed removals differ from proof")
    if sha(OWNERSHIP) == report.get("after", {}).get("ownershipSha256"):
        if canonical_sha(ownership["recipes"]) != proof.get("survivingOwnershipSha256"):
            raise ValidationError("frozen surviving ownership differs from proof")


def main() -> int:
    try:
        validate()
    except (ValidationError, Exception) as error:
        print(f"default restoration validation failed: {error}", file=sys.stderr)
        return 1
    print("Default restoration validated: 160 recipes retired, 178 stock removals restored; no unrelated reviewed entries changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
