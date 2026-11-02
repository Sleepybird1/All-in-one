// Original recipe review: show registered alternatives.
function IC_originalRecipeReview_skip() {}
// Managed-overhaul migration marker.
// Managed construction outputs remain visible in the recipe viewer. This
// same-named no-op safely overwrites the old broad cleanup on deployment.
IC_originalRecipeReview_skip('item', () => {
  console.info('[Industrial Colonies] Legacy machine-retirement viewer cleanup disabled; managed entries remain visible.')
})
