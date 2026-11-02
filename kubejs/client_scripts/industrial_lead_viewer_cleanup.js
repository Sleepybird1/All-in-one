// Original recipe review: show registered alternatives.
function IC_originalRecipeReview_skip() {}
// Hide duplicate Mekanism lead ores and solids after canonicalization.

IC_originalRecipeReview_skip('item', event => {
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
