#!/usr/bin/env python3
"""Freeze the active reviewed requests to restore stock/default recipes.

The completed deployed review ledger contains historical decisions.  Only
cards still present in the deployed review project are active.  This builder
therefore selects the 146 ``restore_default_recipe`` cards and the 14 active
``default_recipe`` cards by exact ID, UID, and design fingerprint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any

from build_managed_recipe_manifest import extract_recipe_outputs
from reconcile_kjsgen_review_batch import design_hash


PROJECT = Path(__file__).resolve().parents[1]
LEDGER = PROJECT / "build/staging-steel-frame-migration-20260902-v2/default.recipe_reviews.json"
DEPLOYED_PROJECT = PROJECT / "build/staging-steel-frame-migration-20260902-v2/default.json"
REVIEWED_SOURCE = PROJECT / "pack-kjsgen/default.reviewed.managed.json"
SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
OUTPUT = PROJECT / "progression/default_recipe_restoration_policy.json"
EXPECTED_REASONS = {"restore_default_recipe": 146, "default_recipe": 14}
EXPECTED_RECIPES = 160
EXPECTED_REMOVALS = 178


class PolicyError(ValueError):
    """Raised when frozen review evidence no longer identifies one exact policy."""


def load(path: Path) -> OrderedDict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=OrderedDict)
    except (OSError, json.JSONDecodeError) as error:
        raise PolicyError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise PolicyError(f"{path} must contain an object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def evidence(path: Path, **counts: int) -> OrderedDict[str, Any]:
    result: OrderedDict[str, Any] = OrderedDict(
        (("path", path.relative_to(PROJECT).as_posix()), ("sha256", sha256(path)))
    )
    result.update(counts)
    return result


def indexed(values: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(values, list):
        raise PolicyError(f"{label} must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(values):
        if not isinstance(value, dict) or not isinstance(value.get(key), str):
            raise PolicyError(f"{label} entry {index} has no {key}")
        identity = value[key]
        if identity in result:
            raise PolicyError(f"{label} duplicates {identity}")
        result[identity] = value
    return result


def build() -> OrderedDict[str, Any]:
    ledger = load(LEDGER)
    deployed = load(DEPLOYED_PROJECT)
    reviewed = load(REVIEWED_SOURCE)
    seed = load(SEED)
    reviews = ledger.get("reviews")
    if not isinstance(reviews, dict):
        raise PolicyError("review ledger has no reviews object")
    deployed_cards = indexed(deployed.get("recipes"), "recipeId", "deployed recipes")
    reviewed_cards = indexed(reviewed.get("recipes"), "recipeId", "reviewed recipes")
    seed_recipes = indexed(seed.get("recipes"), "id", "seed recipes")
    deployed_removals = indexed(deployed.get("removals"), "recipeId", "deployed removals")
    reviewed_removals = indexed(reviewed.get("removals"), "recipeId", "reviewed removals")
    retired_recipe_uids = set(reviewed.get("retiredRecipeUids", []))
    retired_removal_uids = set(reviewed.get("retiredRemovalUids", []))
    previous_policy = load(OUTPUT) if OUTPUT.is_file() else None

    selected: list[tuple[str, dict[str, Any]]] = []
    for recipe_id, decision in reviews.items():
        if not isinstance(decision, dict):
            raise PolicyError(f"review {recipe_id} is not an object")
        reason = decision.get("reason")
        if reason in EXPECTED_REASONS and recipe_id in deployed_cards:
            selected.append((recipe_id, decision))
    reasons = Counter(decision["reason"] for _, decision in selected)
    if dict(reasons) != EXPECTED_REASONS or len(selected) != EXPECTED_RECIPES:
        raise PolicyError(
            f"active default-restoration selection drifted: {dict(reasons)}, {len(selected)} cards"
        )

    entries: list[OrderedDict[str, Any]] = []
    owned_ids: list[str] = []
    outputs: list[str] = []
    for recipe_id, decision in sorted(selected):
        deployed_card = deployed_cards[recipe_id]
        reviewed_card = reviewed_cards.get(recipe_id)
        spec = seed_recipes.get(recipe_id)
        if spec is None:
            raise PolicyError(f"active default restoration {recipe_id} is absent from the seed")
        expected_uid = decision.get("uid")
        expected_hash = decision.get("cardSha256")
        for label, card in (("deployed", deployed_card),):
            if card.get("uid") != expected_uid or design_hash(card) != expected_hash:
                raise PolicyError(f"{label} fingerprint mismatch for {recipe_id}")
        if reviewed_card is not None:
            if reviewed_card.get("uid") != expected_uid or design_hash(reviewed_card) != expected_hash:
                raise PolicyError(f"reviewed fingerprint mismatch for {recipe_id}")
        elif expected_uid not in retired_recipe_uids:
            raise PolicyError(f"reviewed source neither contains nor retires {recipe_id}")
        recipe_outputs = sorted(extract_recipe_outputs(spec, f"seed recipe {recipe_id}"))
        if len(recipe_outputs) != 1:
            raise PolicyError(f"{recipe_id} does not have exactly one item output")
        removals = spec.get("remove", [])
        if not isinstance(removals, list) or any(not isinstance(value, str) for value in removals):
            raise PolicyError(f"{recipe_id} has malformed exact removals")
        if len(removals) != len(set(removals)):
            raise PolicyError(f"{recipe_id} duplicates an owned removal")
        owned: list[OrderedDict[str, str]] = []
        for removal_id in sorted(removals):
            deployed_removal = deployed_removals.get(removal_id)
            reviewed_removal = reviewed_removals.get(removal_id)
            if deployed_removal is None:
                raise PolicyError(f"owned deployed removal {removal_id} is absent for {recipe_id}")
            if reviewed_removal is not None:
                if deployed_removal.get("uid") != reviewed_removal.get("uid"):
                    raise PolicyError(f"owned removal UID mismatch for {removal_id}")
            elif deployed_removal.get("uid") not in retired_removal_uids:
                raise PolicyError(f"reviewed source neither contains nor retires {removal_id}")
            owned.append(
                OrderedDict(
                    (("recipeId", removal_id), ("uid", str(deployed_removal["uid"])))
                )
            )
            owned_ids.append(removal_id)
        outputs.extend(recipe_outputs)
        entries.append(
            OrderedDict(
                (
                    ("recipeId", recipe_id),
                    ("uid", str(expected_uid)),
                    ("status", "rejected"),
                    ("reason", str(decision["reason"])),
                    ("cardSha256", str(expected_hash)),
                    ("outputs", recipe_outputs),
                    ("ownedRemovals", owned),
                )
            )
        )
    if len(set(outputs)) != EXPECTED_RECIPES:
        raise PolicyError("default-restoration outputs are not one-to-one")
    if len(owned_ids) != EXPECTED_REMOVALS or len(set(owned_ids)) != EXPECTED_REMOVALS:
        raise PolicyError(
            f"default-restoration ownership must contain {EXPECTED_REMOVALS} unique removals"
        )
    if previous_policy is not None:
        previous_evidence = previous_policy.get("evidence", {})
        reviewed_before = previous_evidence.get("reviewedSourceBeforeRetirement")
        if not isinstance(reviewed_before, dict):
            raise PolicyError("existing policy lost reviewedSourceBeforeRetirement evidence")
        reviewed_before = OrderedDict(reviewed_before)
    else:
        reviewed_before = evidence(
            REVIEWED_SOURCE,
            recipes=len(reviewed_cards),
            removals=len(reviewed_removals),
        )
    selected_seed_ownership = [
        OrderedDict(
            (
                ("id", recipe_id),
                (
                    "outputs",
                    sorted(extract_recipe_outputs(seed_recipes[recipe_id], recipe_id)),
                ),
                ("remove", sorted(seed_recipes[recipe_id].get("remove", []))),
            )
        )
        for recipe_id, _ in sorted(selected)
    ]
    return OrderedDict(
        (
            ("schemaVersion", 1),
            ("policy", "active_reviewed_default_restoration"),
            ("project", "default"),
            (
                "counts",
                OrderedDict(
                    (
                        ("activeRecipes", len(entries)),
                        ("restoreDefaultRecipe", reasons["restore_default_recipe"]),
                        ("defaultRecipe", reasons["default_recipe"]),
                        ("outputs", len(set(outputs))),
                        ("ownedRemovals", len(set(owned_ids))),
                    )
                ),
            ),
            (
                "evidence",
                OrderedDict(
                    (
                        ("reviewLedger", evidence(LEDGER, reviews=len(reviews))),
                        (
                            "deployedReviewProject",
                            evidence(
                                DEPLOYED_PROJECT,
                                recipes=len(deployed_cards),
                                removals=len(deployed_removals),
                            ),
                        ),
                        (
                            "reviewedSourceBeforeRetirement",
                            reviewed_before,
                        ),
                        (
                            "selectedSeedOwnership",
                            OrderedDict(
                                (
                                    ("path", SEED.relative_to(PROJECT).as_posix()),
                                    ("selectedRecipes", len(selected_seed_ownership)),
                                    ("sha256", canonical_sha256(selected_seed_ownership)),
                                )
                            ),
                        ),
                    )
                ),
            ),
            ("entries", entries),
            ("sharedRemovalResolutions", []),
        )
    )


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        content = encoded(build())
    except PolicyError as error:
        print(f"default restoration policy build failed: {error}")
        return 2
    output = args.output.resolve()
    if args.check:
        if not output.is_file() or output.read_bytes() != content:
            print(f"default restoration policy is stale: {output}")
            return 1
    else:
        atomic_write(output, content)
    print(f"Default restoration policy: {EXPECTED_RECIPES} recipes, {EXPECTED_REMOVALS} removals.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
