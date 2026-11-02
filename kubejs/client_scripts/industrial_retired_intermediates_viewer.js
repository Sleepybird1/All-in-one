// Explicitly retired intermediates must not appear in JEI, including hidden-item searches.
// This is NOT the new material catalog's used/unused visibility rule.
RecipeViewerEvents.removeEntriesCompletely('item',event=>{
  var retired=JsonIO.read('kubejs/config/industrial-retired-intermediates.json');
  retired.items.forEach(id=>{if(Item.exists(id))event.remove(id);});
});
