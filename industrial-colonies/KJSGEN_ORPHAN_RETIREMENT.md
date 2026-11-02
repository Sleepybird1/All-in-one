# KJSGen orphan-retirement migration

## Why this migration exists

The conservative three-way KJSGen merge intentionally never deletes a card
when it disappears from the managed fragment. That rule protects recipes made
or edited in KJSGen, but it also preserved several generations of obsolete
Industrial Colonies cards in the live `default` project.

The captured evidence set contains:

- 632 live recipe cards and 765 live removal cards;
- 402 recipe cards and 661 removal cards in the deployed managed baseline;
- the then-current managed source snapshot, whose exact hash and entry counts
  remain recorded in the ledger provenance;
- 230 live recipe UIDs absent from both active sets, of which 223 are proven
  source-owned and seven are recipe-ID-null user cards; and
- 104 live removal UIDs absent from both active sets, all proven source-owned.

The source-controlled ledger is
`progression/kjsgen_orphan_retirement_ledger.json`. It contains exactly 223
recipe cards and 104 removal cards. The seven recipe-ID-null user cards are
listed only as excluded provenance; they are not retirement entries.

## Ownership proof

A recipe card entered the ledger only when its UID was inactive in the captured
evidence snapshot, its `recipeId` started with `industrial_colonies:`, and its
complete canonical JSON value exactly matched a card in a backed-up managed
baseline.

A removal card has no owner namespace, so admission required the UID to be
inactive in that same captured evidence snapshot and a complete-card historical
managed-baseline match. One removal predates the managed sidecar: the exact AE2
printed-silicon removal UID and value are pinned in the ledger builder, and the
builder requires that unchanged value in every available historical project
snapshot. It is the only permitted exception.

Each ledger entry stores:

- the UID;
- a SHA-256 of the complete canonical card;
- useful recipe/removal identity fields;
- the historical evidence rule and artifact reference; and
- the complete expected card.

This is intentionally stronger than checking a recipe ID or output. Object-key
order is normalized, but every field, scalar type, nested value, and array order
must otherwise match.

## Fail-closed sanitizer

`tools/sanitize_kjsgen_orphans.py` accepts a staged merged project, the current
managed fragment, the ledger, and an audit-report path. For every ledger UID it
does one of four things:

1. If the UID is absent, it records an idempotent `alreadyAbsent` result.
2. If the complete staged card exactly equals the ledger card, it schedules the
   card for retirement.
3. If the UID has become active again, it is preserved only when the ledger,
   current managed fragment, and staged project contain the same complete card
   in the same array. This handles an exact recipe or removal card legitimately
   returning to active ownership without weakening the retirement proof.
4. If the value changed, occurs in the wrong array, occurs more than once, or
   has an ambiguous/drifted active overlap, it blocks the whole operation.

All checks finish before the output is written. A blocked run writes only the
requested audit report and leaves the staged/output project unchanged. A clean
in-place run uses an atomic same-directory replacement. If every ledger entry
is already absent, an in-place run does not rewrite the file at all. Unrelated
recipes, user cards, list order, and project metadata are preserved.

Run the sanitizer immediately after `merge_kjsgen_project.ps1` and before any
validator consumes the staged merge:

```powershell
& $pythonCommand `
  .\tools\sanitize_kjsgen_orphans.py `
  --staged .\build\generated\kjsgen\default.json `
  --managed .\pack-kjsgen\default.managed.json `
  --ledger .\progression\kjsgen_orphan_retirement_ledger.json `
  --report .\build\generated\kjsgen\orphan-retirement-audit.json
```

The command updates `--staged` in place only after a clean plan. `--output` can
be supplied to test against a separate file. Exit code 3 means an ownership or
edit conflict; deployment must stop and surface the audit rather than changing
the ledger or deleting the card.

The ledger is a one-time migration artifact. Do not broaden it from whatever
happens to be in a future live project. Its evidence build command is:

```powershell
python .\tools\build_kjsgen_orphan_retirement_ledger.py `
  --live "C:\path\to\All in one\kjsgen\projects\default.json" `
  --baseline "C:\path\to\All in one\kjsgen\industrial_colonies_sync\default.managed.baseline.json" `
  --managed .\pack-kjsgen\default.managed.json `
  --history-root "C:\path\to\All in one\_industrial_colonies_backups" `
  --output .\progression\kjsgen_orphan_retirement_ledger.json `
  --check
```

## Verification

Run the focused suite with:

```powershell
python -m unittest tools.test_sanitize_kjsgen_orphans -v
```

It covers exact recipe/removal deletion, preservation of user cards and
metadata, edited-card conflict with no staged write, exact active-reactivation
preservation, rejection of incomplete or drifted active overlap, wrong-array
and ledger-hash mutations, idempotence, the exact 223/104 ledger counts, all
complete-card hashes, and the seven excluded user recipe cards.
