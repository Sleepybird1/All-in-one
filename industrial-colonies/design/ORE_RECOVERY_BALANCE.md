# Ore and rock recovery balance

September 22 design update: see SURFACE_ORES_AND_HEMATITE.md for proposed ordinary magnetite ~1 mB and hematite 25 mB recovery. The table below documents the historical implemented balance, not those new targets. Basic/improved route mapping awaits recipe review; rich iron remains separately defined. No recipe migration is performed by this note.

Prepared September 11, 2026. The current candidate is progression/ore-yields/effective.material-catalog.json (300 recipes). Installation requires an APPLIED receipt in that directory. Author: tools/build_ore_yields.py, layered on tools/build_iron_blast_fix.py and the installed full-bucket catalog.

The user requested low recovery from basic melting and a worthwhile, ore-specific reward for proper processing. Rich iron explicitly gives 25 mB in Modern Foundry and 100 mB in the TFMG blast furnace. Rich hematite/magnetite drop minecraft:raw_iron, which enters the blast furnace directly without crushing. Finished ingots remain 100 mB, finished blocks 1,000 mB, nuggets 10 mB.

| Feed | Basic melting | Improved recovery per feed | Route |
|---|---:|---:|---|
| Rich iron's raw iron | 25 mB | 100 mB | Native TFMG blast furnace |
| Low-grade hematite/magnetite | 3 mB | 8 mB | Crush, then TFMG blast reduction |
| Rich copper's raw copper | 15 mB | 100 mB | Crush into four chalcopyrite feeds, wash, melt |
| Chalcopyrite | 4 mB | 25 mB | Crush, wash, melt |
| Rich zinc's raw zinc | 12 mB | 60 mB | Crush into four sphalerite feeds, then existing chemical recovery |
| Sphalerite | 2 mB | 15 mB | Existing leach, precipitation and reduction |
| Raw gold | 10 mB | 25 mB | Native TFMG blast processing |
| Cassiterite | 3 mB | 20 mB | Existing gravity concentration; rich tin gives four concentrates = 80 mB |
| Galena | 3 mB | 20 mB | Roast and reduce; rich galena gives four feeds = 80 mB |
| Argentite | 2 mB | 10 mB | Existing chemical extraction |

Both TFMG iron routes and the gold route produce 10 mB molten slag. Processing time is 30 seconds, converting the previous IE iron reduction's 600 ticks correctly. Normal furnace fuel and hot-air behavior apply. Existing reduced-iron fraction items still melt for 8 mB.

Chemical-only ores do not gain premature direct-melting shortcuts. Their final recovered portion now yields: nickel 25 mB; aluminum 25; magnesium 20; lithium 15; beryllium 10. Rich nickel and bauxite retain four-feed outputs (100 mB). Cobalt remains the existing 10 mB coproduct. Lead purification retains the same metal quantity as crude lead; purity is not extra mass.

Consolidation batches reward successful advanced ore processing: titanium and chromium use four recovered portions per ingot, tungsten five, osmium ten. Boron uses twenty recovered portions for three ingots (15 mB equivalent per portion). Platinum and iridium retain twenty portions per ingot; trace platinum/iridium and the crude ultramafic lottery remain scarce. Their chemical machinery and reagent requirements are retained. Nonmetal rock routes (silicon, graphite, phosphate, sulfur and nuclear feed compounds) already reward their dedicated processing chains and are retained without inventing ingot-based yields.

Raw-metal storage blocks melt for exactly nine loose raw items: iron 225 mB, copper 135, gold 90 and zinc 108. These raw storage blocks are distinct from 1,000 mB finished-metal blocks.

The pass changes 31 ore-recovery recipes relative to the TFMG correction, including four new routes. It preserves all finished-metal melt/cast values, alloy ratios, semiconductor recipes, reagent input amounts, chemical solution volumes, machine requirements and nonmetal-product recipes. The original IE dust recipe is replaced by TFMG; it is not an additional competing route.

Validation includes exact native decoding/loading of all 300 recipes, loaded ore-output assertions, raw-block mass equivalence, native TFMG lookup and consumption/output checks, existing metal-conversion regression tests, semiconductor checks, and the combined world-generation checks. The TFMG completion fixture controls furnace size/timer to isolate recipe handling; it is not a new full multiblock construction test.
