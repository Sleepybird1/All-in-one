"""Curated factory coverage for Create add-ons outside the TFMG power family.

The recipes in this module cover functional gaps in Create: Connected,
Create: Enchantment Industry, Create Factory Controller, Create Metallurgy,
and Create Electro Energetics.  They deliberately leave palettes, dyes,
decorative blocks, conversion-only orientation recipes, creative items, and
Apotheosis-affix machinery alone.

``apply`` is idempotent and mutates only the seed dictionary passed to it.
Importing this module has no filesystem or seed side effects.
"""

from __future__ import annotations

import re
from typing import Any


COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    """Return the exact item id from a simple output slot."""

    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(1) if match else value.strip()


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


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
    loops: int = 1,
) -> dict[str, Any]:
    return {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": loops,
        "steps": [_deploy(item, deployer) for item in ingredients] + [_press(press)],
        "remove": remove,
        "exclusive_output": True,
    }


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
    mechanical: bool = False,
) -> dict[str, Any]:
    return {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "mechanical_crafting" if mechanical else "shaped",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": remove,
        "exclusive_output": True,
    }


def _recipes() -> list[dict[str, Any]]:
    return [
        # Create: Connected -- mechanical controls and factory logistics.
        _sequence(
            "industrial_colonies:create_addons/connected_control_chip",
            phase="Digital Logistics",
            node="CR01 — Early Chips",
            order=180,
            comment="Populate a TFMG circuit substrate with complementary semiconductors, an electron tube, and a timed redstone contact on the Brass electronics line",
            input_item="tfmg:circuit_board",
            output="2x create_connected:control_chip",
            ingredients=[
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "create:electron_tube",
                "create:golden_sheet",
                "minecraft:redstone",
            ],
            remove=["create_connected:sequenced_assembly/control_chip"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
            loops=2,
        ),
        _sequence(
            "industrial_colonies:create_addons/sequenced_pulse_generator",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=181,
            comment="Build the programmable pulse stack around a manufactured control chip, paired timing elements, and a shielded signal lead",
            input_item="create_connected:control_chip",
            output="create_connected:sequenced_pulse_generator",
            ingredients=[
                "create:electron_tube",
                "minecraft:repeater",
                "minecraft:redstone_torch",
                "create:brass_sheet",
                "tfmg:copper_wire",
            ],
            remove=["create_connected:crafting/kinetics/sequenced_pulse_generator"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/connected_dashboard",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=182,
            comment="Instrument a Brass enclosure with a display face, process controller, factory gauge, and serviceable copper signal harness",
            input_item="create:brass_casing",
            output="create_connected:dashboard",
            ingredients=[
                "create:display_board",
                "create_connected:control_chip",
                "create:factory_gauge",
                "tfmg:copper_wire",
            ],
            remove=["create_connected:crafting/kinetics/dashboard"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/inventory_access_port_batch",
            phase="Digital Logistics",
            node="CR01 — Early Digital Crafting",
            order=183,
            comment="Fit a Brass logistics housing with paired chute throats, stock sensing, and one local control stage to produce two matched access ports",
            input_item="create:brass_casing",
            output="2x create_connected:inventory_access_port",
            ingredients=[
                "2x create_connected:brass_chute",
                "create:stock_link",
                "create_connected:control_chip",
                "tfmg:copper_wire",
            ],
            remove=["create_connected:crafting/kinetics/inventory_access_port"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/inventory_bridge",
            phase="Digital Logistics",
            node="CR01 — Early Digital Crafting",
            order=184,
            comment="Join two completed access ports through a mechanical transfer arm, smart chute, and synchronized control board rather than converting one port for free",
            input_item="create_connected:inventory_access_port",
            output="create_connected:inventory_bridge",
            ingredients=[
                "create_connected:inventory_access_port",
                "create:mechanical_arm",
                "create:smart_chute",
                "tfmg:circuit_board",
                "create_connected:control_chip",
            ],
            remove=["create_connected:crafting/kinetics/inventory_bridge"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _shaped(
            "industrial_colonies:create_addons/item_silo",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=185,
            comment="Build the silo as a vertical sheet-metal bin around a proven item-vault body with a top inlet and bottom discharge chute",
            pattern=["ICI", "IVI", "III"],
            key={
                "I": "create:iron_sheet",
                "C": "create:chute",
                "V": "create:item_vault",
            },
            output="create_connected:item_silo",
            remove=[
                "create_connected:crafting/kinetics/item_silo",
                "create_connected:crafting/kinetics/item_silo_from_conversion",
            ],
            mechanical=True,
        ),
        _shaped(
            "industrial_colonies:create_addons/kinetic_battery_batch",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=186,
            comment="Assemble four flywheel cells from a large gear, opposed sturdy faces, a precision hub, and a Brass containment case",
            pattern=[" L ", "SPS", " C "],
            key={
                "L": "create:large_cogwheel",
                "S": "create:sturdy_sheet",
                "P": "create:precision_mechanism",
                "C": "create:brass_casing",
            },
            output="4x create_connected:kinetic_battery",
            remove=["create_connected:crafting/kinetics/kinetic_battery"],
            mechanical=True,
        ),
        _sequence(
            "industrial_colonies:create_addons/kinetic_bridge",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=187,
            comment="Turn a Brass transmission body into a reversible kinetic bridge with opposed shafts, clutching, stress sensing, and synchronized control",
            input_item="create:brass_casing",
            output="create_connected:kinetic_bridge",
            ingredients=[
                "create:clutch",
                "create:shaft",
                "create:shaft",
                "create:stressometer",
                "create_connected:control_chip",
            ],
            remove=["create_connected:crafting/kinetics/kinetic_bridge"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _shaped(
            "industrial_colonies:create_addons/brake",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=188,
            comment="Arrange iron calipers around replaceable obsidian friction pads, an Andesite hub, and its through-shaft",
            pattern=["I I", "OAO", " S "],
            key={
                "I": "create:iron_sheet",
                "O": "minecraft:obsidian",
                "A": "create:andesite_casing",
                "S": "create:shaft",
            },
            output="create_connected:brake",
            remove=["create_connected:crafting/kinetics/brake"],
        ),
        _sequence(
            "industrial_colonies:create_addons/centrifugal_clutch",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=189,
            comment="Calibrate a stock clutch with a speed gauge, weighted large gear, sturdy friction face, and balancing sheet",
            input_item="create:clutch",
            output="create_connected:centrifugal_clutch",
            ingredients=[
                "create:speedometer",
                "create:large_cogwheel",
                "create:sturdy_sheet",
                "create:brass_sheet",
            ],
            remove=["create_connected:crafting/kinetics/centrifugal_clutch"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/overstress_clutch",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=190,
            comment="Instrument a clutch with live stress measurement and a dedicated trip circuit so overload protection is manufactured rather than shapeless",
            input_item="create:clutch",
            output="create_connected:overstress_clutch",
            ingredients=[
                "create:stressometer",
                "create_connected:control_chip",
                "create:brass_sheet",
                "minecraft:redstone_torch",
            ],
            remove=["create_connected:crafting/kinetics/overstress_clutch"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        # Create Factory Controller -- a real digital supervisory controller.
        _sequence(
            "industrial_colonies:create_addons/factory_controller",
            phase="Digital Logistics",
            node="CR01 — Early Digital Crafting",
            order=210,
            comment="Commission a ComputerCraft computer as the supervisory factory controller by adding stock I/O, process gauges, contraption controls, and a dedicated front display",
            input_item="computercraft:computer_normal",
            output="createfactorycontroller:factory_controller",
            ingredients=[
                "create:stock_link",
                "create:factory_gauge",
                "create:contraption_controls",
                "create_connected:control_chip",
                "create:display_board",
                "create:brass_casing",
            ],
            remove=["createfactorycontroller:factory_controller"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        # Create Metallurgy -- durable equipment and serviceable foundry tools.
        _shaped(
            "industrial_colonies:create_addons/mechanical_belt_grinder",
            phase="Steel & Petroleum",
            node="CR01 — Advanced Alloy Mixing",
            order=230,
            comment="Mount one continuous abrasive belt above a shafted Andesite drive and brace the machine on a heavy steel foot",
            pattern=[" B ", "SAS", " H "],
            key={
                "B": "createmetallurgy:sandpaper_belt",
                "S": "create:shaft",
                "A": "create:andesite_casing",
                "H": "tfmg:heavy_plate",
            },
            output="createmetallurgy:mechanical_belt_grinder",
            remove=["createmetallurgy:crafting/content/mechanical_belt_grinder"],
        ),
        _sequence(
            "industrial_colonies:create_addons/labeling_station",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=231,
            comment="Convert a depot into an industrial label head with a name-tag feed, display strip, print control board, and copper signal harness",
            input_item="create:depot",
            output="createmetallurgy:labeling_station",
            ingredients=[
                "minecraft:name_tag",
                "create:display_board",
                "tfmg:circuit_board",
                "create:brass_sheet",
                "tfmg:copper_wire",
            ],
            remove=["createmetallurgy:crafting/content/labeling_station"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _shaped(
            "industrial_colonies:create_addons/foundry_faucet_batch",
            phase="Steel & Petroleum",
            node="CR01 — Advanced Alloy Mixing",
            order=232,
            comment="Form two foundry taps as cast-iron elbows around a pressure-rated pipe and a replaceable fluid valve",
            pattern=["HH ", " PV", " H "],
            key={
                "H": "tfmg:cast_iron_sheet",
                "P": "tfmg:cast_iron_pipe",
                "V": "create:fluid_valve",
            },
            output="2x createmetallurgy:faucet",
            remove=["createmetallurgy:crafting/content/faucet"],
        ),
        _shaped(
            "industrial_colonies:create_addons/ladle_filter_batch",
            phase="Steel & Petroleum",
            node="CR01 — Advanced Alloy Mixing",
            order=233,
            comment="Stretch layered wool media across a sturdy steel frame to make four replaceable ladle filters per fabrication run",
            pattern=["SWS", " W ", " H "],
            key={
                "S": "#c:ingots/steel",
                "W": "#minecraft:wool",
                "H": "create:sturdy_sheet",
            },
            output="4x createmetallurgy:ladle_filter",
            remove=["createmetallurgy:crafting/content/ladle_filter"],
        ),
        _shaped(
            "industrial_colonies:create_addons/sturdy_whisk",
            phase="Steel & Petroleum",
            node="CR01 — Advanced Alloy Mixing",
            order=234,
            comment="Hang a replaceable steel mechanism over three bent sturdy-sheet tines to form a heavy foundry whisk",
            pattern=[" M ", " S ", "S S"],
            key={"M": "tfmg:steel_mechanism", "S": "create:sturdy_sheet"},
            output="createmetallurgy:sturdy_whisk",
            remove=["createmetallurgy:crafting/content/sturdy_whisk"],
        ),
        _shaped(
            "industrial_colonies:create_addons/foundry_gauge_attachment_batch",
            phase="Steel & Petroleum",
            node="CR01 — Advanced Alloy Mixing",
            order=235,
            comment="Build two serviceable foundry gauges with a compass face, steel yoke, sight glass, and copper pickup lead",
            pattern=[" G ", "SCS", " W "],
            key={
                "G": "minecraft:compass",
                "S": "#c:ingots/steel",
                "C": "minecraft:glass_pane",
                "W": "tfmg:copper_wire",
            },
            output="2x createmetallurgy:gauge_attachment",
            remove=["createmetallurgy:crafting/content/gauge_attachment"],
        ),
        # Create: Enchantment Industry -- XP handling, not Apotheosis affixes.
        _shaped(
            "industrial_colonies:create_addons/mechanical_grindstone",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=250,
            comment="Mount a complete grindstone above a shafted Andesite drive with an iron service foot instead of crafting the machine from eight loose alloy pieces",
            pattern=[" G ", "SAS", " I "],
            key={
                "G": "minecraft:grindstone",
                "S": "create:shaft",
                "A": "create:andesite_casing",
                "I": "create:iron_sheet",
            },
            output="create_enchantment_industry:mechanical_grindstone",
            remove=["create_enchantment_industry:crafting/mechanical_grindstone"],
        ),
        _sequence(
            "industrial_colonies:create_addons/enchantment_printer",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=251,
            comment="Turn a spout into a controlled printing head with a precision feed, Brass platen, display strip, ink charge, and TFMG controller",
            input_item="create:spout",
            output="create_enchantment_industry:printer",
            ingredients=[
                "create:precision_mechanism",
                "create:brass_sheet",
                "create:display_board",
                "minecraft:black_dye",
                "tfmg:circuit_board",
            ],
            remove=["create_enchantment_industry:crafting/printer"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/experience_lantern",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=252,
            comment="Convert a copper process enclosure into a buffered experience lamp with absorbent media, luminous quartz, and insulated fluid monitoring",
            input_item="create:copper_casing",
            output="create_enchantment_industry:experience_lantern",
            ingredients=[
                "create:experience_block",
                "minecraft:sponge",
                "create:rose_quartz_lamp",
                "tfmg:glass_insulator_segment",
                "create:copper_sheet",
            ],
            remove=["create_enchantment_industry:crafting/experience_lantern"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/experience_hatch",
            phase="Steel & Petroleum",
            node="CR01 — Chemical Processing",
            order=253,
            comment="Rebuild a generic fluid hatch for liquid experience with a filtered valve, pressure face, and dedicated XP reservoir",
            input_item="create_dragons_plus:fluid_hatch",
            output="create_enchantment_industry:experience_hatch",
            ingredients=[
                "create:experience_block",
                "tfmg:plastic_fluid_valve",
                "create:sturdy_sheet",
                "create:brass_sheet",
            ],
            remove=["create_enchantment_industry:item_application/experience_hatch"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        # Electro Energetics -- TFMG-first internals in unique grid hardware.
        _sequence(
            "industrial_colonies:create_addons/electro_converter",
            phase="Electrical Manufacturing",
            node="CR01 — Electronics Manufacturing",
            order=270,
            comment="Build the kinetic-electric converter around a TFMG motor, wound rotor, laminated magnetic path, and buffered copper terminal",
            input_item="tfmg:industrial_aluminum_casing",
            output="electroenergetics:converter",
            ingredients=[
                "tfmg:electric_motor",
                "tfmg:rotor",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:capacitor_item",
                "electroenergetics:connector",
            ],
            remove=["electroenergetics:crafting/converter"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _shaped(
            "industrial_colonies:create_addons/electrical_panel_batch",
            phase="Electrical Manufacturing",
            node="CR01 — Electronics Manufacturing",
            order=271,
            comment="Fold two insulated control panels from aluminum skins around rubber cableways and paired copper endpoints",
            pattern=["AAA", "RWR", "C C"],
            key={
                "A": "tfmg:aluminum_sheet",
                "R": "tfmg:rubber_sheet",
                "W": "tfmg:copper_wire",
                "C": "electroenergetics:connector",
            },
            output="2x electroenergetics:electrical_panel",
            remove=["electroenergetics:crafting/electrical_panel"],
        ),
        _sequence(
            "industrial_colonies:create_addons/fuse_holder_batch",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=272,
            comment="Fit two panel sections with ceramic fuse beds, insulated covers, copper leads, and replaceable grid connectors",
            input_item="electroenergetics:electrical_panel",
            output="2x electroenergetics:fuse_holder",
            ingredients=[
                "tfmg:fireproof_bricks",
                "tfmg:plastic_sheet",
                "tfmg:copper_wire",
                "electroenergetics:connector",
            ],
            remove=["electroenergetics:crafting/fuse_holder"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/cut_off_switch",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=273,
            comment="Turn an electrical panel into a manual isolator with a fuse bed, opposed terminals, insulated handle, and copper bus",
            input_item="electroenergetics:electrical_panel",
            output="electroenergetics:cut_off_switch",
            ingredients=[
                "electroenergetics:fuse_holder",
                "2x electroenergetics:connector",
                "minecraft:lever",
                "tfmg:plastic_sheet",
                "tfmg:copper_wire",
            ],
            remove=["electroenergetics:crafting/cut_off_switch"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/electrical_relay",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=274,
            comment="Motorize a proven isolator with a TFMG electromagnetic coil, discrete resistor, return contact, and insulated power lead",
            input_item="electroenergetics:cut_off_switch",
            output="electroenergetics:relay",
            ingredients=[
                "tfmg:electromagnetic_coil",
                "tfmg:resistor",
                "electroenergetics:connector",
                "tfmg:copper_wire",
            ],
            remove=["electroenergetics:crafting/relay"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/redstone_relay",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=275,
            comment="Add transistorized redstone control to a completed power relay without repeating its electromechanical coil and contacts",
            input_item="electroenergetics:relay",
            output="electroenergetics:redstone_relay",
            ingredients=[
                "tfmg:circuit_board",
                "tfmg:transistor_item",
                "minecraft:redstone_torch",
                "tfmg:copper_wire",
            ],
            remove=["electroenergetics:crafting/redstone_relay"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _shaped(
            "industrial_colonies:create_addons/resistive_heater",
            phase="Electrical Manufacturing",
            node="CR01 — Electronics Manufacturing",
            order=276,
            comment="Build a serviceable heater with a firebrick hot face above a large resistance coil and a steel, terminal-fed enclosure",
            pattern=["FFF", "RLR", " C "],
            key={
                "F": "tfmg:fireproof_bricks",
                "R": "tfmg:resistor",
                "L": "tfmg:large_coil",
                "C": "tfmg:steel_casing",
            },
            output="electroenergetics:resistive_heater",
            remove=["electroenergetics:crafting/resistive_heater"],
            mechanical=True,
        ),
        _sequence(
            "industrial_colonies:create_addons/energy_meter",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=277,
            comment="Instrument an electrical panel with TFMG measurement hardware, a dual terminal block, and a serviceable logging board",
            input_item="electroenergetics:electrical_panel",
            output="electroenergetics:energy_meter",
            ingredients=[
                "tfmg:multimeter",
                "tfmg:voltmeter",
                "electroenergetics:double_connector",
                "tfmg:circuit_board",
                "minecraft:glass_pane",
            ],
            remove=["electroenergetics:crafting/energy_meter"],
            deployer=BRASS_DEPLOYER,
            press=BRASS_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/grid_compatible_electric_pump",
            phase="Electrical Manufacturing",
            node="CR01 — Grid Engineering",
            order=278,
            comment="Adapt the canonical TFMG electric pump to the Electro Energetics grid with a protected connector, field magnet, insulated lead, and serviceable terminal cover",
            input_item="tfmg:electric_pump",
            output="electroenergetics:electric_pump",
            ingredients=[
                "electroenergetics:connector",
                "electroenergetics:magnet",
                "tfmg:copper_wire",
                "tfmg:plastic_sheet",
            ],
            remove=["electroenergetics:crafting/electric_pump"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            "industrial_colonies:create_addons/tri_polar_energy_meter",
            phase="High-Energy Grid",
            node="CR01 — High-Voltage Systems",
            order=279,
            comment="Upgrade the proven energy meter for three-pole service with a triple terminal, paired current transformers, isolated power transformer, and advanced supervisory circuit",
            input_item="electroenergetics:energy_meter",
            output="electroenergetics:tri_polar_energy_meter",
            ingredients=[
                "electroenergetics:triple_connector",
                "electroenergetics:current_transformer",
                "electroenergetics:current_transformer",
                "tfmg:transformer",
                "mekanism:advanced_control_circuit",
            ],
            remove=["electroenergetics:crafting/tri_polar_energy_meter"],
            deployer="createcasing:weathered_iron_deployer",
            press="createcasing:weathered_iron_press",
        ),
    ]


def _assert_unclaimed(data: dict[str, Any], additions: list[dict[str, Any]]) -> None:
    """Refuse to silently take an output/removal already owned elsewhere."""

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
        raise ValueError(f"Create add-on coverage removals are already globally claimed: {overlap}")

    preserved = set(data.get("preserve_recipe_ids", []))
    overlap = sorted(preserved.intersection(wanted_removals))
    if overlap:
        raise ValueError(f"Create add-on coverage cannot remove preserved recipes: {overlap}")


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
    additions = _recipes()
    _assert_unclaimed(data, additions)
    for recipe in additions:
        _upsert(data, recipe)
