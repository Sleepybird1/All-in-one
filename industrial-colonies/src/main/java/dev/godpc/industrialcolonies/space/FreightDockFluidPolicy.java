package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;

/** Read-only permission boundary; never changes tanks, snapshots or kinetic power. */
public final class FreightDockFluidPolicy {
 private FreightDockFluidPolicy(){}
 private static boolean endpoint(BlockEntity dock,boolean items){
  if(dock==null||dock.isRemoved()||!(dock.getLevel() instanceof ServerLevel level)
    ||!level.getServer().isSameThread()||!level.hasChunkAt(dock.getBlockPos())||level.getBlockEntity(dock.getBlockPos())!=dock)return false;
  var journal=FreightJourneyControl.journal(level.getServer());
  if(!journal.fault().isEmpty())return false;
  var body=Sable.HELPER.getContaining(dock);
  return !(body instanceof ServerSubLevel ship)||
    ((items?journal.nativeItemTransferAllowed(ship.getUniqueId()):journal.nativeFluidTransferAllowed(ship.getUniqueId()))&&!SpaceflightAuthorization.automationDisabled(ship));
 }
 public static boolean allowed(BlockEntity dock){
  return allowed(dock,false);
 }
 public static boolean itemsAllowed(BlockEntity dock){return allowed(dock,true);}
 private static boolean allowed(BlockEntity dock,boolean items){
  if(!endpoint(dock,items))return false;
  try{
   // Native insert targets the peer, while extract uses this tank. Check both
   // endpoints so a powered receiver cannot drain a held cargo ship indirectly.
   Object peer=dock.getClass().getMethod("getOtherConnector").invoke(dock);
   return peer==null||(peer instanceof BlockEntity other&&other.getLevel()==dock.getLevel()&&endpoint(other,items));
  }catch(ReflectiveOperationException|ClassCastException failure){return false;}
 }
}
