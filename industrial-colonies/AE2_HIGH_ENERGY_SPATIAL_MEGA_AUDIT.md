# AE2 High-Energy, Spatial, and MEGA Core audit

Status: **implemented in the authoritative seed**. The nine reviewed contracts and eleven stock-recipe preservation IDs are source-owned; assignments were intentionally unchanged. Generated recipes, quests, deployment/live files, and Draw.io were not edited by this batch.

## Outcome

All nine priority outputs receive recognizable manufacturing contracts instead of the generic A/B 5×5 ring. The export bus uses the Copper electronics line; network control and configuration hardware use Brass; spatial field hardware and the MEGA crafting core use Industrial-Iron heavy assembly. Every contract contains a real TFMG component.

The first ME network remains in Digital Logistics. These upgrades stay in High-Energy Grid and consume earlier terminal/interface/energy-acceptor infrastructure rather than becoming prerequisites of it.

## Exact replacement contracts

| Order | Output / managed ID | Existing node and phase | Process | Physical inputs | Exact removal |
|---:|---|---|---|---|---|
| 160 | `ae2:cell_workbench`<br>`industrial_colonies:ae2_high_energy/cell_workbench` | CR01 — Enhanced ME System Upgrade<br>High-Energy Grid | `compacting`<br>`createcasing:brass_press` | `ae2:terminal`<br>`ae2:calculation_processor`<br>`#c:chests/wooden`<br>`#minecraft:wool`<br>`tfmg:circuit_board`<br>`tfmg:plastic_sheet`<br>`create:precision_mechanism` | `ae2:network/blocks/cell_workbench` |
| 170 | `ae2:controller`<br>`industrial_colonies:ae2_high_energy/controller` | CR01 — ME System Advanced<br>High-Energy Grid | `sequenced_assembly`<br>`createcasing:brass_deployer` → `createcasing:brass_press` | `ae2:energy_acceptor`<br>`ae2:smooth_sky_stone_block`<br>`ae2:engineering_processor`<br>`tfmg:transformer`<br>`ae2:fluix_crystal` | `ae2:network/blocks/controller` |
| 180 | `ae2:export_bus`<br>`industrial_colonies:ae2_high_energy/export_bus` | CR01 — Advanced ME BUS Technology<br>High-Energy Grid | `sequenced_assembly`<br>`createcasing:copper_deployer` → `createcasing:copper_press` | `minecraft:piston`<br>`tfmg:circuit_board`<br>`ae2:formation_core`<br>`tfmg:copper_wire` | `ae2:network/parts/export_bus` |
| 190 | `ae2:io_port`<br>`industrial_colonies:ae2_high_energy/io_port` | CR01 — Enhanced ME System Upgrade<br>High-Energy Grid | `sequenced_assembly`<br>`createcasing:brass_deployer` → `createcasing:brass_press` | `ae2:drive`<br>`ae2:interface`<br>`ae2:logic_processor`<br>`tfmg:circuit_board`<br>`ae2:fluix_glass_cable` | `ae2:network/blocks/io_port` |
| 200 | `ae2:me_p2p_tunnel`<br>`industrial_colonies:ae2_high_energy/me_p2p_tunnel` | CR01 — P2P Tunneling Technology<br>High-Energy Grid | `sequenced_assembly`<br>`createcasing:brass_deployer` → `createcasing:brass_press` | `ae2:quartz_fiber`<br>`ae2:engineering_processor`<br>`tfmg:circuit_board`<br>`tfmg:copper_wire`<br>`ae2:fluix_crystal` | `ae2:network/parts/tunnels_me` |
| 210 | `4x ae2:spatial_pylon`<br>`industrial_colonies:ae2_high_energy/spatial_pylon_batch` | CR01 — Spacial Storage Tech<br>High-Energy Grid | `compacting`<br>`createcasing:industrial_iron_press` | `4x ae2:quartz_glass`<br>`2x ae2:fluix_glass_cable`<br>`ae2:me_p2p_tunnel`<br>`tfmg:transformer`<br>`tfmg:steel_casing`<br>`ae2:calculation_processor` | `ae2:network/blocks/spatial_io_pylon` |
| 220 | `ae2:spatial_io_port`<br>`industrial_colonies:ae2_high_energy/spatial_io_port` | CR01 — Spacial Storage Tech<br>High-Energy Grid | `sequenced_assembly`<br>`createcasing:industrial_iron_deployer` → `createcasing:industrial_iron_press` | `ae2:io_port`<br>`ae2:controller`<br>`ae2:me_p2p_tunnel`<br>`ae2:engineering_processor`<br>`tfmg:steel_casing`<br>`ae2:spatial_cell_component_2` | `ae2:network/blocks/spatial_io_port` |
| 230 | `ae2:spatial_anchor`<br>`industrial_colonies:ae2_high_energy/spatial_anchor` | CR01 — World Loading Technology<br>High-Energy Grid | `compacting`<br>`createcasing:industrial_iron_press` | `ae2:spatial_io_port`<br>`4x ae2:spatial_pylon`<br>`ae2:spatial_cell_component_128`<br>`tfmg:transformer`<br>`ae2:engineering_processor`<br>`tfmg:steel_casing` | `ae2:network/blocks/spatial_anchor` |
| 240 | `megacells:mega_crafting_unit`<br>`industrial_colonies:ae2_high_energy/mega_crafting_unit` | CR01 — Enhanced ME Crafting Upgrade<br>High-Energy Grid | `sequenced_assembly`<br>`createcasing:industrial_iron_deployer` → `createcasing:industrial_iron_press` | `ae2:crafting_unit`<br>`megacells:accumulation_processor`<br>`ae2:engineering_processor`<br>`ae2:fluix_smart_cable`<br>`tfmg:transformer`<br>`tfmg:circuit_board` | `megacells:crafting/mega_crafting_unit` |

Sequences use one loop and finish in their casing-specific press. The four-output pylon compacting batch keeps a large spatial frame buildable at factory scale; it is not a one-off 5×5 craft per segment.

## Dependency shape

- The cell workbench consumes the earlier terminal; the controller upgrades the earlier energy acceptor; the IO port upgrades the earlier drive and interface.
- Controller, IO port, and ME P2P tunnel are ordered before all spatial contracts. The spatial IO port physically consumes all three, and the pylon batch physically consumes the P2P endpoint.
- The spatial anchor consumes a completed spatial IO port plus four pylons, so neither world loading nor the anchor can bypass the spatial control chain.
- The MEGA crafting unit upgrades the stock-managed AE crafting unit and consumes the accumulation processor, engineering processor, smart cable, TFMG transformer, and TFMG circuit board.
- No recipe in this batch consumes a Mekanism control circuit or alloy gate.

## Installed producers and acquisition bypass audit

Each target has exactly one installed data-recipe producer, and those nine exact IDs are the only removals proposed by this batch:

| Output | Installed recipe | Type | JAR / path |
|---|---|---|---|
| `ae2:cell_workbench` | `ae2:network/blocks/cell_workbench` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/cell_workbench.json` |
| `ae2:controller` | `ae2:network/blocks/controller` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/controller.json` |
| `ae2:export_bus` | `ae2:network/parts/export_bus` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/parts/export_bus.json` |
| `ae2:io_port` | `ae2:network/blocks/io_port` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/io_port.json` |
| `ae2:me_p2p_tunnel` | `ae2:network/parts/tunnels_me` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/parts/tunnels_me.json` |
| `ae2:spatial_anchor` | `ae2:network/blocks/spatial_anchor` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/spatial_anchor.json` |
| `ae2:spatial_io_port` | `ae2:network/blocks/spatial_io_port` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/spatial_io_port.json` |
| `ae2:spatial_pylon` | `ae2:network/blocks/spatial_io_pylon` | `minecraft:crafting_shaped` | `appliedenergistics2-19.2.17.jar`<br>`data/ae2/recipe/network/blocks/spatial_io_pylon.json` |
| `megacells:mega_crafting_unit` | `megacells:crafting/mega_crafting_unit` | `minecraft:crafting_shaped` | `megacells-4.11.0.jar`<br>`data/megacells/recipe/crafting/mega_crafting_unit.json` |

All 226 installed JARs were scanned for target references outside recipes and descriptive data. The 7 findings are ordinary target-block self-drop loot tables; no external loot-table or structure acquisition candidate was found.

## Bulk recipes deliberately preserved

Eleven stock recipes remain available because their difficult prerequisite already carries progression: four fluix cable/color-cleanup routes and seven shapeless MEGA crafting-unit closures. This avoids demanding a unique 5×5 craft for every cable or storage/monitor/accelerator closure.

| Role | Exact recipe ID | Type |
|---|---|---|
| `bulk_cable_or_color_cleanup` | `ae2:network/cables/glass_fluix` | `minecraft:crafting_shapeless` |
| `bulk_cable_or_color_cleanup` | `ae2:network/cables/glass_fluix_clean` | `minecraft:crafting_shapeless` |
| `bulk_cable_or_color_cleanup` | `ae2:network/cables/smart_fluix` | `minecraft:crafting_shapeless` |
| `bulk_cable_or_color_cleanup` | `ae2:network/cables/smart_fluix_clean` | `minecraft:crafting_shapeless` |
| `mega_unit_closure` | `megacells:crafting/1m_crafting_storage` | `minecraft:crafting_shapeless` |
| `mega_unit_closure` | `megacells:crafting/4m_crafting_storage` | `minecraft:crafting_shapeless` |
| `mega_unit_closure` | `megacells:crafting/16m_crafting_storage` | `minecraft:crafting_shapeless` |
| `mega_unit_closure` | `megacells:crafting/64m_crafting_storage` | `minecraft:crafting_shapeless` |
| `mega_unit_closure` | `megacells:crafting/256m_crafting_storage` | `minecraft:crafting_shapeless` |
| `mega_unit_closure` | `megacells:crafting/mega_crafting_accelerator` | `minecraft:crafting_shapeless` |
| `mega_unit_closure` | `megacells:crafting/mega_crafting_monitor` | `minecraft:crafting_shapeless` |

All other downstream recipes are audited but not frozen by this batch; they remain eligible for their own source-owned redesign instead of being silently blessed forever.

## Assignment and phase contract

Every target already appears exactly once in the intended node, and each node maps to High-Energy Grid. No assignment edit is proposed.

| Output | Existing node | Phase | Patch action |
|---|---|---|---|
| `ae2:cell_workbench` | CR01 — Enhanced ME System Upgrade | High-Energy Grid | `none` |
| `ae2:controller` | CR01 — ME System Advanced | High-Energy Grid | `none` |
| `ae2:export_bus` | CR01 — Advanced ME BUS Technology | High-Energy Grid | `none` |
| `ae2:io_port` | CR01 — Enhanced ME System Upgrade | High-Energy Grid | `none` |
| `ae2:me_p2p_tunnel` | CR01 — P2P Tunneling Technology | High-Energy Grid | `none` |
| `ae2:spatial_anchor` | CR01 — World Loading Technology | High-Energy Grid | `none` |
| `ae2:spatial_io_port` | CR01 — Spacial Storage Tech | High-Energy Grid | `none` |
| `ae2:spatial_pylon` | CR01 — Spacial Storage Tech | High-Energy Grid | `none` |
| `megacells:mega_crafting_unit` | CR01 — Enhanced ME Crafting Upgrade | High-Energy Grid | `none` |

The existing `Spacial Storage Tech` spelling is preserved because this read-only batch has no assignment-renaming ownership.

## Current automatic owners retired by integration

Adding these nine explicit owners will suppress the current generic automatic IDs on rebuild:

- `industrial_colonies:auto/ae2/cell_workbench`
- `industrial_colonies:auto/ae2/controller`
- `industrial_colonies:auto/ae2/export_bus`
- `industrial_colonies:auto/ae2/io_port`
- `industrial_colonies:auto/ae2/me_p2p_tunnel`
- `industrial_colonies:auto/ae2/spatial_anchor`
- `industrial_colonies:auto/ae2/spatial_io_port`
- `industrial_colonies:auto/ae2/spatial_pylon`
- `industrial_colonies:auto/megacells/mega_crafting_unit`

## Integration boundary

`AE2_HIGH_ENERGY_SPATIAL_MEGA_AUDIT.patch.json` is the applied historical patch record. It locks the released Foundry base hashes, carries the nine exact recipe specs, unions the eleven intentional stock preserves, and records no assignment changes.

## Validation

```powershell
python tools/build_ae2_high_energy_spatial_mega_audit.py --check
python tools/validate_ae2_high_energy_spatial_mega_audit.py
python tools/test_validate_ae2_high_energy_spatial_mega_audit.py
```

The validator locks installed source hashes, direct-producer coverage, non-recipe acquisition evidence, exact removals/preserves, TFMG-first machine routing, physical dependency order, same-batch acyclicity, predecessor availability, phase/assignment parity, current automatic-owner retirement intent, patch parity, and deterministic regeneration.
