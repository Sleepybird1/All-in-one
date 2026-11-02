package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.OrbitalBodyCustody;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.*;
import org.joml.*;
import java.io.IOException;
import java.util.*;

/** One-shot comparison and opt-in operator fixture for the native setter.
 * Retains capture hold and budgets. Live agreement is not persisted ownership;
 * no player command, movement authority or automatic recovery is registered. */
public final class NativeCaptureOwnerChange {
 public record Observed(UUID session,UUID body,UUID transponder,UUID claimant,String comparableCustody){}
 public record AppliedHeld(EnemyCaptureTransferIntent.Held intent,Observed change,NativeCaptureOwnership.LiveSnapshot live){}
 private record Physical(Vector3d position,Quaterniond rotation,Vector3d linear,Vector3d angular){
  static Physical read(ServerSubLevel b){var h=RigidBodyHandle.of(b);return new Physical(new Vector3d(b.logicalPose().position()),new Quaterniond(b.logicalPose().orientation()),new Vector3d(h.getLinearVelocity()),new Vector3d(h.getAngularVelocity()));}
 }
 private final EnemyEncounterJournal journal;
 private final EnemyEncounterJournal.Entry entry;
 private final ServerSubLevel source,target;
 private final ServerPlayer player;
 private final ShipTransponderBlockEntity transponder;
 private final UUID transponderId;
 private final String expectedName;
 private final long tick;
 private final CompoundTag sourceTag,targetTag;
 private final Physical sourcePhysical,targetPhysical;
 private final OrbitalBodyCustody.Snapshot sourceCustody,targetCustody;
 private final EnemyMountedCannonCustody.Snapshot sourceGuns,targetGuns;
 private boolean consumed;
 private boolean intentAttempted;
 private java.nio.file.Path intentDirectory;
 private EnemyCaptureTransferIntent.Held savedIntent;
 private NativeCaptureOwnerChange(EnemyEncounterJournal journal,EnemyEncounterJournal.Entry entry,
     ServerSubLevel source,ServerSubLevel target,ServerPlayer player,ShipTransponderBlockEntity transponder)throws IOException{
  this.journal=journal;this.entry=entry;this.source=source;this.target=target;this.player=player;this.transponder=transponder;
  transponderId=transponder.transponderId();expectedName=IdentityNames.sanitize(player.getGameProfile().getName());tick=source.getLevel().getGameTime();
  sourceTag=copy(source.getUserDataTag());targetTag=copy(target.getUserDataTag());
  sourcePhysical=Physical.read(source);targetPhysical=Physical.read(target);
  sourceCustody=OrbitalBodyCustody.readForCaptureOwnerChange(source,transponder.getBlockPos(),transponderId,Optional.empty(),transponder.ownerName());
  targetCustody=OrbitalBodyCustody.read(target);sourceGuns=EnemyMountedCannonCustody.readHeld(source);targetGuns=EnemyMountedCannonCustody.readHeld(target);
 }
 private static CompoundTag copy(CompoundTag tag){return tag==null?null:tag.copy();}
 private static void require(boolean ok,String reason)throws IOException{if(!ok)throw new IOException(reason);}
 private static void player(ServerSubLevel body,ServerPlayer player)throws IOException{
  var server=body.getLevel().getServer();require(server.isSameThread()&&player!=null&&server.getPlayerList().getPlayer(player.getUUID())==player
      &&player.isAlive()&&!player.isRemoved()&&player.serverLevel()==body.getLevel(),"Live same-level claimant required");
 }
 public static NativeCaptureOwnerChange prepare(EnemyEncounterJournal journal,UUID session,ServerSubLevel source,
     ServerSubLevel target,EnemyEncounterRoster roster,ServerPlayer player,UUID transponderId,IdentityDirectorySavedData directory)throws IOException{
  player(source,player);EnemyEncounterSession.auditCaptureHeld(journal,session,source,target,roster,player.getUUID());
  var authority=NativeCaptureOwnership.read(source,transponderId,player.getUUID(),Optional.empty(),directory);
  var be=source.getLevel().getBlockEntity(authority.position());
  require(be instanceof ShipTransponderBlockEntity&&be.getClass()==ShipTransponderBlockEntity.class,"Original basic transponder unavailable");
  var result=new NativeCaptureOwnerChange(journal,journal.get(session),source,target,player,(ShipTransponderBlockEntity)be);
  result.scope();return result;
 }
 private void scope()throws IOException{
  player(source,player);require(source.getLevel()==target.getLevel()&&!source.isRemoved()&&!target.isRemoved()
      &&source.getLevel().getGameTime()==tick&&entry.equals(journal.get(entry.plan().session()))&&journal.held(entry.plan().session())
      &&!transponder.isRemoved()&&source.getLevel().getBlockEntity(transponder.getBlockPos())==transponder
      &&Sable.HELPER.getContaining(transponder)==source&&transponder.transponderId().equals(transponderId)
      &&Objects.equals(sourceTag,source.getUserDataTag())&&Objects.equals(targetTag,target.getUserDataTag())
      &&sourcePhysical.equals(Physical.read(source))&&targetPhysical.equals(Physical.read(target)),"Capture observation identity/metadata/motion changed");
 }
 /** Must succeed before the caller invokes a native owner setter. Any failed
  * attempt consumes this observation; its possibly partial file remains held. */
 public synchronized EnemyCaptureTransferIntent.Held persistIntent(java.nio.file.Path directory)throws IOException{
  require(!consumed&&!intentAttempted,"Capture intent already attempted");intentAttempted=true;
  try{
   scope();
   NativeEnemyOutcomeStore.requireDirectory(source.getLevel().getServer(),directory,true);
   require(transponder.ownerId().isEmpty(),"Capture source no longer unowned");
   var before=OrbitalBodyCustody.readForCaptureOwnerChange(source,transponder.getBlockPos(),transponderId,Optional.empty(),transponder.ownerName());
   require(sourceCustody.equals(before)&&targetCustody.equals(OrbitalBodyCustody.read(target))
       &&sourceGuns.equals(EnemyMountedCannonCustody.readHeld(source))&&targetGuns.equals(EnemyMountedCannonCustody.readHeld(target)),"Capture custody changed before intent");
   var pos=transponder.getBlockPos();var plan=entry.plan();
   var held=new EnemyCaptureTransferIntent.Held(plan.session(),plan.sourceEncounter(),plan.sourceRoot(),plan.target(),player.getUUID(),transponderId,
       entry.revision(),plan.dimension(),pos.getX(),pos.getY(),pos.getZ(),entry.sourceProof(),entry.targetProof(),sourceCustody.digest());
   var saved=EnemyCaptureTransferIntent.persist(directory,held);scope();
   intentDirectory=directory.toAbsolutePath().normalize();savedIntent=saved;return saved;
  }catch(IOException|RuntimeException ex){consumed=true;throw ex;}
 }
 public synchronized Observed verifyApplied()throws IOException{
  require(!consumed&&intentAttempted,"Capture observation consumed or intent missing");consumed=true;scope();
  require(savedIntent!=null&&savedIntent.equals(EnemyCaptureTransferIntent.inspectHeld(intentDirectory,savedIntent.root())),"Capture intent changed");
  EnemyRootDisposition.require(intentDirectory,new EnemyRootDisposition.Held(savedIntent.root(),savedIntent.encounter(),savedIntent.claimant(),EnemyRootDisposition.Kind.CAPTURE));
  var actual=OrbitalBodyCustody.readForCaptureOwnerChange(source,transponder.getBlockPos(),transponderId,Optional.of(player.getUUID()),expectedName);
  require(sourceCustody.equals(actual)&&targetCustody.equals(OrbitalBodyCustody.read(target))
      &&sourceGuns.equals(EnemyMountedCannonCustody.readHeld(source))&&targetGuns.equals(EnemyMountedCannonCustody.readHeld(target)),"Capture owner setter changed cargo/configuration");
  scope();return new Observed(entry.plan().session(),source.getUniqueId(),transponderId,player.getUUID(),actual.digest());
 }
 /** Disposable fixture only until native transfer/save qualification is accepted.
  * No rollback on error: owner may already have changed, so marker and intent
  * must remain for explicit audit. Never return this as a resume/grant permit. */
 public synchronized AppliedHeld applyHeld(java.nio.file.Path directory,IdentityDirectorySavedData identities)throws IOException{
  require(Boolean.getBoolean("ic.boss.captureTransferProbe")&&player.hasPermissions(4),"Operator capture fixture opt-in required");
  var intent=persistIntent(directory);
  try{
   EnemyRootDisposition.require(intentDirectory,new EnemyRootDisposition.Held(intent.root(),intent.encounter(),intent.claimant(),EnemyRootDisposition.Kind.CAPTURE));
   transponder.setOwner(player);
   var changed=verifyApplied();
   // Separately compare cache-qualified custody around refresh, after the
   // exact owner-only comparison above. No owner or inventory omissions here.
   var beforeRefresh=OrbitalBodyCustody.readForEncounterRecovery(source);
   require(EnemyEncounterCustody.refreshNativeCaches(source)==1,"Expected one native transponder refresh");
   require(beforeRefresh.equals(OrbitalBodyCustody.readForEncounterRecovery(source))
       &&targetCustody.equals(OrbitalBodyCustody.read(target))
       &&sourceGuns.equals(EnemyMountedCannonCustody.readHeld(source))&&targetGuns.equals(EnemyMountedCannonCustody.readHeld(target)),"Capture refresh changed cargo/configuration");
   scope();
   var live=NativeCaptureOwnership.readLive(source,transponderId,player.getUUID(),Optional.of(player.getUUID()),identities);
   require(intent.equals(EnemyCaptureTransferIntent.inspectHeld(intentDirectory,intent.root())),"Capture intent changed after refresh");
   scope();
   EnemyCaptureTransferIntent.acknowledge(intentDirectory,new EnemyCaptureTransferIntent.Applied(intent,
       EnemyEncounterCustody.captureHeld(source,EnemyEncounterCustody.Role.SOURCE).digest(),
       EnemyEncounterCustody.captureHeld(target,EnemyEncounterCustody.Role.TARGET).digest(),
       OrbitalBodyCustody.metadataDigest(source.getUserDataTag()),OrbitalBodyCustody.metadataDigest(target.getUserDataTag())));
   scope();return new AppliedHeld(intent,changed,live);
  }catch(IOException|RuntimeException ex){consumed=true;throw ex;}
 }
}
