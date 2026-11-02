# Controlled trace and independent-diamond boundary acceptance

**PASS — 2026-09-09, corrected combined run final-a2.** All ten trace/diamond cases passed. The first failed attempt is retained below; this result is controlled placement acceptance, not natural trace-abundance or modpack-balance certification.

## Isolated scope and evidence locations

Stage: `C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/isolated-runtime/geology-gametest-20260909-001051-895`.

- Passing report: stage `final-trace-a2.json`.
- Completed passing log: stage `final-acceptance-run-a2-20260909.log`.
- Passing disposable world: stage `final-acceptance-worlds/final-a2`.
- Preserved failed report/log: stage `final-trace-a1.json` and `final-acceptance-run-a1-20260909.log`; failed disposable world `final-acceptance-worlds/final-a1`.
- Tested candidate: stage `mods/industrial_colonies-0.4.0.jar`, **1,695,276 bytes**, SHA-256 `5A4CCD0BA37629225EE88996281FCA7F1A1B704E9E1EE5DC712ECB363EEFFFBA`.
- Source: project `tools/terrain-smoke/src/dev/godpc/industrialcolonies/terraincheck/TraceGameTests.java`.
- Test-only init: project `tools/controlled-geology/trace-smoke.init.gradle`, layered after the staged `geology-smoke.init.gradle` and `terrain-smoke.init.gradle`.
- The accepted combined run additionally uses project `tools/controlled-geology/final-acceptance.init.gradle` with revision `a2`, which supplies its separate world/report destinations and combined test selection.
- Exactly one registered trace test in namespace `ic_trace_smoke` contains these ten controlled cases. The passing combined run contained seven required GameTests overall; it is not ten separately registered trace tests.
- The addon-only empty template alias matches the production empty NBT exactly: SHA-256 `9D4331C7FA69FC53A50A1568F54856B9627A29D30BBB19DA30CA93FE6CC731B5`.

The launcher refuses a previously generated trace world or existing report. It does not deploy the candidate to the live pack. The fixture directly invokes the production private `traces(...)` method, which performs real world block writes; a delegating world adapter supplies explicit synthetic seeds and a flat surface height. This is controlled behavior coverage, **not natural surface availability**.

The final trace report records **10/10 completed cases**, **80,922 assertions**, and **901 ms** elapsed inside this harness. The combined log records `GEOLOGY_TRACE PASS`, **all seven required GameTests passed in 9.662 seconds**, saved dimensions, normal server shutdown, and `BUILD SUCCESSFUL in 1m 34s` (94 seconds; process exit 0). Assertion totals include repeated per-cell/world-access checks, not 80,922 independent scenarios.

World seed is **0**; fixture chunk is **(509665, 119465)**. Loaded settings/biomes/deposits SHA-256 is identical before and after: `f3771f9c23fa1b419a350f250721a0942377f72557053b09921ef55bc2730398`. Restored-and-verified cells total **18,439** across reused fixtures, not that many distinct world coordinates.

## Cases that passed

| Case | Actual final-a2 result |
| --- | --- |
| Iron at the supplied surface | Two Hematite blocks, matching the configured selected attempt |
| Copper below one covered layer | Two Chalcopyrite blocks at the first replaceable layer |
| Coal at `maxSurfaceDepth` | One Coal Ore block at the inclusive three-block search limit |
| Stone deeper than the search limit | Zero output with the only stone layer one block deeper |
| Dirt, air, water, lava | Four separate negative fixtures; zero replacements in each |
| Full attempt budget | Four selected nonoverlapping three-block attempts: six Hematite plus six Coal Ore, exactly twelve total |
| Independent diamond ceiling | 64 seeds × two bounded calls: three blocks per call, zero writes above Y=-20 |

All nine trace fixtures passed both exact input-layout and complete output-layout repeat comparisons, including their inert shells. The diamond case passed paired state hashes for all 64 seeds and all **128 bounded calls**. Its old unrestricted helper produced an above-ceiling neighbor in **21 of the 64 negative-control seeds**, demonstrating that this fixture detects the formerly unrestricted behavior. The bounded helper produced **zero** such writes while preserving its three-block quota.

The complementary source/resource validator, `tools/validate_geology_integration.ps1 -AllowReferenceTextures`, passed **1,126 assertions**. Its two added source contracts establish that the independent-diamond call site passes `integer(diamond,"maxY",-20)` into the bounded overload and that the overload removes candidates whose Y exceeds `maximumY` before clustering. These are source-wiring checks, not natural occurrence measurements. The existing explicit Bertrandite non-native reference-texture exception remains unchanged.

Default trace settings are unchanged: four attempts per chunk, 0.35 probability per attempt, 1–3 blocks per accepted attempt, and a three-block surface-search depth. Seeds are intentionally selected to exercise outcomes and the maximum budget; this is not a frequency measurement. Loaded settings/biome/deposit JSON digests must match before and after the test.

One owner chunk is explicitly requested. The trace fixture interior covers 14×14 columns and six vertical layers (1,176 cells). The corrected fixture adds an inert one-cell shell, for a total 16×16×8 volume (2,048 cells), still below the 4,096-cell limit. The diamond regression reuses a seven-cell cross in that chunk. All temporary states are restored and verified within each case's server tick. Minecraft may perform ordinary generation dependency work around the one requested chunk.

## First combined-run failure and test-only correction

`final-trace-a1.json` records **FAIL**, with **seven completed trace cases**, **28,465 assertions**, and failure `Same trace seed changed exact output layout`. Iron placed three Hematite blocks, Copper placed two Chalcopyrite blocks, and Coal placed three Coal Ore blocks. The deeper-than-search-limit, Dirt, Air, and Water cases had zero writes and identical repeated layouts.

The failure occurred in the eighth case, the Lava negative fixture. In that case the exact before/after material comparisons, zero-output count, and returned-no-change assertions had already passed on **both repeats**. Consequently, the mismatching output hashes establish that the two prepared fixture layouts differed; they do not establish a trace-generator write or production nondeterminism. The old report did not preserve those two input snapshots, so exact differing block IDs cannot be recovered from it. Native fluid placement reactions with unscreened neighboring terrain are the suspected setup mechanism, not a separately measured fact from that failed report.

The combined run ended with eight registered GameTests completed, one required failure (`traceplacementandbounds`), and process exit 1. It is **not** a passing final acceptance run. The last two cases (full attempt budget and independent-diamond ceiling) were not reached in this attempt.

The correction changes only the development fixture:

- Reset the whole bounded volume to inert Barrier before introducing the requested interior material. Keep a one-cell shell between fixture fluids and surrounding natural terrain.
- Assert that every prepared interior/shell state equals its intended state before calling production code.
- Compare exact input layouts between repeats in addition to all existing exact output, protection, quota, and return-value checks.
- Save the phase, mismatch count, hashes, and up to 32 concrete expected/actual block-state differences on a future layout mismatch.
- Clear temporary fluids to Barrier before restoring and verifying the original world states.

This fixture correction changed no production code or configuration and relaxed no existing assertion. The stronger input/output checks subsequently passed in final-a2, including the previously failing Lava case. The failed first attempt remains preserved and is not relabeled as passing.

## Limits

- The trace depth checks validate the configured **search-center depth**, not a new hard ceiling/floor for every neighboring trace-cluster cell. Existing trace clusters retain their one-block neighboring reach.
- The diamond case calls the bounded placement helper, not the naturally rare independent-diamond occurrence gate. Production wiring, biome admission, and natural abundance require complementary source/pure/worldgen evidence.
- No global configuration, rates, registry entries, production saves, extraction behavior, processing, or recipes are changed by this fixture.
- Trace loot and economic recovery remain separate evidence. This suite does not certify ingot-equivalent supply or progression balance.
- A passing test does not mean the full pack's unrelated warning/recipe logs are clean.
