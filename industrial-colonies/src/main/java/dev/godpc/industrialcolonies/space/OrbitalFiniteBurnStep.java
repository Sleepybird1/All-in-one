package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Read-only one-tick model for the qualified native two-substep/18-iteration
 * profile. One participating body, fixed mass and cell, no collisions or other
 * net forces. Input thrust is already queued, not the newly requested throttle.
 * The second force direction uses first-order spin, so this is a prediction,
 * not an exact simulator or a clearance/actuator authorization. */
public final class OrbitalFiniteBurnStep {
 private OrbitalFiniteBurnStep(){}
 public record Result(V localPosition,V localVelocity,V orbitalImpulse){}
 public static Result predict(V position,V velocity,V queuedForce,V angularVelocity,
   double mass,V cellCenter,double cellSide,double refreshedHullDiagonal){
  finite(position);finite(velocity);finite(queuedForce);finite(angularVelocity);finite(cellCenter);
  require(Double.isFinite(mass)&&mass>0&&Double.isFinite(cellSide)&&cellSide>0,"Positive mass and cell size required");
  require(Double.isFinite(refreshedHullDiagonal)&&refreshedHullDiagonal>0&&refreshedHullDiagonal<cellSide/2,"Hull must fit qualified cell");
  require(velocity.length()<=128&&angularVelocity.length()<=.25&&queuedForce.length()/mass<=100,"Outside short-step model envelope");
  V force=queuedForce,impulse=V.ZERO;
  inside(position,cellCenter,cellSide);
  for(int substep=0;substep<2;substep++){
   velocity=rounded(velocity.add(force.mul(.025/mass)));
   var split=OrbitalVelocityCoupling.split(position.sub(cellCenter),velocity,refreshedHullDiagonal,cellSide);
   impulse=impulse.add(split.orbitContribution());velocity=rounded(split.remainingLocalVelocity());
   // Rapier integrates the float position at each solver iteration. A single
   // double position += velocity*.025 incorrectly predicts slow displacement.
   for(int iteration=0;iteration<18;iteration++)position=rounded(position.add(rounded(velocity.mul((float)(.025/18)))));
   inside(position,cellCenter,cellSide);
   force=force.add(angularVelocity.cross(force).mul(.025));
  }
  finite(impulse);return new Result(position,velocity,impulse);
 }
 /** Recompute bounds from the current quaternion and native expanded local box.
  * A server sample's cached global diagonal can still belong to the prior pose.
  * Use native float quaternion values without renormalizing them. */
 public static double refreshedHullDiagonal(V size,double x,double y,double z,double w){
  finite(size);require(size.x()>0&&size.y()>0&&size.z()>0,"Positive native expanded dimensions required");
  double squared=x*x+y*y+z*z+w*w;
  require(Double.isFinite(squared)&&Math.abs(squared-1)<1e-5,"Near-unit native quaternion required");
  double xx=Math.abs(w*w+x*x-y*y-z*z)*size.x()+Math.abs(2*(x*y-z*w))*size.y()+Math.abs(2*(x*z+y*w))*size.z();
  double yy=Math.abs(2*(x*y+z*w))*size.x()+Math.abs(w*w-x*x+y*y-z*z)*size.y()+Math.abs(2*(y*z-x*w))*size.z();
  double zz=Math.abs(2*(x*z-y*w))*size.x()+Math.abs(2*(y*z+x*w))*size.y()+Math.abs(w*w-x*x-y*y+z*z)*size.z();
  double result=new V(xx,yy,zz).length();require(Double.isFinite(result),"Bounds overflow");return result;
 }
 private static V rounded(V v){V r=new V((float)v.x(),(float)v.y(),(float)v.z());finite(r);return r;}
 private static void inside(V p,V c,double side){V d=p.sub(c);double half=(side+1)/2;require(Math.abs(d.x())<half&&Math.abs(d.y())<half&&Math.abs(d.z())<half,"Model leaves native cell");}
 private static void finite(V v){require(v!=null&&v.finite(),"Finite vector required");}
 private static void require(boolean ok,String message){if(!ok)throw new IllegalArgumentException(message);}
}
