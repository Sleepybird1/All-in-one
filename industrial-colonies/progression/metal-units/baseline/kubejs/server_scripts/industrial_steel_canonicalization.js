// Industrial Colonies - canonical solid steel
// TFMG steel is the only player-facing ingot, nugget, and storage block.
// Later metallurgy mods retain their unique machines and molten processes.

ServerEvents.tags('item', event => {
  const canonicalSteelTags = {
    'c:ingots/steel': ['tfmg:steel_ingot'],
    'c:nuggets/steel': ['tfmg:steel_nugget'],
    'c:storage_blocks/steel': ['tfmg:steel_block']
  }

  Object.entries(canonicalSteelTags).forEach(([tag, items]) => {
    event.removeAll(tag)
    event.add(tag, items)
  })
})

ServerEvents.recipes(event => {
  const removedSteelBypasses = [
    // Create Big Cannons: early heated-mixer steel and alternate solid forms.
    'createbigcannons:mixing/alloy_steel',
    'createbigcannons:steel_block',
    'createbigcannons:steel_ingot_from_block',
    'createbigcannons:steel_ingot_from_nuggets',
    'createbigcannons:steel_scrap',
    'createbigcannons:compacting/forge_steel_block',
    'createbigcannons:compacting/forge_steel_ingot',
    'createbigcannons:compacting/forge_steel_nugget',

    // Mekanism: remove the independent carbon-infusion steel route and
    // alternate solid storage conversions. Steel dust remains a later
    // recycling/intermediate form but now smelts back to TFMG steel.
    'mekanism:processing/steel/enriched_iron_to_dust',
    'mekanism:nuggets/steel',
    'mekanism:processing/steel/ingot/from_block',
    'mekanism:processing/steel/ingot/from_dust_blasting',
    'mekanism:processing/steel/ingot/from_dust_smelting',
    'mekanism:processing/steel/ingot/from_nuggets',
    'mekanism:storage_blocks/steel',

    // Create Metallurgy keeps its alloying/casting machines, but its casts
    // produce canonical TFMG solids through replacement recipes below.
    'createmetallurgy:casting_in_basin/steel/block',
    'createmetallurgy:casting_in_table/steel/ingot',
    'createmetallurgy:crafting/materials/steel_block',
    'createmetallurgy:crafting/materials/steel_ingot_from_block',

    // Modern Foundry's own steel solids become legacy registry objects.
    // Tag-output foundry recipes resolve to TFMG after the tag replacement.
    'modernfoundry:common/materials/steel_block_from_ingots',
    'modernfoundry:common/materials/steel_ingot_from_block',
    'modernfoundry:common/materials/steel_ingot_from_nuggets',
    'modernfoundry:common/materials/steel_nugget_blasting',
    'modernfoundry:common/materials/steel_nugget_from_ingot',
    'modernfoundry:common/materials/steel_nugget_smelting'
  ]

  removedSteelBypasses.forEach(id => event.remove({ id: id }))

  // Later Create Metallurgy production remains useful, but its player-facing
  // output is the same TFMG steel unlocked by the main industrial spine.
  event.custom({
    type: 'createmetallurgy:casting_in_table',
    ingredients: [
      { type: 'neoforge:single', amount: 90, fluid: 'createmetallurgy:molten_steel' },
      { item: 'createmetallurgy:graphite_ingot_mold' }
    ],
    processing_time: 60,
    result: { item: { count: 1, id: 'tfmg:steel_ingot' } }
  }).id('industrial_colonies:steel/create_metallurgy_ingot_casting')

  event.custom({
    type: 'createmetallurgy:casting_in_basin',
    ingredients: [
      { type: 'neoforge:single', amount: 810, fluid: 'createmetallurgy:molten_steel' }
    ],
    processing_time: 480,
    result: { item: { count: 1, id: 'tfmg:steel_block' } }
  }).id('industrial_colonies:steel/create_metallurgy_block_casting')

  // Mekanism steel dust remains useful for recycling and later processes,
  // but it can no longer create a competing ingot family.
  event.custom({
    type: 'minecraft:smelting',
    category: 'misc',
    cookingtime: 200,
    experience: 0.4,
    ingredient: { item: 'mekanism:dust_steel' },
    result: { count: 1, id: 'tfmg:steel_ingot' }
  }).id('industrial_colonies:steel/from_mekanism_dust_smelting')

  event.custom({
    type: 'minecraft:blasting',
    category: 'misc',
    cookingtime: 100,
    experience: 0.4,
    ingredient: { item: 'mekanism:dust_steel' },
    result: { count: 1, id: 'tfmg:steel_ingot' }
  }).id('industrial_colonies:steel/from_mekanism_dust_blasting')

  // Lossless one-way migration recipes protect existing saves. These inputs
  // have no remaining survival production route after the removals above.
  const legacyConversions = [
    ['mekanism:ingot_steel', 'tfmg:steel_ingot', 1],
    ['mekanism:nugget_steel', 'tfmg:steel_nugget', 1],
    ['mekanism:block_steel', 'tfmg:steel_ingot', 9],
    ['createmetallurgy:steel_ingot', 'tfmg:steel_ingot', 1],
    ['createmetallurgy:steel_block', 'tfmg:steel_ingot', 9],
    ['modernfoundry:steel_ingot', 'tfmg:steel_ingot', 1],
    ['modernfoundry:steel_nugget', 'tfmg:steel_nugget', 1],
    ['modernfoundry:steel_block', 'tfmg:steel_ingot', 9],
    ['createbigcannons:steel_ingot', 'tfmg:steel_ingot', 1],
    ['createbigcannons:steel_scrap', 'tfmg:steel_nugget', 1],
    ['createbigcannons:steel_block', 'tfmg:steel_ingot', 9]
  ]

  legacyConversions.forEach(entry => {
    const input = entry[0]
    const output = entry[1]
    const count = entry[2]
    const path = input.replace(':', '_').replace(/\//g, '_')
    event.custom({
      type: 'minecraft:crafting_shapeless',
      category: 'misc',
      ingredients: [{ item: input }],
      result: { count: count, id: output }
    }).id(`industrial_colonies:steel/migrate_${path}`)
  })

  console.info(`[Industrial Colonies] Canonical TFMG steel loaded; removed ${removedSteelBypasses.length} alternate recipes.`)
})
