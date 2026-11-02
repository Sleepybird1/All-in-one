// priority: -10003
// One ownership table. No conversion recipes, project edits or inventory deletion.
const IC_RESOURCE_OWNERS = JsonIO.read('kubejs/config/industrial-resource-owners.json');
ServerEvents.tags('item', event => {
  IC_RESOURCE_OWNERS.retiredTagRemovals.forEach(entry => event.remove(entry.tag, entry.item));
  IC_RESOURCE_OWNERS.rules.forEach(rule => {
    if (rule.form !== 'ingot' && rule.form !== 'raw' && rule.form !== 'rod' && rule.form !== 'dust') return; // Sheets remain distinct from plates.
    const tag = (rule.form === 'raw' ? 'c:raw_materials/' : rule.form === 'rod' ? 'c:rods/' : rule.form === 'dust' ? 'c:dusts/' : 'c:ingots/') + rule.material;
    rule.alternatives.forEach(old => event.remove(tag, old));
    event.add(tag, rule.canonical);
  });
  // Mod-specific tags are audited separately; broad material/alloy tags are not guessed.
  IC_RESOURCE_OWNERS.tagUpdates.forEach(update => {
    event.remove(update.tag, update.old);
    event.add(update.tag, update.canonical);
  });
});
ServerEvents.recipes(event => {
  IC_RESOURCE_OWNERS.rules.forEach(rule => rule.alternatives.forEach(old => {
    if (!Item.exists(old)) return; // Archive-only/disabled mods must not abort all resource normalization.
    event.replaceInput({}, old, rule.canonical);
    event.replaceOutput({}, old, rule.canonical);
  }));
  // An identical native sheet producer is redundant; retain other manufacturing routes.
  event.remove({id:'createcasing:pressing/zinc',type:'create:pressing',output:'createaddition:zinc_sheet'});
  IC_RESOURCE_OWNERS.retiredOnly.forEach(id => { if(Item.exists(id)){event.remove({input:id});event.remove({output:id});} });
  // Some serializers (notably NuclearCraft) do not expose item stacks to the
  // generic replacement API. Normalize their serialized item fields centrally.
  const aliases = {};
  IC_RESOURCE_OWNERS.rules.forEach(rule => rule.alternatives.forEach(old => {aliases[old]=rule.canonical;}));
  const normalizedIds={};
  function normalize(recipe) {
    const id=String(recipe.getId());
    if(normalizedIds[id]) return false;
    recipe.serialize();
    const data=recipe.json;
    let changed=false;
    function visit(value) {
      if(value.isJsonArray()){value.getAsJsonArray().forEach(entry=>visit(entry));return;}
      if(value.isJsonObject()) {
        var nodeObject=value.getAsJsonObject();
        nodeObject.keySet().forEach(key=>{
          var child=nodeObject.get(key);
          // Only literal item references; never rewrite fluid/tag/type identities.
          if((String(key)==='item'||String(key)==='id') && child.isJsonPrimitive()
              && child.getAsJsonPrimitive().isString() && aliases[String(child.getAsString())]) {
            nodeObject.addProperty(key,aliases[String(child.getAsString())]);changed=true;
          } else if(String(key)!=='fluid'&&String(key)!=='tag'&&String(key)!=='type')visit(child);
        });
      }
    }
    visit(data);
    // Preserve the original native recipe and its exact ingredient/tag semantics.
    // Re-adding via event.custom rejects existing empty-tag recipes and loses IDs.
    if(changed){
      normalizedIds[id]=true;
      // Newly authored sequences retain nested KubeRecipe component objects.
      // Refresh those from the corrected JSON so final serialization cannot
      // restore a stale rod/ingot inside a cached assembly stage.
      if(recipe.newRecipe)recipe.deserialize(true);
      recipe.changed=true;
    }
    return changed;
  }
  event.forEachRecipe({},recipe=>normalize(recipe));
  event.addedRecipes.forEach(recipe=>normalize(recipe));
});
