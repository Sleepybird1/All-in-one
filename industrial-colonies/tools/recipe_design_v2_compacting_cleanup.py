"""Remove physically implausible whole-machine basin compacting recipes.

This is a pure managed-seed transform.  It deliberately leaves pressure forming,
lamination, pipe/cable batches, cell housings, and structural casing batches in
compacting.  Only exact, already-managed recipe IDs are changed.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def _replace(data: dict[str, Any], recipe_id: str, body: dict[str, Any]) -> bool:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed recipe seed field 'recipes' must be a list")
    matches = [index for index, recipe in enumerate(recipes) if recipe.get("id") == recipe_id]
    if not matches:
        return False
    if len(matches) != 1:
        raise KeyError(f"Expected at most one {recipe_id}, found {len(matches)}")
    old = recipes[matches[0]]
    replacement: dict[str, Any] = {"id": recipe_id}
    for key in ("node", "phase", "order"):
        if key in old:
            replacement[key] = deepcopy(old[key])
    replacement.update(deepcopy(body))
    if "output" not in replacement and "output" in old:
        replacement["output"] = deepcopy(old["output"])
    for key in (
        "remove",
        "exclusive_output",
        "if_mod_loaded",
        "depends_on",
        "components",
    ):
        if key not in replacement and key in old:
            replacement[key] = deepcopy(old[key])
    recipes[matches[0]] = replacement
    return True


def _mechanical(comment: str, pattern: list[str], key: dict[str, str]) -> dict[str, Any]:
    return {
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
    }


def _sequence(
    comment: str,
    input_item: str,
    ingredients: list[str],
    casing: str,
) -> dict[str, Any]:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "loops": 1,
        "steps": [
            {
                "op": "deploying",
                "ingredient": ingredient,
                "machine": f"createcasing:{casing}_deployer",
            }
            for ingredient in ingredients
        ]
        + [{"op": "pressing", "machine": f"createcasing:{casing}_press"}],
    }


def _tfmg_vessels(data: dict[str, Any]) -> None:
    replacements = {
        "industrial_colonies:steelworks/blast_furnace_hatch": _mechanical(
            "Build the tuyere hatch as a refractory wall with a centered tank, paired air pipes, and a cast-iron service face",
            ["FBF", "PTP", "FBF"],
            {
                "F": "tfmg:fireproof_bricks",
                "B": "#c:plates/cast_iron",
                "P": "tfmg:cast_iron_pipe",
                "T": "tfmg:cast_iron_fluid_tank",
            },
        ),
        "industrial_colonies:fluid_infrastructure/cast_iron_chemical_vat": _mechanical(
            "Construct the first chemical vessel as a lead-lined cast-iron shell with a tank core and opposed process connections",
            ["CLC", "PTP", "CLC"],
            {
                "C": "#c:plates/cast_iron",
                "L": "#c:plates/lead",
                "P": "tfmg:cast_iron_pipe",
                "T": "tfmg:cast_iron_fluid_tank",
            },
        ),
        "industrial_colonies:fluid_infrastructure/steel_chemical_vat": _mechanical(
            "Build two pressure-rated vats as nickel-lined steel vessels with paired pipe connections and a shared heavy shell",
            ["HNH", "PTP", "HNH"],
            {
                "H": "tfmg:heavy_plate",
                "N": "#c:plates/nickel",
                "P": "tfmg:steel_pipe",
                "T": "tfmg:steel_fluid_tank",
            },
        ),
        "industrial_colonies:fluid_infrastructure/fireproof_chemical_vat": _sequence(
            "Rebuild a proven steel vat with refractory quadrants, a heavy service frame, precision regulator, and replaceable seal",
            "tfmg:steel_chemical_vat",
            [
                "tfmg:fireproof_bricks",
                "tfmg:fireproof_bricks",
                "tfmg:fireproof_bricks",
                "tfmg:fireproof_bricks",
                "tfmg:heavy_machinery_casing",
                "create:precision_mechanism",
                "tfmg:rubber_sheet",
                "tfmg:steel_pipe",
            ],
            "industrial_iron",
        ),
    }
    for recipe_id, body in replacements.items():
        _replace(data, recipe_id, body)


def _ae2_high_energy(data: dict[str, Any]) -> None:
    replacements = {
        "industrial_colonies:ae2_high_energy/cell_workbench": _sequence(
            "Turn an existing ME terminal into a padded cell-programming bench with storage, control electronics, and a precision tool head",
            "ae2:terminal",
            [
                "#c:chests/wooden",
                "#minecraft:wool",
                "ae2:calculation_processor",
                "tfmg:circuit_board",
                "tfmg:plastic_sheet",
                "create:precision_mechanism",
            ],
            "brass",
        ),
        "industrial_colonies:ae2_high_energy/spatial_anchor": _sequence(
            "Commission a complete spatial IO gateway as an anchor by installing four field emitters, the 128-cubed matrix, regulated power, and engineering control",
            "ae2:spatial_io_port",
            [
                "ae2:spatial_pylon",
                "ae2:spatial_pylon",
                "ae2:spatial_pylon",
                "ae2:spatial_pylon",
                "ae2:spatial_cell_component_128",
                "tfmg:transformer",
                "ae2:engineering_processor",
                "tfmg:steel_casing",
            ],
            "weathered_iron",
        ),
    }
    for recipe_id, body in replacements.items():
        _replace(data, recipe_id, body)


def _bigreactors(data: dict[str, Any]) -> None:
    mechanical = {
        "industrial_colonies:bigreactors/basic_reactor/control_rod": _mechanical(
            "Assemble two control-rod heads as piston actuators over steel guide tubes, service mechanisms, and containment feet",
            ["P P", "T T", "M M", "H H", "C C"],
            {
                "P": "minecraft:piston",
                "T": "tfmg:transistor_item",
                "M": "tfmg:steel_mechanism",
                "H": "tfmg:heavy_plate",
                "C": "bigreactors:basic_reactorcasing",
            },
        ),
        "industrial_colonies:bigreactors/basic_reactor/fuel_rod": _mechanical(
            "Build four uranium-qualified fuel channels as parallel refractory tubes clamped between containment rails",
            ["C   C", "PFPFP", "GUGUG", "PFPFP", "C   C"],
            {
                "C": "bigreactors:basic_reactorcasing",
                "P": "tfmg:steel_pipe",
                "F": "tfmg:fireproof_bricks",
                "G": "#c:ingots/graphite",
                "U": "mekanism:ingot_uranium",
            },
        ),
        "industrial_colonies:bigreactors/basic_turbine/rotor_bearing": _mechanical(
            "Construct the turbine bearing as a symmetric casing cradle around shafts, large gears, heavy races, and service mechanisms",
            [" HCH ", " SGS ", "G M G", " SGS ", " HCH "],
            {
                "H": "tfmg:heavy_plate",
                "C": "bigreactors:basic_turbinecasing",
                "S": "create:shaft",
                "G": "create:large_cogwheel",
                "M": "tfmg:steel_mechanism",
            },
        ),
    }
    for recipe_id, body in mechanical.items():
        _replace(data, recipe_id, body)

    sequences = {
        "industrial_colonies:bigreactors/reprocessor/collector": _sequence(
            "Fit a reprocessor casing with bulk vault storage, paired smart extraction chutes, and serviceable drive hardware",
            "bigreactors:reprocessorcasing",
            ["create:item_vault", "create:smart_chute", "create:smart_chute", "tfmg:steel_mechanism"],
            "weathered_iron",
        ),
        "industrial_colonies:bigreactors/reprocessor/fluid_injector": _sequence(
            "Plumb a reprocessor casing as a metered fluid injector with chemical storage, powered pumping, twin pressure feeds, and isolation",
            "bigreactors:reprocessorcasing",
            ["tfmg:steel_chemical_vat", "tfmg:electric_pump", "tfmg:steel_pipe", "tfmg:steel_pipe", "tfmg:steel_fluid_valve"],
            "weathered_iron",
        ),
        "industrial_colonies:bigreactors/reprocessor/output_port": _sequence(
            "Build the solid-output face into a reprocessor casing with a vault, smart chute, steel frame, and service mechanism",
            "bigreactors:reprocessorcasing",
            ["create:item_vault", "create:smart_chute", "tfmg:steel_frame", "tfmg:steel_mechanism"],
            "weathered_iron",
        ),
        "industrial_colonies:bigreactors/reprocessor/power_port": _sequence(
            "Electrify a reprocessor casing with transformer isolation, a steel cable hub, buffered energy, and a grid connector",
            "bigreactors:reprocessorcasing",
            ["tfmg:transformer", "tfmg:steel_cable_hub", "mekanism:energy_tablet", "electroenergetics:connector"],
            "weathered_iron",
        ),
        "industrial_colonies:bigreactors/reprocessor/waste_injector": _sequence(
            "Configure a reprocessor casing for contained waste feed using a chemical vat, electric pump, pressure line, valve, and buffer tank",
            "bigreactors:reprocessorcasing",
            ["tfmg:steel_chemical_vat", "tfmg:electric_pump", "tfmg:steel_pipe", "tfmg:steel_fluid_valve", "mekanism:basic_chemical_tank"],
            "weathered_iron",
        ),
        "industrial_colonies:bigreactors/reinforced_reactor/control_rod": _sequence(
            "Upgrade a proven control head with reinforced containment, heavy shielding, service mechanics, and ultimate regulation",
            "bigreactors:basic_reactorcontrolrod",
            ["bigreactors:reinforced_reactorcasing", "tfmg:heavy_plate", "tfmg:steel_mechanism", "mekanism:ultimate_control_circuit"],
            "refined_radiance",
        ),
        "industrial_colonies:bigreactors/reinforced_reactor/fuel_rod": _sequence(
            "Rebuild each qualified basic fuel channel with reinforced containment, pressure tubing, shielding, plutonium qualification, and atomic bonding",
            "bigreactors:basic_reactorfuelrod",
            ["bigreactors:reinforced_reactorcasing", "tfmg:steel_pipe", "tfmg:heavy_plate", "mekanism:pellet_plutonium", "mekanism:alloy_atomic"],
            "refined_radiance",
        ),
        "industrial_colonies:bigreactors/reinforced_turbine/rotor_bearing": _sequence(
            "Rebuild the proven turbine bearing as a reinforced high-speed cartridge with containment, heavy races, service mechanics, and atomic bonding",
            "bigreactors:basic_turbinerotorbearing",
            ["bigreactors:reinforced_turbinecasing", "tfmg:heavy_plate", "tfmg:heavy_plate", "tfmg:steel_mechanism", "mekanism:alloy_atomic"],
            "refined_radiance",
        ),
    }
    for recipe_id, body in sequences.items():
        _replace(data, recipe_id, body)


def _space_navigation(data: dict[str, Any]) -> None:
    replacements = {
        "industrial_colonies:space/navigation/velocity_sensor": _sequence(
            "Calibrate a gyroscopic velocity instrument with twin drive motors, voltage telemetry, AE calculation logic, and a protected steel shell",
            "simulated:gyroscopic_mechanism",
            ["tfmg:electric_motor", "tfmg:electric_motor", "tfmg:voltmeter", "tfmg:circuit_board", "ae2:calculation_processor", "tfmg:steel_casing"],
            "refined_radiance",
        ),
        "industrial_colonies:space/navigation/gimbal_sensor": _sequence(
            "Build three-axis attitude sensing around a calibrated gyroscope using magnetic laminations, analog position control, logic, and a steel enclosure",
            "simulated:gyroscopic_mechanism",
            ["tfmg:magnetic_alloy_sheet", "tfmg:magnetic_alloy_sheet", "tfmg:potentiometer", "tfmg:circuit_board", "ae2:logic_processor", "tfmg:steel_casing"],
            "refined_radiance",
        ),
        "industrial_colonies:space/navigation/optical_sensor": _sequence(
            "Populate a protected optical navigation head with aluminum structure, calibrated amethyst optics, discrete amplification, and AE calculation logic",
            "tfmg:steel_casing",
            ["tfmg:aluminum_sheet", "tfmg:aluminum_sheet", "minecraft:amethyst_shard", "minecraft:amethyst_shard", "tfmg:transistor_item", "tfmg:circuit_board", "ae2:calculation_processor"],
            "refined_radiance",
        ),
    }
    for recipe_id, body in replacements.items():
        _replace(data, recipe_id, body)


def apply(data: dict[str, Any]) -> None:
    """Apply all high-confidence compacting cleanups to ``data`` in place."""

    _tfmg_vessels(data)
    _ae2_high_energy(data)
    _bigreactors(data)
    _space_navigation(data)
