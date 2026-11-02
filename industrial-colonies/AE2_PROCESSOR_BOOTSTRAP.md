# AE2 processor bootstrap

The first AE2 processors use the native Inscriber. The pack-owned
`createappliedkinetics-common.toml` sets `overwrite_ae2_recipes = false`, because
the enabled overwrite replaces AE2's processor recipes with Create sequenced
assemblies and removes the Inscriber crafting recipe.

The immutable research topology is unchanged. Exact manufacturing ownership is:

- **Advanced Circuitry:** Charger, Inscriber, silicon/logic press duplication,
  printed silicon, and printed logic circuits.
- **Early Chips:** finished logic processors.
- **Advanced Processors:** calculation/engineering press duplication, printed
  circuits, and finished processors.

The four original processor presses remain exploration rewards from AE2
meteorites. Their Inscriber recipes duplicate an already acquired press; they
do not create a press from nothing. The press items are therefore not claimed
as research-owned outputs; only their duplication recipes are stage-gated.

ExtendedAE's Crystal Assembler remains an acceleration option. Its three AE2
processor recipes carry the same exact research stages as the corresponding
Inscriber outputs, so obtaining the later machine never bypasses the digital
branch.

ExtendedAE's Circuit Cutter is treated the same way: logic prints are locked to
Advanced Circuitry, while calculation and engineering prints are locked to
Advanced Processors.

AE2's stock Drive and 4k Item Cell recipes depended on downstream engineering
and calculation processors. They are replaced at ME System Basics with two
small, factory-relevant recipes using logic processors and ancestor materials.
The stock 4k direct, housing-combination, and 1k-upgrade routes are removed so
the downstream component cannot silently restore the old ordering.

Runtime enforcement is server-side and owner-team based:

- vanilla crafting gates the Charger and Inscriber recipes;
- the AE2 Inscriber gate resolves the cached recipe back to its exact holder ID;
- the ExtendedAE Crystal Assembler gate checks its exact recipe holder ID.

This removes the apparent `processor -> Crystal Assembler -> terminal ->
processor` bootstrap cycle while preserving the Crystal Assembler as a later
factory throughput upgrade.
