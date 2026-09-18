// Industrial Colonies - physical factory-scale reserve proof.
//
// One completed core consumes, through 512 sequenced-assembly loops:
//   4,096 HDPE Pellets
//     512 Plutonium Pellets
// 1,024,000 mB TFMG Sulfuric Acid
// 5,120,000 mB TFMG Diesel
// The large loop count is intentional: the item is a sustained-throughput
// objective, not a one-off expensive crafting table recipe.

ServerEvents.recipes(event => {
  const transitional = 'industrial_colonies:unfinished_industrial_reserve_core'

  const deploying = ingredient => ({
    type: 'industrial_colonies:creative_deploying',
    ingredients: [
      { item: transitional },
      { item: ingredient }
    ],
    results: [{ id: transitional }]
  })

  const filling = fluid => ({
    // Create Encased has no Creative Spout; Brass is the strongest available
    // exact-machine filling environment for this otherwise Creative-tier line.
    type: 'industrial_colonies:brass_filling',
    ingredients: [
      { item: transitional },
      { type: 'neoforge:single', amount: 1000, fluid: fluid }
    ],
    results: [{ id: transitional }]
  })

  const sequence = []
  for (let index = 0; index < 8; index++) {
    sequence.push(deploying('mekanism:hdpe_pellet'))
  }
  sequence.push(deploying('mekanism:pellet_plutonium'))
  for (let index = 0; index < 2; index++) {
    sequence.push(filling('tfmg:sulfuric_acid'))
  }
  for (let index = 0; index < 10; index++) {
    sequence.push(filling('tfmg:diesel'))
  }
  sequence.push({
    type: 'industrial_colonies:creative_pressing',
    ingredients: [{ item: transitional }],
    results: [{ id: transitional }]
  })

  event.custom({
    type: 'industrial_colonies:creative_sequenced_assembly',
    ingredient: { item: 'mekanism:ultimate_control_circuit' },
    loops: 512,
    results: [{ id: 'industrial_colonies:industrial_reserve_core' }],
    sequence: sequence,
    transitional_item: { id: transitional }
  }).id('industrial_colonies:megaproject/industrial_reserve_core')
})
