// Preserve the item's identity/recipes; replace only its generic powder model.
ClientEvents.generateAssets('last',event=>{
  event.json('industrial_colonies:models/item/high_purity_silicon.json',{
    parent:'minecraft:item/generated',textures:{layer0:'tfmg:item/silicon_ingot'}
  });
});
