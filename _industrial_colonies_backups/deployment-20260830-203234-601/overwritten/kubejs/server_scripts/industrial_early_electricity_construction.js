// Industrial Colonies - Phase 5 early electricity, TFMG-default slice
// Early Electricity is before The Steel Age and Electronics Manufacturing.
// TFMG generator/motor construction therefore uses brass, copper, iron, and
// Create mechanics without steel, winding, capacitors, or descendant machines.

ServerEvents.recipes(event => {
  const removedEarlyElectricalRecipes = [
    'tfmg:sequenced_assembly/generator',
    'tfmg:sequenced_assembly/motor',
    'tfmg:crafting/materials/accumulator',
    'tfmg:crafting/materials/accumulatorfrom_lithium',
    'tfmg:crafting/materials/cable_connector',
    'tfmg:crafting/materials/copper_cable_hub',
    'tfmg:crafting/materials/cable_tube',
    'createaddition:mechanical_crafting/alternator',
    'createaddition:mechanical_crafting/electric_motor',
    'createaddition:crafting/modular_accumulator',
    'createaddition:crafting/connector',
    'createaddition:crafting/large_connector',
    'createaddition:crafting/redstone_relay',
    'createaddition:crafting/small_light_connector'
  ]

  removedEarlyElectricalRecipes.forEach(id => event.remove({ id: id }))

  const retiredCreateAdditionMachines = [
    'createaddition:alternator',
    'createaddition:electric_motor',
    'createaddition:modular_accumulator',
    'createaddition:connector',
    'createaddition:large_connector'
  ]

  // These CreateAddition utilities have no TFMG equivalent, so retain their
  // function while replacing their retired wire endpoint with TFMG hardware.
  const portedCreateAdditionRecipes = [
    {
      source: 'createaddition:crafting/redstone_relay',
      replacement: 'industrial_colonies:early_power_cables/redstone_relay'
    },
    {
      source: 'createaddition:crafting/small_light_connector',
      replacement: 'industrial_colonies:early_power_cables/small_light_connector'
    }
  ]
  const shaped = (recipeId, output, count, pattern, key) => event.custom({
    type: 'minecraft:crafting_shaped',
    category: 'misc',
    key: key,
    pattern: pattern,
    result: { count: count, id: output }
  }).id(recipeId)

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      B: { item: 'create:brass_casing' },
      C: { tag: 'c:plates/copper' },
      P: { item: 'create:precision_mechanism' },
      S: { item: 'create:shaft' },
      W: { tag: 'c:wires/copper' }
    },
    pattern: [
      ' CWC ',
      'CPBPC',
      'WBSBW',
      'CPBPC',
      ' CWC '
    ],
    result: { count: 1, id: 'tfmg:generator' },
    show_notification: false
  }).id('industrial_colonies:early_electricity/generator')

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      B: { item: 'create:brass_casing' },
      C: { tag: 'c:wires/copper' },
      G: { item: 'tfmg:generator' },
      I: { tag: 'c:plates/iron' },
      P: { item: 'create:precision_mechanism' },
      S: { item: 'create:shaft' }
    },
    pattern: [
      ' ICI ',
      'IPBPI',
      'CBSBC',
      'IPGPI',
      ' ICI '
    ],
    result: { count: 1, id: 'tfmg:electric_motor' },
    show_notification: false
  }).id('industrial_colonies:early_electricity/electric_motor')

  shaped(
    'industrial_colonies:early_power_cables/cable_connector',
    'tfmg:cable_connector',
    1,
    [
      'III',
      ' C ',
      ' B '
    ],
    {
      B: { tag: 'c:plates/brass' },
      C: { tag: 'c:wires/copper' },
      I: { tag: 'c:nuggets/iron' }
    }
  )

  shaped(
    'industrial_colonies:early_power_cables/copper_cable_hub',
    'tfmg:copper_cable_hub',
    2,
    [
      'WWW',
      'MMM',
      'WWW'
    ],
    {
      M: { tag: 'c:ingots/copper' },
      W: { tag: 'c:wires/copper' }
    }
  )

  shaped(
    'industrial_colonies:early_power_cables/redstone_relay',
    'createaddition:redstone_relay',
    1,
    [
      ' R ',
      'CEC',
      'SSS'
    ],
    {
      C: { item: 'tfmg:cable_connector' },
      E: { item: 'create:precision_mechanism' },
      R: { tag: 'c:dusts/redstone' },
      S: { tag: 'c:stones' }
    }
  )

  event.custom({
    type: 'minecraft:crafting_shapeless',
    category: 'misc',
    ingredients: [
      { tag: 'c:wires/iron' },
      { tag: 'c:glass_blocks' },
      { item: 'tfmg:cable_connector' }
    ],
    result: { count: 1, id: 'createaddition:small_light_connector' }
  }).id('industrial_colonies:early_power_cables/small_light_connector')

  // The TFMG accumulator remains a chemical lead-acid battery. It is staged at
  // Chemical Processing, where sulfuric acid and canonical TFMG steel exist.
  event.custom({
    type: 'minecraft:crafting_shaped',
    category: 'misc',
    key: {
      B: { tag: 'c:storage_blocks/lead' },
      C: { item: 'tfmg:steel_casing' },
      L: { tag: 'c:plates/lead' },
      S: { item: 'tfmg:sulfuric_acid_bucket' },
      W: { tag: 'c:wires/copper' }
    },
    pattern: [
      'LWL',
      'SBS',
      'LCL'
    ],
    result: { count: 1, id: 'tfmg:accumulator' }
  }).id('industrial_colonies:chemical_processing/accumulator')

  shaped(
    'industrial_colonies:chemical_processing/cable_tube',
    'tfmg:cable_tube',
    8,
    [
      ' N ',
      'CRC',
      ' N '
    ],
    {
      C: { tag: 'c:wires/copper' },
      N: { tag: 'c:nuggets/steel' },
      R: { item: 'tfmg:rubber_sheet' }
    }
  )

  console.info(`[Industrial Colonies] TFMG-default electricity loaded; replaced ${removedEarlyElectricalRecipes.length} recipes, retired ${retiredCreateAdditionMachines.length} duplicate machines, and ported ${portedCreateAdditionRecipes.length} specialized utilities.`)
})
