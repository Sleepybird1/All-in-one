# Recipe-independent task review — October 9

Initial review at v383: **175/237 (73.8%)**; progression **31/79 (39.2%)**; space **24/24 (100%)**. Subsequent v384 implementation closes the legacy treatment policy: **176/237 (74.3%)**, progression **32/79 (40.5%)**,61remaining. ALL_TASKS.md reflects the current register.

Every task is classified in ALL_TASKS.md and ALL_TASKS.json. Existing acceptance is reused rather than rerun. At the initial review the62open tasks included29explicit deferrals,16recipe/final-load dependencies,six user playthrough tasks,two design choices,one policy block and four release prerequisites. Four other tasks had useful independent partial work, recorded below; the legacy policy task subsequently reached its fixed acceptance. These categories describe the next constraint, not equal amounts of work.

## Missing addon and retired machines

The read-only scan inspected 280 top-level lab mod archives: 45,683 recipe resources, 19,315 loot resources, 4,366 structures, 10,097 tags and 11,298 other data resources, plus 926 script/config files. Five extractor checks passed; archive hashes were unchanged.

For **mm.ae-digital**, the only scanned data reference to a Mekanism Generators item is MegaCells' radioactive chemical-cell recipe requiring `mekanismgenerators:reactor_glass`. A Carry On compatibility configuration also names two generators; that text is not a loader dependency or acquisition route. The scan bounds the known data dependency without installing the addon or inventing a substitute recipe.

For **mm.legacy-factories**, all ten retired sawmill/combiner machines have ordinary block-self-drop tables. These require an existing block; they are not independent acquisition sources. Ten original recipe definitions, two advancements and one mining tag also reference targets. Raw archive recipe presence is not effective recipe availability: prior staged removal evidence belongs to its own captured baseline. The current lab intentionally keeps generated recipes inactive for original-recipe review, so it must not be presented as that staged candidate. No target identifiers were found in successfully decoded structures.

Four structures initially failed Python gzip decoding. Follow-up verified both MineColonies structures' first gzip members with normal CRC validation; each merely has a trailing newline and neither contains the target identifiers. Two Dungeon Now Loading structures still fail CRC validation and remain unreadable coverage gaps. No game-load defect is claimed from this scanner result and no integrity check was bypassed.

Limits: 232 nested archives, Java-generated trades/code, runtime conditions and datapack priority were not audited. These findings do not prove that every possible acquisition route is disabled. No recipes, mods or production files changed.

### Nested archive follow-up

`NESTED_REFERENCES.json` supersedes the nested-archive coverage gap above: all232direct nested entries were followed recursively, yielding286archive occurrences and265unique archive contents. The scan read1,960JSON data resources and six NBT structures, with zero matches, decoder errors or size/depth exclusions. Outer archive hashes matched the prior scan before and after. Java-generated sources and runtime condition/priority evaluation remain outside this static scan; the two unreadable top-level Dungeon Now Loading structures remain gaps.

## Storage upgrade and terrain diagnostics

Storage charged-input run r1 failed because the expected recipe was absent from the active RecipeManager. The lab's `IC_originalRecipeReview_skip` wrapper intentionally suppresses generated registrations. Run r2 then exposed a fixture input-type error. Corrected r3 passes three unchanged historical recipe definitions through native matching/assembly APIs without registering them: charged predecessors are accepted but output cubes contain zero FE. This cannot establish current effective recipe availability, physical powered crafting or final survival access.

The heightmap diagnostic passed fresh400chunk replays with the same1,515,707owned galena blocks and natural node intact; all three heightmap warnings were attributed to Quark/Zeta calls. It does not establish broad clipping acceptance. The original root-only search across83,424JSON entries missed an embedded resource pack. Native tracing subsequently identified `wythers:terrain/local/cave_disk_basalt`; its WWOO builtin definition has inverted absolute bounds -55..-60. The intended replacement bounds are unknown, so no height correction was made. A narrowly scoped ore-to-basalt guard is now staged and compiled: the full registered supplied-terrain test replaced417ore cells while preserving all other observed states and RNG tails. Its natural400chunk regression preserved galena/node state but exercised zero natural substitutions. See the adjacent wwoo-feature-audit report for exact limits. Full deposit lifetime still depends on final recipes and factory demand; storage prices and access still require the user's recipe review.

### Acquisition follow-up coverage

`ACQUISITION_CODE_REFERENCES.json` inspected3,287classes in545archive contents, selected by trade/loot/village/structure/chest/quest/reward class names. No target references or decoder errors were found. This does not exclude indirect/generic dispatch, reflection or unselected classes. `BUILTIN_PACK_REFERENCES.json` separately scanned1,130JSON resources and31NBT structures in seven archives under embedded pack prefixes, with no target matches or errors. Pack activation, runtime priority and the two unreadable Dungeon Now Loading structures remain outside this evidence. These read-only checks neither install the absent addon nor prove universal acquisition removal.

## Additional natural terrain measurements

The completed deposit-terrain-survey measured three entire additional envelopes: phosphate rock529chunks/2,036,076owned blocks, coal484chunks/1,626,128owned blocks and sphalerite289chunks/687,156owned blocks. All1,302chunks matched their provenance ledgers. Geometric positions below the build limit were0%,4.297% and11.622%, respectively. Two trial-chamber bounding boxes intersected selected envelopes; no matching mineshaft node occurred in these samples, so the existing positive galena/node evidence remains separate. Outside-origin structure starts were not comprehensively enumerated.

These measurements do not choose a desired clipping percentage or predict factory lifetime. The three partial investigations now have bounded evidence ready for their remaining recipe/design prerequisites. The full237-row review preserves176accepted tasks and61remaining tasks, including29explicit deferrals; it does not invent more completion credit for audit administration.
