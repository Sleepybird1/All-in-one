// Industrial Colonies - Phase 4 nuclear construction, slice 03
// Core Engineering is parallel to Containment Engineering and upstream of the
// first usable fuel. Its construction recipes must not consume either sibling
// containment blocks or downstream uranium/Yellorium fuel ingots.

ServerEvents.recipes(event => {
  const removedCoreRecipes = [
    'bigreactors:reactor/basic/fuelrod_ingots_uranium',
    'bigreactors:reactor/basic/fuelrod_ingots_yellorium',
    'bigreactors:reactor/basic/controlrod'
  ]

  removedCoreRecipes.forEach(id => event.remove({ id: id }))

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

  event.custom({
    type: 'create:sequenced_assembly',
    ingredient: { item: 'tfmg:steel_casing' },
    loops: 1,
    results: [{ count: 2, id: 'bigreactors:basic_reactorfuelrod' }],
    sequence: [
      deploying('tfmg:steel_casing', 'create:refined_radiance_casing'),
      deploying('tfmg:steel_casing', 'industrial_colonies:yellorium_compound'),
      deploying('tfmg:steel_casing', '#c:ingots/graphite'),
      deploying('tfmg:steel_casing', '#c:plates/lead'),
      deploying('tfmg:steel_casing', 'tfmg:steel_mechanism'),
      pressing('tfmg:steel_casing')
    ],
    transitional_item: { id: 'tfmg:steel_casing' }
  }).id('industrial_colonies:machine/core/basic_reactor_fuel_rod')

  // The top-mounted control assembly is a large project, but every component
  // is from Nuclear Age or one of its actual ancestors.
  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'mekanism:alloy_atomic' },
      C: { item: 'tfmg:steel_casing' },
      E: { item: 'ae2:engineering_processor' },
      M: { item: 'tfmg:steel_mechanism' },
      P: { item: 'create:precision_mechanism' },
      R: { item: 'create:refined_radiance_casing' },
      T: { item: 'electroenergetics:transformer' },
      U: { item: 'mekanism:ultimate_control_circuit' },
      Y: { item: 'industrial_colonies:yellorium_compound' }
    },
    pattern: [
      ' RYR ',
      'RTETR',
      'YUCAY',
      'RMPMR',
      ' RYR '
    ],
    result: { count: 1, id: 'bigreactors:basic_reactorcontrolrod' },
    show_notification: false
  }).id('industrial_colonies:machine/core/basic_reactor_control_rod')

  console.info(`[Industrial Colonies] Core Engineering loaded; replaced ${removedCoreRecipes.length} fuel-dependent or cross-branch recipes.`)
})
