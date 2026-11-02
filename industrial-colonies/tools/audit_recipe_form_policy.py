#!/usr/bin/env python3
"""Audit approved recipes against the functional-block manufacturing policy."""

from __future__ import annotations

import argparse
import json
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACCEPTANCE = ROOT / "progression/recipe_review_acceptance.json"
DEFAULT_MANIFEST = ROOT / "progression/managed_recipe_overhaul.json"
DEFAULT_CATALOG = Path(
    r"C:\Users\GodPC\Documents\Codex\2026-08-16\ok\exports\ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt"
)
DEFAULT_REPORT = ROOT / "progression/recipe_form_policy_audit.json"

PROCESS_TYPES = {
    "compacting",
    "mixing",
    "deploying",
    "sequenced_assembly",
    "tfmg_vat",
    "pressing",
    "cutting",
    "crushing",
    "mekanism_enriching",
    "mekanism_metallurgic_infusing",
}

# These are component/material families even when Minecraft registers the output
# as a placeable block.  The player explicitly reserved them for process recipes.
COMPONENT_MARKERS = (
    "casing", "frame", "plate", "plating", "sheet", "wire", "cable",
    "pipe", "tube", "conductor", "transporter", "barrel", "tank", "cell",
    "housing", "terminal", "installer", "circuit", "processor",
    "semiconductor", "transistor", "capacitor", "coil", "rotor", "shaft",
    "rod", "blade", "bearing", "valve", "connector", "hub", "panel",
    "brick", "reinforcement", "insulator", "spool", "oil_can", "oil_hammer",
    "casting_sand",
)

ROCKET_SEQUENCE_MARKERS = (
    "thruster", "engine_nozzle", "engine_pipes", "hose_anchor",
    "thruster_mount", "separator", "rocket_engine", "vector",
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def runtime_blocks(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    section = text.split("ALL RUNTIME BLOCK REGISTRY IDS (18749)", 1)[1]
    return {
        line.strip()
        for line in section.splitlines()
        if line.strip() and ":" in line and " " not in line
    }


def output_id(recipe: dict[str, Any]) -> str:
    output = recipe.get("output")
    if isinstance(output, str):
        # Manifest quantities are represented separately in current data, but
        # tolerate the conventional "4x namespace:path" notation as well.
        return output.rsplit(" ", 1)[-1]
    return ""


def card_outputs(card: dict[str, Any]) -> set[str]:
    return {
        str(value.get("id"))
        for key, value in card.get("slots", {}).items()
        if key.startswith("output") and isinstance(value, dict) and value.get("id")
    }


def accepted_recipe(entry: dict[str, Any]) -> dict[str, Any]:
    card = entry.get("card", {})
    card_type = str(card.get("type", ""))
    if card_type.startswith("kjsgen:"):
        card_type = card_type.removeprefix("kjsgen:")
    if card_type.startswith("create_"):
        card_type = card_type.removeprefix("create_")
    outputs = sorted(card_outputs(card))
    return {
        "id": str(entry.get("recipeId", "")),
        "type": card_type,
        "output": outputs[0] if len(outputs) == 1 else "",
    }


def is_process_exception(recipe: dict[str, Any], output: str) -> tuple[bool, str]:
    namespace, _, path = output.partition(":")
    recipe_id = str(recipe.get("id", ""))
    combined = f"{path} {recipe_id}".lower()
    if namespace == "createcasing":
        return True, "Create Encased machine-family tier"
    if any(marker in combined for marker in ROCKET_SEQUENCE_MARKERS):
        return True, "rocket assembly exception"
    if path.endswith("_charge"):
        return True, "component/material exception"
    if any(marker in combined for marker in COMPONENT_MARKERS):
        return True, "component/material exception"
    return False, ""


def verdict(recipe: dict[str, Any], blocks: set[str]) -> tuple[str, str]:
    kind = str(recipe.get("type", ""))
    output = output_id(recipe)
    exception, exception_reason = is_process_exception(recipe, output)
    if kind == "mechanical_crafting":
        if exception:
            return "requeue", f"{exception_reason} must use a process recipe"
        return "conforming", "functional block/machine uses Mechanical Crafting"
    if output in blocks and not exception:
        return "requeue", "functional registered block does not use Mechanical Crafting"
    if exception and kind not in PROCESS_TYPES:
        return "requeue", f"{exception_reason} must use a process recipe"
    if kind in PROCESS_TYPES:
        return "conforming", exception_reason or "component uses a process recipe"
    if output not in blocks:
        return "conforming", "non-block item is outside this form policy"
    return "requeue", "recipe form is neither Mechanical Crafting nor an allowed process"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", type=Path, default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--update-acceptance", action="store_true")
    args = parser.parse_args()

    acceptance = load(args.acceptance)
    manifest = load(args.manifest)
    blocks = runtime_blocks(args.catalog)
    recipes = manifest.get("recipes", [])
    by_id = {recipe["id"]: recipe for recipe in recipes}
    by_output = {output_id(recipe): recipe for recipe in recipes if output_id(recipe)}
    approved = {
        entry["recipeId"]: entry
        for entry in acceptance.get("entries", [])
        if entry.get("decision", {}).get("status") == "approved"
    }

    entries: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    for recipe_id, accepted in sorted(approved.items()):
        # An approval freezes the accepted card even when the later raw source
        # contains a superseding draft, so audit the card the player will
        # actually see and use—not that superseding draft.
        recipe = accepted_recipe(accepted)
        if recipe is None:
            entries.append(OrderedDict((
                ("recipeId", recipe_id),
                ("output", ""),
                ("recipeType", "missing"),
                ("verdict", "requeue"),
                ("reason", "approved recipe is absent from the current managed manifest"),
            )))
            counts["requeue"] += 1
            continue
        result, reason = verdict(recipe, blocks)
        counts[result] += 1
        entries.append(OrderedDict((
            ("recipeId", recipe_id),
            ("currentRecipeId", str(recipe.get("id", ""))),
            ("output", output_id(recipe)),
            ("recipeType", str(recipe.get("type", ""))),
            ("verdict", result),
            ("reason", reason),
        )))

    report = OrderedDict((
        ("schemaVersion", 1),
        ("policy", "functional blocks and machines use Mechanical Crafting; components and explicit exceptions use process recipes"),
        ("approvedAudited", len(approved)),
        ("conforming", counts["conforming"]),
        ("requeued", counts["requeue"]),
        ("requeueRecipeIds", [entry["recipeId"] for entry in entries if entry["verdict"] == "requeue"]),
        ("entries", entries),
    ))
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not args.report.is_file() or args.report.read_text(encoding="utf-8") != encoded:
            raise SystemExit("recipe-form policy audit is stale")
    else:
        args.report.write_text(encoded, encoding="utf-8")
    expected_requeue = report["requeueRecipeIds"]
    if args.update_acceptance:
        acceptance["policyRequeueRecipeIds"] = expected_requeue
        args.acceptance.write_text(
            json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    elif acceptance.get("policyRequeueRecipeIds", []) != expected_requeue:
        raise SystemExit(
            "recipe-form policy requeue list is stale; run with --update-acceptance"
        )
    print(f"Audited {len(approved)} approved recipes: {counts['conforming']} conform, {counts['requeue']} require re-review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
