# Orbital Pressure and Life-Support Audit

## Outcome

The first orbital life-support manufacturing slice is source-owned and ready
for deployment review. It adds nine exact-stock replacements as 5x5 Create
Mechanical Crafting assemblies, arranged as two branches after
`industrial_colonies:space/propulsion/thruster_mount`:

```text
thruster_mount
├─ fan ───────────────────────────────┐
└─ gas_tank ─┬─ large_gas_tank ──────┤
             ├─ oxygen_gear ──────────┤
             └─ fan + gas_tank -> oxygen_loader
                                      │
                                      v
                              oxygen_distributor
                              ├─ oxygen_sensor ─┐
                              └─ vent ──────────┴─ airlock
```

This is deliberately a branch-and-join factory chain rather than nine linear
unlock steps. The fan and pressure-vessel lines can be built in parallel; the
distributor proves that both are operating; the final airlock joins monitoring
and bulk ventilation.

## Installed evidence

The installed catalog identifies one stock shaped recipe for each managed
output in `adastra-1.21.1-1.16.22-neoforge.jar`:

| Managed output | Exact removed stock ID | Installed source path |
|---|---|---|
| `ad_astra:fan` | `ad_astra:fan` | `data/ad_astra/recipe/fan.json` |
| `ad_astra:gas_tank` | `ad_astra:gas_tank` | `data/ad_astra/recipe/gas_tank.json` |
| `ad_astra:large_gas_tank` | `ad_astra:large_gas_tank` | `data/ad_astra/recipe/large_gas_tank.json` |
| `ad_astra:oxygen_gear` | `ad_astra:oxygen_gear` | `data/ad_astra/recipe/oxygen_gear.json` |
| `ad_astra:oxygen_loader` | `ad_astra:oxygen_loader` | `data/ad_astra/recipe/oxygen_loader.json` |
| `ad_astra:oxygen_distributor` | `ad_astra:oxygen_distributor` | `data/ad_astra/recipe/oxygen_distributor.json` |
| `ad_astra:oxygen_sensor` | `ad_astra:oxygen_sensor` | `data/ad_astra/recipe/oxygen_sensor.json` |
| `ad_astra:vent` | `ad_astra:vent` | `data/ad_astra/recipe/vent.json` |
| `ad_astra:airlock` | `ad_astra:airlock` | `data/ad_astra/recipe/airlock.json` |

The catalog rows are currently `recipes.csv:10`, `:127`, `:130`, `:174`,
`:240-242`, `:245`, and `:514`. Each output has exactly one installed stock
producer, so removing the listed ID closes its stock path without an output,
type, or namespace wipe.

Two stock recipes were materially out of order for a first orbital habitat:
the oxygen distributor requires the Moon material Desh and the oxygen sensor
requires the Mars material Ostrum. The managed recipes replace those circular
dependencies with late Earth manufacturing: TFMG pressure hardware and
electronics, Mekanism control/storage, AE processors, and ComputerCraft
supervision.

## Node ownership

`CR02 — Pressure Hardware` owns circulation and breathing hardware:

- `ad_astra:fan`
- `ad_astra:gas_tank`
- `ad_astra:large_gas_tank`
- `ad_astra:oxygen_gear`

`CR02 — Habitat Life Support` owns active habitat equipment:

- `ad_astra:oxygen_loader`
- `ad_astra:oxygen_distributor`
- `ad_astra:oxygen_sensor`
- `ad_astra:vent`
- `ad_astra:airlock`

These are managed-only recipe families. The immutable MineColonies Draw.io
layout is unchanged.

## Canonical oxygen contract

The installed pack already contains a coherent cross-mod oxygen line:

1. `mekanism:separator/water`, from
   `data/mekanism/recipe/separator/water.json`, separates water into
   `mekanism:hydrogen` and `mekanism:oxygen`.
2. `mekanism:rotary/oxygen`, from
   `data/mekanism/recipe/rotary/oxygen.json`, provides the gas/fluid conversion
   for `mekanism:oxygen` and advertises `c:oxygen`.
3. Mekanism's `data/c/tags/fluid/oxygen.json` contributes its oxygen fluids to
   `#c:oxygen`; Ad Astra's `data/ad_astra/tags/fluid/oxygen.json` includes that
   common tag.
4. `ad_astra:oxygen_loading/oxygen_from_oxygen_loading_oxygen`, from
   `data/ad_astra/recipe/oxygen_loading/oxygen_from_oxygen_loading_oxygen.json`,
   remains enabled as the safe oxygen-to-oxygen loader pass-through.

The direct-water recipe
`ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water` remains removed by
exact ID. `mekanism:chemical_conversion/flint_to_oxygen` also remains deferred.
Together those decisions require the industrial separator and rotary line
without disabling Ad Astra's functional oxygen equipment.

TFMG air is intentionally not added to any breathable-oxygen tag. Inspection
of the installed Air Intake implementation found unconditional local air
production rather than a dimension-aware atmosphere check; tagging it as
breathable would create a free orbital oxygen bypass.

## Power, hulls, and consumables deliberately deferred

This slice includes local redundancy inside the distributor through
`mekanism:ultimate_energy_cube`, but it does not claim to finish station power.
The next station-construction batch can use these exact installed candidates:

- first Earth-built hull stock: `ad_astra:iron_plating`,
  `ad_astra:steel_plating`, `ad_astra:steel_panel`, and
  `ad_astra:reinforced_door`;
- concealed service runs: `ad_astra:cable_duct` and
  `ad_astra:fluid_pipe_duct`;
- shipped primary/backup power: Mekanism energy cubes and universal cables;
- post-Moon expansion: `ad_astra:solar_panel`, whose stock recipe at
  `data/ad_astra/recipe/solar_panel.json` requires Desh and is therefore a
  sensible lunar-return upgrade rather than first-station equipment; and
- closed-loop food supply: `mekanism:nutritional_liquifier` and
  `mekanism:nutritional_paste`, later tied to the pack's agricultural output
  and maintenance quests.

The six prefabricated Ad Astra station recipes and the stock nested
`simulated:physics_assembler` recipe remain deferred. The separate source-owned
orbital-construction slice now provides the legitimate 5x5 Physics Assembler
replacement downstream of the completed Airlock and Thruster Mount. Hull batches, dock construction,
primary/backup power qualification, nutritional paste throughput, and actual
failure/maintenance mechanics require their own bounded stages; this batch
does not invent runtime simulation for them.

## Source-level acceptance

Run:

```powershell
python tools/test_validate_orbital_life_support_slice.py
python tools/validate_orbital_life_support_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/test_validate_space_entry_boundary.py
python tools/validate_space_entry_boundary.py --catalog "C:\path\to\recipe-catalog-current"
python tools/build_managed_recipe_manifest.py --check --catalog "C:\path\to\recipe-catalog-current"
python tools/generate_managed_recipe_overhaul.py --check
```

The validator pins all nine recipes, their 5x5 grids, branch/join dependencies,
TFMG-first ingredients, exact stock removals and source paths, node assignments,
compiled KJSGen cards, and the oxygen pass-through exception. This work has not
been deployed to the live instance; client/world acceptance remains required
after the source batch is intentionally deployed.
