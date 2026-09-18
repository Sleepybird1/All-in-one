// Industrial Colonies - Phase 4 nuclear fuel, slice 01
// Yellorium ore and raw material remain refinery feedstocks. Usable reactor
// fuel must pass through Mekanism uranium chemistry and isotope separation.

ServerEvents.recipes(event => {
  const removedDirectFuelRecipes = [
    'bigreactors:smelting/yellorium_from_ore',
    'bigreactors:blasting/yellorium_from_ore',
    'bigreactors:smelting/yellorium_from_raw',
    'bigreactors:blasting/yellorium_from_raw'
  ]

  removedDirectFuelRecipes.forEach(id => event.remove({ id: id }))

  // One uranium ingot enriches into two Yellow Cake, which oxidizes into
  // 500 mB uranium oxide. Hydrofluorination doubles that to 1,000 mB
  // uranium hexafluoride, and isotope separation retains the same volume as
  // fissile fuel. Crystallizing 1,000 mB therefore preserves a 1:1 fuel yield.
  event.custom({
    type: 'mekanism:crystallizing',
    input: {
      amount: 1000,
      chemical: 'mekanism:fissile_fuel'
    },
    output: {
      count: 1,
      id: 'bigreactors:yellorium_ingot'
    }
  }).id('industrial_colonies:fuel/early_nuclear/yellorium_from_fissile_fuel')

  console.info(`[Industrial Colonies] Early Nuclear Fuel loaded; removed ${removedDirectFuelRecipes.length} direct furnace bypasses.`)
})
