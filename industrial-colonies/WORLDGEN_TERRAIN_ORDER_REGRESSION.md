# Terrain-order regression: ordinary decoration versus geology

Date: 2026-09-09. **Status: corrected A/B regression PASS; both fresh-world runs passed 5/5 required tests and the strict shape-state/count comparison.** This is bounded runtime verification, not production deployment or whole-pack acceptance.

## Scope and preserved evidence

Project root: `C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies`.

Isolated stage: `C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/isolated-runtime/geology-gametest-20260909-001051-895`.

All runtime paths below are relative to that exact stage:

- Original fresh worlds: `terrain-worlds/terrain-a` and `terrain-worlds/terrain-b`.
- Original B report: `terrain-report-b.json`. The original A JSON was later overwritten by a development-selector mistake in `final-a1`; **the current `terrain-report-a.json` is not original A evidence**. Its former identity was 11,900 bytes, SHA-256 `21F064D56DEBBC2633CEA239676C65D74881B1339DF96CA9BC78E77675523C20`. No intact JSON backup was found or fabricated. The original A log/world, saved-block comparison and this contemporaneous count record remain preserved. The later contents are also preserved explicitly as `final-unexpected-terrain-a1.json`.
- Successful original launch logs: `terrain-run-a2-20260909.log` and `terrain-run-b-20260909.log`. The earlier `terrain-run-a-20260909.log` is a DevLaunch classpath failure, not terrain evidence.
- Saved-block comparison: `terrain-saved-block-diffs.json`.
- Corrected fresh-world destinations: `terrain-worlds/terrain-a-fixed1` and `terrain-worlds/terrain-b-fixed1`.
- Corrected report destinations: `terrain-report-a-fixed1.json` and `terrain-report-b-fixed1.json`.
- Corrected launch logs: `terrain-run-a-fixed1-20260909.log` and `terrain-run-b-fixed1-20260909.log`.
- Strict corrected comparison: `terrain-comparison-fixed1.json`, checked at `2026-09-09T06:56:00.1793698Z`.

The candidate used for the corrected A/B runs was verified at 1,695,174 bytes, SHA-256 `ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546`; that JAR is now preserved in `backups/diamond-boundary-fix-20260909/`. The stage currently holds the later diamond-ceiling-corrected build identified in `WORLDGEN_FINAL_ACCEPTANCE.md`. Both successful `fixed1` reports, logs and their comparison are untouched.

Pre-fix source/JAR copies remain under project `backups/terrain-order-fix-20260909/`: `GeologyFeature.java`, `industrial_colonies.mixins.json`, and `industrial_colonies-0.4.0-before-terrain-fix.jar`.

## Original result: individual tests passed, order comparison failed

Both original logs report **all 5 required GameTests passed**. This establishes each run's internal assertions, not equality between runs. The later A/B comparison found a real Galena defect.

Both worlds use seed 0, `NoiseBasedChunkGenerator`, `minecraft:overworld` noise settings supplied by **Tectonic**, and build heights -64 through 319. Regions Unexplored was observed in actual generated chunks, not merely detected as an installed mod. The bounded natural-planner search inspected 50 regions, selected 3 families, and explicitly requested 14 initially unloaded footprint chunks. No probability, spacing, or quality override was used.

| Formation center (X, Y, Z) | Intended blocks | A: actual host before rich / rich | B: actual host before rich / rich | Geology equality |
| --- | ---: | ---: | ---: | --- |
| Chalcopyrite (-1, -24, 638) | 2,957 | 2,885 / 80 | 2,885 / 80 | Exact retained-geology and shape-state hashes |
| Galena (-874, 21, -624) | 2,036 | 1,350 / 80 | 1,385 / 82 | **Mismatch** |
| Sphalerite (-1948, -50, -1603) | 1,210 | 1,144 / 28 | 1,144 / 28 | Exact retained-geology and shape-state hashes |

Galena's center is in `minecraft:sulfur_caves`; the actual and planned surface biome is `regions_unexplored:shrubland`, surface Y=66. Plans, geometry, quality, and 0.06 rich fraction match across A/B. Config hashes also match: settings `44e99a5d5905a482252cef21c04bedff56b993fa9527024d6309c27d51473bfd`; biome families `a6b0db109b48ca7d8c5bc25a32cc327c238c2ea38cfd86f11bdce007a4283562`; deposits `0bdad969b46df4e68e3cd56c72b233a308895e185c1400808964cb7ace300a1a`.

Saved chunk data shows exactly 37 geology-related A-to-B block differences:

- 34 `minecraft:dirt` -> `industrial_colonies:galena`, in chunk (-55, -40).
- 1 `minecraft:gravel` -> `industrial_colonies:galena`, in chunk (-54, -39).
- 2 `industrial_colonies:galena` -> `industrial_colonies:rich_galena_ore`, consistent with the larger actual host pool changing its rich quota.

The saved comparison also contains unrelated granite/diorite/andesite and vegetation differences. These are not evidence of a random regional-plan change.

## Cause and selected fix

Previously, `GeologyFeature.major` ran during `underground_ores` and accepted only the current stone/deepslate replacement tags. Ordinary `ore_dirt`/`ore_gravel` decorators can write across their owning chunk boundary. If a neighbor decorates first, its dirt/gravel is already non-replaceable when geology reaches the target chunk; in the opposite order, geology occupies that stone first and the later decorator cannot replace the custom host. This explains the exact saved-block transitions and host-count change without altering any regional decision.

Moving the feature merely to `raw_generation` would not establish a cross-chunk barrier: each chunk executes its own decoration steps. The implemented fix instead uses the real status dependency boundary documented in the cached Minecraft 1.21.1 `ChunkPyramid`: **FEATURES requires CARVERS within radius 1 and may write within radius 1; CARVERS writes only its owner (radius 0).**

Changed production-source paths, relative to the project root:

- `src/main/java/dev/godpc/industrialcolonies/geology/GeologyFeature.java`: new `generateDeposits(WorldGenLevel, ChunkPos)` owns major deposits and micro deposits. The existing placed feature now handles only trace and placer decoration. Major exterior cover uses immutable noise-column heights cached by X/Z for one generation invocation, because neighboring chunks at CARVERS need not yet have usable terrain heightmaps.
- `src/main/java/dev/godpc/industrialcolonies/mixin/GeologyCarversMixin.java`: new `NoiseBasedChunkGenerator.applyCarvers` TAIL hook, `industrialColonies$placeGeologyAfterCarvers`. It runs for AIR carving, Overworld, and non-upgrading chunks only. It does not load or write neighboring chunks.
- `src/main/resources/industrial_colonies.mixins.json`: registers the new required mixin.

The hook uses the verified mapped signature `(WorldGenRegion, long, RandomState, BiomeManager, StructureManager, ChunkAccess, GenerationStep.Carving)`. Air, fluids, bedrock, and non-replaceable blocks remain protected by the existing predicates. Dirt/gravel decorators and replacement tags were **not** removed or broadened. Probabilities, regional spacing, recipe data, and rich/association rules were not changed.

Small deposit indicators remain with major placement so their recorded counts stay coherent; their reads/writes are owner-chunk-only. They now precede decoration and can still be covered by later features. Surface traces and placers remain later, in the original placed-feature stage.

## Corrected result: PASS

`terrain-comparison-fixed1.json` reports `status: PASS`, `exactReverseOrder: true`, and `allShapeStatesAndCountsIdentical: true`. Both corrected reports confirm unchanged config hashes, seed 0, Tectonic noise settings, actual Regions Unexplored biomes, the same 50-region search, and the same three naturally selected families across 14 requested chunks. Both processes exited successfully, recorded server shutdown/chunk-save markers, and logged `BUILD SUCCESSFUL`.

| Formation | A and B actual host before rich | A and B final low-yield host | A and B rich blocks | Nonempty chunks | Cross-chunk neighbor bonds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Chalcopyrite | 2,957 | 2,874 | 83 | 4 | 446 |
| Galena | 1,467 | 1,380 | 87 | 6 | 214 |
| Sphalerite | 1,210 | 1,181 | 29 | 4 | 176 |

Matching final SHA-256 values in **both** corrected worlds:

- Chalcopyrite, full shape-state and retained geology: `8877a9b82788811bedf7c8382ecb1a5b26f6b006e98363dc37bd2dccf5b223c8`.
- Galena, full shape-state: `8b3c2f6458506eba2a33e0784ca1d53615a8d6d8b8f687e8af07b7aef7de2b67`; retained geology: `695adc451a70bc8510bbda94dfa71d41bf375a0d2db4e50c1eca5e8c5f48b96d`.
- Sphalerite, full shape-state and retained geology: `b467b69913ebc6f675dd16cf24a19367a37f1ff8ebb2bf268c34d75eeac4810d`.

The corrected Galena is still terrain-clipped: 1,467 of 2,036 intended positions become geological blocks. Equality was achieved without filling those missing positions or expanding replacement tags. Higher corrected counts across formations are expected when dirt/gravel decoration can no longer win a race against deposit placement.

Timing: A's bounded terrain harness took **13,564 ms** and the full Gradle/server invocation **294 s**; B's harness took **9,183 ms** and its full invocation **222 s**. These timings include different startup/cache effects and are not a controlled performance comparison.

The logs are **not globally clean**. In A, after `All 5 required tests passed` and `Stopping server`, Spark's `spark-java-sampler-0-0` emitted `RejectedExecutionException: Server already shutting down` while its `AsyncWorldInfoProvider` requested world information. The stack is Spark's shutdown sampling path, not the geology sampler. Chunk saving and successful process completion followed. Existing out-of-scope recipe/mod warnings are not certified fixed. No new geology-owned failure was identified in these corrected runs.

## Acceptance criteria applied

The accepted result uses both fresh corrected worlds and their explicit comparison, rather than compilation or a single test pass alone:

1. Confirm the intended candidate hash and unchanged config hashes; confirm normal Tectonic terrain, seed 0, and actual RU evidence.
2. Both runs pass all 5 required tests, including the new transformed hook check and the bounded terrain test.
3. The same three natural plans and shapes are selected, with positive retained geology spanning multiple chunks.
4. Every tested chunk conserves its observed pre-rich host count; actual rich placement equals the deterministic target and per-material allocation. Do not demand actual count equals intended volume: terrain clipping is legitimate.
5. A/B actual host counts, rich targets/counts, associated counts, and sorted retained-geology SHA-256 hashes are identical. Inspect full shape-state hashes and saved-block differences as additional evidence; unrelated decorative differences outside geological positions are not a geology regression by themselves.
6. No new geology-owned resource/mixin errors, out-of-owner writes, or chunk-status access errors appear.

## Limits

- This test covers three naturally selected formations at one seed, not every mineral, quality, biome, cave shape, mountain, or nearby structure.
- The 14 explicit footprint requests exclude Minecraft's implicit generation dependency halo. The harness's eight-minute wall guard cannot interrupt one synchronous chunk generation call.
- The requested order was exactly reversed; Minecraft's internal dependency-halo task order was not fully controlled. This regression passes the recorded A/B pair, not every possible scheduling interleaving.
- The change establishes deposit placement before decoration; it does not promise that arbitrary later third-party features cannot carve or overwrite blocks. Such losses should be exposed by observed-versus-final count checks rather than hidden by broad replacement rules.
- Exact entire-world/chunk byte equality is not claimed. The existing pack contains independent order-sensitive decorative features.
- Existing production saves were not used for this experiment. The hook skips upgrade/retrogen chunks; deployment and broader gameplay validation remain separate decisions.
- Client rendering, oil placement/extraction, whole-world mineral distributions, and survival-economy balance were not accepted by this terrain test.
