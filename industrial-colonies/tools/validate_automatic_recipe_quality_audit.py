#!/usr/bin/env python3
"""Validate the pinned, read-only automatic managed-recipe quality audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
DEFAULT_MANAGED = PROJECT / "build-current-audit" / "managed.json"
DEFAULT_REPORT = PROJECT / "build-current-audit" / "report.json"
DEFAULT_MARKDOWN = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.md"

EXPECTED_MANAGED_SHA256 = "548ADCDB80947B64B57B539E1314C195C2C18BCC07AFE164595C4B7E7ABEFEA6"
EXPECTED_REPORT_SHA256 = "4BBC6310A29D2FA839F08D6D73452FA4224B728A6285234707C7F1F746D42CE9"
EXPECTED_CLASSIFICATION_SHA256 = "3C9F2010E43BE839066461CCA0795E3167A27EF8B8F16E332571DA5325C78C2D"
EXPECTED_COUNTS = {
    "acceptable_stock_derived_utility": 27,
    "needs_source_owned_redesign": 81,
    "redundant_should_retire": 8,
    "runtime_artifact_leave_stock": 56,
}
EXPECTED_DISPOSITIONS = {
    "acceptable_stock_derived_utility": "keep_automatic_exact_stock",
    "needs_source_owned_redesign": "replace_with_source_owned_contract",
    "redundant_should_retire": "retire_output_after_route_parity_check",
    "runtime_artifact_leave_stock": "retire_automatic_owner_preserve_exact_source",
}
EXPECTED_SOURCE_TYPES = {
    "create:mechanical_crafting": 1,
    "mekanism:mek_data": 8,
    "minecraft:crafting_shaped": 130,
    "minecraft:crafting_shapeless": 33,
}
EXPECTED_BATCHES = [
    (1, "tfmg_first_heavy_and_electrical", 8),
    (2, "digital_core_and_peripherals", 14),
    (3, "mekanism_pre_nuclear_machine_chain", 8),
    (4, "mekanism_universal_cable_tail", 3),
    (5, "ae2_high_energy_spatial_and_mega_core", 9),
    (6, "mekanism_nuclear_chemical_and_sps", 12),
    (7, "bigreactors_bulk_structures_and_controllers", 27),
]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one object")
    return value


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def is_gate_ring(recipe: Mapping[str, Any]) -> bool:
    pattern = recipe.get("pattern")
    return bool(
        recipe.get("type") == "mechanical_crafting"
        and isinstance(pattern, list)
        and len(pattern) == 5
        and pattern[0] == "ABABA"
        and pattern[4] == "ABABA"
        and all(isinstance(row, str) and len(row) == 5 for row in pattern)
        and pattern[1][0] == pattern[1][4] == "B"
        and pattern[2][0] == pattern[2][4] == "A"
        and pattern[3][0] == pattern[3][4] == "B"
    )


def classification_digest(entries: list[dict[str, Any]]) -> str:
    rows = [
        f"{entry.get('managed_id')}|{entry.get('classification')}"
        for entry in sorted(entries, key=lambda row: str(row.get("managed_id", "")))
    ]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest().upper()


def auto_managed(document: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(recipe["id"]): recipe
        for recipe in document.get("recipes", [])
        if isinstance(recipe, dict)
        and isinstance(recipe.get("id"), str)
        and recipe["id"].startswith("industrial_colonies:auto/")
    }


def auto_report(document: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row["managed_recipe"]): row
        for row in document.get("generated", [])
        if isinstance(row, dict)
        and isinstance(row.get("managed_recipe"), str)
        and row["managed_recipe"].startswith("industrial_colonies:auto/")
    }


def validate_plan(
    plan: dict[str, Any],
    managed: dict[str, Any],
    report: dict[str, Any],
    managed_hash: str = EXPECTED_MANAGED_SHA256,
    report_hash: str = EXPECTED_REPORT_SHA256,
    markdown: str | None = None,
) -> list[str]:
    failures: list[str] = []
    if plan.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if plan.get("status") != "read_only_quality_audit_complete":
        failures.append("status must remain read_only_quality_audit_complete")
    if plan.get("decision") != "KEEP_27_REDESIGN_81_RETIRE_8_LEAVE_STOCK_56":
        failures.append("decision summary drifted")

    scope = plan.get("scope", {})
    if scope.get("managed_sha256") != EXPECTED_MANAGED_SHA256 or managed_hash != EXPECTED_MANAGED_SHA256:
        failures.append("managed snapshot SHA-256 changed; regenerate and review the audit")
    if scope.get("report_sha256") != EXPECTED_REPORT_SHA256 or report_hash != EXPECTED_REPORT_SHA256:
        failures.append("report snapshot SHA-256 changed; regenerate and review the audit")

    managed_auto = auto_managed(managed)
    report_auto = auto_report(report)
    if set(managed_auto) != set(report_auto):
        failures.append("managed/report automatic owner sets differ")
    if len(managed_auto) != 172:
        failures.append(f"automatic snapshot must contain exactly 172 owners, found {len(managed_auto)}")

    raw_entries = plan.get("entries", [])
    entries = [entry for entry in raw_entries if isinstance(entry, dict)]
    if len(entries) != len(raw_entries):
        failures.append("every plan entry must be an object")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        identity = entry.get("managed_id")
        if not isinstance(identity, str):
            failures.append("plan entry missing string managed_id")
            continue
        if identity in by_id:
            failures.append(f"duplicate plan entry: {identity}")
        by_id[identity] = entry
    if set(by_id) != set(managed_auto):
        failures.append(
            "plan entry coverage differs from the automatic snapshot: "
            f"missing={sorted(set(managed_auto) - set(by_id))}, extra={sorted(set(by_id) - set(managed_auto))}"
        )

    for identity in sorted(set(by_id) & set(managed_auto) & set(report_auto)):
        entry = by_id[identity]
        recipe = managed_auto[identity]
        source = report_auto[identity]
        expected = {
            "output": source.get("output"),
            "managed_output": recipe.get("output"),
            "phase": source.get("phase"),
            "node": source.get("node"),
            "source_recipe_id": source.get("source_recipe"),
            "source_type": source.get("source_type"),
            "managed_type": recipe.get("type"),
            "exact_removals": source.get("removals", []),
            "stock_ingredients": source.get("stock_ingredients", []),
            "managed_dependencies": source.get("depends_on", []),
            "generic_gate_ring": is_gate_ring(recipe),
        }
        for field, value in expected.items():
            if entry.get(field) != value:
                failures.append(f"{identity}: {field} does not match pinned snapshot evidence")
        category = entry.get("classification")
        if category not in EXPECTED_DISPOSITIONS:
            failures.append(f"{identity}: unknown classification {category!r}")
        elif entry.get("disposition") != EXPECTED_DISPOSITIONS[category]:
            failures.append(f"{identity}: disposition does not match classification")
        if not isinstance(entry.get("rationale"), str) or len(entry["rationale"].strip()) < 40:
            failures.append(f"{identity}: rationale is missing or too weak")

    actual_counts = Counter(entry.get("classification") for entry in entries)
    if dict(sorted(actual_counts.items())) != EXPECTED_COUNTS:
        failures.append(f"classification totals changed: {dict(sorted(actual_counts.items()))}")
    if plan.get("classification_counts") != EXPECTED_COUNTS:
        failures.append("declared classification_counts drifted")
    if classification_digest(entries) != EXPECTED_CLASSIFICATION_SHA256:
        failures.append("the exact ID-by-ID classification decisions changed")

    ring_entries = [entry for entry in entries if entry.get("generic_gate_ring") is True]
    mechanical_entries = [entry for entry in entries if entry.get("managed_type") == "mechanical_crafting"]
    actual_mechanical = [recipe for recipe in managed_auto.values() if recipe.get("type") == "mechanical_crafting"]
    actual_rings = [recipe for recipe in actual_mechanical if is_gate_ring(recipe)]
    if (
        len(mechanical_entries) != 146
        or len(actual_mechanical) != 146
        or scope.get("automatic_mechanical_crafting_count") != 146
    ):
        failures.append("automatic Mechanical Crafting count must remain 146")
    if (
        len(ring_entries) != 145
        or len(actual_rings) != 145
        or scope.get("generic_gate_ring_count") != 145
    ):
        failures.append("generic A/B gate-ring count must remain 145")
    acceptable_rings = [
        entry["managed_id"]
        for entry in ring_entries
        if entry.get("classification") == "acceptable_stock_derived_utility"
    ]
    if acceptable_rings:
        failures.append(f"generic gate rings cannot be accepted as finished design: {acceptable_rings}")
    non_ring_mechanical = [entry["managed_id"] for entry in mechanical_entries if not entry["generic_gate_ring"]]
    if non_ring_mechanical != ["industrial_colonies:auto/create/crushing_wheel"]:
        failures.append(f"unexpected non-ring automatic Mechanical Crafting set: {non_ring_mechanical}")

    source_types = Counter(entry.get("source_type") for entry in entries)
    actual_source_types = Counter(row.get("source_type") for row in report_auto.values())
    if (
        dict(sorted(source_types.items())) != EXPECTED_SOURCE_TYPES
        or dict(sorted(actual_source_types.items())) != EXPECTED_SOURCE_TYPES
    ):
        failures.append(
            "automatic source-type evidence drifted: "
            f"plan={dict(sorted(source_types.items()))}, report={dict(sorted(actual_source_types.items()))}"
        )
    if scope.get("source_type_counts") != EXPECTED_SOURCE_TYPES:
        failures.append("declared source_type_counts drifted")

    batches = plan.get("implementation_batches", [])
    observed_batch_signature = [
        (batch.get("priority"), batch.get("id"), len(batch.get("outputs", [])))
        for batch in batches
        if isinstance(batch, dict)
    ]
    if observed_batch_signature != EXPECTED_BATCHES:
        failures.append(f"implementation batch signature changed: {observed_batch_signature}")
    batched_ids: list[str] = []
    batched_outputs: list[str] = []
    for batch in batches:
        if not isinstance(batch, dict):
            continue
        outputs = batch.get("outputs", [])
        managed_ids = batch.get("managed_ids", [])
        installed = batch.get("installed_recipe_ids", [])
        if not (len(outputs) == len(managed_ids) == len(installed)):
            failures.append(f"{batch.get('id')}: output/owner/source columns differ in length")
            continue
        if not batch.get("prerequisite_outputs"):
            failures.append(f"{batch.get('id')}: prerequisite capability list is empty")
        if not batch.get("recommended_environments"):
            failures.append(f"{batch.get('id')}: encased manufacturing roles are empty")
        if len(batch.get("cycle_risks", [])) < 3:
            failures.append(f"{batch.get('id')}: at least three cycle risks are required")
        for output, managed_id, source_id in zip(outputs, managed_ids, installed):
            entry = by_id.get(managed_id)
            if entry is None:
                failures.append(f"{batch.get('id')}: unknown managed owner {managed_id}")
                continue
            if entry.get("classification") != "needs_source_owned_redesign":
                failures.append(f"{batch.get('id')}: non-redesign owner entered a source-owned batch: {managed_id}")
            if entry.get("output") != output or entry.get("source_recipe_id") != source_id:
                failures.append(f"{batch.get('id')}: output/source mapping drifted for {managed_id}")
            batched_ids.append(managed_id)
            batched_outputs.append(output)
    if len(batched_ids) != len(set(batched_ids)):
        failures.append("a redesign owner appears in more than one implementation batch")
    redesign_ids = {
        entry["managed_id"]
        for entry in entries
        if entry.get("classification") == "needs_source_owned_redesign"
    }
    if set(batched_ids) != redesign_ids:
        failures.append(
            "implementation batches must cover every redesign exactly once: "
            f"missing={sorted(redesign_ids - set(batched_ids))}, extra={sorted(set(batched_ids) - redesign_ids)}"
        )

    redundant = [
        entry for entry in entries if entry.get("classification") == "redundant_should_retire"
    ]
    if not all(
        entry.get("output", "").startswith(("createmetallurgy:", "modernfoundry:"))
        for entry in redundant
    ):
        failures.append("only the eight audited duplicate foundry endpoints may be retired")
    if not all("route" in str(entry.get("disposition")) for entry in redundant):
        failures.append("duplicate foundries must retain the route-parity guard")

    declared_phase_counts = plan.get("phase_counts", {})
    actual_phase_counts: dict[str, dict[str, int]] = {}
    for phase in managed.get("phase_order", []):
        actual_phase_counts[str(phase)] = dict(
            sorted(
                Counter(
                    entry.get("classification")
                    for entry in entries
                    if entry.get("phase") == phase
                ).items()
            )
        )
    if declared_phase_counts != actual_phase_counts:
        failures.append("declared phase_counts do not match the ID-by-ID entries")

    if markdown is not None:
        required_fragments = [
            "145 of 146",
            "81 redesigns",
            "TFMG-first",
            "Complete ID-by-ID classification",
        ]
        for fragment in required_fragments:
            if fragment not in markdown:
                failures.append(f"Markdown audit is missing required summary fragment: {fragment!r}")
        for entry in entries:
            if f"`{entry.get('source_recipe_id')}`" not in markdown:
                failures.append(f"Markdown audit omits source recipe ID {entry.get('source_recipe_id')}")
                break

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--managed", type=Path, default=DEFAULT_MANAGED)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    plan = load_json(args.plan)
    managed = load_json(args.managed)
    report = load_json(args.report)
    markdown = args.markdown.read_text(encoding="utf-8")
    failures = validate_plan(
        plan,
        managed,
        report,
        file_sha256(args.managed),
        file_sha256(args.report),
        markdown,
    )
    if failures:
        print("Automatic recipe quality audit validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Automatic recipe quality audit validation passed")
    print("- 172 automatic owners classified exactly once")
    print("- 27 acceptable / 81 redesign / 8 retire / 56 leave stock")
    print("- 145 generic A/B gate rings identified among 146 automatic Mechanical Crafting recipes")
    print("- 7 source-owned implementation batches cover all 81 redesigns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
