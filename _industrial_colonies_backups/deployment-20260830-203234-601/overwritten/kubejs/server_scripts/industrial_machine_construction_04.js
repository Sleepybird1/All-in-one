// Industrial Colonies - Phase 3 machine construction, slice 04
// Chemical Separation is upstream of Reinforced Systems / Precision
// Engineering convergence. Its machines therefore use AE2 computation and
// Basic Mekanism controls instead of circular Advanced/Elite/Ultimate circuits.

ServerEvents.recipes(event => {
  const removedMachineRecipes = [
    'mekanism:purification_chamber',
    'mekanism:chemical_injection_chamber',
    'mekanism:chemical_dissolution_chamber',
    'mekanism:chemical_washer',
    'mekanism:chemical_crystallizer'
  ]

  removedMachineRecipes.forEach(id => event.remove({ id: id }))

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

  const sequencedUpgrade = (id, input, output, sequence) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: input },
      loops: 1,
      results: [{ id: output }],
      sequence: sequence,
      transitional_item: { id: input }
    }).id(id)
  }

  // Preserve the useful Mekanism machine lineage while changing its control
  // dependency: Enrichment -> Purification -> Chemical Injection.
  sequencedUpgrade(
    'industrial_colonies:machine/chemical_separation/purification_chamber',
    'mekanism:enrichment_chamber',
    'mekanism:purification_chamber',
    [
      deploying('mekanism:enrichment_chamber', 'mekanism:basic_control_circuit'),
      deploying('mekanism:enrichment_chamber', 'mekanism:alloy_infused'),
      deploying('mekanism:enrichment_chamber', 'tfmg:steel_chemical_vat'),
      deploying('mekanism:enrichment_chamber', 'ae2:calculation_processor'),
      pressing('mekanism:enrichment_chamber')
    ]
  )

  sequencedUpgrade(
    'industrial_colonies:machine/chemical_separation/chemical_injection_chamber',
    'mekanism:purification_chamber',
    'mekanism:chemical_injection_chamber',
    [
      deploying('mekanism:purification_chamber', 'mekanism:basic_control_circuit'),
      deploying('mekanism:purification_chamber', 'mekanism:alloy_infused'),
      deploying('mekanism:purification_chamber', 'tfmg:transformer'),
      deploying('mekanism:purification_chamber', 'ae2:engineering_processor'),
      deploying('mekanism:purification_chamber', 'create:mechanical_pump'),
      pressing('mekanism:purification_chamber')
    ]
  )

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      B: { item: 'mekanism:basic_control_circuit' },
      C: { item: 'mekanism:steel_casing' },
      F: { item: 'mekanism:chemical_infuser' },
      I: { item: 'ae2:engineering_processor' },
      O: { tag: 'c:ingots/osmium' },
      P: { item: 'create:mechanical_pump' },
      T: { item: 'tfmg:transformer' },
      V: { item: 'tfmg:steel_chemical_vat' }
    },
    pattern: [
      ' OBO ',
      'OVFVO',
      'BPCPB',
      'OTITO',
      ' OBO '
    ],
    result: { count: 1, id: 'mekanism:chemical_dissolution_chamber' },
    show_notification: false
  }).id('industrial_colonies:machine/chemical_separation/chemical_dissolution_chamber')

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'ae2:calculation_processor' },
      B: { item: 'mekanism:basic_control_circuit' },
      C: { item: 'mekanism:steel_casing' },
      O: { tag: 'c:ingots/osmium' },
      P: { item: 'create:mechanical_pump' },
      T: { item: 'tfmg:transformer' },
      V: { item: 'tfmg:steel_chemical_vat' }
    },
    pattern: [
      'OVVO',
      'BCTB',
      'OPPO',
      'OAAO'
    ],
    result: { count: 1, id: 'mekanism:chemical_washer' },
    show_notification: false
  }).id('industrial_colonies:machine/chemical_separation/chemical_washer')

  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      B: { item: 'mekanism:basic_control_circuit' },
      C: { item: 'mekanism:steel_casing' },
      E: { item: 'tfmg:electrode_holder' },
      F: { tag: 'c:gems/fluorite' },
      I: { item: 'ae2:engineering_processor' },
      P: { item: 'create:precision_mechanism' },
      T: { item: 'tfmg:transformer' },
      V: { item: 'tfmg:steel_chemical_vat' }
    },
    pattern: [
      ' FEF ',
      'FBTBF',
      'EICIE',
      'FVPVF',
      ' FEF '
    ],
    result: { count: 1, id: 'mekanism:chemical_crystallizer' },
    show_notification: false
  }).id('industrial_colonies:machine/chemical_separation/chemical_crystallizer')

  console.info(`[Industrial Colonies] Machine construction slice 04 loaded; replaced ${removedMachineRecipes.length} Chemical Separation recipes.`)
})
