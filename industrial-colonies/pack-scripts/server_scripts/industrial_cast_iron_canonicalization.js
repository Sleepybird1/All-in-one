// Industrial Colonies - canonical solid cast iron
// TFMG owns player-facing cast-iron solids. Create Big Cannons keeps its
// 90 mB molten cast iron and cannon machinery as a compatible processing layer.

ServerEvents.tags('item', event => {
  const canonicalCastIronTags = {
    'c:ingots/cast_iron': ['tfmg:cast_iron_ingot'],
    'c:nuggets/cast_iron': ['tfmg:cast_iron_nugget'],
    'c:plates/cast_iron': ['tfmg:cast_iron_sheet'],
    'c:storage_blocks/cast_iron': ['tfmg:cast_iron_block']
  }

  Object.entries(canonicalCastIronTags).forEach(([tag, items]) => {
    event.removeAll(tag)
    event.add(tag, items)
  })
})

ServerEvents.recipes(event => {
  const removedCastIronDuplicates = [
    'createbigcannons:cast_iron_block',
    'createbigcannons:cast_iron_ingot_from_block',
    'createbigcannons:cast_iron_ingot_from_nuggets',
    'createbigcannons:cast_iron_nugget',
    'createbigcannons:compacting/iron_to_cast_iron_block',
    'createbigcannons:compacting/iron_to_cast_iron_ingot',
    'createbigcannons:compacting/forge_cast_iron_block',
    'createbigcannons:compacting/forge_cast_iron_ingot',
    'createbigcannons:compacting/forge_cast_iron_nugget'
  ]

  removedCastIronDuplicates.forEach(id => event.remove({ id: id }))

  // CBC molten cast iron is internally consistent at 90 mB per ingot.
  // Keep that cannon-processing loop, but return canonical TFMG solids.
  ;[
    [810, 'tfmg:cast_iron_block', 'block'],
    [90, 'tfmg:cast_iron_ingot', 'ingot'],
    [10, 'tfmg:cast_iron_nugget', 'nugget']
  ].forEach(entry => {
    const amount = entry[0]
    const output = entry[1]
    const path = entry[2]
    event.custom({
      type: 'create:compacting',
      ingredients: [{ type: 'neoforge:tag', amount: amount, tag: 'c:molten_cast_iron' }],
      results: [{ id: output }]
    }).id(`industrial_colonies:cast_iron/from_cbc_molten_${path}`)
  })

  // Existing-world migration only. CBC solid forms are no longer produced.
  ;[
    ['createbigcannons:cast_iron_ingot', 'tfmg:cast_iron_ingot', 1],
    ['createbigcannons:cast_iron_nugget', 'tfmg:cast_iron_nugget', 1],
    ['createbigcannons:cast_iron_block', 'tfmg:cast_iron_ingot', 9]
  ].forEach(entry => {
    const input = entry[0]
    const output = entry[1]
    const count = entry[2]
    const path = input.replace(':', '_').replace(/\//g, '_')
    event.custom({
      type: 'minecraft:crafting_shapeless',
      category: 'misc',
      ingredients: [{ item: input }],
      result: { count: count, id: output }
    }).id(`industrial_colonies:cast_iron/migrate_${path}`)
  })

  console.info(`[Industrial Colonies] Canonical TFMG cast iron loaded; removed ${removedCastIronDuplicates.length} duplicate recipes.`)
})
