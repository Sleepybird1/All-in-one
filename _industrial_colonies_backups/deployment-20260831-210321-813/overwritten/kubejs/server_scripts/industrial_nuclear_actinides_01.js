// Managed-overhaul migration marker.
// Construction cards are managed separately from the intentionally preserved
// canonical nuclear-chemistry scripts.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Legacy actinide script disabled; managed KJSGen owns construction.')
})
