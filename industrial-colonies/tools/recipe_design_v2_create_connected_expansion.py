"""Finish the practical Create: Connected acquisition surface.

The broader Create add-on module already owns Connected's programmable chip,
dashboard, inventory bridge, silo, battery, brake, and automatic clutch routes.
This module covers the remaining *functional* transmission, vessel, and signal
parts without absorbing the mod's copycats, fan catalysts, dye palettes,
creative vessel, charged/internal battery states, or orientation-only vertical
blocks.

The manufacturing language is intentionally compact:

* native/Andesite machinery handles ordinary kinetic couplings;
* Brass machinery handles precision gearboxes and inverted controls; and
* Copper machinery is reserved for the two conductive network components.

Stock batch sizes are retained (notably the four-at-a-time Brass Chute), small
parts do not become 5x5 projects, and no Precision Mechanism is added merely as
a difficulty token.  ``apply`` is idempotent and has no filesystem side effects.
"""

from __future__ import annotations

import re
from typing import Any


ANDESITE_DEPLOYER = "create:deployer"
ANDESITE_PRESS = "create:mechanical_press"
ANDESITE_SAW = "create:mechanical_saw"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(1) if match else value.strip()


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _shaped(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    remove: list[str],
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "shaped",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": remove,
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = depends_on
    return recipe


def _sequence(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    remove: list[str],
    deployer: str,
    press: str,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": 1,
        "steps": [_deploy(item, deployer) for item in ingredients]
        + [_press(press)],
        "remove": remove,
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = depends_on
    return recipe


def _compacting(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    machine: str,
    inputs: list[str],
    output: str,
    remove: list[str],
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": machine,
        "inputs": inputs,
        "output": output,
        "remove": remove,
        "exclusive_output": True,
    }
    if depends_on:
        recipe["depends_on"] = depends_on
    return recipe


def _cutting(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    remove: list[str],
) -> dict[str, Any]:
    return {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "cutting",
        "comment": comment,
        "machine": ANDESITE_SAW,
        "input": input_item,
        "output": output,
        "processing_time": 200,
        "remove": remove,
        "exclusive_output": True,
    }


def _recipes() -> list[dict[str, Any]]:
    return [
        # Native/Andesite kinetic hardware.  These are ordinary mechanical
        # augments, so their shapes explain the part instead of pricing it with
        # unrelated electronics.
        _shaped(
            "industrial_colonies:create_connected/crank_wheel",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=560,
            comment="Brace a hand crank above a small cog and keyed output shaft to make a compact handwheel",
            pattern=[" H ", "ACA", " S "],
            key={
                "H": "create:hand_crank",
                "A": "create:andesite_alloy",
                "C": "create:cogwheel",
                "S": "create:shaft",
            },
            output="create_connected:crank_wheel",
            remove=["create_connected:crafting/kinetics/crank_wheel"],
        ),
        _shaped(
            "industrial_colonies:create_connected/large_crank_wheel",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=561,
            comment="Mount a hand crank on a large cogwheel with a broad two-point shaft yoke for high-leverage manual drive",
            pattern=[" H ", "ALA", "S S"],
            key={
                "H": "create:hand_crank",
                "A": "create:andesite_alloy",
                "L": "create:large_cogwheel",
                "S": "create:shaft",
            },
            output="create_connected:large_crank_wheel",
            remove=["create_connected:crafting/kinetics/large_crank_wheel"],
        ),
        _shaped(
            "industrial_colonies:create_connected/cross_connector",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=562,
            comment="Brace four perpendicular shafts around a gearbox so the cross coupling has a visible load path in every direction",
            pattern=["ASA", "SGS", "ASA"],
            key={
                "A": "create:andesite_alloy",
                "S": "create:shaft",
                "G": "create:gearbox",
            },
            output="create_connected:cross_connector",
            remove=["create_connected:crafting/kinetics/cross_connector"],
        ),
        _shaped(
            "industrial_colonies:create_connected/parallel_gearbox",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=563,
            comment="Add a large transfer gear above a shaft-through gearbox and close the parallel takeoff in an Andesite housing",
            pattern=[" L ", "SGS", " C "],
            key={
                "L": "create:large_cogwheel",
                "S": "create:shaft",
                "G": "create:gearbox",
                "C": "create:andesite_casing",
            },
            output="create_connected:parallel_gearbox",
            remove=[
                "create_connected:crafting/kinetics/parallel_gearbox",
                "create_connected:crafting/kinetics/parallel_gearbox_from_conversion",
            ],
        ),
        _shaped(
            "industrial_colonies:create_connected/six_way_gearbox",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=564,
            comment="Extend a finished cross connector with opposed vertical large gears and a through-shaft to create all six takeoffs",
            pattern=[" L ", "SCS", " L "],
            key={
                "L": "create:large_cogwheel",
                "S": "create:shaft",
                "C": "create_connected:cross_connector",
            },
            output="create_connected:six_way_gearbox",
            remove=[
                "create_connected:crafting/kinetics/six_way_gearbox",
                "create_connected:crafting/kinetics/six_way_gearbox_from_conversion",
                "create_connected:crafting/kinetics/six_way_gearbox_from_gearbox",
                "create_connected:crafting/kinetics/six_way_gearbox_from_parallel",
            ],
            depends_on=["industrial_colonies:create_connected/cross_connector"],
        ),
        _shaped(
            "industrial_colonies:create_connected/freewheel_clutch",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=565,
            comment="Build the one-way clutch as an asymmetric ratchet around a normal clutch with a gear pawl, iron guard, and paired shafts",
            pattern=[" I ", "GCS", " S "],
            key={
                "I": "create:iron_sheet",
                "G": "create:cogwheel",
                "C": "create:clutch",
                "S": "create:shaft",
            },
            output="create_connected:freewheel_clutch",
            remove=["create_connected:crafting/kinetics/freewheel_clutch"],
        ),
        _shaped(
            "industrial_colonies:create_connected/fluid_vessel",
            phase="Mechanical Foundations",
            node="CR01 — Liquid Tech",
            order=566,
            comment="Wrap a wooden vessel core in a four-sided copper shell and close it over a sturdy serviceable base",
            pattern=[" C ", "CBC", " S "],
            key={
                "C": "create:copper_sheet",
                "B": "#c:barrels/wooden",
                "S": "create:sturdy_sheet",
            },
            output="create_connected:fluid_vessel",
            remove=[
                "create_connected:crafting/kinetics/fluid_vessel",
                "create_connected:crafting/kinetics/fluid_vessel_from_conversion",
            ],
        ),
        _cutting(
            "industrial_colonies:create_connected/shear_pin",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=567,
            comment="Saw one standard shaft into one calibrated sacrificial shear pin on the native Andesite cutting line",
            input_item="create:shaft",
            output="create_connected:shear_pin",
            remove=["create:cutting/shaft"],
        ),
        # Native Create machines are the pack's Andesite manufacturing line.
        # Encasing is delayed only until the Deployer exists; the components
        # themselves remain simple mechanical hardware.
        _sequence(
            "industrial_colonies:create_connected/andesite_encased_cross_connector",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=568,
            comment="Enclose a proven cross connector with an Andesite service shell and one iron wear face on the native mechanical line",
            input_item="create_connected:cross_connector",
            output="create_connected:andesite_encased_cross_connector",
            ingredients=["create:andesite_casing", "create:iron_sheet"],
            remove=[],
            deployer=ANDESITE_DEPLOYER,
            press=ANDESITE_PRESS,
            depends_on=[
                "industrial_colonies:create_connected/cross_connector",
                "industrial_colonies:brass/deployer",
            ],
        ),
        _sequence(
            "industrial_colonies:create_connected/encased_chain_cogwheel",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=569,
            comment="Fit a cogwheel and keyed Andesite collar into an encased chain-drive body instead of combining two finished blocks shapelessly",
            input_item="create:encased_chain_drive",
            output="create_connected:encased_chain_cogwheel",
            ingredients=["create:cogwheel", "create:andesite_alloy"],
            remove=["create_connected:crafting/kinetics/encased_chain_cogwheel"],
            deployer=ANDESITE_DEPLOYER,
            press=ANDESITE_PRESS,
            depends_on=["industrial_colonies:brass/deployer"],
        ),
        # Brass is the precision/control environment.
        _compacting(
            "industrial_colonies:create_connected/brass_chute_batch",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=570,
            comment="Brass-press four native chutes and four formed sheets around one shared Brass feed billet, retaining the stock four-chute batch",
            machine=BRASS_PRESS,
            inputs=[
                "create:chute",
                "create:chute",
                "create:chute",
                "create:chute",
                "create:brass_sheet",
                "create:brass_sheet",
                "create:brass_sheet",
                "create:brass_sheet",
                "create:brass_ingot",
            ],
            output="4x create_connected:brass_chute",
            remove=["create_connected:crafting/kinetics/brass_chute"],
            depends_on=["industrial_colonies:manufacturing/brass_press"],
        ),
        _sequence(
            "industrial_colonies:create_connected/brass_gearbox",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=571,
            comment="Build the precision gearbox around a Brass shell with a speed controller, four matched cogs, and an opposed shaft pair",
            input_item="create:brass_casing",
            output="create_connected:brass_gearbox",
            ingredients=[
                "create:rotation_speed_controller",
                "4x create:cogwheel",
                "2x create:shaft",
            ],
            remove=[
                "create_connected:crafting/kinetics/brass_gearbox",
                "create_connected:crafting/kinetics/brass_gearbox_from_conversion",
            ],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            depends_on=[
                "industrial_colonies:manufacturing/brass_press",
                "industrial_colonies:manufacturing/brass_deployer",
                "industrial_colonies:create_core/rotation_speed_controller",
            ],
        ),
        _sequence(
            "industrial_colonies:create_connected/brass_encased_cross_connector",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=572,
            comment="Rebuild the Andesite encased connector with a Brass service enclosure and paired precision wear plates",
            input_item="create_connected:andesite_encased_cross_connector",
            output="create_connected:brass_encased_cross_connector",
            ingredients=["create:brass_casing", "2x create:brass_sheet"],
            remove=[],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            depends_on=[
                "industrial_colonies:create_connected/andesite_encased_cross_connector",
                "industrial_colonies:manufacturing/brass_press",
                "industrial_colonies:manufacturing/brass_deployer",
            ],
        ),
        _sequence(
            "industrial_colonies:create_connected/inverted_clutch",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=573,
            comment="Reverse a normal clutch's control state with a redstone torch, electron-tube inverter, and Brass contact plate",
            input_item="create:clutch",
            output="create_connected:inverted_clutch",
            ingredients=[
                "minecraft:redstone_torch",
                "create:electron_tube",
                "create:brass_sheet",
            ],
            remove=["create_connected:crafting/kinetics/inverted_clutch_from_conversion"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            depends_on=[
                "industrial_colonies:manufacturing/brass_press",
                "industrial_colonies:manufacturing/brass_deployer",
            ],
        ),
        _sequence(
            "industrial_colonies:create_connected/inverted_gearshift",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=574,
            comment="Give a normal gearshift inverted direction logic with a comparator bridge, electron tube, and Brass contact plate",
            input_item="create:gearshift",
            output="create_connected:inverted_gearshift",
            ingredients=[
                "minecraft:comparator",
                "create:electron_tube",
                "create:brass_sheet",
            ],
            remove=["create_connected:crafting/kinetics/inverted_gearshift_from_conversion"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            depends_on=[
                "industrial_colonies:manufacturing/brass_press",
                "industrial_colonies:manufacturing/brass_deployer",
            ],
        ),
        # Copper is used only where the part is actually conductive/networked.
        _sequence(
            "industrial_colonies:create_connected/linked_transmitter",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=575,
            comment="Convert a paired Redstone Link into a dedicated transmitter with an insulated TFMG lead, copper antenna plate, and directional electron-tube stage",
            input_item="create:redstone_link",
            output="create_connected:linked_transmitter",
            ingredients=[
                "tfmg:copper_wire",
                "create:copper_sheet",
                "create:electron_tube",
            ],
            remove=["create_connected:crafting/kinetics/linked_transmitter_from_conversion"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
            depends_on=[
                "industrial_colonies:manufacturing/copper_press",
                "industrial_colonies:manufacturing/copper_deployer",
                "industrial_colonies:create_core/redstone_link_pair",
            ],
        ),
        _sequence(
            "industrial_colonies:create_connected/redstone_link_wildcard",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=576,
            comment="Build a wildcard link on the Copper network line by masking a transmitter with a crafter cover, insulated lead, quartz frequency element, and redstone contact",
            input_item="create:transmitter",
            output="create_connected:redstone_link_wildcard",
            ingredients=[
                "create:crafter_slot_cover",
                "tfmg:copper_wire",
                "minecraft:quartz",
                "minecraft:redstone",
            ],
            remove=["create_connected:crafting/kinetics/redstone_link_wildcard"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
            depends_on=[
                "industrial_colonies:manufacturing/copper_press",
                "industrial_colonies:manufacturing/copper_deployer",
            ],
        ),
    ]


def _assert_internal_uniqueness(additions: list[dict[str, Any]]) -> None:
    recipe_ids = [recipe["id"] for recipe in additions]
    if len(recipe_ids) != len(set(recipe_ids)):
        raise ValueError("Create: Connected expansion contains duplicate managed IDs")

    output_ids = [_item_id(recipe.get("output")) for recipe in additions]
    if len(output_ids) != len(set(output_ids)):
        raise ValueError("Create: Connected expansion contains duplicate managed outputs")

    removals = [
        removal
        for recipe in additions
        for removal in recipe.get("remove", [])
    ]
    if len(removals) != len(set(removals)):
        raise ValueError("Create: Connected expansion contains duplicate stock removals")


def _assert_unclaimed(data: dict[str, Any], additions: list[dict[str, Any]]) -> None:
    """Refuse to steal an output or stock removal from another module."""

    addition_ids = {recipe["id"] for recipe in additions}
    wanted_outputs = {
        _item_id(recipe.get("output")): recipe["id"] for recipe in additions
    }
    wanted_removals = {
        removal: recipe["id"]
        for recipe in additions
        for removal in recipe.get("remove", [])
    }

    for existing in data.get("recipes", []):
        if existing.get("id") in addition_ids:
            continue
        outputs = [_item_id(existing.get("output"))]
        for field in ("outputs", "results"):
            outputs.extend(_item_id(value) for value in existing.get(field, []))
        for output in outputs:
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
            f"Create: Connected removals are already globally claimed: {overlap}"
        )

    preserved = set(data.get("preserve_recipe_ids", []))
    overlap = sorted(preserved.intersection(wanted_removals))
    if overlap:
        raise ValueError(
            f"Create: Connected expansion cannot remove preserved recipes: {overlap}"
        )


def _upsert(data: dict[str, Any], recipe: dict[str, Any]) -> None:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed recipe seed field 'recipes' must be a list")
    matches = [
        index for index, existing in enumerate(recipes) if existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"Managed recipe is duplicated: {recipe['id']}")
    if matches:
        recipes[matches[0]] = recipe
    else:
        recipes.append(recipe)


def apply(data: dict[str, Any]) -> None:
    """Apply the curated Create: Connected expansion in memory."""

    additions = _recipes()
    _assert_internal_uniqueness(additions)
    _assert_unclaimed(data, additions)
    for recipe in additions:
        _upsert(data, recipe)

