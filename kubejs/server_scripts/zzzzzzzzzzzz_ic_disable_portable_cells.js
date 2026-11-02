// priority: -23000
// Temporarily retired by user request. Preserve registered items and stored contents.
ServerEvents.recipes(event => {
  var disabled = ["ae2:portable_fluid_cell_16k", "ae2:portable_fluid_cell_1k", "ae2:portable_fluid_cell_256k", "ae2:portable_fluid_cell_4k", "ae2:portable_fluid_cell_64k", "ae2:portable_item_cell_16k", "ae2:portable_item_cell_1k", "ae2:portable_item_cell_256k", "ae2:portable_item_cell_4k", "ae2:portable_item_cell_64k", "appmek:portable_chemical_cell_16k", "appmek:portable_chemical_cell_1k", "appmek:portable_chemical_cell_256k", "appmek:portable_chemical_cell_4k", "appmek:portable_chemical_cell_64k", "megacells:portable_chemical_cell_16m", "megacells:portable_chemical_cell_1m", "megacells:portable_chemical_cell_256m", "megacells:portable_chemical_cell_4m", "megacells:portable_chemical_cell_64m", "megacells:portable_experience_cell_16m", "megacells:portable_experience_cell_1m", "megacells:portable_experience_cell_256m", "megacells:portable_experience_cell_4m", "megacells:portable_experience_cell_64m", "megacells:portable_fluid_cell_16m", "megacells:portable_fluid_cell_1m", "megacells:portable_fluid_cell_256m", "megacells:portable_fluid_cell_4m", "megacells:portable_fluid_cell_64m", "megacells:portable_item_cell_16m", "megacells:portable_item_cell_1m", "megacells:portable_item_cell_256m", "megacells:portable_item_cell_4m", "megacells:portable_item_cell_64m", "megacells:portable_mana_cell_16m", "megacells:portable_mana_cell_1m", "megacells:portable_mana_cell_256m", "megacells:portable_mana_cell_4m", "megacells:portable_mana_cell_64m", "megacells:portable_source_cell_16m", "megacells:portable_source_cell_1m", "megacells:portable_source_cell_256m", "megacells:portable_source_cell_4m", "megacells:portable_source_cell_64m"];
  disabled.forEach(id => { if (Item.exists(id)) event.remove({output: id}); });
  function products(value, result) {
    if (!value) return;
    if (typeof value === 'string') { result.push(value); return; }
    if (Array.isArray(value)) { value.forEach(v => products(v, result)); return; }
    if (typeof value.id === 'string') result.push(value.id);
    if (typeof value.item === 'string') result.push(value.item);
  }
  var removed = 0;
  event.addedRecipes.removeIf(recipe => {
    try { recipe.serialize(); } catch (error) { return false; }
    var data = JSON.parse(recipe.json.toString()), outputs = [];
    ['result','results','output','outputs','item_output','item_outputs'].forEach(k => products(data[k], outputs));
    var reject = outputs.some(id => disabled.indexOf(id) >= 0);
    if (reject) removed++;
    return reject;
  });
  console.info('[Industrial Colonies] Portable cells retired: 45 item variants; removed '+removed+' pending recipes.');
});
