package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.OrbitalBodyCustody;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import java.io.*;
import java.security.*;
import java.util.*;

/** Native journal binding using the existing complete held custody profiles.
 * No new NBT omissions, body reconstruction, actuator acquisition or pose writes.
 * A matching digest does not establish crash atomicity or authorize resuming. */
public final class EnemyEncounterCustody {
 public enum Role { SOURCE,TARGET }
 public record Snapshot(UUID body,UUID encounter,UUID root,EnemyNativeFrame.Key frame,
                        int bodyBlocks,int cannonBlocks,String digest){}
 private EnemyEncounterCustody(){}
 /** Explicit native metadata re-query, not a read-only audit or direct cache edit.
  * Only known derived XYZ/heartbeat changes are permitted. Physical pose,
  * velocities, NPC tags and every other transponder field must stay unchanged. */
 public static int refreshNativeCaches(ServerSubLevel body)throws IOException {
  var identity=EnemyHullIdentity.read(body);if(!identity.originalBody())throw new IOException("Original native body required before cache refresh");
  var level=body.getLevel();var tag=body.getUserDataTag().copy();var pose=new org.joml.Vector3d(body.logicalPose().position());var rotation=new org.joml.Quaterniond(body.logicalPose().orientation());
  var handle=dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle.of(body);var linear=new org.joml.Vector3d(handle.getLinearVelocity());var angular=new org.joml.Vector3d(handle.getAngularVelocity());int scanned=0,count=0;
  for(var holder:body.getPlot().getLoadedChunks())for(var actor:holder.getChunk().getBlockEntities().values()){
   if(++scanned>128)throw new IOException("Native refresh census exceeded authority budget");
   if(actor instanceof net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity transponder){
    if(actor.getClass()!=net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity.class||actor.isRemoved()||Sable.HELPER.getContaining(actor)!=body)throw new IOException("Native transponder authority unavailable");
    var before=actor.saveWithFullMetadata(level.registryAccess());if(before.getInt("dataVersion")!=1)throw new IOException("Unsupported native cache refresh schema");
    transponder.refreshRuntimeShip(level);var after=actor.saveWithFullMetadata(level.registryAccess());
    for(String key:List.of("lastSeenGameTime","lastKnownX","lastKnownY","lastKnownZ")){before.remove(key);after.remove(key);}
    if(!before.equals(after))throw new IOException("Native refresh changed non-derived transponder configuration");count++;
   }
  }
  if(!tag.equals(body.getUserDataTag())||!pose.equals(new org.joml.Vector3d(body.logicalPose().position()))||!rotation.equals(new org.joml.Quaterniond(body.logicalPose().orientation()))||!linear.equals(new org.joml.Vector3d(handle.getLinearVelocity()))||!angular.equals(new org.joml.Vector3d(handle.getAngularVelocity())))throw new IOException("Native cache refresh changed physical state or NPC metadata");
  return count;
 }
 public static EnemyEncounterJournal.Plan observePlan(UUID session,ServerSubLevel source,ServerSubLevel target,BlockPos mount)throws IOException {
  if(source==null||target==null||mount==null||source==target||!EnemyNativeFrame.common(source,target))throw new IOException("Complete common native frame required");
  var a=EnemyHullIdentity.read(source);var b=EnemyHullIdentity.read(target);
  if(!a.originalBody()||!b.originalBody()||Sable.HELPER.getContaining(source.getLevel(),mount)!=source
      ||EnemyMountedCannonCustody.readHeld(source).attachments().stream().noneMatch(row->row.mount().equals(mount)))throw new IOException("Original identities and reciprocal disarmed native mount required");
  return new EnemyEncounterJournal.Plan(session,source.getUniqueId(),a.encounter(),a.root(),target.getUniqueId(),b.encounter(),b.root(),source.getLevel().dimension().location().toString(),mount.getX(),mount.getY(),mount.getZ());
 }
 public static Snapshot captureHeld(ServerSubLevel body,Role role)throws IOException {
  Objects.requireNonNull(role);var identity=EnemyHullIdentity.read(body);if(!identity.originalBody())throw new IOException("Copied native NPC identity refused");
  var frame=EnemyNativeFrame.read(body).orElseThrow(()->new IOException("Complete native frame unavailable"));
  var whole=OrbitalBodyCustody.readForEncounterRecovery(body);var guns=EnemyMountedCannonCustody.readHeld(body);
  if(!whole.body().equals(body.getUniqueId())||!guns.body().equals(body.getUniqueId()))throw new IOException("Native custody identity conflict");
  int cannonBlocks=0;var bytes=new ByteArrayOutputStream();
  try(var out=new DataOutputStream(bytes)){
   out.writeUTF("IC_ENCOUNTER_HELD_FULL_NATIVE_V1");out.writeUTF(role.name());uuid(out,body.getUniqueId());uuid(out,identity.encounter());uuid(out,identity.root());out.writeUTF(frame.dimension());out.writeLong(frame.instance());
   out.writeInt(whole.minimum().getX());out.writeInt(whole.minimum().getY());out.writeInt(whole.minimum().getZ());out.writeInt(whole.maximum().getX());out.writeInt(whole.maximum().getY());out.writeInt(whole.maximum().getZ());out.writeInt(whole.blocks());out.writeInt(whole.blockEntities());out.writeUTF(whole.digest());
   out.writeInt(guns.attachments().size());for(var gun:guns.attachments()){cannonBlocks=Math.addExact(cannonBlocks,gun.blocks());out.writeInt(gun.mount().getX());out.writeInt(gun.mount().getY());out.writeInt(gun.mount().getZ());uuid(out,gun.entity());out.writeInt(gun.blocks());out.writeUTF(gun.digest());}
  }
  try{return new Snapshot(body.getUniqueId(),identity.encounter(),identity.root(),frame,whole.blocks(),cannonBlocks,HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes.toByteArray())));}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 private static void uuid(DataOutputStream out,UUID id)throws IOException{out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
 /** Does not create controller, permits or entities. Budget audit remains separate. */
 public static EnemyEncounterJournal.Entry auditHeld(EnemyEncounterJournal journal,UUID session,ServerSubLevel source,ServerSubLevel target)throws IOException {
  var saved=journal.get(session);var p=saved.plan();var observed=observePlan(session,source,target,new BlockPos(p.mountX(),p.mountY(),p.mountZ()));
  var a=captureHeld(source,Role.SOURCE);var b=captureHeld(target,Role.TARGET);if(!a.frame().equals(b.frame()))throw new IOException("Held native frames differ");
  return journal.auditHeld(session,observed,a.digest(),b.digest());
 }
}
