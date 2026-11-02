# Material processing batch — implementation record

Status: implemented and installed as **0.5.0** on 2026-09-09, following native
recipe, Lithosphere A/B and full-241-mod client checks. See
[MATERIAL_PROCESSING_ACCEPTANCE.md](MATERIAL_PROCESSING_ACCEPTANCE.md) for exact
evidence and untested gameplay scope; the checklist below records the design
requirements, not a claim of a complete powered-factory/survival playthrough.

Authority: user's material-processing brief supplied 2026-09-09, plus the explicit
Lithosphere/WWOO compatibility repair request. Preserve approved V27 textures and live saves.
No new Allthemodium/Vibranium/Unobtainium recipes belong to this batch.

## Source ownership

- `tools/material_processing/`: readable recipe builder modules; installed native codecs.
- `processing/material_processing_values.json`: centralized editable values/timings.
- Generated catalog and processing script: deterministic build products, validated before delivery.
- New runtime helpers: manual Cinnabar, exact-machine fan cache correction, mutually
  exclusive PGM recovery. Existing Create tier binding remains authoritative.
- `LITHOSPHERE_COMPATIBILITY.md`: narrow world-generation compatibility scope.

## Acceptance required

- All 24 resource/industry families covered, with authentic process differences.
- Fixed metal amounts, remelting and crafting conversions have no value multiplication.
- Modern Foundry alloying absent; Mixer owns intentional alloys.
- Chromium requires Industrial Iron fan; reject normal/Weathered and allow retry after rejection.
- Industrial machines depend on Ti/W/electronics without requiring their own construction tier.
- Manual Cinnabar is one real-player operation, slow heat then damageable hammer.
- Exclusive crude PGM roll, Ni/Co asymmetric rich recipes, electrical Al/Li/Mg,
  hydrogen W, magnesium Ti, NC fuel handoffs, nonfuel graphite.
- No global sediment-to-gold shortcut; preserve exact cold-river sediment selection TODO.
- Fresh isolated current-mod-matrix recipe decode/game tests and terrain verification.
- Approved textures unchanged; source and candidate deployment changes auditable/recoverable.
