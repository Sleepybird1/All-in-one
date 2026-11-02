// Existing reused dust items also need a material tint for the neutral gunpowder sprite.
if(Platform.isClientEnvironment()) {
  NativeEvents.onEvent(Java.loadClass('net.neoforged.neoforge.client.event.RegisterColorHandlersEvent$Item'), event=>{
    var manifest=JsonIO.read('kubejs/config/industrial-material-parts.json');
    var seen={};
    manifest.parts.forEach(part=>{
      if(part.form!=='dust'||seen[part.canonical]||!Item.exists(part.canonical))return;
      seen[part.canonical]=true;
      var rgb=parseInt(part.color.substring(1),16);
      event.register((stack,index)=>index===0?rgb:-1, Item.of(part.canonical).item);
    });
  });
}
