#!/usr/bin/env python3
"""Resolve the reviewed digital-routing and basic-transmission rejections.

This source-only design pass deliberately stays separate from the builder and
the live pack.  Six AE2/MEGA routes become component-rich electronics
sequences, three useful Mekanism transmitters move to casing-appropriate
compacting, and three redundant transmitter routes are retired while their
exact stock recipes remain disabled.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


Recipe = dict[str, Any]

COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
WEATHERED_PRESS = "createcasing:weathered_iron_press"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"

REJECTION_CONTRACTS = {
    "industrial_colonies:ae2_high_energy/export_bus": {
        "note": "a little more complex please",
        "cardSha256": "sha256:2265187f059ee36d1572fb343bcbff3c9c2c6a6af268949aae9762bba9f3d34f",
    },
    "industrial_colonies:ae2_high_energy/me_p2p_tunnel": {
        "note": "more complex",
        "cardSha256": "sha256:1c47624de39a79e90d7f26f61e9bb6abbf181f6c3cc6fd64a32e122272b11fd5",
    },
    "industrial_colonies:ae2_high_energy/mega_crafting_unit": {
        "note": "too cheap",
        "cardSha256": "sha256:5017447d38f60cc19e3436cf603e819cc97dd9165a9b2c49a64e8b4fb8dedc5d",
    },
    "industrial_colonies:digital_core/import_bus": {
        "note": "eh its a direct link for the ME system make it more complex",
        "cardSha256": "sha256:eb07e6938376bea6ccdee90cf43f351ff63e7aca1b2487d0d60c910d428fe34c",
    },
    "industrial_colonies:digital_core/interface": {
        "note": "refer to impot bus entry",
        "cardSha256": "sha256:a302c10b303eedf4fbf33205ae5e05c7c1ddd5863278ee9100c82714335ede4e",
    },
    "industrial_colonies:digital_core/pattern_provider": {
        "note": "correct machine but way to simple",
        "cardSha256": "sha256:ab392c5829881998b937ef0e58f9a06bdf9c3da541a2bed53ca3633d3e2def10",
    },
    "industrial_colonies:mekanism/transmission/advanced_mechanical_pipe": {
        "note": "create has its own pipes",
        "cardSha256": "sha256:c3f4b228362458108512d75fa7f8a2d9e283b341ed2c6b64521cc4adfa0e30c6",
    },
    "industrial_colonies:mekanism/transmission/advanced_universal_cable": {
        "note": "should be disabled for this cable type",
        "cardSha256": "sha256:8413138643480029ef6e11e7013f9479fad04654fc152437365bc07b62ac9243",
    },
    "industrial_colonies:mekanism/transmission/elite_universal_cable": {
        "note": "should be disabled",
        "cardSha256": "sha256:669f2b846bbb74dbfef9032ec3ddca0af39619230a5c0b7ed88b99665590ae5e",
    },
    "industrial_colonies:mekanism/transmission/ultimate_universal_cable": {
        "note": "should be disabled",
        "cardSha256": "sha256:b180696df955d1593555301db16d1b57436446eebaf51de68a5d0cd2e9c6b0b2",
    },
    "industrial_colonies:mekanism/transmission/basic_logistical_transporter": {
        "note": "love it but should use copper or rustede compacting",
        "cardSha256": "sha256:75bf2f28ce2ac9a81466ff591dbaebd6fade54808a4713e6dec144ae3465700d",
    },
    "industrial_colonies:mekanism/transmission/basic_mechanical_pipe": {
        "note": (
            "love it but should require rusted compacting. Honestly just remove this "
            "because pipes from create do this already."
        ),
        "cardSha256": "sha256:aa2134f1754420a0d71ccbe055712793e47856d6df1710a2e780cf64b98b8dfb",
    },
    "industrial_colonies:mekanism/transmission/basic_pressurized_tube": {
        "note": "love it but should require rusted steel machines",
        "cardSha256": "sha256:30adccfcccbfabd32cc74d5a8cce6a7e4d295796ddfbecc901a80f0a91a1d06a",
    },
    "industrial_colonies:mekanism/transmission/basic_universal_cable": {
        "note": "love it but should use copper compacting",
        "cardSha256": "sha256:d2d8b6b7657673f802c538fbca414373ee50cffcc221c2c0096ccb11f6f796b2",
    },
    "industrial_colonies:mekanism/transmission/ultimate_mechanical_pipe": {
        "note": "create has this feature",
        "cardSha256": "sha256:6122a63893f4e4fe22fa833868a56647e093c8d751fd5208d163a010a043e412",
    },
}

REDESIGNED_IDS = frozenset(
    {
        "industrial_colonies:ae2_high_energy/export_bus",
        "industrial_colonies:ae2_high_energy/me_p2p_tunnel",
        "industrial_colonies:ae2_high_energy/mega_crafting_unit",
        "industrial_colonies:digital_core/import_bus",
        "industrial_colonies:digital_core/interface",
        "industrial_colonies:digital_core/pattern_provider",
        "industrial_colonies:mekanism/transmission/basic_logistical_transporter",
        "industrial_colonies:mekanism/transmission/basic_pressurized_tube",
        "industrial_colonies:mekanism/transmission/basic_universal_cable",
    }
)

# managed recipe ID -> (exact stock recipe ID, disabled output ID)
RETIREMENTS = {
    "industrial_colonies:mekanism/transmission/basic_mechanical_pipe": (
        "mekanism:transmitter/mechanical_pipe/basic",
        "mekanism:basic_mechanical_pipe",
    ),
    "industrial_colonies:mekanism/transmission/advanced_mechanical_pipe": (
        "mekanism:transmitter/mechanical_pipe/advanced",
        "mekanism:advanced_mechanical_pipe",
    ),
    "industrial_colonies:mekanism/transmission/advanced_universal_cable": (
        "mekanism:transmitter/universal_cable/advanced",
        "mekanism:advanced_universal_cable",
    ),
    "industrial_colonies:mekanism/transmission/elite_universal_cable": (
        "mekanism:transmitter/universal_cable/elite",
        "mekanism:elite_universal_cable",
    ),
    "industrial_colonies:mekanism/transmission/ultimate_universal_cable": (
        "mekanism:transmitter/universal_cable/ultimate",
        "mekanism:ultimate_universal_cable",
    ),
    "industrial_colonies:mekanism/transmission/ultimate_mechanical_pipe": (
        "mekanism:transmitter/mechanical_pipe/ultimate",
        "mekanism:ultimate_mechanical_pipe",
    ),
}

RETIRED_IDS = frozenset(RETIREMENTS)
PRIMARY_RETIRED_IDS = frozenset(
    {
        "industrial_colonies:mekanism/transmission/basic_mechanical_pipe",
        "industrial_colonies:mekanism/transmission/advanced_mechanical_pipe",
        "industrial_colonies:mekanism/transmission/advanced_universal_cable",
    }
)
SUPPORT_RETIRED_IDS = RETIRED_IDS - PRIMARY_RETIRED_IDS
REVIEW_DECISION_IDS = REDESIGNED_IDS | RETIRED_IDS

ELITE_MECHANICAL_PIPE_ID = (
    "industrial_colonies:mekanism/transmission/elite_mechanical_pipe"
)

SUPPORT_ITEM_REPLACEMENTS = {
    "industrial_colonies:mekanism/induction/advanced_provider": {
        "mekanism:advanced_universal_cable": "electroenergetics:heavily_insulated_wire"
    },
    "industrial_colonies:mekanism/induction/elite_provider": {
        "mekanism:elite_universal_cable": "electroenergetics:heavily_insulated_wire"
    },
    "industrial_colonies:mekanism/induction/port": {
        "mekanism:ultimate_universal_cable": "electroenergetics:heavily_insulated_wire"
    },
    "industrial_colonies:planetary/outpost/solar_panel": {
        "mekanism:ultimate_universal_cable": "tfmg:aluminum_wire"
    },
    "industrial_colonies:planetary/outpost/gravity_normalizer": {
        "mekanism:ultimate_universal_cable": "electroenergetics:heavily_insulated_wire"
    },
    "industrial_colonies:planetary/venus/netherite_space_suit": {
        "mekanism:ultimate_universal_cable": "electroenergetics:insulated_wire"
    },
    "industrial_colonies:planetary/venus/netherite_space_pants": {
        "mekanism:ultimate_universal_cable": "electroenergetics:insulated_wire"
    },
    "industrial_colonies:mekanism_utility/ultimate_fluid_tank": {
        "mekanism:ultimate_mechanical_pipe": "mekanism:elite_mechanical_pipe"
    },
}

SUPPORT_REDESIGN_IDS = frozenset(
    {ELITE_MECHANICAL_PIPE_ID, *SUPPORT_ITEM_REPLACEMENTS}
)

SUPPORT_COMMENTS = {
    "industrial_colonies:mekanism/induction/advanced_provider": (
        "Refit the complete Basic Provider as a reinforced switchyard bus: protected "
        "Electro Energetics rails meet its steel hub, large regulating coil, Advanced "
        "Cube, structural frame, and Advanced control circuit"
    ),
    "industrial_colonies:mekanism/induction/elite_provider": (
        "Turn the Advanced Provider into an Elite metered switchyard where protected "
        "Electro Energetics rails cross current transformers, voltage regulation, and "
        "a high-voltage isolator around the Elite Cube and atomic-alloy bus"
    ),
    "industrial_colonies:mekanism/induction/port": (
        "Build a matched induction-port pair around protected high-current wire, an "
        "ultimate controller, voltage regulation, and a high-voltage capacitor bank"
    ),
    "industrial_colonies:planetary/outpost/solar_panel": (
        "Fabricate four outpost panels as three photovoltaic rows in a Desh lattice "
        "over a transformer bus, aluminum-wire terminals, and an engineering regulator"
    ),
    "industrial_colonies:planetary/outpost/gravity_normalizer": (
        "Form twin Desh field arches around electromagnetic coils and an Ultimate "
        "Energy Cube while protected grid wire, transformers, and a complete etched "
        "control rack close the field circuit"
    ),
    "industrial_colonies:planetary/venus/netherite_space_suit": (
        "Install the complete oxygen train in a Netherite chestplate, route its compact "
        "insulated suit-power lead and pressure services, then close the Desh-Ostrum shell"
    ),
    "industrial_colonies:planetary/venus/netherite_space_pants": (
        "Line Netherite leggings with Desh, form the doubled Ostrum pressure shell, and "
        "install paired gas cells, a service valve, and an insulated suit-power lead"
    ),
    "industrial_colonies:mekanism_utility/ultimate_fluid_tank": (
        "Qualify the Elite vessel for ultimate throughput with its proven Elite liquid "
        "manifold, redundant HDPE lining, atomic locks, and a TFMG industrial header"
    ),
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
    "exclusive_output",
}


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed seed field {field!r} must be a list")
    return value


def _index(data: dict[str, Any]) -> dict[str, int]:
    recipes = _require_list(data, "recipes")
    result: dict[str, int] = {}
    for index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict) or not isinstance(recipe.get("id"), str):
            raise TypeError("managed recipes must be objects with string IDs")
        recipe_id = recipe["id"]
        if recipe_id in result:
            raise ValueError(f"duplicate managed recipe ID: {recipe_id}")
        result[recipe_id] = index
    return result


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    comment: str,
    input_item: str,
    ingredients: list[str],
    output: Any,
    deployer: str,
    press: str,
) -> Recipe:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "steps": [*(_deploy(item, deployer) for item in ingredients), _press(press)],
        "loops": 1,
        "output": output,
        "exclusive_output": True,
    }


def _compacting(
    *,
    comment: str,
    inputs: list[str],
    output_id: str,
    machine: str,
) -> Recipe:
    return {
        "type": "compacting",
        "comment": comment,
        "inputs": inputs,
        "machine": machine,
        "output": {"kind": "ITEM", "id": output_id, "count": 8},
        "exclusive_output": True,
    }


def _designs() -> dict[str, Recipe]:
    return {
        "industrial_colonies:digital_core/import_bus": _sequence(
            comment=(
                "Build the inbound ME actuator around a piston, then install its "
                "annihilation core, route logic, etched TFMG controller, transistor "
                "switch, copper data lead, fluix network tail, and plastic isolation"
            ),
            input_item="minecraft:piston",
            ingredients=[
                "ae2:annihilation_core",
                "ae2:logic_processor",
                "tfmg:etched_circuit_board",
                "tfmg:transistor_item",
                "tfmg:copper_wire",
                "ae2:fluix_glass_cable",
                "tfmg:plastic_sheet",
            ],
            output="ae2:import_bus",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:digital_core/interface": _sequence(
            comment=(
                "Populate a quartz service chamber with paired transfer cores, logic "
                "control, an etched backplane, transistor switching, capacitor buffering, "
                "a smart fluix uplink, and a plastic isolation liner"
            ),
            input_item="ae2:quartz_glass",
            ingredients=[
                "ae2:annihilation_core",
                "ae2:formation_core",
                "ae2:logic_processor",
                "tfmg:etched_circuit_board",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "ae2:fluix_smart_cable",
                "tfmg:plastic_sheet",
            ],
            output="ae2:interface",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:digital_core/pattern_provider": _sequence(
            comment=(
                "Convert the proven interface into a crafting dispatcher with a worktable "
                "plane, blank pattern socket, calculation and logic processors, an etched "
                "controller, transistor, capacitor, and copper instruction bus"
            ),
            input_item="ae2:interface",
            ingredients=[
                "minecraft:crafting_table",
                "ae2:blank_pattern",
                "ae2:calculation_processor",
                "ae2:logic_processor",
                "tfmg:etched_circuit_board",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
            ],
            output="ae2:pattern_provider",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:ae2_high_energy/export_bus": _sequence(
            comment=(
                "Build the outbound ME actuator around a piston, then install its formation "
                "core, route logic, etched TFMG controller, powered motor, one-way diode, "
                "copper data lead, fluix network tail, and plastic isolation"
            ),
            input_item="minecraft:piston",
            ingredients=[
                "ae2:formation_core",
                "ae2:logic_processor",
                "tfmg:etched_circuit_board",
                "tfmg:electric_motor",
                "tfmg:electric_diode",
                "tfmg:copper_wire",
                "ae2:fluix_glass_cable",
                "tfmg:plastic_sheet",
            ],
            output="ae2:export_bus",
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        "industrial_colonies:ae2_high_energy/me_p2p_tunnel": _sequence(
            comment=(
                "Turn quartz fiber into a multiplexed ME endpoint with engineering logic, "
                "dense smart bandwidth, fluix termination, an etched backplane, transistor "
                "switching, capacitor buffering, copper telemetry, and plastic isolation"
            ),
            input_item="ae2:quartz_fiber",
            ingredients=[
                "ae2:engineering_processor",
                "ae2:fluix_smart_dense_cable",
                "ae2:fluix_crystal",
                "tfmg:etched_circuit_board",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
                "tfmg:plastic_sheet",
            ],
            output="ae2:me_p2p_tunnel",
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        "industrial_colonies:ae2_high_energy/mega_crafting_unit": _sequence(
            comment=(
                "Scale an ME crafting unit into a MEGA scheduling chassis with accumulation, "
                "engineering and calculation processors, a crafting accelerator, pattern "
                "dispatcher, dense smart backbone, TFMG transformer, paired capacitors, etched "
                "control board, and elite supervisory logic"
            ),
            input_item="ae2:crafting_unit",
            ingredients=[
                "megacells:accumulation_processor",
                "ae2:engineering_processor",
                "ae2:calculation_processor",
                "ae2:crafting_accelerator",
                "ae2:pattern_provider",
                "ae2:fluix_smart_dense_cable",
                "tfmg:transformer",
                "2x tfmg:capacitor_item",
                "tfmg:etched_circuit_board",
                "mekanism:elite_control_circuit",
            ],
            output="megacells:mega_crafting_unit",
            deployer=RAILWAY_DEPLOYER,
            press=RAILWAY_PRESS,
        ),
        "industrial_colonies:mekanism/transmission/basic_logistical_transporter": _compacting(
            comment=(
                "Compress chute channels, a depot transfer bed, copper wear plates, infused "
                "couplings, TFMG routing logic, and copper controls in the Weathered Iron line"
            ),
            inputs=[
                "2x create:chute",
                "2x create:depot",
                "2x create:copper_sheet",
                "2x mekanism:alloy_infused",
                "tfmg:circuit_board",
                "tfmg:copper_wire",
            ],
            output_id="mekanism:basic_logistical_transporter",
            machine=WEATHERED_PRESS,
        ),
        "industrial_colonies:mekanism/transmission/basic_pressurized_tube": _compacting(
            comment=(
                "Pressure-laminate TFMG steel pipe and casing around inspection glass, rubber "
                "seals, a steel fluid valve, and infused joints in the Weathered Iron line"
            ),
            inputs=[
                "4x tfmg:steel_pipe",
                "2x tfmg:steel_casing",
                "#c:glass_blocks/cheap",
                "4x tfmg:rubber_sheet",
                "tfmg:steel_fluid_valve",
                "2x mekanism:alloy_infused",
            ],
            output_id="mekanism:basic_pressurized_tube",
            machine=WEATHERED_PRESS,
        ),
        "industrial_colonies:mekanism/transmission/basic_universal_cable": _compacting(
            comment=(
                "Laminate copper conductors through TFMG cable tubes, rubber jackets, copper "
                "armor, infused couplings, and Electro Energetics terminations on the Copper line"
            ),
            inputs=[
                "4x tfmg:copper_wire",
                "2x tfmg:cable_tube",
                "4x tfmg:rubber_sheet",
                "2x create:copper_sheet",
                "2x mekanism:alloy_infused",
                "2x electroenergetics:connector",
            ],
            output_id="mekanism:basic_universal_cable",
            machine=COPPER_PRESS,
        ),
    }


def _support_designs() -> dict[str, Recipe]:
    return {
        ELITE_MECHANICAL_PIPE_ID: _compacting(
            comment=(
                "Fabricate the approved Elite liquid manifold directly from TFMG steel "
                "pipe, smart-flow sections, dedicated pumps, reinforced alloy joints, "
                "Elite control, and heavy pressure bands; no disabled lower pipe is used"
            ),
            inputs=[
                "8x tfmg:steel_pipe",
                "4x tfmg:steel_smart_fluid_pipe",
                "2x tfmg:steel_mechanical_pump",
                "4x mekanism:alloy_reinforced",
                "2x mekanism:elite_control_circuit",
                "2x tfmg:heavy_plate",
            ],
            output_id="mekanism:elite_mechanical_pipe",
            machine=INDUSTRIAL_PRESS,
        )
    }


def _rewrite_exact_items(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in replacements.items():
            if value == old:
                return new
            suffix = "x " + old
            if value.endswith(suffix) and value[: -len(suffix)].isdigit():
                return value[: -len(old)] + new
        return value
    if isinstance(value, list):
        return [_rewrite_exact_items(item, replacements) for item in value]
    if isinstance(value, dict):
        return {
            key: _rewrite_exact_items(item, replacements)
            for key, item in value.items()
        }
    return value


def _rewrite_disabled_transmission_consumers(data: dict[str, Any]) -> None:
    indexes = _index(data)
    missing = sorted(SUPPORT_REDESIGN_IDS.difference(indexes))
    if missing:
        raise KeyError(f"disabled-transmission support recipes are missing: {missing}")

    for recipe_id, process in _support_designs().items():
        _replace(data, recipe_id, process)

    indexes = _index(data)
    process_fields = (
        "input",
        "inputs",
        "held",
        "key",
        "ingredients",
        "steps",
        "machine",
        "transitional",
    )
    for recipe_id, replacements in SUPPORT_ITEM_REPLACEMENTS.items():
        recipe = data["recipes"][indexes[recipe_id]]
        for field in process_fields:
            if field in recipe:
                recipe[field] = _rewrite_exact_items(recipe[field], replacements)
        recipe["comment"] = SUPPORT_COMMENTS[recipe_id]


def _replace(data: dict[str, Any], recipe_id: str, process: Recipe) -> None:
    indexes = _index(data)
    if recipe_id not in indexes:
        raise KeyError(f"expected active rejected recipe is missing: {recipe_id}")
    recipe = data["recipes"][indexes[recipe_id]]
    for field in _PROCESS_FIELDS:
        recipe.pop(field, None)
    recipe.update(deepcopy(process))


def _drop_dependency(recipe: Recipe, retired_ids: frozenset[str]) -> None:
    dependencies = recipe.get("depends_on")
    if dependencies is None:
        return
    if not isinstance(dependencies, list):
        raise TypeError(f"managed recipe {recipe.get('id')!r} has invalid depends_on")
    remaining = [dependency for dependency in dependencies if dependency not in retired_ids]
    if remaining:
        recipe["depends_on"] = remaining
    else:
        recipe.pop("depends_on", None)


def _retire_redundant_transmitters(data: dict[str, Any]) -> None:
    indexes = _index(data)
    additional = _require_list(data, "additional_removals")
    excluded = _require_list(data, "exclude_outputs")
    preserved = _require_list(data, "preserve_recipe_ids")

    for recipe_id, (stock_id, output_id) in RETIREMENTS.items():
        if recipe_id not in indexes and not (
            stock_id in additional and output_id in excluded
        ):
            raise KeyError(f"expected rejected transmitter is missing without retirement: {recipe_id}")
        if stock_id not in additional:
            additional.append(stock_id)
        if output_id not in excluded:
            excluded.append(output_id)
        preserved[:] = [value for value in preserved if value != stock_id]

    data["recipes"] = [
        recipe
        for recipe in data["recipes"]
        if recipe.get("id") not in RETIRED_IDS
    ]
    disabled = _require_list(data, "disabled_recipe_ids")
    disabled[:] = [value for value in disabled if value not in RETIRED_IDS]

    containers = [*data["recipes"]]
    for family in data.get("machine_families", []):
        containers.extend(family.get("recipes", []))
    for recipe in containers:
        _drop_dependency(recipe, RETIRED_IDS)

    additional.sort()
    excluded.sort()
    preserved.sort()
    disabled.sort()


def _sequence_ingredients(recipe: Recipe) -> list[str]:
    return [
        step["ingredient"]
        for step in recipe.get("steps", [])
        if isinstance(step, dict) and step.get("op") == "deploying"
    ]


def apply(data: dict[str, Any]) -> None:
    designs = _designs()
    if set(designs) != set(REDESIGNED_IDS):
        raise ValueError("digital/transmission design table drifted from its review cohort")
    indexes = _index(data)
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        raise KeyError(f"expected active rejected recipes are missing: {missing}")
    for recipe_id, process in designs.items():
        _replace(data, recipe_id, process)
    _rewrite_disabled_transmission_consumers(data)
    _retire_redundant_transmitters(data)
    audit(data)


def audit(data: dict[str, Any]) -> dict[str, Any]:
    indexes = _index(data)
    recipes = data["recipes"]
    errors: list[str] = []
    missing = sorted(REDESIGNED_IDS.difference(indexes))
    if missing:
        errors.append(f"missing redesigned recipes: {missing}")
    surviving = sorted(RETIRED_IDS.intersection(indexes))
    if surviving:
        errors.append(f"redundant transmitters still have managed producers: {surviving}")

    family_by_id = {
        "industrial_colonies:digital_core/import_bus": (COPPER_DEPLOYER, COPPER_PRESS),
        "industrial_colonies:ae2_high_energy/export_bus": (COPPER_DEPLOYER, COPPER_PRESS),
        "industrial_colonies:digital_core/interface": (BRASS_DEPLOYER, BRASS_PRESS),
        "industrial_colonies:digital_core/pattern_provider": (BRASS_DEPLOYER, BRASS_PRESS),
        "industrial_colonies:ae2_high_energy/me_p2p_tunnel": (BRASS_DEPLOYER, BRASS_PRESS),
        "industrial_colonies:ae2_high_energy/mega_crafting_unit": (
            RAILWAY_DEPLOYER,
            RAILWAY_PRESS,
        ),
    }
    signatures: set[tuple[str, ...]] = set()
    for recipe_id, (deployer, press) in family_by_id.items():
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        ingredients = _sequence_ingredients(recipe)
        if recipe.get("type") != "sequenced_assembly":
            errors.append(f"{recipe_id} is not Sequenced Assembly")
            continue
        if len(ingredients) < 7:
            errors.append(f"{recipe_id} remains too simple with {len(ingredients)} deployments")
        if "pattern" in recipe or "key" in recipe:
            errors.append(f"{recipe_id} regressed to a perimeter-grid recipe")
        steps = recipe.get("steps", [])
        if not steps or steps[-1] != _press(press):
            errors.append(f"{recipe_id} does not finish on its electronics-family press")
        if any(step.get("machine") != deployer for step in steps[:-1]):
            errors.append(f"{recipe_id} escaped its electronics-family deployer")
        rendered = repr(recipe)
        if "tfmg:" not in rendered or "ae2:" not in rendered:
            errors.append(f"{recipe_id} lost its TFMG/AE electronics identity")
        signature = tuple(ingredients)
        if signature in signatures:
            errors.append(f"{recipe_id} duplicates another digital assembly sequence")
        signatures.add(signature)

    compacting_machines = {
        "industrial_colonies:mekanism/transmission/basic_logistical_transporter": WEATHERED_PRESS,
        "industrial_colonies:mekanism/transmission/basic_pressurized_tube": WEATHERED_PRESS,
        "industrial_colonies:mekanism/transmission/basic_universal_cable": COPPER_PRESS,
    }
    for recipe_id, machine in compacting_machines.items():
        if recipe_id not in indexes:
            continue
        recipe = recipes[indexes[recipe_id]]
        if recipe.get("type") != "compacting" or recipe.get("machine") != machine:
            errors.append(f"{recipe_id} is not locked to its reviewed compacting line")
        if "pattern" in recipe or "key" in recipe:
            errors.append(f"{recipe_id} regressed to a shaped perimeter recipe")
        output = recipe.get("output", {})
        if not isinstance(output, dict) or output.get("count") != 8:
            errors.append(f"{recipe_id} lost its balanced eight-part batch")

    elite_pipe = recipes[indexes[ELITE_MECHANICAL_PIPE_ID]]
    if (
        elite_pipe.get("type") != "compacting"
        or elite_pipe.get("machine") != INDUSTRIAL_PRESS
        or elite_pipe.get("output", {}).get("count") != 8
    ):
        errors.append("approved Elite Mechanical Pipe lost its direct Industrial-Iron batch")
    if "tfmg:steel_smart_fluid_pipe" not in repr(elite_pipe):
        errors.append("Elite Mechanical Pipe lost its TFMG smart-flow manifold")

    retired_outputs = {output_id for _, output_id in RETIREMENTS.values()}
    input_fields = (
        "input",
        "inputs",
        "held",
        "key",
        "ingredients",
        "steps",
        "machine",
        "transitional",
    )
    for recipe in recipes:
        rendered_inputs = repr(
            {field: recipe[field] for field in input_fields if field in recipe}
        )
        leaked = sorted(output for output in retired_outputs if output in rendered_inputs)
        if leaked:
            errors.append(
                f"{recipe.get('id')} still consumes disabled transmission items: {leaked}"
            )

    additional = set(data.get("additional_removals", []))
    excluded = set(data.get("exclude_outputs", []))
    preserved = set(data.get("preserve_recipe_ids", []))
    for recipe_id, (stock_id, output_id) in RETIREMENTS.items():
        if stock_id not in additional:
            errors.append(f"{recipe_id} lost exact stock removal {stock_id}")
        if output_id not in excluded:
            errors.append(f"{recipe_id} output can be regenerated automatically")
        if stock_id in preserved:
            errors.append(f"{recipe_id} stock recipe is simultaneously preserved and disabled")
        for recipe in recipes:
            if recipe_id in recipe.get("depends_on", []):
                errors.append(f"{recipe.get('id')} still depends on retired {recipe_id}")

    if errors:
        raise ValueError("Digital/transmission rejection audit failed: " + " | ".join(errors))
    return {
        "status": "PASS",
        "review_decisions": len(REVIEW_DECISION_IDS),
        "redesigned": len(REDESIGNED_IDS),
        "retired": len(RETIRED_IDS),
        "support_redesigns": len(SUPPORT_REDESIGN_IDS),
        "digital_sequences": len(family_by_id),
        "transmission_compacting": len(compacting_machines),
    }
