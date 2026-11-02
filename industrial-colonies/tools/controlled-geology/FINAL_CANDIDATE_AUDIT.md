# Final diamond-ceiling candidate — packaging audit PASS

This bounded read-only packaging audit is **100% complete**. It compared every file entry in the old and final JARs, checked approved asset provenance, and reran source/resource integration validation. No Gradle build, Minecraft process, production edit, stage edit, or manifest edit was performed by this audit.

## Candidate identities

| Artifact | Bytes | File entries | SHA-256 |
|---|---:|---:|---|
| [Before diamond fix](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/backups/diamond-boundary-fix-20260909/industrial_colonies-0.4.0-before-diamond-fix.jar>) | 1,695,174 | 896 | `ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546` |
| [Final build](<C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/industrial-colonies/build/libs/industrial_colonies-0.4.0.jar>) | 1,695,276 | 896 | `5A4CCD0BA37629225EE88996281FCA7F1A1B704E9E1EE5DC712ECB363EEFFFBA` |

Each ZIP file entry was decompressed and hashed independently with SHA-256; directory-only ZIP records were excluded from the count. There are **895 byte-identical entries, exactly one changed entry, zero added entries, and zero removed entries**.

## Complete changed-entry inventory

The only changed path is:

`dev/godpc/industrialcolonies/geology/GeologyFeature.class`

| Version | Uncompressed bytes | Entry SHA-256 |
|---|---:|---|
| Before fix | 28,756 | `B7CBFD286E902CE73E642ABD41DF43ECCDC2C155A3D4801F9EEBE242222F2E24` |
| Final | 29,111 | `221D574CA94F1B34020FBF46CB4B8BEA5D909E9FE1C99ADDF37A61522B46E2F0` |

The source comparison against the preserved `GeologyFeature.java` backup shows only the intended diamond micro-cluster ceiling change: the diamond branch passes its configured maximum Y to a `tiny` overload, and that overload filters every candidate voxel above the ceiling. The unchanged-signature overload delegates using the existing world-height safety ceiling for ordinary tiny deposits and starter traces. Source SHA-256 for the final `GeologyFeature.java` is `AE36A800A53499CD6507265BF58CC54DDE393E27971CD8A5E9AC6FDA051180D2`.

This source review explains the change; it is not substituted for the root agent's fresh runtime boundary regression.

## Assets and data

- **All 653 packaged `assets/` and `data/` file entries are byte-identical** between old and final JARs. This includes block/item models, textures, language data, central geology/oil JSON, world-generation data, tags, loot, and the original smoke template.
- All **295** outputs listed in `WORLDGEN_GEOLOGY_ASSETS.json` match their recorded hash, current resource-source bytes, and final packaged bytes. No missing or mismatched output was found.
- All **42 approved PNGs** also match the exact embedded PNG bytes in the approved V27 Blockbench source. The V27 file still has SHA-256 `D6D325AB105AA77F5FF71346B7E5884DD434B9FC6267462E221A6352375BB1F4`.
- **41 PNGs remain 16×16**. The explicitly approved Bertrandite source remains **1254×1254**, unchanged, with SHA-256 `72BB89C5BE9EA79F3C3C4059F3EAFEC5D80BAAF8F73F3A3F194E47C595D687A0`. No resizing or recoloring occurred.
- Every other packaged class is byte-identical, including the oil integration, finite-reservoir mixin, registries, client rendering integration, planner/config/math classes, suppression hooks and entrypoint.

## Development-addon exclusion

No separate development addon is packaged: no `oilcheck`, `terraincheck`, or `clientcheck` classes; no `ic_oil_smoke`, `ic_terrain_smoke`, `ic_controlled_smoke`, `ic_trace_smoke`, or `ic_client_smoke` resource namespace; no tool trees, isolated-runtime files, Blockbench project, or standalone planner/oil test classes.

The original production-source `GeologyGameTests.class` and `data/industrial_colonies/structure/geology_smoke_empty.nbt` remain packaged and unchanged. They are existing candidate entries, not newly leaked development-addon files. The separate addon namespace aliases exist only in development build resources.

## Static integration validation

`tools/validate_geology_integration.ps1 -AllowReferenceTextures` passed **1,124 assertions** against the final source/resources: 40 custom cubes plus placer, 24 deposits, 68 suppressed placed features, and six registered geology mixins/accessors. The only reported texture-dimension exception was the retained approved Bertrandite PNG. This validator is source/resource consistency evidence, not a runtime launch.

Subsequently, two explicit diamond callsite/ceiling contracts were added and the root reran this validator: **1,126 assertions PASS**, recorded in `isolated-runtime/geology-gametest-20260909-001051-895/final-static-validation-20260909.log`. No packaged asset or candidate changed in that test update. The exact final candidate also passed the seven-test runtime in `final-acceptance-run-a2-20260909.log`; its scope is consolidated in `WORLDGEN_FINAL_ACCEPTANCE.md`, not inferred from this earlier package-only audit.

## How earlier positive tests apply

| Earlier positive evidence on candidate `ABC9…` | Applicability to final candidate `5A4C…` |
|---|---|
| Full-client rendering of 40 approved cubes plus placer | Strong component evidence: all tested assets, model data, registration and rendering classes are byte-identical. The old full-client launch is still attributed to `ABC9…`, not falsely relabeled as a fresh final-JAR client run. |
| Native oil placement/scanner/finite extraction, 1 required test and 8,253 checks | Strong component evidence: every oil/TFMG compatibility class and oil/registry resource is byte-identical. This remains the controlled native test on `ABC9…`; it does not become a new final-JAR runtime run or an oil-distribution survey. |
| Pure planner/config/math tests, 5,818,795 assertions | Component-applicable because those packaged classes and their JSON inputs are unchanged. These pure tests do not exercise `GeologyFeature` placement. |
| Natural terrain A/B and controlled placement suite | Earlier outcomes remain useful evidence for their recorded configurations, seeds and component paths. Because `GeologyFeature.class` changed, they must not be described wholesale as fresh runtime acceptance of the exact final JAR. In particular the ceiling correction requires its own final-candidate boundary check. |

The root agent owns fresh runtime testing of the exact final hash, including the updated controlled micro/diamond-ceiling fixtures and actual starter-trace/placer placement checks. Those run reports and logs must record their actual final candidate and result. **This audit establishes package identity and unchanged-component applicability; it neither launches those tests nor asserts unobserved fresh-runtime outcomes.** The final implementation report consolidates the root's completed runs separately.
