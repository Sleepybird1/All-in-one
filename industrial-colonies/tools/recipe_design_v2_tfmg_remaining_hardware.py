#!/usr/bin/env python3
"""Close the small number of real gaps in TFMG's remaining hardware.

The installed TFMG recipes were audited directly from ``tfmg-1.2.0.jar``.
Most of the remaining functional hardware is already well designed: tanks are
recognisable plated vessels, pumps and smart pipes are modest inline parts,
the air/exhaust stack family has a physical silhouette, switches contain
posts and contacts, coils and resistors use the Winding Machine, the
potentiometer is a lubricated sequenced assembly, and the large industrial
machines contain their appropriate casings and drives.  Those source recipes
must stay source-owned rather than becoming redundant managed cards.

Only the Simple Large Engine fails that test: it contains no cylinder, intake,
crankshaft, or gearbox.  The installed Empty Circuit Board recipe remains
source-owned by explicit user request.

This module gives those outputs manufacturing-shaped recipes and removes the
unrelated slime-ball shortcut into the otherwise coherent wound-resistor
chain.  ``apply`` is an idempotent, in-memory seed transform and performs no
filesystem, build, deployment, or runtime work.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


Recipe = dict[str, Any]


# Explicit negative-audit record.  These recipes are intentionally not copied
# into recipe design v2 because their installed source bodies already express
# their function and appropriate manufacturing cost.
AUDITED_SOURCE_OWNED: dict[str, str] = {
    "tfmg:crafting/materials/empty_circuit_board": (
        "The original TFMG substrate recipe is intentionally preserved; the "
        "user explicitly preferred it to a replacement lamination recipe."
    ),
    "tfmg:crafting/materials/accumulator": (
        "Lead plates, a lead storage block, copper conductors, two TFMG "
        "sulfuric-acid buckets, and an industrial aluminum casing form a "
        "complete lead-acid storage assembly."
    ),
    "tfmg:crafting/materials/accumulatorfrom_lithium": (
        "The alternate cell uses lithium stock, nickel plates, copper "
        "conductors, and the same industrial casing; it is not a cheap bypass."
    ),
    "tfmg:crafting/materials/air_intake": (
        "The shaft, propeller, geared housing, barred inlet, and cast-iron "
        "outlet already form a readable intake assembly."
    ),
    "tfmg:crafting/materials/exhaust": (
        "Iron-bar baffles are arranged around a cast-iron pipe and base."
    ),
    "tfmg:crafting/materials/flarestack": (
        "The exhaust stack adds steel support and an explicit ignition head."
    ),
    "tfmg:crafting/materials/aluminum_cable_hub": (
        "A modest conductor hub is already a material spine between two "
        "banks of canonical copper wire."
    ),
    "tfmg:crafting/materials/brass_cable_hub": (
        "A modest conductor hub is already a material spine between two "
        "banks of canonical copper wire."
    ),
    "tfmg:crafting/materials/copper_cable_hub": (
        "A modest conductor hub is already a material spine between two "
        "banks of canonical copper wire."
    ),
    "tfmg:crafting/materials/steel_casing_cable_hub": (
        "A steel casing pierced by two conductor banks is a coherent enclosed hub."
    ),
    "tfmg:crafting/materials/aluminum_fluid_tank": (
        "The early tank is intentionally a cheap barrel with aluminum endcaps."
    ),
    "tfmg:crafting/materials/cast_iron_fluid_tank": (
        "The early tank is intentionally a cheap barrel with cast-iron endcaps."
    ),
    "tfmg:crafting/materials/steel_fluid_tank": (
        "Two pressure-rated tanks from a barrel and two Heavy Plates is a "
        "sensible bulk-infrastructure ratio."
    ),
    "tfmg:crafting/materials/brass_mechanical_pump": (
        "A cogwheel installed inline on the matching pipe is appropriate for "
        "this small replaceable component."
    ),
    "tfmg:crafting/materials/aluminum_mechanical_pump": (
        "A cogwheel installed inline on the matching pipe is appropriate for "
        "this small replaceable component."
    ),
    "tfmg:crafting/materials/plastic_mechanical_pump": (
        "A cogwheel installed inline on the matching pipe is appropriate for "
        "this small replaceable component."
    ),
    "tfmg:crafting/materials/brass_smart_fluid_pipe": (
        "The pipe, sensing tube, and matching contact plate already form a "
        "small readable control fitting."
    ),
    "tfmg:crafting/materials/cast_iron_smart_fluid_pipe": (
        "The pipe, sensing tube, and matching contact plate already form a "
        "small readable control fitting."
    ),
    "tfmg:crafting/materials/coke_oven": (
        "This is a repeat-built multiblock part, so the compact cast-iron shell "
        "around industrial iron is appropriately inexpensive."
    ),
    "tfmg:crafting/materials/firebox": (
        "Fireproof brick, a fuel tank, and a full brass distribution manifold "
        "already describe the machine."
    ),
    "tfmg:crafting/materials/converter": (
        "The source body is a transformer between copper input, lead shielding, "
        "and redstone output columns."
    ),
    "tfmg:crafting/materials/crankshaft": (
        "Alternating rebar journals and aluminum counterweights provide a clear, "
        "modest engine component."
    ),
    "tfmg:crafting/materials/transmission": (
        "The aluminum shell, cog pair, plastic clutch layer, and three Steel "
        "Mechanisms already make a substantial transmission."
    ),
    "tfmg:crafting/materials/engine_gearbox": (
        "The casing, crossed shafting, Steel Mechanism, and service screws form "
        "a compact but complete gearbox."
    ),
    "tfmg:engine_cylinder_cheap": (
        "The starter cylinder is deliberately crude: an iron shell and reusable "
        "igniter are suitable before precision engine manufacture."
    ),
    "tfmg:crafting/materials/electric_diode": (
        "The installed high-current diode already uses P/N semiconductors, "
        "copper leads, plate cooling, and a heavy enclosure."
    ),
    "tfmg:crafting/materials/electrical_switch": (
        "Paired posts and lead contacts surround the heavy switch enclosure."
    ),
    "tfmg:crafting/materials/large_switch": (
        "The large switch already combines the cable hub, posts, connectors, "
        "steel linkage, and a brass contact blade asymmetrically."
    ),
    "tfmg:winding/electromagnetic_coil": (
        "The magnetic-alloy core is wound on TFMG's dedicated Winding Machine."
    ),
    "tfmg:winding/large_coil": (
        "The laminated magnetic block is wound on TFMG's dedicated Winding Machine."
    ),
    "tfmg:crafting/materials/industrial_mixer": (
        "The mixer has a heavy casing, shaft, large gear, twin Steel Mechanisms, "
        "and service screws without an arbitrary ingredient ring."
    ),
    "tfmg:crafting/materials/mixer_blade": (
        "A long shaft ending in a Heavy-Plate-reinforced propeller is a clear blade."
    ),
    "tfmg:crafting/materials/oil_hammer": (
        "The handheld survey hammer is deliberately modest and physically shaped; "
        "it must not regain precision electronics."
    ),
    "tfmg:sequenced_assembly/potentiometer": (
        "Three winding, gearing, wiring, and lubrication loops already make this "
        "one of TFMG's strongest source recipes."
    ),
    "tfmg:crafting/materials/unfinished_resistor": (
        "A plastic dielectric between copper terminals is a good modest blank "
        "before dedicated constantan winding."
    ),
    "tfmg:winding/resistor": (
        "The finished passive is correctly produced by winding constantan onto "
        "the prepared plastic-and-copper blank."
    ),
    "tfmg:mechanical_crafting/stator": (
        "The four-by-four stator visibly grows around electromagnetic coils, "
        "magnets, steel mass, aluminum support, and copper leads."
    ),
    "tfmg:mechanical_crafting/large_engine": (
        "The six-row engine already has a pressure vessel, heavy casing, repeated "
        "Steel Mechanisms, aluminum body, and structural bed."
    ),
    "tfmg:turbine_blade": (
        "Eight iron plates around a shaft form the complete fuel-tagged turbine "
        "rotor; preserving source ownership also preserves its data components."
    ),
    "tfmg:crafting/materials/winding_machine": (
        "The winding spindle, heavy casing, plate, Steel Mechanism, and steel base "
        "are a compact but complete dedicated workstation."
    ),
}


_MANAGED_RECIPES: tuple[Recipe, ...] = (
    {
        "id": "industrial_colonies:tfmg_remaining/simple_large_engine",
        "node": "CR01 \u2014 Early Combusion Engines",
        "phase": "Steel & Petroleum",
        "order": 55,
        "type": "mechanical_crafting",
        "comment": (
            "Build the Simple Large Engine as a visible twin-cylinder head over "
            "its air manifold, paired cast-iron feeds, crankshaft, gearbox, "
            "output shaft, and a Heavy-Plate bed"
        ),
        "pattern": [
            " C C ",
            "P I P",
            "K G S",
            " HHH ",
        ],
        "key": {
            "C": "tfmg:simple_engine_cylinder",
            "P": "tfmg:cast_iron_pipe",
            "I": "tfmg:air_intake",
            "K": "tfmg:crankshaft",
            "G": "tfmg:engine_gearbox",
            "S": "create:shaft",
            "H": "tfmg:heavy_plate",
        },
        "output": "tfmg:simple_large_engine",
        "remove": ["tfmg:mechanical_crafting/simple_large_engine"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:tfmg_core/heavy_plate"],
    },
)


_OBSOLETE_MANAGED_IDS: frozenset[str] = frozenset(
    {"industrial_colonies:tfmg_remaining/empty_circuit_board"}
)

_RESTORED_STOCK_RECIPES: frozenset[str] = frozenset(
    {"tfmg:crafting/materials/empty_circuit_board"}
)


_RETIRED_BYPASSES: tuple[str, ...] = (
    # This alternate turns an ordinary slime ball into the prepared resistor
    # body and bypasses the pack's TFMG plastic manufacturing line.
    "tfmg:crafting/materials/unfinished_resistorfrom_slime",
)


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


def _item_id(value: Any) -> str | None:
    if isinstance(value, str):
        raw = value.strip()
        if "x " in raw and raw.split("x ", 1)[0].isdigit():
            return raw.split("x ", 1)[1]
        return raw
    if isinstance(value, dict):
        identifier = value.get("id") or value.get("item")
        return identifier if isinstance(identifier, str) else None
    return None


def _outputs(recipe: Recipe) -> set[str]:
    outputs: set[str] = set()
    primary = _item_id(recipe.get("output"))
    if primary:
        outputs.add(primary)
    for field in ("outputs", "results"):
        values = recipe.get(field, [])
        if isinstance(values, list):
            for value in values:
                identifier = _item_id(value)
                if identifier:
                    outputs.add(identifier)
    return outputs


def _assert_unclaimed(data: dict[str, Any]) -> None:
    owned_ids = {recipe["id"] for recipe in _MANAGED_RECIPES}
    wanted_outputs = {
        output for recipe in _MANAGED_RECIPES for output in _outputs(recipe)
    }
    conflicts: list[tuple[str, str]] = []
    for recipe in _require_list(data, "recipes"):
        if not isinstance(recipe, dict):
            raise TypeError("managed recipe entries must be objects")
        if recipe.get("id") in owned_ids:
            continue
        overlap = wanted_outputs.intersection(_outputs(recipe))
        for output in sorted(overlap):
            conflicts.append((output, str(recipe.get("id"))))
    if conflicts:
        rendered = ", ".join(
            f"{output} via {recipe_id}" for output, recipe_id in conflicts
        )
        raise ValueError(f"remaining TFMG hardware overlaps managed output: {rendered}")


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


def apply(data: dict[str, Any]) -> None:
    """Apply the remaining TFMG hardware corrections in memory."""

    recipes = _require_list(data, "recipes")
    recipes[:] = [
        recipe
        for recipe in recipes
        if not isinstance(recipe, dict)
        or recipe.get("id") not in _OBSOLETE_MANAGED_IDS
    ]

    _assert_unclaimed(data)
    for recipe in _MANAGED_RECIPES:
        _upsert(data, recipe)

    stock_replacements = {
        stock_id for recipe in _MANAGED_RECIPES for stock_id in recipe["remove"]
    }
    claimed_outputs = {
        output for recipe in _MANAGED_RECIPES for output in _outputs(recipe)
    }

    preserve = _require_list(data, "preserve_recipe_ids")
    preserve[:] = [
        recipe_id
        for recipe_id in preserve
        if recipe_id not in stock_replacements and recipe_id not in _RETIRED_BYPASSES
    ]
    _append_unique(preserve, sorted(_RESTORED_STOCK_RECIPES))

    additional_removals = _require_list(data, "additional_removals")
    additional_removals[:] = [
        recipe_id
        for recipe_id in additional_removals
        if recipe_id not in stock_replacements
        and recipe_id not in _RESTORED_STOCK_RECIPES
    ]
    _append_unique(additional_removals, _RETIRED_BYPASSES)

    exclude_outputs = _require_list(data, "exclude_outputs")
    exclude_outputs[:] = [
        output for output in exclude_outputs if output not in claimed_outputs
    ]
