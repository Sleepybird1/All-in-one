# Runtime launch preflight

Status: **ready for a guarded unattended run**. The exact CurseForge profile and test world are identified, and the installed CurseForge client exposes a profile-specific launch deep link. The remaining non-negotiable guard is visual UI recognition for selecting the world: the profile launch URI starts Minecraft but does not itself load a save.

This was a read-only preflight. Minecraft was not started, no world was opened, and no file in the live instance was changed.

## Exact target

| Property | Verified value |
| --- | --- |
| CurseForge profile name | `All in one` |
| Instance GUID | `8aa92192-8f46-4334-bcfd-95d63824efb5` |
| Minecraft | `1.21.1` |
| Mod loader | `neoforge-21.1.248` |
| Game ID | `432` |
| Live instance | `C:\Users\GodPC\curseforge\minecraft\Instances\All in one` |
| Intended world display name | `Industrial Colonies Runtime Test` |
| Intended world directory | `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\saves\Industrial Colonies Runtime Test` |
| World that must not be selected | `New World` |

The intended save has both `level.dat` and `level.dat_old`. At preflight time, `level.dat` was last written on 2026-08-31 at 13:20:24 local time. The CurseForge quick-play history also records the exact display name as a creative single-player world.

## Supported profile launch route

The safest supported route is to pass CurseForge its own `launch-game` deep link. Inspection of the installed client bundle found a `launch-game` handler that reads `instanceId` and numeric `gameId`, then invokes the client's launch-game service.

Use the installed executable explicitly so the run does not depend on the current Windows URL-protocol association:

```powershell
$curseForgeExe = 'C:\Users\GodPC\AppData\Local\Programs\CurseForge Windows\CurseForge.exe'
$launchUri = 'curseforge://launch-game?instanceId=8aa92192-8f46-4334-bcfd-95d63824efb5&gameId=432'
Start-Process -FilePath $curseForgeExe -ArgumentList $launchUri
```

The executable exists at that path, and prior CurseForge logs show successful launch requests for the same GUID. The resulting client has previously used:

`C:\Users\GodPC\curseforge\minecraft\Install\java\java-runtime-delta\bin\javaw.exe`

A reconstructed direct-Java launch is deliberately rejected. CurseForge supplies a dynamically authenticated account token, version libraries, natives, JVM flags, asset paths, and an instance-specific classpath. The prior log redacts the access token, so copying its command would be incomplete and brittle. It would also bypass normal launcher ownership of the profile.

### Important limitation

The `launch-game` URI launches the exact profile; it does **not** contain a world selector. The `--quickPlayPath` value seen in the Minecraft command line points to a history/output JSON file. It is not equivalent to `--quickPlaySingleplayer` and must not be treated as an auto-load command.

## Guarded unattended state machine

Record the current `logs\latest.log` last-write time and the current `javaw.exe` PIDs before dispatch. A new run must produce a fresh log session; markers from the previous successful run must not be mistaken for current state.

| State | Required evidence | Action / failure policy |
| --- | --- | --- |
| `PRECHECK` | Exact profile metadata and save directory exist; no Minecraft `javaw.exe` for this instance is running | Do not dispatch if the target is missing or already active. A generic unrelated `java.exe` is not enough to block. |
| `DISPATCHED` | CurseForge receives the deep-link argument | Start only the explicit CurseForge executable above. |
| `PROFILE_JVM_STARTED` | A fresh `latest.log` contains `ModLauncher running` with `--gameDir, C:\Users\GodPC\curseforge\minecraft\Instances\All in one` and version `neoforge-21.1.248` | Abort UI automation if the game directory or version differs. If process command lines are available, also require `-DCFInstanceId=8aa92192-8f46-4334-bcfd-95d63824efb5`. |
| `CLIENT_BOOTSTRAPPED` | Fresh log contains `Setting user:` and `Sound engine started`; Minecraft window is visible | These log lines show client initialization, not title-menu readiness by themselves. |
| `TITLE_READY` | Visual/OCR recognition of the Minecraft title screen and the exact `Singleplayer` button | Do not use a blind delay or blind coordinate click. Dismiss no unexpected dialog automatically. |
| `WORLD_LIST_READY` | Visual/OCR recognition of the single-player world list | Locate the row whose complete visible label is exactly `Industrial Colonies Runtime Test`. Do not select by row index because `New World` also exists. |
| `WORLD_STARTING` | Fresh log contains `Starting integrated minecraft server version 1.21.1`, then `Preparing spawn area` | If another world name appears, open the pause menu and perform the graceful save-and-quit sequence immediately. |
| `WORLD_READY` | Fresh log contains both `ServerLevel[Industrial Colonies Runtime Test]` and `VictorStarbird joined the game` | This is the minimum world-loaded criterion used by the existing acceptance validator. For quest/UI tests, additionally wait for FTB Quests client sync (`Read <n> bytes, <n> objects` and its translation-table message). |
| `SAVE_REQUESTED` | Minecraft pause screen is visibly recognized and the exact `Save and Quit to Title` control is visible | Activate that control once. Never close or kill the Java process from the loaded world. |
| `WORLD_SAVED` | Fresh log contains `Stopping server` followed by `ThreadedAnvilChunkStorage (Industrial Colonies Runtime Test): All chunks are saved` | Wait for this exact world marker; dimension-only save lines are insufficient. Confirm `level.dat` advanced and `level.dat_old` still exists. |
| `CLIENT_EXITED` | After returning to the title screen, a normal window close is issued; fresh log contains `[net.minecraft.client.Minecraft/]: Stopping!`; the target `javaw.exe` exits | Allow at least five minutes. Distant Horizons delayed the prior client exit by about 70 seconds after chunk saving. Do not force-kill on timeout. |

### World-selection interaction

1. Bring the Minecraft window to the foreground only after `CLIENT_BOOTSTRAPPED`.
2. Use screenshot/template or OCR recognition to find `Singleplayer`; click the recognized control.
3. Wait for the world list and identify the full exact label `Industrial Colonies Runtime Test`.
4. Select that exact row, then activate `Play Selected World` (or double-click only after the text match is confirmed).
5. Treat the log markers under `WORLD_READY` as authoritative. A window title ending in `- Singleplayer` is not sufficient; the same title can be present while paused or in the wrong save.

Minecraft is configured windowed (`fullscreen:false`), and the prior launcher command requested 1024 by 768. Coordinates may be derived relative to the detected client bounds only after visually confirming the target control. Minecraft/LWJGL controls generally are not exposed as normal Windows UI Automation child controls, so screenshot recognition is safer than blind Tab/Enter sequences.

## Safe save and close

The safe unattended shutdown sequence is:

1. Focus the confirmed Minecraft window.
2. Press Escape only if the pause screen is not already visible.
3. Visually recognize and activate `Save and Quit to Title`.
4. Wait for the exact world's `All chunks are saved` log line and verify the save file timestamp advances.
5. Wait until the title screen is visibly back.
6. Close the client normally with the window close command or Alt+F4.
7. Wait for the client `Stopping!` marker and the target Java process to exit.

Do not use `Stop-Process`, `taskkill`, forced window termination, or an Alt+F4 while the world is still loaded. If a modal, crash screen, wrong world, or unrecognized UI appears, stop automation and report the state; leave the process running rather than risking world corruption.

Suggested upper bounds are ten minutes for client bootstrap, ten minutes after the confirmed world-list click for world join, and five minutes for graceful client shutdown. A timeout is a blocker/report condition, not permission to kill the client.

## Post-run acceptance

After a fresh run has loaded, saved, and cleanly closed the intended world, run the project's read-only validator from the project root:

```powershell
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\validate_live_runtime_log.py
```

The validator defaults to `Industrial Colonies Runtime Test` and defines a fresh world join as the exact world string plus `joined the game`. The last existing runtime log predates current project changes and is evidence for the launch procedure only; it is not acceptance evidence for a later deployment.
It also requires the exact `debug.log` application records for
`SpaceTransitionHandlerMixin` on Cosmonautics' `SpaceTransitionHandler`,
`DeepSpaceInstanceMixin` on Cosmonautics' `DeepSpaceInstance`,
`WaterWheelBlockEntityMixin` on Create's `WaterWheelBlockEntity`, and
`WindmillBearingBlockEntityMixin` on Create's `WindmillBearingBlockEntity`.
Owned Mixin apply/injection failures remain fatal. These records prove that the
orbital policies were injected into their installed targets; ship-transition
authorization, the Mars per-occupied-ship route check, managed-offworld Ender
Chest denial, and denied-dimension 0-RPM behavior remain separate in-world
tests.

## Evidence paths

- Profile identity: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\minecraftinstance.json`
- Instance GUID mirror: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\.curseclient`
- Minecraft options: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\options.txt`
- World save: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\saves\Industrial Colonies Runtime Test`
- Quick-play history: `C:\Users\GodPC\curseforge\minecraft\Quickplay\8aa92192-8f46-4334-bcfd-95d63824efb5.json`
- Latest runtime evidence: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\logs\latest.log`
- Detailed runtime evidence: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\logs\debug.log`
- Captured stdout: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\logs\stdout-logs.txt`
- Launcher/JVM audit: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\logs\instance_audit.txt`
- Installed CurseForge executable: `C:\Users\GodPC\AppData\Local\Programs\CurseForge Windows\CurseForge.exe`
- Installed client bundle containing the deep-link parser: `C:\Users\GodPC\AppData\Local\Programs\CurseForge Windows\resources\app.asar`
- Prior loaded-world screenshot: `C:\Users\GodPC\Documents\Codex\2026-08-16\ok\mc-world-loaded.png`
- Prior pause-menu screenshots: `C:\Users\GodPC\Documents\Codex\2026-08-16\ok\minecraft-printwindow.png`, `C:\Users\GodPC\Documents\Codex\2026-08-16\ok\minecraft-window.png`
- Project acceptance specification: `LIVE_RUNTIME_ACCEPTANCE.md`
- Runtime validator: `tools\validate_live_runtime_log.py`
- Deployment checklist naming the correct and incorrect worlds: `tools\deploy_live_pack.ps1`

## Remaining blockers and assumptions

- No launch or UI action was performed during this preflight, by design. The deep-link syntax is supported by the installed client code and corroborated by prior successful GUID-specific launcher logs, but this exact invocation was not executed in this task.
- There is no reliable log-only marker for "the title screen is ready." Visual recognition is required before selecting `Singleplayer` or the world row.
- No current Windows URL-protocol registration is assumed; the recommended command invokes the known executable explicitly.
- The existing quick-play history identifies the desired save but does not prove the `launch-game` URI will auto-select it. Automation must still select the exact world name.
- Unexpected UI, authentication prompts, launcher updates, crashes, or timeouts require a report and human decision; they must not trigger blind clicking or force termination.
