# All-in-One — Industrial Colonies

Modpack documentation, current to-dos and compact storage-capacity references.

Saved worlds, machine-private state, crash dumps, caches and build outputs are excluded from the published checkpoint; historical tracked files remain preserved.

## Reference spreadsheet

Refer to [Industrial Colonies — Vein Balance](https://docs.google.com/spreadsheets/d/1eB8tn9jFumsnquxsZ1CsZR8GkLkyEhkbVO3lvMMpMzc/edit) for resource and vein balance, production yields and uses, biome habitats, spawn rates and structure spacing, and the editable Recipe index with ingredient costs and material estimates. Planning values and verified gameplay results are labeled separately in the workbook.

## Documentation

| Document | Contents |
|---|---|
| [Design ideas and history](DESIGN_IDEAS.md) | Reactor and controller decisions, recipe review notes, design-document index and chronological evidence |
| [Detailed non-recipe task index](workflow/early-survival/nonrecipe-review/ALL_TASKS.md) | Separate task-by-task acquisition/non-recipe review snapshot; its older totals are historical |
| [Master task register](industrial-colonies/MASTER_TASKS.json) | Authoritative implementation status |
| [Changelog](CHANGELOG.md) | Subsystem changes and maturity limits |
| [Continuation handoff](WEB_HANDOFF.md) | Resume context and next actions |

Recorded current master status: **204/289 complete (70.6%), 85 remaining**; progression **33/79 (41.8%)**.

## To do

An unchecked item may require a design decision, recipe review, implementation or gameplay verification. Supporting decisions and checkpoint history are in [Design Ideas](DESIGN_IDEAS.md).

### Reactor progression and power — current priority

- [ ] **Balance Fission → Molten Salt → Fusion through energy demand.** Earlier reactors should make manufacturing the next tier practical, but skipping a tier should remain possible. Building the fusion controller and core should demand immense energy/material production. Choose actual fabrication energy, throughput and startup/operating costs together; do not substitute mandatory earlier-reactor items for this economic progression. Numeric power balancing is not implemented.
- [ ] Audit all transitive reactor ingredients and alternate production routes for unintended hard locks or cheap bypasses. Removing the explicit controller/calibration dependencies alone does not prove every route is skippable.
- [ ] Review the current Fusion Control Unit sequence: Platinum Plate → press → circuit board, laminated contacts, Osmiridium rails, processors/computing, sensors/regulation/wiring, Iridium contacts and shielding. Export only the exact design is approved; the installed older recipe and latest review draft currently differ.
- [ ] Verify the newly approved Pulse Power and Magnet Protection recipes reach gameplay with their mixed Brass/Railway/Radiance operations. Preserve accepted compact 3D models; rejected flat sprites remain previews only.
- [ ] Review the three revised MSR construction cards (controller, fuel cell, port) and revised shielded Fuel Reprocessor. They are drafts in Progression Review, not newly activated gameplay recipes.
- [ ] Reconcile the latest fusion-core card with the selected subsystems, advanced-computer direction and removal of redundant loose Allthemodium rods; inspect saved edits before changing it. Retain casing output of four.
- [ ] Rework turbine coil recipes around actual conductor/winding materials: aluminum wiring/spool for aluminum coils, appropriate conductor for gold/other coils. Verify the installed TFMG spool/winding process and its supported recipe format first.
- [ ] Retain the researched electromagnet field/power/thermal tradeoffs when balancing magnets; do not turn every branch into a simple price ladder. Research evidence remains referenced in Design Ideas; the local workflow folder is not included in this checkpoint.

### Recipe review, exports and editor reliability

- [ ] Revisit the broad October30review pass before approval:69construction drafts and1quantum-processor machine correction passed offline validation, but the Brass Pattern Provider was explicitly judged worse. Do not describe this batch as approved or continue redesigning it without renewed direction after the paused review.
- [ ] Verify the rejected-card cleanup in-game:397restore-default records were cleared;85native default recipes for67affected outputs were prepared in a late runtime restoration script. The installed-engine callback fixture passes; actual recipe reload/JEI results remain unverified. Three competing NuclearCraft fluid-tank cards moved to Disabled; runtime suppression still needs checking.

- [ ] Reconcile saved review cards, approval records, exported scripts and loaded recipes. Resolve missing JEI recipe visibility separately from merely seeing “zero failed recipes” in a server log.
- [ ] Verify the crafting-table cleanup boolean fix on the next actual reload. Its installed-engine/Java predicate regression passes; that alone is not a new in-game reload result.
- [ ] Remove the older duplicate Fusion Control Unit producer when finalizing its approved replacement; preserve exactly one intended runtime recipe.
- [ ] Investigate archive refresh/card moves so a recipe does not vanish from the running review view when Approved is cached. Do not promise archive auto-refresh that the installed editor does not support.
- [ ] Rework the remaining selected machine recipes against the progression sheet, actual function and balanced cost. Approval means a custom recipe is wanted, not that it must be expensive. Preserve completed personal recipes and never silently resubmit an unchanged rejected design.
- [ ] Revisit Andesite/Brass Pattern Providers and explain Station Services Controller requirements before changing their progression or replacing their role.
- [ ] Keep rejected/default-restoration, Disabled, Maybe and Deferred meanings separate. Verify runtime suppression for explicitly disabled devices; an archive decision alone is not implementation.
- [ ] Finish pending material-processing proposals, including Crystal Binder, only after exact recipe approval. Preserve separate plate/sheet forms, canonical duplicates, authoring visibility, machine-tier gates and first-machine bootstrap.
- [ ] Finish the Manufactory dust/crushed coverage audit and selected cutoff; do not silently keep chemical/wafer/leather shortcuts or add Allthemodium-and-higher grinding. Audit evidence remains referenced in Design Ideas; the local workflow folder is not included in this checkpoint.

### Storage, logistics and mass — design selected, implementation remains

- [ ] Implement the Extended ME Drive efficiency target: 50% lower host overhead per cell than a standard Drive. Keep cell-storage power and transport stabilization separate; select exact FE/t and recipe costs, and verify cell-tier power tradeoffs.

- [ ] Price the ME Chest as the initial single-cell host, gate standard ME Drives substantially later and Extended ME Drives at endgame. The suggested ten-chests-versus-one-drive cost comparison is a target to evaluate, not an implemented ratio. Prevent many cheap1kcells/chests from bypassing physical storage progression.
- [ ] At the endgame storage stage, make Matter Stabilizer authorize shipboard ME Chests only; do not carry forward old Drive/Extended-Drive stabilization. Decide per-ship chest count/aggregate capacity and binding, and close nested-container/subnet/portable-cell bypasses without losing contents.
- [ ] Implement and verify the selected paired cell-capacity rule in the November 1 storage capacity balance above; finalize actual type overhead/limits. Keep the goal clear: physical silos/vaults for large bulk, digital storage for useful mixed inventories; Storage Buses can expose physical inventories without moving them into cells.

- [ ] Implement connected Item Vault storage at forty-eight stacks per block and one item type across the whole structure. Resolve Item Silo parity rather than changing a shared setting blindly.
- [ ] Make loaded Vault cargo increase ship mass, counting shared multiblock inventory once and reducing mass when unloaded.
- [ ] Make Copycat material mass scale by occupied shape volume; empty Copycats remain nearly weightless. Define actual shape fractions and ship-mass integration.
- [ ] Balance late-game AE2 item/fluid cells and housings, including the first 1k tier, while retaining useful automation and physical bulk storage.
- [ ] Design and implement the selected per-cell occupied-byte power rates (1×,2×,4×,8×…), stable ranking/counting and anti-splitting rules; choose actual base/idle/tier values. Design expensive stackable late-game Energy Efficiency Cards with diminishing savings and a minimum power floor. All illustrative numbers remain provisional; power loss must not destroy contents.
- [ ] Complete loaded-cell freight restrictions and enforce physical cargo relevance. [AE2 ship limits](industrial-colonies/design/SHIP_AE2_LIMITS.md).
- [ ] Verify competing standalone tank suppression while retaining Create Fluid Tank and Fluid Vessel. Treat chemical/oxygen equipment, machine parts, digital storage and IE multiblock tank separately.
- [ ] Finish iron/aluminum sheet-metal Vault construction and decide the Silo recipe separately.

### Space, worlds and other implementation work

- [ ] Reconcile the one-navigation-computer direction, excess certification intermediates, station services and practical station/flight costs; preserve functional dependencies until replacements exist.
- [ ] Finish the Atmospheric Scoop's selected late-game 7×7 construction design and extraction prerequisites.
- [ ] Continue world-resource, finite-reserve, prospecting, terrain/structure, ships/combat and remaining implementation work from the canonical registers rather than inferring completion from historical notes.
- [ ] Reconcile processing yields, finite deposit lifetimes and factory demand; preserve the selected Earth geography/material directions. [Earth resource chart](industrial-colonies/design/EARTH_RESOURCE_MASTER_CHART.md).

### Parked for later — do not automatically reopen

- [ ] Copycat acquisition recipes; Big Reactors reactors/turbines; creative/endgame items.
- [ ] Deferred space/planet/navigation items, RTGs, batteries/voltaic piles, decay generators, bombs and other live Deferred selections. Current review decisions, not this broad family summary, control each card.
- [ ] Deferred exotic material routes and undecided design proposals retain their own status and prerequisite decisions.

## Storage capacity

Selected capacity targets; implementation and gameplay verification remain pending.

### ME item-cell capacities

| Cell tier | Bytes/item | One cell | 1 full drive | 2 full drives | 4 full drives | 8 full drives |
|---|---:|---:|---:|---:|---:|---:|
| 1K | 4 | 256 | 2,560 | 5,120 | 10,240 | 20,480 |
| 4K | 8 | 512 | 5,120 | 10,240 | 20,480 | 40,960 |
| 16K | 16 | 1,024 | 10,240 | 20,480 | 40,960 | 81,920 |
| 64K | 16 | 4,096 | 40,960 | 81,920 | 163,840 | 327,680 |
| 256K | 32 | 8,192 | 81,920 | 163,840 | 327,680 | 655,360 |
| 1M | 32 | 32,768 | 327,680 | 655,360 | 1,310,720 | 2,621,440 |
| 4M | 64 | 65,536 | 655,360 | 1,310,720 | 2,621,440 | 5,242,880 |
| 16M | 64 | 262,144 | 2,621,440 | 5,242,880 | 10,485,760 | 20,971,520 |
| 64M | 128 | 524,288 | 5,242,880 | 10,485,760 | 20,971,520 | 41,943,040 |
| 256M | 128 | 2,097,152 | 20,971,520 | 41,943,040 | 83,886,080 | 167,772,160 |

All counts are item budgets **before item-type overhead**, with 10 cells per standard ME Drive, binary K = 1,024 bytes and M = 1,048,576 bytes. Effective capacity = nominal bytes / bytes per item. The first two upgrades each double effective capacity (256 → 512 → 1,024 items/cell); subsequent upgrades alternate 4× and 2× gains. Actual type limits/overhead and technical implementation still require verification.

### Item Vault capacity target

Set the target to **48 inventory slots (stacks) per Vault block**. Item totals assume full stacks of 64; lower-stack or unstackable items reduce totals. Larger structures do not increase capacity per occupied block.

| Vault dimensions | Blocks | Slots | Items at 64/stack |
|---|---:|---:|---:|
| 1 × 1 × 1 | 1 | 48 | 3,072 |
| 1 × 1 × 3 | 3 | 144 | 9,216 |
| 2 × 2 × 6 | 24 | 1,152 | 73,728 |
| 3 × 3 × 9 | 81 | 3,888 | 248,832 |

Maximum 3 × 3 × 9 Vault: **248,832 items**, close to the requested 250,000. Relative to the discussed 20-slot baseline, 48 slots is 2.4× capacity (+140%); verify the installed configuration before applying. Preserve the separately recorded item-type restriction decision and resolve Silo parity before changing a shared setting.
