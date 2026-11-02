# Isolated geology GameTest smoke run

Overall foundation task status is 100%; acceptance passed and final handoff hashes reconcile. Corrected normal-terrain A/B, all-profile/all-quality controlled placement, starter traces/diamond-depth regression, native oil compatibility and full 239-JAR client component rendering now pass. The exact final JAR passed seven required tests in 9.662 seconds; the whole final launch exited normally in 94 seconds. Historical candidate/configuration identities remain distinguished from that final run and the earlier full client. See `WORLDGEN_FINAL_ACCEPTANCE.md` for current results and the first combined test-fixture/selector failure history. No EULA file or live-pack/save change was made.

## Latest additional acceptance

The separate full client stage restored all six held originals and retained 239 hash-identical staged JARs. After setting Connector's supported clean-Minecraft artifact path, it passed actual baked-model, stitched-atlas and GPU rendering checks for 40 approved cubes plus placer. The original 1254-square Bertrandite sprite loaded; the native 1280×720 screenshot was inspected. A 123-case controlled production placement suite then passed all 24 families × four qualities, associated branches, protected cells and micro placement. Native TFMG oil generation/scanning/finite extraction also passed. These checks did not change the candidate or any global production rule; each addon is development-only. Detailed evidence and limitations are in `tools/client-smoke/RESULTS.md`, `tools/controlled-geology/RESULTS.md` and `tools/oil-smoke/RESULTS.md`.

## Latest result: corrected normal-terrain order regression passed

The corrected natural A/B evidence used the 1,695,174-byte candidate, SHA-256 `ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546`, preserved in `backups/diamond-boundary-fix-20260909/`. Original A/B tests found a real Galena race with cross-chunk vanilla dirt/gravel decoration. The fix places owner-only minerals after AIR carving and before FEATURES dependencies complete. No decorator, texture, generation rate or replacement tag was removed/changed. The final build separately bounds tiny diamond neighbors at Y=-20; only `GeologyFeature.class` differs, with all assets/data and other classes unchanged. Its exact identity and combined regression are in `WORLDGEN_FINAL_ACCEPTANCE.md`.

Fresh `terrain-a-fixed1` and `terrain-b-fixed1` worlds use actual Tectonic noise settings and observed RU biomes. All three natural formations match exactly under reversed requests: Copper 2,957 actual/83 rich; Lead 1,467/87; Zinc 1,210/29. Both five-test suites, all smoke markers, staged candidate source, shutdown and exit 0 were verified. The addon requested 14 target chunks per world; Minecraft generated a larger dependency halo. Test elapsed was 13.564/9.183 seconds; whole launches 294/222 seconds, not geology-only benchmarks.

Evidence: `terrain-run-a-fixed1-20260909.log`, `terrain-run-b-fixed1-20260909.log`, their two JSON reports and `terrain-comparison-fixed1.json` under the documented stage. `WORLDGEN_TERRAIN_ORDER_REGRESSION.md` preserves the original mismatch, exact mechanism, fix and limits. The test-only Java source/fixture/launcher are documented under `tools/terrain-smoke/`; none is packaged as an extra production mod. Run A has a Spark world-info sampler warning after passing tests during shutdown; no claim of a warning-free full pack is made.

## Historical result: all four required geology GameTests passed

After the Distant Horizons failure below, the user explicitly answered **"Continue going"** to its temporary exclusion from the disposable GameTest copy. The root agent moved `DistantHorizons-3.2.0-b-1.21.1-fabric-neoforge.jar` recoverably to `excluded-gametest-incompatible-mods`, separate from the five previously approved rendering exclusions. Its preserved size is 30,207,268 bytes and SHA-256 is `D6A7A963F794501678113E2545D8B25C90E123EF6B9256BB5716907D059E1EF5`; the decision is recorded in `gametest-exclusions.json`. No further gameplay mod was excluded.

The next attempt, `server-gametest-exclusion-run4-20260909.log`, exited 1 after 52 seconds before any test. Rocketnautics/Cosmonautics `DeepSpaceData.getInstance` line 70 dereferenced its missing `deepSpace` dimension on the first server tick (fatal log lines 4134–4137). Its tick callback does not call the existing missing-dimension guard or consult a configuration toggle. Minecraft's GameTest startup selects the flat world preset and bakes it against an empty dimension registry, omitting this standalone mod dimension.

The root agent therefore added only a disposable test datapack at `worlds/geology-smoke-world/datapacks/ic-gametest-dimensions`. It extends the test's `minecraft:worldgen/world_preset/flat` with the exact existing `rocketnautics:deep_space` LevelStem from the installed Cosmonautics JAR: its original void-flat generator, type and settings. All three vanilla flat-preset dimension objects and the added existing dimension object were checked for semantic identity against their original archive entries. `gametest-dimension-fixture.json` records this fixture. It invents no resource or generator, patches no mod, and is not included in the candidate JAR or production worldgen.

`server-dimension-fixture-run5-20260909.log` supplies the actual pass evidence:

- Line 3890: the `rocketnautics:deep_space` dimension is initialized.
- Line 4077: four tests start.
- Line 4080: `GEOLOGY_SMOKE registry PASS`, with code source explicitly naming the isolated `mods/industrial_colonies-0.4.0.jar`.
- Lines 4081–4084: loot/placer, required geology mixin applications, config/datapack, and packaged-asset checks all report `PASS`.
- Lines 4086–4087: **4 GAME TESTS COMPLETE in 674.4 ms; All 4 required tests passed.**
- The server shuts down cleanly; line 4148 reports `BUILD SUCCESSFUL in 1m 3s`, and the process exits 0.

**Historical result: 4 of 4 required GameTests passed**, candidate SHA-256 `0815A85BAE9FAD529207D90DF5ECA2CE40535CA6A82494EB1149A1B4EF85AF33`. At that point normal terrain remained untested; the later regression above now supplies bounded evidence with the corrected candidate. These four checks never established a clean audit of every pack recipe, client rendering or an unchanged 239-JAR launch. This world and its logs remain preserved.

## Historical result: Distant Horizons GameTest incompatibility

The user answered **"Continue"** to the explicit request to exclude client-only rendering mods from the disposable server-test copy and rerun. The root agent moved five JARs recoverably from that stage's `mods` directory to `excluded-rendering-mods`; the live installation was untouched. The exact retained files and independently checked SHA-256 values are:

- `sodium-neoforge-0.8.13+mc1.21.1.jar`: `575D187B15328D7BDDD8A9B1BEE64333C22C14735F5780EC49EAC0CD5503C08D`.
- `iris-neoforge-1.8.14-beta.1+mc1.21.1.jar`: `60D5F8BF52F25E9986440F4A4270A6BD986D9CFF994510E1108AC1547063B314`.
- `entity_texture_features_1.21-neoforge-7.1.jar`: `B2E396543C678B8378A2D5557A0CD3D24790364BFF7E96EDAF17921112D6176B`.
- `entity_model_features-3.2.4-1.21-neoforge.jar`: `84C22F2BE06EE6BFAB265A443E075225878BBA9F408843030DC6DE3152E9DEDB`.
- `EuphoriaPatcher-1.9.3-r5.8.1-neoforge.jar`: `9FF48C18CB5FD3425A6C15B16CE16656D6419FDB695E662D9A3CBE5604C40563`.

These were evidence-driven rendering exclusions, not blanket removal of mods with optional client-class warnings. Iris's entry point explicitly targets `Dist.CLIENT`. Entity Model Features declares a mandatory client-side ETF dependency and adds resource-pack custom entity models. No further required dependents on ETF/EMF or Euphoria were found in remaining top-level mod metadata. Create, Sable, Supplementaries and other gameplay mods were retained.

The staged rendering-exclusion attempt history is:

| Captured log in the stage | Rendering JARs excluded at that attempt | Actual result |
| --- | --- | --- |
| `server-render-exclusion-run-20260909.log` | Sodium, Iris | ETF's `ResourceLocation` mixin tried to load client `Screen` on `DEDICATED_SERVER`; exit 1 in 22 seconds. |
| `server-render-exclusion-run2-20260909.log` | Sodium, Iris, ETF, EMF | Euphoria Patcher failed construction on client `ClientLevel`; Gradle misleadingly returned 0 / `BUILD SUCCESSFUL in 37s`, but the log contains a fatal mod-loading report and no tests. This is a failed smoke test. |
| `server-render-exclusion-run3-20260909.log` | All five listed above | Distant Horizons cast `GameTestServer` to `DedicatedServer` during `ServerAboutToStartEvent`; exit 1 in 59 seconds. |

The latest fatal exception is at run3 lines 3862 and 3898–3899: `ClassCastException` in `com.seibel.distanthorizons.common.AbstractModInitializer_neoforge.lambda$onInitializeServer$1`, source line 151. Cached 3.2.0-b bytecode confirms that `onInitializeServer()` unconditionally registers this event listener. `NeoforgeMain.subscribeServerStartingEvent` registers a HIGH-priority `ServerAboutToStartEvent` listener and directly passes `event.getServer()` to it. The lambda's first operation is `checkcast DedicatedServer` (offset 4), before `initConfig()` (offset 11), with no GameTest guard. Turning off LOD rendering, distant generation, or server networking does not guard this cast. No supported configuration/system-property skip for this hook was found in the inspected entry point, initializer, event wrapper or configuration.

Distant Horizons is not merely a client rendering mod in this build: its Fabric metadata explicitly has `environment: "*"` and both client/server entry points, its NeoForge metadata includes `side = "BOTH"`, and its code registers server networking/lifecycle behavior. The otherwise present legacy-looking `clientSideOnly` metadata field must not override that direct evidence. No remaining top-level JAR metadata declares a required Distant Horizons dependency; nevertheless excluding it was a new test-configuration decision, not covered by the rendering-only scope. At this historical stage, `DistantHorizons-3.2.0-b-1.21.1-fabric-neoforge.jar` remained in `mods`, unchanged. No hook patch, config bypass, client-library injection or further exclusion had yet been applied. The later separate user approval and recoverable exclusion are recorded above.

**Result of that historical attempt: 0 of 4 GameTests executed, no `GEOLOGY_SMOKE` success markers, no runtime pass.** The disposable `worlds/geology-smoke-world` directory existed after that startup; this was not evidence that tests executed. No `eula.txt` existed in the stage. The 234-JAR disposable configuration retained candidate SHA-256 `0815A85BAE9FAD529207D90DF5ECA2CE40535CA6A82494EB1149A1B4EF85AF33`. The required separate approval for a test-only Distant Horizons exclusion was subsequently given, as recorded above.

## Historical approved full-pack run: Sodium service failure

After the previously disclosed escalation risks, the user explicitly answered **"Run them"**. The tool accepted the same isolated full-pack GameTest command with elevated execution. This is a new, authorized attempt; the earlier auto-review rejection is historical, not the current permission blocker. Its captured output is `isolated-runtime/geology-gametest-20260909-001051-895/approved-run-20260909.log`.

The approved run resolved the prior sandbox `AccessDeniedException` bootstrap problem. The log records ModLauncher starting at line 809, Sodium's graphics bootstrap invocation at line 821, and `java.lang.NoClassDefFoundError: org/lwjgl/Version` at line 822. It exited with code 1 after 10 seconds (`BUILD FAILED`, line 883). The stack identifies `SodiumWorkarounds.bootstrap` → `PreLaunchChecks.checkEnvironment` → `checkLwjglRuntimeVersion` → `isUsingKnownCompatibleLwjglVersion`; this is a client rendering dependency absent from the headless server distribution, not an observed Industrial Colonies geology failure.

Read-only cached-class inspection confirms that FML `ImmediateWindowHandler.load` invokes `GraphicsBootstrapper` services before its client/server launch-target check and before consulting `EARLY_WINDOW_CONTROL`. Sodium 0.8.13's bootstrap unconditionally checks LWJGL, probes graphics adapters and initializes workarounds before its own early-window setting check. Therefore disabling the splash screen alone does not prevent the failing service. Skipping a single version check would still leave client/native graphics probing and is not established as a valid server-compatible remedy.

**Result of that original full-pack attempt: 0 of 4 GameTests executed; no `GEOLOGY_SMOKE` success markers; no runtime pass.** The same 239-JAR staged pack was retained at that point, with candidate SHA-256 `0815A85BAE9FAD529207D90DF5ECA2CE40535CA6A82494EB1149A1B4EF85AF33`. No exclusions or additional client runtime libraries had yet been applied. The user subsequently authorized the rendering-only exclusions and retries recorded above; those are different test configurations, not unchanged full-pack passes.

## Historical attempt: bootstrap filesystem-access failure

The staged candidate was refreshed after the initial preparation record, terrain-order fix and final diamond-boundary fix. Its current SHA-256 is `5A4CCD0BA37629225EE88996281FCA7F1A1B704E9E1EE5DC712ECB363EEFFFBA` (1,695,276 bytes). The original `preparation.json` retains its historical initial candidate hash; it must not be presented as the final candidate record. The full-client preparation hash likewise remains historical; only the candidate JAR was later refreshed, with the other 238 JARs unchanged.

All three offline preparation workarounds below succeeded, and the supported DevLaunch entry point began execution. BootstrapLauncher then exited with code 1 at `java.util.Optional.orElseThrow`, `cpw.mods.bootstraplauncher.BootstrapLauncher.run` line 210 / `main` line 69, called by `net.neoforged.devlaunch.Main` line 57. Cached BootstrapLauncher 2.0.2 bytecode maps that line to an empty `ServiceLoader` lookup for `java.util.function.Consumer` in its newly constructed bootstrap module layer.

Read-only diagnostics verified all 67 generated legacy-classpath files exist. The original `modlauncher-11.0.5.jar` SHA-1 is `B8F0D49294F733FDB6173931B263553E943DC950`; it contains `BootstrapLaunchConsumer.class`, and its module descriptor explicitly provides `java.util.function.Consumer` using `cpw.mods.modlauncher.BootstrapLaunchConsumer`. The missing provider was therefore not evidence of an absent dependency or a reason to replace its implementation.

The diagnostic flag `bsl.debug=true` was added to the existing isolated init and reusable harness. The root agent's subsequent captured BSL output reported `java.nio.file.AccessDeniedException` while processing essentially every classpath JAR, including Gson, ModLauncher and the physically staged epoll artifacts. BootstrapLauncher catches these metadata/JAR-access `IOException`s and skips the affected JARs; with the ModLauncher consumer skipped, its final service lookup has no provider. This established that earlier failure as filesystem/sandbox access during bootstrap, before application registry/data/mixin execution. The later authorized run passed this point.

No GameTests ran and no `GEOLOGY_SMOKE` success markers were produced in that earlier attempt. Its diagnostic did not itself authorize filesystem ACL changes, firewall changes, altered launcher classes, dropping mods, or unsandboxed execution. The subsequent user-authorized attempt is recorded separately above with its own outcome.

**Historical status before the user's later approval:** the root agent explicitly requested an escalated run of the same isolated full-pack GameTest command and disclosed possible third-party mod outbound activity. Auto-review rejected that request because running the full third-party pack outside the sandbox could have broader filesystem and outbound-network side effects. No unsandboxed runtime occurred at that stage, and no retries or workarounds were attempted until the user subsequently gave explicit approval. The later accepted attempt and its Sodium failure are recorded above. Static/build checks remain distinct from the uncompleted runtime tests.

## Supported headless route

Use the project's NeoForge ModDevGradle `gameTestServer` run, not the CurseForge client or ordinary `runServer`. The cached NeoForge 21.1.248 patched sources establish:

- `net/minecraft/server/Main.java` selects the GameTest server when `neoforge.gameTestServer=true`.
- `net/minecraft/server/Eula.java` uses `SharedConstants.IS_RUNNING_IN_IDE || GameTestHooks.isGametestServer() || readFile()`. Its explicit NeoForge comment describes automatic EULA handling for GameTest CI. The harness uses that supported development path; it does not set `eula=true` or create an acceptance file.
- `GameTestHooks.isGametestServer()` requires a non-production loader and the GameTest system property. ModDevGradle supplies the development loader.
- `GameTestServer` uses `NO_SERVICES` and terminates with its failed-required-test count. This is a bounded CI test rather than an unattended public server.
- Ordinary `--initSettings` explicitly skips `ServerModLoader.load()`, so it is not a valid registry/datapack acceptance test.

These sources were read from the cached `sourcesAndCompiledWithNeoForge_da578f3daa04e03e3d7bae3cc0f73e66f794b43c_output.jar`. ModDevGradle 2.0.144 `RunModel` exposes the gameDirectory, loadedMods, programArguments and systemProperties settings used by the preparation script.

## What is tested

`GeologyGameTests.java` defines four required tests under the Industrial Colonies namespace:

1. All 40 approved block/item registry bindings, 20 low-yield and 16 rich memberships, pickaxe tags, absence of low-yield `c:ores` membership, the placer item/block and the resource tab.
2. Forced application of the noise-vein, placed-feature, fossil-overlay and (when Quark is present) fairy-ring mixins; actual StructureManager accessor use; loaded master config validation; all host/rich/associated block IDs; decoded configured/placed regional_geology features; every configured biome ID.
3. Exact self-drops for rocks/rich ores, one Diamond for Diamond Ore, one Gold Flake for the placer occurrence, and placer support/collision behavior. A pack global loot modifier that unexpectedly changes these outcomes is a genuine test failure to investigate.
4. Packaged block/item/state JSON and all 42 PNG decodes, including original 1254-square Bertrandite and three Spodumene maps. This is a software/headless asset check, not proof of client GPU atlas/rendering correctness.

The tiny owned `data/industrial_colonies/structure/geology_smoke_empty.nbt` is a clean 3×3×3 empty test arena. The cached vanilla resources have no literal `minecraft:empty` test structure; their named bastion 'empty' pieces contain jigsaw connectors. An owned template keeps the enabled test namespace narrowly scoped without running unrelated Minecraft/default-namespace tests. It introduces no geological resource.

## Prepare without launching

After the root build includes the final test class and NBT template, from the project directory:

```powershell
& .\tools\prepare_geology_gametest.ps1
```

Default behavior is a read-only plan. It rejects a stale JAR missing the blocks, tests, template, deposit data or mixin config. The inspected pack has 239 JARs, totaling roughly 1.07 GB.

To stage later, without starting Java:

```powershell
& .\tools\prepare_geology_gametest.ps1 -Stage
```

`-Stage` creates a new timestamped `isolated-runtime/geology-gametest-*` directory. It physically copies 238 installed JARs plus the rebuilt candidate (replacing the installed Industrial Colonies version by mod ID), and selected config/script/data directories. It never copies saves, account/launcher files, logs, options, resourcepacks or natives. It uses no symlinks or hardlinks. Stale `config/industrial_colonies/worldgen` overrides are excluded so candidate defaults are tested. The live source files remain untouched.

The preparation JSON records the candidate hash and exact path. No existing staging directory is overwritten. Normalized text config/scripts were checked for absolute references back to the live pack path; none were found at preparation time.

## Run only after explicit dispatch

The stage tool prints two commands. First perform the offline task-graph check (`--dry-run`) using the generated init script, then the real `runGameTestServer` command only when runtime dispatch is authorized.

Use `--offline --no-configuration-cache --console=plain`. The init script redirects the existing GameTest run into the isolated directory, clears development `loadedMods` so the rebuilt candidate is discovered from its isolated `mods` folder, restricts tests to Industrial Colonies, requests 6 GB maximum heap, sets `java.awt.headless=true`, and passes `--nogui`. Its new test world belongs entirely to the staging directory. The registry test logs the loaded GeologyBlocks code-source URL; confirm it names the staged candidate JAR, not an old live JAR or project output directory.

The initial task-graph dry run passed. The first actual preparation stopped before Minecraft launch because NeoForm's own `download-assets` command attempted an asset-index fetch despite Gradle `--offline`; the network sandbox denied it. The harness now supplies `offline-assets.properties` to `prepareGameTestServerRun.assetProperties` and disables only `downloadAssets` in its dedicated init script. This is an explicit replacement for a preparation input, not a fabricated successful download. Cached ModDevGradle 2.0.144 bytecode confirms that `DownloadedAssetsReference.loadProperties` requires only `assets_root` and `asset_index`, and that `PrepareRunOrTest.writeProgramArguments` reads this input for every run type.

The installed asset root is read-only: `C:/Users/GodPC/curseforge/minecraft/Install/assets`, index `17`. Preparation checks that all 3,911 indexed objects exist with their indexed byte sizes; it does not rehash all object contents. Installed index SHA-1 is `6AE5EB70FE411FACBB5C6C66003475C07A251A76`, which differs from the cached 1.21.1 manifest's `ae4f2779919ee343d3d98445f9a3ae1dc6542bc9` despite the same 449,557-byte size. This substitution is for headless registry/datapack tests, not a claim that the installed client assets exactly match that historical manifest. No live asset is modified or copied, and no asset download is permitted.

If offline run preparation reports another missing cached dependency, stop and report it: do not remove `--offline` or download automatically. The ordinary build currently has many mod APIs as `compileOnly`; launching it without the isolated mod directory is not a full-pack test.

The next offline preparation failure was uncached `io.netty:netty-transport-native-epoll:4.1.97.Final`. Both exact classifier artifacts already exist inside the cached official `minecraft_1.21.1_server.jar`: `META-INF/libraries/io/netty/netty-transport-native-epoll/4.1.97.Final/`. `tools/prepare_offline_epoll_repo.ps1` copies only these two unchanged JARs and their identical embedded upstream Maven POM into the stage's `offline-maven` repository. The init script filters this repository to that single module. SHA-1 matches the cached Mojang manifest: `linux-x86_64` = `54188f271e388e7f313aea995e82f58ce2cdb809` (38,954 bytes), `linux-aarch_64` = `5514744c588190ffda076b35a9b8c9f24946a960` (40,427 bytes). Their contents are native Linux `.so` files and metadata, with zero Java classes; the already-cached `netty-transport-classes-epoll` and other Java dependencies are retained. Nothing is excluded, re-versioned, downloaded, or substituted. This fixes preparation input availability; successful runtime resolution still requires the actual dispatched test.

The next preparation blocker was the absent standalone `net.neoforged:neoforge:21.1.248:moddev-config@json`. The exact cached `neoforge-21.1.248-userdev.jar` already contains the original 10,239-byte `config.json`, including its `gameTestServer` run. The harness verifies JAR SHA-1 `DAB61062B17C39EB246328576AE1BCBD59EE780B` and sets `prepareGameTestServerRun.runTypeTemplatesSource` to that local JAR. Cached ModDevGradle `PrepareRunOrTest.loadUserDevConfig` explicitly supports `.jar` input by reading its `config.json`; no fake standalone artifact, transformed metadata, or download is needed. This preserves the original server launch target and module/JVM configuration. The live installation and Gradle caches remain read-only.

`net.neoforged:DevLaunch:1.0.2` was genuinely absent from both Gradle caches and installed CurseForge libraries. ModDevGradle requires its `net.neoforged.devlaunch.Main` wrapper for the supported run; it was not removed or reimplemented. A separately approved, narrowly scoped official NeoForge HTTPS acquisition of only its JAR, POM, Gradle module metadata, and remote SHA-256 sidecars was therefore required. That dependency acquisition is separate from the network-denied Minecraft test process. The stage exposes the artifact through a local repository filtered only to `net.neoforged:DevLaunch`, with Gradle module metadata preferred as upstream requests.

Future preparation is still fully offline: it validates all three local artifacts against the retained SHA-256 sidecars, checks exact module coordinates and the original entry-point class, then physically copies them to the new stage. The default source is the first stage's `offline-maven/net/neoforged/DevLaunch/1.0.2` directory; use `-DevLaunchSourceDirectory` for another already acquired local copy. Missing artifacts or checksums cause an explanatory failure, never an automatic download. A saved sidecar check detects local inconsistency; provenance remains the separately approved official acquisition and its recorded hashes.

Verified official acquisition SHA-256 values: JAR (3,352 bytes) `366ADC4E95AB9B32C8E33B9F449529C8937C6FC021EE0C6B25419EA2BB703740`; POM (753 bytes) `49BA05392F1BF4A513DA8CE72377230EEC261B6E13A019B6DF526DD22D2CBC30`; Gradle module metadata (2,662 bytes) `30A811979EC04FCCBD1F78D4B1C387913ACD08C52EBD0C97F87DB08B0E61FDDC`. All match the retained remote sidecars; module metadata declares no further dependencies.

Run through the existing hidden/sandboxed command environment. If a background process wrapper is needed, use `Start-Process -WindowStyle Hidden` and redirect output; never open an interactive Minecraft window. Prefer the self-terminating GameTest process over a persistent dedicated server that needs forced termination.

## Network and compatibility limits

`--offline` constrains Gradle resolution, not arbitrary network traffic by third-party mods. Run only under enforced outbound-network denial if the task requires no network. Do not modify global firewall settings or launcher/account state. The server-properties stub is loopback-only, uses port 0, disables query/RCON/status and authentication, and does not create a publicly reachable server; those settings do not substitute for outbound sandboxing.

All 239 installed JARs are kept initially, including client-oriented Sodium/Iris/map/menu/audio mods. Some may be safely ignored on SERVER; others may cause genuine side-loading failures. Do not silently remove such JARs and claim an unchanged full-pack pass. Record the failing mod/target, then obtain a scoped decision before preparing a documented server-compatible subset.

A GameTest run uses a flat test arena. It proves mod load, injection application, registry/data compatibility and bounded block behavior, not real Tectonic/RU deposit geometry, spacing performance or visual terrain appearance. Those need separate controlled fresh-world tests.

## Acceptance evidence

A successful run must have all four required tests passing, exit code zero and the `Game test server shutting down` marker. Require the positive `GEOLOGY_SMOKE` markers for registry, required geology mixin applications, config/datapack, loot/placer and packaged assets. Confirm the registry marker's code-source URL points at the staged rebuilt JAR.

Inspect fresh staging `logs/latest.log`, `logs/debug.log`, captured Gradle output and any test XML. Reject owned Mixin apply/injection failures, missing registry entries, resource/loot decode errors, or a successful-looking process that ran zero tests. Preserve failure logs in the workspace. A timeout is not permission to force-kill an unrelated Java process.

The verified run-5 pass recorded above meets these bounded smoke criteria. It does not certify normal-terrain generation, client rendering or every recipe in the pack.
