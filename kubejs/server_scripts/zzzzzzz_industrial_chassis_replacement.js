// priority: -19999
// Remove retired chassis production before canonical alias normalization (-20000).
ServerEvents.recipes(event=>{
  event.remove({output:'nuclearcraft:chassis'});
});
RecipeViewerEvents.removeEntriesCompletely('item',event=>{
  if(Item.exists('nuclearcraft:chassis'))event.remove('nuclearcraft:chassis');
});
