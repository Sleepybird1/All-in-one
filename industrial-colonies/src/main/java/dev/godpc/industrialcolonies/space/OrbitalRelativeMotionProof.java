package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.godpc.industrialcolonies.space.OrbitalCommonMotionProof.Sample;

/** Separate read-only qualification of unequal constant local velocities in
 * equal celestial orbits. No movement permission or recovery compatibility is
 * implied. Existing stationary/common-motion profiles remain unchanged. */
public final class OrbitalRelativeMotionProof {
 private OrbitalRelativeMotionProof(){}
 public record Qualified(OrbitalEndpoint.Pair latest,V sourceVelocity,V targetVelocity,int observations){}
 public static Qualified verify(List<Sample> samples){
  if(samples==null||samples.size()<20||samples.size()>60)throw new IllegalArgumentException("Twenty to sixty consecutive native observations required");
  Sample first=samples.getFirst();var base=OrbitalEndpoint.pair(first.pair().ship(),first.pair().destination());
  V velocity=base.ship().localVelocity(),targetVelocity=base.destination().localVelocity();
  // Below the native serializer's 0.1 threshold a vector is not even persisted.
  // Also exclude tiny nominal velocities that fit the error tolerance while the
  // actual body remains motionless. This profile covers observed moving bodies.
  for(V v:List.of(velocity,targetVelocity))if(v.length()<=.1||v.length()>1)throw new IllegalArgumentException("Both motions must exceed native save threshold and remain bounded");
  double relative=velocity.sub(targetVelocity).length();
  if(relative<=1e-3||relative>.08)throw new IllegalArgumentException("Resolved nonzero relative speed within encounter envelope required");
  V sourceCenter=first.sourcePosition().sub(base.ship().localOffset()),targetCenter=first.targetPosition().sub(base.destination().localOffset());
  for(int i=0;i<samples.size();i++){
   var s=samples.get(i);var pair=OrbitalEndpoint.pair(s.pair().ship(),s.pair().destination());
   if(pair.relation()!=OrbitalEndpoint.Relation.INDEPENDENT_NATIVE_INSTANCES
     ||!pair.ship().body().equals(base.ship().body())||!pair.destination().body().equals(base.destination().body())
     ||pair.ship().instance()!=base.ship().instance()||pair.destination().instance()!=base.destination().instance()
     ||!pair.ship().frame().equals(base.ship().frame())||!pair.ship().dimension().equals(base.ship().dimension())
     ||pair.ship().mu()!=base.ship().mu()||pair.ship().planetRadius()!=base.ship().planetRadius()
     ||pair.ship().sphere()!=base.ship().sphere()||pair.ship().transitionHeight()!=base.ship().transitionHeight()
     ||pair.ship().serverTick()!=Math.addExact(base.ship().serverTick(),i)
     ||pair.ship().universeTick()!=Math.addExact(base.ship().universeTick(),i))throw new IllegalArgumentException("Motion identity, frame or consecutive clocks changed");
   if(!pair.ship().localVelocity().equals(velocity)||!pair.destination().localVelocity().equals(targetVelocity)
     ||!pair.ship().celestialVelocity().equals(pair.destination().celestialVelocity())
     ||!pair.ship().celestialPosition().equals(pair.destination().celestialPosition()))throw new IllegalArgumentException("Fixed individual velocities and equal celestial motion required");
   if(!s.sourcePosition().sub(pair.ship().localOffset()).equals(sourceCenter)||!s.targetPosition().sub(pair.destination().localOffset()).equals(targetCenter))throw new IllegalArgumentException("Native cell origin changed");
   V displacement=velocity.mul(i*.05);
   if(s.sourcePosition().sub(first.sourcePosition()).sub(displacement).length()>1e-3
     ||s.targetPosition().sub(first.targetPosition()).sub(targetVelocity.mul(i*.05)).length()>1e-3
     ||s.sourceHistoryVelocity().sub(velocity).length()>1e-3||s.targetHistoryVelocity().sub(targetVelocity).length()>1e-3)throw new IllegalArgumentException("Native motion is unresolved or accelerating");
   OrbitalMotionPrecision.requireResolved(s.sourcePosition(),velocity,2,18);OrbitalMotionPrecision.requireResolved(s.targetPosition(),targetVelocity,2,18);
  }
  var latest=samples.getLast().pair();return new Qualified(OrbitalEndpoint.pair(latest.ship(),latest.destination()),velocity,targetVelocity,samples.size());
 }
}
