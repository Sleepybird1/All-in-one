package dev.godpc.industrialcolonies.geology;

import net.minecraft.server.level.ServerLevel;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.level.LevelEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;

/** Separately scoped structure lifecycle; no replacement of the installed geology bootstrap needed. */
@EventBusSubscriber(modid="industrial_colonies")
public final class WorldStartStructureHooks {
 private WorldStartStructureHooks(){}
 @SubscribeEvent public static void load(LevelEvent.Load event){
  if(event.getLevel() instanceof ServerLevel level){WorldStartStructureSpacing.load(level);LightningDragonNativeGate.load(level);}
 }
 @SubscribeEvent public static void unload(LevelEvent.Unload event){
  if(event.getLevel() instanceof ServerLevel level){WorldStartStructureSpacing.unload(level);LightningDragonNativeGate.unload(level);}
 }
 @SubscribeEvent public static void stopped(ServerStoppedEvent event){WorldStartStructureSpacing.clear();LightningDragonNativeGate.clear();}
}
