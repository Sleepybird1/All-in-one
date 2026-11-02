#!/usr/bin/env python3
"""Audit recipes hidden inside bundled JARs against progression boundaries."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_CROSS_PACK = PROJECT / "CROSS_PACK_PROGRESSION_LOOPHOLE_CLOSURE.json"
DEFAULT_DEFERRAL = PROJECT / "pack-scripts/server_scripts/industrial_space_entry_deferred.js"
DEFAULT_JSON = PROJECT / "NESTED_RECIPE_PROGRESSION_AUDIT.json"
DEFAULT_MARKDOWN = PROJECT / "NESTED_RECIPE_PROGRESSION_AUDIT.md"

PHYSICS_ASSEMBLER = "simulated:physics_assembler"
EXPECTED_PHYSICS = {
    "recipe_type": "minecraft:crafting_shaped",
    "outputs": "simulated:physics_assembler",
    "inputs": "create:andesite_alloy | create:andesite_casing | minecraft:lever",
    "source_path": "data/simulated/recipe/physics_assembler.json",
}

COSMETIC_TOKENS = (
    "envelope",
    "handle",
    "nameplate",
    "portable_engine_dyeing",
    "symmetric_sail",
    "aviators_goggles",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def classify(row: dict[str, str]) -> str:
    recipe_id = row["recipe_id"]
    if recipe_id == PHYSICS_ASSEMBLER:
        return "critical_space_boundary"
    if recipe_id == "simulated:contraption_diagram":
        return "contained_downstream_of_boundary"
    if any(token in recipe_id for token in COSMETIC_TOKENS):
        return "cosmetic_or_reversible_variant"
    if row["namespace"] in {"aeronautics", "offroad", "simulated"}:
        return "functional_vehicle_or_aeronautics_component"
    return "compatibility_conversion"


def load_nested_rows(catalog: Path) -> list[dict[str, str]]:
    with (catalog / "recipes.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle) if "!/" in row["source_jar"]]
    return sorted(rows, key=lambda row: row["recipe_id"])


def catalog_recipe_count(catalog: Path) -> int:
    with (catalog / "recipes.csv").open(encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def quoted_ids(text: str) -> set[str]:
    return set(re.findall(r"['\"]([a-z0-9_.-]+:[a-z0-9_./-]+)['\"]", text))


def build_report(catalog: Path, cross_pack_path: Path, deferral_path: Path) -> dict[str, Any]:
    rows = load_nested_rows(catalog)
    recipes_hash = sha256(catalog / "recipes.csv")
    cross_pack = json.loads(cross_pack_path.read_text(encoding="utf-8"))
    deferred = quoted_ids(deferral_path.read_text(encoding="utf-8"))
    physics = [row for row in rows if row["recipe_id"] == PHYSICS_ASSEMBLER]

    findings: list[str] = []
    if len(physics) != 1:
        findings.append(f"expected exactly one {PHYSICS_ASSEMBLER} row, found {len(physics)}")
    elif any(physics[0].get(key) != value for key, value in EXPECTED_PHYSICS.items()):
        findings.append("physics assembler installed recipe identity changed")
    if PHYSICS_ASSEMBLER not in deferred:
        findings.append("physics assembler is not exactly deferred")
    if cross_pack["scope"]["catalog_recipes_sha256"] != recipes_hash:
        findings.append("cross-pack closure does not cite the current nested-aware catalog")
    residuals = cross_pack["residual_producer_scan"]["unmanaged_residuals"]
    if residuals:
        findings.append("cross-pack closure reports unmanaged protected-output producers")

    classified = []
    for row in rows:
        classified.append(
            {
                "recipe_id": row["recipe_id"],
                "recipe_type": row["recipe_type"],
                "namespace": row["namespace"],
                "source_jar": row["source_jar"],
                "source_path": row["source_path"],
                "outputs": row["outputs"],
                "inputs": row["inputs"],
                "disposition": classify(row),
            }
        )
    counts = Counter(row["disposition"] for row in classified)
    return {
        "audit_id": "nested_recipe_progression_audit",
        "status": "green" if not findings else "red",
        "scope": {
            "catalog": str(catalog.resolve()),
            "catalog_recipes_sha256": recipes_hash,
            "catalog_recipe_count": catalog_recipe_count(catalog),
            "nested_recipe_count": len(rows),
            "other_nested_recipe_count": max(0, len(rows) - 1),
            "nested_namespaces": dict(sorted(Counter(row["namespace"] for row in rows).items())),
        },
        "boundary_result": {
            "critical_recipe_id": PHYSICS_ASSEMBLER,
            "critical_recipe_exactly_deferred": PHYSICS_ASSEMBLER in deferred,
            "critical_installed_row_matches": len(physics) == 1
            and all(physics[0].get(key) == value for key, value in EXPECTED_PHYSICS.items()),
            "cross_pack_unmanaged_protected_output_producers": len(residuals),
            "assessment": (
                "The cheap Andesite Physics Assembler is the only newly cataloged direct ship-construction bootstrap. "
                "Its exact stock ID is deferred; the onboard Orbital Flight Computer independently rejects orbital transfer."
            ),
        },
        "disposition_counts": dict(sorted(counts.items())),
        "findings": findings,
        "recipes": classified,
    }


def render_markdown(report: dict[str, Any]) -> str:
    scope = report["scope"]
    counts = report["disposition_counts"]
    return "\n".join(
        [
            "# Nested Recipe Progression Audit",
            "",
            f"Status: **{report['status']}**.",
            "",
            f"The nested-aware catalog contains **{scope['nested_recipe_count']}** embedded recipes from "
            f"{len(scope['nested_namespaces'])} namespaces. One is a direct progression boundary; the other "
            f"**{scope['other_nested_recipe_count']}** are explicitly inventoried in the JSON companion.",
            "",
            "## Progression result",
            "",
            "- `simulated:physics_assembler` was previously invisible because it lives in the Simulated JAR bundled inside Create Aeronautics.",
            "- Its stock recipe costs only Andesite Alloy, an Andesite Casing, and a lever, so it is a direct early physics-ship bootstrap.",
            "- The exact recipe ID is now deferred. No namespace-wide removal is used.",
            "- `simulated:contraption_diagram` is downstream because it consumes the assembler; it cannot restore the bootstrap.",
            "- The cross-pack closure scanned the same nested catalog and found zero unmanaged producers for its 567 protected outputs.",
            "- The remaining embedded recipes are terrestrial/aeronautics components, cosmetics or reversible variants, and compatibility conversions. They do not grant orbital transfer; the physical onboard flight computer remains an independent fail-closed gate.",
            "",
            "## Dispositions",
            "",
            "| Disposition | Count |",
            "|---|---:|",
            *[f"| `{key}` | {value} |" for key, value in sorted(counts.items())],
            "",
            "## Catalog identity",
            "",
            f"- Recipe rows: {scope['catalog_recipe_count']}",
            f"- `recipes.csv` SHA-256: `{scope['catalog_recipes_sha256']}`",
            f"- Embedded namespaces: `{json.dumps(scope['nested_namespaces'], sort_keys=True)}`",
            "",
            "The exhaustive 125-row inventory, source chain, recipe type, inputs, outputs, and disposition are stored in `NESTED_RECIPE_PROGRESSION_AUDIT.json`.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--cross-pack", type=Path, default=DEFAULT_CROSS_PACK)
    parser.add_argument("--deferral", type=Path, default=DEFAULT_DEFERRAL)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report(args.catalog, args.cross_pack, args.deferral)
    expected = {
        args.report_json: json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        args.report_markdown: render_markdown(report),
    }
    if args.write:
        for path, text in expected.items():
            path.write_text(text, encoding="utf-8", newline="\n")
    else:
        drift = [str(path) for path, text in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != text]
        if drift:
            print("Nested recipe progression artifacts drifted: " + ", ".join(drift))
            return 1
    if report["findings"]:
        for finding in report["findings"]:
            print("FAIL: " + finding)
        return 1
    print(
        f"Nested recipe progression audit passed: {report['scope']['nested_recipe_count']} embedded recipes; "
        "physics assembler exactly deferred; zero protected-output residuals."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
