#!/usr/bin/env python3
"""Prove the installed actinide route can physically reach the Industrial Star.

The pack intentionally does not install Mekanism Generators.  This validator
therefore treats the reviewed Blutonium dissolution recipe as the sole source
of Mekanism Nuclear Waste, verifies the two retained stock Mekanism
transformations which follow it, and then follows Plutonium Pellets into the
512-loop Reserve Core and the final Black Hole/Reserve Core/Star convergence.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = PROJECT_ROOT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")

BRIDGE_SCRIPT = "industrial_nuclear_actinides_01.js"
BRIDGE_RECIPE = "industrial_colonies:chemistry/actinide/nuclear_waste_from_blutonium"
PLUTONIUM_RECIPE = "mekanism:processing/lategame/plutonium"
PELLET_RECIPE = "mekanism:processing/lategame/plutonium_pellet/from_reaction"
STOCK_ROUTE_IDS = {PLUTONIUM_RECIPE, PELLET_RECIPE}
NUCLEAR_WASTE = "mekanism:nuclear_waste"
PLUTONIUM = "mekanism:plutonium"
PLUTONIUM_PELLET = "mekanism:pellet_plutonium"

BLACK_HOLE = "industrial_colonies:black_hole"
RESERVE_CORE = "industrial_colonies:industrial_reserve_core"
INDUSTRIAL_STAR = "industrial_colonies:industrial_star"
BLACK_HOLE_RECIPE = "industrial_colonies:megaproject/black_hole"
RESERVE_RECIPE = "industrial_colonies:megaproject/industrial_reserve_core"
STAR_RECIPE = "industrial_colonies:megaproject/industrial_star"
RESERVE_LOOPS = 512

RECIPE_ID_LITERAL = re.compile(
    r"\.id\(\s*['\"]([a-z0-9_.-]+:[a-z0-9_./-]+)['\"]\s*\)"
)
RESOURCE_LITERAL = re.compile(r"['\"]([a-z0-9_.-]+:[a-z0-9_./-]+)['\"]")
FORBIDDEN_BRIDGE_MUTATION = re.compile(
    r"\bevent\.(?:remove|removeAll|replaceInput|replaceOutput|shaped|shapeless|"
    r"smelting|blasting|recipes)\s*\("
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def split_pipe(value: str) -> set[str]:
    return {part.strip() for part in value.split("|") if part.strip()}


def strip_js_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\r\n]*", "", text)


def extract_mod_ids(mods: Path) -> set[str]:
    result: set[str] = set()
    for jar in sorted(mods.glob("*.jar"), key=lambda path: path.name.lower()):
        try:
            with zipfile.ZipFile(jar) as archive:
                for metadata in ("META-INF/neoforge.mods.toml", "META-INF/mods.toml"):
                    try:
                        text = archive.read(metadata).decode("utf-8", errors="ignore")
                    except KeyError:
                        continue
                    result.update(
                        value.lower()
                        for value in re.findall(
                            r"(?im)^\s*modId\s*=\s*['\"]([^'\"]+)", text
                        )
                    )
                try:
                    fabric = json.loads(archive.read("fabric.mod.json"))
                except (KeyError, json.JSONDecodeError, UnicodeDecodeError):
                    fabric = None
                if isinstance(fabric, dict) and isinstance(fabric.get("id"), str):
                    result.add(fabric["id"].lower())
        except (OSError, zipfile.BadZipFile):
            # Other validators inventory malformed archives.  This focused
            # proof only needs positive Mekanism identity evidence.
            continue
    return result


def validate_mod_contract(mod_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if "mekanism" not in mod_ids:
        errors.append("base Mekanism is absent, so the stock actinide route cannot run")
    if "mekanismgenerators" in mod_ids:
        errors.append(
            "Mekanism Generators is installed; the reviewed no-Generators waste-source contract changed"
        )
    return errors


def validate_bridge_text(text: str) -> list[str]:
    errors: list[str] = []
    source = strip_js_comments(text)
    declared_ids = RECIPE_ID_LITERAL.findall(source)
    if declared_ids != [BRIDGE_RECIPE]:
        errors.append(
            "actinide script must declare exactly the canonical nuclear-waste bridge recipe ID"
        )
    if source.count("event.custom(") != 1:
        errors.append("actinide script must define exactly one custom recipe")
    if FORBIDDEN_BRIDGE_MUTATION.search(source):
        errors.append("actinide bridge contains a broad or unrelated recipe mutation")

    required = {
        "mekanism:dissolution type": r"\btype\s*:\s*['\"]mekanism:dissolution['\"]",
        "one unit of Mekanism sulfuric acid": (
            r"\bchemical_input\s*:\s*\{\s*amount\s*:\s*1\s*,\s*"
            r"chemical\s*:\s*['\"]mekanism:sulfuric_acid['\"]\s*\}"
        ),
        "one Blutonium ingot": (
            r"\bitem_input\s*:\s*\{\s*count\s*:\s*1\s*,\s*"
            r"item\s*:\s*['\"]bigreactors:blutonium_ingot['\"]\s*\}"
        ),
        "1000 units of Mekanism Nuclear Waste": (
            r"\boutput\s*:\s*\{\s*amount\s*:\s*1000\s*,\s*"
            r"id\s*:\s*['\"]mekanism:nuclear_waste['\"]\s*\}"
        ),
        "per-tick chemical usage": r"\bper_tick_usage\s*:\s*true\b",
    }
    for label, pattern in required.items():
        if len(re.findall(pattern, source, flags=re.S)) != 1:
            errors.append(f"actinide bridge must contain exactly {label}")

    expected_literals = {
        "mekanism:dissolution",
        "mekanism:sulfuric_acid",
        "bigreactors:blutonium_ingot",
        NUCLEAR_WASTE,
        BRIDGE_RECIPE,
    }
    recipe_literals = set(RESOURCE_LITERAL.findall(source))
    unexpected_recipe_ids = {
        value for value in declared_ids if value != BRIDGE_RECIPE
    }
    if unexpected_recipe_ids or not expected_literals.issubset(recipe_literals):
        errors.append("actinide bridge literal recipe contract changed")
    return errors


def load_raw_recipe(row: dict[str, str], mods: Path) -> dict[str, Any]:
    source_jar = mods / row["source_jar"]
    if not source_jar.is_file():
        raise ValueError(f"catalog source JAR is missing: {source_jar}")
    with zipfile.ZipFile(source_jar) as archive:
        return json.loads(archive.read(row["source_path"]).decode("utf-8-sig"))


def expected_stock_raw() -> dict[str, dict[str, Any]]:
    return {
        PLUTONIUM_RECIPE: {
            "type": "mekanism:centrifuging",
            "input": {"amount": 10, "chemical": NUCLEAR_WASTE},
            "output": {"amount": 1, "id": PLUTONIUM},
        },
        PELLET_RECIPE: {
            "type": "mekanism:reaction",
            "chemical_input": {"amount": 1000, "chemical": PLUTONIUM},
            "chemical_output": {
                "amount": 1000,
                "id": "mekanism:spent_nuclear_waste",
            },
            "duration": 100,
            "fluid_input": {"amount": 1000, "tag": "minecraft:water"},
            "item_input": {"count": 1, "tag": "c:dusts/fluorite"},
            "item_output": {"count": 1, "id": PLUTONIUM_PELLET},
        },
    }


def validate_stock_contract(
    recipes_by_id: dict[str, list[dict[str, str]]],
    refs: list[dict[str, str]],
    raw_by_id: dict[str, dict[str, Any]],
    removed_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    expected_raw = expected_stock_raw()
    for recipe_id in (PLUTONIUM_RECIPE, PELLET_RECIPE):
        rows = recipes_by_id.get(recipe_id, [])
        if len(rows) != 1:
            errors.append(
                f"installed catalog must contain exactly one retained {recipe_id} recipe; found {len(rows)}"
            )
        if recipe_id in removed_ids:
            errors.append(f"retained stock actinide recipe is exactly removed: {recipe_id}")
        if raw_by_id.get(recipe_id) != expected_raw[recipe_id]:
            errors.append(f"installed stock recipe payload changed: {recipe_id}")

    expected_refs = {
        PLUTONIUM_RECIPE: {
            ("input", "chemical", NUCLEAR_WASTE, "10.0"),
            ("output", "item", PLUTONIUM, "1.0"),
        },
        PELLET_RECIPE: {
            ("input", "chemical", PLUTONIUM, "1000.0"),
            ("input", "tag", "minecraft:water", "1000.0"),
            ("input", "tag", "c:dusts/fluorite", "1.0"),
            ("output", "item", PLUTONIUM_PELLET, "1.0"),
            ("output", "item", "mekanism:spent_nuclear_waste", "1000.0"),
        },
    }
    for recipe_id, expected in expected_refs.items():
        observed = {
            (row.get("role", ""), row.get("kind", ""), row.get("resource_id", ""), row.get("count", ""))
            for row in refs
            if row.get("recipe_id") == recipe_id
        }
        if observed != expected:
            errors.append(f"installed catalog references changed for {recipe_id}")

    waste_producers = sorted(
        {
            row.get("recipe_id", "")
            for row in refs
            if row.get("role") == "output" and row.get("resource_id") == NUCLEAR_WASTE
        }
        - {BRIDGE_RECIPE}
    )
    if waste_producers:
        errors.append(
            "conflicting installed Nuclear Waste producer bypass(es): "
            + ", ".join(waste_producers)
        )
    return errors


def output_id(recipe: dict[str, Any]) -> str | None:
    output = recipe.get("output")
    if isinstance(output, str):
        match = re.fullmatch(r"(?:\d+x\s+)?([a-z0-9_.-]+:[a-z0-9_./-]+)", output.strip())
        return match.group(1) if match else None
    if isinstance(output, dict):
        value = output.get("id", output.get("item"))
        return value if isinstance(value, str) else None
    return None


def scripted_stock_removals(script_texts: Iterable[str]) -> set[str]:
    """Conservatively find reviewed stock IDs named by a removal script."""

    result: set[str] = set()
    for raw_text in script_texts:
        text = strip_js_comments(raw_text)
        if "event.remove" in text:
            result.update(STOCK_ROUTE_IDS & set(RESOURCE_LITERAL.findall(text)))
    return result


def project_removal_ids(project: Path) -> set[str]:
    result: set[str] = set()
    for filename in (
        "progression/managed_recipe_overhaul.json",
        "progression/managed_recipe_overhaul.seed.json",
    ):
        data = read_json(project / filename)
        result.update(
            value for value in data.get("additional_removals", []) if isinstance(value, str)
        )
        for recipe in data.get("recipes", []):
            if isinstance(recipe, dict):
                result.update(value for value in recipe.get("remove", []) if isinstance(value, str))

    compiled = read_json(project / "pack-kjsgen" / "default.managed.json")
    result.update(
        row.get("recipeId")
        for row in compiled.get("removals", [])
        if isinstance(row, dict) and isinstance(row.get("recipeId"), str)
    )
    result.update(
        scripted_stock_removals(
            path.read_text(encoding="utf-8-sig")
            for path in (project / "pack-scripts" / "server_scripts").glob("*.js")
        )
    )
    return result


def validate_scripted_waste_sources(script_texts: dict[str, str]) -> list[str]:
    """Reject every scripted Nuclear Waste owner except the reviewed bridge."""

    errors: list[str] = []
    for name, raw_text in sorted(script_texts.items()):
        if name == BRIDGE_SCRIPT:
            continue
        text = strip_js_comments(raw_text)
        if NUCLEAR_WASTE in RESOURCE_LITERAL.findall(text):
            errors.append(f"conflicting scripted Nuclear Waste route in {name}")
    return errors


def validate_source_exclusivity(project: Path, refs: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    server_root = project / "pack-scripts" / "server_scripts"
    errors.extend(
        validate_scripted_waste_sources(
            {
                path.name: path.read_text(encoding="utf-8-sig")
                for path in sorted(server_root.glob("*.js"))
            }
        )
    )

    manifest = read_json(project / "progression" / "managed_recipe_overhaul.json")
    managed_waste = [
        recipe.get("id", "<unknown>")
        for recipe in manifest.get("recipes", [])
        if isinstance(recipe, dict) and output_id(recipe) == NUCLEAR_WASTE
    ]
    if managed_waste:
        errors.append(
            "managed KJSGen also produces Nuclear Waste: " + ", ".join(managed_waste)
        )

    # The bridge is script-authored and therefore absent from the static JAR
    # catalog. Any catalog output is a second installed acquisition route.
    catalog_waste = sorted(
        {
            row.get("recipe_id", "")
            for row in refs
            if row.get("role") == "output" and row.get("resource_id") == NUCLEAR_WASTE
        }
    )
    if catalog_waste:
        errors.append(
            "installed catalog contains a conflicting Nuclear Waste source: "
            + ", ".join(catalog_waste)
        )
    return errors


def validate_capstone_texts(
    black_hole_text: str,
    reserve_text: str,
    star_text: str,
    quests: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    black = strip_js_comments(black_hole_text)
    reserve = strip_js_comments(reserve_text)
    star = strip_js_comments(star_text)

    if RECIPE_ID_LITERAL.findall(black) != [BLACK_HOLE_RECIPE]:
        errors.append("Black Hole recipe identity or uniqueness changed")
    if black.count(f"Item.of('{BLACK_HOLE}')") != 1 or black.count("event.shaped(") != 1:
        errors.append("Black Hole no longer has one physical shaped recipe")

    loops = re.findall(r"\bloops\s*:\s*(\d+)", reserve)
    if loops != [str(RESERVE_LOOPS)]:
        errors.append("Reserve Core must retain exactly 512 sequenced-assembly loops")
    if RECIPE_ID_LITERAL.findall(reserve) != [RESERVE_RECIPE]:
        errors.append("Reserve Core recipe identity or uniqueness changed")
    if reserve.count("sequence.push(deploying('mekanism:pellet_plutonium'))") != 1:
        errors.append("Reserve Core must consume exactly one Plutonium Pellet per loop")
    if reserve.count(f"id: '{RESERVE_CORE}'") != 1:
        errors.append("Reserve Core output changed")
    expected_nested_types = {
        "industrial_colonies:creative_deploying": 1,
        "industrial_colonies:creative_pressing": 1,
        # Create Encased has no Creative Spout; Brass is its strongest exact
        # filling environment for this otherwise Creative-tier line.
        "industrial_colonies:brass_filling": 1,
    }
    for recipe_type, expected in expected_nested_types.items():
        if reserve.count(f"type: '{recipe_type}'") != expected:
            errors.append(f"Reserve Core exact nested machine changed: {recipe_type}")
    for recipe_type in ("create:deploying", "create:pressing", "create:filling"):
        if f"type: '{recipe_type}'" in reserve:
            errors.append(f"Reserve Core contains universal nested step: {recipe_type}")

    if RECIPE_ID_LITERAL.findall(star) != [STAR_RECIPE]:
        errors.append("Industrial Star recipe identity or uniqueness changed")
    if star.count(f"id: '{INDUSTRIAL_STAR}'") != 1:
        errors.append("Industrial Star output changed")
    if star.count(f"item: '{BLACK_HOLE}'") != 1:
        errors.append("Industrial Star must consume exactly one Black Hole key entry")
    if star.count(f"item: '{RESERVE_CORE}'") != 1:
        errors.append("Industrial Star must consume exactly one Reserve Core key entry")
    if star.count("type: 'industrial_colonies:creative_mechanical_crafting'") != 1:
        errors.append("Industrial Star must remain a Creative-tier mechanical craft")

    quest_rows = quests.get("quests")
    if not isinstance(quest_rows, list):
        errors.append("Industrial Endgame quest list is missing")
        return errors
    by_key = {
        row.get("key"): row
        for row in quest_rows
        if isinstance(row, dict) and isinstance(row.get("key"), str)
    }
    expected_dependencies = {
        "black_hole": [],
        "industrial_reserves": ["black_hole"],
        "industrial_star": ["industrial_reserves"],
    }
    expected_items = {
        "black_hole": BLACK_HOLE,
        "industrial_reserves": RESERVE_CORE,
        "industrial_star": INDUSTRIAL_STAR,
    }
    for key, dependencies in expected_dependencies.items():
        row = by_key.get(key)
        if not isinstance(row, dict):
            errors.append(f"capstone guidance quest is missing: {key}")
            continue
        if row.get("dependencies") != dependencies:
            errors.append(f"capstone quest dependency chain changed at {key}")
        if row.get("tasks") != [
            {"type": "item", "item": expected_items[key], "count": 1}
        ]:
            errors.append(f"capstone quest physical item target changed at {key}")
    return errors


def validate(project: Path, catalog: Path, mods: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    required_paths = [
        catalog / "recipes.csv",
        catalog / "recipe_refs.csv",
        project / "pack-scripts" / "server_scripts" / BRIDGE_SCRIPT,
    ]
    for path in required_paths:
        if not path.is_file():
            errors.append(f"required capstone-reachability input is missing: {path}")
    if not mods.is_dir():
        errors.append(f"installed mods directory is missing: {mods}")
    if errors:
        return errors, {}

    recipes = read_csv(catalog / "recipes.csv")
    refs = read_csv(catalog / "recipe_refs.csv")
    recipes_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in recipes:
        recipes_by_id[row.get("recipe_id", "")].append(row)

    mod_ids = extract_mod_ids(mods)
    errors.extend(validate_mod_contract(mod_ids))

    bridge_path = project / "pack-scripts" / "server_scripts" / BRIDGE_SCRIPT
    bridge_text = bridge_path.read_text(encoding="utf-8-sig")
    errors.extend(validate_bridge_text(bridge_text))

    raw_by_id: dict[str, dict[str, Any]] = {}
    for recipe_id in STOCK_ROUTE_IDS:
        rows = recipes_by_id.get(recipe_id, [])
        if len(rows) == 1:
            try:
                raw_by_id[recipe_id] = load_raw_recipe(rows[0], mods)
            except (OSError, KeyError, json.JSONDecodeError, zipfile.BadZipFile, ValueError) as exc:
                errors.append(f"cannot read installed stock recipe {recipe_id}: {exc}")

    removals = project_removal_ids(project)
    errors.extend(validate_stock_contract(recipes_by_id, refs, raw_by_id, removals))
    errors.extend(validate_source_exclusivity(project, refs))

    scripts = project / "pack-scripts" / "server_scripts"
    quests = read_json(project / "progression" / "industrial_megaprojects.json")
    errors.extend(
        validate_capstone_texts(
            (scripts / "industrial_black_hole_megaproject.js").read_text(encoding="utf-8-sig"),
            (scripts / "industrial_reserve_core_megaproject.js").read_text(encoding="utf-8-sig"),
            (scripts / "industrial_star_megaproject.js").read_text(encoding="utf-8-sig"),
            quests,
        )
    )

    report = {
        "status": "PASS" if not errors else "FAIL",
        "mekanism_generators_installed": "mekanismgenerators" in mod_ids,
        "canonical_waste_source": BRIDGE_RECIPE,
        "canonical_waste_source_count": 1,
        "retained_stock_recipes": sorted(STOCK_ROUTE_IDS),
        "conflicting_nuclear_waste_sources": 0,
        "reserve_core_loops": RESERVE_LOOPS,
        "reserve_core_plutonium_pellets": RESERVE_LOOPS,
        "reserve_core_exact_nested_machines": [
            "createcasing:creative_deployer",
            "createcasing:creative_press",
            "createcasing:brass_spout",
        ],
        "minimum_blutonium_ingots_for_reserve_core": 5120,
        "reachable_chain": [
            "bigreactors:blutonium_ingot",
            NUCLEAR_WASTE,
            PLUTONIUM,
            PLUTONIUM_PELLET,
            RESERVE_CORE,
            INDUSTRIAL_STAR,
        ],
        "parallel_star_component": BLACK_HOLE,
    }
    return errors, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors, report = validate(
        args.project.resolve(), args.catalog.resolve(), args.mods.resolve()
    )
    if errors:
        print("FAIL: capstone actinide route is not physically reachable", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(
        "PASS: Mekanism Generators is intentionally absent; one exact Blutonium "
        "dissolution bridge feeds both retained stock Mekanism actinide recipes, "
        "512 Plutonium Pellets feed the Reserve Core, and the Black Hole/Reserve "
        "Core converge on the Industrial Star."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
