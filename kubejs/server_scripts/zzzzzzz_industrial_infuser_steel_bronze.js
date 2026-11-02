// priority: -10000
// Explicit user exception to original-recipe review mode, 2026-09-26.
ServerEvents.recipes(event => {
  event.remove({
    id: 'mekanism:processing/steel/enriched_iron_to_dust',
    type: 'mekanism:metallurgic_infusing'
  })
  event.remove({
    id: 'mekanism:processing/bronze/ingot/from_infusing',
    type: 'mekanism:metallurgic_infusing'
  })
  // Other infusions, bronze dust, enriched iron and other machines stay intact.
  console.info('[Industrial Colonies] Scoped Infuser exclusions registered: steel dust and bronze ingot only.')
})
