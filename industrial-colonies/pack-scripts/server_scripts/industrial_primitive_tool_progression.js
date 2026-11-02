// Industrial Colonies - Primitive Age tool entry
//
// Vanilla's disposable material ladders are replaced by one deliberately poor
// flint pickaxe followed by Modern Foundry's modular tool-building system.
// Tools generated as structure loot are intentionally left available: finding
// a worn tool is an alternate start, not a crafting loophole.

const industrialPrimitiveLeaves = [
  'minecraft:oak_leaves',
  'minecraft:spruce_leaves',
  'minecraft:birch_leaves',
  'minecraft:jungle_leaves',
  'minecraft:acacia_leaves',
  'minecraft:dark_oak_leaves',
  'minecraft:mangrove_leaves',
  'minecraft:cherry_leaves',
  'minecraft:azalea_leaves',
  'minecraft:flowering_azalea_leaves'
]

// Guaranteed player-break fallback before planks are available.
// The standard two-plank stick recipe remains available.
industrialPrimitiveLeaves.forEach(id => {
  BlockEvents.broken(id, event => event.player.give('minecraft:stick'))
})

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

  // Preserve the existing bamboo/log shortcut restrictions; native plank sticks are allowed.
  ;[
    'minecraft:stick_from_bamboo_item',
    'quark:tweaks/crafting/utility/misc/easy_sticks',
    'quark:tweaks/crafting/utility/misc/easy_sticks_bamboo'
  ].forEach(id => event.remove({ id: id }))

  // Quark restores the five stone outputs under alternate recipe IDs. The
  // Apotheosis chain can then upgrade those vanilla tools all the way to
  // diamond, so both paths must be closed even though their base Minecraft
  // recipe IDs were already removed.
  vanillaToolKinds.forEach(kind => {
    event.remove({ id: `quark:tweaks/crafting/utility/better_stone_tools/${kind}` })
    ;[
      `apotheosis:smithing/upgrade_stone_${kind}_to_iron_${kind}`,
      `apotheosis:smithing/upgrade_iron_${kind}_to_golden_${kind}`,
      `apotheosis:smithing/upgrade_golden_${kind}_to_diamond_${kind}`
    ].forEach(id => event.remove({ id: id }))
  })

  // Starting stations must be available before the first cast copper ingot.
  // User-approved bootstrap correction: remove copper without adding a replacement.
  // Keep historical recipe IDs stable for existing integrations and removals.
  ;[
    'modernfoundry:tables/part_builder',
    'modernfoundry:tables/tinker_station'
  ].forEach(id => event.remove({ id: id }))

  // Keep Hilt's retextured recipe serializer so both stations retain their
  // selected plank appearance and block-item components.
  event.custom({
    type: 'hilt:crafting_shaped_retextured',
    category: 'misc',
    key: {
      p: { item: 'modernfoundry:pattern' },
      w: { tag: 'modernfoundry:planklike' }
    },
    match_all: true,
    pattern: ['pp', 'w '],
    result: { id: 'modernfoundry:part_builder' },
    show_notification: true,
    texture: 'w'
  }).id('industrial_colonies:primitive/copper_part_builder')

  event.custom({
    type: 'hilt:crafting_shaped_retextured',
    category: 'misc',
    key: {
      p: { item: 'modernfoundry:pattern' },
      w: { tag: 'modernfoundry:planklike' }
    },
    match_all: true,
    pattern: ['ppp', 'w w', 'w w'],
    result: { id: 'modernfoundry:tinker_station' },
    show_notification: true,
    texture: 'w'
  }).id('industrial_colonies:primitive/copper_tinker_station')

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
