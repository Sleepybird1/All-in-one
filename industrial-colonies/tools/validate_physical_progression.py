#!/usr/bin/env python3
"""Validate the current physical, recipe-authored progression contract.

MineColonies research and FTB Quests are deliberately not recipe gates. The
managed recipe manifest is the progression authority, its compiled KJSGen
project is the executable/editor representation, and focused KubeJS scripts
own canonical materials and the three endgame artifacts.

This is not a compatibility shim for the retired ``physical_recipe_tiers``
design. It delegates the complete schema/compiler/removal/DAG proof to
``validate_managed_recipe_overhaul`` and then checks pack-specific capability
milestones which make that valid graph a real industrial progression.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from validate_ae2_transform_hardening import validate_contract as validate_ae2_transform_contract
from validate_late_machine_hardening import validate_contract as validate_late_machine_contract


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
DEFAULT_COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"
DEFAULT_QUEST_ROOT = PROJECT / "pack-config-overrides" / "ftbquests" / "quests"
DEFAULT_REPORT = PROJECT / "build" / "reports" / "physical-progression-validation.json"
CANONICAL_STEEL_FRAME = "tfmg:steel_frame"
RETIRED_STEEL_CASING = "mekanism:steel_casing"
RETIRED_STEEL_CASING_OWNER = "industrial_colonies:mekanism/steel_casing"

PHASE_ORDER = [
    "Mechanical Foundations",
    "Steam & Brass",
    "Steel & Petroleum",
    "Electrical Manufacturing",
    "Digital Logistics",
    "Mekanized Industry",
    "High-Energy Grid",
    "Nuclear Engineering",
    "Post-Nuclear Megaprojects",
    "Orbital Engineering",
    "Planetary Industry",
    "Outer System Industry",
    "Interstellar Escape",
]

# These are capability milestones, not a frozen list of every recipe. Moving
# one backwards or deleting one is a regression even if the generic graph is
# still acyclic.
MILESTONES: dict[str, tuple[str, str]] = {
    "industrial_colonies:mechanical/mechanical_press": (
        "Mechanical Foundations",
        "shaped",
    ),
    "industrial_colonies:mechanical/mechanical_pump": (
        "Mechanical Foundations",
        "shaped",
    ),
    "industrial_colonies:steam/steam_engine": ("Steam & Brass", "shaped"),
    "industrial_colonies:brass/deployer": ("Steam & Brass", "shaped"),
    "industrial_colonies:brass/mechanical_crafter": ("Steam & Brass", "shaped"),
    "industrial_colonies:heavy_industry/industrial_mixer": (
        "Steel & Petroleum",
        "mechanical_crafting",
    ),
    "industrial_colonies:heavy_industry/scorched_alloyer": (
        "Steel & Petroleum",
        "mechanical_crafting",
    ),
    "industrial_colonies:electronics/circuit_board": (
        "Electrical Manufacturing",
        "sequenced_assembly",
    ),
    "industrial_colonies:electronics/printed_silicon": (
        "Digital Logistics",
        "compacting",
    ),
    "industrial_colonies:digital/storage_drive": (
        "Digital Logistics",
        "mechanical_crafting",
    ),
    "industrial_colonies:mekanism/basic_control_circuit": (
        "Mekanized Industry",
        "mekanism_metallurgic_infusing",
    ),
    "industrial_colonies:mekanism/ultimate_control_circuit": (
        "High-Energy Grid",
        "compacting",
    ),
    "industrial_colonies:nuclear/basic_reactor_controller": (
        "Nuclear Engineering",
        "mechanical_crafting",
    ),
    "industrial_colonies:nuclear/reinforced_reactor_controller": (
        "Nuclear Engineering",
        "mechanical_crafting",
    ),
    "industrial_colonies:space/orbital_flight_computer": (
        "Orbital Engineering",
        "mechanical_crafting",
    ),
    "industrial_colonies:space/propulsion/hose_anchor": (
        "Orbital Engineering",
        "mechanical_crafting",
    ),
    "industrial_colonies:space/propulsion/engine_pipes": (
        "Orbital Engineering",
        "mechanical_crafting",
    ),
    "industrial_colonies:space/propulsion/engine_nozzle": (
        "Orbital Engineering",
        "mechanical_crafting",
    ),
    "industrial_colonies:space/propulsion/thruster_mount": (
        "Orbital Engineering",
        "mechanical_crafting",
    ),
}

ENDGAME_KEYS = ["black_hole", "industrial_reserves", "industrial_star"]
ENDGAME_ITEMS = {
    "black_hole": "industrial_colonies:black_hole",
    "industrial_reserves": "industrial_colonies:industrial_reserve_core",
    "industrial_star": "industrial_colonies:industrial_star",
}
ENDGAME_DEPENDENCIES = {
    "black_hole": [],
    "industrial_reserves": ["black_hole"],
    "industrial_star": ["industrial_reserves"],
}
EXPECTED_QUEST_FILES = {
    "chapter_groups.snbt",
    "chapters/dungeon_exploration.snbt",
    "chapters/electrical_manufacturing.snbt",
    "chapters/digital_logistics.snbt",
    "chapters/factory_foundations.snbt",
    "chapters/high_energy_grid.snbt",
    "chapters/industrial_progression.snbt",
    "chapters/mekanized_industry.snbt",
    "chapters/nuclear_engineering.snbt",
    "chapters/orbital_engineering.snbt",
    "chapters/planetary_industry.snbt",
    "data.snbt",
    "lang/en_us.snbt",
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be an object: {path}")
    return value


def item_ids(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    result: list[str] = []
    for value in values:
        if isinstance(value, str):
            result.append(value.split("x ", 1)[-1].lstrip("#").strip())
        elif isinstance(value, dict) and value.get("kind", "ITEM") in {"ITEM", "ITEM_TAG"}:
            result.append(str(value.get("id", "")).lstrip("#"))
    return result


def recipe_ingredients(recipe: Mapping[str, Any]) -> set[str]:
    values: list[Any] = []
    key = recipe.get("key")
    if isinstance(key, dict):
        values.extend(key.values())
    if isinstance(recipe.get("inputs"), list):
        values.extend(recipe["inputs"])
    for field in ("input", "held", "gas", "infusion", "left", "right"):
        if field in recipe:
            values.append(recipe[field])
    for step in recipe.get("steps", []) if isinstance(recipe.get("steps"), list) else []:
        if isinstance(step, dict):
            for field in ("ingredient", "fluid"):
                if field in step:
                    values.append(step[field])
    return set(item_ids(values))


def recipe_outputs(recipe: Mapping[str, Any]) -> set[str]:
    values: list[Any] = []
    if "output" in recipe:
        values.append(recipe["output"])
    for field in ("outputs", "results"):
        if isinstance(recipe.get(field), list):
            values.extend(recipe[field])
    return set(item_ids(values))


def run_core_validation(
    manifest: Mapping[str, Any], compiled: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[str], list[str], int]:
    """Run the production validator in-process and return expanded recipes."""

    from validate_managed_recipe_overhaul import (  # type: ignore
        Diagnostics,
        validate_compiled_output,
        validate_dependency_graph,
        validate_manifest,
    )

    diagnostics = Diagnostics()
    specs, inputs, outputs, removals, phases = validate_manifest(manifest, diagnostics)
    if specs:
        validate_dependency_graph(specs, inputs, outputs, phases, diagnostics)
    validate_compiled_output(compiled, manifest, specs, removals, diagnostics)
    return specs, diagnostics.errors, diagnostics.warnings, len(set(removals))


def validate_managed_physical_contract(
    project: Path,
    manifest: Mapping[str, Any],
    specs: Sequence[Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    phases = manifest.get("phase_order")
    if phases != PHASE_ORDER:
        errors.append(f"phase spine changed; expected {PHASE_ORDER}, found {phases}")

    recipes = {str(recipe.get("id", "")): recipe for recipe in specs}
    counts = Counter(str(recipe.get("phase", "")) for recipe in specs)
    # The final five phases are bounded late-game slices rather than broad
    # machine tiers, so they intentionally do not carry the four-recipe floor.
    for phase in PHASE_ORDER[:-5]:
        if counts[phase] < 4:
            errors.append(f"phase {phase!r} has only {counts[phase]} managed recipes")

    for recipe_id, (phase, recipe_type) in MILESTONES.items():
        recipe = recipes.get(recipe_id)
        if recipe is None:
            errors.append(f"required progression milestone is missing: {recipe_id}")
            continue
        if recipe.get("phase") != phase:
            errors.append(
                f"{recipe_id} belongs to {recipe.get('phase')!r}; expected {phase!r}"
            )
        if recipe.get("type") != recipe_type:
            errors.append(
                f"{recipe_id} uses {recipe.get('type')!r}; expected {recipe_type!r}"
            )

    board = recipes.get("industrial_colonies:electronics/circuit_board", {})
    board_steps = board.get("steps", []) if isinstance(board, dict) else []
    board_materials = {
        str(step.get("ingredient", ""))
        for step in board_steps
        if isinstance(step, dict)
    }
    if board.get("input") != "tfmg:etched_circuit_board" or not {
        "tfmg:capacitor_item",
        "tfmg:resistor",
        "tfmg:transistor_item",
    }.issubset(board_materials):
        errors.append("TFMG circuit board no longer uses the etched-board component sequence")
    if board.get("loops") not in {2, 3, 4}:
        errors.append("TFMG circuit-board assembly must retain a moderate 2-4 loop sequence")

    silicon = recipes.get("industrial_colonies:electronics/printed_silicon", {})
    if (
        silicon.get("machine") != "createcasing:brass_press"
        or silicon.get("returned_tool") != "ae2:silicon_press"
        or not {"tfmg:silicon_ingot", "ae2:silicon_press"}.issubset(
            recipe_ingredients(silicon)
        )
    ):
        errors.append(
            "printed silicon must compact canonical TFMG silicon in the Brass Press "
            "and return the AE2 mold"
        )

    basic = recipes.get("industrial_colonies:mekanism/basic_control_circuit", {})
    if "tfmg:circuit_board" not in recipe_ingredients(basic):
        errors.append("Mekanism basic control circuits no longer begin from a TFMG board")

    retired_producers = sorted(
        str(recipe.get("id", ""))
        for recipe in specs
        if RETIRED_STEEL_CASING in recipe_outputs(recipe)
    )
    if retired_producers:
        errors.append(
            "retired Mekanism Steel Casing still has managed producer(s): "
            f"{retired_producers}"
        )
    if RETIRED_STEEL_CASING not in set(manifest.get("additional_removals", [])):
        errors.append("retired Mekanism Steel Casing stock recipe is not exactly removed")
    stale_consumers = sorted(
        str(recipe.get("id", ""))
        for recipe in specs
        if RETIRED_STEEL_CASING in recipe_ingredients(recipe)
    )
    if stale_consumers:
        errors.append(
            "managed recipes still consume retired Mekanism Steel Casing: "
            f"{stale_consumers}"
        )
    stale_dependencies = sorted(
        str(recipe.get("id", ""))
        for recipe in specs
        if RETIRED_STEEL_CASING_OWNER in set(recipe.get("depends_on", []))
    )
    if stale_dependencies:
        errors.append(
            "managed recipes still depend on the retired Steel Casing owner: "
            f"{stale_dependencies}"
        )
    if not any(CANONICAL_STEEL_FRAME in recipe_ingredients(recipe) for recipe in specs):
        errors.append("TFMG Steel Frame is no longer consumed by the managed factory DAG")

    alloyer = recipes.get("industrial_colonies:heavy_industry/scorched_alloyer", {})
    if alloyer.get("remove") != ["modernfoundry:smeltery/scorched/alloyer"]:
        errors.append("Scorched Alloyer must retire only its exact stock recipe ID")
    if "industrial_colonies:heavy_industry/industrial_mixer" not in set(
        alloyer.get("depends_on", [])
    ) or not {
        "tfmg:industrial_mixer",
        "tfmg:heavy_machinery_casing",
        "tfmg:cast_iron_frame",
        "modernfoundry:scorched_brick",
    }.issubset(recipe_ingredients(alloyer)):
        errors.append(
            "Scorched Alloyer must remain a reachable TFMG-first heavy-industry assembly"
        )

    for name in ("elite", "ultimate"):
        recipe = recipes.get(f"industrial_colonies:mekanism/{name}_control_circuit", {})
        if recipe.get("machine") != "createcasing:weathered_iron_press":
            errors.append(f"Mekanism {name} control circuit escaped the Weathered Iron Press")

    for recipe_id in (
        "industrial_colonies:nuclear/basic_reactor_controller",
        "industrial_colonies:nuclear/reinforced_reactor_controller",
    ):
        ingredients = recipe_ingredients(recipes.get(recipe_id, {}))
        if not {
            "computercraft:computer_advanced",
            "computercraft:monitor_advanced",
            "ae2:engineering_processor",
        }.issubset(ingredients):
            errors.append(f"{recipe_id} lost its ComputerCraft/AE2 instrumentation")

    # Migration classes may remain in source, but the stage system must not be
    # registered and its MineColonies UI mixins must not be active.
    entrypoint = (
        project / "src/main/java/dev/godpc/industrialcolonies/IndustrialColonies.java"
    ).read_text(encoding="utf-8-sig")
    for token in ("RecipeStageGate.register(", "ResearchStageSynchronizer.register("):
        if token in entrypoint:
            errors.append(f"runtime entrypoint reactivated retired gate: {token}")
    mixins = load_object(project / "src/main/resources/industrial_colonies.mixins.json")
    active_mixins = [
        str(value)
        for key in ("mixins", "client", "server")
        for value in mixins.get(key, [])
    ]
    for suffix in ("LocalResearchTreeMixin", "WindowResearchTreeMixin"):
        if any(value.endswith(suffix) for value in active_mixins):
            errors.append(f"retired MineColonies progression mixin is active: {suffix}")

    return errors


def validate_endgame_guidance(project: Path, quest_root: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    source = load_object(project / "progression/industrial_megaprojects.json")
    quests = source.get("quests", [])
    keys = [str(quest.get("key", "")) for quest in quests if isinstance(quest, dict)]
    if keys != ENDGAME_KEYS:
        errors.append(f"endgame quest order changed; expected {ENDGAME_KEYS}, found {keys}")
    by_key = {str(quest.get("key", "")): quest for quest in quests if isinstance(quest, dict)}
    for key in ENDGAME_KEYS:
        quest = by_key.get(key, {})
        if quest.get("dependencies") != ENDGAME_DEPENDENCIES[key]:
            errors.append(f"endgame quest {key} has wrong guidance dependencies")
        expected_task = [{"type": "item", "item": ENDGAME_ITEMS[key], "count": 1}]
        if quest.get("tasks") != expected_task:
            errors.append(f"endgame quest {key} is not one item-observation task")
        if {"research_dependencies", "stage", "team_stage", "rewards"}.intersection(quest):
            errors.append(f"endgame quest {key} contains a gate or reward")

    found_files = {
        str(path.relative_to(quest_root)).replace("\\", "/")
        for path in quest_root.rglob("*.snbt")
    }
    if found_files != EXPECTED_QUEST_FILES:
        errors.append(
            "generated FTB Quest file set changed; "
            f"expected={sorted(EXPECTED_QUEST_FILES)}, found={sorted(found_files)}"
        )
    chapter_path = quest_root / "chapters/industrial_progression.snbt"
    if chapter_path.is_file():
        chapter = load_object(chapter_path)
        generated = chapter.get("quests", [])
        if len(generated) != 3:
            errors.append(f"generated endgame chapter has {len(generated)} quests instead of 3")
        for quest in generated if isinstance(generated, list) else []:
            tasks = quest.get("tasks", []) if isinstance(quest, dict) else []
            if len(tasks) != 1 or tasks[0].get("type") != "item":
                errors.append(f"generated quest {quest.get('id')} is not item-only")
            if "rewards" in quest:
                errors.append(f"generated quest {quest.get('id')} contains rewards")
    else:
        errors.append(f"generated endgame chapter is missing: {chapter_path}")

    script_contracts = {
        "industrial_black_hole_megaproject.js": (
            "industrial_colonies:megaproject/black_hole",
            "allthecompressed:cobblestone_9x",
            "allthecompressed:oak_planks_9x",
        ),
        "industrial_reserve_core_megaproject.js": (
            "industrial_colonies:megaproject/industrial_reserve_core",
            "loops: 512",
            "tfmg:sulfuric_acid",
            "tfmg:diesel",
        ),
        "industrial_star_megaproject.js": (
            "industrial_colonies:megaproject/industrial_star",
            "industrial_colonies:creative_mechanical_crafting",
            "industrial_colonies:black_hole",
            "industrial_colonies:industrial_reserve_core",
        ),
        "industrial_petroleum_canonicalization.js": (
            "'c:diesel': ['tfmg:diesel', 'tfmg:flowing_diesel']",
            "'c:gasoline': ['tfmg:gasoline', 'tfmg:flowing_gasoline']",
        ),
        "industrial_sulfur_canonicalization.js": (
            "event.add('c:sulfuric_acid', 'tfmg:sulfuric_acid')",
            "mekanism:chemical_infusing/sulfuric_acid",
            "TFMG vat remains required",
        ),
        "industrial_uranium_yellorium_separation.js": (
            "industrial_colonies:yellorium_compound",
            "mekanism:raw_uranium",
            "industrial_colonies:materials/uranium/raw_from_yellorium_compound",
        ),
        "industrial_allthemodium_currency.js": (
            "industrial_colonies:currency/allthemodium/synthesis",
            "industrial_colonies:currency/vibranium/synthesis",
            "industrial_colonies:currency/unobtainium/synthesis",
        ),
        "industrial_space_entry_deferred.js": (
            "ad_astra:nasa_workbench",
            "ad_astra:launch_pad",
            "ad_astra:nasa_workbench/tier_1_rocket_from_nasa_workbench",
            "stock Ad Astra space-entry recipes until the spaceflight expansion",
        ),
    }
    scripts = project / "pack-scripts/server_scripts"
    for filename, tokens in script_contracts.items():
        path = scripts / filename
        if not path.is_file():
            errors.append(f"progression owner script is missing: {filename}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        for token in tokens:
            if token not in text:
                errors.append(f"{filename} is missing progression contract token {token!r}")

    return errors, len(quests) if isinstance(quests, list) else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_COMPILED)
    parser.add_argument("--quest-root", type=Path, default=DEFAULT_QUEST_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    specs: list[dict[str, Any]] = []
    removal_count = 0
    quest_count = 0
    try:
        manifest = load_object(args.manifest.resolve())
        compiled = load_object(args.output.resolve())
        specs, core_errors, core_warnings, removal_count = run_core_validation(
            manifest, compiled
        )
        errors.extend(f"managed core: {error}" for error in core_errors)
        warnings.extend(f"managed core: {warning}" for warning in core_warnings)
        errors.extend(validate_ae2_transform_contract(manifest, compiled))
        errors.extend(validate_late_machine_contract(manifest, compiled))
        errors.extend(validate_managed_physical_contract(project, manifest, specs))
        endgame_errors, quest_count = validate_endgame_guidance(
            project, args.quest_root.resolve()
        )
        errors.extend(endgame_errors)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, ImportError) as exc:
        errors.append(str(exc))

    phase_counts = Counter(str(recipe.get("phase", "")) for recipe in specs)
    report = {
        "schema_version": 2,
        "authority": "managed_recipe_inputs_and_machine_processes",
        "status": "pass" if not errors else "fail",
        "manifest": str(args.manifest.resolve()),
        "compiled_project": str(args.output.resolve()),
        "statistics": {
            "expanded_managed_recipes": len(specs),
            "exact_recipe_removals": removal_count,
            "endgame_guidance_quests": quest_count,
            "recipe_stage_entries": 0,
        },
        "recipes_by_phase": dict(phase_counts),
        "warnings": warnings,
        "errors": errors,
    }
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if errors:
        print(f"FAIL: {len(errors)} physical-progression issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        print(f"Report: {report_path}")
        return 1
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    print(
        "PASS: physical progression is owned by the managed recipe DAG "
        f"({len(specs)} recipes, {removal_count} exact removals, "
        f"{quest_count} non-gating endgame objectives)."
    )
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
