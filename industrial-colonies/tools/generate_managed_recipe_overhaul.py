#!/usr/bin/env python3
"""Compile the Industrial Colonies recipe-design manifest into KJSGen cards.

The compact design manifest is the maintainable source of truth.  The emitted
``pack-kjsgen/default.managed.json`` file is intentionally native KJSGen data so
every managed recipe remains visible and editable in the in-game project UI.
Stable UUIDs allow the three-way deploy merge to preserve player edits.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import uuid
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression/managed_recipe_overhaul.json"
DEFAULT_OUTPUT = PROJECT / "pack-kjsgen/default.managed.json"
UUID_NAMESPACE = uuid.UUID("5a2b9d0f-09e5-52dc-a588-c29e9846e72a")
COUNTED = re.compile(r"^(\d+)x\s+([a-z0-9_.-]+:[a-z0-9_./-]+)$")
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TAG_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
VALID_SLOT_KINDS = {
    "ITEM",
    "ITEM_TAG",
    "FLUID",
    "FLUID_TAG",
    "CHEMICAL",
    "CHEMICAL_TAG",
}
CREATE_MACHINE_FAMILIES = {
    "pressing",
    "compacting",
    "mixing",
    "cutting",
    "deploying",
    "filling",
    "emptying",
    "splashing",
    "haunting",
}
MEKANISM_LAYOUTS: dict[str, tuple[tuple[str, str], ...]] = {
    "mekanism_chemical_infusing": (("left", "CHEMICAL"), ("right", "CHEMICAL"), ("output", "CHEMICAL")),
    "mekanism_combining": (("input1", "ITEM"), ("input2", "ITEM"), ("output", "ITEM")),
    "mekanism_compressing": (("input", "ITEM"), ("gas", "CHEMICAL"), ("output", "ITEM")),
    "mekanism_crushing": (("input", "ITEM"), ("output", "ITEM")),
    "mekanism_crystallizing": (("input", "CHEMICAL"), ("output", "ITEM")),
    "mekanism_dissolution": (("input", "ITEM"), ("gas", "CHEMICAL"), ("output", "CHEMICAL")),
    "mekanism_energy_conversion": (("input", "ITEM"),),
    "mekanism_enriching": (("input", "ITEM"), ("output", "ITEM")),
    "mekanism_injecting": (("input", "ITEM"), ("gas", "CHEMICAL"), ("output", "ITEM")),
    "mekanism_metallurgic_infusing": (("input", "ITEM"), ("infusion", "CHEMICAL"), ("output", "ITEM")),
    "mekanism_oxidizing": (("input", "ITEM"), ("output", "CHEMICAL")),
    "mekanism_purifying": (("input", "ITEM"), ("gas", "CHEMICAL"), ("output", "ITEM")),
    "mekanism_sawing": (("input", "ITEM"), ("output", "ITEM")),
    "mekanism_smelting": (("input", "ITEM"), ("output", "ITEM")),
}
MOD_ID = re.compile(r"^[a-z0-9_.-]+$")
HEAT_VALUES = {"none", "heated", "superheated"}
TFMG_VAT_MODES = {"steel", "firebrick", "both"}
TFMG_VAT_MACHINE_MODES = {"mixing", "two_electrodes"}
TFMG_VAT_CARD_TYPE = "industrial_colonies:tfmg_chemical_vat"
TFMG_VAT_MAX_SLOTS = 4


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8-sig") as handle:
        data = json.load(handle, object_pairs_hook=OrderedDict)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def aliased_field(spec: dict[str, Any], canonical: str, alias: str) -> Any:
    """Read one strict manifest alias without silently choosing conflicting data."""

    has_canonical = canonical in spec
    has_alias = alias in spec
    if has_canonical and has_alias and spec[canonical] != spec[alias]:
        raise ValueError(
            f"{spec.get('id', '<unknown>')} defines conflicting {canonical}/{alias} values"
        )
    if has_canonical:
        return spec[canonical]
    return spec.get(alias)


def stable_uid(kind: str, identity: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, f"{kind}:{identity}"))


def existing_uids(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    if not path.is_file():
        return {}, {}
    data = load_json(path)
    recipes = {
        str(entry.get("recipeId")): str(entry.get("uid"))
        for entry in data.get("recipes", [])
        if entry.get("recipeId") and entry.get("uid")
    }
    removals = {
        str(entry.get("recipeId")): str(entry.get("uid"))
        for entry in data.get("removals", [])
        if entry.get("recipeId") and entry.get("uid")
    }
    return recipes, removals


def valid_components_syntax(value: str) -> bool:
    if not value.startswith("[") or not value.endswith("]") or "=" not in value:
        return False
    stack: list[str] = []
    quote = ""
    escaped = False
    pairs = {"]": "[", "}": "{", ")": "("}
    for character in value:
        if character in "\r\n\x00":
            return False
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
        elif character in "\"'":
            quote = character
        elif character in "[{(":
            stack.append(character)
        elif character in "]})":
            if not stack or stack.pop() != pairs[character]:
                return False
    return not quote and not escaped and not stack


def slot(value: Any, *, output: bool = False) -> dict[str, Any]:
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("#"):
            identifier = value[1:]
            if output:
                raise ValueError(f"outputs cannot be tags: {value!r}")
            if not TAG_ID.fullmatch(identifier):
                raise ValueError(f"invalid item tag ID: {value!r}")
            return OrderedDict((("kind", "ITEM_TAG"), ("id", identifier)))
        counted = COUNTED.fullmatch(value)
        if counted:
            result: dict[str, Any] = OrderedDict(
                (("kind", "ITEM"), ("id", counted.group(2)), ("count", int(counted.group(1))))
            )
            return result
        if not RESOURCE_ID.fullmatch(value):
            raise ValueError(f"invalid item ID: {value!r}")
        return OrderedDict((("kind", "ITEM"), ("id", value)))
    if not isinstance(value, dict):
        raise ValueError(f"slot value must be a string or object, got {value!r}")
    identifier = str(value.get("id", "")).strip()
    if not identifier:
        raise ValueError(f"slot object is missing id: {value!r}")
    kind = str(value.get("kind", "ITEM")).upper()
    if identifier.startswith("#") and kind == "ITEM":
        identifier = identifier[1:]
        kind = "ITEM_TAG"
    if kind not in VALID_SLOT_KINDS:
        raise ValueError(f"unsupported slot kind {kind!r}: {value!r}")
    if not RESOURCE_ID.fullmatch(identifier):
        raise ValueError(f"invalid resource ID {identifier!r}: {value!r}")
    result = OrderedDict((("kind", kind), ("id", identifier)))
    for key in ("amount", "count", "chance"):
        if key in value:
            number = value[key]
            if key in {"amount", "count"} and (not isinstance(number, int) or number <= 0):
                raise ValueError(f"{key} must be a positive integer: {value!r}")
            if key == "chance" and (not isinstance(number, (int, float)) or not 0 < number <= 1):
                raise ValueError(f"chance must be in (0, 1]: {value!r}")
            result[key] = number
    if "components" in value:
        components = value["components"]
        if kind != "ITEM":
            raise ValueError(f"components are only supported on ITEM slots: {value!r}")
        if not isinstance(components, str) or not components.strip():
            raise ValueError(f"components must be a nonblank string: {value!r}")
        components = components.strip()
        if not valid_components_syntax(components):
            raise ValueError(f"components use unsafe item-component syntax: {value!r}")
        result["components"] = components
    if output and kind in {"ITEM_TAG", "FLUID_TAG", "CHEMICAL_TAG"}:
        raise ValueError(f"outputs cannot be tags: {value!r}")
    return result


def recipe_shell(spec: dict[str, Any], uid: str, recipe_type: str) -> OrderedDict[str, Any]:
    phase = str(spec.get("phase", "")).strip()
    comment = str(spec.get("comment", "")).strip()
    if not phase or not comment:
        raise ValueError(f"{spec.get('id', '<unknown>')} must define nonblank phase and comment")
    result: OrderedDict[str, Any] = OrderedDict()
    result["uid"] = uid
    result["type"] = recipe_type
    result["recipeId"] = spec["id"]
    result["comment"] = f"[{phase}] {comment}"
    if spec.get("if_mod_loaded"):
        mod_id = str(spec["if_mod_loaded"]).strip()
        if not MOD_ID.fullmatch(mod_id):
            raise ValueError(f"{spec['id']} has invalid if_mod_loaded value {mod_id!r}")
        result["ifModLoaded"] = mod_id
    result["replaceRecipe"] = False
    return result


def shaped(spec: dict[str, Any], uid: str, mechanical: bool) -> OrderedDict[str, Any]:
    pattern = spec["pattern"]
    if not isinstance(pattern, list) or not pattern:
        raise ValueError(f"{spec['id']} has no pattern")
    width = len(pattern[0])
    if width < 1 or any(len(row) != width for row in pattern):
        raise ValueError(f"{spec['id']} pattern is ragged")
    limit = 9 if mechanical else 3
    if len(pattern) > limit or width > limit:
        raise ValueError(f"{spec['id']} pattern exceeds {limit}x{limit}")
    if not mechanical and (len(pattern) != 3 or width != 3):
        raise ValueError(f"{spec['id']} shaped recipes must be explicitly padded to 3x3")

    keys = spec["key"]
    used = {character for row in pattern for character in row if character != " "}
    missing = sorted(used - set(keys))
    unused = sorted(set(keys) - used)
    if missing or unused:
        raise ValueError(f"{spec['id']} key mismatch; missing={missing}, unused={unused}")

    result = recipe_shell(
        spec, uid, "kjsgen:create_mechanical_crafting" if mechanical else "kjsgen:shaped"
    )
    slots: OrderedDict[str, Any] = OrderedDict()
    if mechanical:
        for row, text in enumerate(pattern):
            for column, character in enumerate(text):
                if character != " ":
                    slots[f"cell_{row}_{column}"] = slot(keys[character])
    else:
        for row, text in enumerate(pattern):
            for column, character in enumerate(text):
                if character != " ":
                    slots[f"in{row * 3 + column}"] = slot(keys[character])
    slots["output"] = slot(spec["output"], output=True)
    result["slots"] = slots
    result["params"] = (
        OrderedDict((("gridW", str(width)), ("gridH", str(len(pattern)))))
        if mechanical
        else OrderedDict()
    )
    return result


def shapeless(spec: dict[str, Any], uid: str) -> OrderedDict[str, Any]:
    inputs = require_list(spec.get("inputs"), f"{spec['id']} inputs")
    if not inputs or len(inputs) > 9:
        raise ValueError(f"{spec['id']} shapeless recipes require 1-9 inputs")
    result = recipe_shell(spec, uid, "kjsgen:shapeless")
    slots: OrderedDict[str, Any] = OrderedDict()
    for index, value in enumerate(inputs):
        slots[f"in{index}"] = slot(value)
    slots["output"] = slot(spec["output"], output=True)
    result["slots"] = slots
    result["params"] = OrderedDict()
    return result


def process(spec: dict[str, Any], uid: str) -> OrderedDict[str, Any]:
    family = spec["type"]
    result = recipe_shell(spec, uid, f"kjsgen:create_{family}")
    slots: OrderedDict[str, Any] = OrderedDict()
    machine = spec.get("machine")
    if family in CREATE_MACHINE_FAMILIES and not machine:
        raise ValueError(f"{spec['id']} must explicitly select its exact {family} machine")
    if machine:
        slots[f"__machine_process_{family}"] = slot(machine)

    if family in {"mixing", "compacting"}:
        for index, value in enumerate(require_list(spec.get("inputs"), f"{spec['id']} inputs")):
            slots[f"in{index}"] = slot(value)
        outputs = spec.get("outputs", [spec.get("output")])
        outputs = require_list(outputs, f"{spec['id']} outputs")
        if not outputs or all(value is None for value in outputs):
            raise ValueError(f"{spec['id']} must contain at least one output")
        if len([value for value in outputs if value is not None]) != 1:
            raise ValueError(
                f"{spec['id']} {family} must use the one visual output slot exposed by KJSGen"
            )
        for index, value in enumerate(outputs):
            if value is None:
                continue
            key = "output" if index == 0 else f"output{index + 1}"
            slots[key] = slot(value, output=True)
        if spec.get("returned_tool"):
            slots["returned_tool"] = slot(spec["returned_tool"], output=True)
    elif family == "deploying":
        slots["input"] = slot(spec["input"])
        slots["held"] = slot(spec["held"])
        slots["output"] = slot(spec["output"], output=True)
    elif family in {
        "pressing",
        "cutting",
        "crushing",
        "milling",
        "splashing",
        "haunting",
        "sandpaper_polishing",
    }:
        slots["input"] = slot(spec["input"])
        outputs = spec.get("outputs")
        if outputs is None:
            output_key = (
                "output0"
                if family in {"cutting", "crushing", "milling", "splashing", "haunting"}
                else "output"
            )
            slots[output_key] = slot(spec["output"], output=True)
        else:
            outputs = require_list(outputs, f"{spec['id']} outputs")
            if not outputs:
                raise ValueError(f"{spec['id']} must contain at least one output")
            if family == "pressing":
                if len(outputs) > 2:
                    raise ValueError(f"{spec['id']} pressing supports at most two visual outputs")
                for index, value in enumerate(outputs):
                    slots["output" if index == 0 else "output2"] = slot(value, output=True)
            elif family == "sandpaper_polishing":
                if len(outputs) != 1:
                    raise ValueError(f"{spec['id']} polishing supports exactly one visual output")
                slots["output"] = slot(outputs[0], output=True)
            else:
                for index, value in enumerate(outputs):
                    slots[f"output{index}"] = slot(value, output=True)
    elif family == "filling":
        slots["base"] = slot(spec["input"])
        fluid = slot(spec["fluid"])
        if fluid["kind"] not in {"FLUID", "FLUID_TAG"}:
            raise ValueError(f"{spec['id']} filling fluid must use FLUID or FLUID_TAG")
        slots["fluid"] = fluid
        slots["output"] = slot(spec["output"], output=True)
    elif family == "emptying":
        slots["input"] = slot(spec["input"])
        slots["outItem"] = slot(spec["out_item"], output=True)
        fluid = slot(spec["out_fluid"], output=True)
        if fluid["kind"] != "FLUID":
            raise ValueError(f"{spec['id']} emptying output must use FLUID")
        slots["outFluid"] = fluid
    else:
        raise ValueError(f"unsupported process family in {spec['id']}: {family}")

    params: OrderedDict[str, str] = OrderedDict()
    if family in {"mixing", "compacting"}:
        heat = str(spec.get("heat", "none"))
        if heat not in HEAT_VALUES:
            raise ValueError(f"{spec['id']} has invalid heat requirement {heat!r}")
        params["heat"] = heat
    if family in {"cutting", "crushing", "milling"}:
        processing_time = spec.get(
            "processing_time", {"cutting": 50, "crushing": 250, "milling": 200}[family]
        )
        if not isinstance(processing_time, int) or processing_time <= 0:
            raise ValueError(f"{spec['id']} processing_time must be a positive integer")
        params["processingTime"] = str(processing_time)
    if family == "deploying":
        params["keepHeldItem"] = str(bool(spec.get("keep_held", False))).lower()
    result["slots"] = slots
    result["params"] = params
    return result


def sequenced(spec: dict[str, Any], uid: str) -> OrderedDict[str, Any]:
    result = recipe_shell(spec, uid, "kjsgen:create_sequenced_assembly")
    slots: OrderedDict[str, Any] = OrderedDict()
    slots["input"] = slot(spec["input"])
    slots["transitional"] = slot(spec["transitional"])
    outputs = require_list(
        spec.get("outputs", [spec.get("output")]), f"{spec['id']} outputs"
    )
    if not outputs or any(value is None for value in outputs):
        raise ValueError(f"{spec['id']} must contain at least one nonblank output")
    for index, value in enumerate(outputs):
        slots[f"output{index}"] = slot(value, output=True)

    params: OrderedDict[str, str] = OrderedDict()
    loops = spec.get("loops", 1)
    if not isinstance(loops, int) or isinstance(loops, bool) or loops <= 0:
        raise ValueError(f"{spec['id']} loops must be a positive integer")
    params["loops"] = str(loops)
    steps = require_list(spec["steps"], f"{spec['id']} steps")
    if not steps:
        raise ValueError(f"{spec['id']} must contain at least one sequence step")
    params["__seqLen"] = str(len(steps))
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValueError(f"{spec['id']} sequence step {index} must be an object")
        operation = step["op"]
        params[f"seq{index}"] = operation
        if operation == "deploying":
            slots[f"seqItem{index}"] = slot(step["ingredient"])
        elif operation == "filling":
            fluid = slot(step["fluid"])
            if fluid["kind"] not in {"FLUID", "FLUID_TAG"}:
                raise ValueError(f"{spec['id']} sequence step {index} requires a fluid slot")
            # KJSGen's native CreateSpecialModel uses seqItemN for fluid steps too.
            slots[f"seqItem{index}"] = fluid
        elif operation not in {"pressing", "cutting"}:
            raise ValueError(f"{spec['id']} has unsupported sequence operation {operation}")
        if operation in {"pressing", "deploying", "cutting", "filling"}:
            if not step.get("machine"):
                raise ValueError(
                    f"{spec['id']} sequence step {index} must explicitly select its {operation} machine"
                )
            slots[f"__machine_step_{index}_{operation}"] = slot(step["machine"])

    result["slots"] = slots
    result["params"] = params
    return result


def mekanism_process(spec: dict[str, Any], uid: str) -> OrderedDict[str, Any]:
    family = str(spec["type"])
    layout = MEKANISM_LAYOUTS[family]
    result = recipe_shell(spec, uid, f"kjsgen:{family}")
    slots: OrderedDict[str, Any] = OrderedDict()
    for key, expected_kind in layout:
        value = spec.get(key)
        if value is None:
            raise ValueError(f"{spec['id']} is missing Mekanism slot {key}")
        parsed = slot(value, output=key in {"output", "extraOutput"})
        allowed = {expected_kind, f"{expected_kind}_TAG"}
        if parsed["kind"] not in allowed or (key == "output" and parsed["kind"].endswith("_TAG")):
            raise ValueError(
                f"{spec['id']} slot {key} requires {expected_kind}, got {parsed['kind']}"
            )
        slots[key] = parsed
    params: OrderedDict[str, str] = OrderedDict()
    if family == "mekanism_metallurgic_infusing":
        params["perTickUsage"] = str(bool(spec.get("per_tick_usage", False))).lower()
    if family == "mekanism_sawing":
        extra = spec.get("extra_output")
        chance = spec.get("secondary_chance", 1.0)
        if extra is not None:
            if not isinstance(chance, (int, float)) or isinstance(chance, bool) or not 0 < chance <= 1:
                raise ValueError(f"{spec['id']} secondary_chance must be in (0, 1]")
            slots["extraOutput"] = slot(extra, output=True)
            params["secondaryChance"] = str(chance)
    if family == "mekanism_energy_conversion":
        energy = spec.get("energy", 10000)
        if not isinstance(energy, int) or isinstance(energy, bool) or energy <= 0:
            raise ValueError(f"{spec['id']} energy must be a positive integer")
        params["energy"] = str(energy)
    result["slots"] = slots
    result["params"] = params
    return result


def tfmg_vat(spec: dict[str, Any], uid: str) -> OrderedDict[str, Any]:
    """Compile a TFMG 1.2.0 Chemical Vat manifest recipe into its visual card."""

    ingredients = require_list(
        aliased_field(spec, "ingredients", "inputs"), f"{spec['id']} ingredients/inputs"
    )
    results = require_list(
        aliased_field(spec, "results", "outputs"), f"{spec['id']} results/outputs"
    )
    for label, values in (("ingredients", ingredients), ("results", results)):
        if not values or len(values) > TFMG_VAT_MAX_SLOTS:
            raise ValueError(
                f"{spec['id']} TFMG Vat requires 1-{TFMG_VAT_MAX_SLOTS} {label}"
            )

    card = recipe_shell(spec, uid, TFMG_VAT_CARD_TYPE)
    slots: OrderedDict[str, Any] = OrderedDict()
    expanded_item_ingredients = 0
    fluid_ingredients = 0
    for index, value in enumerate(ingredients):
        parsed = slot(value)
        if parsed["kind"] not in {"ITEM", "ITEM_TAG", "FLUID", "FLUID_TAG"}:
            raise ValueError(
                f"{spec['id']} TFMG Vat ingredient {index} must be item/tag/fluid"
            )
        if "components" in parsed or "chance" in parsed:
            raise ValueError(
                f"{spec['id']} TFMG Vat ingredient {index} cannot use components/chance"
            )
        if parsed["kind"].startswith("ITEM") and "amount" in parsed:
            raise ValueError(f"{spec['id']} TFMG Vat item ingredient cannot use amount")
        if parsed["kind"].startswith("FLUID") and "count" in parsed:
            raise ValueError(f"{spec['id']} TFMG Vat fluid ingredient cannot use count")
        if parsed["kind"] in {"ITEM", "ITEM_TAG"}:
            expanded_item_ingredients += int(parsed.get("count", 1))
        else:
            fluid_ingredients += 1
        slots[f"ingredients{index}"] = parsed
    if expanded_item_ingredients > TFMG_VAT_MAX_SLOTS or fluid_ingredients > TFMG_VAT_MAX_SLOTS:
        raise ValueError(
            f"{spec['id']} TFMG Vat supports at most four expanded item ingredients "
            "and four fluid ingredients"
        )

    item_results = 0
    fluid_results = 0
    for index, value in enumerate(results):
        parsed = slot(value, output=True)
        if parsed["kind"] not in {"ITEM", "FLUID"}:
            raise ValueError(
                f"{spec['id']} TFMG Vat result {index} must be a concrete item/fluid"
            )
        if "components" in parsed:
            raise ValueError(f"{spec['id']} TFMG Vat results cannot use components")
        if parsed["kind"] == "ITEM" and "amount" in parsed:
            raise ValueError(f"{spec['id']} TFMG Vat item result cannot use amount")
        if parsed["kind"] == "FLUID" and any(key in parsed for key in ("count", "chance")):
            raise ValueError(
                f"{spec['id']} TFMG Vat fluid result cannot use count/chance"
            )
        if parsed["kind"] == "ITEM":
            item_results += 1
        else:
            fluid_results += 1
        slots[f"results{index}"] = parsed
    if item_results > TFMG_VAT_MAX_SLOTS or fluid_results > TFMG_VAT_MAX_SLOTS:
        raise ValueError(
            f"{spec['id']} TFMG Vat supports at most four item results and four fluid results"
        )

    vat_mode = str(aliased_field(spec, "vat_mode", "vat") or "").strip()
    if vat_mode not in TFMG_VAT_MODES:
        raise ValueError(
            f"{spec['id']} vat_mode must be one of {sorted(TFMG_VAT_MODES)}, got {vat_mode!r}"
        )
    machine_mode = str(aliased_field(spec, "machine_mode", "machine") or "").strip()
    if machine_mode not in TFMG_VAT_MACHINE_MODES:
        raise ValueError(
            f"{spec['id']} machine_mode must be one of "
            f"{sorted(TFMG_VAT_MACHINE_MODES)}, got {machine_mode!r}"
        )
    heat = str(spec.get("heat", "none")).strip()
    if heat not in HEAT_VALUES:
        raise ValueError(f"{spec['id']} has invalid TFMG Vat heat requirement {heat!r}")
    min_size = spec.get("min_size", 0)
    if isinstance(min_size, bool) or not isinstance(min_size, int) or min_size < 0:
        raise ValueError(f"{spec['id']} min_size must be a non-negative integer")
    processing_time = spec.get("processing_time", 100)
    if (
        isinstance(processing_time, bool)
        or not isinstance(processing_time, int)
        or processing_time <= 0
    ):
        raise ValueError(f"{spec['id']} processing_time must be a positive integer")
    for forbidden in ("pressure", "heat_level"):
        if forbidden in spec:
            raise ValueError(
                f"{spec['id']} cannot use unsupported TFMG 1.2.0 field {forbidden!r}"
            )

    card["slots"] = slots
    card["params"] = OrderedDict(
        (
            ("vatMode", vat_mode),
            ("machineMode", machine_mode),
            ("heat", heat),
            ("minSize", str(min_size)),
            ("processingTime", str(processing_time)),
        )
    )
    return card


def expand_machine_family(group: dict[str, Any]) -> Iterable[dict[str, Any]]:
    tier = group["tier"]
    source_tier = group["source_tier"]
    phase = group["phase"]
    casing = group["casing"]
    plate = group["plate"]
    control = group["control"]
    drive = group["drive"]
    source_items = group["source_items"]
    recipes = require_list(group["recipes"], f"machine family {tier} recipes")
    # Each functional machine keeps one readable physical silhouette across its
    # casing upgrades.  The prior-tier machine remains the core (B), but saws,
    # fans, depots, gearboxes, and clutches no longer share one copy-pasted grid.
    family_patterns = {
        "press": [" P ", "LBL", "DRC"],
        "deployer": [" D ", "RBL", "CPC"],
        "mixer": ["DLD", "CBC", "PRP"],
        "saw": ["LRL", "CBC", "PDP"],
        "fan": ["PLP", "LBR", "CDC"],
        "roller": ["RLR", "PBP", "CDC"],
        "depot": ["PPP", "LBR", "CDC"],
        "gearbox": ["LDR", "CBC", "PBP"],
        "clutch": ["RDR", "LBC", "PCP"],
        "chain_conveyor": ["LBR", "CCC", "PDP"],
        "automatic_clutch": ["RLR", "CBD", "PCP"],
        "configurable_gearbox": ["DRD", "CBC", "LPR"],
    }
    for entry in recipes:
        kind = entry["kind"]
        source = entry.get("base") or source_items[kind]
        output = entry["output"]
        lower_name = entry.get("name", kind.replace("_", " ").title())
        specific = {
            "press": ("create:shaft", drive),
            "mixer": ("create:whisk", drive),
            "deployer": (group.get("hand", "create:brass_hand"), control),
            "saw": ("create:iron_sheet", drive),
            "fan": ("create:propeller", drive),
            "roller": ("create:crushing_wheel", drive),
            "gearbox": ("create:cogwheel", "create:large_cogwheel"),
            "clutch": ("minecraft:redstone", control),
            "chain_conveyor": ("create:metal_bracket", drive),
            "depot": (plate, "create:andesite_alloy"),
            "configurable_gearbox": ("create:precision_mechanism", control),
            "automatic_clutch": ("create:redstone_link", control),
        }
        left, right = specific[kind]
        yield {
            "id": entry.get("id", f"industrial_colonies:manufacturing/{tier}/{kind}"),
            "phase": phase,
            "type": "shaped",
            "comment": f"Upgrade the {source_tier} {lower_name} into the {tier} manufacturing environment",
            "pattern": family_patterns[kind],
            "key": {
                "P": plate,
                "L": left,
                "C": casing,
                "B": source,
                "D": drive,
                "R": right,
            },
            "output": output,
            "remove": entry.get("remove", []),
            "exclusive_output": True,
        }


def expand_manifest(data: dict[str, Any]) -> list[dict[str, Any]]:
    recipes = list(require_list(data.get("recipes", []), "manifest recipes"))
    for group in require_list(data.get("machine_families", []), "manifest machine_families"):
        recipes.extend(expand_machine_family(group))
    phases = require_list(data.get("phase_order"), "phase_order")
    if not phases or any(not isinstance(phase, str) or not phase.strip() for phase in phases):
        raise ValueError("phase_order must contain nonblank strings")
    if len(phases) != len(set(phases)):
        raise ValueError("phase_order contains duplicates")
    phase_order = {phase: index for index, phase in enumerate(phases)}
    unknown_phases = sorted({recipe.get("phase") for recipe in recipes} - set(phase_order))
    if unknown_phases:
        raise ValueError(f"recipes reference unknown phases: {unknown_phases}")
    recipes.sort(key=lambda recipe: (phase_order[recipe["phase"]], recipe.get("order", 999), recipe["id"]))
    return recipes


def compile_manifest(manifest: Path, output: Path) -> dict[str, Any]:
    data = load_json(manifest)
    if data.get("schema_version") != 1:
        raise ValueError("managed recipe manifest must use schema_version 1")
    preserved_recipe_ids = require_list(
        data.get("preserve_recipe_ids", []), "preserve_recipe_ids"
    )
    if len(preserved_recipe_ids) != len(set(preserved_recipe_ids)):
        raise ValueError("preserve_recipe_ids contains duplicates")
    for identity in preserved_recipe_ids:
        if not isinstance(identity, str) or not RESOURCE_ID.fullmatch(identity):
            raise ValueError(f"preserve_recipe_ids contains invalid recipe ID {identity!r}")
    old_recipes, old_removals = existing_uids(output)
    specs = expand_manifest(data)
    compiled: list[OrderedDict[str, Any]] = []
    removal_ids: list[str] = []
    seen_recipes: set[str] = set()
    for spec in specs:
        identity = str(spec.get("id", "")).strip()
        if not identity or identity in seen_recipes:
            raise ValueError(f"blank or duplicate managed recipe id: {identity!r}")
        seen_recipes.add(identity)
        uid = old_recipes.get(identity, stable_uid("recipe", identity))
        kind = spec["type"]
        if kind == "shaped":
            compiled.append(shaped(spec, uid, False))
        elif kind == "shapeless":
            compiled.append(shapeless(spec, uid))
        elif kind == "mechanical_crafting":
            compiled.append(shaped(spec, uid, True))
        elif kind == "sequenced_assembly":
            compiled.append(sequenced(spec, uid))
        elif kind == "tfmg_vat":
            compiled.append(tfmg_vat(spec, uid))
        elif kind in MEKANISM_LAYOUTS:
            compiled.append(mekanism_process(spec, uid))
        else:
            compiled.append(process(spec, uid))
        removals = require_list(spec.get("remove", []), f"{identity} remove")
        if spec.get("exclusive_output") and not removals:
            raise ValueError(f"{identity} is exclusive_output but removes no source recipes")
        for removal_id in removals:
            if not isinstance(removal_id, str) or not RESOURCE_ID.fullmatch(removal_id):
                raise ValueError(f"{identity} has invalid exact removal ID {removal_id!r}")
            removal_ids.append(removal_id)

    for identity in require_list(data.get("additional_removals", []), "additional_removals"):
        if not isinstance(identity, str) or not RESOURCE_ID.fullmatch(identity):
            raise ValueError(f"additional_removals contains invalid recipe ID {identity!r}")
        removal_ids.append(identity)
    unique_removals = list(OrderedDict.fromkeys(removal_ids))
    preserve_conflicts = sorted(set(unique_removals).intersection(preserved_recipe_ids))
    if preserve_conflicts:
        raise ValueError(
            f"preserved installed recipes are also removed: {preserve_conflicts}"
        )
    removals: list[OrderedDict[str, Any]] = []
    for identity in unique_removals:
        entry: OrderedDict[str, Any] = OrderedDict()
        entry["uid"] = old_removals.get(identity, stable_uid("removal", identity))
        entry["output"] = ""
        entry["input"] = ""
        entry["mod"] = ""
        entry["recipeId"] = identity
        removals.append(entry)

    result: OrderedDict[str, Any] = OrderedDict()
    result["schema"] = 1
    result["project"] = str(data.get("project", "default"))
    result["recipes"] = compiled
    result["removals"] = removals
    result["retiredRecipeUids"] = require_list(
        data.get("retired_recipe_uids", []), "retired_recipe_uids"
    )
    result["retiredRemovalUids"] = require_list(
        data.get("retired_removal_uids", []), "retired_removal_uids"
    )
    all_uids = {
        *(str(entry["uid"]) for entry in compiled),
        *(str(entry["uid"]) for entry in removals),
    }
    all_retired: set[str] = set()
    for label, retired in (
        ("retired_recipe_uids", result["retiredRecipeUids"]),
        ("retired_removal_uids", result["retiredRemovalUids"]),
    ):
        if len(retired) != len(set(retired)):
            raise ValueError(f"{label} contains duplicate UIDs")
        for retired_uid in retired:
            try:
                uuid.UUID(str(retired_uid))
            except ValueError as error:
                raise ValueError(f"{label} contains invalid UUID {retired_uid!r}") from error
            if str(retired_uid) in all_uids:
                raise ValueError(f"retired UID is still actively managed: {retired_uid}")
            if str(retired_uid) in all_retired:
                raise ValueError(f"retired UID occurs in both retirement arrays: {retired_uid}")
            all_retired.add(str(retired_uid))

    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=output.parent,
        prefix=f".{output.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compile to memory and fail when the committed output differs",
    )
    args = parser.parse_args()
    manifest = args.manifest.resolve()
    output = args.output.resolve()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="industrial-colonies-recipes-") as temporary_dir:
            candidate = Path(temporary_dir) / output.name
            # Seed the candidate with the committed file so existing managed
            # IDs retain their historical UIDs during a deterministic check.
            if output.is_file():
                shutil.copyfile(output, candidate)
            result = compile_manifest(manifest, candidate)
            if not output.is_file() or candidate.read_bytes() != output.read_bytes():
                raise SystemExit(
                    f"Managed recipe output is stale; run {Path(__file__).name}: {output}"
                )
    else:
        result = compile_manifest(manifest, output)
    print(
        f"Generated {len(result['recipes'])} KJSGen recipe cards and "
        f"{len(result['removals'])} exact removals: {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
