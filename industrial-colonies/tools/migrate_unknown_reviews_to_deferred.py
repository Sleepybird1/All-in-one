#!/usr/bin/env python3
"""Stage the completed second-pass review ledger into the exact Deferred project.

This is intentionally a one-way, fail-closed staging tool.  It never writes to
the Minecraft instance.  The caller supplies a separate output directory and
deploys the validated files only after Minecraft has closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


DEFERRED_RECIPE_IDS = frozenset(
    {
        "industrial_colonies:electronics/n_semiconductor",
        "industrial_colonies:electronics/p_semiconductor",
        "industrial_colonies:heavy_industry/winding_machine",
        "industrial_colonies:interstellar/navigation_computer",
        "industrial_colonies:interstellar/warp_charge",
        "industrial_colonies:outer_station/atmospheric_scoop",
        "industrial_colonies:outer_station/station_services_controller",
        "industrial_colonies:outer_station/warp_charge_precursor",
        "industrial_colonies:planetary/calorite/concentrate_leaching",
        "industrial_colonies:planetary/calorite/feed_to_grit",
        "industrial_colonies:planetary/calorite/grit_to_concentrate",
        "industrial_colonies:planetary/calorite/leached_compound_reduction",
        "industrial_colonies:planetary/desh/concentrate_leaching",
        "industrial_colonies:planetary/desh/feed_to_grit",
        "industrial_colonies:planetary/desh/grit_to_concentrate",
        "industrial_colonies:planetary/desh/leached_compound_reduction",
        "industrial_colonies:planetary/mercury/navigation_computer",
        "industrial_colonies:planetary/navigation/mars_navigation_computer",
        "industrial_colonies:planetary/ostrum/concentrate_leaching",
        "industrial_colonies:planetary/ostrum/feed_to_grit",
        "industrial_colonies:planetary/ostrum/grit_to_concentrate",
        "industrial_colonies:planetary/ostrum/leached_compound_reduction",
        "industrial_colonies:planetary/venus/navigation_computer",
        "industrial_colonies:space/construction/contraption_diagram",
        "industrial_colonies:space/construction/guidance_certified_plan",
        "industrial_colonies:space/construction/propulsion_certified_plan",
    }
)

EXPECTED_SOURCE_COUNTS = {
    "approved": 309,
    "rejected": 467,
    "maybe": 125,
    "disabled": 11,
}

ARCHIVE_SPECS = {
    "approved": ("approved_recipes.json", "approved recipes"),
    "rejected": ("rejected_recipes.json", "rejected recipes"),
    "disabled": ("disabled_recipes.json", "disabled recipes"),
}


class MigrationError(RuntimeError):
    """A source invariant failed; no staged output should be trusted."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError(f"Cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MigrationError(f"JSON root must be an object: {path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def card_sha256(card: dict[str, Any]) -> str:
    design = {
        "type": card.get("type"),
        "recipeId": card.get("recipeId"),
        "slots": card.get("slots", {}),
        "params": card.get("params", {}),
    }
    canonical = json.dumps(
        design,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def recipe_index(project: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    recipes = project.get("recipes")
    if not isinstance(recipes, list):
        raise MigrationError(f"{label} has no recipes array")
    result: dict[str, dict[str, Any]] = {}
    uids: set[str] = set()
    for index, card in enumerate(recipes):
        if not isinstance(card, dict):
            raise MigrationError(f"{label}.recipes[{index}] is not an object")
        recipe_id = card.get("recipeId")
        uid = card.get("uid")
        if not isinstance(recipe_id, str) or not recipe_id:
            raise MigrationError(f"{label}.recipes[{index}] has no recipeId")
        if not isinstance(uid, str) or not uid:
            raise MigrationError(f"{label}.recipes[{index}] has no uid")
        if recipe_id in result:
            raise MigrationError(f"Duplicate recipeId in {label}: {recipe_id}")
        if uid in uids:
            raise MigrationError(f"Duplicate uid in {label}: {uid}")
        result[recipe_id] = card
        uids.add(uid)
    return result


def validate_archive(
    project: dict[str, Any],
    expected_name: str | set[str],
    status: str,
    reviews: dict[str, dict[str, Any]],
    label: str,
) -> dict[str, dict[str, Any]]:
    allowed_names = {expected_name} if isinstance(expected_name, str) else expected_name
    if project.get("name") not in allowed_names:
        raise MigrationError(
            f"{label} project name {project.get('name')!r} is not one of {sorted(allowed_names)!r}"
        )
    index = recipe_index(project, label)
    expected_ids = {recipe_id for recipe_id, record in reviews.items() if record.get("status") == status}
    if set(index) != expected_ids:
        missing = sorted(expected_ids - set(index))
        extra = sorted(set(index) - expected_ids)
        raise MigrationError(f"{label} does not match ledger; missing={missing}, extra={extra}")
    for recipe_id, card in index.items():
        record = reviews[recipe_id]
        if card.get("uid") != record.get("uid"):
            raise MigrationError(f"UID mismatch for {recipe_id} in {label}")
        if card_sha256(card) != record.get("cardSha256"):
            raise MigrationError(f"Card fingerprint mismatch for {recipe_id} in {label}")
    return index


def validate_archive_partition(
    archives: dict[str, dict[str, dict[str, Any]]],
    label: str,
) -> None:
    seen_ids: dict[str, str] = {}
    seen_uids: dict[str, str] = {}
    for archive_name, cards in archives.items():
        for recipe_id, card in cards.items():
            prior_id_archive = seen_ids.get(recipe_id)
            if prior_id_archive is not None:
                raise MigrationError(
                    f"{label} repeats recipeId {recipe_id} in {prior_id_archive} and {archive_name}"
                )
            uid = card["uid"]
            prior_uid_archive = seen_uids.get(uid)
            if prior_uid_archive is not None:
                raise MigrationError(
                    f"{label} repeats uid {uid} in {prior_uid_archive} and {archive_name}"
                )
            seen_ids[recipe_id] = archive_name
            seen_uids[uid] = archive_name


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def migrate(pack_dir: Path, output_dir: Path) -> dict[str, Any]:
    pack_dir = pack_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir == pack_dir or output_dir.is_relative_to(pack_dir):
        raise MigrationError("Output directory must be outside the live Minecraft instance")
    if output_dir.exists():
        raise MigrationError(f"Output directory already exists: {output_dir}")

    sync_dir = pack_dir / "kjsgen" / "industrial_colonies_sync"
    projects_dir = pack_dir / "kjsgen" / "projects"
    ledger_path = sync_dir / "default.recipe_reviews.json"
    source_paths = {
        "ledger": ledger_path,
        "default": projects_dir / "default.json",
        **{status: projects_dir / filename for status, (filename, _) in ARCHIVE_SPECS.items()},
    }
    deferred_candidates = [projects_dir / "Deferred.json", projects_dir / "maybe_recipes.json"]
    existing_deferred = [path for path in deferred_candidates if path.is_file()]
    if len(existing_deferred) != 1:
        raise MigrationError(
            "Expected exactly one existing Deferred/maybe archive, found: "
            + ", ".join(str(path) for path in existing_deferred)
        )
    source_paths["maybe"] = existing_deferred[0]
    missing = [str(path) for path in source_paths.values() if not path.is_file()]
    if missing:
        raise MigrationError("Missing source files: " + ", ".join(missing))

    ledger = load_json(source_paths["ledger"])
    if ledger.get("schemaVersion") != 1 or ledger.get("project") != "default":
        raise MigrationError("Review ledger must be schemaVersion 1 for project default")
    reviews = ledger.get("reviews")
    if not isinstance(reviews, dict):
        raise MigrationError("Review ledger has no reviews object")
    counts = Counter(record.get("status") for record in reviews.values() if isinstance(record, dict))
    if dict(counts) != EXPECTED_SOURCE_COUNTS:
        raise MigrationError(f"Unexpected source review counts: {dict(counts)}")

    projects = {key: load_json(path) for key, path in source_paths.items() if key != "ledger"}
    if projects["default"].get("name") != "default":
        raise MigrationError("Default project name must be exactly 'default'")
    recipe_index(projects["default"], "Default")
    archive_indexes: dict[str, dict[str, dict[str, Any]]] = {}
    for status, (_, expected_name) in ARCHIVE_SPECS.items():
        archive_indexes[status] = validate_archive(
            projects[status], expected_name, status, reviews, status
        )
    archive_indexes["maybe"] = validate_archive(
        projects["maybe"], {"Deferred", "maybe recipes"}, "maybe", reviews, "Deferred"
    )
    validate_archive_partition(archive_indexes, "source review archives")

    rejected_index = archive_indexes["rejected"]
    if set(DEFERRED_RECIPE_IDS) - set(rejected_index):
        raise MigrationError(
            "Deferred candidates are absent from Rejected: "
            + ", ".join(sorted(set(DEFERRED_RECIPE_IDS) - set(rejected_index)))
        )
    for recipe_id in sorted(DEFERRED_RECIPE_IDS):
        record = reviews[recipe_id]
        if record.get("status") != "rejected" or record.get("reason") != "manual":
            raise MigrationError(f"Candidate is no longer rejected/manual: {recipe_id}")

    staged_ledger = copy.deepcopy(ledger)
    for recipe_id in DEFERRED_RECIPE_IDS:
        record = staged_ledger["reviews"][recipe_id]
        record["status"] = "maybe"
        record["reason"] = "maybe"

    moved_cards = [
        copy.deepcopy(card)
        for card in projects["rejected"]["recipes"]
        if card["recipeId"] in DEFERRED_RECIPE_IDS
    ]
    staged_rejected = copy.deepcopy(projects["rejected"])
    staged_rejected["recipes"] = [
        card for card in staged_rejected["recipes"] if card["recipeId"] not in DEFERRED_RECIPE_IDS
    ]
    staged_deferred = copy.deepcopy(projects["maybe"])
    staged_deferred["name"] = "Deferred"
    staged_deferred["recipes"] = list(staged_deferred["recipes"]) + moved_cards

    staged_reviews = staged_ledger["reviews"]
    staged_indexes = {
        "rejected": validate_archive(
            staged_rejected, "rejected recipes", "rejected", staged_reviews, "staged Rejected"
        ),
        "maybe": validate_archive(
            staged_deferred, "Deferred", "maybe", staged_reviews, "staged Deferred"
        ),
        "approved": validate_archive(
            projects["approved"], "approved recipes", "approved", staged_reviews, "Approved"
        ),
        "disabled": validate_archive(
            projects["disabled"], "disabled recipes", "disabled", staged_reviews, "Disabled"
        ),
    }
    validate_archive_partition(staged_indexes, "staged review archives")

    output_counts = Counter(
        record.get("status") for record in staged_reviews.values() if isinstance(record, dict)
    )
    final_output_paths = {
        "ledger": output_dir / "default.recipe_reviews.json",
        "default": output_dir / "default.json",
        "approved": output_dir / "approved_recipes.json",
        "rejected": output_dir / "rejected_recipes.json",
        "deferred": output_dir / "Deferred.json",
        "disabled": output_dir / "disabled_recipes.json",
    }
    manifest: dict[str, Any] = {
        "schemaVersion": 1,
        "sourcePack": str(pack_dir),
        "selectionRationale": (
            "26 reviews whose notes show the card could not be evaluated because its item, "
            "function, ingredient, or custom recipe layout was not identifiable; this includes "
            "the exact Idk notes plus the two missing-layout notes and winding-machine uncertainty"
        ),
        "sourceFiles": {
            key: {"path": str(path), "sha256": sha256_file(path)}
            for key, path in source_paths.items()
        },
        "candidateRecipeIds": sorted(DEFERRED_RECIPE_IDS),
        "candidateRecords": {
            recipe_id: {
                "uid": reviews[recipe_id].get("uid"),
                "oldStatus": reviews[recipe_id].get("status"),
                "oldReason": reviews[recipe_id].get("reason"),
                "note": reviews[recipe_id].get("note"),
                "cardSha256": reviews[recipe_id].get("cardSha256"),
            }
            for recipe_id in sorted(DEFERRED_RECIPE_IDS)
        },
        "sourceCounts": dict(counts),
        "outputCounts": dict(output_counts),
        "archiveCounts": {
            "approved": len(projects["approved"]["recipes"]),
            "rejected": len(staged_rejected["recipes"]),
            "deferred": len(staged_deferred["recipes"]),
            "disabled": len(projects["disabled"]["recipes"]),
        },
    }

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=str(output_dir.parent))
    )
    try:
        write_json(temporary / "default.recipe_reviews.json", staged_ledger)
        write_json(temporary / "rejected_recipes.json", staged_rejected)
        write_json(temporary / "Deferred.json", staged_deferred)
        for key, filename in (
            ("default", "default.json"),
            ("approved", "approved_recipes.json"),
            ("disabled", "disabled_recipes.json"),
        ):
            shutil.copyfile(source_paths[key], temporary / filename)
        manifest["outputFiles"] = {
            key: {
                "path": str(final_path),
                "sha256": sha256_file(temporary / final_path.name),
            }
            for key, final_path in final_output_paths.items()
        }
        write_json(temporary / "migration_manifest.json", manifest)
        os.replace(temporary, output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    manifest = migrate(args.pack_dir, args.output_dir)
    print(json.dumps(manifest["outputCounts"], sort_keys=True))
    print(json.dumps(manifest["archiveCounts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
