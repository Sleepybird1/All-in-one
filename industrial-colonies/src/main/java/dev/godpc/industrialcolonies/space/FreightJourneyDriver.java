package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.godpc.industrialcolonies.space.FreightJourneyJournal.*;

/** Phase executor. The native adapter owns only its acquired actuator leases.
 * Observation must establish live ownership, cargo conservation, frame/geometry,
 * resources and phase completion; a digest alone is not a physical verifier.
 * Construction and server restart never start work. */
public final class FreightJourneyDriver {
 public record Observation(UUID body,String evidenceDigest,boolean complete,String holdReason){
  public Observation {
   Objects.requireNonNull(body);Objects.requireNonNull(holdReason);
   if(evidenceDigest==null||!evidenceDigest.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Verified physical evidence digest required");
  }
 }
 public interface Adapter {
  boolean enabled();
  Observation observe(Entry entry)throws Exception;
  /** One ordinary server tick; must not create replacement cargo or replay prior legs. */
  void step(Entry entry,Permit permit)throws Exception;
  /** Idempotently release this adapter's leases; never undock/delete/refund cargo. */
  void stop()throws Exception;
 }
 /** Optional independent-instance boundary. Both callbacks run with actuator
  * leases stopped. Preparation must freshly verify the exact physical intent;
  * application must recheck it, change only the coordinate frame, and return
  * complete physical verification. Neither callback may start propulsion.
  */
 public interface EncounterAdapter extends Adapter {
  String prepareEncounter(Entry entry)throws Exception;
  Observation applyEncounter(Entry pending,Permit permit)throws Exception;
 }
 public enum State { HELD, RUNNING, ADVANCED, COMPLETE, CANCELLED }
 public record Result(State state,Phase phase,String reason){}
 private final FreightJourneyJournal journal;
 private final UUID id;
 private final Adapter adapter;
 private Permit permit;
 private boolean stopFailed;
 private long lastTick=-1;
 private String reason="Explicit verified start required";
 public FreightJourneyDriver(FreightJourneyJournal journal,UUID journey,Adapter adapter){
  this.journal=Objects.requireNonNull(journal);this.id=Objects.requireNonNull(journey);this.adapter=Objects.requireNonNull(adapter);journal.get(id);
 }
 public synchronized Result resume(){
  try{
   Entry entry=journal.get(id);
   if(entry.phase().terminal())return terminal(entry);
   if(permit!=null&&journal.admits(permit))return result(State.RUNNING,"Already running");
   if(!adapter.enabled())return hold("Operator disabled journey");
   Observation observation=adapter.observe(entry);validate(entry,observation);
   if(!observation.holdReason().isBlank())return hold(observation.holdReason());
   if(!adapter.enabled())return hold("Control changed during resume observation");
   permit=journal.resume(id,entry.revision(),observation.evidenceDigest());lastTick=-1;reason="";return result(State.RUNNING,"");
  }catch(Exception error){return hold("Resume verification failed: "+error);}
 }
 public synchronized Result tick(long serverTick){
  try{
   Entry entry=journal.get(id);if(entry.phase().terminal())return terminal(entry);
   if(permit==null||!journal.admits(permit))return hold("Journey held or permit revoked");
   if(serverTick<0||serverTick<=lastTick)return hold("Nonmonotonic or duplicate driver tick");
   lastTick=serverTick;
   if(!adapter.enabled())return hold("Operator disabled journey");
   Observation observation=adapter.observe(entry);validate(entry,observation);
   if(!observation.holdReason().isBlank())return hold(observation.holdReason());
   // Recheck after observation: callbacks may have revoked admission.
   if(!journal.admits(permit)||!adapter.enabled())return hold("Control changed during observation");
   if(observation.complete()){
    adapter.stop();
    if(entry.phase()==Phase.ORBIT&&adapter instanceof EncounterAdapter encounter){
     if(!journal.admits(permit)||!adapter.enabled())return hold("Control changed before encounter preparation");
     String intent=encounter.prepareEncounter(entry);
     if(!journal.admits(permit)||!adapter.enabled())return hold("Control changed during encounter preparation");
     // The exact durable intent precedes physical mutation. Any later failure
     // leaves it held for explicit native reconciliation, never automatic retry.
     permit=journal.beginEncounter(permit,intent);
     Entry pending=journal.get(id);
     Observation applied=encounter.applyEncounter(pending,permit);validate(pending,applied);
     if(!applied.complete()||!applied.holdReason().isBlank())return hold("Encounter outcome unverified: "+applied.holdReason());
     if(!journal.admits(permit)||!adapter.enabled())return hold("Control changed during encounter application");
     permit=journal.finishEncounter(permit,applied.body(),applied.evidenceDigest());
     return result(State.ADVANCED,"");
    }
    // Persist the verified boundary before a later tick may operate the next phase.
    Phase next=Phase.values()[entry.phase().ordinal()+1];
    permit=journal.advance(permit,next,observation.body(),observation.evidenceDigest());
    if(next.terminal())return terminal(journal.get(id));
    return result(State.ADVANCED,"");
   }
   if(entry.phase()!=Phase.READY)adapter.step(entry,permit);
   return result(State.RUNNING,"");
  }catch(Exception error){return hold("Journey execution failed: "+error);}
 }
 public synchronized Result hold(String why){
  permit=null;String failure=why;stopFailed=false;
  try{adapter.stop();}catch(Exception error){stopFailed=true;failure+="; actuator stop failed: "+error;}
  try{
   Entry entry=journal.get(id);
   if(!entry.phase().terminal()&&(!journal.held(id)||entry.holdReason().isBlank()))journal.hold(id,failure);
  }catch(Exception error){failure+="; journal hold failed: "+error;}
  reason=failure;return result(State.HELD,failure);
 }
 public synchronized Result cancel(String why){
  Result stopped=hold(why);
  if(stopFailed)return stopped;
  try{Entry entry=journal.get(id);if(entry.phase().terminal())return terminal(entry);journal.cancel(id,entry.revision(),why);return result(State.CANCELLED,why);}
  catch(Exception error){return result(State.HELD,stopped.reason()+"; cancellation not recorded: "+error);}
 }
 private void validate(Entry entry,Observation observation){
  Objects.requireNonNull(observation,"Missing physical observation");
  boolean nativeTransfer=entry.phase()==Phase.HANDOFF&&observation.complete();
  if(nativeTransfer?observation.body().equals(entry.body()):!observation.body().equals(entry.body()))throw new IllegalStateException("Physical body identity disagrees with journey phase");
 }
 private Result terminal(Entry entry){
  permit=null;
  try{adapter.stop();}catch(Exception error){return result(State.HELD,"Terminal actuator stop failed: "+error);}
  return result(entry.phase()==Phase.COMPLETE?State.COMPLETE:State.CANCELLED,entry.holdReason());
 }
 private Result result(State state,String reason){return new Result(state,journal.get(id).phase(),reason);}
}
