// Managed-overhaul migration marker.
// This no-op overwrites the former scripted AE2 slice. Managed KJSGen cards
// now own its exact recipe removals and replacement recipes.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Legacy AE2 ME script disabled; managed KJSGen owns this slice.')
})
