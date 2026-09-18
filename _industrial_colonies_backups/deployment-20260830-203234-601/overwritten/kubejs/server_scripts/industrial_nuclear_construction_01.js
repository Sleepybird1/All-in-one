// Industrial Colonies - Nuclear Age manufacturing platform
// Refined Radiance remains Create's light-collection material, but turning it
// into usable nuclear machinery now converges Yellorium refinement, Ultimate
// machine control, AE2 computation, TFMG steel, and earlier Create machines.

ServerEvents.recipes(event => {
  const removedNuclearAgeRecipes = [
    'createcasing:crafting/deployer/refined_radiance',
    'createcasing:crafting/press/refined_radiance',
    'createcasing:crafting/mixer/refined_radiance',
    'createcasing:crafting/roller/refined_radiance',
    'createcasing:crafting/encased_fan/refined_radiance'
  ]

  removedNuclearAgeRecipes.forEach(id => event.remove({ id: id }))

  const deploying = (transitional, ingredient) => ({
    type: 'create:deploying',
    ingredients: [{ item: transitional }, { item: ingredient }],
    results: [{ id: transitional }]
  })

  const pressing = transitional => ({
    type: 'create:pressing',
    ingredients: [{ item: transitional }],
    results: [{ id: transitional }]
  })

  const sequencedNuclearMachine = (id, input, output, sequence) => {
    event.custom({
      type: 'create:sequenced_assembly',
      ingredient: { item: input },
      loops: 1,
      results: [{ id: output }],
      sequence: sequence,
      transitional_item: { id: input }
    }).id(id)
  }

  // Create ships the legacy Radiant Casing with no data recipe. This line is
  // the controlled construction path and gives Yellorium a structural role
  // before it becomes first-generation reactor fuel.
  sequencedNuclearMachine(
    'industrial_colonies:machine/nuclear_age/refined_radiance_casing',
    'tfmg:steel_casing',
    'create:refined_radiance_casing',
    [
      deploying('tfmg:steel_casing', 'create:refined_radiance'),
      deploying('tfmg:steel_casing', 'industrial_colonies:yellorium_compound'),
      deploying('tfmg:steel_casing', 'mekanism:ultimate_control_circuit'),
      deploying('tfmg:steel_casing', 'ae2:engineering_processor'),
      pressing('tfmg:steel_casing')
    ]
  )

  sequencedNuclearMachine(
    'industrial_colonies:machine/nuclear_age/refined_radiance_deployer',
    'create:precision_mechanism',
    'createcasing:refined_radiance_deployer',
    [
      deploying('create:precision_mechanism', 'create:refined_radiance_casing'),
      deploying('create:precision_mechanism', 'industrial_colonies:yellorium_compound'),
      deploying('create:precision_mechanism', 'mekanism:ultimate_control_circuit'),
      deploying('create:precision_mechanism', 'ae2:engineering_processor'),
      pressing('create:precision_mechanism')
    ]
  )

  sequencedNuclearMachine(
    'industrial_colonies:machine/nuclear_age/refined_radiance_press',
    'create:mechanical_press',
    'createcasing:refined_radiance_press',
    [
      deploying('create:mechanical_press', 'create:refined_radiance_casing'),
      deploying('create:mechanical_press', 'industrial_colonies:yellorium_compound'),
      deploying('create:mechanical_press', 'tfmg:steel_mechanism'),
      deploying('create:mechanical_press', 'create:precision_mechanism'),
      pressing('create:mechanical_press')
    ]
  )

  sequencedNuclearMachine(
    'industrial_colonies:machine/nuclear_age/refined_radiance_mixer',
    'create:mechanical_mixer',
    'createcasing:refined_radiance_mixer',
    [
      deploying('create:mechanical_mixer', 'create:refined_radiance_casing'),
      deploying('create:mechanical_mixer', 'industrial_colonies:yellorium_compound'),
      deploying('create:mechanical_mixer', 'tfmg:industrial_mixer'),
      deploying('create:mechanical_mixer', 'mekanism:ultimate_control_circuit'),
      pressing('create:mechanical_mixer')
    ]
  )

  sequencedNuclearMachine(
    'industrial_colonies:machine/nuclear_age/refined_radiance_mechanical_roller',
    'tfmg:steel_mechanism',
    'createcasing:refined_radiance_mechanical_roller',
    [
      deploying('tfmg:steel_mechanism', 'create:refined_radiance_casing'),
      deploying('tfmg:steel_mechanism', 'industrial_colonies:yellorium_compound'),
      deploying('tfmg:steel_mechanism', 'tfmg:industrial_mixer'),
      deploying('tfmg:steel_mechanism', 'create:precision_mechanism'),
      pressing('tfmg:steel_mechanism')
    ]
  )

  sequencedNuclearMachine(
    'industrial_colonies:machine/nuclear_age/refined_radiance_encased_fan',
    'create:encased_fan',
    'createcasing:refined_radiance_encased_fan',
    [
      deploying('create:encased_fan', 'create:refined_radiance_casing'),
      deploying('create:encased_fan', 'industrial_colonies:yellorium_compound'),
      deploying('create:encased_fan', 'tfmg:electric_motor'),
      deploying('create:encased_fan', 'tfmg:transformer'),
      pressing('create:encased_fan')
    ]
  )

  console.info(`[Industrial Colonies] Nuclear Age manufacturing loaded; replaced ${removedNuclearAgeRecipes.length} cheap machine recipes and added the missing Radiant Casing line.`)
})
