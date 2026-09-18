// Industrial Colonies - Yellorium Refinement
// Extreme Reactors' own Yellorium Dust is conditional on Thermal, which this
// pack does not contain. This recipe creates an owned structural intermediate
// without exposing the downstream Yellorium Ingot fuel recipe.

ServerEvents.recipes(event => {
  event.custom({
    type: 'create:crushing',
    ingredients: [{ item: 'bigreactors:raw_yellorium' }],
    processing_time: 400,
    results: [{ count: 2, id: 'industrial_colonies:yellorium_compound' }]
  }).id('industrial_colonies:materials/yellorium_compound')

  console.info('[Industrial Colonies] Yellorium Refinement loaded; structural compound is separate from reactor fuel.')
})
