// Industrial Colonies - canonical petroleum chain
// TFMG owns crude oil, diesel, and gasoline. Other mods may consume these
// fluids through common tags, but may not publish competing versions.

ServerEvents.tags('fluid', event => {
  const canonicalTags = {
    'c:crude_oil': ['tfmg:crude_oil', 'tfmg:flowing_crude_oil'],
    'c:diesel': ['tfmg:diesel', 'tfmg:flowing_diesel'],
    'c:gasoline': ['tfmg:gasoline', 'tfmg:flowing_gasoline'],
    'createdieselgenerators:pumpjack_output': ['tfmg:crude_oil']
  }

  Object.entries(canonicalTags).forEach(([tag, fluids]) => {
    event.removeAll(tag)
    event.add(tag, fluids)
  })

  // Biodiesel is held back until it has an explicit progression node and
  // balance role. Leaving it enabled would bypass the TFMG refinery spine.
  event.removeAll('c:biodiesel')

  // Preserve TFMG's genuinely different fuels while removing inaccessible
  // CDG petroleum fluids from the broad compatibility tag.
  ;[
    'createdieselgenerators:biodiesel',
    'createdieselgenerators:flowing_biodiesel',
    'createdieselgenerators:diesel',
    'createdieselgenerators:flowing_diesel'
  ].forEach(fluid => event.remove('c:fuel', fluid))
})

ServerEvents.recipes(event => {
  const removedBypassRecipes = [
    'createdieselgenerators:distillation/crude_oil',
    'createdieselgenerators:distillation/superheated_crude_oil',
    'createdieselgenerators:mixing/biodiesel',
    'createdieselgenerators:crafting/asphalt_block',
    'createaddition:liquid_burning/crude_oil'
  ]

  removedBypassRecipes.forEach(id => event.remove({ id: id }))
  console.info(`[Industrial Colonies] Canonical TFMG petroleum loaded; removed ${removedBypassRecipes.length} bypass recipes.`)
})
