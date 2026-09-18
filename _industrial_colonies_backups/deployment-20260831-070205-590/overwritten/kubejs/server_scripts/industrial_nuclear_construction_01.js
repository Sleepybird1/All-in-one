// Stock-recipe restoration marker.
// Create Casing Radiance machines retain their native recipes. The previously
// added Chromatic Compound and Radiant Casing routes are intentionally disabled
// so their final recipes can be authored in the machine-centric editor.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Nuclear Create-machine stock recipes retained; custom construction routes disabled.')
})
