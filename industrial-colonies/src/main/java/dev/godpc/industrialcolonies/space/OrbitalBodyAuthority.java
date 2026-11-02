package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import java.io.IOException;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.ShipTransponderRegistry;

/** Conservative live/registry/stored identity agreement. Does not flush saves,
 * infer cargo from a saved record, or authorize motion. Unsaved new ships wait.
 */
public final class OrbitalBodyAuthority {
 private OrbitalBodyAuthority(){}
 public record Snapshot(UUID body,UUID transponder,UUID owner,BlockPos transponderPosition,String dimension,String storedRecord){}
 private static void require(boolean value,String reason){if(!value)throw new IllegalStateException(reason);}
 public static Snapshot read(ServerSubLevel body,UUID transponder,UUID owner,UUID retiredBody)throws IOException{
  Objects.requireNonNull(transponder);Objects.requireNonNull(owner);Objects.requireNonNull(retiredBody);
  var custody=OrbitalBodyCustody.read(body);var level=body.getLevel();var server=level.getServer();
  require(!body.getUniqueId().equals(retiredBody),"Retired source cannot be the current body");
  int scannedBodies=0,scannedMachines=0,matches=0,currentBodies=0;ShipTransponderBlockEntity found=null;
  for(var world:server.getAllLevels()){
   var container=SubLevelContainer.getContainer(world);if(container==null)continue;
   for(var candidate:container.getAllSubLevels()){
    if(candidate.isRemoved())continue;require(++scannedBodies<=4096,"Loaded body authority scan budget exceeded");
    require(!candidate.getUniqueId().equals(retiredBody),"Retired source remains loaded");
    if(candidate.getUniqueId().equals(body.getUniqueId())){currentBodies++;require(candidate==body&&world==level,"Conflicting loaded body authority");}
    for(var holder:candidate.getPlot().getLoadedChunks())for(var be:holder.getChunk().getBlockEntities().values()){
     require(++scannedMachines<=65536,"Loaded machine authority scan budget exceeded");
     if(be instanceof ShipTransponderBlockEntity t&&!t.isRemoved()&&t.transponderId().equals(transponder)){
      matches++;require(candidate==body&&Sable.HELPER.getContaining(t)==body,"Transponder exists on another loaded body");found=t;
     }
    }
   }
  }
  require(currentBodies==1&&matches==1&&found!=null,"Exactly one loaded body and transponder required");
  require(found.ownerId().equals(Optional.of(owner))&&found.runtimeShipId().equals(Optional.of(body.getUniqueId())),"Live transponder owner or body disagrees");
  var registry=ShipTransponderRegistry.snapshot(transponder).orElseThrow(()->new IllegalStateException("Native transponder registry missing"));
  require(registry.ownerId().equals(Optional.of(owner))&&registry.runtimeShipId().equals(Optional.of(body.getUniqueId()))
    &&registry.dimension().equals(level.dimension())&&registry.transponderPos().equals(found.getBlockPos()),"Native registry identity disagrees");
  var audit=SableStoredBodyAudit.inspect(server);var records=audit.bodies().stream().filter(b->b.id().equals(body.getUniqueId())).toList();
  require(audit.bodies().stream().noneMatch(b->b.id().equals(retiredBody)),"Retired source remains in native storage");
  require(records.size()==1&&records.getFirst().referenced()&&records.getFirst().dimension().equals(custody.dimension()),"Exactly one referenced stored body authority required");
  var identities=audit.bodies().stream().filter(b->b.transponders().containsKey(transponder)).toList();
  require(identities.size()==1&&identities.getFirst().id().equals(body.getUniqueId())
    &&identities.getFirst().transponders().get(transponder).equals(Optional.of(owner)),"Stored transponder owner or body disagrees");
  require(custody.equals(OrbitalBodyCustody.read(body)),"Body changed during authority audit");
  return new Snapshot(body.getUniqueId(),transponder,owner,found.getBlockPos().immutable(),custody.dimension(),records.getFirst().record());
 }
}
