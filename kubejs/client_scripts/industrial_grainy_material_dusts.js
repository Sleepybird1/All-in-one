// Grainy vanilla dust shape; item tint is supplied separately, no recipe changes.
ClientEvents.generateAssets('last', event => {
  var manifest=JsonIO.read('kubejs/config/industrial-material-parts.json');
  var seen={};
  manifest.parts.forEach(part=>{
    if(part.form!=='dust'||seen[part.canonical])return;seen[part.canonical]=true;
    var id=part.canonical.split(':');
    event.json(id[0]+':models/item/'+id[1]+'.json',{
      parent:'minecraft:item/generated',textures:{layer0:'minecraft:item/gunpowder'}
    });
  });
});
