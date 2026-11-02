# Controlled geology placement checks (development only)

These tests use the isolated server-compatible pack stage, not the live pack. They invoke the production `GeologyFeature.major` and `tiny` methods against temporary, restored blocks in one loaded fixture chunk. They do **not** establish natural occurrence rates, biome admission, full configured formation size, or the CARVERS hook; those have separate planner and fresh-world terrain tests.

Coverage is 24 approved profiles × 4 quality values, six additional failed association rolls, sixteen graphite depth/quality fixtures, one protection/owner-boundary fixture, and four bounded micro-placement fixtures: 119 major cases (each repeated for identical voxel output) plus four micro cases. Volumes are fixed at 512 cells, not the much larger configured natural volumes. Rare-event seeds are deliberately selected to exercise successful branches, including all three Osmium/Platinum/Iridium outputs; this is not a statistical sample.

The fixtures use real noise-column cover heights. They alternate stone/deepslate substrates, verify actual rich/association quotas and conservation, preserve air/water/lava/bedrock/dirt/gravel sentinels, reject any out-of-owner access through a world adapter, and restore all fixture cells before the next server tick. Configuration hashes must remain unchanged. No production recipes, registries, replacement tags, or rates are altered.

From the project root, layer the init files in this order:

```powershell
& .\gradlew.bat --offline --no-daemon --no-configuration-cache `
  -I isolated-runtime/geology-gametest-20260909-001051-895/geology-smoke.init.gradle `
  -I isolated-runtime/geology-gametest-20260909-001051-895/terrain-smoke.init.gradle `
  -I tools/controlled-geology/controlled-geology.init.gradle `
  -PcontrolledRevision=a1 runGameTestServer
```

Use the existing approved local Java 21/Gradle cache configuration. Compile-only validation can replace `runGameTestServer` with `compileTerrainSmokeJava`; it does not prepare or start a world.

The last init enables only `ic_controlled_smoke`, excluding the separate natural-terrain tests. NeoForge filters on the template namespace, so the init copies the existing empty template into the addon build resources at `data/ic_controlled_smoke/structure/geology_smoke_empty.nbt`; the test annotation uses that exact namespace. On actual launch it copies the existing normal-noise GameTest world-template datapack into stage `controlled-worlds/world-controlled-a1/datapacks/ic_normal_terrain`. The report is stage `controlled-report-a1.json`. A generated world or existing report causes a hard refusal; select a new revision for another run. It never deletes or resets an old world. The first a1 attempt exposed the namespace filter before any test ran; preserve its diagnostic log and use `-PcontrolledRevision=a2` for the corrected attempt.

The eight-minute harness wall guard cannot interrupt one synchronous chunk call. Minecraft can load/generate dependency chunks around the single explicitly requested fixture chunk. The complete pack startup may take longer than the fixture itself. Wait for the JSON PASS, required GameTest PASS, and process exit/shutdown evidence before reporting success.
