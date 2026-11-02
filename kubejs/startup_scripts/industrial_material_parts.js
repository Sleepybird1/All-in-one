// Generated, fixed registry manifest. Requires a normal full client restart.
const IC_PARTS_STARTUP = JsonIO.read('kubejs/config/industrial-material-parts.json');
StartupEvents.registry('item', event => {
  IC_PARTS_STARTUP.items.forEach(part => {
    event.create(part.canonical).displayName(part.displayName)
      .texture(part.texture).color(0, part.color)
      .tag('c:' + (part.form === 'gear' ? 'gears' : part.form === 'rod' ? 'rods' : part.form === 'sheet' ? 'sheets' : part.form === 'dust' ? 'dusts' : 'plates'))
      .tag('c:' + (part.form === 'gear' ? 'gears' : part.form === 'rod' ? 'rods' : part.form === 'sheet' ? 'sheets' : part.form === 'dust' ? 'dusts' : 'plates') + '/' + part.material);
  });
  // Keep legacy stack IDs readable after retiring the mod; no acquisition tags.
  IC_PARTS_STARTUP.compatibility.forEach(part => {
    event.create(part.id).displayName(part.displayName).texture(part.texture).color(0,part.color);
  });
});
StartupEvents.modifyCreativeTab('kubejs:tab', event => {
  IC_PARTS_STARTUP.compatibility.forEach(part => event.remove(part.id));
});
