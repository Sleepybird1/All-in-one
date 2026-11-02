// priority: -10000
// Explicit user exception to original-recipe review mode, 2026-09-26.
// Only loose copper-wire production is changed. No project export required.
ServerEvents.tags('item', event => {
  // Retain old wire membership so existing inventory remains useful.
  event.add('c:wires/copper', 'tfmg:copper_wire')
  event.add('c:wires/all_metal', 'tfmg:copper_wire')
})

ServerEvents.recipes(event => {
  const wires = [
    'tfmg:copper_wire',
    'createaddition:copper_wire',
    'electroenergetics:copper_wire',
    'immersiveengineering:wire_copper'
  ]
  // Explicit IDs cover custom serializers whose tag results are not exposed
  // as ordinary ItemStack outputs to KubeJS's output filter.
  const alternatives = [
    'tfmg:copper_wire_from_ingots_copper_stonecutting',
    'createaddition:rolling/copper_plate',
    'createdieselgenerators:compat/createaddition/copper_wire',
    'createdieselgenerators:compat/electroenergetics/copper_wire',
    'createdieselgenerators:compat/immersiveengineering/copper_wire',
    'electroenergetics:crafting/copper_wire',
    'immersiveengineering:crafting/wire_copper',
    'immersiveengineering:metalpress/wire_copper',
    'create:cutting/compat/immersiveengineering/wire_copper',
    'modernfoundry:smeltery/casting/metal/copper/wire_gold_cast',
    'modernfoundry:smeltery/casting/metal/copper/wire_sand_cast'
  ]
  alternatives.forEach(id => event.remove({ id: id }))
  wires.forEach(id => event.remove({ output: id }))

  // Literal consumers (including nested assembly steps) use the canonical
  // loose wire. Existing tag-based consumers and specialized cables stay intact.
  wires.slice(1).forEach(id => event.replaceInput({}, id, 'tfmg:copper_wire'))

  event.custom({
    type: 'createaddition:rolling',
    ingredients: [{ tag: 'c:plates/copper' }],
    results: [{ count: 2, id: 'tfmg:copper_wire' }]
  }).id('industrial_colonies:copper_wire/createaddition_rolling')

  // No wire conversion/recycling recipes: rolling is the sole production route.
  console.info('[Industrial Colonies] Rolling-only copper wire policy registered: 1 copper plate -> 2 TFMG copper wires; alternate loose-wire production removed.')
})
