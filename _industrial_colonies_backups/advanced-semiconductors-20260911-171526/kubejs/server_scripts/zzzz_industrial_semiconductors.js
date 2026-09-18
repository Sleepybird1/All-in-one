// priority: -1200
// Semiconductor ownership overlays the unchanged material/early-industry migrations.
ServerEvents.recipes(event => {
  var owned = {"industrial_colonies:prepared_silicon_wafer": "industrial_colonies:electronics/prepared_silicon_wafer", "industrial_colonies:etched_silicon_wafer": "industrial_colonies:electronics/etched_silicon_wafer", "tfmg:n_semiconductor": "industrial_colonies:electronics/n_semiconductor", "tfmg:p_semiconductor": "industrial_colonies:electronics/p_semiconductor"};
  var retired = ["industrial_colonies:processing/silicon/n_semiconductor", "industrial_colonies:processing/silicon/p_semiconductor", "industrial_colonies:processing/silicon/wafer_cutting"];
  Object.keys(owned).forEach(out => event.remove({output:out,not:{id:owned[out]}}));
  retired.forEach(id => event.remove({id:id}));
  function refs(value, list) {
    if(!value || typeof value!=='object')return;
    if(Array.isArray(value)){value.forEach(v=>refs(v,list));return;}
    if(typeof value.id==='string')list.push(value.id);
    if(typeof value.item==='string')list.push(value.item);
    Object.keys(value).forEach(k=>{if(typeof value[k]==='object')refs(value[k],list);});
  }
  event.addedRecipes.removeIf(recipe => {
    var id=String(recipe.getId());
    if(retired.indexOf(id)>=0)return true;
    try{recipe.serialize();}catch(error){return false;}
    var data=JSON.parse(recipe.json.toString()),outputs=[];
    ['result','results','output','outputs','item_output','item_outputs'].forEach(k=>refs(data[k],outputs));
    return outputs.some(out=>owned[out] && owned[out]!==id);
  });
});
