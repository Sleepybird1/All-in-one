// Managed-overhaul migration marker.
// Radiance machine construction and its prerequisite material path are emitted
// by the managed project, not duplicated in this legacy script.
ServerEvents.recipes(() => {
  console.info('[Industrial Colonies] Legacy radiance-construction script disabled; managed KJSGen owns this slice.')
})
