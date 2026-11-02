#!/usr/bin/env python3
"""Curated Mekanism storage and routing utility repairs.

This wave is intentionally smaller than a namespace rewrite.  The installed
Mekanism recipes were audited as functional devices, and only three weak
families are claimed here:

* bins and the upper tank tiers currently repeat generic alloy/ingot rings;
* diversion/restrictive transporters currently bypass the established
  Logistical Transporter line by starting from iron bars;
* the Mekanism resistive heater is better expressed as an instrumented upgrade
  of the already-manufactured Create: Electro Energetics heater core.

The Oredictionificator is retired without a replacement.  The installed
Extreme Reactors JAR adds Yellorium to ``c:ingots/uranium`` while Mekanism adds
its Uranium Ingot to that same tag.  The machine's tag-normalization behavior
would therefore bypass the pack's deliberately directional Yellorium ->
enriched Uranium process.

Good stock recipes remain stock.  In particular, the Flamethrower, Scuba Mask,
Scuba Tank, Personal Chest/Barrel, Modification Station, Fuelwood Heater,
Logistical Sorter, seismic tools, Security Desk, Robit, configuration tools,
Gauge Dropper, Canteen, Dictionary, Crafting Formula, and Cardboard Box already
describe their function without opening a meaningful progression bypass.

``apply`` is a pure, idempotent in-memory transform.  It does not read or write
the seed, query the catalog, generate KJSGen files, build the mod, or touch the
live pack.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Iterable, Mapping


Recipe = dict[str, Any]


INDUSTRIAL_DEPLOYER = "createcasing:industrial_iron_deployer"
INDUSTRIAL_PRESS = "createcasing:industrial_iron_press"
WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"


# These outputs are explicitly deferred or retired by the pack's progression
# policy.  Keeping the guard beside this wave prevents a future expansion from
# accidentally restoring pocket teleportation, QIO entry, direct factories, or
# the intentionally absent shortcut machines/tools.
FORBIDDEN_OUTPUTS = {
    "mekanism:digital_miner",
    "mekanism:energized_smelter",
    "mekanism:formulaic_assemblicator",
    "mekanism:jetpack_armored",
    "mekanism:meka_tool",
    "mekanism:portable_qio_dashboard",
    "mekanism:portable_teleporter",
    "mekanism:qio_dashboard",
    "mekanism:qio_drive_array",
    "mekanism:quantum_entangloporter",
    "mekanism:teleporter",
}


NEW_RETIREMENTS = {
    "mekanism:oredictionificator",
}


# Exact stock recipes reviewed and intentionally left untouched.  This is
# audit documentation, not a list to preserve mechanically: the design-v2 auto
# assignment system is already disabled, and adding redundant seed metadata
# would only create noise.
AUDITED_STOCK_RECIPES = {
    "mekanism:canteen",
    "mekanism:cardboard_box",
    "mekanism:configuration_card",
    "mekanism:crafting_formula",
    "mekanism:dictionary",
    "mekanism:flamethrower",
    "mekanism:fuelwood_heater",
    "mekanism:gauge_dropper",
    "mekanism:logistical_sorter",
    "mekanism:modification_station",
    "mekanism:personal_barrel",
    "mekanism:personal_chest",
    "mekanism:robit",
    "mekanism:scuba_mask",
    "mekanism:scuba_tank",
    "mekanism:security_desk",
    "mekanism:seismic_reader",
    "mekanism:seismic_vibrator",
}


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    input_item: str,
    ingredients: list[str],
    deployer: str,
    press: str,
    output: str,
    stock_id: str,
    depends_on: list[str] | None = None,
) -> Recipe:
    recipe: Recipe = {
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
        "steps": [_deploy(item, deployer) for item in ingredients]
        + [_press(press)],
        "remove": [stock_id],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _grid(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    stock_id: str,
    depends_on: list[str] | None = None,
) -> Recipe:
    if not pattern or len(pattern) > 4:
        raise ValueError(f"utility grid must be no larger than 4x4: {recipe_id}")
    width = len(pattern[0])
    if not width or width > 4 or any(len(row) != width for row in pattern):
        raise ValueError(f"utility grid must be rectangular and <= 4 wide: {recipe_id}")
    used = set("".join(pattern)) - {" "}
    if used != set(key):
        raise ValueError(
            f"grid symbols do not match key for {recipe_id}: "
            f"used={sorted(used)}, key={sorted(key)}"
        )
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": list(pattern),
        "key": dict(key),
        "output": output,
        "remove": [stock_id],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _compacting(
    *,
    recipe_id: str,
    node: str,
    phase: str,
    order: int,
    comment: str,
    inputs: list[str],
    output: str,
    stock_id: str,
    depends_on: list[str] | None = None,
) -> Recipe:
    recipe: Recipe = {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": INDUSTRIAL_PRESS,
        "inputs": list(inputs),
        "output": output,
        "remove": [stock_id],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _recipes() -> list[Recipe]:
    recipes: list[Recipe] = [
        # --------------------------------------------------------------
        # Fluid storage: each tier keeps the proven vessel and adds the
        # corresponding flow hardware, containment, and reinforcement.
        # --------------------------------------------------------------
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/advanced_fluid_tank",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=660,
            comment=(
                "Reinforce the basic vessel with TFMG heavy shellwork, rubber "
                "seals, a steel service valve, and an infused pressure band."
            ),
            input_item="mekanism:basic_fluid_tank",
            ingredients=[
                "2x tfmg:heavy_plate",
                "2x tfmg:rubber_sheet",
                "tfmg:steel_fluid_valve",
                "tfmg:steel_mechanism",
                "mekanism:alloy_infused",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:advanced_fluid_tank",
            stock_id="mekanism:fluid_tank/advanced",
            depends_on=["industrial_colonies:mekanism_components/basic_fluid_tank"],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/elite_fluid_tank",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=740,
            comment=(
                "Refit the advanced vessel with an elite liquid manifold, HDPE "
                "liner, reinforced pressure band, and replaceable heavy shell."
            ),
            input_item="mekanism:advanced_fluid_tank",
            ingredients=[
                "mekanism:elite_mechanical_pipe",
                "2x mekanism:hdpe_sheet",
                "2x tfmg:heavy_plate",
                "tfmg:rubber_sheet",
                "mekanism:alloy_reinforced",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            output="mekanism:elite_fluid_tank",
            stock_id="mekanism:fluid_tank/elite",
            depends_on=[
                "industrial_colonies:mekanism_utility/advanced_fluid_tank",
                "industrial_colonies:mekanism/transmission/elite_mechanical_pipe",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/ultimate_fluid_tank",
            node="CR01 — High-Energy Distribution",
            phase="High-Energy Grid",
            order=750,
            comment=(
                "Qualify the elite vessel for ultimate throughput with an ultimate "
                "liquid manifold, redundant HDPE lining, atomic locks, and a TFMG "
                "industrial header."
            ),
            input_item="mekanism:elite_fluid_tank",
            ingredients=[
                "mekanism:ultimate_mechanical_pipe",
                "2x mekanism:hdpe_sheet",
                "2x tfmg:heavy_plate",
                "tfmg:industrial_pipe",
                "mekanism:alloy_atomic",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            output="mekanism:ultimate_fluid_tank",
            stock_id="mekanism:fluid_tank/ultimate",
            depends_on=[
                "industrial_colonies:mekanism_utility/elite_fluid_tank",
                "industrial_colonies:mekanism/transmission/ultimate_mechanical_pipe",
            ],
        ),

        # --------------------------------------------------------------
        # Chemical storage: unlike the liquid ladder, every tier receives a
        # chemically safe liner and the matching pressurized-tube manifold.
        # --------------------------------------------------------------
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/advanced_chemical_tank",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=670,
            comment=(
                "Line the basic chemical vessel with TFMG plastic and rubber, then "
                "fit an advanced gas manifold, service valve, and infused locks."
            ),
            input_item="mekanism:basic_chemical_tank",
            ingredients=[
                "mekanism:advanced_pressurized_tube",
                "2x tfmg:plastic_sheet",
                "2x tfmg:rubber_sheet",
                "tfmg:steel_fluid_valve",
                "mekanism:alloy_infused",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:advanced_chemical_tank",
            stock_id="mekanism:chemical_tank/advanced",
            depends_on=[
                "industrial_colonies:mekanism_components/basic_chemical_tank",
                "industrial_colonies:mekanism/transmission/advanced_pressurized_tube",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/elite_chemical_tank",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=741,
            comment=(
                "Upgrade the advanced chemical vessel with an elite gas manifold, "
                "redundant HDPE liner, reinforced band, and heavy containment plate."
            ),
            input_item="mekanism:advanced_chemical_tank",
            ingredients=[
                "mekanism:elite_pressurized_tube",
                "2x mekanism:hdpe_sheet",
                "tfmg:plastic_fluid_valve",
                "2x tfmg:heavy_plate",
                "mekanism:alloy_reinforced",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            output="mekanism:elite_chemical_tank",
            stock_id="mekanism:chemical_tank/elite",
            depends_on=[
                "industrial_colonies:mekanism_utility/advanced_chemical_tank",
                "industrial_colonies:mekanism/transmission/elite_pressurized_tube",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/ultimate_chemical_tank",
            node="CR01 — High-Energy Distribution",
            phase="High-Energy Grid",
            order=751,
            comment=(
                "Qualify the elite chemical vessel with an ultimate gas manifold, "
                "double HDPE barrier, atomic locks, and a replaceable plastic valve."
            ),
            input_item="mekanism:elite_chemical_tank",
            ingredients=[
                "mekanism:ultimate_pressurized_tube",
                "2x mekanism:hdpe_sheet",
                "tfmg:plastic_fluid_valve",
                "2x tfmg:heavy_plate",
                "mekanism:alloy_atomic",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            output="mekanism:ultimate_chemical_tank",
            stock_id="mekanism:chemical_tank/ultimate",
            depends_on=[
                "industrial_colonies:mekanism_utility/elite_chemical_tank",
                "industrial_colonies:mekanism/transmission/ultimate_pressurized_tube",
            ],
        ),

        # --------------------------------------------------------------
        # Physical bulk storage.  The basic bin is a recognizable vertical
        # hopper/vault body; upper tiers upgrade its intake and transport rate.
        # --------------------------------------------------------------
        _grid(
            recipe_id="industrial_colonies:mekanism_utility/basic_bin",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=680,
            comment=(
                "Build a vertical industrial bin around an Item Vault, framed sides, "
                "controlled transporter feed, Brass Funnel inlet, and Chute outlet."
            ),
            pattern=[" F ", "SCS", "TVT", " H "],
            key={
                "F": "create:brass_funnel",
                "S": "tfmg:steel_frame",
                "C": "mekanism:basic_control_circuit",
                "T": "mekanism:basic_logistical_transporter",
                "V": "create:item_vault",
                "H": "create:chute",
            },
            output="mekanism:basic_bin",
            stock_id="mekanism:bin/basic",
            depends_on=[
                "industrial_colonies:mekanism/transmission/basic_logistical_transporter"
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/advanced_bin",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=690,
            comment=(
                "Upgrade the basic bin with paired advanced transport feeds, a Smart "
                "Chute, inventory observer, reinforced drive, and advanced control."
            ),
            input_item="mekanism:basic_bin",
            ingredients=[
                "2x mekanism:advanced_logistical_transporter",
                "create:smart_chute",
                "create:content_observer",
                "tfmg:steel_mechanism",
                "mekanism:advanced_control_circuit",
                "mekanism:alloy_infused",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:advanced_bin",
            stock_id="mekanism:bin/advanced",
            depends_on=[
                "industrial_colonies:mekanism_utility/basic_bin",
                "industrial_colonies:mekanism/transmission/advanced_logistical_transporter",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/elite_bin",
            node="CR01 — Precision Engineering",
            phase="High-Energy Grid",
            order=742,
            comment=(
                "Refit the advanced bin with elite transport feeds, a balanced Brass "
                "distribution tunnel, powered feeder, heavy shell, and elite governor."
            ),
            input_item="mekanism:advanced_bin",
            ingredients=[
                "2x mekanism:elite_logistical_transporter",
                "create:brass_tunnel",
                "tfmg:electric_motor",
                "2x tfmg:heavy_plate",
                "mekanism:elite_control_circuit",
                "mekanism:alloy_reinforced",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            output="mekanism:elite_bin",
            stock_id="mekanism:bin/elite",
            depends_on=[
                "industrial_colonies:mekanism_utility/advanced_bin",
                "industrial_colonies:mekanism/transmission/elite_logistical_transporter",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/ultimate_bin",
            node="CR01 — High-Energy Distribution",
            phase="High-Energy Grid",
            order=752,
            comment=(
                "Qualify the elite bin for ultimate throughput with ultimate transport "
                "feeds, an atomic-locked tunnel, redundant drive, and final control."
            ),
            input_item="mekanism:elite_bin",
            ingredients=[
                "2x mekanism:ultimate_logistical_transporter",
                "create:brass_tunnel",
                "2x tfmg:electric_motor",
                "2x tfmg:heavy_plate",
                "mekanism:ultimate_control_circuit",
                "mekanism:alloy_atomic",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            output="mekanism:ultimate_bin",
            stock_id="mekanism:bin/ultimate",
            depends_on=[
                "industrial_colonies:mekanism_utility/elite_bin",
                "industrial_colonies:mekanism/transmission/ultimate_logistical_transporter",
            ],
        ),

        # --------------------------------------------------------------
        # Special routing variants must consume real basic transporters; the
        # stock iron-bar recipes otherwise bypass the logistics foundation.
        # --------------------------------------------------------------
        _compacting(
            recipe_id="industrial_colonies:mekanism_utility/restrictive_transporter",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=700,
            comment=(
                "Rebuild two real transporters with restrictive steel throats and "
                "heavy routing bodies instead of conjuring a network from iron bars."
            ),
            inputs=[
                "2x mekanism:basic_logistical_transporter",
                "2x minecraft:iron_bars",
                "2x tfmg:heavy_plate",
                "2x tfmg:steel_mechanism",
            ],
            output="2x mekanism:restrictive_transporter",
            stock_id="mekanism:transmitter/restrictive_transporter",
            depends_on=[
                "industrial_colonies:mekanism/transmission/basic_logistical_transporter"
            ],
        ),
        _compacting(
            recipe_id="industrial_colonies:mekanism_utility/diversion_transporter",
            node="CR01 — Reinforced Systems",
            phase="Mekanized Industry",
            order=710,
            comment=(
                "Instrument two real transporters with paired Redstone Links, TFMG "
                "transistors, insulated logic, and an advanced routing controller."
            ),
            inputs=[
                "2x mekanism:basic_logistical_transporter",
                "2x create:redstone_link",
                "2x tfmg:transistor_item",
                "2x tfmg:plastic_sheet",
                "mekanism:advanced_control_circuit",
            ],
            output="2x mekanism:diversion_transporter",
            stock_id="mekanism:transmitter/diversion_transporter",
            depends_on=[
                "industrial_colonies:mekanism/transmission/basic_logistical_transporter"
            ],
        ),

        # --------------------------------------------------------------
        # Thermal conversion.  Reusing the existing Create electrical heater
        # makes this an actual cross-mod escalation rather than a second ring.
        # --------------------------------------------------------------
        _sequence(
            recipe_id="industrial_colonies:mekanism_utility/resistive_heater",
            node="CR01 — Electrochemical Engineering",
            phase="Mekanized Industry",
            order=720,
            comment=(
                "Enclose the Create electrical heater core in a Mek steel body, then "
                "add a TFMG high-current coil, resistor bank, transformer, lithium "
                "buffer, and advanced thermal controller."
            ),
            input_item="electroenergetics:resistive_heater",
            ingredients=[
                "mekanism:steel_casing",
                "tfmg:large_coil",
                "2x tfmg:resistor",
                "tfmg:transformer",
                "tfmg:lithium_charge",
                "mekanism:advanced_control_circuit",
            ],
            deployer=INDUSTRIAL_DEPLOYER,
            press=INDUSTRIAL_PRESS,
            output="mekanism:resistive_heater",
            stock_id="mekanism:resistive_heater",
            depends_on=[
                "industrial_colonies:create_addons/resistive_heater",
                "industrial_colonies:mekanism/steel_casing",
            ],
        ),
    ]

    ids = [str(recipe["id"]) for recipe in recipes]
    outputs = [item for recipe in recipes for item in _recipe_output_items(recipe)]
    removals = [stock for recipe in recipes for stock in recipe.get("remove", [])]
    if len(ids) != len(set(ids)):
        raise ValueError("Mekanism utility wave defines duplicate recipe IDs")
    if len(outputs) != len(set(outputs)):
        raise ValueError("Mekanism utility wave defines duplicate outputs")
    if len(removals) != len(set(removals)):
        raise ValueError("Mekanism utility wave claims a stock recipe twice")
    forbidden = set(outputs).intersection(FORBIDDEN_OUTPUTS)
    if forbidden or any("factory" in output.split(":", 1)[-1] for output in outputs):
        raise AssertionError(
            f"Mekanism utility wave attempted to restore retired outputs: {sorted(forbidden)}"
        )
    if any(
        recipe.get("type") == "mechanical_crafting"
        and len(recipe.get("pattern", [])) == 5
        for recipe in recipes
    ):
        raise AssertionError("Mekanism utility wave must not introduce a 5x5 grid")
    return recipes


def _output_item(value: Any) -> str | None:
    if isinstance(value, str):
        return re.sub(r"^\d+x\s+", "", value.strip())
    if isinstance(value, Mapping):
        item = value.get("id") or value.get("item")
        return str(item) if isinstance(item, str) else None
    return None


def _recipe_output_items(recipe: Mapping[str, Any]) -> list[str]:
    result: list[str] = []
    if output := _output_item(recipe.get("output")):
        result.append(output)
    for field in ("results", "outputs"):
        values = recipe.get(field, [])
        if isinstance(values, list):
            for value in values:
                if output := _output_item(value):
                    result.append(output)
    return result


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed seed field {field!r} must be a list")
    return value


def _assert_unclaimed(data: dict[str, Any], additions: Iterable[Recipe]) -> None:
    additions = list(additions)
    addition_ids = {str(recipe["id"]) for recipe in additions}
    wanted_outputs = {
        output for recipe in additions for output in _recipe_output_items(recipe)
    }
    wanted_removals = {
        str(stock) for recipe in additions for stock in recipe.get("remove", [])
    }

    owned = wanted_outputs.intersection(_require_list(data, "user_owned_outputs"))
    if owned:
        raise ValueError(f"Mekanism utility wave cannot claim user-owned outputs: {sorted(owned)}")

    for existing in _require_list(data, "recipes"):
        if not isinstance(existing, dict):
            raise TypeError("managed recipe entries must be objects")
        if existing.get("id") in addition_ids:
            continue
        overlap_outputs = wanted_outputs.intersection(_recipe_output_items(existing))
        if overlap_outputs:
            raise ValueError(
                "Mekanism utility output is already managed by "
                f"{existing.get('id')}: {sorted(overlap_outputs)}"
            )
        overlap_removals = wanted_removals.intersection(existing.get("remove", []))
        if overlap_removals:
            raise ValueError(
                "Mekanism utility stock IDs are already claimed by "
                f"{existing.get('id')}: {sorted(overlap_removals)}"
            )


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = _require_list(data, "recipes")
    matches = [
        index
        for index, existing in enumerate(recipes)
        if isinstance(existing, dict) and existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"duplicate managed recipe before upsert: {recipe['id']}")
    if matches:
        recipes[matches[0]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def apply(data: dict[str, Any]) -> None:
    """Add thirteen utility recipes and close one exact tag-conversion bypass."""

    recipes = _recipes()
    _assert_unclaimed(data, recipes)

    claimed_stock_ids = {
        stock for recipe in recipes for stock in recipe.get("remove", [])
    }
    additional_removals = _require_list(data, "additional_removals")
    additional_removals[:] = [
        stock for stock in additional_removals if stock not in claimed_stock_ids
    ]
    for stock in sorted(NEW_RETIREMENTS):
        if stock not in additional_removals:
            additional_removals.append(stock)
    preserve_recipe_ids = _require_list(data, "preserve_recipe_ids")
    preserve_recipe_ids[:] = [
        stock for stock in preserve_recipe_ids if stock not in claimed_stock_ids
    ]

    managed_outputs = {
        output for recipe in recipes for output in _recipe_output_items(recipe)
    }
    exclude_outputs = _require_list(data, "exclude_outputs")
    exclude_outputs[:] = [
        output for output in exclude_outputs if output not in managed_outputs
    ]
    # The Oredictionificator has no safe recipe in this progression model; the
    # output guard prevents a future automatic policy from silently restoring
    # it while its exact stock recipe remains retired above.
    if "mekanism:oredictionificator" not in exclude_outputs:
        exclude_outputs.append("mekanism:oredictionificator")

    for recipe in recipes:
        _upsert(data, recipe)
