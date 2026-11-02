package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;

/** Read-only full plot/block-entity fingerprint for an immediate same-thread
 * comparison. Reads native saved data, not capabilities that may alias a dock peer.
 * Does not verify ownership, passengers, detached state or persisted body authority.
 */
public final class OrbitalBodyCustody {
 private OrbitalBodyCustody(){}
 /** Exact, separately domain-separated native user metadata, including unknown
  * fields. Null and empty remain distinct; no derived fields are omitted. */
 public static String metadataDigest(CompoundTag tag)throws IOException{
  try{
   var digest=MessageDigest.getInstance("SHA-256");
   try(var out=new DataOutputStream(new BoundedOutput(new DigestOutputStream(OutputStream.nullOutputStream(),digest)))){
    text(out,"IC_CAPTURE_EXACT_METADATA_V1");out.writeBoolean(tag!=null);if(tag!=null)canonical(out,tag,0);
   }
   return HexFormat.of().formatHex(digest.digest());
  }catch(NoSuchAlgorithmException ex){throw new AssertionError(ex);}
 }
 public record Snapshot(UUID body,String dimension,BlockPos minimum,BlockPos maximum,int blocks,int blockEntities,String digest){}
 public static Snapshot read(ServerSubLevel body)throws IOException{return read(body,65536);}
 public static Snapshot read(ServerSubLevel body,int blockBudget)throws IOException{return read(body,blockBudget,0);}
 /** Separate restart comparison: only the basic CAAL v1 transponder's verified
  * lastSeenGameTime heartbeat is omitted. Cargo, positions, owner, schedules,
  * controls and every other field remain exact. Unknown machine clocks still
  * cause mismatches. This never substitutes for the immediate transfer digest.
  */
 public static Snapshot readForRestart(ServerSubLevel body)throws IOException{return read(body,65536,1);}
 /** Frame recovery additionally verifies the basic transponder's cached physical
  * reference position against the live native controller, then omits that derived
  * cache from the digest. Native old/new pose and owner checks remain mandatory.
  * Root block coordinates and every non-derived saved field stay exact.
  */
 public static Snapshot readForEncounterRecovery(ServerSubLevel body)throws IOException{return read(body,65536,2);}
 /** Separate common-motion profile. Checks the native v1 forty-tick cache against
  * current controller position, exact elapsed game time and bounded zero-spin
  * translation before omitting it. Never used for stationary recovery. */
 public static Snapshot readForCommonMotionRecovery(ServerSubLevel body)throws IOException{return read(body,65536,3);}
 public static Snapshot readForDistinctCoastRecovery(ServerSubLevel body)throws IOException{return read(body,65536,4);}
 public static Snapshot readForPoweredUnloadRecovery(ServerSubLevel body)throws IOException{return read(body,65536,5);}
 private record CaptureOwner(BlockPos position,UUID transponder,Optional<UUID> owner,String name){}
 /** Immediate owner-setter comparison only. No cache omissions and no saved
  * restart interpretation; all other fields retain full immediate custody. */
 public static Snapshot readForCaptureOwnerChange(ServerSubLevel body,BlockPos position,UUID transponder,Optional<UUID> owner,String name)throws IOException{
  return read(body,65536,6,new CaptureOwner(Objects.requireNonNull(position).immutable(),Objects.requireNonNull(transponder),Objects.requireNonNull(owner),Objects.requireNonNull(name)));
 }
 private static Snapshot read(ServerSubLevel body,int blockBudget,int profile)throws IOException{
  return read(body,blockBudget,profile,null);
 }
 private static Snapshot read(ServerSubLevel body,int blockBudget,int profile,CaptureOwner capture)throws IOException{
  if(body==null||body.isRemoved()||blockBudget<1||blockBudget>65536)throw new IllegalArgumentException("Live body and bounded block budget required");
  var level=body.getLevel();if(!level.getServer().isSameThread())throw new IllegalStateException("Body custody requires server thread");
  var bounds=body.getPlot().getBoundingBox();if(bounds==null)throw new IllegalStateException("Missing plot bounds");
  long x=(long)bounds.maxX()-bounds.minX()+1,y=(long)bounds.maxY()-bounds.minY()+1,z=(long)bounds.maxZ()-bounds.minZ()+1;
  if(x<=0||y<=0||z<=0||x>256||y>256||z>256||x*y*z>blockBudget)throw new IllegalStateException("Body exceeds complete custody scan budget");
  for(int cx=bounds.minX()>>4;cx<=bounds.maxX()>>4;cx++)for(int cz=bounds.minZ()>>4;cz<=bounds.maxZ()>>4;cz++)
   if(!level.hasChunk(cx,cz))throw new IllegalStateException("Custody plot chunk not loaded");
  var minimum=new BlockPos(bounds.minX(),bounds.minY(),bounds.minZ());var maximum=new BlockPos(bounds.maxX(),bounds.maxY(),bounds.maxZ());
  MessageDigest digest;try{digest=MessageDigest.getInstance("SHA-256");}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
  int blocks=0,entities=0,captureMatches=0;
  try(var out=new DataOutputStream(new BoundedOutput(new DigestOutputStream(OutputStream.nullOutputStream(),digest)))){
   text(out,profile==6?"IC_BODY_CAPTURE_OWNER_COMPARISON_V1":profile==5?"IC_BODY_POWERED_UNLOAD_RECOVERY_V1":profile==4?"IC_BODY_DISTINCT_COAST_RECOVERY_V1":profile==3?"IC_BODY_COMMON_MOTION_RECOVERY_V1":profile==2?"IC_BODY_ENCOUNTER_RECOVERY_V1":profile==1?"IC_BODY_RESTART_CUSTODY_V1":"IC_FULL_BODY_CUSTODY_V1");text(out,body.getUniqueId().toString());text(out,level.dimension().location().toString());
   for(var pos:BlockPos.betweenClosed(minimum,maximum)){
    var state=level.getBlockState(pos);out.writeInt(pos.getX());out.writeInt(pos.getY());out.writeInt(pos.getZ());canonical(out,NbtUtils.writeBlockState(state),0);
    if(!state.isAir())blocks++;
    var be=level.getBlockEntity(pos);out.writeBoolean(be!=null);
    if(state.hasBlockEntity()&&be==null)throw new IllegalStateException("Expected block entity missing from custody scan");
    if(be!=null){
     if(be.isRemoved()||Sable.HELPER.getContaining(be)!=body)throw new IllegalStateException("Block entity body authority disagrees");
     var saved=be.saveWithFullMetadata(level.registryAccess());
     if(profile==6&&pos.equals(capture.position())){
      if(be.getClass()!=net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity.class)throw new IOException("Exact basic capture transponder required");
      var transponder=(net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity)be;
      if(!transponder.transponderId().equals(capture.transponder())||!transponder.ownerId().equals(capture.owner())||!transponder.ownerName().equals(capture.name()))throw new IOException("Live capture owner comparison mismatch");
      saved=dev.godpc.industrialcolonies.space.enemy.CaptureOwnerNbt.comparisonCopy(saved,capture.transponder(),capture.owner(),capture.name());captureMatches++;
     }
     if(profile>0&&profile<6&&saved.getString("id").equals("create_aeronautics_automated_logistics:ship_transponder")){
      if(!(be instanceof net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity)
        ||saved.getInt("dataVersion")!=1||!saved.contains("lastSeenGameTime",Tag.TAG_LONG)
        ||saved.getLong("lastSeenGameTime")<0||saved.getLong("lastSeenGameTime")>level.getGameTime())throw new IOException("Unsupported transponder heartbeat schema");
      // saveWithFullMetadata returns new NBT; never edit the live machine.
      long seen=saved.getLong("lastSeenGameTime");saved.remove("lastSeenGameTime");
      if(profile>=2){
       for(String key:List.of("lastKnownX","lastKnownY","lastKnownZ"))if(!saved.contains(key,Tag.TAG_DOUBLE)||!Double.isFinite(saved.getDouble(key)))throw new IOException("Unsupported transponder position cache");
       var controller=net.sprocketgames.create_aeronautics_automated_logistics.vehicle.SableSubLevelVehicleController.resolveControllerBlock(level,body.getUniqueId(),pos).orElseThrow(()->new IOException("Live native controller reference unavailable"));
       var p=controller.position();double dx=p.x-saved.getDouble("lastKnownX"),dy=p.y-saved.getDouble("lastKnownY"),dz=p.z-saved.getDouble("lastKnownZ");
       if(profile==4){
        var handle=dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle.of(body);var velocity=handle.getLinearVelocity();var origin=body.logicalPose().position();
        if(handle.getAngularVelocity().length()!=0||body.latestLinearVelocity.distance(velocity)>1e-3)throw new IOException("Unqualified distinct-coast cache motion");
        try{OrbitalDistinctCoastProof.requireCurrentCache(new RendezvousGuidance.V(p.x,p.y,p.z),new RendezvousGuidance.V(saved.getDouble("lastKnownX"),saved.getDouble("lastKnownY"),saved.getDouble("lastKnownZ")),new RendezvousGuidance.V(origin.x(),origin.y(),origin.z()),new RendezvousGuidance.V(velocity.x(),velocity.y(),velocity.z()),level.getGameTime(),seen);}
        catch(IllegalArgumentException|IllegalStateException invalid){throw new IOException("Native slow-motion transponder cache is not current",invalid);}
       }else if(profile==3){
        var handle=dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle.of(body);var velocity=handle.getLinearVelocity();
        if(handle.getAngularVelocity().length()!=0||body.latestLinearVelocity.distance(velocity)>1e-3)throw new IOException("Unqualified rotating or unresolved cache motion");
        try{OrbitalCommonMotionProof.requireCurrentCache(new RendezvousGuidance.V(p.x,p.y,p.z),new RendezvousGuidance.V(saved.getDouble("lastKnownX"),saved.getDouble("lastKnownY"),saved.getDouble("lastKnownZ")),new RendezvousGuidance.V(velocity.x(),velocity.y(),velocity.z()),level.getGameTime(),seen);}
        catch(IllegalArgumentException invalid){throw new IOException("Native moving transponder cache is not current",invalid);}
       }else if(!Double.isFinite(dx*dx+dy*dy+dz*dz)||dx*dx+dy*dy+dz*dz>1e-6)throw new IOException("Native transponder position cache is not current");
       saved.remove("lastKnownX");saved.remove("lastKnownY");saved.remove("lastKnownZ");
      }
     }
     if(profile==5&&saved.getString("id").equals("create:mechanical_pump")){
      if(be.getClass()!=com.simibubi.create.content.fluids.pump.PumpBlockEntity.class)throw new IOException("Exact native Create pump required");
      FreightPumpFlowSample.normalize(saved);
     }
     canonical(out,saved,0);entities++;
    }
   }
  }
  if(profile==6&&captureMatches!=1)throw new IOException("Capture transponder missing from full body scan");
  if(body.isRemoved()||!minimum.equals(new BlockPos(body.getPlot().getBoundingBox().minX(),body.getPlot().getBoundingBox().minY(),body.getPlot().getBoundingBox().minZ()))||!maximum.equals(new BlockPos(body.getPlot().getBoundingBox().maxX(),body.getPlot().getBoundingBox().maxY(),body.getPlot().getBoundingBox().maxZ())))throw new IllegalStateException("Body changed during custody scan");
  return new Snapshot(body.getUniqueId(),level.dimension().location().toString(),minimum,maximum,blocks,entities,HexFormat.of().formatHex(digest.digest()));
 }
 private static void canonical(DataOutputStream out,Tag value,int depth)throws IOException{
  if(value==null||depth>64)throw new IOException("Invalid or excessively nested native data");out.writeByte(value.getId());
  if(value instanceof CompoundTag tag){var keys=tag.getAllKeys().stream().sorted().toList();out.writeInt(keys.size());for(String key:keys){text(out,key);canonical(out,tag.get(key),depth+1);}}
  else if(value instanceof ListTag list){out.writeInt(list.size());for(Tag child:list)canonical(out,child,depth+1);}
  else text(out,value.toString());
 }
 private static void text(DataOutputStream out,String value)throws IOException{byte[] bytes=value.getBytes(StandardCharsets.UTF_8);out.writeInt(bytes.length);out.write(bytes);}
 private static final class BoundedOutput extends FilterOutputStream{
  int bytes;BoundedOutput(OutputStream delegate){super(delegate);}
  void reserve(int count)throws IOException{if(count<0||count>8*1024*1024-bytes)throw new IOException("Native custody data budget exceeded");bytes+=count;}
  @Override public void write(int value)throws IOException{reserve(1);out.write(value);}
  @Override public void write(byte[] value,int offset,int length)throws IOException{reserve(length);out.write(value,offset,length);}
 }
}
