# Progression-bypass retirement

This slice removes only confirmed shortcuts by exact recipe ID. It does not
apply namespace-wide or output-wide recipe deletion.

## Physical factory and exploration boundaries

- Mekanism's Digital Miner is retired because it bypasses regional resources,
  exploration, mine infrastructure, trains, and later off-world extraction.
- The Energized Smelter and all four Smelting Factories are retired because
  Create fan smelting/blasting already supplies the intended factory process.
- The Formulaic Assemblicator is deferred so Create automation and the authored
  AE2 crafting chain remain meaningful.
- Atomic Disassembler, Meka-Tool, Jetpacks, and Free Runners are deferred until
  the dedicated modular-tool and mobility progression is authored.
- The AE2 Quantum Link, Quantum Ring, and both entangled-singularity transforms
  are deferred with the other instant-distance logistics systems.
- All Allthemodium/Vibranium/Unobtainium equipment smithing routes and the
  Allthemodium Teleport Pad are retired. Those materials remain industrial
  currency and future Modern Foundry modifiers rather than a standalone gear
  ladder.
- SecurityCraft's base mine, disguised block/ore mines, rail mine, and mine
  remote-access recipe are retired. SecurityCraft's access-control and facility
  security blocks remain available for later integration.

## Nuclear chemistry boundary

The live profile does not contain Create Mekanism Improvements. Its former
Polonium, Antimatter, and Superheated Sodium recipe records came from a stale
catalog snapshot and are deliberately not emitted as phantom removals. The
installed Mekanism PRC, SPS/crystallizer, and rotary routes remain the current
chemistry paths. If that addon is installed later, its direct mixing routes
must be audited before they are admitted.

## Preserved factory production

Create Ultimate Factory's heated coal-block diamond process and low-chance
netherite-scrap crushing process remain. They are physical, scalable factory
routes and will be reviewed later for balance rather than mistaken for
one-block or chemistry bypasses.

Run `python tools/validate_progression_bypass_retirement.py` to verify every
retirement is present in both the managed manifest and compiled KJSGen project,
that no retired item has been accidentally reintroduced by a managed producer
or node assignment, and that the protected industrial routes remain intact.
