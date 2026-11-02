// Keep approved inventory art; render the actual cuboid assembly outside the GUI.
ClientEvents.generateAssets('last', event => {
  event.json('industrial_colonies:models/item/fusion_control_bearing.json', {"loader": "neoforge:separate_transforms", "base": {"parent": "industrial_colonies:item/fusion_subsystems/fusion_control_bearing_held"}, "perspectives": {"gui": {"parent": "minecraft:item/generated", "textures": {"layer0": "industrial_colonies:item/fusion_control_bearing_inventory"}}}});
});
