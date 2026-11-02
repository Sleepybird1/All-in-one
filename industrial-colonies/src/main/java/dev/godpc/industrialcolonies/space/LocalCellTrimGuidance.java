package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Stateless inner-cell position feedback for the qualified 36 float additions
 * per tick. Caller must prove current telemetry, actuator authority, clear path,
 * inner-cell containment and stopping margin. This is not orbital navigation. */
public final class LocalCellTrimGuidance {
 private LocalCellTrimGuidance(){}
 public static V acceleration(V position,V velocity,V target,double acceleration,double speed,double tolerance){
  require(position!=null&&velocity!=null&&target!=null&&position.finite()&&velocity.finite()&&target.finite(),"Finite current local state required");
  require(Double.isFinite(acceleration)&&acceleration>0&&acceleration<=.5&&Double.isFinite(speed)&&speed>0&&speed<=2&&Double.isFinite(tolerance)&&tolerance>0&&tolerance<=.1,"Bounded local trim limits required");
  V error=target.sub(position);require(error.finite()&&error.length()<=256&&velocity.length()<=speed*2,"Outside local trim envelope");
  if(error.length()<tolerance)return velocity.mul(-2).capped(acceleration);
  double axisSpeed=speed/Math.sqrt(3),axisTolerance=tolerance/Math.sqrt(3),axisAcceleration=acceleration/Math.sqrt(3);
  V desired=new V(axis(position.x(),error.x(),axisSpeed,axisTolerance,axisAcceleration),axis(position.y(),error.y(),axisSpeed,axisTolerance,axisAcceleration),axis(position.z(),error.z(),axisSpeed,axisTolerance,axisAcceleration));
  return desired.sub(velocity).mul(1.8).capped(acceleration);
 }
 private static double axis(double position,double error,double speed,double tolerance,double acceleration){
  if(Math.abs(error)<tolerance)return 0;
  // One ULP per solver iteration is deliberately above the half-ULP dead zone.
  double minimum=Math.ulp((float)position)*720.0;
  require(Double.isFinite(minimum)&&minimum<=speed,"Speed budget cannot resolve native float movement");
  double brakingSpeed=.5*Math.sqrt(2*acceleration*Math.abs(error));
  return Math.copySign(Math.min(speed,Math.max(minimum,Math.min(brakingSpeed,Math.abs(error)*.8/1.8))),error);
 }
 private static void require(boolean valid,String why){if(!valid)throw new IllegalArgumentException(why);}
}
