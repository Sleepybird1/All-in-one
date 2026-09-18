// Industrial Colonies - Phase 3 machine construction, slice 02
// Modular Machinery is the first reusable Mekanism machine platform. These
// compact machines use Create Sequenced Assembly and only consume technology
// available at or before the node. In particular, the Combiner and Osmium
// Compressor no longer require their downstream Elite/Advanced circuits.

ServerEvents.recipes(event => {
  const removedMachineRecipes = [
    'mekanism:steel_casing',
    'mekanism:tier_installer/basic',
    'mekanism:enrichment_chamber',
    'mekanism:combiner',
    'mekanism:osmium_compressor'
  ]

  removedMachineRecipes.forEach(id => event.remove({ id: id }))

  const itemIngredient = value => value.charAt(0) === '#'
    ? { tag: value.substring(1) }
    : { item: value }

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [
      { item: transitional },
      itemIngredient(ingredient)
    ],
    results: [{ id: transitional }]
  })

  const pressing = transitional => ({
    type: 'create:pressing',
    ingredients: [{ item: transitional }],
    results: [{ id: transitional }]
  })

  const sequencedMachine = (id, input, transitional, output, sequence) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: itemIngredient(input),
      loops: 1,
      results: [{ id: output }],
      sequence: sequence,
      transitional_item: { id: transitional }
    }).id(id)
  }

  // Convert the established TFMG steel/electronics platform into Mekanism's
  // reusable specialist-machine chassis.
  sequencedMachine(
    'industrial_colonies:machine/modular/steel_casing',
    'tfmg:steel_casing',
    'tfmg:steel_casing',
    'mekanism:steel_casing',
    [
      deploying('tfmg:steel_casing', '#c:ingots/osmium'),
      deploying('tfmg:steel_casing', 'tfmg:coated_circuit_board'),
      deploying('tfmg:steel_casing', 'tfmg:steel_mechanism'),
      deploying('tfmg:steel_casing', '#c:ingots/osmium'),
      pressing('tfmg:steel_casing')
    ]
  )

  // Installer progression starts as manufactured control hardware rather than
  // a cheap plank-framed handcraft.
  sequencedMachine(
    'industrial_colonies:machine/modular/basic_tier_installer',
    'tfmg:coated_circuit_board',
    'tfmg:coated_circuit_board',
    'mekanism:basic_tier_installer',
    [
      deploying('tfmg:coated_circuit_board', 'mekanism:basic_control_circuit'),
      deploying('tfmg:coated_circuit_board', 'mekanism:alloy_infused'),
      pressing('tfmg:coated_circuit_board'),
      deploying('tfmg:coated_circuit_board', 'mekanism:basic_control_circuit'),
      deploying('tfmg:coated_circuit_board', 'mekanism:alloy_infused')
    ]
  )

  sequencedMachine(
    'industrial_colonies:machine/modular/enrichment_chamber',
    'mekanism:steel_casing',
    'mekanism:steel_casing',
    'mekanism:enrichment_chamber',
    [
      deploying('mekanism:steel_casing', 'mekanism:basic_control_circuit'),
      deploying('mekanism:steel_casing', 'mekanism:alloy_infused'),
      deploying('mekanism:steel_casing', 'create:precision_mechanism'),
      deploying('mekanism:steel_casing', 'tfmg:circuit_board'),
      pressing('mekanism:steel_casing')
    ]
  )

  // The default Combiner required an Elite circuit, creating a dependency on
  // Precision Engineering downstream of this node.
  sequencedMachine(
    'industrial_colonies:machine/modular/combiner',
    'mekanism:steel_casing',
    'mekanism:steel_casing',
    'mekanism:combiner',
    [
      deploying('mekanism:steel_casing', 'tfmg:steel_chemical_vat'),
      deploying('mekanism:steel_casing', 'mekanism:basic_control_circuit'),
      deploying('mekanism:steel_casing', 'mekanism:alloy_infused'),
      deploying('mekanism:steel_casing', 'create:precision_mechanism'),
      pressing('mekanism:steel_casing')
    ]
  )

  // The default Osmium Compressor required an Advanced circuit, which is only
  // unlocked by the Reinforced Systems child of Modular Machinery.
  sequencedMachine(
    'industrial_colonies:machine/modular/osmium_compressor',
    'mekanism:steel_casing',
    'mekanism:steel_casing',
    'mekanism:osmium_compressor',
    [
      deploying('mekanism:steel_casing', 'tfmg:steel_chemical_vat'),
      deploying('mekanism:steel_casing', 'mekanism:basic_control_circuit'),
      deploying('mekanism:steel_casing', 'tfmg:transformer'),
      deploying('mekanism:steel_casing', 'create:mechanical_pump'),
      pressing('mekanism:steel_casing')
    ]
  )

  console.info(`[Industrial Colonies] Machine construction slice 02 loaded; replaced ${removedMachineRecipes.length} Modular Machinery recipes.`)
})
