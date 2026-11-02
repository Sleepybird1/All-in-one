## October30 follow-up — occupied-byte power and efficiency cards

README storage design notes are the current authority for the new power proposal. Each cell is billed on its own occupied bytes using its ordinal1×/2×/4×/8×multiplier; adding another cell does not increase earlier cells' rates. Base rate/counting scope/ranking/tier interaction and reset/splitting protections remain undecided. The user's1FEexample is not a selected rate. Expensive stackable late-game Energy Efficiency Cards should give diminishing additional savings;50%then another10percentage points is illustrative only. No power, capacity, card or recipe implementation authorized by this documentation request. Existing chest-only Matter Stabilizer direction remains.

## October 30 — chest-first storage and endgame chest-only stabilization

Latest explicit user direction supersedes the older stabilized-ME-Drive and Extended-Drive ship arrangements below.

- ME Chest is the starting digital storage host, holding one storage cell (not a one-item-type restriction).
- Standard ME Drive unlocks substantially later. Its ten slots must not make many cheap1kcells an early bulk-storage shortcut.
- Extended ME Drive is an endgame ground-storage upgrade.
- Matter Stabilizer unlocks at that endgame stage, but authorizes shipboard digital storage in ME Chests only. It does not authorize standard or Extended ME Drives on moving ships.
- Preserve physical silo/vault bulk logistics. Exact chest/cell ship count, aggregate capacity, stabilizer-to-chest binding, recipes and power demand still need balancing; do not carry the old drive-binding or provisional4KiBlimit forward as newly selected numbers.
- Loaded-cell transport/home/custody protections remain relevant. Do not allow packed drives, portable cells, nested inventories or subnet splitting to bypass the chest-only exception. Networking a chest must not silently authorize a drive elsewhere on the ship.
- Byte density is under discussion: one item per byte and two ordinary items per byte with heavier bulk-item costs were proposals, not a final implemented configuration. No per-item weights or capacity curve selected here.

Design documentation only. No recipe, capacity, ship guard or game files changed. Matter Stabilizer is the existing registered block name.

## October16 latest clarification — inventory movement stays local

Loaded cells must remain transferable through player inventory for rearranging/moving an ME installation. They must not become inventory freight over thousands of blocks or across dimensions. Enforce a configurable local radius from a **fixed home installation** and compatible physical world/frame; the exact radius is unselected. Empty cells stay freely portable. Chest/backpack wrapping, packed drives, reconnecting, relogging, repeated short moves and direct digital copying into another cell must not reset the home. Local handling requires no stabilizer per pickup.

An access lock applied after arrival is insufficient: the prohibited movement/transition itself needs admission checks. This supersedes the controlled-redemption-only preference below. The separate stabilized-drive/card design does not grant unlimited player-inventory range. No runtime movement enforcement is implemented or installed. [Current design](../../workflow/ship-ae2-limits/PORTABLE_CELL_CARGO.md). Overall204/289(70.6%); progression33/79(41.8%).

---

## October16 earlier requirement — loose loaded cells are cargo

The user identified the pocket/chest bypass: disabling onboard access still permits carrying a loaded cell and using it at the destination. The current staged guard does **not** close that exploit. It only scans mounted AE inventories and the portable access path; sealed physical cargo was explicitly allowed by the older design below. That exemption is superseded for bulk loaded cells.

Empty cells move freely; local loaded-cell maintenance remains possible. A small aggregate portable allowance may remain. Bulk payload movement needs an authorized source/carrier/destination handoff using the already requested Matter Stabilizer and pathway card. Preserve cell contents and recovery. Putting the cell into an ordinary chest/backpack/packed drive, splitting it among smaller cells or placing a stabilizer only after arrival must not authorize free transport.

The user's latest carrier arrangement is **one stabilizer for one bound ME Drive on one network**, with Extended drives requiring more operating energy. This supersedes the older one-block-per-cell staging model. Exact energy/portable limits have not been selected; the old4KiB constant is provisional. No such powered per-drive/card or durable cargo-custody system is implemented yet. No production installation follows from this note.

Read [Loaded-cell cargo design and native safety requirements](../../workflow/ship-ae2-limits/PORTABLE_CELL_CARGO.md). Preferred implementation direction: durable source/destination custody and controlled redemption, allowing recoverable movement without freezing actors or deleting data. Never fake a loaded cell as null/empty at a raw inventory API: native disassembly can destroy it. All-host context, existing-cell admission, migration and native transport qualification remain open.

Overall **204/289 (70.6%)**; progression **33/79 (41.8%)**. Source/design audit complete; runtime enforcement of this correction **NOT_IMPLEMENTED**. Historical implementation details below retain their original scope and cannot be used as acceptance for this rule.

---

## October15 historical staged rule

One Matter Stabilizer supports at most ONE physical item-storage cell on ONE local AE2 network at a time. Each additional cell needs a separate stabilizer, including cells in the same drive or another subnet. Cells without a live local grid refuse access. The existing4KiB aggregate ship limit still applies; more stabilizers do not increase it. The live snapshot reserves one interchangeable stabilizer slot per cell; no durable player binding or consumed stabilizer. Contents remain untouched on denial. This code is staged, not installed; native qualification remains pending.

# Staged ship AE2 restriction — October 15

Implementation candidate is now staged in source, **not installed or native-qualified**. This supersedes the earlier unimplemented-design status below.

| Rule | Staged behavior |
|---|---|
| Small onboard system | Requires a placed Matter Stabilizer on the same native ship body. |
| Shared item storage allowance | Provisional 4 KiB rated capacity total per ship, across drives, ME chests and independent grids/subnets. Four 1k cells fit; five do not. An empty or partitioned large cell still counts at full rated capacity. |
| Multiple stabilizers | Presence only; no extra storage allowance. |
| Fluid/gas/unknown cells | Disabled onboard, preserving physical tank freight. Unknown/unmeasurable providers fail closed. |
| Ground networks | Unchanged when entirely ground-based. |
| Remote and dock links | No cross-body/ground links or Quantum Bridge aboard a ship, even while stopped or physically docked. No dock exemption in this candidate. Linking a ship to a base therefore holds the linked grid, rather than exposing unlimited ground storage. |
| Wireless and portable access | AE2 portable/wireless terminal hosts are held aboard ships, including references obtained before boarding. Use a local wired terminal. Player-sourced remote ground transfers are also refused at guarded storage paths. |
| Existing contents | Never delete/eject cells, erase contents, cancel crafting jobs or refund ingredients. Access is held; physical drive maintenance remains possible. |
| Stability anchor | New user-requested `industrial_colonies:matter_stabilizer` block/item and non-ticking marker. Passive presence gate; no invented FE operating cost. |

The capacity is a conservative staging default chosen for this implementation, not a user-selected final number. Source constant: `ShipAeBudget.MAX_ITEM_BYTES`. Matter Stabilizer recipe is a separate proposed full5x5 mechanical-crafting card using completed boards, a rechargeable energy tablet, opposing AE2 formation/annihilation cores, magnetic shielding, cobalt ingots, capacitors and insulated electrum wiring. New item/model is staged only; its card is kept out of the live editor until the item exists there.

Native Sable body ownership determines the rule; velocity zero does not grant an exemption. A fresh live plot/cell scan occurs for access checks, with no cached positive permission. Stale/unloaded provider nodes absent from the body snapshot are refused. All known grid nodes must belong to the same live body; third-party providers without measurable cell ownership are refused. Scan bounds (256 plot chunks / 4096 block entities) refuse oversized cases instead of doing unbounded work.

Implementation covers installed AE2 storage services, power service, drives, ME chests, chest fluid capabilities and AE2 portable/wireless hosts. Addon cell items using AE2's basic-cell capacity interface inherit the aggregate check; custom/opaque cells are refused. Arbitrary third-party bypass code is not certified. Create contraptions outside Sable's native body model, native lifecycle/mixin application and large-body performance remain unqualified. Sealed cells may still be carried as physical cargo; this is an operation/access restriction, not a destructive cargo prohibition.

Validation and evidence: `workflow/ship-ae2-limits/` contains budget/access tests, installed injection signature checks, full main compile, staged recipe and recipe review. Native assembly/docking/restart/cell-swapping tests remain NOT_RUN. Prior dock-link component acceptance remains historical and does not qualify this new policy; integration must be rechecked.

# AE2 aboard ships — October 15 direction

User: "I think AE2 networks should just be disabled on moving objects. I do like the idea of a small one being on a ship but a 256m network on a ship kind of kills my game immersion."

## Required outcome

Large mobile digital warehouses must not replace physical ship cargo. Keep the possibility of a small onboard service network. Ground installations can retain large networks and large crafting computers. This is a design instruction, not implemented behavior.

No numerical allowance has been selected for the small-network exception. Do not invent a final byte/channel/device limit or claim that all AE2 is forbidden: the user explicitly likes small ship networks. Until an enforceable exception is designed, unrestricted onboard networks are not approved.

## Implementation requirements to resolve

- Classify a ship-mounted installation by native moving-body ownership, not instantaneous speed. Stopping in space must not turn an unrestricted warehouse on.
- Bound aggregate onboard storage across drives, chests, portable interfaces, subnets and AE2 addons. Counting one cell per drive or limiting only 256m cells leaves obvious stacking bypasses.
- Separate crafting-job workspace from item/fluid inventory storage. Large stationary crafting computers remain useful; a crafting-storage label is not proof of a cargo restriction.
- Review wireless terminals, quantum bridges, external storage buses and dock links. A small onboard grid must not become a front end to unlimited remote cargo while underway.
- Docked access may be useful, but is not automatically exempt. Any exception must require the retained physical dock lock and invalidate on separation; existing AeDockService provides only a bridge prototype, not this policy.
- Deny operation/access without deleting cells, clearing inventory or ejecting cargo. Preserve exact saved contents, crafting state and recovery across assembly, detachment, restart and docking.
- Explain disabled access in the UI. Avoid silent item loss or a nonresponsive terminal.

## Current code audit

AeDockService is a staged physical connection prototype using native AE nodes. It checks reciprocal physical dock locks and invalidates links, but does not cap onboard network storage. AE2StorageCellItemMixin guards recipe-stage disassembly only. Neither establishes a moving-network restriction. No pack-wide mobile AE2 guard was found in the inspected source search.

## Status and next action

Design recorded; runtime enforcement NOT_IMPLEMENTED. No configuration, recipes, saved networks or installed mods changed. Next technical action: inspect installed AE2 grid storage and service-access hooks alongside native body membership, then draft an aggregate small-network policy with explicit dock/remote-access boundaries. Native qualification must cover large-cell stacks, addon cells, subnets, bridge access, zero-velocity ship ownership and preservation on restart.

Overall 204/289 (70.6%); progression 33/79 (41.8%). This records a new requirement and does not complete a master task.

## October 15 confirmation

User explicitly requested that this rule be written alongside installation of the UI fixes. Large AE2 networks/storage on moving objects are disallowed by design. A small onboard service network is the intended exception, with exact aggregate allowance still to be defined; 256m shipboard storage is outside that exception. Apply by native ship ownership rather than only while measured velocity is nonzero. This confirmation does not implement a runtime guard or select an arbitrary numerical cap. Ground networks remain unrestricted by this ship rule.

Future electronics material note: use existing cobalt in suitable battery, electrode and advanced-electronics recipes where its role and progression justify it. Do not add it to every recipe or alter approved cards merely to increase usage.
