# Disposable native material-processing acceptance fixture

Status: authored; compilation and Minecraft execution are pending the root agent's coordinated run. This document does not claim a runtime pass.

The addon is intentionally separate from production sources and the deliverable JAR. It loads the real staged candidate plus the stage's installed mods, exports the complete merged staged `default` KJSGen project before server-script loading, then examines the actual server recipe manager. The catalog is read dynamically using `ic.material.catalog`; additions to `processing/material_processing_catalog.json` do not require maintaining another recipe-ID list.

## Preparation and invocation

Use the newly prepared, approved disposable Lithosphere stage. Do not point this at the live instance, the historical geology world, or a stage still running Minecraft. First build and copy the intended production candidate and generated material KubeJS scripts/configuration into that disposable stage using the parent's existing preparation workflow. In particular, the full chemistry catalog must be generated: a physical-only catalog deliberately fails the mandatory Chromium, electrical and Tungsten checks.

Layer this init script **after** that stage's existing base init. The base init remains responsible for approved mod isolation, offline repositories, JVM/memory/logging settings and server configuration. This addon does not remove mods, change global configurations, set an EULA acceptance or launch anything by itself.

Example command shape (replace the stage and base-init placeholders with the actual prepared paths):

```powershell
& ./gradlew.bat --offline --no-daemon `
  -I '<prepared-stage-base-init.gradle>' `
  -I tools/material-processing-smoke/material-processing-smoke.init.gradle `
  -PmaterialStage='isolated-runtime/<prepared-lithosphere-stage>' `
  -PmaterialRevision='a1' `
  compileMaterialSmokeJava processMaterialSmokeResources
```

The parent can subsequently run `runGameTestServer` with the same init/property arguments, when coordinated and authorized. If another approved Minecraft process holds the already-generated, matching Minecraft compilation artifact, `-x createMinecraftArtifacts` can be used for this compile-only step; it must not be used to hide missing or incompatible artifacts.

Required Gradle properties:

- `materialStage`: an existing stage under this project's `isolated-runtime`, with a `mods` directory and exactly one current `industrial_colonies-*.jar` (version is resolved, not hardcoded).
- `materialRevision`: a fresh lowercase alphanumeric/hyphen suffix. Existing world data or a report causes a hard refusal before launch.
- `materialCatalog`: optional path override; defaults to `processing/material_processing_catalog.json`.

The init captures SHA-256 identities of the candidate, catalog and merged project at configuration time and rechecks them before launch. The GameTest rechecks the candidate/catalog and the pre-script export evidence. Runtime classes come from the staged candidate, not the main development source set. The addon gets only its own mod namespace and an exact copied NBT template under `data/ic_material_smoke/structure` in generated resources. Filtering uses the explicit `ic_material_smoke` template namespace to avoid selecting historical geology tests.

Outputs are confined to the selected stage:

- `material-processing-report-<revision>.json`
- `material-processing-export-<revision>.json` (complete merged-project export identities and card counts)
- `material-processing-worlds/world-material-<revision>/` (disposable default GameTest world; not a natural-terrain survey)
- The merged project's target `.js` files directly in staged `kubejs/server_scripts`, written by the native marker-aware exporter. The source project JSON is not rewritten.

The run logger emits exactly one final `MATERIAL_PROCESSING_SMOKE PASS` or `MATERIAL_PROCESSING_SMOKE FAIL` marker. The JSON records the candidate and catalog hashes, expected/verified recipe counts, per-section results, individual catalog problems and native sample counts. A recipe failure does not prevent independent sections from reporting their own findings.

## Export timing and stage-only safeguards

`StageProjectExport` registers common-safe `FMLLoadCompleteEvent.enqueueWork`, not a client event and not a late server-starting/reload listener. This intentionally runs after KJSGen's common initialization, which loads bundled layouts and fires `RegisterRecipeTypesEvent`. It reapplies the candidate's machine-centric definitions, then uses the installed `ProjectManager`, `CodegenRegistry` and `KubeJsExporter.exportProject` APIs.

Timing was checked against installed bytecode, rather than inferred from event names:

- KJSGen 2.0.5 `KjsGen.commonSetup()` invokes `JsonLayoutLoader.loadBundled()` and `RegisterRecipeTypesEvent.fire()`.
- NeoForge 21.1.248 `ServerModLoader.load()` synchronously runs common `load()` and `finish()` lifecycle dispatch, including load-complete queued work. Minecraft `Main.main` invokes this before creating the GameTest server/world packs.
- KubeJS 2101.7.2-build.368 `ServerScriptManager.createPackResources()` constructs the manager and invokes `reload()` during subsequent world pack creation; `loadFromDirectory()` reads server scripts there. KubeJS's load-complete callback handles startup post-init, not that server-script reload.

The init supplies the required `ic.material.requireStageRoot` JVM property. Export refuses to run unless the FML game directory and process directory both resolve to that exact existing stage, `neoforge.gameTestServer` is true and no server already exists. It rejects paths outside the stage, symbolic-link destinations, conflicting sanitized filenames, missing code generators, changed project hashes, changed/dropped card UIDs and mismatched removal-rule counts. Every destination is checked before the native exporter writes anything. All merged cards are exported, not just the scoped eighteen-card patch; other cards and text outside the default project markers are retained. The native merge may normalize line endings and boundary whitespace, which the preservation assertion explicitly allows.

`MATERIAL_STAGE_EXPORT PASS` logs the complete project identity/card count before server-script parsing, and each script logs its checksum. The separate export JSON is created without overwriting prior evidence; the later GameTest requires completed export evidence and unchanged project/script hashes. A timing, export or preservation failure aborts mod loading rather than continuing with stale scripts. This lifecycle path has been authored and inspected but still requires the coordinated runtime run to confirm its execution in the selected stage.

## Checks and limits

1. Every generated catalog recipe exists in the loaded manager, uses the expected registered serializer, and canonically encodes identically to a fresh native decode of its catalog definition. Item/fluid references and tags must resolve; native Create inputs/outputs and validation are checked. This catches stale stage scripts, dropped recipes, empty tags and changed machine constraints as well as invalid IDs.
2. No loaded recipe uses the `modernfoundry:alloy` serializer or recipe type. Casting/melting remain available.
3. The real `ExclusiveMillingRecipe` stays in Create's native MILLING family and accepts Ultramafic Rock. One hundred thousand seeded native `rollResults` calls enforce zero-or-one output, exactly one item on success, the configured recovery rate and conditional Os/Pt/Ir distribution. Registry-aware network round-trip, invalid count/weight/missing-rate decoding, and zero/full-recovery endpoints are also exercised.
4. Detached **native** Normal, Weathered Iron and Industrial Iron fan block entities supply real machine context. Chromium separation must reject the first two and accept Industrial Iron. A dropped item's negative cache must become retryable; an actual transported-item processing sequence must finish after its negative cache is cleared. Moving nearly-completed processing to a wrong fan must not complete it. Ordinary ungated washing must still work with all three fans. No production world blocks or existing entities are changed.
5. Generated electrical recipes decode to TFMG's native `VatMachineRecipe`, retain two electrode operations, lining, size and duration, and reference a real registered electrode operation. Aluminum, Magnesium and Lithium electrical routes are mandatory. An unpowered native electrode holder must be inoperable. Tungsten sintering must decode to IE's native Arc Furnace recipe with exact sized input/base time/total energy; enough powder matches, insufficient powder fails, the output is one canonical ingot and the native cache selects the intended recipe.
6. Active manual Cinnabar configuration validates, batching cannot be enabled, the canonical IE hammer is damageable and Roasted Cinnabar is registered. The separate native Cinnabar batch Mixing recipe requires no extra heat.

These are loaded-registry and direct-native-API acceptance tests. They are **not** a complete powered chemical plant, a fan airflow geometry test, an in-game real-player 60-second hammer/burner interaction, a balance/throughput survey, a manual UI test or proof of natural world generation. The existing pure manual/session tests cover interruption and one-at-a-time state transitions separately. Apart from exporting the already-merged staged project through its native exporter, no recipes, configurations, output quantities or production code are changed to make this fixture pass.
