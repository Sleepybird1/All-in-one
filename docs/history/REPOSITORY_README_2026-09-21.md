# Industrial Colonies — shared working handoff

Last updated: 2026-09-21 by desktop Codex. Read this at the beginning of work; update it before a long operation, after a major result, and before switching between desktop and web. Keep history in COMMIT_CHANGELOG.md where available. No automatic pushes or game-launch commits.

## Current priority and next action

Current user direction: **work in gameplay order: world generation and survival through Andesite first; keep recipes deferred until visual confirmation**. The user explicitly authorized the September21 starting-table copper removal; keep other recipe candidates and deferred decisions intact.

Retained later-mechanics checkpoint v82: SPACE-12 moving wired control and disk restart passed. SPACE-13 awaits physical endpoint selection. Native oxygen, exact coverage, ration conversion/restart, sensor, airlock/vent/lock and manually enabled reserve power checks passed scoped reviews. M56 also verifies five suit/gas-tank fills with exact1000mB custody; M57 verifies finite4800FE motor/propeller drive and exhaustion. Four compatibility corrections remain staging only. Real owner/team commissioning and entity breathing remain unproved. Cannon native operation verification is complete: M14 casting, M47 all11 base-CBC incomplete families and M54 actual boring/disassembly/harvest. Missing addon loot remains a separate design decision. WORLD-15 footprint and natural mine access evidence is retained; broader world acceptance remains open. Preserve the established terrain, structure-spacing, ore-yield and machine-ownership rules. Production saves and gameplay files remain untouched; no automatic push.

## Latest recovered web work — reported, not independently verified here

- In “Verify item database and icons”, the user requested selectable Create Encased fan type, Fluid/Heat modes, and fluid selection. The web assistant reported committing editor/layout/registry scaffolding to main, with a hot-fluid tag. It explicitly said the physical Create FanProcessingType Java bridge remained unfinished. Do not treat the editor as working in-world processing.
- The user said they had made fireproof-brick and cast-iron-frame recipes; inspect and preserve those actual recipes.
- In “Branch · Update item catalog tabs”, the user reported a world-creation crash. The assistant attributed it to orphaned dimension data and a later KubeJS registry error. This diagnosis and current resolution still need actual log/code verification; do not delete namespaces based solely on chat history.
- In “Branch · Branch · Branch · Quantum Crafter AE2 Use”, the assistant reported 17 age tabs and provisional catalog classifications, with durable icon insertion unresolved. This is separate catalog work and not evidence that pack recipes or gates are implemented.

Read only recent relevant turns so far; this is not a full export or exhaustive reconciliation of every web chat.

## Verified desktop checkpoint

Overall fixed audit: **145/237 complete (61.2%); 92 remaining**. Native section: **62/68 (91.2%); 6 remaining**. Space section: **13/24 (54.2%); 11 remaining**. World section: **12/15 (80.0%); 3 remaining**. Progression section: **23/79 (29.1%); 56 remaining**. High queue: **4/12 master rows complete in this pass (33.3%)**. These are verified desktop counts, not a percentage of newly recovered web work. Do not credit chat claims as completed master tasks.

H12 powered BSCCO processing and formation-loss cleanup passed with a staging-only cleanup candidate, independently reviewed against the H10 orphan-hole failure. Exact two-dust custody and real laser charging were verified. Survival acquisition, process restart and production integration remain NOT_RUN. R19 remains the previous consolidated gameplay bundle; H12 is additional scoped evidence, not an installed release.

## Repository and evidence locations

The actual pack repository is **Sleepybird1/All-in-one**, branch main. Its local checkout is the CurseForge “All in one” instance. The desktop source workspace “Industrial Minecraft Modpack” is a separate local Git repository with industrial-colonies/ source and historical audit evidence. Do not assume these are the same checkout or overwrite one with the other.

Desktop authority: industrial-colonies/MASTER_TASKS.json, MASTER_TASK_LIST.md, AGENTS.md, applicable design documents and MORNING_REPORT.md. Raw execution evidence is local-only unless deliberately published. A web session missing these files must report that limitation rather than invent their contents.

The GitHub plugin is connected. A missing remote in the separate desktop workspace does not mean GitHub is disconnected. Local README edits do not become visible to the web until deliberately synchronized; no push is automatic.

## Working rules and checkpoint fields

Checkpoint DURING the running task, not only at the end of a chat or task. Before a long operation, after each meaningful edit/test outcome, and whenever the next action or blocker changes, update README and the action log and amend the current local unpushed checkpoint with explicitly selected files. Preserve prior failures and results in the log even when amending Git history. Never include unrelated staged files. Never amend a pushed/shared commit: check remote refs/publication state first, and create a new local checkpoint when publication is uncertain. No automatic pushes. Do not checkpoint each game-generated file or poll; checkpoint meaningful recoverable progress.

Use Medium for a bounded ordinary audit; High only for a demonstrated hard dependency or native failure. Park unchanged blockers. Preserve accepted ownership and 100 mB ingot / 1000 mB block / 10 mB nugget accounting. No bulk uploads, mod upgrades, production-save edits or automatic deployment.

At each meaningful update record: current task; exact files/commit if available; completed actions; tests actually run; NOT_RUN checks; blockers; and the next executable action. Log an operation as IN_PROGRESS before it starts so interrupted work is recoverable. A change in environment is not evidence of successful completion.

Current operation: v93 Medium background massive-vein study COMPLETE6/6(100%); overall145/237(61.2%), world12/15(80%) unchanged. 22 pre-pruning saved layouts; detached chunk-bounded prototype;3,370,665 assertions;393,667 full-piece voxel visits all inside envelopes. Normal-body CPU fell45.9% in offline sample with unchanged positions; wall-time tails vary under background load. Supply comparison, preview and High integration handoff in workflow/early-survival/massive-vein-study. Native reference radius8 and lower-world clipping measured; config/cache/discovery integration remains. No Minecraft launch, live gameplay edits, installation or push; installed JAR hash unchanged. Next High bounded descriptor discovery/generation-phase integration, then native fresh-world tests when suitable. NOT_RUN: native massive veins, final lifetime acceptance, deployment.

## Chat provenance

- Verify item database and icons: 6aad0add-e6b0-83e9-a66a-477de7c9462f; latest user survival request and preceding fan-editor turns read.
- Branch · Update item catalog tabs: 6aacdda6-1380-83e9-a586-92ac82d00a51; latest three turns read.
- Branch · Branch · Branch · Quantum Crafter AE2 Use: 6aac6ea9-b180-83e9-8b99-25109dda3540; latest three turns read.

## Historical project notes

The following entries are retained history, not the latest installed-version or audit status.


The active working source is [industrial-colonies](industrial-colonies/). It was copied from the prior "Design industrial Minecraft modpack" task on September 9, 2026.

Installed: Industrial Colonies 0.5.2 in the CurseForge "All in one" instance. Material-processing recipes, Lithosphere compatibility, approved geology assets and historical documentation are preserved in the source copy.

September 10: [pre-semiconductor progression](industrial-colonies/design/PRE_SEMICONDUCTOR_IMPLEMENTATION.md) is installed. It updates 41 recipe cards, establishes Weathered structural manufacturing and Copper entry equipment, and retires competing early processors. Both native tests and all 299 material-processing recipes passed. Semiconductor recipes remain unchanged. The [progression and machine-ownership rules](industrial-colonies/design/PROGRESSION_MACHINE_OWNERSHIP.md) supersede conflicting historical assumptions; later-tier work remains outside this completed scope.

Current update: [mineshaft ore connections](industrial-colonies/MINESHAFT_VEINS.md). Mineshaft frequency stays unchanged; each new vanilla mineshaft receives one connected ore working. Standalone veins continue independently and do not create mineshafts. Build and all six native tests passed, including 128 unchanged vanilla layouts and an accessible placed ore face. The previous JAR was backed up; saves were untouched.

[Cave exploration traces](industrial-colonies/CAVE_TRACES.md) and [collectible surface clues](industrial-colonies/SURFACE_ROCKS.md) remain from 0.5.1. No universal cave-to-vein guarantee is imposed. Restart Minecraft and explore newly generated chunks. Do not mistake the historical source documents' original absolute paths for this active working directory.
