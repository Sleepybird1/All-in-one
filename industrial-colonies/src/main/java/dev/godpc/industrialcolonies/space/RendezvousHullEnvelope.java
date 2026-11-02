package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Separating-axis proof for two swept, inflated oriented hull boxes.
 * A false result means unknown/overlapping, never permission to approach.
 * Each sweep contains the convex hull of the current and translated boxes;
 * spherical inflation preserves the caller's rotation/acceleration reserves.
 */
public final class RendezvousHullEnvelope {
    private RendezvousHullEnvelope() {}
    public static boolean separated(V[] a,V[] b,V travel,V ownMotion,V otherMotion,double ownMargin,double otherMargin) {
        if(!valid(a)||!valid(b)||travel==null||ownMotion==null||otherMotion==null
                ||!travel.finite()||!ownMotion.finite()||!otherMotion.finite()
                ||!Double.isFinite(ownMargin)||!Double.isFinite(otherMargin)||ownMargin<0||otherMargin<0)return false;
        V[] aa=axes(a),bb=axes(b);
        for(V axis:new V[]{new V(1,0,0),new V(0,1,0),new V(0,0,1)})
            if(gap(a,b,axis,travel,ownMotion,otherMotion,ownMargin+otherMargin))return true;
        for(V axis:aa)if(gap(a,b,axis,travel,ownMotion,otherMotion,ownMargin+otherMargin))return true;
        for(V axis:bb)if(gap(a,b,axis,travel,ownMotion,otherMotion,ownMargin+otherMargin))return true;
        for(V x:aa)for(V y:bb)if(gap(a,b,x.cross(y),travel,ownMotion,otherMotion,ownMargin+otherMargin))return true;
        return false;
    }
    private static boolean valid(V[] points){if(points==null||points.length!=8)return false;for(V p:points)if(p==null||!p.finite())return false;return true;}
    private static V[] axes(V[] p){return new V[]{p[4].sub(p[0]),p[2].sub(p[0]),p[1].sub(p[0])};}
    private static boolean gap(V[] a,V[] b,V axis,V travel,V ownMotion,V otherMotion,double margin){
        double length=axis.length();if(!Double.isFinite(length)||length<1e-9)return false;
        axis=axis.mul(1/length);
        double amin=Double.POSITIVE_INFINITY,amax=Double.NEGATIVE_INFINITY,bmin=amin,bmax=amax;
        for(V p:a){double dot=p.dot(axis);amin=Math.min(amin,dot);amax=Math.max(amax,dot);}
        for(V p:b){double dot=p.dot(axis);bmin=Math.min(bmin,dot);bmax=Math.max(bmax,dot);}
        double trip=travel.dot(axis),motion=ownMotion.dot(axis),other=otherMotion.dot(axis);
        amin+=Math.min(0,Math.min(trip,motion));amax+=Math.max(0,Math.max(trip,motion));
        bmin+=Math.min(0,other);bmax+=Math.max(0,other);
        return bmin-amax>margin+1e-6||amin-bmax>margin+1e-6;
    }
}
