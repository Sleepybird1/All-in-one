package dev.godpc.industrialcolonies.space.enemy;
import java.io.IOException;
import java.nio.file.Path;
import java.util.*;

/** Staged callback coordinator. No native grant implementation. An observed
 * delivery remains unacknowledged on disk and must never be retried on reopen. */
public final class EnemyRewardDelivery {
 public enum State { RESERVED, ATTEMPTING, OBSERVED_DELIVERED, ACKNOWLEDGED, HELD }
 public record Observation(UUID encounter,UUID beneficiary,String planDigest,String inventoryEvidenceDigest){}
 @FunctionalInterface public interface Adapter { Observation deliver()throws Exception; }
 @FunctionalInterface interface Guard { void check()throws IOException; }
 private final Path directory;
 private final EnemyRewardReservation.HeldClaim claim;
 private final Thread owner;
 private State state=State.RESERVED;
 private Observation observation;
 private Guard guard=()->{};
 private EnemyRewardDelivery(Path directory,EnemyRewardReservation.HeldClaim claim){this.directory=directory;this.claim=claim;owner=Thread.currentThread();}
 public static EnemyRewardDelivery reserve(Path directory,EnemyRewardAdmission.Evidence evidence,String plan)throws IOException{
  return new EnemyRewardDelivery(directory,EnemyRewardReservation.reserve(directory,evidence,plan));
 }
 static EnemyRewardDelivery reserveGuarded(Path directory,EnemyRewardAdmission.Evidence evidence,String plan,Guard guard)throws IOException{
  Objects.requireNonNull(guard).check();var result=reserve(directory,evidence,plan);result.guard=guard;return result;
 }
 public synchronized Observation attempt(EnemyRewardAdmission.Evidence fresh,Adapter adapter)throws Exception{
  try {
   if(Thread.currentThread()!=owner||state!=State.RESERVED)throw new IllegalStateException("Delivery session unavailable");
   if(EnemyRewardAdmission.assess(fresh)!=EnemyRewardAdmission.Decision.ALLOW_RESERVATION
       ||!claim.encounter().equals(fresh.encounter())||!claim.root().equals(fresh.root())
       ||!claim.beneficiary().equals(fresh.beneficiary())||claim.revision()!=fresh.revision()
       ||!claim.defeatDigest().equals(fresh.verifiedDestructionDigest()))throw new IllegalStateException("Fresh delivery scope changed");
   if(!claim.equals(EnemyRewardReservation.inspectHeld(directory,claim.encounter())))throw new IOException("Reservation changed");
   disposition();
   guard.check();
   state=State.ATTEMPTING;
   var result=Objects.requireNonNull(adapter).deliver();
   if(state!=State.ATTEMPTING||result==null||!claim.encounter().equals(result.encounter())
       ||!claim.beneficiary().equals(result.beneficiary())||!claim.rewardPlanDigest().equals(result.planDigest())
       ||result.inventoryEvidenceDigest()==null||!result.inventoryEvidenceDigest().matches("[0-9a-f]{64}"))
    throw new IllegalStateException("Delivery outcome uncertain");
   if(!claim.equals(EnemyRewardReservation.inspectHeld(directory,claim.encounter())))throw new IOException("Reservation changed during delivery");
   disposition();
   guard.check();
   observation=result;state=State.OBSERVED_DELIVERED;return result;
  }catch(Exception|Error failure){state=State.HELD;throw failure;}
 }
 public synchronized void hold(){state=State.HELD;}
 public synchronized EnemyRewardReservation.HeldAcknowledgement acknowledge()throws IOException{
  try {
   if(Thread.currentThread()!=owner||state!=State.OBSERVED_DELIVERED||observation==null)throw new IOException("No live delivery to acknowledge");
   disposition();
   guard.check();
   var receipt=EnemyRewardReservation.acknowledge(directory,claim,observation.inventoryEvidenceDigest());
   state=State.ACKNOWLEDGED;return receipt;
  }catch(IOException|RuntimeException failure){state=State.HELD;throw failure;}
 }
 public synchronized State state(){return state;}
 private void disposition()throws IOException{EnemyRootDisposition.require(directory,new EnemyRootDisposition.Held(claim.root(),claim.encounter(),claim.beneficiary(),EnemyRootDisposition.Kind.REWARD));}
 public synchronized Optional<Observation> observed(){return Optional.ofNullable(observation);}
}
