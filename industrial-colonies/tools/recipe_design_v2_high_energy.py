"""High-energy grid and ME integration recipe silhouettes."""

from __future__ import annotations

from typing import Any


def _replace(data: dict[str, Any], recipe_id: str, body: dict[str, Any]) -> None:
    matches = [i for i, recipe in enumerate(data["recipes"]) if recipe["id"] == recipe_id]
    if len(matches) != 1:
        raise KeyError(f"Expected exactly one {recipe_id}, found {len(matches)}")
    old = data["recipes"][matches[0]]
    replacement: dict[str, Any] = {"id": recipe_id}
    for key in ("node", "phase", "order"):
        if key in old:
            replacement[key] = old[key]
    replacement.update(body)
    for key in ("remove", "exclusive_output", "if_mod_loaded", "depends_on"):
        if key not in replacement and key in old:
            replacement[key] = old[key]
    data["recipes"][matches[0]] = replacement


def apply(data: dict[str, Any]) -> None:
    _replace(
        data,
        "industrial_colonies:high_voltage/current_transformer",
        {
            "type": "sequenced_assembly",
            "comment": "Instrument a laminated transformer core with paired terminals, sensing resistors, protected leads, and a ceramic enclosure",
            "input": "electroenergetics:transformer_core",
            "transitional": "electroenergetics:transformer_core",
            "output": "electroenergetics:current_transformer",
            "loops": 1,
            "steps": [
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:connector",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:connector",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:resistor",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:insulated_wire",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "#minecraft:terracotta",
                    "machine": "createcasing:railway_deployer",
                },
                {"op": "pressing", "machine": "createcasing:railway_press"},
            ],
        },
    )
    _replace(
        data,
        "industrial_colonies:high_voltage/voltage_regulator",
        {
            "type": "sequenced_assembly",
            "comment": "Build the regulator cabinet around a completed transformer, sensing transformer, redundant breakers, and local energy buffer",
            "input": "electroenergetics:transformer",
            "transitional": "electroenergetics:transformer",
            "output": "electroenergetics:voltage_regulator",
            "loops": 1,
            "steps": [
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:current_transformer",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:miniature_circuit_breaker",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:miniature_circuit_breaker",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:accumulator",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:copper_wire_spool",
                    "machine": "createcasing:railway_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "electroenergetics:resistor",
                    "machine": "createcasing:railway_deployer",
                },
                {"op": "pressing", "machine": "createcasing:railway_press"},
            ],
        },
    )

    _replace(
        data,
        "industrial_colonies:appliedcreate/kinetic_energy_acceptor",
        {
            "type": "mechanical_crafting",
            "comment": "Lay out the kinetic-to-ME converter as a generator, fluix bus, motor, and controlled energy-entry cabinet",
            "pattern": ["GFM", "WAW", "CPC"],
            "key": {
                "G": "tfmg:generator",
                "F": "ae2:fluix_glass_cable",
                "M": "tfmg:electric_motor",
                "W": "tfmg:copper_wire",
                "A": "ae2:energy_acceptor",
                "C": "create:brass_casing",
                "P": "appliedcreate:stress_processor",
            },
            "output": "appliedcreate:kinetic_energy_acceptor",
        },
    )
    _replace(
        data,
        "industrial_colonies:appliedcreate/me_gearbox",
        {
            "type": "mechanical_crafting",
            "comment": "Build the remote kinetic gateway as an open service frame with physical gearboxes around a dense P2P stress core",
            "pattern": ["GDDG", "P  P", "AKKA", "GDDG"],
            "key": {
                "G": "create:gearbox",
                "D": "ae2:fluix_smart_dense_cable",
                "P": "ae2:me_p2p_tunnel",
                "A": "appliedcreate:advanced_stress_processor",
                "K": "appliedcreate:stress_storage_component_1k",
            },
            "output": "appliedcreate:me_gearbox",
        },
    )
    _replace(
        data,
        "industrial_colonies:extendedae/machine_frame",
        {
            "type": "mechanical_crafting",
            "comment": "Construct the ExtendedAE chassis as an Entro-and-quartz shell around a steel frame, smart bus, and stress controller",
            "pattern": ["EQE", "WSW", "ICI"],
            "key": {
                "E": "extendedae:entro_ingot",
                "Q": "ae2:quartz_glass",
                "W": "ae2:fluix_smart_cable",
                "S": "tfmg:steel_casing",
                "I": "tfmg:steel_mechanism",
                "C": "appliedcreate:advanced_stress_processor",
            },
            "output": "extendedae:machine_frame",
        },
    )
    _replace(
        data,
        "industrial_colonies:extendedae/crystal_assembler",
        {
            "type": "mechanical_crafting",
            "comment": "Arrange the Crystal Assembler around two manipulators, a terminal, a crystal tank, and its ExtendedAE chassis",
            "pattern": ["MTM", "PKP", "QFQ"],
            "key": {
                "M": "create:mechanical_arm",
                "T": "ae2:crafting_terminal",
                "P": "ae2:engineering_processor",
                "K": "ae2:sky_stone_tank",
                "Q": "ae2:quartz_glass",
                "F": "extendedae:machine_frame",
            },
            "output": "extendedae:crystal_assembler",
        },
    )
    _replace(
        data,
        "industrial_colonies:appliedcreate/stress_storage_component_1k",
        {
            "type": "sequenced_assembly",
            "comment": "Wind and populate a buffered stress matrix over two recognizable Brass electronics passes",
            "input": "ae2:cell_component_4k",
            "transitional": "industrial_colonies:unfinished_stress_storage_component",
            "output": "appliedcreate:stress_storage_component_1k",
            "loops": 2,
            "steps": [
                {
                    "op": "deploying",
                    "ingredient": "appliedcreate:stress_processor",
                    "machine": "createcasing:brass_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "tfmg:capacitor_item",
                    "machine": "createcasing:brass_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "tfmg:copper_wire",
                    "machine": "createcasing:brass_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "tfmg:magnetic_alloy_sheet",
                    "machine": "createcasing:brass_deployer",
                },
                {"op": "pressing", "machine": "createcasing:brass_press"},
            ],
        },
    )
