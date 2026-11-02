# FTB Quests guidance boundary

FTB Quests is a non-gating factory guide. Physical recipe inputs, processing
machines, and built infrastructure are the only progression authority. Quest
completion never unlocks a recipe or MineColonies research node.

## Generated chapters

`tools/generate_ftbquests_native.py` deterministically writes ten standard
FTB Quests chapters under `pack-config-overrides/ftbquests/quests`:

| Chapter | Quests | Tasks | Role |
|---|---:|---:|---|
| Factory Foundations | 30 | 60 item | Primitive Start through the first working TFMG diesel engine |
| Dungeon Expeditions | 12 | 4 item, 8 structure, 1 advancement | Optional, reward-free exploration |
| Electrical Manufacturing | 7 | 17 item | Generation, motors, electronics, local power, and the first utility grid |
| Digital Logistics and AE2 | 6 | 14 item | Inscription, processors, ME storage/control, and starter autocrafting |
| Mekanized Industry | 8 | 23 item | Infusion, processing, drain-before-crafting Factory upgrades, Basic transmitters, polymers, and pattern automation |
| High-Energy Grid | 10 | 31 item | Advanced control, large digital/analog networks, storage, induction, and world loading |
| Nuclear Engineering | 9 | 20 item | Fuel preparation, reactor hardware, criticality evidence, and reprocessing |
| Industrial Endgame | 3 | 3 item | Preserved capstone chain |
| Orbital Engineering | 10 | 20 item | Post-Star flight authorization, propulsion, habitat readiness, ground-side ship construction, navigation, docking, and station-material commissioning |
| Planetary Industry | 18 | 39 item, 5 advancement | Moon/Mars/Venus/Mercury arrival, raw-metal and asteroid freight, three metallurgy lines, outpost utilities, physical navigation, and heat-protected Venus readiness |

The Industrial Endgame remains the exact three-objective chain:

   ```text
   Black Hole -> Industrial Reserve Core -> Industrial Star
   ```

The orbital handoff extends that visible route without changing the capstone:

```text
Industrial Star -> Orbital Flight Computer -> Hose Anchor
                                           -> Engine Cycle Pipes
                                           -> Engine Nozzle
                                           -> Thruster Mount
                                              ├-> Habitat Life-Support Readiness
                                              └-------------------------------┐
                                                                               v
                                                                      Physics Assembler
```

The four component observations follow their physical managed recipes: the
hose coupling feeds the engine-cycle plumbing, the plumbing feeds the nozzle,
and all three are integrated into the Thruster Mount. The habitat observation
then checks the Oxygen Distributor, Oxygen Sensor, Vent, and Airlock without
consuming them. The Physics Assembler observation depends on both the mount and
habitat branches and documents the ground-side construction yard. These are
ship-hardware milestones, not destination milestones. This initial chapter contains no
destination-specific objectives. The Orbital Flight Computer block remains the
physical ship-authorization mechanism; completing its quest does not grant
travel permission.

Three further observations commission the dockyard without becoming gates:
the complete navigation/telemetry suite, six Docking Connectors for three
matched service pairs, and material lots of 128 Steel Plating, 32 Steel Panels,
16 Cable Ducts, and 16 Fluid Pipe Ducts. These quantities remain in the
player's inventory and document that the terrestrial factory can sustain
repeatable station construction.

Planetary Industry continues from that final station-material observation:

```text
Station Materials -> Lunar Landfall -> 64 Raw Desh -> Desh Metallurgy
                 -> Mars Navigation Computer -> Martian Landfall
                 -> 64 Raw Ostrum -> Ostrum Metallurgy ------------------┐
                                      Desh Utility Array ----------------+-> Martian Service Reserve
                                                                          -> Closed-Loop Rations
                                                                          -> Venus Expedition Package
                                                                          -> Venusian Landfall
                                                                          -> 64 Raw Calorite
                                                                          -> Calorite Metallurgy
                                                                          -> Mercurian Landfall
                                                                          -> Returned Mercury Iron Sample
                                                                          -> Asteroid Titanium Contact
                                                                          -> Bulk Asteroid Freight Reserve
```

The four landfalls use no-reward changed-dimension advancements. The freight
and metallurgy tasks only observe inventory and never consume it. The Mars
Navigation Computer is a physical 5x5 Desh/electronics assembly and the runtime
travel authority; its quest is documentation, not the gate itself.
The Venus package observes the physical Venus Navigation Computer and all four
automated Netherite Space Suit pieces. Runtime inspection of the installed
computer and correctly slotted heat-resistant armor remains authoritative.
Mercury then requires its own Calorite-descended physical computer on every
occupied ship. The returned Mercury Iron Ore, first asteroid Titanium Ore, and
five-ore bulk reserve are observations only; they do not add a locator, claim,
spawn command, destination grant, or new Mercury metallurgy.

The early campaign has one root and real branches for kinetic processing,
material handling, fluids, storage, steam, brass logistics, rail freight,
metallurgy, petroleum, and engine fabrication. Branches converge only where a
physical build needs both capabilities. For example, diesel-engine
commissioning requires the refinery's TFMG Diesel branch and the engine-parts
branch.

The generated book contains 245 tasks: 231 tangible item observations, eight
native structure visits, and six native advancement observations. Item tasks do
not consume their items. There are no checkbox tasks, rewards, commands,
stages, research references, or recipe-unlock fields. Counts such as two
Crushing Wheels or nine Mechanical Crafters describe useful build lots; they
are not payment because completion leaves every item with the player.

The dungeon chapter is a separate optional branch. It never gates factory or
endgame progress and does not require kills, encounter drops, trophies, bosses,
or Apotheosis content. Structure quests unlock from preparation-item or
advancement observations rather than other structure tasks because FTB Quests
does not retroactively check a `StructureTask` at login. The random Dungeon
Crawl stone-pickaxe observation is deliberately a dead end.

FTB Quests has no reliable task for proving that a dynamic Create/TFMG machine
is turning under load. The final diesel quest therefore audits the complete
commissioning kit and explicitly instructs the player to insert the cylinder
and shaft, connect TFMG Diesel and exhaust, start the engine, and verify shaft
rotation. It does not misrepresent an item task as runtime telemetry.

## TFMG-specific guidance

The petroleum descriptions follow the installed TFMG 1.2.0 implementation and
Ponder text:

- the pumpjack uses an industrial pipe to the deposit, a Pumpjack Base,
  holder, crank, connector, head, glued hammer parts, and kinetic input;
- the steel distillation tower uses Steel Tanks, a Steel Distillation
  Controller, Industrial Pipes, Distillation Outputs, heat, and independently
  routed products;
- a regular engine receives a Diesel Engine Cylinder and shaft, TFMG Diesel
  input, and an exhaust path; redstone starts it and the Engine Controller can
  provide direct control.

TFMG Diesel remains the named canonical fuel. The quest campaign does not add
or modify recipes.

Mekanism Factory upgrades use physical construction rather than the runtime
installer shortcut. The First Basic Factory guidance tells the player to drain
and empty the predecessor, then consume that empty machine and the Basic Tier
Installer in the 5x5 Mechanical Crafting build. Right-click installer upgrades
are disabled for the managed Factory and Energy Cube families.

## Stable endgame identity

The endgame chapter keeps filename `industrial_progression`, chapter ID
`5EAE8C019077D7EF`, and the original three quest/task IDs. This preserves the
existing capstone identity for worlds that loaded the earlier compact chapter.
The old Draw.io/MineColonies research layout is not read, generated, or edited.

## Sources, generation, and validation

- `progression/ftbquests_guidance_campaign.json` is the reviewable early
  campaign source and names the implemented post-Diesel extension.
- `FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json` is the hashed, reviewable source
  for the five later factory chapters. Its evidence validator resolves all 105
  added item tasks to installed and implemented production contracts.
- `progression/ftbquests_dungeon_exploration.json` is the reviewable optional
  exploration source and contains the exact installed structure/advancement
  IDs selected by the dungeon audit.
- `progression/industrial_megaprojects.json` remains the untouched three-quest
  capstone source.
- `progression/ftbquests_orbital_engineering.json` is the reviewable post-Star
  manual source. It observes the Orbital Flight Computer, four installed
  Rocketnautics components, four habitat components, the ground-side
  Physics Assembler, navigation instruments, four-channel docking, and the
  first station-material batches without adding a reward, stage, research
  gate, recipe unlock, or destination objective.
- `progression/ftbquests_planetary_industry.json` is the reviewable
  Moon/Mars/Venus/Mercury continuation. It observes four real dimension changes,
  64-item raw Desh, Ostrum, and Calorite freight lots, all three five-stage
  metallurgy lines, outpost utilities, all three physical navigation
  computers, the heat-resistant expedition suit, returned Mercury iron, and
  asteroid freight without adding rewards, consumption, or stages.
- `tools/generate_ftbquests_native.py` emits strict JSON/SNBT, localization,
  deterministic IDs, and a generated manifest. `--check` detects drift without
  writing.
- `tools/validate_ftbquests_native.py` validates source/output parity,
  topology, installed item IDs, exact structure and advancement paths in the
  installed JARs, native FTB task classes, managed/stock/scripted/loot
  production paths, the no-gates/no-rewards contract, and capstone ID
  preservation.
- `tools/test_ftbquests_guidance_campaign.py` exercises the valid campaign and
  rejects checkbox tasks, reward fields, item consumption, dependency cycles,
  unregistered task items, unknown structures, and boss/Apotheosis objectives.
- `tools/validate_orbital_engineering_quests.py` proves the direct Industrial
  Star handoff, the four-component manufacturing route, installed item identities, generated
  parity, source fingerprint, and non-gating boundary.
- `tools/test_orbital_engineering_quests.py` mutation-tests the entry edge,
  component IDs, reward/consumption rejection, destination exclusions, and
  generated dependency topology.
- `tools/validate_planetary_industry_slice.py` pins the one-grit feed tags,
  exact vat and Refined Radiance routes, 36 exact shortcut removals, packing
  preservation, raw-only Moon loot, the two exact structure palette repairs,
  advancements, and native quest parity.
- `tools/build_planetary_structure_overrides.py` deterministically replaces
  the Lunar Tower's finished Desh Block and Mars Temple's finished Ostrum Block
  with same-length native stone palette strings while preserving the rest of
  each installed structure NBT exactly.
- `tools/test_validate_planetary_industry_slice.py` mutation-tests those
  physical, loot, quest, and compiled KJSGen boundaries.
- `tools/validate_mercury_asteroid_slice.py` and its mutation suite pin the
  Mercury surface bridge, strict physical-computer authorization, installed
  deep-space eligibility API, retained Titanium shortcut retirement, 5x5
  recipe, and four observation-only continuation quests.
- deployment preflight checks/regenerates the deterministic output and runs the
  validator before any live-pack write.

Run the focused checks with:

```powershell
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\generate_ftbquests_native.py --check
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\validate_ftbquests_native.py
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\test_ftbquests_guidance_campaign.py -v
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\validate_orbital_engineering_quests.py
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\test_orbital_engineering_quests.py -v
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\validate_planetary_industry_slice.py
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\test_validate_planetary_industry_slice.py -v
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\validate_mercury_asteroid_slice.py --catalog 'C:\path\to\recipe-catalog-current' --mods 'C:\path\to\instance\mods' --jar build\libs\industrial_colonies-0.4.0.jar
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\test_validate_mercury_asteroid_slice.py -v
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\build_planetary_structure_overrides.py --check
```

These commands only use project and audit artifacts. They do not write to the
live CurseForge instance or launch Minecraft.
