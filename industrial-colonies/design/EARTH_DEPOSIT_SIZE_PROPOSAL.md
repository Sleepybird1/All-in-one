> October 10 authority: [current combined chart](EARTH_RESOURCE_MASTER_CHART.md), including actual Y levels, guaranteed exposed cinnabar with height fade, graphite/diamond and river-gold exceptions, osmium-group restrictions and gas-giant bulk supply. Conflicting earlier values below are historical; no implementation is implied.

# Earth deposit size proposal v2 — October 10, 2026

Latest user acceptance: after the oil50%presence,5/25/100million-mB tiers and shared-per-field proposal was spoken, user said they liked it and confirmed per field. Record oil as accepted design, including displayed80/18/2size odds; not installed or native-qualified. Remaining unselected solid-ore size values remain proposals. This supersedes the earlier pending-oil wording below.

Draft displayed to the user; NOT_APPROVED as a whole, NOT_IMPLEMENTED. Only magnetite70%/hematite40%, rare Earth cap100000, and hematite small~2000/large~50000 come from explicit user selection. Other numbers below are assistant proposals pending review. This extends CONTINENT_RARITY_PROPOSAL.md.

Presence is per sufficiently large geologically suitable continent, not per chunk. Size odds are conditional on presence. Ore counts include rich/associated portions, not total rock volume or recovered ingots. Targets/caps must survive terrain placement accounting; final size variation remains open. Assumes one major deposit per present non-coal family; small surface clues remain separate. Iron marginals are selected; overlap remains a proposal.

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

Coal layout:80%group of1–6small deposits depending on continent size,18%two medium deposits,2%one large deposit. A separate small minimum alongside larger patterns is still unresolved. These are mutually exclusive layout proposals, not individual independent coal-deposit rolls.

Example overall chances: hematite small36%, medium3.6%, large0.4%(one in250); magnetite large0.7%(about one in143). Those calculations assume the stated suitable-continent denominator and single major occurrence, not all islands. Associated uranium/thorium can broaden access beyond standalone deposit presence. Rich-grade availability remains uncalibrated; hematite40%alone does not prove rich hematite is at least as accessible as gold.

Oil uses fluid reserves, and resin/clay/salts/gems/off-world resources need separate source-specific rules. Do not model alloys as mined ores. All24custom geological families are represented; no claim of complete item/loot/planet inventory. Proposals depend on actual demand and block drops. No economy, native generation or performance acceptance is claimed.

Validation:24unique rows, each size odds sum100%, increasing positive sizes and all caps<=100000 checked. Native/gameplay tests NOT_RUN. Exact roster coverage checked separately against deposit_families.json. No production/recipe changes.


## Revised sizes and oil

User requested substantially more variation by resource and larger coal deposits; small gold1000is acceptable. Revised ore sizes are assistant proposals, not measured demand calibration. Earlier table preserved in EARTH_DEPOSIT_SIZE_PROPOSAL_v1.md. Presence and size odds unchanged. Coal small-layout reserves now8000-48000total for1-6deposits; two medium=70000; large=100000.

User explicitly requests oil reserves in millibuckets. Assistant proposal:50%presence on suitable continents; small5000000mB, medium25000000mB, large100000000mB, conditional size chances80/18/2. Equivalent5000/25000/100000buckets. Shared finite recoverable reserve per field, not per pumpjack or per marker. These figures are not selected by user or installed; current native grouping/reserve initialization must be reconciled before implementation. Preserve existing oil geography restrictions unless separately revised. Oil does not use the100000ore-block cap.

Validation of revision:24unique updated rows and increasing positive capacities<=100000PASS; no native/performance/economy tests.
