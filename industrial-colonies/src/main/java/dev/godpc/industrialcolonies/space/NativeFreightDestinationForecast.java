package dev.godpc.industrialcolonies.space;

import java.util.UUID;
import dev.devce.rocketnautics.api.orbit.DeepSpaceHelper;
import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import dev.devce.rocketnautics.content.orbit.DeepSpaceInstance;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.orbits.KeplerianOrbit;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import net.minecraft.server.MinecraftServer;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.godpc.industrialcolonies.space.OrbitalInterceptPlanner.State;

/** Conditional read-only body-origin forecast for an already commissioned dock.
 * Valid only while the same native orbit, cell, clock and nonrotating constant
 * local motion persist. No trajectory mutation, loading, ownership acquisition,
 * cargo access, collision clearance or permission to actuate is provided. */
public final class NativeFreightDestinationForecast {
 private final MinecraftServer server;
 private final FreightDestinationReference reference;
 private final UUID owner;
 private final DeepSpaceInstance instance;
 private final KeplerianOrbit nativeOrbit;
 private final CartesianOrbit snapshot;
 private final OrbitalEndpoint initial;
 private final int horizon;
 public NativeFreightDestinationForecast(MinecraftServer server,FreightDestinationReference reference,UUID owner,int horizonTicks){
  require(horizonTicks>=1&&horizonTicks<=1200,"Forecast horizon must be 1..1200 ticks");
  this.server=server;this.reference=reference;this.owner=owner;horizon=horizonTicks;
  var resolved=NativeFreightDestination.resolve(server,reference,owner);
  initial=OrbitalEndpointTelemetry.read(server,reference.body());
  require(initial.timescale()==1&&initial.localVelocity().length()<=1&&RigidBodyHandle.of(resolved.body()).getAngularVelocity().length()<=1e-8,"Ordinary time and bounded nonrotating local coast required");
  var p=resolved.body().logicalPose().position();instance=DeepSpaceData.getInstance(server).getInstanceForPos((int)Math.floor(p.x()),(int)Math.floor(p.z()));
  var position=instance.getPosition();nativeOrbit=position.getOrbit();snapshot=new CartesianOrbit(position.getCurrentOrbit());
  require(!snapshot.hasNonKeplerianAcceleration(),"Unmodeled celestial acceleration");
  for(int axis=0;axis<3;axis++){
   var unit=DeepSpaceHelper.adapt(new org.joml.Vector3d(axis==0?1:0,axis==1?1:0,axis==2?1:0));
   require(unit.distance(new Vector3D(axis==0?1:0,axis==1?1:0,axis==2?1:0))<1e-12,"Unqualified local-to-celestial basis");
  }
  require(Math.abs(DeepSpaceHelper.getDateByTicks(initial.universeTick()+20).durationFrom(DeepSpaceHelper.getDateByTicks(initial.universeTick()))-1)<1e-12,"Unqualified native clock scale");
  require(position.getOrbit()==nativeOrbit&&position.getLocalUniverseTicks()==initial.universeTick(),"Snapshot altered native trajectory");
 }
 public OrbitalEndpoint initial(){return initial;}
 /** Body origin, not oriented docking-port pose. Pure snapshot propagation. */
 public State predict(int deltaTicks){
  require(deltaTicks>=0&&deltaTicks<=horizon,"Forecast outside committed horizon");
  double seconds=deltaTicks*.05;var pv=snapshot.shiftedBy(seconds).getPVCoordinates();
  return new State(vector(pv.getPosition()).add(initial.localOffset()).add(initial.localVelocity().mul(seconds)),
                   vector(pv.getVelocity()).add(initial.localVelocity()));
 }
 /** Compare the current loaded target with its earlier prediction. Refusal
  * invalidates use of this forecast; it never repairs/repositions the target. */
 public double verify(){
  var resolved=NativeFreightDestination.resolve(server,reference,owner);
  var current=OrbitalEndpointTelemetry.read(server,reference.body());
  require(current.instance()==initial.instance()&&current.frame().equals(initial.frame())&&current.timescale()==1
   &&current.mu()==initial.mu()&&instance.getPosition().getOrbit()==nativeOrbit,"Destination trajectory changed");
  long delta=current.universeTick()-initial.universeTick();require(delta>=0&&delta<=horizon,"Forecast clock expired or moved backwards");
  require(current.localVelocity().sub(initial.localVelocity()).length()<=1e-6
   &&RigidBodyHandle.of(resolved.body()).getAngularVelocity().length()<=1e-8,"Destination local motion changed");
  var predicted=predict((int)delta);
  double error=current.celestialPosition().add(current.localOffset()).sub(predicted.position()).length();
  require(Double.isFinite(error)&&error<=.001&&current.celestialVelocity().add(current.localVelocity()).sub(predicted.velocity()).length()<=1e-6,"Destination deviated from conditional coast forecast");
  return error;
 }
 private static V vector(Vector3D v){return new V(v.getX(),v.getY(),v.getZ());}
 private static void require(boolean valid,String reason){if(!valid)throw new IllegalStateException(reason);}
}
