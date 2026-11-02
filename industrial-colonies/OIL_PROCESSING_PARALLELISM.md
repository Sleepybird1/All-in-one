# Oil Processing and Blast Furnace parallelism

## Progression decision

The authoritative Draw.io remains unchanged. `CR01 — Oil processing` and
`CR01 — Blast Furnace` are parallel children of `CR01 — The Steel Age`, so the
first TFMG crude-oil extraction rig must not consume steel made by the Blast
Furnace branch.

The twelve TFMG recipes needed for prospecting, constructing both pumpjack
sizes, and handling oil in the field are source-owned entries in
`progression/managed_recipe_overhaul.seed.json`. The replacements use TFMG cast
iron and Create brass/precision parts. They contain no steel, heavy machinery
casing, heavy plate, rebar, aluminum, or steel industrial pipe.

`industrial_oil_field_construction.js` is now only a migration marker. The
existing authored Engine Controller, Simple Large Engine, and Large Engine
recipes remain unchanged; the broader refinery and engine progression is
documented in `PETROLEUM_ENGINE_PROGRESSION.md`.

## Functional pumpjack pipe

Changing only the four obvious machine recipes is insufficient. TFMG's
`PumpjackBaseBlockEntity` follows the `tfmg:industrial_pipe` block tag from the
pumpjack base down to an oil deposit. In the installed TFMG 1.2.0 data, that tag
contains only the steel industrial pipe and its concrete-encased variant.

The companion data pack merges `tfmg:cast_iron_pipe` into that block tag via
`src/main/resources/data/tfmg/tags/block/industrial_pipe.json`. This is a native
TFMG fluid pipe with vertical connectivity, so the early pumpjack can reach its
deposit without exposing the later steel industrial pipe recipe.

## Staged unlocks

`CR01 — The Steel Age` now owns the cast-iron construction family used by the
rig: ingot, nugget, sheet, block, frame, truss, pipe, fluid tank, and mechanical
pump. `CR01 — Oil processing` owns the scanner, pumpjack base, crank, hammer
holder, small/large hammer parts, connectors, heads, oil hammer, and oil can.

The oil-field recipes retain the exact authored IDs already referenced by
`tools/machine_recipe_dependencies.json`. Their seed entries remove only the
corresponding installed TFMG recipe IDs, so no unrelated construction path is
silently erased.

## Deliberate boundary

This slice changes crude-oil discovery/extraction plus the downstream steel
distillation and engine-construction gateways. Petroleum-fluid
canonicalization is a separate policy and is not changed here.

That petroleum policy also covers CDG's data-driven engine registry. CDG
declares diesel, gasoline, biodiesel, ethanol, and plant oil as independent
fuel-type resources rather than consulting only `c:fuel`. The companion mod
therefore overrides the biodiesel, ethanol, and plant-oil entries to the empty
`industrial_colonies:disabled_cdg_engine_fuels` fluid tag. Diesel continues to
read `c:diesel` and gasoline continues to read `c:gasoline`; those common tags
contain only their TFMG fluids. The ordinary `c:ethanol` and `c:plantoil` tags
are deliberately not emptied because other non-engine recipes may still use
them.

## Verification

The current focused validation is:

```powershell
python tools\validate_petroleum_engine_progression.py
python -m unittest tools.test_petroleum_engine_progression -v
```

It checks the installed TFMG/CDG recipes, exact removals and counts, node
ownership, the absence of post-Blast-Furnace materials from field recipes, the
functional cast-iron pipe tag, the first diesel engine's lack of digital
prerequisites, and the preserved engine gateways.

The canonicalization validator separately inspects CDG's installed dynamic
fuel registry and requires every discovered engine fuel to be explicitly
allowed or disabled. It also compares each disabled override with the source
entry so engine performance fields cannot drift accidentally:

```powershell
python tools\validate_canonicalization.py `
  "C:\Users\GodPC\curseforge\minecraft\Instances\All in one" `
  --skip-installed-parity
```
