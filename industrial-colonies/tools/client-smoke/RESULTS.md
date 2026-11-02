# Full-client geology rendering acceptance

**PASS — 2026-09-09.** The approved isolated full-client retry loaded the complete 239-JAR input roster and rendered all 40 approved custom rock/ore cubes plus the Gold Flakes placer block through Minecraft's real item renderer. This is GPU-render evidence, not an image-generation or offline contact-sheet substitute.

## Evidence and measured coverage

All runtime evidence is under `isolated-runtime/client-render-20260909-030821-140`:

- `client-render-report.json`: `status: PASS`, 41 unique model IDs, 40 approved cubes, one placer block, 120 rendered frames.
- `screenshots/industrial-colonies-actual-client-render.png`: actual framebuffer capture, 1280×720, 232,687 bytes. Root visually inspected the complete sheet: all approved cubes and labels are visible with no missing-texture appearance.
- `client-render-run2-20260909.log`: line 7427 contains `IC_CLIENT_RENDER_PASS cubes=40 placer=1`; line 7449 records `BUILD SUCCESSFUL in 4m 23s`. Root observed process exit 0, approximately 264 seconds overall including startup and accessibility onboarding. This is not a render-time benchmark: the report's actual 120-frame measurement interval was about 2.09 seconds.

The addon waited for the ordinary title screen and completed resource reload; it did not dismiss onboarding/authentication/error screens. Accessibility onboarding required operator interaction in this disposable client before the checks could begin. The user's separate existing client was not the test target. After saving the screenshot and final report, the addon retained the view for 20 seconds and then closed normally.

The report records LWJGL `3.3.3+5`, NVIDIA GeForce RTX 4090/PCIe/SSE2, OpenGL `4.6.0 NVIDIA 610.88`. The loaded mod-ID count was 336 (not the physical JAR count; nested/aliased modules and the test addon are distinct). The runtime log records a created `8192x8192x4` blocks atlas at line 7239.

For every checked block, the addon asserted a non-missing baked block model, a non-missing item model, nonempty baked quads, no missing quad sprite, the expected stitched sprite dimensions, and a non-missing item particle sprite. All 41 item models reported GUI-3D rendering. Each approved cube had six baked quads; the three-part Gold Flakes model had 18 (258 total). Spodumene Rock correctly retained its separate top, side and bottom sprites.

Bertrandite's explicitly approved **1254×1254** source was retained at that exact stitched-sprite size. All other checked block sprites were **16×16**. No recolor, resize or geometry change was made for the test.

## Input preservation and first-run correction

After the successful retry, an independent SHA-256 check found **239 of 239 staged JARs unchanged** against `client-preparation.json`, with zero missing, extra or mismatched JARs. The six originally held server-only test exclusions were all present in this new client stage: Sodium, Iris, ETF, EMF, Euphoria Patcher and Distant Horizons. They were not removed to obtain this client pass.

The unchanged production candidate hash is:

`ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546`

The first approved run, preserved in `client-render-run-20260909.log`, failed before geology rendering after about 85 seconds because Connector's development launcher lacked `connector.clean.path`. Its exact installed bytecode documents this property. The correction only added that invocation setting and a pinned clean-artifact hash guard to the client init/template; it did not patch/remove mods or change production code. [LAUNCH_PREPARATION.md](LAUNCH_PREPARATION.md) records the clean named Minecraft 1.21.1 artifact and verified provenance. The second run has its own log, so the original failure evidence remains intact.

JAR preservation does **not** imply all copied stage files stayed immutable: Minecraft and mods wrote disposable options/config/cache/log files normally. No existing saves or launcher/account files were copied, and this task did not deploy the candidate to the live pack.

## Mipmap note and remaining limits

The log contains pre-existing texture-size mip warnings: TFMG `diagonal_cable_block` (24×24) limits mip level 4→3, then Create Metallurgy `slag_tiny_bricks` (225×225) limits it 3→0 (lines 3180–3181). Those warnings do not name Bertrandite or another new geology texture. The atlas later logs `8192x8192x4`; these records alone should not be treated as a certification of every sprite's effective mip quality. The approved high-resolution Bertrandite was not changed merely to suppress warnings. Distance filtering, in-world lighting and shaderpack appearance were not exercised by this inventory-render test.

This pass is bounded to the checked geology/placer models on this GPU with the full staged input roster. It does not certify every unrelated mod, eliminate existing recipe/resource warnings, measure whole-world performance, validate survival economics, test multiplayer, or prove absence of outbound network attempts. The user explicitly approved this full-client run outside the sandbox; Gradle `--offline` controls dependency resolution, not mod traffic.

## Evidence hashes

| Runtime evidence | SHA-256 |
| --- | --- |
| Screenshot | `DE54FDD4122D303A1C281E94F4DA143FCEE250662DC60EE07702E96210C2E8AB` |
| Render report | `C4F06D6EF30D90EA149FF9D6BA0A63DDA7CC195709616E8647211DC01BC8234C` |
| Successful retry log | `49FE827C786A241FD601A4D873CF01518825A1AB1FC9285982D223913A5E23DD` |

These PNG/JSON/log files are generated runtime evidence, not newly authored texture assets or authored-source inventory entries.
