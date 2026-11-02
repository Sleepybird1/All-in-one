# Fixed-value material policy tests

2026-09-09 current result: **48/48 pure Node regression tests PASS; 6/6 in-memory mutations detected.** Syntax checking also passes. Separately, the coordinated isolated runtime now confirms a successful Rhino callback and **299/299 owned recipes loaded and codec-verified** in stage `geology-gametest-20260909-064550-754`, run a3. These are distinct checks; neither proves a complete powered factory, real-player manual interaction, live installation, or error-free full pack.

This final report refresh used read-only tests, source/hash checks and existing runtime evidence. It changed no source, configuration, generated recipes, live files or staged files and launched no game.

Run from the project directory:

```powershell
node tools/material_processing/test_policy.js --mutations --installed-audit
node --check tools/material_processing/policy.js
```

The test harness executes the actual `policy.js` in a Node VM with a minimal recipe-event/JsonIO mock. It reads the generated catalog's actual policy maps and original installed-JAR recipe inventory; it does not write an exported policy log. Existing recipe fixture mutations are made in memory only. The six detected mutations disable the whole policy, erase nugget membership, erase finished-value membership, restore the Rhino-incompatible `const counts` binding, skip native casting-stack repair, or recreate an entity-melting recipe through an incompatible schema.

## Corrections verified

The initial, historical 33-case run found 11 failures. The current corrected suite covers:

- 1000 mB ingots, 9000 mB blocks, 25 mB Iron nuggets and 10 mB Gold nuggets; melting and casting use the same declared endpoint values.
- Count wrappers: `IngredientWithSize.basePredicate`, CreateMetallurgy `result.item.count`, TFMG `results[]`, NuclearCraft `item_inputs[]`/`item_outputs[]`, and multiple physical outputs. Ingredient alternatives are not summed as extra consumed items.
- Split molten inputs share the total material charge instead of each charging the full output total. Inputs round upward and outputs downward when an exact division cannot be represented.
- Native raw-material smelting/ore-melting bypasses are removed. Vanilla shaped/shapeless raw storage packing/unpacking is retained only when same-material raw units do not increase. Raw-to-ingot crafting and finished-metal-to-raw conversion are rejected; ordinary ingot/block conversion and unrelated hardware remain.
- Root's map fixes include `c:storage_blocks/raw_<metal>` and installed per-metal crushed raw forms. This closes the exact Modern Foundry raw Iron block recipe that otherwise gave 9000 mB versus the owned 1800 mB endpoint.
- The exact three native TFMG steel blast recipes survive. Their steel endpoints are capped at 200 mB for raw Iron, 200 mB for crushed raw Iron, and 75 mB for Iron dust. Slag, furnace-gas amounts, flux input, heat/hot-air consumption and processing time are unchanged.
- All Modern Foundry alloy recipes are removed, including an AllTheModium-namespace fixture. Brass/Bronze native alloy-smelter or Copper-plus-Zinc/Tin vat routes are removed when selected by the owned alloy map. The NuclearCraft molten Bronze chemical-reactor route is independently recognized from its molten metal feeds/output. Casting existing Bronze and intentional Create Mixer alloy recipes remain.
- Native NC ingot-former/melter establish 90 mB per ingot for the controlled shared metal fluids. Approved chemical-reactor/irradiator fields use that same density: a 144 mB metal quantity becomes 1600 mB, not 1000. Nonmetal compounds, water/reagents, item inputs/outputs, process time and energy remain untouched. Fuel/isotope fixtures are unchanged because Uranium/Thorium compounds are outside the controlled metal-fluid map.
- Unknown future NC codecs are not guessed: controlled-metal fields in them produce an explicit `review-unclassified-metal-fluid` audit entry while leaving the recipe unchanged.
- Controlled CreateMetallurgy casting outputs retain the native nested ItemStack shape after Almost Unified can flatten `result.item` into a string. The existing output count is transferred exactly once; this is not a global repair of unrelated metals.
- Four native entity-melting recipes with empty `ingredients` are normalized in place through `recipe.merge({results: ...})`. This preserves the original valid empty-input recipe and avoids re-entering KubeJS's incompatible nonempty-input creation schema.
- Policy-local lexical declarations use function-scoped `var` where required by the installed Rhino runtime. Synchronous iteration semantics, recipe decisions and quantities are unchanged.

## Installed-resource audit snapshot

The current dry audit visited **29,988** installed recipe JSONs with the generated policy map identified below:

| Action | Count |
| --- | ---: |
| Removed conflicting recipes | 1,207 |
| Normalized metal-fluid quantities through ordinary replacement | 574 |
| Normalized entity-melting quantities in place | 4 |
| Preserved and capped native steel recipes | 3 |
| Unclassified controlled-metal fluid recipes | 0 |

These are static installed-resource decisions, not the count of final runtime recipes. Conditions, data-pack priorities, scripts, dynamic mod recipes and the subsequent addition of owned recipes are resolved by the actual runtime. The recipe inventory does not execute mods. Regeneration or later policy-map changes may legitimately change these counts.

Snapshot SHA256:

- `policy.js`: `0A2456D9BA6005144CFB6C45339AA80DC9F586169981BC3382015905AA88C3D7`
- `test_policy.js`: `8A3781EBBF89FDF5137A44662FD891D43936AA30892BC1E7CDC463BFC3B6D265`
- `processing/material_processing_catalog.json`: `31F344D33295A70F4CC19C1F38B56C604DD13965C7E77E7EC701BC3EFAD4AD45`
- `build/material-processing/installed-inventory.json`: `93BB8589F5253ED2C6C0316F2112B85F46DDBE27B82159E431774CD627A0E71C`

Earlier policy corrections were scoped to `policy.js` and its regression harness; coordinated generation, recipe definitions, candidate staging and runtime acceptance have their own reports. The separate machine-tier seed correction and its audit retain their own provenance.

## Native runtime evidence — current stage 064550-754

Evidence is under `isolated-runtime/geology-gametest-20260909-064550-754/`:

- Run a2, `material-launch-a2.log:21991-21992`: the actual Rhino callback completed **1,366 audited policy changes** and installed **299 owned recipes** at 06:53:34. This proves the earlier redeclaration abort was fixed. It does not mean that entire a2 test passed: its report verified 297/299 recipes because the two distillation recipes omitted the native encoded `processing_time: 100` default.
- Those two owned recipes (`sulfur/desulfurized_oil_distillation` and `coal/tar_fractionation`) now explicitly declare their configurable processing-time default. This was a separate coordinated source/generation correction, not an unrelated-recipe repair.
- Run a3, `material-launch-a3.log:21985-21986`: the actual callback again completed **1,366** changes and installed **299** recipes at 07:04:12. `material-processing-report-a3.json` records **299/299** verified, no catalog problems, no encoded mismatches, and overall **PASS** with **145,355 assertions** across its seven sections. The log confirms the one required GameTest passed, then server shutdown and `BUILD SUCCESSFUL in 2m 44s`.
- The a3 report also confirms all 672 merged review-card UIDs retained and no remaining Modern Foundry alloy recipes. Its native-codec/direct-API scope explicitly excludes a powered factory and real-player manual processing. Broader runtime acceptance remains documented separately.

The current stage's `kubejs/industrial-material-processing-policy.json` records the actual **1,366 runtime actions**: 937 removals, 423 ordinary metal-fluid normalizations, four in-place normalizations and two steel-feed changes. It contains **zero unclassified-metal-fluid review entries**. These runtime totals are intentionally not substituted for the installed-JAR dry totals: scripts, conditions and recipe priority have already changed the runtime inputs.

The a3 catalog SHA256 matches the current catalog above. Its candidate JAR SHA256 is `8DF80E5C7E4B447F651696A9383A1487B26F557A67D6263DEAFA3805BC675D91`.

## Remaining log errors — provenance, not new batch failures

The log is **not clean**. This bounded review found no remaining owned `industrial_colonies:processing/` recipe parse/parity failures or policy callback aborts in a3. It did identify the following pre-existing failures, which were not broadened into this task:

- Ten non-controlled CreateMetallurgy casting recipes: Constantan and Electrum plates/ingots/nuggets/blocks, plus Netherite rods/nuggets. The current log's Almost Unified diagnostic names the same ten malformed casting outputs. The pre-material `isolated-runtime/geology-gametest-20260909-001051-895/controlled-run-a2-20260909.log` already records these exact ten failures (starting at line 3077). They are outside the controlled-metal repair map, not newly owned metal routes.
- Desh/Ostrum/Calorite `industrial_colonies:planetary/<metal>/feed_to_grit` recipes still serialize their tag argument as a 1000 mB fluid ingredient, which Create crushing rejects. The same serialized failure is present in the pre-material log at lines 3315, 3269 and 3393 respectively. Their companion `grit_to_concentrate` calls also already fail the native Mekanism enriching two-argument constructor in that log at lines 3062–3064.
- The six corresponding planetary calls are textually the same in the old stage, the current native export, and live `C:/Users/GodPC/curseforge/minecraft/Instances/All in one/kubejs/server_scripts/kjsgen_recipes.js` (live lines 5827/5831, 5853/5857 and 6084/6088). Export line numbers moved, but those calls and failures were not introduced by the material-processing batch.

Unrelated mod startup, creative-tab and heightmap warnings also remain; this report is not a full-pack warning remediation claim. No unrelated recipe was changed during this audit.

## Historical diagnostics — superseded checkpoints

The original 42/42 Node and 3/3 mutation checkpoint was a static result only. In the earlier **062055-929** stage's `material-launch-a2.log:22165`, native KubeJS then aborted at `itemStacks` with `TypeError: redeclaration of var counts`, despite exporting all 672 cards. The conditional `const counts` was the first repeatedly executed lexical declaration to fail. Node success had not proved Rhino compatibility.

Changing policy-local `const`/`let` declarations to `var` produced the subsequent **43/43 + 4/4** checkpoint, including a mutation that reinstates the broken binding. That earlier checkpoint still required runtime confirmation. It is superseded by the current **48/48 + 6/6** suite and the successful **064550-754 a2/a3** native callbacks above, not left as a pending present-day blocker. The old 578 total normalizations are now reported more precisely as 574 ordinary plus four in-place operations; the aggregate count did not decrease.
