RecipeViewerEvents.removeEntries('item', event => {
  if (Item.exists("createreautomated:infinite_copper_node")) event.remove("createreautomated:infinite_copper_node");
  if (Item.exists("createreautomated:infinite_iron_node")) event.remove("createreautomated:infinite_iron_node");
  if (Item.exists("createreautomated:infinite_gold_node")) event.remove("createreautomated:infinite_gold_node");
  if (Item.exists("createreautomated:infinite_zinc_node")) event.remove("createreautomated:infinite_zinc_node");
  if (Item.exists("createreautomated:infinite_diamond_node")) event.remove("createreautomated:infinite_diamond_node");
  if (Item.exists("createreautomated:infinite_quartz_node")) event.remove("createreautomated:infinite_quartz_node");
});
