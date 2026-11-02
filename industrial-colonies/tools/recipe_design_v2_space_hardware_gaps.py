#!/usr/bin/env python3
"""Close the remaining high-confidence space-hardware recipe gaps.

The broader space wave already owns propulsion, habitat machinery, station
materials, navigation, rovers, and the final Cosmowarp chain.  This transform
is intentionally small: it only replaces six stock routes that are either
currently unobtainable behind the exact deferred boundary or materially break
the manufacturing language established by that wave.

Installed-catalog findings represented here:

* Cosmonautics' anchor boots and leg thrusters are still in the exact deferred
  list and have no managed replacement, despite the managed jetpack existing.
* the Etrionic Capacitor is only steel plates, Diamond, and Redstone, yet it is
  consumed by three managed planetary machines/garments;
* the Photovoltaic Etrium Cell omits silicon, conductors, and electronics even
  though thirteen cells are used by one managed solar-panel batch; and
* the managed Steel -> Desh engine ladder falls back to two very small stock
  upgrades for Ostrum and Calorite.

Audited exclusions (deliberately unchanged):

* Ad Astra NASA workbenches, launch pads, prefab rockets/stations, and the fuel
  refinery remain deferred.  Block-built Cosmonautics ships and canonical TFMG
  kerosene own the flight path; an empty duplicate refinery is not a gap.
* the normal Ad Astra space suit and Jet Suit recipes are coherent upgrades
  using pressure gear, Netherite suit pieces, Calorite hardware, and the engine
  ladder hardened here.  They are not rewritten merely to increase counts.
* Aeronautics' burner, bearing, propeller, and smart-propeller recipes are
  coherent mechanical assemblies; the sophisticated gyroscopic bearing is
  already managed by ``recipe_design_v2_space_coverage``.  Envelopes and their
  encased-shaft states are structural/color variants, not separate tech gates.
* Rocketnautics' nozzles, titanium sheets/alloys/casing, and common parts retain
  their coherent material-processing routes.  The Expansion add-on contributes
  planetary ores/materials but no additional registered functional hardware.
* Cosmowarp memory, driver, route crystal, and drive are already managed in the
  final Interstellar Escape phase.  Moon Crystal remains an exploration feed;
  no earlier warp or teleport route is introduced here.
* redundant generators, hand tools, weapons, food, ores, buckets, decorative
  blocks, and state variants belong outside this focused hardware audit.

``apply`` is a pure, idempotent dictionary transform.  It does not write the
seed, generate KJSGen files, build the mod, deploy, or launch Minecraft.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Iterable


Recipe = dict[str, Any]


# Exact installed producer evidence from recipe-catalog-current.  Keeping this
# map beside the authored routes makes output ownership and removal reviewable.
CATALOG_STOCK_PRODUCERS: dict[str, tuple[str, ...]] = {
    "rocketnautics:copper_anchor_boots": (
        "rocketnautics:crafting/equipment/copper_anchor_boots",
    ),
    "rocketnautics:copper_leg_thrusters": (
        "rocketnautics:crafting/equipment/copper_leg_thrusters",
    ),
    "ad_astra:etrionic_capacitor": ("ad_astra:etrionic_capacitor",),
    "ad_astra:photovoltaic_etrium_cell": (
        "ad_astra:photovoltaic_etrium_cell",
    ),
    "ad_astra:ostrum_engine": ("ad_astra:ostrum_engine",),
    "ad_astra:calorite_engine": ("ad_astra:calorite_engine",),
}


def _deploy(ingredient: str, casing: str) -> Recipe:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": f"createcasing:{casing}_deployer",
    }


def _press(casing: str) -> Recipe:
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
    stock_ids: tuple[str, ...],
    depends_on: list[str],
    loops: int = 1,
) -> Recipe:
    if not ingredients or len(ingredients) > 5:
        raise ValueError(
            f"space-hardware sequences require one to five deployments: {recipe_id}"
        )
    if loops not in {1, 2}:
        raise ValueError(f"unreviewed sequence loop count for {recipe_id}: {loops}")
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
        "loops": loops,
        "steps": [_deploy(ingredient, casing) for ingredient in ingredients]
        + [_press(casing)],
        "remove": list(stock_ids),
        "exclusive_output": True,
        "depends_on": list(depends_on),
    }


def _recipes() -> list[Recipe]:
    recipes = [
        _sequence(
            recipe_id="industrial_colonies:space_hardware/copper_anchor_boots",
            node="CR02 — Pressure Hardware",
            phase="Orbital Engineering",
            order=232,
            comment=(
                "Laminate an iron boot shell with rubber soles, magnetic-alloy "
                "anchors, titanium-alloy reinforcement, and copper grounding"
            ),
            input_item="minecraft:iron_boots",
            output="rocketnautics:copper_anchor_boots",
            ingredients=[
                "tfmg:rubber_sheet",
                "tfmg:magnetic_alloy_sheet",
                "rocketnautics:titanium_alloy_sheet",
                "create:copper_sheet",
            ],
            casing="copper",
            stock_ids=CATALOG_STOCK_PRODUCERS[
                "rocketnautics:copper_anchor_boots"
            ],
            depends_on=["industrial_colonies:space/life_support/airlock"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_hardware/copper_leg_thrusters",
            node="CR02 — Modular Propulsion",
            phase="Orbital Engineering",
            order=233,
            comment=(
                "Plumb two copper nozzles around a propellant anchor and electric "
                "metering pump, then seal the leg harness with TFMG rubber"
            ),
            input_item="minecraft:iron_leggings",
            output="rocketnautics:copper_leg_thrusters",
            ingredients=[
                "rocketnautics:copper_nozzle",
                "rocketnautics:hose_anchor",
                "tfmg:electric_pump",
                "rocketnautics:copper_nozzle",
                "tfmg:rubber_sheet",
            ],
            casing="copper",
            stock_ids=CATALOG_STOCK_PRODUCERS[
                "rocketnautics:copper_leg_thrusters"
            ],
            depends_on=["industrial_colonies:space/propulsion/hose_anchor"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_hardware/etrionic_capacitor",
            node="CR02 — Lunar Metallurgy",
            phase="Planetary Industry",
            order=85,
            comment=(
                "Rehouse a TFMG capacitor as a lithium-buffered Desh power cell "
                "with transistor regulation, diamond dielectric, and plastic isolation"
            ),
            input_item="tfmg:capacitor_item",
            output="ad_astra:etrionic_capacitor",
            ingredients=[
                "mekanism:dust_lithium",
                "tfmg:transistor_item",
                "ad_astra:desh_plate",
                "minecraft:diamond",
                "tfmg:plastic_sheet",
            ],
            casing="refined_radiance",
            stock_ids=CATALOG_STOCK_PRODUCERS["ad_astra:etrionic_capacitor"],
            depends_on=["industrial_colonies:planetary/desh/plate"],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_hardware/photovoltaic_etrium_cell",
            node="CR02 — Lunar Metallurgy",
            phase="Planetary Industry",
            order=86,
            comment=(
                "Print two photovoltaic wafers from TFMG silicon with copper "
                "collection traces, transistor control, Desh backing, and blue glass"
            ),
            input_item="tfmg:silicon_ingot",
            output="2x ad_astra:photovoltaic_etrium_cell",
            ingredients=[
                "tfmg:copper_wire",
                "tfmg:transistor_item",
                "ad_astra:desh_plate",
                "minecraft:blue_stained_glass",
            ],
            casing="refined_radiance",
            stock_ids=CATALOG_STOCK_PRODUCERS[
                "ad_astra:photovoltaic_etrium_cell"
            ],
            depends_on=["industrial_colonies:planetary/desh/plate"],
            loops=2,
        ),
        _sequence(
            recipe_id="industrial_colonies:space_hardware/ostrum_engine",
            node="CR02 — Martian Metallurgy",
            phase="Planetary Industry",
            order=153,
            comment=(
                "Refit the lunar engine with paired Ostrum hot-section shells, a "
                "fresh circulation fan, magnetic bracing, and ultimate regulation"
            ),
            input_item="ad_astra:desh_engine",
            output="ad_astra:ostrum_engine",
            ingredients=[
                "ad_astra:ostrum_plate",
                "ad_astra:fan",
                "tfmg:magnetic_alloy_sheet",
                "mekanism:ultimate_control_circuit",
                "ad_astra:ostrum_plate",
            ],
            casing="refined_radiance",
            stock_ids=CATALOG_STOCK_PRODUCERS["ad_astra:ostrum_engine"],
            depends_on=[
                "industrial_colonies:space_coverage/desh_engine",
                "industrial_colonies:planetary/ostrum/plate",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:space_hardware/calorite_engine",
            node="CR02 — Calorite Metallurgy",
            phase="Planetary Industry",
            order=302,
            comment=(
                "Rebuild the Martian engine's hot section with paired Calorite "
                "shells, a titanium nozzle, turbine blade, and magnetic stabilizer"
            ),
            input_item="ad_astra:ostrum_engine",
            output="ad_astra:calorite_engine",
            ingredients=[
                "ad_astra:calorite_plate",
                "rocketnautics:titanium_nozzle",
                "tfmg:turbine_blade",
                "rocketnautics:magnetic_stabilizer",
                "ad_astra:calorite_plate",
            ],
            casing="refined_radiance",
            stock_ids=CATALOG_STOCK_PRODUCERS["ad_astra:calorite_engine"],
            depends_on=[
                "industrial_colonies:space_hardware/ostrum_engine",
                "industrial_colonies:planetary/calorite/plate",
                "industrial_colonies:space_coverage/magnetic_stabilizer",
            ],
        ),
    ]

    ids = [str(recipe["id"]) for recipe in recipes]
    outputs = [_output_item(recipe.get("output")) for recipe in recipes]
    removals = [
        stock_id
        for recipe in recipes
        for stock_id in recipe.get("remove", [])
    ]
    if len(ids) != len(set(ids)):
        raise ValueError("space-hardware gaps define duplicate managed recipe IDs")
    if None in outputs or len(outputs) != len(set(outputs)):
        raise ValueError("space-hardware gaps define invalid or duplicate outputs")
    if len(removals) != len(set(removals)):
        raise ValueError("space-hardware gaps define duplicate stock removals")
    return recipes


def _output_item(output: Any) -> str | None:
    if not isinstance(output, str):
        return None
    value = re.sub(r"^\s*\d+x\s+", "", output.strip())
    return value if ":" in value else None


def _declared_outputs(recipe: Recipe) -> set[str]:
    output = _output_item(recipe.get("output"))
    return {output} if output else set()


def _assert_unclaimed(data: dict[str, Any], recipes: Iterable[Recipe]) -> None:
    recipes = list(recipes)
    owned_ids = {recipe["id"] for recipe in recipes}
    wanted_outputs = {
        output for recipe in recipes for output in _declared_outputs(recipe)
    }
    wanted_removals = {
        stock_id
        for recipe in recipes
        for stock_id in recipe.get("remove", [])
    }
    for existing in data.get("recipes", []):
        if not isinstance(existing, dict):
            raise TypeError("managed recipe entries must be objects")
        if existing.get("id") in owned_ids:
            continue
        output_overlap = wanted_outputs & _declared_outputs(existing)
        if output_overlap:
            raise ValueError(
                "space-hardware output is already managed by "
                f"{existing.get('id')}: {sorted(output_overlap)}"
            )
        removal_overlap = wanted_removals & set(existing.get("remove", []))
        if removal_overlap:
            raise ValueError(
                "space-hardware stock ID is already claimed by "
                f"{existing.get('id')}: {sorted(removal_overlap)}"
            )


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = data.setdefault("recipes", [])
    matches = [
        index
        for index, existing in enumerate(recipes)
        if isinstance(existing, dict) and existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"managed recipe is duplicated: {recipe['id']}")
    if matches:
        recipes[matches[0]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def apply(data: dict[str, Any]) -> None:
    """Apply the six reviewed space-hardware replacements in place."""

    recipes = _recipes()
    _assert_unclaimed(data, recipes)

    claimed_stock_ids = {
        stock_id
        for recipe in recipes
        for stock_id in recipe.get("remove", [])
    }
    managed_outputs = {
        output for recipe in recipes for output in _declared_outputs(recipe)
    }
    data["preserve_recipe_ids"] = [
        stock_id
        for stock_id in data.get("preserve_recipe_ids", [])
        if stock_id not in claimed_stock_ids
    ]
    data["additional_removals"] = [
        stock_id
        for stock_id in data.get("additional_removals", [])
        if stock_id not in claimed_stock_ids
    ]
    data["exclude_outputs"] = [
        output
        for output in data.get("exclude_outputs", [])
        if output not in managed_outputs
    ]

    for recipe in recipes:
        _upsert(data, recipe)
