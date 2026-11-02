"""Functional Create Encased acquisition coverage.

The seed's ``machine_families`` already expands into the main Press, Deployer,
Mixer, Saw, Fan, Roller, Depot, Gearbox, Clutch, Chain Conveyor, Automatic
Clutch, and Configurable Gearbox ladders.  This module deliberately builds on
that coverage instead of duplicating it:

* the full Railway family becomes a Steel-era parallel heavy branch because
  engine, foundry, and cannon recipes require several Railway machines before
  Electrical Manufacturing;
* the four Steel-era recipes that accidentally called for Industrial Iron
  machines are retargeted to those Railway machines;
* useful missing contraption, logistics, slicer, and transmission variants get
  prior-tier upgrade recipes; and
* the Andesite/Copper/Brass material transmission pieces get explicit,
  machine-appropriate batch routes.

Wood palettes, every possible encased shaft/cog colour combination, Zinc,
Shadow Steel, Creative, steam-whistle, and fluid-palette duplicates remain
stock/decorative on purpose.  Importing this module has no side effects;
``apply`` is idempotent and mutates only the supplied seed dictionary.
"""

from __future__ import annotations

import re
from typing import Any


_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")

_OUTPUT_SUFFIX = {
    "drill": "mechanical_drill",
    "harvester": "mechanical_harvester",
    "plough": "mechanical_plough",
    "portable_storage_interface": "portable_storage_interface",
    "gearshift": "gearshift",
    "chain_drive": "encased_chain_drive",
    "adjustable_chain_drive": "adjustable_chain_gearshift",
    "slicer": "slicer",
}

_ROLE_LABEL = {
    "drill": "Mechanical Drill",
    "harvester": "Mechanical Harvester",
    "plough": "Mechanical Plough",
    "portable_storage_interface": "Portable Storage Interface",
    "gearshift": "Gearshift",
    "chain_drive": "Encased Chain Drive",
    "adjustable_chain_drive": "Adjustable Chain Gearshift",
    "slicer": "Mechanical Slicer",
}

_ROLE_PART = {
    "drill": "create:sturdy_sheet",
    "harvester": "create:iron_sheet",
    "plough": "create:iron_sheet",
    "portable_storage_interface": "create:chute",
    "gearshift": "minecraft:redstone",
    "chain_drive": "create:shaft",
    "adjustable_chain_drive": "create:electron_tube",
    "slicer": "create:turntable",
}

# Each missing functional kind has its own readable silhouette.  The prior-tier
# machine is B, the tier casing C, structural plate P, drive D, control K, and
# the role-specific working part R.
_ROLE_PATTERN = {
    "drill": ["  R", "PBP", "CDC"],
    "harvester": ["R R", "PBP", "CDC"],
    "plough": ["R R", " B ", "PKP"],
    "portable_storage_interface": [" P ", "RBR", "CDC"],
    "gearshift": [" R ", "DBD", "PKP"],
    "chain_drive": [" D ", "CBC", "P P"],
    "adjustable_chain_drive": ["RKR", "DBD", "PCP"],
    "slicer": [" R ", "PBP", "DCD"],
}

_TIER_SPECS: tuple[dict[str, Any], ...] = (
    {
        "tier": "copper",
        "source_tier": "native Create",
        "phase": "Steam & Brass",
        "node": "CR01 — Advanced Mechanical Technology",
        "order": 410,
        "casing": "create:copper_casing",
        "plate": "create:copper_sheet",
        "control": "create:electron_tube",
        "drive": "create:shaft",
        "roles": (
            "drill",
            "harvester",
            "plough",
            "portable_storage_interface",
            "gearshift",
            "chain_drive",
            "adjustable_chain_drive",
            # Slicers only register when the optional Slice & Dice mod is loaded.
        ),
        "sources": {
            "drill": "create:mechanical_drill",
            "harvester": "create:mechanical_harvester",
            "plough": "create:mechanical_plough",
            "portable_storage_interface": "create:portable_storage_interface",
            "gearshift": "create:gearshift",
            "chain_drive": "create:encased_chain_drive",
            "adjustable_chain_drive": "create:adjustable_chain_gearshift",
            "slicer": "create:turntable",
        },
    },
    {
        "tier": "brass",
        "source_tier": "Copper",
        "phase": "Electrical Manufacturing",
        "node": "CR01 — Advanced Electronics Manufacturing",
        "order": 430,
        "casing": "create:brass_casing",
        "plate": "create:brass_sheet",
        "control": "tfmg:circuit_board",
        "drive": "create:precision_mechanism",
        "roles": (
            "drill",
            "harvester",
            "plough",
            "portable_storage_interface",
            "gearshift",
            "chain_drive",
            "adjustable_chain_drive",
            # Slicers only register when the optional Slice & Dice mod is loaded.
        ),
    },
    {
        "tier": "railway",
        "source_tier": "Copper heavy tooling",
        "phase": "Steel & Petroleum",
        "node": "CR01 — The Steel Age",
        "order": 450,
        "casing": "create:railway_casing",
        "plate": "tfmg:heavy_plate",
        "control": "create:electron_tube",
        "drive": "tfmg:steel_mechanism",
        "roles": (
            "drill",
            "portable_storage_interface",
            "gearshift",
            "chain_drive",
            "adjustable_chain_drive",
            # Slicers only register when the optional Slice & Dice mod is loaded.
        ),
        "sources": {
            "drill": "createcasing:copper_mechanical_drill",
            "portable_storage_interface": "createcasing:copper_portable_storage_interface",
            "gearshift": "createcasing:copper_gearshift",
            "chain_drive": "createcasing:copper_encased_chain_drive",
            "adjustable_chain_drive": "createcasing:copper_adjustable_chain_gearshift",
            "slicer": "createcasing:copper_slicer",
        },
    },
    {
        "tier": "industrial_iron",
        "source_tier": "Railway",
        "phase": "Mekanized Industry",
        "node": "CR01 — Modular Machinery",
        "order": 470,
        "casing": "create:industrial_iron_block",
        "plate": "tfmg:heavy_plate",
        "control": "mekanism:basic_control_circuit",
        "drive": "tfmg:electric_motor",
        "roles": (
            "drill",
            "portable_storage_interface",
            "gearshift",
            "chain_drive",
            "adjustable_chain_drive",
            # Slicers only register when the optional Slice & Dice mod is loaded.
        ),
    },
    {
        "tier": "weathered_iron",
        "source_tier": "Industrial Iron",
        "phase": "High-Energy Grid",
        "node": "CR01 — Precision Engineering",
        "order": 490,
        "casing": "create:weathered_iron_block",
        "plate": "create:iron_sheet",
        "control": "mekanism:advanced_control_circuit",
        "drive": "ae2:calculation_processor",
        "roles": (
            "drill",
            "gearshift",
            "chain_drive",
            "adjustable_chain_drive",
            # Slicers only register when the optional Slice & Dice mod is loaded.
        ),
    },
    {
        "tier": "refined_radiance",
        "source_tier": "Weathered Iron",
        "phase": "Nuclear Engineering",
        "node": "CR01 — Core Engineering",
        "order": 510,
        "casing": "create:refined_radiance_casing",
        "plate": "create:refined_radiance",
        "control": "mekanism:elite_control_circuit",
        "drive": "ae2:engineering_processor",
        "roles": (
            "drill",
            "gearshift",
            "chain_drive",
            "adjustable_chain_drive",
            # Slicers only register when the optional Slice & Dice mod is loaded.
        ),
    },
)


def _item_id(value: Any) -> str | None:
    if isinstance(value, dict):
        item_id = value.get("id")
        return item_id if isinstance(item_id, str) else None
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(1) if match else value.strip()


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


def _deploying(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    machine: str,
    input_item: str,
    held: str,
    output: str,
    remove: list[str],
) -> dict[str, Any]:
    return {
        "id": recipe_id,
        "phase": phase,
        "node": node,
        "order": order,
        "type": "deploying",
        "comment": comment,
        "machine": machine,
        "input": input_item,
        "held": held,
        "output": output,
        "remove": remove,
        "exclusive_output": True,
    }


def _cutting(
    recipe_id: str,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    machine: str,
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
        "machine": machine,
        "input": input_item,
        "output": output,
        "processing_time": 80,
        "remove": remove,
        "exclusive_output": True,
    }


def _andesite_controls() -> list[dict[str, Any]]:
    return [
        _shaped(
            "industrial_colonies:createcasing/andesite_automatic_clutch",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=215,
            comment="Add a redstone-link actuator and mechanical return shaft to a native Clutch before upgrading it into later casing families",
            pattern=[" R ", "ACA", " S "],
            key={
                "R": "create:redstone_link",
                "A": "create:andesite_alloy",
                "C": "create:clutch",
                "S": "create:shaft",
            },
            output="createcasing:andesite_automatic_clutch",
            remove=["createcasing:crafting/auto_clutch/andesite"],
        ),
        _shaped(
            "industrial_colonies:createcasing/andesite_configurable_gearbox",
            phase="Steam & Brass",
            node="CR01 — Advanced Redstone",
            order=216,
            comment="Build the baseline configurable gearbox around a native Gearshift, opposed cogs, and an Andesite service enclosure",
            pattern=[" C ", "GAG", " R "],
            key={
                "C": "create:redstone_link",
                "G": "create:cogwheel",
                "A": "create:gearshift",
                "R": "create:andesite_casing",
            },
            output="createcasing:andesite_configurable_gearbox",
            remove=["createcasing:crafting/configurable_gearbox/andesite"],
        ),
    ]


def _material_transmission_recipes() -> list[dict[str, Any]]:
    return [
        _shaped(
            "industrial_colonies:createcasing/andesite_cogwheel_batch",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=217,
            comment="Build four baseline cog hubs around a pair of standard shafts without requiring the later Deployer",
            pattern=[" A ", "ASA", " A "],
            key={"A": "create:andesite_alloy", "S": "create:shaft"},
            output="4x createcasing:andesite_cogwheel",
            remove=[
                "createcasing:crafting/cogwheels/andesite_alloy",
                "createcasing:deploying/cogwheels/andesite_alloy",
            ],
        ),
        _shaped(
            "industrial_colonies:createcasing/andesite_large_cogwheel_batch",
            phase="Mechanical Foundations",
            node="CR01 — Mechanical Technology",
            order=218,
            comment="Build two broad Andesite gear rims around two completed small hubs instead of free shapeless conversion",
            pattern=[" A ", "ACA", " A "],
            key={"A": "create:andesite_alloy", "C": "createcasing:andesite_cogwheel"},
            output="2x createcasing:andesite_large_cogwheel",
            remove=[
                "createcasing:crafting/large_cogwheels/andesite_alloy",
                "createcasing:crafting/large_cogwheels/andesite_alloy_from_small",
                "createcasing:deploying/large_cogwheels/andesite_alloy",
            ],
        ),
        _cutting(
            "industrial_colonies:createcasing/copper_shaft_batch",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=219,
            comment="Cut a Copper ingot into six conductive transmission shafts on the Copper mechanical-saw line",
            machine="createcasing:copper_mechanical_saw",
            input_item="minecraft:copper_ingot",
            output="6x createcasing:copper_shaft",
            remove=["createcasing:cutting/copper_ingot"],
        ),
        _deploying(
            "industrial_colonies:createcasing/copper_cogwheel_batch",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=220,
            comment="Form two conductive cog hubs by fitting Copper sheets to cut Copper shafts on the Copper line",
            machine="createcasing:copper_deployer",
            input_item="createcasing:copper_shaft",
            held="create:copper_sheet",
            output="2x createcasing:copper_cogwheel",
            remove=[
                "createcasing:crafting/cogwheels/copper",
                "createcasing:deploying/cogwheels/copper",
            ],
        ),
        _shaped(
            "industrial_colonies:createcasing/copper_large_cogwheel_batch",
            phase="Steam & Brass",
            node="CR01 — Advanced Mechanical Technology",
            order=221,
            comment="Rivet two broad Copper gear rims around paired conductive cog hubs",
            pattern=[" P ", "PCP", " P "],
            key={"P": "create:copper_sheet", "C": "createcasing:copper_cogwheel"},
            output="2x createcasing:copper_large_cogwheel",
            remove=[
                "createcasing:crafting/large_cogwheels/copper",
                "createcasing:crafting/large_cogwheels/copper_from_small",
                "createcasing:deploying/large_cogwheels/copper",
            ],
        ),
        _cutting(
            "industrial_colonies:createcasing/brass_shaft_batch",
            phase="Electrical Manufacturing",
            node="CR01 — Advanced Electronics Manufacturing",
            order=222,
            comment="Cut a Brass ingot into six low-backlash precision shafts on the Brass mechanical-saw line",
            machine="createcasing:brass_mechanical_saw",
            input_item="create:brass_ingot",
            output="6x createcasing:brass_shaft",
            remove=["createcasing:cutting/brass_ingot"],
        ),
        _deploying(
            "industrial_colonies:createcasing/brass_cogwheel_batch",
            phase="Electrical Manufacturing",
            node="CR01 — Advanced Electronics Manufacturing",
            order=223,
            comment="Fit Brass sheets to two cut precision shafts in the Brass assembly environment",
            machine="createcasing:brass_deployer",
            input_item="createcasing:brass_shaft",
            held="create:brass_sheet",
            output="2x createcasing:brass_cogwheel",
            remove=[
                "createcasing:crafting/cogwheels/brass",
                "createcasing:deploying/cogwheels/brass",
            ],
        ),
        _shaped(
            "industrial_colonies:createcasing/brass_large_cogwheel_batch",
            phase="Electrical Manufacturing",
            node="CR01 — Advanced Electronics Manufacturing",
            order=224,
            comment="Rivet two balanced Brass gear rims around paired precision cog hubs",
            pattern=[" P ", "PCP", " P "],
            key={"P": "create:brass_sheet", "C": "createcasing:brass_cogwheel"},
            output="2x createcasing:brass_large_cogwheel",
            remove=[
                "createcasing:crafting/large_cogwheels/brass",
                "createcasing:crafting/large_cogwheels/brass_from_small",
                "createcasing:deploying/large_cogwheels/brass",
            ],
        ),
    ]


def _source_for(tier_index: int, role: str, spec: dict[str, Any]) -> str:
    explicit_sources = spec.get("sources", {})
    if role in explicit_sources:
        return explicit_sources[role]
    prior_tier = _TIER_SPECS[tier_index - 1]["tier"]
    return f"createcasing:{prior_tier}_{_OUTPUT_SUFFIX[role]}"


def _missing_functional_upgrades() -> list[dict[str, Any]]:
    recipes: list[dict[str, Any]] = []
    for tier_index, spec in enumerate(_TIER_SPECS):
        tier = spec["tier"]
        for role_index, role in enumerate(spec["roles"]):
            output_suffix = _OUTPUT_SUFFIX[role]
            source = _source_for(tier_index, role, spec)
            label = _ROLE_LABEL[role]
            pattern = _ROLE_PATTERN[role]
            symbols = set("".join(pattern).replace(" ", ""))
            all_keys = {
                "P": spec["plate"],
                "C": spec["casing"],
                "B": source,
                "D": spec["drive"],
                "K": spec["control"],
                "R": _ROLE_PART[role],
            }
            recipes.append(
                _shaped(
                    f"industrial_colonies:createcasing/{tier}/{role}",
                    phase=spec["phase"],
                    node=spec["node"],
                    order=spec["order"] + role_index,
                    comment=(
                        f"Upgrade the {spec['source_tier']} {label} into the "
                        f"{tier.replace('_', ' ').title()} functional environment "
                        "around its original serviceable machine core"
                    ),
                    pattern=pattern,
                    key={symbol: item for symbol, item in all_keys.items() if symbol in symbols},
                    output=f"createcasing:{tier}_{output_suffix}",
                    remove=[f"createcasing:crafting/{role}/{tier}"],
                )
            )
    return recipes


def _recipes() -> list[dict[str, Any]]:
    return (
        _andesite_controls()
        + _material_transmission_recipes()
        + _missing_functional_upgrades()
    )


def _family_output_ids(data: dict[str, Any]) -> set[str]:
    outputs: set[str] = set()
    generated_suffix = {
        "fan": "encased_fan",
        "saw": "mechanical_saw",
        "roller": "mechanical_roller",
    }
    for family in data.get("machine_families", []):
        tier = family.get("tier")
        if not isinstance(tier, str):
            continue
        for kind in family.get("kinds", []):
            outputs.add(f"createcasing:{tier}_{generated_suffix.get(kind, kind)}")
        for entry in family.get("recipes", []):
            output = _item_id(entry.get("output")) if isinstance(entry, dict) else None
            if output:
                outputs.add(output)
    return outputs


def _patch_machine_families(data: dict[str, Any]) -> None:
    families = data.get("machine_families", [])
    by_tier: dict[str, dict[str, Any]] = {}
    for family in families:
        tier = family.get("tier")
        if tier in by_tier:
            raise ValueError(f"Create Encased machine family is duplicated: {tier}")
        if isinstance(tier, str):
            by_tier[tier] = family

    required = {"copper", "railway"}
    missing = sorted(required.difference(by_tier))
    if missing:
        raise ValueError(f"Create Encased coverage requires machine families: {missing}")

    # Give the Copper control ladder a real Create Encased Andesite parent.
    copper_sources = by_tier["copper"].setdefault("source_items", {})
    copper_sources["automatic_clutch"] = "createcasing:andesite_automatic_clutch"
    copper_sources["configurable_gearbox"] = "createcasing:andesite_configurable_gearbox"

    # The entire Railway line is heavy Steel-era tooling.  Press and Deployer
    # inherit the already-available explicit Brass machines; every other kind
    # branches in parallel from its Copper counterpart so this does not drag
    # the Brass electronics family backward.
    railway = by_tier["railway"]
    railway["source_tier"] = "Copper tooling with Brass Press/Deployer"
    railway["phase"] = "Steel & Petroleum"
    railway["control"] = "create:electron_tube"
    required_kinds = [
        "press",
        "deployer",
        "mixer",
        "saw",
        "fan",
        "roller",
        "depot",
        "gearbox",
        "clutch",
        "chain_conveyor",
        "automatic_clutch",
        "configurable_gearbox",
    ]
    if "kinds" in railway:
        existing_kinds = [kind for kind in railway["kinds"] if kind in required_kinds]
        railway["kinds"] = existing_kinds + [
            kind for kind in required_kinds if kind not in existing_kinds
        ]
    railway_sources = railway.setdefault("source_items", {})
    railway_sources.update(
        {
            "press": "createcasing:brass_press",
            "deployer": "createcasing:brass_deployer",
            "mixer": "createcasing:copper_mixer",
            "saw": "createcasing:copper_mechanical_saw",
            "fan": "createcasing:copper_encased_fan",
            "roller": "createcasing:copper_mechanical_roller",
            "depot": "createcasing:copper_depot",
            "gearbox": "createcasing:copper_gearbox",
            "clutch": "createcasing:copper_clutch",
            "chain_conveyor": "createcasing:copper_chain_conveyor",
            "automatic_clutch": "createcasing:copper_automatic_clutch",
            "configurable_gearbox": "createcasing:copper_configurable_gearbox",
        }
    )


def _retarget_steel_machine_prerequisites(data: dict[str, Any]) -> None:
    target_ids = {
        "industrial_colonies:fluid_infrastructure/fireproof_chemical_vat",
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_basin",
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_lid",
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_mixer",
    }
    recipes_by_id = {recipe.get("id"): recipe for recipe in data.get("recipes", [])}
    missing = sorted(target_ids.difference(recipes_by_id))
    if missing:
        raise ValueError(f"Steel Create Encased prerequisite recipes are missing: {missing}")

    replacements = {
        "createcasing:industrial_iron_press": "createcasing:railway_press",
        "createcasing:industrial_iron_deployer": "createcasing:railway_deployer",
    }
    for recipe_id in sorted(target_ids):
        recipe = recipes_by_id[recipe_id]
        machine = recipe.get("machine")
        if machine in replacements:
            recipe["machine"] = replacements[machine]
        for step in recipe.get("steps", []):
            machine = step.get("machine") if isinstance(step, dict) else None
            if machine in replacements:
                step["machine"] = replacements[machine]
        if recipe_id.endswith("create_metallurgy_foundry_mixer"):
            recipe["comment"] = recipe["comment"].replace(
                "on Industrial Iron", "on the Railway heavy-assembly line"
            )


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

    family_overlap = sorted(set(wanted_outputs).intersection(_family_output_ids(data)))
    if family_overlap:
        raise ValueError(
            f"Create Encased explicit coverage duplicates machine-family outputs: {family_overlap}"
        )

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
        raise ValueError(f"Create Encased removals are already globally claimed: {overlap}")

    preserved = set(data.get("preserve_recipe_ids", []))
    overlap = sorted(preserved.intersection(wanted_removals))
    if overlap:
        raise ValueError(f"Create Encased coverage cannot remove preserved recipes: {overlap}")


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
    """Apply Create Encased coverage without reading or writing the filesystem."""

    _patch_machine_families(data)
    _retarget_steel_machine_prerequisites(data)
    additions = _recipes()
    _assert_unclaimed(data, additions)
    for recipe in additions:
        _upsert(data, recipe)
