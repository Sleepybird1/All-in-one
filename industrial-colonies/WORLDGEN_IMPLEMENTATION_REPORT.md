# Industrial Colonies — Overworld geology implementation

Authoritative design: the pasted resource-generation framework, SHA-256 `FFC253169D41B8B1439877D61597E6770B3F68F57ED33DC7A774CC490C8B4A68`.

Target: Minecraft 1.21.1 / NeoForge 21.1.248, existing Industrial Colonies 0.4.0 project. Implementation date: September 8–9, 2026.

## Delivery and verification status

The configurable foundation is implemented in the source project. **Overall task status: 100%; requested foundation complete, acceptance passed and handoff hashes reconciled.** Build/planner/data audits, corrected fresh Tectonic/RU terrain A/B tests, all-profile/all-quality controlled placement, starter traces/diamond depth, native TFMG oil compatibility and actual client rendering now pass. The final JAR passed all seven required combined tests. The earlier full client test restored all 239 staged JARs, rendered all 40 approved cubes plus placer, and retained the original Bertrandite texture; the final JAR's assets/rendering components are byte-identical. Server tests use the documented 233-JAR subset with six recoverable exclusions. Exact candidate identities, evidence and limits are in `WORLDGEN_FINAL_ACCEPTANCE.md`. These tests do not claim an exhaustive biome/seed census, shader playthrough, or final recovery-economy balance.

**No live modpack JAR, live configuration, existing save, or generated player chunk was changed.** Isolated testing uses physical workspace copies, not links to live files. No production deployment or retrogen is included.

No Create/Encased redesign, machine progression, tool recipe, quest, final processing/casting recipe, or new unapproved mineral has been added. Existing finished-material compatibility remains registered. The approved block textures are exported byte-for-byte from the V27 Blockbench file; that source file is unchanged.

## 1. Architecture and generation order

`GeologyBootstrap` connects the existing mod entrypoint to the new block registries, feature registries, operator diagnostics and server-stop cache cleanup. `GeologyConfig` copies missing bundled defaults to the external config directory, validates overrides and loads them once per process. Restart after changes; there is deliberately no live worldgen-reload command that could split an already generating formation between rule sets.

`GeologyPlanner` is pure deterministic regional planning. It does not look for deposits in loaded/saved chunks:

1. Hash the world seed and 512-block region coordinates to a candidate position and attempt roll.
2. Apply global opportunity/terrain checks and the 800-block global minimum using seeded, order-independent regional priorities.
3. Build a biome/depth-compatible pool. Each spacing family has its own independent regional reservation priority; this excludes conflicting same-family candidates before a rock is selected. Hematite and Magnetite share the Iron spacing family.
4. Select the rock from that eligible pool using its base, biome and depth weights.
5. Evaluate suitability for the selected rock; only then roll Poor/Normal/Rich/Exceptional.
6. Roll the normal size range, apply the quality multiplier, and create a connected irregular voxel formation.
7. `GeologyCarversMixin` invokes `GeologyFeature.generateDeposits` after the owning normal-noise chunk's AIR carving and before neighboring FEATURES can run. Only tagged stone/deepslate in the owning chunk is replaced; existing carved air, fluids and bedrock are preserved. Upgrade chunks are skipped. Exterior cover uses cached immutable noise heights, not premature neighboring heightmaps. Later third-party structure/features can still overwrite blocks and require broader acceptance tests.
8. Count the host blocks actually placed in that chunk. Calculate rich-block targets from that count and the adjusted fraction, then place connected small clusters inside the host. Rich veins are count-driven, not a fixed number of veins.
9. Apply generic percentage/depth-percentage associated-ore rules. Independent micro, trace, placer and oil systems run separately.

Global thinning and independent family reservations are conservative: a site reserved for a family can ultimately select another eligible material, leaving the first family's reservation unused. This guarantees spacing without chunk-order dependence, but means configured attempt probability is not final deposit density. Unrelated families do not share the same-family reservation; Iron's 1500-block family rule is not incorrectly applied to Silver.

`GeologyMath.shape` grows a connected frontier using an irregular ellipsoidal distance field. Its intended volume is exact. Coal uses a flattened, elongated seam. Caves, the build-height limit, non-replaceable blocks and exterior cover reduce the number actually placed; those clipped volumes are not secretly filled with extra rich ore.

## 2. Complete change inventory

See `WORLDGEN_CHANGE_MANIFEST.md` and `WORLDGEN_CHANGE_MANIFEST.json` for every authored/modified file and hashes. `WORLDGEN_GEOLOGY_ASSETS.json` additionally maps all exported textures/models to their approved V27 face references and hashes.

Principal code is under `src/main/java/dev/godpc/industrialcolonies/geology/`, with separate oil implementation in `geology/oil/`. Six narrow geology mixins/accessors provide suppression and the post-carver placement barrier. Major/micro deposits and limited indicators run there; traces/placer remain in the existing decoration feature. The entrypoint, mixin list and language file have original backups, and the pre-regression source/JAR snapshot is retained separately. Existing oil-only validation/docs were updated to the authoritative rules; extraction and processing were not redesigned.

Generated Gradle caches/build intermediates and the isolated test copy are not source changes. They are identified separately from the authored-file inventory.

## 3–5. Configuration locations and exact biome assignments

Bundled defaults:

| File under `src/main/resources/data/industrial_colonies/geology/` | Responsibility |
| --- | --- |
| `settings.json` | Shared spacing, quality, depth anchors, terrain exposure, geometry bounds, trace/placer/micro controls and economy metadata |
| `biome_families.json` | Exact IDs in the eleven reusable geology families |
| `deposit_families.json` | 24 approved deposit definitions, rich pools and associations |
| `oil.json` | Separate native-compatible basin/offshore field rules |

External editable copies are created at **`config/industrial_colonies/worldgen/`**, relative to the Minecraft instance or isolated test directory. Existing files are never silently overwritten by a mod update. To adopt newer defaults, compare the bundled JSON and merge deliberately, or back up and remove only the external file whose defaults you want regenerated. Restart Minecraft/server afterward. Already generated chunks do not change.

`WORLDGEN_BIOME_ASSIGNMENTS.md` contains the **full exact ID lists for every family**, with 50 vanilla surface-biome IDs and 70 RU IDs verified against the installed JARs. Thirteen RU compatibility/removed-from-normal-selection IDs are explicitly marked. Cave-only biomes inherit the sampled surface-column classification rather than receiving invented surface geology. Other mods' unclassified surface biomes use compatible weight 1 for minerals; oil fails closed until assigned. No `tectonic:*` biome IDs were invented.

## 6–16. How to change the rules

All percentages in JSON are fractions: `0.08` means 8%, not 0.08%.

| Change | Edit |
| --- | --- |
| Biome membership | Arrays in `biome_families.json`; IDs can belong to multiple families |
| A rock's biome preference | Its `biomeWeights` in `deposit_families.json` |
| Overall material selection | Its `baseWeight`; these starting values are explicitly provisional |
| Depth preference | Its three `depthWeights`, ordered shallow/mid/deep |
| Depth interpolation/center limits | `settings.depth`; default anchors 42 / 0 / -44, center bounds -60..64 |
| Global spacing | `settings.globalMinSpacing`, default 800 |
| Same-family spacing | `sameFamilyMinSpacing`; `spacingFamily` joins both Iron hosts |
| Deposit size | `normalSizeMin`, `normalSizeMax`, and `settings.quality.sizeMultipliers` |
| Quality probabilities | `settings.quality.base`, `poor`, `good`, `ideal`; each must sum to 1 |
| Normal rich percentage | `normalRichOrePercent`; actual approved `richOres` pool required |
| Quality richness | `settings.quality.richMultipliers` |
| PGM proportions | Ultramafic `richOres[].weight`: 0.70 Osmium / 0.25 Platinum / 0.05 Iridium |
| Associated ores | `associated`: type, block, quality ranges/chances, depth bands and cluster limits |
| Micro frequency | Per-deposit `micro.chance`; global `settings.micro.frequencyMultiplier` and `maxChancePerChunk` |
| Micro size | Per-deposit `micro.min`, `max`, optional jackpot controls; global `maxBlocks` safety cap |
| Independent lucky diamonds | `settings.micro.diamond` (including maximum Y -20) |
| Trace supply | `settings.trace`: attempts, per-attempt chance, patch sizes, material weights and surface depth |
| River flakes | `settings.placer`: river IDs, favorable families, bank distance, attempts/chance/counts |
| Mountain/cave exposure | `settings.terrain`, `terrainThresholds`, `geometry.caveSearchRange` and `exteriorCover` |
| Limited surface clues | `settings.indicators`; only existing approved low-yield host blocks are used |
| Oil | `oil.json`: family weights, absolute vetoes, regional chance/size/wells and native-compatible height |

Mineral overlap blending uses the arithmetic mean of explicitly matched positive weights. An explicit zero or hard exclusion vetoes the rock before selection. If no configured weight matches, mineral weight is 1. Missing weights are not silently summed into a multi-family advantage. Oil instead uses the strongest applicable positive weight, after its absolute vetoes.

Depth weighting is smoothly interpolated through the three anchors. Suitability averages the selected rock's biome and depth weights. Quality probabilities interpolate between poor/base/good/ideal distributions rather than abruptly changing at a biome boundary. The approved probability arrays and multipliers are retained exactly.

Micro generation chooses an eligible material using base × biome × depth weights, then applies that material's real chance, scaled/capped by the global controls. A cheap maximum-rate check avoids terrain sampling on almost every empty chunk. Diamonds have their separate rare roll and depth/graphite suitability. No independent Cobalt, Osmium, Platinum, Iridium or Redstone micro system was added.

PGM rich-pool allocation uses seeded randomized cumulative rounding. Every chunk's allocated Osmium + Platinum + Iridium count equals its rich target, while small pools retain the expected 70/25/5 proportions over seeds. Ordinary independent rounding with Iridium receiving the leftover would bias the rarest material downward; that approach was removed and directly regression-tested.

The provisional trace baseline is four attempts per chunk at 0.35 chance, with patches of one to three blocks and Iron/Copper/Coal weights 3/3/4. This proposes an average 2.8 blocks per chunk before terrain clipping (approximately 0.84 Iron, 0.84 Copper, 1.12 Coal). It is a configurable starting supply, not a claim of measured ingot recovery or a completed early-game playtest.

`enabled=false` disables the new custom geology/oil generation, **not the pack's entire ore-suppression policy**. `suppressDefaultOres=false` disables the Java bypass guards only. The removal biome modifier, mineral-free stratum replacements and RU surface override are unconditional datapack policy. These flags do not restore old scattered ore generation; restoration requires a deliberate data change. This prevents an accidental generator toggle from silently defeating the authoritative economy.

## Approved roster and resource ownership

Registered: **20 low-yield rocks, 16 rich ores, 4 associated/special ore blocks**, plus a small placer Gold Flakes block and Gold Flake item. One resource creative tab groups them. Coal and Gold retain Minecraft's registered blocks and appearance; the discarded dark-Lead block was not added as a second host.

| Low-yield host | Rich variant(s) / association | Produces |
| --- | --- | --- |
| Sphalerite | Rich Sphalerite | Zinc |
| Chalcopyrite | Rich Copper Ore | Copper |
| Hematite | Rich Hematite | Iron |
| Magnetite | Rich Magnetite | Iron |
| Bauxite | Rich Bauxite | Aluminum |
| Cinnabar | No rich block; no generated Sulfur/Mercury association | Redstone; later Sulfur/Mercury processing |
| Spodumene Rock | Spodumene Ore | Lithium |
| Argentite | Rich Silver Ore | Silver |
| Wolframite Rock | Rich Wolframite Ore | Tungsten |
| Pentlandite | Rich Nickel Ore; rare Cobalt Ore | Nickel / Cobalt association |
| Galena | Rich Galena Ore | Lead |
| Dolomite | No rich block | Magnesium |
| Graphite Rock | No rich block; deep Diamond association | Carbon/Graphite; unrelated to Coal |
| Phosphate Rock | No rich block | Phosphorus |
| Ultramafic Rock | Rich Osmium, Platinum and Iridium ores | PGM pool, Osmium primary |
| Ilmenite | Rich Ilmenite Ore | Titanium |
| Bertrandite | No rich block | Beryllium |
| Borax Rock | No rich block | Boron |
| Cassiterite | Rich Tin Ore | Tin |
| Chromite | Rich Chromium Ore | Chromium |

Uraninite and Thorium Ore are recognizable standalone special formations, not invented extra hosts. Every nonempty generated Uranium formation fragment guarantees some Thorium. Thorium's Uranium presence is rolled once per deposit at the approved 5/10/20/35% quality chances. Pentlandite uses the approved Cobalt range by quality. Graphite's diamond rules use actual block height; none occur above -20. At ambiguous band boundaries, -40 belongs to the -20..-40 band and -55 to the -41..-55 band; below -55 is the deepest band.

Low-yield rocks have dedicated `industrial_colonies:geological_rocks` and material identity tags, not broad `c:ores` membership. This avoids automatically opening unrelated “one ore in, one ingot out” compatibility recipes. Geological blocks generally drop themselves; the diamond variant retains a diamond drop, and placer flakes drop the flake item. No final metal recovery output is assigned through block loot.

## 17–20. Default generator audit and compatibility

`WORLDGEN_SUPPRESSION_AUDIT.md` lists **all 68 suppressed placed-feature IDs**, installed mod versions, source/config evidence and exceptions. `#industrial_colonies:geology/default_ore_features` is shared by the biome remover and runtime direct-placement guard.

Covered: vanilla scattered Iron/Copper/Redstone/Diamond/Coal/Gold; Create Zinc and metal-bearing striations; TFMG Lead/Nickel/Lithium/mixed metal strata; Mekanism Tin/Osmium/Uranium/Lead including retrogen variants; all eleven NuclearCraft ore placements; IE's physical ores and virtual excavator mineral veins; Overworld Cosmonautics Titanium and Stellaris Steel; conflicting RU redstone growths. Existing Allthemodium/Yellorite suppression remains part of the audited policy.

Bypasses handled separately:

- Vanilla giant Iron/Copper **noise veins**, including their raw blocks: a dimension-scoped hook switches off only the ore-vein flag when building an Overworld noise chunk. Tectonic's terrain router, aquifers, surface rules and biome source are not replaced.
- Fossils: retain bones, skip the Coal/Diamond overlay template.
- Quark fairy rings: retain flowers and possible Emerald, reject only Diamond writes.
- RU redstone cave surface rules: retain the original biome/noise conditions, replace only raw Redstone output with stone/deepslate.
- IE/Mekanism direct placement and retrogen: the runtime placed-feature guard catches the same forbidden IDs even when biome lists are bypassed.
- Create/TFMG mixed rock strata: retain source geometry, placement rates and non-resource decoration/fireclay; replace metal-bearing layer outputs with their native stone/deepslate target.

Retained: Emerald, Lapis, Fluorite, Salt, existing Nether/pack Quartz, Nether/planet-specific ore systems, decorative rocks/geodes, AE2 meteor/budding Certus and unrelated magic resources such as Iron's Spellbooks Mithril. No registry blocks were removed. Loot, trades, recipes, saved virtual reserves and already generated ores were not deleted.

Biome modifiers target `#minecraft:is_overworld`; Java guards also check the actual dimension. A custom dimension deliberately reusing an Overworld biome object can share that object's modified feature list. No installed planet-specific biome was found in the Overworld tag; normal-world and planet regression checks remain part of playtesting.

## Separate oil result

See `OIL_WORLDGEN_FRAMEWORK.md`. Deterministic basin/offshore fields reuse TFMG's native, scanner-compatible well builder one chunk-owned column at a time. They do not call its unsafe long random-walk whole-field placement method.

Desert/badlands/outback/ocean weights are 2.5; plains/sedimentary 1.25; lowland forest/wetland 0.5. Mountain/highland/volcanic/ashen/cold-high-altitude categories always veto even if another category is favorable. Height and local-relief checks also veto Tectonic highlands occupying a plains biome. Native well footprints are checked individually. No petroleum recipe, pressure, extraction-rate or reserve-volume rebalance was introduced.

## 21. Deliberate limits and not-yet-verified requirements

1. **Actual-host richness is calculated per generated chunk**, with deterministic stochastic integer rounding. It is not one synchronized global count over unloaded chunks. Expected fractions follow the whole-formation target without forcing future chunks to load; small rounding differences across borders are disclosed.
2. An absolute “some associated ore survives” guarantee under arbitrary cave clipping requires at least one in every surviving fragment when using strictly local deterministic writes. This introduces a boundary floor for Uranium→Thorium and successful guaranteed Cobalt/Uranium rules. Tests on intact compact Uranium shapes measured roughly 0.6–0.9 extra associated blocks on average; heavily clipped slivers can have a larger proportional difference. No claim of an exact deposit-wide percentage is made.
3. Intended connected volume is exact; actual placed volume can be smaller. Caves, exterior cover, bedrock and non-replaceable terrain are never filled merely to satisfy the size number.
4. Cave-exposure multipliers control a deterministic bias toward nearby noise-column cave floors, not a guaranteed measured 2.5× amount of visible surface area. Limited host indicators and exterior cover keep mountain exteriors from becoming giant exposed ore walls. Real Tectonic/RU inspection is needed to calibrate those visual rates.
5. **Several-ingot starter supply and mine lifetime outputs are not yet economically verified.** Trace patches and river flakes exist and rates are configurable, but recoverable mB for low-yield/rich rocks and future recovery efficiency are deliberately unassigned. No forbidden processing/tool recipe was invented to manufacture a numerical pass. The universal 1000 mB ingot / 9000 mB block standard and approved provisional forms/lifetime targets are stored as metadata; existing processing recipes are not globally rewritten in this phase.
6. Prospecting gameplay/UI is not implemented. Operator diagnostics predict deposits for development; they are not exposed as normal-player prospecting.
7. No live retrogen, save migration, loot/trade cleanup, ore radiation behavior redesign, or final cross-mod material unification was attempted.
8. Approved Bertrandite remains the exact **1254×1254** reference PNG from V27; the other 41 texture files are 16×16. No resampling/art change was silently applied. Client atlas/render cost for that non-power-of-two reference needs an explicit texture follow-up; headless PNG decoding is not a GPU render test.
9. The two corrected normal-terrain tests cover three formations at seed 0, including actual RU biomes. They are not an all-family/quality/distribution or playthrough acceptance run. GameTest disables structures. The new barrier applies to normal `NoiseBasedChunkGenerator` terrain, not flat or arbitrary custom generators; no fallback restoring scattered default ores was added.

## 22. Performance and safeguards

Regional hashes and bounded caches replace searches through saved chunks. Shape generation is pure geometry; world writes are clipped to one current chunk. A cheap X/Z reach test skips irrelevant regional planning, and rare micro rolls reject before costly terrain queries. Empty cave/bedrock locations do not trigger cross-chunk correction writes.

Default maximum intended formation is 22,000 blocks (Exceptional Coal), well below the default 50,000-block safety ceiling. Configured final volume is checked before allocation, with an absolute 100,000-block implementation ceiling. Search reach expands conservatively from the configured volume limit. Global spacing is limited to 16 regional cells, same-family spacing to 32 cells; raise region size with extremely large spacing rather than creating unbounded loops. Invalid nonfinite values and unsafe overrides fail with an explanatory error instead of silently reverting to default ores.

Tests measured 313 sampler calls for a cold 3×3 decision window before broad-phase pruning, and 2064 calls over a 32×32 regional test grid. Those are call counts, **not Minecraft/Tectonic timing claims**. Corrected normal-terrain checks subsequently completed their bounded work in 13.564/9.183 seconds; complete mod launches took 294/222 seconds. Cold regional terrain sampling remains worth profiling during later large-scale playtests, rather than treating this small sample as a universal benchmark. Caches are bounded and cleared when the server stops. Developer locate work runs asynchronously and never force-loads chunks.

## 23. Developer testing

Use a **new disposable world**, not a valuable save, for normal-terrain acceptance. Keep the original live mod/config backups before any later deployment. Changing config only affects newly generated chunks; existing edges cannot be made consistent by pretending they were regenerated.

OP level 4 commands:

```text
/icgeology config
/icgeology report
/icgeology locate any 4
/icgeology locate hematite 8
/icgeology simulate ultramafic_rock
```

`report` explains the current regional candidate or its rejection. `locate <deposit_id|any> <1..8 regions>` predicts the nearest accepted candidate in the bounded search area; it does not teleport or generate the area. `simulate` prints all four quality size/fraction ranges and association rules without placing blocks. Observed counts cover only chunks generated during the current server session and may be partial; they are not a persisted total over a mined or unloaded deposit.

Enable `settings.debug` for mineral acceptance/rejection and per-chunk actual/rich/association roll logs. Enable `oil.debug_logging` for independent reservoir diagnostics. Normal players receive neither command access nor unsolicited geology information.

Automated checks:

- `tools/test_geology_planner.ps1`: actual Java planner/math/config, deterministic and concurrent traversal, spacing, depth/quality, volume/connectedness and quota checks.
- `tools/validate_geology_integration.ps1 -AllowReferenceTextures`: registration/data/assets/mixin inventory, with explicit Bertrandite exception.
- `tools/audit_geology_worldgen.py --validate-project .`: installed-JAR feature/surface audit and preservation of non-resource strata.
- `tools/validate_oil_worldgen_framework.ps1`: oil data, veto and chunk-ownership contracts.
- `tools/java/.../OilFieldPlannerTest.java`: oil planner determinism/footprints, 10,000 regional cases.
- `tools/validate_regional_finite_oil_fields.py` and its seven mutation tests: native finite reservoir compatibility and authoritative biome rules.
- `GeologyGameTests`: registered blocks/tags, decoded config/features, mixin target/accessor application, loot/placer behavior and packaged texture/model decoding. See `WORLDGEN_ISOLATED_RUNTIME_SMOKE.md` for the isolated GameTest preparation/run procedure.

Normal-terrain acceptance should inspect deposit spacing/family identity, all four qualities, host/rich counts across chunk borders, uranium/thorium and graphite depth rules, tiny lucky ores, starter trace availability, river flakes, native oil scanners in offshore/basin areas, absolute mountain/volcanic oil vetoes, retained fireclay/fossils/emerald/lapis/fluorite/salt, and unchanged Nether/planet terrain. Repeat traversal in a second world with the same seed to verify border consistency. Do not interpret lack of a rare PGM find in a small search as proof its family is broken.

### Test-result record

Local Gradle `build`: PASS (Java 21 / NeoForge 21.1.248). The existing project's `test` task has no JUnit sources; it is **not** counted as the geology acceptance suite.

Final candidate: `industrial_colonies-0.4.0.jar`, 1,695,276 bytes, SHA-256 **`5A4CCD0BA37629225EE88996281FCA7F1A1B704E9E1EE5DC712ECB363EEFFFBA`**. Build, both isolated stages and delivery copies have the same hash. The last correction prevents independent diamond neighbors above configured Y=-20. Every ZIP entry except `GeologyFeature.class` remains byte-identical to the preserved 1,695,174-byte candidate (`ABC9A4D5…DBD56546`) that passed natural-terrain A/B and full-client rendering. Those tests remain explicitly attributed to the earlier hash; the combined final-candidate placement/trace/oil regression is recorded in `WORLDGEN_FINAL_ACCEPTANCE.md`. It is not blanket certification of every unrelated pack feature or final survival economy. Both earlier candidates remain in the dated terrain-order and diamond-boundary backup folders.

| Check | Actual result |
| --- | --- |
| Java 21 / Gradle / NeoForge build | PASS; final diamond-boundary build completed in 18 seconds |
| Actual Java planner/config/math suite | PASS: 5,818,795 assertions, 80 invalid-config mutations, deterministic/concurrent spacing, depth, quality, connected volume and bounded search checks |
| Small rich-pool regression | PASS: 600,000 samples; 100,000 size-10 pools averaged 7.00000 Osmium / 2.49917 Platinum / 0.50083 Iridium, with exact pool conservation |
| Registration/data/approved-asset integration audit | PASS: 1,126 assertions, including the bounded-diamond callsite/ceiling, six required hooks/accessors and the original Bertrandite reference-size exception |
| Installed worldgen suppression audit | PASS: 68 resolved forbidden feature IDs, zero audit errors; six Create/four TFMG stratum patterns retained, eight economic state substitutions in each source |
| Separate pure oil planner | PASS: 509,179 assertions over 10,000 regions, deterministic footprints and absolute forbidden-biome vetoes |
| Oil framework and native finite-reservoir validators | PASS, plus seven Python mutation tests |
| Full-pack GameTest smoke | **STARTUP FAILED in Sodium graphics bootstrap after user-approved launch; 0/4 GameTests executed** |
| Historical client-rendering subset GameTest smoke | **SERVER STARTUP FAILED in Distant Horizons' dedicated-server cast; 0/4 GameTests executed.** Five rendering JARs excluded; 234 JARs were active at that attempt |
| Separately approved Distant Horizons exclusion, before fixture | Historical failure: Rocketnautics required the missing deep-space dimension; exit 1 in 52 seconds, 0/4 tests |
| 233-JAR subset plus existing deep-space test fixture | **PASS: all 4 required tests, all five `GEOLOGY_SMOKE` markers, staged candidate source confirmed, clean shutdown and process exit 0.** Tests 674.4 ms; Gradle 63 seconds |
| Original normal-terrain A/B regression | Both internal 5/5 suites passed, but cross-run Galena equality FAILED: 35 extra host positions and two extra rich blocks under reverse order. Preserved evidence led to the post-carver fix |
| Corrected normal Tectonic/RU terrain A/B regression | **PASS:** both 5/5 suites, 14 target chunks per fresh world, three natural families, actual RU biome evidence, exact reversed requests and identical complete sampled shape states/counts. Terrain tests 13.564 / 9.183 seconds; whole launches 294 / 222 seconds |
| All profiles/qualities and associated placement | **PASS:** 119 repeated major fixtures + 4 micro fixtures; 1,164,832 assertions, unchanged config, exact repeat states; controlled rather than natural occurrence |
| Native TFMG oil compatibility | **PASS:** 8,253 assertions; native regional placement/scanner/pump, 1000 mB debit, exhaustion and primary-well NBT roundtrip |
| Full 239-JAR client model/atlas/GPU render | **PASS:** 40 approved cubes + placer, 120 frames, inspected native screenshot; all 239 JAR hashes unchanged; normal exit 0 |
| Exact final-candidate combined regression | **PASS:** all seven required tests in 9.662 seconds; 94-second full launch, exit 0. Controlled 123 cases/1,164,842 assertions; traces/diamond ten cases/80,922 assertions, zero above-ceiling writes in 128 calls; native oil 8,253 assertions. Fresh world and unchanged config |
| Exhaustive distribution / recovery-economy playthrough | Not claimed; bounded acceptance is documented separately, and final processing yields are deliberately outside this phase |

The pure suites execute production planner/math/config code; large assertion totals include statistical loops and are not a substitute for Minecraft world-generation coverage. The additional runtime trace/micro fixtures invoke actual placement on deliberately prepared blocks. Neither these fixtures nor pure probability checks prove natural starter availability or final recoverable-ingot income.

Isolated runtime preparation initially contained physical copies of 238 installed mods plus this candidate, no live saves, no account files and no links to mutable live configuration. The first rendering subset had 234 active JARs; the successful configuration has 233 active JARs and six recoverable excluded JARs. Already-cached assets (with the historical asset-index mismatch disclosed in the smoke report), native Netty libraries and the exact NeoForge userdev run configuration were used. The only missing launcher dependency, official `net.neoforged:DevLaunch:1.0.2`, was acquired separately with permission from NeoForge's Maven repository and verified against its published SHA-256 checksums. Initial execution attempts were network-sandboxed. Later user-approved runs were outside the sandbox with broader filesystem/network access disclosed in advance; Gradle still used `--offline`. No claim is made that third-party outbound traffic was technically blocked during those approved attempts.

Initially, Windows denied access to the legacy classpath JARs and the first escalation request was rejected. The user subsequently answered "Run them" to the explicit approval question. That approved isolated attempt ran on September 9, 2026 at 01:09 Eastern, exited 1 (Gradle reported 10 seconds), and is captured in `isolated-runtime/geology-gametest-20260909-001051-895/approved-run-20260909.log`. The prior access error was absent. Sodium 0.8.13's early graphics service called its LWJGL check before FML's client/server side check and failed on missing `org.lwjgl.Version` (log line 822). Disabling the splash screen would not prevent that service call. At that historical stage no graphics check was disabled, no substitute library was added, and no mod had been removed from the staged pack.

The user then approved client-only rendering exclusions with "Continue". Sodium/Iris were moved first; the next run exposed Entity Texture Features loading a client screen. ETF and its required rendering companion EMF were moved next; the following run exposed shader-only Euphoria Patcher loading `ClientLevel`. That run misleadingly returned process 0 / Gradle success while Minecraft startup failed, so it is explicitly not counted as a pass. After Euphoria Patcher was moved, `server-render-exclusion-run3-20260909.log` reached the server thread but exited 1 in 59 seconds on Distant Horizons' cast (lines 3898–3900). No `GEOLOGY_SMOKE` marker was emitted. Excluded files, hashes and restoration instructions are recorded in the stage's `rendering-exclusions.json`; no JAR was deleted or patched.

That historical run loaded far more of the pack but was **not evidence of a four-test geology pass**. A read-only audit found 34 distinct recipe parsing failures (26 Create Metallurgy casting recipes and eight older Industrial Colonies recipes). All 46 staged server scripts, six AlmostUnified configs, the Create Metallurgy JAR and the relevant `base_filling` schema match their live counterparts byte-for-byte; none are recipe edits in this task's change inventory. These unchanged pack inputs need a separate recipe-integration investigation, not silent removal or repair during worldgen work. No new geology-owned resource/registry/mixin load error was identified before that crash. The later smoke pass does not certify unrelated recipe integration.

The user separately approved temporarily excluding Distant Horizons with "Continue going". Its exact JAR is retained under `excluded-gametest-incompatible-mods`, with SHA-256 and restoration instructions in `gametest-exclusions.json`. Run 4 then reached the first server tick but Rocketnautics dereferenced its absent `deep_space` level. Cached `GameTestServer.create` builds the flat preset against an empty dimension registry, omitting standalone mod dimensions; no Rocketnautics mod was removed or patched.

The stage-local `worlds/geology-smoke-world/datapacks/ic-gametest-dimensions` fixture preserves all three vanilla flat-preset dimension objects and adds the exact existing `rocketnautics:deep_space` LevelStem object from the installed Cosmonautics JAR (empty flat void). Semantic equality to all four source objects was checked. This is test harness data only, recorded in `gametest-dimension-fixture.json`; no production generator, geological resource, candidate asset or live save was changed.

Historical run 5 (`server-dimension-fixture-run5-20260909.log`) passed four tests in 674.4 ms, with all five smoke markers, the staged candidate identified, shutdown and exit 0. The later normal-terrain regression and correction supersede that candidate's acceptance record. See `WORLDGEN_TERRAIN_ORDER_REGRESSION.md` for the original failure and corrected fresh-world evidence; `tools/terrain-smoke/README.md` documents the test-only source set and fixture. No stage EULA file exists.

Corrected identical results in each world: Chalcopyrite 2,957 actual positions (2,874 rock + 83 rich), Galena 1,467 (1,380 + 87), Sphalerite 1,210 (1,181 + 29). The Galena shape retains 569 terrain-clipped positions; they were not filled to force its 2,036 intended volume. Every per-chunk rich quota reconciles. All asset and worldgen-data JAR entries are unchanged from the previous candidate; only three class entries and mixin registration differ. A Spark shutdown sampler warning in corrected run A is recorded separately, not hidden as a perfectly clean pack log.

`WORLDGEN_ISOLATED_RUNTIME_SMOKE.md` records the exact procedure, dependency provenance and historical/current evidence. `preparation.json` retains the original initial-stage hash; the candidate hash above identifies the final diamond-corrected build, not the earlier historical runs. The unchanged-component and single-class diff audit is `tools/controlled-geology/FINAL_CANDIDATE_AUDIT.md`.

Normal-terrain, full-client component acceptance and exact final-candidate runtime regression have now succeeded for their documented scopes. The first combined run failed due to a non-repeatable test fixture and included an unintended eighth test that overwrote an early generated A-report; the complete provenance/correction is disclosed in `WORLDGEN_FINAL_ACCEPTANCE.md`. The passing retry selected seven tests with guarded fresh outputs. Deployment into the live pack has not been performed; retain backups and use a fresh disposable world for any subsequent integration/progression playtest. Final processing values and recipes remain deliberately outside this phase.

Technical reference: NeoForge's official [1.21.1 biome modifier documentation](https://docs.neoforged.net/docs/1.21.1/worldgen/biomemodifier/), plus the cached mapped Minecraft/NeoForge source and installed mod JARs inspected locally. The user specification—not an external geology reference—governs resource names, associations and numeric defaults.
