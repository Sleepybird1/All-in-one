package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.utils.PVCoordinates;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;

/** Read-only complete local-maneuver screen from current measured input.
 * Prescribed fixed-hull response only; live control must solve again after the
 * actual crossing and retreat, check clearance, and observe natural settling. */
public final class OrbitalArrivalManeuverPlanner {
 private OrbitalArrivalManeuverPlanner(){}
 public record Proposal(V desiredVelocity,V radial,V stagingPoint,V arrivalGoal,
   V modeledReceivingPosition,V modeledReceivingVelocity,int maneuverTicks,int horizonTicks,
   List<CartesianOrbit> segments){public Proposal{segments=List.copyOf(segments);}}
 private static final class State {
  CartesianOrbit orbit;V p,v=V.ZERO,queued=V.ZERO,impulse=V.ZERO;int ticks;
  final V center;final double hull,mass;final int horizon;final List<CartesianOrbit> segments=new ArrayList<>();
  State(CartesianOrbit orbit,V p,V center,double hull,double mass,int horizon){this.orbit=orbit;this.p=p;this.center=center;this.hull=hull;this.mass=mass;this.horizon=horizon;}
  double overrun(){return 2*(p.sub(center).length()+hull)-256;}
  void step(V a){
   require(ticks<horizon&&a.finite()&&a.length()<=.10000001,"Bounded whole-maneuver control required");
   var r=OrbitalFiniteBurnStep.predict(p,v,queued,V.ZERO,mass,center,256,hull);var pv=orbit.getPVCoordinates();
   var segment=new CartesianOrbit(new PVCoordinates(pv.getPosition(),pv.getVelocity().add(j(r.orbitalImpulse()))),orbit.getFrame(),orbit.getDate(),orbit.getMu());
   segments.add(segment);orbit=segment.shiftedBy(.05);p=r.localPosition();v=r.localVelocity();queued=a.mul(mass);impulse=impulse.add(r.orbitalImpulse());ticks++;
   require(overrun()<.1,"Modeled maneuver exceeds coupling boundary");
  }
  void coast(int n){for(int i=0;i<n;i++)step(V.ZERO);}
  void move(V goal,double speed,int budget){
   int stable=0;for(int i=0;i<budget;i++){
    step(LocalCellTrimGuidance.acceleration(p,v,goal,.1,speed,.055));
    if(p.sub(goal).length()<.06&&v.length()<1e-6)stable++;else stable=0;
    if(stable>=20){coast(101);require(v.length()<1e-5,"Modeled local motion did not settle");return;}
   }
   throw new IllegalArgumentException("Whole-maneuver local positioning budget exhausted");
  }
 }
 public static Proposal screen(CartesianOrbit source,CartesianOrbit target,V position,V center,double hull,double mass,
   V receivingCenter,V receivingOffset,V desired,int horizonTicks){
  return screen(source,target,position,center,hull,mass,receivingCenter,receivingOffset,desired,horizonTicks,100);
 }
 public static Proposal screen(CartesianOrbit source,CartesianOrbit target,V position,V center,double hull,double mass,
   V receivingCenter,V receivingOffset,V desired,int horizonTicks,int poweredTicks){
  require(poweredTicks>=20&&poweredTicks<=800,"Bounded20..800tick pulse required");
  Objects.requireNonNull(source);Objects.requireNonNull(target);
  require(source.getFrame()==target.getFrame()&&source.getMu()==target.getMu()&&source.getDate().equals(target.getDate()),"Synchronized matching inertial source/target required");
  require(horizonTicks>=6000&&horizonTicks<=18000&&position!=null&&center!=null&&receivingCenter!=null&&receivingOffset!=null
   &&position.finite()&&center.finite()&&receivingCenter.finite()&&receivingOffset.finite()&&Double.isFinite(hull)&&hull>0&&hull<128&&Double.isFinite(mass)&&mass>0&&mass<=10000,"Bounded current geometry required");
  require(desired!=null&&desired.finite()&&desired.length()>.001&&desired.length()<=.08,"Bounded desired receiving velocity required");
  require(position.sub(center).length()+hull<128,"Initial source must be inside orbital coupling boundary");
  double seconds=horizonTicks*.05;var arrival=target.shiftedBy(seconds);
  V impulse=OrbitalArrivalPulsePlanner.idealImpulse(source.shiftedBy(220),arrival,desired);
  require(impulse.length()>.06,"Insufficient correction headroom beyond slow crossing");
  V radial=impulse.mul(1/impulse.length()),stage=center.add(radial.mul(128-hull-2));var s=new State(source,position,center,hull,mass,horizonTicks);
  s.move(stage,2,6000);require(s.impulse.length()<1e-6,"Staging changed orbital state");
  boolean crossed=false;for(int i=0;i<2000;i++){
   if(s.overrun()>0){crossed=true;s.step(V.ZERO);break;}s.step(radial.mul(.075).sub(s.v).mul(2).capped(.1));
  }
  require(crossed,"Modeled boundary crossing time budget exhausted");s.coast(100);require(s.v.length()<1e-5,"Crossing did not settle");
  var pulse=OrbitalArrivalPulsePlanner.solve(s.orbit,arrival,s.p,center,256,hull,mass,desired,poweredTicks);
  for(int i=0;i<poweredTicks;i++)s.step(pulse.queuedForce().mul(1/mass));s.coast(100);require(s.v.length()<1e-5,"Pulse did not settle");
  V escape=s.p.sub(s.p.sub(center).mul(2/s.p.sub(center).length()));s.move(escape,.4,2000);require(s.overrun()<-3,"Retreat remains inside coupling boundary");
  var future=s.orbit.shiftedBy(seconds-s.ticks*.05).getPVCoordinates();V separation=v(future.getPosition().subtract(arrival.getPVCoordinates().getPosition()));
  V goal=center.add(receivingOffset.sub(separation));require(goal.sub(center).length()+hull<127.5,"Final receiving position outside source cell: requiredRadius="+(goal.sub(center).length()+hull));
  V before=s.impulse;s.move(goal,2,6000);require(s.impulse.sub(before).length()<1e-6,"Final repositioning changed orbit");
  int finished=s.ticks;require(finished<horizonTicks-200,"Insufficient actual-settling timetable reserve");s.coast(horizonTicks-s.ticks);
  V actual=v(s.orbit.getPVCoordinates().getVelocity().subtract(arrival.getPVCoordinates().getVelocity()));
  V received=receivingCenter.add(v(s.orbit.getPVCoordinates().getPosition().subtract(arrival.getPVCoordinates().getPosition()))).add(s.p.sub(center));
  OrbitalMotionPrecision.requireResolved(received,actual,2,18);
  require(actual.sub(desired).length()<.002&&actual.length()<=.08&&s.v.length()<1e-5,"Modeled arrival outside speed/settling envelope");
  return new Proposal(desired,radial,stage,goal,received,actual,finished,horizonTicks,s.segments);
 }
 private static Vector3D j(V v){return new Vector3D(v.x(),v.y(),v.z());}
 private static V v(Vector3D v){return new V(v.getX(),v.getY(),v.getZ());}
 private static void require(boolean valid,String message){if(!valid)throw new IllegalArgumentException(message);}
}
