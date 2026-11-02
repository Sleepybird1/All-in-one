RecipeViewerEvents.removeEntries('item', event => {
  const owners = JsonIO.read('kubejs/config/industrial-resource-owners.json');
  owners.rules.forEach(rule => rule.alternatives.forEach(id => { if (Item.exists(id)) event.remove(id); }));
  owners.disabled.forEach(id => { if (Item.exists(id)) event.remove(id); });
});
