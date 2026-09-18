// Industrial Colonies - Phase 4 nuclear fuel, slice 01
// Yellorium is a structural alloy and uranium precursor. It never becomes
// reactor fuel directly. Usable first-tier reactor fuel must pass through
// Mekanism uranium chemistry and isotope separation.

ServerEvents.recipes(event => {
  const removedDirectFuelRecipes = [
    'bigreactors:smelting/yellorium_from_ore',
    'bigreactors:blasting/yellorium_from_ore',
    'bigreactors:smelting/yellorium_from_raw',
    'bigreactors:blasting/yellorium_from_raw',
    'bigreactors:crafting/raw_yellorium_component_to_storage',
    'bigreactors:crafting/raw_yellorium_storage_to_component',
    'bigreactors:fluidizer/solid/yellorium',
    'bigreactors:fluidizer/solid/yellorium9',
    'thermal:pulverizer_yellorite_ore_to_dust',
    'thermal:pulverizer_yellorium_ingot_to_dust'
  ]

  removedDirectFuelRecipes.forEach(id => event.remove({ id: id }))

  // The dedicated pellet is the only item tag mapped to Extreme Reactors'
  // first-tier fuel reactant. It proves a full 1,000-unit fissile-fuel batch;
  // no Yellorium ingot, block, molten alloy, or generic uranium item is fuel.
  event.custom({
    type: 'mekanism:crystallizing',
    input: {
      amount: 1000,
      chemical: 'mekanism:fissile_fuel'
    },
    output: {
      count: 1,
      id: 'industrial_colonies:enriched_uranium_fuel_pellet'
    }
  }).id('industrial_colonies:fuel/early_nuclear/enriched_uranium_fuel_pellet')

  console.info(`[Industrial Colonies] Enriched Uranium Fuel loaded; removed ${removedDirectFuelRecipes.length} direct Yellorium acquisition/fuel bypasses.`)
})
