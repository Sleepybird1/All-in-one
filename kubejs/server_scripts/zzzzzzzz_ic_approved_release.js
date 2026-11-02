// Approved output ownership: remove old routes BEFORE adding every approved alternative.
ServerEvents.recipes(event => {
  event.remove({output: "ad_astra:airlock"})
  event.remove({output: "ad_astra:cable_duct"})
  event.remove({output: "ad_astra:calorite_plate"})
  event.remove({output: "ad_astra:calorite_tank"})
  event.remove({output: "ad_astra:cryo_freezer"})
  event.remove({output: "ad_astra:desh_cable"})
  event.remove({output: "ad_astra:desh_fluid_pipe"})
  event.remove({output: "ad_astra:desh_plate"})
  event.remove({output: "ad_astra:desh_tank"})
  event.remove({output: "ad_astra:engine_frame"})
  event.remove({output: "ad_astra:etrionic_capacitor"})
  event.remove({output: "ad_astra:fluid_pipe_duct"})
  event.remove({output: "ad_astra:gravity_normalizer"})
  event.remove({output: "ad_astra:large_gas_tank"})
  event.remove({output: "ad_astra:netherite_space_boots"})
  event.remove({output: "ad_astra:netherite_space_helmet"})
  event.remove({output: "ad_astra:netherite_space_pants"})
  event.remove({output: "ad_astra:netherite_space_suit"})
  event.remove({output: "ad_astra:ostrum_fluid_pipe"})
  event.remove({output: "ad_astra:ostrum_plate"})
  event.remove({output: "ad_astra:ostrum_tank"})
  event.remove({output: "ad_astra:oxygen_distributor"})
  event.remove({output: "ad_astra:oxygen_gear"})
  event.remove({output: "ad_astra:oxygen_loader"})
  event.remove({output: "ad_astra:oxygen_sensor"})
  event.remove({output: "ad_astra:photovoltaic_etrium_cell"})
  event.remove({output: "ad_astra:radio"})
  event.remove({output: "ad_astra:rocket_fin"})
  event.remove({output: "ad_astra:rocket_nose_cone"})
  event.remove({output: "ad_astra:solar_panel"})
  event.remove({output: "ad_astra:steel_cable"})
  event.remove({output: "ad_astra:steel_engine"})
  event.remove({output: "ad_astra:steel_panel"})
  event.remove({output: "ad_astra:steel_plating"})
  event.remove({output: "ad_astra:steel_tank"})
  event.remove({output: "ad_astra:tier_1_rover"})
  event.remove({output: "ad_astra:vent"})
  event.remove({output: "advanced_ae:data_entangler"})
  event.remove({output: "advanced_ae:printed_quantum_processor"})
  event.remove({output: "advanced_ae:quantum_accelerator"})
  event.remove({output: "advanced_ae:quantum_core"})
  event.remove({output: "advanced_ae:quantum_crafter"})
  event.remove({output: "advanced_ae:quantum_multi_threader"})
  event.remove({output: "advanced_ae:quantum_processor"})
  event.remove({output: "advanced_ae:quantum_storage_component"})
  event.remove({output: "advanced_ae:quantum_structure"})
  event.remove({output: "advanced_ae:quantum_unit"})
  event.remove({output: "advanced_ae:reaction_chamber"})
  event.remove({output: "advancedperipherals:block_reader"})
  event.remove({output: "advancedperipherals:chat_box"})
  event.remove({output: "advancedperipherals:chunk_controller"})
  event.remove({output: "advancedperipherals:colony_integrator"})
  event.remove({output: "advancedperipherals:energy_detector"})
  event.remove({output: "advancedperipherals:environment_detector"})
  event.remove({output: "advancedperipherals:geo_scanner"})
  event.remove({output: "advancedperipherals:inventory_manager"})
  event.remove({output: "advancedperipherals:me_bridge"})
  event.remove({output: "advancedperipherals:memory_card"})
  event.remove({output: "advancedperipherals:nbt_storage"})
  event.remove({output: "advancedperipherals:overpowered_end_automata_core"})
  event.remove({output: "advancedperipherals:overpowered_husbandry_automata_core"})
  event.remove({output: "advancedperipherals:peripheral_casing"})
  event.remove({output: "advancedperipherals:player_detector"})
  event.remove({output: "advancedperipherals:weak_automata_core"})
  event.remove({output: "ae2:16k_crafting_storage"})
  event.remove({output: "ae2:1k_crafting_storage"})
  event.remove({output: "ae2:256k_crafting_storage"})
  event.remove({output: "ae2:4k_crafting_storage"})
  event.remove({output: "ae2:64k_crafting_storage"})
  event.remove({output: "ae2:advanced_card"})
  event.remove({output: "ae2:annihilation_core"})
  event.remove({output: "ae2:basic_card"})
  event.remove({output: "ae2:calculation_processor"})
  event.remove({output: "ae2:calculation_processor_press"})
  event.remove({output: "ae2:capacity_card"})
  event.remove({output: "ae2:cell_component_16k"})
  event.remove({output: "ae2:cell_component_1k"})
  event.remove({output: "ae2:cell_component_256k"})
  event.remove({output: "ae2:cell_component_4k"})
  event.remove({output: "ae2:cell_component_64k"})
  event.remove({output: "ae2:cell_workbench"})
  event.remove({output: "ae2:charger"})
  event.remove({output: "ae2:condenser"})
  event.remove({output: "ae2:controller"})
  event.remove({output: "ae2:crafting_card"})
  event.remove({output: "ae2:crafting_terminal"})
  event.remove({output: "ae2:crafting_unit"})
  event.remove({output: "ae2:drive"})
  event.remove({output: "ae2:energy_card"})
  event.remove({output: "ae2:engineering_processor"})
  event.remove({output: "ae2:engineering_processor_press"})
  event.remove({output: "ae2:equal_distribution_card"})
  event.remove({output: "ae2:export_bus"})
  event.remove({output: "ae2:fluid_cell_housing"})
  event.remove({output: "ae2:fluid_storage_cell_16k"})
  event.remove({output: "ae2:fluid_storage_cell_1k"})
  event.remove({output: "ae2:fluid_storage_cell_256k"})
  event.remove({output: "ae2:fluid_storage_cell_4k"})
  event.remove({output: "ae2:fluid_storage_cell_64k"})
  event.remove({output: "ae2:fluix_glass_cable"})
  event.remove({output: "ae2:fluix_smart_cable"})
  event.remove({output: "ae2:fluix_smart_dense_cable"})
  event.remove({output: "ae2:formation_core"})
  event.remove({output: "ae2:fuzzy_card"})
  event.remove({output: "ae2:import_bus"})
  event.remove({output: "ae2:interface"})
  event.remove({output: "ae2:inverter_card"})
  event.remove({output: "ae2:io_port"})
  event.remove({output: "ae2:item_cell_housing"})
  event.remove({output: "ae2:item_storage_cell_16k"})
  event.remove({output: "ae2:item_storage_cell_1k"})
  event.remove({output: "ae2:item_storage_cell_256k"})
  event.remove({output: "ae2:item_storage_cell_4k"})
  event.remove({output: "ae2:item_storage_cell_64k"})
  event.remove({output: "ae2:logic_processor"})
  event.remove({output: "ae2:logic_processor_press"})
  event.remove({output: "ae2:me_p2p_tunnel"})
  event.remove({output: "ae2:molecular_assembler"})
  event.remove({output: "ae2:pattern_access_terminal"})
  event.remove({output: "ae2:pattern_encoding_terminal"})
  event.remove({output: "ae2:pattern_provider"})
  event.remove({output: "ae2:printed_calculation_processor"})
  event.remove({output: "ae2:printed_engineering_processor"})
  event.remove({output: "ae2:printed_logic_processor"})
  event.remove({output: "ae2:printed_silicon"})
  event.remove({output: "ae2:quantum_entangled_singularity"})
  event.remove({output: "ae2:silicon_press"})
  event.remove({output: "ae2:spatial_anchor"})
  event.remove({output: "ae2:spatial_io_port"})
  event.remove({output: "ae2:spatial_pylon"})
  event.remove({output: "ae2:speed_card"})
  event.remove({output: "ae2:terminal"})
  event.remove({output: "ae2:void_card"})
  event.remove({output: "ae2:wireless_access_point"})
  event.remove({output: "aeronautics:gyroscopic_propeller_bearing"})
  event.remove({output: "allthemodium:allthemodium_plate"})
  event.remove({output: "allthemodium:unobtainium_plate"})
  event.remove({output: "allthemodium:vibranium_plate"})
  event.remove({output: "appliedcreate:advanced_stress_circuit_board"})
  event.remove({output: "appliedcreate:advanced_stress_processor"})
  event.remove({output: "appliedcreate:andesite_stress_cell_housing"})
  event.remove({output: "appliedcreate:brass_stress_cell_housing"})
  event.remove({output: "appliedcreate:kinetic_energy_acceptor"})
  event.remove({output: "appliedcreate:me_gearbox"})
  event.remove({output: "appliedcreate:stress_circuit_board"})
  event.remove({output: "appliedcreate:stress_processor"})
  event.remove({output: "appliedcreate:stress_storage_cell_16k"})
  event.remove({output: "appliedcreate:stress_storage_cell_16m"})
  event.remove({output: "appliedcreate:stress_storage_cell_1k"})
  event.remove({output: "appliedcreate:stress_storage_cell_1m"})
  event.remove({output: "appliedcreate:stress_storage_cell_256k"})
  event.remove({output: "appliedcreate:stress_storage_cell_256m"})
  event.remove({output: "appliedcreate:stress_storage_cell_4k"})
  event.remove({output: "appliedcreate:stress_storage_cell_4m"})
  event.remove({output: "appliedcreate:stress_storage_cell_64k"})
  event.remove({output: "appliedcreate:stress_storage_cell_64m"})
  event.remove({output: "appliedcreate:stress_storage_component_16k"})
  event.remove({output: "appliedcreate:stress_storage_component_16m"})
  event.remove({output: "appliedcreate:stress_storage_component_1k"})
  event.remove({output: "appliedcreate:stress_storage_component_1m"})
  event.remove({output: "appliedcreate:stress_storage_component_256k"})
  event.remove({output: "appliedcreate:stress_storage_component_256m"})
  event.remove({output: "appliedcreate:stress_storage_component_4k"})
  event.remove({output: "appliedcreate:stress_storage_component_4m"})
  event.remove({output: "appliedcreate:stress_storage_component_64k"})
  event.remove({output: "appliedcreate:stress_storage_component_64m"})
  event.remove({output: "appmek:chemical_cell_housing"})
  event.remove({output: "bigreactors:basic_reactorredstoneport"})
  event.remove({output: "bigreactors:basic_turbinerotorblade"})
  event.remove({output: "bigreactors:basic_turbinerotorshaft"})
  event.remove({output: "bigreactors:energizercasing"})
  event.remove({output: "bigreactors:energizercell"})
  event.remove({output: "bigreactors:energizerchargingport_fe"})
  event.remove({output: "bigreactors:energizercomputerport"})
  event.remove({output: "bigreactors:energizerpowerport_fe"})
  event.remove({output: "bigreactors:energizerpowerport_fe_active"})
  event.remove({output: "bigreactors:energycore"})
  event.remove({output: "bigreactors:fluidizercasing"})
  event.remove({output: "bigreactors:fluidizercontroller"})
  event.remove({output: "bigreactors:fluidizerfluidinjector"})
  event.remove({output: "bigreactors:fluidizeroutputport"})
  event.remove({output: "bigreactors:fluidizerpowerport"})
  event.remove({output: "bigreactors:fluidizersolidinjector"})
  event.remove({output: "bigreactors:reinforced_turbinecasing"})
  event.remove({output: "bigreactors:reinforced_turbinerotorbearing"})
  event.remove({output: "bigreactors:reinforced_turbinerotorblade"})
  event.remove({output: "bigreactors:reinforced_turbinerotorshaft"})
  event.remove({output: "bigreactors:reprocessorcasing"})
  event.remove({output: "bigreactors:reprocessorcollector"})
  event.remove({output: "bigreactors:reprocessorcontroller"})
  event.remove({output: "bigreactors:reprocessorfluidinjector"})
  event.remove({output: "bigreactors:reprocessoroutputport"})
  event.remove({output: "bigreactors:reprocessorpowerport"})
  event.remove({output: "bigreactors:reprocessorwasteinjector"})
  event.remove({output: "colony4cc:colony_peripheral"})
  event.remove({output: "colony4cc:colony_wireless_normal"})
  event.remove({output: "colony4cc:rgb_charge"})
  event.remove({output: "computercraft:cable"})
  event.remove({output: "computercraft:computer_advanced"})
  event.remove({output: "computercraft:computer_normal"})
  event.remove({output: "computercraft:disk"})
  event.remove({output: "computercraft:disk_drive"})
  event.remove({output: "computercraft:monitor_advanced"})
  event.remove({output: "computercraft:monitor_normal"})
  event.remove({output: "computercraft:pocket_computer_advanced"})
  event.remove({output: "computercraft:pocket_computer_normal"})
  event.remove({output: "computercraft:printer"})
  event.remove({output: "computercraft:redstone_relay"})
  event.remove({output: "computercraft:speaker"})
  event.remove({output: "computercraft:turtle_advanced"})
  event.remove({output: "computercraft:turtle_normal"})
  event.remove({output: "computercraft:wired_modem"})
  event.remove({output: "computercraft:wireless_modem_advanced"})
  event.remove({output: "computercraft:wireless_modem_normal"})
  event.remove({output: "cosmowarp:crystal_driver"})
  event.remove({output: "cosmowarp:memory_card"})
  event.remove({output: "cosmowarp:warp_crystal"})
  event.remove({output: "cosmowarp:warp_drive"})
  event.remove({output: "create:chromatic_compound"})
  event.remove({output: "create:display_board"})
  event.remove({output: "create:factory_gauge"})
  event.remove({output: "create:package_frogport"})
  event.remove({output: "create:redstone_requester"})
  event.remove({output: "create:refined_radiance"})
  event.remove({output: "create:refined_radiance_casing"})
  event.remove({output: "create:shadow_steel_casing"})
  event.remove({output: "create_aeronautics_automated_logistics:ship_transponder"})
  event.remove({output: "create_connected:centrifugal_clutch"})
  event.remove({output: "create_connected:control_chip"})
  event.remove({output: "create_connected:dashboard"})
  event.remove({output: "create_connected:empty_fan_catalyst"})
  event.remove({output: "create_connected:freewheel_clutch"})
  event.remove({output: "create_connected:inventory_access_port"})
  event.remove({output: "create_connected:inventory_bridge"})
  event.remove({output: "create_connected:inverted_clutch"})
  event.remove({output: "create_connected:inverted_gearshift"})
  event.remove({output: "create_connected:kinetic_battery"})
  event.remove({output: "create_connected:kinetic_bridge"})
  event.remove({output: "create_connected:linked_transmitter"})
  event.remove({output: "create_connected:overstress_clutch"})
  event.remove({output: "create_connected:redstone_link_wildcard"})
  event.remove({output: "create_connected:shear_pin"})
  event.remove({output: "create_connected:vertical_brass_gearbox"})
  event.remove({output: "create_connected:vertical_parallel_gearbox"})
  event.remove({output: "create_connected:vertical_six_way_gearbox"})
  event.remove({output: "create_enchantment_industry:blaze_enchanter"})
  event.remove({output: "create_enchantment_industry:blaze_forger"})
  event.remove({output: "create_enchantment_industry:classic_blaze_enchanter"})
  event.remove({output: "create_enchantment_industry:enchanting_template"})
  event.remove({output: "create_enchantment_industry:experience_hatch"})
  event.remove({output: "create_enchantment_industry:printer"})
  event.remove({output: "create_enchantment_industry:super_enchanting_template"})
  event.remove({output: "createaddition:alternator"})
  event.remove({output: "createaddition:connector"})
  event.remove({output: "createaddition:digital_adapter"})
  event.remove({output: "createaddition:large_connector"})
  event.remove({output: "createaddition:redstone_relay"})
  event.remove({output: "createaddition:small_light_connector"})
  event.remove({output: "createaddition:tesla_coil"})
  event.remove({output: "createappliedkinetics:me_proxy"})
  event.remove({output: "createbigcannons:steel_sliding_breechblock"})
  event.remove({output: "createcasing:brass_deployer"})
  event.remove({output: "createcasing:brass_depot"})
  event.remove({output: "createcasing:brass_encased_fan"})
  event.remove({output: "createcasing:brass_mechanical_drill"})
  event.remove({output: "createcasing:brass_mechanical_saw"})
  event.remove({output: "createcasing:brass_mixer"})
  event.remove({output: "createcasing:brass_press"})
  event.remove({output: "createcasing:copper_depot"})
  event.remove({output: "createcasing:copper_encased_fan"})
  event.remove({output: "createcasing:copper_mechanical_drill"})
  event.remove({output: "createcasing:copper_mechanical_saw"})
  event.remove({output: "createcasing:copper_mixer"})
  event.remove({output: "createcasing:industrial_iron_deployer"})
  event.remove({output: "createcasing:industrial_iron_encased_fan"})
  event.remove({output: "createcasing:industrial_iron_mechanical_drill"})
  event.remove({output: "createcasing:industrial_iron_mixer"})
  event.remove({output: "createcasing:railway_depot"})
  event.remove({output: "createcasing:railway_encased_fan"})
  event.remove({output: "createcasing:railway_mechanical_drill"})
  event.remove({output: "createcasing:railway_mechanical_saw"})
  event.remove({output: "createcasing:railway_mixer"})
  event.remove({output: "createcasing:refined_radiance_deployer"})
  event.remove({output: "createcasing:refined_radiance_depot"})
  event.remove({output: "createcasing:refined_radiance_encased_fan"})
  event.remove({output: "createcasing:refined_radiance_mechanical_drill"})
  event.remove({output: "createcasing:refined_radiance_mechanical_saw"})
  event.remove({output: "createcasing:refined_radiance_mixer"})
  event.remove({output: "createcasing:refined_radiance_press"})
  event.remove({output: "createcasing:shadow_steel_mechanical_saw"})
  event.remove({output: "createcasing:shadow_steel_mixer"})
  event.remove({output: "createcasing:weathered_iron_depot"})
  event.remove({output: "createcasing:weathered_iron_encased_fan"})
  event.remove({output: "createcasing:weathered_iron_mechanical_drill"})
  event.remove({output: "createcasing:weathered_iron_mechanical_harvester"})
  event.remove({output: "createcasing:weathered_iron_mechanical_plough"})
  event.remove({output: "createdieselgenerators:bulk_fermenter"})
  event.remove({output: "createdieselgenerators:burner"})
  event.remove({output: "createdieselgenerators:canister"})
  event.remove({output: "createdieselgenerators:diesel_engine"})
  event.remove({output: "createdieselgenerators:engine_piston"})
  event.remove({output: "createdieselgenerators:engine_silencer"})
  event.remove({output: "createdieselgenerators:engine_turbocharger"})
  event.remove({output: "createdieselgenerators:huge_diesel_engine"})
  event.remove({output: "createdieselgenerators:large_diesel_engine"})
  event.remove({output: "createdieselgenerators:oil_barrel"})
  event.remove({output: "createfactorycontroller:factory_controller"})
  event.remove({output: "createmechanisms:advanced_precision_mechanism"})
  event.remove({output: "createmechanisms:advanced_storage_mechanism"})
  event.remove({output: "createmechanisms:basic_energy_mechanism"})
  event.remove({output: "createmechanisms:computing_mechanism"})
  event.remove({output: "createmechanisms:logic_mechanism"})
  event.remove({output: "createmechanisms:nuclear_mechanism"})
  event.remove({output: "createmechanisms:redstone_mechanism"})
  event.remove({output: "createmechanisms:rubber_mechanism"})
  event.remove({output: "createmechanisms:storage_mechanism"})
  event.remove({output: "createmechanisms:uranium_mechanism"})
  event.remove({output: "createmechanisms:wooden_mechanism"})
  event.remove({output: "createmechanisms:zinc_mechanism"})
  event.remove({output: "createmetallurgy:casting_basin"})
  event.remove({output: "createmetallurgy:casting_table"})
  event.remove({output: "createmetallurgy:faucet"})
  event.remove({output: "createmetallurgy:foundry_basin"})
  event.remove({output: "createmetallurgy:foundry_lid"})
  event.remove({output: "createmetallurgy:gauge_attachment"})
  event.remove({output: "createmetallurgy:ladle_filter"})
  event.remove({output: "electroenergetics:accumulator"})
  event.remove({output: "electroenergetics:alternator_brushes"})
  event.remove({output: "electroenergetics:ammeter"})
  event.remove({output: "electroenergetics:commutator"})
  event.remove({output: "electroenergetics:connector"})
  event.remove({output: "electroenergetics:converter"})
  event.remove({output: "electroenergetics:copper_wire_spool"})
  event.remove({output: "electroenergetics:current_transformer"})
  event.remove({output: "electroenergetics:cut_off_switch"})
  event.remove({output: "electroenergetics:electrical_panel"})
  event.remove({output: "electroenergetics:energy_meter"})
  event.remove({output: "electroenergetics:fuse_holder"})
  event.remove({output: "electroenergetics:glass_insulator_segment"})
  event.remove({output: "electroenergetics:ground_rod"})
  event.remove({output: "electroenergetics:hanging_glass_insulator"})
  event.remove({output: "electroenergetics:heavily_insulated_wire"})
  event.remove({output: "electroenergetics:heavily_insulated_wire_spool"})
  event.remove({output: "electroenergetics:high_voltage_switch"})
  event.remove({output: "electroenergetics:inductor"})
  event.remove({output: "electroenergetics:insulated_wire"})
  event.remove({output: "electroenergetics:miniature_circuit_breaker"})
  event.remove({output: "electroenergetics:pantograph"})
  event.remove({output: "electroenergetics:radiator_panel"})
  event.remove({output: "electroenergetics:rail_contact_shoe"})
  event.remove({output: "electroenergetics:redstone_relay"})
  event.remove({output: "electroenergetics:relay"})
  event.remove({output: "electroenergetics:resistive_heater"})
  event.remove({output: "electroenergetics:resistor"})
  event.remove({output: "electroenergetics:sulfur_hexafluoride_breaker"})
  event.remove({output: "electroenergetics:transformer"})
  event.remove({output: "electroenergetics:tri_polar_energy_meter"})
  event.remove({output: "electroenergetics:variac"})
  event.remove({output: "electroenergetics:voltage_regulator"})
  event.remove({output: "extendedae:assembler_matrix_crafter"})
  event.remove({output: "extendedae:assembler_matrix_frame"})
  event.remove({output: "extendedae:assembler_matrix_glass"})
  event.remove({output: "extendedae:assembler_matrix_pattern"})
  event.remove({output: "extendedae:assembler_matrix_speed"})
  event.remove({output: "extendedae:assembler_matrix_wall"})
  event.remove({output: "extendedae:concurrent_processor"})
  event.remove({output: "extendedae:concurrent_processor_press"})
  event.remove({output: "extendedae:ex_pattern_provider"})
  event.remove({output: "extendedae:machine_frame"})
  event.remove({output: "extendedae:wireless_hub"})
  event.remove({output: "immersiveengineering:plate_electrum"})
  event.remove({output: "immersiveengineering:plate_iron"})
  event.remove({output: "immersiveengineering:plate_nickel"})
  event.remove({output: "immersiveengineering:plate_steel"})
  event.remove({output: "industrial_colonies:interstellar_warp_charge"})
  event.remove({output: "megacells:16m_crafting_storage"})
  event.remove({output: "megacells:1m_crafting_storage"})
  event.remove({output: "megacells:256m_crafting_storage"})
  event.remove({output: "megacells:4m_crafting_storage"})
  event.remove({output: "megacells:64m_crafting_storage"})
  event.remove({output: "megacells:accumulation_processor"})
  event.remove({output: "megacells:accumulation_processor_press"})
  event.remove({output: "megacells:cell_component_16m"})
  event.remove({output: "megacells:cell_component_4m"})
  event.remove({output: "megacells:cell_component_64m"})
  event.remove({output: "megacells:fluid_storage_cell_16m"})
  event.remove({output: "megacells:fluid_storage_cell_1m"})
  event.remove({output: "megacells:fluid_storage_cell_256m"})
  event.remove({output: "megacells:fluid_storage_cell_4m"})
  event.remove({output: "megacells:fluid_storage_cell_64m"})
  event.remove({output: "megacells:item_storage_cell_16m"})
  event.remove({output: "megacells:item_storage_cell_1m"})
  event.remove({output: "megacells:item_storage_cell_256m"})
  event.remove({output: "megacells:item_storage_cell_4m"})
  event.remove({output: "megacells:item_storage_cell_64m"})
  event.remove({output: "megacells:mega_crafting_accelerator"})
  event.remove({output: "megacells:mega_crafting_monitor"})
  event.remove({output: "megacells:mega_crafting_unit"})
  event.remove({output: "megacells:mega_fluid_cell_housing"})
  event.remove({output: "megacells:mega_interface"})
  event.remove({output: "megacells:mega_item_cell_housing"})
  event.remove({output: "megacells:mega_pattern_provider"})
  event.remove({output: "mekanism:advanced_chemical_tank"})
  event.remove({output: "mekanism:advanced_control_circuit"})
  event.remove({output: "mekanism:advanced_energy_cube"})
  event.remove({output: "mekanism:advanced_induction_cell"})
  event.remove({output: "mekanism:advanced_induction_provider"})
  event.remove({output: "mekanism:advanced_pressurized_tube"})
  event.remove({output: "mekanism:advanced_thermodynamic_conductor"})
  event.remove({output: "mekanism:alloy_atomic"})
  event.remove({output: "mekanism:alloy_reinforced"})
  event.remove({output: "mekanism:antiprotonic_nucleosynthesizer"})
  event.remove({output: "mekanism:atomic_disassembler"})
  event.remove({output: "mekanism:basic_bin"})
  event.remove({output: "mekanism:basic_chemical_tank"})
  event.remove({output: "mekanism:basic_control_circuit"})
  event.remove({output: "mekanism:basic_energy_cube"})
  event.remove({output: "mekanism:basic_fluid_tank"})
  event.remove({output: "mekanism:basic_induction_cell"})
  event.remove({output: "mekanism:basic_induction_provider"})
  event.remove({output: "mekanism:basic_pressurized_tube"})
  event.remove({output: "mekanism:basic_thermodynamic_conductor"})
  event.remove({output: "mekanism:boiler_casing"})
  event.remove({output: "mekanism:boiler_valve"})
  event.remove({output: "mekanism:chemical_crystallizer"})
  event.remove({output: "mekanism:chemical_dissolution_chamber"})
  event.remove({output: "mekanism:chemical_infuser"})
  event.remove({output: "mekanism:chemical_injection_chamber"})
  event.remove({output: "mekanism:chemical_oxidizer"})
  event.remove({output: "mekanism:chemical_washer"})
  event.remove({output: "mekanism:configurator"})
  event.remove({output: "mekanism:diversion_transporter"})
  event.remove({output: "mekanism:dust_copper"})
  event.remove({output: "mekanism:dynamic_tank"})
  event.remove({output: "mekanism:dynamic_valve"})
  event.remove({output: "mekanism:electrolytic_core"})
  event.remove({output: "mekanism:electrolytic_separator"})
  event.remove({output: "mekanism:elite_chemical_tank"})
  event.remove({output: "mekanism:elite_control_circuit"})
  event.remove({output: "mekanism:elite_energy_cube"})
  event.remove({output: "mekanism:elite_induction_cell"})
  event.remove({output: "mekanism:elite_induction_provider"})
  event.remove({output: "mekanism:elite_pressurized_tube"})
  event.remove({output: "mekanism:elite_tier_installer"})
  event.remove({output: "mekanism:energy_tablet"})
  event.remove({output: "mekanism:enriched_diamond"})
  event.remove({output: "mekanism:enriched_refined_obsidian"})
  event.remove({output: "mekanism:free_runners"})
  event.remove({output: "mekanism:free_runners_armored"})
  event.remove({output: "mekanism:induction_casing"})
  event.remove({output: "mekanism:induction_port"})
  event.remove({output: "mekanism:isotopic_centrifuge"})
  event.remove({output: "mekanism:jetpack"})
  event.remove({output: "mekanism:laser"})
  event.remove({output: "mekanism:laser_tractor_beam"})
  event.remove({output: "mekanism:module_base"})
  event.remove({output: "mekanism:nutritional_liquifier"})
  event.remove({output: "mekanism:pigment_mixer"})
  event.remove({output: "mekanism:pressure_disperser"})
  event.remove({output: "mekanism:purification_chamber"})
  event.remove({output: "mekanism:quantum_entangloporter"})
  event.remove({output: "mekanism:radioactive_waste_barrel"})
  event.remove({output: "mekanism:resistive_heater"})
  event.remove({output: "mekanism:restrictive_transporter"})
  event.remove({output: "mekanism:rotary_condensentrator"})
  event.remove({output: "mekanism:solar_neutron_activator"})
  event.remove({output: "mekanism:sps_casing"})
  event.remove({output: "mekanism:sps_port"})
  event.remove({output: "mekanism:structural_glass"})
  event.remove({output: "mekanism:supercharged_coil"})
  event.remove({output: "mekanism:superheating_element"})
  event.remove({output: "mekanism:teleportation_core"})
  event.remove({output: "mekanism:thermal_evaporation_block"})
  event.remove({output: "mekanism:thermal_evaporation_controller"})
  event.remove({output: "mekanism:thermal_evaporation_valve"})
  event.remove({output: "mekanism:ultimate_chemical_tank"})
  event.remove({output: "mekanism:ultimate_control_circuit"})
  event.remove({output: "mekanism:ultimate_energy_cube"})
  event.remove({output: "mekanism:ultimate_induction_cell"})
  event.remove({output: "mekanism:ultimate_induction_provider"})
  event.remove({output: "mekanism:ultimate_pressurized_tube"})
  event.remove({output: "mekanism:ultimate_thermodynamic_conductor"})
  event.remove({output: "mekanism:ultimate_tier_installer"})
  event.remove({output: "mekanism:upgrade_anchor"})
  event.remove({output: "mekanism:upgrade_chemical"})
  event.remove({output: "mekanism:upgrade_energy"})
  event.remove({output: "mekanism:upgrade_filter"})
  event.remove({output: "mekanism:upgrade_muffling"})
  event.remove({output: "mekanism:upgrade_speed"})
  event.remove({output: "nuclearcraft:actuator"})
  event.remove({output: "nuclearcraft:assembler"})
  event.remove({output: "nuclearcraft:borax_dust"})
  event.remove({output: "nuclearcraft:centrifuge"})
  event.remove({output: "nuclearcraft:chamber_port"})
  event.remove({output: "nuclearcraft:chamber_terminal"})
  event.remove({output: "nuclearcraft:chemical_reactor"})
  event.remove({output: "nuclearcraft:crystallizer"})
  event.remove({output: "nuclearcraft:decay_hastener"})
  event.remove({output: "nuclearcraft:electrolyzer"})
  event.remove({output: "nuclearcraft:event_horizon_stabilizer"})
  event.remove({output: "nuclearcraft:expl"})
  event.remove({output: "nuclearcraft:extractor"})
  event.remove({output: "nuclearcraft:fission_reactor_casing"})
  event.remove({output: "nuclearcraft:fission_reactor_controller"})
  event.remove({output: "nuclearcraft:fission_reactor_irradiation_chamber"})
  event.remove({output: "nuclearcraft:fission_reactor_port"})
  event.remove({output: "nuclearcraft:fluid_enricher"})
  event.remove({output: "nuclearcraft:fluid_infuser"})
  event.remove({output: "nuclearcraft:fusion_reactor_casing"})
  event.remove({output: "nuclearcraft:fusion_reactor_connector"})
  event.remove({output: "nuclearcraft:fusion_reactor_core"})
  event.remove({output: "nuclearcraft:gas_scrubber"})
  event.remove({output: "nuclearcraft:hard_carbon_dust"})
  event.remove({output: "nuclearcraft:heat_exchanger"})
  event.remove({output: "nuclearcraft:heat_exchanger_casing"})
  event.remove({output: "nuclearcraft:heat_exchanger_controller"})
  event.remove({output: "nuclearcraft:heat_exchanger_radiator"})
  event.remove({output: "nuclearcraft:irradiator"})
  event.remove({output: "nuclearcraft:leacher"})
  event.remove({output: "nuclearcraft:msr_controller"})
  event.remove({output: "nuclearcraft:neutronium_frame"})
  event.remove({output: "nuclearcraft:nitrogen_collector"})
  event.remove({output: "nuclearcraft:photon_concentrator"})
  event.remove({output: "nuclearcraft:pressurizer"})
  event.remove({output: "nuclearcraft:quantum_flux_regulator"})
  event.remove({output: "nuclearcraft:quantum_transformer"})
  event.remove({output: "nuclearcraft:servo"})
  event.remove({output: "nuclearcraft:sic_fiber"})
  event.remove({output: "nuclearcraft:sic_sic_cmc_dust"})
  event.remove({output: "nuclearcraft:sic_sic_cmc_plate"})
  event.remove({output: "nuclearcraft:steam_turbine"})
  event.remove({output: "nuclearcraft:subatomic_liquifier"})
  event.remove({output: "nuclearcraft:supercooler"})
  event.remove({output: "nuclearcraft:tungsten_dust"})
  event.remove({output: "nuclearcraft:turbine_casing"})
  event.remove({output: "nuclearcraft:turbine_controller"})
  event.remove({output: "nuclearcraft:water_collector"})
  event.remove({output: "rocketnautics:booster_thruster"})
  event.remove({output: "rocketnautics:copper_anchor_boots"})
  event.remove({output: "rocketnautics:copper_leg_thrusters"})
  event.remove({output: "rocketnautics:copper_nozzle"})
  event.remove({output: "rocketnautics:engine_nozzle"})
  event.remove({output: "rocketnautics:engine_pipes"})
  event.remove({output: "rocketnautics:hologram_block"})
  event.remove({output: "rocketnautics:hose_anchor"})
  event.remove({output: "rocketnautics:magnetic_stabilizer"})
  event.remove({output: "rocketnautics:rcs_thruster"})
  event.remove({output: "rocketnautics:rocket_thruster"})
  event.remove({output: "rocketnautics:separator"})
  event.remove({output: "rocketnautics:separator_charge"})
  event.remove({output: "rocketnautics:separator_shaft"})
  event.remove({output: "rocketnautics:sputnik"})
  event.remove({output: "rocketnautics:thruster_mount"})
  event.remove({output: "rocketnautics:titanium_nozzle"})
  event.remove({output: "rocketnautics:vector_thruster"})
  event.remove({output: "simulated:altitude_sensor"})
  event.remove({output: "simulated:auger_shaft"})
  event.remove({output: "simulated:directional_linked_receiver"})
  event.remove({output: "simulated:docking_connector"})
  event.remove({output: "simulated:engine_assembly"})
  event.remove({output: "simulated:gimbal_sensor"})
  event.remove({output: "simulated:gyroscopic_mechanism"})
  event.remove({output: "simulated:modulating_linked_receiver"})
  event.remove({output: "simulated:navigation_table"})
  event.remove({output: "simulated:optical_sensor"})
  event.remove({output: "simulated:physics_assembler"})
  event.remove({output: "simulated:redstone_magnet"})
  event.remove({output: "simulated:rope_connector"})
  event.remove({output: "simulated:rope_coupling"})
  event.remove({output: "simulated:spring"})
  event.remove({output: "simulated:throttle_lever"})
  event.remove({output: "simulated:velocity_sensor"})
  event.remove({output: "tfmg:aluminum_cogwheel"})
  event.remove({output: "tfmg:aluminum_fluid_valve"})
  event.remove({output: "tfmg:aluminum_smart_fluid_pipe"})
  event.remove({output: "tfmg:blast_furnace_hatch"})
  event.remove({output: "tfmg:blast_furnace_output"})
  event.remove({output: "tfmg:blast_furnace_reinforcement"})
  event.remove({output: "tfmg:blast_stove"})
  event.remove({output: "tfmg:cable_connector"})
  event.remove({output: "tfmg:cable_tube"})
  event.remove({output: "tfmg:cast_iron_chemical_vat"})
  event.remove({output: "tfmg:cast_iron_fluid_tank"})
  event.remove({output: "tfmg:cast_iron_fluid_valve"})
  event.remove({output: "tfmg:cast_iron_mechanical_pump"})
  event.remove({output: "tfmg:cast_iron_pipe"})
  event.remove({output: "tfmg:cast_iron_sheet"})
  event.remove({output: "tfmg:casting_basin"})
  event.remove({output: "tfmg:coated_circuit_board"})
  event.remove({output: "tfmg:copper_cable_hub"})
  event.remove({output: "tfmg:diesel_engine_cylinder"})
  event.remove({output: "tfmg:electric_diode"})
  event.remove({output: "tfmg:electric_motor"})
  event.remove({output: "tfmg:electrical_switch"})
  event.remove({output: "tfmg:empty_spool"})
  event.remove({output: "tfmg:engine_controller"})
  event.remove({output: "tfmg:engine_cylinder"})
  event.remove({output: "tfmg:engine_gearbox"})
  event.remove({output: "tfmg:fireproof_brick_reinforcement"})
  event.remove({output: "tfmg:fireproof_bricks"})
  event.remove({output: "tfmg:fireproof_chemical_vat"})
  event.remove({output: "tfmg:generator"})
  event.remove({output: "tfmg:heavy_cable_hub"})
  event.remove({output: "tfmg:heavy_plate"})
  event.remove({output: "tfmg:industrial_mixer"})
  event.remove({output: "tfmg:industrial_pipe"})
  event.remove({output: "tfmg:large_aluminum_cogwheel"})
  event.remove({output: "tfmg:large_engine"})
  event.remove({output: "tfmg:large_pumpjack_hammer_connector"})
  event.remove({output: "tfmg:large_pumpjack_hammer_head"})
  event.remove({output: "tfmg:large_pumpjack_hammer_part"})
  event.remove({output: "tfmg:large_switch"})
  event.remove({output: "tfmg:machine_input"})
  event.remove({output: "tfmg:multimeter"})
  event.remove({output: "tfmg:oil_can"})
  event.remove({output: "tfmg:oil_hammer"})
  event.remove({output: "tfmg:plastic_fluid_valve"})
  event.remove({output: "tfmg:plastic_smart_fluid_pipe"})
  event.remove({output: "tfmg:polarizer"})
  event.remove({output: "tfmg:pumpjack_base"})
  event.remove({output: "tfmg:pumpjack_crank"})
  event.remove({output: "tfmg:pumpjack_hammer"})
  event.remove({output: "tfmg:pumpjack_hammer_connector"})
  event.remove({output: "tfmg:pumpjack_hammer_head"})
  event.remove({output: "tfmg:pumpjack_hammer_part"})
  event.remove({output: "tfmg:radial_engine"})
  event.remove({output: "tfmg:regular_engine"})
  event.remove({output: "tfmg:segmented_display"})
  event.remove({output: "tfmg:simple_large_engine"})
  event.remove({output: "tfmg:spark_plug"})
  event.remove({output: "tfmg:steel_cable_hub"})
  event.remove({output: "tfmg:steel_casing"})
  event.remove({output: "tfmg:steel_chemical_vat"})
  event.remove({output: "tfmg:steel_distillation_controller"})
  event.remove({output: "tfmg:steel_distillation_output"})
  event.remove({output: "tfmg:steel_fluid_tank"})
  event.remove({output: "tfmg:steel_fluid_valve"})
  event.remove({output: "tfmg:steel_frame"})
  event.remove({output: "tfmg:steel_gearbox"})
  event.remove({output: "tfmg:steel_mechanical_pump"})
  event.remove({output: "tfmg:steel_pipe"})
  event.remove({output: "tfmg:steel_smart_fluid_pipe"})
  event.remove({output: "tfmg:surface_scanner"})
  event.remove({output: "tfmg:transformer"})
  event.remove({output: "tfmg:transistor_item"})
  event.remove({output: "tfmg:turbine_engine"})
  event.remove({output: "tfmg:voltmeter"})
  event.remove({output: "vsie:computronic_substrate"})
  event.remove({output: "vsie:warp_data_chip"})

  // Pending KubeJS additions are separate from originalRecipes. Apply the same
  // replacement ownership before registering this release's custom recipes.
  var replacementOutputs = ["ad_astra:airlock", "ad_astra:cable_duct", "ad_astra:calorite_plate", "ad_astra:calorite_tank", "ad_astra:cryo_freezer", "ad_astra:desh_cable", "ad_astra:desh_fluid_pipe", "ad_astra:desh_plate", "ad_astra:desh_tank", "ad_astra:engine_frame", "ad_astra:etrionic_capacitor", "ad_astra:fluid_pipe_duct", "ad_astra:gravity_normalizer", "ad_astra:large_gas_tank", "ad_astra:netherite_space_boots", "ad_astra:netherite_space_helmet", "ad_astra:netherite_space_pants", "ad_astra:netherite_space_suit", "ad_astra:ostrum_fluid_pipe", "ad_astra:ostrum_plate", "ad_astra:ostrum_tank", "ad_astra:oxygen_distributor", "ad_astra:oxygen_gear", "ad_astra:oxygen_loader", "ad_astra:oxygen_sensor", "ad_astra:photovoltaic_etrium_cell", "ad_astra:radio", "ad_astra:rocket_fin", "ad_astra:rocket_nose_cone", "ad_astra:solar_panel", "ad_astra:steel_cable", "ad_astra:steel_engine", "ad_astra:steel_panel", "ad_astra:steel_plating", "ad_astra:steel_tank", "ad_astra:tier_1_rover", "ad_astra:vent", "advanced_ae:data_entangler", "advanced_ae:printed_quantum_processor", "advanced_ae:quantum_accelerator", "advanced_ae:quantum_core", "advanced_ae:quantum_crafter", "advanced_ae:quantum_multi_threader", "advanced_ae:quantum_processor", "advanced_ae:quantum_storage_component", "advanced_ae:quantum_structure", "advanced_ae:quantum_unit", "advanced_ae:reaction_chamber", "advancedperipherals:block_reader", "advancedperipherals:chat_box", "advancedperipherals:chunk_controller", "advancedperipherals:colony_integrator", "advancedperipherals:energy_detector", "advancedperipherals:environment_detector", "advancedperipherals:geo_scanner", "advancedperipherals:inventory_manager", "advancedperipherals:me_bridge", "advancedperipherals:memory_card", "advancedperipherals:nbt_storage", "advancedperipherals:overpowered_end_automata_core", "advancedperipherals:overpowered_husbandry_automata_core", "advancedperipherals:peripheral_casing", "advancedperipherals:player_detector", "advancedperipherals:weak_automata_core", "ae2:16k_crafting_storage", "ae2:1k_crafting_storage", "ae2:256k_crafting_storage", "ae2:4k_crafting_storage", "ae2:64k_crafting_storage", "ae2:advanced_card", "ae2:annihilation_core", "ae2:basic_card", "ae2:calculation_processor", "ae2:calculation_processor_press", "ae2:capacity_card", "ae2:cell_component_16k", "ae2:cell_component_1k", "ae2:cell_component_256k", "ae2:cell_component_4k", "ae2:cell_component_64k", "ae2:cell_workbench", "ae2:charger", "ae2:condenser", "ae2:controller", "ae2:crafting_card", "ae2:crafting_terminal", "ae2:crafting_unit", "ae2:drive", "ae2:energy_card", "ae2:engineering_processor", "ae2:engineering_processor_press", "ae2:equal_distribution_card", "ae2:export_bus", "ae2:fluid_cell_housing", "ae2:fluid_storage_cell_16k", "ae2:fluid_storage_cell_1k", "ae2:fluid_storage_cell_256k", "ae2:fluid_storage_cell_4k", "ae2:fluid_storage_cell_64k", "ae2:fluix_glass_cable", "ae2:fluix_smart_cable", "ae2:fluix_smart_dense_cable", "ae2:formation_core", "ae2:fuzzy_card", "ae2:import_bus", "ae2:interface", "ae2:inverter_card", "ae2:io_port", "ae2:item_cell_housing", "ae2:item_storage_cell_16k", "ae2:item_storage_cell_1k", "ae2:item_storage_cell_256k", "ae2:item_storage_cell_4k", "ae2:item_storage_cell_64k", "ae2:logic_processor", "ae2:logic_processor_press", "ae2:me_p2p_tunnel", "ae2:molecular_assembler", "ae2:pattern_access_terminal", "ae2:pattern_encoding_terminal", "ae2:pattern_provider", "ae2:printed_calculation_processor", "ae2:printed_engineering_processor", "ae2:printed_logic_processor", "ae2:printed_silicon", "ae2:quantum_entangled_singularity", "ae2:silicon_press", "ae2:spatial_anchor", "ae2:spatial_io_port", "ae2:spatial_pylon", "ae2:speed_card", "ae2:terminal", "ae2:void_card", "ae2:wireless_access_point", "aeronautics:gyroscopic_propeller_bearing", "allthemodium:allthemodium_plate", "allthemodium:unobtainium_plate", "allthemodium:vibranium_plate", "appliedcreate:advanced_stress_circuit_board", "appliedcreate:advanced_stress_processor", "appliedcreate:andesite_stress_cell_housing", "appliedcreate:brass_stress_cell_housing", "appliedcreate:kinetic_energy_acceptor", "appliedcreate:me_gearbox", "appliedcreate:stress_circuit_board", "appliedcreate:stress_processor", "appliedcreate:stress_storage_cell_16k", "appliedcreate:stress_storage_cell_16m", "appliedcreate:stress_storage_cell_1k", "appliedcreate:stress_storage_cell_1m", "appliedcreate:stress_storage_cell_256k", "appliedcreate:stress_storage_cell_256m", "appliedcreate:stress_storage_cell_4k", "appliedcreate:stress_storage_cell_4m", "appliedcreate:stress_storage_cell_64k", "appliedcreate:stress_storage_cell_64m", "appliedcreate:stress_storage_component_16k", "appliedcreate:stress_storage_component_16m", "appliedcreate:stress_storage_component_1k", "appliedcreate:stress_storage_component_1m", "appliedcreate:stress_storage_component_256k", "appliedcreate:stress_storage_component_256m", "appliedcreate:stress_storage_component_4k", "appliedcreate:stress_storage_component_4m", "appliedcreate:stress_storage_component_64k", "appliedcreate:stress_storage_component_64m", "appmek:chemical_cell_housing", "bigreactors:basic_reactorredstoneport", "bigreactors:basic_turbinerotorblade", "bigreactors:basic_turbinerotorshaft", "bigreactors:energizercasing", "bigreactors:energizercell", "bigreactors:energizerchargingport_fe", "bigreactors:energizercomputerport", "bigreactors:energizerpowerport_fe", "bigreactors:energizerpowerport_fe_active", "bigreactors:energycore", "bigreactors:fluidizercasing", "bigreactors:fluidizercontroller", "bigreactors:fluidizerfluidinjector", "bigreactors:fluidizeroutputport", "bigreactors:fluidizerpowerport", "bigreactors:fluidizersolidinjector", "bigreactors:reinforced_turbinecasing", "bigreactors:reinforced_turbinerotorbearing", "bigreactors:reinforced_turbinerotorblade", "bigreactors:reinforced_turbinerotorshaft", "bigreactors:reprocessorcasing", "bigreactors:reprocessorcollector", "bigreactors:reprocessorcontroller", "bigreactors:reprocessorfluidinjector", "bigreactors:reprocessoroutputport", "bigreactors:reprocessorpowerport", "bigreactors:reprocessorwasteinjector", "colony4cc:colony_peripheral", "colony4cc:colony_wireless_normal", "colony4cc:rgb_charge", "computercraft:cable", "computercraft:computer_advanced", "computercraft:computer_normal", "computercraft:disk", "computercraft:disk_drive", "computercraft:monitor_advanced", "computercraft:monitor_normal", "computercraft:pocket_computer_advanced", "computercraft:pocket_computer_normal", "computercraft:printer", "computercraft:redstone_relay", "computercraft:speaker", "computercraft:turtle_advanced", "computercraft:turtle_normal", "computercraft:wired_modem", "computercraft:wireless_modem_advanced", "computercraft:wireless_modem_normal", "cosmowarp:crystal_driver", "cosmowarp:memory_card", "cosmowarp:warp_crystal", "cosmowarp:warp_drive", "create:chromatic_compound", "create:display_board", "create:factory_gauge", "create:package_frogport", "create:redstone_requester", "create:refined_radiance", "create:refined_radiance_casing", "create:shadow_steel_casing", "create_aeronautics_automated_logistics:ship_transponder", "create_connected:centrifugal_clutch", "create_connected:control_chip", "create_connected:dashboard", "create_connected:empty_fan_catalyst", "create_connected:freewheel_clutch", "create_connected:inventory_access_port", "create_connected:inventory_bridge", "create_connected:inverted_clutch", "create_connected:inverted_gearshift", "create_connected:kinetic_battery", "create_connected:kinetic_bridge", "create_connected:linked_transmitter", "create_connected:overstress_clutch", "create_connected:redstone_link_wildcard", "create_connected:shear_pin", "create_connected:vertical_brass_gearbox", "create_connected:vertical_parallel_gearbox", "create_connected:vertical_six_way_gearbox", "create_enchantment_industry:blaze_enchanter", "create_enchantment_industry:blaze_forger", "create_enchantment_industry:classic_blaze_enchanter", "create_enchantment_industry:enchanting_template", "create_enchantment_industry:experience_hatch", "create_enchantment_industry:printer", "create_enchantment_industry:super_enchanting_template", "createaddition:alternator", "createaddition:connector", "createaddition:digital_adapter", "createaddition:large_connector", "createaddition:redstone_relay", "createaddition:small_light_connector", "createaddition:tesla_coil", "createappliedkinetics:me_proxy", "createbigcannons:steel_sliding_breechblock", "createcasing:brass_deployer", "createcasing:brass_depot", "createcasing:brass_encased_fan", "createcasing:brass_mechanical_drill", "createcasing:brass_mechanical_saw", "createcasing:brass_mixer", "createcasing:brass_press", "createcasing:copper_depot", "createcasing:copper_encased_fan", "createcasing:copper_mechanical_drill", "createcasing:copper_mechanical_saw", "createcasing:copper_mixer", "createcasing:industrial_iron_deployer", "createcasing:industrial_iron_encased_fan", "createcasing:industrial_iron_mechanical_drill", "createcasing:industrial_iron_mixer", "createcasing:railway_depot", "createcasing:railway_encased_fan", "createcasing:railway_mechanical_drill", "createcasing:railway_mechanical_saw", "createcasing:railway_mixer", "createcasing:refined_radiance_deployer", "createcasing:refined_radiance_depot", "createcasing:refined_radiance_encased_fan", "createcasing:refined_radiance_mechanical_drill", "createcasing:refined_radiance_mechanical_saw", "createcasing:refined_radiance_mixer", "createcasing:refined_radiance_press", "createcasing:shadow_steel_mechanical_saw", "createcasing:shadow_steel_mixer", "createcasing:weathered_iron_depot", "createcasing:weathered_iron_encased_fan", "createcasing:weathered_iron_mechanical_drill", "createcasing:weathered_iron_mechanical_harvester", "createcasing:weathered_iron_mechanical_plough", "createdieselgenerators:bulk_fermenter", "createdieselgenerators:burner", "createdieselgenerators:canister", "createdieselgenerators:diesel_engine", "createdieselgenerators:engine_piston", "createdieselgenerators:engine_silencer", "createdieselgenerators:engine_turbocharger", "createdieselgenerators:huge_diesel_engine", "createdieselgenerators:large_diesel_engine", "createdieselgenerators:oil_barrel", "createfactorycontroller:factory_controller", "createmechanisms:advanced_precision_mechanism", "createmechanisms:advanced_storage_mechanism", "createmechanisms:basic_energy_mechanism", "createmechanisms:computing_mechanism", "createmechanisms:logic_mechanism", "createmechanisms:nuclear_mechanism", "createmechanisms:redstone_mechanism", "createmechanisms:rubber_mechanism", "createmechanisms:storage_mechanism", "createmechanisms:uranium_mechanism", "createmechanisms:wooden_mechanism", "createmechanisms:zinc_mechanism", "createmetallurgy:casting_basin", "createmetallurgy:casting_table", "createmetallurgy:faucet", "createmetallurgy:foundry_basin", "createmetallurgy:foundry_lid", "createmetallurgy:gauge_attachment", "createmetallurgy:ladle_filter", "electroenergetics:accumulator", "electroenergetics:alternator_brushes", "electroenergetics:ammeter", "electroenergetics:commutator", "electroenergetics:connector", "electroenergetics:converter", "electroenergetics:copper_wire_spool", "electroenergetics:current_transformer", "electroenergetics:cut_off_switch", "electroenergetics:electrical_panel", "electroenergetics:energy_meter", "electroenergetics:fuse_holder", "electroenergetics:glass_insulator_segment", "electroenergetics:ground_rod", "electroenergetics:hanging_glass_insulator", "electroenergetics:heavily_insulated_wire", "electroenergetics:heavily_insulated_wire_spool", "electroenergetics:high_voltage_switch", "electroenergetics:inductor", "electroenergetics:insulated_wire", "electroenergetics:miniature_circuit_breaker", "electroenergetics:pantograph", "electroenergetics:radiator_panel", "electroenergetics:rail_contact_shoe", "electroenergetics:redstone_relay", "electroenergetics:relay", "electroenergetics:resistive_heater", "electroenergetics:resistor", "electroenergetics:sulfur_hexafluoride_breaker", "electroenergetics:transformer", "electroenergetics:tri_polar_energy_meter", "electroenergetics:variac", "electroenergetics:voltage_regulator", "extendedae:assembler_matrix_crafter", "extendedae:assembler_matrix_frame", "extendedae:assembler_matrix_glass", "extendedae:assembler_matrix_pattern", "extendedae:assembler_matrix_speed", "extendedae:assembler_matrix_wall", "extendedae:concurrent_processor", "extendedae:concurrent_processor_press", "extendedae:ex_pattern_provider", "extendedae:machine_frame", "extendedae:wireless_hub", "immersiveengineering:plate_electrum", "immersiveengineering:plate_iron", "immersiveengineering:plate_nickel", "immersiveengineering:plate_steel", "industrial_colonies:interstellar_warp_charge", "megacells:16m_crafting_storage", "megacells:1m_crafting_storage", "megacells:256m_crafting_storage", "megacells:4m_crafting_storage", "megacells:64m_crafting_storage", "megacells:accumulation_processor", "megacells:accumulation_processor_press", "megacells:cell_component_16m", "megacells:cell_component_4m", "megacells:cell_component_64m", "megacells:fluid_storage_cell_16m", "megacells:fluid_storage_cell_1m", "megacells:fluid_storage_cell_256m", "megacells:fluid_storage_cell_4m", "megacells:fluid_storage_cell_64m", "megacells:item_storage_cell_16m", "megacells:item_storage_cell_1m", "megacells:item_storage_cell_256m", "megacells:item_storage_cell_4m", "megacells:item_storage_cell_64m", "megacells:mega_crafting_accelerator", "megacells:mega_crafting_monitor", "megacells:mega_crafting_unit", "megacells:mega_fluid_cell_housing", "megacells:mega_interface", "megacells:mega_item_cell_housing", "megacells:mega_pattern_provider", "mekanism:advanced_chemical_tank", "mekanism:advanced_control_circuit", "mekanism:advanced_energy_cube", "mekanism:advanced_induction_cell", "mekanism:advanced_induction_provider", "mekanism:advanced_pressurized_tube", "mekanism:advanced_thermodynamic_conductor", "mekanism:alloy_atomic", "mekanism:alloy_reinforced", "mekanism:antiprotonic_nucleosynthesizer", "mekanism:atomic_disassembler", "mekanism:basic_bin", "mekanism:basic_chemical_tank", "mekanism:basic_control_circuit", "mekanism:basic_energy_cube", "mekanism:basic_fluid_tank", "mekanism:basic_induction_cell", "mekanism:basic_induction_provider", "mekanism:basic_pressurized_tube", "mekanism:basic_thermodynamic_conductor", "mekanism:boiler_casing", "mekanism:boiler_valve", "mekanism:chemical_crystallizer", "mekanism:chemical_dissolution_chamber", "mekanism:chemical_infuser", "mekanism:chemical_injection_chamber", "mekanism:chemical_oxidizer", "mekanism:chemical_washer", "mekanism:configurator", "mekanism:diversion_transporter", "mekanism:dust_copper", "mekanism:dynamic_tank", "mekanism:dynamic_valve", "mekanism:electrolytic_core", "mekanism:electrolytic_separator", "mekanism:elite_chemical_tank", "mekanism:elite_control_circuit", "mekanism:elite_energy_cube", "mekanism:elite_induction_cell", "mekanism:elite_induction_provider", "mekanism:elite_pressurized_tube", "mekanism:elite_tier_installer", "mekanism:energy_tablet", "mekanism:enriched_diamond", "mekanism:enriched_refined_obsidian", "mekanism:free_runners", "mekanism:free_runners_armored", "mekanism:induction_casing", "mekanism:induction_port", "mekanism:isotopic_centrifuge", "mekanism:jetpack", "mekanism:laser", "mekanism:laser_tractor_beam", "mekanism:module_base", "mekanism:nutritional_liquifier", "mekanism:pigment_mixer", "mekanism:pressure_disperser", "mekanism:purification_chamber", "mekanism:quantum_entangloporter", "mekanism:radioactive_waste_barrel", "mekanism:resistive_heater", "mekanism:restrictive_transporter", "mekanism:rotary_condensentrator", "mekanism:solar_neutron_activator", "mekanism:sps_casing", "mekanism:sps_port", "mekanism:structural_glass", "mekanism:supercharged_coil", "mekanism:superheating_element", "mekanism:teleportation_core", "mekanism:thermal_evaporation_block", "mekanism:thermal_evaporation_controller", "mekanism:thermal_evaporation_valve", "mekanism:ultimate_chemical_tank", "mekanism:ultimate_control_circuit", "mekanism:ultimate_energy_cube", "mekanism:ultimate_induction_cell", "mekanism:ultimate_induction_provider", "mekanism:ultimate_pressurized_tube", "mekanism:ultimate_thermodynamic_conductor", "mekanism:ultimate_tier_installer", "mekanism:upgrade_anchor", "mekanism:upgrade_chemical", "mekanism:upgrade_energy", "mekanism:upgrade_filter", "mekanism:upgrade_muffling", "mekanism:upgrade_speed", "nuclearcraft:actuator", "nuclearcraft:assembler", "nuclearcraft:borax_dust", "nuclearcraft:centrifuge", "nuclearcraft:chamber_port", "nuclearcraft:chamber_terminal", "nuclearcraft:chemical_reactor", "nuclearcraft:crystallizer", "nuclearcraft:decay_hastener", "nuclearcraft:electrolyzer", "nuclearcraft:event_horizon_stabilizer", "nuclearcraft:expl", "nuclearcraft:extractor", "nuclearcraft:fission_reactor_casing", "nuclearcraft:fission_reactor_controller", "nuclearcraft:fission_reactor_irradiation_chamber", "nuclearcraft:fission_reactor_port", "nuclearcraft:fluid_enricher", "nuclearcraft:fluid_infuser", "nuclearcraft:fusion_reactor_casing", "nuclearcraft:fusion_reactor_connector", "nuclearcraft:fusion_reactor_core", "nuclearcraft:gas_scrubber", "nuclearcraft:hard_carbon_dust", "nuclearcraft:heat_exchanger", "nuclearcraft:heat_exchanger_casing", "nuclearcraft:heat_exchanger_controller", "nuclearcraft:heat_exchanger_radiator", "nuclearcraft:irradiator", "nuclearcraft:leacher", "nuclearcraft:msr_controller", "nuclearcraft:neutronium_frame", "nuclearcraft:nitrogen_collector", "nuclearcraft:photon_concentrator", "nuclearcraft:pressurizer", "nuclearcraft:quantum_flux_regulator", "nuclearcraft:quantum_transformer", "nuclearcraft:servo", "nuclearcraft:sic_fiber", "nuclearcraft:sic_sic_cmc_dust", "nuclearcraft:sic_sic_cmc_plate", "nuclearcraft:steam_turbine", "nuclearcraft:subatomic_liquifier", "nuclearcraft:supercooler", "nuclearcraft:tungsten_dust", "nuclearcraft:turbine_casing", "nuclearcraft:turbine_controller", "nuclearcraft:water_collector", "rocketnautics:booster_thruster", "rocketnautics:copper_anchor_boots", "rocketnautics:copper_leg_thrusters", "rocketnautics:copper_nozzle", "rocketnautics:engine_nozzle", "rocketnautics:engine_pipes", "rocketnautics:hologram_block", "rocketnautics:hose_anchor", "rocketnautics:magnetic_stabilizer", "rocketnautics:rcs_thruster", "rocketnautics:rocket_thruster", "rocketnautics:separator", "rocketnautics:separator_charge", "rocketnautics:separator_shaft", "rocketnautics:sputnik", "rocketnautics:thruster_mount", "rocketnautics:titanium_nozzle", "rocketnautics:vector_thruster", "simulated:altitude_sensor", "simulated:auger_shaft", "simulated:directional_linked_receiver", "simulated:docking_connector", "simulated:engine_assembly", "simulated:gimbal_sensor", "simulated:gyroscopic_mechanism", "simulated:modulating_linked_receiver", "simulated:navigation_table", "simulated:optical_sensor", "simulated:physics_assembler", "simulated:redstone_magnet", "simulated:rope_connector", "simulated:rope_coupling", "simulated:spring", "simulated:throttle_lever", "simulated:velocity_sensor", "tfmg:aluminum_cogwheel", "tfmg:aluminum_fluid_valve", "tfmg:aluminum_smart_fluid_pipe", "tfmg:blast_furnace_hatch", "tfmg:blast_furnace_output", "tfmg:blast_furnace_reinforcement", "tfmg:blast_stove", "tfmg:cable_connector", "tfmg:cable_tube", "tfmg:cast_iron_chemical_vat", "tfmg:cast_iron_fluid_tank", "tfmg:cast_iron_fluid_valve", "tfmg:cast_iron_mechanical_pump", "tfmg:cast_iron_pipe", "tfmg:cast_iron_sheet", "tfmg:casting_basin", "tfmg:coated_circuit_board", "tfmg:copper_cable_hub", "tfmg:diesel_engine_cylinder", "tfmg:electric_diode", "tfmg:electric_motor", "tfmg:electrical_switch", "tfmg:empty_spool", "tfmg:engine_controller", "tfmg:engine_cylinder", "tfmg:engine_gearbox", "tfmg:fireproof_brick_reinforcement", "tfmg:fireproof_bricks", "tfmg:fireproof_chemical_vat", "tfmg:generator", "tfmg:heavy_cable_hub", "tfmg:heavy_plate", "tfmg:industrial_mixer", "tfmg:industrial_pipe", "tfmg:large_aluminum_cogwheel", "tfmg:large_engine", "tfmg:large_pumpjack_hammer_connector", "tfmg:large_pumpjack_hammer_head", "tfmg:large_pumpjack_hammer_part", "tfmg:large_switch", "tfmg:machine_input", "tfmg:multimeter", "tfmg:oil_can", "tfmg:oil_hammer", "tfmg:plastic_fluid_valve", "tfmg:plastic_smart_fluid_pipe", "tfmg:polarizer", "tfmg:pumpjack_base", "tfmg:pumpjack_crank", "tfmg:pumpjack_hammer", "tfmg:pumpjack_hammer_connector", "tfmg:pumpjack_hammer_head", "tfmg:pumpjack_hammer_part", "tfmg:radial_engine", "tfmg:regular_engine", "tfmg:segmented_display", "tfmg:simple_large_engine", "tfmg:spark_plug", "tfmg:steel_cable_hub", "tfmg:steel_casing", "tfmg:steel_chemical_vat", "tfmg:steel_distillation_controller", "tfmg:steel_distillation_output", "tfmg:steel_fluid_tank", "tfmg:steel_fluid_valve", "tfmg:steel_frame", "tfmg:steel_gearbox", "tfmg:steel_mechanical_pump", "tfmg:steel_pipe", "tfmg:steel_smart_fluid_pipe", "tfmg:surface_scanner", "tfmg:transformer", "tfmg:transistor_item", "tfmg:turbine_engine", "tfmg:voltmeter", "vsie:computronic_substrate", "vsie:warp_data_chip"];
  var removedPending = 0;
  function primaryProducts(value, result) {
    if (!value) return;
    if (typeof value === 'string') { result.push(value); return; }
    if (Array.isArray(value)) { value.forEach(v => primaryProducts(v, result)); return; }
    if (typeof value.id === 'string') result.push(value.id);
    if (typeof value.item === 'string') result.push(value.item);
  }
  event.addedRecipes.removeIf(recipe => {
    try { recipe.serialize(); } catch (error) { return false; }
    var data = JSON.parse(recipe.json.toString());
    var products = [];
    ['result', 'results', 'output', 'outputs', 'item_output', 'item_outputs'].forEach(k => primaryProducts(data[k], products));
    var replace = products.some(id => replacementOutputs.indexOf(id) >= 0);
    if (replace) removedPending++;
    return replace;
  });
  console.info('[Industrial Colonies] Approved release removed ' + removedPending + ' legacy pending recipe alternatives.');
})

ServerEvents.recipes(event => {
  event.forEachRecipe({type: 'tfmg:vat_machine_recipe'}, recipe => {
    var data = JSON.parse(recipe.json.toString());
    var first = data.results && data.results[0];
    if (first && first.id === 'modernfoundry:molten_chromium') recipe.remove();
  });
})
ServerEvents.recipes(event => {
  // [Casting Basin] Native ingredient/output baseline from tfmg:crafting/materials/casting_basin. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shaped('tfmg:casting_basin', ['ABA', 'CAC', 'CCC'], {
      A: 'tfmg:fireproof_brick',
      B: 'tfmg:cast_iron_pipe',
      C: '#c:ingots/cast_iron'
    }).id('industrial_colonies:priority/tfmg/casting_basin')
})

ServerEvents.recipes(event => {
  // [Centrifugal Clutch] Native ingredient/output baseline from create_connected:crafting/kinetics/centrifugal_clutch. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('create_connected:centrifugal_clutch', ['create:andesite_casing', 'create:shaft', 'create:iron_sheet', 'create:speedometer']).id('industrial_colonies:priority/create_connected/centrifugal_clutch')
})

ServerEvents.recipes(event => {
  // [Freewheel Clutch] Native ingredient/output baseline from create_connected:crafting/kinetics/freewheel_clutch. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('create_connected:freewheel_clutch', ['create:andesite_casing', 'create:shaft', 'create:iron_sheet', 'create:cogwheel']).id('industrial_colonies:priority/create_connected/freewheel_clutch')
})

ServerEvents.recipes(event => {
  // [Inverted Clutch] Native ingredient/output baseline from create_connected:crafting/kinetics/inverted_clutch_from_conversion. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('create_connected:inverted_clutch', ['create:clutch']).id('industrial_colonies:priority/create_connected/inverted_clutch')
})

ServerEvents.recipes(event => {
  // [Overstress Clutch] Native ingredient/output baseline from create_connected:crafting/kinetics/overstress_clutch. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('create_connected:overstress_clutch', ['create:andesite_casing', 'create:shaft', 'create:iron_sheet', 'create:electron_tube']).id('industrial_colonies:priority/create_connected/overstress_clutch')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel Gearbox] Native ingredient/output baseline from tfmg:crafting/materials/steel_gearbox. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
    event.recipes.create.mechanical_crafting('tfmg:steel_gearbox', [' A ', 'ABA', ' A '], {
        A: 'tfmg:steel_cogwheel',
        B: 'tfmg:heavy_machinery_casing'
      }).id('industrial_colonies:priority/tfmg/steel_gearbox')
  }
})

ServerEvents.recipes(event => {
  // [Kinetic Battery] Native ingredient/output baseline from create_connected:crafting/kinetics/kinetic_battery. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shaped('8x create_connected:kinetic_battery', [' A ', ' B ', 'CDC'], {
      A: 'create:precision_mechanism',
      B: 'create:brass_casing',
      C: 'create:iron_sheet',
      D: 'minecraft:redstone'
    }).id('industrial_colonies:priority/create_connected/kinetic_battery')
})

ServerEvents.recipes(event => {
  // [Small Connector With Light] Native ingredient/output baseline from createaddition:crafting/small_light_connector. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('createaddition:small_light_connector', ['#c:wires/iron', '#c:glass_blocks', 'createaddition:connector']).id('industrial_colonies:priority/createaddition/small_light_connector')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Alternator] Native ingredient/output baseline from createaddition:mechanical_crafting/alternator. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
    event.custom({"type":"create:mechanical_crafting","accept_mirrored":true,"pattern":["  C  "," GHI ","KLMNO"," QRS ","  W  "],"key":{"C":{"item":"create:andesite_alloy"},"G":{"tag":"c:plates/iron"},"H":{"item":"createaddition:copper_spool"},"I":{"tag":"c:plates/iron"},"K":{"tag":"c:plates/iron"},"L":{"item":"createaddition:copper_spool"},"M":{"tag":"c:rods/iron"},"N":{"item":"createaddition:copper_spool"},"O":{"tag":"c:plates/iron"},"Q":{"tag":"c:plates/iron"},"R":{"item":"createaddition:copper_spool"},"S":{"tag":"c:plates/iron"},"W":{"item":"create:andesite_alloy"}},"result":{"id":"createaddition:alternator","count":1}}).id('industrial_colonies:priority/createaddition/alternator')
  }
})

ServerEvents.recipes(event => {
  // [Weathered Iron Depot] Native ingredient/output baseline from createcasing:crafting/depot/weathered_iron. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('createcasing:weathered_iron_depot', ['create:andesite_alloy', 'create:weathered_iron_block']).id('industrial_colonies:priority/createcasing/weathered_iron_depot')
})

ServerEvents.recipes(event => {
  // [Empty Fan Catalyst] Native ingredient/output baseline from create_connected:crafting/kinetics/empty_fan_catalyst. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shaped('create_connected:empty_fan_catalyst', ['ABA', 'B B', 'ABA'], {
      A: 'create:brass_ingot',
      B: 'minecraft:iron_bars'
    }).id('industrial_colonies:priority/create_connected/empty_fan_catalyst')
})

ServerEvents.recipes(event => {
  // [Kinetic Bridge] Native ingredient/output baseline from create_connected:crafting/kinetics/kinetic_bridge. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shaped('create_connected:kinetic_bridge', [' A ', 'BCB', ' A '], {
      A: 'create:brass_casing',
      B: 'create:shaft',
      C: 'create:clutch'
    }).id('industrial_colonies:priority/create_connected/kinetic_bridge')
})

ServerEvents.recipes(event => {
  // [Vertical 6-way Gearbox] Native ingredient/output baseline from create_connected:crafting/kinetics/vertical_six_way_gearbox_from_conversion. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('create_connected:vertical_six_way_gearbox', ['create_connected:six_way_gearbox']).id('industrial_colonies:priority/create_connected/vertical_six_way_gearbox')
})

ServerEvents.recipes(event => {
  // [Vertical Brass Gearbox] Native ingredient/output baseline from create_connected:crafting/kinetics/vertical_brass_gearbox_from_conversion. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('create_connected:vertical_brass_gearbox', ['create_connected:brass_gearbox']).id('industrial_colonies:priority/create_connected/vertical_brass_gearbox')
})

ServerEvents.recipes(event => {
  // [Vertical Parallel Gearbox] Native ingredient/output baseline from create_connected:crafting/kinetics/vertical_parallel_gearbox_from_conversion. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('create_connected:vertical_parallel_gearbox', ['create_connected:parallel_gearbox']).id('industrial_colonies:priority/create_connected/vertical_parallel_gearbox')
})

ServerEvents.recipes(event => {
  // [Aluminum Cogwheel] Native ingredient/output baseline from tfmg:crafting/materials/aluminum_cogwheel. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('4x tfmg:aluminum_cogwheel', ['#c:ingots/aluminum', 'create:shaft']).id('industrial_colonies:priority/tfmg/aluminum_cogwheel')
})

ServerEvents.recipes(event => {
  // [Large Aluminum Cogwheel] Native ingredient/output baseline from tfmg:crafting/materials/large_aluminum_cogwheel. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
  event.shapeless('2x tfmg:large_aluminum_cogwheel', ['#c:ingots/aluminum', '#c:ingots/aluminum', 'create:shaft']).id('industrial_colonies:priority/tfmg/large_aluminum_cogwheel')
})

ServerEvents.recipes(event => {
  // DRAFT - Four structural panels: upper/lower plate banks on an existing cast-iron frame and nuclear chassis, with one Radiance mounting treatment per batch. Bulk walls retain the nuclear gate without four Radiance pieces per batch; electronics belong in controllers.
  event.shaped('4x nuclearcraft:heat_exchanger_casing', ['AAA', 'BCB', 'AAA'], {
      A: 'immersiveengineering:plate_lead',
      B: 'create:refined_radiance',
      C: 'tfmg:steel_frame'
    }).group('06 Nuclear structures').id('industrial_colonies:custom_progression/nuclearcraft/heat_exchanger_casing')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-requested full5x5 nuclear heat controller. Central steel frame, two Radiance side supports, lead corner shielding, brass coolant plumbing, nuclear mechanisms, completed boards and calculation/logic control.25occupied inputs; no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:heat_exchanger_controller', ['ABCBA', 'DEFED', 'GBHBG', 'DBFBD', 'ABIBA'], {
        A: 'immersiveengineering:plate_lead',
        B: 'tfmg:brass_pipe',
        C: 'ae2:calculation_processor',
        D: 'tfmg:copper_wire',
        E: 'createmechanisms:nuclear_mechanism',
        F: 'tfmg:circuit_board',
        G: 'create:refined_radiance',
        H: 'tfmg:steel_frame',
        I: 'ae2:logic_processor'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/heat_exchanger_controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Populate a coated TFMG board with engineering and silicon dies, a complementary semiconductor stage, discrete power electronics, plastic insulation, nickel conductors, and magnetic shielding before packaging
    event.recipes.create.sequenced_assembly(['ae2:engineering_processor'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'ae2:printed_engineering_processor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'tfmg:nickel_sheet']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_engineering_processor', ['createappliedkinetics:incomplete_engineering_processor', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('createappliedkinetics:incomplete_engineering_processor', 'createappliedkinetics:incomplete_engineering_processor')
      ]).transitionalItem('createappliedkinetics:incomplete_engineering_processor').loops(1).id('industrial_colonies:ae2/engineering_processor')
  }
})

ServerEvents.recipes(event => {
  // Ordinary crafting baseline from existing Basic Mechanism Recipes.js; available before Weathered Iron machines. No machine gate.
  event.shaped('createmechanisms:zinc_mechanism', ['ABA', 'CDC', 'ACA'], {
      A: '#c:nuggets/zinc',
      B: 'create:large_cogwheel',
      C: '#c:ingots/zinc',
      D: 'createmechanisms:wooden_mechanism'
    }).id('industrial_colonies:priority/createmechanisms/zinc_mechanism')
})

ServerEvents.recipes(event => {
  // Ordinary crafting baseline from existing Basic Mechanism Recipes.js; available before Weathered Iron machines. No machine gate.
  event.shaped('2x createmechanisms:wooden_mechanism', ['AB', 'CD'], {
      A: '#c:stripped_woods',
      B: '#createmechanisms:saw',
      C: '#minecraft:wooden_slabs',
      D: 'create:cogwheel'
    }).id('industrial_colonies:priority/createmechanisms/wooden_mechanism')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Network controller: sky-stone enclosure, shielded routing board banks, distributed processors, dense-cable ports and isolated power around a central frame. Physical network cabling replaces loose generic semiconductor filler. User-review draft; no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:controller', ['ABCBA', 'DEFED', 'GHIHG', 'DEJED', 'ABKBA'], {
        A: 'ae2:smooth_sky_stone_block',
        B: 'tfmg:magnetic_alloy_sheet',
        C: 'ae2:engineering_processor',
        D: 'ae2:fluix_smart_dense_cable',
        E: 'tfmg:circuit_board',
        F: 'ae2:calculation_processor',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:capacitor_item',
        I: 'tfmg:steel_frame',
        J: 'ae2:logic_processor',
        K: 'ae2:energy_acceptor'
      }).id('industrial_colonies:v3_ae2/controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Turn the Andesite stress board into a Brass multilayer board with coated routing, semiconductor junctions, and magnetic clock shielding
    event.recipes.create.sequenced_assembly(['appliedcreate:advanced_stress_circuit_board'], 'appliedcreate:stress_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:brass_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:stress_circuit_board'}})).loops(1).id('industrial_colonies:v3_ae2/advanced_stress_circuit_board')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Build the Andesite stress board after default Create by laminating an Andesite sheet with an etched TFMG board, copper traces, and a plastic dielectric
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_circuit_board'], 'createcasing:andesite_sheet', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:cinder_flour']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createcasing:andesite_sheet'}})).loops(1).id('industrial_colonies:v3_ae2/stress_circuit_board')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Populate a coated TFMG board with calculation and silicon dies, complementary semiconductors, discrete timing electronics, plastic insulation, fluix clock material, and redstone before packaging
    event.recipes.create.sequenced_assembly(['ae2:calculation_processor'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'ae2:printed_calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', Ingredient.of('#c:dusts/fluix')]),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'minecraft:redstone']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_calculation_processor', ['createappliedkinetics:incomplete_calculation_processor', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.brass_pressing('createappliedkinetics:incomplete_calculation_processor', 'createappliedkinetics:incomplete_calculation_processor')
      ]).transitionalItem('createappliedkinetics:incomplete_calculation_processor').loops(1).id('industrial_colonies:ae2/calculation_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Restore the missing Rotary as a real Weathered-built gas/fluid bridge: separate reservoirs, pump, motor, transformer and advanced control. Avoid the unavailable user Energy Tablet and downstream HDPE/Industrial machines; existing unrelated user cards remain untouched.
    event.recipes.create.sequenced_assembly(['mekanism:rotary_condensentrator'], 'tfmg:steel_frame', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_chemical_vat']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_tank']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_chemical_tank']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:mechanical_pump']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transformer']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_control_circuit']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_frame'}})).loops(1).id('industrial_colonies:material_bootstrap/rotary_condensentrator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('electroenergetics:current_transformer', ['A A', 'BCB', 'D D'], {
        A: 'electroenergetics:connector',
        B: 'electroenergetics:insulated_wire',
        C: 'electroenergetics:transformer_core',
        D: 'tfmg:resistor'
      }).id('industrial_colonies:high_voltage/current_transformer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Review correction: a refractory-lined outlet with a central drain and a load-bearing plate. Cast iron piping keeps the first blast furnace independent of its own steel output.
    event.recipes.create.mechanical_crafting('tfmg:blast_furnace_output', [' A ', 'BCB', ' D '], {
        A: 'tfmg:cast_iron_pipe',
        B: 'tfmg:fireproof_bricks',
        C: 'minecraft:hopper',
        D: 'create:iron_sheet'
      }).id('industrial_colonies:steelworks/blast_furnace_output')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('tfmg:transformer', [' A A ', 'BACAB', ' DED '], {
        A: 'tfmg:copper_spool',
        B: 'tfmg:nickel_sheet',
        C: 'tfmg:laminated_magnetic_alloy_block',
        D: 'tfmg:heavy_plate',
        E: 'tfmg:steel_casing'
      }).id('industrial_colonies:tfmg_heavy_electrical/transformer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Review correction: a central mating connector between two sealed service manifolds, driven by locking motors and a dedicated alignment controller.
    event.recipes.create.mechanical_crafting('2x simulated:docking_connector', ['A B A', 'CDEDC', 'FGHGF', ' I I '], {
        A: 'tfmg:steel_pipe',
        B: 'create:portable_storage_interface',
        C: 'ae2:fluix_smart_dense_cable',
        D: 'tfmg:steel_fluid_valve',
        E: 'rocketnautics:titanium_casing',
        F: 'tfmg:heavy_plate',
        G: 'tfmg:electric_motor',
        H: 'ae2:engineering_processor',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:space/dockyard/docking_connector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('simulated:velocity_sensor', [' A ', 'BCB', 'DED', ' F '], {
        A: 'tfmg:voltmeter',
        B: 'tfmg:electric_motor',
        C: 'simulated:gyroscopic_mechanism',
        D: 'tfmg:steel_casing',
        E: 'tfmg:circuit_board',
        F: 'ae2:calculation_processor'
      }).id('industrial_colonies:space/navigation/velocity_sensor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // DRAFT - Tapered titanium shell with a small sensor window, internal equipment casing and steel mounting flange. Existing upstream recipes remain dependencies. No gameplay export.
    event.recipes.create.mechanical_crafting('ad_astra:rocket_nose_cone', ['  A  ', ' ABA ', 'A C A', ' DDD '], {
        A: 'rocketnautics:titanium_alloy',
        B: 'minecraft:glass',
        C: 'tfmg:heavy_machinery_casing',
        D: 'tfmg:steel_ingot'
      }).group('Design 01 / 08 Rocket structures').id('industrial_colonies:functional_design/ad_astra/rocket_nose_cone')
  }
})

ServerEvents.recipes(event => {
  // DRAFT - Swept triangular fin: titanium leading edge over a steel root and spar. Four matching fins per batch. Existing upstream recipes remain dependencies. No gameplay export.
  event.shaped('4x ad_astra:rocket_fin', ['A  ', 'BA ', 'BBA'], {
      A: 'rocketnautics:titanium_alloy',
      B: 'tfmg:steel_ingot'
    }).group('Design 01 / 08 Rocket structures').id('industrial_colonies:functional_design/ad_astra/rocket_fin')
})

ServerEvents.recipes(event => {
  // DRAFT - Copper throat retained inside a titanium-alloy reinforcement jacket; one high-temperature nozzle. Existing upstream recipes remain dependencies. No gameplay export.
  event.shaped('rocketnautics:titanium_nozzle', ['A A', 'ABA', ' A '], {
      A: 'rocketnautics:titanium_alloy',
      B: 'rocketnautics:copper_nozzle'
    }).group('Design 01 / 08 Propulsion parts').id('industrial_colonies:functional_design/rocketnautics/titanium_nozzle')
})

ServerEvents.recipes(event => {
  // DRAFT - Converging sheet-metal nozzle profile: open intake, straight walls and a narrow throat. Two small nozzles per forming batch. Existing upstream recipes remain dependencies. No gameplay export.
  event.shaped('2x rocketnautics:copper_nozzle', ['A A', 'A A', ' A '], {
      A: 'create:copper_sheet'
    }).group('Design 01 / 08 Propulsion parts').id('industrial_colonies:functional_design/rocketnautics/copper_nozzle')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // DRAFT - Two fin banks cross three copper heat paths, with separate inlet and outlet under the bank. Two radiator sections per build. Existing upstream recipes remain dependencies. No gameplay export.
    event.recipes.create.mechanical_crafting('2x nuclearcraft:heat_exchanger_radiator', ['ABABA', 'C C C', 'ABABA', ' D E '], {
        A: 'tfmg:aluminum_sheet',
        B: 'tfmg:copper_frame',
        C: 'createaddition:copper_rod',
        D: 'tfmg:industrial_pipe',
        E: 'tfmg:steel_pipe'
      }).group('Design 01 / 06 Nuclear heat exchange').id('industrial_colonies:functional_design/nuclearcraft/heat_exchanger_radiator')
  }
})

ServerEvents.recipes(event => {
  // DRAFT - Controller and capacitor mounted across the board; two edge contacts below. Two blank upgrade cards per board assembly. Existing upstream recipes remain dependencies. No gameplay export.
  event.shaped('2x ae2:basic_card', ['ABC', ' D ', ' D '], {
      A: 'ae2:logic_processor',
      B: 'createaddition:capacitor',
      C: 'tfmg:coated_circuit_board',
      D: 'createaddition:electrum_wire'
    }).group('Design 01 / 07 Electronics').id('industrial_colonies:functional_design/ae2/basic_card')
})

ServerEvents.recipes(event => {
  // DRAFT - Parallel arithmetic chips and routing processor upgrade one basic card; separated bus contacts below. Existing upstream recipes remain dependencies. No gameplay export.
  event.shaped('ae2:advanced_card', ['ABA', ' C ', 'D D'], {
      A: 'ae2:calculation_processor',
      B: 'ae2:engineering_processor',
      C: 'ae2:basic_card',
      D: 'createaddition:electrum_wire'
    }).group('Design 01 / 07 Electronics').id('industrial_colonies:functional_design/ae2/advanced_card')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // CUSTOM DRAFT - One functional working head and drive, two reusable mechanisms, one frame and controller, wiring and rod supports; four corner plates. Uses existing Personal Recipes outputs where specified. No gameplay export; costs and survival access await review.
    event.recipes.create.mechanical_crafting('nuclearcraft:centrifuge', ['A B A', 'CDEDC', ' FGF ', 'A H A'], {
        A: 'immersiveengineering:plate_lead',
        B: 'ae2:calculation_processor',
        C: 'tfmg:copper_wire',
        D: 'createmechanisms:nuclear_mechanism',
        E: 'tfmg:steel_frame',
        F: 'createaddition:iron_rod',
        G: 'tfmg:electric_motor',
        H: 'tfmg:centrifuge'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/centrifuge')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // CUSTOM DRAFT - One functional working head and drive, two reusable mechanisms, one frame and controller, wiring and rod supports; four corner plates. Uses existing Personal Recipes outputs where specified. No gameplay export; costs and survival access await review.
    event.recipes.create.mechanical_crafting('nuclearcraft:nitrogen_collector', ['A B A', 'CDEDC', ' FGF ', 'A H A'], {
        A: 'immersiveengineering:plate_lead',
        B: 'ae2:calculation_processor',
        C: 'tfmg:copper_wire',
        D: 'createmechanisms:nuclear_mechanism',
        E: 'tfmg:steel_frame',
        F: 'createaddition:iron_rod',
        G: 'tfmg:electric_pump',
        H: 'create:propeller'
      }).group('06 Nuclear support').id('industrial_colonies:custom_progression/nuclearcraft/nitrogen_collector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // REFINED DRAFT - Twin extraction vessels with protective polymer liners feed a common pump; chemistry controls below. Existing vats and pumps remain bulk dependencies. Existing upstream recipes retained. No gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:leacher', [' A A ', 'BC CB', '  D  ', ' EFE '], {
        A: 'tfmg:industrial_pipe',
        B: 'mekanism:hdpe_sheet',
        C: 'tfmg:steel_chemical_vat',
        D: 'tfmg:electric_pump',
        E: 'tfmg:steel_frame',
        F: 'mekanism:advanced_control_circuit'
      }).group('Chain 03 / 06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/leacher')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // REFINED DRAFT - Two feeds enter a lined, sealed chemical vessel; mixer beneath the vessel and frame-mounted control deck. Polymer is used as a liner, not molten containment. Existing upstream recipes retained. No gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:fluid_infuser', ['A   A', 'BCDCB', '  E  ', ' FGF '], {
        A: 'tfmg:industrial_pipe',
        B: 'mekanism:hdpe_sheet',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:steel_chemical_vat',
        E: 'tfmg:industrial_mixer',
        F: 'tfmg:cast_iron_frame',
        G: 'mekanism:advanced_control_circuit'
      }).group('Chain 03 / 06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/fluid_infuser')
  }
})

ServerEvents.recipes(event => {
  // Physical electrical switch block: lever above copper contact cheeks, conductor, rubber insulation and a cast-iron mounting backplate. No unnecessary board/resistor package. User-review draft; no gameplay export.
  event.shaped('tfmg:electrical_switch', [' A ', 'BCB', 'DED'], {
      A: 'minecraft:lever',
      B: 'create:copper_sheet',
      C: 'tfmg:copper_wire',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:cast_iron_sheet'
    }).group('03 Electrical instruments').id('industrial_colonies:custom_progression/tfmg/electrical_switch')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Fission shutdown/control console: lead shielding, paired comparator sensors, board instrumentation and a Radiance reference; opposing rod actuators flank the frame; boron shutdown material and graphite-facing base. Full5x5, distinct rod-control architecture. User-review draft; no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:fission_reactor_controller', ['ABCBA', 'DEFED', 'AGHGA', 'DIJID', 'AKKKA'], {
        A: 'immersiveengineering:plate_lead',
        B: 'minecraft:comparator',
        C: 'ae2:calculation_processor',
        D: 'createaddition:electrum_wire',
        E: 'tfmg:circuit_board',
        F: 'create:refined_radiance',
        G: 'nuclearcraft:actuator',
        H: 'tfmg:steel_frame',
        I: 'nuclearcraft:boron_ingot',
        J: 'mekanism:advanced_control_circuit',
        K: 'createmetallurgy:graphite'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/fission_reactor_controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Chemical reaction skid: top mixer and inspection ports, three lined reaction vessels, twin drive motors, rubber isolation, dual pumped feed and nickel base. Elite process control belongs below the wet section. Full5x5, no fission rod or turbine governor parts. User-review draft; no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:chemical_reactor', ['ABCBA', 'DEEED', 'FGHGF', 'IJAJI', 'KKLKK'], {
        A: 'tfmg:steel_pipe',
        B: 'minecraft:tinted_glass',
        C: 'tfmg:industrial_mixer',
        D: 'mekanism:hdpe_sheet',
        E: 'tfmg:steel_chemical_vat',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:electric_motor',
        H: 'tfmg:steel_frame',
        I: 'tfmg:circuit_board',
        J: 'tfmg:electric_pump',
        K: 'immersiveengineering:plate_nickel',
        L: 'mekanism:elite_control_circuit'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/chemical_reactor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Turbine governor: instrument panel above an insulated speed-governor shaft; two potentiometers provide mechanical feedback, lower steam valves regulate flow. Nickel manifold base and Radiance supports. Open top corners intentional; no generic nuclear shielding shell. User-review draft; no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:turbine_controller', [' ABA ', 'CDEDC', 'FGHGF', 'IJKJI', 'LILIL'], {
        A: 'ae2:calculation_processor',
        B: 'tfmg:voltmeter',
        C: 'tfmg:circuit_board',
        D: 'createaddition:electrum_wire',
        E: 'tfmg:rubber_sheet',
        F: 'create:refined_radiance',
        G: 'tfmg:potentiometer',
        H: 'nuclearcraft:turbine_rotor_shaft',
        I: 'tfmg:steel_pipe',
        J: 'tfmg:steel_fluid_valve',
        K: 'mekanism:advanced_control_circuit',
        L: 'immersiveengineering:plate_nickel'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/turbine_controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Precision drill adds diamond cutter and calibrated control around the copper drive, with brass support. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:brass_mechanical_drill', ['  A  ', ' BBB ', 'CDEDC', 'FGHGF'], {
        A: 'minecraft:diamond',
        B: 'tfmg:nickel_sheet',
        C: 'create:precision_mechanism',
        D: 'tfmg:potentiometer',
        E: 'createcasing:copper_mechanical_drill',
        F: 'tfmg:brass_frame',
        G: 'create:shaft',
        H: 'tfmg:circuit_board'
      }).group('04 Brass precision').id('industrial_colonies:custom_progression/createcasing/brass_mechanical_drill')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Heavy shaft and steel gearing reinforce the precision drill for industrial duty. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:railway_mechanical_drill', ['  A  ', 'BCBCB', 'DEFED', 'BGHGB'], {
        A: 'minecraft:diamond',
        B: 'tfmg:heavy_plate',
        C: 'create:shaft',
        D: 'tfmg:electric_motor',
        E: 'tfmg:steel_mechanism',
        F: 'createcasing:brass_mechanical_drill',
        G: 'tfmg:steel_frame',
        H: 'tfmg:circuit_board'
      }).group('05 Steel industry').id('industrial_colonies:custom_progression/createcasing/railway_mechanical_drill')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Tungsten cutting teeth, geared industrial drive and engineering feedback on a rigid heavy base. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:industrial_iron_mechanical_drill', ['  A  ', 'BACAB', 'DEFED', 'GHIHG', 'JKKKJ'], {
        A: 'createmetallurgy:tungsten_sheet',
        B: 'tfmg:nickel_sheet',
        C: 'create:shaft',
        D: 'tfmg:electric_motor',
        E: 'createmechanisms:advanced_precision_mechanism',
        F: 'createcasing:railway_mechanical_drill',
        G: 'tfmg:circuit_board',
        H: 'ae2:calculation_processor',
        I: 'ae2:engineering_processor',
        J: 'tfmg:heavy_plate',
        K: 'tfmg:steel_frame'
      }).group('05 Industrial Iron').id('industrial_colonies:custom_progression/createcasing/industrial_iron_mechanical_drill')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Horizontal rotor shaft with blade banks above/below, steam manifold at top and governed output base. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:steam_turbine', ['ABBBA', 'ACDCA', 'EFFFE', 'ACDCA', 'AGHGA'], {
        A: 'tfmg:nickel_sheet',
        B: 'tfmg:steel_pipe',
        C: 'nuclearcraft:turbine_steel_rotor_blade',
        D: 'tfmg:steel_fluid_valve',
        E: 'tfmg:electric_motor',
        F: 'create:shaft',
        G: 'ae2:calculation_processor',
        H: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/steam_turbine')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Nickel steam-resistant skin and rubber seals over a steel pressure frame; no irrelevant lead shielding. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('4x nuclearcraft:turbine_casing', ['AAA', 'BCB', 'DDD'], {
      A: 'tfmg:nickel_sheet',
      B: 'tfmg:rubber_sheet',
      C: 'tfmg:steel_frame',
      D: 'tfmg:heavy_plate'
    }).group('06 Nuclear structures').id('industrial_colonies:custom_progression/nuclearcraft/turbine_casing')
})

ServerEvents.recipes(event => {
  // Review revision: Lead shielding above a steel structural base; Radiance side braces, four casing blocks. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('4x nuclearcraft:fission_reactor_casing', ['AAA', 'BCB', 'DDD'], {
      A: 'immersiveengineering:plate_lead',
      B: 'create:refined_radiance',
      C: 'tfmg:steel_frame',
      D: 'tfmg:heavy_plate'
    }).group('06 Nuclear structures').id('industrial_colonies:custom_progression/nuclearcraft/fission_reactor_casing')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Fusion confinement core: opposed superconducting coils, controlled coolant valves and tungsten/titanium hot-zone structure. No fission-controller clone. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:fusion_reactor_core', ['ABCCCBA', 'BDEFEDB', 'CGHIHGC', 'CIJKJIC', 'CGHIHGC', 'BDEFEDB', 'ABCCCBA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'createmetallurgy:tungsten_sheet',
        C: 'tfmg:steel_pipe',
        D: 'nuclearcraft:coil_magnesium_diboride',
        E: 'electroenergetics:high_voltage_capacitor',
        F: 'mekanism:ultimate_control_circuit',
        G: 'tfmg:circuit_board',
        H: 'tfmg:steel_fluid_valve',
        I: 'create:refined_radiance',
        J: 'nuclearcraft:fusion_reactor_casing',
        K: 'ae2:engineering_processor'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/fusion_reactor_core')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Lever bridges two copper contacts above insulated metal backing. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('tfmg:large_switch', [' A ', 'BCB', 'DED'], {
      A: 'minecraft:lever',
      B: 'create:copper_sheet',
      C: 'tfmg:rubber_sheet',
      D: 'tfmg:cast_iron_sheet',
      E: 'tfmg:screw'
    }).group('03 Electrical instruments').id('industrial_colonies:custom_progression/tfmg/large_switch')
})

ServerEvents.recipes(event => {
  // Review revision: Glass display face over driven light element and populated board. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('2x tfmg:segmented_display', ['AAA', 'BCB', 'DED'], {
      A: 'minecraft:glass',
      B: 'tfmg:copper_wire',
      C: 'create:electron_tube',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).group('03 Electrical instruments').id('industrial_colonies:custom_progression/tfmg/segmented_display')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Early zinc mechanism becomes insulated electromechanical power control, without late processors. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:basic_energy_mechanism'], 'createmechanisms:zinc_mechanism', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electromagnetic_coil']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:capacitor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createmechanisms:zinc_mechanism'}})).loops(1).group('04 Control mechanisms').id('industrial_colonies:custom_progression/createmechanisms/basic_energy_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Redstone switching and visual signal element assembled onto an early zinc drive. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:redstone_mechanism'], 'createmechanisms:zinc_mechanism', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:redstone_torch']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:electron_tube']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createmechanisms:zinc_mechanism'}})).loops(1).group('04 Control mechanisms').id('industrial_colonies:custom_progression/createmechanisms/redstone_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Shielded sample chambers with field coils and ultimate timing controls, distinct from the irradiation tunnel. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:decay_hastener', ['ABABA', 'ACDCA', 'EFGFE', 'HIIIH'], {
        A: 'immersiveengineering:plate_lead',
        B: 'nuclearcraft:coil_copper',
        C: 'mekanism:basic_chemical_tank',
        D: 'create:refined_radiance',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'mekanism:ultimate_control_circuit',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/decay_hastener')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Motor-driven separation shaft and centrifuge chamber, collection outlets at opposite sides. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:extractor', ['  A  ', 'BCDCB', 'EFFFE', 'GHIHG', 'BJJJB'], {
        A: 'tfmg:electric_motor',
        B: 'tfmg:nickel_sheet',
        C: 'tfmg:centrifuge',
        D: 'create:shaft',
        E: 'tfmg:steel_pipe',
        F: 'tfmg:steel_chemical_vat',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:circuit_board',
        I: 'ae2:logic_processor',
        J: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/extractor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Reagent tanks over electrode-lined enrichment vessel with insulated electronics and independent fluid flow. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:fluid_enricher', ['A B A', 'CDDDC', 'EFEFE', 'GHIHG', 'GJJJG'], {
        A: 'mekanism:basic_chemical_tank',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:electric_pump',
        D: 'tfmg:steel_chemical_vat',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:graphite_electrode',
        G: 'tfmg:heavy_plate',
        H: 'tfmg:circuit_board',
        I: 'ae2:calculation_processor',
        J: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/fluid_enricher')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Vertical scrubber vessel with corrosion-resistant lining, recirculating pumps and lower control cabinet. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:gas_scrubber', ['A   A', 'BCCCB', 'BDEDB', 'FDGDF', 'HIJIH'], {
        A: 'tfmg:steel_pipe',
        B: 'mekanism:hdpe_sheet',
        C: 'minecraft:glass',
        D: 'tfmg:rubber_sheet',
        E: 'tfmg:steel_chemical_vat',
        F: 'tfmg:electric_pump',
        G: 'tfmg:circuit_board',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:steel_frame',
        J: 'ae2:calculation_processor'
      }).group('Chain 03 / 06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/gas_scrubber')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Fan/radiator bank above a superconducting cooling loop and twin circulation pumps. Higher infrastructure cost without a dragon drop in every radiator. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:supercooler', ['AAAAA', 'BCBCB', 'DEFED', 'GHIHG', 'FJJJF'], {
        A: 'create:propeller',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:nickel_sheet',
        D: 'tfmg:electric_pump',
        E: 'nuclearcraft:coil_magnesium_diboride',
        F: 'tfmg:steel_fluid_tank',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:circuit_board',
        I: 'mekanism:ultimate_control_circuit',
        J: 'tfmg:steel_frame'
      }).group('Chain 03 / 06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/supercooler')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Superconducting conversion vessel, tungsten hot zone and titanium pipe connections; replaces disliked extreme plates. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:subatomic_liquifier', ['ABCBA', 'BDEDB', 'FGHGF', 'IJKJI', 'ABCBA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'createmetallurgy:tungsten_sheet',
        C: 'tfmg:steel_pipe',
        D: 'nuclearcraft:coil_bscco',
        E: 'tfmg:fireproof_chemical_vat',
        F: 'tfmg:electric_pump',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:steel_frame',
        I: 'tfmg:circuit_board',
        J: 'advanced_ae:quantum_processor',
        K: 'mekanism:ultimate_control_circuit'
      }).group('06 Nuclear support').id('industrial_colonies:custom_progression/nuclearcraft/subatomic_liquifier')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Antenna mast above logic reporting board, wired modem and supported radio enclosure. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('create_aeronautics_automated_logistics:ship_transponder', ['  A  ', '  B  ', 'CDEDC', 'FGHGF'], {
        A: 'create:shaft',
        B: 'createaddition:electrum_wire',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:circuit_board',
        E: 'ae2:logic_processor',
        F: 'tfmg:nickel_sheet',
        G: 'tfmg:steel_frame',
        H: 'computercraft:wired_modem_full'
      }).group('Chain 03 / 08 Ship controls').id('industrial_colonies:custom_progression/create_aeronautics_automated_logistics/ship_transponder')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Quantum substrate and superconducting interconnect before the approved final processor cooling assembly; no finished-processor dependency. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['advanced_ae:printed_quantum_processor'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:printed_engineering_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_magnesium_diboride']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).group('Design 01 / 09 Quantum electronics').id('industrial_colonies:functional_design/advanced_ae/printed_quantum_processor')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Motor with precision feedback and AE2 logic instead of the disliked NuclearCraft circuit. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('nuclearcraft:servo', [' A ', 'BCD', 'EFE'], {
      A: 'create:shaft',
      B: 'create:precision_mechanism',
      C: 'tfmg:electric_motor',
      D: 'ae2:logic_processor',
      E: 'tfmg:rubber_sheet',
      F: 'tfmg:copper_wire'
    }).group('Design 01 / 06 Nuclear components').id('industrial_colonies:functional_design/nuclearcraft/servo')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Compact rechargeable power module; lithium reservoir, alloy bus and insulated contacts. No full machine frame. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['mekanism:energy_tablet'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).group('Design 02 / 03 Copper electrical').id('industrial_colonies:functional_design/mekanism/energy_tablet')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Terminal-tier matter/energy link with teleportation core, quantum controllers and isolated power banks. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:quantum_entangloporter', ['ABCBA', 'DEFED', 'CGHGC', 'DIJID', 'ABCBA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'create:refined_radiance',
        C: 'ae2:fluix_smart_dense_cable',
        D: 'tfmg:circuit_board',
        E: 'advanced_ae:quantum_processor',
        F: 'mekanism:teleportation_core',
        G: 'mekanism:ultimate_energy_cube',
        H: 'tfmg:steel_frame',
        I: 'tfmg:rubber_sheet',
        J: 'mekanism:ultimate_control_circuit'
      }).group('Design 02 / 09 Quantum logistics').id('industrial_colonies:functional_design/mekanism/quantum_entangloporter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Monitor face above a populated logic/calculation/engineering computer chassis; wiring and buffered power below. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('computercraft:computer_advanced', ['AAAAA', 'ABBBA', 'CDEFC', 'GHGHG', 'IJJJI'], {
        A: 'minecraft:glass',
        B: 'tfmg:circuit_board',
        C: 'tfmg:rubber_sheet',
        D: 'ae2:calculation_processor',
        E: 'ae2:logic_processor',
        F: 'ae2:engineering_processor',
        G: 'tfmg:copper_wire',
        H: 'tfmg:capacitor_item',
        I: 'tfmg:nickel_sheet',
        J: 'tfmg:steel_frame'
      }).group('Chain 03 / ComputerCraft').id('industrial_colonies:computercraft/computer/advanced_upgrade')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Seven-wide central core: entangled reference, opposed quantum banks, optical enclosure and ultimate control; no antimatter requirement before SPS. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('advanced_ae:quantum_core', ['ABCCCBA', 'BDEEEDB', 'CFGFGFC', 'CEHIHEC', 'CFGFGFC', 'BDJEJDB', 'ABCCCBA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'createmetallurgy:tungsten_sheet',
        C: 'create:refined_radiance',
        D: 'tfmg:circuit_board',
        E: 'ae2:quartz_vibrant_glass',
        F: 'ae2:fluix_smart_dense_cable',
        G: 'advanced_ae:quantum_processor',
        H: 'ae2:quantum_entangled_singularity',
        I: 'tfmg:steel_frame',
        J: 'mekanism:ultimate_control_circuit'
      }).id('industrial_colonies:v3_ae2/quantum_core')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Sensing window, populated signal board and calculation readout; insulated wiring for life-support monitoring. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('ad_astra:oxygen_sensor', [' A ', 'BCD', 'EFE'], {
      A: 'minecraft:glass',
      B: 'tfmg:transistor_item',
      C: 'tfmg:circuit_board',
      D: 'ae2:calculation_processor',
      E: 'tfmg:rubber_sheet',
      F: 'tfmg:copper_wire'
    }).id('industrial_colonies:space/life_support/oxygen_sensor')
})

ServerEvents.recipes(event => {
  // Review revision: Gyroscope centered between magnetic supports, calibration above and calculation below. Keeps the praised materials. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('simulated:gimbal_sensor', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:potentiometer',
      B: 'tfmg:magnetic_alloy_sheet',
      C: 'simulated:gyroscopic_mechanism',
      D: 'tfmg:circuit_board',
      E: 'ae2:calculation_processor'
    }).id('industrial_colonies:space/navigation/gimbal_sensor')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Gyroscopic reference and opposing magnetic coils around supported electronics; no generic machine ring. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('rocketnautics:magnetic_stabilizer', ['  A  ', 'BCDCB', 'EFGFE', 'BCDCB', '  H  '], {
        A: 'simulated:gyroscopic_mechanism',
        B: 'tfmg:nickel_sheet',
        C: 'tfmg:electromagnetic_coil',
        D: 'tfmg:magnetic_alloy_sheet',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'tfmg:steel_frame',
        H: 'create:shaft'
      }).id('industrial_colonies:space_coverage/magnetic_stabilizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Fuel manifold and valves over tungsten combustion throat, titanium shell and lightning-dragon gate before departure. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('rocketnautics:rocket_thruster', ['ABABA', 'CDEDC', 'CFGFC', 'CBHBC', 'ACCCA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'tfmg:steel_pipe',
        C: 'createmetallurgy:tungsten_sheet',
        D: 'tfmg:steel_fluid_valve',
        E: 'iceandfire:lightning_dragon_blood',
        F: 'tfmg:steel_mechanism',
        G: 'tfmg:electric_motor',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:space_coverage/rocket_thruster')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Inspection-window growth vessel with temperature-control elements and refined-obsidian footings; no unrelated fluorite input. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:chemical_crystallizer', ['  A  ', 'BCDCB', 'BEDEB', 'FGHGF', 'IJJJI'], {
        A: 'mekanism:basic_chemical_tank',
        B: 'tfmg:nickel_sheet',
        C: 'minecraft:glass',
        D: 'tfmg:steel_chemical_vat',
        E: 'tfmg:capacitor_item',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'ae2:calculation_processor',
        I: 'mekanism:ingot_refined_obsidian',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_nuclear/chemical_crystallizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dual reagent inlets surround a chemically resistant HDPE-lined vessel; drain below and isolated control bank. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:chemical_dissolution_chamber', ['A B A', 'CDEDC', 'FGEGF', 'FBHBF', 'IJKJI'], {
        A: 'mekanism:basic_chemical_tank',
        B: 'tfmg:steel_pipe',
        C: 'create:mechanical_pump',
        D: 'tfmg:rubber_sheet',
        E: 'tfmg:steel_chemical_vat',
        F: 'mekanism:hdpe_sheet',
        G: 'minecraft:glass',
        H: 'tfmg:steel_frame',
        I: 'tfmg:nickel_sheet',
        J: 'tfmg:circuit_board',
        K: 'mekanism:ultimate_control_circuit'
      }).id('industrial_colonies:mekanism_nuclear/chemical_dissolution_chamber')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Side-fed injection manifold enters a purification chamber, separated from its shielded control cabinet. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:chemical_injection_chamber', ['A  B', 'CCDE', 'FGGH', 'IJJI'], {
        A: 'mekanism:basic_chemical_tank',
        B: 'mekanism:elite_control_circuit',
        C: 'tfmg:steel_pipe',
        D: 'tfmg:rubber_sheet',
        E: 'tfmg:circuit_board',
        F: 'create:mechanical_pump',
        G: 'mekanism:purification_chamber',
        H: 'tfmg:copper_wire',
        I: 'tfmg:nickel_sheet',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_nuclear/chemical_injection_chamber')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Twin wash tanks feed a visible washing trough; opposing pumps and a supported electronic base. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:chemical_washer', ['A B A', 'BCCCB', 'DEEED', 'FGHGF', 'IJJJI'], {
        A: 'tfmg:steel_fluid_tank',
        B: 'tfmg:steel_pipe',
        C: 'minecraft:glass',
        D: 'create:mechanical_pump',
        E: 'tfmg:steel_chemical_vat',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'ae2:calculation_processor',
        I: 'tfmg:nickel_sheet',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_nuclear/chemical_washer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Distinct import/export face, routing electronics below and insulated base; compact network adapter. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:interface', ['A  A', 'BCBD', 'EFGE', 'HCCH'], {
        A: 'minecraft:glass',
        B: 'ae2:annihilation_core',
        C: 'ae2:formation_core',
        D: 'ae2:logic_processor',
        E: 'tfmg:copper_wire',
        F: 'tfmg:circuit_board',
        G: 'ae2:fluix_smart_cable',
        H: 'tfmg:rubber_sheet'
      }).id('industrial_colonies:digital_core/interface')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Pattern slots across the face, calculation/engineering row and an existing interface for item dispatch. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:pattern_provider', ['AAAA', 'BCDB', 'EFGE', 'HIIH'], {
        A: 'ae2:blank_pattern',
        B: 'ae2:logic_processor',
        C: 'ae2:calculation_processor',
        D: 'ae2:engineering_processor',
        E: 'tfmg:copper_wire',
        F: 'ae2:interface',
        G: 'tfmg:circuit_board',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:digital_core/pattern_provider')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Adjustable electronic regulator; remove the oversized motor and full transformer that made the draft too costly. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('electroenergetics:voltage_regulator', ['ABA', 'CDC', 'EFE'], {
      A: 'tfmg:copper_wire',
      B: 'tfmg:capacitor_item',
      C: 'tfmg:potentiometer',
      D: 'tfmg:circuit_board',
      E: 'tfmg:rubber_sheet',
      F: 'tfmg:cast_iron_sheet'
    }).id('industrial_colonies:high_voltage/voltage_regulator')
})

ServerEvents.recipes(event => {
  // Review revision: Steel skin fastened around one frame; simple casing construction. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('2x tfmg:steel_casing', ['AAA', 'BCB', 'AAA'], {
      A: 'tfmg:heavy_plate',
      B: 'tfmg:screw',
      C: 'tfmg:steel_frame'
    }).id('industrial_colonies:ownership/steel_casing')
})

ServerEvents.recipes(event => {
  // Review revision: Colony information interface: goggles/rack reference, peripheral enclosure and populated reporting board. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('advancedperipherals:colony_integrator', [' A ', 'BCD', ' E '], {
      A: 'minecolonies:build_goggles',
      B: 'minecolonies:blockminecoloniesrack',
      C: 'advancedperipherals:peripheral_casing',
      D: 'computercraft:wired_modem_full',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:digital_core/colony_integrator')
})

ServerEvents.recipes(event => {
  // Review revision: Existing gearshift receives an inverted redstone control; preserves recognizable native function. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('create_connected:inverted_gearshift', [' A ', 'BCB', ' D '], {
      A: 'minecraft:redstone_torch',
      B: 'create:shaft',
      C: 'create:gearshift',
      D: 'create:andesite_alloy'
    }).id('industrial_colonies:priority/create_connected/inverted_gearshift')
})

ServerEvents.recipes(event => {
  // Review revision: Steel pipe bundle reinforced by heavy plate; no mechanism consumed for passive pipe. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('6x tfmg:industrial_pipe', ['AAA', 'BBB', 'AAA'], {
      A: 'tfmg:heavy_plate',
      B: 'tfmg:steel_pipe'
    }).id('industrial_colonies:fluid_infrastructure/industrial_pipe')
})

ServerEvents.recipes(event => {
  // Review revision: Graphite sliding contacts held in insulated metal supports around the shaft connection. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('electroenergetics:alternator_brushes', ['ABA', 'CDC', ' E '], {
      A: 'tfmg:copper_wire',
      B: 'createmetallurgy:graphite',
      C: 'tfmg:rubber_sheet',
      D: 'tfmg:cast_iron_sheet',
      E: 'create:shaft'
    }).id('industrial_colonies:grid/alternator_brushes')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Overhead geared motor turns a central shaft and mixer blade inside the supported vessel. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:industrial_mixer', ['  A  ', 'BCDCB', 'B D B', 'BEFEB', 'GHHHG'], {
        A: 'tfmg:electric_motor',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:steel_mechanism',
        D: 'create:shaft',
        E: 'tfmg:steel_casing',
        F: 'tfmg:mixer_blade',
        G: 'tfmg:nickel_sheet',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:heavy_industry/industrial_mixer')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Graphite casting surface on simple heat-resistant legs; modest construction change. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('createmetallurgy:casting_table', ['AAA', 'B B', 'C C'], {
      A: 'createmetallurgy:graphite',
      B: 'tfmg:cast_iron_sheet',
      C: 'createaddition:iron_rod'
    }).id('industrial_colonies:priority/createmetallurgy/casting_table')
})

ServerEvents.recipes(event => {
  // Review revision: Larger terminal adds electrum conductor and reinforced mount around existing connector. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('2x createaddition:large_connector', ['ABA', 'CDC', 'EFE'], {
      A: 'tfmg:copper_wire',
      B: 'createaddition:electrum_wire',
      C: 'tfmg:rubber_sheet',
      D: 'createaddition:connector',
      E: 'tfmg:screw',
      F: 'tfmg:cast_iron_sheet'
    }).id('industrial_colonies:priority/createaddition/large_connector')
})

ServerEvents.recipes(event => {
  // Review revision: Insulated copper contact and mounting screw, four small connectors. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('4x createaddition:connector', [' A ', 'BCB', ' D '], {
      A: 'tfmg:copper_wire',
      B: 'tfmg:rubber_sheet',
      C: 'create:copper_sheet',
      D: 'tfmg:screw'
    }).id('industrial_colonies:priority/createaddition/connector')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Precision drive gains the approved feedback servo, engineering calculation and calibrated supports; a real subassembly upgrade. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:advanced_precision_mechanism'], 'create:precision_mechanism', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:servo']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:potentiometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:nickel_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:precision_mechanism'}})).loops(1).group('04 Control mechanisms').id('industrial_colonies:custom_progression/createmechanisms/advanced_precision_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Buffered storage controller with addressing processor, reinforced interconnect and reserve charge. No storage cell consumed to make the controller needed for that cell. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:advanced_storage_mechanism'], 'createmechanisms:storage_mechanism', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:accumulation_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createmechanisms:storage_mechanism'}})).loops(1).group('04 Control mechanisms').id('industrial_colonies:custom_progression/createmechanisms/advanced_storage_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Logic mechanism uses the approved logic processor and starter switching on a coated board, rather than another fully completed board inside it. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:logic_mechanism'], 'create:precision_mechanism', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:precision_mechanism'}})).loops(1).group('04 Control mechanisms').id('industrial_colonies:custom_progression/createmechanisms/logic_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Zinc drive receives rubber bushings in two staged fits, an alloy mounting hub and a final fastener; early materials retain a recurring role. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:rubber_mechanism'], 'createmechanisms:zinc_mechanism', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:andesite_alloy']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createmechanisms:zinc_mechanism'}})).loops(1).group('04 Control mechanisms').id('industrial_colonies:custom_progression/createmechanisms/rubber_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Radiance nuclear control builds on the shielded uranium drive with populated electronics, refined switching and tungsten thermal protection. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:nuclear_mechanism'], 'createmechanisms:uranium_mechanism', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createmetallurgy:tungsten_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createmechanisms:uranium_mechanism'}})).loops(1).group('06 Nuclear components').id('industrial_colonies:custom_progression/createmechanisms/nuclear_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Opposed superconducting restraint coils and capacitor feedback surround a central frame with isolated sensor boards; containment layout visibly braces the field instead of loose expensive ingredients. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:event_horizon_stabilizer', ['ABCCCBA', 'BDEFEDB', 'CGHIHGC', 'CDJKJDC', 'CGHIHGC', 'BDEFEDB', 'ABCCCBA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'createmetallurgy:tungsten_sheet',
        C: 'create:refined_radiance',
        D: 'nuclearcraft:coil_bscco',
        E: 'advanced_ae:quantum_processor',
        F: 'mekanism:ultimate_control_circuit',
        G: 'advanced_ae:quantum_alloy_plate',
        H: 'tfmg:circuit_board',
        I: 'tfmg:rubber_sheet',
        J: 'electroenergetics:high_voltage_capacitor',
        K: 'tfmg:steel_frame'
      }).group('06 Nuclear support').id('industrial_colonies:custom_progression/nuclearcraft/event_horizon_stabilizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Black-hole optical concentrator: diamond focusing array and a laser alignment axis, superconducting correction coils, quantum feedback and tungsten/titanium support. One per craft; six required by the installed chamber guide. Existing pack items; proposed editor recipe, no gameplay export. Rare-metal tier revision: Iridium optical alignment mounts stabilize the focused high-power beam assembly.
    event.recipes.create.mechanical_crafting('nuclearcraft:photon_concentrator', ['ABCCCBA', 'DEFFFED', 'GHIJIHG', 'DEKKKED', 'ABLLLBA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'createmetallurgy:tungsten_sheet',
        C: 'minecraft:glass',
        D: 'create:refined_radiance',
        E: 'advanced_ae:quantum_alloy_plate',
        F: 'minecraft:diamond',
        G: 'nuclearcraft:iridium_ingot',
        H: 'nuclearcraft:coil_bscco',
        I: 'ae2:calculation_processor',
        J: 'mekanism:laser',
        K: 'tfmg:circuit_board',
        L: 'tfmg:steel_frame'
      }).group('Chain 03 / 06 Nuclear support').id('industrial_colonies:custom_progression/nuclearcraft/photon_concentrator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Expensive shielded uranium-handling drive: doubled uranium mounting plates, controlled servo motion, engineering feedback and reinforced electronic isolation. Existing pack items; proposed editor recipe, no gameplay export. Rare-metal tier revision: Platinum control contacts and a durable osmium handling mount in the deliberately expensive nuclear material-handling drive.
    event.recipes.create.sequenced_assembly(['createmechanisms:uranium_mechanism'], 'tfmg:steel_mechanism', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'immersiveengineering:plate_uranium']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'immersiveengineering:plate_uranium']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'immersiveengineering:plate_lead']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:servo']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:platinum_plate']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ingot_osmium']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_mechanism'}})).loops(1).group('06 Nuclear components').id('industrial_colonies:custom_progression/createmechanisms/uranium_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Feedback servo drives a guided piston bank with titanium load feet; distinct linear actuator silhouette. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:actuator', ['  A  ', 'BCCCB', 'BDAEB', 'FGGGF'], {
        A: 'create:shaft',
        B: 'tfmg:nickel_sheet',
        C: 'minecraft:piston',
        D: 'nuclearcraft:servo',
        E: 'tfmg:steel_mechanism',
        F: 'rocketnautics:titanium_alloy_sheet',
        G: 'tfmg:steel_frame'
      }).group('Design 01 / 06 Nuclear components').id('industrial_colonies:functional_design/nuclearcraft/actuator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Approved optical ingredients remain: tinted lens/amethyst detector and aluminum case. Logic/calculation readout sits below the lens, with insulation around it. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('simulated:optical_sensor', ['ABBA', 'ACDA', 'EFGE', 'AAAA'], {
        A: 'tfmg:aluminum_sheet',
        B: 'minecraft:tinted_glass',
        C: 'minecraft:amethyst_shard',
        D: 'tfmg:circuit_board',
        E: 'tfmg:rubber_sheet',
        F: 'ae2:calculation_processor',
        G: 'ae2:logic_processor'
      }).id('industrial_colonies:space/navigation/optical_sensor')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Observer probe, populated decoder and calculation output to a wired modem, packed into an occupied 3x3 crafting grid. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('advancedperipherals:block_reader', [' A ', 'BCD', 'EFE'], {
      A: 'minecraft:observer',
      B: 'tfmg:circuit_board',
      C: 'advancedperipherals:peripheral_casing',
      D: 'computercraft:wired_modem_full',
      E: 'tfmg:rubber_sheet',
      F: 'ae2:calculation_processor'
    }).id('industrial_colonies:digital_core/block_reader')
})

ServerEvents.recipes(event => {
  // Review revision: Power-throughput metering interface: adjustable current limit, meter and inline conductor connect a populated reporting board to the computer network. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('advancedperipherals:energy_detector', [' AB', 'CDE', 'FGF'], {
      A: 'tfmg:voltmeter',
      B: 'tfmg:potentiometer',
      C: 'tfmg:copper_wire',
      D: 'advancedperipherals:peripheral_casing',
      E: 'computercraft:wired_modem_full',
      F: 'tfmg:rubber_sheet',
      G: 'tfmg:circuit_board'
    }).id('industrial_colonies:digital_core/energy_detector')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: One rare osmium catalyst assembly rather than four structural ingots. Nickel shell and a fan feed oxygen into the enrichment unit; electronics regulate the process. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:purification_chamber', ['  A  ', 'BCDCB', 'BEFGB', 'HIJIH'], {
        A: 'create:encased_fan',
        B: 'tfmg:nickel_sheet',
        C: 'tfmg:steel_pipe',
        D: 'mekanism:basic_chemical_tank',
        E: 'mekanism:enrichment_chamber',
        F: 'tfmg:steel_frame',
        G: 'mekanism:ingot_osmium',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:copper_wire',
        J: 'tfmg:circuit_board'
      }).id('industrial_colonies:mekanism_nuclear/purification_chamber')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Solar aperture and bright neutron-focusing elements sit above the reaction chamber and separate control bank; gas connections below, not generic stacked tanks. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:solar_neutron_activator', ['AAAAA', 'BCBCB', 'DEFED', 'GHIHG', 'DEJED'], {
        A: 'minecraft:tinted_glass',
        B: 'create:refined_radiance',
        C: 'mekanism:ingot_refined_glowstone',
        D: 'tfmg:nickel_sheet',
        E: 'tfmg:steel_pipe',
        F: 'tfmg:steel_frame',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:circuit_board',
        I: 'mekanism:ultimate_control_circuit',
        J: 'mekanism:basic_chemical_tank'
      }).id('industrial_colonies:mekanism_nuclear/solar_neutron_activator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Higher-grade atomic/reinforced buses for a storage-specific buffered processor. Retains reserve charge and shielding; no generic fluix filler. Existing pack items; proposed editor recipe, no gameplay export. Rare-metal tier revision: Platinum memory-addressing contacts; one nugget rather than an entire ingot per storage processor.
    event.recipes.create.sequenced_assembly(['megacells:accumulation_processor'], 'megacells:printed_accumulation_processor', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:platinum_nugget']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:printed_accumulation_processor'}})).loops(1).id('industrial_colonies:v3_ae2/accumulation_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Steel-vessel upgrade adds a continuous refractory liner for molten materials; drive mounting outside the hot liner and a dedicated lower drain. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:fireproof_chemical_vat', ['A   A', 'BCCCB', 'BCDCB', 'BEFEB', 'BBABB'], {
        A: 'tfmg:steel_pipe',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:fireproof_bricks',
        D: 'tfmg:steel_chemical_vat',
        E: 'tfmg:screw',
        F: 'tfmg:steel_mechanism'
      }).id('industrial_colonies:fluid_infrastructure/fireproof_chemical_vat')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Nickel lining and steel walls upgrade a cast-iron vessel; lower structural drive support and drain, avoiding redundant frames. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:steel_chemical_vat', ['A   A', 'BCDCB', 'B E B', 'BFGFB', 'BBABB'], {
        A: 'tfmg:steel_pipe',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:nickel_sheet',
        D: 'minecraft:glass',
        E: 'tfmg:cast_iron_chemical_vat',
        F: 'tfmg:screw',
        G: 'tfmg:steel_mechanism'
      }).id('industrial_colonies:fluid_infrastructure/steel_chemical_vat')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mechanical cutting head, heavy guard and shaft on a geared steel drive; no early electronic bootstrap lock. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:weathered_iron_mechanical_drill', ['  A  ', ' BBB ', 'CDEDC', 'FGGGF'], {
        A: 'minecraft:iron_pickaxe',
        B: 'tfmg:heavy_plate',
        C: 'create:large_cogwheel',
        D: 'create:shaft',
        E: 'create:mechanical_drill',
        F: 'tfmg:cast_iron_sheet',
        G: 'tfmg:steel_mechanism'
      }).id('industrial_colonies:priority/createcasing/weathered_iron_mechanical_drill')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Early inventory access throat and redstone-level reporting in a brass housing, without advanced AE2 dependencies. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('create_connected:inventory_access_port', [' A ', 'BCB', 'DED'], {
      A: 'minecraft:hopper',
      B: 'create:electron_tube',
      C: 'create:brass_casing',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:copper_wire'
    }).id('industrial_colonies:priority/create_connected/inventory_access_port')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Brass control-panel enclosure with display tubes and populated calculation/logic readout, rather than a steel nuclear frame. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('create:factory_gauge', ['AAAA', 'BCCB', 'DEFD', 'GHHG'], {
        A: 'minecraft:glass',
        B: 'create:electron_tube',
        C: 'tfmg:circuit_board',
        D: 'tfmg:rubber_sheet',
        E: 'ae2:calculation_processor',
        F: 'ae2:logic_processor',
        G: 'create:brass_sheet',
        H: 'create:brass_casing'
      }).id('industrial_colonies:priority/create/factory_gauge')
  }
})

ServerEvents.recipes(event => {
  // Second October15 review: Review revision: Rare osmiridium frame joints and iridium inner mount with tungsten refractory crown; two casing outputs share the Radiance/steel structure. Cost rises in late fusion without controller electronics in every wall. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
  event.shaped('2x nuclearcraft:fusion_reactor_casing', ['ABA', 'CDC', 'AEA'], {
      A: 'nuclearcraft:osmiridium_ingot',
      B: 'createmetallurgy:tungsten_sheet',
      C: 'create:refined_radiance',
      D: 'tfmg:steel_frame',
      E: 'nuclearcraft:iridium_ingot'
    }).group('06 Nuclear structures').id('industrial_colonies:custom_progression/nuclearcraft/fusion_reactor_casing')
})

ServerEvents.recipes(event => {
  // Second October15 review: Review revision: One power-diode block: semiconductor junction and insulated leads on a full cast-iron structural base. Output reduced from four to one as requested. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
  event.shaped('tfmg:electric_diode', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:p_semiconductor',
      B: 'tfmg:copper_wire',
      C: 'tfmg:n_semiconductor',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:cast_iron_block'
    }).group('03 Electronics').id('industrial_colonies:custom_progression/tfmg/electric_diode')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Adds a programmed advanced card and industrial control stage to the existing logic drive, populated board, silicon die and calculation processor. New modules have distinct programming/control jobs. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:computing_mechanism'], 'createmechanisms:logic_mechanism', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:nickel_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:advanced_card']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createmechanisms:logic_mechanism'}})).loops(1).group('04 Control mechanisms').id('industrial_colonies:custom_progression/createmechanisms/computing_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Two approved servos provide closed-loop gantry positioning rather than consuming two generic positioning mechanisms; industrial assembly arms and control electronics stay. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:assembler', ['ABBBA', 'CDDDC', 'E F E', 'GHIHG', 'JKKKJ'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'tfmg:electric_motor',
        C: 'nuclearcraft:servo',
        D: 'create:shaft',
        E: 'createcasing:industrial_iron_deployer',
        F: 'tfmg:heavy_machinery_casing',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:circuit_board',
        I: 'mekanism:elite_control_circuit',
        J: 'tfmg:nickel_sheet',
        K: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/assembler')
  }
})

ServerEvents.recipes(event => {
  // Second October15 review: Passive exchanger now uses conductive brass flow channels between nickel fins. Four outputs and the casing-scale Radiance/frame cost remain; no electronic interior block tax. Existing items only; proposed editor card, no gameplay export.
  event.shaped('4x nuclearcraft:heat_exchanger', ['ABA', 'CDC', 'ABA'], {
      A: 'tfmg:nickel_sheet',
      B: 'tfmg:brass_pipe',
      C: 'create:refined_radiance',
      D: 'tfmg:steel_frame'
    }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/heat_exchanger')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: A blank pattern provides a real programmable crafting-request payload on the basic-card assembly. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:crafting_card'], 'ae2:basic_card', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:formation_core']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:blank_pattern']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:basic_card'}})).loops(1).group('07 Digital expansion cards').id('industrial_colonies:custom_progression/ae2/crafting_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Advanced base card, engineering interlock, atomic-alloy bus and shielded package govern the annihilation core. Small electronics use reinforced packaging instead of an unrelated full machine frame. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:void_card'], 'ae2:advanced_card', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:annihilation_core']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:advanced_card'}})).loops(1).group('07 Digital expansion cards').id('industrial_colonies:custom_progression/ae2/void_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: A programmed advanced-card module gives the existing populated substrate a concrete firmware layer; retains silicon-carbide protection and calculation electronics. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['vsie:computronic_substrate'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:silicon_carbide_ingot']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:hdpe_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:advanced_card']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).group('Chain 03 / Design 01 / 08 Ship electronics').id('industrial_colonies:functional_design/vsie/computronic_substrate')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Steel electrode support, infused-alloy current bus and a magnetic shield improve early chemical-processing cost without scarce osmium/platinum/iridium. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['mekanism:electrolytic_core'], 'tfmg:steel_ingot', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:graphite_electrode']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:graphite_electrode']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_ingot'}})).loops(1).id('industrial_colonies:mekanism_components/electrolytic_core')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Industrial navigation-control interlock supplements the programmed route memory and rare-metal reference mount; not another identical processor recipe. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['vsie:warp_data_chip'], 'vsie:computronic_substrate', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'cosmowarp:memory_card']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'cosmowarp:warp_crystal']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:platinum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:iridium_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'vsie:computronic_substrate'}})).loops(1).group('Design 01 / 09 Warp navigation').id('industrial_colonies:functional_design/vsie/warp_data_chip')
  }
})

ServerEvents.recipes(event => {
  // Second October15 review: Repeatable structural glass panel uses an existing osmiridium mount instead of depending on the still-missing replacement Radiance casing reference; four outputs retained. Existing items only; proposed editor card, no gameplay export.
  event.shaped('4x advanced_ae:quantum_structure', ['ABA', 'BCB', 'ABA'], {
      A: 'rocketnautics:titanium_alloy_sheet',
      B: 'ae2:quartz_vibrant_glass',
      C: 'nuclearcraft:osmiridium_ingot'
    }).group('Design 01 / 09 Quantum structures').id('industrial_colonies:functional_design/advanced_ae/quantum_structure')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Four physical lower-density banks now feed this density upgrade. Existing addressing electronics, shielding and rare-metal stages remain; no free fourth bank at each tier. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:cell_component_256k'], 'ae2:cell_component_64k', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_64k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_64k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_64k']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:cell_component_64k'}})).loops(1).id('industrial_colonies:v3_ae2/cell_component_256k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Actual flywheel energy storage complements the earlier stress modules, sensor and controlled kinetic bridge. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_256k'], 'appliedcreate:stress_storage_component_64k', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_64k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_64k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create_connected:kinetic_bridge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:rotation_speed_controller']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:flywheel']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:stress_storage_component_64k'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_256k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Adds a real 100mB liquid-helium filling stage per entangled pair. Existing ice-dragon blood, moon resource and quantum timing remain. The installed Supercooler already makes this fluid; no invented Mekanism helium chemical. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['2x ae2:quantum_entangled_singularity'], 'ae2:singularity', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_infused_dust']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'cosmowarp:moon_crystal']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'iceandfire:ice_dragon_blood']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.base_filling('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', Fluid.of('nuclearcraft:liquid_helium', 100)]),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:singularity'}})).loops(1).id('industrial_colonies:interstellar/quantum_entangled_pair')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Programmed computronic substrate and a refined control interlock mount the route reference in osmiridium. Retains iridium, quantum processor, cold blood and exact native-route removal. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['cosmowarp:warp_crystal'], 'cosmowarp:moon_crystal', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quantum_entangled_singularity']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'cosmowarp:memory_card']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'iceandfire:ice_dragon_blood']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:iridium_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'vsie:computronic_substrate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:osmiridium_ingot']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'cosmowarp:moon_crystal'}})).loops(1).id('industrial_colonies:interstellar/unsigned_route_crystal')
  }
})

ServerEvents.recipes(event => {
  // Second October15 review: Player-bound memory card and complete reporting board gain an explicit access-control logic processor; ordinary three-by-three construction remains. Existing items only; proposed editor card, no gameplay export.
  event.shaped('advancedperipherals:inventory_manager', [' A ', 'BCD', 'EFE'], {
      A: 'minecraft:hopper',
      B: 'advancedperipherals:memory_card',
      C: 'advancedperipherals:peripheral_casing',
      D: 'computercraft:wired_modem_full',
      E: 'tfmg:rubber_sheet',
      F: 'ae2:logic_processor'
    }).id('industrial_colonies:digital_core/inventory_manager')
})

ServerEvents.recipes(event => {
  // Second October15 review: Signal-conversion module adds output-current limiting and clear insulation on the modem/board interface; no advanced storage or rare-metal gate. Existing items only; proposed editor card, no gameplay export.
  event.shaped('createaddition:digital_adapter', [' A ', 'BCD', 'EFE'], {
      A: 'tfmg:transistor_item',
      B: 'tfmg:copper_wire',
      C: 'tfmg:circuit_board',
      D: 'computercraft:wired_modem',
      E: 'tfmg:rubber_sheet',
      F: 'tfmg:resistor'
    }).id('industrial_colonies:tfmg_heavy_electrical/digital_adapter')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Four physical lower-density banks now feed this density upgrade. Existing addressing electronics, shielding and rare-metal stages remain; no free fourth bank at each tier. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:cell_component_64k'], 'ae2:cell_component_16k', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_16k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_16k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_16k']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:cell_component_16k'}})).loops(1).id('industrial_colonies:v3_ae2/cell_component_64k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: A real AE2 item interface, twin fluid-control valves and approved power transformer form the chamber port around its neutronium frame, platinum contacts and control boards. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:chamber_port', ['ABCDA', 'EFGFE', 'HIJIH', 'EFKFE', 'ADHBA'], {
        A: 'nuclearcraft:neutronium_frame',
        B: 'nuclearcraft:platinum_plate',
        C: 'tfmg:transformer',
        D: 'electroenergetics:heavily_insulated_wire',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'mekanism:ultimate_control_circuit',
        H: 'tfmg:steel_pipe',
        I: 'tfmg:steel_fluid_valve',
        J: 'ae2:interface',
        K: 'ae2:engineering_processor'
      }).group('Late quantum - Kugelblitz Chamber').id('industrial_colonies:kugelblitz/chamber_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Second October15 review: Two independent conversion-control channels flank the approved transformer, with superconducting windings, platinum contacts and osmiridium mounts retained. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:quantum_transformer', ['ABCBD', 'EFGFH', 'IJKJI', 'HFJFE', 'DBCBA'], {
        A: 'nuclearcraft:osmiridium_ingot',
        B: 'advanced_ae:quantum_alloy_plate',
        C: 'minecraft:glass',
        D: 'rocketnautics:titanium_alloy_sheet',
        E: 'nuclearcraft:platinum_plate',
        F: 'nuclearcraft:coil_bscco',
        G: 'advanced_ae:quantum_processor',
        H: 'electroenergetics:heavily_insulated_wire',
        I: 'tfmg:circuit_board',
        J: 'mekanism:ultimate_control_circuit',
        K: 'tfmg:transformer'
      }).group('Late quantum - Kugelblitz Chamber').id('industrial_colonies:kugelblitz/quantum_transformer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Review revision: A real 1k memory bank supplies storage, logic addresses it, aluminum carries the bus and magnetic shielding protects the package. The bank must not depend on this mechanism. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['createmechanisms:storage_mechanism'], 'create:precision_mechanism', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:precision_mechanism'}})).loops(1).group('04 Control mechanisms').id('industrial_colonies:custom_progression/createmechanisms/storage_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Independent elite execution controller and ExtendedAE rack replace a deferred matrix-speed module; four accelerator lanes, concurrent schedulers and iridium mounts stay. Does not depend on an undecided machine module. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('megacells:mega_crafting_accelerator', ['ABBBBC', 'DEFFED', 'GFHIFG', 'JKKKKJ', 'CLLLLA'], {
        A: 'nuclearcraft:iridium_ingot',
        B: 'extendedae:concurrent_processor',
        C: 'rocketnautics:titanium_alloy_sheet',
        D: 'tfmg:circuit_board',
        E: 'tfmg:capacitor_item',
        F: 'ae2:crafting_accelerator',
        G: 'ae2:fluix_smart_dense_cable',
        H: 'mekanism:elite_control_circuit',
        I: 'extendedae:machine_frame',
        J: 'tfmg:nickel_sheet',
        K: 'tfmg:rubber_sheet',
        L: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_crafting_accelerator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Paired import/export interfaces share one expansion frame; separate routing control and reporting board replace two undifferentiated capacitor positions. Bidirectional cores and iridium mounts stay. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('megacells:mega_interface', ['AB  BC', 'DEFEGD', 'HIJKDH', 'LMNOML', 'CPPPPA'], {
        A: 'nuclearcraft:iridium_ingot',
        B: 'minecraft:glass',
        C: 'rocketnautics:titanium_alloy_sheet',
        D: 'ae2:annihilation_core',
        E: 'ae2:interface',
        F: 'extendedae:machine_frame',
        G: 'tfmg:rubber_sheet',
        H: 'ae2:fluix_smart_dense_cable',
        I: 'ae2:formation_core',
        J: 'ae2:logic_processor',
        K: 'ae2:calculation_processor',
        L: 'tfmg:nickel_sheet',
        M: 'tfmg:capacitor_item',
        N: 'mekanism:elite_control_circuit',
        O: 'tfmg:circuit_board',
        P: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_interface')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Provider pair sits beside an expansion rack and programmable pattern slot; switch and insulated output bay distinguish dispatch from a generic buffered interface. Iridium and execution circuitry retained. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('megacells:mega_pattern_provider', ['ABBBBC', 'DEFFED', 'GHIBHG', 'JKLMNJ', 'COOOOA'], {
        A: 'nuclearcraft:iridium_ingot',
        B: 'ae2:blank_pattern',
        C: 'rocketnautics:titanium_alloy_sheet',
        D: 'tfmg:circuit_board',
        E: 'ae2:logic_processor',
        F: 'extendedae:concurrent_processor',
        G: 'ae2:fluix_smart_dense_cable',
        H: 'extendedae:ex_pattern_provider',
        I: 'extendedae:machine_frame',
        J: 'tfmg:nickel_sheet',
        K: 'tfmg:transistor_item',
        L: 'ae2:engineering_processor',
        M: 'mekanism:elite_control_circuit',
        N: 'tfmg:rubber_sheet',
        O: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_pattern_provider')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Central expansion frame joins two native CPU units, with a separate execution interlock beneath the scheduling bank. This is a crafting workspace, not a digital item-storage cell; iridium budget retained. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('megacells:mega_crafting_unit', ['ABBBC', 'DEFED', 'GEHEG', 'DIEID', 'CJKJA'], {
        A: 'nuclearcraft:iridium_ingot',
        B: 'ae2:fluix_smart_dense_cable',
        C: 'rocketnautics:titanium_alloy_sheet',
        D: 'tfmg:circuit_board',
        E: 'extendedae:concurrent_processor',
        F: 'ae2:engineering_processor',
        G: 'ae2:crafting_accelerator',
        H: 'extendedae:machine_frame',
        I: 'ae2:crafting_unit',
        J: 'tfmg:rubber_sheet',
        K: 'mekanism:elite_control_circuit'
      }).id('industrial_colonies:ae2_high_energy/mega_crafting_unit')
  }
})

ServerEvents.recipes(event => {
  // Third October15 review: Review revision: Open graphite bowl over a heavy floor and cast-iron cradle. Fits a normal 3x3 crafting recipe; no oversized empty grid or electronics. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
  event.shaped('createmetallurgy:casting_basin', ['A A', 'ABA', 'CDC'], {
      A: 'createmetallurgy:graphite',
      B: 'tfmg:heavy_plate',
      C: 'tfmg:cast_iron_sheet',
      D: 'tfmg:cast_iron_frame'
    }).id('industrial_colonies:priority/createmetallurgy/casting_basin')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Two native providers mount in an ExtendedAE frame over a heavy-machinery casing and osmiridium supports. Radiance control rails and existing platinum contacts make this an advanced expansion, not a cheap duplicate. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('extendedae:ex_pattern_provider', ['ABBBA', 'CDEDC', 'FGHGF', 'IJJJI', 'AKLKA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'ae2:blank_pattern',
        C: 'create:refined_radiance',
        D: 'extendedae:concurrent_processor',
        E: 'tfmg:circuit_board',
        F: 'ae2:fluix_smart_dense_cable',
        G: 'ae2:pattern_provider',
        H: 'extendedae:machine_frame',
        I: 'nuclearcraft:platinum_plate',
        J: 'tfmg:capacitor_item',
        K: 'nuclearcraft:osmiridium_ingot',
        L: 'tfmg:heavy_machinery_casing'
      }).id('industrial_colonies:extendedae_coverage/ex_pattern_provider')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Superconducting feedback coils flank the voltage-regulation subassembly; existing calibration electronics elsewhere, osmiridium mounts and quantum timing remain. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:quantum_flux_regulator', ['ABCBA', 'DEFED', 'CGHGC', 'DIJID', 'ABCBA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'create:refined_radiance',
        C: 'electroenergetics:heavily_insulated_wire',
        D: 'tfmg:circuit_board',
        E: 'nuclearcraft:osmiridium_ingot',
        F: 'advanced_ae:quantum_processor',
        G: 'nuclearcraft:coil_bscco',
        H: 'electroenergetics:voltage_regulator',
        I: 'tfmg:capacitor_item',
        J: 'mekanism:ultimate_control_circuit'
      }).group('06 Nuclear support').id('industrial_colonies:custom_progression/nuclearcraft/quantum_flux_regulator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Review revision: Requested energy-themed capacity card: capacitor and lithium backup support the addressing logic on its basic-card base. Native function remains filter expansion, not energy storage. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:capacity_card'], 'ae2:basic_card', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:basic_card'}})).loops(1).group('07 Digital expansion cards').id('industrial_colonies:custom_progression/ae2/capacity_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Review revision: A rechargeable energy-tablet module feeds a capacitor through a rectifier, with insulated copper leads. Reuses the approved power subassemblies instead of loose generic transistors. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:energy_card'], 'ae2:basic_card', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:energy_tablet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:capacitor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_diode']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:basic_card'}})).loops(1).group('07 Digital expansion cards').id('industrial_colonies:custom_progression/ae2/energy_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Third October15 review: Review revision: An existing speed-upgrade module supplies the acceleration hardware, calculation schedules it and a potentiometer sets its rate; nickel carries heat away. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:speed_card'], 'ae2:advanced_card', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:upgrade_speed']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:potentiometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:nickel_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:advanced_card'}})).loops(1).group('07 Digital expansion cards').id('industrial_colonies:custom_progression/ae2/speed_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Fourth October15 review: Review revision: Compact axial drill head and shaft above one motor and one early power mechanism, insulated copper casing below. Removes the duplicated power mechanism and oversized empty side columns; no late rare metals. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:copper_mechanical_drill', [' A ', 'BCB', 'DED', 'FGF'], {
        A: 'create:mechanical_drill',
        B: 'create:copper_sheet',
        C: 'create:shaft',
        D: 'tfmg:rubber_sheet',
        E: 'tfmg:electric_motor',
        F: 'create:copper_casing',
        G: 'createmechanisms:basic_energy_mechanism'
      }).group('03 Copper electrical').id('industrial_colonies:custom_progression/createcasing/copper_mechanical_drill')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // EXPL reflective-core revision per latest rejection. Pyramid silhouette and laser amplifier retained; platinum block mirror stock flanks the amplifier, platinum plates sit beneath the diamond focus, silver blocks form the lower reflector bank and an iridium alignment mount carries the optics. Quantum timing moved to the base. Proposed expensive reflective-material assembly, not a claim that these blocks simulate optics in game. Existing rare-metal supports and pulse circuitry retained; editor only, no export.
    event.recipes.create.mechanical_crafting('nuclearcraft:expl', ['   A   ', '  BCB  ', ' DEFED ', 'GHIJIHG', 'GKLMLKG', 'NOPQPON', 'GKRHRKG'], {
        A: 'nuclearcraft:photon_concentrator',
        B: 'nuclearcraft:platinum_plate',
        C: 'minecraft:diamond',
        D: 'createmetallurgy:tungsten_sheet',
        E: 'nuclearcraft:platinum_block',
        F: 'mekanism:laser_amplifier',
        G: 'rocketnautics:titanium_alloy_sheet',
        H: 'create:industrial_iron_block',
        I: 'tfmg:capacitor_item',
        J: 'allthemodium:unobtainium_vibranium_alloy_ingot',
        K: 'allthemodium:vibranium_plate',
        L: 'createaddition:electrum_rod',
        M: 'electroenergetics:high_voltage_capacitor',
        N: 'nuclearcraft:coil_bscco',
        O: 'tfmg:circuit_board',
        P: 'create:refined_radiance',
        Q: 'advanced_ae:quantum_processor',
        R: 'tfmg:transformer'
      }).group('Late quantum - Kugelblitz Chamber').id('industrial_colonies:kugelblitz/expl')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Rebuild the wireless modem for interdimensional high-energy networking
    event.recipes.create.sequenced_assembly(['computercraft:wireless_modem_advanced'], 'computercraft:wireless_modem_normal', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:unfinished_computercraft_advanced_wireless_modem', ['industrial_colonies:unfinished_computercraft_advanced_wireless_modem', 'create:weathered_iron_block']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:unfinished_computercraft_advanced_wireless_modem', ['industrial_colonies:unfinished_computercraft_advanced_wireless_modem', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:unfinished_computercraft_advanced_wireless_modem', ['industrial_colonies:unfinished_computercraft_advanced_wireless_modem', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:unfinished_computercraft_advanced_wireless_modem', ['industrial_colonies:unfinished_computercraft_advanced_wireless_modem', 'minecraft:ender_eye']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:unfinished_computercraft_advanced_wireless_modem', ['industrial_colonies:unfinished_computercraft_advanced_wireless_modem', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:unfinished_computercraft_advanced_wireless_modem', 'industrial_colonies:unfinished_computercraft_advanced_wireless_modem')
      ]).transitionalItem('industrial_colonies:unfinished_computercraft_advanced_wireless_modem').loops(1).id('industrial_colonies:computercraft/network/advanced_wireless_modem')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Insulate TFMG copper wire and armor it for factory data networks
    event.recipes.create.sequenced_assembly(['8x computercraft:cable'], 'tfmg:copper_wire', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_cable', ['industrial_colonies:unfinished_computercraft_cable', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_cable', ['industrial_colonies:unfinished_computercraft_cable', 'create:brass_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:unfinished_computercraft_cable', 'industrial_colonies:unfinished_computercraft_cable')
      ]).transitionalItem('industrial_colonies:unfinished_computercraft_cable').loops(2).id('industrial_colonies:computercraft/network/cable')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Populate a wired network endpoint on the Brass electronics line
    event.recipes.create.sequenced_assembly(['computercraft:wired_modem'], 'computercraft:cable', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wired_modem', ['industrial_colonies:unfinished_computercraft_wired_modem', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wired_modem', ['industrial_colonies:unfinished_computercraft_wired_modem', 'ae2:printed_logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wired_modem', ['industrial_colonies:unfinished_computercraft_wired_modem', 'minecraft:repeater']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wired_modem', ['industrial_colonies:unfinished_computercraft_wired_modem', 'create:electron_tube']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wired_modem', ['industrial_colonies:unfinished_computercraft_wired_modem', 'create:brass_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:unfinished_computercraft_wired_modem', 'industrial_colonies:unfinished_computercraft_wired_modem')
      ]).transitionalItem('industrial_colonies:unfinished_computercraft_wired_modem').loops(1).id('industrial_colonies:computercraft/network/wired_modem')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Convert a wired endpoint into a short-range wireless factory modem
    event.recipes.create.sequenced_assembly(['computercraft:wireless_modem_normal'], 'computercraft:wired_modem', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wireless_modem', ['industrial_colonies:unfinished_computercraft_wireless_modem', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wireless_modem', ['industrial_colonies:unfinished_computercraft_wireless_modem', 'ae2:printed_logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wireless_modem', ['industrial_colonies:unfinished_computercraft_wireless_modem', 'minecraft:ender_pearl']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wireless_modem', ['industrial_colonies:unfinished_computercraft_wireless_modem', 'create:electron_tube']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_computercraft_wireless_modem', ['industrial_colonies:unfinished_computercraft_wireless_modem', 'create:brass_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:unfinished_computercraft_wireless_modem', 'industrial_colonies:unfinished_computercraft_wireless_modem')
      ]).transitionalItem('industrial_colonies:unfinished_computercraft_wireless_modem').loops(1).id('industrial_colonies:computercraft/network/wireless_modem')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Cut hardened TFMG planks into reusable spool blanks on the Copper electronics line
    event.recipes.industrial_colonies.copper_cutting(['tfmg:empty_spool'], 'tfmg:hardened_planks').processingTime(80).id('industrial_colonies:electronics_manufacturing/empty_spool')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Pressure-form glass, iron conductor, and TFMG fasteners into four line-insulator segments on the pre-Mekanism Railway line.
    event.recipes.industrial_colonies.railway_compacting(['4x electroenergetics:glass_insulator_segment'], [Ingredient.of('#c:glass_blocks'), Ingredient.of('#c:glass_blocks'), Ingredient.of('#c:glass_blocks'), Ingredient.of('#c:glass_blocks'), Ingredient.of('#c:wires/iron'), Ingredient.of('#c:wires/iron'), 'tfmg:screw']).id('industrial_colonies:extreme_grid/glass_insulator_segment')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Terminate a TFMG copper electrode with grid connector hardware for deliberate grounding.
    event.recipes.industrial_colonies.railway_compacting(['electroenergetics:ground_rod'], ['tfmg:copper_electrode', 'electroenergetics:connector', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:screw']).id('industrial_colonies:extreme_grid/ground_rod')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Assemble four pressure-formed segments into a suspended high-voltage insulator.
    event.recipes.industrial_colonies.railway_compacting(['electroenergetics:hanging_glass_insulator'], ['electroenergetics:glass_insulator_segment', 'electroenergetics:glass_insulator_segment', 'electroenergetics:glass_insulator_segment', 'electroenergetics:glass_insulator_segment', 'tfmg:screw', 'tfmg:screw', Ingredient.of('#c:plates/steel')]).id('industrial_colonies:extreme_grid/hanging_glass_insulator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Press a batch of canonical copper conductors into TFMG rubber insulation on the Copper line
    event.recipes.industrial_colonies.copper_compacting(['8x electroenergetics:insulated_wire'], [Ingredient.of('#c:wires/copper'), Ingredient.of('#c:wires/copper'), Ingredient.of('#c:wires/copper'), Ingredient.of('#c:wires/copper'), Ingredient.of('#c:wires/copper'), Ingredient.of('#c:wires/copper'), Ingredient.of('#c:wires/copper'), Ingredient.of('#c:wires/copper'), 'tfmg:rubber_sheet']).id('industrial_colonies:high_voltage/insulated_wire')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Upgrade the Basic Cube with the reinforced-alloy, advanced-control, and TFMG board line owned by Reinforced Systems.
    event.recipes.create.mechanical_crafting('mekanism:advanced_energy_cube', ['ABCBA', 'BDEDB', 'CEFEC', 'BDEDB', 'ABCBA'], {
        A: 'mekanism:alloy_reinforced',
        B: '#c:ingots/osmium',
        C: 'mekanism:energy_tablet',
        D: 'mekanism:advanced_control_circuit',
        E: 'tfmg:etched_circuit_board',
        F: 'mekanism:basic_energy_cube'
      }).id('industrial_colonies:mekanism/storage/advanced_energy_cube')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Re-seal the Basic chemical run in glass, rubber, and TFMG steel containment under Advanced control.
    event.recipes.industrial_colonies.industrial_iron_compacting(['8x mekanism:advanced_pressurized_tube'], ['mekanism:basic_pressurized_tube', 'mekanism:basic_pressurized_tube', 'mekanism:basic_pressurized_tube', 'mekanism:basic_pressurized_tube', 'mekanism:basic_pressurized_tube', 'mekanism:basic_pressurized_tube', 'mekanism:basic_pressurized_tube', 'mekanism:basic_pressurized_tube', 'mekanism:alloy_infused', 'mekanism:alloy_infused', 'mekanism:alloy_infused', 'mekanism:alloy_infused', 'mekanism:advanced_control_circuit', 'mekanism:advanced_control_circuit', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', Ingredient.of('#c:glass_blocks/cheap'), Ingredient.of('#c:glass_blocks/cheap'), Ingredient.of('#c:glass_blocks/cheap'), Ingredient.of('#c:glass_blocks/cheap'), 'tfmg:steel_casing', 'tfmg:steel_casing']).id('industrial_colonies:mekanism/transmission/advanced_pressurized_tube')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Bond the Basic heat run to copper spreaders, aluminum pipe, and active Create cooling hardware.
    event.recipes.industrial_colonies.industrial_iron_compacting(['8x mekanism:advanced_thermodynamic_conductor'], ['mekanism:basic_thermodynamic_conductor', 'mekanism:basic_thermodynamic_conductor', 'mekanism:basic_thermodynamic_conductor', 'mekanism:basic_thermodynamic_conductor', 'mekanism:basic_thermodynamic_conductor', 'mekanism:basic_thermodynamic_conductor', 'mekanism:basic_thermodynamic_conductor', 'mekanism:basic_thermodynamic_conductor', 'mekanism:alloy_infused', 'mekanism:alloy_infused', 'mekanism:alloy_infused', 'mekanism:alloy_infused', 'mekanism:advanced_control_circuit', 'mekanism:advanced_control_circuit', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'tfmg:aluminum_pipe', 'tfmg:aluminum_pipe', 'create:encased_fan']).id('industrial_colonies:mekanism/transmission/advanced_thermodynamic_conductor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Upgrade the Advanced chemical run with petroleum-made plastic pipe, sheet reinforcement, and service valves.
    event.recipes.industrial_colonies.weathered_iron_compacting(['8x mekanism:elite_pressurized_tube'], ['mekanism:advanced_pressurized_tube', 'mekanism:advanced_pressurized_tube', 'mekanism:advanced_pressurized_tube', 'mekanism:advanced_pressurized_tube', 'mekanism:advanced_pressurized_tube', 'mekanism:advanced_pressurized_tube', 'mekanism:advanced_pressurized_tube', 'mekanism:advanced_pressurized_tube', 'mekanism:alloy_reinforced', 'mekanism:alloy_reinforced', 'mekanism:alloy_reinforced', 'mekanism:alloy_reinforced', 'mekanism:elite_control_circuit', 'mekanism:elite_control_circuit', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet', 'tfmg:plastic_pipe', 'tfmg:plastic_pipe', 'tfmg:plastic_pipe', 'tfmg:plastic_pipe', 'tfmg:plastic_fluid_valve', 'tfmg:plastic_fluid_valve']).id('industrial_colonies:mekanism/transmission/elite_pressurized_tube')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Upgrade the Elite chemical run with plastic pressure sections, service valves, and smart steel monitoring hardware.
    event.recipes.industrial_colonies.weathered_iron_compacting(['8x mekanism:ultimate_pressurized_tube'], ['mekanism:elite_pressurized_tube', 'mekanism:elite_pressurized_tube', 'mekanism:elite_pressurized_tube', 'mekanism:elite_pressurized_tube', 'mekanism:elite_pressurized_tube', 'mekanism:elite_pressurized_tube', 'mekanism:elite_pressurized_tube', 'mekanism:elite_pressurized_tube', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:ultimate_control_circuit', 'mekanism:ultimate_control_circuit', 'tfmg:plastic_pipe', 'tfmg:plastic_pipe', 'tfmg:plastic_pipe', 'tfmg:plastic_pipe', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet', 'tfmg:plastic_fluid_valve', 'tfmg:plastic_fluid_valve', 'tfmg:steel_smart_fluid_pipe', 'tfmg:steel_smart_fluid_pipe']).id('industrial_colonies:mekanism/transmission/ultimate_pressurized_tube')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Upgrade the Elite heat run with industrial thermal channels, constantan junctions, copper spreaders, and redundant fans.
    event.recipes.industrial_colonies.weathered_iron_compacting(['8x mekanism:ultimate_thermodynamic_conductor'], ['mekanism:elite_thermodynamic_conductor', 'mekanism:elite_thermodynamic_conductor', 'mekanism:elite_thermodynamic_conductor', 'mekanism:elite_thermodynamic_conductor', 'mekanism:elite_thermodynamic_conductor', 'mekanism:elite_thermodynamic_conductor', 'mekanism:elite_thermodynamic_conductor', 'mekanism:elite_thermodynamic_conductor', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:ultimate_control_circuit', 'mekanism:ultimate_control_circuit', 'tfmg:industrial_pipe', 'tfmg:industrial_pipe', 'tfmg:industrial_pipe', 'tfmg:industrial_pipe', 'tfmg:constantan_wire', 'tfmg:constantan_wire', 'tfmg:constantan_wire', 'tfmg:constantan_wire', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'create:encased_fan', 'create:encased_fan']).id('industrial_colonies:mekanism/transmission/ultimate_thermodynamic_conductor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Press a fireproof inner vessel, lead shielding, heavy shell, and sealed service pipe into a practical two-barrel waste-handling batch.
    event.recipes.industrial_colonies.industrial_iron_compacting(['2x mekanism:radioactive_waste_barrel'], ['tfmg:steel_fluid_tank', 'tfmg:fireproof_chemical_vat', 'mekanism:ingot_lead', 'mekanism:ingot_lead', 'mekanism:ingot_lead', 'mekanism:ingot_lead', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_casing']).id('industrial_colonies:mekanism_nuclear/radioactive_waste_barrel_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] After first steel, press steel, heavy plate, and refractory wall blocks into four reinforced-furnace supports.
    event.recipes.industrial_colonies.brass_compacting(['4x tfmg:blast_furnace_reinforcement'], [Ingredient.of('#c:ingots/steel'), Ingredient.of('#c:ingots/steel'), Ingredient.of('#c:ingots/steel'), 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks']).id('industrial_colonies:steelworks/blast_furnace_reinforcement')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Build two hot-blast stove blocks from cast-iron piping, tanks, refractory masonry, and precision mechanics.
    event.recipes.create.mechanical_crafting('2x tfmg:blast_stove', ['A   A', 'AB BA', 'ABCBA', 'ADDDA', 'DDDDD'], {
        A: 'tfmg:cast_iron_pipe',
        B: 'tfmg:cast_iron_fluid_tank',
        C: 'create:precision_mechanism',
        D: 'tfmg:fireproof_bricks'
      }).id('industrial_colonies:steelworks/blast_stove')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Press six regular wall blocks into six load-bearing refractory supports without finished steel.
    event.recipes.industrial_colonies.weathered_iron_compacting(['6x tfmg:fireproof_brick_reinforcement'], ['tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks']).id('industrial_colonies:steelworks/fireproof_brick_reinforcement')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Press four fired TFMG refractory bricks into one regular blast-furnace wall block.
    event.recipes.industrial_colonies.weathered_iron_compacting(['tfmg:fireproof_bricks'], ['tfmg:fireproof_brick', 'tfmg:fireproof_brick', 'tfmg:fireproof_brick', 'tfmg:fireproof_brick']).id('industrial_colonies:steelworks/fireproof_bricks')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Convert the formed diesel cylinder into the TFMG spark-ignition cylinder with its canonical spark plug, lead, and service fasteners.
    event.recipes.industrial_colonies.industrial_iron_compacting([Item.of('tfmg:engine_cylinder[tfmg:fuel_tags={"gasoline":"c:gasoline","kerosene":"c:kerosene","naphtha":"c:naphtha"},tfmg:fuels={"gasoline":"Gasoline","kerosene":"Kerosene","naphtha":"Naphtha"}]')], ['tfmg:diesel_engine_cylinder', 'tfmg:spark_plug', 'tfmg:copper_wire', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:tfmg_heavy_electrical/engine_cylinder')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Wind a sparse copper solenoid around the steel field core, brace it with resistor-capacitor rails, and terminate it beneath the voltmeter.
    event.recipes.create.mechanical_crafting('tfmg:polarizer', ['  A  ', ' BCB ', 'DEFED', ' BCB ', ' DCD '], {
        A: 'tfmg:voltmeter',
        B: 'tfmg:capacitor_item',
        C: 'tfmg:copper_wire',
        D: '#c:plates/brass',
        E: 'tfmg:resistor',
        F: 'tfmg:steel_casing'
      }).id('industrial_colonies:electronics/polarizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Lay out the analog engine-control cabinet as an insulated wiring harness, sensor pair, discrete board, and drive linkage
    event.recipes.create.mechanical_crafting('tfmg:engine_controller', [' ABA ', 'CDEDC', 'BFGFB', ' HIH ', ' AIA '], {
        A: 'tfmg:rubber_sheet',
        B: '#c:wires/copper',
        C: 'tfmg:voltmeter',
        D: 'tfmg:capacitor_item',
        E: 'tfmg:heavy_machinery_casing',
        F: 'tfmg:transistor_item',
        G: 'tfmg:circuit_board',
        H: 'create:shaft',
        I: 'tfmg:steel_mechanism'
      }).id('industrial_colonies:engines/electronic_engine_controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Build a wildcard link on the Copper network line by masking a transmitter with a crafter cover, insulated lead, quartz frequency element, and redstone contact
    event.recipes.create.sequenced_assembly(['create_connected:redstone_link_wildcard'], 'create:transmitter', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:crafter_slot_cover']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:quartz']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:redstone']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:transmitter'}})).loops(1).id('industrial_colonies:create_connected/redstone_link_wildcard')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Turn the analog Voltmeter into a real diagnostic instrument with a TFMG board, resistor, transistor, capacitor, insulated test lead, and protected display on the Copper electronics line
    event.recipes.create.sequenced_assembly(['tfmg:multimeter'], 'tfmg:voltmeter', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:resistor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:glass_pane']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:voltmeter'}})).loops(1).id('industrial_colonies:tfmg_core/multimeter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Laminate paper around a magnetic recording sheet, copper data traces, and a small TFMG controller to manufacture two reusable floppy disks; CC's state-aware recolouring recipe remains intact
    event.recipes.create.sequenced_assembly(['2x computercraft:disk'], 'minecraft:paper', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:copper_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:paper'}})).loops(1).id('industrial_colonies:computer_network_coverage/magnetic_floppy_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Build a serviceable heater with a firebrick hot face above a large resistance coil and a steel, terminal-fed enclosure
    event.recipes.create.mechanical_crafting('electroenergetics:resistive_heater', ['AAA', 'BCB', ' D '], {
        A: 'tfmg:fireproof_bricks',
        B: 'tfmg:resistor',
        C: 'tfmg:large_coil',
        D: 'tfmg:steel_casing'
      }).id('industrial_colonies:create_addons/resistive_heater')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Equip a protected control board with a metering tank, TFMG valve, chemical-safe plastic, and its own process controller.
    event.recipes.create.sequenced_assembly(['mekanism:upgrade_chemical'], 'tfmg:circuit_board', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_chemical_tank']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_control_circuit']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:circuit_board'}})).loops(1).id('industrial_colonies:mekanism/upgrade/chemical')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Turn a steel mechanism into a powered service wand with an osmium probe, Energy Tablet, basic controller, and insulated grip.
    event.recipes.create.sequenced_assembly(['mekanism:configurator'], 'tfmg:steel_mechanism', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ingot_osmium']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:energy_tablet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_mechanism'}})).loops(1).id('industrial_colonies:mekanism_tools/configurator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Batch-press thirty-two serviceable station shell plates from TFMG heavy plate, structural frames, aluminum skins, and fire-resistant backing instead of receiving sixty-four blocks from nine plates.
    event.recipes.industrial_colonies.refined_radiance_compacting(['32x ad_astra:steel_plating'], ['tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:space/station/steel_plating')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Press sixteen pressure-service station ducts around TFMG steel pipe, tanks, and electric pumps so the first dockyard fluid network does not require off-world Desh.
    event.recipes.industrial_colonies.refined_radiance_compacting(['16x ad_astra:fluid_pipe_duct'], ['ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_fluid_tank', 'tfmg:steel_fluid_tank', 'tfmg:electric_pump', 'tfmg:electric_pump', 'tfmg:electric_pump', 'tfmg:electric_pump', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:space/station/fluid_pipe_duct')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Batch-form thirty-two instrument-ready wall panels from authored station plating, TFMG cable protection, discrete boards, and aluminum face sheets.
    event.recipes.industrial_colonies.refined_radiance_compacting(['32x ad_astra:steel_panel'], ['ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:circuit_board', 'tfmg:circuit_board', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:space/station/steel_panel')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Planetary Industry] Stamp canonical Desh ingots into plates only on the Refined Radiance manufacturing press.
    event.custom({type: 'industrial_colonies:refined_radiance_pressing', ingredients: [{item: 'ad_astra:desh_ingot'}], results: [{id: 'ad_astra:desh_plate'}]}).id('industrial_colonies:planetary/desh/plate')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Planetary Industry] Stamp canonical Ostrum ingots into plates only on the Refined Radiance manufacturing press.
    event.recipes.industrial_colonies.refined_radiance_pressing(['ad_astra:ostrum_plate'], 'ad_astra:ostrum_ingot').id('industrial_colonies:planetary/ostrum/plate')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Planetary Industry] Stamp canonical Calorite ingots into plates only on the Refined Radiance manufacturing press.
    event.recipes.industrial_colonies.refined_radiance_pressing(['ad_astra:calorite_plate'], 'ad_astra:calorite_ingot').id('industrial_colonies:planetary/calorite/plate')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Forge one steel ingot through three reductions on the proven Brass precision press; this bootstraps the Heavy Plate needed to construct the later Railway heavy-industrial line
    event.recipes.create.sequenced_assembly(['tfmg:heavy_plate'], Ingredient.of('#c:ingots/steel'), [
        event.recipes.industrial_colonies.weathered_iron_pressing('tfmg:unprocessed_heavy_plate', 'tfmg:unprocessed_heavy_plate'),
        event.recipes.industrial_colonies.weathered_iron_pressing('tfmg:unprocessed_heavy_plate', 'tfmg:unprocessed_heavy_plate'),
        event.recipes.industrial_colonies.weathered_iron_pressing('tfmg:unprocessed_heavy_plate', 'tfmg:unprocessed_heavy_plate')
      ]).transitionalItem('tfmg:unprocessed_heavy_plate').loops(1).id('industrial_colonies:tfmg_core/heavy_plate')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Repack a TFMG exhaust with two acoustic baffles, rubber isolation, an aluminum jacket, and a pressure-rated outlet
    event.recipes.create.sequenced_assembly(['createdieselgenerators:engine_silencer'], 'tfmg:exhaust', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:white_wool']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:white_wool']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:exhaust'}})).loops(1).id('industrial_colonies:diesel_generators_coverage/engine_silencer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Construct the huge diesel generator as two complete large diesel sets around a synchronized TFMG engine controller and crankshaft, with turbocharged piston banks, fuel tanks, gearbox, and a full heavy bed; no turbine hardware is used
    event.recipes.create.mechanical_crafting('createdieselgenerators:huge_diesel_engine', ['A B A', 'C D C', 'E F E', 'G H G', 'IIIII'], {
        A: 'createdieselgenerators:engine_turbocharger',
        B: 'tfmg:engine_controller',
        C: 'createdieselgenerators:engine_piston',
        D: 'tfmg:large_engine',
        E: 'createdieselgenerators:large_diesel_engine',
        F: 'tfmg:crankshaft',
        G: 'tfmg:steel_fluid_tank',
        H: 'tfmg:engine_gearbox',
        I: 'tfmg:heavy_plate'
      }).id('industrial_colonies:engines/huge_diesel_engine')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Lay out a steel-framed Basic power substation: parallel Basic cable rails join external connectors through paired cable hubs, an induction core, Basic Cube, transformer, and Basic control circuit.
    event.recipes.create.mechanical_crafting('mekanism:basic_induction_provider', [' ABA ', ' CCC ', 'DEFED', ' CGC ', ' AHA '], {
        A: 'tfmg:steel_frame',
        B: 'mekanism:basic_control_circuit',
        C: 'mekanism:basic_universal_cable',
        D: 'electroenergetics:connector',
        E: 'tfmg:steel_cable_hub',
        F: 'mekanism:induction_casing',
        G: 'mekanism:basic_energy_cube',
        H: 'tfmg:transformer'
      }).id('industrial_colonies:mekanism/induction/basic_provider')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Instrument the 4k matrix inside its Andesite housing with a cogged precision load path, dedicated stress processor and meter, TFMG copper winding, and rubber vibration isolation
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_4k'], 'appliedcreate:andesite_stress_cell_housing', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_4k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:cogwheel']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:stressometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_spool']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:andesite_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_4k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Build the isotope separator as a restrained five-stage rotor tower with magnetic bearings, paired chemical buffers, titanium armor, TFMG frame and transformer base, plus plastic-isolated complementary high-speed control
    event.recipes.create.mechanical_crafting('mekanism:isotopic_centrifuge', [' ABA ', 'CDCDC', 'EFGHE', 'IJKJI', 'LMNML'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:rotor',
        D: 'tfmg:laminated_magnetic_alloy_block',
        E: 'mekanism:advanced_chemical_tank',
        F: 'tfmg:plastic_sheet',
        G: 'tfmg:coated_circuit_board',
        H: 'tfmg:p_semiconductor',
        I: 'tfmg:n_semiconductor',
        J: 'ae2:engineering_processor',
        K: 'mekanism:ultimate_control_circuit',
        L: 'tfmg:steel_frame',
        M: 'tfmg:transformer',
        N: 'tfmg:centrifuge'
      }).id('industrial_colonies:mekanism_nuclear/isotopic_centrifuge')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Raise a real oxygen-loading tower: fan and smart-pipe header feed a valved rotary condenser, paired gas tanks flank the electric pump, and a plastic-isolated etched board, capacitors, and advanced controller regulate the heavy base
    event.recipes.create.mechanical_crafting('ad_astra:oxygen_loader', ['  A  ', ' BCB ', 'D E D', 'FGHIF', 'DJKJD'], {
        A: 'ad_astra:fan',
        B: 'tfmg:steel_smart_fluid_pipe',
        C: 'tfmg:steel_fluid_valve',
        D: 'tfmg:heavy_plate',
        E: 'mekanism:rotary_condensentrator',
        F: 'ad_astra:gas_tank',
        G: 'tfmg:etched_circuit_board',
        H: 'tfmg:electric_pump',
        I: 'tfmg:plastic_sheet',
        J: 'tfmg:capacitor_item',
        K: 'mekanism:advanced_control_circuit'
      }).id('industrial_colonies:space/life_support/oxygen_loader')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Laminate iron boots with rubber soles, magnetic anchors, titanium reinforcement and copper grounding, then add a plastic-isolated coated board and transistor field switch on the Copper line
    event.recipes.create.sequenced_assembly(['rocketnautics:copper_anchor_boots'], 'minecraft:iron_boots', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:copper_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:iron_boots'}})).loops(1).id('industrial_colonies:space_hardware/copper_anchor_boots')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Pressure-fit paired Brass lugs around the small walking-beam pivot, then close its rebar pin and service screws in the Weathered-Iron Press
    event.recipes.industrial_colonies.weathered_iron_compacting(['tfmg:pumpjack_hammer_connector'], ['tfmg:pumpjack_hammer_part', 'create:brass_sheet', 'create:brass_sheet', 'tfmg:rebar', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:machine/oil_processing/pumpjack_hammer_connector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Fabricate the walking beam as a cast-iron truss over its pivot part, heavy wear cap, Weathered-Iron drive gearbox, through-shaft, and framed hanger; these are the few functional parts missing from the prior beam
    event.recipes.create.mechanical_crafting('tfmg:pumpjack_hammer', [' ABA ', 'ACDCA', 'CCECC', '  F  ', '  G  '], {
        A: 'tfmg:cast_iron_ingot',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:cast_iron_truss',
        D: 'tfmg:pumpjack_hammer_part',
        E: 'createcasing:weathered_iron_gearbox',
        F: 'create:shaft',
        G: 'tfmg:cast_iron_frame'
      }).id('industrial_colonies:machine/oil_processing/pumpjack_hammer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Pressure-laminate TFMG steel pipe and casing around inspection glass, rubber seals, a steel fluid valve, and infused joints in the Weathered Iron line
    event.recipes.industrial_colonies.weathered_iron_compacting(['8x mekanism:basic_pressurized_tube'], ['tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_casing', 'tfmg:steel_casing', Ingredient.of('#c:glass_blocks/cheap'), 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:steel_fluid_valve', 'mekanism:alloy_infused', 'mekanism:alloy_infused']).id('industrial_colonies:mekanism/transmission/basic_pressurized_tube')
  }
})

ServerEvents.recipes(event => {
  // [Steel & Petroleum] Build two serviceable foundry gauges with a compass face, steel yoke, sight glass, and copper pickup lead
  event.shaped('2x createmetallurgy:gauge_attachment', [' A ', 'BCB', ' D '], {
      A: 'minecraft:compass',
      B: '#c:ingots/steel',
      C: 'minecraft:glass_pane',
      D: 'tfmg:copper_wire'
    }).id('industrial_colonies:create_addons/foundry_gauge_attachment_batch')
})

ServerEvents.recipes(event => {
  // [Steel & Petroleum] Stretch layered wool media across a sturdy steel frame to make four replaceable ladle filters per fabrication run
  event.shaped('4x createmetallurgy:ladle_filter', ['ABA', ' B ', ' C '], {
      A: '#c:ingots/steel',
      B: '#minecraft:wool',
      C: 'create:sturdy_sheet'
    }).id('industrial_colonies:create_addons/ladle_filter_batch')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Lay out the colony banner, clipboard, resource ledger, build instrument, dual control boards, and a full wired modem as an actual colony operations console
    event.recipes.create.mechanical_crafting('colony4cc:colony_peripheral', ['ABC', 'DED', ' F '], {
        A: 'minecolonies:colony_banner',
        B: 'minecolonies:clipboard',
        C: 'minecolonies:resourcescroll',
        D: 'tfmg:circuit_board',
        E: 'computercraft:wired_modem_full',
        F: 'structurize:sceptergold'
      }).id('industrial_colonies:computer_network_coverage/colony_peripheral')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Lay out an open steam-distribution grate from heavy perimeter plate, iron vents, a crossed pipe manifold, and infused bracing.
    event.recipes.create.mechanical_crafting('mekanism:pressure_disperser', ['ABBA', 'CDDC', 'EEEE', 'ABBA'], {
        A: 'tfmg:heavy_plate',
        B: 'minecraft:iron_bars',
        C: 'tfmg:steel_pipe',
        D: 'tfmg:steel_fluid_valve',
        E: 'mekanism:alloy_infused'
      }).id('industrial_colonies:mekanism/boiler/pressure_disperser')
  }
})

ServerEvents.recipes(event => {
  // [Mechanical Foundations] Stamp four service springs from an iron-strip blank with four opposed nugget coils
  event.shaped('4x simulated:spring', [' A ', 'ABA', ' A '], {
      A: 'minecraft:iron_nugget',
      B: 'create:iron_sheet'
    }).id('industrial_colonies:simulated/spring_batch')
})

ServerEvents.recipes(event => {
  // [Steel & Petroleum] Form two foundry taps as cast-iron elbows around a pressure-rated pipe and a replaceable fluid valve
  event.shaped('2x createmetallurgy:faucet', ['AA ', ' BC', ' A '], {
      A: 'tfmg:cast_iron_sheet',
      B: 'tfmg:cast_iron_pipe',
      C: 'create:fluid_valve'
    }).id('industrial_colonies:create_addons/foundry_faucet_batch')
})

ServerEvents.recipes(event => {
  // [Steel & Petroleum] Link an iron control handle to an analog transmission through a Brass quadrant and spring-return detent
  event.shaped('simulated:throttle_lever', [' A ', 'BCB', ' D '], {
      A: 'simulated:iron_handle',
      B: 'simulated:spring',
      C: 'simulated:analog_transmission',
      D: 'create:brass_casing'
    }).id('industrial_colonies:simulated/throttle_lever')
})

ServerEvents.recipes(event => {
  // [Electrical Manufacturing] Build the unique EE grid inductor around the canonical TFMG copper winding while retaining EE's network terminals
  event.shaped('electroenergetics:inductor', [' A ', 'BCB', ' A '], {
      A: '#c:plates/iron',
      B: 'electroenergetics:connector',
      C: 'tfmg:copper_spool'
    }).id('industrial_colonies:tfmg_canonical/grid_inductor')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Fit a Depot with a piston-driven print carriage, ink feed, dedicated control board, display driver, wiring, and a washable plastic-lined Brass shell.
    event.recipes.create.sequenced_assembly(['computercraft:printer'], 'create:depot', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:mechanical_piston']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:ink_sac']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:display_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:brass_casing']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:depot'}})).loops(1).id('industrial_colonies:computercraft/io/printer')
  }
})

ServerEvents.recipes(event => {
  // [Digital Logistics] Forge four rope-end eyes from heavy plates, metal brackets, and replaceable lead loops
  event.shaped('4x simulated:rope_connector', [' A ', 'BCB', ' A '], {
      A: 'minecraft:lead',
      B: 'create:metal_bracket',
      C: 'tfmg:heavy_plate'
    }).id('industrial_colonies:simulated/rope_connector_batch')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Fabricate four transformer radiator faces as aluminum fins and oil channels braced around a steel truss with copper heat spreaders
    event.recipes.create.mechanical_crafting('4x electroenergetics:radiator_panel', ['ABA', 'CDC', 'ABA'], {
        A: 'tfmg:aluminum_sheet',
        B: 'tfmg:aluminum_pipe',
        C: 'create:copper_sheet',
        D: 'tfmg:steel_truss'
      }).id('industrial_colonies:electroenergetics/radiator_panel_batch')
  }
})

ServerEvents.recipes(event => {
  // [Digital Logistics] Fold a hollow aluminum canister around a real fluid valve with a rubber-sealed bottom instead of hiding a wooden barrel inside it
  event.shaped('createdieselgenerators:canister', ['ABA', 'A A', 'ACA'], {
      A: 'tfmg:aluminum_sheet',
      B: 'tfmg:aluminum_fluid_valve',
      C: 'tfmg:rubber_sheet'
    }).id('industrial_colonies:diesel_generators_coverage/canister')
})

ServerEvents.recipes(event => {
  // [Digital Logistics] Clad a wooden barrel as a sealed mobile oil drum with heavy steel cheeks, rubber gaskets, and a pressure-service TFMG valve
  event.shaped('createdieselgenerators:oil_barrel', [' A ', 'BCB', 'ADA'], {
      A: 'tfmg:heavy_plate',
      B: 'tfmg:rubber_sheet',
      C: 'minecraft:barrel',
      D: 'tfmg:steel_fluid_valve'
    }).id('industrial_colonies:power_addon_gaps/oil_barrel')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Pressure-forge one large walking-beam pivot from a full cast-iron charge around paired heavy bearing cheeks, a steel load block, and twin rebar pins on the Weathered-Iron line
    event.recipes.industrial_colonies.weathered_iron_compacting(['tfmg:large_pumpjack_hammer_part'], ['tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_block', 'tfmg:rebar', 'tfmg:rebar', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Pressure-forge a matched pair of small walking-beam pivots from cast iron around a steel load spine, heavy bearing cheeks, rebar pins, and service screws on the Weathered-Iron line
    event.recipes.industrial_colonies.weathered_iron_compacting(['2x tfmg:pumpjack_hammer_part'], ['tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:steel_ingot', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:rebar', 'tfmg:rebar', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:machine/oil_processing/pumpjack_hammer_part')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Roll copper heat faces, heavy plate, pipe, and refractory lining into an economical eight-block evaporation tower batch.
    event.recipes.industrial_colonies.industrial_iron_compacting(['8x mekanism:thermal_evaporation_block'], ['tfmg:steel_casing', 'tfmg:steel_casing', 'tfmg:steel_casing', 'tfmg:steel_casing', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'create:copper_sheet', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks']).id('industrial_colonies:mekanism/thermal_evaporation/block_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Bond four framed observation panels with rubber and plastic seals plus infused-alloy corner locks for pressure-rated multiblocks.
    event.recipes.industrial_colonies.industrial_iron_compacting(['4x mekanism:structural_glass'], ['minecraft:glass', 'minecraft:glass', 'minecraft:glass', 'minecraft:glass', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet', 'mekanism:alloy_infused', 'mekanism:alloy_infused']).id('industrial_colonies:mekanism_components/structural_glass_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Interstellar Escape] Turn a laser amplifier into an item-capture beamline with a magnetic field yoke and coil, teleport focus, buffered chest, routed transporter, and ultimate beam-control logic
    event.recipes.create.sequenced_assembly(['mekanism:laser_tractor_beam'], 'mekanism:laser_amplifier', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electromagnetic_coil']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:teleportation_core']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:personal_chest']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_logistical_transporter']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_frame']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:laser_amplifier'}})).loops(1).id('industrial_colonies:mekanism/laser/tractor_beam')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Build a load-bearing U-frame beneath a transformer and advanced computer: plastic standoffs and a capacitor isolate the etched controller, while engine pipes, hose anchor, nozzle, steel mechanism, and ultimate interlock occupy their physical service bays
    event.recipes.create.mechanical_crafting('rocketnautics:thruster_mount', [' ABC ', 'DEFED', 'G H G', 'D I D', 'DJKLD'], {
        A: 'tfmg:transformer',
        B: 'computercraft:computer_advanced',
        C: 'tfmg:etched_circuit_board',
        D: 'tfmg:steel_frame',
        E: 'tfmg:plastic_sheet',
        F: 'tfmg:capacitor_item',
        G: 'tfmg:heavy_plate',
        H: 'rocketnautics:engine_pipes',
        I: 'rocketnautics:engine_nozzle',
        J: 'mekanism:ultimate_control_circuit',
        K: 'rocketnautics:hose_anchor',
        L: 'tfmg:steel_mechanism'
      }).id('industrial_colonies:space/propulsion/thruster_mount')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Populate an etched TFMG board with a long-range modem, signal processor, capacitor, antenna lead, and titanium enclosure
    event.recipes.create.sequenced_assembly(['ad_astra:radio'], 'tfmg:etched_circuit_board', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'computercraft:wireless_modem_advanced']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_wire']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:etched_circuit_board'}})).loops(1).id('industrial_colonies:space_coverage/radio')
  }
})

ServerEvents.recipes(event => {
  // [Steel & Petroleum] Batch eight TFMG cable tubes from canonical rubber, steel fasteners, and copper conductors
  event.shaped('8x tfmg:cable_tube', [' A ', 'BCB', ' A '], {
      A: '#c:nuggets/steel',
      B: '#c:wires/copper',
      C: 'tfmg:rubber_sheet'
    }).id('industrial_colonies:chemical_processing/cable_tube')
})

ServerEvents.recipes(event => {
  // [Electrical Manufacturing] Port the unique CreateAddition redstone relay to the canonical TFMG local connector
  event.shaped('createaddition:redstone_relay', [' A ', 'BCB', 'DDD'], {
      A: '#c:dusts/redstone',
      B: 'tfmg:cable_connector',
      C: 'create:precision_mechanism',
      D: '#c:stones'
    }).id('industrial_colonies:early_power_cables/redstone_relay')
})

ServerEvents.recipes(event => {
  // [Electrical Manufacturing] Cycle-breaking Voltmeter made before the Polarizer can produce magnets
  event.shaped('tfmg:voltmeter', ['ABA', 'CDC', 'EFE'], {
      A: 'create:copper_sheet',
      B: 'minecraft:glass_pane',
      C: 'minecraft:redstone',
      D: 'minecraft:compass',
      E: '#c:ingots/zinc',
      F: 'tfmg:copper_wire'
    }).id('industrial_colonies:electronics/voltmeter')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Construct the first chemical vessel as a lead-lined cast-iron shell with a tank core and opposed process connections
    event.recipes.create.mechanical_crafting('tfmg:cast_iron_chemical_vat', ['ABA', 'CDC', 'ABA'], {
        A: '#c:plates/cast_iron',
        B: '#c:plates/lead',
        C: 'tfmg:cast_iron_pipe',
        D: 'tfmg:cast_iron_fluid_tank'
      }).id('industrial_colonies:fluid_infrastructure/cast_iron_chemical_vat')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Press a refractory lining and TFMG steel drive into a Create basin to withstand continuous melting.
    event.recipes.industrial_colonies.weathered_iron_compacting(['createmetallurgy:foundry_basin'], ['create:basin', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:cast_iron_frame', 'tfmg:steel_mechanism', 'createmetallurgy:refractory_mortar']).id('industrial_colonies:foundry_routes/create_metallurgy_foundry_basin')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Laminate a sealed heavy lid around a TFMG steel mechanism and fireproof refractory shell.
    event.recipes.industrial_colonies.weathered_iron_compacting(['createmetallurgy:foundry_lid'], ['tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:fireproof_bricks', 'tfmg:fireproof_bricks', 'tfmg:heavy_plate', 'tfmg:steel_mechanism', 'tfmg:screw']).id('industrial_colonies:foundry_routes/create_metallurgy_foundry_lid')
  }
})

ServerEvents.recipes(event => {
  // [Electrical Manufacturing] Upgrade TFMG local endpoint hardware into paired long-span Electro Energetics grid connectors
  event.shaped('2x electroenergetics:connector', [' A ', 'BCB', ' D '], {
      A: 'tfmg:copper_cable_hub',
      B: 'tfmg:cable_connector',
      C: 'create:brass_casing',
      D: 'tfmg:cast_iron_sheet'
    }).id('industrial_colonies:grid/connector')
})

ServerEvents.recipes(event => {
  // [Electrical Manufacturing] Wind canonical copper wire onto the staged Electro Energetics grid spool
  event.shaped('electroenergetics:copper_wire_spool', ['AAA', 'ABA', 'AAA'], {
      A: '#c:wires/copper',
      B: 'electroenergetics:empty_spool'
    }).id('industrial_colonies:grid/copper_wire_spool')
})

ServerEvents.recipes(event => {
  // [Steel & Petroleum] Form the field sampling can from brass body panels and a cast-iron neck
  event.shaped('tfmg:oil_can', [' AA', 'BBB', ' BB'], {
      A: 'tfmg:cast_iron_nugget',
      B: 'create:brass_ingot'
    }).id('industrial_colonies:machine/oil_processing/oil_can')
})

ServerEvents.recipes(event => {
  // [Steel & Petroleum] Make the field oil hammer from cast iron, a brass striking face, and a replaceable wooden handle
  event.shaped('tfmg:oil_hammer', ['AAB', ' C ', ' C '], {
      A: 'tfmg:cast_iron_ingot',
      B: 'create:brass_ingot',
      C: '#c:rods/wooden'
    }).id('industrial_colonies:machine/oil_processing/oil_hammer')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Press eight induction-frame segments from TFMG steel frames and heavy shell plate, magnetic laminations, insulated high-current wire, and a shared heavy-machinery spine.
    event.recipes.industrial_colonies.industrial_iron_compacting(['8x mekanism:induction_casing'], ['tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:magnetic_alloy_sheet', 'tfmg:magnetic_alloy_sheet', 'tfmg:magnetic_alloy_sheet', 'tfmg:magnetic_alloy_sheet', 'electroenergetics:heavily_insulated_wire', 'electroenergetics:heavily_insulated_wire', 'electroenergetics:heavily_insulated_wire', 'electroenergetics:heavily_insulated_wire', 'tfmg:heavy_machinery_casing', 'tfmg:heavy_machinery_casing']).id('industrial_colonies:mekanism/induction/casing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Build the tuyere hatch as a refractory wall with a centered tank, paired air pipes, and a cast-iron service face
    event.recipes.create.mechanical_crafting('tfmg:blast_furnace_hatch', ['ABA', 'CDC', 'ABA'], {
        A: 'tfmg:fireproof_bricks',
        B: '#c:plates/cast_iron',
        C: 'tfmg:cast_iron_pipe',
        D: 'tfmg:cast_iron_fluid_tank'
      }).id('industrial_colonies:steelworks/blast_furnace_hatch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Pressure-forge the pumpjack wear component on the Weathered-Iron line
    event.recipes.industrial_colonies.weathered_iron_compacting(['tfmg:large_pumpjack_hammer_head'], ['tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_mechanism', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Build the compact 4-by-5 oilfield base around twin cast-iron pumps, one service tank, paired pipe rails, a Brass control housing, a single precision drive, a Weathered-Iron gearbox, framed bed, and rebar feet
    event.recipes.create.mechanical_crafting('tfmg:pumpjack_base', ['A  A', 'BCDB', 'BEFB', 'BGGB', 'GHHG'], {
        A: 'tfmg:cast_iron_mechanical_pump',
        B: 'tfmg:cast_iron_pipe',
        C: 'tfmg:cast_iron_fluid_tank',
        D: 'create:brass_casing',
        E: 'create:precision_mechanism',
        F: 'createcasing:weathered_iron_gearbox',
        G: 'tfmg:cast_iron_frame',
        H: 'tfmg:rebar'
      }).id('industrial_colonies:machine/oil_processing/pumpjack_base')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('simulated:altitude_sensor', [' AB ', ' CD ', 'EFGH'], {
        A: 'minecraft:glass_bottle',
        B: 'minecraft:paper',
        C: 'minecraft:compass',
        D: 'create:copper_casing',
        E: 'create:redstone_link',
        F: 'tfmg:copper_wire',
        G: 'create:electron_tube',
        H: 'create:precision_mechanism'
      }).id('industrial_colonies:simulated/altitude_sensor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Review correction: cheaper Mechanical Crafting conversion unit. One motor supplies the electromechanical conversion; the duplicated standalone rotor and magnetic plate are removed.
    event.recipes.create.mechanical_crafting('electroenergetics:converter', [' A ', 'BCB', ' D '], {
        A: 'tfmg:capacitor_item',
        B: 'electroenergetics:connector',
        C: 'tfmg:industrial_aluminum_casing',
        D: 'tfmg:electric_motor'
      }).id('industrial_colonies:create_addons/electro_converter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('2x electroenergetics:fuse_holder', ['AAAA', 'BCCB', 'DEFD'], {
        A: 'electroenergetics:connector',
        B: 'tfmg:fireproof_bricks',
        C: 'tfmg:copper_wire',
        D: 'tfmg:plastic_sheet',
        E: 'electroenergetics:electrical_panel',
        F: 'electroenergetics:insulator'
      }).id('industrial_colonies:create_addons/fuse_holder_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('electroenergetics:cut_off_switch', [' A ', 'BCB', 'DEF'], {
        A: 'minecraft:lever',
        B: 'electroenergetics:connector',
        C: 'electroenergetics:fuse_holder',
        D: 'tfmg:copper_wire',
        E: 'electroenergetics:electrical_panel',
        F: 'tfmg:plastic_sheet'
      }).id('industrial_colonies:create_addons/cut_off_switch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('electroenergetics:redstone_relay', [' A  ', 'BCDE', ' D  '], {
        A: 'minecraft:redstone_torch',
        B: 'tfmg:transistor_item',
        C: 'electroenergetics:relay',
        D: 'tfmg:circuit_board',
        E: 'tfmg:copper_wire'
      }).id('industrial_colonies:create_addons/redstone_relay')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('ae2:molecular_assembler', ['AB BA', ' CDE ', ' FGH ', 'AIJIA'], {
        A: 'tfmg:plastic_sheet',
        B: 'ae2:quartz_glass',
        C: 'ae2:annihilation_core',
        D: 'minecraft:crafting_table',
        E: 'ae2:formation_core',
        F: 'tfmg:n_semiconductor',
        G: 'create:precision_mechanism',
        H: 'tfmg:p_semiconductor',
        I: 'tfmg:circuit_board',
        J: 'ae2:calculation_processor'
      }).id('industrial_colonies:digital_core/molecular_assembler')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('simulated:directional_linked_receiver', [' A ', 'BCD', ' E '], {
        A: 'create:transmitter',
        B: 'minecraft:compass',
        C: 'create:brass_casing',
        D: 'create_connected:control_chip',
        E: 'create:iron_sheet'
      }).id('industrial_colonies:simulated/directional_linked_receiver')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('simulated:modulating_linked_receiver', [' A ', 'BCD', ' E '], {
        A: 'create:transmitter',
        B: 'simulated:redstone_accumulator',
        C: 'create:brass_casing',
        D: 'create_connected:control_chip',
        E: 'create:golden_sheet'
      }).id('industrial_colonies:simulated/modulating_linked_receiver')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Review correction: a cheaper lithium electrode stack, separated by plastic and supported by a steel casing. No processor bank is needed for this battery.
    event.recipes.create.mechanical_crafting('electroenergetics:accumulator', ['ABA', 'BCB', 'DED'], {
        A: 'create:copper_sheet',
        B: 'tfmg:lithium_charge',
        C: 'tfmg:plastic_sheet',
        D: 'tfmg:copper_wire',
        E: 'tfmg:steel_casing'
      }).id('industrial_colonies:grid/accumulator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Pre-semiconductor ownership] Mechanical components precede final factory assembly.
    event.recipes.create.mechanical_crafting('tfmg:steel_fluid_valve', [' A ', 'BCB', ' D '], {
        A: 'create:copper_valve_handle',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:steel_pipe',
        D: 'tfmg:steel_cogwheel'
      }).id('industrial_colonies:tfmg_coverage/steel_fluid_valve')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Thick paired cylinder banks around fuel injection and crankshaft, pressure manifold overhead; controlled diesel compression engine. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createdieselgenerators:diesel_engine', [' AAA ', 'BCBCB', 'BDEDB', 'FGEGF', 'HIIIH'], {
        A: 'tfmg:steel_pipe',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:diesel_engine_cylinder',
        D: 'tfmg:electric_pump',
        E: 'tfmg:crankshaft',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:engines/diesel_engine')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Two opposing impellers share a driven shaft with separate inlet/outlet piping and bearings; steel thermal shell. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createdieselgenerators:engine_turbocharger', [' A A ', 'BCDCB', 'EFGFE', 'HIIIH'], {
        A: 'tfmg:steel_pipe',
        B: 'tfmg:heavy_plate',
        C: 'create:propeller',
        D: 'create:shaft',
        E: 'tfmg:rubber_sheet',
        F: 'create:cogwheel',
        G: 'tfmg:electric_motor',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:engines/engine_turbocharger')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Central lever bridges electrum contacts; refractory arc separators isolate the high-current poles above steel supports. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('electroenergetics:high_voltage_switch', ['  A  ', 'BCDCB', 'EFEFE', 'GHHHG'], {
        A: 'minecraft:lever',
        B: 'tfmg:copper_wire',
        C: 'createaddition:electrum_wire',
        D: 'tfmg:magnetic_alloy_sheet',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:fireproof_bricks',
        G: 'immersiveengineering:plate_steel',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:extreme_grid/high_voltage_switch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Two separate winding columns share a magnetic core; insulated terminals on top and low monitoring electronics. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('electroenergetics:transformer', [' AAA ', 'BCDCB', 'BCDCB', 'EFFFE', 'GHHHG'], {
        A: 'minecraft:glass',
        B: 'tfmg:copper_wire',
        C: 'tfmg:electromagnetic_coil',
        D: 'tfmg:magnetic_alloy_sheet',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'immersiveengineering:plate_steel',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:high_voltage/transformer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Reuse the preceding battery cube with paired refined conductors, elite control and high-current bus; previous investment stays useful. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:elite_energy_cube', [' AAA ', 'BCDCB', 'AEFEA', 'GHHHG'], {
        A: 'createaddition:electrum_wire',
        B: 'tfmg:rubber_sheet',
        C: 'mekanism:advanced_energy_cube',
        D: 'mekanism:alloy_reinforced',
        E: 'tfmg:circuit_board',
        F: 'mekanism:elite_control_circuit',
        G: 'tfmg:nickel_sheet',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism/storage/elite_energy_cube')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Reuse the preceding battery cube with paired refined conductors, ultimate control and high-current bus; previous investment stays useful. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:ultimate_energy_cube', [' AAA ', 'BCDCB', 'AEFEA', 'GHHHG'], {
        A: 'createaddition:electrum_wire',
        B: 'tfmg:rubber_sheet',
        C: 'mekanism:elite_energy_cube',
        D: 'mekanism:alloy_atomic',
        E: 'tfmg:circuit_board',
        F: 'mekanism:ultimate_control_circuit',
        G: 'tfmg:nickel_sheet',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism/storage/ultimate_energy_cube')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED.
    // 
    // [Digital Logistics] Construct the fermenter as a sealed barrel and basin over a pumped cast-iron reservoir inside a pressure-rated frame
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('createdieselgenerators:bulk_fermenter', [' A ', 'BCB', 'DED', ' F '], {
        A: 'createdieselgenerators:basin_lid',
        B: 'tfmg:steel_pipe',
        C: 'minecraft:barrel',
        D: 'tfmg:heavy_plate',
        E: 'tfmg:cast_iron_fluid_tank',
        F: 'tfmg:steel_mechanical_pump'
      }).id('industrial_colonies:diesel_generators_coverage/bulk_fermenter')
  }
})

ServerEvents.recipes(event => {
  // Review revision: A real plastic pipe and two metering valves gain logic plus a board and rubber seal; chemicals retain plastic wetted surfaces. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('4x tfmg:plastic_smart_fluid_pipe', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:plastic_pipe',
      B: 'tfmg:plastic_fluid_valve',
      C: 'ae2:logic_processor',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:tfmg_coverage/plastic_smart_fluid_pipe')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mechanical cylinder block and crank bed without a digital-control requirement; simpler engine remains an accessible stepping stone. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:simple_large_engine', [' AAA ', 'BC CB', 'DDEDD', 'FGGGF'], {
        A: 'tfmg:steel_pipe',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:engine_cylinder',
        D: 'create:shaft',
        E: 'tfmg:crankshaft',
        F: 'tfmg:nickel_sheet',
        G: 'tfmg:steel_frame'
      }).id('industrial_colonies:tfmg_remaining/simple_large_engine')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Power-efficiency module from charge smoothing, rectification and insulated leads; no complete machine consumed. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['mekanism:upgrade_energy'], 'mekanism:alloy_infused', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_diode']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:alloy_infused'}})).loops(1).id('industrial_colonies:mekanism/upgrade/energy')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Calibrated clock/switching module with variable timing control; can precede expensive digital processors. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['mekanism:upgrade_speed'], 'mekanism:alloy_infused', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:potentiometer']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:constantan_wire']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:alloy_infused'}})).loops(1).id('industrial_colonies:mekanism/upgrade/speed')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Standard reinforced mount with small control board and buffered power; reusable base for the module family. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['mekanism:module_base'], 'immersiveengineering:plate_steel', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'immersiveengineering:plate_steel'}})).loops(1).id('industrial_colonies:mekanism_components/module_base')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Direct small item cell assembly with independent memory and sealing. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:item_storage_cell_1k'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_glass']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:v3_ae2/item_storage_cell_1k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Cutting arbor and powered spindle above a guarded electronics cabinet; precision feed control and structural base match the saw job. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:brass_mechanical_saw', [' ABA ', 'ABCBA', ' DED ', 'FGFGF', 'EHIHE'], {
        A: 'tfmg:nickel_sheet',
        B: 'create:shaft',
        C: 'create:mechanical_saw',
        D: 'tfmg:electric_motor',
        E: 'tfmg:steel_frame',
        F: 'tfmg:circuit_board',
        G: 'ae2:calculation_processor',
        H: 'tfmg:rubber_sheet',
        I: 'ae2:engineering_processor'
      }).id('industrial_colonies:manufacturing/brass/saw')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Spark plugs and carburetor above gasoline cylinders, crank beneath, compact buffered ignition board. No diesel injector copied into a petrol engine. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:regular_engine', [' ABA ', 'CDEDC', 'BFGFB', 'HIJIH', 'KLLLK'], {
        A: 'tfmg:spark_plug',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:heavy_plate',
        D: 'tfmg:engine_cylinder',
        E: 'create:fluid_valve',
        F: 'create:shaft',
        G: 'tfmg:crankshaft',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:circuit_board',
        J: 'tfmg:capacitor_item',
        K: 'tfmg:nickel_sheet',
        L: 'tfmg:steel_frame'
      }).id('industrial_colonies:engines/regular_engine')
  }
})

ServerEvents.recipes(event => {
  // Deferred re-review: Fluid port on the thermal evaporation tower. Installed text: A valve that can be placed on a Thermal Evaporation Plant multiblock, allowing for fluids to be inserted and extracted via external piping.
  // 
  // Review revision: Tower wall with sealed fluid connections and local regulation; reuse the actual evaporation shell, not another controller. Existing pack items; proposed editor recipe, no gameplay export.
  // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
  event.shaped('mekanism:thermal_evaporation_valve', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:steel_pipe',
      B: 'tfmg:steel_fluid_valve',
      C: 'mekanism:thermal_evaporation_block',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:mekanism/thermal_evaporation/valve')
})

ServerEvents.recipes(event => {
  // Deferred re-review: Fluid port on a Dynamic Tank multiblock. Installed text: A valve that can be placed on a Dynamic Tank multiblock, allowing for fluids and chemicals to be inserted and extracted via external piping.
  // 
  // Review revision: Tank-shell service port with paired valves, seals and simple fluid monitoring; not an extra high-capacity tank in item form. Existing pack items; proposed editor recipe, no gameplay export.
  // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
  event.shaped('mekanism:dynamic_valve', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:steel_pipe',
      B: 'tfmg:steel_fluid_valve',
      C: 'mekanism:dynamic_tank',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:mekanism_components/dynamic_valve_batch')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Existing Advanced Peripherals memory component; preserve native item data semantics, not a substitute AE storage cell.
    // 
    // [High-Energy Grid] Laminate an AE 1k memory die, a TFMG coated controller board, gold contacts, copper data traces, and a magnetic stripe into a plastic card
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['advancedperipherals:memory_card'], 'tfmg:plastic_sheet', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:golden_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:plastic_sheet'}})).loops(1).id('industrial_colonies:computer_network_coverage/memory_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Cold-stabilized quantum addressing on a real memory bank; consumed dragon coolant, superconducting interconnect and iridium package. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['advanced_ae:quantum_storage_component'], 'ae2:cell_component_256k', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'iceandfire:ice_dragon_blood']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_bscco']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:iridium_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:cell_component_256k'}})).loops(1).id('industrial_colonies:v3_ae2/quantum_storage_component')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Metered switchboard with visible switches, separated conductor bus and service electronics. Steel lower cabinet instead of arbitrary peripheral tax. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('electroenergetics:electrical_panel', ['AAAAA', 'BCBDB', 'EFGFE', 'HIIIH', 'JKKKJ'], {
        A: 'minecraft:glass',
        B: 'minecraft:lever',
        C: 'electroenergetics:ammeter',
        D: 'tfmg:voltmeter',
        E: 'tfmg:copper_wire',
        F: 'createaddition:electrum_wire',
        G: 'ae2:calculation_processor',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:circuit_board',
        J: 'immersiveengineering:plate_steel',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:create_addons/electrical_panel_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED.
    // 
    // [High-Energy Grid] Build the first matrix battery as a steel-framed lithium stack: three Energy Tablet bus bars feed an infused-alloy casing around the induction core, Basic Cube, magnetic backplate, and Basic control circuit.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('mekanism:basic_induction_cell', [' ABA ', 'CDDDC', 'AEFEA', ' CGC ', ' AHA '], {
        A: 'tfmg:steel_frame',
        B: 'mekanism:basic_control_circuit',
        C: 'tfmg:lithium_charge',
        D: 'mekanism:energy_tablet',
        E: 'mekanism:alloy_infused',
        F: 'mekanism:induction_casing',
        G: 'mekanism:basic_energy_cube',
        H: 'tfmg:magnetic_alloy_sheet'
      }).id('industrial_colonies:mekanism/induction/basic_cell')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED.
    // 
    // [High-Energy Grid] Complete the Elite Provider as an Ultimate protected substation: a five-wire high-current spine crosses HV capacitance, atomic buswork, SF6 interruption, the Ultimate Cube, and a large stabilizing coil.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('mekanism:ultimate_induction_provider', [' ABA ', ' CCC ', 'DEFEG', ' CHC ', ' AIA '], {
        A: 'tfmg:steel_frame',
        B: 'mekanism:ultimate_control_circuit',
        C: 'electroenergetics:heavily_insulated_wire',
        D: 'electroenergetics:high_voltage_capacitor',
        E: 'mekanism:alloy_atomic',
        F: 'mekanism:elite_induction_provider',
        G: 'electroenergetics:sulfur_hexafluoride_breaker',
        H: 'mekanism:ultimate_energy_cube',
        I: 'tfmg:large_coil'
      }).id('industrial_colonies:mekanism/induction/ultimate_provider')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Glass and driven pixel elements form the entire upper display; lower row carries control/data board, not machine drive motors. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('computercraft:monitor_normal', ['AAAA', 'ABBA', 'CDEC', 'FGGF'], {
        A: 'minecraft:glass',
        B: 'create:electron_tube',
        C: 'tfmg:copper_wire',
        D: 'tfmg:circuit_board',
        E: 'ae2:logic_processor',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:steel_frame'
      }).id('industrial_colonies:computercraft/monitor/normal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Readable screen above one completed board/logic CPU and buffered power; ordinary computer stays before quantum technology. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('computercraft:computer_normal', ['AAAA', 'ABBA', 'CDEC', 'FGGF', 'HIIH'], {
        A: 'minecraft:glass',
        B: 'create:electron_tube',
        C: 'tfmg:copper_wire',
        D: 'tfmg:circuit_board',
        E: 'ae2:logic_processor',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:capacitor_item',
        H: 'immersiveengineering:plate_iron',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:computercraft/computer/normal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Two drive mechanisms form the media slot over controller logic and data leads; a mechanical storage peripheral, not another complete computer. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('computercraft:disk_drive', [' AA ', 'BCCB', 'DEFD', 'GHHG'], {
        A: 'minecraft:glass',
        B: 'immersiveengineering:plate_iron',
        C: 'create:precision_mechanism',
        D: 'tfmg:copper_wire',
        E: 'tfmg:circuit_board',
        F: 'ae2:logic_processor',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:computercraft/io/disk_drive')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Aluminum pipe with matched valves and a logic flow-control board; small sensor hardware produced in a practical batch. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('4x tfmg:aluminum_smart_fluid_pipe', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:aluminum_pipe',
      B: 'tfmg:aluminum_fluid_valve',
      C: 'ae2:logic_processor',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:tfmg_coverage/aluminum_smart_fluid_pipe')
})

ServerEvents.recipes(event => {
  // Review revision: Steel pressure pipe receives its own valve pair and addressed metering board; avoids requiring a full pump for each short pipe. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('4x tfmg:steel_smart_fluid_pipe', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:steel_pipe',
      B: 'tfmg:steel_fluid_valve',
      C: 'ae2:logic_processor',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:tfmg_coverage/steel_smart_fluid_pipe')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Adjustable transformer hardware; part of voltage control, not another digital power-storage block.
    // 
    // Review revision: Adjustable tapped winding around a magnetic core, with insulated output terminals and an actual tuning potentiometer; compact variable transformer. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('electroenergetics:variac', [' A A ', 'BCDCB', 'EFGFE', 'HDDDH'], {
        A: 'createaddition:electrum_wire',
        B: 'tfmg:copper_wire',
        C: 'tfmg:electromagnetic_coil',
        D: 'tfmg:magnetic_alloy_sheet',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'tfmg:potentiometer',
        H: 'tfmg:nickel_sheet'
      }).id('industrial_colonies:electroenergetics/variac')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Manipulator and two drive wheels above a computer/cargo chassis, with logic and shielded wiring; automation has a tangible mobile platform cost. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('computercraft:turtle_normal', [' ABA ', 'CDDDC', 'EFGFE', 'AHIHA', 'JKKKJ'], {
        A: 'immersiveengineering:plate_iron',
        B: 'create:brass_hand',
        C: 'tfmg:electric_motor',
        D: 'create:shaft',
        E: 'tfmg:copper_wire',
        F: 'tfmg:circuit_board',
        G: 'ae2:logic_processor',
        H: 'computercraft:computer_normal',
        I: 'minecraft:chest',
        J: 'tfmg:nickel_sheet',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:computercraft/mobile/turtle')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Factory/logistics coordination block; user reviews the retained automation role, no recipe implies new AI behavior. Installed text: Centralized Factory Gauge management with a virtual board and advanced logistics control. / When powered by redstone
    // 
    // Review revision: Production display and factory gauge above stock-link coordination, calculation/programming and buffered control cabinet. Factory scheduling uses real logistics components, not loose arbitrary ingots. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('createfactorycontroller:factory_controller', ['AAAAA', 'ABCBA', 'DEFED', 'GHHBG', 'IJJJI'], {
        A: 'minecraft:glass',
        B: 'create:stock_link',
        C: 'create:factory_gauge',
        D: 'tfmg:rubber_sheet',
        E: 'tfmg:circuit_board',
        F: 'ae2:calculation_processor',
        G: 'createaddition:electrum_wire',
        H: 'tfmg:capacitor_item',
        I: 'tfmg:nickel_sheet',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:create_addons/factory_controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Program/control board cluster on a computing chassis; job workspace only, not digital cargo storage. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:crafting_unit', ['ABBA', 'CDEC', 'FGGF', 'AHHA'], {
        A: 'tfmg:nickel_sheet',
        B: 'tfmg:circuit_board',
        C: 'createaddition:electrum_wire',
        D: 'ae2:calculation_processor',
        E: 'ae2:logic_processor',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:capacitor_item',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/crafting_unit')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Larger active display panel with engineering touch/interface control and power buffering; distinct upgraded screen construction. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('computercraft:monitor_advanced', ['AAAAA', 'ABBBA', 'CDEDC', 'FGGGF', 'HIIIH'], {
        A: 'minecraft:glass',
        B: 'tfmg:segmented_display',
        C: 'createaddition:electrum_wire',
        D: 'tfmg:circuit_board',
        E: 'ae2:engineering_processor',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:capacitor_item',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:computercraft/monitor/advanced')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Inspection window and controlled inlet/outlet valves above heat/process monitoring panel; manages a separate evaporation tower rather than containing that whole tower. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:thermal_evaporation_controller', [' ABA ', 'CDEDC', 'FGHGF', 'CIIIC'], {
        A: 'tfmg:steel_pipe',
        B: 'minecraft:glass',
        C: 'tfmg:nickel_sheet',
        D: 'tfmg:steel_fluid_valve',
        E: 'mekanism:basic_chemical_tank',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'ae2:engineering_processor',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism/thermal_evaporation/controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Single-resource physical bulk storage, not a general AE digital warehouse.
    // 
    // [Mekanized Industry] Build a vertical industrial bin around an Item Vault, framed sides, controlled transporter feed, Brass Funnel inlet, and Chute outlet.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('mekanism:basic_bin', [' A ', 'BCB', 'DED', ' F '], {
        A: 'create:brass_funnel',
        B: 'tfmg:steel_frame',
        C: 'mekanism:basic_control_circuit',
        D: 'mekanism:basic_logistical_transporter',
        E: 'create:item_vault',
        F: 'create:chute'
      }).id('industrial_colonies:mekanism_utility/basic_bin')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Reports player presence/location to programs; security/automation peripheral.
    // 
    // Review revision: Radio and paired observation front end feed player-detection logic; compact peripheral base, no whole quantum computer required for local monitoring. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('advancedperipherals:player_detector', ['  A  ', 'BCBCB', 'DEFED', 'GHIHG'], {
        A: 'computercraft:wireless_modem_normal',
        B: 'minecraft:glass',
        C: 'minecraft:observer',
        D: 'tfmg:rubber_sheet',
        E: 'tfmg:circuit_board',
        F: 'ae2:logic_processor',
        G: 'tfmg:nickel_sheet',
        H: 'advancedperipherals:peripheral_casing',
        I: 'ae2:calculation_processor'
      }).id('industrial_colonies:computer_network_coverage/player_detector')
  }
})

ServerEvents.recipes(event => {
  // Deferred re-review: Pressure shell of the thermoelectric boiler, not the heat source itself. Installed text: A pressure-resistant, dense casing used in the creation of a Thermoelectric Boiler multiblock.
  // 
  // Review revision: Repeatable boiler pressure shell with nickel heat-transfer strips; eight casing blocks per batch, without a processor in every wall. Existing pack items; proposed editor recipe, no gameplay export.
  // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
  event.shaped('8x mekanism:boiler_casing', ['ABA', 'BAB', 'ABA'], {
      A: 'immersiveengineering:plate_steel',
      B: 'tfmg:nickel_sheet'
    }).id('industrial_colonies:mekanism/boiler/casing_batch')
})

ServerEvents.recipes(event => {
  // Deferred re-review: Boiler fluid connection for the existing multiblock. Installed text: A valve that can be placed on a Thermoelectric Boiler multiblock, allowing for the insertion of energy and water along with the extraction of produced steam.
  // 
  // Review revision: Two controlled pressure connections mounted in the existing boiler wall; level board and rubber seals form the service port. Existing pack items; proposed editor recipe, no gameplay export.
  // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
  event.shaped('mekanism:boiler_valve', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:steel_pipe',
      B: 'tfmg:steel_fluid_valve',
      C: 'mekanism:boiler_casing',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:mekanism/boiler/valve')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Nuclear chemical electrolysis/separation, separate from generic ore recovery.
    // 
    // Review revision: Paired electrodes and insulated high-current bus flank a chemical vessel, with separate gas outlets above. Nuclear reagent separation is its role; do not use as a generic ore multiplication shortcut. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('nuclearcraft:electrolyzer', ['A B A', 'CDDDC', 'EFGFE', 'EHIHE', 'JKKKJ'], {
        A: 'mekanism:basic_chemical_tank',
        B: 'tfmg:steel_pipe',
        C: 'mekanism:hdpe_sheet',
        D: 'tfmg:steel_chemical_vat',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:graphite_electrode',
        G: 'createaddition:electrum_wire',
        H: 'tfmg:circuit_board',
        I: 'mekanism:ultimate_control_circuit',
        J: 'tfmg:nickel_sheet',
        K: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/electrolyzer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('simulated:redstone_magnet', ['ABA', 'CDC', 'AEA'], {
        A: 'create:copper_sheet',
        B: 'minecraft:redstone',
        C: 'create:electron_tube',
        D: 'tfmg:cast_iron_frame',
        E: 'tfmg:magnet'
      }).id('industrial_colonies:simulated/redstone_magnet')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('industrial_colonies')) {
    // [Digital Logistics] Stamp canonical TFMG silicon in a reusable AE2 silicon mold
    event.recipes.industrial_colonies.brass_compacting(['ae2:printed_silicon'], ['tfmg:silicon_ingot', 'ae2:silicon_press']).id('industrial_colonies:electronics/printed_silicon')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('mekanism')) {
    // [Mekanized Industry] Infuse the populated TFMG board with redstone to establish Mekanism control logic
    event.custom({ type: 'mekanism:metallurgic_infusing', item_input: { count: 1, item: 'tfmg:circuit_board' }, chemical_input: { amount: 20, tag: 'mekanism:redstone' }, output: { count: 1, id: 'mekanism:basic_control_circuit' }, per_tick_usage: false }).id('industrial_colonies:mekanism/basic_control_circuit')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Industrial digital-matter shell: Radiance supports, precision glass, engineering error control, concurrent addressing and isolated heavy housing. Required by cells above16k; 1k/4k/16k use independent smaller construction. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:item_cell_housing', ['ABBBA', 'CDEDC', 'FGHGF', 'IDJDI', 'AKKKA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'ae2:quartz_vibrant_glass',
        C: 'create:refined_radiance',
        D: 'tfmg:circuit_board',
        E: 'ae2:engineering_processor',
        F: 'createaddition:electrum_wire',
        G: 'tfmg:heavy_machinery_casing',
        H: 'extendedae:concurrent_processor',
        I: 'tfmg:rubber_sheet',
        J: 'ae2:calculation_processor',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:digital_core/item_cell_housing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Two-tier spark-ignition cylinder bank, paired carburetion, common crank bed and lower ignition supply. Large engine remains a fuel machine, not a nuclear gate. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:large_engine', ['ABABA', 'CDEDC', 'CDEDC', 'FFGFF', 'HIJIH', 'KLLLK'], {
        A: 'tfmg:spark_plug',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:heavy_plate',
        D: 'tfmg:engine_cylinder',
        E: 'create:fluid_valve',
        F: 'create:shaft',
        G: 'tfmg:crankshaft',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:circuit_board',
        J: 'tfmg:capacitor_item',
        K: 'tfmg:nickel_sheet',
        L: 'tfmg:steel_frame'
      }).id('industrial_colonies:engines/large_engine')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Build the refinery controller as a lead-lined steel manifold with analog instrumentation and buffer tanks
    event.recipes.create.mechanical_crafting('tfmg:steel_distillation_controller', [' ABA ', 'ACDCA', 'BEFEB', 'AGGGA', ' BBB '], {
        A: '#c:plates/lead',
        B: 'tfmg:industrial_pipe',
        C: 'create:electron_tube',
        D: 'minecraft:compass',
        E: 'tfmg:steel_mechanism',
        F: 'tfmg:heavy_machinery_casing',
        G: 'tfmg:steel_fluid_tank'
      }).id('industrial_colonies:petroleum/steel_distillation_controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Build the third-rail pickup from a rubber-isolated mechanism, hinged heavy-steel carrier, and broad copper contact shoe
    event.recipes.create.mechanical_crafting('electroenergetics:rail_contact_shoe', ['ABA', 'CDC', 'EEE'], {
        A: 'tfmg:rubber_sheet',
        B: 'tfmg:steel_mechanism',
        C: 'tfmg:heavy_plate',
        D: 'create:shaft',
        E: 'create:copper_sheet'
      }).id('industrial_colonies:electroenergetics/rail_contact_shoe')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Steel & Petroleum] Arrange the first pump as an inline cast-iron pipe, gear drive, and replaceable precision crank
    event.recipes.create.mechanical_crafting('tfmg:cast_iron_mechanical_pump', ['ABA', 'CDC', ' A '], {
        A: 'tfmg:cast_iron_sheet',
        B: 'tfmg:cast_iron_pipe',
        C: 'create:precision_mechanism',
        D: 'create:cogwheel'
      }).id('industrial_colonies:fluid_infrastructure/cast_iron_mechanical_pump')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Upper motor/gear head and engineering circuit control drive the central mixing shaft; electrum braces carry measurement wiring and the whisk hangs in an open lower bay. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:brass_mixer', ['  A  ', 'BCDCB', 'EFGFE', 'H C H', 'H I H', ' J J '], {
        A: 'tfmg:electric_motor',
        B: 'tfmg:nickel_sheet',
        C: 'create:shaft',
        D: 'create:large_cogwheel',
        E: 'tfmg:circuit_board',
        F: 'ae2:engineering_processor',
        G: 'mekanism:advanced_control_circuit',
        H: 'immersiveengineering:plate_electrum',
        I: 'create:whisk',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:manufacturing/brass/mixer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Two heavy insulated cable entries feed a central buffered bus and shielded distribution board; reinforced lower mounting beam, no motor-shaped cabinet. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:heavy_cable_hub', ['AB BA', 'CBDBC', 'EFFFE', 'GHHHG'], {
        A: 'electroenergetics:heavily_insulated_wire',
        B: 'createaddition:electrum_wire',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:capacitor_item',
        E: 'tfmg:magnetic_alloy_sheet',
        F: 'tfmg:circuit_board',
        G: 'tfmg:heavy_plate',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:tfmg_coverage/heavy_cable_hub')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Populate the first 1k memory board with quartz memory, silicon addressing, logic, fluix timing, capacitance, and insulation
    event.recipes.create.sequenced_assembly(['ae2:cell_component_1k'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:certus_quartz_crystal']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_dust']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:v3_ae2/cell_component_1k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Fluid digital-matter shell adds pressure manifolds and double sealing to an Industrial Iron/Radiance containment cabinet. Large fluid storage is a stationary industrial investment. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:fluid_cell_housing', ['ABCBA', 'DEFED', 'GHDHG', 'IEJEI', 'AKKKA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'tfmg:steel_pipe',
        C: 'ae2:quartz_vibrant_glass',
        D: 'create:refined_radiance',
        E: 'tfmg:circuit_board',
        F: 'ae2:engineering_processor',
        G: 'createaddition:electrum_wire',
        H: 'tfmg:heavy_machinery_casing',
        I: 'tfmg:rubber_sheet',
        J: 'ae2:calculation_processor',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/fluid_cell_housing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Upgrade the ME Terminal with a real crafting grid, calculation processor, blank-pattern buffer, and stress-aware input controller
    event.recipes.create.sequenced_assembly(['ae2:crafting_terminal'], 'ae2:terminal', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:crafting_table']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:blank_pattern']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:terminal'}})).loops(1).id('industrial_colonies:v3_ae2/crafting_terminal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mekanized Industry] Give the terminal direct pattern inventory access through a provider, capacity controller, smart bus, and logic board
    event.recipes.create.sequenced_assembly(['ae2:pattern_access_terminal'], 'ae2:terminal', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:pattern_provider']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:capacity_card']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_cable']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:terminal'}})).loops(1).id('industrial_colonies:v3_ae2/pattern_access_terminal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Wind and populate a buffered stress matrix over two recognizable Brass electronics passes
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_1k'], 'ae2:cell_component_4k', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(2).id('industrial_colonies:appliedcreate/stress_storage_component_1k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Upgrade installer, not a separately craftable elite machine: previous installation kit, elite controls and revised wiring on structural rails. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:elite_tier_installer', ['ABBBA', 'CDEDC', 'AFGFA', 'AHHHA'], {
        A: 'tfmg:nickel_sheet',
        B: 'createaddition:electrum_wire',
        C: 'tfmg:circuit_board',
        D: 'mekanism:elite_control_circuit',
        E: 'ae2:engineering_processor',
        F: 'mekanism:advanced_tier_installer',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism/tier_installer/elite')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Shape a cobalt-and-atomic cutting head above a magnetic drive, ultimate controller, Energy Tablet, osmium neck, and obsidian grip.
    event.recipes.create.mechanical_crafting('mekanism:atomic_disassembler', ['ABBA', ' CDE', '  F ', '  G '], {
        A: 'mekanism:alloy_atomic',
        B: 'modernfoundry:cobalt_ingot',
        C: 'tfmg:electromagnetic_coil',
        D: 'mekanism:ultimate_control_circuit',
        E: 'mekanism:energy_tablet',
        F: 'mekanism:ingot_osmium',
        G: 'mekanism:ingot_refined_obsidian'
      }).id('industrial_colonies:mekanism_tools/atomic_disassembler')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Install the 16k stress matrix in its braced housing, instrument the kinetic load path, add tier-appropriate stress control, and press the service enclosure closed
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_16k'], 'appliedcreate:andesite_stress_cell_housing', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_16k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:stressometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:andesite_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_16k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Install the 1k stress matrix in its braced housing, instrument the kinetic load path, add tier-appropriate stress control, and press the service enclosure closed
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_1k'], 'appliedcreate:andesite_stress_cell_housing', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:shaft']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:stressometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:andesite_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_1k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Pressure-refit the Andesite stress shell with Brass plates, vibrant windows, magnetic shielding, and a plastic dielectric
    event.recipes.industrial_colonies.railway_compacting(['appliedcreate:brass_stress_cell_housing'], ['appliedcreate:andesite_stress_cell_housing', 'create:brass_sheet', 'create:brass_sheet', 'create:brass_sheet', 'create:brass_sheet', 'ae2:quartz_vibrant_glass', 'ae2:quartz_vibrant_glass', 'tfmg:magnetic_alloy_sheet', 'tfmg:magnetic_alloy_sheet', 'tfmg:plastic_sheet']).id('industrial_colonies:v3_ae2/brass_stress_cell_housing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Install the 64k stress matrix in its braced housing, instrument the kinetic load path, add tier-appropriate stress control, and press the service enclosure closed
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_64k'], 'appliedcreate:andesite_stress_cell_housing', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_64k']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:stressometer']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:andesite_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_64k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Install the 256k stress matrix in its braced housing, instrument the kinetic load path, add tier-appropriate stress control, and press the service enclosure closed
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_256k'], 'appliedcreate:andesite_stress_cell_housing', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_256k']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:rotation_speed_controller']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:stressometer']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:andesite_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_256k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Post-Nuclear Megaprojects] Finish the 256M stress core with its matching MEGA plane, ultimate control, exotic alloy contacts, and matter isolation
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_256m'], 'appliedcreate:stress_storage_component_64m', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'megacells:cell_component_256m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'allthemodium:unobtainium_vibranium_alloy_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:matter_ball']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_256m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Post-Nuclear Megaprojects] Install the 256m stress matrix in its braced housing, instrument the kinetic load path, add tier-appropriate stress control, and press the service enclosure closed
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_256m'], 'appliedcreate:brass_stress_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_256m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create_connected:kinetic_bridge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:kinetic_energy_acceptor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:rotation_speed_controller']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance_casing']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:unobtainium_vibranium_alloy_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:matter_ball']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:brass_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_256m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Stamp a bulk set of station vents from two rubber-isolated heavy-plate rails around a three-pipe airflow manifold
    event.recipes.create.mechanical_crafting('16x ad_astra:vent', ['ABA', 'CCC', 'ABA'], {
        A: 'tfmg:heavy_plate',
        B: 'tfmg:rubber_sheet',
        C: 'tfmg:steel_pipe'
      }).id('industrial_colonies:space/life_support/vent')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Sleeve a Create shaft with the staged separator, magnetic reinforcement, steel timing hardware, and service fasteners
    event.recipes.create.sequenced_assembly(['rocketnautics:separator_shaft'], 'create:shaft', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:separator']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_mechanism']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:shaft'}})).loops(1).id('industrial_colonies:space_coverage/separator_shaft')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Latest review: requested Weathered Iron press capability; all original quantities and output components preserved.
    event.recipes.industrial_colonies.weathered_iron_compacting(['16x ad_astra:steel_cable'], ['tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:copper_wire', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:heavy_plate', 'tfmg:heavy_plate']).id('industrial_colonies:space_coverage/steel_cable')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Press sixteen protected station cable runs around TFMG hubs and conduit, Ad Astra steel cable, and ComputerCraft networking for combined power and data service.
    event.recipes.industrial_colonies.refined_radiance_compacting(['16x ad_astra:cable_duct'], ['ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'ad_astra:steel_plating', 'tfmg:steel_cable_hub', 'tfmg:steel_cable_hub', 'tfmg:steel_cable_hub', 'tfmg:steel_cable_hub', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:cable_tube', 'tfmg:cable_tube', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'computercraft:cable', 'computercraft:cable', 'computercraft:cable', 'computercraft:cable', 'computercraft:cable', 'computercraft:cable', 'computercraft:cable', 'computercraft:cable']).id('industrial_colonies:space/station/cable_duct')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Planetary Industry] Re-jacket one station cable batch in conductive Desh plates and radiation-resistant plastic without discarding its copper core
    event.recipes.industrial_colonies.refined_radiance_compacting(['16x ad_astra:desh_cable'], ['ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:steel_cable', 'ad_astra:desh_plate', 'ad_astra:desh_plate', 'ad_astra:desh_plate', 'ad_astra:desh_plate', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet']).id('industrial_colonies:space_coverage/desh_cable')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Planetary Industry] Form sixteen vacuum-service pipes from TFMG steel tubes, Desh outer shells, glass inspection liners, and rubber seals
    event.recipes.industrial_colonies.refined_radiance_compacting(['16x ad_astra:desh_fluid_pipe'], ['tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'ad_astra:desh_plate', 'ad_astra:desh_plate', 'ad_astra:desh_plate', 'ad_astra:desh_plate', 'minecraft:glass', 'minecraft:glass', 'minecraft:glass', 'minecraft:glass', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet']).id('industrial_colonies:space_coverage/desh_fluid_pipe')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Planetary Industry] Upgrade a complete Desh pipe run with Ostrum pressure shells, magnetic reinforcement, and new service seals
    event.recipes.industrial_colonies.refined_radiance_compacting(['16x ad_astra:ostrum_fluid_pipe'], ['ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:desh_fluid_pipe', 'ad_astra:ostrum_plate', 'ad_astra:ostrum_plate', 'ad_astra:ostrum_plate', 'ad_astra:ostrum_plate', 'tfmg:magnetic_alloy_sheet', 'tfmg:magnetic_alloy_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet']).id('industrial_colonies:space_coverage/ostrum_fluid_pipe')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Planetary Industry] Rehouse a TFMG capacitor as a lithium-buffered Desh power cell with transistor regulation, diamond dielectric, and plastic isolation
    event.recipes.create.sequenced_assembly(['ad_astra:etrionic_capacitor'], 'tfmg:capacitor_item', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:dust_lithium']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:desh_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:diamond']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:capacitor_item'}})).loops(1).id('industrial_colonies:space_hardware/etrionic_capacitor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Twin Supercooler cores inside insulated cold chambers with ice-dragon coolant vials, separate pumping and ultimate regulation. Existing cold technology is used rather than unrelated space tanks. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ad_astra:cryo_freezer', ['ABABA', 'CDDDC', 'EFEFE', 'GHIHG', 'AJJJA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'minecraft:blue_ice',
        C: 'tfmg:electric_pump',
        D: 'nuclearcraft:supercooler',
        E: 'tfmg:steel_pipe',
        F: 'iceandfire:ice_dragon_blood',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:circuit_board',
        I: 'mekanism:ultimate_control_circuit',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:space_coverage/cryo_freezer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Roll and Railway-press steel plate around a steel mandrel into a four-section pressure-line batch.
    event.recipes.industrial_colonies.weathered_iron_compacting(['4x tfmg:steel_pipe'], [Ingredient.of('#c:plates/steel'), Ingredient.of('#c:ingots/steel'), Ingredient.of('#c:plates/steel')]).id('industrial_colonies:fluid_infrastructure/steel_pipe')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mega fluid storage shell: two already-expensive digital housings, central quantum core, quantum control and reinforced exotic containment. Unobtainium anchor points and Vibranium load rails make bulk portable storage a terminal-game investment; machine-space limits still enforce transport policy. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('megacells:mega_fluid_cell_housing', ['ABBBBBA', 'CDEFEDC', 'GHIJIHG', 'KFLMLFK', 'GHIJIHG', 'CDEFEDC', 'ABBBBBA'], {
        A: 'allthemodium:unobtainium_plate',
        B: 'allthemodium:vibranium_plate',
        C: 'rocketnautics:titanium_alloy_sheet',
        D: 'advanced_ae:quantum_alloy_plate',
        E: 'tfmg:circuit_board',
        F: 'advanced_ae:quantum_processor',
        G: 'createaddition:electrum_wire',
        H: 'ae2:fluid_cell_housing',
        I: 'ae2:engineering_processor',
        J: 'mekanism:ultimate_control_circuit',
        K: 'tfmg:rubber_sheet',
        L: 'tfmg:steel_frame',
        M: 'advanced_ae:quantum_core'
      }).id('industrial_colonies:v3_ae2/mega_fluid_cell_housing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mega item storage shell: two already-expensive digital housings, central quantum core, quantum control and reinforced exotic containment. Unobtainium anchor points and Vibranium load rails make bulk portable storage a terminal-game investment; machine-space limits still enforce transport policy. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('megacells:mega_item_cell_housing', ['ABBBBBA', 'CDEFEDC', 'GHIJIHG', 'KFLMLFK', 'GHIJIHG', 'CDEFEDC', 'ABBBBBA'], {
        A: 'allthemodium:unobtainium_plate',
        B: 'allthemodium:vibranium_plate',
        C: 'rocketnautics:titanium_alloy_sheet',
        D: 'advanced_ae:quantum_alloy_plate',
        E: 'tfmg:circuit_board',
        F: 'advanced_ae:quantum_processor',
        G: 'createaddition:electrum_wire',
        H: 'ae2:item_cell_housing',
        I: 'ae2:engineering_processor',
        J: 'mekanism:ultimate_control_circuit',
        K: 'tfmg:rubber_sheet',
        L: 'tfmg:steel_frame',
        M: 'advanced_ae:quantum_core'
      }).id('industrial_colonies:v3_ae2/mega_item_cell_housing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Turn a tested gas tank into a personal regulator by fitting a steel valve, electric metering pump, rubber harness, plastic manifold, coated TFMG controller, and transistor flow switch
    event.recipes.create.sequenced_assembly(['ad_astra:oxygen_gear'], 'ad_astra:gas_tank', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_pump']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ad_astra:gas_tank'}})).loops(1).id('industrial_colonies:space/life_support/oxygen_gear')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Convert a copper nozzle into a closed-loop attitude jet with a hose anchor, electric metering pump, TFMG potentiometer, coated controller, transistor valve driver, plastic insulation, and titanium heat shield
    event.recipes.create.sequenced_assembly(['rocketnautics:rcs_thruster'], 'rocketnautics:copper_nozzle', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:hose_anchor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_pump']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:potentiometer']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'rocketnautics:copper_nozzle'}})).loops(1).id('industrial_colonies:space_coverage/rcs_thruster')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Interstellar Escape] Assemble the reusable Warp Drive as a deliberate field-engine cross-section: paired Crystal Drivers and signed Warp Crystals around ultimate storage and quantum anchors, with Calorite focusing, heavy containment, duplicate route memory, navigation authority, and the Industrial Star core
    event.recipes.create.mechanical_crafting('cosmowarp:warp_drive', ['ABCBA', 'DEFED', 'GHIHG', 'DCJCD', 'AKLKA'], {
        A: 'rocketnautics:titanium_casing',
        B: 'cosmowarp:crystal_driver',
        C: 'tfmg:heavy_machinery_casing',
        D: 'mekanism:ultimate_energy_cube',
        E: 'ae2:quantum_entangled_singularity',
        F: 'mekanism:ultimate_control_circuit',
        G: 'ad_astra:calorite_plate',
        H: 'cosmowarp:warp_crystal',
        I: 'cosmowarp:moon_crystal',
        J: 'industrial_colonies:interstellar_navigation_computer',
        K: 'cosmowarp:memory_card',
        L: 'industrial_colonies:industrial_star'
      }).id('industrial_colonies:interstellar/warp_drive')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Interstellar Escape] Build the interstellar field driver as a layered control core: magnetic stabilizers hold the entangled anchor above the warp crystal, Moon Crystals and encoded memory flank the navigation computer, and TFMG electronics, plastic isolation, titanium, late alloy, and ultimate control close the power stage
    event.recipes.create.mechanical_crafting('cosmowarp:crystal_driver', [' ABA ', 'CDEDC', 'FGHGF', 'IJKJI', ' LML '], {
        A: 'rocketnautics:magnetic_stabilizer',
        B: 'ae2:quantum_entangled_singularity',
        C: 'tfmg:transformer',
        D: 'tfmg:plastic_sheet',
        E: 'cosmowarp:warp_crystal',
        F: 'cosmowarp:moon_crystal',
        G: 'cosmowarp:memory_card',
        H: 'industrial_colonies:interstellar_navigation_computer',
        I: 'rocketnautics:titanium_alloy_sheet',
        J: 'tfmg:etched_circuit_board',
        K: 'tfmg:capacitor_item',
        L: 'allthemodium:unobtainium_vibranium_alloy_ingot',
        M: 'mekanism:ultimate_control_circuit'
      }).id('industrial_colonies:space_coverage/crystal_driver')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Populate a TFMG circuit substrate with complementary semiconductors, an electron tube, and a timed redstone contact on the Brass electronics line
    event.recipes.create.sequenced_assembly(['2x create_connected:control_chip'], 'tfmg:circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:electron_tube']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:golden_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:redstone']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:circuit_board'}})).loops(2).id('industrial_colonies:create_addons/connected_control_chip')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Rehouse the native depot as a conductive Copper production tool with a distinct working assembly.
    event.recipes.create.sequenced_assembly(['createcasing:copper_depot'], 'create:depot', [
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:copper_casing']),
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:copper_sheet']),
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:iron_sheet']),
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:chute']),
        event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:depot'}})).loops(1).id('industrial_colonies:manufacturing/copper/depot')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Index a 16k memory plane through a precision geartrain and logic processor, then shield its stress controller with TFMG magnetic alloy, plastic dielectric, and vibrant quartz
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_16k'], 'appliedcreate:stress_storage_component_4k', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:cell_component_16k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_16k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Bind the 4M MEGA plane to advanced stress and accumulation control, spatial addressing, kinetic acceptance, matter isolation, Refined Radiance contacts, and an Allthemodium conductor plate
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_4m'], 'appliedcreate:stress_storage_component_1m', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'megacells:cell_component_4m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'megacells:accumulation_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:spatial_cell_component_2']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:kinetic_energy_acceptor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:matter_ball']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'create:refined_radiance']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'allthemodium:allthemodium_plate']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_4m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Close the 4M matrix into its Brass housing around a bridged kinetic acceptor and governor, then add advanced stress logic, a Radiance shell, Allthemodium load plate, and TFMG plastic isolation
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_4m'], 'appliedcreate:brass_stress_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_4m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create_connected:kinetic_bridge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:kinetic_energy_acceptor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:rotation_speed_controller']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance_casing']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:allthemodium_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:brass_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_4m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Build the staging plane around a controllable clutch by installing opposed separator charges and titanium break sheets, then add a plastic-isolated coated controller and transistor firing switch
    event.recipes.create.sequenced_assembly(['rocketnautics:separator'], 'create:clutch', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:separator_charge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:separator_charge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:clutch'}})).loops(1).id('industrial_colonies:space_coverage/separator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Planetary Industry] Assemble a recognizable four-wheel Desh rover: computer, radio, and navigation table fill the cab; a capacitor, etched board, and calculation processor form the avionics shelf; plastic-isolated tank and energy storage ride in the steel chassis ahead of the engine
    event.recipes.create.mechanical_crafting('ad_astra:tier_1_rover', [' ABC ', 'DEFGH', 'IJKJI', 'L M L', ' L L '], {
        A: 'computercraft:computer_advanced',
        B: 'simulated:navigation_table',
        C: 'ad_astra:radio',
        D: 'ad_astra:desh_plate',
        E: 'tfmg:etched_circuit_board',
        F: 'tfmg:capacitor_item',
        G: 'ae2:calculation_processor',
        H: 'ad_astra:desh_engine',
        I: 'tfmg:steel_frame',
        J: 'tfmg:plastic_sheet',
        K: 'ad_astra:desh_tank',
        L: 'ad_astra:wheel',
        M: 'mekanism:advanced_energy_cube'
      }).id('industrial_colonies:space_coverage/tier_1_rover')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Couple the first MEGA memory plane to advanced stress and accumulation logic, a kinetic bridge, 2-cubed spatial addressing, isolated TFMG power, magnetic containment, and lithium ride-through
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_1m'], 'appliedcreate:stress_storage_component_256k', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'megacells:cell_component_1m']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'megacells:accumulation_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'create_connected:kinetic_bridge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:spatial_cell_component_2']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:transformer']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_1m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mega fluid capacity installed inside the dedicated endgame shell, with quantum addressing, metered fluid interface and reinforced seal. Memory components remain separately balanced for crafting computers. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:fluid_storage_cell_16m'], 'megacells:mega_fluid_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_16m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_fluid_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_fluid_storage_cell_16m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mega fluid capacity installed inside the dedicated endgame shell, with quantum addressing, metered fluid interface and reinforced seal. Memory components remain separately balanced for crafting computers. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:fluid_storage_cell_1m'], 'megacells:mega_fluid_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_1m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_fluid_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_fluid_storage_cell_1m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mega fluid capacity installed inside the dedicated endgame shell, with quantum addressing, metered fluid interface and reinforced seal. Memory components remain separately balanced for crafting computers. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:fluid_storage_cell_256m'], 'megacells:mega_fluid_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_256m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_fluid_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_fluid_storage_cell_256m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mega fluid capacity installed inside the dedicated endgame shell, with quantum addressing, metered fluid interface and reinforced seal. Memory components remain separately balanced for crafting computers. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:fluid_storage_cell_4m'], 'megacells:mega_fluid_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_4m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_fluid_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_fluid_storage_cell_4m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mega fluid capacity installed inside the dedicated endgame shell, with quantum addressing, metered fluid interface and reinforced seal. Memory components remain separately balanced for crafting computers. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:fluid_storage_cell_64m'], 'megacells:mega_fluid_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_64m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_fluid_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_fluid_storage_cell_64m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Finish the 64M enclosure with a bridged kinetic acceptor and governor, advanced stress control, Radiance shell, dense fluix service bus, TFMG power isolation, and an Unobtainium load plate
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_64m'], 'appliedcreate:brass_stress_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_64m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create_connected:kinetic_bridge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:kinetic_energy_acceptor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:rotation_speed_controller']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance_casing']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_dense_cable']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transformer']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:unobtainium_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:brass_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_64m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Interstellar Escape] Encode a blank ME pattern as interstellar route memory by installing an etched TFMG controller, engineering processor, transistor and capacitor signal stages, Moon Crystal reference, plastic dielectric, and titanium radiation shield
    event.recipes.create.sequenced_assembly(['cosmowarp:memory_card'], 'ae2:blank_pattern', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'cosmowarp:moon_crystal']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quantum_entangled_singularity']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:vibranium_allthemodium_alloy_ingot']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:blank_pattern'}})).loops(1).id('industrial_colonies:space_coverage/warp_memory_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Mechanical Foundations] Saw one standard shaft into one calibrated sacrificial shear pin on the native Andesite cutting line
    event.recipes.industrial_colonies.base_cutting(['create_connected:shear_pin'], 'create:shaft').processingTime(200).id('industrial_colonies:create_connected/shear_pin')
  }
})

ServerEvents.recipes(event => {
  // [Steel & Petroleum] Build the corrosion-service valve with a plastic pipe body, rubber seals, plastic backing, and external handwheel
  event.shaped('tfmg:plastic_fluid_valve', [' A ', 'BCB', ' D '], {
      A: 'create:copper_valve_handle',
      B: 'tfmg:rubber_sheet',
      C: 'tfmg:plastic_pipe',
      D: 'tfmg:plastic_sheet'
    }).id('industrial_colonies:tfmg_coverage/plastic_fluid_valve')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Fabricate a Railway depot as a heavy receiving table over paired observers, with complementary routing electronics, plastic insulation, a populated board, Brass depot core, and framed base
    event.recipes.create.mechanical_crafting('createcasing:railway_depot', ['AAAA', 'BCCB', 'DEFG', 'HHIH'], {
        A: 'tfmg:heavy_plate',
        B: 'create:railway_casing',
        C: 'create:content_observer',
        D: 'tfmg:plastic_sheet',
        E: 'tfmg:n_semiconductor',
        F: 'tfmg:coated_circuit_board',
        G: 'tfmg:p_semiconductor',
        H: 'tfmg:steel_frame',
        I: 'createcasing:brass_depot'
      }).id('industrial_colonies:manufacturing/railway/depot')
  }
})

ServerEvents.recipes(event => {
  // [Digital Logistics] Build the light-service valve as a handwheel and clamped aluminum body around the matching pipe
  event.shaped('tfmg:aluminum_fluid_valve', [' A ', 'BCB', ' D '], {
      A: 'create:copper_valve_handle',
      B: 'tfmg:aluminum_sheet',
      C: 'tfmg:aluminum_pipe',
      D: 'tfmg:screw'
    }).id('industrial_colonies:tfmg_coverage/aluminum_fluid_valve')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Install the 1M stress matrix in its Brass housing with a kinetic bridge and acceptor, advanced stress control, governed rotation, TFMG magnetic bracing, lithium ride-through, and a vibrant service face
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_1m'], 'appliedcreate:brass_stress_cell_housing', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_1m']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create_connected:kinetic_bridge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:kinetic_energy_acceptor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:rotation_speed_controller']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:brass_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_1m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Enclose the 16M matrix around a bridged kinetic acceptor and governor, then stabilize advanced stress control with a Radiance shell, Vibranium load plate, and matter-isolation layer
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_cell_16m'], 'appliedcreate:brass_stress_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_storage_component_16m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create_connected:kinetic_bridge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:kinetic_energy_acceptor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:rotation_speed_controller']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance_casing']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:vibranium_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:matter_ball']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:brass_stress_cell_housing'}})).loops(1).id('industrial_colonies:appliedcreate/stress_storage_cell_16m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Coordinate the 64M MEGA plane with quantum stress logic and full-scale spatial addressing, then route its kinetic acceptor through a dense fluix bus, Unobtainium field plate, and Radiance enclosure
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_64m'], 'appliedcreate:stress_storage_component_16m', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'megacells:cell_component_64m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:spatial_cell_component_128']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:kinetic_energy_acceptor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:fluix_smart_dense_cable']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'allthemodium:unobtainium_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'create:refined_radiance_casing']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_64m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Form two actively monitored titanium nozzle throats around a valved engine-pipe manifold; a plastic-isolated etched board and paired capacitors instrument the steel load mechanism before the two outlet pipes are attached
    event.recipes.create.mechanical_crafting('2x rocketnautics:engine_nozzle', [' A A ', 'BCDCB', ' EFE ', 'BGHGB', ' C C '], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'tfmg:heavy_plate',
        C: 'rocketnautics:engine_pipes',
        D: 'tfmg:steel_fluid_valve',
        E: 'tfmg:plastic_sheet',
        F: 'tfmg:etched_circuit_board',
        G: 'tfmg:capacitor_item',
        H: 'tfmg:steel_mechanism'
      }).id('industrial_colonies:space/propulsion/engine_nozzle')
  }
})

ServerEvents.recipes(event => {
  // [Orbital Engineering] Brace a TFMG steel frame with crossed rods, heavy thrust plates, and a central service mechanism
  event.shaped('ad_astra:engine_frame', ['ABA', 'CDC', 'ABA'], {
      A: 'ad_astra:steel_rod',
      B: 'ad_astra:steel_panel',
      C: 'tfmg:steel_frame',
      D: 'tfmg:steel_mechanism'
    }).id('industrial_colonies:space_coverage/engine_frame')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Give the rocket thruster a closed-loop vector stage with a gimbal sensor, gyroscopic reference, TFMG motor, calculation processor, coated control board, capacitor buffer, and plastic pivot isolation
    event.recipes.create.sequenced_assembly(['rocketnautics:vector_thruster'], 'rocketnautics:rocket_thruster', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'simulated:gimbal_sensor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'simulated:gyroscopic_mechanism']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'rocketnautics:rocket_thruster'}})).loops(1).id('industrial_colonies:space_coverage/vector_thruster')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Reuse the working normal turtle chassis with an advanced onboard computer, engineering control and titanium protective panels. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('computercraft:turtle_advanced', [' ABA ', 'CDDDC', 'EFGFE', 'HIJIH', 'HKKKH'], {
        A: 'immersiveengineering:plate_steel',
        B: 'create:brass_hand',
        C: 'tfmg:electric_motor',
        D: 'create:shaft',
        E: 'createaddition:electrum_wire',
        F: 'tfmg:circuit_board',
        G: 'ae2:engineering_processor',
        H: 'rocketnautics:titanium_alloy_sheet',
        I: 'computercraft:computer_advanced',
        J: 'computercraft:turtle_normal',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:computercraft/mobile/advanced_turtle_upgrade')
  }
})

ServerEvents.recipes(event => {
  // [Electrical Manufacturing] Build the canonical pre-steel TFMG local cable endpoint from brass, copper wire, and iron hardware
  event.shaped('tfmg:cable_connector', ['AAA', ' B ', ' C '], {
      A: '#c:nuggets/iron',
      B: '#c:wires/copper',
      C: '#c:plates/brass'
    }).id('industrial_colonies:early_power_cables/cable_connector')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Expensive quantum-assisted survey proposal with precision optics, engineering interpretation and Radiance supports. Arbitrary ore-target scanning is still unimplemented; this draft changes construction only. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:surface_scanner', ['  A  ', 'BCDCB', 'EFGFE', 'HIJIH', 'KLLLK'], {
        A: 'minecraft:amethyst_shard',
        B: 'minecraft:glass',
        C: 'advanced_ae:quantum_processor',
        D: 'create:content_observer',
        E: 'create:refined_radiance',
        F: 'tfmg:circuit_board',
        G: 'ae2:engineering_processor',
        H: 'createaddition:electrum_wire',
        I: 'tfmg:heavy_machinery_casing',
        J: 'tfmg:capacitor_item',
        K: 'rocketnautics:titanium_alloy_sheet',
        L: 'tfmg:steel_frame'
      }).id('industrial_colonies:machine/oil_processing/surface_scanner')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Interstellar Escape] Build the full five-by-five quantum compute tower as a recognizable physical machine: structural glass shell, alloy bus, processor banks, core, accelerator, unit, assembler, provider, Radiant base, and exotic side conductors
    event.recipes.create.mechanical_crafting('advanced_ae:quantum_crafter', [' ABA ', 'BCDCB', 'EFGFE', 'BCHBC', ' III '], {
        A: 'advanced_ae:quantum_structure',
        B: 'advanced_ae:quantum_alloy_plate',
        C: 'advanced_ae:quantum_processor',
        D: 'advanced_ae:quantum_core',
        E: 'allthemodium:vibranium_allthemodium_alloy_ingot',
        F: 'advanced_ae:quantum_accelerator',
        G: 'extendedae:ex_molecular_assembler',
        H: 'advanced_ae:quantum_unit',
        I: 'create:refined_radiance_casing'
      }).id('industrial_colonies:v3_ae2/quantum_crafter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Electrical Manufacturing] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('electroenergetics:ammeter', [' A ', 'BCD', ' E '], {
        A: 'minecraft:glass_pane',
        B: 'electroenergetics:connector',
        C: 'tfmg:multimeter',
        D: 'tfmg:copper_wire',
        E: 'tfmg:plastic_sheet'
      }).id('industrial_colonies:electroenergetics/grid_meter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('electroenergetics:relay', [' A  ', 'BCDB', ' E  '], {
        A: 'electroenergetics:connector',
        B: 'tfmg:copper_wire',
        C: 'electroenergetics:cut_off_switch',
        D: 'tfmg:electromagnetic_coil',
        E: 'tfmg:resistor'
      }).id('industrial_colonies:create_addons/electrical_relay')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('create_connected:inventory_bridge', [' A  ', 'BCBD', ' EE '], {
        A: 'create:mechanical_arm',
        B: 'create_connected:inventory_access_port',
        C: 'create:smart_chute',
        D: 'create_connected:control_chip',
        E: 'tfmg:circuit_board'
      }).id('industrial_colonies:create_addons/inventory_bridge')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Wide bank of driven displays above one control board and calculation readout, supported by brass brackets. Monitoring panel silhouette, not a motor or generic cube. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('create_connected:dashboard', ['AAAAA', 'ABBBA', 'CDEDC', 'FGGGF'], {
        A: 'minecraft:glass',
        B: 'tfmg:segmented_display',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:circuit_board',
        E: 'ae2:calculation_processor',
        F: 'create:brass_sheet',
        G: 'tfmg:steel_frame'
      }).id('industrial_colonies:create_addons/connected_dashboard')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Fit a memory component into an existing crafting CPU chassis. This is job-planning workspace; it must not inherit portable item-cell housing costs. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:1k_crafting_storage'], 'ae2:crafting_unit', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:crafting_unit'}})).loops(1).id('industrial_colonies:digital_storage/ae2_crafting_storage_1k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Fit a memory component into an existing crafting CPU chassis. This is job-planning workspace; it must not inherit portable item-cell housing costs. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:4k_crafting_storage'], 'ae2:crafting_unit', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_4k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:crafting_unit'}})).loops(1).id('industrial_colonies:digital_storage/ae2_crafting_storage_4k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('advancedperipherals:environment_detector', [' A ', 'BCD', ' EF'], {
        A: 'minecraft:daylight_detector',
        B: 'minecraft:clock',
        C: 'advancedperipherals:peripheral_casing',
        D: 'minecraft:compass',
        E: 'minecraft:sculk_sensor',
        F: 'create:content_observer'
      }).id('industrial_colonies:computer_network_coverage/environment_detector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Compact three-channel metering panel: three instrument faces and an isolated calculation bus. Distinct from the electrical switchboard and transformer recipes. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('electroenergetics:tri_polar_energy_meter', ['AAAAA', 'ABCBA', 'DEFED', 'GHHHG'], {
        A: 'minecraft:glass',
        B: 'electroenergetics:ammeter',
        C: 'tfmg:voltmeter',
        D: 'tfmg:rubber_sheet',
        E: 'createaddition:electrum_wire',
        F: 'ae2:calculation_processor',
        G: 'tfmg:nickel_sheet',
        H: 'tfmg:circuit_board'
      }).id('industrial_colonies:create_addons/tri_polar_energy_meter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Diamond optical axis over a Mekanism power-tablet pump and reinforced-alloy bus, buffered by capacitors; more actual Mekanism power technology, no unrelated crafting core. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:laser', [' A ', 'BCB', 'DED', 'FGF', 'HHH'], {
        A: 'minecraft:diamond',
        B: 'tfmg:nickel_sheet',
        C: 'mekanism:energy_tablet',
        D: 'tfmg:capacitor_item',
        E: 'mekanism:alloy_reinforced',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism/laser/emitter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Separate chemical reservoirs feed a reinforced mixing chamber and refined Mekanism process-control circuit. Chemical handling uses its own industrial circuitry rather than only AE2 digital parts. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:chemical_infuser', ['A B A', 'BCDCB', 'EFGFE', 'HIJIH'], {
        A: 'mekanism:basic_chemical_tank',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:steel_chemical_vat',
        D: 'mekanism:alloy_reinforced',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'mekanism:advanced_control_circuit',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:electric_motor',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_pre_nuclear/chemical_infuser')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Solid feed into an infused-alloy reaction support, gas outlet and basic Mekanism chemical controls; no false oxygen-input requirement or advanced nuclear gate. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:chemical_oxidizer', ['  A  ', 'BCDCB', 'E C E', 'FGHGF', 'BIJIB'], {
        A: 'minecraft:hopper',
        B: 'tfmg:nickel_sheet',
        C: 'tfmg:steel_chemical_vat',
        D: 'mekanism:alloy_infused',
        E: 'tfmg:steel_pipe',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'mekanism:basic_control_circuit',
        I: 'tfmg:steel_frame',
        J: 'tfmg:electric_motor'
      }).id('industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Review correction: a larger 4x4 frame, with a glazed inspection face, central steel structure, reinforced lower rails and dedicated controller mounts.
    event.recipes.create.mechanical_crafting('extendedae:machine_frame', ['ABBA', 'CDEC', 'FGGF', 'ABBA'], {
        A: 'extendedae:entro_ingot',
        B: 'tfmg:heavy_plate',
        C: 'ae2:quartz_glass',
        D: 'megacells:accumulation_processor',
        E: 'extendedae:concurrent_processor',
        F: 'ae2:quartz_vibrant_glass',
        G: 'tfmg:steel_frame'
      }).id('industrial_colonies:extendedae/machine_frame')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Review correction: a simpler insulated disconnect with a sealed gas manifold, rather than the previous dense 5x5 electronics wall.
    event.recipes.create.mechanical_crafting('electroenergetics:sulfur_hexafluoride_breaker', [' A ', 'BCB', 'BDB', ' A '], {
        A: 'tfmg:heavy_machinery_casing',
        B: 'electroenergetics:insulator',
        C: 'electroenergetics:connector',
        D: 'electroenergetics:cut_off_switch'
      }).id('industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Plate, not sheet. Direct adaptation of Personal Recipes steel-plate card: cut, press, deploy screw, press, deploy screw, press; TWO loops, one ingot and four screws total for one plate. weathered_iron machine capability proposed. Existing finished plate as transitional follows the user reference; incomplete-workpiece/shortcut audit remains required before export. Native competing routes not removed by this draft.
    event.recipes.create.sequenced_assembly(['immersiveengineering:plate_iron'], 'minecraft:iron_ingot', [
        event.recipes.industrial_colonies.weathered_iron_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'immersiveengineering:plate_iron'}})).loops(2).id('industrial_colonies:plate_assembly/iron')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Plate, not sheet. Direct adaptation of Personal Recipes steel-plate card: cut, press, deploy screw, press, deploy screw, press; TWO loops, one ingot and four screws total for one plate. weathered_iron machine capability proposed. Existing finished plate as transitional follows the user reference; incomplete-workpiece/shortcut audit remains required before export. Native competing routes not removed by this draft.
    event.recipes.create.sequenced_assembly(['immersiveengineering:plate_steel'], 'mekanism:ingot_steel', [
        event.recipes.industrial_colonies.weathered_iron_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'immersiveengineering:plate_steel'}})).loops(2).id('industrial_colonies:ownership/steel_sheet')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Plate, not sheet. Direct adaptation of Personal Recipes steel-plate card: cut, press, deploy screw, press, deploy screw, press; TWO loops, one ingot and four screws total for one plate. weathered_iron machine capability proposed. Existing finished plate as transitional follows the user reference; incomplete-workpiece/shortcut audit remains required before export. Native competing routes not removed by this draft.
    event.recipes.create.sequenced_assembly(['immersiveengineering:plate_nickel'], 'tfmg:nickel_ingot', [
        event.recipes.industrial_colonies.weathered_iron_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'immersiveengineering:plate_nickel'}})).loops(2).id('industrial_colonies:plate_assembly/nickel')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Plate, not sheet. Direct adaptation of Personal Recipes steel-plate card: cut, press, deploy screw, press, deploy screw, press; TWO loops, one ingot and four screws total for one plate. brass machine capability proposed. Existing finished plate as transitional follows the user reference; incomplete-workpiece/shortcut audit remains required before export. Native competing routes not removed by this draft.
    event.recipes.create.sequenced_assembly(['immersiveengineering:plate_electrum'], 'createaddition:electrum_ingot', [
        event.recipes.industrial_colonies.brass_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'immersiveengineering:plate_electrum'}})).loops(2).id('industrial_colonies:plate_assembly/electrum')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Keep the liked small platinum-contact cost, add a second reinforced support laminate around the Chromatic Compound. Industrial Iron process unchanged, one Radiance output; no nuclear-machine frame consumed per unit.
    event.recipes.industrial_colonies.industrial_iron_compacting(['create:refined_radiance'], ['create:chromatic_compound', 'mekanism:alloy_reinforced', 'minecraft:glowstone_dust', 'minecraft:amethyst_shard', 'nuclearcraft:platinum_nugget', 'nuclearcraft:platinum_nugget', 'mekanism:alloy_reinforced']).id('industrial_colonies:material_processing/refined_radiance')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Turn a TFMG steel enclosure into the common modem, processor, and insulated carrier for every advanced peripheral.
    event.recipes.create.sequenced_assembly(['advancedperipherals:peripheral_casing'], 'tfmg:steel_casing', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'computercraft:wired_modem_full']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_casing'}})).loops(1).id('industrial_colonies:digital_core/peripheral_casing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Orbital Engineering] Stack the booster down its true centerline: valve, feed pipes, tank, titanium casing, completed rocket thruster, and terminal nozzle; a plastic-isolated etched controller with paired capacitors occupies the side instrumentation bay
    event.recipes.create.mechanical_crafting('rocketnautics:booster_thruster', ['  A  ', 'BCDCB', 'BEFEB', 'GHIHG', 'B J B'], {
        A: 'tfmg:steel_smart_fluid_pipe',
        B: 'tfmg:heavy_plate',
        C: 'rocketnautics:engine_pipes',
        D: 'tfmg:etched_circuit_board',
        E: 'tfmg:steel_fluid_tank',
        F: 'rocketnautics:titanium_casing',
        G: 'tfmg:plastic_sheet',
        H: 'tfmg:capacitor_item',
        I: 'rocketnautics:rocket_thruster',
        J: 'rocketnautics:titanium_nozzle'
      }).id('industrial_colonies:space_coverage/booster_thruster')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Three pigment feed channels converge into a central mixture row, with independent upper reservoirs and lower refined process controls; horizontal flow layout rather than merely rotating the old vessel. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:pigment_mixer', ['A   A', 'BCBCB', 'DEEED', 'FGHGF', 'DIIID'], {
        A: 'mekanism:basic_chemical_tank',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:steel_chemical_vat',
        D: 'tfmg:nickel_sheet',
        E: 'mekanism:alloy_infused',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'mekanism:advanced_control_circuit',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_pre_nuclear/pigment_mixer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Scriptable ME interface with engineering processing, elite industrial control and Radiance support. Keeps the native interface and peripheral chassis as functional subassemblies. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('advancedperipherals:me_bridge', [' A A ', 'BCDCB', 'EFGFE', 'HIIIH'], {
        A: 'createaddition:electrum_wire',
        B: 'create:refined_radiance',
        C: 'mekanism:elite_control_circuit',
        D: 'ae2:engineering_processor',
        E: 'tfmg:rubber_sheet',
        F: 'ae2:interface',
        G: 'advancedperipherals:peripheral_casing',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:digital_core/me_bridge')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Solar electricity generation; compare its power/area with other generators rather than inventing a nuclear gate. Installed text: Construct a Solar Panel, allowing you to generate energy from the sun
    // 
    // [Planetary Industry] Fabricate four outpost panels as three photovoltaic cell rows in a Desh support lattice over a transformer bus, ultimate cable terminals, and one engineering regulator
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('4x ad_astra:solar_panel', ['ABABA', 'BAAAB', 'ABABA', 'BBCBB', 'D E D'], {
        A: 'ad_astra:photovoltaic_etrium_cell',
        B: 'ad_astra:desh_plate',
        C: 'tfmg:transformer',
        D: 'mekanism:ultimate_universal_cable',
        E: 'ae2:engineering_processor'
      }).id('industrial_colonies:planetary/outpost/solar_panel')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Controller for swapping a pylon-defined physical volume with a spatial cell. Transport-policy implications require separate approval.
    // 
    // Review revision: Spatial transfer controller around a real spatial cell, engineering/quantum control and isolated housing. This swaps physical volumes; extreme cost alone does not settle transport/ship bypass policy. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('ae2:spatial_io_port', ['ABBBA', 'CDEDC', 'FGHGF', 'IDJDI', 'AKKKA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'ae2:quartz_vibrant_glass',
        C: 'create:refined_radiance',
        D: 'tfmg:circuit_board',
        E: 'ae2:engineering_processor',
        F: 'createaddition:electrum_wire',
        G: 'tfmg:heavy_machinery_casing',
        H: 'ae2:spatial_storage_cell_128',
        I: 'tfmg:rubber_sheet',
        J: 'advanced_ae:quantum_processor',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/spatial_io_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Supplies a local breathable area using oxygen/energy. Needed only where retained dimension hazards require it. Installed text: Construct an Oxygen Distributor, allowing you to create livable environments
    // 
    // [Orbital Engineering] Build a real life-support manifold: paired fans feed a valved loader between large gas tanks, oxygen gear samples the outlet, and a TFMG etched board, capacitor, transistor, plastic insulation, advanced computer, and energy cube supervise the powered base
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('ad_astra:oxygen_distributor', [' ABA ', 'CDEFC', ' GHG ', 'AIJIA', ' KLK '], {
        A: 'ad_astra:fan',
        B: 'tfmg:steel_fluid_valve',
        C: 'ad_astra:large_gas_tank',
        D: 'tfmg:plastic_sheet',
        E: 'ad_astra:oxygen_loader',
        F: 'computercraft:computer_advanced',
        G: 'ad_astra:oxygen_gear',
        H: 'tfmg:etched_circuit_board',
        I: 'tfmg:capacitor_item',
        J: 'tfmg:transistor_item',
        K: 'tfmg:heavy_plate',
        L: 'mekanism:ultimate_energy_cube'
      }).id('industrial_colonies:space/life_support/oxygen_distributor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Sealed passage component for space builds; construction does not certify atmospheric simulation or every seal condition.
    // 
    // [Orbital Engineering] Construct a paired pressure doorway instead of an ingredient ring: heavy doors sit inside rubber-sealed steel uprights, with an oxygen sensor and advanced computer above a plastic-isolated control board, capacitor bank, and motorized latch
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('2x ad_astra:airlock', [' AAA ', 'BCDEB', 'AF FA', 'BCGHB', 'AIJIA'], {
        A: 'tfmg:heavy_plate',
        B: 'tfmg:rubber_sheet',
        C: 'tfmg:steel_frame',
        D: 'computercraft:computer_advanced',
        E: 'ad_astra:oxygen_sensor',
        F: 'tfmg:heavy_plated_door',
        G: 'tfmg:plastic_sheet',
        H: 'tfmg:coated_circuit_board',
        I: 'tfmg:capacitor_item',
        J: 'tfmg:electric_motor'
      }).id('industrial_colonies:space/life_support/airlock')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Guarded impeller in a copper shroud, insulated basic power controls and bearing supports; no completed electronics needed for the starter electrical machinery. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:copper_encased_fan', [' AAA ', 'BCDCB', 'EFGFE', 'HIIIH'], {
        A: 'minecraft:iron_bars',
        B: 'create:copper_casing',
        C: 'tfmg:copper_wire',
        D: 'create:propeller',
        E: 'tfmg:rubber_sheet',
        F: 'createaddition:capacitor',
        G: 'create:precision_mechanism',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:cast_iron_frame'
      }).id('industrial_colonies:manufacturing/copper/fan')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Open mixer support with insulated drive and existing basic capacitors, terminating in the existing whisk fitted below. Pre-Copper inputs only; no finished semiconductors or Copper-made board needed to build its own production line. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:copper_mixer', ['  A  ', 'BCDCB', 'EFFFE', ' AGA ', ' H H '], {
        A: 'create:shaft',
        B: 'create:copper_casing',
        C: 'tfmg:copper_wire',
        D: 'create:precision_mechanism',
        E: 'tfmg:rubber_sheet',
        F: 'createaddition:capacitor',
        G: 'create:whisk',
        H: 'tfmg:cast_iron_frame'
      }).id('industrial_colonies:manufacturing/copper/mixer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Review correction: three high-capacity storage banks sit above an addressing backplane and dual scheduling units. Mechanical Crafting builds the complete server block; its storage components remain process-manufactured.
    event.recipes.create.mechanical_crafting('megacells:1m_crafting_storage', ['ABBBA', 'CDDDC', 'EFGFE', 'HIJIH'], {
        A: 'ae2:quartz_vibrant_glass',
        B: 'megacells:cell_component_1m',
        C: 'ae2:fluix_smart_dense_cable',
        D: 'tfmg:coated_circuit_board',
        E: 'tfmg:capacitor_item',
        F: 'ae2:engineering_processor',
        G: 'megacells:accumulation_processor',
        H: 'tfmg:magnetic_alloy_sheet',
        I: 'megacells:mega_crafting_unit',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_crafting_storage_1m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Review correction: three high-capacity storage banks sit above an addressing backplane and dual scheduling units. Mechanical Crafting builds the complete server block; its storage components remain process-manufactured.
    event.recipes.create.mechanical_crafting('megacells:256m_crafting_storage', ['ABBBA', 'CDDDC', 'EFGFE', 'HIJIH'], {
        A: 'ae2:quartz_vibrant_glass',
        B: 'megacells:cell_component_256m',
        C: 'ae2:fluix_smart_dense_cable',
        D: 'tfmg:coated_circuit_board',
        E: 'tfmg:capacitor_item',
        F: 'ae2:engineering_processor',
        G: 'megacells:accumulation_processor',
        H: 'allthemodium:allthemodium_ingot',
        I: 'megacells:mega_crafting_unit',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_crafting_storage_256m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Review correction: three high-capacity storage banks sit above an addressing backplane and dual scheduling units. Mechanical Crafting builds the complete server block; its storage components remain process-manufactured.
    event.recipes.create.mechanical_crafting('megacells:4m_crafting_storage', ['ABBBA', 'CDDDC', 'EFGFE', 'HIJIH'], {
        A: 'ae2:quartz_vibrant_glass',
        B: 'megacells:cell_component_4m',
        C: 'ae2:fluix_smart_dense_cable',
        D: 'tfmg:coated_circuit_board',
        E: 'tfmg:capacitor_item',
        F: 'ae2:engineering_processor',
        G: 'megacells:accumulation_processor',
        H: 'tfmg:magnetic_alloy_sheet',
        I: 'megacells:mega_crafting_unit',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_crafting_storage_4m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Review correction: three high-capacity storage banks sit above an addressing backplane and dual scheduling units. Mechanical Crafting builds the complete server block; its storage components remain process-manufactured.
    event.recipes.create.mechanical_crafting('megacells:64m_crafting_storage', ['ABBBA', 'CDDDC', 'EFGFE', 'HIJIH'], {
        A: 'ae2:quartz_vibrant_glass',
        B: 'megacells:cell_component_64m',
        C: 'ae2:fluix_smart_dense_cable',
        D: 'tfmg:coated_circuit_board',
        E: 'tfmg:capacitor_item',
        F: 'ae2:engineering_processor',
        G: 'megacells:accumulation_processor',
        H: 'allthemodium:allthemodium_ingot',
        I: 'megacells:mega_crafting_unit',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_crafting_storage_64m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('computercraft:redstone_relay', [' AB ', 'CDEF', ' DB '], {
        A: 'create:redstone_link',
        B: 'create:electron_tube',
        C: 'ae2:printed_logic_processor',
        D: 'tfmg:circuit_board',
        E: 'computercraft:wired_modem',
        F: 'create:content_observer'
      }).id('industrial_colonies:computercraft/io/redstone_relay')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Pre-semiconductor ownership] Mechanical components precede final factory assembly.
    event.recipes.industrial_colonies.weathered_iron_pressing(['tfmg:cast_iron_sheet'], Ingredient.of('#c:ingots/cast_iron')).id('industrial_colonies:ownership/cast_iron_sheet')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Review correction: three high-capacity storage banks sit above an addressing backplane and dual scheduling units. Mechanical Crafting builds the complete server block; its storage components remain process-manufactured.
    event.recipes.create.mechanical_crafting('megacells:16m_crafting_storage', ['ABBBA', 'CDDDC', 'EFGFE', 'HIJIH'], {
        A: 'ae2:quartz_vibrant_glass',
        B: 'megacells:cell_component_16m',
        C: 'ae2:fluix_smart_dense_cable',
        D: 'tfmg:coated_circuit_board',
        E: 'tfmg:capacitor_item',
        F: 'ae2:engineering_processor',
        G: 'megacells:accumulation_processor',
        H: 'tfmg:magnetic_alloy_sheet',
        I: 'megacells:mega_crafting_unit',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_crafting_storage_16m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Digital Logistics] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('computercraft:speaker', [' A ', 'BCB', 'DED'], {
        A: 'tfmg:circuit_board',
        B: 'tfmg:copper_wire',
        C: 'minecraft:note_block',
        D: 'create:brass_sheet',
        E: 'create:electron_tube'
      }).id('industrial_colonies:computercraft/io/speaker')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Weathered Iron Mechanical Harvester] Native ingredient/output baseline from createcasing:crafting/harvester/weathered_iron. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
    event.recipes.create.mechanical_crafting('createcasing:weathered_iron_mechanical_harvester', ['ABA', 'ABA', ' C '], {
        A: 'create:andesite_alloy',
        B: '#c:plates/iron',
        C: 'create:weathered_iron_block'
      }).id('industrial_colonies:priority/createcasing/weathered_iron_mechanical_harvester')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Weathered Iron Mechanical Plough] Native ingredient/output baseline from createcasing:crafting/plough/weathered_iron. Draft progression/cost review; not gameplay-exported. Preserve recognizable mechanics.
    event.recipes.create.mechanical_crafting('createcasing:weathered_iron_mechanical_plough', ['AAA', 'BBB', ' C '], {
        A: '#c:plates/iron',
        B: 'create:andesite_alloy',
        C: 'create:weathered_iron_block'
      }).id('industrial_colonies:priority/createcasing/weathered_iron_mechanical_plough')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Restored prior user-reviewed reference after older Standby duplicate was reviewed: [Digital Logistics] Populate an existing empty TFMG circuit board with the printed logic and silicon dies, plastic dielectric, two green Starter Semiconductors, transistor, capacitor and redstone contacts; finish on the Brass press. Pink semiconductors are reserved for later electronics.
    event.recipes.create.sequenced_assembly(['ae2:logic_processor'], 'tfmg:empty_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_logic_processor', ['createappliedkinetics:incomplete_logic_processor', 'ae2:printed_logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_logic_processor', ['createappliedkinetics:incomplete_logic_processor', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_logic_processor', ['createappliedkinetics:incomplete_logic_processor', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_logic_processor', ['createappliedkinetics:incomplete_logic_processor', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_logic_processor', ['createappliedkinetics:incomplete_logic_processor', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_logic_processor', ['createappliedkinetics:incomplete_logic_processor', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_logic_processor', ['createappliedkinetics:incomplete_logic_processor', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('createappliedkinetics:incomplete_logic_processor', ['createappliedkinetics:incomplete_logic_processor', 'minecraft:redstone']),
        event.recipes.industrial_colonies.brass_pressing('createappliedkinetics:incomplete_logic_processor', 'createappliedkinetics:incomplete_logic_processor')
      ]).transitionalItem('createappliedkinetics:incomplete_logic_processor').loops(1).id('industrial_colonies:ae2/logic_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Restored prior user-reviewed reference after older Standby duplicate was reviewed: Review revision: Calibrated sensor and populated readout board feed a calculation lane; constantan sensing and shielded power make its kinetic role explicit. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['appliedcreate:advanced_stress_processor'], 'appliedcreate:advanced_stress_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:constantan_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:advanced_stress_circuit_board'}})).loops(1).id('industrial_colonies:electronics/advanced_stress_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Restored prior user-reviewed reference after older Standby duplicate was reviewed: [Mekanized Industry] Upgrade basic control using a completed populated TFMG circuit board, infused-alloy buses and the existing discrete control/shielding stages. Board production remains a recurring upstream demand.
    event.recipes.create.sequenced_assembly(['mekanism:advanced_control_circuit'], 'mekanism:basic_control_circuit', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:basic_control_circuit'}})).loops(1).id('industrial_colonies:mekanism/advanced_control_circuit')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Restored prior user-reviewed reference after older Standby duplicate was reviewed: Review revision: One coated-board calculation print with quartz timing element and constantan traces; reusable press returned, no fluix filler. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.industrial_colonies.brass_compacting(['ae2:printed_calculation_processor'], ['tfmg:coated_circuit_board', 'ae2:certus_quartz_crystal', 'tfmg:p_semiconductor', 'tfmg:constantan_wire', 'ae2:calculation_processor_press']).id('industrial_colonies:ae2/printed_calculation_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Restored prior user-reviewed reference after older Standby duplicate was reviewed: One printed engineering circuit: coated-board foundation, diamond, advanced semiconductor, nickel and magnetic shield; reusable Engineering Press returned. Starter engineering die uses green semiconductor to avoid the approved Brass saw engineering-processor bootstrap cycle; diamond/nickel precision role retained.
    event.recipes.industrial_colonies.brass_compacting(['ae2:printed_engineering_processor'], ['tfmg:coated_circuit_board', 'minecraft:diamond', 'tfmg:p_semiconductor', 'tfmg:nickel_sheet', 'tfmg:magnetic_alloy_sheet', 'ae2:engineering_processor_press']).id('industrial_colonies:ae2/printed_engineering_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Restored prior user-reviewed reference after older Standby duplicate was reviewed: One printed logic circuit: user-authored coated-board foundation supplies gold coating/plastic; one green semiconductor, redstone and copper wire; reusable Logic Press returned. No eight-circuit batch or separate gold sheet.
    event.recipes.industrial_colonies.brass_compacting(['ae2:printed_logic_processor'], ['tfmg:coated_circuit_board', 'tfmg:p_semiconductor', 'minecraft:redstone', 'tfmg:copper_wire', 'ae2:logic_processor_press']).id('industrial_colonies:ae2/printed_logic_processor').merge({heat_requirement: 'lowheated'})
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Restored prior user-reviewed reference after older Standby duplicate was reviewed: Review revision: Approved advanced circuit receives refined die switching, a complete board and reinforced shielded engineering control; industrial rather than quantum. Existing pack items; proposed editor recipe, no gameplay export. Rare-metal tier revision: Platinum microcontacts and one osmium contact portion for refined elite control; basic/advanced controls unchanged.
    event.recipes.create.sequenced_assembly(['mekanism:elite_control_circuit'], 'mekanism:advanced_control_circuit', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:platinum_nugget']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:nugget_osmium']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:advanced_control_circuit'}})).loops(1).id('industrial_colonies:mekanism/elite_control_circuit')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Restored prior user-reviewed reference after older Standby duplicate was reviewed: Review revision: Concurrent execution couples separate scheduling and logic lanes, with printed silicon, advanced switching and a cooled nickel package. Existing pack items; proposed editor recipe, no gameplay export. Rare-metal tier revision: Rare microcontacts for parallel execution interconnect; ordinary AE2 processors unchanged.
    event.recipes.create.sequenced_assembly(['extendedae:concurrent_processor'], 'extendedae:concurrent_processor_print', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:nickel_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:platinum_nugget']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:nugget_osmium']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'extendedae:concurrent_processor_print'}})).loops(1).id('industrial_colonies:extendedae_coverage/concurrent_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Instrumented cell service bay: real housing cradle, engineering diagnostic board, elite configuration control and isolated power. A substantial industrial bench; stabilization-card functionality remains a separate feature. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:cell_workbench', ['AAAAA', 'BCDCB', 'EFGFE', 'HIJIH', 'KLLLK'], {
        A: 'immersiveengineering:plate_electrum',
        B: 'minecraft:glass',
        C: 'tfmg:circuit_board',
        D: 'ae2:item_cell_housing',
        E: 'createaddition:electrum_wire',
        F: 'ae2:calculation_processor',
        G: 'ae2:engineering_processor',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:capacitor_item',
        J: 'mekanism:elite_control_circuit',
        K: 'tfmg:nickel_sheet',
        L: 'tfmg:steel_frame'
      }).id('industrial_colonies:ae2_high_energy/cell_workbench')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Readable screen with paired display elements over addressed logic and a network backplane; relevant terminal electronics instead of loose filler. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:terminal', ['AAAA', 'ABBA', 'CDEC', 'FGGF'], {
        A: 'minecraft:glass',
        B: 'tfmg:segmented_display',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:circuit_board',
        E: 'ae2:logic_processor',
        F: 'tfmg:nickel_sheet',
        G: 'tfmg:steel_frame'
      }).id('industrial_colonies:digital_core/terminal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Requested iron SHEETS explicitly replace every broad plate tag; other starter machinery and conductor quantities retained.
    event.recipes.create.mechanical_crafting('tfmg:electric_motor', [' ABA ', 'ACDCA', 'BDEDB', 'ACFCA', ' ABA '], {
        A: 'create:iron_sheet',
        B: '#c:wires/copper',
        C: 'create:precision_mechanism',
        D: 'create:brass_casing',
        E: 'create:shaft',
        F: 'tfmg:generator'
      }).id('industrial_colonies:early_electricity/electric_motor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Requested copper SHEETS explicitly replace every broad plate tag; other starter machinery and conductor quantities retained.
    event.recipes.create.mechanical_crafting('tfmg:generator', [' ABA ', 'ACDCA', 'BDEDB', 'ACDCA', ' ABA '], {
        A: 'create:copper_sheet',
        B: '#c:wires/copper',
        C: 'create:precision_mechanism',
        D: 'create:brass_casing',
        E: 'create:shaft'
      }).id('industrial_colonies:early_electricity/generator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Battery cube: lithium reservoirs and power tablets in an insulated copper bus with a low monitoring board. A layered energy module rather than a hollow tank shape. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:basic_energy_cube', ['AAAA', 'BCCB', 'ADDA', 'EFFE'], {
        A: 'tfmg:copper_wire',
        B: 'tfmg:rubber_sheet',
        C: 'tfmg:lithium_charge',
        D: 'mekanism:energy_tablet',
        E: 'immersiveengineering:plate_iron',
        F: 'tfmg:circuit_board'
      }).id('industrial_colonies:mekanism/storage/basic_energy_cube')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Ordinary3x3 construction: aluminum cylinder skin around a cast-iron liner/frame, valve gear, seals and fasteners. Requested crafting type; diesel fuel components preserved. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('tfmg:diesel_engine_cylinder', ['ABA', 'CDC', 'EFE'], {
      A: 'tfmg:aluminum_sheet',
      B: 'tfmg:screw',
      C: 'tfmg:cast_iron_sheet',
      D: 'tfmg:cast_iron_frame',
      E: 'tfmg:rubber_sheet',
      F: 'tfmg:steel_mechanism'
    }).id('industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder')
})

ServerEvents.recipes(event => {
  // Review revision: Dedicated early kinetic enclosure with andesite hub, physical shaft and sight windows. Does not consume the expensive digital item-cell housing; late digital cargo gates do not belong here. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('appliedcreate:andesite_stress_cell_housing', ['AAA', 'BCB', 'DED'], {
      A: 'create:andesite_alloy',
      B: 'minecraft:glass',
      C: 'create:andesite_casing',
      D: 'tfmg:rubber_sheet',
      E: 'create:shaft'
    }).id('industrial_colonies:v3_ae2/andesite_stress_cell_housing')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Full5x5 controller cabinet as requested: quantum timing, engineering supervision, ultimate control and heavy structural module fill every slot. No empty outline pretending to be expensive. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('advancedperipherals:chunk_controller', ['ABBBA', 'BCDCB', 'EFGFE', 'HIJIH', 'AKKKA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'create:refined_radiance',
        C: 'tfmg:circuit_board',
        D: 'advanced_ae:quantum_processor',
        E: 'createaddition:electrum_wire',
        F: 'ae2:engineering_processor',
        G: 'mekanism:ultimate_control_circuit',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:heavy_machinery_casing',
        J: 'tfmg:capacitor_item',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:world_loading/chunk_controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Top current-collection strip on a diamond-shaped articulated arm, with two independent lower pivots and steel mounting rail. A pantograph silhouette rather than a square motor. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('electroenergetics:pantograph', ['  A  ', ' B B ', 'B   B', ' C C ', 'DEEED'], {
        A: 'createaddition:electrum_wire',
        B: 'createaddition:iron_rod',
        C: 'create:precision_mechanism',
        D: 'immersiveengineering:plate_steel',
        E: 'tfmg:steel_frame'
      }).id('industrial_colonies:electroenergetics/pantograph')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Small wireless redstone input transmitter, attached by right-clicking an input; matching item-pair frequencies communicate.
    // USES / PROGRESSION / OVERLAP: Installed Ponder specifies128blocks. A control-signal gadget, not an energy cable or inventory teleporter; normal Create control era.
    // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
    // 
    // [Electrical Manufacturing] Convert a paired Redstone Link into a dedicated transmitter with an insulated TFMG lead, copper antenna plate, and directional electron-tube stage
    event.recipes.create.sequenced_assembly(['create_connected:linked_transmitter'], 'create:redstone_link', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:copper_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:electron_tube']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:redstone_link'}})).loops(1).id('industrial_colonies:create_connected/linked_transmitter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Reinforced conductor hub with steel guards, basic logic switching and insulated bus/backing; physically distinct from a heavy high-voltage transformer cabinet. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:steel_cable_hub', [' A ', 'BCB', 'DED', 'FGF'], {
        A: 'createaddition:electrum_wire',
        B: 'tfmg:copper_wire',
        C: 'ae2:logic_processor',
        D: 'immersiveengineering:plate_steel',
        E: 'tfmg:circuit_board',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:steel_frame'
      }).id('industrial_colonies:tfmg_coverage/steel_cable_hub')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Intake matter conversion gate uses quartz coupling and switched logic; complements the formation interface without exotic filler. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['2x ae2:annihilation_core'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:quartz']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:ae2_coverage/annihilation_core_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Formation interface uses addressed matter placement, crystalline coupling and a refined conductor on a physical board. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['2x ae2:formation_core'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:certus_quartz_crystal']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:ae2_coverage/formation_core_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Two steel check valves flank a driven impeller, with a lower mechanical coupling and pressure-supported foot. Short physical pump construction, no unnecessary processor. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:steel_mechanical_pump', [' A ', 'BCB', 'DED', 'FGG'], {
        A: 'tfmg:steel_pipe',
        B: 'tfmg:steel_fluid_valve',
        C: 'tfmg:electric_motor',
        D: 'tfmg:rubber_sheet',
        E: 'tfmg:steel_mechanism',
        F: 'tfmg:nickel_sheet',
        G: 'tfmg:steel_frame'
      }).id('industrial_colonies:fluid_infrastructure/steel_mechanical_pump')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dense addressed fluid storage has engineering supervision, refined controls and dedicated pressure sealing. Existing large-cell housing gate retained; no ingredient ring. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:fluid_storage_cell_16k'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_16k']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:hdpe_sheet']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:v3_ae2/fluid_storage_cell_16k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Actual pattern medium and crafting-program cards sit below a display and calculation encoder, so the ingredients reflect programming crafting patterns. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:pattern_encoding_terminal', ['AAAAA', 'ABBBA', 'CDEDC', 'FGHGF', 'IJJJI'], {
        A: 'minecraft:glass',
        B: 'tfmg:segmented_display',
        C: 'tfmg:circuit_board',
        D: 'ae2:logic_processor',
        E: 'ae2:calculation_processor',
        F: 'createaddition:electrum_wire',
        G: 'ae2:crafting_card',
        H: 'ae2:blank_pattern',
        I: 'tfmg:nickel_sheet',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/pattern_encoding_terminal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Escalating advanced chemical containment reuses the basic vessel, refined infused hardware and advanced process controls. Higher tiers add substantial real structural/control subassemblies; no change to native capacity or transport mechanics. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:advanced_chemical_tank', ['ABBBA', 'CDEDC', 'FGHGF', 'AIIIA'], {
        A: 'tfmg:nickel_sheet',
        B: 'mekanism:alloy_infused',
        C: 'tfmg:heavy_machinery_casing',
        D: 'mekanism:advanced_control_circuit',
        E: 'mekanism:basic_chemical_tank',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'ae2:calculation_processor',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_utility/advanced_chemical_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dense crosshead fabrication bed with actual piston/precision drive modules, paired working surfaces and programmed contraption diagrams. No perimeter ring or decorative arch around an empty center. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('simulated:physics_assembler', ['AABAA', 'CDDDC', 'EEFEE', 'GHGHG', 'IJJJI'], {
        A: 'tfmg:electric_motor',
        B: 'create:mechanical_piston',
        C: 'create:precision_mechanism',
        D: 'create:shaft',
        E: 'tfmg:circuit_board',
        F: 'mekanism:ultimate_control_circuit',
        G: 'rocketnautics:titanium_alloy_sheet',
        H: 'simulated:contraption_diagram',
        I: 'tfmg:heavy_machinery_casing',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:space/construction/physics_assembler')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Projected optical cone rises from amethyst emitters over quantum image processing and buffered control. Distinct optics-and-display layout, not a generic machine with one substituted component. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('rocketnautics:hologram_block', ['  A  ', ' BAB ', 'CDEDC', 'FGHGF', 'IJJJI'], {
        A: 'ae2:quartz_vibrant_glass',
        B: 'minecraft:amethyst_shard',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:circuit_board',
        E: 'advanced_ae:quantum_processor',
        F: 'createaddition:electrum_wire',
        G: 'tfmg:capacitor_item',
        H: 'mekanism:ultimate_control_circuit',
        I: 'rocketnautics:titanium_alloy_sheet',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:space_coverage/hologram_table')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Calorite rocket-construction tank component used by the retained upper Ad Astra rocket tier.
    // USES / PROGRESSION / OVERLAP: Space-tier component, not blanket approval for a giant portable general-purpose tank. Keep only if that rocket route is retained.
    // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
    // 
    // [Planetary Industry] Apply two Calorite thermal shells, a plastic isolation layer, and titanium-alloy service armor to the Ostrum pressure vessel
    event.recipes.create.sequenced_assembly(['ad_astra:calorite_tank'], 'ad_astra:ostrum_tank', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:calorite_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:calorite_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ad_astra:ostrum_tank'}})).loops(1).id('industrial_colonies:space_coverage/calorite_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dense addressed fluid storage has engineering supervision, refined controls and dedicated pressure sealing. Existing large-cell housing gate retained; no ingredient ring. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:fluid_storage_cell_64k'], 'ae2:fluid_cell_housing', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_64k']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:hdpe_sheet']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:fluid_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/fluid_storage_cell_64k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: A network-wide chunk anchor integrates an actual chunk controller with quantum timing and ultimate regulation; expensive electronics/structure serve a real chunk-loading function. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:spatial_anchor', ['ABBBA', 'BCDCB', 'EFGFE', 'HIJIH', 'AKKKA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'create:refined_radiance',
        C: 'tfmg:circuit_board',
        D: 'advanced_ae:quantum_processor',
        E: 'createaddition:electrum_wire',
        F: 'ae2:engineering_processor',
        G: 'mekanism:ultimate_control_circuit',
        H: 'tfmg:rubber_sheet',
        I: 'advancedperipherals:chunk_controller',
        J: 'tfmg:capacitor_item',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/spatial_anchor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('industrial_colonies')) {
    // Review revision: More substantial starter switching package: paired green junctions, resistor-biased gate and insulated copper leads. Four transistors per package, no late pink-substrate bootstrap gate. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['4x tfmg:transistor_item'], 'tfmg:plastic_sheet', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:redstone']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:resistor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:plastic_sheet'}})).loops(1).id('industrial_colonies:electronics/transistor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Raised discharge terminal on a tall paired winding, with insulated base supply and control board. A coil silhouette, not a flat square of electronics. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createaddition:tesla_coil', ['  A  ', ' B B ', 'CBDBC', 'EFGFE', 'CHHHC'], {
        A: 'createaddition:electrum_wire',
        B: 'tfmg:copper_wire',
        C: 'tfmg:nickel_sheet',
        D: 'tfmg:electromagnetic_coil',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'tfmg:capacitor_item',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:createaddition_coverage/tesla_coil')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Raises energy transfer throughput of an Induction Matrix; it is not the cell that stores the energy.
    // USES / PROGRESSION / OVERLAP: High-voltage storage infrastructure. More providers add throughput, while induction cells add capacity.
    // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
    // 
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED.
    // 
    // [High-Energy Grid] Refit the complete Basic Provider as a reinforced switchyard bus: protected Electro Energetics rails meet its steel hub, large regulating coil, Advanced Cube, structural frame, and Advanced control circuit
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('mekanism:advanced_induction_provider', [' ABA ', ' CCC ', 'DEFED', 'GCHCG', ' AIA '], {
        A: 'tfmg:steel_frame',
        B: 'mekanism:advanced_control_circuit',
        C: 'electroenergetics:heavily_insulated_wire',
        D: 'electroenergetics:connector',
        E: 'tfmg:steel_cable_hub',
        F: 'mekanism:basic_induction_provider',
        G: 'mekanism:alloy_reinforced',
        H: 'mekanism:advanced_energy_cube',
        I: 'tfmg:large_coil'
      }).id('industrial_colonies:mekanism/induction/advanced_provider')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Higher-tier Induction Matrix transfer-throughput hardware, distinct from stored energy capacity.
    // USES / PROGRESSION / OVERLAP: Advanced electrical infrastructure after advanced providers; price its conductors/control more heavily than the previous tier.
    // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
    // 
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED.
    // 
    // [High-Energy Grid] Turn the Advanced Provider into an Elite metered switchyard where protected Electro Energetics rails cross current transformers, voltage regulation, and a high-voltage isolator around the Elite Cube and atomic-alloy bus
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('mekanism:elite_induction_provider', [' ABA ', ' CDC ', 'EFGFH', ' DID ', ' AJA '], {
        A: 'tfmg:steel_frame',
        B: 'mekanism:elite_control_circuit',
        C: 'electroenergetics:current_transformer',
        D: 'electroenergetics:heavily_insulated_wire',
        E: 'electroenergetics:voltage_regulator',
        F: 'mekanism:alloy_atomic',
        G: 'mekanism:advanced_induction_provider',
        H: 'electroenergetics:high_voltage_switch',
        I: 'mekanism:elite_energy_cube',
        J: 'tfmg:laminated_magnetic_alloy_block'
      }).id('industrial_colonies:mekanism/induction/elite_provider')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Metal electrode receives copper contact, refractory insulator and suppression resistor. Four service plugs per assembly batch. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['4x tfmg:spark_plug'], 'createaddition:iron_rod', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:copper_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:fireproof_brick']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:resistor']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createaddition:iron_rod'}})).loops(1).id('industrial_colonies:tfmg_coverage/spark_plug')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Quantum reference, ultimate timing and superconducting field coupling inside an atomic-alloy carrier, stabilized by consumed cold blood. Teleporter retention remains undecided; this ingredient does not approve early teleportation. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['mekanism:teleportation_core'], 'mekanism:alloy_atomic', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quantum_entangled_singularity']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_bscco']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'iceandfire:ice_dragon_blood']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:alloy_atomic'}})).loops(1).id('industrial_colonies:mekanism_components/teleportation_core')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Rotational input hardware for TFMG heavy multiblock machines.
    // USES / PROGRESSION / OVERLAP: Used with heavy industrial machinery rather than as a generic item chute. Installed bytecode identity reviewed; exact multiblock connection limits remain native-test work.
    // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
    // 
    // [High-Energy Grid] Fit a heavy multiblock input with its drive shaft, service gear, steel mechanism, and fastener on the Railway assembly line
    event.recipes.create.sequenced_assembly(['tfmg:machine_input'], 'tfmg:heavy_machinery_casing', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_mechanism']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:shaft']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_cogwheel']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:heavy_machinery_casing'}})).loops(1).id('industrial_colonies:tfmg_coverage/machine_input')
  }
})

ServerEvents.recipes(event => {
  // WHAT IT DOES: Transfers HEAT between compatible machines. It does not carry FE or chemical gas.
  // USES / PROGRESSION / OVERLAP: Thermal infrastructure for heat exchangers, heaters and evaporation chains; insulated conductors and transfer rules differ from electrical cables.
  // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
  // 
  // [Mekanized Industry] Jacket a copper thermal path with TFMG cast-iron pipe, grid-grade wire, and infused-alloy junctions
  event.shaped('8x mekanism:basic_thermodynamic_conductor', ['ABA', 'CDC', 'ABA'], {
      A: '#c:plates/copper',
      B: 'tfmg:copper_spool',
      C: 'tfmg:cast_iron_pipe',
      D: 'mekanism:alloy_infused'
    }).id('industrial_colonies:mekanism/transmission/basic_thermodynamic_conductor')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dense addressed item storage has engineering supervision, refined controls and dedicated concurrent memory interconnect. Existing large-cell housing gate retained; no ingredient ring. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:item_storage_cell_256k'], 'ae2:item_cell_housing', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_256k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:item_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/item_storage_cell_256k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Central propeller shaft in a gyroscopic yoke, twin precision pivots and motor/electronic attitude feedback below. Existing gyroscopic parts perform the stabilizing role; no invented navigation module. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('aeronautics:gyroscopic_propeller_bearing', ['  A  ', 'BCCCB', 'DEFED', 'GHIHG', 'JKKKJ'], {
        A: 'create:shaft',
        B: 'simulated:gyroscopic_mechanism',
        C: 'create:propeller',
        D: 'create:precision_mechanism',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:electric_motor',
        G: 'tfmg:circuit_board',
        H: 'ae2:calculation_processor',
        I: 'ae2:engineering_processor',
        J: 'rocketnautics:titanium_alloy_sheet',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:space_coverage/gyroscopic_propeller_bearing')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Three copper conductor branches meet a basic logic-controlled terminal with insulated board backing. Compact early distribution hardware; no expensive full transformer. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('tfmg:copper_cable_hub', ['ABA', 'BCB', 'DED'], {
      A: 'create:copper_sheet',
      B: 'tfmg:copper_wire',
      C: 'ae2:logic_processor',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:early_power_cables/copper_cable_hub')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Upgrade an existing Copper deployer with precision drives, green switching and mechanical position feedback. Prior-tier machine now explicitly carries forward; no AE2/Brass self-production gate. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:brass_deployer', ['  A  ', 'BCCCB', 'DEFED', 'GHIHG', 'J K J'], {
        A: 'tfmg:electric_motor',
        B: 'tfmg:nickel_sheet',
        C: 'create:shaft',
        D: 'tfmg:coated_circuit_board',
        E: 'tfmg:p_semiconductor',
        F: 'tfmg:potentiometer',
        G: 'tfmg:rubber_sheet',
        H: 'create:brass_hand',
        I: 'createcasing:copper_deployer',
        J: 'create:brass_ingot',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:manufacturing/brass_deployer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Build on the existing Copper press, adding green electronic pressure feedback, geared ram and reinforced die bed. Previous machinery remains useful without requiring the processor factory being built. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:brass_press', ['  A  ', 'BCDCB', 'EFGFE', 'H C H', 'HIJIH', 'BKKKB'], {
        A: 'tfmg:electric_motor',
        B: 'tfmg:nickel_sheet',
        C: 'create:shaft',
        D: 'create:large_cogwheel',
        E: 'tfmg:coated_circuit_board',
        F: 'tfmg:potentiometer',
        G: 'tfmg:p_semiconductor',
        H: 'tfmg:heavy_plate',
        I: 'createcasing:copper_press',
        J: 'immersiveengineering:plate_steel',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:manufacturing/brass_press')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Close design retains the real intake core and adds advanced industrial control plus a reinforced addressed switching bus; one useful interface rather than a controller-sized casing. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:import_bus'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:annihilation_core']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:digital_core/import_bus')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Close output design gains refined industrial control and a stronger formation interface, with recurring boards, capacitors and conductors. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:export_bus'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:formation_core']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:ae2_high_energy/export_bus')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dedicated 16k job-planning memory bank uses two matching components, one real crafting CPU, scheduling processors and heat-spreading rails. Crafting workspace remains distinct from portable cargo storage. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:16k_crafting_storage', ['AAAAA', 'BCDCB', 'EFGFE', 'AHHHA'], {
        A: 'tfmg:nickel_sheet',
        B: 'tfmg:circuit_board',
        C: 'ae2:cell_component_16k',
        D: 'ae2:crafting_unit',
        E: 'createaddition:electrum_wire',
        F: 'ae2:calculation_processor',
        G: 'ae2:engineering_processor',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:digital_storage/ae2_crafting_storage_16k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Computer peripheral that stores structured NBT program data; scripts can write/read tables or JSON.
    // USES / PROGRESSION / OVERLAP: ComputerCraft automation data, not stored item cargo or an AE2 cell. Useful for persistent program settings/state.
    // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
    // 
    // [High-Energy Grid] Review correction: functional hardware now uses Mechanical Crafting. The working parts, connections and structural support are assembled in the shown layout; the former sequenced assembly is replaced, not added as an alternative.
    event.recipes.create.mechanical_crafting('advancedperipherals:nbt_storage', [' AA', 'BCD', ' EF'], {
        A: 'advancedperipherals:memory_card',
        B: 'ae2:cell_component_1k',
        C: 'advancedperipherals:peripheral_casing',
        D: 'tfmg:capacitor_item',
        E: 'ae2:calculation_processor',
        F: 'computercraft:wired_modem_full'
      }).id('industrial_colonies:computer_network_coverage/nbt_storage')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Compact3x3 hollow steel vessel with two gauge windows and a valved insulated base; removes the rejected oversized5x5 footprint. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('tfmg:steel_fluid_tank', ['ABA', 'CDC', 'ABA'], {
      A: 'immersiveengineering:plate_steel',
      B: 'tfmg:rubber_sheet',
      C: 'minecraft:glass',
      D: 'tfmg:steel_fluid_valve'
    }).id('industrial_colonies:fluid_infrastructure/steel_fluid_tank')
})

ServerEvents.recipes(event => {
  // Distillation outlet: matched pressure valves and a steel casing, insulated monitoring board and rubber seals. No complete controller consumed for each outlet.
  event.shaped('tfmg:steel_distillation_output', [' A ', 'BCB', 'DED'], {
      A: 'tfmg:steel_pipe',
      B: 'tfmg:steel_fluid_valve',
      C: 'tfmg:steel_casing',
      D: 'tfmg:rubber_sheet',
      E: 'tfmg:circuit_board'
    }).id('industrial_colonies:petroleum/steel_distillation_output')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Sturdy structural plate: form the rare ingot, bond a mekanism:alloy_reinforced reinforcement and rocketnautics:titanium_alloy_sheet backing, trim and finish-press. No screw-only structure and no new item; one plate from one rare ingot plus real support materials.
    event.recipes.create.sequenced_assembly(['allthemodium:allthemodium_plate'], 'allthemodium:allthemodium_ingot', [
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.industrial_iron_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'allthemodium:allthemodium_ingot'}})).loops(1).id('industrial_colonies:plate_assembly/allthemodium')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Sturdy structural plate: form the rare ingot, bond a mekanism:alloy_atomic reinforcement and rocketnautics:titanium_alloy_sheet backing, trim and finish-press. No screw-only structure and no new item; one plate from one rare ingot plus real support materials.
    event.recipes.create.sequenced_assembly(['allthemodium:vibranium_plate'], 'allthemodium:vibranium_ingot', [
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'allthemodium:vibranium_ingot'}})).loops(1).id('industrial_colonies:plate_assembly/vibranium')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Sturdy structural plate: form the rare ingot, bond a mekanism:alloy_atomic reinforcement and createmetallurgy:tungsten_sheet backing, trim and finish-press. No screw-only structure and no new item; one plate from one rare ingot plus real support materials.
    event.recipes.create.sequenced_assembly(['allthemodium:unobtainium_plate'], 'allthemodium:unobtainium_ingot', [
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createmetallurgy:tungsten_sheet']),
        event.recipes.industrial_colonies.refined_radiance_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'allthemodium:unobtainium_ingot'}})).loops(1).id('industrial_colonies:plate_assembly/unobtainium')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Five cell-service fixtures mount above a real drive/backplane and engineering transfer computer; elite routing, buffer and support frame justify a mass-transfer station. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:io_port', ['AAAAA', 'BCDCB', 'EFGFE', 'HIJIH', 'KLLLK'], {
        A: 'ae2:item_cell_housing',
        B: 'minecraft:glass',
        C: 'tfmg:circuit_board',
        D: 'ae2:engineering_processor',
        E: 'createaddition:electrum_wire',
        F: 'ae2:logic_processor',
        G: 'mekanism:elite_control_circuit',
        H: 'tfmg:rubber_sheet',
        I: 'ae2:drive',
        J: 'tfmg:capacitor_item',
        K: 'tfmg:nickel_sheet',
        L: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/io_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Assemble around an actual TFMG engine module with cylinder service hardware, crankshaft, engineering supervision and heavy machinery mounts. Real subassemblies replace the undercosted cylinder-only sequence. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('simulated:engine_assembly', [' ABA ', 'CDEDC', 'BFGFB', 'HIJIH', 'KLLLK'], {
        A: 'tfmg:spark_plug',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:heavy_plate',
        D: 'tfmg:engine_cylinder',
        E: 'tfmg:regular_engine',
        F: 'create:shaft',
        G: 'tfmg:crankshaft',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:circuit_board',
        J: 'ae2:engineering_processor',
        K: 'tfmg:nickel_sheet',
        L: 'tfmg:heavy_machinery_casing'
      }).id('industrial_colonies:simulated/engine_assembly')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dense addressed fluid storage has engineering supervision, refined controls and dedicated pressure sealing. Existing large-cell housing gate retained; no ingredient ring. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:fluid_storage_cell_256k'], 'ae2:fluid_cell_housing', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_256k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:hdpe_sheet']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:fluid_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/fluid_storage_cell_256k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Keep the liked blue-glass optical cover, with a green photovoltaic junction, collector traces and Desh backing. One controlled pass makes two cells; removes the doubled-loop tax. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['2x ad_astra:photovoltaic_etrium_cell'], 'tfmg:silicon_ingot', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:desh_plate']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:blue_stained_glass']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:silicon_ingot'}})).loops(1).id('industrial_colonies:space_hardware/photovoltaic_etrium_cell')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Fully supported hydraulic-style compression bank: twin opposed rows of pressure pistons below a motor/gear crosshead, tungsten guide columns and ultimate process control. No single dangling piston in an empty frame. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:pressurizer', ['ABBBA', 'CDEDC', 'AFFFA', 'AFFFA', 'GHIHG', 'CJJJC'], {
        A: 'tfmg:heavy_plate',
        B: 'tfmg:electric_motor',
        C: 'createmetallurgy:tungsten_sheet',
        D: 'create:shaft',
        E: 'create:large_cogwheel',
        F: 'minecraft:sticky_piston',
        G: 'tfmg:circuit_board',
        H: 'mekanism:ultimate_control_circuit',
        I: 'ae2:engineering_processor',
        J: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/pressurizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Repeatable quantum compute chassis now has an explicit consumed ice-dragon coolant vial between its two processing lanes. It is computation infrastructure, not a portable item cell. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('advanced_ae:quantum_unit', ['AB BA', 'CDEDC', 'FGGGF', 'AHHHA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'advanced_ae:quantum_processor',
        C: 'createaddition:electrum_wire',
        D: 'tfmg:circuit_board',
        E: 'iceandfire:ice_dragon_blood',
        F: 'tfmg:rubber_sheet',
        G: 'ae2:calculation_processor',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/quantum_unit')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Field-column segments define the physical region swapped by AE2 spatial IO.
    // USES / PROGRESSION / OVERLAP: Late spatial-transfer infrastructure, not decorative pillars or normal storage cells. Transport bypasses and complete enclosure cost require separate review.
    // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
    // 
    // Deferred re-review: Field-column segments define the physical region used by spatial IO.
    // 
    // Review revision: Repeatable field-column segment: aligned optical face, quantum-alloy backing, superconducting field windings and engineering synchronization; eight segments per precision batch. The overall enclosure remains costly. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['8x ae2:spatial_pylon'], 'tfmg:steel_frame', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_bscco']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_frame'}})).loops(1).id('industrial_colonies:v3_ae2/spatial_pylon_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: One narrow saw on an aligned spindle with twin precision lead-screw feeds and a capacitor-controlled motor stage. Iron guide rods and copper instrumentation make this a precise saw without post-Copper semiconductors. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:copper_mechanical_saw', ['  A  ', 'BCDCB', 'EFGFE', 'HICIH', 'BJJJB'], {
        A: 'create:mechanical_saw',
        B: 'tfmg:nickel_sheet',
        C: 'create:precision_mechanism',
        D: 'create:shaft',
        E: 'create:copper_casing',
        F: 'tfmg:copper_wire',
        G: 'createaddition:capacitor',
        H: 'tfmg:rubber_sheet',
        I: 'createaddition:iron_rod',
        J: 'tfmg:cast_iron_frame'
      }).id('industrial_colonies:manufacturing/copper/saw')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Three resistive heating strips between refractory fins, with insulated power contacts and thermal calculation control below. No motor, combustion cylinder or cryogenic components. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:resistive_heater', ['ABABA', 'CDCDC', 'EFGFE', 'EHHHE'], {
        A: 'tfmg:fireproof_bricks',
        B: 'tfmg:constantan_wire',
        C: 'tfmg:rubber_sheet',
        D: 'mekanism:alloy_infused',
        E: 'tfmg:nickel_sheet',
        F: 'tfmg:circuit_board',
        G: 'ae2:calculation_processor',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_utility/resistive_heater')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Food hopper and paired blending heads feed a sealed nutritional reservoir, with simple metering below; unrelated to nuclear dissolution or ore chemistry. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:nutritional_liquifier', ['  A  ', 'BCDCB', 'EF FE', 'GHIHG', 'BJJJB'], {
        A: 'minecraft:hopper',
        B: 'tfmg:nickel_sheet',
        C: 'create:mechanical_mixer',
        D: 'create:shaft',
        E: 'tfmg:steel_pipe',
        F: 'mekanism:basic_chemical_tank',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:circuit_board',
        I: 'ae2:logic_processor',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:planetary/outpost/nutritional_liquifier')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dedicated 256k job-planning memory bank uses two matching components, one real crafting CPU, scheduling processors and heat-spreading rails. Crafting workspace remains distinct from portable cargo storage. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:256k_crafting_storage', ['AAAAA', 'BCDCB', 'EFGFE', 'AHHHA'], {
        A: 'tfmg:nickel_sheet',
        B: 'tfmg:circuit_board',
        C: 'ae2:cell_component_256k',
        D: 'ae2:crafting_unit',
        E: 'createaddition:electrum_wire',
        F: 'ae2:calculation_processor',
        G: 'ae2:engineering_processor',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:digital_storage/ae2_crafting_storage_256k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Dedicated 64k job-planning memory bank uses two matching components, one real crafting CPU, scheduling processors and heat-spreading rails. Crafting workspace remains distinct from portable cargo storage. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:64k_crafting_storage', ['AAAAA', 'BCDCB', 'EFGFE', 'AHHHA'], {
        A: 'tfmg:nickel_sheet',
        B: 'tfmg:circuit_board',
        C: 'ae2:cell_component_64k',
        D: 'ae2:crafting_unit',
        E: 'createaddition:electrum_wire',
        F: 'ae2:calculation_processor',
        G: 'ae2:engineering_processor',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:digital_storage/ae2_crafting_storage_64k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: A real mega memory bank mounts inside its already-expensive containment shell, with quantum addressing, parallel control and superconducting interconnect. No alternate cheap shell route. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:item_storage_cell_16m'], 'megacells:mega_item_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_16m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_bscco']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:vibranium_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_item_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_item_storage_cell_16m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: A real mega memory bank mounts inside its already-expensive containment shell, with quantum addressing, parallel control and superconducting interconnect. No alternate cheap shell route. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:item_storage_cell_1m'], 'megacells:mega_item_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_1m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_bscco']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:vibranium_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_item_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_item_storage_cell_1m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Heavy motor head and reduction gear drive paired mixing shafts over a low structural bed. Train-tier current/process controls flank the gearbox; actual whisks occupy the working end. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:railway_mixer', ['  A  ', 'BCDCB', ' EFE ', 'GHCHG', 'BE EB', ' I I '], {
        A: 'tfmg:electric_motor',
        B: 'tfmg:nickel_sheet',
        C: 'tfmg:steel_frame',
        D: 'create:large_cogwheel',
        E: 'create:shaft',
        F: 'ae2:engineering_processor',
        G: 'immersiveengineering:plate_steel',
        H: 'mekanism:advanced_control_circuit',
        I: 'create:whisk'
      }).id('industrial_colonies:manufacturing/railway/mixer')
  }
})

ServerEvents.recipes(event => {
  // Review revision: Small cast-iron tank assembled at the normal crafting table from a barrel core and four protective sheets. No mechanical-crafter-only gate. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('tfmg:cast_iron_fluid_tank', [' A ', 'ABA', ' A '], {
      A: 'tfmg:cast_iron_sheet',
      B: 'minecraft:barrel'
    }).id('industrial_colonies:ownership/cast_iron_fluid_tank')
})

ServerEvents.recipes(event => {
  // Review revision: Lever and sealed cast-iron saddle form a manually operated valve over the matching pipe. Simple physical hardware, not an electronic controller. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('tfmg:cast_iron_fluid_valve', [' A ', 'BCB', ' D '], {
      A: 'minecraft:lever',
      B: 'tfmg:cast_iron_sheet',
      C: 'tfmg:rubber_sheet',
      D: 'tfmg:cast_iron_pipe'
    }).id('industrial_colonies:ownership/cast_iron_fluid_valve')
})

ServerEvents.recipes(event => {
  // Review revision: Two folded sidewalls define an open bore; ordinary crafting produces six cast-iron pipe sections. No unrelated cast-iron ingot left inside the flow channel. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('6x tfmg:cast_iron_pipe', ['ABA'], {
      A: 'tfmg:cast_iron_sheet',
      B: 'tfmg:cast_iron_ingot'
    }).id('industrial_colonies:ownership/cast_iron_pipe')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Wide job-progress display with an accumulation/readout processor, scheduling logic and buffered control. A monitor for large crafting jobs, not another mega storage shell. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('megacells:mega_crafting_monitor', ['AAAAA', 'ABBBA', 'CDEDC', 'FGHGF', 'BIIIB'], {
        A: 'minecraft:glass',
        B: 'tfmg:segmented_display',
        C: 'tfmg:circuit_board',
        D: 'ae2:calculation_processor',
        E: 'ae2:logic_processor',
        F: 'createaddition:electrum_wire',
        G: 'tfmg:capacitor_item',
        H: 'megacells:accumulation_processor',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/mega_crafting_monitor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Direct nine-stage adaptation of Personal cast-iron-frame reference: cut sheet-metal blank, fit two steel stock pieces, form, add rebar, trim, add steel rod, press and heat-finish. One steel frame; no three-step rebar shortcut. Uses the same basic Create capability as the ungated Personal reference: approved Weathered machines themselves require this frame, so requiring those machines here would be a bootstrap cycle. Personal reference unchanged.
    event.recipes.create.sequenced_assembly(['tfmg:steel_frame'], 'immersiveengineering:sheetmetal_steel', [
        event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece').merge({processing_time: 20}),
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ingot_steel']),
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ingot_steel']),
        event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rebar']),
        event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece').merge({processing_time: 20}),
        event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'immersiveengineering:stick_steel']),
        event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.custom({type: 'industrial_colonies:assembly_blasting', ingredients: [{item: 'industrial_colonies:assembly_workpiece'}], results: [{id: 'industrial_colonies:assembly_workpiece'}], processing_time: 100})
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'immersiveengineering:sheetmetal_steel'}})).loops(1).id('industrial_colonies:ownership/steel_frame')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: A real rotational sensing module, calibration bridge and buffered readout on the approved stress board. Mechanical load sensing, not another generic AE2 silicon processor. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_processor'], 'appliedcreate:stress_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:speedometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:constantan_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:potentiometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:resistor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'appliedcreate:stress_circuit_board'}})).loops(1).id('industrial_colonies:electronics/stress_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Fourth October15 review: Review revision: Parallel bank controller and independent address logic multiplex four prior packages; constantan sensing and magnetic shielding provide a different manufacturing stage. Proposed for massive crafting computers. Portable item/fluid-cell access is NOT approved or restricted by this card; transport-preserving route policy remains open. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:cell_component_4m'], 'megacells:cell_component_1m', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_1m']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_1m']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_1m']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:constantan_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:cell_component_1m'}})).loops(1).id('industrial_colonies:v3_ae2/mega_cell_component_4m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Fourth October15 review: Review revision: Paired memory-address controllers and an elite refresh controller drive sixteen-megabyte density, with switched refresh and nickel heat spreading. Proposed for massive crafting computers. Portable item/fluid-cell access is NOT approved or restricted by this card; transport-preserving route policy remains open. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:cell_component_16m'], 'megacells:cell_component_4m', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_4m']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_4m']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_4m']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:accumulation_processor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:accumulation_processor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:nickel_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:platinum_plate']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:cell_component_4m'}})).loops(1).id('industrial_colonies:v3_ae2/mega_cell_component_16m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Fourth October15 review: Review revision: Quantum timing and superconducting readout coordinate four large banks inside a titanium isolated enclosure; prior-tier manufacture remains necessary. Proposed for massive crafting computers. Portable item/fluid-cell access is NOT approved or restricted by this card; transport-preserving route policy remains open. Existing pack items; proposed editor recipe, no gameplay export. Existing items only; proposed editor card, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:cell_component_64m'], 'megacells:cell_component_16m', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_16m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_16m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_16m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_bscco']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:osmiridium_ingot']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:cell_component_16m'}})).loops(1).id('industrial_colonies:v3_ae2/mega_cell_component_64m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [High-Energy Grid] Build the kinetic-to-ME conversion cabinet around a canonical TFMG generator and an existing AE energy interface
    event.recipes.create.mechanical_crafting('appliedcreate:kinetic_energy_acceptor', ['ABCBA', 'BDEDB', 'CFGFC', 'BDHIB', 'ABCBA'], {
        A: 'tfmg:steel_mechanism',
        B: 'create:brass_casing',
        C: 'appliedcreate:stress_processor',
        D: 'tfmg:copper_wire',
        E: 'ae2:fluix_glass_cable',
        F: 'tfmg:generator',
        G: 'ae2:energy_acceptor',
        H: 'mekanism:advanced_control_circuit',
        I: 'tfmg:electric_motor'
      }).id('industrial_colonies:appliedcreate/kinetic_energy_acceptor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Requested5x4 handheld enclosure: display band, engineering board, battery pack and thin aluminum lower shell; no heavy steel frames in a pocket computer. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('computercraft:pocket_computer_advanced', ['ABBBA', 'CDEDC', 'FGGGF', 'HIIIH'], {
        A: 'minecraft:glass',
        B: 'tfmg:segmented_display',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:circuit_board',
        E: 'ae2:engineering_processor',
        F: 'createaddition:electrum_wire',
        G: 'mekanism:energy_tablet',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:aluminum_sheet'
      }).id('industrial_colonies:computercraft/mobile/advanced_pocket_upgrade')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Chemical hardware first: four ultimate chemical containment vessels, a rotary phase-conversion module, chemical infuser and paired electrochemical interfaces within an HDPE liner. Ultimate interlocks and osmiridium pressure supports; no unrelated quantum processor substituted for chemistry. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('appmek:chemical_cell_housing', ['ABBBA', 'BCDCB', 'CEFEC', 'BGHGB', 'AIJIA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'mekanism:hdpe_sheet',
        C: 'mekanism:ultimate_chemical_tank',
        D: 'mekanism:chemical_infuser',
        E: 'mekanism:rotary_condensentrator',
        F: 'mekanism:ultimate_control_circuit',
        G: 'mekanism:electrolytic_core',
        H: 'tfmg:circuit_board',
        I: 'nuclearcraft:osmiridium_ingot',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:digital_core/chemical_cell_housing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [High-Energy Grid] Laminate High-Voltage insulated conductor in canonical TFMG rubber and plastic.
    event.recipes.industrial_colonies.railway_compacting(['4x electroenergetics:heavily_insulated_wire'], ['electroenergetics:insulated_wire', 'electroenergetics:insulated_wire', 'electroenergetics:insulated_wire', 'electroenergetics:insulated_wire', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:rubber_sheet', 'tfmg:plastic_sheet']).id('industrial_colonies:extreme_grid/heavily_insulated_wire')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [High-Energy Grid] Wind the protected conductor onto reinforced grid-spool hardware.
    event.recipes.industrial_colonies.railway_compacting(['electroenergetics:heavily_insulated_wire_spool'], ['electroenergetics:empty_spool', 'electroenergetics:heavily_insulated_wire', 'electroenergetics:heavily_insulated_wire', 'electroenergetics:heavily_insulated_wire', 'electroenergetics:heavily_insulated_wire', 'tfmg:steel_mechanism']).id('industrial_colonies:extreme_grid/heavily_insulated_wire_spool')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Heavy offset crank on a continuous shaft, reinforced connecting rod, steel bearing housings and four structural frames. A steel mechanism and precision governor replace the undercosted loose cog/rod construction. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:pumpjack_crank', ['  A  ', 'BCCCD', '  E  ', ' FGF ', 'HGGGH'], {
        A: 'tfmg:heavy_plate',
        B: 'tfmg:steel_mechanism',
        C: 'create:shaft',
        D: 'create:precision_mechanism',
        E: 'tfmg:rebar',
        F: 'tfmg:steel_casing',
        G: 'tfmg:steel_frame',
        H: 'tfmg:nickel_sheet'
      }).id('industrial_colonies:machine/oil_processing/pumpjack_crank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Precision instrumented work pedestal upgrades the copper depot with optical work detection, green switching, buffered power and alignment mechanism. Completed boards and substantial steel supports replace the thin casing-only retrofit; avoids AE2 processor bootstrap dependencies. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:brass_depot', ['  A  ', 'BCCCB', 'DEFED', 'GHIHG', 'JKKKJ'], {
        A: 'create:content_observer',
        B: 'tfmg:nickel_sheet',
        C: 'create:brass_casing',
        D: 'tfmg:circuit_board',
        E: 'tfmg:transistor_item',
        F: 'create:precision_mechanism',
        G: 'tfmg:rubber_sheet',
        H: 'createaddition:capacitor',
        I: 'createcasing:copper_depot',
        J: 'create:brass_ingot',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:manufacturing/brass/depot')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [Digital Logistics] Build the liquid-fuel burner as an ignited steel feed over a TFMG firebox, enclosed by refractory brick and a heavy base
    event.recipes.create.mechanical_crafting('createdieselgenerators:burner', ['ABA', 'CDC', 'EFE'], {
        A: 'tfmg:fireproof_bricks',
        B: 'tfmg:spark_plug',
        C: 'tfmg:steel_pipe',
        D: 'create:empty_blaze_burner',
        E: 'tfmg:heavy_plate',
        F: 'tfmg:firebox'
      }).id('industrial_colonies:diesel_generators_coverage/burner')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Review revision: Direct small fluid cell assembly with independent memory and sealing. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:fluid_storage_cell_1k'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_glass']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:v3_ae2/fluid_storage_cell_1k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Review revision: A readable channel-monitor module and logic/controller board are fitted to a basic cable, instead of duplicating a default cable recipe. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['4x ae2:fluix_smart_cable'], 'ae2:fluix_glass_cable', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:segmented_display']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:fluix_glass_cable'}})).loops(1).id('industrial_colonies:v3_ae2/fluix_smart_cable_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Four advanced vessels form a pressure-isolated elite bank. Fourfold recursive vessel demand replaces the previous1:1 upgrade, plus refined reinforcement and elite safety control. Native capacity is unchanged; cost recursion, not a claimed capacity modification. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:elite_chemical_tank', ['ABBBA', 'CDCDC', 'BCECB', 'FEGEF', 'AHHHA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'mekanism:hdpe_sheet',
        C: 'mekanism:advanced_chemical_tank',
        D: 'mekanism:alloy_reinforced',
        E: 'mekanism:elite_control_circuit',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_utility/elite_chemical_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Eight elite vessels, each requiring four advanced vessels:32advanced-vessel equivalents before atomic reinforcement, superconducting-tier digital supervision, six ultimate interlocks, osmiridium anchors and titanium pressure skin. A much steeper recursive infrastructure investment; capacity unchanged. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:ultimate_chemical_tank', ['ABBBBBA', 'CDEDEDC', 'BEFFFEB', 'CDEGEDC', 'BEFFFEB', 'CDEDEDC', 'AHHHHHA'], {
        A: 'nuclearcraft:osmiridium_ingot',
        B: 'rocketnautics:titanium_alloy_sheet',
        C: 'mekanism:hdpe_sheet',
        D: 'mekanism:elite_chemical_tank',
        E: 'mekanism:alloy_atomic',
        F: 'mekanism:ultimate_control_circuit',
        G: 'advanced_ae:quantum_processor',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_utility/ultimate_chemical_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [High-Energy Grid] Calibrate a late spatial anchor around a teleportation core, AE spatial lattice, magnetic alloy, and engineering governor.
    event.recipes.create.sequenced_assembly(['mekanism:upgrade_anchor'], 'mekanism:advanced_control_circuit', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:teleportation_core']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:spatial_pylon']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_ingot']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:advanced_control_circuit'}})).loops(1).id('industrial_colonies:mekanism/upgrade/anchor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [Orbital Engineering] Build the navigation workstation as a twin-monitor console over distinct optical, velocity, and gimbal channels, with one computer, ultimate and engineering control, TFMG backplanes, and a heavy bench base
    event.recipes.create.mechanical_crafting('simulated:navigation_table', [' A A ', 'B C B', 'DEFGD', 'BHIHB', 'JJJJJ'], {
        A: 'computercraft:monitor_advanced',
        B: 'tfmg:steel_frame',
        C: 'computercraft:computer_advanced',
        D: 'tfmg:circuit_board',
        E: 'simulated:optical_sensor',
        F: 'simulated:velocity_sensor',
        G: 'simulated:gimbal_sensor',
        H: 'mekanism:ultimate_control_circuit',
        I: 'ae2:engineering_processor',
        J: 'tfmg:heavy_plate'
      }).id('industrial_colonies:space/navigation/navigation_table')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [Orbital Engineering] Seal two redundant staging charges in plastic, titanium, and electrically supervised energetic cartridges
    event.recipes.industrial_colonies.refined_radiance_compacting(['2x rocketnautics:separator_charge'], ['minecraft:gunpowder', 'minecraft:gunpowder', 'minecraft:gunpowder', 'minecraft:gunpowder', 'tfmg:plastic_sheet', 'tfmg:plastic_sheet', 'tfmg:copper_wire', 'mekanism:advanced_control_circuit', 'rocketnautics:titanium_alloy_sheet']).id('industrial_colonies:space_coverage/separator_charge')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [High-Energy Grid] Pressure-form a matched piston pair from aluminum crowns, a cast-iron skirt, shaft stock, and one service fastener
    event.recipes.industrial_colonies.industrial_iron_compacting(['2x createdieselgenerators:engine_piston'], ['tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:cast_iron_sheet', 'create:shaft', 'tfmg:screw']).id('industrial_colonies:diesel_generators_coverage/engine_piston')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Review revision: Direct small item cell assembly with independent memory and sealing. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:item_storage_cell_4k'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_4k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_glass']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:v3_ae2/item_storage_cell_4k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Review revision: Direct small fluid cell assembly with independent memory and sealing. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:fluid_storage_cell_4k'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_4k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_glass']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:v3_ae2/fluid_storage_cell_4k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Review revision: Four pressure cylinders on a long crank bed, twin fuel pumps and top manifolds, with a low governed control panel. Distinct heavy compression-engine geometry. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createdieselgenerators:large_diesel_engine', [' AAAA ', 'BCBBCB', 'BCBBCB', 'DEEEED', 'FGHGGF', 'BIIIIB'], {
        A: 'tfmg:steel_pipe',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:diesel_engine_cylinder',
        D: 'tfmg:electric_pump',
        E: 'create:shaft',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'ae2:engineering_processor',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:engines/large_diesel_engine')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Wireless terminal access now requires a substantial RF coil, dual concurrent controllers, atomic signal shielding and elite supervision, plus two receiver modules and titanium supports. Costlier digital radio hardware without conflating ordinary local wireless access with the terminal-game ExtendedAE bridge. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:wireless_access_point', ['  A  ', ' BCB ', 'DEFED', 'GHIHG', 'JKKKJ'], {
        A: 'computercraft:wireless_modem_advanced',
        B: 'createaddition:electrum_wire',
        C: 'tfmg:large_coil',
        D: 'mekanism:alloy_atomic',
        E: 'extendedae:concurrent_processor',
        F: 'tfmg:circuit_board',
        G: 'tfmg:rubber_sheet',
        H: 'ae2:wireless_receiver',
        I: 'mekanism:elite_control_circuit',
        J: 'rocketnautics:titanium_alloy_sheet',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:ae2_coverage/wireless_access_point')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [Digital Logistics] Balance a precision rotor with paired magnetic bearings, a compass reference, Brass trim, and a sprung Railway mount
    event.recipes.create.sequenced_assembly(['simulated:gyroscopic_mechanism'], 'create:precision_mechanism', [
        event.recipes.industrial_colonies.railway_deploying('simulated:incomplete_gyroscopic_mechanism', ['simulated:incomplete_gyroscopic_mechanism', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('simulated:incomplete_gyroscopic_mechanism', ['simulated:incomplete_gyroscopic_mechanism', 'minecraft:compass']),
        event.recipes.industrial_colonies.railway_deploying('simulated:incomplete_gyroscopic_mechanism', ['simulated:incomplete_gyroscopic_mechanism', 'create:brass_sheet']),
        event.recipes.industrial_colonies.railway_deploying('simulated:incomplete_gyroscopic_mechanism', ['simulated:incomplete_gyroscopic_mechanism', 'simulated:spring']),
        event.recipes.industrial_colonies.railway_deploying('simulated:incomplete_gyroscopic_mechanism', ['simulated:incomplete_gyroscopic_mechanism', 'tfmg:steel_frame']),
        event.recipes.industrial_colonies.railway_deploying('simulated:incomplete_gyroscopic_mechanism', ['simulated:incomplete_gyroscopic_mechanism', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.railway_deploying('simulated:incomplete_gyroscopic_mechanism', ['simulated:incomplete_gyroscopic_mechanism', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_pressing('simulated:incomplete_gyroscopic_mechanism', 'simulated:incomplete_gyroscopic_mechanism')
      ]).transitionalItem('simulated:incomplete_gyroscopic_mechanism').loops(2).id('industrial_colonies:simulated/gyroscopic_mechanism')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Preserve the approved fan silhouette. Late electronic package now uses two elite controls, concurrent motor regulation and titanium bearing/support rails; working impeller and shaft geometry unchanged.
    event.recipes.create.mechanical_crafting('createcasing:railway_encased_fan', [' AAA ', 'BBCBB', 'DEFED', 'GHIHG', 'DJJJD'], {
        A: 'minecraft:iron_bars',
        B: 'immersiveengineering:plate_steel',
        C: 'create:propeller',
        D: 'rocketnautics:titanium_alloy_sheet',
        E: 'create:shaft',
        F: 'tfmg:electric_motor',
        G: 'tfmg:circuit_board',
        H: 'mekanism:elite_control_circuit',
        I: 'extendedae:concurrent_processor',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:manufacturing/railway/fan')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Deferred re-review: Large gas-supply infrastructure; capacity and mobility still need the transport-policy audit.
    // 
    // [Orbital Engineering] Stack two tested gas tanks in a heavy pressure tower: a steel valve and smart manifold join the vessels, plastic standoffs isolate them, and a coated TFMG board plus capacitor supervise the ultimate chemical-tank base
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('ad_astra:large_gas_tank', ['  A  ', ' BCB ', 'BDEDB', 'B E B', 'FGHIF'], {
        A: 'tfmg:steel_fluid_valve',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:steel_smart_fluid_pipe',
        D: 'tfmg:plastic_sheet',
        E: 'ad_astra:gas_tank',
        F: 'tfmg:steel_frame',
        G: 'tfmg:coated_circuit_board',
        H: 'mekanism:ultimate_chemical_tank',
        I: 'tfmg:capacitor_item'
      }).id('industrial_colonies:space/life_support/large_gas_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Review revision: Central seed chamber fed from one solution reservoir, separated side circulation and precision pumps, visible growth windows and a low control cabinet. A crystallizer fluid path, not an electrolyzer copy. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:crystallizer', ['  A  ', 'BCDCB', 'AC CA', 'EFGFE', 'EHHHE'], {
        A: 'tfmg:steel_pipe',
        B: 'minecraft:glass',
        C: 'tfmg:steel_chemical_vat',
        D: 'mekanism:basic_chemical_tank',
        E: 'tfmg:nickel_sheet',
        F: 'tfmg:electric_pump',
        G: 'ae2:engineering_processor',
        H: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/crystallizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Review clarification: powered footwear provides step assistance and fall protection while charged, with armor protection in this version. It is mobility equipment, not production machinery. Ingredients retained for a second review.
    event.recipes.create.mechanical_crafting('mekanism:free_runners_armored', ['A   A', 'B   B', 'C D C', 'E   E', 'F   F'], {
        A: 'modernfoundry:cobalt_ingot',
        B: 'tfmg:heavy_plate',
        C: 'mekanism:alloy_atomic',
        D: 'mekanism:free_runners',
        E: 'minecraft:diamond',
        F: 'tfmg:rubber_sheet'
      }).id('industrial_colonies:mekanism_tools/armored_free_runners')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [Orbital Engineering] Review correction: dual communications arrays feed dedicated navigation boards and an onboard computer, with insulated wiring and structural support.
    event.recipes.create.mechanical_crafting('rocketnautics:sputnik', [' A A ', 'BCDCB', ' EFE ', ' GHG '], {
        A: 'create:transmitter',
        B: 'tfmg:heavy_plate',
        C: 'tfmg:coated_circuit_board',
        D: 'ae2:calculation_processor',
        E: 'tfmg:copper_wire',
        F: 'computercraft:computer_advanced',
        G: 'tfmg:plastic_sheet',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:space/navigation/sputnik')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: The installed mod tooltip calls this a proxy for accessing an AE2 network item/fluid inventory. It provides a physical inventory interface for external logistics connected to the network.
    // USES / OVERLAP: Useful at a factory transfer boundary; compare with AE2 interfaces/storage buses and keep only if its integration adds value. This is inventory access, not extra storage capacity. Exact sided/rate behavior is not qualified here.
    // PROGRESSION: After a working AE2 network; no early alternative to the network itself. Recipe unchanged for this explanation.
    // 
    // Review revision: Bridge interface in an insulated peripheral chassis with elite/engineering routing control and dense links. Native proxy behavior is unchanged; off-ship access is not granted by this construction. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('createappliedkinetics:me_proxy', ['ABBBA', 'CDEDC', 'FGHGF', 'IJJJI'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'createaddition:electrum_wire',
        C: 'tfmg:circuit_board',
        D: 'mekanism:elite_control_circuit',
        E: 'ae2:engineering_processor',
        F: 'tfmg:rubber_sheet',
        G: 'advancedperipherals:peripheral_casing',
        H: 'ae2:interface',
        I: 'tfmg:nickel_sheet',
        J: 'tfmg:steel_frame'
      }).id('industrial_colonies:createappliedkinetics/me_proxy')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Repair accidental first-step edit: restore the ME P2P addressing tunnel and its deploying step; retain the existing reviewed gearbox, advanced stress processing and other physical components.
    event.recipes.create.sequenced_assembly(['appliedcreate:me_gearbox'], 'create:gearbox', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:me_p2p_tunnel']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_dense_cable']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_frame']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:railway_casing']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:gearbox'}})).loops(1).id('industrial_colonies:appliedcreate/me_gearbox')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // Review revision: Paired electrum endpoints and two engineering interfaces around a shielded channel junction; a routing subassembly rather than an item warehouse. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:me_p2p_tunnel', [' A A ', 'BCBCB', 'DEFED', 'GHHHG'], {
        A: 'createaddition:electrum_wire',
        B: 'tfmg:rubber_sheet',
        C: 'ae2:engineering_processor',
        D: 'ae2:fluix_glass_cable',
        E: 'tfmg:circuit_board',
        F: 'tfmg:heavy_machinery_casing',
        G: 'tfmg:nickel_sheet',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:ae2_high_energy/me_p2p_tunnel')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [Digital Logistics] Convert the Copper fan into a populated Brass precision tool with serviceable drive and role-specific control.
    event.recipes.create.sequenced_assembly(['createcasing:brass_encased_fan'], 'createcasing:copper_encased_fan', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:brass_casing']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createcasing:copper_encased_fan'}})).loops(1).id('industrial_colonies:manufacturing/brass/fan')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: A substantial iron charging column on a cast-iron frame foundation. Copper electrode jaws flank the visible quartz charging bay; capacitor and addressed control below. Added actual load-bearing frame/casing cost, no quantum filler. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:charger', [' ABA ', 'A C A', 'ADCDA', 'EFGFE', 'HIIIH'], {
        A: 'immersiveengineering:plate_iron',
        B: 'createaddition:capacitor',
        C: 'tfmg:copper_wire',
        D: 'ae2:quartz_glass',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'ae2:logic_processor',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:cast_iron_frame'
      }).id('industrial_colonies:ae2/charger')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: An enhanced husbandry automata turtle upgrade for animal-related automation.
    // USES / PROGRESSION / OVERLAP: Specialized programmable farming, not an industrial material processor. Enhanced abilities need separate cost/automation balance; not required for basic electronics.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED.
    // 
    // [High-Energy Grid] Upgrade the earned husbandry core with star power, a gentle mechanical manipulator, electric drive, feed recognizer, biological control board, and a buffered actuator supply
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['advancedperipherals:overpowered_husbandry_automata_core'], 'advancedperipherals:husbandry_automata_core', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:nether_star']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:mechanical_arm']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:golden_carrot']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'advancedperipherals:husbandry_automata_core'}})).loops(1).id('industrial_colonies:computer_network_coverage/overpowered_husbandry_automata_core')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: A turtle upgrade that enables the mod metaphysics/automata abilities; it is the starter automata core rather than a general CPU.
    // USES / PROGRESSION / OVERLAP: Optional programmable-turtle progression. Keep only if those turtle abilities fit the automation plan; not a mandatory board for every machine.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED. Installed text: Does the afterlife exist in minecraft?
    // 
    // [High-Energy Grid] Assemble the first turtle automata core from a mechanical arm, electric drive, soul lantern, brewing interface, controller board, and precision motion package
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['advancedperipherals:weak_automata_core'], 'advancedperipherals:peripheral_casing', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:mechanical_arm']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:soul_lantern']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:brewing_stand']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'advancedperipherals:peripheral_casing'}})).loops(1).id('industrial_colonies:computer_network_coverage/weak_automata_core')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Two dedicated chemical fuel reservoirs sit above paired thrusters. Gyroscopic reference and calculation control stabilize thrust; ultimate interlock meters supply. Retains the requested late-space Ostrum/suit gate and titanium harness. These are construction ingredients; this edit does not change native hydrogen capacity or flight control. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:jetpack', [' ABA ', 'CDEDC', 'FGHGF', 'IJKJI', 'LMMML'], {
        A: 'tfmg:rubber_sheet',
        B: 'tfmg:circuit_board',
        C: 'rocketnautics:titanium_alloy_sheet',
        D: 'ad_astra:ostrum_plate',
        E: 'mekanism:ultimate_control_circuit',
        F: 'mekanism:hdpe_sheet',
        G: 'mekanism:advanced_chemical_tank',
        H: 'ad_astra:space_suit',
        I: 'rocketnautics:copper_leg_thrusters',
        J: 'simulated:gyroscopic_mechanism',
        K: 'ae2:calculation_processor',
        L: 'mekanism:alloy_atomic',
        M: 'tfmg:steel_frame'
      }).id('industrial_colonies:mekanism_tools/jetpack')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Item-routing segment that gives its route a high path cost so other available routes are preferred.
    // USES / PROGRESSION / OVERLAP: Useful overflow/fallback routing. It is not a filter or a bigger inventory; compare with Create overflow logistics.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Less-preferred routing segment in logistical transporter networks.
    // 
    // Review revision: Add routing-resistance control to the ordinary transporter, making this a routing choice rather than a new unlimited-range tier. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['2x mekanism:restrictive_transporter'], 'mekanism:basic_logistical_transporter', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:repeater']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:resistor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:basic_logistical_transporter'}})).loops(1).id('industrial_colonies:mekanism_utility/restrictive_transporter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Reposition to advanced nuclear digital networking, below terminal quantum/exotic storage: paired concurrent routers, native wireless connector, dense buffer, ultimate supervision and Radiance RF supports. Removed quantum core, Vibranium and Unobtainium overgate; still more costly than the local access point. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('extendedae:wireless_hub', ['  A  ', ' BCB ', 'DEFED', 'GHIHG', 'JKKKJ'], {
        A: 'computercraft:wireless_modem_advanced',
        B: 'createaddition:electrum_wire',
        C: 'tfmg:large_coil',
        D: 'create:refined_radiance',
        E: 'extendedae:concurrent_processor',
        F: 'mekanism:ultimate_control_circuit',
        G: 'tfmg:rubber_sheet',
        H: 'extendedae:wireless_connect',
        I: 'ae2:dense_energy_cell',
        J: 'rocketnautics:titanium_alloy_sheet',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:extendedae_coverage/wireless_hub')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Addressed memory now has a completed populated board, calculation controller, advanced industrial error control, reinforced bus and magnetic shielding. Practical single-cell assembly; no late quantum demand. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:item_storage_cell_16k'], 'tfmg:coated_circuit_board', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_16k']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_reinforced']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:coated_circuit_board'}})).loops(1).id('industrial_colonies:v3_ae2/item_storage_cell_16k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Large memory requires the costly existing shell plus an internal heavy containment cassette, concurrent addressing, engineering correction and elite industrial interlocks. Actual structural subassembly and refined buses, not more loose logic chips. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:item_storage_cell_64k'], 'ae2:item_cell_housing', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_64k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_machinery_casing']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:item_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/item_storage_cell_64k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Automates copying/printing supported book or enchantment-related content using the mod printing processes.
    // USES / PROGRESSION / OVERLAP: Optional experience/enchanting factory. Check actual retained print recipes before adding expensive electronics; not needed for metal production.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED.
    // 
    // [Digital Logistics] Turn a spout into a controlled printing head with a precision feed, Brass platen, display strip, ink charge, and TFMG controller
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['create_enchantment_industry:printer'], 'create:spout', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:brass_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:display_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:black_dye']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:spout'}})).loops(1).id('industrial_colonies:create_addons/enchantment_printer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Experience-handling hatch in the mod liquid-experience automation system.
    // USES / PROGRESSION / OVERLAP: An XP-service connection, not a liquid fuel refinery. Useful only if the enchanting/XP line is retained.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Function not established from the saved card. Keep deferred; inspect native implementation and consumers before deciding. Evidence: NOT VERIFIED.
    // 
    // [Digital Logistics] Rebuild a generic fluid hatch for liquid experience with a filtered valve, pressure face, and dedicated XP reservoir
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['create_enchantment_industry:experience_hatch'], 'create_dragons_plus:fluid_hatch', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:experience_block']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_fluid_valve']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:sturdy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:brass_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create_dragons_plus:fluid_hatch'}})).loops(1).id('industrial_colonies:create_addons/experience_hatch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Blaze-powered automated enchanting apparatus in the installed enchantment automation family.
    // USES / PROGRESSION / OVERLAP: Optional equipment-enchantment production, separate from chemical processing. Inspect its Ponder/template/fuel requirements when comparing with the Classic variant.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Create Enchantment Industry enchanting hardware or template. Exact installed behavior and upgrades need verification; keep deferred rather than inventing an explanation or recipe. Evidence: Installed identity only.
    // 
    // [Digital Logistics] Convert an Enchanting Table into a liquid-XP production machine by installing its Blaze heat source, upgrade die, Spout inlet, and precision level controller
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['create_enchantment_industry:blaze_enchanter'], 'minecraft:enchanting_table', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:blaze_burner']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create_dragons_plus:blaze_upgrade_smithing_template']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:spout']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:enchanting_table'}})).loops(1).id('industrial_colonies:enchantment_industry/blaze_enchanter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Automated anvil-like machine: merges enchantments/templates, applies templates and can strip enchantments onto a blank template, powered by experience.
    // USES / PROGRESSION / OVERLAP: Equipment/enchanting industry. Installed Ponder also documents super-enchanting mode; powerful equipment features deserve separate balance from material machines.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Create Enchantment Industry enchanting hardware or template. Exact installed behavior and upgrades need verification; keep deferred rather than inventing an explanation or recipe. Evidence: Installed identity only.
    // 
    // [Digital Logistics] Rebuild an Anvil as a liquid-XP forging station around a captured Blaze, the upgrade die, a complete Mechanical Press ram, and a sturdy heat shield
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['create_enchantment_industry:blaze_forger'], 'minecraft:anvil', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:blaze_burner']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create_dragons_plus:blaze_upgrade_smithing_template']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:mechanical_press']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:sturdy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:anvil'}})).loops(1).id('industrial_colonies:enchantment_industry/blaze_forger')
  }
})

ServerEvents.recipes(event => {
  // Review revision: All nine slots occupied as requested: sturdy corner braces, dense top/bottom backplanes and magnetic guide rails surrounding one machine-frame spine. Ordinary3x3 crafting, four frame segments. Existing pack items; proposed editor recipe, no gameplay export.
  event.shaped('4x extendedae:assembler_matrix_frame', ['ABA', 'CDC', 'ABA'], {
      A: 'create:sturdy_sheet',
      B: 'ae2:fluix_smart_dense_cable',
      C: 'tfmg:magnetic_alloy_sheet',
      D: 'extendedae:machine_frame'
    }).id('industrial_colonies:digital_storage/assembler_matrix_frame_batch')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Thin5x2 high-temperature plumbing bank: titanium pressure straps and tungsten thermal joints along four industrial bores. Removes full pumps/controllers and thick three-row manifold; eight thin engine pipe sections per batch. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('8x rocketnautics:engine_pipes', ['ABABA', 'CBCBC'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'tfmg:industrial_pipe',
        C: 'createmetallurgy:tungsten_sheet'
      }).id('industrial_colonies:space/propulsion/engine_pipes')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Converts items using antimatter and large energy input in its registered recipes. SPS makes the antimatter; this machine consumes it. It is not a fission/fusion reactor or an antimatter generator.
    // USES / PROGRESSION / OVERLAP: Extreme endgame transmutation after SPS. Its permitted outputs must be audited for rare-material shortcuts before enabling replacements. Construction must not be an SPS prerequisite, or the chain would be circular. Recipe unchanged for this explanation.
    // 
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // WHAT IT DOES: Consumes antimatter and very large amounts of energy in its registered item-conversion recipes.
    // USES / PROGRESSION / OVERLAP: After SPS antimatter production, at extreme endgame. It is not the machine that makes the first antimatter and must not be required to build SPS.
    // Your recipe is unchanged. Choose Maybe if unsure, Approve if suitable, or Park for later.
    // 
    // [Interstellar Escape] Mechanically assemble the functional subassemblies in their physical working layout
    event.recipes.create.mechanical_crafting('mekanism:antiprotonic_nucleosynthesizer', [' ABC ', 'DEFED', 'GHIHG', 'DEFED', ' CBA '], {
        A: 'ae2:quantum_entangled_singularity',
        B: 'mekanism:ultimate_control_circuit',
        C: 'mekanism:ultimate_energy_cube',
        D: 'create:refined_radiance',
        E: 'mekanism:pellet_polonium',
        F: 'mekanism:laser',
        G: 'tfmg:heavy_machinery_casing',
        H: 'create:refined_radiance_casing',
        I: 'mekanism:supercharged_coil'
      }).id('industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Keep the liked ten-slot disk rack and addressed backplane. Aluminum cabinet panels replace every steel plate; plastic separators and electrum contacts retain the same slot arrangement. No finished storage cells consumed.
    event.recipes.create.mechanical_crafting('ae2:drive', ['AAAAA', 'BC CB', 'BC CB', 'BC CB', 'BC CB', 'BC CB', 'ADEFA'], {
        A: 'tfmg:aluminum_sheet',
        B: 'tfmg:plastic_sheet',
        C: 'createaddition:electrum_wire',
        D: 'tfmg:circuit_board',
        E: 'ae2:engineering_processor',
        F: 'ae2:logic_processor'
      }).id('industrial_colonies:v3_ae2/drive')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Enhanced End automata turtle upgrade, associated with the End/teleportation ability family.
    // USES / PROGRESSION / OVERLAP: Treat as late optional programmable mobility. Exact method costs/range are not asserted here; assess teleportation bypasses before retaining.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Advanced Peripherals upgrade core; installed tooltip identifies it as a stronger, fragile End Automata upgrade. Keep deferred until the exact enabled abilities and limits are audited; do not infer safe balance from the name. Evidence: Installed identity / functional summary; exact balance not certified.
    // 
    // [High-Energy Grid] Upgrade the earned end automata core with star power, an ender-range modem, paired locator optics, fluix coupling, a tuned radio coil, and stress-stable teleport control
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['advancedperipherals:overpowered_end_automata_core'], 'advancedperipherals:end_automata_core', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:nether_star']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'computercraft:wireless_modem_advanced']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:ender_eye']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_pearl']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:large_coil']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'advancedperipherals:end_automata_core'}})).loops(1).id('industrial_colonies:computer_network_coverage/overpowered_end_automata_core')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Computer peripheral that scans nearby blocks and reports geological/block information to Lua programs.
    // USES / PROGRESSION / OVERLAP: Useful prospecting tool. Compare its information/range/cost with the expensive surface-scanner plan; this does not itself mine ore.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Computer peripheral that scans nearby blocks/ores, with native FE cost and scan cooldown.
    // 
    // Review revision: Amethyst sensing head and observer over engineering survey processing, buffered supply and a computer peripheral chassis. Powerful nearby block/ore scans justify a serious digital survey gate; native FE/cooldown still apply. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('advancedperipherals:geo_scanner', ['  A  ', 'BCDCB', 'EFGFE', 'HIJIH', 'BKKKB'], {
        A: 'minecraft:amethyst_shard',
        B: 'tfmg:nickel_sheet',
        C: 'minecraft:glass',
        D: 'minecraft:observer',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:circuit_board',
        G: 'ae2:engineering_processor',
        H: 'createaddition:electrum_wire',
        I: 'advancedperipherals:peripheral_casing',
        J: 'tfmg:capacitor_item',
        K: 'tfmg:steel_frame'
      }).id('industrial_colonies:computer_network_coverage/geo_scanner')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Fluidizer multiblock control/status block. The complete multiblock provides solid/fluid material conversion through its registered processing recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Fluidizer: Provides the multiblock control interface. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Build a three-vat vertical process column with paired circulation pumps, a monitor crown, controller face, and chemical manifold bed.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('bigreactors:fluidizercontroller', ['  A  ', ' BCB ', ' DCD ', ' BCB ', 'EFGHE'], {
        A: 'computercraft:monitor_advanced',
        B: 'tfmg:electric_pump',
        C: 'tfmg:steel_chemical_vat',
        D: 'create:refined_radiance_casing',
        E: 'mekanism:elite_control_circuit',
        F: 'computercraft:computer_advanced',
        G: 'ae2:engineering_processor',
        H: 'bigreactors:fluidizercasing'
      }).id('industrial_colonies:bigreactors/fluidizer/controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Steel rocket tank component used in the corresponding Ad Astra spacecraft construction chain.
    // USES / PROGRESSION / OVERLAP: Space construction component. This tank is a rocket ingredient, not blanket approval for a giant portable fluid inventory; this engine component is not a standalone FE generator. Retain only if the corresponding Ad Astra rocket route remains in the pack.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Ad Astra rocket-tank construction component, tier steel. Keep only where a retained rocket recipe needs it; distinguish it from portable general-purpose fluid storage. Evidence: Installed component identity; exact consumers to audit.
    // 
    // [Orbital Engineering] Turn a basic gas tank into a serviceable steel pressure vessel with heavy cheeks, a pipe neck, elastomer seal, and fastener
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['ad_astra:steel_tank'], 'ad_astra:gas_tank', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_plate']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ad_astra:gas_tank'}})).loops(1).id('industrial_colonies:space_coverage/steel_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Desh rocket tank component used in the corresponding Ad Astra spacecraft construction chain.
    // USES / PROGRESSION / OVERLAP: Space construction component. This tank is a rocket ingredient, not blanket approval for a giant portable fluid inventory; this engine component is not a standalone FE generator. Retain only if the corresponding Ad Astra rocket route remains in the pack.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Ad Astra rocket-tank construction component, tier desh. Keep only where a retained rocket recipe needs it; distinguish it from portable general-purpose fluid storage. Evidence: Installed component identity; exact consumers to audit.
    // 
    // [Planetary Industry] Overwrap the steel pressure vessel with two formed Desh layers, a renewed rubber seal, and a titanium service neck
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['ad_astra:desh_tank'], 'ad_astra:steel_tank', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:desh_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:desh_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ad_astra:steel_tank'}})).loops(1).id('industrial_colonies:space_coverage/desh_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Ostrum rocket tank component used in the corresponding Ad Astra spacecraft construction chain.
    // USES / PROGRESSION / OVERLAP: Space construction component. This tank is a rocket ingredient, not blanket approval for a giant portable fluid inventory; this engine component is not a standalone FE generator. Retain only if the corresponding Ad Astra rocket route remains in the pack.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Ad Astra rocket-tank construction component, tier ostrum. Keep only where a retained rocket recipe needs it; distinguish it from portable general-purpose fluid storage. Evidence: Installed component identity; exact consumers to audit.
    // 
    // [Planetary Industry] Refit the lunar tank with dual Ostrum shells, magnetic bracing, and a fresh high-pressure seal
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['ad_astra:ostrum_tank'], 'ad_astra:desh_tank', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ad_astra:desh_tank'}})).loops(1).id('industrial_colonies:space_coverage/ostrum_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: RGB charge component from the Colony4CC display/hologram integration family.
    // USES / PROGRESSION / OVERLAP: A specialized display-related item, not general battery energy or rocket fuel. Exact consumption/use must be checked in its installed recipe/use pages before changing its cost.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Colony4CC RGB charge item; the saved card is a production batch. Exact consumer/use requires verification; do not price an unexplained consumable yet. Evidence: Installed identity / functional summary; exact balance not certified.
    // 
    // [Digital Logistics] Build eight rechargeable hologram charges by layering red, green, and blue emitters over glowstone, then adding switching powder and a TFMG capacitor; MineColonies crafter routes remain available
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['8x colony4cc:rgb_charge'], 'minecraft:glowstone_dust', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:red_dye']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:green_dye']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:blue_dye']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:redstone']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:glowstone_dust'}})).loops(1).id('industrial_colonies:computer_network_coverage/rgb_hologram_charge_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Energizer FE energy input/output connection; active variants participate in the machine energy-output behavior. The complete multiblock provides bulk electrical energy storage/charging.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Energizer: Connects the machine to power. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Convert an Energizer casing into a buffered grid interface with a transformer, steel cable termination, double connector, capacitor bank, and plastic-isolated complementary control board
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:energizerpowerport_fe'], 'bigreactors:energizercasing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transformer']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_cable_hub']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_energy_cube']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:double_connector']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:energizercasing'}})).loops(1).id('industrial_colonies:bigreactors/energizer/power_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Energizer FE energy input/output connection; active variants participate in the machine energy-output behavior. The complete multiblock provides bulk electrical energy storage/charging.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Energizer: Active power connection; inspect transfer direction/limits before balancing. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Instrument the passive Energizer interface with a double grid connector, current transformer, relay, plastic-isolated N/P sensing board, capacitor, and elite transfer governor
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:energizerpowerport_fe_active'], 'bigreactors:energizerpowerport_fe', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:double_connector']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:current_transformer']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'computercraft:redstone_relay']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:energizerpowerport_fe'}})).loops(1).id('industrial_colonies:bigreactors/energizer/active_power_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Fluidizer FE energy input/output connection; active variants participate in the machine energy-output behavior. The complete multiblock provides solid/fluid material conversion through its registered processing recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Fluidizer: Connects the machine to power. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Terminate the Fluidizer grid feed through transformer isolation, buffered energy, a steel cable hub, double connector, and plastic-isolated N/P dosing controller
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:fluidizerpowerport'], 'bigreactors:fluidizercasing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transformer']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_energy_cube']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_cable_hub']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:double_connector']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:fluidizercasing'}})).loops(1).id('industrial_colonies:bigreactors/fluidizer/power_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Fluidizer solid-material input connection. The complete multiblock provides solid/fluid material conversion through its registered processing recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Fluidizer: Supplies solid material to the process. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Build a metered solids feed from vault storage, a filtered smart chute, powered piston and motor, steel drive mechanism, and protected advanced dosing control
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:fluidizersolidinjector'], 'bigreactors:fluidizercasing', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:item_vault']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:smart_chute']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:filter']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:mechanical_piston']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_mechanism']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:fluidizercasing'}})).loops(1).id('industrial_colonies:bigreactors/fluidizer/solid_injector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Reprocessor multiblock control/status block. The complete multiblock provides processing used reactor material through its registered recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reprocessor: Provides the multiblock control interface. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Lay out the reprocessor as a visible material-flow console: waste and collection heads over twin chemical-vat lanes, solid output below, inherited reactor safety, and a plastic-isolated N/P digital control shelf
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('bigreactors:reprocessorcontroller', [' ABC ', 'DEFED', 'GHIHG', 'JKLMN', ' HOH '], {
        A: 'tfmg:n_semiconductor',
        B: 'bigreactors:reprocessorwasteinjector',
        C: 'bigreactors:reprocessorcollector',
        D: 'tfmg:plastic_sheet',
        E: 'tfmg:steel_chemical_vat',
        F: 'bigreactors:reprocessoroutputport',
        G: 'computercraft:monitor_advanced',
        H: 'bigreactors:reprocessorcasing',
        I: 'bigreactors:basic_reactorcontroller',
        J: 'tfmg:p_semiconductor',
        K: 'tfmg:coated_circuit_board',
        L: 'mekanism:ultimate_control_circuit',
        M: 'computercraft:computer_advanced',
        N: 'ae2:engineering_processor',
        O: 'create:refined_radiance_casing'
      }).id('industrial_colonies:bigreactors/reprocessor/controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Normal wireless colony/computer integration peripheral from Colony4CC.
    // USES / PROGRESSION / OVERLAP: Colony management branch, not a general inventory radio or ship navigation computer. Retain only if scripted colony integration is wanted.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Colony4CC wireless integration component. Exact range and colony functions still need verification; defer recipe decision. Evidence: Installed identity / functional summary; exact balance not certified.
    // 
    // [Digital Logistics] Convert the wired colony console into a field upgrade by fitting the normal radio, an insulated antenna lead, rechargeable lithium power, and the adhesive interface used by pocket computers
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['colony4cc:colony_wireless_normal'], 'colony4cc:colony_peripheral', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'computercraft:wireless_modem_normal']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', Ingredient.of('#c:slime_balls')]),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'colony4cc:colony_peripheral'}})).loops(1).id('industrial_colonies:computer_network_coverage/colony_wireless_normal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Template for the mod super-enchanting operations.
    // USES / PROGRESSION / OVERLAP: Advanced enchanting branch; assess above-vanilla enchantment behavior separately. Not an industrial electronics material.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Create Enchantment Industry enchanting hardware or template. Exact installed behavior and upgrades need verification; keep deferred rather than inventing an explanation or recipe. Evidence: Installed identity only.
    // 
    // [Digital Logistics] Upgrade a blank template with an Ancient City Echo Shard, a full experience reservoir, a lapis matrix, and a sturdy backing before the final Brass precision press
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['create_enchantment_industry:super_enchanting_template'], 'create_enchantment_industry:enchanting_template', [
        event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:experience_block']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:lapis_block']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:sturdy_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create_enchantment_industry:enchanting_template'}})).loops(1).id('industrial_colonies:enchantment_industry/super_enchanting_template')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: External energy input/output connection of a Mekanism Induction Matrix.
    // USES / PROGRESSION / OVERLAP: Bulk electrical storage infrastructure. Cells store energy, providers govern throughput, ports connect the matrix; not a reactor or chemical machine.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Energy input/output connection of the Induction Matrix multiblock. Installed text: A port that can be placed on an Energized Induction Matrix multiblock, allowing for energy to be inserted from and output to external cabling.
    // 
    // [High-Energy Grid] Build regulated matrix I/O from the completed shell, ultimate local cable, and both analog voltage-control branches.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('2x mekanism:induction_port', ['AABAA', 'ACDCA', 'BEFEB', 'ACDCA', 'AABAA'], {
        A: 'mekanism:induction_casing',
        B: 'mekanism:ultimate_universal_cable',
        C: 'electroenergetics:voltage_regulator',
        D: 'mekanism:ultimate_control_circuit',
        E: 'electroenergetics:high_voltage_capacitor',
        F: 'tfmg:heavy_machinery_casing'
      }).id('industrial_colonies:mekanism/induction/port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Fluidizer structural enclosure segment. The complete multiblock provides solid/fluid material conversion through its registered processing recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Fluidizer: Forms the multiblock shell. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Pressure-form eight Fluidizer shell segments around paired chemical vats, pumped steel manifolds, service valves, radiance lining, and a load-bearing steel frame.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['8x bigreactors:fluidizercasing'], ['create:refined_radiance_casing', 'create:refined_radiance_casing', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_chemical_vat', 'tfmg:steel_chemical_vat', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:electric_pump', 'tfmg:electric_pump', 'mekanism:dynamic_valve', 'mekanism:dynamic_valve']).id('industrial_colonies:bigreactors/fluidizer/casing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Turbine rotor blade that extracts energy from the working fluid. The complete multiblock provides converting supplied working-fluid energy through a rotor/generator.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Basic Turbine: Receives steam flow to drive the turbine. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Stamp four balanced turbine blades from Cyanite-alloy cores, tapered aluminum skins, heavy steel roots, and matched drive mechanisms.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['4x bigreactors:basic_turbinerotorblade'], ['bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:aluminum_sheet', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:magnetic_alloy_ingot', 'tfmg:magnetic_alloy_ingot']).id('industrial_colonies:bigreactors/basic_turbine/rotor_blade')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Turbine rotating shaft connecting the turbine blade stages. The complete multiblock provides converting supplied working-fluid energy through a rotor/generator.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Basic Turbine: Connects the rotating turbine blades. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Key four rotor-shaft modules around concentric Create shafts and steel tube, then lock them with Cyanite bearings, magnetic laminations, and serviceable drive mechanisms.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['4x bigreactors:basic_turbinerotorshaft'], ['create:shaft', 'create:shaft', 'create:shaft', 'create:shaft', 'create:shaft', 'create:shaft', 'create:shaft', 'create:shaft', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'tfmg:magnetic_alloy_ingot', 'tfmg:magnetic_alloy_ingot', 'tfmg:magnetic_alloy_ingot', 'tfmg:magnetic_alloy_ingot', 'tfmg:heavy_plate', 'tfmg:heavy_plate']).id('industrial_colonies:bigreactors/basic_turbine/rotor_shaft')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Energizer central energy-storage core component. The complete multiblock provides bulk electrical energy storage/charging.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Energizer: Internal energy-storage component. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Grow a resonance core around a proven energy buffer using Magentite field material, paired Anglesite optics, complementary semiconductor control, populated TFMG logic, atomic alloy, and radiance confinement
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:energycore'], 'mekanism:advanced_energy_cube', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'bigreactors:magentite_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'bigreactors:anglesite_crystal']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'bigreactors:anglesite_crystal']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance_casing']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:advanced_energy_cube'}})).loops(1).id('industrial_colonies:bigreactors/energizer/energy_core')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Energizer stored-energy cell component. The complete multiblock provides bulk electrical energy storage/charging.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Energizer: Contributes to stored energy. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Sleeve the completed resonance core with paired Benitoite optics, an elite induction buffer, magnetic laminations, plastic-isolated complementary sensing, and radiance shielding
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:energizercell'], 'bigreactors:energycore', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'bigreactors:benitoite_crystal']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'bigreactors:benitoite_crystal']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_induction_cell']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance_casing']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:energycore'}})).loops(1).id('industrial_colonies:bigreactors/energizer/energy_cell')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Energizer structural enclosure segment. The complete multiblock provides bulk electrical energy storage/charging.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Energizer: Forms the multiblock shell. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Compress eight Energizer shell segments from radiance field lining, steel frames and plate, transformer windings, induction buffering, capacitors, and a high-current cable termination.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['8x bigreactors:energizercasing'], ['create:refined_radiance_casing', 'create:refined_radiance_casing', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:steel_frame', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:transformer', 'tfmg:transformer', 'tfmg:transformer', 'tfmg:transformer', 'mekanism:elite_induction_cell', 'mekanism:elite_induction_cell', 'tfmg:capacitor_item', 'tfmg:capacitor_item', 'tfmg:capacitor_item', 'tfmg:capacitor_item', 'tfmg:steel_cable_hub', 'tfmg:steel_cable_hub']).id('industrial_colonies:bigreactors/energizer/casing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Reprocessor structural enclosure segment. The complete multiblock provides processing used reactor material through its registered recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reprocessor: Forms the multiblock shell. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Pressure-seal eight Cyanite-handling reprocessor wall segments on the nuclear Refined Radiance containment line.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['8x bigreactors:reprocessorcasing'], ['tfmg:steel_casing', 'tfmg:steel_casing', 'tfmg:steel_casing', 'tfmg:steel_casing', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'bigreactors:cyanite_ingot', 'tfmg:steel_chemical_vat', 'tfmg:steel_chemical_vat', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_fluid_valve', 'tfmg:steel_fluid_valve']).id('industrial_colonies:bigreactors/reprocessor/casing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Fluidizer product output connection. The complete multiblock provides solid/fluid material conversion through its registered processing recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Fluidizer: Extracts processed output. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Build a controlled product outlet from a storage vault, smart chute, ME storage bus, steel mechanism, and advanced circuit.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:fluidizeroutputport'], 'bigreactors:fluidizercasing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:item_vault']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:smart_chute']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:storage_bus']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_mechanism']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:fluidizercasing'}})).loops(1).id('industrial_colonies:bigreactors/fluidizer/output_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Fluidizer fluid input connection. The complete multiblock provides solid/fluid material conversion through its registered processing recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Fluidizer: Supplies fluid to the process. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Assemble the fluid feed from a TFMG electric pump, chemical vat, metering valve, Mekanism tank, and advanced process control.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:fluidizerfluidinjector'], 'bigreactors:fluidizercasing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_pump']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_chemical_vat']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_chemical_tank']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:fluidizercasing'}})).loops(1).id('industrial_colonies:bigreactors/fluidizer/fluid_injector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Energizer computer-control/telemetry connection. The complete multiblock provides bulk electrical energy storage/charging.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Energizer: Exposes the machine to computer integration. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Network an Energizer casing with a wired modem, redstone relay, engineering processor, protected leads, and elite interface logic.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:energizercomputerport'], 'bigreactors:energizercasing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'computercraft:wired_modem']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'computercraft:redstone_relay']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:energizercasing'}})).loops(1).id('industrial_colonies:bigreactors/energizer/computer_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Energizer equipment charging connection. The complete multiblock provides bulk electrical energy storage/charging.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Energizer: Provides an item-charging connection. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Convert an Energizer shell into a controlled charging face with an induction port, tablet, capacitor, transformer, and interlock.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:energizerchargingport_fe'], 'bigreactors:energizercasing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:induction_port']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:energy_tablet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transformer']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:energizercasing'}})).loops(1).id('industrial_colonies:bigreactors/energizer/charging_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Turbine rotating shaft connecting the turbine blade stages. The complete multiblock provides converting supplied working-fluid energy through a rotor/generator.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reinforced Turbine: Connects the rotating turbine blades. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Upgrade four basic shafts into atomic-alloy reinforced drive modules.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['4x bigreactors:reinforced_turbinerotorshaft'], ['bigreactors:basic_turbinerotorshaft', 'bigreactors:basic_turbinerotorshaft', 'bigreactors:basic_turbinerotorshaft', 'bigreactors:basic_turbinerotorshaft', 'bigreactors:reinforced_turbinecasing', 'bigreactors:reinforced_turbinecasing', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic']).id('industrial_colonies:bigreactors/reinforced_turbine/rotor_shaft')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Turbine rotor blade that extracts energy from the working fluid. The complete multiblock provides converting supplied working-fluid energy through a rotor/generator.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reinforced Turbine: Receives steam flow to drive the turbine. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Upgrade four matched basic blades as an economical reinforced rotor batch.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['4x bigreactors:reinforced_turbinerotorblade'], ['bigreactors:basic_turbinerotorblade', 'bigreactors:basic_turbinerotorblade', 'bigreactors:basic_turbinerotorblade', 'bigreactors:basic_turbinerotorblade', 'bigreactors:reinforced_turbinecasing', 'bigreactors:reinforced_turbinecasing', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic']).id('industrial_colonies:bigreactors/reinforced_turbine/rotor_blade')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Turbine rotor support/bearing required by the turbine structure. The complete multiblock provides converting supplied working-fluid energy through a rotor/generator.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reinforced Turbine: Supports the rotating turbine assembly. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Rebuild the proven basic bearing as a reinforced high-speed cartridge.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['bigreactors:reinforced_turbinerotorbearing'], ['bigreactors:basic_turbinerotorbearing', 'bigreactors:reinforced_turbinecasing', 'bigreactors:reinforced_turbinecasing', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'tfmg:steel_mechanism', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic']).id('industrial_colonies:bigreactors/reinforced_turbine/rotor_bearing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Turbine structural enclosure segment. The complete multiblock provides converting supplied working-fluid energy through a rotor/generator.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reinforced Turbine: Forms the multiblock shell. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Upgrade eight basic turbine walls at the Blutonium-Plutonium convergence instead of repeating full electronics in every wall.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.industrial_colonies.refined_radiance_compacting(['8x bigreactors:reinforced_turbinecasing'], ['bigreactors:basic_turbinecasing', 'bigreactors:basic_turbinecasing', 'bigreactors:basic_turbinecasing', 'bigreactors:basic_turbinecasing', 'bigreactors:basic_turbinecasing', 'bigreactors:basic_turbinecasing', 'bigreactors:basic_turbinecasing', 'bigreactors:basic_turbinecasing', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'create:refined_radiance_casing', 'create:refined_radiance_casing', 'create:refined_radiance_casing', 'create:refined_radiance_casing', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:alloy_atomic', 'mekanism:pellet_plutonium', 'mekanism:pellet_plutonium', 'bigreactors:blutonium_ingot', 'bigreactors:blutonium_ingot', 'bigreactors:blutonium_ingot', 'bigreactors:blutonium_ingot', 'bigreactors:reprocessorcasing', 'bigreactors:reprocessorcasing']).id('industrial_colonies:bigreactors/reinforced_turbine/casing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Carries an enchantment configuration for the mod enchanting/forging machines.
    // USES / PROGRESSION / OVERLAP: A reusable production pattern in relevant operations, not a silicon circuit or universal mechanism. Use only in the enchanting branch.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Create Enchantment Industry enchanting hardware or template. Exact installed behavior and upgrades need verification; keep deferred rather than inventing an explanation or recipe. Evidence: Installed identity only.
    // 
    // [Digital Logistics] Laminate two layers of lapis and condensed experience into paper, then Brass-press a reusable blank enchanting record
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['create_enchantment_industry:enchanting_template'], 'minecraft:paper', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:lapis_lazuli']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:experience_nugget']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:paper'}})).loops(2).id('industrial_colonies:enchantment_industry/enchanting_template')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Reprocessor fluid input connection. The complete multiblock provides processing used reactor material through its registered recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reprocessor: Supplies fluid to the process. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Plumb a pressure-rated reprocessor injector from a chemical vat, powered pump, twin steel feeds, shutoff valve, chemical buffer, smart flow section, and elite metering circuit
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:reprocessorfluidinjector'], 'bigreactors:reprocessorcasing', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_chemical_vat']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_pump']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_chemical_tank']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_smart_fluid_pipe']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_pipe']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_frame']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:reprocessorcasing'}})).loops(1).id('industrial_colonies:bigreactors/reprocessor/fluid_injector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Reprocessor product output connection. The complete multiblock provides processing used reactor material through its registered recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reprocessor: Extracts processed output. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Build a powered solid-output face around vault storage, filtered smart extraction, a framed steel drive, logistical sorter, and advanced routing control
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:reprocessoroutputport'], 'bigreactors:reprocessorcasing', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:item_vault']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:smart_chute']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:filter']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_frame']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_mechanism']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:logistical_sorter']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_pipe']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:reprocessorcasing'}})).loops(1).id('industrial_colonies:bigreactors/reprocessor/output_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Reprocessor FE energy input/output connection; active variants participate in the machine energy-output behavior. The complete multiblock provides processing used reactor material through its registered recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reprocessor: Connects the machine to power. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Electrify the reprocessor through transformer isolation, a steel cable hub, buffered energy and double connector, then add a capacitor and plastic-isolated complementary control board
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:reprocessorpowerport'], 'bigreactors:reprocessorcasing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transformer']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_cable_hub']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:energy_tablet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:double_connector']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_pipe']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_frame']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:reprocessorcasing'}})).loops(1).id('industrial_colonies:bigreactors/reprocessor/power_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Reprocessor waste input connection for reprocessing. The complete multiblock provides processing used reactor material through its registered recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reprocessor: Supplies waste material for reprocessing. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Build a contained waste feed from a chemical vat, powered pump, isolated steel line and valve, radioactive buffer barrel, smart flow section, and elite interlock
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:reprocessorwasteinjector'], 'bigreactors:reprocessorcasing', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_chemical_vat']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_pump']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_chemical_tank']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:radioactive_waste_barrel']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_smart_fluid_pipe']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_pipe']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_frame']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:reprocessorcasing'}})).loops(1).id('industrial_colonies:bigreactors/reprocessor/waste_injector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Reprocessor processed-output collection component. The complete multiblock provides processing used reactor material through its registered recipes.
    // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Reprocessor: Internal collection component; exact operation requires verification. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
    // 
    // [Nuclear Engineering] Build bulk product collection around vault storage, paired smart extraction chutes, a filter and logistical sorter, then drive it with a serviceable steel mechanism and motor
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['bigreactors:reprocessorcollector'], 'bigreactors:reprocessorcasing', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:item_vault']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:smart_chute']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:smart_chute']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:filter']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:logistical_sorter']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_mechanism']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_motor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'bigreactors:reprocessorcasing'}})).loops(1).id('industrial_colonies:bigreactors/reprocessor/collector')
  }
})

ServerEvents.recipes(event => {
  // WHAT IT DOES: Reactor redstone control/monitor connection. The complete multiblock provides nuclear fuel power/heat production.
  // USES / PROGRESSION / OVERLAP: OPTIONAL FAMILY: You have not decided to retain Extreme Reactors alongside NuclearCraft/Mekanism. This explanation is for that decision, not approval to keep it. Compare whole-machine function/cost. Basic/reinforced names are construction tiers; this part alone is not a working machine or a recipe prerequisite for unrelated branches.
  // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
  // 
  // Deferred re-review: Basic Reactor: Control or connection component of the reactor system; inspect exact function before balancing. Hold the whole Extreme Reactors family while you decide whether to keep this alternative to NuclearCraft. Do not redesign every part before that decision. Evidence: Installed item identity; component role summary, family retention undecided. Optional Extreme Reactors family: returning this draft for a KEEP/NATIVE/CUSTOM decision does not approve retaining the competing nuclear route.
  // 
  // [Nuclear Engineering] Integrate a ComputerCraft redstone relay into a basic reactor port
  // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
  event.shaped('bigreactors:basic_reactorredstoneport', ['ABA', 'CDC', 'ACA'], {
      A: 'computercraft:cable',
      B: 'computercraft:redstone_relay',
      C: 'bigreactors:basic_reactorcasing',
      D: 'mekanism:elite_control_circuit'
    }).id('industrial_colonies:nuclear/basic_reactor_redstone_port')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Crafting component of the ExtendedAE Assembler Matrix multiblock.
    // USES / PROGRESSION / OVERLAP: Adds actual crafting machinery to the matrix; distinguish from walls, pattern capacity and speed upgrades. Digital manufacturing rather than portable cargo storage.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Adds actual crafting capacity to the assembler matrix.
    // 
    // Review revision: Matrix assembly head: motorized gantry, working hand and programmed electronic feed. A functional expansion component rather than the whole matrix controller. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('extendedae:assembler_matrix_crafter', ['  A  ', 'BCDCB', 'EFGFE', 'HIIIH'], {
        A: 'tfmg:electric_motor',
        B: 'create:precision_mechanism',
        C: 'create:shaft',
        D: 'create:brass_hand',
        E: 'createaddition:electrum_wire',
        F: 'tfmg:circuit_board',
        G: 'ae2:engineering_processor',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:steel_frame'
      }).group('07 Advanced digital manufacturing').id('industrial_colonies:custom_progression/extendedae/assembler_matrix_crafter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Pattern-related component of the ExtendedAE Assembler Matrix.
    // USES / PROGRESSION / OVERLAP: Supports matrix crafting-pattern infrastructure; not an item-storage cell. Exact capacity contribution depends on installed multiblock rules and is not asserted here.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Adds pattern capacity to the assembler matrix.
    // 
    // Review revision: Four pattern slots above addressed lookup and scheduling logic; dedicated matrix pattern capacity, not item memory. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('extendedae:assembler_matrix_pattern', ['AAAA', 'BCCB', 'DEED', 'FGGF'], {
        A: 'ae2:blank_pattern',
        B: 'tfmg:circuit_board',
        C: 'ae2:logic_processor',
        D: 'createaddition:electrum_wire',
        E: 'ae2:calculation_processor',
        F: 'tfmg:nickel_sheet',
        G: 'tfmg:steel_frame'
      }).group('07 Advanced digital manufacturing').id('industrial_colonies:custom_progression/extendedae/assembler_matrix_pattern')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Speed-related component of the ExtendedAE Assembler Matrix.
    // USES / PROGRESSION / OVERLAP: Throughput upgrade for digital autocrafting. Price alongside actual power/crafting benefit, not like a giant portable storage cell.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Speed expansion for assembler matrix work.
    // 
    // Review revision: Fit the existing assembly head with calibrated speed drive, parallel scheduling and cooled contacts; earlier crafter investment remains useful. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['extendedae:assembler_matrix_speed'], 'extendedae:assembler_matrix_crafter', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:upgrade_speed']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:potentiometer']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:nickel_sheet']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'extendedae:assembler_matrix_crafter'}})).loops(1).group('07 Advanced digital manufacturing').id('industrial_colonies:custom_progression/extendedae/assembler_matrix_speed')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Upgrade card that allows supported AE2 filters to use fuzzy matching, such as ignoring supported item damage distinctions.
    // USES / PROGRESSION / OVERLAP: Situational logistics filtering, not extra storage or faster crafting. Uses an existing AE2 base card; exact supported fuzzy modes depend on the host device.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Adjust matching rules for compatible filters; does not grant memory capacity.
    // 
    // Review revision: Adjustable comparison logic on the existing card base. Native fuzzy matching changes item-filter comparison; it does not increase capacity. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['ae2:fuzzy_card'], 'ae2:advanced_card', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:logic_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:comparator']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:potentiometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:advanced_card'}})).loops(1).group('07 Digital expansion cards').id('industrial_colonies:custom_progression/ae2/fuzzy_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Reverses the supported device filter selection, allowing blacklist behavior instead of the normal whitelist.
    // USES / PROGRESSION / OVERLAP: Small logistics/configuration upgrade. Uses the existing base-card chain, not a separate high-tier processor line.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Invert compatible inclusion/exclusion filtering; no new processor function.
    // 
    // Review revision: Signal inverter on a basic-card carrier with controlled output; native function reverses filtering behavior, not item storage. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['ae2:inverter_card'], 'ae2:basic_card', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:redstone_torch']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:resistor']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:basic_card'}})).loops(1).group('07 Digital expansion cards').id('industrial_colonies:custom_progression/ae2/inverter_card')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: Continuously applies enchantments selected by an Enchanting Template, using liquid experience. The template is not consumed each operation.
    // USES / PROGRESSION / OVERLAP: Automated equipment enchanting. Installed Ponder describes optional super-enchanting behavior; review that separately for balance, not as a required electronics gate.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Create Enchantment Industry enchanting hardware or template. Exact installed behavior and upgrades need verification; keep deferred rather than inventing an explanation or recipe. Evidence: Installed identity only.
    // 
    // [Digital Logistics] Build the automated enchanter as a handbook-guided workstation: Mechanical Arm and experience lantern above the original Blaze Enchanter, twin precision drives, Stress Processor control, and a rigid Brass base
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('create_enchantment_industry:classic_blaze_enchanter', [' AB ', '  CD', 'E FE', 'GGGG'], {
        A: 'create_enchantment_industry:blazes_enchanting_handbook',
        B: 'create:mechanical_arm',
        C: 'create_enchantment_industry:experience_lantern',
        D: 'appliedcreate:stress_processor',
        E: 'create:precision_mechanism',
        F: 'create_enchantment_industry:blaze_enchanter',
        G: 'create:brass_casing'
      }).id('industrial_colonies:enchantment_industry/classic_blaze_enchanter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Keep narrow breaker window/toggle/contact/trip-strip layout, but use four actual iron plate corner guards for a hardened casing over the insulating plastic body. No heavy motor or full transformer. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('electroenergetics:miniature_circuit_breaker', ['ABA', 'CDC', 'EFE', 'GHG', 'AIA'], {
        A: 'immersiveengineering:plate_iron',
        B: 'minecraft:glass',
        C: 'tfmg:plastic_sheet',
        D: 'minecraft:lever',
        E: 'tfmg:copper_wire',
        F: 'createaddition:electrum_wire',
        G: 'tfmg:rubber_sheet',
        H: 'tfmg:magnetic_alloy_sheet',
        I: 'tfmg:circuit_board'
      }).id('industrial_colonies:high_voltage/miniature_circuit_breaker')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Mirrored powered boots: existing recoil springs absorb impacts beside piston cylinders and a shared small hydraulic reservoir; two pump/guide assemblies meter the suspension, rubber soles soften landing and osmium heel supports carry load. Energy tablets/control boards retain powered assistance. Uses real pack springs, not an invented shock absorber or a MekaSuit-only hydraulic module. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:free_runners', ['ABCBA', 'DECED', 'FG GF', 'HI IH', 'JK KJ'], {
        A: 'mekanism:basic_control_circuit',
        B: 'tfmg:coated_circuit_board',
        C: 'tfmg:rebar',
        D: 'minecraft:sticky_piston',
        E: 'mekanism:energy_tablet',
        F: 'createbigcannons:recoil_spring',
        G: 'tfmg:cast_iron_fluid_tank',
        H: 'createaddition:iron_rod',
        I: 'tfmg:electric_pump',
        J: 'tfmg:rubber_sheet',
        K: 'mekanism:ingot_osmium'
      }).id('industrial_colonies:mekanism_tools/free_runners')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES: A redstone-controlled gate for ITEM pipes. Example: put it on the path to one chest, then power it to allow that branch only while the signal is on. Each connection can be set to Always active, Active with signal, or Active without signal using Shift-right-click with a Configurator.
    // WHY KEEP IT: Enables conditional overflow/priority routing in a short-range Mekanism item line. It does not store items, pump fluid or create energy. Compare with Create funnels/filters if the same job is already covered. Recipe unchanged.
    // SOURCE: Official Mekanism Diversion Transporter wiki and installed redstone-control tooltip.
    // 
    // WHAT IT DOES: Item transporter segment with redstone-controlled routing on its connections.
    // USES / PROGRESSION / OVERLAP: Local item-routing control, not a fluid pipe. Compare with Create routing and the retained short-range Mekanism exception; no long-distance transport approval implied.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Redstone-controlled logistics routing gate.
    // 
    // Review revision: Add a redstone-controlled directional gate to the ordinary transporter; native transport range policy is separate. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['2x mekanism:diversion_transporter'], 'mekanism:basic_logistical_transporter', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:comparator']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:basic_logistical_transporter'}})).loops(1).id('industrial_colonies:mekanism_utility/diversion_transporter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Rocket engine assembly: top propellant valve feeds paired pump/cylinder hardware, injector plumbing around the metering mechanism, refractory combustion throat below and a single exhaust nozzle. Steel load frame supports the hot zone. It is an actual engine construction shape, not a board-population sequence. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ad_astra:steel_engine', [' ABA ', 'ACDCA', 'AEFEA', ' GHG ', '  I  '], {
        A: 'immersiveengineering:plate_steel',
        B: 'tfmg:steel_fluid_valve',
        C: 'tfmg:engine_cylinder',
        D: 'tfmg:electric_pump',
        E: 'tfmg:steel_pipe',
        F: 'tfmg:steel_mechanism',
        G: 'tfmg:fireproof_bricks',
        H: 'tfmg:steel_frame',
        I: 'rocketnautics:copper_nozzle'
      }).id('industrial_colonies:space_coverage/steel_engine')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // CORRECTION: This is a pump RECIPE INPUT ITEM, not a standalone placeable water-making machine. The installed nuclearcraft:pump/water_collector recipe takes one Water Collector item and lists200mB water output,20processing ticks and energy_per_tick50.
    // HOW IT IS USED: Obtain the collector item, then use the NuclearCraft Pump process that lists it as an input. Whether the input is reused/consumed and actual throughput under upgrades require native checks; do not assume infinite free water.
    // WHY KEEP IT: A water-supply input for that specific Pump recipe. Compare with existing Create water pumping before keeping another custom collector construction recipe. The previous giant standalone-machine-shaped draft was misleading. Recipe left unchanged for your decision; no new water recipe installed.
    // SOURCE: Installed NuclearCraft JAR data/nuclearcraft/recipe/pump/water_collector.json.
    // 
    // WHAT IT DOES: Water collection/supply machine in NuclearCraft.
    // USES / PROGRESSION / OVERLAP: Compare with existing retained water sources/pumps before keeping another automatic supply machine. It is not water purification or a required new water recipe; exact production rate is not claimed.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Collects water for industrial use; no isotope/quantum production role inferred.
    // 
    // Review revision: Collection surface drains through twin pumps to a reservoir and basic level control. A water-source machine does not need nuclear mechanisms or quantum processors. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.mechanical_crafting('nuclearcraft:water_collector', ['ABABA', 'BCDCB', 'EFGFE', 'HIIIH'], {
        A: 'minecraft:glass',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:electric_pump',
        D: 'tfmg:steel_fluid_tank',
        E: 'tfmg:nickel_sheet',
        F: 'tfmg:circuit_board',
        G: 'ae2:logic_processor',
        H: 'tfmg:rubber_sheet',
        I: 'tfmg:steel_frame'
      }).group('06 Nuclear support').id('industrial_colonies:custom_progression/nuclearcraft/water_collector')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Pre-quantum singularity preparation: ordinary quartz observation window, electromagnetic confinement, reinforced industrial supports and engineering/advanced control. Removes every quantum-alloy plate and superconducting/rare thermal gate from this draft. No quantum processors, singularities, antimatter or downstream black-hole machinery required. This produces upstream feedstock for later quantum systems rather than depending on them. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('ae2:condenser', ['ABBBA', 'CDEDC', 'FGHGF', 'IJKJI', 'ALLLA'], {
        A: 'immersiveengineering:plate_steel',
        B: 'ae2:quartz_glass',
        C: 'tfmg:electromagnetic_coil',
        D: 'tfmg:steel_fluid_tank',
        E: 'ae2:annihilation_core',
        F: 'mekanism:alloy_reinforced',
        G: 'ae2:engineering_processor',
        H: 'mekanism:advanced_control_circuit',
        I: 'tfmg:rubber_sheet',
        J: 'tfmg:circuit_board',
        K: 'tfmg:capacitor_item',
        L: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/condenser')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Review revision: Installed radial-engine item model has radial spokes around a central hub, not a machine standing on a separate control cabinet. Seven-wide circular cylinder bank, ignition tips, cast-iron cooling fins and crank hub reproduce that radial silhouette. Existing pack items; proposed editor recipe, no gameplay export.
    event.recipes.create.mechanical_crafting('tfmg:radial_engine', ['  A A  ', ' BCCCB ', ' CDEDC ', 'ACEFECA', ' CDEDC ', ' BCCCB ', '  A A  '], {
        A: 'tfmg:spark_plug',
        B: 'immersiveengineering:plate_aluminum',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:aluminum_sheet',
        E: 'tfmg:crankshaft',
        F: 'tfmg:aluminum_smart_fluid_pipe'
      }).id('industrial_colonies:engines/radial_engine')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Based on USER-EDITED turbine reference: retain original aluminum plate/sheet outer shell,front intake,left/right pipes,calculation processor and sparkplug in their exact horizontal positions. Add one narrow internal liner row: three rubber sheets directly below the existing rubber/processor/ignition assembly,with aluminum end walls and two clearances below the pipe connections. Four rubber sheets total,instead of one. Original lower aluminum shell shifts down intact.7x4mechanical crafting,2shellsegments. No new internal blades,compressor,steelframes or extra processor suite;native right-click assembly unchanged.
    event.recipes.create.mechanical_crafting('2x tfmg:turbine_engine', [' AAAAA ', 'BCDCDCB', 'EF G FH', 'BCDCDCB', ' AAAAA '], {
        A: 'tfmg:aluminum_sheet',
        B: 'immersiveengineering:plate_aluminum',
        C: 'tfmg:rubber_sheet',
        D: 'tfmg:spark_plug',
        E: 'tfmg:air_intake',
        F: 'tfmg:aluminum_pipe',
        G: 'ae2:calculation_processor',
        H: 'rocketnautics:copper_nozzle'
      }).id('industrial_colonies:engines/turbine_engine')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // SECOND JUDGMENT: Previous Maybe expressed uncertainty, not a requested ingredient change. Recipe unchanged; compare with the newly approved references.
    // 
    // [Digital Logistics] Laminate a copper signal strand between quartz glass, fluix conductor, and plastic insulation; one pass yields eight practical starter cables
    event.recipes.create.sequenced_assembly(['8x ae2:fluix_glass_cable'], 'tfmg:copper_wire', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_glass']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_glass']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_crystal']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:copper_wire'}})).loops(1).id('industrial_colonies:v3_ae2/fluix_glass_cable_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [High-Energy Grid] Complete the Ultimate Installer from the entire Elite card, engineering logic, matched semiconductors, a high-voltage capacitor bank, redundant HDPE, refined-obsidian structure, magnetic isolation, and atomic control.
    event.recipes.create.sequenced_assembly(['mekanism:ultimate_tier_installer'], 'mekanism:elite_tier_installer', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:high_voltage_capacitor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:hdpe_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:hdpe_sheet']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ingot_refined_obsidian']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:elite_tier_installer'}})).loops(1).id('industrial_colonies:mekanism/tier_installer/ultimate')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [Planetary Industry] Line Netherite boots with Desh, close doubled Ostrum shells, and fit their gas cell, pressure valve, circulation fan, and rubber seals.
    event.recipes.create.sequenced_assembly(['ad_astra:netherite_space_boots'], 'minecraft:netherite_boots', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:desh_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:gas_tank']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:fan']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:netherite_boots'}})).loops(1).id('industrial_colonies:planetary/venus/netherite_space_boots')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [Planetary Industry] Pressure-fit the Netherite helmet with a Desh thermal liner, doubled Ostrum shell, visor, oxygen sensor, and exhaust vent before final pressing.
    event.recipes.create.sequenced_assembly(['ad_astra:netherite_space_helmet'], 'minecraft:netherite_helmet', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:desh_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:tinted_glass']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:oxygen_sensor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:vent']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:netherite_helmet'}})).loops(1).id('industrial_colonies:planetary/venus/netherite_space_helmet')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [Mekanized Industry] Bond four 1k dies behind calculation logic and a coated TFMG board, then add complementary semiconductor address drivers, paired buffers, a copper bus, dielectric laminate, and visible data face
    event.recipes.create.sequenced_assembly(['ae2:cell_component_4k'], 'ae2:cell_component_1k', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_1k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:cell_component_1k'}})).loops(1).id('industrial_colonies:v3_ae2/cell_component_4k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [High-Energy Grid] Expand the approved 1k stress matrix with a real 4k memory plane, stress feedback, wound TFMG copper buffering, paired capacitors, and a vibrant quartz service face
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_4k'], 'appliedcreate:stress_storage_component_1k', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:cell_component_4k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'create:stressometer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:copper_spool']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_4k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [Mekanized Industry] Bond four 4k planes through calculation and advanced stress control, a coated backplane, complementary TFMG gates, paired capacitors, lithium buffering, magnetic shielding, and a doubled dielectric package
    event.recipes.create.sequenced_assembly(['ae2:cell_component_16k'], 'ae2:cell_component_4k', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_4k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_4k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:cell_component_4k']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:cell_component_4k'}})).loops(1).id('industrial_colonies:v3_ae2/cell_component_16k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [High-Energy Grid] Wrap the module base in wool, TFMG rubber damping, and a plastic shell, then lock the quiet cartridge with infused alloy
    event.recipes.create.sequenced_assembly(['mekanism:upgrade_muffling'], 'mekanism:module_base', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:white_wool']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:white_wool']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:module_base'}})).loops(1).id('industrial_colonies:mekanism_components/upgrade_muffling')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [High-Energy Grid] Move the 64k matrix onto the Railway electronics line with advanced stress control, calculation logic, governed rotation, capacitor banks, laminated magnetic shielding, and a TFMG lithium reserve
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_64k'], 'appliedcreate:stress_storage_component_16k', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:cell_component_64k']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'create:rotation_speed_controller']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_64k')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [Nuclear Engineering] Schedule the 16M MEGA plane through concurrent stress control and a 16-cubed spatial map, then couple the kinetic acceptor through a Vibranium field plate and doubled Radiance contacts
    event.recipes.create.sequenced_assembly(['appliedcreate:stress_storage_component_16m'], 'appliedcreate:stress_storage_component_4m', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'megacells:cell_component_16m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'ae2:spatial_cell_component_16']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'appliedcreate:kinetic_energy_acceptor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:transformer']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'allthemodium:vibranium_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'create:refined_radiance']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'create:refined_radiance']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:unfinished_stress_storage_component', ['industrial_colonies:unfinished_stress_storage_component', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:unfinished_stress_storage_component', 'industrial_colonies:unfinished_stress_storage_component')
      ]).transitionalItem('industrial_colonies:unfinished_stress_storage_component').loops(1).id('industrial_colonies:appliedcreate/stress_storage_component_16m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: Use an actual shaft for the large hammer connector pivot. This separates its exact input bill from both hammer heads while preserving the approved metal body, fastening and Weathered Iron compacting process.
    // 
    // Existing approved layout and output retained.
    event.recipes.industrial_colonies.weathered_iron_compacting(['tfmg:large_pumpjack_hammer_connector'], ['tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'create:shaft', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector')
  }
})

ServerEvents.recipes(event => {
  // October 16 back-review proposal: Build the auger around an obtainable Create shaft; the three heavy steel plates form its helical flight and the Railway Casing forms its drive collar. The old encased-shaft block does not establish an obtainable ingredient stack and its loot returns the ordinary shaft. Preserve all other inputs, the cross-shaped layout and output.
  // 
  // Existing approved layout and output retained.
  event.shaped('simulated:auger_shaft', [' A ', 'ABA', ' C '], {
      A: 'tfmg:heavy_plate',
      B: 'create:shaft',
      C: 'create:railway_casing'
    }).id('industrial_colonies:simulated/auger_shaft')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: Retain the existing battery layout and electronics, but build this storage tier from four complete Basic cells, as in the installed Mekanism recipe. The remaining fresh lithium bank is retained. The Ultimate tier therefore contains 64 Basic cells through this upgrade chain; this is a material-use calculation, not an FE-capacity change.
    // 
    // Existing approved layout and output retained.
    event.recipes.create.mechanical_crafting('mekanism:advanced_induction_cell', [' ABA ', ' CDE ', 'FGCGF', ' CFC ', ' AHA '], {
        A: 'tfmg:steel_frame',
        B: 'mekanism:advanced_control_circuit',
        C: 'mekanism:basic_induction_cell',
        D: 'mekanism:advanced_energy_cube',
        E: 'tfmg:lithium_charge',
        F: 'tfmg:capacitor_item',
        G: 'mekanism:alloy_reinforced',
        H: 'tfmg:laminated_magnetic_alloy_block'
      }).id('industrial_colonies:mekanism/induction/advanced_cell')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: Retain the existing battery layout and electronics, but build this storage tier from four complete Advanced cells, as in the installed Mekanism recipe. A cobalt electrode support replaces the remaining loose lithium charge at this advanced tier; the embedded cells retain their lithium production demand. The Ultimate tier therefore contains 64 Basic cells through this upgrade chain; this is a material-use calculation, not an FE-capacity change.
    // 
    // Existing approved layout and output retained.
    event.recipes.create.mechanical_crafting('mekanism:elite_induction_cell', [' ABA ', ' CDE ', 'FGCGF', ' CHC ', ' AIA '], {
        A: 'tfmg:steel_frame',
        B: 'mekanism:elite_control_circuit',
        C: 'mekanism:advanced_induction_cell',
        D: 'mekanism:elite_energy_cube',
        E: 'modernfoundry:cobalt_ingot',
        F: 'mekanism:hdpe_sheet',
        G: 'tfmg:capacitor_item',
        H: 'mekanism:alloy_atomic',
        I: 'tfmg:laminated_magnetic_alloy_block'
      }).id('industrial_colonies:mekanism/induction/elite_cell')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: Retain the existing battery layout and electronics, but build this storage tier from four complete Elite cells, as in the installed Mekanism recipe. A cobalt electrode support replaces the remaining loose lithium charge at this advanced tier; the embedded cells retain their lithium production demand. The Ultimate tier therefore contains 64 Basic cells through this upgrade chain; this is a material-use calculation, not an FE-capacity change.
    // 
    // Existing approved layout and output retained.
    event.recipes.create.mechanical_crafting('mekanism:ultimate_induction_cell', [' ABA ', 'CDEDC', 'FGCGF', 'CDFDH', ' AIA '], {
        A: 'tfmg:steel_frame',
        B: 'mekanism:ultimate_control_circuit',
        C: 'mekanism:elite_induction_cell',
        D: 'electroenergetics:high_voltage_capacitor',
        E: 'mekanism:ultimate_energy_cube',
        F: 'mekanism:alloy_atomic',
        G: 'mekanism:energy_tablet',
        H: 'modernfoundry:cobalt_ingot',
        I: 'tfmg:laminated_magnetic_alloy_block'
      }).id('industrial_colonies:mekanism/induction/ultimate_cell')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: Use a bronze pivot blank for the small hammer head. Previously this card had exactly the same ingredients, amounts, process and machine as both the large head and connector, so its output was ambiguous. Keep its iron body, plates, screws, output and compacting process.
    // 
    // Existing approved layout and output retained.
    event.recipes.industrial_colonies.weathered_iron_compacting(['tfmg:pumpjack_hammer_head'], ['tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:cast_iron_ingot', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'mekanism:ingot_bronze', 'tfmg:screw', 'tfmg:screw']).id('industrial_colonies:machine/oil_processing/pumpjack_hammer_head')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // WHAT IT DOES: Enclosure wall segment for the ExtendedAE Assembler Matrix multiblock.
    // USES / PROGRESSION / OVERLAP: Digital autocrafting infrastructure. Repeated structural segment, not stored item capacity; compare cost per completed matrix rather than pricing every wall as a controller.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Structural wall of the assembler matrix; do not charge for a controller in every wall.
    // 
    // [High-Energy Grid] Skin an assembler frame as two service walls with sturdy panels, vibrant windows, buffered control, and a dense data trunk
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['2x extendedae:assembler_matrix_wall'], 'extendedae:assembler_matrix_frame', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:sturdy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:sturdy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:sturdy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:sturdy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_dense_cable']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'extendedae:assembler_matrix_frame'}})).loops(1).id('industrial_colonies:digital_storage/assembler_matrix_wall_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // WHAT IT DOES: Rope coupling component for the installed Simulated physical mechanism family.
    // USES / PROGRESSION / OVERLAP: Physical mechanism/ship construction branch. Exact connection limits and control behavior remain native-test questions; not a digital storage stabilizer.
    // REVIEW STATUS: Returned because your deferred note requests an explanation or second review. Recipe ingredients, output and machine type are unchanged. Use Parked for later only to set it aside.
    // 
    // Deferred re-review: Simulated rope-coupling component, produced as a batch in this card. Verify native attachment/rope use; do not infer function solely from the draft ingredients. Evidence: Installed identity / functional summary; exact balance not certified.
    // 
    // [Digital Logistics] Pair two finished rope eyes around a through-shaft, wrap the swivel in a TFMG Heavy Plate, secure it with paired service screws, and Railway-press a matched pair of load-rated couplings
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['2x simulated:rope_coupling'], 'simulated:rope_connector', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'simulated:rope_connector']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:shaft']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_plate']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'simulated:rope_connector'}})).loops(1).id('industrial_colonies:simulated/rope_coupling_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: A single Allthemodium–Vibranium reinforcement supports the repeatable quantum execution module. Preserve both execution lanes, calculation schedulers, rubber insulation and titanium shell. This module adds shared crafting threads; it is not item-storage capacity.
    // 
    // Existing approved layout and output retained.
    event.recipes.create.mechanical_crafting('advanced_ae:quantum_accelerator', ['ABBA', 'CDDC', 'EFFE', 'AGHA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'advanced_ae:quantum_processor',
        C: 'createaddition:electrum_wire',
        D: 'ae2:calculation_processor',
        E: 'tfmg:rubber_sheet',
        F: 'extendedae:concurrent_processor',
        G: 'allthemodium:vibranium_allthemodium_alloy_ingot',
        H: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_ae2/quantum_accelerator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // Deferred re-review: Advanced Ad Astra space-suit equipment. Potential late hazardous-environment protection. Confirm hazards and retained travel chain before costing it. Evidence: Installed equipment identity; configured protection not certified.
    // 
    // [Planetary Industry] Line Netherite leggings with Desh, form the doubled Ostrum pressure shell, and install paired gas cells, a service valve, and an insulated suit-power lead
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['ad_astra:netherite_space_pants'], 'minecraft:netherite_leggings', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:desh_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:gas_tank']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:gas_tank']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:insulated_wire']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:netherite_leggings'}})).loops(1).id('industrial_colonies:planetary/venus/netherite_space_pants')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // Deferred re-review: Advanced Ad Astra space-suit equipment. Potential late hazardous-environment protection. Confirm hazards and retained travel chain before costing it. Evidence: Installed equipment identity; configured protection not certified.
    // 
    // [Planetary Industry] Install the complete oxygen train in a Netherite chestplate, route its compact insulated suit-power lead and pressure services, then close the Desh-Ostrum shell
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    event.recipes.create.sequenced_assembly(['ad_astra:netherite_space_suit'], 'minecraft:netherite_chestplate', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:oxygen_gear']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:large_gas_tank']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:oxygen_distributor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_valve']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:etrionic_capacitor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:insulated_wire']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:desh_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:ostrum_plate']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:netherite_chestplate'}})).loops(1).id('industrial_colonies:planetary/venus/netherite_space_suit')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: One Unobtainium–Allthemodium reinforcement anchors the entanglement field. The rest of the approved frame, electronics and paired singularity layout stay intact. Its fourfold shared crafting-workspace effect warrants a late manufacturing gate.
    // 
    // Existing approved layout and output retained.
    event.recipes.create.mechanical_crafting('advanced_ae:data_entangler', ['ABBBA', 'CDEDC', 'FGHGF', 'IEJEI', 'AKLKA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'advanced_ae:quantum_processor',
        C: 'createaddition:electrum_wire',
        D: 'create:refined_radiance',
        E: 'ae2:quantum_entangled_singularity',
        F: 'tfmg:circuit_board',
        G: 'ae2:engineering_processor',
        H: 'ae2:calculation_processor',
        I: 'tfmg:rubber_sheet',
        J: 'mekanism:ultimate_control_circuit',
        K: 'tfmg:steel_frame',
        L: 'allthemodium:unobtainium_allthemodium_alloy_ingot'
      }).group('Chain 03 / 07 Advanced digital manufacturing').id('industrial_colonies:custom_progression/advanced_ae/data_entangler')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [High-Energy Grid] Review correction: additional 2 plastic sheet, 1 circuit board, 1 ingot osmium are installed before final closure. These additions strengthen the specific control, containment or structural function of this assembly.
    event.recipes.create.sequenced_assembly(['mekanism:upgrade_filter'], 'mekanism:module_base', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:filter']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_infused']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ingot_osmium']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:module_base'}})).loops(1).id('industrial_colonies:mekanism_components/upgrade_filter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-requested housing base: build a fresh MEGA item cell on one MEGA Item Cell Housing, then install the matching capacity component and the existing electronics, contacts and insulation. All remaining assembly ingredients, quantities, ordered steps, selected machines, loops and output are unchanged.
    event.recipes.create.sequenced_assembly(['megacells:item_storage_cell_256m'], 'megacells:mega_item_cell_housing', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_256m']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_dense_cable']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:unobtainium_vibranium_alloy_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance_casing']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_item_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_item_storage_cell_256m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Returned for review after your note that this recipe was changed by accident. Preserve the current Elite-circuit base, two atomic-alloy supports, Engineering Processor, magnetic sheet, second Elite circuit, etched board, two green and two pink semiconductors and four capacitors. Each counted part now has its own single-item operation; the earlier seal explicitly uses the Brass press like the final seal. No approval is inferred, and this remains a prerequisite that must be reviewed before exporting its downstream machines.
    event.recipes.create.sequenced_assembly(['mekanism:ultimate_control_circuit'], 'mekanism:elite_control_circuit', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:alloy_atomic']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:elite_control_circuit']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:elite_control_circuit'}})).loops(1).id('industrial_colonies:mekanism/ultimate_control_circuit')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('industrial_colonies')) {
    // October 16 back-review proposal: Use the exact molten-gold source already produced by the protected recovery cards; retain your 10 mB coating, empty-board base and all four assembly steps. A flowing fluid is not a source-fluid alias.
    // 
    // Existing approved layout and output retained.
    event.recipes.create.sequenced_assembly(['tfmg:coated_circuit_board'], 'tfmg:empty_circuit_board', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.base_filling('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', Fluid.of('createmetallurgy:molten_gold', 10)]),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.copper_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:empty_circuit_board'}})).loops(1).id('industrial_colonies:electronics/coated_circuit_board')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: One bronze bearing blank supports the central gearbox; the side shafts, steel mechanism, casing and screw pattern stay unchanged. Bronze now has a repeatable construction use without taxing every machine.
    // 
    // Existing approved layout and output retained.
    event.recipes.create.mechanical_crafting('tfmg:engine_gearbox', ['ABA', 'CDC', 'AEA'], {
        A: 'tfmg:screw',
        B: 'tfmg:steel_mechanism',
        C: 'create:shaft',
        D: 'tfmg:steel_casing',
        E: 'mekanism:ingot_bronze'
      }).id('industrial_colonies:priority/tfmg/engine_gearbox')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October 16 back-review proposal: A single Allthemodium–Vibranium anchor supports the late planetary field generator. Preserve the existing control and field geometry instead of replacing the design with a generic expensive ring.
    // 
    // Existing approved layout and output retained.
    event.recipes.create.mechanical_crafting('ad_astra:gravity_normalizer', ['ABBBA', 'CDEDC', 'FGHGF', 'CIJIC', 'ABKBA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'create:refined_radiance',
        C: 'tfmg:circuit_board',
        D: 'advanced_ae:quantum_processor',
        E: 'ae2:calculation_processor',
        F: 'nuclearcraft:iridium_ingot',
        G: 'nuclearcraft:coil_bscco',
        H: 'rocketnautics:magnetic_stabilizer',
        I: 'tfmg:rubber_sheet',
        J: 'mekanism:ultimate_control_circuit',
        K: 'allthemodium:vibranium_allthemodium_alloy_ingot'
      }).id('industrial_colonies:planetary/outpost/gravity_normalizer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [Quantum Engineering] Apply one existing Ice Dragon Blood item directly during sequenced assembly before final pressing. Consumed per chip as the cooling ingredient; no separate cooler or ongoing cooling mechanic is introduced. Saturn-moon resource gate still needs its exact existing item. Other assembly inputs retained pending review.
    event.recipes.create.sequenced_assembly(['advanced_ae:quantum_processor'], 'advanced_ae:printed_quantum_processor', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:printed_silicon']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:n_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:accumulation_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:accumulation_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:advanced_stress_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:high_voltage_capacitor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'modernfoundry:cobalt_reinforcement']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:allthemodium_ingot']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_alloy_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:p_semiconductor']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'iceandfire:ice_dragon_blood']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'advanced_ae:printed_quantum_processor'}})).loops(1).id('industrial_colonies:v3_ae2/quantum_processor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [Interstellar Escape] Review correction: additional 2 pellet antimatter, 2 titanium alloy sheet are installed before final closure. These additions strengthen the specific control, containment or structural function of this assembly.
    event.recipes.create.sequenced_assembly(['industrial_colonies:interstellar_warp_charge'], 'industrial_colonies:warp_charge_precursor', [
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'cosmowarp:moon_crystal']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ad_astra:calorite_plate']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:pellet_antimatter']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:pellet_antimatter']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:pellet_antimatter']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_alloy_sheet']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'industrial_colonies:warp_charge_precursor'}})).loops(2).id('industrial_colonies:interstellar/warp_charge')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Back-review consumption repair: each displayed group of parts is now installed through explicit single-item deployment steps. Native Create consumes one held item per activation, so a stack count on one operation did not enforce the displayed cost. Materials, total displayed bill, operation order, machine choices, output and loop count are retained.
    // 
    // [High-Energy Grid] Review correction: additional 2 entro ingot, 2 magnetic alloy sheet are installed before final closure. These additions strengthen the specific control, containment or structural function of this assembly.
    event.recipes.create.sequenced_assembly(['2x extendedae:assembler_matrix_glass'], 'extendedae:assembler_matrix_frame', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_cable']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:entro_ingot']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:entro_ingot']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'extendedae:assembler_matrix_frame'}})).loops(1).id('industrial_colonies:digital_storage/assembler_matrix_glass_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review revision: Use one Vibranium plate for the upper structural cap instead of a combined-alloy ingot. Keep the quantum-plate corners, tungsten span, titanium, osmiridium/iridium joints, 5 by 5 outline and four-frame yield. The scarce plate cost is shared across the four structural blocks. Existing items only; review proposal, no gameplay export.
    event.recipes.create.mechanical_crafting('4x nuclearcraft:neutronium_frame', ['ABCBA', 'D E F', 'CEGEC', 'F E D', 'AHCHA'], {
        A: 'advanced_ae:quantum_alloy_plate',
        B: 'createmetallurgy:tungsten_sheet',
        C: 'allthemodium:vibranium_plate',
        D: 'nuclearcraft:osmiridium_ingot',
        E: 'create:refined_radiance',
        F: 'rocketnautics:titanium_alloy_sheet',
        G: 'tfmg:heavy_machinery_casing',
        H: 'nuclearcraft:iridium_ingot'
      }).group('Late quantum - Kugelblitz Chamber').id('industrial_colonies:kugelblitz/neutronium_frame')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review revision: Use Vibranium plates at the four outside containment corners in place of the four combined-alloy ingots. Retain the full occupied 7 by 7 grid, every other quantum/electronic/frame ingredient and the user-selected central Antimatter Block exactly. Existing items only; review proposal, no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:chamber_terminal', ['ABBCBBA', 'DEFGFED', 'BFHIHFB', 'CGIJIGC', 'BFHKHFB', 'DEFGFED', 'ABBCBBA'], {
        A: 'allthemodium:vibranium_plate',
        B: 'create:refined_radiance',
        C: 'tfmg:steel_frame',
        D: 'advanced_ae:quantum_alloy_plate',
        E: 'createmechanisms:nuclear_mechanism',
        F: 'tfmg:circuit_board',
        G: 'electroenergetics:high_voltage_capacitor',
        H: 'mekanism:ultimate_control_circuit',
        I: 'advanced_ae:quantum_processor',
        J: 'allthecompressed:antimatter_block',
        K: 'ae2:engineering_processor'
      }).group('Late quantum - black hole engineering').id('industrial_colonies:custom_progression/nuclearcraft/chamber_terminal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES — Package Frogport: Package transfer station between nearby Chain Conveyors and the inventory beneath it. It sends outbound addressed packages onto the chain and collects packages matching its configured address. Pair it with Packagers and physical conveyors; it is neither digital storage nor a teleportation block.
    // 
    // WHERE IT FITS: It belongs with physical package logistics before bulk digital storage. Your native Create transport remains useful; this description does not authorize replacing a working default recipe.
    // 
    // REVIEW STATUS: You deferred this for a second pass. This return changes only the description; the original stored design, ingredients, counts, machines, outputs, UID and parameters are unchanged. The retained native/default option remains available as a review choice.
    // 
    // SOURCE: assets/create/lang/en_us.json: create.ponder.package_frogport.*; https://wiki.createmod.net/users/cc-tweaked-integration/logistics/package-frogport
    // 
    // PREVIOUS DESIGN NOTE:
    // [Digital Logistics] Build the Frogport as a package tray over a Vault buffer, Packager linkage, and two spring-loaded launch gears
    event.recipes.create.mechanical_crafting('create:package_frogport', [' A ', 'BCB', 'DED'], {
        A: 'create:packager',
        B: 'create:cogwheel',
        C: 'create:andesite_funnel',
        D: 'create:item_vault',
        E: 'create:andesite_casing'
      }).id('industrial_colonies:create_core/package_frogport')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES — Redstone Requester: A configured order terminal for Create logistics. Bind it to a Stock Link and configure the items and destination address; each redstone pulse requests that order through the logistics network. Packagers and transport still supply and move the physical items. It does not manufacture items or provide an ME inventory.
    // 
    // WHERE IT FITS: Useful for automated restocking and factory demand signals. It belongs beside Stock Links, Packagers and address-based transport; no need for quantum material merely because it sends requests.
    // 
    // REVIEW STATUS: You deferred this for a second pass. This return changes only the description; the original stored design, ingredients, counts, machines, outputs, UID and parameters are unchanged. The retained native/default option remains available as a review choice.
    // 
    // SOURCE: assets/create/lang/en_us.json: create.ponder.redstone_requester.*; https://wiki.createmod.net/users/changelogs/6.0.0
    // 
    // PREVIOUS DESIGN NOTE:
    // [Digital Logistics] Turn a Stock Link into an active requester with a Redstone Link, stress board, filter, and Brass command logic
    event.recipes.create.sequenced_assembly(['create:redstone_requester'], 'create:stock_link', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:redstone_link']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'appliedcreate:stress_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:package_filter']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:precision_mechanism']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:stock_link'}})).loops(1).id('industrial_colonies:create_core/redstone_requester')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHAT IT DOES — Steel Sliding Breechblock: A small cannon construction component installed into an incomplete Steel Sliding Breech; it is not a complete gun or a standalone processing machine. The finished sliding breech lets rotational power open the rear of a cannon for loading and must close unobstructed before firing. The mod trades quick rear loading against the pressure/strength limits of this breech design.
    // 
    // WHERE IT FITS: Keep the cannon manufacturing/casting and incomplete-block assembly chain intact. Your instruction to leave Big Cannons mostly native remains the default; this is an explanation-only return, not a new custom cannon gate.
    // 
    // REVIEW STATUS: You deferred this for a second pass. This return changes only the description; the original stored design, ingredients, counts, machines, outputs, UID and parameters are unchanged. The retained native/default option remains available as a review choice.
    // 
    // SOURCE: createbigcannons-5.11.7+mc.1.21.1.jar: assets/createbigcannons/lang/en_us.json, createbigcannons.ponder.cannon_mount/sliding_breech.*
    // 
    // PREVIOUS DESIGN NOTE:
    // [High-Energy Grid] Machine a solid TFMG steel block into a sliding breech with opposed rack gears, return spring, wear plate, and pinned service fastener
    // 
    // TECHNICAL CORRECTION: The two displayed cogwheels now use two separate deployment operations, so the full original bill is actually consumed. Materials, total quantities, machine tier and output are unchanged.
    event.recipes.create.sequenced_assembly(['createbigcannons:steel_sliding_breechblock'], 'tfmg:steel_block', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_cogwheel']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_cogwheel']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createbigcannons:recoil_spring']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_plate']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_block'}})).loops(1).id('industrial_colonies:big_cannons/steel_sliding_breechblock')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review revision: Keep the MEGA Item Cell Housing as both base and transitional workpiece, the matching capacity component and all existing electronics/insulation. Add one Refined Radiance containment cap immediately before final sealing; install and seal it on Refined Radiance machines. Earlier Railway routing operations are unchanged. This adds one physical Radiance piece and an actual Radiance capability gate. Existing items only; review proposal, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:item_storage_cell_64m'], 'megacells:mega_item_cell_housing', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_64m']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'advanced_ae:quantum_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:spatial_cell_component_128']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_dense_cable']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:matter_ball']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:unobtainium_plate']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_item_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_item_storage_cell_64m')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review revision: Keep the existing desktop as the electronics base, add one etched interposer, a lithium reserve, a small screen, plastic insulation and aluminum cover. Remove the separate full monitor and modem bills and both gold sheets. The plain pocket output does not include a wireless upgrade, so charging for one was misleading. Output remains one. Existing items only; review proposal, no gameplay export.
    event.recipes.create.sequenced_assembly(['computercraft:pocket_computer_normal'], 'computercraft:computer_normal', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:etched_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:quartz_vibrant_glass']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:aluminum_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'computercraft:computer_normal'}})).loops(1).id('industrial_colonies:computercraft/mobile/pocket_computer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review revision: Build one dense smart cable from four existing smart cables total, a single coated routing board, plastic dielectric, redstone signal contact and rubber jacket. Remove the calculation processor, four gold sheets and separate semiconductor/transistor/capacitor bank. Eight stages on Brass equipment replace the previous thirty-five-stage sixteen-output batch. The four-to-one cable bundle prevents the old one-smart-cable-per-dense-cable effective gain. Existing items only; review proposal, no gameplay export.
    event.recipes.create.sequenced_assembly(['ae2:fluix_smart_dense_cable'], 'ae2:fluix_smart_cable', [
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_cable']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_cable']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_cable']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'minecraft:redstone']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.brass_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'ae2:fluix_smart_cable'}})).loops(1).id('industrial_colonies:v3_ae2/fluix_dense_smart_cable_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review revision: This powered reaction vessel is a prerequisite for AdvancedAE quantum-material chemistry; it must be buildable before those products. Replace the asymmetric Allthemodium reinforcement and opposite lower heavy casing with two matched tungsten heat shields. Preserve the 5 by 5 vessel layout, upper heavy casings, pressure-reactor core, engineering controllers, condensers, vibration chambers, frames and output. This is another judgment proposal, not inferred approval. Existing items only; review proposal, no gameplay export.
    event.recipes.create.mechanical_crafting('advanced_ae:reaction_chamber', ['ABCBA', 'DEFED', 'CGHGC', 'IEFEI', 'ABCBA'], {
        A: 'ae2:quartz_glass',
        B: 'ae2:engineering_processor',
        C: 'ae2:fluix_dust',
        D: 'tfmg:heavy_machinery_casing',
        E: 'ae2:condenser',
        F: 'extendedae:machine_frame',
        G: 'ae2:vibration_chamber',
        H: 'mekanism:pressurized_reaction_chamber',
        I: 'createmetallurgy:tungsten_sheet'
      }).id('industrial_colonies:advanced_ae/reaction_chamber')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Chain support] Grind one FULL refined copper ingot into one existing NuclearCraft Copper Dust. This is powder forming for the native BSCCO assembler exact input, not ore crushing or an ore multiplier. Preserve the native Manufactory full-ingot1:1bill and240nominal processing setting while moving physical grinding to Create. Do not use raw copper or ore-grade crushed copper here; existing ore recovery is untouched.
    event.recipes.create.crushing(['mekanism:dust_copper'], 'minecraft:copper_ingot').processingTime(240).id('industrial_colonies:review/processing/refined_copper_powder')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('tfmg')) {
    // [Capacity/chemistry proposal] Four original chromium-concentrate dust recover90mB chromium plus10mB slag on the same three powered graphite electrodes in a Fireproof Vat. The core user-selected4dust→90mB yield,200nominal work ticks and existing equipment remain. Remove the explicitly unapproved draft coke/limesand add-ons that exceeded native four-solid capacity, and remove their unsupported CO2 exhaust. This is an ancillary bill change, not a claim the six-input bill was preserved. Protected Material Processing remains byte-exact. Equipment must be operational; physical attachment/heat/output custody and alternative furnace/melting closures remain pre-export checks.
    event.custom({ type: 'tfmg:vat_machine_recipe', ingredients: [{ item: 'nuclearcraft:chromium_dust' }, { item: 'nuclearcraft:chromium_dust' }, { item: 'nuclearcraft:chromium_dust' }, { item: 'nuclearcraft:chromium_dust' }], results: [{ id: 'modernfoundry:molten_chromium', amount: 90 }, { id: 'tfmg:molten_slag', amount: 10 }], allowed_vat_types: ['tfmg:firebrick_lined_vat'], machines: ['tfmg:graphite_electrode', 'tfmg:graphite_electrode', 'tfmg:graphite_electrode'], heat_level: 0, min_size: 3, processing_time: 200 }).id('industrial_colonies:ore_recovery/chromium/vat')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('tfmg')) {
    // [Back review] Granulate90mB of the existing hard-carbon melt under1B ordinary NuclearCraft nitrogen in an8-block Fireproof Vat centrifuge, producing one existing powder. Nitrogen gives a protected-atmosphere process role rather than unexplained water cleaning. It is a game abstraction, not a claim that this composite is an ordinary real melt. Normal nitrogen avoids a new cryogenic bootstrap requirement.
    event.custom({ type: 'tfmg:vat_machine_recipe', ingredients: [{ type: 'neoforge:single', fluid: 'nuclearcraft:molten_hard_carbon', amount: 90 }, { type: 'neoforge:single', fluid: 'nuclearcraft:nitrogen', amount: 1000 }], results: [{ id: 'nuclearcraft:hard_carbon_dust' }], allowed_vat_types: ['tfmg:firebrick_lined_vat'], machines: ['tfmg:centrifuge'], heat_level: 0, min_size: 8, processing_time: 400 }).id('industrial_colonies:review/exotics/hard_carbon_atomization')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('tfmg')) {
    // [Back review] Granulate90mB of the existing SiC/SiC CMC game fluid under1B ordinary NuclearCraft nitrogen in an8-block Fireproof Vat centrifuge, producing one existing powder. Preserve material yield; no new wafer, dust, gas chemical or vapor is introduced. This is composite-powder process design, not a literal real liquid-SiC chemistry claim.
    event.custom({ type: 'tfmg:vat_machine_recipe', ingredients: [{ type: 'neoforge:single', fluid: 'nuclearcraft:molten_sic_sic_cmc', amount: 90 }, { type: 'neoforge:single', fluid: 'nuclearcraft:nitrogen', amount: 1000 }], results: [{ id: 'nuclearcraft:sic_sic_cmc_dust' }], allowed_vat_types: ['tfmg:firebrick_lined_vat'], machines: ['tfmg:centrifuge'], heat_level: 0, min_size: 8, processing_time: 400 }).id('industrial_colonies:review/exotics/sic_sic_cmc_atomization')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review revision: Replace the two full osmium ingots with two ordinary iron reinforcement sheets. Keep the steel vessel, seals, liner/manifold or valve, basic controller, machine selections, output and stage order. Osmium no longer forms a bulk armor tax on a basic utility tank. Existing items only; review proposal, no gameplay export.
    // 
    // October16 whole-pack research proposal: Starter chemical hardware uses reachable Weathered Iron structure and Copper/Brass electronic fitting, avoiding the Industrial Iron Press -> HDPE -> first chemistry tooling loop. Every material, quantity, output and stage remains unchanged; later chemical hardware stays advanced.
    event.recipes.create.sequenced_assembly(['mekanism:basic_chemical_tank'], 'tfmg:steel_fluid_tank', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:iron_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:iron_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_pressurized_tube']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_control_circuit']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_fluid_tank'}})).loops(1).id('industrial_colonies:mekanism_components/basic_chemical_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review revision: Replace the two full osmium ingots with two ordinary iron reinforcement sheets. Keep the steel vessel, seals, liner/manifold or valve, basic controller, machine selections, output and stage order. Osmium no longer forms a bulk armor tax on a basic utility tank. Existing items only; review proposal, no gameplay export.
    // 
    // October16 whole-pack research proposal: Starter chemical hardware uses reachable Weathered Iron structure and Copper/Brass electronic fitting, avoiding the Industrial Iron Press -> HDPE -> first chemistry tooling loop. Every material, quantity, output and stage remains unchanged; later chemical hardware stays advanced.
    event.recipes.create.sequenced_assembly(['mekanism:basic_fluid_tank'], 'tfmg:steel_fluid_tank', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:iron_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:iron_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_fluid_valve']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_control_circuit']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_fluid_tank'}})).loops(1).id('industrial_colonies:mekanism_components/basic_fluid_tank')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // WHOLE-PACK BACK-REVIEW — One formed copper contact segment replaces one of the two identical processors; keep the other control package and the existing rotor/support silhouette. Copper contacts, shaft, magnet and insulated lower drive each have a role. Do not insert Alternator Brushes here: their native construction already requires this commutator.
    event.recipes.create.mechanical_crafting('electroenergetics:commutator', [' ABA ', 'ACDEA', 'FBGBF', 'HIIIH'], {
        A: 'tfmg:copper_wire',
        B: 'create:shaft',
        C: 'create:copper_sheet',
        D: 'tfmg:magnet',
        E: 'ae2:calculation_processor',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:electric_motor',
        H: 'immersiveengineering:plate_iron',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:electroenergetics/commutator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Pressure-form four modular reservoir sections from one real tank, heavy plate, steel manifold pipe, osmium ribs, and a rubber gasket.
    // 
    // October16 whole-pack research proposal: Starter chemical hardware uses reachable Weathered Iron structure and Copper/Brass electronic fitting, avoiding the Industrial Iron Press -> HDPE -> first chemistry tooling loop. Every material, quantity, output and stage remains unchanged; later chemical hardware stays advanced.
    event.recipes.industrial_colonies.weathered_iron_compacting(['4x mekanism:dynamic_tank'], ['tfmg:steel_fluid_tank', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:heavy_plate', 'tfmg:steel_pipe', 'tfmg:steel_pipe', 'mekanism:ingot_osmium', 'mekanism:ingot_osmium', 'tfmg:rubber_sheet']).id('industrial_colonies:mekanism_components/dynamic_tank_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [High-Energy Grid] Assemble a true electrolysis cell from opposed TFMG electrodes, a pumped chemical vessel, transformer, separator core, and controller.
    // 
    // October16 whole-pack research proposal: Starter chemical hardware uses reachable Weathered Iron structure and Copper/Brass electronic fitting, avoiding the Industrial Iron Press -> HDPE -> first chemistry tooling loop. Every material, quantity, output and stage remains unchanged; later chemical hardware stays advanced.
    event.recipes.create.sequenced_assembly(['mekanism:electrolytic_separator'], 'tfmg:steel_frame', [
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:electrolytic_core']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_chemical_vat']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_electrode']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:zinc_electrode']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:mechanical_pump']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transformer']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:basic_control_circuit']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_fluid_tank']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:steel_frame'}})).loops(1).id('industrial_colonies:mekanism_pre_nuclear/electrolytic_separator')
  }
})

ServerEvents.recipes(event => {
  // WHOLE-PACK BACK-REVIEW — A carbon resistive body now sits between the two electrical terminals, with the existing cast-iron thermal supports above and below. Graphite Dust comes from the protected Graphite Rock crushing route before Industrial Iron; no new graphite supplier, processor tax or shape change.
  event.shaped('electroenergetics:resistor', [' A ', 'BCB', ' A '], {
      A: 'tfmg:cast_iron_sheet',
      B: 'electroenergetics:connector',
      C: 'nuclearcraft:graphite_dust'
    }).id('industrial_colonies:grid/resistor')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-pack review tweak: retain the reviewed fan retrofit and every original fitted subsystem. Add one light titanium rotor support and refractory tungsten hub. Fit the advanced control/processor and new inserts with earlier Brass precision tooling; the original Weathered press still seals the first Industrial Iron machine, avoiding a self-tooling loop. Canonical Ti/W ingots only; no ingot-to-plate shortcut is implied. Intended Ti casting ownership remains a separate qualification hold. Review proposal only; no gameplay export.
    event.recipes.create.sequenced_assembly(['createcasing:industrial_iron_encased_fan'], 'createcasing:weathered_iron_encased_fan', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:industrial_iron_block']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_machinery_casing']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:hdpe_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_plate']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:propeller']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_ingot']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createmetallurgy:tungsten_ingot']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createcasing:weathered_iron_encased_fan'}})).loops(1).id('industrial_colonies:manufacturing/industrial_iron/fan')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Deferred re-review: Quantum Computer expansion multiplying shared co-processing capability.
    // 
    // Review revision: Separate concurrent scheduling lanes share calculation and logic control over an ultimate bus; designed as parallel crafting execution hardware. Existing pack items; proposed editor recipe, no gameplay export.
    // Existing item; no gameplay export or new mechanic installed. Exact costs/bootstrap remain proposals.
    // 
    // October16 whole-pack research proposal: The existing Computing Mechanism occupies the scheduler's central logic position. It provides a programmed calculation/control assembly for the parallel lanes; the approved five-by-five layout and all other parts remain.
    event.recipes.create.mechanical_crafting('advanced_ae:quantum_multi_threader', ['ABCBA', 'DCDCD', 'EFGFE', 'HIJIH', 'AKKKA'], {
        A: 'rocketnautics:titanium_alloy_sheet',
        B: 'advanced_ae:quantum_processor',
        C: 'ae2:calculation_processor',
        D: 'createaddition:electrum_wire',
        E: 'tfmg:circuit_board',
        F: 'ae2:engineering_processor',
        G: 'createmechanisms:computing_mechanism',
        H: 'tfmg:rubber_sheet',
        I: 'mekanism:ultimate_control_circuit',
        J: 'extendedae:concurrent_processor',
        K: 'tfmg:steel_frame'
      }).group('Chain 03 / 07 Advanced digital manufacturing').id('industrial_colonies:custom_progression/advanced_ae/quantum_multi_threader')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review pressing refinement: Seat the Industrial Iron body block, then press the Heavy Machinery Casing onto it before installing any electronics. These two forming operations use the existing Weathered Iron Press so the first Industrial Iron Deployer never requires itself or another Industrial Iron machine. Preserve all twelve installed parts, their existing Copper/Brass electronic operations, their order and the final Weathered Iron press. Existing items only; review proposal, no gameplay export.
    event.recipes.create.sequenced_assembly(['createcasing:industrial_iron_deployer'], 'createcasing:weathered_iron_deployer', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:industrial_iron_block']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_machinery_casing']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_plate']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:brass_hand']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transistor_item']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:titanium_ingot']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:tungsten_ingot']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:silicon_ingot']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createcasing:weathered_iron_deployer'}})).loops(1).id('industrial_colonies:manufacturing/industrial_iron/deployer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Post-review pressing refinement: Seat the fitted Allthemodium containment plate with a Refined Radiance Press immediately after its installation and before the rubber seals. Keep the MEGA Item Cell Housing base, every fitted component, all deployment machine choices, the physical Radiance cap and the separate final Radiance sealing operation. Existing items only; review proposal, no gameplay export.
    event.recipes.create.sequenced_assembly(['megacells:item_storage_cell_4m'], 'megacells:mega_item_cell_housing', [
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'megacells:cell_component_4m']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:fluix_smart_dense_cable']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:lithium_charge']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:laminated_magnetic_alloy_block']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'allthemodium:allthemodium_plate']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:copper_wire']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance']),
        event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'megacells:mega_item_cell_housing'}})).loops(1).id('industrial_colonies:v3_ae2/mega_item_storage_cell_4m')
  }
})

ServerEvents.recipes(event => {
  // CUSTOM DRAFT - Pair of compact functional expansion boards; shared circuitry keeps repeated upgrades practical. Uses existing Personal Recipes outputs where specified. No gameplay export; costs and survival access await review.
  // 
  // October16 whole-pack research proposal: Two Advanced Card substrates become two partitioning cards; the central Calculation Processor divides configured storage types. Existing wire, printed silicon, cross shape and output of two remain.
  event.shaped('ae2:equal_distribution_card', [' A ', 'BCB', ' D '], {
      A: 'createaddition:electrum_wire',
      B: 'ae2:advanced_card',
      C: 'ae2:calculation_processor',
      D: 'ae2:printed_silicon'
    }).group('07 Digital expansion cards').id('industrial_colonies:custom_progression/ae2/equal_distribution_card')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-pack review tweak: replace only the ordinary viewing pane with existing shielded Fission Reactor Glass. Keep the approved5x5 irradiation channel, coils, lead shielding, monitoring electronics and all other quantities. The glass inherits the earlier casing gate and does not require an Irradiator to make. Review proposal only; no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:irradiator', ['ABABA', 'ACDCA', 'AEFEA', 'AGCGA', 'HIIIH'], {
        A: 'immersiveengineering:plate_lead',
        B: 'tfmg:steel_pipe',
        C: 'tfmg:electromagnetic_coil',
        D: 'nuclearcraft:fission_reactor_glass',
        E: 'mekanism:ingot_refined_obsidian',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board',
        H: 'tfmg:nickel_sheet',
        I: 'tfmg:steel_frame'
      }).group('06 Nuclear machines').id('industrial_colonies:custom_progression/nuclearcraft/irradiator')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-pack review tweak: reuse a complete regular Fission Reactor Controller as the lower control module before constructing the MSR controller. Keep the approved full5x5, central Steel Frame, uranium/nickel/electrum shielding, wiring, boards, Radiance, nuclear mechanisms and gold contacts. This enforces prior fission-controller construction; it does not certify an operated reactor or rewrite native fuel chemistry. Review proposal only; no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:msr_controller', ['ABCBA', 'DEFED', 'GHIHG', 'DJKJD', 'ABCBA'], {
        A: 'immersiveengineering:plate_uranium',
        B: 'immersiveengineering:plate_nickel',
        C: 'immersiveengineering:plate_electrum',
        D: 'createaddition:electrum_wire',
        E: 'createmechanisms:nuclear_mechanism',
        F: 'ae2:engineering_processor',
        G: 'create:refined_radiance',
        H: 'tfmg:circuit_board',
        I: 'tfmg:steel_frame',
        J: 'minecraft:gold_nugget',
        K: 'nuclearcraft:fission_reactor_controller'
      }).group('Nuclear - post-fission MSR').id('industrial_colonies:custom_progression/nuclearcraft/msr_controller')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Shielded reactor I/O bracket: lead cap, carbon-facing insulation, tough-alloy arms and opposed Servo handling around the existing Fission Casing. Expand the disliked two Advanced Plates into their actual two lead, two tough-alloy, two graphite and one redstone inputs, rather than inventing a composite item or lowering them to generic steel. Native four additional Tough Alloy plate-equivalents become existing ingot reinforcement. This inherits the approved casing gate. Material quantities preserved; old plate-forming time/energy is not claimed equivalent. Review proposal only; no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:fission_reactor_port', ['ABBA', 'CDEC', 'FAAF', 'A  A'], {
        A: 'nuclearcraft:tough_alloy_ingot',
        B: 'immersiveengineering:plate_lead',
        C: 'nuclearcraft:graphite_dust',
        D: 'nuclearcraft:fission_reactor_casing',
        E: 'minecraft:redstone',
        F: 'nuclearcraft:servo'
      }).id('industrial_colonies:back_review/nuclearcraft/fission_reactor_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // In-reactor irradiation target: Boron corner shielding, lead cap and graphite-facing material channel, with tough-alloy support and two Servo handlers around the item chest. This is the interior neutron/moderator-line part, distinct from the standalone Irradiator. Preserve the native two Advanced Plates as two lead, two tough-alloy, two graphite and one redstone instead of their disliked plate icons. Four Boron ingots retain the native plate metal amount. No controller electronics or Quantum materials on every interior target. Material quantities preserved; old forming energy/time remains a separate issue. Review proposal only; no gameplay export.
    event.recipes.create.mechanical_crafting('nuclearcraft:fission_reactor_irradiation_chamber', ['ABBA', 'CDEC', 'FDGF', 'A  A'], {
        A: 'nuclearcraft:boron_ingot',
        B: 'immersiveengineering:plate_lead',
        C: 'nuclearcraft:graphite_dust',
        D: 'nuclearcraft:tough_alloy_ingot',
        E: 'minecraft:chest',
        F: 'nuclearcraft:servo',
        G: 'minecraft:redstone'
      }).id('industrial_colonies:back_review/nuclearcraft/fission_reactor_irradiation_chamber')
  }
})

ServerEvents.recipes(event => {
  // Retain the native three-by-three connector cross and two-output batch: four Lead Plates, FOUR existing Fusion Casings and one AE2 Logic Processor. The processor replaces the disliked NuclearCraft Basic Electric Circuit for alignment/control instrumentation; it does not turn this axial structural arm into an independent processor. Existing fusion casings already carry osmiridium/iridium/tungsten/Radiance cost. Review proposal only; no gameplay export.
  event.shaped('2x nuclearcraft:fusion_reactor_connector', ['ABA', 'BCB', 'ABA'], {
      A: 'immersiveengineering:plate_lead',
      B: 'nuclearcraft:fusion_reactor_casing',
      C: 'ae2:logic_processor'
    }).id('industrial_colonies:back_review/nuclearcraft/fusion_reactor_connector')
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Copper Leg Thrusters: Weathered Iron tooling fits the two nozzles, pressure-vessel shell, hose coupling and pump, then crimps the mechanical harness. Copper tooling installs the coated board and retained Ultimate Control Circuit. Weathered tooling fits the rubber seal and closes the pressure joints. The entire original paid bill and late flight interlock remain; only operation assignment and one structural crimp stage change. Native flight draws air from a separately worn Create backtank, not the recipe tank; this card does not establish flight range, fuel balance or worn-data preservation.
    event.recipes.create.sequenced_assembly(['rocketnautics:copper_leg_thrusters'], 'minecraft:iron_leggings', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:copper_nozzle']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:cast_iron_fluid_tank']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:hose_anchor']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:electric_pump']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:copper_nozzle']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:coated_circuit_board']),
        event.recipes.industrial_colonies.copper_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:iron_leggings'}})).loops(1).id('industrial_colonies:space_hardware/copper_leg_thrusters')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Hose Anchor pair: the middle row is a straight pipe, rubber seal and isolation-valve coupling. Two formed steel mounting cheeks and their screws attach the socket to a wall. No electric pump or four heavy armor plates: the installed anchor equalizes linked hose fluid/pressure and is not a pumping station. Four columns keep the flow path separate from the compact mounting edge. Output remains two anchors; wearable flight control remains on the separate thruster harness.
    event.recipes.create.mechanical_crafting('2x rocketnautics:hose_anchor', ['  AB', 'CDEC', '  AB'], {
        A: 'immersiveengineering:plate_steel',
        B: 'tfmg:screw',
        C: 'tfmg:industrial_pipe',
        D: 'tfmg:rubber_sheet',
        E: 'tfmg:steel_fluid_valve'
      }).id('industrial_colonies:space/propulsion/hose_anchor')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Stamp an existing logic press pattern into one iron block with the Brass Press. The two output slots are the new press and the returned master, not two free copies. An original press must first be recovered from a meteorite. These standard dies carry no stored cargo; arbitrary renamed/component-bearing tool round trips are not qualified by this card.
    // 
    // October16 review four: Use the requested compacting process. One iron block and one master press yield one newly stamped copy plus the returned master; net gain remains exactly one press.
    event.recipes.industrial_colonies.brass_compacting(['ae2:logic_processor_press'], ['minecraft:iron_block', 'ae2:logic_processor_press']).group('07 Digital fabrication / native tool bridges').id('industrial_colonies:electronics/press_cloning/logic')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Stamp an existing calculation press pattern into one iron block with the Brass Press. The two output slots are the new press and the returned master, not two free copies. An original press must first be recovered from a meteorite. These standard dies carry no stored cargo; arbitrary renamed/component-bearing tool round trips are not qualified by this card.
    // 
    // October16 review four: Use the requested compacting process. One iron block and one master press yield one newly stamped copy plus the returned master; net gain remains exactly one press.
    event.recipes.industrial_colonies.brass_compacting(['ae2:calculation_processor_press'], ['minecraft:iron_block', 'ae2:calculation_processor_press']).group('07 Digital fabrication / native tool bridges').id('industrial_colonies:electronics/press_cloning/calculation')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Stamp an existing engineering press pattern into one iron block with the Brass Press. The two output slots are the new press and the returned master, not two free copies. An original press must first be recovered from a meteorite. These standard dies carry no stored cargo; arbitrary renamed/component-bearing tool round trips are not qualified by this card.
    // 
    // October16 review four: Use the requested compacting process. One iron block and one master press yield one newly stamped copy plus the returned master; net gain remains exactly one press.
    event.recipes.industrial_colonies.brass_compacting(['ae2:engineering_processor_press'], ['minecraft:iron_block', 'ae2:engineering_processor_press']).group('07 Digital fabrication / native tool bridges').id('industrial_colonies:electronics/press_cloning/engineering')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Stamp an existing silicon press pattern into one iron block with the Brass Press. The two output slots are the new press and the returned master, not two free copies. An original press must first be recovered from a meteorite. These standard dies carry no stored cargo; arbitrary renamed/component-bearing tool round trips are not qualified by this card.
    // 
    // October16 review four: Use the requested compacting process. One iron block and one master press yield one newly stamped copy plus the returned master; net gain remains exactly one press.
    event.recipes.industrial_colonies.brass_compacting(['ae2:silicon_press'], ['minecraft:iron_block', 'ae2:silicon_press']).group('07 Digital fabrication / native tool bridges').id('industrial_colonies:electronics/press_cloning/silicon')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Press the Entro crystal pattern into a nickel-faced Concurrent die. Three Eyes align the four crystal faces against the consumed Silicon Press pattern; one nickel sheet supplies the actual wear face. The first die does not require a Crystal Assembler Frame or Concurrent Processor. Every repeated native ingredient occupies its own slot so the installed compiler preserves the quantity.
    // 
    // October16 review four: Retain the first-tool-safe Brass Press and native three Eyes, four Entro Crystals and consumed Silicon Press; add one existing nickel sheet as a durable die face. This stays a small tooling operation rather than a Crystal Assembler prerequisite cycle.
    event.recipes.industrial_colonies.refined_radiance_compacting(['extendedae:concurrent_processor_press'], ['minecraft:ender_eye', 'minecraft:ender_eye', 'minecraft:ender_eye', 'extendedae:entro_crystal', 'extendedae:entro_crystal', 'extendedae:entro_crystal', 'extendedae:entro_crystal', 'ae2:silicon_press', 'tfmg:nickel_sheet']).group('07 Digital fabrication / native tool bridges').id('industrial_colonies:electronics/concurrent_processor_press')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Forge the Accumulation Processor Press on a Refined Radiance Press. Singularity provides the dense imprint core; the two existing AE2 master patterns define its calculation and engineering geometry. This is late precision tooling, not a processor assembly. No return output is present: the two precursor presses are consumed, and separate iron-block cloning can preserve their originals.
    // 
    // October16 review four: Apply the requested Refined Radiance machine family, preserving the exact native Singularity, Calculation Press and Engineering Press bill. Both precursor dies remain consumed.
    event.recipes.industrial_colonies.refined_radiance_compacting(['megacells:accumulation_processor_press'], ['ae2:singularity', 'ae2:calculation_processor_press', 'ae2:engineering_processor_press']).group('07 Digital fabrication / native tool bridges').id('industrial_colonies:electronics/accumulation_processor_press')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Shadow housing batch: the earlier Refined Radiance Press bonds four existing radiant housings and four Shadow Steel pieces around one shared finished Vibranium reinforcement plate. The rare reinforcement is split across four output casings rather than charging Unobtainium for ordinary machine housing. All nine inputs remain separate real basin slots, preserving the shown cost in the installed exporter. The approved Vibranium Plate uses earlier Radiance tooling, so the first Shadow casing does not require a Shadow machine. Four casings per batch; no new item.
    event.recipes.industrial_colonies.refined_radiance_compacting(['4x create:shadow_steel_casing'], ['create:refined_radiance_casing', 'create:refined_radiance_casing', 'create:refined_radiance_casing', 'create:refined_radiance_casing', 'create:shadow_steel', 'create:shadow_steel', 'create:shadow_steel', 'create:shadow_steel', 'allthemodium:vibranium_plate']).id('industrial_colonies:manufacturing/shadow_steel/casing')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Borax Rock supplies borax flux: crush one existing Borax Rock into one existing Borax Dust using the established Crushing Wheels route. This is a one-output correction proposal to the old unreviewed Borax Rock draft, which accidentally produced elemental Boron Dust. It replaces the rejected End Stone detour rather than adding a second rock source. The protected Material Processing card remains unchanged for comparison. Boron metal and Germanium production are separate chemistry/source questions; neither is claimed as a free byproduct here.
    event.recipes.create.crushing(['nuclearcraft:borax_dust'], 'industrial_colonies:borax_rock').processingTime(250).id('industrial_colonies:crushing_review/industrial_colonies/borax_rock')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Tungsten powder stock: dry-pulverize one already refined Tungsten Ingot into one Tungsten Dust in Create Crushing Wheels. This replaces the rejected molten-metal/helium centrifuge; no liquid is mislabeled as powder and no inert gas is charged for ordinary grinding. The installed NuclearCraft Manufactory already defines tungsten ingot to dust at one-to-one; this assigns that operation to the pack's Create grinding tools. It consumes refined metal, never raw ore or crushed raw tungsten, so the existing ore-recovery yields remain upstream.
    event.recipes.create.crushing(['nuclearcraft:tungsten_dust'], 'createmetallurgy:tungsten_ingot').processingTime(400).group('Exotic metallurgy / powder metallurgy and reinforcement').id('industrial_colonies:review/processing/tungsten_powder_atomization')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Corrected output: two Reinforced Alloys + one Chromatic Compound + one Refined Radiance + one Osmiridium Ingot + one Enriched Refined Obsidian -> one Atomic Alloy. Low Heated Industrial Iron Mixer. Enriched Refined Obsidian is the prepared INPUT produced by the preceding Mekanism Infuser, never the mixing output. Reinforced matrix, radiant/chromatic phase, osmium-iridium reinforcement and refractory enriched obsidian retain distinct roles. No custom item. Native Create rotation/heat semantics. Radiance remains upstream of Atomic; its earlier Atomic-to-Reinforced cycle correction is preserved.
    event.recipes.industrial_colonies.refined_radiance_mixing(['mekanism:alloy_atomic'], ['mekanism:alloy_reinforced', 'mekanism:alloy_reinforced', 'create:chromatic_compound', 'create:refined_radiance', 'nuclearcraft:osmiridium_ingot', 'mekanism:enriched_refined_obsidian', 'mekanism:dust_uranium']).group('Mekanism Alloys / 4 Atomic Alloy').id('industrial_colonies:material_processing/atomic_composite_feed').merge({heat_requirement: 'lowheated'})
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Corrected output: one Enriched Diamond + one Industrial Iron Block + one Cobalt Ingot + one Infused Alloy -> one Reinforced Alloy, Heated Industrial Iron Press. Enriched Diamond is an INPUT made in the preceding Infuser step, never the compacting output. Industrial Iron provides the matrix, cobalt the binder, diamond reinforcement and Infused Alloy the electronic core. Native cheap Industrial Iron block stonecutting alone is not a gate; the tier-specific press is required. Retains the user-liked Industrial Iron Block. Native Create rotation/heat semantics, no invented FE or duration.
    event.recipes.industrial_colonies.industrial_iron_compacting(['mekanism:alloy_reinforced'], ['mekanism:enriched_diamond', 'create:industrial_iron_block', 'nuclearcraft:cobalt_ingot', 'mekanism:alloy_infused']).heated().group('Mekanism Alloys / 2 Reinforced Alloy').id('industrial_colonies:material_processing/diamond_reinforcement_feed')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('mekanism')) {
    // Corrected production direction: Metallurgic Infuser makes one Enriched Diamond from one Diamond and 40 Carbon infusion units, consumed once per operation. Carbon enrichment is a proposed pack process, not a native stock recipe or real diamond synthesis claim. Native Infuser base duration/energy and upgrades apply. The Enriched Diamond ITEM then goes into the Industrial Iron compacting recipe to make Reinforced Alloy. Enriched Diamond is no longer made by compacting. Existing conversion of Enriched Diamond into Diamond infusion remains available for other consumers.
    event.custom({ type: 'mekanism:metallurgic_infusing', item_input: { count: 1, item: 'minecraft:diamond' }, chemical_input: { amount: 40, chemical: 'mekanism:carbon' }, output: { count: 1, id: 'mekanism:enriched_diamond' }, per_tick_usage: false }).id('industrial_colonies:material_processing/reinforced_alloy_infusion')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-directed Chromatic Compound mixture: three Chromium Dust + one Titanium Alloy + two Reinforced Alloy + 1,000 mB NuclearCraft Sulfuric Acid yield two Chromatic Compound. Industrial Iron Mixer and basin, Low Heated. Ingredients, quantities, UID and recipe ID preserved from the user-approved vat card. Replaces the vat/electrode operation; no graphite electrodes or vat-size requirement. This is a pack mixture proposal, not real chemical stoichiometry. No gameplay export.
    event.recipes.industrial_colonies.industrial_iron_mixing(['2x create:chromatic_compound'], ['nuclearcraft:chromium_dust', 'nuclearcraft:chromium_dust', 'nuclearcraft:chromium_dust', 'rocketnautics:titanium_alloy', 'mekanism:alloy_reinforced', 'mekanism:alloy_reinforced', Fluid.of('nuclearcraft:sulfuric_acid', 1000)]).group('Refined Radiance / 2 Chromatic synthesis').id('industrial_colonies:nuclear/chromatic_compound').merge({heat_requirement: 'lowheated'})
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('mekanism')) {
    // Corrected production direction: one Refined Obsidian Dust + 40 Diamond infusion units -> one Enriched Refined Obsidian in the Metallurgic Infuser. Infusion consumed once per operation. Existing Enriched Diamond converts to 80 Diamond infusion units and can supply two operations here. The Enriched Refined Obsidian ITEM is consumed by the following Radiance/Chromatic/Osmiridium mixing recipe to make Atomic Alloy. It is not the mixing output. Native Infuser base cycle/energy applies; previous PRC settings remain withdrawn. This is a pack-specific enrichment recipe, not the native Enrichment Chamber route.
    event.custom({ type: 'mekanism:metallurgic_infusing', item_input: { count: 1, item: 'mekanism:dust_refined_obsidian' }, chemical_input: { amount: 40, chemical: 'mekanism:diamond' }, output: { count: 1, id: 'mekanism:enriched_refined_obsidian' }, per_tick_usage: false }).id('industrial_colonies:material_processing/atomic_alloy_pressure_bonding')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Shadow saw: Vibranium working edges and the tungsten crown surround a Tungsten Carbide wear guide above the retained Radiance spindle. A Concurrent Processor coordinates the twin drives and precision contacts, replacing Quantum positioning control; completed boards, Ultimate Control and rubber isolation remain. Existing Tungsten Carbide stock has a protected Material Processing producer and the Concurrent chain uses earlier tools. Thus the scarce cutting surfaces, Shadow housings and previous Radiance Saw keep the machine above Radiance without requiring the Quantum parts it will later machine. Same 5x5 geometry, 23 fitted parts and output; no Unobtainium or antimatter.
    event.recipes.create.mechanical_crafting('createcasing:shadow_steel_mechanical_saw', [' ABA ', 'CDEDC', 'FGHGF', 'CIJIC', 'KLMLK'], {
        A: 'allthemodium:vibranium_plate',
        B: 'createmetallurgy:tungsten_sheet',
        C: 'create:shadow_steel_casing',
        D: 'tfmg:rubber_sheet',
        E: 'nuclearcraft:tungsten_carbide_ingot',
        F: 'nuclearcraft:osmiridium_ingot',
        G: 'tfmg:electric_motor',
        H: 'createcasing:refined_radiance_mechanical_saw',
        I: 'tfmg:circuit_board',
        J: 'extendedae:concurrent_processor',
        K: 'tfmg:heavy_plate',
        L: 'mekanism:ultimate_control_circuit',
        M: 'tfmg:steel_frame'
      }).id('industrial_colonies:manufacturing/shadow_steel/saw')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Shadow Mixer upgrade: a completed-board Concurrent control cabinet sits over the motor and paired osmiridium pivots, supported by two steel brace rods. Two finished Vibranium wear plates and rubber vibration bushings seat the existing Refined Radiance Mixer. The lower Shadow housing carries one straight Create shaft down to the actual Sturdy Whisk working head. Four already-approved Shadow housings are consumed, not newly invented casings. Its predecessor, bearings and advanced controller remain pre-Quantum; the approved Vibranium Plate uses earlier Radiance tools. This tool is needed after the first pure-metal refining line, not to make its own first Vibranium. Casing identity is a processing capability, not a claim of automatically increased SU or FE demand.
    event.recipes.create.mechanical_crafting('createcasing:shadow_steel_mixer', ['ABCBA', 'DEFED', 'GHIHG', ' AJA ', '  K  '], {
        A: 'create:shadow_steel_casing',
        B: 'tfmg:circuit_board',
        C: 'extendedae:concurrent_processor',
        D: 'nuclearcraft:osmiridium_ingot',
        E: 'immersiveengineering:stick_steel',
        F: 'tfmg:electric_motor',
        G: 'tfmg:rubber_sheet',
        H: 'allthemodium:vibranium_plate',
        I: 'createcasing:refined_radiance_mixer',
        J: 'create:shaft',
        K: 'createmetallurgy:sturdy_whisk'
      }).group('Exotic metallurgy / required precision machinery').id('industrial_colonies:manufacturing/shadow_steel/mixer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-card review: Cast-iron ring and opposed propeller sections surround the retained fan; the shaft and andesite mounts sit below it. Removes the repeated steel-frame/heavy-plate template and late steel-mechanism dependency. Existing pack items; proposed construction card, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:weathered_iron_encased_fan', [' ABA ', 'CDEDC', 'CFGFC', ' ABA '], {
        A: 'tfmg:cast_iron_frame',
        B: 'tfmg:rubber_sheet',
        C: 'tfmg:cast_iron_sheet',
        D: 'create:propeller',
        E: 'create:encased_fan',
        F: 'create:shaft',
        G: 'create:andesite_alloy'
      }).id('industrial_colonies:manufacturing/weathered_iron/fan')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-card review: Nickel-faced resistor heating bank with electrum terminals, enclosed by fireproof supports and a heavy machinery casing. The casing is the requested substantial subassembly; heat-resistant faces replace arbitrary control electronics on a passive heating element. Existing pack items; proposed construction card, no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:superheating_element', ['ABBA', 'CDDC', ' EE ', 'AFFA'], {
        A: 'tfmg:fireproof_bricks',
        B: 'tfmg:nickel_sheet',
        C: 'createaddition:electrum_wire',
        D: 'tfmg:resistor',
        E: 'tfmg:steel_frame',
        F: 'createaddition:copper_rod'
      }).id('industrial_colonies:mekanism/boiler/superheating_element')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-card review: A continuous tinted-glass display face sits above paired electron-tube drivers and copper signal contacts. Replaces three polished Rose Quartz blocks with a screen-and-driver construction, retaining a modest coated-board control layer rather than a late digital processor. Existing pack items; proposed construction card, no gameplay export.
    event.recipes.create.mechanical_crafting('2x create:display_board', ['AAAA', 'BCCB', 'DEFD'], {
        A: 'minecraft:tinted_glass',
        B: 'create:electron_tube',
        C: 'tfmg:transistor_item',
        D: 'tfmg:copper_wire',
        E: 'create:copper_casing',
        F: 'tfmg:coated_circuit_board'
      }).id('industrial_colonies:create_core/display_board_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-card review: Two protected meter windows form the front panel; measuring instruments sit above terminal connections and a completed board, with insulated mounting feet. The layout reads as a measuring cabinet rather than disconnected instruments with empty border columns. Existing pack items; proposed construction card, no gameplay export.
    event.recipes.create.mechanical_crafting('electroenergetics:energy_meter', ['A A', 'BCB', 'DED', 'FGF'], {
        A: 'minecraft:glass_pane',
        B: 'tfmg:multimeter',
        C: 'tfmg:voltmeter',
        D: 'electroenergetics:double_connector',
        E: 'electroenergetics:electrical_panel',
        F: 'tfmg:rubber_sheet',
        G: 'tfmg:circuit_board'
      }).id('industrial_colonies:create_addons/energy_meter')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-card review: A communication bridge and paired wireless interfaces sit over a speaker-equipped peripheral chassis; a completed board and rubber isolation provide routing/control. Materials now describe chat communication rather than a stray gold sheet. Existing pack items; proposed construction card, no gameplay export.
    event.recipes.create.mechanical_crafting('advancedperipherals:chat_box', ['ABA', ' C ', 'DED', ' F '], {
        A: 'computercraft:wireless_modem_normal',
        B: 'create:display_link',
        C: 'advancedperipherals:peripheral_casing',
        D: 'computercraft:speaker',
        E: 'tfmg:circuit_board',
        F: 'tfmg:rubber_sheet'
      }).id('industrial_colonies:computer_network_coverage/chat_box')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-card review: Paired cutting heads ride a magnetic motor carriage above an advanced electronic driver shelf. Engineering Processor, Advanced Control and completed boards address the cost rejection; the complementary pink power junction stays below the blade assembly. Existing pack items; proposed construction card, no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:railway_mechanical_saw', [' A A ', 'BCDCB', 'EFGHE', ' I I '], {
        A: 'createcasing:copper_mechanical_saw',
        B: 'create:railway_casing',
        C: 'tfmg:magnetic_alloy_sheet',
        D: 'tfmg:electric_motor',
        E: 'tfmg:circuit_board',
        F: 'mekanism:advanced_control_circuit',
        G: 'ae2:engineering_processor',
        H: 'tfmg:p_semiconductor',
        I: 'tfmg:steel_frame'
      }).id('industrial_colonies:v3_createcasing/railway_saw')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Whole-card review: retain the Personal Sturdy Whisk, titanium support, cobalt wear surface, Weathered structural tooling and Brass control fitting. Replace only HDPE liner with ordinary TFMG plastic so the first Industrial Iron mixer does not require the downstream PRC/HDPE branch. The chemical liner remains plastic, with rubber seals; the rest of the retrofit stays exact.
    event.recipes.create.sequenced_assembly(['createcasing:industrial_iron_mixer'], 'createcasing:weathered_iron_mixer', [
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:industrial_iron_block']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'rocketnautics:titanium_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createmetallurgy:sturdy_whisk']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'modernfoundry:cobalt_ingot']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:steel_pipe']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:rubber_sheet']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_machinery_casing']),
        event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_plate']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:calculation_processor']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:advanced_control_circuit']),
        event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'createcasing:weathered_iron_mixer'}})).loops(1).id('industrial_colonies:manufacturing/industrial_iron/mixer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Slice one dense ceramic preform into four fine reinforcement strips represented by the existing SiC Fiber item. This is a pack machining abstraction for short reinforcement, not a claim to simulate continuous CVD fiber production. Existing pack items only; no gameplay export. Shared precursors are made once for all three alloy paths.
    event.recipes.industrial_colonies.industrial_iron_cutting(['4x nuclearcraft:sic_fiber'], 'nuclearcraft:silicon_carbide_ingot').processingTime(1200).group('Shared precursor workshop / Precision ceramic reinforcement strips').id('industrial_colonies:alloy_materials/sic_fibers')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // A real plate comes from an Industrial Iron press. It becomes the reinforcing phase for the later alloy, rather than a deployer pretending to press a plate. Existing pack items only; no gameplay export. Shared precursors are made once for all three alloy paths.
    event.recipes.industrial_colonies.industrial_iron_pressing(['nuclearcraft:sic_sic_cmc_plate'], 'nuclearcraft:sic_sic_cmc_ingot').group('Shared precursor workshop / Press ceramic reinforcement plates').id('industrial_colonies:alloy_materials/ceramic_plate')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('nuclearcraft')) {
    // The specialized nuclear Pressurizer grows/densifies nitride crystals from nitride powder. Explicit64,000FE/t for2,400ticks is153.6millionFE, not Mekanism J; no numeric pressure parameter is invented. Existing pack items only; no gameplay export. Shared precursors are made once for all three alloy paths.
    event.custom({"type":"nuclearcraft:pressurizer","item_inputs":[{"item":"nuclearcraft:boron_nitride_dust","count":1}],"item_outputs":[{"item":"nuclearcraft:boron_nitride_gem"}],"energy_per_tick":64000,"process_time":2400}).id('industrial_colonies:alloy_materials/boron_nitride_crystal')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Build the Supercharged Coil on one SPS casing. First deploy the Mekanism laser onto that casing; then install two BSCCO windings, two polonium pellets, transformer, capacitor, Ultimate Control Circuit and Concurrent Processor, followed by two rubber insulation sheets. Industrial Iron deployers mount each component. One final Shadow Steel Press operation closes the assembly, retaining the requested late-machine gate. One loop, one coil, same complete material bill as the immediately preceding compacting version; no quantum/antimatter/pair alloy. Existing workpiece system handles in-progress custody. No gameplay export.
    event.recipes.create.sequenced_assembly(['mekanism:supercharged_coil'], 'mekanism:sps_casing', [
        event.recipes.industrial_colonies.shadow_steel_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:laser']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_bscco']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:coil_bscco']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:pellet_polonium']),
        event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:pellet_polonium']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:transformer']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'mekanism:ultimate_control_circuit']),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.shadow_steel_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:magnetic_alloy_sheet']),
        event.recipes.industrial_colonies.shadow_steel_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.brass_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_rod'])
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'mekanism:sps_casing'}})).loops(1).id('industrial_colonies:mekanism_nuclear/supercharged_coil')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Square SPS casing housing: five-by-five outline, Radiance upper crossmember between Vibranium upper corners, titanium side shoulders, tungsten/silicon carbide side barriers, heavy machinery casing at center, platinum lower side contacts and Allthemodium bottom crossmember between two steel-frame feet. Same fifteen input items and four-casing output as the prior rectangle; only spatial arrangement changes. No quantum plates, antimatter or pair-alloy input. No gameplay export.
    event.recipes.create.mechanical_crafting('4x mekanism:sps_casing', [' ABA ', 'ACDCA', 'EFGFE', 'ACDCA', ' AHA '], {
        A: 'nuclearcraft:platinum_plate',
        B: 'nuclearcraft:silicon_carbide_ingot',
        C: 'allthemodium:allthemodium_rod',
        D: 'rocketnautics:titanium_alloy_sheet',
        E: 'allthemodium:vibranium_plate',
        F: 'create:refined_radiance',
        G: 'tfmg:heavy_machinery_casing',
        H: 'nuclearcraft:tungsten_carbide_ingot'
      }).id('industrial_colonies:mekanism_nuclear/sps_casing_batch')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // Latest user-edited SPS Port layout preserved, including both central SPS casings and relocated Ultimate Control Circuit. Replace all four early TFMG boards with two Concurrent Processors for parallel feed monitoring and two additional Ultimate Control Circuits for high-power switching. Two Engineering Processors occupy the vacant upper corners. Existing Allthemodium block, BSCCO coils, power bank, ceramics, pipes and rubber stay exact. No quantum electronics or finished pair alloys. One port; no gameplay export.
    event.recipes.create.mechanical_crafting('mekanism:sps_port', ['ABCBA', 'DEFED', 'GHIHG', 'AJFJA', 'CKLKC'], {
        A: 'tfmg:rubber_sheet',
        B: 'nuclearcraft:tungsten_carbide_ingot',
        C: 'mekanism:ultimate_control_circuit',
        D: 'ae2:engineering_processor',
        E: 'nuclearcraft:silicon_carbide_ingot',
        F: 'mekanism:sps_casing',
        G: 'tfmg:steel_smart_fluid_pipe',
        H: 'nuclearcraft:coil_bscco',
        I: 'mekanism:ultimate_energy_cube',
        J: 'extendedae:concurrent_processor',
        K: 'nuclearcraft:platinum_plate',
        L: 'allthemodium:allthemodium_block'
      }).id('industrial_colonies:mekanism_nuclear/sps_port')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-requested machine-only revision: heated Industrial Iron Mixer. Exact ingredient quantities and one Refined Radiance output preserved. 600 processing ticks; kinetic machine, not electrical energy.
    event.recipes.industrial_colonies.industrial_iron_mixing(['create:refined_radiance'], ['mekanism:alloy_reinforced', 'mekanism:ingot_refined_glowstone', 'mekanism:ingot_refined_glowstone', 'mekanism:dust_refined_obsidian', 'nuclearcraft:platinum_dust', 'create:chromatic_compound', 'create:chromatic_compound']).processingTime(600).heated().group('Refined Radiance').id('industrial_colonies:radiance/phosphor_activation')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // [Nuclear Engineering] Build the final-tier machine as a five-row radiance-shielded industrial assembly
    event.recipes.create.mechanical_crafting('createcasing:refined_radiance_depot', ['AAAAA', ' BCB ', ' DED ', '  F  '], {
        A: 'tfmg:heavy_plate',
        B: 'createcasing:industrial_iron_press',
        C: 'create:industrial_iron_block',
        D: 'tfmg:steel_mechanism',
        E: 'create:refined_radiance_casing',
        F: 'mekanism:elite_control_circuit'
      }).id('industrial_colonies:manufacturing/refined_radiance/depot')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October24 explicit user cost/progression revision. Iron-bar guard grille, nickel shroud and three impeller parts around the existing Industrial Iron fan. Rubber isolates the motor on a Radiance-cased steel mount. No Ultimate circuit, Atomic Alloy, tungsten frame or titanium shroud needed for stationary airflow. One machine output, one Radiance casing, no direct additional Radiance. Construction review only, no gameplay export. The casing supplies its own earlier-tier electronics; no Atomic/Radiance-machine circular ingredient.
    event.recipes.create.mechanical_crafting('createcasing:refined_radiance_encased_fan', ['AAA', 'BCB', 'CDC', 'EFE', 'GHG'], {
        A: 'minecraft:iron_bars',
        B: 'tfmg:nickel_sheet',
        C: 'create:propeller',
        D: 'createcasing:industrial_iron_encased_fan',
        E: 'tfmg:rubber_sheet',
        F: 'tfmg:electric_motor',
        G: 'tfmg:steel_frame',
        H: 'create:refined_radiance_casing'
      }).group('Refined Radiance / Functional machinery').id('industrial_colonies:manufacturing/refined_radiance/fan')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-directed electronics revision, narrow3x7mixer. Engineering Processor, speed-control board and Logic Processor regulate the wired motor above brass bearings and one Radiance casing. Guided steel frame supports retained Industrial Iron mixer, shaft and whisk. All inputs precede Atomic Alloy; no Atomic/Ultimate/Osmiridium/direct Osmium loop. One machine output, review-only; no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:refined_radiance_mixer', ['ABC', 'DED', 'FGF', 'HIH', 'JKJ', 'LML', ' L '], {
        A: 'ae2:engineering_processor',
        B: 'tfmg:circuit_board',
        C: 'ae2:logic_processor',
        D: 'tfmg:steel_frame',
        E: 'tfmg:electric_motor',
        F: 'immersiveengineering:wire_electrum',
        G: 'create:refined_radiance_casing',
        H: 'createaddition:gold_rod',
        I: 'createcasing:industrial_iron_mixer',
        J: 'createaddition:gold_wire',
        K: 'immersiveengineering:stick_steel',
        L: 'tfmg:heavy_plate',
        M: 'create:whisk'
      }).group('Refined Radiance / Functional machinery').id('industrial_colonies:manufacturing/refined_radiance/mixer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // October24 explicit user cost/progression revision. Heavy crossbeam with paired ram guide rods and one motor. Rubber dampers and side frames brace the Industrial Iron press; one Radiance housing and a steel drive mechanism sit in the reinforced lower assembly. No three-motor/three-elite-circuit stack. One machine output, one Radiance casing, no direct additional Radiance. Construction review only, no gameplay export. The casing supplies its own earlier-tier electronics; no Atomic/Radiance-machine circular ingredient.
    event.recipes.create.mechanical_crafting('createcasing:refined_radiance_press', [' AAA ', 'BCDCB', ' EFE ', ' GHG ', ' AGA '], {
        A: 'tfmg:heavy_plate',
        B: 'tfmg:rubber_sheet',
        C: 'immersiveengineering:stick_steel',
        D: 'tfmg:electric_motor',
        E: 'tfmg:heavy_machinery_casing',
        F: 'createcasing:industrial_iron_press',
        G: 'tfmg:steel_mechanism',
        H: 'create:refined_radiance_casing'
      }).group('Refined Radiance / Functional machinery').id('industrial_colonies:manufacturing/refined_radiance/press')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-directed saw drive/control refinement. Keep5x3and saw top-center within tungsten inserts/nickel guards. Motor sits directly underneath the saw, paired steel rods and brass bearing shoulders brace its drive. Lower electrical/mounting row has copper leads, one Radiance casing, heavy mounting plate and Engineering Processor. No Atomic, Ultimate circuit, Osmiridium or direct Osmium. Review-only; no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:refined_radiance_mechanical_saw', ['ABCBA', 'DEFED', 'GHIJG'], {
        A: 'tfmg:nickel_sheet',
        B: 'createmetallurgy:tungsten_sheet',
        C: 'createcasing:industrial_iron_mechanical_saw',
        D: 'create:brass_ingot',
        E: 'immersiveengineering:stick_steel',
        F: 'tfmg:electric_motor',
        G: 'createaddition:gold_wire',
        H: 'create:refined_radiance_casing',
        I: 'tfmg:heavy_plate',
        J: 'ae2:engineering_processor'
      }).group('Refined Radiance / Functional machinery').id('industrial_colonies:manufacturing/refined_radiance/saw')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-directed late-game narrow3x7deployer. New top control bank: Engineering Processor for actuator control, Logic Processor for commands, Calculation Processor for positioning. Preserve every current player-edited lower row exactly, shifted down once: copper leads/precision mechanism, dual motors/Industrial Iron deployer, frame/Radiance housing, shaft, Brass Hand and heavy feet. One Radiance casing; no Atomic, Ultimate circuit, Osmiridium or direct Osmium. Review-only; no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:refined_radiance_deployer', ['ABC', 'DED', 'FGF', 'HIH', 'JKJ', 'JLJ', ' J '], {
        A: 'ae2:engineering_processor',
        B: 'ae2:logic_processor',
        C: 'ae2:calculation_processor',
        D: 'createaddition:gold_wire',
        E: 'create:precision_mechanism',
        F: 'tfmg:electric_motor',
        G: 'createcasing:industrial_iron_deployer',
        H: 'tfmg:steel_frame',
        I: 'create:refined_radiance_casing',
        J: 'tfmg:heavy_plate',
        K: 'immersiveengineering:stick_steel',
        L: 'create:brass_hand'
      }).group('Refined Radiance / Functional machinery').id('industrial_colonies:manufacturing/refined_radiance/deployer')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-requested tougher5x7drill. Three tungsten cutting parts form a pointed crown around the Industrial Iron drill; cobalt shoulders and one pre-Radiance Reinforced Alloy form the load sleeve. Guide rods flank the shaft. Twin motors and Engineering Processor with copper leads drive the assembly above one Radiance casing, steel supports and heavy mounting plates. No Atomic/Ultimate/Osmiridium/Osmium input; Reinforced Alloy remains earlier than Radiance. Review-only; no gameplay export.
    event.recipes.create.mechanical_crafting('createcasing:refined_radiance_mechanical_drill', ['  A  ', ' ABA ', ' CDC ', ' EFE ', 'GHIHG', ' JKJ ', ' EEE '], {
        A: 'createmetallurgy:tungsten_sheet',
        B: 'createcasing:industrial_iron_mechanical_drill',
        C: 'nuclearcraft:cobalt_ingot',
        D: 'mekanism:alloy_reinforced',
        E: 'tfmg:heavy_plate',
        F: 'immersiveengineering:stick_steel',
        G: 'createaddition:gold_wire',
        H: 'tfmg:electric_motor',
        I: 'ae2:engineering_processor',
        J: 'tfmg:steel_frame',
        K: 'create:refined_radiance_casing'
      }).group('Refined Radiance / Functional machinery').id('industrial_colonies:custom_progression/createcasing/refined_radiance_mechanical_drill')
  }
})

ServerEvents.recipes(event => {
  if (Platform.isLoaded('create')) {
    // User-directed casing-specific assembly: Industrial Iron Block base, then deploy Electrum Wire, one AE2 Logic Processor, one Refined Radiance core, and a second Electrum Wire; close with Industrial Iron Press. One loop yields one Radiance Casing. Industrial Iron tooling remains earlier than Radiance machinery. Two separate wire deployments consume two wires. No Atomic, Osmiridium or direct Osmium ingredient. Existing workpiece system retains intermediate custody; review-only, no gameplay export. Does not impose this assembly or wiring on other machine cards.
    event.recipes.create.sequenced_assembly(['create:refined_radiance_casing'], 'create:industrial_iron_block', [
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:refined_radiance']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:circuit_board']),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:electrum_wire']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.railway_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:capacitor_item']),
        event.recipes.industrial_colonies.railway_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
        event.recipes.industrial_colonies.industrial_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:gold_rod']),
        event.recipes.industrial_colonies.industrial_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
      ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'create:industrial_iron_block'}})).loops(1).group('Refined Radiance / Casing construction').id('industrial_colonies:back_review/refined_radiance_casing')
  }
})

// Disabled decisions: exact retired designs plus acquisition of explicitly disabled machines.
// Does not remove processing recipes merely because they run in a disabled machine.
ServerEvents.recipes(event => {
  event.remove({id: "industrial_colonies:ae2_coverage/dense_energy_cell"})
  event.remove({id: "industrial_colonies:ae2_coverage/energy_cell"})
  event.remove({id: "industrial_colonies:computer_network_coverage/colony_wireless_advanced"})
  event.remove({id: "industrial_colonies:create_addons/grid_compatible_electric_pump"})
  event.remove({id: "industrial_colonies:create_addons/kinetic_battery_batch"})
  event.remove({id: "industrial_colonies:createappliedkinetics/energy_provider"})
  event.remove({id: "industrial_colonies:custom_progression/extendedae/circuit_cutter"})
  event.remove({id: "industrial_colonies:custom_progression/nuclearcraft/nuclear_furnace"})
  event.remove({id: "industrial_colonies:custom_progression/nuclearcraft/pump"})
  event.remove({id: "industrial_colonies:functional_design/mekanism/teleporter"})
  event.remove({id: "industrial_colonies:functional_design/mekanism/teleporter_frame"})
  event.remove({id: "industrial_colonies:megacells_coverage/mega_energy_cell"})
  event.remove({id: "industrial_colonies:mekanism/combiner"})
  event.remove({id: "industrial_colonies:mekanism/electric_pump"})
  event.remove({id: "industrial_colonies:mekanism/steel_casing"})
  event.remove({id: "industrial_colonies:mekanism/transmission/basic_universal_cable"})
  event.remove({id: "industrial_colonies:mekanism/transmission/elite_universal_cable"})
  event.remove({id: "industrial_colonies:mekanism/transmission/ultimate_universal_cable"})
  event.remove({id: "industrial_colonies:mekanism_components/upgrade_stone_generator"})
  event.remove({id: "industrial_colonies:mekanism_pre_nuclear/crusher"})
  event.remove({id: "industrial_colonies:mekanism_pre_nuclear/digital_miner"})
  event.remove({id: "industrial_colonies:mekanism_pre_nuclear/energized_smelter"})
  event.remove({id: "industrial_colonies:mekanism_pre_nuclear/formulaic_assemblicator"})
  event.remove({id: "industrial_colonies:mekanism_pre_nuclear/precision_sawmill"})
  event.remove({id: "industrial_colonies:mekanism_utility/advanced_bin"})
  event.remove({id: "industrial_colonies:mekanism_utility/elite_bin"})
  event.remove({id: "industrial_colonies:mekanism_utility/ultimate_bin"})
  event.remove({id: "industrial_colonies:nuclear/refined_radiance_casing"})
  event.remove({id: "industrial_colonies:ownership/nuclear_boundary/alloy_smelter"})
  event.remove({id: "industrial_colonies:ownership/nuclear_boundary/ingot_former"})
  event.remove({id: "industrial_colonies:ownership/nuclear_boundary/melter"})
  event.remove({id: "industrial_colonies:planetary/outpost/energizer"})
  event.remove({id: "industrial_colonies:review/atm_only/feed_alloys"})
  event.remove({id: "industrial_colonies:review/atm_only/feed_metals"})
  event.remove({id: "industrial_colonies:simulated/portable_engine"})
  event.remove({id: "industrial_colonies:space_coverage/compressor"})
  event.remove({id: "industrial_colonies:space_coverage/cosmonautics_jetpack"})
  event.remove({id: "industrial_colonies:v3_ae2/inscriber"})
  event.remove({output: "ad_astra:compressor"})
  event.remove({output: "ad_astra:energizer"})
  event.remove({output: "ae2:dense_energy_cell"})
  event.remove({output: "ae2:energy_cell"})
  event.remove({output: "ae2:inscriber"})
  event.remove({output: "colony4cc:colony_wireless_advanced"})
  event.remove({output: "createappliedkinetics:energy_provider"})
  event.remove({output: "electroenergetics:electric_pump"})
  event.remove({output: "extendedae:circuit_cutter"})
  event.remove({output: "megacells:mega_energy_cell"})
  event.remove({output: "mekanism:advanced_bin"})
  event.remove({output: "mekanism:basic_universal_cable"})
  event.remove({output: "mekanism:combiner"})
  event.remove({output: "mekanism:crusher"})
  event.remove({output: "mekanism:digital_miner"})
  event.remove({output: "mekanism:electric_pump"})
  event.remove({output: "mekanism:elite_bin"})
  event.remove({output: "mekanism:elite_universal_cable"})
  event.remove({output: "mekanism:energized_smelter"})
  event.remove({output: "mekanism:formulaic_assemblicator"})
  event.remove({output: "mekanism:precision_sawmill"})
  event.remove({output: "mekanism:steel_casing"})
  event.remove({output: "mekanism:teleporter"})
  event.remove({output: "mekanism:teleporter_frame"})
  event.remove({output: "mekanism:ultimate_bin"})
  event.remove({output: "mekanism:ultimate_universal_cable"})
  event.remove({output: "mekanism:upgrade_stone_generator"})
  event.remove({output: "nuclearcraft:alloy_smelter"})
  event.remove({output: "nuclearcraft:ingot_former"})
  event.remove({output: "nuclearcraft:melter"})
  event.remove({output: "nuclearcraft:nuclear_furnace"})
  event.remove({output: "nuclearcraft:pump"})
  event.remove({output: "rocketnautics:jetpack"})
  event.remove({output: "simulated:red_portable_engine"})
})
