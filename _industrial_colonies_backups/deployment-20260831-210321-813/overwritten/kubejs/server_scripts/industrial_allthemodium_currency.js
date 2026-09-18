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

// Output-filter removals force KubeJS to resolve every recipe result.  Modern
// Foundry has config-backed tag outputs that cannot be queried this early, so
// the audited stock producer census is deliberately expressed as exact IDs.
const ATM_STOCK_PRODUCER_IDS = [
  'allthemodium:allthemodium_block',
  'allthemodium:allthemodium_dust_from_ore_crushing',
  'allthemodium:allthemodium_gear',
  'allthemodium:allthemodium_ingot',
  'allthemodium:allthemodium_ingot_from_block',
  'allthemodium:allthemodium_ingot_from_dust_blasting',
  'allthemodium:allthemodium_ingot_from_dust_smelting',
  'allthemodium:allthemodium_ingot_from_ore_blasting',
  'allthemodium:allthemodium_ingot_from_ore_smelting',
  'allthemodium:allthemodium_ingot_from_raw_blasting',
  'allthemodium:allthemodium_ingot_from_raw_smelting',
  'allthemodium:allthemodium_nugget_from_ingot',
  'allthemodium:allthemodium_plate',
  'allthemodium:allthemodium_rod',
  'allthemodium:raw_allthemodium_block',
  'allthemodium:raw_allthemodium_from_block',
  'allthemodium:raw_unobtainium_block',
  'allthemodium:raw_unobtainium_from_block',
  'allthemodium:raw_vibranium_block',
  'allthemodium:raw_vibranium_from_block',
  'allthemodium:unobtainium_allthemodium_alloy_block',
  'allthemodium:unobtainium_allthemodium_alloy_ingot_from_block',
  'allthemodium:unobtainium_block',
  'allthemodium:unobtainium_dust_from_ore_crushing',
  'allthemodium:unobtainium_gear',
  'allthemodium:unobtainium_ingot',
  'allthemodium:unobtainium_ingot_from_block',
  'allthemodium:unobtainium_ingot_from_dust_blasting',
  'allthemodium:unobtainium_ingot_from_dust_smelting',
  'allthemodium:unobtainium_ingot_from_ore_blasting',
  'allthemodium:unobtainium_ingot_from_ore_smelting',
  'allthemodium:unobtainium_ingot_from_raw_blasting',
  'allthemodium:unobtainium_ingot_from_raw_smelting',
  'allthemodium:unobtainium_nugget_from_ingot',
  'allthemodium:unobtainium_plate',
  'allthemodium:unobtainium_rod',
  'allthemodium:unobtainium_vibranium_alloy_block',
  'allthemodium:unobtainium_vibranium_alloy_ingot_from_block',
  'allthemodium:vibranium_allthemodium_alloy_block',
  'allthemodium:vibranium_allthemodium_alloy_ingot_from_block',
  'allthemodium:vibranium_block',
  'allthemodium:vibranium_dust_from_ore_crushing',
  'allthemodium:vibranium_gear',
  'allthemodium:vibranium_ingot',
  'allthemodium:vibranium_ingot_from_block',
  'allthemodium:vibranium_ingot_from_dust_blasting',
  'allthemodium:vibranium_ingot_from_dust_smelting',
  'allthemodium:vibranium_ingot_from_ore_blasting',
  'allthemodium:vibranium_ingot_from_ore_smelting',
  'allthemodium:vibranium_ingot_from_raw_blasting',
  'allthemodium:vibranium_ingot_from_raw_smelting',
  'allthemodium:vibranium_nugget_from_ingot',
  'allthemodium:vibranium_plate',
  'allthemodium:vibranium_rod'
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
  // Remove all 54 active non-Mekanism producers from the audited ATM JAR.
  // Conditional TConstruct producers are closed by exact recipe type below.
  ATM_STOCK_PRODUCER_IDS.forEach(id => event.remove({ id: id }))

  // AllTheCompressed is valid for the bulk-matter megaproject, but the 81 ATM
  // aliases are deliberately not currency storage.  Remove both exact recipe
  // IDs for every alias rather than asking KubeJS to inspect recipe outputs.
  ATM_COMPRESSED_FAMILIES.forEach(family => {
    for (let level = 1; level <= 9; level++) {
      event.remove({ id: `allthecompressed:compress/${family}_${level}x` })
      event.remove({ id: `allthecompressed:decompress/${family}_${level}x` })
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

  const sequencedElement = (id, outerType, input, output, loops, sequence) => {
    event.custom({
      type: outerType,
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
    'industrial_colonies:weathered_iron_sequenced_assembly',
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
    // Vibranium must bootstrap the Chromatic Compound used to build the
    // Refined-Radiance platform, so this route cannot require that platform.
    'industrial_colonies:weathered_iron_sequenced_assembly',
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
    'industrial_colonies:refined_radiance_sequenced_assembly',
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
