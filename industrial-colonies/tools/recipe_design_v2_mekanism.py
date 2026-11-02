#!/usr/bin/env python3
"""Manufacturing-first Mekanism and nuclear structural recipe redesign.

This module is deliberately side-effect free.  ``apply`` mutates only the seed
dictionary supplied by its caller; it does not read, write, build, validate, or
deploy anything.  Existing ownership metadata, removals, dependencies, and any
unknown component metadata are retained while obsolete process fields are
replaced.
"""

from __future__ import annotations

from typing import Any


Recipe = dict[str, Any]


_PROCESS_FIELDS = {
    "type",
    "comment",
    "pattern",
    "key",
    "inputs",
    "input",
    "held",
    "machine",
    "transitional",
    "steps",
    "loops",
    "ingredients",
    "results",
    "outputs",
    "returned_tool",
    "keep_held",
    "heat",
    "processing_time",
    "vat_mode",
    "machine_mode",
    "min_size",
    "infusion",
    "chemical",
    "fluid",
    "fluid_input",
}


def _find(data: dict[str, Any], recipe_id: str) -> Recipe | None:
    """Return the unique managed recipe with ``recipe_id``, if it exists."""

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed recipe seed must contain a recipes list")
    matches = [recipe for recipe in recipes if recipe.get("id") == recipe_id]
    if len(matches) > 1:
        raise ValueError(f"duplicate managed recipe id: {recipe_id}")
    return matches[0] if matches else None


def _replace(data: dict[str, Any], recipe_id: str, body: Recipe) -> None:
    """Replace process data in-place while preserving source-owned metadata."""

    recipe = _find(data, recipe_id)
    if recipe is None:
        return
    for key in _PROCESS_FIELDS:
        recipe.pop(key, None)
    recipe.update(body)


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    comment: str,
    input_item: str,
    output: str,
    steps: list[Recipe],
    transitional: str | None = None,
) -> Recipe:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional or input_item,
        "output": output,
        "loops": 1,
        "steps": steps,
    }


def _redesign_pre_nuclear_machines(data: dict[str, Any]) -> None:
    railway_deployer = "createcasing:railway_deployer"
    railway_press = "createcasing:railway_press"
    industrial_deployer = "createcasing:industrial_iron_deployer"
    industrial_press = "createcasing:industrial_iron_press"

    replacements: dict[str, Recipe] = {
        "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber": _sequence(
            comment=(
                "Build a vibratory enrichment chamber around a high-speed TFMG "
                "rotor, a real milling head, and serviceable drive electronics."
            ),
            input_item="mekanism:steel_casing",
            output="mekanism:enrichment_chamber",
            steps=[
                _deploy("tfmg:rotor", railway_deployer),
                _deploy("create:millstone", railway_deployer),
                _deploy("mekanism:basic_control_circuit", railway_deployer),
                _deploy("tfmg:copper_wire", railway_deployer),
                _deploy("tfmg:steel_mechanism", railway_deployer),
                _press(railway_press),
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/osmium_compressor": _sequence(
            comment=(
                "Install a pumped TFMG pressure vessel, powered platen, and "
                "transformer into a steel machine body."
            ),
            input_item="mekanism:steel_casing",
            output="mekanism:osmium_compressor",
            steps=[
                _deploy("tfmg:steel_chemical_vat", railway_deployer),
                _deploy("create:mechanical_pump", railway_deployer),
                _deploy("tfmg:transformer", railway_deployer),
                _deploy("create:mechanical_press", railway_deployer),
                _deploy("mekanism:basic_control_circuit", railway_deployer),
                _press(railway_press),
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/crusher": {
            "type": "mechanical_crafting",
            "comment": (
                "Arrange two opposed crushing wheels around a steel drive body; "
                "the grid depicts the actual crushing path instead of a gate ring."
            ),
            "pattern": [" H H ", "CWSWC", " H H "],
            "key": {
                "H": "tfmg:heavy_plate",
                "C": "create:crushing_wheel",
                "W": "tfmg:steel_mechanism",
                "S": "mekanism:steel_casing",
            },
            "output": "mekanism:crusher",
        },
        "industrial_colonies:mekanism_pre_nuclear/precision_sawmill": _sequence(
            comment=(
                "Fit a powered saw carriage and one precision feed mechanism into "
                "a steel casing before final heavy alignment."
            ),
            input_item="mekanism:steel_casing",
            output="mekanism:precision_sawmill",
            steps=[
                _deploy("create:mechanical_saw", railway_deployer),
                _deploy("tfmg:electric_motor", railway_deployer),
                _deploy("create:precision_mechanism", railway_deployer),
                _deploy("tfmg:steel_mechanism", railway_deployer),
                _deploy("tfmg:heavy_plate", railway_deployer),
                _press(railway_press),
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator": _sequence(
            comment=(
                "Assemble the electrolysis cell from its Mekanism core, TFMG "
                "electrodes, chemical vessel, transformer, and controller."
            ),
            input_item="mekanism:steel_casing",
            output="mekanism:electrolytic_separator",
            steps=[
                _deploy("tfmg:steel_chemical_vat", industrial_deployer),
                _deploy("mekanism:electrolytic_core", industrial_deployer),
                _deploy("tfmg:copper_electrode", industrial_deployer),
                _deploy("tfmg:zinc_electrode", industrial_deployer),
                _deploy("tfmg:transformer", industrial_deployer),
                _deploy("mekanism:basic_control_circuit", industrial_deployer),
                _press(industrial_press),
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer": _sequence(
            comment=(
                "Build the oxidizer as a fan-driven, pumped TFMG process vessel "
                "with local chemical storage and controlled power buffering."
            ),
            input_item="mekanism:steel_casing",
            output="mekanism:chemical_oxidizer",
            steps=[
                _deploy("tfmg:steel_chemical_vat", industrial_deployer),
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("create:encased_fan", industrial_deployer),
                _deploy("create:mechanical_pump", industrial_deployer),
                _deploy("tfmg:capacitor_item", industrial_deployer),
                _deploy("mekanism:basic_control_circuit", industrial_deployer),
                _press(industrial_press),
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/chemical_infuser": _sequence(
            comment=(
                "Join two independent chemical reservoirs through twin pumps and "
                "a transformer-powered TFMG mixing vessel."
            ),
            input_item="mekanism:steel_casing",
            output="mekanism:chemical_infuser",
            steps=[
                _deploy("tfmg:steel_chemical_vat", industrial_deployer),
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("create:mechanical_pump", industrial_deployer),
                _deploy("create:mechanical_pump", industrial_deployer),
                _deploy("tfmg:steel_pipe", industrial_deployer),
                _deploy("tfmg:transformer", industrial_deployer),
                _deploy("mekanism:basic_control_circuit", industrial_deployer),
                _press(industrial_press),
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber": _sequence(
            comment=(
                "Convert an enrichment chamber into a true three-phase reactor "
                "with separate fluid, chemical, and pressure hardware."
            ),
            input_item="mekanism:enrichment_chamber",
            output="mekanism:pressurized_reaction_chamber",
            steps=[
                _deploy("tfmg:steel_chemical_vat", industrial_deployer),
                _deploy("mekanism:dynamic_tank", industrial_deployer),
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("mekanism:basic_fluid_tank", industrial_deployer),
                _deploy("create:mechanical_pump", industrial_deployer),
                _deploy("tfmg:transformer", industrial_deployer),
                _deploy("mekanism:advanced_control_circuit", industrial_deployer),
                _press(industrial_press),
            ],
        ),
    }
    for recipe_id, body in replacements.items():
        _replace(data, recipe_id, body)


def _redesign_nuclear_process_machines(data: dict[str, Any]) -> None:
    industrial_deployer = "createcasing:industrial_iron_deployer"
    industrial_press = "createcasing:industrial_iron_press"
    radiance_deployer = "createcasing:refined_radiance_deployer"
    radiance_press = "createcasing:refined_radiance_press"

    replacements: dict[str, Recipe] = {
        "industrial_colonies:mekanism_nuclear/purification_chamber": _sequence(
            comment=(
                "Upgrade a fresh enrichment chamber with an oxygen reservoir, "
                "osmium wetted surface, circulation fan, and metered controller."
            ),
            input_item="mekanism:enrichment_chamber",
            output="mekanism:purification_chamber",
            steps=[
                _deploy("mekanism:ingot_osmium", industrial_deployer),
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("create:encased_fan", industrial_deployer),
                _deploy("tfmg:steel_pipe", industrial_deployer),
                _deploy("mekanism:advanced_control_circuit", industrial_deployer),
                _press(industrial_press),
            ],
        ),
        "industrial_colonies:mekanism_nuclear/chemical_injection_chamber": _sequence(
            comment=(
                "Convert a purification chamber into a chemically sealed metering "
                "line with its own reservoir, pump, and elite controller."
            ),
            input_item="mekanism:purification_chamber",
            output="mekanism:chemical_injection_chamber",
            steps=[
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("tfmg:steel_pipe", industrial_deployer),
                _deploy("create:mechanical_pump", industrial_deployer),
                _deploy("mekanism:elite_control_circuit", industrial_deployer),
                _deploy("tfmg:plastic_sheet", industrial_deployer),
                _press(industrial_press),
            ],
        ),
        "industrial_colonies:mekanism_nuclear/chemical_dissolution_chamber": _sequence(
            comment=(
                "Enclose a TFMG acid vessel with dual chemical feeds, an isolated "
                "pump, polymer liner, and ultimate process control."
            ),
            input_item="tfmg:steel_chemical_vat",
            output="mekanism:chemical_dissolution_chamber",
            steps=[
                _deploy("mekanism:steel_casing", industrial_deployer),
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("create:mechanical_pump", industrial_deployer),
                _deploy("tfmg:steel_pipe", industrial_deployer),
                _deploy("mekanism:hdpe_sheet", industrial_deployer),
                _deploy("mekanism:ultimate_control_circuit", industrial_deployer),
                _press(industrial_press),
            ],
        ),
        "industrial_colonies:mekanism_nuclear/chemical_washer": _sequence(
            comment=(
                "Build the slurry washer around separate fluid and chemical "
                "reservoirs feeding a pumped TFMG wash vessel."
            ),
            input_item="tfmg:steel_fluid_tank",
            output="mekanism:chemical_washer",
            steps=[
                _deploy("mekanism:steel_casing", industrial_deployer),
                _deploy("mekanism:basic_chemical_tank", industrial_deployer),
                _deploy("tfmg:steel_chemical_vat", industrial_deployer),
                _deploy("create:mechanical_pump", industrial_deployer),
                _deploy("tfmg:steel_pipe", industrial_deployer),
                _deploy("mekanism:ultimate_control_circuit", industrial_deployer),
                _press(industrial_press),
            ],
        ),
        "industrial_colonies:mekanism_nuclear/isotopic_centrifuge": _sequence(
            comment=(
                "Convert the proven TFMG centrifuge into a gas isotope separator "
                "with a real rotor, magnetic bearing shell, titanium-alloy restraint, "
                "and isolated high-speed controls."
            ),
            input_item="tfmg:centrifuge",
            output="mekanism:isotopic_centrifuge",
            steps=[
                _deploy("tfmg:rotor", radiance_deployer),
                _deploy("tfmg:laminated_magnetic_alloy_block", radiance_deployer),
                _deploy("rocketnautics:titanium_alloy_sheet", radiance_deployer),
                _deploy("mekanism:basic_chemical_tank", radiance_deployer),
                _deploy("mekanism:ultimate_control_circuit", radiance_deployer),
                _deploy("tfmg:transformer", radiance_deployer),
                _press(radiance_press),
            ],
        ),
        "industrial_colonies:mekanism_nuclear/radioactive_waste_barrel_batch": {
            "type": "mechanical_crafting",
            "comment": (
                "Fold lead shielding, steel shell plates, and service pipes into a "
                "practical two-barrel waste-handling batch."
            ),
            "pattern": ["SLS", "P P", "SLS"],
            "key": {
                "S": "#c:plates/steel",
                "L": "#c:plates/lead",
                "P": "tfmg:steel_pipe",
            },
            "output": "2x mekanism:radioactive_waste_barrel",
        },
    }
    for recipe_id, body in replacements.items():
        _replace(data, recipe_id, body)


def _redesign_nuclear_structures(data: dict[str, Any]) -> None:
    _replace(
        data,
        "industrial_colonies:bigreactors/basic_reactor/casing",
        {
            "type": "mechanical_crafting",
            "comment": (
                "Fabricate eight graphite-lined reactor wall panels as a literal "
                "steel-and-firebrick shell, without electronics in every segment."
            ),
            "pattern": ["SSSSS", "SFFFS", "SFGFS", "SFFFS", "SSSSS"],
            "key": {
                "S": "#c:plates/steel",
                "F": "tfmg:fireproof_bricks",
                "G": "#c:ingots/graphite",
            },
            "output": "8x bigreactors:basic_reactorcasing",
        },
    )
    _replace(
        data,
        "industrial_colonies:bigreactors/reinforced_reactor/casing",
        {
            "type": "mechanical_crafting",
            "comment": (
                "Upgrade eight basic wall panels with lead shielding, refined-"
                "obsidian liner, and one central Blutonium progress gate."
            ),
            "pattern": ["BBLBB", "LRRRL", "LRXRL", "LRRRL", "BBLBB"],
            "key": {
                "B": "bigreactors:basic_reactorcasing",
                "L": "#c:plates/lead",
                "R": "mekanism:ingot_refined_obsidian",
                "X": "bigreactors:blutonium_ingot",
            },
            "output": "8x bigreactors:reinforced_reactorcasing",
        },
    )
    _replace(
        data,
        "industrial_colonies:mekanism_nuclear/sps_casing_batch",
        {
            "type": "mechanical_crafting",
            "comment": (
                "Build four SPS wall segments from heavy shell, polymer insulation, "
                "lead shielding, and a single embedded polonium progress gate."
            ),
            "pattern": ["HHHHH", "HPLPH", "HLXLH", "HPLPH", "HHHHH"],
            "key": {
                "H": "tfmg:heavy_plate",
                "P": "mekanism:hdpe_sheet",
                "L": "#c:plates/lead",
                "X": "mekanism:pellet_polonium",
            },
            "output": "4x mekanism:sps_casing",
        },
    )
    _replace(
        data,
        "industrial_colonies:mekanism_nuclear/supercharged_coil",
        _sequence(
            comment=(
                "Turn a TFMG large coil into the SPS injector by adding magnetic "
                "containment, a laser emitter, structural SPS shell, and isolated "
                "polonium power conditioning."
            ),
            input_item="tfmg:large_coil",
            output="mekanism:supercharged_coil",
            steps=[
                _deploy(
                    "tfmg:laminated_magnetic_alloy_block",
                    "createcasing:refined_radiance_deployer",
                ),
                _deploy("mekanism:laser", "createcasing:refined_radiance_deployer"),
                _deploy("mekanism:sps_casing", "createcasing:refined_radiance_deployer"),
                _deploy("tfmg:transformer", "createcasing:refined_radiance_deployer"),
                _deploy(
                    "mekanism:pellet_polonium",
                    "createcasing:refined_radiance_deployer",
                ),
                _deploy("tfmg:capacitor_item", "createcasing:refined_radiance_deployer"),
                _press("createcasing:refined_radiance_press"),
            ],
        ),
    )


def apply(data: dict[str, Any]) -> None:
    """Apply this recipe wave to ``data`` in place.

    Reapplying the transform produces the same dictionary.  Recipes not present
    in the supplied seed are intentionally ignored, which keeps the module safe
    for reduced audit fixtures and avoids inventing owners for absent content.
    """

    _redesign_pre_nuclear_machines(data)
    _redesign_nuclear_process_machines(data)
    _redesign_nuclear_structures(data)

