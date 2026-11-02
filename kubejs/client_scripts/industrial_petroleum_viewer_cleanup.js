// Original recipe review: show registered alternatives.
function IC_originalRecipeReview_skip() {}
// Hide registered legacy petroleum entries after their survival production
// paths have been disabled. The registry objects remain for world-save safety.

IC_originalRecipeReview_skip('fluid', event => {
  ;[
    'createdieselgenerators:crude_oil',
    'createdieselgenerators:diesel',
    'createdieselgenerators:gasoline',
    'createdieselgenerators:biodiesel'
  ].forEach(fluid => event.remove(fluid))
})

IC_originalRecipeReview_skip('item', event => {
  ;[
    'createdieselgenerators:crude_oil_bucket',
    'createdieselgenerators:diesel_bucket',
    'createdieselgenerators:gasoline_bucket',
    'createdieselgenerators:biodiesel_bucket',
    'createdieselgenerators:oil_scanner',
    'createdieselgenerators:pumpjack_bearing',
    'createdieselgenerators:pumpjack_crank',
    'createdieselgenerators:pumpjack_head',
    'createdieselgenerators:pumpjack_hole'
  ].forEach(item => event.remove(item))
})
