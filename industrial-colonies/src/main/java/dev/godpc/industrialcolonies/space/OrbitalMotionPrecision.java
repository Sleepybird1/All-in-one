package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Conservative qualification for the installed Rapier configuration only.
 * Native r70 reproduced174 coordinate steps with36 float additions per tick.
 * This is an admission check, never a replacement integrator or movement command.
 */
public final class OrbitalMotionPrecision {
 private OrbitalMotionPrecision(){}
 public record Estimate(V representedPosition,V representedVelocity,double positionError,double velocityError){}
 public static Estimate estimate(V position,V velocity,int substeps,int solverIterations){
  if(substeps!=2||solverIterations!=18)throw new IllegalArgumentException("Unqualified native physics configuration");
  if(position==null||velocity==null||!position.finite()||!velocity.finite())throw new IllegalArgumentException("Finite native motion required");
  float dt=(float)(.05/36);double[] p={position.x(),position.y(),position.z()},v={velocity.x(),velocity.y(),velocity.z()};double[] start=new double[3],end=new double[3];
  for(int axis=0;axis<3;axis++){
   float at=(float)p[axis],step=(float)((float)v[axis]*dt);start[axis]=at;
   if(!Float.isFinite(at)||!Float.isFinite(step))throw new IllegalArgumentException("Native float overflow");
   for(int n=0;n<36;n++)at=(float)(at+step);end[axis]=at;
   if(!Float.isFinite(at))throw new IllegalArgumentException("Native motion overflow");
  }
  V represented=new V(start[0],start[1],start[2]);
  V resolved=new V((end[0]-start[0])*20,(end[1]-start[1])*20,(end[2]-start[2])*20);
  return new Estimate(represented,resolved,represented.sub(position).length(),resolved.sub(velocity).length());
 }
 public static Estimate requireResolved(V position,V velocity,int substeps,int solverIterations){
  var result=estimate(position,velocity,substeps,solverIterations);
  if(result.positionError()>1e-3||result.velocityError()>1e-3)throw new IllegalStateException("Native motion below qualified coordinate precision");
  return result;
 }
}
