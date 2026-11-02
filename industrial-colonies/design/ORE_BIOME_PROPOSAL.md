> October 10 authority: [current combined chart](EARTH_RESOURCE_MASTER_CHART.md), including actual Y levels, guaranteed exposed cinnabar with height fade, graphite/diamond and river-gold exceptions, osmium-group restrictions and gas-giant bulk supply. Conflicting earlier values below are historical; no implementation is implied.

# Ore-to-biome proposal

October10 discussion draft, not implemented or approved. These are gameplay-oriented habitat suggestions, not claims that surface climate determines mineral geology. Human-readable terrain descriptions still need exact registered biome mappings. Preserve existing explicit restrictions, including elevated redstone and the separate gold placer route. Major ores outside their approved eligible set would be excluded once that set is selected; spacing preferences never override eligibility.

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

Keep bulk iron, copper and zinc accessible across several common land biomes. Specialty ores can use narrower geological districts. Test combined biome availability and continent rolls so these choices do not silently multiply rarity into excessive travel. Native placement, depletion and economy validation NOT_RUN.

## User biome-preference clarification

Oil: Badlands highest preference, deserts medium, savannas very low. Magnetite: taiga highest, plains medium, mountains lowest. Ordinary forests tentatively excluded (user said probably not forests); hills remain unresolved. This refers to magnetite, not automatically hematite.

Proposed shared relative placement weights, not approved percentages: high4, medium2, low1, very low0.25, excluded0. Choose among eligible candidate sites using normalized weights after continent presence is decided; do not add an independent chance roll that silently reduces the agreed continent presence. Candidate availability/biome area still affects final outcomes. If no suitable site exists, report the placement failure; do not bypass exclusions. No biome, worldgen or recipe files changed.


Latest user correction: **gold should spawn in colder biomes**. This supersedes the major-deposit badlands/dry-plateau proposal. Draft cold-biome rankings and the combined numbers are in EARTH_RESOURCE_MASTER_CHART.md; no generation changes.

Latest climate revision: gold/silver favour cold mountains; copper/tin favour warmer mountains and savanna highlands, with lower cold-region chances. See EARTH_RESOURCE_MASTER_CHART.md for the current rows; earlier contradictory rankings are historical. Preserve explicit resource exceptions.

Latest cinnabar correction: climate-neutral high mountain peaks; prominent exposed summit-tip and mountain-face deposits, not buried veins. Supersedes the earlier cold-biome shortlist. Exact elevation/coverage/thickness remain unselected. See combined chart.
