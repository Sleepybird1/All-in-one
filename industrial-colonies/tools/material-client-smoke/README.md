# Current material-processing full-client smoke fixture

Status: **PASS and accepted candidate installed.** Fresh full-client stage `material-client-20260909-072449-528` passed 7,773 assertions, all four inspected native framebuffer captures, 241 physical JARs / 338 loaded mod IDs, 74 item models, 25 fluids and 41 geology models / 258 quads. Process exit 0; Gradle success in 1m51s. See `RESULTS.md` for exact identities and limits; this is not survival-playthrough certification. The first attempt `material-client-20260909-070642-400` produced no render PASS and remains preserved as an unsuccessful attempt. Do not rerun either evidence profile. `tools/client-smoke` and its historical accepted stages/results remain untouched.

## Preparation

`prepare-material-client-smoke.ps1` defaults to a read-only plan. The parent must first finish and verify the corrected candidate, apply `tools/material_processing/stage.py` to a fresh isolated server stage, and complete the coordinated server acceptance. Preparation requires that stage's `material-stage-patch.json` and verifies its current project/script/catalog identities. The preparator never applies a missing recipe patch itself.

The current intended source is the a3-accepted `isolated-runtime/geology-gametest-20260909-064550-754`, but it is a required argument, not a hardcoded historical dependency:

```powershell
& ./tools/material-client-smoke/prepare-material-client-smoke.ps1 `
  -ServerStage './isolated-runtime/geology-gametest-20260909-064550-754'
```

Only the parent should subsequently add `-Stage` after the source is ready. This creates a **new** `isolated-runtime/material-client-<timestamp>` directory and a `material-client-preparation.json` manifest. Candidate filename/version is resolved from current `gradle.properties` (or explicit `-CandidateJar`) and must match the source stage exactly; no old candidate hash is substituted.

The full client copy must contain exactly **241 unique physical mod JARs**. A 235-JAR server subset is reconstituted with all six held originals: Sodium, Iris, ETF, EMF, Euphoria Patcher and Distant Horizons. A full 241-JAR source is also accepted. Held directories are read only; no source file is moved, removed or patched. Every destination JAR is SHA-256 checked. Lithosphere, WWOO and CristelLib must be present; a stale Tectonic input causes refusal.

Only the selected stage's configuration/scripts/project/data/offline dependency directories are copied. Existing worlds, launcher identities, tokens, server lists, options, resourcepacks and shaderpacks are not copied. The current material source `content.json` and recipe catalog are snapshotted and hashed into `material-client-inputs`. The candidate's bundled content must be byte-identical to the source and contain all **74 items and 25 fluids**. The new Radiance mixin must be registered in the common mixin list, and no development addon classes may be packaged in the production candidate.

### Explicit first-launch orientation seed

For each **new** disposable profile only, the preparator authors `options.txt` with exactly one UTF-8, LF-terminated line:

```text
onboardAccessibility:false
```

This is setup for a non-security first-launch orientation screen, not a copied live options file or a change to narration, accessibility preferences, account/authentication, telemetry/privacy, multiplayer, rendering or any other setting. All other options are unspecified and keep native defaults. The seed text and SHA-256 are recorded in `material-client-preparation.json`; the init requires the exact file before launch. Minecraft may subsequently write its normal expanded defaults, so runtime acceptance checks the loaded native boolean rather than expecting the initial one-line file to remain unchanged.

The key was verified in cached named Minecraft 1.21.1, SHA-256 `BC811B3368CA4E056672AB7425682247A68AB72210F14B0BA68B91EEAE040CE3`: `Options.processOptions` visits the boolean key `onboardAccessibility`; the load visitor `Options$2.process(String, boolean)` reads it through `Options.isTrue`, retaining existing defaults for missing keys; `Minecraft.addInitialScreens` adds `AccessibilityOnboardingScreen` only when the flag is true. No runtime method patches, interception, automatic buttons, screen dismissal or existing-profile edits are used.

Installed assets and exact NeoForge 21.1.248 userdev metadata are verified read-only. The exact previously acquired DevLaunch artifacts and bundled offline dependency repository are copied from the source stage. No downloads or launches occur. As with the accepted client harness, Gradle `--offline` is not a runtime network firewall: the parent controls approval and launch permissions separately.

## Compile and launch contract

Preparation outputs exact commands without running them. The generated init binds only the new `materialClientSmoke` source set and `ic_material_client_smoke` addon; the real candidate loads from the copied `mods` directory. It retains the verified Connector clean-Minecraft artifact guard and official client run template used by the accepted test.

```powershell
# Use the generated NEW stage init, not the historical accepted client init.
& ./gradlew.bat --offline --no-daemon --no-configuration-cache --console=plain `
  -I '<new-stage>/material-client-smoke.init.gradle' `
  compileMaterialClientSmokeJava processMaterialClientSmokeResources `
  prepareClientRun auditMaterialClientSmokeDependencies
```

The parent launches `runClient` separately with that same init after coordination. It uses only an offline dummy development identity, with no server-join or world-load arguments. There is no GameTest-server/headless flag. The init rechecks all 241 JAR identities and both material input snapshots before launch, and refuses existing report/screenshots/saves rather than overwriting evidence. The addon checks JARs again at runtime and after rendering.

The addon waits for the normal title screen with no resource-reload overlay. It does not dismiss onboarding, authentication, errors, permissions or other screens. `MATERIAL_CLIENT_WAIT` reports the current screen/overlay class on changes and every 15 seconds while waiting. If client ticks continue but an unexpected screen/overlay lasts 180 seconds after the first observed client tick, it writes a failing diagnostic report with the screen class and elapsed time, then requests closure of this disposable client. The bound can be configured through `ic.materialclient.titleWaitMillis` (clamped to 1–600 seconds). This event-driven diagnostic **cannot interrupt a native GL/driver call or diagnose a startup that never reaches client ticks**.

Once ready it verifies assets, shows its own native render sheets and captures four actual framebuffers after 120 frames each. It closes only this disposable client five seconds after success, or on a test failure. It asserts that no world or server connection exists while waiting and throughout its render sequence. The initial options seed is reported as fixture setup; it does not count as a content/render test or justify a PASS without the unchanged native checks and four actual captures.

## Measured runtime coverage

- **41 geological models / 258 block quads:** all 40 approved blocks plus the Gold Flakes placer. Exactly six quads per cube and eighteen for the placer, valid baked block/item models, GUI-3D items, no missing sprites and the approved resolution of each sprite. Bertrandite retains its approved 1254×1254 source; the other sprites remain 16×16.
- **74 material item models:** actual registered items, non-missing baked models, nonempty native quads, valid stitched particle/quad sprites and the exact reused texture specified by the source content manifest. Both item sheets render with Minecraft's actual item renderer.
- **25 tank-fluid pairs / 50 still-flow sprite checks:** source/flow registration and linkage, shared fluid type, no bucket, active client fluid extensions, exact source-catalog tint and valid atlas still/flow sprites. The fluid sheet draws both actual stitched sprites with the native fluid tint for every fluid. These are inventory/tank-style sprite samples, not placed world fluids or a physical tank model test.
- **Radiance mixin runtime applicability:** the actual registered native `ChromaticCompoundItem` must load successfully with the strict production mixin, contain exactly one merged `engineeredRadianceOnly` handler with the correct `ConfigBool` parameter, and return false when passed the existing Refined Radiance switch object. This directly invokes the merged runtime branch without reading/changing server configuration, fabricating entities or opening a world. It does not claim a thrown-entity conversion test or runtime testing of Shadow Steel behavior.
- **Identity:** dynamic candidate hash, copied authoritative content/catalog hashes, full physical JAR roster and graphics backend/API are recorded. The physical JAR count is not conflated with NeoForge's nested/aliased loaded-mod count.

## New evidence only

The new stage receives:

- `material-client-preparation.json` and `material-client-runtime-dependencies.json`
- `material-client-report.json`
- `material-client-screenshots/01-geology-blocks.png`
- `material-client-screenshots/02-material-items-a.png`
- `material-client-screenshots/03-material-items-b.png`
- `material-client-screenshots/04-tank-fluids.png`

Success emits `MATERIAL_CLIENT_RENDER_PASS items=74 fluids=25 geology=41 quads=258 screenshots=4`. Failure emits `MATERIAL_CLIENT_RENDER_FAIL` with a failing JSON report when initialization progressed far enough to resolve its guarded output path. The parent must inspect runtime logs/report and actual screenshots before declaring a client pass.

This test does not certify server recipes, material progression, powered machines, world generation, survival balance, player UI interaction, multiplayer or absence of third-party network attempts. Those remain separate checks. No textures are synthesized, recolored or replaced for this fixture.
