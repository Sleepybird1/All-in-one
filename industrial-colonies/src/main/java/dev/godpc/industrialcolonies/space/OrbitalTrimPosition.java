package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Read-only candidate geometry for an outward orbital impulse. Neither the
 * path to these points nor the maneuver has been authorized or flown. */
public final class OrbitalTrimPosition {
 private OrbitalTrimPosition(){}
 public record Candidate(V staging,V pulsePosition,double boundaryOverrun,
                         OrbitalTrimPulsePlanner.Proposal pulse){}
 public static Candidate propose(V center,double side,double hull,double mass,V impulse,
                                 int poweredTicks,int settleTicks,double maximumForce){
  require(center!=null&&center.finite(),"Finite native cell center required");
  require(Double.isFinite(side)&&side>0&&Double.isFinite(hull)&&hull>0&&hull+4<side/2,"Hull and staging margin must fit cell");
  require(impulse!=null&&impulse.finite()&&impulse.length()>1e-8&&impulse.length()<=1,"Nonzero bounded trim required");
  V direction=impulse.mul(1/impulse.length());
  double radius=side/2-hull;
  V staging=rounded(center.add(direction.mul(radius-2)));
  V pulse=rounded(center.add(direction.mul(radius+.2)));
  double overrun=2*(pulse.sub(center).length()+hull)-side;
  require(overrun>=.1&&overrun<=.8,"Native float position cannot resolve the gentle coupling band");
  require(staging.sub(center).length()+hull<=side/2-1.5,"Staging float error exceeds inner margin");
  // A conservative sphere encloses the hull. This checks cell geometry only;
  // it is not a collision/planet clearance certificate or a movement command.
  for(V p:new V[]{staging,pulse}){
   V offset=p.sub(center);double half=(side+1)/2;
   require(Math.abs(offset.x())+hull<half&&Math.abs(offset.y())+hull<half&&Math.abs(offset.z())+hull<half,"Conservative hull leaves native cell");
  }
  var plan=OrbitalTrimPulsePlanner.solve(pulse,center,side,hull,mass,impulse,poweredTicks,settleTicks,maximumForce);
  return new Candidate(staging,pulse,overrun,plan);
 }
 private static V rounded(V p){return new V((float)p.x(),(float)p.y(),(float)p.z());}
 private static void require(boolean ok,String why){if(!ok)throw new IllegalArgumentException(why);}
}
