package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Bounded read-only motion qualification. This is not a journey permit or a
 * crash-recovery record and never relaxes the stationary encounter coordinator. */
public final class OrbitalCommonMotionProof {
 private OrbitalCommonMotionProof(){}
 public record Sample(OrbitalEndpoint.Pair pair,V sourcePosition,V targetPosition,
                      V sourceHistoryVelocity,V targetHistoryVelocity,double sourceSpin,double targetSpin) {
  public Sample {
   Objects.requireNonNull(pair);
   for(V v:List.of(sourcePosition,targetPosition,sourceHistoryVelocity,targetHistoryVelocity))
    if(!v.finite()||!Double.isFinite(v.length()))throw new IllegalArgumentException("Finite motion sample required");
   if(!Double.isFinite(sourceSpin)||!Double.isFinite(targetSpin)||sourceSpin!=0||targetSpin!=0)throw new IllegalArgumentException("Rotating common motion is unqualified");
  }
 }
 public record Qualified(OrbitalEndpoint.Pair latest,V commonVelocity,int observations){}
 /** Basic CAAL v1 refreshes its derived position every forty game ticks.
  * Only bounded constant translation is accepted; this does not validate cargo,
  * identity, rotation or the surrounding native motion proof. */
 public static void requireCurrentCache(V current,V cached,V velocity,long now,long seen){
  if(current==null||cached==null||velocity==null||!current.finite()||!cached.finite()||!velocity.finite()
    ||velocity.length()<=.1||velocity.length()>1||seen<0||now<seen||now-seen>40)
   throw new IllegalArgumentException("Unsupported moving transponder cache age or velocity");
  double error=current.sub(cached).sub(velocity.mul((now-seen)*.05)).length();
  if(!Double.isFinite(error)||error>1e-3)throw new IllegalArgumentException("Moving transponder cache disagrees with clock-qualified translation");
 }
 public static Qualified verify(List<Sample> samples){
  if(samples==null||samples.size()<20||samples.size()>60)throw new IllegalArgumentException("Twenty to sixty consecutive native observations required");
  Sample first=samples.getFirst();var base=OrbitalEndpoint.pair(first.pair().ship(),first.pair().destination());
  V velocity=base.ship().localVelocity();
  // Below the native serializer's 0.1 threshold a vector is not even persisted.
  // Also exclude tiny nominal velocities that fit the error tolerance while the
  // actual body remains motionless. This profile covers observed moving bodies.
  if(velocity.length()<=.1||velocity.length()>1)throw new IllegalArgumentException("Common motion must exceed native save threshold and remain bounded");
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
   if(!pair.ship().localVelocity().equals(velocity)||!pair.destination().localVelocity().equals(velocity)
     ||!pair.ship().celestialVelocity().equals(pair.destination().celestialVelocity())
     ||!pair.ship().celestialPosition().equals(pair.destination().celestialPosition()))throw new IllegalArgumentException("Common native and celestial motion required");
   if(!s.sourcePosition().sub(pair.ship().localOffset()).equals(sourceCenter)||!s.targetPosition().sub(pair.destination().localOffset()).equals(targetCenter))throw new IllegalArgumentException("Native cell origin changed");
   V displacement=velocity.mul(i*.05);
   if(s.sourcePosition().sub(first.sourcePosition()).sub(displacement).length()>1e-3
     ||s.targetPosition().sub(first.targetPosition()).sub(displacement).length()>1e-3
     ||s.sourceHistoryVelocity().sub(velocity).length()>1e-3||s.targetHistoryVelocity().sub(velocity).length()>1e-3)throw new IllegalArgumentException("Native motion is unresolved or accelerating");
   OrbitalMotionPrecision.requireResolved(s.sourcePosition(),velocity,2,18);OrbitalMotionPrecision.requireResolved(s.targetPosition(),velocity,2,18);
  }
  var latest=samples.getLast().pair();return new Qualified(OrbitalEndpoint.pair(latest.ship(),latest.destination()),velocity,samples.size());
 }
}
