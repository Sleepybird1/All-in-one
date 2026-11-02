> October 10 authority: [current combined chart](EARTH_RESOURCE_MASTER_CHART.md), including actual Y levels, guaranteed exposed cinnabar with height fade, graphite/diamond and river-gold exceptions, osmium-group restrictions and gas-giant bulk supply. Conflicting earlier values below are historical; no implementation is implied.

# Continent resource distribution â€” October 10, 2026

Status: user design direction recorded from in-game voice discussion. NOT_IMPLEMENTED; no generation, production saves or recipes changed. Use ReTerraForged's continent system as the intended geographical basis; stable continent identity and generation feasibility still require investigation.

## Main deposit direction

Oil addition accepted in the recipe-review conversation:50%presence on suitable continents; small5,000,000mB, medium25,000,000mB, large100,000,000mB with proposed table's80/18/2size distribution. One shared finite recoverable reserve per field, never per pumpjack. Design acceptance only; native reservoir grouping and demand calibration remain unqualified. Oil uses fluid amounts, not ore-block caps.

Latest explicit user-selected presence rates: **magnetite70%, hematite40%**. These supersede the assistant magnetite60%proposal. Their overlap and combined any-iron rate remain undecided;75%combined was an assistant proposal, not user-approved. One possible coordinated allocation is35%magnetite-only,5%hematite-only,35%both,25%neither. No generation changes.

Iron rarity follow-up: user rejects the proposed95%iron/magnetite presence as too high. No replacement percentage is approved. Evaluate the combined chance of accessible iron across magnetite, hematite and other retained sources; independent rolls can unintentionally make iron nearly guaranteed. A75%any-iron-family roll is an assistant suggestion only, not selected settings.

Latest rarity correction: the user rejects the assistant's5%hematite proposal and says hematite/rich hematite should not be rarer than gold. This supersedes the older extremely-rare-Earth-hematite direction where it conflicts. Compare actual access to rich hematite as well as parent-deposit presence; a vanishing rich-grade fraction must not defeat that intent. Exact continent probabilities and rich fractions remain open. The assistant's displayed24-family probability table is a proposal, not approved generation settings; gold25%was also only a proposal.

Latest user clarification supersedes the initial single-ore-type interpretation: **every resource type may occur on the same continent**, with its own presence rules, abundance and deposit pattern. Continents should differ substantially in their resource supply; some resources can be absent. Iron should be relatively dependable because factory demand is high; gold may be absent entirely. The earlier approximately75%presence suggestion is not a finalized universal probability for every ore. No fixed numerical per-resource chances have been approved.

Continent size and available placement room should influence resource presence and deposit sizes/counts. A small continent may lack room for a resource's deposit, in which case that deposit can be absent rather than forced in. This depends on whether ReTerraForged can provide a suitable, stable continent identity and size/space measure during generation; that capability is NOT_VERIFIED. Do not silently implement repeated per-chunk chances or replace continent identity with arbitrary grid cells. Earlier single-vein language is superseded by per-resource patterns, not an instruction to restrict an entire continent to one mineral.

Approximate proposed sizes, measured as ore-block targets rather than bounding-box volume:

- Small:1,000â€“2,000 blocks.
- Medium:10,000 blocks.
- Large:100,000 blocks.

Later size clarification: **Earth deposits should top out at100,000actual ore blocks, with deposits at that upper end rare**. Hematite gets a lower proposed family limit: large deposits around50,000ore blocks maximum, small deposits around2,000. Its medium size and size-selection probabilities remain undecided. These are ore-block reserve targets, not ingots, rectangular volume or per-continent total reserves. Preserve all normal/rich/associated ore accounting when enforcing a deposit cap; rich hematite is a grade within the hematite deposit, not an extra uncapped duplicate body. The user floated500,000-scale deposits on Mars as a future possibility, not an approved planetary setting. Existing larger staged test formations are historical capability evidence, not this new Earth balance target. No generated terrain is edited.

These are design targets, not a tested generator distribution. Size-category frequencies, ore-selection weights, rich-grade fraction, underground geometry, islands/continent boundaries and treatment of existing terrain remain open. Existing tiny surface/prospecting clues and rare hematite rules must be reconciled explicitly; do not remove those independent systems based on this note alone.

## Coal pattern exception

Coal should be more abundant and vary substantially by continent. Latest examples expand the earlier fixed alternatives: one or two small deposits on some continents, up to around six small deposits on others, or two medium deposits, or one large deposit. The user states that each continent should have at least one small deposit while discussing coal; record that as the coal minimum, not a guarantee of every mineral. Whether a medium/large deposit replaces that small minimum or accompanies it, and how it applies to tiny islands, remain unspecified. Earlier three/four-small examples are not a final hard cap. Do not sum all example layouts together. Exact weights and coal-specific size targets remain open. Coal can coexist with other ores under the clarified multiple-resource continent model.

## Economy and iron recovery goals

Large deposits should be valuable and long-lived but exhaustible. A100,000-block iron deposit should support sustained factories rather than instantly trivialize iron supply. Continued industrial demand should create recurring pressure to mine, process and transport more iron; routine enormous idle stockpiles are not the desired balance. This is an economy goal, not a promise that every player's inventory stays scarce or a request to delete/cap stored items.

Evaluate actual ore drops, rich-grade share, full-route recovery, throughput, fuel/reagents, material recycling and recurring factory demand together. Crushing outputs and subsequent recovery multiply; avoid counting each stage as independent new ore. Deposit lifetime equals recoverable iron divided by net consumption rate, with transport and mining throughput also constraining supply. Final numeric balancing waits for the user-defined recipes; no measured factory demand is available from this conversation.

Current explicit iron anchor: **one rich hematite ore yields one full iron ingot only through the fireproof vat**. Other ore grades and earlier routes remain below one ingot per original ore. Ordinary chemical vat gets no iron-production route. Seared Smelter remains the low-yield starter. Lower yields remain undecided; do not adopt the assistant's rejected three-tier table. Steel-making is separate: starter blast furnace low yield, later fireproof vat highest efficiency, provisional Weathered Iron entry gate.

Next: finish recipe yields with user, then audit continent identity/size APIs before choosing per-resource presence, placement budgets and generation code. Coal coexistence and multiple ore types are now clarified; coal minimum semantics and exact numeric distribution remain open. No task completion credit from recording this direction.


## Continent measurement marker — October 10

User supplied **X 5812, Z 23369** while measuring continent size. This is **not** a resin/tree location. A second endpoint and the intended measurement direction are not yet supplied; do not infer a continent diameter from this point alone.

Second user-reported continent edge: **X 17252, Z 23459**. Between the two reported endpoints: X span **11,440 blocks**, Z offset **90 blocks**, horizontal straight-line distance **11,440.35 blocks** (about **11.44 km** at one metre per block). This is one measured cross-continent line, not the maximum diameter, coastline length, area, or verified ReTerraForged continent boundary.

User-reported **northern coastline marker: X 12529, Z -8553** (tundra transitioning to frozen ocean). Not independently verified as the same continent. A southern edge is still needed for full north-south extent; the earlier west/east markers are not assumed to be southern extrema. The earlier measured line is almost east-west, not a southwest-to-northeast diagonal.

User-reported **southernmost coastline marker: X 10086, Z 24049**. North-south Z span from the reported northern marker is **32,602 blocks**; east-west offset is **2,443 blocks**; straight-line endpoint distance is **32,693.40 blocks**. Combined surveyed dimensions are approximately **11,440 blocks across the earlier east-west transect and 32,602 blocks north-south**. The east-west transect is not proven to be the maximum width. Do not infer land area or formal continent membership from these four user-reported markers.

## Per-resource spacing proposal — not approved or implemented

Soft preferred horizontal distance from a deposit centre to its nearest independent major deposit, in blocks. Not repeated same-ore spacing: normally one major deposit per present non-coal family per continent. These ranges are design starting points, not a simulated feasible layout or calibrated economy. They cannot all be enforced as exact pairwise distances. Use a proposed 2000-block minimum between unrelated major centres; coal district members may be1000apart. Associated minerals inside one deposit are exempt. Larger specialty distances are soft preferences, not an extra probability roll or a reason to silently remove an otherwise selected resource. Fit to actual land/geology and report unmet placement constraints; validate continent detection and packing before implementation. Oil distances refer to fields, not pumpjacks.

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

Coal row describes spacing within its own district; use the unrelated-major minimum for other resource types. An occasional8,000–12,000-block empty stretch can arise from land/geology; it is not imposed around every rare deposit. Presence probabilities and reserves remain separate decisions.

## Biome restrictions and reasonable replacement travel — user clarification

Certain ores must remain restricted to their designated biomes. Apply existing approved biome/geology eligibility before the proposed soft spacing preferences; never place an ore in an ineligible biome to satisfy spacing. Exact ore-to-biome assignments are not newly selected here and must be reconciled with the existing catalog.

User rejects punitive or gimmicky travel, specifically needing to travel100000blocks for replacement iron after depletion. No numeric maximum travel distance was approved. Validate the combined effect of continent presence, eligible-biome availability, deposit counts, reserves and spacing on replacement access; do not claim a3–5kinter-deposit target guarantees nearby iron. Where eligible land cannot fit the draft, report the constraint and revisit soft spacing/counts with the existing design rather than silently weakening biome restrictions or inventing a hard travel guarantee.

## Offshore oil — user decision

Ocean oil is allowed as a separate offshore field category. It should be **very rare**, with **every offshore field fixed at100000000mB** (100million mB), shared per field rather than per pumpjack. Do not apply the onshore80/18/2size distribution to offshore fields. Exact offshore occurrence probability, eligible ocean biome IDs, spacing and roll area are not yet chosen; do not infer50%offshore presence or invent a numerical rarity. Preserve the onshore5/25/100million-mB tiers and badlands-high/desert-medium/savanna-very-low preference. This supersedes the earlier land-only oil proposal, not evidence of installed offshore generation.

## Base chance multiplied by biome — latest user direction

User specifies base spawn probability multiplied by biome suitability, superseding the earlier assistant proposal to normalize biome preferences solely for site selection without changing occurrence probability. Magnetite examples: mountains0.5x, plains1.0x, taiga1.5x. Treat these as user-provided example factors for the proposed model; ordinary forests and hills remain unresolved.

With the existing70%magnetite base, these calculate to35%,70%,105%raw. Clamping probabilities at100%is an assistant proposal, not yet a user-approved guarantee;1.5xtaiga would then guarantee the roll in a suitable taiga site. The continent has multiple biomes, so selecting the candidate biome and limiting rolls must be specified before implementation. Do not silently roll per chunk or per biome repeatedly: that would raise aggregate continent presence and undermine missing-resource goals. No worldgen changes.

## Multiplier clarification — supersedes literal factors above

User clarifies0.5/1/1.5were illustrative, not mandatory. Choose sensible bounded biome-specific chances; examples for magnetite are taiga70%,plains50%,mountains35%. These are provisional tuning examples, not final exact approval. Preserve highest-to-lowest ordering and avoid the earlier accidental guaranteed-taiga interpretation. The former70%continent-wide marginal is no longer safe to report as the actual aggregate occurrence under this developing biome-dependent model. Candidate selection and roll scope still need definition before implementation. No configuration changes.
