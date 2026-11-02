# Isolated full-client launch preparation

Prepared and exercised 2026-09-09. The separately approved full-client retry passed actual stitched-sprite, baked-model and GPU inventory-render checks: 40 approved cubes plus Gold Flakes. See [RESULTS.md](RESULTS.md) for runtime evidence, the preserved first failure and scope limits.

The new stage is `isolated-runtime/client-render-20260909-030821-140`. Its 239 physical mod JARs are the corrected candidate plus every original staged mod, including the six recoverably held server-test exclusions (Sodium, Iris, ETF, EMF, Euphoria Patcher and Distant Horizons). Every copied JAR was SHA-256 compared to its source. Candidate SHA-256 is `ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546`.

No existing worlds, launcher/account files, tokens, options, resourcepacks or shaderpacks were copied. No server stage or live-pack inputs were changed by this harness. The client uses a disposable offline development identity; it is not configured to join a server. Actual runtime may write its own options/config/cache files inside the client stage; those copied/generated settings are not claimed immutable. After the successful run, all 239 staged JARs still matched their preparation SHA-256 values.

## Verified preparation

- ModDevGradle 2.0.144's existing `client` run uses the unmodified NeoForge 21.1.248 userdev `config.json` run template (`forgeclientdev`). The exact cached userdev SHA-1 is checked by the preparation script.
- The installed asset index 17 and all 3,911 indexed objects were present with expected sizes. Their root is read-only input. `downloadAssets` is disabled explicitly because NeoForm's downloader does not obey Gradle `--offline`.
- Previously acquired, official-checksum-verified DevLaunch 1.0.2 and exact bundled epoll artifacts are copied into the new stage's narrow offline Maven repository. No download occurred.
- `runClient --dry-run` passed in 26 seconds and selected `clientSmoke`, not production main classes.
- `prepareClientRun auditClientSmokeDependencies` passed in 10 seconds. All 109 runtime files resolved, including LWJGL 3.3.3 Windows natives, text-to-speech, ModLauncher, BootstrapLauncher and DevLaunch. Evidence: `client-prepare-offline.log` and `client-runtime-dependencies.json` in the stage.
- Generated `build/moddev/clientRunProgramArgs.txt` selects `forgeclientdev`, local assets and the dummy `GeologySmoke` identity. Client VM arguments do not enable `java.awt.headless` or `neoforge.gameTestServer`.

## Required Connector development input

The first approved launch exposed a supported-development-configuration omission: Connector 2.0.0-beta.17's `ConnectorTransformerEnvironment.getCleanClassLookup()` reads `System.getProperty("connector.clean.path")` when FML is not in production mode, requires that path to exist, and loads clean classes from it. Without the property it throws `Could not determine clean minecraft artifact path`.

Both the current init and reusable template now set `connector.clean.path` to the exact cached **named, unpatched Minecraft 1.21.1** artifact:

`../gradle-user-home/caches/neoformruntime/intermediate_results/rename_3f859ecde63343fee4a46c3fa3b7c05c19de9bf2_output.jar`

The invocation refuses a missing artifact or a SHA-256 other than `BC811B3368CA4E056672AB7425682247A68AB72210F14B0BA68B91EEAE040CE3` (18,887,912 bytes). Cached NeoForm provenance identifies 1.21.1-20240808.144430, a clean client/server merge with `--inject false`, and AutoRenamingTool output. The input merge, mappings and version-manifest hashes were verified against that provenance, and the original client download matches the cached official manifest SHA-1. Do not substitute the raw obfuscated client download, a NeoForge-patched runtime, or the similarly named cached **1.21** rename artifact. This fixes the invocation only: no Connector or other mod JAR was modified or removed.

## Commands

Run from the project directory with the already-installed JDK and workspace Gradle cache:

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21'
$env:GRADLE_USER_HOME='C:\Users\GodPC\Documents\Codex\2026-08-16\ok\work\gradle-user-home'
$clientInit='.\isolated-runtime\client-render-20260909-030821-140\client-smoke.init.gradle'
.\gradlew.bat --offline --no-configuration-cache --console=plain -I $clientInit prepareClientRun auditClientSmokeDependencies
.\gradlew.bat --offline --no-configuration-cache --console=plain -I $clientInit runClient --dry-run
```

The preparation commands above do not launch Minecraft. After explicit user approval for the full isolated client outside the sandbox, the operator/root task separately ran `runClient`; the corrected retry passed and the addon closed the client normally after saving its screenshot/report. Gradle `--offline` is dependency control, not a runtime network firewall; third-party client mods may attempt outbound traffic. The successful run does not establish absence of network attempts.

## Addon contract

The invocation-only init binds addon `ic_client_smoke` to `clientSmoke` from `tools/client-smoke/src` and `resources`. Its compile-only IC dependency is the staged candidate JAR. The candidate remains loaded from `mods`, not production Gradle class directories.

- `ic.client.report`: stage `client-render-report.json`.
- `ic.client.screenshots`: stage `screenshots` directory.
- `ic.client.exitAfterSuccess=true`: the addon closes normally after screenshot/report persistence and a 20-second inspection interval. The preparation property alone does not implement shutdown.
- Heap ceiling 8 GiB; initial viewport 1280×720. No game world is preselected or copied.

The root task owns addon source and actual launch controls. Runtime evidence now verifies the 41 checked models/sprites and their inventory renders on this machine; preparation alone would not do so. This is not an in-world lighting, shaderpack, other-hardware, survival-economy or complete-mod compatibility certification.

For another new isolated copy, `prepare-client-smoke.ps1` defaults to a read-only plan; `-Stage` creates a new timestamped directory. It refuses an unexpected candidate or any count other than 239 unique JARs and never launches Minecraft.
