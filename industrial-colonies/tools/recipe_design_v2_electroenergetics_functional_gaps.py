#!/usr/bin/env python3
"""Close weak Create Electro Energetics functional-hardware routes.

This module is deliberately narrower than a blanket mod rewrite.  The
installed Electro Energetics recipes were audited as actual assemblies:

* the clamp meter, fuse, inductor, double/momentary/emergency switches,
  catenary holder, wire damper, and Lineman's Stick already communicate their
  construction well and remain stock;
* connector aggregation/deconstruction and motor dyeing are useful lossless
  state conversions and remain stock;
* the two panel meters become modes of one manufactured TFMG-first grid meter;
* the commutator, variac, railway collectors, and transformer radiator are
  rebuilt as recognizable electromechanical assemblies.

Duplicate loose components, including the inductor bridge and canonical
coloured-motor adapter, belong to ``recipe_design_v2_tfmg_duplicate_canonicalization``
and are intentionally not claimed here.

``apply`` is an idempotent, in-memory seed transform.  Importing this module
does not write files, inspect a running game, or modify the live instance.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Iterable, Mapping


Recipe = dict[str, Any]

COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")

def _deploy(ingredient: str) -> dict[str, str]:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": COPPER_DEPLOYER,
    }


def _press() -> dict[str, str]:
    return {"op": "pressing", "machine": COPPER_PRESS}


def _sequence(
    recipe_id: str,
    *,
    order: int,
    node: str,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    remove: list[str],
    loops: int = 1,
) -> Recipe:
    return {
        "id": recipe_id,
        "phase": "Electrical Manufacturing",
        "node": node,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": loops,
        "steps": [_deploy(ingredient) for ingredient in ingredients] + [_press()],
        "remove": remove,
        "exclusive_output": True,
    }


_MANAGED_RECIPES: tuple[Recipe, ...] = (
    _sequence(
        "industrial_colonies:electroenergetics/grid_meter",
        order=260,
        node="CR01 — Control Electronics",
        comment=(
            "Package the proven TFMG Multimeter as a panel instrument with a "
            "grid terminal, insulated enclosure, copper sensing lead, and "
            "protected dial; the stock one-item conversion selects current or "
            "voltage mode"
        ),
        input_item="tfmg:multimeter",
        output="electroenergetics:ammeter",
        ingredients=[
            "electroenergetics:connector",
            "tfmg:plastic_sheet",
            "tfmg:copper_wire",
            "minecraft:glass_pane",
        ],
        remove=["electroenergetics:crafting/ammeter"],
    ),
    _sequence(
        "industrial_colonies:electroenergetics/commutator",
        order=263,
        node="CR01 — Electronics Manufacturing",
        comment=(
            "Build two insulated copper commutator sectors around a shaft, "
            "fastening and pressing each sector on the Copper motor line"
        ),
        input_item="create:shaft",
        output="electroenergetics:commutator",
        ingredients=[
            "create:copper_sheet",
            "tfmg:plastic_sheet",
            "tfmg:screw",
        ],
        remove=["electroenergetics:crafting/commutator"],
        loops=2,
    ),
    _sequence(
        "industrial_colonies:electroenergetics/variac",
        order=283,
        node="CR01 — Grid Engineering",
        comment=(
            "Convert the canonical TFMG Transformer into a variable "
            "autotransformer with a geared wiper, potentiometer, secondary "
            "copper winding, grid terminal, and serviceable resistor"
        ),
        input_item="tfmg:transformer",
        output="electroenergetics:variac",
        ingredients=[
            "create:shaft",
            "tfmg:potentiometer",
            "tfmg:copper_spool",
            "electroenergetics:connector",
            "tfmg:resistor",
        ],
        remove=["electroenergetics:crafting/variac"],
    ),
    {
        "id": "industrial_colonies:electroenergetics/pantograph",
        "phase": "Electrical Manufacturing",
        "node": "CR01 — Grid Engineering",
        "order": 284,
        "type": "mechanical_crafting",
        "comment": (
            "Arrange the overhead collector as a terminal-tipped steel-truss "
            "scissor frame on an insulated, serviceable hinge base"
        ),
        "pattern": [" C ", "T T", "RMR"],
        "key": {
            "C": "electroenergetics:connector",
            "T": "tfmg:steel_truss",
            "R": "tfmg:rubber_sheet",
            "M": "tfmg:steel_mechanism",
        },
        "output": "electroenergetics:pantograph",
        "remove": ["electroenergetics:crafting/pantograph"],
        "exclusive_output": True,
    },
    {
        "id": "industrial_colonies:electroenergetics/rail_contact_shoe",
        "phase": "Electrical Manufacturing",
        "node": "CR01 — Grid Engineering",
        "order": 285,
        "type": "mechanical_crafting",
        "comment": (
            "Build the third-rail pickup from a rubber-isolated mechanism, "
            "hinged heavy-steel carrier, and broad copper contact shoe"
        ),
        "pattern": ["RMR", "HSH", "CCC"],
        "key": {
            "R": "tfmg:rubber_sheet",
            "M": "tfmg:steel_mechanism",
            "H": "tfmg:heavy_plate",
            "S": "create:shaft",
            "C": "create:copper_sheet",
        },
        "output": "electroenergetics:rail_contact_shoe",
        "remove": ["electroenergetics:crafting/rail_contact_shoe"],
        "exclusive_output": True,
    },
    {
        "id": "industrial_colonies:electroenergetics/radiator_panel_batch",
        "phase": "Electrical Manufacturing",
        "node": "CR01 — Grid Engineering",
        "order": 286,
        "type": "mechanical_crafting",
        "comment": (
            "Fabricate four transformer radiator faces as aluminum fins and "
            "oil channels braced around a steel truss with copper heat spreaders"
        ),
        "pattern": ["APA", "STS", "APA"],
        "key": {
            "A": "tfmg:aluminum_sheet",
            "P": "tfmg:aluminum_pipe",
            "S": "create:copper_sheet",
            "T": "tfmg:steel_truss",
        },
        "output": "4x electroenergetics:radiator_panel",
        "remove": ["electroenergetics:crafting/radiator_panel"],
        "exclusive_output": True,
    },
)


# The direct stock Voltmeter is the second raw-component shortcut.  The two
# one-for-one recipes below remain as a reversible meter-mode conversion.
_OTHER_RETIREMENTS: frozenset[str] = frozenset(
    {"electroenergetics:crafting/voltmeter"}
)

_PRESERVED_STOCK_RECIPES: frozenset[str] = frozenset(
    {
        # Lossless connector topology conversions.
        "electroenergetics:crafting/double_connector",
        "electroenergetics:crafting/triple_connector",
        "electroenergetics:crafting/quad_connector",
        "electroenergetics:crafting/quad_connector_from_double",
        "electroenergetics:crafting/connector_from_double",
        "electroenergetics:crafting/connector_from_triple",
        "electroenergetics:crafting/connector_from_quad",
        # Reversible Ammeter/Voltmeter operating modes.
        "electroenergetics:crafting/ammeter_from_voltmeter",
        "electroenergetics:crafting/voltmeter_from_ammeter",
        # Coherent small instruments, protection, and control hardware.
        "electroenergetics:crafting/clamp_meter",
        "electroenergetics:crafting/fuse",
        "electroenergetics:crafting/redstone_variac",
        "electroenergetics:crafting/double_switch",
        "electroenergetics:crafting/momentary_switch",
        "electroenergetics:crafting/emergency_stop_button",
        # Coherent structural/utility recipes; the damper is decorative.
        "electroenergetics:crafting/catenary_holder",
        "electroenergetics:crafting/wire_damper",
        "electroenergetics:mechanical_crafting/linemans_stick",
    }
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
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(1) if match else value.strip()


def _outputs(recipe: Mapping[str, Any]) -> set[str]:
    output = _item_id(recipe.get("output"))
    return {output} if output else set()


def _assert_unclaimed(data: dict[str, Any]) -> None:
    owned_ids = {recipe["id"] for recipe in _MANAGED_RECIPES}
    wanted_outputs = {
        output
        for recipe in _MANAGED_RECIPES
        for output in _outputs(recipe)
    }
    wanted_removals = {
        stock_id
        for recipe in _MANAGED_RECIPES
        for stock_id in recipe.get("remove", [])
    }
    conflicts: list[str] = []
    for recipe in _require_list(data, "recipes"):
        if not isinstance(recipe, dict):
            raise TypeError("managed recipe entries must be objects")
        if recipe.get("id") in owned_ids:
            continue
        overlap = _outputs(recipe) & wanted_outputs
        if overlap:
            conflicts.append(
                f"{recipe.get('id')} already owns {', '.join(sorted(overlap))}"
            )
        stock_overlap = set(recipe.get("remove", [])) & wanted_removals
        if stock_overlap:
            conflicts.append(
                f"{recipe.get('id')} already removes {', '.join(sorted(stock_overlap))}"
            )
    if conflicts:
        raise ValueError("Electro Energetics coverage conflict: " + "; ".join(conflicts))


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
    """Apply the focused functional-hardware gap closure in place."""

    _assert_unclaimed(data)
    for recipe in _MANAGED_RECIPES:
        _upsert(data, recipe)

    managed_stock_ids = {
        stock_id
        for recipe in _MANAGED_RECIPES
        for stock_id in recipe.get("remove", [])
    }
    retired_stock_ids = _OTHER_RETIREMENTS

    preserve_recipe_ids = _require_list(data, "preserve_recipe_ids")
    preserve_recipe_ids[:] = [
        recipe_id
        for recipe_id in preserve_recipe_ids
        if recipe_id not in managed_stock_ids | retired_stock_ids
    ]
    _append_unique(preserve_recipe_ids, sorted(_PRESERVED_STOCK_RECIPES))

    additional_removals = _require_list(data, "additional_removals")
    # Managed recipes own their replaced stock IDs locally.  The global list
    # only retires the second direct panel-meter shortcut.
    additional_removals[:] = [
        recipe_id
        for recipe_id in additional_removals
        if recipe_id not in managed_stock_ids
    ]
    _append_unique(additional_removals, sorted(retired_stock_ids))
