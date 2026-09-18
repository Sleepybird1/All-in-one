// Industrial Colonies - canonical loose copper wire
// TFMG owns the shared loose-wire material. Mod-specific spools, cables,
// connectors, motors, and grid hardware remain separate progression systems.

ServerEvents.tags('item', event => {
  event.removeAll('c:wires/copper')
  event.add('c:wires/copper', 'tfmg:copper_wire')
})

ServerEvents.recipes(event => {
  const removedCopperWireDuplicates = [
    'createaddition:rolling/copper_plate',
    'createdieselgenerators:compat/createaddition/copper_wire',
    'createdieselgenerators:compat/electroenergetics/copper_wire',
    'createdieselgenerators:compat/immersiveengineering/copper_wire',
    'electroenergetics:crafting/copper_wire',
    'create:cutting/compat/immersiveengineering/wire_copper'
  ]

  removedCopperWireDuplicates.forEach(id => event.remove({ id: id }))

  // Preserve the industrial production routes, but make every route output
  // the canonical TFMG loose wire.
  event.custom({
    type: 'createaddition:rolling',
    ingredients: [{ tag: 'c:plates/copper' }],
    results: [{ count: 2, id: 'tfmg:copper_wire' }]
  }).id('industrial_colonies:copper_wire/createaddition_rolling')

  event.custom({
    type: 'createdieselgenerators:wire_cutting',
    ingredients: [{ tag: 'c:plates/copper' }],
    results: [{ count: 3, id: 'tfmg:copper_wire' }]
  }).id('industrial_colonies:copper_wire/wire_cutting')

  // Preserve Create's saw route independently of whether Immersive
  // Engineering is enabled, but return TFMG wire instead of an IE duplicate.
  event.custom({
    type: 'create:cutting',
    ingredients: [{ tag: 'c:plates/copper' }],
    processing_time: 50,
    results: [{ count: 2, id: 'tfmg:copper_wire' }]
  }).id('industrial_colonies:copper_wire/create_cutting')

  // Existing-world migration only. These alternate loose wires no longer
  // have normal production recipes or membership in the shared wire tag.
  ;[
    'createaddition:copper_wire',
    'electroenergetics:copper_wire'
  ].forEach(input => {
    const path = input.replace(':', '_').replace(/\//g, '_')
    event.custom({
      type: 'minecraft:crafting_shapeless',
      category: 'misc',
      ingredients: [{ item: input }],
      result: { count: 1, id: 'tfmg:copper_wire' }
    }).id(`industrial_colonies:copper_wire/migrate_${path}`)
  })

  console.info(`[Industrial Colonies] Canonical TFMG copper wire loaded; removed ${removedCopperWireDuplicates.length} duplicate recipes.`)
})
