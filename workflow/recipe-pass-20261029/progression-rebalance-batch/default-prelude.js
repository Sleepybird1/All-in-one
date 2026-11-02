function r(data){return {removed:false,serialize:function(){},json:{toString:function(){return JSON.stringify(data);}}};}
rows.add(r({result:{id:'minecraft:crafting_table'}}));
rows.add(r({result:{id:'industrial_colonies:fusion_control_unit'}}));
rows.add(r({type:'test:no_result'}));
var restored=[];var removed=[];
var ServerEvents={recipes:function(cb){cb({remove:function(filter){removed.push(filter.output);},addedRecipes:rows,custom:function(data){return {id:function(id){restored.push({id:id,data:data});}};}});}};
