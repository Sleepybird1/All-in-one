#!/usr/bin/env python3
"""Prove closure of the immutable 172-owner automatic recipe backlog."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


PROJECT = Path(__file__).resolve().parents[1]
PLAN = PROJECT / "AUTOMATIC_RECIPE_BACKLOG_CLOSURE.plan.json"
AUDIT = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
AUTO_PREFIX = "industrial_colonies:auto/"
EXPECTED_AUDIT_SHA256 = "BEA5CDFC80C152F479FA367E621D2E3F37D9CAEC6AA511347AA1D8D609868963"
EXPECTED_COUNTS = {
    "acceptable_stock_derived_utility": 27,
    "needs_source_owned_redesign": 81,
    "redundant_should_retire": 8,
    "runtime_artifact_leave_stock": 56,
}
EXPECTED_RETAINED_EXCEPTION = {
    "output": "tfmg:engine_cylinder",
    "artifact": "TFMG_HEAVY_ELECTRICAL_REDESIGN_AUDIT.plan.json",
    "source_owned_id": "industrial_colonies:tfmg_heavy_electrical/engine_cylinder",
    "retained_recipe_id": "tfmg:engine_cylinder_gas",
    "required_exclusive_output": False,
    "reason": "TFMG's gas-cylinder route transfers the installed fuel state and was explicitly retained by the implemented heavy/electrical review.",
}
EXPECTED_BATCHES = [
    {
        "batch_id": "tfmg_first_heavy_and_electrical",
        "artifact": "TFMG_HEAVY_ELECTRICAL_REDESIGN_AUDIT.plan.json",
        "output_count": 8,
        "allowed_statuses": ["implemented_in_seed"],
        "closure_status": "implemented_in_seed",
    },
    {
        "batch_id": "digital_core_and_peripherals",
        "artifact": "DIGITAL_CORE_PERIPHERALS_AUDIT.plan.json",
        "output_count": 14,
        "allowed_statuses": ["implemented_in_seed"],
        "closure_status": "implemented_in_seed",
    },
    {
        "batch_id": "mekanism_pre_nuclear_machine_chain",
        "artifact": "MEKANISM_PRE_NUCLEAR_MACHINE_CHAIN_AUDIT.plan.json",
        "output_count": 8,
        "allowed_statuses": ["implemented_in_seed"],
        "closure_status": "implemented_in_seed",
    },
    {
        "batch_id": "mekanism_universal_cable_tail",
        "artifact": "MEKANISM_UNIVERSAL_CABLE_TAIL_AUDIT.plan.json",
        "output_count": 3,
        "allowed_statuses": ["implemented_in_seed"],
        "closure_status": "implemented_in_seed",
    },
    {
        "batch_id": "ae2_high_energy_spatial_and_mega_core",
        "artifact": "AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.plan.json",
        "output_count": 9,
        "allowed_statuses": [
            "reviewed_patch_plan_not_applied",
            "implemented_in_seed",
        ],
        "closure_status": "implemented_in_seed",
    },
    {
        "batch_id": "mekanism_nuclear_chemical_and_sps",
        "artifact": "MEKANISM_NUCLEAR_CHEMICAL_SPS_AUDIT.plan.json",
        "output_count": 12,
        "allowed_statuses": [
            "reviewed_patch_plan_not_applied",
            "implemented_in_seed",
        ],
        "closure_status": "implemented_in_seed",
    },
    {
        "batch_id": "bigreactors_bulk_structures_and_controllers",
        "artifact": "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.plan.json",
        "output_count": 27,
        "allowed_statuses": [
            "review_ready_no_shared_mutation",
            "implemented_in_seed",
        ],
        "closure_status": "implemented_in_seed",
    },
]
EXPECTED_FOUNDRY_CONTRACT = {
    "artifact": "FOUNDRY_ROUTE_PARITY_AUDIT.plan.json",
    "status": "implemented",
    "output_count": 8,
    "exact_stock_removal_count": 9,
}
EXPECTED_LEAVE_STOCK_CONTRACT = {
    "artifact": "STOCK_UTILITY_RESTORATION_AUDIT.patch.json",
    "status": "implemented",
    "output_count": 56,
    "exact_installed_recipe_count": 77,
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def resource_id(value: Any) -> str:
    if isinstance(value, str):
        head, separator, tail = value.partition("x ")
        return tail.strip() if separator and head.strip().isdigit() else value.strip()
    if isinstance(value, Mapping) and isinstance(value.get("id"), str):
        return str(value["id"])
    return ""


def manifest_removals(manifest: Mapping[str, Any]) -> set[str]:
    result = {
        str(value)
        for value in manifest.get("additional_removals", [])
        if isinstance(value, str)
    }
    for recipe in manifest.get("recipes", []):
        if isinstance(recipe, Mapping):
            result.update(
                str(value)
                for value in recipe.get("remove", [])
                if isinstance(value, str)
            )
    return result


def recipes_by_id(value: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    result: dict[str, Mapping[str, Any]] = {}
    duplicates: list[str] = []
    for recipe in value.get("recipes", []):
        if not isinstance(recipe, Mapping) or not isinstance(recipe.get("id"), str):
            continue
        identity = str(recipe["id"])
        if identity in result:
            duplicates.append(identity)
        result[identity] = recipe
    return result, sorted(set(duplicates))


def contracts_by_output(
    artifact: Mapping[str, Any], failures: list[str], label: str
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    identities: set[str] = set()
    for contract in artifact.get("replacement_contracts", []):
        if not isinstance(contract, Mapping):
            failures.append(f"{label}: replacement contract is not an object")
            continue
        output = resource_id(contract.get("output"))
        identity = str(contract.get("id", ""))
        if not output or not identity or identity.startswith(AUTO_PREFIX):
            failures.append(f"{label}: invalid source-owned contract {identity!r}/{output!r}")
            continue
        if output in result:
            failures.append(f"{label}: duplicate replacement output {output}")
        if identity in identities:
            failures.append(f"{label}: duplicate source-owned contract ID {identity}")
        identities.add(identity)
        result[output] = contract
    return result


def retained_same_output_recipe(
    contract: Mapping[str, Any],
    immutable: Mapping[str, Any],
    failures: list[str],
    output: str,
) -> str:
    """Return the one reviewed retained source while keeping the exception exact."""
    retained = contract.get("retained_same_output_recipe")
    if retained is None:
        return ""
    if not isinstance(retained, str) or not retained:
        failures.append(f"{output}: retained same-output recipe must be a resource ID")
        return ""
    immutable_removals = {
        str(value) for value in immutable.get("exact_removals", [])
    }
    contract_removals = {
        str(value) for value in contract.get("remove", [])
    }
    if retained not in immutable_removals:
        failures.append(
            f"{output}: retained same-output recipe is not an immutable stock source"
        )
    if retained in contract_removals:
        failures.append(f"{output}: retained same-output recipe is also removed")
    if contract.get("exclusive_output") is not False:
        failures.append(
            f"{output}: retained same-output recipe requires exclusive_output=false"
        )
    return retained


def load_artifacts(plan: Mapping[str, Any], project: Path = PROJECT) -> dict[str, dict[str, Any]]:
    names = {
        str(row.get("artifact"))
        for row in plan.get("redesign_batches", [])
        if isinstance(row, Mapping)
    }
    names.add(str(plan.get("foundry_contract", {}).get("artifact")))
    names.add(str(plan.get("leave_stock_contract", {}).get("artifact")))
    return {name: load_json(project / name) for name in sorted(names)}


def evaluate(
    plan: Mapping[str, Any],
    audit: Mapping[str, Any],
    seed: Mapping[str, Any],
    manifest: Mapping[str, Any],
    artifacts: Mapping[str, Mapping[str, Any]],
) -> tuple[list[str], list[str], dict[str, Any]]:
    failures: list[str] = []
    open_items: list[str] = []

    authority = plan.get("authority", {})
    if plan.get("schema_version") != 1 or plan.get("plan_id") != "automatic_recipe_backlog_closure":
        failures.append("closure plan identity/schema drifted")
    if plan.get("status") not in {
        "proof_ready_pending_final_authoritative_manifest",
        "closed_authoritative_manifest",
    }:
        failures.append(f"unsupported closure-plan status {plan.get('status')!r}")
    if authority.get("sha256") != EXPECTED_AUDIT_SHA256:
        failures.append("closure plan no longer pins the immutable automatic audit")
    if authority.get("entry_count") != 172 or authority.get("classification_counts") != EXPECTED_COUNTS:
        failures.append("closure plan authority counts drifted")
    if plan.get("retained_same_output_exception") != EXPECTED_RETAINED_EXCEPTION:
        failures.append("reviewed TFMG retained same-output exception drifted")

    entries = [row for row in audit.get("entries", []) if isinstance(row, Mapping)]
    entry_ids = [str(row.get("managed_id", "")) for row in entries]
    entry_outputs = [str(row.get("output", "")) for row in entries]
    counts = Counter(str(row.get("classification", "")) for row in entries)
    if audit.get("status") != "read_only_quality_audit_complete":
        failures.append("immutable automatic audit status drifted")
    if len(entries) != 172 or len(set(entry_ids)) != 172 or len(set(entry_outputs)) != 172:
        failures.append("immutable audit must contain 172 unique IDs and outputs")
    if dict(counts) != EXPECTED_COUNTS:
        failures.append(f"immutable audit classification counts drifted: {dict(counts)}")
    if set(entry_ids) != {
        identity
        for identity in entry_ids
        if identity.startswith(AUTO_PREFIX)
    }:
        failures.append("immutable audit contains a non-automatic managed ID")

    by_class = {
        classification: {
            str(row["output"]): row
            for row in entries
            if row.get("classification") == classification
        }
        for classification in EXPECTED_COUNTS
    }
    all_audited_auto = set(entry_ids)
    acceptable = by_class["acceptable_stock_derived_utility"]
    redesigned = by_class["needs_source_owned_redesign"]
    foundry = by_class["redundant_should_retire"]
    leave_stock = by_class["runtime_artifact_leave_stock"]

    audit_batches = {
        str(row.get("id")): row
        for row in audit.get("implementation_batches", [])
        if isinstance(row, Mapping)
    }
    batch_rows = [row for row in plan.get("redesign_batches", []) if isinstance(row, Mapping)]
    if batch_rows != EXPECTED_BATCHES:
        failures.append("closure plan redesign batch mapping drifted")
    if len(batch_rows) != 7 or len({str(row.get("batch_id")) for row in batch_rows}) != 7:
        failures.append("closure plan must map exactly seven redesign batches")
    mapped_redesign_outputs: set[str] = set()
    redesign_owners: dict[str, Mapping[str, Any]] = {}
    pending_batches: list[str] = []
    for row in batch_rows:
        batch_id = str(row.get("batch_id", ""))
        audit_batch = audit_batches.get(batch_id, {})
        expected_outputs = [str(value) for value in audit_batch.get("outputs", [])]
        expected_ids = [str(value) for value in audit_batch.get("managed_ids", [])]
        if len(expected_outputs) != row.get("output_count") or len(expected_ids) != row.get("output_count"):
            failures.append(f"{batch_id}: immutable batch count drifted")
        if set(expected_outputs) - set(redesigned):
            failures.append(f"{batch_id}: batch contains outputs outside redesign classification")
        if set(expected_ids) != {str(redesigned[output]["managed_id"]) for output in expected_outputs if output in redesigned}:
            failures.append(f"{batch_id}: batch automatic-ID coverage drifted")
        overlap = mapped_redesign_outputs & set(expected_outputs)
        if overlap:
            failures.append(f"{batch_id}: outputs overlap another batch: {sorted(overlap)}")
        mapped_redesign_outputs.update(expected_outputs)

        artifact_name = str(row.get("artifact", ""))
        artifact = artifacts.get(artifact_name, {})
        status = artifact.get("status")
        if status not in row.get("allowed_statuses", []):
            failures.append(f"{batch_id}: unsupported artifact status {status!r}")
        if status != row.get("closure_status"):
            pending_batches.append(batch_id)
            open_items.append(f"batch pending integration: {batch_id} ({status})")
        contracts = contracts_by_output(artifact, failures, batch_id)
        if set(contracts) != set(expected_outputs):
            failures.append(f"{batch_id}: replacement output coverage drifted")
        for output in expected_outputs:
            contract = contracts.get(output)
            immutable = redesigned.get(output)
            if contract is None or immutable is None:
                continue
            retained = retained_same_output_recipe(
                contract, immutable, failures, output
            )
            covered_sources = set(contract.get("remove", []))
            if retained:
                covered_sources.add(retained)
            if not set(immutable.get("exact_removals", [])) <= covered_sources:
                failures.append(f"{output}: redesigned contract lost immutable stock removal")
            redesign_owners[output] = contract
    if mapped_redesign_outputs != set(redesigned):
        failures.append("seven redesign batches do not partition all 81 outputs")
    observed_retained = [
        {
            "output": output,
            "source_owned_id": str(contract.get("id", "")),
            "retained_recipe_id": str(contract.get("retained_same_output_recipe", "")),
            "required_exclusive_output": contract.get("exclusive_output"),
        }
        for output, contract in redesign_owners.items()
        if contract.get("retained_same_output_recipe") is not None
    ]
    expected_retained = {
        key: EXPECTED_RETAINED_EXCEPTION[key]
        for key in (
            "output",
            "source_owned_id",
            "retained_recipe_id",
            "required_exclusive_output",
        )
    }
    if observed_retained != [expected_retained]:
        failures.append("redesign contracts no longer contain the one exact retained source")

    foundry_contract = plan.get("foundry_contract", {})
    if foundry_contract != EXPECTED_FOUNDRY_CONTRACT:
        failures.append("closure plan foundry contract mapping drifted")
    foundry_artifact = artifacts.get(str(foundry_contract.get("artifact", "")), {})
    if foundry_artifact.get("status") != foundry_contract.get("status"):
        failures.append("foundry closure artifact status drifted")
    foundry_owners = contracts_by_output(foundry_artifact, failures, "foundry")
    if set(foundry_owners) != set(foundry) or len(foundry_owners) != foundry_contract.get("output_count"):
        failures.append("foundry replacement output coverage drifted")
    expected_foundry_removals = {
        value for row in foundry.values() for value in row.get("exact_removals", [])
    }
    if set(foundry_artifact.get("exact_stock_removals", [])) != expected_foundry_removals:
        failures.append("foundry exact stock-removal inventory drifted")
    for output, contract in foundry_owners.items():
        immutable = foundry.get(output)
        if immutable is None:
            continue
        if not set(immutable.get("exact_removals", [])) <= set(contract.get("remove", [])):
            failures.append(f"{output}: foundry replacement lost exact stock removal")

    stock_contract = plan.get("leave_stock_contract", {})
    if stock_contract != EXPECTED_LEAVE_STOCK_CONTRACT:
        failures.append("closure plan leave-stock contract mapping drifted")
    stock_artifact = artifacts.get(str(stock_contract.get("artifact", "")), {})
    if stock_artifact.get("status") != stock_contract.get("status"):
        failures.append("leave-stock restoration artifact status drifted")
    stock_entries = {
        str(row.get("output")): row
        for row in stock_artifact.get("entries", [])
        if isinstance(row, Mapping)
    }
    if set(stock_entries) != set(leave_stock) or len(stock_entries) != stock_contract.get("output_count"):
        failures.append("leave-stock restoration output coverage drifted")
    exact_stock_ids = {
        str(value)
        for row in stock_entries.values()
        for value in row.get("exact_source_recipe_ids", [])
    }
    if len(exact_stock_ids) != stock_contract.get("exact_installed_recipe_count"):
        failures.append("leave-stock exact installed-recipe count drifted")
    for output, immutable in leave_stock.items():
        stock = stock_entries.get(output, {})
        if not set(immutable.get("exact_removals", [])) <= set(stock.get("exact_source_recipe_ids", [])):
            failures.append(f"{output}: restoration patch lost immutable stock source")
        if stock.get("automatic_managed_id") != immutable.get("managed_id"):
            failures.append(f"{output}: restoration patch automatic ID drifted")

    manifest_by_id, manifest_duplicates = recipes_by_id(manifest)
    seed_by_id, seed_duplicates = recipes_by_id(seed)
    if manifest_duplicates:
        failures.append(f"managed manifest repeats recipe IDs: {manifest_duplicates}")
    if seed_duplicates:
        failures.append(f"seed repeats recipe IDs: {seed_duplicates}")
    manifest_auto_ids = {
        identity for identity in manifest_by_id if identity.startswith(AUTO_PREFIX)
    }
    unknown_auto = sorted(manifest_auto_ids - all_audited_auto)
    if unknown_auto:
        failures.append(f"unclassified automatic owners exist: {unknown_auto}")
    approved_auto_ids = {str(row["managed_id"]) for row in acceptable.values()}
    for output, immutable in acceptable.items():
        identity = str(immutable["managed_id"])
        recipe = manifest_by_id.get(identity)
        if recipe is None:
            failures.append(f"approved automatic owner disappeared: {identity}")
            continue
        if resource_id(recipe.get("output")) != output:
            failures.append(f"approved automatic owner output drifted: {identity}")
    extra_auto = sorted(manifest_auto_ids - approved_auto_ids)
    if extra_auto:
        open_items.append(f"{len(extra_auto)} non-approved audited automatic owners remain")

    removals = manifest_removals(manifest)
    seed_excludes = {str(value) for value in seed.get("exclude_outputs", [])}
    seed_preserves = {str(value) for value in seed.get("preserve_recipe_ids", [])}
    closed_redesign: set[str] = set()
    for output, immutable in redesigned.items():
        old_id = str(immutable["managed_id"])
        contract = redesign_owners.get(output, {})
        source_id = str(contract.get("id", ""))
        source_manifest = manifest_by_id.get(source_id)
        source_seed = seed_by_id.get(source_id)
        retained = str(contract.get("retained_same_output_recipe", ""))
        required_removals = set(contract.get("remove", []))
        manifest_output_owners = {
            identity
            for identity, recipe in manifest_by_id.items()
            if resource_id(recipe.get("output")) == output
        }
        seed_output_owners = {
            identity
            for identity, recipe in seed_by_id.items()
            if resource_id(recipe.get("output")) == output
        }
        unexpected_non_auto = {
            identity
            for identity in manifest_output_owners
            if not identity.startswith(AUTO_PREFIX) and identity != source_id
        }
        unexpected_seed = seed_output_owners - {source_id}
        if unexpected_non_auto:
            failures.append(
                f"{output}: unexpected non-automatic managed producers: "
                f"{sorted(unexpected_non_auto)}"
            )
        if unexpected_seed:
            failures.append(
                f"{output}: unexpected source-seed producers: {sorted(unexpected_seed)}"
            )
        conditions = [
            old_id not in manifest_by_id,
            source_manifest is not None,
            source_seed is not None,
            source_manifest is not None and resource_id(source_manifest.get("output")) == output,
            manifest_output_owners == {source_id},
            seed_output_owners == {source_id},
            source_id not in removals,
            required_removals <= removals,
            not retained or retained not in removals,
        ]
        if source_manifest is not None and resource_id(source_manifest.get("output")) != output:
            failures.append(f"{output}: source-owned manifest producer output drifted: {source_id}")
        if source_seed is not None and resource_id(source_seed.get("output")) != output:
            failures.append(f"{output}: source-owned seed producer output drifted: {source_id}")
        if all(conditions):
            closed_redesign.add(output)
        else:
            open_items.append(f"redesign closure incomplete: {output}")

    closed_foundry: set[str] = set()
    for output, immutable in foundry.items():
        old_id = str(immutable["managed_id"])
        contract = foundry_owners.get(output, {})
        source_id = str(contract.get("id", ""))
        source_manifest = manifest_by_id.get(source_id)
        source_seed = seed_by_id.get(source_id)
        manifest_output_owners = {
            identity
            for identity, recipe in manifest_by_id.items()
            if resource_id(recipe.get("output")) == output
        }
        seed_output_owners = {
            identity
            for identity, recipe in seed_by_id.items()
            if resource_id(recipe.get("output")) == output
        }
        conditions = [
            old_id not in manifest_by_id,
            source_manifest is not None,
            source_seed is not None,
            source_manifest is not None and resource_id(source_manifest.get("output")) == output,
            manifest_output_owners == {source_id},
            seed_output_owners == {source_id},
            source_id not in removals,
            set(immutable.get("exact_removals", [])) <= removals,
        ]
        if source_manifest is not None and resource_id(source_manifest.get("output")) != output:
            failures.append(f"{output}: foundry manifest producer output drifted")
        if all(conditions):
            closed_foundry.add(output)
        else:
            open_items.append(f"foundry closure incomplete: {output}")

    closed_stock: set[str] = set()
    for output, immutable in leave_stock.items():
        old_id = str(immutable["managed_id"])
        exact_ids = set(stock_entries.get(output, {}).get("exact_source_recipe_ids", []))
        custom_owners = [
            identity
            for identity, recipe in manifest_by_id.items()
            if resource_id(recipe.get("output")) == output
        ]
        seed_custom_owners = [
            identity
            for identity, recipe in seed_by_id.items()
            if resource_id(recipe.get("output")) == output
        ]
        unexpected_non_auto = [
            identity
            for identity in custom_owners
            if not identity.startswith(AUTO_PREFIX)
        ]
        if unexpected_non_auto or seed_custom_owners:
            failures.append(
                f"{output}: leave-stock output has a source-owned managed producer"
            )
        conditions = [
            old_id not in manifest_by_id,
            output in seed_excludes,
            exact_ids <= seed_preserves,
            not (exact_ids & removals),
            not custom_owners,
            not seed_custom_owners,
        ]
        if all(conditions):
            closed_stock.add(output)
        else:
            open_items.append(f"leave-stock closure incomplete: {output}")

    if open_items and plan.get("status") == "closed_authoritative_manifest":
        failures.append("closure plan claims closed while proof items remain open")
    if not open_items and plan.get("status") != "closed_authoritative_manifest":
        open_items.append("closure plan status has not been promoted to closed")

    summary = {
        "immutable_entries": len(entries),
        "manifest_automatic_ids": len(manifest_auto_ids),
        "approved_automatic_present": len(approved_auto_ids & manifest_auto_ids),
        "redesign_closed": len(closed_redesign),
        "redesign_total": len(redesigned),
        "foundry_closed": len(closed_foundry),
        "foundry_total": len(foundry),
        "leave_stock_closed": len(closed_stock),
        "leave_stock_total": len(leave_stock),
        "pending_batches": pending_batches,
        "open_item_count": len(open_items),
        "failure_count": len(failures),
    }
    return failures, open_items, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--require-closed", action="store_true")
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    plan_path = args.plan.resolve() if args.plan else project / PLAN.name
    audit_path = args.audit.resolve() if args.audit else project / AUDIT.name
    seed_path = args.seed.resolve() if args.seed else project / "progression/managed_recipe_overhaul.seed.json"
    manifest_path = args.manifest.resolve() if args.manifest else project / "progression/managed_recipe_overhaul.json"
    try:
        plan = load_json(plan_path)
        audit = load_json(audit_path)
        if sha256(audit_path) != EXPECTED_AUDIT_SHA256:
            print("FAIL: immutable automatic audit SHA-256 drifted", file=sys.stderr)
            return 1
        artifacts = load_artifacts(plan, project)
        failures, open_items, summary = evaluate(
            plan,
            audit,
            load_json(seed_path),
            load_json(manifest_path),
            artifacts,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if args.report_json:
        args.report_json.write_text(
            json.dumps(
                {"status": "failed" if failures else "open" if open_items else "closed", "summary": summary, "failures": failures, "open": open_items},
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
    if failures:
        print(f"FAIL: automatic backlog closure contract has {len(failures)} error(s):", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    if open_items:
        print(
            "OPEN: automatic backlog proof is structurally valid but authoritative closure is incomplete."
        )
        print(json.dumps(summary, indent=2))
        for item in open_items[:20]:
            print(f" - {item}")
        if len(open_items) > 20:
            print(f" - ... {len(open_items) - 20} additional open item(s)")
        return 1 if args.require_closed else 0
    print("CLOSED: exactly 27 approved automatic owners remain; all 145 other audited owners satisfy their reviewed redesign, foundry, or leave-stock contracts.")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
