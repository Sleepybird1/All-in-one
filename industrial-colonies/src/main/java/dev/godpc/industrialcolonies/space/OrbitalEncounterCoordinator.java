package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.godpc.industrialcolonies.space.FreightJourneyJournal.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.godpc.industrialcolonies.space.station.StationLifeSupport;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import net.minecraft.server.MinecraftServer;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import net.sprocketgames.create_aeronautics_automated_logistics.service.AutomatedLogisticsServices;
import org.joml.Quaterniond;
import org.joml.Vector3d;

/** Same-thread, stationary native frame conversion behind a durable journey
 * intent. No cell claim/retirement, orbital-state write, cargo reconstruction,
 * velocity impulse or propulsion. Moving native frame conversion is deliberately
 * refused until its precision/history behavior has separate acceptance.
 * This is a component of a native journey adapter, not a saved flight controller.
 */
public final class OrbitalEncounterCoordinator {
 private OrbitalEncounterCoordinator(){}
 private record Rotation(double x,double y,double z,double w){}
 private record Facts(OrbitalEncounterPlanner.Proposal proposal,OrbitalBodyQuiescence.Snapshot source,
   OrbitalBodyQuiescence.Snapshot target,OrbitalBodyAuthority.Snapshot sourceAuthority,
   OrbitalBodyAuthority.Snapshot targetAuthority,Rotation sourceRotation,Rotation targetRotation,V receivingPosition){}
 public static final class Prepared {
  private final MinecraftServer server;private final Entry entry;private final UUID target,transponder,retiredBody;private final Facts facts;private final String intent;private final boolean coastAgreement;
  private Prepared(MinecraftServer server,Entry entry,UUID target,UUID transponder,UUID retiredBody,Facts facts)throws IOException{
   this(server,entry,target,transponder,retiredBody,facts,false);
  }
  private Prepared(MinecraftServer server,Entry entry,UUID target,UUID transponder,UUID retiredBody,Facts facts,boolean coastAgreement)throws IOException{
   this.coastAgreement=coastAgreement;
   this.server=server;this.entry=entry;this.target=target;this.transponder=transponder;this.retiredBody=retiredBody;this.facts=facts;
   var source=body(server,entry.body());var receiver=body(server,target);var pair=facts.proposal().observation();
   var record=new OrbitalEncounterRecoveryRecord(entry.plan().journey(),entry.plan().owner(),entry.body(),target,entry.plan().transponder(),transponder,entry.plan().sourceBody(),retiredBody,
     entry.revision(),server.getTickCount(),pair.ship().instance(),pair.destination().instance(),pair.ship().dimension(),pair.ship().frame(),vector(source),facts.receivingPosition(),vector(receiver),
     recoveryRotation(facts.sourceRotation()),recoveryRotation(facts.targetRotation()),OrbitalBodyCustody.readForEncounterRecovery(source).digest(),OrbitalBodyCustody.readForEncounterRecovery(receiver).digest());
   if(coastAgreement){var certificate=coastAgreement(server,pair);
    this.intent=new OrbitalCoastRecoveryRecord(record,DeepSpaceData.getInstance(server).getUniverseTicks(),certificate.positionBound(),certificate.velocityBound(),digest(entry.plan().destinationRoute())).encode();
   }else this.intent=record.encode();
  }
  public String intent(){return intent;}
 }
 private static void require(boolean ok,String why){if(!ok)throw new IllegalStateException(why);}
 static ServerSubLevel body(MinecraftServer server,UUID id){
  var level=server.getLevel(StationLifeSupport.DEEP_SPACE);require(level!=null,"Orbital dimension unavailable");
  var container=SubLevelContainer.getContainer(level);var found=container==null?null:container.getSubLevel(id);
  require(found instanceof ServerSubLevel&&!found.isRemoved(),"Original orbital body unavailable");return (ServerSubLevel)found;
 }
 private static Rotation rotation(ServerSubLevel body){var q=body.logicalPose().orientation();return new Rotation(q.x(),q.y(),q.z(),q.w());}
 private static OrbitalEncounterRecoveryRecord.Rotation recoveryRotation(Rotation q){return new OrbitalEncounterRecoveryRecord.Rotation(q.x(),q.y(),q.z(),q.w());}
 private static V vector(ServerSubLevel body){var p=body.logicalPose().position();return new V(p.x(),p.y(),p.z());}
 private static double radius(ServerSubLevel body){
  var b=body.boundingBox().toMojang();var p=body.logicalPose().position();
  double x=Math.max(Math.abs(b.minX-p.x()),Math.abs(b.maxX-p.x())),y=Math.max(Math.abs(b.minY-p.y()),Math.abs(b.maxY-p.y())),z=Math.max(Math.abs(b.minZ-p.z()),Math.abs(b.maxZ-p.z()));return Math.sqrt(x*x+y*y+z*z);
 }
 private static void freeController(ServerSubLevel body,OrbitalBodyAuthority.Snapshot authority){freeController(body,authority,true);}
 static void freeController(ServerSubLevel body,OrbitalBodyAuthority.Snapshot authority,boolean requireEnabled){
  freeController(body,authority,requireEnabled,false);
 }
 static void freeController(ServerSubLevel body,OrbitalBodyAuthority.Snapshot authority,boolean requireEnabled,boolean allowStoppedSession){
  var server=body.getLevel().getServer();var id=authority.transponder();
  require(!requireEnabled||!AutonomousShipControl.get(server).disabled(id),"Operator disabled encounter participant");
  var t=(ShipTransponderBlockEntity)body.getLevel().getBlockEntity(authority.transponderPosition());
  require(!t.scheduleActive()&&!t.dockOutputActive()&&t.dockOutputOwner().isEmpty(),"Native controller still owns encounter participant");
  require(AutomatedLogisticsServices.SCHEDULES.runtimeScheduleSummaries().stream().noneMatch(s->s.transponderId().equals(id)),"Native schedule still active");
  require(AutomatedLogisticsServices.PLAYBACK.runtimePlaybackSummaries(server).stream().noneMatch(s->s.transponderId().equals(Optional.of(id))||s.vehicleId().equals(Optional.of(body.getUniqueId()))),"Native playback still active");
  require(AutomatedLogisticsServices.DOCK_RESERVATIONS.snapshots().stream().noneMatch(r->java.util.stream.Stream.concat(r.holder().stream(),r.waiting().stream()).anyMatch(s->s.transponderId().equals(Optional.of(id)))),"Native dock reservation remains held or queued");
  var session=RendezvousService.snapshot(server,body.getUniqueId());
  require(session.isEmpty()||(allowStoppedSession&&session.orElseThrow().state().equals("STOPPED")),"Rendezvous session still owns encounter participant");
 }
 private static Facts inspect(MinecraftServer server,Entry entry,UUID targetId,UUID targetTransponder,UUID targetRetired)throws IOException{
  return inspect(server,entry,targetId,targetTransponder,targetRetired,null);
 }
 private static Facts inspect(MinecraftServer server,Entry entry,UUID targetId,UUID targetTransponder,UUID targetRetired,List<OrbitalCommonMotionProof.Sample> motion)throws IOException{
  return inspect(server,entry,targetId,targetTransponder,targetRetired,motion,false);
 }
 private static Facts inspect(MinecraftServer server,Entry entry,UUID targetId,UUID targetTransponder,UUID targetRetired,List<OrbitalCommonMotionProof.Sample> motion,boolean relative)throws IOException{
  return inspect(server,entry,targetId,targetTransponder,targetRetired,motion,relative,false);
 }
 private static Facts inspect(MinecraftServer server,Entry entry,UUID targetId,UUID targetTransponder,UUID targetRetired,List<OrbitalCommonMotionProof.Sample> motion,boolean relative,boolean coast)throws IOException{
  return inspect(server,entry,targetId,targetTransponder,targetRetired,motion,relative,coast,false);
 }
 private static Facts inspect(MinecraftServer server,Entry entry,UUID targetId,UUID targetTransponder,UUID targetRetired,List<OrbitalCommonMotionProof.Sample> motion,boolean relative,boolean coast,boolean distinct)throws IOException{
  require(server.isSameThread(),"Encounter requires server thread");
  require(entry.phase()==Phase.ORBIT&&entry.plan().destinationDimension().equals(StationLifeSupport.DEEP_SPACE.location().toString()),"Journey is not in its planned orbital dimension");
  var ship=body(server,entry.body());var target=body(server,targetId);
  var sourceAuthority=OrbitalBodyAuthority.read(ship,entry.plan().transponder(),entry.plan().owner(),entry.plan().sourceBody());
  var targetAuthority=OrbitalBodyAuthority.read(target,targetTransponder,entry.plan().owner(),targetRetired);
  freeController(ship,sourceAuthority);freeController(target,targetAuthority);
  require(!FreightJourneyControl.journal(server).unfinished(targetTransponder),"Destination has another unfinished journey");
  var source=OrbitalBodyQuiescence.read(ship);var destination=OrbitalBodyQuiescence.read(target);
  var pair=OrbitalEndpointTelemetry.pair(server,entry.body(),targetId);
  require(pair.relation()==OrbitalEndpoint.Relation.INDEPENDENT_NATIVE_INSTANCES,"Encounter already shares one native cell");
  require(OrbitalInstanceMembership.read(server,pair.ship()).soleLoadedBodyWithoutPlayers(entry.body()),"Source cell contains another body or player");
  require(OrbitalInstanceMembership.read(server,pair.destination()).soleLoadedBodyWithoutPlayers(targetId),"Destination cell contains another body or player");
  var data=DeepSpaceData.getInstance(server);var targetCell=data.getInstance(pair.destination().instance());
  var offset=pair.ship().celestialPosition().sub(pair.destination().celestialPosition()).add(pair.ship().localOffset());
  var c=targetCell.getCenter();var receiving=new V(c.x(),c.y(),c.z()).add(offset);
  var velocity=pair.ship().celestialVelocity().sub(pair.destination().celestialVelocity()).add(pair.ship().localVelocity());
  require(RigidBodyHandle.of(ship).getAngularVelocity().length()==0&&RigidBodyHandle.of(target).getAngularVelocity().length()==0,"Rotating native frame conversion remains unqualified");
  if(distinct){
   require(!relative&&!coast,"Distinct coast profile must be exclusive");var proof=OrbitalDistinctCoastProof.verify(motion);
   require(proof.latest().equals(pair)&&proof.receivingVelocity().equals(velocity),"Exact current distinct-coast proof required");
   var ref=FreightDestinationReference.decode(entry.plan().destinationRoute());ref.requirePlan(entry.plan());
   require(ref.body().equals(targetId)&&NativeFreightDestination.resolve(server,ref,entry.plan().owner()).body()==target,"Distinct-coast destination must match committed dock");
   require(offset.length()+ship.boundingBox().size().length()+.25+velocity.length()*.5<targetCell.getSideLength()/2.0,"Distinct coast receiving coupling margin too small");
  }else if(coast){
   require(motion==null&&!relative&&pair.ship().localVelocity().length()==0&&pair.destination().localVelocity().length()==0,"Coast agreement requires stationary local bodies");
   coastAgreement(server,pair);
   var ref=FreightDestinationReference.decode(entry.plan().destinationRoute());ref.requirePlan(entry.plan());
   require(ref.body().equals(targetId)&&NativeFreightDestination.resolve(server,ref,entry.plan().owner()).body()==target,"Coast destination must match committed physical dock");
  }
  else if(motion==null)require(pair.ship().localVelocity().length()==0&&pair.destination().localVelocity().length()==0&&velocity.length()==0,"Only qualified stationary native frame conversion is admitted");
  else{
   if(relative){var proof=OrbitalRelativeMotionProof.verify(motion);require(proof.latest().equals(pair)&&proof.sourceVelocity().equals(velocity),"Exact current relative-motion proof required");}
   else{var proof=OrbitalCommonMotionProof.verify(motion);require(proof.latest().equals(pair)&&proof.commonVelocity().equals(velocity),"Exact current common-motion proof required");}
   var ref=FreightDestinationReference.decode(entry.plan().destinationRoute());ref.requirePlan(entry.plan());
   require(ref.body().equals(targetId)&&NativeFreightDestination.resolve(server,ref,entry.plan().owner()).body()==target,"Common-motion destination must match committed physical dock");
  }
  require(pair.ship().surfaceDistance()>pair.ship().transitionHeight()+100&&pair.destination().surfaceDistance()>pair.destination().transitionHeight()+100,"Native planetary transition too close");
  var clearance=OrbitalReceivingClearance.check(ship,receiving,velocity);require(clearance.clear(),"Receiving footprint refused: "+clearance.reason());
  var proposal=OrbitalEncounterPlanner.propose(pair.ship(),pair.destination(),new OrbitalEncounterPlanner.Envelope(radius(ship),radius(target),targetCell.getSideLength()/2.0),new OrbitalEncounterPlanner.Eligibility(true,true,true,true,true,true));
  OrbitalEncounterMotionCheck.verify(server,proposal);
  return new Facts(proposal,source,destination,sourceAuthority,targetAuthority,rotation(ship),rotation(target),receiving);
 }
 private static OrbitalCoastAgreement.Certificate coastAgreement(MinecraftServer server,OrbitalEndpoint.Pair pair){
  var data=DeepSpaceData.getInstance(server);var a=data.getInstance(pair.ship().instance()).getPosition();var b=data.getInstance(pair.destination().instance()).getPosition();
  require(a.getLocalUniverseTicks()==b.getLocalUniverseTicks()&&a.getLocalUniverseTicks()==data.getUniverseTicks()&&a.getTimescale()==1&&b.getTimescale()==1,"Current synchronized unit-rate coast clocks required");
  return OrbitalCoastAgreement.certify(new dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit(a.getCurrentOrbit()),new dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit(b.getCurrentOrbit()),180);
 }
 /** Separate distinct-orbit path. Velocity conversion preserves inertial motion;
  * it is never a requested course correction or propulsion command. */
 public static final class PreparedDistinct {
  private final MinecraftServer server;private final Entry entry;private final UUID target,transponder,retired;
  private final Facts facts;private final List<OrbitalCommonMotionProof.Sample> samples;private final String intent;
  private PreparedDistinct(MinecraftServer server,Entry entry,UUID target,UUID transponder,UUID retired,Facts facts,List<OrbitalCommonMotionProof.Sample> samples)throws IOException{
   this.server=server;this.entry=entry;this.target=target;this.transponder=transponder;this.retired=retired;this.facts=facts;this.samples=List.copyOf(samples);
   var ship=body(server,entry.body());var receiver=body(server,target);var pair=facts.proposal().observation();
   var baseline=new OrbitalEncounterRecoveryRecord(entry.plan().journey(),entry.plan().owner(),entry.body(),target,entry.plan().transponder(),transponder,entry.plan().sourceBody(),retired,entry.revision(),server.getTickCount(),pair.ship().instance(),pair.destination().instance(),pair.ship().dimension(),pair.ship().frame(),vector(ship),facts.receivingPosition(),vector(receiver),recoveryRotation(facts.sourceRotation()),recoveryRotation(facts.targetRotation()),OrbitalBodyCustody.readForDistinctCoastRecovery(ship).digest(),OrbitalBodyCustody.readForDistinctCoastRecovery(receiver).digest());
   var coasts=new OrbitalDistinctCoastState(pair.ship().celestialPosition(),pair.ship().celestialVelocity(),pair.destination().celestialPosition(),pair.destination().celestialVelocity(),pair.ship().mu());
   intent=new OrbitalDistinctCoastRecoveryRecord(baseline,facts.proposal().receivingVelocity(),pair.ship().universeTick(),digest(samples.toString()),digest(entry.plan().destinationRoute()),coasts).encode();
  }
  public String intent(){return intent;}
 }
 public static PreparedDistinct prepareDistinct(MinecraftServer server,Entry entry,UUID target,UUID targetTransponder,UUID retiredTarget,List<OrbitalCommonMotionProof.Sample> samples)throws IOException{
  require(server.isSameThread(),"Encounter requires server thread");var journal=FreightJourneyControl.journal(server);
  require(journal.fault().isEmpty()&&!journal.held(entry.plan().journey())&&journal.get(entry.plan().journey()).equals(entry)&&entry.encounterIntent().isEmpty(),"Current admitted distinct-coast journey required");
  return new PreparedDistinct(server,entry,target,targetTransponder,retiredTarget,inspect(server,entry,target,targetTransponder,retiredTarget,samples,false,false,true),samples);
 }
 public static FreightJourneyDriver.Observation applyDistinct(PreparedDistinct p,Entry pending,Permit permit)throws IOException{
  Objects.requireNonNull(p);var server=p.server;require(server.isSameThread(),"Encounter requires server thread");var journal=FreightJourneyControl.journal(server);
  require(journal.admits(permit)&&permit.journey().equals(p.entry.plan().journey())&&journal.get(permit.journey()).equals(pending)&&pending.plan().equals(p.entry.plan())&&pending.body().equals(p.entry.body())&&pending.revision()==p.entry.revision()+1&&pending.encounterIntent().equals(p.intent),"Exact durable distinct-coast intent and permit required");
  require(p.facts.equals(inspect(server,pending,p.target,p.transponder,p.retired,p.samples,false,false,true)),"Distinct coast changed since preparation");
  var ship=body(server,pending.body());var target=body(server,p.target);var f=p.facts;var position=f.receivingPosition();var q=f.sourceRotation();var before=f.proposal().observation();
  var handle=RigidBodyHandle.of(ship);handle.teleport(new Vector3d(position.x(),position.y(),position.z()),new Quaterniond(q.x(),q.y(),q.z(),q.w()));ship.updateLastPose();ship.forceUpdateGlobalBounds();
  var after=OrbitalEndpointTelemetry.pair(server,pending.body(),p.target);
  require(after.relation()==OrbitalEndpoint.Relation.SHARED_NATIVE_INSTANCE&&after.destination().equals(before.destination()),"Distinct coast receiving cell changed");
  V delta=before.ship().celestialVelocity().add(before.ship().localVelocity()).sub(after.ship().celestialVelocity()).sub(after.ship().localVelocity());
  require(delta.length()<=.08,"Frame velocity conversion exceeds qualified envelope");
  handle.addLinearAndAngularVelocity(new Vector3d(delta.x(),delta.y(),delta.z()),new Vector3d());
  after=OrbitalEndpointTelemetry.pair(server,pending.body(),p.target);
  require(after.ship().celestialPosition().sub(before.ship().celestialPosition()).add(after.ship().localOffset().sub(before.ship().localOffset())).length()<=1e-3&&after.ship().celestialVelocity().sub(before.ship().celestialVelocity()).add(after.ship().localVelocity().sub(before.ship().localVelocity())).length()<=1e-6,"Distinct coast physical state changed");
  require(rotation(ship).equals(f.sourceRotation())&&rotation(target).equals(f.targetRotation())&&handle.getAngularVelocity().length()==0,"Distinct coast rotation changed");
  require(OrbitalBodyCustody.read(ship).equals(f.source().custody())&&OrbitalBodyCustody.read(target).equals(f.target().custody()),"Distinct coast custody changed");
  require(journal.admits(permit)&&!AutonomousShipControl.get(server).disabled(pending.plan().transponder()),"Distinct coast permission changed");
  return new FreightJourneyDriver.Observation(pending.body(),digest(p.intent+"\nVERIFIED_DISTINCT_COAST\n"+after),true,"");
 }
 /** Separate experimental common-motion path. Stationary entry points and old
  * receipts retain their original interpretation. No velocity impulse is used. */
 public static final class PreparedCommon {
  private final MinecraftServer server;private final Entry entry;private final UUID target,transponder,retired;
  private final Facts facts;private final List<OrbitalCommonMotionProof.Sample> samples;private final String intent;
  private PreparedCommon(MinecraftServer server,Entry entry,UUID target,UUID transponder,UUID retired,Facts facts,List<OrbitalCommonMotionProof.Sample> samples)throws IOException{
   this.server=server;this.entry=entry;this.target=target;this.transponder=transponder;this.retired=retired;this.facts=facts;this.samples=List.copyOf(samples);
   var ship=body(server,entry.body());var receiver=body(server,target);var pair=facts.proposal().observation();
   var baseline=new OrbitalEncounterRecoveryRecord(entry.plan().journey(),entry.plan().owner(),entry.body(),target,entry.plan().transponder(),transponder,entry.plan().sourceBody(),retired,entry.revision(),server.getTickCount(),pair.ship().instance(),pair.destination().instance(),pair.ship().dimension(),pair.ship().frame(),vector(ship),facts.receivingPosition(),vector(receiver),recoveryRotation(facts.sourceRotation()),recoveryRotation(facts.targetRotation()),OrbitalBodyCustody.readForCommonMotionRecovery(ship).digest(),OrbitalBodyCustody.readForCommonMotionRecovery(receiver).digest());
   intent=new OrbitalCommonMotionRecoveryRecord(baseline,pair.ship().localVelocity(),dev.devce.rocketnautics.content.orbit.DeepSpaceData.getInstance(server).getUniverseTicks(),digest(samples.toString())).encode();
  }
  public String intent(){return intent;}
 }
 public static PreparedCommon prepareCommon(MinecraftServer server,Entry entry,UUID target,UUID targetTransponder,UUID retiredTarget,List<OrbitalCommonMotionProof.Sample> samples)throws IOException{
  require(server.isSameThread(),"Encounter requires server thread");var journal=FreightJourneyControl.journal(server);
  require(journal.fault().isEmpty()&&!journal.held(entry.plan().journey())&&journal.get(entry.plan().journey()).equals(entry)&&entry.encounterIntent().isEmpty(),"Current admitted common-motion journey required");
  return new PreparedCommon(server,entry,target,targetTransponder,retiredTarget,inspect(server,entry,target,targetTransponder,retiredTarget,samples),samples);
 }
 public static FreightJourneyDriver.Observation applyCommon(PreparedCommon p,Entry pending,Permit permit)throws IOException{
  Objects.requireNonNull(p);var server=p.server;require(server.isSameThread(),"Encounter requires server thread");var journal=FreightJourneyControl.journal(server);
  require(journal.admits(permit)&&permit.journey().equals(p.entry.plan().journey())&&journal.get(permit.journey()).equals(pending)&&pending.plan().equals(p.entry.plan())&&pending.body().equals(p.entry.body())&&pending.revision()==p.entry.revision()+1&&pending.encounterIntent().equals(p.intent),"Exact durable common-motion intent and permit required");
  require(p.facts.equals(inspect(server,pending,p.target,p.transponder,p.retired,p.samples)),"Common-motion facts changed since preparation");
  var ship=body(server,pending.body());var target=body(server,p.target);var f=p.facts;var position=f.receivingPosition();var q=f.sourceRotation();
  RigidBodyHandle.of(ship).teleport(new Vector3d(position.x(),position.y(),position.z()),new Quaterniond(q.x(),q.y(),q.z(),q.w()));ship.updateLastPose();ship.forceUpdateGlobalBounds();
  var before=f.proposal().observation();var after=OrbitalEndpointTelemetry.pair(server,pending.body(),p.target);
  require(after.relation()==OrbitalEndpoint.Relation.SHARED_NATIVE_INSTANCE&&after.destination().equals(before.destination()),"Receiving common-motion frame changed unexpectedly");
  require(after.ship().celestialPosition().sub(before.ship().celestialPosition()).add(after.ship().localOffset().sub(before.ship().localOffset())).length()<=1e-3&&after.ship().celestialVelocity().sub(before.ship().celestialVelocity()).add(after.ship().localVelocity().sub(before.ship().localVelocity())).length()<=1e-6,"Common-motion conversion changed celestial state");
  require(rotation(ship).equals(f.sourceRotation())&&rotation(target).equals(f.targetRotation())&&RigidBodyHandle.of(ship).getAngularVelocity().length()==0,"Common-motion orientation changed");
  require(OrbitalBodyCustody.read(ship).equals(f.source().custody())&&OrbitalBodyCustody.read(target).equals(f.target().custody()),"Common-motion body custody changed");
  require(journal.admits(permit)&&!AutonomousShipControl.get(server).disabled(pending.plan().transponder()),"Common-motion admission changed before verification");
  return new FreightJourneyDriver.Observation(pending.body(),digest(p.intent+"\nVERIFIED_COMMON_MOTION\n"+after),true,"");
 }
 /** Separate relative-motion schema; never reinterpret stationary/common receipts. */
 public static final class PreparedRelative {
  private final MinecraftServer server;private final Entry entry;private final UUID target,transponder,retired;
  private final Facts facts;private final List<OrbitalCommonMotionProof.Sample> samples;private final String intent;
  private PreparedRelative(MinecraftServer server,Entry entry,UUID target,UUID transponder,UUID retired,Facts facts,List<OrbitalCommonMotionProof.Sample> samples)throws IOException{
   this.server=server;this.entry=entry;this.target=target;this.transponder=transponder;this.retired=retired;this.facts=facts;this.samples=List.copyOf(samples);
   var ship=body(server,entry.body());var receiver=body(server,target);var pair=facts.proposal().observation();
   var baseline=new OrbitalEncounterRecoveryRecord(entry.plan().journey(),entry.plan().owner(),entry.body(),target,entry.plan().transponder(),transponder,entry.plan().sourceBody(),retired,entry.revision(),server.getTickCount(),pair.ship().instance(),pair.destination().instance(),pair.ship().dimension(),pair.ship().frame(),vector(ship),facts.receivingPosition(),vector(receiver),recoveryRotation(facts.sourceRotation()),recoveryRotation(facts.targetRotation()),OrbitalBodyCustody.readForCommonMotionRecovery(ship).digest(),OrbitalBodyCustody.readForCommonMotionRecovery(receiver).digest());
   intent=new OrbitalRelativeMotionRecoveryRecord(baseline,pair.ship().localVelocity(),pair.destination().localVelocity(),DeepSpaceData.getInstance(server).getUniverseTicks(),digest(samples.toString())).encode();
  }
  public String intent(){return intent;}
 }
 public static PreparedRelative prepareRelative(MinecraftServer server,Entry entry,UUID target,UUID targetTransponder,UUID retiredTarget,List<OrbitalCommonMotionProof.Sample> samples)throws IOException{
  require(server.isSameThread(),"Encounter requires server thread");var journal=FreightJourneyControl.journal(server);
  require(journal.fault().isEmpty()&&!journal.held(entry.plan().journey())&&journal.get(entry.plan().journey()).equals(entry)&&entry.encounterIntent().isEmpty(),"Current admitted relative-motion journey required");
  return new PreparedRelative(server,entry,target,targetTransponder,retiredTarget,inspect(server,entry,target,targetTransponder,retiredTarget,samples,true),samples);
 }
 public static FreightJourneyDriver.Observation applyRelative(PreparedRelative p,Entry pending,Permit permit)throws IOException{
  Objects.requireNonNull(p);var server=p.server;require(server.isSameThread(),"Encounter requires server thread");var journal=FreightJourneyControl.journal(server);
  require(journal.admits(permit)&&permit.journey().equals(p.entry.plan().journey())&&journal.get(permit.journey()).equals(pending)&&pending.plan().equals(p.entry.plan())&&pending.body().equals(p.entry.body())&&pending.revision()==p.entry.revision()+1&&pending.encounterIntent().equals(p.intent),"Exact durable relative-motion intent and permit required");
  require(p.facts.equals(inspect(server,pending,p.target,p.transponder,p.retired,p.samples,true)),"Relative-motion facts changed since preparation");
  var ship=body(server,pending.body());var target=body(server,p.target);var f=p.facts;var position=f.receivingPosition();var q=f.sourceRotation();
  RigidBodyHandle.of(ship).teleport(new Vector3d(position.x(),position.y(),position.z()),new Quaterniond(q.x(),q.y(),q.z(),q.w()));ship.updateLastPose();ship.forceUpdateGlobalBounds();
  var before=f.proposal().observation();var after=OrbitalEndpointTelemetry.pair(server,pending.body(),p.target);
  require(after.relation()==OrbitalEndpoint.Relation.SHARED_NATIVE_INSTANCE&&after.destination().equals(before.destination()),"Receiving relative-motion frame changed unexpectedly");
  require(after.ship().celestialPosition().sub(before.ship().celestialPosition()).add(after.ship().localOffset().sub(before.ship().localOffset())).length()<=1e-3&&after.ship().celestialVelocity().sub(before.ship().celestialVelocity()).add(after.ship().localVelocity().sub(before.ship().localVelocity())).length()<=1e-6,"Relative-motion conversion changed celestial state");
  require(rotation(ship).equals(f.sourceRotation())&&rotation(target).equals(f.targetRotation())&&RigidBodyHandle.of(ship).getAngularVelocity().length()==0,"Relative-motion orientation changed");
  require(OrbitalBodyCustody.read(ship).equals(f.source().custody())&&OrbitalBodyCustody.read(target).equals(f.target().custody()),"Relative-motion body custody changed");
  require(journal.admits(permit)&&!AutonomousShipControl.get(server).disabled(pending.plan().transponder()),"Relative-motion admission changed before verification");
  return new FreightJourneyDriver.Observation(pending.body(),digest(p.intent+"\nVERIFIED_RELATIVE_MOTION\n"+after),true,"");
 }
 public static Prepared prepare(MinecraftServer server,Entry entry,UUID target,UUID targetTransponder,UUID targetRetired)throws IOException{
  require(server.isSameThread(),"Encounter requires server thread");var journal=FreightJourneyControl.journal(server);
  require(journal.fault().isEmpty()&&!journal.held(entry.plan().journey())&&journal.get(entry.plan().journey()).equals(entry)&&entry.encounterIntent().isEmpty(),"Current explicitly admitted journey required");
  return new Prepared(server,entry,target,targetTransponder,targetRetired,inspect(server,entry,target,targetTransponder,targetRetired));
 }
 /** Opt-in stationary profile for independently reconstructed coasts. The native
  * velocity is not rewritten; any celestial rounding difference must fit the
  * explicit 1e-6 velocity and 0.5mm predicted-position numerical budget. */
 public static Prepared prepareCoastAgreement(MinecraftServer server,Entry entry,UUID target,UUID targetTransponder,UUID targetRetired)throws IOException{
  require(server.isSameThread(),"Encounter requires server thread");var journal=FreightJourneyControl.journal(server);
  require(journal.fault().isEmpty()&&!journal.held(entry.plan().journey())&&journal.get(entry.plan().journey()).equals(entry)&&entry.encounterIntent().isEmpty(),"Current explicitly admitted journey required");
  return new Prepared(server,entry,target,targetTransponder,targetRetired,inspect(server,entry,target,targetTransponder,targetRetired,null,false,true),true);
 }
 public static FreightJourneyDriver.Observation apply(Prepared prepared,Entry pending,Permit permit)throws IOException{
  Objects.requireNonNull(prepared);var server=prepared.server;require(server.isSameThread(),"Encounter requires server thread");
  var journal=FreightJourneyControl.journal(server);
  require(journal.admits(permit)&&permit.journey().equals(prepared.entry.plan().journey())&&journal.get(permit.journey()).equals(pending)
    &&pending.plan().equals(prepared.entry.plan())&&pending.body().equals(prepared.entry.body())
    &&pending.revision()==prepared.entry.revision()+1&&pending.encounterIntent().equals(prepared.intent),"Exact durable encounter intent and current permit required");
  require(prepared.facts.equals(inspect(server,pending,prepared.target,prepared.transponder,prepared.retiredBody,null,false,prepared.coastAgreement)),"Native encounter changed since preparation");
  var ship=body(server,pending.body());var target=body(server,prepared.target);var f=prepared.facts;var p=f.receivingPosition();var q=f.sourceRotation();
  // No work that may yield or invoke external callbacks between final preflight
  // and this native operation. The original source cell remains available for
  // uncertain crash recovery; it is not retired by this coordinator.
  RigidBodyHandle.of(ship).teleport(new Vector3d(p.x(),p.y(),p.z()),new Quaterniond(q.x(),q.y(),q.z(),q.w()));
  ship.updateLastPose();ship.forceUpdateGlobalBounds();
  var after=OrbitalEndpointTelemetry.pair(server,pending.body(),prepared.target);var before=f.proposal().observation();
  require(after.relation()==OrbitalEndpoint.Relation.SHARED_NATIVE_INSTANCE&&after.destination().equals(before.destination()),"Receiving frame or destination changed unexpectedly");
  require(after.ship().celestialPosition().sub(before.ship().celestialPosition()).add(after.ship().localOffset().sub(before.ship().localOffset())).length()<=1e-3
    &&after.ship().celestialVelocity().sub(before.ship().celestialVelocity()).add(after.ship().localVelocity().sub(before.ship().localVelocity())).length()<=1e-6,"Frame conversion changed physical celestial state");
  require(rotation(ship).equals(f.sourceRotation())&&rotation(target).equals(f.targetRotation())&&RigidBodyHandle.of(ship).getAngularVelocity().length()==0,"Orientation or angular motion changed");
  require(OrbitalBodyCustody.read(ship).equals(f.source().custody())&&OrbitalBodyCustody.read(target).equals(f.target().custody()),"Complete ship or receiver custody changed during frame conversion");
  require(journal.admits(permit)&&!AutonomousShipControl.get(server).disabled(pending.plan().transponder()),"Encounter permission changed before verification");
  return new FreightJourneyDriver.Observation(pending.body(),digest(prepared.intent+"\nVERIFIED\n"+after),true,"");
 }
 /** Explicit read-only physical outcome audit followed only by journal repair.
  * Never moves either body, starts propulsion, or resumes the held journey.
  * Unsupported old intents and ambiguous/mismatched native states remain held.
  */
 public static Entry recover(MinecraftServer server,UUID journey)throws IOException{
  require(server.isSameThread(),"Encounter recovery requires server thread");var journal=FreightJourneyControl.journal(server);var entry=journal.get(journey);
  boolean acknowledged=entry.phase()==Phase.APPROACH&&!entry.encounterReceipt().isEmpty();
  require(journal.fault().isEmpty()&&journal.held(journey)&&(acknowledged||entry.phase()==Phase.ORBIT&&!entry.encounterIntent().isEmpty()),"Held pending or acknowledged native encounter required");
  String intent=acknowledged?entry.encounterReceipt():entry.encounterIntent();
  if(intent.startsWith(OrbitalDistinctCoastRecoveryRecord.PREFIX))return recoverDistinct(server,journal,entry,acknowledged,intent);
  if(intent.startsWith(OrbitalCommonMotionRecoveryRecord.PREFIX))return recoverCommon(server,journal,entry,acknowledged,intent);
  if(intent.startsWith(OrbitalRelativeMotionRecoveryRecord.PREFIX))return recoverRelative(server,journal,entry,acknowledged,intent);
  var coast=intent.startsWith(OrbitalCoastRecoveryRecord.PREFIX)?OrbitalCoastRecoveryRecord.decode(intent):null;
  var r=coast==null?OrbitalEncounterRecoveryRecord.decode(intent):coast.baseline();var plan=entry.plan();
  if(coast!=null){
   require(coast.destinationDigest().equals(digest(plan.destinationRoute()))&&DeepSpaceData.getInstance(server).getUniverseTicks()>=coast.preparedUniverseTick(),"Coast receipt destination or clock changed");
   var ref=FreightDestinationReference.decode(plan.destinationRoute());ref.requirePlan(plan);
   require(ref.body().equals(r.target())&&NativeFreightDestination.resolve(server,ref,plan.owner()).body()==body(server,r.target()),"Coast recovery requires original committed destination");
  }
  require(r.journey().equals(journey)&&r.body().equals(entry.body())&&r.owner().equals(plan.owner())&&r.transponder().equals(plan.transponder())
    &&r.retiredSource().equals(plan.sourceBody())&&r.preparedRevision()<entry.revision()&&r.dimension().equals(plan.destinationDimension()),"Recovery record disagrees with saved journey");
  var ship=body(server,r.body());var target=body(server,r.target());
  var a=OrbitalBodyAuthority.read(ship,r.transponder(),r.owner(),r.retiredSource());var b=OrbitalBodyAuthority.read(target,r.targetTransponder(),r.owner(),r.retiredTarget());
  freeController(ship,a,false);freeController(target,b,false);OrbitalBodyQuiescence.read(ship);OrbitalBodyQuiescence.read(target);
  require(!journal.unfinished(r.targetTransponder()),"Destination owns another journey");
  var pair=OrbitalEndpointTelemetry.pair(server,r.body(),r.target());
  require(pair.ship().dimension().equals(r.dimension())&&pair.ship().frame().equals(r.frame())&&pair.destination().instance()==r.targetCell()
    &&vector(target).sub(r.targetPosition()).length()<=1e-3&&recoveryRotation(rotation(ship)).equals(r.sourceRotation())&&recoveryRotation(rotation(target)).equals(r.targetRotation()),"Native recovery frames, target or orientation changed");
  require(pair.ship().localVelocity().length()==0&&pair.destination().localVelocity().length()==0&&RigidBodyHandle.of(ship).getAngularVelocity().length()==0&&RigidBodyHandle.of(target).getAngularVelocity().length()==0,"Recovery requires stationary original bodies");
  boolean old=pair.ship().instance()==r.sourceCell()&&vector(ship).sub(r.oldPosition()).length()<=1e-3;
  boolean applied=pair.ship().instance()==r.targetCell()&&vector(ship).sub(r.newPosition()).length()<=1e-3;
  require(old!=applied,"Native encounter outcome is ambiguous");
  var targetMembers=OrbitalInstanceMembership.read(server,pair.destination());
  if(old)require(OrbitalInstanceMembership.read(server,pair.ship()).soleLoadedBodyWithoutPlayers(r.body())&&targetMembers.soleLoadedBodyWithoutPlayers(r.target()),"Unapplied native cell membership changed");
  else require(targetMembers.loadedBodies().equals(Set.of(r.body(),r.target()))&&targetMembers.unloadedBodies().isEmpty()&&targetMembers.onlinePlayers().isEmpty()&&targetMembers.offlinePlayers().isEmpty(),"Applied native cell membership changed");
  require(OrbitalBodyCustody.readForEncounterRecovery(ship).digest().equals(r.sourceDigest())&&OrbitalBodyCustody.readForEncounterRecovery(target).digest().equals(r.targetDigest()),"Native recovery cargo or machine configuration changed");
  require(journal.held(journey)&&journal.get(journey).equals(entry),"Journal changed during native recovery audit");
  String evidence=digest(intent+"\nNATIVE_RECOVERY="+applied+"\n"+pair);
  return acknowledged?journal.reconcileAcknowledgedEncounter(journey,entry.revision(),entry.body(),applied,evidence):journal.reconcileEncounter(journey,entry.revision(),entry.body(),applied,evidence);
 }
 private static Entry recoverCommon(MinecraftServer server,FreightJourneyJournal journal,Entry entry,boolean acknowledged,String intent)throws IOException{
  var moving=OrbitalCommonMotionRecoveryRecord.decode(intent);var r=moving.baseline();var plan=entry.plan();var journey=plan.journey();
  require(r.journey().equals(journey)&&r.body().equals(entry.body())&&r.owner().equals(plan.owner())&&r.transponder().equals(plan.transponder())&&r.retiredSource().equals(plan.sourceBody())&&r.preparedRevision()<entry.revision()&&r.dimension().equals(plan.destinationDimension()),"Common-motion recovery record disagrees with journey");
  var ref=FreightDestinationReference.decode(plan.destinationRoute());ref.requirePlan(plan);require(ref.body().equals(r.target()),"Common-motion recovery destination commitment differs");NativeFreightDestination.resolve(server,ref,plan.owner());
  var ship=body(server,r.body());var target=body(server,r.target());
  var a=OrbitalBodyAuthority.read(ship,r.transponder(),r.owner(),r.retiredSource());var b=OrbitalBodyAuthority.read(target,r.targetTransponder(),r.owner(),r.retiredTarget());
  freeController(ship,a,false);freeController(target,b,false);OrbitalBodyQuiescence.read(ship);OrbitalBodyQuiescence.read(target);require(!journal.unfinished(r.targetTransponder()),"Common-motion destination owns another journey");
  var pair=OrbitalEndpointTelemetry.pair(server,r.body(),r.target());
  require(pair.ship().dimension().equals(r.dimension())&&pair.ship().frame().equals(r.frame())&&pair.ship().celestialPosition().equals(pair.destination().celestialPosition())&&pair.ship().celestialVelocity().equals(pair.destination().celestialVelocity())&&recoveryRotation(rotation(ship)).equals(r.sourceRotation())&&recoveryRotation(rotation(target)).equals(r.targetRotation()),"Common-motion recovery frame or orientation changed");
  require(RigidBodyHandle.of(ship).getAngularVelocity().length()==0&&RigidBodyHandle.of(target).getAngularVelocity().length()==0,"Rotating common-motion recovery is unqualified");
  var config=dev.ryanhcode.sable.sublevel.system.SubLevelPhysicsSystem.require(ship.getLevel()).getConfig();
  for(var body:List.of(ship,target)){
   var v=RigidBodyHandle.of(body).getLinearVelocity();var history=body.latestLinearVelocity;
   require(history.distance(v)<=1e-3,"Restored common-motion velocity disagrees with native history");OrbitalMotionPrecision.requireResolved(vector(body),new V(v.x(),v.y(),v.z()),config.substepsPerTick,config.solverIterations);
  }
  boolean applied=moving.classify(pair.ship().instance(),pair.destination().instance(),vector(ship),vector(target),pair.ship().localVelocity(),pair.destination().localVelocity(),dev.devce.rocketnautics.content.orbit.DeepSpaceData.getInstance(server).getUniverseTicks())==OrbitalCommonMotionRecoveryRecord.Outcome.APPLIED;
  var members=OrbitalInstanceMembership.read(server,pair.destination());
  if(applied)require(members.loadedBodies().equals(Set.of(r.body(),r.target()))&&members.unloadedBodies().isEmpty()&&members.onlinePlayers().isEmpty()&&members.offlinePlayers().isEmpty(),"Applied common-motion membership differs");
  else require(OrbitalInstanceMembership.read(server,pair.ship()).soleLoadedBodyWithoutPlayers(r.body())&&members.soleLoadedBodyWithoutPlayers(r.target()),"Unapplied common-motion membership differs");
  require(OrbitalBodyCustody.readForCommonMotionRecovery(ship).digest().equals(r.sourceDigest())&&OrbitalBodyCustody.readForCommonMotionRecovery(target).digest().equals(r.targetDigest()),"Common-motion recovery cargo or configuration changed");
  require(journal.held(journey)&&journal.get(journey).equals(entry),"Journal changed during common-motion audit");String evidence=digest(intent+"\nCOMMON_MOTION_RECOVERY="+applied+"\n"+pair);
  return acknowledged?journal.reconcileAcknowledgedEncounter(journey,entry.revision(),entry.body(),applied,evidence):journal.reconcileEncounter(journey,entry.revision(),entry.body(),applied,evidence);
 }
 private static Entry recoverRelative(MinecraftServer server,FreightJourneyJournal journal,Entry entry,boolean acknowledged,String intent)throws IOException{
  var moving=OrbitalRelativeMotionRecoveryRecord.decode(intent);var r=moving.baseline();var plan=entry.plan();var journey=plan.journey();
  require(r.journey().equals(journey)&&r.body().equals(entry.body())&&r.owner().equals(plan.owner())&&r.transponder().equals(plan.transponder())&&r.retiredSource().equals(plan.sourceBody())&&r.preparedRevision()<entry.revision()&&r.dimension().equals(plan.destinationDimension()),"Relative-motion recovery record disagrees with journey");
  var ref=FreightDestinationReference.decode(plan.destinationRoute());ref.requirePlan(plan);require(ref.body().equals(r.target()),"Relative-motion recovery destination commitment differs");NativeFreightDestination.resolve(server,ref,plan.owner());
  var ship=body(server,r.body());var target=body(server,r.target());
  var a=OrbitalBodyAuthority.read(ship,r.transponder(),r.owner(),r.retiredSource());var b=OrbitalBodyAuthority.read(target,r.targetTransponder(),r.owner(),r.retiredTarget());
  freeController(ship,a,false);freeController(target,b,false);OrbitalBodyQuiescence.read(ship);OrbitalBodyQuiescence.read(target);require(!journal.unfinished(r.targetTransponder()),"Relative-motion destination owns another journey");
  var pair=OrbitalEndpointTelemetry.pair(server,r.body(),r.target());
  require(pair.ship().dimension().equals(r.dimension())&&pair.ship().frame().equals(r.frame())&&pair.ship().celestialPosition().equals(pair.destination().celestialPosition())&&pair.ship().celestialVelocity().equals(pair.destination().celestialVelocity())&&recoveryRotation(rotation(ship)).equals(r.sourceRotation())&&recoveryRotation(rotation(target)).equals(r.targetRotation()),"Relative-motion recovery frame or orientation changed");
  require(RigidBodyHandle.of(ship).getAngularVelocity().length()==0&&RigidBodyHandle.of(target).getAngularVelocity().length()==0,"Rotating relative-motion recovery is unqualified");
  var config=dev.ryanhcode.sable.sublevel.system.SubLevelPhysicsSystem.require(ship.getLevel()).getConfig();
  for(var body:List.of(ship,target)){
   var v=RigidBodyHandle.of(body).getLinearVelocity();var history=body.latestLinearVelocity;
   require(history.distance(v)<=1e-3,"Restored relative-motion velocity disagrees with native history");OrbitalMotionPrecision.requireResolved(vector(body),new V(v.x(),v.y(),v.z()),config.substepsPerTick,config.solverIterations);
  }
  boolean applied=moving.classify(pair.ship().instance(),pair.destination().instance(),vector(ship),vector(target),pair.ship().localVelocity(),pair.destination().localVelocity(),DeepSpaceData.getInstance(server).getUniverseTicks())==OrbitalRelativeMotionRecoveryRecord.Outcome.APPLIED;
  var members=OrbitalInstanceMembership.read(server,pair.destination());
  if(applied)require(members.loadedBodies().equals(Set.of(r.body(),r.target()))&&members.unloadedBodies().isEmpty()&&members.onlinePlayers().isEmpty()&&members.offlinePlayers().isEmpty(),"Applied relative-motion membership differs");
  else require(OrbitalInstanceMembership.read(server,pair.ship()).soleLoadedBodyWithoutPlayers(r.body())&&members.soleLoadedBodyWithoutPlayers(r.target()),"Unapplied relative-motion membership differs");
  require(OrbitalBodyCustody.readForCommonMotionRecovery(ship).digest().equals(r.sourceDigest())&&OrbitalBodyCustody.readForCommonMotionRecovery(target).digest().equals(r.targetDigest()),"Relative-motion recovery cargo or configuration changed");
  require(journal.held(journey)&&journal.get(journey).equals(entry),"Journal changed during relative-motion audit");String evidence=digest(intent+"\nRELATIVE_MOTION_RECOVERY="+applied+"\n"+pair);
  return acknowledged?journal.reconcileAcknowledgedEncounter(journey,entry.revision(),entry.body(),applied,evidence):journal.reconcileEncounter(journey,entry.revision(),entry.body(),applied,evidence);
 }
 private static Entry recoverDistinct(MinecraftServer server,FreightJourneyJournal journal,Entry entry,boolean acknowledged,String intent)throws IOException{
  var saved=OrbitalDistinctCoastRecoveryRecord.decode(intent);var r=saved.baseline();var plan=entry.plan();var journey=plan.journey();
  require(r.journey().equals(journey)&&r.body().equals(entry.body())&&r.owner().equals(plan.owner())&&r.transponder().equals(plan.transponder())&&r.retiredSource().equals(plan.sourceBody())&&r.preparedRevision()<entry.revision()&&r.dimension().equals(plan.destinationDimension())&&saved.destinationDigest().equals(digest(plan.destinationRoute())),"Distinct coast receipt disagrees with journey");
  var ref=FreightDestinationReference.decode(plan.destinationRoute());ref.requirePlan(plan);require(ref.body().equals(r.target()),"Distinct coast destination commitment changed");NativeFreightDestination.resolve(server,ref,plan.owner());
  var ship=body(server,r.body());var target=body(server,r.target());
  var a=OrbitalBodyAuthority.read(ship,r.transponder(),r.owner(),r.retiredSource());var b=OrbitalBodyAuthority.read(target,r.targetTransponder(),r.owner(),r.retiredTarget());
  freeController(ship,a,false);freeController(target,b,false);OrbitalBodyQuiescence.read(ship);OrbitalBodyQuiescence.read(target);require(!journal.unfinished(r.targetTransponder()),"Distinct coast target has another journey");
  var pair=OrbitalEndpointTelemetry.pair(server,r.body(),r.target());
  require(pair.ship().dimension().equals(r.dimension())&&pair.ship().frame().equals(r.frame())&&recoveryRotation(rotation(ship)).equals(r.sourceRotation())&&recoveryRotation(rotation(target)).equals(r.targetRotation()),"Distinct coast recovery frame or orientation changed");
  var config=dev.ryanhcode.sable.sublevel.system.SubLevelPhysicsSystem.require(ship.getLevel()).getConfig();
  for(var body:List.of(ship,target)){var handle=RigidBodyHandle.of(body);var v=handle.getLinearVelocity();require(handle.getAngularVelocity().length()==0&&body.latestLinearVelocity.distance(v)<=1e-3,"Distinct coast native history or rotation changed");OrbitalMotionPrecision.requireResolved(vector(body),new V(v.x(),v.y(),v.z()),config.substepsPerTick,config.solverIterations);}
  var data=DeepSpaceData.getInstance(server);long now=data.getUniverseTicks();
  var outcome=acknowledged?saved.classifyAcknowledged(pair.ship().instance(),pair.destination().instance(),vector(ship),vector(target),pair.ship().localVelocity(),pair.destination().localVelocity(),now):saved.classify(pair.ship().instance(),pair.destination().instance(),vector(ship),vector(target),pair.ship().localVelocity(),pair.destination().localVelocity(),now);
  boolean applied=outcome==OrbitalDistinctCoastRecoveryRecord.Outcome.APPLIED;
  var sourceCell=data.getInstance(r.sourceCell());var targetCell=data.getInstance(r.targetCell());require(targetCell!=null,"Committed target cell unavailable");var targetOrbit=targetCell.getPosition();
  require(targetOrbit.getLocalUniverseTicks()==now&&targetOrbit.getTimescale()==1&&targetOrbit.getCurrentOrbit().getMu()==pair.ship().mu(),"Target coast clock or gravity changed");
  var targetPV=targetOrbit.getCurrentPVCoords();double elapsed=(now-saved.preparedUniverseTick())*.05;
  if(sourceCell==null){
   require(acknowledged&&applied,"Unacknowledged or unapplied encounter requires original source cell");
   saved.coasts().verifyTarget(coastVector(targetPV.getPosition()),coastVector(targetPV.getVelocity()),pair.ship().mu(),elapsed);
  }else{
   var sourceOrbit=sourceCell.getPosition();require(sourceOrbit.getFrame()==targetOrbit.getFrame()&&sourceOrbit.getLocalUniverseTicks()==now&&sourceOrbit.getTimescale()==1&&sourceOrbit.getCurrentOrbit().getMu()==pair.ship().mu(),"Original source coast clock or gravity changed");
   var sourcePV=sourceOrbit.getCurrentPVCoords();saved.coasts().verify(coastVector(sourcePV.getPosition()),coastVector(sourcePV.getVelocity()),coastVector(targetPV.getPosition()),coastVector(targetPV.getVelocity()),pair.ship().mu(),elapsed);
  }
  var members=OrbitalInstanceMembership.read(server,pair.destination());
  if(applied)require(members.loadedBodies().equals(Set.of(r.body(),r.target()))&&members.unloadedBodies().isEmpty()&&members.onlinePlayers().isEmpty()&&members.offlinePlayers().isEmpty(),"Applied distinct coast membership differs");
  else require(OrbitalInstanceMembership.read(server,pair.ship()).soleLoadedBodyWithoutPlayers(r.body())&&members.soleLoadedBodyWithoutPlayers(r.target()),"Unapplied distinct coast membership differs");
  require(OrbitalBodyCustody.readForDistinctCoastRecovery(ship).digest().equals(r.sourceDigest())&&OrbitalBodyCustody.readForDistinctCoastRecovery(target).digest().equals(r.targetDigest()),"Distinct coast recovery cargo or configuration changed");
  require(journal.held(journey)&&journal.get(journey).equals(entry),"Journal changed during distinct coast audit");String evidence=digest(intent+"\nDISTINCT_COAST_RECOVERY="+applied+"\n"+pair);
  return acknowledged?journal.reconcileAcknowledgedEncounter(journey,entry.revision(),entry.body(),applied,evidence):journal.reconcileEncounter(journey,entry.revision(),entry.body(),applied,evidence);
 }
 private static V coastVector(dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D p){return new V(p.getX(),p.getY(),p.getZ());}
 private static String digest(String text){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
}
