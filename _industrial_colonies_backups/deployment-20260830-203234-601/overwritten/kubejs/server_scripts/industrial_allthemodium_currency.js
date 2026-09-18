// Industrial Colonies - manufactured Allthemodium research currencies
//
// The stock mod treats Allthemodium, Vibranium, and Unobtainium as mined
// metals.  This pack treats them as manufactured elements instead.  Every
// ore/raw/furnace/Mekanism producer and every AllTheCompressed storage alias
// is removed before the controlled Create-only routes below are registered.
//
// The source audit for this policy is:
//   work/industrial-audit/ALLTHEMODIUM_CURRENCY_ROUTE_AUDIT.{md,json}

// No recipe in this file uses Tinkers' Construct, molten ATM fluids, Piglich
// Hearts, or a normal crafting/furnace recipe.

const ATM_CURRENCY_METALS = [
  {
    id: 'allthemodium',
    ingot: 'allthemodium:allthemodium_ingot',
    nugget: 'allthemodium:allthemodium_nugget',
    dust: 'allthemodium:allthemodium_dust',
    block: 'allthemodium:allthemodium_block',
    plate: 'allthemodium:allthemodium_plate',
    gear: 'allthemodium:allthemodium_gear',
    rod: 'allthemodium:allthemodium_rod'
  },
  {
    id: 'vibranium',
    ingot: 'allthemodium:vibranium_ingot',
    nugget: 'allthemodium:vibranium_nugget',
    dust: 'allthemodium:vibranium_dust',
    block: 'allthemodium:vibranium_block',
    plate: 'allthemodium:vibranium_plate',
    gear: 'allthemodium:vibranium_gear',
    rod: 'allthemodium:vibranium_rod'
  },
  {
    id: 'unobtainium',
    ingot: 'allthemodium:unobtainium_ingot',
    nugget: 'allthemodium:unobtainium_nugget',
    dust: 'allthemodium:unobtainium_dust',
    block: 'allthemodium:unobtainium_block',
    plate: 'allthemodium:unobtainium_plate',
    gear: 'allthemodium:unobtainium_gear',
    rod: 'allthemodium:unobtainium_rod'
  }
]

const ATM_CURRENCY_ALLOYS = [
  {
    id: 'vibranium_allthemodium_alloy',
    ingot: 'allthemodium:vibranium_allthemodium_alloy_ingot',
    dust: 'allthemodium:vibranium_allthemodium_alloy_dust',
    block: 'allthemodium:vibranium_allthemodium_alloy_block',
    constituents: [
      'allthemodium:allthemodium_ingot',
      'allthemodium:vibranium_ingot'
    ]
  },
  {
    id: 'unobtainium_allthemodium_alloy',
    ingot: 'allthemodium:unobtainium_allthemodium_alloy_ingot',
    dust: 'allthemodium:unobtainium_allthemodium_alloy_dust',
    block: 'allthemodium:unobtainium_allthemodium_alloy_block',
    constituents: [
      'allthemodium:allthemodium_ingot',
      'allthemodium:unobtainium_ingot'
    ]
  },
  {
    id: 'unobtainium_vibranium_alloy',
    ingot: 'allthemodium:unobtainium_vibranium_alloy_ingot',
    dust: 'allthemodium:unobtainium_vibranium_alloy_dust',
    block: 'allthemodium:unobtainium_vibranium_alloy_block',
    constituents: [
      'allthemodium:vibranium_ingot',
      'allthemodium:unobtainium_ingot'
    ]
  }
]

const ATM_DISABLED_OUTPUTS = [
  'allthemodium:allthemodium_block',
  'allthemodium:allthemodium_clump',
  'allthemodium:allthemodium_crystal',
  'allthemodium:allthemodium_dust',
  'allthemodium:allthemodium_gear',
  'allthemodium:allthemodium_ingot',
  'allthemodium:allthemodium_nugget',
  'allthemodium:allthemodium_ore',
  'allthemodium:allthemodium_plate',
  'allthemodium:allthemodium_rod',
  'allthemodium:allthemodium_shard',
  'allthemodium:allthemodium_slate_ore',
  'allthemodium:dirty_allthemodium_dust',
  'allthemodium:dirty_unobtainium_dust',
  'allthemodium:dirty_vibranium_dust',
  'allthemodium:molten_allthemodium_bucket',
  'allthemodium:molten_unobtainium_bucket',
  'allthemodium:molten_vibranium_bucket',
  'allthemodium:other_vibranium_ore',
  'allthemodium:raw_allthemodium',
  'allthemodium:raw_allthemodium_block',
  'allthemodium:raw_unobtainium',
  'allthemodium:raw_unobtainium_block',
  'allthemodium:raw_vibranium',
  'allthemodium:raw_vibranium_block',
  'allthemodium:unobtainium_allthemodium_alloy_block',
  'allthemodium:unobtainium_allthemodium_alloy_dust',
  'allthemodium:unobtainium_allthemodium_alloy_ingot',
  'allthemodium:unobtainium_block',
  'allthemodium:unobtainium_clump',
  'allthemodium:unobtainium_crystal',
  'allthemodium:unobtainium_dust',
  'allthemodium:unobtainium_gear',
  'allthemodium:unobtainium_ingot',
  'allthemodium:unobtainium_nugget',
  'allthemodium:unobtainium_ore',
  'allthemodium:unobtainium_plate',
  'allthemodium:unobtainium_rod',
  'allthemodium:unobtainium_shard',
  'allthemodium:unobtainium_vibranium_alloy_block',
  'allthemodium:unobtainium_vibranium_alloy_dust',
  'allthemodium:unobtainium_vibranium_alloy_ingot',
  'allthemodium:vapor_allthemodium_bucket',
  'allthemodium:vapor_unobtainium_bucket',
  'allthemodium:vapor_vibranium_bucket',
  'allthemodium:vibranium_allthemodium_alloy_block',
  'allthemodium:vibranium_allthemodium_alloy_dust',
  'allthemodium:vibranium_allthemodium_alloy_ingot',
  'allthemodium:vibranium_block',
  'allthemodium:vibranium_clump',
  'allthemodium:vibranium_crystal',
  'allthemodium:vibranium_dust',
  'allthemodium:vibranium_gear',
  'allthemodium:vibranium_ingot',
  'allthemodium:vibranium_nugget',
  'allthemodium:vibranium_ore',
  'allthemodium:vibranium_plate',
  'allthemodium:vibranium_rod',
  'allthemodium:vibranium_shard'
]

const ATM_COMPRESSED_FAMILIES = [
  'allthemodium_block',
  'vibranium_block',
  'unobtainium_block',
  'raw_allthemodium_block',
  'raw_vibranium_block',
  'raw_unobtainium_block',
  'vibranium_allthemodium_alloy_block',
  'unobtainium_allthemodium_alloy_block',
  'unobtainium_vibranium_alloy_block'
]

const ATM_MEKANISM_PROCESSING_SUFFIXES = [
  'clump/from_ore',
  'clump/from_raw_block',
  'clump/from_raw_ore',
  'clump/from_shard',
  'crystal/from_slurry',
  'dirty_dust/from_clump',
  'dust/from_dirty_dust',
  'dust/from_ingot',
  'dust/from_ore',
  'dust/from_raw_block',
  'dust/from_raw_ore',
  'shard/from_crystal',
  'shard/from_ore',
  'shard/from_raw_block',
  'shard/from_raw_ore',
  'slurry/clean',
  'slurry/dirty/from_ore',
  'slurry/dirty/from_raw_block',
  'slurry/dirty/from_raw_ore'
]

const ATM_TCONSTRUCT_RECIPE_TYPES = [
  'tconstruct:alloy',
  'tconstruct:casting_basin',
  'tconstruct:casting_table',
  'tconstruct:material',
  'tconstruct:material_fluid',
  'tconstruct:melting'
]

const atmRepeatedItems = (item, count) => {
  const ingredients = []
  for (let index = 0; index < count; index++) {
    ingredients.push({ item: item })
  }
  return ingredients
}

const atmDeploying = (transitional, ingredient) => ({
  type: 'create:deploying',
  ingredients: [{ item: transitional }, { item: ingredient }],
  results: [{ id: transitional }]
})

const atmPressing = transitional => ({
  type: 'create:pressing',
  ingredients: [{ item: transitional }],
  results: [{ id: transitional }]
})

ServerEvents.tags('item', event => {
  const ores = {
    allthemodium: [
      'allthemodium:allthemodium_ore',
      'allthemodium:allthemodium_slate_ore'
    ],
    vibranium: [
      'allthemodium:vibranium_ore',
      'allthemodium:other_vibranium_ore'
    ],
    unobtainium: ['allthemodium:unobtainium_ore']
  }

  Object.entries(ores).forEach(entry => {
    const metal = entry[0]
    const oreItems = entry[1]
    event.removeAll(`c:ores/${metal}`)
    oreItems.forEach(item => event.remove('c:ores', item))
  })

  ;[
    ['allthemodium', 'allthemodium:raw_allthemodium', 'allthemodium:raw_allthemodium_block'],
    ['vibranium', 'allthemodium:raw_vibranium', 'allthemodium:raw_vibranium_block'],
    ['unobtainium', 'allthemodium:raw_unobtainium', 'allthemodium:raw_unobtainium_block']
  ].forEach(entry => {
    const metal = entry[0]
    const raw = entry[1]
    const rawBlock = entry[2]
    event.removeAll(`c:raw_materials/${metal}`)
    event.remove('c:raw_materials', raw)
    event.removeAll(`c:storage_blocks/raw_${metal}`)
    event.remove('c:storage_blocks', rawBlock)
  })

  event.remove('c:ores_in_ground/stone', 'allthemodium:allthemodium_ore')
  event.remove('c:ores_in_ground/deepslate', 'allthemodium:allthemodium_slate_ore')
  event.remove('c:ores_in_ground/netherrack', 'allthemodium:vibranium_ore')
  event.remove('c:ores_in_ground/ancient_stone', 'allthemodium:other_vibranium_ore')
  event.remove('c:ores_in_ground/end_stone', 'allthemodium:unobtainium_ore')
})

ServerEvents.tags('block', event => {
  const ores = {
    allthemodium: [
      'allthemodium:allthemodium_ore',
      'allthemodium:allthemodium_slate_ore'
    ],
    vibranium: [
      'allthemodium:vibranium_ore',
      'allthemodium:other_vibranium_ore'
    ],
    unobtainium: ['allthemodium:unobtainium_ore']
  }

  Object.entries(ores).forEach(entry => {
    const metal = entry[0]
    const oreBlocks = entry[1]
    event.removeAll(`c:ores/${metal}`)
    oreBlocks.forEach(block => event.remove('c:ores', block))
  })

  ;[
    ['allthemodium', 'allthemodium:raw_allthemodium_block'],
    ['vibranium', 'allthemodium:raw_vibranium_block'],
    ['unobtainium', 'allthemodium:raw_unobtainium_block']
  ].forEach(entry => {
    const metal = entry[0]
    const rawBlock = entry[1]
    event.removeAll(`c:storage_blocks/raw_${metal}`)
    event.remove('c:storage_blocks', rawBlock)
  })

  event.remove('c:ores_in_ground/stone', 'allthemodium:allthemodium_ore')
  event.remove('c:ores_in_ground/deepslate', 'allthemodium:allthemodium_slate_ore')
  event.remove('c:ores_in_ground/netherrack', 'allthemodium:vibranium_ore')
  event.remove('c:ores_in_ground/ancient_stone', 'allthemodium:other_vibranium_ore')
  event.remove('c:ores_in_ground/end_stone', 'allthemodium:unobtainium_ore')
})

ServerEvents.recipes(event => {
  // Remove every audited solid/container producer.  This includes all 18
  // furnace recipes, the nugget/block/raw conversions, manual components,
  // and any conditional item cast that might become active later.
  ATM_DISABLED_OUTPUTS.forEach(output => event.remove({ output: output }))

  // AllTheCompressed is valid for the bulk-matter megaproject, but the 81 ATM
  // aliases are deliberately not currency storage.  Removing every alias
  // output also removes every level-to-level compression/decompression path.
  ATM_COMPRESSED_FAMILIES.forEach(family => {
    for (let level = 1; level <= 9; level++) {
      event.remove({ output: `allthecompressed:${family}_${level}x` })
    }
  })

  // Remove all 57 active Mekanism ore-processing recipes by exact audited ID.
  // This closes enriching, purifying, injecting, dissolution, washing,
  // crystallizing, and the Crusher recipes already retired elsewhere.
  ATM_CURRENCY_METALS.forEach(metal => {
    ATM_MEKANISM_PROCESSING_SUFFIXES.forEach(suffix => {
      event.remove({ id: `allthemodium:processing/${metal.id}/${suffix}` })
    })
  })

  // These six recipe types account for all 69 audited TConstruct-conditional
  // ATM recipes, including the equipment-salvage multiplication exploit.
  ATM_TCONSTRUCT_RECIPE_TYPES.forEach(type => {
    event.remove({ mod: 'allthemodium', type: type })
  })

  const sequencedElement = (id, input, output, loops, sequence) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: input },
      loops: loops,
      results: [{ id: output }],
      sequence: sequence,
      transitional_item: { id: input }
    }).id(id)
  }

  // Exotic Metallurgy: bulk steel is repeatedly doped with Cobalt and Osmium
  // and mechanically worked.  One ingot requires a real deployer/press line.
  sequencedElement(
    'industrial_colonies:currency/allthemodium/synthesis',
    'tfmg:steel_ingot',
    'allthemodium:allthemodium_ingot',
    4,
    [
      atmDeploying('tfmg:steel_ingot', 'modernfoundry:cobalt_ingot'),
      atmDeploying('tfmg:steel_ingot', 'mekanism:ingot_osmium'),
      atmDeploying('tfmg:steel_ingot', 'tfmg:steel_mechanism'),
      atmPressing('tfmg:steel_ingot')
    ]
  )

  // Yellorium Refinement: Allthemodium becomes the substrate for Vibranium;
  // the compound is produced by the owned Yellorium factory at this node.
  sequencedElement(
    'industrial_colonies:currency/vibranium/synthesis',
    'allthemodium:allthemodium_ingot',
    'allthemodium:vibranium_ingot',
    4,
    [
      atmDeploying('allthemodium:allthemodium_ingot', 'industrial_colonies:yellorium_compound'),
      atmDeploying('allthemodium:allthemodium_ingot', 'modernfoundry:cobalt_ingot'),
      atmDeploying('allthemodium:allthemodium_ingot', 'tfmg:steel_mechanism'),
      atmPressing('allthemodium:allthemodium_ingot')
    ]
  )

  // Nuclear Age: Vibranium is irradiated/worked with the three converging
  // branches represented by Radiance, Yellorium, and Ultimate electronics.
  sequencedElement(
    'industrial_colonies:currency/unobtainium/synthesis',
    'allthemodium:vibranium_ingot',
    'allthemodium:unobtainium_ingot',
    4,
    [
      atmDeploying('allthemodium:vibranium_ingot', 'create:refined_radiance'),
      atmDeploying('allthemodium:vibranium_ingot', 'industrial_colonies:yellorium_compound'),
      atmDeploying('allthemodium:vibranium_ingot', 'mekanism:ultimate_control_circuit'),
      atmPressing('allthemodium:vibranium_ingot')
    ]
  )

  // Safe, lossless factory recycling.  No recipe produces ore/raw/slurry
  // forms and no conversion yields more metal than it consumes.
  ATM_CURRENCY_METALS.forEach(metal => {
    const root = `industrial_colonies:currency/${metal.id}`

    event.custom({
      type: 'create:crushing',
      ingredients: [{ item: metal.ingot }],
      processing_time: 150,
      results: [{ id: metal.dust }]
    }).id(`${root}/dust_from_ingot`)

    event.custom({
      type: 'create:compacting',
      ingredients: [{ item: metal.dust }],
      results: [{ id: metal.ingot }]
    }).id(`${root}/ingot_from_dust`)

    event.custom({
      type: 'create:cutting',
      ingredients: [{ item: metal.ingot }],
      processing_time: 100,
      results: [{ count: 9, id: metal.nugget }]
    }).id(`${root}/nuggets_from_ingot`)

    event.custom({
      type: 'create:compacting',
      ingredients: atmRepeatedItems(metal.nugget, 9),
      results: [{ id: metal.ingot }]
    }).id(`${root}/ingot_from_nuggets`)

    event.custom({
      type: 'create:compacting',
      ingredients: atmRepeatedItems(metal.ingot, 9),
      results: [{ id: metal.block }]
    }).id(`${root}/block_from_ingots`)

    event.custom({
      type: 'create:crushing',
      ingredients: [{ item: metal.block }],
      processing_time: 250,
      results: [{ count: 9, id: metal.ingot }]
    }).id(`${root}/ingots_from_block`)

    event.custom({
      type: 'create:pressing',
      ingredients: [{ item: metal.ingot }],
      results: [{ id: metal.plate }]
    }).id(`${root}/plate`)

    event.custom({
      type: 'create:compacting',
      ingredients: atmRepeatedItems(metal.ingot, 4),
      results: [{ id: metal.gear }]
    }).id(`${root}/gear`)

    event.custom({
      type: 'create:cutting',
      ingredients: [{ item: metal.ingot }],
      processing_time: 100,
      results: [{ count: 2, id: metal.rod }]
    }).id(`${root}/rods`)
  })

  // Nuclear Age pairwise alloys.  Superheated Create mixing replaces the
  // absent TConstruct 9000-degree alloy/casting/Piglich-Heart route.
  ATM_CURRENCY_ALLOYS.forEach(alloy => {
    const root = `industrial_colonies:currency/${alloy.id}`

    event.custom({
      type: 'create:mixing',
      heat_requirement: 'superheated',
      ingredients: [
        { item: alloy.constituents[0] },
        { item: alloy.constituents[1] },
        { item: 'mekanism:alloy_atomic' },
        { item: 'create:refined_radiance' }
      ],
      results: [{ id: alloy.ingot }]
    }).id(`${root}/synthesis`)

    event.custom({
      type: 'create:crushing',
      ingredients: [{ item: alloy.ingot }],
      processing_time: 150,
      results: [{ id: alloy.dust }]
    }).id(`${root}/dust_from_ingot`)

    event.custom({
      type: 'create:compacting',
      ingredients: [{ item: alloy.dust }],
      results: [{ id: alloy.ingot }]
    }).id(`${root}/ingot_from_dust`)

    event.custom({
      type: 'create:compacting',
      ingredients: atmRepeatedItems(alloy.ingot, 9),
      results: [{ id: alloy.block }]
    }).id(`${root}/block_from_ingots`)

    event.custom({
      type: 'create:crushing',
      ingredients: [{ item: alloy.block }],
      processing_time: 250,
      results: [{ count: 9, id: alloy.ingot }]
    }).id(`${root}/ingots_from_block`)
  })

  console.info('[Industrial Colonies] Manufactured ATM currencies loaded: 3 staged elements, 3 staged alloys, no mined or dungeon acquisition.')
})
