"""Digital-factory recipe redesign applied by apply_recipe_design_v2.py."""

from __future__ import annotations

from typing import Any


def _index(data: dict[str, Any]) -> dict[str, int]:
    return {recipe["id"]: index for index, recipe in enumerate(data["recipes"])}


def _output_item(value: Any) -> str | None:
    if isinstance(value, str):
        parts = value.strip().split()
        if len(parts) == 2 and parts[0].endswith("x") and parts[0][:-1].isdigit():
            return parts[1]
        return value.strip() if ":" in value else None
    if isinstance(value, dict):
        identifier = value.get("id") or value.get("item")
        return identifier if isinstance(identifier, str) else None
    return None


def _replace(data: dict[str, Any], recipe_id: str, body: dict[str, Any]) -> None:
    indexes = _index(data)
    if recipe_id not in indexes:
        # v3 gives some digital outputs new authoritative card IDs.  Keep this
        # legacy pass rerunnable without masking a genuinely missing output.
        wanted = _output_item(body.get("output"))
        if wanted and any(_output_item(recipe.get("output")) == wanted for recipe in data["recipes"]):
            return
        raise KeyError(f"Expected managed recipe is missing: {recipe_id}")
    old = data["recipes"][indexes[recipe_id]]
    replacement: dict[str, Any] = {"id": recipe_id}
    for key in ("node", "phase", "order"):
        if key in old:
            replacement[key] = old[key]
    replacement.update(body)
    for key in ("remove", "exclusive_output", "if_mod_loaded", "depends_on"):
        if key not in replacement and key in old:
            replacement[key] = old[key]
    data["recipes"][indexes[recipe_id]] = replacement


def _deploy(ingredient: str, casing: str = "brass") -> dict[str, str]:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": f"createcasing:{casing}_deployer",
    }


def _press(casing: str = "brass") -> dict[str, str]:
    return {"op": "pressing", "machine": f"createcasing:{casing}_press"}


def _sequence(
    comment: str,
    input_item: str,
    transitional: str,
    output: Any,
    ingredients: list[str],
    *,
    casing: str = "brass",
) -> dict[str, Any]:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional,
        "output": output,
        "loops": 1,
        "steps": [_deploy(item, casing) for item in ingredients] + [_press(casing)],
    }


def _redesign_whole_machine_compacting(data: dict[str, Any]) -> None:
    replacements = {
        "industrial_colonies:digital_core/energy_acceptor": _sequence(
            "Wire a TFMG transformer into an insulated AE power-entry cabinet on the Copper electrical line",
            "tfmg:transformer",
            "tfmg:transformer",
            "ae2:energy_acceptor",
            [
                "ae2:quartz_glass",
                "ae2:fluix_crystal",
                "tfmg:copper_wire",
                "tfmg:copper_wire",
                "tfmg:circuit_board",
            ],
            casing="copper",
        ),
        "industrial_colonies:digital_core/molecular_assembler": _sequence(
            "Build an autocrafting chamber around a real crafting bed, paired matter-transfer cores, and Brass precision control",
            "minecraft:crafting_table",
            "minecraft:crafting_table",
            "ae2:molecular_assembler",
            [
                "ae2:quartz_glass",
                "ae2:quartz_glass",
                "ae2:annihilation_core",
                "ae2:formation_core",
                "create:precision_mechanism",
                "tfmg:circuit_board",
            ],
        ),
        "industrial_colonies:digital_core/block_reader": _sequence(
            "Instrument the shared peripheral chassis with optical and mechanical observers for block telemetry",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:block_reader",
            [
                "minecraft:observer",
                "create:content_observer",
                "computercraft:wired_modem_full",
                "ae2:calculation_processor",
            ],
        ),
        "industrial_colonies:digital_core/energy_detector": _sequence(
            "Instrument the shared peripheral chassis with a TFMG voltage sensor and isolated telemetry lead",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:energy_detector",
            [
                "tfmg:voltage_observer",
                "tfmg:copper_wire",
                "minecraft:comparator",
                "ae2:calculation_processor",
            ],
        ),
        "industrial_colonies:digital_core/inventory_manager": _sequence(
            "Build physical inventory I/O into the shared peripheral chassis instead of basin-compacting a complete computer",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:inventory_manager",
            [
                "computercraft:wired_modem_full",
                "minecraft:hopper",
                "#c:chests",
                "create:content_observer",
                "ae2:calculation_processor",
            ],
        ),
        "industrial_colonies:digital_core/colony_integrator": _sequence(
            "Bind MineColonies planning and builder instruments to the common networked peripheral platform",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:colony_integrator",
            [
                "computercraft:wired_modem_full",
                "minecolonies:blockminecoloniesrack",
                "minecolonies:build_goggles",
                "structurize:sceptergold",
            ],
        ),
        "industrial_colonies:digital_core/me_bridge": _sequence(
            "Bridge a proven ME interface into the common modem chassis with fluix bandwidth and engineering control",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:peripheral_casing",
            "advancedperipherals:me_bridge",
            [
                "ae2:interface",
                "ae2:fluix_block",
                "computercraft:wired_modem_full",
                "ae2:engineering_processor",
                "tfmg:capacitor_item",
            ],
        ),
    }
    for recipe_id, body in replacements.items():
        _replace(data, recipe_id, body)


def _redesign_advanced_computers(data: dict[str, Any]) -> None:
    replacements = {
        "industrial_colonies:computercraft/network/advanced_wireless_modem": _sequence(
            "Retune the normal modem for long-range service with fluix coupling, a large coil, and calculation control",
            "computercraft:wireless_modem_normal",
            "industrial_colonies:unfinished_computercraft_advanced_wireless_modem",
            "computercraft:wireless_modem_advanced",
            [
                "ae2:fluix_pearl",
                "ae2:calculation_processor",
                "tfmg:large_coil",
                "tfmg:capacitor_item",
            ],
        ),
        "industrial_colonies:computercraft/computer/advanced_upgrade": _sequence(
            "Upgrade the normal computer with faster stress logic, magnetic shielding, a lithium backup, and a new display controller",
            "computercraft:computer_normal",
            "industrial_colonies:unfinished_computercraft_advanced_computer",
            "computercraft:computer_advanced",
            [
                "appliedcreate:advanced_stress_processor",
                "ae2:calculation_processor",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:lithium_charge",
                "create:display_board",
            ],
        ),
        "industrial_colonies:computercraft/monitor/advanced": _sequence(
            "Upgrade the monochrome monitor with a color display link, calculation logic, vibrant glass, and magnetic shielding",
            "computercraft:monitor_normal",
            "industrial_colonies:unfinished_computercraft_advanced_monitor",
            "computercraft:monitor_advanced",
            [
                "create:display_link",
                "ae2:calculation_processor",
                "ae2:quartz_vibrant_glass",
                "tfmg:magnetic_alloy_sheet",
            ],
        ),
        "industrial_colonies:computercraft/mobile/advanced_pocket_upgrade": _sequence(
            "Upgrade the pocket computer around its radio, processor, compact lithium supply, and hardened display glass",
            "computercraft:pocket_computer_normal",
            "industrial_colonies:unfinished_computercraft_advanced_pocket_computer",
            "computercraft:pocket_computer_advanced",
            [
                "computercraft:wireless_modem_advanced",
                "appliedcreate:advanced_stress_processor",
                "tfmg:lithium_charge",
                "ae2:quartz_vibrant_glass",
            ],
        ),
        "industrial_colonies:computercraft/mobile/advanced_turtle_upgrade": _sequence(
            "Rebuild the turtle as a heavy autonomous robot with an advanced computer, drive motor, tool arm, and magnetic chassis",
            "computercraft:turtle_normal",
            "industrial_colonies:unfinished_computercraft_advanced_turtle",
            "computercraft:turtle_advanced",
            [
                "computercraft:computer_advanced",
                "tfmg:steel_mechanism",
                "tfmg:electric_motor",
                "create:mechanical_arm",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            casing="industrial_iron",
        ),
    }
    for recipe_id, body in replacements.items():
        _replace(data, recipe_id, body)


def _redesign_mega_crafting_unit(data: dict[str, Any]) -> None:
    _replace(
        data,
        "industrial_colonies:ae2_high_energy/mega_crafting_unit",
        _sequence(
            "Scale a standard crafting unit with accumulation logic, stress control, dense bandwidth, and a transformer-backed magnetic plane",
            "ae2:crafting_unit",
            "ae2:crafting_unit",
            "megacells:mega_crafting_unit",
            [
                "megacells:accumulation_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:engineering_processor",
                "ae2:fluix_smart_dense_cable",
                "tfmg:transformer",
                "tfmg:magnetic_alloy_sheet",
            ],
        ),
    )


def apply(data: dict[str, Any]) -> None:
    _redesign_whole_machine_compacting(data)
    _redesign_advanced_computers(data)
    _redesign_mega_crafting_unit(data)
