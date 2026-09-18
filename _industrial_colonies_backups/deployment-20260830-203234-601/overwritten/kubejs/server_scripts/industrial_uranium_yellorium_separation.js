// Industrial Colonies - keep Mekanism uranium and Extreme Reactors Yellorium
// as distinct material families.
//
// Extreme Reactors intentionally places Yellorite, Raw Yellorium, Yellorium
// Ingots, and Yellorium Blocks in generic uranium tags. It also registers
// c:ingots/uranium and c:storage_blocks/uranium directly as reactor fuel in
// ReactorGameData. In this pack those two ITEM tags must therefore stay empty:
// otherwise a physical Mekanism Uranium Ingot bypasses the UF6/fissile chain.

ServerEvents.tags('item', event => {
  const canonicalUraniumItemTags = {
    'c:ores/uranium': ['mekanism:uranium_ore', 'mekanism:deepslate_uranium_ore'],
    'c:raw_materials/uranium': ['mekanism:raw_uranium'],
    'c:storage_blocks/raw_uranium': ['mekanism:block_raw_uranium'],
    'c:ingots/uranium': [],
    'c:nuggets/uranium': ['mekanism:nugget_uranium'],
    'c:dusts/uranium': ['mekanism:dust_uranium'],
    'c:dirty_dusts/uranium': ['mekanism:dirty_dust_uranium'],
    'c:clumps/uranium': ['mekanism:clump_uranium'],
    'c:shards/uranium': ['mekanism:shard_uranium'],
    'c:crystals/uranium': ['mekanism:crystal_uranium'],
    'c:storage_blocks/uranium': [],
    'forge:storage_blocks/uranium': []
  }

  Object.entries(canonicalUraniumItemTags).forEach(entry => {
    const tag = entry[0]
    const items = entry[1]
    event.removeAll(tag)
    if (items.length > 0) {
      event.add(tag, items)
    }
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

  // Modern Foundry provides a complete ore/raw -> molten uranium -> cast
  // ingot alternate path. That path never enters the intended Mekanism
  // enrichment chain, so the whole uranium material family is disabled while
  // every normal Mekanism ore-processing tier remains available and staged.
  const removedModernFoundryUraniumRoutes = [
    'modernfoundry:smeltery/casting/metal/uranium/block',
    'modernfoundry:smeltery/casting/metal/uranium/coin_gold_cast',
    'modernfoundry:smeltery/casting/metal/uranium/coin_sand_cast',
    'modernfoundry:smeltery/casting/metal/uranium/gear_gold_cast',
    'modernfoundry:smeltery/casting/metal/uranium/gear_sand_cast',
    'modernfoundry:smeltery/casting/metal/uranium/ingot_gold_cast',
    'modernfoundry:smeltery/casting/metal/uranium/ingot_sand_cast',
    'modernfoundry:smeltery/casting/metal/uranium/nugget_gold_cast',
    'modernfoundry:smeltery/casting/metal/uranium/nugget_sand_cast',
    'modernfoundry:smeltery/casting/metal/uranium/plate_gold_cast',
    'modernfoundry:smeltery/casting/metal/uranium/plate_sand_cast',
    'modernfoundry:smeltery/melting/metal/uranium/block',
    'modernfoundry:smeltery/melting/metal/uranium/coin',
    'modernfoundry:smeltery/melting/metal/uranium/dust',
    'modernfoundry:smeltery/melting/metal/uranium/gear',
    'modernfoundry:smeltery/melting/metal/uranium/ingot',
    'modernfoundry:smeltery/melting/metal/uranium/nugget',
    'modernfoundry:smeltery/melting/metal/uranium/ore_dense',
    'modernfoundry:smeltery/melting/metal/uranium/ore_singular',
    'modernfoundry:smeltery/melting/metal/uranium/ore_sparse',
    'modernfoundry:smeltery/melting/metal/uranium/oreberry',
    'modernfoundry:smeltery/melting/metal/uranium/plate',
    'modernfoundry:smeltery/melting/metal/uranium/raw',
    'modernfoundry:smeltery/melting/metal/uranium/raw_block',
    'modernfoundry:smeltery/melting/metal/uranium/sheetmetal'
  ]

  removedModernFoundryUraniumRoutes.forEach(id => event.remove({ id: id }))

  // These Mekanism recipes normally consume c:ingots/uranium. Recreate them
  // with exact Mekanism inputs so clearing the reactor-fuel tag does not break
  // legitimate physical processing or storage. Their original IDs are kept,
  // preserving the existing exact recipe-stage assignments.
  const removedUraniumTagRecipes = [
    'mekanism:processing/uranium/dust/from_ingot',
    'mekanism:processing/uranium/storage_blocks/from_ingots',
    'mekanism:processing/uranium/yellow_cake_uranium'
  ]

  removedUraniumTagRecipes.forEach(id => event.remove({ id: id }))

  event.custom({
    type: 'mekanism:crushing',
    input: { count: 1, item: 'mekanism:ingot_uranium' },
    output: { count: 1, id: 'mekanism:dust_uranium' }
  }).id('mekanism:processing/uranium/dust/from_ingot')

  event.custom({
    type: 'minecraft:crafting_shaped',
    category: 'misc',
    key: { U: { item: 'mekanism:ingot_uranium' } },
    pattern: ['UUU', 'UUU', 'UUU'],
    result: { count: 1, id: 'mekanism:block_uranium' }
  }).id('mekanism:processing/uranium/storage_blocks/from_ingots')

  event.custom({
    type: 'mekanism:enriching',
    input: { count: 1, item: 'mekanism:ingot_uranium' },
    output: { count: 2, id: 'mekanism:yellow_cake_uranium' }
  }).id('mekanism:processing/uranium/yellow_cake_uranium')

  // Physical uranium powder is consolidated in a Create basin. The exact
  // recipe is owned by Isotope Materials in additional_recipe_stages.json.
  event.custom({
    type: 'create:compacting',
    ingredients: [{ item: 'mekanism:dust_uranium' }],
    results: [{ id: 'mekanism:ingot_uranium' }]
  }).id('industrial_colonies:materials/uranium/sintered_ingot')

  console.info(`[Industrial Colonies] Uranium/Yellorium separation loaded; removed ${removedUraniumFurnaceRoutes.length} furnace routes and ${removedModernFoundryUraniumRoutes.length} foundry bypasses.`)
})
