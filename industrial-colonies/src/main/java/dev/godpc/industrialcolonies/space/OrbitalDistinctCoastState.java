package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;
import dev.devce.rocketnautics.shaded.orekit.frames.Frame;
import dev.devce.rocketnautics.shaded.orekit.time.AbsoluteDate;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.utils.PVCoordinates;

/** Immutable inertial initial conditions for both cells; no world mutation. */
public record OrbitalDistinctCoastState(V sourcePosition,V sourceVelocity,V targetPosition,V targetVelocity,double mu){
 public OrbitalDistinctCoastState{
  for(V v:List.of(sourcePosition,sourceVelocity,targetPosition,targetVelocity))if(!v.finite()||!Double.isFinite(v.length()))throw new IllegalArgumentException("Finite coast state required");
  if(!Double.isFinite(mu)||mu<=0||sourcePosition.length()<=0||targetPosition.length()<=0)throw new IllegalArgumentException("Invalid gravity or position");
  for(var o:List.of(orbit(sourcePosition,sourceVelocity,mu),orbit(targetPosition,targetVelocity,mu)))if(!Double.isFinite(o.getA())||o.getA()<=0||!Double.isFinite(o.getE())||o.getE()>=1)throw new IllegalArgumentException("Bound elliptic coast required");
 }
 private static Vector3D j(V v){return new Vector3D(v.x(),v.y(),v.z());}
 private static CartesianOrbit orbit(V p,V v,double mu){return new CartesianOrbit(new PVCoordinates(j(p),j(v)),Frame.getRoot(),AbsoluteDate.J2000_EPOCH,mu);}
 public void verify(V sourceNow,V sourceVelocityNow,V targetNow,V targetVelocityNow,double currentMu,double seconds){
  if(currentMu!=mu||!Double.isFinite(seconds)||seconds<0||seconds>30)throw new IllegalStateException("Coast clock or gravity changed");
  var actual=List.of(sourceNow,sourceVelocityNow,targetNow,targetVelocityNow);
  for(V v:actual)if(!v.finite())throw new IllegalStateException("Nonfinite actual coast state");
  var initial=List.of(orbit(sourcePosition,sourceVelocity,mu),orbit(targetPosition,targetVelocity,mu));
  for(int i=0;i<2;i++){
   var pv=initial.get(i).shiftedBy(seconds).getPVCoordinates();
   if(pv.getPosition().distance(j(actual.get(2*i)))>1e-3||pv.getVelocity().distance(j(actual.get(2*i+1)))>1e-6)throw new IllegalStateException("Native cell no longer follows recorded coast");
  }
 }
 /** An acknowledged applied encounter may outlive its empty departed cell.
  * The caller proves that acknowledgement and original body membership first. */
 public void verifyTarget(V targetNow,V targetVelocityNow,double currentMu,double seconds){
  if(currentMu!=mu||!Double.isFinite(seconds)||seconds<0||seconds>30||targetNow==null||targetVelocityNow==null||!targetNow.finite()||!targetVelocityNow.finite())throw new IllegalStateException("Invalid surviving coast evidence");
  var pv=orbit(targetPosition,targetVelocity,mu).shiftedBy(seconds).getPVCoordinates();
  if(pv.getPosition().distance(j(targetNow))>1e-3||pv.getVelocity().distance(j(targetVelocityNow))>1e-6)throw new IllegalStateException("Surviving target no longer follows recorded coast");
 }
 void write(DataOutput out)throws IOException{for(V v:List.of(sourcePosition,sourceVelocity,targetPosition,targetVelocity)){out.writeDouble(v.x());out.writeDouble(v.y());out.writeDouble(v.z());}out.writeDouble(mu);}
 static OrbitalDistinctCoastState read(DataInput in)throws IOException{return new OrbitalDistinctCoastState(vector(in),vector(in),vector(in),vector(in),in.readDouble());}
 private static V vector(DataInput in)throws IOException{return new V(in.readDouble(),in.readDouble(),in.readDouble());}
}
