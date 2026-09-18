// Industrial Colonies - Create Metallurgy casting codec repair
//
// Create Metallurgy publishes these nine optional casts through common output
// tags. KubeJS 1.21 resolves each tag to a Mekanism item, but serializes the
// resolved output using the obsolete { item: "namespace:path" } shape. Replace
// them with the current CastingOutput item-stack shape while preserving the
// original IDs, fluid costs, molds, and processing times.

ServerEvents.recipes(event => {
  const casts = [
    { material: 'tin', form: 'nugget', amount: 10, time: 6, mold: 'createmetallurgy:graphite_nugget_mold', output: 'mekanism:nugget_tin' },
    { material: 'tin', form: 'ingot', amount: 90, time: 60, mold: 'createmetallurgy:graphite_ingot_mold', output: 'mekanism:ingot_tin' },
    { material: 'tin', form: 'block', amount: 810, time: 480, output: 'mekanism:block_tin' },
    { material: 'bronze', form: 'nugget', amount: 10, time: 6, mold: 'createmetallurgy:graphite_nugget_mold', output: 'mekanism:nugget_bronze' },
    { material: 'bronze', form: 'ingot', amount: 90, time: 60, mold: 'createmetallurgy:graphite_ingot_mold', output: 'mekanism:ingot_bronze' },
    { material: 'bronze', form: 'block', amount: 810, time: 480, output: 'mekanism:block_bronze' },
    { material: 'osmium', form: 'nugget', amount: 10, time: 6, mold: 'createmetallurgy:graphite_nugget_mold', output: 'mekanism:nugget_osmium' },
    { material: 'osmium', form: 'ingot', amount: 90, time: 60, mold: 'createmetallurgy:graphite_ingot_mold', output: 'mekanism:ingot_osmium' },
    { material: 'osmium', form: 'block', amount: 810, time: 480, output: 'mekanism:block_osmium' }
  ]

  casts.forEach(cast => {
    const basin = cast.form === 'block'
    const id = `createmetallurgy:casting_in_${basin ? 'basin' : 'table'}/${cast.material}/${cast.form}`
    const ingredients = [
      { type: 'neoforge:single', amount: cast.amount, fluid: `createmetallurgy:molten_${cast.material}` }
    ]

    if (cast.mold) {
      ingredients.push({ item: cast.mold })
    }

    event.remove({ id: id })
    event.custom({
      type: basin ? 'createmetallurgy:casting_in_basin' : 'createmetallurgy:casting_in_table',
      ingredients: ingredients,
      processing_time: cast.time,
      result: { item: { count: 1, id: cast.output } }
    }).id(id)
  })

  console.info('[Industrial Colonies] Repaired 9 Create Metallurgy tag-output casting recipes for KubeJS 1.21.')
})
