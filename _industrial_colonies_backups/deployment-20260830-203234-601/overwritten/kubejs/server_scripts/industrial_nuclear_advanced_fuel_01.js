// Industrial Colonies - Phase 4 advanced nuclear fuel, slice 01
// Reinforced reactor construction is the physical payoff for Mekanism
// plutonium production. Every new construction line consumes a Plutonium
// Pellet; only the two same-tier casing recycling recipes remain untouched.

ServerEvents.recipes(event => {
  const removedReinforcedRecipes = [
    'bigreactors:reactor/reinforced/activefluidport_forge',
    'bigreactors:reactor/reinforced/activetap_fe',
    'bigreactors:reactor/reinforced/casing',
    'bigreactors:reactor/reinforced/casing_alt',
    'bigreactors:reactor/reinforced/casing_upgrade',
    'bigreactors:reactor/reinforced/casing_upgrade_alt',
    'bigreactors:reactor/reinforced/chargingfe',
    'bigreactors:reactor/reinforced/computerport',
    'bigreactors:reactor/reinforced/computerport_alt',
    'bigreactors:reactor/reinforced/controller_ingots_uranium',
    'bigreactors:reactor/reinforced/controller_ingots_yellorium',
    'bigreactors:reactor/reinforced/controlrod',
    'bigreactors:reactor/reinforced/controlrod_alt',
    'bigreactors:reactor/reinforced/fluidaccessport',
    'bigreactors:reactor/reinforced/fluidaccessport_alt',
    'bigreactors:reactor/reinforced/fuelrod_alt_ingots_uranium',
    'bigreactors:reactor/reinforced/fuelrod_alt_ingots_yellorium',
    'bigreactors:reactor/reinforced/fuelrod_ingots_uranium',
    'bigreactors:reactor/reinforced/fuelrod_ingots_yellorium',
    'bigreactors:reactor/reinforced/glass',
    'bigreactors:reactor/reinforced/passivefluidport_forge',
    'bigreactors:reactor/reinforced/passivefluidport_mekanism',
    'bigreactors:reactor/reinforced/passivetap_fe',
    'bigreactors:reactor/reinforced/redstoneport',
    'bigreactors:reactor/reinforced/redstoneport_alt',
    'bigreactors:reactor/reinforced/solidaccessport',
    'bigreactors:reactor/reinforced/solidaccessport_alt',
    'er2create:reactor/reinforced/diplaysource',
    'er2create:reactor/reinforced/diplaysource_alt'
  ]

  removedReinforcedRecipes.forEach(id => event.remove({ id: id }))

  const itemIngredient = value => value.charAt(0) === '#'
    ? { tag: value.substring(1) }
    : { item: value }

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [{ item: transitional }, itemIngredient(ingredient)],
    results: [{ id: transitional }]
  })

  const pressing = transitional => ({
    type: 'create:pressing',
    ingredients: [{ item: transitional }],
    results: [{ id: transitional }]
  })

  const sequencedReinforced = (id, input, output, count, ingredients) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: input },
      loops: 1,
      results: [{ count: count, id: output }],
      sequence: ingredients
        .map(ingredient => deploying(input, ingredient))
        .concat([pressing(input)]),
      transitional_item: { id: input }
    }).id(id)
  }

  // The advanced shell grows out of the post-criticality reprocessor rather
  // than bypassing it with steel, graphite, and an iron block.
  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_reactor_casing',
    'bigreactors:reprocessorcasing',
    'bigreactors:reinforced_reactorcasing',
    4,
    [
      'mekanism:pellet_plutonium',
      'create:refined_radiance_casing',
      'mekanism:alloy_atomic',
      '#c:plates/lead',
      'tfmg:steel_mechanism'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_reactor_glass',
    'bigreactors:reinforced_reactorcasing',
    'bigreactors:reinforced_reactorglass',
    1,
    ['mekanism:pellet_plutonium', '#c:glass_blocks']
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_reactor_fuel_rod',
    'bigreactors:basic_reactorfuelrod',
    'bigreactors:reinforced_reactorfuelrod',
    1,
    [
      'mekanism:pellet_plutonium',
      'mekanism:alloy_atomic',
      '#c:plates/lead',
      'tfmg:steel_mechanism',
      'create:refined_radiance_casing'
    ]
  )

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'mekanism:alloy_atomic' },
      B: { item: 'bigreactors:basic_reactorcontrolrod' },
      C: { item: 'bigreactors:reinforced_reactorcasing' },
      E: { item: 'ae2:engineering_processor' },
      P: { item: 'mekanism:pellet_plutonium' },
      U: { item: 'mekanism:ultimate_control_circuit' }
    },
    pattern: [
      ' CAC ',
      'CUPUC',
      'APBPA',
      'CUEUC',
      ' CAC '
    ],
    result: { count: 1, id: 'bigreactors:reinforced_reactorcontrolrod' },
    show_notification: false
  }).id('industrial_colonies:machine/advanced_nuclear/reinforced_reactor_control_rod')

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'mekanism:alloy_atomic' },
      B: { item: 'bigreactors:basic_reactorcontroller' },
      C: { item: 'bigreactors:reinforced_reactorcasing' },
      E: { item: 'ae2:engineering_processor' },
      P: { item: 'mekanism:pellet_plutonium' },
      R: { item: 'create:refined_radiance_casing' },
      U: { item: 'mekanism:ultimate_control_circuit' },
      X: { item: 'bigreactors:reprocessorcontroller' }
    },
    pattern: [
      ' CRC ',
      'CPEPC',
      'AUBUA',
      'CPXPC',
      ' CRC '
    ],
    result: { count: 1, id: 'bigreactors:reinforced_reactorcontroller' },
    show_notification: false
  }).id('industrial_colonies:machine/advanced_nuclear/reinforced_reactor_controller')

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_solid_access_port',
    'bigreactors:reinforced_reactorcasing',
    'bigreactors:reinforced_reactorsolidaccessport',
    1,
    [
      'mekanism:pellet_plutonium',
      'bigreactors:basic_reactorsolidaccessport',
      'bigreactors:reprocessoroutputport',
      'create:chute',
      'mekanism:ultimate_control_circuit'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_fluid_access_port',
    'bigreactors:reinforced_reactorcasing',
    'bigreactors:reinforced_reactorfluidaccessport',
    1,
    [
      'mekanism:pellet_plutonium',
      'bigreactors:reprocessorfluidinjector',
      'bigreactors:reprocessoroutputport',
      'create:mechanical_pump',
      'mekanism:rotary_condensentrator',
      'mekanism:ultimate_control_circuit'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_power_tap_passive',
    'bigreactors:reinforced_reactorcasing',
    'bigreactors:reinforced_reactorpowertapfe_passive',
    1,
    [
      'mekanism:pellet_plutonium',
      'bigreactors:basic_reactorpowertapfe_passive',
      'bigreactors:reprocessorpowerport',
      'electroenergetics:connector',
      'mekanism:ultimate_universal_cable',
      'tfmg:transformer'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_power_tap_active',
    'bigreactors:reinforced_reactorpowertapfe_passive',
    'bigreactors:reinforced_reactorpowertapfe_active',
    1,
    [
      'mekanism:pellet_plutonium',
      'create:content_observer',
      'mekanism:ultimate_control_circuit',
      'tfmg:generator'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_charging_port',
    'bigreactors:reinforced_reactorpowertapfe_active',
    'bigreactors:reinforced_reactorchargingportfe',
    1,
    [
      'mekanism:pellet_plutonium',
      'mekanism:ultimate_induction_cell',
      'ae2:engineering_processor',
      'create:refined_radiance_casing'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_redstone_port',
    'bigreactors:reinforced_reactorcasing',
    'bigreactors:reinforced_reactorredstoneport',
    1,
    [
      'mekanism:pellet_plutonium',
      'bigreactors:basic_reactorredstoneport',
      'create:content_observer',
      'tfmg:circuit_board',
      'mekanism:ultimate_control_circuit'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_computer_port',
    'bigreactors:reinforced_reactorcasing',
    'bigreactors:reinforced_reactorcomputerport',
    1,
    [
      'mekanism:pellet_plutonium',
      'createaddition:digital_adapter',
      'ae2:engineering_processor',
      'tfmg:circuit_board',
      'mekanism:ultimate_control_circuit'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_display_source',
    'bigreactors:reinforced_reactorcasing',
    'er2create:reinforced_reactordisplaysource',
    1,
    [
      'mekanism:pellet_plutonium',
      'createaddition:digital_adapter',
      'create:content_observer',
      'ae2:engineering_processor',
      'tfmg:steel_mechanism'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_fluid_port_forge_passive',
    'bigreactors:reinforced_reactorcasing',
    'bigreactors:reinforced_reactorfluidport_forge_passive',
    1,
    [
      'mekanism:pellet_plutonium',
      'create:mechanical_pump',
      'create:fluid_pipe',
      'bigreactors:reprocessorfluidinjector',
      'create:refined_radiance_casing'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_fluid_port_forge_active',
    'bigreactors:reinforced_reactorfluidport_forge_passive',
    'bigreactors:reinforced_reactorfluidport_forge_active',
    1,
    [
      'mekanism:pellet_plutonium',
      'create:content_observer',
      'mekanism:ultimate_control_circuit',
      'create:mechanical_pump'
    ]
  )

  sequencedReinforced(
    'industrial_colonies:machine/advanced_nuclear/reinforced_fluid_port_mekanism_passive',
    'bigreactors:reinforced_reactorcasing',
    'bigreactors:reinforced_reactorfluidport_mekanism_passive',
    1,
    [
      'mekanism:pellet_plutonium',
      'mekanism:rotary_condensentrator',
      'mekanism:chemical_washer',
      'bigreactors:reprocessorfluidinjector',
      'mekanism:ultimate_control_circuit'
    ]
  )

  console.info(`[Industrial Colonies] Advanced Nuclear Fuel loaded; replaced ${removedReinforcedRecipes.length} reinforced construction recipes and preserved two recycling recipes.`)
})
