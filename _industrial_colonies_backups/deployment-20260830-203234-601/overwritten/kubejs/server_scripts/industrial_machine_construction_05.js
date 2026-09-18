// Industrial Colonies - Phase 3 machine construction, slice 05
// The Isotopic Centrifuge is a major Nuclear Age accomplishment, not a small
// handcraft around three Ultimate circuits and lead ingots.

ServerEvents.recipes(event => {
  const removedMachineRecipes = [
    'mekanism:isotopic_centrifuge'
  ]

  removedMachineRecipes.forEach(id => event.remove({ id: id }))

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      C: { item: 'mekanism:steel_casing' },
      E: { item: 'ae2:engineering_processor' },
      F: { item: 'createcasing:refined_radiance_encased_fan' },
      L: { tag: 'c:ingots/lead' },
      M: { item: 'createcasing:refined_radiance_mixer' },
      P: { item: 'createcasing:refined_radiance_press' },
      R: { item: 'create:refined_radiance_casing' },
      T: { item: 'tfmg:transformer' },
      U: { item: 'mekanism:ultimate_control_circuit' },
      V: { item: 'tfmg:steel_chemical_vat' }
    },
    pattern: [
      ' RFR ',
      'RVUVR',
      'LECEL',
      'RVTMR',
      ' RPR '
    ],
    result: { count: 1, id: 'mekanism:isotopic_centrifuge' },
    show_notification: false
  }).id('industrial_colonies:machine/uranium_processing/isotopic_centrifuge')

  console.info(`[Industrial Colonies] Machine construction slice 05 loaded; replaced ${removedMachineRecipes.length} Uranium Processing recipe.`)
})
