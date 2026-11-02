"""Purpose-built sequenced assembly for every finished digital storage cell.

The component and housing recipes remain owned by the earlier AE2/MEGA Cells
and AppliedCreate passes.  This module replaces only the thirty *finished*
cells which were still being closed by a single compacting operation:

* AE2 item and fluid cells, 1k through 256k;
* MEGA item and fluid cells, 1M through 256M; and
* AppliedCreate stress cells, 1k through 256M.

Each family has a different physical vocabulary.  Item cells receive a logic
processor, an indexed interconnect, and insulation.  Fluid cells receive a
pipe/valve path, rubber sealing, and a glass service face.  MEGA cells install
an Accumulation Processor, complementary semiconductors, lithium buffering,
and magnetic shielding.  Stress cells install shafts, stress instrumentation,
and increasingly capable kinetic control rather than copying the ordinary
AE item-cell sequence.

``apply`` is idempotent and mutates only the supplied seed dictionary.  This
module deliberately performs no filesystem or live-instance writes.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable


BRASS_DEPLOYER = "createcasing:brass_deployer"
BRASS_PRESS = "createcasing:brass_press"
RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"
WEATHERED_DEPLOYER = "createcasing:weathered_iron_deployer"
WEATHERED_PRESS = "createcasing:weathered_iron_press"
RADIANCE_DEPLOYER = "createcasing:refined_radiance_deployer"
RADIANCE_PRESS = "createcasing:refined_radiance_press"

DIGITAL = "Digital Logistics"
MEKANIZED = "Mekanized Industry"
HIGH_ENERGY = "High-Energy Grid"
NUCLEAR = "Nuclear Engineering"
POST_NUCLEAR = "Post-Nuclear Megaprojects"

ME_NODE = "CR01 — ME System Basics"
MID_STORAGE_NODE = "CR01 — Improved Digital Chemical Storage"
STORAGE_NODE = "CR01 — Advanced ME Storage"
CORE_NODE = "CR01 — Core Engineering"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    if isinstance(value, dict):
        item_id = value.get("item") or value.get("id")
        return item_id if isinstance(item_id, str) else None
    if not isinstance(value, str):
        return None
    match = _COUNTED_ITEM.fullmatch(value)
    return match.group(1) if match else value.strip()


def _deploy(ingredient: str, machine: str) -> dict[str, str]:
    return {"op": "deploying", "ingredient": ingredient, "machine": machine}


def _press(machine: str) -> dict[str, str]:
    return {"op": "pressing", "machine": machine}


def _merge_unique(*groups: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for entry in group:
            if entry not in seen:
                seen.add(entry)
                result.append(entry)
    return result


def _sequence(
    recipe_id: str,
    *,
    phase: str,
    node: str | None,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    ingredients: list[str],
    deployer: str,
    press: str,
    remove: Iterable[str],
    depends_on: Iterable[str] = (),
) -> dict[str, Any]:
    if not 4 <= len(ingredients) <= 8:
        raise ValueError(
            f"{recipe_id} must have four to eight meaningful deployments; "
            f"got {len(ingredients)}"
        )
    recipe: dict[str, Any] = {
        "id": recipe_id,
        "phase": phase,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": input_item,
        "output": output,
        "loops": 1,
        "steps": [_deploy(item, deployer) for item in ingredients]
        + [_press(press)],
        "remove": list(remove),
        "exclusive_output": True,
    }
    if node is not None:
        recipe["node"] = node
    dependencies = list(depends_on)
    if dependencies:
        recipe["depends_on"] = dependencies
    return recipe


def _ae_cells() -> list[dict[str, Any]]:
    tiers = [
        {
            "tier": "1k",
            "phase": DIGITAL,
            "node": ME_NODE,
            "order": 50,
            "deployer": BRASS_DEPLOYER,
            "press": BRASS_PRESS,
            "item": [
                "ae2:cell_component_1k",
                "ae2:logic_processor",
                "tfmg:copper_wire",
                "tfmg:rubber_sheet",
                "ae2:quartz_glass",
            ],
            "fluid": [
                "ae2:cell_component_1k",
                "create:fluid_pipe",
                "create:fluid_valve",
                "tfmg:rubber_sheet",
                "ae2:quartz_glass",
            ],
        },
        {
            "tier": "4k",
            "phase": MEKANIZED,
            "node": MID_STORAGE_NODE,
            "order": 52,
            "deployer": BRASS_DEPLOYER,
            "press": BRASS_PRESS,
            "item": [
                "ae2:cell_component_4k",
                "ae2:logic_processor",
                "ae2:fluix_smart_cable",
                "tfmg:plastic_sheet",
                "tfmg:capacitor_item",
                "ae2:quartz_glass",
            ],
            "fluid": [
                "ae2:cell_component_4k",
                "create:fluid_pipe",
                "create:fluid_valve",
                "tfmg:rubber_sheet",
                "tfmg:plastic_sheet",
                "ae2:quartz_glass",
            ],
        },
        {
            "tier": "16k",
            "phase": MEKANIZED,
            "node": MID_STORAGE_NODE,
            "order": 54,
            "deployer": BRASS_DEPLOYER,
            "press": BRASS_PRESS,
            "item": [
                "ae2:cell_component_16k",
                "ae2:logic_processor",
                "ae2:fluix_smart_cable",
                "2x tfmg:copper_wire",
                "tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
            "fluid": [
                "ae2:cell_component_16k",
                "tfmg:plastic_pipe",
                "tfmg:plastic_fluid_valve",
                "tfmg:rubber_sheet",
                "tfmg:plastic_sheet",
                "ae2:quartz_vibrant_glass",
            ],
        },
        {
            "tier": "64k",
            "phase": HIGH_ENERGY,
            "node": STORAGE_NODE,
            "order": 90,
            "deployer": RAILWAY_DEPLOYER,
            "press": RAILWAY_PRESS,
            "item": [
                "ae2:cell_component_64k",
                "ae2:engineering_processor",
                "ae2:fluix_smart_cable",
                "2x tfmg:plastic_sheet",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:lithium_charge",
            ],
            "fluid": [
                "ae2:cell_component_64k",
                "tfmg:plastic_pipe",
                "tfmg:plastic_fluid_valve",
                "2x tfmg:rubber_sheet",
                "ae2:quartz_vibrant_glass",
                "tfmg:lithium_charge",
            ],
        },
        {
            "tier": "256k",
            "phase": HIGH_ENERGY,
            "node": STORAGE_NODE,
            "order": 92,
            "deployer": RAILWAY_DEPLOYER,
            "press": RAILWAY_PRESS,
            "item": [
                "ae2:cell_component_256k",
                "ae2:engineering_processor",
                "2x ae2:fluix_smart_cable",
                "2x tfmg:plastic_sheet",
                "tfmg:laminated_magnetic_alloy_block",
                "2x tfmg:lithium_charge",
                "ae2:quartz_vibrant_glass",
            ],
            "fluid": [
                "ae2:cell_component_256k",
                "ae2:engineering_processor",
                "tfmg:steel_pipe",
                "tfmg:steel_fluid_valve",
                "2x tfmg:rubber_sheet",
                "ae2:quartz_vibrant_glass",
                "tfmg:laminated_magnetic_alloy_block",
                "2x tfmg:lithium_charge",
            ],
        },
    ]

    recipes: list[dict[str, Any]] = []
    for spec in tiers:
        tier = str(spec["tier"])
        common = {
            "phase": str(spec["phase"]),
            "node": str(spec["node"]),
            "deployer": str(spec["deployer"]),
            "press": str(spec["press"]),
        }
        recipes.append(
            _sequence(
                f"industrial_colonies:v3_ae2/item_storage_cell_{tier}",
                order=int(spec["order"]),
                comment=(
                    f"Install the {tier} memory plane in its item housing, "
                    "wire an indexed logic bus, insulate the package, and "
                    "press on its quartz service face"
                ),
                input_item="ae2:item_cell_housing",
                output=f"ae2:item_storage_cell_{tier}",
                ingredients=list(spec["item"]),
                remove=[
                    f"ae2:network/cells/item_storage_cell_{tier}",
                    f"ae2:network/cells/item_storage_cell_{tier}_storage",
                ],
                **common,
            )
        )
        recipes.append(
            _sequence(
                f"industrial_colonies:v3_ae2/fluid_storage_cell_{tier}",
                order=int(spec["order"]) + 1,
                comment=(
                    f"Install the {tier} memory plane in its fluid housing, "
                    "plumb a metered valve, seat the rubber seal, and close "
                    "the visible quartz service face"
                ),
                input_item="ae2:fluid_cell_housing",
                output=f"ae2:fluid_storage_cell_{tier}",
                ingredients=list(spec["fluid"]),
                remove=[
                    f"ae2:network/cells/fluid_storage_cell_{tier}",
                    f"ae2:network/cells/fluid_storage_cell_{tier}_storage",
                ],
                **common,
            )
        )
    return recipes


def _mega_cells() -> list[dict[str, Any]]:
    tiers = [
        ("1m", "2x tfmg:plastic_sheet", "tfmg:lithium_charge", "tfmg:magnetic_alloy_sheet", "tfmg:capacitor_item", "tfmg:plastic_fluid_valve"),
        ("4m", "2x tfmg:plastic_sheet", "2x tfmg:lithium_charge", "tfmg:magnetic_alloy_sheet", "ae2:fluix_smart_cable", "tfmg:plastic_fluid_valve"),
        ("16m", "3x tfmg:plastic_sheet", "2x tfmg:lithium_charge", "tfmg:laminated_magnetic_alloy_block", "ae2:engineering_processor", "tfmg:steel_fluid_valve"),
        ("64m", "3x tfmg:plastic_sheet", "3x tfmg:lithium_charge", "tfmg:laminated_magnetic_alloy_block", "ae2:matter_ball", "tfmg:steel_fluid_valve"),
        ("256m", "4x tfmg:plastic_sheet", "4x tfmg:lithium_charge", "tfmg:laminated_magnetic_alloy_block", "allthemodium:vibranium_allthemodium_alloy_ingot", "tfmg:steel_fluid_valve"),
    ]

    recipes: list[dict[str, Any]] = []
    for index, (tier, plastic, lithium, shielding, item_control, fluid_valve) in enumerate(tiers):
        component = f"megacells:cell_component_{tier}"
        core = [
            component,
            "megacells:accumulation_processor",
            "tfmg:n_semiconductor",
            "tfmg:p_semiconductor",
            plastic,
            lithium,
            shielding,
        ]
        recipes.append(
            _sequence(
                f"industrial_colonies:v3_ae2/mega_item_storage_cell_{tier}",
                phase=HIGH_ENERGY,
                node=STORAGE_NODE,
                order=320 + index * 2,
                comment=(
                    f"Populate the {tier} MEGA item housing with complementary "
                    "semiconductors, Accumulation control, lithium buffering, "
                    "magnetic shielding, and an indexed item-bus controller"
                ),
                input_item="megacells:mega_item_cell_housing",
                output=f"megacells:item_storage_cell_{tier}",
                ingredients=[*core, item_control],
                deployer=RAILWAY_DEPLOYER,
                press=RAILWAY_PRESS,
                remove=[
                    f"megacells:cells/standard/item_storage_cell_{tier}",
                    f"megacells:cells/standard/item_storage_cell_{tier}_with_housing",
                ],
            )
        )
        recipes.append(
            _sequence(
                f"industrial_colonies:v3_ae2/mega_fluid_storage_cell_{tier}",
                phase=HIGH_ENERGY,
                node=STORAGE_NODE,
                order=321 + index * 2,
                comment=(
                    f"Populate the {tier} MEGA fluid housing with complementary "
                    "semiconductors, Accumulation control, lithium buffering, "
                    "magnetic shielding, and a pressure-rated fluid valve"
                ),
                input_item="megacells:mega_fluid_cell_housing",
                output=f"megacells:fluid_storage_cell_{tier}",
                ingredients=[*core, fluid_valve],
                deployer=RAILWAY_DEPLOYER,
                press=RAILWAY_PRESS,
                remove=[
                    f"megacells:cells/standard/fluid_storage_cell_{tier}",
                    f"megacells:cells/standard/fluid_storage_cell_{tier}_with_housing",
                ],
            )
        )
    return recipes


def _stress_cells() -> list[dict[str, Any]]:
    specs = [
        (
            "1k", HIGH_ENERGY, STORAGE_NODE, 640,
            "appliedcreate:andesite_stress_cell_housing",
            BRASS_DEPLOYER, BRASS_PRESS,
            [
                "appliedcreate:stress_storage_component_1k",
                "create:shaft",
                "appliedcreate:stress_processor",
                "create:stressometer",
                "tfmg:rubber_sheet",
            ],
            [
                "industrial_colonies:v3_ae2/andesite_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_1k",
            ],
        ),
        (
            "4k", HIGH_ENERGY, STORAGE_NODE, 641,
            "appliedcreate:andesite_stress_cell_housing",
            BRASS_DEPLOYER, BRASS_PRESS,
            [
                "appliedcreate:stress_storage_component_4k",
                "create:cogwheel",
                "appliedcreate:stress_processor",
                "create:stressometer",
                "tfmg:copper_wire",
            ],
            [
                "industrial_colonies:v3_ae2/andesite_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_4k",
            ],
        ),
        (
            "16k", HIGH_ENERGY, STORAGE_NODE, 642,
            "appliedcreate:andesite_stress_cell_housing",
            BRASS_DEPLOYER, BRASS_PRESS,
            [
                "appliedcreate:stress_storage_component_16k",
                "create:precision_mechanism",
                "appliedcreate:stress_processor",
                "create:stressometer",
                "tfmg:capacitor_item",
                "tfmg:plastic_sheet",
            ],
            [
                "industrial_colonies:v3_ae2/andesite_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_16k",
            ],
        ),
        (
            "64k", HIGH_ENERGY, STORAGE_NODE, 643,
            "appliedcreate:andesite_stress_cell_housing",
            WEATHERED_DEPLOYER, WEATHERED_PRESS,
            [
                "appliedcreate:stress_storage_component_64k",
                "create:precision_mechanism",
                "appliedcreate:advanced_stress_processor",
                "create:stressometer",
                "tfmg:magnetic_alloy_sheet",
                "tfmg:plastic_sheet",
            ],
            [
                "industrial_colonies:v3_ae2/andesite_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_64k",
            ],
        ),
        (
            "256k", HIGH_ENERGY, STORAGE_NODE, 644,
            "appliedcreate:andesite_stress_cell_housing",
            WEATHERED_DEPLOYER, WEATHERED_PRESS,
            [
                "appliedcreate:stress_storage_component_256k",
                "create:rotation_speed_controller",
                "appliedcreate:advanced_stress_processor",
                "create:stressometer",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:plastic_sheet",
                "tfmg:lithium_charge",
            ],
            [
                "industrial_colonies:v3_ae2/andesite_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_256k",
            ],
        ),
        (
            "1m", HIGH_ENERGY, STORAGE_NODE, 645,
            "appliedcreate:brass_stress_cell_housing",
            WEATHERED_DEPLOYER, WEATHERED_PRESS,
            [
                "appliedcreate:stress_storage_component_1m",
                "create_connected:kinetic_bridge",
                "appliedcreate:advanced_stress_processor",
                "create:rotation_speed_controller",
                "tfmg:laminated_magnetic_alloy_block",
                "tfmg:plastic_sheet",
                "tfmg:lithium_charge",
            ],
            [
                "industrial_colonies:v3_ae2/brass_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_1m",
            ],
        ),
        (
            "4m", NUCLEAR, CORE_NODE, 720,
            "appliedcreate:brass_stress_cell_housing",
            RADIANCE_DEPLOYER, RADIANCE_PRESS,
            [
                "appliedcreate:stress_storage_component_4m",
                "create_connected:kinetic_bridge",
                "appliedcreate:advanced_stress_processor",
                "appliedcreate:kinetic_energy_acceptor",
                "create:rotation_speed_controller",
                "create:refined_radiance",
                "tfmg:plastic_sheet",
            ],
            [
                "industrial_colonies:v3_ae2/brass_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_4m",
            ],
        ),
        (
            "16m", NUCLEAR, CORE_NODE, 721,
            "appliedcreate:brass_stress_cell_housing",
            RADIANCE_DEPLOYER, RADIANCE_PRESS,
            [
                "appliedcreate:stress_storage_component_16m",
                "create_connected:kinetic_bridge",
                "appliedcreate:advanced_stress_processor",
                "appliedcreate:kinetic_energy_acceptor",
                "create:rotation_speed_controller",
                "create:refined_radiance",
                "ae2:matter_ball",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            [
                "industrial_colonies:v3_ae2/brass_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_16m",
            ],
        ),
        (
            "64m", NUCLEAR, CORE_NODE, 722,
            "appliedcreate:brass_stress_cell_housing",
            RADIANCE_DEPLOYER, RADIANCE_PRESS,
            [
                "appliedcreate:stress_storage_component_64m",
                "create_connected:kinetic_bridge",
                "appliedcreate:advanced_stress_processor",
                "appliedcreate:kinetic_energy_acceptor",
                "create:rotation_speed_controller",
                "2x create:refined_radiance",
                "ae2:matter_ball",
                "tfmg:laminated_magnetic_alloy_block",
            ],
            [
                "industrial_colonies:v3_ae2/brass_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_64m",
            ],
        ),
        (
            "256m", POST_NUCLEAR, None, 820,
            "appliedcreate:brass_stress_cell_housing",
            RADIANCE_DEPLOYER, RADIANCE_PRESS,
            [
                "appliedcreate:stress_storage_component_256m",
                "create_connected:kinetic_bridge",
                "appliedcreate:advanced_stress_processor",
                "appliedcreate:kinetic_energy_acceptor",
                "create:rotation_speed_controller",
                "create:refined_radiance_casing",
                "allthemodium:unobtainium_vibranium_alloy_ingot",
                "ae2:matter_ball",
            ],
            [
                "industrial_colonies:v3_ae2/brass_stress_cell_housing",
                "industrial_colonies:appliedcreate/stress_storage_component_256m",
            ],
        ),
    ]

    recipes: list[dict[str, Any]] = []
    for (
        tier,
        phase,
        node,
        order,
        housing,
        deployer,
        press,
        ingredients,
        dependencies,
    ) in specs:
        recipes.append(
            _sequence(
                f"industrial_colonies:appliedcreate/stress_storage_cell_{tier}",
                phase=phase,
                node=node,
                order=order,
                comment=(
                    f"Install the {tier} stress matrix in its braced housing, "
                    "instrument the kinetic load path, add tier-appropriate "
                    "stress control, and press the service enclosure closed"
                ),
                input_item=housing,
                output=f"appliedcreate:stress_storage_cell_{tier}",
                ingredients=ingredients,
                deployer=deployer,
                press=press,
                remove=[f"appliedcreate:stress_storage_cell_{tier}"],
                depends_on=dependencies,
            )
        )
    return recipes


def replacements() -> list[dict[str, Any]]:
    """Return fresh recipe dictionaries for all thirty finished cells."""

    recipes = [*_ae_cells(), *_mega_cells(), *_stress_cells()]
    outputs = [_item_id(recipe["output"]) for recipe in recipes]
    if len(recipes) != 30 or len(set(outputs)) != 30:
        raise ValueError(
            f"storage-cell pass must own exactly 30 unique outputs; "
            f"got {len(recipes)} recipes / {len(set(outputs))} outputs"
        )
    if any(recipe.get("type") != "sequenced_assembly" for recipe in recipes):
        raise ValueError("every finished storage cell must be sequenced assembly")
    return recipes


def apply(data: dict[str, Any]) -> None:
    """Replace only completed-cell outputs while preserving removal ownership."""

    additions = replacements()
    claimed = {_item_id(recipe["output"]) for recipe in additions}
    new_id_by_output = {
        _item_id(recipe["output"]): str(recipe["id"]) for recipe in additions
    }
    recipe_ids = {str(recipe["id"]) for recipe in additions}

    old_removals: dict[str, list[str]] = {
        output: [] for output in claimed if output is not None
    }
    old_dependencies: dict[str, list[str]] = {
        output: [] for output in claimed if output is not None
    }
    dependency_redirects: dict[str, str] = {}
    survivors: list[dict[str, Any]] = []

    for recipe in data.get("recipes", []):
        output = _item_id(recipe.get("output"))
        if output in claimed or recipe.get("id") in recipe_ids:
            if output in old_removals:
                old_removals[output] = _merge_unique(
                    old_removals[output], recipe.get("remove", [])
                )
                old_dependencies[output] = _merge_unique(
                    old_dependencies[output], recipe.get("depends_on", [])
                )
            old_id = recipe.get("id")
            new_id = new_id_by_output.get(output)
            if isinstance(old_id, str) and isinstance(new_id, str):
                dependency_redirects[old_id] = new_id
            continue
        survivors.append(recipe)

    for recipe in additions:
        output = _item_id(recipe["output"])
        recipe["remove"] = _merge_unique(
            recipe.get("remove", []), old_removals.get(output or "", [])
        )
        preserved_dependencies = [
            dependency_redirects.get(entry, entry)
            for entry in old_dependencies.get(output or "", [])
        ]
        dependencies = _merge_unique(
            recipe.get("depends_on", []), preserved_dependencies
        )
        if dependencies:
            recipe["depends_on"] = dependencies

    claimed_removals = {
        removal for recipe in additions for removal in recipe.get("remove", [])
    }
    for recipe in survivors:
        output = _item_id(recipe.get("output"))
        if output in claimed:
            raise ValueError(
                f"finished storage-cell output is still multiply owned: {output}"
            )
        overlap = claimed_removals.intersection(recipe.get("remove", []))
        if overlap:
            raise ValueError(
                f"stock storage-cell removals have another managed owner in "
                f"{recipe.get('id')}: {sorted(overlap)}"
            )

    global_overlap = claimed_removals.intersection(
        data.get("additional_removals", [])
    )
    if global_overlap:
        raise ValueError(
            "stock storage-cell removals are also globally owned: "
            f"{sorted(global_overlap)}"
        )

    data["recipes"] = [*survivors, *additions]
    for recipe in data["recipes"]:
        dependencies = recipe.get("depends_on", [])
        if dependencies:
            recipe["depends_on"] = _merge_unique(
                dependency_redirects.get(entry, entry) for entry in dependencies
            )

    data["preserve_recipe_ids"] = [
        entry
        for entry in data.get("preserve_recipe_ids", [])
        if entry not in claimed_removals
    ]
    data["exclude_outputs"] = [
        entry for entry in data.get("exclude_outputs", []) if entry not in claimed
    ]

    final_outputs = [_item_id(recipe.get("output")) for recipe in data["recipes"]]
    for output in claimed:
        if output is not None and final_outputs.count(output) != 1:
            raise ValueError(
                f"finished storage-cell output {output} appears "
                f"{final_outputs.count(output)} times after replacement"
            )


def _recipe_resources(recipe: dict[str, Any]) -> set[str]:
    values: list[Any] = [
        recipe.get("input"),
        recipe.get("transitional"),
        recipe.get("output"),
    ]
    for step in recipe.get("steps", []):
        values.extend([step.get("ingredient"), step.get("machine")])
    return {
        item
        for value in values
        if (item := _item_id(value)) is not None
    }


def validate_catalog(catalog_sqlite: str | Path) -> dict[str, Any]:
    """Require every concrete item and exact stock recipe ID in the catalog."""

    database = Path(catalog_sqlite)
    if not database.is_file():
        raise FileNotFoundError(database)

    recipes = replacements()
    resources = sorted(set().union(*(_recipe_resources(r) for r in recipes)))
    removals = sorted({entry for r in recipes for entry in r.get("remove", [])})

    with sqlite3.connect(database) as connection:
        item_placeholders = ",".join("?" for _ in resources)
        recipe_placeholders = ",".join("?" for _ in removals)
        known_items = {
            row[0]
            for row in connection.execute(
                f"SELECT item_id FROM items WHERE item_id IN ({item_placeholders})",
                resources,
            )
        }
        known_items.update(
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT resource_id FROM recipe_refs "
                f"WHERE resource_id IN ({item_placeholders})",
                resources,
            )
        )
        known_recipes = {
            row[0]
            for row in connection.execute(
                "SELECT recipe_id FROM recipes "
                f"WHERE recipe_id IN ({recipe_placeholders})",
                removals,
            )
        }

    missing_items = sorted(set(resources) - known_items)
    missing_removals = sorted(set(removals) - known_recipes)
    if missing_items:
        raise ValueError(
            f"storage-cell recipes reference missing items: {missing_items}"
        )
    if missing_removals:
        raise ValueError(
            "storage-cell recipes reference missing exact stock recipe IDs: "
            f"{missing_removals}"
        )
    return {
        "replacement_count": len(recipes),
        "resource_count": len(resources),
        "removal_count": len(removals),
        "missing_items": missing_items,
        "missing_removal_ids": missing_removals,
    }


__all__ = ["apply", "replacements", "validate_catalog"]
