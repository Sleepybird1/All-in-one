// Industrial Colonies - MEGA radioactive chemical storage compatibility
//
// Mega Cells checks for Applied Mekanistics but not Mekanism Generators before
// requiring Generators' reactor glass. This pack intentionally has no
// Mekanism Generators. Reinforced Extreme Reactors glass is the closest installed
// reactor-rated equivalent and makes this cell a natural late-nuclear plus
// digital-storage intersection without introducing a new progression cycle.

ServerEvents.recipes(event => {
  const id = 'megacells:cells/standard/radioactive_chemical_cell'

  event.remove({ id: id })
  event.custom({
    type: 'minecraft:crafting_shaped',
    category: 'misc',
    key: {
      A: { item: 'bigreactors:reinforced_reactorglass' },
      D: { item: 'ae2:sky_dust' },
      C: { item: 'megacells:radioactive_cell_component' },
      H: { item: 'mekanism:hdpe_sheet' },
      P: { item: 'mekanism:pellet_polonium' }
    },
    pattern: [
      'ADA',
      'DCD',
      'HPH'
    ],
    result: { count: 1, id: 'megacells:radioactive_chemical_cell' }
  }).id(id)

  console.info('[Industrial Colonies] Repaired the MEGA Radioactive Chemical Storage Cell without Mekanism Generators.')
})
