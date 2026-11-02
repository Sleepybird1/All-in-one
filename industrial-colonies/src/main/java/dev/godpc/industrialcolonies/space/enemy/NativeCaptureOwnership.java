package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.OrbitalBodyCustody;
import dev.godpc.industrialcolonies.space.SableStoredBodyAudit;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.*;
import java.io.IOException;
import java.util.*;

/** Read-only identity agreement for a captured original body. No ownership
 * writes, registry refresh, save flush, control or transfer authority. Caller
 * supplies the server's already loaded authoritative identity directory.
 * Saved identity agreement is not a saved cargo-conservation proof. */
public final class NativeCaptureOwnership {
 public record Snapshot(UUID body,UUID transponder,UUID claimant,Optional<UUID> owner,
                        BlockPos position,String dimension,String storedRecord,String custodyDigest){}
 public record LiveSnapshot(UUID body,UUID transponder,UUID claimant,Optional<UUID> owner,
                            BlockPos position,String dimension,String custodyDigest){}
 private NativeCaptureOwnership(){}
 private static void require(boolean value,String reason)throws IOException{if(!value)throw new IOException(reason);}
 public static Snapshot read(ServerSubLevel body,UUID transponder,UUID claimant,Optional<UUID> expectedOwner,
                             IdentityDirectorySavedData directory)throws IOException{
  return read(body,transponder,claimant,expectedOwner,directory,true);
 }
 /** Live-only view after native registry refresh. Does not certify disk ownership. */
 public static LiveSnapshot readLive(ServerSubLevel body,UUID transponder,UUID claimant,Optional<UUID> expectedOwner,
                                    IdentityDirectorySavedData directory)throws IOException{
  var v=read(body,transponder,claimant,expectedOwner,directory,false);
  return new LiveSnapshot(v.body(),v.transponder(),v.claimant(),v.owner(),v.position(),v.dimension(),v.custodyDigest());
 }
 private static Snapshot read(ServerSubLevel body,UUID transponder,UUID claimant,Optional<UUID> expectedOwner,
                              IdentityDirectorySavedData directory,boolean inspectStorage)throws IOException{
  Objects.requireNonNull(body);Objects.requireNonNull(transponder);Objects.requireNonNull(claimant);
  Objects.requireNonNull(expectedOwner);Objects.requireNonNull(directory);
  require(expectedOwner.isEmpty()||expectedOwner.equals(Optional.of(claimant)),"Foreign capture owner refused");
  var identity=EnemyHullIdentity.read(body);require(identity.originalBody(),"Original captured body required");
  var metadata=body.getUserDataTag().copy();require(metadata.contains(EnemyCaptureHold.KEY,10),"Native capture hold required");
  var hold=EnemyCaptureHold.decode(metadata.getCompound(EnemyCaptureHold.KEY));
  require(hold.encounter().equals(identity.encounter())&&hold.root().equals(identity.root())
      &&hold.claimant().equals(claimant),"Capture hold identity mismatch");
  // Pre-transfer custody belongs to the separate held-journal audit. This
  // observer intentionally permits the expected owner field to have changed.
  var custody=OrbitalBodyCustody.read(body);var attachments=EnemyMountedCannonCustody.readHeld(body);
  var level=body.getLevel();var server=level.getServer();long tick=level.getGameTime();
  require(server.isSameThread(),"Capture ownership requires server thread");
  int bodies=0,machines=0,current=0,matches=0,localTransponders=0;ShipTransponderBlockEntity found=null;
  for(var world:server.getAllLevels()){
   var container=SubLevelContainer.getContainer(world);if(container==null)continue;
   for(var candidate:container.getAllSubLevels()){
    if(candidate.isRemoved())continue;require(++bodies<=4096,"Capture body scan budget exceeded");
    if(candidate.getUniqueId().equals(body.getUniqueId())){current++;require(candidate==body&&world==level,"Conflicting loaded capture body");}
    for(var holder:candidate.getPlot().getLoadedChunks())for(var be:holder.getChunk().getBlockEntities().values()){
     require(++machines<=65536,"Capture machine scan budget exceeded");
     if(be instanceof ShipTransponderBlockEntity t){
      if(candidate==body)localTransponders++;
      if(t.transponderId().equals(transponder)){
       matches++;require(candidate==body&&!t.isRemoved()&&t.getClass()==ShipTransponderBlockEntity.class
           &&level.hasChunkAt(t.getBlockPos())&&Sable.HELPER.getContaining(t)==body,"Capture transponder not uniquely on original body");found=t;
      }
     }
    }
   }
  }
  require(current==1&&matches==1&&localTransponders==1&&found!=null,"Exactly one capture body/transponder required");
  require(found.ownerId().equals(expectedOwner)&&found.runtimeShipId().equals(Optional.of(body.getUniqueId())),"Live capture owner/body mismatch");
  var registry=ShipTransponderRegistry.snapshot(transponder).orElseThrow(()->new IOException("Capture registry absent"));
  require(registry.ownerId().equals(expectedOwner)&&registry.runtimeShipId().equals(Optional.of(body.getUniqueId()))
      &&registry.dimension().equals(level.dimension())&&registry.transponderPos().equals(found.getBlockPos()),"Capture registry disagrees");
  var persisted=directory.ship(transponder).orElseThrow(()->new IOException("Capture directory absent"));
  require(persisted.ownerId().equals(expectedOwner)&&persisted.dimension().equals(level.dimension())
      &&persisted.transponderPos().equals(found.getBlockPos()),"Capture directory disagrees");
  String storedRecord="NOT_AUDITED";
  if(inspectStorage){
  var storage=SableStoredBodyAudit.inspect(server);
  var records=storage.bodies().stream().filter(b->b.id().equals(body.getUniqueId())).toList();
  require(records.size()==1&&records.getFirst().referenced()&&records.getFirst().dimension().equals(custody.dimension()),"Unique referenced saved capture body required");
  var identities=storage.bodies().stream().filter(b->b.transponders().containsKey(transponder)).toList();
  require(identities.size()==1&&identities.getFirst().equals(records.getFirst())&&records.getFirst().transponders().size()==1
      &&expectedOwner.equals(records.getFirst().transponders().get(transponder)),"Saved capture owner/transponder mismatch");
  storedRecord=records.getFirst().record();
  }
  require(level.getGameTime()==tick&&custody.equals(OrbitalBodyCustody.read(body))
      &&attachments.equals(EnemyMountedCannonCustody.readHeld(body))&&metadata.equals(body.getUserDataTag())
      &&registry.equals(ShipTransponderRegistry.snapshot(transponder).orElse(null))
      &&persisted.equals(directory.ship(transponder).orElse(null)),"Capture ownership observation changed");
  return new Snapshot(body.getUniqueId(),transponder,claimant,expectedOwner,found.getBlockPos().immutable(),custody.dimension(),storedRecord,custody.digest());
 }
}
