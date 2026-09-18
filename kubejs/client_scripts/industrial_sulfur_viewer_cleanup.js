// Hide inaccessible duplicate sulfur forms while preserving Mekanism's unique
// sulfur dioxide/trioxide chemistry and internal sulfuric-acid chemical.

RecipeViewerEvents.removeEntries('item', event => {
  ;[
    'mekanism:dust_sulfur',
    'mekanism:sulfuric_acid_bucket'
  ].forEach(item => event.remove(item))
})

RecipeViewerEvents.removeEntries('fluid', event => {
  event.remove('mekanism:sulfuric_acid')
})
