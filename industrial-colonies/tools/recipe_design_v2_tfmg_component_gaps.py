"""Close proven bypasses in TFMG's otherwise sound component pipeline.

TFMG already gives its reusable electrical materials meaningful factory
processes: magnetic alloy is heated and mixed, magnets are polarized, coils
and resistors are wound from charged spools, plastic is polymerized in a vat
and cast, and rubber is vulcanized in a heated vat.  Those stock recipes are
intentionally not copied into the managed recipe set.

The one audited exception is the alternate unfinished-resistor recipe which
accepts a vanilla slime ball in place of a TFMG plastic sheet.  That route
skips the pack's petrochemical and casting infrastructure for a component used
throughout the electrical line.  Removing only that alternate recipe leaves
TFMG's original plastic-bodied resistor and winding process intact.

Importing this module has no filesystem side effects.  ``apply`` is
idempotent and mutates only the supplied seed dictionary.
"""

from __future__ import annotations

from typing import Any


_SLIME_RESISTOR_BYPASS = "tfmg:crafting/materials/unfinished_resistorfrom_slime"


def _require_list(data: dict[str, Any], field: str) -> list[Any]:
    value = data.setdefault(field, [])
    if not isinstance(value, list):
        raise TypeError(f"managed recipe seed field {field!r} must be a list")
    return value


def apply(data: dict[str, Any]) -> None:
    """Retire the slime-bodied resistor bypass without copying stock recipes."""

    additional_removals = _require_list(data, "additional_removals")
    preserve_recipe_ids = _require_list(data, "preserve_recipe_ids")

    # A recipe cannot be both preserved and removed.  Keep the correction
    # deterministic even if the module is applied to an older seed revision.
    preserve_recipe_ids[:] = [
        recipe_id
        for recipe_id in preserve_recipe_ids
        if recipe_id != _SLIME_RESISTOR_BYPASS
    ]

    if _SLIME_RESISTOR_BYPASS not in additional_removals:
        additional_removals.append(_SLIME_RESISTOR_BYPASS)

