#!/usr/bin/env python3
"""Restore the late quantum component without restoring AE2 teleportation.

The two stock explosion transforms for Quantum Entangled Singularities are
retired alongside AE2's Quantum Link/Ring because those blocks bypass the
pack's physical planetary logistics.  Four Interstellar Escape assemblies
still require the component as a field reference, however, and therefore need
one controlled manufacturing route.  This transform creates the entangled
pair directly on the Refined Radiance line while leaving both bridge blocks
and both cheap explosion transforms disabled.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


RECIPE_ID = "industrial_colonies:interstellar/quantum_entangled_pair"
OUTPUT = "ae2:quantum_entangled_singularity"
STOCK_TRANSFORMS = {
    "ae2:transform/entangled_singularity",
    "ae2:transform/entangled_singularity_from_pearl",
}


def _recipe() -> dict[str, Any]:
    return {
        "id": RECIPE_ID,
        "phase": "Interstellar Escape",
        "order": 350,
        "type": "sequenced_assembly",
        "comment": (
            "Manufacture a matched entangled pair around an AE2 Singularity: "
            "quantum logic defines the state, infused dust and a Moon Crystal "
            "carry the field, antimatter supplies the excitation, and a high-"
            "voltage capacitor stabilizes the Radiance-line package"
        ),
        "input": "ae2:singularity",
        "transitional": "ae2:singularity",
        "output": "2x ae2:quantum_entangled_singularity",
        "loops": 1,
        "steps": [
            {
                "op": "deploying",
                "ingredient": "advanced_ae:quantum_processor",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "advanced_ae:quantum_infused_dust",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "cosmowarp:moon_crystal",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "mekanism:pellet_antimatter",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {
                "op": "deploying",
                "ingredient": "electroenergetics:high_voltage_capacitor",
                "machine": "createcasing:refined_radiance_deployer",
            },
            {
                "op": "pressing",
                "machine": "createcasing:refined_radiance_press",
            },
        ],
        "remove": sorted(STOCK_TRANSFORMS),
        "exclusive_output": True,
        "depends_on": [
            "industrial_colonies:advanced_ae_coverage/quantum_processor",
            "industrial_colonies:extreme_grid/high_voltage_capacitor",
        ],
    }


def apply(data: dict[str, Any]) -> None:
    """Add the sole manufactured entangled-pair route idempotently."""

    recipes = data.setdefault("recipes", [])
    if not isinstance(recipes, list):
        raise TypeError("managed seed field 'recipes' must be a list")

    for existing in recipes:
        if not isinstance(existing, dict):
            raise TypeError("managed recipe entries must be objects")
        if existing.get("id") == RECIPE_ID:
            continue
        raw_output = existing.get("output")
        if isinstance(raw_output, str) and raw_output.removeprefix("2x ") == OUTPUT:
            raise ValueError(
                f"quantum entangled singularity is already managed by {existing.get('id')}"
            )

    matches = [
        index
        for index, existing in enumerate(recipes)
        if isinstance(existing, dict) and existing.get("id") == RECIPE_ID
    ]
    if len(matches) > 1:
        raise ValueError(f"managed recipe is duplicated: {RECIPE_ID}")
    replacement = _recipe()
    if matches:
        recipes[matches[0]] = deepcopy(replacement)
    else:
        recipes.append(deepcopy(replacement))

    # The new recipe owns the exact removals.  Keep the bridge component out
    # of the retired-output guard, but do not disturb the retired Link/Ring.
    additional = data.setdefault("additional_removals", [])
    additional[:] = [value for value in additional if value not in STOCK_TRANSFORMS]
    preserves = data.setdefault("preserve_recipe_ids", [])
    preserves[:] = [value for value in preserves if value not in STOCK_TRANSFORMS]
    excludes = data.setdefault("exclude_outputs", [])
    excludes[:] = [value for value in excludes if value != OUTPUT]

