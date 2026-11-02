// Managed-overhaul migration marker.
// This no-op overwrites the obsolete broad retirement script. Exact machine
// recipe ownership and installer-only factory removals now live in KJSGen.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Legacy machine-retirement script disabled; exact managed removals are authoritative.')
})
