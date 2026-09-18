// Stock-entry restoration marker.
// No Mekanism or Create Crafts & Additions machines are hidden from the recipe
// viewer. This same-named file safely overwrites the old cleanup on deployment.
RecipeViewerEvents.removeEntries('item', () => {
  console.info('[Industrial Colonies] Machine retirement viewer cleanup disabled; stock entries remain visible.')
})
