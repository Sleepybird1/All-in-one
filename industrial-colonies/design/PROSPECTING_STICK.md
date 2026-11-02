# Temporary prospecting stick — September 23

Status: DESIGN STAGED, implementation NOT_RUN / NOT_IMPLEMENTED. User requests a temporary prospecting stick giving only whether the checked spot contains a vein. This takes priority over new TFC-style ground-rock artwork. Do not claim a working item exists from this specification.

## User-required behavior

- A stick is the temporary prospecting tool.
- Report vein presence or absence only; no ore identity, grade, quantity or coordinates.
- Preserve TFC-style ground rocks as the desired later presentation. This does not authorize removing existing surface rocks or installing TFC.

## Proposed minimal implementation defaults

- Reuse a normal Minecraft stick; crouch and right-click a ground block to prospect. No new item, art or crafting recipe required. Crouching avoids intercepting ordinary stick interactions.
- Define the checked spot as the clicked block's 16 by 16 chunk footprint, from that Y down to the dimension bottom. The exact footprint is an implementation proposal, not a user-selected numeric range.
- Action-bar results: "Vein detected beneath this area." or "No vein detected beneath this area."
- No consumption or durability; a short server-side cooldown prevents repeated scans.
- Detect actual surviving custom deposits, both standalone and mineshaft-associated. Do not treat every mine as proof of remaining ore, every planned formation as successfully generated, or every mineral block as a vein. Tiny independent 1–3-block pockets and loose surface rocks are not positive vein evidence.
- Read loaded/generated data only; do not generate distant terrain just to answer. If the required data cannot be checked, return an explicit unavailable result instead of a false negative. Normal successful checks remain yes/no.

## Integration work still required

The current source has regional geology plans/shape caches and separate saved MineshaftVeinPiece geometry. SurfaceRockClues handles regional candidates, so reusing it alone would miss the separate mine-associated deposit path. A scan must cover both and verify remaining ore while keeping work bounded, especially after massive-vein integration. Avoid introducing an arbitrary ore-count heuristic that mistakes cave traces or player-placed minerals for actual veins.

Acceptance: positive standalone vein; positive mine-bearing vein; negative ordinary terrain and small pockets; exhausted deposit negative; negative coordinates and area boundaries; restart consistency; cooldown and both-hand interaction behavior; no forced terrain generation. All NOT_RUN.

Next action: implement the bounded combined lookup and stick interaction in staging, then run native acceptance before deployment. No production mod, config or save changed by this design checkpoint.
