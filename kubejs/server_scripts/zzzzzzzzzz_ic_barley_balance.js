// priority: -20001
// User's final balance: six Regions Unexplored barley -> one Create wheat flour.
ServerEvents.recipes(event => {
  event.remove({ id: 'regions_unexplored:barley_smelting' })
  event.remove({ id: 'regions_unexplored:barley_smoking' })
  event.shapeless('create:wheat_flour', Array(6).fill('regions_unexplored:barley'))
    .id('industrial_colonies:food/barley_to_wheat_flour')
})
