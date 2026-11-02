# Petroleum and Engine Progression

## Source of truth

The petroleum construction slice is authored in
`progression/managed_recipe_overhaul.seed.json`. The old
`industrial_oil_field_construction.js` file is only a migration marker; it no
longer owns recipes. A manifest rebuild must therefore retain the authored IDs
instead of recreating `industrial_colonies:auto/...` recipes.

Each authored recipe removes exactly one installed stock recipe ID. There are
no output-wide or mod-wide removals in this slice.

## Manufacturing flow

1. **Prospecting and extraction** — the Surface Scanner and twelve-piece TFMG
   field kit use Create brass/precision parts and TFMG cast iron. Small tools,
   heads, pivots, and connectors remain readable 3x3 recipes; the pumpjack
   base, crank, and walking beam are shaped 5x5 assemblies.
2. **Steel refining** — the Distillation Controller is a lead-lined,
   instrumented manifold. Its output block is a separate steel tank-and-pipe
   pressure assembly. Neither requires digital electronics.
3. **Combustion foundation** — `tfmg:regular_engine` is built as a matched pair
   from TFMG cylinders, gearbox, heavy casing, and steel mechanisms. The three
   existing authored gateways for `engine_controller`, `simple_large_engine`,
   and `large_engine` are preserved unchanged.
4. **First diesel** — the Create Diesel Generators engine consumes a TFMG
   regular engine and canonical TFMG diesel cylinder. It has no AE2,
   ComputerCraft, Applied Create, or Mekanism prerequisite.
5. **Heavy engines** — the turbocharger uses TFMG turbine blades and ducting;
   the large diesel consumes compact diesel units plus the TFMG Large Engine;
   the TFMG Turbine Engine consumes the turbocharger; and the huge diesel
   converges those heavy components.
6. **Radial aviation** — the radial engine is a literal radial 5x5 layout of
   eight TFMG gasoline cylinders around a geared steel hub.

TFMG's Pumpjack only follows blocks in its `tfmg:industrial_pipe` block tag.
The companion data pack merges `tfmg:cast_iron_pipe` into that tag at
`src/main/resources/data/tfmg/tags/block/industrial_pipe.json`, keeping the
pre-steel extraction route functional rather than merely craftable.

## Verification

Validate the source seed and the installed TFMG/CDG recipes:

```powershell
python tools\validate_petroleum_engine_progression.py
python -m unittest tools.test_petroleum_engine_progression -v
```

To verify a temporary or newly regenerated manifest as well:

```powershell
python tools\validate_petroleum_engine_progression.py --manifest <manifest.json>
```

The validator checks all 21 source-owned recipes, the three preserved engine
gateways, exact stock removals and output counts, node ownership, pre-steel oil
materials, first-diesel digital independence, TFMG-first heavy-engine
dependencies, non-generic grid layouts, and the functional cast-iron pipe tag.
