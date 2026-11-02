# Orbital Construction Audit

## Outcome

The first authored Sable ship-construction route is source-owned. It begins
only after both the modular Thruster Mount and habitat Airlock exist, preserves
the hardware intended for installation aboard the vessel, and ends in a
ground-side Physics Assembler:

```text
Orbital Flight Computer (retained)
  + AE Blank Pattern -> Guidance-Certified Construction Plan
Thruster Mount (retained)
  + Guidance Plan -> Propulsion-Certified Construction Plan
Airlock (retained)
  + Propulsion Plan -> Contraption Diagram
Contraption Diagram
  + 5x5 heavy/digital gantry -> Physics Assembler
```

All three certification operations use the exact
`createcasing:refined_radiance_deployer` route with `keep_held: true`. The
Orbital Flight Computer, Thruster Mount, and Airlock therefore remain usable
as onboard hardware instead of becoming construction-yard consumables.

## Stock-path ownership

The embedded Simulated mod ships two stock recipes inside Create Aeronautics:

| Stock ID | Type | Inputs | Decision |
|---|---|---|---|
| `simulated:contraption_diagram` | shapeless | Paper + Physics Assembler | Removed by this managed replacement's exact ID |
| `simulated:physics_assembler` | shaped | Andesite Alloy + Andesite Casing + Lever | Remains in the exact 35-ID deferred boundary |

The diagram is no longer a backwards assembler-to-paper shortcut. Its only
authored path is the reusable three-stage certification line. The replacement
Physics Assembler is a 5x5 Mechanical Crafting build using TFMG heavy plates,
motors, frames and circuit boards, Create pistons, Ad Astra vents, Mekanism
ultimate controls, ComputerCraft advanced computers, and the certified diagram.

At completion of this construction slice, the source set contained 415 managed
recipe cards and 671 exact stock removals. The later dockyard slice adds its
own reviewed records without broad Simulated removal.

## Quest observation boundary

Orbital Engineering adds two non-gating observations. Habitat Life-Support
Readiness observes the Oxygen Distributor, Oxygen Sensor, Vent, and Airlock.
Physics Assembler depends visibly on both that habitat observation and the
Thruster Mount. Neither quest consumes items, grants rewards, unlocks recipes,
or authorizes a destination.

## Source-level acceptance

```powershell
python tools/test_validate_orbital_construction_slice.py
python tools/validate_orbital_construction_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/test_orbital_engineering_quests.py
python tools/validate_orbital_engineering_quests.py
```

These checks pin the exact machine, held-catalyst behavior, dependency ancestry,
custom item registration/models/language, stock nested-JAR evidence, compiled
KJSGen cards and removal, immutable MineColonies layout, and observation-only
quest topology. This source batch has not been deployed to the live instance.
