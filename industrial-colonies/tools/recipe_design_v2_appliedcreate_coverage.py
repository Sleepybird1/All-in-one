"""AppliedCreate stress-storage and Create Applied Kinetics coverage.

The stock stress-storage ladder is a chain of ordinary shaped and shapeless
recipes.  This module turns it into two readable manufacturing operations:

* a progressively populated stress-storage component; and
* a separately sealed, reusable cell housing.

Small k-tier matrices stay on the Brass precision line, high-capacity k/1M
matrices move to Weathered Iron, and nuclear-scale matrices use Refined
Radiance tooling.  Create Applied Kinetics' two functional network blocks are
included, while its cosmetic/convenience conversions and AppliedCreate's
pattern-provider block/part conversions are deliberately left alone.

Importing this module has no filesystem or seed side effects.  ``apply`` is
idempotent and mutates only the supplied seed dictionary.
"""

from __future__ import annotations

import re
from typing import Any


BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"

UNFINISHED_STRESS_COMPONENT = (
    "industrial_colonies:unfinished_stress_storage_component"
)

HIGH_ENERGY = "High-Energy Grid"
NUCLEAR = "Nuclear Engineering"
POST_NUCLEAR = "Post-Nuclear Megaprojects"

STORAGE_NODE = "CR01 — Advanced ME Storage"
NETWORK_NODE = "CR01 — Advanced ME BUS Technology"
GRID_NODE = "CR01 — High-Energy Distribution"
NUCLEAR_NODE = "CR01 — Core Engineering"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    if isinstance(value, dict):
        item_id = value.get("id")
        return item_id if isinstance(item_id, str) else None
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(1) if match else value.strip()


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _grid(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    remove: str,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    widths = {len(row) for row in pattern}
    if len(widths) != 1:
        raise ValueError(f"{recipe_id} has a ragged crafting pattern")
    used = {symbol for row in pattern for symbol in row if symbol != " "}
    if used != set(key):
        raise ValueError(
            f"{recipe_id} pattern/key mismatch: used={sorted(used)}, "
            f"key={sorted(key)}"
        )

    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": [remove],
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _sequence(
    recipe_id: str,
    *,
    phase: str,
    node: str | None,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    deployer: str,
    press: str,
    remove: str,
    transitional: str = UNFINISHED_STRESS_COMPONENT,
    loops: int = 1,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional,
        "output": output,
        "loops": loops,
        "steps": [_deploy(item, deployer) for item in ingredients]
        + [_press(press)],
        "remove": [remove],
        "exclusive_output": True,
    }
    if node is not None:
        recipe["node"] = node
    if depends_on:
        recipe["depends_on"] = list(depends_on)
    return recipe


def _compacting(
    recipe_id: str,
    *,
    phase: str,
    node: str | None,
    order: int,
    comment: str,
    machine: str,
    inputs: list[str],
    output: str,
    remove: str,
    depends_on: list[str],
) -> dict[str, Any]:
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": inputs,
        "output": output,
        "remove": [remove],
        "exclusive_output": True,
        "depends_on": list(depends_on),
    }
    if node is not None:
        recipe["node"] = node
    return recipe


def _component_id(tier: str) -> str:
    return f"industrial_colonies:appliedcreate/stress_storage_component_{tier}"


def _cell_id(tier: str) -> str:
    return f"industrial_colonies:appliedcreate/stress_storage_cell_{tier}"


def _stock_component(tier: str) -> str:
    return f"appliedcreate:stress_storage_component_{tier}"


def _stock_cell(tier: str) -> str:
    return f"appliedcreate:stress_storage_cell_{tier}"


def _recipes() -> list[dict[str, Any]]:
    recipes: list[dict[str, Any]] = [
        # The housings are physical frames, not processor recipes.  Their open
        # silhouettes make the inner AE housing and sealing glass visible.
        _grid(
            "industrial_colonies:appliedcreate/andesite_stress_cell_housing",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=610,
            comment=(
                "Brace an ordinary ME cell housing with an Andesite frame, "
                "quartz windows, and cinder packing"
            ),
            pattern=["QGQ", "ACA", "QGQ"],
            key={
                "Q": "ae2:quartz_glass",
                "G": "create:cinder_flour",
                "A": "create:andesite_alloy",
                "C": "ae2:item_cell_housing",
            },
            output="appliedcreate:andesite_stress_cell_housing",
            remove="appliedcreate:andesite_stress_cell_housing",
        ),
        _grid(
            "industrial_colonies:appliedcreate/brass_stress_cell_housing",
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=611,
            comment=(
                "Rebuild the Andesite frame as a Brass precision enclosure "
                "with vibrant windows and magnetic side shielding"
            ),
            pattern=["BVB", "MHM", "BVB"],
            key={
                "B": "create:brass_sheet",
                "V": "ae2:quartz_vibrant_glass",
                "M": "tfmg:magnetic_alloy_sheet",
                "H": "appliedcreate:andesite_stress_cell_housing",
            },
            output="appliedcreate:brass_stress_cell_housing",
            remove="appliedcreate:brass_stress_cell_housing",
            depends_on=[
                "industrial_colonies:appliedcreate/andesite_stress_cell_housing"
            ],
        ),
        # Preserve the existing 1k design as the recognizable first matrix.
        _sequence(
            _component_id("1k"),
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=620,
            comment=(
                "Wind and populate a buffered stress matrix over two "
                "recognizable Brass electronics passes"
            ),
            input_item="ae2:cell_component_4k",
            output=_stock_component("1k"),
            ingredients=[
                "appliedcreate:stress_processor",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
                "tfmg:magnetic_alloy_sheet",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove=_stock_component("1k"),
            loops=2,
            depends_on=["industrial_colonies:electronics/stress_processor"],
        ),
        _sequence(
            _component_id("4k"),
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=621,
            comment=(
                "Expand the first stress matrix around a 4k ME plane, local "
                "capacitance, and a vibrant quartz data face"
            ),
            input_item=_stock_component("1k"),
            output=_stock_component("4k"),
            ingredients=[
                "ae2:cell_component_4k",
                "appliedcreate:stress_processor",
                "tfmg:capacitor_item",
                "ae2:quartz_vibrant_glass",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove=_stock_component("4k"),
            depends_on=[_component_id("1k")],
        ),
        _sequence(
            _component_id("16k"),
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=622,
            comment=(
                "Add a 16k ME plane to the prior matrix, then route and shield "
                "its expanded Brass-line address bus"
            ),
            input_item=_stock_component("4k"),
            output=_stock_component("16k"),
            ingredients=[
                "ae2:cell_component_16k",
                "appliedcreate:stress_processor",
                "tfmg:copper_wire",
                "tfmg:magnetic_alloy_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            remove=_stock_component("16k"),
            depends_on=[_component_id("4k")],
        ),
        _sequence(
            _component_id("64k"),
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=623,
            comment=(
                "Repackage the 16k matrix with a 64k memory plane, paired "
                "buffers, elastic isolation, and magnetic shielding"
            ),
            input_item=_stock_component("16k"),
            output=_stock_component("64k"),
            ingredients=[
                "ae2:cell_component_64k",
                "appliedcreate:stress_processor",
                "2x tfmg:capacitor_item",
                "tfmg:rubber_sheet",
                "tfmg:magnetic_alloy_sheet",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            remove=_stock_component("64k"),
            depends_on=[_component_id("16k")],
        ),
        _sequence(
            _component_id("256k"),
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=624,
            comment=(
                "Address a 256k ME plane through accumulation logic, then "
                "laminate the enlarged stress matrix behind vibrant glass"
            ),
            input_item=_stock_component("64k"),
            output=_stock_component("256k"),
            ingredients=[
                "ae2:cell_component_256k",
                "appliedcreate:stress_processor",
                "megacells:accumulation_processor",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:quartz_vibrant_glass",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            remove=_stock_component("256k"),
            depends_on=[
                _component_id("64k"),
                "industrial_colonies:digital/accumulation_processor",
            ],
        ),
        _sequence(
            _component_id("1m"),
            phase=HIGH_ENERGY,
            node=STORAGE_NODE,
            order=625,
            comment=(
                "Integrate the first MEGA memory plane with advanced stress "
                "control, spatial addressing, and laminated containment"
            ),
            input_item=_stock_component("256k"),
            output=_stock_component("1m"),
            ingredients=[
                "megacells:cell_component_1m",
                "appliedcreate:advanced_stress_processor",
                "megacells:accumulation_processor",
                "ae2:spatial_cell_component_2",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            deployer=WEATHERED_DEPLOYER,
            press=WEATHERED_PRESS,
            remove=_stock_component("1m"),
            depends_on=[
                _component_id("256k"),
                "industrial_colonies:megacells/cell_component_1m",
                "industrial_colonies:electronics/advanced_stress_processor",
            ],
        ),
        # Nuclear-scale matrices require both their matching MEGA plane and
        # the complete prior stress component; capacity never appears ex nihilo.
        _sequence(
            _component_id("4m"),
            phase=NUCLEAR,
            node=NUCLEAR_NODE,
            order=700,
            comment=(
                "Couple a 4M MEGA plane to the 1M stress core with spatial "
                "addressing, matter isolation, and Refined Radiance contacts"
            ),
            input_item=_stock_component("1m"),
            output=_stock_component("4m"),
            ingredients=[
                "megacells:cell_component_4m",
                "appliedcreate:advanced_stress_processor",
                "ae2:spatial_cell_component_2",
                "ae2:matter_ball",
                "create:refined_radiance",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove=_stock_component("4m"),
            depends_on=[
                _component_id("1m"),
                "industrial_colonies:megacells_coverage/cell_component_4m",
            ],
        ),
        _sequence(
            _component_id("16m"),
            phase=NUCLEAR,
            node=NUCLEAR_NODE,
            order=701,
            comment=(
                "Schedule a 16M MEGA plane through concurrent control and a "
                "16-cubed spatial map before Radiance pressing"
            ),
            input_item=_stock_component("4m"),
            output=_stock_component("16m"),
            ingredients=[
                "megacells:cell_component_16m",
                "appliedcreate:advanced_stress_processor",
                "extendedae:concurrent_processor",
                "ae2:spatial_cell_component_16",
                "2x create:refined_radiance",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove=_stock_component("16m"),
            depends_on=[
                _component_id("4m"),
                "industrial_colonies:megacells_coverage/cell_component_16m",
                "industrial_colonies:extendedae_coverage/concurrent_processor",
            ],
        ),
        _sequence(
            _component_id("64m"),
            phase=NUCLEAR,
            node=NUCLEAR_NODE,
            order=702,
            comment=(
                "Bind a 64M MEGA plane to full-scale spatial addressing, "
                "accumulation control, and a laminated Radiance shield"
            ),
            input_item=_stock_component("16m"),
            output=_stock_component("64m"),
            ingredients=[
                "megacells:cell_component_64m",
                "megacells:accumulation_processor",
                "ae2:spatial_cell_component_128",
                "tfmg:laminated_magnetic_alloy_block",
                "create:refined_radiance",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove=_stock_component("64m"),
            depends_on=[
                _component_id("16m"),
                "industrial_colonies:megacells_coverage/cell_component_64m",
            ],
        ),
        _sequence(
            _component_id("256m"),
            phase=POST_NUCLEAR,
            node=None,
            order=800,
            comment=(
                "Finish the 256M stress core with its matching MEGA plane, "
                "ultimate control, exotic alloy contacts, and matter isolation"
            ),
            input_item=_stock_component("64m"),
            output=_stock_component("256m"),
            ingredients=[
                "megacells:cell_component_256m",
                "appliedcreate:advanced_stress_processor",
                "mekanism:ultimate_control_circuit",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
                "ae2:matter_ball",
            ],
            deployer=RADIANCE_DEPLOYER,
            press=RADIANCE_PRESS,
            remove=_stock_component("256m"),
            depends_on=[
                _component_id("64m"),
                "industrial_colonies:megacells_coverage/cell_component_256m",
                "industrial_colonies:mekanism/ultimate_control_circuit",
            ],
        ),
    ]

    # A finished stress cell is a component sealed inside a housing, so every
    # tier is compacted rather than treated as a machine assembly.
    cell_specs = [
        (
            "1k",
            HIGH_ENERGY,
            STORAGE_NODE,
            640,
            BRASS_PRESS,
            "appliedcreate:andesite_stress_cell_housing",
            ["tfmg:rubber_sheet", "ae2:quartz_glass"],
            "Seal the 1k matrix behind a rubber gasket and quartz service face",
        ),
        (
            "4k",
            HIGH_ENERGY,
            STORAGE_NODE,
            641,
            BRASS_PRESS,
            "appliedcreate:andesite_stress_cell_housing",
            ["tfmg:rubber_sheet", "tfmg:copper_wire"],
            "Seal the 4k matrix with an elastic gasket and a wired stress contact",
        ),
        (
            "16k",
            HIGH_ENERGY,
            STORAGE_NODE,
            642,
            BRASS_PRESS,
            "appliedcreate:andesite_stress_cell_housing",
            ["tfmg:plastic_sheet", "tfmg:capacitor_item"],
            "Encapsulate the 16k matrix with a plastic dielectric and local buffer",
        ),
        (
            "64k",
            HIGH_ENERGY,
            STORAGE_NODE,
            643,
            WEATHERED_PRESS,
            "appliedcreate:andesite_stress_cell_housing",
            ["tfmg:plastic_sheet", "tfmg:magnetic_alloy_sheet"],
            "Pressure-seal the 64k matrix behind dielectric and magnetic shielding",
        ),
        (
            "256k",
            HIGH_ENERGY,
            STORAGE_NODE,
            644,
            WEATHERED_PRESS,
            "appliedcreate:andesite_stress_cell_housing",
            ["tfmg:plastic_sheet", "ae2:quartz_vibrant_glass", "tfmg:capacitor_item"],
            "Close the 256k cell around a vibrant data face and buffered dielectric",
        ),
        (
            "1m",
            HIGH_ENERGY,
            STORAGE_NODE,
            645,
            WEATHERED_PRESS,
            "appliedcreate:brass_stress_cell_housing",
            ["tfmg:plastic_sheet", "tfmg:laminated_magnetic_alloy_block"],
            "Seal the first MEGA stress matrix inside a Brass and laminated shield",
        ),
        (
            "4m",
            NUCLEAR,
            NUCLEAR_NODE,
            720,
            RADIANCE_PRESS,
            "appliedcreate:brass_stress_cell_housing",
            ["tfmg:plastic_sheet", "create:refined_radiance"],
            "Radiance-seal the 4M matrix inside its Brass precision housing",
        ),
        (
            "16m",
            NUCLEAR,
            NUCLEAR_NODE,
            721,
            RADIANCE_PRESS,
            "appliedcreate:brass_stress_cell_housing",
            ["tfmg:plastic_sheet", "create:refined_radiance", "ae2:matter_ball"],
            "Isolate and Radiance-seal the 16M matrix against stress leakage",
        ),
        (
            "64m",
            NUCLEAR,
            NUCLEAR_NODE,
            722,
            RADIANCE_PRESS,
            "appliedcreate:brass_stress_cell_housing",
            ["tfmg:plastic_sheet", "2x create:refined_radiance", "ae2:matter_ball"],
            "Double-seal the 64M matrix with Radiance contacts and matter isolation",
        ),
        (
            "256m",
            POST_NUCLEAR,
            None,
            820,
            RADIANCE_PRESS,
            "appliedcreate:brass_stress_cell_housing",
            [
                "tfmg:plastic_sheet",
                "create:refined_radiance_casing",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
            ],
            "Close the 256M cell with a Radiance shell and exotic alloy bus",
        ),
    ]
    for tier, phase, node, order, machine, housing, seals, comment in cell_specs:
        housing_recipe = (
            "industrial_colonies:appliedcreate/brass_stress_cell_housing"
            if housing.endswith("brass_stress_cell_housing")
            else "industrial_colonies:appliedcreate/andesite_stress_cell_housing"
        )
        recipes.append(
            _compacting(
                _cell_id(tier),
                phase=phase,
                node=node,
                order=order,
                comment=comment,
                machine=machine,
                inputs=[housing, _stock_component(tier), *seals],
                output=_stock_cell(tier),
                remove=_stock_cell(tier),
                depends_on=[housing_recipe, _component_id(tier)],
            )
        )

    recipes.extend(
        [
            _sequence(
                "industrial_colonies:createappliedkinetics/energy_provider",
                phase=HIGH_ENERGY,
                node=GRID_NODE,
                order=660,
                comment=(
                    "Instrument the kinetic ME converter with a real generator, "
                    "transformer, energy buffer, and local capacitance"
                ),
                input_item="appliedcreate:kinetic_energy_acceptor",
                transitional="appliedcreate:kinetic_energy_acceptor",
                output="createappliedkinetics:energy_provider",
                ingredients=[
                    "tfmg:generator",
                    "tfmg:transformer",
                    "ae2:energy_cell",
                    "tfmg:capacitor_item",
                ],
                deployer=WEATHERED_DEPLOYER,
                press=WEATHERED_PRESS,
                remove="createappliedkinetics:energy_provider",
                depends_on=[
                    "industrial_colonies:appliedcreate/kinetic_energy_acceptor",
                    "industrial_colonies:tfmg_heavy_electrical/transformer",
                ],
            ),
            _sequence(
                "industrial_colonies:createappliedkinetics/me_proxy",
                phase=HIGH_ENERGY,
                node=NETWORK_NODE,
                order=661,
                comment=(
                    "Turn an ME interface into a bidirectional contraption proxy "
                    "with formation, annihilation, logic, and smart-cable control"
                ),
                input_item="ae2:interface",
                transitional="ae2:interface",
                output="createappliedkinetics:me_proxy",
                ingredients=[
                    "ae2:annihilation_core",
                    "ae2:formation_core",
                    "ae2:logic_processor",
                    "ae2:fluix_smart_cable",
                ],
                deployer=BRASS_DEPLOYER,
                press=BRASS_PRESS,
                remove="createappliedkinetics:me_proxy",
                depends_on=[
                    "industrial_colonies:digital_core/interface",
                    "industrial_colonies:ae2_coverage/annihilation_core_batch",
                    "industrial_colonies:ae2_coverage/formation_core_batch",
                ],
            ),
        ]
    )
    return recipes


def _assert_unclaimed(data: dict[str, Any], additions: list[dict[str, Any]]) -> None:
    addition_ids = {recipe["id"] for recipe in additions}
    wanted_outputs = {
        _item_id(recipe["output"]): recipe["id"]
        for recipe in additions
        if _item_id(recipe.get("output")) is not None
    }
    wanted_removals = {
        removal: recipe["id"]
        for recipe in additions
        for removal in recipe.get("remove", [])
    }

    for existing in data.get("recipes", []):
        if existing.get("id") in addition_ids:
            continue
        output = _item_id(existing.get("output"))
        if output in wanted_outputs:
            raise ValueError(
                f"{wanted_outputs[output]} cannot claim {output}; "
                f"it is already managed by {existing.get('id')}"
            )
        for removal in existing.get("remove", []):
            if removal in wanted_removals:
                raise ValueError(
                    f"{wanted_removals[removal]} cannot remove {removal}; "
                    f"it is already owned by {existing.get('id')}"
                )

    additional_removals = set(data.get("additional_removals", []))
    overlap = sorted(additional_removals.intersection(wanted_removals))
    if overlap:
        raise ValueError(
            f"AppliedCreate removals are already globally claimed: {overlap}"
        )

    preserved = set(data.get("preserve_recipe_ids", []))
    overlap = sorted(preserved.intersection(wanted_removals))
    if overlap:
        raise ValueError(
            f"AppliedCreate coverage cannot remove preserved recipes: {overlap}"
        )


def _upsert(data: dict[str, Any], recipe: dict[str, Any]) -> None:
    matches = [
        index
        for index, existing in enumerate(data["recipes"])
        if existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"Managed recipe is duplicated: {recipe['id']}")
    if matches:
        data["recipes"][matches[0]] = recipe
    else:
        data["recipes"].append(recipe)


def apply(data: dict[str, Any]) -> None:
    """Apply the curated stress-storage ladder without filesystem effects."""

    additions = _recipes()
    _assert_unclaimed(data, additions)
    for recipe in additions:
        _upsert(data, recipe)

