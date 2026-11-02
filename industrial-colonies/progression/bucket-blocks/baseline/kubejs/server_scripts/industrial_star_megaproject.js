// Industrial Colonies - base-pack capstone artifact.
//
// The Black Hole proves bulk production. The Reserve Core proves sustained
// chemical/fuel throughput. The three alloy families prove that the
// manufactured Allthemodium currency chain has also reached completion.

ServerEvents.recipes(event => {
  event.custom({
    type: 'industrial_colonies:creative_mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'allthemodium:vibranium_allthemodium_alloy_ingot' },
      V: { item: 'allthemodium:unobtainium_vibranium_alloy_ingot' },
      U: { item: 'allthemodium:unobtainium_allthemodium_alloy_ingot' },
      B: { item: 'mekanism:ultimate_control_circuit' },
      H: { item: 'industrial_colonies:black_hole' },
      C: { item: 'industrial_colonies:industrial_reserve_core' }
    },
    pattern: [
      '  A  ',
      ' VAV ',
      'UBHBU',
      ' VCV ',
      '  A  '
    ],
    result: { count: 1, id: 'industrial_colonies:industrial_star' },
    show_notification: true
  }).id('industrial_colonies:megaproject/industrial_star')
})
