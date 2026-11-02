#!/usr/bin/env python3
"""Validate the unattended, marker-safe KJSGen startup export hook."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "src/main/java/dev/godpc/industrialcolonies"
KJSGEN_JAR = ROOT / "libs/kjsgen-neoforge-2.0.5+mc1.21.1.jar"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    auto_export = (JAVA / "KjsGenAutoExporter.java").read_text(encoding="utf-8")
    entrypoint = (JAVA / "IndustrialColonies.java").read_text(encoding="utf-8")
    layout_hook = (JAVA / "mixin/KjsGenJsonLayoutLoaderMixin.java").read_text(encoding="utf-8")
    assembler = (JAVA / "mixin/KjsGenScriptAssemblerMixin.java").read_text(encoding="utf-8")
    metadata = (ROOT / "src/main/templates/META-INF/neoforge.mods.toml").read_text(encoding="utf-8")

    for token in (
        "FMLClientSetupEvent",
        "event.enqueueWork(KjsGenAutoExporter::afterClientSetup)",
        "KjsGenIntegration.installMachineCentricDefinitions()",
        "ProjectManager.load(DEFAULT_PROJECT)",
        "ProjectManager.setCurrent(project)",
        "KubeJsExporter.exportProject(project)",
        "!layoutFallbackUsed",
        "layoutFallbackUsed = true",
        "catch (Exception | LinkageError exception)",
        "The client will continue to the main menu",
    ):
        require(token in auto_export, f"startup exporter is missing {token!r}", failures)

    require(
        "FMLEnvironment.dist == Dist.CLIENT" in entrypoint
        and "KjsGenAutoExporter.register(modEventBus)" in entrypoint,
        "auto-export listener is not guarded to the physical client",
        failures,
    )
    require(
        "KjsGenAutoExporter.onRecipeLayoutsReady()" in layout_hook,
        "late-layout one-shot export fallback is missing",
        failures,
    )
    require(
        layout_hook.index("KjsGenIntegration.installMachineCentricDefinitions()")
        < layout_hook.index("KjsGenAutoExporter.onRecipeLayoutsReady()"),
        "resource fallback runs before process-centric layouts are restored",
        failures,
    )
    require(
        "Files.write(" not in auto_export and "Files.writeString(" not in auto_export,
        "startup hook writes scripts directly instead of using KJSGen's marker-aware exporter",
        failures,
    )
    require(
        ".filter(KjsGenScriptAssemblerMixin::isExportable)" in assembler,
        "startup export no longer inherits the WIP-card filter",
        failures,
    )

    dependency = re.search(
        r"\[\[dependencies\.\$\{mod_id\}\]\]\s*"
        r"modId=\"kjsgen\"(?P<body>.*?)(?=\[\[dependencies\.|\Z)",
        metadata,
        re.DOTALL,
    )
    require(dependency is not None, "KJSGen dependency declaration is missing", failures)
    if dependency is not None:
        require('type="required"' in dependency.group("body"), "KJSGen dependency is not required", failures)
        require('side="BOTH"' in dependency.group("body"), "KJSGen dependency is not available on both sides", failures)

    require(KJSGEN_JAR.is_file(), f"KJSGen compile jar is missing: {KJSGEN_JAR}", failures)
    if KJSGEN_JAR.is_file():
        try:
            with zipfile.ZipFile(KJSGEN_JAR) as archive:
                exporter = archive.read(
                    "com/zizazr/kjsgen/integration/kubejs/KubeJsExporter.class"
                )
            require(b"// kjsgen:start" in exporter, "KJSGen exporter start marker is absent", failures)
            require(b"// kjsgen:end" in exporter, "KJSGen exporter end marker is absent", failures)
            require(b"mergeBlock" in exporter, "KJSGen exporter has no marker-aware merge implementation", failures)
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            failures.append(f"could not inspect KJSGen exporter bytecode: {exc}")

    if failures:
        print(f"FAIL: {len(failures)} KJSGen auto-export issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: default KJSGen project auto-exports on client startup through the "
        "marker-aware exporter, with WIP filtering and nonfatal failure handling."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
