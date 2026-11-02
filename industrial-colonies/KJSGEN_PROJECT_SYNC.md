# KJSGen project synchronization

KJSGen's Project screen reads `kjsgen/projects/default.json`. The generated
`kubejs/server_scripts/kjsgen_recipes.js` file is an export artifact and KJSGen
does not reconstruct a project by parsing that JavaScript.

Interactive approve/reject feedback is deliberately kept outside both files.
See [KJSGEN_RECIPE_REVIEW.md](KJSGEN_RECIPE_REVIEW.md) for the in-editor review
queue, stale-design fingerprints, and the review-only `approved recipes`
project.

The completed 2026-09-02 review is a deliberate exception to the normal
unmanaged-card preservation rule. Its 381 decisions are frozen in
`progression/recipe_review_acceptance.json`, and its clean deployment source is
`pack-kjsgen/default.reviewed.managed.json`. Use the reconciliation and
one-time deployment commands documented in `KJSGEN_RECIPE_REVIEW.md`; feeding
the current 844-card generated fragment directly into the conservative
merge would resurrect rejected designs and overwrite approved snapshots.

Any new or changed recipe that Industrial Colonies expects the player to edit
visually must therefore be represented in KJSGen's native recipe model in
`pack-kjsgen/default.managed.json`. The entry must use a stable UUID in `uid`, a
registered KJSGen `type`, native `slots`, and native `params`. Recipes whose
logic cannot be expressed by a registered KJSGen layout remain regular KubeJS
scripts and are not presented as editable visual recipes.

TFMG 1.2.0 Chemical Vat recipes use the custom
`industrial_colonies:tfmg_chemical_vat` visual type and the manifest compiler
type `tfmg_vat`. See [KJSGEN_TFMG_CHEMICAL_VAT.md](KJSGEN_TFMG_CHEMICAL_VAT.md)
for its exact slots, selector presets, codec boundaries, and validation rules.

The managed set is compiled from
`progression/managed_recipe_overhaul.seed.json` plus the installed recipe
catalog into `progression/managed_recipe_overhaul.json`, then into KJSGen's
native project format. It includes the encased manufacturing families,
TFMG-first electronics, AE2/ComputerCraft/Mekanism machinery, power and reactor
construction, and late megaproject components. Processing cards contain the
real exact-machine routing slots. Matching removal cards use installed source
recipe IDs; managed recipe cards have `replaceRecipe: false`, so exporting
never falls back to a broad output wipe.

The seed can list unavailable optional-integration definitions in
`disabled_recipe_ids`. Those definitions are excluded before dependency,
removal, and KJSGen compilation. The current list disables all six Create
Encased slicer tiers because their item registrations require Slice & Dice,
which is not installed; their stock-removal rules are therefore excluded too.

`tools/deploy_live_pack.ps1` runs `tools/merge_kjsgen_project.ps1` before it
builds its copy plan. The last deployed managed fragment is stored outside the
KJSGen project directory at
`kjsgen/industrial_colonies_sync/default.managed.baseline.json`, so KJSGen does
not mistake the sidecar for another editable project. The merge is intentionally
conservative:

- Live project metadata and unknown future metadata are preserved.
- Existing recipes and removal rules with unrelated UIDs are preserved.
- If only the managed source changed since the baseline, that change is applied
  in the same list position.
- If only the live KJSGen card changed, the live edit is preserved.
- If both sides changed to identical content, the card is already synchronized.
- KJSGen's omitted default `amount: 1000` fluid serialization is treated as
  identical to an explicitly stored 1000 mB amount.
- When live and source independently reach the same complete recipe design and
  differ only in explanatory `comment` text, the maintained source comment is
  applied. Ingredients, machines, shapes, parameters, and outputs must all
  match for this narrow reconciliation.
- If source and live changed differently, deployment aborts with the exact
  conflicting UID before either staged output is written.
- A managed entry with a new UID is appended.
- Removing an entry from the managed fragment does not delete it from the live
  project.
- An empty managed fragment is a byte-for-byte no-op.

That normal preservation rule previously accumulated retired source-owned
cards. The bounded one-time migration in
[`KJSGEN_ORPHAN_RETIREMENT.md`](KJSGEN_ORPHAN_RETIREMENT.md) removes only 223
recipe cards and 104 removal cards whose complete historical managed values are
recorded in a source-controlled ledger. It runs on the staged merge, fails
before writing on any edit or active-UID overlap, and leaves the seven
recipe-ID-null user cards untouched.

After that bounded cleanup, `tools/validate_staged_kjsgen_project.py` compares
every active managed recipe and removal to the staged project by UID and full
canonical value. It permits unrelated user cards and unfinished recipe-ID-null
drafts, while rejecting missing or edited managed entries, duplicate recipe
IDs/removals, and any second producer for an `exclusive_output` contract. This
check runs before the deployment copy plan can modify the live instance.

Before that merge, deployment runs the complete managed-recipe compiler
preflight. It checks the assembled manifest against the installed mod JARs and
static recipe catalog, deterministically rebuilds stale manifest/report files,
checks them again, then does the same for `pack-kjsgen/default.managed.json`.
Schema/compiler/dependency validation, installed item/recipe validation,
TFMG-first canonical-material validation, and nuclear-chemistry boundary
validation must all pass before a copy plan is allowed to touch the live
instance. `-PlanOnly` runs this same preflight and stages the conservative merge
under `build/generated`, but still performs no live-pack writes.

Python is discovered from `python`, `python3`, or the Windows `py -3` launcher.
Use `-PythonExecutable` when it is not on `PATH`. The recipe and runtime item
catalogs are discovered in nearby `outputs`/`exports` directories, or can be
provided explicitly with `-RecipeCatalog` and `-RuntimeItemCatalog`.

This makes `default.json` safe for recipes authored directly in KJSGen while
also allowing maintained recipes to appear in the same Project screen. Both the
merged project and next baseline are staged first. Normal deployment then backs
up, atomically copies, rolls back on failure, and verifies SHA256 parity for
both files. Unmanaged user recipes are never replaced.

The committed cards use KJSGen's native slot naming: compacting uses list input
keys such as `in0` with singular `output`; shaped recipes use singular `output`;
sequenced assembly uses singular `input`/`transitional` and list output
`output0`.

The visual project and generated recipe must have one owner. A recipe moved to
the managed KJSGen fragment must not also be emitted by a project-owned KubeJS
script, because exporting the KJSGen project would otherwise create duplicate
recipe definitions. KJSGen exports continue to target the user-owned
`kjsgen_recipes.js`, which the deployment script never overwrites.

On a client launch, Industrial Colonies now loads the merged `default` project
and invokes KJSGen's own exporter from the NeoForge client-setup work queue.
This happens after KJSGen registers its recipe layouts and code generators but
before a singleplayer integrated server can read `kubejs/server_scripts`.
KJSGen's marker-aware merge remains the only code that writes the script, so
handwritten content outside `// kjsgen:start ... // kjsgen:end` is preserved.
The existing assembler compatibility mixin still removes invalid/WIP cards
from the emitted batch and includes project removal cards. A one-shot callback
after KJSGen's initial client resource layout reload retries the export if
registry initialization was unexpectedly late.

Missing, invalid, or unreadable projects and exporter exceptions are logged
clearly and leave the main menu usable. The hook does not register on a
dedicated server. KJSGen remains a required `BOTH`-side dependency in mod
metadata, so the companion mod never reaches this integration with its API
absent.

KJSGen 2.0.5 saves removal cards in the project model but its stock exporter
forgets to pass them to the assembler. Industrial Colonies patches the
two-argument export path to call the existing three-argument assembler with
the project's removals. Removal cards are emitted once in the project's
default target file; a project containing only removals still creates that
default file. Other target files do not receive duplicate removal statements.

Run the merge regression test with:

```powershell
.\tools\test_merge_kjsgen_project.ps1
```

Run the staged ownership and orphan-retirement regression tests with:

```powershell
python .\tools\test_sanitize_kjsgen_orphans.py
python .\tools\test_validate_staged_kjsgen_project.py
```

Run the deterministic managed-recipe compiler checks with:

```powershell
python .\tools\test_build_managed_recipe_manifest.py
python .\tools\build_managed_recipe_manifest.py --check
python .\tools\generate_managed_recipe_overhaul.py --check
python .\tools\validate_managed_recipe_overhaul.py
```

Validate the removal-export compatibility patch with:

```powershell
python .\tools\validate_kjsgen_removal_export.py
```

Validate unattended startup export and marker preservation with:

```powershell
python .\tools\validate_kjsgen_auto_export.py
```

Validate the managed electronics cards and their installed source IDs with:

```powershell
python .\tools\validate_managed_electronics_slice.py `
  "C:\Users\GodPC\curseforge\minecraft\Instances\All in one" `
  --catalog "C:\path\to\ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt"
```
