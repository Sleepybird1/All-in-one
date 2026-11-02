# Automatic Recipe Quality Audit

Status: **read-only audit complete**. This document audits the pinned `build-current-audit` snapshot only. It does not authorize or perform seed, assignment, generated-artifact, quest, deployment, live-pack, or Draw.io edits.

## Outcome

The snapshot contains **172** automatic recipe owners. Exactly **145 of 146** automatic Mechanical Crafting recipes use the same generated `A/B` perimeter. The one exception is Create's installed Crushing Wheel layout. That makes the problem structural: the converter is expressing phase gates, not manufacturing logic.

| Disposition | Count | Meaning |
|---|---:|---|
| Acceptable stock-derived / utility | 27 | Keep the automatic exact-stock owner. |
| Needs source-owned redesign | 81 | Replace the generated owner with an explicit recipe contract. |
| Redundant / should retire | 8 | Disable the duplicate output only after route-parity proof. |
| Runtime artifact / leave stock | 56 | Retire the automatic owner and preserve its exact installed recipe. |

The **81 redesigns are the actual content backlog**. The 56 leave-stock items are not freebies: their prerequisite processors, housings, casings, conductors, or machines carry the progression cost once those reusable chains are fixed.

## Rules used

- Difficulty belongs in reusable manufactured subcomponents and capability order, not in identical gate rings pasted around every output.
- TFMG owns overlapping fuels, electronics, pressure chemistry, and heavy industrial materials unless an audited unique function requires another system.
- Copper environments make electrical parts, Brass environments make precision/digital parts, and Industrial Iron environments make pressure/heavy components.
- The first useful Create, TFMG, Mekanism, ComputerCraft, and AE2 capabilities must exist before late nuclear construction; spatial and mega-scale extensions may move later.
- Bulk closures, reversible storage forms, visual variants, and compatibility adapters inherit progression from their hard prerequisite and stay stock-scalable.

## Priority implementation batches

### 1. `tfmg_first_heavy_and_electrical`

Outputs and installed source recipe IDs:

| Output | Installed recipe ID |
|---|---|
| `tfmg:centrifuge` | `tfmg:crafting/materials/centrifuge` |
| `tfmg:diesel_engine_cylinder` | `tfmg:engine_cylinder` |
| `tfmg:engine_cylinder` | `tfmg:engine_cylinder_spark_plug` |
| `tfmg:electrode_holder` | `tfmg:crafting/materials/electrode_holder` |
| `tfmg:transformer` | `tfmg:crafting/materials/transformer` |
| `tfmg:voltage_observer` | `tfmg:crafting/materials/voltage_observer` |
| `createaddition:digital_adapter` | `createaddition:crafting/digital_adapter` |
| `createaddition:portable_energy_interface` | `createaddition:crafting/portable_energy_interface` |

Prerequisite capabilities:

- `tfmg:cast_iron_frame`
- `tfmg:copper_spool`
- `tfmg:steel_casing`
- `tfmg:circuit_board`
- `tfmg:transistor_item`
- `tfmg:capacitor_item`
- `create:precision_mechanism`

Recommended encased roles:

- `heavy_rotating_and_engine_parts` → `createcasing:industrial_iron_press/deployer`
- `electrical_windings_and_observation` → `createcasing:copper_press/deployer`
- `precision_adapters` → `createcasing:brass_press/deployer`

Cycle risks:

- Do not require a transformer, centrifuge, finished engine, or refined fuel to manufacture its own prerequisite subassembly.
- Keep the cast-iron and first-steel bootstrap earlier than industrial-iron-environment recipes.
- The portable energy interface must not become a prerequisite of the copper spool or base connector that it consumes.

### 2. `digital_core_and_peripherals`

Outputs and installed source recipe IDs:

| Output | Installed recipe ID |
|---|---|
| `ae2:energy_acceptor` | `ae2:network/blocks/energy_energy_acceptor` |
| `ae2:import_bus` | `ae2:network/parts/import_bus` |
| `ae2:interface` | `ae2:network/blocks/interfaces_interface` |
| `ae2:item_cell_housing` | `ae2:network/cells/item_cell_housing` |
| `ae2:molecular_assembler` | `ae2:network/crafting/molecular_assembler` |
| `ae2:terminal` | `ae2:network/parts/terminals` |
| `appmek:chemical_cell_housing` | `appmek:chemical_cell_housing` |
| `ae2:pattern_provider` | `ae2:network/blocks/pattern_providers_interface` |
| `advancedperipherals:peripheral_casing` | `advancedperipherals:peripheral_casing` |
| `advancedperipherals:block_reader` | `advancedperipherals:block_reader` |
| `advancedperipherals:colony_integrator` | `advancedperipherals:colony_integrator` |
| `advancedperipherals:energy_detector` | `advancedperipherals:energy_detector` |
| `advancedperipherals:inventory_manager` | `advancedperipherals:inventory_manager` |
| `advancedperipherals:me_bridge` | `advancedperipherals:me_bridge` |

Prerequisite capabilities:

- `tfmg:circuit_board`
- `ae2:logic_processor`
- `ae2:calculation_processor`
- `ae2:engineering_processor`
- `computercraft:wired_modem_full`

Recommended encased roles:

- `board_and_bus_assembly` → `createcasing:copper_deployer/press`
- `precision_terminal_and_interface_assembly` → `createcasing:brass_deployer/press`

Cycle risks:

- Peripheral casing must precede all six Advanced Peripherals devices.
- AE2 interface must precede the ME bridge; item and chemical housings must precede their stock-preserved cell closures.
- Do not require Mekanism advanced circuits for the first usable ME network; digital logistics must exist before the nuclear tier.

### 3. `mekanism_pre_nuclear_machine_chain`

Outputs and installed source recipe IDs:

| Output | Installed recipe ID |
|---|---|
| `mekanism:chemical_infuser` | `mekanism:chemical_infuser` |
| `mekanism:chemical_oxidizer` | `mekanism:chemical_oxidizer` |
| `mekanism:crusher` | `mekanism:crusher` |
| `mekanism:electrolytic_separator` | `mekanism:electrolytic_separator` |
| `mekanism:enrichment_chamber` | `mekanism:enrichment_chamber` |
| `mekanism:osmium_compressor` | `mekanism:osmium_compressor` |
| `mekanism:precision_sawmill` | `mekanism:precision_sawmill` |
| `mekanism:pressurized_reaction_chamber` | `mekanism:pressurized_reaction_chamber` |

Prerequisite capabilities:

- `tfmg:circuit_board`
- `tfmg:steel_casing`
- `tfmg:steel_chemical_vat`
- `tfmg:transformer`
- `mekanism:basic_control_circuit`
- `create:mechanical_pump`

Recommended encased roles:

- `electrochemical_controls` → `createcasing:copper_deployer/press`
- `pressure_and_process_frames` → `createcasing:industrial_iron_press/deployer`
- `precision_sawmill` → `createcasing:brass_deployer/press`

Cycle risks:

- Enrichment chamber must precede the pressurized reaction chamber and purification line.
- Do not use HDPE or a product of the PRC to construct the first PRC.
- Sulfuric acid remains TFMG chemical-vat-owned; no machine recipe may create a second acid route.

### 4. `mekanism_universal_cable_tail`

Outputs and installed source recipe IDs:

| Output | Installed recipe ID |
|---|---|
| `mekanism:advanced_universal_cable` | `mekanism:transmitter/universal_cable/advanced` |
| `mekanism:elite_universal_cable` | `mekanism:transmitter/universal_cable/elite` |
| `mekanism:ultimate_universal_cable` | `mekanism:transmitter/universal_cable/ultimate` |

Prerequisite capabilities:

- `mekanism:basic_universal_cable`
- `tfmg:copper_spool`
- `electroenergetics:extreme_wire`
- `tfmg:sulfur_hexafluoride_bucket`

Recommended encased roles:

- `conductor_lamination` → `createcasing:copper_press`
- `high_voltage_insulation` → `createcasing:industrial_iron_deployer`

Cycle risks:

- Keep the basic cable reachable before the first upgraded-cable recipe.
- Only the Ultimate convergence may require the Extreme wire and SF6 contract; applying both to Advanced would jump directly to the late grid.
- The tier-installer runtime blacklist must cover the managed cable ladder or recipes remain bypassable.

### 5. `ae2_high_energy_spatial_and_mega_core`

Outputs and installed source recipe IDs:

| Output | Installed recipe ID |
|---|---|
| `ae2:cell_workbench` | `ae2:network/blocks/cell_workbench` |
| `ae2:controller` | `ae2:network/blocks/controller` |
| `ae2:export_bus` | `ae2:network/parts/export_bus` |
| `ae2:io_port` | `ae2:network/blocks/io_port` |
| `ae2:me_p2p_tunnel` | `ae2:network/parts/tunnels_me` |
| `ae2:spatial_anchor` | `ae2:network/blocks/spatial_anchor` |
| `ae2:spatial_io_port` | `ae2:network/blocks/spatial_io_port` |
| `ae2:spatial_pylon` | `ae2:network/blocks/spatial_io_pylon` |
| `megacells:mega_crafting_unit` | `megacells:crafting/mega_crafting_unit` |

Prerequisite capabilities:

- `ae2:interface`
- `ae2:terminal`
- `ae2:engineering_processor`
- `ae2:calculation_processor`
- `megacells:accumulation_processor`
- `tfmg:transformer`

Recommended encased roles:

- `network_control_hardware` → `createcasing:brass_deployer/press`
- `high_energy_and_spatial_frames` → `createcasing:industrial_iron_press/deployer`

Cycle risks:

- Controller, IO port, and P2P must not depend on spatial hardware.
- Move spatial transport and the mega core to Nuclear Engineering or Post-Nuclear Megaprojects without moving the first ME network with them.
- Keep bulk cell closures stock-preserved so factory scaling does not require one 5x5 craft per cell.

### 6. `mekanism_nuclear_chemical_and_sps`

Outputs and installed source recipe IDs:

| Output | Installed recipe ID |
|---|---|
| `mekanism:antiprotonic_nucleosynthesizer` | `mekanism:antiprotonic_nucleosynthesizer` |
| `mekanism:chemical_crystallizer` | `mekanism:chemical_crystallizer` |
| `mekanism:chemical_dissolution_chamber` | `mekanism:chemical_dissolution_chamber` |
| `mekanism:chemical_injection_chamber` | `mekanism:chemical_injection_chamber` |
| `mekanism:chemical_washer` | `mekanism:chemical_washer` |
| `mekanism:isotopic_centrifuge` | `mekanism:isotopic_centrifuge` |
| `mekanism:purification_chamber` | `mekanism:purification_chamber` |
| `mekanism:radioactive_waste_barrel` | `mekanism:radioactive_waste_barrel` |
| `mekanism:solar_neutron_activator` | `mekanism:solar_neutron_activator` |
| `mekanism:sps_casing` | `mekanism:sps_casing` |
| `mekanism:sps_port` | `mekanism:sps_port` |
| `mekanism:supercharged_coil` | `mekanism:supercharged_coil` |

Prerequisite capabilities:

- `mekanism:enrichment_chamber`
- `mekanism:chemical_infuser`
- `mekanism:ultimate_control_circuit`
- `tfmg:steel_chemical_vat`
- `tfmg:transformer`
- `ae2:engineering_processor`

Recommended encased roles:

- `chemical_pressure_equipment` → `createcasing:industrial_iron_press/deployer`
- `nuclear_instrumentation` → `createcasing:refined_radiance_press/deployer`

Cycle risks:

- Purification, dissolution, washing, crystallization, and injection must form a forward uranium-processing path, not mutually require later machines.
- The first usable uranium input must exist before any reactor or SPS product is required.
- SPS casing must precede SPS port and supercharged coil; antimatter may only appear after an operational SPS path.

### 7. `bigreactors_bulk_structures_and_controllers`

Outputs and installed source recipe IDs:

| Output | Installed recipe ID |
|---|---|
| `bigreactors:basic_reactorcasing` | `bigreactors:reactor/basic/casing` |
| `bigreactors:basic_reactorcontrolrod` | `bigreactors:reactor/basic/controlrod` |
| `bigreactors:basic_reactorfuelrod` | `bigreactors:reactor/basic/fuelrod_ingots_uranium` |
| `bigreactors:basic_turbinecasing` | `bigreactors:turbine/basic/casing` |
| `bigreactors:basic_turbinecontroller` | `bigreactors:turbine/basic/controller` |
| `bigreactors:basic_turbinerotorbearing` | `bigreactors:turbine/basic/bearing` |
| `bigreactors:basic_turbinerotorblade` | `bigreactors:turbine/basic/blade` |
| `bigreactors:basic_turbinerotorshaft` | `bigreactors:turbine/basic/shaft` |
| `bigreactors:energizercasing` | `bigreactors:energizer/casing` |
| `bigreactors:energizercontroller` | `bigreactors:energizer/controller` |
| `bigreactors:fluidizercasing` | `bigreactors:fluidizer/casing` |
| `bigreactors:fluidizercontroller` | `bigreactors:fluidizer/controller` |
| `bigreactors:reinforced_reactorcasing` | `bigreactors:reactor/reinforced/casing` |
| `bigreactors:reinforced_reactorcontrolrod` | `bigreactors:reactor/reinforced/controlrod` |
| `bigreactors:reinforced_reactorfuelrod` | `bigreactors:reactor/reinforced/fuelrod_ingots_uranium` |
| `bigreactors:reinforced_turbinecasing` | `bigreactors:turbine/reinforced/casing` |
| `bigreactors:reinforced_turbinecontroller` | `bigreactors:turbine/reinforced/controller` |
| `bigreactors:reinforced_turbinerotorbearing` | `bigreactors:turbine/reinforced/bearing` |
| `bigreactors:reinforced_turbinerotorblade` | `bigreactors:turbine/reinforced/blade` |
| `bigreactors:reinforced_turbinerotorshaft` | `bigreactors:turbine/reinforced/shaft` |
| `bigreactors:reprocessorcasing` | `bigreactors:reprocessor/casing` |
| `bigreactors:reprocessorcollector` | `bigreactors:reprocessor/collector` |
| `bigreactors:reprocessorcontroller` | `bigreactors:reprocessor/controller` |
| `bigreactors:reprocessorfluidinjector` | `bigreactors:reprocessor/fluidinjector` |
| `bigreactors:reprocessoroutputport` | `bigreactors:reprocessor/outputport` |
| `bigreactors:reprocessorpowerport` | `bigreactors:reprocessor/powerport` |
| `bigreactors:reprocessorwasteinjector` | `bigreactors:reprocessor/wasteinjector` |

Prerequisite capabilities:

- `tfmg:heavy_plate`
- `tfmg:steel_casing`
- `tfmg:transformer`
- `computercraft:computer_advanced`
- `computercraft:monitor_advanced`
- `mekanism:ingot_uranium`

Recommended encased roles:

- `bulk_casing_and_rotors` → `createcasing:industrial_iron_press/deployer`
- `controllers_and_safety_instrumentation` → `createcasing:brass_deployer plus ComputerCraft subassemblies`

Cycle risks:

- Basic reactor structures cannot consume cyanite, plutonium, reactor waste, or any material produced only after the first reactor runs.
- Bulk casings and rotor parts should be batched from reusable heavy subcomponents; do not charge full control electronics for every wall block.
- Energizer and fluidizer recipes cannot require the fuel product they enable, and reinforced-tier parts must remain downstream of the basic tier.

## Redundant systems

The eight duplicate foundry endpoints are retirement candidates, not immediate deletions. Before retiring them, prove that every unique cast, alloy, and mold route they enable has a TFMG-first canonical path. This prevents the cure from creating a new dead end.

## Complete ID-by-ID classification

### Acceptable stock-derived / utility (27)

| Output | Installed recipe ID | Phase | Decision basis |
|---|---|---|---|
| `create:andesite_funnel` | `create:crafting/logistics/andesite_funnel` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:belt_connector` | `create:crafting/kinetics/belt_connector` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:cart_assembler` | `create:crafting/kinetics/cart_assembler` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:chute` | `create:crafting/kinetics/chute` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:depot` | `create:crafting/kinetics/depot` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:hose_pulley` | `create:crafting/kinetics/hose_pulley` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:item_drain` | `create:crafting/kinetics/item_drain` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:item_vault` | `create:crafting/kinetics/item_vault` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:packager` | `create:crafting/logistics/packager` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:portable_fluid_interface` | `create:crafting/kinetics/portable_fluid_interface` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:portable_storage_interface` | `create:crafting/kinetics/portable_storage_interface` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:spout` | `create:crafting/kinetics/spout` | Mechanical Foundations | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:content_observer` | `create:crafting/logistics/content_observer` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:controls` | `create:crafting/kinetics/controls` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:crushing_wheel` | `create:mechanical_crafting/crushing_wheel` | Steam & Brass | Installed Create mechanical-crafting layout is already a legible machine recipe and is the snapshot's only non-generic automatic 5x5 layout. |
| `create:mechanical_arm` | `create:crafting/kinetics/mechanical_arm` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:pulse_extender` | `create:crafting/logistics/pulse_extender` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:pulse_repeater` | `create:crafting/logistics/pulse_repeater` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:rotation_speed_controller` | `create:crafting/kinetics/rotation_speed_controller` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:schedule` | `create:crafting/kinetics/schedule` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:steam_whistle` | `create:crafting/kinetics/steam_whistle` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:stockpile_switch` | `create:crafting/logistics/stockpile_switch` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:track_observer` | `create:crafting/kinetics/track_observer` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:track_signal` | `create:crafting/kinetics/track_signal` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `create:track_station` | `create:crafting/kinetics/track_station` | Steam & Brass | Stock-scale Create utility recipe is legible, phase-appropriate, and has no automatic 5x5 gate ring. |
| `tfmg:cast_iron_frame` | `tfmg:crafting/materials/cast_iron_frame` | Steel & Petroleum | Canonical TFMG material conversion yields four reusable cast-iron frames at stock scale without an injected gate ring. |
| `tfmg:copper_spool` | `tfmg:copper_spool` | Electrical Manufacturing | Canonical TFMG-first bulk electrical component; the stock wire winding already depends on the source-owned empty spool. |

### Needs source-owned redesign (81)

| Output | Installed recipe ID | Phase | Decision basis |
|---|---|---|---|
| `tfmg:centrifuge` | `tfmg:crafting/materials/centrifuge` | Steel & Petroleum | Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies. |
| `tfmg:diesel_engine_cylinder` | `tfmg:engine_cylinder` | Steel & Petroleum | Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies. |
| `tfmg:engine_cylinder` | `tfmg:engine_cylinder_spark_plug` | Steel & Petroleum | Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies. |
| `createaddition:digital_adapter` | `createaddition:crafting/digital_adapter` | Electrical Manufacturing | Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies. |
| `createaddition:portable_energy_interface` | `createaddition:crafting/portable_energy_interface` | Electrical Manufacturing | Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies. |
| `tfmg:electrode_holder` | `tfmg:crafting/materials/electrode_holder` | Electrical Manufacturing | Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies. |
| `tfmg:transformer` | `tfmg:crafting/materials/transformer` | Electrical Manufacturing | Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies. |
| `tfmg:voltage_observer` | `tfmg:crafting/materials/voltage_observer` | Electrical Manufacturing | Hand-author a TFMG-first manufacturing sequence with a meaningful Copper, Brass, or Industrial-Iron environment and reusable subassemblies. |
| `ae2:energy_acceptor` | `ae2:network/blocks/energy_energy_acceptor` | Digital Logistics | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:import_bus` | `ae2:network/parts/import_bus` | Digital Logistics | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:interface` | `ae2:network/blocks/interfaces_interface` | Digital Logistics | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:item_cell_housing` | `ae2:network/cells/item_cell_housing` | Digital Logistics | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:molecular_assembler` | `ae2:network/crafting/molecular_assembler` | Digital Logistics | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:terminal` | `ae2:network/parts/terminals` | Digital Logistics | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `appmek:chemical_cell_housing` | `appmek:chemical_cell_housing` | Digital Logistics | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:pattern_provider` | `ae2:network/blocks/pattern_providers_interface` | Mekanized Industry | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `mekanism:advanced_universal_cable` | `mekanism:transmitter/universal_cable/advanced` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:chemical_infuser` | `mekanism:chemical_infuser` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:chemical_oxidizer` | `mekanism:chemical_oxidizer` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:crusher` | `mekanism:crusher` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:electrolytic_separator` | `mekanism:electrolytic_separator` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:enrichment_chamber` | `mekanism:enrichment_chamber` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:osmium_compressor` | `mekanism:osmium_compressor` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:precision_sawmill` | `mekanism:precision_sawmill` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:pressurized_reaction_chamber` | `mekanism:pressurized_reaction_chamber` | Mekanized Industry | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `advancedperipherals:block_reader` | `advancedperipherals:block_reader` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `advancedperipherals:colony_integrator` | `advancedperipherals:colony_integrator` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `advancedperipherals:energy_detector` | `advancedperipherals:energy_detector` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `advancedperipherals:inventory_manager` | `advancedperipherals:inventory_manager` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `advancedperipherals:me_bridge` | `advancedperipherals:me_bridge` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `advancedperipherals:peripheral_casing` | `advancedperipherals:peripheral_casing` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:cell_workbench` | `ae2:network/blocks/cell_workbench` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:controller` | `ae2:network/blocks/controller` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:export_bus` | `ae2:network/parts/export_bus` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:io_port` | `ae2:network/blocks/io_port` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:me_p2p_tunnel` | `ae2:network/parts/tunnels_me` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:spatial_anchor` | `ae2:network/blocks/spatial_anchor` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:spatial_io_port` | `ae2:network/blocks/spatial_io_port` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `ae2:spatial_pylon` | `ae2:network/blocks/spatial_io_pylon` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `megacells:mega_crafting_unit` | `megacells:crafting/mega_crafting_unit` | High-Energy Grid | Hand-author the digital device around TFMG boards and the appropriate AE processor; remove generic Mekanism/AE gate rings and keep the first useful ME network pre-nuclear. |
| `mekanism:elite_universal_cable` | `mekanism:transmitter/universal_cable/elite` | High-Energy Grid | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:ultimate_universal_cable` | `mekanism:transmitter/universal_cable/ultimate` | High-Energy Grid | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `bigreactors:basic_reactorcasing` | `bigreactors:reactor/basic/casing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:basic_reactorcontrolrod` | `bigreactors:reactor/basic/controlrod` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:basic_reactorfuelrod` | `bigreactors:reactor/basic/fuelrod_ingots_uranium` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:basic_turbinecasing` | `bigreactors:turbine/basic/casing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:basic_turbinecontroller` | `bigreactors:turbine/basic/controller` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:basic_turbinerotorbearing` | `bigreactors:turbine/basic/bearing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:basic_turbinerotorblade` | `bigreactors:turbine/basic/blade` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:basic_turbinerotorshaft` | `bigreactors:turbine/basic/shaft` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:energizercasing` | `bigreactors:energizer/casing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:energizercontroller` | `bigreactors:energizer/controller` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:fluidizercasing` | `bigreactors:fluidizer/casing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:fluidizercontroller` | `bigreactors:fluidizer/controller` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reinforced_reactorcasing` | `bigreactors:reactor/reinforced/casing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reinforced_reactorcontrolrod` | `bigreactors:reactor/reinforced/controlrod` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reinforced_reactorfuelrod` | `bigreactors:reactor/reinforced/fuelrod_ingots_uranium` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reinforced_turbinecasing` | `bigreactors:turbine/reinforced/casing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reinforced_turbinecontroller` | `bigreactors:turbine/reinforced/controller` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reinforced_turbinerotorbearing` | `bigreactors:turbine/reinforced/bearing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reinforced_turbinerotorblade` | `bigreactors:turbine/reinforced/blade` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reinforced_turbinerotorshaft` | `bigreactors:turbine/reinforced/shaft` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reprocessorcasing` | `bigreactors:reprocessor/casing` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reprocessorcollector` | `bigreactors:reprocessor/collector` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reprocessorcontroller` | `bigreactors:reprocessor/controller` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reprocessorfluidinjector` | `bigreactors:reprocessor/fluidinjector` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reprocessoroutputport` | `bigreactors:reprocessor/outputport` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reprocessorpowerport` | `bigreactors:reprocessor/powerport` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `bigreactors:reprocessorwasteinjector` | `bigreactors:reprocessor/wasteinjector` | Nuclear Engineering | Hand-author a reusable nuclear structural or controller subassembly; bulk blocks need industrial batching while controllers carry the expensive digital gate. |
| `mekanism:antiprotonic_nucleosynthesizer` | `mekanism:antiprotonic_nucleosynthesizer` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:chemical_crystallizer` | `mekanism:chemical_crystallizer` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:chemical_dissolution_chamber` | `mekanism:chemical_dissolution_chamber` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:chemical_injection_chamber` | `mekanism:chemical_injection_chamber` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:chemical_washer` | `mekanism:chemical_washer` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:isotopic_centrifuge` | `mekanism:isotopic_centrifuge` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:purification_chamber` | `mekanism:purification_chamber` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:radioactive_waste_barrel` | `mekanism:radioactive_waste_barrel` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:solar_neutron_activator` | `mekanism:solar_neutron_activator` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:sps_casing` | `mekanism:sps_casing` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:sps_port` | `mekanism:sps_port` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |
| `mekanism:supercharged_coil` | `mekanism:supercharged_coil` | Nuclear Engineering | Hand-author the machine or transmitter around TFMG electronics, pressure equipment, and a meaningful encased environment; runtime source data is evidence, not a design. |

### Redundant / should retire (8)

| Output | Installed recipe ID | Phase | Decision basis |
|---|---|---|---|
| `createmetallurgy:casting_basin` | `createmetallurgy:crafting/content/casting_basin` | Steel & Petroleum | Create Metallurgy duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route. |
| `createmetallurgy:casting_table` | `createmetallurgy:crafting/content/casting_table` | Steel & Petroleum | Create Metallurgy duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route. |
| `createmetallurgy:foundry_basin` | `createmetallurgy:crafting/content/foundry_basin` | Steel & Petroleum | Create Metallurgy duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route. |
| `createmetallurgy:foundry_lid` | `createmetallurgy:crafting/content/foundry_lid` | Steel & Petroleum | Create Metallurgy duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route. |
| `createmetallurgy:foundry_mixer` | `createmetallurgy:crafting/content/foundry_mixer` | Steel & Petroleum | Create Metallurgy duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route. |
| `modernfoundry:scorched_basin` | `modernfoundry:smeltery/scorched/basin` | Steel & Petroleum | Modern Foundry duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route. |
| `modernfoundry:scorched_drain` | `modernfoundry:smeltery/scorched/drain` | Steel & Petroleum | Modern Foundry duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route. |
| `modernfoundry:scorched_table` | `modernfoundry:smeltery/scorched/table` | Steel & Petroleum | Modern Foundry duplicates the pack's TFMG-first casting/foundry role; retire only after proving every unique output has a canonical TFMG route. |

### Runtime artifact / leave stock (56)

| Output | Installed recipe ID | Phase | Decision basis |
|---|---|---|---|
| `tfmg:cast_iron_truss` | `tfmg:crafting/materials/cast_iron_truss` | Steel & Petroleum | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `tfmg:coal_coke` | `tfmg:crafting/materials/coal_coke` | Steel & Petroleum | Reversible material packing/unpacking is a utility conversion, not a progression gate; preserve the exact stock recipe and audit the underlying material-production path separately. |
| `electroenergetics:double_connector` | `electroenergetics:crafting/double_connector` | Electrical Manufacturing | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `electroenergetics:quad_connector` | `electroenergetics:crafting/quad_connector` | Electrical Manufacturing | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `electroenergetics:triple_connector` | `electroenergetics:crafting/triple_connector` | Electrical Manufacturing | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:1k_crafting_storage` | `ae2:network/crafting/1k_cpu_crafting_storage` | Digital Logistics | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:fluix_glass_cable` | `ae2:network/cables/glass_fluix` | Digital Logistics | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:item_storage_cell_1k` | `ae2:network/cells/item_storage_cell_1k` | Digital Logistics | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:item_storage_cell_4k` | `ae2:network/cells/item_storage_cell_4k` | Digital Logistics | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:storage_bus` | `ae2:network/parts/storage_bus` | Digital Logistics | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `appmek:chemical_storage_cell_1k` | `appmek:chemical_storage_cell_1k` | Digital Logistics | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `appmek:chemical_storage_cell_4k` | `appmek:chemical_storage_cell_4k` | Digital Logistics | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:16k_crafting_storage` | `ae2:network/crafting/16k_cpu_crafting_storage` | Mekanized Industry | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:4k_crafting_storage` | `ae2:network/crafting/4k_cpu_crafting_storage` | Mekanized Industry | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `appmek:chemical_storage_cell_16k` | `appmek:chemical_storage_cell_16k` | Mekanized Industry | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `appmek:chemical_storage_cell_64k` | `appmek:chemical_storage_cell_64k` | Mekanized Industry | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `mekanism:advanced_tier_installer` | `mekanism:tier_installer/advanced` | Mekanized Industry | Tier installer is a general runtime utility; preserve its exact stock recipe and enforce managed factory/cube/transmitter ladders with the Mekanism installer blacklist. |
| `mekanism:basic_tier_installer` | `mekanism:tier_installer/basic` | Mekanized Industry | Tier installer is a general runtime utility; preserve its exact stock recipe and enforce managed factory/cube/transmitter ladders with the Mekanism installer blacklist. |
| `mekanism:hdpe_rod` | `mekanism:hdpe_rod` | Mekanized Industry | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `mekanism:hdpe_stick` | `mekanism:hdpe_stick` | Mekanized Industry | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `ae2:cable_interface` | `ae2:network/blocks/interfaces_interface_part` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:crafting_card` | `ae2:materials/cardcrafting` | High-Energy Grid | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `ae2:dense_energy_cell` | `ae2:network/blocks/energy_dense_energy_cell` | High-Energy Grid | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `ae2:fluid_storage_cell_256k` | `ae2:network/cells/fluid_storage_cell_256k` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:fluix_smart_cable` | `ae2:network/cables/smart_fluix` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:fluix_smart_dense_cable` | `ae2:network/cables/dense_smart_fluix` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:item_storage_cell_16k` | `ae2:network/cells/item_storage_cell_16k` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:item_storage_cell_256k` | `ae2:network/cells/item_storage_cell_256k` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:item_storage_cell_64k` | `ae2:network/cells/item_storage_cell_64k` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:spatial_storage_cell_128` | `ae2:network/cells/spatial_storage_cell_128_cubed` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:spatial_storage_cell_16` | `ae2:network/cells/spatial_storage_cell_16_cubed` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `ae2:spatial_storage_cell_2` | `ae2:network/cells/spatial_storage_cell_2_cubed` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `megacells:1m_crafting_storage` | `megacells:crafting/1m_crafting_storage` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `megacells:4m_crafting_storage` | `megacells:crafting/4m_crafting_storage` | High-Energy Grid | Bulk network closure or conductor conversion should inherit difficulty from its components; preserve the exact stock recipe instead of charging a per-item 5x5 gate ring. |
| `megacells:mega_crafting_accelerator` | `megacells:crafting/mega_crafting_accelerator` | High-Energy Grid | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `megacells:mega_pattern_provider` | `megacells:network/mega_pattern_provider` | High-Energy Grid | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `mekanism:elite_tier_installer` | `mekanism:tier_installer/elite` | High-Energy Grid | Tier installer is a general runtime utility; preserve its exact stock recipe and enforce managed factory/cube/transmitter ladders with the Mekanism installer blacklist. |
| `mekanism:hdpe_elytra` | `mekanism:hdpe_elytra` | High-Energy Grid | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `mekanism:ultimate_tier_installer` | `mekanism:tier_installer/ultimate` | High-Energy Grid | Tier installer is a general runtime utility; preserve its exact stock recipe and enforce managed factory/cube/transmitter ladders with the Mekanism installer blacklist. |
| `bigreactors:basic_reactorglass` | `bigreactors:reactor/basic/glass` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:basic_reactorsolidaccessport` | `bigreactors:reactor/basic/solidaccessport` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorchargingportfe` | `bigreactors:reactor/reinforced/chargingfe` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorfluidaccessport` | `bigreactors:reactor/reinforced/fluidaccessport` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorfluidport_forge_active` | `bigreactors:reactor/reinforced/activefluidport_forge` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorfluidport_forge_passive` | `bigreactors:reactor/reinforced/passivefluidport_forge` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorfluidport_mekanism_passive` | `bigreactors:reactor/reinforced/passivefluidport_mekanism` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorglass` | `bigreactors:reactor/reinforced/glass` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorpowertapfe_active` | `bigreactors:reactor/reinforced/activetap_fe` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorpowertapfe_passive` | `bigreactors:reactor/reinforced/passivetap_fe` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorredstoneport` | `bigreactors:reactor/reinforced/redstoneport` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reinforced_reactorsolidaccessport` | `bigreactors:reactor/reinforced/solidaccessport` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:reprocessorglass` | `bigreactors:reprocessor/glass` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `bigreactors:yellorium_block` | `bigreactors:crafting/yellorium_component_to_storage` | Nuclear Engineering | Reversible material packing/unpacking is a utility conversion, not a progression gate; preserve the exact stock recipe and audit the underlying material-production path separately. |
| `er2create:reinforced_reactordisplaysource` | `er2create:reactor/reinforced/diplaysource` | Nuclear Engineering | Compatibility or final-form utility recipe should remain exact stock once its prerequisite machine/component is genuinely gated. |
| `mekanism:block_raw_uranium` | `mekanism:processing/uranium/raw_storage_blocks/from_raw` | Nuclear Engineering | Reversible material packing/unpacking is a utility conversion, not a progression gate; preserve the exact stock recipe and audit the underlying material-production path separately. |
| `mekanism:nugget_uranium` | `mekanism:processing/uranium/nugget/from_ingot` | Nuclear Engineering | Reversible material packing/unpacking is a utility conversion, not a progression gate; preserve the exact stock recipe and audit the underlying material-production path separately. |

## Validation boundary

The audit is pinned to SHA-256 `548ADCDB80947B64B57B539E1314C195C2C18BCC07AFE164595C4B7E7ABEFEA6` for `managed.json` and `4BBC6310A29D2FA839F08D6D73452FA4224B728A6285234707C7F1F746D42CE9` for `report.json`. If either snapshot changes, regenerate and review this audit instead of silently carrying classifications forward.
