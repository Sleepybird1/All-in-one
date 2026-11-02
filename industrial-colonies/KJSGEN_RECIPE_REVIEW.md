# KJSGen recipe review queue

Industrial Colonies adds a non-destructive review layer to KJSGen's normal
visual editor.  It is intended for rapidly reviewing the managed overhaul
without encoding feedback in chat messages or mutating recipe cards.

Only recipe UIDs present in the deployed managed baseline are reviewable. This
keeps drafts and unrelated user cards out of the queue. The visible card is
always the card being reviewed.

## Controls

- **Approve** records the current card, updates its snapshot in the KJSGen
  project named `approved recipes`, and selects the next pending card.
- **Reject** opens an opaque, blocking reason dialog over the editor. It offers
  eight frequent audit phrases plus custom text. Enter submits custom text,
  Escape cancels, and clicks outside the dialog cannot reach the recipe editor.
  A save failure keeps the dialog and typed reason open. Rejecting a card that
  was previously approved also removes its old approval snapshot.
- The common phrases preserve the special `default_recipe` and
  `ring_of_items` ledger codes and include wrong machine, cost, tier,
  electronics, shape/material, and **item should be disabled / not craftable**
  feedback.
- **Previous Recipe** follows actual viewing history and stops at the beginning;
  it never wraps to the final card. **Next pending** advances without deciding.

The main review bar has a reserved footer below the KJSGen editor. It does not
cover recipe code, machine controls, item slots, or editor buttons at smaller
GUI scales.

The `approved recipes` project is a visual archive. The companion export mixin
forces that project to export an empty recipe batch, so browsing it cannot
create a second producer for every approved output.

## Persistence and stale approvals

Review decisions are stored separately from both KJSGen project cards and the
managed baseline:

```text
kjsgen/industrial_colonies_sync/default.recipe_reviews.json
```

Each decision stores the recipe ID, UID, reason/note, and a SHA-256 design
fingerprint. The fingerprint covers the visual recipe type, recipe ID, slots,
and parameters. Comments, target files, and generated UIDs are excluded.

If any ingredient, operation, machine, grid shape, loop count, or output is
changed later, the fingerprint no longer matches. The old decision is retained
for context but its effective state becomes **stale/pending**, so the changed
recipe is shown for review again.

The sidecar never changes `default.json`, never calls KJSGen's dirty-state
path, and never participates in the managed three-way project merge.

## Reading feedback from source tools

Use the read-only report tool to compare the exact live cards that were
reviewed with the currently generated source cards:

```powershell
python .\tools\recipe_review_feedback.py `
  --reviews "C:\path\to\instance\kjsgen\industrial_colonies_sync\default.recipe_reviews.json"
```

Add `--json` for machine-readable output. A review made against an older live
card is reported as stale instead of approving a different source design.

## Completed review reconciliation

The first full review was closed on 2026-09-02. Its durable authority is
`progression/recipe_review_acceptance.json`, which freezes all 381 exact cards
and decisions (141 approved and 240 rejected) before the live project is
cleaned.

Run `tools/reconcile_kjsgen_review_batch.py` to combine that completed review
with a newly generated managed source. The policy is fail-closed:

- the exact approved snapshot wins over a same-ID or same-output source card;
- an unchanged rejected design is removed;
- a genuinely redesigned rejection returns as pending;
- a genuinely new recipe enters the pending queue;
- recipe IDs, UIDs, concrete outputs, and removals must remain unique.

The reconciled source is `pack-kjsgen/default.reviewed.managed.json`. The
matching exclusive-output audit view is
`progression/reviewed_ownership_manifest.json`, and the complete classification
report is `progression/recipe_review_reconciliation_report.json`.

After the initial live files have been cleaned, regenerate or check those two
active artifacts directly from the frozen acceptance (the removed rejection
cards no longer need to remain in the live project):

```powershell
python .\tools\apply_recipe_review_acceptance.py `
  --acceptance .\progression\recipe_review_acceptance.json `
  --previous-reviewed .\pack-kjsgen\default.reviewed.managed.json `
  --next-managed .\pack-kjsgen\default.managed.json `
  --next-manifest .\progression\managed_recipe_overhaul.json `
  --output-reviewed .\pack-kjsgen\default.reviewed.managed.json `
  --output-ownership-manifest .\progression\reviewed_ownership_manifest.json `
  --check
```

The current clean batch contains 813 managed cards and 1,224 exact removals:

- 141 approved;
- 141 redesigned cards whose old rejection is stale;
- 531 new/unreviewed cards;
- zero unchanged rejections, drafts, or unmanaged cards.

Six pending Create Encased slicer cards and their six native-removal rules were
retired after runtime verification showed that the entire slicer family only
registers when the optional Slice & Dice mod is installed. The current pack
does not install Slice & Dice, so keeping those cards would abort KubeJS recipe
loading on nonexistent item IDs.

Do not use the normal conservative three-way merge to perform this cleanup.
That merge intentionally preserves unmanaged cards. The one-time
`tools/deploy_reconciled_review_batch.ps1` command pins every reviewed input,
backs up the live project, approved archive, baseline, review ledger, and
generated script, then atomically installs the project, approved archive, and
baseline together. The review ledger is preserved so the 141 redesigned cards
retain the user's notes and appear as stale rather than losing their history.

The exact staged and predecessor deployment snapshots live under
`progression/review-batches/20260902/`. Their manifest pins every file hash, so
`gradlew clean` cannot erase the reviewed deployment inputs. The deploy command
also verifies those snapshots against the canonical acceptance, reconciliation,
ownership, and reviewed-managed source files before touching the live instance.
