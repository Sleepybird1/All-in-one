// priority: -90000
// User explicitly disables this redundant pattern autocrafter.
ServerEvents.recipes(event=>{
 event.remove({output:'nuclearcraft:engineers_crafting_table'});
 event.addedRecipes.removeIf(recipe=>{
  if(recipe.removed)return false;
  recipe.serialize();var d=JSON.parse(recipe.json.toString());
  return !!(d.result&&(d.result.id==='nuclearcraft:engineers_crafting_table'||d.result.item==='nuclearcraft:engineers_crafting_table'));
 });
});
RecipeViewerEvents.removeEntriesCompletely('item',event=>{
 if(Item.exists('nuclearcraft:engineers_crafting_table'))event.remove('nuclearcraft:engineers_crafting_table');
});
