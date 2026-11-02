# Material-processing acceptance record

Status: **Implemented, scoped automated acceptance PASS, and installed on 2026-09-09.** Native material a3, full-client rendering and Lithosphere A/B all passed for the same candidate. Installation is not a claim of a survival playthrough, physical manual-operation testing or complete powered-factory certification; the explicit limits and placer TODO below remain.

## Observed native runtime evidence

Stage: `isolated-runtime/geology-gametest-20260909-064550-754`.

- Candidate: `industrial_colonies-0.5.0.jar`, SHA-256 `8DF80E5C7E4B447F651696A9383A1487B26F557A67D6263DEAFA3805BC675D91`.
- Catalog used by a3: SHA-256 `31F344D33295A70F4CC19C1F38B56C604DD13965C7E77E7EC701BC3EFAD4AD45`.
- Material script: SHA-256 `1E44F7BC42718AAF3218C48526F2F534DB31679BC2E18127A37CAC5158A2EC78`.
- Report: `material-processing-report-a3.json`, SHA-256 `F5854F65678147346EE96A02221BF7A63A4FAB5F0DC81CB1B47B92B61B4B8F03`.
- Export evidence: `material-processing-export-a3.json`, SHA-256 `C4A08AB2B7DF868A405E115A65A8F36F9C125C4853F135C492437B70CFC72C43`.
- Log: `material-launch-a3.log`. `MATERIAL_PROCESSING_SMOKE PASS` and the single required GameTest passed; Gradle succeeded after 2m44s. The report's 176 ms is the fixture's own synchronous checks, **not** startup or machine-processing elapsed time.
- Roster: 241 copied physical input JARs, with the six documented server-incompatible rendering/Distant Horizons JARs held recoverably; 235 active server JARs. This is not a full-client launch.

| Check | Observed a3 status | Evidence / remaining work |
| --- | --- | --- |
| All generated recipes and native encoded parity | **PASS: 299/299 verified, 2,846 assertions** | Both TFMG distillation timings are explicit; zero catalog problems and zero native encoding mismatches. Strict parity was preserved. |
| No Modern Foundry alloy recipes | PASS, 3 assertions | Both serializer `modernfoundry:alloy` and native type `modernfoundry:alloying` registered; zero matching loaded recipes. Seventeen unrelated unregistered type/serializer identities are recorded, not ignored through an exception. |
| Retained electronics bootstrap | PASS, 6 assertions | Native sequenced assemblies still produce two n-semiconductors, two p-semiconductors and one prepared silicon wafer. |
| Native exclusive PGM milling | PASS, 142,376 assertions | 100,000 native rolls; 20,177 recoveries, with Os/Pt/Ir counts 14,053 / 5,091 / 1,033. Zero-or-one output, network codec, invalid inputs and probability endpoints checked. |
| Exact fan gate and negative-cache retry | PASS, 34 assertions | Normal/Weathered reject industrial separation; Industrial Iron succeeds after a negative cache; 153 direct processing calls. Ordinary washing remains usable with all three families. |
| Native electrical vat and tungsten arc | PASS, 67 assertions | Eight registered electrical routes; native electrode operation constraints; unpowered electrode rejected; tungsten native arc lookup and input/output quantities. Arc base time 800 ticks, base total energy 409,600. |
| Manual configuration and no-heat Cinnabar batch | PASS, 13 assertions | Enabled, 1,200 ticks, no batching, 20-tick hammer cooldown, damage 1, reach 4.5; damageable IE hammer registered; batch Create mixing requires no heat. |

The a3 fixture passed **145,355 assertions across all seven sections**. Its pre-script export passed with 672 merged recipe cards and 1,058 removal rules; all merged card identities were retained. Modern Foundry basin casts omit a mold intentionally: only the exact `Ingredient.EMPTY` identity in `modernfoundry:casting_basin` with no source `cast` field is exempt from nonempty ingredient checks. Empty tags are not exempt.

Historical correction: a2 failed at 297/299 because the sulfur distillation and coal-tar fractionation recipes omitted the TFMG/KubeJS default `processing_time: 100`. Explicit timings corrected the two parity mismatches; a3 freshly verified the corrected catalog. The preserved a2 failure is not relabeled as a pass.

## Pure/data-contract verification — PASS

Fresh checks completed on 2026-09-09, recorded separately from native game acceptance:

- Combined catalog: **3,914 assertions across 18 groups**, covering 299 recipes / 74 items / 25 fluids, installed resource references, intermediate closure, fixed-value contracts, explicit native timing/energy limits and reproducible builder output. See `MATERIAL_PROCESSING_CHEMISTRY_AUDIT.md` and `tools/material_processing/test_catalog.py`.
- Manual/exclusive runtime logic: **1,205,434 assertions**, including 50 invalid cases, in `tools/test_processing_runtime.ps1`. These are pure state/probability tests, not a real-player burner/hammer session.
- Fixed-value policy: **48 Node regression cases and six detected in-memory mutations**, via `tools/material_processing/test_policy.js`. Node fixtures are not Rhino runtime evidence; a3's successful actual KubeJS/recipe-manager load supplies the separate native layer.

## Full-client acceptance — PASS

Fresh stage `isolated-runtime/material-client-20260909-072449-528` passed **7,773 assertions**, using all **241 physical JARs / 338 loaded mod IDs** and the same candidate/a3 catalog above. The harness compiled, resolved 109 dependencies and completed on an NVIDIA GeForce RTX 4090, OpenGL 4.6.0 / NVIDIA 610.88 (LWJGL 3.3.3+5). `client-launch.log` contains `MATERIAL_CLIENT_RENDER_PASS`; the process exited 0 and Gradle succeeded in 1m51s.

The report `material-client-report.json` has SHA-256 `43A94194ED1A8DB58E8D142995BBC8FCE2E3A699571F8426659B58B8AE88D67B`. It verifies 74 native item models, 25 fluid pairs / 50 still-flow sprites, 41 geology/placer models / 258 quads, 299 catalog identities and the transformed native Radiance branch returning false. The four 1280×720 framebuffers were captured after 120 frames each (480 total); the lead agent inspected all four and confirmed the rendered content. These are actual Minecraft GPU captures, not generated/replacement images. See `tools/material-client-smoke/RESULTS.md` for screenshot hashes.

The functional gray placeholder component icons deliberately reuse registered existing textures; passing rendering does not imply finished unique artwork. Separate source/package reconciliation passed **563 asset byte comparisons**, excluding the one existing Gradle-excluded research resource; all **42 approved PNGs remained unchanged**.

Historical failed attempt: `material-client-20260909-070642-400` reached accessibility onboarding, showed unusable white captures and was observed inside native GL drawing through Iris. Only the verified isolated client process was stopped; that attempt ended after 7m20s with no render PASS. The successful replacement profile seeded only `onboardAccessibility:false` plus LF, preserving all other native defaults; no live options, authentication/privacy changes or runtime screen dismissal were used. This does not establish that onboarding alone caused the earlier GL issue.

## Native Lithosphere terrain A/B — PASS

Both fresh `r1` worlds in stage `geology-gametest-20260909-064550-754` passed all **six required tests each**. A succeeded in 2m52s, B in 2m51s. The separate receipt `lithosphere-acceptance-r1.json` passed **37 wrapper assertions**, SHA-256 `80EBB537F181C329EE882197A0F5603684C007CB4EF48A1A2DBDD3F876977911`.

Exactly reversed requests for **12 chunks per world**, seed 0, produced identical full shape-state hashes/counts for three formations/families: Galena (1,205 surviving host positions), Sphalerite (1,126) and Magnetite (4,830), each spanning four chunks. Actual Regions Unexplored biomes were observed. Cross-boundary retained-neighbor bonds were 201 / 154 / 301 respectively. Both native compatibility reports passed with five economic features, ten direct guard calls, 129 inspected Overworld biomes and all 12 decorative resource priorities checked.

The comparator is read-only without `-OutputPath`. It requires both reports to pass, the same configuration/selected formations, exactly reversed direct chunk requests, and identical full formation records including counts, state hashes and biome metadata. It checks three selected natural formations under a maximum of 60 direct chunk requests; Minecraft's implicit dependency halo is not capped by that number. This is a bounded same-seed order comparison, not a whole-world distribution survey.

The separate current validator includes the historical comparison, then requires both reports to have `expectedTerrainMod: mr_lithosphere`, noise source containing `lithosphere`, effective heights -64 through 512, and `noiseSettingsSha256` equal to both `lithosphere-preparation.json` and the actual staged Lithosphere resource. It checks source/staged candidate hashes against preparation and both companion compatibility reports. The current expected noise hash is `E78449FBA92C289267BDDB3E315B670F860B3B183FD0208541BE8BAE8676805E`.

```powershell
# Preferred complete read-only validation; use the bare compatRevision here.
& ./tools/lithosphere-compat/validate-lithosphere-acceptance.ps1 `
  -Stage './isolated-runtime/geology-gametest-20260909-064550-754' `
  -Revision r1
```

The wrapper does not alter the historical comparator/results or launch a game. Optional `-OutputPath` may create one new result inside the selected disposable stage and refuses overwrites. Its source candidate defaults to the base preparation path; use `-CandidateJar` only for an explicitly identified byte-identical archived/delivery candidate. Terrain reports do not embed a candidate hash, so retain the matching launch logs/preparation provenance rather than claiming stronger runtime attestation. The required GameTest summary must also pass.

These current reports support the observed RU/multiple-family/cross-boundary results above. Historical tests with other candidates/Tectonic remain separately attributed. Do not relaunch the accepted worlds; any new runtime attempt needs a fresh revision/profile.

## Live deployment — APPLIED

The scoped installer completed exactly four live writes in `C:/Users/GodPC/curseforge/minecraft/Instances/All in one`: the accepted 0.5.0 JAR, merged default project, native generated recipe script and material-processing script. The previous active 0.4.0 JAR was retired recoverably; 240 third-party JARs, saves and other projects/configurations were not replaced. All 653 unrelated recipe cards were preserved.

[Deployment journal and recovery record](<C:/Users/GodPC/curseforge/minecraft/Instances/All in one/_industrial_colonies_backups/material-lithosphere-0.5-20260909T112922.207472Z/deployment.json>) records `APPLIED` and the exact reviewed plan. Installed candidate/catalog/script identities are listed above; the live merged project is `0AACB7B7BC2E0BA0A0AA8C4211A115146FDC521141A1CCEB400ED71532FF5DA9`, and native export is `D9DE3956D56B9015603C496302AEEE27983C31D3F6E01DEC92660C7BF65DD692`. Recovery/install details are in `tools/material_processing/DEPLOYMENT.md`. No existing-world retrogen or survival playthrough is claimed.

## Explicit untested scope and remaining TODO

- **Manual physical operation: NOT TESTED by this runtime addon.** A real player's prolonged 60-second burner interaction, interruption/reset, station contention, hammer wear and rejected automation are not replaced by a configuration or pure-state-machine test.
- **Powered factories: NOT TESTED.** Native recipe decoding, matching, rolling and direct API checks do not establish assembled multiblock power/heat/transfer behavior, actual fan airflow geometry, sustained throughput, or all processing economics.
- **Gold placer sediment: TODO, intentionally not finalized.** After inspecting installed block/biome registries, select an appropriate existing cold-river sediment/dirt/gravel block before finalizing its gold-flake processing recipe. Do not invent a new placeholder block or treat the existing Gold Flakes model/render check as completion of this requirement.
- **Evidence preservation:** keep failed/revised evidence and its original identity. Installation uses the current passing candidate; a2 and the earlier failed client were not relabeled as passes.

No active stage, catalog, chemistry recipe, production source or historical accepted harness was changed by this review. Authored files are this acceptance record and `tools/lithosphere-compat/validate-lithosphere-acceptance.ps1`.
