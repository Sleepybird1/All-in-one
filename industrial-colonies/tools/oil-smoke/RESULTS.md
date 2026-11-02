# Native TFMG oil compatibility — PASS

This bounded oil acceptance task is **100% complete**. One required development-only GameTest passed on September 9, 2026 in the disposable server-compatible test copy. This result is not a claim that the entire modpack, every extraction machine, or production balance is complete.

## Verified evidence

- [Runtime report](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/isolated-runtime/geology-gametest-20260909-001051-895/oil-native-report.json>): `status: PASS`, **8,253 executed checks**, fixture elapsed **698 ms**. The check count includes **8,192 per-position pre-existing-block-entity guards**, not 8,253 independent gameplay scenarios.
- [Captured run](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/isolated-runtime/geology-gametest-20260909-001051-895/oil-native-run-20260909.log:4096>): line 4096 records `GEOLOGY_OIL_NATIVE PASS`; line 4099 records all **1 required test passed**; line 4159 records Gradle success in **1 minute 34 seconds**. The invoking process exited **0**.
- Fixture report SHA-256: `D297E70899A2758C860BEA3A3414F27A3F12276D052F4A34039E66F55DAC7BFB`.
- Captured log SHA-256: `F6CF8FB1345374042803C3AB60059471B44D6917A777463A50A4CA8EAFFF7E6C`.

## Actual fixture result

| Check | Observed result |
|---|---|
| World seed | `0` |
| Eligible regional candidates inspected | `1` of the hard maximum `289` |
| Explicit chunk request | Chunk `(19, 15)`; maximum `1` |
| Selected well | Block `(309, -64, 250)` |
| Field center | `(309, 250)`; accepted field roll `0.29234796689071296` |
| Actual registered feature | `industrial_colonies:regional_oil_reservoir`, implemented by `OilReservoirFeature` |
| Native output | Native oil-deposit marker and **6 TFMG source-crude blocks** before installing extraction fixtures |
| Native scanner predicate | Negative before regional placement; positive afterward |
| Native pipe/pump discovery | `PumpjackBaseBlockEntity.findDeposit()` found the well through native industrial pipes |
| Finite reserve | **1,890 → 1,889** native reserve units after **1,000 mB** TFMG crude extraction |
| Exhaustion control | Setting only the fixture-created reservoir to zero stopped output and zeroed its mining rate; prior reserve then restored |
| Native saved-data codec | Primary well identity and remaining reserve survived native `TestSavedData.save/load` NBT roundtrip |
| Cleanup | Restoration routine completed for **8,192 snapshotted block positions**, removed the fixture-created reservoir record, and released the chunk ticket |

The fixture called the real configured regional feature and native TFMG placement/extraction code. It did **not** substitute fake scanner data or directly fill the pump tank. The native saved NBT representation had SHA-256 `0D82D7F204103EBF46EEB9BF1013115FECDB479C36D8DBA2CB7D839B340F8E55`.

The well was selected using unchanged regional/biome/terrain eligibility. Its chunk was then deliberately snapshotted, scanner-findable bottom markers were cleared for a negative control, and regional placement was invoked again. Therefore this is a **controlled native compatibility fixture**, not an observational survey of natural oil frequency, field size, regional abundance, or extraction balance.

## Scope and unchanged state

- No production source, production resource, recipe, global TFMG setting, installed modpack, or live save was changed by this addon. `infiniteDeposits=false` and scanner depth `-64` were prerequisites, not settings changed to make the test pass.
- The only reserve forced to zero was the fixture-created native record in the disposable world. It was restored immediately after the exhaustion assertion, then removed during cleanup.
- Current staged, build-output, and delivery candidate JARs are identical: SHA-256 `ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546`. The oil fixture did not rebuild or modify that candidate.
- Post-run staged `config/tfmg-common.toml` SHA-256 is `0FB1F8830443BB25E8EE0DDE81490B9F49151DECD42BB9F5C109EC376F6BB4B0`. No config setter or config-file write is present in the fixture.
- One explicit FULL-chunk request can cause Minecraft to generate its dependency halo. It does not prove that only one chunk was generated in total.
- Cleanup reports that the restoration routine completed; this fixture did not perform a separate post-cleanup saved-region byte comparison. Native temporary fluid placement may schedule fluid/block updates in the disposable world.
- No complete powered pumpjack/hammer/crank assembly, client scanner display, all associated-well serialization, disk restart persistence, long-duration reservoir economics, or unrelated pack recipe behavior was validated here.

The template-namespace correction was verified before launch: both the annotation and enabled test filter use `ic_oil_smoke`. Generated addon resources contain the unchanged 107-byte empty NBT under that namespace; source/copy SHA-256 is `9D4331C7FA69FC53A50A1568F54856B9627A29D30BBB19DA30CA93FE6CC731B5`.

## Final candidate rerun — combined final-a2 PASS

**Latest acceptance: 2026-09-09, 100% of this bounded suite complete.** The preceding standalone run's `ABC9A4D5…` candidate, timings, reserve counts and hashes remain historical evidence, not claims about the newer candidate.

The final staged JAR is **1,695,276 bytes**, SHA-256 `5A4CCD0BA37629225EE88996281FCA7F1A1B704E9E1EE5DC712ECB363EEFFFBA`. The combined final-acceptance layer ran revision `a2` in fresh stage world `final-acceptance-worlds/final-a2`, with the same approved 233-JAR server-compatible subset and both test addons. No oil configuration or production oil source was changed for this rerun.

`final-oil-a2.json` records **PASS**, **8,253 assertions**, **627 ms**, seed 0 and one inspected regional candidate. The well remains **(309, -64, 250)**, chunk **(19, 15)**, with six actual native source-crude blocks. Scanner negative/positive controls and native pipe/pump discovery passed. This run's native reserve was **7,011 → 7,010** after **1,000 mB** extraction; exhaustion stopped output, and the native primary-well NBT roundtrip passed. Cleanup completed for **8,192 snapshotted positions**, removed the temporary reservoir and released its ticket. The new reserve counts are observed native values, not substituted historical values or a claim about reservoir-balance determinism.

- Final oil report SHA-256: `E5648BC74AB8A6D7C22627DC3F6239D47071FB10D6FD9EA0A8C761242D7FE5E4`.
- Native serialized NBT SHA-256: `A25B18FB3CBCBE8FB8D8DCBA51F1AB070792588226CC7C614965C3D08F35B8BE`.
- `final-acceptance-run-a2-20260909.log` line 4088 records oil PASS. Lines 4111–4112 record **all seven required GameTests passed in 9.662 seconds**; line 4172 records `BUILD SUCCESSFUL in 1m 34s`. The invoking process exited 0.
- Combined log SHA-256: `68A1F892942E7E411814486B48BD75470E781762972FFA4066D1624DBAF98916`.

The first combined attempt, `final-acceptance-run-a1-20260909.log`, had an individual oil PASS but **failed overall**: an unintended eighth natural-terrain test was selected and the trace fixture failed. The namespace/report-path and trace-fixture corrections preceded final-a2. That earlier overall failure is not promoted to acceptance. All native-compatibility scope limits above remain, including no complete powered-machine, disk-restart, natural-abundance or unrelated recipe certification.
