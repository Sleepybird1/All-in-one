// Industrial Colonies - Mekanism factory progression
//
// Generic Crusher/Sawmill/Smelter factories are retired elsewhere. The six
// specialist factory families below remain, but they must be created and
// advanced in-world with the Basic -> Advanced -> Elite -> Ultimate Tier
// Installers. Direct crafting recipes are removed at every tier.

ServerEvents.recipes(event => {
  const removedFactoryRecipes = [
    'mekanism:factory/basic/combining',
    'mekanism:factory/advanced/combining',
    'mekanism:factory/elite/combining',
    'mekanism:factory/ultimate/combining',
    'mekanism:factory/basic/compressing',
    'mekanism:factory/advanced/compressing',
    'mekanism:factory/elite/compressing',
    'mekanism:factory/ultimate/compressing',
    'mekanism:factory/basic/enriching',
    'mekanism:factory/advanced/enriching',
    'mekanism:factory/elite/enriching',
    'mekanism:factory/ultimate/enriching',
    'mekanism:factory/basic/infusing',
    'mekanism:factory/advanced/infusing',
    'mekanism:factory/elite/infusing',
    'mekanism:factory/ultimate/infusing',
    'mekanism:factory/basic/purifying',
    'mekanism:factory/advanced/purifying',
    'mekanism:factory/elite/purifying',
    'mekanism:factory/ultimate/purifying',
    'mekanism:factory/basic/injecting',
    'mekanism:factory/advanced/injecting',
    'mekanism:factory/elite/injecting',
    'mekanism:factory/ultimate/injecting'
  ]

  removedFactoryRecipes.forEach(id => event.remove({ id: id }))

  console.info(`[Industrial Colonies] Installer-only factory progression loaded; removed ${removedFactoryRecipes.length} direct factory recipes.`)
})
