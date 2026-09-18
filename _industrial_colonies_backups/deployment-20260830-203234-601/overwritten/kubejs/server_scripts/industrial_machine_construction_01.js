// Industrial Colonies - Phase 3 machine construction, slice 01
// Major machines are manufactured from earlier branches instead of cheap 3x3
// recipes. Runtime MineColonies/team-stage enforcement remains a separate hook.

ServerEvents.recipes(event => {
  const removedMachineRecipes = [
    'mekanism:metallurgic_infuser'
  ]

  removedMachineRecipes.forEach(id => event.remove({ id: id }))

  // Infusion Technology comes after TFMG steel, chemical processing, early
  // circuitry, and control electronics. The recipe deliberately does not use
  // a Mekanism control circuit because those are produced by this machine.
  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'tfmg:capacitor_item' },
      B: { item: 'tfmg:circuit_board' },
      C: { item: 'tfmg:steel_casing' },
      O: { tag: 'c:ingots/osmium' },
      P: { item: 'create:precision_mechanism' },
      R: { tag: 'c:dusts/redstone' },
      T: { item: 'tfmg:transformer' },
      V: { item: 'tfmg:steel_chemical_vat' }
    },
    pattern: [
      ' ORO ',
      'OBABO',
      'RTCTR',
      'OPVPO',
      ' ORO '
    ],
    result: { count: 1, id: 'mekanism:metallurgic_infuser' },
    show_notification: false
  }).id('industrial_colonies:machine/metallurgic_infuser')

  console.info(`[Industrial Colonies] Machine construction slice 01 loaded; replaced ${removedMachineRecipes.length} default recipe.`)
})
