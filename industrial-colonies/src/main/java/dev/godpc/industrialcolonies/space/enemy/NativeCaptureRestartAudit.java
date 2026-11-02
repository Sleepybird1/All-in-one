package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.OrbitalBodyCustody;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.IdentityDirectorySavedData;
import java.io.IOException;
import java.nio.file.Path;
import java.util.*;

/** Read-only restarted ownership/custody evidence. Never repairs the original
 * roster (whose owner fingerprint changes), releases budgets, resumes control,
 * repeats the setter or grants salvage/rewards. Pending applied custody without
 * a receipt is explicitly UNVERIFIED, even if saved ownership agrees. */
public final class NativeCaptureRestartAudit {
 public enum State { UNAPPLIED_HELD, ACKNOWLEDGED_ROLLBACK_HELD, APPLIED_HELD, PENDING_APPLIED_UNVERIFIED_HELD }
 public record Result(State state,EnemyCaptureTransferIntent.Held intent,String sourceCustody,String targetCustody){}
 private NativeCaptureRestartAudit(){}
 private static void require(boolean ok,String why)throws IOException{if(!ok)throw new IOException(why);}
 public static Result inspect(Path directory,UUID root,EnemyEncounterJournal journal,ServerSubLevel source,
     ServerSubLevel target,IdentityDirectorySavedData identities)throws IOException{
  require(source!=null&&target!=null&&source.getLevel()==target.getLevel()&&source.getLevel().getServer().isSameThread(),"Same-level server-thread capture audit required");
  NativeEnemyOutcomeStore.requireDirectory(source.getLevel().getServer(),directory,false);
  long tick=source.getLevel().getGameTime();var intent=EnemyCaptureTransferIntent.inspectHeld(directory,root);
  var disposition=new EnemyRootDisposition.Held(root,intent.encounter(),intent.claimant(),EnemyRootDisposition.Kind.CAPTURE);
  EnemyRootDisposition.require(directory,disposition);
  var acknowledgement=EnemyCaptureTransferIntent.inspectAppliedHeld(directory,root);
  var entry=journal.get(intent.session());var plan=entry.plan();
  require(journal.held(intent.session())&&entry.checkpointed()&&entry.revision()==intent.revision()
      &&plan.source().equals(root)&&plan.sourceRoot().equals(root)&&plan.sourceEncounter().equals(intent.encounter())
      &&plan.target().equals(intent.target())&&source.getUniqueId().equals(root)&&target.getUniqueId().equals(intent.target())
      &&plan.dimension().equals(intent.dimension())&&entry.sourceProof().equals(intent.sourceProof())&&entry.targetProof().equals(intent.targetProof()),"Capture intent/journal mismatch");
  var observedPlan=EnemyEncounterCustody.observePlan(intent.session(),source,target,new BlockPos(plan.mountX(),plan.mountY(),plan.mountZ()));
  require(plan.equals(observedPlan),"Capture physical plan changed");
  var sourceMetadata=OrbitalBodyCustody.metadataDigest(source.getUserDataTag());var targetMetadata=OrbitalBodyCustody.metadataDigest(target.getUserDataTag());
  var tag=source.getUserDataTag();require(tag!=null&&tag.contains(EnemyCaptureHold.KEY,10),"Capture hold absent");
  EnemyCaptureHold.requireBinding(EnemyCaptureHold.decode(tag.getCompound(EnemyCaptureHold.KEY)),intent.encounter(),root,intent.claimant(),intent.sourceProof());
  var be=source.getLevel().getBlockEntity(new BlockPos(intent.x(),intent.y(),intent.z()));
  require(be!=null&&be.getClass()==ShipTransponderBlockEntity.class,"Original capture transponder absent");
  var transponder=(ShipTransponderBlockEntity)be;var owner=transponder.ownerId();
  require(transponder.transponderId().equals(intent.transponder())&&(owner.isEmpty()||owner.equals(Optional.of(intent.claimant()))),"Foreign capture owner");
  NativeCaptureOwnership.read(source,intent.transponder(),intent.claimant(),owner,identities);
  var a=EnemyEncounterCustody.captureHeld(source,EnemyEncounterCustody.Role.SOURCE);var b=EnemyEncounterCustody.captureHeld(target,EnemyEncounterCustody.Role.TARGET);
  require(b.digest().equals(intent.targetProof()),"Capture target custody changed");
  State state;
  if(owner.isEmpty()){
   require(a.digest().equals(intent.sourceProof()),"Unapplied capture custody changed");
   state=acknowledgement.isPresent()?State.ACKNOWLEDGED_ROLLBACK_HELD:State.UNAPPLIED_HELD;
  }else if(acknowledgement.isPresent()){
   var ack=acknowledgement.get();require(a.digest().equals(ack.sourceCustody())&&b.digest().equals(ack.targetCustody()),"Applied capture custody changed");
   state=State.APPLIED_HELD;
  }else state=State.PENDING_APPLIED_UNVERIFIED_HELD;
  if(acknowledgement.isPresent()){
   var ack=acknowledgement.get();require(sourceMetadata.equals(ack.sourceMetadata())&&targetMetadata.equals(ack.targetMetadata()),"Capture metadata changed");
  }
  require(source.getLevel().getGameTime()==tick&&entry.equals(journal.get(intent.session()))
      &&a.equals(EnemyEncounterCustody.captureHeld(source,EnemyEncounterCustody.Role.SOURCE))&&b.equals(EnemyEncounterCustody.captureHeld(target,EnemyEncounterCustody.Role.TARGET))
      &&sourceMetadata.equals(OrbitalBodyCustody.metadataDigest(source.getUserDataTag()))&&targetMetadata.equals(OrbitalBodyCustody.metadataDigest(target.getUserDataTag()))
      &&intent.equals(EnemyCaptureTransferIntent.inspectHeld(directory,root))&&acknowledgement.equals(EnemyCaptureTransferIntent.inspectAppliedHeld(directory,root)),"Capture restart observation changed");
  EnemyRootDisposition.require(directory,disposition);return new Result(state,intent,a.digest(),b.digest());
 }
}
