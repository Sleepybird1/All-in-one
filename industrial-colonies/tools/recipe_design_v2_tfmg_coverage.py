#!/usr/bin/env python3
"""Close important TFMG-adjacent recipe gaps in recipe design v2.

This module is a pure, idempotent seed transform.  It intentionally covers
only functional machines and components whose installed recipes either bypass
the pack's casing-language progression or reduce an industrial part to a
one-line/shapeless craft.  Coherent source recipes remain source-owned; in
particular, TFMG's stator, transmission, crankshaft, engine gearbox, diode,
electrical switches, air intake, exhaust, firebox, and potentiometer are not
copied into the managed project.

Manufacturing environments follow the pack's established grammar:

* Copper handles conductors and electromechanical winding/formation.
* Brass handles sensing and control logic.
* Railway handles engines, pressure service, and high-current equipment.

``apply`` mutates only the dictionary supplied by its caller.  It performs no
file writes, registry scans, builds, deployments, or runtime tests.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


Recipe = dict[str, Any]


def _deploy(ingredient: str, casing: str) -> dict[str, str]:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": f"createcasing:{casing}_deployer",
    }


def _press(casing: str) -> dict[str, str]:
    return {"op": "pressing", "machine": f"createcasing:{casing}_press"}


def _sequence(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    casing: str,
    remove: list[str],
) -> Recipe:
    return {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": 1,
        "steps": [_deploy(ingredient, casing) for ingredient in ingredients]
        + [_press(casing)],
        "remove": remove,
        "exclusive_output": True,
    }


def _compacting(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    machine: str,
    inputs: list[str],
    output: str,
    remove: list[str],
) -> Recipe:
    return {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": inputs,
        "output": output,
        "remove": remove,
        "exclusive_output": True,
    }


def _grid(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    recipe_type: str,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    remove: list[str],
) -> Recipe:
    if recipe_type not in {"shaped", "mechanical_crafting"}:
        raise ValueError(f"unsupported grid type: {recipe_type}")
    if not pattern or any(len(row) != len(pattern[0]) for row in pattern):
        raise ValueError(f"non-rectangular pattern for {recipe_id}: {pattern!r}")
    return {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": recipe_type,
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": remove,
        "exclusive_output": True,
    }


_MANAGED_RECIPES: tuple[Recipe, ...] = (
    _compacting(
        recipe_id="industrial_colonies:tfmg_coverage/spark_plug",
        node="CR01 — Early Combusion Engines",
        phase="Steel & Petroleum",
        order=300,
        comment=(
            "Copper-press a fired ceramic insulator, aluminum terminal, and "
            "copper lead into one inexpensive but manufactured spark plug"
        ),
        machine="createcasing:copper_press",
        inputs=[
            "tfmg:unfinished_insulator",
            "tfmg:aluminum_nugget",
            "tfmg:copper_wire",
        ],
        output="tfmg:spark_plug",
        remove=["tfmg:mechanical_crafting/spark_plug"],
    ),
    _sequence(
        recipe_id="industrial_colonies:tfmg_coverage/machine_input",
        node="CR01 — The Steel Age",
        phase="Steel & Petroleum",
        order=300,
        comment=(
            "Fit a heavy multiblock input with its drive shaft, service gear, "
            "steel mechanism, and fastener on the Railway assembly line"
        ),
        input_item="tfmg:heavy_machinery_casing",
        output="tfmg:machine_input",
        ingredients=[
            "tfmg:steel_mechanism",
            "create:shaft",
            "tfmg:steel_cogwheel",
            "tfmg:screw",
        ],
        casing="railway",
        remove=["tfmg:crafting/materials/machine_input"],
    ),
    _grid(
        recipe_id="industrial_colonies:tfmg_coverage/aluminum_fluid_valve",
        node="CR01 — Chemical Processing",
        phase="Steel & Petroleum",
        order=301,
        recipe_type="shaped",
        comment=(
            "Build the light-service valve as a handwheel and clamped aluminum "
            "body around the matching pipe"
        ),
        pattern=[" H ", "APA", " S "],
        key={
            "H": "create:copper_valve_handle",
            "A": "tfmg:aluminum_sheet",
            "P": "tfmg:aluminum_pipe",
            "S": "tfmg:screw",
        },
        output="tfmg:aluminum_fluid_valve",
        remove=["tfmg:crafting/materials/aluminum_fluid_valve"],
    ),
    _grid(
        recipe_id="industrial_colonies:tfmg_coverage/steel_fluid_valve",
        node="CR01 — Chemical Processing",
        phase="Steel & Petroleum",
        order=302,
        recipe_type="shaped",
        comment=(
            "Build the pressure valve around a steel pipe with a geared stem "
            "and heavy cheek plates"
        ),
        pattern=[" H ", "PSP", " G "],
        key={
            "H": "create:copper_valve_handle",
            "P": "tfmg:heavy_plate",
            "S": "tfmg:steel_pipe",
            "G": "tfmg:steel_cogwheel",
        },
        output="tfmg:steel_fluid_valve",
        remove=["tfmg:crafting/materials/steel_fluid_valve"],
    ),
    _grid(
        recipe_id="industrial_colonies:tfmg_coverage/plastic_fluid_valve",
        node="CR01 — Chemical Processing",
        phase="Steel & Petroleum",
        order=303,
        recipe_type="shaped",
        comment=(
            "Build the corrosion-service valve with a plastic pipe body, "
            "rubber seals, plastic backing, and external handwheel"
        ),
        pattern=[" H ", "RTR", " P "],
        key={
            "H": "create:copper_valve_handle",
            "R": "tfmg:rubber_sheet",
            "T": "tfmg:plastic_pipe",
            "P": "tfmg:plastic_sheet",
        },
        output="tfmg:plastic_fluid_valve",
        remove=["tfmg:crafting/materials/plastic_fluid_valve"],
    ),
    _sequence(
        recipe_id="industrial_colonies:tfmg_coverage/aluminum_smart_fluid_pipe",
        node="CR01 — Control Electronics",
        phase="Electrical Manufacturing",
        order=310,
        comment=(
            "Instrument the aluminum valve with a TFMG control board, discrete "
            "transistor, copper signal lead, and matching light-service cover"
        ),
        input_item="tfmg:aluminum_fluid_valve",
        output="tfmg:aluminum_smart_fluid_pipe",
        ingredients=[
            "tfmg:circuit_board",
            "tfmg:transistor_item",
            "tfmg:copper_wire",
            "tfmg:aluminum_sheet",
        ],
        casing="brass",
        remove=["tfmg:crafting/materials/aluminum_smart_fluid_pipe"],
    ),
    _sequence(
        recipe_id="industrial_colonies:tfmg_coverage/steel_smart_fluid_pipe",
        node="CR01 — Control Electronics",
        phase="Electrical Manufacturing",
        order=311,
        comment=(
            "Instrument the pressure valve with a TFMG board, directional "
            "diode, analog set-point control, and heavy protective cover"
        ),
        input_item="tfmg:steel_fluid_valve",
        output="tfmg:steel_smart_fluid_pipe",
        ingredients=[
            "tfmg:circuit_board",
            "tfmg:electric_diode",
            "tfmg:potentiometer",
            "tfmg:heavy_plate",
        ],
        casing="brass",
        remove=["tfmg:crafting/materials/steel_smart_fluid_pipe"],
    ),
    _sequence(
        recipe_id="industrial_colonies:tfmg_coverage/plastic_smart_fluid_pipe",
        node="CR01 — Control Electronics",
        phase="Electrical Manufacturing",
        order=312,
        comment=(
            "Instrument the chemical valve with sealed TFMG logic, a discrete "
            "transistor, rubber isolation, and a plastic electronics cover"
        ),
        input_item="tfmg:plastic_fluid_valve",
        output="tfmg:plastic_smart_fluid_pipe",
        ingredients=[
            "tfmg:circuit_board",
            "tfmg:transistor_item",
            "tfmg:rubber_sheet",
            "tfmg:plastic_sheet",
        ],
        casing="brass",
        remove=["tfmg:crafting/materials/plastic_smart_fluid_pipe"],
    ),
    _sequence(
        recipe_id="industrial_colonies:tfmg_coverage/steel_cable_hub",
        node="CR01 — Early Power Cables",
        phase="Electrical Manufacturing",
        order=320,
        comment=(
            "Turn one steel enclosure into a matched hub pair by installing "
            "TFMG endpoints, twin copper conductors, and rubber isolation"
        ),
        input_item="tfmg:steel_casing",
        output="2x tfmg:steel_cable_hub",
        ingredients=[
            "tfmg:cable_connector",
            "tfmg:copper_wire",
            "tfmg:copper_wire",
            "tfmg:rubber_sheet",
        ],
        casing="copper",
        remove=["tfmg:crafting/materials/steel_cable_hub"],
    ),
    _sequence(
        recipe_id="industrial_colonies:tfmg_coverage/heavy_cable_hub",
        node="CR01 — Early Power Cables",
        phase="Electrical Manufacturing",
        order=321,
        comment=(
            "Rebuild a steel hub for heavy current with a machinery shell, "
            "complete copper winding, insulated endpoint, and Railway closure"
        ),
        input_item="tfmg:steel_cable_hub",
        output="tfmg:heavy_cable_hub",
        ingredients=[
            "tfmg:heavy_machinery_casing",
            "tfmg:copper_spool",
            "tfmg:cable_connector",
            "tfmg:rubber_sheet",
        ],
        casing="railway",
        remove=["tfmg:crafting/materials/heavy_cable_hub"],
    ),
    _sequence(
        recipe_id="industrial_colonies:createaddition_coverage/rolling_mill",
        node="CR01 — Electronics Manufacturing",
        phase="Electrical Manufacturing",
        order=330,
        comment=(
            "Refit a Copper press into a continuous rolling stand with twin "
            "shafts, a steel drive gear, pressure plate, and service mechanism"
        ),
        input_item="createcasing:copper_press",
        output="createaddition:rolling_mill",
        ingredients=[
            "create:shaft",
            "create:shaft",
            "tfmg:steel_cogwheel",
            "tfmg:heavy_plate",
            "tfmg:steel_mechanism",
        ],
        casing="copper",
        remove=["createaddition:crafting/rolling_mill"],
    ),
    _sequence(
        recipe_id="industrial_colonies:createaddition_coverage/tesla_coil",
        node="CR01 — Advanced Electronics Manufacturing",
        phase="Electrical Manufacturing",
        order=331,
        comment=(
            "Convert the canonical TFMG transformer into a controlled Tesla "
            "coil with wound copper, stored charge, directional protection, "
            "voltage observation, and a steel power endpoint"
        ),
        input_item="tfmg:transformer",
        output="createaddition:tesla_coil",
        ingredients=[
            "tfmg:copper_spool",
            "tfmg:copper_spool",
            "tfmg:capacitor_item",
            "tfmg:electric_diode",
            "tfmg:voltage_observer",
            "tfmg:steel_cable_hub",
        ],
        casing="railway",
        remove=["createaddition:mechanical_crafting/tesla_coil"],
    ),
    _compacting(
        recipe_id="industrial_colonies:diesel_generators_coverage/engine_piston",
        node="CR01 — Diesel Engines",
        phase="Steel & Petroleum",
        order=340,
        comment=(
            "Pressure-form a matched piston pair from aluminum crowns, a "
            "cast-iron skirt, shaft stock, and one service fastener"
        ),
        machine="createcasing:railway_press",
        inputs=[
            "tfmg:aluminum_sheet",
            "tfmg:aluminum_sheet",
            "tfmg:cast_iron_sheet",
            "create:shaft",
            "tfmg:screw",
        ],
        output="2x createdieselgenerators:engine_piston",
        remove=[
            "createdieselgenerators:crafting/engine_piston",
            "createdieselgenerators:crafting/engine_piston_from_rods",
        ],
    ),
    _sequence(
        recipe_id="industrial_colonies:diesel_generators_coverage/basin_lid",
        node="CR01 — Diesel Processing",
        phase="Steel & Petroleum",
        order=341,
        comment=(
            "Build the timed basin lid as a heavy cover with clockwork, an "
            "electron-tube trigger, a steel latch mechanism, and Brass facing"
        ),
        input_item="tfmg:heavy_plate",
        output="createdieselgenerators:basin_lid",
        ingredients=[
            "minecraft:clock",
            "create:electron_tube",
            "tfmg:steel_mechanism",
            "create:brass_sheet",
        ],
        casing="brass",
        remove=["createdieselgenerators:crafting/basin_lid"],
    ),
    _grid(
        recipe_id="industrial_colonies:diesel_generators_coverage/bulk_fermenter",
        node="CR01 — Diesel Processing",
        phase="Steel & Petroleum",
        order=342,
        recipe_type="mechanical_crafting",
        comment=(
            "Construct the fermenter as a sealed barrel and basin over a "
            "pumped cast-iron reservoir inside a pressure-rated frame"
        ),
        pattern=[" L ", "PBP", "HTH", " M "],
        key={
            "L": "createdieselgenerators:basin_lid",
            "P": "tfmg:steel_pipe",
            "B": "minecraft:barrel",
            "H": "tfmg:heavy_plate",
            "T": "tfmg:cast_iron_fluid_tank",
            "M": "tfmg:steel_mechanical_pump",
        },
        output="createdieselgenerators:bulk_fermenter",
        remove=["createdieselgenerators:crafting/bulk_fermenter"],
    ),
    _grid(
        recipe_id="industrial_colonies:diesel_generators_coverage/burner",
        node="CR01 — Diesel Engines",
        phase="Steel & Petroleum",
        order=343,
        recipe_type="mechanical_crafting",
        comment=(
            "Build the liquid-fuel burner as an ignited steel feed over a "
            "TFMG firebox, enclosed by refractory brick and a heavy base"
        ),
        pattern=["FSF", "PBP", "HMH"],
        key={
            "F": "tfmg:fireproof_bricks",
            "S": "tfmg:spark_plug",
            "P": "tfmg:steel_pipe",
            "B": "create:empty_blaze_burner",
            "H": "tfmg:heavy_plate",
            "M": "tfmg:firebox",
        },
        output="createdieselgenerators:burner",
        remove=["createdieselgenerators:crafting/burner"],
    ),
    _grid(
        recipe_id="industrial_colonies:diesel_generators_coverage/canister",
        node="CR01 — Diesel Processing",
        phase="Steel & Petroleum",
        order=344,
        recipe_type="shaped",
        comment=(
            "Fold a hollow aluminum canister around a real fluid valve with a "
            "rubber-sealed bottom instead of hiding a wooden barrel inside it"
        ),
        pattern=["AVA", "A A", "ARA"],
        key={
            "A": "tfmg:aluminum_sheet",
            "V": "tfmg:aluminum_fluid_valve",
            "R": "tfmg:rubber_sheet",
        },
        output="createdieselgenerators:canister",
        remove=["createdieselgenerators:crafting/canister"],
    ),
    _sequence(
        recipe_id="industrial_colonies:diesel_generators_coverage/engine_silencer",
        node="CR01 — Diesel Engines",
        phase="Steel & Petroleum",
        order=345,
        comment=(
            "Repack a TFMG exhaust with two acoustic baffles, rubber isolation, "
            "an aluminum jacket, and a pressure-rated outlet"
        ),
        input_item="tfmg:exhaust",
        output="createdieselgenerators:engine_silencer",
        ingredients=[
            "minecraft:white_wool",
            "minecraft:white_wool",
            "tfmg:rubber_sheet",
            "tfmg:aluminum_sheet",
            "tfmg:steel_pipe",
        ],
        casing="railway",
        remove=["createdieselgenerators:crafting/engine_silencer"],
    ),
)


# These outputs are direct duplicates of the canonical TFMG system rather than
# useful alternate machines.  The CreateAddition capacitor is no longer a
# dependency after the unique Tesla Coil is ported above, and CDG's controller
# has no valid process after the duplicate petroleum distillation recipes are
# retired by the canonical petroleum layer.
_RETIREMENTS: dict[str, tuple[str, ...]] = {
    "createaddition:capacitor": (
        "createaddition:crafting/capacitor_1",
        "createaddition:crafting/capacitor_2",
    ),
    "createdieselgenerators:distillation_controller": (
        "createdieselgenerators:crafting/distillation_controller",
    ),
}


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed seed field {field!r} must be a list")
    return value


def _append_unique(values: list[Any], additions: Iterable[str]) -> None:
    seen = set(values)
    for value in additions:
        if value not in seen:
            values.append(value)
            seen.add(value)


def _declared_outputs(recipe: Recipe) -> set[str]:
    outputs: set[str] = set()

    def collect(value: Any) -> None:
        if isinstance(value, str):
            outputs.add(value.rsplit(" ", 1)[-1])
        elif isinstance(value, dict):
            item_id = value.get("id") or value.get("item")
            if isinstance(item_id, str):
                outputs.add(item_id)

    collect(recipe.get("output"))
    collect(recipe.get("result"))
    results = recipe.get("results", [])
    if isinstance(results, list):
        for result in results:
            collect(result)
    return outputs


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = _require_list(data, "recipes")
    matches = [
        index
        for index, current in enumerate(recipes)
        if isinstance(current, dict) and current.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"managed recipe is duplicated: {recipe['id']}")
    if matches:
        recipes[matches[0]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def _assert_no_output_collisions(data: dict[str, Any]) -> None:
    owned_ids = {recipe["id"] for recipe in _MANAGED_RECIPES}
    wanted = {
        output
        for recipe in _MANAGED_RECIPES
        for output in _declared_outputs(recipe)
    }
    conflicts: list[tuple[str, str]] = []
    for recipe in _require_list(data, "recipes"):
        if not isinstance(recipe, dict):
            raise TypeError("managed recipe entries must be objects")
        recipe_id = recipe.get("id")
        if recipe_id in owned_ids:
            continue
        for output in sorted(_declared_outputs(recipe) & wanted):
            conflicts.append((output, str(recipe_id)))
    if conflicts:
        rendered = ", ".join(f"{output} via {recipe_id}" for output, recipe_id in conflicts)
        raise ValueError(f"TFMG coverage overlaps an existing managed output: {rendered}")


def apply(data: dict[str, Any]) -> None:
    """Apply the audited TFMG/CreateAddition/CDG coverage wave in place."""

    _assert_no_output_collisions(data)
    for recipe in _MANAGED_RECIPES:
        _upsert(data, recipe)

    managed_stock_ids = {
        stock_id
        for recipe in _MANAGED_RECIPES
        for stock_id in recipe.get("remove", [])
    }
    retired_stock_ids = {
        stock_id for stock_ids in _RETIREMENTS.values() for stock_id in stock_ids
    }
    preserve_recipe_ids = _require_list(data, "preserve_recipe_ids")
    preserve_recipe_ids[:] = [
        recipe_id
        for recipe_id in preserve_recipe_ids
        if recipe_id not in managed_stock_ids | retired_stock_ids
    ]

    # A managed recipe owns its stock replacement through its local ``remove``
    # list.  Keep global removals only for intentionally inaccessible duplicate
    # outputs so the resulting manifest remains easy to audit.
    additional_removals = _require_list(data, "additional_removals")
    additional_removals[:] = [
        recipe_id
        for recipe_id in additional_removals
        if recipe_id not in managed_stock_ids
    ]
    _append_unique(additional_removals, sorted(retired_stock_ids))

    exclude_outputs = _require_list(data, "exclude_outputs")
    managed_outputs = {
        output
        for recipe in _MANAGED_RECIPES
        for output in _declared_outputs(recipe)
    }
    exclude_outputs[:] = [
        output for output in exclude_outputs if output not in managed_outputs
    ]
    _append_unique(exclude_outputs, sorted(_RETIREMENTS))
