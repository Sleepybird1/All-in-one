// Managed-overhaul migration marker.
// Direct factory recipes are removed by exact managed removal cards. Managed
// Tier Installer recipes are the only factory-upgrade construction path.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Legacy factory script disabled; managed KJSGen enforces installer-only upgrades.')
})
