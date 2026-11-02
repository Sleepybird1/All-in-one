#!/usr/bin/env python3
"""Prove the final cross-pack progression-loophole closure contract.

This is deliberately a composite validator.  Mature domain validators remain
authoritative for petroleum, canonical materials, nuclear chemistry, ATM
currency, explicit bypass retirement, and TFMG steelworks.  This layer adds a
catalog-wide residual-producer census across every exclusive seed output plus
the explicitly retired/canonical/currency surfaces.

The command is read-only except when ``--write`` is supplied, in which case it
writes only the two audit artifacts owned by this validator.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


PROJECT = Path(__file__).resolve().parents[1]
TOOLS = PROJECT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_allthemodium_currency as atm_currency
import validate_canonicalization as canonicalization
import validate_progression_bypass_retirement as bypass_retirement


DEFAULT_INSTANCE = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one")
DEFAULT_CATALOG = PROJECT.parents[1] / "outputs" / "recipe-catalog-current"
DEFAULT_JSON = PROJECT / "CROSS_PACK_PROGRESSION_LOOPHOLE_CLOSURE.json"
DEFAULT_MARKDOWN = PROJECT / "CROSS_PACK_PROGRESSION_LOOPHOLE_CLOSURE.md"
SEED = PROJECT / "progression" / "managed_recipe_overhaul.seed.json"
ASSIGNMENTS = PROJECT / "progression" / "machine_node_assignments.json"
MANIFEST = PROJECT / "progression" / "managed_recipe_overhaul.json"
COMPILED = PROJECT / "pack-kjsgen" / "default.managed.json"
POLICIES = TOOLS / "canonicalization_policies.json"
SERVER_SCRIPTS = PROJECT / "pack-scripts" / "server_scripts"
BIG_PLAN = PROJECT / "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.plan.json"
BIG_PATCH = PROJECT / "BIGREACTORS_BULK_STRUCTURES_CONTROLLERS_AUDIT.patch.json"

RETIRED_TECH_RECIPE_IDS = frozenset(
    {
        "mekanism:digital_miner",
        "mekanism:energized_smelter",
        "mekanism:oredictionificator",
        "mekanism:factory/basic/smelting",
        "mekanism:factory/advanced/smelting",
        "mekanism:factory/elite/smelting",
        "mekanism:factory/ultimate/smelting",
        "mekanism:portable_teleporter",
        "mekanism:teleporter",
        "mekanism:qio_dashboard",
        "mekanism:qio_drive_array",
        "mekanism:quantum_entangloporter",
    }
)

RETIRED_TECH_OUTPUTS = frozenset(
    {
        "mekanism:digital_miner",
        "mekanism:energized_smelter",
        "mekanism:oredictionificator",
        "mekanism:basic_smelting_factory",
        "mekanism:advanced_smelting_factory",
        "mekanism:elite_smelting_factory",
        "mekanism:ultimate_smelting_factory",
        "mekanism:portable_teleporter",
        "mekanism:teleporter",
        "mekanism:qio_dashboard",
        "mekanism:qio_drive_array",
        "mekanism:quantum_entangloporter",
    }
)

REQUIRED_CRITICAL_OUTPUTS = frozenset(
    {
        "ae2:printed_silicon",
        "tfmg:steel_ingot",
        "tfmg:steel_nugget",
        "tfmg:steel_block",
        "tfmg:sulfur_dust",
        "tfmg:sulfuric_acid",
        "mekanism:sulfuric_acid",
        "tfmg:diesel",
        "tfmg:gasoline",
        "bigreactors:yellorium_ingot",
        "industrial_colonies:yellorium_compound",
        "mekanism:raw_uranium",
        *RETIRED_TECH_OUTPUTS,
    }
)

# These are closures, recovery paths, or the canonical stock process itself.
# The residual scan rejects every other surviving direct producer.
ALLOWED_STOCK_PRODUCERS_BY_OUTPUT: Mapping[str, frozenset[str]] = {
    # These self-clearing, dye-reset, charge-state, and block/part conversions
    # require the already-manufactured capability.  They cannot bootstrap a
    # protected output, so retaining them preserves normal device usability
    # without reopening an acquisition route.
    "create:factory_gauge": frozenset(
        {"create:crafting/logistics/factory_gauge_clear"}
    ),
    "create:redstone_requester": frozenset(
        {"create:crafting/logistics/redstone_requester_clear"}
    ),
    "create:stock_link": frozenset(
        {"create:crafting/logistics/stock_link_clear"}
    ),
    "create:stock_ticker": frozenset(
        {"create:crafting/logistics/stock_ticker_clear"}
    ),
    "create_connected:kinetic_battery": frozenset(
        {
            "create_connected:crafting/kinetics/kinetic_battery_discharge",
            "create_connected:crafting/kinetics/kinetic_battery_from_charged",
        }
    ),
    "electroenergetics:electrical_panel": frozenset(
        {"electroenergetics:crafting/electrical_panel_undye"}
    ),
    "extendedae:ex_pattern_provider": frozenset(
        {"extendedae:ex_pattern_provider_alt"}
    ),
    "megacells:mega_interface": frozenset(
        {"megacells:network/mega_interface_block"}
    ),
    "bigreactors:yellorium_ingot": frozenset(
        {"bigreactors:crafting/yellorium_storage_to_component"}
    ),
    "mekanism:raw_uranium": frozenset(
        {"mekanism:processing/uranium/raw/from_raw_block"}
    ),
    "tfmg:diesel": frozenset(
        {
            "tfmg:distillation/crude_oil",
            "tfmg:distillation/crude_oil_light_distillation",
            "tfmg:distillation/crude_oil_no_naphtha",
            "tfmg:distillation/heavy_oil",
            "tfmg:distillation/heavy_oil_light_distillation",
            "tfmg:distillation/heavy_oil_no_naphtha",
        }
    ),
    "tfmg:gasoline": frozenset(
        {
            "tfmg:distillation/crude_oil",
            "tfmg:distillation/crude_oil_light_distillation",
            "tfmg:distillation/crude_oil_no_naphtha",
        }
    ),
    "tfmg:steel_block": frozenset(
        {"tfmg:crafting/materials/steel_block_from_compacting"}
    ),
    "tfmg:steel_ingot": frozenset(
        {
            "tfmg:casting/steel",
            "tfmg:crafting/materials/steel_ingot_from_compacting",
            "tfmg:crafting/materials/steel_ingot_from_decompacting",
        }
    ),
    "tfmg:steel_nugget": frozenset(
        {"tfmg:crafting/materials/steel_nugget_from_decompacting"}
    ),
    "tfmg:sulfur_dust": frozenset(
        {"create:crushing/sulfur", "tfmc:sulfur_crushing_recipe"}
    ),
    "tfmg:sulfuric_acid": frozenset(
        {"tfmg:vat_machine_recipe/sulfuric_acid"}
    ),
}

EXPLICIT_CLOSURE_RECIPE_IDS = frozenset(
    {
        "computercraft:wired_modem_full_to",
        "electroenergetics:crafting/connector_from_double",
        "electroenergetics:crafting/connector_from_triple",
        "electroenergetics:crafting/connector_from_quad",
    }
)

CORE_COMPONENTS = (
    (
        "canonical_materials_and_engine_fuels",
        "TFMG petroleum/steel/sulfur canonicalization and CDG fuel registry",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "validate_canonicalization.py"),
            str(instance),
            "--project",
            str(PROJECT),
            "--skip-installed-parity",
        ],
    ),
    (
        "petroleum_engine_progression",
        "TFMG crude, diesel, gasoline, and engine construction",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "validate_petroleum_engine_progression.py"),
            "--mods",
            str(instance / "mods"),
            "--manifest",
            str(MANIFEST),
        ],
    ),
    (
        "nuclear_chemistry_boundaries",
        "Chemical Vat sulfuric acid and forward-only Yellorium/uranium route",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "validate_nuclear_chemistry_boundaries.py"),
            str(instance),
            "--project",
            str(PROJECT),
        ],
    ),
    (
        "allthemodium_currency",
        "manufactured ATM/Vibranium/Unobtainium currency and shortcut retirement",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "validate_allthemodium_currency.py"),
        ],
    ),
    (
        "confirmed_bypass_retirement",
        "Digital Miner, smelting factories, equipment, mines, and teleport bypasses",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "validate_progression_bypass_retirement.py"),
        ],
    ),
    (
        "tfmg_steelworks",
        "canonical coke/hot-blast/industrial-blasting/TFMG casting chain",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "validate_steelworks_manufacturing_audit.py"),
            "--catalog",
            str(catalog),
            "--mods",
            str(instance / "mods"),
            "--manifest",
            str(MANIFEST),
        ],
    ),
)

RELEASE_COMPONENTS = (
    (
        "bigreactors_release_integrity",
        "27 reviewed Big Reactors bulk/controller contracts are present in the released seed",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "validate_bigreactors_bulk_structures_audit.py"),
            "--catalog",
            str(catalog / "recipe_catalog.sqlite"),
            "--mods",
            str(instance / "mods"),
        ],
    ),
    (
        "managed_manifest_freshness",
        "released seed compiles to the committed managed manifest",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "build_managed_recipe_manifest.py"),
            "--catalog",
            str(catalog),
            "--mods",
            str(instance / "mods"),
            "--check",
        ],
    ),
    (
        "compiled_kjsgen_freshness",
        "committed managed manifest compiles to the committed KJSGen project",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "generate_managed_recipe_overhaul.py"),
            "--check",
        ],
    ),
    (
        "managed_overhaul_integrity",
        "committed manifest and KJSGen project remain dependency-consistent",
        lambda instance, catalog: [
            sys.executable,
            str(TOOLS / "validate_managed_recipe_overhaul.py"),
        ],
    ),
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def digest_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def normalized_ref(value: str) -> str:
    value = value.strip()
    parts = value.split("x ", 1)
    return parts[1] if len(parts) == 2 and parts[0].isdigit() else value


def split_refs(value: str) -> set[str]:
    return {normalized_ref(part) for part in value.split("|") if part.strip()}


def output_id(recipe: Mapping[str, Any]) -> str:
    value = recipe.get("output")
    if isinstance(value, str):
        return normalized_ref(value)
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return str(value["id"])
    return ""


def load_catalog_rows(catalog: Path) -> list[dict[str, str]]:
    with (catalog / "recipes.csv").open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def seed_removals(seed: Mapping[str, Any]) -> set[str]:
    removed = {
        str(value)
        for value in seed.get("additional_removals", [])
        if isinstance(value, str)
    }
    for recipe in seed.get("recipes", []):
        if isinstance(recipe, dict):
            removed.update(
                str(value) for value in recipe.get("remove", []) if isinstance(value, str)
            )
    return removed


def currency_contract() -> tuple[set[str], set[str], set[str]]:
    source = atm_currency.SCRIPT.read_text(encoding="utf-8")
    exact = set(
        atm_currency.literal_strings(
            source,
            "const ATM_STOCK_PRODUCER_IDS = [",
            "]\n\nconst ATM_COMPRESSED_FAMILIES",
        )
    )
    exact.update(
        f"allthecompressed:{direction}/{family}_{level}x"
        for direction in ("compress", "decompress")
        for family in atm_currency.COMPRESSED_FAMILIES
        for level in range(1, 10)
    )
    exact.update(
        f"allthemodium:processing/{metal}/{suffix}"
        for metal in atm_currency.METALS
        for suffix in atm_currency.MEKANISM_SUFFIXES
    )
    audit = load_json(atm_currency.AUDIT_JSON)
    protected = {
        str(value)
        for value in audit.get("forms", {}).get("items", [])
        if isinstance(value, str)
    }
    protected.update(
        str(value)
        for value in audit.get("forms", {}).get("compressed_storage_aliases", [])
        if isinstance(value, str)
    )
    inactive = {
        str(recipe.get("recipe_id"))
        for recipe in audit.get("recipes", [])
        if isinstance(recipe, dict)
        and not recipe.get("conditions_active")
        and isinstance(recipe.get("recipe_id"), str)
    }
    return exact, protected, inactive


def protected_outputs(
    seed: Mapping[str, Any], policies: Mapping[str, Any], currency_outputs: set[str]
) -> tuple[set[str], dict[str, int]]:
    exclusive = {
        output_id(recipe)
        for recipe in seed.get("recipes", [])
        if isinstance(recipe, dict) and recipe.get("exclusive_output") is True
    }
    exclusive.discard("")
    deprecated: set[str] = set()
    for group in policies.get("groups", []):
        if isinstance(group, dict):
            deprecated.update(
                str(value)
                for value in group.get("deprecated_outputs", [])
                if isinstance(value, str)
            )
    retired = set(bypass_retirement.NO_MANAGED_PRODUCER_OUTPUTS) | set(
        RETIRED_TECH_OUTPUTS
    )
    critical = set(REQUIRED_CRITICAL_OUTPUTS)
    combined = exclusive | deprecated | retired | currency_outputs | critical
    return combined, {
        "exclusive_seed_outputs": len(exclusive),
        "canonical_deprecated_outputs": len(deprecated),
        "retired_bypass_outputs": len(retired),
        "currency_and_compressed_outputs": len(currency_outputs),
        "required_critical_outputs": len(critical),
        "unique_protected_outputs": len(combined),
    }


def validate_policy_contracts(
    seed: Mapping[str, Any],
    policies: Mapping[str, Any],
    protected: set[str],
    exact_removals: set[str],
) -> list[str]:
    failures: list[str] = []
    missing_critical = sorted(REQUIRED_CRITICAL_OUTPUTS - protected)
    if missing_critical:
        failures.append(f"required critical outputs escaped protection: {missing_critical}")
    missing_retirements = sorted(RETIRED_TECH_RECIPE_IDS - exact_removals)
    if missing_retirements:
        failures.append(f"retired technology recipe IDs are not exactly removed: {missing_retirements}")

    seed_owners: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for recipe in seed.get("recipes", []):
        if isinstance(recipe, dict):
            seed_owners[output_id(recipe)].append(recipe)
    for output in RETIRED_TECH_OUTPUTS:
        if seed_owners.get(output):
            failures.append(f"retired technology regained a managed producer: {output}")

    silicon = seed_owners.get("ae2:printed_silicon", [])
    if len(silicon) != 1:
        failures.append("printed silicon must have exactly one authoritative seed owner")
    else:
        recipe = silicon[0]
        if recipe.get("type") != "compacting" or recipe.get("machine") != "createcasing:brass_press":
            failures.append("printed silicon is not compacted in the Brass press")
        if recipe.get("inputs") != ["tfmg:silicon_ingot", "ae2:silicon_press"]:
            failures.append("printed silicon no longer uses canonical TFMG silicon and the AE2 mold")
        if recipe.get("returned_tool") != "ae2:silicon_press":
            failures.append("printed silicon no longer returns its AE2 mold")
        if recipe.get("remove") != ["ae2:inscriber/silicon_print"]:
            failures.append("printed silicon does not exactly retire the AE2 Inscriber shortcut")
    if "extendedae:cutter/silicon_print" not in exact_removals:
        failures.append("ExtendedAE silicon cutting shortcut is not exactly retired")

    groups = {
        str(group.get("name")): group
        for group in policies.get("groups", [])
        if isinstance(group, dict)
    }
    petroleum = groups.get("petroleum", {})
    if petroleum.get("canonical_tags", {}).get("c:diesel") != [
        "tfmg:diesel",
        "tfmg:flowing_diesel",
    ]:
        failures.append("TFMG diesel canonical-tag contract drifted")
    if petroleum.get("canonical_tags", {}).get("c:gasoline") != [
        "tfmg:gasoline",
        "tfmg:flowing_gasoline",
    ]:
        failures.append("TFMG gasoline canonical-tag contract drifted")
    fuels = petroleum.get("cdg_engine_fuel_policy", {})
    if fuels.get("allowed") != {
        "createdieselgenerators:diesel": "c:diesel",
        "createdieselgenerators:gasoline": "c:gasoline",
    }:
        failures.append("CDG engine canonical fuel allowlist drifted")
    if set(fuels.get("disabled", [])) != {
        "createdieselgenerators:biodiesel",
        "createdieselgenerators:ethanol",
        "createdieselgenerators:plantoil",
    }:
        failures.append("CDG alternate engine-fuel shutdown drifted")

    sulfur = groups.get("sulfur chemistry", {})
    if sulfur.get("canonical_tags", {}).get("c:sulfuric_acid") != [
        "tfmg:sulfuric_acid"
    ]:
        failures.append("TFMG sulfuric-acid canonical fluid contract drifted")
    steel = groups.get("steel solids", {})
    if steel.get("canonical_tags", {}).get("c:ingots/steel") != [
        "tfmg:steel_ingot"
    ]:
        failures.append("TFMG steel canonical ingot contract drifted")
    return failures


def classify_catalog_producers(
    rows: Sequence[Mapping[str, str]],
    mods: Path,
    protected: set[str],
    exact_removals: set[str],
    preserved: set[str],
    inactive_recipe_ids: set[str],
) -> dict[str, Any]:
    classifications: Counter[str] = Counter()
    by_output: dict[str, dict[str, set[str]]] = {
        output: defaultdict(set) for output in protected
    }
    installed_rows = 0
    relevant_rows = 0
    for row in rows:
        source_jar = str(row.get("source_jar", ""))
        if not (mods / source_jar).is_file():
            continue
        installed_rows += 1
        outputs = split_refs(str(row.get("outputs", ""))) & protected
        if not outputs:
            continue
        relevant_rows += 1
        identity = str(row.get("recipe_id", ""))
        recipe_type = str(row.get("recipe_type", ""))
        inputs = split_refs(str(row.get("inputs", "")))
        for output in outputs:
            if identity in inactive_recipe_ids:
                role = "inactive_conditioned_definition"
            elif identity in exact_removals:
                role = "exactly_removed"
            elif identity in preserved:
                role = "explicitly_preserved_closure"
            elif identity in ALLOWED_STOCK_PRODUCERS_BY_OUTPUT.get(output, frozenset()):
                role = "canonical_stock_route"
            elif identity in EXPLICIT_CLOSURE_RECIPE_IDS:
                role = "explicit_downconversion_closure"
            elif recipe_type == "computercraft:impostor_shaped":
                role = "display_only_impostor"
            elif recipe_type == "ae2:storage_cell_disassembly":
                role = "storage_recovery_closure"
            elif recipe_type == "computercraft:transform_shapeless" and output in inputs:
                role = "self_transform_closure"
            else:
                role = "unmanaged_residual"
            by_output[output][role].add(identity)
            classifications[role] += 1

    residual = {
        output: sorted(roles.get("unmanaged_residual", set()))
        for output, roles in by_output.items()
        if roles.get("unmanaged_residual")
    }
    canonical_survivor_drift: dict[str, dict[str, list[str]]] = {}
    for output, expected in ALLOWED_STOCK_PRODUCERS_BY_OUTPUT.items():
        observed = set(by_output.get(output, {}).get("canonical_stock_route", set()))
        if observed != set(expected):
            canonical_survivor_drift[output] = {
                "expected": sorted(expected),
                "observed": sorted(observed),
            }

    evidence = []
    for output in sorted(protected):
        roles = by_output[output]
        if not roles:
            continue
        evidence.append(
            {
                "output": output,
                "roles": OrderedDict(
                    (role, sorted(roles[role])) for role in sorted(roles)
                ),
            }
        )
    return {
        "catalog_rows": len(rows),
        "installed_source_rows": installed_rows,
        "relevant_installed_rows": relevant_rows,
        "protected_outputs_with_installed_producers": sum(bool(value) for value in by_output.values()),
        "classification_counts": OrderedDict(sorted(classifications.items())),
        "unmanaged_residuals": residual,
        "canonical_survivor_drift": canonical_survivor_drift,
        "producer_evidence": evidence,
    }


def component_specs(instance: Path, catalog: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    def make(specs: Iterable[tuple[str, str, Callable[[Path, Path], list[str]]]]) -> list[dict[str, Any]]:
        return [
            {"id": identity, "purpose": purpose, "command": factory(instance, catalog)}
            for identity, purpose, factory in specs
        ]

    return make(CORE_COMPONENTS), make(RELEASE_COMPONENTS)


def execute_components(
    specs: Sequence[Mapping[str, Any]],
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in specs:
        command = [str(value) for value in spec["command"]]
        completed = runner(
            command,
            cwd=PROJECT,
            capture_output=True,
            text=True,
            check=False,
        )
        output = (completed.stdout + completed.stderr).replace("\r\n", "\n").strip()
        results.append(
            {
                "id": spec["id"],
                "purpose": spec["purpose"],
                "command": command,
                "returncode": completed.returncode,
                "output_sha256": digest_text(output),
                "output": output.splitlines(),
            }
        )
    return results


def big_release_gate() -> dict[str, Any]:
    plan = load_json(BIG_PLAN) if BIG_PLAN.is_file() else {}
    patch = load_json(BIG_PATCH) if BIG_PATCH.is_file() else {}
    plan_status = plan.get("status")
    patch_status = patch.get("status")
    implemented = (
        plan_status == "implemented_in_seed"
        and patch_status == "implemented_in_seed"
    )
    return {
        "plan": str(BIG_PLAN.relative_to(PROJECT)).replace("\\", "/"),
        "plan_status": plan_status,
        "patch": str(BIG_PATCH.relative_to(PROJECT)).replace("\\", "/"),
        "patch_status": patch_status,
        "implemented": implemented,
    }


def evaluate_release_status(
    policy_failures: Sequence[str],
    core: Sequence[Mapping[str, Any]],
    release: Sequence[Mapping[str, Any]],
    big_gate: Mapping[str, Any],
) -> tuple[str, list[str]]:
    """Classify hard safety failures separately from release-order blockers."""

    core_failures = [str(row["id"]) for row in core if row.get("returncode") != 0]
    release_pending = [
        str(row["id"]) for row in release if row.get("returncode") != 0
    ]
    blockers = list(policy_failures)
    if core_failures:
        blockers.append(
            "authoritative component validators failed: " + ", ".join(core_failures)
        )
    if not big_gate.get("implemented"):
        blockers.append("Big Reactors reviewed batch is not yet recorded as implemented")
    if release_pending:
        blockers.append(
            "managed/generated release artifacts are stale: "
            + ", ".join(release_pending)
        )

    if policy_failures or core_failures:
        status = "failed"
    elif not big_gate.get("implemented") or release_pending:
        status = "pending_big_integration_or_regeneration"
    else:
        status = "green"
    return status, blockers


def build_report(
    instance: Path = DEFAULT_INSTANCE,
    catalog: Path = DEFAULT_CATALOG,
    *,
    run_components: bool = True,
    core_results: Sequence[Mapping[str, Any]] | None = None,
    release_results: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    seed = load_json(SEED)
    policies = load_json(POLICIES)
    rows = load_catalog_rows(catalog)
    currency_removals, currency_outputs, inactive_currency = currency_contract()
    exact_removals = seed_removals(seed)
    exact_removals.update(canonicalization.parse_removed_recipe_ids(SERVER_SCRIPTS))
    exact_removals.update(currency_removals)
    protected, protected_counts = protected_outputs(seed, policies, currency_outputs)
    preserved = {
        str(value)
        for value in seed.get("preserve_recipe_ids", [])
        if isinstance(value, str)
    }
    scan = classify_catalog_producers(
        rows,
        instance / "mods",
        protected,
        exact_removals,
        preserved,
        inactive_currency,
    )
    policy_failures = validate_policy_contracts(
        seed, policies, protected, exact_removals
    )
    if scan["unmanaged_residuals"]:
        policy_failures.append("catalog-wide residual producer scan found unmanaged survivors")
    if scan["canonical_survivor_drift"]:
        policy_failures.append("canonical stock-producer allowlist drifted")

    core_specs, release_specs = component_specs(instance, catalog)
    if run_components:
        core = execute_components(core_specs)
        release = execute_components(release_specs)
    else:
        core = [dict(value) for value in (core_results or [])]
        release = [dict(value) for value in (release_results or [])]

    big_gate = big_release_gate()
    status, blockers = evaluate_release_status(
        policy_failures, core, release, big_gate
    )

    relevant_scripts = [
        "industrial_petroleum_canonicalization.js",
        "industrial_sulfur_canonicalization.js",
        "industrial_steel_canonicalization.js",
        "industrial_uranium_yellorium_separation.js",
        "industrial_allthemodium_currency.js",
    ]
    return {
        "schema_version": 1,
        "status": status,
        "audit_id": "cross_pack_progression_loophole_closure",
        "scope": {
            "catalog": str(catalog),
            "catalog_recipes_sha256": digest_path(catalog / "recipes.csv"),
            "instance_mods": str(instance / "mods"),
            "installed_jar_count": len(list((instance / "mods").glob("*.jar"))),
            "seed": str(SEED.relative_to(PROJECT)).replace("\\", "/"),
            "seed_sha256": digest_path(SEED),
            "assignments_sha256": digest_path(ASSIGNMENTS),
            "manifest_sha256": digest_path(MANIFEST),
            "compiled_sha256": digest_path(COMPILED),
            "canonicalization_policy_sha256": digest_path(POLICIES),
            "relevant_script_sha256": OrderedDict(
                (
                    name,
                    digest_path(SERVER_SCRIPTS / name),
                )
                for name in relevant_scripts
            ),
        },
        "release_gate": {
            "big_reactors": big_gate,
            "blocking_reasons": blockers,
        },
        "protected_contract": {
            **protected_counts,
            "exact_removal_ids": len(exact_removals),
            "preserved_stock_recipe_ids": len(preserved),
            "required_retired_technology_recipe_ids": sorted(RETIRED_TECH_RECIPE_IDS),
            "required_retired_technology_outputs": sorted(RETIRED_TECH_OUTPUTS),
            "required_critical_outputs": sorted(REQUIRED_CRITICAL_OUTPUTS),
            "allowed_canonical_stock_producers": OrderedDict(
                (output, sorted(values))
                for output, values in sorted(ALLOWED_STOCK_PRODUCERS_BY_OUTPUT.items())
            ),
        },
        "policy_failures": policy_failures,
        "residual_producer_scan": scan,
        "component_validators": {
            "authoritative": core,
            "release_freshness": release,
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    status = str(report["status"])
    protected = report["protected_contract"]
    scan = report["residual_producer_scan"]
    lines = [
        "# Cross-pack progression loophole closure",
        "",
        f"Status: **{status}**.",
        "",
        "This is the final composite safety net for the industrial progression overhaul. It reuses the authoritative domain validators and adds a catalog-wide direct-producer census over every exclusive seed output, canonical/deprecated material surface, manufactured-currency form, and explicitly retired bypass output.",
        "",
        "## Coverage",
        "",
        f"- {protected['unique_protected_outputs']} unique protected outputs.",
        f"- {protected['exact_removal_ids']} exact recipe-removal IDs from source policy.",
        f"- {scan['catalog_rows']} catalog rows; {scan['installed_source_rows']} backed by currently installed JARs.",
        f"- {scan['relevant_installed_rows']} installed rows touch protected outputs.",
        f"- {len(scan['unmanaged_residuals'])} protected outputs have unmanaged residual producers.",
        "",
        "## Authoritative validators",
        "",
        "| Validator | Result | Purpose |",
        "|---|---|---|",
    ]
    for group in ("authoritative", "release_freshness"):
        for result in report["component_validators"][group]:
            result_text = "PASS" if result["returncode"] == 0 else "PENDING/FAIL"
            lines.append(f"| `{result['id']}` | {result_text} | {result['purpose']} |")

    lines.extend(
        [
            "",
            "## Locked progression conclusions",
            "",
            "- Create Diesel Generators may burn only the canonical TFMG Diesel/Gasoline tags; biodiesel, ethanol, and plant oil fuel definitions remain disabled.",
            "- Player-facing sulfuric acid is synthesized only by `tfmg:vat_machine_recipe/sulfuric_acid`; the approved Rotary Condensentrator bridge is conversion, not synthesis.",
            "- Yellorium feeds forward into raw uranium and staged Mekanism enrichment; reverse conversion and furnace shortcuts remain rejected by the full active-JAR chemistry scan.",
            "- Allthemodium, Vibranium, Unobtainium, and their alloys remain manufactured currency; ore placement, loot, stock furnace/Mekanism/TConstruct acquisition, normal smithing upgrades, compression aliases, and the Teleport Pad remain closed.",
            "- Digital Miner, Energized Smelter and all four Smelting Factory entrances, Mekanism teleport/QIO entrances, and Quantum Entangloporter remain physically retired.",
            "- TFMG steel remains the sole solid steel family, and AE2 Printed Silicon is Brass-press compacted from `tfmg:silicon_ingot` with both stock AE2 and ExtendedAE shortcuts removed.",
            "",
            "## Residual producer classifications",
            "",
        ]
    )
    for role, count in scan["classification_counts"].items():
        lines.append(f"- `{role}`: {count}")
    if scan["unmanaged_residuals"]:
        lines.extend(["", "### Unmanaged residuals", ""])
        for output, identities in scan["unmanaged_residuals"].items():
            lines.append(f"- `{output}`: " + ", ".join(f"`{value}`" for value in identities))

    blockers = report["release_gate"]["blocking_reasons"]
    lines.extend(["", "## Release gate", ""])
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("All closure checks are green. The report is ready for serialized README/deploy wiring.")
    lines.extend(
        [
            "",
            "## Commands",
            "",
            "```powershell",
            "python tools/validate_cross_pack_progression_loophole_closure.py --write --allow-pending",
            "python tools/validate_cross_pack_progression_loophole_closure.py",
            "python -m unittest tools.test_validate_cross_pack_progression_loophole_closure",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def encoded_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_MARKDOWN)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument(
        "--contract-only",
        action="store_true",
        help=(
            "validate a caller-supplied instance/catalog without comparing "
            "machine-specific evidence paths to the committed report"
        ),
    )
    parser.add_argument("--allow-pending", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(args.instance.resolve(), args.catalog.resolve())
    json_text = encoded_json(report)
    markdown_text = render_markdown(report)
    if args.write:
        args.report_json.resolve().write_text(json_text, encoding="utf-8")
        args.report_markdown.resolve().write_text(markdown_text, encoding="utf-8")
        print(f"Wrote {args.report_json.resolve()}")
        print(f"Wrote {args.report_markdown.resolve()}")
    elif not args.contract_only:
        drift: list[Path] = []
        for path, expected in (
            (args.report_json.resolve(), json_text),
            (args.report_markdown.resolve(), markdown_text),
        ):
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                drift.append(path)
        if drift:
            print("Cross-pack loophole closure artifacts drifted:")
            for path in drift:
                print(f"- {path}")
            return 1

    status = report["status"]
    scan = report["residual_producer_scan"]
    print(f"Cross-pack progression loophole closure: {status}")
    print(
        f"- {report['protected_contract']['unique_protected_outputs']} protected outputs; "
        f"{scan['relevant_installed_rows']} relevant installed catalog rows"
    )
    print(f"- unmanaged residual producers: {len(scan['unmanaged_residuals'])}")
    if status == "green":
        return 0
    if status == "pending_big_integration_or_regeneration" and args.allow_pending:
        return 0
    return 2 if status == "pending_big_integration_or_regeneration" else 1


if __name__ == "__main__":
    raise SystemExit(main())
