// Hide alternate loose copper wires after canonicalization. Unique spools,
// cables, connectors, motors, and electrical machines remain visible.

RecipeViewerEvents.removeEntries('item', event => {
  ;[
    'createaddition:copper_wire',
    'electroenergetics:copper_wire'
  ].forEach(item => event.remove(item))
})
