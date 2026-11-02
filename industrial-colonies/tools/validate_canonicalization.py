from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RECIPE_PATH = re.compile(r"^data/([^/]+)/(?:recipe|recipes)/(.+)\.json$")
REMOVAL_ARRAY = re.compile(
    r"const\s+removed\w+\s*=\s*\[(.*?)\]",
    re.DOTALL,
)
RESOURCE_ID = re.compile(r"['\"]([a-z0-9_.-]+:[a-z0-9_./-]+)['\"]")
OUTPUT_KEYS = {
    "result",
    "results",
    "output",
    "outputs",
    "primary_output",
    "secondary_output",
    "item_output",
    "chemical_output",
    "fluid_output",
    "main_output",
    "byproduct",
    "byproducts",
}


@dataclass(frozen=True)
class Recipe:
    recipe_id: str
    recipe_type: str
    jar: str
    outputs: frozenset[str]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_outputs(node: Any, output_context: bool = False) -> set[str]:
    outputs: set[str] = set()
    if isinstance(node, str):
        if output_context and ":" in node:
            outputs.add(node.lstrip("#"))
        return outputs
    if isinstance(node, list):
        for value in node:
            outputs.update(extract_outputs(value, output_context))
        return outputs
    if not isinstance(node, dict):
        return outputs

    if output_context:
        for key in ("item", "id", "fluid", "chemical"):
            value = node.get(key)
            if isinstance(value, str) and ":" in value:
                outputs.add(value.lstrip("#"))
            elif isinstance(value, (dict, list)):
                outputs.update(extract_outputs(value, True))
        tag = node.get("tag")
        if isinstance(tag, str) and ":" in tag:
            outputs.add("#" + tag.lstrip("#"))

    for key, value in node.items():
        normalized = key.lower().replace("-", "_")
        child_output = output_context or normalized in OUTPUT_KEYS or normalized.endswith("_output")
        outputs.update(extract_outputs(value, child_output))
    return outputs


def load_active_recipes(mods_dir: Path) -> tuple[dict[str, Recipe], list[str]]:
    recipes: dict[str, Recipe] = {}
    errors: list[str] = []
    for jar_path in sorted(mods_dir.glob("*.jar"), key=lambda path: path.name.lower()):
        try:
            with zipfile.ZipFile(jar_path) as archive:
                for entry in archive.namelist():
                    match = RECIPE_PATH.match(entry)
                    if not match:
                        continue
                    namespace, path = match.groups()
                    recipe_id = f"{namespace}:{path}"
                    try:
                        data = json.loads(archive.read(entry).decode("utf-8-sig"))
                    except Exception as exc:  # report malformed data without hiding other results
                        errors.append(f"{jar_path.name}!{entry}: {exc}")
                        continue
                    recipe_type = data.get("type", "") if isinstance(data, dict) else ""
                    recipes[recipe_id] = Recipe(
                        recipe_id=recipe_id,
                        recipe_type=recipe_type,
                        jar=jar_path.name,
                        outputs=frozenset(extract_outputs(data)),
                    )
        except Exception as exc:
            errors.append(f"{jar_path.name}: {exc}")
    return recipes, errors


def parse_removed_recipe_ids(server_scripts: Path) -> set[str]:
    removed: set[str] = set()
    for script in server_scripts.glob("*.js"):
        text = script.read_text(encoding="utf-8")
        for body in REMOVAL_ARRAY.findall(text):
            removed.update(RESOURCE_ID.findall(body))
    return removed


def cdg_fuel_type_path(resource_id: str) -> str:
    namespace, path = resource_id.split(":", 1)
    if namespace != "createdieselgenerators":
        raise ValueError(f"not a Create Diesel Generators fuel type: {resource_id}")
    return f"data/{namespace}/{namespace}/fuel_type/{path}.json"


def validate_cdg_engine_fuels(
    project: Path,
    mods_dir: Path,
    petroleum_group: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Validate CDG's data-driven engine fuels, which recipe scans cannot see."""

    failures: list[str] = []
    report: dict[str, Any] = {
        "source_jar": None,
        "discovered": [],
        "allowed": [],
        "disabled": [],
        "empty_fluid_tag": None,
    }
    policy = petroleum_group.get("cdg_engine_fuel_policy")
    if not isinstance(policy, dict):
        failures.append("petroleum policy is missing cdg_engine_fuel_policy")
        return report, failures

    allowed = policy.get("allowed")
    disabled = policy.get("disabled")
    empty_tag = policy.get("empty_fluid_tag")
    if not isinstance(allowed, dict) or not allowed:
        failures.append("CDG engine policy has no allowed fuel types")
        allowed = {}
    if not isinstance(disabled, list) or not disabled:
        failures.append("CDG engine policy has no disabled fuel types")
        disabled = []
    if not isinstance(empty_tag, str) or ":" not in empty_tag:
        failures.append("CDG engine policy has an invalid empty_fluid_tag")
        empty_tag = "industrial_colonies:disabled_cdg_engine_fuels"

    allowed_ids = set(allowed)
    disabled_ids = set(disabled)
    if allowed_ids & disabled_ids:
        failures.append(
            "CDG engine fuel types are both allowed and disabled: "
            + " | ".join(sorted(allowed_ids & disabled_ids))
        )
    if len(disabled_ids) != len(disabled):
        failures.append("CDG engine disabled fuel list contains duplicates")

    report["allowed"] = sorted(allowed_ids)
    report["disabled"] = sorted(disabled_ids)
    report["empty_fluid_tag"] = empty_tag

    candidates = sorted(mods_dir.glob("createdieselgenerators-*.jar"))
    if len(candidates) != 1:
        failures.append(
            f"expected exactly one Create Diesel Generators jar, found {len(candidates)}"
        )
        return report, failures

    jar_path = candidates[0]
    report["source_jar"] = jar_path.name
    prefix = "data/createdieselgenerators/createdieselgenerators/fuel_type/"
    stock: dict[str, dict[str, Any]] = {}
    try:
        with zipfile.ZipFile(jar_path) as archive:
            for entry in archive.namelist():
                if not entry.startswith(prefix) or not entry.endswith(".json"):
                    continue
                path = entry[len(prefix) : -len(".json")]
                resource_id = f"createdieselgenerators:{path}"
                try:
                    value = json.loads(archive.read(entry).decode("utf-8-sig"))
                except Exception as exc:
                    failures.append(f"invalid CDG fuel type {resource_id}: {exc}")
                    continue
                if not isinstance(value, dict):
                    failures.append(f"CDG fuel type is not an object: {resource_id}")
                    continue
                stock[resource_id] = value
    except Exception as exc:
        failures.append(f"unable to inspect CDG fuel registry in {jar_path.name}: {exc}")
        return report, failures

    discovered = set(stock)
    report["discovered"] = sorted(discovered)
    declared = allowed_ids | disabled_ids
    if discovered != declared:
        missing = sorted(discovered - declared)
        stale = sorted(declared - discovered)
        if missing:
            failures.append(
                "CDG engine fuel types lack an explicit allow/disable policy: "
                + " | ".join(missing)
            )
        if stale:
            failures.append(
                "CDG engine policy names absent source fuel types: " + " | ".join(stale)
            )

    resources = project / "src" / "main" / "resources"
    for resource_id, fluid_tag in sorted(allowed.items()):
        source = stock.get(resource_id)
        if source is not None and source.get("fluid") != f"#{fluid_tag}":
            failures.append(
                f"allowed CDG fuel {resource_id} no longer reads #{fluid_tag}"
            )
        override = resources / cdg_fuel_type_path(resource_id)
        if override.exists():
            failures.append(f"allowed CDG fuel must not be overridden: {resource_id}")

    for resource_id in sorted(disabled_ids):
        source = stock.get(resource_id)
        if source is None:
            continue
        override_path = resources / cdg_fuel_type_path(resource_id)
        if not override_path.exists():
            failures.append(f"disabled CDG fuel has no datapack override: {resource_id}")
            continue
        try:
            override = json.loads(override_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            failures.append(f"invalid CDG override {override_path}: {exc}")
            continue
        expected = dict(source)
        expected["fluid"] = f"#{empty_tag}"
        if override != expected:
            failures.append(
                f"CDG override must preserve source performance and only replace fluid: {resource_id}"
            )

    tag_namespace, tag_path = empty_tag.split(":", 1)
    empty_tag_path = (
        resources / "data" / tag_namespace / "tags" / "fluid" / f"{tag_path}.json"
    )
    if not empty_tag_path.exists():
        failures.append(f"CDG disabled-engine empty tag is absent: {empty_tag_path}")
    else:
        try:
            tag_data = json.loads(empty_tag_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            failures.append(f"invalid CDG disabled-engine empty tag: {exc}")
        else:
            if tag_data != {"replace": True, "values": []}:
                failures.append(
                    "CDG disabled-engine fluid tag must be an explicit, empty replacement tag"
                )

    script_path = (
        project
        / "pack-scripts"
        / "server_scripts"
        / petroleum_group.get("script", "")
    )
    script = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
    if "removeAll('c:biodiesel')" not in script:
        failures.append("petroleum script does not clear the common biodiesel tag")

    return report, failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Industrial Colonies canonical materials against active mod jars."
    )
    parser.add_argument("instance", type=Path, help="Minecraft instance directory")
    parser.add_argument(
        "--project",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="industrial-colonies project root",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="optional JSON report path",
    )
    parser.add_argument(
        "--skip-installed-parity",
        action="store_true",
        help="validate project policies before deployment without comparing the live script copies",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    source_server = project / "pack-scripts" / "server_scripts"
    source_client = project / "pack-scripts" / "client_scripts"
    installed_server = args.instance / "kubejs" / "server_scripts"
    installed_client = args.instance / "kubejs" / "client_scripts"
    policies_path = project / "tools" / "canonicalization_policies.json"

    policies = json.loads(policies_path.read_text(encoding="utf-8"))
    stock_recipe_baseline = policies.get("runtime_mode") == "stock_recipe_baseline"
    recipes, archive_errors = load_active_recipes(args.instance / "mods")
    removed = parse_removed_recipe_ids(source_server)

    failures: list[str] = []
    warnings: list[str] = []
    bypasses: list[dict[str, str]] = []

    deprecated_to_group: dict[str, str] = {}
    for group in policies["groups"]:
        script_path = source_server / group["script"]
        if not script_path.exists():
            failures.append(f"Missing policy script: {script_path}")
            continue
        script_text = script_path.read_text(encoding="utf-8")
        if "removeAll" not in script_text:
            failures.append(f"{group['script']} does not clear canonical tags")
        for tag, values in group["canonical_tags"].items():
            if tag not in script_text:
                failures.append(f"{group['script']} does not mention tag {tag}")
            for value in values:
                if value not in script_text:
                    failures.append(f"{group['script']} does not add canonical value {value} to {tag}")
        for resource_id in group["deprecated_outputs"]:
            deprecated_to_group[resource_id] = group["name"]

    petroleum_groups = [
        group for group in policies["groups"] if group.get("name") == "petroleum"
    ]
    cdg_engine_fuels: dict[str, Any] = {}
    if len(petroleum_groups) != 1:
        failures.append(
            f"expected exactly one petroleum canonicalization policy, found {len(petroleum_groups)}"
        )
    else:
        cdg_engine_fuels, cdg_failures = validate_cdg_engine_fuels(
            project, args.instance.resolve() / "mods", petroleum_groups[0]
        )
        failures.extend(cdg_failures)

    effective_recipes = {
        recipe_id: recipe for recipe_id, recipe in recipes.items() if recipe_id not in removed
    }
    for recipe in effective_recipes.values():
        for output in recipe.outputs:
            group = deprecated_to_group.get(output)
            if group:
                bypasses.append(
                    {
                        "group": group,
                        "recipe_id": recipe.recipe_id,
                        "recipe_type": recipe.recipe_type,
                        "output": output,
                        "jar": recipe.jar,
                    }
                )

    machine_overhauls: list[dict[str, Any]] = []
    for policy in ([] if stock_recipe_baseline else policies.get("machine_overhauls", [])):
        machine = policy["machine"]
        source_producers = sorted(
            recipe.recipe_id for recipe in recipes.values() if machine in recipe.outputs
        )
        surviving_producers = sorted(
            recipe_id for recipe_id in source_producers if recipe_id not in removed
        )
        allowed_survivors = set(policy.get("allowed_surviving_source_recipes", []))
        unexpected_survivors = sorted(set(surviving_producers) - allowed_survivors)
        script_path = source_server / policy["script"]
        script_text = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
        replacement_declared = (
            policy["replacement_recipe"] in script_text
            and policy["replacement_type"] in script_text
            and machine in script_text
        )
        machine_overhauls.append(
            {
                **policy,
                "source_producers": source_producers,
                "surviving_source_producers": surviving_producers,
                "allowed_surviving_source_recipes": sorted(allowed_survivors),
                "unexpected_surviving_source_producers": unexpected_survivors,
                "replacement_declared": replacement_declared,
            }
        )
        if not source_producers and not policy.get("allow_missing_source_recipe", False):
            failures.append(f"Machine-overhaul target has no active source recipe: {machine}")
        missing_allowed = sorted(allowed_survivors - set(source_producers))
        if missing_allowed:
            failures.append(
                f"Allowed surviving recipe is absent for {machine}: {' | '.join(missing_allowed)}"
            )
        if unexpected_survivors:
            failures.append(
                f"Machine-overhaul bypass for {machine}: {' | '.join(unexpected_survivors)}"
            )
        if not replacement_declared:
            failures.append(
                f"Replacement recipe declaration is incomplete for {machine} in {policy['script']}"
            )

    machine_retirements: list[dict[str, Any]] = []
    for policy in ([] if stock_recipe_baseline else policies.get("machine_retirements", [])):
        machine = policy["machine"]
        script_path = source_server / policy["script"]
        script_text = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
        source_producers = sorted(
            recipe.recipe_id for recipe in recipes.values() if machine in recipe.outputs
        )
        surviving_producers = sorted(
            recipe_id for recipe_id in source_producers if recipe_id not in removed
        )
        factory_checks: list[dict[str, Any]] = []
        for factory in policy.get("factories", []):
            factory_producers = sorted(
                recipe.recipe_id for recipe in recipes.values() if factory in recipe.outputs
            )
            factory_survivors = sorted(
                recipe_id for recipe_id in factory_producers if recipe_id not in removed
            )
            factory_checks.append(
                {
                    "factory": factory,
                    "source_producers": factory_producers,
                    "surviving_source_producers": factory_survivors,
                }
            )
            if not factory_producers:
                failures.append(f"Retired factory has no active source recipe: {factory}")
            if factory_survivors:
                failures.append(
                    f"Retired-factory bypass for {factory}: {' | '.join(factory_survivors)}"
                )

        processing_removal_declared = True
        if policy["processing_type"].startswith("mekanism:"):
            processing_removal_declared = policy["processing_type"] in script_text
        declared_port_count = script_text.count("source: '")
        port_count_valid = declared_port_count >= policy.get("ported_recipe_count", 0)
        retirement_declared = (
            script_path.exists()
            and policy["source_recipe"] in script_text
            and machine in script_text
            and processing_removal_declared
            and port_count_valid
        )
        machine_retirements.append(
            {
                **policy,
                "source_producers": source_producers,
                "surviving_source_producers": surviving_producers,
                "processing_removal_declared": processing_removal_declared,
                "declared_port_count": declared_port_count,
                "factory_checks": factory_checks,
                "retirement_declared": retirement_declared,
            }
        )
        if not source_producers:
            failures.append(f"Machine-retirement target has no active source recipe: {machine}")
        if surviving_producers:
            failures.append(
                f"Machine-retirement bypass for {machine}: {' | '.join(surviving_producers)}"
            )
        if not retirement_declared:
            failures.append(
                f"Retirement declaration is incomplete for {machine} in {policy['script']}"
            )

    installer_factory_checks: list[dict[str, Any]] = []
    installer_policy = None if stock_recipe_baseline else policies.get("installer_only_factories")
    if installer_policy:
        script_path = source_server / installer_policy["script"]
        script_text = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
        if not script_path.exists():
            failures.append(f"Missing installer-only factory script: {script_path}")
        for recipe_id in installer_policy.get("recipes", []):
            recipe = recipes.get(recipe_id)
            declared = recipe_id in script_text
            removed_by_script = recipe_id in removed
            installer_factory_checks.append(
                {
                    "recipe_id": recipe_id,
                    "source_present": recipe is not None,
                    "outputs": sorted(recipe.outputs) if recipe else [],
                    "declared": declared,
                    "removed": removed_by_script,
                }
            )
            if recipe is None:
                failures.append(f"Installer-only factory source recipe is absent: {recipe_id}")
            if not declared:
                failures.append(
                    f"Installer-only factory recipe is not declared in {installer_policy['script']}: {recipe_id}"
                )
            if not removed_by_script:
                failures.append(f"Direct factory recipe survives installer-only policy: {recipe_id}")

    for bypass in bypasses:
        failures.append(
            "Unremoved deprecated output: "
            f"{bypass['recipe_id']} -> {bypass['output']} ({bypass['jar']})"
        )

    missing_removal_targets = sorted(recipe_id for recipe_id in removed if recipe_id not in recipes)
    for recipe_id in missing_removal_targets:
        warnings.append(f"Removal target is not present in an active jar: {recipe_id}")

    parity: list[dict[str, Any]] = []
    for source_dir, installed_dir, side in (
        (source_server, installed_server, "server"),
        (source_client, installed_client, "client"),
    ):
        for source in sorted(source_dir.glob("*.js")):
            installed = installed_dir / source.name
            match = installed.exists() and sha256(source) == sha256(installed)
            parity.append({"side": side, "script": source.name, "match": match})
            if not match and not args.skip_installed_parity:
                failures.append(f"Installed/source mismatch: {side}/{source.name}")

    report = {
        "runtime_mode": policies.get("runtime_mode", "legacy_progression"),
        "active_jars": len(list((args.instance / "mods").glob("*.jar"))),
        "active_recipes": len(recipes),
        "removed_recipe_ids": len(removed),
        "effective_recipes": len(effective_recipes),
        "policy_groups": len(policies["groups"]),
        "deprecated_resources": len(deprecated_to_group),
        "cdg_engine_fuels": cdg_engine_fuels,
        "bypasses": bypasses,
        "machine_overhauls": machine_overhauls,
        "machine_retirements": machine_retirements,
        "installer_only_factory_recipes": installer_factory_checks,
        "script_parity": parity,
        "archive_errors": archive_errors,
        "warnings": warnings,
        "failures": failures,
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"Scanned {report['active_jars']} active jars and {report['active_recipes']} recipes; "
        f"applied {report['removed_recipe_ids']} scripted recipe removals."
    )
    print(
        f"Checked {report['policy_groups']} policies, {report['deprecated_resources']} deprecated resources, "
        f"and {len(parity)} installed/source script pairs."
    )
    print(f"Checked {len(machine_overhauls)} major-machine construction overhaul(s).")
    print(f"Checked {len(machine_retirements)} Create-first machine retirement(s).")
    print(f"Checked {len(installer_factory_checks)} installer-only factory recipe(s).")
    print(
        "Checked CDG engine fuel registry policy: "
        f"{len(cdg_engine_fuels.get('allowed', []))} allowed, "
        f"{len(cdg_engine_fuels.get('disabled', []))} disabled."
    )
    if stock_recipe_baseline:
        print("Stock-recipe baseline mode: retired construction-overhaul policies were not enforced.")
    if archive_errors:
        print(f"Archive/JSON errors: {len(archive_errors)}", file=sys.stderr)
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"  WARN {warning}")
    if failures:
        print(f"FAIL: {len(failures)} issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: no active recipe produces a deprecated canonical-material output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
