// Hide duplicate Mekanism lead ores and solids after canonicalization.

RecipeViewerEvents.removeEntries('item', event => {
  ;[
    'mekanism:lead_ore',
    'mekanism:deepslate_lead_ore',
    'mekanism:raw_lead',
    'mekanism:block_raw_lead',
    'mekanism:ingot_lead',
    'mekanism:nugget_lead',
    'mekanism:block_lead'
  ].forEach(item => event.remove(item))
})
