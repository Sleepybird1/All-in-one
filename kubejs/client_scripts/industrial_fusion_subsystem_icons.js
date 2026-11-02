// Detailed native cuboid models; item identities and recipes remain unchanged.
ClientEvents.generateAssets('last',event=>{
 ['pulse_power_module','magnet_protection_module','fusion_control_unit'].forEach(name=>{
  event.json('industrial_colonies:models/item/'+name+'.json',{parent:'industrial_colonies:item/fusion_subsystems/'+name});
 });
});
