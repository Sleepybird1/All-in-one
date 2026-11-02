package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Read-only inverse of the qualified finite-burn model for one constant queued
 * force pulse followed by unpowered settling. Zero initial local velocity/spin,
 * fixed mass/cell/hull, no collisions or other force. Continuous force is an
 * ideal actuator request: real jet quantization, queue timing, attitude, orbital
 * propagation, clearance and live feedback still require separate qualification. */
public final class OrbitalTrimPulsePlanner {
 private OrbitalTrimPulsePlanner(){}
 public record Proposal(V queuedForce,V orbitalImpulse,V localPosition,V localVelocity,
                        double impulseError,int poweredTicks,int settleTicks,int iterations){}
 private record Trial(V impulse,V position,V velocity){}
 public static Proposal solve(V position,V cellCenter,double cellSide,double hull,double mass,
   V desiredImpulse,int poweredTicks,int settleTicks,double maximumForce){
  require(desiredImpulse!=null&&desiredImpulse.finite()&&desiredImpulse.length()<=1,"Finite trim impulse up to1block/s required");
  require(poweredTicks>=1&&poweredTicks<=200&&settleTicks>=1&&settleTicks<=400,"Bounded pulse and settle durations required");
  require(Double.isFinite(mass)&&mass>0&&Double.isFinite(maximumForce)&&maximumForce>0&&maximumForce/mass<=.5,"Finite low-acceleration force budget required");
  V force=desiredImpulse.mul(mass/(poweredTicks*.05));
  require(force.length()<=maximumForce,"Initial trim estimate exceeds force budget");
  for(int iteration=0;iteration<=12;iteration++){
   var trial=simulate(position,cellCenter,cellSide,hull,mass,force,poweredTicks,settleTicks);
   V error=desiredImpulse.sub(trial.impulse());
   if(error.length()<=1e-6){
    require(trial.velocity().length()<=1e-5,"Pulse has not settled within the modeled window");
    return new Proposal(force,trial.impulse(),trial.position(),trial.velocity(),error.length(),poweredTicks,settleTicks,iteration);
   }
   require(iteration<12,"Bounded pulse inverse did not converge");
   double h=Math.max(.001,maximumForce*1e-4);V[] columns=new V[3];
   for(int axis=0;axis<3;axis++){
    V d=axis==0?new V(h,0,0):axis==1?new V(0,h,0):new V(0,0,h);
    columns[axis]=simulate(position,cellCenter,cellSide,hull,mass,force.add(d),poweredTicks,settleTicks).impulse()
     .sub(simulate(position,cellCenter,cellSide,hull,mass,force.sub(d),poweredTicks,settleTicks).impulse()).mul(.5/h);
   }
   V correction=linear(columns,error);boolean improved=false;
   for(int backtrack=0;backtrack<12;backtrack++){
    V candidate=force.add(correction.mul(Math.scalb(1.0,-backtrack)));
    if(candidate.length()>maximumForce)continue;
    var next=simulate(position,cellCenter,cellSide,hull,mass,candidate,poweredTicks,settleTicks);
    if(desiredImpulse.sub(next.impulse()).length()<error.length()){force=candidate;improved=true;break;}
   }
   require(improved,"No improving bounded trim pulse");
  }
  throw new AssertionError("Unreachable pulse inverse");
 }
 private static Trial simulate(V position,V center,double side,double hull,double mass,V force,int powered,int settle){
  V velocity=V.ZERO,impulse=V.ZERO;
  for(int tick=0;tick<powered+settle;tick++){
   var step=OrbitalFiniteBurnStep.predict(position,velocity,tick<powered?force:V.ZERO,V.ZERO,mass,center,side,hull);
   position=step.localPosition();velocity=step.localVelocity();impulse=impulse.add(step.orbitalImpulse());
  }
  return new Trial(impulse,position,velocity);
 }
 private static V linear(V[] c,V rhs){
  double det=c[0].dot(c[1].cross(c[2]));double scale=c[0].length()*c[1].length()*c[2].length();
  require(Double.isFinite(det)&&Double.isFinite(scale)&&scale>0&&Math.abs(det)>scale*1e-8,"No resolved orbital response to a bounded pulse");
  V result=new V(rhs.dot(c[1].cross(c[2]))/det,c[0].dot(rhs.cross(c[2]))/det,c[0].dot(c[1].cross(rhs))/det);
  require(result.finite(),"Trim inverse overflow");return result;
 }
 private static void require(boolean ok,String message){if(!ok)throw new IllegalArgumentException(message);}
}
