"""Curated functional coverage for Create: Simulated.

Simulated ships a compact set of genuinely useful flight, sensing, control,
rope, and heavy-motion blocks alongside a much larger palette of handles,
nameplates, sails, portable-engine colours, and novelty items.  This module
manages only the former.  Existing Orbital recipes for the Physics Assembler,
Contraption Diagram, velocity/gimbal/optical sensors, Navigation Table, and
Docking Connector are intentionally left to ``recipe_design_v2_space_coverage``.

Importing this module has no filesystem or seed side effects.  ``apply`` is
idempotent and mutates only the supplied seed dictionary.
"""

from __future__ import annotations

import re
from typing import Any


COPPER_DEPLOYER = "createcasing:copper_deployer"
COPPER_PRESS = "createcasing:copper_press"
BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"

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
) -> dict[str, Any]:
    return {
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


def _sequence(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    input_item: str,
    transitional: str,
    output: str,
    steps: list[dict[str, str]],
    remove: list[str],
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
        "transitional": transitional,
        "output": output,
        "loops": loops,
        "steps": steps,
        "remove": remove,
        "exclusive_output": True,
    }


def _recipes() -> list[dict[str, Any]]:
    return [
        # Baseline elastic and mechanical controls.
        _shaped(
            "industrial_colonies:simulated/spring_batch",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=520,
            comment="Stamp four service springs from an iron-strip blank with four opposed nugget coils",
            pattern=[" N ", "NSN", " N "],
            key={
                "N": "minecraft:iron_nugget",
                "S": "create:iron_sheet",
            },
            output="4x simulated:spring",
            remove=["simulated:spring"],
        ),
        _shaped(
            "industrial_colonies:simulated/torsion_spring",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=521,
            comment="Seat opposed service springs around a shaft inside an Andesite torsion housing",
            pattern=[" S ", "SAS", " C "],
            key={
                "S": "simulated:spring",
                "A": "create:shaft",
                "C": "create:andesite_casing",
            },
            output="simulated:torsion_spring",
            remove=["simulated:torsion_spring"],
        ),
        _shaped(
            "industrial_colonies:simulated/directional_gearshift",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=522,
            comment="Add a compass-indexed redstone selector and service handle to a native Gearshift",
            pattern=[" C ", "HGH", " R "],
            key={
                "C": "minecraft:compass",
                "H": "simulated:iron_handle",
                "G": "create:gearshift",
                "R": "create:redstone_link",
            },
            output="simulated:directional_gearshift",
            remove=["simulated:directional_gearshift"],
        ),
        _shaped(
            "industrial_colonies:simulated/analog_transmission",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=523,
            comment="Build a continuously variable Brass transmission around opposed shafts, a precision gear train, and electron-tube feedback",
            pattern=[" E ", "SCS", "GPG"],
            key={
                "E": "create:electron_tube",
                "S": "create:shaft",
                "C": "create:brass_casing",
                "G": "create:cogwheel",
                "P": "create:precision_mechanism",
            },
            output="simulated:analog_transmission",
            remove=["simulated:analog_transmission"],
        ),
        # Copper sensing line.
        _shaped(
            "industrial_colonies:simulated/altitude_sensor",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=524,
            comment="Build a sealed Copper barometric sensor with a paper diaphragm, glass reference chamber, and wired readout",
            pattern=[" G ", "PWP", " C "],
            key={
                "G": "minecraft:glass_bottle",
                "P": "minecraft:paper",
                "W": "tfmg:copper_wire",
                "C": "create:copper_casing",
            },
            output="simulated:altitude_sensor",
            remove=["simulated:altitude_sensor"],
        ),
        _sequence(
            "industrial_colonies:simulated/laser_pointer",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=525,
            comment="Align an amethyst emitter, redstone source, and insulated lead inside a pressed Copper optical barrel",
            input_item="create:copper_casing",
            transitional="create:copper_casing",
            output="simulated:laser_pointer",
            steps=[
                _deploy("tfmg:copper_wire", COPPER_DEPLOYER),
                _deploy("minecraft:redstone_torch", COPPER_DEPLOYER),
                _deploy("minecraft:amethyst_shard", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
            remove=["simulated:laser_pointer"],
        ),
        _sequence(
            "industrial_colonies:simulated/laser_sensor",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=526,
            comment="Assemble a filtered Copper photoreceiver from tinted glass, an electron tube, amethyst optics, and a wired pickup",
            input_item="create:copper_casing",
            transitional="create:copper_casing",
            output="simulated:laser_sensor",
            steps=[
                _deploy("minecraft:tinted_glass", COPPER_DEPLOYER),
                _deploy("create:electron_tube", COPPER_DEPLOYER),
                _deploy("minecraft:amethyst_shard", COPPER_DEPLOYER),
                _deploy("tfmg:copper_wire", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
            remove=["simulated:laser_sensor"],
        ),
        # Electrical redstone-field components.
        _sequence(
            "industrial_colonies:simulated/redstone_inductor",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=527,
            comment="Wind a Copper spool over a magnetic-alloy core, add redstone excitation, and laminate the inductor on the Copper line",
            input_item="tfmg:magnetic_alloy_sheet",
            transitional="tfmg:magnetic_alloy_sheet",
            output="simulated:redstone_inductor",
            steps=[
                _deploy("tfmg:copper_spool", COPPER_DEPLOYER),
                _deploy("minecraft:redstone_torch", COPPER_DEPLOYER),
                _deploy("create:copper_sheet", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
            remove=["simulated:redstone_inductor"],
        ),
        _sequence(
            "industrial_colonies:simulated/redstone_magnet",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=528,
            comment="Instrument a TFMG permanent magnet with Copper pole faces, a redstone winding, and an electron-tube switch",
            input_item="tfmg:magnet",
            transitional="tfmg:magnet",
            output="simulated:redstone_magnet",
            steps=[
                _deploy("create:copper_sheet", COPPER_DEPLOYER),
                _deploy("minecraft:redstone", COPPER_DEPLOYER),
                _deploy("create:electron_tube", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
            remove=["simulated:redstone_magnet"],
        ),
        _sequence(
            "industrial_colonies:simulated/redstone_accumulator",
            phase="Electrical Manufacturing",
            node="CR01 — Control Electronics",
            order=529,
            comment="Convert a TFMG accumulator into an analog signal reservoir with rose-quartz memory, Brass electrodes, and tube regulation",
            input_item="tfmg:accumulator",
            transitional="tfmg:accumulator",
            output="simulated:redstone_accumulator",
            steps=[
                _deploy("create:polished_rose_quartz", COPPER_DEPLOYER),
                _deploy("create:brass_sheet", COPPER_DEPLOYER),
                _deploy("create:electron_tube", COPPER_DEPLOYER),
                _press(COPPER_PRESS),
            ],
            remove=["simulated:redstone_accumulator"],
        ),
        # Railway heavy-motion and air-transport hardware.
        _sequence(
            "industrial_colonies:simulated/engine_assembly",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=530,
            comment="Build the portable power core around a cast-iron frame with a TFMG cylinder, crankshaft, steel flywheel, and serviceable mechanism",
            input_item="tfmg:cast_iron_frame",
            transitional="simulated:incomplete_engine_assembly",
            output="simulated:engine_assembly",
            steps=[
                _deploy("tfmg:engine_cylinder", RAILWAY_DEPLOYER),
                _deploy("tfmg:crankshaft", RAILWAY_DEPLOYER),
                _deploy("tfmg:steel_flywheel", RAILWAY_DEPLOYER),
                _deploy("tfmg:steel_mechanism", RAILWAY_DEPLOYER),
                _press(RAILWAY_PRESS),
            ],
            remove=["simulated:sequenced_assembly/engine_assembly"],
        ),
        _sequence(
            "industrial_colonies:simulated/gyroscopic_mechanism",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=531,
            comment="Balance a precision rotor with paired magnetic bearings, a compass reference, Brass trim, and a sprung Railway mount",
            input_item="create:precision_mechanism",
            transitional="simulated:incomplete_gyroscopic_mechanism",
            output="simulated:gyroscopic_mechanism",
            steps=[
                _deploy("tfmg:magnetic_alloy_sheet", RAILWAY_DEPLOYER),
                _deploy("minecraft:compass", RAILWAY_DEPLOYER),
                _deploy("create:brass_sheet", RAILWAY_DEPLOYER),
                _deploy("simulated:spring", RAILWAY_DEPLOYER),
                _press(RAILWAY_PRESS),
            ],
            remove=["simulated:sequenced_assembly/gyroscopic_mechanism"],
            loops=2,
        ),
        _shaped(
            "industrial_colonies:simulated/portable_engine",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=532,
            comment="Package the completed engine assembly with a cast-iron fuel tank, throttle linkage, ventilation, and Railway service shell",
            pattern=["IVI", "TEF", "CRC"],
            key={
                "I": "create:iron_sheet",
                "V": "tfmg:cast_iron_fluid_tank",
                "T": "simulated:throttle_lever",
                "E": "simulated:engine_assembly",
                "F": "create:encased_fan",
                "C": "create:railway_casing",
                "R": "tfmg:steel_mechanism",
            },
            output="simulated:red_portable_engine",
            remove=["simulated:red_portable_engine"],
        ),
        _shaped(
            "industrial_colonies:simulated/rope_connector_batch",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=533,
            comment="Forge four rope-end eyes from heavy plates, metal brackets, and replaceable lead loops",
            pattern=[" L ", "BHB", " L "],
            key={
                "L": "minecraft:lead",
                "B": "create:metal_bracket",
                "H": "tfmg:heavy_plate",
            },
            output="4x simulated:rope_connector",
            remove=["simulated:rope_connector"],
        ),
        _shaped(
            "industrial_colonies:simulated/rope_coupling_batch",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=534,
            comment="Join paired rope eyes through a steel swivel mechanism to make two load-rated couplings",
            pattern=[" C ", "RMR", " C "],
            key={
                "C": "create:shaft",
                "R": "simulated:rope_connector",
                "M": "tfmg:steel_mechanism",
            },
            output="2x simulated:rope_coupling",
            remove=["simulated:rope_coupling"],
        ),
        _shaped(
            "industrial_colonies:simulated/rope_winch",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=535,
            comment="Build a Railway winch around a completed rope coupling, large reduction gear, through-shaft, and heavy brake",
            pattern=[" C ", "GSG", "RBR"],
            key={
                "C": "simulated:rope_coupling",
                "G": "create:large_cogwheel",
                "S": "create:shaft",
                "R": "create:railway_casing",
                "B": "tfmg:heavy_plate",
            },
            output="simulated:rope_winch",
            remove=["simulated:rope_winch"],
        ),
        _shaped(
            "industrial_colonies:simulated/swivel_bearing",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=536,
            comment="Mount a proven Mechanical Bearing in a Railway yoke with a large reduction gear and opposed sturdy pivot plates",
            pattern=[" P ", "GBG", " C "],
            key={
                "P": "create:sturdy_sheet",
                "G": "create:large_cogwheel",
                "B": "create:mechanical_bearing",
                "C": "create:railway_casing",
            },
            output="simulated:swivel_bearing",
            remove=["simulated:swivel_bearing"],
        ),
        _shaped(
            "industrial_colonies:simulated/throttle_lever",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=537,
            comment="Link an iron control handle to an analog transmission through a Brass quadrant and spring-return detent",
            pattern=[" H ", "SAS", " B "],
            key={
                "H": "simulated:iron_handle",
                "S": "simulated:spring",
                "A": "simulated:analog_transmission",
                "B": "create:brass_casing",
            },
            output="simulated:throttle_lever",
            remove=["simulated:throttle_lever"],
        ),
        _shaped(
            "industrial_colonies:simulated/steering_wheel",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=538,
            comment="Build a load-rated steering wheel around a large gear hub, directional transmission, twin grips, and Railway column",
            pattern=["H H", "GDG", " S "],
            key={
                "H": "simulated:iron_handle",
                "G": "create:large_cogwheel",
                "D": "simulated:directional_gearshift",
                "S": "create:railway_casing",
            },
            output="simulated:steering_wheel",
            remove=["simulated:steering_wheel"],
        ),
        _shaped(
            "industrial_colonies:simulated/auger_shaft",
            phase="Steel & Petroleum",
            node="CR01 — Air Transport",
            order=539,
            comment="Wrap a steel encased shaft with a continuous heavy helical flight and Railway drive collar",
            pattern=[" H ", "HSH", " C "],
            key={
                "H": "tfmg:heavy_plate",
                "S": "tfmg:steel_encased_shaft",
                "C": "create:railway_casing",
            },
            output="simulated:auger_shaft",
            remove=[
                "simulated:auger_shaft",
                "simulated:auger_shaft_from_auger_cogwheel",
            ],
        ),
        # Linked receivers genuinely need the Digital control-chip stage.
        _sequence(
            "industrial_colonies:simulated/directional_linked_receiver",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=540,
            comment="Program a Brass linked receiver with directional reference, a Create transmitter, and a manufactured control chip",
            input_item="create:brass_casing",
            transitional="create:brass_casing",
            output="simulated:directional_linked_receiver",
            steps=[
                _deploy("create:transmitter", BRASS_DEPLOYER),
                _deploy("minecraft:compass", BRASS_DEPLOYER),
                _deploy("create_connected:control_chip", BRASS_DEPLOYER),
                _deploy("create:iron_sheet", BRASS_DEPLOYER),
                _press(BRASS_PRESS),
            ],
            remove=["simulated:directional_linked_receiver"],
        ),
        _sequence(
            "industrial_colonies:simulated/modulating_linked_receiver",
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=541,
            comment="Program a second Brass receiver around an analog accumulator, transmitter, control chip, and gold modulation contact",
            input_item="create:brass_casing",
            transitional="create:brass_casing",
            output="simulated:modulating_linked_receiver",
            steps=[
                _deploy("create:transmitter", BRASS_DEPLOYER),
                _deploy("simulated:redstone_accumulator", BRASS_DEPLOYER),
                _deploy("create_connected:control_chip", BRASS_DEPLOYER),
                _deploy("create:golden_sheet", BRASS_DEPLOYER),
                _press(BRASS_PRESS),
            ],
            remove=["simulated:modulating_linked_receiver"],
        ),
    ]


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
        raise ValueError(f"Simulated removals are already globally claimed: {overlap}")

    preserved = set(data.get("preserve_recipe_ids", []))
    overlap = sorted(preserved.intersection(wanted_removals))
    if overlap:
        raise ValueError(f"Simulated coverage cannot remove preserved recipes: {overlap}")


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
    """Apply curated Simulated recipes without touching the filesystem."""

    additions = _recipes()
    _assert_unclaimed(data, additions)
    for recipe in additions:
        _upsert(data, recipe)
