package dev.godpc.industrialcolonies.space;

import java.io.*;

/** Authenticated checkpoint pose, compared only after zero-motion verification.
 * Native rigid-body reconstruction rounds quaternions on reload. Cargo and
 * configuration remain exact; this bound permits no meaningful displacement. */
public record FreightHeldPose(double x,double y,double z,double qx,double qy,double qz,double qw) {
 public FreightHeldPose {
  for(double v:new double[]{x,y,z,qx,qy,qz,qw})if(!Double.isFinite(v))throw new IllegalArgumentException("Finite checkpoint pose required");
  double norm=qx*qx+qy*qy+qz*qz+qw*qw;
  if(Math.abs(norm-1)>1e-5)throw new IllegalArgumentException("Near-unit native quaternion required");
 }
 public String canonical(){return x+","+y+","+z+":"+qx+","+qy+","+qz+","+qw;}
 public void verify(FreightHeldPose now){
  if(now==null)throw new IllegalArgumentException("Current pose required");
  double dx=x-now.x,dy=y-now.y,dz=z-now.z;
  if(dx*dx+dy*dy+dz*dz>1e-10)throw new IllegalStateException("Held pose moved beyond10micrometers");
  double a=Math.sqrt(qx*qx+qy*qy+qz*qz+qw*qw),b=Math.sqrt(now.qx*now.qx+now.qy*now.qy+now.qz*now.qz+now.qw*now.qw);
  double same=0,opposite=0;
  double[] old={qx/a,qy/a,qz/a,qw/a},current={now.qx/b,now.qy/b,now.qz/b,now.qw/b};
  for(int i=0;i<4;i++){double d=old[i]-current[i],s=old[i]+current[i];same+=d*d;opposite+=s*s;}
  if(Math.min(same,opposite)>2.5e-13)throw new IllegalStateException("Held orientation changed beyond1microradian");
 }
 void write(DataOutput out)throws IOException{for(double v:new double[]{x,y,z,qx,qy,qz,qw})out.writeDouble(v);}
 static FreightHeldPose read(DataInput in)throws IOException{return new FreightHeldPose(in.readDouble(),in.readDouble(),in.readDouble(),in.readDouble(),in.readDouble(),in.readDouble(),in.readDouble());}
}
