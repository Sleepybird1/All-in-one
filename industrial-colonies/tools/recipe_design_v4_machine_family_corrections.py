#!/usr/bin/env python3
"""Apply explicit machine-family corrections from the second review pass."""

from __future__ import annotations

from typing import Any


WEATHERED_IDS = frozenset(
    {
        "industrial_colonies:big_cannons/casting_sand_batch",
        "industrial_colonies:fluid_infrastructure/aluminum_pipe",
        "industrial_colonies:fluid_infrastructure/steel_pipe",
        "industrial_colonies:tfmg_core/heavy_plate",
    }
)

INDUSTRIAL_IDS = frozenset(
    {
        "industrial_colonies:big_cannons/steel_breech_extractor",
        "industrial_colonies:big_cannons/steel_screw_lock",
        "industrial_colonies:big_cannons/steel_sliding_breechblock",
        "industrial_colonies:diesel_generators_coverage/engine_piston",
        "industrial_colonies:diesel_generators_coverage/engine_silencer",
        "industrial_colonies:simulated/engine_assembly",
        "industrial_colonies:tfmg_coverage/machine_input",
    }
)

DEFAULT_CREATE_IDS = frozenset(
    {
        "industrial_colonies:manufacturing/weathered_iron/deployer",
        "industrial_colonies:manufacturing/weathered_iron/depot",
        "industrial_colonies:manufacturing/weathered_iron/fan",
        "industrial_colonies:manufacturing/weathered_iron/mixer",
        "industrial_colonies:manufacturing/weathered_iron/press",
        "industrial_colonies:manufacturing/weathered_iron/saw",
    }
)

_DEFAULT_CREATE_SOURCE_BY_ID = {
    "industrial_colonies:manufacturing/weathered_iron/deployer": "create:deployer",
    "industrial_colonies:manufacturing/weathered_iron/depot": "create:depot",
    "industrial_colonies:manufacturing/weathered_iron/fan": "create:encased_fan",
    "industrial_colonies:manufacturing/weathered_iron/mixer": "create:mechanical_mixer",
    "industrial_colonies:manufacturing/weathered_iron/press": "create:mechanical_press",
    "industrial_colonies:manufacturing/weathered_iron/saw": "create:mechanical_saw",
}

# These are deliberately role-specific rather than a shared expensive shell.
# The Weathered line is the first electrically assisted machine-building branch:
# it upgrades native Create tools and, crucially, exists before the Railway line
# that consumes TFMG Heavy Plates.
_DEFAULT_CREATE_LOADS_BY_ID = {
    "industrial_colonies:manufacturing/weathered_iron/deployer": (
        "create:weathered_iron_block",
        "create:iron_sheet",
        "tfmg:circuit_board",
        "tfmg:plastic_sheet",
        "create:brass_hand",
        "tfmg:transistor_item",
        "tfmg:electric_motor",
    ),
    "industrial_colonies:manufacturing/weathered_iron/depot": (
        "create:weathered_iron_block",
        "create:iron_sheet",
        "create:sturdy_sheet",
        "tfmg:plastic_sheet",
        "create:content_observer",
        "tfmg:capacitor_item",
    ),
    "industrial_colonies:manufacturing/weathered_iron/fan": (
        "create:weathered_iron_block",
        "create:iron_sheet",
        "tfmg:magnetic_alloy_sheet",
        "create:propeller",
        "tfmg:electric_motor",
        "tfmg:capacitor_item",
    ),
    "industrial_colonies:manufacturing/weathered_iron/mixer": (
        "create:weathered_iron_block",
        "create:iron_sheet",
        "create:whisk",
        "tfmg:electric_motor",
        "create:large_cogwheel",
        "tfmg:magnetic_alloy_sheet",
    ),
    "industrial_colonies:manufacturing/weathered_iron/press": (
        "create:weathered_iron_block",
        "2x create:iron_sheet",
        "create:sturdy_sheet",
        "tfmg:electric_motor",
        "tfmg:magnetic_alloy_sheet",
        "tfmg:circuit_board",
    ),
    "industrial_colonies:manufacturing/weathered_iron/saw": (
        "create:weathered_iron_block",
        "create:iron_sheet",
        "create:sturdy_sheet",
        "tfmg:electric_motor",
        "tfmg:magnetic_alloy_sheet",
        "tfmg:copper_wire",
    ),
}

CORRECTED_IDS = WEATHERED_IDS | INDUSTRIAL_IDS | DEFAULT_CREATE_IDS

_SUFFIXES = (
    "adjustable_chain_gearshift",
    "automatic_clutch",
    "chain_conveyor",
    "configurable_gearbox",
    "portable_storage_interface",
    "mechanical_roller",
    "mechanical_drill",
    "mechanical_saw",
    "encased_chain_drive",
    "encased_fan",
    "deployer",
    "gearshift",
    "gearbox",
    "clutch",
    "mixer",
    "press",
    "slicer",
    "depot",
)


def _index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed seed must contain a recipes list")
    result: dict[str, dict[str, Any]] = {}
    for recipe in recipes:
        if not isinstance(recipe, dict) or not isinstance(recipe.get("id"), str):
            raise TypeError("managed recipes must be objects with string IDs")
        recipe_id = recipe["id"]
        if recipe_id in result:
            raise ValueError(f"duplicate managed recipe ID: {recipe_id}")
        result[recipe_id] = recipe
    return result


def _machine_for_family(machine: str, family: str) -> str:
    if family == "default_create":
        defaults = {
            "deployer": "create:deployer",
            "press": "create:mechanical_press",
            "mixer": "create:mechanical_mixer",
            "mechanical_saw": "create:mechanical_saw",
            "encased_fan": "create:encased_fan",
        }
        if machine in defaults.values():
            return machine
        for suffix, replacement in defaults.items():
            if machine.endswith("_" + suffix):
                return replacement
        raise ValueError(f"cannot map reviewed machine {machine!r} to base Create")
    for suffix in _SUFFIXES:
        if machine.endswith("_" + suffix):
            return f"createcasing:{family}_{suffix}"
    raise ValueError(f"cannot map reviewed machine {machine!r} to {family}")


def _rebuild_weathered_bootstrap(recipe: dict[str, Any], recipe_id: str) -> None:
    source = _DEFAULT_CREATE_SOURCE_BY_ID[recipe_id]
    loads = _DEFAULT_CREATE_LOADS_BY_ID[recipe_id]
    role = recipe_id.rsplit("/", 1)[-1]
    preserved = {
        key: recipe[key]
        for key in ("id", "output", "remove", "exclusive_output")
        if key in recipe
    }
    recipe.clear()
    recipe.update(preserved)
    recipe.update(
        {
            "phase": "Steel & Petroleum",
            "node": "CR01 — The Steel Age",
            "order": 240 + sorted(DEFAULT_CREATE_IDS).index(recipe_id),
            "type": "sequenced_assembly",
            "comment": (
                f"Rehouse the native Create {role.replace('_', ' ')} as a "
                "Weathered Iron production tool, installing only its structural, "
                "drive, control, and role-specific working parts before sealing."
            ),
            "input": source,
            "transitional": source,
            "loops": 1,
            "steps": [
                {
                    "op": "deploying",
                    "ingredient": ingredient,
                    "machine": "create:deployer",
                }
                for ingredient in loads
            ]
            + [{"op": "pressing", "machine": "create:mechanical_press"}],
        }
    )


def apply(data: dict[str, Any]) -> None:
    recipes = _index(data)
    missing = sorted(CORRECTED_IDS.difference(recipes))
    if missing:
        raise KeyError(f"expected wrong-family recipes are missing: {missing}")

    for recipe_id in sorted(CORRECTED_IDS):
        if recipe_id in DEFAULT_CREATE_IDS:
            _rebuild_weathered_bootstrap(recipes[recipe_id], recipe_id)
            continue
        elif recipe_id in WEATHERED_IDS:
            family = "weathered_iron"
        else:
            family = "industrial_iron"
        recipe = recipes[recipe_id]
        if isinstance(recipe.get("machine"), str):
            recipe["machine"] = _machine_for_family(recipe["machine"], family)
        for step in recipe.get("steps", []):
            if isinstance(step, dict) and isinstance(step.get("machine"), str):
                step["machine"] = _machine_for_family(step["machine"], family)

    # ``tfmg:steel_sheet`` was carried in from an early catalog assumption but
    # is not registered by the installed TFMG 1.2.0 jar.  The Weathered line
    # uses Create's real pressed iron sheet before Heavy Plates exist, and the
    # nonexistent identifier must not remain as an excluded pseudo-output.
    for field in ("exclude_outputs", "user_owned_outputs"):
        if isinstance(data.get(field), list):
            data[field] = [value for value in data[field] if value != "tfmg:steel_sheet"]

    audit(data)


def audit(data: dict[str, Any]) -> dict[str, Any]:
    recipes = _index(data)
    errors: list[str] = []
    for recipe_id in sorted(CORRECTED_IDS):
        if recipe_id not in recipes:
            errors.append(f"missing corrected recipe {recipe_id}")
            continue
        if recipe_id in DEFAULT_CREATE_IDS:
            expected = "default_create"
        elif recipe_id in WEATHERED_IDS:
            expected = "weathered_iron"
        else:
            expected = "industrial_iron"
        machines: list[str] = []
        recipe = recipes[recipe_id]
        if isinstance(recipe.get("machine"), str):
            machines.append(recipe["machine"])
        machines.extend(
            step["machine"]
            for step in recipe.get("steps", [])
            if isinstance(step, dict) and isinstance(step.get("machine"), str)
        )
        if not machines:
            errors.append(f"{recipe_id} exposes no machine selection")
        for machine in machines:
            if expected == "default_create":
                valid = machine in {
                    "create:deployer",
                    "create:mechanical_press",
                    "create:mechanical_mixer",
                    "create:mechanical_saw",
                    "create:encased_fan",
                }
            else:
                valid = machine.startswith(f"createcasing:{expected}_")
            if not valid:
                errors.append(f"{recipe_id} still uses wrong machine {machine}")
        if recipe_id in DEFAULT_CREATE_IDS:
            source = _DEFAULT_CREATE_SOURCE_BY_ID[recipe_id]
            if recipe.get("input") != source or recipe.get("transitional") != source:
                errors.append(f"{recipe_id} does not upgrade its native Create machine")
            if recipe.get("phase") != "Steel & Petroleum":
                errors.append(f"{recipe_id} is not in the pre-Railway Steel branch")
            loads = tuple(
                step.get("ingredient")
                for step in recipe.get("steps", [])
                if isinstance(step, dict) and step.get("op") == "deploying"
            )
            if loads != _DEFAULT_CREATE_LOADS_BY_ID[recipe_id]:
                errors.append(f"{recipe_id} lost its reviewed role-specific loads")
            if "tfmg:steel_sheet" in repr(recipe):
                errors.append(f"{recipe_id} uses nonexistent TFMG Steel Sheet")
    for field in ("exclude_outputs", "user_owned_outputs"):
        if "tfmg:steel_sheet" in data.get(field, []):
            errors.append(f"{field} still contains nonexistent TFMG Steel Sheet")
    if errors:
        raise ValueError("Reviewed machine-family audit failed: " + " | ".join(errors))
    return {
        "status": "PASS",
        "corrected": len(CORRECTED_IDS),
        "default_create": len(DEFAULT_CREATE_IDS),
        "weathered": len(WEATHERED_IDS),
        "industrial": len(INDUSTRIAL_IDS),
    }
