// Industrial Colonies - deferred spaceflight entry
//
// Space is the post-Star progression expansion. Keep raw space materials and
// non-travel components available for future authored factories, but prevent
// stock recipes from opening either prefabricated Ad Astra rockets or
// Cosmonautics block-built ships before their industrial replacements exist.
// Exact IDs are intentional: never wipe a complete mod or output namespace.

ServerEvents.recipes(event => {
  const deferredAdAstraRecipes = [
    'ad_astra:nasa_workbench',
    'ad_astra:launch_pad',
    'ad_astra:fuel_refinery',
    'ad_astra:refining/fuel_from_refining_oil',
    'ad_astra:oxygen_loading/oxygen_from_oxygen_loading_water',
    'ad_astra:nasa_workbench/tier_1_rocket_from_nasa_workbench',
    'ad_astra:nasa_workbench/tier_2_rocket_from_nasa_workbench',
    'ad_astra:nasa_workbench/tier_3_rocket_from_nasa_workbench',
    'ad_astra:nasa_workbench/tier_4_rocket_from_nasa_workbench',
    'ad_astra:space_station/earth_orbit_space_station',
    'ad_astra:space_station/moon_orbit_space_station',
    'ad_astra:space_station/mars_orbit_space_station',
    'ad_astra:space_station/venus_orbit_space_station',
    'ad_astra:space_station/mercury_orbit_space_station',
    'ad_astra:space_station/glacio_orbit_space_station'
  ]

  const deferredCosmonauticsRecipes = [
    'rocketnautics:hologram_block',
    'rocketnautics:magnetic_stabilizer',
    'rocketnautics:mechanical_crafting/rocket_thruster',
    'rocketnautics:mechanical_crafting/booster_thruster',
    'rocketnautics:crafting/mechanisms/rcs_thruster',
    'rocketnautics:crafting/mechanisms/separator',
    'rocketnautics:crafting/mechanisms/separator_charge',
    'rocketnautics:crafting/mechanisms/separator_shaft',
    'rocketnautics:crafting/mechanisms/vector_thruster',
    'rocketnautics:crafting/equipment/copper_anchor_boots',
    'rocketnautics:crafting/equipment/copper_leg_thrusters',
    'rocketnautics:crafting/equipment/jetpack',
    'rocketnautics:splashing/crushed_raw_titanium'
  ]

  const deferredOxygenShortcuts = [
    // Water electrolysis plus rotary condensation is the intended LOX line.
    // Converting one piece of flint directly into launch oxidizer is not.
    'mekanism:chemical_conversion/flint_to_oxygen'
  ]

  const deferredOrbitalConstructionRecipes = [
    // The stock Andesite recipe bootstraps physics-ship assembly before the
    // authored Orbital Construction slice. Keep this exact nested-JAR recipe
    // unavailable while leaving every other Simulated recipe untouched.
    'simulated:physics_assembler'
  ]

  const deferredWarpRecipes = [
    'cosmowarp:crystal_driver',
    'cosmowarp:memory_card'
  ]

  const deferredSpaceEntryRecipes = deferredAdAstraRecipes
    .concat(deferredCosmonauticsRecipes)
    .concat(deferredOxygenShortcuts)
    .concat(deferredOrbitalConstructionRecipes)
    .concat(deferredWarpRecipes)

  deferredSpaceEntryRecipes.forEach(id => event.remove({ id: id }))

  console.info(`[Industrial Colonies] Deferred ${deferredAdAstraRecipes.length} stock Ad Astra space-entry recipes until the spaceflight expansion.`)
  console.info(`[Industrial Colonies] Deferred ${deferredCosmonauticsRecipes.length} Cosmonautics ship-entry recipes and ${deferredWarpRecipes.length} premature warp recipes.`)
  console.info(`[Industrial Colonies] Deferred ${deferredOrbitalConstructionRecipes.length} stock physics-ship construction bootstrap pending the authored orbital construction slice.`)
  console.info(`[Industrial Colonies] Deferred ${deferredOxygenShortcuts.length} non-industrial oxygen shortcut; launch oxidizer starts with water electrolysis.`)
})
