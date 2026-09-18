// Managed-overhaul migration marker.
// Stock Factory recipes are removed by exact managed cards. Thirty-two
// non-smelting outputs use fresh-state 5x5 construction; four Smelting
// Factories stay retired. Tier Installer right-click bypasses are closed by
// the project-owned Mekanism installer blacklist block tag.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Legacy factory script disabled; managed KJSGen and the installer blacklist own Factory progression.')
})
