// Industrial Colonies - canonical sulfur and sulfuric acid
// TFMG owns the player-facing sulfur dust and sulfuric-acid fluid.
// Mekanism keeps unique sulfur gases and consumes TFMG acid through its
// Rotary Condensentrator chemical/fluid bridge.

ServerEvents.tags('item', event => {
  event.removeAll('c:dusts/sulfur')
  event.add('c:dusts/sulfur', 'tfmg:sulfur_dust')

  event.removeAll('c:buckets/sulfuric_acid')
  event.add('c:buckets/sulfuric_acid', 'tfmg:sulfuric_acid_bucket')
})

ServerEvents.tags('fluid', event => {
  event.removeAll('c:sulfuric_acid')
  event.add('c:sulfuric_acid', 'tfmg:sulfuric_acid')

  // Existing-world migration input. This is deliberately not a common tag.
  event.removeAll('industrial_colonies:legacy_mekanism_sulfuric_acid')
  event.add('industrial_colonies:legacy_mekanism_sulfuric_acid', 'mekanism:sulfuric_acid')
})

ServerEvents.recipes(event => {
  const removedSulfurDuplicates = [
    'mekanism:chemical_conversion/sulfur_to_sulfuric_acid',
    'mekanism:chemical_infusing/sulfuric_acid',
    'mekanism:rotary/sulfuric_acid',
    'mekanism:injecting/gunpowder_to_sulfur',
    'mekanism:reaction/coal_gasification/blocks_coals',
    'mekanism:reaction/coal_gasification/coals',
    'mekanism:reaction/coal_gasification/dusts_coals',
    'mekanism:sulfur_dye'
  ]

  removedSulfurDuplicates.forEach(id => event.remove({ id: id }))

  // Mekanism may still recover sulfur using its unique machines, but their
  // player-facing solid output is the canonical TFMG dust.
  event.custom({
    type: 'mekanism:injecting',
    chemical_input: { amount: 1, chemical: 'mekanism:hydrogen_chloride' },
    item_input: { count: 1, tag: 'c:gunpowders' },
    output: { count: 1, id: 'tfmg:sulfur_dust' },
    per_tick_usage: true
  }).id('industrial_colonies:sulfur/gunpowder_recovery')

  ;[
    {
      path: 'blocks_coals',
      chemical: 1000,
      duration: 900,
      fluid: 1000,
      input: {
        type: 'neoforge:compound',
        children: [{ tag: 'c:storage_blocks/coal' }, { tag: 'c:storage_blocks/charcoal' }],
        count: 1
      },
      sulfur: 9
    },
    {
      path: 'coals',
      chemical: 100,
      duration: 100,
      fluid: 100,
      input: { count: 1, tag: 'minecraft:coals' },
      sulfur: 1
    },
    {
      path: 'dusts_coals',
      chemical: 100,
      duration: 100,
      fluid: 100,
      input: {
        type: 'neoforge:compound',
        children: [{ tag: 'c:dusts/coal' }, { tag: 'c:dusts/charcoal' }],
        count: 1
      },
      sulfur: 1
    }
  ].forEach(recipe => {
    event.custom({
      type: 'mekanism:reaction',
      chemical_input: { amount: recipe.chemical, chemical: 'mekanism:oxygen' },
      chemical_output: { amount: recipe.chemical, id: 'mekanism:hydrogen' },
      duration: recipe.duration,
      fluid_input: { amount: recipe.fluid, tag: 'minecraft:water' },
      item_input: recipe.input,
      item_output: { count: recipe.sulfur, id: 'tfmg:sulfur_dust' }
    }).id(`industrial_colonies:sulfur/coal_gasification_${recipe.path}`)
  })

  event.custom({
    type: 'minecraft:crafting_shapeless',
    category: 'misc',
    ingredients: [{ tag: 'c:dusts/sulfur' }],
    result: { count: 1, id: 'minecraft:yellow_dye' }
  }).id('industrial_colonies:sulfur/yellow_dye')

  // Canonical bridge: TFMG acid fluid <-> Mekanism acid chemical. Mekanism's
  // own sulfuric-acid synthesis was removed, so the TFMG vat remains required.
  event.custom({
    type: 'mekanism:rotary',
    chemical_input: { amount: 1, chemical: 'mekanism:sulfuric_acid' },
    chemical_output: { amount: 1, id: 'mekanism:sulfuric_acid' },
    fluid_input: { amount: 1, tag: 'c:sulfuric_acid' },
    fluid_output: { amount: 1, id: 'tfmg:sulfuric_acid' }
  }).id('industrial_colonies:sulfur/tfmg_acid_rotary_bridge')

  // Existing Mekanism acid fluid can be recovered from old tanks/saves.
  event.custom({
    type: 'mekanism:rotary',
    chemical_input: { amount: 1, chemical: 'mekanism:sulfuric_acid' },
    chemical_output: { amount: 1, id: 'mekanism:sulfuric_acid' },
    fluid_input: { amount: 1, tag: 'industrial_colonies:legacy_mekanism_sulfuric_acid' },
    fluid_output: { amount: 1, id: 'tfmg:sulfuric_acid' }
  }).id('industrial_colonies:sulfur/migrate_mekanism_acid')

  event.custom({
    type: 'minecraft:crafting_shapeless',
    category: 'misc',
    ingredients: [{ item: 'mekanism:dust_sulfur' }],
    result: { count: 1, id: 'tfmg:sulfur_dust' }
  }).id('industrial_colonies:sulfur/migrate_mekanism_dust')

  console.info(`[Industrial Colonies] Canonical TFMG sulfur chemistry loaded; removed ${removedSulfurDuplicates.length} duplicate recipes.`)
})
