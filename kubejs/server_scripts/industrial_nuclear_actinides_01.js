// Industrial Colonies - canonical actinide chemistry bridge.
//
// Managed KJSGen owns the Radioactive Waste Barrel and Solar Neutron
// Activator construction recipes. Mekanism Generators is intentionally absent
// from this pack, however, so its reactor cannot supply Mekanism Nuclear Waste.
// Route spent Extreme Reactors fuel forward through the existing TFMG acid and
// Mekanism chemical-processing chain instead.
ServerEvents.recipes(event => {
  event.custom({
    type: 'mekanism:dissolution',
    chemical_input: { amount: 1, chemical: 'mekanism:sulfuric_acid' },
    item_input: { count: 1, item: 'bigreactors:blutonium_ingot' },
    output: { amount: 1000, id: 'mekanism:nuclear_waste' },
    per_tick_usage: true
  }).id('industrial_colonies:chemistry/actinide/nuclear_waste_from_blutonium')

  console.info('[Industrial Colonies] Canonical actinide waste bridge loaded; managed KJSGen owns machine construction.')
})
