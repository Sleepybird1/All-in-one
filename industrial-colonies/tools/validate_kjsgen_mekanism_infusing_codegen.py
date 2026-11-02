#!/usr/bin/env python3
"""Guard the 1.21.1 KJSGen -> Mekanism metallurgic-infusing export fix."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA = Path("src/main/java/dev/godpc/industrialcolonies/KjsGenIntegration.java")
PROJECT = Path("pack-kjsgen/default.managed.json")
KJSGEN_JAR = Path("libs/kjsgen-neoforge-2.0.5+mc1.21.1.jar")
LAYOUT = "assets/kjsgen/kjsgen_layouts/mekanism_metallurgic_infusing.json"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def validate(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    java = root / JAVA
    project_path = root / PROJECT
    kjsgen_jar = root / KJSGEN_JAR
    source = java.read_text(encoding="utf-8")

    required_source_tokens = (
        "MEKANISM_METALLURGIC_INFUSING_CODEGEN",
        "new MekanismMetallurgicInfusingCodegen()",
        'RecipeTypeRegistry.get("kjsgen:mekanism_metallurgic_infusing")',
        "withCodegen(source, MEKANISM_METALLURGIC_INFUSING_CODEGEN)",
        "event.custom({ type: 'mekanism:metallurgic_infusing'",
        "item_input:",
        "chemical_input:",
        "per_tick_usage:",
        'KjsGenIntegration.requireRecipeId(recipe, "Mekanism metallurgic infusing")',
        '}).id(" + JsUtil.quote(recipeId) + ")"',
        'Optional.of("mekanism:metallurgic_infusing")',
    )
    for token in required_source_tokens:
        require(token in source, f"Mekanism compatibility codegen is missing {token!r}", failures)

    require(
        "event.recipes.mekanism.metallurgic_infusing" not in source,
        "compatibility codegen regressed to the incompatible positional recipe constructor",
        failures,
    )
    require(
        "installMachineCentricDefinitions()" in source,
        "resource-reload reinstallation path is missing",
        failures,
    )

    require(kjsgen_jar.is_file(), f"KJSGen compile jar is missing: {kjsgen_jar}", failures)
    if kjsgen_jar.is_file():
        try:
            with zipfile.ZipFile(kjsgen_jar) as archive:
                bundled = json.loads(archive.read(LAYOUT))
            template = next(
                parameter["default"]
                for parameter in bundled["parameters"]
                if parameter["key"] == "__template"
            )
            require(
                template.endswith(", {param:perTickUsage})"),
                "upstream KJSGen layout no longer has the four-argument incompatibility; "
                "review whether the override is still needed",
                failures,
            )
        except (OSError, KeyError, StopIteration, ValueError, zipfile.BadZipFile) as exc:
            failures.append(f"could not inspect KJSGen's bundled Mekanism layout: {exc}")

    project = json.loads(project_path.read_text(encoding="utf-8"))
    recipes = [
        recipe
        for recipe in project.get("recipes", [])
        if recipe.get("type") == "kjsgen:mekanism_metallurgic_infusing"
    ]
    require(recipes, "managed project has no metallurgic-infusing regression fixture", failures)
    for recipe in recipes:
        recipe_id = recipe.get("recipeId", recipe.get("uid", "<unknown>"))
        slots = recipe.get("slots", {})
        expected_kinds = {
            "input": {"ITEM", "ITEM_TAG"},
            "infusion": {"CHEMICAL", "CHEMICAL_TAG"},
            "output": {"ITEM"},
        }
        for key, kinds in expected_kinds.items():
            slot = slots.get(key, {})
            require(
                slot.get("kind") in kinds,
                f"{recipe_id} has unsupported {key} kind {slot.get('kind')!r}",
                failures,
            )
            require(
                not slot.get("components"),
                f"{recipe_id} uses components in {key}; extend the custom JSON codegen first",
                failures,
            )
        per_tick = recipe.get("params", {}).get("perTickUsage", "false")
        require(
            per_tick in {"true", "false"},
            f"{recipe_id} has invalid perTickUsage value {per_tick!r}",
            failures,
        )

    return failures


def main() -> int:
    failures = validate()
    if failures:
        print(f"FAIL: {len(failures)} KJSGen Mekanism codegen issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: KJSGen metallurgic-infusing cards retain their visual layout but export "
        "through Mekanism's exact 1.21.1 JSON codec shape, including per_tick_usage "
        "and an explicit recipe ID."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
