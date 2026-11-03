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

### Latest basic rock melting and Vibranium targets

October 26–27 records take precedence over the older processing table below. Installation records do not establish a subsequent gameplay reload. Rich/raw and chemical-only routes were not changed by the basic-rock correction.

| Input / route | Recorded yield | Status |
|---|---:|---|
| Ordinary hematite, basic melting | 3 mB/item | Installed October 26; reload/play verification separate |
| Ordinary magnetite, basic melting | 3 mB/item | Same |
| Chalcopyrite, basic melting | 4 mB/item | Same |
| Cassiterite, basic melting | 3 mB/item | Same |
| Galena, both supported identities, basic melting | 3 mB/item | Same |
| Argentite, basic melting | 2 mB/item | Same |
| Ordinary sphalerite, basic melting | 2 mB/block | Installed fixed output; no ore multiplier or copper byproduct; 45 blocks per recorded 90 mB zinc ingot |
| Ordinary magnetite, proposed revised recovery | About 1 mB/item | Design target; basic/improved mapping unreviewed, not the installed 3 mB basic route |
| Ordinary hematite, proposed revised recovery | 25 mB/item | Same unresolved route distinction |
| Vibranium, best full-deposit processing | Small 10 / medium 35 / large 100 ingots | October 27 selected tiers; ore-count conversion and shared formation accounting pending; supersedes older 20–30-ingot total |
| P / N semiconductor assembly | 5 semiconductors | October 29 design direction; empty circuit-board workpiece; green P uses gold/copper, pink N also electrum; actual saved/runtime state must be checked |

### Recorded full production-yield table

Retained from the October 19 design table. Entries marked draft/pending remain proposals. It preserves historical arithmetic and mixed metal-unit assumptions; **do not use it as a verified installed recipe catalog**. Use the latest correction table above for basic rock melting and Vibranium. Full reconciliation against current recipes remains open.

| Ore input | Crushing / collection | Amount per input | Seared Smelter output | Blast Furnace output | Fireproof Vat / final recovery |
|---|---|---|---|---|---|
| Magnetite / Rich Magnetite | Crushed Raw Iron | 1 / 3 | 3 / 9 mB iron | Separate steel recipe, later | Fireproof Vat: 10 mB iron/output; 10 / 30 mB per ore |
| Hematite / Rich Hematite | Crushed Raw Iron | 5 / 9 | 15 / 30 mB iron | Separate steel recipe, later | Fireproof Vat: 10 mB iron/output; 50 / 90 mB per ore |
| Sphalerite / Rich Zinc | Crushed Raw Zinc | 6 / 12 (draft) | Not assigned | Not assigned | Heated Steel Chemical Vat: 10 mB zinc/output target; 60 / 120 per ore |
| Chalcopyrite / Rich Copper | Crushed Raw Copper | 6 (draft) / 10 | Not assigned | Not assigned | 10 mB copper/output target; 60 / 100 per ore; machine pending |
| Bauxite / Rich Bauxite | TFMG Bauxite Powder | 6 / 12 | No direct ore melting | Not assigned | Heated Steel Chemical Vat, centrifuge + side electrodes; 10 mB aluminum/powder target; CO2 byproduct amount pending |
| Galena / Rich Galena | Crushed Galena | 3 / 6 (draft) | Not assigned | Not assigned | 10 mB lead/output target; 30 / 60 per ore |
| Cassiterite / Rich Tin | Crushed Raw Tin | 2 / 4 (draft) | Not assigned | Not assigned | 10 mB tin/output target; 20 / 40 per ore |
| Pentlandite / Rich Nickel | Crushed Raw Nickel | 2 / 4 (draft) | No direct ore melting selected | Not assigned | 10 mB nickel/output target; 20 / 40 per ore; machine pending |
| Argentite / Rich Silver | Crushed Raw Silver | 1 / 2 (draft) | Not assigned | Not assigned | 10 mB silver/output target; 10 / 20 per ore |
| Gold ore / Deepslate Gold ore | Crushed Raw Gold | 1 (draft) | Not assigned | Not assigned | 10 mB gold/output target |
| Ilmenite / Rich Titanium | Crushed Raw Titanium | 2 / 4 (draft) | No direct ore melting selected | Not assigned | 10 mB titanium/output target; 20 / 40 per ore; machine pending |
| Chromite / Rich Chromium | Chromium Dust | 1 / 4 | Not assigned | Earlier batch proposal: 4 dust -> 70 mB; machine pending | Fireproof Vat: 4 dust -> 90 mB chromium; 22.5 mB/dust equivalent; normal 22.5 / rich 90 |
| Wolframite / Rich Tungsten | Crushed Raw Tungsten | 1 / 2 (draft) | No direct ore melting selected | Not assigned | 10 mB tungsten/output target; 10 / 20 per ore; machine pending |
| Spodumene rock / Spodumene ore | Crushed Raw Lithium | 1 / 3 (draft) | No direct ore melting selected | Not assigned | 10 mB lithium/output target; 10 / 30 per input; machine pending |
| Dolomite | Magnesium Dust | 2 (draft) | Not assigned | Not assigned | 10 mB magnesium/dust target; 20 per ore |
| Bertrandite | Beryllium Dust | 1 (draft) | Not assigned | Not assigned | 10 mB beryllium/dust target |
| Borax rock | Boron Dust | 1 (draft) | Not assigned | Not assigned | 10 mB boron/dust target |
| Cobalt ore | Cobalt Dust | 1 (draft) | Not assigned | Not assigned | 10 mB cobalt/dust target |
| Uraninite | Crushed Raw Uranium | 1 (draft) | Not assigned | Not assigned | Mekanism processing retained; 10 mB/output balance target, exact recipe pending |
| Thorium ore | Thorium Dust | 1 (draft) | Not assigned | Not assigned | 10 mB/dust balance target; nuclear recipe pending |
| Ultramafic rock | Osmium Dust / Platinum Dust / Iridium Dust / Lime Sand | 14% 1 / 5% 1 / 1% 1 / 80% 1 | Not assigned | Not assigned | Metal-dust targets 10 mB/output (draft); independent rolls |
| Rich Osmium ore | Crushed Raw Osmium + Lime Sand | 80% 1 crushed + 20% 1 sand | Not assigned | Not assigned | 45 mB/successful crushed item; 36 mB expected per ore |
| Rich Platinum ore | Crushed Raw Platinum + Lime Sand | 80% 1 crushed + 20% 1 sand | Not assigned | Not assigned | 45 mB/successful crushed item; 36 mB expected per ore |
| Rich Iridium ore | Iridium Dust + Lime Sand | 80% 1 dust + 20% 1 sand | Not assigned | Not assigned | 10 mB/dust target (draft); 8 mB expected per ore |
| Coal ore | Mining -> Coal; no crushing | 1 | Not a metal | Not a metal | 1 Coal |
| Graphite rock | Graphite Dust | 1 | Not a metal | Not a metal | 1 Graphite Dust; electrodes are separate |
| Cinnabar | Cinder Flour | 2 | Not a metal | Not a metal | 2 Cinder Flour; replace old netherrack crushing on export |
| Calcite | Calcium Dust + Potassium Dust | 40% 1 calcium + 20% 1 potassium | Not assigned | Not assigned | Independent output rolls; downstream chemicals separate |
| Phosphate rock | Industrial Colonies Phosphate Dust | 1 | Not a metal | Not a metal | 1 Phosphate Dust; white texture requested |
| Diamond-bearing ore | Intact Diamond | 75% 1 (draft) | Not a metal | Not a metal | Expected 0.75 Diamond per ore |
| River gold-flake deposit | Collect Gold Flakes | 1-3 | Batch recipe pending | Not assigned | 2 flakes -> 1 mB gold; lone flake waits; 0.5 mB/flake |
| Finished Gold Dust | Grind finished Gold Ingot -> dust | 1 | 90 mB gold/dust target | Same full-ingot value | 90 mB gold/dust = 1 ingot |
| Crude oil | Finite field extraction | No crushing | Not a metal | Not a metal | Onshore 5M / 25M / 100M mB; offshore always 100M, very rare |
| Gas-giant gases | Late-game bulk extraction | Rates pending | Not a metal | Not a metal | Scale extraction/storage/shipping to high late-game chemical demand |

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
