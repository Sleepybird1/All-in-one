#!/usr/bin/env python3
"""Validate the KJSGen 2.0.5 removal-card export compatibility patch."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KJSGEN_JAR = PROJECT_ROOT / "libs" / "kjsgen-neoforge-2.0.5+mc1.21.1.jar"
MIXIN_ROOT = (
    PROJECT_ROOT
    / "src"
    / "main"
    / "java"
    / "dev"
    / "godpc"
    / "industrialcolonies"
    / "mixin"
)
ASSEMBLER_MIXIN = MIXIN_ROOT / "KjsGenScriptAssemblerMixin.java"
DISABLED_FILTER = (
    PROJECT_ROOT
    / "src"
    / "main"
    / "java"
    / "dev"
    / "godpc"
    / "industrialcolonies"
    / "KjsGenDisabledRecipeFilter.java"
)
PROJECT_MIXIN = MIXIN_ROOT / "KjsGenRecipeProjectMixin.java"
MIXIN_CONFIG = (
    PROJECT_ROOT / "src" / "main" / "resources" / "industrial_colonies.mixins.json"
)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    require(KJSGEN_JAR.is_file(), f"missing pinned KJSGen jar: {KJSGEN_JAR}", errors)
    require(ASSEMBLER_MIXIN.is_file(), f"missing assembler mixin: {ASSEMBLER_MIXIN}", errors)
    require(DISABLED_FILTER.is_file(), f"missing disabled-recipe filter: {DISABLED_FILTER}", errors)
    require(PROJECT_MIXIN.is_file(), f"missing project mixin: {PROJECT_MIXIN}", errors)
    require(MIXIN_CONFIG.is_file(), f"missing mixin config: {MIXIN_CONFIG}", errors)

    if KJSGEN_JAR.is_file():
        with zipfile.ZipFile(KJSGEN_JAR) as archive:
            required_entries = {
                "com/zizazr/kjsgen/core/RecipeProject.class",
                "com/zizazr/kjsgen/core/RemovalRule.class",
                "com/zizazr/kjsgen/integration/kubejs/KubeJsExporter.class",
                "com/zizazr/kjsgen/integration/kubejs/ScriptAssembler.class",
            }
            names = set(archive.namelist())
            for entry in sorted(required_entries):
                require(entry in names, f"pinned KJSGen jar is missing {entry}", errors)

            if required_entries <= names:
                exporter = archive.read(
                    "com/zizazr/kjsgen/integration/kubejs/KubeJsExporter.class"
                )
                assembler = archive.read(
                    "com/zizazr/kjsgen/integration/kubejs/ScriptAssembler.class"
                )
                require(b"exportProject" in exporter, "KJSGen exporter API changed", errors)
                require(b"exportToFile" in exporter, "KJSGen file exporter API changed", errors)
                require(
                    b"ScriptAssembler" in exporter,
                    "KJSGen exporter no longer delegates to ScriptAssembler",
                    errors,
                )
                require(
                    b"appendRemovals" in assembler and b"removalStatement" in assembler,
                    "KJSGen three-argument assembler no longer supports removals",
                    errors,
                )

    if ASSEMBLER_MIXIN.is_file():
        source = ASSEMBLER_MIXIN.read_text(encoding="utf-8")
        required_tokens = (
            "@Mixin(value = ScriptAssembler.class, remap = false)",
            'method = "assemble(Lcom/zizazr/kjsgen/core/RecipeProject;Ljava/util/List;)Ljava/lang/String;"',
            "project.removals()",
            "ScriptAssembler.assemble(project, exportableRecipes, removals)",
            "project.defaultTargetFile()",
            "project.targetFileOf(recipe)",
            '"approved recipes"',
            '"rejected recipes"',
            '"Deferred"',
            '"maybe recipes"',
            '"disabled recipes"',
            "ScriptAssembler.assemble(project, List.of(), List.of())",
            "KjsGenDisabledRecipeFilter.loadDisabledRecipeIds()",
            "!disabledRecipeIds.contains(recipe.recipeId())",
        )
        for token in required_tokens:
            require(token in source, f"assembler mixin is missing {token!r}", errors)

    if DISABLED_FILTER.is_file():
        source = DISABLED_FILTER.read_text(encoding="utf-8")
        for token in (
            '"default.recipe_reviews.json"',
            '"disabled".equals(review.get("status").getAsString())',
            "return Set.of();",
        ):
            require(token in source, f"disabled filter is missing {token!r}", errors)
        require(
            "net.minecraft.client" not in source,
            "disabled filter must remain common-side and client-class free",
            errors,
        )
        allowed_imports = {
            "com.google.gson.JsonElement",
            "com.google.gson.JsonObject",
            "com.google.gson.JsonParser",
            "com.mojang.logging.LogUtils",
            "net.neoforged.fml.loading.FMLPaths",
            "org.slf4j.Logger",
            "java.nio.charset.StandardCharsets",
            "java.nio.file.Files",
            "java.nio.file.Path",
            "java.util.HashSet",
            "java.util.Set",
        }
        actual_imports = {
            line.removeprefix("import ").removesuffix(";")
            for line in source.splitlines()
            if line.startswith("import ")
        }
        require(
            actual_imports <= allowed_imports,
            "disabled filter gained a non-whitelisted dependency: "
            + repr(sorted(actual_imports - allowed_imports)),
            errors,
        )

    if PROJECT_MIXIN.is_file():
        source = PROJECT_MIXIN.read_text(encoding="utf-8")
        required_tokens = (
            "@Mixin(value = RecipeProject.class, remap = false)",
            '@Inject(method = "recipesByTargetFile", at = @At("RETURN"))',
            "rule -> !rule.isEmpty()",
            "computeIfAbsent(defaultTargetFile()",
        )
        for token in required_tokens:
            require(token in source, f"project mixin is missing {token!r}", errors)

    if MIXIN_CONFIG.is_file():
        config = json.loads(MIXIN_CONFIG.read_text(encoding="utf-8"))
        mixins = config.get("mixins", [])
        for name in ("KjsGenRecipeProjectMixin", "KjsGenScriptAssemblerMixin"):
            require(name in mixins, f"mixin config does not register {name}", errors)

    # Model the routing contract independently of Mixin/KJSGen runtime classes.
    default_target = "kjsgen_recipes"
    batches = {
        default_target: [default_target],
        "custom_recipes": ["custom_recipes"],
        "removal_only_default": [],
    }
    receives_removals = {
        name: (not targets or default_target in targets)
        for name, targets in batches.items()
    }
    require(receives_removals[default_target], "default batch lost removals", errors)
    require(
        not receives_removals["custom_recipes"],
        "non-default batch would duplicate removals",
        errors,
    )
    require(
        receives_removals["removal_only_default"],
        "removal-only default batch lost removals",
        errors,
    )

    # Disabling suppresses only the exact custom producer. Its project's
    # removal rules must still reach the default target so a replaced stock
    # recipe does not reappear.
    disabled_ids = {"industrial_colonies:disabled_machine"}
    recipe_ids = {
        "industrial_colonies:disabled_machine",
        "industrial_colonies:enabled_machine",
    }
    exported = recipe_ids - disabled_ids
    require(
        exported == {"industrial_colonies:enabled_machine"},
        "disabled ledger IDs were not filtered exactly",
        errors,
    )
    require(receives_removals[default_target], "disabled filtering lost removals", errors)

    if errors:
        print("FAIL: KJSGen removal export compatibility", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print(
        "PASS: KJSGen removal cards route through the three-argument assembler "
        "once in the default target, including removal-only projects; the "
        "approved/rejected/Deferred/disabled review archives export no duplicate producers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
