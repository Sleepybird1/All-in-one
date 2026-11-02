# Planetary Outpost Commissioning Audit

## Outcome

The first sustained Moon/Mars outpost slice is source-owned without opening a
new destination or adding a runtime gate. Five exact stock recipes become 5x5
Mechanical Crafting builds under `CR02 — Planetary Outpost Utilities`:

| Managed recipe | Result | Exact stock removal | Physical gate |
|---|---|---|---|
| `industrial_colonies:planetary/outpost/solar_panel` | `4x ad_astra:solar_panel` | `ad_astra:solar_panel` | Desh plate line |
| `industrial_colonies:planetary/outpost/water_pump` | `ad_astra:water_pump` | `ad_astra:water_pump` | Desh plate line |
| `industrial_colonies:planetary/outpost/gravity_normalizer` | `ad_astra:gravity_normalizer` | `ad_astra:gravity_normalizer` | Desh plate line |
| `industrial_colonies:planetary/outpost/energizer` | `ad_astra:energizer` | `ad_astra:energizer` | Ostrum plate line |
| `industrial_colonies:planetary/outpost/nutritional_liquifier` | `mekanism:nutritional_liquifier` | `mekanism:nutritional_liquifier` | Ostrum plate line |

The patterns depict their working systems rather than filling the grid with
raw material. Photovoltaic cells surround a supervised transformer/cable
spine; the Water Pump has a mirrored TFMG pump, pipe, valve, and tank train;
the Gravity Normalizer closes a Desh field lattice around buffered FE and
digital controls; the Energizer braces an ultimate-energy core in Ostrum; and
the Nutritional Liquifier combines Ostrum containment with pumps, valves,
Mekanism casing/control, AE engineering logic, and a Farmer's Delight Cooking
Pot as its recognizable food-processing core.

## Observation-only commissioning

The outpost branch adds three non-gating quests, which later feed the Venus
expedition branch:

- `lunar_utility_array` observes four Solar Panels, one Water Pump, and one
  Gravity Normalizer after Desh metallurgy.
- `martian_service_reserve` requires both Ostrum metallurgy and the lunar
  utility observation, then observes an Energizer, an Ultimate Energy Cube,
  and sixteen Ultimate Universal Cables.
- `closed_loop_rations` observes the Nutritional Liquifier and four Canteens;
  the installed `mekanism:full_canteen` advancement proves that nutritional
  paste actually filled a canteen.

All tasks consume nothing and grant no reward, recipe, stage, research, or
destination. The current Venus-extended native generation produces ten
chapters and 109 quests.

## Preserved boundaries

The direct water-to-oxygen loader recipe and Mekanism flint-to-oxygen recipe
remain deferred, so the Water Pump does not bypass the separator and rotary
oxygen line. This bounded slice did not itself enable a destination; the later
Venus continuation is independently audited, while cryo fuel, Ad Astra rocket
recipes, prefab stations, Mercury, Glacio, and Cosmowarp remain deferred. The immutable
MineColonies layout is unchanged, and no Java listener or Mixin was added.

## Validation

Run:

```powershell
python tools/test_validate_planetary_outpost_slice.py
python tools/validate_planetary_outpost_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/test_ftbquests_guidance_campaign.py
python tools/validate_ftbquests_native.py --item-catalog "C:\path\to\ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt" --recipe-catalog "C:\path\to\recipe-catalog-current" --instance "C:\path\to\instance"
python tools/build_managed_recipe_manifest.py --check --catalog "C:\path\to\recipe-catalog-current"
python tools/generate_managed_recipe_overhaul.py --check
python tools/generate_ftbquests_native.py --check
```

The focused validator pins the five exact recipes, 5x5 patterns, output counts,
one-owner removals, physical Desh/Ostrum ancestry, installed stock paths and
counts, node assignment, compiled KJSGen slots, three quest observations,
full-canteen advancement, and unchanged oxygen/travel boundaries.
