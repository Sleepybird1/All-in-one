// Original recipe review: registrations retained below, temporarily inactive.
function IC_originalRecipeReview_skip() {}
// Managed-overhaul migration marker.
// ComputerCraft construction is emitted as managed, editable KJSGen cards;
// this same-named no-op removes the former script owner from deployment.
IC_originalRecipeReview_skip(() => {
  console.info('[Industrial Colonies] Legacy ComputerCraft hardware script disabled; managed KJSGen owns this slice.')
})
