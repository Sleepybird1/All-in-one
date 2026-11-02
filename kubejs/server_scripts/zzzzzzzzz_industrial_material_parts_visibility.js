// priority: -80000
// Only custom material parts: unrelated items and recipes are never disabled here.
var IC_PART_VISIBILITY = JsonIO.read('kubejs/config/industrial-material-parts.json');
let IC_USED_PARTS = {};
let IC_PART_USAGE_READY = false;
ServerEvents.recipes(event => {
  IC_USED_PARTS = {}; IC_PART_USAGE_READY = false;
  var targets={}, seenTags={};
  IC_PART_VISIBILITY.items.forEach(part=>{targets[part.canonical]=true;});
  function mark(id){id=String(id);if(targets[id])IC_USED_PARTS[id]=true;}
  function visit(value, key) {
    if(value.isJsonArray()){value.getAsJsonArray().forEach(v=>visit(v,key));return;}
    if(value.isJsonObject()){
      var obj=value.getAsJsonObject();
      obj.keySet().forEach(k=>{var name=String(k);if(name!=='fluid'&&name!=='type')visit(obj.get(k),name);});return;
    }
    if(!value.isJsonPrimitive()||!value.getAsJsonPrimitive().isString())return;
    var text=String(value.getAsString());
    if(key==='tag') {
      if(seenTags[text])return;seenTags[text]=true;
      // Item tags are expanded against the current loaded registry, not a cached snapshot.
      Ingredient.of('#'+text).itemIds.forEach(mark);
    } else mark(text);
  }
  function inspect(recipe){
    if(recipe.removed||recipe.creationError)return;
    var id=String(recipe.getId());
    // One-for-one legacy recovery alone must not make an otherwise unused part visible.
    if(id.indexOf('industrial_colonies:material_parts/migrate/')===0||id.indexOf('industrial_colonies:fabrication/recover/')===0)return;
    recipe.serialize();visit(recipe.json,'');
  }
  event.forEachRecipe({},inspect);event.addedRecipes.forEach(inspect);
  IC_PART_USAGE_READY = true;
});
RecipeViewerEvents.removeEntries('item',event=>{
  // Retired duplicates stay hidden even if an old recipe still mentions their IDs.
  Object.keys(IC_PART_VISIBILITY.aliases).forEach(old=>{
    var target=IC_PART_VISIBILITY.aliases[old];
    if(target&&Item.exists(target)&&Item.exists(old))event.remove(old);
  });
  // Fail open for unused-part filtering until the recipe scan has run.
  if(!IC_PART_USAGE_READY)return;
  IC_PART_VISIBILITY.items.forEach(part=>{
    if((IC_PART_VISIBILITY.authoringVisible||[]).indexOf(part.canonical)>=0)return;
    if(Item.exists(part.canonical)&&!IC_USED_PARTS[part.canonical])event.remove(part.canonical);
  });
});
