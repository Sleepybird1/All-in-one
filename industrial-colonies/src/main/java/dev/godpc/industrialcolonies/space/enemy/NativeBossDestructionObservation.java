package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.*;

/** Package-private native hull-cell witness. Air alone cannot create it: an
 * intact commissioned cell must be observed before the synchronous callback.
 * Does not prove drops, mounted contents, journal durability or whole-body loss. */
final class NativeBossDestructionObservation {
 private final ServerLevel level;
 private final ServerSubLevel body;
 private final EnemyBossModules baseline;
 private final UUID encounter,root;
 private final String name;
 private final EnemyBossModules.Location location;
 private final BlockPos position;
 private final long tick;
 NativeBossDestructionObservation(ServerLevel level,Map<UUID,ServerSubLevel> bodies,
     EnemyBossModules baseline,UUID encounter,UUID root,String name){
  this.level=level;this.baseline=baseline;this.encounter=encounter;this.root=root;this.name=name;
  var module=baseline.modules().get(name);
  if(!level.getServer().isSameThread()||!baseline.belongsTo(encounter,root)||module==null||module.destroyed())
   throw new IllegalStateException("Intact commissioned module required");
  location=module.location();body=bodies.get(location.body());position=new BlockPos(location.x(),location.y(),location.z());tick=level.getGameTime();
  if(body==null||body.isRemoved()||body.getLevel()!=level||!level.hasChunkAt(position)
      ||Sable.HELPER.getContaining(level,position)!=body||level.getBlockState(position).isAir())
   throw new IllegalStateException("Native source cell unavailable");
  if(level.getBlockState(position).hasBlockEntity()){
   var be=level.getBlockEntity(position);
   if(be==null||be.isRemoved()||Sable.HELPER.getContaining(be)!=body)
    throw new IllegalStateException("Native source machine unavailable");
  }
 }
 EnemyBossModules after(boolean nativeReturn,boolean sameTick){
  if(!level.getServer().isSameThread()||!nativeReturn||!sameTick||level.getGameTime()!=tick
      ||body.isRemoved()||body.getLevel()!=level||!level.hasChunkAt(position)
      ||Sable.HELPER.getContaining(level,position)!=body||!level.getBlockState(position).isAir()
      ||level.getBlockEntity(position)!=null)throw new IllegalStateException("Native destruction unproven");
  return baseline.apply(encounter,root,baseline.revision(),List.of(new EnemyBossModules.Change(name,location,null)));
 }
}
