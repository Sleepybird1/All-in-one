package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import java.io.IOException;
import java.util.*;

/** Explicit caller-owned native session. No event registration, spawning,
 * saved-phase replay or native body/cargo reconstruction. Semantic updates alone
 * perform journal IO; steady aim ticks do not synchronously save files.
 * Mid-native-call crash/quarantine is separately unqualified. */
public final class EnemyEncounterSession implements AutoCloseable {
 /** Native supplied CBC firing cooldown is120ticks. Retain its complete NBT
  * and allow40additional ordinary ticks for two stable observations; never
  * clear cooldown or accept changing data to manufacture readiness. */
 public static final int CHECKPOINT_SETTLE_TICKS=160;
 private final EnemyEncounterJournal journal;
 private final EnemyEncounterController controller;
 private final ServerSubLevel source,target;
 private EnemyEncounterJournal.Permit permit;
 private boolean stopped;
 private long stoppedAt=-1,lastCheckpointSample=-1;
 private String sampledSource="",sampledTarget="";
 private String reason="ADMITTED";
 private EnemyEncounterSession(EnemyEncounterJournal journal,EnemyEncounterController controller,
        ServerSubLevel source,ServerSubLevel target,EnemyEncounterJournal.Permit permit){
  this.journal=journal;this.controller=controller;this.source=source;this.target=target;this.permit=permit;
 }
 public static Optional<EnemyEncounterSession> start(EnemyEncounterJournal journal,ServerSubLevel source,
        NativeEnemyHull hull,List<BlockPos> engines,BlockPos mount,ServerSubLevel target,Set<UUID> hostile,
        EnemyEncounterController.Settings settings)throws IOException {
  Objects.requireNonNull(journal);var admitted=EnemyEncounterController.start(source,hull,engines,mount,target,hostile,settings);
  if(admitted.isEmpty())return Optional.empty();boolean recorded=false;
  try{var plan=EnemyEncounterCustody.observePlan(UUID.randomUUID(),source,target,mount);var permit=journal.begin(plan);var session=new EnemyEncounterSession(journal,admitted.get(),source,target,permit);recorded=true;return Optional.of(session);}
  finally{if(!recorded)admitted.get().close();}
 }
 private void thread(){if(!source.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread encounter session required");}
 public boolean tick()throws IOException {
  thread();if(stopped)return false;
  if(!journal.current(permit)){controller.close();stopped=true;reason="JOURNAL_PERMIT_LOST";return false;}
  boolean advanced=controller.tick();
  try{var old=journal.get(permit.session());var phase=EnemyEncounterJournal.Phase.valueOf(controller.phase().name());
   if(phase!=old.phase()||controller.emissions()!=old.emissions())permit=journal.observe(permit,phase,controller.emissions(),controller.reason());
   reason=controller.reason();stopped=phase.terminal();if(stopped&&stoppedAt<0)stoppedAt=source.getLevel().getGameTime();return advanced;
  }catch(IOException|RuntimeException failure){controller.close();stopped=true;reason="JOURNAL_UPDATE_FAILED";try{journal.abandon(permit);}catch(RuntimeException alreadyInvalid){failure.addSuppressed(alreadyInvalid);}throw new IOException("Native session stopped after journal update failure; no refunds/replay",failure);}
 }
 @Override public void close()throws IOException {
  thread();controller.close();stopped=true;if(stoppedAt<0)stoppedAt=source.getLevel().getGameTime();reason=controller.reason();
  var old=journal.get(permit.session());if(!old.phase().terminal())permit=journal.observe(permit,EnemyEncounterJournal.Phase.HELD,controller.emissions(),reason);
 }
 /** Stop real actuators before taking exact held snapshots. No budget release. */
 public EnemyEncounterJournal.Entry stopAndCheckpoint(EnemyEncounterBudget budget)throws IOException {
  close();return tryCheckpointHeld(budget).orElseThrow(()->new IOException("Native stopped custody still settling; remain held"));
 }
 /** Explicit capture preparation for this session's exact source. Closing the
  * controller releases existing actuator leases before ordinary-tick settling.
  * A returned marker is still HELD: no ownership transfer, roster deletion,
  * budget release, rewards or permission to resume follows. Native body saving
  * of the marker and journal saving are not claimed to be one transaction. */
 public Optional<EnemyCaptureHold.Record> tryCaptureHeld(UUID claimant,EnemyEncounterBudget budget)throws IOException {
  thread();Objects.requireNonNull(claimant);Objects.requireNonNull(budget);
  if(EnemyCaptureHold.inhibits(source.getUserDataTag()))throw new IOException("Existing capture disposition retained; explicit recovery required");
  close();
  var entry=journal.get(permit.session());
  if(!entry.checkpointed()){
   var checkpoint=tryCheckpointHeld(budget);if(checkpoint.isEmpty())return Optional.empty();entry=checkpoint.get();
  }
  // Reuse the established complete held-custody profile, not a new relaxed
  // digest that drops cargo, ammunition or non-derived machine configuration.
  EnemyEncounterCustody.refreshNativeCaches(source);EnemyEncounterCustody.refreshNativeCaches(target);
  var audited=EnemyEncounterCustody.auditHeld(journal,id(),source,target);
  if(!audited.equals(entry)||controller.active())throw new IOException("Capture session changed after stop");
  var metadata=source.getUserDataTag().copy();
  var record=EnemyCaptureHold.beginHeld(source,claimant,entry.sourceProof());
  metadata.put(EnemyCaptureHold.KEY,EnemyCaptureHold.encode(record));
  // On any failure the new hold is deliberately retained, never rolled back
  // to NPC control. Commission/physical bodies/cargo are not rewritten.
  if(!metadata.equals(source.getUserDataTag()))throw new IOException("Capture metadata changed unexpectedly; remain held");
  EnemyEncounterCustody.auditHeld(journal,id(),source,target);
  reason="CAPTURE_HELD_REQUIRES_TRANSFER_REVIEW";
  return Optional.of(record);
 }
 /** Two consecutive ordinary-tick complete snapshots must match after stop.
  * Repeated same-tick polling cannot qualify readiness. Unknown changing data
  * remains covered; timeout never creates a checkpoint or drops reservations. */
 public Optional<EnemyEncounterJournal.Entry> tryCheckpointHeld(EnemyEncounterBudget budget)throws IOException {
  thread();if(!stopped||controller.active()||stoppedAt<0)throw new IllegalStateException("Explicit stopped session required");
  long now=source.getLevel().getGameTime();if(now<stoppedAt||now<lastCheckpointSample)throw new IOException("Native checkpoint clock rollback");
  if(now-stoppedAt>CHECKPOINT_SETTLE_TICKS)throw new IOException("Native stopped custody did not settle within bounded observations");
  if(now==stoppedAt||now==lastCheckpointSample)return Optional.empty();
  EnemyEncounterCustody.refreshNativeCaches(source);EnemyEncounterCustody.refreshNativeCaches(target);var a=EnemyEncounterCustody.captureHeld(source,EnemyEncounterCustody.Role.SOURCE);var b=EnemyEncounterCustody.captureHeld(target,EnemyEncounterCustody.Role.TARGET);
  if(!a.frame().equals(b.frame()))throw new IOException("Stopped native frames differ");
  boolean stable=now-lastCheckpointSample==1&&a.digest().equals(sampledSource)&&b.digest().equals(sampledTarget);
  lastCheckpointSample=now;sampledSource=a.digest();sampledTarget=b.digest();if(!stable)return Optional.empty();
  var roster=EnemyEncounterRoster.get(source.getLevel());roster.record(source);roster.record(target);roster.seal(source.getLevel(),budget);
  permit=journal.checkpointHeld(permit,a.digest(),b.digest());return Optional.of(journal.get(permit.session()));
 }
 /** Native audit/budget reconstruction only; never constructs a controller. */
 public static EnemyEncounterRoster.HeldRecovery recoverHeld(EnemyEncounterJournal journal,UUID session,
        ServerSubLevel source,ServerSubLevel target,EnemyEncounterBudget budget)throws IOException {
  var entry=journal.get(session);if(!entry.checkpointed())throw new IOException("Uncheckpointed native recovery remains held");
  var p=entry.plan();if(!EnemyEncounterCustody.observePlan(session,source,target,new BlockPos(p.mountX(),p.mountY(),p.mountZ())).equals(p))throw new IOException("Native recovery identity changed before refresh");
  EnemyEncounterCustody.refreshNativeCaches(source);EnemyEncounterCustody.refreshNativeCaches(target);EnemyEncounterCustody.auditHeld(journal,session,source,target);
  return EnemyEncounterRoster.get(source.getLevel()).recoverHeld(source.getLevel(),budget);
 }
 public boolean active(){return !stopped&&controller.active()&&journal.current(permit);}
 /** Explicit read-only capture restart inspection. No controller construction,
  * derived-cache refresh, budget repair, metadata mutation or transfer authority.
  * The caller supplies the already loaded authoritative roster and claimant. */
 public static EnemyCaptureHold.Record auditCaptureHeld(EnemyEncounterJournal journal,UUID session,
      ServerSubLevel source,ServerSubLevel target,EnemyEncounterRoster roster,UUID claimant)throws IOException {
  Objects.requireNonNull(claimant);Objects.requireNonNull(roster);
  if(source==null||target==null||!source.getLevel().getServer().isSameThread())throw new IOException("Native server-thread capture audit required");
  var metadata=source.getUserDataTag();
  if(metadata==null||!metadata.contains(EnemyCaptureHold.KEY,10))throw new IOException("Capture hold missing or malformed");
  var sourceTag=metadata.copy();var targetTag=target.getUserDataTag()==null?null:target.getUserDataTag().copy();
  var record=EnemyCaptureHold.decode(sourceTag.getCompound(EnemyCaptureHold.KEY));
  var entry=journal.get(session);var plan=entry.plan();
  EnemyCaptureHold.requireBinding(record,plan.sourceEncounter(),plan.sourceRoot(),claimant,entry.sourceProof());
  EnemyEncounterCustody.auditHeld(journal,session,source,target);
  var audit=roster.auditSealedReadOnly(source.getLevel());
  if(!plan.sourceEncounter().equals(audit.bodies().get(source.getUniqueId()))
      ||!plan.targetAuthority().equals(audit.bodies().get(target.getUniqueId()))
      ||!sourceTag.equals(source.getUserDataTag())||!Objects.equals(targetTag,target.getUserDataTag())
      ||!entry.equals(journal.get(session)))throw new IOException("Capture audit scope changed");
  return record;
 }
 public String reason(){return reason;}
 public EnemyEncounterController.Phase phase(){return controller.phase();}
 public int emissions(){return controller.emissions();}
 public UUID id(){return permit.session();}
}
