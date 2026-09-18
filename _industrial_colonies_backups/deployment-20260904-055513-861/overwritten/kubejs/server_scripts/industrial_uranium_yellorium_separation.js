// Industrial Colonies - Yellorium-to-uranium enrichment boundary.
//
// Extreme Reactors intentionally places Yellorite, Raw Yellorium, Yellorium
// Ingots, and Yellorium Blocks in generic uranium tags. It also registers
// c:ingots/uranium and c:storage_blocks/uranium directly as reactor fuel in
// ReactorGameData. In this pack those two ITEM tags must therefore stay empty:
// otherwise a physical Mekanism Uranium Ingot bypasses the enrichment chain.

ServerEvents.tags('item', event => {
  const disabledYelloriteOres = [
    'bigreactors:yellorite_ore',
    'bigreactors:deepslate_yellorite_ore'
  ]

  // Yellorium is manufactured, never mined. Isolate the disabled ore/raw
  // family from both its narrow tags and the broad common acquisition tags so
  // tag-based crushers, miners, or future compatibility recipes cannot revive
  // a natural Yellorite entry point.
  event.removeAll('c:ores/yellorite')
  disabledYelloriteOres.forEach(item => event.remove('c:ores', item))
  event.remove('c:ores_in_ground/stone', 'bigreactors:yellorite_ore')
  event.remove('c:ores_in_ground/deepslate', 'bigreactors:deepslate_yellorite_ore')
  event.removeAll('c:raw_materials/yellorium')
  event.remove('c:raw_materials', 'bigreactors:raw_yellorium')
  event.removeAll('c:storage_blocks/raw_yellorium')
  event.remove('c:storage_blocks', 'bigreactors:raw_yellorium_block')

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
  const disabledYelloriteOres = [
    'bigreactors:yellorite_ore',
    'bigreactors:deepslate_yellorite_ore'
  ]

  event.removeAll('c:ores/yellorite')
  disabledYelloriteOres.forEach(block => event.remove('c:ores', block))
  event.removeAll('c:storage_blocks/raw_yellorium')
  event.remove('c:storage_blocks', 'bigreactors:raw_yellorium_block')

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

ServerEvents.tags('fluid', event => {
  // ReactorGameData registers c:yellorium as fluid reactor fuel. Molten
  // Yellorium is an early alloying intermediate in this pack, so that common
  // tag must be empty. The dedicated enriched pellet is the only first-tier
  // reactor source and is registered through Extreme Reactors' ModPack API.
  event.removeAll('c:yellorium')
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

  // Create's compat chain turns ore/raw uranium into washed nuggets and then
  // uses basin compacting as a furnace substitute. Uranium enrichment now
  // remains entirely inside real Mekanism machines.
  const removedCreateUraniumShortcuts = [
    'create:crushing/raw_uranium',
    'create:crushing/raw_uranium_block',
    'create:crushing/uranium_ore',
    'create:splashing/mekanism/crushed_raw_uranium',
    'create:splashing/ic2/crushed_raw_uranium',
    'create:splashing/immersiveengineering/crushed_raw_uranium',
    'create_mekanism_improvements:uranium_ingot'
  ]

  removedCreateUraniumShortcuts.forEach(id => event.remove({ id: id }))

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

  // These Mekanism recipes normally consume c:ingots/uranium. Remove all
  // common-tag variants before clearing the reactor-fuel tag. Storage and
  // Yellow Cake are recreated with exact inputs; ingot-to-dust recycling stays
  // retired because the Crusher is retired and the Enrichment Chamber already
  // has the deliberate ingot-to-Yellow-Cake operation.
  const removedUraniumTagRecipes = [
    'mekanism:processing/uranium/dust/from_ingot',
    'mekanism:processing/uranium/ingot/from_nuggets',
    'mekanism:processing/uranium/storage_blocks/from_ingots',
    'mekanism:processing/uranium/yellow_cake_uranium'
  ]

  removedUraniumTagRecipes.forEach(id => event.remove({ id: id }))

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

  // Isotope Materials is the sole Yellorium -> uranium bridge. It deliberately
  // produces raw uranium, never an ingot, Yellow Cake, or fuel, so the output
  // must still pass through the Mekanism physical and chemical chain.
  event.custom({
    type: 'mekanism:enriching',
    input: { count: 1, item: 'industrial_colonies:yellorium_compound' },
    output: { count: 1, id: 'mekanism:raw_uranium' }
  }).id('industrial_colonies:materials/uranium/raw_from_yellorium_compound')

  // The stock furnace conversion is intentionally absent. An Osmium
  // Compressor consolidates enriched uranium dust into metal while remaining
  // inside the owner-team Mekanism recipe-stage gate.
  event.custom({
    type: 'mekanism:compressing',
    chemical_input: { amount: 1, chemical: 'mekanism:osmium' },
    item_input: { count: 1, item: 'mekanism:dust_uranium' },
    output: { count: 1, id: 'mekanism:ingot_uranium' },
    per_tick_usage: true
  }).id('industrial_colonies:materials/uranium/osmium_compressed_ingot')

  console.info(`[Industrial Colonies] Yellorium-to-uranium boundary loaded; removed ${removedUraniumFurnaceRoutes.length} furnace, ${removedCreateUraniumShortcuts.length} Create, and ${removedModernFoundryUraniumRoutes.length} foundry bypasses.`)
})
