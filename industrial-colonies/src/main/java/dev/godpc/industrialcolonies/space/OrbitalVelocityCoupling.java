package dev.godpc.industrialcolonies.space;

import java.util.List;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Read-only model of the installed native local-velocity/orbit boundary.
 * Inputs must be the native physics-hook sample, not an earlier server sample.
 * It is neither a force integrator nor authority to write orbit or body state. */
public final class OrbitalVelocityCoupling {
 private OrbitalVelocityCoupling(){}
 public record Split(V orbitContribution,V remainingLocalVelocity,double boundaryOverrun){}
 public record Contribution(double mass,V velocity){
  public Contribution{require(Double.isFinite(mass)&&mass>0,"Positive finite native mass required");finite(velocity);}
 }
 public static Split split(V localOffset,V localVelocity,double hullDiagonal,double cellSide){
  finite(localOffset);finite(localVelocity);
  require(Double.isFinite(hullDiagonal)&&hullDiagonal>0&&Double.isFinite(cellSide)&&cellSide>0,"Positive finite native geometry required");
  double radius=localOffset.length();require(Double.isFinite(radius),"Offset magnitude overflow");
  double overrun=2*(radius+hullDiagonal)-cellSide;require(Double.isFinite(overrun),"Boundary geometry overflow");
  if(localOffset.dot(localOffset)<=1e-20||overrun<=0)return new Split(V.ZERO,localVelocity,overrun);
  V direction=localOffset.mul(1/radius);double radialSpeed=direction.dot(localVelocity);
  V radial=direction.mul(radialSpeed),tangent=localVelocity.sub(radial);
  V outward=radialSpeed<=0?V.ZERO:overrun>1?radial.add(direction.mul(Math.sqrt(overrun))):radial;
  V transferred=outward.add(tangent.mul(.5)),remaining=localVelocity.sub(transferred);
  finite(transferred);finite(remaining);return new Split(transferred,remaining,overrun);
 }
 /** Native instance sums mass*contribution and divides by total participating
  * mass, including inner-cell bodies contributing zero. Caller must establish
  * the exact native participating set; one controlled ship is not that proof. */
 public static V aggregate(List<Contribution> contributions){
  require(contributions!=null&&!contributions.isEmpty(),"Complete nonempty native contribution set required");
  double mass=0;V momentum=V.ZERO;
  for(var contribution:contributions){mass+=contribution.mass();momentum=momentum.add(contribution.velocity().mul(contribution.mass()));}
  require(Double.isFinite(mass),"Mass sum overflow");finite(momentum);
  // The installed implementation compares the weighted numerator, before division.
  double squared=momentum.dot(momentum);require(Double.isFinite(squared),"Momentum magnitude overflow");
  return squared<=1e-20?V.ZERO:momentum.mul(1/mass);
 }
 private static void finite(V v){require(v!=null&&v.finite(),"Finite vector required");}
 private static void require(boolean valid,String reason){if(!valid)throw new IllegalArgumentException(reason);}
}
