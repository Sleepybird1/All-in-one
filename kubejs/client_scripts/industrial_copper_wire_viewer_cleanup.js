// Original recipe review: show registered alternatives.
function IC_originalRecipeReview_skip() {}
// Hide alternate loose copper wires after canonicalization. Unique spools,
// cables, connectors, motors, and electrical machines remain visible.

IC_originalRecipeReview_skip('item', event => {
  ;[
    'createaddition:copper_wire',
    'electroenergetics:copper_wire'
  ].forEach(item => event.remove(item))
})
