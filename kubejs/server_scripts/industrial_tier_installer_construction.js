// Original recipe review: registrations retained below, temporarily inactive.
function IC_originalRecipeReview_skip() {}
// Managed-overhaul migration marker.
// Tier Installer recipes are managed cards and remain the only construction
// path to upgraded factories.
IC_originalRecipeReview_skip(() => {
  console.info('[Industrial Colonies] Legacy Tier Installer script disabled; managed KJSGen owns this slice.')
})
