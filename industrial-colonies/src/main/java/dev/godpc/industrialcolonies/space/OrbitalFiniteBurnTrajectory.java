package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.utils.PVCoordinates;

/** Prescribed-force trajectory proposal for one unchanged native cell/body.
 * Attitude/queued-force history must be supplied by a separate model. This
 * class does not forecast command response, fuel, collisions, clearances,
 * additional cell participants or future native frame transitions. */
public final class OrbitalFiniteBurnTrajectory {
 private OrbitalFiniteBurnTrajectory(){}
 public record Command(V queuedForce,V angularVelocity,double qx,double qy,double qz,double qw){}
 public record Sample(CartesianOrbit orbit,V localPosition,V localVelocity){}
 public static List<Sample> predict(CartesianOrbit initial,V localPosition,V localVelocity,
   V cellCenter,double cellSide,V expandedLocalBounds,double mass,List<Command> commands){
  require(initial!=null&&initial.getFrame().isPseudoInertial()&&!initial.hasNonKeplerianAcceleration(),"Inertial two-body seed required");
  require(Double.isFinite(initial.getMu())&&initial.getMu()>0&&Double.isFinite(initial.getA())&&initial.getA()>0&&initial.getE()<1,"Bound elliptic seed required");
  require(commands!=null&&!commands.isEmpty()&&commands.size()<=3600,"One to3600 prescribed native ticks required");
  commands=List.copyOf(commands);var result=new ArrayList<Sample>(commands.size());var orbit=initial;
  for(var command:commands){
   double hull=OrbitalFiniteBurnStep.refreshedHullDiagonal(expandedLocalBounds,command.qx(),command.qy(),command.qz(),command.qw());
   var step=OrbitalFiniteBurnStep.predict(localPosition,localVelocity,command.queuedForce(),command.angularVelocity(),mass,cellCenter,cellSide,hull);
   var pv=orbit.getPVCoordinates();V impulse=step.orbitalImpulse();
   orbit=new CartesianOrbit(new PVCoordinates(pv.getPosition(),pv.getVelocity().add(new Vector3D(impulse.x(),impulse.y(),impulse.z()))),orbit.getFrame(),orbit.getDate(),orbit.getMu()).shiftedBy(.05);
   require(Double.isFinite(orbit.getA())&&orbit.getA()>0&&orbit.getE()<1,"Prescribed burn leaves elliptic model");
   localPosition=step.localPosition();localVelocity=step.localVelocity();result.add(new Sample(orbit,localPosition,localVelocity));
  }
  return List.copyOf(result);
 }
 private static void require(boolean ok,String message){if(!ok)throw new IllegalArgumentException(message);}
}
