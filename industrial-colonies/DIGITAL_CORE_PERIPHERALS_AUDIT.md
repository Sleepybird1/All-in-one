# Digital Core and Peripherals audit

Status: **implemented in the authoritative seed**. The 14 reviewed contracts and 44 stock-cell preservation IDs are source-owned; assignments were intentionally unchanged. Authoritative generated recipes, quests, deployment/live files, and Draw.io were not edited by this batch.

## Outcome

All 14 priority-batch outputs have exact replacement contracts. The generic 5×5 A/B gate rings are replaced by recognizable component assembly: four Copper-line recipes for power, bus, and housings; ten Brass-line recipes for terminals, interfaces, crafting hardware, and peripherals. Every contract uses a real TFMG electronic or structural component, while the first usable ME network contains no Mekanism control circuit or alloy gate.

## Exact replacement contracts

| Order | Output / managed ID | Node and phase | Process | Physical inputs | Exact removals |
|---:|---|---|---|---|---|
| 10 | `ae2:energy_acceptor`<br>`industrial_colonies:digital_core/energy_acceptor` | CR01 — ME System Basics<br>Digital Logistics | `compacting`<br>`createcasing:copper_press` | `ae2:quartz_glass`<br>`ae2:quartz_glass`<br>`tfmg:copper_wire`<br>`tfmg:copper_wire`<br>`tfmg:transformer`<br>`tfmg:circuit_board`<br>`ae2:fluix_crystal` | `ae2:network/blocks/energy_energy_acceptor`<br>`ae2:network/blocks/energy_energy_acceptor_alt` |
| 20 | `ae2:item_cell_housing`<br>`industrial_colonies:digital_core/item_cell_housing` | CR01 — ME System Basics<br>Digital Logistics | `compacting`<br>`createcasing:copper_press` | `ae2:quartz_glass`<br>`ae2:quartz_glass`<br>`tfmg:plastic_sheet`<br>`tfmg:plastic_sheet`<br>`tfmg:copper_wire`<br>`tfmg:circuit_board` | `ae2:network/cells/item_cell_housing` |
| 30 | `ae2:terminal`<br>`industrial_colonies:digital_core/terminal` | CR01 — ME System Basics<br>Digital Logistics | `sequenced_assembly`<br>`createcasing:brass_deployer` → `createcasing:brass_press` | `ae2:semi_dark_monitor`<br>`tfmg:circuit_board`<br>`ae2:logic_processor`<br>`ae2:formation_core`<br>`ae2:annihilation_core` | `ae2:network/parts/terminals` |
| 40 | `ae2:import_bus`<br>`industrial_colonies:digital_core/import_bus` | CR01 — Early ME BUS Technology<br>Digital Logistics | `sequenced_assembly`<br>`createcasing:copper_deployer` → `createcasing:copper_press` | `minecraft:piston`<br>`tfmg:circuit_board`<br>`ae2:annihilation_core`<br>`tfmg:copper_wire` | `ae2:network/parts/import_bus` |
| 50 | `ae2:interface`<br>`industrial_colonies:digital_core/interface` | CR01 — Early ME BUS Technology<br>Digital Logistics | `sequenced_assembly`<br>`createcasing:brass_deployer` → `createcasing:brass_press` | `ae2:quartz_glass`<br>`tfmg:circuit_board`<br>`ae2:logic_processor`<br>`ae2:annihilation_core`<br>`ae2:formation_core` | `ae2:network/blocks/interfaces_interface`<br>`ae2:network/blocks/interfaces_interface_alt` |
| 60 | `ae2:molecular_assembler`<br>`industrial_colonies:digital_core/molecular_assembler` | CR01 — Early Digital Crafting<br>Digital Logistics | `compacting`<br>`createcasing:brass_press` | `minecraft:crafting_table`<br>`ae2:quartz_glass`<br>`ae2:quartz_glass`<br>`ae2:annihilation_core`<br>`ae2:formation_core`<br>`create:precision_mechanism`<br>`tfmg:circuit_board` | `ae2:network/crafting/molecular_assembler` |
| 70 | `appmek:chemical_cell_housing`<br>`industrial_colonies:digital_core/chemical_cell_housing` | CR01 — Early Digital Chemical Storage<br>Digital Logistics | `compacting`<br>`createcasing:copper_press` | `ae2:quartz_glass`<br>`ae2:quartz_glass`<br>`tfmg:plastic_sheet`<br>`tfmg:plastic_sheet`<br>`#c:ingots/osmium`<br>`#c:ingots/osmium`<br>`tfmg:copper_wire`<br>`tfmg:circuit_board` | `appmek:chemical_cell_housing` |
| 10 | `ae2:pattern_provider`<br>`industrial_colonies:digital_core/pattern_provider` | CR01 — Advanced Digital Crafting<br>Mekanized Industry | `sequenced_assembly`<br>`createcasing:brass_deployer` → `createcasing:brass_press` | `ae2:interface`<br>`minecraft:crafting_table`<br>`ae2:calculation_processor`<br>`tfmg:circuit_board`<br>`create:precision_mechanism` | `ae2:network/blocks/pattern_providers_interface`<br>`ae2:network/blocks/pattern_providers_interface_alt` |
| 10 | `advancedperipherals:peripheral_casing`<br>`industrial_colonies:digital_core/peripheral_casing` | CR01 — Advanced Perhipherals<br>High-Energy Grid | `sequenced_assembly`<br>`createcasing:brass_deployer` → `createcasing:brass_press` | `tfmg:steel_casing`<br>`tfmg:circuit_board`<br>`computercraft:wired_modem_full`<br>`ae2:engineering_processor`<br>`tfmg:plastic_sheet` | `advancedperipherals:peripheral_casing` |
| 20 | `advancedperipherals:block_reader`<br>`industrial_colonies:digital_core/block_reader` | CR01 — Advanced Perhipherals<br>High-Energy Grid | `compacting`<br>`createcasing:brass_press` | `advancedperipherals:peripheral_casing`<br>`computercraft:wired_modem_full`<br>`minecraft:observer`<br>`create:content_observer`<br>`tfmg:circuit_board`<br>`ae2:calculation_processor` | `advancedperipherals:block_reader` |
| 30 | `advancedperipherals:energy_detector`<br>`industrial_colonies:digital_core/energy_detector` | CR01 — Advanced Perhipherals<br>High-Energy Grid | `compacting`<br>`createcasing:brass_press` | `advancedperipherals:peripheral_casing`<br>`tfmg:voltage_observer`<br>`tfmg:copper_wire`<br>`minecraft:comparator`<br>`tfmg:circuit_board`<br>`ae2:calculation_processor` | `advancedperipherals:energy_detector` |
| 40 | `advancedperipherals:inventory_manager`<br>`industrial_colonies:digital_core/inventory_manager` | CR01 — Advanced Perhipherals<br>High-Energy Grid | `compacting`<br>`createcasing:brass_press` | `advancedperipherals:peripheral_casing`<br>`computercraft:wired_modem_full`<br>`minecraft:hopper`<br>`#c:chests`<br>`create:content_observer`<br>`tfmg:circuit_board`<br>`ae2:calculation_processor` | `advancedperipherals:inventory_manager` |
| 50 | `advancedperipherals:colony_integrator`<br>`industrial_colonies:digital_core/colony_integrator` | CR01 — Advanced Perhipherals<br>High-Energy Grid | `compacting`<br>`createcasing:brass_press` | `advancedperipherals:peripheral_casing`<br>`computercraft:wired_modem_full`<br>`minecolonies:blockminecoloniesrack`<br>`minecolonies:build_goggles`<br>`structurize:sceptergold`<br>`tfmg:circuit_board` | `advancedperipherals:colony_integrator` |
| 60 | `advancedperipherals:me_bridge`<br>`industrial_colonies:digital_core/me_bridge` | CR01 — Advanced Perhipherals<br>High-Energy Grid | `compacting`<br>`createcasing:brass_press` | `advancedperipherals:peripheral_casing`<br>`ae2:interface`<br>`ae2:fluix_block`<br>`ae2:fluix_block`<br>`computercraft:wired_modem_full`<br>`tfmg:circuit_board`<br>`ae2:engineering_processor` | `advancedperipherals:me_bridge` |

Every sequenced assembly uses one loop and four or five meaningful operations. No shaped or mechanical-crafting recipe in this batch uses a decorative generic gate ring.

## Dependency order

- `advancedperipherals:peripheral_casing` is manufactured first and is a physical input plus explicit dependency of all five downstream Advanced Peripherals devices.
- `ae2:interface` is manufactured in Digital Logistics. It is a physical input of the later `ae2:pattern_provider` upgrade and `advancedperipherals:me_bridge`.
- `ae2:item_cell_housing` and `appmek:chemical_cell_housing` are manufactured before the preserved stock closure recipes that combine them with cell components.
- Digital Logistics uses `tfmg:circuit_board` and, where appropriate, `ae2:logic_processor`; it does not consume any Mekanism control circuit or infused/reinforced/atomic alloy.
- `ae2:calculation_processor` enters only at Mekanized Industry or later. `ae2:engineering_processor` enters only in the High-Energy peripheral platform.

## Assignment contract

No assignment edit is proposed because every output already appears exactly once under its intended node.

| Output | Required existing node | Patch action |
|---|---|---|
| `ae2:energy_acceptor` | CR01 — ME System Basics | `none` |
| `ae2:import_bus` | CR01 — Early ME BUS Technology | `none` |
| `ae2:interface` | CR01 — Early ME BUS Technology | `none` |
| `ae2:item_cell_housing` | CR01 — ME System Basics | `none` |
| `ae2:molecular_assembler` | CR01 — Early Digital Crafting | `none` |
| `ae2:terminal` | CR01 — ME System Basics | `none` |
| `appmek:chemical_cell_housing` | CR01 — Early Digital Chemical Storage | `none` |
| `ae2:pattern_provider` | CR01 — Advanced Digital Crafting | `none` |
| `advancedperipherals:peripheral_casing` | CR01 — Advanced Perhipherals | `none` |
| `advancedperipherals:block_reader` | CR01 — Advanced Perhipherals | `none` |
| `advancedperipherals:colony_integrator` | CR01 — Advanced Perhipherals | `none` |
| `advancedperipherals:energy_detector` | CR01 — Advanced Perhipherals | `none` |
| `advancedperipherals:inventory_manager` | CR01 — Advanced Perhipherals | `none` |
| `advancedperipherals:me_bridge` | CR01 — Advanced Perhipherals | `none` |

The existing node spelling `CR01 — Advanced Perhipherals` is preserved because this batch has no ownership to rename shared progression data.

## Installed source audit and removals

The 17 IDs below are the only installed recipes removed by this patch. The three AE block/part conversion recipes are included because leaving them would bypass the new energy acceptor, interface, or pattern-provider manufacturing route.

| Recipe ID | Type | Installed JAR / path | Catalog outputs |
|---|---|---|---|
| `ae2:network/blocks/energy_energy_acceptor` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/energy_energy_acceptor.json` | `ae2:energy_acceptor` |
| `ae2:network/blocks/energy_energy_acceptor_alt` | `minecraft:crafting_shapeless` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/energy_energy_acceptor_alt.json` | `ae2:energy_acceptor` |
| `ae2:network/parts/import_bus` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/parts/import_bus.json` | `ae2:import_bus` |
| `ae2:network/blocks/interfaces_interface` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/interfaces_interface.json` | `ae2:interface` |
| `ae2:network/blocks/interfaces_interface_alt` | `minecraft:crafting_shapeless` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/interfaces_interface_alt.json` | `ae2:interface` |
| `ae2:network/cells/item_cell_housing` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/cells/item_cell_housing.json` | `ae2:item_cell_housing` |
| `ae2:network/crafting/molecular_assembler` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/crafting/molecular_assembler.json` | `ae2:molecular_assembler` |
| `ae2:network/parts/terminals` | `minecraft:crafting_shapeless` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/parts/terminals.json` | `ae2:terminal` |
| `appmek:chemical_cell_housing` | `minecraft:crafting_shaped` | `Applied-Mekanistics-1.6.3.jar`<br>`data/appmek/recipe/chemical_cell_housing.json` | `appmek:chemical_cell_housing` |
| `ae2:network/blocks/pattern_providers_interface` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/pattern_providers_interface.json` | `ae2:pattern_provider` |
| `ae2:network/blocks/pattern_providers_interface_alt` | `minecraft:crafting_shapeless` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/pattern_providers_interface_alt.json` | `ae2:pattern_provider` |
| `advancedperipherals:peripheral_casing` | `minecraft:crafting_shaped` | `AdvancedPeripherals-1.21.1-0.7.62b.jar`<br>`data/advancedperipherals/recipe/peripheral_casing.json` | `advancedperipherals:peripheral_casing` |
| `advancedperipherals:block_reader` | `minecraft:crafting_shaped` | `AdvancedPeripherals-1.21.1-0.7.62b.jar`<br>`data/advancedperipherals/recipe/block_reader.json` | `advancedperipherals:block_reader` |
| `advancedperipherals:colony_integrator` | `minecraft:crafting_shaped` | `AdvancedPeripherals-1.21.1-0.7.62b.jar`<br>`data/advancedperipherals/recipe/colony_integrator.json` | `advancedperipherals:colony_integrator` |
| `advancedperipherals:energy_detector` | `minecraft:crafting_shaped` | `AdvancedPeripherals-1.21.1-0.7.62b.jar`<br>`data/advancedperipherals/recipe/energy_detector.json` | `advancedperipherals:energy_detector` |
| `advancedperipherals:inventory_manager` | `minecraft:crafting_shaped` | `AdvancedPeripherals-1.21.1-0.7.62b.jar`<br>`data/advancedperipherals/recipe/inventory_manager.json` | `advancedperipherals:inventory_manager` |
| `advancedperipherals:me_bridge` | `minecraft:crafting_shaped` | `AdvancedPeripherals-1.21.1-0.7.62b.jar`<br>`data/advancedperipherals/recipe/me_bridge.json` | `advancedperipherals:me_bridge` |

## Stock cell recipes explicitly preserved

Housing recovery/disassembly and cell closure remain stock. This preserves AE2/AppMek's reversible cell behavior while ensuring the manufactured housing is the prerequisite shell.

| Role | Exact recipe ID | Type |
|---|---|---|
| `housing_recovery` | `ae2:cell_upgrade/item_storage_cell_16k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/item_storage_cell_1k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/item_storage_cell_256k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/item_storage_cell_4k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/item_storage_cell_64k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/portable_item_cell_16k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/portable_item_cell_1k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/portable_item_cell_256k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/portable_item_cell_4k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `ae2:cell_upgrade/portable_item_cell_64k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/chemical_storage_cell_16k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/chemical_storage_cell_1k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/chemical_storage_cell_256k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/chemical_storage_cell_4k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/chemical_storage_cell_64k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/portable_chemical_cell_16k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/portable_chemical_cell_1k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/portable_chemical_cell_256k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/portable_chemical_cell_4k` | `ae2:storage_cell_disassembly` |
| `housing_recovery` | `appmek:cell_upgrade/portable_chemical_cell_64k` | `ae2:storage_cell_disassembly` |
| `cell_closure` | `ae2:network/cells/item_storage_cell_16k_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:network/cells/item_storage_cell_1k_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:network/cells/item_storage_cell_256k_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:network/cells/item_storage_cell_4k_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:network/cells/item_storage_cell_64k_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:network/cells/spatial_storage_cell_128_cubed_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:network/cells/spatial_storage_cell_16_cubed_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:network/cells/spatial_storage_cell_2_cubed_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:network/cells/view_cell_storage` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:tools/portable_item_cell_16k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:tools/portable_item_cell_1k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:tools/portable_item_cell_256k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:tools/portable_item_cell_4k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `ae2:tools/portable_item_cell_64k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:chemical_storage_cell_16k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:chemical_storage_cell_1k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:chemical_storage_cell_256k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:chemical_storage_cell_4k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:chemical_storage_cell_64k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:portable_chemical_cell_16k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:portable_chemical_cell_1k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:portable_chemical_cell_256k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:portable_chemical_cell_4k` | `minecraft:crafting_shapeless` |
| `cell_closure` | `appmek:portable_chemical_cell_64k` | `minecraft:crafting_shapeless` |

## Automatic owners retired by integration

The pre-integration generated snapshot contained one automatic 5×5 owner for every batch output. The reviewed explicit seed owners suppress these 14 automatic IDs in an isolated rebuild:

- `industrial_colonies:auto/ae2/energy_acceptor`
- `industrial_colonies:auto/ae2/import_bus`
- `industrial_colonies:auto/ae2/interface`
- `industrial_colonies:auto/ae2/item_cell_housing`
- `industrial_colonies:auto/ae2/molecular_assembler`
- `industrial_colonies:auto/ae2/terminal`
- `industrial_colonies:auto/appmek/chemical_cell_housing`
- `industrial_colonies:auto/ae2/pattern_provider`
- `industrial_colonies:auto/advancedperipherals/peripheral_casing`
- `industrial_colonies:auto/advancedperipherals/block_reader`
- `industrial_colonies:auto/advancedperipherals/colony_integrator`
- `industrial_colonies:auto/advancedperipherals/energy_detector`
- `industrial_colonies:auto/advancedperipherals/inventory_manager`
- `industrial_colonies:auto/advancedperipherals/me_bridge`

## Integration boundary

`DIGITAL_CORE_PERIPHERALS_AUDIT.patch.json` is the applied historical patch record. It is rebased to the released Heavy/Electrical source hashes, carries the unchanged 14 reviewed recipe specs and 44-ID preservation union, and records that no assignment edit was made. The audit validator checks the implemented seed against those immutable payloads.

## Validation

Run:

```powershell
python tools/build_digital_core_peripherals_audit.py --check
python tools/validate_digital_core_peripherals_audit.py
python tools/test_validate_digital_core_peripherals_audit.py
```

The validator checks installed JAR and recipe hashes, catalog identity, exact output/removal coverage, all 44 preserved closures and recoveries in the seed, prerequisite and TFMG transformer/voltage-observer ownership, Copper/Brass routing, phase gates, same-batch acyclicity, exact assignment parity, applied-patch parity, and deterministic regeneration. With `--managed` pointed at an isolated rebuild, it also proves all 14 automatic owners retired and all 17 removals compiled. Mutation tests prove each major invariant fails closed.
