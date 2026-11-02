#!/usr/bin/env python3
"""Validate managed ComputerCraft hardware and its closed state transfers.

The broad recipe overhaul is authored as managed KJSGen cards, not as KubeJS
recipe calls. This validator checks the expanded manifest and compiled editor
project directly, then scans installed dependencies to prove only cheap
ComputerCraft acquisition recipes are removed. Peripheral attachment, turtle
tool, recolouring, overlay, and full wired-modem conversions must remain.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import audit_recipe_reachability as audit
from validate_physical_progression import load_object, recipe_ingredients, run_core_validation


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = PROJECT / "build" / "reports" / "computercraft-hardware-validation.json"

KNOWN_THIRD_PARTY_MALFORMED_RESOURCES = {
    (
        "pamhc2foodextended-NEOFORGE-1.21.1-1.0.0.jar",
        "data/pamhc2foodextended/recipe/cookedtofabbititem_campfire.json",
    ): "Extra data:",
    (
        "pamhc2foodextended-NEOFORGE-1.21.1-1.0.0.jar",
        "data/pamhc2foodextended/recipe/cookedtofabbititem_forge.json",
    ): "Extra data:",
    (
        "pamhc2foodextended-NEOFORGE-1.21.1-1.0.0.jar",
        "data/pamhc2foodextended/recipe/cookedtofabbititem_smoker.json",
    ): "Extra data:",
}

STOCK_ACQUISITION_IDS = {
    "computercraft:cable",
    "computercraft:computer_normal",
    "computercraft:computer_advanced",
    "computercraft:computer_advanced_upgrade",
    "computercraft:disk_drive",
    "computercraft:monitor_normal",
    "computercraft:monitor_advanced",
    "computercraft:pocket_computer_normal",
    "computercraft:pocket_computer_advanced",
    "computercraft:pocket_computer_advanced_upgrade",
    "computercraft:printer",
    "computercraft:redstone_relay",
    "computercraft:speaker",
    "computercraft:turtle_normal",
    "computercraft:turtle_advanced",
    "computercraft:turtle_advanced_upgrade",
    "computercraft:wired_modem",
    "computercraft:wireless_modem_normal",
    "computercraft:wireless_modem_advanced",
}

PRESERVED_EXACT_IDS = {
    "computercraft:clear_colour",
    "computercraft:colour",
    "computercraft:pocket_computer_upgrade",
    "computercraft:turtle_upgrade",
    "computercraft:wired_modem_full_from",
    "computercraft:wired_modem_full_to",
}

PRESERVED_PREFIXES = (
    "computercraft:pocket_advanced/",
    "computercraft:pocket_normal/",
    "computercraft:turtle_advanced/",
    "computercraft:turtle_advanced_overlays/",
    "computercraft:turtle_normal/",
    "computercraft:turtle_normal_overlays/",
)


def classify_dependency_scan_errors(
    rows: list[dict[str, str]],
) -> tuple[list[str], list[str], list[dict[str, str]]]:
    """Fail unknown/project resources; retain exact reviewed third-party evidence."""

    failures: list[str] = []
    warnings: list[str] = []
    evidence: list[dict[str, str]] = []
    for row in rows:
        jar = str(row.get("jar", ""))
        path = str(row.get("path", ""))
        error = str(row.get("error", ""))
        key = (jar, path)
        project_owned = (
            jar.lower().startswith(("industrial-colonies", "industrial_colonies"))
            or "/industrial_colonies/" in f"/{path}"
        )
        expected_prefix = KNOWN_THIRD_PARTY_MALFORMED_RESOURCES.get(key)
        if project_owned:
            failures.append(f"project-owned malformed dependency resource: {jar}!/{path}: {error}")
        elif expected_prefix is None or not error.startswith(expected_prefix):
            failures.append(f"unreviewed malformed dependency resource: {jar}!/{path}: {error}")
        else:
            reviewed = {
                "classification": "reviewed_nonfatal_third_party_malformed_recipe",
                "jar": jar,
                "path": path,
                "error": error,
            }
            evidence.append(reviewed)
            warnings.append(f"reviewed third-party malformed recipe: {jar}!/{path}: {error}")
    return failures, warnings, evidence


def recipe_policy(
    phase: str,
    recipe_type: str,
    output: str,
    tier: str,
    required: set[str],
    *,
    transitional: str = "",
    removals: set[str] | None = None,
    count: int = 1,
) -> dict[str, Any]:
    return {
        "phase": phase,
        "type": recipe_type,
        "output": output,
        "tier": tier,
        "form": (
            "tiered_mechanical_crafting"
            if recipe_type == "mechanical_crafting"
            else "tiered_sequenced_assembly"
        ),
        "required": required,
        "transitional": transitional,
        "removals": removals or set(),
        "count": count,
    }


EXPECTED_RECIPES = {
    "industrial_colonies:computercraft/network/cable": recipe_policy(
        "Digital Logistics", "sequenced_assembly", "computercraft:cable", "brass",
        {"tfmg:copper_wire", "tfmg:rubber_sheet", "create:brass_sheet"},
        transitional="industrial_colonies:unfinished_computercraft_cable",
        removals={"computercraft:cable"}, count=8,
    ),
    "industrial_colonies:computercraft/network/wired_modem": recipe_policy(
        "Digital Logistics", "sequenced_assembly", "computercraft:wired_modem", "brass",
        {"computercraft:cable", "tfmg:circuit_board", "ae2:printed_logic_processor"},
        transitional="industrial_colonies:unfinished_computercraft_wired_modem",
        removals={"computercraft:wired_modem"},
    ),
    "industrial_colonies:computercraft/network/wireless_modem": recipe_policy(
        "Digital Logistics", "sequenced_assembly", "computercraft:wireless_modem_normal", "brass",
        {"computercraft:wired_modem", "tfmg:circuit_board", "ae2:printed_logic_processor", "minecraft:ender_pearl"},
        transitional="industrial_colonies:unfinished_computercraft_wireless_modem",
        removals={"computercraft:wireless_modem_normal"},
    ),
    "industrial_colonies:computercraft/computer/normal": recipe_policy(
        "Digital Logistics", "mechanical_crafting", "computercraft:computer_normal", "brass",
        {"create:brass_casing", "create:precision_mechanism", "tfmg:circuit_board", "ae2:printed_logic_processor"},
        removals={"computercraft:computer_normal"},
    ),
    "industrial_colonies:computercraft/monitor/normal": recipe_policy(
        "Digital Logistics", "mechanical_crafting", "computercraft:monitor_normal", "brass",
        {"create:brass_sheet", "create:display_board", "tfmg:circuit_board"},
        removals={"computercraft:monitor_normal"}, count=2,
    ),
    "industrial_colonies:computercraft/io/disk_drive": recipe_policy(
        "Digital Logistics", "mechanical_crafting", "computercraft:disk_drive", "brass",
        {"create:brass_sheet", "create:precision_mechanism", "tfmg:circuit_board", "ae2:printed_logic_processor"},
        removals={"computercraft:disk_drive"},
    ),
    "industrial_colonies:computercraft/io/printer": recipe_policy(
        "Digital Logistics", "mechanical_crafting", "computercraft:printer", "brass",
        {"create:brass_casing", "create:mechanical_piston", "tfmg:circuit_board", "ae2:printed_logic_processor"},
        removals={"computercraft:printer"},
    ),
    "industrial_colonies:computercraft/io/speaker": recipe_policy(
        "Digital Logistics", "sequenced_assembly", "computercraft:speaker", "brass",
        {"minecraft:note_block", "create:brass_sheet", "tfmg:circuit_board", "tfmg:copper_wire"},
        transitional="industrial_colonies:unfinished_computercraft_speaker",
        removals={"computercraft:speaker"},
    ),
    "industrial_colonies:computercraft/io/redstone_relay": recipe_policy(
        "Digital Logistics", "sequenced_assembly", "computercraft:redstone_relay", "brass",
        {"computercraft:wired_modem", "create:content_observer", "create:redstone_link", "tfmg:circuit_board"},
        transitional="industrial_colonies:unfinished_computercraft_redstone_relay",
        removals={"computercraft:redstone_relay"},
    ),
    "industrial_colonies:computercraft/mobile/pocket_computer": recipe_policy(
        "Digital Logistics", "mechanical_crafting", "computercraft:pocket_computer_normal", "brass",
        {"computercraft:computer_normal", "computercraft:monitor_normal", "computercraft:wireless_modem_normal"},
        removals={"computercraft:pocket_computer_normal"},
    ),
    "industrial_colonies:computercraft/mobile/turtle": recipe_policy(
        "Digital Logistics", "mechanical_crafting", "computercraft:turtle_normal", "brass",
        {"computercraft:computer_normal", "create:brass_casing", "create:precision_mechanism", "tfmg:electric_motor", "tfmg:circuit_board"},
        removals={"computercraft:turtle_normal"},
    ),
    "industrial_colonies:computercraft/network/advanced_wireless_modem": recipe_policy(
        "High-Energy Grid", "sequenced_assembly", "computercraft:wireless_modem_advanced", "weathered_iron",
        {"computercraft:wireless_modem_normal", "create:weathered_iron_block", "ae2:calculation_processor", "tfmg:etched_circuit_board", "minecraft:ender_eye"},
        transitional="industrial_colonies:unfinished_computercraft_advanced_wireless_modem",
        removals={"computercraft:wireless_modem_advanced"},
    ),
    "industrial_colonies:computercraft/computer/advanced_upgrade": recipe_policy(
        "High-Energy Grid", "sequenced_assembly", "computercraft:computer_advanced", "weathered_iron",
        {"computercraft:computer_normal", "create:weathered_iron_block", "ae2:calculation_processor", "ae2:engineering_processor", "tfmg:etched_circuit_board"},
        transitional="industrial_colonies:unfinished_computercraft_advanced_computer",
        removals={"computercraft:computer_advanced", "computercraft:computer_advanced_upgrade"},
    ),
    "industrial_colonies:computercraft/monitor/advanced": recipe_policy(
        "High-Energy Grid", "sequenced_assembly", "computercraft:monitor_advanced", "weathered_iron",
        {"computercraft:monitor_normal", "create:weathered_iron_block", "ae2:calculation_processor", "tfmg:etched_circuit_board"},
        transitional="industrial_colonies:unfinished_computercraft_advanced_monitor",
        removals={"computercraft:monitor_advanced"},
    ),
    "industrial_colonies:computercraft/mobile/advanced_pocket_upgrade": recipe_policy(
        "High-Energy Grid", "sequenced_assembly", "computercraft:pocket_computer_advanced", "weathered_iron",
        {"computercraft:pocket_computer_normal", "create:weathered_iron_block", "computercraft:wireless_modem_advanced", "computercraft:monitor_advanced", "ae2:engineering_processor"},
        transitional="industrial_colonies:unfinished_computercraft_advanced_pocket_computer",
        removals={"computercraft:pocket_computer_advanced", "computercraft:pocket_computer_advanced_upgrade"},
    ),
    "industrial_colonies:computercraft/mobile/advanced_turtle_upgrade": recipe_policy(
        "High-Energy Grid", "sequenced_assembly", "computercraft:turtle_advanced", "weathered_iron",
        {"computercraft:turtle_normal", "create:weathered_iron_block", "computercraft:computer_advanced", "ae2:engineering_processor", "tfmg:etched_circuit_board"},
        transitional="industrial_colonies:unfinished_computercraft_advanced_turtle",
        removals={"computercraft:turtle_advanced", "computercraft:turtle_advanced_upgrade"},
    ),
}

STATE_TRANSFER_RECIPES = {
    "data/industrial_colonies/recipe/computercraft/computer/advanced_state_transfer.json": ("computercraft:computer_advanced", "computercraft:computer_normal"),
    "data/industrial_colonies/recipe/computercraft/mobile/turtle_state_transfer.json": ("computercraft:turtle_normal", "computercraft:computer_normal"),
    "data/industrial_colonies/recipe/computercraft/mobile/advanced_turtle_state_transfer.json": ("computercraft:turtle_advanced", "computercraft:turtle_normal"),
    "data/industrial_colonies/recipe/computercraft/mobile/advanced_pocket_state_transfer.json": ("computercraft:pocket_computer_advanced", "computercraft:pocket_computer_normal"),
}

DOWNSTREAM_CONTROL_RECIPES = {
    "industrial_colonies:nuclear/basic_reactor_controller": {"computercraft:computer_advanced", "computercraft:monitor_advanced", "computercraft:redstone_relay"},
    "industrial_colonies:nuclear/reinforced_reactor_controller": {"computercraft:computer_advanced", "computercraft:monitor_advanced"},
    "industrial_colonies:nuclear/reinforced_computer_port": {"computercraft:computer_advanced", "computercraft:wired_modem"},
}

PROTECTED_OUTPUTS = {str(policy["output"]) for policy in EXPECTED_RECIPES.values()}


def spec_output(recipe: Mapping[str, Any]) -> tuple[str, int]:
    values = recipe.get("outputs")
    if not isinstance(values, list):
        values = [recipe.get("output")]
    if len(values) != 1:
        return "", 0
    value = values[0]
    if isinstance(value, str):
        if "x " in value:
            count, identifier = value.split("x ", 1)
            return identifier, int(count)
        return value, 1
    if isinstance(value, dict):
        return str(value.get("id", "")), int(value.get("count", 1))
    return "", 0


def card_output(card: Mapping[str, Any]) -> tuple[str, int]:
    slots = card.get("slots")
    if not isinstance(slots, dict):
        return "", 0
    outputs = [value for key, value in slots.items() if str(key).startswith("output") and isinstance(value, dict)]
    if len(outputs) != 1:
        return "", 0
    return str(outputs[0].get("id", "")), int(outputs[0].get("count", 1))


def direct_item_inputs(recipe: audit.Recipe) -> set[str]:
    return {resource.resource_id for group in recipe.inputs for resource in group if resource.kind == "item" and not resource.tag}


def direct_item_outputs(recipe: audit.Recipe) -> set[str]:
    return {resource.resource_id for resource in recipe.outputs if resource.kind == "item" and not resource.tag}


def validate_state_transfers(project: Path) -> list[str]:
    errors: list[str] = []
    resource_root = project / "src" / "main" / "resources"
    for relative, (target, source) in STATE_TRANSFER_RECIPES.items():
        path = resource_root / relative
        if not path.is_file():
            errors.append(f"missing state-transfer recipe: {path}")
            continue
        data = load_object(path)
        if data.get("type") != "computercraft:transform_shapeless":
            errors.append(f"{path.name} is not a ComputerCraft state-copying transform")
        result = data.get("result")
        if not isinstance(result, dict) or result.get("id") != target:
            errors.append(f"{path.name} does not output {target}")
        ingredients = data.get("ingredients") if isinstance(data.get("ingredients"), list) else []
        target_shell = ingredients[0] if ingredients and isinstance(ingredients[0], dict) else {}
        if not (
            target_shell.get("type") == "neoforge:components"
            and target_shell.get("items") == target
            and target_shell.get("components") == {}
            and target_shell.get("strict") is True
        ):
            errors.append(
                f"{path.name} must accept only a pristine {target} target shell through "
                "strict empty-component matching"
            )
        source_ingredients = {
            str(value.get("item"))
            for value in ingredients[1:]
            if isinstance(value, dict) and isinstance(value.get("item"), str)
        }
        if source not in source_ingredients:
            errors.append(f"{path.name} must consume configured state source {source}")
        functions = data.get("function") if isinstance(data.get("function"), list) else []
        copied_from = {str(function.get("from", {}).get("item")) for function in functions if isinstance(function, dict)}
        if source not in copied_from or not any(isinstance(function, dict) and function.get("type") == "computercraft:copy_components" for function in functions):
            errors.append(f"{path.name} does not copy ComputerCraft components from {source}")
    return errors


def validate_physical_rows(tiers: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    rows: dict[str, Mapping[str, Any]] = {}
    for group in tiers.get("canonical_output_groups", []):
        if not isinstance(group, dict):
            continue
        tier = str(group.get("tier", ""))
        for output in group.get("outputs", []):
            if not isinstance(output, dict):
                continue
            for recipe_id in output.get("recipe_ids", []):
                if isinstance(recipe_id, str):
                    rows[recipe_id] = {**output, "tier": tier}
    for recipe_id, policy in EXPECTED_RECIPES.items():
        row = rows.get(recipe_id)
        if row is None:
            errors.append(f"physical tier contract is missing {recipe_id}")
            continue
        if row.get("output") != policy["output"]:
            errors.append(f"physical tier output mismatch for {recipe_id}")
        if row.get("tier") != policy["tier"]:
            errors.append(f"physical tier mismatch for {recipe_id}: {row.get('tier')} != {policy['tier']}")
        if row.get("form") != policy["form"]:
            errors.append(f"physical form mismatch for {recipe_id}: {row.get('form')} != {policy['form']}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--compiled", type=Path)
    parser.add_argument("--tiers", type=Path)
    parser.add_argument("--node", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    instance = args.instance.resolve()
    manifest_path = (args.manifest or project / "progression/managed_recipe_overhaul.json").resolve()
    compiled_path = (args.compiled or project / "pack-kjsgen/default.managed.json").resolve()
    tiers_path = (args.tiers or project / "progression/physical_recipe_tiers.json").resolve()
    errors: list[str] = []
    warnings: list[str] = []
    stats: dict[str, int] = {}
    preserved_installed: set[str] = set()
    loopholes: list[dict[str, str]] = []
    dependency_scan_warning_evidence: list[dict[str, str]] = []

    try:
        manifest = load_object(manifest_path)
        compiled = load_object(compiled_path)
        tiers = load_object(tiers_path)
        specs, core_errors, core_warnings, removal_count = run_core_validation(manifest, compiled)
        errors.extend(f"managed core: {error}" for error in core_errors)
        warnings.extend(f"managed core: {warning}" for warning in core_warnings)
        specs_by_id = {str(spec.get("id", "")): spec for spec in specs}
        cards_by_id = {str(card.get("recipeId", "")): card for card in compiled.get("recipes", []) if isinstance(card, dict)}
        removal_ids = {str(card.get("recipeId")) for card in compiled.get("removals", []) if isinstance(card, dict) and isinstance(card.get("recipeId"), str)}
        cc_removals = {value for value in removal_ids if value.startswith("computercraft:")}
        if cc_removals != STOCK_ACQUISITION_IDS:
            errors.append(
                "ComputerCraft exact-removal set differs; "
                f"missing={sorted(STOCK_ACQUISITION_IDS - cc_removals)}, "
                f"extra={sorted(cc_removals - STOCK_ACQUISITION_IDS)}"
            )

        transitionals: list[str] = []
        for recipe_id, policy in EXPECTED_RECIPES.items():
            spec = specs_by_id.get(recipe_id)
            card = cards_by_id.get(recipe_id)
            if spec is None:
                errors.append(f"missing managed ComputerCraft recipe: {recipe_id}")
                continue
            if card is None:
                errors.append(f"missing compiled KJSGen card: {recipe_id}")
                continue
            if spec.get("phase") != policy["phase"] or spec.get("type") != policy["type"]:
                errors.append(f"{recipe_id} phase/type changed: {spec.get('phase')}/{spec.get('type')}")
            output, count = spec_output(spec)
            if (output, count) != (policy["output"], policy["count"]):
                errors.append(f"{recipe_id} source output changed: {(output, count)}")
            if card_output(card) != (policy["output"], policy["count"]):
                errors.append(f"{recipe_id} compiled output changed: {card_output(card)}")
            missing = sorted(policy["required"] - recipe_ingredients(spec))
            if missing:
                errors.append(f"{recipe_id} is missing required factory inputs: {missing}")
            if set(spec.get("remove", [])) != policy["removals"]:
                errors.append(f"{recipe_id} exact removals changed: {spec.get('remove')} != {sorted(policy['removals'])}")
            expected_card_type = "kjsgen:create_mechanical_crafting" if policy["type"] == "mechanical_crafting" else "kjsgen:create_sequenced_assembly"
            if card.get("type") != expected_card_type:
                errors.append(f"{recipe_id} has wrong KJSGen card type {card.get('type')}")

            if policy["type"] == "mechanical_crafting":
                pattern = spec.get("pattern")
                width = max((len(row) for row in pattern), default=0) if isinstance(pattern, list) else 0
                height = len(pattern) if isinstance(pattern, list) else 0
                if width < 5 or height < 5:
                    errors.append(f"{recipe_id} escaped its 5x5 construction ({width}x{height})")
            else:
                transitional = str(spec.get("transitional", ""))
                transitionals.append(transitional)
                if transitional != policy["transitional"]:
                    errors.append(f"{recipe_id} uses wrong closed transitional item {transitional}")
                slots = card.get("slots") if isinstance(card.get("slots"), dict) else {}
                transitional_slot = slots.get("transitional")
                if not isinstance(transitional_slot, dict) or transitional_slot.get("id") != transitional:
                    errors.append(f"{recipe_id} compiled transitional slot is stale")
                expected_deployer = f"createcasing:{policy['tier']}_deployer"
                expected_press = f"createcasing:{policy['tier']}_press"
                for slot_name, value in slots.items():
                    if not str(slot_name).startswith("__machine_step_") or not isinstance(value, dict):
                        continue
                    expected_machine = expected_press if str(slot_name).endswith("_pressing") else expected_deployer
                    if value.get("id") != expected_machine:
                        errors.append(f"{recipe_id} machine route escaped {policy['tier']}: {slot_name}={value.get('id')}")

        if len(transitionals) != len(set(transitionals)):
            errors.append("ComputerCraft sequenced assemblies reuse a transitional item")
        if any(not value.startswith("industrial_colonies:unfinished_computercraft_") for value in transitionals):
            errors.append("ComputerCraft sequences do not all use owned closed transitional items")

        for recipe_id, required in DOWNSTREAM_CONTROL_RECIPES.items():
            recipe = specs_by_id.get(recipe_id)
            if recipe is None:
                errors.append(f"missing downstream ComputerCraft control consumer: {recipe_id}")
                continue
            missing = sorted(required - recipe_ingredients(recipe))
            if missing:
                errors.append(f"{recipe_id} lost ComputerCraft instrumentation: {missing}")

        errors.extend(validate_physical_rows(tiers))
        errors.extend(validate_state_transfers(project))

        jar_scan = audit.scan_jars(instance / "mods")
        scan_failures, scan_warnings, dependency_scan_warning_evidence = (
            classify_dependency_scan_errors(jar_scan["errors"])
        )
        errors.extend(scan_failures)
        warnings.extend(scan_warnings)
        definitions = [recipe for recipe in jar_scan["definitions"] if recipe.condition_state != "inactive"]
        installed_ids = {recipe.recipe_id for recipe in definitions}
        missing_stock = sorted(STOCK_ACQUISITION_IDS - installed_ids)
        if missing_stock:
            errors.append(f"installed CC:Tweaked is missing expected acquisition IDs: {missing_stock}")
        missing_preserved = sorted(PRESERVED_EXACT_IDS - installed_ids)
        if missing_preserved:
            errors.append(f"installed CC:Tweaked is missing preserved transforms: {missing_preserved}")
        preserved_installed = {
            recipe_id for recipe_id in installed_ids
            if recipe_id in PRESERVED_EXACT_IDS or any(recipe_id.startswith(prefix) for prefix in PRESERVED_PREFIXES)
        }
        accidentally_removed = sorted(preserved_installed.intersection(removal_ids))
        if accidentally_removed:
            errors.append("peripheral/tool/overlay/full-modem recipes were removed: " + ", ".join(accidentally_removed))

        for recipe in definitions:
            outputs = direct_item_outputs(recipe).intersection(PROTECTED_OUTPUTS)
            if not outputs:
                continue
            inputs = direct_item_inputs(recipe)
            for output in outputs:
                if recipe.recipe_id in STOCK_ACQUISITION_IDS or output in inputs:
                    continue
                if recipe.recipe_id == "computercraft:wired_modem_full_to" and "computercraft:wired_modem_full" in inputs:
                    continue
                loopholes.append({"output": output, "recipe_id": recipe.recipe_id, "recipe_type": recipe.recipe_type, "source": recipe.source})
        for row in loopholes:
            errors.append(f"unapproved installed acquisition for {row['output']}: {row['recipe_id']} ({row['recipe_type']})")

        full_modem_producers = [recipe for recipe in definitions if "computercraft:wired_modem_full" in direct_item_outputs(recipe)]
        unsafe_full_modem = sorted({recipe.recipe_id for recipe in full_modem_producers if "computercraft:wired_modem" not in direct_item_inputs(recipe)})
        if unsafe_full_modem:
            errors.append(f"wired_modem_full gained an independent producer: {unsafe_full_modem}")

        stats = {
            "expanded_managed_recipes": len(specs),
            "exact_recipe_removals": removal_count,
            "computercraft_factory_cards": len(EXPECTED_RECIPES),
            "computercraft_stock_removals": len(STOCK_ACQUISITION_IDS),
            "unique_transitional_items": len(set(transitionals)),
            "state_transfer_recipes": len(STATE_TRANSFER_RECIPES),
            "preserved_installed_transforms": len(preserved_installed),
            "downstream_control_recipes": len(DOWNSTREAM_CONTROL_RECIPES),
            "jars_scanned": len(jar_scan["jars"]),
            "jar_recipe_definitions": len(jar_scan["definitions"]),
            "jar_scan_warnings": len(dependency_scan_warning_evidence),
            "jar_scan_failures": len(scan_failures),
            "loopholes": len(loopholes),
        }
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, KeyError, ImportError) as exc:
        errors.append(str(exc))

    report = {
        "schema_version": 2,
        "authority": "managed_kjsgen_computercraft_hardware",
        "status": "pass" if not errors else "fail",
        "project": str(project),
        "instance": str(instance),
        "manifest": str(manifest_path),
        "compiled_project": str(compiled_path),
        "physical_tiers": str(tiers_path),
        "statistics": stats,
        "stock_acquisition_removals": sorted(STOCK_ACQUISITION_IDS),
        "preserved_installed_recipes": sorted(preserved_installed),
        "state_transfer_resources": sorted(STATE_TRANSFER_RECIPES),
        "dependency_scan_warning_evidence": dependency_scan_warning_evidence,
        "loopholes": loopholes,
        "warnings": warnings,
        "errors": errors,
    }
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if errors:
        print(f"FAIL: {len(errors)} ComputerCraft progression issue(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        print(f"Report: {report_path}")
        return 1
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    print(
        "PASS: ComputerCraft uses "
        f"{stats.get('computercraft_factory_cards', 0)} managed factory cards, "
        f"{stats.get('computercraft_stock_removals', 0)} exact stock removals, "
        f"{stats.get('unique_transitional_items', 0)} closed intermediates, and "
        f"{stats.get('state_transfer_recipes', 0)} non-bootstrap state transfers."
    )
    print(
        f"Preserved {stats.get('preserved_installed_transforms', 0)} installed "
        "peripheral/tool/overlay/full-modem transforms; no acquisition bypass found."
    )
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
