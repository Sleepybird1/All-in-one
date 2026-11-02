# Stock Utility Restoration audit

Status: **implemented in the authoritative seed**.

## Decision

Retire the 56 automatic recipes classified as `runtime_artifact_leave_stock`
in `AUTOMATIC_RECIPE_QUALITY_AUDIT.plan.json`. Add each output to the managed
seed's `exclude_outputs` set and preserve every one of its 77 exact installed
producer IDs. This restores the installed recipe rather than inventing a
second recipe or deleting the item.

These are bulk closures, reversible storage forms, cable/connector
conversions, tier-installer utilities, compatibility ports, and other final
forms whose real progression cost belongs in their prerequisite component or
machine. Charging another generic 5x5 A/B ring per cable, storage cell, glass
variant, or reactor port does not create a factory; it only adds repetitive
manual assembly.

## Scope

| Phase | Automatic owners retired |
|---|---:|
| Steel & Petroleum | 2 |
| Electrical Manufacturing | 3 |
| Digital Logistics | 7 |
| Mekanized Industry | 8 |
| High-Energy Grid | 19 |
| Nuclear Engineering | 17 |
| **Total** | **56** |

The exact output, automatic owner, node, phase, rationale, and full source-ID
set are recorded in `STOCK_UTILITY_RESTORATION_AUDIT.patch.json`.

## Safety contract

- Preserve all 77 exact producer IDs; do not use namespace or output-wide
  removals.
- Retire only the 56 listed `industrial_colonies:auto/...` owners.
- Do not remove assignments. The assignment map remains useful documentation
  and FTB Quests guidance even though it no longer authorizes recipes.
- Keep tier installers craftable. The companion JAR's exact upgradeable-block
  blacklist, not recipe deletion, protects the managed Factory, cube, and
  transmitter ladders.
- Keep uranium block/nugget packing reversible. This does not create usable
  uranium; the enrichment and fuel-production chain remains the production
  boundary.
- Keep AE2/AppMek cell closures and recovery recipes stock-scalable. Their
  manufactured housings, processors, and storage components carry the cost.
- Keep Big Reactors glass, ports, and compatibility adapters stock-scalable.
  Their casing/controller/fuel prerequisites carry the nuclear cost.

## Integration boundary

Integration must union, not replace, the existing `exclude_outputs` and
`preserve_recipe_ids` arrays. After rebuilding, every listed automatic owner
must be absent, every listed source recipe must remain unremoved, the managed
dependency graph must be acyclic, and all canonical fuel/material validators
must still pass.

## Implemented result

The seed now contains all 56 reviewed outputs in `exclude_outputs` and all 77
reviewed source IDs in `preserve_recipe_ids`. Sixty-five preserve IDs were new;
twelve AE2/AppMek recovery routes were already protected. No replacement
recipe, assignment change, family owner, or source override was added.

An isolated rebuild produced 329 managed recipes, including 86 remaining
automatic owners, 397 compiled KJSGen cards, 661 exact removals, 33 documented
skips, and zero dependency warnings. All 56 targeted automatic owners were
absent and none of the 77 preserved stock recipes appeared in the removal set.
