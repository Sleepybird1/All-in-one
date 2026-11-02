#!/usr/bin/env python3
"""Validate a merged KJSGen project without treating user drafts as managed cards.

The source-controlled managed project is authoritative for every UID it owns.
The staged deployment may also contain user-authored cards, including unfinished
cards with no recipe ID or output.  Those cards are preserved, but they may not
replace, edit, or duplicate an exclusive managed output.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCE = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalized_uid(value: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} has invalid uid {value!r}")
        return None
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError):
        errors.append(f"{label} uid is not a UUID: {value!r}")
        return None


def index_entries(
    project: dict[str, Any], field: str, label: str, errors: list[str]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    raw = project.get(field)
    if not isinstance(raw, list):
        errors.append(f"{label} project {field} must be an array")
        return [], {}

    entries: list[dict[str, Any]] = []
    by_uid: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(raw):
        if not isinstance(entry, dict):
            errors.append(f"{label} {field}[{index}] must be an object")
            continue
        entries.append(entry)
        uid = normalized_uid(entry.get("uid"), f"{label} {field}[{index}]", errors)
        if uid is None:
            continue
        if uid in by_uid:
            errors.append(f"{label} {field} contains duplicate uid {uid}")
            continue
        by_uid[uid] = entry
    return entries, by_uid


def item_outputs(recipe: dict[str, Any]) -> set[str]:
    outputs: set[str] = set()
    slots = recipe.get("slots")
    if not isinstance(slots, dict):
        return outputs
    for slot_name, stack in slots.items():
        slot_label = str(slot_name)
        if not (
            slot_label.startswith("output") or slot_label.startswith("results")
        ):
            continue
        if not isinstance(stack, dict) or stack.get("kind") != "ITEM":
            continue
        item_id = stack.get("id")
        if isinstance(item_id, str) and RESOURCE.fullmatch(item_id):
            outputs.add(item_id)
    return outputs


def validate(
    managed: dict[str, Any], staged: dict[str, Any], manifest: dict[str, Any]
) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    managed_recipes, managed_recipe_uids = index_entries(
        managed, "recipes", "managed", errors
    )
    managed_removals, managed_removal_uids = index_entries(
        managed, "removals", "managed", errors
    )
    staged_recipes, staged_recipe_uids = index_entries(
        staged, "recipes", "staged", errors
    )
    staged_removals, staged_removal_uids = index_entries(
        staged, "removals", "staged", errors
    )

    for label, recipe_uids, removal_uids in (
        ("managed", managed_recipe_uids, managed_removal_uids),
        ("staged", staged_recipe_uids, staged_removal_uids),
    ):
        for uid in sorted(set(recipe_uids).intersection(removal_uids)):
            errors.append(f"{label} project reuses uid {uid} across recipes and removals")

    for uid, expected in managed_recipe_uids.items():
        actual = staged_recipe_uids.get(uid)
        if actual is None:
            errors.append(f"staged project is missing active managed recipe uid {uid}")
        elif canonical(actual) != canonical(expected):
            errors.append(f"active managed recipe uid {uid} was edited in the staged project")

    for uid, expected in managed_removal_uids.items():
        actual = staged_removal_uids.get(uid)
        if actual is None:
            errors.append(f"staged project is missing active managed removal uid {uid}")
        elif canonical(actual) != canonical(expected):
            errors.append(f"active managed removal uid {uid} was edited in the staged project")

    recipe_id_owners: dict[str, list[str]] = defaultdict(list)
    output_owners: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
    for index, recipe in enumerate(staged_recipes):
        raw_uid = recipe.get("uid")
        uid = normalized_uid(raw_uid, f"staged recipes[{index}]", errors)
        recipe_id = recipe.get("recipeId")
        is_managed = uid is not None and uid in managed_recipe_uids
        if recipe_id is None:
            if is_managed:
                errors.append(f"active managed recipe uid {raw_uid} has no recipeId")
        elif not isinstance(recipe_id, str) or not RESOURCE.fullmatch(recipe_id):
            errors.append(f"staged recipe {index} has invalid recipeId {recipe_id!r}")
        else:
            recipe_id_owners[recipe_id].append(str(raw_uid))

        for output in item_outputs(recipe):
            output_owners[output].append(
                (uid or str(raw_uid), recipe_id if isinstance(recipe_id, str) else None)
            )

    for recipe_id, owners in sorted(recipe_id_owners.items()):
        if len(owners) > 1:
            errors.append(
                f"staged recipeId {recipe_id} has multiple cards: {', '.join(owners)}"
            )

    removal_id_owners: dict[str, list[str]] = defaultdict(list)
    for index, removal in enumerate(staged_removals):
        raw_uid = removal.get("uid")
        uid = normalized_uid(raw_uid, f"staged removals[{index}]", errors)
        recipe_id = removal.get("recipeId")
        is_managed = uid is not None and uid in managed_removal_uids
        if recipe_id in (None, ""):
            if is_managed:
                errors.append(f"active managed removal uid {raw_uid} has no exact recipeId")
            continue
        if not isinstance(recipe_id, str) or not RESOURCE.fullmatch(recipe_id):
            errors.append(f"staged removal {index} has invalid recipeId {recipe_id!r}")
            continue
        removal_id_owners[recipe_id].append(str(raw_uid))

    for recipe_id, owners in sorted(removal_id_owners.items()):
        if len(owners) > 1:
            errors.append(
                f"staged exact removal {recipe_id} is duplicated by: {', '.join(owners)}"
            )

    manifest_recipes = manifest.get("recipes")
    if not isinstance(manifest_recipes, list):
        errors.append("managed manifest recipes must be an array")
        manifest_recipes = []
    managed_by_id = {
        recipe.get("recipeId"): recipe
        for recipe in managed_recipes
        if isinstance(recipe.get("recipeId"), str)
    }
    exclusive_outputs = 0
    for contract in manifest_recipes:
        if not isinstance(contract, dict) or contract.get("exclusive_output") is not True:
            continue
        recipe_id = contract.get("id")
        if not isinstance(recipe_id, str):
            errors.append("exclusive managed contract has no valid id")
            continue
        managed_recipe = managed_by_id.get(recipe_id)
        if managed_recipe is None:
            errors.append(f"exclusive managed contract {recipe_id} has no compiled card")
            continue
        expected_uid = normalized_uid(
            managed_recipe.get("uid"), f"managed recipe {recipe_id}", errors
        )
        if expected_uid is None:
            continue
        outputs = item_outputs(managed_recipe)
        if not outputs:
            errors.append(f"exclusive managed contract {recipe_id} has no compiled item output")
            continue
        for output in sorted(outputs):
            exclusive_outputs += 1
            owners = output_owners.get(output, [])
            if owners != [(expected_uid, recipe_id)]:
                rendered = ", ".join(
                    f"{owner_id or '<draft>'} ({owner_uid})"
                    for owner_uid, owner_id in owners
                ) or "none"
                errors.append(
                    f"exclusive managed output {output} must be owned only by "
                    f"{recipe_id} ({expected_uid}); found {rendered}"
                )

    stats = {
        "managed_recipes": len(managed_recipes),
        "managed_removals": len(managed_removals),
        "user_recipes": len(staged_recipes) - len(managed_recipes),
        "user_removals": len(staged_removals) - len(managed_removals),
        "exclusive_outputs": exclusive_outputs,
    }
    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--managed", type=Path, default=PROJECT_ROOT / "pack-kjsgen" / "default.managed.json"
    )
    parser.add_argument("--staged", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "progression" / "managed_recipe_overhaul.json",
    )
    args = parser.parse_args()

    try:
        managed = load_json(args.managed.resolve())
        staged = load_json(args.staged.resolve())
        manifest = load_json(args.manifest.resolve())
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    errors, stats = validate(managed, staged, manifest)
    if errors:
        print("FAIL: staged KJSGen project violates managed ownership", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print(
        "PASS: staged KJSGen ownership is safe; "
        f"{stats['managed_recipes']} active managed recipes, "
        f"{stats['managed_removals']} active managed removals, "
        f"{stats['user_recipes']} preserved user recipes, "
        f"{stats['user_removals']} preserved user removals, "
        f"{stats['exclusive_outputs']} exclusive outputs protected."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
