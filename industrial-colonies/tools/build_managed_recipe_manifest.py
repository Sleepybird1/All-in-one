#!/usr/bin/env python3
"""Assemble the editable Industrial Colonies managed-recipe manifest.

The seed file contains the hand-authored recipes and progression policy.  This
tool fills the remaining assigned item unlocks from the installed pack's static
recipe catalog.  It deliberately emits exact recipe-id removals only; broad
output/mod/input removals do not belong in generated progression data.

Auto policy used by the seed::

    "auto_policy": {
      "mechanical_from_phase": "Digital",
      "phase_gates": {
        "Digital": ["industrial_colonies:digital_gate"],
        "Nuclear": ["industrial_colonies:nuclear_gate", "#c:plates/lead"]
      }
    }

At and after ``mechanical_from_phase``, the most recent gate definition is
cycled clockwise around a 5x5 outer ring.  The original recipe occupies the
center 3x3.  A gate item is never gated by itself.  A normal shaped recipe is
padded to 3x3 before that threshold.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import zipfile
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
DEFAULT_DEPENDENCIES = PROJECT / "tools/machine_recipe_dependencies.json"
DEFAULT_OUTPUT = PROJECT / "progression/managed_recipe_overhaul.json"
DEFAULT_REPORT = PROJECT / "progression/managed_recipe_overhaul.report.json"
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
CRAFTING_TYPES = (
    "minecraft:crafting_shaped",
    "mekanism:mek_data",
    "minecraft:crafting_shapeless",
    "create:mechanical_crafting",
)
SHAPED_TYPES = {"minecraft:crafting_shaped", "mekanism:mek_data"}
CONDITIONAL_TYPES = {"forge:conditional", "neoforge:conditional"}
BAD_SOURCE_MARKERS = (
    "_alt",
    "/alt",
    "_clean",
    "/clean",
    "_upgrade",
    "/upgrade",
    "_from_",
    "/from_",
    "conversion",
    "decraft",
    "recolor",
    "recycling",
    "reverse",
    "unpack",
)
RING_POSITIONS = tuple(
    [(0, column) for column in range(5)]
    + [(row, 4) for row in range(1, 5)]
    + [(4, column) for column in range(3, -1, -1)]
    + [(row, 0) for row in range(3, 0, -1)]
)
SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@$%^&*?+="
DEFAULT_RESTORATION_REASON_COUNTS = {
    "restore_default_recipe": 146,
    "default_recipe": 14,
}
DEFAULT_RESTORATION_RECIPE_COUNT = 160
DEFAULT_RESTORATION_REMOVAL_COUNT = 178


class ManifestBuildError(RuntimeError):
    """A malformed or ambiguous input that must not be silently guessed."""

    def __init__(self, message: str, report: dict[str, Any] | None = None):
        super().__init__(message)
        self.report = report


class UnsupportedStockRecipe(ValueError):
    """A valid stock recipe that the editable KJSGen schema cannot preserve."""


@dataclass(frozen=True)
class CatalogRow:
    recipe_id: str
    recipe_type: str
    source_jar: str
    source_path: str


@dataclass(frozen=True)
class ParsedRecipe:
    source: CatalogRow
    recipe_type: str
    output_id: str
    output_count: int
    output_components: str = ""
    pattern: tuple[str, ...] = ()
    key: tuple[tuple[str, str], ...] = ()
    inputs: tuple[str, ...] = ()

    def signature(self) -> tuple[Any, ...]:
        return (
            self.recipe_type,
            self.output_id,
            self.output_count,
            self.output_components,
            self.pattern,
            self.key,
            self.inputs,
        )


def load_object(path: Path, label: str) -> OrderedDict[str, Any]:
    try:
        with path.open(encoding="utf-8-sig") as handle:
            value = json.load(handle, object_pairs_hook=OrderedDict)
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestBuildError(f"cannot read {label} {path}: {error}") from error
    if not isinstance(value, dict):
        raise ManifestBuildError(f"{label} {path} must contain a JSON object")
    return value


def file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    except OSError as error:
        raise ManifestBuildError(f"cannot hash {path}: {error}") from error


def load_default_restoration_policy(
    seed: Mapping[str, Any],
) -> tuple[Path | None, OrderedDict[str, Any] | None]:
    reference = seed.get("default_restoration_policy")
    if reference is None:
        return None, None
    if not isinstance(reference, str) or not reference.strip():
        raise ManifestBuildError("default_restoration_policy must be a nonblank path")
    candidate = (PROJECT / reference).resolve()
    try:
        candidate.relative_to(PROJECT.resolve())
    except ValueError as error:
        raise ManifestBuildError(
            "default_restoration_policy must resolve inside the project"
        ) from error
    if not candidate.is_file():
        raise ManifestBuildError(f"default restoration policy does not exist: {candidate}")
    return candidate, load_object(candidate, "default restoration policy")


def normalize_default_restoration_policy(
    policy_path: Path | None,
    policy: Mapping[str, Any] | None,
) -> OrderedDict[str, Any]:
    empty: OrderedDict[str, Any] = OrderedDict(
        (
            ("active", False),
            ("path", None),
            ("sha256", None),
            ("recipe_ids", []),
            ("outputs", []),
            ("removal_ids", []),
            ("entries", []),
            ("reason_counts", OrderedDict()),
        )
    )
    if policy_path is None or policy is None:
        return empty
    if policy.get("schemaVersion") != 1:
        raise ManifestBuildError("default restoration policy must use schemaVersion 1")
    if policy.get("policy") != "active_reviewed_default_restoration":
        raise ManifestBuildError("unexpected default restoration policy name")
    entries = require_array(policy.get("entries"), "default restoration entries")
    recipe_ids: list[str] = []
    outputs: list[str] = []
    removal_ids: list[str] = []
    reason_counts: dict[str, int] = defaultdict(int)
    normalized_entries: list[OrderedDict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ManifestBuildError(f"default restoration entry {index} must be an object")
        recipe_id = require_resource_id(
            entry.get("recipeId"), f"default restoration entry {index} recipeId"
        )
        uid = entry.get("uid")
        if not isinstance(uid, str) or not uid.strip():
            raise ManifestBuildError(f"default restoration entry {recipe_id} has invalid uid")
        reason = entry.get("reason")
        if reason not in DEFAULT_RESTORATION_REASON_COUNTS:
            raise ManifestBuildError(
                f"default restoration entry {recipe_id} has unsupported reason {reason!r}"
            )
        if entry.get("status") != "rejected":
            raise ManifestBuildError(
                f"default restoration entry {recipe_id} must have rejected status"
            )
        card_hash = entry.get("cardSha256")
        if not isinstance(card_hash, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", card_hash):
            raise ManifestBuildError(
                f"default restoration entry {recipe_id} has invalid cardSha256"
            )
        entry_outputs = unique_resource_array(
            entry.get("outputs"), f"default restoration entry {recipe_id} outputs"
        )
        if len(entry_outputs) != 1:
            raise ManifestBuildError(
                f"default restoration entry {recipe_id} must have exactly one item output"
            )
        owned_removals = require_array(
            entry.get("ownedRemovals"),
            f"default restoration entry {recipe_id} ownedRemovals",
        )
        normalized_removals: list[OrderedDict[str, str]] = []
        for removal_index, removal in enumerate(owned_removals):
            if not isinstance(removal, dict):
                raise ManifestBuildError(
                    f"default restoration entry {recipe_id} removal {removal_index} must be an object"
                )
            removal_id = require_resource_id(
                removal.get("recipeId"),
                f"default restoration entry {recipe_id} removal {removal_index} recipeId",
            )
            removal_uid = removal.get("uid")
            if not isinstance(removal_uid, str) or not removal_uid.strip():
                raise ManifestBuildError(
                    f"default restoration entry {recipe_id} removal {removal_id} has invalid uid"
                )
            normalized_removals.append(
                OrderedDict((("recipeId", removal_id), ("uid", removal_uid)))
            )
            removal_ids.append(removal_id)
        recipe_ids.append(recipe_id)
        outputs.extend(entry_outputs)
        reason_counts[reason] += 1
        normalized_entries.append(
            OrderedDict(
                (
                    ("recipeId", recipe_id),
                    ("uid", uid),
                    ("status", "rejected"),
                    ("reason", reason),
                    ("cardSha256", card_hash),
                    ("outputs", entry_outputs),
                    ("ownedRemovals", normalized_removals),
                )
            )
        )
    if len(entries) != DEFAULT_RESTORATION_RECIPE_COUNT:
        raise ManifestBuildError(
            "default restoration policy must contain exactly "
            f"{DEFAULT_RESTORATION_RECIPE_COUNT} entries, found {len(entries)}"
        )
    duplicates = sorted(item for item in set(recipe_ids) if recipe_ids.count(item) > 1)
    if duplicates:
        raise ManifestBuildError(f"default restoration recipe IDs are duplicated: {duplicates}")
    duplicate_outputs = sorted(item for item in set(outputs) if outputs.count(item) > 1)
    if duplicate_outputs:
        raise ManifestBuildError(f"default restoration outputs are duplicated: {duplicate_outputs}")
    duplicate_removals = sorted(
        item for item in set(removal_ids) if removal_ids.count(item) > 1
    )
    if duplicate_removals:
        raise ManifestBuildError(
            "default restoration removals require an explicit shared-owner resolution: "
            f"{duplicate_removals}"
        )
    resolutions = require_array(
        policy.get("sharedRemovalResolutions", []), "sharedRemovalResolutions"
    )
    if resolutions:
        raise ManifestBuildError(
            "default restoration shared-removal resolutions are unsupported; resolve ownership first"
        )
    actual_reasons = {reason: reason_counts.get(reason, 0) for reason in DEFAULT_RESTORATION_REASON_COUNTS}
    if actual_reasons != DEFAULT_RESTORATION_REASON_COUNTS:
        raise ManifestBuildError(
            f"default restoration reason counts drifted: {actual_reasons}"
        )
    if len(removal_ids) != DEFAULT_RESTORATION_REMOVAL_COUNT:
        raise ManifestBuildError(
            "default restoration policy must own exactly "
            f"{DEFAULT_RESTORATION_REMOVAL_COUNT} removals, found {len(removal_ids)}"
        )
    normalized_entries.sort(key=lambda entry: entry["recipeId"])
    return OrderedDict(
        (
            ("active", True),
            ("path", policy_path.relative_to(PROJECT).as_posix()),
            ("sha256", file_sha256(policy_path)),
            ("recipe_ids", sorted(recipe_ids)),
            ("outputs", sorted(outputs)),
            ("removal_ids", sorted(removal_ids)),
            ("entries", normalized_entries),
            ("reason_counts", OrderedDict(sorted(actual_reasons.items()))),
        )
    )


def require_array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ManifestBuildError(f"{label} must be an array")
    return value


def require_resource_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not RESOURCE_ID.fullmatch(value):
        raise ManifestBuildError(f"{label} must be an exact resource ID, got {value!r}")
    return value


def unique_resource_array(value: Any, label: str) -> list[str]:
    result = [require_resource_id(entry, f"{label} entry") for entry in require_array(value, label)]
    duplicates = sorted(item for item in set(result) if result.count(item) > 1)
    if duplicates:
        raise ManifestBuildError(f"{label} contains duplicates: {duplicates}")
    return result


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def encoded_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def parse_gradle_properties(path: Path) -> dict[str, str]:
    properties: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as error:
        raise ManifestBuildError(f"cannot read {path}: {error}") from error
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "!")):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        properties[key.strip()] = value.strip()
    return properties


def default_catalog() -> Path:
    candidates = (
        PROJECT.parents[1] / "outputs/recipe-catalog-current",
        PROJECT.parent / "outputs/recipe-catalog-current",
        PROJECT / "../outputs/recipe-catalog-current",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    return candidates[0].resolve()


def default_mods() -> Path:
    properties = parse_gradle_properties(PROJECT / "gradle.properties")
    value = properties.get("pack_mods_dir")
    if not value:
        raise ManifestBuildError("gradle.properties is missing pack_mods_dir")
    return Path(value).expanduser().resolve()


class Catalog:
    def __init__(self, directory: Path):
        self.directory = directory
        recipes_path = directory / "recipes.csv"
        refs_path = directory / "recipe_refs.csv"
        if not recipes_path.is_file() or not refs_path.is_file():
            raise ManifestBuildError(
                f"catalog {directory} must contain recipes.csv and recipe_refs.csv"
            )
        self.rows_by_source: dict[tuple[str, str], list[CatalogRow]] = defaultdict(list)
        self.producers: dict[str, set[tuple[str, str]]] = defaultdict(set)
        with recipes_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"recipe_id", "recipe_type", "source_jar", "source_path"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ManifestBuildError(f"{recipes_path} is missing columns {sorted(required)}")
            for line, raw in enumerate(reader, 2):
                recipe_id = require_resource_id(raw["recipe_id"], f"{recipes_path}:{line} recipe_id")
                recipe_type = str(raw["recipe_type"]).strip()
                # Some data generators serialize the literal fallback type
                # ``recipe``.  It is not selectable for auto conversion, but it
                # is still valid catalog evidence for exact producer removal.
                if not recipe_type or any(character.isspace() for character in recipe_type):
                    raise ManifestBuildError(
                        f"{recipes_path}:{line} has invalid recipe_type {recipe_type!r}"
                    )
                source_jar = str(raw["source_jar"]).strip()
                source_path = str(raw["source_path"]).strip()
                if not source_jar or not source_path:
                    raise ManifestBuildError(f"{recipes_path}:{line} has a blank source location")
                row = CatalogRow(recipe_id, recipe_type, source_jar, source_path)
                self.rows_by_source[(recipe_id, source_jar)].append(row)
        for source, rows in self.rows_by_source.items():
            locations = {(row.recipe_type, row.source_path) for row in rows}
            if len(locations) != len(rows):
                raise ManifestBuildError(f"catalog duplicates recipe source rows for {source}")

        with refs_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"recipe_id", "source_jar", "role", "kind", "resource_id"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ManifestBuildError(f"{refs_path} is missing columns {sorted(required)}")
            for line, raw in enumerate(reader, 2):
                if raw["role"] != "output" or raw["kind"] != "item":
                    continue
                output = require_resource_id(
                    raw["resource_id"], f"{refs_path}:{line} output resource_id"
                )
                recipe_id = require_resource_id(
                    raw["recipe_id"], f"{refs_path}:{line} recipe_id"
                )
                source = (recipe_id, str(raw["source_jar"]).strip())
                if source not in self.rows_by_source:
                    raise ManifestBuildError(
                        f"{refs_path}:{line} references missing recipes.csv source {source}"
                    )
                self.producers[output].add(source)

    def producer_ids(self, output: str) -> list[str]:
        return sorted({recipe_id for recipe_id, _jar in self.producers.get(output, set())})

    def candidate_rows(self, output: str) -> list[CatalogRow]:
        result: list[CatalogRow] = []
        for source in sorted(self.producers.get(output, set())):
            result.extend(self.rows_by_source[source])
        return sorted(result, key=lambda row: (row.recipe_id, row.source_jar, row.source_path))


class JarRecipes:
    def __init__(self, mods: Path):
        if not mods.is_dir():
            raise ManifestBuildError(f"mods directory does not exist: {mods}")
        self.mods = mods
        self.by_name: dict[str, Path] = {}
        for path in sorted(mods.iterdir(), key=lambda value: value.name.lower()):
            if path.is_file() and path.suffix.lower() == ".jar":
                lowered = path.name.lower()
                if lowered in self.by_name:
                    raise ManifestBuildError(
                        f"mods directory contains case-colliding JAR names: {path.name}"
                    )
                self.by_name[lowered] = path
        self.cache: dict[tuple[str, str], OrderedDict[str, Any]] = {}

    def is_installed(self, row: CatalogRow) -> bool:
        return row.source_jar.lower() in self.by_name

    def load(self, row: CatalogRow) -> OrderedDict[str, Any]:
        key = (row.source_jar.lower(), row.source_path)
        if key in self.cache:
            return copy.deepcopy(self.cache[key])
        jar = self.by_name.get(row.source_jar.lower())
        if jar is None:
            raise ManifestBuildError(
                f"catalog source JAR is not installed in {self.mods}: {row.source_jar}"
            )
        try:
            with zipfile.ZipFile(jar) as archive:
                raw = archive.read(row.source_path)
            value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=OrderedDict)
        except (OSError, KeyError, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile) as error:
            raise ManifestBuildError(
                f"cannot load {row.recipe_id} from {jar.name}!/{row.source_path}: {error}"
            ) from error
        if not isinstance(value, dict):
            raise ManifestBuildError(f"{row.recipe_id} recipe JSON must be an object")
        self.cache[key] = value
        return copy.deepcopy(value)


def conditional_variants(recipe: Mapping[str, Any], source: str) -> Iterable[Mapping[str, Any]]:
    recipe_type = recipe.get("type")
    if recipe_type not in CONDITIONAL_TYPES:
        yield recipe
        return
    entries = recipe.get("recipes")
    if not isinstance(entries, list) or not entries:
        raise ManifestBuildError(f"conditional recipe {source} has no recipes array")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("recipe"), dict):
            raise ManifestBuildError(
                f"conditional recipe {source} entry {index} has no recipe object"
            )
        yield from conditional_variants(entry["recipe"], f"{source}#{index}")


def primary_output_id(value: Any) -> str | None:
    """Extract one item ID from a result/output stack without reading nested recipe steps."""
    if isinstance(value, str):
        return value if RESOURCE_ID.fullmatch(value) else None
    if not isinstance(value, dict):
        return None
    identifier = value.get("id")
    if isinstance(identifier, str) and RESOURCE_ID.fullmatch(identifier):
        return identifier
    item = value.get("item")
    if isinstance(item, str) and RESOURCE_ID.fullmatch(item):
        return item
    if isinstance(item, dict):
        return primary_output_id(item)
    return None


def primary_outputs(recipe: Mapping[str, Any], source: str) -> tuple[bool, set[str]]:
    """Return whether a recipe schema was classified and its primary item outputs.

    Create/TFMG ``results`` arrays put the principal result first and later
    entries are probabilistic byproducts.  Those later values must not cause a
    recipe removal for the byproduct item.  AE2 storage-cell disassembly is a
    deliberately multi-return salvage recipe with no singular primary output,
    so it is classified as non-primary for this purpose.
    """
    recipe_type = recipe.get("type")
    if recipe_type in CONDITIONAL_TYPES:
        entries = recipe.get("recipes")
        if not isinstance(entries, list) or not entries:
            raise ManifestBuildError(f"conditional recipe {source} has no recipes array")
        outputs: set[str] = set()
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or not isinstance(entry.get("recipe"), dict):
                raise ManifestBuildError(
                    f"conditional recipe {source} entry {index} has no recipe object"
                )
            classified, nested = primary_outputs(entry["recipe"], f"{source}#{index}")
            if not classified:
                return False, set()
            outputs.update(nested)
        return True, outputs
    if recipe_type == "ae2:storage_cell_disassembly":
        return True, set()
    for field in ("result", "output", "item_output"):
        if field in recipe:
            identifier = primary_output_id(recipe[field])
            return (identifier is not None), ({identifier} if identifier else set())
    for field in ("results", "outputs"):
        if field in recipe:
            values = recipe[field]
            if not isinstance(values, list) or not values:
                return False, set()
            identifier = primary_output_id(values[0])
            return (identifier is not None), ({identifier} if identifier else set())
    return False, set()


def classify_primary_producers(
    output: str,
    rows: Sequence[CatalogRow],
    jars: JarRecipes,
) -> tuple[list[CatalogRow], list[OrderedDict[str, Any]]]:
    producers: list[CatalogRow] = []
    audit: list[OrderedDict[str, Any]] = []
    seen_sources: set[tuple[str, str, str]] = set()
    for row in rows:
        source_key = (row.recipe_id, row.source_jar, row.source_path)
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        if not jars.is_installed(row):
            audit.append(
                OrderedDict(
                    (
                        ("output", output),
                        ("recipe_id", row.recipe_id),
                        ("source_jar", row.source_jar),
                        ("status", "uninstalled_catalog_source"),
                    )
                )
            )
            continue
        raw = jars.load(row)
        classified, primary = primary_outputs(raw, row.recipe_id)
        if not classified:
            raise ManifestBuildError(
                f"cannot classify primary output for catalog producer reference "
                f"{output} <- {row.recipe_id} ({raw.get('type')!r}, fields={sorted(raw)})"
            )
        if output in primary:
            producers.append(row)
        else:
            audit.append(
                OrderedDict(
                    (
                        ("output", output),
                        ("recipe_id", row.recipe_id),
                        ("source_jar", row.source_jar),
                        ("status", "non_primary_catalog_reference"),
                        ("primary_outputs", sorted(primary)),
                    )
                )
            )
    producers.sort(key=lambda row: (row.recipe_id, row.source_jar, row.source_path))
    audit.sort(key=lambda entry: (entry["output"], entry["recipe_id"], entry["source_jar"]))
    return producers, audit


def parse_slot(value: Any, label: str) -> str:
    if isinstance(value, list):
        if not value:
            raise UnsupportedStockRecipe(f"{label} uses an empty ingredient alternative")
        choices = {parse_slot(entry, f"{label} alternative") for entry in value}
        if len(choices) != 1:
            raise UnsupportedStockRecipe(
                f"{label} has alternatives that KJSGen cannot preserve: {sorted(choices)}"
            )
        return next(iter(choices))
    if isinstance(value, str):
        slot = value.strip()
        if slot.startswith("#"):
            require_resource_id(slot[1:], label)
        else:
            require_resource_id(slot, label)
        return slot
    if not isinstance(value, dict):
        raise ManifestBuildError(f"{label} ingredient must be a string/object/array")
    meaningful_extra = set(value) - {"item", "tag"}
    if meaningful_extra:
        raise UnsupportedStockRecipe(
            f"{label} uses unsupported ingredient fields {sorted(meaningful_extra)}"
        )
    has_item = "item" in value
    has_tag = "tag" in value
    if has_item == has_tag:
        raise ManifestBuildError(f"{label} ingredient must contain exactly one of item/tag")
    if has_item:
        return require_resource_id(value["item"], f"{label} item")
    return "#" + require_resource_id(value["tag"], f"{label} tag")


def parse_seed_slot(value: Any, label: str) -> str:
    """Normalize either a stock ingredient object or compiler slot object."""
    if isinstance(value, dict) and ("kind" in value or "id" in value):
        extras = set(value) - {"kind", "id"}
        if extras:
            raise ManifestBuildError(f"{label} uses unsupported slot fields {sorted(extras)}")
        kind = str(value.get("kind", "ITEM")).upper()
        identifier = require_resource_id(value.get("id"), f"{label} id")
        if kind == "ITEM":
            return identifier
        if kind == "ITEM_TAG":
            return "#" + identifier
        raise ManifestBuildError(f"{label} must be an ITEM or ITEM_TAG slot, got {kind!r}")
    return parse_slot(value, label)


def component_string(value: Any, label: str) -> str:
    """Render a 1.21 result component patch as deterministic item syntax."""
    if not isinstance(value, dict) or not value:
        raise UnsupportedStockRecipe(f"{label} components must be a nonempty object")
    entries: list[str] = []

    def validate_data(data: Any, path: str) -> None:
        if isinstance(data, bool) or data is None:
            raise UnsupportedStockRecipe(f"{path} uses unsupported null/boolean data")
        if isinstance(data, float) and not math.isfinite(data):
            raise UnsupportedStockRecipe(f"{path} uses a non-finite number")
        if isinstance(data, (str, int, float)):
            return
        if isinstance(data, list):
            for index, child in enumerate(data):
                validate_data(child, f"{path}[{index}]")
            return
        if isinstance(data, dict):
            for key, child in data.items():
                if not isinstance(key, str):
                    raise UnsupportedStockRecipe(f"{path} contains a non-string object key")
                validate_data(child, f"{path}.{key}")
            return
        raise UnsupportedStockRecipe(f"{path} uses unsupported data type")

    for component_id in sorted(value):
        require_resource_id(component_id, f"{label} component ID")
        component_value = value[component_id]
        validate_data(component_value, f"{label} component {component_id}")
        try:
            encoded = json.dumps(
                component_value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
        except (TypeError, ValueError) as error:
            raise UnsupportedStockRecipe(
                f"{label} component {component_id} cannot be encoded losslessly: {error}"
            ) from error
        entries.append(f"{component_id}={encoded}")
    return "[" + ",".join(entries) + "]"


def parse_result(value: Any, label: str) -> tuple[str, int, str]:
    if isinstance(value, str):
        return require_resource_id(value, label), 1, ""
    if not isinstance(value, dict):
        raise ManifestBuildError(f"{label} result must be a string or object")
    identifier = value.get("id", value.get("item"))
    if identifier is None or ("id" in value and "item" in value):
        raise ManifestBuildError(f"{label} result must contain exactly one id/item")
    extras = set(value) - {"id", "item", "count", "components"}
    if extras:
        raise UnsupportedStockRecipe(
            f"{label} result uses unsupported component fields {sorted(extras)}"
        )
    output = require_resource_id(identifier, f"{label} result ID")
    count = value.get("count", 1)
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise ManifestBuildError(f"{label} result count must be a positive integer")
    components = component_string(value["components"], label) if "components" in value else ""
    return output, count, components


def apply_replacement(slot: str, replacements: Mapping[str, str]) -> str:
    visited: list[str] = []
    while slot in replacements:
        if slot in visited:
            raise ManifestBuildError(
                f"ingredient_replacements contains a cycle: {' -> '.join(visited + [slot])}"
            )
        visited.append(slot)
        slot = replacements[slot]
    return slot


def parse_recipe_variant(
    row: CatalogRow,
    raw: Mapping[str, Any],
    wanted_output: str,
    replacements: Mapping[str, str],
) -> ParsedRecipe | None:
    recipe_type = raw.get("type")
    if recipe_type not in CRAFTING_TYPES:
        return None
    output, count, components = parse_result(raw.get("result"), row.recipe_id)
    if output != wanted_output:
        return None
    if recipe_type in SHAPED_TYPES | {"create:mechanical_crafting"}:
        pattern_value = raw.get("pattern")
        key_value = raw.get("key")
        if not isinstance(pattern_value, list) or not pattern_value:
            raise ManifestBuildError(f"{row.recipe_id} has no shaped pattern")
        if not isinstance(key_value, dict):
            raise ManifestBuildError(f"{row.recipe_id} has no shaped key object")
        if any(not isinstance(line, str) or not line for line in pattern_value):
            raise ManifestBuildError(f"{row.recipe_id} pattern rows must be nonblank strings")
        width = len(pattern_value[0])
        if any(len(line) != width for line in pattern_value):
            raise ManifestBuildError(f"{row.recipe_id} pattern is ragged")
        size_limit = 3 if recipe_type in SHAPED_TYPES else 9
        if width > size_limit or len(pattern_value) > size_limit:
            raise ManifestBuildError(f"{row.recipe_id} pattern exceeds {size_limit}x{size_limit}")
        used = {character for line in pattern_value for character in line if character != " "}
        if used != set(key_value):
            raise ManifestBuildError(
                f"{row.recipe_id} key mismatch; missing={sorted(used - set(key_value))}, "
                f"unused={sorted(set(key_value) - used)}"
            )
        key: list[tuple[str, str]] = []
        for character in sorted(used):
            if len(character) != 1 or character == " ":
                raise ManifestBuildError(f"{row.recipe_id} has invalid key symbol {character!r}")
            ingredient = parse_slot(key_value[character], f"{row.recipe_id} key {character}")
            key.append((character, apply_replacement(ingredient, replacements)))
        return ParsedRecipe(
            row,
            recipe_type,
            output,
            count,
            components,
            tuple(pattern_value),
            tuple(key),
        )
    ingredients = raw.get("ingredients")
    if not isinstance(ingredients, list) or not ingredients or len(ingredients) > 9:
        raise ManifestBuildError(f"{row.recipe_id} shapeless recipe requires 1-9 ingredients")
    parsed = tuple(
        apply_replacement(parse_slot(value, f"{row.recipe_id} ingredient {index}"), replacements)
        for index, value in enumerate(ingredients)
    )
    return ParsedRecipe(row, recipe_type, output, count, components, inputs=parsed)


def candidate_quality(candidate: ParsedRecipe) -> tuple[int, int, int]:
    output_namespace, output_path = candidate.output_id.split(":", 1)
    recipe_namespace, recipe_path = candidate.source.recipe_id.split(":", 1)
    basename = output_path.rsplit("/", 1)[-1]
    exact_path = recipe_path == output_path or recipe_path.rsplit("/", 1)[-1] == basename
    clean = not any(marker in recipe_path.lower() for marker in BAD_SOURCE_MARKERS)
    return int(exact_path), int(clean), int(recipe_namespace == output_namespace)


def choose_stock_recipe(
    output: str,
    rows: Sequence[CatalogRow],
    jars: JarRecipes,
    replacements: Mapping[str, str],
    override: str | None = None,
) -> tuple[ParsedRecipe | None, list[dict[str, str]]]:
    candidates: list[ParsedRecipe] = []
    unsupported: list[dict[str, str]] = []
    for row in rows:
        raw = jars.load(row)
        variants = list(conditional_variants(raw, row.recipe_id))
        for index, variant in enumerate(variants):
            try:
                parsed = parse_recipe_variant(row, variant, output, replacements)
            except UnsupportedStockRecipe as error:
                unsupported.append(
                    OrderedDict(
                        (("recipe_id", row.recipe_id), ("variant", str(index)), ("reason", str(error)))
                    )
                )
                continue
            if parsed is not None:
                candidates.append(parsed)
    if not candidates:
        return None, unsupported
    if override is not None:
        candidates = [candidate for candidate in candidates if candidate.source.recipe_id == override]
        if not candidates:
            return None, unsupported
        signatures = {candidate.signature() for candidate in candidates}
        if len(signatures) > 1:
            raise ManifestBuildError(
                f"source override {override} has conflicting installed definitions for {output}"
            )
        return min(
            candidates,
            key=lambda candidate: (
                candidate.source.source_jar,
                candidate.source.source_path,
            ),
        ), unsupported
    priority = {
        "minecraft:crafting_shaped": 0,
        "mekanism:mek_data": 0,
        "minecraft:crafting_shapeless": 1,
        "create:mechanical_crafting": 2,
    }
    best_type_priority = min(priority[candidate.recipe_type] for candidate in candidates)
    candidates = [
        candidate
        for candidate in candidates
        if priority[candidate.recipe_type] == best_type_priority
    ]
    best_quality = max(candidate_quality(candidate) for candidate in candidates)
    candidates = [candidate for candidate in candidates if candidate_quality(candidate) == best_quality]
    signatures = {candidate.signature() for candidate in candidates}
    if len(signatures) > 1:
        choices = sorted({candidate.source.recipe_id for candidate in candidates})
        raise ManifestBuildError(
            f"ambiguous stock crafting sources for {output}: {choices}; "
            "make the output explicit, user-owned, or excluded"
        )
    return min(
        candidates,
        key=lambda candidate: (
            candidate.source.recipe_id,
            candidate.source.source_jar,
            candidate.source.source_path,
        ),
    ), unsupported


def output_slot(identifier: str, count: int, components: str = "") -> str | OrderedDict[str, Any]:
    if components:
        result: OrderedDict[str, Any] = OrderedDict((("kind", "ITEM"), ("id", identifier)))
        if count != 1:
            result["count"] = count
        result["components"] = components
        return result
    return identifier if count == 1 else f"{count}x {identifier}"


def exact_slot_item(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        counted = re.fullmatch(r"\d+x\s+(.+)", stripped)
        if counted:
            stripped = counted.group(1)
        return stripped if RESOURCE_ID.fullmatch(stripped) else None
    if isinstance(value, dict):
        kind = str(value.get("kind", "ITEM")).upper()
        identifier = value.get("id")
        if kind == "ITEM" and isinstance(identifier, str) and RESOURCE_ID.fullmatch(identifier):
            return identifier
    return None


def stock_ingredients(candidate: ParsedRecipe) -> list[str]:
    if candidate.inputs:
        return list(candidate.inputs)
    key = dict(candidate.key)
    return [key[character] for line in candidate.pattern for character in line if character != " "]


def pad_shaped(pattern: Sequence[str]) -> list[str]:
    if len(pattern) > 3 or max(len(line) for line in pattern) > 3:
        raise UnsupportedStockRecipe("stock shaped recipe cannot fit in the preserved 3x3 grid")
    width = max(len(line) for line in pattern)
    result = [line.ljust(3) for line in pattern]
    result.extend([" " * 3] * (3 - len(result)))
    if width > 3:
        raise AssertionError("width validation failed")
    return result


def canonical_grid(cells: Mapping[tuple[int, int], str], size: int) -> tuple[list[str], OrderedDict[str, str]]:
    values: OrderedDict[str, str] = OrderedDict()
    for row in range(size):
        for column in range(size):
            value = cells.get((row, column))
            if value is not None and value not in values:
                values[value] = ""
    if len(values) > len(SYMBOLS):
        raise ManifestBuildError("generated mechanical recipe exhausts safe key symbols")
    for symbol, value in zip(SYMBOLS, list(values)):
        values[value] = symbol
    pattern = [
        "".join(values[cells[(row, column)]] if (row, column) in cells else " " for column in range(size))
        for row in range(size)
    ]
    key = OrderedDict((symbol, value) for value, symbol in values.items())
    return pattern, key


def gated_mechanical(candidate: ParsedRecipe, gates: Sequence[str]) -> tuple[list[str], OrderedDict[str, str]]:
    if not gates or len(gates) > 16:
        raise ManifestBuildError("phase gate arrays must contain 1-16 slot values")
    cells: dict[tuple[int, int], str] = {}
    if candidate.inputs:
        for index, value in enumerate(candidate.inputs):
            cells[(1 + index // 3, 1 + index % 3)] = value
    else:
        if len(candidate.pattern) > 3 or max(len(line) for line in candidate.pattern) > 3:
            raise UnsupportedStockRecipe(
                "stock mechanical pattern is larger than 3x3, so a complete 5x5 gate ring cannot be added"
            )
        key = dict(candidate.key)
        top = 1 + (3 - len(candidate.pattern)) // 2
        left = 1 + (3 - max(len(line) for line in candidate.pattern)) // 2
        for row, line in enumerate(candidate.pattern):
            for column, character in enumerate(line):
                if character != " ":
                    cells[(top + row, left + column)] = key[character]
    for index, position in enumerate(RING_POSITIONS):
        if position in cells:
            raise UnsupportedStockRecipe("stock recipe occupies a required 5x5 gate-ring cell")
        cells[position] = gates[index % len(gates)]
    return canonical_grid(cells, 5)


def ungated_mechanical(candidate: ParsedRecipe) -> tuple[list[str], OrderedDict[str, str]]:
    if candidate.inputs:
        cells = {(index // 3, index % 3): value for index, value in enumerate(candidate.inputs)}
        return canonical_grid(cells, 3)
    return list(candidate.pattern), OrderedDict(candidate.key)


def make_auto_recipe(
    candidate: ParsedRecipe,
    phase: str,
    gates: Sequence[str] | None,
) -> tuple[OrderedDict[str, Any], bool]:
    output = output_slot(
        candidate.output_id, candidate.output_count, candidate.output_components
    )
    recipe_id = f"industrial_colonies:auto/{candidate.output_id.replace(':', '/', 1)}"
    spec: OrderedDict[str, Any] = OrderedDict()
    spec["id"] = recipe_id
    spec["phase"] = phase
    spec["order"] = 5000
    gated = gates is not None
    if gated:
        pattern, key = gated_mechanical(candidate, gates)
        spec["type"] = "mechanical_crafting"
        spec["comment"] = (
            f"Industrial 5x5 rebuild of {candidate.output_id} from stock recipe "
            f"{candidate.source.recipe_id}"
        )
        spec["pattern"] = pattern
        spec["key"] = key
    elif candidate.recipe_type == "minecraft:crafting_shapeless":
        spec["type"] = "shapeless"
        spec["comment"] = f"Editable stock-derived recipe from {candidate.source.recipe_id}"
        spec["inputs"] = list(candidate.inputs)
    elif candidate.recipe_type in SHAPED_TYPES:
        spec["type"] = "shaped"
        spec["comment"] = f"Editable stock-derived recipe from {candidate.source.recipe_id}"
        spec["pattern"] = pad_shaped(candidate.pattern)
        spec["key"] = OrderedDict(candidate.key)
    else:
        pattern, key = ungated_mechanical(candidate)
        spec["type"] = "mechanical_crafting"
        spec["comment"] = f"Editable stock-derived recipe from {candidate.source.recipe_id}"
        spec["pattern"] = pattern
        spec["key"] = key
    spec["output"] = output
    return spec, gated


def extract_recipe_outputs(spec: Mapping[str, Any], label: str) -> list[str]:
    values: list[Any] = []
    if "output" in spec:
        values.append(spec["output"])
    if "outputs" in spec:
        values.extend(require_array(spec["outputs"], f"{label} outputs"))
    if "results" in spec:
        values.extend(require_array(spec["results"], f"{label} results"))
    outputs = [item for item in (exact_slot_item(value) for value in values) if item]
    if not outputs:
        raise ManifestBuildError(f"{label} has no exact item output")
    return outputs


def extract_recipe_ingredients(spec: Mapping[str, Any]) -> set[str]:
    values: list[Any] = []
    key = spec.get("key")
    if isinstance(key, dict):
        values.extend(key.values())
    inputs = spec.get("inputs")
    if isinstance(inputs, list):
        values.extend(inputs)
    ingredients = spec.get("ingredients")
    if isinstance(ingredients, list):
        values.extend(ingredients)
    for field in (
        "input",
        "held",
        "base",
        "fluid",
        "left",
        "right",
        "input1",
        "input2",
        "gas",
        "infusion",
    ):
        if field in spec:
            values.append(spec[field])
    steps = spec.get("steps")
    if isinstance(steps, list):
        for step in steps:
            if isinstance(step, dict):
                for field in ("ingredient", "fluid"):
                    if field in step:
                        values.append(step[field])
    return {item for item in (exact_slot_item(value) for value in values) if item}


def authored_dependency_ids(spec: Mapping[str, Any]) -> set[str]:
    values = spec.get("depends_on", [])
    return {
        require_resource_id(value, f"{spec.get('id')} depends_on")
        for value in require_array(values, f"{spec.get('id')} depends_on")
    }


def machine_family_recipe_id(family: Mapping[str, Any], entry: Mapping[str, Any]) -> str:
    explicit = entry.get("id")
    if explicit is not None:
        return require_resource_id(explicit, "machine family recipe id")
    tier = family.get("tier")
    kind = entry.get("kind")
    if not isinstance(tier, str) or not isinstance(kind, str):
        raise ManifestBuildError("machine family recipe is missing tier/kind identity")
    return f"industrial_colonies:manufacturing/{tier}/{kind}"


def deduplicate_exact_removals(
    recipes: Sequence[dict[str, Any]],
    machine_families: Sequence[dict[str, Any]],
    additional: Sequence[str],
    phase_index: Mapping[str, int],
) -> tuple[list[str], list[OrderedDict[str, str]]]:
    """Give every exact removal one deterministic manifest owner.

    Ownership order exactly mirrors compiler expansion order so validator and
    compiled KJSGen removal arrays remain byte-for-byte predictable.
    """
    owners: list[tuple[tuple[int, int, str], dict[str, Any], str, bool]] = []
    for spec in recipes:
        identity = require_resource_id(spec.get("id"), "managed recipe id")
        phase = spec.get("phase")
        owners.append(
            (
                (phase_index[str(phase)], int(spec.get("order", 999)), identity),
                spec,
                identity,
                False,
            )
        )
    for family in machine_families:
        phase = family.get("phase")
        for entry in require_array(family.get("recipes"), "machine family recipes"):
            identity = machine_family_recipe_id(family, entry)
            owners.append(((phase_index[str(phase)], 999, identity), entry, identity, True))
    owners.sort(key=lambda record: record[0])
    claimed: dict[str, str] = {}
    audit: list[OrderedDict[str, str]] = []
    for _sort_key, owner, identity, is_family in owners:
        values = unique_resource_array(owner.get("remove", []), f"{identity} remove")
        kept: list[str] = []
        for removal in values:
            previous = claimed.get(removal)
            if previous is None:
                claimed[removal] = identity
                kept.append(removal)
            else:
                audit.append(
                    OrderedDict(
                        (
                            ("recipe_id", removal),
                            ("owner", previous),
                            ("deduplicated_from", identity),
                        )
                    )
                )
        owner["remove"] = kept
        if is_family and not kept:
            raise ManifestBuildError(
                f"machine family recipe {identity} lost every removal to another owner"
            )
        if not kept and owner.get("exclusive_output") is True:
            owner.pop("exclusive_output", None)
            owner["allow_stock_alternative"] = True
    remaining_additional: list[str] = []
    for removal in unique_resource_array(list(additional), "additional_removals"):
        previous = claimed.get(removal)
        if previous is None:
            claimed[removal] = "additional_removals"
            remaining_additional.append(removal)
        else:
            audit.append(
                OrderedDict(
                    (
                        ("recipe_id", removal),
                        ("owner", previous),
                        ("deduplicated_from", "additional_removals"),
                    )
                )
            )
    return remaining_additional, audit


def parse_assignments(data: Mapping[str, Any]) -> tuple[OrderedDict[str, str], dict[str, str]]:
    nodes = data.get("nodes")
    if not isinstance(nodes, dict):
        raise ManifestBuildError("machine_node_assignments.json must contain a nodes object")
    output_to_node: OrderedDict[str, str] = OrderedDict()
    unlock_types: dict[str, str] = {}
    for node, entry in nodes.items():
        if not isinstance(node, str) or not node.strip() or not isinstance(entry, dict):
            raise ManifestBuildError("assignment nodes must map nonblank names to objects")
        unlocks = require_array(entry.get("unlocks", []), f"assignment node {node} unlocks")
        type_map = entry.get("unlock_types", {})
        if not isinstance(type_map, dict):
            raise ManifestBuildError(f"assignment node {node} unlock_types must be an object")
        validated_unlocks = [
            require_resource_id(output, f"assignment node {node} unlock") for output in unlocks
        ]
        if len(validated_unlocks) != len(set(validated_unlocks)):
            raise ManifestBuildError(f"assignment node {node} contains duplicate unlock IDs")
        for identifier in validated_unlocks:
            previous = output_to_node.get(identifier)
            if previous is not None and previous != node:
                raise ManifestBuildError(
                    f"assigned output {identifier} occurs in both {previous!r} and {node!r}"
                )
            output_to_node[identifier] = node
            kind = str(type_map.get(identifier, "item"))
            if kind not in {"item", "vanilla_item", "block", "fluid", "chemical"}:
                raise ManifestBuildError(
                    f"assignment {node} gives {identifier} unknown unlock type {kind!r}"
                )
            unlock_types[identifier] = kind
        unknown_typed = sorted(set(type_map) - set(validated_unlocks))
        if unknown_typed:
            raise ManifestBuildError(
                f"assignment node {node} types non-unlocked outputs: {unknown_typed}"
            )
    return output_to_node, unlock_types


def parse_dependencies(data: Mapping[str, Any], assignments: Mapping[str, str]) -> dict[str, dict[str, Any]]:
    entries = require_array(data.get("recipes"), "machine recipe dependencies recipes")
    result: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ManifestBuildError(f"dependency recipe {index} must be an object")
        output = require_resource_id(entry.get("output"), f"dependency recipe {index} output")
        if output in result:
            raise ManifestBuildError(f"duplicate dependency recipe output {output}")
        node = entry.get("node")
        if not isinstance(node, str) or not node.strip():
            raise ManifestBuildError(f"dependency recipe {output} has no node")
        assigned = assignments.get(output)
        if assigned is not None and assigned != node:
            raise ManifestBuildError(
                f"dependency recipe {output} names node {node!r}, assignment uses {assigned!r}"
            )
        ingredients = unique_resource_array(
            entry.get("ingredients", []), f"dependency recipe {output} ingredients"
        )
        tags = require_array(entry.get("foundational_tags", []), f"dependency recipe {output} tags")
        for tag in tags:
            if not isinstance(tag, str) or not tag.startswith("#"):
                raise ManifestBuildError(f"dependency recipe {output} has invalid tag {tag!r}")
            require_resource_id(tag[1:], f"dependency recipe {output} tag")
        result[output] = {"node": node, "ingredients": ingredients, "foundational_tags": tags}
    return result


def normalize_replacements(value: Any) -> OrderedDict[str, str]:
    if not isinstance(value, dict):
        raise ManifestBuildError("ingredient_replacements must be an object")
    result: OrderedDict[str, str] = OrderedDict()
    for source, target in value.items():
        source_slot = parse_seed_slot(source, "ingredient replacement source")
        target_slot = parse_seed_slot(target, f"ingredient replacement {source}")
        result[source_slot] = target_slot
    for source in result:
        apply_replacement(source, result)
    return result


def normalize_source_overrides(value: Any) -> OrderedDict[str, str]:
    if not isinstance(value, dict):
        raise ManifestBuildError("source_recipe_overrides must be an object")
    result: OrderedDict[str, str] = OrderedDict()
    for output, recipe_id in sorted(value.items()):
        exact_output = require_resource_id(output, "source recipe override output")
        exact_recipe = require_resource_id(
            recipe_id, f"source recipe override for {exact_output}"
        )
        result[exact_output] = exact_recipe
    return result


def normalize_policy(
    seed: Mapping[str, Any], phase_order: Sequence[str]
) -> tuple[int | None, OrderedDict[int, list[str]], set[str]]:
    policy = seed.get("auto_policy", {})
    if not isinstance(policy, dict):
        raise ManifestBuildError("auto_policy must be an object")
    mechanical_from = policy.get("mechanical_from_phase")
    threshold: int | None = None
    if mechanical_from is not None:
        if mechanical_from not in phase_order:
            raise ManifestBuildError(
                f"auto_policy mechanical_from_phase is unknown: {mechanical_from!r}"
            )
        threshold = phase_order.index(mechanical_from)
    raw_gates = policy.get("phase_gates", {})
    if not isinstance(raw_gates, dict):
        raise ManifestBuildError("auto_policy phase_gates must be an object")
    gates: OrderedDict[int, list[str]] = OrderedDict()
    exact_gate_items: set[str] = set()
    for phase, values in raw_gates.items():
        if phase not in phase_order:
            raise ManifestBuildError(f"phase_gates references unknown phase {phase!r}")
        slots = [
            parse_seed_slot(value, f"phase_gates {phase}")
            for value in require_array(values, f"phase_gates {phase}")
        ]
        if not slots or len(slots) > 16:
            raise ManifestBuildError(f"phase_gates {phase} must contain 1-16 slots")
        gates[phase_order.index(phase)] = slots
        exact_gate_items.update(slot for slot in slots if RESOURCE_ID.fullmatch(slot))
    return threshold, OrderedDict(sorted(gates.items())), exact_gate_items


def normalize_machine_families(value: Any, phase_index: Mapping[str, int]) -> list[dict[str, Any]]:
    families = copy.deepcopy(require_array(value, "seed machine_families"))
    normalized: list[dict[str, Any]] = []
    stock_kind = {
        "fan": "encased_fan",
        "saw": "saw",
        "roller": "roller",
        "automatic_clutch": "auto_clutch",
    }
    output_suffix = {
        "fan": "encased_fan",
        "saw": "mechanical_saw",
        "roller": "mechanical_roller",
    }
    for index, family in enumerate(families):
        if not isinstance(family, dict):
            raise ManifestBuildError(f"machine family {index} must be an object")
        tier = family.get("tier")
        if not isinstance(tier, str) or not re.fullmatch(r"[a-z0-9_]+", tier):
            raise ManifestBuildError(f"machine family {index} has invalid tier {tier!r}")
        if family.get("phase") not in phase_index:
            raise ManifestBuildError(
                f"machine family {index} uses unknown phase {family.get('phase')!r}"
            )
        explicit = family.get("recipes", [])
        if not isinstance(explicit, list):
            raise ManifestBuildError(f"machine family {tier} recipes must be an array")
        explicit_by_kind: OrderedDict[str, dict[str, Any]] = OrderedDict()
        for entry_index, entry in enumerate(explicit):
            if not isinstance(entry, dict):
                raise ManifestBuildError(
                    f"machine family {tier} recipe {entry_index} must be an object"
                )
            kind = entry.get("kind")
            if not isinstance(kind, str) or not kind:
                raise ManifestBuildError(
                    f"machine family {tier} recipe {entry_index} has no kind"
                )
            if kind in explicit_by_kind:
                raise ManifestBuildError(f"machine family {tier} repeats explicit kind {kind}")
            explicit_by_kind[kind] = entry

        generated: OrderedDict[str, dict[str, Any]] = OrderedDict()
        kinds = family.get("kinds", [])
        if not isinstance(kinds, list):
            raise ManifestBuildError(f"machine family {tier} kinds must be an array")
        for kind in kinds:
            if not isinstance(kind, str) or not re.fullmatch(r"[a-z0-9_]+", kind):
                raise ManifestBuildError(f"machine family {tier} has invalid kind {kind!r}")
            if kind in generated:
                raise ManifestBuildError(f"machine family {tier} repeats kind {kind}")
            generated[kind] = OrderedDict(
                (
                    ("kind", kind),
                    ("output", f"createcasing:{tier}_{output_suffix.get(kind, kind)}"),
                    (
                        "remove",
                        [f"createcasing:crafting/{stock_kind.get(kind, kind)}/{tier}"],
                    ),
                )
            )
        for kind, entry in explicit_by_kind.items():
            generated[kind] = entry
        if not generated:
            raise ManifestBuildError(
                f"machine family {tier} must define at least one kind or explicit recipe"
            )
        family.pop("kinds", None)
        family["recipes"] = list(generated.values())
        normalized.append(family)
    return normalized


def active_gates(
    phase_index: int,
    threshold: int | None,
    gates: Mapping[int, list[str]],
    output: str,
    exact_gate_items: set[str],
) -> list[str] | None:
    if threshold is None or phase_index < threshold or output in exact_gate_items:
        return None
    applicable = [index for index in gates if threshold <= index <= phase_index]
    return list(gates[max(applicable)]) if applicable else None


def add_fatal(report: dict[str, Any], code: str, message: str, **details: Any) -> None:
    entry: OrderedDict[str, Any] = OrderedDict((('code', code), ('message', message)))
    for key in sorted(details):
        entry[key] = details[key]
    report.setdefault("fatal_errors", []).append(entry)
    report["status"] = "failed"


def build_manifest(
    seed_path: Path,
    assignments_path: Path,
    dependencies_path: Path,
    catalog_path: Path,
    mods_path: Path,
) -> tuple[OrderedDict[str, Any], OrderedDict[str, Any]]:
    report: OrderedDict[str, Any] = OrderedDict(
        (
            ("schema_version", 1),
            ("status", "building"),
            ("generated", []),
            ("skipped", []),
            ("ignored", []),
            ("source_choices", []),
            ("producer_classification", []),
            ("preserved_removals", []),
            ("disabled_recipes", []),
            ("removal_deduplications", []),
            ("fatal_errors", []),
        )
    )
    try:
        seed = load_object(seed_path, "seed")
        assignments_data = load_object(assignments_path, "assignments")
        dependencies_data = load_object(dependencies_path, "dependencies")
        if seed.get("schema_version") != 1:
            raise ManifestBuildError("managed recipe seed must use schema_version 1")
        restoration_path, restoration_policy = load_default_restoration_policy(seed)
        restoration = normalize_default_restoration_policy(
            restoration_path, restoration_policy
        )
        restoration_recipe_ids = set(restoration["recipe_ids"])
        restoration_outputs = set(restoration["outputs"])
        restoration_removal_ids = set(restoration["removal_ids"])
        project = seed.get("project", "default")
        if not isinstance(project, str) or not project.strip():
            raise ManifestBuildError("seed project must be a nonblank string")
        phase_order = require_array(seed.get("phase_order"), "seed phase_order")
        if not phase_order or any(not isinstance(phase, str) or not phase.strip() for phase in phase_order):
            raise ManifestBuildError("seed phase_order must contain nonblank strings")
        if len(phase_order) != len(set(phase_order)):
            raise ManifestBuildError("seed phase_order contains duplicates")
        phase_index = {phase: index for index, phase in enumerate(phase_order)}
        output_to_node, unlock_types = parse_assignments(assignments_data)
        dependencies = parse_dependencies(dependencies_data, output_to_node)
        preserved_recipe_ids = set(
            unique_resource_array(seed.get("preserve_recipe_ids", []), "preserve_recipe_ids")
        )
        phase_by_node = seed.get("phase_by_node")
        if not isinstance(phase_by_node, dict):
            raise ManifestBuildError("seed phase_by_node must be an object")
        assignment_nodes = set(assignments_data["nodes"])
        for node, phase in phase_by_node.items():
            if node not in assignment_nodes:
                raise ManifestBuildError(f"phase_by_node references unknown node {node!r}")
            if phase not in phase_index:
                raise ManifestBuildError(f"phase_by_node {node!r} references unknown phase {phase!r}")

        all_explicit = copy.deepcopy(require_array(seed.get("recipes", []), "seed recipes"))
        disabled_recipe_ids = set(
            unique_resource_array(
                seed.get("disabled_recipe_ids", []), "disabled_recipe_ids"
            )
        )
        all_explicit_ids: set[str] = set()
        for index, spec in enumerate(all_explicit):
            if not isinstance(spec, dict):
                raise ManifestBuildError(f"seed recipe {index} must be an object")
            recipe_id = require_resource_id(spec.get("id"), f"seed recipe {index} id")
            if recipe_id in all_explicit_ids:
                raise ManifestBuildError(f"duplicate seed recipe id {recipe_id}")
            all_explicit_ids.add(recipe_id)
        unknown_disabled = sorted(disabled_recipe_ids - all_explicit_ids)
        if unknown_disabled:
            raise ManifestBuildError(
                "disabled_recipe_ids references unknown seed recipes: "
                f"{unknown_disabled}"
            )
        explicit = [
            spec for spec in all_explicit if spec["id"] not in disabled_recipe_ids
        ]
        report["disabled_recipes"] = sorted(disabled_recipe_ids)
        machine_families = normalize_machine_families(
            seed.get("machine_families", []), phase_index
        )
        explicit_ids: set[str] = set()
        explicit_outputs: set[str] = set()
        for index, spec in enumerate(explicit):
            if not isinstance(spec, dict):
                raise ManifestBuildError(f"seed recipe {index} must be an object")
            recipe_id = require_resource_id(spec.get("id"), f"seed recipe {index} id")
            if recipe_id in explicit_ids:
                raise ManifestBuildError(f"duplicate seed recipe id {recipe_id}")
            explicit_ids.add(recipe_id)
            if spec.get("phase") not in phase_index:
                raise ManifestBuildError(f"seed recipe {recipe_id} uses unknown phase {spec.get('phase')!r}")
            for output in extract_recipe_outputs(spec, f"seed recipe {recipe_id}"):
                if output in explicit_outputs:
                    raise ManifestBuildError(f"multiple explicit recipes manage output {output}")
                explicit_outputs.add(output)

        if restoration["active"]:
            explicit_by_id = {str(spec["id"]): spec for spec in explicit}
            missing_restorations = sorted(restoration_recipe_ids - set(explicit_by_id))
            if missing_restorations:
                raise ManifestBuildError(
                    "default restoration policy references inactive or missing seed recipes: "
                    f"{missing_restorations}"
                )
            for entry in restoration["entries"]:
                recipe_id = entry["recipeId"]
                spec = explicit_by_id[recipe_id]
                actual_outputs = sorted(
                    extract_recipe_outputs(spec, f"seed recipe {recipe_id}")
                )
                if actual_outputs != entry["outputs"]:
                    raise ManifestBuildError(
                        f"default restoration output fingerprint drifted for {recipe_id}: "
                        f"expected {entry['outputs']}, found {actual_outputs}"
                    )
                actual_removals = sorted(
                    unique_resource_array(spec.get("remove", []), f"{recipe_id} remove")
                )
                expected_removals = sorted(
                    removal["recipeId"] for removal in entry["ownedRemovals"]
                )
                if actual_removals != expected_removals:
                    raise ManifestBuildError(
                        f"default restoration removal ownership drifted for {recipe_id}: "
                        f"expected {expected_removals}, found {actual_removals}"
                    )

        family_outputs: set[str] = set()
        for index, family in enumerate(machine_families):
            for entry in require_array(family.get("recipes"), f"machine family {index} recipes"):
                if not isinstance(entry, dict):
                    raise ManifestBuildError(f"machine family {index} recipe must be an object")
                output = require_resource_id(entry.get("output"), f"machine family {index} output")
                if output in family_outputs or output in explicit_outputs:
                    raise ManifestBuildError(f"multiple managed recipes claim output {output}")
                family_outputs.add(output)

        excluded = set(unique_resource_array(seed.get("exclude_outputs", []), "exclude_outputs"))
        excluded.update(restoration_outputs)
        user_owned = set(
            unique_resource_array(seed.get("user_owned_outputs", []), "user_owned_outputs")
        )
        overlap = sorted(excluded & user_owned)
        if overlap:
            raise ManifestBuildError(f"outputs are both excluded and user-owned: {overlap}")
        managed_seed_outputs = (explicit_outputs - restoration_outputs) | family_outputs
        conflicting = sorted(managed_seed_outputs & (excluded | user_owned))
        if conflicting:
            raise ManifestBuildError(
                f"explicit/family managed outputs cannot also be excluded/user-owned: {conflicting}"
            )
        replacements = normalize_replacements(seed.get("ingredient_replacements", {}))
        source_overrides = normalize_source_overrides(seed.get("source_recipe_overrides", {}))
        additional_removals = sorted(
            set(unique_resource_array(seed.get("additional_removals", []), "additional_removals"))
        )
        additional_removal_set = set(additional_removals)
        if restoration["active"]:
            surviving_removal_owners: dict[str, list[str]] = defaultdict(list)
            for spec in explicit:
                identity = str(spec["id"])
                if identity in restoration_recipe_ids:
                    continue
                for recipe_id in unique_resource_array(
                    spec.get("remove", []), f"{identity} remove"
                ):
                    surviving_removal_owners[recipe_id].append(identity)
            for family in machine_families:
                for entry in require_array(family.get("recipes"), "machine family recipes"):
                    identity = machine_family_recipe_id(family, entry)
                    for recipe_id in unique_resource_array(
                        entry.get("remove", []), f"{identity} remove"
                    ):
                        surviving_removal_owners[recipe_id].append(identity)
            for recipe_id in additional_removals:
                surviving_removal_owners[recipe_id].append("additional_removals")
            ambiguous = OrderedDict(
                (recipe_id, sorted(surviving_removal_owners[recipe_id]))
                for recipe_id in sorted(restoration_removal_ids)
                if surviving_removal_owners.get(recipe_id)
            )
            if ambiguous:
                raise ManifestBuildError(
                    "default restoration removals are still required by surviving owners; "
                    f"refusing ambiguous stock restoration: {dict(ambiguous)}"
                )
            preserved_recipe_ids.update(restoration_removal_ids)
        conflicting_preserves = sorted(preserved_recipe_ids & additional_removal_set)
        if conflicting_preserves:
            raise ManifestBuildError(
                "recipe IDs are both preserved and additionally removed: "
                f"{conflicting_preserves}"
            )
        for spec in explicit:
            identity = str(spec["id"])
            if identity in restoration_recipe_ids:
                continue
            conflicts = sorted(
                preserved_recipe_ids
                & set(unique_resource_array(spec.get("remove", []), f"{identity} remove"))
            )
            if conflicts:
                raise ManifestBuildError(
                    f"explicit recipe {identity} removes preserved recipe IDs: {conflicts}"
                )
        for family in machine_families:
            for entry in require_array(family.get("recipes"), "machine family recipes"):
                identity = machine_family_recipe_id(family, entry)
                conflicts = sorted(
                    preserved_recipe_ids
                    & set(unique_resource_array(entry.get("remove", []), f"{identity} remove"))
                )
                if conflicts:
                    raise ManifestBuildError(
                        f"machine family recipe {identity} removes preserved recipe IDs: {conflicts}"
                    )
        threshold, phase_gates, exact_gate_items = normalize_policy(seed, phase_order)
        catalog = Catalog(catalog_path)
        jars = JarRecipes(mods_path)
        auto_assignments = seed.get("auto_assignments", True)
        if not isinstance(auto_assignments, bool):
            raise ManifestBuildError("auto_assignments must be boolean")
        if source_overrides and not auto_assignments:
            raise ManifestBuildError(
                "source_recipe_overrides cannot be used while auto_assignments is false"
            )
        for output, recipe_id in source_overrides.items():
            node = output_to_node.get(output)
            if node is None or unlock_types.get(output) in {"fluid", "chemical"}:
                raise ManifestBuildError(
                    f"source override output is not an assigned item unlock: {output}"
                )
            if output in managed_seed_outputs | excluded | user_owned:
                raise ManifestBuildError(
                    f"source override output is not eligible for auto assembly: {output}"
                )
            if node not in phase_by_node:
                raise ManifestBuildError(
                    f"source override output {output} belongs to an unmapped node {node!r}"
                )

        auto_recipes: list[OrderedDict[str, Any]] = []
        generated_meta: dict[str, dict[str, Any]] = {}
        item_assignments = [
            (output, node)
            for output, node in output_to_node.items()
            if unlock_types[output] not in {"fluid", "chemical"}
        ]
        for output, node in sorted(item_assignments):
            if output in explicit_outputs or output in family_outputs:
                report["ignored"].append(
                    OrderedDict((("output", output), ("node", node), ("reason", "explicit_recipe")))
                )
                continue
            if output in excluded:
                report["ignored"].append(
                    OrderedDict((("output", output), ("node", node), ("reason", "excluded_output")))
                )
                continue
            if output in user_owned:
                report["ignored"].append(
                    OrderedDict((("output", output), ("node", node), ("reason", "user_owned_output")))
                )
                continue
            if not auto_assignments:
                report["ignored"].append(
                    OrderedDict((("output", output), ("node", node), ("reason", "auto_assignments_disabled")))
                )
                continue
            phase = phase_by_node.get(node)
            if phase is None:
                report["skipped"].append(
                    OrderedDict((("output", output), ("node", node), ("reason", "unmapped_node_phase")))
                )
                continue
            rows = catalog.candidate_rows(output)
            try:
                producer_rows, classification_audit = classify_primary_producers(
                    output, rows, jars
                )
            except ManifestBuildError as error:
                add_fatal(
                    report,
                    "unclassifiable_primary_producer",
                    str(error),
                    output=output,
                    node=node,
                    phase=phase,
                )
                raise ManifestBuildError(str(error), report) from error
            report["producer_classification"].extend(classification_audit)
            producer_ids = sorted({row.recipe_id for row in producer_rows})
            if output in source_overrides and source_overrides[output] not in producer_ids:
                message = (
                    f"source override {source_overrides[output]} is not an installed primary "
                    f"producer of {output}"
                )
                add_fatal(
                    report,
                    "invalid_source_recipe_override",
                    message,
                    output=output,
                    node=node,
                    phase=phase,
                    recipe_id=source_overrides[output],
                    primary_producers=producer_ids,
                )
                raise ManifestBuildError(message, report)
            if not producer_ids:
                report["skipped"].append(
                    OrderedDict((("output", output), ("node", node), ("phase", phase), ("reason", "no_static_producer")))
                )
                continue
            if set(producer_ids).issubset(additional_removal_set):
                report["ignored"].append(
                    OrderedDict(
                        (
                            ("output", output),
                            ("node", node),
                            ("phase", phase),
                            ("reason", "retired_output"),
                            ("producer_ids", producer_ids),
                        )
                    )
                )
                continue
            try:
                chosen, unsupported = choose_stock_recipe(
                    output,
                    producer_rows,
                    jars,
                    replacements,
                    source_overrides.get(output),
                )
            except ManifestBuildError as error:
                error_code = (
                    "invalid_source_recipe_override"
                    if output in source_overrides
                    else "ambiguous_stock_recipe"
                )
                add_fatal(
                    report,
                    error_code,
                    str(error),
                    output=output,
                    node=node,
                    phase=phase,
                    producer_ids=producer_ids,
                )
                raise ManifestBuildError(str(error), report) from error
            if chosen is None:
                if output in source_overrides:
                    message = (
                        f"source override {source_overrides[output]} for {output} is not a "
                        "supported shaped, shapeless, or Create mechanical crafting recipe"
                    )
                    add_fatal(
                        report,
                        "invalid_source_recipe_override",
                        message,
                        output=output,
                        node=node,
                        phase=phase,
                        recipe_id=source_overrides[output],
                        unsupported=unsupported,
                    )
                    raise ManifestBuildError(message, report)
                direct_types = sorted({row.recipe_type for row in rows})
                reason = "unsupported_stock_crafting" if unsupported else "processing_only"
                report["skipped"].append(
                    OrderedDict(
                        (
                            ("output", output),
                            ("node", node),
                            ("phase", phase),
                            ("reason", reason),
                            ("producer_types", direct_types),
                            ("unsupported", unsupported),
                        )
                    )
                )
                continue
            gates = active_gates(
                phase_index[phase], threshold, phase_gates, output, exact_gate_items
            )
            try:
                spec, gated = make_auto_recipe(chosen, phase, gates)
            except UnsupportedStockRecipe as error:
                report["skipped"].append(
                    OrderedDict(
                        (
                            ("output", output),
                            ("node", node),
                            ("phase", phase),
                            ("reason", "cannot_apply_phase_gate"),
                            ("detail", str(error)),
                            ("source_recipe", chosen.source.recipe_id),
                        )
                    )
                )
                continue
            spec["remove"] = [
                recipe_id for recipe_id in producer_ids if recipe_id not in preserved_recipe_ids
            ]
            for recipe_id in sorted(set(producer_ids) & preserved_recipe_ids):
                report["preserved_removals"].append(
                    OrderedDict(
                        (
                            ("output", output),
                            ("managed_recipe", spec["id"]),
                            ("recipe_id", recipe_id),
                        )
                    )
                )
            spec["exclusive_output"] = True
            auto_recipes.append(spec)
            generated_meta[output] = {
                "node": node,
                "phase": phase,
                "source_recipe": chosen.source.recipe_id,
                "source_type": chosen.recipe_type,
                "managed_recipe": spec["id"],
                "removals": list(spec["remove"]),
                "gated_5x5": gated,
                "stock_ingredients": stock_ingredients(chosen),
                "unsupported_alternatives": unsupported,
                "selection": (
                    "seed_override" if output in source_overrides else "ranked_stock"
                ),
            }

        # Default-restoration decisions are applied only after normal explicit and
        # automatic selection.  The original explicit claims therefore suppress
        # same-run auto recreation, while dependency/removal ownership below sees
        # only the surviving managed set.
        explicit = [
            spec for spec in explicit if str(spec["id"]) not in restoration_recipe_ids
        ]
        all_recipes = explicit + auto_recipes
        managed_recipe_by_output: dict[str, str] = {}
        for spec in all_recipes:
            identity = str(spec["id"])
            for output in extract_recipe_outputs(spec, f"managed recipe {identity}"):
                managed_recipe_by_output[output] = identity
        for family in machine_families:
            for entry in require_array(family.get("recipes"), "machine family recipes"):
                output = require_resource_id(entry.get("output"), "machine family output")
                managed_recipe_by_output[output] = machine_family_recipe_id(family, entry)
        managed_recipe_ids = set(managed_recipe_by_output.values())
        for spec in all_recipes:
            outputs = extract_recipe_outputs(spec, f"managed recipe {spec.get('id')}")
            ingredients = extract_recipe_ingredients(spec)
            authored = authored_dependency_ids(spec)
            restored_default_dependencies = sorted(authored & restoration_recipe_ids)
            authored.difference_update(restoration_recipe_ids)
            unknown_authored = sorted(authored - managed_recipe_ids)
            if unknown_authored:
                raise ManifestBuildError(
                    f"{spec['id']} depends_on references unknown managed recipes: {unknown_authored}"
                )
            if restored_default_dependencies:
                report.setdefault("restored_default_dependency_edges", []).append(
                    OrderedDict(
                        (
                            ("recipe_id", str(spec["id"])),
                            ("retired_dependencies", restored_default_dependencies),
                        )
                    )
                )
            depends_on = {
                managed_recipe_by_output[ingredient]
                for ingredient in ingredients
                if ingredient in managed_recipe_by_output
            }
            depends_on.update(authored)
            depends_on.discard(str(spec["id"]))
            sorted_dependencies = sorted(depends_on)
            if sorted_dependencies:
                spec["depends_on"] = sorted_dependencies
            else:
                spec.pop("depends_on", None)
            for output in outputs:
                if output in generated_meta:
                    generated_meta[output]["depends_on"] = sorted_dependencies
                    hint = dependencies.get(output)
                    generated_meta[output]["dependency_manifest_ingredients"] = (
                        hint["ingredients"] if hint else []
                    )

        all_recipe_ids = [spec["id"] for spec in all_recipes]
        if len(all_recipe_ids) != len(set(all_recipe_ids)):
            raise ManifestBuildError("auto-generated recipe IDs collide with explicit recipe IDs")
        all_recipes.sort(
            key=lambda spec: (
                phase_index[spec["phase"]],
                spec.get("order", 999),
                spec["id"],
            )
        )
        additional_removals, removal_audit = deduplicate_exact_removals(
            all_recipes,
            machine_families,
            additional_removals,
            phase_index,
        )
        result: OrderedDict[str, Any] = OrderedDict()
        result["schema_version"] = 1
        result["project"] = project
        result["phase_order"] = list(phase_order)
        result["recipes"] = all_recipes
        result["machine_families"] = machine_families
        result["additional_removals"] = additional_removals
        result["preserve_recipe_ids"] = sorted(preserved_recipe_ids)
        result["disabled_recipe_ids"] = sorted(disabled_recipe_ids)
        if restoration["active"]:
            result["default_restoration"] = OrderedDict(
                (
                    ("policy", restoration["path"]),
                    ("policy_sha256", restoration["sha256"]),
                    ("retired_recipe_count", len(restoration_recipe_ids)),
                    ("restored_removal_count", len(restoration_removal_ids)),
                    ("excluded_outputs", sorted(restoration_outputs)),
                )
            )
        for source_key, output_key in (
            ("retired_recipe_uids", "retired_recipe_uids"),
            ("retired_removal_uids", "retired_removal_uids"),
        ):
            values = require_array(seed.get(source_key, []), source_key)
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ManifestBuildError(f"{source_key} must contain nonblank UUID strings")
            if len(values) != len(set(values)):
                raise ManifestBuildError(f"{source_key} contains duplicates")
            result[output_key] = sorted(values)

        report["generated"] = [
            OrderedDict((("output", output), *generated_meta[output].items()))
            for output in sorted(generated_meta)
        ]
        report["source_choices"] = [
            OrderedDict(
                (
                    ("output", output),
                    ("chosen", generated_meta[output]["source_recipe"]),
                    ("type", generated_meta[output]["source_type"]),
                    ("selection", generated_meta[output]["selection"]),
                )
            )
            for output in sorted(generated_meta)
        ]
        report["producer_classification"].sort(
            key=lambda entry: (entry["output"], entry["recipe_id"], entry["source_jar"])
        )
        report["removal_deduplications"] = removal_audit
        report["skipped"].sort(key=lambda entry: (entry["output"], entry["reason"]))
        report["ignored"].sort(key=lambda entry: (entry["output"], entry["reason"]))
        if restoration["active"]:
            report["default_restoration"] = OrderedDict(
                (
                    ("policy", restoration["path"]),
                    ("policy_sha256", restoration["sha256"]),
                    ("reason_counts", restoration["reason_counts"]),
                    ("recipe_ids", sorted(restoration_recipe_ids)),
                    ("outputs", sorted(restoration_outputs)),
                    ("restored_removal_ids", sorted(restoration_removal_ids)),
                    ("shared_removal_ambiguities", []),
                )
            )
        report["counts"] = OrderedDict(
            (
                ("assigned_item_outputs", len(item_assignments)),
                ("explicit_outputs", len(explicit_outputs - restoration_outputs)),
                ("disabled_explicit", len(disabled_recipe_ids)),
                ("machine_family_outputs", len(family_outputs)),
                ("auto_generated", len(auto_recipes)),
                ("retired_default_recipes", len(restoration_recipe_ids)),
                ("restored_default_removals", len(restoration_removal_ids)),
                ("skipped", len(report["skipped"])),
                ("ignored", len(report["ignored"])),
                ("managed_recipes", len(all_recipes)),
            )
        )
        report["status"] = "ok_with_skips" if report["skipped"] else "ok"
        return result, report
    except ManifestBuildError as error:
        if error.report is not None:
            raise
        add_fatal(report, "malformed_input", str(error))
        raise ManifestBuildError(str(error), report) from error


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--dependencies", type=Path, default=DEFAULT_DEPENDENCIES)
    parser.add_argument("--catalog", type=Path, default=None)
    parser.add_argument("--mods", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--check", action="store_true", help="fail if output or deterministic report is stale"
    )
    args = parser.parse_args(argv)
    catalog = (args.catalog or default_catalog()).resolve()
    mods = (args.mods or default_mods()).resolve()
    output = args.output.resolve()
    report_path = args.report.resolve()
    try:
        manifest, report = build_manifest(
            args.seed.resolve(),
            args.assignments.resolve(),
            args.dependencies.resolve(),
            catalog,
            mods,
        )
    except ManifestBuildError as error:
        if error.report is not None and not args.check:
            atomic_write(report_path, encoded_json(error.report))
        print(f"managed recipe manifest build failed: {error}", file=sys.stderr)
        return 2
    manifest_bytes = encoded_json(manifest)
    report_bytes = encoded_json(report)
    if args.check:
        stale = []
        if not output.is_file() or output.read_bytes() != manifest_bytes:
            stale.append(str(output))
        if not report_path.is_file() or report_path.read_bytes() != report_bytes:
            stale.append(str(report_path))
        if stale:
            print("managed recipe assembler outputs are stale: " + ", ".join(stale), file=sys.stderr)
            return 1
    else:
        atomic_write(output, manifest_bytes)
        atomic_write(report_path, report_bytes)
    print(
        f"Assembled {report['counts']['managed_recipes']} managed recipes "
        f"({report['counts']['auto_generated']} automatic); "
        f"{report['counts']['skipped']} assigned outputs reported as skipped."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
