# Mekanism Recipe V3 Audit

## Result

**PASS — source-only dry application; no live project, build, deployment, or game files were changed.**

The audit used the current managed seed plus the catalog at
`outputs/recipe-catalog-current/recipe_catalog.sqlite`.

| Check | Result |
|---|---:|
| Mekanism catalog recipes inspected | 2,230 |
| Stock shaped/shapeless recipes classified | 204 |
| Existing managed Mekanism outputs inspected | 110 |
| Managed Mekanism outputs after dry v3 application | 119 |
| Actual process machines covered by v3 | 19 |
| Tier Installer assemblies | 4 |
| Energy Cube recipes | 4 |
| Rigid casing compacting batches | 3 |
| Direct Factory stock recipes retired | 36 / 36 |
| Direct Factory outputs excluded | 36 / 36 |
| Duplicate managed outputs | 0 |
| Missing non-vanilla item references | 0 |
| Idempotence | PASS |
| Python compilation | PASS |

## Manufacturing policy applied

- Actual Mekanism process machines are Industrial Iron sequenced assemblies.
- Copper remains an electronics/component line; Railway casing is not used to assemble Mekanism process machines.
- A process-machine recipe depicts internal function: rotors, crushing wheels, pumps, vessels, electrodes, heaters, mixers, feed systems, and controllers are used where they physically belong.
- Compacting is reserved here for rigid structural shells: the Mek Steel Casing, Induction Casing batch, and SPS Casing batch.
- Direct Basic, Advanced, Elite, and Ultimate Factory blocks have no recipes. Upgrading a machine requires the appropriate Tier Installer and Mekanism's normal right-click upgrade behavior.
- The three live user-reference outputs—Metallurgic Infuser, Rotary Condensentrator, and Energy Tablet—remain user-owned and are not overwritten by this module.
- Allthemodium-family currency was not inserted into the installer ladder. Those materials belong to later progression; using them here would risk making the machinery needed to manufacture the currency depend on the currency itself.

## Process-machine coverage

All recipes in this table use the Industrial Iron Deployer and Industrial Iron Press.

| Machine | Manufacturing identity |
|---|---|
| Combiner | opposed platen, depot, powered steel drive, heavy closure |
| Enrichment Chamber | rotor, millstone, eccentric precision drive, vibration bed |
| Osmium Compressor | pumped pressure vessel, transformer, motorized platen, osmium face |
| Crusher | paired crushing wheels, motor, steel drivetrain, heavy shell |
| Precision Sawmill | powered saw carriage, precision feeder, guarded drive |
| Electrolytic Separator | electrolytic core, opposed TFMG electrodes, pumped chemical cell |
| Chemical Oxidizer | fan-driven vat, chemical storage, pumped manifold, capacitor buffer |
| Chemical Infuser | dual chemical feeds, dual pumps, mixing vessel, transformer |
| Pressurized Reaction Chamber | fluid/chemical reservoirs, process vat, pressure shell, controller |
| Energized Smelter | large heating coil, transformer, forced air, refractory burner core |
| Formulaic Assemblicator | Mechanical Crafter, formula socket, precision feed, logic |
| Fuelwood Heater | forced-draft Blaze Burner, heat channels, thermostat, refractory shell |
| Modification Station | module socket, formula interface, tool carriage, diagnostics |
| Pigment Extractor | milling head, chemical reservoir, extraction vat, pump |
| Pigment Mixer | dual reservoirs, dual pumps, driven mixer, color control |
| Painting Machine | Deployer head, pigment tank, sealed pump, precision feed |
| Nutritional Liquifier | sanitary mixer/basin, food-safe tank, pump, plastic lining |
| Seismic Vibrator | eccentric rotor, twin motors, reaction mass, magnetic suspension |
| Digital Miner | surveyed seismic base, laser head, sorter, teleportation core, ultimate logic |

Existing nuclear process recipes were audited separately. Chemical processing remains on Industrial Iron; isotope/SPS/final nuclear machinery remains on Refined Radiance. They were not replaced with generic templates.

## Tier Installer progression

The four assemblies are cumulative but do not merely recolor one template.

| Installer | Prior assembly | Processor | Distinct engineering purpose |
|---|---|---|---|
| Basic | TFMG Steel Mechanism | Andesite Stress Processor | physical service card, paired semiconductors, plastic, infused bus, steel frame |
| Advanced | Basic Installer | Logic Processor | etched backplane, osmium spine, magnetic shielding, Advanced control |
| Elite | Advanced Installer | Calculation Processor | four-capacitor bank, HDPE, lithium buffer, cobalt reinforcement |
| Ultimate | Elite Installer | Engineering Processor | high-voltage capacitor, redundant HDPE, refined obsidian, magnetic/atomic isolation |

Every installer contains:

- one progression-appropriate processor;
- both TFMG semiconductor types;
- a capacitor package;
- plastic or HDPE insulation;
- the matching Mekanism Control Circuit; and
- a tier-specific structural alloy or reinforcement.

The Basic and Advanced cards use Industrial Iron. Elite and Ultimate use Weathered Iron so the installer ladder remains available before nuclear infrastructure; Refined Radiance stays reserved for the SPS/final nuclear line.

## Energy Cube balance

The Energy Cube family is the explicit exception where a dense outer shell is appropriate.

- Basic remains a compact 3×3 lithium/tablet accumulator pack.
- Advanced uses a 5×5 magnetic-osmium enclosure with a complete Basic Cube and a populated 3×3 interior.
- Elite uses a 5×5 cobalt/gold enclosure with a complete Advanced Cube, semiconductor pair, reinforced bus, and Elite control.
- Ultimate uses a 5×5 atomic/refined-obsidian enclosure with a complete Elite Cube, SF6 breaker, TFMG accumulator, Engineering Processor, lithium reserve, and Ultimate control.
- The Ultimate recipe yields **two cubes**, compensating for the full high-voltage enclosure and internal component cost.

## Ring and border review

The pre-v3 Mekanism ring scan found two unjustified structural borders:

- `industrial_colonies:mekanism/induction/casing`
- `industrial_colonies:mekanism_nuclear/sps_casing_batch`

Both are now compacting batches on their appropriate late casing lines. The smaller Mek Steel Casing shell was also converted to Industrial Iron compacting. No other Mekanism 5×5 grid remains except:

- the three explicitly approved Advanced/Elite/Ultimate Energy Cube battery enclosures; and
- the Dimensional Stabilizer, which belongs to the explicitly excluded world-loading scope.

## Factory retirement proof

The catalog contains nine Factory processes at four tiers, for exactly 36 stock recipes. The module:

1. removes all 36 exact `mekanism:factory/<tier>/<process>` recipe IDs;
2. removes any managed recipe whose output is one of the 36 Factory blocks;
3. adds all Factory outputs to the managed exclusion set; and
4. removes conflicting preserve declarations.

This leaves Tier Installers as the only intended Factory progression route.

## Validation performed

- Imported and compiled `tools/recipe_design_v3_mekanism.py`.
- Applied the module to a deep-copied current seed.
- Ran the module's strict `audit()` checks.
- Applied the module a second time and compared the complete dictionaries byte-for-byte in memory.
- Resolved every v3 ingredient against the installed catalog, exempting vanilla Minecraft IDs and item tags.
- Confirmed no direct Factory output remained and all 36 stock Factory recipe IDs were retired.
- Confirmed every covered process machine is a sequence using only Industrial Iron machinery.
- Confirmed each installer has its processor, semiconductor pair, capacitor package, plastic insulation, Mekanism circuit, structural identity, and cumulative prior installer.
