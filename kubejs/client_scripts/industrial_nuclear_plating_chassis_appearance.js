// Preserve NuclearCraft identities and behavior; change only their item models.
ClientEvents.generateAssets('last',event=>{
  var models={
    'nuclearcraft:plate_advanced':'industrial_colonies:item/nuclear_advanced_plating_detail',
    'nuclearcraft:plate_du':'industrial_colonies:item/nuclear_du_plating_detail',
    'nuclearcraft:plate_elite':'industrial_colonies:item/nuclear_elite_plating_detail',
    'nuclearcraft:plate_extreme':'industrial_colonies:item/nuclear_extreme_plating_detail'
  };
  Object.keys(models).forEach(id=>{
    var parts=id.split(':');event.json(parts[0]+':models/item/'+parts[1]+'.json',{
      parent:'minecraft:item/generated',textures:{layer0:models[id]}
    });
  });
  event.json('industrial_colonies:models/item/material_parts/lead_graphite_composite_plate.json',{parent:'minecraft:item/generated',textures:{layer0:'industrial_colonies:item/lead_graphite_composite_detail'}});
  // Chassis is a structural component item, not a new placed machine/block.
  event.json('nuclearcraft:models/item/chassis.json',{parent:'tfmg:block/steel_frame/block'});
});
