"""Create Encased tier-family progression redesign for recipe pass v3.

This transform owns only the already-managed ``createcasing`` acquisition
ladder.  The old machine-family expander could only emit one family of 3x3
templates, which made a Copper saw and a Refined-Radiance controller feel like
the same recipe with different expensive trim.  V3 expands those families into
explicit recipes so that every tier can use the manufacturing process that its
place in the pack actually calls for:

* Copper upgrades native Create machinery on the native Deployer/Press line;
* Brass is the populated precision/electronics line;
* Railway machines are readable 4x4 steel fabrications using their completed
  Brass predecessors, rather than 3x3 ingredient rings;
* Weathered Iron is the first serious electrically controlled machine-building
  line and is also the platform that bootstraps manufactured ATM currency;
* Industrial Iron adds Mekanism/AE control, HDPE and magnetic construction for
  late machines; and
* Refined Radiance combines the Industrial machine, nuclear Yellorium, atomic
  alloy, late ATM alloy, elite logic and engineering processors in a ten-load
  assembly followed by the Industrial press.

The live KubeJSGen edit of ``industrial_colonies:manufacturing/brass_press`` is
authoritative here: ``CPC / EBE / LSL`` where C is the TFMG capacitor, P the
Precision Mechanism, E the Electron Tube, B the Copper Press, L the TFMG
plastic sheet and S the Brass Casing.  The user's related Brass Deployer edit
is preserved as ``PEP / LBL / TST``.

Negative audit (intentionally unchanged)
-----------------------------------------

Ten coherent foundation recipes remain under their existing owners: the two
Andesite control devices plus Andesite/Copper/Brass shaft and cog batches.
They are material transmission or baseline control hardware, not tier-machine
construction.  The catalog's un-managed wood palettes, decorative encased
shaft/cog permutations, Zinc/Shadow-Steel/Creative palettes, whistles and
fluid-palette duplicates also remain stock.  Pulling those hundreds of visual
variants into progression would add recipe noise without a new factory job.

``apply`` is an in-memory, idempotent transform.  It neither reads nor writes
the live pack and deliberately refuses partial coverage, duplicate outputs,
3x3 Railway cards, compacted electronics, or a broken Brass Press reference.
"""

from __future__ import annotations

import re
from typing import Any, Iterable


Recipe = dict[str, Any]


_COUNTED_ITEM = re.compile(
    r"^\s*(?:\d+x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)\s*$"
)

_OUTPUT_SUFFIX = {
    "press": "press",
    "deployer": "deployer",
    "mixer": "mixer",
    "saw": "mechanical_saw",
    "fan": "encased_fan",
    "roller": "mechanical_roller",
    "depot": "depot",
    "gearbox": "gearbox",
    "clutch": "clutch",
    "chain_conveyor": "chain_conveyor",
    "automatic_clutch": "automatic_clutch",
    "configurable_gearbox": "configurable_gearbox",
    "drill": "mechanical_drill",
    "harvester": "mechanical_harvester",
    "plough": "mechanical_plough",
    "portable_storage_interface": "portable_storage_interface",
    "gearshift": "gearshift",
    "chain_drive": "encased_chain_drive",
    "adjustable_chain_drive": "adjustable_chain_gearshift",
    "slicer": "slicer",
}

_STOCK_KIND = {
    "fan": "encased_fan",
    "saw": "saw",
    "roller": "roller",
    "automatic_clutch": "auto_clutch",
}

_ALL_ROLES = tuple(_OUTPUT_SUFFIX)
_FAMILY_ROLES = (
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
)

_TIER_ROLES: dict[str, tuple[str, ...]] = {
    "copper": _ALL_ROLES,
    "brass": _ALL_ROLES,
    "railway": _FAMILY_ROLES
    + (
        "drill",
        "portable_storage_interface",
        "gearshift",
        "chain_drive",
        "adjustable_chain_drive",
        "slicer",
    ),
    "weathered_iron": _FAMILY_ROLES
    + ("drill", "gearshift", "chain_drive", "adjustable_chain_drive", "slicer"),
    "industrial_iron": _FAMILY_ROLES
    + (
        "drill",
        "portable_storage_interface",
        "gearshift",
        "chain_drive",
        "adjustable_chain_drive",
        "slicer",
    ),
    "refined_radiance": _FAMILY_ROLES
    + ("drill", "gearshift", "chain_drive", "adjustable_chain_drive", "slicer"),
}

_TARGET_TIERS = tuple(_TIER_ROLES)

# The user deleted the original Railway Saw card from the live project. Its v3
# replacement is a materially different 4x4 fabrication, so it receives a new
# identity and returns as a fresh pending review instead of silently reviving
# the deleted card under its old UID.
_RAILWAY_SAW_REPROPOSAL_ID = "industrial_colonies:v3_createcasing/railway_saw"

_FOUNDATION_OUTPUTS = {
    "createcasing:andesite_automatic_clutch",
    "createcasing:andesite_configurable_gearbox",
    "createcasing:andesite_cogwheel",
    "createcasing:andesite_large_cogwheel",
    "createcasing:copper_shaft",
    "createcasing:copper_cogwheel",
    "createcasing:copper_large_cogwheel",
    "createcasing:brass_shaft",
    "createcasing:brass_cogwheel",
    "createcasing:brass_large_cogwheel",
}

NEGATIVE_AUDIT = {
    "preserved_managed_foundations": tuple(sorted(_FOUNDATION_OUTPUTS)),
    "preserved_stock_categories": (
        "wood and bamboo casing palettes",
        "decorative encased shaft/cog/large-cog permutations",
        "zinc, shadow-steel, creative and purely visual casing palettes",
        "steam-whistle palette variants",
        "fluid-pipe/tank/valve palette duplicates not already managed",
    ),
    "reason": (
        "These recipes are coherent material conversions, baseline controls, "
        "or visual variants; changing them would not create a new factory job."
    ),
}


_NATIVE_SOURCE = {
    "press": "create:mechanical_press",
    "deployer": "create:deployer",
    "mixer": "create:mechanical_mixer",
    "saw": "create:mechanical_saw",
    "fan": "create:encased_fan",
    "roller": "create:mechanical_roller",
    "depot": "create:depot",
    "gearbox": "create:gearbox",
    "clutch": "create:clutch",
    "chain_conveyor": "create:chain_conveyor",
    "automatic_clutch": "createcasing:andesite_automatic_clutch",
    "configurable_gearbox": "createcasing:andesite_configurable_gearbox",
    "drill": "create:mechanical_drill",
    "harvester": "create:mechanical_harvester",
    "plough": "create:mechanical_plough",
    "portable_storage_interface": "create:portable_storage_interface",
    "gearshift": "create:gearshift",
    "chain_drive": "create:encased_chain_drive",
    "adjustable_chain_drive": "create:adjustable_chain_gearshift",
    "slicer": "create:turntable",
}


_COPPER_PARTS: dict[str, tuple[str, str]] = {
    "mixer": ("create:whisk", "create:shaft"),
    "saw": ("create:iron_sheet", "create:shaft"),
    "fan": ("create:propeller", "create:shaft"),
    "roller": ("create:crushing_wheel", "create:sturdy_sheet"),
    "depot": ("create:iron_sheet", "create:chute"),
    "gearbox": ("create:cogwheel", "create:large_cogwheel"),
    "clutch": ("minecraft:redstone", "create:electron_tube"),
    "chain_conveyor": ("create:metal_bracket", "create:shaft"),
    "automatic_clutch": ("create:redstone_link", "create:electron_tube"),
    "configurable_gearbox": ("create:precision_mechanism", "create:electron_tube"),
    "drill": ("create:sturdy_sheet", "create:shaft"),
    "harvester": ("create:iron_sheet", "create:cogwheel"),
    "plough": ("create:iron_sheet", "create:sturdy_sheet"),
    "portable_storage_interface": ("create:chute", "create:brass_funnel"),
    "gearshift": ("minecraft:redstone", "create:cogwheel"),
    "chain_drive": ("create:shaft", "create:cogwheel"),
    "adjustable_chain_drive": ("create:electron_tube", "create:analog_lever"),
    "slicer": ("create:turntable", "create:iron_sheet"),
}

_BRASS_PARTS: dict[str, tuple[str, str]] = {
    "mixer": ("tfmg:electric_motor", "create:whisk"),
    "saw": ("tfmg:electric_motor", "create:sturdy_sheet"),
    "fan": ("tfmg:electric_motor", "tfmg:capacitor_item"),
    "roller": ("tfmg:electric_motor", "tfmg:heavy_plate"),
    "depot": ("create:content_observer", "create:electron_tube"),
    "gearbox": ("create:large_cogwheel", "tfmg:resistor"),
    "clutch": ("create:redstone_link", "tfmg:transistor_item"),
    "chain_conveyor": ("tfmg:electric_motor", "create:metal_bracket"),
    "automatic_clutch": ("create:redstone_link", "tfmg:transistor_item"),
    "configurable_gearbox": ("tfmg:transistor_item", "tfmg:resistor"),
    "drill": ("tfmg:electric_motor", "create:sturdy_sheet"),
    "harvester": ("tfmg:electric_motor", "create:iron_sheet"),
    "plough": ("tfmg:electric_motor", "tfmg:heavy_plate"),
    "portable_storage_interface": ("create:content_observer", "create:brass_funnel"),
    "gearshift": ("create:redstone_link", "tfmg:resistor"),
    "chain_drive": ("tfmg:electric_motor", "createcasing:brass_cogwheel"),
    "adjustable_chain_drive": ("create:analog_lever", "tfmg:transistor_item"),
    "slicer": ("tfmg:electric_motor", "create:sturdy_sheet"),
}


# Every Railway role draws a different physical silhouette in the 4x4 grid.
# B is the completed Brass machine; the remaining symbols are structure,
# enclosure, drive, insulation, control and the role-specific working part.
_RAILWAY_PATTERNS: dict[str, list[str]] = {
    "press": [" HHH", " EMH", "PCB ", "SSSS"],
    "deployer": ["  RH", " EMH", "PCB ", " SSS"],
    "mixer": ["M HH", " CEC", " PB ", "SSSS"],
    "saw": [" HH ", "HME ", " CB ", "SSSS"],
    "fan": [" HH ", "HMER", " CB ", "SSSS"],
    "roller": ["HHHH", " CMH", "EPB ", "SSSS"],
    "depot": ["HHHH", " CCB", "PEM ", "SSSS"],
    "gearbox": [" M M", "HCCH", "EBC ", "SSSP"],
    "clutch": ["  R ", "MECH", "HBEH", "SSSP"],
    "chain_conveyor": ["M  M", "HCCE", " PBP", "SSSS"],
    "automatic_clutch": ["  R ", "MECH", "HB E", "SSSP"],
    "configurable_gearbox": ["R  R", "MECM", "HCBH", "SSSP"],
    "drill": [" HM ", " CCH", "EPB ", " SSR"],
    "harvester": ["M  M", "HCBH", "PECE", "RRRR"],
    "plough": ["   M", " CBE", " HHH", "RRR "],
    "portable_storage_interface": ["H  H", "CPBC", "M  E", "SSSS"],
    "gearshift": [" R  ", " ME ", "HCBH", "SSSP"],
    "chain_drive": [" M M", " CEC", "HCBH", " S S"],
    "adjustable_chain_drive": ["R  R", "MEM ", "HCBH", "PCES"],
    "slicer": [" HR ", " MCH", "EPB ", "SSSS"],
}

_RAILWAY_PARTS: dict[str, tuple[str, str]] = {
    "press": ("tfmg:copper_wire", "create:shaft"),
    "deployer": ("create:electron_tube", "create:brass_hand"),
    "mixer": ("tfmg:copper_wire", "create:whisk"),
    "saw": ("tfmg:copper_wire", "create:sturdy_sheet"),
    "fan": ("create:electron_tube", "create:propeller"),
    "roller": ("tfmg:copper_wire", "create:crushing_wheel"),
    "depot": ("create:content_observer", "create:iron_sheet"),
    "gearbox": ("create:electron_tube", "create:large_cogwheel"),
    "clutch": ("tfmg:circuit_board", "create:redstone_link"),
    "chain_conveyor": ("tfmg:copper_wire", "create:metal_bracket"),
    "automatic_clutch": ("tfmg:circuit_board", "tfmg:transistor_item"),
    "configurable_gearbox": ("tfmg:circuit_board", "tfmg:n_semiconductor"),
    "drill": ("tfmg:copper_wire", "create:sturdy_sheet"),
    "harvester": ("create:electron_tube", "create:iron_sheet"),
    "plough": ("tfmg:copper_wire", "create:sturdy_sheet"),
    "portable_storage_interface": ("tfmg:circuit_board", "tfmg:transistor_item"),
    "gearshift": ("tfmg:circuit_board", "create:redstone_link"),
    "chain_drive": ("tfmg:copper_wire", "create:shaft"),
    "adjustable_chain_drive": ("tfmg:circuit_board", "tfmg:p_semiconductor"),
    "slicer": ("tfmg:copper_wire", "create:sturdy_sheet"),
}

_WEATHERED_COMMON = (
    "create:weathered_iron_block",
    "tfmg:steel_casing",
    "tfmg:circuit_board",
    "tfmg:plastic_sheet",
    "mekanism:basic_control_circuit",
    "tfmg:magnetic_alloy_sheet",
)

_INDUSTRIAL_COMMON = (
    "create:industrial_iron_block",
    "tfmg:heavy_machinery_casing",
    "mekanism:advanced_control_circuit",
    "ae2:calculation_processor",
    "tfmg:magnetic_alloy_sheet",
    "mekanism:hdpe_sheet",
    "tfmg:heavy_plate",
)

_RADIANCE_COMMON = (
    "create:refined_radiance_casing",
    "create:refined_radiance",
    "bigreactors:yellorium_ingot",
    "allthemodium:vibranium_allthemodium_alloy_ingot",
    "mekanism:elite_control_circuit",
    "ae2:engineering_processor",
    "tfmg:laminated_magnetic_alloy_block",
    "mekanism:alloy_atomic",
)

_WEATHERED_PARTS: dict[str, tuple[str, str]] = {
    "press": ("tfmg:electric_motor", "modernfoundry:cobalt_ingot"),
    "deployer": ("create:brass_hand", "tfmg:transistor_item"),
    "mixer": ("create:whisk", "tfmg:electric_motor"),
    "saw": ("create:sturdy_sheet", "modernfoundry:cobalt_ingot"),
    "fan": ("create:propeller", "tfmg:electric_motor"),
    "roller": ("create:crushing_wheel", "modernfoundry:cobalt_ingot"),
    "depot": ("create:content_observer", "tfmg:capacitor_item"),
    "gearbox": ("create:large_cogwheel", "tfmg:electric_motor"),
    "clutch": ("create:redstone_link", "tfmg:resistor"),
    "chain_conveyor": ("create:metal_bracket", "tfmg:electric_motor"),
    "automatic_clutch": ("create:redstone_link", "tfmg:transistor_item"),
    "configurable_gearbox": ("create:precision_mechanism", "tfmg:n_semiconductor"),
    "drill": ("create:sturdy_sheet", "tfmg:electric_motor"),
    "harvester": ("create:iron_sheet", "tfmg:electric_motor"),
    "plough": ("create:sturdy_sheet", "tfmg:electric_motor"),
    "portable_storage_interface": ("create:content_observer", "tfmg:capacitor_item"),
    "gearshift": ("create:redstone_link", "tfmg:resistor"),
    "chain_drive": ("create:large_cogwheel", "tfmg:electric_motor"),
    "adjustable_chain_drive": ("create:analog_lever", "tfmg:p_semiconductor"),
    "slicer": ("create:sturdy_sheet", "tfmg:electric_motor"),
}

_INDUSTRIAL_PARTS: dict[str, tuple[str, str]] = {
    "press": ("modernfoundry:cobalt_ingot", "tfmg:electric_motor"),
    "deployer": ("create:brass_hand", "tfmg:transistor_item"),
    "mixer": ("create:whisk", "modernfoundry:cobalt_ingot"),
    "saw": ("create:sturdy_sheet", "modernfoundry:cobalt_ingot"),
    "fan": ("create:propeller", "tfmg:lithium_charge"),
    "roller": ("create:crushing_wheel", "modernfoundry:cobalt_ingot"),
    "depot": ("create:content_observer", "tfmg:lithium_charge"),
    "gearbox": ("create:large_cogwheel", "tfmg:laminated_magnetic_alloy_block"),
    "clutch": ("create:redstone_link", "tfmg:lithium_charge"),
    "chain_conveyor": ("create:metal_bracket", "tfmg:electric_motor"),
    "automatic_clutch": ("create:redstone_link", "tfmg:transistor_item"),
    "configurable_gearbox": ("create:precision_mechanism", "tfmg:n_semiconductor"),
    "drill": ("create:sturdy_sheet", "modernfoundry:cobalt_ingot"),
    "harvester": ("create:iron_sheet", "tfmg:electric_motor"),
    "plough": ("create:sturdy_sheet", "tfmg:electric_motor"),
    "portable_storage_interface": ("create:content_observer", "tfmg:lithium_charge"),
    "gearshift": ("create:redstone_link", "tfmg:resistor"),
    "chain_drive": ("create:large_cogwheel", "tfmg:electric_motor"),
    "adjustable_chain_drive": ("create:analog_lever", "tfmg:p_semiconductor"),
    "slicer": ("create:sturdy_sheet", "modernfoundry:cobalt_ingot"),
}

_RADIANCE_PARTS: dict[str, tuple[str, str]] = {
    "press": ("modernfoundry:cobalt_ingot", "electroenergetics:high_voltage_capacitor"),
    "deployer": ("create:brass_hand", "megacells:accumulation_processor"),
    "mixer": ("create:whisk", "modernfoundry:cobalt_ingot"),
    "saw": ("create:sturdy_sheet", "allthemodium:vibranium_plate"),
    "fan": ("create:propeller", "electroenergetics:high_voltage_capacitor"),
    "roller": ("create:crushing_wheel", "modernfoundry:cobalt_ingot"),
    "depot": ("create:content_observer", "mekanism:energy_tablet"),
    "gearbox": ("create:large_cogwheel", "tfmg:magnetic_alloy_sheet"),
    "clutch": ("create:redstone_link", "megacells:accumulation_processor"),
    "chain_conveyor": ("create:metal_bracket", "tfmg:electric_motor"),
    "automatic_clutch": ("create:redstone_link", "megacells:accumulation_processor"),
    "configurable_gearbox": ("create:precision_mechanism", "megacells:accumulation_processor"),
    "drill": ("create:sturdy_sheet", "modernfoundry:cobalt_ingot"),
    "harvester": ("create:iron_sheet", "tfmg:electric_motor"),
    "plough": ("create:sturdy_sheet", "modernfoundry:cobalt_ingot"),
    "portable_storage_interface": ("create:content_observer", "mekanism:energy_tablet"),
    "gearshift": ("create:redstone_link", "megacells:accumulation_processor"),
    "chain_drive": ("create:large_cogwheel", "tfmg:electric_motor"),
    "adjustable_chain_drive": ("create:analog_lever", "megacells:accumulation_processor"),
    "slicer": ("create:sturdy_sheet", "modernfoundry:cobalt_ingot"),
}


def _item_id(value: Any) -> str | None:
    if isinstance(value, dict):
        item_id = value.get("id")
        return item_id if isinstance(item_id, str) else None
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(1) if match else None


def _output(tier: str, role: str) -> str:
    return f"createcasing:{tier}_{_OUTPUT_SUFFIX[role]}"


def _expected_outputs() -> set[str]:
    return {
        _output(tier, role)
        for tier, roles in _TIER_ROLES.items()
        for role in roles
    }


def _family_rows(data: dict[str, Any]) -> Iterable[Recipe]:
    """Mirror the pre-normalization family identities without expanding cards."""

    for family in data.get("machine_families", []):
        tier = family.get("tier")
        if tier not in _TARGET_TIERS:
            continue
        rows: dict[str, Recipe] = {}
        for role in family.get("kinds", []):
            rows[role] = {
                "kind": role,
                "id": f"industrial_colonies:manufacturing/{tier}/{role}",
                "output": _output(tier, role),
                "remove": [
                    f"createcasing:crafting/{_STOCK_KIND.get(role, role)}/{tier}"
                ],
            }
        for entry in family.get("recipes", []):
            if not isinstance(entry, dict) or not isinstance(entry.get("kind"), str):
                continue
            role = entry["kind"]
            rows[role] = {
                "kind": role,
                "id": entry.get(
                    "id", f"industrial_colonies:manufacturing/{tier}/{role}"
                ),
                "output": _item_id(entry.get("output")) or _output(tier, role),
                "remove": list(
                    entry.get(
                        "remove",
                        [
                            f"createcasing:crafting/"
                            f"{_STOCK_KIND.get(role, role)}/{tier}"
                        ],
                    )
                ),
            }
        yield from rows.values()


def _collect_records(data: dict[str, Any]) -> dict[str, Recipe]:
    records: dict[str, Recipe] = {}
    for recipe in data.get("recipes", []):
        output = _item_id(recipe.get("output"))
        if output not in _expected_outputs():
            continue
        if output in records:
            raise ValueError(f"Create Encased output is managed twice: {output}")
        records[output] = {
            "id": recipe["id"],
            "output": output,
            "remove": list(recipe.get("remove", [])),
        }
    for row in _family_rows(data):
        output = row["output"]
        if output in records:
            raise ValueError(
                f"Create Encased family duplicates explicit managed output: {output}"
            )
        records[output] = row
    missing = sorted(_expected_outputs().difference(records))
    extra = sorted(set(records).difference(_expected_outputs()))
    if missing or extra:
        raise ValueError(
            "Create Encased v3 coverage is incomplete: "
            f"missing={missing}, extra={extra}"
        )
    return records


def _all_managed_createcasing_outputs(data: dict[str, Any]) -> set[str]:
    outputs = {
        output
        for recipe in data.get("recipes", [])
        if (output := _item_id(recipe.get("output")))
        and output.startswith("createcasing:")
    }
    outputs.update(row["output"] for row in _family_rows(data))
    return outputs


def _source_for(tier: str, role: str) -> str:
    if tier == "copper":
        return _NATIVE_SOURCE[role]
    prior = {
        "brass": "copper",
        "railway": "brass",
        "weathered_iron": "railway",
        "industrial_iron": "weathered_iron",
        "refined_radiance": "industrial_iron",
    }[tier]
    if tier == "industrial_iron" and role == "portable_storage_interface":
        # Weathered Iron intentionally has no managed portable-interface card.
        prior = "railway"
    return _output(prior, role)


def _deploy(ingredient: str, machine: str) -> Recipe:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> Recipe:
    return {"op": "pressing", "machine": machine}


def _base_recipe(
    record: Recipe,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
) -> Recipe:
    return {
        "id": record["id"],
        "phase": phase,
        "node": node,
        "order": order,
        "comment": comment,
        "output": record["output"],
        "remove": list(record.get("remove", [])),
        "exclusive_output": True,
    }


def _sequence_recipe(
    record: Recipe,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    source: str,
    ingredients: Iterable[str],
    deployer: str,
    press: str,
) -> Recipe:
    recipe = _base_recipe(
        record,
        phase=phase,
        node=node,
        order=order,
        comment=comment,
    )
    loads = tuple(ingredients)
    if len(loads) != len(set(loads)):
        raise ValueError(f"{record['id']} repeats an assembly load: {loads}")
    recipe.update(
        {
            "type": "sequenced_assembly",
            "input": source,
            "transitional": source,
            "loops": 1,
            "steps": [_deploy(item, deployer) for item in loads]
            + [_press(press)],
        }
    )
    return recipe


def _shaped_reference(
    record: Recipe,
    *,
    phase: str,
    node: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
) -> Recipe:
    recipe = _base_recipe(
        record,
        phase=phase,
        node=node,
        order=order,
        comment=comment,
    )
    recipe.update({"type": "shaped", "pattern": pattern, "key": key})
    return recipe


def _copper_recipe(role: str, record: Recipe, index: int) -> Recipe:
    if role == "press":
        return _shaped_reference(
            record,
            phase="Electrical Manufacturing",
            node="CR01 — Electronics Manufacturing",
            order=5,
            comment=(
                "Rebuild the native Mechanical Press with a Copper ram, "
                "conductive casing, geared base and through-shaft."
            ),
            pattern=["CSC", "AMA", "GKG"],
            key={
                "C": "create:copper_sheet",
                "S": "create:shaft",
                "A": "create:andesite_alloy",
                "M": "create:mechanical_press",
                "G": "create:cogwheel",
                "K": "create:copper_casing",
            },
        )
    if role == "deployer":
        return _shaped_reference(
            record,
            phase="Electrical Manufacturing",
            node="CR01 — Electronics Manufacturing",
            order=6,
            comment=(
                "Rebuild the native Deployer with a Copper service shell, "
                "electron-tube control, reinforced drive and conductive base."
            ),
            pattern=["CEC", "ADA", "SKS"],
            key={
                "C": "create:copper_sheet",
                "E": "create:electron_tube",
                "A": "create:andesite_alloy",
                "D": "create:deployer",
                "S": "create:shaft",
                "K": "create:copper_casing",
            },
        )
    ingredients = (
        "create:copper_casing",
        "create:copper_sheet",
        "tfmg:copper_wire",
        *_COPPER_PARTS[role],
    )
    return _sequence_recipe(
        record,
        phase="Electrical Manufacturing",
        node="CR01 — Electronics Manufacturing",
        order=10 + index,
        comment=(
            f"Rehouse the native {role.replace('_', ' ')} as a conductive "
            "Copper production tool with a distinct working assembly."
        ),
        source=_source_for("copper", role),
        ingredients=ingredients,
        deployer="create:deployer",
        press="create:mechanical_press",
    )


def _brass_recipe(role: str, record: Recipe, index: int) -> Recipe:
    if role == "press":
        # Exact live KubeJSGen authority supplied by the user.
        return _shaped_reference(
            record,
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=10,
            comment=(
                "Upgrade the Copper Press into the precision Brass Press with "
                "paired capacitor banks, tube control and insulated casing."
            ),
            pattern=["CPC", "EBE", "LSL"],
            key={
                "C": "tfmg:capacitor_item",
                "P": "create:precision_mechanism",
                "E": "create:electron_tube",
                "B": "createcasing:copper_press",
                "L": "tfmg:plastic_sheet",
                "S": "create:brass_casing",
            },
        )
    if role == "deployer":
        # Preserve the user's companion Brass Deployer card as well.
        return _shaped_reference(
            record,
            phase="Digital Logistics",
            node="CR01 — Advanced Circuitry",
            order=11,
            comment=(
                "Upgrade the Copper Deployer with paired precision drives, a "
                "blank controller board, plastic isolation and transistor stages."
            ),
            pattern=["PEP", "LBL", "TST"],
            key={
                "P": "create:precision_mechanism",
                "E": "tfmg:empty_circuit_board",
                "L": "tfmg:plastic_sheet",
                "B": "createcasing:copper_deployer",
                "T": "tfmg:transistor_item",
                "S": "create:brass_casing",
            },
        )
    ingredients = (
        "create:brass_casing",
        "create:precision_mechanism",
        "tfmg:plastic_sheet",
        "tfmg:circuit_board",
        *_BRASS_PARTS[role],
    )
    return _sequence_recipe(
        record,
        phase="Digital Logistics",
        node="CR01 — Advanced Circuitry",
        order=20 + index,
        comment=(
            f"Convert the Copper {role.replace('_', ' ')} into a populated "
            "Brass precision tool with serviceable drive and role-specific control."
        ),
        source=_source_for("brass", role),
        ingredients=ingredients,
        deployer="createcasing:copper_deployer",
        press="createcasing:copper_press",
    )


def _railway_recipe(role: str, record: Recipe, index: int) -> Recipe:
    # Railway is the late-Digital fabrication bridge: steel and petroleum
    # materials already exist, while the completed Brass electronics line is
    # now available to instrument the heavy frame before Mekanized Industry.
    phase = "Digital Logistics"
    node = "CR01 — Early Digital Crafting"
    order = 300 + index
    pattern = list(_RAILWAY_PATTERNS[role])
    electrical, working = _RAILWAY_PARTS[role]
    all_keys = {
        "H": "tfmg:heavy_plate",
        "M": "tfmg:steel_mechanism",
        "C": "create:railway_casing",
        "B": _source_for("railway", role),
        "S": "tfmg:steel_casing",
        "P": "tfmg:plastic_sheet",
        "E": electrical,
        "R": working,
    }
    used = set("".join(pattern)) - {" "}
    recipe = _base_recipe(
        record,
        phase=phase,
        node=node,
        order=order,
        comment=(
            f"Fabricate a full Railway {role.replace('_', ' ')} in a readable "
            "4x4 steel frame around its completed Brass machine core."
        ),
    )
    recipe.update(
        {
            "type": "mechanical_crafting",
            "pattern": pattern,
            "key": {symbol: all_keys[symbol] for symbol in used},
        }
    )
    if role == "saw":
        recipe["id"] = _RAILWAY_SAW_REPROPOSAL_ID
    return recipe


def _late_sequence_recipe(
    tier: str,
    role: str,
    record: Recipe,
    index: int,
) -> Recipe:
    if tier == "weathered_iron":
        phase = "Mekanized Industry"
        node = "CR01 — Modular Machinery"
        order = 200 + index
        common = _WEATHERED_COMMON
        parts = _WEATHERED_PARTS[role]
        deployer = "createcasing:railway_deployer"
        press = "createcasing:railway_press"
        tier_label = "Weathered Iron"
        description = "electrically controlled machine-building"
    elif tier == "industrial_iron":
        phase = "High-Energy Grid"
        node = "CR01 — Precision Engineering"
        order = 200 + index
        common = _INDUSTRIAL_COMMON
        parts = _INDUSTRIAL_PARTS[role]
        deployer = "createcasing:weathered_iron_deployer"
        press = "createcasing:weathered_iron_press"
        tier_label = "Industrial Iron"
        description = "late industrial machine construction"
    elif tier == "refined_radiance":
        phase = "Nuclear Engineering"
        node = "CR01 — Core Engineering"
        order = 200 + index
        common = _RADIANCE_COMMON
        parts = _RADIANCE_PARTS[role]
        deployer = "createcasing:industrial_iron_deployer"
        press = "createcasing:industrial_iron_press"
        tier_label = "Refined Radiance"
        description = "reactor and final-tier component manufacturing"
    else:
        raise ValueError(f"unsupported late Create Encased tier: {tier}")

    return _sequence_recipe(
        record,
        phase=phase,
        node=node,
        order=order,
        comment=(
            f"Rebuild the prior {role.replace('_', ' ')} as the {tier_label} "
            f"{description} platform, loading each subsystem separately before sealing."
        ),
        source=_source_for(tier, role),
        ingredients=(*common, *parts),
        deployer=deployer,
        press=press,
    )


def _replacement(tier: str, role: str, record: Recipe, index: int) -> Recipe:
    if tier == "copper":
        return _copper_recipe(role, record, index)
    if tier == "brass":
        return _brass_recipe(role, record, index)
    if tier == "railway":
        return _railway_recipe(role, record, index)
    return _late_sequence_recipe(tier, role, record, index)


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    matches = [
        index
        for index, existing in enumerate(data["recipes"])
        if existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"managed recipe ID is duplicated: {recipe['id']}")
    if matches:
        data["recipes"][matches[0]] = recipe
    else:
        data["recipes"].append(recipe)


def _validate_recipe(recipe: Recipe, tier: str, role: str) -> None:
    if recipe["type"] == "compacting":
        raise ValueError(f"Create Encased machine cannot be compacted: {recipe['id']}")
    if recipe["type"] in {"shaped", "mechanical_crafting"}:
        pattern = recipe["pattern"]
        width = len(pattern[0])
        if not pattern or any(len(row) != width for row in pattern):
            raise ValueError(f"non-rectangular Create Encased grid: {recipe['id']}")
        used = set("".join(pattern)) - {" "}
        if used != set(recipe["key"]):
            raise ValueError(
                f"Create Encased grid key mismatch: {recipe['id']} "
                f"used={sorted(used)} key={sorted(recipe['key'])}"
            )
    if tier == "railway":
        if recipe["type"] == "mechanical_crafting":
            pattern = recipe["pattern"]
            if len(pattern) < 4 or max(map(len, pattern)) < 4:
                raise ValueError(f"Railway recipe is smaller than 4x4: {recipe['id']}")
        elif len(recipe.get("steps", [])) < 9:
            raise ValueError(f"Railway sequence has fewer than nine steps: {recipe['id']}")
    expected_steps = {
        "weathered_iron": 9,
        "industrial_iron": 10,
        "refined_radiance": 11,
    }
    if tier in expected_steps and len(recipe.get("steps", [])) != expected_steps[tier]:
        raise ValueError(
            f"{tier} assembly depth drift for {recipe['id']}: "
            f"expected {expected_steps[tier]}, got {len(recipe.get('steps', []))}"
        )
    if role not in {"press", "deployer"} and tier in {"copper", "brass"}:
        if recipe["type"] != "sequenced_assembly":
            raise ValueError(f"{tier} machine is not assembled in sequence: {recipe['id']}")

    expected_source = _source_for(tier, role)
    if recipe["type"] == "sequenced_assembly":
        actual_source = recipe.get("input")
    else:
        actual_source = next(
            (
                item
                for item in recipe.get("key", {}).values()
                if item == expected_source
            ),
            None,
        )
    if actual_source != expected_source:
        raise ValueError(
            f"{recipe['id']} does not retain its prior-tier machine core: "
            f"expected {expected_source}, got {actual_source}"
        )


def _validate_result(data: dict[str, Any]) -> None:
    target = _expected_outputs()
    by_output: dict[str, list[Recipe]] = {output: [] for output in target}
    for recipe in data.get("recipes", []):
        output = _item_id(recipe.get("output"))
        if output in by_output:
            by_output[output].append(recipe)
    duplicated = sorted(output for output, rows in by_output.items() if len(rows) != 1)
    if duplicated:
        raise ValueError(f"Create Encased v3 output ownership drift: {duplicated}")
    if any(family.get("tier") in _TARGET_TIERS for family in data.get("machine_families", [])):
        raise ValueError("Create Encased template families survived explicit v3 expansion")

    brass_press = by_output["createcasing:brass_press"][0]
    if brass_press.get("pattern") != ["CPC", "EBE", "LSL"] or brass_press.get("key") != {
        "C": "tfmg:capacitor_item",
        "P": "create:precision_mechanism",
        "E": "create:electron_tube",
        "B": "createcasing:copper_press",
        "L": "tfmg:plastic_sheet",
        "S": "create:brass_casing",
    }:
        raise ValueError("the user-authored Brass Press reference was not preserved")


def validation_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Return a compact, deterministic summary for the parent audit/report."""

    recipes = [
        recipe
        for recipe in data.get("recipes", [])
        if _item_id(recipe.get("output")) in _expected_outputs()
    ]
    counts: dict[str, int] = {}
    for recipe in recipes:
        counts[recipe["type"]] = counts.get(recipe["type"], 0) + 1
    return {
        "managed_tier_outputs": len(recipes),
        "tier_counts": {
            tier: len(roles) for tier, roles in _TIER_ROLES.items()
        },
        "recipe_type_counts": dict(sorted(counts.items())),
        "preserved_foundation_outputs": len(_FOUNDATION_OUTPUTS),
        "brass_press_reference": "CPC/EBE/LSL",
        "phase_strategy": {
            "copper": "Electrical Manufacturing (bootstrap orders 5-6)",
            "brass": "Digital Logistics",
            "railway": "late Digital Logistics (orders 300+)",
            "weathered_iron": "Mekanized Industry",
            "industrial_iron": "High-Energy Grid",
            "refined_radiance": "Nuclear Engineering",
        },
        "late_sequence_steps": {
            "weathered_iron": 9,
            "industrial_iron": 10,
            "refined_radiance": 11,
        },
        "negative_audit": NEGATIVE_AUDIT,
    }


def migration_report(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map every owned machine ID to its explicit v3 phase/order/process."""

    report: dict[str, dict[str, Any]] = {}
    for recipe in data.get("recipes", []):
        output = _item_id(recipe.get("output"))
        if output not in _expected_outputs():
            continue
        report[output] = {
            "recipe_id": recipe["id"],
            "phase": recipe["phase"],
            "order": recipe["order"],
            "type": recipe["type"],
        }
    missing = _expected_outputs().difference(report)
    if missing:
        raise ValueError(
            f"cannot report missing Create Encased v3 outputs: {sorted(missing)}"
        )
    return {output: report[output] for output in sorted(report)}


def apply(data: dict[str, Any]) -> None:
    """Replace the six managed Create Encased template families explicitly."""

    records = _collect_records(data)
    managed_before = _all_managed_createcasing_outputs(data)
    expected_scope = _expected_outputs() | _FOUNDATION_OUTPUTS
    if managed_before != expected_scope:
        raise ValueError(
            "Create Encased managed-output audit changed: "
            f"missing={sorted(expected_scope - managed_before)}, "
            f"unreviewed={sorted(managed_before - expected_scope)}"
        )

    data["machine_families"] = [
        family
        for family in data.get("machine_families", [])
        if family.get("tier") not in _TARGET_TIERS
    ]

    identity_rewrites: dict[str, str] = {}
    for tier, roles in _TIER_ROLES.items():
        for index, role in enumerate(roles):
            output = _output(tier, role)
            recipe = _replacement(tier, role, records[output], index)
            _validate_recipe(recipe, tier, role)
            old_identity = str(records[output]["id"])
            new_identity = str(recipe["id"])
            if old_identity != new_identity:
                data["recipes"] = [
                    existing
                    for existing in data["recipes"]
                    if existing.get("id") != old_identity
                ]
                identity_rewrites[old_identity] = new_identity
            _upsert(data, recipe)

    if identity_rewrites:
        for recipe in data["recipes"]:
            dependencies = recipe.get("depends_on")
            if not isinstance(dependencies, list):
                continue
            recipe["depends_on"] = [
                identity_rewrites.get(str(dependency), dependency)
                for dependency in dependencies
            ]

    _validate_result(data)
