"""TFMG electrical instruments and pump assemblies."""

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


def _sequence(
    comment: str,
    input_item: str,
    output: Any,
    ingredients: list[str],
    casing: str,
) -> dict[str, Any]:
    return {
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": 1,
        "steps": [
            {
                "op": "deploying",
                "ingredient": ingredient,
                "machine": f"createcasing:{casing}_deployer",
            }
            for ingredient in ingredients
        ]
        + [{"op": "pressing", "machine": f"createcasing:{casing}_press"}],
    }


def _upsert(data: dict[str, Any], recipe: dict[str, Any]) -> None:
    matches = [i for i, existing in enumerate(data["recipes"]) if existing["id"] == recipe["id"]]
    if len(matches) > 1:
        raise KeyError(f"Managed recipe is duplicated: {recipe['id']}")
    if matches:
        data["recipes"][matches[0]] = recipe
    else:
        data["recipes"].append(recipe)


def apply(data: dict[str, Any]) -> None:
    _upsert(
        data,
        {
            "id": "industrial_colonies:electronics/rotor",
            "node": "CR01 — Advanced Electronics Manufacturing",
            "phase": "Electrical Manufacturing",
            "order": 125,
            "type": "sequenced_assembly",
            "comment": "Wind the TFMG rotor around a shaft over two balanced Copper electromechanical passes instead of buying difficulty with a twelve-coil crafting ring",
            "input": "create:shaft",
            "transitional": "create:shaft",
            "output": "tfmg:rotor",
            "loops": 2,
            "steps": [
                {
                    "op": "deploying",
                    "ingredient": "tfmg:aluminum_sheet",
                    "machine": "createcasing:copper_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "tfmg:electromagnetic_coil",
                    "machine": "createcasing:copper_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "tfmg:magnetic_alloy_sheet",
                    "machine": "createcasing:copper_deployer",
                },
                {
                    "op": "deploying",
                    "ingredient": "tfmg:screw",
                    "machine": "createcasing:copper_deployer",
                },
                {"op": "pressing", "machine": "createcasing:copper_press"},
            ],
            "remove": ["tfmg:mechanical_crafting/rotor"],
            "exclusive_output": True,
        },
    )
    data["preserve_recipe_ids"] = [
        recipe_id
        for recipe_id in data.get("preserve_recipe_ids", [])
        if recipe_id != "tfmg:mechanical_crafting/rotor"
    ]

    _replace(
        data,
        "industrial_colonies:fluid_infrastructure/cast_iron_mechanical_pump",
        {
            "type": "mechanical_crafting",
            "comment": "Arrange the first pump as an inline cast-iron pipe, gear drive, and replaceable precision crank",
            "pattern": ["ICI", "PGP", " I "],
            "key": {
                "I": "tfmg:cast_iron_sheet",
                "C": "tfmg:cast_iron_pipe",
                "P": "create:precision_mechanism",
                "G": "create:cogwheel",
            },
            "output": "tfmg:cast_iron_mechanical_pump",
        },
    )
    _replace(
        data,
        "industrial_colonies:fluid_infrastructure/steel_mechanical_pump",
        {
            "type": "mechanical_crafting",
            "comment": "Arrange the pressure-rated pump around a steel pipe, geared drive, and serviceable steel mechanism",
            "pattern": ["HSH", "PGP", " H "],
            "key": {
                "H": "tfmg:heavy_plate",
                "S": "tfmg:steel_pipe",
                "P": "tfmg:steel_mechanism",
                "G": "create:cogwheel",
            },
            "output": "tfmg:steel_mechanical_pump",
        },
    )
    _replace(
        data,
        "industrial_colonies:fluid_infrastructure/electric_pump",
        _sequence(
            "Motorize the completed steel pump with one manufactured motor, control board, capacitor, and insulated power lead",
            "tfmg:steel_mechanical_pump",
            "tfmg:electric_pump",
            [
                "tfmg:electric_motor",
                "tfmg:circuit_board",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
                "tfmg:steel_mechanism",
            ],
            "copper",
        ),
    )
    _replace(
        data,
        "industrial_colonies:tfmg_heavy_electrical/electrode_holder",
        _sequence(
            "Build the high-current holder from a heavy casing, steel clamps, lead shielding, and paired copper feeds",
            "tfmg:heavy_machinery_casing",
            "tfmg:electrode_holder",
            [
                "#c:ingots/steel",
                "#c:ingots/steel",
                "#c:plates/lead",
                "tfmg:copper_wire",
                "tfmg:copper_wire",
            ],
            "railway",
        ),
    )
    _replace(
        data,
        "industrial_colonies:tfmg_heavy_electrical/portable_energy_interface",
        _sequence(
            "Convert a proven portable mechanical interface into a moving electrical contact with a wound spool and TFMG endpoint",
            "create:portable_storage_interface",
            "createaddition:portable_energy_interface",
            [
                "tfmg:copper_spool",
                "tfmg:cable_connector",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
            ],
            "copper",
        ),
    )
    _replace(
        data,
        "industrial_colonies:tfmg_heavy_electrical/transformer",
        _sequence(
            "Wind primary and secondary copper coils around a laminated magnetic core, then close the steel transformer enclosure",
            "tfmg:laminated_magnetic_alloy_block",
            "tfmg:transformer",
            [
                "tfmg:copper_spool",
                "tfmg:copper_spool",
                "tfmg:nickel_sheet",
                "tfmg:steel_casing",
                "tfmg:heavy_plate",
            ],
            "copper",
        ),
    )
    _replace(
        data,
        "industrial_colonies:tfmg_heavy_electrical/voltage_observer",
        _sequence(
            "Turn an aluminum instrument enclosure into a networked voltage observer using an actual voltmeter and discrete analog control stages",
            "tfmg:industrial_aluminum_casing",
            "tfmg:voltage_observer",
            [
                "tfmg:voltmeter",
                "tfmg:circuit_board",
                "tfmg:transistor_item",
                "tfmg:capacitor_item",
                "tfmg:copper_wire",
            ],
            "copper",
        ),
    )
    _replace(
        data,
        "industrial_colonies:tfmg_heavy_electrical/digital_adapter",
        _sequence(
            "Convert a proven wired modem into the Create power-network adapter with a populated TFMG board and isolated signal hardware",
            "computercraft:wired_modem",
            "createaddition:digital_adapter",
            [
                "tfmg:circuit_board",
                "create:brass_sheet",
                "create:electron_tube",
                "minecraft:redstone_torch",
                "tfmg:copper_wire",
            ],
            "brass",
        ),
    )
