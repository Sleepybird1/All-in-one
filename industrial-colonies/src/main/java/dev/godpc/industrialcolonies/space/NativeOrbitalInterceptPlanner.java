package dev.godpc.industrialcolonies.space;

import java.util.Objects;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.utils.PVCoordinates;
import dev.devce.rocketnautics.shaded.orekit.utils.TimeStampedAngularCoordinates;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.godpc.industrialcolonies.space.OrbitalInterceptPlanner.State;

/** Uses the installed mod's shaded Cartesian propagator. Only a read-only,
 * same-frame/same-epoch elliptic proposal; no local body offsets, finite burns,
 * terrain/traffic clearance, native encounter conversion or actuators. */
public final class NativeOrbitalInterceptPlanner {
 private NativeOrbitalInterceptPlanner(){}
 public record ClearedProposal(OrbitalInterceptPlanner.Proposal proposal,
     OrbitalTrajectoryClearance.Certificate transferClearance,OrbitalTrajectoryClearance.Certificate targetClearance){}
 /** Adds constant-spin native sphere/cube clearance for both ideal coasts.
  * Required distance must already include transition height, hull and margin.
  * Local body offsets, finite burns, other bodies and admission remain separate. */
 public static ClearedProposal solveCleared(CartesianOrbit source,CartesianOrbit target,
     TimeStampedAngularCoordinates rotation,double radius,boolean sphere,double requiredDistance,
     double seconds,double departureBudget,double arrivalBudget){
  var proposal=solve(source,target,seconds,radius,departureBudget,arrivalBudget);
  var initial=source.getPVCoordinates();
  var transfer=new CartesianOrbit(new PVCoordinates(initial.getPosition(),initial.getVelocity().add(vector(proposal.departureImpulse()))),source.getFrame(),source.getDate(),source.getMu());
  var transferClearance=OrbitalTrajectoryClearance.certify(transfer,rotation,radius,sphere,requiredDistance,seconds);
  var targetClearance=OrbitalTrajectoryClearance.certify(target,rotation,radius,sphere,requiredDistance,seconds);
  return new ClearedProposal(proposal,transferClearance,targetClearance);
 }
 public static OrbitalInterceptPlanner.Proposal solve(CartesianOrbit source,CartesianOrbit target,
     double seconds,double minimumRadius,double departureBudget,double arrivalBudget){
  Objects.requireNonNull(source);Objects.requireNonNull(target);
  require(Double.isFinite(seconds)&&seconds>=1&&seconds<=3600,"Qualified flight time is 1..3600 seconds");
  require(source.getFrame()==target.getFrame()&&source.getFrame().isPseudoInertial()
   &&source.getDate().equals(target.getDate())&&source.getMu()==target.getMu(),"Exact common inertial frame, epoch and gravity required");
  require(Double.isFinite(minimumRadius)&&minimumRadius>0,"Positive minimum orbital radius required");
  qualified(source,minimumRadius);qualified(target,minimumRadius);
  var departure=state(source);var destination=state(target.shiftedBy(seconds));
  return OrbitalInterceptPlanner.solve(departure,destination,seconds,departureBudget,arrivalBudget,(initial,dt)->{
   var orbit=new CartesianOrbit(new PVCoordinates(vector(initial.position()),vector(initial.velocity())),source.getFrame(),source.getDate(),source.getMu());
   qualified(orbit,minimumRadius);return state(orbit.shiftedBy(dt));
  });
 }
 private static void qualified(CartesianOrbit orbit,double minimumRadius){
  require(!orbit.hasNonKeplerianAcceleration()&&Double.isFinite(orbit.getMu())&&orbit.getMu()>0
   &&Double.isFinite(orbit.getA())&&orbit.getA()>0&&Double.isFinite(orbit.getE())&&orbit.getE()<1
   &&orbit.getA()*(1-orbit.getE())>minimumRadius,"Unsupported or clearance-violating elliptic trajectory");
 }
 private static State state(CartesianOrbit orbit){
  var pv=orbit.getPVCoordinates();V p=vector(pv.getPosition()),v=vector(pv.getVelocity());
  require(8*(Math.ulp(p.x())+Math.ulp(p.y())+Math.ulp(p.z()))<=.001,"Insufficient orbital coordinate precision");
  return new State(p,v);
 }
 private static Vector3D vector(V v){return new Vector3D(v.x(),v.y(),v.z());}
 private static V vector(Vector3D v){return new V(v.getX(),v.getY(),v.getZ());}
 private static void require(boolean value,String reason){if(!value)throw new IllegalArgumentException(reason);}
}
