# Extreme analog transmission audit

## Decision

**Implemented in the authoritative seed.**

The eight replacement cards are valid analog manufacturing contracts, and their
complete dependency graph is now analog as well. The seven predecessor recipes
were repaired in the High Voltage batch: they use TFMG/Create components and
Railway-class Create Encased machinery instead of AE2 processors, Mekanism
components, or indirectly Mekanism-gated Industrial Iron machines.

The protected Electro Energetics grid should remain an analog manufacturing
branch until the authoritative convergence at High-Energy Distribution. A fresh
isolated manifest proves that boundary is clean and that all seven repaired
predecessors reach the final breaker through the combined dependency graph.

All eight reviewed contracts now source-own their outputs in
`progression/managed_recipe_overhaul.seed.json`. The obsolete
`industrial_colonies:grid/sulfur_hexafluoride_breaker` owner was removed; no
unrelated seed entry, generated project, live-pack file, quest, or Draw.io file
was changed.

This bounded repair replaces eight exact installed recipe IDs. It adds two
factory-made intermediates—pressure-formed glass segments and heavily insulated
wire—then builds spools, suspended insulators, grounding hardware, an analog
disconnect, a capacitor bank, and finally the SF6 breaker. The final breaker
therefore represents an actual transmission yard rather than one cheap machine.

## Manufacturing flow

1. The Railway press makes glass insulator segments and laminates High-Voltage
   wire in canonical TFMG rubber/plastic without introducing a hidden Mekanism
   machine dependency.
2. The same line winds protected conductor, assembles hanging insulators, and
   terminates TFMG copper electrodes as ground rods.
3. Mechanical Crafting constructs the switch and capacitor bank from completed
   High-Voltage components.
4. A final 5x5 breaker recipe converges the switch, capacitor bank, transformer,
   regulator, insulation, grounding, transformer oil, and TFMG heavy casing.

The installed Electro Energetics build exposes a transformer-oil fluid but no
craftable sulfur-hexafluoride fluid or gas. The final recipe therefore uses the
mod's own transformer-oil bucket instead of inventing a fake cross-mod chemical.

## Independent review corrections

- Stock recipe IDs, output items, recipe types, and all eight stock output
  counts were rechecked directly against
  `electroenergetics-1.21.1-1.1.1.jar`.
- Counted tags such as `4x #c:glass_blocks` are unsupported by the KJSGen slot
  compiler. The glass contract now repeats its tag slots explicitly.
- All five compacting cards now select `createcasing:railway_press`. The former
  Industrial Iron machine introduced an indirect Mekanism control-circuit gate.
- The predecessor list now uses all seven actual High-Voltage managed IDs,
  including Current Transformer because the repaired Voltage Regulator makes it
  a real transitive prerequisite of the final breaker.
- The validator compiles every proposed card in memory, checks stock output
  counts from the installed JAR, enforces dependency order as well as acyclicity,
  proves the seven repaired upstream recipes remain boundary-clean, and checks
  exact field-for-field parity between the reviewed contracts and the
  authoritative seed.

## Safety and bypass policy

- Every stock producer is retired by exact recipe ID.
- No namespace-wide or output-wide removal is permitted.
- No AE2 processor, Applied Create processor, Mekanism circuit/alloy, or
  Mekanism-dependent machine environment may enter this branch.
- Same-batch dependencies are acyclic and ordered.
- `glass_insulator_spool` remains stock because it neither creates a raw
  material bypass nor replaces the protected-wire spool.

The machine-readable contract is
`EXTREME_TRANSMISSION_AUDIT.plan.json`; run
`tools/validate_extreme_transmission_audit.py` after any future recipe edit.

A fresh temporary build after implementation contains 325 managed recipes, 393
compiled KJSGen cards, and 709 exact removals. These temporary results were used
for validation only; the shared generated manifest and KJSGen project remain
intentionally untouched for the root integration pass.

The 20 focused mutation tests cover installed output counts, KJSGen syntax,
Railway machine locks, semantic ingredients, exact seed parity, the retired
legacy owner, predecessor boundary regression, and dependency reachability.
