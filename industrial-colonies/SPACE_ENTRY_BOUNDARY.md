# Space Entry Boundary

Spaceflight begins after the Industrial Star. It is an expansion of the
factory campaign, not a parallel early-game shortcut and not the final reward.
The first implemented slice establishes an auditable boundary between the
completed Earth progression and future orbital industry.

## Authorization contract

A Sable/Cosmonautics block-built craft may cross the installed space-transition
boundary only while it contains a live
`industrial_colonies:orbital_flight_computer` block entity. The transition
hook combines the destination dimension's normal `allowToSpace()` result with
that onboard-computer check. Missing computers fail closed.

The Orbital Flight Computer is a 5x5 KJSGen-managed recipe downstream of the
Industrial Star. Its construction consumes late AE2, ComputerCraft, TFMG,
Mekanism, and Allthemodium-alloy components, so placing the block aboard a ship
is physical proof that the Earth factory campaign was completed. FTB Quests
documents the step but does not authorize it.

## Propellant and propulsion contract

The launch fluids have one canonical owner:

- rocket fuel is TFMG kerosene, including its flowing fluid;
- oxidizer is liquid Mekanism oxygen, including its flowing fluid; and
- the intended oxygen line begins with water electrolysis and uses Mekanism
  rotary condensation. The one-flint oxygen conversion is disabled.

Ad Astra's oxygen-to-oxygen loading pass-through remains available so the
canonical Mekanism oxygen line can feed Ad Astra habitat equipment through the
installed fluid tags. Its direct water-to-oxygen loading recipe remains
deferred because that route bypasses both separation and rotary condensation.

Four formerly recipe-less Cosmonautics parts now form the first modular
propulsion manufacturing chain:

1. hose anchors establish propellant interfaces;
2. engine pipes establish dual-fluid distribution;
3. engine nozzles consume the prior fluid-handling subassemblies; and
4. the thruster mount combines the completed nozzle train with late digital,
   electrical, and structural components.

These recipes are assigned to the **Orbital Engineering** family and depend on
the Orbital Flight Computer. They deliberately use exact source-owned recipes;
there are no invented stock-removal IDs for outputs that shipped recipe-less.

## Orbital construction contract

The completed propulsion and habitat branches now converge through three
Refined Radiance Deployer certification passes. The Orbital Flight Computer,
Thruster Mount, and Airlock are reusable held fixtures, so the only copies
needed aboard the ship are never consumed. The passes turn an AE blank pattern
into a guidance-certified plan, then a propulsion-certified plan, and finally
the sole authored `simulated:contraption_diagram` route.

That diagram is consumed by a 5x5 Mechanical Crafting recipe for the
ground-side `simulated:physics_assembler`. The assembler belongs at the shipyard;
the flight computer, propulsion mount, and airlock remain onboard hardware.
Only the stock diagram recipe is removed by its exact ID, bringing the managed
replacement set to 415 cards and 671 exact removals before the dockyard slice.

## Deferred stock entry paths

`industrial_space_entry_deferred.js` currently removes 35 recipes by exact ID.
The list covers prefabricated Ad Astra rockets and instant station creation,
early Cosmonautics propulsion/equipment, the embedded Simulated physics
assembler, the non-industrial oxygen shortcut, and premature Cosmowarp items.
It does not wipe an output, recipe type, or entire mod namespace.

The earlier stock Sputnik deferral has moved into the managed dockyard slice:
its exact stock ID is retired alongside the source-owned telemetry-probe
replacement, so it has one removal owner rather than both the boundary script
and KJSGen.

The embedded `simulated:physics_assembler` is especially important: its stock
recipe uses only two Andesite Alloy, an Andesite Casing, and a Lever but can
produce a functioning Sable craft. The nested-JAR-aware catalog sees that
recipe and the boundary continues to retire exactly that stock ID. A distinct
source-owned 5x5 recipe now supplies the legitimate downstream assembler path.

## Canonical Moon, Mars, Venus, and Mercury bridge

Rocketnautics owns the navigation graph while Ad Astra owns the physical Moon,
Mars, Venus, and Mercury surfaces. Source-owned universe overrides map the
`moon`, `mars`, `venus`, and `mercury` nodes only to their matching Ad Astra
surface dimensions, with no
second survival link. Their priority is above installed defaults/add-ons, so a
legacy or future lower-priority link cannot become the effective destination.

Sable dimension-physics resources give moving ships the Ad Astra surface
accelerations: 1.622 m/s² on the Moon, 3.72076 m/s² on Mars, 8.87 m/s² on
Venus, and 3.7 m/s² on Mercury. Rocketnautics
player gravity correction, atmosphere damage, universe rendering, and time
control are disabled in those linked dimensions. Ad Astra therefore remains
the single owner of player gravity, oxygen, temperature, sky, and time while
Sable supplies ship physics. Mercury's orbit dimension is not linked.

## Deep-space asteroid freight

Cosmonautics' installed asteroid spawner formerly accepted a dimension path
named `space` or any height above 5000, while the actual physical-station
dimension is `rocketnautics:deep_space`. The source mixin replaces that local
eligibility result with `DeepSpaceHelper.isDeepSpace`, using the installed API
and failing closed everywhere else. It leaves the installed spawn timer,
moving-body construction, and ore distribution intact and does not invoke the
spawn routine directly. The exact Titanium washing-to-Netherite Scrap shortcut
remains retired; normal Mercury-iron and asteroid-titanium crushing remain
available.

## Deliberately unresolved expansion work

Constructed station progression and gas-giant atmospheric extraction remain
later slices. Glacio is intentionally
not linked, and Cosmowarp remains deferred until the final solar-system escape
stage; neither may be activated by the Moon/Mars/Venus/Mercury bridge.

## Source-level acceptance

Run these checks with Java 21 and the installed pack catalog/mod directory:

```powershell
python tools/test_validate_space_entry_boundary.py
python tools/test_validate_space_destination_bridge.py
python tools/test_validate_orbital_flight_gate.py
python tools/test_validate_orbital_propulsion_slice.py
python tools/test_validate_orbital_life_support_slice.py
python tools/test_validate_orbital_construction_slice.py
python tools/test_validate_venus_calorite_slice.py
python tools/test_validate_mercury_asteroid_slice.py
python tools/test_validate_orbital_dockyard_slice.py
python tools/validate_space_entry_boundary.py --catalog "C:\path\to\recipe-catalog-current"
python tools/validate_space_destination_bridge.py --mods "C:\path\to\instance\mods"
python tools/validate_orbital_flight_gate.py --mods "C:\path\to\instance\mods"
python tools/validate_orbital_propulsion_slice.py --catalog "C:\path\to\recipe-catalog-current"
python tools/validate_orbital_life_support_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/validate_orbital_construction_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/validate_mercury_asteroid_slice.py --catalog "C:\path\to\recipe-catalog-current" --mods "C:\path\to\instance\mods" --jar build/libs/industrial_colonies-0.4.0.jar
```

Source validation proves the exact recipe boundary, dependency chain, block
registration, and bytecode target. A controlled client/world launch is still
required after deployment to prove the mixin applies to the installed runtime
and the new recipes/tags load without errors.
