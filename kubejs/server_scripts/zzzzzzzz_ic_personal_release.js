// Explicit user request: deploy Personal Recipes unchanged; preserve approved alternatives.
ServerEvents.recipes(event => {
  if (Item.exists("create:andesite_alloy")) event.remove({output: "create:andesite_alloy"});
  if (Item.exists("create:electron_tube")) event.remove({output: "create:electron_tube"});
  if (Item.exists("create:mechanical_press")) event.remove({output: "create:mechanical_press"});
  if (Item.exists("create:precision_mechanism")) event.remove({output: "create:precision_mechanism"});
  if (Item.exists("create:rotation_speed_controller")) event.remove({output: "create:rotation_speed_controller"});
  if (Item.exists("create:whisk")) event.remove({output: "create:whisk"});
  if (Item.exists("createaddition:capacitor")) event.remove({output: "createaddition:capacitor"});
  if (Item.exists("createaddition:copper_rod")) event.remove({output: "createaddition:copper_rod"});
  if (Item.exists("createaddition:iron_rod")) event.remove({output: "createaddition:iron_rod"});
  if (Item.exists("createaddition:rolling_mill")) event.remove({output: "createaddition:rolling_mill"});
  if (Item.exists("createcasing:copper_deployer")) event.remove({output: "createcasing:copper_deployer"});
  if (Item.exists("createcasing:copper_press")) event.remove({output: "createcasing:copper_press"});
  if (Item.exists("createcasing:weathered_iron_deployer")) event.remove({output: "createcasing:weathered_iron_deployer"});
  if (Item.exists("createcasing:weathered_iron_mechanical_saw")) event.remove({output: "createcasing:weathered_iron_mechanical_saw"});
  if (Item.exists("createcasing:weathered_iron_mixer")) event.remove({output: "createcasing:weathered_iron_mixer"});
  if (Item.exists("createcasing:weathered_iron_press")) event.remove({output: "createcasing:weathered_iron_press"});
  if (Item.exists("createmechanisms:rubber")) event.remove({output: "createmechanisms:rubber"});
  if (Item.exists("createmetallurgy:foundry_mixer")) event.remove({output: "createmetallurgy:foundry_mixer"});
  if (Item.exists("createmetallurgy:sturdy_whisk")) event.remove({output: "createmetallurgy:sturdy_whisk"});
  if (Item.exists("mekanism:enrichment_chamber")) event.remove({output: "mekanism:enrichment_chamber"});
  if (Item.exists("mekanism:metallurgic_infuser")) event.remove({output: "mekanism:metallurgic_infuser"});
  if (Item.exists("tfmg:air_intake")) event.remove({output: "tfmg:air_intake"});
  if (Item.exists("tfmg:cast_iron_frame")) event.remove({output: "tfmg:cast_iron_frame"});
  if (Item.exists("tfmg:cast_iron_ingot")) event.remove({output: "tfmg:cast_iron_ingot"});
  if (Item.exists("tfmg:cast_iron_nugget")) event.remove({output: "tfmg:cast_iron_nugget"});
  if (Item.exists("tfmg:centrifuge")) event.remove({output: "tfmg:centrifuge"});
  if (Item.exists("tfmg:coke_oven")) event.remove({output: "tfmg:coke_oven"});
  if (Item.exists("tfmg:copper_electrode")) event.remove({output: "tfmg:copper_electrode"});
  if (Item.exists("tfmg:electrode_holder")) event.remove({output: "tfmg:electrode_holder"});
  if (Item.exists("tfmg:graphite_electrode")) event.remove({output: "tfmg:graphite_electrode"});
  if (Item.exists("tfmg:heavy_machinery_casing")) event.remove({output: "tfmg:heavy_machinery_casing"});
  if (Item.exists("tfmg:rubber_sheet")) event.remove({output: "tfmg:rubber_sheet"});
  if (Item.exists("tfmg:steel_mechanism")) event.remove({output: "tfmg:steel_mechanism"});
  if (Item.exists("tfmg:zinc_electrode")) event.remove({output: "tfmg:zinc_electrode"});

  // Personal card a11c982f-a80f-41f6-8a95-fc1686e45b8c
event.shaped('create:whisk', [' A ', 'BAB', 'BBB'], {
    A: 'create:zinc_ingot',
    B: 'createcasing:andesite_sheet'
  }).id('industrial_colonies:personal/a11c982f_a80f_41f6_8a95_fc1686e45b8c')

  // Personal card f9b5f021-c117-4301-81b5-bfe40e397167
event.shaped('create:andesite_alloy', ['AB', 'BA'], {
    A: 'create:zinc_nugget',
    B: 'minecraft:andesite'
  }).id('industrial_colonies:personal/f9b5f021_c117_4301_81b5_bfe40e397167')

  // Personal card 9cae5c3e-65de-4598-9d14-b3743df86a48
event.recipes.create.sequenced_assembly(['tfmg:cast_iron_frame'], 'immersiveengineering:sheetmetal_iron', [
    event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece').merge({processing_time: 20}),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:cast_iron_sheet']),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createbigcannons:cast_iron_ingot']),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:iron_rod']),
    event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece').merge({processing_time: 20}),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createaddition:iron_rod']),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.custom({type: 'industrial_colonies:assembly_blasting', ingredients: [{item: 'industrial_colonies:assembly_workpiece'}], results: [{id: 'industrial_colonies:assembly_workpiece'}], processing_time: 100})
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'immersiveengineering:sheetmetal_iron'}})).loops(1).id('industrial_colonies:personal/9cae5c3e_65de_4598_9d14_b3743df86a48')

  // Personal card ef05a8f3-fad2-4e0f-81a8-1c9b93ddde7c
event.recipes.create.sequenced_assembly(['tfmg:cast_iron_ingot'], 'minecraft:iron_ingot', [
    event.recipes.industrial_colonies.base_mixing('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', {item: 'minecraft:coal'}, {item: 'minecraft:iron_ingot'}, {item: 'minecraft:fire_charge'}] ).merge({heat_requirement: 'lowheated', processing_time: 1000}),
    event.recipes.industrial_colonies.base_compacting('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', Fluid.of('minecraft:water', 250)] ).merge({heat_requirement: 'none', processing_time: 200})
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:iron_ingot'}})).loops(1).id('industrial_colonies:drafts/cast_iron/coal_batch_20260926')

  // Personal card 4db13837-154b-59f5-b9d4-b82c46b8832b
event.recipes.create.mechanical_crafting('createcasing:weathered_iron_deployer', ['A A', 'BCD', 'EFE', 'GHG', 'IJI'], {
    A: 'create:electron_tube',
    B: 'create:precision_mechanism',
    C: 'create:deployer',
    D: 'createmechanisms:zinc_mechanism',
    E: 'tfmg:copper_wire',
    F: 'tfmg:cast_iron_frame',
    G: 'minecraft:redstone',
    H: 'createaddition:iron_rod',
    I: 'tfmg:cast_iron_sheet',
    J: 'create:brass_hand'
  }).id('industrial_colonies:manufacturing/weathered_iron/deployer')

  // Personal card 6aa81d1a-b387-45cc-aa40-8192fb8efe25
event.shaped('createaddition:rolling_mill', ['ABA', 'CBC', 'DED'], {
    A: 'create:iron_sheet',
    B: 'create:shaft',
    C: 'create:cogwheel',
    D: 'create:andesite_alloy',
    E: 'create:andesite_casing'
  }).id('industrial_colonies:personal/6aa81d1a_b387_45cc_aa40_8192fb8efe25')

  // Personal card 35042bf4-d573-4391-8091-4b15e9c6725a
event.shaped('create:mechanical_press', ['A', 'B', 'C'], {
    A: 'create:shaft',
    B: 'create:andesite_casing',
    C: 'create:andesite_alloy_block'
  }).id('industrial_colonies:personal/35042bf4_d573_4391_8091_4b15e9c6725a')

  // Personal card d2e95693-e6f2-4380-8a3b-5b5c0ba06b88
event.recipes.create.mechanical_crafting('createcasing:weathered_iron_encased_fan', ['ABCBA', 'DEFED', 'GHIHG', ' EJE ', 'ABKBA'], {
    A: 'tfmg:cast_iron_sheet',
    B: 'tfmg:copper_wire',
    C: 'createmechanisms:zinc_mechanism',
    D: 'create:electron_tube',
    E: 'createaddition:iron_rod',
    F: 'create:encased_fan',
    G: 'create:shaft',
    H: 'create:propeller',
    I: 'tfmg:cast_iron_frame',
    J: 'createaddition:electric_motor',
    K: 'create:precision_mechanism'
  }).id('industrial_colonies:drafts/weathered_iron/fan_spacious_5x5_20260926')

  // Personal card f8354d44-4ad8-434f-b916-8179cafcc412
event.recipes.create.mechanical_crafting('createcasing:weathered_iron_press', ['ABA', 'CDC', 'EFE', 'GHG', 'GIG'], {
    A: 'create:electron_tube',
    B: 'create:precision_mechanism',
    C: 'minecraft:iron_ingot',
    D: 'create:mechanical_press',
    E: 'tfmg:copper_wire',
    F: 'tfmg:cast_iron_frame',
    G: 'tfmg:cast_iron_sheet',
    H: 'createaddition:iron_rod',
    I: 'minecraft:iron_block'
  }).id('industrial_colonies:drafts/weathered_iron/press_review_20260926')

  // Personal card 294ac263-6663-4c7a-8a0b-613bc20f010e
event.recipes.create.mechanical_crafting('createcasing:weathered_iron_mechanical_saw', ['ABCBA', 'DEFGH', 'BIJIB'], {
    A: 'tfmg:copper_wire',
    B: 'tfmg:cast_iron_sheet',
    C: 'create:iron_sheet',
    D: 'create:precision_mechanism',
    E: 'createaddition:iron_rod',
    F: 'create:mechanical_saw',
    G: 'createaddition:electric_motor',
    H: 'createmechanisms:zinc_mechanism',
    I: 'create:electron_tube',
    J: 'tfmg:cast_iron_frame'
  }).id('industrial_colonies:drafts/weathered_iron/saw_review_20260926')

  // Personal card 28dc5686-b2e1-4547-92f5-a7e15c0432f7
event.recipes.create.mechanical_crafting('mekanism:metallurgic_infuser', [' ABA ', 'CDEDC', 'FGHIF', 'JFEFJ', ' KLK '], {
    A: 'create:electron_tube',
    B: 'tfmg:zinc_electrode',
    C: 'minecraft:gold_nugget',
    D: 'tfmg:copper_wire',
    E: 'create:precision_mechanism',
    F: 'minecraft:redstone',
    G: 'tfmg:graphite_electrode',
    H: 'tfmg:cast_iron_frame',
    I: 'tfmg:copper_electrode',
    J: 'tfmg:cast_iron_ingot',
    K: 'createmechanisms:zinc_mechanism',
    L: 'tfmg:coated_circuit_board'
  }).id('industrial_colonies:personal/28dc5686_b2e1_4547_92f5_a7e15c0432f7')

  // Personal card 2ed81181-9724-47b9-ad72-ea78887507b1
event.recipes.create.mechanical_crafting('createcasing:weathered_iron_mixer', ['ABA', 'CDC', 'EFG', 'HIH', 'HJH'], {
    A: 'create:cogwheel',
    B: 'createaddition:electric_motor',
    C: 'tfmg:copper_wire',
    D: 'create:mechanical_mixer',
    E: 'createmechanisms:zinc_mechanism',
    F: 'tfmg:cast_iron_frame',
    G: 'create:precision_mechanism',
    H: 'tfmg:cast_iron_sheet',
    I: 'createaddition:iron_rod',
    J: 'create:whisk'
  }).id('industrial_colonies:drafts/weathered_iron_mixer_review_20260927')

  // Personal card d3472ae5-70ba-449e-93d6-f4f00eb637f8
event.recipes.create.mechanical_crafting('mekanism:enrichment_chamber', [' ABA ', 'CDEDC', 'FGHGF', 'IJKJI', ' LFL '], {
    A: 'createaddition:capacitor',
    B: 'tfmg:coated_circuit_board',
    C: 'minecraft:redstone',
    D: 'createaddition:iron_rod',
    E: 'create:electron_tube',
    F: 'tfmg:cast_iron_sheet',
    G: 'tfmg:centrifuge',
    H: 'tfmg:cast_iron_frame',
    I: 'tfmg:copper_wire',
    J: 'create:shaft',
    K: 'tfmg:steel_mechanism',
    L: 'create:precision_mechanism'
  }).id('industrial_colonies:drafts/enrichment_chamber_review_20260926')

  // Personal card c6ec40da-bfd2-4fff-8d66-ea7f097e47c9
event.recipes.create.sequenced_assembly([CreateItem.of('tfmg:centrifuge', 0.75), CreateItem.of('minecraft:iron_nugget', 0.25)], 'tfmg:aluminum_sheet', [
    event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'immersiveengineering:stick_aluminum']),
    event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.weathered_iron_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.weathered_iron_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'create:iron_sheet']),
    event.recipes.industrial_colonies.weathered_iron_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:aluminum_sheet'}})).loops(4).id('industrial_colonies:drafts/centrifuge_weathered_review_20260927')

  // Personal card 1be2e3c0-7694-4649-b3af-ed0fe38084d1
event.shaped('2x tfmg:coke_oven', ['ABA', 'BCB', 'DBD'], {
    A: 'tfmg:copper_wire',
    B: 'tfmg:cast_iron_sheet',
    C: 'tfmg:cast_iron_block',
    D: 'createaddition:copper_rod'
  }).id('industrial_colonies:personal/1be2e3c0_7694_4649_b3af_ed0fe38084d1')

  // Personal card 7d831dfc-67b0-4668-aefa-3ad2ade2873d
event.recipes.create.mechanical_crafting('3x tfmg:air_intake', ['AAA', 'BCB', 'ADA'], {
    A: 'tfmg:cast_iron_sheet',
    B: 'tfmg:cast_iron_pipe',
    C: 'create:propeller',
    D: 'create:shaft'
  }).id('industrial_colonies:drafts/air_intake_review_20260927')

  // Personal card 3ac7eb96-af04-4cd2-b864-515211cb8c91
event.recipes.create.mechanical_crafting('createmetallurgy:sturdy_whisk', [' A ', 'BAB', 'BBB'], {
    A: 'immersiveengineering:stick_steel',
    B: 'create:sturdy_sheet'
  }).id('industrial_colonies:drafts/sturdy_whisk_review_20260927')

  // Personal card 12a9d8ff-582a-4b30-ad16-b0ab574cf497
event.recipes.create.mechanical_crafting('createmetallurgy:foundry_mixer', ['ABCBA', 'ADEDA', ' AFA ', '  G  '], {
    A: 'i_architecture:industrial_iron_ingot',
    B: 'tfmg:steel_cogwheel',
    C: 'create:copper_casing',
    D: 'createcasing:brass_shaft',
    E: 'tfmg:steel_frame',
    F: 'tfmg:steel_mechanism',
    G: 'createmetallurgy:sturdy_whisk'
  }).id('industrial_colonies:drafts/foundry_mixer_review_20260927')

  // Personal card 1b1a604f-1fd6-45ba-8d1d-3c861864d857
event.recipes.industrial_colonies.base_mixing(['createmechanisms:rubber'], ['minecraft:resin_clump', 'minecraft:resin_clump', 'minecraft:resin_clump', 'minecraft:resin_clump', 'minecraft:water_bucket', 'tfmg:sulfur_dust']).id('industrial_colonies:drafts/resin_rubber_review_20260927').merge({heat_requirement: 'lowheated'})

  // Personal card 377a876d-cd14-404f-95dc-a5e82186daa0
event.recipes.create.sequenced_assembly([CreateItem.of('tfmg:steel_mechanism', 0.9375), CreateItem.of('minecraft:compass', 0.03125), CreateItem.of('tfmg:steel_ingot', 0.03125)], 'tfmg:heavy_plate', [
    event.recipes.industrial_colonies.weathered_iron_deploying('tfmg:unfinished_steel_mechanism', ['tfmg:unfinished_steel_mechanism', 'tfmg:steel_cogwheel']),
    event.recipes.industrial_colonies.weathered_iron_deploying('tfmg:unfinished_steel_mechanism', ['tfmg:unfinished_steel_mechanism', 'tfmg:cast_iron_sheet']),
    event.recipes.industrial_colonies.weathered_iron_deploying('tfmg:unfinished_steel_mechanism', ['tfmg:unfinished_steel_mechanism', 'tfmg:large_steel_cogwheel']),
    event.recipes.industrial_colonies.weathered_iron_deploying('tfmg:unfinished_steel_mechanism', ['tfmg:unfinished_steel_mechanism', 'tfmg:lead_sheet']),
    event.recipes.industrial_colonies.weathered_iron_deploying('tfmg:unfinished_steel_mechanism', ['tfmg:unfinished_steel_mechanism', 'tfmg:screw']),
    event.recipes.industrial_colonies.weathered_iron_deploying('tfmg:unfinished_steel_mechanism', ['tfmg:unfinished_steel_mechanism', 'tfmg:screwdriver']).merge({keep_held_item: false, industrial_tool_damage: 1, processing_time: 0}),
    event.recipes.industrial_colonies.weathered_iron_pressing('tfmg:unfinished_steel_mechanism', 'tfmg:unfinished_steel_mechanism'),
    event.recipes.industrial_colonies.weathered_iron_cutting('tfmg:unfinished_steel_mechanism', 'tfmg:unfinished_steel_mechanism')
  ]).transitionalItem('tfmg:unfinished_steel_mechanism').loops(2).id('industrial_colonies:drafts/tfmg_original_steel_mechanism_review')

  // Personal card 15aa7acc-81b9-4a10-9842-3fb0706232d3
event.recipes.industrial_colonies.weathered_iron_cutting(['tfmg:graphite_electrode'], 'nuclearcraft:graphite_block').processingTime(50).id('industrial_colonies:personal/15aa7acc_81b9_4a10_9842_3fb0706232d3')

  // Personal card 406eea54-9e46-42ee-bb58-5caf13c4a2f2
event.recipes.industrial_colonies.base_cutting(['4x tfmg:copper_electrode'], 'minecraft:copper_block').processingTime(50).id('industrial_colonies:personal/406eea54_9e46_42ee_bb58_5caf13c4a2f2')

  // Personal card 7383cbd3-e4fd-4ae1-8b79-45336ee2c95e
event.recipes.create.sequenced_assembly(['tfmg:heavy_machinery_casing'], 'tfmg:steel_casing', [
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:heavy_plate'])
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'tfmg:heavy_plate'}})).loops(3).id('industrial_colonies:personal/7383cbd3_e4fd_4ae1_8b79_45336ee2c95e')

  // Personal card 9b8e0d34-125a-46ad-8af8-8ebd1c83d7db
event.shaped('tfmg:electrode_holder', ['ABA', 'CDC', 'EFE'], {
    A: 'tfmg:copper_wire',
    B: 'minecraft:gold_nugget',
    C: 'immersiveengineering:plate_lead',
    D: 'tfmg:steel_frame',
    E: 'immersiveengineering:stick_steel',
    F: 'create:precision_mechanism'
  }).id('industrial_colonies:drafts/electrode_holder_review_20260927')

  // Personal card 1f5ee7d5-67f9-46ca-beb2-a56be17eb398
event.recipes.create.mechanical_crafting('2x tfmg:steel_chemical_vat', ['ABA', 'CDC', 'AEA'], {
    A: 'immersiveengineering:plate_steel',
    B: 'tfmg:rubber_sheet',
    C: 'immersiveengineering:plate_lead',
    D: 'tfmg:steel_frame',
    E: 'tfmg:steel_fluid_tank'
  }).id('industrial_colonies:drafts/steel_chemical_vat_review_20260927')

  // Personal card e8112d91-17f5-4a98-a272-63e5dd097278
event.recipes.create.mechanical_crafting('tfmg:fireproof_chemical_vat', ['AAA', 'BCB', 'BBB'], {
    A: 'tfmg:heavy_plate',
    B: 'tfmg:fireproof_bricks',
    C: 'tfmg:steel_chemical_vat'
  }).id('industrial_colonies:drafts/fireproof_chemical_vat_review_20260927')

  // Personal card aafe1c53-3f2a-41f9-917b-9c89ca8b9b1e
event.recipes.create.mechanical_crafting('tfmg:industrial_mixer', ['ABCBA', 'DEFED', 'GHIHG', 'AJGJA', ' DGD '], {
    A: 'tfmg:screw',
    B: 'tfmg:copper_wire',
    C: 'create:precision_mechanism',
    D: 'immersiveengineering:plate_steel',
    E: 'tfmg:circuit_board',
    F: 'tfmg:steel_mechanism',
    G: 'immersiveengineering:stick_steel',
    H: 'tfmg:large_steel_cogwheel',
    I: 'tfmg:heavy_machinery_casing',
    J: 'tfmg:rubber_sheet'
  }).id('industrial_colonies:drafts/industrial_mixer_review_20260927')

  // Personal card 8ed3f389-d0ea-4020-9733-62ebb11483f0
event.recipes.create.sequenced_assembly(['immersiveengineering:plate_steel'], 'mekanism:ingot_steel', [
    event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:screw']),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'immersiveengineering:plate_steel'}})).loops(2).id('industrial_colonies:personal/8ed3f389_d0ea_4020_9733_62ebb11483f0')

  // Personal card 19a7e8b6-b3d9-4989-a1b3-e4f9327d4e1f
event.recipes.create.mechanical_crafting('createcasing:copper_encased_fan', ['ABCBA', ' DED ', ' BFB ', ' GHG ', 'IDJDI'], {
    A: 'create:electron_tube',
    B: 'tfmg:rubber_sheet',
    C: 'create:propeller',
    D: 'tfmg:copper_wire',
    E: 'createaddition:copper_rod',
    F: 'create:precision_mechanism',
    G: 'immersiveengineering:plate_copper',
    H: 'tfmg:copper_frame',
    I: 'createaddition:capacitor',
    J: 'create:rotation_speed_controller'
  }).id('industrial_colonies:drafts/copper_fan_review_20260927')

  // Personal card 6dcf1418-f419-4342-8980-c4d29acb4f56
event.recipes.create.mechanical_crafting('createcasing:copper_mixer', ['ABCBA', 'DEFGD', 'HIIIH', 'JBKBJ', ' HLH '], {
    A: 'create:electron_tube',
    B: 'createaddition:capacitor',
    C: 'create:rotation_speed_controller',
    D: 'tfmg:copper_wire',
    E: 'create:large_cogwheel',
    F: 'create:copper_casing',
    G: 'create:cogwheel',
    H: 'immersiveengineering:plate_copper',
    I: 'create:precision_mechanism',
    J: 'tfmg:rubber_sheet',
    K: 'createaddition:copper_rod',
    L: 'create:whisk'
  }).id('industrial_colonies:drafts/copper_mixer_review_20260927')

  // Personal card 94275602-1e9c-4701-b2ae-efc6d0334f0b
event.recipes.create.mechanical_crafting('createcasing:copper_press', ['ABA', 'CDC', 'EFE', 'GEG', 'HIH', 'HJH'], {
    A: 'create:electron_tube',
    B: 'createaddition:capacitor',
    C: 'tfmg:copper_wire',
    D: 'create:copper_casing',
    E: 'create:precision_mechanism',
    F: 'create:rotation_speed_controller',
    G: 'tfmg:rubber_sheet',
    H: 'immersiveengineering:plate_copper',
    I: 'createaddition:copper_rod',
    J: 'minecraft:iron_block'
  }).id('industrial_colonies:drafts/copper_press_review_20260927')

  // Personal card bb7cba58-35d1-46bc-ae4b-3b7418bf1c85
event.recipes.create.mechanical_crafting('createcasing:copper_mechanical_saw', ['A B A', 'CBCBC', 'DEFED', 'GHIHG'], {
    A: 'createaddition:copper_rod',
    B: 'create:iron_sheet',
    C: 'create:precision_mechanism',
    D: 'tfmg:rubber_sheet',
    E: 'createaddition:capacitor',
    F: 'create:rotation_speed_controller',
    G: 'create:electron_tube',
    H: 'tfmg:copper_wire',
    I: 'create:copper_casing'
  }).id('industrial_colonies:drafts/copper_saw_review_20260927')

  // Personal card 59392cb9-087b-4eaf-918f-0f32d31b4517
event.recipes.create.mechanical_crafting('createcasing:copper_deployer', ['ABA', 'CDC', 'BEB', 'FCF', 'GHG', 'IJI'], {
    A: 'create:electron_tube',
    B: 'createaddition:capacitor',
    C: 'create:precision_mechanism',
    D: 'create:copper_casing',
    E: 'create:rotation_speed_controller',
    F: 'tfmg:rubber_sheet',
    G: 'tfmg:copper_wire',
    H: 'createaddition:copper_rod',
    I: 'immersiveengineering:plate_copper',
    J: 'create:brass_hand'
  }).id('industrial_colonies:drafts/copper_deployer_review_20260927')

  // Personal card c810c4d0-485b-4e25-9083-1e2f70b12103
event.recipes.create.sequenced_assembly(['tfmg:cast_iron_nugget'], 'minecraft:iron_nugget', [
    event.recipes.industrial_colonies.base_mixing('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', {item: 'minecraft:charcoal'}, {item: 'minecraft:fire_charge'}, {item: 'minecraft:iron_nugget'}] ).merge({heat_requirement: 'heated', processing_time: 100}),
    event.recipes.industrial_colonies.base_compacting('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', Fluid.of('minecraft:water', 250)] ).merge({heat_requirement: 'none', processing_time: 200})
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:iron_nugget'}})).loops(1).id('industrial_colonies:drafts/cast_iron/charcoal_trial_20260926')

  // Personal card 7c33c78b-1eb8-4c78-9d91-897868ef4a43
event.recipes.industrial_colonies.base_compacting(['tfmg:rubber_sheet'], ['createmechanisms:rubber']).id('industrial_colonies:personal/7c33c78b_1eb8_4c78_9d91_897868ef4a43').merge({heat_requirement: 'lowheated'})

  // Personal card 4cddb1f7-0ee7-4e57-8560-b9043d2eaace
event.shaped('createaddition:capacitor', ['A', 'B', 'C'], {
    A: 'create:copper_sheet',
    B: 'createaddition:zinc_sheet',
    C: 'minecraft:redstone_torch'
  }).id('industrial_colonies:personal/4cddb1f7_0ee7_4e57_8560_b9043d2eaace')

  // Personal card a23b9338-bd2d-4dfe-b47c-c0436288cbc6
event.shaped('create:electron_tube', ['A', 'B'], {
    A: 'create:polished_rose_quartz',
    B: 'immersiveengineering:plate_iron'
  }).id('industrial_colonies:personal/a23b9338_bd2d_4dfe_b47c_c0436288cbc6')

  // Personal card 074a2c95-1157-4568-ade8-fcdc7853b68b
event.shaped('create:rotation_speed_controller', [' A ', 'BCB', 'DED'], {
    A: 'create:precision_mechanism',
    B: 'tfmg:copper_wire',
    C: 'create:brass_casing',
    D: 'createaddition:capacitor',
    E: 'tfmg:empty_circuit_board'
  }).id('industrial_colonies:personal/074a2c95_1157_4568_ade8_fcdc7853b68b')

  // Personal card 2035c63b-8c9d-4407-9f77-45ae5f683157
event.recipes.industrial_colonies.base_cutting(['tfmg:zinc_electrode'], 'create:zinc_block').processingTime(50).id('industrial_colonies:personal/2035c63b_8c9d_4407_9f77_45ae5f683157')

  // Personal card 4cfd06a2-0733-4e32-adac-424eeb6bc789
event.recipes.create.sequenced_assembly([CreateItem.of('create:precision_mechanism', 0.8), CreateItem.of('create:brass_ingot', 0.2)], 'create:brass_sheet', [
    event.recipes.industrial_colonies.base_deploying('create:incomplete_precision_mechanism', ['create:incomplete_precision_mechanism', 'create:iron_sheet']),
    event.recipes.industrial_colonies.base_pressing('create:incomplete_precision_mechanism', 'create:incomplete_precision_mechanism'),
    event.recipes.industrial_colonies.base_deploying('create:incomplete_precision_mechanism', ['create:incomplete_precision_mechanism', 'tfmg:copper_wire']),
    event.recipes.industrial_colonies.base_deploying('create:incomplete_precision_mechanism', ['create:incomplete_precision_mechanism', 'createaddition:copper_rod']),
    event.recipes.industrial_colonies.base_pressing('create:incomplete_precision_mechanism', 'create:incomplete_precision_mechanism'),
    event.recipes.industrial_colonies.base_deploying('create:incomplete_precision_mechanism', ['create:incomplete_precision_mechanism', 'create:cogwheel'])
  ]).transitionalItem('create:incomplete_precision_mechanism').loops(2).id('industrial_colonies:drafts/precision_mechanism_brass_review_20260927')

  // Personal card 31b11e0a-4757-4536-89da-3d27ed9ca3d9
event.recipes.create.sequenced_assembly([CreateItem.of('9x createaddition:iron_rod', 0.6), CreateItem.of('6x createaddition:iron_rod', 0.4)], 'minecraft:iron_block', [
    event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece').merge({processing_time: 200}),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece').merge({processing_time: 200})
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:iron_block'}})).loops(1).id('industrial_colonies:personal/31b11e0a_4757_4536_89da_3d27ed9ca3d9')

  // Personal card 709473cd-f3c2-485b-833b-af45146cf615
event.recipes.create.sequenced_assembly([CreateItem.of('9x createaddition:copper_rod', 0.6), CreateItem.of('6x createaddition:copper_rod', 0.4)], 'minecraft:copper_block', [
    event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece'),
    event.recipes.industrial_colonies.base_cutting('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'minecraft:copper_block'}})).loops(1).id('industrial_colonies:drafts/copper_rods_review_20260927')
  console.info("IC_PERSONAL_RELEASE_COMPLETE cards=42");
});
