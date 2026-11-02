#!/usr/bin/env python3
"""Pin the KJSGen editor/compiler contract for TFMG 1.2.0 Chemical Vats."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = Path(
    "src/main/resources/assets/industrial_colonies/kjsgen_layouts/tfmg_chemical_vat.json"
)
INTEGRATION = Path("src/main/java/dev/godpc/industrialcolonies/KjsGenIntegration.java")
CODEGEN = Path("src/main/java/dev/godpc/industrialcolonies/TfmgChemicalVatCodegen.java")
COMPILER = Path("tools/generate_managed_recipe_overhaul.py")
MANAGED_VALIDATOR = Path("tools/validate_managed_recipe_overhaul.py")
REQUIRED_FILES = (LAYOUT, INTEGRATION, CODEGEN, COMPILER, MANAGED_VALIDATOR)

TFMG_JAR_NAME = "tfmg-1.2.0.jar"
TFMG_CLASSES = {
    "com/drmangotea/tfmg/recipes/VatRecipeParams.class": (
        "42F8F1D72B2479BCF3EA4D45E48FDCA09F96E85AB9696E3E10C5D084138E7B5F"
    ),
    "com/drmangotea/tfmg/recipes/VatMachineRecipe.class": (
        "459022E8F54BD1378499D65176B29D6196E951A3580866DFF6C44A34AD0D9DD0"
    ),
}
STOCK_RECIPES = (
    "data/tfmg/recipe/vat_machine_recipe/sulfuric_acid.json",
    "data/tfmg/recipe/vat_machine_recipe/aluminum.json",
)
PROJECT_JAR_ENTRIES = (
    "assets/industrial_colonies/kjsgen_layouts/tfmg_chemical_vat.json",
    "dev/godpc/industrialcolonies/KjsGenIntegration.class",
    "dev/godpc/industrialcolonies/TfmgChemicalVatCodegen.class",
)

EXPECTED_VAT_MODES = ["steel", "firebrick", "both"]
EXPECTED_MACHINE_MODES = ["mixing", "two_electrodes"]
EXPECTED_HEAT_MODES = ["none", "heated", "superheated"]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _load_compiler(path: Path) -> ModuleType:
    name = f"_tfmg_vat_compiler_{hash(path.resolve()) & 0xFFFFFFFF:x}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load compiler module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_layout(root: Path, failures: list[str]) -> dict[str, Any] | None:
    path = root / LAYOUT
    try:
        layout = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.append(f"cannot read Chemical Vat layout: {exc}")
        return None

    expected_top = {
        "id": "industrial_colonies:tfmg_chemical_vat",
        "jei": "tfmg:vat_machine_recipe",
        "mod": "tfmg",
        "icon": "tfmg:steel_chemical_vat",
        "width": 176,
        "height": 64,
        "codegen": "industrial_colonies:tfmg_chemical_vat",
        "requiresMod": "tfmg",
    }
    for key, value in expected_top.items():
        require(layout.get(key) == value, f"layout {key} drifted from {value!r}", failures)

    slots = layout.get("slots")
    require(isinstance(slots, list) and len(slots) == 2, "layout must have two list slots", failures)
    by_key = {
        slot.get("key"): slot
        for slot in slots or []
        if isinstance(slot, dict) and isinstance(slot.get("key"), str)
    }
    expected_slots = {
        "ingredients": {
            "role": "INPUT",
            "x": 0,
            "y": 4,
            "required": True,
            "item": True,
            "tag": True,
            "fluid": True,
            "count": True,
            "list": True,
        },
        "results": {
            "role": "OUTPUT",
            "x": 116,
            "y": 4,
            "required": True,
            "item": True,
            "fluid": True,
            "count": True,
            "chance": True,
            "list": True,
        },
    }
    for key, contract in expected_slots.items():
        slot = by_key.get(key, {})
        for field, value in contract.items():
            require(
                slot.get(field) == value,
                f"layout {key}.{field} drifted from {value!r}",
                failures,
            )
    require(
        by_key.get("results", {}).get("tag") is not True,
        "layout must not promise tagged Chemical Vat outputs",
        failures,
    )

    parameters = {
        parameter.get("key"): parameter
        for parameter in layout.get("parameters", [])
        if isinstance(parameter, dict)
    }
    expected_parameters = {
        "vatMode": ("ENUM", "both", EXPECTED_VAT_MODES),
        "machineMode": ("ENUM", "mixing", EXPECTED_MACHINE_MODES),
        "heat": ("ENUM", "none", EXPECTED_HEAT_MODES),
        "minSize": ("INT", "0", None),
        "processingTime": ("INT", "100", None),
    }
    require(
        set(parameters) == set(expected_parameters),
        "layout parameters must be exactly vatMode/machineMode/heat/minSize/processingTime",
        failures,
    )
    for key, (kind, default, options) in expected_parameters.items():
        parameter = parameters.get(key, {})
        require(parameter.get("type") == kind, f"layout parameter {key} type drifted", failures)
        require(
            parameter.get("default") == default,
            f"layout parameter {key} default drifted",
            failures,
        )
        if options is not None:
            require(
                parameter.get("options") == options,
                f"layout parameter {key} options drifted",
                failures,
            )
    return layout


def validate_source(root: Path, failures: list[str]) -> None:
    integration = (root / INTEGRATION).read_text(encoding="utf-8")
    codegen = (root / CODEGEN).read_text(encoding="utf-8")
    compiler = (root / COMPILER).read_text(encoding="utf-8")
    managed = (root / MANAGED_VALIDATOR).read_text(encoding="utf-8")

    for token in (
        "TFMG_CHEMICAL_VAT_CODEGEN",
        "new TfmgChemicalVatCodegen()",
        "event.registerCodegen(TFMG_CHEMICAL_VAT_CODEGEN",
    ):
        require(token in integration, f"KJSGen registration is missing {token!r}", failures)

    required_codegen = (
        'RECIPE_TYPE = "tfmg:vat_machine_recipe"',
        "MAX_VISIBLE_SLOTS = 4",
        'recipe.listSlots("ingredients")',
        'recipe.listSlots("results")',
        'recipe.param(type, "vatMode")',
        'recipe.param(type, "machineMode")',
        'recipe.param(type, "heat")',
        'recipe.paramInt(type, "minSize", 0)',
        'recipe.paramInt(type, "processingTime", 100)',
        'case "steel" -> List.of("tfmg:steel_vat")',
        'case "firebrick" -> List.of("tfmg:firebrick_lined_vat")',
        'case "both" -> List.of("tfmg:steel_vat", "tfmg:firebrick_lined_vat")',
        'case "mixing" -> List.of("tfmg:mixing")',
        'case "two_electrodes" -> List.of("tfmg:electrode", "tfmg:electrode")',
        'requireDomainLimits(ingredientSlots, true, "ingredients")',
        "supports at most four expanded items and four fluids",
        "for (int index = 0; index < copies; index++)",
        "type: 'neoforge:single'",
        "type: 'neoforge:tag'",
        "heat_requirement:",
        "processing_time:",
        "allowed_vat_types:",
        "KjsGenIntegration.requireRecipeId(recipe, \"TFMG Chemical Vat\")",
        '}).id("',
        "return Optional.of(RECIPE_TYPE)",
    )
    for token in required_codegen:
        require(token in codegen, f"Chemical Vat codegen is missing {token!r}", failures)
    require("pressure" not in codegen, "Chemical Vat codegen exposes unsupported pressure", failures)
    require("heat_level" not in codegen, "Chemical Vat codegen exposes heat_level", failures)

    required_compiler = (
        "def tfmg_vat(",
        'TFMG_VAT_CARD_TYPE = "industrial_colonies:tfmg_chemical_vat"',
        'aliased_field(spec, "ingredients", "inputs")',
        'aliased_field(spec, "results", "outputs")',
        'aliased_field(spec, "vat_mode", "vat")',
        'aliased_field(spec, "machine_mode", "machine")',
        "defines conflicting {canonical}/{alias} values",
        'slots[f"ingredients{index}"]',
        'slots[f"results{index}"]',
        'expanded_item_ingredients += int(parsed.get("count", 1))',
        "expanded item ingredients",
        '("vatMode", vat_mode)',
        '("machineMode", machine_mode)',
        '("processingTime", str(processing_time))',
        'elif kind == "tfmg_vat":',
        "compiled.append(tfmg_vat(spec, uid))",
        'for forbidden in ("pressure", "heat_level")',
    )
    for token in required_compiler:
        require(token in compiler, f"managed compiler is missing {token!r}", failures)

    required_managed = (
        '"tfmg_vat": TFMG_VAT_CARD_TYPE',
        'elif recipe_type == "tfmg_vat":',
        'aliased_field(spec, "ingredients", "inputs", path, diagnostics)',
        'aliased_field(spec, "results", "outputs", path, diagnostics)',
        'aliased_field(spec, "vat_mode", "vat", path, diagnostics)',
        'aliased_field(spec, "machine_mode", "machine", path, diagnostics)',
        "return tfmg_vat(dict(spec), dummy_uid)",
        "card_type == TFMG_VAT_CARD_TYPE and key.startswith(\"results\")",
        'for forbidden in ("pressure", "heat_level")',
    )
    for token in required_managed:
        require(token in managed, f"managed validator is missing {token!r}", failures)

    try:
        module = _load_compiler(root / COMPILER)
        fixture = {
            "id": "industrial_colonies:validation/tfmg_vat",
            "phase": "validation",
            "comment": "Validate Chemical Vat visual compilation",
            "type": "tfmg_vat",
            "inputs": [
                {"kind": "ITEM", "id": "tfmg:sulfur_dust", "count": 3},
                {"kind": "ITEM_TAG", "id": "c:dusts/nitrate"},
                {"kind": "FLUID", "id": "minecraft:water", "amount": 1000},
                {"kind": "FLUID_TAG", "id": "c:water", "amount": 250},
            ],
            "outputs": [
                {"kind": "ITEM", "id": "tfmg:rubber_sheet", "count": 2, "chance": 0.5},
                {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 500},
            ],
            "vat": "both",
            "machine": "two_electrodes",
            "heat": "heated",
            "min_size": 2,
            "processing_time": 160,
        }
        card = module.tfmg_vat(fixture, "00000000-0000-0000-0000-000000000000")
        require(card.get("type") == "industrial_colonies:tfmg_chemical_vat", "compiler card type drifted", failures)
        require(
            list(card.get("slots", {}))
            == ["ingredients0", "ingredients1", "ingredients2", "ingredients3", "results0", "results1"],
            "compiler Chemical Vat slot keys/order drifted",
            failures,
        )
        require(
            card.get("params")
            == {
                "vatMode": "both",
                "machineMode": "two_electrodes",
                "heat": "heated",
                "minSize": "2",
                "processingTime": "160",
            },
            "compiler Chemical Vat params drifted",
            failures,
        )
    except (ImportError, KeyError, TypeError, ValueError) as exc:
        failures.append(f"managed compiler cannot emit the Chemical Vat fixture: {exc}")


def validate_tfmg_jar(mods: Path, failures: list[str]) -> None:
    expected = mods / TFMG_JAR_NAME
    candidates = sorted(mods.glob("tfmg-*.jar"))
    require(
        candidates == [expected],
        f"TFMG API must be exactly {TFMG_JAR_NAME}; found {[path.name for path in candidates]}",
        failures,
    )
    if candidates != [expected]:
        return
    try:
        with zipfile.ZipFile(expected) as archive:
            for entry, digest in TFMG_CLASSES.items():
                bytecode = archive.read(entry)
                actual = hashlib.sha256(bytecode).hexdigest().upper()
                require(actual == digest, f"TFMG 1.2.0 Vat bytecode drifted: {entry} -> {actual}", failures)
            params = archive.read("com/drmangotea/tfmg/recipes/VatRecipeParams.class")
            for marker in (b"min_size", b"machines", b"allowed_vat_types", b"heat_level"):
                require(marker in params, f"TFMG Vat API lost bytecode marker {marker!r}", failures)
            require(b"pressure" not in params, "TFMG 1.2.0 Vat API unexpectedly exposes pressure", failures)

            sulfuric = json.loads(archive.read(STOCK_RECIPES[0]))
            aluminum = json.loads(archive.read(STOCK_RECIPES[1]))
            for name, payload in (("sulfuric_acid", sulfuric), ("aluminum", aluminum)):
                require(payload.get("type") == "tfmg:vat_machine_recipe", f"stock {name} Vat type drifted", failures)
                require(isinstance(payload.get("ingredients"), list), f"stock {name} lost ingredients", failures)
                require(isinstance(payload.get("results"), list), f"stock {name} lost results", failures)
            water = sulfuric.get("ingredients", [])[-1]
            require(
                water == {"type": "neoforge:single", "amount": 1000, "fluid": "minecraft:water"},
                "stock TFMG fluid-ingredient codec shape drifted",
                failures,
            )
            require(
                sulfuric.get("machines") == ["tfmg:mixing"],
                "stock TFMG mixing machine ID drifted",
                failures,
            )
            require(
                aluminum.get("machines") == ["tfmg:electrode", "tfmg:electrode"],
                "stock TFMG two-electrode machine contract drifted",
                failures,
            )
            require(
                aluminum.get("allowed_vat_types")
                == ["tfmg:steel_vat", "tfmg:firebrick_lined_vat"],
                "stock TFMG allowed vat IDs/order drifted",
                failures,
            )
            require(aluminum.get("heat_requirement") == "heated", "stock TFMG heat field drifted", failures)
    except (OSError, KeyError, IndexError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect pinned TFMG Vat API: {exc}")


def validate_project_jar(project_jar: Path, layout: dict[str, Any] | None, failures: list[str]) -> None:
    if not project_jar.is_file():
        failures.append(f"candidate project JAR is missing: {project_jar}")
        return
    try:
        with zipfile.ZipFile(project_jar) as archive:
            names = set(archive.namelist())
            missing = sorted(set(PROJECT_JAR_ENTRIES) - names)
            require(not missing, f"candidate JAR lacks Chemical Vat entries: {missing}", failures)
            if missing:
                return
            packed_layout = json.loads(archive.read(PROJECT_JAR_ENTRIES[0]))
            require(packed_layout == layout, "candidate JAR Chemical Vat layout is stale", failures)
            integration = archive.read(PROJECT_JAR_ENTRIES[1])
            require(
                b"industrial_colonies:tfmg_chemical_vat" in integration
                and b"TfmgChemicalVatCodegen" in integration,
                "candidate JAR lacks Chemical Vat codegen registration markers",
                failures,
            )
            codegen = archive.read(PROJECT_JAR_ENTRIES[2])
            markers = (
                b"tfmg:vat_machine_recipe",
                b"ingredients",
                b"results",
                b"allowed_vat_types",
                b"machines",
                b"min_size",
                b"processing_time",
                b"heat_requirement",
                b"neoforge:single",
                b"neoforge:tag",
                b"tfmg:steel_vat",
                b"tfmg:firebrick_lined_vat",
                b"tfmg:mixing",
                b"tfmg:electrode",
                b" }).id(",
            )
            for marker in markers:
                require(marker in codegen, f"candidate Vat codegen lacks marker {marker!r}", failures)
            require(b"pressure" not in codegen, "candidate Vat codegen exposes pressure", failures)
    except (OSError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect candidate Chemical Vat JAR: {exc}")


def validate(root: Path, *, mods: Path, project_jar: Path) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        require((root / relative).is_file(), f"required Chemical Vat file is missing: {relative}", failures)
    if failures:
        return failures
    layout = validate_layout(root, failures)
    validate_source(root, failures)
    validate_tfmg_jar(mods, failures)
    validate_project_jar(project_jar, layout, failures)
    return failures


def newest_project_jar(root: Path) -> Path:
    candidates = sorted((root / "build/libs").glob("industrial_colonies-*.jar"))
    return candidates[-1] if candidates else root / "build/libs/industrial_colonies-missing.jar"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument(
        "--mods",
        type=Path,
        default=Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods"),
    )
    parser.add_argument("--project-jar", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    project_jar = args.project_jar.resolve() if args.project_jar else newest_project_jar(project)
    failures = validate(project, mods=args.mods.resolve(), project_jar=project_jar)
    if failures:
        print(f"FAIL: {len(failures)} KJSGen TFMG Chemical Vat issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print(
        "PASS: KJSGen exposes the pinned TFMG 1.2.0 Chemical Vat layout/codegen, "
        "the managed compiler emits matching editable cards, and the candidate JAR "
        "contains the exact no-pressure implementation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
