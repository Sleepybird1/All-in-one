# Worldgen planner verification

Independent code/data verification, 2026-09-09. **5,818,795 assertions passed** against the current production `GeologyConfig`, `GeologyPlanner`, and `GeologyMath` Java sources. No world, running game, live pack, recipes, or resource textures were changed by these tests.

## Reproduce

From the project directory:

```powershell
& .\tools\test_geology_planner.ps1 -JavaDirectory 'C:/Program Files/Java/jdk-21/bin'
```

This compiles the production planner/math/config classes with the exact cached Gson 2.10.1 dependency and a **test-only** `FMLPaths` shim. It writes class files under `build/geology-planner-test/classes`, not the mod output. It does not invoke Gradle or boot Minecraft. `GeologyPlannerSelfTest` reads bundled JSON directly and constructs config records; it does not initialize or overwrite the live external config directory.

The final verification used Oracle Java 21 outside the restrictive process sandbox and completed cleanly with exit code zero. Previous sandbox-only javac runs printed an `AccessDeniedException` while closing the Gson ZIP filesystem after class generation; that environment warning is not presented as a successful full mod build. The final clean run did not have it.

## Covered invariants

- **80 invalid override mutations rejected:** zero/excessive final-size cap, quality-adjusted overflow of the cap, negative/nonfinite quality multipliers, invalid quality distributions, nonfinite/negative global and same-family spacing, nonfinite/negative biome/base/depth/rich-pool weights, zero-weight and overflowing rich-pool totals, too-small/large regions, bounded geometric/cave/global/same-family search ranges, inverted/nonfinite depth anchors, invalid micro-frequency values, negative/nonfinite terrain major/cave/indicator multipliers and trace resource weights, and out-of-range surface-trace depth/placer riverbank distance.
- **Strict center spacing:** all accepted pairs in the synthetic 32×32-region fixture meet the 800-block global minimum and their configured same-family minimum. Hematite and Magnetite share the Iron spacing family.
- **Determinism:** forward, reverse, seeded-shuffled, warm-cache, and four-thread concurrent region evaluations produce the same accepted plans, positions, selected families, qualities, sizes, and fractions.
- **Biome exclusions:** exact biome-ID, family, and terrain exclusions are honored. An explicit zero wins over an overlapping positive biome family.
- **Depth:** shallow/mid/deep anchors, both linear interpolation intervals, and endpoint clamping match expectations.
- **Quality:** all four configured probability anchors and 400,000 deterministic rolls pass distribution tolerances. Interpolated distributions remain normalized.
- **Shapes:** exact unique intended volume, deterministic voxel order, and six-neighbor connectedness; Coal is flattened rather than a spherical ore blob.
- **Quota math:** stochastic floor/ceiling behavior, expected-value check, available-host cap, zero-host/zero-fraction behavior, positive minimum guarantees, and configured association chance/depth data.
- **Rich-pool allocation:** 3,348,871 direct production `GeologyMath.split` assertions cover exact conservation, repeated-seed determinism, nonnegative allocations, unchanged input weights, zero-weight exclusion, zero targets, subnormal/large finite weights, targets through `Integer.MAX_VALUE`, rejected negative/nonfinite/empty-positive/overflowing pools, and 600,000 small-pool 70/25/5 distribution samples. The rare last entry retains its expected probability instead of disappearing through separate rounding.
- **Broad phase:** 32 actual generated host/Coal shapes, including 100,000-block shapes at region sizes 128 and 512 and negative regional boundaries. All 956 occupied-chunk cases pass the production `mayReach` predicate and the automatic region search window. No tested real shape chunk was rejected.

The broad-phase search-radius formula and pure micro gate are modeled from the current `GeologyFeature` source; the Minecraft feature itself is not invoked in this standalone test. The tested broad-phase sample is regression evidence, not a proof over every possible world seed.

## Measured results

| Fixture | Result |
|---|---|
| Cold first 3×3 regional decisions | 313 synthetic surface-sampler calls; 12.16 ms Java-only |
| 32×32 regional area | 135 accepted deposits across 268.44 km²; 2,064 sampler calls; 79.14 ms Java-only |
| 22,000-block ordinary host | 42×29×37 block bounds (X×Y×Z) |
| 22,000-block Coal seam | 43×9×125 block bounds |
| 32 broad-phase shapes up to 100,000 blocks | 956 occupied-chunk checks; maximum observed horizontal radius 96 versus conservative configured reach 279; 1,309.37 ms |
| 64×64 chunk broad-phase fixture | 3,033 / 36,864 candidate region/chunk pairs require decisions: about 91.8% rejected before decision lookup; 313 terrain-sampler calls total; 2.05 ms Java-only |
| Pure micro probability model, 1,000,000 candidates | High-rate family 1,539 versus 1,500 expected; low-rate family 65 versus 50 expected; 3,209 candidates need terrain sampling |

The pure micro fixture uses two equally selected eligible families with occurrence chances 0.003 and 0.0001. It confirms that the coarse upper-bound roll plus the selected family's own roll retains the different probabilities. About **99.68%** of fixture candidates skip terrain sampling. It does not measure ore blocks surviving actual-world replacement checks, cave clipping, depth filtering, or biome suitability.

All timings are illustrative measurements on this machine. The sampler is a cheap deterministic biome/terrain fixture, **not Minecraft/Tectonic noise**. In particular, a cold 313-call planning burst still warrants normal-world chunk-time profiling. The broad phase reduces how often cold decisions are needed; it does not make an individual expensive noise query free.

### Small PGM pools

Each row uses 100,000 deterministic seeds and calls the actual production split method with Osmium/Platinum/Iridium weights 70/25/5. Every allocation conserves the exact pool target. The test compares each mean to its mathematical expectation with a 0.006-block absolute tolerance.

| Pool target | Mean Osmium | Mean Platinum | Mean Iridium | Pools containing Iridium |
|---:|---:|---:|---:|---:|
| 1 | 0.70071 | 0.24901 | 0.05028 | 5,028 |
| 2 | 1.39817 | 0.50092 | 0.10091 | 10,091 |
| 3 | 2.09870 | 0.74988 | 0.15142 | 15,142 |
| 5 | 3.50129 | 1.24819 | 0.25052 | 25,052 |
| 10 | 7.00000 | 2.49917 | 0.50083 | 50,083 |
| 19 | 13.29848 | 4.75135 | 0.95017 | 95,017 |

For a target of ten, Iridium is always either zero or one and averages 0.50083 against 0.5 expected. This is allocation verification, not an assertion that actual terrain placement or clustering has passed runtime tests. Cumulative rounding correlates allocations within a pool to preserve its total; it is not independent per-block multinomial sampling.

## Guaranteed association boundary bias

The implementation guarantees at least one positive required associated ore in each nonempty clipped deposit chunk. This preserves the strict Uranium→Thorium guarantee even if all other chunks' planned host was removed by caves or other replacement restrictions, while avoiding cross-chunk writes and generation-order dependence.

It is not an exact global percentage. Across all 256 X/Z chunk offsets of a compact fixture:

| Uranium host size | Fraction | Percentage target | Mean with chunk-local guarantee | Observed range |
|---:|---:|---:|---:|---:|
| 600 | 0.5% | 3 | 3.84 | 2–6 |
| 900 | 0.5% | 4.5 | 5.37 | 3–7 |
| 1,200 | 0.5% | 6 | 6.78 | 5–10 |
| 1,500 | 1% | 15 | 15.62 | 14–18 |
| 2,000 | 1% | 20 | 20.61 | 19–23 |

For intact compact fixture shapes, the observed mean overhead was about 0.6–0.9 associated blocks. Arbitrary extreme clipping can magnify that proportional overhead. A deliberately pathological 1,000-host fixture divided into 40 tiny independent chunks produces a 40-block minimum instead of a five-block percentage target. That is a mathematical boundary-case illustration, not a claim that the compact default Uranium shape occupies 40 chunks.

No fixed preselected anchor guarantees an actually generated associated block under arbitrary clipping: its host may be missing. Reducing this minimum while guaranteeing exactly one over the whole deposit would require global knowledge of surviving host or persisted cross-chunk correction. Both are outside the current strictly chunk-local model.

## Remaining runtime validation

These tests do **not** prove:

- Minecraft feature registration and datapack reload success; use the combined build and isolated runtime tests for that.
- Tectonic/RU terrain behavior, actual chunk-generation latency, or the shape of natural cave exposures.
- Actual host counts after caves, liquids, exterior-cover and replacement-tag checks. There is no structure-bounding-box guard: ordinary structure-placed stone matching a replacement tag is not distinguished from natural stone.
- Actual rich/associated block placement, clusters straddling chunk borders, raw-drop behavior, or economic playtesting.
- Oil field appearance, scanner behavior, or extraction in a loaded world. The oil planner has its separate native-column and finite-oil regression tests.
- Population representativeness from one synthetic biome sampler. Its 135 accepted deposits are not an estimate of actual modded-world density.

Final source review findings concerning nonfinite depth anchors, terrain multipliers, trace resource weights, and overflowing rich-pool totals were addressed by the implementation owner. The clean final test includes their regressions within the 80 passing invalid-override checks.

## Recommended deterministic normal-world checks

Use **fresh disposable normal Overworlds**, with the current Tectonic/RU mod set and the exact same config/data on each comparison. Superflat is unsuitable for these geological checks. Suggested seeds are `246813579`, `7342`, and `-8675309`. They are reproducible test inputs, **not seeds claimed to have known resources or biomes at particular coordinates**.

1. Start with X/Z `-4096..4095` around the origin. Query predicted deposits before generating large areas. Use `/icgeology config`, `/icgeology report`, and `/icgeology locate any 8`. Specific useful queries include `/icgeology locate uranium 8`, `/icgeology locate graphite_rock 8`, and `/icgeology locate coal 8`. An empty local result is expected for rare families; it is not proof of a bug.
2. Expand searches around `(8192, 0)`, `(-8192, 0)`, `(0, 8192)`, and `(0, -8192)` if local biome diversity or rare deposits are insufficient. The command's radius is measured in configured regions, not blocks; at 512-block regions, radius eight covers centers roughly four kilometres from the query position on each axis.
3. In one copy of a seed, approach the same predicted deposit from positive X/Z; in another fresh copy, approach from negative X/Z. Generate the whole formation's intersected chunks. Compare block counts and shapes after all relevant chunks exist, not midway through exploration.
4. Include formations close to chunk edges and negative X/Z multiples of 16 and region boundaries. Include a long Coal seam and a high-quality large host. Compare six-neighbor continuity and absence of truncated chunk faces.
5. Inspect lowlands, caves, mountain cliffs, and deep ocean terrain. Useful biome targets already present in the family definitions include `minecraft:desert`, `minecraft:deep_ocean`, `minecraft:jagged_peaks`, `regions_unexplored:ashen_woodland`, and `regions_unexplored:highland_fields`. Confirm only small deliberate indicators expose exterior hosts and cave intersections remain discoverable.
6. Test positive Uranium→Thorium guarantees after actual clipping, optional Thorium→Uranium and Pentlandite→Cobalt rolls, and the prohibition of Graphite-associated Diamonds above Y-20. `/icgeology simulate <family>` reports configuration expectations without placing blocks; observed counts in reports are limited to the current session's generated chunks.
7. Profile both the first cold region encountered and sustained exploration. Record chunk-time percentiles, not only average Java planner times. Do not mass-load a large area solely to satisfy this checklist.

No normal-world coordinates, biome outcomes, ore sightings, or runtime pass results are asserted by this report.
