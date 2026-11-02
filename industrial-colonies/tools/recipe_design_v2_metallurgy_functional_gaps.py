"""Close the remaining functional Create Metallurgy/Modern Foundry bypasses.

This is a pure, idempotent seed transform.  It deliberately leaves coherent
source-owned processes alone: the Industrial Crucible and transfer ladle are
already manufactured sequences, graphite molds have a press-and-machining
route, the sandpaper belt is a sensible consumable, and both Modern Foundry
controllers are cast in their own foundry hardware.

The recipes below are limited to capability-bearing endpoints that otherwise
skip the pack's TFMG-first heavy-industry chain.  Every replacement is an
upgrade of earlier casting or pressure-rated hardware and uses the Railway
manufacturing environment appropriate to Steel & Petroleum production.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


_REPLACEMENTS: tuple[dict[str, Any], ...] = (
    {
        "id": "industrial_colonies:foundry_routes/create_metallurgy_casting_table",
        "node": "CR01 — Advanced Metallurgy",
        "phase": "Steel & Petroleum",
        "order": 120,
        "type": "compacting",
        "comment": (
            "Railway-press a proven TFMG casting basin into a refractory "
            "precision table with a graphite form, cast-iron support, and "
            "service screw"
        ),
        "machine": "createcasing:railway_press",
        "inputs": [
            "tfmg:casting_basin",
            "2x tfmg:fireproof_bricks",
            "create:depot",
            "tfmg:cast_iron_ingot",
            "tfmg:screw",
            "createmetallurgy:graphite_ingot_mold",
        ],
        "output": "createmetallurgy:casting_table",
        "remove": ["createmetallurgy:crafting/content/casting_table"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:steelworks/fireproof_bricks"],
    },
    {
        "id": "industrial_colonies:foundry_routes/create_metallurgy_casting_basin",
        "node": "CR01 — Advanced Metallurgy",
        "phase": "Steel & Petroleum",
        "order": 130,
        "type": "compacting",
        "comment": (
            "Reinforce a TFMG casting basin with a cast-iron frame, refractory "
            "lining, and heavy bottom plate for block-scale pours"
        ),
        "machine": "createcasing:railway_press",
        "inputs": [
            "tfmg:casting_basin",
            "2x tfmg:fireproof_bricks",
            "tfmg:cast_iron_frame",
            "tfmg:heavy_plate",
            "tfmg:screw",
        ],
        "output": "createmetallurgy:casting_basin",
        "remove": ["createmetallurgy:crafting/content/casting_basin"],
        "exclusive_output": True,
        "depends_on": ["industrial_colonies:steelworks/fireproof_bricks"],
    },
    {
        "id": "industrial_colonies:foundry_routes/modern_scorched_basin",
        "node": "CR01 — Exotic Metallurgy",
        "phase": "Steel & Petroleum",
        "order": 170,
        "type": "compacting",
        "comment": (
            "Upgrade the refractory block-casting line into a high-temperature "
            "Scorched Basin around its gold support platform"
        ),
        "machine": "createcasing:railway_press",
        "inputs": [
            "createmetallurgy:casting_basin",
            "4x modernfoundry:scorched_brick",
            "modernfoundry:gold_platform",
            "tfmg:heavy_plate",
            "tfmg:steel_mechanism",
        ],
        "output": "modernfoundry:scorched_basin",
        "remove": ["modernfoundry:smeltery/scorched/basin"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:foundry_routes/create_metallurgy_casting_basin"
        ],
    },
    {
        "id": "industrial_colonies:foundry_routes/modern_scorched_drain",
        "node": "CR01 — Exotic Metallurgy",
        "phase": "Steel & Petroleum",
        "order": 180,
        "type": "compacting",
        "comment": (
            "Build the Scorched Drain as a refractory fluid interface around "
            "TFMG steel pipework, a pressure buffer, and obsidian sight panes"
        ),
        "machine": "createcasing:railway_press",
        "inputs": [
            "4x modernfoundry:scorched_brick",
            "2x modernfoundry:obsidian_pane",
            "2x tfmg:steel_pipe",
            "tfmg:steel_fluid_tank",
            "tfmg:screw",
        ],
        "output": "modernfoundry:scorched_drain",
        "remove": [
            "modernfoundry:smeltery/scorched/drain",
            "modernfoundry:smeltery/scorched/drain_retextured",
        ],
        "exclusive_output": True,
        "depends_on": [],
    },
    {
        "id": "industrial_colonies:foundry_routes/modern_scorched_table",
        "node": "CR01 — Exotic Metallurgy",
        "phase": "Steel & Petroleum",
        "order": 190,
        "type": "compacting",
        "comment": (
            "Upgrade the precision casting table with a Scorched refractory "
            "shell, replaceable gold rails, and a heavy service plate"
        ),
        "machine": "createcasing:railway_press",
        "inputs": [
            "createmetallurgy:casting_table",
            "4x modernfoundry:scorched_brick",
            "modernfoundry:gold_bars",
            "tfmg:heavy_plate",
            "tfmg:screw",
        ],
        "output": "modernfoundry:scorched_table",
        "remove": ["modernfoundry:smeltery/scorched/table"],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:foundry_routes/create_metallurgy_casting_table"
        ],
    },
)


def _recipes(data: dict[str, Any]) -> list[dict[str, Any]]:
    recipes = data.setdefault("recipes", [])
    if not isinstance(recipes, list):
        raise TypeError("managed recipe seed field 'recipes' must be a list")
    return recipes


def _upsert(data: dict[str, Any], replacement: dict[str, Any]) -> None:
    recipes = _recipes(data)
    recipe_id = replacement["id"]
    for index, recipe in enumerate(recipes):
        if isinstance(recipe, dict) and recipe.get("id") == recipe_id:
            recipes[index] = deepcopy(replacement)
            return
    recipes.append(deepcopy(replacement))


def _remove_values(data: dict[str, Any], field: str, values: set[str]) -> None:
    current = data.get(field)
    if current is None:
        return
    if not isinstance(current, list):
        raise TypeError(f"managed recipe seed field {field!r} must be a list")
    data[field] = [value for value in current if value not in values]


def apply(data: dict[str, Any]) -> None:
    """Apply remaining endpoints; preserve the user-restored starter melter."""

    # September 21 explicit user correction: the starter Seared Melter uses its
    # native shaped recipe. Retire stale seeds as well as avoiding new overrides.
    data["recipes"] = [recipe for recipe in _recipes(data)
                       if not isinstance(recipe, dict)
                       or recipe.get("id") != "industrial_colonies:foundry_routes/modern_seared_melter"]
    for field, value in (("preserve_recipe_ids", "modernfoundry:smeltery/seared/melter"),
                         ("exclude_outputs", "modernfoundry:seared_melter")):
        values = data.setdefault(field, [])
        if not isinstance(values, list):
            raise TypeError(f"managed recipe seed field {field!r} must be a list")
        if value not in values:
            values.append(value)

    for replacement in _REPLACEMENTS:
        _upsert(data, replacement)

    stock_ids = {
        recipe_id
        for replacement in _REPLACEMENTS
        for recipe_id in replacement.get("remove", [])
    }
    outputs = {
        replacement["output"]
        for replacement in _REPLACEMENTS
        if isinstance(replacement.get("output"), str)
    }

    # recipe_design_v2_tfmg intentionally restores ordinary source recipes.
    # This late, narrowly-scoped transform must remove only the exact source
    # endpoints it replaces and take them back out of automatic-exclusion.
    _remove_values(data, "preserve_recipe_ids", stock_ids)
    _remove_values(data, "exclude_outputs", outputs)


if __name__ == "__main__":
    raise SystemExit(
        "This module is a seed transform; import it and call apply(data)."
    )
