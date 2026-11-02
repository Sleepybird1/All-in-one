# Induction Matrix completion audit

## Decision

**IMPLEMENTED, after Extreme Power Transmission and the four-cube ladder.**

The ten reviewed cards are now source-owned in
`progression/managed_recipe_overhaul.seed.json`. They were added only after the
complete four-cube storage ladder and Extreme Power Transmission repair were
implemented. The seven previously missing cell/provider assignments were
appended to `CR01 — High-Energy Distribution` without changing the thirteen
entries already assigned to that node.

The Induction Matrix is one functional multiblock, so all ten of its craftable
parts must be owned together. The current pack hardens casing, port, and the
Ultimate Cell while leaving basic through elite cells and every provider on
cheap stock routes. Those routes bypass the intended High-Energy Distribution
convergence.

The reviewed repair uses two manufacturing languages:

- 5x5 Mechanical Crafting produces structural casing in useful batches and
  ports from completed analog-grid regulation plus Ultimate Mekanism control.
- Encased compacting produces capacity cells and throughput providers. Basic
  parts use the Industrial Iron press; Advanced, Elite, and Ultimate use
  Weathered Iron.

Refined Radiance was removed from the proposal after independent phase review.
That press belongs to Nuclear Engineering, which is later than High-Energy
Distribution and would make the matrix circular or post-phase. Weathered Iron
is the installed High-Energy Grid manufacturing environment and is explicitly
present in `tier_recipe_environments.json`.

Cells consume Energy Tablets and the matching Energy Cube tier. Providers use
the matching control circuit and Universal Cable tier. Every tier consumes the
previous cell/provider, creating two clean, parallel upgrade lines. Advanced,
Elite, and Ultimate retain the installed recipes' four-to-one aggregation
semantics rather than silently reducing each upgrade to two predecessors.
Both Basic parts also consume the reviewed Induction Casing, so they cannot
bypass the protected-grid shell and become available back in Mekanized
Industry merely because their press and cube are older.

The basic lithium inputs are repeated tag slots. KJSGen supports counted item
inputs but not strings such as `8x #c:dusts/lithium`; repetition preserves the
installed lithium tag without producing an un-compilable card.

Seven formerly unassigned cell/provider items now belong to the internal
High-Energy Distribution assignment, so the whole family shares one physical
phase. This metadata change does not reactivate the discarded MineColonies
research gate.

All removals are the ten exact installed Mekanism IDs listed in
`INDUCTION_MATRIX_COMPLETION_AUDIT.plan.json`.

## Installed-recipe and data policy

Direct JAR inspection verifies the ten source paths, types, and counts. Casing
normally outputs four and the reviewed structural line intentionally outputs
eight; port remains two and every cell/provider remains one. The four cell
sources use `mekanism:mek_data`, which copies supported components. Create
Compacting cannot emulate that assembler, so cell upgrades are intentionally
lossy and must use drained cubes/cells with removable upgrades taken out first.
No energy is duplicated; the output cell starts empty.

Run `tools/validate_induction_matrix_completion_audit.py` against a freshly
assembled manifest to check the installed JAR and item catalog, exact source
ownership, absence of the three retired automatic owners, output counts,
Encased machine bindings, dependency IDs, assignment append order, 5x5
patterns, and KJSGen compilation. The validator includes twelve mutations;
`tools/test_induction_matrix_completion_audit.py` adds twelve focused unit
tests. The implementation was isolated-build verified at 332 managed recipes,
182 automatic recipes, 400 compiled cards, and 716 exact removals; shared
generated artifacts remain intentionally untouched for the authoritative
regeneration step.
