// The unfinished Reserve Core is a Create Sequenced Assembly transition, not
// an independently obtainable quest item. Keep the completed artifacts visible.

RecipeViewerEvents.removeEntries('item', event => {
  event.remove('industrial_colonies:unfinished_industrial_reserve_core')
})
