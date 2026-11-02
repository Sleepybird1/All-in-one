from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


RECIPE_PATH = re.compile(r"^data/([^/]+)/(?:recipe|recipes)/(.+)\.json$")
TAG_PATH = re.compile(r"^data/([^/]+)/tags/(item|block|fluid|chemical)/(.+)\.json$")
RESOURCE_ID = re.compile(r"['\"]([a-z0-9_.-]+:[a-z0-9_./-]+)['\"]")
REMOVAL_ARRAY = re.compile(r"const\s+removed\w+\s*=\s*\[(.*?)\]", re.DOTALL)

INPUT_KEYS = {
    "addition",
    "base",
    "catalyst",
    "chemical_input",
    "extra_input",
    "fluid_input",
    "ingredient",
    "ingredients",
    "input",
    "inputs",
    "item_input",
    "key",
    "left_input",
    "main_input",
    "right_input",
    "template",
}
OUTPUT_KEYS = {
    "byproduct",
    "byproducts",
    "chemical_output",
    "fluid_output",
    "item_output",
    "main_output",
    "output",
    "outputs",
    "primary_output",
    "result",
    "results",
    "secondary_output",
}

RAW_URANIUM = {
    "mekanism:uranium_ore",
    "mekanism:deepslate_uranium_ore",
    "mekanism:raw_uranium",
    "mekanism:block_raw_uranium",
}
PHYSICAL_URANIUM = {
    "mekanism:ingot_uranium",
    "mekanism:nugget_uranium",
    "mekanism:block_uranium",
    "mekanism:dust_uranium",
    "mekanism:dirty_dust_uranium",
    "mekanism:clump_uranium",
    "mekanism:shard_uranium",
    "mekanism:crystal_uranium",
}
CHEMICAL_URANIUM = {
    "mekanism:yellow_cake_uranium",
    "mekanism:dirty_uranium",
    "mekanism:clean_uranium",
    "mekanism:uranium_oxide",
    "mekanism:uranium_hexafluoride",
    "mekanism:fissile_fuel",
}
NATURAL_YELLORIUM = {
    "bigreactors:yellorite_ore",
    "bigreactors:deepslate_yellorite_ore",
    "bigreactors:raw_yellorium",
    "bigreactors:raw_yellorium_block",
}
REFINED_YELLORIUM = {
    "industrial_colonies:yellorium_compound",
    "bigreactors:yellorium_ingot",
    "bigreactors:yellorium_block",
    "bigreactors:yellorium",
    "bigreactors:flowing_yellorium",
    "bigreactors:yellorium_bucket",
}
YELLORIUM_FAMILY = NATURAL_YELLORIUM | REFINED_YELLORIUM
REACTOR_FUELS = {
    "industrial_colonies:enriched_uranium_fuel_pellet",
}
SULFUR_ACIDS = {
    "tfmg:sulfuric_acid",
    "tfmg:sulfuric_acid_bucket",
    "mekanism:sulfuric_acid",
    "mekanism:sulfuric_acid_bucket",
}

CANONICAL_ITEM_TAGS = {
    "c:ores/uranium": RAW_URANIUM & {
        "mekanism:uranium_ore",
        "mekanism:deepslate_uranium_ore",
    },
    "c:raw_materials/uranium": {"mekanism:raw_uranium"},
    "c:storage_blocks/raw_uranium": {"mekanism:block_raw_uranium"},
    # Empty on purpose: Extreme Reactors registers these two common tags as
    # direct reactor fuel in ReactorGameData.  Mekanism's recipes are rewritten
    # to exact inputs so physical uranium can still be processed without
    # becoming pre-enrichment reactor fuel.
    "c:ingots/uranium": set(),
    "c:storage_blocks/uranium": set(),
    "forge:storage_blocks/uranium": set(),
    "c:nuggets/uranium": {"mekanism:nugget_uranium"},
    "c:dusts/uranium": {"mekanism:dust_uranium"},
    "c:dirty_dusts/uranium": {"mekanism:dirty_dust_uranium"},
    "c:clumps/uranium": {"mekanism:clump_uranium"},
    "c:shards/uranium": {"mekanism:shard_uranium"},
    "c:crystals/uranium": {"mekanism:crystal_uranium"},
    "c:dusts/sulfur": {"tfmg:sulfur_dust"},
    "c:buckets/sulfuric_acid": {"tfmg:sulfuric_acid_bucket"},
}
CANONICAL_FLUID_TAGS = {
    # Extreme Reactors maps this common fluid tag straight to its built-in
    # Yellorium reactant. Manufactured molten Yellorium is a precursor only.
    "c:yellorium": set(),
    "c:sulfuric_acid": {"tfmg:sulfuric_acid"},
    "industrial_colonies:legacy_mekanism_sulfuric_acid": {"mekanism:sulfuric_acid"},
}

MODERNFOUNDRY_URANIUM_ROUTES = {
    "modernfoundry:smeltery/casting/metal/uranium/block",
    "modernfoundry:smeltery/casting/metal/uranium/coin_gold_cast",
    "modernfoundry:smeltery/casting/metal/uranium/coin_sand_cast",
    "modernfoundry:smeltery/casting/metal/uranium/gear_gold_cast",
    "modernfoundry:smeltery/casting/metal/uranium/gear_sand_cast",
    "modernfoundry:smeltery/casting/metal/uranium/ingot_gold_cast",
    "modernfoundry:smeltery/casting/metal/uranium/ingot_sand_cast",
    "modernfoundry:smeltery/casting/metal/uranium/nugget_gold_cast",
    "modernfoundry:smeltery/casting/metal/uranium/nugget_sand_cast",
    "modernfoundry:smeltery/casting/metal/uranium/plate_gold_cast",
    "modernfoundry:smeltery/casting/metal/uranium/plate_sand_cast",
    "modernfoundry:smeltery/melting/metal/uranium/block",
    "modernfoundry:smeltery/melting/metal/uranium/coin",
    "modernfoundry:smeltery/melting/metal/uranium/dust",
    "modernfoundry:smeltery/melting/metal/uranium/gear",
    "modernfoundry:smeltery/melting/metal/uranium/ingot",
    "modernfoundry:smeltery/melting/metal/uranium/nugget",
    "modernfoundry:smeltery/melting/metal/uranium/ore_dense",
    "modernfoundry:smeltery/melting/metal/uranium/ore_singular",
    "modernfoundry:smeltery/melting/metal/uranium/ore_sparse",
    "modernfoundry:smeltery/melting/metal/uranium/oreberry",
    "modernfoundry:smeltery/melting/metal/uranium/plate",
    "modernfoundry:smeltery/melting/metal/uranium/raw",
    "modernfoundry:smeltery/melting/metal/uranium/raw_block",
    "modernfoundry:smeltery/melting/metal/uranium/sheetmetal",
}

REQUIRED_REMOVALS = {
    "bigreactors:smelting/yellorium_from_ore",
    "bigreactors:blasting/yellorium_from_ore",
    "bigreactors:smelting/yellorium_from_raw",
    "bigreactors:blasting/yellorium_from_raw",
    "bigreactors:crafting/raw_yellorium_component_to_storage",
    "bigreactors:crafting/raw_yellorium_storage_to_component",
    "bigreactors:fluidizer/solid/yellorium",
    "bigreactors:fluidizer/solid/yellorium9",
    "thermal:pulverizer_yellorite_ore_to_dust",
    "thermal:pulverizer_yellorium_ingot_to_dust",
    "create:crushing/raw_uranium",
    "create:crushing/raw_uranium_block",
    "create:crushing/uranium_ore",
    "create:splashing/mekanism/crushed_raw_uranium",
    "create:splashing/ic2/crushed_raw_uranium",
    "create:splashing/immersiveengineering/crushed_raw_uranium",
    "create_mekanism_improvements:uranium_ingot",
    "create:smelting/ingot_uranium_compat_ic2",
    "create:smelting/ingot_uranium_compat_immersiveengineering",
    "create:smelting/ingot_uranium_compat_mekanism",
    "create:blasting/ingot_uranium_compat_ic2",
    "create:blasting/ingot_uranium_compat_immersiveengineering",
    "create:blasting/ingot_uranium_compat_mekanism",
    "mekanism:processing/uranium/ingot/from_dust_smelting",
    "mekanism:processing/uranium/ingot/from_dust_blasting",
    "mekanism:processing/uranium/ingot/from_ore_smelting",
    "mekanism:processing/uranium/ingot/from_ore_blasting",
    "mekanism:processing/uranium/ingot/from_raw_smelting",
    "mekanism:processing/uranium/ingot/from_raw_blasting",
    "mekanism:processing/uranium/dust/from_ingot",
    "mekanism:processing/uranium/ingot/from_nuggets",
    # The Oredictionificator performs a runtime tag conversion rather than a
    # datapack recipe.  If another mod restores either shared uranium tag, it
    # would otherwise normalize Yellorium straight into Mekanism uranium and
    # bypass the directional enrichment chain.
    "mekanism:oredictionificator",
    "mekanism:chemical_conversion/sulfur_to_sulfuric_acid",
    "mekanism:chemical_infusing/sulfuric_acid",
    "mekanism:rotary/sulfuric_acid",
} | MODERNFOUNDRY_URANIUM_ROUTES

EXACT_URANIUM_REWRITES = {
    "mekanism:processing/uranium/yellow_cake_uranium",
    "mekanism:processing/uranium/storage_blocks/from_ingots",
}

EXPECTED_STAGES = {
    "tfmg:vat_machine_recipe/sulfuric_acid": "CR01 — Chemical Processing",
    "industrial_colonies:sulfur/tfmg_acid_rotary_bridge": "CR01 — Electrochemical Engineering",
    "createmetallurgy:crafting/content/foundry_basin": "CR01 — Advanced Alloy Mixing",
    "createmetallurgy:crafting/content/foundry_lid": "CR01 — Advanced Alloy Mixing",
    "createmetallurgy:crafting/content/foundry_mixer": "CR01 — Advanced Alloy Mixing",
    "createmetallurgy:sequenced_assembly/industrial_crucible": "CR01 — Advanced Alloy Mixing",
    "industrial_colonies:materials/yellorium/molten_alloy": "CR01 — Advanced Alloy Mixing",
    "industrial_colonies:materials/yellorium/ingot_casting": "CR01 — Advanced Metallurgy",
    "industrial_colonies:materials/yellorium_compound": "CR01 — Yellorium Refinement",
    "industrial_colonies:materials/uranium/raw_from_yellorium_compound": "CR01 — Isotope Materials",
    "industrial_colonies:materials/uranium/osmium_compressed_ingot": "CR01 — Isotope Materials",
    "mekanism:processing/uranium/dust/from_raw_ore": "CR01 — Isotope Materials",
    "mekanism:processing/uranium/yellow_cake_uranium": "CR01 — Isotope Materials",
    "mekanism:processing/uranium/fissile_fuel": "CR01 — Uranium Processing",
    "mekanism:processing/uranium/sulfuric_acid": "CR01 — Uranium Processing",
    "mekanism:processing/uranium/uranium_oxide": "CR01 — Uranium Processing",
    "industrial_colonies:fuel/early_nuclear/enriched_uranium_fuel_pellet": "CR01 — Early Nuclear Fuel",
    "bigreactors:crafting/yellorium_component_to_storage": "CR01 — Yellorium Refinement",
    "bigreactors:crafting/yellorium_storage_to_component": "CR01 — Yellorium Refinement",
    "mekanism:processing/uranium/reprocessing/from_plutonium": "CR01 — Plutonium Production",
    "mekanism:processing/uranium/reprocessing/to_fuel": "CR01 — Plutonium Production",
}

# Fingerprint the external pack separately from Industrial Colonies itself.
# The project JAR is the artifact under test, so a normal project version bump
# must not look like an unaudited third-party modpack change.
# Re-audited against the 236 external JARs installed on 2026-09-04.  The additions
# changed only the pack inventory fingerprint: the independently
# scanned compiled/NBT nuclear references below remained byte-for-byte stable.
EXPECTED_EXTERNAL_JAR_COUNT = 236
EXPECTED_EXTERNAL_JAR_INVENTORY_SHA256 = "5ba7b3634dfa64e127394bb59c260b39e5b8ca36b39509dc94796f1f7ab646bd"
EXPECTED_BINARY_HITS_SHA256 = "b5a8f9fdf17bce326be06bc2aa8fc26c4d915ca857b676e8c4df19f6142d689b"
# Stock construction recipes were restored, so the focused inventory now
# contains only the retained Yellorium -> uranium route, sulfuric-acid bridge,
# and enriched fuel pellet. Update this only after inspecting the report's
# kubejs_sensitive_output_hits list, not merely because the hash changed.
EXPECTED_KUBEJS_OUTPUT_HITS_SHA256 = "6950a85fc8933ff39ec7ea762e4080a3862aa30e80cac7e35f23dd3a5a4382c8"
AUDITED_JAR_SHA256 = {
    "allthecompressed-1.21.1-4.4.0.jar": "D1B0C1135D8C206B8F18C73AFA08256C74F8B9504626F90E2A64614C92163C36",
    "allthemodium-3.0.1_mc_1.21.1.jar": "870004C1D6FBD0891FF322B9FF9E8D42C6AAA082ACE7562E25948F1636B5C6F1",
    "ExtremeReactors2-1.21.1-2.4.28.jar": "74FDFDFC91C3C8E5A439D411E6F081D12193635FFFE2C55142F2F28F75B9D621",
    "Mekanism-1.21.1-10.7.19.85.jar": "004DBC9F3106F4D192AEAA1EE1190DD16EC9CA8059ED3D093B80034F4C574F43",
    "ModernFoundry-1.21.1-4.1.6-NeoForge.jar": "0B0026DB1C27A1D08B1E3D3EBA8FD2CC470D4CB534EB08D74633ADC5BE5691F1",
    "tfmg-1.2.0.jar": "FC824A91CFE22E137C9014ED608EE9BF35F16490D2162B687666332C6EB3A555",
}

BINARY_TOKENS = {
    "bigreactors:yellorium": b"bigreactors:yellorium",
    "bigreactors:yellorium_ingot": b"bigreactors:yellorium_ingot",
    "bigreactors:raw_yellorium": b"bigreactors:raw_yellorium",
    "mekanism:ingot_uranium": b"mekanism:ingot_uranium",
    "mekanism:raw_uranium": b"mekanism:raw_uranium",
    "mekanism:fissile_fuel": b"mekanism:fissile_fuel",
    "mekanism:sulfuric_acid": b"mekanism:sulfuric_acid",
    "tfmg:sulfuric_acid": b"tfmg:sulfuric_acid",
    "ingots/uranium": b"ingots/uranium",
    "storage_blocks/uranium": b"storage_blocks/uranium",
    "raw_materials/uranium": b"raw_materials/uranium",
    "sulfuric_acid": b"sulfuric_acid",
}

KUBEJS_OUTPUT_BLOCK = re.compile(
    r"(?:result|results|output|outputs|item_output|chemical_output|fluid_output)\s*:\s*"
    r"(\[[^\]]*\]|\{[^}]*\})",
    re.DOTALL,
)


@dataclass(frozen=True)
class Recipe:
    recipe_id: str
    recipe_type: str
    jar: str
    path: str
    inputs: frozenset[str]
    outputs: frozenset[str]
    conditions_active: bool


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from strings(nested)


def contextual_ids(node: Any, context: str | None = None) -> set[str]:
    result: set[str] = set()
    if isinstance(node, str):
        if context and ":" in node:
            result.add(node.lstrip("#"))
        return result
    if isinstance(node, list):
        for value in node:
            result.update(contextual_ids(value, context))
        return result
    if not isinstance(node, dict):
        return result

    if context:
        for key in ("item", "id", "fluid", "chemical"):
            value = node.get(key)
            if isinstance(value, str) and ":" in value:
                result.add(value.lstrip("#"))
        tag = node.get("tag")
        if isinstance(tag, str) and ":" in tag:
            result.add("#" + tag.lstrip("#"))

    for key, value in node.items():
        normalized = key.lower().replace("-", "_")
        child_context = context
        if normalized in INPUT_KEYS or normalized.endswith("_input"):
            child_context = "input"
        elif normalized in OUTPUT_KEYS or normalized.endswith("_output"):
            child_context = "output"
        result.update(contextual_ids(value, child_context))
    return result


def mod_ids(archive: zipfile.ZipFile) -> set[str]:
    result: set[str] = set()
    for name in ("META-INF/neoforge.mods.toml", "META-INF/mods.toml"):
        try:
            text = archive.read(name).decode("utf-8", errors="ignore")
        except KeyError:
            continue
        result.update(re.findall(r"(?im)^\s*modId\s*=\s*[\"']([^\"']+)", text))
    try:
        fabric = json.loads(archive.read("fabric.mod.json"))
        if isinstance(fabric.get("id"), str):
            result.add(fabric["id"])
    except (KeyError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    return result


def condition_active(condition: Any, installed: set[str]) -> bool:
    if not isinstance(condition, dict):
        return True
    kind = condition.get("type", "")
    if kind in {"neoforge:mod_loaded", "forge:mod_loaded"}:
        return condition.get("modid") in installed
    if kind in {"neoforge:tag_empty", "forge:tag_empty"}:
        # Pack-wide route discovery is deliberately conservative. Treat an
        # unevaluated tag as populated so `not(tag_empty)` compatibility
        # recipes remain visible to the audit rather than being hidden.
        return False
    if kind in {"neoforge:not", "forge:not"}:
        return not condition_active(condition.get("value"), installed)
    if kind in {"neoforge:and", "forge:and"}:
        return all(condition_active(value, installed) for value in condition.get("values", []))
    if kind in {"neoforge:or", "forge:or"}:
        return any(condition_active(value, installed) for value in condition.get("values", []))
    # Unknown conditions are treated as active: the audit must not hide a
    # possible route just because it cannot statically evaluate a predicate.
    return True


def recipe_conditions_active(data: dict[str, Any], installed: set[str]) -> bool:
    conditions = data.get("neoforge:conditions", data.get("conditions", []))
    return all(condition_active(value, installed) for value in conditions)


def parse_removed_ids(server_scripts: Path) -> set[str]:
    removed: set[str] = set()
    for path in server_scripts.glob("*.js"):
        text = path.read_text(encoding="utf-8")
        for body in REMOVAL_ARRAY.findall(text):
            removed.update(RESOURCE_ID.findall(body))
    return removed


def parse_seed_removed_ids(project: Path) -> set[str]:
    """Collect exact removals owned by the recipe-v2 seed.

    The nuclear audit predates the managed-recipe compiler and originally saw
    only JavaScript removal arrays.  Runtime-only machines such as the
    Oredictionificator are now retired through the same authoritative seed as
    the rest of the recipe overhaul, so the safety audit must include both
    ownership surfaces.
    """

    seed_path = project / "progression" / "managed_recipe_overhaul.seed.json"
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    removed = {
        str(recipe_id)
        for recipe_id in data.get("additional_removals", [])
        if isinstance(recipe_id, str)
    }
    for recipe in data.get("recipes", []):
        if isinstance(recipe, dict):
            removed.update(
                str(recipe_id)
                for recipe_id in recipe.get("remove", [])
                if isinstance(recipe_id, str)
            )
    for family in data.get("machine_families", []):
        if not isinstance(family, dict):
            continue
        for recipe in family.get("recipes", []):
            if isinstance(recipe, dict):
                removed.update(
                    str(recipe_id)
                    for recipe_id in recipe.get("remove", [])
                    if isinstance(recipe_id, str)
                )
    return removed


def load_stages(project: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for filename in ("machine_recipe_dependencies.json", "additional_recipe_stages.json"):
        data = json.loads((project / "tools" / filename).read_text(encoding="utf-8"))
        rows = data.get("recipes", data) if isinstance(data, dict) else data
        for row in rows:
            recipe_id = row.get("recipe_id")
            node = row.get("node")
            if recipe_id and node:
                previous = result.setdefault(recipe_id, node)
                if previous != node:
                    raise ValueError(f"Conflicting stage for {recipe_id}: {previous} / {node}")
    return result


def load_pack(mods_dir: Path) -> tuple[list[Recipe], dict[str, set[str]], list[dict[str, Any]], list[dict[str, Any]], set[str], list[dict[str, str]]]:
    jars = sorted(mods_dir.glob("*.jar"), key=lambda path: path.name.lower())
    installed: set[str] = set()
    jar_errors: list[dict[str, str]] = []
    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as archive:
                installed.update(mod_ids(archive))
        except (OSError, zipfile.BadZipFile) as exc:
            jar_errors.append({"jar": jar.name, "error": str(exc)})

    recipes: list[Recipe] = []
    tags: dict[str, set[str]] = defaultdict(set)
    nonrecipe_hits: list[dict[str, Any]] = []
    binary_hits: list[dict[str, Any]] = []
    targets = (
        RAW_URANIUM
        | PHYSICAL_URANIUM
        | CHEMICAL_URANIUM
        | YELLORIUM_FAMILY
        | REACTOR_FUELS
        | SULFUR_ACIDS
    )
    target_words = ("uranium", "yellor", "sulfuric_acid", "sulphuric_acid", "fissile_fuel")

    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as archive:
                for name in archive.namelist():
                    if name.endswith(".class") or (name.startswith("data/") and name.endswith(".nbt")):
                        payload = archive.read(name)
                        if name.endswith(".nbt") and payload.startswith(b"\x1f\x8b"):
                            try:
                                payload = gzip.decompress(payload)
                            except OSError:
                                pass
                        hits = sorted(label for label, token in BINARY_TOKENS.items() if token in payload)
                        if hits:
                            binary_hits.append({"jar": jar.name, "path": name, "tokens": hits})
                        continue
                    if not name.startswith("data/") or not name.endswith(".json"):
                        continue
                    try:
                        data = json.loads(archive.read(name).decode("utf-8-sig"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                    tag_match = TAG_PATH.fullmatch(name)
                    if tag_match and isinstance(data, dict):
                        namespace, registry, path = tag_match.groups()
                        tag = f"{registry}#{namespace}:{path}"
                        for value in data.get("values", []):
                            if isinstance(value, str):
                                tags[tag].add(value)
                            elif isinstance(value, dict) and isinstance(value.get("id"), str):
                                tags[tag].add(value["id"])
                    recipe_match = RECIPE_PATH.fullmatch(name)
                    if recipe_match and isinstance(data, dict):
                        namespace, path = recipe_match.groups()
                        all_contextual = contextual_ids(data)
                        inputs = contextual_ids({"input": {key: value for key, value in data.items() if key.lower().replace("-", "_") not in OUTPUT_KEYS}})
                        outputs = contextual_ids({"output": {key: value for key, value in data.items() if key.lower().replace("-", "_") in OUTPUT_KEYS or key.lower().replace("-", "_").endswith("_output")}})
                        # Fallback for serializers that place a bare result ID in
                        # an unconventional output field.
                        outputs.update(value for value in all_contextual if value in targets and value not in inputs)
                        recipes.append(
                            Recipe(
                                recipe_id=f"{namespace}:{path}",
                                recipe_type=str(data.get("type", "")),
                                jar=jar.name,
                                path=name,
                                inputs=frozenset(inputs),
                                outputs=frozenset(outputs),
                                conditions_active=recipe_conditions_active(data, installed),
                            )
                        )
                    else:
                        values = sorted(set(strings(data)))
                        relevant = sorted(
                            value for value in values
                            if value in targets or any(word in value.lower() for word in target_words)
                        )
                        if relevant:
                            nonrecipe_hits.append({"jar": jar.name, "path": name, "refs": relevant})
        except (OSError, zipfile.BadZipFile):
            continue
    return recipes, tags, nonrecipe_hits, binary_hits, installed, jar_errors


def resolve_tag(tag: str, registry: str, tags: dict[str, set[str]], seen: set[str] | None = None) -> set[str]:
    if registry == "item" and tag in CANONICAL_ITEM_TAGS:
        return set(CANONICAL_ITEM_TAGS[tag])
    if registry == "fluid" and tag in CANONICAL_FLUID_TAGS:
        return set(CANONICAL_FLUID_TAGS[tag])
    seen = set() if seen is None else seen
    key = f"{registry}#{tag}"
    if key in seen:
        return set()
    seen.add(key)
    result: set[str] = set()
    for value in tags.get(key, set()):
        if value.startswith("#"):
            result.update(resolve_tag(value[1:], registry, tags, seen))
        else:
            result.add(value)
    return result


def expanded_inputs(recipe: Recipe, tags: dict[str, set[str]]) -> set[str]:
    result: set[str] = set()
    for value in recipe.inputs:
        if not value.startswith("#"):
            result.add(value)
            continue
        tag = value[1:]
        for registry in ("item", "fluid", "chemical"):
            result.update(resolve_tag(tag, registry, tags))
    return result


def inspect_extreme_reactors_fuel_mapping(mods_dir: Path) -> dict[str, Any]:
    jar = mods_dir / "ExtremeReactors2-1.21.1-2.4.28.jar"
    evidence = {
        "jar": jar.name,
        "content_tags_declares_ingots_uranium": False,
        "content_tags_declares_ingots_yellorium": False,
        "content_tags_declares_blocks_yellorium": False,
        "content_tags_declares_fluid_yellorium": False,
        "reactor_data_registers_ingot_mapping": False,
        "reactor_data_registers_fluid_mapping": False,
        "reactor_data_references_ingots_yellorium": False,
        "reactor_data_references_blocks_yellorium": False,
        "reactor_data_references_fluid_yellorium": False,
        "reactor_data_references_ingots_uranium": False,
        "reactor_data_references_storage_blocks_uranium": False,
    }
    if not jar.exists():
        return evidence
    with zipfile.ZipFile(jar) as archive:
        content_tags = archive.read(
            "it/zerono/mods/extremereactors/gamecontent/ContentTags$Items.class"
        )
        content_fluid_tags = archive.read(
            "it/zerono/mods/extremereactors/gamecontent/ContentTags$Fluids.class"
        )
        reactor_data = archive.read(
            "it/zerono/mods/extremereactors/gamecontent/ReactorGameData.class"
        )
    evidence.update(
        {
            "content_tags_declares_ingots_uranium": b"ingots/uranium" in content_tags,
            "content_tags_declares_ingots_yellorium": b"ingots/yellorium" in content_tags,
            "content_tags_declares_blocks_yellorium": b"storage_blocks/yellorium" in content_tags,
            "content_tags_declares_fluid_yellorium": b"YELLORIUM" in content_fluid_tags,
            "reactor_data_registers_ingot_mapping": b"registerIngotReactantMapping" in reactor_data,
            "reactor_data_registers_fluid_mapping": b"registerFluidReactantMapping" in reactor_data,
            "reactor_data_references_ingots_yellorium": b"INGOTS_YELLORIUM" in reactor_data,
            "reactor_data_references_blocks_yellorium": b"BLOCKS_YELLORIUM" in reactor_data,
            "reactor_data_references_fluid_yellorium": b"YELLORIUM" in reactor_data,
            "reactor_data_references_ingots_uranium": b"INGOTS_URANIUM" in reactor_data,
            "reactor_data_references_storage_blocks_uranium": b"c:storage_blocks/uranium" in reactor_data,
        }
    )
    return evidence


def scan_kubejs_sensitive_outputs(server_scripts: Path) -> list[dict[str, Any]]:
    targets = (
        RAW_URANIUM
        | PHYSICAL_URANIUM
        | CHEMICAL_URANIUM
        | YELLORIUM_FAMILY
        | REACTOR_FUELS
        | SULFUR_ACIDS
    )
    result: list[dict[str, Any]] = []
    for script in sorted(server_scripts.glob("*.js")):
        text = script.read_text(encoding="utf-8")
        outputs: set[str] = set()
        for block in KUBEJS_OUTPUT_BLOCK.findall(text):
            outputs.update(value for value in RESOURCE_ID.findall(block) if value in targets)
        if outputs:
            result.append({"script": script.name, "outputs": sorted(outputs)})
    return result


def custom_recipe_block(text: str, recipe_id: str) -> str:
    marker = f".id('{recipe_id}')"
    end = text.find(marker)
    if end < 0:
        return ""
    start = text.rfind("event.custom({", 0, end)
    if start < 0:
        return ""
    return text[start : end + len(marker)]


def inspect_project_reactor_policy(project: Path) -> dict[str, Any]:
    config_path = project / "pack-config-overrides" / "ExtremeReactors" / "modpack_api.json"
    tag_path = (
        project
        / "src/main/resources/data/industrial_colonies/tags/item/reactor_fuels/enriched_uranium.json"
    )
    config = json.loads(config_path.read_text(encoding="utf-8"))
    tag = json.loads(tag_path.read_text(encoding="utf-8"))
    sources = config["ReactorReactantSources"]
    yellorium_additions = [
        row for row in sources.get("Add", []) if row.get("ProductName") == "yellorium"
    ]
    return {
        "config": str(config_path.relative_to(project)),
        "generic_source_tags_removed": sorted(sources.get("Remove", [])),
        "yellorium_source_additions": yellorium_additions,
        "pellet_tag": tag,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the manufactured-Yellorium -> Mekanism uranium -> enriched-fuel "
            "route and the sole-source sulfuric-acid boundary against every active JAR."
        )
    )
    parser.add_argument("instance", type=Path, help="Minecraft instance directory")
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--inventory-only", action="store_true", help="emit discovery inventory without enforcing policy"
    )
    args = parser.parse_args()

    project = args.project.resolve()
    scripts = project / "pack-scripts" / "server_scripts"
    mods_dir = args.instance / "mods"
    recipes, tags, nonrecipe_hits, binary_hits, installed, archive_errors = load_pack(mods_dir)
    removed = parse_removed_ids(scripts) | parse_seed_removed_ids(project)
    stages = load_stages(project)
    effective = [recipe for recipe in recipes if recipe.conditions_active and recipe.recipe_id not in removed]
    effective_by_id: dict[str, list[Recipe]] = defaultdict(list)
    for recipe in effective:
        effective_by_id[recipe.recipe_id].append(recipe)

    jar_names = sorted(path.name for path in mods_dir.glob("*.jar"))
    project_jar_names = [
        name for name in jar_names if re.fullmatch(r"industrial_colonies-.+\.jar", name, re.IGNORECASE)
    ]
    external_jar_names = [name for name in jar_names if name not in project_jar_names]
    jar_inventory_sha256 = hashlib.sha256("\n".join(jar_names).encode()).hexdigest()
    external_jar_inventory_sha256 = hashlib.sha256("\n".join(external_jar_names).encode()).hexdigest()
    audited_jar_hashes = {
        name: sha256(mods_dir / name).upper()
        for name in AUDITED_JAR_SHA256
        if (mods_dir / name).exists()
    }
    reactor_fuel_mapping = inspect_extreme_reactors_fuel_mapping(mods_dir)
    project_reactor_policy = inspect_project_reactor_policy(project)
    kubejs_output_hits = scan_kubejs_sensitive_outputs(scripts)
    binary_hits_sha256 = hashlib.sha256(
        "\n".join(
            f"{row['jar']}!{row['path']}:{','.join(row['tokens'])}"
            for row in sorted(binary_hits, key=lambda value: (value["jar"], value["path"]))
        ).encode()
    ).hexdigest()
    kubejs_output_hits_sha256 = hashlib.sha256(
        "\n".join(f"{row['script']}:{','.join(row['outputs'])}" for row in kubejs_output_hits).encode()
    ).hexdigest()

    relevant_materials = (
        RAW_URANIUM | PHYSICAL_URANIUM | CHEMICAL_URANIUM | YELLORIUM_FAMILY | REACTOR_FUELS
    )
    relevant_recipes: list[dict[str, Any]] = []
    acid_producers: list[dict[str, Any]] = []
    jar_yellorium_to_uranium: list[str] = []
    uranium_to_yellorium: list[str] = []
    natural_yellorium_producers: list[str] = []
    uranium_tag_consumers: list[str] = []
    unclassified_fuel_producers: list[str] = []
    for recipe in recipes:
        inputs = expanded_inputs(recipe, tags)
        row = {
            "recipe_id": recipe.recipe_id,
            "type": recipe.recipe_type,
            "jar": recipe.jar,
            "inputs": sorted(recipe.inputs),
            "expanded_inputs": sorted(inputs),
            "outputs": sorted(recipe.outputs),
            "conditions_active": recipe.conditions_active,
            "removed": recipe.recipe_id in removed,
            "stage": stages.get(recipe.recipe_id),
        }
        if (inputs | set(recipe.outputs)) & (relevant_materials | SULFUR_ACIDS):
            relevant_recipes.append(row)
        if set(recipe.outputs) & SULFUR_ACIDS:
            acid_producers.append(row)
        if not recipe.conditions_active or recipe.recipe_id in removed:
            continue
        outputs = set(recipe.outputs)
        if inputs & YELLORIUM_FAMILY and outputs & (RAW_URANIUM | PHYSICAL_URANIUM | CHEMICAL_URANIUM):
            jar_yellorium_to_uranium.append(recipe.recipe_id)
        if inputs & (RAW_URANIUM | PHYSICAL_URANIUM | CHEMICAL_URANIUM | REACTOR_FUELS) and outputs & REFINED_YELLORIUM:
            uranium_to_yellorium.append(recipe.recipe_id)
        if outputs & NATURAL_YELLORIUM:
            natural_yellorium_producers.append(recipe.recipe_id)
        if any(
            value in recipe.inputs
            for value in ("#c:ingots/uranium", "#c:storage_blocks/uranium", "#forge:storage_blocks/uranium")
        ):
            uranium_tag_consumers.append(recipe.recipe_id)
        if outputs & (CHEMICAL_URANIUM | REACTOR_FUELS):
            if recipe.recipe_id not in stages and not recipe.recipe_id.startswith("industrial_colonies:"):
                unclassified_fuel_producers.append(recipe.recipe_id)

    uranium_script = (scripts / "industrial_uranium_yellorium_separation.js").read_text(encoding="utf-8")
    yellorium_script = (scripts / "industrial_yellorium_refinement.js").read_text(encoding="utf-8")
    fuel_script = (scripts / "industrial_nuclear_fuel_01.js").read_text(encoding="utf-8")
    sulfur_script = (scripts / "industrial_sulfur_canonicalization.js").read_text(encoding="utf-8")
    all_script_text = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(scripts.glob("*.js"))
    )

    custom_steps = [
        {
            "recipe_id": "industrial_colonies:materials/yellorium/molten_alloy",
            "script": "industrial_yellorium_refinement.js",
            "type": "createmetallurgy:alloying",
            "node": "CR01 — Advanced Alloy Mixing",
            "inputs": ["createmetallurgy:molten_lead", "createmetallurgy:molten_gold"],
            "outputs": ["bigreactors:yellorium"],
            "required_tokens": ["processing_time: 160", "amount: 90", "amount: 180"],
        },
        {
            "recipe_id": "industrial_colonies:materials/yellorium/ingot_casting",
            "script": "industrial_yellorium_refinement.js",
            "type": "createmetallurgy:casting_in_table",
            "node": "CR01 — Advanced Metallurgy",
            "inputs": ["bigreactors:yellorium", "createmetallurgy:graphite_ingot_mold"],
            "outputs": ["bigreactors:yellorium_ingot"],
            "required_tokens": ["amount: 90", "processing_time: 60"],
        },
        {
            "recipe_id": "industrial_colonies:materials/yellorium_compound",
            "script": "industrial_yellorium_refinement.js",
            "type": "create:crushing",
            "node": "CR01 — Yellorium Refinement",
            "inputs": ["bigreactors:yellorium_ingot"],
            "outputs": ["industrial_colonies:yellorium_compound"],
            "required_tokens": ["count: 2"],
        },
        {
            "recipe_id": "industrial_colonies:materials/uranium/raw_from_yellorium_compound",
            "script": "industrial_uranium_yellorium_separation.js",
            "type": "mekanism:enriching",
            "node": "CR01 — Isotope Materials",
            "inputs": ["industrial_colonies:yellorium_compound"],
            "outputs": ["mekanism:raw_uranium"],
            "required_tokens": ["count: 1"],
        },
        {
            "recipe_id": "industrial_colonies:materials/uranium/osmium_compressed_ingot",
            "script": "industrial_uranium_yellorium_separation.js",
            "type": "mekanism:compressing",
            "node": "CR01 — Isotope Materials",
            "inputs": ["mekanism:dust_uranium", "mekanism:osmium"],
            "outputs": ["mekanism:ingot_uranium"],
            "required_tokens": ["per_tick_usage: true"],
        },
        {
            "recipe_id": "mekanism:processing/uranium/yellow_cake_uranium",
            "script": "industrial_uranium_yellorium_separation.js",
            "type": "mekanism:enriching",
            "node": "CR01 — Isotope Materials",
            "inputs": ["mekanism:ingot_uranium"],
            "outputs": ["mekanism:yellow_cake_uranium"],
            "required_tokens": ["count: 2"],
        },
        {
            "recipe_id": "industrial_colonies:fuel/early_nuclear/enriched_uranium_fuel_pellet",
            "script": "industrial_nuclear_fuel_01.js",
            "type": "mekanism:crystallizing",
            "node": "CR01 — Early Nuclear Fuel",
            "inputs": ["mekanism:fissile_fuel"],
            "outputs": ["industrial_colonies:enriched_uranium_fuel_pellet"],
            "required_tokens": ["amount: 1000"],
        },
    ]
    stock_steps = [
        {
            "recipe_id": "createmetallurgy:melting/lead/ingot",
            "type": "createmetallurgy:melting",
            "inputs": ["tfmg:lead_ingot"],
            "outputs": ["createmetallurgy:molten_lead"],
            "node": "material input to CR01 — Advanced Alloy Mixing",
        },
        {
            "recipe_id": "createmetallurgy:melting/gold/ingot",
            "type": "createmetallurgy:melting",
            "inputs": ["minecraft:gold_ingot"],
            "outputs": ["createmetallurgy:molten_gold"],
            "node": "material input to CR01 — Advanced Alloy Mixing",
        },
        {
            "recipe_id": "mekanism:processing/uranium/dust/from_raw_ore",
            "type": "mekanism:enriching",
            "inputs": ["mekanism:raw_uranium"],
            "outputs": ["mekanism:dust_uranium"],
            "node": "CR01 — Isotope Materials",
        },
        {
            "recipe_id": "mekanism:processing/uranium/uranium_oxide",
            "type": "mekanism:oxidizing",
            "inputs": ["mekanism:yellow_cake_uranium"],
            "outputs": ["mekanism:uranium_oxide"],
            "node": "CR01 — Uranium Processing",
        },
        {
            "recipe_id": "mekanism:processing/uranium/sulfuric_acid",
            "type": "mekanism:chemical_infusing",
            "inputs": ["mekanism:hydrofluoric_acid", "mekanism:uranium_oxide"],
            "outputs": ["mekanism:uranium_hexafluoride"],
            "node": "CR01 — Uranium Processing",
        },
        {
            "recipe_id": "mekanism:processing/uranium/fissile_fuel",
            "type": "mekanism:centrifuging",
            "inputs": ["mekanism:uranium_hexafluoride"],
            "outputs": ["mekanism:fissile_fuel"],
            "node": "CR01 — Uranium Processing",
        },
    ]

    failures: list[str] = []
    warnings: list[str] = []
    route_validation: list[dict[str, Any]] = []
    worldgen_evidence: list[dict[str, Any]] = []
    if not args.inventory_only:
        active_jars = len(list(mods_dir.glob("*.jar")))
        if len(external_jar_names) != EXPECTED_EXTERNAL_JAR_COUNT:
            failures.append(
                f"Expected the audited {EXPECTED_EXTERNAL_JAR_COUNT} external JARs, "
                f"found {len(external_jar_names)}"
            )
        if len(project_jar_names) != 1:
            failures.append(
                "Expected exactly one active Industrial Colonies JAR, found: " + " | ".join(project_jar_names)
            )
        if external_jar_inventory_sha256 != EXPECTED_EXTERNAL_JAR_INVENTORY_SHA256:
            failures.append(
                "External JAR inventory changed; re-audit required: "
                f"{external_jar_inventory_sha256} != {EXPECTED_EXTERNAL_JAR_INVENTORY_SHA256}"
            )
        if EXPECTED_BINARY_HITS_SHA256 and binary_hits_sha256 != EXPECTED_BINARY_HITS_SHA256:
            failures.append(
                "Compiled/NBT nuclear-chemistry reference inventory changed; re-audit required: "
                f"{binary_hits_sha256} != {EXPECTED_BINARY_HITS_SHA256}"
            )
        if EXPECTED_KUBEJS_OUTPUT_HITS_SHA256 and kubejs_output_hits_sha256 != EXPECTED_KUBEJS_OUTPUT_HITS_SHA256:
            failures.append(
                "Pack-owned KubeJS nuclear/acid output inventory changed; re-audit required: "
                f"{kubejs_output_hits_sha256} != {EXPECTED_KUBEJS_OUTPUT_HITS_SHA256}"
            )
        unexpected_binary_owners = sorted(
            f"{row['jar']}!{row['path']}" for row in binary_hits if row["jar"] not in AUDITED_JAR_SHA256
        )
        if unexpected_binary_owners:
            failures.append(
                "A non-audited mod contains compiled nuclear/acid route references: "
                + " | ".join(unexpected_binary_owners)
            )
        for name, expected_hash in AUDITED_JAR_SHA256.items():
            actual_hash = audited_jar_hashes.get(name)
            if actual_hash != expected_hash:
                failures.append(
                    f"Audited chemistry JAR changed or is missing: {name} ({actual_hash!r} != {expected_hash})"
                )

        missing_removals = sorted(REQUIRED_REMOVALS - removed)
        if missing_removals:
            failures.append("Required removal declarations missing: " + " | ".join(missing_removals))
        missing_rewrite_removals = sorted(EXACT_URANIUM_REWRITES - removed)
        if missing_rewrite_removals:
            failures.append(
                "Original common-tag uranium recipes were not removed before exact rewrite: "
                + " | ".join(missing_rewrite_removals)
            )
        if jar_yellorium_to_uranium:
            failures.append(
                "An unowned JAR Yellorium-to-uranium shortcut survives; the custom Isotope Materials bridge must be sole: "
                + " | ".join(sorted(set(jar_yellorium_to_uranium)))
            )
        if uranium_to_yellorium:
            failures.append(
                "Forbidden uranium/fissile/reactor-fuel -> Yellorium route survives: "
                + " | ".join(sorted(set(uranium_to_yellorium)))
            )
        if natural_yellorium_producers:
            failures.append(
                "A recipe still produces disabled natural Yellorite/raw Yellorium: "
                + " | ".join(sorted(set(natural_yellorium_producers)))
            )
        if unclassified_fuel_producers:
            failures.append(
                "Unstaged usable-fuel producer survives: "
                + " | ".join(sorted(set(unclassified_fuel_producers)))
            )
        for recipe_id, node in EXPECTED_STAGES.items():
            if stages.get(recipe_id) != node:
                failures.append(f"{recipe_id} must be staged at {node}, found {stages.get(recipe_id)!r}")

        script_by_name = {
            "industrial_yellorium_refinement.js": yellorium_script,
            "industrial_uranium_yellorium_separation.js": uranium_script,
            "industrial_nuclear_fuel_01.js": fuel_script,
        }
        for step in custom_steps:
            block = custom_recipe_block(script_by_name[step["script"]], step["recipe_id"])
            missing = [
                token
                for token in [step["type"], *step["inputs"], *step["outputs"], *step["required_tokens"]]
                if token not in block
            ]
            route_validation.append({**step, "source": "KubeJS", "missing_tokens": missing})
            if not block:
                failures.append(f"Custom route recipe is missing: {step['recipe_id']}")
            elif missing:
                failures.append(
                    f"Custom route recipe {step['recipe_id']} is incomplete: " + " | ".join(missing)
                )
            if stages.get(step["recipe_id"]) != step["node"]:
                failures.append(
                    f"Custom route recipe {step['recipe_id']} has wrong stage: {stages.get(step['recipe_id'])!r}"
                )

        for step in stock_steps:
            candidates = effective_by_id.get(step["recipe_id"], [])
            valid = []
            for candidate in candidates:
                expanded = expanded_inputs(candidate, tags)
                valid.append(
                    candidate.recipe_type == step["type"]
                    and set(step["inputs"]).issubset(expanded)
                    and set(step["outputs"]).issubset(candidate.outputs)
                )
            route_validation.append(
                {
                    **step,
                    "source": "active JAR",
                    "candidate_count": len(candidates),
                    "validated": any(valid),
                }
            )
            if not any(valid):
                failures.append(
                    f"Required active Mekanism/Create Metallurgy route is absent or changed: {step['recipe_id']}"
                )

        forbidden_recipe_id = "industrial_colonies:fuel/early_nuclear/yellorium_from_fissile_fuel"
        if forbidden_recipe_id in all_script_text or forbidden_recipe_id in stages:
            failures.append("The reversed fissile-fuel -> Yellorium project recipe still exists")
        if "mekanism:fissile_fuel" in yellorium_script:
            failures.append("The manufactured-Yellorium script references fissile fuel in the wrong direction")

        for empty_tag in (
            "c:ingots/uranium",
            "c:storage_blocks/uranium",
            "forge:storage_blocks/uranium",
        ):
            if not re.search(rf"['\"]{re.escape(empty_tag)}['\"]\s*:\s*\[\s*\]", uranium_script):
                failures.append(f"Reactor-fuel item tag is not explicitly empty: {empty_tag}")
        for token in (
            "event.removeAll('c:yellorium')",
            "event.removeAll('c:ores/yellorite')",
            "event.removeAll('c:raw_materials/yellorium')",
            "event.removeAll('c:storage_blocks/raw_yellorium')",
            "event.remove('c:raw_materials', 'bigreactors:raw_yellorium')",
            "event.remove('c:storage_blocks', 'bigreactors:raw_yellorium_block')",
        ):
            if token not in uranium_script:
                failures.append(f"Yellorite/Yellorium tag isolation token missing: {token}")
        if not all(value is True for key, value in reactor_fuel_mapping.items() if key != "jar"):
            failures.append(
                "Could not prove all audited Extreme Reactors Yellorium/uranium solid and fluid fuel mappings"
            )

        required_er_removals = {
            "c:ingots/yellorium",
            "c:ingots/uranium",
            "c:storage_blocks/yellorium",
            "c:storage_blocks/uranium",
        }
        actual_er_removals = set(project_reactor_policy["generic_source_tags_removed"])
        if not required_er_removals.issubset(actual_er_removals):
            failures.append(
                "Extreme Reactors generic fuel-source removals are incomplete: "
                + " | ".join(sorted(required_er_removals - actual_er_removals))
            )
        expected_yellorium_add = [
            {
                "SourceTagId": "industrial_colonies:reactor_fuels/enriched_uranium",
                "ProductName": "yellorium",
                "ProductQuantity": 1000,
            }
        ]
        if project_reactor_policy["yellorium_source_additions"] != expected_yellorium_add:
            failures.append("The dedicated enriched pellet is not the sole project-added first-tier reactor source")
        pellet_tag = project_reactor_policy["pellet_tag"]
        if pellet_tag.get("replace") is not True or pellet_tag.get("values") != [
            "industrial_colonies:enriched_uranium_fuel_pellet"
        ]:
            failures.append("The enriched uranium reactor-fuel tag contains anything except the dedicated pellet")

        for tag, values in CANONICAL_ITEM_TAGS.items():
            owner = sulfur_script if "sulfur" in tag else uranium_script
            if tag not in owner:
                failures.append(f"Canonical item tag policy does not mention {tag}")
            for value in values:
                if value not in owner:
                    failures.append(f"Canonical tag value missing from script: {tag} -> {value}")
        for tag, values in CANONICAL_FLUID_TAGS.items():
            owner = uranium_script if tag == "c:yellorium" else sulfur_script
            if tag not in owner:
                failures.append(f"Canonical fluid tag policy does not mention {tag}")
            for value in values:
                if value not in owner:
                    failures.append(f"Canonical fluid value missing from script: {tag} -> {value}")
        for recipe_id in EXACT_URANIUM_REWRITES:
            if recipe_id not in uranium_script:
                failures.append(f"Exact-input uranium rewrite missing: {recipe_id}")

        for recipe in effective:
            recipe_id = recipe.recipe_id
            must_be_staged = (
                recipe_id.startswith("mekanism:processing/uranium/")
                or (recipe_id.startswith("create:") and "uranium" in recipe_id)
                or recipe_id
                in {
                    "mekanism:rotary/uranium_hexafluoride",
                    "mekanism:rotary/uranium_oxide",
                    "bigreactors:crafting/yellorium_component_to_storage",
                    "bigreactors:crafting/yellorium_storage_to_component",
                    "tfmg:vat_machine_recipe/sulfuric_acid",
                }
            )
            if must_be_staged and recipe_id not in stages:
                failures.append(f"Nuclear/acid processing recipe has no exact research stage: {recipe_id}")

        feature_specs = {
            "src/main/resources/data/bigreactors/neoforge/biome_modifier/yellorite.json": "bigreactors:yellorite_ore",
            "src/main/resources/data/bigreactors/neoforge/biome_modifier/yellorite_deepslate.json": "bigreactors:yellorite_deepslate_ore",
            "src/main/resources/data/industrial_colonies/neoforge/biome_modifier/remove_yellorite_overworld.json": "bigreactors:yellorite_ore",
            "src/main/resources/data/industrial_colonies/neoforge/biome_modifier/remove_yellorite_deepslate_overworld.json": "bigreactors:yellorite_deepslate_ore",
        }
        for relative, feature in feature_specs.items():
            path = project / relative
            data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
            valid = (
                data.get("type") == "neoforge:remove_features"
                and data.get("biomes") == "#minecraft:is_overworld"
                and data.get("features") == feature
                and data.get("step") == "underground_ores"
            )
            worldgen_evidence.append({"resource": relative, "feature": feature, "valid": valid})
            if not valid:
                failures.append(f"Safe remove_features Yellorite override is missing or malformed: {relative}")
        unsafe_tag = (
            project
            / "src/main/resources/data/industrial_colonies/tags/worldgen/biome/no_yellorite_worldgen.json"
        )
        if unsafe_tag.exists():
            failures.append("Unsafe empty-biome-tag Yellorite override still exists (empty means wildcard in ER)")
        for relative in (
            "src/main/resources/data/bigreactors/loot_table/blocks/yellorite_ore.json",
            "src/main/resources/data/bigreactors/loot_table/blocks/deepslate_yellorite_ore.json",
            "src/main/resources/data/bigreactors/loot_table/blocks/raw_yellorium_block.json",
        ):
            path = project / relative
            data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
            refs = set(strings(data))
            valid = data.get("type") == "minecraft:block" and not refs & NATURAL_YELLORIUM
            worldgen_evidence.append({"resource": relative, "natural_yellorium_removed": valid})
            if not valid:
                failures.append(f"Yellorite block loot is not disabled: {relative}")

        allowed_sensitive_loot = {
            "data/bigreactors/loot_table/blocks/yellorite_ore.json",
            "data/bigreactors/loot_table/blocks/deepslate_yellorite_ore.json",
            "data/bigreactors/loot_table/blocks/raw_yellorium_block.json",
            "data/bigreactors/loot_table/blocks/yellorium_block.json",
            "data/mekanism/loot_table/blocks/block_uranium.json",
        }
        sensitive_nonrecipe_paths: list[str] = []
        sensitive_nonrecipe_values = (
            NATURAL_YELLORIUM | PHYSICAL_URANIUM | CHEMICAL_URANIUM | REACTOR_FUELS | SULFUR_ACIDS
        )
        for record in nonrecipe_hits:
            path = record["path"]
            if not re.search(r"(?:loot_table|trades?|structures?)/", path):
                continue
            if not set(record["refs"]) & sensitive_nonrecipe_values:
                continue
            if path not in allowed_sensitive_loot:
                sensitive_nonrecipe_paths.append(f"{record['jar']}!{path}")
        if sensitive_nonrecipe_paths:
            failures.append(
                "Usable nuclear fuel, natural Yellorite, or acid appears in loot/trade/structure data: "
                + " | ".join(sorted(sensitive_nonrecipe_paths))
            )

        assignments = json.loads(
            (project / "progression/machine_node_assignments.json").read_text(encoding="utf-8")
        )["nodes"]
        if assignments["CR01 — Early Nuclear Fuel"].get("unlocks") != [
            "industrial_colonies:enriched_uranium_fuel_pellet"
        ]:
            failures.append("Early Nuclear Fuel unlocks anything other than the dedicated enriched pellet")
        if assignments["CR01 — Early Nuclear Fuel"].get("icon") != (
            "industrial_colonies:enriched_uranium_fuel_pellet"
        ):
            failures.append("Early Nuclear Fuel still advertises a Yellorium-alloy icon")
        if assignments["CR01 — Yellorium Refinement"].get("icon") != (
            "industrial_colonies:yellorium_compound"
        ):
            failures.append("Yellorium Refinement still advertises disabled natural Yellorite")
        forbidden_yellorite_unlocks = NATURAL_YELLORIUM & set(
            assignments["CR01 — Yellorium Refinement"].get("unlocks", [])
        )
        if forbidden_yellorite_unlocks:
            failures.append(
                "Yellorium Refinement still advertises disabled natural resources: "
                + " | ".join(sorted(forbidden_yellorite_unlocks))
            )
        costs = json.loads((project / "progression/research_costs.json").read_text(encoding="utf-8"))["nodes"]
        criticality_cost = costs["CR01 — First Criticality"]["costs"]
        if {"item": "industrial_colonies:enriched_uranium_fuel_pellet", "count": 12} not in criticality_cost:
            failures.append("First Criticality does not require twelve 1,000-unit enriched fuel pellets")
        metallurgy_cost_items = {
            row["item"] for row in costs["CR01 — Advanced Metallurgy"]["costs"]
        }
        if metallurgy_cost_items != {
            "createmetallurgy:foundry_basin",
            "createmetallurgy:foundry_lid",
            "createmetallurgy:foundry_mixer",
        }:
            failures.append("Advanced Metallurgy cost does not prove the reachable parent-node foundry line")

        mixin_metadata = json.loads(
            (project / "src/main/resources/industrial_colonies.mixins.json").read_text(encoding="utf-8")
        )
        for mixin in ("FoundryMixerBlockEntityMixin", "CastingBlockEntityMixin"):
            source = project / f"src/main/java/dev/godpc/industrialcolonies/mixin/{mixin}.java"
            if mixin not in mixin_metadata.get("mixins", []) or not source.exists():
                failures.append(f"Create Metallurgy exact-stage runtime enforcement is missing: {mixin}")
            elif "CreateRecipeStageGate.canUse" not in source.read_text(encoding="utf-8"):
                failures.append(f"Create Metallurgy mixin does not call the shared stage gate: {mixin}")

        surviving_acid = {
            row["recipe_id"]
            for row in acid_producers
            if row["conditions_active"] and not row["removed"]
        }
        if surviving_acid != {"tfmg:vat_machine_recipe/sulfuric_acid"}:
            failures.append(
                "Unexpected active JAR sulfuric-acid producers: " + " | ".join(sorted(surviving_acid))
            )
        for token in (
            "industrial_colonies:sulfur/tfmg_acid_rotary_bridge",
            "industrial_colonies:sulfur/migrate_mekanism_acid",
            "fluid_input: { amount: 1, tag: 'c:sulfuric_acid' }",
            "fluid_input: { amount: 1, tag: 'industrial_colonies:legacy_mekanism_sulfuric_acid' }",
            "fluid_output: { amount: 1, id: 'tfmg:sulfuric_acid' }",
            "chemical_input: { amount: 1, chemical: 'mekanism:sulfuric_acid' }",
            "chemical_output: { amount: 1, id: 'mekanism:sulfuric_acid' }",
        ):
            if token not in sulfur_script:
                failures.append(f"Controlled sulfuric-acid bridge token missing: {token}")

    report = {
        "pack": str(args.instance.resolve()),
        "project": str(project),
        "active_jars": len(list(mods_dir.glob("*.jar"))),
        "jar_inventory_sha256": jar_inventory_sha256,
        "external_jars": len(external_jar_names),
        "external_jar_inventory_sha256": external_jar_inventory_sha256,
        "industrial_colonies_jars": project_jar_names,
        "audited_jar_sha256": audited_jar_hashes,
        "extreme_reactors_default_fuel_mapping_evidence": reactor_fuel_mapping,
        "project_reactor_fuel_policy": project_reactor_policy,
        "binary_reference_hits_sha256": binary_hits_sha256,
        "binary_reference_hits": binary_hits,
        "kubejs_sensitive_output_hits_sha256": kubejs_output_hits_sha256,
        "kubejs_sensitive_output_hits": kubejs_output_hits,
        "installed_mod_ids": sorted(installed),
        "recipes_scanned": len(recipes),
        "active_recipes_after_conditions_and_removals": len(effective),
        "scripted_recipe_removals": len(removed),
        "canonical_runtime_tags": {
            "item": {tag: sorted(values) for tag, values in CANONICAL_ITEM_TAGS.items()},
            "fluid": {tag: sorted(values) for tag, values in CANONICAL_FLUID_TAGS.items()},
        },
        "before_path_removed": (
            "Natural Yellorite/raw Yellorium or furnace/Create/foundry conversion -> uranium/Yellorium fuel"
        ),
        "after_path_required": (
            "lead+gold -> Create Metallurgy Yellorium alloy -> cast ingot -> refined compound -> "
            "Mekanism raw uranium -> Enrichment Chamber dust -> Osmium Compressor ingot -> "
            "Yellow Cake -> uranium oxide -> UF6 -> Isotopic Centrifuge fissile fuel -> enriched pellet"
        ),
        "route_validation": route_validation,
        "worldgen_and_loot_boundary": worldgen_evidence,
        "relevant_recipes": sorted(relevant_recipes, key=lambda row: (row["recipe_id"], row["jar"])),
        "acid_producers": sorted(acid_producers, key=lambda row: (row["recipe_id"], row["jar"])),
        "uranium_tag_consumers_after_runtime_override": sorted(set(uranium_tag_consumers)),
        "unowned_jar_yellorium_to_uranium_survivors": sorted(set(jar_yellorium_to_uranium)),
        "uranium_or_fuel_to_yellorium_survivors": sorted(set(uranium_to_yellorium)),
        "natural_yellorium_recipe_producers": sorted(set(natural_yellorium_producers)),
        "unclassified_fuel_producers": sorted(set(unclassified_fuel_producers)),
        "nonrecipe_keyword_hits": nonrecipe_hits,
        "archive_errors": archive_errors,
        "warnings": warnings,
        "failures": failures,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        f"Scanned {report['active_jars']} JARs, {report['recipes_scanned']} recipes, "
        f"and {len(nonrecipe_hits)} relevant non-recipe resources."
    )
    print(
        f"Found {len(relevant_recipes)} material routes, {len(acid_producers)} acid producer definitions, "
        f"and validated {len(route_validation)} canonical route steps."
    )
    print(f"Binary inventory fingerprint: {binary_hits_sha256}")
    print(f"KubeJS output fingerprint: {kubejs_output_hits_sha256}")
    if args.inventory_only:
        print("INVENTORY: policy enforcement skipped.")
        return 0
    if failures:
        print(f"FAIL: {len(failures)} boundary issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: Yellorium flows only forward into staged Mekanism enrichment and dedicated reactor fuel.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
