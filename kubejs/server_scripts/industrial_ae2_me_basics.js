// Original recipe review: registrations retained below, temporarily inactive.
function IC_originalRecipeReview_skip() {}
// Managed-overhaul migration marker.
// This no-op overwrites the former scripted AE2 slice. Managed KJSGen cards
// now own its exact recipe removals and replacement recipes.
IC_originalRecipeReview_skip(() => {
  console.info('[Industrial Colonies] Legacy AE2 ME script disabled; managed KJSGen owns this slice.')
})
