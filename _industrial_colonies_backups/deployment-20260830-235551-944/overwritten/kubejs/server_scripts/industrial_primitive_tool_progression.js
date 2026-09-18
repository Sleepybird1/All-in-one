// Industrial Colonies - Primitive Age tool entry
//
// Vanilla's disposable material ladders are replaced by one deliberately poor
// flint pickaxe followed by Modern Foundry's modular tool-building system.
// Tools generated as structure loot are intentionally left available: finding
// a worn tool is an alternate start, not a crafting loophole.

ServerEvents.recipes(event => {
  const vanillaToolMaterials = ['wooden', 'stone', 'iron', 'golden', 'diamond']
  const vanillaToolKinds = ['pickaxe', 'axe', 'shovel', 'hoe', 'sword']
  const removedVanillaTools = []

  vanillaToolMaterials.forEach(material => {
    vanillaToolKinds.forEach(kind => {
      const id = `minecraft:${material}_${kind}`
      event.remove({ id: id })
      removedVanillaTools.push(id)
    })
  })

  vanillaToolKinds.forEach(kind => {
    const id = `minecraft:netherite_${kind}_smithing`
    event.remove({ id: id })
    removedVanillaTools.push(id)
  })

  // Quark's log recipes skip the intended leaf/gravel scavenging opening.
  ;[
    'quark:tweaks/crafting/utility/misc/easy_sticks',
    'quark:tweaks/crafting/utility/misc/easy_sticks_bamboo'
  ].forEach(id => event.remove({ id: id }))

  // The modular tool workshop starts only after the crude pick has obtained
  // copper. Without this, Modern Foundry can assemble a wooden-head pickaxe
  // immediately and create a third, unintended opening route.
  ;[
    'modernfoundry:tables/part_builder',
    'modernfoundry:tables/tinker_station'
  ].forEach(id => event.remove({ id: id }))

  event.shaped(
    'modernfoundry:part_builder',
    [
      'PP',
      'CC'
    ],
    {
      P: 'modernfoundry:pattern',
      C: 'minecraft:copper_ingot'
    }
  ).id('industrial_colonies:primitive/copper_part_builder')

  event.shaped(
    'modernfoundry:tinker_station',
    [
      'PPP',
      'C C',
      'C C'
    ],
    {
      P: 'modernfoundry:pattern',
      C: 'minecraft:copper_ingot'
    }
  ).id('industrial_colonies:primitive/copper_tinker_station')

  // Vanilla leaves already drop sticks and gravel already rolls flint. Modern
  // Foundry also keeps its 3-gravel fallback so unlucky players cannot softlock.
  event.shaped(
    'industrial_colonies:crude_flint_pickaxe',
    [
      'FFF',
      ' S ',
      ' S '
    ],
    {
      F: 'minecraft:flint',
      S: 'minecraft:stick'
    }
  ).id('industrial_colonies:primitive/crude_flint_pickaxe')

  console.info(`[Industrial Colonies] Primitive tool progression loaded; removed ${removedVanillaTools.length} ordinary tool recipes.`)
})
