"""Focused AE-family factory coverage for the manufacturing-first redesign.

This module intentionally leaves ordinary cable conversions, cell housing
assembly, colours, cards, and block/part form conversions alone.  It claims
only the high-impact electronics, high-throughput machines, and storage
components whose stock recipes otherwise bypass the TFMG/encased production
lines.

``apply`` is idempotent and mutates only the supplied seed dictionary.  It is
kept separate from the migration driver so it can be reviewed before it is
added to the normal recipe-design wave.
"""

from __future__ import annotations

from typing import Any, Iterable


BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
QUANTUM_DEPLOYER = "createcasing:weathered_iron_deployer"
QUANTUM_PRESS = "createcasing:weathered_iron_press"


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _sequence(
    *,
    recipe_id: str,
    phase: str,
    node: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    remove: list[str],
    deployer: str = BRASS_DEPLOYER,
    press: str = BRASS_PRESS,
) -> dict[str, Any]:
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
        "steps": [_deploy(item, deployer) for item in ingredients] + [_press(press)],
        "remove": remove,
        "exclusive_output": True,
    }


def _mechanical(
    *,
    recipe_id: str,
    phase: str,
    node: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    remove: list[str],
) -> dict[str, Any]:
    return {
        "id": recipe_id,
        "node": node,
        "phase": phase,
        "order": order,
        "type": "mechanical_crafting",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": remove,
        "exclusive_output": True,
    }


def _ae2_recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            recipe_id="industrial_colonies:ae2_coverage/annihilation_core_batch",
            phase="Digital Logistics",
            node="CR01 — ME System Basics",
            order=80,
            comment="Split a logic package into paired extraction cores with fluix timing, a quartz cutting face, and TFMG switching hardware",
            input_item="ae2:logic_processor",
            output="2x ae2:annihilation_core",
            ingredients=[
                "ae2:fluix_dust",
                "ae2:certus_quartz_crystal",
                "tfmg:transistor_item",
                "tfmg:copper_wire",
            ],
            remove=["ae2:materials/annihilationcore"],
        ),
        _sequence(
            recipe_id="industrial_colonies:ae2_coverage/formation_core_batch",
            phase="Digital Logistics",
            node="CR01 — ME System Basics",
            order=81,
            comment="Split a logic package into paired placement cores with a conductive face, fluix timing, and a stabilized TFMG capacitor",
            input_item="ae2:logic_processor",
            output="2x ae2:formation_core",
            ingredients=[
                "ae2:fluix_dust",
                "create:golden_sheet",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
            ],
            remove=["ae2:materials/formationcore"],
        ),
        _sequence(
            recipe_id="industrial_colonies:ae2_coverage/energy_cell",
            phase="Digital Logistics",
            node="CR01 — ME System Basics",
            order=90,
            comment="Convert the transformer-backed AE power inlet into a rechargeable cell with lithium charge storage and magnetic containment",
            input_item="ae2:energy_acceptor",
            output="ae2:energy_cell",
            ingredients=[
                "tfmg:lithium_charge",
                "tfmg:capacitor_item",
                "ae2:quartz_glass",
                "ae2:fluix_crystal",
                "tfmg:magnetic_alloy_sheet",
            ],
            remove=["ae2:network/blocks/energy_energy_cell"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            recipe_id="industrial_colonies:ae2_coverage/dense_energy_cell",
            phase="Mekanized Industry",
            node="CR01 — Advanced Digital Crafting",
            order=80,
            comment="Rebuild the basic AE cell as a dense lithium bank with calculation control, a high-current capacitor, and laminated magnetic shielding",
            input_item="ae2:energy_cell",
            output="ae2:dense_energy_cell",
            ingredients=[
                "2x tfmg:lithium_charge",
                "tfmg:capacitor_item",
                "ae2:calculation_processor",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:quartz_vibrant_glass",
            ],
            remove=["ae2:network/blocks/energy_dense_energy_cell"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            recipe_id="industrial_colonies:ae2_coverage/crafting_accelerator",
            phase="Mekanized Industry",
            node="CR01 — Advanced Digital Crafting",
            order=81,
            comment="Turn a crafting-unit chassis into a parallel compute block with calculation logic, stress scheduling, motor timing, and local capacitance",
            input_item="ae2:crafting_unit",
            output="ae2:crafting_accelerator",
            ingredients=[
                "ae2:calculation_processor",
                "appliedcreate:advanced_stress_processor",
                "tfmg:electric_motor",
                "tfmg:capacitor_item",
                "tfmg:magnetic_alloy_sheet",
            ],
            remove=["ae2:network/crafting/cpu_crafting_accelerator"],
        ),
        _sequence(
            recipe_id="industrial_colonies:ae2_coverage/crafting_monitor",
            phase="Mekanized Industry",
            node="CR01 — Advanced Digital Crafting",
            order=82,
            comment="Instrument a crafting-unit chassis with a storage monitor, calculation logic, Create display hardware, and a shielded signal lead",
            input_item="ae2:crafting_unit",
            output="ae2:crafting_monitor",
            ingredients=[
                "ae2:storage_monitor",
                "ae2:calculation_processor",
                "create:display_board",
                "ae2:quartz_vibrant_glass",
                "tfmg:copper_wire",
            ],
            remove=["ae2:network/crafting/cpu_crafting_monitor"],
        ),
        _sequence(
            recipe_id="industrial_colonies:ae2_coverage/condenser",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=250,
            comment="Build the matter condenser around a pressure-rated TFMG tank, opposed matter-transfer cores, power entry, and engineering control",
            input_item="tfmg:steel_fluid_tank",
            output="ae2:condenser",
            ingredients=[
                "ae2:annihilation_core",
                "ae2:formation_core",
                "ae2:engineering_processor",
                "ae2:energy_acceptor",
                "ae2:quartz_vibrant_glass",
                "tfmg:capacitor_item",
            ],
            remove=["ae2:network/blocks/io_condenser"],
        ),
        _sequence(
            recipe_id="industrial_colonies:ae2_coverage/wireless_access_point",
            phase="High-Energy Grid",
            node="CR01 — Advanced ME BUS Technology",
            order=90,
            comment="Turn the wireless receiver into an amplified network station with a TFMG antenna coil, fluix backbone, and calculation control",
            input_item="ae2:wireless_receiver",
            output="ae2:wireless_access_point",
            ingredients=[
                "tfmg:large_coil",
                "ae2:calculation_processor",
                "ae2:fluix_smart_cable",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
            ],
            remove=["ae2:network/wireless_access_point"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
    ]


def _extendedae_recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            recipe_id="industrial_colonies:extendedae_coverage/concurrent_processor",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=260,
            comment="Package concurrent logic on the Brass line with both semiconductor polarities, local capacitance, and stress-aware scheduling",
            input_item="extendedae:concurrent_processor_print",
            output="extendedae:concurrent_processor",
            ingredients=[
                "ae2:printed_silicon",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "tfmg:capacitor_item",
                "appliedcreate:advanced_stress_processor",
                "ae2:fluix_dust",
            ],
            remove=[
                "extendedae:assembler/concurrent_processor",
                "extendedae:inscriber/concurrent_process",
            ],
        ),
        _sequence(
            recipe_id="industrial_colonies:extendedae_coverage/ingredient_buffer",
            phase="High-Energy Grid",
            node="CR01 — Advanced ME Storage",
            order=270,
            comment="Build a buffered autocrafting reservoir inside the ExtendedAE frame with a real cell housing and bidirectional matter-transfer control",
            input_item="extendedae:machine_frame",
            output="extendedae:ingredient_buffer",
            ingredients=[
                "ae2:item_cell_housing",
                "ae2:cell_component_4k",
                "ae2:annihilation_core",
                "ae2:formation_core",
                "ae2:quartz_glass",
                "tfmg:capacitor_item",
            ],
            remove=["extendedae:ingredient_buffer"],
        ),
        _sequence(
            recipe_id="industrial_colonies:extendedae_coverage/ex_drive",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=271,
            comment="Expand the standard ME drive with concurrent addressing, extra cell bays, capacity logic, and a dedicated TFMG control board",
            input_item="ae2:drive",
            output="extendedae:ex_drive",
            ingredients=[
                "extendedae:concurrent_processor",
                "ae2:capacity_card",
                "2x ae2:item_cell_housing",
                "ae2:speed_card",
                "tfmg:circuit_board",
            ],
            remove=["extendedae:assembler/ex_drive"],
        ),
        _sequence(
            recipe_id="industrial_colonies:extendedae_coverage/ex_molecular_assembler",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME Crafting Upgrade",
            order=272,
            comment="Refit the molecular assembler for high-throughput work with concurrent and engineering logic, stress scheduling, and precision motion",
            input_item="ae2:molecular_assembler",
            output="extendedae:ex_molecular_assembler",
            ingredients=[
                "extendedae:concurrent_processor",
                "ae2:engineering_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:speed_card",
                "create:precision_mechanism",
                "tfmg:capacitor_item",
            ],
            remove=["extendedae:assembler/ex_molecular_assembler"],
        ),
        _sequence(
            recipe_id="industrial_colonies:extendedae_coverage/ex_pattern_provider",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME Crafting Upgrade",
            order=273,
            comment="Scale the pattern provider with concurrent scheduling, accumulation memory, capacity control, and a dedicated Brass-line circuit board",
            input_item="ae2:pattern_provider",
            output="extendedae:ex_pattern_provider",
            ingredients=[
                "extendedae:concurrent_processor",
                "megacells:accumulation_processor",
                "ae2:capacity_card",
                "minecraft:crafting_table",
                "tfmg:circuit_board",
            ],
            remove=["extendedae:assembler/ex_pattern_provider"],
        ),
        _sequence(
            recipe_id="industrial_colonies:extendedae_coverage/wireless_hub",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=274,
            comment="Commission the wireless connector as a network hub with a full access point, dense power buffer, concurrent routing, and a large TFMG antenna coil",
            input_item="extendedae:wireless_connect",
            output="extendedae:wireless_hub",
            ingredients=[
                "ae2:wireless_access_point",
                "ae2:dense_energy_cell",
                "extendedae:concurrent_processor",
                "tfmg:large_coil",
                "ae2:calculation_processor",
            ],
            remove=["extendedae:assembler/wireless_hub"],
        ),
    ]


def _megacells_recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            recipe_id="industrial_colonies:megacells_coverage/cell_component_4m",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=300,
            comment="Bond four 1M memory planes into a 4M component with accumulation control, local capacitance, and a vibrant-glass data face",
            input_item="megacells:cell_component_1m",
            output="megacells:cell_component_4m",
            ingredients=[
                "3x megacells:cell_component_1m",
                "megacells:accumulation_processor",
                "tfmg:capacitor_item",
                "ae2:quartz_vibrant_glass",
            ],
            remove=["megacells:cells/cell_component_4m"],
        ),
        _sequence(
            recipe_id="industrial_colonies:megacells_coverage/cell_component_16m",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=301,
            comment="Stack four 4M planes around a spatial addressing layer with stress scheduling and magnetic shielding",
            input_item="megacells:cell_component_4m",
            output="megacells:cell_component_16m",
            ingredients=[
                "3x megacells:cell_component_4m",
                "ae2:spatial_cell_component_2",
                "appliedcreate:advanced_stress_processor",
                "tfmg:magnetic_alloy_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            remove=["megacells:cells/cell_component_16m"],
        ),
        _sequence(
            recipe_id="industrial_colonies:megacells_coverage/cell_component_64m",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=302,
            comment="Address four 16M planes through a concurrent processor, a 16-cubed spatial map, and matter-ball isolation",
            input_item="megacells:cell_component_16m",
            output="megacells:cell_component_64m",
            ingredients=[
                "3x megacells:cell_component_16m",
                "extendedae:concurrent_processor",
                "ae2:spatial_cell_component_16",
                "ae2:matter_ball",
                "ae2:quartz_vibrant_glass",
            ],
            remove=["megacells:cells/cell_component_64m"],
        ),
        _sequence(
            recipe_id="industrial_colonies:megacells_coverage/cell_component_256m",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=303,
            comment="Complete the 256M component from four 64M planes, full-scale spatial addressing, engineering control, and laminated magnetic containment",
            input_item="megacells:cell_component_64m",
            output="megacells:cell_component_256m",
            ingredients=[
                "3x megacells:cell_component_64m",
                "ae2:spatial_cell_component_128",
                "ae2:engineering_processor",
                "tfmg:laminated_magnetic_alloy_block",
                "ae2:matter_ball",
            ],
            remove=["megacells:cells/cell_component_256m"],
        ),
        _sequence(
            recipe_id="industrial_colonies:megacells_coverage/mega_energy_cell",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=310,
            comment="Scale the dense AE cell into a transformer-coupled lithium bank with accumulation telemetry and laminated magnetic containment",
            input_item="ae2:dense_energy_cell",
            output="megacells:mega_energy_cell",
            ingredients=[
                "megacells:accumulation_processor",
                "tfmg:transformer",
                "4x tfmg:lithium_charge",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:capacitor_item",
            ],
            remove=["megacells:crafting/mega_energy_cell"],
            deployer=COPPER_DEPLOYER,
            press=COPPER_PRESS,
        ),
        _sequence(
            recipe_id="industrial_colonies:megacells_coverage/mega_interface",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME System Upgrade",
            order=311,
            comment="Expand an ME interface with accumulation buffering, concurrent routing, high-capacity control, and dense fluix bandwidth",
            input_item="ae2:interface",
            output="megacells:mega_interface",
            ingredients=[
                "megacells:accumulation_processor",
                "extendedae:concurrent_processor",
                "ae2:capacity_card",
                "ae2:fluix_smart_dense_cable",
                "tfmg:capacitor_item",
            ],
            remove=["megacells:network/mega_interface"],
        ),
        _sequence(
            recipe_id="industrial_colonies:megacells_coverage/mega_pattern_provider",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME Crafting Upgrade",
            order=312,
            comment="Turn the standard provider into a massive pattern dispatcher with accumulation memory, concurrent scheduling, and engineering control",
            input_item="ae2:pattern_provider",
            output="megacells:mega_pattern_provider",
            ingredients=[
                "megacells:accumulation_processor",
                "extendedae:concurrent_processor",
                "ae2:engineering_processor",
                "ae2:crafting_card",
                "tfmg:circuit_board",
            ],
            remove=["megacells:network/mega_pattern_provider"],
        ),
        _sequence(
            recipe_id="industrial_colonies:megacells_coverage/mega_crafting_accelerator",
            phase="High-Energy Grid",
            node="CR01 — Enhanced ME Crafting Upgrade",
            order=313,
            comment="Convert the mega crafting chassis into a compute accelerator with concurrent scheduling, stress control, precision drive, and power buffering",
            input_item="megacells:mega_crafting_unit",
            output="megacells:mega_crafting_accelerator",
            ingredients=[
                "extendedae:concurrent_processor",
                "appliedcreate:advanced_stress_processor",
                "ae2:engineering_processor",
                "tfmg:electric_motor",
                "tfmg:capacitor_item",
            ],
            remove=["megacells:crafting/mega_crafting_accelerator"],
        ),
    ]


def _advancedae_recipes() -> list[dict[str, Any]]:
    return [
        _sequence(
            recipe_id="industrial_colonies:advanced_ae_coverage/quantum_processor",
            phase="High-Energy Grid",
            node="CR01 — Overclocked Processors",
            order=400,
            comment="Package two quantum processors on the Radiance line with bipolar TFMG semiconductors, accumulation logic, and stress-synchronized shielding",
            input_item="advanced_ae:printed_quantum_processor",
            output="2x advanced_ae:quantum_processor",
            ingredients=[
                "ae2:printed_silicon",
                "tfmg:n_semiconductor",
                "tfmg:p_semiconductor",
                "megacells:accumulation_processor",
                "appliedcreate:advanced_stress_processor",
                "tfmg:magnetic_alloy_sheet",
            ],
            remove=[
                "advanced_ae:quantum_processor",
                "advanced_ae:quantum_processor_eae",
            ],
            deployer=QUANTUM_DEPLOYER,
            press=QUANTUM_PRESS,
        ),
        _sequence(
            recipe_id="industrial_colonies:advanced_ae_coverage/quantum_storage_component",
            phase="High-Energy Grid",
            node="CR01 — Overclocked Processors",
            order=401,
            comment="Turn a 256M memory plane into quantum storage with full-scale spatial addressing, quantum control, and singularity isolation",
            input_item="megacells:cell_component_256m",
            output="advanced_ae:quantum_storage_component",
            ingredients=[
                "advanced_ae:quantum_processor",
                "ae2:spatial_cell_component_128",
                "advanced_ae:quantum_alloy_plate",
                "advanced_ae:shattered_singularity",
                "ae2:quartz_vibrant_glass",
            ],
            remove=["advanced_ae:quantum_storage_component"],
            deployer=QUANTUM_DEPLOYER,
            press=QUANTUM_PRESS,
        ),
        _sequence(
            recipe_id="industrial_colonies:advanced_ae_coverage/quantum_unit",
            phase="High-Energy Grid",
            node="CR01 — Overclocked Processors",
            order=402,
            comment="Refit the mega crafting chassis as a quantum compute unit with quantum and concurrent logic inside a singularity-shielded magnetic frame",
            input_item="megacells:mega_crafting_unit",
            output="advanced_ae:quantum_unit",
            ingredients=[
                "advanced_ae:quantum_processor",
                "extendedae:concurrent_processor",
                "advanced_ae:shattered_singularity",
                "advanced_ae:quantum_alloy_plate",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            remove=[
                "advanced_ae:eaequantumunit",
                "advanced_ae:quantumunit",
            ],
            deployer=QUANTUM_DEPLOYER,
            press=QUANTUM_PRESS,
        ),
        _sequence(
            recipe_id="industrial_colonies:advanced_ae_coverage/quantum_accelerator",
            phase="High-Energy Grid",
            node="CR01 — Overclocked Processors",
            order=403,
            comment="Instrument the quantum unit for accelerated execution with concurrent scheduling, stress timing, accumulation buffering, and singularity isolation",
            input_item="advanced_ae:quantum_unit",
            output="advanced_ae:quantum_accelerator",
            ingredients=[
                "advanced_ae:quantum_processor",
                "extendedae:concurrent_processor",
                "appliedcreate:advanced_stress_processor",
                "megacells:accumulation_processor",
                "advanced_ae:shattered_singularity",
                "tfmg:capacitor_item",
            ],
            remove=[
                "advanced_ae:eaequantumaccel",
                "advanced_ae:quantumaccel",
            ],
            deployer=QUANTUM_DEPLOYER,
            press=QUANTUM_PRESS,
        ),
        _sequence(
            recipe_id="industrial_colonies:advanced_ae_coverage/quantum_core",
            phase="High-Energy Grid",
            node="CR01 — Overclocked Processors",
            order=404,
            comment="Fuse quantum storage, acceleration, and control into a shielded central core instead of surrounding stock parts in another generic ring",
            input_item="advanced_ae:quantum_storage_component",
            output="advanced_ae:quantum_core",
            ingredients=[
                "advanced_ae:quantum_accelerator",
                "advanced_ae:quantum_unit",
                "2x advanced_ae:quantum_processor",
                "advanced_ae:shattered_singularity",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            remove=["advanced_ae:quantumcore"],
            deployer=QUANTUM_DEPLOYER,
            press=QUANTUM_PRESS,
        ),
        _mechanical(
            recipe_id="industrial_colonies:advanced_ae_coverage/quantum_crafter",
            phase="High-Energy Grid",
            node="CR01 — Overclocked Processors",
            order=405,
            comment="Lay out a full five-by-five quantum crafting lattice with a central molecular chamber, dedicated core, accelerator, pattern control, and compute unit",
            pattern=[
                "V E V",
                "QPCPQ",
                "EAMAE",
                "QPUQP",
                "V R V",
            ],
            key={
                "V": "ae2:quartz_vibrant_glass",
                "E": "ae2:engineering_processor",
                "Q": "advanced_ae:quantum_alloy_plate",
                "P": "advanced_ae:quantum_processor",
                "C": "advanced_ae:quantum_core",
                "A": "advanced_ae:quantum_accelerator",
                "M": "extendedae:ex_molecular_assembler",
                "U": "advanced_ae:quantum_unit",
                "R": "extendedae:ex_pattern_provider",
            },
            output="advanced_ae:quantum_crafter",
            remove=["advanced_ae:quantumcrafter"],
        ),
    ]


def _output_item(output: Any) -> str | None:
    if not isinstance(output, str):
        return None
    value = output.strip()
    if "x " in value and value.split("x ", 1)[0].isdigit():
        value = value.split("x ", 1)[1]
    return value if ":" in value else None


def _recipe_set() -> list[dict[str, Any]]:
    recipes = [
        *_ae2_recipes(),
        *_extendedae_recipes(),
        *_megacells_recipes(),
        *_advancedae_recipes(),
    ]
    ids = [recipe["id"] for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise ValueError("AE-family coverage defines duplicate managed recipe IDs")
    return recipes


def _assert_unclaimed(data: dict[str, Any], recipes: Iterable[dict[str, Any]]) -> None:
    recipes = list(recipes)
    managed_ids = {recipe["id"] for recipe in recipes}
    outputs = {_output_item(recipe["output"]) for recipe in recipes}
    outputs.discard(None)
    removals = {stock_id for recipe in recipes for stock_id in recipe["remove"]}

    for existing in data.get("recipes", []):
        if existing.get("id") in managed_ids:
            continue
        existing_output = _output_item(existing.get("output"))
        if existing_output in outputs:
            raise ValueError(
                f"AE-family coverage output {existing_output} is already managed by "
                f"{existing.get('id')}"
            )
        overlap = removals.intersection(existing.get("remove", []))
        if overlap:
            raise ValueError(
                f"AE-family coverage stock IDs are already claimed by "
                f"{existing.get('id')}: {sorted(overlap)}"
            )


def _upsert(data: dict[str, Any], recipe: dict[str, Any]) -> None:
    matches = [
        index
        for index, existing in enumerate(data.get("recipes", []))
        if existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"Duplicate managed recipe before upsert: {recipe['id']}")
    if matches:
        data["recipes"][matches[0]] = recipe
    else:
        data.setdefault("recipes", []).append(recipe)


def apply(data: dict[str, Any]) -> None:
    """Add the curated AE-family coverage wave to ``data`` in place."""

    recipes = _recipe_set()
    _assert_unclaimed(data, recipes)

    claimed_stock_ids = {
        stock_id for recipe in recipes for stock_id in recipe.get("remove", [])
    }
    data["additional_removals"] = [
        stock_id
        for stock_id in data.get("additional_removals", [])
        if stock_id not in claimed_stock_ids
    ]
    data["preserve_recipe_ids"] = [
        stock_id
        for stock_id in data.get("preserve_recipe_ids", [])
        if stock_id not in claimed_stock_ids
    ]

    for recipe in recipes:
        _upsert(data, recipe)
