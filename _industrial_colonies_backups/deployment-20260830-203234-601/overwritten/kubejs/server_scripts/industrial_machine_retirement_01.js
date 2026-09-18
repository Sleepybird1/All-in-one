// Industrial Colonies - Create-first machine retirement, slice 01
//
// These generic Mekanism machines duplicate factory roles already owned by
// Create or, later, AE2. Their construction paths and factory variants are
// removed. Unique Crusher transformations are retained as Create crushing
// recipes so the Mekanism ore-processing chain and niche conversions remain
// usable without a parallel generic Crusher line.

ServerEvents.recipes(event => {
  const removedMachineRecipes = [
    'mekanism:crusher',
    'mekanism:precision_sawmill',
    'mekanism:energized_smelter',
    'mekanism:formulaic_assemblicator',
    'mekanism:factory/basic/crushing',
    'mekanism:factory/advanced/crushing',
    'mekanism:factory/elite/crushing',
    'mekanism:factory/ultimate/crushing',
    'mekanism:factory/basic/sawing',
    'mekanism:factory/advanced/sawing',
    'mekanism:factory/elite/sawing',
    'mekanism:factory/ultimate/sawing',
    'mekanism:factory/basic/smelting',
    'mekanism:factory/advanced/smelting',
    'mekanism:factory/elite/smelting',
    'mekanism:factory/ultimate/smelting'
  ]

  removedMachineRecipes.forEach(id => event.remove({ id: id }))

  // With the Crusher and Sawmill families retired, their private processing
  // categories should not remain as misleading recipe-viewer dead ends.
  event.remove({ type: 'mekanism:crushing' })
  event.remove({ type: 'mekanism:sawing' })

  const crusherPorts = [
    { input: '#c:clumps/copper', output: 'mekanism:dirty_dust_copper', count: 1, source: 'processing/copper/dirty_dust/from_clump' },
    { input: '#c:clumps/gold', output: 'mekanism:dirty_dust_gold', count: 1, source: 'processing/gold/dirty_dust/from_clump' },
    { input: '#c:clumps/iron', output: 'mekanism:dirty_dust_iron', count: 1, source: 'processing/iron/dirty_dust/from_clump' },
    { input: '#c:clumps/lead', output: 'mekanism:dirty_dust_lead', count: 1, source: 'processing/lead/dirty_dust/from_clump' },
    { input: '#c:clumps/osmium', output: 'mekanism:dirty_dust_osmium', count: 1, source: 'processing/osmium/dirty_dust/from_clump' },
    { input: '#c:clumps/tin', output: 'mekanism:dirty_dust_tin', count: 1, source: 'processing/tin/dirty_dust/from_clump' },
    { input: '#c:clumps/uranium', output: 'mekanism:dirty_dust_uranium', count: 1, source: 'processing/uranium/dirty_dust/from_clump' },
    { input: '#c:ores/netherite_scrap', output: 'mekanism:dirty_netherite_scrap', count: 3, source: 'processing/netherite/ancient_debris_to_dirty_scrap' },
    { input: 'minecraft:coal', output: 'mekanism:dust_coal', count: 1, source: 'processing/coal/to_dust' },
    { input: '#c:gems/diamond', output: 'mekanism:dust_diamond', count: 1, source: 'processing/diamond/to_dust' },
    { input: '#c:gems/emerald', output: 'mekanism:dust_emerald', count: 1, source: 'processing/emerald/to_dust' },
    { input: '#c:gems/fluorite', output: 'mekanism:dust_fluorite', count: 1, source: 'processing/fluorite/to_dust' },
    { input: '#c:gems/lapis', output: 'mekanism:dust_lapis_lazuli', count: 1, source: 'processing/lapis_lazuli/to_dust' },
    { input: '#c:obsidians/normal', output: 'mekanism:dust_obsidian', count: 4, source: 'crushing/obsidian_to_dust' },
    { input: '#c:gems/quartz', output: 'mekanism:dust_quartz', count: 1, source: 'processing/quartz/to_dust' },
    { input: 'minecraft:polished_andesite_stairs', output: 'minecraft:andesite_stairs', count: 1, source: 'crushing/andesite/stairs_from_polished_stairs' },
    { input: 'minecraft:polished_blackstone_stairs', output: 'minecraft:blackstone_stairs', count: 1, source: 'crushing/blackstone/polished_stairs_to_stairs' },
    { input: 'minecraft:polished_blackstone_wall', output: 'minecraft:blackstone_wall', count: 1, source: 'crushing/blackstone/polished_wall_to_wall' },
    { input: 'minecraft:quartz_bricks', output: 'minecraft:chiseled_quartz_block', count: 1, source: 'crushing/quartz/bricks_to_chiseled' },
    { input: 'minecraft:deepslate_tile_stairs', output: 'minecraft:cobbled_deepslate_stairs', count: 1, source: 'crushing/deepslate/tile_stairs_to_cobbled' },
    { input: 'minecraft:deepslate_tile_wall', output: 'minecraft:cobbled_deepslate_wall', count: 1, source: 'crushing/deepslate/tile_wall_to_cobbled' },
    { input: 'minecraft:nether_bricks', output: 'minecraft:cracked_nether_bricks', count: 1, source: 'crushing/nether_bricks_to_cracked_nether_bricks' },
    { input: 'minecraft:polished_diorite_stairs', output: 'minecraft:diorite_stairs', count: 1, source: 'crushing/diorite/stairs_from_polished_stairs' },
    { input: 'minecraft:music_disc_5', output: 'minecraft:disc_fragment_5', count: 9, source: 'crushing/break_disc_5' },
    { input: 'minecraft:polished_granite_stairs', output: 'minecraft:granite_stairs', count: 1, source: 'crushing/granite/stairs_from_polished_stairs' },
    { input: 'minecraft:dripstone_block', output: 'minecraft:pointed_dripstone', count: 4, source: 'crushing/pointed_dripstone_from_block' },
    { input: 'minecraft:cracked_polished_blackstone_bricks', output: 'minecraft:polished_blackstone', count: 1, source: 'crushing/blackstone/from_cracked_bricks' },
    { input: 'minecraft:purpur_pillar', output: 'minecraft:purpur_block', count: 1, source: 'crushing/purpur_block_from_pillar' },
    { input: 'minecraft:smooth_quartz', output: 'minecraft:quartz_bricks', count: 1, source: 'crushing/quartz/smooth_to_bricks' },
    { input: 'minecraft:chiseled_quartz_block', output: 'minecraft:quartz_pillar', count: 1, source: 'crushing/quartz/chiseled_to_pillar' },
    { input: 'minecraft:quartz_block', output: 'minecraft:smooth_quartz', count: 1, source: 'crushing/quartz/to_smooth_quartz' },
    { input: 'minecraft:quartz_stairs', output: 'minecraft:smooth_quartz_stairs', count: 1, source: 'crushing/quartz/stairs_to_smooth_stairs' },
    { input: '#c:rods/breeze', output: 'minecraft:wind_charge', count: 6, source: 'crushing/breeze_rod' }
  ]

  crusherPorts.forEach(port => {
    const ingredient = port.input.charAt(0) === '#'
      ? { tag: port.input.substring(1) }
      : { item: port.input }

    event.custom({
      type: 'create:crushing',
      ingredients: [ingredient],
      processing_time: 150,
      results: [{ count: port.count, id: port.output }]
    }).id(`industrial_colonies:create_first/${port.source}`)
  })

  console.info(`[Industrial Colonies] Create-first machine retirement loaded; retired ${removedMachineRecipes.length} construction recipes and ported ${crusherPorts.length} Crusher transformations.`)
})
