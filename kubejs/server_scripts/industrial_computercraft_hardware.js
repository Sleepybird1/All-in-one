// Managed-overhaul migration marker.
// ComputerCraft construction is emitted as managed, editable KJSGen cards;
// this same-named no-op removes the former script owner from deployment.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Legacy ComputerCraft hardware script disabled; managed KJSGen owns this slice.')
})
