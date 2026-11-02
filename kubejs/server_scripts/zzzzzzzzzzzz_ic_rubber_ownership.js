// priority: -30000
// Preserve the user's resin rubber and rubber-sheet recipes; remove bypasses.
ServerEvents.recipes(event => {
  var owned = {
    'createmechanisms:rubber': 'industrial_colonies:drafts/resin_rubber_review_20260927',
    'tfmg:rubber_sheet': 'industrial_colonies:personal/7c33c78b_1eb8_4c78_9d91_897868ef4a43'
  };
  Object.keys(owned).forEach(output => event.remove({output: output, not: {id: owned[output]}}));
  function outputs(value, result) {
    if (!value) return;
    if (typeof value === 'string') { result.push(value); return; }
    if (Array.isArray(value)) { value.forEach(v => outputs(v, result)); return; }
    if (typeof value.id === 'string') result.push(value.id);
    if (typeof value.item === 'string') result.push(value.item);
  }
  var removed = 0;
  event.addedRecipes.removeIf(recipe => {
    recipe.serialize();
    var data = JSON.parse(recipe.json.toString()), result = [], id = String(recipe.getId());
    ['result', 'results', 'output', 'outputs', 'item_output', 'item_outputs'].forEach(k => outputs(data[k], result));
    var bypass = result.some(output => owned[output] && owned[output] !== id);
    if (bypass) removed++;
    return bypass;
  });
  console.info('IC_RUBBER_OWNERSHIP_COMPLETE removed_pending=' + removed);
});
