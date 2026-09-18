// Industrial Colonies - Phase 5 electrical grid construction, slice 01
// TFMG is the canonical machine and local-cable stack. Create Crafts &
// Additions contributes only specialized utilities without a TFMG equivalent.
// Electro Energetics begins at Grid Engineering as the 128-block utility grid.

ServerEvents.recipes(event => {
  const removedGridRecipes = [
    'electroenergetics:crafting/empty_spool',
    'electroenergetics:crafting/connector',
    'electroenergetics:crafting/copper_wire_spool',
    'electroenergetics:crafting/accumulator',
    'electroenergetics:crafting/alternator_rotor',
    'electroenergetics:crafting/alternator_brushes',
    'electroenergetics:crafting/resistor'
  ]

  removedGridRecipes.forEach(id => event.remove({ id: id }))

  const shaped = (recipeId, output, count, pattern, key) => event.custom({
    type: 'minecraft:crafting_shaped',
    category: 'misc',
    key: key,
    pattern: pattern,
    result: { count: count, id: output }
  }).id(recipeId)

  shaped(
    'industrial_colonies:grid/empty_spool',
    'electroenergetics:empty_spool',
    4,
    [
      'NSN',
      ' R ',
      'NSN'
    ],
    {
      N: { item: 'tfmg:cast_iron_nugget' },
      R: { tag: 'c:rods/wooden' },
      S: { tag: 'minecraft:wooden_slabs' }
    }
  )

  shaped(
    'industrial_colonies:grid/connector',
    'electroenergetics:connector',
    2,
    [
      ' L ',
      'CBC',
      ' T '
    ],
    {
      B: { item: 'create:brass_casing' },
      C: { item: 'tfmg:cable_connector' },
      L: { item: 'tfmg:copper_cable_hub' },
      T: { item: 'tfmg:cast_iron_sheet' }
    }
  )

  shaped(
    'industrial_colonies:grid/copper_wire_spool',
    'electroenergetics:copper_wire_spool',
    1,
    [
      'WWW',
      'WSW',
      'WWW'
    ],
    {
      S: { item: 'electroenergetics:empty_spool' },
      W: { tag: 'c:wires/copper' }
    }
  )

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'tfmg:accumulator' },
      B: { item: 'create:brass_casing' },
      C: { item: 'electroenergetics:connector' },
      S: { item: 'tfmg:steel_casing' },
      W: { item: 'electroenergetics:copper_wire_spool' }
    },
    pattern: [
      ' CWC ',
      'CSASC',
      'WABAW',
      'CSASC',
      ' CWC '
    ],
    result: { count: 1, id: 'electroenergetics:accumulator' },
    show_notification: false
  }).id('industrial_colonies:grid/accumulator')

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'tfmg:generator' },
      I: { item: 'tfmg:cast_iron_ingot' },
      M: { item: 'tfmg:steel_mechanism' },
      S: { item: 'create:shaft' },
      W: { item: 'electroenergetics:copper_wire_spool' }
    },
    pattern: [
      '  W  ',
      ' IWI ',
      'MASAM',
      ' IWI ',
      '  W  '
    ],
    result: { count: 1, id: 'electroenergetics:alternator_rotor' },
    show_notification: false
  }).id('industrial_colonies:grid/alternator_rotor')

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [{ item: transitional }, { item: ingredient }],
    results: [{ id: transitional }]
  })

  event.custom({
    type: 'create:sequenced_assembly',
    ingredient: { item: 'tfmg:copper_cable_hub' },
    loops: 2,
    results: [{ id: 'electroenergetics:alternator_brushes' }],
    sequence: [
      deploying('tfmg:copper_cable_hub', 'electroenergetics:connector'),
      deploying('tfmg:copper_cable_hub', 'create:shaft'),
      deploying('tfmg:copper_cable_hub', 'tfmg:cast_iron_sheet'),
      deploying('tfmg:copper_cable_hub', 'create:brass_casing'),
      {
        type: 'create:pressing',
        ingredients: [{ item: 'tfmg:copper_cable_hub' }],
        results: [{ id: 'tfmg:copper_cable_hub' }]
      }
    ],
    transitional_item: { id: 'tfmg:copper_cable_hub' }
  }).id('industrial_colonies:grid/alternator_brushes')

  shaped(
    'industrial_colonies:grid/resistor',
    'electroenergetics:resistor',
    1,
    [
      ' T ',
      'CCC',
      ' T '
    ],
    {
      C: { item: 'electroenergetics:connector' },
      T: { item: 'tfmg:cast_iron_sheet' }
    }
  )

  console.info(`[Industrial Colonies] Grid Engineering construction loaded; replaced ${removedGridRecipes.length} Electro Energetics recipes.`)
})
