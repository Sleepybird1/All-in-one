# Surface ores and hematite — September 22 direction

October10 user correction supersedes the extreme hematite rarity below: hematite/rich hematite should not be rarer than gold. The proposed5%continent presence was rejected; no replacement percentage is approved. See CONTINENT_RESOURCE_DISTRIBUTION.md. Older text remains historical; do not implement its extreme-rarity target over this correction.

Status: user design recorded; runtime implementation and recipe migration NOT_RUN. This updates the geology design without claiming installed behavior.

## Distribution

- Only iron, copper and coal may form independent small surface patches of 1–3 ore blocks.
- All other ores must occur in their own proper veins. Those veins may intersect the surface; this is not a ban on exposed ore veins.
- Hematite veins on Earth must be incredibly rare and very large. Hematite is explicitly allowed in random 1–3-block pockets, including surface traces under the iron exception, but their frequency must be massively reduced from the current rate. Do not remove these pockets. Exact pocket frequency and large-vein frequency/size remain to be selected independently.
- Rock veins should be massive, with the accepted noisy boundaries and native-rock gaps retained. A mine should occupy a substantial deposit, not acquire an ore coating around its walls.
- High-yield magnetite and hematite veins remain possible. Hematite's extreme Earth rarity applies to its distribution, including its high-yield deposits.
- More common hematite on Mars is a tentative future proposal, not an approved numeric distribution or an installed change.

The surface patch rule concerns generated ore blocks. Pickup prospecting rocks are a separate existing feature; do not silently remove their clues. Audit independent underground micro-deposits and placers against the instruction that other ores belong to proper veins before implementation; do not assume the surface trace function is the only relevant path.

The latest clarification preserves tiny hematite pockets alongside the extremely rare massive veins; rarity must be enforced in each generation path, not achieved by deleting the pockets.

## Proposed ordinary rock-item recovery

| Ordinary rock item | Latest user target |
| --- | ---: |
| Magnetite | About 1 mB per item |
| Hematite | 25 mB per item |

The user explicitly supports buffing hematite yield to compensate for rarer pockets. Retain the preceding 25 mB ordinary-item target; no additional numeric increase was specified.

At the existing 100 mB per ingot, these correspond to roughly 100 magnetite items or four hematite items per ingot. These are rock-item targets, not output per generated block: block drops and processing routes must be accounted for separately.

The historical basic/improved ordinary-rock values are 3/8 mB for both minerals. Exact application of the new targets to basic versus improved processing remains unresolved. Keep recipe edits deferred for visual review; do not silently set every route to the same output or erase advanced recovery benefits. Preserve the separate rich iron route (25 mB basic, 100 mB TFMG), rich drop identity and unrelated material values unless explicitly revised. With hematite's proposed ordinary recovery equalling the current rich-iron basic yield, the eventual recipe review must explain the rich-grade benefit through drops and/or processing rather than inventing an unapproved multiplier.

## Implementation acceptance queue

1. Audit surface traces, underground micro-deposits, placers and competing ore generators; enforce the iron/copper/coal surface whitelist and 1–3 block limit while preserving legitimate vein outcrops.
2. Implement bounded massive-body generation and discovery before raising deposit sizes. Prove substantial ore volume beyond mineshaft walls and retain legacy saved geometry.
3. Select and verify extreme Earth hematite rarity without common trace or rich-deposit bypasses. Keep Mars frequency tentative.
4. Prepare visually reviewable ordinary-rock recipe changes, with block-drop, rich-grade and advanced-route accounting. Native loading and recovery tests remain NOT_RUN.

Related: MINESHAFT_EXTRACTION_NODES.md, MASSIVE_VEINS_AND_MINESHAFT_SCALE.md and ORE_RECOVERY_BALANCE.md. Node-only-in-mine eligibility and rarer, widely separated mines remain required.
