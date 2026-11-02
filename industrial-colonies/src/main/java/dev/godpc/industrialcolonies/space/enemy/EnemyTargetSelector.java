package dev.godpc.industrialcolonies.space.enemy;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import java.util.*;

/** Read-only explicit target allowlists. No automatic hostility inference.
 * Deep-space targets require the same complete native instance frame.
 * Selection is only a fresh identity observation, never firing permission. */
public final class EnemyTargetSelector {
 public record Selection(UUID source,UUID target,UUID authority,long tick,String dimension){}
 private EnemyTargetSelector(){}
 private static Set<UUID> owners(ServerSubLevel b){
  var owners=new HashSet<UUID>();int scanned=0;
  for(var holder:b.getPlot().getLoadedChunks())for(var actor:holder.getChunk().getBlockEntities().values()){
   if(++scanned>128)throw new IllegalStateException("Target owner scan budget");
   if(actor instanceof ShipTransponderBlockEntity t){
    if(t.isRemoved()||!b.getLevel().hasChunkAt(t.getBlockPos())||Sable.HELPER.getContaining(t)!=b)throw new IllegalStateException("Unavailable ownership");
    t.ownerId().ifPresent(owners::add);
   }
  }
  return owners;
 }
 /** NPC control must stop when a player claims any native transponder. */
 public static boolean mayControlSource(ServerSubLevel source,NativeEnemyHull hull){
  if(source==null||source.isRemoved()||!source.getLevel().getServer().isSameThread())return false;
  try{return source.getPlot().getLoadedChunks().iterator().hasNext()
      &&EnemyHullIdentity.mayControl(source,hull)&&owners(source).isEmpty();}
  catch(IllegalStateException invalid){return false;}
 }
 public static Optional<Selection> choose(ServerSubLevel source,NativeEnemyHull hull,ServerSubLevel target,
        Set<UUID> hostileNpcEncounters,Set<UUID> approvedPlayerOwners,Set<UUID> friendlyAuthorities){
  if(source==null||target==null||source==target||source.getLevel()!=target.getLevel()
    ||source.isRemoved()||target.isRemoved()||!source.getLevel().getServer().isSameThread()
    ||hostileNpcEncounters==null||approvedPlayerOwners==null||friendlyAuthorities==null)return Optional.empty();
  var level=source.getLevel();String dimension=level.dimension().location().toString();
  if(!EnemyNativeFrame.common(source,target))return Optional.empty();
  try{
   if(!dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle.of(target).isValid()
      ||!target.getPlot().getLoadedChunks().iterator().hasNext())return Optional.empty();
   if(!mayControlSource(source,hull)||EnemyCaptureHold.inhibits(target.getUserDataTag()))return Optional.empty();
   var own=EnemyHullIdentity.read(source);var targetOwners=owners(target);UUID authority;
   if(target.getUserDataTag()!=null&&target.getUserDataTag().contains(EnemyHullIdentity.KEY)){
    var npc=EnemyHullIdentity.read(target);
    if(!npc.originalBody()||!targetOwners.isEmpty()||npc.encounter().equals(own.encounter())
       ||!hostileNpcEncounters.contains(npc.encounter()))return Optional.empty();
    authority=npc.encounter();
   }else{
    if(targetOwners.size()!=1)return Optional.empty();authority=targetOwners.iterator().next();
    if(!approvedPlayerOwners.contains(authority))return Optional.empty();
   }
   if(friendlyAuthorities.contains(authority))return Optional.empty();
   return Optional.of(new Selection(source.getUniqueId(),target.getUniqueId(),authority,level.getGameTime(),dimension));
  }catch(IllegalStateException invalid){return Optional.empty();}
 }
}
