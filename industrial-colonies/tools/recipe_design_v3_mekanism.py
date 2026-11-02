#!/usr/bin/env python3
"""Mekanism recipe-design pass v3.

This pass is intentionally limited to Mekanism.  It corrects machine-building
environments, makes factory installers cumulative manufactured assemblies,
retire direct Factory recipes, and gives the Energy Cube ladder progressively
denser internal battery construction.

``apply`` mutates only the supplied seed dictionary.  The module performs no
file I/O, build, deployment, or live KubeJSGen changes and is idempotent.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping
import re


Recipe = dict[str, Any]


INDUSTRIAL_DEPLOYER = "createcasing:industrial_iron_deployer"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"
WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"
RADIANCE_PRESS = "createcasing:refined_radiance_press"


FACTORY_PROCESSES = (
    "combining",
    "compressing",
    "crushing",
    "enriching",
    "infusing",
    "injecting",
    "purifying",
    "sawing",
    "smelting",
)
FACTORY_TIERS = ("basic", "advanced", "elite", "ultimate")
FACTORY_STOCK_IDS = frozenset(
    f"mekanism:factory/{tier}/{process}"
    for tier in FACTORY_TIERS
    for process in FACTORY_PROCESSES
)
FACTORY_OUTPUTS = frozenset(
    f"mekanism:{tier}_{process}_factory"
    for tier in FACTORY_TIERS
    for process in FACTORY_PROCESSES
)

LATE_TRANSMISSION_IDS = (
    "industrial_colonies:mekanism/transmission/elite_logistical_transporter",
    "industrial_colonies:mekanism/transmission/elite_mechanical_pipe",
    "industrial_colonies:mekanism/transmission/elite_pressurized_tube",
    "industrial_colonies:mekanism/transmission/elite_thermodynamic_conductor",
    "industrial_colonies:mekanism/transmission/elite_universal_cable",
    "industrial_colonies:mekanism/transmission/ultimate_logistical_transporter",
    "industrial_colonies:mekanism/transmission/ultimate_mechanical_pipe",
    "industrial_colonies:mekanism/transmission/ultimate_pressurized_tube",
    "industrial_colonies:mekanism/transmission/ultimate_thermodynamic_conductor",
    "industrial_colonies:mekanism/transmission/ultimate_universal_cable",
)

# The later review pass retires these exact redundant transmission routes in
# favor of Create/TFMG/Electro Energetics infrastructure.  Keeping the proof
# here makes this earlier v3 pass idempotent after those cards are gone.
REVIEW_RETIRED_LATE_TRANSMISSION = {
    "industrial_colonies:mekanism/transmission/elite_universal_cable": (
        "mekanism:transmitter/universal_cable/elite",
        "mekanism:elite_universal_cable",
    ),
    "industrial_colonies:mekanism/transmission/ultimate_mechanical_pipe": (
        "mekanism:transmitter/mechanical_pipe/ultimate",
        "mekanism:ultimate_mechanical_pipe",
    ),
    "industrial_colonies:mekanism/transmission/ultimate_universal_cable": (
        "mekanism:transmitter/universal_cable/ultimate",
        "mekanism:ultimate_universal_cable",
    ),
}


USER_OWNED_REFERENCE_OUTPUTS = frozenset(
    {
        "mekanism:metallurgic_infuser",
        "mekanism:rotary_condensentrator",
        "mekanism:energy_tablet",
    }
)


# TFMG owns the pack's structural steel vocabulary.  Mekanism's plain steel
# casing is intentionally not a parallel craftable frame, including in cards
# that were approved before this policy was adopted.
CANONICAL_STEEL_FRAME = "tfmg:steel_frame"
RETIRED_STEEL_CASING = "mekanism:steel_casing"
RETIRED_STEEL_CASING_RECIPE_ID = "industrial_colonies:mekanism/steel_casing"
RETIRED_PROCESS_MACHINE_RECIPES = {
    "industrial_colonies:mekanism_pre_nuclear/energized_smelter": (
        "mekanism:energized_smelter"
    ),
    "industrial_colonies:mekanism_pre_nuclear/formulaic_assemblicator": (
        "mekanism:formulaic_assemblicator"
    ),
    "industrial_colonies:mekanism_pre_nuclear/digital_miner": "mekanism:digital_miner",
}
RETIRED_PROCESS_MACHINE_OUTPUTS = frozenset(RETIRED_PROCESS_MACHINE_RECIPES.values())

# Later review passes may own additional intentional 5x5 Mekanism structures.
# Keep this explicit so the v3 anti-template guard still fails closed for every
# other large grid instead of treating all downstream 5x5 recipes as trusted.
REVIEWED_EXTERNAL_FIVE_BY_FIVE_IDS = frozenset(
    {
        *(
            f"industrial_colonies:mekanism/induction/{tier}_{kind}"
            for tier in ("basic", "advanced", "elite", "ultimate")
            for kind in ("cell", "provider")
        ),
        # Explicitly reviewed in the final rejected-recipe pass.  These are
        # physical machine/tool silhouettes, not the template rings guarded
        # against below.
        "industrial_colonies:mekanism_nuclear/isotopic_centrifuge",
        "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer",
        "industrial_colonies:mekanism_tools/armored_free_runners",
    }
)


_INPUT_MATERIAL_FIELDS = (
    "base",
    "ingredient",
    "input",
    "transitional",
    "inputs",
    "ingredients",
    "held",
    "input1",
    "input2",
    "left",
    "right",
    "gas",
    "infusion",
)
_COUNTED_STACK = re.compile(r"^(\s*\d+x\s+)([^\s]+)(\s*)$")


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
    "output",
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


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed seed field {field!r} must be a list")
    return value


def _recipe_index(data: dict[str, Any]) -> dict[str, int]:
    recipes = _require_list(data, "recipes")
    result: dict[str, int] = {}
    for index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict) or not isinstance(recipe.get("id"), str):
            raise TypeError("managed recipe entries must be objects with string IDs")
        recipe_id = recipe["id"]
        if recipe_id in result:
            raise ValueError(f"duplicate managed recipe id before Mekanism v3: {recipe_id}")
        result[recipe_id] = index
    return result


def _replace(data: dict[str, Any], recipe_id: str, body: Recipe) -> None:
    indexes = _recipe_index(data)
    if recipe_id not in indexes:
        raise KeyError(f"expected Mekanism recipe is missing: {recipe_id}")
    recipe = _require_list(data, "recipes")[indexes[recipe_id]]
    for field in _PROCESS_FIELDS:
        recipe.pop(field, None)
    recipe.update(deepcopy(body))


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    indexes = _recipe_index(data)
    recipes = _require_list(data, "recipes")
    if recipe["id"] in indexes:
        recipes[indexes[recipe["id"]]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def _deploy(ingredient: str, machine: str = INDUSTRIAL_DEPLOYER) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str = INDUSTRIAL_PRESS) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    comment: str,
    input_item: str,
    output: str,
    ingredients: Iterable[str],
    deployer: str = INDUSTRIAL_DEPLOYER,
    press: str = INDUSTRIAL_PRESS,
    loops: int = 1,
) -> Recipe:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": loops,
        "steps": [*(_deploy(item, deployer) for item in ingredients), _press(press)],
        "exclusive_output": True,
    }


def _new_sequence(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    stock_id: str,
    depends_on: Iterable[str],
    **process: Any,
) -> Recipe:
    recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "remove": [stock_id],
        "depends_on": list(depends_on),
        **_sequence(**process),
    }
    return recipe


def _normal_process_machines(data: dict[str, Any]) -> None:
    """Build every covered process machine on the Industrial Iron line."""

    replacements: dict[str, Recipe] = {
        "industrial_colonies:mekanism/combiner": _sequence(
            comment=(
                "Build the Combiner as an opposed compression chamber with a real "
                "platen, material depot, powered steel drive, advanced controller, "
                "and replaceable heavy closure."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:combiner",
            ingredients=[
                "create:mechanical_press",
                "create:depot",
                "tfmg:steel_mechanism",
                "tfmg:electric_motor",
                "mekanism:advanced_control_circuit",
                "2x mekanism:alloy_infused",
                "2x tfmg:heavy_plate",
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber": _sequence(
            comment=(
                "Install a TFMG rotor, milling head, precision eccentric drive, and "
                "controlled infused-alloy vibration bed on the TFMG steel frame."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:enrichment_chamber",
            ingredients=[
                "tfmg:rotor",
                "create:millstone",
                "create:precision_mechanism",
                "tfmg:steel_mechanism",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
                "2x mekanism:alloy_infused",
                "2x tfmg:heavy_plate",
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/osmium_compressor": _sequence(
            comment=(
                "Fit a pumped chemical pressure vessel, transformer, motorized platen, "
                "osmium wetted face, and serviceable controller onto a TFMG steel frame."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:osmium_compressor",
            ingredients=[
                "tfmg:steel_chemical_vat",
                "create:mechanical_pump",
                "tfmg:transformer",
                "create:mechanical_press",
                "tfmg:electric_motor",
                "mekanism:ingot_osmium",
                "mekanism:basic_control_circuit",
                "2x tfmg:heavy_plate",
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/crusher": _sequence(
            comment=(
                "Mount a matched pair of Create crushing wheels around a powered TFMG "
                "drive, then align and close the heavy industrial shell."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:crusher",
            ingredients=[
                "create:crushing_wheel",
                "create:crushing_wheel",
                "tfmg:electric_motor",
                "tfmg:steel_mechanism",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
                "2x mekanism:alloy_infused",
                "2x tfmg:heavy_plate",
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/precision_sawmill": _sequence(
            comment=(
                "Align a powered saw carriage, precision feed mechanism, and guarded "
                "steel drive before the Industrial Iron press squares the enclosure."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:precision_sawmill",
            ingredients=[
                "create:mechanical_saw",
                "tfmg:electric_motor",
                "create:precision_mechanism",
                "tfmg:steel_mechanism",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
                "mekanism:alloy_infused",
                "2x tfmg:heavy_plate",
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator": _sequence(
            comment=(
                "Assemble a true electrolysis cell from opposed TFMG electrodes, a "
                "pumped chemical vessel, transformer, separator core, and controller."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:electrolytic_separator",
            ingredients=[
                "mekanism:electrolytic_core",
                "tfmg:steel_chemical_vat",
                "tfmg:copper_electrode",
                "tfmg:zinc_electrode",
                "create:mechanical_pump",
                "tfmg:transformer",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer": _sequence(
            comment=(
                "Build a fan-driven oxidation vessel with a dedicated chemical tank, "
                "pumped steel manifold, capacitor buffer, and metered control board."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:chemical_oxidizer",
            ingredients=[
                "tfmg:steel_chemical_vat",
                "mekanism:basic_chemical_tank",
                "create:encased_fan",
                "create:mechanical_pump",
                "tfmg:steel_pipe",
                "tfmg:capacitor_item",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/chemical_infuser": _sequence(
            comment=(
                "Join two independent chemical feeds through dual pumps and a TFMG "
                "mixing vessel, then condition the line with a transformer and control."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:chemical_infuser",
            ingredients=[
                "tfmg:steel_chemical_vat",
                "2x mekanism:basic_chemical_tank",
                "create:mechanical_pump",
                "create:mechanical_pump",
                "2x tfmg:steel_pipe",
                "tfmg:transformer",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
            ],
        ),
        "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber": _sequence(
            comment=(
                "Convert an enrichment chamber into a three-phase reactor with a TFMG "
                "process vat, separate fluid and chemical reservoirs, pumped manifold, "
                "pressure shell, transformer, and advanced governor."
            ),
            input_item="mekanism:enrichment_chamber",
            output="mekanism:pressurized_reaction_chamber",
            ingredients=[
                CANONICAL_STEEL_FRAME,
                "tfmg:steel_chemical_vat",
                "mekanism:dynamic_tank",
                "mekanism:basic_fluid_tank",
                "mekanism:basic_chemical_tank",
                "create:mechanical_pump",
                "tfmg:steel_pipe",
                "tfmg:transformer",
                "mekanism:advanced_control_circuit",
            ],
        ),
    }
    for recipe_id, body in replacements.items():
        _replace(data, recipe_id, body)

    additions = [
        _new_sequence(
            recipe_id="industrial_colonies:mekanism_pre_nuclear/fuelwood_heater",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=370,
            stock_id="mekanism:fuelwood_heater",
            depends_on=[],
            comment=(
                "Build a forced-draft biomass heater around a Blaze Burner, encased fan, "
                "steel heat channels, thermostatic circuit, and heavy refractory closure."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:fuelwood_heater",
            ingredients=[
                "create:blaze_burner",
                "create:encased_fan",
                "2x tfmg:steel_pipe",
                "tfmg:large_coil",
                "tfmg:resistor",
                "mekanism:basic_control_circuit",
                "2x tfmg:heavy_plate",
            ],
        ),
        _new_sequence(
            recipe_id="industrial_colonies:mekanism_pre_nuclear/modification_station",
            node="CR01 — Modular Machinery",
            phase="Mekanized Industry",
            order=640,
            stock_id="mekanism:modification_station",
            depends_on=[
                "industrial_colonies:mekanism_components/module_base",
            ],
            comment=(
                "Equip a service bench with a module socket, encoded formula interface, "
                "precision tool carriage, energy buffer, and advanced diagnostic logic."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:modification_station",
            ingredients=[
                "mekanism:module_base",
                "mekanism:crafting_formula",
                "create:deployer",
                "create:precision_mechanism",
                "mekanism:energy_tablet",
                "ae2:logic_processor",
                "mekanism:advanced_control_circuit",
                "tfmg:etched_circuit_board",
            ],
        ),
        _new_sequence(
            recipe_id="industrial_colonies:mekanism_pre_nuclear/pigment_extractor",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=650,
            stock_id="mekanism:pigment_extractor",
            depends_on=[
                "industrial_colonies:mekanism_components/basic_chemical_tank",
            ],
            comment=(
                "Combine a milling head, chemical reservoir, pumped extraction vat, and "
                "metered controller into a contained pigment-processing line."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:pigment_extractor",
            ingredients=[
                "create:millstone",
                "mekanism:basic_chemical_tank",
                "tfmg:steel_chemical_vat",
                "create:mechanical_pump",
                "tfmg:steel_pipe",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
                "tfmg:electric_motor",
            ],
        ),
        _new_sequence(
            recipe_id="industrial_colonies:mekanism_pre_nuclear/pigment_mixer",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=660,
            stock_id="mekanism:pigment_mixer",
            depends_on=[
                "industrial_colonies:mekanism_components/basic_chemical_tank",
            ],
            comment=(
                "Feed two pigment reservoirs through separate pumps into a driven mixer, "
                "then add a steel outlet manifold and color-control electronics."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:pigment_mixer",
            ingredients=[
                "2x mekanism:basic_chemical_tank",
                "create:mechanical_mixer",
                "create:mechanical_pump",
                "create:mechanical_pump",
                "2x tfmg:steel_pipe",
                "tfmg:electric_motor",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
            ],
        ),
        _new_sequence(
            recipe_id="industrial_colonies:mekanism_pre_nuclear/painting_machine",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=670,
            stock_id="mekanism:painting_machine",
            depends_on=[
                "industrial_colonies:mekanism_components/basic_chemical_tank",
            ],
            comment=(
                "Install a controlled Deployer head over a pumped pigment reservoir with "
                "a sealed steel manifold, precision feed, and local color controller."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:painting_machine",
            ingredients=[
                "create:deployer",
                "mekanism:basic_chemical_tank",
                "create:mechanical_pump",
                "tfmg:steel_pipe",
                "create:precision_mechanism",
                "tfmg:electric_motor",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
            ],
        ),
        _new_sequence(
            recipe_id="industrial_colonies:planetary/outpost/nutritional_liquifier",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=640,
            stock_id="mekanism:nutritional_liquifier",
            depends_on=[
                "industrial_colonies:mekanism_components/basic_fluid_tank",
            ],
            comment=(
                "Build a sanitary liquefaction cell from a mixer, basin, food-safe fluid "
                "tank, pump, plastic liner, and metered drive controller."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:nutritional_liquifier",
            ingredients=[
                "create:mechanical_mixer",
                "create:basin",
                "mekanism:basic_fluid_tank",
                "create:mechanical_pump",
                "2x tfmg:plastic_sheet",
                "tfmg:electric_motor",
                "mekanism:basic_control_circuit",
                "tfmg:circuit_board",
            ],
        ),
        _new_sequence(
            recipe_id="industrial_colonies:mekanism_pre_nuclear/seismic_vibrator",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=430,
            stock_id="mekanism:seismic_vibrator",
            depends_on=[
                "industrial_colonies:mekanism/advanced_control_circuit",
            ],
            comment=(
                "Build an instrumented vibration table from an eccentric rotor, twin "
                "motors, heavy reaction mass, magnetic suspension, and advanced control."
            ),
            input_item=CANONICAL_STEEL_FRAME,
            output="mekanism:seismic_vibrator",
            ingredients=[
                "tfmg:rotor",
                "2x tfmg:electric_motor",
                "tfmg:laminated_magnetic_alloy_block",
                "4x tfmg:heavy_plate",
                "tfmg:steel_mechanism",
                "mekanism:advanced_control_circuit",
                "ae2:calculation_processor",
                "tfmg:capacitor_item",
            ],
        ),
    ]
    for recipe in additions:
        _upsert(data, recipe)


def _tier_installers(data: dict[str, Any]) -> None:
    """Make the installer ladder cumulative without color-swapped templates."""

    designs = {
        "industrial_colonies:mekanism/tier_installer/basic": _sequence(
            comment=(
                "Build the first factory service card around an Andesite stress processor, "
                "paired TFMG semiconductors, capacitor bank, plastic insulation, basic "
                "Mekanism logic, and infused buswork before the final Industrial Iron press."
            ),
            input_item="tfmg:steel_mechanism",
            output="mekanism:basic_tier_installer",
            ingredients=[
                "appliedcreate:stress_processor",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:capacitor_item",
                "2x tfmg:plastic_sheet",
                "mekanism:basic_control_circuit",
                "mekanism:alloy_infused",
            ],
        ),
        "industrial_colonies:mekanism/tier_installer/advanced": _sequence(
            comment=(
                "Refit the complete Basic Installer with AE logic, a fresh semiconductor "
                "pair, etched backplane, capacitor bank, polymer jacket, osmium spine, "
                "magnetic shielding, and advanced Mekanism control."
            ),
            input_item="mekanism:basic_tier_installer",
            output="mekanism:advanced_tier_installer",
            ingredients=[
                "ae2:logic_processor",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:etched_circuit_board",
                "2x tfmg:capacitor_item",
                "2x tfmg:plastic_sheet",
                "mekanism:advanced_control_circuit",
                "mekanism:ingot_osmium",
                "tfmg:magnetic_alloy_sheet",
            ],
        ),
        "industrial_colonies:mekanism/tier_installer/elite": _sequence(
            comment=(
                "Upgrade the complete Advanced Installer with calculation logic, matched "
                "semiconductors, a four-capacitor power bank, HDPE insulation, lithium "
                "buffering, cobalt reinforcement, and elite reinforced control."
            ),
            input_item="mekanism:advanced_tier_installer",
            output="mekanism:elite_tier_installer",
            ingredients=[
                "ae2:calculation_processor",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "4x tfmg:capacitor_item",
                "2x mekanism:hdpe_sheet",
                "tfmg:lithium_charge",
                "modernfoundry:cobalt_reinforcement",
                "mekanism:elite_control_circuit",
                "2x mekanism:alloy_reinforced",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
        ),
        "industrial_colonies:mekanism/tier_installer/ultimate": _sequence(
            comment=(
                "Complete the Ultimate Installer from the entire Elite card, engineering "
                "logic, matched semiconductors, a high-voltage capacitor bank, redundant "
                "HDPE, refined-obsidian structure, magnetic isolation, and atomic control."
            ),
            input_item="mekanism:elite_tier_installer",
            output="mekanism:ultimate_tier_installer",
            ingredients=[
                "ae2:engineering_processor",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "4x tfmg:capacitor_item",
                "electroenergetics:high_voltage_capacitor",
                "2x mekanism:hdpe_sheet",
                "mekanism:ultimate_control_circuit",
                "mekanism:ingot_refined_obsidian",
                "tfmg:laminated_magnetic_alloy_block",
                "2x mekanism:alloy_atomic",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
        ),
    }
    for recipe_id, body in designs.items():
        _replace(data, recipe_id, body)


def _energy_cubes(data: dict[str, Any]) -> None:
    """Retain the dense-battery ring exception with richer internal packs."""

    designs: dict[str, Recipe] = {
        "industrial_colonies:mekanism/storage/basic_energy_cube": {
            "type": "mechanical_crafting",
            "comment": (
                "Package four lithium charges and two Energy Tablets around the TFMG "
                "accumulator, copper service bus, and Basic Mekanism controller."
            ),
            "pattern": ["LTL", "EGE", "LCL"],
            "key": {
                "L": "tfmg:lithium_charge",
                "T": "tfmg:copper_wire",
                "E": "mekanism:energy_tablet",
                "G": "tfmg:accumulator",
                "C": "mekanism:basic_control_circuit",
            },
            "output": "mekanism:basic_energy_cube",
            "exclusive_output": True,
        },
        "industrial_colonies:mekanism/storage/advanced_energy_cube": {
            "type": "mechanical_crafting",
            "comment": (
                "Build a magnetic-osmium shell around a complete Basic Cube; the inner "
                "3x3 adds lithium reserve, infused buswork, twin tablets, and Advanced control."
            ),
            "pattern": ["MOOOM", "OLALO", "OEBEO", "OLCLO", "MOOOM"],
            "key": {
                "M": "tfmg:magnetic_alloy_sheet",
                "O": "mekanism:ingot_osmium",
                "L": "tfmg:lithium_charge",
                "A": "mekanism:alloy_infused",
                "E": "mekanism:energy_tablet",
                "B": "mekanism:basic_energy_cube",
                "C": "mekanism:advanced_control_circuit",
            },
            "output": "mekanism:advanced_energy_cube",
            "exclusive_output": True,
        },
        "industrial_colonies:mekanism/storage/elite_energy_cube": {
            "type": "mechanical_crafting",
            "comment": (
                "Reinforce a complete Advanced Cube with a cobalt-and-gold shell; its inner "
                "3x3 adds matched semiconductors, lithium, reinforced alloy, and Elite control."
            ),
            "pattern": ["KGGGK", "GLRLG", "GNBPG", "GLCLG", "KGGGK"],
            "key": {
                "K": "modernfoundry:cobalt_reinforcement",
                "G": "create:golden_sheet",
                "L": "tfmg:lithium_charge",
                "R": "mekanism:alloy_reinforced",
                "N": "tfmg:n_semiconductor",
                "B": "mekanism:advanced_energy_cube",
                "P": "tfmg:p_semiconductor",
                "C": "mekanism:elite_control_circuit",
            },
            "output": "mekanism:elite_energy_cube",
            "exclusive_output": True,
        },
        "industrial_colonies:mekanism/storage/ultimate_energy_cube": {
            "type": "mechanical_crafting",
            "comment": (
                "Produce two Ultimate Cubes by enclosing a complete Elite Cube in an "
                "atomic/refined-obsidian shell; the inner 3x3 adds lithium, an SF6 breaker, "
                "TFMG accumulator, Engineering Processor, and Ultimate governor."
            ),
            "pattern": ["ARRRA", "RLHLR", "RQBER", "RLCLR", "ARRRA"],
            "key": {
                "A": "mekanism:alloy_atomic",
                "R": "mekanism:ingot_refined_obsidian",
                "L": "tfmg:lithium_charge",
                "H": "electroenergetics:sulfur_hexafluoride_breaker",
                "Q": "tfmg:accumulator",
                "B": "mekanism:elite_energy_cube",
                "E": "ae2:engineering_processor",
                "C": "mekanism:ultimate_control_circuit",
            },
            "output": "2x mekanism:ultimate_energy_cube",
            "exclusive_output": True,
        },
    }
    for recipe_id, body in designs.items():
        _replace(data, recipe_id, body)


def _rigid_casing_batches(data: dict[str, Any]) -> None:
    """Press repetitive rigid shells in basins instead of drawing 5x5 borders."""

    _replace(
        data,
        "industrial_colonies:mekanism/induction/casing",
        {
            "type": "compacting",
            "comment": (
                "Press eight induction-frame segments from TFMG steel frames and heavy "
                "shell plate, magnetic laminations, insulated high-current wire, and a "
                "shared heavy-machinery spine."
            ),
            "inputs": [
                "4x tfmg:steel_frame",
                "8x tfmg:heavy_plate",
                "4x tfmg:magnetic_alloy_sheet",
                "4x electroenergetics:heavily_insulated_wire",
                "2x tfmg:heavy_machinery_casing",
            ],
            "machine": INDUSTRIAL_PRESS,
            "heat": "none",
            "output": "8x mekanism:induction_casing",
            "exclusive_output": True,
        },
    )
    _replace(
        data,
        "industrial_colonies:mekanism_nuclear/sps_casing_batch",
        {
            "type": "compacting",
            "comment": (
                "Press four SPS containment segments from redundant HDPE and lead barriers, "
                "heavy TFMG shell plate, reactor-derived polonium/plutonium, transformer "
                "conditioning, and engineering-grade field control."
            ),
            "inputs": [
                "4x mekanism:hdpe_sheet",
                "4x tfmg:lead_sheet",
                "6x tfmg:heavy_plate",
                "3x mekanism:pellet_polonium",
                "mekanism:pellet_plutonium",
                "tfmg:transformer",
                "ae2:engineering_processor",
            ],
            "machine": RADIANCE_PRESS,
            "heat": "none",
            "output": "4x mekanism:sps_casing",
            "exclusive_output": True,
        },
    )


def _retarget_late_transmission(data: dict[str, Any]) -> None:
    """Keep Elite/Ultimate transmission fabrication on the later press line."""

    indexes = _recipe_index(data)
    for recipe_id in LATE_TRANSMISSION_IDS:
        if recipe_id not in indexes:
            proof = REVIEW_RETIRED_LATE_TRANSMISSION.get(recipe_id)
            if proof is not None:
                stock_id, output_id = proof
                if (
                    stock_id in data.get("additional_removals", [])
                    and output_id in data.get("exclude_outputs", [])
                ):
                    continue
            raise KeyError(f"late Mekanism transmission recipe is missing: {recipe_id}")
        recipe = data["recipes"][indexes[recipe_id]]
        if recipe.get("type") != "compacting":
            raise ValueError(f"late Mekanism transmission recipe is no longer compacting: {recipe_id}")
        recipe["machine"] = INDUSTRIAL_PRESS


def _output_item(value: Any) -> str | None:
    if isinstance(value, str):
        return re.sub(r"^\d+x\s+", "", value.strip())
    if isinstance(value, Mapping):
        item = value.get("id") or value.get("item")
        return str(item) if isinstance(item, str) else None
    return None


def _recipe_output_items(recipe: Mapping[str, Any]) -> list[str]:
    outputs: list[str] = []
    if output := _output_item(recipe.get("output")):
        outputs.append(output)
    for field in ("results", "outputs"):
        values = recipe.get(field, [])
        if isinstance(values, list):
            for value in values:
                if output := _output_item(value):
                    outputs.append(output)
    return outputs


def _replace_steel_stack(value: Any) -> Any:
    """Replace a steel-casing input stack without touching recipe outputs."""

    if isinstance(value, str):
        match = _COUNTED_STACK.fullmatch(value)
        if match and match.group(2) == RETIRED_STEEL_CASING:
            return f"{match.group(1)}{CANONICAL_STEEL_FRAME}{match.group(3)}"
        return CANONICAL_STEEL_FRAME if value.strip() == RETIRED_STEEL_CASING else value
    if isinstance(value, list):
        for index, entry in enumerate(value):
            value[index] = _replace_steel_stack(entry)
        return value
    if isinstance(value, dict):
        for identity_field in ("id", "item"):
            if value.get(identity_field) == RETIRED_STEEL_CASING:
                value[identity_field] = CANONICAL_STEEL_FRAME
        return value
    return value


def _stack_item_ids(value: Any) -> list[str]:
    """Return exact item identities represented by an input stack value."""

    if isinstance(value, str):
        match = _COUNTED_STACK.fullmatch(value)
        return [match.group(2) if match else value.strip()]
    if isinstance(value, list):
        return [item for entry in value for item in _stack_item_ids(entry)]
    if isinstance(value, Mapping):
        return [
            item
            for field in ("id", "item")
            if isinstance((item := value.get(field)), str)
        ]
    return []


def _canonicalize_steel_frame_consumers(data: dict[str, Any]) -> None:
    """Apply the TFMG-frame policy to every managed consumer and dependency.

    This deliberately has no review-status exemption: an Approved recipe keeps
    its approval metadata and design, but its structural input is canonicalized.
    """

    for recipe in _require_list(data, "recipes"):
        if not isinstance(recipe, dict):
            raise TypeError("managed recipe entries must be objects")
        for field in _INPUT_MATERIAL_FIELDS:
            if field in recipe:
                recipe[field] = _replace_steel_stack(recipe[field])

        key = recipe.get("key")
        if isinstance(key, dict):
            for symbol, value in list(key.items()):
                key[symbol] = _replace_steel_stack(value)

        steps = recipe.get("steps")
        if isinstance(steps, list):
            for step in steps:
                if isinstance(step, dict) and "ingredient" in step:
                    step["ingredient"] = _replace_steel_stack(step["ingredient"])

        dependencies = recipe.get("depends_on")
        if isinstance(dependencies, list):
            recipe["depends_on"] = [
                dependency
                for dependency in dependencies
                if dependency != RETIRED_STEEL_CASING_RECIPE_ID
            ]

    replacements = data.setdefault("ingredient_replacements", {})
    if not isinstance(replacements, dict):
        raise TypeError("managed seed field 'ingredient_replacements' must be an object")
    existing = replacements.get(RETIRED_STEEL_CASING)
    if existing not in (None, CANONICAL_STEEL_FRAME):
        raise ValueError(
            f"conflicting canonical frame replacement for {RETIRED_STEEL_CASING}: {existing}"
        )
    replacements[RETIRED_STEEL_CASING] = CANONICAL_STEEL_FRAME


def _retire_steel_casing(data: dict[str, Any]) -> None:
    """Remove the duplicate managed producer and keep the stock recipe disabled."""

    recipes = _require_list(data, "recipes")
    transferred_removals = {RETIRED_STEEL_CASING}
    kept: list[Recipe] = []
    for recipe in recipes:
        if not isinstance(recipe, dict):
            raise TypeError("managed recipe entries must be objects")
        retired = (
            recipe.get("id") == RETIRED_STEEL_CASING_RECIPE_ID
            or RETIRED_STEEL_CASING in _recipe_output_items(recipe)
        )
        if retired:
            transferred_removals.update(map(str, recipe.get("remove", [])))
        else:
            kept.append(recipe)
    recipes[:] = kept

    additional = _require_list(data, "additional_removals")
    additional[:] = sorted(set(map(str, additional)).union(transferred_removals))

    preserved = _require_list(data, "preserve_recipe_ids")
    preserved[:] = [
        recipe_id for recipe_id in preserved if recipe_id not in transferred_removals
    ]

    excluded = _require_list(data, "exclude_outputs")
    excluded[:] = sorted(set(map(str, excluded)).union({RETIRED_STEEL_CASING}))


def _retire_factories(data: dict[str, Any]) -> None:
    recipes = _require_list(data, "recipes")
    recipes[:] = [
        recipe
        for recipe in recipes
        if not (
            str(recipe.get("id", "")).startswith("industrial_colonies:mekanism/factory/")
            or FACTORY_OUTPUTS.intersection(_recipe_output_items(recipe))
        )
    ]

    additional = _require_list(data, "additional_removals")
    additional[:] = sorted(set(map(str, additional)).union(FACTORY_STOCK_IDS))

    preserved = _require_list(data, "preserve_recipe_ids")
    preserved[:] = [stock for stock in preserved if stock not in FACTORY_STOCK_IDS]

    excluded = _require_list(data, "exclude_outputs")
    excluded[:] = sorted(set(map(str, excluded)).union(FACTORY_OUTPUTS))


def _retire_redundant_process_machines(data: dict[str, Any]) -> None:
    """Retire redundant/forbidden Mekanism machines but keep stock IDs disabled."""

    recipes = _require_list(data, "recipes")
    transferred_removals = set(RETIRED_PROCESS_MACHINE_OUTPUTS)
    kept: list[Recipe] = []
    for recipe in recipes:
        if not isinstance(recipe, dict):
            raise TypeError("managed recipe entries must be objects")
        retired = (
            recipe.get("id") in RETIRED_PROCESS_MACHINE_RECIPES
            or bool(RETIRED_PROCESS_MACHINE_OUTPUTS.intersection(_recipe_output_items(recipe)))
        )
        if retired:
            transferred_removals.update(map(str, recipe.get("remove", [])))
        else:
            kept.append(recipe)
    recipes[:] = kept

    additional = _require_list(data, "additional_removals")
    additional[:] = sorted(set(map(str, additional)).union(transferred_removals))

    preserved = _require_list(data, "preserve_recipe_ids")
    preserved[:] = [
        recipe_id for recipe_id in preserved if recipe_id not in transferred_removals
    ]

    excluded = _require_list(data, "exclude_outputs")
    excluded[:] = sorted(
        set(map(str, excluded)).union(RETIRED_PROCESS_MACHINE_OUTPUTS)
    )


def _claim_managed_stock_removals(data: dict[str, Any]) -> None:
    """Prevent exact Mek replacements from also appearing as broad removals."""

    owned_recipe_ids = (
        set(PROCESS_MACHINE_IDS)
        | set(INSTALLER_IDS)
        | set(ENERGY_CUBE_IDS)
        | set(RIGID_CASING_IDS)
    )
    claimed: set[str] = set()
    for recipe in _require_list(data, "recipes"):
        if recipe.get("id") in owned_recipe_ids:
            claimed.update(map(str, recipe.get("remove", [])))
    additional = _require_list(data, "additional_removals")
    additional[:] = [stock for stock in additional if stock not in claimed]
    preserved = _require_list(data, "preserve_recipe_ids")
    preserved[:] = [stock for stock in preserved if stock not in claimed]


PROCESS_MACHINE_IDS = frozenset(
    {
        "industrial_colonies:mekanism/combiner",
        "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber",
        "industrial_colonies:mekanism_pre_nuclear/osmium_compressor",
        "industrial_colonies:mekanism_pre_nuclear/crusher",
        "industrial_colonies:mekanism_pre_nuclear/precision_sawmill",
        "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator",
        "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer",
        "industrial_colonies:mekanism_pre_nuclear/chemical_infuser",
        "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber",
        "industrial_colonies:mekanism_pre_nuclear/fuelwood_heater",
        "industrial_colonies:mekanism_pre_nuclear/modification_station",
        "industrial_colonies:mekanism_pre_nuclear/pigment_extractor",
        "industrial_colonies:mekanism_pre_nuclear/pigment_mixer",
        "industrial_colonies:mekanism_pre_nuclear/painting_machine",
        "industrial_colonies:planetary/outpost/nutritional_liquifier",
        "industrial_colonies:mekanism_pre_nuclear/seismic_vibrator",
    }
)


INSTALLER_IDS = (
    "industrial_colonies:mekanism/tier_installer/basic",
    "industrial_colonies:mekanism/tier_installer/advanced",
    "industrial_colonies:mekanism/tier_installer/elite",
    "industrial_colonies:mekanism/tier_installer/ultimate",
)


ENERGY_CUBE_IDS = (
    "industrial_colonies:mekanism/storage/basic_energy_cube",
    "industrial_colonies:mekanism/storage/advanced_energy_cube",
    "industrial_colonies:mekanism/storage/elite_energy_cube",
    "industrial_colonies:mekanism/storage/ultimate_energy_cube",
)


RIGID_CASING_IDS = (
    "industrial_colonies:mekanism/induction/casing",
    "industrial_colonies:mekanism_nuclear/sps_casing_batch",
)


def audit(data: dict[str, Any]) -> dict[str, Any]:
    """Return a strict, JSON-serializable validation report for this pass."""

    recipes = _require_list(data, "recipes")
    indexes = _recipe_index(data)
    errors: list[str] = []

    outputs: dict[str, list[str]] = {}
    for recipe in recipes:
        for output in _recipe_output_items(recipe):
            outputs.setdefault(output, []).append(str(recipe["id"]))
    duplicate_outputs = {
        output: ids for output, ids in outputs.items() if len(ids) > 1
    }
    if duplicate_outputs:
        errors.append(f"duplicate managed outputs: {duplicate_outputs}")

    if RETIRED_STEEL_CASING_RECIPE_ID in indexes:
        errors.append("retired Mekanism steel-casing producer remains managed")
    if RETIRED_STEEL_CASING in outputs:
        errors.append("Mekanism steel casing remains a managed output")
    if RETIRED_STEEL_CASING not in set(map(str, data.get("additional_removals", []))):
        errors.append("stock Mekanism steel-casing recipe is not disabled")
    if RETIRED_STEEL_CASING not in set(map(str, data.get("exclude_outputs", []))):
        errors.append("Mekanism steel casing is not excluded from managed coverage")
    if data.get("ingredient_replacements", {}).get(RETIRED_STEEL_CASING) != CANONICAL_STEEL_FRAME:
        errors.append("Mekanism steel casing is not mapped to the canonical TFMG frame")

    additional_removals = set(map(str, data.get("additional_removals", [])))
    excluded_outputs = set(map(str, data.get("exclude_outputs", [])))
    for recipe_id, output in RETIRED_PROCESS_MACHINE_RECIPES.items():
        if recipe_id in indexes:
            errors.append(f"retired Mekanism process-machine producer remains: {recipe_id}")
        if output in outputs:
            errors.append(f"retired Mekanism process-machine output remains managed: {output}")
        if output not in additional_removals:
            errors.append(f"retired Mekanism stock recipe is not disabled: {output}")
        if output not in excluded_outputs:
            errors.append(f"retired Mekanism output is not excluded from coverage: {output}")

    stale_frame_consumers: list[tuple[str, str]] = []
    stale_frame_dependencies: list[str] = []
    for recipe in recipes:
        recipe_id = str(recipe["id"])
        for field in _INPUT_MATERIAL_FIELDS:
            if RETIRED_STEEL_CASING in _stack_item_ids(recipe.get(field)):
                stale_frame_consumers.append((recipe_id, field))
        key = recipe.get("key")
        if isinstance(key, Mapping):
            for symbol, value in key.items():
                if RETIRED_STEEL_CASING in _stack_item_ids(value):
                    stale_frame_consumers.append((recipe_id, f"key.{symbol}"))
        steps = recipe.get("steps")
        if isinstance(steps, list):
            for index, step in enumerate(steps):
                if (
                    isinstance(step, Mapping)
                    and RETIRED_STEEL_CASING in _stack_item_ids(step.get("ingredient"))
                ):
                    stale_frame_consumers.append((recipe_id, f"steps[{index}].ingredient"))
        if RETIRED_STEEL_CASING_RECIPE_ID in recipe.get("depends_on", []):
            stale_frame_dependencies.append(recipe_id)
    if stale_frame_consumers:
        errors.append(f"managed recipes still consume Mekanism steel casing: {stale_frame_consumers}")
    if stale_frame_dependencies:
        errors.append(
            "managed recipes still depend on the retired steel-casing producer: "
            f"{sorted(stale_frame_dependencies)}"
        )

    missing_process = sorted(PROCESS_MACHINE_IDS.difference(indexes))
    if missing_process:
        errors.append(f"missing Mekanism process-machine recipes: {missing_process}")
    for recipe_id in sorted(PROCESS_MACHINE_IDS.intersection(indexes)):
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not a sequenced assembly")
            continue
        machines = {
            step.get("machine")
            for step in recipe.get("steps", [])
            if isinstance(step, dict) and step.get("machine")
        }
        expected = {INDUSTRIAL_DEPLOYER, INDUSTRIAL_PRESS}
        if machines != expected:
            errors.append(
                f"{recipe_id} does not exclusively use Industrial Iron: {sorted(machines)}"
            )
        if len(recipe.get("steps", [])) < 7:
            errors.append(f"{recipe_id} has an underdeveloped machine sequence")

    installer_ingredient_sets: list[frozenset[str]] = []
    processors = (
        "appliedcreate:stress_processor",
        "ae2:logic_processor",
        "ae2:calculation_processor",
        "ae2:engineering_processor",
    )
    previous_inputs = (
        "tfmg:steel_mechanism",
        "mekanism:basic_tier_installer",
        "mekanism:advanced_tier_installer",
        "mekanism:elite_tier_installer",
    )
    for recipe_id, processor, prior in zip(INSTALLER_IDS, processors, previous_inputs):
        if recipe_id not in indexes:
            errors.append(f"missing installer recipe: {recipe_id}")
            continue
        recipe = recipes[indexes[recipe_id]]
        installer_machines = {
            step.get("machine")
            for step in recipe.get("steps", [])
            if isinstance(step, dict) and step.get("machine")
        }
        if installer_machines != {INDUSTRIAL_DEPLOYER, INDUSTRIAL_PRESS}:
            errors.append(f"{recipe_id} regressed from the Industrial Iron line")
        ingredients = frozenset(
            re.sub(r"^\d+x\s+", "", str(step.get("ingredient", "")))
            for step in recipe.get("steps", [])
            if isinstance(step, dict) and step.get("op") == "deploying"
        )
        installer_ingredient_sets.append(ingredients)
        required = {
            processor,
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            "tfmg:capacitor_item",
        }
        if not required.issubset(ingredients):
            errors.append(
                f"{recipe_id} lacks processor/semiconductor/capacitor identity: "
                f"{sorted(required.difference(ingredients))}"
            )
        if not ({"tfmg:plastic_sheet", "mekanism:hdpe_sheet"} & ingredients):
            errors.append(f"{recipe_id} lacks plastic insulation")
        if not any(item.startswith("mekanism:") and "control_circuit" in item for item in ingredients):
            errors.append(f"{recipe_id} lacks a Mekanism control circuit")
        if recipe.get("input") != prior:
            errors.append(f"{recipe_id} is not cumulative from {prior}")
        # The reviewed Basic Installer intentionally stops after seven deployed
        # components and the final press. Later cumulative cards retain their
        # longer nine-plus-step assemblies.
        minimum_steps = 8 if recipe_id == INSTALLER_IDS[0] else 9
        if len(recipe.get("steps", [])) < minimum_steps:
            errors.append(
                f"{recipe_id} has fewer than {minimum_steps} manufactured steps"
            )
    if len(installer_ingredient_sets) != 4 or len(set(installer_ingredient_sets)) != 4:
        errors.append("installer sequences are not four unique BOMs")

    for recipe_id in ENERGY_CUBE_IDS:
        if recipe_id not in indexes:
            errors.append(f"missing Energy Cube recipe: {recipe_id}")
    if all(recipe_id in indexes for recipe_id in ENERGY_CUBE_IDS):
        advanced = recipes[indexes[ENERGY_CUBE_IDS[1]]]
        elite = recipes[indexes[ENERGY_CUBE_IDS[2]]]
        ultimate = recipes[indexes[ENERGY_CUBE_IDS[3]]]
        if [len(advanced.get("pattern", [])), len(elite.get("pattern", [])), len(ultimate.get("pattern", []))] != [5, 5, 5]:
            errors.append("Advanced/Elite/Ultimate Energy Cubes are not full 5x5 packs")
        if ultimate.get("output") != "2x mekanism:ultimate_energy_cube":
            errors.append("Ultimate Energy Cube is not balanced to an output of two")

    expected_casing_presses = {
        RIGID_CASING_IDS[0]: INDUSTRIAL_PRESS,
        RIGID_CASING_IDS[1]: RADIANCE_PRESS,
    }
    for recipe_id, expected_machine in expected_casing_presses.items():
        if recipe_id not in indexes:
            errors.append(f"missing rigid casing batch: {recipe_id}")
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "compacting" or recipe.get("machine") != expected_machine:
            errors.append(
                f"{recipe_id} is not compacted on its intended casing line"
            )

    for recipe_id in LATE_TRANSMISSION_IDS:
        if recipe_id not in indexes:
            proof = REVIEW_RETIRED_LATE_TRANSMISSION.get(recipe_id)
            if proof is not None:
                stock_id, output_id = proof
                if (
                    stock_id in data.get("additional_removals", [])
                    and output_id in data.get("exclude_outputs", [])
                ):
                    continue
            errors.append(f"missing late transmission recipe: {recipe_id}")
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "compacting" or recipe.get("machine") != INDUSTRIAL_PRESS:
            errors.append(f"{recipe_id} regressed from the Industrial Iron line")

    allowed_five_by_five = set(ENERGY_CUBE_IDS[1:]) | set(
        REVIEWED_EXTERNAL_FIVE_BY_FIVE_IDS
    )
    for recipe in recipes:
        output_items = _recipe_output_items(recipe)
        if not any(item.startswith("mekanism:") for item in output_items):
            continue
        pattern = recipe.get("pattern", [])
        if (
            recipe.get("type") == "mechanical_crafting"
            and isinstance(pattern, list)
            and len(pattern) == 5
            and recipe["id"] not in allowed_five_by_five
            and recipe["id"] != "industrial_colonies:world_loading/dimensional_stabilizer"
        ):
            errors.append(f"unreviewed Mekanism 5x5 grid remains: {recipe['id']}")

    managed_factory_outputs = sorted(FACTORY_OUTPUTS.intersection(outputs))
    if managed_factory_outputs:
        errors.append(f"direct Factory outputs remain managed: {managed_factory_outputs}")
    missing_factory_removals = sorted(
        FACTORY_STOCK_IDS.difference(map(str, data.get("additional_removals", [])))
    )
    if missing_factory_removals:
        errors.append(f"Factory stock recipes remain enabled: {missing_factory_removals}")

    touched_user_owned = sorted(USER_OWNED_REFERENCE_OUTPUTS.intersection(outputs))
    if touched_user_owned:
        errors.append(f"v3 overwrote user-owned reference cards: {touched_user_owned}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "managed_recipe_count": len(recipes),
        "process_machine_sequences": len(PROCESS_MACHINE_IDS),
        "installer_sequences": len(INSTALLER_IDS),
        "energy_cube_recipes": len(ENERGY_CUBE_IDS),
        "rigid_casing_compacting_batches": len(RIGID_CASING_IDS),
        "factory_stock_recipes_retired": len(FACTORY_STOCK_IDS),
        "factory_outputs_excluded": len(FACTORY_OUTPUTS),
        "user_owned_reference_outputs_preserved": sorted(USER_OWNED_REFERENCE_OUTPUTS),
    }


def apply(data: dict[str, Any]) -> None:
    """Apply the Mekanism v3 redesign and fail immediately on policy drift."""

    _normal_process_machines(data)
    _retire_redundant_process_machines(data)
    _tier_installers(data)
    _energy_cubes(data)
    _rigid_casing_batches(data)
    _retarget_late_transmission(data)
    _retire_steel_casing(data)
    _canonicalize_steel_frame_consumers(data)
    _claim_managed_stock_removals(data)
    _retire_factories(data)
    report = audit(data)
    if report["status"] != "PASS":
        raise AssertionError("Mekanism v3 validation failed: " + "; ".join(report["errors"]))
