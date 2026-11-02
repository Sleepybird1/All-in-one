#!/usr/bin/env python3
"""Build a deterministic TFMG heavy/electrical integration report.

Before integration the command describes the reviewed patch. After integration
it validates the exact source-owned state and emits a deterministic no-op
report. It deliberately has no ``--apply`` mode.
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
DEFAULT_PLAN = PROJECT / "TFMG_HEAVY_ELECTRICAL_REDESIGN_AUDIT.plan.json"
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
    "pattern",
    "key",
    "inputs",
    "output",
    "outputs",
    "remove",
    "exclusive_output",
    "depends_on",
)


class PatchPlanError(ValueError):
    """Raised when the reviewed preconditions no longer match the project."""


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
    outputs: set[str] = set()
    for contract in contracts:
        if not isinstance(contract, dict) or not isinstance(contract.get("id"), str):
            raise PatchPlanError("replacement_contracts contains an invalid entry")
        identity = contract["id"]
        if identity in result:
            raise PatchPlanError(f"duplicate replacement contract id {identity}")
        output = output_id(contract)
        if output in outputs:
            raise PatchPlanError(f"multiple replacement contracts claim {output}")
        outputs.add(output)
        result[identity] = contract
    return result


def seed_recipe(contract: dict[str, Any]) -> dict[str, Any]:
    """Strip audit-only annotations from one reviewed recipe contract."""
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
    unlocks = entry["unlocks"]
    if not all(isinstance(value, str) for value in unlocks):
        raise PatchPlanError(f"assignment node contains a non-string unlock: {node}")
    return unlocks


def validate_preconditions(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers_path: Path = DEFAULT_PHYSICAL_TIERS,
) -> None:
    validate_physical_authority(plan, physical_tiers_path)
    status = plan.get("status")
    if status not in {"review_ready_no_shared_mutation", "implemented_in_seed"}:
        raise PatchPlanError("plan is neither review-ready nor implemented")
    contracts = contracts_by_id(plan)
    patch_contract = plan.get("seed_patch_contract")
    if not isinstance(patch_contract, dict):
        raise PatchPlanError("seed_patch_contract must be an object")
    append_ids = patch_contract.get("append_recipe_ids")
    if not isinstance(append_ids, list) or set(append_ids) != set(contracts):
        raise PatchPlanError("append_recipe_ids must contain every contract exactly once")
    if len(append_ids) != len(set(append_ids)):
        raise PatchPlanError("append_recipe_ids contains duplicates")

    overrides = seed.get("source_recipe_overrides")
    if not isinstance(overrides, dict):
        raise PatchPlanError("seed source_recipe_overrides must be an object")
    remove_overrides = patch_contract.get("remove_source_recipe_override_outputs")
    if remove_overrides != ["tfmg:engine_cylinder"]:
        raise PatchPlanError("the engine-cylinder source override removal contract drifted")
    move = plan.get("assignment_patch")
    if not isinstance(move, dict):
        raise PatchPlanError("assignment_patch must be an object")
    value = move.get("move_output")
    source = assignment_unlocks(assignments, str(move.get("from_node")))
    target = assignment_unlocks(assignments, str(move.get("to_node")))
    after = move.get("insert_after")
    if target.count(after) != 1:
        raise PatchPlanError("assignment insertion anchor must occur exactly once")

    current = recipes_by_id(seed)
    if status == "review_ready_no_shared_mutation":
        collisions = sorted(set(append_ids) & set(current))
        if collisions:
            raise PatchPlanError(f"reviewed recipe ids are already present in seed: {collisions}")
        current_outputs = {
            output
            for recipe in current.values()
            for output in output_ids(recipe)
        }
        output_collisions = sorted(
            {output_id(contract) for contract in contracts.values()} & current_outputs
        )
        if output_collisions:
            raise PatchPlanError(f"reviewed outputs already have explicit seed owners: {output_collisions}")
        if overrides.get("tfmg:engine_cylinder") != "tfmg:engine_cylinder_spark_plug":
            raise PatchPlanError("the reviewed engine-cylinder source override is absent or changed")
        if source.count(value) != 1:
            raise PatchPlanError("assignment move source must contain the cylinder exactly once")
        if value in target:
            raise PatchPlanError("assignment move target already contains the cylinder")
        return

    for identity in append_ids:
        expected = seed_recipe(contracts[identity])
        actual = current.get(identity)
        if actual is None:
            raise PatchPlanError(f"implemented recipe is absent from seed: {identity}")
        if actual != expected:
            raise PatchPlanError(f"implemented recipe differs from reviewed contract: {identity}")
    for identity in append_ids:
        output = output_id(contracts[identity])
        owners = [
            candidate_id for candidate_id, recipe in current.items()
            if output in output_ids(recipe)
        ]
        if owners != [identity]:
            raise PatchPlanError(f"implemented output owner set changed for {output}: {owners}")
    if "tfmg:engine_cylinder" in overrides:
        raise PatchPlanError("implemented seed restored the removed engine-cylinder source override")
    if value in source:
        raise PatchPlanError("implemented assignment still contains the cylinder in its old node")
    if target.count(value) != 1 or target.index(value) != target.index(after) + 1:
        raise PatchPlanError("implemented assignment does not place the cylinder after its diesel predecessor")


def build_patch_plan(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers_path: Path = DEFAULT_PHYSICAL_TIERS,
) -> dict[str, Any]:
    validate_preconditions(plan, seed, assignments, physical_tiers_path)
    contracts = contracts_by_id(plan)
    append_ids = plan["seed_patch_contract"]["append_recipe_ids"]
    move = copy.deepcopy(plan["assignment_patch"])
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
            "recipe_ids_match_reviewed_contracts": append_ids if implemented else [],
            "recipe_ids_absent": [] if implemented else append_ids,
            "source_recipe_override_absent": ["tfmg:engine_cylinder"] if implemented else [],
            "source_recipe_override_equals": {} if implemented else {
                "tfmg:engine_cylinder": "tfmg:engine_cylinder_spark_plug"
            },
            "assignment_output_position": "after tfmg:diesel_engine_cylinder in CR01 — Diesel Engines" if implemented else "present only in CR01 — Early Combusion Engines",
        },
        "seed": {
            "append_recipes": [] if implemented else [seed_recipe(contracts[identity]) for identity in append_ids],
            "remove_source_recipe_override_outputs": [] if implemented else copy.deepcopy(
                plan["seed_patch_contract"]["remove_source_recipe_override_outputs"]
            ),
            "additional_removals": [],
        },
        "assignments": {"move": None if implemented else move},
        "expected_effect": {
            "explicit_recipe_owners_added": len(append_ids),
            "automatic_recipe_owners_suppressed": len(plan["current_automatic_owners"]),
            "exact_stock_recipe_removals": sum(
                len(contract.get("remove", [])) for contract in contracts.values()
            ),
            "retained_stateful_stock_recipes": plan["compiled_contract"][
                "retained_recipe_ids"
            ],
        },
    }


def apply_patch_to_copies(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any],
    physical_tiers_path: Path = DEFAULT_PHYSICAL_TIERS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply the reviewed plan only to deep copies for validation/tests."""
    patch = build_patch_plan(plan, seed, assignments, physical_tiers_path)
    staged_seed = copy.deepcopy(seed)
    staged_assignments = copy.deepcopy(assignments)
    if patch["mode"] == "implemented_source_owned_noop":
        return staged_seed, staged_assignments
    staged_seed["recipes"].extend(copy.deepcopy(patch["seed"]["append_recipes"]))
    for output in patch["seed"]["remove_source_recipe_override_outputs"]:
        staged_seed["source_recipe_overrides"].pop(output)

    move = patch["assignments"]["move"]
    source = assignment_unlocks(staged_assignments, move["from_node"])
    target = assignment_unlocks(staged_assignments, move["to_node"])
    source.remove(move["move_output"])
    target.insert(target.index(move["insert_after"]) + 1, move["move_output"])
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
        help="Optional review artifact. Omit to print JSON; this never edits shared inputs.",
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
        print("OK: TFMG heavy/electrical deterministic patch preconditions passed")
        return 0
    text = json.dumps(patch, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.resolve().write_text(text, encoding="utf-8")
        print(f"Wrote non-mutating patch plan: {args.output.resolve()}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
