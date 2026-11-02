// priority: -1100
// Generated ownership policy; source: tools/build_ownership_progression.py.
// Run after material reconciliation so neither stock recipes nor exporters regain bypasses.
ServerEvents.recipes(event => {
  var owned = {"createcasing:weathered_iron_press": ["industrial_colonies:manufacturing/weathered_iron/press"], "createcasing:weathered_iron_deployer": ["industrial_colonies:manufacturing/weathered_iron/deployer"], "createcasing:weathered_iron_depot": ["industrial_colonies:manufacturing/weathered_iron/depot"], "createcasing:weathered_iron_encased_fan": ["industrial_colonies:manufacturing/weathered_iron/fan"], "createcasing:weathered_iron_mixer": ["industrial_colonies:manufacturing/weathered_iron/mixer"], "createcasing:weathered_iron_mechanical_saw": ["industrial_colonies:manufacturing/weathered_iron/saw"], "tfmg:steel_frame": ["industrial_colonies:ownership/steel_frame"], "tfmg:steel_casing": ["industrial_colonies:ownership/steel_casing"], "tfmg:steel_mechanism": ["industrial_colonies:ownership/steel_mechanism"], "tfmg:heavy_machinery_casing": ["industrial_colonies:tfmg_core/heavy_machinery_casing"], "tfmg:heavy_plate": ["industrial_colonies:tfmg_core/heavy_plate"], "immersiveengineering:plate_steel": ["industrial_colonies:ownership/steel_sheet"], "nuclearcraft:steel_plate": ["industrial_colonies:ownership/nuclearcraft_steel_plate"], "ad_astra:steel_plate": ["industrial_colonies:ownership/ad_astra_steel_plate"], "tfmg:cast_iron_sheet": ["industrial_colonies:ownership/cast_iron_sheet"], "tfmg:cast_iron_fluid_tank": ["industrial_colonies:ownership/cast_iron_fluid_tank"], "tfmg:cast_iron_fluid_valve": ["industrial_colonies:ownership/cast_iron_fluid_valve"], "tfmg:cast_iron_pipe": ["industrial_colonies:ownership/cast_iron_pipe"], "createcasing:copper_press": ["industrial_colonies:manufacturing/copper_press"], "createcasing:copper_deployer": ["industrial_colonies:manufacturing/copper_deployer"], "createcasing:copper_depot": ["industrial_colonies:manufacturing/copper/depot"], "createcasing:copper_encased_fan": ["industrial_colonies:manufacturing/copper/fan"], "createcasing:copper_mixer": ["industrial_colonies:manufacturing/copper/mixer"], "createcasing:copper_mechanical_saw": ["industrial_colonies:manufacturing/copper/saw"], "tfmg:steel_pipe": ["industrial_colonies:fluid_infrastructure/steel_pipe"], "tfmg:industrial_pipe": ["industrial_colonies:fluid_infrastructure/industrial_pipe"], "tfmg:fireproof_bricks": ["industrial_colonies:steelworks/fireproof_bricks"], "tfmg:fireproof_brick_reinforcement": ["industrial_colonies:steelworks/fireproof_brick_reinforcement"], "tfmg:blast_furnace_reinforcement": ["industrial_colonies:steelworks/blast_furnace_reinforcement"], "tfmg:steel_fluid_tank": ["industrial_colonies:fluid_infrastructure/steel_fluid_tank"], "tfmg:steel_chemical_vat": ["industrial_colonies:fluid_infrastructure/steel_chemical_vat"], "tfmg:fireproof_chemical_vat": ["industrial_colonies:fluid_infrastructure/fireproof_chemical_vat"], "tfmg:steel_distillation_output": ["industrial_colonies:petroleum/steel_distillation_output"], "tfmg:industrial_mixer": ["industrial_colonies:heavy_industry/industrial_mixer"], "tfmg:steel_fluid_valve": ["industrial_colonies:tfmg_coverage/steel_fluid_valve"], "tfmg:plastic_fluid_valve": ["industrial_colonies:tfmg_coverage/plastic_fluid_valve"], "tfmg:cable_tube": ["industrial_colonies:chemical_processing/cable_tube"], "createaddition:rolling_mill": ["industrial_colonies:createaddition_coverage/rolling_mill"], "nuclearcraft:alloy_smelter": ["industrial_colonies:ownership/nuclear_boundary/alloy_smelter"], "nuclearcraft:melter": ["industrial_colonies:ownership/nuclear_boundary/melter"], "nuclearcraft:ingot_former": ["industrial_colonies:ownership/nuclear_boundary/ingot_former"]};
  var retired = ["immersiveengineering:crusher", "mekanism:advanced_crushing_factory", "mekanism:basic_crushing_factory", "mekanism:crusher", "mekanism:elite_crushing_factory", "mekanism:ultimate_crushing_factory", "modernfoundry:scorched_alloyer", "nuclearcraft:manufactory", "nuclearcraft:rock_crusher"];
  var removed = 0;
  var transfers = [];
  Object.keys(owned).forEach(output => {
    event.forEachRecipe({output: output}, recipe => {
      if (owned[output].indexOf(String(recipe.id)) < 0) { recipe.remove(); removed++; }
    });
  });
  retired.forEach(output => event.remove({output: output}));
  // Empty the duplicate crushers, including already placed machines and factory upgrades.
  var blockedTypes = ['mekanism:crushing','immersiveengineering:crusher','createmetallurgy:grinding','mekanism:washing','nuclearcraft:rock_crusher',
  // Modern Foundry exclusively supplies ordinary molten-metal casting/melting.
   'modernfoundry:alloy','immersiveengineering:alloy','createmetallurgy:alloying','createmetallurgy:melting',
   'createmetallurgy:bulk_melting','createmetallurgy:entity_melting',
   'createmetallurgy:casting_in_table','createmetallurgy:casting_in_basin','createdieselgenerators:casting','tfmg:casting'];
  // Several serializers share Create's runtime RecipeType. Inspect serialized identity.
  event.forEachRecipe({}, recipe => {
    recipe.serialize();
    var data=JSON.parse(recipe.json.toString());
    // Preserve surviving non-ore NC grinding operations on Create. Raw-ore bypasses
    // have already been removed by the material policy. Multi-input conversion
    // (leather/bioplastic) uses exact-count compacting, not a probabilistic yield.
    if(data.type==='nuclearcraft:manufactory') {
      var inputs=[]; var results=[];
      (data.item_inputs || []).forEach(stack => {
        for(var n=0;n<(stack.count || 1);n++) {
          if(stack.item) inputs.push({item:stack.item});
          else if(stack.tag) inputs.push({tag:stack.tag});
          else throw new Error('Unsupported NC manufacturing input: '+recipe.getId());
        }
      });
      (data.item_outputs || []).forEach(stack => {
        if(!stack.item) throw new Error('Unsupported NC manufacturing output: '+recipe.getId());
        var result={id:stack.item,count:stack.count || 1};
        if(stack.chance!==undefined) result.chance=stack.chance;
        results.push(result);
      });
      if(inputs.length===0 || inputs.length>9 || results.length===0 || results.length>9) throw new Error('Unsupported NC manufacturing dimensions: '+recipe.getId());
      transfers.push({id:'industrial_colonies:ownership/nc/'+String(recipe.getId()).split(':')[1],data:{type:inputs.length===1?'create:crushing':'create:compacting',ingredients:inputs,results:results,processing_time:data.process_time || 200}});
      recipe.remove();removed++;return;
    }
    if(blockedTypes.indexOf(data.type)>=0) {recipe.remove();removed++;}
  });
  // KubeJS 2101 keeps added recipes separate: forEachRecipe/remove only visit
  // originalRecipes. Reconcile its public pending collection before final encoding.
  function refs(value,result) {
    if(!value || typeof value!=='object') return result;
    if(Array.isArray(value)){value.forEach(v=>refs(v,result));return result;}
    if(typeof value.id==='string')result.push(value.id);
    if(typeof value.item==='string')result.push(value.item);
    Object.keys(value).forEach(k=>{if(typeof value[k]==='object')refs(value[k],result);});
    return result;
  }
  event.addedRecipes.removeIf(recipe => {
    try {recipe.serialize();} catch(error) {return false;}
    var data=JSON.parse(recipe.json.toString());
    var values=[];
    ['result','results','output','outputs','item_output','item_outputs'].forEach(k=>refs(data[k],values));
    var id=String(recipe.getId());
    var reject=blockedTypes.indexOf(data.type)>=0 || values.some(v=>retired.indexOf(v)>=0 || (owned[v] && owned[v].indexOf(id)<0));
    if(reject)removed++;
    return reject;
  });
  transfers.forEach(entry => event.custom(entry.data).id(entry.id));
  // Keep the established coke-dust electrode feed available through the designated grinder.
  event.custom({type:'create:crushing',ingredients:[{tag:'c:coal_coke'}],results:[{id:'tfmg:coal_coke_dust'}],processing_time:250}).id('industrial_colonies:ownership/coke_grinding');
  event.custom({type:'create:crushing',ingredients:[{item:'minecraft:coal'}],results:[{id:'mekanism:dust_coal'}],processing_time:250}).id('industrial_colonies:ownership/coal_grinding');
  event.custom({type:'create:crushing',ingredients:[{item:'minecraft:charcoal'}],results:[{id:'mekanism:dust_charcoal'}],processing_time:250}).id('industrial_colonies:ownership/charcoal_grinding');
  event.custom({type:'create:mixing',ingredients:[{tag:'c:glass_blocks'},{tag:'c:glass_blocks'},{tag:'c:dusts/iron'}],results:[{id:'immersiveengineering:insulating_glass',count:2}],heat_requirement:'heated'}).id('industrial_colonies:ownership/insulating_glass');
  // Preserve this existing downstream construction-metal endpoint when retiring
  // CM's legacy cast/alloy serializers. This is not a new nuclear fuel recipe.
  event.custom({type:'industrial_colonies:industrial_iron_mixing',ingredients:[{tag:'c:ingots/lead'},{tag:'c:ingots/gold'}],results:[{id:'bigreactors:yellorium',amount:200}],heat_requirement:'heated',processing_time:160}).id('industrial_colonies:materials/yellorium/molten_alloy');
  event.custom({id:'industrial_colonies:materials/yellorium/ingot_casting',type:'modernfoundry:casting_table',fluid:{fluid:'bigreactors:yellorium',amount:100},cast:{tag:'modernfoundry:casts/multi_use/ingot'},result:{item:'bigreactors:yellorium_ingot'},cooling_time:60}).id('industrial_colonies:materials/yellorium/ingot_casting');
  console.info('[Industrial Colonies] Pre-semiconductor ownership reconciled '+removed+' alternate component/machine recipes; migrated '+transfers.length+' NC manufacturing operations.');
});
