package dev.godpc.industrialcolonies.space;

import java.util.ArrayDeque;
import java.util.Objects;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.utils.TimeStampedAngularCoordinates;

/** Read-only continuous clearance bound within an immutable two-body coast
 * model and constant-spin sphere/cube geometry. This is not finite-burn,
 * terrain/traffic, native frame-transition or actual flight certification. */
public final class OrbitalTrajectoryClearance {
 private OrbitalTrajectoryClearance(){}
 public record Certificate(double minimumModelMargin,int samples,double horizonSeconds,double speedBound){}
 private record Interval(double start,double end,double startMargin,double endMargin){}
 public static Certificate certify(CartesianOrbit orbit,TimeStampedAngularCoordinates rotation,
                                  double radius,boolean sphere,double requiredSurfaceDistance,double seconds){
  Objects.requireNonNull(orbit);Objects.requireNonNull(rotation);
  for(double n:new double[]{radius,requiredSurfaceDistance,seconds})require(Double.isFinite(n)&&n>0,"Positive finite clearance inputs required");
  require(seconds<=3600,"Bounded one-hour clearance horizon required");
  double a=orbit.getA(),e=orbit.getE(),mu=orbit.getMu();
  require(!orbit.hasNonKeplerianAcceleration()&&Double.isFinite(a)&&a>0&&Double.isFinite(e)&&e>=0&&e<1&&Double.isFinite(mu)&&mu>0,"Unforced elliptic orbit required");
  double periapsis=a*(1-e),apoapsis=a*(1+e),maximumSpeed=Math.sqrt(mu*(2/periapsis-1/a));
  double spin=rotation.getRotationRate().getNorm();
  require(Double.isFinite(spin)&&rotation.getRotationAcceleration().getNorm()==0,"Only constant-spin rotation is qualified");
  require(Double.isFinite(apoapsis)&&Double.isFinite(maximumSpeed)&&32*Math.ulp(apoapsis)<.001,"Insufficient finite orbital precision");
  if(sphere){double margin=periapsis-radius-requiredSurfaceDistance-.001;require(margin>=0,"Sphere clearance violated");return new Certificate(margin,0,seconds,maximumSpeed);}
  double bound=maximumSpeed+spin*apoapsis;require(Double.isFinite(bound)&&bound>0,"Finite cube-relative speed bound required");
  double epoch=orbit.getDate().durationFrom(rotation.getDate());require(Double.isFinite(epoch),"Finite rotation epoch required");
  java.util.function.DoubleUnaryOperator margin=t->{
   var p=rotation.rotationShiftedBy(epoch+t).applyInverseTo(orbit.shiftedBy(t).getPVCoordinates().getPosition());
   double dx=Math.max(0,Math.abs(p.getX())-radius),dy=Math.max(0,Math.abs(p.getY())-radius),dz=Math.max(0,Math.abs(p.getZ())-radius);
   double value=Math.sqrt(dx*dx+dy*dy+dz*dz)-requiredSurfaceDistance-.001;
   require(Double.isFinite(value)&&value>=0,"Cube clearance violated at "+t+" seconds");return value;
  };
  var pending=new ArrayDeque<Interval>();pending.push(new Interval(0,seconds,margin.applyAsDouble(0),margin.applyAsDouble(seconds)));
  int samples=2;double minimum=Double.POSITIVE_INFINITY;
  while(!pending.isEmpty()){
   var interval=pending.pop();
   // Distance to a closed cube is 1-Lipschitz. Every point is at most half
   // this interval from an endpoint; orbital speed + spin*apoapsis bounds
   // motion in the rotating frame even at a face/edge/corner transition.
   double lower=Math.min(interval.startMargin(),interval.endMargin())-bound*(interval.end()-interval.start())/2;
   if(lower>=0){minimum=Math.min(minimum,lower);continue;}
   require(samples<131073,"Clearance subdivision budget exhausted");
   double mid=(interval.start()+interval.end())/2;
   require(mid>interval.start()&&mid<interval.end(),"Clearance interval precision exhausted");
   double value=margin.applyAsDouble(mid);samples++;
   pending.push(new Interval(mid,interval.end(),value,interval.endMargin()));pending.push(new Interval(interval.start(),mid,interval.startMargin(),value));
  }
  return new Certificate(minimum,samples,seconds,bound);
 }
 private static void require(boolean valid,String reason){if(!valid)throw new IllegalArgumentException(reason);}
}
