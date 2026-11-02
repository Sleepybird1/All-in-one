# Material-processing chemistry audit and implementation

Date: 2026-09-09. Scope: the authoritative material-processing brief in attachment `eaa584ec-be68-4b66-8d0b-0e2ec04b9266/pasted-text.txt`, not a world-generation or full power-system redesign.

## Outcome and verification boundary

Subsequent integration completed: native revision a3 verified **299/299 recipes** with 145,355 assertions; the full-client and Lithosphere A/B checks passed, and 0.5.0 was installed. See **MATERIAL_PROCESSING_ACCEPTANCE.md**. Historical correction notes below retain their original context; physical player operation and assembled powered factories remain outside the automated coverage.

`tools/material_processing/chemistry.py` defines **135 recipes**, **56 genuinely missing intermediate items**, and **22 process fluids**. The common metal registry independently contributes two molten-metal fluids; the chemistry-only test with that registry therefore reports 24 fluids total. Definitions are deterministic, native recipe JSON built by the common generator. The module does not write the live instance, edit worldgen, replace nuclear isotope/fuel recipes, or register a new machine.

Final combined-catalog checks passed **3,914 assertions across 18 groups** in **2.049 seconds** in `tools/material_processing/test_catalog.py`, covering **299 recipes, 74 new items and 25 fluids** across all modules, plus identical output from two fresh builder executions. Checks include actual installed item/texture resources, native fluid/chemical references, all 67 ingredient/cast tags, new-intermediate graph closure, TFMG ingredient capacities, exact fractional consolidation values, the native Foundry fuel ceiling, first-metal solid-fuel temperatures, numeric source-value validation, native PRC energy capacity and explicit distillation timing. That is resource/data-contract evidence, **not a substitute for actual registry/recipe-codec loading or physical machine testing**. Native inputs are treated as boundary inputs for the closure check; it does not prove the entire survival prerequisite graph. The parent integration task owns those checks and the complete bypass-retirement scan.

New intermediate models initially reuse the vanilla gunpowder texture. Their names and chemical roles are distinct, but these are functional placeholder icons, not approved custom artwork.

## Installed sources inspected

Live JAR directory: `C:/Users/GodPC/curseforge/minecraft/Instances/All in one/mods`.

| Source | Evidence used |
|---|---|
| `tfmg-1.2.0.jar` | Native vat, distillation, coking and industrial-blasting JSON; TFMG material/fluid registration; item models |
| `Mekanism-1.21.1-10.7.19.85.jar` | Gas/fluid rotary bridges, brine separator, sulfur oxidation/infusion, PRC examples, salt item/tag/loot/worldgen |
| `NuclearCraft-1.21.1-1.3.0-rc1.jar` | Existing materials/fluid registration, reagent models, chemical/leacher recipes, U/Th isotope separation |
| `ModernFoundry-1.21.1-4.1.6-NeoForge.jar` | Melting/ore-melting/casting/alloy JSON, existing molten-metal endpoints |
| `ImmersiveEngineering-1.21.1-12.4.2-194.jar` | Native arc-furnace recipe schema, sized ingredients/results, Nickel Dust |
| `createlowheated-neoforge-1.21.1-6.0.10-2.jar` | Native `mixing/builders_tea.json` verifies `heat_requirement: "lowheated"` |
| `regions-unexplored-0.6.2-neoforge-21.1.jar` | Cold River biome, silt biome tags, muddy-river surface rule and silt recipes |
| Cached NeoForge `21.1.248` sources | `SizedFluidIngredient.FLAT_CODEC`, `FluidIngredient` and `SingleFluidIngredient` confirm exact fluid+amount input syntax |

Project checks include `geology/GeologyBlocks.java`, `data/industrial_colonies/geology/deposit_families.json`, existing item models and Chemical Vat recipe-editor layout. Existing KubeJS was read from the live instance; it was **not modified by this module**.

Important existing scripts:

- `industrial_sulfur_canonicalization.js`: TFMG sulfur/acid canonicalization, Mek acid bridge, existing bulk coal/gunpowder sulfur recovery that conflicts with the new source hierarchy.
- `industrial_petroleum_canonicalization.js`: TFMG petroleum identity and competing Create Diesel Generators retirement; native TFMG refinery recipe chain remains available.
- `industrial_electronics_progression.js` and `kjsgen_recipes.js`: electronics are already managed by recipe-generator data. Prepared/etched Silicon Wafers already exist; do not duplicate them. Existing semiconductor sequences contain empty-fluid `base_filling` operations, reported separately to the integration owner.
- `industrial_nuclear_fuel_01.js`: existing fuel-pellet handoff is separate from this module's new U/Th feed preparation.
- `industrial_metallurgy_casting_compat.js`: existing 90/810 mB metal handling conflicts with this batch's global 1000/9000 mB rules; normalization belongs to the central metal policy, not this chemistry module.

## Canonical reuse

| Role | Exact reused IDs |
|---|---|
| Sulfur, acid, carbon reductant, slag | `tfmg:sulfur_dust`, `tfmg:sulfuric_acid`, `tfmg:coal_coke_dust`, `tfmg:slag` |
| Bauxite preparation | `tfmg:bauxite_powder` |
| Hydrogen and coking CO2 | `tfmg:hydrogen`, `tfmg:carbon_dioxide` |
| Reagent fluids | `mekanism:oxygen`, `mekanism:chlorine`, `mekanism:hydrogen_chloride`, `mekanism:sodium`, `mekanism:sulfur_trioxide`, `mekanism:brine` |
| Caustic, Borax Dust and boric acid | `nuclearcraft:sodium_hydroxide_dust`, `nuclearcraft:borax_dust`, `nuclearcraft:boric_acid` |
| Nickel product | `immersiveengineering:dust_nickel` — **not** nonexistent `nuclearcraft:nickel_dust` |
| Graphite tiers already present | `nuclearcraft:graphite_dust`, `nuclearcraft:graphite_ingot` |
| Zinc/Co/Mg/Li/Ag/Cr/Be/B powders | Existing `nuclearcraft:<metal>_dust` |
| Refractory Ti/W | `nuclearcraft:titanium_ingot`, `nuclearcraft:tungsten_dust`, `nuclearcraft:tungsten_ingot` |
| PGM products | `mekanism:dust_osmium`, `nuclearcraft:platinum_dust`, `nuclearcraft:iridium_dust`, `nuclearcraft:iridium_ingot` |
| Nuclear feed | `nuclearcraft:uranium_slurry`, `nuclearcraft:thorium_slurry`, `nuclearcraft:uranium_dust`, `nuclearcraft:thorium_dust` |

No exact installed TiCl4, Titanium Sponge, MgCl2, Alumina, Tungsten Oxide, Boron Oxide, Beryllium Oxide or Phosphoric Acid material was found in the audited registrations/resources. Those and necessary separated solutions/fractions are intentionally new. Existing NuclearCraft Silicon Gem/Boule/Wafers were reported to the silicon-chain owner; this module does not add competing wafers.

## Resource identities implemented

| Family | Recipes | Meaningful stages / endpoint |
|---|---:|---|
| Zinc | 6 | Crush → acid dissolution → zinc solution → precipitation → carbon reduction → melt; poor direct 12 mB versus proper 75 mB |
| Lead | 8 | Crush → low-heat roast → carbon reduction → crude lead; optional electrode purification; direct 15 versus proper 75 mB; sulfur chance 1.5% |
| Nickel / Cobalt | 10 / 6 | Linked leach/clarification/separation; consumed mother liquor has one 8% Cobalt roll. Rich Nickel uses an entirely separate nickel-only solution; Cobalt-rich crushing has 25% chance of one smaller Nickel fraction |
| Aluminum | 7 | TFMG Bauxite Powder → caustic slurry → red-mud separation → Alumina → mandatory powered electrodes → granules → melt |
| Magnesium | 6 | Calcine Dolomite → acid separation → purified MgCl2 → mandatory electrodes → Mg; Ti returns this same chloride |
| Titanium | 7 | Ilmenite purification → chlorination → crude/pure TiCl4 → Magnesium reduction → Titanium Sponge → powered arc consolidation |
| Tungsten | 7 | Alkaline leach → tungstate → precipitate → oxide → Hydrogen reduction → powder → high-energy arc sintering |
| Chromium | 7 | Alkaline roast → **Industrial Iron-only fan washing** → purification → reduction → arc consolidation |
| Lithium | 7 | Thermal activation → leach → precipitation → mandatory electrochemical reduction → melt |
| Silver | 7 | Low-heat roast → acid leach → precipitation → melt; direct 12 versus proper 60 mB |
| Phosphate | 6 | Prolonged low heat → acid extraction → Phosphoric Acid/compound; useful fertilizer first, later high-energy carbon reduction to elemental Phosphorus |
| Graphite | 4 | Crush → mechanical agitation → chemical purification → high-temperature purified Carbon; no Coal output |
| Beryllium | 6 | Leach → precipitate → oxide → large firebrick/electrode reduction → low-volume metal |
| Boron | 6 | Existing NC Borax Dust → purified borate → existing Boric Acid → oxide → advanced Mg reduction; returns MgCl2; final electrical consolidation |
| Uranium / Thorium | 5 each | Bearing dust → existing NC slurry → concentrate → refined compound → NC dust feed for existing isotope/fuel systems |
| PGMs | 17 | Aggressive four-rock leach → Osmium first → Platinum from mother liquor → Iridium refractory residue with harsher purification; rich ores remain single-metal feeds |
| Reagents | 5 | H2 rotary bridge, salt dissolution, powered bootstrap brine electrolysis, later caustic synthesis, final acid hydration |
| Sulfur extension | 3 | Finite heavy-oil desulfurization → captured sulfide → bulk sulfur; native-ratio distillation of desulfurized residue |

The crude one-result 70/25/5 Osmium/Platinum/Iridium route is owned by the physical-processing module. Proper chemistry yields expected fractions 7 / 2.5 / 0.5 per four-rock batch across **separate** stages, not three ready metals from one vat. Twenty Iridium powder fractions consolidate to one ingot; Iridium receives both the harshest purification and largest energy budget of these metal endpoints.

## Bootstrap and loop safeguards

1. **Aluminum/electronics cycle avoided:** an existing Salt item dissolves with 15 mB Water into 15 mB existing Mek Brine. Two powered TFMG electrodes process 30 mB Brine + Water into one existing NC Sodium Hydroxide, with small Chlorine/Hydrogen outputs. No Mekanism circuit-dependent machine is needed for the first caustic. The companion machine patch must expose powered electrodes/vats at the Copper-era bootstrap. Aluminum still requires purification and electrical reduction; no raw-Bauxite smelting exception was introduced.
2. **Salt duplication avoided:** native `mekanism:oxidizing/brine` produces 15 mB per Salt; native rotary/crystallizing returns one Salt per 15 mB. New dissolution uses that exact ratio, not a convenient bucket-sized multiplier. Existing Salt blocks drop four Salt and use a native underwater dirt/clay disk feature; no new salt worldgen or mineral was added.
3. **Later caustic efficiency:** Mek brine separation consumes 10 mB per Sodium unit; one Sodium then makes one hydroxide. The early electrode route consumes 30 mB per hydroxide and therefore does not supersede mature reagent infrastructure.
4. **Hydrogen identity:** the rotary bridge outputs existing `tfmg:hydrogen` and takes that exact fluid on its return side. This avoids relying on the old common tag, which initially contained only Mek Hydrogen. Native gas machinery still owns Mek Hydrogen chemical production.
5. **Magnesium recovery:** Titanium consumes two Magnesium Dust and returns 500 mB MgCl2. Each 250 mB electrode batch returns one Magnesium Dust. This is recovery with electrical cost, not Magnesium multiplication. Boron consumes one Magnesium and returns one 250 mB batch.
6. **No refinery sulfur loop:** the 1000 mB native Heavy Oil side stream becomes 900 mB *desulfurized* Heavy Oil plus captured sulfide. The residue distills at native Heavy Oil ratios: 200 → 100 residual / 25 lubrication / 50 diesel / 20 kerosene / 5 naphtha. The residual remains desulfurized and cannot re-enter sulfur extraction. Native crude/heavy-oil recipe IDs are never overwritten.
7. **Pre-Mek acid retained:** the existing TFMG sulfur + nitrate + water vat recipe remains available. Later Mek SO2/SO3 production feeds vat hydration into the same TFMG acid; conflicting alternate sulfur/acid shortcuts are submitted to central retirement.
8. **Nuclear ownership retained:** no isotope separator, fuel fabrication, enrichment or breeder recipe is removed here. Existing NC isotope recipes consume U/Th dust and therefore provide a concrete handoff; chemistry does not end at an ore-to-ingot shortcut.

## Codec decisions verified against installed sources

- Create/TFMG fluid ingredients: `{"type":"neoforge:single","fluid":"mod:fluid","amount":250}`. Fluid **results**: `{"id":"mod:fluid","amount":250}`. Item results use `id`, `count`, and optional `chance`.
- TFMG vats: `type: tfmg:vat_machine_recipe`, `allowed_vat_types`, `machines`, `min_size`, `processing_time`, optional `heat_requirement`. Native Aluminum confirms repeated `tfmg:electrode` entries. This module uses the actual machine-capability fields, not a descriptive label.
- Create Low Heated uses exactly `lowheated`. Heated/superheated remain normal Create heat levels.
- IE arc: `input`, `additives`, `results`, `energy`, `time`. A count greater than one uses `{"basePredicate":{"item":"mod:item"},"count":8}`. Putting `count` beside `item` is not the installed IE sized-ingredient schema.
- Mek rotary uses chemical-input `chemical`, chemical-output `id`, fluid-input exact `fluid` or `tag` with `amount`, and fluid-output `id` with `amount`.
- Modern Foundry new chemistry endpoints use ordinary `modernfoundry:melting`, not multiplier-sensitive `ore_melting`; canonical molten fluids and global 1000/9000 normalization are supplied by the shared metal builder.

### Native distillation timing parity correction

The isolated native `material-processing-report-a2.json` under `isolated-runtime/geology-gametest-20260909-064550-754/` verified 297 of 299 recipes and reported exactly two canonical-encoding differences: Sulfur's desulfurized-oil distillation and Coal Tar fractionation gained `processing_time: 100` during native/KubeJS loading, while their source definitions omitted that field. This was an encoding/default mismatch, not an input, yield or refinery-product change.

Both definitions now include the same explicit configurable **100-tick** default. Their source settings are `chemistry.timing.desulfurized_oil_distillation` and `timing.coal_tar_fractionation`. Group 18 checks both defaults, their serialized configuration entries and independently overridden values (137/173) using in-memory builders. The generator and `build.py --check` passed after the correction. Native parity must still be confirmed in the next isolated run; the historical stage/report was not edited.

## Bypass integration contracts

The module submits 15 exact removal IDs and 21 claimed intermediate outputs to the shared late recipe policy. Claims target ore/chemical acquisition, **not every final ingot recipe**, so useful storage conversion and refined-material recycling remain the integration policy's responsibility. Critical conflicts include native direct TFMG Bauxite electrolysis, NC direct ore-to-U/Th slurry, direct Tungsten/Chromium powder acquisition, untreated Borax Dust, easy bulk coal/gunpowder sulfur, and duplicated acid synthesis. Root must evaluate native/other-mod alternatives against the complete input/output graph; this document does not claim that 15 exact IDs alone close all paths.

Important prerequisite contracts: IE Arc Furnace and suitable electrodes must be obtainable before Industrial Iron because Titanium/Tungsten consolidate there. Chromium's custom fan serializer must reject base and Weathered Iron fans. The chemical module's explicit serializer ID is `industrial_colonies:industrial_iron_splashing`; enforcement is owned by the existing tiered-processing implementation and its runtime checks.

## Foundry fuel reachability correction

The complete installed recipe inventory contains only three Modern Foundry fuel temperatures: solid fuel **800**, Lava **1000**, and Blazing Blood **1500**. No hotter fuel recipe or live-script override was found. Bytecode inspection confirmed `FuelModule` stores the selected fuel recipe's temperature directly and the Foundry passes that temperature to `heatItems`; neither the larger structure nor its fuel rate supplies a higher temperature. Native Blaze entity melting produces Blazing Blood, and the Blaze Head melting route requires only 1000, so the documented hotter fuel source does not itself require Titanium, Tungsten, or Allthemodium.

The audit caught 11 new melting definitions above the actual ceiling. All were corrected without adding a fuel or changing native refinery/power mechanics:

| Corrected endpoint | Exact replacement / value preservation |
|---|---|
| Osmium powder | IE Arc Furnace: 20 × 50 mB fractions → one 1000 mB ingot; 204,800 energy / 600 ticks |
| Platinum powder | IE Arc Furnace: 20 × 50 mB fractions → one 1000 mB ingot; 409,600 energy / 800 ticks |
| Iridium trace fragments | IE Arc Furnace: 40 × 25 mB fragments → one 1000 mB ingot; 819,200 energy / 1200 ticks |
| Chemically reduced Boron powder | IE Arc Furnace: 50 × 60 mB fractions → three 1000 mB ingots; 409,600 energy / 800 ticks |
| Seven already-finished Ti/W/Cr/Ir remelting forms | Reachable 1500 temperature; ingot/block/nugget values unchanged. These inputs have already passed their required reduction/consolidation, so this is not a raw-ore shortcut |

Titanium Sponge, Tungsten powder and proper Iridium powder already used native electrical consolidation and remain unchanged. Configurable Os/Pt/Boron and trace-Ir mB values use the greatest common divisor with 1000 to derive an exact integer input/output batch. Values requiring more than a normal 64-item input or output stack are rejected with an explicit error, never silently rounded. Native IE `basePredicate`/`count` sized ingredients and outputs are retained.

Regression group 14 rejects any owned Foundry melt above the highest installed fuel, checks all four fractional arc conversions, verifies removal of the old unreachable powder melts, and checks the native Blazing Blood source. Survival access to the Nether, fuel capture and machinery remains a runtime/gameplay concern rather than a resource-audit claim.

### First-metal solid-fuel correction

The common melting helper now chooses installed per-metal temperatures when no explicit process override is supplied, rather than applying 1000 universally. This removes an avoidable melting-stage dependency on a Lava bucket before recovering the first Iron. Hematite/Magnetite and reduced/raw Iron use 800, Copper uses 500, direct/raw Zinc 420, Tin 225, and Gold/Gold Flakes 700. Chemically recovered Zinc retains its explicit 550 processing requirement, still within solid-fuel reach. Explicit reduction/consolidation requirements remain separate; all mB values are preserved.

Regression group 15 checks exact early-route temperatures and unchanged amounts against the installed 800 solid-fuel tier, including raw storage blocks and finished forms. It also verifies that explicit thermal overrides and the unknown-metal fallback still work. Group 16 tests the common configuration boundary: NaN, infinities, negatives, booleans, strings and other nonnumeric values are rejected; integer defaults reject floating-point settings, while valid zero/positive numeric values and nested default insertion are retained. Recipe-specific positivity and probability ceilings remain separate catalog checks.

The first expanded run caught a surviving explicit 700 override on direct Sphalerite instead of the requested native 420; the source owner corrected it and the full 16-group rerun passed with zero failures/errors. The pure checks compile the batch in memory only: this follow-up did not regenerate the pinned catalog or write to the running integration stage.

Other corrected audit findings: the electrode feed now consumes existing `nuclearcraft:graphite_ingot`, rather than an unregistered IC Purified Graphite; Borax Dust now reuses the existing NC item; and two Radiance placeholder textures reference the actual Create `chromatic_compound_0.png` resource instead of a nonexistent unsuffixed PNG.

The previously serialized, unused `metals.iron.nugget: 100` and `metals.gold.nugget: 100` settings are normalized to **25** and **10**. Those two values are fixed by the brief, not editable balance knobs; generated config now agrees with the actual recipes. Other metal nugget values remain configurable. Regression checks load the old misleading 100 values and verify normalization without changing the already-correct actual Iron/Gold yields.

## Radiance PRC energy units and native capacity

Installed Mekanism `10.7.19.85` uses **extra Joules per tick** for reaction JSON `energy_required`, not total energy per item or FE. `PRCEnergyContainer.getBaseEnergyPerTick()` adds the recipe charge to the machine baseline; `CachedRecipe.useEnergy()` spends that sum on every processing tick. `TileEntityPressurizedReactionChamber.onCachedRecipeChanged()` updates consumption, not buffer capacity. `MachineEnergyContainer` and `MekanismUtils` apply the normal energy/speed upgrade scaling.

Actual configuration provenance is the live instance's read-only `C:/Users/GodPC/curseforge/minecraft/Instances/All in one/config/Mekanism/`:

| File and key | Audited value |
|---|---:|
| `machine-storage.toml`: `pressurizedReactionBase` | 2,000 J buffer |
| `machine-usage.toml`: `pressurizedReactionBase` | 5 J/t baseline |
| `general.toml`: `energy_conversion.feConversionRate` | 2.5 J per FE |
| `general.toml`: `maxUpgradeMultiplier` | 10 |
| `tiers.toml`: `energy_cubes.basicOutput` | 4,000 J/t |

The initial 8,000,000 setting would charge 8,000,000 J every tick: at 6,000 ticks, that is 19.2 billion extra FE per operation if it could run. It cannot fit the native buffer. Even maximum Energy upgrades with no Speed upgrades reduce that draw only to 800,001 J/t including the baseline, while capacity reaches only 20,000 J. An unlimited external supply does not remove this internal capacity obstruction.

The corrected defaults are **1,600 extra J/t for 12,500 ticks**. An unupgraded machine uses **1,605 J/t = 642 FE/t**, below its 2,000 J buffer and an ordinary Basic Energy Cube's configured output. The extra charge is exactly **8,000,000 FE**; baseline consumption adds **25,000 FE**, for **8,025,000 FE total**. The configured time is 625 seconds at 20 TPS before upgrades or interruptions. Actual generation still must supply that sustained demand; this audit does not create energy or assert an entire tested power build.

The renamed source setting is `radiance.pressure_extra_joules_per_tick: 1600`, alongside `radiance.pressure_ticks: 12500`; the ambiguous old `pressure_energy` field is gone. **Normal Mekanism Energy and Speed upgrades change actual cost and duration. The 8M extra FE figure is an unupgraded baseline, not an invariant enforced against upgrades.** The separate final IE Arc Furnace stabilization keeps its native total-energy budget.

Regression group 17 reads those four actual TOML files and checks exact recipe/config values, unupgraded tick demand versus buffer and ordinary output capacity, FE conversion, base overhead, rejection of the obsolete config name, and the old setting as a failing capacity control. It is configuration/data evidence backed by the installed bytecode audit, not a claim of a completed live PRC operation. No native Mekanism capacity, transfer, upgrade or power setting was modified.

## Placer Gold TODO — deliberately inactive

The audit found real `regions_unexplored:cold_river` (temperature 0.4), plus existing `silt_dirt`, `silt_mud`, `peat_dirt` and `peat_mud`. It did **not** establish a unique cold-river-only sediment block. The RU silt surface-biome tag does not include Cold River; the muddy-river rule selects peat mud or ordinary mud. Silt coarse dirt is also craftable from Silt Dirt and ordinary Gravel.

Create fan washing sees an ItemStack, not the biome where it was mined. A global Gravel/Silt washing → Gold recipe would therefore provide gold outside the intended cold rivers and could accept crafted material. No such recipe, invented sediment block, or worldgen change is added here. TODO: choose an existing sediment together with a verifiable origin-qualified collection mechanism before enabling placer washing. The physical module may register the specified 1 mB Gold Flake value while this acquisition recipe stays inactive.

## Verification scope

- Full generated resource/recipe-codec loading and direct native TFMG vat/IE arc/Industrial Iron fan checks passed in integration revision a3. These are not a full powered-world machine build.
- Gameplay throughput, FE consumption under installed server configs, and final recipe-review artwork remain separate from pure data validity.
- Existing downstream NC isotope/fuel machinery is preserved; this batch does not claim a tested complete nuclear fuel cycle.
- First-pass configurable yields are intentional balance defaults, not a real-world mass/chemistry simulation.
- No Allthemodium, Vibranium, Unobtainium, new planet/worldgen, universal Gravel-to-Gold, or new refinery structure is introduced.
