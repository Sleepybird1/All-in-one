// Managed-overhaul migration marker.
// This no-op prevents a legacy script from duplicating the managed, editable
// AE2 processor construction cards.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Legacy AE2 processor script disabled; managed KJSGen owns this slice.')
})
