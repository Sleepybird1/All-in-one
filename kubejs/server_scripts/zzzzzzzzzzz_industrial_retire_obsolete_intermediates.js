// priority: -60001
// User explicitly retires these old intermediates; do not remove High Purity Silicon or raw ores.
var IC_OBSOLETE_INTERMEDIATES = JsonIO.read('kubejs/config/industrial-retired-intermediates.json').items;
ServerEvents.recipes(event=>{
  IC_OBSOLETE_INTERMEDIATES.forEach(id=>{if(Item.exists(id)){event.remove({input:id});event.remove({output:id});}});
  event.addedRecipes.forEach(recipe=>{
    if(recipe.removed)return;recipe.serialize();var body=String(recipe.json);
    if(IC_OBSOLETE_INTERMEDIATES.some(id=>body.indexOf('"'+id+'"')>=0))recipe.remove();
  });
});
ServerEvents.tags('item',event=>{IC_OBSOLETE_INTERMEDIATES.forEach(id=>{if(Item.exists(id))event.removeAllTagsFrom(id);});});
RecipeViewerEvents.removeEntriesCompletely('item',event=>{
  IC_OBSOLETE_INTERMEDIATES.forEach(id=>{if(Item.exists(id))event.remove(id);});
});
