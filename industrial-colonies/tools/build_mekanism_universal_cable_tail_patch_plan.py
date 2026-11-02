#!/usr/bin/env python3
"""Build the reviewed Universal Cable tail patch without mutating authorities.

The builder intentionally has no ``--apply`` mode.  It emits the three recipe
appends and the exact dependency-ID substitutions required in the shared seed,
then leaves integration to the parent task's single-writer workflow.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "MEKANISM_UNIVERSAL_CABLE_TAIL_AUDIT.plan.json"
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"

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
    """Raised when the review plan no longer matches shared-file preconditions."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise PatchPlanError(f"expected a JSON object: {path}")
    return value


def split_stack(value: str) -> tuple[int, str]:
    if "x " in value:
        count, identity = value.split("x ", 1)
        if count.isdigit() and int(count) > 0:
            return int(count), identity
    return 1, value


def output_id(recipe: dict[str, Any]) -> str:
    output = recipe.get("output")
    if isinstance(output, str):
        _, identity = split_stack(output)
    elif isinstance(output, dict):
        identity = output.get("id")
    else:
        identity = None
    if not isinstance(identity, str) or ":" not in identity:
        raise PatchPlanError(f"recipe {recipe.get('id')!r} has no valid output")
    return identity


def output_ids(recipe: dict[str, Any]) -> list[str]:
    """Return every concrete output from either supported seed spelling.

    ``results`` is the canonical TFMG Chemical Vat spelling; ``outputs`` is
    retained for the other managed families.  Conflicting aliases are rejected
    rather than allowing the ownership audit to inspect only one declaration.
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
        if isinstance(output, str):
            _, identity = split_stack(output)
        elif isinstance(output, dict):
            identity = output.get("id")
        else:
            identity = None
        if not isinstance(identity, str) or ":" not in identity:
            raise PatchPlanError(
                f"recipe {recipe.get('id')!r} has an invalid plural output"
            )
        values.append(identity)
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
    values = plan.get("replacement_contracts")
    if not isinstance(values, list):
        raise PatchPlanError("replacement_contracts must be an array")
    result: dict[str, dict[str, Any]] = {}
    outputs: set[str] = set()
    for contract in values:
        if not isinstance(contract, dict) or not isinstance(contract.get("id"), str):
            raise PatchPlanError("replacement_contracts contains an invalid entry")
        identity = contract["id"]
        if identity in result:
            raise PatchPlanError(f"duplicate replacement contract id {identity}")
        output = output_id(contract)
        if output in outputs:
            raise PatchPlanError(f"multiple contracts claim {output}")
        outputs.add(output)
        result[identity] = contract
    return result


def seed_recipe(contract: dict[str, Any]) -> dict[str, Any]:
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
    if not all(isinstance(value, str) for value in entry["unlocks"]):
        raise PatchPlanError(f"assignment node contains a non-string unlock: {node}")
    return entry["unlocks"]


def validate_assignments(plan: dict[str, Any], assignments: dict[str, Any]) -> None:
    policy = plan.get("assignment_contract")
    if not isinstance(policy, dict) or policy.get("changes") != []:
        raise PatchPlanError("assignment contract must remain a no-change review")
    placements = policy.get("required_existing_placement")
    if not isinstance(placements, list) or len(placements) != 3:
        raise PatchPlanError("assignment placement inventory must contain three entries")
    seen: set[str] = set()
    for placement in placements:
        if not isinstance(placement, dict):
            raise PatchPlanError("assignment placement entry is invalid")
        output = placement.get("output")
        node = placement.get("node")
        if not isinstance(output, str) or not isinstance(node, str):
            raise PatchPlanError("assignment placement is missing output or node")
        if output in seen:
            raise PatchPlanError(f"duplicate assignment placement for {output}")
        seen.add(output)
        owners = [
            label
            for label, entry in assignments.get("nodes", {}).items()
            if isinstance(entry, dict)
            and isinstance(entry.get("unlocks"), list)
            and output in entry["unlocks"]
        ]
        if owners != [node]:
            raise PatchPlanError(
                f"assignment placement drifted for {output}: expected {[node]}, got {owners}"
            )


def dependency_occurrences(
    seed: dict[str, Any], old_ids: set[str]
) -> list[dict[str, Any]]:
    occurrences: list[dict[str, Any]] = []
    recipes = seed.get("recipes", [])
    for recipe_index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict):
            continue
        dependencies = recipe.get("depends_on", [])
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list):
            raise PatchPlanError(
                f"recipe {recipe.get('id')!r} has a non-array depends_on field"
            )
        for dependency_index, dependency in enumerate(dependencies):
            if dependency in old_ids:
                occurrences.append(
                    {
                        "json_pointer": (
                            f"/recipes/{recipe_index}/depends_on/{dependency_index}"
                        ),
                        "owner_recipe_id": recipe.get("id"),
                        "from": dependency,
                    }
                )
    return occurrences


def validate_dependency_preconditions(plan: dict[str, Any], seed: dict[str, Any]) -> None:
    policy = plan.get("dependency_rewrite_contract")
    if not isinstance(policy, dict) or not isinstance(policy.get("id_map"), dict):
        raise PatchPlanError("dependency rewrite id_map is absent")
    id_map = policy["id_map"]
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in id_map.items()):
        raise PatchPlanError("dependency rewrite id_map contains invalid entries")
    expected_entries = policy.get("authoritative_seed_rewrites")
    if not isinstance(expected_entries, list):
        raise PatchPlanError("authoritative_seed_rewrites must be an array")
    expected = sorted(
        (
            entry.get("json_pointer"),
            entry.get("owner_recipe_id"),
            entry.get("from"),
            entry.get("to"),
        )
        for entry in expected_entries
        if isinstance(entry, dict)
    )
    observed_entries = dependency_occurrences(seed, set(id_map))
    observed = sorted(
        (
            entry["json_pointer"],
            entry["owner_recipe_id"],
            entry["from"],
            id_map[entry["from"]],
        )
        for entry in observed_entries
    )
    if observed != expected:
        raise PatchPlanError(
            f"authoritative dependency occurrence drift: expected {expected}, got {observed}"
        )
    expected_counts = plan.get("seed_patch_contract", {}).get(
        "expected_dependency_rewrite_counts"
    )
    if not isinstance(expected_counts, dict):
        raise PatchPlanError("expected_dependency_rewrite_counts is absent")
    counts = Counter(entry["from"] for entry in observed_entries)
    actual_counts = {identity: counts[identity] for identity in id_map}
    if actual_counts != expected_counts:
        raise PatchPlanError(
            f"dependency rewrite counts drifted: expected {expected_counts}, got {actual_counts}"
        )


def validate_preconditions(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any]
) -> None:
    status = plan.get("status")
    if status not in {"review_ready_no_shared_mutation", "implemented_in_seed"}:
        raise PatchPlanError("plan is neither review-ready nor implemented")
    contracts = contracts_by_id(plan)
    patch = plan.get("seed_patch_contract")
    if not isinstance(patch, dict):
        raise PatchPlanError("seed_patch_contract must be an object")
    append_ids = patch.get("append_recipe_ids")
    if not isinstance(append_ids, list) or append_ids != list(contracts):
        raise PatchPlanError("append_recipe_ids must match contract order exactly")
    if len(append_ids) != len(set(append_ids)):
        raise PatchPlanError("append_recipe_ids contains duplicates")
    if patch.get("rewrite_dependencies") is not True:
        raise PatchPlanError("reviewed dependency rewrite was disabled")
    if patch.get("remove_source_recipe_override_outputs") != []:
        raise PatchPlanError("this batch must not mutate source_recipe_overrides")
    if patch.get("additional_removals") != []:
        raise PatchPlanError("this batch must not add removals outside recipe contracts")

    current = recipes_by_id(seed)
    target_outputs = {output_id(contract) for contract in contracts.values()}
    overrides = seed.get("source_recipe_overrides")
    if not isinstance(overrides, dict):
        raise PatchPlanError("seed source_recipe_overrides must be an object")
    collisions = sorted(target_outputs & set(overrides))
    if collisions:
        raise PatchPlanError(f"reviewed outputs unexpectedly have overrides: {collisions}")

    validate_assignments(plan, assignments)
    if status == "review_ready_no_shared_mutation":
        collisions = sorted(set(append_ids) & set(current))
        if collisions:
            raise PatchPlanError(f"reviewed recipe IDs already exist in seed: {collisions}")
        existing_outputs = {
            output for recipe in current.values() for output in output_ids(recipe)
        }
        collisions = sorted(existing_outputs & target_outputs)
        if collisions:
            raise PatchPlanError(f"reviewed outputs already have explicit owners: {collisions}")
        validate_dependency_preconditions(plan, seed)
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

    id_map = plan["dependency_rewrite_contract"]["id_map"]
    old_occurrences = dependency_occurrences(seed, set(id_map))
    if old_occurrences:
        raise PatchPlanError(f"implemented seed retains retired dependencies: {old_occurrences}")
    for entry in plan["dependency_rewrite_contract"]["authoritative_seed_rewrites"]:
        owner = current.get(entry["owner_recipe_id"])
        dependencies = owner.get("depends_on", []) if isinstance(owner, dict) else []
        if entry["to"] not in dependencies or entry["from"] in dependencies:
            raise PatchPlanError(
                f"implemented dependency migration changed for {entry['owner_recipe_id']}"
            )


def build_patch_plan(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any]
) -> dict[str, Any]:
    validate_preconditions(plan, seed, assignments)
    contracts = contracts_by_id(plan)
    append_ids = plan["seed_patch_contract"]["append_recipe_ids"]
    implemented = plan.get("status") == "implemented_in_seed"
    rewrites = copy.deepcopy(
        plan["dependency_rewrite_contract"]["authoritative_seed_rewrites"]
    )
    return {
        "schema_version": 1,
        "status": "implemented_in_seed" if implemented else "review_ready_no_shared_mutation",
        "plan_id": plan["plan_id"],
        "mode": "implemented_historical_patch" if implemented else "review_only_no_shared_mutation",
        "preconditions": {
            "recipe_ids_absent": copy.deepcopy(append_ids),
            "outputs_without_explicit_seed_owner": [
                output_id(contracts[identity]) for identity in append_ids
            ],
            "exact_dependency_occurrences": rewrites,
            "assignment_placements_unchanged": copy.deepcopy(
                plan["assignment_contract"]["required_existing_placement"]
            ),
        },
        "seed": {
            "append_recipes": [seed_recipe(contracts[identity]) for identity in append_ids],
            "replace_dependency_ids": copy.deepcopy(
                plan["dependency_rewrite_contract"]["id_map"]
            ),
            "exact_dependency_rewrites": rewrites,
            "remove_source_recipe_override_outputs": [],
            "additional_removals": [],
        },
        "assignments": {"changes": []},
        "external_follow_up": {
            "induction_audit_plan_rewrites": copy.deepcopy(
                plan["dependency_rewrite_contract"]["induction_audit_plan_rewrites"]
            ),
            "active_validator_rewrites": copy.deepcopy(
                plan["dependency_rewrite_contract"]["active_validator_rewrites"]
            ),
            "supersession_contract": copy.deepcopy(plan["supersession_contract"]),
        },
        "expected_effect": {
            "explicit_recipe_owners_added": 3,
            "automatic_recipe_owners_suppressed": 3,
            "exact_stock_recipe_removals": 3,
            "authoritative_dependency_rewrites": 2,
            "assignment_changes": 0,
        },
    }


def apply_patch_to_copies(
    plan: dict[str, Any], seed: dict[str, Any], assignments: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply the reviewed patch to deep copies for manifest/compiler proofs."""
    patch = build_patch_plan(plan, seed, assignments)
    staged_seed = copy.deepcopy(seed)
    staged_assignments = copy.deepcopy(assignments)
    if plan.get("status") == "implemented_in_seed":
        return staged_seed, staged_assignments
    staged_seed["recipes"].extend(copy.deepcopy(patch["seed"]["append_recipes"]))
    id_map = patch["seed"]["replace_dependency_ids"]
    replacements = 0
    for recipe in staged_seed["recipes"]:
        dependencies = recipe.get("depends_on")
        if not isinstance(dependencies, list):
            continue
        for index, dependency in enumerate(dependencies):
            if dependency in id_map:
                dependencies[index] = id_map[dependency]
                replacements += 1
    if replacements != len(patch["seed"]["exact_dependency_rewrites"]):
        raise PatchPlanError(
            f"staged dependency rewrite count drifted: expected "
            f"{len(patch['seed']['exact_dependency_rewrites'])}, got {replacements}"
        )
    return staged_seed, staged_assignments


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional review artifact; supplied authorities are never edited.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        patch = build_patch_plan(
            load_json(args.plan.resolve()),
            load_json(args.seed.resolve()),
            load_json(args.assignments.resolve()),
        )
    except (OSError, json.JSONDecodeError, PatchPlanError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    encoded = json.dumps(patch, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.resolve().write_text(encoded, encoding="utf-8")
        print(f"Wrote non-mutating patch plan: {args.output.resolve()}")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
