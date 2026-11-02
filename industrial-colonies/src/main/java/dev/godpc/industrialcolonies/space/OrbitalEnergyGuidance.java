package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Pure calculation extracted from the accepted native energy burn.
 * All vectors must already share the celestial frame. Pending velocity is measured
 * native local motion converted into that frame, not an assumed extra impulse.
 * This does not certify terrain clearance, fuel reserve, engine authority or a route. */
public final class OrbitalEnergyGuidance {
 private OrbitalEnergyGuidance(){}
 public enum Band { WARMUP, CRUISE, TRIM, CUTOFF }
 public record Solution(V forward,V up,double specificEnergy,double correctedAxis) {}
 public static Solution solve(V position,V velocity,V pendingVelocity,double mu,double outwardBias,int normalSign){
  require(position!=null&&velocity!=null&&pendingVelocity!=null&&position.finite()&&velocity.finite()&&pendingVelocity.finite(),"Finite common-frame vectors required");
  require(Double.isFinite(mu)&&mu>0&&Double.isFinite(outwardBias)&&Math.abs(outwardBias)<Math.PI/2&&(normalSign==1||normalSign==-1),"Invalid orbital guidance parameters");
  V radial=unit(position),along=unit(velocity);
  V outward=unit(radial.sub(along.mul(radial.dot(along))));
  V forward=along.mul(Math.cos(outwardBias)).add(outward.mul(Math.sin(outwardBias)));
  V up=unit(position.cross(velocity)).mul(normalSign);
  double energy=velocity.dot(velocity)/2-mu/position.length();
  V total=velocity.add(pendingVelocity);double correctedEnergy=total.dot(total)/2-mu/position.length();
  require(Double.isFinite(energy)&&Double.isFinite(correctedEnergy)&&correctedEnergy<0,"Bound elliptic corrected energy required");
  double axis=-mu/(2*correctedEnergy);require(Double.isFinite(axis)&&axis>0&&forward.finite(),"Invalid energy solution");
  return new Solution(forward,up,energy,axis);
 }
 public static double axisForRotation(double mu,double angularRate){
  require(Double.isFinite(mu)&&mu>0&&Double.isFinite(angularRate)&&angularRate>0,"Measured positive rotation and gravity required");
  double axis=Math.cbrt(mu/(angularRate*angularRate));require(Double.isFinite(axis)&&axis>0,"Invalid rotation target");return axis;
 }
 public static Band band(double correctedAxis,double targetAxis,double trimWindow,double cutoffMargin,boolean trimLatched,boolean pairedReady){
  for(double value:new double[]{correctedAxis,targetAxis,trimWindow,cutoffMargin})require(Double.isFinite(value)&&value>0,"Positive finite burn limits required");
  require(cutoffMargin<trimWindow&&trimWindow<targetAxis,"Inconsistent burn limits");
  if(!pairedReady)return Band.WARMUP;
  if(correctedAxis>=targetAxis-cutoffMargin)return Band.CUTOFF;
  return trimLatched||correctedAxis>=targetAxis-trimWindow?Band.TRIM:Band.CRUISE;
 }
 private static V unit(V vector){double length=vector.length();require(Double.isFinite(length)&&length>1e-12,"Degenerate orbital basis");return vector.mul(1/length);}
 private static void require(boolean valid,String reason){if(!valid)throw new IllegalArgumentException(reason);}
}
