#!/usr/bin/env python3
"""Build the deterministic Mekanism pre-nuclear integration report.

Before integration it emits the reviewed append payload. After integration it
validates exact source ownership and emits a deterministic no-op report. It
intentionally has no ``--apply`` mode.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "MEKANISM_PRE_NUCLEAR_MACHINE_CHAIN_AUDIT.plan.json"
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
DEFAULT_PHYSICAL_TIERS = PROJECT / "progression/physical_recipe_tiers.json"

SEED_RECIPE_FIELDS = (
    "id",
    "node",
    "phase",
    "order",
    "type",
    "comment",
    "machine",
    "inputs",
    "output",
    "outputs",
    "remove",
    "exclusive_output",
    "depends_on",
)


class PatchPlanError(ValueError):
    """Raised when reviewed patch preconditions no longer match the project."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise PatchPlanError(f"expected a JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def validate_physical_authority(plan: dict[str, Any], physical_tiers_path: Path) -> None:
    scope = plan.get("scope")
    if not isinstance(scope, dict):
        raise PatchPlanError("plan scope must be an object")
    if scope.get("physical_tiers") != "progression/physical_recipe_tiers.json":
        raise PatchPlanError("physical tier authority path changed")
    expected = scope.get("physical_tiers_sha256")
    actual = sha256_file(physical_tiers_path)
    if actual != expected:
        raise PatchPlanError(
            f"physical tier authority hash changed: expected {expected}, got {actual}"
        )


def output_id(recipe: dict[str, Any]) -> str:
    output = recipe.get("output")
    if isinstance(output, dict):
        value = output.get("id")
    elif isinstance(output, str):
        value = output.split("x ", 1)[-1]
    else:
        value = None
    if not isinstance(value, str) or ":" not in value:
        raise PatchPlanError(f"recipe {recipe.get('id')!r} has no valid output")
    return value


def output_ids(recipe: dict[str, Any]) -> list[str]:
    """Return every concrete output from either supported seed spelling.

    TFMG Chemical Vat recipes use the canonical ``results`` field while the
    older manifest families use ``outputs``.  Treat the pair as strict aliases
    just like the compiler does: equal duplicate declarations are harmless,
    but conflicting declarations fail closed.
    """
    values: list[str] = []
    if "output" in recipe:
        values.append(output_id(recipe))
    has_outputs = "outputs" in recipe
    has_results = "results" in recipe
    if has_outputs and has_results and recipe["outputs"] != recipe["results"]:
        raise PatchPlanError(
            f"recipe {recipe.get('id')!r} defines conflicting outputs/results values"
        )
    outputs = recipe["outputs"] if has_outputs else recipe.get("results", [])
    if outputs is None:
        outputs = []
    if not isinstance(outputs, list):
        raise PatchPlanError(
            f"recipe {recipe.get('id')!r} outputs/results must be an array"
        )
    for output in outputs:
        if isinstance(output, dict):
            value = output.get("id")
        elif isinstance(output, str):
            value = output.split("x ", 1)[-1]
        else:
            value = None
        if not isinstance(value, str) or ":" not in value:
            raise PatchPlanError(f"recipe {recipe.get('id')!r} has an invalid plural output")
        values.append(value)
    if not values:
        raise PatchPlanError(f"recipe {recipe.get('id')!r} has no valid output")
    return values


def recipes_by_id(seed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    recipes = seed.get("recipes")
    if not isinstance(recipes, list):
        raise PatchPlanError("seed recipes must be an array")
    result: dict[str, dict[str, Any]] = {}
    for recipe in recipes:
        if not isinstance(recipe, dict) or not isinstance(recipe.get("id"), str):
            raise PatchPlanError("seed contains an invalid recipe entry")
        identity = recipe["id"]
        if identity in result:
            raise PatchPlanError(f"seed contains duplicate recipe id {identity}")
        result[identity] = recipe
    return result


def contracts_by_id(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    contracts = plan.get("replacement_contracts")
    if not isinstance(contracts, list):
        raise PatchPlanError("replacement_contracts must be an array")
    result: dict[str, dict[str, Any]] = {}
    claimed_outputs: set[str] = set()
    for contract in contracts:
        if not isinstance(contract, dict) or not isinstance(contract.get("id"), str):
            raise PatchPlanError("replacement_contracts contains an invalid entry")
        identity = contract["id"]
        if identity in result:
            raise PatchPlanError(f"duplicate replacement contract id {identity}")
        output = output_id(contract)
        if output in claimed_outputs:
            raise PatchPlanError(f"multiple replacement contracts claim {output}")
        claimed_outputs.add(output)
        result[identity] = contract
    return result


def seed_recipe(contract: dict[str, Any]) -> dict[str, Any]:
    """Strip audit-only annotations from one reviewed contract."""
    result = {
        field: copy.deepcopy(contract[field])
        for field in SEED_RECIPE_FIELDS
        if field in contract
    }
    if not result.get("depends_on"):
        result.pop("depends_on", None)
    return result


def assignment_unlocks(assignments: dict[str, Any], node: str) -> list[str]:
    nodes = assignments.get("nodes")
    if not isinstance(nodes, dict) or node not in nodes:
        raise PatchPlanError(f"assignment node is absent: {node}")
    entry = nodes[node]
    if not isinstance(entry, dict) or not isinstance(entry.get("unlocks"), list):
        raise PatchPlanError(f"assignment node has no unlock array: {node}")
    values = entry["unlocks"]
    if not all(isinstance(value, str) for value in values):
        raise PatchPlanError(f"assignment node contains a non-string unlock: {node}")
    return values


def validate_assignment_contract(plan: dict[str, Any], assignments: dict[str, Any]) -> None:
    contract = plan.get("assignment_contract")
    if not isinstance(contract, dict) or contract.get("changes") != []:
        raise PatchPlanError("assignment contract must remain a no-change audit")
    sequences = contract.get("required_relative_sequences")
    if not isinstance(sequences, dict):
        raise PatchPlanError("assignment relative sequences must be an object")
    observed: set[str] = set()
    for node, expected in sequences.items():
        if not isinstance(expected, list) or not expected:
            raise PatchPlanError(f"invalid assignment sequence for {node}")
        unlocks = assignment_unlocks(assignments, node)
        if any(unlocks.count(value) != 1 for value in expected):
            raise PatchPlanError(f"assignment sequence members are absent or duplicated: {node}")
        positions = [unlocks.index(value) for value in expected]
        if positions != sorted(positions):
            raise PatchPlanError(f"assignment relative order drifted: {node}")
        overlap = observed & set(expected)
        if overlap:
            raise PatchPlanError(f"outputs occur in multiple assignment sequences: {sorted(overlap)}")
        observed.update(expected)


def validate_preconditions(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers_path: Path = DEFAULT_PHYSICAL_TIERS,
) -> None:
    validate_physical_authority(plan, physical_tiers_path)
    status = plan.get("status")
    if status not in {"review_ready_no_shared_mutation", "implemented_in_seed"}:
        raise PatchPlanError("plan is neither review-ready nor implemented")
    contracts = contracts_by_id(plan)
    patch = plan.get("seed_patch_contract")
    if not isinstance(patch, dict):
        raise PatchPlanError("seed_patch_contract must be an object")
    append_ids = patch.get("append_recipe_ids")
    if not isinstance(append_ids, list) or set(append_ids) != set(contracts):
        raise PatchPlanError("append_recipe_ids must contain every contract exactly once")
    if len(append_ids) != len(set(append_ids)):
        raise PatchPlanError("append_recipe_ids contains duplicates")
    if patch.get("remove_source_recipe_override_outputs") != []:
        raise PatchPlanError("this batch must not mutate source_recipe_overrides")
    if patch.get("additional_removals") != []:
        raise PatchPlanError("this batch must not add removals outside its recipe contracts")

    current = recipes_by_id(seed)
    target_outputs = {output_id(contract) for contract in contracts.values()}
    overrides = seed.get("source_recipe_overrides")
    if not isinstance(overrides, dict):
        raise PatchPlanError("seed source_recipe_overrides must be an object")
    conflicting_overrides = sorted(target_outputs & set(overrides))
    if conflicting_overrides:
        raise PatchPlanError(
            f"reviewed outputs unexpectedly have source overrides: {conflicting_overrides}"
        )
    validate_assignment_contract(plan, assignments)
    if status == "review_ready_no_shared_mutation":
        collisions = sorted(set(append_ids) & set(current))
        if collisions:
            raise PatchPlanError(f"reviewed recipe ids are already present in seed: {collisions}")
        existing_outputs = {
            output
            for recipe in current.values()
            for output in output_ids(recipe)
        }
        collisions = sorted(existing_outputs & target_outputs)
        if collisions:
            raise PatchPlanError(f"reviewed outputs already have explicit seed owners: {collisions}")
        return

    for identity in append_ids:
        actual = current.get(identity)
        expected = seed_recipe(contracts[identity])
        if actual is None:
            raise PatchPlanError(f"implemented recipe is absent from seed: {identity}")
        if actual != expected:
            raise PatchPlanError(f"implemented recipe differs from reviewed contract: {identity}")
        output = output_id(contracts[identity])
        owners = [
            candidate_id
            for candidate_id, recipe in current.items()
            if output in output_ids(recipe)
        ]
        if owners != [identity]:
            raise PatchPlanError(f"implemented output owner set changed for {output}: {owners}")


def build_patch_plan(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers_path: Path = DEFAULT_PHYSICAL_TIERS,
) -> dict[str, Any]:
    validate_preconditions(plan, seed, assignments, physical_tiers_path)
    contracts = contracts_by_id(plan)
    append_ids = plan["seed_patch_contract"]["append_recipe_ids"]
    implemented = plan.get("status") == "implemented_in_seed"
    return {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "mode": "implemented_source_owned_noop" if implemented else "review_only_no_shared_mutation",
        "preconditions": {
            "physical_tier_authority": {
                "path": plan["scope"]["physical_tiers"],
                "sha256": plan["scope"]["physical_tiers_sha256"],
            },
            "recipe_ids_absent": [] if implemented else copy.deepcopy(append_ids),
            "recipe_ids_match_reviewed_contracts": copy.deepcopy(append_ids) if implemented else [],
            "outputs_without_explicit_seed_owner": [] if implemented else [
                output_id(contracts[identity]) for identity in append_ids
            ],
            "assignment_sequences_unchanged": copy.deepcopy(
                plan["assignment_contract"]["required_relative_sequences"]
            ),
        },
        "seed": {
            "append_recipes": [] if implemented else [seed_recipe(contracts[identity]) for identity in append_ids],
            "remove_source_recipe_override_outputs": [],
            "additional_removals": [],
        },
        "assignments": {"changes": []},
        "expected_effect": {
            "explicit_recipe_owners_added": len(append_ids),
            "automatic_recipe_owners_suppressed": len(plan["current_automatic_owners"]),
            "exact_stock_recipe_removals": sum(
                len(contract.get("remove", [])) for contract in contracts.values()
            ),
            "assignment_changes": 0,
        },
    }


def apply_patch_to_copies(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers_path: Path = DEFAULT_PHYSICAL_TIERS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply the reviewed recipe append only to deep copies for proof builds."""
    patch = build_patch_plan(plan, seed, assignments, physical_tiers_path)
    staged_seed = copy.deepcopy(seed)
    staged_assignments = copy.deepcopy(assignments)
    staged_seed["recipes"].extend(copy.deepcopy(patch["seed"]["append_recipes"]))
    return staged_seed, staged_assignments


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--physical-tiers", type=Path, default=DEFAULT_PHYSICAL_TIERS)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate all deterministic preconditions without emitting the JSON plan.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional review artifact; this never edits the supplied seed or assignments.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        patch = build_patch_plan(
            load_json(args.plan.resolve()),
            load_json(args.seed.resolve()),
            load_json(args.assignments.resolve()),
            args.physical_tiers.resolve(),
        )
    except (OSError, json.JSONDecodeError, PatchPlanError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if args.check:
        if args.output:
            print("ERROR: --check and --output are mutually exclusive", file=sys.stderr)
            return 2
        print("OK: Mekanism pre-nuclear deterministic patch preconditions passed")
        return 0
    encoded = json.dumps(patch, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.resolve().write_text(encoded, encoding="utf-8")
        print(f"Wrote non-mutating patch plan: {args.output.resolve()}")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
