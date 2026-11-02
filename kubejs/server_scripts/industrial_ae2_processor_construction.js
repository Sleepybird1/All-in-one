// Original recipe review: registrations retained below, temporarily inactive.
function IC_originalRecipeReview_skip() {}
// Managed-overhaul migration marker.
// This no-op prevents a legacy script from duplicating the managed, editable
// AE2 processor construction cards.
IC_originalRecipeReview_skip(() => {
  console.info('[Industrial Colonies] Legacy AE2 processor script disabled; managed KJSGen owns this slice.')
})
