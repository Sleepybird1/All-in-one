// Industrial Colonies - Phase 4 plutonium production, slice 01
// The Actinide node constructs the neutron activator; this node unlocks its
// plutonium reaction and the final pellet-production run in the PRC.

ServerEvents.recipes(event => {
  const removedPlutoniumRecipes = [
    'mekanism:processing/lategame/plutonium',
    'mekanism:processing/lategame/plutonium_pellet/from_reaction'
  ]

  removedPlutoniumRecipes.forEach(id => event.remove({ id: id }))

  // Move plutonium production from the already-unlocked Isotopic Centrifuge
  // into the Solar Neutron Activator constructed by Actinide Chemistry.
  event.custom({
    type: 'mekanism:activating',
    input: { amount: 10, chemical: 'mekanism:nuclear_waste' },
    output: { amount: 1, id: 'mekanism:plutonium' }
  }).id('industrial_colonies:chemistry/plutonium/from_nuclear_waste')

  event.custom({
    type: 'mekanism:reaction',
    chemical_input: { amount: 1000, chemical: 'mekanism:plutonium' },
    chemical_output: { amount: 1000, id: 'mekanism:spent_nuclear_waste' },
    duration: 100,
    fluid_input: { amount: 1000, tag: 'minecraft:water' },
    item_input: { count: 1, tag: 'c:dusts/fluorite' },
    item_output: { count: 1, id: 'mekanism:pellet_plutonium' }
  }).id('industrial_colonies:chemistry/plutonium/pellet_from_reaction')

  console.info(`[Industrial Colonies] Plutonium Production loaded; replaced ${removedPlutoniumRecipes.length} processing recipes.`)
})
