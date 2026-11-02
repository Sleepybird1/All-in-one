#!/usr/bin/env python3
"""Validate the implemented Mekanism transmitter upgrade ladders."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import generate_managed_recipe_overhaul as generator
import validate_mekanism_factory_restoration_audit as factory_audit


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "MEKANISM_TRANSMITTER_UPGRADE_AUDIT.plan.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_MANIFEST = PROJECT / "progression/managed_recipe_overhaul.json"
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
ENVIRONMENTS = PROJECT / "src/main/resources/data/industrial_colonies/tier_recipe_environments.json"
POWER_PLAN = PROJECT / "POWER_BACKBONE_AUDIT.plan.json"
EXTREME_PLAN = PROJECT / "EXTREME_TRANSMISSION_AUDIT.plan.json"
STORAGE_PLAN = PROJECT / "MEKANISM_STORAGE_LADDER_AUDIT.plan.json"
MATRIX_PLAN = PROJECT / "INDUCTION_MATRIX_COMPLETION_AUDIT.plan.json"
FACTORY_PLAN = PROJECT / "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json"
UNIVERSAL_TAIL_PLAN = PROJECT / "MEKANISM_UNIVERSAL_CABLE_TAIL_AUDIT.plan.json"
EXPECTED_JAR = "Mekanism-1.21.1-10.7.19.85.jar"
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^#[a-z0-9_.-]+:[a-z0-9_./-]+$")
STACK = re.compile(r"^(?:([1-9][0-9]*)x )?(.+)$")
FAMILIES = (
    "universal_cable",
    "logistical_transporter",
    "mechanical_pipe",
    "pressurized_tube",
    "thermodynamic_conductor",
)
TIERS = ("advanced", "elite", "ultimate")
NODE = {
    "advanced": "CR01 — Reinforced Systems",
    "elite": "CR01 — Precision Engineering",
    "ultimate": "CR01 — High-Energy Distribution",
}
PHASE = {"advanced": "Mekanized Industry", "elite": "High-Energy Grid", "ultimate": "High-Energy Grid"}
PRESS = {
    "advanced": "createcasing:industrial_iron_press",
    "elite": "createcasing:weathered_iron_press",
    "ultimate": "createcasing:weathered_iron_press",
}
REFINED_PRESS = "createcasing:refined_radiance_press"
ALLOY = {
    "advanced": "mekanism:alloy_infused",
    "elite": "mekanism:alloy_reinforced",
    "ultimate": "mekanism:alloy_atomic",
}
CIRCUIT = {
    "advanced": "mekanism:advanced_control_circuit",
    "elite": "mekanism:elite_control_circuit",
    "ultimate": "mekanism:ultimate_control_circuit",
}
CIRCUIT_RECIPE = {
    "advanced": "industrial_colonies:mekanism/advanced_control_circuit",
    "elite": "industrial_colonies:mekanism/elite_control_circuit",
    "ultimate": "industrial_colonies:mekanism/ultimate_control_circuit",
}
EXTREME_WIRE_RECIPE = "industrial_colonies:extreme_grid/heavily_insulated_wire"
EXTREME_BREAKER_RECIPE = "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker"


def managed_id(tier: str, family: str) -> str:
    if family == "universal_cable":
        return f"industrial_colonies:auto/mekanism/{tier}_universal_cable"
    return f"industrial_colonies:mekanism/transmission/{tier}_{family}"


def source_universal_id(tier: str) -> str:
    return f"industrial_colonies:mekanism/transmission/{tier}_universal_cable"


def item_id(tier: str, family: str) -> str:
    return f"mekanism:{tier}_{family}"


def stock_id(tier: str, family: str) -> str:
    return f"mekanism:transmitter/{family}/{tier}"


def basic_recipe(family: str) -> str:
    return f"industrial_colonies:mekanism/transmission/basic_{family}"


EXPECTED = [
    {
        "order": tier_index * 50 + family_index * 10 + 10,
        "tier": tier,
        "family": family,
        "id": managed_id(tier, family),
        "output": item_id(tier, family),
        "stock": stock_id(tier, family),
    }
    for tier_index, tier in enumerate(TIERS)
    for family_index, family in enumerate(FAMILIES)
]
EXPECTED_BY_ID = {row["id"]: row for row in EXPECTED}
UNIVERSAL_EXPECTED = [row for row in EXPECTED if row["family"] == "universal_cable"]
NON_UNIVERSAL_EXPECTED = [row for row in EXPECTED if row["family"] != "universal_cable"]
UNIVERSAL_IDS = {str(row["id"]) for row in UNIVERSAL_EXPECTED}
NON_UNIVERSAL_IDS = {str(row["id"]) for row in NON_UNIVERSAL_EXPECTED}
BASIC = {
    family: {
        "recipe_id": basic_recipe(family),
        "output": item_id("basic", family),
        "output_count": 8,
        "remove_exact": stock_id("basic", family),
    }
    for family in FAMILIES
}
SUPPORTING = {
    "mekanism:advanced_control_circuit": CIRCUIT_RECIPE["advanced"],
    "mekanism:elite_control_circuit": CIRCUIT_RECIPE["elite"],
    "mekanism:ultimate_control_circuit": CIRCUIT_RECIPE["ultimate"],
    "electroenergetics:heavily_insulated_wire": EXTREME_WIRE_RECIPE,
    "electroenergetics:sulfur_hexafluoride_breaker": EXTREME_BREAKER_RECIPE,
}
FAMILY_REQUIREMENTS: dict[tuple[str, str], set[str]] = {
    ("advanced", "universal_cable"): {"tfmg:aluminum_wire", "tfmg:aluminum_cable_hub", "tfmg:rubber_sheet"},
    ("elite", "universal_cable"): {"tfmg:aluminum_wire", "tfmg:glass_cable_insulator", "tfmg:steel_cable_hub"},
    ("ultimate", "universal_cable"): {"electroenergetics:heavily_insulated_wire", "electroenergetics:sulfur_hexafluoride_breaker"},
    ("advanced", "logistical_transporter"): {"create:smart_chute", "create:brass_tunnel", "create:filter"},
    ("elite", "logistical_transporter"): {"create:content_observer", "create:stockpile_switch", "create:attribute_filter"},
    ("ultimate", "logistical_transporter"): {"create:packager", "create:stock_link", "create:redstone_requester"},
    ("advanced", "mechanical_pipe"): {"create:fluid_pipe", "create:mechanical_pump", "tfmg:steel_mechanism"},
    ("elite", "mechanical_pipe"): {"tfmg:steel_pipe", "tfmg:steel_mechanical_pump", "tfmg:steel_smart_fluid_pipe"},
    ("ultimate", "mechanical_pipe"): {"tfmg:industrial_pipe", "tfmg:electric_pump", "tfmg:steel_smart_fluid_pipe"},
    ("advanced", "pressurized_tube"): {"tfmg:rubber_sheet", "#c:glass_blocks/cheap", "tfmg:steel_casing"},
    ("elite", "pressurized_tube"): {"tfmg:plastic_sheet", "tfmg:plastic_pipe", "tfmg:plastic_fluid_valve"},
    ("ultimate", "pressurized_tube"): {"tfmg:plastic_sheet", "tfmg:plastic_pipe", "tfmg:plastic_fluid_valve", "tfmg:steel_smart_fluid_pipe"},
    ("advanced", "thermodynamic_conductor"): {"create:copper_sheet", "tfmg:aluminum_pipe", "create:encased_fan"},
    ("elite", "thermodynamic_conductor"): {"tfmg:constantan_wire", "create:copper_sheet", "create:encased_fan"},
    ("ultimate", "thermodynamic_conductor"): {"tfmg:industrial_pipe", "tfmg:constantan_wire", "create:copper_sheet", "create:encased_fan"},
}


def expected_dependencies(tier: str, family: str) -> set[str]:
    if tier == "advanced":
        result = {basic_recipe(family), CIRCUIT_RECIPE[tier]}
    else:
        prior = TIERS[TIERS.index(tier) - 1]
        result = {managed_id(prior, family), CIRCUIT_RECIPE[tier]}
    if tier == "ultimate" and family == "universal_cable":
        result.update({EXTREME_WIRE_RECIPE, EXTREME_BREAKER_RECIPE})
    return result


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def audited_factory_assignment_delta(node: str, errors: list[str]) -> tuple[list[str], set[str]]:
    """Load the exact later Factory assignment migration for one node."""
    try:
        factory_plan = load_object(FACTORY_PLAN)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"cannot inspect Factory assignment plan: {error}")
        return [], set()
    delta = factory_plan.get("assignment_delta", {})
    expected_additions, expected_removals = factory_audit.expected_assignment_delta()
    additions = factory_audit.flatten_delta(delta.get("additions"))
    removals = factory_audit.flatten_delta(delta.get("removals"))
    if (
        factory_plan.get("status") != "implemented_in_seed"
        or additions != expected_additions
        or removals != expected_removals
        or delta.get("addition_count") != 16
        or delta.get("removal_count") != 8
    ):
        errors.append("Factory assignment plan must retain its exact implemented 16-add/8-remove delta")

    def outputs(field: str) -> list[str]:
        matches = [
            entry for entry in delta.get(field, [])
            if isinstance(entry, dict) and entry.get("node") == node
        ]
        if len(matches) != 1 or not isinstance(matches[0].get("outputs"), list):
            errors.append(f"Factory assignment plan must contain exactly one {field} entry for {node}")
            return []
        values = [str(value) for value in matches[0]["outputs"]]
        if len(values) != len(set(values)):
            errors.append(f"Factory assignment plan contains duplicate {field} for {node}")
        return values

    return outputs("additions"), set(outputs("removals"))


def default_mods() -> Path:
    for raw in (PROJECT / "gradle.properties").read_text(encoding="utf-8-sig").splitlines():
        if raw.strip().startswith("pack_mods_dir="):
            return Path(raw.split("=", 1)[1].strip()).expanduser().resolve()
    raise ValueError("gradle.properties is missing pack_mods_dir")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_stack(value: Any) -> tuple[str, int]:
    if isinstance(value, dict):
        return str(value.get("id", "")), int(value.get("count", 1))
    match = STACK.fullmatch(str(value).strip())
    if not match:
        return "", 0
    return match.group(2), int(match.group(1) or 1)


def primary_output(recipe: Mapping[str, Any]) -> tuple[str, int]:
    if recipe.get("output") is not None:
        return parse_stack(recipe.get("output"))
    outputs = recipe.get("outputs", [])
    if isinstance(outputs, list) and outputs:
        return parse_stack(outputs[0])
    return "", 0


def input_counts(recipe: Mapping[str, Any]) -> Counter[str]:
    result: Counter[str] = Counter()
    for value in recipe.get("inputs", []):
        resource, count = parse_stack(value)
        if resource:
            result[resource] += count
    return result


def installed_recipe(
    row: Mapping[str, str], expected: Mapping[str, Any], mods: Path
) -> tuple[str, str, int, Counter[str]]:
    if row.get("source_jar") != EXPECTED_JAR:
        raise ValueError(f"catalog source JAR changed to {row.get('source_jar')!r}")
    if row.get("source_path") != expected.get("source_path"):
        raise ValueError(f"catalog source path changed to {row.get('source_path')!r}")
    jar = mods / EXPECTED_JAR
    if not jar.is_file():
        raise OSError(f"installed source JAR is missing: {jar}")
    with zipfile.ZipFile(jar) as archive:
        value = json.loads(archive.read(str(expected["source_path"])).decode("utf-8"))
    result = value.get("result")
    if isinstance(result, str):
        output, count = result, 1
    elif isinstance(result, dict):
        output, count = str(result.get("id", "")), int(result.get("count", 1))
    else:
        output, count = "", 0
    ingredient_counts: Counter[str] = Counter()
    key = value.get("key", {})
    pattern = value.get("pattern", [])
    if isinstance(key, dict) and isinstance(pattern, list):
        symbols = Counter(char for line in pattern if isinstance(line, str) for char in line if char != " ")
        for symbol, occurrences in symbols.items():
            ingredient = key.get(symbol, {})
            if isinstance(ingredient, dict):
                resource = str(ingredient.get("item", ""))
                if not resource and ingredient.get("tag"):
                    resource = f"#{ingredient['tag']}"
                if resource:
                    ingredient_counts[resource] += occurrences
    return str(value.get("type", "")), output, count, ingredient_counts


def seed_spec(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": contract["id"], "node": contract["node"], "phase": contract["phase"],
        "order": contract["batch_order"], "type": contract["type"],
        "comment": contract["comment"], "machine": contract["machine"],
        "inputs": contract["inputs"], "output": contract["output"],
        "remove": contract["remove_exact"],
        "exclusive_output": contract["exclusive_output"],
        "depends_on": contract.get("depends_on_batch", []),
    }


def universal_seed_spec(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(contract[key])
        for key in (
            "id", "node", "phase", "order", "type", "comment", "machine",
            "inputs", "output", "remove", "exclusive_output", "depends_on",
        )
    }


def compile_card(contract: Mapping[str, Any]) -> dict[str, Any]:
    spec = seed_spec(contract)
    return generator.process(spec, generator.stable_uid("recipe", str(spec["id"])))


def recipes_by_id(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(recipe["id"]): recipe for recipe in manifest.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def compacting_machine_items() -> set[str]:
    environments = load_object(ENVIRONMENTS)
    for family in environments.get("recipe_families", []):
        if isinstance(family, dict) and family.get("id") == "compacting":
            return {str(machine.get("item", "")) for machine in family.get("machines", []) if isinstance(machine, dict)}
    return set()


def validate_dag(contracts: list[dict[str, Any]], errors: list[str]) -> None:
    graph = {
        str(recipe.get("id")): {
            dependency for dependency in recipe.get("depends_on_batch", [])
            if dependency in EXPECTED_BY_ID
        }
        for recipe in contracts
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> None:
        if identity in visiting:
            errors.append(f"dependency cycle detected at {identity}")
            return
        if identity in visited:
            return
        visiting.add(identity)
        for dependency in graph.get(identity, set()):
            visit(dependency)
        visiting.remove(identity)
        visited.add(identity)

    for identity in graph:
        visit(identity)


def validate_implementation_parity(
    plan: dict[str, Any], contracts: list[dict[str, Any]],
    universal_tail: Mapping[str, Any],
    seed: Mapping[str, Any], manifest: Mapping[str, Any],
    assignments: Mapping[str, Any], errors: list[str],
) -> None:
    seed_recipes = recipes_by_id(seed)
    manifest_recipes = recipes_by_id(manifest)
    contracts_by_id = {str(row.get("id", "")): row for row in contracts}
    expected_outputs = {str(row["output"]) for row in EXPECTED}

    seed_owners: dict[str, list[str]] = {}
    manifest_owners: dict[str, list[str]] = {}
    for identity, recipe in seed_recipes.items():
        output = primary_output(recipe)[0]
        if output in expected_outputs:
            seed_owners.setdefault(output, []).append(identity)
    for identity, recipe in manifest_recipes.items():
        output = primary_output(recipe)[0]
        if output in expected_outputs:
            manifest_owners.setdefault(output, []).append(identity)

    for expected in NON_UNIVERSAL_EXPECTED:
        identity = str(expected["id"])
        output = str(expected["output"])
        contract = contracts_by_id.get(identity)
        if contract is None:
            errors.append(f"implemented non-universal contract is missing from plan: {identity}")
            continue
        actual = seed_recipes.get(identity)
        reviewed = seed_spec(contract)
        if actual is None:
            errors.append(f"implemented non-universal recipe is absent from authoritative seed: {identity}")
        elif actual != reviewed:
            differing = sorted(
                field for field in set(actual) | set(reviewed)
                if actual.get(field) != reviewed.get(field)
            )
            errors.append(f"{identity}: authoritative seed differs from reviewed contract in {differing}")
        if seed_owners.get(output) != [identity]:
            errors.append(f"{identity}: non-universal output does not have one seed owner; owners={seed_owners.get(output, [])}")
        if manifest_owners.get(output) != [identity]:
            errors.append(f"{identity}: non-universal output does not have one assembled owner; owners={manifest_owners.get(output, [])}")
        assembled = manifest_recipes.get(identity)
        if assembled is None:
            errors.append(f"implemented non-universal recipe is absent from assembled manifest: {identity}")
        elif primary_output(assembled) != (output, 8):
            errors.append(f"{identity}: assembled output identity/count changed")

    preserved_rows = [row for row in plan.get("preserved_universal_managed_ids", []) if isinstance(row, dict)]
    preserved = {str(row.get("id", "")): row for row in preserved_rows}
    if len(preserved_rows) != 3 or set(preserved) != UNIVERSAL_IDS:
        errors.append("the three preserved Universal Cable managed IDs changed")
    supersession = plan.get("universal_tail_supersession", {})
    if supersession != {
        "status": "implemented_in_seed",
        "authority": "MEKANISM_UNIVERSAL_CABLE_TAIL_AUDIT.plan.json",
        "historical_automatic_ids_retired": [
            managed_id(tier, "universal_cable") for tier in TIERS
        ],
        "source_owned_recipe_ids": [source_universal_id(tier) for tier in TIERS],
    }:
        errors.append("Universal Cable tail supersession metadata changed")
    tail_contracts = {
        str(row.get("id", "")): row
        for row in universal_tail.get("replacement_contracts", [])
        if isinstance(row, dict)
    }
    if universal_tail.get("status") != "implemented_in_seed":
        errors.append("Universal Cable tail supersession is not implemented_in_seed")
    for expected in UNIVERSAL_EXPECTED:
        identity = str(expected["id"])
        tier = str(expected["tier"])
        source_identity = source_universal_id(tier)
        output = str(expected["output"])
        evidence = preserved.get(identity, {})
        contract = tail_contracts.get(source_identity)
        if identity in seed_recipes or identity in manifest_recipes:
            errors.append(f"retired automatic Universal Cable ID survived supersession: {identity}")
        actual = seed_recipes.get(source_identity)
        if contract is None:
            errors.append(f"Universal Cable tail contract is missing: {source_identity}")
        elif actual != universal_seed_spec(contract):
            errors.append(f"source-owned Universal Cable seed contract changed: {source_identity}")
        if seed_owners.get(output) != [source_identity]:
            errors.append(
                f"{output}: Universal Cable output does not have one source-owned seed owner; "
                f"owners={seed_owners.get(output, [])}"
            )
        assembled = manifest_recipes.get(source_identity)
        if assembled is None:
            errors.append(f"source-owned Universal Cable managed ID is absent: {source_identity}")
            continue
        assembled_output, assembled_count = primary_output(assembled)
        if manifest_owners.get(output) != [source_identity]:
            errors.append(f"{source_identity}: Universal Cable output owner changed; owners={manifest_owners.get(output, [])}")
        if (
            assembled_output != output
            or assembled_count != 8
            or assembled.get("type") != "compacting"
            or assembled.get("remove") != [str(expected["stock"])]
        ):
            errors.append(f"source-owned Universal Cable managed route changed: {source_identity}")
        if evidence != {
            "id": identity,
            "output": output,
            "output_count": 8,
            "type": "mechanical_crafting",
            "remove_exact": [str(expected["stock"])],
        }:
            errors.append(f"preserved Universal Cable evidence changed: {identity}")

    prefixes = plan.get("assignment_existing_prefixes", {})
    if not isinstance(prefixes, dict) or set(prefixes) != set(NODE.values()):
        errors.append("assignment_existing_prefixes must cover the three reviewed nodes")
    nodes = assignments.get("nodes", {})
    for addition in plan.get("assignment_additions", []):
        if not isinstance(addition, dict):
            continue
        node = str(addition.get("node", ""))
        prefix = prefixes.get(node, []) if isinstance(prefixes, dict) else []
        outputs = addition.get("outputs", [])
        actual = nodes.get(node, {}).get("unlocks", []) if isinstance(nodes, dict) else []
        factory_additions, factory_removals = audited_factory_assignment_delta(node, errors)
        historical_segment = prefix + outputs
        if any(historical_segment.count(output) != 1 for output in factory_removals):
            errors.append(f"{node}: Factory removals must each target one locked historical assignment")
        transformed_segment = [output for output in historical_segment if output not in factory_removals]
        expected = transformed_segment + factory_additions
        if actual != expected:
            errors.append(
                f"{node}: assignments must preserve the locked transmitter sequence after the exact Factory removals, "
                "then append only the exact Factory additions"
            )

    implementation = plan.get("seed_implementation", {})
    if (
        implementation.get("status") != "source_owned_non_universal"
        or implementation.get("authoritative_source") != "progression/managed_recipe_overhaul.seed.json"
        or implementation.get("recipe_count") != 12
        or implementation.get("exact_stock_removals") != 12
        or implementation.get("exclusive_output_owners") != 12
        or implementation.get("preserved_universal_managed_ids") != 3
        or implementation.get("authoritative_basic_routes_untouched") != 5
    ):
        errors.append("transmitter seed_implementation metadata is incomplete or stale")
    assignment_implementation = plan.get("assignment_implementation", {})
    if (
        assignment_implementation.get("status") != "appended_without_reordering"
        or assignment_implementation.get("authoritative_source") != "progression/machine_node_assignments.json"
        or assignment_implementation.get("node_count") != 3
        or assignment_implementation.get("appended_count") != 12
    ):
        errors.append("transmitter assignment_implementation metadata is incomplete or stale")


def validate(
    plan: dict[str, Any], catalog: Path, manifest: Mapping[str, Any], mods: Path,
    seed: Mapping[str, Any], assignments: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if plan.get("status") != "implemented_in_seed":
        errors.append("audit status must be implemented_in_seed")
    scope = plan.get("scope", {})
    if (
        scope.get("replacement_count") != 15
        or scope.get("implemented_replacement_count") != 12
        or scope.get("preserved_managed_id_count") != 3
        or scope.get("family_count") != 5
        or scope.get("tiers") != list(TIERS)
    ):
        errors.append("scope must describe five families across fifteen upgrades")
    if scope.get("installed_mod") != EXPECTED_JAR:
        errors.append("scope installed_mod changed")
    if scope.get("implementation_readiness") != "implemented_after_extreme_transmission":
        errors.append("scope must record implemented_after_extreme_transmission readiness")
    assessment = plan.get("implementation_assessment", {})
    if assessment.get("decision") != "go" or assessment.get("required_predecessor_recipe_id") != EXTREME_BREAKER_RECIPE:
        errors.append("implementation assessment must be go after the Extreme breaker")

    items = {row["item_id"] for row in load_rows(catalog / "items.csv")}
    installed = {row["recipe_id"]: row for row in load_rows(catalog / "recipes.csv")}
    manifest_recipes = recipes_by_id(manifest)
    seed_recipes = recipes_by_id(seed)
    phase_order = manifest.get("phase_order", [])
    phase_rank = {str(phase): index for index, phase in enumerate(phase_order)}
    if PHASE["advanced"] not in phase_rank or PHASE["elite"] not in phase_rank or phase_rank[PHASE["advanced"]] >= phase_rank[PHASE["elite"]]:
        errors.append("manifest phase order no longer places Mekanized Industry before High-Energy Grid")
    known_output_phase = {
        primary_output(recipe)[0]: str(recipe.get("phase", ""))
        for recipe in manifest_recipes.values() if primary_output(recipe)[0]
    }
    known_output_phase.update({str(row["output"]): PHASE[str(row["tier"])] for row in EXPECTED})
    known_output_phase.update({
        "electroenergetics:heavily_insulated_wire": "High-Energy Grid",
        "electroenergetics:sulfur_hexafluoride_breaker": "High-Energy Grid",
    })
    source_rows = plan.get("source_recipe_contracts", [])
    source = {str(row.get("recipe_id", "")): row for row in source_rows if isinstance(row, dict)}
    if len(source_rows) != 15 or len(source) != 15:
        errors.append("source_recipe_contracts must contain fifteen unique upgrades")

    basic_rows = plan.get("authoritative_basic_prerequisites", [])
    declared_basics = {str(row.get("output", "")): row for row in basic_rows if isinstance(row, dict)}
    if len(basic_rows) != 5 or set(declared_basics) != {row["output"] for row in BASIC.values()}:
        errors.append("authoritative_basic_prerequisites must contain the five Basic families")
    for family, expected in BASIC.items():
        declared = declared_basics.get(expected["output"], {})
        if declared != expected:
            errors.append(f"authoritative Basic contract changed for {family}")
        current = manifest_recipes.get(expected["recipe_id"])
        if current is None:
            errors.append(f"authoritative Basic managed recipe is missing: {expected['recipe_id']}")
            continue
        output, count = primary_output(current)
        if output != expected["output"] or count != 8 or current.get("remove") != [expected["remove_exact"]]:
            errors.append(f"authoritative Basic managed recipe changed: {expected['recipe_id']}")
        if current.get("phase") != "Mekanized Industry" or current.get("exclusive_output") is not True:
            errors.append(f"authoritative Basic phase/ownership changed: {expected['recipe_id']}")
        source_owned = seed_recipes.get(expected["recipe_id"])
        if source_owned is None:
            errors.append(f"authoritative Basic seed route is missing: {expected['recipe_id']}")
        else:
            source_output, source_count = primary_output(source_owned)
            if source_output != expected["output"] or source_count != 8 or source_owned.get("remove") != [expected["remove_exact"]]:
                errors.append(f"authoritative Basic seed route changed: {expected['recipe_id']}")

    supporting_rows = plan.get("supporting_predecessors", [])
    declared_support = {str(row.get("output", "")): str(row.get("recipe_id", "")) for row in supporting_rows if isinstance(row, dict)}
    if declared_support != SUPPORTING or len(supporting_rows) != len(SUPPORTING):
        errors.append("supporting_predecessors changed or are incomplete")
    for tier in TIERS:
        if tier == "advanced" or tier in {"elite", "ultimate"}:
            current = manifest_recipes.get(CIRCUIT_RECIPE[tier])
            if current is None or primary_output(current)[0] != CIRCUIT[tier]:
                errors.append(f"managed {tier} circuit predecessor is missing or changed")

    press_items = compacting_machine_items()
    if {PRESS["advanced"], PRESS["elite"], REFINED_PRESS} - press_items:
        errors.append("tier_recipe_environments.json no longer exposes the reviewed Encased presses")
    machine_families = {
        str(row.get("tier", "")): str(row.get("phase", ""))
        for row in manifest.get("machine_families", []) if isinstance(row, dict)
    }
    if machine_families.get("industrial_iron") != "Mekanized Industry" or machine_families.get("weathered_iron") != "High-Energy Grid" or machine_families.get("refined_radiance") != "Nuclear Engineering":
        errors.append("machine-family phase ownership changed")

    contracts = [row for row in plan.get("replacement_contracts", []) if isinstance(row, dict)]
    if len(contracts) != 15:
        errors.append("replacement_contracts must contain exactly fifteen recipes")
    try:
        universal_tail = load_object(UNIVERSAL_TAIL_PLAN)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"cannot inspect Universal Cable tail supersession: {error}")
        universal_tail = {}
    validate_implementation_parity(
        plan, contracts, universal_tail, seed, manifest, assignments, errors
    )
    seen_outputs: set[str] = set()
    removals: list[str] = []
    order_by_id = {row["id"]: row["order"] for row in EXPECTED}

    for index, recipe in enumerate(contracts):
        if index >= len(EXPECTED):
            break
        expected = EXPECTED[index]
        tier = str(expected["tier"])
        family = str(expected["family"])
        identity = str(expected["id"])
        output, output_count = parse_stack(recipe.get("output"))
        actual_identity = (recipe.get("batch_order"), recipe.get("id"), output, recipe.get("node"), recipe.get("phase"))
        wanted_identity = (expected["order"], identity, expected["output"], NODE[tier], PHASE[tier])
        if actual_identity != wanted_identity:
            errors.append(f"contract {index + 1} has wrong order/id/output/node/phase")
        if output_count != 8 or output not in items or output in seen_outputs:
            errors.append(f"{identity}: output must be eight unique installed segments")
        seen_outputs.add(output)
        if recipe.get("type") != "compacting":
            errors.append(f"{identity}: upgrade must use Compacting")
        if recipe.get("machine") != PRESS[tier]:
            errors.append(f"{identity}: wrong Encased press for {tier}; expected {PRESS[tier]}")
        if recipe.get("machine") == REFINED_PRESS:
            errors.append(f"{identity}: Refined Radiance is a post-nuclear dependency")
        if not isinstance(recipe.get("comment"), str) or not recipe.get("comment", "").strip():
            errors.append(f"{identity}: nonblank generator comment is required")
        if recipe.get("exclusive_output") is not True:
            errors.append(f"{identity}: exclusive_output must be true")

        counts = input_counts(recipe)
        prior_tier = "basic" if tier == "advanced" else TIERS[TIERS.index(tier) - 1]
        prior_item = item_id(prior_tier, family)
        if counts[prior_item] != 8:
            errors.append(f"{identity}: requires exactly 8x {prior_item}")
        if counts[ALLOY[tier]] != 4 or counts[CIRCUIT[tier]] != 2:
            errors.append(f"{identity}: must use 4x {ALLOY[tier]} and 2x {CIRCUIT[tier]}")
        missing_family = FAMILY_REQUIREMENTS[(tier, family)] - set(counts)
        if missing_family:
            errors.append(f"{identity}: missing family-specific infrastructure {sorted(missing_family)}")
        for value in recipe.get("inputs", []):
            resource, count = parse_stack(value)
            if not resource:
                errors.append(f"{identity}: cannot parse input {value!r}")
            elif resource.startswith("#"):
                if not TAG_ID.fullmatch(resource):
                    errors.append(f"{identity}: invalid input tag {resource}")
                if count > 1:
                    errors.append(f"{identity}: counted tags are unsupported by KJSGen: {value}")
            elif not RESOURCE_ID.fullmatch(resource) or resource not in items:
                errors.append(f"{identity}: installed input is missing or invalid: {resource}")
            elif resource in known_output_phase:
                ingredient_phase = known_output_phase[resource]
                if ingredient_phase in phase_rank and PHASE[tier] in phase_rank and phase_rank[ingredient_phase] > phase_rank[PHASE[tier]]:
                    errors.append(f"{identity}: post-phase managed input {resource} belongs to {ingredient_phase}")
        if family != "universal_cable" and any(resource.startswith("electroenergetics:") for resource in counts):
            errors.append(f"{identity}: nonsensical electrical-grid ingredient entered {family}")

        dependencies = recipe.get("depends_on_batch", [])
        expected_deps = expected_dependencies(tier, family)
        if not isinstance(dependencies, list) or set(dependencies) != expected_deps:
            errors.append(f"{identity}: dependency set changed")
        if isinstance(dependencies, list):
            for dependency in dependencies:
                if dependency in order_by_id and order_by_id[dependency] >= int(expected["order"]):
                    errors.append(f"{identity}: dependency is not earlier in batch order: {dependency}")

        exact = recipe.get("remove_exact", [])
        if exact != [expected["stock"]]:
            errors.append(f"{identity}: exact stock removal changed")
        removals.extend(exact if isinstance(exact, list) else [])
        expected_source = source.get(str(expected["stock"]))
        catalog_row = installed.get(str(expected["stock"]))
        if expected_source is None or catalog_row is None:
            errors.append(f"{identity}: stock source evidence is missing")
        else:
            try:
                installed_type, installed_output, installed_count, stock_inputs = installed_recipe(catalog_row, expected_source, mods)
            except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
                errors.append(f"{identity}: cannot inspect installed stock recipe: {error}")
            else:
                if installed_type != "minecraft:crafting_shaped" or expected_source.get("recipe_type") != installed_type:
                    errors.append(f"{identity}: stock recipe type changed")
                if installed_output != expected["output"] or expected_source.get("output") != expected["output"]:
                    errors.append(f"{identity}: stock output changed")
                if installed_count != 8 or expected_source.get("stock_output_count") != 8:
                    errors.append(f"{identity}: stock output count changed")
                stock_prior = item_id("basic" if tier == "advanced" else TIERS[TIERS.index(tier) - 1], family)
                stock_alloy_tag = f"#mekanism:alloys/{'infused' if tier == 'advanced' else 'reinforced' if tier == 'elite' else 'atomic'}"
                if stock_inputs[stock_prior] != 8 or stock_inputs[stock_alloy_tag] != 1 or sum(stock_inputs.values()) != 9:
                    errors.append(f"{identity}: installed stock recipe is no longer the eight-segment plus one-alloy shortcut")
                if catalog_row.get("recipe_type") != installed_type or expected["output"] not in catalog_row.get("outputs", "").split("|"):
                    errors.append(f"{identity}: catalog/JAR source evidence differs")

        try:
            card = compile_card(recipe)
        except (KeyError, TypeError, ValueError) as error:
            errors.append(f"{identity}: KJSGen compiler rejected contract: {error}")
        else:
            card_output = card.get("slots", {}).get("output", {})
            machine_slot = card.get("slots", {}).get("__machine_process_compacting", {})
            if card.get("type") != "kjsgen:create_compacting" or machine_slot.get("id") != PRESS[tier]:
                errors.append(f"{identity}: KJSGen lost exact Compacting machine binding")
            if card_output.get("id") != expected["output"] or int(card_output.get("count", 1)) != 8:
                errors.append(f"{identity}: KJSGen changed output identity/count")

    expected_sources = {str(row["stock"]) for row in EXPECTED}
    if set(source) != expected_sources or Counter(removals) != Counter({identity: 1 for identity in expected_sources}):
        errors.append("source audit and exact removals are not one-to-one")
    if any(identity.endswith("/basic") for identity in removals):
        errors.append("upgrade batch must not retire any authoritative Basic recipe")
    validate_dag(contracts, errors)

    additions = plan.get("assignment_additions", [])
    expected_additions = [
        {
            "node": NODE[tier], "phase": PHASE[tier],
            "outputs": [item_id(tier, family) for family in FAMILIES if family != "universal_cable"],
        }
        for tier in TIERS
    ]
    if additions != expected_additions:
        errors.append("the twelve implemented non-universal assignment additions changed")

    machine_policy = plan.get("machine_policy", {})
    if machine_policy != {**PRESS, "excluded_post_phase_machine": REFINED_PRESS}:
        errors.append("machine_policy changed")
    generator_contract = plan.get("generator_contract", {})
    if generator_contract.get("supported_types") != ["compacting"] or generator_contract.get("counted_tags_supported") is not False or generator_contract.get("exact_machine_binding_required") is not True:
        errors.append("generator_contract changed")

    for path in (EXTREME_PLAN, STORAGE_PLAN, MATRIX_PLAN):
        try:
            predecessor = load_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"cannot inspect intended predecessor {path.name}: {error}")
        else:
            if predecessor.get("implementation_assessment", {}).get("decision") != "go":
                errors.append(f"intended predecessor is not go: {path.name}")
            if predecessor.get("status") != "implemented_in_seed":
                errors.append(f"intended predecessor is not implemented_in_seed: {path.name}")
    try:
        extreme = load_object(EXTREME_PLAN)
        extreme_ids = {row.get("id") for row in extreme.get("replacement_contracts", []) if isinstance(row, dict)}
        if {EXTREME_WIRE_RECIPE, EXTREME_BREAKER_RECIPE} - extreme_ids:
            errors.append("Extreme Transmission no longer owns both Ultimate cable prerequisites")
        matrix = load_object(MATRIX_PLAN)
        matrix_external = {row.get("recipe_id") for row in matrix.get("external_prerequisites", []) if isinstance(row, dict)}
        if source_universal_id("ultimate") not in matrix_external:
            errors.append("source-owned Ultimate Universal Cable ID no longer matches the matrix contract")
        power = load_object(POWER_PLAN)
        ranks = {row.get("node"): row.get("rank") for row in power.get("age_order", []) if isinstance(row, dict)}
        if [ranks.get(NODE[tier]) for tier in TIERS] != [90, 100, 110]:
            errors.append("POWER_BACKBONE_AUDIT transmitter node order changed")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"cannot validate intended predecessor compatibility: {error}")

    result = plan.get("validation_result", {})
    expected_result = {
        "status": "passed",
        "embedded_mutation_tests": 15,
        "focused_unit_tests": 15,
        "installed_source_recipes": 15,
        "implemented_non_universal_recipes": 12,
        "preserved_universal_managed_ids": 3,
        "authoritative_basic_routes": 5,
        "assignment_additions": 12,
        "isolated_manifest_recipes": 346,
        "isolated_automatic_recipes": 177,
        "isolated_compiled_recipe_cards": 414,
        "isolated_exact_removals": 730,
        "managed_dependency_edges": 890,
        "managed_dependency_warnings": 0,
        "physical_progression": "passed",
        "transmission_foundation_regression": "passed",
        "extreme_transmission_regression": "passed",
        "storage_ladder_regression": "passed",
        "induction_matrix_regression": "passed",
        "steelworks_regression": "passed",
    }
    for field, expected_value in expected_result.items():
        if result.get(field) != expected_value:
            errors.append(f"validation_result.{field} must be {expected_value!r}")
    return errors


def mutation_tests(
    plan: dict[str, Any], catalog: Path, manifest: Mapping[str, Any], mods: Path,
    seed: Mapping[str, Any], assignments: Mapping[str, Any],
) -> list[str]:
    tests: list[tuple[str, dict[str, Any], Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], str]] = []
    wrong_output = copy.deepcopy(plan)
    wrong_output["replacement_contracts"][1]["output"] = "7x mekanism:advanced_logistical_transporter"
    tests.append(("seven-segment output", wrong_output, seed, manifest, assignments, "output must be eight"))
    cheap_prior = copy.deepcopy(plan)
    cheap_prior["replacement_contracts"][6]["inputs"][0] = "mekanism:advanced_logistical_transporter"
    tests.append(("one-segment upgrade", cheap_prior, seed, manifest, assignments, "requires exactly 8x"))
    missing_breaker = copy.deepcopy(plan)
    missing_breaker["replacement_contracts"][11]["inputs"].pop()
    tests.append(("lost request control", missing_breaker, seed, manifest, assignments, "missing family-specific infrastructure"))
    nuclear_press = copy.deepcopy(plan)
    nuclear_press["replacement_contracts"][14]["machine"] = REFINED_PRESS
    tests.append(("post-nuclear press", nuclear_press, seed, manifest, assignments, "wrong Encased press"))
    generic_logistics = copy.deepcopy(plan)
    generic_logistics["replacement_contracts"][11]["inputs"][3] = "4x tfmg:rubber_sheet"
    tests.append(("generic Ultimate logistics", generic_logistics, seed, manifest, assignments, "missing family-specific infrastructure"))
    missing_assignment = copy.deepcopy(plan)
    missing_assignment["assignment_additions"][1]["outputs"].pop()
    tests.append(("missing assignment", missing_assignment, seed, manifest, assignments, "twelve implemented"))
    cyclic = copy.deepcopy(plan)
    cyclic["replacement_contracts"][6]["depends_on_batch"].append(managed_id("ultimate", "logistical_transporter"))
    tests.append(("cycle", cyclic, seed, manifest, assignments, "dependency cycle"))
    stale_source = copy.deepcopy(plan)
    stale_source["source_recipe_contracts"][0]["stock_output_count"] = 1
    tests.append(("stale stock count", stale_source, seed, manifest, assignments, "stock output count changed"))

    stale_status = copy.deepcopy(plan)
    stale_status["status"] = "review_only"
    tests.append(("stale status", stale_status, seed, manifest, assignments, "status must be implemented_in_seed"))

    missing_seed = copy.deepcopy(seed)
    missing_seed["recipes"] = [
        recipe for recipe in missing_seed.get("recipes", [])
        if recipe.get("id") != managed_id("advanced", "logistical_transporter")
    ]
    tests.append(("missing explicit seed owner", plan, missing_seed, manifest, assignments, "absent from authoritative seed"))

    drifted_seed = copy.deepcopy(seed)
    recipes_by_id(drifted_seed)[managed_id("elite", "mechanical_pipe")]["machine"] = PRESS["advanced"]
    tests.append(("drifted explicit seed owner", plan, drifted_seed, manifest, assignments, "authoritative seed differs"))

    copied_universal = copy.deepcopy(seed)
    copied_universal["recipes"].append(seed_spec(plan["replacement_contracts"][0]))
    tests.append(("copied retired Universal owner", plan, copied_universal, manifest, assignments, "retired automatic Universal Cable ID survived"))

    missing_universal = copy.deepcopy(manifest)
    missing_universal["recipes"] = [
        recipe for recipe in missing_universal.get("recipes", [])
        if recipe.get("id") != source_universal_id("elite")
    ]
    tests.append(("missing source-owned Universal owner", plan, seed, missing_universal, assignments, "source-owned Universal Cable managed ID is absent"))

    reordered_assignments = copy.deepcopy(assignments)
    unlocks = reordered_assignments["nodes"][NODE["ultimate"]]["unlocks"]
    left = unlocks.index(item_id("ultimate", "logistical_transporter"))
    right = unlocks.index(item_id("ultimate", "mechanical_pipe"))
    unlocks[left], unlocks[right] = unlocks[right], unlocks[left]
    tests.append(("assignment reorder", plan, seed, manifest, reordered_assignments, "preserve the locked transmitter sequence"))

    changed_basic = copy.deepcopy(seed)
    recipes_by_id(changed_basic)[basic_recipe("mechanical_pipe")]["output"] = "4x mekanism:basic_mechanical_pipe"
    tests.append(("Basic route changed", plan, changed_basic, manifest, assignments, "authoritative Basic seed route changed"))

    failures: list[str] = []
    for name, mutated_plan, mutated_seed, mutated_manifest, mutated_assignments, expected in tests:
        found = validate(
            mutated_plan, catalog, mutated_manifest, mods,
            mutated_seed, mutated_assignments,
        )
        if not any(expected in error for error in found):
            failures.append(f"mutation test {name!r} was not rejected with {expected!r}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--mods", type=Path, default=None)
    parser.add_argument("--skip-mutation-tests", action="store_true")
    args = parser.parse_args()
    try:
        plan = load_object(args.plan.resolve())
        catalog = args.catalog.resolve()
        manifest = load_object(args.manifest.resolve())
        seed = load_object(args.seed.resolve())
        assignments = load_object(args.assignments.resolve())
        mods = (args.mods or default_mods()).resolve()
        errors = validate(plan, catalog, manifest, mods, seed, assignments)
        if not args.skip_mutation_tests:
            errors.extend(mutation_tests(plan, catalog, manifest, mods, seed, assignments))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("Checked 15 installed stock recipes/counts, 12 source-owned exact-machine cards, 3 stable Universal routes, 5 authoritative Basic recipes, three locked transmitter segments after the exact Factory transformation, 5 family ladders, the DAG, and 15 mutations.")
    if errors:
        print(f"FAIL: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("PASS / IMPLEMENTED: the transmitter-upgrade batch is source-owned after Extreme Power Transmission.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
