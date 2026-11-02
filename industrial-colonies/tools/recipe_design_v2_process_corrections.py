"""Correct process mismatches and padded compatibility recipes.

This pass deliberately changes only recipes whose process contradicts the
manufacturing action or whose managed replacement is worse than stock.  It
keeps recipe identity and progression metadata stable while replacing the
body, so later auditing can attribute every change to the original card.
"""

from __future__ import annotations

from typing import Any


WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"
RAILWAY_PRESS = "createcasing:railway_press"
RAILWAY_SAW = "createcasing:railway_mechanical_saw"


def _recipe_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for recipe in data.get("recipes", []):
        recipe_id = recipe.get("id")
        if not isinstance(recipe_id, str):
            continue
        if recipe_id in result:
            raise ValueError(f"Managed recipe is duplicated: {recipe_id}")
        result[recipe_id] = recipe
    return result


def _replace(data: dict[str, Any], recipe_id: str, body: dict[str, Any]) -> None:
    recipes = data.get("recipes", [])
    matches = [index for index, recipe in enumerate(recipes) if recipe.get("id") == recipe_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one managed recipe for {recipe_id}; found {len(matches)}")
    old = recipes[matches[0]]
    replacement: dict[str, Any] = {"id": recipe_id}
    for field in ("node", "phase", "order", "remove", "exclusive_output", "if_mod_loaded", "depends_on"):
        if field in old:
            replacement[field] = old[field]
    replacement.update(body)
    recipes[matches[0]] = replacement


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    comment: str,
    input_item: str,
    output: str,
    steps: list[dict[str, str]],
    transitional: str | None = None,
    loops: int = 1,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    recipe: dict[str, Any] = {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional or input_item,
        "output": output,
        "loops": loops,
        "steps": steps,
    }
    if depends_on is not None:
        recipe["depends_on"] = depends_on
    return recipe


def _restore_stock_create_logistics(data: dict[str, Any]) -> None:
    managed_ids = {
        "industrial_colonies:create_core/andesite_funnel_batch",
        "industrial_colonies:create_core/andesite_tunnel_batch",
    }
    stock_ids = {
        "create:crafting/logistics/andesite_funnel",
        "create:crafting/logistics/andesite_tunnel",
    }
    present = {recipe.get("id") for recipe in data.get("recipes", [])}
    present_targets = managed_ids.intersection(present)
    if present_targets and present_targets != managed_ids:
        missing = sorted(managed_ids.difference(present))
        raise ValueError(f"Create stock-restoration targets are partially missing: {missing}")
    data["recipes"] = [
        recipe for recipe in data["recipes"] if recipe.get("id") not in managed_ids
    ]
    data["additional_removals"] = [
        recipe_id
        for recipe_id in data.get("additional_removals", [])
        if recipe_id not in stock_ids
    ]
    preserved = data.setdefault("preserve_recipe_ids", [])
    for recipe_id in sorted(stock_ids):
        if recipe_id not in preserved:
            preserved.append(recipe_id)


def _retarget_heavy_press_work(data: dict[str, Any]) -> None:
    target_ids = {
        "industrial_colonies:steelworks/fireproof_bricks",
        "industrial_colonies:steelworks/fireproof_brick_reinforcement",
        "industrial_colonies:steelworks/blast_furnace_reinforcement",
        "industrial_colonies:fluid_infrastructure/steel_pipe",
        "industrial_colonies:fluid_infrastructure/industrial_pipe",
        "industrial_colonies:fluid_infrastructure/aluminum_pipe",
    }
    recipes = _recipe_map(data)
    missing = sorted(target_ids.difference(recipes))
    if missing:
        raise ValueError(f"Heavy press retargets are missing: {missing}")
    comments = {
        "industrial_colonies:steelworks/fireproof_bricks": (
            "Railway-press four fired TFMG refractory bricks into one regular "
            "blast-furnace wall block."
        ),
        "industrial_colonies:steelworks/fireproof_brick_reinforcement": (
            "Railway-press six regular wall blocks into six load-bearing "
            "refractory supports without finished steel."
        ),
        "industrial_colonies:steelworks/blast_furnace_reinforcement": (
            "After first steel, Railway-press steel, Heavy Plates, and refractory "
            "wall blocks into four reinforced-furnace supports."
        ),
        "industrial_colonies:fluid_infrastructure/steel_pipe": (
            "Roll and Railway-press steel plate around a steel mandrel into a "
            "four-section pressure-line batch."
        ),
        "industrial_colonies:fluid_infrastructure/industrial_pipe": (
            "Railway-press steel pipe, Heavy Plates, and a Steel Mechanism into "
            "an eight-block structural refinery-column batch."
        ),
        "industrial_colonies:fluid_infrastructure/aluminum_pipe": (
            "Roll and Railway-press aluminum plate around a light-alloy mandrel "
            "into four turbine-service pipe sections."
        ),
    }
    for recipe_id in sorted(target_ids):
        recipe = recipes[recipe_id]
        if recipe.get("type") != "compacting" or recipe.get("machine") not in {
            "createcasing:brass_press",
            RAILWAY_PRESS,
        }:
            raise ValueError(f"{recipe_id} is no longer the expected heavy compacting recipe")
        recipe["machine"] = RAILWAY_PRESS
        recipe["comment"] = comments[recipe_id]


def _correct_nuclear_ports(data: dict[str, Any]) -> None:
    _replace(
        data,
        "industrial_colonies:nuclear/basic_reactor_power_tap",
        _sequence(
            comment=(
                "Convert one basic reactor casing into a serviceable grid tap with "
                "one TFMG transformer, one protected connector, a completed "
                "high-current spool, and an elite trip controller"
            ),
            input_item="bigreactors:basic_reactorcasing",
            output="bigreactors:basic_reactorpowertapfe_passive",
            steps=[
                _deploy("tfmg:transformer", WEATHERED_DEPLOYER),
                _deploy("electroenergetics:connector", WEATHERED_DEPLOYER),
                _deploy("electroenergetics:heavily_insulated_wire_spool", WEATHERED_DEPLOYER),
                _deploy("mekanism:elite_control_circuit", WEATHERED_DEPLOYER),
                _press(WEATHERED_PRESS),
            ],
            depends_on=["industrial_colonies:extreme_grid/heavily_insulated_wire_spool"],
        ),
    )
    _replace(
        data,
        "industrial_colonies:nuclear/reinforced_computer_port",
        _sequence(
            comment=(
                "Instrument one reinforced casing as a network port with a single "
                "wired modem, ultimate interface controller, TFMG board, and "
                "shielded Fluix data lead; the reactor controller owns the computer"
            ),
            input_item="bigreactors:reinforced_reactorcasing",
            output="bigreactors:reinforced_reactorcomputerport",
            steps=[
                _deploy("computercraft:wired_modem", RADIANCE_DEPLOYER),
                _deploy("mekanism:ultimate_control_circuit", RADIANCE_DEPLOYER),
                _deploy("tfmg:circuit_board", RADIANCE_DEPLOYER),
                _deploy("ae2:fluix_smart_cable", RADIANCE_DEPLOYER),
                _press(RADIANCE_PRESS),
            ],
        ),
    )


def _correct_process_types(data: dict[str, Any]) -> None:
    _replace(
        data,
        "industrial_colonies:extreme_grid/heavily_insulated_wire_spool",
        _sequence(
            comment=(
                "Wind two matched pairs of protected conductor onto the grid spool, "
                "fit its rubber edge seal and steel ratchet, then close it on the "
                "Weathered high-energy line"
            ),
            input_item="electroenergetics:empty_spool",
            output="electroenergetics:heavily_insulated_wire_spool",
            steps=[
                _deploy("2x electroenergetics:heavily_insulated_wire", WEATHERED_DEPLOYER),
                _deploy("2x electroenergetics:heavily_insulated_wire", WEATHERED_DEPLOYER),
                _deploy("tfmg:rubber_sheet", WEATHERED_DEPLOYER),
                _deploy("tfmg:steel_mechanism", WEATHERED_DEPLOYER),
                _press(WEATHERED_PRESS),
            ],
            depends_on=["industrial_colonies:extreme_grid/heavily_insulated_wire"],
        ),
    )
    _replace(
        data,
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_part",
        {
            "type": "cutting",
            "comment": (
                "Saw one cast-iron billet into a matched pair of small walking-beam "
                "pivots on the Railway heavy-machining line"
            ),
            "machine": RAILWAY_SAW,
            "input": "tfmg:cast_iron_block",
            "output": "2x tfmg:pumpjack_hammer_part",
            "processing_time": 160,
        },
    )
    _replace(
        data,
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part",
        {
            "type": "cutting",
            "comment": (
                "Machine one cast-iron billet into one load-rated large walking-beam "
                "pivot on the Railway heavy-saw line"
            ),
            "machine": RAILWAY_SAW,
            "input": "tfmg:cast_iron_block",
            "output": "tfmg:large_pumpjack_hammer_part",
            "processing_time": 240,
        },
    )


def apply(data: dict[str, Any]) -> None:
    """Apply process corrections without reading or writing the filesystem."""

    _restore_stock_create_logistics(data)
    _retarget_heavy_press_work(data)
    _correct_nuclear_ports(data)
    _correct_process_types(data)
