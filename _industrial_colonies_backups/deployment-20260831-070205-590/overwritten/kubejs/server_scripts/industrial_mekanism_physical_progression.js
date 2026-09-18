// Stock-recipe restoration marker.
// Control circuits, energy storage, induction hardware, and every factory tier
// retain Mekanism's native recipes until edited through the in-game UI.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Mekanism stock circuits, power hardware, and factory recipes retained; physical overrides disabled.')
})
