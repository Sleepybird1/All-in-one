// Hide inaccessible legacy steel solids. Their registry entries remain so
// existing worlds can migrate them through the one-way conversion recipes.

RecipeViewerEvents.removeEntries('item', event => {
  ;[
    'mekanism:ingot_steel',
    'mekanism:nugget_steel',
    'mekanism:block_steel',
    'createmetallurgy:steel_ingot',
    'createmetallurgy:steel_block',
    'modernfoundry:steel_ingot',
    'modernfoundry:steel_nugget',
    'modernfoundry:steel_block',
    'createbigcannons:steel_ingot',
    'createbigcannons:steel_scrap',
    'createbigcannons:steel_block'
  ].forEach(item => event.remove(item))
})
