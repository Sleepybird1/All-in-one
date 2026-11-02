# Venus Expedition and Calorite Metallurgy Audit

## Outcome

Venus is the third canonical Ad Astra surface destination in the block-built
ship campaign. `rocketnautics:venus` is source-owned at priority 2000 and
links only to `ad_astra:venus`; its parent is `sol` and surface acceleration is
8.87. The 2,850,000-block body radius follows the installed Rocketnautics
half-scale convention. Ad Astra retains all world generation, atmosphere,
temperature, sky, time, and player-environment authority.

Sable receives one explicit priority-2000 `ad_astra:venus` physics record with
ship gravity `[0, -8.87, 0]`, zero pressure, and zero universal drag. This is
deliberate parity with the source-owned Moon/Mars bridge: Sable controls the
constructed craft, while Ad Astra controls the surface environment.

The loader contract is bytecode-pinned to the installed Cosmonautics
26.08.307 and Sable 2.0.3 JARs. No installed JAR supplies another Venus planet
or dimension-physics record.

## Physical descent authorization

`industrial_colonies:venus_navigation_computer` is a registered block, item,
block entity, Sable sublevel actor, model, loot-table self-drop, and language
entry. Its exact 5x5 recipe is:

```text
PSWSP
PEBEP
GNCNG
PLZLP
PIMIP
```

It physically joins Ostrum structure, Solar Panels, Water Pump, Gravity
Normalizer, Energizer, Nutritional Liquifier, TFMG/AE electronics,
ComputerCraft control, the Navigation Table, and the existing Mars Navigation
Computer. All five outpost utility recipes are explicit DAG parents.

The sole Cosmonautics `AllowedTransfer.allowToDimension()` decision is
modified without cancelling `DeepSpaceInstance.tick()`:

- Mars accepts either the Mars or Venus Navigation Computer.
- Venus requires a Venus Navigation Computer aboard every occupied loaded
  ship.
- Every associated player must wear a complete correctly slotted set from
  `#ad_astra:heat_resistant_armor`.
- Offline players, unloaded ships, an empty player/ship set, or an unassociated
  player fail closed.
- Moon and every unmanaged destination retain their installed behavior.

The four stock Netherite Space Suit recipes are replaced by automatable 5x5
Mechanical Crafting routes. Each retains its canonical Ad Astra output and
physically uses both Desh and Ostrum plus life-support hardware. The stock
recipe IDs are removed exactly; no armor tag or output namespace is broadly
removed.
The same heat-resistant tag also contains the Jet Suit family, but a complete
Jet Suit remains post-Calorite: its chest, pants, and boots require Calorite
machinery or blocks plus the corresponding Netherite Space Suit pieces. It
therefore cannot bootstrap first Venus landfall.

## Calorite factory

The physical line is assigned to `CR02 — Calorite Metallurgy`:

1. canonical Venus ore/raw feed tags crush to exactly one Calorite Grit;
2. Mekanism enrichment produces Calorite Concentrate;
3. four concentrates, 1000 mB TFMG Sulfuric Acid, and 1500 mB Water run in a
   heated size-7 firebrick mixing vat to produce two leached compounds;
4. a superheated size-7 firebrick vat with two electrodes reduces each
   compound to the canonical Ad Astra ingot;
5. only the Refined Radiance press stamps the canonical plate.

Twenty exact recipe IDs are retired: four stock suit recipes, three ore
multipliers, six smelting/blasting ingot shortcuts, and seven plate shortcuts.
The two Modern Industrialization compatibility recipes use absent legacy tags
today but are retired by exact ID for parity with the established Desh/Ostrum
future-proof policy. Nugget, ingot, finished-block, and raw-block packing are
preserved.

An exhaustive installed-JAR audit found no finished Calorite or Netherite
Space Suit chest/entity loot, no finished Calorite in structure NBT, and no
external contributors to the canonical Calorite tags. Raw ore drops remain
the intended Venus feedstock.

## Observation-only quests

Four quests extend Planetary Industry after `closed_loop_rations`:

1. `venus_expedition_package` observes the computer and all four suit pieces;
2. `venus_arrival` observes the no-reward changed-dimension advancement;
3. `calorite_freight` observes 64 Raw Calorite without consuming it;
4. `calorite_metallurgy` observes all five physical process outputs.

They grant no reward, destination, stage, research, or recipe. The generated
book contains 10 chapters, 109 quests, 237 tasks (224 item, eight structure,
five advancement), and 155 visual dependencies.

## Preserved boundaries

This slice does not enable Mercury, Glacio, prefab stations, cryogenic fuel,
Ad Astra rockets, Cosmowarp, freighter enforcement, bosses, Apotheosis, or
interstellar content. It does not edit the immutable Draw.io source or the
live pack.

## Focused verification

```powershell
python tools/build_managed_recipe_manifest.py --check
python tools/generate_managed_recipe_overhaul.py --check
python tools/generate_ftbquests_native.py --check
python tools/test_validate_venus_calorite_slice.py
python tools/validate_venus_calorite_slice.py --catalog "C:\path\to\recipe-catalog-current" --mods "C:\path\to\mods"
python tools/test_validate_planetary_freight_gates.py
python tools/test_validate_planetary_industry_slice.py
python tools/test_ftbquests_guidance_campaign.py
```

The focused mutation suite has 29 cases covering destination ownership,
runtime fail-closed behavior, correct-slot heat protection, physical recipe
ancestry, exact removals, Calorite packing, external loot/structure bypasses,
quest DAG integrity, and candidate-JAR resources.
