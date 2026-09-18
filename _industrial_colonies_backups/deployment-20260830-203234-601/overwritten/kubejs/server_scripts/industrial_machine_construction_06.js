// Industrial Colonies - Phase 3 machine construction, slice 06
// The Pressurized Reaction Chamber is general electrochemical infrastructure,
// not a Plutonium-only machine and not a cheap crafting-table block.

ServerEvents.recipes(event => {
  const removedMachineRecipes = [
    'mekanism:pressurized_reaction_chamber'
  ]

  removedMachineRecipes.forEach(id => event.remove({ id: id }))

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [{ item: transitional }, { item: ingredient }],
    results: [{ id: transitional }]
  })

  event.custom({
    type: 'create:sequenced_assembly',
    ingredient: { item: 'mekanism:steel_casing' },
    loops: 2,
    results: [{ id: 'mekanism:pressurized_reaction_chamber' }],
    sequence: [
      deploying('mekanism:steel_casing', 'tfmg:steel_chemical_vat'),
      deploying('mekanism:steel_casing', 'create:mechanical_pump'),
      deploying('mekanism:steel_casing', 'mekanism:basic_control_circuit'),
      deploying('mekanism:steel_casing', 'tfmg:transformer'),
      deploying('mekanism:steel_casing', 'create:precision_mechanism'),
      {
        type: 'create:pressing',
        ingredients: [{ item: 'mekanism:steel_casing' }],
        results: [{ id: 'mekanism:steel_casing' }]
      }
    ],
    transitional_item: { id: 'mekanism:steel_casing' }
  }).id('industrial_colonies:machine/electrochemical/pressurized_reaction_chamber')

  console.info(`[Industrial Colonies] Machine construction slice 06 loaded; replaced ${removedMachineRecipes.length} electrochemical machine recipe.`)
})
