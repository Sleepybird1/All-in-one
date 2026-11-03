# All-in-One — Industrial Colonies

Reference tables for storage, resource generation, processing yields and balance. **A selected design is not automatically implemented.** Each section identifies its scope; historical proposals remain explicitly marked.

Saved worlds, machine-private state, crash dumps, caches and build outputs are excluded from the published checkpoint; historical tracked files remain preserved.

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

## Table index

- [ME cells and Vaults](#storage-capacity)
- [Spawn rates and structure spacing](#spawn-rates-and-structure-spacing)
- [Earth resources: occurrence, reserves, heights and biomes](#earth-resource-reference)
- [Processing yields](#processing-yields)
- [Other balance tables](#other-balance-tables)
- [Earlier comparison tables](#earlier-comparison-tables)

## Storage capacity

Selected November 1; implementation and gameplay verification remain pending. Extended ME Drives target **50% lower host overhead per cell** relative to standard Drives, excluding cell-storage and transport-stabilization power. Exact FE/t, recipes and efficiency-card interactions remain open.

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

### Capacity crossovers and power decisions

- First full standard Drive tier exceeding the maximum Vault: **1M**, 327,680 items across ten cells; ten 256K cells hold 81,920.
- First single-cell tier exceeding the maximum Vault: **16M**, 262,144 items; one 4M cell holds 65,536.
- Twenty-four full Drives of 16K cells hold 245,760 items, slightly below one maximum Vault.
- These are capacity comparisons, not verified construction-cost equivalence. A full transitive recipe-cost audit remains pending.
- Higher-density cells should cost more to construct and more power per stored item. Paired byte weights already increase occupied bytes/item at every other upgrade; even a constant occupied-byte power rate therefore increases power/item. Extra rate increases multiply this penalty and must be tested against adding smaller cells.
- Exact base/idle rates, tier power multipliers, efficiency cards and transport stabilization costs remain **undecided/unimplemented**. The earlier 3.5× idle-power table is illustrative and is not the approved operating curve. Power loss must not destroy contents.

## Spawn rates and structure spacing

These are the latest recorded design selections from the [decision history](DESIGN_IDEAS.md), not a claim that every native generation path implements them. Probabilities are per stated scope, never per chunk unless explicitly stated. Placement failures and unsuitable terrain can leave larger gaps.

| Content | Selected rate or target | Scope / limits |
|---|---|---|
| Platinum-bearing deposits | 25% (1 in 4) | Per continent target; mapping family occurrence to actual platinum availability still needs reconciliation |
| Giant Veridium formations | 1 in 7 (about 14.2857%) | Per continent; supersedes 1 in 10; no specific biome restriction |
| Visible Vibranium-bearing formation | 10% of Veridium formations | About 1 in 70 continents combined; not 10% of host blocks |
| Embedded Vibranium density | About 1 per 20,000 host blocks (0.005%) | Conditional ore-bearing formation target; final ore counts must reconcile newer finished-yield tiers |
| Veridium host size | 50,000–100,000 host blocks | Host rock, not Vibranium ore or ingots; no mineshafts |
| Mineshafts | 10% per eligible vein | All ordinary families; Veridium excluded; no minimum distance; failed fits tracked separately |
| Lightning Dragon first site | 25% | Per continent, mountains; maximum four sites shared across types/sizes |
| Lightning Dragon second site | 20% after first | 5% cumulative chance of at least two; stop on failed roll |
| Lightning Dragon third site | 10% after second | 0.5% cumulative chance of at least three |
| Lightning Dragon fourth site | 1% after third | 0.005% cumulative chance of four; replaces older one-site cap |
| Other Overworld dragon types | Excluded | Fire sites disabled pending planetary decisions; dead skeleton generation also requested off |
| Villages | Usually 800–4,000 blocks apart | 4,000 unusual; larger terrain-driven gaps possible; measurement semantics pending |
| Small structures | 1,000–4,000 blocks apart | Target band; size classification and distance semantics pending |
| Medium structures | 2,000–4,000 blocks apart | Same terrain/measurement limitations |
| Large structures | At least 4,000 blocks apart | Separate dragon/mine rules remain |
| Merchant and pirate ships | 1,000–4,000 blocks apart | Marine eligibility retained; not every underwater structure |
| Independent surface ore patches | 1–3 blocks | Iron, copper and coal only; legitimate outcrops of other full veins remain allowed |
| Cinnabar concentrations | 1,000 / 5,000 / 15,000 blocks; 80% / 18% / 2% | October 25 correction; localized exposed deposits, never a blanket mountain coating |
| New continent reserve policy | Medium 150,000; large 300,000 ore blocks | October 26 staged/native-tested policy for newly recorded continents; existing commissioned policy retained; production rollout not implied |
| Offshore oil | Very rare; exact probability pending | Every field 100,000,000 mB; no onshore size lottery |
| Other resource presence increases | Pending exact values | Preserve relative rarity; no invented approved all-family percentages |

## Earth resource reference

The combined chart below is the October 10 **discussion/reference chart**, with later corrections shown above and in its source. It is not a table of verified effective spawn rates. In particular, its 15% PGM reference and earlier reserve sizes must not override the later platinum and new-continent policy. Biome-specific roll scope remains unresolved; provisional magnetite examples are taiga 70%, plains 50%, mountains 35%.

### Resource occurrence, reserves and biome preferences

k = 1,000 ore blocks; oil quantities are mB. Size odds are conditional on occurrence; spacing is a preferred nearest-independent-deposit distance. [Source](industrial-colonies/design/EARTH_RESOURCE_MASTER_CHART.md).

| Resource | Reference chance | Small / medium / large reserve | Small / medium / large odds | Spacing | Actual Y / placement | Highest biome preference | Medium | Low |
|---|---:|---|---|---|---|---|---|---|
| Coal | Guaranteed minimum supply | 8k / 35k / 100k | 80% / 18% / 2% | 1–3k within coal district | 0–100 | Swamps, marshes, bayous | Forests, lowland rivers, floodplains | Plains; no mountain preference |
| Zinc | 90% | 5k / 20k / 75k | 80% / 18% / 2% | 3–5k | −20–80 | Limestone/dolomite plains, river valleys | Meadows, sedimentary foothills | Forests over carbonate rock |
| Copper | 85% | 6k / 25k / 90k | 80% / 18% / 2% | 3–5k | −10–160; mountain ceiling review | Badlands, warm rocky hills, warm mountains, savanna highlands | Deserts, temperate mountains, foothills | Cold mountains |
| Cinnabar / redstone | Guaranteed per qualifying mountain range | 1k / 5k / 15k per concentration | 80% / 18% / 2% | Distributed across range | 200–399; exposed, fade above300 | Exposed summit tips above height threshold | Exposed high mountain faces | No warm/cold preference |
| Magnesium | 80% | 4k / 15k / 60k | 80% / 18% / 2% | 3–5k | 30–140 | Limestone/dolomite plains, coastal terraces | Chalk-cliff districts, river-cut carbonate valleys | Dry sedimentary plateaus |
| Graphite | 75% | 5k / 20k / 80k | 80% / 18% / 2% | 3–5k | 30–120; deep diamond-associated exception | Rocky metamorphic highlands | Wooded hills over metamorphic rock | Taiga over metamorphic rock |
| Magnetite iron | 70% | 5k / 25k / 100k | 80% / 19% / 1% | 3–5k | −20–100 | Taiga | Plains | Mountains (very low) |
| Aluminum | 70% | 6k / 25k / 90k | 80% / 18% / 2% | 4–6k | 65–180; near surface | Rainforests, jungles on weathered uplands | Humid tropical woodland | Savanna with deep weathered soil |
| Lead | 70% | 3k / 12k / 50k | 85% / 13% / 2% | 3–5k | −45–60; deepslate variant where appropriate | Limestone/dolomite plains, river valleys | Sedimentary foothills | Forests over carbonate rock |
| Tin | 65% | 2k / 8k / 35k | 85% / 13% / 2% | 3–5k | 0–140; mountain ceiling review | Warm rocky mountains, savanna highlands | Temperate granite hills, mountains | Cold mountains |
| Phosphorus | 65% | 4k / 18k / 70k | 80% / 18% / 2% | 4–6k | 15–90 | Coastal plains, former shallow-sea basins | Sedimentary plains | Exposed sedimentary desert basins |
| Nickel | 45% | 3k / 12k / 50k | 85% / 14% / 1% | 4–6k | −45–35 | Mafic/ultramafic rocky highlands | Ashen Woodland over suitable rock | Other hills over mafic intrusions |
| Boron | 45% | 1k / 5k / 20k | 85% / 14% / 1% | 4–6k | 45–120; near basin floor | Dry lake beds, closed desert basins | Desert basin margins | Badlands with evaporite beds |
| Hematite iron | 40% | 2k / 10k / 50k | 90% / 9% / 1% | 4–6k | 20–160; mountain ceiling review | Badlands, exposed iron-rich sedimentary hills | Dry plateaus, savanna | Exposed iron-rich mountain strata |
| Titanium | 40% | 3k / 15k / 65k | 85% / 14% / 1% | 4–6k | 40–100; near surface | Beaches, coastal dunes with heavy-mineral sands | Coastal plains, ancient beach beds, river mouths | River sands downstream of suitable rock |
| Lithium | 40% | 1.5k / 7k / 30k | 85% / 14% / 1% | 4–6k | −20–100 | Granite/pegmatite hills | Granite highlands, rocky meadows | Forested terrain over pegmatite |
| Chromium | 35% | 2k / 10k / 40k | 85% / 14% / 1% | 4–6k | −40–60 | Ultramafic rocky highlands | Exposed ultramafic hills | Ashen Woodland over ultramafic rock |
| Silver | 35% | 1k / 4k / 20k | 90% / 9% / 1% | 4–6k | −30–200 | Cold mountains, snowy highlands | Cold wooded highlands | Warmer mountains |
| Gold | 25% | 1k / 5k / 20k | 90% / 9% / 1% | 5–7k | −45–100; mountain ceiling review | Cold mountains, taiga mountain districts | Taiga, Cold River, Frozen River | Other cold foothills; warmer access unresolved |
| Tungsten | 25% | 1.5k / 8k / 35k | 85% / 14% / 1% | 5–7k | −40–100; mountain ceiling review | Granite mountain slopes, granite foothills | Rocky granite highlands | Wooded terrain over granite veins |
| Uranium | 20% | 0.75k / 4k / 20k | 90% / 9% / 1% | 5–7k | −55–−10 | Sandstone desert basins, badlands | Sedimentary plateaus | Rocky granitic highlands |
| Thorium | 20% | 1k / 5k / 25k | 90% / 9% / 1% | 5–7k | −50–0 | Granitic/alkaline rocky highlands | Wooded terrain over suitable rock | Heavy-mineral coastal sands: separate form |
| Beryllium | 15% | 0.5k / 2.5k / 15k | 90% / 9% / 1% | 5–7k | −20–100 (new proposal) | Arid volcanic hills with suitable host rock | Rocky mineralized highlands | Desert hills over suitable host rock |
| Osmium / platinum-or-palladium / iridium | 15% | 2k / 10k / 50k | 90% / 9% / 1% | 5–7k | Badlands surface; mountains150–300 | Badlands and mountainous regions ONLY | Relative weighting undecided | Other biomes excluded |
| Onshore crude oil | 50% | 5M / 25M / 100M mB | 80% / 18% / 2% | 4–6k | −45–20; buried | Badlands | Deserts | Savannas (very low) |
| Offshore crude oil | Very rare; rate TBD | 100M mB only | 0% / 0% / 100% | TBD | −50–0; below seabed | Ocean biomes; exact list TBD | — | — |

## Processing yields

Snapshot of the **Production** tab in [Industrial Colonies — Vein Balance](https://docs.google.com/spreadsheets/d/1eB8tn9jFumsnquxsZ1CsZR8GkLkyEhkbVO3lvMMpMzc/edit), read November 2, 2026. All **116 populated input rows** and all 12 source columns are represented below. Resource group is the section heading; the remaining columns are split into yield/route and use/demand tables for readability. Blank source cells remain blank, without implying inherited values or verified routes.

**Planning reference, not an installed recipe guarantee.** Recipe/loot reconciliation, active overrides and exact recovery-dust identities remain unresolved where indicated. The sheet uses a **90 mB design basis** for most metals and a separate **144 mB silicon casting unit**; these are copied as recorded, not silently reconciled with older 100 mB accounting notes.

Estimated total use is a lean-to-expanded colony scenario: **costed subtotals, not a complete spawn-to-warp bill**. Rock counts assume planned rich-vein averages. Unknown routes and blocked antimatter are excluded; uranium and thorium are alternatives. Recipe examples containing ellipses are retained exactly as displayed in the sheet, not expanded into inferred recipes.

[Complete 12-column CSV](docs/reference/production-yields.csv) · [Source values and provenance](docs/reference/production-sheet-snapshot.json). This replaces the older October 19 README production table; that historical table remains in [Design Ideas](DESIGN_IDEAS.md).

### Iron

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Iron / Magnetite | 1 block | 3–10 mB | 9–30 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich magnetite ore | 1 rich ore block | 21–30 mB | 3–5 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Iron ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled recipe; active override not verified |
| Iron nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Iron dust | 1 dust | 90 mB | 1 dust |  | Bundled conditional tag recipe; active override not verified |
| Iron / Hematite | 1 block | 3–50 mB | 2–30 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich hematite ore | 1 rich ore block | 63–90 mB | 1–2 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Iron / Magnetite | 3 mB Molten Iron<br>1 indexed recipes | Steel, tools, machine frames, structural parts | Foundational bulk metal | 183,500–807,300 iron ingots*<br>Magnetite only: 1,214,600–5,342,100 blocks<br>Hematite only: 296,200–1,303,000 blocks | Processor: Foundry Melting |
| Rich magnetite ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Iron ingot | Weathered Iron Press<br>Cast Iron Ingot<br>338 indexed recipes |  |  |  | Processor: Mechanical Crafters<br>Processor: Sequenced Assembly<br>Makes: Weathered Iron Press |
| Iron nugget | Cable Insulator<br>4 × Spring<br>98 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Processor: Mechanical Mixer<br>Makes: Cable Insulator |
| Iron dust | Iron Heat Sink<br>144 mB Molten Steel + 144 mB Molten Slag ...<br>7 indexed recipes |  |  |  | Processor: Industrial Blast Furnace<br>Processor: Alloy Smelter<br>Makes: Iron Heat Sink |
| Iron / Hematite | 3 mB Molten Iron<br>1 indexed recipes |  |  |  | Processor: Foundry Melting |
| Rich hematite ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |

### Aluminum

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Aluminum / Bauxite | 1 block | 60–60 mB | 2 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich bauxite | 1 rich ore block | 120–120 mB | 1 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Aluminum ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Aluminum nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Aluminum dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Aluminum / Bauxite | 4 × Bauxite Powder<br>1 indexed recipes | Lightweight aircraft frames, machinery, electrical parts | Bulk lightweight construction | 55,000–256,100 ingots*<br>75,700–352,500 vein blocks* | Processor: Crushing Wheels |
| Rich bauxite | 8 × Bauxite Powder<br>1 indexed recipes |  |  |  | Processor: Crushing Wheels |
| Aluminum ingot | 2 × Large Aluminum Cogwheel<br>4 × Aluminum Cogwheel<br>60 indexed recipes |  |  |  | Processor: Stonecutting<br>Processor: Mechanical Crafters<br>Makes: 2 × Large Aluminum Cogwheel |
| Aluminum nugget | 4 × Aluminum Frame<br>4 × Aluminum Truss<br>3 indexed recipes |  |  |  | Makes: 4 × Aluminum Frame |
| Aluminum dust | Aluminum Heat Sink<br>4 × Flare Cartridge<br>5 indexed recipes |  |  |  | Processor: Engineer's Blueprint<br>Processor: Subatomic Liquifier<br>Makes: Aluminum Heat Sink |

### Copper

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Copper / Chalcopyrite | 1 block | 4–60 mB | 2–23 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich copper ore | 1 rich ore block | 70–100 mB | 1–2 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Copper ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled recipe; active override not verified |
| Copper nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Copper dust | 1 dust | 90 mB | 1 dust |  | Bundled conditional tag recipe; active override not verified |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Copper / Chalcopyrite | 4 mB Molten Copper<br>1 indexed recipes | Wiring, motors, coils, brass | Foundational electrical metal | 394,600–1,776,400 ingots*<br>546,000–2,458,100 vein blocks* | Processor: Foundry Melting |
| Rich copper ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Copper ingot | 4 × Fluid Pipe<br>4 × LV Wire Connector<br>131 indexed recipes |  |  |  | Processor: Crafting Shaped Retextured<br>Processor: Metal Press<br>Makes: 4 × Fluid Pipe |
| Copper nugget | 4 × Copper Frame<br>4 × Neon Tube<br>20 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Processor: Mechanical Press / Basin<br>Makes: 4 × Copper Frame |
| Copper dust | Copper Heat Sink<br>2 × Constantan Grit<br>8 indexed recipes |  |  |  | Processor: Assembler<br>Processor: Metallurgic Infuser<br>Makes: Copper Heat Sink |

### Zinc

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Zinc / Sphalerite | 1 block | 2–60 mB | 2–45 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich sphalerite | 1 rich ore block | 84–120 mB | 1–2 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Zinc ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Zinc nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Zinc dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Zinc / Sphalerite | 2 mB Molten Zinc<br>1 indexed recipes | Brass, alloy feed, starter Create industry | Progression alloy metal | 7,560–26,400 ingots*<br>10,200–35,700 vein blocks* | Processor: Foundry Melting |
| Rich sphalerite | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Zinc ingot | Zinc Mechanism<br>Electric Gauge<br>80 indexed recipes |  |  |  | Processor: Stonecutting<br>Processor: Mechanical Saw<br>Makes: Zinc Mechanism |
| Zinc nugget | Andesite Alloy<br>Zinc Mechanism<br>13 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Processor: Mechanical Mixer<br>Makes: Andesite Alloy |
| Zinc dust | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |

### Magnesium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Magnesium / Dolomite | 1 block | 20–20 mB | 5 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Magnesium ingot (design unit) | 90 mB molten metal | 1 ingot | 1 casting unit | Sheet unit basis; exact casting recipe unverified | 90 mB design basis; not verified native remelting |
| Magnesium recovery dust | 1 dust | 10 mB | 9 dust | Saved vat recovery design | Saved recipe card, not loaded-recipe acceptance |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Magnesium / Dolomite | No manufacturing recipe in retained index | Titanium reduction, lightweight and nuclear alloys | Chemical and alloy feed | 61–132 ingots*<br>273–594 vein blocks* | No direct machine-part match in retained index |
| Magnesium ingot (design unit) | Drive Upgrade<br>Import/Export Bus Upgrade<br>13 indexed recipes |  |  |  | Processor: Alloy Smelter<br>Processor: Subatomic Liquifier<br>Makes: Drive Upgrade |
| Magnesium recovery dust | Saved recovery dust; exact input identity... |  |  |  | Exact recovery-dust item identity unverified |

### Lead

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Lead / Galena | 1 block | 3–30 mB | 3–30 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich galena ore | 1 rich ore block | 42–60 mB | 2–3 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Lead ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Lead nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Lead dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Lead / Galena | 2 × Cut Galena Brick Slab<br>2 × Cut Galena Slab<br>22 indexed recipes | Radiation shielding, nuclear machinery, specialty alloys | Shielding and nuclear industry | 2,130–5,580 ingots*<br>5,780–15,100 vein blocks* | Processor: Stonecutting<br>Processor: Foundry Melting |
| Rich galena ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Lead ingot | 2 × Radioactive Waste Barrel<br>Drive Upgrade<br>36 indexed recipes |  |  |  | Processor: Industrial Iron Compacting<br>Processor: Stonecutting<br>Makes: 2 × Radioactive Waste Barrel |
| Lead nugget | 4 × Lead Frame<br>4 × Casull Cartridge<br>7 indexed recipes |  |  |  | Processor: Engineer's Blueprint<br>Processor: Smelting<br>Makes: 4 × Lead Frame |
| Lead dust | Lead Heat Sink<br>16 × White Dye<br>5 indexed recipes |  |  |  | Processor: Alloy Smelter<br>Processor: Subatomic Liquifier<br>Makes: Lead Heat Sink |

### Uranium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Lead + uranium / Galena | 1 block | Lead: ≈2.94–29.4 mB<br>Uranium: ≈0.2–0.2 mB | N/A | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Uranium ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Uranium nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Uranium dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Lead + uranium / Galena | No manufacturing recipe in retained index | Nuclear fuel and nuclear processing | Specialist energy feed | 17,900–595,700 ingot-equivalents*<br>8,076,800–268,065,000 host blocks*<br>If this fuel supplies the ordinary grid | No direct machine-part match in retained index |
| Uranium ingot | Drive Upgrade<br>Import/Export Bus Upgrade<br>20 indexed recipes |  |  |  | Processor: Fluidizersolid<br>Processor: Enrichment Chamber<br>Makes: Drive Upgrade |
| Uranium nugget | Only generic mold-making matches<br>1 indexed recipes |  |  |  | Processor: Casting Table |
| Uranium dust | Atomic Alloy<br>450 mB Subliquid Matter<br>4 indexed recipes |  |  |  | Processor: Refined Radiance Mixing<br>Processor: Subatomic Liquifier<br>Makes: Atomic Alloy |

### Thorium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Lead + thorium / Galena | 1 block | Lead: ≈2.94–29.4 mB<br>Thorium: ≈0.2–0.2 mB | N/A | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Thorium ingot (design unit) | 90 mB molten metal | 1 ingot | 1 casting unit | Sheet unit basis; exact casting recipe unverified | 90 mB design basis; not verified native remelting |
| Thorium recovery dust | 1 dust | 10 mB | 9 dust | Saved vat recovery design | Saved recipe card, not loaded-recipe acceptance |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Lead + thorium / Galena | No manufacturing recipe in retained index | Nuclear fuel chains and nuclear alloys | Specialist nuclear feed | 12,600–395,300 ingot-equivalents*<br>5,671,000–177,902,000 host blocks*<br>If this fuel supplies the ordinary grid | No direct machine-part match in retained index |
| Thorium ingot (design unit) | Drive Upgrade<br>Import/Export Bus Upgrade<br>10 indexed recipes |  |  |  | Processor: Subatomic Liquifier<br>Makes: Drive Upgrade<br>Makes: Import/Export Bus Upgrade |
| Thorium recovery dust | Saved recovery dust; exact input identity... |  |  |  | Exact recovery-dust item identity unverified |

### Tin

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Tin / Cassiterite | 1 block | 3–20 mB | 5–30 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich tin ore | 1 rich ore block | 28–40 mB | 3–4 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Tin ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Tin nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Tin dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Tin / Cassiterite | 3 mB Molten Tin<br>1 indexed recipes | Bronze and other alloys, electronics components | General alloy feed | 1–3 ingots*<br>4.2–13 vein blocks* | Processor: Foundry Melting |
| Rich tin ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Tin ingot | 4 × Cable Anchor<br>Drive Upgrade<br>20 indexed recipes |  |  |  | Processor: Quartz Cutting<br>Processor: Alloy Smelter<br>Makes: 4 × Cable Anchor |
| Tin nugget | Only generic mold-making matches<br>1 indexed recipes |  |  |  | Processor: Casting Table |
| Tin dust | Tin Heat Sink<br>10 chemical units Tin<br>9 indexed recipes |  |  |  | Processor: Alloy Smelter<br>Processor: Chemical Oxidizer<br>Makes: Tin Heat Sink |

### Nickel

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Nickel / Pentlandite | 1 block | 14–20 mB | 5–7 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich nickel ore | 1 rich ore block | 28–40 mB | 3–4 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Nickel ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Nickel nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Nickel dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Nickel / Pentlandite | No manufacturing recipe in retained index | Steel alloys, invar, magnetic alloys | Broad industrial alloy metal | 201,100–919,600 ingots*<br>830,100–3,796,400 vein blocks* | No direct machine-part match in retained index |
| Rich nickel ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Nickel ingot | Nickel Plate<br>2 × Magnetic Alloy Ingot<br>15 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Processor: Mechanical Mixer<br>Makes: 2 × Magnetic Alloy Ingot |
| Nickel nugget | 4 × Nickel Frame<br>4 × Nickel Truss<br>3 indexed recipes |  |  |  | Makes: 4 × Nickel Frame |
| Nickel dust | 2 × Constantan Grit<br>1 indexed recipes |  |  |  | Processor: Crafting |

### Cobalt

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Cobalt / Pentlandite | 1 block | ≈0.07–0.1 mB | 900–1286 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Cobalt ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled recipe; active override not verified |
| Cobalt nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Cobalt dust | 1 dust | 90 mB | 1 dust |  | Bundled conditional tag recipe; active override not verified |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Cobalt / Pentlandite | No manufacturing recipe in retained index | Specialty alloys and nuclear materials | Pentlandite-associated specialist | 6,550–25,700 ingots*<br>5,893,600–23,171,400 vein blocks* | No direct machine-part match in retained index |
| Cobalt ingot | Elite Induction Cell<br>Industrial Iron Mixer<br>20 indexed recipes |  |  |  | Processor: Mechanical Crafters<br>Processor: Sequenced Assembly<br>Makes: Elite Induction Cell |
| Cobalt nugget | 4 × Cobalt Platform<br>2 indexed recipes |  |  |  | Processor: Casting Table<br>Processor: Crafting |
| Cobalt dust | Cobalt Heat Sink<br>450 mB Subliquid Matter<br>2 indexed recipes |  |  |  | Processor: Subatomic Liquifier<br>Makes: Cobalt Heat Sink |

### Titanium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Titanium / Ilmenite | 1 block | 14–20 mB | 5–7 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich ilmenite ore | 1 rich ore block | 28–40 mB | 3–4 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Titanium ingot (design unit) | 90 mB molten metal | 1 ingot | 1 casting unit | Sheet unit basis; exact casting recipe unverified | 90 mB design basis; not verified native remelting |
| Titanium recovery dust | 1 dust | 10 mB | 9 dust | Saved vat recovery design | Saved recipe card, not loaded-recipe acceptance |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Titanium / Ilmenite | No manufacturing recipe in retained index | Aircraft, spacecraft, advanced structural alloys | Advanced structural metal | 1,370–4,110 ingots*<br>5,770–17,300 vein blocks* | No direct machine-part match in retained index |
| Rich ilmenite ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Titanium ingot (design unit) | Industrial Iron Deployer<br>Industrial Iron Encased Fan<br>13 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Processor: Mechanical Mixer<br>Makes: Industrial Iron Deployer |
| Titanium recovery dust | Saved recovery dust; exact input identity... |  |  |  | Exact recovery-dust item identity unverified |

### Chromium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Chromium / Chromite | 1 block | 17.5–22.5 mB | 4–6 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich chromium ore | 1 rich ore block | 70–90 mB | 1–2 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Chromium ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Chromium nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Chromium dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Chromium / Chromite | No manufacturing recipe in retained index | Steel and specialty alloy production | Industrial alloy additive | 2,370–7,730 ingots*<br>7,810–25,400 vein blocks* | No direct machine-part match in retained index |
| Rich chromium ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Chromium ingot | Drive Upgrade<br>Import/Export Bus Upgrade<br>10 indexed recipes |  |  |  | Processor: Alloy Smelter<br>Makes: Drive Upgrade<br>Makes: Import/Export Bus Upgrade |
| Chromium nugget | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Chromium dust | 2 × Chromatic Compound<br>90 mB Molten Chromium + 10 mB Molten Slag<br>4 indexed recipes |  |  |  | Processor: Industrial Iron Mixing<br>Processor: Vat Machine Recipe |

### Lithium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Lithium / Spodumene | 1 block | 10–10 mB | 9 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Spodumene ore | 1 rich ore block | 30–30 mB | 3 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Lithium ingot (design unit) | 90 mB molten metal | 1 ingot | 1 casting unit | Sheet unit basis; exact casting recipe unverified | 90 mB design basis; not verified native remelting |
| Lithium recovery dust | 1 dust | 10 mB | 9 dust | Saved vat recovery design | Saved recipe card, not loaded-recipe acceptance |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Lithium / Spodumene | No manufacturing recipe in retained index | Batteries, nuclear/fusion and chemical chains | Energy and chemical specialist | 6,370–102,500 ingots*<br>50,100–806,500 vein blocks* | No direct machine-part match in retained index |
| Spodumene ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Lithium ingot (design unit) | 2 × Tough Alloy Ingot<br>Drive Upgrade<br>14 indexed recipes |  |  |  | Processor: Alloy Smelter<br>Processor: Subatomic Liquifier<br>Makes: 2 × Tough Alloy Ingot |
| Lithium recovery dust | Saved recovery dust; exact input identity... |  |  |  | Exact recovery-dust item identity unverified |

### Silver

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Silver / Argentite | 1 block | 2–10 mB | 9–45 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich silver ore | 1 rich ore block | 14–20 mB | 5–7 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Silver ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Silver nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Silver dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Silver / Argentite | 2 mB Molten Silver<br>1 indexed recipes | Conductors, electrum and specialty electronics | Precious electrical metal | 16–80 ingots*<br>137–683 vein blocks* | Processor: Foundry Melting |
| Rich silver ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Silver ingot | 3 × Coil Bscco<br>Basic Processor<br>26 indexed recipes |  |  |  | Processor: Assembler<br>Processor: Alloy Smelter<br>Makes: 3 × Coil Bscco |
| Silver nugget | 4 × Silver Cartridge<br>Pile of Silver<br>3 indexed recipes |  |  |  | Processor: Engineer's Blueprint |
| Silver dust | Silver Heat Sink<br>2 × Electrum Grit<br>7 indexed recipes |  |  |  | Processor: Alloy Smelter<br>Processor: Subatomic Liquifier<br>Makes: Silver Heat Sink |

### Gold

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Gold / Gold ore | 1 block | 7–10 mB | 9–13 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Gold ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled recipe; active override not verified |
| Gold nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Gold dust | 1 dust | 90 mB | 1 dust |  | Bundled conditional tag recipe; active override not verified |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Gold / Gold ore | 1 mB Gold Slurry<br>1000 chemical units Dirty Gold Slurry<br>9 indexed recipes | Electronics, electrum and advanced components | Precious electronics metal | 6,530–26,600 ingots*<br>58,800–239,800 vein blocks* | Processor: Leacher<br>Processor: Chemical Dissolution Chamber |
| Gold ingot | 2 × Heat Exchanger Hot Coolant Port<br>2 × Turbine Bearing<br>110 indexed recipes |  |  |  | Processor: Quartz Cutting<br>Processor: Assembler<br>Makes: 2 × Heat Exchanger Hot Coolant Port |
| Gold nugget | Electrode Holder<br>Metallurgic Infuser<br>25 indexed recipes |  |  |  | Processor: Mechanical Crafters<br>Processor: Mechanical Press / Basin<br>Makes: Electrode Holder |
| Gold dust | Gold Heat Sink<br>10 chemical units Gold<br>8 indexed recipes |  |  |  | Processor: Alloy Smelter<br>Processor: Subatomic Liquifier<br>Makes: Gold Heat Sink |

### Tungsten

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Tungsten / Wolframite | 1 block | 7–10 mB | 9–13 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Rich wolframite ore | 1 rich ore block | 14–20 mB | 5–7 blocks | Crushing → saved recovery route | Saved design cards; rich drop identity still matters |
| Tungsten ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Tungsten nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Tungsten dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Tungsten / Wolframite | No manufacturing recipe in retained index | High-temperature parts and specialty alloys | Refractory specialist | 205–615 ingots*<br>1,750–5,250 vein blocks* | No direct machine-part match in retained index |
| Rich wolframite ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |
| Tungsten ingot | Industrial Iron Deployer<br>Industrial Iron Encased Fan<br>11 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Makes: Industrial Iron Deployer<br>Makes: Industrial Iron Encased Fan |
| Tungsten nugget | Only generic mold-making matches<br>1 indexed recipes |  |  |  | Processor: Casting Table |
| Tungsten dust | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |

### Boron

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Boron / Borax rock | 1 block | 10–10 mB | 9 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Boron ingot (design unit) | 90 mB molten metal | 1 ingot | 1 casting unit | Sheet unit basis; exact casting recipe unverified | 90 mB design basis; not verified native remelting |
| Boron recovery dust | 1 dust | 10 mB | 9 dust | Saved vat recovery design | Saved recipe card, not loaded-recipe acceptance |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Boron / Borax rock | Borax DUst<br>1 indexed recipes | Nuclear materials, chemistry and semiconductor feed | Nuclear / chemical additive | 500–1,250 ingots*<br>4,500–11,200 vein blocks* | Processor: Crushing Wheels |
| Boron ingot (design unit) | Fission Reactor Controller<br>Fission Reactor Irradiation Chamber<br>14 indexed recipes |  |  |  | Processor: Mechanical Crafters<br>Processor: Alloy Smelter<br>Makes: Fission Reactor Controller |
| Boron recovery dust | Saved recovery dust; exact input identity... |  |  |  | Exact recovery-dust item identity unverified |

### Beryllium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Beryllium / Bertrandite | 1 block | 10–10 mB | 9 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Beryllium ingot (design unit) | 90 mB molten metal | 1 ingot | 1 casting unit | Sheet unit basis; exact casting recipe unverified | 90 mB design basis; not verified native remelting |
| Beryllium recovery dust | 1 dust | 10 mB | 9 dust | Saved vat recovery design | Saved recipe card, not loaded-recipe acceptance |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Beryllium / Bertrandite | No manufacturing recipe in retained index | Nuclear and aerospace material chains | Specialist material; demand not measured | No quantified consumption in the costed scenario*<br>Unresolved endgame inputs remain | No direct machine-part match in retained index |
| Beryllium ingot (design unit) | Drive Upgrade<br>Import/Export Bus Upgrade<br>10 indexed recipes |  |  |  | Makes: Drive Upgrade<br>Makes: Import/Export Bus Upgrade<br>Makes: Turbine Beryllium Coil |
| Beryllium recovery dust | Saved recovery dust; exact input identity... |  |  |  | Exact recovery-dust item identity unverified |

### Coal

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Coal / Coal ore | 1 block | 1 coal | N/A | Mining | Selected one coal per ore |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Coal / Coal ore | Coal<br>Coal Ore Mine<br>9 indexed recipes | Fuel, coke, steelmaking and carbon chemistry | Bulk fuel / carbon | 71,300–304,800 coal*<br>71,300–304,800 ore blocks* | Processor: Blasting<br>Processor: Nuclear Blast |

### Graphite

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Graphite / Graphite rock | 1 block | 1–1 dust | N/A | Crushing | Sheet draft; recipe/loot reconciliation pending |
| Diamond / Graphite rock | 1 block | ≈0.001–0.001 diamond |  | Associated diamond recovery | Draft host average; not yield of a diamond ore block |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Graphite / Graphite rock | No manufacturing recipe in retained index | Electrodes, nuclear components and carbon processing | Industrial carbon | 1,630–4,470 graphite dust*<br>17,200–60,000 diamonds*<br>17,217,000–60,001,000 shared host blocks* | No direct machine-part match in retained index |
| Diamond / Graphite rock | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |

### Phosphorus

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Phosphorus / Phosphate rock | 1 block | 1–1 dust | N/A | Saved processing design | Sheet draft; recipe/loot reconciliation pending |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Phosphorus / Phosphate rock | No manufacturing recipe in retained index | Fertilizers, chemistry and semiconductor doping | Agricultural / chemical feed | No quantified consumption in the costed scenario*<br>Unresolved semiconductor inputs remain | No direct machine-part match in retained index |

### Cinnabar

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Redstone, sulfur / Cinnabar | 1 block | Redstone: ≈1<br>Sulfur: ≈0.2 dust | N/A | Crushing → washing | Saved design; expected chance-based outputs |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Redstone, sulfur / Cinnabar | No manufacturing recipe in retained index | Redstone control circuits; sulfur for chemistry | Controls plus chemical coproduct | 241,200–1,173,600 redstone dust*<br>53,000–241,200 sulfur dust*<br>264,900–1,206,200 shared cinnabar blocks* | No direct machine-part match in retained index |

### Ultramafic rock

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Ultramafic rock | 1 block | Osmium: ≈0.63%<br>Platinum: ≈0.225%<br>Iridium: ≈0.045% | ≈1,429 Os / 4,000 Pt / 20,000 Ir blocks | Trace nugget recovery | Draft chance per host block |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Ultramafic rock | No manufacturing recipe in retained index | Trace osmium, platinum and iridium recovery | Low-yield host feed | 3,652,500–16,225,600 ordinary host blocks*<br>Meets all three PGM demands jointly | No direct machine-part match in retained index |

### Osmium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Osmium-rich / Ultramafic rock | 1 rich ore block | 31.5–45 mB | 2–3 blocks | Crush → blast / vat | Saved rich-ore design; main product guaranteed by crushing. Vein mixture differs. |
| Osmium ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Osmium nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Osmium dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Osmium-rich / Ultramafic rock | No manufacturing recipe in retained index | Mekanism machinery and advanced alloys | Most accessible enriched PGM variant | 1,490–11,400 ingots*<br>213,100–1,622,600 vein blocks* | No direct machine-part match in retained index |
| Osmium ingot | Advanced Energy Cube<br>4 × Dynamic Tank<br>31 indexed recipes |  |  |  | Processor: Mechanical Crafters<br>Processor: Weathered Iron Press<br>Makes: Advanced Energy Cube |
| Osmium nugget | Concurrent Processor<br>Elite Control Circuit<br>3 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Makes: Concurrent Processor<br>Makes: Elite Control Circuit |
| Osmium dust | 4 × Osmiridium Ingot<br>1 indexed recipes |  |  |  | Processor: Alloy Smelter |

### Platinum

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Platinum-rich / Ultramafic rock | 1 rich ore block | 31.5–45 mB | 2–3 blocks | Crush → blast / vat | Saved rich-ore design; main product guaranteed by crushing. Vein mixture differs. |
| Platinum ingot | 1 ingot | 90 mB | 1 ingot | Foundry melting | Bundled conditional tag recipe; active override not verified |
| Platinum nugget | 1 nugget | 10 mB | 9 nuggets |  |  |
| Platinum dust | 1 dust | 90 mB | 1 dust |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Platinum-rich / Ultramafic rock | No manufacturing recipe in retained index | Specialty processing, electronics and alloys | Rare PGM specialist | 475–1,390 ingots*<br>67,900–198,700 vein blocks* | No direct machine-part match in retained index |
| Platinum ingot | Drive Upgrade<br>Elite Processor<br>11 indexed recipes |  |  |  | Processor: Assembler<br>Processor: Alloy Smelter<br>Makes: Drive Upgrade |
| Platinum nugget | Accumulation Processor<br>Concurrent Processor<br>5 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Processor: Industrial Iron Compacting<br>Makes: Accumulation Processor |
| Platinum dust | Refined Radiance<br>Platinum Heat Sink<br>3 indexed recipes |  |  |  | Processor: Industrial Iron Mixing<br>Processor: Alloy Smelter<br>Makes: Platinum Heat Sink |

### Iridium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Iridium-rich / Ultramafic rock | 1 rich ore block | 7–10 mB | 9–13 blocks | Crush → blast / vat | Saved rich-ore design; main product guaranteed by crushing. Vein mixture differs. |
| Iridium ingot (design unit) | 90 mB molten metal | 1 ingot | 1 casting unit | Sheet unit basis; exact casting recipe unverified | 90 mB design basis; not verified native remelting |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Iridium-rich / Ultramafic rock | No manufacturing recipe in retained index | High-tier alloys and advanced components | Rarest enriched PGM variant | 183–570 ingots*<br>26,100–81,500 vein blocks* | No direct machine-part match in retained index |
| Iridium ingot (design unit) | Warp Crystal<br>2 × Fusion Reactor Casing<br>20 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Processor: Mechanical Crafters<br>Makes: Warp Crystal |

### Vibranium

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Vibranium / Veridium | 1 block | ≈0.09–0.09 mB | 1000 blocks | Basic melting where allowed; crushing + best processing | Sheet draft; recipe/loot reconciliation pending |
| Vibranium ingot (design unit) | 90 mB molten metal | 1 ingot | 1 casting unit | Sheet unit basis; exact casting recipe unverified | 90 mB design basis; not verified native remelting |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Vibranium / Veridium | 2 × Cut Veridium Brick Slab<br>2 × Cut Veridium Slab<br>22 indexed recipes | Late-game Allthemodium progression and specialty components | Very rare endgame material | 40–88 ingots*<br>39,500–88,000 vein blocks* | Processor: Stonecutting<br>Processor: Crafting Shaped Retextured |
| Vibranium ingot (design unit) | Vibranium Plate<br>Drive Upgrade<br>21 indexed recipes |  |  |  | Processor: Sequenced Assembly<br>Processor: Smithing Transform<br>Makes: Drive Upgrade |

### Salt

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Salt / Salt block | 1 block | 4 salt | N/A | Mining | Bundled Mekanism loot; no Silk Touch |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Salt / Salt block | No manufacturing recipe in retained index | Brine and chlorine/caustic chemistry | Common reagent feed | Consumption not quantified*<br>Remaining chemical routes are unresolved | No direct machine-part match in retained index |

### Fluorite

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Fluorite / Normal ore | 1 block | 2–4 gems | N/A | Mining | Bundled Mekanism loot; no Fortune |
| Fluorite / Buried ore | 1 block | 2–4 gems |  |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Fluorite / Normal ore | No manufacturing recipe in retained index | Fluorine-based chemistry and nuclear processing | Specialist chemical feed | Consumption not quantified*<br>Exact chemical feed routes remain unresolved | No direct machine-part match in retained index |
| Fluorite / Buried ore | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |

### Crude oil

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Crude oil / Onshore field | 1,000 mB crude | 1,000 mB crude | N/A | Finite field extraction | Current field-size draft |
| Crude oil / Offshore field | 1,000 mB crude | 1,000 mB crude |  |  |  |
| Heavy oil | 1,000 mB crude | ≈176.47 mB |  | Crude distillation + one heavy-oil pass | Normalized per bucket; full crude distillation + one heavy-oil pass. Native batches apply; rounded output. |
| Diesel | 1,000 mB crude | ≈264.71 mB |  |  |  |
| Kerosene | 1,000 mB crude | ≈123.53 mB |  |  |  |
| Naphtha | 1,000 mB crude | ≈38.24 mB |  |  |  |
| Gasoline | 1,000 mB crude | ≈176.47 mB |  |  |  |
| LPG | 1,000 mB crude | ≈176.47 mB |  |  |  |
| Lubrication oil | 1,000 mB crude | ≈44.12 mB |  |  |  |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Crude oil / Onshore field | 120 mB Heavy Oil + 60 mB Diesel + 30 mB K...<br>120 mB Heavy Oil + 60 mB Diesel + 30 mB K...<br>3 indexed recipes | Fuels, lubricants, petrochemicals and plastics | Bulk petroleum supply | 1,834,200–8,401,400 buckets crude*<br>Petrochemicals + covered operating fuel<br>Single full distillation + heavy-oil pass | Processor: Distillation Tower |
| Crude oil / Offshore field | 120 mB Heavy Oil + 60 mB Diesel + 30 mB K...<br>120 mB Heavy Oil + 60 mB Diesel + 30 mB K...<br>3 indexed recipes |  |  |  | Processor: Distillation Tower |
| Heavy oil | 100 mB Heavy Oil + 25 mB Lubrication Oil ...<br>100 mB Heavy Oil + 30 mB Lubrication Oil ...<br>4 indexed recipes |  |  |  | Processor: Distillation Tower<br>Processor: Mechanical Press / Basin |
| Diesel | Fuel use defined by machine code; no manu... |  |  |  | TFMG Firebox<br>TFMG regular inline Diesel Engine |
| Kerosene | Fuel use defined by machine code; no manu... |  |  |  | TFMG Firebox<br>Fueled space-craft departure scenario |
| Naphtha | 250 mB Ethylene + 250 mB Propylene<br>1 indexed recipes |  |  |  | TFMG Firebox |
| Gasoline | 250 mB Napalm<br>1 indexed recipes |  |  |  | Processor: Mechanical Mixer |
| LPG | Lpg Tank<br>1 indexed recipes |  |  |  | TFMG Firebox |
| Lubrication oil | No manufacturing recipe in retained index |  |  |  | No direct machine-part match in retained index |

### Silicon

Yield and processing

| Resource / Input form | Input amount | Output / input | Inputs per ingot | Processing route | Evidence / assumptions |
|---|---|---|---|---|---|
| Quartz → silicon | 1 quartz | 40 mB liquid silicon | 3.6 quartz (average) | TFMG industrial blasting | Confirmed bundled TFMG recipe; live override not checked |
| Silicon ingot casting | 144 mB liquid silicon | 1 silicon ingot | 144 mB | TFMG casting | Confirmed TFMG native casting unit; differs from 90 mB sheet metal basis |

Uses and estimated demand

| Resource / Input form | Recipes using this input<br>Examples + indexed count | Industrial uses<br>(examples) | Supply / value role | Total estimated use*<br>Material + rock mined | Machines / parts<br>For this input form |
|---|---|---|---|---|---|
| Quartz → silicon | 2 × Annihilation Core<br>Redstone Link Wildcard<br>39 indexed recipes | Semiconductors and electronics | Electronics feed | 278,500–1,146,300 quartz items*<br>Includes silicon, glass and circuit inputs | Processor: Sequenced Assembly<br>Processor: Foundry Melting<br>Makes: Scorched Fuel Tank |
| Silicon ingot casting | Silicon Ingot<br>1 indexed recipes | Semiconductors, magnetic alloy and electronics |  |  | Processor: TFMG Casting |

## Other balance tables

### Full-bucket metal forms

September 11 installed accounting snapshot. Later recipe-specific records may use different units; this is not proof of current universal fluid accounting. [Source](industrial-colonies/design/BUCKET_BLOCK_MIGRATION.md).

| Form | Molten metal |
|---|---:|
| Nugget | 10 mB |
| Ingot | 100 mB |
| Finished metal storage block | 1,000 mB |

### Machine roles and capability tiers

Recorded progression reference. Later explicit Create-first exceptions and review decisions in Design Ideas take precedence. [Source](industrial-colonies/design/PROGRESSION_MACHINE_OWNERSHIP.md).

| Function | Primary family | Required boundary |
|---|---|---|
| Crushing/grinding | Create Crushing Wheels | Completely disable Mekanism Crusher and overlapping generic alternatives; include factory/upgrade bypasses in the audit. |
| Melting/casting | Modern Foundry | Retire competing bypasses. |
| Alloying | Create Mixer and designated capability tiers | Foundry alloying stays disabled, including automatic molten alloying. |
| Washing/airflow separation | Create Fans and Encased fan tiers | Overlapping washing machines must not bypass the assigned tier. |
| Chemicals/gases/acids/reagents | Primarily Mekanism | Chemical infrastructure remains useful; generic ore multiplication is not its role. |
| Oil refining | Primarily TFMG | Preserve its normal refining unless specifically modified. |
| Nuclear fuel/isotopes/reprocessing/enrichment/breeding | NuclearCraft where appropriate | Audit competing nuclear routes against this assignment. |

| Tier | Intended role |
|---|---|
| Basic/Andesite Create | Recognizable default machinery, logistics and mechanical automation. Retain normal recipes wherever possible. |
| Weathered Iron | First heavy industry and TFMG entry: structural parts, steel/reinforced/boiler plates, frames, mechanisms, bearings, valves, pumps and pressure hardware. Press forms parts; deployer assembles mechanical subassemblies. |
| Copper | Conductive parts, basic/intermediate electronics and precision electronic subassemblies. |
| Brass | More complex circuits, processors/control assemblies, denser electronics and the beginning of higher-voltage manufacture. |
| Train | Heavy electrical machinery, transformers, large coils, high-current switching, transmission, generators and traction hardware. Shares high-voltage work with Brass. |
| Industrial Iron | Advanced electromechanical heavy industry, Titanium/Tungsten structures, advanced electronics, harsh chemistry/metallurgy, stronger airflow and Refined Radiance-era work. |

### Ship damage, repair and encounter balance

October 12 proposal for review; values are not accepted or installed gameplay. [Source](industrial-colonies/design/SPACE_COMBAT_BALANCE_PROPOSAL.md).

| System | Starting proposal | Player-facing result |
|---|---|---|
| Low-speed contact | No additional hull damage below 1 block/second of closing speed along the contact normal | Docking bumps and stationary rubbing do not grind a ship apart. Native collision response still occurs. |
| Glancing contact | Measure normal closing speed at the actual contact point, including angular motion; tangential speed alone does not set damage | A scrape is less destructive than a direct impact at the same overall speed. |
| Moderate impact | From 1 to 3 blocks/second, allow localized wear only; no newly removed blocks | Pilots get visible damage to repair before structural failure. Exact visual implementation is separate. |
| Damaging impact | From 3 to 7 blocks/second, allow local hull failure, beginning at the contact surface | A collision damages the nose or wing that hits, rather than random distant blocks. |
| Severe crash | At 7 blocks/second or above, permit deeper local damage and native splitting when structural connections are actually lost | A ship can break apart because its connecting structure is destroyed. There is no scripted whole-ship explosion. |
| Damage work budget | At most 16 structural removals from one fresh contact episode, 32 per ship per server tick, and 64 globally per server tick | Limits sudden server work. A cap does not authorize repeatedly charging a resting contact. |
| Contact deduplication | Aggregate solver contacts for the same body pair and local impact region; release the episode after 10 separated ticks | Multiple physics substeps cannot multiply one impact into dozens of independent hits. |
| Material resistance | Start with native block resistance where meaningful; compare accepted hull materials in a calibration fixture before setting multipliers | Better hull construction matters. Decorative blocks do not become arbitrary invulnerable armor. |
| Repair access | Manual repairs while safely held; dockside maintenance for substantial reconstruction | Emergency patching is possible, while major repairs support a workshop and supply line. |
| Repair cost | Replace missing blocks with the exact corresponding blocks; repair wear using matching plate/frame parts, with no upgrade in material grade | A cheap patch does not turn into stronger armor or a complete free machine. |
| Repair throughput | Proposed dockside limit: one ordinary hull block per second; machinery reinstatement requires its real finished item | Large repairs have a time and manufacturing cost. No final recipe price is implied. |
| Cargo damage | Structural hull damage first; inventory-bearing blocks enter the damage pool only after their native break/drop and restart behavior is qualified | Storage is not permanently invulnerable, but an untested duplicate/drop path cannot be enabled. |
| Fragments | Let Sable perform topology splitting. Preserve physical cargo and body lineage; stop invalidated automation leases | Broken sections remain actual wreckage. Splitting never manufactures a second owner, inventory or encounter reward. |
| Empty debris | Proposed cleanup after 10 unloaded minutes, only for verified empty NPC debris with no player ownership or boarding | Abandoned empty debris can be reclaimed without deleting valuable wrecks. Time alone never authorizes cargo deletion. |
| Salvage | Surviving hull blocks and existing cargo are the initial reward; no extra loot roll for the same recovered material | Salvage is useful without paying twice for one wreck. Additional encounter rewards need their own durable once-only receipt. |
| First encounter | One scout, one pass, at most one native shot, then retreat | Introduces hostile ships without an endless chase or immediate fleet battle. This matches the bounded shape of the existing controller. |
| Escalation | Start with one active encounter per participating player and two globally; do not escalate from inventory value or total playtime alone | Carrying valuable freight does not secretly summon a stronger opponent. Actual supported defensive hardware and an explicit encounter tier determine eligibility. |
| Encounter pacing | Proposed 15-minute quiet interval after completion, plus 0–5 minutes of deterministic jitter; held/unresolved encounters occupy their reservations | Predictable minimum recovery time, without restart farming or repeated rerolls. Automatic spawning stays off until its full admission path is qualified. |
| Target selection | Explicitly approved player-owned targets or commissioned hostile NPCs; friendly exclusion wins | A neutral base, unrelated ship, or nearby player cannot become collateral merely by being close. |
| Warning and escape | Proposed 10-second warning before approach; failed safety or ownership checks hold, and no automatic resume follows | Players can understand the threat. A repaired sensor or re-enabled switch does not unexpectedly resume firing. |
| Weapon economy | Native ammunition, loading and cooldowns; no infinite ammunition or shortened cooldown to fit a design target | Manufacturing and resupply constrain firepower. Existing one-shot tests do not justify sustained volleys. |
| Retreat | Disengage on lost propulsion, unsafe clearance, invalid aim, ammunition exhaustion or loss of target authority | A damaged AI should not teleport or issue impossible thrust demands to continue fighting. |
| Boss encounter | An explicit late-game opt-in mission, separate from ambient scouts | A large battle cannot appear while the player is still learning the first ship systems. Boss geometry, weapons and rewards remain unbuilt. |
| Jetpacks and storage | Keep the recorded transport-preserving limits: short personal flight, modest portable tanks, late digital storage | A jetpack or pocket tank should not replace ships, trains, vaults and bulk logistics. Exact item-specific values belong to their balance tasks. |

### Structure placement changes

Recorded placement reference; latest spacing and habitat decisions above take precedence. [Source](industrial-colonies/design/STRUCTURE_CLEANUP.md).

| Content | Result |
|---|---|
| Modern Foundry ocean islands | Spacing 96, separation 48 chunks; frequency 0.05, previously spacing 30 / frequency 0.5 |
| Modern Foundry sky islands | Spacing 128, separation 64 chunks; frequency 0.05, previously spacing 35 / frequency 0.5 |
| Large surface ships | One shared `industrial_colonies:rare_maritime_sites` structure set, spacing 128 / separation 64 chunks |
| CTOV jungle and jungle-tree villages | Disabled for small, medium and large sizes |
| Block Factory Dragon Tower | Eligible only in the installed Ad Astra and Stellaris Venus biomes |

## Earlier comparison tables

These tables preserve previous comparisons and proposals, not additional current balance selections. They are collapsed to keep the main reference readable. Later corrections and the combined Earth chart take precedence. Technical audit/checklist tables remain with their evidence documents rather than being presented as gameplay balance.

<details>
<summary>Earlier rarity, reserve, biome, spacing, metal-unit and recovery tables</summary>

### Earlier continent rarity proposal

Historical/reference snapshot only; preserve source qualifications and later corrections. [Source](industrial-colonies/design/CONTINENT_RARITY_PROPOSAL.md).

| Family | Proposed percent |
|---|---:|
| Coal |100|
| Sphalerite / zinc |90|
| Chalcopyrite / copper |85|
| Cinnabar / redstone |85|
| Dolomite / magnesium |80|
| Magnetite — selected |70|
| Hematite — selected |40|
| Any major iron, combined — proposal only |75|
| Graphite rock |75|
| Bauxite / aluminum |70|
| Galena / lead |70|
| Cassiterite / tin |65|
| Phosphate rock / phosphorus |65|
| Pentlandite / nickel |45|
| Borax / boron |45|
| Ilmenite / titanium |40|
| Spodumene / lithium |40|
| Chromite / chromium |35|
| Argentite / silver |35|
| Gold |25|
| Wolframite / tungsten |25|
| Uraninite / uranium |20|
| Standalone thorium |20|
| Bertrandite / beryllium |15|
| Ultramafic / osmium-platinum-iridium |15|

### Earlier deposit sizes v2

Historical/reference snapshot only; preserve source qualifications and later corrections. [Source](industrial-colonies/design/EARTH_DEPOSIT_SIZE_PROPOSAL.md).

| Deposit | Resource | Presence % | Small ore blocks | Medium | Large/cap | Small % | Medium % | Large % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| coal | Coal | 100 | 8000 | 35000 | 100000 | 80 | 18 | 2 |
| sphalerite | Zinc | 90 | 5000 | 20000 | 75000 | 80 | 18 | 2 |
| chalcopyrite | Copper | 85 | 6000 | 25000 | 90000 | 80 | 18 | 2 |
| cinnabar | Redstone | 85 | 3000 | 12000 | 50000 | 80 | 18 | 2 |
| dolomite | Magnesium | 80 | 4000 | 15000 | 60000 | 80 | 18 | 2 |
| graphite_rock | Graphite | 75 | 5000 | 20000 | 80000 | 80 | 18 | 2 |
| magnetite | Iron | 70 | 5000 | 25000 | 100000 | 80 | 19 | 1 |
| bauxite | Aluminum | 70 | 6000 | 25000 | 90000 | 80 | 18 | 2 |
| galena | Lead | 70 | 3000 | 12000 | 50000 | 85 | 13 | 2 |
| cassiterite | Tin | 65 | 2000 | 8000 | 35000 | 85 | 13 | 2 |
| phosphate_rock | Phosphorus | 65 | 4000 | 18000 | 70000 | 80 | 18 | 2 |
| pentlandite | Nickel | 45 | 3000 | 12000 | 50000 | 85 | 14 | 1 |
| borax_rock | Boron | 45 | 1000 | 5000 | 20000 | 85 | 14 | 1 |
| hematite | Iron | 40 | 2000 | 10000 | 50000 | 90 | 9 | 1 |
| ilmenite | Titanium | 40 | 3000 | 15000 | 65000 | 85 | 14 | 1 |
| spodumene_rock | Lithium | 40 | 1500 | 7000 | 30000 | 85 | 14 | 1 |
| chromite | Chromium | 35 | 2000 | 10000 | 40000 | 85 | 14 | 1 |
| argentite | Silver | 35 | 1000 | 4000 | 20000 | 90 | 9 | 1 |
| gold | Gold | 25 | 1000 | 5000 | 20000 | 90 | 9 | 1 |
| wolframite_rock | Tungsten | 25 | 1500 | 8000 | 35000 | 85 | 14 | 1 |
| uranium | Uranium | 20 | 750 | 4000 | 20000 | 90 | 9 | 1 |
| thorium | Thorium | 20 | 1000 | 5000 | 25000 | 90 | 9 | 1 |
| bertrandite | Beryllium | 15 | 500 | 2500 | 15000 | 90 | 9 | 1 |
| ultramafic_rock | Osmium/platinum/iridium | 15 | 2000 | 10000 | 50000 | 90 | 9 | 1 |

### Superseded deposit sizes v1

Historical/reference snapshot only; preserve source qualifications and later corrections. [Source](industrial-colonies/design/EARTH_DEPOSIT_SIZE_PROPOSAL_v1.md).

| Deposit | Resource | Presence % | Small ore blocks | Medium | Large/cap | Small % | Medium % | Large % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| coal | Coal | 100 | 2000 | 20000 | 100000 | 80 | 18 | 2 |
| sphalerite | Zinc | 90 | 2000 | 12000 | 60000 | 80 | 18 | 2 |
| chalcopyrite | Copper | 85 | 2000 | 15000 | 80000 | 80 | 18 | 2 |
| cinnabar | Redstone | 85 | 1500 | 10000 | 50000 | 80 | 18 | 2 |
| dolomite | Magnesium | 80 | 2000 | 15000 | 80000 | 80 | 18 | 2 |
| graphite_rock | Graphite | 75 | 2000 | 15000 | 75000 | 80 | 18 | 2 |
| magnetite | Iron | 70 | 2000 | 20000 | 100000 | 80 | 19 | 1 |
| bauxite | Aluminum | 70 | 2000 | 15000 | 80000 | 80 | 18 | 2 |
| galena | Lead | 70 | 1500 | 10000 | 50000 | 85 | 13 | 2 |
| cassiterite | Tin | 65 | 1500 | 8000 | 40000 | 85 | 13 | 2 |
| phosphate_rock | Phosphorus | 65 | 2000 | 12000 | 60000 | 80 | 18 | 2 |
| pentlandite | Nickel | 45 | 1500 | 10000 | 50000 | 85 | 14 | 1 |
| borax_rock | Boron | 45 | 1000 | 6000 | 30000 | 85 | 14 | 1 |
| hematite | Iron | 40 | 2000 | 10000 | 50000 | 90 | 9 | 1 |
| ilmenite | Titanium | 40 | 2000 | 12000 | 60000 | 85 | 14 | 1 |
| spodumene_rock | Lithium | 40 | 1000 | 6000 | 30000 | 85 | 14 | 1 |
| chromite | Chromium | 35 | 1500 | 8000 | 40000 | 85 | 14 | 1 |
| argentite | Silver | 35 | 1000 | 5000 | 25000 | 90 | 9 | 1 |
| gold | Gold | 25 | 1000 | 5000 | 20000 | 90 | 9 | 1 |
| wolframite_rock | Tungsten | 25 | 1000 | 8000 | 40000 | 85 | 14 | 1 |
| uranium | Uranium | 20 | 1000 | 6000 | 30000 | 90 | 9 | 1 |
| thorium | Thorium | 20 | 1000 | 6000 | 30000 | 90 | 9 | 1 |
| bertrandite | Beryllium | 15 | 1000 | 4000 | 20000 | 90 | 9 | 1 |
| ultramafic_rock | Osmium/platinum/iridium | 15 | 1000 | 6000 | 30000 | 90 | 9 | 1 |

### Earlier deposit spacing proposal

Historical/reference snapshot only; preserve source qualifications and later corrections. [Source](industrial-colonies/design/CONTINENT_RESOURCE_DISTRIBUTION.md).

| Deposit/resource | Preferred nearest independent deposit distance (blocks) |
|---|---:|
| Coal | 1,000–3,000 within a coal district |
| Sphalerite — zinc | 3,000–5,000 |
| Chalcopyrite — copper | 3,000–5,000 |
| Cinnabar — redstone | 3,000–5,000 |
| Dolomite — magnesium | 3,000–5,000 |
| Graphite | 3,000–5,000 |
| Magnetite — iron | 3,000–5,000 |
| Bauxite — aluminum | 4,000–6,000 |
| Galena — lead | 3,000–5,000 |
| Cassiterite — tin | 3,000–5,000 |
| Phosphate rock | 4,000–6,000 |
| Pentlandite — nickel | 4,000–6,000 |
| Borax — boron | 4,000–6,000 |
| Hematite — iron | 4,000–6,000 |
| Ilmenite — titanium | 4,000–6,000 |
| Spodumene — lithium | 4,000–6,000 |
| Chromite — chromium | 4,000–6,000 |
| Argentite — silver | 4,000–6,000 |
| Gold | 5,000–7,000 |
| Wolframite — tungsten | 5,000–7,000 |
| Uranium | 5,000–7,000 |
| Thorium | 5,000–7,000 |
| Bertrandite — beryllium | 5,000–7,000 |
| Ultramafic — osmium/platinum/iridium | 5,000–7,000 |
| Crude oil field | 4,000–6,000 |

### Earlier ore-to-biome proposal

Historical/reference snapshot only; preserve source qualifications and later corrections. [Source](industrial-colonies/design/ORE_BIOME_PROPOSAL.md).

| Resource | Proposed biomes / terrain |
|---|---|
| Coal | Plains, forests, taiga, foothills |
| Zinc — sphalerite | Plains, meadows, forests, foothills |
| Copper — chalcopyrite | Plains, wooded hills, mountains, badlands |
| Redstone — cinnabar | Frozen Peaks, Jagged Peaks, Snowy Slopes, Icy Heights, Spires; retain the existing high-elevation requirement |
| Magnesium — dolomite | Plains, meadows, chalk cliffs, dry plateaus |
| Graphite | Forested hills, taiga, mountain foothills |
| Iron — magnetite | Plains, forests, taiga, hills, mountains |
| Aluminum — bauxite | Jungles, rainforests, savannas, warm woodlands |
| Lead — galena | Plains, forests, foothills, chalk cliffs |
| Tin — cassiterite | Wooded hills, mountains, highland river valleys |
| Phosphorus — phosphate rock | Plains, dry basins, coastal plains |
| Nickel — pentlandite | Rocky mountains, stony highlands, Ashen Woodland |
| Boron — borax | Deserts, badlands, dry inland basins |
| Iron — hematite | Badlands, savannas, dry hills, exposed mountain slopes |
| Titanium — ilmenite | Beaches, stony shores, coastal dunes; keep initial major deposits on land |
| Lithium — spodumene | Rocky hills, mountains, highland meadows |
| Chromium — chromite | Rocky mountains, stony highlands, Ashen Woodland |
| Silver — argentite | Mountains, wooded highlands, badlands |
| Gold | Badlands, dry plateaus, mountain foothills; separate river placer route remains its own design |
| Tungsten — wolframite | Mountains, rocky highlands, cold mountain slopes |
| Uranium | Badlands, deserts, rocky highlands |
| Thorium | Rocky highlands, wooded hills, selected coastal sand districts |
| Beryllium — bertrandite | Arid mountains, desert hills, rocky highlands |
| Osmium / platinum / iridium — ultramafic rock | Rocky mountains, stony highlands, Ashen Woodland |
| Crude oil | Deserts, badlands, savannas; retain current dry-biome scope |

### Historical whole-mB migration

Historical/reference snapshot only; preserve source qualifications and later corrections. [Source](industrial-colonies/design/METAL_UNIT_MIGRATION.md).

| Feed | Old mB | New mB | New feed per ingot |
|---|---:|---:|---:|
| Hematite or magnetite, directly melted | 25 | 3 | 34 pieces yield 102 mB |
| Reduced iron fraction | 75 | 8 | 13 pieces yield 104 mB |
| Raw iron | 200 | 20 | 5 |
| Raw copper or zinc | 125 | 13 | 8 pieces yield 104 mB |
| Processed copper dust | 50 | 5 | 20 |
| Gold flake | 1 | 1 | 100 |

### Historical basic and improved ore recovery

Historical/reference snapshot only; preserve source qualifications and later corrections. [Source](industrial-colonies/design/ORE_RECOVERY_BALANCE.md).

| Feed | Basic melting | Improved recovery per feed | Route |
|---|---:|---:|---|
| Rich iron's raw iron | 25 mB | 100 mB | Native TFMG blast furnace |
| Low-grade hematite/magnetite | 3 mB | 8 mB | Crush, then TFMG blast reduction |
| Rich copper's raw copper | 15 mB | 100 mB | Crush into four chalcopyrite feeds, wash, melt |
| Chalcopyrite | 4 mB | 25 mB | Crush, wash, melt |
| Rich zinc's raw zinc | 12 mB | 60 mB | Crush into four sphalerite feeds, then existing chemical recovery |
| Sphalerite | 2 mB | 15 mB | Existing leach, precipitation and reduction |
| Raw gold | 10 mB | 25 mB | Native TFMG blast processing |
| Cassiterite | 3 mB | 20 mB | Existing gravity concentration; rich tin gives four concentrates = 80 mB |
| Galena | 3 mB | 20 mB | Roast and reduce; rich galena gives four feeds = 80 mB |
| Argentite | 2 mB | 10 mB | Existing chemical extraction |

### Ordinary rock-item recovery proposal

Historical/reference snapshot only; preserve source qualifications and later corrections. [Source](industrial-colonies/design/SURFACE_ORES_AND_HEMATITE.md).

| Ordinary rock item | Latest recovery target |
| --- | ---: |
| Magnetite | About 1 mB per item |
| Hematite | 25 mB per item |

### Earlier staged ship AE2 behavior

Historical/reference snapshot only. Its source records scope and superseding decisions; old drive-stabilization rules are superseded by chest-only Matter Stabilizer direction. [Source](industrial-colonies/design/SHIP_AE2_LIMITS.md).

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
| Stability anchor | Registered `industrial_colonies:matter_stabilizer` block/item and non-ticking marker. Passive presence gate; no invented FE operating cost. |

</details>

For implementation evidence, outstanding decisions and all original checkpoint entries, see [Design Ideas](DESIGN_IDEAS.md). Keep future discussion and chronological updates there; keep this README focused on the to-do list and reference tables.
