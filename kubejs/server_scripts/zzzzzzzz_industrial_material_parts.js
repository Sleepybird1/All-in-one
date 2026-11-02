// priority: -20000
// Retire generated shortcuts; keep existing material manufacturing and exact amounts.
var IC_PARTS_RUNTIME = JsonIO.read('kubejs/config/industrial-material-parts.json');
ServerEvents.recipes(event => {
  // More Plates is removed on cutover, but also refuse its stale/generated acquisition routes.
  event.remove({mod: 'moreplates'});
  Object.keys(IC_PARTS_RUNTIME.aliases).forEach(old => {
    var target = IC_PARTS_RUNTIME.aliases[old];
    if (target && Item.exists(target)) {
      event.replaceInput({}, old, target);
      event.replaceOutput({}, old, target);
    }
  });
  // Native NuclearCraft serializers need direct JSON item normalization too.
  var visited = {};
  function normalize(recipe) {
    var id=String(recipe.getId()); if(visited[id]) return;
    recipe.serialize(); let changed=false;
    function visit(value) {
      if(value.isJsonArray()){value.getAsJsonArray().forEach(visit);return;}
      if(!value.isJsonObject())return;
      var obj=value.getAsJsonObject();
      obj.keySet().forEach(key=>{
        var child=obj.get(key), k=String(key);
        if((k==='item'||k==='id')&&child.isJsonPrimitive()&&child.getAsJsonPrimitive().isString()) {
          var target=IC_PARTS_RUNTIME.aliases[String(child.getAsString())];
          if(target&&Item.exists(target)){obj.addProperty(key,target);changed=true;}
        } else if(k!=='tag'&&k!=='fluid'&&k!=='type')visit(child);
      });
    }
    visit(recipe.json);
    if(changed){if(recipe.newRecipe)recipe.deserialize(true);recipe.changed=true;visited[id]=true;}
  }
  event.forEachRecipe({},normalize);event.addedRecipes.forEach(normalize);
  // Migration only: existing old stacks become the canonical part one-for-one.
  IC_PARTS_RUNTIME.compatibility.forEach(part => {
    if(part.target&&Item.exists(part.target))event.shapeless(part.target,[part.id])
      .id('industrial_colonies:material_parts/migrate/'+part.id.split(':')[1]);
  });
  // Existing native duplicate stacks retain a one-for-one recovery route.
  (IC_PARTS_RUNTIME.retiredDuplicates || []).forEach(part=>{
    if(Item.exists(part.id)&&Item.exists(part.target))event.shapeless(part.target,[part.id])
      .id('industrial_colonies:material_parts/migrate/native/'+part.id.replace(':','/'));
  });
});
ServerEvents.tags('item',event=>{
  var replacements=[];
  // Gather before mutation: preserve broad and mod-specific tags, not guessed tag names.
  event.tags.entrySet().forEach(entry=>{
    var tag=entry.getKey(), wrapper=entry.getValue();
    wrapper.objectIds.forEach(old=>{
      var source=String(old), target=IC_PARTS_RUNTIME.aliases[source];
      if(target&&Item.exists(target)&&source!==target)replacements.push([tag,source,target]);
    });
  });
  replacements.forEach(row=>{event.remove(row[0],row[1]);event.add(row[0],row[2]);});
  IC_PARTS_RUNTIME.parts.forEach(part=>{
    if(!Item.exists(part.canonical))return;
    var forms={gear:'gears',rod:'rods',sheet:'sheets',dust:'dusts',plate:'plates'};
    var form=forms[part.form];
    ['c:'+form,'c:'+form+'/'+part.material].forEach(tag=>event.add(tag,part.canonical));
  });
});
