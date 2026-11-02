#!/usr/bin/env python3
"""Validate the narrow KubeJS/Modern Foundry bootstrap compatibility mixin."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "src/main/java/dev/godpc/industrialcolonies/mixin/KubeJsOutputFilterMixin.java"
)
MIXINS = ROOT / "src/main/resources/industrial_colonies.mixins.json"
BUILD_GRADLE = ROOT / "build.gradle"
GRADLE_PROPERTIES = ROOT / "gradle.properties"
TARGET_CLASS = "dev/latvian/mods/kubejs/recipe/filter/OutputFilter.class"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def property_value(name: str) -> str:
    text = GRADLE_PROPERTIES.read_text(encoding="utf-8")
    match = re.search(rf"(?m)^{re.escape(name)}=(.+)$", text)
    require(match is not None, f"Missing {name} in gradle.properties")
    return match.group(1).strip()


def validate_source() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    require(
        'targets = "dev.latvian.mods.kubejs.recipe.filter.OutputFilter"' in source,
        "Mixin no longer targets only KubeJS OutputFilter",
    )
    require(
        'method = "test(Ldev/latvian/mods/kubejs/recipe/filter/RecipeMatchContext;)Z"'
        in source,
        "Mixin no longer selects the exact KubeJS 368 test signature",
    )
    require(
        "RecipeLikeKJS;" in source
        and "hasOutput(" in source
        and "ReplacementMatchInfo;)Z" in source,
        "Mixin no longer redirects only RecipeLikeKJS.hasOutput",
    )
    require(
        "Cannot get config value before config is loaded." in source,
        "Mixin must match the exact expected NeoForge lifecycle message",
    )
    require(
        "TagPreference$RegistryComparator" in source
        and "modernmods.modernfoundry.library.recipe.casting.ItemCastingRecipe" in source,
        "Mixin must verify both Hilt and Modern Foundry stack frames",
    )
    require(
        "throw exception;" in source and "return false;" in source,
        "Mixin must rethrow unrelated failures and skip only the affected recipe match",
    )


def validate_registration() -> None:
    config = json.loads(MIXINS.read_text(encoding="utf-8"))
    require(
        "KubeJsOutputFilterMixin" in config.get("mixins", []),
        "KubeJS compatibility mixin is not registered",
    )
    build = BUILD_GRADLE.read_text(encoding="utf-8")
    require(
        "kubejs-neoforge-2101.7.2-build.368.jar" in build,
        "Exact KubeJS 368 compile-only dependency is missing",
    )


def validate_installed_signature() -> Path:
    mods_dir = Path(property_value("pack_mods_dir"))
    jars = sorted(mods_dir.glob("kubejs-neoforge-2101.7.2-build.368.jar"))
    require(len(jars) == 1, f"Expected one exact KubeJS 368 JAR, found {jars}")
    jar = jars[0]
    with zipfile.ZipFile(jar) as archive:
        require(TARGET_CLASS in archive.namelist(), f"Missing {TARGET_CLASS} in {jar.name}")
        bytecode = archive.read(TARGET_CLASS)

    for marker in (
        b"test",
        b"(Ldev/latvian/mods/kubejs/recipe/filter/RecipeMatchContext;)Z",
        b"dev/latvian/mods/kubejs/core/RecipeLikeKJS",
        b"hasOutput",
        b"(Ldev/latvian/mods/kubejs/recipe/filter/RecipeMatchContext;"
        b"Ldev/latvian/mods/kubejs/recipe/match/ReplacementMatchInfo;)Z",
    ):
        require(marker in bytecode, f"Installed OutputFilter lacks marker {marker!r}")
    return jar


def validate_compiled_output() -> None:
    if not (ROOT / "build").exists():
        return
    compiled = (
        ROOT
        / "build/classes/java/main/dev/godpc/industrialcolonies/mixin"
        / "KubeJsOutputFilterMixin.class"
    )
    require(compiled.is_file(), "Compiled KubeJS output-filter mixin is missing")


def main() -> int:
    try:
        validate_source()
        validate_registration()
        jar = validate_installed_signature()
        validate_compiled_output()
    except (AssertionError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1
    print(f"[PASS] KubeJS output-filter compatibility validated against {jar.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
