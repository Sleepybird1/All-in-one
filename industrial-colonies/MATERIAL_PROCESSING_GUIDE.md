# Material processing: player and pack-development guide

Version **0.5.0 is installed in All in one**, dated 9 September 2026. All 299 recipes passed native verification; Lithosphere A/B and the full 241-mod client checks also passed. These are bounded implementation checks, not a complete survival playthrough or powered-factory test. Start the pack normally to use the recipes; the quantities below are the installed defaults. See **MATERIAL_PROCESSING_ACCEPTANCE.md** for evidence, scope and the recovery record.

## Where the machines fit

Ordinary Create crushing, basin mixing and selected fan washing start material preparation. The TFMG Industrial Mixer now has a mechanical-crafting recipe using screws, a shaft, steel frames, an ordinary steel casing and a large steel cogwheel: it does not require its own downstream electronics.

The Copper line builds the electrode holder and fireproof Chemical Vat. Powered vat electrodes provide the first caustic and Aluminum without requiring Aluminum-bearing circuit machinery first. Salt dissolves into Brine; powered Brine electrolysis supplies Sodium Hydroxide. Existing TFMG Sulfur + Nitrate + Water chemistry supplies early Sulfuric Acid.

Weathered Iron builds the reagent machinery: the Electrolytic Separator, Chemical Oxidizer, Chemical Infuser, chemical storage, evaporation parts and Rotary Condensentrator. The rotary bridges fluid handling and Mekanism chemicals. The early Metallurgic Infuser can use Osmium recovered through the crude Ultramafic route.

The six Industrial Iron machine assemblies—press, deployer, mixer, saw, fan and roller—each install **one Titanium ingot, one Tungsten ingot and one High-Purity Silicon**, alongside their existing advanced electronics. They are assembled on Weathered machines. Titanium and Tungsten therefore consolidate in the existing Immersive Engineering Arc Furnace, not a machine that first needs Industrial Iron. Chromium's separation step specifically requires the **Industrial Iron Encased Fan**; an ordinary or Weathered fan is insufficient.

TFMG vat recipes still require their stated heat, lining, size and installed machinery. A recipe that names two electrodes genuinely needs powered electrodes; a mixer alone does not replace them. Modern Foundry handles melting/casting, while intentional Brass and Bronze alloys belong in heated Create mixers.

## Cinnabar: the exact manual interaction

This slow route is for a real player, one rock at a time:

1. Fuel and light a **Create Low Heat Basic Burner**. Hold exactly **one Cinnabar** in your main hand and right-click the burner.
2. Keep that one rock selected and keep looking directly at the same lit burner, within **4.5 blocks**, for **1,200 ticks: 60 seconds at 20 TPS**. One click starts the work; there is no automatic repeat. Looking away, changing the item, leaving reach or losing the lit burner cancels progress without consuming the rock. Another player cannot use that same burner simultaneously.
3. When the rock becomes **Roasted Cinnabar**, put exactly one in your **off hand**. Hold a working **Immersive Engineering Engineer's Hammer** in your main hand—not a TFMG oil hammer.
4. Right-click the **top face of a solid block** while looking at it. One strike replaces the off-hand rock with **one Redstone**, applies one hammer durability damage, and starts a **20-tick / one-second** cooldown.

Deployers, fake players and stack-sized hand operations cannot batch this manual route. The industrial alternative is different: crush Cinnabar into two dust, then process **four dust → eight Redstone** in an **unheated regular mixer**, with small Sulfur and Mercury-residue chances. Its processing time is machine-dependent, not the manual 60-second timer.

## What to do with each resource

Arrows describe separate recipes, not ingredients to put into one machine. “Melt” means the prepared product enters the Foundry and is then cast; it does not mean every raw rock can skip its chemistry.

### Early recovery and bulk materials

| Resource | Implemented route |
|---|---|
| Hematite / Magnetite → Iron | Crush to Iron-Bearing Dust → carbon-fueled IE Blast Furnace reduction, producing slag → melt the reduced fraction. Poor direct melting remains: **25 mB**, versus **75 mB** after reduction. |
| Chalcopyrite → Copper | Crush → ordinary **Fan + Water** washing → Copper Dust → melt. **20 mB** direct versus **50 mB** processed. |
| Cassiterite → Tin | Crush → water agitation in a mixer → Heavy Cassiterite Concentrate → melt. This is **not fan washing**. **20 mB** direct versus **75 mB** concentrated; Rich Tin yields four concentrates. |
| Sphalerite → Zinc | Crush → acid dissolution → Sodium Hydroxide precipitation → coke reduction → melt. **12 mB** direct versus **75 mB** processed. |
| Galena → Lead | Crush → low-heat roast → coke reduction → Crude Lead Granules → melt. Optional electrode/acid purification produces High-Purity Lead without multiplying metal. **15 mB** direct versus **75 mB** processed. |
| Argentite → Silver | Crush → low-heat roast → acid leach → precipitation → melt. **12 mB** direct versus **60 mB** processed. |
| Gold | Existing Raw Gold melts for **100 mB**. Gold Flakes are valued at **1 mB**, but the proposed river-sediment washing acquisition is deliberately inactive. |
| Coal | Coal remains fuel. Pulverization adds a Coke Oven feed that produces Coke, Coal Tar and a little Hydrogen. Tar distillation supplies Creosote and Naphtha, not a free Sulfur source. |
| Brass / Bronze | Heated mixer: three Copper ingots + one Zinc/Tin ingot → four Brass/Bronze ingots. Foundry tank alloying is disabled by the processing policy. |

Rich Iron, Copper and Zinc ores use the corresponding raw-metal drops, with Silk Touch retaining the block. The other chemical rich ores retain their own feed blocks and improve concentrate quantity; “rich” does not bypass purification.

### Chemical and electrical metals

| Resource | Implemented route |
|---|---|
| Pentlandite → Nickel / minor Cobalt | Acid leach → clarification → Nickel precipitation → roast → Hydrogen reduction → melt. Consumed mother liquor has one **8%** Cobalt recovery roll. Rich Nickel is **Nickel-only**; Cobalt-rich ore can yield a smaller Nickel byproduct. |
| Bauxite → Aluminum | Powder → caustic digestion → red-mud removal → Alumina precipitation → **powered electrode reduction** → granules → melt. No direct Bauxite smelting shortcut. |
| Dolomite → Magnesium | Calcine → acid separation → purified Magnesium Chloride → **powered electrolysis** → Magnesium powder → melt. |
| Ilmenite → Titanium | Purify → chlorinate → purify Titanium Tetrachloride → Magnesium reduction → Titanium Sponge → **eight sponges per Arc Furnace ingot**. Returned Magnesium Chloride can be electrically recovered, not duplicated. |
| Wolframite → Tungsten | Alkaline leach → tungstate precipitation → oxide → Hydrogen reduction → **eight powders per Arc Furnace ingot**. |
| Chromite → Chromium | Alkaline roast → **Industrial Iron fan separation** → purification → reduction → **eight powders per Arc Furnace ingot**. |
| Spodumene → Lithium | Thermal activation → acid leach → precipitation → **electrochemical reduction** → melt. |
| Bertrandite → Beryllium | Leach → precipitate → oxide → large firebrick vat with powered electrodes → low-volume Beryllium powder → melt. |
| Borax Rock → Boron | Existing NC Borax Dust → purified borate → Boric Acid → Boron Oxide → Magnesium reduction → electrical consolidation. Default: **50 Boron Dust → three ingots**. |
| Uraninite / Thorium ore | Bearing dust → existing NuclearCraft slurry → concentrate → refined compound → NuclearCraft Uranium/Thorium Dust. Existing isotope separation and fuel machinery take over here; this batch does not replace them. |

### Carbon, electronics, PGMs and the capstone

Phosphate Rock is crushed, conditioned with prolonged low heat and acid-extracted into Phosphoric Acid. Phosphate compounds first support fertilizer; later carbon reduction in the Arc Furnace makes elemental Phosphorus. Create's machine speed affects processing throughput.

Graphite Rock follows crushing → water agitation → chemical purification → high-temperature purification. It supplies clean carbon and electrode feed, **not Coal**. Existing Coke → Hop Graphite remains available for the Arc Furnace electrode bootstrap.

Sand becomes Fine Silica Dust, then undergoes superheated carbon reduction to existing TFMG Silicon. Chloride purification followed by Hydrogen treatment makes **High-Purity Silicon**. That grade feeds the existing prepared wafer and optional n/p semiconductor routes; the Industrial Iron construction recipes consume it directly.

Ultramafic Rock has two distinct PGM routes. Crude milling has a **20% recovery chance**, then selects **only one** Osmium/Platinum/Iridium result at **70/25/5** weighting. Proper wet chemistry uses a four-rock batch: aggressive leaching separates Osmium first, Platinum from the remaining liquor, then rare Iridium from a more demanding residue treatment. Rich Os/Pt/Ir ores stay single-metal feeds. Default consolidation is **20 powders per ingot**; crude Iridium trace fragments instead require **40 per ingot**.

Refined Radiance combines Titanium/Tungsten refractory lattices, all three PGMs, purified Graphite and high-grade Silicon. Industrial mixing, a Mekanism Pressurized Reaction Chamber and expensive final arc stabilization form one engineered capstone. **No new Allthemodium, Vibranium or Unobtainium processing chain is implemented in this batch.**

Radiance's PRC stage defaults to **1,600 extra Joules per tick for 12,500 ticks**: **8M extra FE**, plus **25,000 FE** base overhead, in an unupgraded chamber. That is 642 FE/t total and 625 seconds at 20 TPS, within the native buffer and ordinary power-transfer capacity. **Energy/Speed upgrades change the actual cost and time**; 8M is the baseline, not a guaranteed total with upgrades. Final Arc Furnace stabilization is a separate energy cost.

## Metal accounting and heat

The fixed scale is **1 ingot = 1,000 mB; 1 storage block = 9,000 mB**. Iron Nuggets are **25 mB**, Gold Nuggets **10 mB**. Raw Iron is **200 mB**, Raw Copper **125 mB**, Raw Gold **100 mB**; raw storage blocks hold nine raw units. Other configured nugget defaults are 100 mB. Do not assume vanilla nine-nuggets-to-one-ingot conversion remains valid: the policy retires conversions that create metal value.

Foundry fuels found in the installed sources top out at **800 / 1,000 / 1,500** for solid fuel, Lava and Blazing Blood. Powder consolidation therefore uses the Arc Furnace where necessary; it does not demand an unavailable hotter fuel. Finished Ti/W/Cr/Ir forms can remelt at 1,500 without reopening raw-ore shortcuts. See the [source audit and fuel correction](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/MATERIAL_PROCESSING_CHEMISTRY_AUDIT.md>).

Early melting uses the installed metal temperatures instead of a universal 1,000 default: Iron **800**, Copper **500**, direct/raw Zinc **420**, Tin **225**, and Gold/Gold Flakes **700**. Chemically recovered Zinc uses **550**, also within solid-fuel reach. These melting steps do not require obtaining an Iron lava bucket first. Their mB yields are unchanged.

Boron’s 50-powder batch is intentional: **50 × 60 mB = 3,000 mB**. Configuring its fractional value changes the exact integer batch. Os/Pt powders and Iridium fragments use the same exact-value calculation; settings requiring more than 64 inputs or outputs in one stack are rejected rather than rounded.

## What stays unchanged, and what is still inactive

TFMG oil extraction, finite reservoirs, native refinery products and existing power systems remain intact. The added heavy-oil side stream recovers Sulfur and leaves **desulfurized** oil for further distillation; its residue cannot repeatedly yield Sulfur. Early TFMG acid chemistry remains, while later Mek sulfur gases feed the same acid identity. Trace Sulfur from Galena/Cinnabar is not intended to replace refining.

The two added distillation recipes—desulfurized oil and Coal Tar—explicitly use the native **100-tick** default. Their timings can be tuned separately without changing native refinery recipes or product ratios.

Cold-river placer washing remains a TODO. Existing RU silt/peat is not proven unique to Cold River, and ordinary washing cannot identify where an ItemStack was mined. A global Gravel/Silt → Gold recipe would accept material from elsewhere, including crafted sediment. No such recipe or new sediment worldgen was added. The 1 mB flake value is ready for a later origin-qualified collection method.

## Editing the pack's values

Recipe tuning lives in [processing/material_processing_values.json](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/processing/material_processing_values.json>): yields, chances, selected times, electrical budgets and fractional batch values. It is a **build-time source file**, not a hot-loaded game config. Iron/Gold nugget values and the fixed ingot/block scale are not editable balance knobs.

Numeric source values must be finite and nonnegative; count, time and volume settings must be integers, not decimals or quoted strings. Recipe validation additionally checks stricter requirements such as positive ingredient amounts and bounded chances.

The PRC tuning field is `radiance.pressure_extra_joules_per_tick`, not a total-FE field. Tune it together with `radiance.pressure_ticks`; raising per-tick demand above the native buffer can stop processing even with a large external power network.

From the project root, run `python -B tools/material_processing/build.py` after changing source values. It regenerates the catalog, late-priority KubeJS script and content resources; `--check` only checks for stale outputs. Build the candidate JAR when bundled content/resources change, and stage the matching generated script, managed recipe export and candidate together. Validate the stage before a separately authorized deployment. Do not hand-edit generated catalog/script copies: regeneration overwrites them.

Manual Cinnabar is separate: the running pack uses `config/industrial_colonies/processing/manual_cinnabar.json`, initialized from its bundled default if absent. Change its heating time, hammer cooldown/damage or reach there, then **restart**. `manualNoBatch` must remain true. These settings do not rebuild the industrial recipes or change their yields.

Implementation references: [recipe builders](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/tools/material_processing/build.py>), [machine-tier patch](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/tools/upgrade_material_machine_tiers.py>), and [manual interaction code](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/src/main/java/dev/godpc/industrialcolonies/processing/ManualCinnabar.java>). New intermediates currently reuse functional placeholder item icons; this is not another approved texture overhaul.
