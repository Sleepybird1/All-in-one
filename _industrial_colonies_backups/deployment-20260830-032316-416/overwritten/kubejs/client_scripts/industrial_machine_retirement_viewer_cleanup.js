// Hide retired generic Mekanism machines and their factory variants. The
// specialist chemical, ore-processing, energy, and nuclear machines remain.

RecipeViewerEvents.removeEntries('item', event => {
  ;[
    'mekanism:crusher',
    'mekanism:precision_sawmill',
    'mekanism:energized_smelter',
    'mekanism:formulaic_assemblicator',
    'mekanism:basic_crushing_factory',
    'mekanism:advanced_crushing_factory',
    'mekanism:elite_crushing_factory',
    'mekanism:ultimate_crushing_factory',
    'mekanism:basic_sawing_factory',
    'mekanism:advanced_sawing_factory',
    'mekanism:elite_sawing_factory',
    'mekanism:ultimate_sawing_factory',
    'mekanism:basic_smelting_factory',
    'mekanism:advanced_smelting_factory',
    'mekanism:elite_smelting_factory',
    'mekanism:ultimate_smelting_factory'
  ].forEach(item => event.remove(item))
})
