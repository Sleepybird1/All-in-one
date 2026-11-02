"""TFMG and heavy-industry recipe redesign for the v2 migration.

The module is intentionally a pure seed transform: :func:`apply` mutates the
provided manifest dictionary and performs no file, registry, build, or deploy
work.  Ordinary source-mod recipes are restored instead of being copied into
the managed project, while the recipes retained here have a distinct physical
assembly or a useful Create Encased manufacturing environment.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


_RETIRED_MANAGED_RECIPES: dict[str, dict[str, tuple[str, ...]]] = {
    "industrial_colonies:machine/oil_processing/oil_hammer": {
        "stock": ("tfmg:crafting/materials/oil_hammer",),
        "outputs": ("tfmg:oil_hammer",),
    },
    "industrial_colonies:chemical_processing/accumulator": {
        "stock": (
            "tfmg:crafting/materials/accumulator",
            "tfmg:crafting/materials/accumulatorfrom_lithium",
        ),
        "outputs": ("tfmg:accumulator",),
    },
    "industrial_colonies:chemical_processing/cable_tube": {
        "stock": ("tfmg:crafting/materials/cable_tube",),
        "outputs": ("tfmg:cable_tube",),
    },
    "industrial_colonies:steelworks/coke_oven": {
        "stock": ("tfmg:crafting/materials/coke_oven",),
        "outputs": ("tfmg:coke_oven",),
    },
    "industrial_colonies:fluid_infrastructure/cast_iron_fluid_tank": {
        "stock": ("tfmg:crafting/materials/cast_iron_fluid_tank",),
        "outputs": ("tfmg:cast_iron_fluid_tank",),
    },
    "industrial_colonies:fluid_infrastructure/steel_fluid_tank": {
        "stock": ("tfmg:crafting/materials/steel_fluid_tank",),
        "outputs": ("tfmg:steel_fluid_tank",),
    },
    "industrial_colonies:engines/simple_large_engine": {
        "stock": ("tfmg:mechanical_crafting/simple_large_engine",),
        "outputs": ("tfmg:simple_large_engine",),
    },
    "industrial_colonies:engines/large_engine": {
        "stock": ("tfmg:mechanical_crafting/large_engine",),
        "outputs": ("tfmg:large_engine",),
    },
    "industrial_colonies:heavy_industry/winding_machine": {
        "stock": ("tfmg:crafting/materials/winding_machine",),
        "outputs": ("tfmg:winding_machine",),
    },
    "industrial_colonies:heavy_industry/industrial_mixer": {
        "stock": ("tfmg:crafting/materials/industrial_mixer",),
        "outputs": ("tfmg:industrial_mixer",),
    },
    "industrial_colonies:heavy_industry/smeltery_controller": {
        "stock": ("modernfoundry:smeltery/casting/seared/smeltery_controller",),
        "outputs": ("modernfoundry:smeltery_controller",),
    },
    "industrial_colonies:heavy_industry/foundry_controller": {
        "stock": ("modernfoundry:smeltery/casting/scorched/foundry_controller",),
        "outputs": ("modernfoundry:foundry_controller",),
    },
    "industrial_colonies:foundry_routes/create_metallurgy_casting_table": {
        "stock": ("createmetallurgy:crafting/content/casting_table",),
        "outputs": ("createmetallurgy:casting_table",),
    },
    "industrial_colonies:foundry_routes/create_metallurgy_casting_basin": {
        "stock": ("createmetallurgy:crafting/content/casting_basin",),
        "outputs": ("createmetallurgy:casting_basin",),
    },
    "industrial_colonies:foundry_routes/modern_scorched_basin": {
        "stock": ("modernfoundry:smeltery/scorched/basin",),
        "outputs": ("modernfoundry:scorched_basin",),
    },
    "industrial_colonies:foundry_routes/modern_scorched_drain": {
        "stock": (
            "modernfoundry:smeltery/scorched/drain",
            "modernfoundry:smeltery/scorched/drain_retextured",
        ),
        "outputs": ("modernfoundry:scorched_drain",),
    },
    "industrial_colonies:foundry_routes/modern_scorched_table": {
        "stock": ("modernfoundry:smeltery/scorched/table",),
        "outputs": ("modernfoundry:scorched_table",),
    },
}


def _recipes(data: dict[str, Any]) -> list[dict[str, Any]]:
    recipes = data.setdefault("recipes", [])
    if not isinstance(recipes, list):
        raise TypeError("managed recipe seed field 'recipes' must be a list")
    return recipes


def _index(data: dict[str, Any]) -> dict[str, int]:
    return {
        recipe["id"]: index
        for index, recipe in enumerate(_recipes(data))
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def _append_unique(data: dict[str, Any], field: str, values: tuple[str, ...]) -> None:
    current = data.setdefault(field, [])
    if not isinstance(current, list):
        raise TypeError(f"managed recipe seed field {field!r} must be a list")
    seen = set(current)
    for value in values:
        if value not in seen:
            current.append(value)
            seen.add(value)


def _remove_values(data: dict[str, Any], field: str, values: set[str]) -> None:
    current = data.get(field)
    if current is None:
        return
    if not isinstance(current, list):
        raise TypeError(f"managed recipe seed field {field!r} must be a list")
    data[field] = [value for value in current if value not in values]


def _replace_existing(
    data: dict[str, Any], recipe_id: str, body: dict[str, Any]
) -> bool:
    """Replace one exact managed recipe while retaining its exact output value.

    Several TFMG engine-cylinder outputs carry fuel component strings.  The
    output is therefore copied from the seed rather than reconstructed here.
    Returning ``False`` for an absent recipe makes the module safe when a later
    migration has intentionally retired that recipe.
    """

    indexes = _index(data)
    if recipe_id not in indexes:
        return False

    old = _recipes(data)[indexes[recipe_id]]
    replacement: dict[str, Any] = {"id": recipe_id}
    for key in ("node", "phase", "order"):
        if key in old:
            replacement[key] = deepcopy(old[key])

    replacement.update(deepcopy(body))
    if "output" not in replacement and "output" in old:
        replacement["output"] = deepcopy(old["output"])
    for key in ("remove", "exclusive_output", "if_mod_loaded", "depends_on"):
        if key not in replacement and key in old:
            replacement[key] = deepcopy(old[key])

    _recipes(data)[indexes[recipe_id]] = replacement
    return True


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _restore_source_owned_recipes(data: dict[str, Any]) -> None:
    retired_ids = set(_RETIRED_MANAGED_RECIPES)
    stock_ids = {
        stock_id
        for policy in _RETIRED_MANAGED_RECIPES.values()
        for stock_id in policy["stock"]
    }
    stock_outputs = tuple(
        output
        for policy in _RETIRED_MANAGED_RECIPES.values()
        for output in policy["outputs"]
    )

    data["recipes"] = [
        recipe
        for recipe in _recipes(data)
        if not (
            isinstance(recipe, dict)
            and isinstance(recipe.get("id"), str)
            and recipe["id"] in retired_ids
        )
    ]

    # A managed dependency cannot point to a recipe that has deliberately gone
    # back to its source mod.  The real ingredient remains the gameplay gate.
    for recipe in _recipes(data):
        dependencies = recipe.get("depends_on")
        if isinstance(dependencies, list):
            recipe["depends_on"] = [
                dependency
                for dependency in dependencies
                if dependency not in retired_ids
            ]

    _append_unique(data, "preserve_recipe_ids", tuple(sorted(stock_ids)))
    _append_unique(data, "exclude_outputs", stock_outputs)
    _remove_values(data, "additional_removals", stock_ids)

    # Coal coke and the TFMG rotor already have coherent source recipes.  Keep
    # both out of automatic recipe generation even though neither has a custom
    # managed recipe to retire in the current seed.
    _append_unique(
        data,
        "preserve_recipe_ids",
        ("tfmg:crafting/materials/coal_coke", "tfmg:mechanical_crafting/rotor"),
    )
    _append_unique(data, "exclude_outputs", ("tfmg:coal_coke", "tfmg:rotor"))


def _redesign_engine_cylinders(data: dict[str, Any]) -> None:
    _replace_existing(
        data,
        "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder",
        {
            "type": "compacting",
            "comment": (
                "Pressure-form the small diesel cylinder from two aluminum "
                "shell halves, a cast-iron liner, and one service screw"
            ),
            "machine": "createcasing:railway_press",
            "inputs": [
                "#c:plates/aluminum",
                "#c:plates/aluminum",
                "tfmg:cast_iron_sheet",
                "tfmg:screw",
            ],
            "remove": ["tfmg:engine_cylinder"],
            "exclusive_output": True,
            "depends_on": [],
        },
    )
    _replace_existing(
        data,
        "industrial_colonies:tfmg_heavy_electrical/engine_cylinder",
        {
            "type": "sequenced_assembly",
            "comment": (
                "Convert the formed diesel cylinder to spark ignition on the "
                "Copper electrical line; this is a short component process, "
                "not a full machine build"
            ),
            "input": "tfmg:diesel_engine_cylinder",
            "transitional": "tfmg:diesel_engine_cylinder",
            "loops": 1,
            "steps": [
                _deploy("tfmg:spark_plug", "createcasing:copper_deployer"),
                _deploy("tfmg:copper_wire", "createcasing:copper_deployer"),
                _press("createcasing:copper_press"),
            ],
            "remove": ["tfmg:engine_cylinder_spark_plug"],
            "exclusive_output": False,
            "depends_on": [
                "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder"
            ],
        },
    )


def _redesign_combustion_engines(data: dict[str, Any]) -> None:
    replacements: dict[str, dict[str, Any]] = {
        "industrial_colonies:engines/regular_engine": {
            "type": "mechanical_crafting",
            "comment": (
                "Build a matched pair of regular engines as cylinder heads, "
                "intake pipes, crankshaft line, gearbox, crankcase, and sump"
            ),
            "pattern": ["CCC", "PGP", "SMS", "HHH"],
            "key": {
                "C": "tfmg:simple_engine_cylinder",
                "P": "tfmg:steel_pipe",
                "G": "tfmg:engine_gearbox",
                "S": "create:shaft",
                "M": "tfmg:heavy_machinery_casing",
                "H": "tfmg:heavy_plate",
            },
            "remove": ["tfmg:crafting/materials/regular_engine"],
            "exclusive_output": True,
        },
        "industrial_colonies:engines/diesel_engine": {
            "type": "mechanical_crafting",
            "comment": (
                "Assemble the compact diesel generator vertically from its "
                "two cylinder heads, piston bank, crankcase, fuel tank, and bed"
            ),
            "pattern": ["C C", "PPP", "KRG", " T ", "HHH"],
            "key": {
                "C": "tfmg:diesel_engine_cylinder",
                "P": "createdieselgenerators:engine_piston",
                "K": "tfmg:crankshaft",
                "R": "tfmg:regular_engine",
                "G": "tfmg:engine_gearbox",
                "T": "tfmg:steel_fluid_tank",
                "H": "tfmg:heavy_plate",
            },
            "remove": ["createdieselgenerators:crafting/diesel_engine"],
            "exclusive_output": True,
        },
        "industrial_colonies:engines/engine_turbocharger": {
            "type": "mechanical_crafting",
            "comment": (
                "Build the turbocharger as an asymmetric aluminum intake, "
                "turbine wheel, balanced shaft, and steel exhaust cartridge"
            ),
            "pattern": ["APF", "BSB", "AHA"],
            "key": {
                "A": "tfmg:aluminum_pipe",
                "P": "create:propeller",
                "F": "tfmg:steel_pipe",
                "B": "tfmg:turbine_blade",
                "S": "create:shaft",
                "H": "tfmg:heavy_plate",
            },
            "remove": ["createdieselgenerators:crafting/engine_turbocharger"],
            "exclusive_output": True,
        },
        "industrial_colonies:engines/large_diesel_engine": {
            "type": "mechanical_crafting",
            "comment": (
                "Build the large diesel set as twin turbo heads over a piston "
                "bank, paired compact engines, central mechanical transmission, tanks, and bed"
            ),
            "pattern": [" T T ", "P C P", "D L D", "F G F", "HHHHH"],
            "key": {
                "T": "createdieselgenerators:engine_turbocharger",
                "P": "createdieselgenerators:engine_piston",
                "C": "tfmg:transmission",
                "D": "createdieselgenerators:diesel_engine",
                "L": "tfmg:large_engine",
                "F": "tfmg:steel_fluid_tank",
                "G": "tfmg:engine_gearbox",
                "H": "tfmg:heavy_plate",
            },
            "remove": ["createdieselgenerators:crafting/large_diesel_engine"],
            "exclusive_output": True,
        },
        "industrial_colonies:engines/turbine_engine": {
            "type": "mechanical_crafting",
            "comment": (
                "Assemble a matched turbine pair as a staged aluminum duct "
                "around its propeller, blade rows, turbo core, and gearbox"
            ),
            "pattern": ["APA", "ABA", "ATA", "ABA", "HGH"],
            "key": {
                "A": "tfmg:aluminum_pipe",
                "P": "create:propeller",
                "B": "tfmg:turbine_blade",
                "T": "createdieselgenerators:engine_turbocharger",
                "H": "tfmg:heavy_plate",
                "G": "tfmg:engine_gearbox",
            },
            "remove": ["tfmg:crafting/materials/turbine_engine"],
            "exclusive_output": True,
        },
        "industrial_colonies:engines/huge_diesel_engine": {
            "type": "mechanical_crafting",
            "comment": (
                "Construct the huge generator as two complete large sets around "
                "a turbine-assisted TFMG core, redundant tanks, and a full bed"
            ),
            "pattern": ["T   T", "P L P", "D U D", "F G F", "HHHHH"],
            "key": {
                "T": "createdieselgenerators:engine_turbocharger",
                "P": "createdieselgenerators:engine_piston",
                "L": "tfmg:large_engine",
                "D": "createdieselgenerators:large_diesel_engine",
                "U": "tfmg:turbine_engine",
                "F": "tfmg:steel_fluid_tank",
                "G": "tfmg:engine_gearbox",
                "H": "tfmg:heavy_plate",
            },
            "remove": ["createdieselgenerators:crafting/huge_diesel_engine"],
            "exclusive_output": True,
        },
        "industrial_colonies:engines/radial_engine": {
            "type": "mechanical_crafting",
            "comment": (
                "Arrange eight spark-ignition cylinders radially around an "
                "aluminum crank plate, shaft, intake pipes, and geared hub"
            ),
            "pattern": [" C C ", "C A C", "P S P", "C G C", " C C "],
            "key": {
                "C": "tfmg:engine_cylinder",
                "A": "tfmg:aluminum_sheet",
                "P": "tfmg:aluminum_pipe",
                "S": "create:shaft",
                "G": "tfmg:engine_gearbox",
            },
            "remove": ["tfmg:crafting/materials/radial_engine"],
            "exclusive_output": True,
        },
        "industrial_colonies:engines/electronic_engine_controller": {
            "type": "mechanical_crafting",
            "comment": (
                "Lay out the analog engine-control cabinet as an insulated "
                "wiring harness, sensor pair, discrete board, and drive linkage"
            ),
            "pattern": [" RWR ", "VCHCV", "WTBTW", " SMS ", " RMR "],
            "key": {
                "R": "tfmg:rubber_sheet",
                "W": "#c:wires/copper",
                "V": "tfmg:voltmeter",
                "C": "tfmg:capacitor_item",
                "H": "tfmg:heavy_machinery_casing",
                "T": "tfmg:transistor_item",
                "B": "tfmg:circuit_board",
                "S": "create:shaft",
                "M": "tfmg:steel_mechanism",
            },
            "remove": ["tfmg:mechanical_crafting/engine_controller"],
            "exclusive_output": True,
        },
    }
    for recipe_id, body in replacements.items():
        _replace_existing(data, recipe_id, body)


def _redesign_foundry_machines(data: dict[str, Any]) -> None:
    _replace_existing(
        data,
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_mixer",
        {
            "type": "sequenced_assembly",
            "comment": (
                "Refit the proven TFMG industrial mixer with a sturdy whisk, "
                "refractory liner, and copper thermal jacket on the Railway "
                "heavy-assembly line"
            ),
            "input": "tfmg:industrial_mixer",
            "transitional": "tfmg:industrial_mixer",
            "loops": 1,
            "steps": [
                _deploy(
                    "createmetallurgy:sturdy_whisk",
                    "createcasing:railway_deployer",
                ),
                _deploy(
                    "createmetallurgy:refractory_mortar",
                    "createcasing:railway_deployer",
                ),
                _deploy(
                    "create:copper_casing",
                    "createcasing:railway_deployer",
                ),
                _press("createcasing:railway_press"),
            ],
            "remove": ["createmetallurgy:crafting/content/foundry_mixer"],
            "exclusive_output": True,
            "depends_on": [],
        },
    )
    _replace_existing(
        data,
        "industrial_colonies:heavy_industry/scorched_alloyer",
        {
            "type": "shaped",
            "comment": (
                "Build the compact Scorched Alloyer as a refractory shell around "
                "its ingot gauge and a replaceable TFMG mixer blade"
            ),
            "pattern": ["BGB", "BMB", "BBB"],
            "key": {
                "B": "modernfoundry:scorched_brick",
                "G": "modernfoundry:scorched_ingot_gauge",
                "M": "tfmg:mixer_blade",
            },
            "remove": ["modernfoundry:smeltery/scorched/alloyer"],
            "exclusive_output": True,
            "depends_on": [],
        },
    )


def _redesign_safe_electrics(data: dict[str, Any]) -> None:
    # These exact transitional items are registered by installed TFMG 1.2.0.
    # No industrial_colonies Java item is introduced by either sequence.
    _replace_existing(
        data,
        "industrial_colonies:early_electricity/generator",
        {
            "type": "sequenced_assembly",
            "comment": (
                "Build the first generator on the Copper electromechanical line "
                "from a shaft, wound copper, a brass frame, and one precision core"
            ),
            "input": "create:shaft",
            "transitional": "tfmg:unfinished_generator",
            "loops": 1,
            "steps": [
                _deploy("tfmg:copper_spool", "createcasing:copper_deployer"),
                _deploy("create:brass_casing", "createcasing:copper_deployer"),
                _deploy("create:precision_mechanism", "createcasing:copper_deployer"),
                _deploy("create:copper_sheet", "createcasing:copper_deployer"),
                _press("createcasing:copper_press"),
            ],
            "remove": ["tfmg:sequenced_assembly/generator"],
            "exclusive_output": True,
        },
    )
    _replace_existing(
        data,
        "industrial_colonies:early_electricity/electric_motor",
        {
            "type": "sequenced_assembly",
            "comment": (
                "Reverse a proven generator into a motor with polarized magnets, "
                "nickel laminations, copper leads, and an Andesite drive housing"
            ),
            "input": "tfmg:generator",
            "transitional": "tfmg:unfinished_electric_motor",
            "loops": 1,
            "steps": [
                _deploy("tfmg:magnet", "createcasing:copper_deployer"),
                _deploy("tfmg:nickel_sheet", "createcasing:copper_deployer"),
                _deploy("tfmg:copper_wire", "createcasing:copper_deployer"),
                _deploy("create:andesite_casing", "createcasing:copper_deployer"),
                _press("createcasing:copper_press"),
            ],
            "remove": ["tfmg:sequenced_assembly/motor"],
            "exclusive_output": True,
        },
    )

    # TFMG has no registered unfinished rotor, and the seed has no exact
    # managed tfmg:rotor recipe.  Its stock mechanical-crafting recipe is
    # intentionally preserved above instead of inventing an unsafe transition.


def _remove_preservation_conflicts(data: dict[str, Any]) -> None:
    replaced_stock_ids = {
        "tfmg:engine_cylinder",
        "tfmg:engine_cylinder_spark_plug",
        "tfmg:crafting/materials/regular_engine",
        "createdieselgenerators:crafting/diesel_engine",
        "createdieselgenerators:crafting/engine_turbocharger",
        "createdieselgenerators:crafting/large_diesel_engine",
        "tfmg:crafting/materials/turbine_engine",
        "createdieselgenerators:crafting/huge_diesel_engine",
        "tfmg:crafting/materials/radial_engine",
        "tfmg:mechanical_crafting/engine_controller",
        "createmetallurgy:crafting/content/foundry_mixer",
        "modernfoundry:smeltery/scorched/alloyer",
        "tfmg:sequenced_assembly/generator",
        "tfmg:sequenced_assembly/motor",
    }
    _remove_values(data, "preserve_recipe_ids", replaced_stock_ids)


def apply(data: dict[str, Any]) -> None:
    """Apply the TFMG/Create Encased redesign to ``data`` in place."""

    _restore_source_owned_recipes(data)
    _redesign_engine_cylinders(data)
    _redesign_combustion_engines(data)
    _redesign_foundry_machines(data)
    _redesign_safe_electrics(data)
    _remove_preservation_conflicts(data)
