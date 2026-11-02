# Phase 7 — Industrial Resource Worldgen Audit

Audit date: 2026-08-30  
Target: Minecraft 1.21.1, NeoForge  
Installed instance inspected read-only: C:\Users\GodPC\curseforge\minecraft\Instances\All in one

## Scope and authority

This audit traces the installed pack's active industrial-resource generation from the authoritative sources that actually load:

1. active mod JAR data resources;
2. active common/server configuration;
3. active KubeJS tag and recipe scripts;
4. custom-feature and reservoir bytecode where JSON does not expose the behavior;
5. vanilla 1.21.1 worldgen source from the local NeoForm development cache.

No pack files, worlds, worldgen resources, or Draw.io files were changed. The companion file WORLDGEN_INDUSTRIAL_RESOURCE_AUDIT.json contains the same core findings in machine-readable form.

The instance has no external worldgen datapack overriding these sources:

- instance datapacks: 0 files;
- moonlight-global-datapacks: 0 files;
- New World/datapacks: 0 files;
- KubeJS: no configured-feature, placed-feature, or biome-modifier resources;
- installed industrial_colonies-0.3.0.jar: no worldgen registry resources.

ImmersiveEngineering-1.21.1-12.4.2-194.jar.disabled is present but disabled. Mekanism Generators and Mekanism Tools are absent. Their surviving config files are not authoritative.

## Executive findings

- All mandatory stock resources currently exist. There is no immediate new-world hard softlock for lead, nickel, zinc, tin, osmium, uranium, fluorite, sulfur, coal, or crude oil.
- Uranium is duplicated materially and geologically. Mekanism uranium and Extreme Reactors Yellorite both generate in the Overworld, and both contribute to c:ores/uranium, c:raw_materials/uranium, and c:ingots/uranium.
- TFMG is correctly the only active normal lead-ore generator: Mekanism lead is disabled in config and Immersive Engineering is disabled. TFMG Galena is a second, rarer TFMG lead source.
- TFMG sulfur is the canonical technology sulfur. Vanilla Backport adds a very abundant, biome-scale minecraft:sulfur cave material, but it is not in c:dusts/sulfur and currently has no canonical conversion into TFMG sulfur dust.
- Oil has two independent geological models that do not share reserves:
  - TFMG physical oil-deposit blocks and native Pumpjack;
  - Create Diesel Generators seed/noise oil chunks and its Pumpjack.
  Active KubeJS makes the CDG Pumpjack output tfmg:crude_oil, but it does not make either pumpjack use the other mod's reserve system.
- TFMG 1.2.0 records finite reservoir reserves but its Pumpjack process method never decrements them. With infiniteDeposits=false, extraction still behaves as infinite. This is verified from the installed bytecode.
- The TFMG layered Overworld feature selects one of four patterns per successful feature invocation. At one invocation opportunity per 18 chunks, each of Bauxite, Galena, Lignite, and Fireclay has a nominal one-in-72 chunk pattern selection before placement success.
- The TFMG Nether layered feature selects one of two patterns. Sulfur therefore has a nominal one-in-36 chunk pattern selection before placement success.
- Create's global disableWorldGen flag also controls TFMG and Create Metallurgy placed features that use create:config_filter. Turning it on would silently suppress TFMG lead, nickel, lithium, oil, layered resources, Create zinc, and Create Metallurgy wolframite.
- Almost Unified does not protect worldgen in this pack: world_gen_unification=false and loot_unification=false.
- Create Metallurgy provides an unrestricted furnace/blast-furnace route from coal to createmetallurgy:coke. Extreme Reactors provides unrestricted smelting/blasting from coal or charcoal to bigreactors:graphite_ingot. Those are recipe/progression bypasses even though the underlying coal worldgen is healthy.
- Large clustered regional solid deposits do not require custom Java. Vanilla minecraft:noise_threshold_count and minecraft:noise_based_count placement modifiers can gate attempts into broad noise regions; minecraft:ore supports size 0–64. NeoForge add/remove biome modifiers and custom biome tags complete the datapack-only solution.
- CDG exposes a result-bearing KubeJS server event, CDGEvents.oilAmount, which can replace its oil amount algorithm per chunk. It is the strongest no-custom-Java system for arbitrary regional liquid fields.

## Active source inventory

| System | Active source | Worldgen role |
|---|---|---|
| Mekanism | Mekanism-1.21.1-10.7.19.85.jar | Tin, osmium, uranium, fluorite, configurable lead, salt |
| TFMG | tfmg-1.2.0.jar | Lead, nickel, lithium, bauxite, galena, lignite, fireclay, sulfur, physical oil deposits/wells |
| Create | create-1.21.1-6.0.10.jar | Zinc and layered-ore feature type |
| Create Diesel Generators | createdieselgenerators-1.21.1-1.3.15.jar | Programmatic seed/noise oil chunks |
| Create Metallurgy | createmetallurgy-1.0.3-1.21.1.jar | Nether wolframite/tungsten |
| Extreme Reactors | ExtremeReactors2-1.21.1-2.4.28.jar | Yellorite/Yellorium uranium-family ore |
| Modern Foundry | ModernFoundry-1.21.1-4.1.6-NeoForge.jar | Nether cobalt |
| Applied Energistics 2 | appliedenergistics2-19.2.17.jar | Certus-bearing meteorite structures |
| Vanilla Backport | VanillaBackport-neoforge-1.21.1-1.1.7.10.jar | Regional sulfur-cave biome and decorative sulfur material |
| Regions Unexplored | regions-unexplored-0.6.2-neoforge-21.1.jar | Large redstone veins in redstone_caves |
| Deeper and Darker | deeperdarker-neoforge-1.21.1-1.4.1.jar | Alternate vanilla ores in the Otherside dimension |
| Vanilla | local NeoForm 1.21.1 source | Coal, iron, copper, gold, redstone baseline |

## Exact resource registry matrix

### TFMG normal ores

All three biome modifiers use neoforge:add_features, target #minecraft:is_overworld, and run at underground_ores. All three placed features end with create:config_filter and therefore depend on Create's global worldgen switch.

| Resource | Biome modifier | Configured / placed feature | Configuration | Placement |
|---|---|---|---|---|
| Lead | tfmg:lead_ore | tfmg:lead_ore / tfmg:lead_ore | minecraft:ore; size 12; discard 0; tfmg:lead_ore and tfmg:deepslate_lead_ore | count 5; uniform absolute Y -15..80 |
| Nickel | tfmg:nickel_ore | tfmg:nickel_ore / tfmg:nickel_ore | minecraft:ore; size 10; discard 0; tfmg:nickel_ore and tfmg:deepslate_nickel_ore | count 5; uniform absolute Y -63..20 |
| Lithium | tfmg:lithium_ore | tfmg:lithium_ore / tfmg:lithium_ore | minecraft:ore; size 7; discard 0; tfmg:lithium_ore and tfmg:deepslate_lithium_ore | count 3; uniform absolute Y -63..-5 |

Lead status:

- Mekanism biome modifier ID mekanism:lead and feature mekanism:ore_lead_normal exist in the JAR, but installed config has lead.shouldGenerate=false and lead.normal.shouldGenerate=false.
- The disabled Mekanism lead's nominal settings are count 8, size 9, discard 0.25, trapezoid, ABOVE_BOTTOM(-24)..ABSOLUTE(64).
- Immersive Engineering's JAR is disabled.
- TFMG Galena also yields lead through data/create/recipe/crushing/galena.json: 40% one create:crushed_raw_lead plus 10% two tfmg:lead_nugget.
- Result: no lead softlock and no cross-mod physical lead-ore duplication, but lead has both a common direct vein and a rare TFMG stratum.

### TFMG layered deposits

Biome modifiers:

- tfmg:tfmg_striated_ores_overworld -> placed feature tfmg:tfmg_striated_ores_overworld, all Overworld biomes, underground_ores.
- tfmg:tfmg_striated_ores_nether -> placed feature tfmg:tfmg_striated_ores_nether, all Nether biomes, underground_ores.

Both configured features use create:layered_ore, size 32, discard chance 0. The Create implementation chooses exactly one layer_patterns entry with random.nextInt(patternCount) for each feature invocation.

Overworld placement:

- rarity filter chance 18;
- in square;
- uniform absolute Y -30..70;
- create:config_filter.

| Selected pattern | Technology material | Material layer | Nominal selection |
|---|---|---|---|
| 0 | Bauxite | tfmg:bauxite, weight 2, min layer 1, max layer 3 | 1/4 of 1/18 feature opportunities = nominal 1/72 chunks |
| 1 | Galena | tfmg:galena, weight 2, min 1, max 3 | nominal 1/72 chunks |
| 2 | Lignite | tfmg:lignite, weight 2, min 1, max 3 | nominal 1/72 chunks |
| 3 | Fireclay | tfmg:fireclay, weight 2, min 1, max 2 | nominal 1/72 chunks |

These probabilities are pattern-selection opportunities, not guaranteed deposits; terrain replacement and feature success still apply.

Feedstock relevance:

- data/create/recipe/crushing/bauxite.json yields 75% two plus 20% one tfmg:bauxite_powder, expected 1.7 powder per block.
- data/create/recipe/crushing/galena.json supplies canonical TFMG lead as described above.
- data/create/recipe/crushing/lignite.json yields independent 75% and 20% coal results, expected 0.95 minecraft:coal per block.
- Fireclay is a TFMG refractory/construction feedstock.

Nether placement:

- rarity filter chance 18;
- in square;
- uniform absolute Y 40..90;
- create:config_filter.

| Selected pattern | Technology material | Material layer | Nominal selection |
|---|---|---|---|
| 0 | Sulfur | tfmg:sulfur, weight 4, min 1, max 2 | 1/2 of 1/18 = nominal 1/36 chunks |
| 1 | Fireclay | tfmg:fireclay, weight 5, min 1, max 2 | nominal 1/36 chunks |

### Create zinc

- biome modifier: create:zinc_ore;
- type: neoforge:add_features;
- biomes: #minecraft:is_overworld;
- step: underground_ores;
- configured feature: create:zinc_ore;
- placed feature: create:zinc_ore;
- feature type: minecraft:ore;
- blocks: create:zinc_ore and create:deepslate_zinc_ore;
- size 12, discard 0;
- count 8, uniform absolute Y -63..70;
- placement ends with create:config_filter.

No second active zinc generator was found.

### Mekanism configurable resources

All biome modifiers target #mekanism:spawn_ores. That tag contains #minecraft:is_overworld and #c:is_overworld. Ore modifiers run at underground_ores.

The configured features use mekanism:ore and select an ore config entry by ore_type/index. The placed features use:

1. mekanism:disableable;
2. minecraft:count with mekanism:configurable_constant;
3. minecraft:in_square;
4. minecraft:height_range with mekanism:configurable;
5. minecraft:biome.

Installed config is C:\Users\GodPC\curseforge\minecraft\Instances\All in one\config\Mekanism\world.toml.

| Resource / variant | Biome modifier -> feature | Enabled | Attempts/chunk | Max size | Discard | Shape / plateau | Exact anchors |
|---|---|---:|---:|---:|---:|---|---|
| Tin small | mekanism:tin -> mekanism:ore_tin_small | yes | 14 | 4 | 0 | TRAPEZOID / 0 | ABSOLUTE(-20)..ABSOLUTE(94) |
| Tin large | mekanism:tin -> mekanism:ore_tin_large | yes | 12 | 9 | 0 | TRAPEZOID / 0 | ABSOLUTE(-32)..ABSOLUTE(72) |
| Osmium upper | mekanism:osmium -> mekanism:ore_osmium_upper | yes | 65 | 7 | 0 | TRAPEZOID / 8 | ABSOLUTE(72)..BELOW_TOP(-24) |
| Osmium middle | mekanism:osmium -> mekanism:ore_osmium_middle | yes | 6 | 9 | 0 | TRAPEZOID / 0 | ABSOLUTE(-32)..ABSOLUTE(56) |
| Osmium small | mekanism:osmium -> mekanism:ore_osmium_small | yes | 8 | 4 | 0 | UNIFORM / 0 | ABOVE_BOTTOM(0)..ABSOLUTE(64) |
| Uranium small | mekanism:uranium -> mekanism:ore_uranium_small | yes | 4 | 4 | 0 | TRAPEZOID / 0 | ABOVE_BOTTOM(0)..ABSOLUTE(8) |
| Uranium buried | mekanism:uranium -> mekanism:ore_uranium_buried | yes | 7 | 9 | 0.75 | TRAPEZOID / 16 | ABOVE_BOTTOM(-24)..ABOVE_BOTTOM(56) |
| Fluorite normal | mekanism:fluorite -> mekanism:ore_fluorite_normal | yes | 5 | 5 | 0 | UNIFORM / 0 | ABOVE_BOTTOM(0)..ABSOLUTE(23) |
| Fluorite buried | mekanism:fluorite -> mekanism:ore_fluorite_buried | yes | 3 | 13 | 1.0 | TRAPEZOID / 0 | ABOVE_BOTTOM(0)..ABSOLUTE(4) |
| Lead normal | mekanism:lead -> mekanism:ore_lead_normal | no | 8 nominal | 9 | 0.25 | TRAPEZOID / 0 | ABOVE_BOTTOM(-24)..ABSOLUTE(64) |

The unusual negative anchor values above are preserved exactly from the installed config and should not be normalized in a future override without testing.

Salt:

- biome modifier: mekanism:salt;
- configured / placed feature: mekanism:salt;
- custom feature type: mekanism:disk;
- enabled;
- count 2;
- radius configurable uniform with minRadius 2 and maxRadius 3;
- halfHeight 1;
- OCEAN_FLOOR_WG heightmap;
- water predicate;
- replaces dirt and clay with mekanism:block_salt.

Retrogen:

- every Mekanism ore has a corresponding _retrogen configured and placed feature;
- enableRegeneration=false;
- userWorldGenVersion=0.

Existing explored chunks therefore do not gain newly enabled or redistributed Mekanism ores automatically.

### Extreme Reactors uranium-family ore

Stone Yellorite:

- biome modifier: bigreactors:yellorite;
- modifier type: bigreactors:oregen_yellorite;
- biomes: #minecraft:is_overworld;
- feature: bigreactors:yellorite_ore;
- configured feature: bigreactors:yellorite_ore;
- block: bigreactors:yellorite_ore;
- minecraft:ore, size 9, discard 0;
- placed feature: bigreactors:yellorite_ore;
- count 5;
- raw JSON height: uniform min {above_bottom:15, absolute:0, below_top:0}, max {absolute:32, above_bottom:0, below_top:0}.

Deepslate Yellorite:

- biome modifier: bigreactors:yellorite_deepslate;
- feature: bigreactors:yellorite_deepslate_ore;
- configured feature: bigreactors:yellorite_deepslate_ore;
- block: bigreactors:deepslate_yellorite_ore;
- minecraft:ore, size 9, discard 0;
- placed feature: bigreactors:yellorite_deepslate_ore;
- count 3;
- raw JSON height: uniform min {absolute:-64, above_bottom:15, below_top:0}, max {absolute:-48, above_bottom:0, below_top:0}.

The composite anchor objects are preserved verbatim because they are not normal modern single-field VerticalAnchor JSON. Do not rewrite them based on assumed effective Y values without a registry-load/worldgen test.

Duplication is exact:

| Common tag | Mekanism member | Extreme Reactors member |
|---|---|---|
| c:ores/uranium | mekanism:uranium_ore, mekanism:deepslate_uranium_ore | bigreactors:yellorite_ore, bigreactors:deepslate_yellorite_ore |
| c:raw_materials/uranium | mekanism:raw_uranium | bigreactors:raw_yellorium |
| c:ingots/uranium | mekanism:ingot_uranium | bigreactors:yellorium_ingot |

This is the largest active worldgen/progression overlap.

### Create Metallurgy wolframite

- biome modifier: createmetallurgy:wolframite_ore;
- type: neoforge:add_features;
- biomes: #minecraft:is_nether;
- step: underground_ores;
- configured / placed feature: createmetallurgy:wolframite_ore;
- minecraft:ore replacing netherrack;
- block: createmetallurgy:wolframite_ore;
- size 9, discard 0;
- count 7, uniform absolute Y 0..60;
- create:config_filter;
- common material: c:ores/tungsten.

This is the only active tungsten/wolframite generator found.

### Modern Foundry cobalt

- biome modifier: modernfoundry:cobalt_ore;
- type: neoforge:add_features;
- biomes: #minecraft:is_nether;
- step: underground_decoration;
- features: modernfoundry:cobalt_ore_small and modernfoundry:cobalt_ore_large.

Small:

- configured feature modernfoundry:cobalt_ore_small;
- placed feature modernfoundry:cobalt_ore_small;
- minecraft:ore replacing netherrack;
- modernfoundry:cobalt_ore, size 4, discard 0;
- count 5;
- uniform ABOVE_BOTTOM(8)..BELOW_TOP(8).

Large:

- configured feature modernfoundry:cobalt_ore_large;
- placed feature modernfoundry:cobalt_ore_large;
- modernfoundry:cobalt_ore, size 6, discard 0;
- count 3;
- trapezoid absolute Y 8..32.

No second active cobalt generator was found.

## Crude oil and reservoirs

### TFMG physical deposits

Registry chain:

- biome modifier tfmg:oil_deposit;
- neoforge:add_features;
- biomes #minecraft:is_overworld;
- step underground_ores;
- configured feature tfmg:oil_deposit;
- type tfmg:oil_deposit;
- empty JSON config;
- placed feature tfmg:oil_deposit;
- rarity filter 1/4 chunks;
- fixed absolute Y -64;
- create:config_filter.

The installed custom feature adds an internal random.nextInt(20)==0 gate. Effective successful feature entry is therefore at most about one per 80 chunks before terrain/placement outcomes.

On an internal pass, OilDepositFeature:

- attempts a variable cluster with no more than six anchors;
- re-rolls the loop bound each iteration rather than choosing a fixed cluster size once;
- moves successive anchors by independent horizontal offsets in the range -20..19;
- places tfmg:oil_deposit at each anchor;
- grows a variable vertical column containing tfmg:crude_oil and early tfmg:fossilstone.

The configured feature has an empty config. A datapack can alter the placed feature's frequency, height, or biome attachment, but cannot alter the internal 1/20 gate, cluster loop, offsets, or column algorithm.

Oil-well landmark:

- biome modifier tfmg:oil_well;
- biomes #minecraft:has_structure/desert_pyramid;
- step fluid_springs;
- configured feature/type tfmg:oil_well;
- placed feature tfmg:oil_well;
- rarity 1/500;
- fixed absolute Y -64;
- create:config_filter.

Reservoir state:

- saved-data key: tfmg_deposits;
- a newly accessed deposit joins a reservoir whose anchor is found in the horizontal scan square -32..31 X and Z, or creates a new reservoir;
- new oilReserves = RandomSource.nextInt(1000, depositMaxReserves);
- installed depositMaxReserves=10000, so initial values are 1000 inclusive through 9999 inclusive;
- installed infiniteDeposits=false.

Critical installed-code defect:

PumpjackBaseBlockEntity.process() fills tfmg:crude_oil, tests infiniteDeposits, and when false only reads level.getRandom() before returning. It never looks up a FluidReservoir and never subtracts from oilReserves. The saved reserves exist but are not consumed. Finite depletion cannot be made real by TOML or datapack changes.

### Create Diesel Generators oil chunks

This system has no configured-feature, placed-feature, or biome-modifier ID. It is programmatic and stored under:

- class com.jesz.createdieselgenerators.world.OilChunksSavedData;
- saved-data key cdg_oil_chunks.

Base algorithm:

1. Create PerlinNoise from the world seed with octaves -2, -1, 0, 1.
2. Sample at chunkX × Oil chunk map scale, 0, chunkZ × Oil chunk map scale.
3. Normalize as (noise + 1) / 1.6.
4. Square the normalized value.
5. Multiply by 7,000,000 and either the normal or high-oil biome multiplier.
6. Return 0 below the oil-chunk threshold.
7. Return Integer.MAX_VALUE above the infinite threshold.
8. Otherwise return the finite integer amount.

Installed server config:

| Key | Value |
|---|---:|
| Infinite oil chunk threshold | 10,000,000 |
| Oil chunk threshold | 4,000,000 |
| Disable normal oil chunks | false |
| Disable high oil chunks | false |
| Normal oil chunks oil amount multiplier | 1.3 |
| High oil chunks oil amount multiplier | 2.0 |
| Oil chunk map scale | 1.0 |
| Max Oil Scanner Level | 10,000 |

High-oil biome tag:

- createdieselgenerators:oil_biomes;
- savanna, savanna_plateau, desert, badlands, wooded_badlands, eroded_badlands, plains;
- all standard ocean and deep-ocean variants listed by the JAR.

The code also checks createdieselgenerators:deny_oil_biomes, but the installed JAR supplies no JSON values for that tag.

Pumpjack substrate:

- block tag createdieselgenerators:oil_deposit;
- installed member minecraft:bedrock.

Pump output:

- JAR default fluid tag createdieselgenerators:pumpjack_output contains createdieselgenerators:crude_oil;
- active KubeJS industrial_petroleum_canonicalization.js replaces that tag with tfmg:crude_oil;
- result: CDG's independent regional oil map yields the canonical TFMG crude fluid.

KubeJS hook:

- event group/name: CDGEvents.oilAmount;
- server event;
- result-bearing;
- public event fields: chunkPos, biomes, seed;
- when a listener exists, its numeric result completely replaces the built-in calculation.

This enables deterministic oil provinces, dry zones, finite fields, and deliberately infinite superfields without custom Java. It only governs the CDG oil-chunk system.

### Oil progression decision required

The two extraction systems cannot be made one system with datapack/tag work:

- TFMG Pumpjack requires physical tfmg:oil_deposit blocks and uses TFMG's reservoir save data.
- CDG Pumpjack reads cdg_oil_chunks under bedrock.
- The shared output tag only unifies the produced fluid.

Recommended choices:

1. TFMG-native route: keep TFMG physical deposits as the Oil Processing unlock, gate or remove the CDG Pumpjack until a later augmentation, and accept infinite extraction until a small Java fix decrements TFMG reserves.
2. Regional CDG route: use CDGEvents.oilAmount for Satisfactory-style fields, make CDG Pumpjack the canonical extractor, and demote the TFMG Pumpjack. This is fully scriptable but changes the intended machine identity.
3. Hybrid route: deliberately keep rare TFMG physical wildcats plus broad CDG fields, but make their separate prospecting and progression roles explicit. Do not present them as one reserve pool.

## Sulfur systems

### Canonical technology sulfur

Active KubeJS industrial_sulfur_canonicalization.js:

- removes all members of c:dusts/sulfur;
- adds only tfmg:sulfur_dust;
- removes Mekanism sulfur production routes and re-adds controlled TFMG-sulfur outputs.

The primary geological feedstock is the TFMG Nether layered feature described above: tfmg:sulfur, nominal one selected sulfur pattern per 36 chunks before placement success.

The stock conversion is also lossy:

- recipe ID data/create/recipe/crushing/sulfur.json, registry ID create:crushing/sulfur;
- one tfmg:sulfur block;
- independent 20% and 10% chances for one tfmg:sulfur_dust;
- expected output 0.30 sulfur dust per mined sulfur block.

The active coal-gasification recovery recipes eventually provide deterministic TFMG sulfur dust, but they depend on Mekanism reaction infrastructure and are not a substitute for an early geological supply.

Softlock condition:

- if Nether access is ever locked behind a node that already requires sulfur chemistry, this becomes circular;
- if Nether access remains available before Chemical Processing, it is not absent, but the combination of nominal 1/36 pattern selection and only 0.30 expected dust per block makes pre-prospecting bulk requirements risky.

### Vanilla Backport sulfur caves

Installed config:

- has_sulfur_caves=true;
- has_sulfur_springs=true.

Biome:

- minecraft:sulfur_caves;
- TerraBlender region ID minecraft:overworld with region weight 5;
- climate overlay: temperature full range, humidity full range, continentalness COAST through INLAND, erosion EROSION_5 through EROSION_6, depth UNDERGROUND, weirdness -1.1 through -0.85.

Important feature IDs:

- configured / placed minecraft:sulfur_spike_cluster;
- configured / placed minecraft:sulfur_spike;
- configured / placed minecraft:sulfur_pool;
- configured / placed minecraft:rooted_sulfur_spring;
- configured minecraft:sulfur_spring.

High-density examples:

- sulfur_spike_cluster: radius uniform 2..8, height 1..4, layer thickness 2..4; placed count uniform 48..96, height ABOVE_BOTTOM(0)..ABSOLUTE(256);
- sulfur_spike: placed count uniform 192..256, then a second count uniform 1..5, same vertical range;
- sulfur_pool: count 256 with its cave predicates.

This is an excellent built-in example of biome-scale regional resource presentation. It is not currently a technology sulfur source:

- material block: minecraft:sulfur;
- spike: minecraft:sulfur_spike;
- neither is a member of c:dusts/sulfur;
- canonicalization intentionally leaves tfmg:sulfur_dust as the only technology dust.

Without an explicit, gated conversion, players will see abundant sulfur that machines cannot use.

## Coal, coke, lignite, and graphite

Vanilla coal:

- configured feature minecraft:ore_coal: minecraft:ore, size 17;
- configured feature minecraft:ore_coal_buried: size 17, discard 0.5;
- placed feature minecraft:ore_coal_upper: count 30, uniform ABSOLUTE(136)..TOP;
- placed feature minecraft:ore_coal_lower: count 20, triangle ABSOLUTE(0)..ABSOLUTE(192).

This is a plentiful, reliable coke feedstock. TFMG Lignite adds a rare regional-looking alternate and crushes to an expected 0.95 coal per block.

Canonical TFMG coking:

- recipe ID tfmg:coking/coal;
- type tfmg:coking;
- one minecraft:coal;
- 1200 processing ticks;
- outputs one tfmg:coal_coke, 1 mB tfmg:creosote, and 30 mB tfmg:carbon_dioxide.

Active bypass:

- createmetallurgy:blasting/coke_from_coal: one coal -> one createmetallurgy:coke in 100 ticks;
- createmetallurgy:smelting/coke_from_coal: one coal -> one createmetallurgy:coke in 200 ticks.

Interop mismatch:

- createmetallurgy:coke is in c:coal_coke;
- TFMG does not put tfmg:coal_coke in c:coal_coke;
- TFMG only tags tfmg:coal_coke_dust as c:dusts/coal_coke and its block as c:storage_blocks/coal_coke.

Graphite bypass:

- bigreactors:blasting/graphite_from_coal;
- bigreactors:blasting/graphite_from_charcoal;
- bigreactors:smelting/graphite_from_coal;
- bigreactors:smelting/graphite_from_charcoal;
- all directly produce bigreactors:graphite_ingot, the only member found in c:ingots/graphite.

If Coke Ovens, Industrial Coking, or graphite metallurgy are supposed to be research gates, these recipes must be handled separately from worldgen.

## Vanilla and alternate mandatory ores

### Vanilla baseline

| Material | Configured feature | Size | Main placed features and exact stock placement |
|---|---|---:|---|
| Iron | minecraft:ore_iron; minecraft:ore_iron_small | 9; 4 | ore_iron_upper count 90 triangle Y 80..384; ore_iron_middle count 10 triangle -24..56; ore_iron_small count 10 uniform bottom..72 |
| Copper | minecraft:ore_copper_small; minecraft:ore_copper_large | 10; 20 | ore_copper and ore_copper_large each count 16 triangle Y -16..112; vanilla biome generation chooses where each is attached |
| Gold | minecraft:ore_gold; minecraft:ore_gold_buried | 9; 9 discard 0.5 | ore_gold count 4 triangle -64..32; ore_gold_lower uniform-count 0..1 at -64..-48; ore_gold_extra count 50 uniform 32..256 in its vanilla special biome context |
| Redstone | minecraft:ore_redstone | 8 | ore_redstone count 4 uniform bottom..15; ore_redstone_lower count 8 triangle ABOVE_BOTTOM(-32)..ABOVE_BOTTOM(32) |

### Regions Unexplored redstone province

- biome: regions_unexplored:redstone_caves;
- configured feature: regions_unexplored:special/ore_redstone_large;
- minecraft:ore, size 20, discard 0;
- placed feature: regions_unexplored:special/ore_redstone_large;
- count 16;
- trapezoid ABOVE_BOTTOM(0)..ABSOLUTE(112).

This creates a large biome-specific redstone surplus and is another useful no-Java regional model.

### Deeper and Darker alternate vanilla ores

These are in Otherside biome JSON rather than Overworld biome modifiers. They are late alternate supplies, not safe foundations for early research:

- deeperdarker:sculk_coal / iron / copper / gold / redstone in deeperdarker:blooming_caverns, deeperdarker:deeplands, and deeperdarker:echoing_forest;
- deeperdarker:gloomslate_coal / iron / copper / gold / redstone in deeperdarker:overcast_columns.

Placed IDs are the material names above. Counts are coal 7, iron 6, copper 5, gold 6, redstone 4. The configured IDs are prefixed deeperdarker:ore_; sizes are coal 14, iron 13, copper 15, gold 13, redstone 8, with host-specific air-exposure discard.

## Applied Energistics resource acquisition

AE2 supplies Certus through a structure, not an ore placed feature:

- structure ID ae2:meteorite;
- structure type ae2:ae2mtrt;
- biome tag #ae2:has_meteorites;
- optional tag member #minecraft:is_overworld;
- generation step top_layer_modification;
- structure-set ID ae2:meteorite;
- placement minecraft:random_spread;
- spacing 32 chunks;
- separation 8 chunks;
- salt 124895654;
- structure weight 1.

Installed config:

- spawnPressesInMeteorites=true;
- spawnFlawlessOnly=false.

Datapacks can change structure-set spacing/separation and the biome tag without Java. The meteorite piece's internal Certus and chest placement is code-driven and not exposed as a configured feature.

## Duplication, bypass, and softlock register

| Severity | Finding | Exact consequence | Recommended disposition |
|---|---|---|---|
| High | Mekanism uranium + ER Yellorite both active | Two Overworld ore families share c:uranium tags and can cross-feed tag recipes | Keep Yellorite as the geological early-nuclear ore and suppress Mekanism uranium generation, or make an explicit opposite choice |
| High | TFMG finite reserves are not decremented | infiniteDeposits=false does not produce finite gameplay | Fix PumpjackBaseBlockEntity with Java/mixin if depletion matters; otherwise document/set intentional infinity |
| High | Two independent oil maps | CDG output unification hides that the pumps and reserves are unrelated | Choose one canonical extraction model or explicitly stage the hybrid |
| High | Furnace/blast coke bypass | Coal skips tfmg:coking/coal and its infrastructure/byproducts | Remove or stage createmetallurgy:smelting/coke_from_coal and blasting/coke_from_coal |
| High | Direct ER graphite from coal/charcoal | Graphite can skip planned coking/metallurgy | Remove or stage the four graphite smelting/blasting IDs |
| High if Nether is gated | TFMG technology sulfur is Nether-only and its stock crushing yield is only 0.30 expected dust/block | A sulfur prerequisite before Nether access becomes circular; large early quantities can become an exploration wall even when the Nether is open | Guarantee Nether access first, keep early quantities low/provide prospecting, or add a deliberately gated Overworld route |
| Medium | Bauxite/Galena/Lignite/Fireclay share one 1/18 feature | Each pattern is only nominally selected around 1/72 chunks | Use prospecting, maps, or noise-gated regional replacement before making large quantities mandatory |
| Medium | Almost Unified worldgen and loot unification off | Physical duplicates remain and drops are not automatically canonical | Treat every source family explicitly |
| Medium | Create disableWorldGen controls addon resources | One global toggle can remove most TFMG and Create Metallurgy resources | Never use the global switch as a selective duplicate-removal tool |
| Medium | Vanilla Backport sulfur is visually abundant but noncanonical | Players may mine the “wrong” sulfur | Add a gated conversion or JEI/tooltip explanation; do not silently tag it unless balance permits |
| Medium | Osmium has 79 configured attempts/chunk across variants | Likely far above an exploration-driven factory-resource target | Rebalance or region-gate after an empirical new-world sample |
| Medium | Mekanism retrogen disabled | Changed generation affects only new chunks | Test in a disposable new world; document new-chunk requirement |
| Low | Lead | TFMG regular ore plus rare Galena is redundant but canonical and safe | Keep unless regional scarcity is desired |
| Low | Nickel, zinc, lithium, fluorite, tin, wolframite, cobalt | Each has an active source with no second same-material generator found | Safe baseline; tune only for regional design |

## What supports large clustered regional deposits without custom Java

### 1. Vanilla noise placement — best for solid ore provinces

Two generic placement modifiers are present in 1.21.1 and can be used on any placed feature:

minecraft:noise_threshold_count fields:

- noise_level: double;
- below_noise: integer attempt count;
- above_noise: integer attempt count.

It samples Biome.BIOME_INFO_NOISE at block X / 200 and Z / 200. Using 0 on one side and one or more attempts on the other creates broad provinces approximately many chunks across.

minecraft:noise_based_count fields:

- noise_to_count_ratio: integer;
- noise_factor: double spatial scale;
- noise_offset: double, default 0.

It samples the same noise at X / noise_factor and Z / noise_factor and converts it into a variable attempt count. A large noise_factor makes broader fields.

Combine either modifier with:

- minecraft:in_square;
- a height_range;
- minecraft:biome;
- a custom configured minecraft:ore feature;
- a NeoForge add_features modifier.

The vanilla OreConfiguration codec restricts size to 0..64. A province can contain several size-64 veins per allowed chunk, but a single vanilla ore feature cannot be encoded above 64.

### 2. Create layered ore — best for visible Satisfactory-style strata

create:layered_ore already works from datapack JSON. Current TFMG examples use size 32 and weighted layer patterns. It creates visually distinct strata and can be gated by the same vanilla noise placement modifiers.

This is suitable for Bauxite, Galena, Lignite, Fireclay, sulfur, and potentially large mixed industrial seams.

### 3. NeoForge biome modifiers — exact source replacement

Verified built-in removal schema:

{
  "type": "neoforge:remove_features",
  "biomes": "#namespace:biome_tag",
  "features": ["namespace:placed_feature"],
  "steps": ["underground_ores"]
}

Then add replacements with neoforge:add_features. This avoids globally disabling Create and permits one material at a time.

### 4. Custom biome tags — coarse geological regions

Attach deposits only to selected vanilla/modded biome tags. This is deterministic and datapack-only, but geological geography follows biome layout rather than an independent resource map.

### 5. CDGEvents.oilAmount — best for regional liquids

KubeJS can return an oil amount for each seed/chunk/biome set. This supports arbitrary deterministic cellular or noise provinces and can designate dry, finite, and infinite fields. It controls only CDG extraction.

### 6. Existing TFMG physical oil feature — local clusters only

Datapack placement can move or thin the opportunities, but the feature's empty config means its internal 1/20 gate and cluster geometry require Java to change.

### 7. Structures

AE2 meteorite spacing and separation are datapack-controlled. Structures are useful for sparse landmark resources, but their internal contents remain mod-code-driven.

## Recommended Phase 7 implementation plan

No implementation is performed by this audit.

1. Establish one geological source of truth per material.
   - Lead: TFMG regular ore plus optional Galena.
   - Nickel/lithium: TFMG.
   - Zinc: Create.
   - Tin/osmium/fluorite/salt: Mekanism.
   - Uranium: recommended Yellorite geology, then explicit Mekanism chemical processing.
   - Tungsten: Create Metallurgy wolframite.
   - Cobalt: Modern Foundry.
   - Sulfur: TFMG sulfur, with Nether-access ancestry verified.

2. Suppress stock duplicates with source-ID removal, not Create's global switch.
   - Example uranium removal target if Yellorite is retained:
     - biomes #mekanism:spawn_ores;
     - features mekanism:ore_uranium_small and mekanism:ore_uranium_buried;
     - step underground_ores.
   - Alternatively disable uranium in a maintained Mekanism world.toml override.

3. Replace uniform every-chunk availability with noise provinces.
   - Define industrial_colonies configured features using canonical blocks.
   - Use noise_threshold_count for clear resource/no-resource provinces.
   - Use noise_based_count where density should vary within a province.
   - Keep minecraft:ore size at or below 64.
   - Prefer create:layered_ore for Bauxite/Galena/Lignite/Sulfur presentation.

4. Make prospecting precede bulk consumption.
   - Rare 1/72 layered materials should not be demanded in quantity before the player gains a prospecting tool, survey map, or MineColonies exploration unlock.

5. Decide oil machine identity before changing geology.
   - A TFMG-first tree and CDG regional oil are mechanically different choices.
   - If TFMG remains canonical, a finite-reserve Java fix is required for depletion.
   - If CDG becomes canonical, implement the province map through CDGEvents.oilAmount and preserve the existing tfmg:crude_oil output tag.

6. Close transformation bypasses in the recipe phase.
   - createmetallurgy:smelting/coke_from_coal;
   - createmetallurgy:blasting/coke_from_coal;
   - bigreactors:smelting/graphite_from_coal;
   - bigreactors:smelting/graphite_from_charcoal;
   - bigreactors:blasting/graphite_from_coal;
   - bigreactors:blasting/graphite_from_charcoal.

7. Test only in disposable new worlds first.
   - Datapack registry load;
   - world creation;
   - locate/sample at least several thousand new chunks;
   - confirm biome-modifier removal before judging replacement rates;
   - inspect tags and drops in-game;
   - confirm no mandatory material requires an already-dependent research node.

8. Treat existing worlds separately.
   - Stock blocks already generated will remain.
   - Mekanism retrogen is currently disabled.
   - CDG and TFMG saved reservoir data persists independently.
   - A worldgen redesign needs a documented “new chunks only” rule or an explicit migration policy.

## Exact source paths used

Representative JAR paths:

- data/mekanism/neoforge/biome_modifier/*.json
- data/mekanism/worldgen/configured_feature/*.json
- data/mekanism/worldgen/placed_feature/*.json
- data/tfmg/neoforge/biome_modifier/*.json
- data/tfmg/worldgen/configured_feature/*.json
- data/tfmg/worldgen/placed_feature/*.json
- data/create/neoforge/biome_modifier/zinc_ore.json
- data/create/worldgen/configured_feature/zinc_ore.json
- data/create/worldgen/placed_feature/zinc_ore.json
- data/createmetallurgy/neoforge/biome_modifier/wolframite_ore.json
- data/bigreactors/neoforge/biome_modifier/yellorite*.json
- data/modernfoundry/neoforge/biome_modifier/cobalt_ore.json
- data/ae2/worldgen/structure/meteorite.json
- data/ae2/worldgen/structure_set/meteorite.json
- data/minecraft/worldgen/*/sulfur*.json inside Vanilla Backport

Installed configs/scripts:

- config/Mekanism/world.toml
- config/create-common.toml
- config/tfmg-common.toml
- config/createdieselgenerators-server.toml
- config/vanillabackport-common.toml
- config/ae2-common.toml
- config/almostunified/startup.json
- config/almostunified/unification/materials.json
- kubejs/server_scripts/industrial_petroleum_canonicalization.js
- kubejs/server_scripts/industrial_sulfur_canonicalization.js

Bytecode inspected where JSON was insufficient:

- com.drmangotea.tfmg.worldgen.deposits.OilDepositFeature
- com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity
- com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.TestSavedDataManager
- com.simibubi.create.infrastructure.worldgen.LayeredOreFeature
- com.simibubi.create.infrastructure.worldgen.ConfigPlacementFilter
- com.jesz.createdieselgenerators.world.OilChunksSavedData
- com.jesz.createdieselgenerators.compat.kubejs.CDGKubeJSPlugin
- com.blackgear.vanillabackport.common.worldgen.biomes.terrablender.OverworldRegion
- com.blackgear.vanillabackport.core.neoforge.VanillaBackportTerrablender
