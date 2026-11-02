// Original recipe review: registrations retained below, temporarily inactive.
function IC_originalRecipeReview_skip() {}
// Managed-overhaul migration marker.
// This no-op overwrites the obsolete broad retirement script. Exact machine
// recipe ownership and installer-only factory removals now live in KJSGen.
IC_originalRecipeReview_skip(() => {
  console.info('[Industrial Colonies] Legacy machine-retirement script disabled; exact managed removals are authoritative.')
})
