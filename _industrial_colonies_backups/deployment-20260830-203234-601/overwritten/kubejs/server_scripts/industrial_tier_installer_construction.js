// Industrial Colonies - staged Mekanism Tier Installer construction
// Factory tiers remain upgraded in-world, but the upgrade hardware itself is
// manufactured through Create. Each installer consumes the previous tier, so
// no tier can be mass-produced without first establishing the earlier line.

ServerEvents.recipes(event => {
  const removedInstallerRecipes = [
    'mekanism:tier_installer/advanced',
    'mekanism:tier_installer/elite',
    'mekanism:tier_installer/ultimate'
  ]

  removedInstallerRecipes.forEach(id => event.remove({ id: id }))

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [
      { item: transitional },
      { item: ingredient }
    ],
    results: [{ id: transitional }]
  })

  const pressing = transitional => ({
    type: 'create:pressing',
    ingredients: [{ item: transitional }],
    results: [{ id: transitional }]
  })

  const sequencedInstaller = (id, input, output, loops, sequence) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: input },
      loops: loops,
      results: [{ id: output }],
      sequence: sequence,
      transitional_item: { id: input }
    }).id(id)
  }

  // Reinforced Systems: upgrade the Basic programming hardware twice with
  // Advanced controls, diamond-infused alloy, and TFMG steel mechanisms.
  sequencedInstaller(
    'industrial_colonies:machine/installer/advanced',
    'mekanism:basic_tier_installer',
    'mekanism:advanced_tier_installer',
    2,
    [
      deploying('mekanism:basic_tier_installer', 'mekanism:advanced_control_circuit'),
      deploying('mekanism:basic_tier_installer', 'mekanism:alloy_reinforced'),
      deploying('mekanism:basic_tier_installer', 'tfmg:steel_mechanism'),
      pressing('mekanism:basic_tier_installer')
    ]
  )

  // Precision Engineering: the Elite installer converges the reinforced
  // factory line with AE2 computation and the atomic-alloy process.
  sequencedInstaller(
    'industrial_colonies:machine/installer/elite',
    'mekanism:advanced_tier_installer',
    'mekanism:elite_tier_installer',
    2,
    [
      deploying('mekanism:advanced_tier_installer', 'mekanism:elite_control_circuit'),
      deploying('mekanism:advanced_tier_installer', 'mekanism:alloy_atomic'),
      deploying('mekanism:advanced_tier_installer', 'ae2:engineering_processor'),
      deploying('mekanism:advanced_tier_installer', 'create:precision_mechanism'),
      pressing('mekanism:advanced_tier_installer')
    ]
  )

  // High-Energy Distribution: the last installer is a large assembly project
  // and explicitly consumes equipment from the converging high-voltage branch.
  event.custom({
    type: 'create:mechanical_crafting',
    accept_mirrored: false,
    category: 'misc',
    key: {
      A: { item: 'mekanism:alloy_atomic' },
      C: { item: 'mekanism:ultimate_control_circuit' },
      E: { item: 'ae2:engineering_processor' },
      I: { item: 'mekanism:elite_tier_installer' },
      T: { item: 'electroenergetics:transformer' },
      V: { item: 'electroenergetics:high_voltage_capacitor' },
      W: { item: 'electroenergetics:heavily_insulated_wire_spool' }
    },
    pattern: [
      ' WTW ',
      'ACCCA',
      'VEIEV',
      'ACCCA',
      ' WTW '
    ],
    result: { count: 1, id: 'mekanism:ultimate_tier_installer' },
    show_notification: false
  }).id('industrial_colonies:machine/installer/ultimate')

  console.info(`[Industrial Colonies] Tier Installer construction loaded; replaced ${removedInstallerRecipes.length} default recipes.`)
})
