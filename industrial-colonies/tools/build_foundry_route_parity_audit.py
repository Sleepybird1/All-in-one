#!/usr/bin/env python3
"""Build the reviewed TFMG-gated foundry endpoint redesign."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_PLAN = PROJECT / "FOUNDRY_ROUTE_PARITY_AUDIT.plan.json"
DEFAULT_PATCH = PROJECT / "FOUNDRY_ROUTE_PARITY_AUDIT.patch.json"
DEFAULT_MARKDOWN = PROJECT / "FOUNDRY_ROUTE_PARITY_AUDIT.md"
AUTOMATIC_AUDIT = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"

CANDIDATE_OUTPUTS = (
    "createmetallurgy:casting_basin",
    "createmetallurgy:casting_table",
    "createmetallurgy:foundry_basin",
    "createmetallurgy:foundry_lid",
    "createmetallurgy:foundry_mixer",
    "modernfoundry:scorched_basin",
    "modernfoundry:scorched_drain",
    "modernfoundry:scorched_table",
)

STOCK_RECIPE_IDS: dict[str, tuple[str, ...]] = {
    "createmetallurgy:casting_basin": ("createmetallurgy:crafting/content/casting_basin",),
    "createmetallurgy:casting_table": ("createmetallurgy:crafting/content/casting_table",),
    "createmetallurgy:foundry_basin": ("createmetallurgy:crafting/content/foundry_basin",),
    "createmetallurgy:foundry_lid": ("createmetallurgy:crafting/content/foundry_lid",),
    "createmetallurgy:foundry_mixer": ("createmetallurgy:crafting/content/foundry_mixer",),
    "modernfoundry:scorched_basin": ("modernfoundry:smeltery/scorched/basin",),
    "modernfoundry:scorched_drain": (
        "modernfoundry:smeltery/scorched/drain",
        "modernfoundry:smeltery/scorched/drain_retextured",
    ),
    "modernfoundry:scorched_table": ("modernfoundry:smeltery/scorched/table",),
}

AUTOMATIC_OWNER_IDS = {
    output: f"industrial_colonies:auto/{output.replace(':', '/', 1)}"
    for output in CANDIDATE_OUTPUTS
}

ASSIGNMENT_BY_OUTPUT = {
    "createmetallurgy:casting_basin": "CR01 — Advanced Metallurgy",
    "createmetallurgy:casting_table": "CR01 — Advanced Metallurgy",
    "createmetallurgy:foundry_basin": "CR01 — Advanced Alloy Mixing",
    "createmetallurgy:foundry_lid": "CR01 — Advanced Alloy Mixing",
    "createmetallurgy:foundry_mixer": "CR01 — Advanced Alloy Mixing",
    "modernfoundry:scorched_basin": "CR01 — Exotic Metallurgy",
    "modernfoundry:scorched_drain": "CR01 — Exotic Metallurgy",
    "modernfoundry:scorched_table": "CR01 — Exotic Metallurgy",
}

CREATE_METALLURGY_CORE_TYPES = {
    "createmetallurgy:alloying",
    "createmetallurgy:bulk_melting",
    "createmetallurgy:casting_in_basin",
    "createmetallurgy:casting_in_table",
    "createmetallurgy:melting",
}
CREATE_METALLURGY_FINISHING_TYPES = {
    "createmetallurgy:alloying",
    "createmetallurgy:casting_in_basin",
    "createmetallurgy:casting_in_table",
}

IMPLEMENTATION = {
    "base_seed_sha256": "D34BB136243F77BA8786053F2CD422AB57860D051B90280EE4638144B777A923",
    "implemented_seed_sha256": "FEAFDF1383C840D750AA93D45F17A28DBEEA8E6B8FFDE0C9995177FA0873BAB3",
    "unchanged_assignments_sha256": "329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E",
    "recipes_added": 8,
    "automatic_owners_retired": 8,
    "exact_stock_removals": 9,
    "assignment_changes": 0,
    "subsystems_disabled": 0,
    "isolated_result": {
        "managed_recipes": 329,
        "automatic_recipes": 75,
        "compiled_cards": 397,
        "exact_removals": 661,
        "skipped_assigned_outputs": 33,
        "dag_warnings": 0,
    },
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def split_refs(value: str) -> set[str]:
    result: set[str] = set()
    for token in value.split(" | "):
        token = token.strip()
        if not token:
            continue
        head, separator, tail = token.partition("x ")
        result.add(tail.strip() if separator and head.strip().isdigit() else token)
    return result


def output_id(value: Any) -> str:
    if isinstance(value, str):
        return value.split("x ", 1)[-1].strip()
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return value["id"]
    raise ValueError(f"unsupported output reference: {value!r}")


def compacting(
    identity: str,
    output: str,
    order: int,
    inputs: list[str],
    comment: str,
    depends_on: list[str],
) -> dict[str, Any]:
    return {
        "id": identity,
        "node": ASSIGNMENT_BY_OUTPUT[output],
        "phase": "Steel & Petroleum",
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": "createcasing:industrial_iron_press",
        "inputs": inputs,
        "output": output,
        "remove": list(STOCK_RECIPE_IDS[output]),
        "exclusive_output": True,
        "depends_on": depends_on,
    }


def sequence(
    identity: str,
    output: str,
    order: int,
    input_item: str,
    ingredients: list[str],
    comment: str,
    depends_on: list[str],
) -> dict[str, Any]:
    return {
        "id": identity,
        "node": ASSIGNMENT_BY_OUTPUT[output],
        "phase": "Steel & Petroleum",
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "loops": 1,
        "steps": [
            *[
                {
                    "op": "deploying",
                    "ingredient": ingredient,
                    "machine": "createcasing:industrial_iron_deployer",
                }
                for ingredient in ingredients
            ],
            {"op": "pressing", "machine": "createcasing:industrial_iron_press"},
        ],
        "output": output,
        "remove": list(STOCK_RECIPE_IDS[output]),
        "exclusive_output": True,
        "depends_on": depends_on,
    }


PROPOSALS: tuple[dict[str, Any], ...] = (
    compacting(
        "industrial_colonies:foundry_routes/create_metallurgy_casting_table",
        "createmetallurgy:casting_table",
        120,
        [
            "tfmg:casting_basin",
            "2x tfmg:fireproof_bricks",
            "create:depot",
            "tfmg:cast_iron_ingot",
            "tfmg:screw",
            "createmetallurgy:graphite_ingot_mold",
        ],
        "Rebuild TFMG casting hardware into a refractory graphite-mold table for precision molten-metal forms.",
        ["industrial_colonies:steelworks/fireproof_bricks"],
    ),
    compacting(
        "industrial_colonies:foundry_routes/create_metallurgy_casting_basin",
        "createmetallurgy:casting_basin",
        130,
        [
            "tfmg:casting_basin",
            "2x tfmg:fireproof_bricks",
            "tfmg:cast_iron_frame",
            "tfmg:heavy_plate",
            "tfmg:screw",
        ],
        "Reinforce the TFMG casting basin with a cast-iron frame and refractory lining for block-scale pours.",
        [
            "industrial_colonies:steelworks/fireproof_bricks",
            "industrial_colonies:auto/tfmg/cast_iron_frame",
        ],
    ),
    compacting(
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_basin",
        "createmetallurgy:foundry_basin",
        140,
        [
            "create:basin",
            "4x tfmg:fireproof_bricks",
            "tfmg:cast_iron_frame",
            "tfmg:steel_mechanism",
            "createmetallurgy:refractory_mortar",
        ],
        "Press a refractory lining and TFMG steel drive into a Create basin to withstand continuous melting.",
        [
            "industrial_colonies:steelworks/fireproof_bricks",
            "industrial_colonies:auto/tfmg/cast_iron_frame",
        ],
    ),
    compacting(
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_lid",
        "createmetallurgy:foundry_lid",
        150,
        [
            "4x tfmg:cast_iron_ingot",
            "2x tfmg:fireproof_bricks",
            "tfmg:heavy_plate",
            "tfmg:steel_mechanism",
            "tfmg:screw",
        ],
        "Laminate a sealed heavy lid around a TFMG steel mechanism and fireproof refractory shell.",
        ["industrial_colonies:steelworks/fireproof_bricks"],
    ),
    sequence(
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_mixer",
        "createmetallurgy:foundry_mixer",
        160,
        "tfmg:industrial_mixer",
        [
            "createmetallurgy:sturdy_whisk",
            "create:copper_casing",
            "tfmg:steel_mechanism",
            "tfmg:cast_iron_frame",
        ],
        "Convert a proven TFMG industrial mixer into the refractory kinetic head that owns Create Metallurgy alloying.",
        [
            "industrial_colonies:heavy_industry/industrial_mixer",
            "industrial_colonies:auto/tfmg/cast_iron_frame",
        ],
    ),
    compacting(
        "industrial_colonies:foundry_routes/modern_scorched_basin",
        "modernfoundry:scorched_basin",
        170,
        [
            "createmetallurgy:casting_basin",
            "4x modernfoundry:scorched_brick",
            "modernfoundry:gold_platform",
            "tfmg:heavy_plate",
            "tfmg:steel_mechanism",
        ],
        "Upgrade the refractory block-casting line into Modern Foundry's high-temperature scorched basin.",
        ["industrial_colonies:foundry_routes/create_metallurgy_casting_basin"],
    ),
    compacting(
        "industrial_colonies:foundry_routes/modern_scorched_drain",
        "modernfoundry:scorched_drain",
        180,
        [
            "4x modernfoundry:scorched_brick",
            "2x modernfoundry:obsidian_pane",
            "2x tfmg:steel_pipe",
            "tfmg:steel_fluid_tank",
            "tfmg:screw",
        ],
        "Build the scorched fluid interface around TFMG pressure-rated pipework and a steel buffer tank.",
        [
            "industrial_colonies:fluid_infrastructure/steel_pipe",
            "industrial_colonies:fluid_infrastructure/steel_fluid_tank",
        ],
    ),
    compacting(
        "industrial_colonies:foundry_routes/modern_scorched_table",
        "modernfoundry:scorched_table",
        190,
        [
            "createmetallurgy:casting_table",
            "4x modernfoundry:scorched_brick",
            "modernfoundry:gold_bars",
            "tfmg:heavy_plate",
            "tfmg:screw",
        ],
        "Upgrade the precision casting table with a scorched refractory shell and replaceable gold working rails.",
        ["industrial_colonies:foundry_routes/create_metallurgy_casting_table"],
    ),
)


def is_modern_casting_type(recipe_type: str) -> bool:
    if not recipe_type.startswith("modernfoundry:"):
        return False
    local = recipe_type.split(":", 1)[1]
    return (
        "casting" in local
        or local.startswith("table_")
        or local.startswith("basin_")
        or local == "molding_table"
    )


def route_evidence(rows: list[dict[str, str]]) -> dict[str, Any]:
    output_namespaces: dict[str, set[str]] = {}
    for row in rows:
        for output in split_refs(row.get("outputs", "")):
            output_namespaces.setdefault(output, set()).add(row.get("namespace", ""))
    cm_core = [row for row in rows if row.get("recipe_type") in CREATE_METALLURGY_CORE_TYPES]
    cm_finish = [row for row in rows if row.get("recipe_type") in CREATE_METALLURGY_FINISHING_TYPES]
    cm_outputs = sorted(
        {output for row in cm_finish for output in split_refs(row.get("outputs", ""))}
    )
    cm_exclusive = [
        output
        for output in cm_outputs
        if output_namespaces.get(output, set()) <= {"createmetallurgy"}
    ]
    tfmg = [row for row in rows if row.get("recipe_type") == "tfmg:casting"]
    tfmg_outputs = sorted(
        {output for row in tfmg for output in split_refs(row.get("outputs", ""))}
    )
    modern = [row for row in rows if is_modern_casting_type(row.get("recipe_type", ""))]
    modern_outputs = sorted(
        {output for row in modern for output in split_refs(row.get("outputs", ""))}
    )
    modern_exclusive = [
        output
        for output in modern_outputs
        if output_namespaces.get(output, set()) <= {"modernfoundry"}
    ]
    return {
        "create_metallurgy": {
            "core_route_recipe_count": len(cm_core),
            "core_type_counts": dict(
                sorted(Counter(row["recipe_type"] for row in cm_core).items())
            ),
            "casting_and_alloy_recipe_count": len(cm_finish),
            "casting_and_alloy_output_reference_count": len(cm_outputs),
            "exclusive_output_reference_count": len(cm_exclusive),
            "exclusive_output_reference_examples": cm_exclusive[:24],
        },
        "tfmg": {
            "casting_recipe_count": len(tfmg),
            "casting_outputs": tfmg_outputs,
        },
        "modernfoundry": {
            "table_basin_route_recipe_count": len(modern),
            "route_type_counts": dict(
                sorted(Counter(row["recipe_type"] for row in modern).items())
            ),
            "output_reference_count": len(modern_outputs),
            "exclusive_output_reference_count": len(modern_exclusive),
            "exclusive_output_reference_examples": modern_exclusive[:24],
        },
    }


def build_documents(catalog: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    rows = load_rows(catalog / "recipes.csv")
    by_id = {row["recipe_id"]: row for row in rows}
    automatic = load_json(AUTOMATIC_AUDIT)
    old_entries = {
        row["output"]: row
        for row in automatic.get("entries", [])
        if isinstance(row, dict) and row.get("output") in CANDIDATE_OUTPUTS
    }
    sources = []
    for output in CANDIDATE_OUTPUTS:
        for recipe_id in STOCK_RECIPE_IDS[output]:
            row = by_id[recipe_id]
            sources.append(
                {
                    "output": output,
                    "id": recipe_id,
                    "recipe_type": row["recipe_type"],
                    "source_jar": row["source_jar"],
                    "source_path": row["source_path"],
                    "inputs": sorted(split_refs(row.get("inputs", ""))),
                }
            )
    evidence = route_evidence(rows)
    removals = [
        recipe_id
        for output in CANDIDATE_OUTPUTS
        for recipe_id in STOCK_RECIPE_IDS[output]
    ]
    plan = {
        "schema_version": 1,
        "status": "implemented",
        "batch_id": "foundry_route_parity",
        "audited_on": "2026-08-31",
        "decision": "RETAIN_FUNCTIONAL_FOUNDRIES_WITH_TFMG_GATED_ENDPOINTS",
        "reason": "Route parity failed, so both unique foundry systems stay. Their cheap stock construction recipes are replaced by eight meaningful TFMG-gated Industrial-Iron manufacturing contracts.",
        "implementation": IMPLEMENTATION,
        "candidate_outputs": list(CANDIDATE_OUTPUTS),
        "old_automatic_classification": {
            output: {
                "managed_id": old_entries[output]["managed_id"],
                "classification": old_entries[output]["classification"],
                "disposition": old_entries[output]["disposition"],
            }
            for output in CANDIDATE_OUTPUTS
        },
        "installed_stock_producers": sources,
        "route_evidence": evidence,
        "replacement_contracts": list(PROPOSALS),
        "exact_stock_removals": removals,
        "automatic_managed_ids_to_retire": [
            AUTOMATIC_OWNER_IDS[output] for output in CANDIDATE_OUTPUTS
        ],
        "assignment_edits": [],
        "boundaries": [
            "TFMG remains first: Create Metallurgy casting starts from TFMG casting/refractory hardware, alloying starts from a TFMG industrial mixer, and Modern Foundry endpoints consume the earlier line or TFMG pressure infrastructure.",
            "Existing steel canonicalization keeps TFMG steel as the player-facing solid and removes alternate solid-steel bypasses.",
            "Unique casting, molding, tool-part, alloy, and recycling routes remain available.",
            "No generic 5x5 perimeter ring and no cheap stock endpoint recipe survives.",
        ],
        "primary_project_references": [
            "https://www.curseforge.com/minecraft/mc-mods/create-metallurgy",
            "https://lucreeper74.github.io/CreateMetallurgy-Wiki/developers/kjs-integration/recipes",
            "https://github.com/Modern-Mods/ModernFoundry",
        ],
    }
    patch = {
        "schema_version": 1,
        "status": "implemented",
        "mode": "implemented_historical_patch",
        "batch_id": "foundry_route_parity",
        "decision": plan["decision"],
        "implementation": IMPLEMENTATION,
        "recipes_to_append": list(PROPOSALS),
        "exact_stock_removals": removals,
        "automatic_managed_ids_to_retire": plan[
            "automatic_managed_ids_to_retire"
        ],
        "assignment_edits": [],
    }
    cm = evidence["create_metallurgy"]
    tfmg = evidence["tfmg"]
    modern = evidence["modernfoundry"]
    markdown = f"""# Foundry Route-Parity Audit

Status: **implemented in the authoritative seed**.

## Decision

Keep both foundry systems, but replace the eight generic automatic gate rings with real Industrial-Iron manufacturing. Do not restore the cheap stock endpoint recipes.

TFMG remains first. Create Metallurgy's casting blocks are upgrades of TFMG casting/refractory hardware; its alloy mixer consumes a TFMG industrial mixer. Modern Foundry's scorched endpoints then consume the earlier casting line or TFMG pressure-rated fluid infrastructure.

## Why the subsystems cannot be deleted

| System | Audited functional recipes | Distinct output references | Output references with no producer outside that namespace |
|---|---:|---:|---:|
| Create Metallurgy casting + alloy finishing | {cm['casting_and_alloy_recipe_count']} | {cm['casting_and_alloy_output_reference_count']} | {cm['exclusive_output_reference_count']} |
| Modern Foundry table/basin routes | {modern['table_basin_route_recipe_count']} | {modern['output_reference_count']} | {modern['exclusive_output_reference_count']} |
| TFMG casting | {tfmg['casting_recipe_count']} | {len(tfmg['casting_outputs'])} | n/a |

Create Metallurgy also has **{cm['core_route_recipe_count']}** installed recipes across melting, bulk melting, alloying, and casting. TFMG's **{tfmg['casting_recipe_count']}** casting recipes are canonical for its own industrial line, not replacements for hundreds of unique foundry routes.

## Manufacturing result

- 7 Industrial-Iron compacting recipes.
- 1 Industrial-Iron sequenced assembly, upgrading the TFMG Industrial Mixer into the Create Metallurgy Foundry Mixer.
- 9 exact stock recipe removals.
- 8 automatic gate-ring owners retired.
- 0 assignment edits and 0 subsystem deletions.

This supersedes the tentative `redundant_should_retire` label. Its required parity proof failed, while physical TFMG-first gating remains intact.

## Implemented proof

The authoritative seed adds the eight source-owned contracts without changing assignments. Its post-batch SHA-256 is `{IMPLEMENTATION['implemented_seed_sha256']}`; the unchanged assignments SHA-256 is `{IMPLEMENTATION['unchanged_assignments_sha256']}`. An isolated rebuild produced 329 managed recipes (75 automatic), 397 compiled KJSGen cards, 661 exact removals, 33 intentional skips, and no dependency warning.
"""
    return plan, patch, markdown


def encoded(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    plan, patch, markdown = build_documents(args.catalog.resolve())
    expected = {
        DEFAULT_PLAN: encoded(plan),
        DEFAULT_PATCH: encoded(patch),
        DEFAULT_MARKDOWN: markdown,
    }
    if args.check:
        drifted = [
            str(path)
            for path, text in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        if drifted:
            raise SystemExit("Foundry parity artifacts drifted: " + ", ".join(drifted))
        print("Foundry route-parity redesign artifacts are deterministic and current.")
        return 0
    for path, text in expected.items():
        path.write_text(text, encoding="utf-8", newline="\n")
    print("Wrote reviewed TFMG-gated foundry redesign plan, patch, and audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
