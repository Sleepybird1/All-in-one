#!/usr/bin/env python3
"""Validate KJSGen WIP-card filtering and unambiguous Create item-tag codegen."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "src/main/java/dev/godpc/industrialcolonies"
MANAGED = ROOT / "pack-kjsgen/default.managed.json"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    assembler = (JAVA / "mixin/KjsGenScriptAssemblerMixin.java").read_text(encoding="utf-8")
    safety = (JAVA / "KjsGenCodegenSafety.java").read_text(encoding="utf-8")
    process = (JAVA / "KjsGenIntegration.java").read_text(encoding="utf-8")
    sequence = (JAVA / "KjsGenSequencedAssemblyIntegration.java").read_text(encoding="utf-8")
    managed = json.loads(MANAGED.read_text(encoding="utf-8-sig"))

    for token in (
        "RecipeValidator.validate(recipe, type)",
        "RecipeValidator.hasErrors",
        ".filter(KjsGenScriptAssemblerMixin::isExportable)",
        "ScriptAssembler.assemble(project, exportableRecipes, removals)",
    ):
        require(token in assembler, f"invalid/WIP export filter is missing {token!r}", failures)

    require("Ingredient.of(" in safety, "item-tag repair does not emit Ingredient.of", failures)
    require("BARE_ITEM_TAG" in safety, "item-tag repair pattern is absent", failures)
    require(
        "KjsGenCodegenSafety.forceItemTagIngredients" in process,
        "process codegen does not repair ambiguous item tags",
        failures,
    )
    require(
        "KjsGenCodegenSafety.forceItemTagIngredients" in sequence,
        "sequenced codegen does not repair ambiguous item tags",
        failures,
    )
    require(
        '"returned_tool", SlotRole.OUTPUT' in process,
        "compacting editor has no optional returned-mold output",
        failures,
    )

    recipes = {recipe.get("recipeId"): recipe for recipe in managed.get("recipes", [])}
    printed = recipes.get("industrial_colonies:electronics/printed_silicon", {})
    slots = printed.get("slots", {})
    require(printed.get("type") == "kjsgen:create_compacting", "printed silicon is not compacting", failures)
    require(
        slots.get("__machine_process_compacting", {}).get("id") == "createcasing:brass_press",
        "printed silicon is not bound to the Brass Press",
        failures,
    )
    require(slots.get("in0", {}).get("id") == "tfmg:silicon_ingot", "printed silicon is not TFMG-first", failures)
    require(slots.get("in1", {}).get("id") == "ae2:silicon_press", "silicon mold input is absent", failures)
    require(
        slots.get("returned_tool", {}).get("id") == "ae2:silicon_press",
        "silicon mold is not returned",
        failures,
    )

    recipe_ids = set(recipes)
    removal_ids = {entry.get("recipeId") for entry in managed.get("removals", [])}
    require(
        "industrial_colonies:electronics/empty_circuit_board" not in recipe_ids,
        "stock TFMG empty-board recipe is still replaced",
        failures,
    )
    require(
        "tfmg:crafting/materials/empty_circuit_board" not in removal_ids,
        "stock TFMG empty-board recipe is still removed",
        failures,
    )

    # The repair must be idempotent for already wrapped expressions.
    pattern = re.compile(r"(?<!Ingredient\.of\()'#[^']+'");
    sample = "['#c:plates/copper', Ingredient.of('#c:plates/gold')]"
    repaired = pattern.sub(lambda match: f"Ingredient.of({match.group(0)})", sample)
    require(
        repaired == "[Ingredient.of('#c:plates/copper'), Ingredient.of('#c:plates/gold')]",
        "item-tag repair is not idempotent",
        failures,
    )

    if failures:
        print(f"FAIL: {len(failures)} KJSGen export-safety issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: invalid WIP cards are skipped and exact-machine Create item tags are unambiguous.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
