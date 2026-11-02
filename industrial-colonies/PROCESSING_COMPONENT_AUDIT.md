# Processing-component audit

## Scope and decision rule

This is a read-only design audit of the 44 entries in `progression/managed_recipe_overhaul.report.json` whose report reason is `processing_only` or `no_static_producer`. The audited report SHA-256 is `066E0827F927167246CC13EADE9213F8958BE843F2817B8B8C063680AC397FEE`.

Every producer ID below was checked against `outputs/recipe-catalog-current/item_recipe_map.csv`, `recipes.csv`, and the corresponding JSON inside the installed mod JAR. Current managed recipes, focused KubeJS scripts, canonicalization policies, and validators were also searched. No recipe, deployment, quest, or live-pack source was changed as part of this audit.

The classifications mean:

- **A — intentionally stock processing:** the installed machine/process and its physical inputs already express the intended progression. Replacing it would add duplication rather than close a bypass.
- **B — controlled elsewhere:** the report cannot auto-compile the output, but a focused boundary or an already-assigned implementation owns it.
- **C — explicit overhaul required:** the surviving route is materially earlier or simpler than the output's intended physical tier, or an intended focused replacement is currently absent.
- **D — runtime artifact:** the item is produced by attunement or fluid-container behavior, not a static recipe. It should not be added to the managed recipe manifest merely to silence the report.

| Classification | Count | Action |
|---|---:|---|
| A | 20 | Retain the listed stock processing recipes. |
| B | 9 | Do not duplicate; preserve the named focused owner. |
| C | 5 | Review and implement the exact replacement plan below. |
| D | 10 | Treat as attunement/container artifacts; keep out of recipe generation. |
| **Total** | **44** | Every skipped output is accounted for exactly once. |

The generated recipe-stage manifest is currently in `physical_recipe_progression` mode with no recipe entries. Therefore a category-C component must carry its tier in physical inputs and machine environment; a node assignment alone is not sufficient.

## A — intentionally stock processing

| Output | Exact installed producer recipe ID(s) | Why the stock operation is appropriate |
|---|---|---|
| `create:andesite_casing` | `create:item_application/andesite_casing_from_log`; `create:item_application/andesite_casing_from_wood` | Create's first casing is deliberately one andesite-alloy application to stripped wood. The alloy, not an artificial later component, is the Andesite-age gate. |
| `create:brass_casing` | `create:item_application/brass_casing_from_log`; `create:item_application/brass_casing_from_wood`; `createmetallurgy:casting_in_basin/brass_casing` | Brass acquisition already carries the heated-alloy gate. Both application and molten-brass casting are valid factory routes. |
| `create:precision_mechanism` | `create:sequenced_assembly/precision_mechanism` | The five-loop cogwheel/large-cogwheel/nugget sequence is Create's canonical precision-manufacturing benchmark and already matches the pack's desired moderate repeated assembly. |
| `create:railway_casing` | `create:item_application/railway_casing` | Applying an obsidian plate to a brass casing preserves the Brass-to-rail material dependency without an extra synthetic component. |
| `create:track` | `create:sequenced_assembly/track`; `createmetallurgy:sequenced_assembly/steel_track` | Both routes are genuine deploy/deploy/press rail production. The steel route is an appropriate later material alternative, not an early bypass. |
| `createmetallurgy:graphite_ingot_mold` | `createmetallurgy:graphite_ingot_mold_from_graphite_molds_stonecutting` | This only reshapes an existing graphite mold. It neither creates graphite nor advances metallurgy, so mold selection can remain a geometry operation. |
| `createmetallurgy:graphite_rod_mold` | `createmetallurgy:graphite_rod_mold_from_graphite_molds_stonecutting` | Same mold-family geometry rule as the ingot mold; there is no material multiplication. |
| `createmetallurgy:industrial_crucible` | `createmetallurgy:sequenced_assembly/industrial_crucible` | The installed sequence already requires refractory mortar, obdurium plate, grinding, and molten tungsten. It is more progression-bearing than a replacement 5x5 shell would be. |
| `mekanism:alloy_infused` | `mekanism:metallurgic_infusing/alloy/infused` | Copper plus redstone infusion is the intended entry to Mekanism metallurgy and requires the hardened Metallurgic Infuser. |
| `mekanism:alloy_reinforced` | `mekanism:metallurgic_infusing/alloy/reinforced` | The recipe consumes the preceding infused alloy plus diamond infusion, preserving the alloy ladder. |
| `mekanism:alloy_atomic` | `mekanism:metallurgic_infusing/alloy/atomic` | The recipe consumes reinforced alloy plus refined-obsidian infusion, preserving the final alloy tier. |
| `mekanism:substrate` | `mekanism:reaction/substrate/water_hydrogen`; `mekanism:reaction/substrate/water_ethene` | Both are Pressurized Reaction Chamber chemistry. The second is the intended bulk recycling loop, not a crafting loophole. |
| `mekanism:hdpe_pellet` | `mekanism:reaction/substrate/ethene_oxygen` | It requires substrate, ethene, oxygen, energy, and the hardened reaction chamber; this is already the correct chemical-factory gate. |
| `mekanism:hdpe_sheet` | `mekanism:enriching/hdpe_sheet` | Three HDPE pellets through the hardened Enrichment Chamber is a sensible final forming step. |
| `mekanism:reprocessed_fissile_fragment` | `mekanism:processing/uranium/reprocessing/from_plutonium` | Hydrogen-chloride injection into a plutonium pellet is already a late nuclear reprocessing operation. |
| `tfmg:copper_electrode` | `tfmg:copper_electrode_from_storage_blocks_copper_stonecutting` | The focused electronics policy explicitly retains this recipe. Consuming a full copper block for one electrode is not a cheap material conversion, and the output is a TFMG-first consumable. |
| `tfmg:zinc_electrode` | `tfmg:zinc_electrode_from_storage_blocks_zinc_stonecutting` | Same retained electronics policy and full-block material cost as the copper electrode. |
| `tfmg:rubber_sheet` | `tfmg:vat_machine_recipe/rubber` | This is exactly the desired TFMG chemical environment: heated steel/firebrick VAT mixing sulfur dust with 250 mB heavy oil. |
| `tfmg:steel_casing` | `tfmg:item_application/steel_casing`; incidental sequenced-assembly result entries `tfmg:sequenced_assembly/generator`, `tfmg:sequenced_assembly/motor`, and `tfmg:sequenced_assembly/potentiometer` | The primary route applies canonical TFMG steel to hardened planks. Steel production is the physical age gate; the other catalog rows are sequence result/fallback entries, not independent cheap casing crafts. |
| `tfmg:steel_mechanism` | `tfmg:sequenced_assembly/steel_mechanism` | The installed two-loop sequence uses heavy plate, steel gearing, nickel sheet, lead sheet, screws, and a screwdriver. It is already a substantial TFMG-first manufactured component. |

## B — already controlled elsewhere

### Uranium physical and chemical boundary

These seven outputs remain stock Mekanism machine products, but they are not uncontrolled. `industrial_uranium_yellorium_separation.js` removes furnace, Create-washing/compacting, Modern Foundry, and uranium-tag shortcuts; rebuilds the only Yellorium-to-raw-uranium bridge; and isolates the common uranium tags. `validate_nuclear_chemistry_boundaries.py` then verifies the retained Mekanism chain. Replacing these machine transformations in the managed crafting manifest would split ownership and risk reopening the already-audited boundary.

| Output | Exact installed producer recipe ID(s) | Focused handling |
|---|---|---|
| `mekanism:clump_uranium` | `mekanism:processing/uranium/clump/from_ore`; `mekanism:processing/uranium/clump/from_raw_block`; `mekanism:processing/uranium/clump/from_raw_ore`; `mekanism:processing/uranium/clump/from_shard` | Retained Purification Chamber paths inside the canonical uranium family. |
| `mekanism:crystal_uranium` | `mekanism:processing/uranium/crystal/from_slurry` | Retained Chemical Crystallizer step after slurry washing. |
| `mekanism:deepslate_uranium_ore` | `mekanism:processing/uranium/ore/deepslate_from_raw` | Retained Combiner reconstruction; it does not create raw uranium. |
| `mekanism:dirty_dust_uranium` | `mekanism:processing/uranium/dirty_dust/from_clump` | Retained Crusher step inside the physical enrichment chain. |
| `mekanism:dust_uranium` | `mekanism:processing/uranium/dust/from_dirty_dust`; `mekanism:processing/uranium/dust/from_ingot`; `mekanism:processing/uranium/dust/from_ore`; `mekanism:processing/uranium/dust/from_raw_block`; `mekanism:processing/uranium/dust/from_raw_ore` | The focused script explicitly removes `mekanism:processing/uranium/dust/from_ingot`; the other Enrichment Chamber paths remain the deliberate physical feedstock route. |
| `mekanism:shard_uranium` | `mekanism:processing/uranium/shard/from_crystal`; `mekanism:processing/uranium/shard/from_ore`; `mekanism:processing/uranium/shard/from_raw_block`; `mekanism:processing/uranium/shard/from_raw_ore` | Retained Chemical Injection Chamber paths; tag cleanup prevents foreign uranium substitutions. |
| `mekanism:uranium_ore` | `mekanism:processing/uranium/ore/from_raw` | Retained Combiner reconstruction from canonical raw uranium. |

### Petroleum batch ownership

The two following rows were still listed as skipped in the audited report, but their overhaul is explicitly assigned to the petroleum/pumpjack construction batch. That batch must remove the two exact stonecutting recipes and supply the reviewed pumpjack-assembly replacements. They must not receive a second implementation from this audit.

| Output | Exact stock recipe to retire | Owner |
|---|---|---|
| `tfmg:pumpjack_hammer_part` | `tfmg:pumpjack_hammer_part_from_storage_blocks_steel_stonecutting` | Petroleum/pumpjack construction batch. |
| `tfmg:large_pumpjack_hammer_part` | `tfmg:large_pumpjack_hammer_part_from_storage_blocks_steel_stonecutting` | Petroleum/pumpjack construction batch. |

## C — explicit overhaul required

These are the only five gaps found. The companion `PROCESSING_COMPONENT_AUDIT.plan.json` records the same exact removal and replacement intent in machine-readable form.

### 1. TFMG empty spool

Current producer: `tfmg:empty_spool_from_hardened_planks_stonecutting`.

This is a confirmed migration hole. `canonicalization_policies.json` and `validate_tfmg_electronics_progression.py` both expect the stock stonecutting recipe to be removed and replaced by `industrial_colonies:electronics_manufacturing/empty_spool`, but the current assembled manifest and compiled KJSGen project contain neither the removal nor the replacement. The migration-marker `industrial_electronics_progression.js` intentionally emits no recipe, so the one-step Stonecutter path survives.

Recommended replacement:

- Remove only `tfmg:empty_spool_from_hardened_planks_stonecutting`.
- Add `industrial_colonies:electronics_manufacturing/empty_spool` as Create cutting from `tfmg:hardened_planks` to one `tfmg:empty_spool`.
- Bind the operation to `createcasing:copper_mechanical_saw`, the installed Copper electronics-line cutter. This restores the already-documented TFMG-first design without inventing another intermediate.

### 2. MEGA Cells accumulation processor

Current producers: `megacells:inscriber/accumulation_processor` and `extendedae:assembler/accumulation_processor`.

The normal AE2 logic/calculation/engineering processors have authored TFMG-board manufacturing, but this later processor still uses the stock printed-circuit + printed-silicon + fluix recipe. The Crystal Assembler path then bulk-crafts four with the same three inputs. This is the one processor-family hole that bypasses the pack's physical electronics language.

Recommended replacement:

- Remove both exact producer IDs.
- Add `industrial_colonies:digital/accumulation_processor` as a two-loop Sequenced Assembly beginning with `megacells:printed_accumulation_processor` as the transitional workpiece.
- Each loop should use a `createcasing:copper_deployer` for `tfmg:coated_circuit_board`, `ae2:printed_silicon`, and `tfmg:capacitor_item`, then a `createcasing:brass_press` precision step. Fluix dust may be retained as one additional deployment if material parity with Mega Cells is desired.
- Preserve the intended late-game acceleration by re-adding a Crystal Assembler bulk route only after the assembler's own hardened recipe. A sensible four-unit batch is four printed accumulation circuits, four printed silicon, four fluix dust, and four TFMG coated circuit boards to four processors. This keeps acceleration without restoring the board-free shortcut.

The accumulation press and printed-accumulation recipes are not part of the 44 skipped outputs. They can remain the specialized Mega Cells precursor path unless a later processor-press audit deliberately expands scope.

### 3. Electroenergetics transformer-core lamination

Current producer: `electroenergetics:stonecutting/transformer_core_lamination`.

One generic iron plate currently becomes a High-Energy-Grid transformer lamination in a Stonecutter. With recipe stages disabled, this is physically an Iron-age component despite its high-voltage assignment.

Recommended replacement:

- Remove only `electroenergetics:stonecutting/transformer_core_lamination`.
- Add `industrial_colonies:high_voltage/transformer_core_lamination` as Create pressing of `#c:plates/steel`, bound to `createcasing:industrial_iron_press`.
- An output of two laminations per steel plate is reasonable: the progression cost is the steel/heavy press environment, not deliberate material waste.

### 4. Electroenergetics transformer core

Current producer: `electroenergetics:sequenced_assembly/transformer_core`.

The stock sequence is mechanically attractive, but its complete bill of materials is only iron-plate laminations and copper-wire spools. It can therefore be manufactured several physical tiers before High-Voltage Systems.

Recommended replacement:

- Remove only `electroenergetics:sequenced_assembly/transformer_core`.
- Retain Sequenced Assembly and the installed `electroenergetics:incomplete_transformer_core` transitional item.
- Use industrial-iron deployment/pressing for three steel laminations, a Copper Deployer for `electroenergetics:copper_wire_spool`, and precision deployment of `tfmg:transformer` plus `mekanism:alloy_reinforced` before the final `createcasing:industrial_iron_press` step.
- Keep the sequence to one moderate pass; the component count already supplies the manufacturing depth.

### 5. Electroenergetics miniature circuit breaker

Current producer: `electroenergetics:sequenced_assembly/miniature_circuit_breaker`.

The stock sequence uses a Precision Mechanism and basic copper parts, so the functional high-voltage breaker is reachable from Brass-age materials. Unlike a passive mold, this directly exposes a late-grid utility block.

Recommended replacement:

- Remove only `electroenergetics:sequenced_assembly/miniature_circuit_breaker`.
- Retain Sequenced Assembly and `electroenergetics:incomplete_miniature_circuit_breaker`.
- Start from `tfmg:coated_circuit_board`; deploy `create:precision_mechanism`, `tfmg:capacitor_item`, `tfmg:transistor_item`, `electroenergetics:copper_wire_spool`, and `mekanism:alloy_reinforced` with Copper/Industrial-Iron Deployers; finish in `createcasing:industrial_iron_press`.
- One pass is enough. The goal is to require the electronics and reinforced-grid factories, not inflate operation count.

## D — non-craftable fluid or attunement artifacts

The static catalog has no producer rows for any item below. That absence matches the installed runtime design, so these should stay skipped.

| Output | Runtime acquisition semantics |
|---|---|
| `ae2:fe_p2p_tunnel` | Attuned form of an AE2 ME P2P tunnel, not a crafted block. |
| `ae2:fluid_p2p_tunnel` | Attuned form of an AE2 ME P2P tunnel. |
| `ae2:item_p2p_tunnel` | Attuned form of an AE2 ME P2P tunnel. |
| `appmek:chemical_p2p_tunnel` | Applied Mekanistics chemical attunement form. |
| `bigreactors:blutonium_bucket` | Registered bucket/container for the Blutonium fluid. |
| `bigreactors:cyanite_bucket` | Registered bucket/container for the Cyanite fluid. |
| `bigreactors:magentite_bucket` | Registered bucket/container for the Magentite fluid. |
| `mekanism:uranium_hexafluoride_bucket` | Container representation of the uranium-hexafluoride chemical/fluid; the chemical chain, not a bucket craft, owns production. |
| `mekanism:uranium_oxide_bucket` | Container representation of uranium oxide; the Chemical Oxidizer route owns production. |
| `tfmg:diesel_bucket` | Standard container for canonical TFMG diesel. Petroleum processing owns the fluid; filling a bucket must not become a second fuel recipe. |

## Implementation order for category C

1. Restore the already-intended empty-spool cutting recipe first; it is an objective missing migration, not a balance redesign.
2. Close the accumulation-processor family hole while preserving the hardened Crystal Assembler as the later throughput reward.
3. Replace the lamination, transformer-core, and breaker routes together. Deploying only one of those three would leave the high-voltage component chain internally inconsistent.
4. After implementation, require exact-removal validation for all five stock IDs plus the second accumulation-processor producer, verify that each replacement appears in KubeJS Gen, and rerun the full managed DAG/bootstrap check.

No category-A or category-D recipe should be removed merely to reduce the skipped count. A nonzero skipped count is correct when it documents runtime artifacts and intentionally retained processing recipes.
