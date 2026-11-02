#!/usr/bin/env python3
"""Reviewed redesigns for recipes the player explicitly rejected.

This pass is deliberately small and family-oriented.  It must not turn a
rejection into approval; changing the design fingerprint lets the review
reconciliation layer return the card to Pending for another player review.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"

PROCESSOR_REDESIGN_IDS = frozenset(
    {
        "industrial_colonies:ae2/printed_logic_processor",
        "industrial_colonies:ae2/printed_calculation_processor",
        "industrial_colonies:ae2/printed_engineering_processor",
        "industrial_colonies:ae2/logic_processor",
        "industrial_colonies:ae2/calculation_processor",
        "industrial_colonies:ae2/engineering_processor",
        "industrial_colonies:electronics/stress_processor",
        "industrial_colonies:electronics/advanced_stress_processor",
    }
)

INDUCTION_TIERS = ("basic", "advanced", "elite", "ultimate")
INDUCTION_CELL_IDS = {
    tier: f"industrial_colonies:mekanism/induction/{tier}_cell"
    for tier in INDUCTION_TIERS
}
INDUCTION_PROVIDER_IDS = {
    tier: f"industrial_colonies:mekanism/induction/{tier}_provider"
    for tier in INDUCTION_TIERS
}
INDUCTION_REDESIGN_IDS = frozenset(
    {*INDUCTION_CELL_IDS.values(), *INDUCTION_PROVIDER_IDS.values()}
)
INDUCTION_OUTPUTS = {
    **{
        recipe_id: f"mekanism:{tier}_induction_cell"
        for tier, recipe_id in INDUCTION_CELL_IDS.items()
    },
    **{
        recipe_id: f"mekanism:{tier}_induction_provider"
        for tier, recipe_id in INDUCTION_PROVIDER_IDS.items()
    },
}
INDUCTION_REMOVALS = {
    **{
        recipe_id: [f"mekanism:induction/cell/{tier}"]
        for tier, recipe_id in INDUCTION_CELL_IDS.items()
    },
    **{
        recipe_id: [f"mekanism:induction/provider/{tier}"]
        for tier, recipe_id in INDUCTION_PROVIDER_IDS.items()
    },
}
TIER_CIRCUITS = {
    tier: f"mekanism:{tier}_control_circuit" for tier in INDUCTION_TIERS
}
TIER_CUBES = {tier: f"mekanism:{tier}_energy_cube" for tier in INDUCTION_TIERS}
PROVIDER_CONDUCTORS = {
    "basic": "mekanism:basic_universal_cable",
    "advanced": "mekanism:advanced_universal_cable",
    "elite": "mekanism:elite_universal_cable",
    "ultimate": "electroenergetics:heavily_insulated_wire",
}

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


def _index(data: dict[str, Any]) -> dict[str, int]:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed seed must contain a recipes list")
    result: dict[str, int] = {}
    for index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict) or not isinstance(recipe.get("id"), str):
            raise TypeError("managed recipes must be objects with string IDs")
        recipe_id = recipe["id"]
        if recipe_id in result:
            raise ValueError(f"duplicate managed recipe ID: {recipe_id}")
        result[recipe_id] = index
    return result


def _replace(data: dict[str, Any], recipe_id: str, process: Recipe) -> None:
    indexes = _index(data)
    if recipe_id not in indexes:
        raise KeyError(f"expected rejected recipe is missing: {recipe_id}")
    recipe = data["recipes"][indexes[recipe_id]]
    for field in _PROCESS_FIELDS:
        recipe.pop(field, None)
    recipe.update(deepcopy(process))


def _deploy(ingredient: str) -> Recipe:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": BRASS_DEPLOYER,
    }


def _press() -> Recipe:
    return {"op": "pressing", "machine": BRASS_PRESS}


def _printed(
    *,
    comment: str,
    material: str,
    press: str,
    additions: list[Any],
    output: str,
) -> Recipe:
    return {
        "type": "compacting",
        "comment": comment,
        "inputs": [material, press, *additions],
        "machine": BRASS_PRESS,
        "heat": "none",
        "output": f"2x {output}",
        "returned_tool": press,
        "exclusive_output": True,
    }


def _processor(
    *,
    comment: str,
    transitional: str,
    ingredients: list[str],
    output: str,
) -> Recipe:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": "tfmg:coated_circuit_board",
        "transitional": transitional,
        "steps": [*(_deploy(item) for item in ingredients), _press()],
        "loops": 1,
        "output": output,
        "exclusive_output": True,
    }


def _mechanical(
    *,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
) -> Recipe:
    return {
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "exclusive_output": True,
    }


def _redesign_induction_ladder(data: dict[str, Any]) -> None:
    """Give rejected Induction parts distinct 5x5 electrical assemblies."""

    designs = {
        INDUCTION_CELL_IDS["basic"]: _mechanical(
            comment=(
                "Build the first matrix battery as a steel-framed lithium stack: three "
                "Energy Tablet bus bars feed an infused-alloy casing around the induction "
                "core, Basic Cube, magnetic backplate, and Basic control circuit."
            ),
            pattern=[" FCF ", "LTTTL", "FAIAF", " LBL ", " FMF "],
            key={
                "F": "tfmg:steel_frame",
                "C": "mekanism:basic_control_circuit",
                "L": "tfmg:lithium_charge",
                "T": "mekanism:energy_tablet",
                "A": "mekanism:alloy_infused",
                "I": "mekanism:induction_casing",
                "B": "mekanism:basic_energy_cube",
                "M": "tfmg:magnetic_alloy_sheet",
            },
            output="mekanism:basic_induction_cell",
        ),
        INDUCTION_PROVIDER_IDS["basic"]: _mechanical(
            comment=(
                "Lay out a steel-framed Basic power substation: parallel Basic cable rails "
                "join external connectors through paired cable hubs, an induction core, "
                "Basic Cube, transformer, and Basic control circuit."
            ),
            pattern=[" FCF ", " UUU ", "EHIHE", " UBU ", " FTF "],
            key={
                "F": "tfmg:steel_frame",
                "C": "mekanism:basic_control_circuit",
                "U": "mekanism:basic_universal_cable",
                "E": "electroenergetics:connector",
                "H": "tfmg:steel_cable_hub",
                "I": "mekanism:induction_casing",
                "B": "mekanism:basic_energy_cube",
                "T": "tfmg:transformer",
            },
            output="mekanism:basic_induction_provider",
        ),
        INDUCTION_CELL_IDS["advanced"]: _mechanical(
            comment=(
                "Refit the complete Basic Cell inside a steel service frame with an "
                "Advanced Cube, four fresh lithium banks, a three-capacitor buffer, "
                "reinforced-alloy rails, magnetic laminations, and Advanced control."
            ),
            pattern=[" FCF ", " LQL ", "PRBRP", " LPL ", " FMF "],
            key={
                "F": "tfmg:steel_frame",
                "C": "mekanism:advanced_control_circuit",
                "L": "tfmg:lithium_charge",
                "Q": "mekanism:advanced_energy_cube",
                "P": "tfmg:capacitor_item",
                "R": "mekanism:alloy_reinforced",
                "B": "mekanism:basic_induction_cell",
                "M": "tfmg:laminated_magnetic_alloy_block",
            },
            output="mekanism:advanced_induction_cell",
        ),
        INDUCTION_PROVIDER_IDS["advanced"]: _mechanical(
            comment=(
                "Refit the complete Basic Provider as a reinforced Advanced bus: twin "
                "connector/hub terminals meet Advanced cable rails around its Advanced "
                "Cube, large regulating coil, steel frame, and Advanced controller."
            ),
            pattern=[" FCF ", " UUU ", "EHBHE", "RUQUR", " FOF "],
            key={
                "F": "tfmg:steel_frame",
                "C": "mekanism:advanced_control_circuit",
                "U": "mekanism:advanced_universal_cable",
                "E": "electroenergetics:connector",
                "H": "tfmg:steel_cable_hub",
                "B": "mekanism:basic_induction_provider",
                "R": "mekanism:alloy_reinforced",
                "Q": "mekanism:advanced_energy_cube",
                "O": "tfmg:large_coil",
            },
            output="mekanism:advanced_induction_provider",
        ),
        INDUCTION_CELL_IDS["elite"]: _mechanical(
            comment=(
                "Rebuild the complete Advanced Cell as an insulated Elite battery: HDPE "
                "separators isolate paired capacitor banks, four lithium charges, an "
                "atomic-alloy rail, Elite Cube, magnetic core, and Elite controller."
            ),
            pattern=[" FCF ", " LQL ", "HPBPH", " LAL ", " FMF "],
            key={
                "F": "tfmg:steel_frame",
                "C": "mekanism:elite_control_circuit",
                "L": "tfmg:lithium_charge",
                "Q": "mekanism:elite_energy_cube",
                "H": "mekanism:hdpe_sheet",
                "P": "tfmg:capacitor_item",
                "B": "mekanism:advanced_induction_cell",
                "A": "mekanism:alloy_atomic",
                "M": "tfmg:laminated_magnetic_alloy_block",
            },
            output="mekanism:elite_induction_cell",
        ),
        INDUCTION_PROVIDER_IDS["elite"]: _mechanical(
            comment=(
                "Turn the complete Advanced Provider into an Elite metered switchyard: "
                "Elite cable rails pass current transformers, voltage regulation, and a "
                "high-voltage isolator around the Elite Cube and atomic-alloy bus."
            ),
            pattern=[" FCF ", " TUT ", "VABAS", " UQU ", " FMF "],
            key={
                "F": "tfmg:steel_frame",
                "C": "mekanism:elite_control_circuit",
                "T": "electroenergetics:current_transformer",
                "U": "mekanism:elite_universal_cable",
                "V": "electroenergetics:voltage_regulator",
                "A": "mekanism:alloy_atomic",
                "B": "mekanism:advanced_induction_provider",
                "S": "electroenergetics:high_voltage_switch",
                "Q": "mekanism:elite_energy_cube",
                "M": "tfmg:laminated_magnetic_alloy_block",
            },
            output="mekanism:elite_induction_provider",
        ),
        INDUCTION_CELL_IDS["ultimate"]: _mechanical(
            comment=(
                "Assemble the complete Elite Cell into an Ultimate high-voltage battery: "
                "four lithium banks and tablet links alternate with four HV capacitors, "
                "atomic reinforcement, an Ultimate Cube, magnetic core, and controller."
            ),
            pattern=[" FCF ", "LHQHL", "ATBTA", "LHAHL", " FMF "],
            key={
                "F": "tfmg:steel_frame",
                "C": "mekanism:ultimate_control_circuit",
                "L": "tfmg:lithium_charge",
                "H": "electroenergetics:high_voltage_capacitor",
                "Q": "mekanism:ultimate_energy_cube",
                "A": "mekanism:alloy_atomic",
                "T": "mekanism:energy_tablet",
                "B": "mekanism:elite_induction_cell",
                "M": "tfmg:laminated_magnetic_alloy_block",
            },
            output="mekanism:ultimate_induction_cell",
        ),
        INDUCTION_PROVIDER_IDS["ultimate"]: _mechanical(
            comment=(
                "Complete the Elite Provider as an Ultimate protected substation: a "
                "five-wire high-current spine crosses HV capacitance, atomic buswork, "
                "SF6 interruption, the Ultimate Cube, and a large stabilizing coil."
            ),
            pattern=[" FCF ", " WWW ", "HABAS", " WQW ", " FOF "],
            key={
                "F": "tfmg:steel_frame",
                "C": "mekanism:ultimate_control_circuit",
                "W": "electroenergetics:heavily_insulated_wire",
                "H": "electroenergetics:high_voltage_capacitor",
                "A": "mekanism:alloy_atomic",
                "B": "mekanism:elite_induction_provider",
                "S": "electroenergetics:sulfur_hexafluoride_breaker",
                "Q": "mekanism:ultimate_energy_cube",
                "O": "tfmg:large_coil",
            },
            output="mekanism:ultimate_induction_provider",
        ),
    }
    for recipe_id, process in designs.items():
        _replace(data, recipe_id, process)


def apply(data: dict[str, Any]) -> None:
    """Apply the processor and Induction rejected-redesign cohorts in memory."""

    printed = {
        "industrial_colonies:ae2/printed_logic_processor": _printed(
            comment=(
                "Laminate two gold logic dies with plastic dielectric, an N-type "
                "switching layer, redstone traces, and copper interconnect under the "
                "reusable Logic mask"
            ),
            material="2x create:golden_sheet",
            press="ae2:logic_processor_press",
            additions=[
                "2x tfmg:plastic_sheet",
                "tfmg:n_semiconductor",
                "2x minecraft:redstone",
                "2x tfmg:copper_wire",
            ],
            output="ae2:printed_logic_processor",
        ),
        "industrial_colonies:ae2/printed_calculation_processor": _printed(
            comment=(
                "Laminate two Certus calculation dies with plastic dielectric, a "
                "P-type switching layer, fluix timing dust, and a TFMG capacitor "
                "under the reusable Calculation mask"
            ),
            material="2x ae2:certus_quartz_crystal",
            press="ae2:calculation_processor_press",
            additions=[
                "2x tfmg:plastic_sheet",
                "tfmg:p_semiconductor",
                {"kind": "ITEM_TAG", "id": "c:dusts/fluix", "count": 2},
                "tfmg:capacitor_item",
            ],
            output="ae2:printed_calculation_processor",
        ),
        "industrial_colonies:ae2/printed_engineering_processor": _printed(
            comment=(
                "Laminate two diamond engineering dies with plastic dielectric, a "
                "complementary semiconductor pair, and magnetic shielding under the "
                "reusable Engineering mask"
            ),
            material="2x minecraft:diamond",
            press="ae2:engineering_processor_press",
            additions=[
                "2x tfmg:plastic_sheet",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "2x tfmg:magnetic_alloy_sheet",
            ],
            output="ae2:printed_engineering_processor",
        ),
    }
    for recipe_id, process in printed.items():
        _replace(data, recipe_id, process)

    processors = {
        "industrial_colonies:ae2/logic_processor": _processor(
            comment=(
                "Populate a coated TFMG board with the printed logic and silicon "
                "dies, complementary semiconductors, discrete transistor/capacitor "
                "logic, plastic insulation, and redstone traces before final packaging"
            ),
            transitional="createappliedkinetics:incomplete_logic_processor",
            ingredients=[
                "ae2:printed_logic_processor",
                "ae2:printed_silicon",
                "tfmg:plastic_sheet",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "minecraft:redstone",
            ],
            output="ae2:logic_processor",
        ),
        "industrial_colonies:ae2/calculation_processor": _processor(
            comment=(
                "Populate a coated TFMG board with calculation and silicon dies, "
                "complementary semiconductors, discrete timing electronics, plastic "
                "insulation, fluix clock material, and redstone before packaging"
            ),
            transitional="createappliedkinetics:incomplete_calculation_processor",
            ingredients=[
                "ae2:printed_calculation_processor",
                "ae2:printed_silicon",
                "tfmg:plastic_sheet",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:capacitor_item",
                "tfmg:transistor_item",
                "#c:dusts/fluix",
                "minecraft:redstone",
            ],
            output="ae2:calculation_processor",
        ),
        "industrial_colonies:ae2/engineering_processor": _processor(
            comment=(
                "Populate a coated TFMG board with engineering and silicon dies, a "
                "complementary semiconductor stage, discrete power electronics, plastic "
                "insulation, nickel conductors, and magnetic shielding before packaging"
            ),
            transitional="createappliedkinetics:incomplete_engineering_processor",
            ingredients=[
                "ae2:printed_engineering_processor",
                "ae2:printed_silicon",
                "tfmg:plastic_sheet",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "tfmg:nickel_sheet",
                "tfmg:magnetic_alloy_sheet",
            ],
            output="ae2:engineering_processor",
        ),
        "industrial_colonies:electronics/stress_processor": _processor(
            comment=(
                "Populate a coated board with the stress circuit substrate, silicon die, "
                "complementary semiconductors, discrete TFMG electronics, insulated "
                "copper interconnect, and cinder stress medium before packaging"
            ),
            transitional="appliedcreate:stress_circuit_board",
            ingredients=[
                "appliedcreate:stress_circuit_board",
                "ae2:printed_silicon",
                "tfmg:plastic_sheet",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
                "create:cinder_flour",
            ],
            output="appliedcreate:stress_processor",
        ),
        "industrial_colonies:electronics/advanced_stress_processor": _processor(
            comment=(
                "Package the prior stress and logic processors on a coated board with a "
                "second complementary semiconductor stage, plastic isolation, stored "
                "charge, magnetic shielding, and calibrated cinder stress medium"
            ),
            transitional="appliedcreate:advanced_stress_circuit_board",
            ingredients=[
                "appliedcreate:advanced_stress_circuit_board",
                "appliedcreate:stress_processor",
                "ae2:logic_processor",
                "tfmg:plastic_sheet",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:capacitor_item",
                "tfmg:magnetic_alloy_sheet",
                "create:cinder_flour",
            ],
            output="appliedcreate:advanced_stress_processor",
        ),
    }
    for recipe_id, process in processors.items():
        _replace(data, recipe_id, process)

    _redesign_induction_ladder(data)

    audit(data)


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    missing = sorted(PROCESSOR_REDESIGN_IDS.difference(indexes))
    missing_induction = sorted(INDUCTION_REDESIGN_IDS.difference(indexes))
    errors: list[str] = []
    if missing:
        errors.append(f"missing processor redesigns: {missing}")
    if missing_induction:
        errors.append(f"missing induction redesigns: {missing_induction}")

    recipes = data.get("recipes", [])
    for recipe_id in sorted(PROCESSOR_REDESIGN_IDS.intersection(indexes)):
        recipe = recipes[indexes[recipe_id]]
        serialized = repr(recipe)
        if "tfmg:plastic_sheet" not in serialized:
            errors.append(f"{recipe_id} lacks plastic insulation")
        if not ({"tfmg:n_semiconductor", "tfmg:p_semiconductor"} & set(_ingredients(recipe))):
            errors.append(f"{recipe_id} lacks a semiconductor")
        if recipe_id.startswith("industrial_colonies:ae2/printed_"):
            if recipe.get("type") != "compacting" or recipe.get("machine") != BRASS_PRESS:
                errors.append(f"{recipe_id} is not Brass compacting")
            if not recipe.get("returned_tool"):
                errors.append(f"{recipe_id} does not return its processor mask")
            if not str(recipe.get("output", "")).startswith("2x "):
                errors.append(f"{recipe_id} is not balanced as a two-die batch")
        else:
            if recipe.get("type") != "sequenced_assembly":
                errors.append(f"{recipe_id} is not sequenced assembly")
            if recipe.get("input") != "tfmg:coated_circuit_board":
                errors.append(f"{recipe_id} does not begin on a coated TFMG board")
            machines = {
                step.get("machine")
                for step in recipe.get("steps", [])
                if isinstance(step, dict) and step.get("machine")
            }
            if machines != {BRASS_DEPLOYER, BRASS_PRESS}:
                errors.append(f"{recipe_id} escapes the Brass electronics line")
            if len(recipe.get("steps", [])) < 9:
                errors.append(f"{recipe_id} remains too cheap")

    patterns: set[tuple[str, ...]] = set()
    boms: set[frozenset[str]] = set()
    for tier in INDUCTION_TIERS:
        for family, recipe_id in (
            ("cell", INDUCTION_CELL_IDS[tier]),
            ("provider", INDUCTION_PROVIDER_IDS[tier]),
        ):
            if recipe_id not in indexes:
                continue
            recipe = recipes[indexes[recipe_id]]
            pattern = recipe.get("pattern")
            key = recipe.get("key")
            if recipe.get("type") != "mechanical_crafting":
                errors.append(f"{recipe_id} is not mechanical crafting")
            if (
                not isinstance(pattern, list)
                or len(pattern) != 5
                or any(not isinstance(row, str) or len(row) != 5 for row in pattern)
            ):
                errors.append(f"{recipe_id} is not an exact 5x5 layout")
                continue
            pattern_tuple = tuple(pattern)
            if pattern_tuple in patterns:
                errors.append(f"{recipe_id} reuses another induction layout")
            patterns.add(pattern_tuple)
            perimeter = (
                list(pattern[0])
                + list(pattern[-1])
                + [row[0] for row in pattern[1:-1]]
                + [row[-1] for row in pattern[1:-1]]
            )
            if all(character != " " for character in perimeter):
                errors.append(f"{recipe_id} falls back to a filled perimeter ring")
            if not isinstance(key, dict) or not key:
                errors.append(f"{recipe_id} has no mechanical-crafting key")
                continue
            used = {character for row in pattern for character in row if character != " "}
            if used != set(key):
                errors.append(f"{recipe_id} pattern/key symbols do not match")
            if len(key) < 8:
                errors.append(f"{recipe_id} lacks a meaningful component BOM")
            ingredients = {str(value).split()[-1] for value in key.values()}
            bom = frozenset(ingredients)
            if bom in boms:
                errors.append(f"{recipe_id} reuses another induction BOM")
            boms.add(bom)
            if "tfmg:steel_frame" not in ingredients:
                errors.append(f"{recipe_id} lacks the canonical TFMG steel frame")
            if "mekanism:steel_casing" in ingredients:
                errors.append(f"{recipe_id} revives the retired Mekanism steel casing")
            if TIER_CIRCUITS[tier] not in ingredients:
                errors.append(f"{recipe_id} lacks {tier} control")
            if TIER_CUBES[tier] not in ingredients:
                errors.append(f"{recipe_id} lacks its {tier} energy cube")
            if family == "cell":
                if "tfmg:lithium_charge" not in ingredients:
                    errors.append(f"{recipe_id} lacks lithium battery media")
                if tier == "basic":
                    predecessor = "mekanism:induction_casing"
                else:
                    predecessor = f"mekanism:{INDUCTION_TIERS[INDUCTION_TIERS.index(tier) - 1]}_induction_cell"
            else:
                if PROVIDER_CONDUCTORS[tier] not in ingredients:
                    errors.append(f"{recipe_id} lacks its tier-appropriate power conductor")
                if tier == "basic":
                    predecessor = "mekanism:induction_casing"
                else:
                    predecessor = f"mekanism:{INDUCTION_TIERS[INDUCTION_TIERS.index(tier) - 1]}_induction_provider"
            if predecessor not in ingredients:
                errors.append(f"{recipe_id} does not consume its prior ladder component")
            if recipe.get("output") != INDUCTION_OUTPUTS[recipe_id]:
                errors.append(f"{recipe_id} changed its exact output")
            if recipe.get("remove") != INDUCTION_REMOVALS[recipe_id]:
                errors.append(f"{recipe_id} changed its stock-recipe removal")
            if recipe.get("exclusive_output") is not True:
                errors.append(f"{recipe_id} is not exclusive")
            if any(field in recipe for field in ("input", "transitional", "steps", "loops", "machine")):
                errors.append(f"{recipe_id} retains stale sequenced-assembly fields")

    if errors:
        raise ValueError("Rejected recipe redesign audit failed: " + " | ".join(errors))
    return {
        "status": "PASS",
        "redesigned": len(PROCESSOR_REDESIGN_IDS | INDUCTION_REDESIGN_IDS),
        "processor_redesigns": len(PROCESSOR_REDESIGN_IDS),
        "induction_redesigns": len(INDUCTION_REDESIGN_IDS),
        "printed_batches": 3,
        "sequenced_processors": 5,
        "mechanical_induction_parts": len(INDUCTION_REDESIGN_IDS),
    }


def _ingredients(recipe: Recipe) -> list[str]:
    values: list[str] = []
    for value in recipe.get("inputs", []):
        if isinstance(value, str):
            values.append(value.split()[-1])
    for step in recipe.get("steps", []):
        if isinstance(step, dict) and isinstance(step.get("ingredient"), str):
            values.append(step["ingredient"].split()[-1])
    return values
