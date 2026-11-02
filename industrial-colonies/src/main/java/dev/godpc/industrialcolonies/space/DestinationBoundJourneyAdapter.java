package dev.godpc.industrialcolonies.space;

import java.util.Objects;
import net.minecraft.server.MinecraftServer;
import dev.godpc.industrialcolonies.space.FreightJourneyJournal.*;

/** Validate the immutable physical destination before delegating native work.
 * This adds no trajectory or propulsion and never replaces the adapter's cargo,
 * ownership, resource, coordinate-frame or arrival checks. */
public class DestinationBoundJourneyAdapter implements FreightJourneyDriver.Adapter {
 private final MinecraftServer server;
 private final FreightJourneyDriver.Adapter delegate;
 private DestinationBoundJourneyAdapter(MinecraftServer server,FreightJourneyDriver.Adapter delegate){
  this.server=Objects.requireNonNull(server);this.delegate=Objects.requireNonNull(delegate);
 }
 public static FreightJourneyDriver.Adapter wrap(MinecraftServer server,FreightJourneyDriver.Adapter delegate){
  return delegate instanceof FreightJourneyDriver.EncounterAdapter encounter?new Encounter(server,encounter):new DestinationBoundJourneyAdapter(server,delegate);
 }
 protected final void verify(Entry entry){
  var ref=FreightDestinationReference.decode(entry.plan().destinationRoute());ref.requirePlan(entry.plan());
  if(ref.body().equals(entry.body()))throw new IllegalStateException("Cargo body cannot also be its destination");
  NativeFreightDestination.resolve(server,ref,entry.plan().owner());
 }
 @Override public boolean enabled(){return delegate.enabled();}
 @Override public FreightJourneyDriver.Observation observe(Entry entry)throws Exception{
  verify(entry);var result=delegate.observe(entry);verify(entry);return result;
 }
 @Override public void step(Entry entry,Permit permit)throws Exception{verify(entry);delegate.step(entry,permit);}
 /** Always permit stopping even if the destination was destroyed or unloaded. */
 @Override public void stop()throws Exception{delegate.stop();}
 private static final class Encounter extends DestinationBoundJourneyAdapter implements FreightJourneyDriver.EncounterAdapter {
  private final FreightJourneyDriver.EncounterAdapter encounter;
  Encounter(MinecraftServer server,FreightJourneyDriver.EncounterAdapter delegate){super(server,delegate);encounter=delegate;}
  @Override public String prepareEncounter(Entry entry)throws Exception{verify(entry);String intent=encounter.prepareEncounter(entry);verify(entry);return intent;}
  @Override public FreightJourneyDriver.Observation applyEncounter(Entry entry,Permit permit)throws Exception{verify(entry);var result=encounter.applyEncounter(entry,permit);verify(entry);return result;}
 }
}
