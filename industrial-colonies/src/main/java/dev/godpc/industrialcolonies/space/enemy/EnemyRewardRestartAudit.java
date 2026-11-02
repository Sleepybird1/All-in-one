package dev.godpc.industrialcolonies.space.enemy;

import java.io.IOException;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Optional;

/** Read-only restart diagnostic. Every outcome remains held: even an exact
 * acknowledgement match cannot authorize another grant. The trusted observer
 * must read actual inventory custody; digest syntax alone proves nothing. */
public final class EnemyRewardRestartAudit {
 public enum State { ACKNOWLEDGEMENT_MATCHED_HELD, UNACKNOWLEDGED_HELD, EVIDENCE_MISMATCH_HELD }
 public record Observation(EnemyRewardReservation.HeldClaim claim, long tick,
                           boolean complete, String inventoryEvidenceDigest) {}
 public record Result(State state, EnemyRewardReservation.HeldClaim claim,
                      Optional<EnemyRewardReservation.HeldAcknowledgement> acknowledgement) {}
 @FunctionalInterface public interface Observer {
  Observation observe(EnemyRewardReservation.HeldClaim claim) throws IOException;
 }
 private EnemyRewardRestartAudit() {}
 public static Result inspect(Path directory, java.util.UUID encounter, long currentTick,
                              Observer observer) throws IOException {
  if(currentTick<0)throw new IOException("Invalid audit clock");
  var claim=EnemyRewardReservation.inspectHeld(directory,encounter);
  var ack=readAck(directory,claim);
  var observation=Objects.requireNonNull(observer).observe(claim);
  // Observation is not allowed to alter the record being audited. A missing,
  // newly created or different acknowledgement invalidates this audit too.
  if(!claim.equals(EnemyRewardReservation.inspectHeld(directory,encounter))
      ||!ack.equals(readAck(directory,claim)))throw new IOException("Reward records changed during audit");
  if(observation==null||!claim.equals(observation.claim())||!observation.complete()
      ||observation.tick()!=currentTick||observation.inventoryEvidenceDigest()==null
      ||!observation.inventoryEvidenceDigest().matches("[0-9a-f]{64}"))
   return new Result(State.EVIDENCE_MISMATCH_HELD,claim,ack);
  if(ack.isEmpty())return new Result(State.UNACKNOWLEDGED_HELD,claim,ack);
  return new Result(ack.get().inventoryEvidenceDigest().equals(observation.inventoryEvidenceDigest())
      ?State.ACKNOWLEDGEMENT_MATCHED_HELD:State.EVIDENCE_MISMATCH_HELD,claim,ack);
 }
 private static Optional<EnemyRewardReservation.HeldAcknowledgement> readAck(
     Path directory, EnemyRewardReservation.HeldClaim claim)throws IOException {
  try {
   var ack=EnemyRewardReservation.inspectAcknowledgementHeld(directory,claim.encounter());
   if(!claim.equals(ack.claim()))throw new IOException("Reward claim changed during acknowledgement read");
   return Optional.of(ack);
  }catch(NoSuchFileException absent){
   // inspectAcknowledgementHeld reads the claim first. Never misclassify a
   // missing/replaced claim as a merely absent acknowledgement.
   if(!claim.equals(EnemyRewardReservation.inspectHeld(directory,claim.encounter())))
    throw new IOException("Reward claim changed",absent);
   return Optional.empty();
  }
 }
}
