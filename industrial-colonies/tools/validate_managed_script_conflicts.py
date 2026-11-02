#!/usr/bin/env python3
"""Reject ownership conflicts between managed KJSGen cards and KubeJS scripts.

The managed manifest is the only owner of the broad machine-construction
overhaul.  Small KubeJS scripts still own canonical materials, nuclear
chemistry, compatibility repairs, primitive tools, and megaproject recipes.
This validator keeps those two recipe-authoring layers from silently deleting,
duplicating, hiding, or recreating one another's content.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCE = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
LITERAL_RESOURCE = re.compile(r"['\"]([a-z0-9_.-]+:[a-z0-9_./-]+)['\"]")
LITERAL_CUSTOM_ID = re.compile(
    r"\.id\(\s*['\"]([a-z0-9_.-]+:[a-z0-9_./-]+)['\"]\s*\)"
)
RECIPE_MUTATION = re.compile(
    r"\bevent\.(?:remove|removeAll|replaceInput|replaceOutput|custom|shaped|"
    r"shapeless|smelting|blasting|recipes)\s*\("
)
REMOVE_OBJECT = re.compile(r"\bevent\.remove\s*\(\s*\{(?P<body>[^{}]*)\}\s*\)", re.S)


ATM_METALS = ("allthemodium", "vibranium", "unobtainium")
ATM_METAL_FORMS = ("ingot", "nugget", "dust", "block", "plate", "gear", "rod")
ATM_ALLOYS = (
    "vibranium_allthemodium_alloy",
    "unobtainium_allthemodium_alloy",
    "unobtainium_vibranium_alloy",
)
ATM_ALLOY_FORMS = ("ingot", "dust", "block")

ATM_SCRIPT_OUTPUTS = {
    *(f"allthemodium:{metal}_{form}" for metal in ATM_METALS for form in ATM_METAL_FORMS),
    *(f"allthemodium:{alloy}_{form}" for alloy in ATM_ALLOYS for form in ATM_ALLOY_FORMS),
}

# These outputs have intentional, hand-audited script implementations.  They
# must never be auto-imported into the broad managed construction pass.
SCRIPT_OWNED_OUTPUTS: dict[str, set[str]] = {
    "industrial_allthemodium_currency.js": ATM_SCRIPT_OUTPUTS,
    "industrial_cast_iron_canonicalization.js": {
        "tfmg:cast_iron_ingot",
        "tfmg:cast_iron_nugget",
        "tfmg:cast_iron_sheet",
        "tfmg:cast_iron_block",
    },
    "industrial_copper_wire_canonicalization.js": {"tfmg:copper_wire"},
    "industrial_lead_canonicalization.js": {
        "tfmg:lead_ore",
        "tfmg:deepslate_lead_ore",
        "tfmg:raw_lead",
        "tfmg:raw_lead_block",
        "tfmg:lead_ingot",
        "tfmg:lead_nugget",
        "tfmg:lead_sheet",
        "tfmg:lead_block",
    },
    "industrial_steel_canonicalization.js": {
        "tfmg:steel_ingot",
        "tfmg:steel_nugget",
        "tfmg:steel_sheet",
        "tfmg:steel_block",
    },
    "industrial_sulfur_canonicalization.js": {
        "tfmg:sulfur_dust",
        "tfmg:sulfuric_acid_bucket",
    },
    "industrial_uranium_yellorium_separation.js": {
        "mekanism:raw_uranium",
        "mekanism:ingot_uranium",
        "mekanism:block_uranium",
        "mekanism:yellow_cake_uranium",
    },
    "industrial_yellorium_refinement.js": {
        "bigreactors:yellorium_ingot",
        "industrial_colonies:yellorium_compound",
    },
    "industrial_nuclear_fuel_01.js": {
        "industrial_colonies:enriched_uranium_fuel_pellet"
    },
    "industrial_nuclear_actinides_01.js": {"mekanism:nuclear_waste"},
    "industrial_black_hole_megaproject.js": {"industrial_colonies:black_hole"},
    "industrial_reserve_core_megaproject.js": {
        "industrial_colonies:industrial_reserve_core"
    },
    "industrial_star_megaproject.js": {"industrial_colonies:industrial_star"},
    "industrial_megacells_radioactive_compat.js": {
        "megacells:radioactive_chemical_cell"
    },
    "industrial_primitive_tool_progression.js": {
        "industrial_colonies:crude_flint_pickaxe",
        "modernfoundry:part_builder",
        "modernfoundry:tinker_station",
    },
}

# Only outputs which can be selected by the assignment importer need to be in
# exclude_outputs.  Keeping this explicit also documents why the exclusions
# are not accidental gaps in the managed overhaul.
MANDATORY_EXCLUSIONS = set().union(
    ATM_SCRIPT_OUTPUTS,
    SCRIPT_OWNED_OUTPUTS["industrial_cast_iron_canonicalization.js"],
    SCRIPT_OWNED_OUTPUTS["industrial_copper_wire_canonicalization.js"],
    SCRIPT_OWNED_OUTPUTS["industrial_lead_canonicalization.js"],
    SCRIPT_OWNED_OUTPUTS["industrial_steel_canonicalization.js"],
    SCRIPT_OWNED_OUTPUTS["industrial_sulfur_canonicalization.js"],
    SCRIPT_OWNED_OUTPUTS["industrial_uranium_yellorium_separation.js"],
    SCRIPT_OWNED_OUTPUTS["industrial_yellorium_refinement.js"],
    SCRIPT_OWNED_OUTPUTS["industrial_nuclear_fuel_01.js"],
    SCRIPT_OWNED_OUTPUTS["industrial_nuclear_actinides_01.js"],
)

FACTORY_TIERS = ("basic", "advanced", "elite", "ultimate")
FACTORY_KINDS = (
    "combining",
    "compressing",
    "crushing",
    "enriching",
    "infusing",
    "injecting",
    "purifying",
    "sawing",
    "smelting",
)
DIRECT_FACTORY_RECIPES = {
    f"mekanism:factory/{tier}/{kind}"
    for tier in FACTORY_TIERS
    for kind in FACTORY_KINDS
}
DIRECT_FACTORY_ITEMS = {
    f"mekanism:{tier}_{kind}_factory"
    for tier in FACTORY_TIERS
    for kind in FACTORY_KINDS
}
RESTORED_FACTORY_RECIPES = {
    f"mekanism:factory/{tier}/{kind}"
    for tier in FACTORY_TIERS
    for kind in FACTORY_KINDS
    if kind != "smelting"
}
RESTORED_FACTORY_ITEMS = {
    f"mekanism:{tier}_{kind}_factory"
    for tier in FACTORY_TIERS
    for kind in FACTORY_KINDS
    if kind != "smelting"
}
RETIRED_SMELTING_RECIPES = {
    f"mekanism:factory/{tier}/smelting" for tier in FACTORY_TIERS
}
RETIRED_SMELTING_ITEMS = {
    f"mekanism:{tier}_smelting_factory" for tier in FACTORY_TIERS
}
TIER_INSTALLER_POLICY = (
    "Tier installer is a general runtime utility; preserve its exact stock recipe and "
    "enforce managed factory/cube/transmitter ladders with the Mekanism installer blacklist."
)
TIER_INSTALLER_RESTORATION = {
    "mekanism:basic_tier_installer": {
        "recipe_id": "mekanism:tier_installer/basic",
        "node": "CR01 — Modular Machinery",
        "automatic_managed_id": "industrial_colonies:auto/mekanism/basic_tier_installer",
    },
    "mekanism:advanced_tier_installer": {
        "recipe_id": "mekanism:tier_installer/advanced",
        "node": "CR01 — Reinforced Systems",
        "automatic_managed_id": "industrial_colonies:auto/mekanism/advanced_tier_installer",
    },
    "mekanism:elite_tier_installer": {
        "recipe_id": "mekanism:tier_installer/elite",
        "node": "CR01 — Precision Engineering",
        "automatic_managed_id": "industrial_colonies:auto/mekanism/elite_tier_installer",
    },
    "mekanism:ultimate_tier_installer": {
        "recipe_id": "mekanism:tier_installer/ultimate",
        "node": "CR01 — High-Energy Distribution",
        "automatic_managed_id": "industrial_colonies:auto/mekanism/ultimate_tier_installer",
    },
}
TIER_INSTALLERS = set(TIER_INSTALLER_RESTORATION)
TIER_INSTALLER_RECIPES = {
    str(contract["recipe_id"]) for contract in TIER_INSTALLER_RESTORATION.values()
}
TIER_INSTALLER_AUTOMATIC_OWNERS = {
    str(contract["automatic_managed_id"])
    for contract in TIER_INSTALLER_RESTORATION.values()
}
TIER_INSTALLER_OUTPUT = re.compile(r"^mekanism:[a-z0-9_]+_tier_installer$")
TIER_INSTALLER_RECIPE = re.compile(r"^mekanism:tier_installer/[a-z0-9_]+$")
TIER_INSTALLER_AUTOMATIC_OWNER = re.compile(
    r"^industrial_colonies:auto/mekanism/[a-z0-9_]+_tier_installer$"
)


def assignment_nodes_by_output(assignments: dict[str, Any]) -> dict[str, set[str]]:
    """Return every documentation node which names an output."""
    result: dict[str, set[str]] = defaultdict(set)
    nodes = assignments.get("nodes")
    if not isinstance(nodes, dict):
        return result
    for node_name, node in nodes.items():
        if not isinstance(node_name, str) or not isinstance(node, dict):
            continue
        unlocks = node.get("unlocks")
        if not isinstance(unlocks, list):
            continue
        for output in unlocks:
            if isinstance(output, str):
                result[output].add(node_name)
    return result


def validate_tier_installer_restoration(
    restoration: dict[str, Any],
    seed: dict[str, Any],
    manifest: dict[str, Any],
    assignments: dict[str, Any],
    managed_outputs: set[str],
    managed_ids: set[str],
    removal_ids: set[str],
    additional_removals: set[str],
) -> list[str]:
    """Enforce the reviewed stock tier-installer policy and its live implementation."""
    errors: list[str] = []
    expected_outputs = set(TIER_INSTALLER_RESTORATION)
    expected_recipes = set(TIER_INSTALLER_RECIPES)
    expected_owners = set(TIER_INSTALLER_AUTOMATIC_OWNERS)

    expected_metadata = {
        "schema_version": 1,
        "status": "implemented",
        "batch_id": "stock_utility_restoration",
        "source_audit": "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json",
        "classification": "runtime_artifact_leave_stock",
        "decision": (
            "Retire automatic gate-ring owners and preserve every exact installed source producer."
        ),
    }
    for key, value in expected_metadata.items():
        if restoration.get(key) != value:
            errors.append(f"stock utility restoration {key} changed from the reviewed policy")

    artifact_outputs = {
        value
        for value in restoration.get("outputs_to_exclude", [])
        if isinstance(value, str) and TIER_INSTALLER_OUTPUT.fullmatch(value)
    }
    artifact_recipes = {
        value
        for value in restoration.get("recipe_ids_to_preserve", [])
        if isinstance(value, str) and TIER_INSTALLER_RECIPE.fullmatch(value)
    }
    artifact_owners = {
        value
        for value in restoration.get("automatic_managed_ids_to_retire", [])
        if isinstance(value, str) and TIER_INSTALLER_AUTOMATIC_OWNER.fullmatch(value)
    }
    if artifact_outputs != expected_outputs:
        errors.append(
            "stock utility restoration must contain exactly the four reviewed tier-installer outputs"
        )
    if artifact_recipes != expected_recipes:
        errors.append(
            "stock utility restoration must preserve exactly the four reviewed tier-installer recipes"
        )
    if artifact_owners != expected_owners:
        errors.append(
            "stock utility restoration must retire exactly the four reviewed automatic installer owners"
        )

    entries = restoration.get("entries")
    if not isinstance(entries, list):
        errors.append("stock utility restoration entries must be an array")
        entries = []
    installer_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and (
            isinstance(entry.get("output"), str)
            and TIER_INSTALLER_OUTPUT.fullmatch(str(entry["output"]))
            or isinstance(entry.get("source_recipe_id"), str)
            and TIER_INSTALLER_RECIPE.fullmatch(str(entry["source_recipe_id"]))
            or isinstance(entry.get("automatic_managed_id"), str)
            and TIER_INSTALLER_AUTOMATIC_OWNER.fullmatch(str(entry["automatic_managed_id"]))
        )
    ]
    entry_outputs = [str(entry.get("output")) for entry in installer_entries]
    if len(installer_entries) != len(expected_outputs) or set(entry_outputs) != expected_outputs:
        errors.append(
            "stock utility restoration entries must describe exactly the four reviewed tier installers"
        )
    if len(entry_outputs) != len(set(entry_outputs)):
        errors.append("stock utility restoration contains duplicate tier-installer entries")

    entries_by_output = {
        str(entry.get("output")): entry
        for entry in installer_entries
        if str(entry.get("output")) in expected_outputs
    }
    for output, contract in TIER_INSTALLER_RESTORATION.items():
        entry = entries_by_output.get(output)
        if entry is None:
            continue
        recipe_id = str(contract["recipe_id"])
        if entry.get("source_recipe_id") != recipe_id:
            errors.append(f"{output} source recipe changed from {recipe_id}")
        if entry.get("exact_source_recipe_ids") != [recipe_id]:
            errors.append(f"{output} must preserve only its one reviewed exact source recipe")
        if entry.get("node") != contract["node"]:
            errors.append(f"{output} documentation node changed from {contract['node']}")
        if entry.get("automatic_managed_id") != contract["automatic_managed_id"]:
            errors.append(f"{output} retired automatic owner changed")
        if entry.get("rationale") != TIER_INSTALLER_POLICY:
            errors.append(f"{output} restoration rationale changed from the reviewed utility policy")

    seed_excluded = set(seed.get("exclude_outputs", []))
    seed_preserved = set(seed.get("preserve_recipe_ids", []))
    manifest_preserved = set(manifest.get("preserve_recipe_ids", []))
    missing_exclusions = sorted(expected_outputs - seed_excluded)
    if missing_exclusions:
        errors.append(
            "restored tier installers are missing seed exclusions: " + ", ".join(missing_exclusions)
        )
    missing_seed_preserves = sorted(expected_recipes - seed_preserved)
    if missing_seed_preserves:
        errors.append(
            "restored tier-installer recipes are missing seed preserves: "
            + ", ".join(missing_seed_preserves)
        )
    missing_manifest_preserves = sorted(expected_recipes - manifest_preserved)
    if missing_manifest_preserves:
        errors.append(
            "restored tier-installer recipes are missing assembled preserves: "
            + ", ".join(missing_manifest_preserves)
        )

    managed_installer_outputs = sorted(expected_outputs & managed_outputs)
    if managed_installer_outputs:
        errors.append(
            "stock-restored tier installers still have managed cards: "
            + ", ".join(managed_installer_outputs)
        )
    surviving_automatic_owners = sorted(expected_owners & managed_ids)
    if surviving_automatic_owners:
        errors.append(
            "retired automatic tier-installer owners survived: "
            + ", ".join(surviving_automatic_owners)
        )
    removed_installer_recipes = sorted(
        expected_recipes & (removal_ids | additional_removals)
    )
    if removed_installer_recipes:
        errors.append(
            "stock-restored tier-installer recipes are still removed: "
            + ", ".join(removed_installer_recipes)
        )

    assigned_nodes = assignment_nodes_by_output(assignments)
    for output, contract in TIER_INSTALLER_RESTORATION.items():
        expected_node = {str(contract["node"])}
        if assigned_nodes.get(output, set()) != expected_node:
            errors.append(
                f"{output} must remain documented only by {contract['node']}; "
                f"found {sorted(assigned_nodes.get(output, set()))}"
            )
    return errors


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def compiled_outputs(recipes: list[dict[str, Any]], errors: list[str]) -> dict[str, list[str]]:
    owners: dict[str, list[str]] = defaultdict(list)
    for index, recipe in enumerate(recipes):
        recipe_id = recipe.get("recipeId")
        if not isinstance(recipe_id, str) or not RESOURCE.fullmatch(recipe_id):
            errors.append(f"compiled recipe {index} has invalid recipeId {recipe_id!r}")
            continue
        slots = recipe.get("slots")
        if not isinstance(slots, dict):
            errors.append(f"compiled recipe {recipe_id} has no slots object")
            continue
        found = False
        for slot_name, stack in slots.items():
            slot_label = str(slot_name)
            if not (
                slot_label.startswith("output") or slot_label.startswith("results")
            ) or not isinstance(stack, dict):
                continue
            if stack.get("kind") != "ITEM":
                continue
            output = stack.get("id")
            if isinstance(output, str) and RESOURCE.fullmatch(output):
                owners[output].append(recipe_id)
                found = True
        if not found:
            errors.append(f"compiled recipe {recipe_id} has no item output slot")
    return owners


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    args = parser.parse_args()

    root = args.project_root.resolve()
    server_root = root / "pack-scripts" / "server_scripts"
    client_root = root / "pack-scripts" / "client_scripts"
    seed = load_json((args.seed or root / "progression" / "managed_recipe_overhaul.seed.json").resolve())
    manifest = load_json((args.manifest or root / "progression" / "managed_recipe_overhaul.json").resolve())
    compiled = load_json((args.compiled or root / "pack-kjsgen" / "default.managed.json").resolve())
    factory_plan = load_json(root / "MEKANISM_FACTORY_RESTORATION_AUDIT.plan.json")
    stock_restoration = load_json(root / "STOCK_UTILITY_RESTORATION_AUDIT.patch.json")
    assignments = load_json(root / "progression" / "machine_node_assignments.json")
    factory_implemented = factory_plan.get("status") == "implemented_in_seed"
    errors: list[str] = []

    recipes = compiled.get("recipes")
    removals = compiled.get("removals")
    if not isinstance(recipes, list) or not isinstance(removals, list):
        errors.append("compiled project must contain recipe and removal arrays")
        recipes = []
        removals = []

    recipe_ids = [recipe.get("recipeId") for recipe in recipes if isinstance(recipe, dict)]
    duplicate_recipe_ids = sorted(
        recipe_id
        for recipe_id, count in Counter(recipe_ids).items()
        if isinstance(recipe_id, str) and count > 1
    )
    if duplicate_recipe_ids:
        errors.append("duplicate managed recipe IDs: " + ", ".join(duplicate_recipe_ids))

    recipe_uids = [recipe.get("uid") for recipe in recipes if isinstance(recipe, dict)]
    duplicate_recipe_uids = sorted(
        uid for uid, count in Counter(recipe_uids).items() if isinstance(uid, str) and count > 1
    )
    if duplicate_recipe_uids:
        errors.append("duplicate managed recipe UIDs: " + ", ".join(duplicate_recipe_uids))

    output_owners = compiled_outputs(recipes, errors)
    duplicate_outputs = {
        output: owners for output, owners in sorted(output_owners.items()) if len(owners) > 1
    }
    for output, owners in duplicate_outputs.items():
        errors.append(f"managed output {output} has multiple cards: {', '.join(owners)}")

    managed_outputs = set(output_owners)
    managed_ids = {value for value in recipe_ids if isinstance(value, str)}
    removal_ids = {
        removal.get("recipeId")
        for removal in removals
        if isinstance(removal, dict) and isinstance(removal.get("recipeId"), str)
    }
    duplicate_removals = sorted(
        recipe_id
        for recipe_id, count in Counter(
            removal.get("recipeId")
            for removal in removals
            if isinstance(removal, dict) and removal.get("recipeId")
        ).items()
        if count > 1
    )
    if duplicate_removals:
        errors.append("duplicate exact managed removals: " + ", ".join(duplicate_removals))

    if managed_ids & removal_ids:
        errors.append(
            "managed cards remove managed recipe IDs: " + ", ".join(sorted(managed_ids & removal_ids))
        )

    excluded = set(seed.get("exclude_outputs", []))
    missing_exclusions = sorted(MANDATORY_EXCLUSIONS - excluded)
    if missing_exclusions:
        errors.append(
            "script-owned canonical outputs missing from exclude_outputs: "
            + ", ".join(missing_exclusions)
        )

    for script, owned_outputs in SCRIPT_OWNED_OUTPUTS.items():
        if not (server_root / script).is_file():
            errors.append(f"missing script owner {script}")
        overlap = sorted(owned_outputs & managed_outputs)
        if overlap:
            errors.append(f"{script} output(s) also managed by KJSGen: {', '.join(overlap)}")

    literal_script_ids: dict[str, list[str]] = defaultdict(list)
    server_literals: dict[str, set[str]] = {}
    for path in sorted(server_root.glob("*.js")):
        text = path.read_text(encoding="utf-8-sig")
        server_literals[path.name] = set(LITERAL_RESOURCE.findall(text))
        for recipe_id in LITERAL_CUSTOM_ID.findall(text):
            literal_script_ids[recipe_id].append(path.name)

        if "migration marker" in text.lower() and RECIPE_MUTATION.search(text):
            errors.append(f"legacy no-op marker {path.name} contains a recipe mutation")

        for match in REMOVE_OBJECT.finditer(text):
            body = match.group("body")
            if re.search(r"\bid\s*:", body):
                continue
            normalized = re.sub(r"\s+", " ", body).strip()
            allowed_atm_type_filter = (
                path.name == "industrial_allthemodium_currency.js"
                and re.fullmatch(r"mod\s*:\s*['\"]allthemodium['\"]\s*,\s*type\s*:\s*type", normalized)
            )
            if not allowed_atm_type_filter:
                errors.append(f"broad recipe removal in {path.name}: event.remove({{{normalized}}})")

    for recipe_id, scripts in sorted(literal_script_ids.items()):
        if len(scripts) > 1:
            errors.append(f"script recipe ID {recipe_id} is declared by: {', '.join(scripts)}")
        if recipe_id in managed_ids:
            errors.append(f"script recipe ID {recipe_id} duplicates a managed card")

    # A source script must not delete an industrial_colonies managed ID.  The
    # literal scan intentionally errs on the conservative side and only checks
    # exact managed IDs, not ingredients mentioned by a script.
    for script, literals in server_literals.items():
        overlap = sorted(managed_ids & literals)
        if overlap:
            errors.append(f"{script} references managed recipe ID(s): {', '.join(overlap)}")

    hidden_literals: set[str] = set()
    for path in sorted(client_root.glob("*.js")):
        text = path.read_text(encoding="utf-8-sig")
        if "event.remove" in text:
            hidden_literals.update(LITERAL_RESOURCE.findall(text))
    hidden_managed = sorted(managed_outputs & hidden_literals)
    if hidden_managed:
        errors.append("client viewer cleanup hides managed outputs: " + ", ".join(hidden_managed))

    additional_removals = set(manifest.get("additional_removals", []))
    missing_factory_removals = sorted(DIRECT_FACTORY_RECIPES - removal_ids)
    if missing_factory_removals:
        errors.append("stock Mekanism Factory recipes lack exact removals: " + ", ".join(missing_factory_removals))
    if factory_implemented:
        missing_factory_cards = sorted(RESTORED_FACTORY_ITEMS - managed_outputs)
        if missing_factory_cards:
            errors.append("restored Factory outputs lack managed cards: " + ", ".join(missing_factory_cards))
        unexpected_factory_cards = sorted((DIRECT_FACTORY_ITEMS - RESTORED_FACTORY_ITEMS) & managed_outputs)
        if unexpected_factory_cards:
            errors.append("retired Smelting Factories have managed cards: " + ", ".join(unexpected_factory_cards))
        restored_bare_removals = sorted(RESTORED_FACTORY_RECIPES & additional_removals)
        if restored_bare_removals:
            errors.append("restored Factory sources remain bare removals: " + ", ".join(restored_bare_removals))
        missing_smelting_retirements = sorted(RETIRED_SMELTING_RECIPES - additional_removals)
        if missing_smelting_retirements:
            errors.append("Smelting Factory retirements are missing: " + ", ".join(missing_smelting_retirements))
    else:
        missing_factories = sorted(DIRECT_FACTORY_RECIPES - additional_removals)
        if missing_factories:
            errors.append("pre-integration Factory recipes are not bare removals: " + ", ".join(missing_factories))
        unexpected_factory_cards = sorted(DIRECT_FACTORY_ITEMS & managed_outputs)
        if unexpected_factory_cards:
            errors.append("pre-integration Factory outputs already have managed cards: " + ", ".join(unexpected_factory_cards))
    errors.extend(
        validate_tier_installer_restoration(
            stock_restoration,
            seed,
            manifest,
            assignments,
            managed_outputs,
            managed_ids,
            removal_ids,
            additional_removals,
        )
    )

    user_owned = set(seed.get("user_owned_outputs", []))
    user_overlap = sorted(user_owned & managed_outputs)
    if user_overlap:
        errors.append("user-owned KJSGen outputs were overwritten: " + ", ".join(user_overlap))
    missing_user_stock_removals = sorted(user_owned - additional_removals)
    if missing_user_stock_removals:
        errors.append(
            "user-owned cards lack exact stock removals: " + ", ".join(missing_user_stock_removals)
        )

    if errors:
        print("FAIL: managed/script ownership conflicts detected", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print(
        "PASS: managed/script ownership is disjoint; "
        f"{len(recipes)} managed cards, {len(removal_ids)} exact removals, "
        f"{len(SCRIPT_OWNED_OUTPUTS)} active script owners, "
        f"{len(DIRECT_FACTORY_RECIPES)} exact Factory source removals "
        f"({'32 restored cards + 4 Smelting retirements' if factory_implemented else 'pre-integration boundary'})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
