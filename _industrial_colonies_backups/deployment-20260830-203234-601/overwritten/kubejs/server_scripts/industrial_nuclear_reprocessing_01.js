// Industrial Colonies - Phase 4 nuclear reprocessing, slice 01
// The reprocessor is a complete post-criticality factory. Its shell reuses
// first-reactor hardware and its ports specialize that shell through Create
// assembly instead of seven unrelated crafting-table recipes.

ServerEvents.recipes(event => {
  const removedReprocessorRecipes = [
    'bigreactors:reprocessor/casing',
    'bigreactors:reprocessor/glass',
    'bigreactors:reprocessor/controller',
    'bigreactors:reprocessor/wasteinjector',
    'bigreactors:reprocessor/fluidinjector',
    'bigreactors:reprocessor/collector',
    'bigreactors:reprocessor/outputport',
    'bigreactors:reprocessor/powerport'
  ]

  removedReprocessorRecipes.forEach(id => event.remove({ id: id }))

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

  const sequencedReprocessor = (id, input, output, count, ingredients) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: input },
      loops: 1,
      results: [{ count: count, id: output }],
      sequence: ingredients
        .map(ingredient => deploying(input, ingredient))
        .concat([pressing(input)]),
      transitional_item: { id: input }
    }).id(id)
  }

  // Cyanite is proof that the first reactor has actually operated. One spent
  // reactor casing seeds a four-block batch for the new multiblock shell.
  sequencedReprocessor(
    'industrial_colonies:machine/fuel_reprocessing/reprocessor_casing',
    'bigreactors:basic_reactorcasing',
    'bigreactors:reprocessorcasing',
    4,
    [
      'create:refined_radiance_casing',
      'bigreactors:cyanite_ingot',
      '#c:plates/lead',
      'tfmg:steel_mechanism'
    ]
  )

  event.custom({
    type: 'create:item_application',
    ingredients: [
      { item: 'bigreactors:reprocessorcasing' },
      { tag: 'c:glass_blocks' }
    ],
    results: [{ id: 'bigreactors:reprocessorglass' }]
  }).id('industrial_colonies:machine/fuel_reprocessing/reprocessor_glass')

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'mekanism:alloy_atomic' },
      C: { item: 'bigreactors:cyanite_ingot' },
      E: { item: 'ae2:engineering_processor' },
      K: { item: 'mekanism:chemical_crystallizer' },
      M: { item: 'tfmg:steel_mechanism' },
      R: { item: 'bigreactors:reprocessorcasing' },
      U: { item: 'mekanism:ultimate_control_circuit' },
      X: { item: 'bigreactors:basic_reactorcontroller' },
      Y: { item: 'bigreactors:yellorium_ingot' }
    },
    pattern: [
      ' RCR ',
      'RAEAR',
      'CYXYC',
      'RUKUR',
      ' RMR '
    ],
    result: { count: 1, id: 'bigreactors:reprocessorcontroller' },
    show_notification: false
  }).id('industrial_colonies:machine/fuel_reprocessing/reprocessor_controller')

  sequencedReprocessor(
    'industrial_colonies:machine/fuel_reprocessing/reprocessor_waste_injector',
    'bigreactors:reprocessorcasing',
    'bigreactors:reprocessorwasteinjector',
    1,
    ['create:chute', 'mekanism:chemical_oxidizer', 'bigreactors:cyanite_ingot', 'mekanism:ultimate_control_circuit']
  )

  sequencedReprocessor(
    'industrial_colonies:machine/fuel_reprocessing/reprocessor_fluid_injector',
    'bigreactors:reprocessorcasing',
    'bigreactors:reprocessorfluidinjector',
    1,
    ['create:mechanical_pump', 'create:fluid_pipe', 'tfmg:steel_chemical_vat', 'mekanism:ultimate_control_circuit']
  )

  sequencedReprocessor(
    'industrial_colonies:machine/fuel_reprocessing/reprocessor_collector',
    'bigreactors:reprocessorcasing',
    'bigreactors:reprocessorcollector',
    1,
    ['create:chute', 'create:depot', 'create:content_observer', 'bigreactors:cyanite_ingot']
  )

  sequencedReprocessor(
    'industrial_colonies:machine/fuel_reprocessing/reprocessor_output_port',
    'bigreactors:reprocessorcasing',
    'bigreactors:reprocessoroutputport',
    1,
    ['create:chute', 'create:precision_mechanism', 'create:content_observer', 'mekanism:ultimate_control_circuit']
  )

  sequencedReprocessor(
    'industrial_colonies:machine/fuel_reprocessing/reprocessor_power_port',
    'bigreactors:reprocessorcasing',
    'bigreactors:reprocessorpowerport',
    1,
    ['electroenergetics:connector', 'mekanism:ultimate_universal_cable', 'tfmg:generator', 'tfmg:transformer']
  )

  console.info(`[Industrial Colonies] Fuel Reprocessing loaded; replaced ${removedReprocessorRecipes.length} construction recipes.`)
})
