package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** World-frame shortest-rotation attitude demand; does not apply torque. */
public final class RendezvousAttitude {
    private RendezvousAttitude() {}
    public record Demand(V angularAcceleration, double angle) {}

    public static Demand demand(V forward,V up,V angularVelocity,V desiredForward,V desiredUp,
                                V targetAngularVelocity,double maxRate,double maxAcceleration) {
        basis(forward,up);basis(desiredForward,desiredUp);
        if(angularVelocity==null||targetAngularVelocity==null||!angularVelocity.finite()
                ||!targetAngularVelocity.finite()||!Double.isFinite(maxRate)||maxRate<=0
                ||!Double.isFinite(maxAcceleration)||maxAcceleration<=0)
            throw new IllegalArgumentException("Invalid angular state or limits");
        V right=up.cross(forward),desiredRight=desiredUp.cross(desiredForward);
        double[][] a={{desiredRight.x(),desiredUp.x(),desiredForward.x()},
                      {desiredRight.y(),desiredUp.y(),desiredForward.y()},
                      {desiredRight.z(),desiredUp.z(),desiredForward.z()}};
        double[][] b={{right.x(),up.x(),forward.x()},
                      {right.y(),up.y(),forward.y()},
                      {right.z(),up.z(),forward.z()}};
        double[][] r=new double[3][3];
        for(int i=0;i<3;i++)for(int j=0;j<3;j++)for(int k=0;k<3;k++)r[i][j]+=a[i][k]*b[j][k];
        double x,y,z,w,trace=r[0][0]+r[1][1]+r[2][2];
        if(trace>0){double s=2*Math.sqrt(trace+1);w=s/4;x=(r[2][1]-r[1][2])/s;y=(r[0][2]-r[2][0])/s;z=(r[1][0]-r[0][1])/s;}
        else if(r[0][0]>r[1][1]&&r[0][0]>r[2][2]){double s=2*Math.sqrt(1+r[0][0]-r[1][1]-r[2][2]);w=(r[2][1]-r[1][2])/s;x=s/4;y=(r[0][1]+r[1][0])/s;z=(r[0][2]+r[2][0])/s;}
        else if(r[1][1]>r[2][2]){double s=2*Math.sqrt(1+r[1][1]-r[0][0]-r[2][2]);w=(r[0][2]-r[2][0])/s;x=(r[0][1]+r[1][0])/s;y=s/4;z=(r[1][2]+r[2][1])/s;}
        else{double s=2*Math.sqrt(1+r[2][2]-r[0][0]-r[1][1]);w=(r[1][0]-r[0][1])/s;x=(r[0][2]+r[2][0])/s;y=(r[1][2]+r[2][1])/s;z=s/4;}
        if(w<0){w=-w;x=-x;y=-y;z=-z;}
        double sin=Math.sqrt(x*x+y*y+z*z),angle=2*Math.atan2(sin,w);
        V error=sin<1e-12?V.ZERO:new V(x,y,z).mul(angle/sin);
        V desiredRate=targetAngularVelocity.add(error.mul(2).capped(maxRate));
        V acceleration=desiredRate.sub(angularVelocity).mul(3).capped(maxAcceleration);
        if(!acceleration.finite()||!Double.isFinite(angle))throw new IllegalArgumentException("Angular overflow");
        return new Demand(acceleration,angle);
    }
    private static void basis(V f,V u){
        if(f==null||u==null||!f.finite()||!u.finite()||Math.abs(f.length()-1)>1e-6
                ||Math.abs(u.length()-1)>1e-6||Math.abs(f.dot(u))>1e-6)
            throw new IllegalArgumentException("Orthonormal port basis required");
    }
}
