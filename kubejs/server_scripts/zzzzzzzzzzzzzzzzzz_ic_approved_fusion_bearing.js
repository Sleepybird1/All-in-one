// priority: -95000
// Approved item/recipe only. Never export the temporary Diorite prototype.
ServerEvents.recipes(event=>{
 event.remove({id:'industrial_colonies:mockup/fusion_controller_blank'});
 if(!Item.exists('industrial_colonies:fusion_control_bearing')){
  console.warn('Fusion Control Bearing: full game restart required to register the approved component.');
  return;
 }
 event.remove({output:'industrial_colonies:fusion_control_bearing'});
event.recipes.create.mechanical_crafting('industrial_colonies:fusion_control_bearing', ['ABCBA', 'BDEDB', 'CEFEC', 'BDEDB', 'ABCBA'], {
    A: 'industrial_colonies:material_parts/tough_alloy_plate',
    B: 'industrial_colonies:material_parts/hsla_steel_rod',
    C: 'industrial_colonies:material_parts/stainless_steel_plate',
    D: 'industrial_colonies:material_parts/tungsten_carbide_plate',
    E: 'allthemodium:allthemodium_rod',
    F: 'tfmg:nickel_frame'
  }).group('Fusion Control Bearing / approved structural component').id('industrial_colonies:fusion_subsystems/control_bearing');
});
