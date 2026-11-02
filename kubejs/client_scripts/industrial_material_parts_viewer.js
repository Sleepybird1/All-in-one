const IC_PARTS_VIEW = JsonIO.read('kubejs/config/industrial-material-parts.json');
RecipeViewerEvents.removeEntries('item',event=>{
  IC_PARTS_VIEW.compatibility.forEach(part=>{if(Item.exists(part.id))event.remove(part.id);});
  Object.keys(IC_PARTS_VIEW.aliases).forEach(old=>{
    const target=IC_PARTS_VIEW.aliases[old];
    if(Item.exists(old)&&(!target||Item.exists(target)))event.remove(old);
  });
});
