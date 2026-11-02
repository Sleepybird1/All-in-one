#!/usr/bin/env python3
"""Build the implemented Mekanism nuclear chemistry and SPS redesign batch.

The builder reads only released project state, the installed recipe catalog,
and installed mod JARs. It writes only this batch's audit, plan, and historical
applied-patch artifacts. It never edits the shared recipe seed, assignments,
generated artifacts, quests, deployment/live files, or Draw.io.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from collections import OrderedDict
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_MODS = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods")
DEFAULT_PLAN = PROJECT / "MEKANISM_NUCLEAR_CHEMICAL_SPS_AUDIT.plan.json"
DEFAULT_PATCH = PROJECT / "MEKANISM_NUCLEAR_CHEMICAL_SPS_AUDIT.patch.json"
DEFAULT_MARKDOWN = PROJECT / "MEKANISM_NUCLEAR_CHEMICAL_SPS_AUDIT.md"
SEED = PROJECT / "progression/managed_recipe_overhaul.seed.json"
ASSIGNMENTS = PROJECT / "progression/machine_node_assignments.json"
CURRENT_MANAGED = PROJECT / "build-current-audit/managed.json"
AUTOMATIC_AUDIT = PROJECT / "AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json"
SULFUR_SCRIPT = PROJECT / "pack-scripts/server_scripts/industrial_sulfur_canonicalization.js"
URANIUM_SCRIPT = PROJECT / "pack-scripts/server_scripts/industrial_uranium_yellorium_separation.js"
CHEMISTRY_VALIDATOR = PROJECT / "tools/validate_nuclear_chemistry_boundaries.py"
REBASED_BASE_FILES = {
    "progression/managed_recipe_overhaul.seed.json":
        "0C02CC3AF93E25F0A820D018A152C52385CBA4868958F65D91AC2409BBCD942C",
    "progression/machine_node_assignments.json":
        "329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E",
}
NUCLEAR_IMPLEMENTATION_SEED_SHA256 = (
    "F4A369A4E0A2508356A563415D54B3E86C2F2FCA9516F80329730BFE85D76C9B"
)

BATCH_ID = "mekanism_nuclear_chemical_and_sps"
BATCH_OUTPUTS = (
    "mekanism:antiprotonic_nucleosynthesizer",
    "mekanism:chemical_crystallizer",
    "mekanism:chemical_dissolution_chamber",
    "mekanism:chemical_injection_chamber",
    "mekanism:chemical_washer",
    "mekanism:isotopic_centrifuge",
    "mekanism:purification_chamber",
    "mekanism:radioactive_waste_barrel",
    "mekanism:solar_neutron_activator",
    "mekanism:sps_casing",
    "mekanism:sps_port",
    "mekanism:supercharged_coil",
)

SOURCE_REMOVALS = {output: (output,) for output in BATCH_OUTPUTS}

# These definitions may remain in an older catalog after their source add-on is
# removed, or disappear from a freshly rebuilt catalog. The builder checks both
# the catalog and current mods directory and proposes an exact removal only if
# the defining JAR is actually installed.
CHAIN_BYPASS_CANDIDATES = (
    "create_mekanism_improvements:pollonium_pellet",
    "create_mekanism_improvements:antimatter_pellet",
)

# All The Compressed adds a reversible 9-pellet storage block. Its decompression
# recipe is a second direct producer in the catalog, but it cannot bootstrap
# antimatter because the paired compression recipe consumes the same nine
# pellets. Keep both definitions as audited utility closures rather than
# misclassifying decompression as an SPS bypass.
ANTIMATTER_STORAGE_RECOVERY_RECIPES = (
    "allthecompressed:compress/antimatter_block",
    "allthecompressed:decompress/antimatter_block",
)

AUTO_OWNERS = {
    output: f"industrial_colonies:auto/{output.replace(':', '/', 1)}"
    for output in BATCH_OUTPUTS
}

ASSIGNMENT_BY_OUTPUT = {
    "mekanism:antiprotonic_nucleosynthesizer": "CR01 \u2014 The Nuclear Age",
    "mekanism:chemical_crystallizer": "CR01 \u2014 Chemical Separation",
    "mekanism:chemical_dissolution_chamber": "CR01 \u2014 Chemical Separation",
    "mekanism:chemical_injection_chamber": "CR01 \u2014 Chemical Separation",
    "mekanism:chemical_washer": "CR01 \u2014 Chemical Separation",
    "mekanism:isotopic_centrifuge": "CR01 \u2014 Uranium Processing",
    "mekanism:purification_chamber": "CR01 \u2014 Chemical Separation",
    "mekanism:radioactive_waste_barrel": "CR01 \u2014 Actinide Chemistry",
    "mekanism:solar_neutron_activator": "CR01 \u2014 Actinide Chemistry",
    "mekanism:sps_casing": "CR01 \u2014 The Nuclear Age",
    "mekanism:sps_port": "CR01 \u2014 The Nuclear Age",
    "mekanism:supercharged_coil": "CR01 \u2014 The Nuclear Age",
}
PHASE_BY_OUTPUT = {output: "Nuclear Engineering" for output in BATCH_OUTPUTS}

PREREQUISITE_OWNER_IDS = OrderedDict(
    (
        ("mekanism:enrichment_chamber", "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber"),
        ("mekanism:chemical_infuser", "industrial_colonies:mekanism_pre_nuclear/chemical_infuser"),
        ("mekanism:advanced_control_circuit", "industrial_colonies:mekanism/advanced_control_circuit"),
        ("mekanism:elite_control_circuit", "industrial_colonies:mekanism/elite_control_circuit"),
        ("mekanism:ultimate_control_circuit", "industrial_colonies:mekanism/ultimate_control_circuit"),
        ("tfmg:steel_chemical_vat", "industrial_colonies:fluid_infrastructure/steel_chemical_vat"),
        ("tfmg:transformer", "industrial_colonies:tfmg_heavy_electrical/transformer"),
        ("tfmg:centrifuge", "industrial_colonies:tfmg_heavy_electrical/centrifuge"),
        ("ae2:engineering_processor", "industrial_colonies:ae2/engineering_processor"),
    )
)

STOCK_PREREQUISITE_RECIPE_IDS = (
    "mekanism:chemical_tank/basic",
    "mekanism:fluid_tank/basic",
    "mekanism:laser",
    "mekanism:enriching/hdpe_sheet",
    "mekanism:processing/lategame/plutonium_pellet/from_reaction",
    "mekanism:processing/lategame/polonium",
    "mekanism:processing/lategame/polonium_pellet/from_reaction",
    "mekanism:processing/lategame/antimatter_pellet/from_gas",
    "mekanism:processing/uranium/fissile_fuel",
    "tfmg:vat_machine_recipe/sulfuric_acid",
)

CHEMICAL_OUTPUTS = (
    "mekanism:purification_chamber",
    "mekanism:chemical_injection_chamber",
    "mekanism:chemical_dissolution_chamber",
    "mekanism:chemical_washer",
    "mekanism:chemical_crystallizer",
    "mekanism:isotopic_centrifuge",
)
ACTINIDE_OUTPUTS = (
    "mekanism:radioactive_waste_barrel",
    "mekanism:solar_neutron_activator",
)
SPS_OUTPUTS = (
    "mekanism:sps_casing",
    "mekanism:sps_port",
    "mekanism:supercharged_coil",
    "mekanism:antiprotonic_nucleosynthesizer",
)

NUCLEAR_OR_REVERSE_BOOTSTRAP_INPUTS = {
    "mekanism:raw_uranium",
    "mekanism:ingot_uranium",
    "mekanism:dust_uranium",
    "mekanism:yellow_cake_uranium",
    "mekanism:uranium_oxide",
    "mekanism:uranium_hexafluoride",
    "mekanism:fissile_fuel",
    "mekanism:nuclear_waste",
    "mekanism:spent_nuclear_waste",
    "mekanism:plutonium",
    "mekanism:polonium",
    "mekanism:antimatter",
    "mekanism:pellet_plutonium",
    "mekanism:pellet_polonium",
    "mekanism:pellet_antimatter",
    "bigreactors:yellorium_ingot",
    "industrial_colonies:yellorium_compound",
}

ACID_REFS = {
    "tfmg:sulfuric_acid",
    "tfmg:sulfuric_acid_bucket",
    "mekanism:sulfuric_acid",
    "mekanism:sulfuric_acid_bucket",
    "#c:sulfuric_acid",
    "#c:buckets/sulfuric_acid",
}

SULFUR_REQUIRED_TOKENS = (
    "mekanism:chemical_conversion/sulfur_to_sulfuric_acid",
    "mekanism:chemical_infusing/sulfuric_acid",
    "mekanism:rotary/sulfuric_acid",
    "industrial_colonies:sulfur/tfmg_acid_rotary_bridge",
    "industrial_colonies:sulfur/migrate_mekanism_acid",
)
URANIUM_REQUIRED_TOKENS = (
    "create_mekanism_improvements:uranium_ingot",
    "industrial_colonies:materials/uranium/raw_from_yellorium_compound",
    "industrial_colonies:materials/uranium/osmium_compressed_ingot",
    "industrial_colonies:yellorium_compound",
    "mekanism:raw_uranium",
    "mekanism:yellow_cake_uranium",
)


def output_id_from_ref(value: str) -> str:
    parts = value.split("x ", 1)
    return parts[1] if len(parts) == 2 and parts[0].isdigit() else value


def compacting(
    identity: str,
    output: str,
    order: int,
    machine_family: str,
    inputs: list[str],
    comment: str,
    *,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    normalized = output_id_from_ref(output)
    return {
        "id": identity,
        "node": ASSIGNMENT_BY_OUTPUT[normalized],
        "phase": PHASE_BY_OUTPUT[normalized],
        "order": order,
        "type": "compacting",
        "comment": comment,
        "machine": f"createcasing:{machine_family}_press",
        "inputs": inputs,
        "output": output,
        "remove": list(SOURCE_REMOVALS[normalized]),
        "exclusive_output": True,
        "depends_on": depends_on or [],
    }


def sequence(
    identity: str,
    output: str,
    order: int,
    carrier: str,
    machine_family: str,
    ingredients: list[str],
    comment: str,
    *,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    normalized = output_id_from_ref(output)
    deployer = f"createcasing:{machine_family}_deployer"
    press = f"createcasing:{machine_family}_press"
    steps = [
        {"op": "deploying", "ingredient": ingredient, "machine": deployer}
        for ingredient in ingredients
    ]
    steps.append({"op": "pressing", "machine": press})
    return {
        "id": identity,
        "node": ASSIGNMENT_BY_OUTPUT[normalized],
        "phase": PHASE_BY_OUTPUT[normalized],
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": carrier,
        "transitional": carrier,
        "loops": 1,
        "steps": steps,
        "output": output,
        "remove": list(SOURCE_REMOVALS[normalized]),
        "exclusive_output": True,
        "depends_on": depends_on or [],
    }


PROPOSALS: tuple[dict[str, Any], ...] = (
    sequence(
        "industrial_colonies:mekanism_nuclear/purification_chamber",
        "mekanism:purification_chamber",
        400,
        "mekanism:enrichment_chamber",
        "industrial_iron",
        [
            "mekanism:advanced_control_circuit",
            "tfmg:circuit_board",
            "mekanism:ingot_osmium",
            "tfmg:steel_chemical_vat",
            "tfmg:steel_pipe",
        ],
        "Upgrade a fresh Enrichment Chamber with osmium wetted surfaces, a TFMG pressure vat and manifold, and dedicated process control for oxygen purification.",
        depends_on=[
            "industrial_colonies:mekanism_pre_nuclear/enrichment_chamber",
            "industrial_colonies:mekanism/advanced_control_circuit",
            "industrial_colonies:fluid_infrastructure/steel_chemical_vat",
        ],
    ),
    sequence(
        "industrial_colonies:mekanism_nuclear/chemical_injection_chamber",
        "mekanism:chemical_injection_chamber",
        410,
        "mekanism:purification_chamber",
        "industrial_iron",
        [
            "mekanism:elite_control_circuit",
            "tfmg:circuit_board",
            "mekanism:basic_chemical_tank",
            "tfmg:steel_chemical_vat",
            "tfmg:steel_pipe",
        ],
        "Convert a fresh Purification Chamber into a metered injection line with a chemical reservoir, pressure vat, manifold, and elite controller.",
        depends_on=[
            "industrial_colonies:mekanism_nuclear/purification_chamber",
            "industrial_colonies:mekanism/elite_control_circuit",
        ],
    ),
    compacting(
        "industrial_colonies:mekanism_nuclear/chemical_dissolution_chamber",
        "mekanism:chemical_dissolution_chamber",
        420,
        "industrial_iron",
        [
            "tfmg:steel_frame",
            "2x mekanism:basic_chemical_tank",
            "tfmg:steel_chemical_vat",
            "create:mechanical_pump",
            "2x tfmg:steel_pipe",
            "tfmg:transformer",
            "mekanism:ultimate_control_circuit",
            "ae2:engineering_processor",
        ],
        "Press a dual-feed acid dissolution body from a TFMG vat, pumped steel manifold, isolated transformer, and high-energy instrumentation.",
        depends_on=[
            "industrial_colonies:mekanism_pre_nuclear/chemical_infuser",
            "industrial_colonies:fluid_infrastructure/steel_chemical_vat",
            "industrial_colonies:mechanical/mechanical_pump",
            "industrial_colonies:tfmg_heavy_electrical/transformer",
            "industrial_colonies:mekanism/ultimate_control_circuit",
            "industrial_colonies:ae2/engineering_processor",
        ],
    ),
    compacting(
        "industrial_colonies:mekanism_nuclear/chemical_washer",
        "mekanism:chemical_washer",
        430,
        "industrial_iron",
        [
            "tfmg:steel_frame",
            "mekanism:basic_fluid_tank",
            "mekanism:basic_chemical_tank",
            "tfmg:steel_chemical_vat",
            "tfmg:steel_fluid_tank",
            "create:mechanical_pump",
            "tfmg:steel_pipe",
            "mekanism:ultimate_control_circuit",
        ],
        "Build the slurry washer as separate fluid and chemical reservoirs feeding a TFMG vat through a controlled pump and steel manifold.",
        depends_on=[
            "industrial_colonies:mekanism_nuclear/chemical_dissolution_chamber",
            "industrial_colonies:fluid_infrastructure/steel_fluid_tank",
            "industrial_colonies:mekanism/ultimate_control_circuit",
        ],
    ),
    sequence(
        "industrial_colonies:mekanism_nuclear/chemical_crystallizer",
        "mekanism:chemical_crystallizer",
        440,
        "tfmg:steel_frame",
        "industrial_iron",
        [
            "tfmg:steel_chemical_vat",
            "mekanism:basic_chemical_tank",
            "mekanism:fluorite_gem",
            "mekanism:ingot_refined_obsidian",
            "mekanism:ultimate_control_circuit",
        ],
        "Line a controlled TFMG crystallization vessel with fluorite and refined obsidian, then close it in the Industrial-Iron pressure press.",
        depends_on=[
            "industrial_colonies:mekanism_nuclear/chemical_washer",
            "industrial_colonies:mekanism/ultimate_control_circuit",
        ],
    ),
    sequence(
        "industrial_colonies:mekanism_nuclear/isotopic_centrifuge",
        "mekanism:isotopic_centrifuge",
        450,
        "tfmg:centrifuge",
        "refined_radiance",
        [
            "mekanism:basic_chemical_tank",
            "mekanism:ultimate_control_circuit",
            "ae2:engineering_processor",
            "tfmg:transformer",
            "tfmg:steel_casing",
        ],
        "Instrument a proven TFMG centrifuge with sealed chemical storage, ultimate control, engineering telemetry, and isolated nuclear power conditioning.",
        depends_on=[
            "industrial_colonies:tfmg_heavy_electrical/centrifuge",
            "industrial_colonies:mekanism_pre_nuclear/chemical_infuser",
            "industrial_colonies:mekanism/ultimate_control_circuit",
            "industrial_colonies:ae2/engineering_processor",
            "industrial_colonies:tfmg_heavy_electrical/transformer",
        ],
    ),
    compacting(
        "industrial_colonies:mekanism_nuclear/radioactive_waste_barrel_batch",
        "2x mekanism:radioactive_waste_barrel",
        460,
        "industrial_iron",
        [
            "tfmg:steel_fluid_tank",
            "tfmg:fireproof_chemical_vat",
            "4x mekanism:ingot_lead",
            "2x tfmg:heavy_plate",
            "2x tfmg:steel_pipe",
            "tfmg:steel_casing",
        ],
        "Press a fireproof inner vessel, lead shielding, heavy shell, and sealed service pipe into a practical two-barrel waste-handling batch.",
        depends_on=[
            "industrial_colonies:fluid_infrastructure/steel_fluid_tank",
            "industrial_colonies:fluid_infrastructure/fireproof_chemical_vat",
        ],
    ),
    sequence(
        "industrial_colonies:mekanism_nuclear/solar_neutron_activator",
        "mekanism:solar_neutron_activator",
        470,
        "tfmg:steel_frame",
        "refined_radiance",
        [
            "mekanism:hdpe_sheet",
            "tfmg:steel_chemical_vat",
            "tfmg:transformer",
            "ae2:engineering_processor",
            "mekanism:ultimate_control_circuit",
        ],
        "Fit a radiation-tolerant HDPE process window, TFMG vat and transformer, and high-energy instrumentation before radiant final closure.",
        depends_on=[
            "industrial_colonies:mekanism_nuclear/radioactive_waste_barrel_batch",
            "industrial_colonies:mekanism/ultimate_control_circuit",
            "industrial_colonies:ae2/engineering_processor",
        ],
    ),
    compacting(
        "industrial_colonies:mekanism_nuclear/sps_casing_batch",
        "4x mekanism:sps_casing",
        480,
        "refined_radiance",
        [
            "4x mekanism:hdpe_sheet",
            "3x mekanism:pellet_polonium",
            "mekanism:pellet_plutonium",
            "2x tfmg:heavy_plate",
            "tfmg:steel_casing",
            "tfmg:transformer",
            "ae2:engineering_processor",
        ],
        "Press reactor-derived polonium and plutonium into four repeatable SPS frame segments with HDPE insulation and a transformer-backed TFMG shell.",
        depends_on=[
            "industrial_colonies:mekanism_nuclear/solar_neutron_activator",
            "industrial_colonies:mekanism_nuclear/isotopic_centrifuge",
            "industrial_colonies:tfmg_heavy_electrical/transformer",
        ],
    ),
    sequence(
        "industrial_colonies:mekanism_nuclear/sps_port",
        "mekanism:sps_port",
        490,
        "mekanism:sps_casing",
        "refined_radiance",
        [
            "mekanism:ultimate_control_circuit",
            "ae2:engineering_processor",
            "tfmg:circuit_board",
            "tfmg:transformer",
            "tfmg:copper_wire",
        ],
        "Instrument one SPS casing with ultimate control, engineering telemetry, TFMG signal electronics, and isolated power entry.",
        depends_on=[
            "industrial_colonies:mekanism_nuclear/sps_casing_batch",
            "industrial_colonies:mekanism/ultimate_control_circuit",
        ],
    ),
    compacting(
        "industrial_colonies:mekanism_nuclear/supercharged_coil",
        "mekanism:supercharged_coil",
        500,
        "refined_radiance",
        [
            "mekanism:laser",
            "mekanism:sps_casing",
            "2x mekanism:pellet_polonium",
            "mekanism:ultimate_control_circuit",
            "ae2:engineering_processor",
            "tfmg:transformer",
            "tfmg:copper_wire",
            "tfmg:capacitor_item",
        ],
        "Integrate a laser and SPS frame with polonium, buffered TFMG power conditioning, and ultimate beam-control instrumentation.",
        depends_on=[
            "industrial_colonies:mekanism_nuclear/sps_casing_batch",
            "industrial_colonies:mekanism/ultimate_control_circuit",
        ],
    ),
    sequence(
        "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer",
        "mekanism:antiprotonic_nucleosynthesizer",
        510,
        "tfmg:steel_frame",
        "refined_radiance",
        [
            "mekanism:sps_port",
            "mekanism:supercharged_coil",
            "mekanism:pellet_antimatter",
            "mekanism:ultimate_control_circuit",
            "tfmg:transformer",
        ],
        "Close an SPS-qualified port, supercharged injection coil, and first SPS-produced antimatter pellet into the final nucleosynthesis instrument.",
        depends_on=[
            "industrial_colonies:mekanism_nuclear/sps_port",
            "industrial_colonies:mekanism_nuclear/supercharged_coil",
            "industrial_colonies:mekanism/ultimate_control_circuit",
        ],
    ),
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def output_id(recipe: dict[str, Any]) -> str:
    output = recipe.get("output")
    if isinstance(output, str):
        return output_id_from_ref(output)
    if isinstance(output, dict) and isinstance(output.get("id"), str):
        return output["id"]
    return ""


def split_refs(value: str) -> set[str]:
    return {part.strip() for part in value.split("|") if part.strip()}


def recipe_inputs(recipe: dict[str, Any]) -> list[str]:
    if recipe.get("type") == "compacting":
        return list(recipe.get("inputs", []))
    values = [recipe.get("input", "")]
    values.extend(
        step["ingredient"]
        for step in recipe.get("steps", [])
        if step.get("op") == "deploying" and isinstance(step.get("ingredient"), str)
    )
    return [value for value in values if value]


def source_evidence(
    recipe_id: str,
    rows_by_id: dict[str, dict[str, str]],
    mods: Path,
    jar_hashes: dict[str, str],
    *,
    require_source: bool = True,
) -> dict[str, Any]:
    row = rows_by_id.get(recipe_id)
    if row is None:
        if require_source:
            raise ValueError(f"catalog is missing installed recipe {recipe_id}")
        return {
            "id": recipe_id,
            "recipe_type": None,
            "source_jar": None,
            "source_path": None,
            "source_present": False,
            "source_sha256": None,
            "catalog_outputs": [],
            "catalog_inputs": [],
            "raw_type": None,
            "raw_recipe": None,
        }
    jar = mods / row["source_jar"]
    if not jar.is_file():
        if require_source:
            raise ValueError(f"installed source JAR is missing: {jar}")
        return {
            "id": recipe_id,
            "recipe_type": row["recipe_type"],
            "source_jar": row["source_jar"],
            "source_path": row["source_path"],
            "source_present": False,
            "source_sha256": None,
            "catalog_outputs": sorted(split_refs(row["outputs"])),
            "catalog_inputs": sorted(split_refs(row["inputs"])),
            "raw_type": None,
            "raw_recipe": None,
        }
    jar_hashes.setdefault(jar.name, digest_path(jar))
    with zipfile.ZipFile(jar) as archive:
        raw = archive.read(row["source_path"])
    document = json.loads(raw)
    return {
        "id": recipe_id,
        "recipe_type": row["recipe_type"],
        "source_jar": row["source_jar"],
        "source_path": row["source_path"],
        "source_present": True,
        "source_sha256": digest_bytes(raw),
        "catalog_outputs": sorted(split_refs(row["outputs"])),
        "catalog_inputs": sorted(split_refs(row["inputs"])),
        "raw_type": document.get("type"),
        "raw_recipe": document,
    }


def find_assignment_nodes(assignments: dict[str, Any], output: str) -> list[str]:
    return sorted(
        name
        for name, value in assignments.get("nodes", {}).items()
        if isinstance(value, dict) and output in value.get("unlocks", [])
    )


def find_owner(recipes: list[dict[str, Any]], output: str) -> dict[str, Any] | None:
    for recipe in recipes:
        if isinstance(recipe, dict) and output_id(recipe) == output:
            return recipe
    return None


def prerequisite_evidence(seed: dict[str, Any]) -> list[dict[str, Any]]:
    recipes = [row for row in seed.get("recipes", []) if isinstance(row, dict)]
    result: list[dict[str, Any]] = []
    for output, expected_id in PREREQUISITE_OWNER_IDS.items():
        owner = find_owner(recipes, output)
        result.append(
            {
                "output": output,
                "expected_managed_owner": expected_id,
                "observed_managed_owner": owner.get("id") if owner else None,
                "phase": owner.get("phase") if owner else None,
                "order": owner.get("order") if owner else None,
            }
        )
    return result


def scan_non_recipe_occurrences(mods: Path) -> tuple[int, list[dict[str, str]]]:
    """Classify target references outside recipes and descriptive/index data."""

    occurrences: list[dict[str, str]] = []
    jar_count = 0
    for jar in sorted(mods.glob("*.jar"), key=lambda path: path.name.lower()):
        try:
            with zipfile.ZipFile(jar) as archive:
                jar_count += 1
                for path in archive.namelist():
                    lower = path.lower()
                    if not lower.endswith(".json"):
                        continue
                    if lower.startswith("assets/"):
                        continue
                    if any(
                        marker in lower
                        for marker in (
                            "/recipe/",
                            "/recipes/",
                            "/advancement/",
                            "/advancements/",
                            "/model/",
                            "/models/",
                            "/lang/",
                            "/tag/",
                            "/tags/",
                        )
                    ):
                        continue
                    try:
                        text = archive.read(path).decode("utf-8")
                    except (KeyError, UnicodeDecodeError):
                        continue
                    for target in BATCH_OUTPUTS:
                        if target not in text:
                            continue
                        namespace, item = target.split(":", 1)
                        expected = f"data/{namespace}/loot_table/blocks/{item}.json"
                        role = (
                            "self_drop_block_loot"
                            if path == expected
                            else "external_acquisition_candidate"
                        )
                        occurrences.append(
                            {
                                "source_jar": jar.name,
                                "source_path": path,
                                "target": target,
                                "role": role,
                            }
                        )
        except zipfile.BadZipFile:
            continue
    return jar_count, sorted(
        occurrences,
        key=lambda row: (row["target"], row["source_jar"], row["source_path"]),
    )


def build_documents(catalog: Path, mods: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    rows = load_rows(catalog / "recipes.csv")
    rows_by_id = {row["recipe_id"]: row for row in rows}
    seed = load_json(SEED)
    assignments = load_json(ASSIGNMENTS)
    current = load_json(CURRENT_MANAGED)
    automatic = load_json(AUTOMATIC_AUDIT)
    batch = next(
        row
        for row in automatic.get("implementation_batches", [])
        if row.get("id") == BATCH_ID
    )

    jar_hashes: dict[str, str] = {}
    installed_removal_ids = [
        identity for output in BATCH_OUTPUTS for identity in SOURCE_REMOVALS[output]
    ]
    removed_evidence = [
        source_evidence(identity, rows_by_id, mods, jar_hashes)
        for identity in installed_removal_ids
    ]
    bypass_evidence = []
    for identity in CHAIN_BYPASS_CANDIDATES:
        evidence = source_evidence(
            identity, rows_by_id, mods, jar_hashes, require_source=False
        )
        bypass_evidence.append(
            {
                **evidence,
                "catalog_present": identity in rows_by_id,
                "disposition": (
                    "exact_remove"
                    if evidence["source_present"]
                    else "inactive_catalog_only_no_patch"
                    if identity in rows_by_id
                    else "absent_from_catalog_no_patch"
                ),
                "reason": (
                    "bypasses reactor waste and Solar Neutron Activator"
                    if "pollonium" in identity
                    else "creates Antimatter Pellet without an operational SPS"
                ),
            }
        )
    active_bypass_removals = [
        row["id"] for row in bypass_evidence if row["source_present"]
    ]
    stock_prerequisite_evidence = [
        source_evidence(identity, rows_by_id, mods, jar_hashes)
        for identity in STOCK_PREREQUISITE_RECIPE_IDS
    ]
    antimatter_storage_recovery_evidence = [
        source_evidence(identity, rows_by_id, mods, jar_hashes)
        for identity in ANTIMATTER_STORAGE_RECOVERY_RECIPES
    ]

    producers_by_output = OrderedDict(
        (
            output,
            sorted(
                row["recipe_id"]
                for row in rows
                if output in split_refs(row["outputs"])
            ),
        )
        for output in BATCH_OUTPUTS
    )
    sensitive_catalog_producers = OrderedDict(
        (
            output,
            sorted(
                row["recipe_id"]
                for row in rows
                if output in split_refs(row["outputs"])
            ),
        )
        for output in ("mekanism:pellet_polonium", "mekanism:pellet_antimatter")
    )
    sensitive_active_producers = OrderedDict(
        (
            output,
            [
                identity
                for identity in identities
                if (mods / rows_by_id[identity]["source_jar"]).is_file()
            ],
        )
        for output, identities in sensitive_catalog_producers.items()
    )

    seed_recipes = [row for row in seed.get("recipes", []) if isinstance(row, dict)]
    seed_owner_by_output = {output_id(row): row.get("id") for row in seed_recipes}
    downstream_rows = sorted(
        (
            row
            for row in rows
            if split_refs(row["inputs"]).intersection(BATCH_OUTPUTS)
        ),
        key=lambda row: row["recipe_id"],
    )
    downstream_evidence: list[dict[str, Any]] = []
    for row in downstream_rows:
        identity = row["recipe_id"]
        outputs = sorted(split_refs(row["outputs"]))
        downstream_evidence.append(
            {
                **source_evidence(identity, rows_by_id, mods, jar_hashes),
                "role": (
                    "same_batch_replaced"
                    if identity in installed_removal_ids
                    else "shared_seed_managed_closure"
                    if any(output in seed_owner_by_output for output in outputs)
                    else "downstream_not_owned_by_batch"
                ),
                "observed_shared_seed_owner": next(
                    (seed_owner_by_output[output] for output in outputs if output in seed_owner_by_output),
                    None,
                ),
            }
        )

    jar_count, occurrences = scan_non_recipe_occurrences(mods)
    for occurrence in occurrences:
        jar = mods / occurrence["source_jar"]
        jar_hashes.setdefault(jar.name, digest_path(jar))

    current_by_output = {
        output_id(recipe): recipe
        for recipe in current.get("recipes", [])
        if isinstance(recipe, dict) and output_id(recipe) in BATCH_OUTPUTS
    }
    current_auto = [
        {
            "output": output,
            "id": current_by_output.get(output, {}).get("id"),
            "phase": current_by_output.get(output, {}).get("phase"),
            "type": current_by_output.get(output, {}).get("type"),
            "remove": current_by_output.get(output, {}).get("remove", []),
        }
        for output in BATCH_OUTPUTS
    ]
    assignment_snapshot = [
        {
            "output": output,
            "required_node": ASSIGNMENT_BY_OUTPUT[output],
            "required_phase": PHASE_BY_OUTPUT[output],
            "current_nodes": find_assignment_nodes(assignments, output),
            "patch_action": "none",
        }
        for output in BATCH_OUTPUTS
    ]

    proposal_copy = json.loads(json.dumps(PROPOSALS))
    plan: dict[str, Any] = {
        "schema_version": 1,
        "status": "implemented_in_seed",
        "batch_id": BATCH_ID,
        "priority": 6,
        "audited_on": "2026-08-31",
        "scope": {
            "catalog": str(catalog),
            "catalog_recipes_sha256": digest_path(catalog / "recipes.csv"),
            "mods_directory": str(mods),
            "installed_jar_sha256": OrderedDict(sorted(jar_hashes.items())),
            "installed_jars_scanned_for_non_recipe_acquisition": jar_count,
            "seed": str(SEED.relative_to(PROJECT)).replace("\\", "/"),
            "seed_sha256": NUCLEAR_IMPLEMENTATION_SEED_SHA256,
            "assignments": str(ASSIGNMENTS.relative_to(PROJECT)).replace("\\", "/"),
            "assignments_sha256": digest_path(ASSIGNMENTS),
            "current_managed_snapshot": str(CURRENT_MANAGED.relative_to(PROJECT)).replace("\\", "/"),
            "current_managed_sha256": digest_path(CURRENT_MANAGED),
            "sulfur_canonicalization": str(SULFUR_SCRIPT.relative_to(PROJECT)).replace("\\", "/"),
            "sulfur_canonicalization_sha256": digest_path(SULFUR_SCRIPT),
            "uranium_boundary": str(URANIUM_SCRIPT.relative_to(PROJECT)).replace("\\", "/"),
            "uranium_boundary_sha256": digest_path(URANIUM_SCRIPT),
            "chemistry_validator": str(CHEMISTRY_VALIDATOR.relative_to(PROJECT)).replace("\\", "/"),
            "chemistry_validator_sha256": digest_path(CHEMISTRY_VALIDATOR),
        },
        "decision": {
            "replace_exactly_12_outputs": list(BATCH_OUTPUTS),
            "manufacturing_philosophy": "TFMG-first Industrial-Iron chemical pressure equipment followed by Refined-Radiance nuclear instrumentation",
            "all_targets_remain_phase": "Nuclear Engineering",
            "exact_chain_bypass_removals": active_bypass_removals,
            "sulfuric_acid_synthesis_owner": "tfmg:vat_machine_recipe/sulfuric_acid",
            "approved_acid_phase_bridge": "industrial_colonies:sulfur/tfmg_acid_rotary_bridge",
            "assignment_changes": 0,
            "shared_files_modified": True,
        },
        "automatic_audit_contract": {
            key: batch.get(key)
            for key in (
                "outputs",
                "prerequisite_outputs",
                "recommended_environments",
                "cycle_risks",
                "managed_ids",
                "installed_recipe_ids",
            )
        },
        "direct_producer_audit": producers_by_output,
        "removed_installed_recipes": removed_evidence,
        "chain_bypass_audit": {
            "sensitive_catalog_producers": sensitive_catalog_producers,
            "sensitive_active_producers_before_exact_removals": sensitive_active_producers,
            "candidates": bypass_evidence,
            "exact_active_removals": active_bypass_removals,
            "antimatter_storage_recovery_closure": antimatter_storage_recovery_evidence,
            "active_survivors_after_exact_removals": {
                output: [
                    identity
                    for identity in identities
                    if identity not in active_bypass_removals
                ]
                for output, identities in sensitive_active_producers.items()
            },
        },
        "stock_processing_prerequisites": stock_prerequisite_evidence,
        "downstream_consumer_audit": downstream_evidence,
        "non_recipe_acquisition_audit": {
            "occurrences": occurrences,
            "external_acquisition_candidates": [
                row for row in occurrences if row["role"] == "external_acquisition_candidate"
            ],
            "finding": "Only ordinary self-drop block loot is accepted; any external loot, trade, or structure occurrence fails validation.",
        },
        "canonical_chemistry_boundary": {
            "sulfur_required_tokens": list(SULFUR_REQUIRED_TOKENS),
            "uranium_required_tokens": list(URANIUM_REQUIRED_TOKENS),
            "forward_route": [
                "industrial_colonies:yellorium_compound",
                "mekanism:raw_uranium",
                "mekanism:dust_uranium",
                "mekanism:ingot_uranium",
                "mekanism:yellow_cake_uranium",
                "mekanism:uranium_oxide",
                "mekanism:uranium_hexafluoride",
                "mekanism:fissile_fuel",
                "mekanism:nuclear_waste",
                "mekanism:polonium",
                "mekanism:pellet_polonium",
                "mekanism:sps_casing",
                "mekanism:sps_port",
                "mekanism:supercharged_coil",
                "mekanism:antimatter",
                "mekanism:pellet_antimatter",
                "mekanism:antiprotonic_nucleosynthesizer",
            ],
            "construction_recipe_acid_refs": sorted(
                {
                    output_id_from_ref(value)
                    for recipe in proposal_copy
                    for value in recipe_inputs(recipe)
                    if output_id_from_ref(value) in ACID_REFS
                }
            ),
            "existing_full_validator_command": "python tools/validate_nuclear_chemistry_boundaries.py 'C:\\Users\\GodPC\\curseforge\\minecraft\\Instances\\All in one' --project .",
        },
        "prerequisite_evidence": prerequisite_evidence(seed),
        "replacement_contracts": proposal_copy,
        "assignment_contract": assignment_snapshot,
        "dependency_contract": {
            "chemical_groups": {
                "purification_upgrade": [
                    "mekanism:enrichment_chamber",
                    "mekanism:purification_chamber",
                    "mekanism:chemical_injection_chamber",
                ],
                "slurry_separation": [
                    "mekanism:chemical_dissolution_chamber",
                    "mekanism:chemical_washer",
                    "mekanism:chemical_crystallizer",
                ],
                "fissile_fuel": [
                    "mekanism:chemical_infuser",
                    "mekanism:isotopic_centrifuge",
                ],
            },
            "sps_order": list(SPS_OUTPUTS),
            "sps_casing_batch_size": 4,
            "waste_barrel_batch_size": 2,
            "forbidden_early_construction_inputs": sorted(NUCLEAR_OR_REVERSE_BOOTSTRAP_INPUTS),
            "acid_refs_forbidden_in_machine_construction": sorted(ACID_REFS),
            "mek_data_outputs_are_fresh_empty": [
                source["catalog_outputs"][0]
                for source in removed_evidence
                if source["raw_type"] == "mekanism:mek_data"
            ],
        },
        "current_managed_state": {
            "replaced_automatic_owners": current_auto,
            "expected_retired_ids_after_rebuild": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
        },
        "implementation": {
            "status": "source_owned",
            "authoritative_source": "progression/managed_recipe_overhaul.seed.json",
            "source_recipe_count": 12,
            "source_recipe_ids": [recipe["id"] for recipe in proposal_copy],
            "exact_stock_recipe_removals": len(installed_removal_ids) + len(active_bypass_removals),
            "active_bypass_removals": active_bypass_removals,
            "automatic_owners_retired_on_rebuild": 12,
            "assignment_changes": 0,
            "authoritative_generated_artifacts": "intentionally_not_regenerated_by_batch_owner",
            "rebased_base_files": REBASED_BASE_FILES,
        },
        "integration_boundary": {
            "seed_edit_applied": True,
            "assignment_edit_required": False,
            "generated_output_edit_authorized": False,
            "quest_edit_authorized": False,
            "deploy_or_live_edit_authorized": False,
            "drawio_edit_authorized": False,
        },
    }

    all_exact_removals = installed_removal_ids + active_bypass_removals
    patch: dict[str, Any] = {
        "schema_version": 1,
        "status": "applied_to_authoritative_seed",
        "batch_id": BATCH_ID,
        "base_files": REBASED_BASE_FILES,
        "preconditions": {
            "explicit_seed_owners_for_outputs": 0,
            "exact_outputs": list(BATCH_OUTPUTS),
            "exact_current_auto_owners": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
            "required_prerequisite_managed_ids": list(PREREQUISITE_OWNER_IDS.values()),
            "exact_installed_bypass_recipe_ids": active_bypass_removals,
        },
        "seed_operations": [
            {
                "op": "append_recipe_specs_after_output_ownership_assertion",
                "recipes": proposal_copy,
            },
        ] + (
            [{"op": "union_additional_removals_exact_ids", "recipe_ids": active_bypass_removals}]
            if active_bypass_removals
            else []
        ),
        "assignment_operations": [],
        "assignment_assertions": assignment_snapshot,
        "expected_rebuild_effects": {
            "retire_automatic_managed_ids": [AUTO_OWNERS[output] for output in BATCH_OUTPUTS],
            "compile_exact_managed_ids": [recipe["id"] for recipe in proposal_copy],
            "remove_exact_installed_recipe_ids": all_exact_removals,
            "preserve_recipe_ids_added": [],
        },
        "deferred_actions": [
            "Rebuild managed manifests/KJSGen only in the parent integration workflow.",
            "Run the full nuclear chemistry boundary validator and runtime JEI exact-machine acceptance after integration.",
        ],
    }
    return plan, patch, render_markdown(plan, patch)


def format_inputs(recipe: dict[str, Any]) -> str:
    return "<br>".join(f"`{value}`" for value in recipe_inputs(recipe))


def format_machine(recipe: dict[str, Any]) -> str:
    if recipe["type"] == "compacting":
        return f"`{recipe['machine']}`"
    machines: list[str] = []
    for step in recipe["steps"]:
        if step["machine"] not in machines:
            machines.append(step["machine"])
    return " \u2192 ".join(f"`{machine}`" for machine in machines)


def render_markdown(plan: dict[str, Any], patch: dict[str, Any]) -> str:
    lines = [
        "# Mekanism Nuclear Chemistry and SPS audit",
        "",
        "Status: **implemented in the authoritative seed**. The twelve reviewed contracts are source-owned and assignments were intentionally unchanged. Generated/live, quest, deployment, and Draw.io files were not edited by this batch.",
        "",
        "## Outcome",
        "",
        "The twelve remaining automatic-owned nuclear outputs become three coherent physical lines: Industrial-Iron pressure equipment for ore chemistry, Refined-Radiance instrumentation for fissile/actinide work, and an SPS frame/port/coil chain that must run before antimatter equipment.",
        "",
        "The design retains the existing Yellorium-to-uranium boundary. None of the first eight machine-construction contracts consumes uranium, fissile fuel, reactor waste, polonium, plutonium, antimatter, or sulfuric acid. SPS casing is the first construction contract allowed to consume reactor-derived actinides; the nucleosynthesizer is the only one allowed to consume an Antimatter Pellet.",
        "",
        "## Exact replacement contracts",
        "",
        "| Order | Output / managed ID | Existing node | Process | Physical inputs | Exact stock removal |",
        "|---:|---|---|---|---|---|",
    ]
    for recipe in sorted(plan["replacement_contracts"], key=lambda row: row["order"]):
        lines.append(
            f"| {recipe['order']} | `{recipe['output']}`<br>`{recipe['id']}` | {recipe['node']}<br>{recipe['phase']} | `{recipe['type']}`<br>{format_machine(recipe)} | {format_inputs(recipe)} | `{recipe['remove'][0]}` |"
        )
    lines.extend(
        [
            "",
            "All sequences run one pass and end in their casing-specific press. Compacting uses six to eight recognizable components. There are no generic 5x5 A/B gate rings.",
            "",
            "The two-output waste-barrel contract supports practical decay arrays; the four-output SPS casing contract supports a large multiblock without repeating a one-block craft dozens of times.",
            "",
            "## Forward dependency shape",
            "",
            "- Purification physically upgrades a fresh Enrichment Chamber; Injection physically upgrades a fresh Purification Chamber.",
            "- Dissolution, Washing, and Crystallization are ordered as a slurry-processing line but do not consume one another, because all three machines must coexist in the running factory.",
            "- The Isotopic Centrifuge upgrades the earlier TFMG Centrifuge and requires the already-reviewed Chemical Infuser, Ultimate Control Circuit, Engineering Processor, and Transformer. It does not require fissile fuel or a reactor product to construct.",
            "- Waste barrels precede the Solar Neutron Activator. The activator has no polonium input, so it can create the first legitimate polonium from reactor waste.",
            "- SPS casing consumes reactor-derived polonium and plutonium; both SPS port and supercharged coil physically consume an SPS casing.",
            "- The Antiprotonic Nucleosynthesizer physically consumes an SPS port, a supercharged coil, and an Antimatter Pellet, proving an operational SPS path before nucleosynthesis.",
            "",
            "## Bypass audit",
            "",
            "The two known Create Mekanism Improvements mixing bypass candidates are classified against both the current catalog and mods directory. An active definition is removed exactly; an inactive or catalog-absent candidate adds no removal operation:",
            "",
        ]
    )
    for source in plan["chain_bypass_audit"]["candidates"]:
        location = (
            f"`{source['source_jar']}` / `{source['source_path']}`"
            if source["catalog_present"]
            else "absent from the current catalog"
        )
        lines.append(
            f"- `{source['id']}` ({location}): {source['reason']}; disposition `{source['disposition']}`."
        )
    lines.extend(
        [
            "",
            "In the active pack, the sole Polonium Pellet route is Mekanism PRC processing of Solar-Neutron-Activator polonium, and the sole Antimatter Pellet manufacturing route is crystallization of SPS-produced antimatter. All The Compressed may recover nine pellets from its Antimatter Block, but the paired block recipe consumes those same nine pellets, so this is a lossless storage closure rather than a bootstrap. The already-existing uranium boundary separately retires `create_mekanism_improvements:uranium_ingot` if that compatibility definition is present.",
            "",
            "## Sulfuric acid and uranium boundaries",
            "",
            "No construction recipe in this batch synthesizes or consumes sulfuric acid. The sole active JAR synthesis remains `tfmg:vat_machine_recipe/sulfuric_acid`; `industrial_colonies:sulfur/tfmg_acid_rotary_bridge` remains the approved TFMG-fluid to Mekanism-chemical phase conversion, not a second synthesis route.",
            "",
            "The canonical forward fuel route remains: manufactured Yellorium compound -> raw uranium in the Enrichment Chamber -> uranium dust -> Osmium Compressor ingot -> Yellow Cake -> uranium oxide -> UF6 -> Isotopic Centrifuge fissile fuel. No proposed input points backward into Yellorium, and no pre-SPS recipe consumes an actinide or antimatter product.",
            "",
            "## Producer, acquisition, and downstream audit",
            "",
            "Each of the twelve target outputs has exactly one active installed recipe producer. Those twelve exact IDs are the complete active removal set implemented by this batch. Catalog rows whose source JAR is absent are never mislabeled as active producers.",
            "",
            "All installed JARs were scanned outside recipe and descriptive data. Ordinary self-drop block loot is classified as non-acquisition; any external loot, trade, or structure occurrence is a validation failure.",
            "",
            "Downstream consumers are classified rather than silently removed: the Injecting and Purifying factory closures are already owned in the shared seed, same-batch Injection/SPS Port sources are replaced here, and MEGA Cells' radioactive component remains outside this batch.",
            "",
            "## State-transfer rule",
            "",
            "Five stock sources use `mekanism:mek_data`: Purification, Injection, Dissolution, Washing, and the Isotopic Centrifuge. Create encased processing cannot merge Mekanism component data. Their replacements therefore create fresh, empty, unsecured, unupgraded machines; carrier machines/tanks used in upgrades must also be fresh and empty.",
            "",
            "## Assignment and integration boundary",
            "",
            "All twelve outputs already appear exactly once in their current nodes and all map to Nuclear Engineering. No assignment edit was needed. The historical patch locks the released AE2 seed and assignment hashes and records the twelve source-owned recipe specs. It added no global removal in the current installed-mod state.",
            "",
            "## Validation",
            "",
            "```powershell",
            "python tools/build_mekanism_nuclear_chemical_sps_audit.py --check",
            "python tools/validate_mekanism_nuclear_chemical_sps_audit.py",
            "python tools/test_validate_mekanism_nuclear_chemical_sps_audit.py",
            "python tools/validate_nuclear_chemistry_boundaries.py 'C:\\Users\\GodPC\\curseforge\\minecraft\\Instances\\All in one' --project .",
            "```",
            "",
            "Validation locks source JSON/JAR hashes, producer coverage, exact removals, non-recipe acquisition evidence, concrete item identities, machine environments, sequence moderation, dependency acyclicity, uranium/acid boundaries, SPS order, managed prerequisites, assignment parity, current automatic-owner retirement, patch parity, and deterministic regeneration.",
            "",
        ]
    )
    return "\n".join(lines)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    plan, patch, markdown = build_documents(args.catalog, args.mods)
    expected = {
        args.plan: json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
        args.patch: json.dumps(patch, indent=2, ensure_ascii=False) + "\n",
        args.markdown: markdown,
    }
    if args.check:
        drift = [
            str(path)
            for path, text in expected.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != text
        ]
        if drift:
            print("Mekanism nuclear chemistry/SPS artifacts drifted:")
            for path in drift:
                print(f"- {path}")
            return 1
        print("Mekanism nuclear chemistry/SPS artifacts are deterministic and current.")
        return 0
    write_json(args.plan, plan)
    write_json(args.patch, patch)
    args.markdown.write_text(markdown, encoding="utf-8")
    print(f"Wrote {args.plan}")
    print(f"Wrote {args.patch}")
    print(f"Wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
