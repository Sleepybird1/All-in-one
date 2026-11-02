# Planetary Industry: Desh, Ostrum, and Mars Navigation

## Result

The first planetary manufacturing slice is source-owned and deterministic.
Moon Desh and Mars Ostrum are no longer furnace metals or generic press
materials: each must pass through Create crushing, Mekanism enrichment, two
TFMG Chemical Vat operations, and a Refined Radiance press. The physical Mars
Navigation Computer sits between the completed Desh line and the Ostrum line.

This work does not modify the historical Draw.io tree or the live CurseForge
instance.

## Physical process routes

Both feed recipes use project-owned item tags so the managed-recipe architecture
retains one editable KJSGen authority per output while accepting every installed
ore/raw source. Each ore or raw item yields exactly one grit; silk-touching an
ore therefore cannot duplicate final ingots.

```text
Desh ore/raw (Ad Astra or Rocketnautics Addon)
  -> Create crushing: 1 Desh Grit
  -> Mekanism enriching: 1 Desh Concentrate
  -> steel TFMG vat, mixing: 2 concentrate + 250 mB sulfuric acid
     + 750 mB water -> 2 leached compound (size 3, 200 ticks)
  -> heated steel TFMG vat, two electrodes: compound -> Desh ingot
     (size 3, 300 ticks)
  -> Refined Radiance press: ingot -> plate

Ostrum ore/raw
  -> Create crushing: 1 Ostrum Grit
  -> Mekanism enriching: 1 Ostrum Concentrate
  -> firebrick TFMG vat, mixing: 2 concentrate + 500 mB sulfuric acid
     + 1000 mB water -> 2 leached compound (size 5, 400 ticks)
  -> heated firebrick TFMG vat, two electrodes: compound -> Ostrum ingot
     (size 5, 600 ticks)
  -> Refined Radiance press: ingot -> plate
```

Ostrum therefore requires a larger vat, twice the Desh acid, more water, and
longer leaching/reduction cycles.

## Mars Navigation Computer

The 5x5 Mechanical Crafting recipe consumes substantial Desh plate/ingot
structure, TFMG etched and normal circuit boards, AE2 Engineering Processors,
an advanced ComputerCraft computer and monitor, the installed Navigation
Table, and the existing Orbital Flight Computer. It is assigned to `CR02 — Mars
Navigation`, between Lunar Metallurgy and Martian Metallurgy. The block and
runtime descent authority are implemented elsewhere in the same source mod;
this slice registers its block item, language entry, managed recipe, node, and
observational quest.

## Shortcut retirement and retained packing

The 11 managed recipes own exactly 36 audited removals:

- four Ad Astra/Create ore-crushing shortcuts;
- two Modern Industrialization macerator shortcuts;
- twelve Ad Astra smelting/blasting recipes;
- four Rocketnautics Addon Mars-Desh smelting/blasting recipes;
- fourteen Ad Astra/Create/Immersive Engineering/Modern Industrialization/
  Thermal direct-plate recipes.

The normal Desh/Ostrum ingot, nugget, block, raw material, and raw block packing
recipes remain intact. Rocketnautics Addon's ingot/nugget packing also remains.
Vat ingot recipes intentionally do not claim exclusive output; only the two
plate recipes are exclusive.

## Structure and loot bypass closure

The installed Ad Astra JAR
`adastra-1.21.1-1.16.22-neoforge.jar` is pinned at SHA-256
`FAF21D02C71D2D5B5A671A746334ED18A9DDBA79A5A9D9BD95E93A1D9EE9EC86`.
An exhaustive compressed-structure scan found only two finished-metal palette
entries:

- `village/moon/lunar_tower.nbt`: `ad_astra:desh_block` becomes
  `ad_astra:moon_stone`;
- `temple/mars/mars_temple.nbt`: `ad_astra:ostrum_block` becomes
  `ad_astra:conglomerate`.

Both replacements are exactly the same byte length as the original palette
string. `tools/build_planetary_structure_overrides.py` pins the source JAR,
compressed entry hashes, decompressed entry hashes, occurrence counts, and
deterministic output hashes before writing the two source resources. It changes
no geometry, palette index, entity, or loot marker.

The two Moon village chest overrides contain only modest Raw Desh (maximum
three) plus vanilla loot. They cannot grant grit, concentrate, leached
compound, launch pads, fuel, tanks, spacesuits, or other manufactured hardware.

## Observation-only guidance

`Planetary Industry` is chapter 10, after Orbital Engineering's Station
Materials objective. Its seven quests observe:

1. real Moon landfall through a no-reward changed-dimension advancement;
2. 64 Raw Desh;
3. all five Desh process outputs;
4. the Mars Navigation Computer;
5. real Mars landfall through a no-reward changed-dimension advancement;
6. 64 Raw Ostrum;
7. all five Ostrum process outputs.

The chapter adds 13 item tasks, two advancement tasks, and seven visual
dependencies. It has no rewards, stages, consumption, commands, research, or
recipe-unlock fields. After the later outpost and Venus extensions, the full
generated book contains 10 chapters, 109 quests, 237 tasks (224 item, eight
structure, five advancement), and 155 dependencies.

## Exact source delta

- six registered metallurgy intermediate items, six external-texture models,
  and six item language entries;
- one Mars Navigation Computer block-item registration and language entry;
- two ore/raw feed tags;
- 11 managed recipes and 36 exact removals;
- three logical machine-node assignments;
- one seven-quest chapter, two no-reward advancements, and generated native
  quest/localization/manifest output;
- two raw-only Moon loot-table overrides;
- two deterministic Ad Astra structure overrides;
- one focused validator and 25 mutation tests;
- runtime-log quest topology initially moved from 9/95 to 10/102; the current
  Venus-extended topology is 10/109.

## Focused verification

```powershell
python tools/build_planetary_structure_overrides.py --check
python tools/build_managed_recipe_manifest.py --check
python tools/generate_managed_recipe_overhaul.py --check
python tools/generate_ftbquests_native.py --check
python tools/validate_planetary_industry_slice.py
python tools/test_validate_planetary_industry_slice.py
python tools/test_validate_live_runtime_log.py
```

The focused validator fails closed on recipe topology, exact one-grit counts,
vat mode/heat/size/time/fluid charges, the Refined Radiance machine lock, the
5x5 navigation assembly, exact removals, packing preservation, item assets,
node assignments, raw-only loot, structure hashes/palette strings, arrival
advancements, generated quests, installed registry IDs, and compiled KJSGen
cards.
