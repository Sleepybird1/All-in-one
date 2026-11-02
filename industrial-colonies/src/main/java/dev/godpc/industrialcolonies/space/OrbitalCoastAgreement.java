package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;

/** Continuous relative-error bound for independently reconstructed near-equal
 * two-body coasts. Read-only mathematical proof, not encounter admission.
 * No thrust, frame transition, local body motion or rotation is covered. */
public final class OrbitalCoastAgreement {
 private OrbitalCoastAgreement(){}
 public record Certificate(double positionBound,double velocityBound,double seconds){}
 public static Certificate certify(CartesianOrbit a,CartesianOrbit b,double seconds){
  require(a!=null&&b!=null&&a.getFrame()==b.getFrame()&&a.getDate().equals(b.getDate())&&a.getMu()==b.getMu(),"Same inertial frame, epoch and gravity required");
  require(a.getFrame().isPseudoInertial()&&!a.hasNonKeplerianAcceleration()&&!b.hasNonKeplerianAcceleration(),"Unforced inertial coasts required");
  require(Double.isFinite(seconds)&&seconds>0&&seconds<=180,"Bounded positive coast window up to180seconds required");
  for(var orbit:new CartesianOrbit[]{a,b})require(Double.isFinite(orbit.getA())&&orbit.getA()>0&&Double.isFinite(orbit.getE())&&orbit.getE()<1&&Double.isFinite(orbit.getMu())&&orbit.getMu()>0,"Finite elliptic coasts required");
  // Bootstrap the gravity-gradient bound inside a0.5mm separation tube. Every
  // segment joining both positions then remains at least min(periapsis)-tube
  // from the origin. The central-gravity Jacobian norm is2*mu/r^3 there.
  double tube=.0005;
  double radius=Math.min(a.getA()*(1-a.getE()),b.getA()*(1-b.getE()))-tube;
  require(radius>1&&Double.isFinite(radius),"Positive well-resolved periapsis required");
  var av=a.getPVCoordinates();var bv=b.getPVCoordinates();
  for(var pv:new dev.devce.rocketnautics.shaded.orekit.utils.PVCoordinates[]{av,bv})
   require(Double.isFinite(pv.getPosition().getNorm())&&Double.isFinite(pv.getVelocity().getNorm())&&Math.ulp(pv.getPosition().getNorm())<=1e-7&&Math.ulp(pv.getVelocity().getNorm())<=1e-9,"State precision exceeds reconstruction allowance");
  // Explicit allowance for the inspected library's finite-precision state
  // reconstruction. This is not a universal floating-point theorem.
  double p=av.getPosition().distance(bv.getPosition())+1e-6;
  double v=av.getVelocity().distance(bv.getVelocity())+1e-8;
  double rate=Math.sqrt(2*a.getMu()/(radius*radius*radius));
  require(Double.isFinite(rate)&&rate>0&&rate*seconds<=20,"Gravity-gradient bound is ill-conditioned");
  double c=Math.cosh(rate*seconds),s=Math.sinh(rate*seconds);
  double position=c*p+s/rate*v,velocity=rate*s*p+c*v;
  require(Double.isFinite(position)&&Double.isFinite(velocity)&&position<=tube&&velocity<=1e-6,"Independent coasts exceed numerical-agreement envelope");
  return new Certificate(position,velocity,seconds);
 }
 private static void require(boolean ok,String message){if(!ok)throw new IllegalArgumentException(message);}
}
