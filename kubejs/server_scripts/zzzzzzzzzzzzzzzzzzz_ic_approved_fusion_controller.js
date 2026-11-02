// priority: -96000
// User-approved bearing-to-controller recipe.
ServerEvents.recipes(event => {
 if(!Item.exists('industrial_colonies:fusion_control_bearing')) throw new Error('Fusion controller requires registered bearing.');
 event.remove({output:'industrial_colonies:fusion_control_unit'});
 event.recipes.create.sequenced_assembly(['industrial_colonies:fusion_control_unit'], 'industrial_colonies:fusion_control_bearing', [
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createmechanisms:computing_mechanism']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'extendedae:concurrent_processor']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'ae2:engineering_processor']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'simulated:optical_sensor']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:voltage_observer']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'electroenergetics:voltage_regulator']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'immersiveengineering:wire_electrum']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'tfmg:plastic_sheet']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:promethium_147_dust']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:caesium_137_dust']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:plate_elite']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'nuclearcraft:plate_elite']),
    event.recipes.industrial_colonies.refined_radiance_deploying('industrial_colonies:assembly_workpiece', ['industrial_colonies:assembly_workpiece', 'createmechanisms:computing_mechanism']),
    event.recipes.industrial_colonies.refined_radiance_pressing('industrial_colonies:assembly_workpiece', 'industrial_colonies:assembly_workpiece')
  ]).transitionalItem(Item.of('industrial_colonies:assembly_workpiece', {'minecraft:custom_data': {'industrial_colonies:workpiece_appearance': 'industrial_colonies:fusion_control_unit'}})).loops(1).group('Fusion subsystems / plasma control and interlocks').id('industrial_colonies:fusion_subsystems/control_unit');
});
