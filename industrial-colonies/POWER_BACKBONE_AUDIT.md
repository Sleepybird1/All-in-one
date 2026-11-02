# Power generation, storage, and transmission audit

> **Implementation update — 2026-08-31:** The recommended 15-recipe Power Backbone Recovery batch, the Create Steam gate, seven-recipe analog High-Voltage repair, eight-recipe Extreme Transmission branch, four Energy Cube replacements, and complete ten-part Induction Matrix family now live in the authoritative seed. See the focused progression/audit documents for source contracts and isolated validation results. Shared generated and live artifacts remain intentionally unchanged pending coordinated integration.

## Outcome

The next implementation should be a **Power Backbone Recovery** batch, not a new speculative power tier. Fifteen reviewed TFMG/EE/CreateAddition compatibility recipes are still named in `canonicalization_policies.json`, `machine_recipe_dependencies.json`, and `ELECTRICAL_INFRASTRUCTURE_AUDIT.md`, but none of those exact managed recipe IDs exists in the current seed-derived manifest. The two legacy scripts that once emitted them are now migration markers, so generic auto recipes or stock recipes took their place.

The bounded recovery batch is:

- 15 source-owned recipes from Early Electricity through Grid Engineering;
- five exact Create Crafts & Additions duplicate retirements;
- no broad output or namespace removals;
- no AE2 or Mekanism prerequisite inserted before the grid; and
- preservation of the three safe Electro Energetics connector-reclamation recipes.

This is higher-value and lower-risk than immediately redesigning high voltage or induction storage because the intended definitions already existed, were previously validated, and are still referenced by project policy.

The companion `POWER_BACKBONE_AUDIT.plan.json` contains the exact recipe IDs, patterns, item counts, removals, order, and deferred batches. This audit did not modify the seed, generated KJSGen project, deployment code, quests, live pack, or Minecraft.

## Audited snapshot

| Source | SHA-256 |
|---|---|
| `progression/managed_recipe_overhaul.seed.json` | `023B573D264A2A91E775A3673505B735B9BCA4A42C2D687D7A93E6360D7CE5CE` |
| `progression/managed_recipe_overhaul.json` | `2346B2EDC8DEDC0507183716040A4CF1FC8049D59C9A6922DF89DB91B1CE91C8` |
| `progression/managed_recipe_overhaul.report.json` | `066E0827F927167246CC13EADE9213F8958BE843F2817B8B8C063680AC397FEE` |
| catalog `items.csv` | `2AC81008AA7832FAE99AFE48A2940B3021A893E8A75F08024E60956D23E14715` |
| catalog `recipes.csv` | `3F2B7E1D60E2578AA0B52A2B3825195766C3D0C099EE3EAC83EF3A6FA3BCA733` |

Installed power-system evidence:

| System | Installed JAR | Audit disposition |
|---|---|---|
| Create | `create-1.21.1-6.0.10.jar` | Water wheels/wind remain early rotational foundations; Steam Engine hardening is a follow-up. |
| TFMG | `tfmg-1.2.0.jar` | Canonical early generation, motors, local cabling, and chemical storage. Immediate recovery scope. |
| Electro Energetics | `electroenergetics-1.21.1-1.1.1.jar` | Canonical long-span grid. Immediate recovery scope through first-grid equipment. |
| Create Crafts & Additions | `createaddition-1.6.0.jar` | Retain specialized utilities; retire the five duplicate fixed-power machines/endpoints. |
| Mekanism | `Mekanism-1.21.1-10.7.19.85.jar` | Cube ladder and induction family need separate coherent batches. |
| Immersive Engineering | **not installed** | Do not invent IE registry or recipe IDs. `ImmersiveUI-NEOFORGE-0.3.3+1.21.1.jar` is unrelated. |

The item and recipe namespaces were checked against the current catalog and the corresponding installed JAR source paths. There is no `immersiveengineering` namespace in the catalog.

## Physical age order

The power systems are not one linear mod ladder. Their intended topology is:

1. Andesite foundations: Create water wheels and wind provide basic rotation.
2. Steam Power: Create boilers/Steam Engines provide the first scalable rotation.
3. Early Electricity Technology: TFMG generator and motor convert rotation and FE.
4. Early Power Cables: TFMG connectors and hubs distribute power locally.
5. Chemical Processing: sulfuric acid, lead-acid storage, rubber, and steel cable tubes mature the local network. This develops beside Early Power Cables.
6. Grid Engineering: after both local cables and chemistry, Electro Energetics adds the 128-block overhead grid, grid alternator parts, and upgraded storage.
7. High-Voltage Systems, then Extreme Power Transmission: analog grid conversion/protection remains its own branch.
8. Reinforced Systems, then Precision Engineering: Mekanism supplies dense in-factory storage and local transmission on the factory branch.
9. High-Energy Distribution: Extreme Power Transmission and Precision Engineering converge before ultimate cables/cubes and induction storage.

The generated research files confirm the important joins: Grid Engineering requires both Chemical Processing and Early Power Cables; High-Voltage Systems requires only Grid Engineering; High-Energy Distribution requires both Extreme Power Transmission and Precision Engineering.

## Concrete gaps and bypasses

### 1. Early TFMG generation is missing, not merely expensive

`tfmg:generator` and `tfmg:electric_motor` remain in `exclude_outputs`, but the source-owned IDs expected by policy are absent:

- `industrial_colonies:early_electricity/generator`
- `industrial_colonies:early_electricity/electric_motor`

The only installed producers are `tfmg:sequenced_assembly/generator` and `tfmg:sequenced_assembly/motor`. They require steel mechanisms, winding, magnets, and (for the generator) a TFMG capacitor. Those are later than the pre-steel Early Electricity node and make the intended gateway physically unreachable. The recovery recipes use brass casing, copper/iron, shafts, and Precision Mechanisms, exactly as the earlier reviewed design specified.

### 2. The local TFMG cable boundary regressed to sibling dependencies

The managed auto recipes for `tfmg:cable_connector` and `tfmg:copper_cable_hub` both use `tfmg:copper_spool` as a generic phase gate. Copper spools belong to Electronics Manufacturing, a sibling child of Early Electricity, not an ancestor of Early Power Cables. This creates an unintended research detour.

The current auto recipes for `createaddition:redstone_relay` and `createaddition:small_light_connector` also still consume `createaddition:connector`. The reviewed compatibility recipes instead use `tfmg:cable_connector`, preserving those two unique utilities without preserving a duplicate connector system.

### 3. The TFMG-default duplicate retirements disappeared

All five exact Create Crafts & Additions recipes below are installed and absent from current managed removals:

| Exact recipe ID | Duplicate output | Canonical replacement |
|---|---|---|
| `createaddition:mechanical_crafting/alternator` | `createaddition:alternator` | `tfmg:generator` |
| `createaddition:mechanical_crafting/electric_motor` | `createaddition:electric_motor` | `tfmg:electric_motor` |
| `createaddition:crafting/modular_accumulator` | `createaddition:modular_accumulator` | `tfmg:accumulator` |
| `createaddition:crafting/connector` | `createaddition:connector` | `tfmg:cable_connector` |
| `createaddition:crafting/large_connector` | `createaddition:large_connector` | `tfmg:copper_cable_hub` |

The catalog shows only two consumers of the retired connector: Redstone Relay and Small Light Connector. Both are ported in the recovery batch. No installed recipe consumes the large connector. `createaddition:portable_energy_interface` is not a duplicate fixed endpoint and should remain.

### 4. Chemical storage lost its intended construction language

`industrial_colonies:auto/tfmg/accumulator` does remove both stock TFMG recipes, but its 5x5 shell retains `tfmg:industrial_aluminum_casing`. The documented pack design is a TFMG lead-acid accumulator made from sulfuric acid, canonical lead, copper wire, and steel casing at Chemical Processing.

`tfmg:cable_tube` uses chemically correct rubber and steel in the auto recipe, but it was also meant to be a compact eight-tube production batch, not another phase-ring 5x5. Restoring both reviewed recipes makes the Chemical Processing factory legible.

### 5. All seven first-grid recipe IDs are missing

The current manifest contains only `industrial_colonies:auto/electroenergetics/...` replacements for the seven Grid Engineering outputs. Those recipes use `tfmg:copper_spool` as a generic sibling-branch gate instead of upgrading actual TFMG generation, local endpoints, and chemical storage.

The most concrete regression is the base connector: auto-generation removes all four recipes that produce `electroenergetics:connector`, including these safe reverse conversions:

- `electroenergetics:crafting/connector_from_double`
- `electroenergetics:crafting/connector_from_triple`
- `electroenergetics:crafting/connector_from_quad`

Those recipes create no early material and only reclaim already-manufactured connector variants. Policy explicitly preserves them. The source-owned replacement must remove only `electroenergetics:crafting/connector`.

## Recommended implementation batch

The exact contracts are in the JSON plan. The implementation order is:

| Order | Node | Source-owned recipe ID | Output | Exact stock ID(s) to remove |
|---:|---|---|---|---|
| 10 | Early Electricity | `industrial_colonies:early_electricity/generator` | `tfmg:generator` | `tfmg:sequenced_assembly/generator` |
| 20 | Early Electricity | `industrial_colonies:early_electricity/electric_motor` | `tfmg:electric_motor` | `tfmg:sequenced_assembly/motor` |
| 30 | Early Power Cables | `industrial_colonies:early_power_cables/cable_connector` | `tfmg:cable_connector` | `tfmg:crafting/materials/cable_connector` |
| 40 | Early Power Cables | `industrial_colonies:early_power_cables/copper_cable_hub` | `2x tfmg:copper_cable_hub` | `tfmg:crafting/materials/copper_cable_hub` |
| 50 | Early Power Cables | `industrial_colonies:early_power_cables/redstone_relay` | `createaddition:redstone_relay` | `createaddition:crafting/redstone_relay` |
| 60 | Early Power Cables | `industrial_colonies:early_power_cables/small_light_connector` | `createaddition:small_light_connector` | `createaddition:crafting/small_light_connector` |
| 70 | Chemical Processing | `industrial_colonies:chemical_processing/accumulator` | `tfmg:accumulator` | both TFMG accumulator crafting IDs |
| 80 | Chemical Processing | `industrial_colonies:chemical_processing/cable_tube` | `8x tfmg:cable_tube` | `tfmg:crafting/materials/cable_tube` |
| 90 | Grid Engineering | `industrial_colonies:grid/empty_spool` | `4x electroenergetics:empty_spool` | `electroenergetics:crafting/empty_spool` |
| 100 | Grid Engineering | `industrial_colonies:grid/connector` | `2x electroenergetics:connector` | base connector recipe only |
| 110 | Grid Engineering | `industrial_colonies:grid/copper_wire_spool` | `electroenergetics:copper_wire_spool` | `electroenergetics:crafting/copper_wire_spool` |
| 120 | Grid Engineering | `industrial_colonies:grid/resistor` | `electroenergetics:resistor` | `electroenergetics:crafting/resistor` |
| 130 | Grid Engineering | `industrial_colonies:grid/accumulator` | `electroenergetics:accumulator` | `electroenergetics:crafting/accumulator` |
| 140 | Grid Engineering | `industrial_colonies:grid/alternator_rotor` | `electroenergetics:alternator_rotor` | `electroenergetics:crafting/alternator_rotor` |
| 150 | Grid Engineering | `industrial_colonies:grid/alternator_brushes` | `electroenergetics:alternator_brushes` | `electroenergetics:crafting/alternator_brushes` |

Implementation rules:

- Put the recipes in `managed_recipe_overhaul.seed.json`; do not reactivate legacy scripts.
- Keep exact removal ownership with each source recipe and place the five duplicate retirements in exact additional removals.
- Keep generator/motor excluded from auto-generation so only their deliberate pre-steel recipes own the outputs.
- Preserve the three connector-reclamation IDs.
- Preserve the Portable Energy Interface.
- Regenerate shared artifacts only after the source patch is reviewed, because other agents may also be editing the seed.

## Deferred but confirmed problems

### Analog High-Voltage Systems

The seven-output family must be repaired together. Four generic recipes (`transformer`, `current_transformer`, `voltage_regulator`, and `insulated_wire`) use both `ae2:calculation_processor` and `mekanism:advanced_control_circuit`. The source-owned transformer core uses `tfmg:transformer` and `mekanism:alloy_reinforced`; the source-owned miniature breaker uses later TFMG circuitry plus reinforced alloy. None of those branches is an ancestor of High-Voltage Systems.

The High-Voltage follow-up must source-own these exact stock IDs:

- `electroenergetics:stonecutting/transformer_core_lamination`
- `electroenergetics:sequenced_assembly/transformer_core`
- `electroenergetics:crafting/transformer`
- `electroenergetics:crafting/current_transformer`
- `electroenergetics:crafting/voltage_regulator`
- `electroenergetics:sequenced_assembly/miniature_circuit_breaker`
- `electroenergetics:crafting/insulated_wire`

It should use Grid Engineering ancestors and same-node analog components only. This topology finding supersedes the sibling-Mekanism ingredient suggestions in `PROCESSING_COMPONENT_AUDIT.plan.json`; it does not change that audit's classification of the three processing-only routes as requiring explicit ownership.

### Extreme Power Transmission

The same issue continues into the next grid node. In particular, the current source-owned sulfur-hexafluoride breaker requires an AE2 Engineering Processor and Mekanism Advanced Control Circuit even though Extreme Power Transmission has only High-Voltage Systems as a parent. The full seven-output follow-up, including the currently unassigned `electroenergetics:heavily_insulated_wire`, is listed with exact stock IDs in the JSON plan.

### Mekanism energy cubes

Stock cube recipes are correctly removed, but their generated replacements do not encode their assigned physical tiers:

| Cube | Assigned node | Current physical issue |
|---|---|---|
| Basic | Reinforced Systems | Uses only basic controls/infused alloy, tablets, and steel casing. |
| Advanced | Reinforced Systems | Consumes the basic cube but still only basic controls/infused alloy; it never requires the node's advanced circuit or reinforced alloy. |
| Elite | Precision Engineering | Uses advanced controls, reinforced alloy, and an unrelated Calculation Processor; it omits elite controls and atomic alloy. |
| Ultimate | High-Energy Distribution | Uses atomic alloy but still only advanced controls/Calculation Processor; it omits the Ultimate Control Circuit and any Extreme Power Transmission component. |

The cube repair should converge the EE accumulator into the basic cube, then require the correct circuit/alloy tier at each upgrade. The ultimate cube must consume an Extreme Power Transmission component because High-Energy Distribution is the graph's explicit convergence node.

### Induction storage

Only induction casing, port, and the ultimate cell are assigned to High-Energy Distribution. Basic/advanced/elite cells and all four providers retain stock recipes outside that physical ownership. The complete ten-recipe multiblock family should be handled together after the cube ladder, not piecemeal.

### Create Steam Engine

Water wheels and the Windmill Bearing are legitimate early rotational sources. The Steam Engine is different: its current managed recipe is still the stock gold-plate/andesite/copper-block craft, so it does not physically express the Steam Power node's brass and fluid-handling foundation. A one-recipe follow-up should consume that foundation without removing the early kinetic options.

### Immersive Engineering

Integration is blocked by installation state, not design uncertainty. Once a compatible NeoForge 1.21.1 Immersive Engineering JAR is actually present, rebuild the item/recipe catalog and only then place its dynamo, capacitors, connectors, relays, transformers, and coils. No IDs from ImmersiveUI may be used as substitutes.

## Validation target

`tools/validate_power_backbone_audit.py` validates the plan against the current installed catalog and mod directory. It checks every proposed output, concrete ingredient, machine environment, exact stock removal, retirement, safe survivor, and expected source-output relation. Tags are syntax-checked but deliberately not guessed from item rows.

Run it from the project root with:

```powershell
python tools/validate_power_backbone_audit.py `
  --catalog "C:\Users\GodPC\Documents\Codex\2026-08-16\ok\outputs\recipe-catalog-current" `
  --mods "C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods"
```
