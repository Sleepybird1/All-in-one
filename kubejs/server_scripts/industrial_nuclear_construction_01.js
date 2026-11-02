// Original recipe review: registrations retained below, temporarily inactive.
function IC_originalRecipeReview_skip() {}
// Managed-overhaul migration marker.
// Radiance machine construction and its prerequisite material path are emitted
// by the managed project, not duplicated in this legacy script.
IC_originalRecipeReview_skip(() => {
  console.info('[Industrial Colonies] Legacy radiance-construction script disabled; managed KJSGen owns this slice.')
})
