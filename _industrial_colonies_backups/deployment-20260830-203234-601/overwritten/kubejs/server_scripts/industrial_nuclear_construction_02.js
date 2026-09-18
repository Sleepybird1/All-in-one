// Industrial Colonies - Phase 4 nuclear construction, slice 02
// Basic containment is a bulk manufactured system built on the Nuclear Age
// platform. Same-tier recycling recipes remain available so dismantling a
// reactor does not destroy its material value.

ServerEvents.recipes(event => {
  const removedContainmentRecipes = [
    'bigreactors:reactor/basic/casing',
    'bigreactors:reactor/basic/glass',
    'bigreactors:reactor/basic/solidaccessport'
  ]

  removedContainmentRecipes.forEach(id => event.remove({ id: id }))

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

  const sequencedContainment = (id, input, output, count, sequence) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: input },
      loops: 1,
      results: [{ count: count, id: output }],
      sequence: sequence,
      transitional_item: { id: input }
    }).id(id)
  }

  // One Nuclear Age casing becomes a four-block batch suitable for building a
  // real multiblock shell. Lead sheet supplies shielding without consuming the
  // still-locked Yellorium fuel ingot.
  sequencedContainment(
    'industrial_colonies:machine/containment/basic_reactor_casing',
    'create:refined_radiance_casing',
    'bigreactors:basic_reactorcasing',
    4,
    [
      deploying('create:refined_radiance_casing', 'tfmg:steel_mechanism'),
      deploying('create:refined_radiance_casing', '#c:plates/lead'),
      deploying('create:refined_radiance_casing', 'industrial_colonies:yellorium_compound'),
      deploying('create:refined_radiance_casing', 'tfmg:steel_casing'),
      pressing('create:refined_radiance_casing')
    ]
  )

  // Window production remains a simple repeatable application once the player
  // owns containment casing; it cannot create casing from nothing.
  event.custom({
    type: 'create:item_application',
    ingredients: [
      { item: 'bigreactors:basic_reactorcasing' },
      { tag: 'c:glass_blocks' }
    ],
    results: [{ id: 'bigreactors:basic_reactorglass' }]
  }).id('industrial_colonies:machine/containment/basic_reactor_glass')

  sequencedContainment(
    'industrial_colonies:machine/containment/basic_solid_access_port',
    'bigreactors:basic_reactorcasing',
    'bigreactors:basic_reactorsolidaccessport',
    1,
    [
      deploying('bigreactors:basic_reactorcasing', 'create:chute'),
      deploying('bigreactors:basic_reactorcasing', 'create:content_observer'),
      deploying('bigreactors:basic_reactorcasing', 'mekanism:ultimate_control_circuit'),
      deploying('bigreactors:basic_reactorcasing', 'create:refined_radiance_casing'),
      pressing('bigreactors:basic_reactorcasing')
    ]
  )

  console.info(`[Industrial Colonies] Containment Engineering loaded; replaced ${removedContainmentRecipes.length} construction recipes while preserving same-tier recycling.`)
})
