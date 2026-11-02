// Original recipe review: registrations retained below, temporarily inactive.
function IC_originalRecipeReview_skip() {}
// Managed-overhaul migration marker.
// Stock Factory recipes are removed by exact managed cards. Thirty-two
// non-smelting outputs use fresh-state 5x5 construction; four Smelting
// Factories stay retired. Tier Installer right-click bypasses are closed by
// the project-owned Mekanism installer blacklist block tag.
IC_originalRecipeReview_skip(() => {
  console.info('[Industrial Colonies] Legacy factory script disabled; managed KJSGen and the installer blacklist own Factory progression.')
})
