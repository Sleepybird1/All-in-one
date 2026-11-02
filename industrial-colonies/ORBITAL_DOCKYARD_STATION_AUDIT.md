# Orbital Dockyard and Station Fabrication Audit

## Outcome

The first post-construction dockyard slice is source-owned. Ten exact stock
recipes are replaced by three connected CR02 manufacturing nodes:

```text
CR02 — Orbital Construction
  -> CR02 — Orbital Navigation
       Velocity + Gimbal + Optical Sensors
       -> Navigation Table -> Sputnik telemetry probe
  -> CR02 — Dockyard Interfaces
       -> matched Docking Connector pairs
  -> CR02 — Station Fabrication
       -> Steel Plating -> Steel Panels
       -> Cable Ducts + Fluid Pipe Ducts
```

Every recipe is downstream of the 5x5 Physics Assembler route. The three
sensors and four construction-material batches run in the exact
`createcasing:refined_radiance_press`; the Navigation Table, Sputnik, and
Docking Connector pair are 5x5 Mechanical Crafting builds. TFMG frames,
plates, motors, pipes, tanks, pumps, cable hardware, and discrete electronics
remain the manufacturing foundation while AE2, Mekanism, and ComputerCraft
provide late digital supervision.

## Exact stock ownership

| Managed result | Exact stock recipe removed | Replacement output |
|---|---|---:|
| Velocity Sensor | `simulated:velocity_sensor` | 1 |
| Gimbal Sensor | `simulated:gimbal_sensor` | 1 |
| Optical Sensor | `simulated:optical_sensor` | 1 |
| Navigation Table | `simulated:navigation_table` | 1 |
| Sputnik Probe | `rocketnautics:sputnik` | 1 |
| Docking Connector | `simulated:mechanical_crafting/docking_connector` | 2 |
| Steel Plating | `ad_astra:steel_plating` | 32 |
| Steel Panel | `ad_astra:steel_panel` | 32 |
| Cable Duct | `ad_astra:cable_duct` | 16 |
| Fluid Pipe Duct | `ad_astra:fluid_pipe_duct` | 16 |

The Docking Connector recipe deliberately produces the stock pair. Its 5x5
layout includes Create Portable Storage and Portable Fluid Interfaces, a
Create Crafts & Additions Portable Energy Interface, and ComputerCraft wired
modems/cable. Those four ingredients mirror the block's actual item, fluid,
FE, and wired-network bridge functions instead of using decorative stand-ins.

The first Fluid Pipe Duct batch uses TFMG steel pipes, a steel tank, and
electric pumps. It does not require Desh, so an initial Earth-orbit dockyard is
not circularly gated behind off-world material.

## Boundary ownership

Sputnik's stock ID moved from `industrial_space_entry_deferred.js` into the
managed replacement's exact removal. The fail-closed boundary is therefore 35
IDs instead of 36, with one and only one owner for the stock probe recipe.
Prefab Ad Astra station recipes, the water-to-oxygen shortcut, the stock
Physics Assembler, and premature Cosmowarp routes remain unchanged in that
boundary. Existing AE2 quantum bridge retirements are also unchanged.

## Observation-only commissioning

Orbital Engineering adds three non-gating quests:

- Navigation and Telemetry Suite observes one of each sensor, one Navigation
  Table, and one Sputnik Probe.
- Four-Channel Docking Interface observes six Docking Connectors, or three
  matched pairs.
- Station Fabrication Batches observes 128 Steel Plating, 32 Steel Panels,
  16 Cable Ducts, and 16 Fluid Pipe Ducts.

The larger quantities give the bulk recipes a concrete commissioning purpose.
Tasks consume nothing, grant nothing, and emit no stage, research, recipe, or
destination authorization.

## Pressure-hull limitation

Steel Plating is a fabrication material, not a new pressure-hull authority.
The installed oxygen flood-fill accepts any full-collision enclosure, so a
true whitelist-backed station-hull rule requires a later custom-mod slice.
This batch intentionally does not claim or enforce that behavior.

## Source-level acceptance

```powershell
python tools/test_validate_orbital_dockyard_slice.py
python tools/validate_orbital_dockyard_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/test_orbital_engineering_quests.py
python tools/validate_orbital_engineering_quests.py
python tools/test_validate_space_entry_boundary.py
python tools/validate_space_entry_boundary.py --catalog "C:\path\to\recipe-catalog-current"
```

The focused checks pin all ten installed stock IDs and output counts, exact
removals, registry-backed ingredients, three node assignments, construction
ancestry, four physical docking channels, no-Desh first-duct routing, compiled
KJSGen slots, quantity-based non-gating quests, and the unchanged boundaries.
This source batch has not been deployed to the live instance.
