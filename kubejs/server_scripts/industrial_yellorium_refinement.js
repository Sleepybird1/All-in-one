// Industrial Colonies - manufactured Yellorium alloy and refinement
//
// Yellorium is an alloy in this pack, not a naturally smelted uranium alias.
// Advanced Alloy Mixing combines one ingot-equivalent each of molten lead and
// molten gold. The resulting molten Yellorium is deliberately removed from
// Extreme Reactors' reactor-fluid tag by the uranium boundary script; casting
// it creates a construction metal, not reactor fuel.

ServerEvents.recipes(event => {
  event.custom({
    type: 'createmetallurgy:alloying',
    heat_requirement: 'heated',
    ingredients: [
      { type: 'neoforge:single', amount: 90, fluid: 'createmetallurgy:molten_lead' },
      { type: 'neoforge:single', amount: 90, fluid: 'createmetallurgy:molten_gold' }
    ],
    processing_time: 160,
    results: [{ amount: 180, id: 'bigreactors:yellorium' }]
  }).id('industrial_colonies:materials/yellorium/molten_alloy')

  // Casting belongs to the immediately following Advanced Metallurgy node.
  // One 180 mB alloy batch therefore yields exactly two ingots.
  event.custom({
    type: 'createmetallurgy:casting_in_table',
    ingredients: [
      { type: 'neoforge:single', amount: 90, fluid: 'bigreactors:yellorium' },
      { item: 'createmetallurgy:graphite_ingot_mold' }
    ],
    processing_time: 60,
    result: { item: { count: 1, id: 'bigreactors:yellorium_ingot' } }
  }).id('industrial_colonies:materials/yellorium/ingot_casting')

  // Yellorium Refinement turns the stable alloy into the owned structural and
  // isotope-feed compound. Raw Yellorium ore is intentionally not accepted.
  event.custom({
    type: 'create:crushing',
    ingredients: [{ item: 'bigreactors:yellorium_ingot' }],
    processing_time: 400,
    results: [{ count: 2, id: 'industrial_colonies:yellorium_compound' }]
  }).id('industrial_colonies:materials/yellorium_compound')

  console.info('[Industrial Colonies] Manufactured Yellorium alloy and refinement loaded; alloy forms are not reactor fuel.')
})
