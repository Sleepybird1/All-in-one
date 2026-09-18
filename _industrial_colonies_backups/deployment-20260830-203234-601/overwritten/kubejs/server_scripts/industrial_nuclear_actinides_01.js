// Industrial Colonies - Phase 4 actinide chemistry, slice 01
// Mekanism Generators is intentionally absent, so the Extreme Reactors spent-
// fuel loop becomes the pack's source of nuclear waste. Polonium production is
// reserved for a later expansion rather than silently unlocking quantum gear.

ServerEvents.recipes(event => {
  const removedActinideRecipes = [
    'mekanism:radioactive_waste_barrel',
    'mekanism:solar_neutron_activator',
    'mekanism:processing/lategame/polonium',
    'mekanism:processing/lategame/polonium_pellet/from_reaction'
  ]

  removedActinideRecipes.forEach(id => event.remove({ id: id }))

  const itemIngredient = value => value.charAt(0) === '#'
    ? { tag: value.substring(1) }
    : { item: value }

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [{ item: transitional }, itemIngredient(ingredient)],
    results: [{ id: transitional }]
  })

  event.custom({
    type: 'create:sequenced_assembly',
    ingredient: { item: 'bigreactors:reprocessorcasing' },
    loops: 1,
    results: [{ count: 2, id: 'mekanism:radioactive_waste_barrel' }],
    sequence: [
      deploying('bigreactors:reprocessorcasing', '#c:plates/lead'),
      deploying('bigreactors:reprocessorcasing', 'bigreactors:cyanite_ingot'),
      deploying('bigreactors:reprocessorcasing', 'tfmg:steel_mechanism'),
      deploying('bigreactors:reprocessorcasing', 'mekanism:ultimate_control_circuit'),
      {
        type: 'create:pressing',
        ingredients: [{ item: 'bigreactors:reprocessorcasing' }],
        results: [{ id: 'bigreactors:reprocessorcasing' }]
      }
    ],
    transitional_item: { id: 'bigreactors:reprocessorcasing' }
  }).id('industrial_colonies:machine/actinide_chemistry/radioactive_waste_barrel')

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      C: { item: 'electroenergetics:connector' },
      D: { item: 'minecraft:daylight_detector' },
      E: { item: 'ae2:engineering_processor' },
      G: { item: 'bigreactors:reprocessorglass' },
      L: { tag: 'c:plates/lead' },
      M: { item: 'tfmg:steel_mechanism' },
      N: { item: 'bigreactors:cyanite_ingot' },
      R: { item: 'create:refined_radiance_casing' },
      U: { item: 'mekanism:ultimate_control_circuit' },
      W: { item: 'mekanism:radioactive_waste_barrel' }
    },
    pattern: [
      'GDNDG',
      'GRCRG',
      'NWUWN',
      'GECEG',
      'RMLMR'
    ],
    result: { count: 1, id: 'mekanism:solar_neutron_activator' },
    show_notification: false
  }).id('industrial_colonies:machine/actinide_chemistry/solar_neutron_activator')

  // TFMG sulfuric acid enters Mekanism as a chemical through the canonical
  // Rotary bridge, then the Dissolution Chamber strips reprocessed Blutonium
  // into the nuclear-waste feed needed by the rest of the actinide plant.
  event.custom({
    type: 'mekanism:dissolution',
    chemical_input: { amount: 1, chemical: 'mekanism:sulfuric_acid' },
    item_input: { count: 1, item: 'bigreactors:blutonium_ingot' },
    output: { amount: 1000, id: 'mekanism:nuclear_waste' },
    per_tick_usage: true
  }).id('industrial_colonies:chemistry/actinide/nuclear_waste_from_blutonium')

  console.info(`[Industrial Colonies] Actinide Chemistry loaded; replaced two machine recipes, added the waste bridge, and deferred polonium.`)
})
