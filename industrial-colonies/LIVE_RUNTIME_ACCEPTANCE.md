# Live runtime acceptance

`tools/validate_live_runtime_log.py` performs a read-only check of the latest
integrated-server launch. It never starts Minecraft or changes the live pack.

The validator uses `latest.log` to require the complete owned KubeJS script
set, zero recipe-construction failures, the exact generated FTB Quests
topology, a successful client quest sync, and a join of the named acceptance
world. It uses `debug.log` to require exact application records for these 20
critical Mixins:

| Mixin | Exact runtime target |
| --- | --- |
| `TFMGPumpjackFiniteReservoirMixin` | `com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity` |
| `DungeonCrawlRandomItemsMixin` | `xiroc.dungeoncrawl.dungeon.treasure.RandomItems` |
| `SpaceTransitionHandlerMixin` | `dev.devce.rocketnautics.content.physics.SpaceTransitionHandler` |
| `DeepSpaceInstanceMixin` | `dev.devce.rocketnautics.content.orbit.DeepSpaceInstance` |
| `AsteroidSpawnerMixin` | `dev.devce.rocketnautics.content.physics.AsteroidSpawner` |
| `OxygenDistributorBlockEntityMixin` | `earth.terrarium.adastra.common.blockentities.machines.OxygenDistributorBlockEntity` |
| `GlobalSpacePhysicsHandlerMixin` | `dev.devce.rocketnautics.content.physics.GlobalSpacePhysicsHandler` |
| `SubLevelWarperUserDataMixin` | `dev.egg.SubLevelWarper` |
| `SableRemovalBoundaryMixin` | `dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer` |
| `ReactorSolidAccessPortEntityMixin` | `it.zerono.mods.extremereactors.gamecontent.multiblock.reactor.part.ReactorSolidAccessPortEntity` |
| `CosmowarpWarpDriveMixin` | `dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity` |
| `CosmowarpNetworkingMixin` | `dev.waco0311.cosmowarp.network.ModNetworking` |
| `CosmowarpWarpDriveBlockMixin` | `dev.waco0311.cosmowarp.block.WarpDriveBlock` |
| `CosmowarpWarpDriveMenuMixin` | `dev.waco0311.cosmowarp.menu.WarpDriveMenu` |
| `CosmowarpWarpDriveClickMixin` | `net.minecraft.world.inventory.AbstractContainerMenu` |
| `CosmowarpCrystalSlotOwnerMixin` | `dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity$1` |
| `CosmowarpCrystalSlotFreezeMixin` | `net.neoforged.neoforge.items.ItemStackHandler` |
| `CosmowarpCapabilityMixin` | `dev.waco0311.cosmowarp.Cosmonauticswarpdrive` |
| `WaterWheelBlockEntityMixin` | `com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntity` |
| `WindmillBearingBlockEntityMixin` | `com.simibubi.create.content.contraptions.bearing.WindmillBearingBlockEntity` |

These records prove that the installed targets received the finite-oil,
dungeon-loot, reactor, orbital, Stage 13 station, and Stage 14 interstellar
boundaries. Any owned Mixin apply, injection, or missing-class failure remains
fatal.

Successful resource reloads are normally silent. The validator therefore
rejects decoder or reload errors that name any of these 24 exact owned
resource IDs:

```text
industrial_colonies:regional_oil_field
industrial_colonies:add_regional_oil_fields
industrial_colonies:remove_tfmg_global_oil_deposits
rocketnautics:venus
industrial_colonies:ad_astra_venus
industrial_colonies:planetary/venus_arrival
rocketnautics:mercury
industrial_colonies:ad_astra_mercury
industrial_colonies:planetary/mercury_arrival
industrial_colonies:calorite_crushing_feed
rocketnautics:proxima_centauri
rocketnautics:glacio
industrial_colonies:ad_astra_glacio
industrial_colonies:planetary/glacio_arrival
industrial_colonies:ad_astra_moon_crystal_ore
industrial_colonies:add_ad_astra_moon_crystal_ore
dungeonnowloading:chests/labyrinth/rewards/gears
dungeonnowloading:chests/temple_of_duality/equipment/normal_puzzle
dungeonnowloading:chests/temple_of_duality/equipment/hard_puzzle
dungeonnowloading:chests/temple_of_duality/equipment/hard_combat
dungeonnowloading:chests/temple_of_duality/equipment/normal_combat
betterdungeons:zombie_dungeon/chests/common
betterdungeons:zombie_dungeon/chests/special
betterdungeons:zombie_dungeon/chests/tombstone
```

Stock-mod warnings for unrelated resources are deliberately outside this
acceptance boundary.

Run it after a clean client launch, world join, and shutdown:

```powershell
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\validate_live_runtime_log.py
```

This evidence proves that the critical injections reached the expected runtime
classes and that the owned data decoded without a reported error. It does not
replace a behavioral game test that extracts a full oil bucket and observes a
reserve decrement, or that opens generated dungeon loot. The static
`validate_regional_finite_oil_fields.py` and `validate_dungeon_tool_loot.py`
checks remain the source/JAR contract checks for those systems.

## Final Stage 13 and Stage 14 static acceptance

Run the mutation suites first:

```powershell
python tools/test_validate_outer_station_extraction_slice.py
python tools/test_validate_interstellar_escape_isolated.py
```

The current suites contain 37 Stage 13 tests and 84 Stage 14 tests. Then run
the full source/catalog/installed-mod/candidate-JAR contracts:

```powershell
python tools/validate_outer_station_extraction_slice.py --catalog "C:\path\to\recipe-catalog-current" --mods "C:\path\to\instance\mods" --jar build/libs/industrial_colonies-0.4.0.jar
python tools/validate_interstellar_escape_isolated.py --catalog "C:\path\to\recipe-catalog-current" --mods "C:\path\to\instance\mods" --jar build/libs/industrial_colonies-0.4.0.jar
```

Stage 13 pins three 5x5 manufacturing routes, four observation-only quests,
three installed dependency JARs, and 27 required candidate-JAR entries. Stage
14 pins five manufacturing routes, three exact stock removals, seven
observation-only quests, four installed dependency JARs, and 48 required
candidate-JAR entries/assets. These are static fail-closed contracts; the live
log validator and the behavioral checks below remain separate requirements.

## Post-Star orbital entry acceptance

The deployment preflight now fails closed on all three layers of the first
orbital slice before it constructs a live-file plan:

- `validate_space_entry_boundary.py` requires the exact reviewed set of 35
  stock space, warp, oxygen-shortcut, and ship-construction recipe IDs. It
  rejects missing, duplicate, unexpected, or broad removals.
- `validate_orbital_flight_gate.py` checks both the installed Cosmonautics
  transition target and the deployment-candidate Industrial Colonies JAR. The
  candidate JAR must contain the flight-computer block and block-entity
  classes, transition mixin, mixin configuration, blockstate, block/item
  models, loot table, and language entry.
- `validate_orbital_ambient_kinetics.py` pins Create 6.0.10's exact water-wheel
  and windmill-bearing bytecode, the two independent HEAD-cancellable Mixins,
  and the explicit wind/hydro dimension sets. It rejects an Overworld or broad
  base-generator rule and checks the deployment candidate JAR.
- `validate_planetary_freight_gates.py` and
  `validate_venus_calorite_slice.py` pin Cosmonautics 26.08.307's exact
  deep-space transition class, per-occupied-ship route computers, correctly
  slotted heat-resistant armor for Venus, and
  the managed-dimension Ender Chest denial. It also checks the candidate JAR.
- `validate_orbital_propulsion_slice.py` checks the recipe-less Hose Anchor,
  Engine Cycle Pipes, Engine Nozzle, and Thruster Mount source recipes, their
  post-Star dependency chain, assembled manifest records, and all four KJSGen
  Mechanical Crafting cards. Deployment runs it again against the merged
  KJSGen project that is actually staged for copying, so a three-way merge
  cannot silently omit a managed propulsion card.
- `validate_orbital_life_support_slice.py` pins the nine 5x5 Ad Astra pressure
  and habitat replacements and the canonical Mekanism-oxygen pass-through.
- `validate_orbital_construction_slice.py` pins the three reusable
  Refined-Radiance-Deployer certification passes, exact stock Diagram removal,
  both custom plan assets, and the 5x5 ground-side Physics Assembler. It also
  runs against the merged KJSGen project staged for deployment.

After a clean launch, world join, and JEI reload, confirm that the four modular
propulsion recipes and four orbital-construction recipes appear exactly once.
Certification must retain the flight computer, mount, and airlock. The stock
Rocket Thruster, Booster Thruster, Jetpack, Contraption Diagram, and Physics
Assembler recipes must remain absent while their authored construction routes
remain visible. A
block-built craft without an Orbital Flight Computer must not transition into
space. These behavioral checks complement the source/catalog/JAR checks; they
are not inferred from a successful game startup alone. The runtime validator's
positive `SpaceTransitionHandlerMixin` record proves injection into the exact
installed class, but only the two-craft transition test proves the gate's
behavior with and without the computer actor. Likewise, positive ambient
Mixin records prove target application, while a denied-dimension 0-RPM check
plus an Overworld generating control prove the intended wind/water behavior.
The destination matrix must separately prove Moon remains open; Mars fails
with zero or partially equipped occupied ships and accepts either approved
computer on every occupied ship; Venus fails without every ship computer or
any player's full correctly slotted suit and succeeds only with both. Ender
Chest acceptance likewise needs an
Overworld control and managed-offworld denial checks.
