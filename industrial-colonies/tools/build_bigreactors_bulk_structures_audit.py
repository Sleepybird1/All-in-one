#!/usr/bin/env python3
"""Build the read-only Big Reactors bulk/controller redesign review package.

This builder writes only the three batch-owned review artifacts.  It has no
mode that mutates the managed seed, assignments, generated output, quests, or
the live pack.  The exported patch is therefore a deterministic integration
plan for the parent task's single-writer workflow.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sqlite3
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
DEFAULT_CATALOG = WORKSPACE / "outputs/recipe-catalog-current/recipe_catalog.sqlite"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_AUTOMATIC = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
DEFAULT_FTB = PROJECT / "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json"
DEFAULT_PHYSICAL = PROJECT / "progression/physical_recipe_tiers.json"
DEFAULT_RESTORATION = PROJECT / "STOCK_UTILITY_RESTORATION_AUDIT.patch.json"
DEFAULT_PLAN = PROJECT / "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.plan.json"
DEFAULT_PATCH = PROJECT / "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.patch.json"
DEFAULT_MARKDOWN = PROJECT / "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.md"

BATCH_ID = "bigreactors_bulk_structures_and_controllers"
EXTREME_REACTORS_JAR = "ExtremeReactors2-1.21.1-2.4.28.jar"
CREATE_COMPAT_JAR = "ExtremeReactors2-CreateCompat-1.21.1-1.0.4.jar"
ENCASED_JAR = "Create Encased-1.21.1-1.9.0-ht3.jar"
EXPECTED_JAR_HASHES = {
    EXTREME_REACTORS_JAR: "74FDFDFC91C3C8E5A439D411E6F081D12193635FFFE2C55142F2F28F75B9D621",
    CREATE_COMPAT_JAR: "A6F4DFA81DF77908118CF907BCE192D93B6BFC96A7B18CB45470133137E98A23",
    ENCASED_JAR: "E93BB110241AB8283C6238590EB04F1FB37199815623F53F3E981EE650F344A3",
}

INDUSTRIAL = "createcasing:industrial_iron_press"
WEATHERED = "createcasing:weathered_iron_press"
RADIANT = "createcasing:refined_radiance_press"


class AuditBuildError(ValueError):
    """Raised when a reviewed source or integration precondition drifted."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise AuditBuildError(f"expected a JSON object: {path}")
    return value


def stack(count: int, identity: str) -> str:
    return identity if count == 1 else f"{count}x {identity}"


def compact(
    identity: str,
    output: str,
    output_count: int,
    node: str,
    order: int,
    machine: str,
    inputs: list[str],
    comment: str,
    *,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": identity,
        "node": node,
        "phase": "Nuclear Engineering",
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": inputs,
        "output": stack(output_count, output),
        "exclusive_output": True,
    }
    if depends_on:
        result["depends_on"] = depends_on
    return result


def controller(
    identity: str,
    output: str,
    node: str,
    order: int,
    pattern: list[str],
    key: dict[str, str],
    comment: str,
    *,
    depends_on: list[str],
) -> dict[str, Any]:
    return {
        "id": identity,
        "node": node,
        "phase": "Nuclear Engineering",
        "order": order,
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "exclusive_output": True,
        "depends_on": depends_on,
    }


def replacement_contracts() -> list[dict[str, Any]]:
    containment = "CR01 — Containment Engineering"
    core = "CR01 — Core Engineering"
    criticality = "CR01 — First Criticality"
    reprocessing = "CR01 — Fuel Reprocessing"
    advanced = "CR01 — Advanced Nuclear Fuel"

    basic_casing = "industrial_colonies:bigreactors/basic_reactor/casing"
    basic_control = "industrial_colonies:bigreactors/basic_reactor/control_rod"
    basic_fuel = "industrial_colonies:bigreactors/basic_reactor/fuel_rod"
    turbine_casing = "industrial_colonies:bigreactors/basic_turbine/casing"
    turbine_controller = "industrial_colonies:bigreactors/basic_turbine/controller"
    turbine_bearing = "industrial_colonies:bigreactors/basic_turbine/rotor_bearing"
    turbine_blade = "industrial_colonies:bigreactors/basic_turbine/rotor_blade"
    turbine_shaft = "industrial_colonies:bigreactors/basic_turbine/rotor_shaft"
    energizer_casing = "industrial_colonies:bigreactors/energizer/casing"
    energizer_controller = "industrial_colonies:bigreactors/energizer/controller"
    fluidizer_casing = "industrial_colonies:bigreactors/fluidizer/casing"
    fluidizer_controller = "industrial_colonies:bigreactors/fluidizer/controller"
    reprocessor_casing = "industrial_colonies:bigreactors/reprocessor/casing"
    reprocessor_controller = "industrial_colonies:bigreactors/reprocessor/controller"
    reinforced_casing = "industrial_colonies:bigreactors/reinforced_reactor/casing"
    reinforced_turbine_casing = "industrial_colonies:bigreactors/reinforced_turbine/casing"

    contracts = [
        compact(
            basic_casing,
            "bigreactors:basic_reactorcasing",
            8,
            containment,
            300,
            INDUSTRIAL,
            [
                "4x tfmg:steel_casing",
                "8x tfmg:heavy_plate",
                "4x tfmg:fireproof_bricks",
                "#c:ingots/graphite",
                "#c:ingots/graphite",
                "#c:ingots/graphite",
                "#c:ingots/graphite",
                "2x tfmg:steel_mechanism",
            ],
            "Press eight graphite-lined reactor wall segments from reusable TFMG steel containment subassemblies.",
        ),
        compact(
            basic_control,
            "bigreactors:basic_reactorcontrolrod",
            2,
            core,
            310,
            INDUSTRIAL,
            [
                "2x bigreactors:basic_reactorcasing",
                "4x tfmg:heavy_plate",
                "2x tfmg:steel_pipe",
                "2x tfmg:steel_mechanism",
                "2x tfmg:transistor_item",
                "2x minecraft:piston",
            ],
            "Form two serviceable graphite-control actuators around the completed basic containment shell.",
            depends_on=[basic_casing],
        ),
        compact(
            basic_fuel,
            "bigreactors:basic_reactorfuelrod",
            4,
            core,
            320,
            INDUSTRIAL,
            [
                "2x bigreactors:basic_reactorcasing",
                "8x tfmg:steel_pipe",
                "4x tfmg:fireproof_bricks",
                "#c:ingots/graphite",
                "#c:ingots/graphite",
                "#c:ingots/graphite",
                "#c:ingots/graphite",
                "4x mekanism:ingot_uranium",
            ],
            "Seal four basic fuel channels around enriched Mekanism uranium; Yellorium is never reversed into finished uranium here.",
            depends_on=[basic_casing],
        ),
        compact(
            energizer_casing,
            "bigreactors:energizercasing",
            8,
            criticality,
            330,
            INDUSTRIAL,
            [
                "4x tfmg:steel_casing",
                "8x tfmg:heavy_plate",
                "4x tfmg:transformer",
                "4x tfmg:capacitor_item",
                "2x tfmg:steel_cable_hub",
            ],
            "Press eight transformer-backed Energizer shell segments without consuming any reactant the Energizer enables.",
        ),
        controller(
            energizer_controller,
            "bigreactors:energizercontroller",
            criticality,
            340,
            [" RMR ", "RTPTR", "MCAUM", "RTEER", " RMR "],
            {
                "R": "create:refined_radiance_casing",
                "M": "computercraft:monitor_advanced",
                "T": "tfmg:transformer",
                "P": "tfmg:capacitor_item",
                "C": "computercraft:computer_advanced",
                "A": "bigreactors:energizercasing",
                "U": "mekanism:elite_control_circuit",
                "E": "ae2:engineering_processor",
            },
            "Integrate Energizer power regulation, four advanced displays, and a ComputerCraft control core inside a Radiant instrument shell.",
            depends_on=[
                energizer_casing,
                "industrial_colonies:tfmg_heavy_electrical/transformer",
                "industrial_colonies:ae2/engineering_processor",
                "industrial_colonies:computercraft/computer/advanced_upgrade",
                "industrial_colonies:computercraft/monitor/advanced",
            ],
        ),
        compact(
            fluidizer_casing,
            "bigreactors:fluidizercasing",
            8,
            criticality,
            350,
            INDUSTRIAL,
            [
                "4x tfmg:steel_casing",
                "8x tfmg:heavy_plate",
                "2x tfmg:steel_chemical_vat",
                "4x tfmg:steel_pipe",
                "2x tfmg:electric_pump",
            ],
            "Press eight pressure-rated Fluidizer shell segments from TFMG vats, pipework, and pumps without consuming its future product.",
        ),
        controller(
            fluidizer_controller,
            "bigreactors:fluidizercontroller",
            criticality,
            360,
            [" RMR ", "RVPVR", "MCAUM", "RVEER", " RMR "],
            {
                "R": "create:refined_radiance_casing",
                "M": "computercraft:monitor_advanced",
                "V": "tfmg:steel_chemical_vat",
                "P": "tfmg:electric_pump",
                "C": "computercraft:computer_advanced",
                "A": "bigreactors:fluidizercasing",
                "U": "mekanism:elite_control_circuit",
                "E": "ae2:engineering_processor",
            },
            "Integrate pressure control, four advanced displays, and a ComputerCraft process core inside a Radiant instrument shell.",
            depends_on=[
                fluidizer_casing,
                "industrial_colonies:ae2/engineering_processor",
                "industrial_colonies:computercraft/computer/advanced_upgrade",
                "industrial_colonies:computercraft/monitor/advanced",
            ],
        ),
        compact(
            turbine_casing,
            "bigreactors:basic_turbinecasing",
            8,
            criticality,
            370,
            INDUSTRIAL,
            [
                "4x tfmg:steel_casing",
                "8x tfmg:heavy_plate",
                "4x bigreactors:cyanite_ingot",
                "2x tfmg:transformer",
                "2x tfmg:steel_mechanism",
            ],
            "Press eight generator shell segments only after a basic reactor has produced its first Cyanite waste.",
            depends_on=["industrial_colonies:nuclear/basic_reactor_controller"],
        ),
        compact(
            turbine_bearing,
            "bigreactors:basic_turbinerotorbearing",
            1,
            criticality,
            380,
            INDUSTRIAL,
            [
                "2x bigreactors:basic_turbinecasing",
                "8x tfmg:heavy_plate",
                "4x tfmg:steel_mechanism",
                "4x create:large_cogwheel",
                "4x create:shaft",
            ],
            "Balance one serviceable turbine bearing from a casing cradle and a reusable TFMG drive cartridge.",
            depends_on=[turbine_casing],
        ),
        compact(
            turbine_blade,
            "bigreactors:basic_turbinerotorblade",
            4,
            criticality,
            390,
            INDUSTRIAL,
            [
                "2x bigreactors:basic_turbinecasing",
                "8x tfmg:heavy_plate",
                "4x bigreactors:cyanite_ingot",
                "4x tfmg:steel_mechanism",
            ],
            "Stamp four matched Cyanite-alloy rotor blades as an economical turbine expansion batch.",
            depends_on=[turbine_casing],
        ),
        compact(
            turbine_shaft,
            "bigreactors:basic_turbinerotorshaft",
            4,
            criticality,
            400,
            INDUSTRIAL,
            [
                "2x bigreactors:basic_turbinecasing",
                "8x create:shaft",
                "4x tfmg:steel_pipe",
                "4x tfmg:steel_mechanism",
                "2x bigreactors:cyanite_ingot",
            ],
            "Press four keyed rotor-shaft modules around TFMG pipe and drive mechanisms.",
            depends_on=[turbine_casing],
        ),
        controller(
            turbine_controller,
            "bigreactors:basic_turbinecontroller",
            criticality,
            410,
            [" RMR ", "KTEEK", "MCAUM", "RTEER", " RMR "],
            {
                "R": "create:refined_radiance_casing",
                "M": "computercraft:monitor_advanced",
                "K": "bigreactors:basic_turbinecasing",
                "T": "tfmg:transformer",
                "E": "ae2:engineering_processor",
                "C": "computercraft:computer_advanced",
                "A": "bigreactors:basic_reactorcontroller",
                "U": "mekanism:elite_control_circuit",
            },
            "Build a turbine governor around the proven basic-reactor controller, four displays, AE diagnostics, and TFMG transformers.",
            depends_on=[
                turbine_casing,
                "industrial_colonies:nuclear/basic_reactor_controller",
                "industrial_colonies:tfmg_heavy_electrical/transformer",
                "industrial_colonies:ae2/engineering_processor",
                "industrial_colonies:computercraft/computer/advanced_upgrade",
                "industrial_colonies:computercraft/monitor/advanced",
            ],
        ),
        compact(
            reprocessor_casing,
            "bigreactors:reprocessorcasing",
            8,
            reprocessing,
            500,
            WEATHERED,
            [
                "4x tfmg:steel_casing",
                "8x tfmg:heavy_plate",
                "4x bigreactors:cyanite_ingot",
                "2x tfmg:steel_chemical_vat",
                "4x tfmg:steel_pipe",
                "2x tfmg:steel_fluid_valve",
            ],
            "Pressure-seal eight Cyanite-handling reprocessor wall segments on the Weathered Iron line.",
            depends_on=["industrial_colonies:nuclear/basic_reactor_controller"],
        ),
        compact(
            "industrial_colonies:bigreactors/reprocessor/collector",
            "bigreactors:reprocessorcollector",
            1,
            reprocessing,
            510,
            WEATHERED,
            [
                "2x bigreactors:reprocessorcasing",
                "2x create:item_vault",
                "2x create:smart_chute",
                "2x tfmg:steel_mechanism",
            ],
            "Build a shielded product collector from the completed casing and bulk Create logistics hardware.",
            depends_on=[reprocessor_casing],
        ),
        compact(
            "industrial_colonies:bigreactors/reprocessor/fluid_injector",
            "bigreactors:reprocessorfluidinjector",
            1,
            reprocessing,
            520,
            WEATHERED,
            [
                "bigreactors:reprocessorcasing",
                "2x tfmg:steel_chemical_vat",
                "2x tfmg:electric_pump",
                "4x tfmg:steel_pipe",
                "2x tfmg:steel_fluid_valve",
            ],
            "Seal a metered reprocessing-fluid injector from TFMG vats, pumps, pipe, and isolation valves.",
            depends_on=[reprocessor_casing],
        ),
        compact(
            "industrial_colonies:bigreactors/reprocessor/output_port",
            "bigreactors:reprocessoroutputport",
            1,
            reprocessing,
            530,
            WEATHERED,
            [
                "bigreactors:reprocessorcasing",
                "create:item_vault",
                "create:smart_chute",
                "2x tfmg:steel_mechanism",
                "tfmg:steel_frame",
            ],
            "Press a shielded solid-output port around a bulk vault, smart chute, and TFMG service frame.",
            depends_on=[reprocessor_casing],
        ),
        compact(
            "industrial_colonies:bigreactors/reprocessor/power_port",
            "bigreactors:reprocessorpowerport",
            1,
            reprocessing,
            540,
            WEATHERED,
            [
                "bigreactors:reprocessorcasing",
                "2x tfmg:transformer",
                "2x tfmg:steel_cable_hub",
                "mekanism:energy_tablet",
                "electroenergetics:connector",
            ],
            "Terminate reprocessor power through TFMG transformers and serviceable grid conductor hardware.",
            depends_on=[
                reprocessor_casing,
                "industrial_colonies:tfmg_heavy_electrical/transformer",
            ],
        ),
        compact(
            "industrial_colonies:bigreactors/reprocessor/waste_injector",
            "bigreactors:reprocessorwasteinjector",
            1,
            reprocessing,
            550,
            WEATHERED,
            [
                "bigreactors:reprocessorcasing",
                "tfmg:steel_chemical_vat",
                "tfmg:electric_pump",
                "4x tfmg:steel_pipe",
                "tfmg:steel_fluid_valve",
                "mekanism:basic_chemical_tank",
            ],
            "Build a contained waste injector with TFMG pressure hardware and a replaceable Mekanism buffer tank.",
            depends_on=[reprocessor_casing],
        ),
        controller(
            reprocessor_controller,
            "bigreactors:reprocessorcontroller",
            reprocessing,
            560,
            ["RMMMR", "RVAVR", "CUBUC", "RETER", " RMR "],
            {
                "R": "create:refined_radiance_casing",
                "M": "computercraft:monitor_advanced",
                "V": "tfmg:steel_chemical_vat",
                "A": "bigreactors:reprocessorcasing",
                "C": "computercraft:computer_advanced",
                "U": "mekanism:ultimate_control_circuit",
                "B": "bigreactors:basic_reactorcontroller",
                "E": "ae2:engineering_processor",
                "T": "tfmg:transformer",
            },
            "Build the reprocessor control room from two advanced computers, four monitors, the proven reactor controller, and TFMG process hardware.",
            depends_on=[
                reprocessor_casing,
                "industrial_colonies:nuclear/basic_reactor_controller",
                "industrial_colonies:tfmg_heavy_electrical/transformer",
                "industrial_colonies:ae2/engineering_processor",
                "industrial_colonies:computercraft/computer/advanced_upgrade",
                "industrial_colonies:computercraft/monitor/advanced",
            ],
        ),
        compact(
            reinforced_casing,
            "bigreactors:reinforced_reactorcasing",
            8,
            advanced,
            600,
            RADIANT,
            [
                "8x bigreactors:basic_reactorcasing",
                "8x tfmg:heavy_plate",
                "4x create:refined_radiance_casing",
                "4x mekanism:alloy_atomic",
                "2x mekanism:pellet_plutonium",
                "4x bigreactors:blutonium_ingot",
                "2x bigreactors:reprocessorcasing",
            ],
            "Upgrade eight basic walls only after reprocessing yields Blutonium and the Mekanism actinide line yields Plutonium Pellets.",
            depends_on=[basic_casing, reprocessor_controller],
        ),
        compact(
            "industrial_colonies:bigreactors/reinforced_reactor/control_rod",
            "bigreactors:reinforced_reactorcontrolrod",
            2,
            advanced,
            610,
            RADIANT,
            [
                "2x bigreactors:basic_reactorcontrolrod",
                "2x bigreactors:reinforced_reactorcasing",
                "4x tfmg:heavy_plate",
                "2x tfmg:steel_mechanism",
                "2x mekanism:ultimate_control_circuit",
            ],
            "Upgrade two proven control assemblies with Radiant containment and ultimate regulation hardware.",
            depends_on=[reinforced_casing, basic_control],
        ),
        compact(
            "industrial_colonies:bigreactors/reinforced_reactor/fuel_rod",
            "bigreactors:reinforced_reactorfuelrod",
            4,
            advanced,
            620,
            RADIANT,
            [
                "4x bigreactors:basic_reactorfuelrod",
                "2x bigreactors:reinforced_reactorcasing",
                "8x tfmg:steel_pipe",
                "4x tfmg:heavy_plate",
                "2x mekanism:pellet_plutonium",
                "4x mekanism:alloy_atomic",
            ],
            "Upgrade four uranium-qualified channels into Plutonium-rated reinforced fuel rods without a Yellorium shortcut.",
            depends_on=[reinforced_casing, basic_fuel],
        ),
        compact(
            reinforced_turbine_casing,
            "bigreactors:reinforced_turbinecasing",
            8,
            advanced,
            630,
            RADIANT,
            [
                "8x bigreactors:basic_turbinecasing",
                "8x tfmg:heavy_plate",
                "4x create:refined_radiance_casing",
                "4x mekanism:alloy_atomic",
                "2x mekanism:pellet_plutonium",
                "4x bigreactors:blutonium_ingot",
                "2x bigreactors:reprocessorcasing",
            ],
            "Upgrade eight basic turbine walls at the Blutonium-Plutonium convergence instead of repeating full electronics in every wall.",
            depends_on=[turbine_casing, reprocessor_controller],
        ),
        compact(
            "industrial_colonies:bigreactors/reinforced_turbine/rotor_bearing",
            "bigreactors:reinforced_turbinerotorbearing",
            1,
            advanced,
            640,
            RADIANT,
            [
                "bigreactors:basic_turbinerotorbearing",
                "2x bigreactors:reinforced_turbinecasing",
                "8x tfmg:heavy_plate",
                "4x tfmg:steel_mechanism",
                "4x mekanism:alloy_atomic",
            ],
            "Rebuild the proven basic bearing as a reinforced high-speed cartridge.",
            depends_on=[reinforced_turbine_casing, turbine_bearing],
        ),
        compact(
            "industrial_colonies:bigreactors/reinforced_turbine/rotor_blade",
            "bigreactors:reinforced_turbinerotorblade",
            4,
            advanced,
            650,
            RADIANT,
            [
                "4x bigreactors:basic_turbinerotorblade",
                "2x bigreactors:reinforced_turbinecasing",
                "8x tfmg:heavy_plate",
                "4x mekanism:alloy_atomic",
            ],
            "Upgrade four matched basic blades as an economical reinforced rotor batch.",
            depends_on=[reinforced_turbine_casing, turbine_blade],
        ),
        compact(
            "industrial_colonies:bigreactors/reinforced_turbine/rotor_shaft",
            "bigreactors:reinforced_turbinerotorshaft",
            4,
            advanced,
            660,
            RADIANT,
            [
                "4x bigreactors:basic_turbinerotorshaft",
                "2x bigreactors:reinforced_turbinecasing",
                "8x tfmg:steel_pipe",
                "4x tfmg:steel_mechanism",
                "4x mekanism:alloy_atomic",
            ],
            "Upgrade four basic shafts into atomic-alloy reinforced drive modules.",
            depends_on=[reinforced_turbine_casing, turbine_shaft],
        ),
        controller(
            "industrial_colonies:bigreactors/reinforced_turbine/controller",
            "bigreactors:reinforced_turbinecontroller",
            advanced,
            670,
            ["RMMMR", "RTETR", "CBAPC", "RUEUR", " RMR "],
            {
                "R": "create:refined_radiance_casing",
                "M": "computercraft:monitor_advanced",
                "T": "tfmg:transformer",
                "E": "ae2:engineering_processor",
                "C": "computercraft:computer_advanced",
                "B": "bigreactors:basic_turbinecontroller",
                "A": "bigreactors:reinforced_turbinecasing",
                "P": "bigreactors:reprocessorcontroller",
                "U": "mekanism:ultimate_control_circuit",
            },
            "Converge the basic turbine governor and reprocessor control room into a redundant reinforced turbine controller.",
            depends_on=[
                reinforced_turbine_casing,
                turbine_controller,
                reprocessor_controller,
                "industrial_colonies:tfmg_heavy_electrical/transformer",
                "industrial_colonies:ae2/engineering_processor",
                "industrial_colonies:computercraft/computer/advanced_upgrade",
                "industrial_colonies:computercraft/monitor/advanced",
            ],
        ),
    ]
    return contracts


def split_stack(value: Any) -> tuple[int, str]:
    if isinstance(value, str):
        if "x " in value:
            count, identity = value.split("x ", 1)
            if count.isdigit():
                return int(count), identity
        return 1, value
    if isinstance(value, dict):
        identity = value.get("id")
        count = value.get("count", 1)
        if isinstance(identity, str) and isinstance(count, int):
            return count, identity
    raise AuditBuildError(f"invalid item stack: {value!r}")


def output_of(recipe: dict[str, Any]) -> tuple[int, str]:
    return split_stack(recipe["output"])


def automatic_batch(automatic: dict[str, Any]) -> dict[str, Any]:
    values = automatic.get("implementation_batches", [])
    matches = [value for value in values if value.get("id") == BATCH_ID]
    if len(matches) != 1:
        raise AuditBuildError(f"expected one automatic batch {BATCH_ID}, got {len(matches)}")
    return matches[0]


def contracts_by_output(contracts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    ids: set[str] = set()
    for recipe in contracts:
        if recipe["id"] in ids:
            raise AuditBuildError(f"duplicate contract id {recipe['id']}")
        ids.add(recipe["id"])
        _, output = output_of(recipe)
        if output in result:
            raise AuditBuildError(f"duplicate contract output {output}")
        result[output] = recipe
    return result


def source_inventory(
    catalog: Path, outputs: list[str]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    connection = sqlite3.connect(catalog)
    try:
        producers: dict[str, list[dict[str, Any]]] = {}
        consumers: dict[str, list[dict[str, Any]]] = {}
        for output in outputs:
            rows = connection.execute(
                """
                SELECT m.recipe_id, m.recipe_type, m.source_jar, m.count,
                       r.source_path
                  FROM item_recipe_map m
                  JOIN recipes r ON r.recipe_id = m.recipe_id
                 WHERE m.item_id = ? AND m.role = 'output'
                 ORDER BY m.recipe_id
                """,
                (output,),
            ).fetchall()
            producers[output] = [
                {
                    "recipe_id": recipe_id,
                    "recipe_type": recipe_type,
                    "source_jar": source_jar,
                    "source_path": source_path,
                    "output_count": int(count or 1),
                }
                for recipe_id, recipe_type, source_jar, count, source_path in rows
            ]
            rows = connection.execute(
                """
                SELECT m.recipe_id, m.recipe_type, m.source_jar, r.source_path
                  FROM item_recipe_map m
                  JOIN recipes r ON r.recipe_id = m.recipe_id
                 WHERE m.item_id = ? AND m.role = 'input'
                 ORDER BY m.recipe_id
                """,
                (output,),
            ).fetchall()
            consumers[output] = [
                {
                    "recipe_id": recipe_id,
                    "recipe_type": recipe_type,
                    "source_jar": source_jar,
                    "source_path": source_path,
                }
                for recipe_id, recipe_type, source_jar, source_path in rows
            ]
        return producers, consumers
    finally:
        connection.close()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest().upper()


def jar_artifacts(mods: Path) -> list[dict[str, str]]:
    result = []
    for name, expected in EXPECTED_JAR_HASHES.items():
        path = mods / name
        if not path.is_file():
            raise AuditBuildError(f"missing reviewed installed artifact: {path}")
        observed = sha256(path)
        if observed != expected:
            raise AuditBuildError(
                f"installed artifact drift for {name}: expected {expected}, got {observed}"
            )
        result.append({"jar": name, "sha256": observed})
    return result


def nonrecipe_reference_inventory(
    mods: Path, outputs: list[str]
) -> dict[str, dict[str, Any]]:
    hits: dict[str, list[str]] = defaultdict(list)
    for jar in sorted(mods.glob("*.jar"), key=lambda value: value.name.lower()):
        try:
            with zipfile.ZipFile(jar) as archive:
                for name in archive.namelist():
                    if not name.endswith(".json") or "/recipe/" in name:
                        continue
                    try:
                        text = archive.read(name).decode("utf-8")
                    except (KeyError, UnicodeDecodeError):
                        continue
                    for output in outputs:
                        if output in text:
                            hits[output].append(f"{jar.name}!/{name}")
        except zipfile.BadZipFile:
            continue

    result: dict[str, dict[str, Any]] = {}
    for output in outputs:
        path = output.split(":", 1)[1]
        expected_loot = (
            f"{EXTREME_REACTORS_JAR}!/data/bigreactors/loot_table/blocks/{path}.json"
        )
        references = sorted(hits.get(output, []))
        loot_tables = [value for value in references if "/loot_table/" in value]
        if loot_tables != [expected_loot]:
            raise AuditBuildError(
                f"non-recipe loot acquisition drift for {output}: {loot_tables}"
            )
        categories = {
            "self_block_loot": 1,
            "advancement_recipe_metadata": sum(
                "/advancement/recipes/" in value for value in references
            ),
            "patchouli_documentation": sum(
                "/patchouli_books/" in value for value in references
            ),
            "item_or_block_tags": sum("/tags/" in value for value in references),
        }
        if sum(categories.values()) != len(references):
            unknown = [
                value
                for value in references
                if not any(
                    fragment in value
                    for fragment in (
                        "/loot_table/",
                        "/advancement/recipes/",
                        "/patchouli_books/",
                        "/tags/",
                    )
                )
            ]
            raise AuditBuildError(
                f"unclassified non-recipe references for {output}: {unknown}"
            )
        result[output] = {
            "block_loot_table": expected_loot,
            "classification": "recovery_only_self_drop",
            "reference_counts": categories,
        }
    return result


def find_json_values(root: Any, wanted: set[str], pointer: str = "") -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    if isinstance(root, dict):
        for key, value in root.items():
            escaped = key.replace("~", "~0").replace("/", "~1")
            result.extend(find_json_values(value, wanted, f"{pointer}/{escaped}"))
    elif isinstance(root, list):
        for index, value in enumerate(root):
            result.extend(find_json_values(value, wanted, f"{pointer}/{index}"))
    elif isinstance(root, str) and root in wanted:
        result.append({"json_pointer": pointer, "value": root})
    return result


def seed_recipe_output(recipe: dict[str, Any]) -> str | None:
    if "output" not in recipe:
        return None
    try:
        return output_of(recipe)[1]
    except (AuditBuildError, KeyError):
        return None


def validate_shared_preconditions(
    contracts: list[dict[str, Any]],
    seed: dict[str, Any],
    assignments: dict[str, Any],
) -> tuple[list[dict[str, str]], bool]:
    by_output = contracts_by_output(contracts)
    contract_ids = {recipe["id"] for recipe in contracts}
    seed_recipes = seed.get("recipes")
    if not isinstance(seed_recipes, list):
        raise AuditBuildError("managed seed recipes must be an array")
    seed_ids = {recipe.get("id") for recipe in seed_recipes if isinstance(recipe, dict)}
    present_contract_ids = sorted(contract_ids & seed_ids)
    if present_contract_ids and set(present_contract_ids) != contract_ids:
        raise AuditBuildError(
            "Big Reactors seed integration is partial: "
            f"{len(present_contract_ids)} of {len(contract_ids)} contract ids exist"
        )
    implemented = set(present_contract_ids) == contract_ids
    if implemented:
        current = {
            recipe.get("id"): recipe
            for recipe in seed_recipes
            if isinstance(recipe, dict) and recipe.get("id") in contract_ids
        }
        drifted = sorted(
            recipe["id"] for recipe in contracts if current.get(recipe["id"]) != recipe
        )
        if drifted:
            raise AuditBuildError(
                f"implemented Big Reactors contract bodies drifted: {drifted}"
            )
    owned = {
        seed_recipe_output(recipe)
        for recipe in seed_recipes
        if isinstance(recipe, dict)
    }
    collisions = sorted(set(by_output) & owned)
    if not implemented and collisions:
        raise AuditBuildError(f"review outputs already have explicit seed owners: {collisions}")
    if implemented and set(collisions) != set(by_output):
        raise AuditBuildError("implemented Big Reactors outputs lost explicit ownership")

    nodes = assignments.get("nodes")
    if not isinstance(nodes, dict):
        raise AuditBuildError("assignment nodes must be an object")
    placements = []
    for output, recipe in by_output.items():
        owners = [
            node
            for node, entry in nodes.items()
            if isinstance(entry, dict)
            and isinstance(entry.get("unlocks"), list)
            and output in entry["unlocks"]
        ]
        if owners != [recipe["node"]]:
            raise AuditBuildError(
                f"assignment placement drift for {output}: expected {[recipe['node']]}, got {owners}"
            )
        placements.append({"output": output, "node": recipe["node"]})
    return placements, implemented


def build_plan(
    catalog: Path,
    mods: Path,
    automatic: dict[str, Any],
    seed: dict[str, Any],
    assignments: dict[str, Any],
    ftb: dict[str, Any],
    physical: dict[str, Any],
    restoration: dict[str, Any],
) -> dict[str, Any]:
    contracts = replacement_contracts()
    by_output = contracts_by_output(contracts)
    batch = automatic_batch(automatic)
    outputs = list(batch.get("outputs", []))
    if set(outputs) != set(by_output) or len(outputs) != 27:
        raise AuditBuildError("replacement contracts do not cover the exact 27-output batch")
    automatic_ids = list(batch.get("managed_ids", []))
    if len(automatic_ids) != 27:
        raise AuditBuildError("automatic batch no longer contains 27 managed ids")
    automatic_map = dict(zip(outputs, automatic_ids, strict=True))
    producers, consumers = source_inventory(catalog, outputs)
    exact_removals = {
        output: [entry["recipe_id"] for entry in producers[output]]
        for output in outputs
    }
    removal_union = sorted(
        {identity for values in exact_removals.values() for identity in values}
    )
    if len(removal_union) != 49:
        raise AuditBuildError(
            f"exact installed producer union drifted: expected 49, got {len(removal_union)}"
        )
    for output, recipe in by_output.items():
        recipe["remove"] = copy.deepcopy(exact_removals[output])

    placements, implemented = validate_shared_preconditions(contracts, seed, assignments)
    expected_source_overrides = {
        "bigreactors:basic_reactorfuelrod":
            "bigreactors:reactor/basic/fuelrod_ingots_uranium",
        "bigreactors:reinforced_reactorfuelrod":
            "bigreactors:reactor/reinforced/fuelrod_ingots_uranium",
    }
    source_overrides = seed.get("source_recipe_overrides")
    if not isinstance(source_overrides, dict):
        raise AuditBuildError("managed seed source_recipe_overrides must be an object")
    observed_source_overrides = {
        output: source_overrides.get(output) for output in expected_source_overrides
    }
    if implemented:
        if any(value is not None for value in observed_source_overrides.values()):
            raise AuditBuildError(
                "implemented Big Reactors recipes retained obsolete fuel-rod source overrides"
            )
    elif observed_source_overrides != expected_source_overrides:
        raise AuditBuildError(
            "review fuel-rod source override precondition drifted: "
            f"{observed_source_overrides}"
        )
    id_map = {
        automatic_map[output]: by_output[output]["id"] for output in outputs
    }
    seed_refs = find_json_values(seed.get("recipes", []), set(id_map))
    if seed_refs:
        raise AuditBuildError(
            f"authoritative seed unexpectedly references retired automatic ids: {seed_refs}"
        )

    ftb_wanted = {
        automatic_map["bigreactors:basic_reactorcasing"],
        automatic_map["bigreactors:basic_reactorfuelrod"],
        automatic_map["bigreactors:basic_reactorcontrolrod"],
        automatic_map["bigreactors:reprocessorcontroller"],
    }
    ftb_new = {id_map[value] for value in ftb_wanted}
    ftb_occurrences = find_json_values(ftb, ftb_wanted | ftb_new)
    if len(ftb_occurrences) != 4:
        raise AuditBuildError(
            "expected four FTB guidance old-or-migrated Big Reactors occurrences, "
            f"got {len(ftb_occurrences)}"
        )
    reverse_id_map = {value: key for key, value in id_map.items()}
    ftb_rewrites = [
        {
            "path": "FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json",
            "json_pointer": entry["json_pointer"],
            "from": (
                entry["value"]
                if entry["value"] in id_map
                else reverse_id_map[entry["value"]]
            ),
            "to": (
                id_map[entry["value"]]
                if entry["value"] in id_map
                else entry["value"]
            ),
        }
        for entry in sorted(ftb_occurrences, key=lambda value: value["json_pointer"])
    ]

    old_physical_id = "industrial_colonies:machine/fuel_reprocessing/reprocessor_controller"
    new_physical_id = by_output["bigreactors:reprocessorcontroller"]["id"]
    physical_occurrences = find_json_values(
        physical, {old_physical_id, new_physical_id}
    )
    if len(physical_occurrences) != 1:
        raise AuditBuildError(
            "expected one old-or-migrated physical-tier reprocessor id, "
            f"got {len(physical_occurrences)}"
        )
    physical_rewrites = [
        {
            "path": "progression/physical_recipe_tiers.json",
            "json_pointer": physical_occurrences[0]["json_pointer"],
            "from": old_physical_id,
            "to": new_physical_id,
        }
    ]

    protected_preserve = set(restoration.get("recipe_ids_to_preserve", []))
    if protected_preserve & set(removal_union):
        raise AuditBuildError("review removals collide with stock-utility preservation")
    protected_outputs = {
        value
        for value in restoration.get("outputs_to_exclude", [])
        if value.startswith("bigreactors:") or value.startswith("er2create:")
    }

    preserved_consumers = {
        output: [
            entry
            for entry in consumers[output]
            if entry["recipe_id"] not in set(removal_union)
        ]
        for output in outputs
    }

    source_artifacts = jar_artifacts(mods)
    nonrecipe = nonrecipe_reference_inventory(mods, outputs)

    target_entries = []
    for output in outputs:
        recipe = by_output[output]
        count, _ = output_of(recipe)
        target_entries.append(
            {
                "output": output,
                "automatic_managed_id": automatic_map[output],
                "source_owned_id": recipe["id"],
                "node": recipe["node"],
                "process": recipe["type"],
                "machine": recipe.get("machine"),
                "output_count": count,
                "installed_producers": producers[output],
                "preserved_installed_consumers": preserved_consumers[output],
                "nonrecipe_acquisition": nonrecipe[output],
            }
        )

    return {
        "schema_version": 1,
        "status": (
            "implemented_in_seed" if implemented else "review_ready_no_shared_mutation"
        ),
        "plan_id": "redesign_bigreactors_bulk_structures_and_controllers",
        "audited_on": "2026-08-31",
        "decision": "GO_WITH_27_SOURCE_OWNED_TFMG_FIRST_NUCLEAR_CONTRACTS",
        "scope": {
            "outputs": 27,
            "source_owned_contracts": 27,
            "automatic_owners_retired": 27,
            "installed_recipe_producers_removed_exactly": 49,
            "compacting_contracts": 22,
            "controller_mechanical_crafting_contracts": 5,
            "assignment_changes": 0,
            "source_recipe_overrides_retired": 2,
            "ftb_guidance_id_rewrites": 4,
            "physical_tier_id_rewrites": 1,
        },
        "source_artifacts": source_artifacts,
        "automatic_batch_contract": copy.deepcopy(batch),
        "targets": target_entries,
        "replacement_contracts": contracts,
        "automatic_to_source_owned_ids": id_map,
        "assignment_contract": {
            "changes": [],
            "required_existing_placements": sorted(
                placements, key=lambda value: (value["node"], value["output"])
            ),
        },
        "progression_contract": {
            "ranked_physical_lines": [
                {
                    "rank": 0,
                    "name": "precritical_basic_reactor_and_fuel_processing_shells",
                    "rule": "No Cyanite, Blutonium, Plutonium, Magentite, reactor waste, fissile fuel, or reprocessor/reinforced output may build the first reactor or the Energizer/Fluidizer that precede their own products.",
                },
                {
                    "rank": 1,
                    "name": "first_reactor_turbine_and_reprocessing",
                    "rule": "Basic turbine and reprocessor containment consume Cyanite, physically proving a basic reactor has run.",
                },
                {
                    "rank": 2,
                    "name": "reinforced_plutonium_infrastructure",
                    "rule": "Reinforced casings converge upgraded basic structures, reprocessor hardware and Blutonium, and Mekanism Plutonium Pellets; downstream rods and rotors inherit that gate.",
                },
            ],
            "uranium_direction": "bigreactors:yellorium_ingot -> managed enrichment chain -> mekanism:ingot_uranium -> four basic fuel rods; no recipe in this batch turns uranium back into Yellorium or obtains uranium from a Big Reactors structure.",
            "sulfuric_acid_policy": "This construction batch neither produces nor consumes sulfuric acid. Its sole synthesis remains the TFMG Chemical Vat route.",
            "controller_policy": "The five reviewed controllers and the two existing reactor controllers must each consume ComputerCraft computer/monitor hardware, AE diagnostics, a Mekanism control circuit, and meaningful TFMG control or process hardware.",
            "bulk_economy": {
                "casing_outputs": 8,
                "fuel_rod_outputs": 4,
                "rotor_blade_outputs": 4,
                "rotor_shaft_outputs": 4,
                "control_rod_outputs": 2,
            },
            "manufacturing_environments": {
                INDUSTRIAL: 9,
                WEATHERED: 6,
                RADIANT: 7,
                "create:mechanical_crafter_with_refined_radiance_shell": 5,
            },
        },
        "stock_utility_preservation": {
            "rule": "Only the 49 installed producers of the 27 target outputs are removed. Every installed recipe that consumes a target casing/part to make a port, glass, adapter, computer port, power tap, redstone port, display source, or other utility remains untouched.",
            "restoration_audit_protected_outputs": sorted(protected_outputs),
            "restoration_audit_protected_recipe_ids": sorted(
                identity
                for identity in protected_preserve
                if identity.startswith("bigreactors:") or identity.startswith("er2create:")
            ),
            "removal_intersection": [],
        },
        "nonrecipe_acquisition_contract": {
            "allowed": "One exact self-block loot table per target, returning only that target and guarded by minecraft:survives_explosion.",
            "non_acquisition_metadata": [
                "Patchouli guide entries",
                "recipe-unlock advancements",
                "block/item mining and casing-user tags",
            ],
            "forbidden": [
                "chest/entity/gameplay loot",
                "global loot modifiers",
                "world generation",
                "quest item rewards",
                "runtime grants or conversion scripts",
            ],
        },
        "dependency_rewrite_contract": {
            "authoritative_seed_rewrites": [],
            "automatic_generated_dependencies": "Regenerate; explicit output ownership replaces old automatic casing/controller IDs for preserved utility recipes.",
            "ftb_guidance_plan_rewrites": ftb_rewrites,
            "physical_tier_plan_rewrites": physical_rewrites,
            "documentation_rewrites": [
                {
                    "path": "COMPUTERCRAFT_REACTOR_FACTORY_PROGRESSION.md",
                    "from": old_physical_id,
                    "to": by_output["bigreactors:reprocessorcontroller"]["id"],
                    "occurrences": 1,
                }
            ],
            "validator_follow_up": [
                "Rerun tools/validate_ftb_post_diesel_guidance_audit.py after the four objective_evidence IDs are updated; its expectations are plan-driven and contain no additional literal Big Reactors auto IDs.",
                "Rerun tools/validate_computercraft_reactor_progression.py after the physical-tier/documentation reprocessor ID is updated.",
            ],
        },
        "seed_patch_contract": {
            "append_recipe_ids": [recipe["id"] for recipe in contracts],
            "replace_dependency_ids": id_map,
            "remove_source_recipe_override_outputs": sorted(
                expected_source_overrides
            ),
            "additional_removals": [],
            "assignment_changes": [],
        },
        "supersession_contract": {
            "supersedes": "The 27 needs_source_owned_redesign entries and generic automatic recipe bodies in AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json.",
            "preserves": "The automatic audit remains source evidence; this package supplies the authoritative replacement contracts for this batch only.",
        },
        "validation_expectations": {
            "compiled_contracts": 27,
            "compiled_type_counts": {"compacting": 22, "mechanical_crafting": 5},
            "compiled_machine_counts": {
                INDUSTRIAL: 9,
                WEATHERED: 6,
                RADIANT: 7,
            },
            "exact_removals": 49,
            "static_single_owner_outputs": 27,
            "nonrecipe_self_drop_loot_tables": 27,
            "preserved_utility_removals": 0,
            "mutation_tests": 36,
        },
    }


SEED_RECIPE_FIELDS = (
    "id",
    "node",
    "phase",
    "order",
    "type",
    "comment",
    "machine",
    "inputs",
    "pattern",
    "key",
    "output",
    "remove",
    "exclusive_output",
    "depends_on",
)


def build_patch(plan: dict[str, Any]) -> dict[str, Any]:
    contracts = plan.get("replacement_contracts")
    if not isinstance(contracts, list) or len(contracts) != 27:
        raise AuditBuildError("plan must contain 27 replacement contracts")
    append = [
        {
            field: copy.deepcopy(recipe[field])
            for field in SEED_RECIPE_FIELDS
            if field in recipe
        }
        for recipe in contracts
    ]
    return {
        "schema_version": 1,
        "status": plan["status"],
        "plan_id": plan["plan_id"],
        "mode": "declarative_seed_patch",
        "preconditions": {
            "recipe_ids_absent": (
                [recipe["id"] for recipe in contracts]
                if plan["status"] == "review_ready_no_shared_mutation"
                else []
            ),
            "recipe_ids_present_exactly": (
                [recipe["id"] for recipe in contracts]
                if plan["status"] == "implemented_in_seed"
                else []
            ),
            "outputs_without_explicit_seed_owner": (
                [output_of(recipe)[1] for recipe in contracts]
                if plan["status"] == "review_ready_no_shared_mutation"
                else []
            ),
            "assignment_placements_unchanged": copy.deepcopy(
                plan["assignment_contract"]["required_existing_placements"]
            ),
            "installed_source_producers": {
                entry["output"]: [
                    source["recipe_id"] for source in entry["installed_producers"]
                ]
                for entry in plan["targets"]
            },
        },
        "seed": {
            "append_recipes": append,
            "replace_dependency_ids": copy.deepcopy(
                plan["automatic_to_source_owned_ids"]
            ),
            "authoritative_dependency_rewrites": [],
            "remove_source_recipe_override_outputs": copy.deepcopy(
                plan["seed_patch_contract"]["remove_source_recipe_override_outputs"]
            ),
            "additional_removals": [],
        },
        "assignments": {"changes": []},
        "external_follow_up": copy.deepcopy(plan["dependency_rewrite_contract"]),
        "expected_effect": {
            "explicit_recipe_owners_added": 27,
            "automatic_recipe_owners_suppressed": 27,
            "exact_stock_recipe_removals": 49,
            "assignment_changes": 0,
            "ftb_guidance_id_rewrites": 4,
            "physical_tier_id_rewrites": 1,
            "documentation_id_rewrites": 1,
            "source_recipe_overrides_retired": 2,
        },
    }


def markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Big Reactors bulk structures and controllers audit",
        "",
        "## Outcome",
        "",
        "The 27 generic automatic owners become source-owned TFMG-first nuclear construction contracts. Bulk expansion remains economical (eight casings, four fuel rods/blades/shafts, and two control rods per run), while the scarce digital parts are concentrated in five recognizable controller assemblies.",
        "",
        "The physical order is explicit: precritical basic reactor and fuel-processing shells; Cyanite-gated turbine/reprocessing; then Blutonium plus Mekanism Plutonium convergence for reinforced infrastructure. No recipe reverses uranium into Yellorium, produces sulfuric acid, or consumes a product from the Energizer/Fluidizer it builds.",
        "",
        "## Exact source-owned contracts",
        "",
        "| Order | Output | Managed ID | Node | Process / environment | Yield | Physical bill | Exact installed removals |",
        "| ---: | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    targets = {entry["output"]: entry for entry in plan["targets"]}
    for recipe in plan["replacement_contracts"]:
        count, output = output_of(recipe)
        process = recipe["type"]
        if recipe.get("machine"):
            process += f" / `{recipe['machine']}`"
        if recipe["type"] == "compacting":
            bill = ", ".join(f"`{value}`" for value in recipe["inputs"])
        else:
            counts: dict[str, int] = defaultdict(int)
            for row in recipe["pattern"]:
                for symbol in row:
                    if symbol != " ":
                        counts[recipe["key"][symbol]] += 1
            bill = ", ".join(
                f"`{stack(amount, identity)}`"
                for identity, amount in sorted(counts.items())
            )
        removals = ", ".join(
            f"`{entry['recipe_id']}`" for entry in targets[output]["installed_producers"]
        )
        lines.append(
            f"| {recipe['order']} | `{output}` | `{recipe['id']}` | {recipe['node']} | {process} | {count} | {bill} | {removals} |"
        )

    lines.extend(
        [
            "",
            "## Bypass and utility result",
            "",
            "The installed catalog contains exactly 49 producers for the 27 outputs, and every one appears as an exact removal on its owning contract. The only non-recipe acquisition is each block's own `minecraft:survives_explosion` loot table, which is recovery rather than bootstrap. Patchouli pages, recipe advancements, and tags are metadata only.",
            "",
            "Every stock recipe that *consumes* these casings or parts to construct glass, ports, taps, adapters, computer ports, redstone ports, or Create display sources remains untouched. The removal union has no intersection with the implemented Stock Utility Restoration preserve set.",
            "",
            "## Required integration rewrites",
            "",
        ]
    )
    for entry in plan["dependency_rewrite_contract"]["ftb_guidance_plan_rewrites"]:
        lines.append(
            f"- `{entry['path']}{entry['json_pointer']}`: `{entry['from']}` -> `{entry['to']}`"
        )
    for entry in plan["dependency_rewrite_contract"]["physical_tier_plan_rewrites"]:
        lines.append(
            f"- `{entry['path']}{entry['json_pointer']}`: `{entry['from']}` -> `{entry['to']}`"
        )
    for entry in plan["dependency_rewrite_contract"]["documentation_rewrites"]:
        lines.append(
            f"- `{entry['path']}` ({entry['occurrences']} occurrence): `{entry['from']}` -> `{entry['to']}`"
        )
    lines.extend(
        [
            "- Regenerate the managed manifest/KJSGen project so preserved stock utilities infer the new casing owners.",
            "- Do not edit assignments; all 27 outputs already occupy the intended five MineColonies nodes.",
            "",
            "## Validation",
            "",
            "Run:",
            "",
            "```powershell",
            "& 'C:\\Users\\GodPC\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' tools/validate_bigreactors_bulk_structures_audit.py",
            "& 'C:\\Users\\GodPC\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' tools/test_validate_bigreactors_bulk_structures_audit.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def write_or_check(path: Path, content: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != content:
            raise AuditBuildError(f"checked-in artifact drifted: {path}")
        return
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--automatic", type=Path, default=DEFAULT_AUTOMATIC)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--ftb", type=Path, default=DEFAULT_FTB)
    parser.add_argument("--physical", type=Path, default=DEFAULT_PHYSICAL)
    parser.add_argument("--restoration", type=Path, default=DEFAULT_RESTORATION)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = build_plan(
            args.catalog.resolve(),
            args.mods.resolve(),
            load_json(args.automatic.resolve()),
            load_json(args.seed.resolve()),
            load_json(args.assignments.resolve()),
            load_json(args.ftb.resolve()),
            load_json(args.physical.resolve()),
            load_json(args.restoration.resolve()),
        )
        patch = build_patch(plan)
        write_or_check(args.plan.resolve(), canonical_json(plan), args.check)
        write_or_check(args.patch.resolve(), canonical_json(patch), args.check)
        write_or_check(args.markdown.resolve(), markdown(plan), args.check)
    except (OSError, ValueError, KeyError, sqlite3.Error, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    verb = "verified" if args.check else "wrote"
    print(
        f"{verb} Big Reactors review package: 27 contracts, 49 exact installed "
        "producer removals, zero assignment changes, and four FTB guidance rewrites."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
