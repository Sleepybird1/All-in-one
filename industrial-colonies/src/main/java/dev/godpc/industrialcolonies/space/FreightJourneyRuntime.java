package dev.godpc.industrialcolonies.space;

import java.util.*;
import java.util.function.Supplier;
import net.minecraft.server.MinecraftServer;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import dev.godpc.industrialcolonies.space.FreightJourneyJournal.*;

/** Explicitly admitted, server-owned journey execution. No persisted adapter or
 * automatic resume. A fresh factory must supply actual phase/actuator/cargo
 * verification; this lifecycle supplies no trajectory and cannot replace it. */
public final class FreightJourneyRuntime {
 private FreightJourneyRuntime(){}
 public static final int MAX_ACTIVE=8;
 private static final Map<MinecraftServer,Map<UUID,FreightJourneyDriver>> RUNS=new WeakHashMap<>();
 private static boolean registered;
 private static void thread(MinecraftServer server){if(!server.isSameThread())throw new IllegalStateException("Journey runtime requires server thread");}
 private static void register(){
  if(registered)return;registered=true;
  NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e)->tick(e.getServer()));
  NeoForge.EVENT_BUS.addListener((ServerStoppingEvent e)->shutdown(e.getServer()));
 }
 /** Called only by an authorized commissioning flow, never while loading saves.
  * Factory construction/observation must not acquire or command actuators. */
 public static FreightJourneyDriver.Result resume(MinecraftServer server,UUID id,long expectedRevision,Supplier<FreightJourneyDriver.Adapter> freshFactory){
  thread(server);Objects.requireNonNull(freshFactory);var journal=FreightJourneyControl.journal(server);var entry=journal.get(id);
  if(!journal.fault().isEmpty()||entry.phase().terminal()||!journal.held(id)||entry.revision()!=expectedRevision)
   throw new IllegalStateException("Exact held nonterminal journey revision required");
  var runs=RUNS.computeIfAbsent(server,k->new LinkedHashMap<>());
  if(runs.containsKey(id)||runs.size()>=MAX_ACTIVE)throw new IllegalStateException("Journey already attached or active-session limit reached");
  if(AutonomousShipControl.get(server).disabled(entry.plan().transponder()))throw new IllegalStateException("Ship automation disabled");
  var ref=FreightDestinationReference.decode(entry.plan().destinationRoute());ref.requirePlan(entry.plan());NativeFreightDestination.resolve(server,ref,entry.plan().owner());
  var delegate=Objects.requireNonNull(freshFactory.get(),"Fresh physical adapter required");
  if(!journal.get(id).equals(entry)||!journal.held(id)){try{delegate.stop();}catch(Exception ignored){}throw new IllegalStateException("Journey changed during adapter construction");}
  FreightJourneyDriver.Adapter controlled=delegate instanceof FreightJourneyDriver.EncounterAdapter encounter?new ControlledEncounter(server,entry.plan().transponder(),encounter):new Controlled(server,entry.plan().transponder(),delegate);
  var driver=new FreightJourneyDriver(journal,id,DestinationBoundJourneyAdapter.wrap(server,controlled));
  register();var result=driver.resume();if(result.state()==FreightJourneyDriver.State.RUNNING)runs.put(id,driver);return result;
 }
 public static int activeCount(MinecraftServer server){thread(server);return RUNS.getOrDefault(server,Map.of()).size();}
 /** Stopping never requires a present destination and never undocks/refunds. */
 public static boolean hold(MinecraftServer server,UUID id,String reason){
  thread(server);var runs=RUNS.get(server);var driver=runs==null?null:runs.remove(id);if(driver==null)return false;driver.hold(reason);return true;
 }
 private static void tick(MinecraftServer server){
  thread(server);var runs=RUNS.get(server);if(runs==null)return;
  for(var item:List.copyOf(runs.entrySet())){
   if(runs.get(item.getKey())!=item.getValue())continue;
   var result=item.getValue().tick(server.getTickCount());
   if(result.state()!=FreightJourneyDriver.State.RUNNING&&result.state()!=FreightJourneyDriver.State.ADVANCED)runs.remove(item.getKey(),item.getValue());
  }
 }
 private static void shutdown(MinecraftServer server){
  thread(server);var runs=RUNS.remove(server);if(runs!=null)for(var driver:runs.values())driver.hold("Server stopping; explicit fresh verification required");
 }
 private static class Controlled implements FreightJourneyDriver.Adapter {
  final MinecraftServer server;final UUID transponder;final FreightJourneyDriver.Adapter delegate;
  Controlled(MinecraftServer server,UUID transponder,FreightJourneyDriver.Adapter delegate){this.server=server;this.transponder=transponder;this.delegate=delegate;}
  public boolean enabled(){return !AutonomousShipControl.get(server).disabled(transponder)&&delegate.enabled();}
  public FreightJourneyDriver.Observation observe(Entry entry)throws Exception{return delegate.observe(entry);}
  public void step(Entry entry,Permit permit)throws Exception{delegate.step(entry,permit);}
  public void stop()throws Exception{delegate.stop();}
 }
 private static final class ControlledEncounter extends Controlled implements FreightJourneyDriver.EncounterAdapter {
  final FreightJourneyDriver.EncounterAdapter encounter;
  ControlledEncounter(MinecraftServer server,UUID transponder,FreightJourneyDriver.EncounterAdapter delegate){super(server,transponder,delegate);encounter=delegate;}
  public String prepareEncounter(Entry entry)throws Exception{return encounter.prepareEncounter(entry);}
  public FreightJourneyDriver.Observation applyEncounter(Entry entry,Permit permit)throws Exception{return encounter.applyEncounter(entry,permit);}
 }
}
