# Late-machine hardening

The managed KJSGen project now owns the construction path for 26 additional
machines which previously survived as inexpensive stock recipes.

## Mekanism

- Basic through Ultimate Energy Cubes are rebuilt as 5x5 machines at their
  corresponding control tier.
- Crusher and Precision Sawmill join the Mekanized Industry construction layer
  instead of remaining ordinary 3x3 purchases.
- SPS Casing, SPS Port, Supercharged Coil, and the Antiprotonic
  Nucleosynthesizer are Nuclear Engineering builds.

Teleporters, the Quantum Entangloporter, and the two QIO network entry blocks
are deliberately deferred. They conflict with the design requirement that
trains, AE2 infrastructure, and later planetary freight remain meaningful.
Their five exact acquisition recipes are removal cards in KJSGen; no broad
Mekanism removal is used. The Teleportation Core remains available as a
legitimate component for later authored systems.

The Digital Miner and Energized Smelter are retired instead of hardened. The
former bypasses exploration, regional resources, rail freight, and mining
infrastructure; the latter duplicates Create fan smelting/blasting. Their exact
stock IDs, along with the disabled Mekanism smelting-factory family, are covered
by `tools/validate_progression_bypass_retirement.py`.

## Extreme Reactors

Basic and reinforced turbine casings, controllers, bearings, blades, and shafts
are now 5x5 Nuclear Engineering builds. Fluidizer and Energizer casings and
controllers are hardened at the same boundary. Stock recycling routes may
remain where they cannot produce a forward tier bypass.

## Modern Foundry

The Seared Smeltery Controller and Scorched Foundry Controller now have explicit
5x5 heavy-industrial recipes. The latter consumes an already-reachable TFMG
Industrial Mixer, so Modern Foundry's large process catalog cannot be opened by
the old cheap casting-basin controller recipe.

## Validation

Run `python tools/validate_late_machine_hardening.py`. The contract checks one
managed 5x5 producer for every hardened output, exact retirement of every stock
producer, compilation into KJSGen, and continued deferral of all five
teleport/QIO entry recipes.
