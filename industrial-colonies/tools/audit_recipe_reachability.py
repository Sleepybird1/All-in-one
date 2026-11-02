from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


RESOURCE_LOCATION = re.compile(r"^#?[a-z0-9_.-]+:[a-z0-9_./-]+$")
RECIPE_PATH = re.compile(r"^data/([^/]+)/(?:recipe|recipes)/(.+)\.json$")
TAG_PATH = re.compile(r"^data/([^/]+)/tags/(item|items|block|blocks|fluid|fluids)/(.+)\.json$")
CHEMICAL_TAG_PATH = re.compile(r"^data/([^/]+)/tags/mekanism/chemical/(.+)\.json$")
LOOT_PATH = re.compile(r"^data/([^/]+)/(?:loot_table|loot_tables)/(.+)\.json$")
CONFIGURED_FEATURE_PATH = re.compile(r"^data/([^/]+)/worldgen/configured_feature/(.+)\.json$")
MODEL_PATH = re.compile(r"^assets/([^/]+)/models/(item|block)/(.+)\.json$")

INPUT_KEYS = {
    "ingredient", "ingredients", "input", "inputs", "item_input", "fluid_input",
    "chemical_input", "main_input", "secondary_input", "left_input", "right_input",
    "template", "base", "addition", "catalyst", "tool", "materials", "fluid", "waste",
    "cast", "pattern_item", "input_items", "ingredient1", "ingredient2", "ammo",
    "input_cell", "input_component", "cell", "upgrade_item", "container", "bottle",
    "terminal", "terminala", "terminalb", "components", "extra_materials",
}
OUTPUT_KEYS = {
    "result", "results", "output", "outputs", "item_output", "fluid_output",
    "chemical_output", "primary_output", "secondary_output", "main_output",
    "byproduct", "byproducts", "result_cell", "result_component", "upgraded_block",
    "cell_disassembly_items", "adult_result",
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
CATEGORY_PRIORITY = {
    "nuclear_reverse_conversion": 0,
    "missing_yellorium_to_uranium_route": 1,
    "yellorium_not_an_alloy": 2,
    "advanced_alloy_mixing_gate_set": 3,
    "non_mekanism_raw_uranium_processing": 3,
    "reactor_fuel_tag_bypass": 4,
    "staged_recipe_missing": 5,
    "recipe_input_unparsed": 5,
    "recipe_output_unparsed": 5,
    "unreachable_owned_output": 6,
    "blocked_owned_output": 7,
    "not_reachable_at_intended_stage": 8,
    "early_unlock_bypass": 9,
    "downstream_owned_ingredient": 10,
    "removed_without_replacement": 11,
    "unknown_seed_only": 12,
    "cross_mod_tag_alias_review": 13,
    "intentional_loot_bootstrap": 14,
}
DRAWIO_SHA256 = "d941f52c1bdd8e0ab2fd30011a48b339abc526524cb6a3e314493e60a59560b5"

# These scripts deliberately retire stock/deprecated routes as part of a
# documented replacement progression. A removed output is not necessarily
# supposed to remain obtainable: raw ATM ores, compressed ATM ore blocks,
# uranium/Yellorium shortcuts, and obsolete machine-construction components
# are all intentionally absent. Keep those records in the evidence table,
# but do not report them as unexplained recipe loss.
INTENTIONAL_RETIREMENT_SCRIPTS = {
    "industrial_allthemodium_currency.js",
    "industrial_early_electricity_construction.js",
    "industrial_metallurgy_casting_compat.js",
    "industrial_nuclear_actinides_01.js",
    "industrial_nuclear_fuel_01.js",
    "industrial_uranium_yellorium_separation.js",
}


@dataclass
class Resource:
    kind: str
    resource_id: str
    tag: bool = False

    @property
    def key(self) -> str:
        return f"{'tag:' if self.tag else ''}{self.kind}:{self.resource_id}"


@dataclass
class Recipe:
    recipe_id: str
    recipe_type: str
    source: str
    source_kind: str
    data: dict[str, Any]
    inputs: list[list[Resource]] = field(default_factory=list)
    outputs: list[Resource] = field(default_factory=list)
    machine_requirements: list[str] = field(default_factory=list)
    stage: str | None = None
    condition_state: str = "active"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalize_kind(value: str) -> str:
    return {"items": "item", "blocks": "block", "fluids": "fluid"}.get(value, value)


def normalize_resource(value: Any, kind_hint: str = "item") -> Resource | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if value.startswith("#"):
        value = value[1:]
        tag = True
    else:
        tag = False
    if not RESOURCE_LOCATION.match(value):
        return None
    return Resource(kind_hint, value, tag)


def resources_in(node: Any, kind_hint: str = "item") -> list[Resource]:
    found: list[Resource] = []
    if isinstance(node, str):
        resource = normalize_resource(node, kind_hint)
        if resource:
            found.append(resource)
        return found
    if isinstance(node, list):
        for value in node:
            found.extend(resources_in(value, kind_hint))
        return unique_resources(found)
    if not isinstance(node, dict):
        return found

    direct = False
    if "item" in node:
        direct = True
        found.extend(resources_in(node["item"], "item"))
    if "tag" in node:
        direct = True
        tag_value = node["tag"]
        if isinstance(tag_value, str):
            found.append(Resource(kind_hint, tag_value.lstrip("#"), True))
    if "fluid" in node:
        direct = True
        found.extend(resources_in(node["fluid"], "fluid"))
    if "chemical" in node:
        direct = True
        found.extend(resources_in(node["chemical"], "chemical"))
    if "id" in node:
        direct = True
        found.extend(resources_in(node["id"], kind_hint))
    if "value" in node and isinstance(node.get("value"), str):
        value = str(node["value"])
        if RESOURCE_LOCATION.match(value.lstrip("#")):
            direct = True
            found.extend(resources_in(value, kind_hint))

    if not direct:
        for key, value in node.items():
            lower = key.lower()
            child_kind = "fluid" if "fluid" in lower else "chemical" if "chemical" in lower else kind_hint
            found.extend(resources_in(value, child_kind))
    return unique_resources(found)


def unique_resources(resources: Iterable[Resource]) -> list[Resource]:
    seen: set[str] = set()
    result: list[Resource] = []
    for resource in resources:
        if resource.key not in seen:
            seen.add(resource.key)
            result.append(resource)
    return result


def loot_item_ids(node: Any) -> set[str]:
    """Return actual item entry names, excluding conditions/functions/random-sequence ids."""
    found: set[str] = set()
    if isinstance(node, list):
        for value in node:
            found.update(loot_item_ids(value))
    elif isinstance(node, dict):
        if node.get("type") == "minecraft:item":
            name = node.get("name")
            if isinstance(name, str) and RESOURCE_LOCATION.match(name):
                found.add(name)
        for value in node.values():
            found.update(loot_item_ids(value))
    return found


def configured_feature_blocks(node: Any) -> set[str]:
    """Collect block states selected by configured world-generation features."""
    found: set[str] = set()
    if isinstance(node, list):
        for value in node:
            found.update(configured_feature_blocks(value))
    elif isinstance(node, dict):
        name = node.get("Name")
        if isinstance(name, str) and RESOURCE_LOCATION.match(name):
            found.add(name)
        for value in node.values():
            found.update(configured_feature_blocks(value))
    return found


def input_groups(data: dict[str, Any], recipe_type: str) -> list[list[Resource]]:
    groups: list[list[Resource]] = []

    def add(value: Any, hint: str = "item") -> None:
        values = resources_in(value, hint)
        if values:
            groups.append(values)

    # Many mods wrap the vanilla shaped codec under their own serializer ID
    # (Mekanism mek_data, CC impostor_shaped, sophisticated upgrades, etc.).
    # A top-level key map plus pattern is a stable structural signature.
    if isinstance(data.get("key"), dict) and isinstance(data.get("pattern"), list):
        for value in (data.get("key") or {}).values():
            add(value)
        return dedupe_groups(groups)
    if recipe_type == "minecraft:crafting_shapeless":
        for value in data.get("ingredients", []):
            add(value)
        return dedupe_groups(groups)
    # The pack's Encased recipe serializers are intentionally drop-in wrappers
    # around Create's Sequenced Assembly codec. Treat them as such here so the
    # deployed components remain part of the physical dependency graph.
    if recipe_type == "create:sequenced_assembly" or (
        recipe_type.startswith("industrial_colonies:")
        and recipe_type.endswith("_sequenced_assembly")
    ):
        add(data.get("ingredient"))
        transitional_value = data.get("transitional_item", data.get("transitionalItem"))
        transitional = {r.key for r in resources_in(transitional_value)}
        for step in data.get("sequence", []):
            if not isinstance(step, dict):
                continue
            for value in step.get("ingredients", []):
                resources = [r for r in resources_in(value) if r.key not in transitional]
                if resources:
                    groups.append(resources)
        return dedupe_groups(groups)

    for key, value in data.items():
        lower = key.lower().replace("-", "_")
        if lower in INPUT_KEYS or lower.endswith("_input"):
            hint = "fluid" if "fluid" in lower else "chemical" if "chemical" in lower else "item"
            if lower == "fluid":
                hint = "fluid"
            if lower in {"ingredients", "inputs"} and isinstance(value, list):
                for entry in value:
                    add(entry, hint)
            else:
                add(value, hint)
    return dedupe_groups(groups)


def output_resources(data: dict[str, Any], recipe_type: str) -> list[Resource]:
    outputs: list[Resource] = []
    for key, value in data.items():
        lower = key.lower().replace("-", "_")
        if lower in OUTPUT_KEYS or lower.endswith("_output"):
            hint = "fluid" if "fluid" in lower else "chemical" if "chemical" in lower else "item"
            values = value if isinstance(value, list) else [value]
            for entry in values:
                entry_hint = hint
                if entry_hint == "item" and isinstance(entry, dict) and "amount" in entry and "count" not in entry:
                    # 1.21 machine serializers use `count` for items and `amount`
                    # for fluids/chemicals, while both commonly encode the result
                    # registry id as `id`. Resolve that ambiguity deterministically.
                    if recipe_type.startswith("mekanism:"):
                        entry_hint = "chemical"
                    else:
                        entry_hint = "fluid"
                outputs.extend(resources_in(entry, entry_hint))
    return unique_resources(outputs)


def dedupe_groups(groups: list[list[Resource]]) -> list[list[Resource]]:
    seen: set[tuple[str, ...]] = set()
    result: list[list[Resource]] = []
    for group in groups:
        signature = tuple(sorted(resource.key for resource in group))
        if signature and signature not in seen:
            seen.add(signature)
            result.append(group)
    return result


MACHINE_REQUIREMENTS: list[tuple[str, str]] = [
    ("create:milling", "create:millstone"),
    ("create:crushing", "create:crushing_wheel"),
    ("create:pressing", "create:mechanical_press"),
    ("create:compacting", "create:mechanical_press"),
    ("create:mixing", "create:mechanical_mixer"),
    ("create:cutting", "create:mechanical_saw"),
    ("create:splashing", "create:encased_fan"),
    ("create:haunting", "create:encased_fan"),
    ("create:smoking", "create:encased_fan"),
    ("create:filling", "create:spout"),
    ("create:mechanical_crafting", "create:mechanical_crafter"),
    ("create:sequenced_assembly", "create:deployer"),
    ("ae2:inscriber", "ae2:inscriber"),
    ("ae2:charger", "ae2:charger"),
    ("extendedae:circuit_cutter", "extendedae:circuit_cutter"),
    ("extendedae:crystal_assembler", "extendedae:crystal_assembler"),
    ("extendedae:crystal_fixer", "extendedae:crystal_fixer"),
    ("advanced_ae:reaction", "advanced_ae:reaction_chamber"),
    ("mekanism:enriching", "mekanism:enrichment_chamber"),
    ("mekanism:crushing", "mekanism:crusher"),
    ("mekanism:sawing", "mekanism:precision_sawmill"),
    ("mekanism:metallurgic_infusing", "mekanism:metallurgic_infuser"),
    ("mekanism:smelting", "mekanism:energized_smelter"),
    ("mekanism:combining", "mekanism:combiner"),
    ("mekanism:purifying", "mekanism:purification_chamber"),
    ("mekanism:injecting", "mekanism:chemical_injection_chamber"),
    ("mekanism:dissolution", "mekanism:chemical_dissolution_chamber"),
    ("mekanism:washing", "mekanism:chemical_washer"),
    ("mekanism:crystallizing", "mekanism:chemical_crystallizer"),
    ("mekanism:oxidizing", "mekanism:chemical_oxidizer"),
    ("mekanism:activating", "mekanism:solar_neutron_activator"),
    ("mekanism:compressing", "mekanism:osmium_compressor"),
    ("mekanism:separating", "mekanism:electrolytic_separator"),
    ("mekanism:rotary", "mekanism:rotary_condensentrator"),
    ("mekanism:chemical_infusing", "mekanism:chemical_infuser"),
    ("mekanism:reaction", "mekanism:pressurized_reaction_chamber"),
    ("mekanism:nucleosynthesizing", "mekanism:antiprotonic_nucleosynthesizer"),
    ("mekanism:centrifuging", "mekanism:isotopic_centrifuge"),
    ("tfmg:vat_machine_recipe", "tfmg:cast_iron_chemical_vat"),
    ("tfmg:industrial_mixing", "tfmg:industrial_mixer"),
    ("tfmg:industrial_blasting", "tfmg:blast_stove"),
    ("tfmg:winding", "tfmg:winding_machine"),
    ("tfmg:polarizing", "tfmg:polarizer"),
    ("tfmg:distillation", "tfmg:steel_distillation_controller"),
    ("tfmg:coking", "tfmg:coke_oven"),
    ("tfmg:casting", "tfmg:casting_basin"),
    ("tfmg:hot_blast", "tfmg:blast_stove"),
    ("createmetallurgy:melting", "createmetallurgy:industrial_crucible"),
    ("createmetallurgy:alloying", "createmetallurgy:foundry_mixer"),
    ("createmetallurgy:casting_in_table", "createmetallurgy:casting_table"),
    ("createmetallurgy:casting_in_basin", "createmetallurgy:casting_basin"),
    ("createmetallurgy:grinding", "createmetallurgy:mechanical_belt_grinder"),
    ("createmetallurgy:bulk_melting", "create:encased_fan"),
    ("bigreactors:reprocessor", "bigreactors:reprocessorcontroller"),
    ("bigreactors:fluidizer", "bigreactors:fluidizer_controller"),
]


def machine_requirements(data: dict[str, Any], recipe_type: str) -> list[str]:
    requirements = [machine for prefix, machine in MACHINE_REQUIREMENTS if recipe_type.startswith(prefix)]
    tiered_sequence = (
        recipe_type.startswith("industrial_colonies:")
        and recipe_type.endswith("_sequenced_assembly")
    )
    tiered_mechanical = (
        recipe_type.startswith("industrial_colonies:")
        and recipe_type.endswith("_mechanical_crafting")
    )
    if tiered_sequence:
        requirements.append("create:deployer")
    if tiered_mechanical:
        requirements.append("create:mechanical_crafter")
    if recipe_type == "create:sequenced_assembly" or tiered_sequence:
        for step in data.get("sequence", []):
            if isinstance(step, dict):
                step_type = str(step.get("type", ""))
                requirements.extend(machine for prefix, machine in MACHINE_REQUIREMENTS if step_type.startswith(prefix))
    return sorted(set(requirements))


def parse_mod_ids(archive: zipfile.ZipFile, jar_name: str) -> set[str]:
    ids: set[str] = set()
    for metadata in ("META-INF/neoforge.mods.toml", "META-INF/mods.toml"):
        try:
            text = archive.read(metadata).decode("utf-8-sig", errors="replace")
        except KeyError:
            continue
        ids.update(re.findall(r'(?m)^\s*modId\s*=\s*["\']([^"\']+)["\']', text))
    if not ids:
        ids.add(jar_name.rsplit(".jar", 1)[0].split("-")[0].lower())
    return ids


def condition_state(
    data: dict[str, Any], installed_mods: set[str],
    tags: dict[tuple[str, str], list[str]] | None = None,
) -> str:
    conditions = data.get("neoforge:conditions", data.get("conditions"))
    if not conditions:
        return "active"

    unknown = False

    def evaluate(condition: Any) -> bool | None:
        nonlocal unknown
        if not isinstance(condition, dict):
            unknown = True
            return None
        ctype = str(condition.get("type", condition.get("condition", "")))
        if ctype.endswith("mod_loaded"):
            return str(condition.get("modid", condition.get("mod", ""))) in installed_mods
        if ctype.endswith("tag_empty") or ctype.endswith("tag_filled"):
            if tags is None:
                unknown = True
                return None
            tag_id = str(condition.get("tag", "")).lstrip("#")
            registry = normalize_kind(str(condition.get("registry", "item")))
            seen: set[str] = set()
            frontier = [tag_id]
            members: set[str] = set()
            while frontier:
                current = frontier.pop()
                if current in seen:
                    continue
                seen.add(current)
                for value in tags.get((registry, current), []):
                    if value.startswith("#"):
                        frontier.append(value[1:])
                    else:
                        members.add(value)
            filled = bool(members)
            return filled if ctype.endswith("tag_filled") else not filled
        if ctype.endswith(":not"):
            value = evaluate(condition.get("value", condition.get("condition")))
            return None if value is None else not value
        if ctype.endswith(":and"):
            values = [evaluate(value) for value in condition.get("values", condition.get("conditions", []))]
            if any(value is False for value in values):
                return False
            return None if any(value is None for value in values) else True
        if ctype.endswith(":or"):
            values = [evaluate(value) for value in condition.get("values", condition.get("conditions", []))]
            if any(value is True for value in values):
                return True
            return None if any(value is None for value in values) else False
        unknown = True
        return None

    values = conditions if isinstance(conditions, list) else [conditions]
    evaluations = [evaluate(value) for value in values]
    if any(value is False for value in evaluations):
        return "inactive"
    return "active_unknown_condition" if unknown or any(value is None for value in evaluations) else "active"


def select_conditional_recipe(
    data: dict[str, Any], installed_mods: set[str], condition_flags: dict[str, bool],
) -> tuple[dict[str, Any], int | None]:
    """Resolve Forge/NeoForge conditional wrappers against verified live flags."""
    if str(data.get("type", "")) not in {"forge:conditional", "neoforge:conditional"}:
        return data, None

    def evaluate(condition: Any) -> bool | None:
        if not isinstance(condition, dict):
            return None
        condition_type = str(condition.get("type", condition.get("condition", "")))
        if condition_type in condition_flags:
            return condition_flags[condition_type]
        if condition_type.endswith("mod_loaded"):
            return str(condition.get("modid", condition.get("mod", ""))) in installed_mods
        if condition_type.endswith(":not"):
            value = evaluate(condition.get("value", condition.get("condition")))
            return None if value is None else not value
        if condition_type.endswith(":and"):
            values = [evaluate(value) for value in condition.get("values", condition.get("conditions", []))]
            if any(value is False for value in values):
                return False
            return None if any(value is None for value in values) else True
        if condition_type.endswith(":or"):
            values = [evaluate(value) for value in condition.get("values", condition.get("conditions", []))]
            if any(value is True for value in values):
                return True
            return None if any(value is None for value in values) else False
        return None

    for index, branch in enumerate(data.get("recipes", [])):
        if not isinstance(branch, dict) or not isinstance(branch.get("recipe"), dict):
            continue
        conditions = branch.get("conditions", [])
        conditions = conditions if isinstance(conditions, list) else [conditions]
        values = [evaluate(condition) for condition in conditions]
        if all(value is True for value in values):
            return branch["recipe"], index
    return data, None


def scan_jars(
    mods_dir: Path, vanilla_jar: Path | None = None,
    condition_flags: dict[str, bool] | None = None,
) -> dict[str, Any]:
    recipe_definitions: list[Recipe] = []
    tags: dict[tuple[str, str], list[tuple[bool, list[str]]]] = defaultdict(list)
    loot_sources: dict[str, set[str]] = defaultdict(set)
    block_loot_drops: dict[str, set[str]] = defaultdict(set)
    worldgen_blocks: set[str] = set()
    registry_models: set[str] = set()
    installed_mods: set[str] = set()
    jars: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    selected_conditional_recipes: list[dict[str, Any]] = []
    condition_flags = condition_flags or {}

    mod_jar_paths = sorted(mods_dir.glob("*.jar"), key=lambda value: value.name.lower())
    jar_paths = ([vanilla_jar] if vanilla_jar and vanilla_jar.exists() else []) + mod_jar_paths
    for jar_path in jar_paths:
        jar_record = {
            "name": jar_path.name,
            "sha256": sha256(jar_path),
            "kind": "vanilla" if vanilla_jar and jar_path == vanilla_jar else "mod",
        }
        jars.append(jar_record)
        try:
            with zipfile.ZipFile(jar_path) as archive:
                installed_mods.update(parse_mod_ids(archive, jar_path.name))
        except Exception as exc:
            errors.append({"jar": jar_path.name, "path": "<archive>", "error": str(exc)})

    for jar_path in jar_paths:
        try:
            with zipfile.ZipFile(jar_path) as archive:
                for name in sorted(archive.namelist()):
                    model = MODEL_PATH.match(name)
                    if model:
                        registry_models.add(f"{model.group(1)}:{model.group(3)}")
                        continue
                    tag_match = TAG_PATH.match(name)
                    chemical_tag_match = CHEMICAL_TAG_PATH.match(name)
                    recipe_match = RECIPE_PATH.match(name)
                    loot_match = LOOT_PATH.match(name)
                    worldgen_match = CONFIGURED_FEATURE_PATH.match(name)
                    if not tag_match and not chemical_tag_match and not recipe_match and not loot_match and not worldgen_match:
                        continue
                    try:
                        data = json.loads(archive.read(name).decode("utf-8-sig"))
                    except Exception as exc:
                        errors.append({"jar": jar_path.name, "path": name, "error": str(exc)})
                        continue
                    if (tag_match or chemical_tag_match) and isinstance(data, dict):
                        if chemical_tag_match:
                            registry = "chemical"
                            tag_id = f"{chemical_tag_match.group(1)}:{chemical_tag_match.group(2)}"
                        else:
                            registry = normalize_kind(tag_match.group(2))
                            tag_id = f"{tag_match.group(1)}:{tag_match.group(3)}"
                        values: list[str] = []
                        for value in data.get("values", []):
                            if isinstance(value, dict):
                                value = value.get("id")
                            if isinstance(value, str) and RESOURCE_LOCATION.match(value):
                                values.append(value)
                        tags[(registry, tag_id)].append((bool(data.get("replace", False)), values))
                    elif recipe_match and isinstance(data, dict):
                        recipe_id = f"{recipe_match.group(1)}:{recipe_match.group(2)}"
                        selected_data, branch_index = select_conditional_recipe(data, installed_mods, condition_flags)
                        recipe_type = str(selected_data.get("type", "unknown:unknown"))
                        state = condition_state(selected_data, installed_mods)
                        source = f"{jar_path.name}!/{name}"
                        if branch_index is not None:
                            source += f"#conditional_branch_{branch_index}"
                            selected_conditional_recipes.append({
                                "recipe_id": recipe_id,
                                "wrapper_type": data.get("type"),
                                "selected_branch": branch_index,
                                "selected_recipe_type": recipe_type,
                                "source": source,
                            })
                        recipe_definitions.append(Recipe(
                            recipe_id=recipe_id,
                            recipe_type=recipe_type,
                            source=source,
                            source_kind="jar",
                            data=selected_data,
                            inputs=input_groups(selected_data, recipe_type),
                            outputs=output_resources(selected_data, recipe_type),
                            machine_requirements=machine_requirements(selected_data, recipe_type),
                            condition_state=state,
                        ))
                    elif loot_match and isinstance(data, dict):
                        loot_path = loot_match.group(2)
                        loot_parts = loot_path.split("/", 1)
                        loot_kind = loot_parts[0]
                        source_path = loot_parts[1] if len(loot_parts) > 1 else loot_path
                        source_id = f"{loot_match.group(1)}:{source_path}"
                        for item_id in loot_item_ids(data):
                            loot_sources[item_id].add(f"{loot_kind}:{source_id}")
                            if loot_kind == "blocks":
                                block_loot_drops[source_id].add(item_id)
                    elif worldgen_match and isinstance(data, dict):
                        worldgen_blocks.update(configured_feature_blocks(data))
        except Exception as exc:
            errors.append({"jar": jar_path.name, "path": "<archive>", "error": str(exc)})

    merged_tags: dict[tuple[str, str], list[str]] = {}
    for key, layers in tags.items():
        values: list[str] = []
        for replace, additions in layers:
            if replace:
                values = []
            for value in additions:
                if value not in values:
                    values.append(value)
        merged_tags[key] = values

    # Resolve tag-dependent recipe conditions only after every JAR tag layer is
    # merged. Treating an unknown nested condition as boolean true under `not`
    # would otherwise incorrectly deactivate valid recipes.
    for recipe in recipe_definitions:
        recipe.condition_state = condition_state(recipe.data, installed_mods, merged_tags)

    return {
        "definitions": recipe_definitions,
        "tags": merged_tags,
        "loot_sources": loot_sources,
        "block_loot_drops": block_loot_drops,
        "worldgen_blocks": worldgen_blocks,
        "registry_models": registry_models,
        "installed_mods": installed_mods,
        "jars": jars,
        "errors": errors,
        "selected_conditional_recipes": selected_conditional_recipes,
    }


def find_node(project: Path, explicit: Path | None) -> Path:
    if explicit:
        return explicit
    candidates = [
        shutil.which("node"),
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    raise FileNotFoundError("Node.js is required to deterministically execute the KubeJS registration scripts")


def capture_kubejs(project: Path, directory: Path, node: Path) -> dict[str, Any]:
    helper = project / "tools" / "capture_kubejs_runtime.mjs"
    completed = subprocess.run(
        [str(node), str(helper), str(directory)],
        check=True,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    return json.loads(completed.stdout)


def apply_tag_operations(tags: dict[tuple[str, str], list[str]], operations: list[dict[str, Any]]) -> None:
    for operation in operations:
        if operation.get("domain") != "tag":
            continue
        key = (normalize_kind(str(operation["registry"])), str(operation["tag"]).lstrip("#"))
        if operation["action"] == "clear":
            tags[key] = []
            continue
        raw = operation.get("value")
        values = raw if isinstance(raw, list) else [raw]
        for value in values:
            if isinstance(value, dict):
                value = value.get("id", value.get("item"))
            if not isinstance(value, str):
                continue
            if operation["action"] == "add" and value not in tags.setdefault(key, []):
                tags[key].append(value)
            elif operation["action"] == "remove" and value in tags.setdefault(key, []):
                tags[key].remove(value)


def recipe_matches(recipe: Recipe, operation: dict[str, Any], tags: dict[tuple[str, str], list[str]]) -> bool:
    recipe_filter = operation.get("filter")
    if isinstance(recipe_filter, str):
        return recipe.recipe_type == recipe_filter
    if not isinstance(recipe_filter, dict):
        return False
    if "id" in recipe_filter and recipe.recipe_id != recipe_filter["id"]:
        return False
    if "mod" in recipe_filter and recipe.recipe_id.split(":", 1)[0] != recipe_filter["mod"]:
        return False
    if "type" in recipe_filter and recipe.recipe_type != recipe_filter["type"]:
        return False
    if "output" in recipe_filter:
        target = str(recipe_filter["output"])
        output_ids = {
            member
            for resource in recipe.outputs
            for member in (
                expand_tag(tags, resource.kind, resource.resource_id)
                if resource.tag else [resource.resource_id]
            )
        }
        if target.startswith("#"):
            members = set(expand_tag(tags, "item", target[1:]))
            if not output_ids.intersection(members):
                return False
        elif target not in output_ids:
            return False
    if "input" in recipe_filter:
        target = str(recipe_filter["input"])
        input_ids = {
            member
            for group in recipe.inputs
            for resource in group
            for member in (
                expand_tag(tags, resource.kind, resource.resource_id)
                if resource.tag else [resource.resource_id]
            )
        }
        if target.startswith("#"):
            members = set(expand_tag(tags, "item", target[1:]))
            if not input_ids.intersection(members):
                return False
        elif target not in input_ids:
            return False
    return True


def apply_kubejs_recipes(
    definitions: list[Recipe], operations: list[dict[str, Any]], tags: dict[tuple[str, str], list[str]]
) -> tuple[dict[str, Recipe], list[dict[str, Any]], int]:
    by_id: dict[str, Recipe] = {}
    duplicates = 0
    for recipe in definitions:
        if recipe.condition_state == "inactive":
            continue
        if recipe.recipe_id in by_id:
            duplicates += 1
        by_id[recipe.recipe_id] = recipe

    removed: list[dict[str, Any]] = []
    for operation in operations:
        if operation.get("domain") != "recipe":
            continue
        if operation["action"] == "remove":
            matches = [recipe_id for recipe_id, recipe in by_id.items() if recipe_matches(recipe, operation, tags)]
            for recipe_id in sorted(matches):
                recipe = by_id.pop(recipe_id)
                removed.append({
                    "recipe_id": recipe_id,
                    "recipe_type": recipe.recipe_type,
                    "outputs": sorted(resource.key for resource in recipe.outputs),
                    "original_source": recipe.source,
                    "removed_by": operation["script"],
                    "filter": operation.get("filter"),
                })
        elif operation["action"] == "add":
            data = operation.get("data") or {}
            if not isinstance(data, dict):
                continue
            recipe_type = str(data.get("type", "unknown:unknown"))
            recipe_id = str(operation["recipe_id"])
            by_id[recipe_id] = Recipe(
                recipe_id=recipe_id,
                recipe_type=recipe_type,
                source=f"{operation['script']}#{operation['ordinal']}",
                source_kind="kubejs",
                data=data,
                inputs=input_groups(data, recipe_type),
                outputs=output_resources(data, recipe_type),
                machine_requirements=machine_requirements(data, recipe_type),
            )
    return by_id, removed, duplicates


def add_verified_dynamic_routes(
    recipes: dict[str, Recipe], instance: Path,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    create_config = instance / "config" / "create-server.toml"
    config_text = create_config.read_text(encoding="utf-8-sig", errors="replace") if create_config.exists() else ""
    match = re.search(r"(?mi)^\s*enableRefinedRadianceRecipe\s*=\s*(true|false)\s*$", config_text)
    enabled = match is not None and match.group(1).lower() == "true"
    chromatic_producers = sorted(
        recipe.recipe_id for recipe in recipes.values()
        if "item:create:chromatic_compound" in {output.key for output in recipe.outputs if not output.tag}
    )
    installed = enabled and bool(chromatic_producers)
    recipe_id = "industrial_audit:dynamic/create/chromatic_compound_to_refined_radiance"
    if installed:
        recipes[recipe_id] = Recipe(
            recipe_id=recipe_id,
            recipe_type="create:in_world_refined_radiance",
            source=f"{create_config}!/enableRefinedRadianceRecipe=true",
            source_kind="verified_dynamic",
            data={
                "type": "create:in_world_refined_radiance",
                "input": {"item": "create:chromatic_compound"},
                "result": {"id": "create:refined_radiance"},
            },
            inputs=[[Resource("item", "create:chromatic_compound")]],
            outputs=[Resource("item", "create:refined_radiance")],
        )
    checks.append({
        "route_id": recipe_id,
        "input": "item:create:chromatic_compound",
        "output": "item:create:refined_radiance",
        "config_path": str(create_config),
        "config_present": create_config.exists(),
        "config_enabled": enabled,
        "active_input_producers": chromatic_producers,
        "installed_in_reachability_graph": installed,
        "policy": "The dynamic edge exists only when Create enables the in-world recipe and Chromatic Compound has an active producer; Refined Radiance is never a seed.",
    })

    # Filled buckets are runtime container operations, not recipe JSON. Install
    # an edge only when the matching fluid itself has an active producer (or is
    # one of the explicitly verified world fluids), so a bucket never becomes a
    # free seed and cannot hide a missing fluid-production line.
    snapshot = list(recipes.values())
    produced = {
        output.key for recipe in snapshot for output in recipe.outputs if not output.tag
    }
    bucket_inputs = {
        resource.key
        for recipe in snapshot
        for group in recipe.inputs
        for resource in group
        if not resource.tag and resource.kind == "item" and resource.resource_id.endswith("_bucket")
    }
    world_fluids = {
        "fluid:minecraft:water", "fluid:minecraft:flowing_water",
        "fluid:minecraft:lava", "fluid:minecraft:flowing_lava",
        "fluid:tfmg:crude_oil", "fluid:tfmg:flowing_crude_oil",
    }
    for bucket_key in sorted(bucket_inputs - produced):
        bucket_id = bucket_key.split(":", 1)[1]
        namespace, path = bucket_id.split(":", 1)
        fluid_key = f"fluid:{namespace}:{path[:-len('_bucket')]}"
        if fluid_key not in produced and fluid_key not in world_fluids:
            continue
        route_id = f"industrial_audit:dynamic/bucket_fill/{namespace}/{path[:-len('_bucket')]}"
        recipes[route_id] = Recipe(
            recipe_id=route_id,
            recipe_type="minecraft:runtime_bucket_fill",
            source="verified bucket/container runtime using an active fluid producer",
            source_kind="verified_dynamic",
            data={"type": "minecraft:runtime_bucket_fill"},
            inputs=[[Resource("fluid", f"{namespace}:{path[:-len('_bucket')]}" )]],
            outputs=[Resource("item", bucket_id)],
        )
        checks.append({
            "route_id": route_id,
            "input": fluid_key,
            "output": bucket_key,
            "installed_in_reachability_graph": True,
            "policy": "Runtime bucket filling is modeled only from a verified world fluid or active fluid producer; the filled bucket is never a seed.",
        })
    return checks


def expand_tag(tags: dict[tuple[str, str], list[str]], kind: str, tag_id: str) -> list[str]:
    result: set[str] = set()
    frontier = [tag_id]
    seen: set[str] = set()
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        for value in tags.get((kind, current), []):
            if value.startswith("#"):
                frontier.append(value[1:])
            else:
                result.add(value)
    return sorted(result)


def load_stage_map(project: Path) -> tuple[dict[str, str], list[dict[str, Any]]]:
    entries: list[dict[str, Any]] = []
    for entry in json_read(project / "tools" / "additional_recipe_stages.json")["recipes"]:
        entries.append({**entry, "source": "additional_recipe_stages.json"})
    for entry in json_read(project / "tools" / "machine_recipe_dependencies.json")["recipes"]:
        entries.append({
            "recipe_id": entry["recipe_id"],
            "node": entry["node"],
            "reason": f"Construction recipe for {entry['output']}",
            "source": "machine_recipe_dependencies.json",
        })
    mapping: dict[str, str] = {}
    for entry in entries:
        existing = mapping.get(entry["recipe_id"])
        if existing and existing != entry["node"]:
            raise ValueError(f"Conflicting stage mapping for {entry['recipe_id']}: {existing} vs {entry['node']}")
        mapping[entry["recipe_id"]] = entry["node"]
    return mapping, entries


def load_graph(drawio: Path) -> dict[str, Any]:
    graph = json_read(drawio)
    if graph.get("source_sha256", "").lower() != DRAWIO_SHA256:
        raise ValueError("Authoritative Draw.io export hash changed")
    id_to_label = {node["id"]: node["label"] for node in graph["nodes"]}
    incoming: dict[str, set[str]] = defaultdict(set)
    for edge in graph["edges"]:
        incoming[id_to_label[edge["target"]]].add(id_to_label[edge["source"]])
    labels = [node["label"] for node in graph["nodes"]]
    index = {label: position for position, label in enumerate(labels)}

    def ancestors(label: str) -> set[str]:
        result: set[str] = set()
        frontier = list(incoming.get(label, set()))
        while frontier:
            parent = frontier.pop()
            if parent not in result:
                result.add(parent)
                frontier.extend(incoming.get(parent, set()))
        return result

    masks = {label: sum(1 << index[name] for name in ancestors(label) | {label}) for label in labels}
    return {"raw": graph, "labels": labels, "index": index, "incoming": incoming, "masks": masks}


def load_owners(project: Path) -> tuple[dict[str, set[str]], dict[str, Any]]:
    mapping = json_read(project / "progression" / "machine_node_assignments.json")
    owners: dict[str, set[str]] = defaultdict(set)
    for node, definition in mapping["nodes"].items():
        unlock_types = definition.get("unlock_types", {})
        for unlock in definition.get("unlocks", []):
            kind = unlock_types.get(unlock, "item")
            if kind == "vanilla_item":
                kind = "item"
            owners[f"{kind}:{unlock}"].add(node)
    return owners, mapping


def pareto_add(masks: list[int], candidate: int, cap: int = 16) -> bool:
    if any((existing | candidate) == candidate for existing in masks):
        return False
    masks[:] = [existing for existing in masks if (existing | candidate) != existing]
    masks.append(candidate)
    masks.sort(key=lambda value: (value.bit_count(), value))
    if len(masks) > cap:
        del masks[cap:]
    return candidate in masks


def group_alternatives(group: list[Resource], tags: dict[tuple[str, str], list[str]]) -> list[str]:
    alternatives: set[str] = set()
    for resource in group:
        if resource.tag:
            for member in expand_tag(tags, resource.kind, resource.resource_id):
                alternatives.add(f"{resource.kind}:{member}")
        else:
            alternatives.add(resource.key)
    return sorted(alternatives)


def compute_reachability(
    recipes: dict[str, Recipe], tags: dict[tuple[str, str], list[str]], seeds: set[str], optimistic: bool,
    owners: dict[str, set[str]], node_masks: dict[str, int], registry_models: set[str],
) -> tuple[dict[str, list[int]], dict[str, dict[int, dict[str, Any]]], int]:
    producers = {resource.key for recipe in recipes.values() for resource in recipe.outputs if not resource.tag}
    all_inputs = {
        alternative
        for recipe in recipes.values()
        for group in recipe.inputs
        for alternative in group_alternatives(group, tags)
    }
    available: dict[str, list[int]] = defaultdict(list)
    witness: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for seed in sorted(seeds):
        pareto_add(available[seed], 0)
        witness[seed][0] = {"kind": "verified_seed"}
    # Runtime transformations and machine byproducts do not have datapack
    # recipe JSON, but progression ownership still gives them a deterministic
    # earliest stage. Make them available at that owner-stage mask so they can
    # feed downstream routes without pretending they are free world seeds.
    for resource, resource_owners in sorted(owners.items()):
        dynamic_reason = intentional_dynamic_reason(resource)
        if not dynamic_reason:
            continue
        for node in sorted(resource_owners):
            mask = node_masks.get(node)
            if mask is None:
                continue
            if pareto_add(available[resource], mask):
                witness[resource][mask] = {
                    "kind": "intentional_dynamic_source",
                    "node": node,
                    "reason": dynamic_reason,
                }
    if optimistic:
        for resource in sorted(all_inputs - producers - set(owners)):
            # Optimistic mode is deliberately a ceiling: any unowned input with
            # no static producer may come from a runtime mechanic (pumpjack,
            # reactor operation, mob, world source, or serializer-specific
            # process). Strict mode never makes this assumption.
            pareto_add(available[resource], 0)
            witness[resource][0] = {"kind": "unknown_external_seed"}

    variants: dict[str, list[tuple[list[list[str]], list[str], str]]] = {}
    for recipe in recipes.values():
        machine_groups = [[f"item:{machine}"] for machine in recipe.machine_requirements]
        if recipe.recipe_type == "mekanism:rotary":
            rotary_variants: list[tuple[list[list[str]], list[str], str]] = []
            chemical_input = group_alternatives(resources_in(recipe.data.get("chemical_input"), "chemical"), tags)
            fluid_input = group_alternatives(resources_in(recipe.data.get("fluid_input"), "fluid"), tags)
            fluid_outputs = [resource.key for resource in resources_in(recipe.data.get("fluid_output"), "fluid")]
            chemical_outputs = [resource.key for resource in resources_in(recipe.data.get("chemical_output"), "chemical")]
            if chemical_input and fluid_outputs:
                rotary_variants.append(([chemical_input, *machine_groups], fluid_outputs, "chemical_to_fluid"))
            if fluid_input and chemical_outputs:
                rotary_variants.append(([fluid_input, *machine_groups], chemical_outputs, "fluid_to_chemical"))
            variants[recipe.recipe_id] = rotary_variants
        else:
            groups = [group_alternatives(group, tags) for group in recipe.inputs]
            groups.extend(machine_groups)
            outputs: list[str] = []
            for output in recipe.outputs:
                if output.tag:
                    outputs.extend(f"{output.kind}:{member}" for member in expand_tag(tags, output.kind, output.resource_id))
                else:
                    outputs.append(output.key)
            variants[recipe.recipe_id] = [([group for group in groups if group], sorted(set(outputs)), "default")]

    passes = 0
    for passes in range(1, 129):
        changed = False
        for recipe_id in sorted(recipes):
            recipe = recipes[recipe_id]
            stage_mask = node_masks.get(recipe.stage or "", 0)
            for groups, output_keys, variant_name in variants[recipe_id]:
                combinations = [stage_mask]
                ready = True
                for group in groups:
                    options = [mask for alternative in group for mask in available.get(alternative, [])]
                    if not options:
                        ready = False
                        break
                    next_masks: list[int] = []
                    for base in combinations:
                        for option in options:
                            pareto_add(next_masks, base | option)
                    combinations = next_masks
                if not ready:
                    continue
                for output_key in output_keys:
                    for mask in combinations:
                        if pareto_add(available[output_key], mask):
                            changed = True
                            witness[output_key][mask] = {
                                "kind": "recipe",
                                "recipe_id": recipe_id,
                                "recipe_type": recipe.recipe_type,
                                "source": recipe.source,
                                "variant": variant_name,
                            }
        if not changed:
            break
    return available, witness, passes


def seed_resources(
    tags: dict[tuple[str, str], list[str]], recipes: dict[str, Recipe], owners: dict[str, set[str]],
    loot_sources: dict[str, set[str]], registry_models: set[str], worldgen_blocks: set[str],
    block_loot_drops: dict[str, set[str]],
) -> tuple[set[str], dict[str, list[str]]]:
    producers = {resource.key for recipe in recipes.values() for resource in recipe.outputs if not resource.tag}
    seeds: set[str] = set()
    reasons: dict[str, list[str]] = defaultdict(list)

    def add(resource: str, reason: str) -> None:
        seeds.add(resource)
        reasons[resource].append(reason)

    natural_tag_roots = {
        "ores", "raw_materials", "logs", "leaves", "saplings", "sand", "sands",
        "stones", "cobblestones", "gravel", "gravels", "dirt", "dirts", "seeds",
        "crops", "flowers",
    }

    def is_natural_tag(tag_id: str) -> bool:
        path = tag_id.split(":", 1)[-1]
        root = path.split("/", 1)[0]
        return root in natural_tag_roots or root.startswith(("logs_", "leaves_", "flowers_"))

    for (kind, tag_id), _values in tags.items():
        if kind != "item" or not is_natural_tag(tag_id):
            continue
        for item in expand_tag(tags, kind, tag_id):
            add(f"item:{item}", f"natural_tag:{tag_id}")

    for item in sorted(registry_models):
        key = f"item:{item}"
        if key in owners or key in producers or not item.startswith("minecraft:"):
            continue
        loot_kinds = loot_sources.get(item, set())
        add(key, "vanilla_world_or_mob_source" if not loot_kinds else f"vanilla_loot:{','.join(sorted(loot_kinds))}")

    # Chest/entity/gameplay loot is a real acquisition path. Block loot is a
    # seed only when its source block is present in configured worldgen; this
    # avoids treating every craftable block's self-drop as a free resource.
    for item, sources in sorted(loot_sources.items()):
        non_block_sources = sorted(source for source in sources if not source.startswith("blocks:"))
        for source in non_block_sources:
            add(f"item:{item}", f"loot:{source}")
    for block_id in sorted(worldgen_blocks):
        drops = sorted(block_loot_drops.get(block_id, set()))
        if not drops and block_id in registry_models:
            drops = [block_id]
        for item in drops:
            add(f"item:{item}", f"configured_worldgen_block:{block_id}")

    # AE2's bundled guide and active meteorite structure define these as
    # Mysterious Cube drops. Their self-consuming duplication recipes are not
    # bootstrap producers and must not hide the real world-source edge.
    for press in (
        "ae2:silicon_press", "ae2:logic_processor_press",
        "ae2:calculation_processor_press", "ae2:engineering_processor_press",
    ):
        add(f"item:{press}", "ae2_meteorite_mysterious_cube_drop")

    for fluid in (
        "minecraft:water", "minecraft:flowing_water", "minecraft:lava", "minecraft:flowing_lava",
        "tfmg:crude_oil", "tfmg:flowing_crude_oil",
    ):
        add(f"fluid:{fluid}", "world_or_dynamic_fluid_source")
    return seeds, reasons


def labels_from_mask(mask: int, graph: dict[str, Any]) -> list[str]:
    return [label for label, index in graph["index"].items() if mask & (1 << index)]


def finding(severity: str, category: str, subject: str, message: str, **details: Any) -> dict[str, Any]:
    return {"severity": severity, "category": category, "subject": subject, "message": message, **details}


FACTORY_UPGRADE = re.compile(
    r"^item:mekanism:(?:basic|advanced|elite|ultimate)_"
    r"(?:combining|compressing|enriching|infusing|injecting|purifying)_factory$"
)


def intentional_dynamic_reason(resource_key: str) -> str | None:
    if FACTORY_UPGRADE.match(resource_key):
        return "Mekanism factory created in-world by applying a physically manufactured Tier Installer to the prior machine/factory tier"
    if resource_key in {
        "item:ae2:item_p2p_tunnel", "item:ae2:fluid_p2p_tunnel", "item:ae2:fe_p2p_tunnel",
        "item:appmek:chemical_p2p_tunnel",
    }:
        return "P2P tunnel attunement conversion from the craftable ME P2P tunnel"
    if resource_key.startswith("item:") and resource_key.endswith("_bucket"):
        return "dynamic bucket filling from the corresponding fluid"
    if resource_key in {
        "item:bigreactors:cyanite_ingot",
        "item:bigreactors:magentite_ingot",
    }:
        return "runtime Extreme Reactors solid byproduct at the owning reactor stage"
    if (
        resource_key.startswith("fluid:bigreactors:")
        and resource_key != "fluid:bigreactors:yellorium"
    ) or resource_key in {
        "chemical:mekanism:nuclear_waste", "chemical:mekanism:spent_nuclear_waste",
    }:
        return "runtime reactor/reprocessor byproduct rather than a datapack recipe output"
    return None


def unresolved_recipe_groups(
    recipe: Recipe, availability: dict[str, list[int]], tags: dict[tuple[str, str], list[str]]
) -> list[list[str]]:
    groups = [group_alternatives(group, tags) for group in recipe.inputs]
    groups.extend([[f"item:{machine}"] for machine in recipe.machine_requirements])
    return [group for group in groups if group and not any(availability.get(resource) for resource in group)]


def special_nuclear_findings(
    recipes: dict[str, Recipe], tags: dict[tuple[str, str], list[str]], stage_map: dict[str, str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    def ids(resources: Iterable[Resource], kind: str | None = None) -> set[str]:
        return {
            resource.resource_id
            for resource in resources
            if not resource.tag and (kind is None or resource.kind == kind)
        }

    def expanded_ids(resources: Iterable[Resource], kind: str | None = None) -> set[str]:
        values: set[str] = set()
        for resource in resources:
            if kind is not None and resource.kind != kind:
                continue
            if resource.tag:
                values.add(f"#{resource.resource_id}")
                values.update(expand_tag(tags, resource.kind, resource.resource_id))
            else:
                values.add(resource.resource_id)
        return values

    raw_uranium = {
        "mekanism:raw_uranium", "mekanism:block_raw_uranium", "mekanism:uranium_ore",
        "mekanism:deepslate_uranium_ore",
    }
    uranium_or_fuel_fragments = (
        "uranium", "fissile", "plutonium", "cyanite", "blutonium", "reactor_fuel", "fuel_pellet",
    )
    processed_fragments = ("ingot", "dust", "clump", "shard", "crystal", "yellow_cake", "fissile", "oxide", "hexafluoride")

    for recipe in recipes.values():
        input_resources = [resource for group in recipe.inputs for resource in group]
        input_ids = expanded_ids(input_resources)
        output_ids = expanded_ids(recipe.outputs)
        yellorium_outputs = {value for value in output_ids if "yellorium" in value}
        forbidden_sources = {
            value for value in input_ids
            if "yellorium" not in value
            and any(fragment in value for fragment in uranium_or_fuel_fragments)
        }
        if yellorium_outputs and forbidden_sources:
            findings.append(finding(
                "critical", "nuclear_reverse_conversion", recipe.recipe_id,
                "A Yellorium form is produced from uranium, fissile material, or another reactor fuel; the required chain is strictly forward-only.",
                recipe_type=recipe.recipe_type, forbidden_inputs=sorted(forbidden_sources),
                yellorium_outputs=sorted(yellorium_outputs), source=recipe.source,
            ))

        raw_inputs = input_ids.intersection(raw_uranium)
        processed_outputs = {
            value for value in output_ids
            if any(fragment in value for fragment in processed_fragments) and value not in raw_uranium
        }
        if raw_inputs and processed_outputs and not recipe.recipe_type.startswith("mekanism:"):
            findings.append(finding(
                "critical", "non_mekanism_raw_uranium_processing", recipe.recipe_id,
                "Raw uranium is transformed outside a Mekanism machine.",
                recipe_type=recipe.recipe_type, inputs=sorted(raw_inputs), outputs=sorted(processed_outputs), source=recipe.source,
            ))

    dangerous_tags = [
        ("item", "c:ingots/uranium"),
        ("item", "forge:ingots/uranium"),
        ("item", "c:storage_blocks/uranium"),
        ("item", "forge:storage_blocks/uranium"),
        ("fluid", "c:yellorium"),
    ]
    for registry, tag_id in dangerous_tags:
        members = expand_tag(tags, registry, tag_id)
        if members:
            findings.append(finding(
                "critical", "reactor_fuel_tag_bypass", tag_id,
                "A direct reactor-fuel/storage alias is non-empty.", members=members,
                registry=registry,
            ))

    alloy_producers = [
        recipe for recipe in recipes.values()
        if "bigreactors:yellorium" in ids(recipe.outputs)
    ]
    alloy_valid = [
        recipe.recipe_id for recipe in alloy_producers
        if recipe.recipe_type in {"create:mixing", "tfmg:industrial_mixing", "createmetallurgy:alloying"}
        and len(recipe.inputs) >= 2
    ]
    if not alloy_valid:
        findings.append(finding(
            "critical", "yellorium_not_an_alloy", "bigreactors:yellorium",
            "Molten Yellorium has no active multi-input alloy-mixing recipe at its Advanced Alloy Mixing progression node.",
            active_producers=[{
                "recipe_id": recipe.recipe_id, "recipe_type": recipe.recipe_type,
                "stage": stage_map.get(recipe.recipe_id), "source": recipe.source,
            } for recipe in alloy_producers],
        ))

    advanced_alloy_checks = [
        {"recipe_id": "createmetallurgy:crafting/content/foundry_basin", "policy": "exact_stage"},
        {"recipe_id": "createmetallurgy:crafting/content/foundry_lid", "policy": "exact_stage"},
        {"recipe_id": "createmetallurgy:crafting/content/foundry_mixer", "policy": "exact_stage"},
        {"recipe_id": "createmetallurgy:sequenced_assembly/industrial_crucible", "policy": "exact_stage"},
        {"recipe_id": "createmetallurgy:melting/lead/ingot", "policy": "industrial_crucible_machine_gate"},
        {"recipe_id": "createmetallurgy:melting/gold/ingot", "policy": "industrial_crucible_machine_gate"},
        {"recipe_id": "industrial_colonies:materials/yellorium/molten_alloy", "policy": "exact_stage"},
    ]
    advanced_alloy_results: list[dict[str, Any]] = []
    for check in advanced_alloy_checks:
        recipe_id = check["recipe_id"]
        recipe = recipes.get(recipe_id)
        result = {**check, "active": recipe is not None, "mapped_stage": stage_map.get(recipe_id)}
        if recipe:
            result["recipe_type"] = recipe.recipe_type
            result["machine_requirements"] = recipe.machine_requirements
        advanced_alloy_results.append(result)
        if recipe is None:
            findings.append(finding(
                "critical", "advanced_alloy_mixing_gate_set", recipe_id,
                "A required Advanced Alloy Mixing enabling recipe is not active.", policy=check["policy"],
            ))
        elif check["policy"] == "exact_stage" and stage_map.get(recipe_id) != "CR01 — Advanced Alloy Mixing":
            findings.append(finding(
                "critical", "advanced_alloy_mixing_gate_set", recipe_id,
                "The enabling recipe is not exact-staged at Advanced Alloy Mixing.",
                expected_stage="CR01 — Advanced Alloy Mixing", actual_stage=stage_map.get(recipe_id),
            ))
        elif check["policy"] == "industrial_crucible_machine_gate" and "createmetallurgy:industrial_crucible" not in recipe.machine_requirements:
            findings.append(finding(
                "critical", "advanced_alloy_mixing_gate_set", recipe_id,
                "The stock molten-metal route is not modeled behind the staged Industrial Crucible.",
                machine_requirements=recipe.machine_requirements,
            ))

    adjacency: dict[str, set[str]] = defaultdict(set)
    edge_recipes: dict[tuple[str, str], set[str]] = defaultdict(set)
    for recipe in recipes.values():
        input_ids = ids(resource for group in recipe.inputs for resource in group)
        output_ids = ids(recipe.outputs)
        for source in input_ids:
            for target in output_ids:
                adjacency[source].add(target)
                edge_recipes[(source, target)].add(recipe.recipe_id)

    start = "bigreactors:yellorium"
    feedstocks = {
        "mekanism:raw_uranium", "mekanism:clump_uranium", "mekanism:dirty_dust_uranium",
        "mekanism:dust_uranium", "mekanism:yellow_cake_uranium",
    }
    parent: dict[str, str] = {}
    frontier = deque([start])
    reached_feedstock: str | None = None
    seen = {start}
    while frontier and not reached_feedstock:
        current = frontier.popleft()
        for target in sorted(adjacency.get(current, set())):
            if target in seen:
                continue
            seen.add(target)
            parent[target] = current
            if target in feedstocks:
                reached_feedstock = target
                break
            frontier.append(target)
    route: list[str] = []
    if reached_feedstock:
        cursor = reached_feedstock
        route.append(cursor)
        while cursor != start:
            cursor = parent[cursor]
            route.append(cursor)
        route.reverse()
    else:
        findings.append(finding(
            "critical", "missing_yellorium_to_uranium_route", start,
            "No active recipe path converts the Yellorium alloy into a Mekanism uranium feedstock.",
            target_feedstocks=sorted(feedstocks),
        ))

    return findings, {
        "required_direction": "Yellorium alloy -> uranium feedstock -> Mekanism machine enrichment -> fuel",
        "alloy_recipe_ids": alloy_valid,
        "advanced_alloy_mixing_recipe_ids": [check["recipe_id"] for check in advanced_alloy_checks],
        "advanced_alloy_mixing_expected_count": 7,
        "advanced_alloy_mixing_checks": advanced_alloy_results,
        "yellorium_to_uranium_route": route,
    }


def runtime_family(recipe_type: str) -> str:
    namespace = recipe_type.split(":", 1)[0]
    if namespace == "minecraft":
        return "vanilla_crafting_cooking_smithing"
    return {
        "create": "create_processing",
        "createmetallurgy": "create_metallurgy",
        "mekanism": "mekanism_machine_and_crafting",
        "tfmg": "tfmg_processing_and_crafting",
        "bigreactors": "extreme_reactors",
        "ae2": "ae2_crafting_and_transform",
        "extendedae": "extended_ae_processing",
        "advanced_ae": "advanced_ae_processing",
    }.get(namespace, f"modded_{namespace}")


def known_non_static_serializer(recipe: Recipe) -> str | None:
    recipe_type = recipe.recipe_type
    namespace = recipe_type.split(":", 1)[0]
    if namespace in {"apotheosis", "apothic_spawners"}:
        return "excluded_apotheosis_runtime"
    if recipe_type.startswith("minecraft:crafting_special_") or recipe_type == "minecraft:smithing_trim":
        return "intentional_runtime_special_recipe"
    if namespace in {
        "createbigcannons", "cbc_at", "securitycraft", "computercraft", "supplementaries",
        "amendments", "aquaculture", "farmersdelight", "deeperdarker",
    } and not recipe.outputs:
        return "intentional_runtime_special_recipe"
    if recipe_type in {
        "ae2:matter_cannon", "ae2:add_item_upgrade", "ae2:remove_item_upgrade", "ae2:facade",
        "mekanism:energy_conversion", "minecolonies:composting",
    }:
        return "intentional_declarative_recipe_data"
    if namespace in {"chipped", "domum_ornamentum"} and not recipe.outputs:
        return "intentional_decorative_runtime_recipe"
    if recipe_type == "createaddition:liquid_burning":
        return "intentional_fuel_property_recipe"
    return None


def serializer_coverage(recipes: dict[str, Recipe]) -> dict[str, Any]:
    classifications: Counter[str] = Counter()
    type_groups: dict[str, Counter[str]] = defaultdict(Counter)
    review_records: list[dict[str, Any]] = []
    for recipe in recipes.values():
        known = known_non_static_serializer(recipe)
        if recipe.inputs and recipe.outputs:
            classification = "static_transform_parsed"
        elif known:
            classification = known
        elif recipe.outputs:
            classification = "unmodeled_input_schema"
        elif recipe.inputs:
            classification = "unmodeled_output_or_sink_schema"
        else:
            classification = "opaque_or_declarative_schema"
        classifications[classification] += 1
        type_groups[classification][recipe.recipe_type] += 1
        if classification.startswith(("unmodeled_", "opaque_")):
            review_records.append({
                "recipe_id": recipe.recipe_id,
                "recipe_type": recipe.recipe_type,
                "source": recipe.source,
                "has_inputs": bool(recipe.inputs),
                "outputs": sorted(output.key for output in recipe.outputs),
            })
    return {
        "classification_counts": dict(sorted(classifications.items())),
        "recipe_type_counts_by_classification": {
            classification: dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
            for classification, counts in sorted(type_groups.items())
        },
        "review_records": sorted(review_records, key=lambda value: (value["recipe_type"], value["recipe_id"])),
    }


def build_stage_gap_groups(
    findings: list[dict[str, Any]], active: dict[str, Recipe], owners: dict[str, set[str]],
) -> list[dict[str, Any]]:
    early_outputs = {
        entry["subject"] for entry in findings if entry["category"] == "early_unlock_bypass"
    }
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for recipe in active.values():
        offending_outputs = sorted({
            output.key for output in recipe.outputs
            if output.key in early_outputs and recipe.stage not in owners.get(output.key, set())
        })
        if not offending_outputs:
            continue
        family = runtime_family(recipe.recipe_type)
        grouped[family].append({
            "recipe_id": recipe.recipe_id,
            "recipe_type": recipe.recipe_type,
            "current_stage": recipe.stage,
            "required_owner_nodes": sorted({
                node for output in offending_outputs for node in owners.get(output, set())
            }),
            "outputs": offending_outputs,
            "source": recipe.source,
        })
    return [
        {
            "runtime_family": family,
            "recipe_count": len(records),
            "output_count": len({output for record in records for output in record["outputs"]}),
            "recipes": sorted(records, key=lambda value: value["recipe_id"]),
        }
        for family, records in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
    ]


def build_blocker_cascades(
    findings: list[dict[str, Any]], active: dict[str, Recipe],
    availability: dict[str, list[int]], tags: dict[tuple[str, str], list[str]],
) -> list[dict[str, Any]]:
    blocked = {
        entry["subject"]: entry
        for entry in findings
        if entry["category"] in {"blocked_owned_output", "unreachable_owned_output"}
    }
    producers: dict[str, list[Recipe]] = defaultdict(list)
    for recipe in active.values():
        for output in recipe.outputs:
            if not output.tag:
                producers[output.key].append(recipe)

    dependencies: dict[str, set[str]] = {}

    def unresolved_dependencies(resource: str) -> set[str]:
        if resource in dependencies:
            return dependencies[resource]
        values: set[str] = set()
        for recipe in producers.get(resource, []):
            for group in unresolved_recipe_groups(recipe, availability, tags):
                values.update(group)
        dependencies[resource] = values
        return values

    memo: dict[str, set[str]] = {}

    def roots(subject: str, stack: tuple[str, ...] = ()) -> set[str]:
        if subject in memo:
            return memo[subject]
        if subject in stack:
            body = list(stack[stack.index(subject):])
            rotations = [body[index:] + body[:index] for index in range(len(body))]
            canonical = min(rotations)
            return {"cycle:" + " -> ".join(canonical + [canonical[0]])}
        deps = unresolved_dependencies(subject)
        if not deps:
            memo[subject] = {subject}
            return memo[subject]
        result: set[str] = set()
        for dependency in sorted(deps):
            if not availability.get(dependency) and producers.get(dependency):
                result.update(roots(dependency, stack + (subject,)))
            else:
                result.add(dependency)
        memo[subject] = result or {subject}
        return memo[subject]

    affected: dict[str, set[str]] = defaultdict(set)
    for subject in sorted(blocked):
        for root in roots(subject):
            affected[root].add(subject)
    return [
        {
            "root_resource": root,
            "affected_owned_output_count": len(subjects),
            "affected_owned_outputs": sorted(subjects),
        }
        for root, subjects in sorted(affected.items(), key=lambda item: (-len(item[1]), item[0]))
    ]


def markdown_report(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# Global Recipe Reachability and Loophole Audit",
        "",
        "This is a deterministic project-targeted static audit over the live dependency set. It does not edit the authoritative Draw.io file or gameplay recipes.",
        "",
        "## Coverage",
        "",
        f"- JARs scanned: **{counts['jars']}**",
        f"- Vanilla data JARs scanned in addition: **{counts['vanilla_data_jars']}**",
        f"- Recipe JSON definitions inspected: **{counts['jar_recipe_definitions']}**",
        f"- Unique active recipes after conditions, KubeJS removals, and additions: **{counts['active_recipes']}**",
        f"- KubeJS recipe additions executed: **{counts['kubejs_recipe_additions']}**",
        f"- KubeJS recipe removal operations executed: **{counts['kubejs_recipe_removal_operations']}**",
        f"- Deliberate no-replacement retirements classified: **{counts['intentional_removed_recipe_retirements']}**",
        f"- Verified runtime edges installed: **{counts['active_verified_dynamic_routes']}**",
        f"- Stage manifest rows / unique exact recipe IDs: **{counts['stage_manifest_rows']} / {counts['exact_stage_mappings']}**",
        f"- Active staged recipes / missing staged IDs: **{counts['active_staged_recipes']} / {counts['missing_staged_recipes']}**",
        f"- Authoritative graph: **{counts['drawio_nodes']} nodes / {counts['drawio_edges']} edges**",
        f"- Progression-owned resources checked: **{counts['owned_resources']}**",
        f"- Findings: **{counts['findings']}** ({', '.join(f'{key} {value}' for key, value in report['severity_counts'].items())})",
        "",
        "## Required nuclear direction",
        "",
        f"`{report['nuclear_policy']['required_direction']}`",
        "",
        f"Detected Yellorium alloy recipes: {', '.join(report['nuclear_policy']['alloy_recipe_ids']) or '**none**'}",
        "",
        f"Detected Yellorium-to-uranium path: {' -> '.join(report['nuclear_policy']['yellorium_to_uranium_route']) or '**none**'}",
        "",
        "Advanced Alloy Mixing gate set:",
        "",
    ]
    for check in report["nuclear_policy"]["advanced_alloy_mixing_checks"]:
        status = "PASS" if check.get("active") else "FAIL"
        detail = check.get("mapped_stage") or ", ".join(check.get("machine_requirements", [])) or "no gate detected"
        lines.append(f"- **{status}** `{check['recipe_id']}` — {check['policy']} ({detail})")
    lines.extend([
        "",
        "## Prioritized repair list",
        "",
    ])
    root_cascades = report["repair_plan"]["root_blocker_cascades"]
    if root_cascades:
        lines.extend(["### Root blockers and cascades", ""])
        for index, cascade in enumerate(root_cascades[:20], 1):
            examples = ", ".join(f"`{value}`" for value in cascade["affected_owned_outputs"][:5])
            lines.append(
                f"{index}. `{cascade['root_resource']}` blocks **{cascade['affected_owned_output_count']}** owned outputs"
                + (f" (for example {examples})" if examples else "") + "."
            )
        if len(root_cascades) > 20:
            lines.append(f"\nThe JSON report contains {len(root_cascades) - 20} additional blocker roots.")
    else:
        lines.append("No unresolved root blocker cascade remains.")

    stage_groups = report["repair_plan"]["missing_or_mismatched_exact_stage_groups"]
    lines.extend(["", "### Exact-stage gaps by runtime family", ""])
    if not stage_groups:
        lines.append("No early-output recipe family is missing or mismatched to its owning node.")
    else:
        for group in stage_groups:
            example_ids = ", ".join(f"`{entry['recipe_id']}`" for entry in group["recipes"][:5])
            lines.append(
                f"- **{group['runtime_family']}**: {group['recipe_count']} recipes / "
                f"{group['output_count']} owned outputs. Examples: {example_ids}."
            )

    prioritized = [
        entry for entry in report["findings"]
        if entry["severity"] in {"critical", "high"}
        and entry["category"] not in {"early_unlock_bypass", "blocked_owned_output", "unreachable_owned_output"}
    ]
    lines.extend(["", "### Other critical/high structural findings", ""])
    if not prioritized:
        lines.append("No additional critical/high structural findings.")
    else:
        for index, entry in enumerate(prioritized[:30], 1):
            lines.append(
                f"{index}. **{entry['severity'].upper()} — {entry['category']}** — "
                f"`{entry['subject']}`: {entry['message']}"
            )
        if len(prioritized) > 30:
            lines.append(f"\nThe JSON report contains {len(prioritized) - 30} additional findings in this class.")

    schema_counts = report["serializer_coverage"]["classification_counts"]
    lines.extend([
        "",
        "## Serializer coverage",
        "",
        f"- Fully parsed static transformations: **{schema_counts.get('static_transform_parsed', 0)}**",
        f"- Unmodeled input schemas: **{schema_counts.get('unmodeled_input_schema', 0)}**",
        f"- Unmodeled output/sink schemas: **{schema_counts.get('unmodeled_output_or_sink_schema', 0)}**",
        f"- Opaque/declarative schemas requiring review: **{schema_counts.get('opaque_or_declarative_schema', 0)}**",
        "- Intentional runtime, decorative, fuel-property, and excluded Apotheosis serializers are counted separately in the JSON report.",
    ])
    lines.extend([
        "",
        "## Interpretation rules",
        "",
        "- `early_unlock_bypass` means the static recipe/machine dependency path omits at least one required Draw.io ancestor.",
        "- `unreachable_owned_output` means no complete strict or optimistic recipe path was found; dynamic in-world mechanics are separately identified for review.",
        "- `unknown_seed_only` is not asserted as a confirmed break: it needs a runtime/dynamic-source decision.",
        "- Deprecated canonical materials, deliberately retired duplicate machines, migration-only recipes, loot-only items, and decorative outputs are classified separately.",
        "",
        "The complete machine-readable evidence, exact IDs, sources, masks, removal provenance, tag memberships, and stage coverage are in `GLOBAL_RECIPE_REACHABILITY_AUDIT.json`.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Exhaustively audit static recipe reachability and progression loopholes.")
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--instance", type=Path, default=Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one"))
    parser.add_argument("--drawio-export", type=Path)
    parser.add_argument("--vanilla-jar", type=Path)
    parser.add_argument("--node", type=Path)
    parser.add_argument("--scripts-source", choices=("project", "live"), default="project")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    instance = args.instance.resolve()
    audit_dir = project.parent / "industrial-audit"
    drawio = (args.drawio_export or audit_dir / "drawio-export" / "drawio_tree.json").resolve()
    report_path = (args.report or audit_dir / "GLOBAL_RECIPE_REACHABILITY_AUDIT.json").resolve()
    markdown_path = (args.markdown or audit_dir / "GLOBAL_RECIPE_REACHABILITY_AUDIT.md").resolve()

    graph = load_graph(drawio)
    owners, owner_manifest = load_owners(project)
    stage_map, stage_entries = load_stage_map(project)
    vanilla_jar = (args.vanilla_jar or instance.parent.parent / "Install" / "versions" / "1.21.1" / "1.21.1.jar").resolve()
    project_create_applied_config = project / "pack-config-overrides" / "createappliedkinetics-common.toml"
    live_create_applied_config = instance / "config" / "createappliedkinetics-common.toml"
    create_applied_config = (
        project_create_applied_config
        if project_create_applied_config.exists() else live_create_applied_config
    )
    create_applied_text = (
        create_applied_config.read_text(encoding="utf-8-sig", errors="replace")
        if create_applied_config.exists() else ""
    )
    create_applied_match = re.search(
        r"(?mi)^\s*overwrite_ae2_recipes\s*=\s*(true|false)\s*$", create_applied_text
    )
    effective_condition_flags = {
        "createappliedkinetics:ae2_overwrite": bool(
            create_applied_match and create_applied_match.group(1).lower() == "true"
        ),
    }
    jar_scan = scan_jars(instance / "mods", vanilla_jar, effective_condition_flags)
    tags = dict(jar_scan["tags"])
    node = find_node(project, args.node)
    live_scripts = instance / "kubejs" / "server_scripts"
    selected_scripts = project / "pack-scripts" / "server_scripts" if args.scripts_source == "project" else live_scripts
    kube_capture = capture_kubejs(project, selected_scripts, node)
    apply_tag_operations(tags, kube_capture["operations"])
    active, removed, duplicate_definitions = apply_kubejs_recipes(
        jar_scan["definitions"], kube_capture["operations"], tags
    )
    for recipe_id, recipe in active.items():
        recipe.stage = stage_map.get(recipe_id)
    verified_dynamic_routes = add_verified_dynamic_routes(active, instance)

    seeds, seed_reasons = seed_resources(
        tags, active, owners, jar_scan["loot_sources"], jar_scan["registry_models"],
        jar_scan["worldgen_blocks"], jar_scan["block_loot_drops"],
    )
    strict, strict_witness, strict_passes = compute_reachability(
        active, tags, seeds, False, owners, graph["masks"], jar_scan["registry_models"]
    )
    optimistic, optimistic_witness, optimistic_passes = compute_reachability(
        active, tags, seeds, True, owners, graph["masks"], jar_scan["registry_models"]
    )

    findings: list[dict[str, Any]] = []
    natural_feedstock_fragments = ("_ore", "raw_", ":raw", "yellorite")
    owned_results: list[dict[str, Any]] = []
    for resource_key in sorted(owners):
        resource_owners = sorted(owners[resource_key])
        expected_masks = [graph["masks"][node_name] for node_name in resource_owners]
        strict_masks = strict.get(resource_key, [])
        optimistic_masks = optimistic.get(resource_key, [])
        record = {
            "resource": resource_key,
            "owners": resource_owners,
            "strict_masks": [labels_from_mask(mask, graph) for mask in strict_masks],
            "optimistic_masks": [labels_from_mask(mask, graph) for mask in optimistic_masks],
            "seed_reasons": seed_reasons.get(resource_key, []),
            "active_producers": sorted(
                recipe.recipe_id for recipe in active.values()
                if resource_key in {output.key for output in recipe.outputs if not output.tag}
            ),
            "active_producer_details": sorted((
                {
                    "recipe_id": recipe.recipe_id,
                    "recipe_type": recipe.recipe_type,
                    "stage": recipe.stage,
                    "source": recipe.source,
                    "strict_unresolved_groups": unresolved_recipe_groups(recipe, strict, tags),
                    "optimistic_unresolved_groups": unresolved_recipe_groups(recipe, optimistic, tags),
                }
                for recipe in active.values()
                if resource_key in {output.key for output in recipe.outputs if not output.tag}
            ), key=lambda value: value["recipe_id"]),
        }
        owned_results.append(record)
        is_natural_feedstock = resource_key in seeds and any(fragment in resource_key for fragment in natural_feedstock_fragments)
        if is_natural_feedstock:
            findings.append(finding(
                "info", "intentional_natural_feedstock", resource_key,
                "The resource is naturally obtainable; progression must be enforced on its processing routes rather than acquisition.",
                owners=resource_owners, seed_reasons=seed_reasons.get(resource_key, []),
            ))
            continue
        if (
            resource_key in {
                "item:ae2:silicon_press", "item:ae2:logic_processor_press",
                "item:ae2:calculation_processor_press", "item:ae2:engineering_processor_press",
            }
            and "ae2_meteorite_mysterious_cube_drop" in seed_reasons.get(resource_key, [])
        ):
            findings.append(finding(
                "info", "intentional_loot_bootstrap", resource_key,
                "AE2 intentionally bootstraps this processor press from a Mysterious Cube in its active meteorite structure; exact stages apply to duplication/processing recipes, not acquisition of the first press.",
                owners=resource_owners, seed_reasons=seed_reasons.get(resource_key, []),
            ))
            continue
        dynamic_reason = intentional_dynamic_reason(resource_key)
        if dynamic_reason:
            findings.append(finding(
                "info", "intentional_dynamic_output", resource_key,
                "No static recipe is expected for this resource; downstream reachability starts at its owning stage.",
                owners=resource_owners, dynamic_source=dynamic_reason,
                active_producers=record["active_producers"],
            ))
            continue
        if not optimistic_masks:
            producer_details = []
            for recipe_id in record["active_producers"]:
                producer = active[recipe_id]
                producer_details.append({
                    "recipe_id": recipe_id,
                    "recipe_type": producer.recipe_type,
                    "stage": producer.stage,
                    "source": producer.source,
                    "unresolved_groups": unresolved_recipe_groups(producer, optimistic, tags),
                })
            if producer_details:
                severity = "critical" if resource_key.startswith(("chemical:mekanism:", "item:bigreactors:yellorium")) else "high"
                findings.append(finding(
                    severity, "blocked_owned_output", resource_key,
                    "Recipes exist, but every production route is blocked by unavailable ingredients or machines.",
                    owners=resource_owners, producers=producer_details,
                ))
            else:
                findings.append(finding(
                    "critical", "unreachable_owned_output", resource_key,
                    "No active recipe produces this progression-owned resource and no verified dynamic-source exception applies.",
                    owners=resource_owners, active_producers=[],
                ))
            continue
        if not strict_masks:
            findings.append(finding(
                "medium", "unknown_seed_only", resource_key,
                "The only static path depends on an unverified external/dynamic seed.",
                owners=resource_owners, optimistic_masks=record["optimistic_masks"],
            ))
        best_expected = min(expected_masks, key=lambda value: value.bit_count())
        masks_to_check = strict_masks or optimistic_masks
        violating = [mask for mask in masks_to_check if not any((mask | expected) == mask for expected in expected_masks)]
        if violating:
            severity = "critical" if resource_key.startswith(("item:mekanism:", "item:bigreactors:", "item:allthemodium:", "chemical:mekanism:", "item:industrial_colonies:")) else "high"
            findings.append(finding(
                severity, "early_unlock_bypass", resource_key,
                "At least one complete recipe/machine path omits required Draw.io prerequisites.",
                owners=resource_owners,
                bypass_masks=[labels_from_mask(mask, graph) for mask in violating],
                expected_masks=[labels_from_mask(mask, graph) for mask in expected_masks],
            ))
        if not any((mask | best_expected) == best_expected for mask in masks_to_check):
            findings.append(finding(
                "high", "not_reachable_at_intended_stage", resource_key,
                "Every path requires a sibling/downstream node, so the resource cannot be produced when its owning node unlocks.",
                owners=resource_owners, actual_masks=[labels_from_mask(mask, graph) for mask in masks_to_check],
            ))

    downstream_ingredient_results: list[dict[str, Any]] = []
    for recipe in active.values():
        output_owners = {
            node_name
            for output in recipe.outputs
            for node_name in owners.get(output.key, set())
        }
        if not output_owners:
            continue
        for group in recipe.inputs:
            expanded: set[str] = set()
            for resource in group:
                if resource.tag:
                    expanded.update(f"{resource.kind}:{member}" for member in expand_tag(tags, resource.kind, resource.resource_id))
                else:
                    expanded.add(resource.key)
            input_owners = {node_name for resource in expanded for node_name in owners.get(resource, set())}
            if not input_owners:
                continue
            valid_pairs = [
                (input_node, output_node)
                for input_node in input_owners
                for output_node in output_owners
                if (graph["masks"][input_node] | graph["masks"][output_node]) == graph["masks"][output_node]
            ]
            if valid_pairs:
                continue
            evidence = {
                "recipe_id": recipe.recipe_id,
                "recipe_type": recipe.recipe_type,
                "stage": recipe.stage,
                "source": recipe.source,
                "input_resources": sorted(expanded),
                "input_owners": sorted(input_owners),
                "output_resources": sorted(output.key for output in recipe.outputs if output.key in owners),
                "output_owners": sorted(output_owners),
            }
            downstream_ingredient_results.append(evidence)
            stage_is_output = recipe.stage in output_owners
            findings.append(finding(
                "high" if stage_is_output else "medium", "downstream_owned_ingredient", recipe.recipe_id,
                "A recipe for a progression-owned output requires an item owned only by sibling/downstream nodes.",
                **{key: value for key, value in evidence.items() if key != "recipe_id"},
            ))

    output_producers: dict[str, list[str]] = defaultdict(list)
    for recipe in active.values():
        for output in recipe.outputs:
            if not output.tag:
                output_producers[output.key].append(recipe.recipe_id)
    deprecated_outputs = {
        f"item:{output}"
        for group in json_read(project / "tools" / "canonicalization_policies.json").get("groups", [])
        for output in group.get("deprecated_outputs", [])
        if output.count(":") == 1 and not output.endswith(("_oil", "diesel", "gasoline", "biodiesel"))
    }
    removal_results: list[dict[str, Any]] = []
    for record in removed:
        outputs = record["outputs"]
        replacements = sorted({recipe_id for output in outputs for recipe_id in output_producers.get(output, [])})
        status = "replacement_present" if replacements else "no_replacement"
        intentional_dynamic = bool(outputs) and all(intentional_dynamic_reason(output) for output in outputs)
        intentional = (
            "retirement" in record["removed_by"]
            or "canonicalization" in record["removed_by"]
            or record["removed_by"] in INTENTIONAL_RETIREMENT_SCRIPTS
            or any(output in deprecated_outputs for output in outputs)
            or intentional_dynamic
        )
        record = {
            **record,
            "status": status,
            "replacement_recipes": replacements,
            "intentional_retirement": intentional,
            "intentional_runtime_replacement": intentional_dynamic,
        }
        removal_results.append(record)
        if status == "no_replacement" and not intentional:
            owned_outputs = sorted(output for output in outputs if output in owners)
            findings.append(finding(
                "high" if owned_outputs else "low", "removed_without_replacement", record["recipe_id"],
                "An active recipe was removed and no remaining recipe produces its output.",
                outputs=outputs, owned_outputs=owned_outputs, removed_by=record["removed_by"], original_source=record["original_source"],
            ))

    missing_stage_recipes = sorted(set(stage_map) - set(active))
    for recipe_id in missing_stage_recipes:
        findings.append(finding(
            "high", "staged_recipe_missing", recipe_id,
            "An exact stage mapping points to no active recipe.", node=stage_map[recipe_id],
        ))

    for recipe in active.values():
        if recipe.outputs:
            owned_outputs = sorted(output.key for output in recipe.outputs if output.key in owners)
            if not recipe.inputs and (recipe.source_kind == "kubejs" or recipe.recipe_id in stage_map or owned_outputs):
                findings.append(finding(
                    "high", "recipe_input_unparsed", recipe.recipe_id,
                    "The active custom/staged/owned-output recipe has no statically recognized input; it may appear as a free production route.",
                    recipe_type=recipe.recipe_type, source=recipe.source, owned_outputs=owned_outputs,
                ))
            continue
        if recipe.source_kind == "kubejs" or recipe.recipe_id in stage_map:
            findings.append(finding(
                "high", "recipe_output_unparsed", recipe.recipe_id,
                "The active custom/staged recipe has no statically recognized output; reachability cannot be trusted until its schema is supported.",
                recipe_type=recipe.recipe_type, source=recipe.source,
            ))

    nuclear_findings, nuclear_policy = special_nuclear_findings(active, tags, stage_map)
    findings.extend(nuclear_findings)

    # Tag aliases are reported for every input tag used by a progression-owned output recipe.
    alias_results: list[dict[str, Any]] = []
    for recipe in active.values():
        owned_outputs = sorted(output.key for output in recipe.outputs if output.key in owners)
        if not owned_outputs:
            continue
        for group in recipe.inputs:
            for resource in group:
                if not resource.tag:
                    continue
                members = expand_tag(tags, resource.kind, resource.resource_id)
                namespaces = sorted({member.split(":", 1)[0] for member in members})
                alias = {
                    "recipe_id": recipe.recipe_id,
                    "recipe_type": recipe.recipe_type,
                    "tag": resource.key,
                    "members": members,
                    "namespaces": namespaces,
                    "owned_outputs": owned_outputs,
                }
                alias_results.append(alias)
                if len(namespaces) > 1:
                    findings.append(finding(
                        "medium", "cross_mod_tag_alias_review", recipe.recipe_id,
                        "A recipe producing a progression-owned output accepts a tag populated by multiple mod namespaces.",
                        tag=resource.key, members=members, owned_outputs=owned_outputs,
                    ))

    project_capture = capture_kubejs(project, project / "pack-scripts" / "server_scripts", node)
    live_hashes = {path.name: sha256(path) for path in sorted(live_scripts.glob("*.js"))}
    project_hashes = {path.name: sha256(path) for path in sorted((project / "pack-scripts/server_scripts").glob("*.js"))}
    script_drift = [
        {"script": name, "live_sha256": live_hashes.get(name), "project_sha256": project_hashes.get(name)}
        for name in sorted(set(live_hashes) | set(project_hashes))
        if live_hashes.get(name) != project_hashes.get(name)
    ]

    stage_entry_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in stage_entries:
        stage_entry_groups[entry["recipe_id"]].append(entry)
    repeated_stage_rows = [
        {
            "recipe_id": recipe_id,
            "row_count": len(entries),
            "nodes": sorted({entry["node"] for entry in entries}),
            "reasons": sorted({entry["reason"] for entry in entries}),
            "sources": sorted({entry["source"] for entry in entries}),
        }
        for recipe_id, entries in sorted(stage_entry_groups.items())
        if len(entries) > 1
    ]
    stage_gap_groups = build_stage_gap_groups(findings, active, owners)
    blocker_cascades = build_blocker_cascades(findings, active, optimistic, tags)
    serializer_results = serializer_coverage(active)
    dynamic_exception_results = {
        "owned_runtime_outputs": [
            entry for entry in findings if entry["category"] == "intentional_dynamic_output"
        ],
        "removed_static_recipes_replaced_by_runtime_mechanics": [
            record for record in removal_results if record.get("intentional_runtime_replacement")
        ],
        "intentional_removed_recipe_retirements": [
            record for record in removal_results
            if record.get("status") == "no_replacement"
            and record.get("intentional_retirement")
            and not record.get("intentional_runtime_replacement")
        ],
    }

    severity_counts = Counter(entry["severity"] for entry in findings)
    ordered_severity = {severity: severity_counts.get(severity, 0) for severity in SEVERITY_ORDER}
    findings.sort(key=lambda entry: (
        SEVERITY_ORDER[entry["severity"]],
        CATEGORY_PRIORITY.get(entry["category"], 100),
        entry["category"],
        entry["subject"],
    ))
    recipe_types = Counter(recipe.recipe_type for recipe in active.values())
    active_by_source = Counter(recipe.source_kind for recipe in active.values())
    report = {
        "schema_version": 1,
        "scope": "Every recipe JSON in every live dependency JAR plus the selected project/live KubeJS registration, removal, and tag operations executed in deterministic filename order.",
        "instance": str(instance),
        "project": str(project),
        "recipe_script_source": args.scripts_source,
        "recipe_script_directory": str(selected_scripts),
        "drawio_source": graph["raw"].get("source"),
        "drawio_source_sha256": graph["raw"].get("source_sha256"),
        "counts": {
            "jars": sum(record["kind"] == "mod" for record in jar_scan["jars"]),
            "vanilla_data_jars": sum(record["kind"] == "vanilla" for record in jar_scan["jars"]),
            "jar_recipe_definitions": len(jar_scan["definitions"]),
            "inactive_known_conditions": sum(recipe.condition_state == "inactive" for recipe in jar_scan["definitions"]),
            "active_unknown_conditions": sum(recipe.condition_state == "active_unknown_condition" for recipe in jar_scan["definitions"]),
            "duplicate_recipe_ids": duplicate_definitions,
            "active_recipes": len(active),
            "active_jar_recipes": active_by_source["jar"],
            "active_kubejs_recipes": active_by_source["kubejs"],
            "active_verified_dynamic_routes": active_by_source["verified_dynamic"],
            "selected_conditional_recipes": len(jar_scan["selected_conditional_recipes"]),
            "kubejs_scripts": len(kube_capture["scripts"]),
            "kubejs_operations": len(kube_capture["operations"]),
            "kubejs_recipe_additions": sum(op.get("domain") == "recipe" and op.get("action") == "add" for op in kube_capture["operations"]),
            "kubejs_recipe_removal_operations": sum(op.get("domain") == "recipe" and op.get("action") == "remove" for op in kube_capture["operations"]),
            "actual_recipe_removals": len(removed),
            "intentional_removed_recipe_retirements": len(
                dynamic_exception_results["intentional_removed_recipe_retirements"]
            ),
            "tag_operations": sum(op.get("domain") == "tag" for op in kube_capture["operations"]),
            "merged_tags": len(tags),
            "stage_manifest_rows": len(stage_entries),
            "exact_stage_mappings": len(stage_map),
            "repeated_same_stage_recipe_rows": len(repeated_stage_rows),
            "active_staged_recipes": sum(recipe_id in active for recipe_id in stage_map),
            "missing_staged_recipes": len(missing_stage_recipes),
            "drawio_nodes": len(graph["labels"]),
            "drawio_edges": len(graph["raw"]["edges"]),
            "owned_resources": len(owners),
            "downstream_owned_ingredient_routes": len(downstream_ingredient_results),
            "verified_seeds": len(seeds),
            "strict_reachable_resources": len(strict),
            "optimistic_reachable_resources": len(optimistic),
            "strict_fixed_point_passes": strict_passes,
            "optimistic_fixed_point_passes": optimistic_passes,
            "findings": len(findings),
        },
        "severity_counts": ordered_severity,
        "recipe_type_counts": dict(sorted(recipe_types.items(), key=lambda item: (-item[1], item[0]))),
        "verified_dynamic_routes": verified_dynamic_routes,
        "effective_condition_flags": effective_condition_flags,
        "condition_config_sources": {
            "createappliedkinetics:ae2_overwrite": str(create_applied_config),
        },
        "selected_conditional_recipes": jar_scan["selected_conditional_recipes"],
        "serializer_coverage": serializer_results,
        "nuclear_policy": nuclear_policy,
        "repair_plan": {
            "root_blocker_cascades": blocker_cascades,
            "missing_or_mismatched_exact_stage_groups": stage_gap_groups,
            "known_dynamic_source_exceptions": dynamic_exception_results,
        },
        "findings": findings,
        "owned_resource_results": owned_results,
        "downstream_owned_ingredient_results": downstream_ingredient_results,
        "removed_recipe_results": removal_results,
        "progression_tag_aliases": alias_results,
        "missing_stage_recipes": missing_stage_recipes,
        "stage_entries": stage_entries,
        "repeated_same_stage_recipe_rows": repeated_stage_rows,
        "script_drift": script_drift,
        "kubejs_capture_errors": kube_capture["errors"],
        "project_kubejs_capture_errors": project_capture["errors"],
        "jar_scan_errors": jar_scan["errors"],
        "jar_inventory": jar_scan["jars"],
        "methodology": {
            "recipe_id_conflict_policy": "Deterministic lexicographic JAR order; later definition wins before KubeJS operations.",
            "tag_policy": "JAR tag replace/add layers followed by executed KubeJS clear/add/remove operations.",
            "stage_policy": (
                f"{len(stage_entries)} manifest rows de-duplicated to {len(stage_map)} exact recipe IDs; "
                "same-node repeated IDs may intentionally track multiple outputs of one machine recipe."
            ),
            "reachability_policy": "Pareto-minimal Draw.io prerequisite masks across recipe ingredients, expanded tags, exact recipe stages, and machine prerequisites.",
            "strict_seeds": "Verified natural tag roots, vanilla recipe-less resources, and explicit world fluids; owned runtime outputs enter at their Draw.io owner stage.",
            "optimistic_seeds": "Strict seeds plus registered, unowned recipe inputs that have no static producer.",
            "limitations": [
                "Known runtime-only transformations are classified explicitly and enter downstream reachability at their owner stage; unknown external inputs remain optimistic-only.",
                "Unknown third-party recipe conditions are included and counted as active_unknown_condition.",
                "Recipe serializer schemas with unrecognized output fields are explicitly reported.",
            ],
        },
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown_path.write_text(markdown_report(report), encoding="utf-8")

    print(
        f"Scanned {report['counts']['jars']} JARs / {report['counts']['jar_recipe_definitions']} recipe definitions; "
        f"resolved {report['counts']['active_recipes']} active recipes and {report['counts']['exact_stage_mappings']} exact stage mappings."
    )
    print(
        "Findings: " + ", ".join(f"{severity}={count}" for severity, count in ordered_severity.items())
    )
    print(f"JSON: {report_path}")
    print(f"Markdown: {markdown_path}")
    return 1 if severity_counts.get("critical", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
