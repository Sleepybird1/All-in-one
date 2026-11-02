// Industrial Colonies - canonical lead
// TFMG owns lead ores, raw material, ingots, nuggets, sheets, and blocks.
// Mekanism keeps its unique chemical-processing intermediates.

ServerEvents.tags('item', event => {
  const canonicalLeadTags = {
    'c:ores/lead': ['tfmg:lead_ore', 'tfmg:deepslate_lead_ore'],
    'c:raw_materials/lead': ['tfmg:raw_lead'],
    'c:storage_blocks/raw_lead': ['tfmg:raw_lead_block'],
    'c:ingots/lead': ['tfmg:lead_ingot'],
    'c:nuggets/lead': ['tfmg:lead_nugget'],
    'c:plates/lead': ['tfmg:lead_sheet'],
    'c:storage_blocks/lead': ['tfmg:lead_block']
  }

  Object.entries(canonicalLeadTags).forEach(([tag, items]) => {
    event.removeAll(tag)
    event.add(tag, items)
  })
})

ServerEvents.recipes(event => {
  const removedLeadDuplicates = [
    'mekanism:processing/lead/ingot/from_block',
    'mekanism:processing/lead/ingot/from_dust_blasting',
    'mekanism:processing/lead/ingot/from_dust_smelting',
    'mekanism:processing/lead/ingot/from_nuggets',
    'mekanism:processing/lead/ingot/from_ore_blasting',
    'mekanism:processing/lead/ingot/from_ore_smelting',
    'mekanism:processing/lead/ingot/from_raw_blasting',
    'mekanism:processing/lead/ingot/from_raw_smelting',
    'mekanism:processing/lead/nugget/from_ingot',
    'mekanism:processing/lead/storage_blocks/from_ingots',
    'mekanism:processing/lead/raw_storage_blocks/from_raw',
    'mekanism:processing/lead/raw/from_raw_block',
    'mekanism:processing/lead/ore/from_raw',
    'mekanism:processing/lead/ore/deepslate_from_raw',
    'create:splashing/mekanism/crushed_raw_lead',
    'create:smelting/ingot_lead_compat_mekanism',
    'create:blasting/ingot_lead_compat_mekanism'
  ]

  removedLeadDuplicates.forEach(id => event.remove({ id: id }))

  // Mekanism's advanced lead chains terminate in its unique dust, which is
  // then consolidated back into the canonical TFMG ingot.
  event.custom({
    type: 'minecraft:smelting',
    category: 'misc',
    cookingtime: 200,
    experience: 0.3,
    ingredient: { item: 'mekanism:dust_lead' },
    result: { count: 1, id: 'tfmg:lead_ingot' }
  }).id('industrial_colonies:lead/from_mekanism_dust_smelting')

  event.custom({
    type: 'minecraft:blasting',
    category: 'misc',
    cookingtime: 100,
    experience: 0.3,
    ingredient: { item: 'mekanism:dust_lead' },
    result: { count: 1, id: 'tfmg:lead_ingot' }
  }).id('industrial_colonies:lead/from_mekanism_dust_blasting')

  // Create's compatibility recipes are valuable factory/recovery routes, but
  // their installed versions return Mekanism's deprecated player-facing solids.
  event.custom({
    type: 'create:splashing',
    ingredients: [{ item: 'create:crushed_raw_lead' }],
    results: [{ count: 9, id: 'tfmg:lead_nugget' }]
  }).id('industrial_colonies:lead/create_splashing_crushed_raw_lead')

  event.custom({
    type: 'minecraft:smelting',
    category: 'blocks',
    cookingtime: 200,
    experience: 0.1,
    ingredient: { item: 'create:crushed_raw_lead' },
    result: { count: 1, id: 'tfmg:lead_ingot' }
  }).id('industrial_colonies:lead/create_crushed_raw_lead_smelting')

  event.custom({
    type: 'minecraft:blasting',
    category: 'blocks',
    cookingtime: 100,
    experience: 0.1,
    ingredient: { item: 'create:crushed_raw_lead' },
    result: { count: 1, id: 'tfmg:lead_ingot' }
  }).id('industrial_colonies:lead/create_crushed_raw_lead_blasting')

  // Existing-world migration only. Mekanism's duplicate lead ore generation
  // is disabled and these forms no longer have normal production recipes.
  const legacyConversions = [
    ['mekanism:lead_ore', 'tfmg:lead_ore', 1],
    ['mekanism:deepslate_lead_ore', 'tfmg:deepslate_lead_ore', 1],
    ['mekanism:raw_lead', 'tfmg:raw_lead', 1],
    ['mekanism:block_raw_lead', 'tfmg:raw_lead', 9],
    ['mekanism:ingot_lead', 'tfmg:lead_ingot', 1],
    ['mekanism:nugget_lead', 'tfmg:lead_nugget', 1],
    ['mekanism:block_lead', 'tfmg:lead_ingot', 9]
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
    }).id(`industrial_colonies:lead/migrate_${path}`)
  })

  console.info(`[Industrial Colonies] Canonical TFMG lead loaded; removed ${removedLeadDuplicates.length} duplicate recipes.`)
})
