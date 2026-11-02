// Inventory-only preview skin for the temporary recipe output; ordinary Diorite is unchanged.
ClientEvents.generateAssets('last',event=>{event.json('minecraft:models/item/diorite.json',{"parent": "minecraft:block/diorite", "overrides": [{"predicate": {"custom_model_data": 1054301}, "model": "industrial_colonies:item/fusion_control_bearing_inventory"}]});});
