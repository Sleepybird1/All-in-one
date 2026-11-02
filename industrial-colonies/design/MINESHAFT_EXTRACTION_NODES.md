## October24 explicit exception — Veridium/Vibranium formation

Giant underground Veridium formations never contain mineshafts. This is the user-selected exception to the otherwise10%per-vein all-family rule. No biome restriction; formations rare, embedded Vibranium ore rarer still. Exact numeric generation parameters pending.

## October24 selected probability

10% chance per vein, across ALL vein families regardless of material. No minimum spacing; adjacent lucky mines allowed. Chance is not a quota. Native fit/placement and actual resulting frequency require verification; no family restrictions may be silently added. Implementation pending.

## October24 superseding rarity correction

Veins generate first; eligible veins have a chance to contain a mineshaft. Adjacent mineshafts are allowed. The older hard-separation requirements below are historical and superseded. Exact per-vein probability remains undecided. Node-only-in-mine and shared finite depletion requirements remain.

# Mineshaft extraction nodes — September 22 user direction

This is the latest design authority for WORLD-15 and linked ore extraction. It supersedes earlier instructions to keep mineshaft frequency unchanged. It does not mean node machinery, rarity or massive deposits are installed.

## Required relationship

- Ore veins can exist without mineshafts. Do not attach a mine to every vein.
- An extraction node may occur only in a vein that contains a mineshaft.
- Generated mineshafts have an extraction node within their associated vein/workings.
- An expensive Create-based drill can connect to the node and mine the entire node. Exact supported machine, acquisition cost and extraction behavior require implementation design; no new recipe is approved by this note.
- Make mineshafts rarer than the current installed rate. Extraction nodes must be extremely far apart. Choose and test actual spatial separation, not just a low average spawn probability.
- Node-associated deposits must represent thousands of ore blocks and be substantially larger than the thin deposit the user inspected. Thousands is not an upper cap or approval of the existing roughly1,552-block result. Exact normal/large reserves and separation distances remain unselected.

## Preserve the accepted appearance

The user explicitly likes the broken-up vein appearance visible in the mineshaft. Preserve noisy shapes, irregular boundaries, lobes, native-rock gaps and normal/rich ore distinctions. Increase substantial physical mineral depth beyond tunnel walls; do not replace that appearance with a solid rectangular mass or a tunnel-following coating.

The earlier deposit-first rule remains: vein size determines supported mine size; the mineshaft can influence shape. Small and large mines/veins may exist, but eligible node-bearing mines must meet the newly requested reserve and separation criteria. Standalone veins are not implicitly made rarer by the mine/node rarity change. The later SURFACE_ORES_AND_HEMATITE.md direction separately makes Earth hematite extremely rare and very large, limits small surface ore patches to iron/copper/coal, and proposes ordinary magnetite/hematite recovery of about 1/25 mB. Preserve unrelated yields and rich proportions; ordinary-rock recipe migration is deferred for review, not installed.

## Implementation and acceptance still required

1. Integrate bounded massive deposit descriptors and full-chunk discovery before enlarging deposits; preserve old saved geometry.
2. Define deterministic eligibility and spatial exclusion for mine/node pairs while allowing standalone deposits. Test actual nearest-node separation across ore families, negative coordinates, reload and chunk order.
3. Define node identity, reserve ownership and persistence. Establish how manual mining and automated extraction affect the same deposit so they cannot duplicate its stock. Do not infer that the node is an infinite generator.
4. Identify the intended expensive Create drill and prove node interaction, progression cost, power/rotation demand, extraction accounting and exhaustion. Gate exact recipe changes on the user's established visual-review process.
5. Verify every accepted new mine has a reachable node and a substantial noisy ore body, no node appears without its associated mine, and pre-existing saves are not rewritten.

Runtime node existence, rarity changes, drill integration, massive-body placement and new native acceptance: NOT_RUN / NOT_IMPLEMENTED by this documentation update. No production save or mod file changed.

Related evidence: design/MASSIVE_VEINS_AND_MINESHAFT_SCALE.md and workflow/early-survival/massive-vein-study/PLAYER_REPORT_DIAGNOSIS.md (workspace-relative path). The observed corridor fix works for the reported mine; massive-scale acceptance remains open.


Latest hematite clarification: retain random 1–3-block hematite pockets, including surface traces as iron, but massively reduce their frequency. These coexist with extremely rare massive Earth hematite veins. Higher recovery is supported; retain the proposed ordinary-item 25 mB target, with no additional numeric increase inferred. Exact generation rates await selection; gameplay changes NOT_RUN / not installed.
