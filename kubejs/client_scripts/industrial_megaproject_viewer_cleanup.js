// Original recipe review: show registered alternatives.
function IC_originalRecipeReview_skip() {}
// The unfinished Reserve Core is a Create Sequenced Assembly transition, not
// an independently obtainable quest item. Keep the completed artifacts visible.

IC_originalRecipeReview_skip('item', event => {
  event.remove('industrial_colonies:unfinished_industrial_reserve_core')
})
