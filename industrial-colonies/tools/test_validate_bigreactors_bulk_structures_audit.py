#!/usr/bin/env python3
"""Mutation tests for the Big Reactors bulk/controller audit validator."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any, Callable


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_bigreactors_bulk_structures_audit as validator


Mutation = Callable[[dict[str, Any]], None]


def recipe(plan: dict[str, Any], identity: str) -> dict[str, Any]:
    return next(value for value in plan["replacement_contracts"] if value["id"] == identity)


def case(name: str, target: str, mutate: Mutation, expected: str) -> dict[str, Any]:
    return {"name": name, "target": target, "mutate": mutate, "expected": expected}


def replace_input(value: dict[str, Any], old: str, new: str | None) -> None:
    inputs = value["inputs"]
    index = inputs.index(old)
    if new is None:
        inputs.pop(index)
    else:
        inputs[index] = new


def contract_mutation(identity: str, operation: Callable[[dict[str, Any]], None]) -> Mutation:
    return lambda plan: operation(recipe(plan, identity))


def main() -> int:
    base = {
        "plan": validator.load_json(validator.DEFAULT_PLAN),
        "patch": validator.load_json(validator.DEFAULT_PATCH),
        "automatic": validator.load_json(validator.DEFAULT_AUTOMATIC),
        "seed": validator.load_json(validator.DEFAULT_SEED),
        "assignments": validator.load_json(validator.DEFAULT_ASSIGNMENTS),
        "ftb": validator.load_json(validator.DEFAULT_FTB),
        "physical": validator.load_json(validator.DEFAULT_PHYSICAL),
        "restoration": validator.load_json(validator.DEFAULT_RESTORATION),
        "environments": validator.load_json(validator.DEFAULT_ENVIRONMENTS),
    }

    baseline = validator.validate_plan(
        base["plan"], base["patch"], base["automatic"],
        validator.DEFAULT_CATALOG, validator.DEFAULT_MODS,
        base["seed"], base["assignments"], base["ftb"], base["physical"],
        base["restoration"], base["environments"], validator.DEFAULT_NUCLEAR_QUEST,
        validator.DEFAULT_COMPUTERCRAFT_DOC, deep_artifacts=False, compile_batch=False,
    )
    if baseline:
        print("baseline unexpectedly failed:")
        for failure in baseline:
            print(f"- {failure}")
        return 1

    basic_casing = "industrial_colonies:bigreactors/basic_reactor/casing"
    basic_fuel = "industrial_colonies:bigreactors/basic_reactor/fuel_rod"
    energizer_casing = "industrial_colonies:bigreactors/energizer/casing"
    turbine_casing = "industrial_colonies:bigreactors/basic_turbine/casing"
    reprocessor_casing = "industrial_colonies:bigreactors/reprocessor/casing"
    reinforced_casing = "industrial_colonies:bigreactors/reinforced_reactor/casing"
    controller_id = "industrial_colonies:bigreactors/energizer/controller"

    cases = [
        case("schema version", "plan", lambda p: p.__setitem__("schema_version", 2), "schema_version"),
        case("status", "plan", lambda p: p.__setitem__("status", "done"), "status is neither"),
        case("decision", "plan", lambda p: p.__setitem__("decision", "NO"), "review decision"),
        case("scope", "plan", lambda p: p["scope"].__setitem__("outputs", 26), "scope counts"),
        case("validation summary", "plan", lambda p: p["validation_expectations"].__setitem__("mutation_tests", 35), "validation expectation"),
        case("patch mode", "patch", lambda p: p.__setitem__("mode", "apply"), "patch mode"),
        case("assignment mutation", "patch", lambda p: p.__setitem__("assignments", {"changes": ["bad"]}), "changes assignments"),
        case("source override retirement", "patch", lambda p: p["seed"].__setitem__("remove_source_recipe_override_outputs", []), "two fuel-rod source overrides"),
        case("broad removal", "patch", lambda p: p["seed"].__setitem__("additional_removals", ["minecraft:stick"]), "broad removals"),
        case("dependency rewrite", "patch", lambda p: p["seed"].__setitem__("authoritative_dependency_rewrites", ["bad"]), "rewrites current seed dependencies"),
        case("contract removed", "plan", lambda p: p["replacement_contracts"].pop(), "contract count"),
        case("duplicate id", "plan", lambda p: p["replacement_contracts"][1].__setitem__("id", p["replacement_contracts"][0]["id"]), "IDs are not unique"),
        case("type count", "plan", contract_mutation(basic_casing, lambda r: r.__setitem__("type", "mechanical_crafting")), "recipe type counts"),
        case("machine count", "plan", contract_mutation(basic_casing, lambda r: r.__setitem__("machine", validator.audit_builder.WEATHERED)), "Encased press counts"),
        case("bulk yield", "plan", contract_mutation(basic_casing, lambda r: r.__setitem__("output", "7x bigreactors:basic_reactorcasing")), "economical output count"),
        case("exact removal", "plan", contract_mutation(basic_casing, lambda r: r["remove"].pop()), "exact installed removals"),
        case("TFMG-first", "plan", contract_mutation(basic_casing, lambda r: r.__setitem__("inputs", ["4x create:industrial_iron_block", "8x create:sturdy_sheet", "4x #c:ingots/graphite"])), "no longer TFMG-first"),
        case("sulfuric acid", "plan", contract_mutation(basic_casing, lambda r: r["inputs"].append("tfmg:sulfuric_acid")), "consumes sulfuric acid"),
        case("generic ring", "plan", contract_mutation(controller_id, lambda r: (r.__setitem__("pattern", copy.deepcopy(validator.GENERIC_RING)), r.__setitem__("key", {"A": "create:refined_radiance_casing", "B": "tfmg:transformer", "C": "computercraft:monitor_advanced", "D": "computercraft:computer_advanced", "E": "mekanism:elite_control_circuit"}))), "generic A/B gate ring"),
        case("controller dimensions", "plan", contract_mutation(controller_id, lambda r: r["pattern"].pop()), "not a deliberate 5x5"),
        case("Radiant shell", "plan", contract_mutation(controller_id, lambda r: r["key"].__setitem__("R", "create:andesite_casing")), "lost its Radiant shell"),
        case("computer hardware", "plan", contract_mutation(controller_id, lambda r: r["key"].__setitem__("C", "tfmg:circuit_board")), "ComputerCraft computer count"),
        case("monitor hardware", "plan", contract_mutation(controller_id, lambda r: r["key"].__setitem__("M", "tfmg:circuit_board")), "ComputerCraft monitor count"),
        case("AE diagnostics", "plan", contract_mutation(controller_id, lambda r: r["key"].__setitem__("E", "tfmg:circuit_board")), "AE diagnostics disappeared"),
        case("Mekanism controls", "plan", contract_mutation(controller_id, lambda r: r["key"].__setitem__("U", "tfmg:circuit_board")), "Mekanism control hardware disappeared"),
        case("precritical Cyanite", "plan", contract_mutation(basic_casing, lambda r: r["inputs"].append("bigreactors:cyanite_ingot")), "precritical bootstrap ingredient"),
        case("fuel processor product", "plan", contract_mutation(energizer_casing, lambda r: r["inputs"].append("bigreactors:yellorium_ingot")), "consumes a fuel product"),
        case("uranium count", "plan", contract_mutation(basic_fuel, lambda r: replace_input(r, "4x mekanism:ingot_uranium", "3x mekanism:ingot_uranium")), "four canonical Mekanism uranium"),
        case("Yellorium shortcut", "plan", contract_mutation(basic_fuel, lambda r: r["inputs"].append("bigreactors:yellorium_ingot")), "regained a Yellorium shortcut"),
        case("turbine Cyanite gate", "plan", contract_mutation(turbine_casing, lambda r: replace_input(r, "4x bigreactors:cyanite_ingot", None)), "Cyanite proof disappeared"),
        case("reprocessor Cyanite gate", "plan", contract_mutation(reprocessor_casing, lambda r: replace_input(r, "4x bigreactors:cyanite_ingot", None)), "Cyanite proof disappeared"),
        case("Plutonium convergence", "plan", contract_mutation(reinforced_casing, lambda r: replace_input(r, "2x mekanism:pellet_plutonium", None)), "lost mekanism:pellet_plutonium"),
        case("Blutonium convergence", "plan", contract_mutation(reinforced_casing, lambda r: replace_input(r, "4x bigreactors:blutonium_ingot", None)), "lost bigreactors:blutonium_ingot"),
        case("reprocessor convergence", "plan", contract_mutation(reinforced_casing, lambda r: replace_input(r, "2x bigreactors:reprocessorcasing", None)), "lost bigreactors:reprocessorcasing"),
        case("internal cycle", "plan", lambda p: (recipe(p, basic_casing).__setitem__("depends_on", [energizer_casing]), recipe(p, energizer_casing).__setitem__("depends_on", [basic_casing])), "internal dependency cycle"),
        case("FTB stable mapping", "plan", lambda p: p["dependency_rewrite_contract"]["ftb_guidance_plan_rewrites"][0].__setitem__("to", "industrial_colonies:bad/id"), "four stable FTB mappings changed"),
    ]

    if len(cases) != 36:
        print(f"test inventory drifted: expected 36, got {len(cases)}")
        return 1

    failures = []
    for entry in cases:
        fixtures = copy.deepcopy(base)
        entry["mutate"](fixtures[entry["target"]])
        observed = validator.validate_plan(
            fixtures["plan"], fixtures["patch"], fixtures["automatic"],
            validator.DEFAULT_CATALOG, validator.DEFAULT_MODS,
            fixtures["seed"], fixtures["assignments"], fixtures["ftb"],
            fixtures["physical"], fixtures["restoration"], fixtures["environments"],
            validator.DEFAULT_NUCLEAR_QUEST, validator.DEFAULT_COMPUTERCRAFT_DOC,
            deep_artifacts=False, compile_batch=False,
        )
        if not any(entry["expected"] in value for value in observed):
            failures.append(
                f"{entry['name']}: expected {entry['expected']!r}; got {observed}"
            )

    if failures:
        print(f"Big Reactors validator mutation suite failed ({len(failures)} case(s)):")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "Big Reactors validator mutation suite passed: all 36 independent metadata, "
        "patch-scope, manufacturing, controller, physical-order, and dependency-ID "
        "mutations were rejected."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
