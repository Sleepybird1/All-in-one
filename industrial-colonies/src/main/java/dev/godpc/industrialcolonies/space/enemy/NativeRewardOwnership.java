package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.OrbitalBodyCustody;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import net.minecraft.server.level.ServerLevel;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import java.io.IOException;
import java.util.*;

/** Live-lineage-issued exclusion evidence only, never proof of defeat or loot.
 * Rejects current player owners and capture markers on original and tracked
 * fragments. Historical manual ownership after removal is not established.
 * All cargo/configuration is reread in the same tick before token consumption. */
public final class NativeRewardOwnership {
 private record Body(String metadata,OrbitalBodyCustody.Snapshot cargo,EnemyMountedCannonCustody.Snapshot guns){}
 private final NativeBossLineage lineage;
 private final EnemyBossModules modules;
 private final ServerLevel level;
 private final UUID encounter,root;
 private final long tick;
 private final Map<UUID,ServerSubLevel> bodies;
 private final Map<UUID,Body> baseline;
 private boolean consumed;
 NativeRewardOwnership(NativeBossLineage lineage,EnemyBossModules modules,ServerLevel level,UUID encounter,UUID root,Map<UUID,ServerSubLevel> bodies)throws IOException{
  this.lineage=lineage;this.modules=modules;this.level=level;this.encounter=encounter;this.root=root;this.bodies=Map.copyOf(bodies);tick=level.getGameTime();baseline=read();
 }
 private static void require(boolean ok,String why)throws IOException{if(!ok)throw new IOException(why);}
 private Map<UUID,Body> read()throws IOException{
  require(level.getServer().isSameThread()&&level.getGameTime()==tick&&lineage.rewardScope(modules,bodies)
      &&!bodies.isEmpty()&&bodies.size()<=128&&bodies.containsKey(root),"Current complete live lineage required");
  var identity=EnemyHullIdentity.read(bodies.get(root));require(identity.originalBody()&&identity.encounter().equals(encounter)&&identity.root().equals(root),"Original reward root changed");
  var loaded=new HashSet<UUID>();int scanned=0;
  for(var world:level.getServer().getAllLevels()){
   var container=SubLevelContainer.getContainer(world);if(container==null)continue;
   for(var body:container.getAllSubLevels()){
    require(++scanned<=4096,"Reward body census exceeded");
    if(bodies.containsKey(body.getUniqueId()))require(bodies.get(body.getUniqueId())==body&&world==level&&!body.isRemoved()&&loaded.add(body.getUniqueId()),"Replaced or duplicate reward body");
    var tag=body.getUserDataTag();
    if(tag!=null&&tag.contains(EnemyHullIdentity.KEY)){
     var id=EnemyHullIdentity.read(body);
     if(id.root().equals(root)||id.encounter().equals(encounter))require(bodies.get(body.getUniqueId())==body,"Untracked reward lineage body");
    }
   }
  }
  require(loaded.equals(bodies.keySet()),"Unloaded reward lineage member");
  var result=new HashMap<UUID,Body>();var transponders=new HashSet<UUID>();int machines=0;
  for(var entry:bodies.entrySet()){
   var body=entry.getValue();require(!EnemyCaptureHold.inhibits(body.getUserDataTag()),"Captured body cannot earn destruction reward");
   var before=OrbitalBodyCustody.read(body);var metadata=OrbitalBodyCustody.metadataDigest(body.getUserDataTag());
   for(var holder:body.getPlot().getLoadedChunks())for(var be:holder.getChunk().getBlockEntities().values()){
    require(++machines<=65536,"Reward machine census exceeded");
    if(be instanceof ShipTransponderBlockEntity transponder){
     require(be.getClass()==ShipTransponderBlockEntity.class&&!be.isRemoved()&&Sable.HELPER.getContaining(be)==body
         &&level.hasChunkAt(be.getBlockPos())&&transponder.ownerId().isEmpty()
         &&transponder.runtimeShipId().equals(Optional.of(body.getUniqueId()))&&transponders.add(transponder.transponderId()),"Owned, unknown or duplicated reward transponder");
     CaptureOwnerNbt.comparisonCopy(be.saveWithFullMetadata(level.registryAccess()),transponder.transponderId(),Optional.empty(),transponder.ownerName());
    }
   }
   var guns=EnemyMountedCannonCustody.readHeld(body);
   require(before.equals(OrbitalBodyCustody.read(body))&&metadata.equals(OrbitalBodyCustody.metadataDigest(body.getUserDataTag())),"Reward body changed during ownership census");
   result.put(entry.getKey(),new Body(metadata,before,guns));
  }
  return Map.copyOf(result);
 }
 /** This token does not validate the supplied destruction digest. The future
  * native defeat adapter must separately establish that evidence. */
 public synchronized void consume(EnemyRewardAdmission.Evidence evidence)throws IOException{
  require(!consumed,"Reward ownership observation consumed");consumed=true;
  require(evidence!=null&&encounter.equals(evidence.encounter())&&root.equals(evidence.root())
      &&modules.modules().keySet().equals(evidence.commissioned())
      &&root.equals(evidence.currentOwner())&&evidence.now()==tick&&evidence.observationTick()==tick
      &&baseline.equals(read()),"Reward ownership/custody scope changed");
 }
 public synchronized void recheck()throws IOException{
  require(consumed&&baseline.equals(read()),"Reserved reward ownership/custody changed");
 }
}
