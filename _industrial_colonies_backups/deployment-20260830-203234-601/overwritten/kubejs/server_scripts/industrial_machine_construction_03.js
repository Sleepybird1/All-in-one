// Industrial Colonies - Phase 3 machine construction, slice 03
// Electrochemical Engineering deliberately grows out of TFMG chemical and
// electrical infrastructure plus the Modular Machinery chassis.

ServerEvents.recipes(event => {
  const removedMachineRecipes = [
    'mekanism:electrolytic_separator',
    'mekanism:chemical_oxidizer',
    'mekanism:chemical_infuser',
    'mekanism:rotary_condensentrator'
  ]

  removedMachineRecipes.forEach(id => event.remove({ id: id }))

  const itemIngredient = value => value.charAt(0) === '#'
    ? { tag: value.substring(1) }
    : { item: value }

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [{ item: transitional }, itemIngredient(ingredient)],
    results: [{ id: transitional }]
  })

  const pressing = transitional => ({
    type: 'create:pressing',
    ingredients: [{ item: transitional }],
    results: [{ id: transitional }]
  })

  const sequencedMachine = (id, output, sequence) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: 'mekanism:steel_casing' },
      loops: 1,
      results: [{ id: output }],
      sequence: sequence,
      transitional_item: { id: 'mekanism:steel_casing' }
    }).id(id)
  }

  // A major electrical/chemical machine: built as a 4x4 assembled system
  // rather than a handcraft around a single default Electrolytic Core.
  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      B: { item: 'mekanism:basic_control_circuit' },
      C: { item: 'tfmg:copper_electrode' },
      E: { item: 'create:precision_mechanism' },
      I: { item: 'tfmg:circuit_board' },
      O: { tag: 'c:ingots/osmium' },
      P: { item: 'create:mechanical_pump' },
      T: { item: 'tfmg:transformer' },
      V: { item: 'tfmg:steel_chemical_vat' },
      Z: { item: 'tfmg:zinc_electrode' }
    },
    pattern: [
      'OZCO',
      'BTIB',
      'OVVO',
      'OPEO'
    ],
    result: { count: 1, id: 'mekanism:electrolytic_separator' },
    show_notification: false
  }).id('industrial_colonies:machine/electrochemical/electrolytic_separator')

  sequencedMachine(
    'industrial_colonies:machine/electrochemical/chemical_oxidizer',
    'mekanism:chemical_oxidizer',
    [
      deploying('mekanism:steel_casing', 'tfmg:steel_chemical_vat'),
      deploying('mekanism:steel_casing', 'mekanism:basic_control_circuit'),
      deploying('mekanism:steel_casing', 'tfmg:circuit_board'),
      deploying('mekanism:steel_casing', 'create:encased_fan'),
      pressing('mekanism:steel_casing')
    ]
  )

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      B: { item: 'mekanism:basic_control_circuit' },
      C: { item: 'mekanism:steel_casing' },
      I: { item: 'tfmg:circuit_board' },
      O: { tag: 'c:ingots/osmium' },
      P: { item: 'create:mechanical_pump' },
      T: { item: 'tfmg:transformer' },
      V: { item: 'tfmg:steel_chemical_vat' }
    },
    pattern: [
      'OVVO',
      'BCTB',
      'OPPO',
      'OIOO'
    ],
    result: { count: 1, id: 'mekanism:chemical_infuser' },
    show_notification: false
  }).id('industrial_colonies:machine/electrochemical/chemical_infuser')

  sequencedMachine(
    'industrial_colonies:machine/electrochemical/rotary_condensentrator',
    'mekanism:rotary_condensentrator',
    [
      deploying('mekanism:steel_casing', 'tfmg:steel_chemical_vat'),
      deploying('mekanism:steel_casing', 'mekanism:basic_control_circuit'),
      deploying('mekanism:steel_casing', 'create:mechanical_pump'),
      deploying('mekanism:steel_casing', 'tfmg:capacitor_item'),
      pressing('mekanism:steel_casing')
    ]
  )

  console.info(`[Industrial Colonies] Machine construction slice 03 loaded; replaced ${removedMachineRecipes.length} Electrochemical Engineering recipes.`)
})
