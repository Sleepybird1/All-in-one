# Scoped 0.5 material-processing / Lithosphere deployment

Status: **APPLIED on 2026-09-09** after native material a3, Lithosphere A/B r1 and fresh full-client `material-client-20260909-072449-528` all passed. Exactly four live targets were installed; the previous active 0.4.0 JAR was retired recoverably. [Deployment and recovery journal](<C:/Users/GodPC/curseforge/minecraft/Instances/All in one/_industrial_colonies_backups/material-lithosphere-0.5-20260909T112922.207472Z/deployment.json>) records `APPLIED` and plan SHA-256 `C55CAF6CAA6BF7A65A7271EA7651EDB05B0860E6ABF139BD5251C086BC074F82`. Installed candidate SHA-256 is `8DF80E5C7E4B447F651696A9383A1487B26F557A67D6263DEAFA3805BC675D91`. This is not a survival-playthrough or powered-factory certification.

The remaining sections document the guarded deployment mechanism and its original prerequisites, not an instruction to reapply into a changed live pack. The default command remains read-only; `--apply` requires the exact reviewed plan SHA-256. It never builds, launches Minecraft, exports a project, downloads dependencies, or copies a whole modpack.

## Exact install scope

The fixed live pack is `C:\Users\GodPC\curseforge\minecraft\Instances\All in one`. The default candidate stage is `work/industrial-colonies/isolated-runtime/geology-gametest-20260909-064550-754`.

| Live target | Source / operation |
| --- | --- |
| `mods/industrial_colonies-0.5.0.jar` | Exact accepted stage JAR; embedded geology, textures, recipes, and conditional WWOO compatibility resources travel in this JAR. |
| `kjsgen/projects/default.json` | Exact native-exported staged project: 19 scoped machine cards, 653 unrelated cards unchanged, old Radiance card retired. Existing removal cards stay identical; only the four explicitly allowed native-removal identities may be appended. |
| `kubejs/server_scripts/kjsgen_recipes.js` | The accepted native export's `default` marker block, spliced into the current live file. All bytes outside that block, including other projects and trailing whitespace, remain live-original. |
| `kubejs/server_scripts/zz_industrial_material_processing.js` | Exact accepted stage script containing the owned 299 recipes and compatibility policy. |

Exactly `mods/industrial_colonies-0.4.0.jar` is moved recoverably to the timestamped deployment backup. Its expected SHA-256 is `c053f1da65db73d8bd4158f8c082d51653efdbc6320de4d022e219fb0627f3b4`. Existing `.disabled`/`.bak` files are not active JARs and are not moved. All 240 third-party active JARs must still match the prepared full-pack inventory, including all six mods held out of the server-only test copy. They stay in the live client pack.

No saves/worlds, account/launcher files, other projects, resourcepacks, full config tree, defaultconfigs, test add-ons, test datapacks, old 0.4 artifacts, or server-subset mod inventory are installed. The helper does not enumerate saves. This is not existing-world migration or retrogen.

## Native export, config, and catalog handling

`StageProjectExport` already uses KJSGen's real native exporter against all 672 merged cards before server script loading. Its report must be `PASS`, bind the exact project/export bytes, retain all card UUIDs, and be identical to the pre-script export embedded in the passing material runtime report. The helper never regenerates this file itself and never replaces the entire live KubeJS directory. The candidate includes the legitimate legacy filling-slot compatibility repair for later native re-exports.

Live `default.json` must still equal the original captured SHA-256 `f2ac4d50a62da9926dc02da67c3c34d9b77032d3b1c4d11b9ea3d8ea4596a79c`. If the user edits a card after staging, deployment stops: re-merge and re-test instead of overwriting that work. The helper separately verifies all 653 unrelated card objects and their order, project options, existing removal objects, and UUIDs of the 16 replaced cards.

The catalog is build/test provenance, not an external runtime configuration. It is archived with the deployment evidence, not copied to an invented live config path. The script and catalog must match `material-stage-patch.json`, and the genuine runtime report must verify 299/299 recipes against the current catalog/candidate.

The candidate auto-initializes missing `config/industrial_colonies/worldgen/{settings,biome_families,deposit_families,oil}.json` and `config/industrial_colonies/processing/manual_cinnabar.json` from its bundled defaults. The helper verifies accepted stage values equal those defaults, and any existing live IC override must equal the accepted values semantically; otherwise it stops for review. It copies **no** config files. The WWOO `removeOres=true` config is retained: the candidate's narrowly scoped conditional built-in pack restores the 12 decorative definitions and retains WWOO lava policy.

Read-only config audit on 2026-09-09 found 418 live / 430 stage config files and two byte-identical defaultconfigs. Non-IC differences were development/startup artifacts: Mekanism adds `alphaWarning`, C2ME/ModernFix comment defaults differ, Moonlight adds `test_category`, Quark removes a client hotbar-animation setting, and several support files are generated. None is an install target. Existing WWOO, Lithostitched, Modern Foundry common, and TFMG common/server config bytes matched. The plan includes a fresh full config-difference inventory without changing any of it.

## Required evidence and read-only plan

1. Finish the exact candidate's material run. Supply its revision (currently `a3` is the observed 299/299 PASS; do not relabel that report if candidate bytes change).
2. Finish both normal-terrain Lithosphere request orders and native WWOO compatibility tests. Run the existing `tools/lithosphere-compat/validate-lithosphere-acceptance.ps1` separately, with an explicit fresh `-OutputPath` inside this stage. It verifies A/B comparison, candidate/preparation/noise provenance and all four report hashes. The deployment helper only consumes that existing receipt; it does not run the validator or invent an acceptance result.
3. Complete the full 241-JAR client check in its separate material-client stage. Supply `--client-stage`: the helper requires matching preparation/candidate/catalog/content, all physical JAR hashes, 41 geology models / 258 quads, 74 material item models, 25 fluids / 50 sprites, the applied Radiance branch, and four native framebuffer screenshot hashes and PNG dimensions. The client report must be `PASS`. This covers actual client rendering, **not** powered-factory or survival-playthrough certification.
4. Close Minecraft and every `java.exe`/`javaw.exe` process, including development Gradle daemons. The helper conservatively blocks apply if any remain. Its process inspection uses only image names and PIDs from `tasklist`; no command lines, access tokens, usernames, or process termination.

From the project directory, after those reports exist (replace the receipt filename with the actual validator output):

```powershell
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  tools/material_processing/deploy.py --revision a3 `
  --acceptance isolated-runtime/geology-gametest-20260909-064550-754/lithosphere-acceptance-r1.json `
  --client-stage isolated-runtime/material-client-20260909-072449-528
```

This prints the exact plan, input/output hashes, config differences, process inventory, blockers, and `planSha256` without creating any file. The plan includes the Lithosphere receipt, its canonical A/B comparison hash, both preparation identities, all bound report hashes, and client/full-pack manifest hashes. A missing/failed/mismatched report cannot become ready by merely passing `--apply`. Structural/path/hash violations fail closed. Symlinks/junctions in source, destination, or traversed folders are rejected. If process inspection is denied, dry-run reports `javaProcesses: null` and a diagnostic, never an empty list or ready status; apply stops. No permission bypass or process-check override is provided.

Only after reviewing that exact plan and obtaining deployment authorization, repeat the same command with `--apply --expected-plan-sha256 <printed-digest>`. Changing a source, live target, preserved config/script, or receipt changes the plan and invalidates that digest. There is no broad overwrite, force, skip-tests, or ignore-Java option.

## Backup / transaction / recovery

The apply operation creates only a unique `_industrial_colonies_backups/material-lithosphere-0.5-<UTC timestamp>` backup directory plus the four listed install targets. It verifies backups of every replaced file and the old JAR before installing. The catalog, preparation, material/export/terrain reports and acceptance receipt are copied into `evidence/`; `deployment.json` records the full reviewed plan, hashes, write journal and result. It then rechecks the complete plan and Java process state.

The journal records `INSTALLING` and retirement intent before the old active JAR moves into `retired/`. Immediately before that move and each payload write, the helper checks the expected original hash or absence again. Each new file is installed by an exact-parent temporary file and atomic replacement. Post-checks verify output hashes, all 240 unrelated active mod hashes, all config/defaultconfig hashes, and unrelated KubeJS files. Final `APPLIED` journal persistence is part of the protected transaction. A normal write/check failure restores the original targets automatically; failed new files are retained under `failed-new/`. Rollback refuses to overwrite any concurrent target edit with unexpected bytes and reports manual recovery instead. No backup is deleted.

An operating-system kill/power loss cannot make a multi-file transaction atomic. Before starting Minecraft, inspect `deployment.json`: only `APPLIED` is success. An interrupted `BACKING_UP`/write journal or `MANUAL_RECOVERY_REQUIRED` needs review. Close all Java processes, use the exact target/`before` entries and hashes recorded in that backup to restore the replaced project/export and old JAR, and recoverably move any newly installed 0.5 JAR/batch script aside. Do not copy an entire old config/modpack backup over the live instance. The helper intentionally has no broad automatic rollback command.

## Historical preparation validation and final application

The initial helper-only subtask syntax-parsed the source and inspected native project UID/removal layout, live baseline hashes, config differences and the active old-JAR target. Its first dry-run verified material a3 and Lithosphere r1 but correctly blocked because the client result and process clearance were not yet available. That historical subtask performed no install.

After the fresh 072449 client passed and processes were cleared, the parent reviewed and applied the exact final plan. The journal now records **APPLIED**; independent read-only post-checks matched all four installed target hashes. The active old 0.4.0 JAR is absent and its recoverable retired copy remains in the timestamped backup. The live pack retains 241 active JARs. Final scoped tests and installation are complete; the explicit manual-operation, powered-factory and placer-selection limits in `MATERIAL_PROCESSING_ACCEPTANCE.md` remain unchanged.
