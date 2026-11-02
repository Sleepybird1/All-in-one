package dev.godpc.industrialcolonies.space;

import java.io.IOException;
import java.util.*;
import dev.godpc.industrialcolonies.space.FreightJourneyJournal.*;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.sprocketgames.create_aeronautics_automated_logistics.dock.DockingConnectorDiscovery;

/** Planned zero-motion checkpoint of an already verified later phase. No file
 * is loaded or saved automatically and no body, cargo or actuator is changed.
 * Exact native saved-data equality deliberately refuses unclassified changes.
 * Active UNLOAD capture requires existing admission; recovery always stays held. */
public final class FreightHeldPhaseAudit {
 private FreightHeldPhaseAudit(){}
 private record NativeSnapshot(String head,OrbitalBodyAuthority.Snapshot sourceAuthority,OrbitalBodyAuthority.Snapshot targetAuthority,OrbitalBodyCustody.Snapshot sourceState,OrbitalBodyCustody.Snapshot targetState,long tick,OrbitalDistinctCoastState coasts,FreightHeldPose sourcePose,FreightHeldPose targetPose){
  String prefix(){return prefix(sourceAuthority.storedRecord(),targetAuthority.storedRecord());}
  String prefix(String sourceStorage,String targetStorage){return head+relocated(sourceAuthority,sourceStorage)+"\n"+relocated(targetAuthority,targetStorage)+"\n"+sourceState+"\n"+targetState+"\n";}
  String digest(){return FreightHeldPhaseRecord.hash(prefix()+sourcePose.canonical()+"\n"+targetPose.canonical());}
  String authenticatePose(FreightHeldPhaseCheckpoint saved){
   if(saved.sourcePose()==null)return digest();
   saved.sourcePose().verify(sourcePose);saved.targetPose().verify(targetPose);
   // Candidate historical poses are useful only if the complete original
   // native-state digest authenticates them in the subsequent journal check.
   String prefix=saved.sourceStorage()==null?prefix():prefix(saved.sourceStorage(),saved.targetStorage());
   return FreightHeldPhaseRecord.hash(prefix+saved.sourcePose().canonical()+"\n"+saved.targetPose().canonical());
  }
 }
 private static OrbitalBodyAuthority.Snapshot relocated(OrbitalBodyAuthority.Snapshot actual,String originalStorage){return new OrbitalBodyAuthority.Snapshot(actual.body(),actual.transponder(),actual.owner(),actual.transponderPosition(),actual.dimension(),originalStorage);}
 public static FreightHeldPhaseCheckpoint capture(MinecraftServer server,UUID journey)throws IOException{
  var journal=FreightJourneyControl.journal(server);var entry=journal.get(journey);
  var ref=FreightDestinationReference.decode(entry.plan().destinationRoute());
  // Check existing in-process authority before reading a new baseline.
  journal.prepareHeldPhaseRecovery(journey,entry.revision(),ref.body(),"0".repeat(64));
  var state=inspect(server,entry);require(journal.get(journey).equals(entry)&&journal.held(journey),"Held journal changed during capture");
  var phase=journal.prepareHeldPhaseRecovery(journey,entry.revision(),ref.body(),FreightHeldPhaseCheckpoint.bind(state.digest(),state.tick(),state.coasts()));
  return new FreightHeldPhaseCheckpoint(phase,state.tick(),state.coasts(),state.sourcePose(),state.targetPose(),state.sourceAuthority().storedRecord(),state.targetAuthority().storedRecord());
 }
 public static FreightHeldPhaseCheckpoint captureActiveUnload(MinecraftServer server,UUID journey)throws IOException{
  var journal=FreightJourneyControl.journal(server);var entry=journal.get(journey);
  var ref=FreightDestinationReference.decode(entry.plan().destinationRoute());
  journal.prepareActiveUnloadRecovery(journey,entry.revision(),ref.body(),"0".repeat(64));
  var state=inspect(server,entry,true,true);require(journal.get(journey).equals(entry),"Active journal changed during capture");
  var phase=journal.prepareActiveUnloadRecovery(journey,entry.revision(),ref.body(),FreightHeldPhaseCheckpoint.bind(state.digest(),state.tick(),state.coasts()));
  return new FreightHeldPhaseCheckpoint(phase,state.tick(),state.coasts(),state.sourcePose(),state.targetPose(),state.sourceAuthority().storedRecord(),state.targetAuthority().storedRecord(),true);
 }
 public static void verifyActiveUnload(MinecraftServer server,FreightHeldPhaseCheckpoint saved)throws IOException{
  var journal=FreightJourneyControl.journal(server);var entry=journal.get(saved.phase().journey());
  var target=FreightDestinationReference.decode(entry.plan().destinationRoute()).body();
  journal.prepareActiveUnloadRecovery(saved.phase().journey(),entry.revision(),target,"0".repeat(64));
  var state=inspect(server,entry,true,saved.pumpFlowSamples());saved.verifyCoast(state.tick(),state.coasts());
  require(journal.get(saved.phase().journey()).equals(entry)&&!journal.held(saved.phase().journey()),"Active journal changed during audit");
  saved.phase().verify(entry,entry.body(),target,FreightHeldPhaseCheckpoint.bind(state.authenticatePose(saved),saved.universeTick(),saved.coasts()));
 }
 public static Entry recover(MinecraftServer server,FreightHeldPhaseCheckpoint saved)throws IOException{
  return recover(server,saved,false);
 }
 public static Entry recoverUnflushedUnloadResume(MinecraftServer server,FreightHeldPhaseCheckpoint saved)throws IOException{
  return recover(server,saved,true);
 }
 private static Entry recover(MinecraftServer server,FreightHeldPhaseCheckpoint saved,boolean unflushedResume)throws IOException{
  Objects.requireNonNull(saved);var journal=FreightJourneyControl.journal(server);var entry=journal.get(saved.phase().journey());
  var state=inspect(server,entry,false,saved.pumpFlowSamples());saved.verifyCoast(state.tick(),state.coasts());require(journal.get(saved.phase().journey()).equals(entry)&&journal.held(saved.phase().journey()),"Held journal changed during native audit");
  var target=FreightDestinationReference.decode(entry.plan().destinationRoute()).body();String digest=FreightHeldPhaseCheckpoint.bind(state.authenticatePose(saved),saved.universeTick(),saved.coasts());
  return unflushedResume?journal.reconcileUnflushedUnloadResume(saved.phase(),entry.body(),target,digest):journal.reconcileHeldPhaseRecovery(saved.phase(),entry.body(),target,digest);
 }
 public static void verifyHeld(MinecraftServer server,FreightHeldPhaseCheckpoint saved)throws IOException{
  var entry=FreightJourneyControl.journal(server).get(saved.phase().journey());var state=inspect(server,entry,false,saved.pumpFlowSamples());saved.verifyCoast(state.tick(),state.coasts());
  require(FreightHeldPhaseCheckpoint.bind(state.authenticatePose(saved),saved.universeTick(),saved.coasts()).equals(saved.phase().nativeStateDigest()),"Original held native snapshot changed");
 }
 /** Read-only field breakdown for a refused checkpoint; never reconciles or
  * creates admission. Keep this output local because it identifies the bodies. */
 public static Map<String,String> diagnose(MinecraftServer server,FreightHeldPhaseCheckpoint saved)throws IOException{
  var state=inspect(server,FreightJourneyControl.journal(server).get(saved.phase().journey()),false,saved.pumpFlowSamples());
  var result=new LinkedHashMap<String,String>();result.put("prefix",state.prefix());result.put("sourcePose",state.sourcePose().canonical());result.put("targetPose",state.targetPose().canonical());
  result.put("expected",saved.phase().nativeStateDigest());result.put("currentExact",FreightHeldPhaseCheckpoint.bind(state.digest(),saved.universeTick(),saved.coasts()));
  if(saved.sourcePose()!=null){result.put("sourceWitness",saved.sourcePose().canonical());result.put("targetWitness",saved.targetPose().canonical());result.put("withWitness",FreightHeldPhaseCheckpoint.bind(state.authenticatePose(saved),saved.universeTick(),saved.coasts()));}
  return Map.copyOf(result);
 }
 private static NativeSnapshot inspect(MinecraftServer server,Entry entry)throws IOException{
  return inspect(server,entry,false,false);
 }
 private static NativeSnapshot inspect(MinecraftServer server,Entry entry,boolean activeUnload,boolean pumpFlowSamples)throws IOException{
  require(server.isSameThread(),"Current-phase audit requires server thread");var journal=FreightJourneyControl.journal(server);var plan=entry.plan();
  require(journal.fault().isEmpty()&&(activeUnload?!journal.held(plan.journey())&&entry.phase()==Phase.UNLOAD:journal.held(plan.journey()))&&journal.get(plan.journey()).equals(entry)&&entry.encounterIntent().isEmpty()
   &&(entry.phase()==Phase.APPROACH||entry.phase()==Phase.UNLOAD),"Exact held approach/unload required");
  var old=OrbitalDistinctCoastRecoveryRecord.decode(entry.encounterReceipt()).baseline();
  require(old.journey().equals(plan.journey())&&old.owner().equals(plan.owner())&&old.transponder().equals(plan.transponder())&&old.body().equals(entry.body())&&old.retiredSource().equals(plan.sourceBody())&&old.preparedRevision()<entry.revision(),"Retained receipt identity disagrees");
  var ref=FreightDestinationReference.decode(plan.destinationRoute());ref.requirePlan(plan);require(ref.body().equals(old.target()),"Exact original destination required");
  var resolved=NativeFreightDestination.resolve(server,ref,plan.owner());var ship=OrbitalEncounterCoordinator.body(server,entry.body());var target=resolved.body();
  var sourceAuthority=OrbitalBodyAuthority.read(ship,plan.transponder(),plan.owner(),plan.sourceBody());
  var targetAuthority=OrbitalBodyAuthority.read(target,old.targetTransponder(),plan.owner(),old.retiredTarget());
  OrbitalEncounterCoordinator.freeController(ship,sourceAuthority,false,true);OrbitalEncounterCoordinator.freeController(target,targetAuthority,false,true);
  require(!journal.unfinished(old.targetTransponder()),"Destination has another unfinished journey");
  var pair=OrbitalEndpointTelemetry.pair(server,ship.getUniqueId(),target.getUniqueId());
  require(pair.relation()==OrbitalEndpoint.Relation.SHARED_NATIVE_INSTANCE&&pair.ship().instance()==old.targetCell()&&pair.ship().timescale()==1&&pair.destination().timescale()==1,"Original receiving instance required");
  var members=OrbitalInstanceMembership.read(server,pair.ship());require(members.loadedBodies().equals(Set.of(ship.getUniqueId(),target.getUniqueId()))&&members.unloadedBodies().isEmpty()&&members.onlinePlayers().isEmpty()&&members.offlinePlayers().isEmpty(),"Exact empty receiving pair membership required");
  var data=dev.devce.rocketnautics.content.orbit.DeepSpaceData.getInstance(server);
  var cell=data.getInstance(pair.ship().instance());require(cell!=null&&cell.getPosition().getLocalUniverseTicks()==data.getUniverseTicks(),"Current native orbital clock required");
  var coasts=new OrbitalDistinctCoastState(pair.ship().celestialPosition(),pair.ship().celestialVelocity(),pair.destination().celestialPosition(),pair.destination().celestialVelocity(),pair.ship().mu());
  String coastState=pair.ship().dimension()+":"+pair.ship().frame()+":"+pair.ship().mu();
  var targetPort=resolved.blockEntity();var sourcePort=peer(targetPort);
  if(entry.phase()==Phase.UNLOAD){
   require(sourcePort!=null&&Sable.HELPER.getContaining(sourcePort)==ship&&peer(sourcePort)==targetPort
    &&DockingConnectorDiscovery.isLockedPair(ship.getLevel(),sourcePort.getBlockPos(),resolved.port()),"Exact reciprocal commissioned dock required");
   require(FreightDockFluidPolicy.allowed(sourcePort)==activeUnload&&FreightDockFluidPolicy.allowed(targetPort)==activeUnload&&FreightDockFluidPolicy.itemsAllowed(sourcePort)==activeUnload&&FreightDockFluidPolicy.itemsAllowed(targetPort)==activeUnload,"Both endpoints match audited transfer admission");
  }else require(sourcePort==null,"Partial approach capture requires a separately verified dock checkpoint");
  for(var body:List.of(ship,target)){
   var handle=RigidBodyHandle.of(body);require(handle.isValid()&&handle.getLinearVelocity().length()==0&&handle.getAngularVelocity().length()==0&&body.latestLinearVelocity.length()==0,"Checkpoint requires natural zero motion and history");
   OrbitalBodyQuiescence.controls(body);var queued=body.getQueuedForceGroups();int groups=0;
   if(queued!=null)for(var group:queued.values()){require(++groups<=256,"Bounded force audit");var force=group.getForceTotal();require(force.getLocalForce().length()==0&&force.getLocalTorque().length()==0,"No queued force or torque");}
   for(var actor:body.getPlot().getBlockEntityActors()){var dependencies=actor.sable$getConnectionDependencies();if(dependencies!=null)for(var other:dependencies)require(other==body||(entry.phase()==Phase.UNLOAD&&(other==ship||other==target)),"Unknown physical attachment");}
   int scanned=0;for(var entity:body.getLevel().getAllEntities()){require(++scanned<=4096,"Bounded entity audit");if(entity.isRemoved())continue;require(Sable.HELPER.getTrackingOrVehicleSubLevel(entity)!=body&&!entity.getBoundingBox().intersects(body.boundingBox().toMojang().inflate(.25)),"No passengers or intersecting entities");}
  }
  // Entire native block and block-entity state, including item/fluid components,
  // fuel and dock state. Only verified heartbeat/position caches are omitted.
  var sourceState=custody(ship,pumpFlowSamples);var targetState=custody(target,pumpFlowSamples);
  String head="IC_HELD_NATIVE_PAIR_V1\n"+ref.encode()+"\n"+entry.phase()+"\n"+pair.ship().instance()+"\n"+coastState+"\n";
  require(sourceState.equals(custody(ship,pumpFlowSamples))&&targetState.equals(custody(target,pumpFlowSamples)),"Native custody changed during checkpoint");
  return new NativeSnapshot(head,portableAuthority(server,sourceAuthority),portableAuthority(server,targetAuthority),sourceState,targetState,data.getUniverseTicks(),coasts,pose(ship),pose(target));
 }
 private static OrbitalBodyCustody.Snapshot custody(ServerSubLevel body,boolean pumpFlowSamples)throws IOException{return pumpFlowSamples?OrbitalBodyCustody.readForPoweredUnloadRecovery(body):OrbitalBodyCustody.readForEncounterRecovery(body);}
 private static FreightHeldPose pose(ServerSubLevel body){var p=body.logicalPose().position();var q=body.logicalPose().orientation();
  return new FreightHeldPose(p.x(),p.y(),p.z(),q.x(),q.y(),q.z(),q.w());
 }
 private static OrbitalBodyAuthority.Snapshot portableAuthority(MinecraftServer server,OrbitalBodyAuthority.Snapshot snapshot)throws IOException{
  String record=snapshot.storedRecord();int separator=record.lastIndexOf('#');require(separator>0&&record.substring(separator+1).matches("[0-9]+"),"Verified native storage slot required");
  var root=server.getWorldPath(net.minecraft.world.level.storage.LevelResource.ROOT).toRealPath();var file=java.nio.file.Path.of(record.substring(0,separator)).toRealPath();
  require(file.startsWith(root),"Stored authority must remain in this world");
  // Preserve the exact file/slot within the save, while allowing an intact
  // explicitly copied test world to live under a different outer folder.
  String relative=root.relativize(file).toString().replace('\\','/')+record.substring(separator);
  return new OrbitalBodyAuthority.Snapshot(snapshot.body(),snapshot.transponder(),snapshot.owner(),snapshot.transponderPosition(),snapshot.dimension(),relative);
 }
 private static BlockEntity peer(BlockEntity dock){try{Object p=dock.getClass().getMethod("getOtherConnector").invoke(dock);require(p==null||p instanceof BlockEntity,"Supported dock peer");return (BlockEntity)p;}catch(ReflectiveOperationException e){throw new IllegalStateException("Native dock unavailable",e);}}
 private static void require(boolean valid,String message){if(!valid)throw new IllegalStateException(message);}
}
