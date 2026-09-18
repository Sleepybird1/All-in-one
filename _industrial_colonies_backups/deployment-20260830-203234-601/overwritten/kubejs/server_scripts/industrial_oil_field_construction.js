// Industrial Colonies - pre-steel oil-field construction
// The Draw.io graph makes Oil Processing and Blast Furnace parallel children
// of The Steel Age. TFMG's native pumpjack recipes require Blast-Furnace steel,
// so the first extraction rig is rebuilt from TFMG cast iron and Create brass.

ServerEvents.tags('block', event => {
  // PumpjackBaseBlockEntity follows TFMG's industrial_pipe block tag down to
  // an oil deposit. Cast-iron fluid pipe is the Oil Processing-era member.
  event.add('tfmg:industrial_pipe', 'tfmg:cast_iron_pipe')
})

ServerEvents.recipes(event => {
  const removedOilFieldRecipes = [
    'tfmg:crafting/materials/surface_scanner',
    'tfmg:crafting/materials/pumpjack_base',
    'tfmg:crafting/materials/pumpjack_crank',
    'tfmg:crafting/materials/pumpjack_hammer',
    'tfmg:pumpjack_hammer_part_from_storage_blocks_steel_stonecutting',
    'tfmg:large_pumpjack_hammer_part_from_storage_blocks_steel_stonecutting',
    'tfmg:crafting/materials/pumpjack_hammer_connector',
    'tfmg:crafting/materials/large_pumpjack_hammer_connector',
    'tfmg:crafting/materials/pumpjack_hammer_head',
    'tfmg:crafting/materials/large_pumpjack_hammer_head',
    'tfmg:crafting/materials/oil_hammer',
    'tfmg:crafting/materials/oil_can'
  ]

  removedOilFieldRecipes.forEach(id => event.remove({ id: id }))

  const shaped = (recipeId, output, count, pattern, key) => event.custom({
    type: 'minecraft:crafting_shaped',
    category: 'misc',
    key: key,
    pattern: pattern,
    result: { count: count, id: output }
  }).id(recipeId)

  shaped(
    'industrial_colonies:machine/oil_processing/surface_scanner',
    'tfmg:surface_scanner',
    1,
    [
      ' O ',
      'PBP',
      ' F '
    ],
    {
      B: { item: 'create:brass_casing' },
      F: { item: 'tfmg:cast_iron_frame' },
      O: { item: 'create:content_observer' },
      P: { item: 'create:precision_mechanism' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/pumpjack_base',
    'tfmg:pumpjack_base',
    1,
    [
      'STS',
      'MCM',
      'PAP'
    ],
    {
      A: { item: 'create:precision_mechanism' },
      C: { item: 'create:brass_casing' },
      M: { item: 'tfmg:cast_iron_mechanical_pump' },
      P: { item: 'tfmg:cast_iron_pipe' },
      S: { tag: 'c:strings' },
      T: { item: 'tfmg:cast_iron_fluid_tank' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/pumpjack_crank',
    'tfmg:pumpjack_crank',
    1,
    [
      'S S',
      'TPT',
      'HCH'
    ],
    {
      C: { item: 'create:brass_casing' },
      H: { item: 'create:shaft' },
      P: { item: 'create:precision_mechanism' },
      S: { tag: 'c:strings' },
      T: { item: 'tfmg:cast_iron_truss' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/pumpjack_hammer',
    'tfmg:pumpjack_hammer',
    1,
    [
      'IFI',
      'TCT',
      ' T '
    ],
    {
      C: { item: 'create:brass_casing' },
      F: { item: 'tfmg:cast_iron_frame' },
      I: { item: 'tfmg:cast_iron_ingot' },
      T: { item: 'tfmg:cast_iron_truss' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/pumpjack_hammer_part',
    'tfmg:pumpjack_hammer_part',
    2,
    ['B'],
    {
      B: { item: 'tfmg:cast_iron_block' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/large_pumpjack_hammer_part',
    'tfmg:large_pumpjack_hammer_part',
    2,
    ['BB'],
    {
      B: { item: 'tfmg:cast_iron_block' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/pumpjack_hammer_connector',
    'tfmg:pumpjack_hammer_connector',
    1,
    ['BHB'],
    {
      B: { item: 'create:brass_ingot' },
      H: { item: 'tfmg:pumpjack_hammer_part' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector',
    'tfmg:large_pumpjack_hammer_connector',
    1,
    ['BHB'],
    {
      B: { item: 'create:brass_ingot' },
      H: { item: 'tfmg:large_pumpjack_hammer_part' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/pumpjack_hammer_head',
    'tfmg:pumpjack_hammer_head',
    1,
    [
      'B',
      'P'
    ],
    {
      B: { item: 'tfmg:cast_iron_block' },
      P: { item: 'tfmg:cast_iron_sheet' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head',
    'tfmg:large_pumpjack_hammer_head',
    1,
    [
      'PP',
      'BB'
    ],
    {
      B: { item: 'tfmg:cast_iron_block' },
      P: { item: 'tfmg:cast_iron_sheet' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/oil_hammer',
    'tfmg:oil_hammer',
    1,
    [
      'IIB',
      ' R ',
      ' R '
    ],
    {
      B: { item: 'create:brass_ingot' },
      I: { item: 'tfmg:cast_iron_ingot' },
      R: { tag: 'c:rods/wooden' }
    }
  )

  shaped(
    'industrial_colonies:machine/oil_processing/oil_can',
    'tfmg:oil_can',
    1,
    [
      ' NN',
      'BBB',
      ' BB'
    ],
    {
      B: { item: 'create:brass_ingot' },
      N: { item: 'tfmg:cast_iron_nugget' }
    }
  )

  console.info(`[Industrial Colonies] Pre-steel oil-field construction loaded; replaced ${removedOilFieldRecipes.length} TFMG recipes.`)
})
