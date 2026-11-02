# Mekanism Transmission Foundation

This slice establishes Mekanism's five **basic** transmitter families as the
local distribution layer of Modular Machinery. It does not replace Create
trains or Electro Energetics overhead lines: trains remain the bulk terrestrial
logistics system, while Electro Energetics remains the long-span electrical
grid.

## Basic transmitter recipes

Each managed recipe produces eight segments, matching the useful stock batch
size. The cost is therefore paid per installed network run without making
factory-scale construction tedious.

| Output | Managed recipe | Manufacturing purpose |
| --- | --- | --- |
| `mekanism:basic_universal_cable` | `industrial_colonies:mekanism/transmission/basic_universal_cable` | TFMG rubber/cable tube around Electro Energetics terminations, joined with infused alloy |
| `mekanism:basic_logistical_transporter` | `industrial_colonies:mekanism/transmission/basic_logistical_transporter` | Create depots/chutes converted into controlled item transport with TFMG mechanisms and first-tier Mekanism logic |
| `mekanism:basic_mechanical_pipe` | `industrial_colonies:mekanism/transmission/basic_mechanical_pipe` | TFMG cast-iron plumbing integrated with Create fluid pipes and a mechanical pump |
| `mekanism:basic_pressurized_tube` | `industrial_colonies:mekanism/transmission/basic_pressurized_tube` | TFMG steel housings, inspection glass, rubber seals, and infused-alloy joints |
| `mekanism:basic_thermodynamic_conductor` | `industrial_colonies:mekanism/transmission/basic_thermodynamic_conductor` | Copper plates and grid-grade wire jacketed by TFMG cast-iron pipe |

All exact ingredients are assigned to Mechanical Foundations, Steel &
Petroleum, Electrical Manufacturing, or the first Mekanized Industry step.
Nothing requires an advanced circuit, AE processor, upgraded Mekanism alloy, or
another transmitter made by the same recipe. This keeps the five recipes
reachable immediately after the pack's existing Infusion Technology and
Modular Machinery foundation is built.

The five stock recipe IDs are removed exactly. No output-, input-, or
namespace-wide removal is used, and later transmitter upgrades continue to
consume these basic segments normally.

## Infinite source cells

The following two ExtendedAE recipes are retired exactly:

- `extendedae:cobblestone_cell`
- `extendedae:water_cell`

Their outputs generate or expose effectively unlimited cobblestone and water
from one compact ME cell. That would bypass the intended quarry/compression and
fluid-pumping infrastructure, especially the compressed-resource megaprojects.
Ordinary AE2/ExtendedAE storage remains available; only these two infinite
source recipes are disabled.

## Verification

Run:

```text
python tools/validate_mekanism_transmission_foundation.py
```

The validator locks the installed stock-producer evidence, exact replacement
IDs, eight-segment yields, cross-mod patterns, prerequisite phases, compiled
KJSGen slots, exact removal cards, and absence of managed infinite-cell
producers. Regression tests additionally prove that a missing infinite-cell
removal or a future-tier transmitter ingredient is rejected.
