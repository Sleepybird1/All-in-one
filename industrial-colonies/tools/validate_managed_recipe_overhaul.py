#!/usr/bin/env python3
"""Validate the managed recipe-overhaul manifest and compiled KJSGen project.

The compact manifest is the design authority and ``default.managed.json`` is
the in-game editor representation.  This checker validates both sides without
rewriting either file.  Graph diagnostics intentionally distinguish hard
reachability defects (cycles and backwards phase dependencies) from useful
design hints (bootstrap recipes and terminal products).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression/managed_recipe_overhaul.json"
DEFAULT_OUTPUT = PROJECT / "pack-kjsgen/default.managed.json"

RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
MOD_ID = re.compile(r"^[a-z0-9_.-]+$")
COUNTED_ITEM = re.compile(r"^(\d+)x\s+([a-z0-9_.-]+:[a-z0-9_./-]+)$")

CREATE_PROCESS_TYPES = {
    "mixing",
    "compacting",
    "deploying",
    "pressing",
    "cutting",
    "crushing",
    "milling",
    "splashing",
    "haunting",
    "sandpaper_polishing",
    "filling",
    "emptying",
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
TFMG_VAT_MODES = {"steel", "firebrick", "both"}
TFMG_VAT_MACHINE_MODES = {"mixing", "two_electrodes"}
TFMG_VAT_CARD_TYPE = "industrial_colonies:tfmg_chemical_vat"
TFMG_VAT_MAX_SLOTS = 4
RECIPE_TYPES = {
    "shaped",
    "shapeless",
    "mechanical_crafting",
    "sequenced_assembly",
    "tfmg_vat",
    *CREATE_PROCESS_TYPES,
    *MEKANISM_LAYOUTS,
}
PROCESS_TYPES = CREATE_PROCESS_TYPES
SEQUENCE_OPERATIONS = {"deploying", "filling", "pressing", "cutting"}
MACHINE_FAMILY_KINDS = {
    "press",
    "mixer",
    "deployer",
    "saw",
    "roller",
    "fan",
    "gearbox",
    "clutch",
    "chain_conveyor",
    "depot",
    "configurable_gearbox",
    "automatic_clutch",
}
SLOT_KINDS = {
    "ITEM",
    "ITEM_TAG",
    "FLUID",
    "FLUID_TAG",
    "CHEMICAL",
    "CHEMICAL_TAG",
}
TAG_KINDS = {kind for kind in SLOT_KINDS if kind.endswith("_TAG")}
EXPECTED_COMPILED_TYPE = {
    "shaped": "kjsgen:shaped",
    "shapeless": "kjsgen:shapeless",
    "mechanical_crafting": "kjsgen:create_mechanical_crafting",
    "sequenced_assembly": "kjsgen:create_sequenced_assembly",
    "tfmg_vat": TFMG_VAT_CARD_TYPE,
    **{family: f"kjsgen:create_{family}" for family in CREATE_PROCESS_TYPES},
    **{family: f"kjsgen:{family}" for family in MEKANISM_LAYOUTS},
}


@dataclass(frozen=True)
class SlotValue:
    kind: str
    identifier: str
    components: str = ""

    @property
    def is_exact_item(self) -> bool:
        return self.kind == "ITEM"


class Diagnostics:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.hints: list[str] = []

    def error(self, path: str, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    def warn(self, path: str, message: str) -> None:
        self.warnings.append(f"{path}: {message}")

    def hint(self, message: str) -> None:
        self.hints.append(message)


def load_object(path: Path, diagnostics: Diagnostics, label: str) -> dict[str, Any] | None:
    if not path.is_file():
        diagnostics.error(label, f"file does not exist: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        diagnostics.error(label, f"cannot read JSON: {exc}")
        return None
    if not isinstance(value, dict):
        diagnostics.error(label, "top level must be a JSON object")
        return None
    return value


def as_list(value: Any, path: str, diagnostics: Diagnostics) -> list[Any]:
    if not isinstance(value, list):
        diagnostics.error(path, "must be an array")
        return []
    return value


def aliased_field(
    spec: Mapping[str, Any],
    canonical: str,
    alias: str,
    path: str,
    diagnostics: Diagnostics,
) -> Any:
    """Read a strict manifest alias and diagnose ambiguous dual definitions."""

    has_canonical = canonical in spec
    has_alias = alias in spec
    if has_canonical and has_alias and spec[canonical] != spec[alias]:
        diagnostics.error(
            path,
            f"defines conflicting {canonical}/{alias} values",
        )
    if has_canonical:
        return spec[canonical]
    return spec.get(alias)


def valid_resource_id(value: Any) -> bool:
    return isinstance(value, str) and bool(RESOURCE_ID.fullmatch(value.strip()))


def validate_resource_id(value: Any, path: str, diagnostics: Diagnostics) -> str:
    identifier = value.strip() if isinstance(value, str) else ""
    if not identifier:
        diagnostics.error(path, "resource ID is blank")
    elif not RESOURCE_ID.fullmatch(identifier):
        diagnostics.error(path, f"invalid resource ID {identifier!r}")
    return identifier


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


def parse_slot(
    value: Any,
    path: str,
    diagnostics: Diagnostics,
    *,
    output: bool = False,
    machine: bool = False,
    expected_domain: str | None = None,
) -> SlotValue | None:
    """Validate a manifest or compiled slot and return its normalized identity."""

    kind = "ITEM"
    identifier = ""
    metadata: Mapping[str, Any] = {}
    components = ""
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            diagnostics.error(path, "ingredient is blank")
            return None
        if raw.startswith("#"):
            kind = "ITEM_TAG"
            identifier = raw[1:]
        else:
            counted = COUNTED_ITEM.fullmatch(raw)
            if counted:
                if int(counted.group(1)) <= 0:
                    diagnostics.error(path, "item count must be positive")
                identifier = counted.group(2)
            else:
                identifier = raw
    elif isinstance(value, dict):
        metadata = value
        raw_kind = value.get("kind", "ITEM")
        kind = raw_kind.strip().upper() if isinstance(raw_kind, str) else ""
        raw_identifier = value.get("id", "")
        identifier = raw_identifier.strip() if isinstance(raw_identifier, str) else ""
        if identifier.startswith("#") and kind == "ITEM":
            identifier = identifier[1:]
            kind = "ITEM_TAG"
        if not kind:
            diagnostics.error(f"{path}.kind", "slot kind is blank")
        elif kind not in SLOT_KINDS:
            diagnostics.error(f"{path}.kind", f"unsupported slot kind {kind!r}")
        for numeric_key in ("count", "amount"):
            if numeric_key in value:
                amount = value[numeric_key]
                if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
                    diagnostics.error(f"{path}.{numeric_key}", "must be a positive integer")
        if "chance" in value:
            chance = value["chance"]
            if (
                isinstance(chance, bool)
                or not isinstance(chance, (int, float))
                or not 0 < chance <= 1
            ):
                diagnostics.error(f"{path}.chance", "must be greater than 0 and at most 1")
        if "components" in value:
            raw_components = value["components"]
            if kind != "ITEM":
                diagnostics.error(f"{path}.components", "is only supported on ITEM slots")
            if not isinstance(raw_components, str) or not raw_components.strip():
                diagnostics.error(f"{path}.components", "must be a nonblank string")
            else:
                components = raw_components.strip()
                if not valid_components_syntax(components):
                    diagnostics.error(
                        f"{path}.components", "must use safe bracketed item-component syntax"
                    )
    else:
        diagnostics.error(path, f"ingredient must be a string or object, got {type(value).__name__}")
        return None

    if not identifier:
        diagnostics.error(f"{path}.id", "resource ID is blank")
        return None
    if not RESOURCE_ID.fullmatch(identifier):
        diagnostics.error(f"{path}.id", f"invalid resource ID {identifier!r}")
    if output and kind in TAG_KINDS:
        diagnostics.error(path, "outputs cannot be tags")
    if machine and kind != "ITEM":
        diagnostics.error(path, "exact-machine metadata must be a concrete ITEM, not a tag/fluid")
    if machine and isinstance(metadata, Mapping) and any(
        key in metadata for key in ("count", "amount", "chance")
    ):
        diagnostics.error(path, "exact-machine metadata cannot carry count, amount, or chance")
    if expected_domain == "fluid" and kind not in {"FLUID", "FLUID_TAG"}:
        diagnostics.error(path, "a filling step requires FLUID or FLUID_TAG metadata")
    if expected_domain == "item" and kind not in {"ITEM", "ITEM_TAG"}:
        diagnostics.error(path, "this operation requires an item ingredient")
    if expected_domain == "chemical" and kind not in {"CHEMICAL", "CHEMICAL_TAG"}:
        diagnostics.error(path, "this operation requires a chemical ingredient")
    return SlotValue(kind, identifier, components)


def validate_remove_list(
    value: Any, path: str, diagnostics: Diagnostics
) -> list[str]:
    removals = as_list(value, path, diagnostics)
    result: list[str] = []
    for index, identity in enumerate(removals):
        normalized = validate_resource_id(identity, f"{path}[{index}]", diagnostics)
        if normalized:
            result.append(normalized)
    duplicates = sorted(identity for identity, count in Counter(result).items() if count > 1)
    if duplicates:
        diagnostics.error(path, f"contains duplicate exact removals: {duplicates}")
    return result


def output_values(spec: Mapping[str, Any]) -> list[Any]:
    recipe_type = spec.get("type")
    if recipe_type == "emptying":
        return [spec.get("out_item"), spec.get("out_fluid")]
    if recipe_type == "tfmg_vat":
        value = spec.get("results", spec.get("outputs", []))
        return list(value) if isinstance(value, list) else []
    if isinstance(spec.get("outputs"), list):
        values = list(spec["outputs"])
    elif "output" in spec:
        values = [spec["output"]]
    else:
        values = []
    if recipe_type == "mekanism_sawing" and spec.get("extra_output") is not None:
        values.append(spec["extra_output"])
    return values


def validate_uuid_list(value: Any, path: str, diagnostics: Diagnostics) -> list[str]:
    entries = as_list(value, path, diagnostics)
    normalized: list[str] = []
    for index, value in enumerate(entries):
        entry_path = f"{path}[{index}]"
        if not isinstance(value, str):
            diagnostics.error(entry_path, "must be a UUID string")
            continue
        normalized.append(value)
        try:
            uuid.UUID(value)
        except ValueError:
            diagnostics.error(entry_path, f"invalid UUID {value!r}")
    duplicates = sorted(identity for identity, count in Counter(normalized).items() if count > 1)
    if duplicates:
        diagnostics.error(path, f"contains duplicate UIDs: {duplicates}")
    return normalized


def validate_pattern(spec: Mapping[str, Any], path: str, diagnostics: Diagnostics) -> list[SlotValue]:
    pattern = as_list(spec.get("pattern"), f"{path}.pattern", diagnostics)
    rows: list[str] = []
    for index, row in enumerate(pattern):
        if not isinstance(row, str):
            diagnostics.error(f"{path}.pattern[{index}]", "pattern row must be a string")
            continue
        rows.append(row)
    if not rows:
        diagnostics.error(f"{path}.pattern", "must contain at least one row")
        return []
    width = len(rows[0])
    if width < 1 or any(len(row) != width for row in rows):
        diagnostics.error(f"{path}.pattern", "must be rectangular and non-empty")
    limit = 9 if spec.get("type") == "mechanical_crafting" else 3
    if len(rows) > limit or width > limit:
        diagnostics.error(f"{path}.pattern", f"exceeds the supported {limit}x{limit} grid")
    if spec.get("type") == "shaped" and (len(rows) != 3 or width != 3):
        diagnostics.error(f"{path}.pattern", "shaped recipes must be explicitly padded to 3x3")

    key = spec.get("key")
    if not isinstance(key, dict):
        diagnostics.error(f"{path}.key", "must be an object")
        return []
    used = {character for row in rows for character in row if character != " "}
    defined = set(key)
    if " " in defined:
        diagnostics.error(f"{path}.key", "space is reserved for an empty grid cell")
    missing = sorted(used - defined)
    unused = sorted(defined - used)
    if missing or unused:
        diagnostics.error(f"{path}.key", f"symbol mismatch; missing={missing}, unused={unused}")
    inputs: list[SlotValue] = []
    for symbol, value in key.items():
        if not isinstance(symbol, str) or len(symbol) != 1:
            diagnostics.error(f"{path}.key", f"key symbol must be one character: {symbol!r}")
        parsed = parse_slot(value, f"{path}.key[{symbol!r}]", diagnostics, expected_domain="item")
        if parsed:
            inputs.append(parsed)
    return inputs


def exact_machine_required(spec: Mapping[str, Any]) -> bool:
    return any(
        spec.get(key) is True
        for key in ("exact_machine", "machine_required", "requires_exact_machine")
    )


def validate_recipe_spec(
    spec: Any,
    path: str,
    phases: Mapping[str, int],
    diagnostics: Diagnostics,
) -> tuple[list[SlotValue], list[SlotValue], list[str]]:
    """Validate one expanded recipe and return inputs, outputs, removals."""

    if not isinstance(spec, dict):
        diagnostics.error(path, "recipe must be an object")
        return [], [], []
    identity = validate_resource_id(spec.get("id"), f"{path}.id", diagnostics)
    phase = spec.get("phase")
    if not isinstance(phase, str) or not phase.strip() or phase not in phases:
        diagnostics.error(f"{path}.phase", f"unknown phase {phase!r}")
    comment = spec.get("comment")
    if not isinstance(comment, str) or not comment.strip():
        diagnostics.error(f"{path}.comment", "must be a non-blank string")
    recipe_type = spec.get("type")
    if recipe_type not in RECIPE_TYPES:
        diagnostics.error(f"{path}.type", f"unsupported compiler recipe type {recipe_type!r}")
        return [], [], validate_remove_list(spec.get("remove", []), f"{path}.remove", diagnostics)
    if "if_mod_loaded" in spec:
        mod = spec.get("if_mod_loaded")
        if not isinstance(mod, str) or not MOD_ID.fullmatch(mod.strip()):
            diagnostics.error(f"{path}.if_mod_loaded", f"invalid mod ID {mod!r}")
    if "order" in spec and (
        isinstance(spec["order"], bool) or not isinstance(spec["order"], (int, float))
    ):
        diagnostics.error(f"{path}.order", "must be numeric")

    inputs: list[SlotValue] = []
    outputs: list[SlotValue] = []
    if recipe_type in {"shaped", "mechanical_crafting"}:
        inputs.extend(validate_pattern(spec, path, diagnostics))
        if "output" not in spec:
            diagnostics.error(f"{path}.output", "is required")
        else:
            parsed = parse_slot(spec["output"], f"{path}.output", diagnostics, output=True)
            if parsed:
                outputs.append(parsed)
    elif recipe_type == "shapeless":
        raw_inputs = as_list(spec.get("inputs"), f"{path}.inputs", diagnostics)
        if not raw_inputs or len(raw_inputs) > 9:
            diagnostics.error(f"{path}.inputs", "shapeless recipes require 1-9 ingredients")
        for index, value in enumerate(raw_inputs):
            parsed = parse_slot(
                value,
                f"{path}.inputs[{index}]",
                diagnostics,
                expected_domain="item",
            )
            if parsed:
                inputs.append(parsed)
        parsed = parse_slot(
            spec.get("output"), f"{path}.output", diagnostics, output=True
        )
        if parsed:
            outputs.append(parsed)
    elif recipe_type in {"mixing", "compacting"}:
        raw_inputs = as_list(spec.get("inputs"), f"{path}.inputs", diagnostics)
        if not raw_inputs:
            diagnostics.error(f"{path}.inputs", "must contain at least one ingredient")
        for index, value in enumerate(raw_inputs):
            parsed = parse_slot(value, f"{path}.inputs[{index}]", diagnostics)
            if parsed:
                inputs.append(parsed)
        if "outputs" in spec:
            raw_outputs = as_list(spec.get("outputs"), f"{path}.outputs", diagnostics)
        else:
            raw_outputs = [spec.get("output")]
        visual_outputs = [value for value in raw_outputs if value is not None]
        if len(visual_outputs) != 1:
            diagnostics.error(
                f"{path}.outputs",
                f"{recipe_type} requires exactly one nonblank visual output",
            )
        for index, value in enumerate(raw_outputs):
            if value is None:
                continue
            parsed = parse_slot(value, f"{path}.outputs[{index}]", diagnostics, output=True)
            if parsed:
                outputs.append(parsed)
        if spec.get("returned_tool") is not None:
            parse_slot(spec["returned_tool"], f"{path}.returned_tool", diagnostics, output=True)
        if spec.get("heat", "none") not in {
            "none",
            "heated",
            "superheated",
        }:
            diagnostics.error(f"{path}.heat", "must be none, heated, or superheated")
    elif recipe_type == "deploying":
        for field in ("input", "held"):
            parsed = parse_slot(spec.get(field), f"{path}.{field}", diagnostics, expected_domain="item")
            if parsed:
                inputs.append(parsed)
        parsed = parse_slot(spec.get("output"), f"{path}.output", diagnostics, output=True)
        if parsed:
            outputs.append(parsed)
        if "keep_held" in spec and not isinstance(spec["keep_held"], bool):
            diagnostics.error(f"{path}.keep_held", "must be boolean")
    elif recipe_type in {
        "pressing",
        "cutting",
        "crushing",
        "milling",
        "splashing",
        "haunting",
        "sandpaper_polishing",
    }:
        parsed = parse_slot(spec.get("input"), f"{path}.input", diagnostics, expected_domain="item")
        if parsed:
            inputs.append(parsed)
        if "outputs" in spec:
            raw_outputs = as_list(spec.get("outputs"), f"{path}.outputs", diagnostics)
            if not raw_outputs:
                diagnostics.error(f"{path}.outputs", "must contain at least one output")
            if recipe_type == "pressing" and len(raw_outputs) > 2:
                diagnostics.error(f"{path}.outputs", "pressing supports at most two outputs")
            if recipe_type == "sandpaper_polishing" and len(raw_outputs) != 1:
                diagnostics.error(
                    f"{path}.outputs", "sandpaper polishing supports exactly one output"
                )
            for index, value in enumerate(raw_outputs):
                parsed = parse_slot(
                    value, f"{path}.outputs[{index}]", diagnostics, output=True
                )
                if parsed:
                    outputs.append(parsed)
        else:
            parsed = parse_slot(
                spec.get("output"), f"{path}.output", diagnostics, output=True
            )
            if parsed:
                outputs.append(parsed)
        if recipe_type in {"cutting", "crushing", "milling"}:
            defaults = {"cutting": 50, "crushing": 250, "milling": 200}
            processing_time = spec.get("processing_time", defaults[recipe_type])
            if (
                isinstance(processing_time, bool)
                or not isinstance(processing_time, int)
                or processing_time <= 0
            ):
                diagnostics.error(f"{path}.processing_time", "must be a positive integer")
    elif recipe_type == "filling":
        parsed = parse_slot(
            spec.get("input"), f"{path}.input", diagnostics, expected_domain="item"
        )
        if parsed:
            inputs.append(parsed)
        parse_slot(
            spec.get("fluid"),
            f"{path}.fluid",
            diagnostics,
            expected_domain="fluid",
        )
        parsed = parse_slot(
            spec.get("output"), f"{path}.output", diagnostics, output=True
        )
        if parsed:
            outputs.append(parsed)
    elif recipe_type == "emptying":
        parsed = parse_slot(
            spec.get("input"), f"{path}.input", diagnostics, expected_domain="item"
        )
        if parsed:
            inputs.append(parsed)
        parsed = parse_slot(
            spec.get("out_item"),
            f"{path}.out_item",
            diagnostics,
            output=True,
            expected_domain="item",
        )
        if parsed:
            outputs.append(parsed)
        parsed = parse_slot(
            spec.get("out_fluid"),
            f"{path}.out_fluid",
            diagnostics,
            output=True,
            expected_domain="fluid",
        )
        if parsed:
            outputs.append(parsed)
            if parsed.kind != "FLUID":
                diagnostics.error(f"{path}.out_fluid", "must be a concrete FLUID output")
    elif recipe_type == "sequenced_assembly":
        parsed = parse_slot(spec.get("input"), f"{path}.input", diagnostics, expected_domain="item")
        if parsed:
            inputs.append(parsed)
        parse_slot(
            spec.get("transitional"),
            f"{path}.transitional",
            diagnostics,
            expected_domain="item",
        )
        if "outputs" in spec:
            raw_outputs = as_list(spec.get("outputs"), f"{path}.outputs", diagnostics)
        else:
            raw_outputs = [spec.get("output")]
        if not raw_outputs or any(value is None for value in raw_outputs):
            diagnostics.error(f"{path}.outputs", "must contain at least one nonblank output")
        for index, value in enumerate(raw_outputs):
            parsed = parse_slot(value, f"{path}.outputs[{index}]", diagnostics, output=True)
            if parsed:
                outputs.append(parsed)
        loops = spec.get("loops", 1)
        if isinstance(loops, bool) or not isinstance(loops, int) or loops <= 0:
            diagnostics.error(f"{path}.loops", "must be a positive integer")
        steps = as_list(spec.get("steps"), f"{path}.steps", diagnostics)
        if not steps:
            diagnostics.error(f"{path}.steps", "must contain at least one operation")
        for index, step in enumerate(steps):
            step_path = f"{path}.steps[{index}]"
            if not isinstance(step, dict):
                diagnostics.error(step_path, "step must be an object")
                continue
            operation = step.get("op")
            if operation not in SEQUENCE_OPERATIONS:
                diagnostics.error(f"{step_path}.op", f"unsupported operation {operation!r}")
                continue
            if operation == "deploying":
                parsed = parse_slot(
                    step.get("ingredient"),
                    f"{step_path}.ingredient",
                    diagnostics,
                    expected_domain="item",
                )
                if parsed:
                    inputs.append(parsed)
            elif operation == "filling":
                parse_slot(
                    step.get("fluid"),
                    f"{step_path}.fluid",
                    diagnostics,
                    expected_domain="fluid",
                )
            if step.get("machine") is not None:
                parse_slot(step["machine"], f"{step_path}.machine", diagnostics, machine=True)
            else:
                diagnostics.error(
                    f"{step_path}.machine",
                    f"must explicitly select its exact {operation} machine",
                )
    elif recipe_type == "tfmg_vat":
        raw_ingredients = as_list(
            aliased_field(spec, "ingredients", "inputs", path, diagnostics),
            f"{path}.ingredients/inputs",
            diagnostics,
        )
        raw_results = as_list(
            aliased_field(spec, "results", "outputs", path, diagnostics),
            f"{path}.results/outputs",
            diagnostics,
        )
        for label, values in (("ingredients", raw_ingredients), ("results", raw_results)):
            if not values or len(values) > TFMG_VAT_MAX_SLOTS:
                diagnostics.error(
                    f"{path}.{label}",
                    f"TFMG Vat requires 1-{TFMG_VAT_MAX_SLOTS} {label}",
                )
        expanded_item_ingredients = 0
        fluid_ingredients = 0
        for index, value in enumerate(raw_ingredients):
            field_path = f"{path}.ingredients[{index}]"
            parsed = parse_slot(value, field_path, diagnostics)
            if parsed is None:
                continue
            if parsed.kind not in {"ITEM", "ITEM_TAG", "FLUID", "FLUID_TAG"}:
                diagnostics.error(field_path, "must be an item/tag/fluid ingredient")
            if parsed.kind in {"ITEM", "ITEM_TAG"}:
                inputs.append(parsed)
                counted = COUNTED_ITEM.fullmatch(value.strip()) if isinstance(value, str) else None
                if counted:
                    expanded_item_ingredients += int(counted.group(1))
                elif isinstance(value, dict):
                    count = value.get("count", 1)
                    if isinstance(count, int) and not isinstance(count, bool) and count > 0:
                        expanded_item_ingredients += count
                else:
                    expanded_item_ingredients += 1
            elif parsed.kind in {"FLUID", "FLUID_TAG"}:
                fluid_ingredients += 1
            if isinstance(value, dict):
                if "components" in value or "chance" in value:
                    diagnostics.error(field_path, "cannot use components or chance")
                if parsed.kind.startswith("ITEM") and "amount" in value:
                    diagnostics.error(field_path, "item ingredients cannot use amount")
                if parsed.kind.startswith("FLUID") and "count" in value:
                    diagnostics.error(field_path, "fluid ingredients cannot use count")
        if expanded_item_ingredients > TFMG_VAT_MAX_SLOTS:
            diagnostics.error(
                f"{path}.ingredients",
                "expanded item ingredients exceed TFMG's four-item limit",
            )
        if fluid_ingredients > TFMG_VAT_MAX_SLOTS:
            diagnostics.error(
                f"{path}.ingredients", "fluid ingredients exceed TFMG's four-fluid limit"
            )

        item_results = 0
        fluid_results = 0
        for index, value in enumerate(raw_results):
            field_path = f"{path}.results[{index}]"
            parsed = parse_slot(value, field_path, diagnostics, output=True)
            if parsed is None:
                continue
            if parsed.kind not in {"ITEM", "FLUID"}:
                diagnostics.error(field_path, "must be a concrete item/fluid result")
            else:
                outputs.append(parsed)
                if parsed.kind == "ITEM":
                    item_results += 1
                else:
                    fluid_results += 1
            if isinstance(value, dict):
                if "components" in value:
                    diagnostics.error(field_path, "results cannot use components")
                if parsed.kind == "ITEM" and "amount" in value:
                    diagnostics.error(field_path, "item results cannot use amount")
                if parsed.kind == "FLUID" and any(key in value for key in ("count", "chance")):
                    diagnostics.error(field_path, "fluid results cannot use count or chance")
        if item_results > TFMG_VAT_MAX_SLOTS:
            diagnostics.error(f"{path}.results", "item results exceed TFMG's four-item limit")
        if fluid_results > TFMG_VAT_MAX_SLOTS:
            diagnostics.error(f"{path}.results", "fluid results exceed TFMG's four-fluid limit")

        vat_mode = aliased_field(spec, "vat_mode", "vat", path, diagnostics)
        if vat_mode not in TFMG_VAT_MODES:
            diagnostics.error(
                f"{path}.vat_mode", f"must be one of {sorted(TFMG_VAT_MODES)}"
            )
        machine_mode = aliased_field(spec, "machine_mode", "machine", path, diagnostics)
        if machine_mode not in TFMG_VAT_MACHINE_MODES:
            diagnostics.error(
                f"{path}.machine_mode",
                f"must be one of {sorted(TFMG_VAT_MACHINE_MODES)}",
            )
        if spec.get("heat", "none") not in {"none", "heated", "superheated"}:
            diagnostics.error(f"{path}.heat", "must be none, heated, or superheated")
        min_size = spec.get("min_size", 0)
        if isinstance(min_size, bool) or not isinstance(min_size, int) or min_size < 0:
            diagnostics.error(f"{path}.min_size", "must be a non-negative integer")
        processing_time = spec.get("processing_time", 100)
        if (
            isinstance(processing_time, bool)
            or not isinstance(processing_time, int)
            or processing_time <= 0
        ):
            diagnostics.error(f"{path}.processing_time", "must be a positive integer")
        for forbidden in ("pressure", "heat_level"):
            if forbidden in spec:
                diagnostics.error(
                    f"{path}.{forbidden}",
                    "is not exposed by the bounded TFMG 1.2.0 Chemical Vat editor",
                )
    elif recipe_type in MEKANISM_LAYOUTS:
        for field, expected_kind in MEKANISM_LAYOUTS[recipe_type]:
            field_path = f"{path}.{field}"
            is_output = field == "output"
            parsed = parse_slot(
                spec.get(field),
                field_path,
                diagnostics,
                output=is_output,
                expected_domain=expected_kind.lower(),
            )
            if not parsed:
                continue
            if is_output:
                outputs.append(parsed)
            elif expected_kind == "ITEM":
                inputs.append(parsed)
        if recipe_type == "mekanism_metallurgic_infusing" and "per_tick_usage" in spec:
            if not isinstance(spec["per_tick_usage"], bool):
                diagnostics.error(f"{path}.per_tick_usage", "must be boolean")
        if recipe_type == "mekanism_sawing":
            extra = spec.get("extra_output")
            if extra is not None:
                parsed = parse_slot(
                    extra,
                    f"{path}.extra_output",
                    diagnostics,
                    output=True,
                    expected_domain="item",
                )
                if parsed:
                    outputs.append(parsed)
                chance = spec.get("secondary_chance", 1.0)
                if (
                    isinstance(chance, bool)
                    or not isinstance(chance, (int, float))
                    or not 0 < chance <= 1
                ):
                    diagnostics.error(
                        f"{path}.secondary_chance", "must be greater than 0 and at most 1"
                    )
            elif "secondary_chance" in spec:
                diagnostics.warn(
                    f"{path}.secondary_chance",
                    "is ignored because extra_output is not defined",
                )
        if recipe_type == "mekanism_energy_conversion":
            energy = spec.get("energy", 10000)
            if isinstance(energy, bool) or not isinstance(energy, int) or energy <= 0:
                diagnostics.error(f"{path}.energy", "must be a positive integer")

    if recipe_type in PROCESS_TYPES:
        if spec.get("machine") is not None:
            parse_slot(spec["machine"], f"{path}.machine", diagnostics, machine=True)
        elif recipe_type in CREATE_MACHINE_FAMILIES or exact_machine_required(spec):
            diagnostics.error(f"{path}.machine", "exact-machine recipe has no machine metadata")

    removals = validate_remove_list(spec.get("remove", []), f"{path}.remove", diagnostics)
    if spec.get("exclusive_output") is True and not removals:
        diagnostics.error(f"{path}.remove", "exclusive output has no stock/source recipe removal")
    if identity and identity in removals:
        diagnostics.error(f"{path}.remove", "replacement recipe removes itself")
    return inputs, outputs, removals


def validate_machine_families(
    data: Mapping[str, Any], phases: Mapping[str, int], diagnostics: Diagnostics
) -> None:
    groups = as_list(data.get("machine_families", []), "manifest.machine_families", diagnostics)
    for group_index, group in enumerate(groups):
        path = f"manifest.machine_families[{group_index}]"
        if not isinstance(group, dict):
            diagnostics.error(path, "machine family must be an object")
            continue
        for field in ("tier", "source_tier", "phase"):
            if not isinstance(group.get(field), str) or not group[field].strip():
                diagnostics.error(f"{path}.{field}", "must be a non-blank string")
        if isinstance(group.get("phase"), str) and group["phase"] not in phases:
            diagnostics.error(f"{path}.phase", f"unknown phase {group['phase']!r}")
        for field in ("casing", "plate", "control", "drive"):
            validate_resource_id(group.get(field), f"{path}.{field}", diagnostics)
        if "hand" in group:
            validate_resource_id(group.get("hand"), f"{path}.hand", diagnostics)
        source_items = group.get("source_items")
        if not isinstance(source_items, dict):
            diagnostics.error(f"{path}.source_items", "must be an object")
            source_items = {}
        else:
            for kind, value in source_items.items():
                if kind not in MACHINE_FAMILY_KINDS:
                    diagnostics.error(f"{path}.source_items", f"unsupported machine kind {kind!r}")
                validate_resource_id(value, f"{path}.source_items.{kind}", diagnostics)
        entries = as_list(group.get("recipes"), f"{path}.recipes", diagnostics)
        if not entries:
            diagnostics.error(f"{path}.recipes", "must contain at least one machine recipe")
        for entry_index, entry in enumerate(entries):
            entry_path = f"{path}.recipes[{entry_index}]"
            if not isinstance(entry, dict):
                diagnostics.error(entry_path, "machine recipe must be an object")
                continue
            kind = entry.get("kind")
            if kind not in MACHINE_FAMILY_KINDS:
                diagnostics.error(f"{entry_path}.kind", f"unsupported machine-family kind {kind!r}")
            if not entry.get("base") and kind not in source_items:
                diagnostics.error(
                    f"{entry_path}.base",
                    f"no base item and source_items has no entry for {kind!r}",
                )
            if entry.get("base"):
                validate_resource_id(entry["base"], f"{entry_path}.base", diagnostics)
            validate_resource_id(entry.get("output"), f"{entry_path}.output", diagnostics)
            if "id" in entry:
                validate_resource_id(entry["id"], f"{entry_path}.id", diagnostics)
            removals = validate_remove_list(entry.get("remove", []), f"{entry_path}.remove", diagnostics)
            if not removals:
                diagnostics.error(
                    f"{entry_path}.remove",
                    "machine-family upgrades are exclusive but have no source removal",
                )


def expand_manifest_safely(
    data: Mapping[str, Any], diagnostics: Diagnostics
) -> list[dict[str, Any]]:
    """Use the real compiler expansion only after basic family validation."""

    try:
        from generate_managed_recipe_overhaul import expand_manifest  # type: ignore

        expanded = expand_manifest(dict(data))
    except (ImportError, KeyError, TypeError, ValueError) as exc:
        diagnostics.error("manifest", f"compiler cannot expand this manifest: {exc}")
        return []
    if not isinstance(expanded, list) or any(not isinstance(spec, dict) for spec in expanded):
        diagnostics.error("manifest", "compiler expansion did not return recipe objects")
        return []
    return expanded


def validate_manifest(
    data: Mapping[str, Any], diagnostics: Diagnostics
) -> tuple[list[dict[str, Any]], dict[str, list[SlotValue]], dict[str, list[SlotValue]], list[str], dict[str, int]]:
    if data.get("schema_version") != 1:
        diagnostics.error("manifest.schema_version", "must equal 1")
    project = data.get("project", "default")
    if not isinstance(project, str) or not project.strip():
        diagnostics.error("manifest.project", "must be a non-blank string")

    phase_order = as_list(data.get("phase_order"), "manifest.phase_order", diagnostics)
    phases: dict[str, int] = {}
    for index, phase in enumerate(phase_order):
        if not isinstance(phase, str) or not phase.strip():
            diagnostics.error(f"manifest.phase_order[{index}]", "phase must be a non-blank string")
            continue
        if phase in phases:
            diagnostics.error(f"manifest.phase_order[{index}]", f"duplicate phase {phase!r}")
        else:
            phases[phase] = index
    if not phases:
        diagnostics.error("manifest.phase_order", "must define at least one phase")

    raw_recipes = as_list(data.get("recipes", []), "manifest.recipes", diagnostics)
    for index, spec in enumerate(raw_recipes):
        if not isinstance(spec, dict):
            diagnostics.error(f"manifest.recipes[{index}]", "recipe must be an object")
    validate_machine_families(data, phases, diagnostics)
    additional = validate_remove_list(
        data.get("additional_removals", []), "manifest.additional_removals", diagnostics
    )
    preserved_recipe_ids = validate_remove_list(
        data.get("preserve_recipe_ids", []), "manifest.preserve_recipe_ids", diagnostics
    )
    retired_recipe_uids = validate_uuid_list(
        data.get("retired_recipe_uids", []),
        "manifest.retired_recipe_uids",
        diagnostics,
    )
    retired_removal_uids = validate_uuid_list(
        data.get("retired_removal_uids", []),
        "manifest.retired_removal_uids",
        diagnostics,
    )
    retired_overlap = sorted(set(retired_recipe_uids).intersection(retired_removal_uids))
    if retired_overlap:
        diagnostics.error(
            "manifest.retired_uids",
            f"UIDs occur in both retirement arrays: {retired_overlap}",
        )

    expanded = expand_manifest_safely(data, diagnostics)
    recipe_inputs: dict[str, list[SlotValue]] = {}
    recipe_outputs: dict[str, list[SlotValue]] = {}
    all_removals: list[str] = []
    identities: list[str] = []
    primary_outputs: defaultdict[str, list[str]] = defaultdict(list)
    specs_by_id: dict[str, dict[str, Any]] = {}
    for index, spec in enumerate(expanded):
        path = f"expanded.recipes[{index}]"
        identity = spec.get("id") if isinstance(spec.get("id"), str) else ""
        inputs, outputs, removals = validate_recipe_spec(spec, path, phases, diagnostics)
        if identity:
            identities.append(identity)
            specs_by_id[identity] = spec
            recipe_inputs[identity] = inputs
            recipe_outputs[identity] = outputs
            if outputs:
                primary_outputs[outputs[0].identifier].append(identity)
        all_removals.extend(removals)

    duplicate_ids = sorted(identity for identity, count in Counter(identities).items() if count > 1)
    if duplicate_ids:
        diagnostics.error("manifest.recipes", f"duplicate expanded recipe IDs: {duplicate_ids}")
    for output, producers in sorted(primary_outputs.items()):
        if len(producers) <= 1:
            continue
        allowed = all(specs_by_id[identity].get("allow_duplicate_output") is True for identity in producers)
        if allowed:
            diagnostics.warn(
                "manifest.recipes",
                f"explicitly allowed duplicate primary output {output}: {producers}",
            )
        else:
            diagnostics.error(
                "manifest.recipes",
                f"duplicate primary output {output}: {producers}; use unique outputs or explicitly opt in",
            )

    all_removals.extend(additional)
    preserve_conflicts = sorted(set(all_removals).intersection(preserved_recipe_ids))
    if preserve_conflicts:
        diagnostics.error(
            "manifest.preserve_recipe_ids",
            f"preserved installed recipes are also removed: {preserve_conflicts}",
        )
    duplicate_removals = sorted(
        identity for identity, count in Counter(all_removals).items() if count > 1
    )
    if duplicate_removals:
        diagnostics.error(
            "manifest.removals",
            f"exact recipe removals are declared more than once: {duplicate_removals}",
        )
    managed_ids = set(identities)
    overlap = sorted(managed_ids.intersection(all_removals))
    if overlap:
        diagnostics.error("manifest.removals", f"managed replacements also remove themselves: {overlap}")

    for identity, spec in specs_by_id.items():
        output = recipe_outputs.get(identity, [])
        own_removals = spec.get("remove", [])
        if (
            output
            and output[0].identifier.split(":", 1)[0] != "industrial_colonies"
            and not own_removals
            and spec.get("new_output") is not True
            and spec.get("allow_stock_alternative") is not True
        ):
            diagnostics.warn(
                identity,
                "recreates an external-mod output without removing a source recipe; mark new_output/allow_stock_alternative if intentional",
            )

    return expanded, recipe_inputs, recipe_outputs, all_removals, phases


def expected_machine_slots(spec: Mapping[str, Any]) -> dict[str, SlotValue]:
    expected: dict[str, SlotValue] = {}
    recipe_type = spec.get("type")
    machine = spec.get("machine")
    if recipe_type in PROCESS_TYPES and machine is not None:
        parsed = normalize_slot_without_diagnostics(machine)
        if parsed:
            expected[f"__machine_process_{recipe_type}"] = parsed
    if recipe_type == "sequenced_assembly":
        for index, step in enumerate(spec.get("steps", [])):
            if not isinstance(step, dict) or step.get("machine") is None:
                continue
            parsed = normalize_slot_without_diagnostics(step["machine"])
            if parsed:
                expected[f"__machine_step_{index}_{step.get('op')}"] = parsed
    return expected


def expected_compiled_card(
    spec: Mapping[str, Any], diagnostics: Diagnostics
) -> Mapping[str, Any] | None:
    """Compile one card with the production helpers for stale-output checks.

    Independent validation above still checks the safety properties so a
    compiler defect cannot bless itself.  This comparison has a narrower job:
    prove that the checked-in KJSGen card reflects the current manifest byte
    semantics for slots and parameters.
    """

    try:
        from generate_managed_recipe_overhaul import (  # type: ignore
            mekanism_process,
            process,
            sequenced,
            shaped,
            shapeless,
            tfmg_vat,
        )

        recipe_type = spec.get("type")
        dummy_uid = "00000000-0000-0000-0000-000000000000"
        if recipe_type == "shaped":
            return shaped(dict(spec), dummy_uid, False)
        if recipe_type == "shapeless":
            return shapeless(dict(spec), dummy_uid)
        if recipe_type == "mechanical_crafting":
            return shaped(dict(spec), dummy_uid, True)
        if recipe_type == "sequenced_assembly":
            return sequenced(dict(spec), dummy_uid)
        if recipe_type == "tfmg_vat":
            return tfmg_vat(dict(spec), dummy_uid)
        if recipe_type in MEKANISM_LAYOUTS:
            return mekanism_process(dict(spec), dummy_uid)
        if recipe_type in PROCESS_TYPES:
            return process(dict(spec), dummy_uid)
    except (ImportError, KeyError, TypeError, ValueError) as exc:
        diagnostics.error(
            f"recipe[{spec.get('id')}]",
            f"compiler cannot emit this recipe: {exc}",
        )
        return None
    diagnostics.error(
        f"recipe[{spec.get('id')}].type",
        f"compiler has no handler for {spec.get('type')!r}",
    )
    return None


def normalize_slot_without_diagnostics(value: Any) -> SlotValue | None:
    if isinstance(value, str):
        raw = value.strip()
        if raw.startswith("#"):
            return SlotValue("ITEM_TAG", raw[1:])
        counted = COUNTED_ITEM.fullmatch(raw)
        return SlotValue("ITEM", counted.group(2) if counted else raw) if raw else None
    if isinstance(value, dict):
        kind = str(value.get("kind", "ITEM")).upper()
        identifier = str(value.get("id", "")).strip()
        if identifier.startswith("#") and kind == "ITEM":
            return SlotValue("ITEM_TAG", identifier[1:])
        components = value.get("components", "")
        return SlotValue(kind, identifier, components) if identifier else None
    return None


def compiled_output_slots(recipe: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    slots = recipe.get("slots")
    if not isinstance(slots, dict):
        return []
    recipe_type = recipe.get("type")
    if recipe_type == "kjsgen:mekanism_energy_conversion":
        return []
    if recipe_type == "kjsgen:create_emptying":
        return [
            (key, slots[key])
            for key in ("outItem", "outFluid")
            if isinstance(slots.get(key), dict)
        ]
    if recipe_type == "kjsgen:mekanism_sawing":
        return [
            (key, slots[key])
            for key in ("output", "extraOutput")
            if isinstance(slots.get(key), dict)
        ]
    if recipe_type == TFMG_VAT_CARD_TYPE:
        return sorted(
            [
                (key, value)
                for key, value in slots.items()
                if isinstance(key, str)
                and key.startswith("results")
                and isinstance(value, dict)
            ],
            key=lambda entry: int(entry[0].removeprefix("results")),
        )
    result: list[tuple[str, Mapping[str, Any]]] = []
    for key, value in slots.items():
        if isinstance(key, str) and key.startswith("output") and isinstance(value, dict):
            result.append((key, value))

    def rank(entry: tuple[str, Mapping[str, Any]]) -> tuple[int, str]:
        key = entry[0]
        if key == "output":
            return (0, key)
        suffix = key.removeprefix("output")
        return (int(suffix) + 1 if suffix.isdigit() else 9999, key)

    return sorted(result, key=rank)


def validate_compiled_output(
    data: Mapping[str, Any],
    manifest: Mapping[str, Any],
    specs: Sequence[Mapping[str, Any]],
    manifest_removals: Sequence[str],
    diagnostics: Diagnostics,
) -> None:
    expected_root_fields = {
        "schema",
        "project",
        "recipes",
        "removals",
        "retiredRecipeUids",
        "retiredRemovalUids",
    }
    actual_root_fields = set(data)
    if actual_root_fields != expected_root_fields:
        diagnostics.error(
            "compiled",
            "top-level fields differ from compiler output; "
            f"missing={sorted(expected_root_fields - actual_root_fields)}, "
            f"extra={sorted(actual_root_fields - expected_root_fields)}",
        )
    if data.get("schema") != 1:
        diagnostics.error("compiled.schema", "must equal 1")
    expected_project = str(manifest.get("project", "default"))
    if data.get("project") != expected_project:
        diagnostics.error(
            "compiled.project",
            f"expected {expected_project!r}, got {data.get('project')!r}",
        )
    recipes = as_list(data.get("recipes"), "compiled.recipes", diagnostics)
    removals = as_list(data.get("removals"), "compiled.removals", diagnostics)
    retired_recipe_uids = validate_uuid_list(
        data.get("retiredRecipeUids"), "compiled.retiredRecipeUids", diagnostics
    )
    retired_removal_uids = validate_uuid_list(
        data.get("retiredRemovalUids"), "compiled.retiredRemovalUids", diagnostics
    )
    expected_retired_recipes = manifest.get("retired_recipe_uids", [])
    expected_retired_removals = manifest.get("retired_removal_uids", [])
    if retired_recipe_uids != expected_retired_recipes:
        diagnostics.error(
            "compiled.retiredRecipeUids",
            "does not exactly match manifest.retired_recipe_uids",
        )
    if retired_removal_uids != expected_retired_removals:
        diagnostics.error(
            "compiled.retiredRemovalUids",
            "does not exactly match manifest.retired_removal_uids",
        )
    retired_overlap = sorted(set(retired_recipe_uids).intersection(retired_removal_uids))
    if retired_overlap:
        diagnostics.error(
            "compiled.retiredUids",
            f"UIDs occur in both retirement arrays: {retired_overlap}",
        )
    compiled_by_id: dict[str, Mapping[str, Any]] = {}
    recipe_ids: list[str] = []
    removal_ids: list[str] = []
    all_uids: list[str] = []

    for index, recipe in enumerate(recipes):
        path = f"compiled.recipes[{index}]"
        if not isinstance(recipe, dict):
            diagnostics.error(path, "recipe card must be an object")
            continue
        identity = validate_resource_id(recipe.get("recipeId"), f"{path}.recipeId", diagnostics)
        if identity:
            recipe_ids.append(identity)
            compiled_by_id[identity] = recipe
        uid = recipe.get("uid")
        if not isinstance(uid, str):
            diagnostics.error(f"{path}.uid", "must be a UUID string")
        else:
            all_uids.append(uid)
            try:
                uuid.UUID(uid)
            except ValueError:
                diagnostics.error(f"{path}.uid", f"invalid UUID {uid!r}")
        if recipe.get("replaceRecipe") is not False:
            diagnostics.error(f"{path}.replaceRecipe", "must be false; use exact removal cards")
        slots = recipe.get("slots")
        if not isinstance(slots, dict):
            diagnostics.error(f"{path}.slots", "must be an object")
            slots = {}
        card_type = recipe.get("type")
        for key, slot in slots.items():
            is_output = isinstance(key, str) and (
                key.startswith("output")
                or key in {"returned_tool", "outItem", "outFluid", "extraOutput"}
                or (card_type == TFMG_VAT_CARD_TYPE and key.startswith("results"))
            )
            parse_slot(
                slot,
                f"{path}.slots.{key}",
                diagnostics,
                output=is_output,
                machine=isinstance(key, str) and key.startswith("__machine_"),
            )
        if (
            recipe.get("type") != "kjsgen:mekanism_energy_conversion"
            and not compiled_output_slots(recipe)
        ):
            diagnostics.error(f"{path}.slots", "contains no output slot")

    for index, removal in enumerate(removals):
        path = f"compiled.removals[{index}]"
        if not isinstance(removal, dict):
            diagnostics.error(path, "removal card must be an object")
            continue
        identity = validate_resource_id(removal.get("recipeId"), f"{path}.recipeId", diagnostics)
        if identity:
            removal_ids.append(identity)
        uid = removal.get("uid")
        if not isinstance(uid, str):
            diagnostics.error(f"{path}.uid", "must be a UUID string")
        else:
            all_uids.append(uid)
            try:
                uuid.UUID(uid)
            except ValueError:
                diagnostics.error(f"{path}.uid", f"invalid UUID {uid!r}")
        broad = [field for field in ("output", "input", "mod") if str(removal.get(field, "")).strip()]
        if broad:
            diagnostics.error(path, f"exact removal card also sets broad filters: {broad}")
        expected_fields = {"uid", "output", "input", "mod", "recipeId"}
        actual_fields = set(removal)
        if actual_fields != expected_fields:
            diagnostics.error(
                path,
                "fields differ from compiler output; "
                f"missing={sorted(expected_fields - actual_fields)}, "
                f"extra={sorted(actual_fields - expected_fields)}",
            )

    for label, identities in (("recipe", recipe_ids), ("removal", removal_ids)):
        duplicates = sorted(identity for identity, count in Counter(identities).items() if count > 1)
        if duplicates:
            diagnostics.error(f"compiled.{label}s", f"duplicate IDs: {duplicates}")
    duplicate_uids = sorted(uid for uid, count in Counter(all_uids).items() if count > 1)
    if duplicate_uids:
        diagnostics.error("compiled", f"recipe/removal UIDs are duplicated: {duplicate_uids}")
    active_retired_overlap = sorted(set(all_uids).intersection(retired_recipe_uids + retired_removal_uids))
    if active_retired_overlap:
        diagnostics.error(
            "compiled.retiredUids",
            f"retired UIDs are still actively managed: {active_retired_overlap}",
        )

    expected_ids = {str(spec.get("id")) for spec in specs}
    actual_ids = set(recipe_ids)
    if expected_ids != actual_ids:
        diagnostics.error(
            "compiled.recipes",
            f"manifest/compiler recipe coverage differs; missing={sorted(expected_ids - actual_ids)}, extra={sorted(actual_ids - expected_ids)}",
        )
    expected_recipe_order = [str(spec.get("id")) for spec in specs]
    if recipe_ids != expected_recipe_order:
        diagnostics.error(
            "compiled.recipes",
            "recipe order differs from expanded manifest/compiler order",
        )
    expected_removal_set = set(manifest_removals)
    actual_removal_set = set(removal_ids)
    if expected_removal_set != actual_removal_set:
        diagnostics.error(
            "compiled.removals",
            f"manifest removal coverage differs; missing={sorted(expected_removal_set - actual_removal_set)}, extra={sorted(actual_removal_set - expected_removal_set)}",
        )
    if removal_ids != list(manifest_removals):
        diagnostics.error(
            "compiled.removals",
            "removal order differs from manifest/compiler order",
        )
    overlap = sorted(actual_ids.intersection(actual_removal_set))
    if overlap:
        diagnostics.error("compiled", f"replacement recipe IDs are also removed: {overlap}")

    for spec in specs:
        identity = str(spec.get("id", ""))
        recipe = compiled_by_id.get(identity)
        if recipe is None:
            continue
        path = f"compiled.recipe[{identity}]"
        expected_type = EXPECTED_COMPILED_TYPE.get(str(spec.get("type")))
        if recipe.get("type") != expected_type:
            diagnostics.error(
                f"{path}.type",
                f"expected {expected_type!r}, got {recipe.get('type')!r}",
            )
        expected_card = expected_compiled_card(spec, diagnostics)
        if expected_card is not None:
            unexpected_fields = sorted(set(recipe) - set(expected_card))
            missing_fields = sorted(set(expected_card) - set(recipe))
            if unexpected_fields or missing_fields:
                diagnostics.error(
                    path,
                    "fields differ from compiler output; "
                    f"missing={missing_fields}, extra={unexpected_fields}",
                )
            for field in ("type", "recipeId", "comment", "ifModLoaded", "replaceRecipe"):
                expected_present = field in expected_card
                actual_present = field in recipe
                if expected_present != actual_present or (
                    expected_present and expected_card.get(field) != recipe.get(field)
                ):
                    diagnostics.error(
                        f"{path}.{field}",
                        f"stale compiler output; expected={expected_card.get(field)!r}, actual={recipe.get(field)!r}",
                    )
            for field in ("slots", "params"):
                if expected_card.get(field) != recipe.get(field):
                    diagnostics.error(
                        f"{path}.{field}",
                        "stale compiler output differs from the current manifest",
                    )
        slots = recipe.get("slots", {})
        actual_machine: dict[str, SlotValue] = {}
        if isinstance(slots, dict):
            for key, value in slots.items():
                if isinstance(key, str) and key.startswith("__machine_"):
                    parsed = normalize_slot_without_diagnostics(value)
                    if parsed:
                        actual_machine[key] = parsed
        expected_machine = expected_machine_slots(spec)
        if actual_machine != expected_machine:
            diagnostics.error(
                f"{path}.slots",
                f"exact-machine metadata differs; expected={expected_machine}, actual={actual_machine}",
            )
        source_outputs = [
            parsed
            for value in output_values(spec)
            if (parsed := normalize_slot_without_diagnostics(value)) is not None
        ]
        card_outputs = [
            parsed
            for _, value in compiled_output_slots(recipe)
            if (parsed := normalize_slot_without_diagnostics(value)) is not None
        ]
        if source_outputs != card_outputs:
            diagnostics.error(
                f"{path}.slots",
                f"compiled outputs differ from manifest; expected={source_outputs}, actual={card_outputs}",
            )
        if spec.get("type") == "sequenced_assembly":
            params = recipe.get("params")
            if not isinstance(params, dict):
                diagnostics.error(f"{path}.params", "sequenced assembly needs a params object")
            else:
                steps = spec.get("steps", [])
                if params.get("__seqLen") != str(len(steps)):
                    diagnostics.error(f"{path}.params.__seqLen", "does not match manifest steps")
                if params.get("loops") != str(spec.get("loops", 1)):
                    diagnostics.error(f"{path}.params.loops", "does not match manifest loops")
                for index, step in enumerate(steps):
                    if isinstance(step, dict) and params.get(f"seq{index}") != step.get("op"):
                        diagnostics.error(
                            f"{path}.params.seq{index}",
                            f"does not match manifest operation {step.get('op')!r}",
                        )


def explicit_dependencies(spec: Mapping[str, Any], diagnostics: Diagnostics) -> list[str]:
    result: list[str] = []
    for field in ("depends_on", "dependencies"):
        if field not in spec:
            continue
        values = as_list(spec[field], f"recipe[{spec.get('id')}].{field}", diagnostics)
        for index, value in enumerate(values):
            identity = validate_resource_id(
                value, f"recipe[{spec.get('id')}].{field}[{index}]", diagnostics
            )
            if identity:
                result.append(identity)
    return result


def find_cycles(nodes: Iterable[str], edges: Mapping[str, set[str]]) -> list[list[str]]:
    color: dict[str, int] = {}
    stack: list[str] = []
    cycles: list[list[str]] = []
    seen_cycles: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for child in sorted(edges.get(node, set())):
            if color.get(child, 0) == 0:
                visit(child)
            elif color.get(child) == 1:
                start = stack.index(child)
                cycle = stack[start:] + [child]
                body = cycle[:-1]
                rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
                canonical = min(rotations) if rotations else tuple()
                if canonical not in seen_cycles:
                    seen_cycles.add(canonical)
                    cycles.append(cycle)
        stack.pop()
        color[node] = 2

    for node in sorted(nodes):
        if color.get(node, 0) == 0:
            visit(node)
    return cycles


def validate_dependency_graph(
    specs: Sequence[Mapping[str, Any]],
    inputs: Mapping[str, Sequence[SlotValue]],
    outputs: Mapping[str, Sequence[SlotValue]],
    phases: Mapping[str, int],
    diagnostics: Diagnostics,
) -> None:
    specs_by_id = {str(spec.get("id")): spec for spec in specs}
    producer_by_item: dict[str, str] = {}
    for identity, values in outputs.items():
        if values and values[0].is_exact_item:
            producer_by_item[values[0].identifier] = identity

    incoming: defaultdict[str, set[str]] = defaultdict(set)
    outgoing: defaultdict[str, set[str]] = defaultdict(set)
    inferred_edges = 0
    explicit_edges = 0
    external_inputs = 0
    for consumer, values in inputs.items():
        for value in values:
            if not value.is_exact_item:
                external_inputs += 1
                continue
            producer = producer_by_item.get(value.identifier)
            if producer is None:
                external_inputs += 1
                continue
            incoming[consumer].add(producer)
            outgoing[producer].add(consumer)
            inferred_edges += 1
        for producer in explicit_dependencies(specs_by_id[consumer], diagnostics):
            if producer not in specs_by_id:
                diagnostics.error(
                    f"recipe[{consumer}].depends_on",
                    f"references unknown managed recipe {producer}",
                )
                continue
            incoming[consumer].add(producer)
            outgoing[producer].add(consumer)
            explicit_edges += 1

    for consumer, producers in sorted(incoming.items()):
        consumer_phase = specs_by_id[consumer].get("phase")
        for producer in sorted(producers):
            if producer == consumer:
                diagnostics.error(f"recipe[{consumer}]", "depends on its own primary output")
                continue
            producer_phase = specs_by_id[producer].get("phase")
            if producer_phase in phases and consumer_phase in phases:
                if phases[str(producer_phase)] > phases[str(consumer_phase)]:
                    diagnostics.error(
                        f"recipe[{consumer}]",
                        f"depends on later-phase {producer} ({producer_phase} -> {consumer_phase})",
                    )

    cycles = find_cycles(specs_by_id, outgoing)
    for cycle in cycles:
        diagnostics.error("dependency_graph", "cycle: " + " -> ".join(cycle))

    roots = sorted(identity for identity in specs_by_id if not incoming.get(identity))
    terminals = sorted(identity for identity in specs_by_id if not outgoing.get(identity))
    visited: set[str] = set(roots)
    queue = deque(roots)
    while queue:
        node = queue.popleft()
        for child in outgoing.get(node, set()):
            if child not in visited:
                visited.add(child)
                queue.append(child)
    unreachable = sorted(set(specs_by_id) - visited)
    if unreachable and not cycles:
        diagnostics.warn(
            "dependency_graph",
            f"recipes are not reachable from an external-input bootstrap: {unreachable}",
        )
    diagnostics.hint(
        f"Dependency graph: {len(specs_by_id)} recipes, {inferred_edges} inferred item edges, "
        f"{explicit_edges} explicit edges, {len(roots)} bootstrap roots, {len(terminals)} terminal products, "
        f"and {external_inputs} external/tag ingredient references."
    )
    if roots:
        diagnostics.hint("Bootstrap roots: " + ", ".join(roots[:12]) + (" ..." if len(roots) > 12 else ""))
    if terminals:
        diagnostics.hint(
            "Terminal products: " + ", ".join(terminals[:12]) + (" ..." if len(terminals) > 12 else "")
        )


def report(diagnostics: Diagnostics, recipe_count: int, removal_count: int) -> int:
    print(f"Checked {recipe_count} expanded managed recipes and {removal_count} exact removals.")
    for hint in diagnostics.hints:
        print(f"HINT: {hint}")
    for warning in diagnostics.warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if diagnostics.errors:
        print(
            f"FAIL: {len(diagnostics.errors)} error(s), {len(diagnostics.warnings)} warning(s)",
            file=sys.stderr,
        )
        for error in diagnostics.errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: managed recipe overhaul is schema-valid, compiler-covered, exact-removal-safe, "
        f"and dependency-consistent ({len(diagnostics.warnings)} warning(s))."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    diagnostics = Diagnostics()
    manifest = load_object(args.manifest.resolve(), diagnostics, "manifest")
    compiled = load_object(args.output.resolve(), diagnostics, "compiled")
    specs: list[dict[str, Any]] = []
    recipe_inputs: dict[str, list[SlotValue]] = {}
    recipe_outputs: dict[str, list[SlotValue]] = {}
    removal_ids: list[str] = []
    phases: dict[str, int] = {}
    if manifest is not None:
        specs, recipe_inputs, recipe_outputs, removal_ids, phases = validate_manifest(
            manifest, diagnostics
        )
        if specs:
            validate_dependency_graph(
                specs, recipe_inputs, recipe_outputs, phases, diagnostics
            )
        if compiled is not None:
            validate_compiled_output(
                compiled, manifest, specs, removal_ids, diagnostics
            )
    return report(diagnostics, len(specs), len(set(removal_ids)))


if __name__ == "__main__":
    raise SystemExit(main())
