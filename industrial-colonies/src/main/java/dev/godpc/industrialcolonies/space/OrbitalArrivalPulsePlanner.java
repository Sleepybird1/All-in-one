package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.utils.PVCoordinates;

/** Read-only finite pulse and inward-retreat proposal from a settled boundary.
 * Includes actual-coordinate float integration and nonneutral retreat impulse.
 * Prescribed response/fixed hull only: not actuator, clearance, live settling,
 * destination placement, ownership or encounter authority. Never moves a body. */
public final class OrbitalArrivalPulsePlanner {
 private OrbitalArrivalPulsePlanner(){}
 public record Proposal(V queuedForce,V escapeTarget,V modeledPosition,V modeledVelocity,
   CartesianOrbit postEscapeOrbit,List<CartesianOrbit> segments,int ticks,double velocityError,int iterations){
  public Proposal{segments=List.copyOf(segments);}
 }
 private static final int POWERED=100,SETTLE=100;
 private static final class Trial {
  CartesianOrbit orbit;V p,v=V.ZERO,queued=V.ZERO,target;int ticks;final int budget;final List<CartesianOrbit> segments=new ArrayList<>();
  Trial(CartesianOrbit source,V position,int powered){orbit=source;p=position;budget=powered+2100;}
  void step(V acceleration,V center,double side,double hull,double mass){
   require(acceleration.finite()&&acceleration.length()<=.10000001&&ticks<budget,"Bounded finite arrival control required");
   var r=OrbitalFiniteBurnStep.predict(p,v,queued,V.ZERO,mass,center,side,hull);var pv=orbit.getPVCoordinates();
   var segment=new CartesianOrbit(new PVCoordinates(pv.getPosition(),pv.getVelocity().add(vector(r.orbitalImpulse()))),orbit.getFrame(),orbit.getDate(),orbit.getMu());
   qualified(segment);segments.add(segment);orbit=segment.shiftedBy(.05);p=r.localPosition();v=r.localVelocity();queued=acceleration.mul(mass);ticks++;
   require(2*(p.sub(center).length()+hull)-side<.1,"Finite arrival leaves bounded coupling region");
  }
 }
 public static Proposal solve(CartesianOrbit source,CartesianOrbit targetAtArrival,V position,V center,
   double side,double hull,double mass,V desiredRelativeVelocity){
  return solve(source,targetAtArrival,position,center,side,hull,mass,desiredRelativeVelocity,POWERED);
 }
 public static Proposal solve(CartesianOrbit source,CartesianOrbit targetAtArrival,V position,V center,
   double side,double hull,double mass,V desiredRelativeVelocity,int poweredTicks){
  require(poweredTicks>=20&&poweredTicks<=800,"Bounded20..800tick pulse required");
  Objects.requireNonNull(source);Objects.requireNonNull(targetAtArrival);qualified(source);qualified(targetAtArrival);
  require(source.getFrame()==targetAtArrival.getFrame()&&source.getFrame().isPseudoInertial()&&source.getMu()==targetAtArrival.getMu(),"Exact common inertial frame and gravity required");
  double horizon=targetAtArrival.getDate().durationFrom(source.getDate());require(Double.isFinite(horizon)&&horizon>=20&&horizon<=1800,"Bounded20..1800second arrival epoch required");
  require(position!=null&&center!=null&&position.finite()&&center.finite()&&side==256&&Double.isFinite(hull)&&hull>0&&hull<128&&Double.isFinite(mass)&&mass>0&&mass<=10000,"Qualified source cell and finite geometry required");
  double overrun=2*(position.sub(center).length()+hull)-side;require(overrun>0&&overrun<.1,"Settled first-crossing boundary required");
  require(desiredRelativeVelocity!=null&&desiredRelativeVelocity.finite()&&desiredRelativeVelocity.length()>.001&&desiredRelativeVelocity.length()<=.08,"Bounded nonzero arrival velocity required");
  double maxForce=mass*.1;V force=idealImpulse(source,targetAtArrival,desiredRelativeVelocity).mul(mass/(poweredTicks*.05));
  require(force.length()<=maxForce,"Initial finite arrival force exceeds budget");
  for(int iteration=0;iteration<16;iteration++){
   var trial=simulate(source,position,center,side,hull,mass,force,poweredTicks);V error=residual(trial.orbit,targetAtArrival,desiredRelativeVelocity);
   if(error.length()<.0002)return new Proposal(force,trial.target,trial.p,trial.v,trial.orbit,trial.segments,trial.ticks,error.length(),iteration);
   V[] columns=new V[3];double h=.01;
   for(int axis=0;axis<3;axis++){V delta=axis(axis,h);var plus=simulate(source,position,center,side,hull,mass,force.add(delta),poweredTicks);var minus=simulate(source,position,center,side,hull,mass,force.sub(delta),poweredTicks);columns[axis]=residual(plus.orbit,targetAtArrival,desiredRelativeVelocity).sub(residual(minus.orbit,targetAtArrival,desiredRelativeVelocity)).mul(.5/h);}
   V correction=linear(columns,error.mul(-1));boolean improved=false;
   for(int backtrack=0;backtrack<12;backtrack++){
    V candidate=force.add(correction.mul(Math.scalb(1.,-backtrack)));if(candidate.length()>maxForce)continue;
    try{var next=simulate(source,position,center,side,hull,mass,candidate,poweredTicks);if(residual(next.orbit,targetAtArrival,desiredRelativeVelocity).length()<error.length()){force=candidate;improved=true;break;}}catch(IllegalArgumentException infeasible){}
   }
   require(improved,"No improving bounded pulse/retreat proposal");
  }
  throw new IllegalArgumentException("Finite arrival solve budget exhausted");
 }
 /** Ideal impulse only for selecting a prospective staging direction; no authority. */
 public static V idealImpulse(CartesianOrbit source,CartesianOrbit targetAtArrival,V desired){
  require(source!=null&&targetAtArrival!=null&&desired!=null&&desired.finite()&&source.getFrame()==targetAtArrival.getFrame()&&source.getMu()==targetAtArrival.getMu(),"Finite matching ideal-impulse inputs required");
  qualified(source);qualified(targetAtArrival);double dt=targetAtArrival.getDate().durationFrom(source.getDate());require(Double.isFinite(dt)&&dt>0&&dt<=1800,"Bounded future impulse epoch required");
  V base=residual(source,targetAtArrival,desired);V[] columns=new V[3];double h=.001;
  for(int axis=0;axis<3;axis++){V delta=axis(axis,h);columns[axis]=residual(add(source,delta),targetAtArrival,desired).sub(residual(add(source,delta.mul(-1)),targetAtArrival,desired)).mul(.5/h);}
  return linear(columns,base.mul(-1));
 }
 private static Trial simulate(CartesianOrbit source,V position,V center,double side,double hull,double mass,V force,int poweredTicks){
  require(force.finite()&&force.length()<=mass*.1,"Finite pulse force budget exceeded");var t=new Trial(source,position,poweredTicks);
  for(int i=0;i<poweredTicks;i++)t.step(force.mul(1/mass),center,side,hull,mass);for(int i=0;i<SETTLE;i++)t.step(V.ZERO,center,side,hull,mass);
  require(t.v.length()<1e-5,"Modeled pulse did not settle");V radial=t.p.sub(center);t.target=t.p.sub(radial.mul(2/radial.length()));int stable=0;
  for(int i=0;i<1950;i++){
   t.step(LocalCellTrimGuidance.acceleration(t.p,t.v,t.target,.1,.4,.055),center,side,hull,mass);
   if(t.p.sub(t.target).length()<.06&&t.v.length()<1e-6)stable++;else stable=0;
   if(stable>=20){for(int n=0;n<41;n++)t.step(V.ZERO,center,side,hull,mass);require(t.v.length()<1e-5&&2*(t.p.sub(center).length()+hull)-side<-3,"Modeled retreat did not settle inside source cell");return t;}
  }
  throw new IllegalArgumentException("Modeled retreat time budget exhausted");
 }
 private static V residual(CartesianOrbit source,CartesianOrbit target,V desired){double seconds=target.getDate().durationFrom(source.getDate());require(seconds>=0,"Maneuver exceeds committed arrival epoch");return vector(source.shiftedBy(seconds).getPVCoordinates().getVelocity().subtract(target.getPVCoordinates().getVelocity())).sub(desired);}
 private static CartesianOrbit add(CartesianOrbit orbit,V impulse){var p=orbit.getPVCoordinates();return new CartesianOrbit(new PVCoordinates(p.getPosition(),p.getVelocity().add(vector(impulse))),orbit.getFrame(),orbit.getDate(),orbit.getMu());}
 private static V linear(V[] c,V e){double det=c[0].dot(c[1].cross(c[2])),scale=c[0].length()*c[1].length()*c[2].length();require(Double.isFinite(det)&&Double.isFinite(scale)&&scale>0&&Math.abs(det)>scale*1e-8,"Unresolved finite arrival response");V v=new V(e.dot(c[1].cross(c[2]))/det,c[0].dot(e.cross(c[2]))/det,c[0].dot(c[1].cross(e))/det);require(v.finite(),"Finite arrival inverse overflow");return v;}
 private static V axis(int n,double h){return new V(n==0?h:0,n==1?h:0,n==2?h:0);}
 private static Vector3D vector(V v){return new Vector3D(v.x(),v.y(),v.z());}
 private static V vector(Vector3D v){return new V(v.getX(),v.getY(),v.getZ());}
 private static void qualified(CartesianOrbit o){require(!o.hasNonKeplerianAcceleration()&&Double.isFinite(o.getA())&&o.getA()>0&&Double.isFinite(o.getE())&&o.getE()>=0&&o.getE()<1&&Double.isFinite(o.getMu())&&o.getMu()>0,"Unforced finite elliptic orbit required");}
 private static void require(boolean value,String message){if(!value)throw new IllegalArgumentException(message);}
}
