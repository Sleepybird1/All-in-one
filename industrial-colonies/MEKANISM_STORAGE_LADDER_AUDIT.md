# Mekanism storage ladder audit

## Decision

**Implemented after the reviewed Extreme Power Transmission batch.**

The four reviewed cards now source-own the Energy Cube ladder in
`progression/managed_recipe_overhaul.seed.json`. The Ultimate Cube consumes
`industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker`, and that analog
predecessor was implemented and validated first.

The former automatic 5x5 cube owners were replaced one-for-one. Their output
ownership is now explicit, uses the correct component tiers, and makes Ultimate
storage require the analog transmission branch.

The reviewed ladder does the following:

1. Basic converts an Electro Energetics accumulator into the first dense local
   Mekanism buffer.
2. Advanced consumes Basic plus an Advanced Control Circuit and Reinforced
   Alloy.
3. Elite consumes Advanced plus an Elite Control Circuit and Atomic Alloy.
4. Ultimate consumes two Elite Cubes, an Ultimate Control Circuit, a completed
   TFMG circuit board, and the completed Electro Energetics SF6 breaker.

That final ingredient makes High-Energy Distribution a real convergence: the
player must complete both the protected overhead grid and the Mekanism factory
branch. AE2 processors are intentionally absent from the cube ladder; digital
storage remains useful without becoming an arbitrary ingredient in every power
component.

All four replacements use complete 5x5 Mechanical Crafting patterns and retire
only their four exact installed recipe IDs. Direct inspection of
`Mekanism-1.21.1-10.7.19.85.jar` confirms all four sources are
`mekanism:mek_data`, output one cube, and occupy the exact paths recorded in the
plan.

## Component-transfer caveat

`mekanism:mek_data` is not merely a shaped-recipe label. Mekanism's custom
assembler copies supported data components, including stored energy, from
inputs into its output. KJSGen's Create Mechanical Crafting card cannot emulate
that behavior. These replacements are intentionally safe but lossy: the player
must drain each input cube and remove transferable upgrades before crafting the
next tier. The output is a valid empty cube; no energy is duplicated.

The Induction Matrix family remains a separate follow-up because it has ten
functional components that must be owned together and depends on this entire
cube ladder.

The machine-readable contract is
`MEKANISM_STORAGE_LADDER_AUDIT.plan.json`.

Run `tools/validate_mekanism_storage_ladder_audit.py` to recheck the installed
JAR, catalog evidence, patterns, dependencies, KJSGen compilation, exact seed
parity, assembled output ownership, and nine embedded mutations. The separate
`tools/test_mekanism_storage_ladder_audit.py` suite adds eleven focused tests for
owner replacement, recipe drift, convergence, component handling, and pattern
shape.

A fresh temporary build contains 325 managed recipes, 185 automatic recipes,
393 compiled KJSGen cards, and 709 exact removals. Its managed DAG has 822
inferred item edges and zero warnings. Managed-overhaul, physical-progression,
Extreme Transmission, and High-Voltage regression validators all pass. The
shared generated manifest/KJSGen files and live pack were intentionally not
regenerated or deployed.
