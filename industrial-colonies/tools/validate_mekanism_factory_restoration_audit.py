#!/usr/bin/env python3
"""Validate the installer-only Mekanism Factory progression contract.

The pack deliberately disables all direct Factory recipes.  The only supported
construction route is Mekanism's state-preserving Tier Installer interaction,
backed by four difficult managed installer recipes.  This audit pins both the
installed recipe/runtime evidence and the exact blacklist boundary needed to
keep that route usable while Energy Cubes remain on their own recipe ladder.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from generate_managed_recipe_overhaul import compile_manifest


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PROJECT / "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json"
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
COUNTED_REF = re.compile(r"^(?:(\d+)x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)$")

TIERS = ("basic", "advanced", "elite", "ultimate")
PROCESSES = (
    "combining",
    "compressing",
    "crushing",
    "enriching",
    "infusing",
    "injecting",
    "purifying",
    "sawing",
)
ALL_PROCESSES = (*PROCESSES, "smelting")
BASE_MACHINES = {
    "combining": "mekanism:combiner",
    "compressing": "mekanism:osmium_compressor",
    "crushing": "mekanism:crusher",
    "enriching": "mekanism:enrichment_chamber",
    "infusing": "mekanism:metallurgic_infuser",
    "injecting": "mekanism:chemical_injection_chamber",
    "purifying": "mekanism:purification_chamber",
    "sawing": "mekanism:precision_sawmill",
    "smelting": "mekanism:energized_smelter",
}
GENERAL_NODES = {
    "basic": "CR01 — Modular Machinery",
    "advanced": "CR01 — Reinforced Systems",
    "elite": "CR01 — Precision Engineering",
    "ultimate": "CR01 — High-Energy Distribution",
}
CHEMICAL_NODE = "CR01 — Chemical Separation"
RUNTIME_CLASSES = {
    "mekanism/common/registries/MekanismBlockTypes.class",
    "mekanism/common/registries/MekanismItems.class",
    "mekanism/common/item/ItemTierInstaller.class",
    "mekanism/common/content/blocktype/Machine$FactoryMachine.class",
    "mekanism/common/content/blocktype/Factory.class",
    "mekanism/common/block/attribute/AttributeUpgradeable.class",
    "mekanism/api/MekanismAPITags$Blocks.class",
    "mekanism/common/content/blocktype/FactoryType.class",
    "mekanism/common/tier/FactoryTier.class",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def output_id(recipe: dict[str, Any]) -> str | None:
    value = recipe.get("output")
    if isinstance(value, str):
        match = COUNTED_REF.fullmatch(value.strip())
        return match.group(2) if match else None
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return value["id"]
    return None


def result(document: dict[str, Any]) -> tuple[str | None, int]:
    value = document.get("result")
    if not isinstance(value, dict):
        return None, 0
    count = value.get("count", 1)
    return value.get("id") if isinstance(value.get("id"), str) else None, count if isinstance(count, int) else 0


def identity(tier: str, process: str) -> tuple[str, str, str]:
    return (
        f"mekanism:factory/{tier}/{process}",
        f"data/mekanism/recipe/factory/{tier}/{process}.json",
        f"mekanism:{tier}_{process}_factory",
    )


def predecessor(tier: str, process: str) -> str:
    if tier == "basic":
        return BASE_MACHINES[process]
    prior = {"advanced": "basic", "elite": "advanced", "ultimate": "elite"}[tier]
    return f"mekanism:{prior}_{process}_factory"


def plan_maps(plan: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    tiers = {str(entry.get("tier")): entry for entry in plan.get("tiers", []) if isinstance(entry, dict)}
    processes = {
        str(entry.get("process")): entry
        for entry in plan.get("processes", [])
        if isinstance(entry, dict)
    }
    return tiers, processes


def proposed_specs(plan: dict[str, Any]) -> list[dict[str, Any]]:
    tier_map, process_map = plan_maps(plan)
    contract = plan["mechanical_crafting_contract"]
    specs: list[dict[str, Any]] = []
    for tier in TIERS:
        tier_entry = tier_map[tier]
        for process in PROCESSES:
            process_entry = process_map[process]
            phase = (
                str(process_entry["forced_phase"])
                if process_entry.get("phase_policy") == "forced"
                else str(tier_entry["general_phase"])
            )
            key = dict(contract["fixed_key"])
            key.update(
                {
                    "A": str(tier_entry["alloy"]),
                    "C": str(tier_entry["control"]),
                    "P": str(tier_entry["precision_component"]),
                    "T": str(tier_entry["installer"]),
                    "X": predecessor(tier, process),
                    "R": str(process_entry["process_anchor"]),
                }
            )
            stock_id, _, output = identity(tier, process)
            specs.append(
                {
                    "id": f"industrial_colonies:mekanism/factory/{tier}_{process}",
                    "type": "mechanical_crafting",
                    "phase": phase,
                    "order": int(tier_entry["order"]) + int(process_entry["order"]),
                    "comment": f"Construct the {tier.title()} {process.title()} Factory as a fresh-state 5x5 assembly.",
                    "pattern": list(contract["pattern"]),
                    "key": key,
                    "output": output,
                    "remove": [stock_id],
                    "exclusive_output": True,
                }
            )
    return specs


def expected_assignment_delta() -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    additions = {
        (GENERAL_NODES[tier], f"mekanism:{tier}_{process}_factory")
        for tier in TIERS
        for process in ("crushing", "sawing")
    }
    additions.update(
        (CHEMICAL_NODE, f"mekanism:{tier}_{process}_factory")
        for tier in TIERS
        for process in ("injecting", "purifying")
    )
    removals = {
        (GENERAL_NODES[tier], f"mekanism:{tier}_{process}_factory")
        for tier in TIERS
        for process in ("injecting", "purifying")
    }
    return additions, removals


def flatten_delta(entries: Any) -> set[tuple[str, str]]:
    if not isinstance(entries, list):
        return set()
    return {
        (str(entry.get("node")), str(output))
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("outputs"), list)
        for output in entry["outputs"]
    }


def expected_blacklist(plan: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    closure = plan["installer_bypass_closure"]
    factory = set(map(str, closure["factory_base_blocks"]))
    factory.update(
        f"mekanism:{tier}_{process}_factory"
        for tier in closure["factory_tiers"]
        for process in closure["factory_processes"]
    )
    cubes = set(map(str, closure["energy_cube_blocks"]))
    transmitters = set(map(str, closure["excluded_transmitter_blocks"]))
    return factory, cubes, transmitters


def has_cycle(specs: list[dict[str, Any]]) -> bool:
    outputs = {str(spec["output"]) for spec in specs}
    graph = {
        str(spec["output"]): {str(spec["key"]["X"])} & outputs
        for spec in specs
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph[node]):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def validate(args: argparse.Namespace) -> tuple[list[str], dict[str, int]]:
    plan = load_json(args.plan.resolve())
    seed = load_json(args.seed.resolve())
    manifest = load_json(args.manifest.resolve())
    assignments = load_json(args.assignments.resolve())
    failures: list[str] = []

    if plan.get("schema_version") != 3:
        failures.append("plan must use schema_version 3")
    tier_map, process_map = plan_maps(plan)
    if set(tier_map) != set(TIERS) or len(plan.get("tiers", [])) != 4:
        failures.append("plan must define exactly Basic, Advanced, Elite, and Ultimate tiers")
    if set(process_map) != set(PROCESSES) or len(plan.get("processes", [])) != 8:
        failures.append("plan must define exactly the eight non-smelting Factory processes")
    if failures:
        return failures, {"sources": 0, "contracts": 0, "blacklist": 0, "active_upgrades": 0, "assignments": 0}

    scope = plan.get("scope", {})
    jars = sorted(args.mods.resolve().glob("Mekanism-1.21.1-*.jar"))
    if len(jars) != 1:
        failures.append(f"expected one installed Mekanism JAR, found {len(jars)}")
        return failures, {"sources": 0, "contracts": 0, "blacklist": 0, "active_upgrades": 0, "assignments": 0}
    jar = jars[0]
    actual_jar_hash = sha256(jar.read_bytes())
    if jar.name != scope.get("installed_mod"):
        failures.append(f"installed Mekanism JAR changed: {jar.name}")
    if actual_jar_hash != scope.get("installed_mod_sha256"):
        failures.append(f"installed Mekanism JAR hash changed: {actual_jar_hash}")

    catalog_by_id = {row["recipe_id"]: row for row in load_csv(args.catalog.resolve() / "recipes.csv")}
    catalog_items = {row["item_id"] for row in load_csv(args.catalog.resolve() / "items.csv")}
    source_hashes = plan.get("source_sha256", {})
    expected_source_ids = {
        identity(tier, process)[0]
        for tier in TIERS
        for process in ALL_PROCESSES
    }
    if set(source_hashes) != expected_source_ids:
        failures.append("source_sha256 must pin exactly all 36 installed Factory sources")

    runtime_hashes = plan.get("runtime_class_sha256", {})
    if set(runtime_hashes) != RUNTIME_CLASSES:
        failures.append("runtime_class_sha256 does not pin the exact reviewed class set")

    stock_template = plan.get("source_template", {})
    stock_pattern = stock_template.get("pattern")
    stock_tier_keys = stock_template.get("tier_keys", {})
    with zipfile.ZipFile(jar) as archive:
        names = set(archive.namelist())
        installed_factory_paths = {
            name
            for name in names
            if re.fullmatch(r"data/mekanism/recipe/factory/(?:basic|advanced|elite|ultimate)/(?:combining|compressing|crushing|enriching|infusing|injecting|purifying|sawing|smelting)\.json", name)
        }
        expected_paths = {
            identity(tier, process)[1]
            for tier in TIERS
            for process in ALL_PROCESSES
        }
        if installed_factory_paths != expected_paths:
            failures.append("installed JAR Factory source path set is no longer exactly 36 audited files")

        for tier in TIERS:
            for process in ALL_PROCESSES:
                recipe_id, source_path, expected_output = identity(tier, process)
                row = catalog_by_id.get(recipe_id)
                if row is None:
                    failures.append(f"installed catalog is missing {recipe_id}")
                else:
                    if row.get("recipe_type") != "mekanism:mek_data":
                        failures.append(f"{recipe_id}: expected mekanism:mek_data in catalog")
                    if row.get("source_path") != source_path:
                        failures.append(f"{recipe_id}: catalog source path changed")
                    outputs = {part.strip() for part in row.get("outputs", "").split("|") if part.strip()}
                    if outputs != {expected_output}:
                        failures.append(f"{recipe_id}: catalog output changed: {sorted(outputs)}")
                if source_path not in names:
                    failures.append(f"installed JAR is missing {source_path}")
                    continue
                payload = archive.read(source_path)
                if sha256(payload) != source_hashes.get(recipe_id):
                    failures.append(f"{recipe_id}: installed source hash changed")
                document = json.loads(payload)
                actual_output, actual_count = result(document)
                if document.get("type") != "mekanism:mek_data" or actual_output != expected_output or actual_count != 1:
                    failures.append(f"{recipe_id}: installed type/result contract changed")
                if document.get("pattern") != stock_pattern:
                    failures.append(f"{recipe_id}: installed stock pattern changed")
                expected_key = dict(stock_tier_keys.get(tier, {}))
                expected_key["P"] = {"item": predecessor(tier, process)}
                if document.get("key") != expected_key:
                    failures.append(f"{recipe_id}: installed stock ingredient key changed")

        runtime_payloads: dict[str, bytes] = {}
        for class_path in RUNTIME_CLASSES:
            if class_path not in names:
                failures.append(f"installed JAR is missing reviewed runtime class {class_path}")
                continue
            payload = archive.read(class_path)
            runtime_payloads[class_path] = payload
            if sha256(payload) != runtime_hashes.get(class_path):
                failures.append(f"reviewed runtime class hash changed: {class_path}")
        required_literals = {
            "mekanism/common/item/ItemTierInstaller.class": (b"BLACKLIST_INSTALLER_UPGRADEABLE", b"AttributeUpgradeable", b"fromTier", b"toTier"),
            "mekanism/api/MekanismAPITags$Blocks.class": (b"blacklist/installer_upgradeable",),
            "mekanism/common/content/blocktype/Machine$FactoryMachine.class": (b"AttributeUpgradeable",),
            "mekanism/common/content/blocktype/Factory.class": (b"AttributeUpgradeable", b"FACTORY_TIERS"),
            "mekanism/common/registries/MekanismBlockTypes.class": (b"createEnergyCube", b"createTransmitter", b"AttributeUpgradeable", b"AttributeTier"),
            "mekanism/common/registries/MekanismItems.class": (b"ItemTierInstaller",),
        }
        for class_path, literals in required_literals.items():
            payload = runtime_payloads.get(class_path, b"")
            for literal in literals:
                if literal not in payload:
                    failures.append(f"reviewed runtime literal {literal!r} is absent from {class_path}")

    contract = plan.get("installer_upgrade_contract", {})
    expected_installer_ids = {
        tier: f"industrial_colonies:mekanism/tier_installer/{tier}"
        for tier in TIERS
    }
    expected_state_fields = {
        "inventory", "tanks", "energy", "upgrades", "side_configuration",
        "ownership", "security",
    }
    if contract.get("construction_route") != "right_click_immediate_predecessor_with_tier_installer":
        failures.append("Factory construction route must be the Tier Installer right-click interaction")
    if contract.get("installer_consumed") is not True:
        failures.append("Factory upgrade contract must consume the Tier Installer")
    if contract.get("direct_factory_recipes_disabled") is not True:
        failures.append("Factory upgrade contract must disable direct Factory recipes")
    if contract.get("managed_factory_recipe_count") != 0 or contract.get("runtime_factory_output_count") != 36:
        failures.append("Factory route counts must remain zero managed cards and 36 runtime outputs")
    if contract.get("state_transfer") != "mekanism_copies_tile_data":
        failures.append("Factory upgrade contract lost Mekanism tile-data transfer")
    if set(contract.get("state_fields", [])) != expected_state_fields:
        failures.append("Factory upgrade state-transfer field inventory changed")
    if contract.get("tier_installer_recipe_ids") != expected_installer_ids:
        failures.append("Factory upgrade contract must name the four managed Tier Installer recipes")
    if contract.get("energy_cube_policy") != "separate_managed_recipe_ladder":
        failures.append("Energy Cubes must remain on their separate managed recipe ladder")

    manifest_by_id = {
        str(recipe.get("id")): recipe
        for recipe in manifest.get("recipes", [])
        if isinstance(recipe, dict)
    }
    for tier, recipe_id in expected_installer_ids.items():
        recipe = manifest_by_id.get(recipe_id)
        output = f"mekanism:{tier}_tier_installer"
        stock_id = f"mekanism:tier_installer/{tier}"
        if recipe is None:
            failures.append(f"managed Tier Installer recipe is missing: {recipe_id}")
            continue
        if output_id(recipe) != output:
            failures.append(f"{recipe_id}: output changed from {output}")
        if set(recipe.get("remove", [])) != {stock_id}:
            failures.append(f"{recipe_id}: must remove exactly {stock_id}")

    factory_blacklist, cube_blacklist, excluded_transmitters = expected_blacklist(plan)
    expected_factory_blacklist: set[str] = set()
    expected_cubes = {f"mekanism:{tier}_energy_cube" for tier in TIERS}
    expected_transmitters = {
        f"mekanism:{tier}_{suffix}"
        for tier in TIERS
        for suffix in (
            "universal_cable",
            "mechanical_pipe",
            "pressurized_tube",
            "logistical_transporter",
            "thermodynamic_conductor",
        )
    }
    if factory_blacklist != expected_factory_blacklist:
        failures.append("installer blacklist must not block any Factory predecessor")
    if cube_blacklist != expected_cubes:
        failures.append("installer blacklist Energy Cube family must be exactly the four owned cubes")
    if excluded_transmitters != expected_transmitters:
        failures.append("transmitter exclusion must enumerate exactly the 20 reviewed tiered transmitters")
    required_blacklist = factory_blacklist | cube_blacklist
    if len(required_blacklist) != 4 or plan["installer_bypass_closure"].get("exact_required_value_count") != 4:
        failures.append("installer blacklist must contain exactly the four owned Energy Cubes")
    if required_blacklist & excluded_transmitters:
        failures.append("transmitters must remain excluded from the installer blacklist")
    if not required_blacklist.issubset(catalog_items):
        failures.append(f"installer blacklist contains absent installed blocks: {sorted(required_blacklist - catalog_items)}")

    blacklist_path = args.installer_blacklist.resolve()
    implemented = plan.get("status") == "implemented_in_seed"
    if blacklist_path.is_file():
        blacklist_document = load_json(blacklist_path)
        if blacklist_document.get("replace") is not False:
            failures.append("installer blacklist resource must use replace:false")
        values = blacklist_document.get("values")
        if not isinstance(values, list) or set(values) != required_blacklist or len(values) != 4:
            failures.append("installer blacklist resource does not contain the exact four-value contract")
    elif implemented:
        failures.append("implemented plan is missing the installer blacklist resource")

    additional_removals = set(seed.get("additional_removals", []))
    current_factory_removals = {value for value in additional_removals if value.startswith("mekanism:factory/")}
    direct_factory_ids = {
        identity(tier, process)[0]
        for tier in TIERS
        for process in ALL_PROCESSES
    }
    if plan.get("intentional_retirements") != []:
        failures.append("installer-only policy must not retire any Factory output")
    if current_factory_removals != direct_factory_ids:
        failures.append("all 36 direct Factory recipes must remain exact bare removals")

    seed_factory_owners = [
        recipe for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict) and output_id(recipe) in {identity(tier, process)[2] for tier in TIERS for process in ALL_PROCESSES}
    ]
    manifest_factory_outputs = [
        output_id(recipe)
        for recipe in manifest.get("recipes", [])
        if isinstance(recipe, dict) and output_id(recipe) in {identity(tier, process)[2] for tier in TIERS for process in ALL_PROCESSES}
    ]
    if seed_factory_owners or manifest_factory_outputs:
        failures.append("installer-only policy forbids managed Factory recipe owners")
    all_factory_outputs = {
        identity(tier, process)[2]
        for tier in TIERS
        for process in ALL_PROCESSES
    }
    excluded_factory_outputs = set(seed.get("exclude_outputs", [])) & all_factory_outputs
    if excluded_factory_outputs != all_factory_outputs:
        failures.append("all 36 Factory outputs must be excluded from recipe generation")
    runtime_predecessors = set(BASE_MACHINES.values()) | {
        f"mekanism:{tier}_{process}_factory"
        for tier in ("basic", "advanced", "elite")
        for process in ALL_PROCESSES
    }
    if runtime_predecessors & required_blacklist:
        failures.append("an installer-only Factory predecessor is blocked by the blacklist")
    energized_owner = [
        recipe for recipe in manifest.get("recipes", [])
        if isinstance(recipe, dict) and output_id(recipe) == "mekanism:energized_smelter"
    ]
    if len(energized_owner) != 1:
        failures.append("the Energized Smelter base machine must retain one managed recipe")
    if "mekanism:metallurgic_infuser" not in set(seed.get("user_owned_outputs", [])):
        failures.append("the player-authored Metallurgic Infuser output is no longer protected")

    expected_additions, expected_removals = expected_assignment_delta()
    delta = plan.get("assignment_delta", {})
    additions = flatten_delta(delta.get("additions"))
    removals = flatten_delta(delta.get("removals"))
    if additions != expected_additions or delta.get("addition_count") != 16:
        failures.append("assignment plan must contain the exact 16 additions")
    if removals != expected_removals or delta.get("removal_count") != 8:
        failures.append("assignment plan must contain the exact eight chemical-node moves")
    assignment_nodes = assignments.get("nodes", {})
    for node, output in additions:
        unlocks = assignment_nodes.get(node, {}).get("unlocks", [])
        if implemented and output not in unlocks:
            failures.append(f"implemented assignment is missing {output} from {node}")
        if not implemented and output in unlocks:
            failures.append(f"pre-integration assignment unexpectedly already contains {output} in {node}")
    for node, output in removals:
        unlocks = assignment_nodes.get(node, {}).get("unlocks", [])
        if implemented and output in unlocks:
            failures.append(f"implemented assignment still contains moved output {output} in {node}")
        if not implemented and output not in unlocks:
            failures.append(f"pre-integration assignment evidence changed: {output} is absent from {node}")
    phase_by_node = seed.get("phase_by_node", {})
    for tier, node in GENERAL_NODES.items():
        if phase_by_node.get(node) != tier_map[tier].get("general_phase"):
            failures.append(f"{node}: planned general phase does not match authoritative phase_by_node")
    if phase_by_node.get(CHEMICAL_NODE) != "Nuclear Engineering":
        failures.append("Chemical Separation must remain a Nuclear Engineering node")

    if (
        scope.get("replacement_count") != 0
        or scope.get("runtime_upgrade_output_count") != 36
        or scope.get("disabled_direct_recipe_count") != 36
        or scope.get("installed_factory_source_count") != 36
    ):
        failures.append("scope counts do not match 36 installer-only upgrades with zero direct replacements")
    return failures, {
        "sources": 36,
        "contracts": 36,
        "blacklist": len(required_blacklist),
        "active_upgrades": 36,
        "assignments": len(additions) + len(removals),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    result.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    result.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    result.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    result.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    result.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    result.add_argument(
        "--installer-blacklist",
        type=Path,
        default=PROJECT / "src/main/resources/data/mekanism/tags/block/blacklist/installer_upgradeable.json",
    )
    return result


def main() -> int:
    try:
        failures, counts = validate(parser().parse_args())
    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if failures:
        print(f"FAIL: {len(failures)} issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print(
        f"Checked {counts['sources']} hash-pinned installed Factory sources, "
        f"verified {counts['contracts']} installer-only runtime outputs, "
        f"and verified the exact {counts['blacklist']}-block Energy Cube closure."
    )
    print(
        "All 36 Factory base/lower-tier predecessors remain installer-upgradeable; "
        "the four Energy Cubes stay protected by their separate managed ladder."
    )
    print(
        f"PASS: all 36 direct Factory recipes are disabled, no Factory has a managed "
        f"recipe owner, and {counts['assignments']} assignment mutations are implemented exactly."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
