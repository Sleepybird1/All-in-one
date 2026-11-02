# Industrial Colonies — final foundation acceptance

Overall task status: **100% — requested Overworld resource-generation foundation completed and verified**.

This report covers the requested Overworld resource-generation foundation, not final recovery recipes, tools, quests, survival progression, or live deployment. Those remain deliberately outside this phase. A completed foundation is not a claim that every unrelated mod or legacy recipe in the pack is error-free.

## Candidate identity

`industrial_colonies-0.4.0.jar`, Minecraft 1.21.1 / NeoForge 21.1.248, 1,695,276 bytes.

SHA-256: `5A4CCD0BA37629225EE88996281FCA7F1A1B704E9E1EE5DC712ECB363EEFFFBA`.

The candidate contains the tested post-carver order correction and final diamond-depth boundary fix. A tiny diamond cluster centered at Y=-20 could previously place its upper neighbor at Y=-19. The bounded placement overload now rejects every candidate above the configured ceiling; other tiny resources retain their existing behavior. Development-only acceptance addons are separate source sets and are never packaged into this JAR. The original approved texture source and live modpack/saves are unchanged.

The earlier natural A/B and GPU evidence used the preserved 1,695,174-byte candidate, SHA-256 `ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546`. Comparing every ZIP file entry shows exactly one changed entry, `GeologyFeature.class`, no additions/removals, and byte-identical assets, data, models, textures and all other classes. Natural A/B major-placement evidence and client asset-render evidence therefore remain component-applicable; they are not falsely relabeled as launches of the final hash. The combined fresh-world suite below exercises actual placement and native oil on the final JAR. See `tools/controlled-geology/FINAL_CANDIDATE_AUDIT.md`.

## Evidence and scope

| Check | Result | What it proves |
| --- | --- | --- |
| Build, production planner and static integration | PASS | Java build; 5,818,795 geology assertions; 1,126 integration assertions including diamond callsite/ceiling contracts; 68 resolved suppressed features; separate 509,179 oil-planner assertions and finite-oil validators |
| Fresh normal Tectonic/RU worlds, reversed chunk requests | PASS | Three natural formations, 14 requested chunks/world, exact state/count equality; preserved clipping; all five tests in each world |
| Every profile/quality and associated-resource placement | PASS | Final JAR: 24 profiles × 4 qualities, 119 major cases repeated identically plus 4 micro cases; 1,164,842 assertions in 5.945 seconds |
| Native TFMG oil integration | PASS | Final JAR: 8,253 assertions in 627 ms; actual regional feature, native marker/scanner/pump, 1000 mB extraction, finite debit, exhaustion stop and primary-well NBT roundtrip |
| Direct starter-trace placement and diamond ceiling | PASS | Final JAR: ten controlled cases, 80,922 assertions; exact repeated inputs/outputs, protected materials, twelve-block trace budget; 128 bounded diamond calls, zero above Y=-20 |
| Exact final JAR, combined fresh-world acceptance | PASS | All seven required tests passed in 9.662 seconds; 94-second full launch, normal shutdown and process exit 0 |
| Full client actual model/atlas/GPU render | PASS | All 239 staged JARs; 40 approved cubes + placer; valid baked models and stitched sprites; actual 1280×720 GPU screenshot after 120 frames |
| Final handoff/hash inventory | PASS | 485 source/backup/delivery/control/evidence records verified; all four candidate copies match; all four delivered JSON defaults match source |

## Runtime boundaries and earlier failed attempts

The server stage has 233 active JARs, with five rendering-only JARs and Distant Horizons preserved separately under explicit earlier approvals. The client stage restores all six into a new physical copy, for 239 total JARs. Neither stage contains copied account files or live saves. The user explicitly approved the full client outside the sandbox after disclosure of broader filesystem access and possible normal mod outbound requests. Gradle remains offline; that does not prevent third-party mods from contacting their update services.

The first full-client launch failed before asset acceptance: Connector's development loader required `connector.clean.path`. The supported property now points to the cached clean, named Minecraft 1.21.1 artifact, not the raw obfuscated client or NeoForge-patched runtime. Its SHA-256 is pinned to `BC811B3368CA4E056672AB7425682247A68AB72210F14B0BA68B91EEAE040CE3`; cached merge/rename provenance and the vanilla client download checksum were checked. No mod was removed or patched to repair this launcher setup.

Two controlled-test build attempts stopped before Minecraft because an idle Gradle daemon held the generated artifact JAR. Gradle's normal stop operation released that lock. The first actual controlled launch then exposed a development test-namespace mismatch and ran zero tests despite a successful Gradle exit. It is not counted as a pass. All attempt logs are retained.

The original terrain-order failure and corrected fresh-world proof are documented in `WORLDGEN_TERRAIN_ORDER_REGRESSION.md`. Known pre-existing recipe parsing errors and unrelated mod warnings remain disclosed in `WORLDGEN_ISOLATED_RUNTIME_SMOKE.md`; this task does not silently change or disable their sources.

The first combined final-candidate attempt (`final-a1`) is retained as **FAIL**, not a seven-test pass. Its test selector accidentally included the natural-terrain test because that test explicitly used the production template namespace, making eight tests. That test inherited `terrain-report-a.json` and overwrote the original early A JSON. The original A world/log, B report, saved-block diff and both corrected `fixed1` reports/comparison survive; the lost original JSON identity and the replacement provenance are recorded in the change manifest. No reconstruction is presented as original evidence. A dedicated addon template namespace, seven-test preflight, fresh-world guard and unique defensive output path now prevent this collision. The later report is preserved separately as `final-unexpected-terrain-a1.json`.

In that same attempt, the trace Lava fixture's two prepared layouts differed, although both production calls performed zero writes. The original run lacks input snapshots, so fluid reactions are a suspected mechanism rather than a measured diagnosis. The corrected fixture uses an inert shell, checks every intended input state and exact repeated input/output layouts, and retains all prior assertions. The corrected `final-a2` run selected exactly seven tests, emitted no natural-test marker or unexpected terrain report, and passed all tests without changing production code or configuration.

## Completed additional checks

The corrected client run took 4 minutes 23 seconds including the first-run accessibility screen. The computer-use skill was used to inspect that screen and continue with its default narrator/accessibility settings; no login or privacy setting was changed. Minecraft itself rendered the accepted textures through its item renderer on an NVIDIA RTX 4090, OpenGL 4.6, LWJGL 3.3.3. The block atlas was 8192×8192. The 1254×1254 Bertrandite sprite loaded at its approved dimensions; the other checked block sprites were 16×16. The process shut down normally with exit 0 after writing `IC_CLIENT_RENDER_PASS`, its JSON report and the inspected native screenshot. This is inventory/block-model GPU acceptance, not in-world shader or survival certification.

The corrected controlled test (`controlled-report-a2.json`) passed all 123 cases in 5.249 seconds; the full launch exited 0 in 1 minute 33 seconds with `All 1 required tests passed`. It invoked actual production placement on 512-cell fixtures in one loaded owner chunk, twice per major case, and compared exact state hashes. Tests covered every profile/quality, PGM allocation, cobalt and uranium/thorium success/failure branches, graphite depth bands, protected air/fluid/bedrock/dirt/gravel cells, and micro bounds. Configuration hashes before/after matched, and 60,955 fixture writes were restored. These are deliberately conditioned placement cases, not 123 naturally found deposits.

Evidence lives under `isolated-runtime/client-render-20260909-030821-140/` and `isolated-runtime/geology-gametest-20260909-001051-895/`. Detailed development-only reports are under `tools/client-smoke/RESULTS.md` and `tools/controlled-geology/RESULTS.md`.

## Exact final-build runtime acceptance

On September 9, 2026, `final-acceptance-run-a2-20260909.log` records seven tests starting at 04:13:59 Eastern and all seven passing at 04:14:08, followed by normal shutdown and exit 0. The launcher verifies the final JAR's complete SHA-256 and byte length before launch and refuses an existing world/report. It uses fresh `final-acceptance-worlds/final-a2` with the same bounded normal-terrain test preset and 233-JAR server subset.

The four packaged production tests verified registries, loot/placer behavior, applied required mixins, config/datapack loading and decoded assets. `final-controlled-a2.json` passed all 123 cases with 1,164,842 assertions and restored 60,955 temporary positions. `final-trace-a2.json` passed ten cases with 80,922 assertions and restored 18,439 temporary positions. Both configuration SHA-256 values matched before/after: `f3771f9c23fa1b419a350f250721a0942377f72557053b09921ef55bc2730398`.

The trace suite verified Iron/Copper/Coal outputs, no writes into Dirt/Air/Water/Lava, inclusive search-depth behavior, exact twelve-block maximum-attempt output, and matching repeated states. Across 64 seeds, 128 bounded diamond calls placed exactly three blocks each and none above Y=-20. The old unbounded helper placed above the ceiling on 21 control seeds, demonstrating that the regression actually detects the earlier behavior. Source validation separately verifies the natural diamond branch uses this bounded overload; total static integration assertions are now 1,126.

`final-oil-a2.json` independently repeated the native feature/scanner/pump, finite-debit, exhaustion and primary-well NBT roundtrip checks on the final JAR, with 8,253 assertions and cleanup of all 8,192 snapshot blocks. The specific runtime reserve amount is reported in that JSON; this fixture does not claim deterministic native reserve initialization or final balance. The earlier standalone oil run below remains historical evidence, not a restated final-run reserve value.

The native oil check passed in 698 ms, with a 94-second complete server launch and normal exit 0. The first inspected eligible regional candidate supplied a well at (309, -64, 250), chunk (19, 15). After a negative marker/scanner control, the actual registered feature placed the native TFMG deposit and six crude-oil source blocks; the native scanner detected it. A connected native pump registered 1,890 reserve units, extracted 1,000 mB and reduced reserves to 1,889. A controlled exhausted reserve stopped output. Primary-well data survived the native in-memory NBT save/load roundtrip; all 8,192 snapshot blocks and the temporary reservoir record were cleaned up. This is not a powered pumpjack animation, full field restart, or extraction-balance playtest. See `tools/oil-smoke/RESULTS.md`.

## Deliberate limits

The final inventory records 400 task-authored files (392 created, eight modified), plus separately classified backups, controls, delivery copies and generated evidence. Its two index files exclude their own hashes to avoid recursive self-hashing. The final JAR is a matched copy of the built/tested artifact; no development addon is shipped. The source Blockbench model and approved texture bytes remain unchanged. Deliverable: `outputs/geology-framework-20260909` under the workspace root, containing the JAR, four default JSON files and README.

- Bounded and controlled tests are not an exhaustive census of every biome, seed, structure collision, or world generator. Normal-noise Overworld generation is the supported target; no retrogen is performed.
- Per-chunk rich-quota rounding, clipped actual deposit volumes, associated-resource integer floors and the bounded cave-exposure approximation remain the documented implementation limits. The trace search-center depth is bounded; tiny trace neighbors can reach one additional block. These are not silently represented as exact global quotas or exhaustive surface-connectivity proofs.
- Final recoverable low-yield/rich volumes and processing recipes are deferred by the specification. The 1000 mB ingot / 9000 mB storage-block standard is metadata, not proof of starter-ingot income or mine-lifetime balance.
- The approved Bertrandite texture remains the explicit 1254×1254 exception. It is not silently resampled to satisfy a test; the other approved exported textures are 16×16.
- No production deployment, user-save editing, or blanket certification of the unrelated pack content is included.
