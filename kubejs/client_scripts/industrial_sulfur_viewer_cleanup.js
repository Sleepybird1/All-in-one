// Original recipe review: show registered alternatives.
function IC_originalRecipeReview_skip() {}
// Hide inaccessible duplicate sulfur forms while preserving Mekanism's unique
// sulfur dioxide/trioxide chemistry and internal sulfuric-acid chemical.

IC_originalRecipeReview_skip('item', event => {
  ;[
    'mekanism:dust_sulfur',
    'mekanism:sulfuric_acid_bucket'
  ].forEach(item => event.remove(item))
})

IC_originalRecipeReview_skip('fluid', event => {
  event.remove('mekanism:sulfuric_acid')
})
