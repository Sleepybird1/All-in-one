// priority: -22000
ServerEvents.recipes(event => {
  if (Item.exists("createreautomated:infinite_copper_node")) event.remove({output: "createreautomated:infinite_copper_node"});
  if (Item.exists("createreautomated:infinite_iron_node")) event.remove({output: "createreautomated:infinite_iron_node"});
  if (Item.exists("createreautomated:infinite_gold_node")) event.remove({output: "createreautomated:infinite_gold_node"});
  if (Item.exists("createreautomated:infinite_zinc_node")) event.remove({output: "createreautomated:infinite_zinc_node"});
  if (Item.exists("createreautomated:infinite_diamond_node")) event.remove({output: "createreautomated:infinite_diamond_node"});
  if (Item.exists("createreautomated:infinite_quartz_node")) event.remove({output: "createreautomated:infinite_quartz_node"});
});
