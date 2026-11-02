// priority: -32000
// Upgrade installers are the only route into Mekanism factory tiers.
ServerEvents.recipes(event => {
 const blocked = ["mekanism:basic_combining_factory", "mekanism:basic_compressing_factory", "mekanism:basic_crushing_factory", "mekanism:basic_enriching_factory", "mekanism:basic_infusing_factory", "mekanism:basic_injecting_factory", "mekanism:basic_purifying_factory", "mekanism:basic_sawing_factory", "mekanism:basic_smelting_factory", "mekanism:advanced_combining_factory", "mekanism:advanced_compressing_factory", "mekanism:advanced_crushing_factory", "mekanism:advanced_enriching_factory", "mekanism:advanced_infusing_factory", "mekanism:advanced_injecting_factory", "mekanism:advanced_purifying_factory", "mekanism:advanced_sawing_factory", "mekanism:advanced_smelting_factory", "mekanism:elite_combining_factory", "mekanism:elite_compressing_factory", "mekanism:elite_crushing_factory", "mekanism:elite_enriching_factory", "mekanism:elite_infusing_factory", "mekanism:elite_injecting_factory", "mekanism:elite_purifying_factory", "mekanism:elite_sawing_factory", "mekanism:elite_smelting_factory", "mekanism:ultimate_combining_factory", "mekanism:ultimate_compressing_factory", "mekanism:ultimate_crushing_factory", "mekanism:ultimate_enriching_factory", "mekanism:ultimate_infusing_factory", "mekanism:ultimate_injecting_factory", "mekanism:ultimate_purifying_factory", "mekanism:ultimate_sawing_factory", "mekanism:ultimate_smelting_factory", "ad_astra:etrionic_blast_furnace", "modernfoundry:scorched_drain", "modernfoundry:scorched_table", "ad_astra:fan"];
 blocked.forEach(id=>event.remove({output:id}));
 event.replaceInput({}, 'ad_astra:fan', 'create:propeller');
 function replaceFan(v){
   if(!v || v.isJsonNull())return;
   if(v.isJsonArray()){v.getAsJsonArray().forEach(x=>replaceFan(x));return;}
   if(!v.isJsonObject())return;
   const o=v.getAsJsonObject();
   ['item','id'].forEach(k=>{if(o.has(k)&&o.get(k).isJsonPrimitive()&&o.get(k).getAsString()==='ad_astra:fan')o.addProperty(k,'create:propeller');});
   o.entrySet().forEach(e=>replaceFan(e.getValue()));
 }
 event.addedRecipes.removeIf(recipe=>{
   try{recipe.serialize();}catch(e){return false;}
   const d=JSON.parse(recipe.json.toString()),a=[];
   function products(v){if(!v)return;if(typeof v==='string'){a.push(v);return;}if(Array.isArray(v)){v.forEach(products);return;}if(v.id)a.push(v.id);if(v.item)a.push(v.item);}
   ['result','results','output','outputs','item_output','item_outputs'].forEach(k=>products(d[k]));
   if(a.some(id=>blocked.indexOf(id)>=0))return true;
   ['ingredient','ingredients','input','inputs','key'].forEach(k=>{if(recipe.json.has(k))replaceFan(recipe.json.get(k));});
   return false;
 });
 console.info('IC_REVIEW_R2_GATES factories=36 retired=4 installers=preserved');
});
