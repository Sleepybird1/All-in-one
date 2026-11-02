# Native TFMG oil acceptance fixture

Development-only addon `ic_oil_smoke`; no source or resource from this folder is included in the Industrial Colonies production JAR. It does not alter generation settings, TFMG configuration, recipes, the installed pack, or any live save.

## What it checks

The fixture searches at most 289 regional oil candidates using the unchanged planner and generator noise sampling. It requests one naturally eligible well chunk, snapshots its 16×16×32 bottom volume, clears scanner-findable bottom markers as a negative control, then invokes the **actual registered** `industrial_colonies:regional_oil_reservoir` configured feature. It requires the resulting native oil marker, source crude oil, and a positive native `SurfaceScannerBlockEntity.hasOil()` result.

It installs a native pipe-connected pumpjack base in that disposable snapshot, calls `findDeposit()` and the real `process()` implementation, verifies native lazy reservoir registration and 1000 mB TFMG crude extraction, and checks the existing finite-reservoir mixin debits exactly one reserve unit. A controlled zero-reserve state must stop further extraction; its prior amount is immediately restored. Native `TestSavedData.save/load` must roundtrip that primary well and its amount. Finally, the fixture removes its new reservoir record and restores all captured block states.

This is **not** a natural occurrence/frequency survey, complete powered pumpjack/hammer assembly test, client scanner UI test, full associated-well persistence test, restart/disk-persistence test, or production-balance test. Minecraft may generate dependency chunks while servicing the one explicit chunk request. A 240-second wall guard cannot interrupt a synchronous chunk-generation call. The temporary fluid placement can schedule native block/fluid updates in the disposable world; no live world is used.

## Invocation prerequisites

Coordinate with the root agent before any server launch; do not run alongside the 8 GB client acceptance process. Layer `oil-smoke.init.gradle` **after** the approved stage's `geology-smoke.init.gradle`. The addon has namespace `ic_oil_smoke`, uses the unchanged candidate in staged `mods`, and writes `oil-native-report.json` inside that stage. Expected runtime marker: `GEOLOGY_OIL_NATIVE PASS`.

The init's `prepareOilNativeFixture` dependency copies the existing `tools/terrain-smoke/world-template` datapack into the fresh `isolated-runtime/geology-gametest-20260909-001051-895/oil-worlds/oil-native` world before an explicitly invoked runtime task. This makes the GameTest flat preset resolve to the pack's normal Overworld noise generator. A fresh-world/report guard refuses reuse. Compile-only tasks do not prepare a world or launch Minecraft. Root owns runtime invocation.

The annotation explicitly uses template namespace `ic_oil_smoke`, matching the enabled filter: NeoForge filters by that template namespace. `processOilSmokeResources` copies the exact existing empty NBT into generated addon resources at `data/ic_oil_smoke/structure/geology_smoke_empty.nbt`; the production source and filter remain unchanged.

Compile/resource-only tasks: `compileOilSmokeJava processOilSmokeResources`; runtime task: `runGameTestServer`. Both require the existing verified offline launcher init followed by this addon's init. When another isolated process holds the already verified Minecraft artifact, `-x createMinecraftArtifacts` uses the existing exact artifact without regenerating it. No EULA or network-policy change is made by this addon.

Status: bounded native oil acceptance **100% complete / PASS**. The coordinated isolated run passed its one required GameTest: 8,253 checks, scanner negative/positive controls, native feature placement, 1,000 mB extraction, reserves 1,890 → 1,889, exhaustion stop, native primary-well NBT roundtrip, and completed cleanup. Process exit 0; Gradle duration 94 seconds. See [RESULTS.md](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/tools/oil-smoke/RESULTS.md>) for exact evidence, hashes, coordinates and scope limitations. This is controlled native compatibility, not a natural-frequency survey or full machinery/production-balance acceptance.

Namespace-corrected addon compile/resources also passed on Java 21 / NeoForge 21.1.248 (`compileOilSmokeJava processOilSmokeResources`, 10 seconds, offline, fresh process, existing Minecraft artifact retained). The generated 107-byte NBT matches the unchanged source exactly: SHA-256 `9D4331C7FA69FC53A50A1568F54856B9627A29D30BBB19DA30CA93FE6CC731B5`. The first sandboxed/shared-daemon attempts hit the known cached-JAR access failure; a fresh offline Gradle process with forked javac compiled successfully.
