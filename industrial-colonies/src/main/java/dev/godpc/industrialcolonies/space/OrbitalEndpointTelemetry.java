package dev.godpc.industrialcolonies.space;

import java.util.UUID;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.godpc.industrialcolonies.space.station.StationLifeSupport;
import dev.devce.rocketnautics.api.orbit.DeepSpaceHelper;
import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.server.MinecraftServer;

/** Reads existing loaded orbital bodies only. No chunk loads, instance claims,
 * propagation, time changes, physical movement or cargo access. */
public final class OrbitalEndpointTelemetry {
 private OrbitalEndpointTelemetry(){}
 public static OrbitalEndpoint read(MinecraftServer server,UUID bodyId){
  if(!server.isSameThread())throw new IllegalStateException("Endpoint observation requires server thread");
  var level=server.getLevel(StationLifeSupport.DEEP_SPACE);
  if(level==null)throw new IllegalStateException("Native orbital dimension unavailable");
  var container=SubLevelContainer.getContainer(level);
  var found=container==null?null:container.getSubLevel(bodyId);
  if(!(found instanceof ServerSubLevel body)||body.isRemoved())throw new IllegalStateException("Original orbital body is not loaded");
  var local=body.logicalPose().position();var data=DeepSpaceData.getInstance(server);
  if(!Double.isFinite(local.x())||!Double.isFinite(local.y())||!Double.isFinite(local.z())||Math.abs(local.x())>Integer.MAX_VALUE||Math.abs(local.z())>Integer.MAX_VALUE)throw new IllegalStateException("Invalid native physical location");
  var instance=data.getInstanceForPos((int)Math.floor(local.x()),(int)Math.floor(local.z()));
  if(instance==null||instance.isCorrupted()||!instance.boundingBox().contains(local.x(),local.y(),local.z()))throw new IllegalStateException("Body has no valid containing native orbital instance");
  var position=instance.getPosition();var frame=position.getFrame();var planetId=data.getUniverse().getIDByFrameName(frame.getName());
  if(planetId.isEmpty())throw new IllegalStateException("Unknown native planetary frame");
  var planet=data.getUniverse().getPlanetById(planetId.getAsInt());
  if(planet==null||planet.linkedDimension()==null||planet.orekitFrame()!=frame)throw new IllegalStateException("Native planetary frame identity disagrees");
  var pv=position.getCurrentPVCoords();var p=pv.getPosition();var v=pv.getVelocity();
  var rotated=planet.getRotationAtTime(position.getLocalUniverseTime()).applyInverseTo(p);
  boolean sphere=DeepSpaceHelper.isSphereShape();double radius=planet.radius();
  double dx=Math.max(0,Math.abs(rotated.getX())-radius),dy=Math.max(0,Math.abs(rotated.getY())-radius),dz=Math.max(0,Math.abs(rotated.getZ())-radius);
  double altitude=sphere?Math.max(0,rotated.getNorm()-radius):Math.sqrt(dx*dx+dy*dy+dz*dz);
  var center=instance.getCenter();var velocity=RigidBodyHandle.of(body).getLinearVelocity();
  return new OrbitalEndpoint(bodyId,level.dimension().location().toString(),instance.getId(),frame.getName(),server.getTickCount(),position.getLocalUniverseTicks(),position.getTimescale(),
   new V(p.getX(),p.getY(),p.getZ()),new V(v.getX(),v.getY(),v.getZ()),new V(local.x()-center.x(),local.y()-center.y(),local.z()-center.z()),new V(velocity.x(),velocity.y(),velocity.z()),
   position.getCurrentOrbit().getMu(),radius,sphere,altitude,planet.linkedDimension().transitionHeight());
 }
 public static OrbitalEndpoint.Pair pair(MinecraftServer server,UUID ship,UUID destination){return OrbitalEndpoint.pair(read(server,ship),read(server,destination));}
}
