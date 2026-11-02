package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.system.SubLevelPhysicsSystem;
import dev.godpc.industrialcolonies.space.station.StationLifeSupport;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import net.minecraft.server.MinecraftServer;

/** Read-only additional gate. Does not establish ownership/cargo/clearance,
 * grant a journey permit, load a body, or move anything. */
public final class OrbitalEncounterMotionCheck {
 private OrbitalEncounterMotionCheck(){}
 public static void verify(MinecraftServer server,OrbitalEncounterPlanner.Proposal proposal){
  if(!server.isSameThread())throw new IllegalStateException("Native motion check requires server thread");
  var pair=proposal.observation();var live=OrbitalEndpointTelemetry.pair(server,pair.ship().body(),pair.destination().body());
  if(!live.equals(pair))throw new IllegalStateException("Encounter observation changed before motion check");
  var level=server.getLevel(StationLifeSupport.DEEP_SPACE);var config=SubLevelPhysicsSystem.require(level).getConfig();
  var container=SubLevelContainer.getContainer(level);var data=DeepSpaceData.getInstance(server);
  for(var endpoint:new OrbitalEndpoint[]{pair.ship(),pair.destination()}){
   var body=(ServerSubLevel)container.getSubLevel(endpoint.body());var nativePosition=body.logicalPose().position();var history=body.latestLinearVelocity;
   V measured=new V(history.x(),history.y(),history.z());
   if(!measured.finite()||measured.sub(endpoint.localVelocity()).length()>1e-3)throw new IllegalStateException("Native velocity disagrees with observed pose history");
   OrbitalMotionPrecision.requireResolved(new V(nativePosition.x(),nativePosition.y(),nativePosition.z()),endpoint.localVelocity(),config.substepsPerTick,config.solverIterations);
  }
  var center=data.getInstance(pair.destination().instance()).getCenter();
  OrbitalMotionPrecision.requireResolved(new V(center.x(),center.y(),center.z()).add(proposal.receivingOffset()),proposal.receivingVelocity(),config.substepsPerTick,config.solverIterations);
 }
}
