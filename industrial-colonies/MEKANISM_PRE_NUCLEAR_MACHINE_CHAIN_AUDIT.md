# Mekanism Pre-Nuclear Machine Chain — Source-Owned Redesign Audit

Status: **implemented in the authoritative recipe seed**  
Decision: **GO — replace the eight generic automatic 5×5 owners with eight exact TFMG-first encased manufacturing contracts.**

The reviewed batch edits only:

- `progression/managed_recipe_overhaul.seed.json`

It does not edit:

- `progression/machine_node_assignments.json`
- authoritative generated manifests or KJSGen output
- quests
- deploy or live-pack output
- the immutable Draw.io source

The deterministic builder now validates exact source ownership and emits an implemented no-op report. It has no apply mode.

## 1. Installed evidence

Audited JAR:

- `Mekanism-1.21.1-10.7.19.85.jar`
- SHA-256: `004DBC9F3106F4D192AEAA1EE1190DD16EC9CA8059ED3D093B80034F4C574F43`

Catalog:

- `outputs/recipe-catalog-current/recipe_catalog.sqlite`
- SHA-256: `21C274B8C8A02BC2BDF32A4F2A3BE1720894B8A59D8283773474A424133C1574`

Every target has exactly one static installed producer. The full cross-JAR audit found no alternate recipe, chest loot, trade, or advancement reward for any target. Their block loot tables only return an already-placed machine and therefore are not acquisition routes.

| Output / exact recipe ID | Source type | Exact source pattern | Installed JSON SHA-256 |
|---|---|---|---|
| `mekanism:chemical_infuser` | `mekanism:mek_data` | `ACA / TXT / ACA` | `4D71AE990BFB53EF0F362D47AF7E3FF48B16BC0B9DA5C4F057533BCC7C5C4511` |
| `mekanism:chemical_oxidizer` | `mekanism:mek_data` | `ACA / P#T / ACA` | `748B9C5553922757B37B23D81B7F0E75A83C0464D7106150EFD0DDEC51384825` |
| `mekanism:crusher` | `minecraft:crafting_shaped` | `RCR / BXB / RCR` | `6C354FF9AD75438F5F5CF6CB71F0F1BA450CFC08D489B2A71A4E184BAA4A1909` |
| `mekanism:electrolytic_separator` | `minecraft:crafting_shaped` | `IRI / A#A / IRI` | `DFDD37DEB19EADFAFFABC78D670BAF6B78EC1B4D444AEF34B37366EB1961D0EE` |
| `mekanism:enrichment_chamber` | `minecraft:crafting_shaped` | `ACA / IXI / ACA` | `2DDE7A2B2342D6B0A85B528059BCFC2B8B77DAFF40C6A418E0BBDF0EC0DA2639` |
| `mekanism:osmium_compressor` | `minecraft:crafting_shaped` | `ACA / BXB / ACA` | `3E106E844B502177494713F0AA285CCC17241A85376E992995A2CD384AA273A6` |
| `mekanism:precision_sawmill` | `minecraft:crafting_shaped` | `ICI / AXA / ICI` | `D625421942B0BA33A2DC577BE8CF60ADDFB96521AB0214E2C301747C5670B83E` |
| `mekanism:pressurized_reaction_chamber` | `mekanism:mek_data` | `SAS / CPC / T#T` | `12049D9BB91BA42A107DA42B3C35B8ED6006C9F7F76ADAD2C9FA7ECED49C690A` |

All eight source paths are `data/mekanism/recipe/<recipe-id-path>.json`.

### Exact stock ingredients

- `chemical_infuser`: four `#mekanism:alloys/infused`, two `#c:circuits/basic`, two `mekanism:basic_chemical_tank`, one `mekanism:steel_casing`.
- `chemical_oxidizer`: four `#mekanism:alloys/infused`, two `#c:circuits/basic`, one `#mekanism:personal_storage`, one `mekanism:dynamic_tank`, one `mekanism:basic_chemical_tank`.
- `crusher`: four `#c:dusts/redstone`, two `#c:circuits/basic`, two `#c:buckets/lava`, one `mekanism:steel_casing`.
- `electrolytic_separator`: four `#c:ingots/iron`, two `#c:dusts/redstone`, two `#mekanism:alloys/infused`, one `mekanism:electrolytic_core`.
- `enrichment_chamber`: four `#mekanism:alloys/basic`, two `#c:circuits/basic`, two `#c:ingots/iron`, one `mekanism:steel_casing`.
- `osmium_compressor`: four `#mekanism:alloys/infused`, two `#c:circuits/advanced`, two `minecraft:bucket`, one `mekanism:steel_casing`.
- `precision_sawmill`: four `#c:ingots/iron`, two `#c:circuits/basic`, two `#mekanism:alloys/infused`, one `mekanism:steel_casing`.
- `pressurized_reaction_chamber`: two `#c:ingots/steel`, one `#mekanism:alloys/infused`, two `#c:circuits/basic`, one `mekanism:enrichment_chamber`, two `mekanism:basic_chemical_tank`, one `mekanism:dynamic_tank`.

The broad stock `#c:ingots/steel` tag accepts steel from several mods. The replacements avoid that canonicalization escape by using concrete TFMG pressure components and the managed Mekanism casing.

## 2. Important `mek_data` behavior

The stock infuser, oxidizer, and PRC recipes use Mekanism's `mekanism:mek_data` serializer. It can merge compatible security, energy, fluid, chemical, item, lock, sorting, upgrade, and QIO-drive data from ingredients into the output. Create compacting has no equivalent state-merging serializer.

The reviewed contract is therefore explicit:

- all eight encased recipes create a **fresh, empty** machine;
- basic chemical tanks used by the infuser or PRC must be fresh and empty;
- the enrichment chamber consumed by the first PRC must be fresh, empty, unsecured, and unupgraded;
- this is a new-machine construction route, not a state-preserving upgrade route.

This avoids promising state transfer that KJSGen/Create cannot provide. It also avoids silently destroying a player's configured production machine when the PRC is constructed as intended from a newly manufactured enrichment chamber.

## 3. Manufacturing environment decision

The physical tier authority ranks Copper 1, Brass 2, Railway 3, and Industrial Iron 4.

| Environment | Count | Role in this batch |
|---|---:|---|
| `createcasing:railway_press` | 6 | Heavy frames, compression bodies, chemical manifolds, and pressure chambers |
| `createcasing:copper_press` | 1 | Electrode alignment and power-stack assembly for electrolysis |
| `createcasing:brass_press` | 1 | Alignment of the precision saw and fine drive components |

The default Create press and Industrial Iron, Weathered Iron, and Refined Radiance presses are forbidden by the contract. Difficulty comes from meaningful parts and routing, not a generic perimeter of phase-gate ingredients.

## 4. Exact replacement contracts

All outputs are one item, all are exclusive, and every listed stock ID is removed exactly.

### 4.1 Enrichment Chamber

- Managed ID: `industrial_colonies:mekanism_pre_nuclear/enrichment_chamber`
- Assignment: `CR01 — Modular Machinery`
- Phase/order: `Mekanized Industry`, `300`
- Machine: `createcasing:railway_press`
- Inputs:
  - `mekanism:steel_casing`
  - `mekanism:basic_control_circuit`
  - `tfmg:circuit_board`
  - `create:precision_mechanism`
  - `tfmg:steel_mechanism`
  - `2x mekanism:alloy_infused`
  - `2x tfmg:heavy_plate`
- Output: `mekanism:enrichment_chamber`
- Exact removal: `mekanism:enrichment_chamber`

This is the first controlled granular-processing machine and the sole same-batch predecessor of the PRC.

### 4.2 Osmium Compressor

- Managed ID: `industrial_colonies:mekanism_pre_nuclear/osmium_compressor`
- Assignment: `CR01 — Modular Machinery`
- Phase/order: `Mekanized Industry`, `310`
- Machine: `createcasing:railway_press`
- Inputs:
  - `mekanism:steel_casing`
  - `tfmg:steel_chemical_vat`
  - `create:mechanical_pump`
  - `tfmg:transformer`
  - `mekanism:basic_control_circuit`
  - `tfmg:circuit_board`
  - `2x tfmg:heavy_plate`
  - `2x tfmg:steel_pipe`
- Output/removal: `mekanism:osmium_compressor`

This replaces the two stock buckets and generic advanced-circuit ring with an actual pumped pressure body and power hardware.

### 4.3 Crusher

- Managed ID: `industrial_colonies:mekanism_pre_nuclear/crusher`
- Assignment: `CR01 — Reinforced Systems`
- Phase/order: `Mekanized Industry`, `320`
- Machine: `createcasing:railway_press`
- Inputs:
  - `mekanism:steel_casing`
  - `2x create:crushing_wheel`
  - `tfmg:steel_mechanism`
  - `mekanism:basic_control_circuit`
  - `tfmg:circuit_board`
  - `2x tfmg:heavy_plate`
  - `2x mekanism:alloy_infused`
- Output/removal: `mekanism:crusher`

The recipe visibly contains the machine's actual crushing pair instead of two lava buckets.

### 4.4 Precision Sawmill

- Managed ID: `industrial_colonies:mekanism_pre_nuclear/precision_sawmill`
- Assignment: `CR01 — Reinforced Systems`
- Phase/order: `Mekanized Industry`, `330`
- Machine: `createcasing:brass_press`
- Inputs:
  - `mekanism:steel_casing`
  - `create:mechanical_saw`
  - `create:precision_mechanism`
  - `tfmg:steel_mechanism`
  - `mekanism:basic_control_circuit`
  - `tfmg:circuit_board`
  - `2x tfmg:heavy_plate`
  - `mekanism:alloy_infused`
- Output/removal: `mekanism:precision_sawmill`

Brass owns this recipe because blade and precision-drive alignment is fine manufacturing, not pressure-vessel forming.

### 4.5 Electrolytic Separator

- Managed ID: `industrial_colonies:mekanism_pre_nuclear/electrolytic_separator`
- Assignment: `CR01 — Electrochemical Engineering`
- Phase/order: `Mekanized Industry`, `340`
- Machine: `createcasing:copper_press`
- Inputs:
  - `mekanism:steel_casing`
  - `mekanism:electrolytic_core`
  - `tfmg:steel_chemical_vat`
  - `tfmg:copper_electrode`
  - `tfmg:zinc_electrode`
  - `create:mechanical_pump`
  - `tfmg:transformer`
  - `mekanism:basic_control_circuit`
  - `tfmg:circuit_board`
- Output/removal: `mekanism:electrolytic_separator`

This is the batch's Copper-line electrical stack and gives both functional TFMG electrodes a concrete role.

### 4.6 Chemical Oxidizer

- Managed ID: `industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer`
- Assignment: `CR01 — Electrochemical Engineering`
- Phase/order: `Mekanized Industry`, `350`
- Machine: `createcasing:railway_press`
- Inputs:
  - `mekanism:steel_casing`
  - `tfmg:steel_chemical_vat`
  - `mekanism:basic_chemical_tank`
  - `create:encased_fan`
  - `create:mechanical_pump`
  - `tfmg:steel_pipe`
  - `tfmg:capacitor_item`
  - `mekanism:basic_control_circuit`
  - `tfmg:circuit_board`
- Output/removal: `mekanism:chemical_oxidizer`

The fan supplies the recognizable gas-flow stage; the TFMG vat, pump, pipe, and capacitor form the process body and local electrical buffer.

### 4.7 Chemical Infuser

- Managed ID: `industrial_colonies:mekanism_pre_nuclear/chemical_infuser`
- Assignment: `CR01 — Electrochemical Engineering`
- Phase/order: `Mekanized Industry`, `360`
- Machine: `createcasing:railway_press`
- Inputs:
  - `mekanism:steel_casing`
  - `2x mekanism:basic_chemical_tank`
  - `tfmg:steel_chemical_vat`
  - `2x create:mechanical_pump`
  - `2x tfmg:steel_pipe`
  - `tfmg:transformer`
  - `mekanism:basic_control_circuit`
  - `tfmg:circuit_board`
- Output/removal: `mekanism:chemical_infuser`

The exact dual-tank, dual-pump, dual-manifold contract expresses a two-feed chemical machine rather than repeating generic alloys around a casing.

### 4.8 Pressurized Reaction Chamber

- Managed ID: `industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber`
- Assignment: `CR01 — Electrochemical Engineering`
- Phase/order: `Mekanized Industry`, `380`
- Machine: `createcasing:railway_press`
- Inputs:
  - `mekanism:enrichment_chamber`
  - `mekanism:steel_casing`
  - `tfmg:steel_chemical_vat`
  - `mekanism:dynamic_tank`
  - `2x mekanism:basic_chemical_tank`
  - `create:mechanical_pump`
  - `2x tfmg:steel_pipe`
  - `tfmg:transformer`
  - `mekanism:basic_control_circuit`
  - `tfmg:circuit_board`
  - `2x tfmg:heavy_plate`
- Output/removal: `mekanism:pressurized_reaction_chamber`
- Same-batch dependency: `industrial_colonies:mekanism_pre_nuclear/enrichment_chamber`

The PRC consumes the reviewed Enrichment output and declares that exact owner as its sole same-batch dependency. It contains no HDPE, substrate, PRC product, sulfuric acid, AE2 processor, or nuclear material.

## 5. Exact removal set

Only these eight installed recipe IDs are removed by the contracts:

1. `mekanism:chemical_infuser`
2. `mekanism:chemical_oxidizer`
3. `mekanism:crusher`
4. `mekanism:electrolytic_separator`
5. `mekanism:enrichment_chamber`
6. `mekanism:osmium_compressor`
7. `mekanism:precision_sawmill`
8. `mekanism:pressurized_reaction_chamber`

There are no additional removals and no source-recipe override mutations.

## 6. Assignment result

No assignment edit is proposed. Current relative assignment order is already correct:

- `CR01 — Modular Machinery`: Enrichment Chamber before Osmium Compressor.
- `CR01 — Reinforced Systems`: Crusher before Precision Sawmill.
- `CR01 — Electrochemical Engineering`: Electrolytic Separator, Chemical Oxidizer, Chemical Infuser, then Pressurized Reaction Chamber.

The deterministic builder rejects missing, duplicated, moved, or reversed members of these sequences. In addition, the physical recipe DAG enforces Enrichment before PRC even if quest/research gating is disabled.

## 7. Sulfuric-acid boundary

This batch does not add a chemical-processing recipe. Neither `tfmg:sulfuric_acid` nor `mekanism:sulfuric_acid` appears as an input or output. Sulfuric-acid synthesis remains owned by the TFMG Chemical Vat, with the existing compatibility bridge remaining a phase conversion rather than a second synthesis route.

## 8. Implemented integration contract

Integration was applied deterministically against seed SHA-256 `297CE846E57E8764A32642B3A3846893533477D289556B1297A1A98DABB07106` and unchanged assignment SHA-256 `329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E`:

1. Append the eight contracts in `seed_patch_contract.append_recipe_ids` order.
2. Do not edit `source_recipe_overrides`.
3. Do not add global removals; each recipe owns its one exact stock removal.
4. Do not change `machine_node_assignments.json`.
5. Regenerate authoritative manifests/KJSGen only in the parent integration workflow.

The eight explicit output owners suppress the corresponding automatic owners during manifest construction.

## 9. Validation

Commands:

```text
python tools/validate_mekanism_pre_nuclear_machine_chain_audit.py
python -m unittest tools.test_validate_mekanism_pre_nuclear_machine_chain_audit
python tools/build_mekanism_pre_nuclear_patch_plan.py
```

Green proof:

- eight installed source JSON files and hashes verified;
- eight catalog outputs each have exactly one static installed producer;
- eight automatic generic owners identified and retired in the in-memory build;
- eight replacement recipe cards compile as `kjsgen:create_compacting`;
- exact machine count: Railway 6, Copper 1, Brass 1;
- exact eight-removal set compiled;
- Enrichment is both a physical input and declared same-batch dependency of PRC;
- no HDPE, substrate, PRC-derived product, sulfuric-acid, AE2, or nuclear bootstrap input;
- all three `mek_data` state-transfer limitations remain explicit;
- no assignment mutation;
- 29 mutation tests pass;
- one shared progression file modified (the authoritative seed); assignments remained byte-identical.
