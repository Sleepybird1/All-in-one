// priority: -60000
// User explicitly retires these two intermediates; raw Cinnabar remains untouched.
var IC_RETIRED_CINNABAR=['industrial_colonies:cinnabar_dust','industrial_colonies:roasted_cinnabar'];
ServerEvents.recipes(event=>{
  IC_RETIRED_CINNABAR.forEach(id=>{event.remove({input:id});event.remove({output:id});});
  event.addedRecipes.forEach(recipe=>{
    if(recipe.removed)return;
    recipe.serialize();var body=String(recipe.json);
    if(IC_RETIRED_CINNABAR.some(id=>body.indexOf('"'+id+'"')>=0))recipe.remove();
  });
});
ServerEvents.tags('item',event=>{
  IC_RETIRED_CINNABAR.forEach(id=>event.removeAllTagsFrom(id));
});
RecipeViewerEvents.removeEntries('item',event=>{
  IC_RETIRED_CINNABAR.forEach(id=>{if(Item.exists(id))event.remove(id);});
});
