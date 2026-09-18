// Hide registered legacy petroleum entries after their survival production
// paths have been disabled. The registry objects remain for world-save safety.

RecipeViewerEvents.removeEntries('fluid', event => {
  ;[
    'createdieselgenerators:crude_oil',
    'createdieselgenerators:diesel',
    'createdieselgenerators:gasoline',
    'createdieselgenerators:biodiesel'
  ].forEach(fluid => event.remove(fluid))
})

RecipeViewerEvents.removeEntries('item', event => {
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
