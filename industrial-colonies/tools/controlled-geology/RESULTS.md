# Controlled geology placement acceptance

**PASS — 2026-09-09, corrected run a2.** This verifies the bounded development-only placement suite, not natural mineral abundance or complete modpack balance.

## Exact evidence

Stage: `C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/isolated-runtime/geology-gametest-20260909-001051-895`.

- Report: stage `controlled-report-a2.json`.
- Completed process log: stage `controlled-run-a2-20260909.log`.
- Disposable world: stage `controlled-worlds/world-controlled-a2`.
- Candidate: stage `mods/industrial_colonies-0.4.0.jar`, SHA-256 `ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546`.
- Test source: project `tools/terrain-smoke/src/dev/godpc/industrialcolonies/terraincheck/ControlledGeologyGameTests.java`.
- Test-only launcher: project `tools/controlled-geology/controlled-geology.init.gradle`, layered after the two existing staged GameTest init files.

The report records `status: PASS`, **123 completed cases**, **1,164,832 assertions**, and **5,249 ms** elapsed within the fixture harness. The log records `GEOLOGY_CONTROLLED PASS`, **all 1 required GameTest passed**, normal server shutdown, and `BUILD SUCCESSFUL in 1m 33s`. The single registered GameTest contains the 123 cases; it is not 123 separately registered GameTests. The large assertion count includes repeated per-cell and world-access checks, not that many independent scenarios.

Seed: **0**. Exactly **one fixture chunk** was explicitly requested, at chunk **(-533063, 302729)**. Major fixtures are connected **8×8×8, 512-cell** volumes. Minecraft's surrounding generation dependency work is not counted as another explicitly requested fixture.

Combined loaded settings/biomes/deposits digest before and after the test is identical: `f3771f9c23fa1b419a350f250721a0942377f72557053b09921ef55bc2730398`.

## Coverage that passed

| Case group | Cases | Actual assertions exercised |
| --- | ---: | --- |
| All approved profiles × all four qualities | 96 | Real major placement, rich quotas, per-material allocation, associations, conservation, zero-rich profiles |
| Failed association rolls | 6 | Pentlandite→Cobalt at Poor/Normal; Thorium→Uraninite at all four qualities remain absent when the roll fails |
| Graphite depth/quality fixtures | 16 | Four qualities at Y -63…-56, -53…-46, -39…-32, and -18…-11 |
| Protection and owner clipping | 1 | Air, water, lava, bedrock, dirt, and gravel remain unchanged; extra out-of-owner geometry cannot cause a neighboring access |
| Micro placement | 4 | Exact one-, two-, and three-block placement; owner-boundary case; untagged dirt preserved |
| **Total** | **123** | **119 major-placement cases plus 4 micro cases** |

Every major case was rebuilt and repeated using the same constructed Plan and seed. All **119 paired full fixture-state hashes matched**. Actual low-yield host + rich + associated counts conserved the accepted host volume; production observations and actual block counts agreed. Both stone and deepslate substrates were used. Cover checks used real noise-column heights, not invented elevations or globally altered rules.

The delegating world adapter rejected any out-of-owner block access by the exercised production paths. Fixtures were restored and verified before advancing to the next server tick, including fluid sentinels. `restoredFixtureWrites: 60955` is the sum of restored cells across reused fixtures, not 60,955 distinct world coordinates.

## Selected material evidence

Actual ultramafic rich-pool counts, in **Osmium / Platinum / Iridium** order:

| Quality | Total rich | Os | Pt | Ir |
| --- | ---: | ---: | ---: | ---: |
| Poor | 8 | 5 | 2 | 1 |
| Normal | 20 | 14 | 5 | 1 |
| Rich | 37 | 26 | 9 | 2 |
| Exceptional | 61 | 43 | 15 | 3 |

Seeds were deliberately selected to exercise every pool member, including rare Iridium in a small Poor pool. These are successful branch-coverage examples, **not a statistical estimate** of the 70/25/5 distribution.

Successful Pentlandite→Cobalt cases placed **1, 1, 4, 8** associated blocks by ascending quality; the two applicable failure cases placed zero. Uranium→Thorium cases placed **3, 6, 10, 15**; successful Thorium→Uraninite cases placed **3, 4, 7, 6**, while all four deliberately failed chance rolls placed zero. The chosen seeds and configured variable fractions explain non-monotonic individual examples; the test does not assert those examples are average yields.

For Graphite, positive depth/quality cases exercised actual Diamond Ore placement. Poor graphite at Y -39…-32 correctly produced none, and all four above-band fixtures at Y -18…-11 produced none. Graphite has no ordinary rich pool; diamond is its separate depth-dependent association.

## Harness issue corrected before acceptance

The first Minecraft launch, `controlled-run-a1-launch-20260909.log`, exited without running tests and reported `No test functions were given!`. It is **not** a passing test run. Two earlier a1 logs are build-artifact file-lock failures, also not test evidence.

Cached NeoForge sources confirmed that the enabled-namespace filter uses the explicit `@GameTest.templateNamespace`, ahead of `@GameTestHolder`. The development annotation was corrected to `ic_controlled_smoke`; the controlled init now copies the original empty NBT under that addon-only namespace. The alias hash matches the original exactly: `9D4331C7FA69FC53A50A1568F54856B9627A29D30BBB19DA30CA93FE6CC731B5`. The filter remained controlled-only, so natural A/B tests were not silently rerun. No production placement change was needed for this discovery issue.

## Limits and complementary evidence

- Plans, qualities, and successful rare-event seeds are constructed/conditioned. Natural biome admission, occurrence probabilities, spacing, full natural volume, and scheduling are not measured here. Use the pure planner tests and separately passed natural-terrain A/B regression for those respective claims.
- The 512-cell fixture volume does not apply quality size multipliers to real thousands-of-block formations. Quality-dependent rich and association behavior is tested; natural-size generation is separate.
- Direct production `major` and `tiny` calls do not by themselves validate the CARVERS injection or feature registration. The fresh-world A/B and required-mixin tests provide that evidence.
- Micro cases test bounded placement, not occurrence frequency. Existing loot tests are separate from this suite. Surface trace supply, placer frequency, and ingot-equivalent recovery economics still require their own distribution/processing-yield acceptance; the loaded trace configuration describes its pre-clipping supply estimate as provisional.
- Oil generation/extraction, client rendering, recipes, progression balance, and player-world performance are outside this suite. Existing unrelated mod/recipe warnings were not repaired or certified absent.
- All edits and fixture writes were development/stage-only. No live pack deployment or production-save mutation is claimed.

## Final candidate rerun — combined final-a2 PASS

**Latest acceptance: 2026-09-09, 100% of this bounded suite complete.** The earlier sections retain the separate `ABC9A4D5…` candidate's original counts and evidence; they are not relabeled as this newer run.

The final staged candidate is **1,695,276 bytes**, SHA-256 `5A4CCD0BA37629225EE88996281FCA7F1A1B704E9E1EE5DC712ECB363EEFFFBA`. This includes the independent-diamond neighboring-voxel Y-ceiling correction. The combined layer `tools/controlled-geology/final-acceptance.init.gradle`, revision `a2`, ran in the fresh stage world `final-acceptance-worlds/final-a2`, with the same approved 233-JAR server-compatible subset and both test addons.

- `final-controlled-a2.json`: **PASS**, **123 cases** (119 major + 4 micro), **1,164,842 assertions**, **5,945 ms**, **60,955 restored fixture writes**. One explicit fixture chunk: **(509663, 119465)**, seed 0. All 119 repeated full-state comparisons passed.
- Loaded configuration digest before/after remains exactly `f3771f9c23fa1b419a350f250721a0942377f72557053b09921ef55bc2730398`.
- Report SHA-256: `AFAA0D4E72F08EA5166E653E0B30F660F4A8B8396083D97AFA157B2A06403111`.
- `final-acceptance-run-a2-20260909.log`: line 4109 records controlled PASS; lines 4111–4112 record **all 7 required GameTests passed in 9.662 seconds**. Line 4172 records `BUILD SUCCESSFUL in 1m 34s`; the invoking process exited 0. These seven are four production tests, controlled placement, trace/depth regression, and native oil—not seven controlled scenarios.
- Combined log SHA-256: `68A1F892942E7E411814486B48BD75470E781762972FFA4066D1624DBAF98916`.

The separate trace suite in the same process passed its direct trace and diamond-ceiling regression checks; its detailed evidence is maintained separately. The final-a2 namespace selection did not run the natural A/B test, and no `final-unexpected-terrain-a2.json` exists. This rerun retains all bounded-scope limitations above; unrelated pack recipe errors remain in the log.

### Failed first combined attempt remains historical

`final-acceptance-run-a1-20260909.log` is **failed overall**, despite individual controlled and oil PASS markers. It selected eight tests because the natural terrain test still explicitly used the production template namespace, and the trace fixture failed. The unintended natural test overwrote historical `terrain-report-a.json`; no intact backup was found in the bounded task-owned search, and the original report was not reconstructed. Corrected `fixed1` A/B reports remain preserved. The dedicated natural-test namespace/empty-template alias and unique defensive report path were corrected before final-a2; the trace fixture was also corrected separately. The final-a1 result is not counted as seven-test acceptance.
