# Material-machine bootstrap audit and scoped correction

Status: source/seed correction complete; runtime acquisition and the new full processing batch are not yet certified. Audited 2026-09-09. No live pack, saved world, approved texture, prior runtime evidence, or Java engine was changed by this task.

## Authoritative inputs

The authoritative machine definitions are the explicit `recipes` array in `progression/managed_recipe_overhaul.seed.json`, not a currently active family template. `machine_families` is empty. Historical `recipe_design_v2_*`, `recipe_design_v3_*` and `machine_recipe_dependencies.json` contain older tier assumptions; the current seed builds its six Industrial Iron sequenced machines on Weathered Iron deployer/press.

Baseline seed: 828 recipes; SHA256 `3D66CA27C3279EAEE1195D60F463AB1362361E82F152CD4C3C10E728A1945912`. Exact backup: `backups/material-processing-20260909/machine-tiers.seed.before.json`. After this bounded patch: 830 recipes; SHA256 `D9229B2C3E2177353B0B640B50B8CEB06B167F2AF36F236C0FE127484737E86C`. Later root-owned changes will legitimately change that hash.

Installed recipe evidence was read directly from `Mekanism-1.21.1-10.7.19.85.jar`, `tfmg-1.2.0.jar` and `ImmersiveEngineering-1.21.1-12.4.2-194.jar`. The live KJSGen default project and scripts were inspected read-only. The live default project has no producer for the protected Metallurgic Infuser or Rotary outputs, only their removals and downstream uses. Their absence was not treated as permission to overwrite arbitrary user cards: the parent explicitly approved recovery of these two outputs, and the third protected output, Energy Tablet, remains untouched.

## Changes: exact recipe IDs and operations

All IDs below are prefixed `industrial_colonies:`. Existing recipe IDs, outputs, loop counts and ingredient quantities remain unchanged except the named substitutions/additions. No broad tier rewrite was applied.

| Recipes | Before | After and reason |
| --- | --- | --- |
| `mekanism_pre_nuclear/electrolytic_separator`, `chemical_oxidizer`, `chemical_infuser` | Industrial Iron deployer/press | Weathered deployer/press, so reagent production precedes the Ti/W Industrial gate. |
| `mekanism_components/electrolytic_core`, `basic_chemical_tank` | Industrial Iron deployer/press | Weathered deployer/press. Moving the machines alone would leave their core/storage prerequisites circular. Osmium inputs are retained. |
| `mekanism/thermal_evaporation/block_batch`, `controller`, `valve` | Industrial Iron press/deployer | Weathered press/deployer, retaining all material quantities. This preserves a reachable native brine supply. |
| `tfmg_heavy_electrical/electrode_holder` | Railway machines; heavy machinery casing input/transitional | Copper machines; ordinary steel casing input/transitional. Existing two steel clamps, lead shielding and two copper wire feeds remain. |
| `fluid_infrastructure/fireproof_chemical_vat` | Railway machines; one heavy casing deployment | Copper machines; one ordinary steel casing deployment. Four refractory bricks, prior steel vat, precision mechanism, rubber and pipe remain. |
| `manufacturing/industrial_iron/{press,deployer,mixer,saw,fan,roller}` | Weathered construction; advanced control + calculation processor; one HDPE sheet | Same construction/electronics plus one `nuclearcraft:titanium_ingot`, one `nuclearcraft:tungsten_ingot`, one `industrial_colonies:high_purity_silicon` each. Only the one HDPE insulation is substituted with one `tfmg:plastic_sheet`. |

Two new managed recipes:

- `material_bootstrap/metallurgic_infuser`: restores the exact installed native ingredient counts and crafting arrangement: four iron ingots, two furnaces, two redstone and one osmium. Its producer cannot require the basic circuit it manufactures. Native source: `data/mekanism/recipe/metallurgic_infuser.json`.
- `material_bootstrap/rotary_condensentrator`: Weathered sequence on a steel frame, installing separate TFMG fluid/vat and Mek basic chemical reservoirs, pump, motor, transformer, basic and advanced control circuits, capacitor and plastic. It deliberately does not depend on the missing user Energy Tablet, HDPE, or Industrial machines. Removes the native recipe while adding one explicit managed producer.

Only the Infuser and Rotary are removed from `user_owned_outputs`. At initial completion, the other 812 existing recipes and all other seed root fields were exactly equal to the baseline. Existing factory, advanced storage, PRC, enrichment, enrichment-derived HDPE, Nuclear and space machinery were not downgraded. A subsequent validation correction moves only `mekanism_components/basic_chemical_tank`'s display/dependency phase to `Mekanized Industry`, consistent with its Weathered construction and the Rotary's phase; retaining `High-Energy Grid` falsely made the earlier Rotary depend on a later phase. Root separately removed the old Refined Radiance recipe after this audit's initial snapshot.

## Why these are necessary

1. A Tungsten gate on Industrial machines would otherwise require Tungsten -> Hydrogen -> Electrolytic Separator -> Industrial machines. The separator's core and gas reservoirs must move with it.
2. Titanium's magnesium/chlorine reduction and Tungsten's caustic route also need reachable brine and gas/fluid conversion. The Rotary had no active managed/default producer. It is now a real physical machine recipe, not a material bypass.
3. The prior Industrial HDPE input required Industrial-built enrichment/pressurized reaction equipment. Substituting only the construction insulation avoids moving the entire advanced processing line earlier.
4. The new mandatory electrical Aluminum route would otherwise require Aluminum -> capacitor -> circuit board -> Weathered/Railway machines -> heavy plate/casing -> electrode holder/fireproof vat -> Aluminum. The two Copper-built ordinary-steel equipment corrections remove that hardware cycle while retaining powered electrodes and heat.
5. The chemistry module must also supply its agreed pre-electronics powered-vat caustic bootstrap. Merely correcting equipment recipes does not make a Mek-only initial caustic route reachable. This chemical route is owned by the chemistry agent, not this seed patch. Existing native TFMG sulfur/nitrate/water acid is preserved for early etched boards/semiconductors.
6. Osmium is intentionally retained in the first Infuser, core and basic chemical tank. Root confirmed the independent crude Ultramafic Millstone route (20% successful recovery, then 70% Osmium category) and finite nugget melting/casting are available before wet PGM chemistry. This is the intended low-yield bootstrap, not an invented alternative host or a chemistry dependency.

## Arc furnace and electronics boundaries

The installed `data/immersiveengineering/structure/multiblocks/arcfurnace.nbt` has 77 non-air parts: 8 steel sheetmetal, 6 steel blocks, 5 heavy engineering, 1 redstone engineering, 10 light engineering, 27 reinforced blastbricks, 14 steel-sheetmetal slabs, 5 steel scaffolds and 1 cauldron. Native engineering/reinforced-brick recipes use ordinary steel/iron/copper/electrum/refractory materials, not Titanium or Tungsten. No furnace construction rewrite is needed.

Native IE electrode evidence: `recipe/bottling/graphite_electrode.json` consumes four hop-graphite dust and 1000 mB creosote with a returned rod mold. `recipe/squeezer/graphite_dust.json` supplies hop graphite from eight coke dust. Root intentionally retains this electrode bootstrap and adds a real purified-natural-graphite feed; high-purity Silicon/Graphite must not become the only electrode feed for their own arc-furnace producer.

The existing advanced-control and calculation-processor recipes are Brass-built and are retained in all six Industrial machines. The new explicit high-purity Silicon deployment makes the specified material gate physical without rewriting every existing electronic component. Root's `tools/material_processing/capstone.py` registers that exact item. Root/chemistry own the actual high-purity Silicon, Magnesium/Titanium, Hydrogen/Tungsten, and final alloy recipes.

## Verification and reproducibility

`tools/upgrade_material_machine_tiers.py` defaults to read-only validation/planning; `--apply` performs the deterministic bounded seed transformation and writes a non-overwritten baseline backup. Checks passed:

- Exact transformation of the saved baseline to the modified seed.
- 16 modified existing recipes, 2 additions, 812 unrelated recipes preserved.
- All six machines contain exactly one each of Ti, W and high-purity Silicon; advanced circuit and calculation processor remain.
- No new Industrial dependency in the selected bootstrap machines; Copper electrical-vat hardware no longer consumes a heavy casing.
- Second invocation is idempotent: zero further changes.
- All 18 selected recipes compile successfully through the actual managed recipe compiler's shaped/process/sequenced serializers.

Whole-seed compilation separately exposed an inherited issue: `industrial_colonies:nuclear/refined_radiance` has `exclusive_output=true` but no source removals. That unchanged baseline recipe causes the existing compiler to fail before completing all cards. Root was notified; this task did not silently change its Nuclear/capstone scope. No managed KJSGen output was exported by this task and no live/runtime pass is claimed.

The compatibility test preparator was also updated to derive its default candidate filename from the current `gradle.properties` version (now 0.5.0), while retaining explicit `-CandidateJar` support. It does not launch Gradle/Minecraft or modify a live pack.

## Follow-on: actual pre-board vat mixer cycle (2026-09-09)

The staged default card `industrial_colonies:heavy_industry/industrial_mixer` claimed to precede circuit boards, but consumed heavy plates, steel mechanisms and three heavy machinery casings. Those depend on Weathered/Railway equipment whose electronics need the vat's semiconductor/silicon/acid operations. The native alternative, `tfmg:crafting/materials/industrial_mixer`, also uses steel mechanisms and a heavy casing, so it does not break the cycle. The installed TFMG vat integration supplies the `tfmg:mixing` operation through its Industrial Mixer, not an ordinary Create basin mixer.

The explicitly approved correction reuses that existing card ID and UUID `2adabefb-d5a0-5b94-a12c-ea08f0615d58`. Its ordinary 3×3 mechanical-crafting pattern is `KSK / FCF / KGK`: four screws, one shaft, two steel frames, one ordinary steel casing and one large steel cogwheel. It requires physical early steel hardware without any circuit board, steel mechanism, heavy plate or heavy casing. It does not remove heating, electrical or chemical requirements from vat recipes. The exact native mixer recipe is retired; only this output's former exclusion and native-recipe preservation markers transfer to managed ownership. All 829 preceding seed recipes are unchanged by this follow-on.

`COPPER` selection now includes this early-base mixer, bringing the bounded runtime patch to 19 cards. The seed is 830 recipes, SHA256 `4AB5A0CDA4C5718FD208DD13CF8D90095F11F721599FA058795A83EF38481793`; exact preceding bytes are preserved in `backups/material-processing-20260909/machine-tiers-mixer.seed.before.json`. The updater reproduces the current seed exactly from that backup and is idempotent. Normal manifest assembly, card generation and schema/dependency validation pass: 664 cards, 1058 exact removals, zero warnings. These scratch outputs are under `build/material-processing`; no live export or Minecraft launch was performed by this task.

### First-cast check

Installed Modern Foundry 4.1.6 explicitly includes `modernfoundry:seared_brick` and `modernfoundry:scorched_brick` in `data/c/tags/item/ingots.json`. Therefore its gold ingot-cast recipe and sand ingot molding accept a non-metal brick pattern; they do not require an already cast metal ingot. One sand crafts four blank sand casts, and `smeltery/casts/sand/molding/ingots` makes a single-use ingot cast directly. This avoids the otherwise Copper-gated part builder. Alternatively a brick pattern plus molten gold makes the reusable ingot cast used by owned casting recipes.

An in-memory run of the actual material policy preserves those three native cast recipes and both Copper/Zinc single-use ingot casting recipes. The gold mold cost normalizes to 1000 mB gold; Copper/Zinc casts consume 1000 mB per ingot. No Brass alloying or electronics is needed to create the cast itself. This is a recipe/source check, not a completed survival playthrough or runtime machine test.

### Selected Industrial roller and repeatable batch assembly

The normal assembler applies the older reviewed-default restoration policy, which retires all roller cards, including `manufacturing/industrial_iron/roller`. Therefore the initial 664-card compile did not contain that selected card even though its updated seed recipe was correct. The new material-processing approval explicitly includes its Ti/W/Silicon gate. `--restore-batch-roller` now restores only that one seed recipe into this batch's scratch manifest and removes only `createcasing:crafting/roller/industrial_iron` from the scratch preservation list. The historical restoration policy, other rollers, old reviewed cards and prior evidence remain unchanged. Its original deterministic UID is `a27afc5f-89f6-59c5-b35d-4848f5b77021`.

Repeatable order: normal `build_managed_recipe_manifest.py` to `build/material-processing`, then `upgrade_material_machine_tiers.py --restore-batch-roller`, then the normal generator and validator against that scratch manifest. Final result: **665 cards, 1059 removals, all 19 selected cards present, zero validation warnings**. The runtime stage patch must include both exact native removals for the TFMG mixer and Industrial roller.

### Heat-source finding handed to the physical-recipe owner

Worldgen traces place configured Hematite/Chalcopyrite rock blocks, not loose Iron nuggets (`GeologyFeature.traces` and geology `settings.json`). At this audit snapshot, their owned direct melts and raw Iron/Copper/Zinc inherited 1000°C, so the native 800°C loose-nugget recipe does not prove a guaranteed first-Iron/lava-bucket route. The parent was notified to apply the smallest native-temperature-only correction in its physical-recipe scope; this audit did not alter those independently owned recipes or claim the issue already runtime-verified. All fixed mB values should remain unchanged.
