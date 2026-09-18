// Industrial Colonies - Phase 4 nuclear construction, slice 04
// Reactor Instrumentation descends from Core Engineering, not Containment.
// Controllers and ports therefore use the core control rod and established
// electronics/grid hardware instead of a sibling-branch reactor casing.

ServerEvents.recipes(event => {
  const removedInstrumentationRecipes = [
    'bigreactors:reactor/basic/controller_ingots_uranium',
    'bigreactors:reactor/basic/controller_ingots_yellorium',
    'bigreactors:reactor/basic/redstoneport',
    'bigreactors:reactor/basic/passivetap_fe'
  ]

  removedInstrumentationRecipes.forEach(id => event.remove({ id: id }))

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [{ item: transitional }, { item: ingredient }],
    results: [{ id: transitional }]
  })

  const pressing = transitional => ({
    type: 'create:pressing',
    ingredients: [{ item: transitional }],
    results: [{ id: transitional }]
  })

  const sequencedInstrument = (id, input, output, sequence) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: input },
      loops: 1,
      results: [{ id: output }],
      sequence: sequence,
      transitional_item: { id: input }
    }).id(id)
  }

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      C: { item: 'bigreactors:basic_reactorcontrolrod' },
      E: { item: 'ae2:engineering_processor' },
      G: { item: 'tfmg:generator' },
      I: { item: 'tfmg:circuit_board' },
      M: { item: 'tfmg:steel_mechanism' },
      R: { item: 'create:refined_radiance_casing' },
      T: { item: 'electroenergetics:transformer' },
      U: { item: 'mekanism:ultimate_control_circuit' },
      Y: { item: 'industrial_colonies:yellorium_compound' }
    },
    pattern: [
      ' RYR ',
      'RTETR',
      'YUCUY',
      'RIGIR',
      ' RMR '
    ],
    result: { count: 1, id: 'bigreactors:basic_reactorcontroller' },
    show_notification: false
  }).id('industrial_colonies:machine/instrumentation/basic_reactor_controller')

  sequencedInstrument(
    'industrial_colonies:machine/instrumentation/basic_reactor_redstone_port',
    'create:content_observer',
    'bigreactors:basic_reactorredstoneport',
    [
      deploying('create:content_observer', 'create:refined_radiance_casing'),
      deploying('create:content_observer', 'mekanism:ultimate_control_circuit'),
      deploying('create:content_observer', 'ae2:logic_processor'),
      deploying('create:content_observer', 'tfmg:circuit_board'),
      pressing('create:content_observer')
    ]
  )

  sequencedInstrument(
    'industrial_colonies:machine/instrumentation/basic_reactor_power_tap',
    'electroenergetics:connector',
    'bigreactors:basic_reactorpowertapfe_passive',
    [
      deploying('electroenergetics:connector', 'create:refined_radiance_casing'),
      deploying('electroenergetics:connector', 'mekanism:ultimate_universal_cable'),
      deploying('electroenergetics:connector', 'tfmg:generator'),
      deploying('electroenergetics:connector', 'electroenergetics:transformer'),
      deploying('electroenergetics:connector', 'mekanism:alloy_atomic'),
      pressing('electroenergetics:connector')
    ]
  )

  console.info(`[Industrial Colonies] Reactor Instrumentation loaded; replaced ${removedInstrumentationRecipes.length} fuel- or containment-dependent recipes.`)
})
