# Worldgen biome assignments and configuration defaults

Status: configuration foundation for the authoritative Industrial Colonies Overworld resource specification. These files do not define processing recipes, machine/tool progression, or final recovery yields.

## Files and source of authority

- `src/main/resources/data/industrial_colonies/geology/settings.json`: shared placement, quality, terrain exposure, micro, trace, placer and economy settings.
- `src/main/resources/data/industrial_colonies/geology/biome_families.json`: eleven logical family-to-exact-biome-ID arrays.
- `src/main/resources/data/industrial_colonies/geology/deposit_families.json`: 24 deposit definitions, associated-ore rules and per-family micro settings.

Authoritative attachment: `C:/Users/GodPC/.codex/attachments/34fe6255-ad44-4a38-a19a-72fbd308315e/pasted-text.txt`.

SHA-256: `FFC253169D41B8B1439877D61597E6770B3F68F57ED33DC7A774CC490C8B4A68`.

Biome IDs were checked against the installed `regions-unexplored-0.6.2-neoforge-21.1.jar` (SHA-256 `CCF32ED714F2724F54406B9E02A8D6F94D87DC5C72397BC39B3D6ED8F32412EA`) and Minecraft 1.21.1 client resources (SHA-256 `499F6897D1837516680F3114072D8106E11C9ADCD933FE5CF051B551089B0C99`). Primary RU archive evidence: `data/regions_unexplored/worldgen/biome/*.json`, `data/regions_unexplored/tags/worldgen/biome/all_overworld.json`, `removed.json`, `all_nether.json`, and its `data/{minecraft,c}/tags/worldgen/biome` classification tags. Vanilla names and membership were checked against `assets/minecraft/lang/en_us.json` and `data/minecraft/tags/worldgen/biome/*.json`.

## Consumer semantics and exclusions

- Arrays may overlap. The mineral planner uses the **arithmetic mean of explicitly mapped applicable positive biome weights**; any applicable explicit zero weight or hard exclusion vetoes that deposit. Unmapped families do not dilute an explicit weight. Only when none of the location's families has an explicit weight does the planner fall back to compatible/default 1.0. Oil has its own separate overlap rule.
- Family arrays are editable gameplay geology assignments informed by source biome tags/names, not an additional simulated geology system. Tectonic changes terrain; it does not require invented `tectonic:*` biome IDs here. Actual elevation/relief classification must remain separate from biome membership.
- Underground cave-biome IDs should inherit their surface-column geology when classifying deposits. Do not infer tropical, forest or sedimentary geology solely from an underground cave biome's decorative identity.
- `hardBiomeExclusions` contains logical family names. Borax repeats the approved tropical_humid and wetland zero weights as explicit vetoes. No new mineral terrain bans were invented.
- `primaryMaterials` describes production identity, not physical host appearance: graphite produces carbon; Pentlandite's association is cobalt; the PGM family produces Os/Pt/Ir. Coal is independent of Graphite.
- Oil is a separate generator/configuration concern. Reuse these categories, but its mountain/highland, volcanic/ashen and extreme-cold mountain prohibitions must always beat a simultaneous positive basin/forest/lowland weight. These deposit files do not generate Oil.

## Exact assignments

11 families contain 120 distinct IDs: 50 vanilla and 70 RU. Repeated IDs across families are intentional.

### mountain_highland

Mountain and exposed-highland geology. Includes tagged RU mountains/slopes and explicitly tall cliff/spire terrain; overlaps arid or cold categories where appropriate.

Vanilla:

- `minecraft:cherry_grove`
- `minecraft:frozen_peaks`
- `minecraft:grove`
- `minecraft:jagged_peaks`
- `minecraft:meadow`
- `minecraft:savanna_plateau`
- `minecraft:snowy_slopes`
- `minecraft:stony_peaks`
- `minecraft:windswept_forest`
- `minecraft:windswept_gravelly_hills`
- `minecraft:windswept_hills`
- `minecraft:windswept_savanna`

Regions Unexplored:

- `regions_unexplored:arid_mountains` — legacy/removed compatibility ID
- `regions_unexplored:highland_fields`
- `regions_unexplored:icy_heights`
- `regions_unexplored:mountains` — legacy/removed compatibility ID
- `regions_unexplored:pine_slopes`
- `regions_unexplored:spires`
- `regions_unexplored:towering_cliffs`
- `regions_unexplored:windswept_maple_forest`
- `regions_unexplored:wisteria_grove`

### arid_badlands

Dry, badland and savanna geology. Desert and outback basins also receive desert_basin; a dry mountain remains mountain_highland as well.

Vanilla:

- `minecraft:badlands`
- `minecraft:desert`
- `minecraft:eroded_badlands`
- `minecraft:savanna`
- `minecraft:savanna_plateau`
- `minecraft:windswept_savanna`
- `minecraft:wooded_badlands`

Regions Unexplored:

- `regions_unexplored:arid_mountains` — legacy/removed compatibility ID
- `regions_unexplored:baobab_savanna`
- `regions_unexplored:dry_bushland`
- `regions_unexplored:joshua_desert`
- `regions_unexplored:outback`
- `regions_unexplored:saguaro_desert`
- `regions_unexplored:steppe` — legacy/removed compatibility ID

### tropical_humid

Warm humid jungle/tropical vegetation and the tropical delta/river contexts. Temperate wet forests are not automatically tropical.

Vanilla:

- `minecraft:bamboo_jungle`
- `minecraft:jungle`
- `minecraft:mangrove_swamp`
- `minecraft:sparse_jungle`

Regions Unexplored:

- `regions_unexplored:ancient_delta`
- `regions_unexplored:bamboo_forest`
- `regions_unexplored:eucalyptus_forest`
- `regions_unexplored:rainforest`
- `regions_unexplored:sparse_rainforest`
- `regions_unexplored:tropical_river`
- `regions_unexplored:tropics`

### sedimentary_plains

Lowland plains, river sediment, selected swamps and coasts, plus desert/outback basins. A gameplay geology grouping, not a claim that every real-world biome has one bedrock type.

Vanilla:

- `minecraft:beach`
- `minecraft:desert`
- `minecraft:frozen_river`
- `minecraft:mangrove_swamp`
- `minecraft:mushroom_fields`
- `minecraft:plains`
- `minecraft:river`
- `minecraft:savanna`
- `minecraft:snowy_beach`
- `minecraft:snowy_plains`
- `minecraft:sunflower_plains`
- `minecraft:swamp`

Regions Unexplored:

- `regions_unexplored:barley_fields` — legacy/removed compatibility ID
- `regions_unexplored:bayou`
- `regions_unexplored:chalk_cliffs`
- `regions_unexplored:clover_plains`
- `regions_unexplored:cold_river`
- `regions_unexplored:fen`
- `regions_unexplored:flower_fields`
- `regions_unexplored:frozen_tundra` — legacy/removed compatibility ID
- `regions_unexplored:fungal_fen`
- `regions_unexplored:grassland`
- `regions_unexplored:grassy_beach`
- `regions_unexplored:marsh`
- `regions_unexplored:muddy_river`
- `regions_unexplored:old_growth_bayou`
- `regions_unexplored:outback`
- `regions_unexplored:poppy_fields`
- `regions_unexplored:prairie`
- `regions_unexplored:pumpkin_fields` — legacy/removed compatibility ID
- `regions_unexplored:rocky_meadow` — legacy/removed compatibility ID
- `regions_unexplored:shrubland`
- `regions_unexplored:steppe` — legacy/removed compatibility ID
- `regions_unexplored:tropical_river`
- `regions_unexplored:tundra`

### coastal_oceanic

All vanilla oceans and shores, RU ocean biomes and explicit beaches/coastal cliffs. Rivers are not oceans.

Vanilla:

- `minecraft:beach`
- `minecraft:cold_ocean`
- `minecraft:deep_cold_ocean`
- `minecraft:deep_frozen_ocean`
- `minecraft:deep_lukewarm_ocean`
- `minecraft:deep_ocean`
- `minecraft:frozen_ocean`
- `minecraft:lukewarm_ocean`
- `minecraft:mushroom_fields`
- `minecraft:ocean`
- `minecraft:snowy_beach`
- `minecraft:stony_shore`
- `minecraft:warm_ocean`

Regions Unexplored:

- `regions_unexplored:chalk_cliffs`
- `regions_unexplored:grassy_beach`
- `regions_unexplored:gravel_beach`
- `regions_unexplored:hyacinth_deeps`
- `regions_unexplored:rocky_reef`
- `regions_unexplored:tropics`

### volcanic_ashen

RU ashen_woodland, inferno and the legacy scorching_caves definition. Vanilla has no assigned Overworld volcanic biome; Nether basalt_deltas is deliberately excluded.

Vanilla:

None.

Regions Unexplored:

- `regions_unexplored:ashen_woodland`
- `regions_unexplored:inferno`
- `regions_unexplored:scorching_caves` — legacy/removed compatibility ID

### wetland

Swamps, deltas, rivers and selected wet woodland. Borax is vetoed here, including when another favorable category overlaps.

Vanilla:

- `minecraft:frozen_river`
- `minecraft:mangrove_swamp`
- `minecraft:river`
- `minecraft:swamp`

Regions Unexplored:

- `regions_unexplored:ancient_delta`
- `regions_unexplored:bayou`
- `regions_unexplored:cold_river`
- `regions_unexplored:fen`
- `regions_unexplored:fungal_fen`
- `regions_unexplored:marsh`
- `regions_unexplored:muddy_river`
- `regions_unexplored:old_growth_bayou`
- `regions_unexplored:tropical_river`
- `regions_unexplored:willow_forest`

### cold_high_altitude

Cold mountain slopes/peaks/spires only. Ordinary snowy plains and boreal forests are not mislabeled high-altitude terrain.

Vanilla:

- `minecraft:frozen_peaks`
- `minecraft:grove`
- `minecraft:jagged_peaks`
- `minecraft:snowy_slopes`

Regions Unexplored:

- `regions_unexplored:icy_heights`
- `regions_unexplored:spires`

### ordinary_forest

Temperate, boreal, mixed and old-growth forests; mountain forests can overlap mountain_highland.

Vanilla:

- `minecraft:birch_forest`
- `minecraft:cherry_grove`
- `minecraft:dark_forest`
- `minecraft:flower_forest`
- `minecraft:forest`
- `minecraft:old_growth_birch_forest`
- `minecraft:old_growth_pine_taiga`
- `minecraft:old_growth_spruce_taiga`
- `minecraft:snowy_taiga`
- `minecraft:taiga`
- `minecraft:windswept_forest`

Regions Unexplored:

- `regions_unexplored:alpha_grove`
- `regions_unexplored:autumnal_maple_forest`
- `regions_unexplored:blackwood_taiga`
- `regions_unexplored:boreal_taiga`
- `regions_unexplored:cold_boreal_taiga`
- `regions_unexplored:cold_deciduous_forest` — legacy/removed compatibility ID
- `regions_unexplored:deciduous_forest` — legacy/removed compatibility ID
- `regions_unexplored:frozen_pine_taiga`
- `regions_unexplored:golden_boreal_taiga` — legacy/removed compatibility ID
- `regions_unexplored:magnolia_woodland`
- `regions_unexplored:maple_forest`
- `regions_unexplored:mauve_hills` — legacy/removed compatibility ID
- `regions_unexplored:old_growth_boreal_taiga`
- `regions_unexplored:old_growth_forest`
- `regions_unexplored:old_growth_golden_boreal_taiga`
- `regions_unexplored:orchard`
- `regions_unexplored:pine_slopes`
- `regions_unexplored:pine_taiga`
- `regions_unexplored:redwoods`
- `regions_unexplored:silver_birch_forest`
- `regions_unexplored:sparse_redwoods`
- `regions_unexplored:temperate_grove` — legacy/removed compatibility ID
- `regions_unexplored:willow_forest`
- `regions_unexplored:windswept_maple_forest`
- `regions_unexplored:wisteria_grove`

### ordinary_plains

Ordinary open plains/meadows and cold open lowlands; highland_fields also carries mountain_highland.

Vanilla:

- `minecraft:ice_spikes`
- `minecraft:meadow`
- `minecraft:mushroom_fields`
- `minecraft:plains`
- `minecraft:savanna`
- `minecraft:snowy_plains`
- `minecraft:sunflower_plains`

Regions Unexplored:

- `regions_unexplored:barley_fields` — legacy/removed compatibility ID
- `regions_unexplored:clover_plains`
- `regions_unexplored:flower_fields`
- `regions_unexplored:frozen_tundra` — legacy/removed compatibility ID
- `regions_unexplored:grassland`
- `regions_unexplored:highland_fields`
- `regions_unexplored:poppy_fields`
- `regions_unexplored:prairie`
- `regions_unexplored:pumpkin_fields` — legacy/removed compatibility ID
- `regions_unexplored:rocky_meadow` — legacy/removed compatibility ID
- `regions_unexplored:shrubland`
- `regions_unexplored:steppe` — legacy/removed compatibility ID
- `regions_unexplored:tundra`

### desert_basin

Vanilla deserts/badlands and RU desert/outback basins. No arid-mountain ID is assigned automatically, preventing a basin/oil interpretation of mountains.

Vanilla:

- `minecraft:badlands`
- `minecraft:desert`
- `minecraft:eroded_badlands`
- `minecraft:wooded_badlands`

Regions Unexplored:

- `regions_unexplored:joshua_desert`
- `regions_unexplored:outback`
- `regions_unexplored:saguaro_desert`

## Compatibility IDs and deliberately unclassified cave biomes

RU's all_overworld tag contains 73 IDs, including old definitions also listed in its removed tag. Mapping those existing IDs permits old-world compatibility; it is **not evidence that RU 0.6.2 currently selects them for new terrain**. The 13 mapped legacy IDs are:

- `regions_unexplored:arid_mountains`
- `regions_unexplored:barley_fields`
- `regions_unexplored:cold_deciduous_forest`
- `regions_unexplored:deciduous_forest`
- `regions_unexplored:frozen_tundra`
- `regions_unexplored:golden_boreal_taiga`
- `regions_unexplored:mauve_hills`
- `regions_unexplored:mountains`
- `regions_unexplored:pumpkin_fields`
- `regions_unexplored:rocky_meadow`
- `regions_unexplored:scorching_caves`
- `regions_unexplored:steppe`
- `regions_unexplored:temperate_grove`

The three remaining Overworld-tagged RU IDs are `regions_unexplored:bioshroom_caves`, `regions_unexplored:prismachasm`, and `regions_unexplored:redstone_caves`. They intentionally have no invented surface geology assignment. Likewise vanilla `minecraft:deep_dark`, `minecraft:dripstone_caves`, and `minecraft:lush_caves` use surface-column classification. `ancient_delta` has explicit wet delta affinities; `inferno` is assigned volcanic and the legacy `scorching_caves` definition is volcanic. No Nether or End biome is mapped. In particular `regions_unexplored:redstone_abyss` is a Nether/removed ID and is excluded.

## Deposit inventory and approved/provisional values

All 23 approved rock/coal/radioactive biome-weight profiles, depth profiles, and normal-size ranges are copied from sections XII, XVI and XIX. Gold is the 24th entry, using regular `minecraft:gold_ore`, not an invented low-yield host. Coal uses regular `minecraft:coal_ore`. Uranium uses `industrial_colonies:uraninite`; Thorium uses `industrial_colonies:thorium_ore`.

| Deposit ID | Primary material(s) | Spacing family | Same-family spacing | Normal host size | Normal rich fraction | Base weight |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| hematite | iron | iron | 1500 | 3000–5000 | 0.08 | 5 provisional |
| magnetite | iron | iron | 1500 | 3000–6000 | 0.1 | 5 provisional |
| chalcopyrite | copper | copper | 1500 | 2500–5000 | 0.07 | 5 provisional |
| sphalerite | zinc | zinc | 1875 | 1500–3000 | 0.06 | 3 provisional |
| galena | lead | lead | 1875 | 1500–3000 | 0.06 | 3 provisional |
| pentlandite | nickel | nickel | 1875 | 1500–3000 | 0.05 | 3 provisional |
| bauxite | aluminum | aluminum | 2000 provisional | 3000–6000 | 0.05 | 5 provisional |
| spodumene_rock | lithium | lithium | 2250 | 1000–2500 | 0.04 | 1 provisional |
| argentite | silver | silver | 2500 | 750–1500 | 0.03 | 0.6 provisional |
| wolframite_rock | tungsten | tungsten | 2250 | 750–1500 | 0.03 | 1 provisional |
| dolomite | magnesium | magnesium | 2000 provisional | 3000–6000 | 0 | 3 provisional |
| graphite_rock | carbon | graphite | 2250 provisional | 1500–3000 | 0 | 2 provisional |
| phosphate_rock | phosphorus | phosphorus | 2000 provisional | 3000–6000 | 0 | 2 provisional |
| ultramafic_rock | osmium, platinum, iridium | pgm | 3500 | 1500–3000 | 0.04 | 0.4 provisional |
| ilmenite | titanium | titanium | 2250 | 2000–4000 | 0.04 | 2 provisional |
| bertrandite | beryllium | beryllium | 2500 provisional | 750–1500 | 0 | 1 provisional |
| borax_rock | boron | boron | 2250 provisional | 1500–3500 | 0 | 1 provisional |
| cassiterite | tin | tin | 1875 | 1000–2000 | 0.04 | 2 provisional |
| chromite | chromium | chromium | 2250 | 1500–3000 | 0.04 | 2 provisional |
| cinnabar | redstone | redstone | 2000 provisional | 2000–4000 | 0 | 2 provisional |
| uranium | uranium | uranium | 3000 | 1000–2000 | 0 | 1 provisional |
| thorium | thorium | thorium | 3000 | 1000–2000 | 0 | 1 provisional |
| coal | coal | coal | 1125 | 3000–8000 | 0 | 6 provisional |
| gold | gold | gold | 2750 | 750–1500 provisional | 0 | 0.6 provisional |

Spacing ranges use their arithmetic midpoints: Coal 1125, Zinc/Lead/Nickel/Tin 1875, Titanium/Tungsten/Lithium/Chromium 2250, Gold 2750, Uranium and Thorium 3000, PGM 3500. Iron and Copper retain exact 1500; Hematite and Magnetite share `spacingFamily: iron`, so their combined family spacing is 1500. Uranium and Thorium retain separate spacing families; their approved 2500–3500 range applies to each. Global spacing remains 800. Where no spacing was specified, the table flags the new tuning value provisional.

No rich block was invented for Dolomite, Graphite, Phosphate, Bertrandite, Borax or Cinnabar. Their `richOres` arrays are empty and normalRichOrePercent is 0. Coal, Gold, Uranium and Thorium likewise have no fabricated separate rich form. The sole PGM major family uses total rich density 0.04, then weights Osmium/Platinum/Iridium 0.70/0.25/0.05. Cobalt and Diamond exist only as approved associations/micro exceptions, not independent major families.

All `baseWeight` values are provisional starting rarity tiers: Coal 6; Hematite/Magnetite/Chalcopyrite/Bauxite 5; Sphalerite/Galena/Pentlandite/Dolomite 3; specialized Graphite/Phosphate/Ilmenite/Cassiterite/Chromite/Cinnabar 2; strategic Spodumene/Wolframite/Bertrandite/Borax/Uranium/Thorium 1; Argentite/Gold 0.6; Ultramafic 0.4. Each Iron source has its own selection weight but shares spacing. These are relative weights, not probabilities or finalized consumption balance.

Gold's 750–1500 normal block count, full biome profile, depth [0.5,1.5,2.0], and baseWeight 0.6 are provisional because the specification gives no exact profile/size. Its 2750 spacing follows the approved midpoint. Gold micro sizes remain 1–2, with a provisional 2% three-block jackpot. No finished-ingot output is inferred from any block count.

## Associated ores and exact boundary conventions

- Percentages are fractions of the original actual generated host formation and are independent of ordinary rich-ore quotas.
- Cobalt: exact fraction ranges [0,0.0025], [0,0.005], [0.0075,0.01], [0.015,0.02]. Poor/Normal occurrence chances 0.50/0.75 are explicitly provisional; Rich/Exceptional are guaranteed. Successful positive guaranteed quantities need at least one block. Cluster size 1–3 is provisional.
- Uranium → Thorium: guaranteed fractions 0.005, 0.01, 0.02, 0.03. No chance gate may cancel them.
- Thorium → Uranium: exact occurrence chances 0.05, 0.10, 0.20, 0.35. Successful quantity ranges [0.0025,0.005], [0.005,0.01], [0.0075,0.015], [0.01,0.02] are explicitly provisional; no amount was finalized in the specification.
- Graphite → Diamond: no diamonds above -20. Inclusive -40..-20 uses [0,0.0001,0.00025,0.0005]; -55..-41 uses [0.0001,0.00025,0.0005,0.001]; -64..-56 uses [0.00025,0.0005,0.001,0.002]. This resolves the overlapping textual -40 boundary in favor of the upper listed band, while -55 belongs to the middle band and below -55 to the deepest. Clusters are normally 1–2; 3-block jackpot chance 0.02 is provisional. Sub-block expectations must not be rounded into a guaranteed one-block diamond quota for every small formation.
- No Sulfur/Mercury ore generation accompanies Cinnabar.

`associated[].byQuality` is four [min,max] fraction pairs. `chanceByQuality` is four occurrence chances. For `type: depth_percentage`, `depthBands` holds {minY,maxY,byQuality:[four fractional rates]}; missing bands yield zero. Optional clusterMin/clusterMax, jackpotMax/jackpotChance and guaranteeWhenPositive fields express the approved size/guarantee constraints; the generator must honor them, not merely preserve the JSON metadata.

## Shared tuning, micro, trace and placer

`settings.json` keeps the approved quality distributions, quality size/richness multipliers, and normal/mountain/extreme terrain exposure multipliers exact. Region size 512, attempt chance 0.65, center bounds -60..64, and interpolation anchors 42/0/-44 are operational provisional choices. Accepted deposit density depends on spacing rejection; 0.65 is not the fraction of chunks containing a deposit.

Micro settings preserve eligible rich ores only: the two Iron sources, Copper, Zinc, Lead, Nickel, Tin, Aluminum, Lithium, Titanium, Chromium, Silver, Tungsten, Gold, Uranium and Thorium. PGM, Cobalt and Redstone cannot generate independently. Graphite has no rich micro block; Diamond uses the explicit global micro exception with maximum Y -20. Most eligible patches are 1–2; Uranium/Thorium are one block; only Gold/Diamond allow rare three-block jackpots. Occurrence chances are provisional. Disabled entries carry chance 0.

The mineral micro pool selects an eligible family by base, biome and depth suitability, then that selected family's `micro.chance` determines its actual per-chunk occurrence roll. It is not merely a normalized selection weight. Shared `settings.micro.frequencyMultiplier` (default 1) scales those chances and `maxChancePerChunk` caps them; `maxBlocks` caps occurrence size. A cheap maximum-chance precheck avoids biome/depth sampling on chunks that cannot pass any configured family roll. Diamond retains a separate chance and depth/suitability check. Actual successful block placement also depends on finding replaceable stone; these are attempt probabilities, not guarantees of a placed ore.

Trace starts provisionally at four attempts/chunk, chance 0.35/attempt, at most three blocks below the surface. Weighted sources are Iron/Hematite 3, Copper/Chalcopyrite 3 and Coal/default Coal Ore 4; each starts with 1–3 blocks. These rates require a measured exploration/yield test for several ingots' worth of early tools and a small workshop. Do not claim that final output target is proven without final recovery values and gameplay testing. Gold uses the separate placer system rather than a fabricated trace host.

Placer starts provisionally at three attempts/chunk, chance 0.035/attempt, riverbank reach eight blocks, 1–3 flakes. Exact river IDs are minecraft:river, minecraft:frozen_river, regions_unexplored:cold_river, regions_unexplored:muddy_river, regions_unexplored:tropical_river. Favorable surrounding geology categories are mountain_highland, arid_badlands and sedimentary_plains. Flakes are not a low-yield Gold host rock. Proper Gold Ore must remain substantially more productive after later economy testing.

The only finalized metal volumes are 1000 mB/ingot and 9000 mB/storage block. Provisional concepts Gold Flake 1 mB, Gold Nugget 10 mB, Raw Gold 100 mB and Raw Iron 200 mB are metadata, not recipes. No tool/casting/machine progression is implemented in these files.

## Editing and validation checklist

- Change family membership in biome_families.json; preserve exact namespace IDs and explicit zero vetoes.
- Change a deposit's biomeWeights/depthWeights, baseWeight, sameFamilyMinSpacing, normalSizeMin/Max or normalRichOrePercent in deposit_families.json. The depth array order is shallow, mid, deep. The quality array order is poor, normal, rich, exceptional.
- Change global spacing, probabilities/multipliers, terrain exposures, micro scaling/caps, trace or placer rates in settings.json. Change actual per-family occurrence rates in deposit_families.json under micro.chance; do not treat that field as a relative selection weight.
- Edit associated fraction/chance/band tables instead of hardcoding material-specific exceptions in Java.
- Treat provisionalFields and settings.provisional as documentation, not generation rules. Remove a provisional marker only after an intentional approved balance decision.
- Test shared Iron spacing, globally overlapping category zero vetoes (especially Borax), PGM split, guaranteed Uranium→Thorium, nonguaranteed reverse association, Diamond depths, cross-chunk determinism and tiny micro maximum size.
- Verify actual accepted spacing and generated/replaced host counts in debug output; intended size is not necessarily placed size at cavities or world bounds. Final rich quotas must be derived from actual host count.
