#!/usr/bin/env python3
"""Validate the complete KJSGen-managed Industrial Colonies recipe set.

The script intentionally validates the compiled KJSGen project rather than a
fixed recipe count. It combines runtime-registry evidence from the exported
catalog with candidate-JAR registration evidence and static recipe/layout
evidence from every installed mod JAR.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import uuid
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
MANAGED = PROJECT / "pack-kjsgen/default.managed.json"
MANIFEST = PROJECT / "progression/managed_recipe_overhaul.json"
PROJECT_ITEMS_SOURCE = (
    PROJECT
    / "src/main/java/dev/godpc/industrialcolonies/IndustrialItems.java"
)
LEGACY_TRANSISTOR_UID = "5f2584b1-19d4-49f9-a3d6-265659ea0c05"

RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
RECIPE_ENTRY = re.compile(r"^data/([^/]+)/recipes?/([^/].*)\.json$")
LAYOUT_ENTRY = re.compile(r"^assets/[^/]+/kjsgen_layouts/[^/]+\.json$")
VALID_SLOT_KINDS = {
    "ITEM",
    "ITEM_TAG",
    "FLUID",
    "FLUID_TAG",
    "CHEMICAL",
    "CHEMICAL_TAG",
}

# These are registered in KJSGen's BuiltinRecipeTypes class rather than JSON
# layout resources. Every other accepted type must be found in an installed
# kjsgen_layouts JSON resource.
KJSGEN_BUILTINS = {
    "kjsgen:shaped",
    "kjsgen:shapeless",
    "kjsgen:smelting",
    "kjsgen:blasting",
    "kjsgen:smoking",
    "kjsgen:campfire_cooking",
    "kjsgen:stonecutting",
    "kjsgen:smithing_transform",
    "kjsgen:smithing_trim",
    "kjsgen:brewing",
}

# Missing static sources should normally be a hard failure. Keep this set
# deliberately tiny; version-conditional/future-proof exceptions belong in
# managed/manifest metadata so the reason remains beside the recipe design.
MISSING_SOURCE_ALLOWLIST: frozenset[str] = frozenset()

PRINTED_SILICON_RECIPE = "industrial_colonies:electronics/printed_silicon"
PRINTED_SILICON = "ae2:printed_silicon"


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def catalog_item_ids(path: Path) -> set[str]:
    """Read either the runtime text export or a catalog items.csv file."""

    if path.is_dir():
        path = path / "items.csv"
    if not path.is_file():
        raise ValueError(f"runtime item catalog does not exist: {path}")

    if path.suffix.lower() == ".csv":
        found: set[str] = set()
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError(f"runtime item catalog has no CSV header: {path}")
            id_column = "item_id" if "item_id" in reader.fieldnames else reader.fieldnames[0]
            for row in reader:
                identifier = str(row.get(id_column, "")).strip()
                if RESOURCE_ID.fullmatch(identifier):
                    found.add(identifier)
        if not found:
            raise ValueError(f"runtime item catalog contains no item IDs: {path}")
        return found

    found: set[str] = set()
    in_items = False
    saw_item_heading = False
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if line.startswith("ALL RUNTIME ITEM REGISTRY IDS"):
            in_items = True
            saw_item_heading = True
            continue
        if line.startswith("ALL RUNTIME BLOCK REGISTRY IDS"):
            in_items = False
            if saw_item_heading:
                break
        if (in_items or not saw_item_heading) and RESOURCE_ID.fullmatch(line):
            found.add(line)
    if not found:
        raise ValueError(f"runtime item catalog contains no item IDs: {path}")
    return found


def source_registered_project_item_ids(path: Path) -> set[str]:
    """Return companion-mod item IDs that will exist after this deployment.

    The runtime export necessarily describes the currently installed JAR.  A
    pre-deployment validator must also recognize items registered by the new
    JAR being validated, otherwise adding a closed transitional item creates a
    chicken-and-egg failure: the safe deployment is rejected because the old
    runtime could not already contain the new item.  Keep this deliberately
    scoped to the companion mod's DeferredRegister calls rather than accepting
    arbitrary recipe identifiers.
    """

    if not path.is_file():
        raise ValueError(f"project item registration source does not exist: {path}")
    source = path.read_text(encoding="utf-8")
    names = set(
        re.findall(
            r'ITEMS\.(?:register|registerSimpleItem|registerSimpleBlockItem)\(\s*'
            r'"([a-z0-9_./-]+)"',
            source,
        )
    )
    if not names:
        raise ValueError(f"project item registration source contains no registrations: {path}")
    return {f"industrial_colonies:{name}" for name in names}


def class_string_constants(data: bytes) -> set[str]:
    """Read exact CONSTANT_String values from one Java class file."""

    view = memoryview(data)
    offset = 0

    def take(length: int) -> bytes:
        nonlocal offset
        if offset + length > len(view):
            raise ValueError("truncated Java class file")
        result = bytes(view[offset : offset + length])
        offset += length
        return result

    if int.from_bytes(take(4), "big") != 0xCAFEBABE:
        raise ValueError("IndustrialItems.class has invalid class-file magic")
    take(4)  # minor and major versions
    constant_pool_count = int.from_bytes(take(2), "big")
    utf8_values: dict[int, str] = {}
    string_references: list[int] = []
    index = 1
    while index < constant_pool_count:
        tag = take(1)[0]
        if tag == 1:  # CONSTANT_Utf8
            length = int.from_bytes(take(2), "big")
            utf8_values[index] = take(length).decode("utf-8", errors="replace")
        elif tag in {3, 4}:  # Integer / Float
            take(4)
        elif tag in {5, 6}:  # Long / Double consume two pool entries
            take(8)
            index += 1
        elif tag == 7:  # Class
            take(2)
        elif tag == 8:  # String
            string_references.append(int.from_bytes(take(2), "big"))
        elif tag in {9, 10, 11, 12, 17, 18}:  # refs / NameAndType / dynamic
            take(4)
        elif tag == 15:  # MethodHandle
            take(3)
        elif tag in {16, 19, 20}:  # MethodType / Module / Package
            take(2)
        else:
            raise ValueError(f"unsupported Java constant-pool tag {tag}")
        index += 1
    return {utf8_values[index] for index in string_references if index in utf8_values}


def candidate_jar_registered_project_item_ids(path: Path) -> set[str]:
    """Return item IDs corroborated by the exact deployment candidate JAR.

    A name must be a compiled String constant in IndustrialItems, have an item
    model in the same JAR, and have an item or block translation. This admits
    registered block items without trusting an arbitrary namespace output or
    a stray asset alone.
    """

    if not path.is_file():
        raise ValueError(f"candidate project JAR does not exist: {path}")
    class_entry = "dev/godpc/industrialcolonies/IndustrialItems.class"
    language_entry = "assets/industrial_colonies/lang/en_us.json"
    model_prefix = "assets/industrial_colonies/models/item/"
    try:
        with zipfile.ZipFile(path) as archive:
            archive_names = set(archive.namelist())
            if class_entry not in archive_names or language_entry not in archive_names:
                raise ValueError(
                    "candidate project JAR lacks IndustrialItems.class or en_us.json"
                )
            constants = class_string_constants(archive.read(class_entry))
            language = json.loads(archive.read(language_entry))
    except (OSError, KeyError, RuntimeError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        raise ValueError(f"cannot inspect candidate project JAR {path}: {error}") from error
    if not isinstance(language, dict):
        raise ValueError(f"candidate project JAR language file is not an object: {path}")

    model_names = {
        entry[len(model_prefix) : -len(".json")]
        for entry in archive_names
        if entry.startswith(model_prefix)
        and entry.endswith(".json")
        and "/" not in entry[len(model_prefix) : -len(".json")]
    }
    registration_names = {
        name
        for name in constants
        if re.fullmatch(r"[a-z0-9_./-]+", name)
        and name in model_names
        and (
            f"item.industrial_colonies.{name}" in language
            or f"block.industrial_colonies.{name}" in language
        )
    }
    if not registration_names:
        raise ValueError(
            f"candidate project JAR contains no corroborated IndustrialItems registrations: {path}"
        )
    return {f"industrial_colonies:{name}" for name in registration_names}


def slot_id(recipe: dict[str, Any], key: str) -> str | None:
    slot = recipe.get("slots", {}).get(key)
    return str(slot.get("id")) if isinstance(slot, dict) and slot.get("id") else None


def input_item_ids(recipe: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for key, value in recipe.get("slots", {}).items():
        if not isinstance(value, dict) or value.get("kind") != "ITEM":
            continue
        if key.startswith("in") or key in {
            "input",
            "base",
            "held",
            "ingredient",
            "template",
            "addition",
            "left",
            "right",
            "gas",
            "infusion",
        }:
            identifier = value.get("id")
            if identifier:
                result.add(str(identifier))
    return result


def output_item_ids(recipe: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for key, value in recipe.get("slots", {}).items():
        if not isinstance(value, dict) or value.get("kind") != "ITEM":
            continue
        if key.lower().startswith("output") or key in {"outItem", "extraOutput"}:
            identifier = value.get("id")
            if identifier:
                result.add(str(identifier))
    return result


def primary_managed_item(recipe: dict[str, Any]) -> str | None:
    """Return the one primary item output in a compiled KJSGen card."""

    slots = recipe.get("slots", {})
    if not isinstance(slots, dict):
        return None
    # Sequenced assembly uses output0; ordinary layouts use output. Emptying
    # calls its container result outItem. Do not consider extraOutput,
    # returned_tool, transitional, or later weighted/byproduct slots.
    for key in ("output", "output0", "outItem"):
        value = slots.get(key)
        if isinstance(value, dict) and value.get("kind") == "ITEM":
            identifier = str(value.get("id", "")).strip()
            if RESOURCE_ID.fullmatch(identifier):
                return identifier
    return None


def require_output(failures: list[str], recipe: dict[str, Any], expected: str) -> None:
    outputs = output_item_ids(recipe)
    if expected not in outputs:
        fail(
            failures,
            f"{recipe.get('recipeId')} does not produce its canonical output {expected}; "
            f"found {sorted(outputs)}",
        )


def require_exact_machine(
    failures: list[str], recipe: dict[str, Any], family: str, machine: str
) -> None:
    key = f"__machine_process_{family}"
    if slot_id(recipe, key) != machine:
        fail(failures, f"{recipe.get('recipeId')} is not bound to {machine} through {key}")


def require_sequence_operation_machine(
    failures: list[str], recipe: dict[str, Any], operation: str, machine: str
) -> None:
    params = recipe.get("params", {})
    try:
        length = int(params.get("__seqLen", "0"))
    except (TypeError, ValueError):
        length = 0
    if length <= 0:
        fail(failures, f"{recipe.get('recipeId')} has no sequence rows")
        return
    found_operation = False
    for index in range(length):
        if params.get(f"seq{index}") != operation:
            continue
        found_operation = True
        key = f"__machine_step_{index}_{operation}"
        if slot_id(recipe, key) != machine:
            fail(
                failures,
                f"{recipe.get('recipeId')} row {index} is not bound to {machine}",
            )
    if not found_operation:
        fail(failures, f"{recipe.get('recipeId')} has no {operation} sequence step")


def validate_critical_recipes(
    failures: list[str], recipes_by_id: dict[str, dict[str, Any]]
) -> None:
    """Preserve the accepted TFMG-first electronics invariants when present."""

    printed = recipes_by_id.get(PRINTED_SILICON_RECIPE)
    if printed:
        require_output(failures, printed, PRINTED_SILICON)
        require_exact_machine(failures, printed, "compacting", "createcasing:brass_press")
        if slot_id(printed, "in0") != "tfmg:silicon_ingot":
            fail(failures, "printed silicon does not explicitly start from TFMG silicon")
        if slot_id(printed, "in1") != "ae2:silicon_press":
            fail(failures, "printed silicon is missing its AE2 silicon mold input")
        if slot_id(printed, "returned_tool") != "ae2:silicon_press":
            fail(failures, "AE2 silicon mold is not returned by compacting")

    expected_outputs = {
        "industrial_colonies:manufacturing/copper_press": "createcasing:copper_press",
        "industrial_colonies:manufacturing/copper_deployer": "createcasing:copper_deployer",
        "industrial_colonies:manufacturing/brass_press": "createcasing:brass_press",
        "industrial_colonies:manufacturing/brass_deployer": "createcasing:brass_deployer",
        "industrial_colonies:electronics/coated_circuit_board": "tfmg:coated_circuit_board",
        "industrial_colonies:electronics/capacitor": "tfmg:capacitor_item",
        "industrial_colonies:electronics/transistor": "tfmg:transistor_item",
        "industrial_colonies:electronics/circuit_board": "tfmg:circuit_board",
        "industrial_colonies:electronics/voltmeter": "tfmg:voltmeter",
    }
    for recipe_id, output in expected_outputs.items():
        recipe = recipes_by_id.get(recipe_id)
        if recipe:
            require_output(failures, recipe, output)

    forbidden_machine_inputs = {
        "tfmg:capacitor_item",
        "tfmg:transistor_item",
        "tfmg:circuit_board",
        "tfmg:coated_circuit_board",
        "tfmg:etched_circuit_board",
        PRINTED_SILICON,
    }
    for recipe_id in (
        "industrial_colonies:manufacturing/copper_press",
        "industrial_colonies:manufacturing/copper_deployer",
    ):
        recipe = recipes_by_id.get(recipe_id)
        if not recipe:
            continue
        forbidden = sorted(input_item_ids(recipe) & forbidden_machine_inputs)
        if forbidden:
            fail(failures, f"{recipe_id} consumes downstream electronics: {forbidden}")

    upgrade_slots = {
        "industrial_colonies:manufacturing/copper_press": "create:mechanical_press",
        "industrial_colonies:manufacturing/copper_deployer": "create:deployer",
        "industrial_colonies:manufacturing/brass_press": "createcasing:copper_press",
        "industrial_colonies:manufacturing/brass_deployer": "createcasing:copper_deployer",
    }
    for recipe_id, base in upgrade_slots.items():
        recipe = recipes_by_id.get(recipe_id)
        if recipe and slot_id(recipe, "in4") != base:
            fail(failures, f"{recipe_id} is not an upgrade of {base} in center slot in4")

    coated = recipes_by_id.get("industrial_colonies:electronics/coated_circuit_board")
    if coated:
        require_exact_machine(failures, coated, "deploying", "createcasing:copper_deployer")
        if slot_id(coated, "input") != "tfmg:empty_circuit_board":
            fail(failures, "coated circuit board does not start from the TFMG empty board")

    sequence_expectations = {
        "industrial_colonies:electronics/capacitor": "tfmg:unfinished_capacitor",
        "industrial_colonies:electronics/transistor": "tfmg:unfinished_transistor",
        "industrial_colonies:electronics/circuit_board": "tfmg:unfinished_circuit_board",
    }
    for recipe_id, transitional in sequence_expectations.items():
        recipe = recipes_by_id.get(recipe_id)
        if not recipe:
            continue
        require_sequence_operation_machine(
            failures, recipe, "deploying", "createcasing:copper_deployer"
        )
        if slot_id(recipe, "transitional") != transitional:
            fail(failures, f"{recipe_id} uses the wrong transitional item")

    board = recipes_by_id.get("industrial_colonies:electronics/circuit_board")
    if board and board.get("params", {}).get("loops") != "4":
        fail(failures, "TFMG circuit board no longer preserves its original four-loop assembly")

    voltmeter = recipes_by_id.get("industrial_colonies:electronics/voltmeter")
    if voltmeter and "tfmg:copper_wire" not in input_item_ids(voltmeter):
        fail(failures, "TFMG voltmeter does not consume canonical TFMG copper wire")


def ids_from_metadata(value: Any, label: str, failures: list[str]) -> set[str]:
    """Read explicit missing-source exceptions, requiring a reason for objects."""

    if value is None:
        return set()
    if not isinstance(value, list):
        fail(failures, f"{label} must be an array")
        return set()
    result: set[str] = set()
    for index, entry in enumerate(value):
        if isinstance(entry, str):
            identifier = entry.strip()
        elif isinstance(entry, dict):
            identifier = str(entry.get("id", "")).strip()
            if not str(entry.get("reason", "")).strip():
                fail(failures, f"{label}[{index}] must give a nonblank reason")
        else:
            fail(failures, f"{label}[{index}] must be a recipe ID or metadata object")
            continue
        if not RESOURCE_ID.fullmatch(identifier):
            fail(failures, f"{label}[{index}] has invalid recipe ID {identifier!r}")
            continue
        if identifier in result:
            fail(failures, f"{label} repeats {identifier}")
        result.add(identifier)
    return result


def declared_missing_sources(data: dict[str, Any], failures: list[str]) -> set[str]:
    result = set(MISSING_SOURCE_ALLOWLIST)
    sources: list[tuple[str, dict[str, Any]]] = [("managed", data)]
    validation = data.get("validation")
    if isinstance(validation, dict):
        sources.append(("managed.validation", validation))
    if MANIFEST.is_file():
        try:
            manifest = read_json(MANIFEST)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            fail(failures, f"cannot read manifest removal metadata: {error}")
        else:
            sources.append(("manifest", manifest))
            validation = manifest.get("validation")
            if isinstance(validation, dict):
                sources.append(("manifest.validation", validation))

    keys = (
        "allowMissingRemovalIds",
        "conditionalRemovalIds",
        "allow_missing_removals",
        "conditional_removals",
    )
    for source_name, source in sources:
        for key in keys:
            if key in source:
                result.update(
                    ids_from_metadata(source[key], f"{source_name}.{key}", failures)
                )
    return result


def output_mismatch_exceptions(
    spec: dict[str, Any], label: str, failures: list[str]
) -> dict[str, str]:
    """Read precise, reasoned source-output parity exceptions from one recipe."""

    value = spec.get("remove_output_mismatch_exceptions", [])
    if not isinstance(value, list):
        fail(failures, f"{label}.remove_output_mismatch_exceptions must be an array")
        return {}
    result: dict[str, str] = {}
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            fail(
                failures,
                f"{label}.remove_output_mismatch_exceptions[{index}] must be an object "
                "with exact id and reason",
            )
            continue
        identifier = str(entry.get("id", "")).strip()
        reason = str(entry.get("reason", "")).strip()
        if not RESOURCE_ID.fullmatch(identifier):
            fail(
                failures,
                f"{label}.remove_output_mismatch_exceptions[{index}] has invalid id "
                f"{identifier!r}",
            )
            continue
        if not reason:
            fail(
                failures,
                f"{label}.remove_output_mismatch_exceptions[{index}] must give a "
                "nonblank reason",
            )
            continue
        if identifier in result:
            fail(
                failures,
                f"{label}.remove_output_mismatch_exceptions repeats {identifier}",
            )
        result[identifier] = reason
    return result


def manifest_replacement_removals(
    failures: list[str], warnings: list[str]
) -> dict[str, list[tuple[str, str | None]]]:
    """Map each recipe-owned source removal to managed recipe and opt-out reason.

    Top-level additional_removals are intentionally omitted: those are global
    retirement/loophole closures and need not have a one-for-one replacement.
    """

    if not MANIFEST.is_file():
        return {}
    try:
        manifest = read_json(MANIFEST)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        fail(failures, f"cannot read manifest replacement metadata: {error}")
        return {}

    specs: list[tuple[str, dict[str, Any]]] = []
    recipes = manifest.get("recipes", [])
    if not isinstance(recipes, list):
        fail(failures, "manifest recipes must be an array for removal-output validation")
        recipes = []
    for index, spec in enumerate(recipes):
        if not isinstance(spec, dict):
            fail(failures, f"manifest recipes[{index}] is not an object")
            continue
        recipe_id = str(spec.get("id", "")).strip()
        specs.append((recipe_id, spec))

    families = manifest.get("machine_families", [])
    if not isinstance(families, list):
        fail(failures, "manifest machine_families must be an array")
        families = []
    for family_index, family in enumerate(families):
        if not isinstance(family, dict):
            fail(failures, f"manifest machine_families[{family_index}] is not an object")
            continue
        tier = str(family.get("tier", "")).strip()
        entries = family.get("recipes", [])
        if not isinstance(entries, list):
            fail(failures, f"manifest machine family {tier!r} recipes must be an array")
            continue
        for entry_index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                fail(
                    failures,
                    f"manifest machine family {tier!r} recipe {entry_index} is not an object",
                )
                continue
            kind = str(entry.get("kind", "")).strip()
            recipe_id = str(
                entry.get("id", f"industrial_colonies:manufacturing/{tier}/{kind}")
            ).strip()
            specs.append((recipe_id, entry))

    result: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
    for recipe_id, spec in specs:
        if not RESOURCE_ID.fullmatch(recipe_id):
            fail(failures, f"manifest replacement recipe has invalid id {recipe_id!r}")
            continue
        removals = spec.get("remove", [])
        if not isinstance(removals, list):
            fail(failures, f"manifest recipe {recipe_id} remove must be an array")
            continue
        exceptions = output_mismatch_exceptions(spec, f"manifest recipe {recipe_id}", failures)
        removal_set: set[str] = set()
        for source in removals:
            source_id = str(source).strip()
            if not RESOURCE_ID.fullmatch(source_id):
                fail(failures, f"manifest recipe {recipe_id} has invalid remove ID {source_id!r}")
                continue
            if source_id in removal_set:
                fail(failures, f"manifest recipe {recipe_id} repeats remove ID {source_id}")
            removal_set.add(source_id)
            reason = exceptions.get(source_id)
            result[source_id].append((recipe_id, reason))
            if reason:
                warnings.append(
                    "LOUD OPT-OUT: removal output parity waived for "
                    f"{recipe_id} -> {source_id}: {reason}"
                )
        stale_exceptions = sorted(set(exceptions) - removal_set)
        if stale_exceptions:
            fail(
                failures,
                f"manifest recipe {recipe_id} has parity exceptions for IDs it does not "
                f"remove: {stale_exceptions}",
            )
    return dict(result)


def output_item_identifier(value: Any) -> str | None:
    """Read the first concrete item stack from an output field only."""

    if isinstance(value, str):
        return value if RESOURCE_ID.fullmatch(value) else None
    if isinstance(value, list):
        for entry in value:
            identifier = output_item_identifier(entry)
            if identifier:
                return identifier
        return None
    if not isinstance(value, dict):
        return None
    for key in ("id", "item"):
        identifier = value.get(key)
        if isinstance(identifier, str) and RESOURCE_ID.fullmatch(identifier):
            return identifier
    # A few serializers wrap a stack once more. Restrict recursion to
    # stack/result/output keys so tags or ingredient alternatives cannot be
    # mistaken for a produced item.
    for key in ("stack", "result", "output"):
        if key in value:
            identifier = output_item_identifier(value[key])
            if identifier:
                return identifier
    return None


def source_primary_item_outputs(value: Any) -> set[str]:
    """Extract type-aware primary outputs, including conditional branches.

    Only direct top-level result fields of the real recipe are considered.
    In particular, Create sequenced-assembly sequence-step results and later
    weighted results are deliberately ignored.
    """

    if not isinstance(value, dict):
        return set()
    recipe_type = str(value.get("type", ""))
    if recipe_type.endswith(":conditional"):
        branches: list[Any] = []
        recipes = value.get("recipes")
        if isinstance(recipes, list):
            for branch in recipes:
                if isinstance(branch, dict) and "recipe" in branch:
                    branches.append(branch["recipe"])
        recipe = value.get("recipe")
        if isinstance(recipe, dict):
            branches.append(recipe)
        result: set[str] = set()
        for branch in branches:
            result.update(source_primary_item_outputs(branch))
        return result

    # Singular fields represent the primary stack for vanilla, AE2,
    # Mekanism, ExtendedAE, and most custom serializers.
    for key in ("result", "output"):
        if key in value:
            identifier = output_item_identifier(value[key])
            if identifier:
                return {identifier}

    # Create processing and sequenced assembly expose a result list. The first
    # concrete stack is the primary output; later entries are weighted
    # byproducts/failure remnants, not equivalent recipe outputs.
    for key in ("results", "outputs"):
        if key in value:
            identifier = output_item_identifier(value[key])
            if identifier:
                return {identifier}
    return set()


def nested_output_contains(value: Any, item_id: str) -> bool:
    if isinstance(value, str):
        return value == item_id
    if isinstance(value, list):
        return any(nested_output_contains(entry, item_id) for entry in value)
    if not isinstance(value, dict):
        return False
    if value.get("id") == item_id or value.get("item") == item_id:
        return True
    return any(nested_output_contains(entry, item_id) for entry in value.values())


def recipe_outputs_item(value: Any, item_id: str) -> bool:
    """Find result/output fields, including recipes nested in condition wrappers."""

    if isinstance(value, list):
        return any(recipe_outputs_item(entry, item_id) for entry in value)
    if not isinstance(value, dict):
        return False
    for key, nested in value.items():
        if key in {"result", "results", "output", "outputs"} and nested_output_contains(
            nested, item_id
        ):
            return True
        if isinstance(nested, (dict, list)) and recipe_outputs_item(nested, item_id):
            return True
    return False


def inspect_installed_jars(
    mods: Path, failures: list[str], tracked_source_ids: set[str]
) -> tuple[
    dict[str, set[str]],
    set[str],
    set[str],
    dict[str, dict[str, set[str]]],
]:
    """Return recipe/layout evidence and primary outputs for tracked sources."""

    if not mods.is_dir():
        fail(failures, f"instance has no mods directory: {mods}")
        return {}, set(KJSGEN_BUILTINS), set(), {}
    jars = sorted(mods.glob("*.jar"), key=lambda path: path.name.lower())
    if not jars:
        fail(failures, f"instance has no installed mod JARs: {mods}")
        return {}, set(KJSGEN_BUILTINS), set(), {}

    recipe_sources: dict[str, set[str]] = defaultdict(set)
    supported_types = set(KJSGEN_BUILTINS)
    printed_silicon_sources: set[str] = set()
    primary_outputs: dict[str, dict[str, set[str]]] = defaultdict(dict)
    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as archive:
                for info in archive.infolist():
                    name = info.filename.replace("\\", "/")
                    recipe_match = RECIPE_ENTRY.fullmatch(name)
                    if recipe_match:
                        recipe_id = f"{recipe_match.group(1)}:{recipe_match.group(2)}"
                        recipe_sources[recipe_id].add(jar.name)
                        raw = archive.read(info)
                        silicon_candidate = PRINTED_SILICON.encode("utf-8") in raw
                        if recipe_id not in tracked_source_ids and not silicon_candidate:
                            continue
                        try:
                            recipe_data = json.loads(raw)
                        except (UnicodeDecodeError, json.JSONDecodeError) as error:
                            fail(
                                failures,
                                f"cannot parse tracked source recipe {recipe_id} "
                                f"from {jar.name}: {error}",
                            )
                            continue
                        if recipe_id in tracked_source_ids:
                            primary_outputs[recipe_id][jar.name] = source_primary_item_outputs(
                                recipe_data
                            )
                        if silicon_candidate:
                            try:
                                if recipe_outputs_item(recipe_data, PRINTED_SILICON):
                                    printed_silicon_sources.add(recipe_id)
                            except (TypeError, ValueError) as error:
                                fail(
                                    failures,
                                    f"cannot inspect silicon-candidate recipe {recipe_id} "
                                    f"from {jar.name}: {error}",
                                )
                        continue
                    if not LAYOUT_ENTRY.fullmatch(name):
                        continue
                    try:
                        layout = json.loads(archive.read(info))
                    except (UnicodeDecodeError, json.JSONDecodeError) as error:
                        fail(failures, f"cannot parse KJSGen layout {name} in {jar.name}: {error}")
                        continue
                    layout_id = layout.get("id") if isinstance(layout, dict) else None
                    if isinstance(layout_id, str) and RESOURCE_ID.fullmatch(layout_id):
                        supported_types.add(layout_id)
                    else:
                        fail(failures, f"KJSGen layout {name} in {jar.name} has no valid id")
        except (OSError, zipfile.BadZipFile, RuntimeError) as error:
            fail(failures, f"cannot inspect installed mod JAR {jar.name}: {error}")
    return (
        dict(recipe_sources),
        supported_types,
        printed_silicon_sources,
        {recipe_id: dict(by_jar) for recipe_id, by_jar in primary_outputs.items()},
    )


def validate_uids(
    failures: list[str], entries: Iterable[dict[str, Any]], retired: Iterable[Any]
) -> None:
    active: list[str] = []
    for entry in entries:
        uid = str(entry.get("uid", "")).strip()
        active.append(uid)
        try:
            uuid.UUID(uid)
        except (ValueError, AttributeError):
            fail(failures, f"{entry.get('recipeId', '<unknown>')} has invalid UID {uid!r}")
    if len(active) != len(set(active)):
        fail(failures, "managed recipe/removal UIDs are duplicated")
    if LEGACY_TRANSISTOR_UID in active:
        fail(failures, "the live-deleted legacy transistor card is still managed")

    retired_ids = [str(value).strip() for value in retired]
    if len(retired_ids) != len(set(retired_ids)):
        fail(failures, "retired managed UIDs are duplicated")
    for uid in retired_ids:
        try:
            uuid.UUID(uid)
        except (ValueError, AttributeError):
            fail(failures, f"retired managed UID is invalid: {uid!r}")
        if uid in active:
            fail(failures, f"retired UID is still actively managed: {uid}")


def validate_recipe_slots(
    failures: list[str],
    recipes: Iterable[dict[str, Any]],
    registry: set[str],
) -> None:
    """Validate compiled KJSGen slots against exact registry evidence."""

    for recipe in recipes:
        recipe_id = str(recipe.get("recipeId", ""))
        if recipe.get("replaceRecipe", True):
            fail(failures, f"{recipe_id} still requests broad output replacement")
        slots = recipe.get("slots")
        if not isinstance(slots, dict):
            fail(failures, f"{recipe_id} has no slot object")
            continue
        for key, value in slots.items():
            if not isinstance(value, dict):
                fail(failures, f"{recipe_id} slot {key} is not an object")
                continue
            kind = value.get("kind")
            identifier = str(value.get("id", "")).strip()
            if kind not in VALID_SLOT_KINDS:
                fail(failures, f"{recipe_id} slot {key} has unsupported kind {kind!r}")
            if not RESOURCE_ID.fullmatch(identifier):
                fail(failures, f"{recipe_id} slot {key} has invalid ID {identifier!r}")
            if kind == "ITEM" and identifier not in registry:
                fail(failures, f"unregistered item in {recipe_id} {key}: {identifier}")
            if key.startswith("__machine_"):
                if kind != "ITEM":
                    fail(failures, f"{recipe_id} hidden machine selector {key} is not an item")
                if not (
                    key.startswith("__machine_process_")
                    or re.fullmatch(r"__machine_step_\d+_[a-z0-9_]+", key)
                ):
                    fail(failures, f"{recipe_id} has malformed hidden machine selector {key}")
            for number_key in ("count", "amount"):
                number = value.get(number_key)
                if number is not None and (
                    not isinstance(number, int) or isinstance(number, bool) or number <= 0
                ):
                    fail(
                        failures,
                        f"{recipe_id} slot {key} has invalid {number_key} {number!r}",
                    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path, help="Minecraft instance directory")
    parser.add_argument("--catalog", type=Path, required=True, help="Runtime item catalog")
    parser.add_argument(
        "--project-jar",
        type=Path,
        help=(
            "Exact deployment candidate JAR used as authoritative evidence for newly "
            "registered Industrial Colonies item and block-item IDs"
        ),
    )
    args = parser.parse_args()

    try:
        data = read_json(MANAGED)
        registry = catalog_item_ids(args.catalog.resolve())
        if args.project_jar:
            project_registry = candidate_jar_registered_project_item_ids(
                args.project_jar.resolve()
            )
            project_registry_source = "candidate JAR"
        else:
            project_registry = source_registered_project_item_ids(PROJECT_ITEMS_SOURCE)
            project_registry_source = "registration source"
        registry.update(project_registry)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: cannot load validation inputs: {error}", file=sys.stderr)
        return 1

    failures: list[str] = []
    warnings: list[str] = []
    recipes_value = data.get("recipes", [])
    removals_value = data.get("removals", [])
    if not isinstance(recipes_value, list) or not isinstance(removals_value, list):
        print("FAIL: managed recipes and removals must be arrays", file=sys.stderr)
        return 1
    recipes = [entry for entry in recipes_value if isinstance(entry, dict)]
    removals = [entry for entry in removals_value if isinstance(entry, dict)]
    if len(recipes) != len(recipes_value):
        fail(failures, "managed recipes contains non-object entries")
    if len(removals) != len(removals_value):
        fail(failures, "managed removals contains non-object entries")

    recipe_ids = [str(recipe.get("recipeId", "")).strip() for recipe in recipes]
    removal_ids = [str(removal.get("recipeId", "")).strip() for removal in removals]
    for label, identifiers in (("recipe", recipe_ids), ("removal", removal_ids)):
        if len(identifiers) != len(set(identifiers)):
            fail(failures, f"managed {label} IDs are not unique")
        for identifier in identifiers:
            if not RESOURCE_ID.fullmatch(identifier):
                fail(failures, f"managed {label} ID is invalid: {identifier!r}")
    overlap = sorted(set(recipe_ids) & set(removal_ids))
    if overlap:
        fail(failures, f"IDs occur as both managed recipes and removals: {overlap}")

    retired_recipe_uids = data.get("retiredRecipeUids", [])
    retired_removal_uids = data.get("retiredRemovalUids", [])
    if not isinstance(retired_recipe_uids, list) or not isinstance(retired_removal_uids, list):
        fail(failures, "retiredRecipeUids and retiredRemovalUids must be arrays")
        retired_recipe_uids = []
        retired_removal_uids = []
    validate_uids(
        failures,
        [*recipes, *removals],
        [*retired_recipe_uids, *retired_removal_uids],
    )

    validate_recipe_slots(failures, recipes, registry)

    for removal in removals:
        recipe_id = str(removal.get("recipeId", ""))
        for field in ("output", "input", "mod"):
            value = removal.get(field, "")
            if value is not None and str(value).strip():
                fail(failures, f"{recipe_id} mixes broad {field} and exact recipe-ID removal")

    replacement_removals = manifest_replacement_removals(failures, warnings)
    recipe_sources, supported_types, silicon_sources, source_primary_outputs = (
        inspect_installed_jars(
            args.instance.resolve() / "mods", failures, set(removal_ids)
        )
    )
    for recipe in recipes:
        recipe_type = str(recipe.get("type", "")).strip()
        if recipe_type not in supported_types:
            fail(
                failures,
                f"{recipe.get('recipeId')} uses unavailable KJSGen type {recipe_type!r}",
            )

    missing_source_exceptions = declared_missing_sources(data, failures)
    undeclared_exceptions = sorted(missing_source_exceptions - set(removal_ids))
    if undeclared_exceptions:
        fail(
            failures,
            f"missing-source metadata names recipes that are not managed removals: "
            f"{undeclared_exceptions}",
        )
    for source_id in removal_ids:
        if source_id not in recipe_sources and source_id not in missing_source_exceptions:
            fail(
                failures,
                f"installed source recipe is absent from every mod JAR: {source_id}; "
                "declare a reasoned conditional-removal exception if intentional",
            )

    recipes_by_id = {identifier: recipe for identifier, recipe in zip(recipe_ids, recipes)}
    validate_critical_recipes(failures, recipes_by_id)

    # Recipe-owned removals are replacements, so each removed source must have
    # exactly the new card's primary item output. This is deliberately stricter
    # than catalog reference roles: Create's weighted sequenced-assembly
    # byproducts (for example cogwheels and shafts from a failed precision
    # mechanism) must never make an unrelated recipe look replaceable.
    for source_id, owners in sorted(replacement_removals.items()):
        if source_id not in recipe_sources:
            # The exact-source check above already handles absent conditional
            # recipes and its explicit future-proof exception metadata.
            continue
        definitions = source_primary_outputs.get(source_id, {})
        for managed_id, opt_out_reason in owners:
            if opt_out_reason:
                continue
            managed_recipe = recipes_by_id.get(managed_id)
            if not managed_recipe:
                fail(
                    failures,
                    f"manifest replacement recipe is absent from compiled KJSGen data: "
                    f"{managed_id}",
                )
                continue
            expected = primary_managed_item(managed_recipe)
            if not expected:
                fail(
                    failures,
                    f"manifest replacement recipe {managed_id} has no exact primary item output",
                )
                continue
            for jar_name in sorted(recipe_sources[source_id]):
                actual = definitions.get(jar_name)
                if not actual:
                    fail(
                        failures,
                        f"cannot determine type-aware primary item output for source "
                        f"{source_id} in {jar_name} (replacement {managed_id} expects {expected})",
                    )
                elif actual != {expected}:
                    fail(
                        failures,
                        f"source-output mismatch: {managed_id} produces {expected}, but removed "
                        f"{source_id} in {jar_name} primarily produces {sorted(actual)}",
                    )

    # A canonical TFMG-silicon recipe is only meaningful if every installed
    # static producer of AE2 printed silicon is removed. This catches the AE2
    # Inscriber/Create Applied Kinetics shared ID and ExtendedAE's circuit cutter.
    if PRINTED_SILICON_RECIPE in recipes_by_id:
        managed_silicon_producers = {
            recipe_id
            for recipe_id, recipe in recipes_by_id.items()
            if PRINTED_SILICON in output_item_ids(recipe)
        }
        if managed_silicon_producers != {PRINTED_SILICON_RECIPE}:
            fail(
                failures,
                f"managed printed-silicon producers bypass the canonical recipe: "
                f"{sorted(managed_silicon_producers)}",
            )
        unremoved = sorted(silicon_sources - set(removal_ids))
        if unremoved:
            provenance = {
                recipe_id: sorted(recipe_sources.get(recipe_id, set())) for recipe_id in unremoved
            }
            fail(
                failures,
                f"installed printed-silicon bypass recipes are not removed: {provenance}",
            )

    print(
        f"Checked {len(recipes)} visual recipes, {len(removals)} exact removals, "
        f"{len(registry)} runtime/deployment item IDs "
        f"({len(project_registry)} project-owned from {project_registry_source}), "
        f"{len(recipe_sources)} installed recipe IDs, "
        f"and {len(supported_types)} KJSGen recipe types."
    )
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if failures:
        print(f"FAIL: {len(failures)} managed-recipe issue(s)", file=sys.stderr)
        for issue in failures:
            print(f"  {issue}", file=sys.stderr)
        return 1
    print("PASS: managed recipes are exact-ID, registry-valid, and layout-supported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
