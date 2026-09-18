// Hide alternate Create Big Cannons cast-iron solids. Cannon parts and molten
// cast iron remain visible because they are unique gameplay components.

RecipeViewerEvents.removeEntries('item', event => {
  ;[
    'createbigcannons:cast_iron_ingot',
    'createbigcannons:cast_iron_nugget',
    'createbigcannons:cast_iron_block'
  ].forEach(item => event.remove(item))
})
