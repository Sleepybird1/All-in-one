// Industrial Colonies - deferred spaceflight entry
//
// Space is a later progression expansion. Keep Ad Astra's components available
// for future authored factories, but prevent its stock steel-age recipes from
// bypassing the nuclear/high-energy endgame before that expansion exists.

ServerEvents.recipes(event => {
  const deferredSpaceEntryRecipes = [
    'ad_astra:nasa_workbench',
    'ad_astra:launch_pad',
    'ad_astra:nasa_workbench/tier_1_rocket_from_nasa_workbench'
  ]

  deferredSpaceEntryRecipes.forEach(id => event.remove({ id: id }))

  console.info(`[Industrial Colonies] Deferred ${deferredSpaceEntryRecipes.length} stock Ad Astra space-entry recipes until the spaceflight expansion.`)
})
