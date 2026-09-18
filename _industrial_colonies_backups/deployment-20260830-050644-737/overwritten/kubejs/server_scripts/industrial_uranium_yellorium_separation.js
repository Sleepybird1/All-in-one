// Industrial Colonies - keep Mekanism uranium and Extreme Reactors Yellorium
// as distinct material families.
//
// Extreme Reactors intentionally places Yellorite, Raw Yellorium, Yellorium
// Ingots, and Yellorium Blocks in generic uranium tags. In this pack that
// makes Create, Mekanism, and Modern Foundry treat Yellorium as Mekanism
// uranium, bypassing both Yellorium Refinement and the isotope-material chain.

ServerEvents.tags('item', event => {
  const canonicalUraniumItemTags = {
    'c:ores/uranium': ['mekanism:uranium_ore', 'mekanism:deepslate_uranium_ore'],
    'c:raw_materials/uranium': ['mekanism:raw_uranium'],
    'c:storage_blocks/raw_uranium': ['mekanism:block_raw_uranium'],
    'c:ingots/uranium': ['mekanism:ingot_uranium'],
    'c:nuggets/uranium': ['mekanism:nugget_uranium'],
    'c:dusts/uranium': ['mekanism:dust_uranium'],
    'c:dirty_dusts/uranium': ['mekanism:dirty_dust_uranium'],
    'c:clumps/uranium': ['mekanism:clump_uranium'],
    'c:shards/uranium': ['mekanism:shard_uranium'],
    'c:crystals/uranium': ['mekanism:crystal_uranium'],
    'c:storage_blocks/uranium': ['mekanism:block_uranium'],
    'forge:storage_blocks/uranium': ['mekanism:block_uranium']
  }

  Object.entries(canonicalUraniumItemTags).forEach(entry => {
    const tag = entry[0]
    const items = entry[1]
    event.removeAll(tag)
    event.add(tag, items)
  })
})

ServerEvents.tags('block', event => {
  const canonicalUraniumBlockTags = {
    'c:ores/uranium': ['mekanism:uranium_ore', 'mekanism:deepslate_uranium_ore'],
    'c:storage_blocks/raw_uranium': ['mekanism:block_raw_uranium'],
    'c:storage_blocks/uranium': ['mekanism:block_uranium'],
    'forge:storage_blocks/uranium': ['mekanism:block_uranium']
  }

  Object.entries(canonicalUraniumBlockTags).forEach(entry => {
    const tag = entry[0]
    const blocks = entry[1]
    event.removeAll(tag)
    event.add(tag, blocks)
  })
})

ServerEvents.recipes(event => {
  // Furnace recipes cannot currently resolve an owning FTB Team. Remove the
  // direct ore/raw/dust cooking routes and use team-gated Create/Mekanism
  // processing instead. This also closes the Create crushed-uranium shortcut
  // that originally exposed the Yellorite -> Mekanism uranium conversion.
  const removedUraniumFurnaceRoutes = [
    'create:smelting/ingot_uranium_compat_ic2',
    'create:smelting/ingot_uranium_compat_immersiveengineering',
    'create:smelting/ingot_uranium_compat_mekanism',
    'create:blasting/ingot_uranium_compat_ic2',
    'create:blasting/ingot_uranium_compat_immersiveengineering',
    'create:blasting/ingot_uranium_compat_mekanism',
    'mekanism:processing/uranium/ingot/from_dust_smelting',
    'mekanism:processing/uranium/ingot/from_dust_blasting',
    'mekanism:processing/uranium/ingot/from_ore_smelting',
    'mekanism:processing/uranium/ingot/from_ore_blasting',
    'mekanism:processing/uranium/ingot/from_raw_smelting',
    'mekanism:processing/uranium/ingot/from_raw_blasting'
  ]

  removedUraniumFurnaceRoutes.forEach(id => event.remove({ id: id }))

  // Physical uranium powder is consolidated in a Create basin. The exact
  // recipe is owned by Isotope Materials in additional_recipe_stages.json.
  event.custom({
    type: 'create:compacting',
    ingredients: [{ item: 'mekanism:dust_uranium' }],
    results: [{ id: 'mekanism:ingot_uranium' }]
  }).id('industrial_colonies:materials/uranium/sintered_ingot')

  console.info(`[Industrial Colonies] Uranium/Yellorium separation loaded; removed ${removedUraniumFurnaceRoutes.length} ungated furnace routes.`)
})
