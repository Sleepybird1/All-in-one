# Orbital Ambient Kinetics Audit

## Implemented boundary

Create water wheels and windmill bearings no longer manufacture free kinetic
power in environments where the pack does not provide ambient flowing water or
usable wind. The implementation is deliberately limited to two independent,
HEAD-cancellable Mixins:

- `WaterWheelBlockEntity#getGeneratedSpeed()F`
- `WindmillBearingBlockEntity#getGeneratedSpeed()F`

Each injection has `require = 1`. A Create update that removes or changes the
method therefore fails during Mixin application instead of silently reopening
the progression bypass. No Mixin targets the shared
`GeneratingKineticBlockEntity` base class, so engines, motors, hand cranks, and
every other deliberate power source remain outside this rule.

## Dimension policy

`AmbientKineticPolicy` owns separate explicit wind and hydro deny sets. Both
currently contain:

- `rocketnautics:deep_space`
- `ad_astra:earth_orbit`
- `ad_astra:moon` and `ad_astra:moon_orbit`
- `ad_astra:mars` and `ad_astra:mars_orbit`
- `ad_astra:mercury` and `ad_astra:mercury_orbit`
- `ad_astra:venus` and `ad_astra:venus_orbit`
- `ad_astra:glacio` and `ad_astra:glacio_orbit`
- legacy `rocketnautics:moon`
- legacy `rocketnautics_addon:mars`

The legacy IDs are harmless when their dimensions are absent. They prevent an
older save or optional bridge from reintroducing ambient generation.

`minecraft:overworld` is intentionally absent. Ordinary terrestrial Create
factories and water/wind generators aboard Sable vehicles in the Overworld
remain functional. The policy reads the block entity's parent `Level`
dimension, which is also the owning physical environment for Sable plot block
entities.

The wind and hydro sets remain separate even though their initial contents are
identical. A later planetary system can restore one resource without
accidentally restoring the other.

## Pinned compatibility

The companion metadata now accepts Create `6.0.10` only (`[6.0.10,6.0.11)`).
`tools/validate_orbital_ambient_kinetics.py` verifies:

- both exact source targets, descriptors, HEAD injections, cancellability, and
  `require = 1`;
- both exact and independently enumerated dimension sets;
- the absence of an Overworld or base-generator Mixin;
- the exact installed Create JAR name;
- Java 21 class structure, superclass, public instance
  `getGeneratedSpeed()F` methods, and exact SHA-256 hashes for both Create
  6.0.10 target class files;
- both compiled Mixins, the policy class, and Mixin registration in the
  deployment candidate JAR.

The companion runtime-log validator also requires positive application records
for both exact Create targets and rejects any owned Mixin application or
injection failure.

## Verification

Focused static and mutation validation:

```powershell
python tools\validate_orbital_ambient_kinetics.py --mods "C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods" --project-jar build\libs\industrial_colonies-0.4.0.jar
python tools\test_validate_orbital_ambient_kinetics.py
python tools\test_validate_live_runtime_log.py
```

The deployment preflight runs these checks automatically. Runtime acceptance
still requires an actual world launch: the debug log must show both Mixins
applied, denied dimensions must report 0 RPM for windmills/water wheels, and an
Overworld control build must continue to generate power.

This slice does not add or implement a station hull/pressure controller.
