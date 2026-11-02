package dev.godpc.industrialcolonies.space;

import java.util.Objects;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Read-only coordinate proposal, never authority to move a native body.
 * Requires the installed identity-axis conversion; native transfer, crash recovery,
 * collision queries and custody verification remain the adapter's responsibility.
 */
public final class OrbitalEncounterPlanner {
 private OrbitalEncounterPlanner() {}
 public record Eligibility(boolean owned, boolean cargoVerified, boolean noPassengers,
                           boolean detachedSingleBody, boolean actuatorsStopped,
                           boolean receivingCellClear) {
  boolean eligible(){return owned&&cargoVerified&&noPassengers&&detachedSingleBody&&actuatorsStopped&&receivingCellClear;}
 }
 /** Radii bound every hull point about the logical pose origin, not the COM. */
 public record Envelope(double shipRadius,double targetRadius,double usableCellHalfSize) {
  public Envelope {
   for(double d:new double[]{shipRadius,targetRadius,usableCellHalfSize})
    if(!Double.isFinite(d)||d<=0)throw new IllegalArgumentException("Positive finite envelope required");
  }
 }
 public record Proposal(OrbitalEndpoint.Pair observation,V receivingOffset,V receivingVelocity,
                        V relativePosition,V relativeVelocity) {}
 public static Proposal propose(OrbitalEndpoint ship,OrbitalEndpoint target,Envelope hull,Eligibility eligibility) {
  Objects.requireNonNull(hull);Objects.requireNonNull(eligibility);
  var pair=OrbitalEndpoint.pair(ship,target);
  if(pair.relation()!=OrbitalEndpoint.Relation.INDEPENDENT_NATIVE_INSTANCES)
   throw new IllegalArgumentException("Already shares native instance");
  if(!eligibility.eligible())throw new IllegalArgumentException("Native eligibility unverified");
  // A mathematically close result can still be meaningless after catastrophic
  // cancellation at large celestial coordinates. Refuse sub-millimeter ambiguity.
  double positionError=rounding(ship.celestialPosition(),target.celestialPosition(),ship.localOffset(),target.localOffset());
  double velocityError=rounding(ship.celestialVelocity(),target.celestialVelocity(),ship.localVelocity(),target.localVelocity());
  if(positionError>1e-3||velocityError>1e-6)throw new IllegalArgumentException("Insufficient coordinate precision");
  // Subtract frame centers first to avoid unnecessarily rounding local offsets.
  V offset=ship.celestialPosition().sub(target.celestialPosition()).add(ship.localOffset());
  V velocity=ship.celestialVelocity().sub(target.celestialVelocity()).add(ship.localVelocity());
  V relative=offset.sub(target.localOffset());
  V speed=velocity.sub(target.localVelocity());
  for(V v:new V[]{offset,velocity,relative,speed})
   if(!v.finite()||!Double.isFinite(v.length()))throw new IllegalArgumentException("Coordinate overflow");
  if(relative.length()+positionError>32||speed.length()+velocityError>.08)throw new IllegalArgumentException("Outside conservative encounter envelope");
  if(relative.length()-positionError<=hull.shipRadius()+hull.targetRadius())throw new IllegalArgumentException("Hull envelopes overlap");
  if(!fits(offset,hull.shipRadius()+positionError,hull.usableCellHalfSize())||!fits(target.localOffset(),hull.targetRadius()+positionError,hull.usableCellHalfSize()))
   throw new IllegalArgumentException("Hull does not fit receiving cell");
  return new Proposal(pair,offset,velocity,relative,speed);
 }
 private static boolean fits(V offset,double radius,double half) {
  return Math.abs(offset.x())+radius<half&&Math.abs(offset.y())+radius<half&&Math.abs(offset.z())+radius<half;
 }
 private static double rounding(V... values) {
  double bound=0;
  for(V v:values)bound+=Math.ulp(v.x())+Math.ulp(v.y())+Math.ulp(v.z());
  // Covers input representation and each subsequent addition/subtraction.
  return 8*bound;
 }
}
