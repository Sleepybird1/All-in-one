# Industrial Colonies overnight checkpoint

**ACTIVE**. **176/237 complete — 74.3% overall; 61 remaining.**

Current section: **Reachability, ownership, balance and factory costs: 32/79 — 40.5%; 47 remaining.**

176/237(74.3%); progression32/79(40.5%);61remaining. All237tasks reviewed. Independent legacy policy implementation, missing-addon/acquisition coverage, storage snapshot checks, terrain warning attribution, staged WWOO ore guard and1302chunk multi-family measurements are recorded. Remaining fixed acceptance depends on explicit deferrals, final recipes, user playthrough/design choices or release/tool prerequisites.

The [complete task register](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/MASTER_TASK_LIST.md>) is the fixed denominator. The earlier25/25 was a test batch. R19 remains staged only.

**Production preservation:** All1,397 source baseline files remain unchanged. The live baseline check is **FAIL:8 changed files,2 missing disabled mod files** after live mod changes and game runs. The original failure and observed file copies are retained in `execution/overnight-20260912/baseline/live-drift-n7v/`; no files were restored or rebaselined. Capture and merge live changes before future deployment. No production saves were edited by this work. **R18 remains staging only**,25targets/27files; deployment **NOT_RUN**.

**Client crash recovery:** Air War4.66's mixin plugin reflected on Sodium during early class loading, matching three startup failures. After the user disabled Air War, the client logged world entry at20:03:24. The diagnosis and `RELAUNCH_RECEIPT.json` are in `execution/overnight-20260912/crash-investigation-20260913-195455/`. This confirms startup recovery, not long-term stability or a controlled single-variable trial. No mod was installed, upgraded or disabled by the assistant.

**Nickel/Cobalt:** The full route passed in two isolated native runs: N7n (4m13s) and N7o (4m12s). Both supplied one Pentlandite, one rich Nickel ore and one Cobalt ore, then carried their actual outputs through crushing, chemical separation, heated roasting, Firebrick Vat Hydrogen reduction and Foundry molten recovery. No replacement intermediates or forced random outcomes were supplied.

| Actual full route | Nickel | Cobalt | Spent liquor | Slag |
|---|---:|---:|---:|---:|
| N7n | 125 mB | 40 mB | 1,850 mB | 0 |
| N7o, natural Nickel bonus | 150 mB | 40 mB | 2,000 mB | 1 |

N7m exposed an observer bug: four Cobalt concentrates occupied the single-product Depot while the actual optional Nickel remained in the Crusher. The corrected observer collects primary products first and then waits for natural ejection. N7o directly proved this: primary recovery at tick100, actual Nickel recovery at tick101, followed by processing all six Nickel powders. N7n's separate separation trial naturally produced the optional Cobalt precipitate. Chance frequencies were NOT_RUN; none were changed.

Both full runs passed seven200tick negative boundaries: missing Vat heat, missing Vat rotation,99mB Hydrogen Chloride, exhausted mother liquor, missing roasting heat, missing roasting rotation and249mB Hydrogen. Every active Vat timer and Foundry heat step was reconstructed. The actual consumed mother liquor could not be processed twice; unused test Chloride was recovered and reused. Roasting used ordinary Coal in captured Blaze Burners; reduction used exact TFMG Hydrogen and melting used Blazing Blood.

The readers accepted 20,763,089 full-route checks against 1,547,190 native assertions.63 full-route,39 separation and6 observed-Nickel-bonus corruption controls passed. The original full-route control run had61rejections and two mistargeted tests against an unfueled frame. Those original results are retained; the two corrected hot-frame controls were rerun and rejected. Neither native source nor reader changed for that correction. The two runs completed25 and28 native Vat cycles with12,040 and13,440 active timer frames. Process products, the actual mixer blade and unused drainable fuel were recovered. Undrainable Diesel and converted residual burn units were measured and explicitly disposed with test hardware.

All26,437 loaded recipes and five typed registries match the prior catalog.98Java sources and229compiled classes were frozen per run. Both temporary actor caches were restored.1,397 source baseline files are unchanged. The live baseline has eight changed files and two missing disabled mod files; those differences were preserved and were not restored.23 regression commands exited zero, but the aggregate continues to report the live-baseline FAIL and known unrelated coolant/accounting limitations. This is not a whole-pack acceptance or deployment.

Native processing task mm.nickel-cobalt-route is complete. Upstream resource acquisition, connected automatic transport, casting, non-Firebrick rejection, staged client/restart and deployment are NOT_RUN in this route proof and remain separately scoped. Independent agent review is NOT_RUN. All gameplay and recipe values are unchanged; only observers and their readers changed.


**Create: Metalwork2.0.0:** The user's live addition was reviewed from its actual JAR. It registers two non-bucket items and11molten fluid families; twelve extra dust PNGs lack registered items/models. Its51recipe resources include111mB ingot recipes and a111Cu+111Zn→444Brass route that remain unchanged in the two-policy static replay. Conditions and other callbacks were not simulated; staged/native integration is **NOT_RUN**. The compatibility report records ownership/unit conflicts without silently rewriting them. One detached candidate switches only the existing Nickel-concentrate model's texture reference to existing Create crushed Nickel; no new item or Metalwork dependency. Client/JEI **NOT_RUN**; original four-icon acceptance **NOT_MET**.

**Next:** Continue Nickel/Cobalt actual separation, mother-liquor exhaustion, rich single-metal boundaries, roasting and Hydrogen reduction. Preserve R18 and all existing material values. Upstream reagent/fuel acquisition, connected transport, staged client/restart and deployment remain separate unfinished work. Historical checkpoints follow below.

## R13 accepted checkpoint

Fresh N5v passed in95 seconds. All six owner checks,53 observation scopes and preservation checks passed. Independent review verified exactly the two approved Bronze/Hop Graphite removals, all26,438 surviving recipe payloads and all five typed registries/tags. All234 generated Arc recycling routes retain their base and damage-sampled returns when compared by actual input. The same147 compiled classes were used. Full return components are addressed by the pending58-item observer.

The two retired recipes are Mekanism Bronze Infusing and IE Hop Graphite Squeezing. Existing heated Create Mixer Bronze and TFMG Steel/Firebrick Vat Hop Graphite remain unchanged. Both IE Steel routes remain because TFMG Slag does not satisfy their item-Slag downstream requirements. Connected replacement factories and first-feed acquisition are NOT_RUN.

The R13 package retains20 deployment targets and22 files, with the exact existing R10/R12 JAR. Native review96 checks and actual-bundle review28 checks passed. [R13_COMPLETE_CHECKPOINT.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/R13_COMPLETE_CHECKPOINT.json>) binds the actual acceptance. Existing coolant/Foundry/Vat accounting failures and CO2 incompatibility remain findings; observation PASS does not repair them. Deployment remains NOT_RUN.

## N5u and current source work

The stationary wired docking prerequisite passed in 93 seconds and was independently accepted. All 6,373 native checks, 30 owner checks and the separate raw-record reviews passed. Three original connectors joined, separated, rejoined, changed partners and cleaned up through normal updates. All 53 observation scopes and 26,440 R12 recipes were preserved. The earlier N5t failure occurred during test compilation, before Minecraft; its evidence remains unchanged. N5u adds the already-installed ComputerCraft JAR only to the test compilation classpath.

SPACE-12 remains open: actual computer/modem communication, moving connections and restart are **NOT_RUN**. Source feasibility for the real computer/modem test passed; the actual computer-input fixture is being prepared. The accepted evidence is [N5U_INDEPENDENT_CHECKPOINT.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/N5U_INDEPENDENT_CHECKPOINT.json>).

The ownership inventory now maps 129 families and all 51 formerly unmapped rows. It retains unresolved NC special-material choices, exact replacements and space-fluid decisions inside the existing open tasks. The Bronze Infuser and Hop Graphite Squeezer duplicates have independently reviewed existing Mixer/Vat alternatives and are removed in accepted R13 staging. TFMG Slag does not satisfy the current IE item-Slag tag, so the Steel recipes cannot be removed on that assumption.

The expanded Basic Create comparison covers 78 outputs and 97 archive recipes: 92 preserved, one normal sequence-initialization difference, one approved ten-ingot conversion and three legacy overrides (Redstone Link, Item Vault and Cart Assembler). The latest explicit instruction to preserve ordinary Create recipes supplies the restoration authority. A minimal recipe/UI candidate is being prepared; restoration and native downstream checks are NOT_RUN. Resource-supply work is extending the conditional Iron/Copper scenarios into complete component bills, including components consumed internally by other crafts. No ore yield or production target was changed.

## Reviewable changes

R13 contains **20 deployment targets**: nine server scripts, one item tag, nine source/build files and one existing-tool correction. The 22-file review bundle also includes the tested JAR and consolidated diff. Review [PATCHSET-r13.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/PATCHSET-r13.json>), [changes.patch](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/review-bundle-r13/changes.patch>) and the [independent package checkpoint](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/R13_COMPLETE_CHECKPOINT.json>). No deployment is requested or performed by this overnight run.

R12 preserves every accepted R11 change. It corrects Ad Astra Steel block/ingot compression to ten inputs in the established5×2 Mechanical Crafter pattern and retires one exact Etrionic Steel alloy recipe. The Etrionic machine and its separate BLASTING mode remain. Actual N5s passed in88seconds; independent checks verified exactly three changed recipe IDs,26,438 other payloads preserved, all typed registries/tags preserved and52 observation scopes. The original Copper checker failed only its stale26,441-count expectation; its separate R5 correction passed without rerunning Minecraft or rewriting the failed evidence. Full connected survival Steel production and new Mechanical Crafter withdrawal tests are NOT_RUN.

| Change | Result and verification |

|---|---|

| Saved KJSGen recipes and code generator | Restored nine already-approved TFMG vat recipes, repaired three Mekanism enriching recipes and typed inputs for three planetary crushing recipes. Generator tests and native recipe/ingredient checks passed. |

| Ordinary metal accounting | Removed two CBC Bronze forging gain paths; corrected ten ordinary Cast Iron/Nethersteel fluid fields to current units. Specialized cannon shapes were preserved. Twenty-three represented pure-form routes conserve material. |

| Startup resource handling | Synchronized CDP's private resource map after reproducing concurrent lost writes. Candidate retained all 13,312 test resources with exact bytes. The specific historical Glacio omission is not proved to have this cause. |

| Startup tag compatibility | Narrowly corrected two faucet and six Allthemodium weapon-tag contributions while preserving existing valid members and map identity. 58 native and 18 independent checks passed; targeted errors/warnings disappeared. |

| Blast Furnace Output fluid loss | R10 selects the available fluid without consuming it, then uses the original typed extraction over the same4,000+4,000mB tanks. Oversized mixed extraction now returns100mB Iron and retains10mB Slag. Same native fixture:170 assertions/82 owner/157 independent checks pass; all seven controls are unchanged. Independent formed Blast/Mixer regression passes84 checks over8,654 before/after frames plus events. No recipes, costs or other machines changed. |

| Cached docking inventory | R9 verifies current block-entity identities and mutual locked partnership before cached remote access. Disconnected, differently paired and replaced endpoints reject transfer; normal relock, fresh pairing and local retained-buffer extraction continue working. No capacities, contents or recipes changed. |

| Machine ownership | Removed IE Brass/Bronze arc duplication, then eleven further exact arc/plate duplicates with complete existing alternatives. Retained Brass/Lead/Zinc pressing and specialized material routes. |

| Fluorite and Uranium | Existing fluorite crushing accepts both registered gem identities; existing output/time and PRCs retained. Removed four incomplete IE Uranium arc paths with canonical alternatives, and stopped re-encoding five already-inactive Uranium rows. Intentional fuel-tag separation preserved. |

| Generated arc recycling | Excluded only Electro Energetics Iron Wire: three nuggets crafted a wire that recycled to four. Native comparison retained the other 234 generated input routes, allowing only recorded output-stack order permutations. |

| Sawmill phase bug | Repaired 29 exact IE recipes that returned unchanged input plus repeatable byproducts without a blade. Zero repeatable cases remained; all 29 blade-output totals and 43 other sawmill recipes were preserved. |

| Direct woodchip loop | Removed one chance-gain stick crushing recipe. Existing 1:1 Create cutting still accepts ordinary and treated sticks; 39 related recipe payloads retained. Three indirect chip-return loops remain review decisions below. |

| Reachability tooling | Staged a correction to the existing parser for NuclearCraft plural inputs/outputs. 1,491 recipes gain coverage; 24,960 existing parses stay identical; ten regression groups passed. |
| Waxed Copper block accounting | R11 changes only `minecraft:copper_ingot_from_waxed_copper_block` from nine to ten ingots, matching 1,000 mB/block and 100 mB/ingot. Native catalog comparison preserves the other 26,440 recipes; independent source, native and package reviews passed. |

The staged Industrial Colonies JAR remains version **0.5.5**, SHA-256 `d36db49a5666c745077ac2fa7f85b7f88bcc7355b442bcd529fcf78de2abe25c`. Its isolated build passed in 22 seconds. R11 reuses that exact R10 JAR. The Gradle unit-test task had no sources: **NOT_RUN_NO_SOURCE**; actual native tests below were executed separately.

## Latest native tests

**N5n corrected Windmill result:** Native parent PASS in 97 seconds. Windmill passed 1,682 native assertions and 36 owner checks across 541 regular and six phase frames. It delivered 2,387 FE, passed wrong-facing/obstruction/removal controls, and completed all 81 known block destructions and attributed item disposals. Final mask, body and forced-ticket restoration passed. Only the exact owned Stone obstruction receives the native default-Cobblestone classification; all unrelated unknown-drop guards remain. ACT regression passed 675 native/63 owner checks; Copper passed 158/150. All 50 supplemental scopes and 1,397-source/1,017-live preservation checks passed. All 71 source files, 130 compiled package classes, 62 reports and exact invoked readers are frozen. Independent adoption is complete: 497 native-evidence checks plus 31 integration/execution checks passed. Root verified 723 pinned files in capabilities/N5N_INDEPENDENT_CHECKPOINT.json (SHA 5160ead3334e2b9a05e18307e24b876060e70f299fc90c3c72fa523796502a58). Earlier failed worlds and receipts remain unchanged.

**N5m Windmill attempt:** Compilation passed; parent failed in 95 seconds during final guarded cleanup. All 541 regular and six phase observations are available. The Dynamo delivered 2,398 FE through 218 positive packets; wrong-facing delivery remained zero, and obstruction/source-removal tails stayed flat. The exact owned Stone obstruction became air and dropped one ordinary Cobblestone. The original fixture classified that drop as unknown, so it retained the drop and chunk ticket and reported cleanup FAIL. Final mask/body/ticket inventories were NOT_OBSERVED. All 71 sources, 130 classes and 60 reports are frozen; original owner reader preserves FAIL. ACT was NOT_RUN in this attempt because the earlier Windmill cleanup failed. This does not invalidate the separately accepted N5l actuation result. The old world remains untouched; a narrow test-only drop-attribution correction is being reviewed.

**N5l actuation accepted:** Native parent PASS in 161 seconds; 675 native assertions, 63 corrected owner checks, 349 independent checks and 49 independent reader groups accepted. Both cached hull bounds initialized on tick 1 and both rigs had 40 supported cold frames before the pulse. The powered rig rose 4.5865 blocks; the unpowered control drifted 0.0000661 blocks across 121 frames. All 322 frames satisfy original physical limits. Cleanup disposed four hull blocks and 162 platform blocks and restored baseline body, ticket and forced-chunk sets. The original owner FAIL remains preserved: a separately reviewed R4 reader uses the installed distinct point/matrix quaternion paths and restores prior values to binary32 before float interpolation. No native or tolerance change was required. All 70 sources, 126 classes and 61 reports remain frozen; supplemental validation passes 49 required scopes and preserves 26,440 other recipe payloads. See capabilities/N5L_INDEPENDENT_CHECKPOINT.json (SHA 5dd90a06f0b345b63bfa6d56413eaa7facae36450d4050dfe2a9ea3f4a04a11d). This is a bounded supplied-Creative-Motor experiment; survival power, saved-route playback and continuous subtick containment remain unproved.

**N5k runtime attempt:** Compilation PASS; parent FAIL in77seconds. Copper again158native/150readerPASS. The ACT coordinate correction now yields identical logical/native centers and contained physical hull bounds. Its initial cached `ship.boundingBox()` is still allzero, so the unchanged cached-bound guard rejects the first observation. Actual pressure is1.5 atplatformY-44, mass2, gravity(0,-11,0); the later declaredpressure<=1premise would also reject. No pulse or propulsion was executed, and both cold hulls/platforms were retained. Corrected owner reader reconciles failure with17checksPASS while preserving nativeFAIL. Normal cache initialization and a clear altitude satisfying original pressure assumptions are under source review. Preservation1,397source/1,017livePASS.

**N5j runtime attempt:** Compilation PASS; combined test FAIL in78seconds. Copper public-API observation completed158native checks over22selected recipes,4canonical stacks and253cached Arc entries, with zero world ticks and all payload/object/prefix guards preserved. It observes wires1/2, nuggets1/9, all13CDGcutting filters rejected, and one matching Copper-wire Arc child returning4IECopperNuggets. Powered recycling and physical cutting remain NOT_RUN. The original owner reader confused crafting serializer/type IDs on3rows; corrected reader passes150checks against the same raw bytes;41independent checks and root adoption complete.

ACT failed at its initial tick0 observation: the physics reader supplies position/quaternion but leaves a new destination pivot at zero. The observer incorrectly applied that zero-pivot transform to remote plot coordinates. Raw logical/native positions and orientations agree. No motor pulse occurred; movement/thrust/control are NOT_RUN. Cleanup retained both cold hulls and162platform blocks rather than disposing state whose interpreted bounds failed. That disposable world is retained for diagnosis; no retroactive cleanup or gameplay change. The R2 observer/reader correction is in preparation with unchanged movement limits. All1,397source/1,017live baseline files remain preserved.

**N5i runtime attempt:** Compilation PASS; combined native test FAIL in79seconds during Copper recipe-type enumeration because an unrelated loaded recipe has no registry key for its type. Four actual canonical decompositions were captured before failure, but all final preservation guards in that probe were NOT_RUN, so its owner verifier correctly reports FAIL. Actuator was not invoked. All70source files,126compiled package classes and59report files are frozen. Production/source preservation again passes1,397/1,017files. R3 will correct only the test-helper null comparison.

**N5h compile attempt:** FAIL in10seconds before Minecraft started. The Copper receipt helper passed an ItemStack array to an Iterable parameter. Exact70source files and compiler log are frozen; compiled fixture classes and native receipts are absent. A minimal Arrays.asList adapter is under independent review for fresh N5i. Native actuator testing remains **NOT_RUN**; all1,397source and1,017live baseline files still pass preservation.

**N5e Crafter native PASS in 84 seconds:** 2,083 native assertions and 41 owner checks, 201 raw snapshots, four withdrawals and 76 menu clicks. The actual 2×2 and missing-part controls reject the target; the real recipe yields exactly three Crafters. Supplied Brass/Polished Quartz and retained Hammer/Pick remain explicit prerequisites. Both tools wear once; casing recovery waits 12 natural ticks. All 45 supplemental scopes and the exact R11 recipe delta passed, with 50 acceptance files frozen. Independent native review passed **81 raw and 125 checkpoint checks**, reconstructing 383 component ledgers. The root completion checkpoint preserves 87 evidence pins.

| Test | Executed result | Explicit limit |
|---|---|---|
| Disabled re-encasing, N5g | PASS79seconds;352native/52owner checks. Three actual cross-tier useItemOn attempts return ordinary FAIL and retain original fan identities, full serialized state, named live observations and all casing item components/counts.15guarded block removals restore180cells; log contains no component save/load warnings. Independent raw review passed275 checks; root adoption complete. | Actual event dispatch, loaded false policy and cold-state retention only. Positive swaps, powered machines, next ticks and reload NOT_RUN. |
| Fission/Irradiator, N5f | PASS in87seconds;26087 native assertions and81 owner checks across8660 case frames. Normal reactor produced1N-doped Silicon; no-fuel/no-moderator/no-power controls produced none. Both burning cases completed LEN236 fuel to depleted fuel, shut down naturally, recovered materials/FE and cleared840 owned cells. Independent raw review passed284 checks. | Existing Wafer/fuel/parts supplied. Acquisition, reload, client automation and formed Fusion NOT_RUN. |
| First Mixer workshop, N5d | PASS in 86 seconds; 8,397 native assertions, 41 owner checks, independent 222 raw + 8 detail + 104 checkpoint checks. Thirty actual crafting withdrawals and 943 snapshots account for one Wheel, three Large Cogs, two Small Cogs, one Mixer, one Basin and one spare Shaft. Actual Andesite casing application, harvest and natural pickup completed; the 168-cell reservation was cleared. | Conditional supplied raw bill: 9 Iron, 20 Andesite, 17 Planks, one Stripped Log, two Sticks and one String. A separately crafted recovery pick adds three Flint and two Sticks. Infrastructure is separate. Hammer wear 5 and pick wear 1 are retained. These newly crafted machines were not powered in this test; earlier powered Mixer evidence is separate. |
| Placed Blueprint Workbench, N5c | PASS in 87 seconds; 2,412 native assertions, 164 owner checks; independent 211 raw + 74 checkpoint checks. Five actual native master/dummy pairs, real menus and PICKUP withdrawals. Three Steel Plates become one Rod Mold, Blueprint remains, cutter wears once. Four negative cases retain their inputs; cleanup verified. | Blueprint supplied via the existing recipe, not acquired from a complete survival chain. Normal client window packets, restart persistence and player reach were NOT_RUN. |
| Wooden stripping tool, N5b | PASS in 86 seconds; 1,109 native assertions, 84 owner and 135 raw + 7 checkpoint independent checks. Real Part Builder/Tinker Station, eight withdrawals, actual Wooden Hand Axe and three native stripping uses. Components, 281 snapshots and cleanup verified. | Requires two supplied Copper Ingots plus the recorded wood bill. No full first-Copper acquisition or client timing claim. |
| Starter loot, N4z | 74 native, 134 owner and 71 independent checks passed. Fourteen loaded loot tables and nine roots were resolved with exact nested-entry closure. | Weighted tables are conditional sources; actual encounter/RNG/global loot modifiers, fishing and lockbox use were NOT_RUN. |
| Blast output repair, N4y | Native run PASS; 170 focused native assertions, 82 owner and 157 independent checks. An oversized mixed drain extracts 100 mB Iron while retaining 10 mB Slag. Seven other control paths are preserved. | Does not change the original two 4,000 mB tank capacities, recipe yields or unrelated output-disposal policies. |

N5d also passed all **44 supplemental observation scopes**, with 26,441 recipes and zero encoding errors. The R11 one-recipe count change is still exact. Scope PASS does **not** turn the separately observed Foundry/Vat/Fusion accounting failures below into successful behavior.

Frozen latest evidence: [N5d independent checkpoint](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/N5D_INDEPENDENT_CHECKPOINT.json>), [N5c independent checkpoint](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/N5C_INDEPENDENT_CHECKPOINT.json>), [N5b independent checkpoint](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/N5B_INDEPENDENT_CHECKPOINT.json>). Each links actual executed source, log, raw observations, receipt checks and provenance. [Starter survival evidence](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/dependencies/STARTER_SURVIVAL_EVIDENCE.md>) distinguishes tested actions from conditional acquisition.

## Other completed evidence

| Area | Established result and remaining boundary |
|---|---|
| Existing-item sequences and tiers | Placed spouts consumed 20 + 20 mB for the pink sequence, rejected lower tiers and 19 mB, and preserved the existing item intermediate with its sequence progress. Actual fans accepted ordinary White Concrete at all three tiers; only Industrial Iron processed Chromium. A full client production line remains NOT_RUN. |
| Primitive operations and water power | Native crafting, crude-pick harvest, coal-heated Melter, 100/1,000 mB casting, faucet transfer and water-powered Mixer were exercised. Natural Wheel 8 RPM and Mixer 32 RPM were observed, with dry/disconnected/underspeed controls. Conditional supplied machinery and raw-material boundaries remain explicit. |
| Graphite and metals | Real formed IE Arc Furnace produced Titanium/Tungsten with original quantities, FE and electrode wear. A formed bottler consumed 1,000 mB creosote and four Hop Graphite Dust per electrode while retaining its mold. Real crushing, mixing, heated vat and CO2 filling were exercised. Energy/countdown predictions are distinguished from actual machine observations. |
| Chemical/fluid identity | Actual predicates and machine capabilities distinguish TFMG, NC and Mekanism identities; equal names do not imply interchangeable fluids. NC Electrum plate/ingot gates and five exact NC plate alternatives were proved. Flowing TFMG CO2 is rejected by three source-only consumers. Broad aliasing and full powered chemical networks remain NOT_RUN. |
| Physical cargo | A six-block hull carried 17 Cobblestone, named Paper and 1,000 mB Water outward/back through 62 real ticks; chemical/FE storage and a 277-unit AE cell were separately preserved. Dock cached-endpoint defects were repaired and rechecked after disconnect/replacement/relock. Cross-dimension autonomous transport remains unimplemented. |
| Recipe and recovery coverage | NuclearCraft plural recipe inputs/outputs add 1,491 parser-covered recipes without changing 24,960 earlier parses. Separate dynamic IE recycling and CBC managers were inspected. Missing CBC loot and nonserialized conversions are not treated as proof of no route. |
| Material research and textures | All 27 dossier material families were mapped to existing items and machine roles. The 61 dust textures currently use placeholders. An original chromite concept failed the native-size/palette acceptance and was not installed. The existing comparison-sheet browser display check remains NOT_RUN because browser URL policy rejected the local file; no workaround was attempted. New science-inspired uses remain proposals; no duplicate material variants or generic CPU were added. |

## Newly completed source audits

| Audit | Finding | Next executable work |
|---|---|---|
| Saved single-dimension freight route |37source checks identify actual recording, directional segment, saved schedule, pause/resume and docking APIs. Normal recording resolves an online PlayerList recorder every sample. | NOT_READY_FOR_NATIVE: genuine local-player connection and bounded propeller-driven recording/braking must be established first. No permission bypass or fabricated route points. |
| Local-player admission prerequisite | 36 owner and 148 independent source checks passed. Actual memory transport exists, but the standard client protocol handlers need the client distribution; current dedicated-server harness has no proved genuine peer. | SOURCE_BLOCKED_FOR_CURRENT_HARNESS; native admission, recording and logout cleanup NOT_RUN. No mock compatibility, direct PlayerList admission or protocol-task bypass. |
| First Arc power | 126 owner and 196 independent source checks passed. Native Dynamo side/budget behavior, ambient rotor requirements, exact acquisition bills and Arc per-step FE accumulation were checked against installed classes and current recipes. | Generator-to-Arc execution NOT_RUN. Separate placement preflight is in preparation; starter Dynamo ownership exception remains unresolved. |
| Copper Wire recovery | 79 owner and 134 independent checks close a Copper-only recipe/API loop: 5 ingots can return 6, with cutter wear and Arc operating costs. Current native cache sample returns four nuggets per wire. | Physical cutting, powered recycling and return crafting NOT_RUN. Full indirect graph NOT_AUDITED; no fabrication yield, global valuation or blacklist change selected. |
| Copper recycling controls | 90 independent source checks confirm result-prefix valuation precedes ingredient costing and first-seen deduplication does not minimize recipe cost. Source default wires=1/2; fractional recovery uses nine nuggets per ingot. | Live-map/predicate probe in preparation. No global type registration, prefix change, nine-to-ten patch or blacklist selected. |
| Material reference refresh, N5f | All27 original dossier families reconcile:4932unique recipe references,4914unchanged,8semantic changes,1entity-type ordering change and9removed references. All6039typed registry references remain registered.172owner/110independent checks passed. | Original selection only; new recipe classification and full acquisition are not inferred.17common electronics recipes are unchanged;3approved Vat restores are present. |
| First Mechanical Crafter | Existing 1×3 table recipe makes **three Crafters** from Electron Tube, Brass Casing and Crafting Table, with no direct semiconductor or earlier Crafter requirement. Recurring three-Crafter bill: one Brass, one Iron, one Quartz, eight Redstone, four Planks and one Stripped Log; retained Hammer/Sandpaper each wear once. Owner 47 focused + 14 supplementary checks passed; root repinned 55 files and rechecked 97 exact N5d payloads. | N5e native table/casing recovery with supplied Brass and Polished Quartz is fully accepted. Zinc/Brass acquisition and natural polishing timing remain NOT_RUN. |
| Decorative Copper | Actual N5d cache contains 234 generated Arc children; all 24 vanilla cut/stair/slab states return 220/110 mB. Twenty-four full-block stonecutting paths each return **880 from 1,000 mB**. Eight Quark slab reverts preserve that recovery. No increase in the bounded 236-recipe decorative closure. Owner 59 checks passed; root repinned 44 files and recomputed saved recovery bounds. | No price change is justified. Powered decorative recycling and exact SecurityCraft runtime tool mappings remain NOT_RUN. Code-based recovery cannot be excluded using JSON absence. |
| Fission/Irradiator | Source supports a real 3×3×5 reactor with a separate chamber and shell Irradiator. Actual flux drives the retained one-Wafer→one-N-doped-Silicon recipe. Owner 83 static checks passed; root repinned 89 files and three exact N5d recipes. Reactor starts active by default; native SWITCH mode must establish inactivity before fuel. Shutdown retains heat and partial fuel. | N5f native/owner acceptance passed for all four formed cases, complete fuel burn, signal controls, native heat/FE accounting, depleted fuel recovery and cleanup. Independent raw review passed284 checks; supplied inputs and no-reload limits remain. |
| NC silicon and processors | Exact Silicon Gem has no established current recipe seed after Rock Crusher retirement; the legacy Hafnium source also disappeared. P-doped Silicon has no established producer. Separate TFMG/AE/NC silicon identities were preserved. The existing Kugelblitz route can make BSCCO from exact Tough Alloy; its silver-coil/Elite Processor bills are recorded. | Native reactor proof can proceed conditionally. Restoring seeds, choosing nuclear owners or adding new processor uses requires design review. Kugelblitz formation/beam/black-hole operation remains NOT_RUN. |

Detailed source reports: [Crafter](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/dependencies/first-mechanical-crafter-preflight/REPORT.md>), [Copper recovery](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/machine-coverage/decorative-copper-recovery/REPORT.md>), [Fission feasibility](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/dependencies/fission-irradiator-preflight/PREFLIGHT.md>), [BSCCO/chamber](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/machine-coverage/bscco-chamber-followup/REPORT.md>), [semiconductor research](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/machine-coverage/doped-silicon-followup/research-note/REPORT.md>).

## Decisions and limitations preserved

| Blocker | Evidence and required decision |
|---|---|
| First Zinc/Brass and starter seeds | Selected recipe/owner graph loops through first Crafters/Foundry. The raw-Zinc furnace tag is absent, while the differently named raw-material tag is populated. Silently repairing that tag would cross the assigned ore-processing boundary. The bounded external audit found only block self-drops, test templates and an operator schematic among its candidates; no usable survival seed was established. The four-file diagnostic found no target in two completely parsed MineColonies templates; two DNL payloads remain corrupt and their intended contents unknown. Both template families have conditional shared-landmark source routes. One alias coverage gap and arbitrary-code limits remain. Low Heater/Andesite and genuinely log-free first-tool acquisition retain their earlier unresolved boundaries. |
| Semiconductor authority | Accepted green starter uses Boric Acid, while the later handoff forbids Boron/Phosphorus in the first semiconductor chain. Pink is the later high-density recipe. Existing green-only starter transistor and both accepted semiconductor recipes are preserved pending reconciliation. No Copper-semiconductor bootstrap cycle is introduced. |
| Later progression | Ti/W must precede Industrial Iron; current Depot lacks direct Ti/W and six later machines remain sequences. A conditional RR-free Allthemodium path needs a complete gate decision. Quantum Crafter includes Quantum Core. Industrial Star and Black Hole must continue feeding the final Warp Drive; existing transitive paths were not silently redesigned. |
| Blocked outputs | Foundry native tests lost byproduct when only primary metal fit. Vat tests lost one Graphite and 400 mB spent liquor across three cases, and created a 65-item stack in one case. Detached Fusion coolant logic consumed against blocked outputs. Observation tests passed; these **behavior/accounting cases FAILED**. Complete-output backpressure, persisted pending output, deliberate disposal and Fusion cooling policy require explicit decisions. |
| Gas Tank | Existing 3×5 recipe returns two unstackable tanks; strict native output codec rejects it, with seven dependents. Quantity, stack size or multi-output capability must be decided; not silently rewritten. |
| Woodchip balance | Three indirect paths yield at least 162 from 84, 165 from 84, and 21 from 12 before bonuses. Exact recipes/native matches are recorded. Complete replacement yields/feedstocks need review. |
| Nuclear and chemical roles | Four Uranium-clump dead ends, reactor/reprocessing/Polonium ownership, exact NC identities, Cryotheum bootstrap and three absent NC cold-chain fluids remain unresolved. TFMG flowing-CO2 acceptance requires a narrow route decision. No SF6 is registered and UF6 is not substituted. |
| Restoration risks | Restoring ordinary Gold enrichment could enable a conditional 500→720 mB recovery with outside Blackstone. CBC has 224 separate manager recipes, but only 68 represented recovery chains have complete loot; twelve hypothetical restoration gains were found. Pyrium and raw-metal-brick gaps remain scoped findings. No blind restoration. |
| Automated space freight | Cross-dimension route/controller identity, autonomous landing authorization and compatible ports need a designed adapter and one authoritative cargo owner. No teleport substitute or duplicate cargo store is used. |
| Terrain and full playthrough | Current server profile omits seven client rendering archives. ReTerraForged custom preset appearance, player GUI/reach/timing, complete first-resource survival progression and client rendering are **NOT_RUN** in these tests. Prior installed terrain fixes and both C2ME overrides are preserved. |

The user-authorized values remain **100 mB per ingot, 1,000 mB per finished block and 10 mB per nugget**, with the current ore-specific yield catalog. Titanium/Tungsten, Refined Radiance, Quantum Core and final Warp requirements remain authority constraints, including where implementation is still incomplete. New science recipes, material variants, board duplicates and redundant machines are not approved by research alone.

## Continue from here

The Crafter, Fission and disabled re-encasing stages are complete with independent native acceptance. Review the actual motor/propeller source proposal, prepare a bounded native rehearsal if cleared, and retain the genuine-client admission blocker for saved route recording. The four-file NBT and current material-reference source audits are complete. Root serializes Minecraft/Gradle runs; no new runtime starts until the prior evidence is settled. Record design blockers and continue another approved task without silently changing progression.

Resume from [CURRENT_STATE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/CURRENT_STATE.json>), [OVERNIGHT_PROGRESS.md](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/OVERNIGHT_PROGRESS.md>) and [the candidate queue](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/machine-coverage/CANDIDATE_QUEUE.md>). [Output-accounting review](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/machine-coverage/OUTPUT_ACCOUNTING_REVIEW.md>) and [space logistics matrix](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/space/SPACE_LOGISTICS_MATRIX.md>) retain exact pending design boundaries.

**History is preserved:** [the full report through N5d before consolidation](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/report-history/morning-through-n5d-before-consolidation.md>) retains all earlier observations, failures and superseded percentages. Frozen run receipts were not edited. Historical failure fixtures, parser corrections and failed image concepts remain evidence, not accepted gameplay changes.


Latest bounded source evidence: [material reference refresh](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/materials-assets/n5f-current-references/REPORT.md>) and [four original structure files](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/dependencies/first-zinc-external-seed/malformed-nbt-followup/REPORT.md>). These reports preserve the original historical audits and add no gameplay changes.


### Selected recovery and stationary computers; R14 actual serializer finding

111/237 complete (46.8%;126 remaining), fixed denominator. Progression22/79 (27.8%;57 remaining); space10/24 (41.7%;14 remaining). Selected43-object accounting completed and P05 reopened for3named-nugget gains; net completion unchanged. N5y stationary actual computer messaging independently accepted87checks780pins, including positive ping/ACK, closed-channel/undocked negatives and reconnect. Moving/restart and acquisition remainNOT_RUN.

R14 three Basic Create recipes/UI records are staged only. N5z nativePASS105s; first owner acceptanceFAIL preserved because all3actual recipe serializers arekubejs:shaped while the source expectation predictedminecraft:crafting_shaped. Allother3targetfields match. Installed serializer/source and exact revised contract review are underway; no broad serializer waiver or completion credit. Production preservation1397source/1017livePASS.


## Galena lowheat checkpoint — N7b

Overall **121/237 complete (51.1%)**,116 remaining. Native processing **42/68 (61.8%)**,26 remaining. The Lead task remains open.

Three supplied Galena dust became three roasted Galena in ordinary Create Mixers over actual Basic Burners. One unlit and one unpowered control retained their dust for200 ticks, then resumed when normally ignited or connected. Three Coal supplied4,800 burn units;1,480 were consumed and3,320 remaining units were explicitly disposed with empty test hardware. Three Flint-and-Steel items were ignited by native survival interactions, each wore once, and all three worn tools were recovered. Outputs first appeared at ticks273,473,473. No Sulfur happened in these three unforced rolls; no probability/rate claim is made.

The native run passed in2m49s with26,107 assertions;130,097 reader checks and26 deliberate-corruption controls passed. Fourteen broader postcheck commands passed, including all56 retained scoped observations and preservation of1,397 source/1,017 live baseline files. Existing unrelated coolant/Vat/Foundry failures remain open. N7a's compile failure is retained: only the test compiler lacked the already installed Basic Burner API; N7b added that JAR to compileOnly without changing any of the90 Java sources.

**NOT_RUN:** Upstream crushing, downstream Coke reduction and physical Lead melting in this fixture; Sulfur occurrence/rate, survival acquisition, real power generation, connected transport, real client and process restart. No production deployment. Root review complete; independent review NOT_COMPLETED. Next: native Firebrick Vat reduction and downstream material accounting.


## Lead Coke reduction checkpoint — N7d

Overall **121/237 complete (51.1%)**,116 remaining. Native processing **42/68 (61.8%)**,26 remaining. The full Lead route remains open.

Four native single-block Firebrick Vats converted four supplied roasted Galena and four Coke dust into **four crude Lead and one incidental Slag**. Heat, power and missing-Coke controls retained their exact inputs for200 ticks, then completed after normal supply/connection. Every active Vat ran its existing600tick recipe; outputs appeared at667,843,843,854. No recipe changed. Native Firebrick inventory exposes8 item slots and8 fluid stores of4,000mB each.

Four actual mixer blades were installed and recovered through native survival item interactions. Fireboxes received4,000mB Diesel, consumed3,050mB, and produced **30,500mB flowing Carbon Dioxide**, all retrieved through the native exhaust capability. The950mB remaining Diesel was measured and explicitly disposed with the empty test hardware. Each observed burn consumed50mB and produced500mB; observed events were61worldticks apart. Two exhaust withdrawals per rig prevented capacity stalling without assigning any tank or machine state.

The native run passed in3m with29,282 assertions;270,660 result-reader checks,28 deliberate-corruption controls and3844 additional timer comparisons passed. Fifteen regression commands passed; all26,437 recipes and five typed registries are preserved. All1,397 source/1,017 live baseline files are unchanged. Known unrelated coolant/Vat/Foundry failures remain unresolved. N7c's failed compile is retained; N7d changed only how the observer reads TFMG's package-private mixer mode item, using read-only reflection. The reader and every processing/custody control stayed unchanged.

**NOT_RUN:** Connected actual ore crushing→roasting→reduction handoffs and physical molten Lead recovery; survival acquisition, real power generation, client, process restart, production deployment. Root review complete; independent review NOT_COMPLETED. Current loaded recipes still specify20mB per processed ordinary Galena,80mB per rich ore,3mB direct, and20mB for both crude and high-purity Lead. Those computed chain totals are not substitutes for physical evidence.

## N7h Silver thermal prerequisite (counts unchanged)

N7h passed with naturally formed Melters and actual native fuel tanks. Coal (800°C) and Lava (1,000°C) each left one Silver powder unchanged for560 observed ticks. Both powder items, the unused Coal and all1,000mB cold Lava were physically recovered.

Existing Blazing Blood (1,500°C) produced10mB Silver from one powder. It consumed50mB fuel, generated150 burn units, consumed140 units and left10 measured units disposed with the test hardware. All950mB unused fluid was drained once. Lava produced2mB Silver from Argentite, consumed50mB/100 burn units, and returned950mB unused fuel.

The native run passed in3m52s with22,886 assertions. The revised result reader passed64,597 checks, including1,118 exact native heat-step comparisons. All31 deliberate-corruption controls and19 regression commands passed. All26,437 recipes, five typed registries and the1,397source/1,017live baseline files were preserved. The original reader incorrectly capped progress at800: rate15 naturally reaches810 before the next heating call completes the recipe. Its failure and exact bytes remain preserved; the corrected reader reconstructs actual heating from fuel consumption. No native results were edited and no rerun was needed for that reader correction.

This is a prerequisite within mm.silver-route, not a completed master task. Overall remains123/237(51.9%); native processing44/68(64.7%). Full ore-to-Silver handoffs, upstream reagent/fuel acquisition, connected logistics, casting, client, process restart and deployment are NOT_RUN. Existing R18 staging is unchanged.


# Basic Iron Foundry acceptance

N7p passed in the isolated native runtime (3m59s). Ordinary Lava melted actual supplied Hematite and Magnetite to 3 mB each and raw Iron to 25 mB. The unfueled Hematite control retained its one ore for 560 observed frames. Each positive case consumed 50 mB Lava and recovered 950 mB unused Lava, with no residual burn units at teardown.

The independent reader passed 65,702 checks, including 1,677 reconstructed heat steps, against 22,554 native assertions. All 18 receipt-corruption controls were rejected. The exact 99 Java sources, 232 compiled classes and 93 reports were frozen after process exit; the temporary actor cache was restored to absence.

All 24 postcheck commands exited zero. This is a scoped acceptance: the aggregate retains the live baseline failure (eight changed files, two missing disabled mod files) and the separate known coolant-accounting issue. All 1,397 source baseline files remain unchanged. Live differences were copied read-only for evidence, with no restoration or rebaselining.

The full Iron route remains open. Actual crushing into TFMG, upstream acquisition, connected transport, casting, client/restart and deployment are NOT_RUN in this proof. No recipe, gameplay, mod or production-save changes were made.


# Iron native processing acceptance

N7q passed in the isolated runtime (7m23s). This closes mm.iron-route with current ordinary and rich Iron values.

| Actual feed | Basic Foundry | Owned industrial route |
|---|---:|---|
| One Hematite | 3 mB Iron | Actual Crusher dust → TFMG → 8 mB Iron + 10 mB Slag |
| One Magnetite | 3 mB Iron | Actual Crusher dust → TFMG → 8 mB Iron + 10 mB Slag |
| One raw Iron | 25 mB Iron | Native TFMG → 100 mB Iron + 10 mB Slag |

Both actual Crusher outputs were recovered from their Depots and those same ItemStack objects were split once into the original TFMG feeding hatches. Native falling-item intake delivered the dust and Coke to complete ordinary three-layer furnaces. Each 510-decrement native cycle consumed 10,200 mB Hot Air and recovered 8 mB Iron plus 10 mB Slag. Both retained internal Coke reserves were recorded and disposed with test hardware, without invented refunds. This proof supplied test fuel, power and Hot Air; it does not claim their acquisition or connected transport.

The independent chain reader passed 66,883 checks across 81 Crusher frames and 1,442 furnace frames. All30corruption controls passed. Its original version rejected four frames where a consumed ItemEntity briefly remained empty. The preserved TFMG code shrinks the item after transferring it into fuel/input. R2 requires the same previously observed entity, exact matching inventory gain, normal age progression and absence on the next tick. Both original FAIL reports remain preserved; the native run and its sources were not changed or rerun for this correction.

The direct Foundry reader also passed, with its prior18corruption controls retained. The current raw-Iron furnace rerun passed its positive and no-fuel/19mB-Hot-Air/missing-support controls and exact typed cleanup.101Java sources,238compiled classes and134reports were frozen after process exit; the actor cache was restored. All26,437recipes and five typed registries match the prior catalog. All1,397source baseline files remain unchanged. The eight changed live files and two missing disabled mods were preserved, not restored.

This is scoped route acceptance. Fuel/reagent acquisition, connected Crusher-to-Hatch transport, casting, staged client/restart and deployment are NOT_RUN here and remain separately tracked. The unrelated coolant/accounting issue and live baseline failure are still open. No gameplay, recipe, mod or production-save changes were made.

Iron ordinary/rich route accepted.126/237 complete (53.2%);111 remaining. Native47/68 (69.1%);21 remaining. Next: Tungsten superheat feasibility and actual upstream chain using existing items/recipes.


## Tungsten superheat boundary — N7u accepted

Overall126/237 (53.2%); native processing47/68 (69.1%). Counts unchanged: mm.tungsten-route still needs its actual upstream material chain.

N7u PASSED in2m17s:102 compiled Java sources,241 package classes,4 reports frozen. Naturally formed2x2 Firebrick Vat/Firebox reached heat8 and completed the unchanged Tungsten recipe in600 native increments; a singleton reached heat2 and retained its oxide/500mB Hydrogen. Recovered one powder, one retained oxide,500mB Hydrogen, both mixing blades and42,500mB flowing CO2. Supplied5,200mB Diesel;4,250 consumed and950 undrainable remainder explicitly disposed with owned test hardware.150 dry cells cleared and original chunk tickets restored. No recipe, machine, gameplay or live-instance edits.

Independent reader PASSED134,547 checks and all23 corruption controls.26,437 loaded recipes and five typed registries preserved. Source baseline1,397 PASS; known live8changed/2missing FAIL remains open and untouched. Cache restoration PASS. Exact receipts: execution/overnight-20260912/capabilities/TUNGSTEN_SUPERHEAT_N7U_ROOT_ACCEPTANCE.json and machine-coverage/tungsten-superheat-native-r4/NATIVE_ACCEPTANCE_N7U.json.

Earlier failures remain frozen: N7r confused numeric heat_level0 with the SUPERHEATED enum; N7s assumed fresh exhaust capacity scaled; N7t produced powder but had insufficient test fuel for its final hot dwell. Installed TFMG applyFluidTankSize resizes fuel only; fresh2x2 fuel32,000/exhaust8,000 differs from NBT read resizing both. This capacity inconsistency is documented, NOT patched. N7t postcheck remains FAIL. N7u reader separately corrected the native cold sentinel-1/positive-only heat sum and extracted stack observations without slot metadata.

Full ore→leach→precipitate→oxide→powder custody, connected automation, acquisition, client/restart and deployment: NOT_RUN here. Earlier Tungsten Arc proof uses a formed machine with accelerated direct native ticks and supplied FE; it is not a continuously powered connected chain. Next: actual ordinary/rich ore custody through the existing upstream recipes; no new grades or recipes.


# Tungsten processing acceptance

N7v passed the actual upstream route in the isolated runtime. One ordinary Wolframite rock plus one rich ore produced five dust, then five Tungsten powders through the unchanged recipes. Actual extracted ItemStack/FluidStack objects moved between machines; no processing intermediates were supplied.

| Stage | Actual input | Actual recovered output |
|---|---|---|
| Create crushing | 1 rock + 1 rich ore | 5 Wolframite dust |
| Firebrick Vat alkaline leach | 5 actual dust + 5 Sodium Hydroxide +1,250 mB Water | 1,250 mB Tungstate solution +5 Slag |
| Vat precipitation | Actual solution +750 mB Hydrogen Chloride | 5 precipitates +625 mB spent liquor |
| Heated Create Mixer | 5 actual precipitates | 5 Tungsten oxide |
| Superheated Firebrick Vat | 5 actual oxide +2,500 mB Hydrogen | 5 Tungsten powders |

All fifteen Vat cycles completed with7,000 active native timer increments. Six200tick controls blocked missing Vat heat, Vat rotation, sufficient Chloride, roaster heat, roaster rotation and sufficient Hydrogen.9,317 consecutive observations preserved five Tungsten units across items/fluids and reconciled each recovered intermediate. All25corruption controls passed. Native assertions270,563; independent repeated ledger/observation checks4,382,137.103Java sources,246compiled classes and4reports frozen after process exit. Native run2m7s;9,360world ticks. This focused run did not rerun unrelated native scopes.

All five powders, five Slag,625mB spent liquor,298,000mB flowing CO2 and the mixing blade were recovered.40,000mB supplied Diesel comprised29,800consumed and10,200undrainable remainder explicitly disposed with owned hardware. One Coal supplied1,600burn units, all consumed.530dry cells cleared, original chunk tickets restored, actor cache restored.26,437recipes/five typed registries preserved; source1,397PASS. Known live8changed/2missingFAIL remains untouched, with a fresh read-only drift snapshot.

The separate N7q final Arc proof is reused as the task explicitly permits: five supplied powders became one ingot in a real formed77block Arc Furnace,800 accelerated native logic calls,409,600FE, three electrodes and no-FE/no-electrode controls. Its recipe and source still match. It does not prove these same five upstream powders were transported into the Arc, natural Arc throughput or connected power. Those limits remain explicit.

Fuel/reagent acquisition, connected transport, staged client/restart and deployment are NOT_RUN here. Existing unrelated coolant/accounting and baseline issues remain open. No gameplay recipe, machine, mod, live configuration or production save was changed.

Tungsten route accepted:127/237 complete (53.6%),110 remaining. Native48/68 (70.6%),20 remaining. Next: actual Titanium chlorination/reduction and returned Magnesium Chloride custody.


# Titanium repeated-output loss — N7w

Actual native run FAILED at tick1,472 in the second acid impurity-removal cycle. Before:4Ilmenite dust,1Titanium concentrate,1Slag,1,000mB acid,timer480. After:3dust,2concentrate,1Slag,750mB acid,timer0. The existing recipe requires a second Slag. Two output slots were empty, existing stacks far below64, native heat8 and mixer-128RPM. This is not output pressure or a changed yield. The source observer immediately stopped; later processing/recovery/cleanup stages were NOT_RUN and test hardware remains only in the disposable world.

Installed TFMG handleRecipe merges its rolled first output, then bytecode369 jumps429 past the entire item-output loop. Empty-slot insertion uses426→240 and continues. On batch2 the existing concentrate stack is merged and the guaranteed Slag is skipped. The diagnostic independently checks exact before/after materials, consumed acid, full timer and available output slots; four corruption controls reject false evidence. It does not claim save/reload or later recovery was tested.

This expands the existing mm.vat-output-policy defect evidence. No output algorithm, pending buffer, recipe, capacity, probability, quantity or mod was patched. The repeated-batch Titanium route stays BLOCKED; do not relabel a per-batch extraction workaround as a fix. Continue other useful processing tests while that existing design decision remains open.

Compile passed104Java sources/250classes; native build failed2m8s. All4reports and exact classes/sources/log frozen. Full route reader FAIL (incomplete successful-custody evidence); its25corruption controls NOT_RUN. The separate four-case loss-diagnosis controls PASSED. All26,437recipes/five typed registries preserved. Source1,397PASS; known live8changed/2missingFAIL untouched. Actor cache restorationPASS. No production changes.

127/237 complete (53.6%),110 remaining. Native48/68 (70.6%);19 unverified and1 blocked. Titanium now linked to existing Vat output-policy decision. Next: independent Magnesium calcining/electrolysis and return-path tests.


## Magnesium calcining boundary — N7y accepted

Overall127/237 (53.6%); native48/68 (70.6%). Counts unchanged: Magnesium chemical/electrical and reagent-return stages remain NOT_RUN.

Actual two Dolomite were crushed into two dust and physically transferred through the machine capabilities to a superheated Create mixer. Ordinary Coal heat and special heat without rotation each retained both dust for200 consecutive ticks. One actual Coal and one Blaze Cake were consumed. At128RPM the unchanged processing_time1000 recipe uses Create's native301-tick processing counter, twice:602 observed processing frames. One calcined item appeared at823 and another at1125; both actual items were recovered at1144, hardware removed at1164 and cleanup confirmed at1168. These are natural server ticks, with supplied native creative motors. Neither processing fields nor outcomes were forced.

Fuel accounting:1600normal burn units supplied,260consumed,1340displaced by the Cake;3200special units supplied,864consumed,2336residual units disposed with owned hardware. Create's installed data map assigns Blaze Cake3200; native fuel replacement was measured.259dry cells cleared, prior chunk tickets and isolated actor cache restored. Full chemistry, real motor/fuel acquisition, continuous transport, client/restart and deployment NOT_RUN.

N7y compiled105Java sources/254classes and PASSED in1m18s. Independent reader270,555checks and22corruption controls PASS. Separate native-duration reconstruction and four corrupt-timing cases PASS. All26,437recipes/five typed registries preserved. Source1,397PASS; known live8changed/2missingFAIL remains untouched. EarlierN7x setup failure remains frozen: a placement callback formed the Crusher controller after initial discovery; r2 records that native identity before its first guard. No gameplay changes were made.

Evidence: execution/overnight-20260912/capabilities/MAGNESIUM_CALCINE_N7Y_ROOT_ACCEPTANCE.json and machine-coverage/magnesium-calcine-native-r2/.


## Magnesium chemical/electrical continuation — N7z preserved, N8a running

Overall127/237 (53.6%), native48/68 (70.6%); whole Magnesium task remains unverified. N7z reran actual upstream calcining successfully and completed two acid-separation and two chloride-purification cycles. It stopped at tick2259, before electrolysis: the test assumed40ticks was enough for heat to propagate. The Fireboxes first reported heat2each at2258; the Vat still reported0at2259. Generator removal correctly left both electrodes at0V/0current/cannotOperate. N7z's failed process/classes/4reports and incomplete full-reader result are frozen;24reader corruption controls NOT_RUN. Source1,397PASS and26,437recipes/five registries preserved; live8changed/2missingFAIL unchanged; cache restored.

R2 now waits at least40and at most100ticks for measured Vat heat>=2 before starting the unchanged full200tick power-loss hold. The independent reader also corrects a separate assumption: the native Creative Generator supplies500V by default;20,000V is an electrode limit, not the test's supply. No gameplay state or recipe was patched. N8a is running in isolation; do not mark it accepted before native exit, freezing and independent postchecks. The planned reagent-return segment explicitly supplies250mB purified Titanium Chloride, then uses actual Magnesium and actual returned chloride; it does not bypass or close the separately blocked whole Titanium route.


# Magnesium processing acceptance

N8a passed actual same-run Dolomite processing and returned-chloride recovery in isolation. No Magnesium processing intermediates were supplied.

| Stage | Actual feed plus supplied reagents | Recovered output |
|---|---|---|
| Create crushing/calcining | 2Dolomite, one Coal, one Blaze Cake | 2actual calcined Dolomite |
| Vat acid separation | Actual calcined feed +500mB Hydrogen Chloride | 500mB Magnesium-bearing solution +1naturally rolled Slag |
| Vat purification | Actual solution +2Sodium Hydroxide | 500mB Magnesium Chloride +250mB spent liquor |
| Heated two-electrode Firebrick Vat | Actual500mB chloride, native electricity | 2Magnesium powders +500mB Chlorine |
| Superheated Titanium reagent-return step | Both actual powders +explicitly supplied250mB purified Titanium Chloride | 1Titanium sponge +500mB returned Magnesium Chloride |
| Heated two-electrode Firebrick Vat | Actual returned500mB chloride | 2Magnesium powders +500mB additional Chlorine |

Four200tick chemical controls blocked insufficient acid, powered electrolysis without heat, heated electrolysis without electricity, and Titanium reduction without superheat. Same-run upstream also repeated both200tick calcining controls. Vat processing completed9cycles/6,360actual timer increments. All actual item/fluid handoffs and the return loop were reconstructed independently. Final custody:2Magnesium powders,1Titanium sponge,1Slag,250mB spent liquor and1,000mB Chlorine. No probability was forced; chance frequency NOT_RUN.

The native generators supplied500V. Each electrode drew50A and reported25,000power usage when powered. The observed cumulative power-usage-tick sum was351,800,000across processing and idle observation; it is not labelled FE. Supplied40,000mB Diesel:25,600consumed,14,400undrainable remainder explicitly disposed with owned hardware;256,000mB flowing CO2 recovered. Upstream Coal/Cake accounting is retained in the report. Mixing blade and both unchanged electrodes recovered;192chemical hardware cells and259upstream cells cleared. Original tickets/electrical network members and actor cache restored.

Native build PASSED1m19s,106Java sources/257classes/4reports frozen after process exit. Upstream1,168ticks plus chemical7,328ticks; chemical189,056native assertions and1,267,180independent checks. All24corruption controls PASS. The calcining verifier independently checked its embedded same-run evidence. All26,437recipes/five typed registries preserved; source1,397PASS. Known live8changed/2missingFAIL remains untouched. R18 remains staging only.

N7z remains a failed preserved run: the test's fixed40tick warmup ended when Firebox heat first appeared, before Vat heat caught up. N8a measured the transition at49ticks, then held the full200tick power-loss control. The reader's separate source-voltage assumption was corrected from the electrode limit20,000V to the native generator's actual500V default. No machine/recipe state was patched.

This closes the task's separation/electrolysis/returned-chloride acceptance. It does not close the independently blocked whole Titanium route: its purified chloride here was an explicit supplied substrate. Final Magnesium melting, real energy generation and acquisition, continuous automated transport, client/restart and deployment are NOT_RUN here. No gameplay or production-save changes.

Magnesium separation/electrolysis and returned-chloride custody accepted:128/237 complete (54.0%),109 remaining. Native49/68 (72.1%),19 remaining. Next: actual Bauxite digestion/red-mud separation and powered Aluminum reduction.


# Aluminum processing acceptance

N8b passed the current Bauxite route with actual native item/fluid handoffs, without supplying processing intermediates.

| Stage | Actual feed plus supplied reagents | Output |
|---|---|---|
| Create crushing | 1 ordinary and 1 rich Bauxite | 5 Bauxite powders |
| Heated caustic digestion | Actual powders, 5 Sodium Hydroxide, 1,250 mB Water | 1,250 mB Alumina-rich slurry |
| Red-mud separation | Actual slurry | 1,250 mB clarified aluminate, 5 Slag |
| Precipitation | Actual aluminate, 500 mB source TFMG CO2 | 5 Alumina, 625 mB spent liquor |
| Heated two-electrode Firebrick Vat | Actual Alumina, 5 Graphite, native electricity | 5 Aluminum granules, 500 mB source CO2 |
| Modern Foundry | All 5 actual granules, native Blazing Blood fuel | 125 mB molten Aluminum |

Four 200-tick controls blocked digestion without heat, precipitation with only 99 mB source CO2, powered reduction without heat, and heated reduction without electricity. The 20 Vat cycles required 11,000 observed timer increments. Both native electrodes received 500 V; observed power-usage-tick sum 611,250,000 is recorded without labelling it FE. Foundry processed all five actual granules through its three single-item slots at the existing 25 mB yield.

Final recovery: 125 mB molten Aluminum, 5 Slag, 625 mB spent liquor and 500 mB source CO2. Diesel supplied 72,000 mB, consumed 59,000 mB, remaining 13,000 mB explicitly disposed because native Firebox input cannot be drained. All 590,000 mB flowing fuel exhaust was recovered separately. Foundry consumed 50 mB Blazing Blood; 950 mB unused fluid recovered, 115 burn units consumed and 35 residual burn units disposed. Blade/electrodes recovered, all 578 reserved hardware cells cleared, prior chunk tickets/electrical members/actor cache restored.

Native build PASS in 1m23s; 107 Java sources, 262 classes and four reports frozen after process exit. 12,520 observed ticks, 528,143 native assertions, 6,691,733 independent checks and all 28 corrupted-evidence controls PASS. All 26,437 recipes and five typed registries preserved; source baseline 1,397 files PASS. Known live 8 changed/2 missing FAIL remains untouched.

This closes the fixed Aluminum processing task. Source/flowing CO2 compatibility is still a separate blocked policy decision. Fuel/reagent/machine acquisition, actual survival power generation, connected automation, client/restart and deployment are NOT_RUN here. R18 remains staging only; no gameplay or production-save changes.

Aluminum route accepted: 129/237 complete (54.4%), 108 remaining. Native 50/68 (73.5%), 18 remaining. Next: Bertrandite large powered-vat Beryllium recovery.


# Beryllium processing acceptance

Frozen N8c passed the actual Bertrandite-to-molten-Beryllium route. No processing intermediates were supplied.

| Stage | Actual feed plus supplied reagents | Output |
|---|---|---|
| Create crushing | 2 Bertrandite | 2 Bertrandite dust |
| Heated Steel Vat leach | Actual dust, 600 mB TFMG Sulfuric Acid | 500 mB Beryllium-bearing solution |
| Precipitation | Actual solution, 2 Sodium Hydroxide | 2 precipitate, 500 mB spent liquor |
| Superheated Create Mixer | Both actual precipitates, native Blaze Cake | 2 Beryllium oxides |
| Size/material controls | Both actual oxides and 500 mB Mekanism Hydrogen Chloride | Same materials recovered from rejected 2x2 Firebrick and 3x3 Steel Vats |
| Superheated powered 3x3 Firebrick Vat | Both actual oxides and actual recovered Hydrogen Chloride | 2 Beryllium powders |
| Modern Foundry | Both actual powders, native Blazing Blood | 20 mB molten Beryllium |

Seven 200-tick controls passed: cold leaching, ordinary-heat calcining, special-fueled calcining without rotation, hot/powered undersized Firebrick, hot/powered large Steel, powered/cold large Firebrick, and superheated/unpowered large Firebrick. The valid Vat was naturally formed with size9 and two native electrodes. Six Vat cycles used 3,600 observed timer increments; two Create cycles each counted301 through1 before native completion.

Final custody: 20 mB molten Beryllium and 500 mB spent liquor. Four native Fireboxes consumed69,650 of112,000 mB supplied Diesel;42,350 mB undrainable remainder explicitly disposed and696,500 mB flowing CO2 exhaust recovered. Coal provided1,600 burn units:200 consumed,1,400 displaced by Cake. Cake provided3,200:844 consumed,2,356 disposed when the empty roaster was removed. Foundry consumed50 mB Blood:950 mB unused fuel recovered,60 burn units consumed,90 residual disposed. All six electrodes and the mixing blade recovered;787 reserved dry cells cleared; original tickets/network members/actor cache restored. Observed electrical usage is retained per rig without equating it to FE.

Native build PASS in1m22s;108 Java sources,268 classes and four reports frozen after process exit.6,140 observed ticks and353,758 native assertions. Independent reader r2 passed3,532,346 checks and all26 corrupted-evidence controls. All26,437 recipes/five typed registries preserved; source1,397 files PASS. Known live8changed/2missing FAIL remains untouched.

The original verifier failed exactly twice because it expected completed Create counter0. Installed bytecode writes-1 immediately before applying the Basin recipe; both recorded output frames correctly show1 to-1. The r2 reader changes only that sentinel assertion. Original failed reader/result, native source/classes/log and raw reports remain unchanged. Native rerun NOT_RUN because this was a reader-only correction.

This closes the fixed Beryllium processing task. Reagent/fuel/machine acquisition, survival power generation, continuous transport automation, client/restart and deployment are NOT_RUN. No gameplay or production-save changes; R18 remains staging only.

Beryllium accepted:130/237 complete (54.9%),107 remaining. Native51/68 (75.0%),17 remaining. Next: Borax purification, Boron reduction and consolidation.


# Boron chemistry checkpoint — full task remains open

Overall130/237 (54.9%); native51/68 (75.0%). This checkpoint does not close mm.boron-route.

N8f compiled and passed in1m51s.109Java sources,272classes and four reports frozen.38,191 observed ticks;1,199,160 native assertions;12,227,749 independent checks; all24 corrupted-evidence controls passed. The exact26,437 recipes and five typed registries were preserved. Source1,397 files PASS; known live8changed/2missing FAIL remains untouched. Actor cache restored.

Actual20Borax rocks produced20dust. Dissolution used5000mB Water and produced5000mB purified Borate solution plus4naturally rolled Slag. Actual solution plus3000mB TFMG Sulfuric Acid produced5000mB NuclearCraft Boric Acid; heated Firebrick dehydration produced20Boron oxide. Actual oxide plus20explicitly supplied Magnesium dust and2000mB Mekanism Hydrogen Chloride produced20Boron powder and5000mB Magnesium Chloride in a naturally formed3x3superheated Firebrick Vat. All80native cycles completed:9600+6400+8000+12000=36000active timer increments. Seven200tick negative holds covered missing Water/Acid, wrong Steel, missing heat, undersized Vat, large cold Vat and stopped rotation.

All process outputs and three mixing blades recovered;517dry reserved cells cleared and original tickets restored. Fireboxes received240000mB Diesel, consumed229500mB, and produced2295000mB flowingCO2, all recovered.10500mB undrainable Diesel was measured and disposed with test hardware. Those are supplied test fuels and explicit machine idle costs, not a minimum optimized factory budget.

N8d failed before material admission because a3x3Mixer was placed at the corner; installed TOP_CENTER requires its center. N8e then preserved all material but stopped after16dissolution cycles:4000mB output reached the selector's fixed ceiling even though the formed tank reports32000mB. N8f uses ordinary typed4000mB output withdrawals, retains those actual fluids in custody, and combines each with the final1000mB. That is manual output handling; the underlying capacity mismatch and existing atomic-output policy remain unresolved. All failed revisions and results remain preserved.

N8g's combined chemistry/Arc attempt compiled but exhausted Java heap while Gson built one giant result String. Only its before-snapshot was written; Arc success cannot be claimed from the callback stack. N8g source/classes/log/crash report are preserved. N8h changes only the four focused-report writes to stream through UTF8 CREATE_NEW writers. N8h native run is IN_PROGRESS; its result, final preservation and Arc corruption checks remain NOT_RUN until completion.

Arc feed must be the same actual20powder stack; native Windmill/Dynamo must pay409600FE across800active intervals for3Boron ingots. Acquisition, connected automatic material transport, client/restart and deployment NOT_RUN. Production saves/mods unchanged. Lithium recipe preflight and an uncompiled activation candidate are prepared as the next route.


# Complete Boron route acceptance

N8h passed the same-run chain from20actual Borax rocks through purification, Boric Acid, oxide and Magnesium reduction to20actual Boron powders. That exact component-identical stack was inserted into a naturally formed77-block IE Arc Furnace and produced3existing Boron ingots. No powder was supplied at the Arc endpoint.

The adjacent native unsailed Windmill/Dynamo generated409618FE. The800active Arc ticks consumed409600FE;18FE residual was recorded and disposed during empty-hardware teardown. Wrong-facing generation, missing third electrode, physical rotor obstruction, power starvation and resumption controls passed. All three original graphite electrodes were recovered with728wear each;72work ticks ended with zero stored FE and correctly skipped native electrode wear. The stopped source left the finished output stable for40ticks.

The upstream same-run reader reconfirmed80chemical cycles/36000active increments, seven200tick gates,5000mB returned Magnesium Chloride and4naturally rolled Slag. The separate N8f chemistry corruption suite passed24cases; the combined N8h suite passed19cases, including upstream-ore, handoff and returned-fluid corruption. No probabilities were forced. All actual fluid output withdrawn at the native4000mB selection ceiling remained in custody and was reused; the underlying capacity mismatch remains documented.

Native build PASS in2m50s;110Java sources,276classes and four reports frozen after exit. Arc observations span38098ticks and154003native assertions; upstream adds1199160assertions. Independent verification passed13561558checks. Both chemistry and Arc hardware reservations were cleared, original tickets and actor cache restored, final product/electrodes/fluids recovered. All26437recipes/five typed registries preserved; source1397files PASS. Known live8changed/2missing FAIL remains untouched.

N8g's report-writer heap failure is retained. N8h streams the same focused JSON values directly to CREATE_NEW UTF8 writers; the full1.29GB native sidecar was saved and independently parsed. Native fixture, machine settings and recipes were unchanged by that harness repair.

This closes mm.boron-route. Same-run existing Borax-to-Boron-ingot route accepted. Native Windmill/Dynamo powers final Arc; chemical mixers still use declared creative motors, and hardware/electrodes/fuels/reagents are supplied. Three native4000mB fluid withdrawals explicitly model manual output handling; no capacity/atomic-output policy repair claimed. Acquisition, connected automatic transport, client/restart and deployment NOT_RUN. Existing output/accounting/live drift issues remain.

Boron accepted:131/237 complete (55.3%),106 remaining. Native52/68 (76.5%),16 remaining. Next: Lithium activation and electrochemical/Foundry recovery.


# Lithium activation checkpoint — N8j

One actual ordinary Spodumene rock and one actual rich ore yielded five dusts in the native Crusher. The same dusts produced five activated items in the native Coal-heated Mixer. Cold and heated/unpowered controls each held for 200 ticks. Five native 241-to-1 processing sequences completed with the installed -1 sentinel; 1,470 of 1,600 Coal burn units were consumed and 130 explicitly disposed at teardown.

Native PASS (1m15s): 111 Java sources, 280 classes, four frozen reports; 1,834 observed ticks, 38,045 native assertions. Independent reader PASS: 438,076 checks and all 25 corruption controls. All 26,437 recipes and five typed registries preserved; source 1,397 files PASS. Known live drift remains untouched. Actor cache restored. N8i's incomplete Crusher-output observer and its failed evidence remain preserved.

This is partial evidence for mm.lithium-route. Chemical processing, electrolysis, Foundry recovery, acquisition and continuous automated transport are NOT_RUN here. Overall remains 131/237 (55.3%); native section 52/68 (76.5%). Next: reviewed full-chain fixture using these actual activated items.


# Complete Lithium route acceptance — N8k

One actual ordinary Spodumene rock and one rich ore produced five dusts, then five actual activated items in the Coal-heated Create Mixer. The exact component-identical output passed through native capabilities to acid leaching (1,250mB solution), precipitation (five items plus 750mB spent liquor), heated two-electrode reduction (five NuclearCraft Lithium powders), and Modern Foundry melting (75mB molten Lithium). No intermediate product was supplied.

The downstream run completed 15 native Vat cycles and 9,000 active timer increments. Four 200-tick controls rejected 199mB acid, missing Sodium Hydroxide, cold powered electrodes, and hot unpowered electrodes. The upstream same-run reader also revalidated the cold/unpowered activation controls and all five 241-to-1 native Mixer sequences.

Native build PASS in 1m24s: 112 Java sources, 285 classes and four reports frozen. Downstream observations span 10,443 ticks with 327,065 native assertions; upstream adds 1,834 ticks and 38,045 assertions. Independent verification passed 2,422,652 checks across both parts. All 27 combined corruption controls passed; the separate upstream suite previously passed 25 controls.

The Mixer Vat remained unfueled. The electrode Vat received 24,000mB Diesel: 18,800 consumed, 5,200 explicitly disposed, and 188,000mB native flowing CO2 recovered. Electrode observed power-usage tick sum was 506,850,000 (not labelled FE). Foundry consumed 50mB Blazing Blood, recovered 950mB unused fluid and used 115 of 150 burn units, with 35 residual units explicitly disposed. Activation consumed 1,470 Coal burn units and disposed 130. These are measured fixture costs, including controls and dwell, not optimized production costs.

All actual products, blade and both original electrodes were recovered. Both fixture reservations were cleared; actor cache, tickets and electrical network membership restored. All 26,437 recipes/five typed registries preserved; source 1,397 files PASS. Known live 8 changed/2 missing FAIL remains untouched.

This closes mm.lithium-route. Actual ordinary/rich Spodumene-to-molten-Lithium route accepted at existing 15mB per powder. Hardware, reagents, fuels, creative motors and creative electrode generators are explicitly supplied. Actual intermediates are manually transferred through native capabilities. Survival acquisition, connected automated transport, client/restart and deployment NOT_RUN. Existing unrelated output/accounting and live drift issues remain.

Lithium accepted:132/237 complete (55.7%),105 remaining. Native53/68 (77.9%),15 remaining. Next: Phosphate low-heat conditioning, acid recovery and fertilizer/Phosphorus split.


# Phosphate conditioning checkpoint — N8l

Five actual Phosphate rocks were crushed and all five resulting dusts conditioned in the ordinary Create Mixer over the native LOW Basic Burner. The same actual five output items are available for the chemical-stage callback. Two 200-tick holds rejected unlit and lowheat/unpowered processing. Five complete 361-to-1 native processing counters and -1 completion sentinels were independently verified.

Two Coal were supplied through the native fuel capability. Normal flint-and-steel ignition and the automatic second-Coal refill were observed; the actual ignition tool was recovered with one damage. Exactly 2,070 of 3,200 burn units were consumed and 1,130 explicitly disposed with empty test hardware.

Native PASS in 1m19s: 113 Java sources, 289 classes, four reports frozen, 2,368 ticks and 51,710 native assertions. Independent PASS: 584,327 checks and all 25 corruption controls. All 26,437 recipes/five typed registries preserved; source 1,397 files PASS. Known live drift remains untouched. All owned cells cleared, actor cache and tickets restored. Initial uncompiled r1 contained duplicate inherited fuel fields; r2 corrected those before integration and preserved r1 unchanged.

Chemistry, fertilizer and Arc remain NOT_RUN. No master-task credit yet: overall 132/237 (55.7%); native 53/68 (77.9%). Next: same actual conditioned items through Phosphoric Acid extraction and precipitation.


# Phosphate chemistry checkpoint — N8m

The same five actual conditioned ore items were extracted with 1,250mB Sulfuric Acid into 1,250mB Phosphoric Acid and five Slag, then precipitated with five Sodium Hydroxide into five purified Phosphate compounds and 625mB spent liquor. All ten native Vat cycles completed over 4,000 active increments. Full acid while cold, 249mB acid while hot, and missing caustic each held for 200 ticks. The hot-short-acid control recovered the original acid and retained/reinserted exactly 1,001mB; no extra acid or substitute intermediate was supplied.

Native PASS in 1m21s: 114 sources, 293 classes and four reports frozen. Chemistry: 4,767 ticks and 75,272 native assertions. Independent chemistry333,941 plus upstream584,327 checks PASS; all27corruption controls PASS. Actual fuel ledger:24,000mB Diesel supplied,15,000 consumed,9,000 explicitly disposed,150,000mB native flowing CO2 recovered. Original blade, all products and waste recovered;96 downstream dry cells and259 upstream cells cleared; original tickets and actor cache restored.

All26,437recipes/five typed registries preserved; source1,397files PASS. Known live drift remains untouched. Unrun r1 with a combined cold/short-acid negative remains preserved; r2 separates those controls. Fertilizer, Arc, acquisition, continuous transport, client/restart and deployment NOT_RUN here. Overall remains132/237 (55.7%); native53/68 (77.9%).


# Phosphate fertilizer checkpoint — N8n

One of the five actual ore-derived purified compounds was split and used in the ordinary Create Mixer with one supplied Nitrate and one supplied Bone Meal. Six Bone Meal were recovered (net five), and four actual compounds remain for the Arc. Native 200-duration recipe completed its observed61-to-1 timer and -1 sentinel. Compound alone, missing Bone Meal and unpowered complete feed each held200ticks. The first gate omits both reagents, so it is not evidence for nitrate-only rejection.

Native PASS in1m23s;115Java sources,295classes and four reports frozen. Fertilizer766ticks/10,421native assertions; independent52,657plus918,268upstream checks PASS. All22corruptions rejected. Four owned blocks and84dry cells cleared; original tickets and actor cache restored. All26,437recipes/five typed registries preserved; source1,397files PASS. Existing unrelated live drift untouched.

Arc, acquisition, continuous automation, client/restart and deployment NOT_RUN here. Full route remains open. Overall132/237 (55.7%); native53/68 (77.9%).


# Complete Phosphate route acceptance — N8o

Five actual Phosphate rocks passed through Crushing Wheels, LOW Basic Burner conditioning, acid extraction and precipitation into five actual purified compounds. One compound, one supplied Nitrate and one supplied Bone Meal produced six Bone Meal (net five). The remaining four actual compounds entered the native Arc with two supplied Coke dust and produced one elemental Phosphorus. No intermediate product was fabricated. Five Slag and625mB spent liquor were recovered.

The formed77-block Arc used only its adjacent unsailed Windmill/Dynamo:307,219FE generated,307,200FE consumed across800active native ticks,19FE explicitly disposed after recovery. Wrong orientation, missing electrode, physical obstruction, buffer starvation and resume controls passed. All three electrodes were recovered with728wear each;72zero-remainder work ticks correctly skipped wear. Final product remained stable for40ticks after the source stopped.

Native PASS in2m8s;116Java sources,299classes and four reports frozen. Arc observations span28,789ticks. Across conditioning, chemistry, fertilizer and Arc, 254,172native assertions and 2,036,417independent checks passed. All22combined corruption controls rejected altered quantities, additives, power, time, ownership, upstream ore and fertilizer evidence. Separate conditioning25, chemistry27 and fertilizer22control suites remain accepted.

All owned hardware reservations cleared, exact final products/electrodes recovered, original tickets and actor cache restored. All26,437recipes/five typed registries preserved; source1,397files PASS. Known live8changed/2missing FAIL remains untouched. No gameplay recipe or production files changed.

This closes mm.phosphate-route. Same-run existing ore-to-fertilizer-and-elemental-Phosphorus route accepted. Native Windmill/Dynamo powers the final Arc; upstream kinetic machinery uses declared creative motors. Hardware, reagents, fuel and electrodes are supplied. Actual intermediates are manually transferred through native capabilities. Acquisition, continuous automatic transport, client/restart and deployment NOT_RUN. Existing unrelated output/accounting/live drift issues remain.

Phosphate accepted:133/237 complete (56.1%),104remaining. Native54/68 (79.4%),14remaining. Next: Chromite conditioning, exclusive Fan and Chromium recovery.


# Chromium conditioning checkpoint — N8p

One actual ordinary Chromite and one rich ore yielded five dusts; those same dusts plus five supplied Sodium Hydroxide yielded five alkaline-roasted Chromite in the Create Mixer. Ordinary Coal heat and unpowered special heat each rejected the complete feed for200ticks. Five241..1native counters completed with -1sentinels.

Native PASS in1m28s:117Java sources,303classes,four reports frozen. 1,834ticks/39,722native assertions;439,758independent checks and all28corruption controls PASS. Coal1,600units accounted as200consumed and1,400displaced by the native Cake interaction. Cake3,200units accounted as1,470consumed/1,730disposed. Actual five items recovered;259dry cells cleared and original tickets/actor cache restored.

All26,437recipes/five typed registries preserved; source1,397files PASS. Existing live drift untouched. Fan, purification/reduction, Arc, acquisition, connected transport, client/restart and deployment NOT_RUN. Overall133/237 (56.1%); native54/68 (79.4%).


# Chromium actual-feed fan checkpoint — N8q

The five actual alkaline-roasted Chromite from ordinary/rich ore passed through an actual Industrial Iron Fan, source water and Depot. Five Chromium-bearing fractions and one naturally rolled Slag were recovered. An ordinary White Concrete Powder calibration was processed and recovered separately. Native completion clocks were233 and463; all461 consecutive frames preserved the225-cell block/entity/fluid mask.

Native PASS in1m46s.118Java sources,306classes and four reports frozen.16,157fan checks plus439,758upstream checks =455,915independent checks; all22corruption controls PASS. Original four scoped tickets restored; hardware/fluid cleanup and actor-cache restoration PASS.26,437recipes/five typed registries and1,397source files preserved. Existing unrelated live drift untouched.

Chemistry, Arc, acquisition, continuous connected transport, client/restart and deployment NOT_RUN. This is a partial receipt, not task completion. Overall133/237 (56.1%); native54/68 (79.4%).


# Chromium chemistry checkpoint — N8r

The same five actual Industrial Iron fan fractions from ordinary/rich Chromite were purified with1,250mB Sulfuric Acid into5precipitate and625mBspent liquor. The same5precipitate reduced with2,500mBHydrogen into5ChromiumDust in a naturally formed2x2Firebrick Vat. Ten original cycles completed over4,600active increments. Four200tick controls passed: cold full acid feed, hot249mBacid, hot499mBHydrogen and unpowered hot full reduction feed. Original acid was recovered/reinserted; no substituted processing intermediates.

Native PASS in1m55s:119sources,310classes and four reports frozen.5,564ticks/5,521frames/86,819native assertions.395,678chemical plus455,915upstream =851,593independent checks; all30corruptions rejected. Fuel ledger: [{"rig": 0, "dieselSupplied": 24000, "dieselConsumed": 17600, "dieselDisposed": 6400, "exhaustRecovered": 176000}]. Same5powders and625mBspent recovered, original mixing blade returned;96dry chemical cells cleaned and prior tickets/actor cache restored.

All26,437recipes/five typed registries and1,397source files preserved; known live drift untouched. Arc, acquisition, continuous transport, client/restart and deployment NOT_RUN. Overall133/237 (56.1%); native54/68 (79.4%).


# Chromium route acceptance — N8s

One ordinary Chromite and one rich Chromium ore yielded five dusts. Those same items passed through special-heat alkaline roasting, an actual Industrial Iron Fan, heated purification and superheated Hydrogen reduction into five Chromium dust. Four actual dust then produced one Chromium ingot in the native Arc; the fifth remains in tracked custody. 2 naturally rolled Slag and625mB spent liquor were recovered. No processing intermediate was fabricated.

The formed77-block Arc used its adjacent unsailed Windmill/Dynamo:204,512FE generated,204,500FE consumed over500active ticks,12FE explicitly disposed after recovery. The unchanged recipe encodes204,800FE; native integer division computes409FE/tick, explaining the300FE difference. Wrong orientation, missing electrode, rotor obstruction, starvation and resume passed. Three electrodes recovered with455wear each;45zero-remainder work ticks skipped wear. Product and retained powder stayed intact through40ticks after source removal.

Native PASS in2m21s;120Java sources,314classes and four reports frozen. Arc observations span19,452ticks. Across conditioning/fan/chemistry/Arc, 206,048native assertions and 1,532,795independent checks passed. All24combined corruption controls rejected altered upstream ore/tier, material custody, energy, time, ownership and the integer remainder. Separate conditioning28, fan22 and chemistry30control suites remain accepted.

Owned hardware cleared, products/electrodes/retained powder recovered, original tickets and actor cache restored. All26,437recipes/five typed registries and1,397source files preserved. Known live8changed/2missing FAIL remains untouched. No recipe or production files changed.

This closes mm.chromium-route. Same-run existing Chromite conditioning, exclusive Industrial Iron fan, purification, Hydrogen reduction and Arc consolidation accepted. Final Arc uses physical Windmill/Dynamo power; upstream motors, hardware, reagents, fuel and electrodes are supplied. Actual intermediates are manually transferred through native capabilities. Acquisition, continuous automatic transport, client/restart and deployment NOT_RUN. Prior lower-tier physical fan rejection remains accepted. Unrelated output/accounting/live drift issues remain.

Chromium accepted:134/237 complete (56.5%),103remaining. Native55/68 (80.9%),13remaining. Next: actual silica-to-Silicon purification.


# Silica crushing checkpoint — N8t

Six actual Sand produced six Silica Dust through the original tagged recipe. Both motors held at zero for200ticks with all raw feed retained. After native128RPM opposing rotation resumed, stack-scaled Float decrement3.9613726139068604 produced dust at336 and Depot recovery337; teardown357, exit361. Native algorithm uses log2(stack count); the unexecuted single-item20-clamp reader draft was preserved and corrected before execution.

Native PASS in2m11s:121sources,317classes and four reports frozen.4,222native assertions,41,387independent checks and18corruption controls PASS.175owned dry cells cleaned; actual6dust retained, prior tickets and actor cache restored. All26,437recipes/five typed registries and1,397source files preserved; known live drift untouched. Silicon chemistry, acquisition, continuous transport, client/restart and deployment NOT_RUN. Overall134/237 (56.5%); native55/68 (80.9%).


# Silicon route failure — N8u

The actual Sand-to-Silica stage passed. The next stage selected carbon reduction with six actual Silica Dust and two supplied Coke Dust while cold. Both Coke Dust were then physically extracted through the normal item capability at tick 240. At tick 254, the native Firebox reached heat 8 and the Vat timer advanced to 1 despite the Coke remaining entirely outside the machine. Six Silica remained inside; no product had been created when the guard stopped the test.

Installed bytecode explains the stale selection: Vat inventories lack an inventory-change recipe callback, lazyTick only selects when the cached recipe is null, and handleRecipe advances the cached recipe without revalidating its item requirements. Fluid changes have a separate callback. The staged operability fix checks native attachments and power, not ingredient availability.

Native FAIL is preserved. Compile PASS; 122 Java sources, 321 classes and four reports frozen. The positive-route reader correctly rejected incomplete evidence; its corruption suite is NOT_RUN. All 26,437 recipes, five typed registries and baseline source files remain unchanged. Actor cache restored. Known unrelated live drift remains untouched. Failed hardware is retained only in the disposable test world. No production changes.

Silicon remains BLOCKED. A future Vat repair must address stale ingredient selection together with the separately documented output-loss/backpressure defects, with quantities, reusable ingredients, timer behavior and partial input/output controls preserved. Do not count a route as working by removing the missing-Coke check. Completion without Coke has NOT_RUN; this receipt proves invalid progress only.

134/237 complete (56.5%), 103 remaining; native 55/68 (80.9%), 13 remaining. Silicon blocked by native stale item-recipe selection. Continuing Coal/Tar source and native feasibility.


# Coal/Tar native accounting — N8w

One supplied registered Coal Dust produced one actual Coke, 120,000 mB Coal Tar and 24,000 mB Hydrogen in the naturally formed size-2 TFMG Coke Oven. No Sulfur was produced. Native code emits the recipe's full 100 mB Tar and 20 mB Hydrogen on each of 1,200 active processing ticks. These are 1,200 times the values previously treated as batch totals.

The primary tank filled at tick 140 with 8,000 mB Tar and 1,600 mB Hydrogen. A 200-tick hold preserved the original dust and timer 1,120. Normal sided extraction resumed processing. The single Coke appeared as a native item entity at tick 1,461, was recovered once, and all actual liquids were drained into tracked custody. Empty-machine dwell, hardware removal and original chunk tickets passed; actor cache restored.

Native PASS in 2m30s. All 123 Java sources, 323 compiled classes and four reports frozen. 16,405 native assertions, 20,606 independent checks and 14 corruption controls passed. All 26,437 recipes, five typed registries and baseline source files preserved. Known unrelated live drift untouched. Earlier N8v fixture constructor compile failure is preserved; no machine ran in that attempt.

This is a confirmed accounting incompatibility, not acceptance of those inflated yields. Coal/Tar remains BLOCKED. No recipe coefficients or machine code were changed. Reconciling batch authoring with native per-tick integer fluids needs a scoped solution covering oven size and interrupted/blocked output behavior; silently rounding or changing the agreed totals is not an accepted fix.

The next source finding is separate: native distillation divides each branch's input consumption by six. With two Tar outputs at heat 2, code predicts 332 mB actual input consumption for 700 mB Creosote and 150 mB Naphtha, leaving 668 mB from a supplied bucket. This distillation prediction is NOT_RUN and must not be reported as a measured result.

Machine characterization only, with one supplied registered Coal Dust and manually recovered native outputs. Upstream Coal crushing, downstream distillation, acquisition, continuous automatic transport and deployment NOT_RUN. Full route remains blocked because authored fluid totals are consumed as per-tick rates by this native implementation.

134/237 complete (56.5%), 103 remaining; native55/68 (80.9%),13 remaining. Coal/Tar native coking characterized; balance blocked. Next: native distillation accounting.


# Tar distillation accounting — N8x

A native four-high Steel Tank, single Firebox, controller and two outlets processed the existing Tar fractionation recipe. One supplied bucket produced700mB Creosote and150mB Naphtha while consuming only332mB Tar. The remaining668mB Tar was physically recovered. The two native branches each drain integer(1000/6)=166mB. Actual production took one native tick; the encoded100-tick duration was not observed as a processing delay.

All three200-tick boundaries passed: full bucket while cold, heated999mB with the actual withdrawn1mB retained separately, and the668mB remainder after production. Returning the same1mB triggered the single output pair. Heat came from a normal Firebox and remained2. Actual process fluids and exhaust were recovered; undrainable Diesel was measured and explicitly disposed with the empty test hardware. Original tickets and actor cache restored.

Native PASS in2m43s:124Java sources,325classes and four reports frozen;682observed ticks. 6,455native assertions and13,766independent checks passed;14corruptions rejected. The first reader selected a future phase at the first snapshot because of an incorrect `or t==40` condition. Its failed result and executed reader are preserved. R2 corrects only that initial-frame selection and passes against the same frozen native data; Minecraft was not rerun.

All26,437recipes, five typed registries and baseline source files preserved. Known live drift untouched. Coal/Tar remains BLOCKED because both coke production and two-output distillation disagree with authored batch accounting. This probe records actual behavior and does not approve the inflated yields or silently alter established values.

Native two-output Tower accounting only, supplied1000mBTar and8000mBDiesel. Actual cold and short-input gates, remainder dwell and output/fuel custody proved. Connected Coal/Coke chain, full/partial/wrong-fluid output behavior, acquisition, continuous transport and deployment NOT_RUN. Recipe balance and processing time remain unresolved; no coefficients or machine code changed.

134/237 complete (56.5%),103remaining; native55/68 (80.9%),13remaining. Coal/Tar discrepancies measured and recorded. Continuing powered chemical/fluid endpoints (CF01–CF10).


# Native Hydrogen Rotary — N9a

CF01/CF02 actual endpoint proof passed:10001mB TFMG Hydrogen converted into10001Mekanism chemical units, then the same actual chemical returned10001mB TFMG Hydrogen.20002actual native operations consumed1000100J at50J/operation.1017500J supplied,17400J measured and disposed with owned empty hardware. Both noncanonical NC and Mek Hydrogen fluids were rejected by native sided input capabilities.

Four200tick holds passed: unpowered feed, powered wrong mode, actual full chemical output and actual full fluid output. Full tanks were filled by actual processing. Recovering1unit released each output-pressure hold without lost remainders. Native frames retain each store, retained stack, action, mode, cache and energy charge.231699native assertions,358629independent checks and22negative controls passed.125sources327classes4reports frozen; native3m10s;21063observedticks. Source1397files/26437recipes/five typed registries preserved; actor cache restored and known live drift untouched.

**Automatic mode-only recovery FAILED.** After switching back from the empty chemical direction, the machine remained paused with `hasNoRecipe=true`, `pausedForErrors=true`, `shouldUnpause=false`, the same cached target recipe and20000J. At640, a recorded normal withdrawal and return of the same1mB changed the native cache flags; processing began at641. This diagnostic recovery is not a pack fix and does not pass CF10 automatic mode recovery. The exact installed `nextMode()` only changes mode and marks saved state; it does not notify the recipe monitor of the changed input direction. A narrowly scoped cache notification is ready for staged implementation review.

The earlier owner-stage explanation was incorrect. Actual runtime evidence shows `requiredStage=NONE`, `canFunction=true` and no owner both before and after recovery. No team/research mapping or permission was changed. N8y failure and N8z observer failure are preserved. N8z reflected over Mekanism's public ticker and thereby resolved an unrelated client SoundInstance field; N9a reads the public ticker directly.

CF03–CF08 remaining endpoints, typed transport, reload and acquisition are not established by this test. NuclearCraft CF04/CF08 native fixture/readers are prepared but NOT_RUN. Overall134/237complete(56.5%),103remaining; native55/68(80.9%),13remaining. Chemical plant remains IN_PROGRESS.


# NuclearCraft chemical endpoints — N9b

Actual Chemical Reactor: 250mB NC nitric acid +750mB NC hydrochloric acid produced1000mB NC aqua regia over300 active native ticks, consuming15000FE. Actual Electrolyzer:250mB NC hydrofluoric acid produced250mB NC hydrogen +250mB NC fluorine over100 active ticks, consuming5000FE. The normal sided fluid input rejected Mekanism hydrofluoric acid during simulation and execution.

Both machines passed200-tick initial power-off, halfway power-loss and completed-output holds. Each received two exact half-energy tranches. NuclearCraft reserves its inputs before processing: the observer tracked the pending recipe and retained halfway progress, so reserved inputs are neither lost nor counted twice. Actual products were withdrawn once; process stores and supplied energy ended empty. No catalysts, upgrades, internal fills, progress setters or manual machine ticks were used.

Native941ticks/15682assertions,39641independent checks and19negative controls passed.126sources330classes4reports and the1m23s successful run are frozen.26437recipes, five typed registries and1397source files were preserved. Actor cache restored. Existing live drift is recorded and untouched.

This accepts CF08 and the NC consumer portion of CF04. Actual upstream Rotary delivery, remaining CF endpoints, connected physical pipes, save/reload and acquisition remain NOT_RUN. Overall134/237(56.5%); native55/68(80.9%). Chemical plant remains IN_PROGRESS.


# Rotary direction cache repair — R19 / N9c

Switching Rotary direction now notifies its existing recipe monitor when the direction actually changes. The native monitor rechecks eligibility and unpauses cached errors before normal processing. This changes one existing mixin class; the owner/team stage guard is unchanged. No recipe, fluid identity, quantity, energy rate or timing changed.

The exact original N8y Java fixture and reader were replayed without the diagnostic one-unit withdrawal/return. N8y had stalled after the mode switch until its11001-tick guard failed. Under R19, the mode was restored at440 and conversion resumed at441. The actual10001mB hydrogen batch converted to chemical and back with20002operations consuming1000100J. Four200-tick unpowered, wrong-mode, full-chemical and full-fluid holds passed.229491native assertions,313364independent checks and19negative controls passed across20863observed ticks. Native run1m12s;126sources330classes4reports frozen; actor cache restored.

The full offline build and KubeJS history validation passed. Ordinary Gradle tests were NOT_RUN_NO_SOURCE. The archive comparison found exactly one changed class and1132unchanged entries, with no additions/removals. All26437loaded recipes, five typed registries and1397baseline source files were preserved. Known live drift is recorded and untouched.

R19 is staged only. CF01/CF02 and selected CF10 controls are accepted; the complete chemical plant, remaining reagent endpoints, physical pipes and actual save/reload remain unfinished. Overall134/237complete(56.5%),103remaining; native55/68(80.9%),13remaining.


# Reagent Rotary endpoints — N9d

Five actual powered1000-unit round trips passed. NC chlorine returned Mek chlorine fluid; NC hydrofluoric acid returned Mek HF fluid; TFMG sulfuric acid returned TFMG acid; legacy Mek sulfuric acid canonicalized to TFMG acid; Mek sulfur trioxide returned Mek SO3 fluid. Both acid machines rejected NC sulfuric acid through normal sided insertion, in simulation and execution. No identity alias was added.

Each case consumed100000J over2000native conversions. Each passed200tick unpowered, powered wrong-mode, retained chemical and retained fluid holds. Actual intermediate chemicals were withdrawn and returned; only actual canonical output fluids were recovered. Native capacities stayed10000; full-tank pressure was separately proved by N9c and was not repeated using fabricated full tanks.

156844native assertions across14305case ticks,187874independent checks and20negative controls passed. Native1m9s;127sources333classes4reports frozen. Actor cache restored;26437recipes, five registries and1397source files preserved. Existing live drift untouched. Accepted R19 staging artifact unchanged.

CF03/CF04/CF05 Rotary endpoints plus CF07 SO3 conversion accepted. Actual downstream Vat/NC handoff, CF06 bootstrap chemistry, CF09 pipes and CF10 save/reload pending. No acquisition or complete plant claimed. Overall134/237(56.5%); native55/68(80.9%).


# Actual Rotary-to-contact-acid hydration — N9e / reader R2

The accepted native SO3 Rotary trial produced1000mB Mek sulfur trioxide fluid. The same actual recovered stack supplied250mB to an existing steel TFMG vat;750mB was retained. With250mB water, the real mixer produced250mB TFMG sulfuric acid. The Vat exposes no chemical tank on its input side; this fluid handoff did not treat a chemical handler as a fluid handler.

Missing one water unit prevented processing for200ticks. Full reagents with the native motor stopped also held for200ticks. The completed250mB acid output was retained200ticks, then actually withdrawn. The native blade was recovered; all process inventories and owned hardware were cleared. No physical pipe, save/reload or survival acquisition is claimed by this normal-capability handoff.

Native128sources336classes4reports are frozen. The first checker failed because it expected completion while incrementing the timer to300. Installed bytecode and frozen frames show300counter advances followed by a separate completion tick, clearing recipe and timer. R2 corrects that model; the original reader/failure is preserved and Minecraft was not rerun.32585downstream checks,37574upstream checks and17negative controls passed. Native consumer962ticks/13542assertions, with actual processing301ticks.26437recipes/five registries/1397source files preserved; actor cache restored; existing live drift untouched.

CF07 is accepted. Connected chlorine consumption, actual brine electrolysis, typed physical pipes and actual reload remain. Overall134/237(56.5%); native55/68(80.9%). R19 staging unchanged.


# Native brine electrolysis — N9f

The existing steel TFMG vat consumed 30 mB Mekanism brine and 250 mB water, producing one NuclearCraft sodium hydroxide dust, 2 mB Mekanism chlorine fluid and 1 mB TFMG hydrogen. Both native copper/zinc electrodes received power through actual generator blocks. No electrical state or process timer was assigned by the observer.

An initial 200-tick unpowered hold retained the reagents. Removing the actual zinc electrode at timer 500 paused for 200 ticks; reinserting that same recovered item resumed processing. Completion took 1,000 timer advances and the native separate completion tick. All three outputs were retained for 200 ticks and recovered. Both original electrodes, process stores, owned hardware and chunk tickets were accounted for during cleanup.

Native run: PASS, 1m 4s, 1,669 observed ticks and 33,629 native assertions. Frozen: 129 Java sources, 339 classes and four reports. Independent reader: 82,273 checks and 16 corruption controls PASS. Actor cache restored. All 26,437 recipe semantics, five typed registries and 1,397 baseline source files preserved. Existing live drift remains untouched. Ordinary acquisition, electrode automation, physical pipes and save/reload were NOT_RUN.

Overall 134/237 complete (56.5%); native verification 55/68 (80.9%). The chemical-plant task remains IN_PROGRESS. R19 remains staged only.


# Physical typed transport — N9i

Three real basic Mechanical Pipes delivered 7,001 mB Mekanism chlorine fluid between two real fluid tanks. Three real basic Pressurized Tubes delivered 13,001 Mekanism chlorine chemical units between two chemical tanks. Each source was held disconnected for 200 ticks. Destination tanks began full (32,000 mB fluid / 64,000 chemical units). Both networks filled to their native capacities (6,000 / 12,000), retaining 1,001 units at each source throughout a 200-tick full-output hold. After normal destination extraction, native transport delivered the complete payload, retained it for 200 ticks, and recovered it exactly once.

The opposite-type tank physically adjacent to each middle transmitter had no accepted capability and remained empty. Each frame independently accounts for source, destination, unique shared network, local transmitter buffers and actual recovered stacks. No network contents or networks were assigned, and no machine/network ticks were manually invoked. All 12 owned blocks and four owned chunk tickets were removed/restored with empty native material stores.

N9g compilation failed because the observer used an unsupported bounding-box constructor; Minecraft was NOT_RUN. N9h timed out because the observer changed raw connection mode without the refresh/notification used by the native interaction. Both attempts remain frozen. N9i uses the full existing public mode-change sequence from installed bytecode. This corrects the test controls; no gameplay patch was introduced.

N9i PASS in 1m: 691 native ticks, 8,877 native assertions, 32,535 independent checks and 18 corruption controls. Frozen: 130 sources, 341 compiled classes and four reports. Cache restored; 26,437 recipes, five registries and 1,397 baseline source files preserved. Existing live drift untouched. CF09 accepted; actual connected chlorine/HF and disposable save/reload remain. Reagent acquisition NOT_RUN.

Overall 134/237 complete (56.5%); native 55/68 (80.9%). R19 staging unchanged.


# Actual HF Rotary-to-NuclearCraft boundary — N9j

The existing powered Rotary converted 1,000 mB NuclearCraft hydrofluoric acid into Mekanism chemical and then 1,000 mB Mekanism HF fluid. The actual recovered stack was passed to the native NC consumer test. Offering 250 mB through the NC electrolyzer's normal fluid capability returned zero acceptance for both simulation and execution. All 1,000 mB of actual converted Mek HF remained accounted for throughout 944 observations.

The separately seeded exact NC HF positive control still consumed 250 mB NC HF and produced 250 mB NC hydrogen plus 250 mB NC fluorine, with 100 active ticks and 5,000 FE. The unchanged aqua-regia positive control also passed. Initial unpowered, halfway power-loss and retained-output controls remain intact. No fluid alias or consumer recipe was opened.

N9j native PASS in 1m4s, 941 consumer ticks and 16,628 native consumer assertions. Frozen: 131 Java sources, 344 classes, four reports. Independent checks: 39,641 NC plus 37,574 Rotary, with 27 corruption controls PASS. All 26,437 recipe semantics, five typed registries and 1,397 baseline source files preserved. Actor cache restored; existing live drift untouched. Physical pipe delivery to NC and survival acquisition NOT_RUN.

Chemical-plant queue: 8/10 checks complete (80%); remaining CF03 chlorine consumption and CF10 actual disposable-world save/reload. Overall 134/237 (56.5%); native 55/68 (80.9%). R19 staged package unchanged.


# Actual chlorine consumer — N9k / reader R2

The existing powered Rotary returned 1,000 mB Mekanism chlorine fluid from NC chlorine. Its actual recovered stack supplied 250 mB to the existing 2x2 steel TFMG vat hydrogen-chloride recipe; the other 750 mB remained in custody. With 250 mB TFMG hydrogen, the native heated mixer produced 250 mB Mekanism hydrogen chloride. The 249 mB hydrogen and motor-off controls held for 200 ticks each; completion required 600 timer advances plus the native completion tick. Product was retained 200 ticks before exact recovery.

A real singleton Firebox consumed 1,000 mB of the 4,000 mB seeded diesel across the whole test, including holds. All 10,000 mB generated flowing CO2 was actually recovered. The remaining 3,000 mB undrainable test fuel was explicitly accounted as disposed during owned hardware teardown. This is whole-fixture fuel use, not a new recipe balance or acquisition claim. The mixing blade and all process fluids were recovered; owned hardware/chunk tickets restored.

N9k native PASS in 1m3s: 1,262 consumer ticks, 19,877 native assertions; 132 sources, 347 classes and four reports frozen. The first independent reader failed because its fuel loop reused the assertion-counter variable n. Reader R2 only renames that local variable; the original failure remains preserved and Minecraft was not rerun. R2 passed 53,603 downstream checks, 37,574 upstream checks and 21 corruption controls. All 26,437 recipes, five registries and 1,397 source baseline files preserved. Cache restored; existing live drift untouched.

Chemical-plant checks 9/10 (90%); actual disposable save/reload remains. Overall 134/237 (56.5%); native55/68 (80.9%). R19 remains staged only. Physical pipes to this particular consumer and survival acquisition NOT_RUN.


# Selected chemical-plant native acceptance — N9o

All ten selected checks are accepted. The fixed master row `mm.chemical-plant` is complete; this does not close separate acquisition, recipe-policy or continuous factory integration tasks.

The native save N9m held 6,667 mB TFMG hydrogen fluid and 3,333 units Mekanism hydrogen chemical with zero energy, exact side configuration and decondensing mode. Its actual Anvil block entity and all 119 files were pinned after shutdown. N9o loaded a verified copy in a different server process, obtained fresh capability handlers without rewriting machine state/configuration, held the partial batch without power for 200 ticks, and completed the forward/reverse conversion. It recovered exactly 10,000 mB TFMG hydrogen. The whole roundtrip used 1,000,000 J for 20,000 native operations. Hardware and only owned tickets were removed; unrelated test tickets were preserved.

N9o native PASS in 1m8s: 17,328 observed ticks and 156,604 native assertions. Frozen-data reader PASS: 225,483 checks and 16 corruption controls. The earlier save phase passed 49,001 checks and 13 controls. All 26,437 recipes, five typed registries and 1,397 baseline source files preserved. Both original checkpoint and immutable snapshot still match all 119 hashes. Temporary actor cache restored. Existing live drift remains untouched.

The failed N9l energy-capacity attempt and N9n ticket-persistence assumption remain frozen. GameTestRunner clears all forced chunks after a test batch; GameTestServer constructs fresh level metadata. R3 respects those documented test-harness behaviors by reacquiring only four bounded observer tickets and checking the actual new clock origin. It still requires byte-pinned saved block-entity state, a different process, normal native processing, exact quantities and unchanged sides. No machine or recipe changes were made for this correction. Regular dedicated-server metadata persistence is NOT_RUN.

| Check | Actual proof |
|---|---|
| CF01 | Actual powered 10,001-unit hydrogen roundtrip with canonical TFMG output. [HYDROGEN_ROTARY_N9C_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/HYDROGEN_ROTARY_N9C_ROOT_ACCEPTANCE.json>) |
| CF02 | Exact NC/Mek fluid hydrogen inputs rejected by the current canonical bridge. [HYDROGEN_ROTARY_N9C_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/HYDROGEN_ROTARY_N9C_ROOT_ACCEPTANCE.json>) |
| CF03 | NC chlorine converted; actual recovered Mek chlorine consumed by existing heated TFMG HCl recipe. [CHLORINE_HANDOFF_N9K_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/CHLORINE_HANDOFF_N9K_ROOT_ACCEPTANCE.json>) |
| CF04 | Actual recovered Mek HF rejected at NC input; all 1,000 mB retained; exact NC HF positive control processed. [HF_HANDOFF_N9J_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/HF_HANDOFF_N9J_ROOT_ACCEPTANCE.json>) |
| CF05 | TFMG and legacy Mek acid return canonical TFMG; exact NC acid rejected. [REAGENT_ROTARIES_N9D_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/REAGENT_ROTARIES_N9D_ROOT_ACCEPTANCE.json>) |
| CF06 | Native powered vat and actual copper/zinc electrodes yield NaOH dust, chlorine fluid and hydrogen fluid; electrode-loss pause. [BRINE_ELECTROLYSIS_N9F_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/BRINE_ELECTROLYSIS_N9F_ROOT_ACCEPTANCE.json>) |
| CF07 | Actual Rotary SO3 fluid consumed by native hydration; exact sulfuric acid output. [CONTACT_ACID_N9E_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/CONTACT_ACID_N9E_ROOT_ACCEPTANCE.json>) |
| CF08 | Actual NC reactor nitric/HCl input yields aqua regia with native energy/timing. [NC_CHEMICAL_N9B_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/NC_CHEMICAL_N9B_ROOT_ACCEPTANCE.json>) |
| CF09 | Physical mechanical pipes/pressurized tubes and sided tanks conserve complete payloads under full destination pressure; wrong registry excluded. [TYPED_TRANSPORT_N9I_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/TYPED_TRANSPORT_N9I_ROOT_ACCEPTANCE.json>) |
| CF10 | Paired actual save/load holds partial native state without power, refreshes sided handlers, completes conversion; N9c supplies full-output/mode/power controls. [ROTARY_RELOAD_N9O_ROOT_ACCEPTANCE.json](<C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack/industrial-colonies/execution/overnight-20260912/capabilities/ROTARY_RELOAD_N9O_ROOT_ACCEPTANCE.json>) |

Overall **135/237 (57.0%)**, 102 remaining. Native **56/68 (82.4%)**, 12 remaining. Chemical plant **10/10 (100%)**. R19 remains staged only; independent review is NOT_COMPLETED. Survival acquisition, a fully continuous combined plant, client visual acceptance and deployment are NOT_RUN.


# Actual Uranium and Thorium ore-to-feed — N9p

Both existing ore paths passed. Five supplied Uraninite and five supplied Thorium Ore were processed separately by connected native Crushing Wheels. The actual five bearing dust from each crusher passed into a naturally formed 2x2 Firebrick Vat with its native mixer/blade and Firebox. Each family completed five cycles of each of its four existing recipes: leach, impurity removal, chloride/oxygen refining and hydrogen reduction.

Per family, the actual recipe bill was 2,000 mB TFMG sulfuric acid, five NC sodium hydroxide dust, 1,250 mB Mekanism hydrogen chloride fluid, 500 mB Mekanism oxygen fluid and 1,250 mB TFMG hydrogen fluid. Exact recovered output: five matching NC Uranium/Thorium Dust plus 1,250 mB spent leach liquor. No upstream intermediate was supplied or replaced. Per-family native reaction counters totalled 9,000 advances across 20 completed cycles.

Each crusher passed a 200-tick stopped-motor control. Each chemical path passed six 200-tick controls: cold full feed, hot 399 mB acid, missing caustic, 99 mB oxygen, 249 mB hydrogen and full hot reduction feed with the motor stopped. All blade, intermediate, product and waste recoveries were tracked through actual capabilities. Owned hardware and chunk tickets were cleared without disturbing unrelated tickets.

Each entire chemical fixture supplied 40,000 mB Diesel and consumed 33,400 mB across processing and holds. All 334,000 mB native flowing CO2 was recovered; the undrainable 6,600 mB remaining test fuel was explicitly accounted as disposed on teardown. These are whole-fixture observations, not a proposed per-recipe fuel bill.

Native N9p PASS in 1m13s. Both paths each observed 318 upstream ticks and 10,415 chemical ticks, totalling 334,540 native assertions. The frozen-data reader passed 1,553,080 checks and all 24 corruption controls. All 26,437 recipes, five registries and 1,397 baseline source files preserved; actor cache restored. Existing live drift untouched. 135 Java sources, 357 compiled classes and four native reports frozen.

Uranium/Thorium paths **2/2 (100%)**; master row `mm.uranium-thorium-route` is complete. Overall **136/237 (57.4%)**, 101 remaining. Native **57/68 (83.8%)**, 11 remaining. Existing fuel/isotope owner decisions and the separate Extreme Reactors burn test remain open. Automatic connected transport, acquisition, client/reload and deployment are NOT_RUN. R19 remains staged only; independent review NOT_COMPLETED.


# PGM crude milling — N9q

The actual native Millstone consumed 64 supplied Ultramafic Rocks, each in a separate native 500-counter cycle. Every consumed rock produced zero or one approved metal result. The run recovered 13 Osmium Nuggets and four Platinum Trace Fragments; 47 rocks yielded nothing. No random seed or result was forced. No Iridium occurred in this finite sample, which does not establish the statistical weights or guarantee first Osmium.

The fixture passed 200 ticks with the full raw stack and stopped motor, all 64 cycles at native 128 RPM, 200 ticks retaining all outputs and actual output extraction through the native capability. All produced material and the owned hardware/tickets were accounted. Native PASS in 1m4s, 4,557 ticks, 56,928 assertions. Frozen-data reader PASS: 171,926 checks and 16 corruption controls. All 26,437 recipes and five registries preserved. Actor cache restored. Source baseline preserved; existing live drift untouched.

Crude processing is accepted. Wet sequential separation, later reduction and consolidation remain unverified for the whole `mm.pgm-route` task. The known Vat multi-item merge issue remains a separate open dependency; this crude result does not resolve it. Connected automation, survival acquisition, client/reload and deployment are NOT_RUN. R19 remains staging only. Independent review NOT_COMPLETED.

Overall **136/237 (57.4%)**, 101 remaining; native section **57/68 (83.8%)**, 11 remaining.


# Actual PGM wet processing — N9r

Four supplied Ultramafic Rocks passed through actual native Crushing Wheels. Their four recovered dust passed into a naturally formed 3x3 Firebrick Vat with native mixer and Firebox. The same liquid passed through aggressive leaching, Osmium-first separation and Platinum-second separation. No supplied intermediate, forced roll or replacement product was used.

Actual separation: seven Osmium fractions, two Platinum fractions and one optional Iridium residue. All seven Osmium fractions and both Platinum fractions were reduced. The actual Iridium residue passed harsh purification and reduction. Final recovered products: seven Mekanism Osmium Dust, two NC Platinum Dust, one NC Iridium Dust, and 1,750 mB spent liquor. The 1,000 mB mixed PGM solution and subsequent 1,000 mB mother liquor were each consumed once.

Reagent bill: 1,750 mB TFMG sulfuric acid, 1,000 mB Mekanism hydrogen chloride fluid, 250 mB Mekanism oxygen fluid, one NC sodium hydroxide dust, 5,000 mB TFMG hydrogen, and 500 mB Mekanism chlorine fluid. Fourteen native reaction cycles totalled 7,600 counter advances. Six 200-tick controls passed: cold full feed, hot 499 mB HCl, 249 mB Oxygen, absent caustic, 499 mB Hydrogen and hot full feed with stopped rotation. The crusher also retained all raw material for 200 unpowered ticks.

Native N9r PASS in 1m7s: 8,968 chemical ticks, 144,532 total native assertions including upstream crushing. Frozen-data reader PASS: 679,984 chemical checks plus 34,757 crusher checks, all 20 corruption controls. All 26,437 recipes and five registries preserved. 138 sources, 366 classes and four reports frozen; actor cache restored; 1,397 source baseline files preserved. Known live drift untouched.

The observed crude and wet fixtures both pass, but the complete PGM task remains BLOCKED by `mm.vat-output-policy`. Exact native code can skip the Iridium roll after merging optional Platinum; retained Platinum can also skip both optional outputs on later batches. N9r's actual two-Pt/one-Ir result does not demonstrate a loss and does not resolve that source-confirmed defect. No output policy, recipe or probability changed. Arc consolidation, rich ores, acquisition, continuous connected automation, client/reload and deployment are NOT_RUN. R19 remains staging only; independent review NOT_COMPLETED.

Overall **136/237 (57.4%)**, 101 remaining; native **57/68 (83.8%)**, 11 remaining. Continue the connected Melter/Faucet/casting boundary while output policy is unresolved.


# Connected Foundry line — N9u

Two physically connected Modern Foundry Melter → Faucet → Casting Table → Hopper → Barrel rigs passed native execution. The first melted three Raw Iron to 75 mB, held the partial casting for 200 ticks, then accepted a fourth Raw Iron and cast one ingot. The second melted twelve Raw Iron in four actual three-slot batches, stopped the Faucet after its current packet, retained the 90/210 mB destination/source split for 200 ticks, then resumed all three ingot casts. Both retained full finished output for 200 ticks with the physical Hopper locked, then automatically transferred all four ingots into their Barrels after unlock.

All actual raw material, molten iron, retained casts, products and Lava were accounted for. Rig one consumed 100 mB Lava and recovered 900 mB; rig two consumed 200 mB and recovered 800 mB. Both original casts were recovered through the native inventory API. This Raw Iron recipe has no byproduct, so no fictitious byproduct test is claimed. All four casts completed exactly 40 native cooling counter advances. No molten metal or output was supplied, no forced machine tick or output setter was used.

N9u PASS: 2,122 native ticks, 54,877 native assertions. Reader R4 PASS: 589,907 checks and 23 corruption controls. The earlier reader incorrectly assumed every first full-fluid snapshot had cooling counter zero; one correctly had counter one after a same-world-tick fill. R4 verifies each actual counter advance against the observed initial counter. The original failed receipt remains preserved; no native rerun was used for this reader repair. N9s and N9t fixture failures also remain preserved.

139 Java sources, 369 classes and four reports frozen; actor cache restored. All 26,437 recipes, five typed registries and 1,397 source baseline files preserved. Existing live drift (eight changed, two missing) remains untouched and is not reported as a clean live baseline. R19 remains staging only; independent review NOT_COMPLETED. Other materials, full Melter source-tank policy, survival acquisition, chunk reload and deployment are NOT_RUN.

This closes `mm.melt-cast-automation` within its connected transfer, partial/full destination, interruption and custody acceptance. Overall **137/237 (57.8%)**, 100 remaining; native **58/68 (85.3%)**, 10 remaining. Continue the existing Refined Radiance machine route and its PRC energy/upgrade behavior.


# Refined Radiance pressure treatment — N9v

Three placed native Mekanism PRCs each consumed one supplied existing Radiant Precursor, 1,000 mB NuclearCraft Boric Acid and 8,192 units of Mekanism Hydrogen Chloride chemical, and each produced exactly one Pressure-Conditioned Radiant Composite. These are supplied endpoint tests: upstream component manufacturing, actual mixing, separate Arc stabilization and acquisition remain NOT_RUN.

| Installed upgrades | Native processing ticks | Joules per processing tick | Total consumed Joules |
|---|---:|---:|---:|
| None | 12,500 | 1,605 | 20,062,500 |
| Eight speed + eight energy | 1,250 | 16,050 | 20,062,500 |
| Eight energy only | 12,500 | 161 | 2,012,500 |

The recipe's `energy_required=1600` adds to the machine's five-Joule base usage each processing tick. It is not the total recipe energy. Eight speed upgrades alone demand 160,500 J/t while the machine can store only 2,000 J. The actual fully charged chamber remained stalled with all material intact for 200 ticks. Normal insertion of eight energy upgrades raised capacity to 20,000 J and reduced demand to 16,050 J/t; processing then completed. This is observed installed behavior, not a recipe or upgrade policy change.

The other controls held a full unpowered bill and a powered 8,191-unit HCl shortage for 200 ticks. Each of the three processing chambers was interrupted at progress 100 by normal manual energy extraction, held without power for 200 ticks with its progress retained, then resumed. All three actual outputs, 24 original upgrade items and unused energy were recovered through native APIs. No direct upgrade installation, process tick, progress write or contents setter was used.

Native N9v PASS in 1m8s: 13,201 observed ticks, 342,481 assertions. Frozen-data verification PASS: 778,273 checks and 17 corruption controls. 140 sources, 372 compiled classes and four reports frozen; actor cache restored. All 26,437 recipes, five registries and 1,397 source baseline files preserved. Known live drift remains untouched; R19 stays staging only. Independent review NOT_COMPLETED.

`mm.radiance-route` is IN_PROGRESS. Overall **137/237 (57.8%)**, 100 remaining; native **58/68 (85.3%)**, 10 remaining. Next: manufacture the existing lattice and silicon substrate in real Arc Furnaces, then the PGM matrix/composite in the assigned Industrial Iron Mixer and the separate final Arc stage. Preserve the upstream Titanium/Silicon/PGM blockers and do not claim a supplied-input test establishes acquisition.


# Existing full Radiance route — N9w

One Refined Radiance was produced through all six current recipe types in nine actual machine cycles: two refractory lattice Arc batches, two silicon substrate Arc batches, two PGM matrix batches in the assigned Industrial Iron Mixer, one composite mixing batch, native PRC pressure treatment and separate final Arc stabilization. Every intermediate handed to a later stage was recovered from the preceding actual machine. No intermediate product or Refined Radiance was supplied.

The exact full bill is 32 NC Titanium Ingots, 32 NC Tungsten Ingots, 12 existing High-Purity Graphite, eight Mekanism Osmium Ingots, four NC Platinum Ingots, two NC Iridium Ingots, 16 existing High-Purity Silicon and four pink TFMG Semiconductors. Fluids: 1,000 mB TFMG Sulfuric Acid and 1,000 mB NC Boric Acid. Chemical: 8,192 units Mekanism Hydrogen Chloride. All materials were reconciled in every observed inventory and retained intermediate against this original bill. No new material, tier, variant, recipe or progression rule was introduced.

The Arc stages consumed 21,993,600 FE. Their encoded total is 22,000,000 FE; native integer-per-tick rounding explains the 6,400 FE difference. The unupgraded PRC consumed 20,062,500 J, matching accepted N9v behavior. These energy units are reported separately. Remaining terminal supplies were recovered: 64,000 FE and 2,000 J. Three original electrodes were recovered, each with exactly 13,200 damage matching actual Arc advances. One normally inserted Blaze Cake supplied 3,200 special-heat counter units and the native 5,000-unit normal-heat tail; both were fully exhausted before teardown. Mixer countdowns were 361, 361 and 721, consistent with the installed 128 RPM calculation. Encoded recipe times were preserved.

N9w native PASS in 1m21s: 27,671 observed ticks and 399,923 assertions. Frozen-data route reader PASS: 2,362,190 checks and 14 corruption controls. Additional exact fuel, Mixer counter, Arc counter and electrode-wear verification PASS: 150,288 checks and six corruption controls. Existing N9v additionally proves the PRC's no-power/short-feed controls, speed-only capacity stall, native upgrade installation and interrupted progress. 141 sources, 374 compiled classes and four reports frozen; actor cache restored. All 26,437 recipes, five registries and 1,397 source baseline files preserved. Known live drift remains unchanged; R19 is staging only; independent review NOT_COMPLETED.

This closes `mm.radiance-route` for actual processing through existing machines. Feedstock, hardware, motor and terminal power were supplied to the isolated fixture. Survival acquisition, automated intermachine transport, reload, client and deployment are NOT_RUN. Existing Titanium, Silicon, PGM-output and Refined-Radiance-before-Allthemodium gate decisions remain open in their own tasks. No successful supplied-feed test resolves those upstream blockers.

Overall **138/237 (58.2%)**, 99 remaining; native **59/68 (86.8%)**, nine remaining. Continue the actual Extreme Reactors fuel, waste and reinforced-port boundary.


# Extreme Reactors fuel and waste endpoints — N9y

Two real 3×3×5 reactors formed using existing Basic and Reinforced blocks, each with three fuel rods, one control rod, ordinary fuel/waste ports and a passive FE power tap. No forced assembly, direct fuel insertion, heat modification or manual reactor processing ticks were used.

| Reactor | Actual supplied fuel | Actual waste recovered | Unburned fuel retained | FE extracted |
|---|---|---|---:|---:|
| Basic | 12 dedicated enriched-uranium pellets | 2 Cyanite ingots | 10,000 reactant units | 16,577,027 |
| Reinforced | 12 Mekanism plutonium pellets | 1 Magentite ingot | 11,000 reactant units | 13,446,747 |

Both reactors account for all 12,000 supplied reactant units. Remaining fractional usage counters were 0.028542519 and 0.03145635; these pending fractions are not additional integer material losses. Actual products remain in owned barrels; unburned fuel remains in shut-down reactors in the disposable test world, with native controller/barrel SNBT included in the evidence. Hardware was deliberately retained, not cleared while containing fuel. Extracted FE was an explicit test energy sink, not survival power infrastructure.

The Basic port accepted one plutonium pellet into its slot but refused to consume it for 200 ticks. The same actual pellet was recovered into its barrel; it never became Basic reactor fuel. Reinforced consumed its plutonium normally. Both tiers rejected generic NuclearCraft uranium, Yellorium and Blutonium ingots through simulated and real port insertion. The basic reactor then consumed the dedicated enriched-uranium pellets normally.

Loaded but inactive reactors, active reactors with 100% inserted control rods, and mid-burn shutdowns all retained their fuel through the 200-tick controls. Both reactors resumed and ejected their actual waste through native ports. Every observed tick checked material custody, exact reactant identities, port inventories, fractional counters, the 490-cell dry boundary, 92 owned block entities and ticket ownership. Original forced-chunk tickets were restored.

Native N9y PASS: 27,135 ticks and 665,760 assertions; 142 sources, 377 compiled classes and four reports frozen. Frozen reader PASS: 920,997 checks and 10 deliberately corrupted cases rejected. All 26,437 recipes, five typed registries and 1,397 source baseline files preserved. Live baseline still has the known eight changed/two missing files; untouched. Independent review NOT_COMPLETED.

N9x compilation failed because the observer compile-only list omitted the already installed Extreme Reactors and ZeroCore JARs. That attempt and its source remain frozen; its gameplay test was NOT_RUN. N9y only added those exact installed compile dependencies. No gameplay change or mod upgrade occurred.

`mm.er-cycle` remains IN_PROGRESS: the next test must carry actual Cyanite through the native Reprocessor to Blutonium. Downstream actinide conversion, survival acquisition, reload and deployment are NOT_RUN here. **Overall 138/237 (58.2%); native 59/68 (86.8%).**


# ER Reprocessor native continuation — N10b

Actual same-run reactor waste was transferred from its barrel through the Reprocessor's ordinary item port. The empty slot accepted one Cyanite, then accepted the second; its native slot limit changed from 1 to 64 after the first insertion. No port capacity, recipe lookup, lifecycle state or gameplay code was changed.

The naturally formed 3×3×7 Reprocessor consumed two Cyanite and 1,000 mB water and returned one actual Blutonium to the source barrel. Its first ten processing advances spent 250 FE, then power loss reset progress while preserving the inputs. Resumption took the normal 40 advances and 1,000 FE. All 1,250 FE came from the two actual reactors in this same run. A 200-tick unpowered control, short-water control, interruption and completed-output hold passed.

Native PASS: 27,135 reactor ticks plus 951 Reprocessor ticks; 697,917 native assertions. Frozen cycle reader: 14,245 checks plus the unchanged burn reader and ten corruption controls. All 26,437 recipes, five typed registries and 1,397 source baseline files preserved. Live baseline remains the known eight changed/two missing files; untouched. Independent review NOT_COMPLETED.

N9z's whole-stack admission failure remains frozen. N10a proved the global recipe manager available; its first diagnostic reader's opposite hypothesis was rejected. Corrected reader R2 passed against the frozen native evidence. These were observer assumptions, not gameplay defects.

Actual downstream actinide conversion is next. Full pellet return, automatic transport, survival acquisition, reload and deployment are NOT_RUN. Overall **138/237 (58.2%)**, native section **59/68 (86.8%)**; the ER task remains IN_PROGRESS.


# ER waste and actinide native production — N10c

The existing production path now has a same-run native proof: dedicated enriched-uranium pellets burned in a real Basic reactor, its two actual Cyanite ingots became one Blutonium in a real Reprocessor, that actual Blutonium became 1,000 Nuclear Waste in the Dissolution Chamber, and the actual waste became 100 Plutonium chemical in the Isotopic Centrifuge. All 100 units remain in a native radioactive-waste barrel. A real Reinforced reactor separately consumed the supplied Mek Plutonium pellets and produced one Magentite ingot, retained in its original barrel. The Basic port refused to consume that fuel.

No radioactive intermediate was supplied to skip a processing step. The initial reactor pellets, hardware, water and sulfuric acid were declared supplied endpoints. Transfers used actual native sided capabilities. The Mekanism machines used normal block-placement callbacks, including the Centrifuge's linked upper bounding block. No recipe, progress, fuel, heat, internal tank or capacity was forced.

The Dissolution Chamber ran 100 native advances at 400 J each: 40,000 J. The Centrifuge ran 100 native operations at 200 J each: 20,000 J. Native FE adapters accepted 183,600 FE from the prior reactor output and delivered 459,000 J (2.5 J/FE). Of that, 60,000 J was consumed, 159,600 J was recovered during the interruption into the declared external energy ledger, and 239,400 J remains in the machines. After earlier Reprocessor use, 29,838,924 FE remains in the original reactor-output ledger. No residual energy was silently discarded or credited twice.

The current Dissolution recipe has per-tick usage with the installed machine's stochastic draw. This run used **99** sulfuric-acid chemical units and retained **901** from the supplied 1,000. This is an observed bill, not a fixed99-unit recipe. The 200-tick initial power hold, interrupted25/100progress hold with unchanged acid, powered9/10waste short-input hold, and200-tick final Plutonium storage hold all passed. No radiation sources appeared. All154 block entities,1,090 dry boundary cells, reactor fuel and completed goods were retained; original chunk tickets restored.

Native PASS: 29,127 observed ticks across the chained helpers,714,038 assertions;144 sources,381 classes and four reports frozen. Frozen readers PASS:956,390 checks, plus10 deliberately corrupted actinide cases rejected. All26,437 recipes, five typed registries and1,397 baseline source files preserved. The known live8changed/2missing baseline drift remains untouched. Independent review NOT_COMPLETED.

The current route map preserves Magentite's Energizer/Fluidizer uses and the separate Spent Nuclear Waste disposal path. N6i already accepted native barrel decay and blacklisted actinide retention; N10c adds retention of actually produced Plutonium. The current pellet recipe needs1,000Plutonium,1FluoriteDust and1,000water and emits1pellet plus1,000SpentWaste. This run's100Plutonium is one tenth of that batch. A complete pellet return, Polonium production, survival acquisition, automatic physical transport, restart and deployment are **NOT_RUN** here. Nothing was added to bridge those limits.

The fixed `mm.er-cycle` acceptance is complete. **Overall139/237 (58.6%),98remaining; native60/68 (88.2%),8remaining.** Next: prepare the remaining BSCCO chamber native proof within a bounded isolated fixture. Nuclear ownership and missing feedstock decisions stay open in their existing tasks.
