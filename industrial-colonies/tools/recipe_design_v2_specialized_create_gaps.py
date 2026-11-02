"""Close the one proven acquisition gap in the smaller installed Create add-ons.

The installed versions were audited from their JAR recipes and registry/lang
resources, then compared with the current recipe-v2 seed and static catalog.
Only Create: Dragons Plus' Fluid Hatch needs a replacement: the block is a
real manual fluid-container interface, is consumed by the managed Experience
Hatch recipe, and its source route is only a shapeless Item Drain plus one
copper ingot.  The replacement remains a small native-Create assembly rather
than turning a service fitting into a late-game machine.

Deliberate non-changes:

* Dragons Plus fragile impact tanks already have readable tank/payload recipes;
  its dye fluids, fan catalysts, fluid buckets, and template duplication are
  utilities or state/conversion content rather than factory-machine gates.
* Create: Factory contains food production and coloured fluid jars.  The jar
  shells are already physically shaped and the consumables are not tech gates.
* Create: Ultimate Factory 2.2.4 registers recipes, not new functional blocks.
  Its coal-to-diamond and nether-brick-to-scrap processes are explicitly
  protected factory routes in the project's bypass-retirement contract; the
  remaining transformations are resource processes, not acquisition recipes
  for factory hardware.
* Create Low-Heated has one functional block, the Basic Burner, which is
  already owned by ``recipe_design_v2_lowheat``.

``apply`` is pure with respect to the filesystem, idempotent, and mutates only
the supplied seed dictionary.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Mapping


RECIPE_ID = "industrial_colonies:specialized_create/dragons_fluid_hatch"
OUTPUT = "create_dragons_plus:fluid_hatch"
STOCK_RECIPE = "create_dragons_plus:crafting/fluid_hatch"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.strip()
    counted = _COUNTED_ITEM.fullmatch(raw)
    return counted.group(1) if counted else raw


def _recipe() -> dict[str, Any]:
    return {
        "id": RECIPE_ID,
        "node": "CR01 — Steam Power",
        "phase": "Steam & Brass",
        "order": 64,
        "type": "sequenced_assembly",
        "comment": (
            "Convert a proven Item Drain into a hand-service tank hatch by "
            "adding a pipe neck, formed copper face, and manual valve lever on "
            "the native mechanical line"
        ),
        "input": "create:item_drain",
        "transitional": "create:item_drain",
        "output": OUTPUT,
        "loops": 1,
        "steps": [
            {
                "op": "deploying",
                "ingredient": "create:fluid_pipe",
                "machine": "create:deployer",
            },
            {
                "op": "deploying",
                "ingredient": "create:copper_sheet",
                "machine": "create:deployer",
            },
            {
                "op": "deploying",
                "ingredient": "minecraft:lever",
                "machine": "create:deployer",
            },
            {"op": "pressing", "machine": "create:mechanical_press"},
        ],
        "remove": [STOCK_RECIPE],
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:brass/deployer",
            "industrial_colonies:create_core/item_drain",
        ],
    }


def _output_id(recipe: Mapping[str, Any]) -> str | None:
    return _item_id(recipe.get("output"))


def _remove_values(data: dict[str, Any], field: str, values: set[str]) -> None:
    current = data.get(field)
    if current is None:
        return
    if not isinstance(current, list):
        raise TypeError(f"managed recipe seed field {field!r} must be a list")
    data[field] = [value for value in current if value not in values]


def apply(data: dict[str, Any]) -> None:
    """Upsert the Fluid Hatch replacement without touching unrelated routes."""

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("managed recipe seed field 'recipes' must be a list")

    owned = [
        index
        for index, recipe in enumerate(recipes)
        if isinstance(recipe, Mapping) and recipe.get("id") == RECIPE_ID
    ]
    if len(owned) > 1:
        raise ValueError(f"managed recipe is duplicated: {RECIPE_ID}")

    foreign = [
        str(recipe.get("id"))
        for recipe in recipes
        if isinstance(recipe, Mapping)
        and recipe.get("id") != RECIPE_ID
        and _output_id(recipe) == OUTPUT
    ]
    if foreign:
        raise ValueError(
            f"{OUTPUT} already has a different managed producer: {sorted(foreign)}"
        )

    replacement = _recipe()
    if owned:
        recipes[owned[0]] = deepcopy(replacement)
    else:
        recipes.append(deepcopy(replacement))

    _remove_values(data, "exclude_outputs", {OUTPUT})
    _remove_values(data, "preserve_recipe_ids", {STOCK_RECIPE})


if __name__ == "__main__":
    raise SystemExit(
        "This module is a seed transform; import it and call apply(data)."
    )
