# Mekanism non-smelting Factory restoration audit

Status: **IMPLEMENTED — 32 restored Factory cards, four Smelting retirements, and installer closure are source-owned.**

## Corrected finding

The installed `Mekanism-1.21.1-10.7.19.85.jar` contains exactly 36 Factory
recipes: four tiers across Combining, Compressing, Crushing, Enriching,
Infusing, Injecting, Purifying, Sawing, and Smelting. The authoritative seed
now owns one direct-empty 5x5 card for each of the 32 non-smelting outputs.
Only these four remain bare intentional retirements:

- `mekanism:factory/basic/smelting`
- `mekanism:factory/advanced/smelting`
- `mekanism:factory/elite/smelting`
- `mekanism:factory/ultimate/smelting`

Each installed source is a
one-output `mekanism:mek_data` recipe at
`data/mekanism/recipe/factory/<tier>/<process>.json`, has the exact pattern
`ACA / IPI / ACA`, and consumes the corresponding single-block machine at
Basic or the immediate same-process prior Factory thereafter. The plan pins
the SHA-256 of all 36 payloads, including the four retirements.

## Replacement contract

The plan expands to exactly 32 source-owned, 5×5 Create Mechanical Crafting
cards. Every card uses this filled 25-slot layout:

```text
AHCHA
HSPCH
CTXRC
HCMSH
AHCHA
```

`H/S/M` are TFMG Heavy Plate, Mekanism Steel Casing, and TFMG Steel
Mechanism. `A/C/P/T/X/R` are the tier alloy, tier control circuit, tier
precision component, tier installer, immediate same-process predecessor, and
process anchor. All are exact installed items; no counted tag or invented ID
is present. Temporary compilation produces 32
`kjsgen:create_mechanical_crafting` cards, each with `gridW=5`, `gridH=5`, 25
input cells, and one exact stock removal.

The eight Factory lines remain independent DAGs. Basic consumes its matching
single-block machine; Advanced consumes Basic; Elite consumes Advanced; and
Ultimate consumes Elite. No Factory cross-converts into another process type.

Injecting and Purifying are physically held at `CR01 — Chemical Separation`
in Nuclear Engineering because that node owns their base machines. This fixes
the earlier draft, which left those eight Factory outputs in four general tier
nodes. The implemented assignment delta is 16 additions and eight removals:

- Add Crushing and Sawing to each tier's general node: eight additions.
- Add all Injecting and Purifying Factories to Chemical Separation: eight additions.
- Remove those Injecting and Purifying outputs from the four general tier nodes: eight removals.

The assignment order remains cross-audit deterministic. Each general node keeps
its locked historical entries after removing its two chemical Factories, then
keeps any already-audited Induction/transmitter segment unchanged, and finally
appends only that tier's Crushing and Sawing Factories. Both earlier validators
now derive this exact transformation from this plan's 16-add/8-remove delta;
they do not accept arbitrary later unlocks.

## Tier-installer bypass closure

Recipe ownership alone is insufficient. Installed `ItemTierInstaller.useOn`
checks `mekanism:blacklist/installer_upgradeable`, then obtains
`AttributeUpgradeable`, verifies the installer's `fromTier`, replaces the
block, and transfers tile data. Without a data tag, right-click upgrades bypass
the 32 hard recipes and can recreate the four retired Smelting Factories.

The project now contains and the focused validator checks this exact
non-replacing resource:

`src/main/resources/data/mekanism/tags/block/blacklist/installer_upgradeable.json`

The exact protected contract is 49 blocks.

### Factory family — 45 values

Base machines:

- `mekanism:combiner`
- `mekanism:osmium_compressor`
- `mekanism:crusher`
- `mekanism:enrichment_chamber`
- `mekanism:metallurgic_infuser`
- `mekanism:chemical_injection_chamber`
- `mekanism:purification_chamber`
- `mekanism:precision_sawmill`
- `mekanism:energized_smelter`

For every tier `basic`, `advanced`, `elite`, and `ultimate`, include each of:

- `mekanism:<tier>_combining_factory`
- `mekanism:<tier>_compressing_factory`
- `mekanism:<tier>_crushing_factory`
- `mekanism:<tier>_enriching_factory`
- `mekanism:<tier>_infusing_factory`
- `mekanism:<tier>_injecting_factory`
- `mekanism:<tier>_purifying_factory`
- `mekanism:<tier>_sawing_factory`
- `mekanism:<tier>_smelting_factory`

Runtime-minimal active upgrade sources are the nine base machines plus Basic,
Advanced, and Elite Factories: 36 blocks. Ultimate Factories are terminal and
do not receive `AttributeUpgradeable`. The exact family contract still keeps
all 45 owned/retired Factory blocks so the data boundary is explicit and cannot
silently reopen if Mekanism changes its terminal mapping.

### Energy Cubes — four values

- `mekanism:basic_energy_cube`
- `mekanism:advanced_energy_cube`
- `mekanism:elite_energy_cube`
- `mekanism:ultimate_energy_cube`

`createEnergyCube` attaches `AttributeUpgradeable`; Basic, Advanced, and Elite
have concrete next-block suppliers and can bypass the owned Advanced, Elite,
and Ultimate Cube recipes. Ultimate is terminal with a null supplier. As with
Factories, the narrow contract names the complete four-block owned family.

Thus only 39 of the 49 values are active installer source blocks today; ten are
terminal exact-family guards.

### Transmitters are deliberately excluded

The installed constructors for Universal Cables, Mechanical Pipes, Pressurized
Tubes, Logistical Transporters, and Thermodynamic Conductors all delegate to
`createTransmitter`. That builder attaches `AttributeTier` only, not
`AttributeUpgradeable`, so these blocks cannot pass `ItemTierInstaller`'s
runtime gate. None of their 20 Basic/Advanced/Elite/Ultimate IDs belongs in the
blacklist. Their hard recipes need exact recipe removal/ownership, but no
right-click installer closure.

## State-transfer rule

The stock `mekanism:mek_data` recipes preserve machine data. Mechanical
Crafting does not copy inventories, tanks, energy, upgrades, side
configuration, ownership, or security data. Player guidance must therefore say
**drain and empty before construction**; the resulting Factory starts with
fresh state.

## Implemented boundary

The source now enforces all of the following:

1. The 32 expanded cards do not change the user-owned Metallurgic Infuser recipe.
2. Each restored stock ID is owned by exactly one card's exact `remove` array.
3. Only the four `factory/*/smelting` IDs remain bare Factory retirements; `mekanism:energized_smelter` remains separately retired.
4. The assignment map contains the exact 16 additions and eight removals above.
5. The exact 49-value installer blacklist remains `replace: false`.
6. Existing player guidance states the drain-before-upgrade policy before the first Factory construction step.

The focused validator pins all 36 source recipes and nine reviewed runtime
classes, proves the current removal/ownership boundary, verifies assignment
phases and deltas, compiles the 32 proposed cards only in temporary storage,
checks DAG acyclicity, and validates the implemented blacklist. Its 28 mutation
tests cover source/runtime hashes, retirement boundaries, implementation parity, compile
shape, phase regressions, assignment drift, Factory/Cube omissions, and
accidental transmitter blocking.
