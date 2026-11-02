> October 10 authority: [current combined chart](EARTH_RESOURCE_MASTER_CHART.md), including actual Y levels, guaranteed exposed cinnabar with height fade, graphite/diamond and river-gold exceptions, osmium-group restrictions and gas-giant bulk supply. Conflicting earlier values below are historical; no implementation is implied.

# Revised continent rarity proposal â€” October 10, 2026

Assistant proposal presented for user review; NOT_APPROVED as a whole and NOT_IMPLEMENTED. Based on the24families in `src/main/resources/data/industrial_colonies/geology/deposit_families.json`, with the two iron families coordinated. Percentages describe major-deposit presence on sufficiently large, geologically suitable continents, not ore density or probability per chunk. Continent-size API feasibility remains unverified. See CONTINENT_RESOURCE_DISTRIBUTION.md for user authority and open semantics.

User adjustments informing this revision: zinc/copper more common than iron;95%iron rejected; hematite/rich hematite not rarer than gold; nickel lower; aluminum around70%; cinnabar increased, around85%; lithium somewhat higher than chromium; silver acceptable. User explicitly allows judgment rather than requiring every suggested percentage exactly.

| Family | Proposed percent |
|---|---:|
| Coal |100|
| Sphalerite / zinc |90|
| Chalcopyrite / copper |85|
| Cinnabar / redstone |85|
| Dolomite / magnesium |80|
| Magnetite — user selected |70|
| Hematite — user selected |40|
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

Proposed coordinated iron outcomes: magnetite-only35%, hematite-only5%, both35%, neither25%. They sum100%; union75%, magnetite marginal70%, hematite marginal40%. The user explicitly selected70%magnetite and40%hematite after seeing the previous table; these marginal rates are approved design. This revised overlap allocation and combined75%remain assistant proposals. These are not independent rolls. Rich hematite's actual accessible grade distribution still needs tuning to satisfy the user comparison with gold;40%parent deposits alone does not prove that comparison.

Additional provisional presence suggestions: crude oil50%, fireclay80%, fluorite50%, conditional on appropriate geography. Sulfur, lignite and other non-catalog resources still need separate current-source audits. Salt/brine, clay/sand/gravel/andesite are intended broadly available in suitable terrain; peat lowland-biome-bound; pale-oak resin Pale-Garden-bound and finite. Cobalt, diamonds and PGM outputs are associations/grades, not extra independent rolls. Nuclear associations may make access more common than standalone chances. Placer gold is separate from major deposits. Amethyst, emeralds, lapis and Certus need source-specific review; Nether and planetary resources are not assigned Earth rolls here. Manufactured alloys, fuels and chemicals are excluded from ore-spawn rolls.

Not an exhaustive inventory of every mod item, crop, loot source or off-world material. The complete24custom major deposit families are covered. Size/count/grade, placement budget, coal minimum and tiny-island rules remain open; no automatic removal of existing surface clues. Economy calibration waits for recipes and measured demand. No tests or game changes were performed for this proposal.
