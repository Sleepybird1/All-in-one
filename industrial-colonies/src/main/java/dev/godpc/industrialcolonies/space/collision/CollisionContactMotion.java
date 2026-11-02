package dev.godpc.industrialcolonies.space.collision;

import java.util.*;
import org.joml.Quaterniond;
import org.joml.Vector3d;
import dev.godpc.industrialcolonies.space.collision.CollisionObservationBuffer.Contact;
import dev.godpc.industrialcolonies.space.collision.CollisionObservationBuffer.Vector;

/** Read-only contact kinematics. The caller supplies every native pre-step sample
 * from the contact's tick and independently verifies persistent body ownership.
 * This class neither grants damage authority nor infers units from the raw scalar.
 * A matching pose is not necessarily the unique generating step: retain an interval
 * and use its lower bound for any later conservative severity decision. */
public final class CollisionContactMotion {
    private CollisionContactMotion() {}
    public record Rotation(double x,double y,double z,double w) {
        public Rotation {
            double length=x*x+y*y+z*z+w*w;
            if(!Double.isFinite(length)||Math.abs(length-1)>0.001)
                throw new IllegalArgumentException("Finite near-unit rotation required");
        }
        Quaterniond quaternion(){return new Quaterniond(x,y,z,w);}
    }
    public record Body(int runtimeId,UUID identity,Vector position,Rotation orientation,
                       Vector linear,Vector angular,double mass) {
        public Body {
            Objects.requireNonNull(identity);Objects.requireNonNull(orientation);
            finite(position);finite(linear);finite(angular);
            if(runtimeId < -1 || !Double.isFinite(mass) || mass < 0
                    || (runtimeId >= 0 && mass == 0))
                throw new IllegalArgumentException("Native body mass/identity required");
            if(runtimeId==-1&&(mass!=0||length(position)!=0||length(linear)!=0||length(angular)!=0
                    ||orientation.x()!=0||orientation.y()!=0||orientation.z()!=0||orientation.w()!=1))
                throw new IllegalArgumentException("Static main world has identity pose and zero motion");
        }
    }
    public record Step(long tick,int ordinal,Body first,Body second) {
        public Step {
            Objects.requireNonNull(first);Objects.requireNonNull(second);
            if(tick<0||ordinal<0||ordinal>=64||first.runtimeId()==second.runtimeId()
                    ||first.identity().equals(second.identity()))
                throw new IllegalArgumentException("Distinct observed pair required");
        }
    }
    public record Tolerance(double normalError,double pointSeparation) {
        public Tolerance {
            if(!Double.isFinite(normalError)||normalError<=0||normalError>0.001
                    ||!Double.isFinite(pointSeparation)||pointSeparation<=0||pointSeparation>1)
                throw new IllegalArgumentException("Explicit qualified geometry bounds required");
        }
    }
    public record Result(boolean accepted,String reason,int candidates,double minimumClosing,
                         double maximumClosing,double minimumEnergy,double maximumEnergy) {
        static Result refused(String reason){return new Result(false,reason,0,0,0,0,0);}
    }
    public static Result estimate(long tick,Contact contact,UUID firstIdentity,UUID secondIdentity,
                                  List<Step> observations,Tolerance tolerance) {
        Objects.requireNonNull(contact);Objects.requireNonNull(tolerance);
        if(tick<0||observations==null||observations.isEmpty()||observations.size()>64)
            return Result.refused("INCOMPLETE_OR_UNBOUNDED_CAPTURE");
        if(firstIdentity==null||secondIdentity==null||firstIdentity.equals(secondIdentity))
            return Result.refused("UNKNOWN_IDENTITY");
        try {
            finite(contact.rawVectorA());finite(contact.rawVectorB());
            finite(contact.localPointA());finite(contact.localPointB());
        }catch(IllegalArgumentException invalid){return Result.refused("NONFINITE_CONTACT");}
        if(Math.abs(length(contact.rawVectorA())-1)>0.001||Math.abs(length(contact.rawVectorB())-1)>0.001)
            return Result.refused("NONUNIT_NORMAL");
        Set<Integer> ordinals=new HashSet<>();
        int matches=0;double min=Double.POSITIVE_INFINITY,max=0,minEnergy=Double.POSITIVE_INFINITY,maxEnergy=0;
        for(Step step:observations){
            if(step==null||step.tick()!=tick||!ordinals.add(step.ordinal()))
                return Result.refused("STALE_OR_DUPLICATE_STEP");
            Body a=step.first(),b=step.second();
            if(a.runtimeId()!=contact.bodyA()||b.runtimeId()!=contact.bodyB()
                    ||!a.identity().equals(firstIdentity)||!b.identity().equals(secondIdentity))
                return Result.refused("FOREIGN_BODY");
            Vector3d na=rotate(a,contact.rawVectorA()),nb=rotate(b,contact.rawVectorB());
            if(new Vector3d(na).add(nb).length()>tolerance.normalError())continue;
            Vector3d ra=rotate(a,contact.localPointA()),rb=rotate(b,contact.localPointB());
            Vector3d pa=new Vector3d(ra).add(vector(a.position())),pb=new Vector3d(rb).add(vector(b.position()));
            if(pa.distance(pb)>tolerance.pointSeparation())continue;
            Vector3d va=vector(a.angular()).cross(ra).add(vector(a.linear()));
            Vector3d vb=vector(b.angular()).cross(rb).add(vector(b.linear()));
            double closing=Math.max(0,va.sub(vb).dot(na.normalize()));
            double mass=a.mass()==0?b.mass():b.mass()==0?a.mass():1/(1/a.mass()+1/b.mass());
            double energy=0.5*mass*closing*closing;
            if(!Double.isFinite(closing)||!Double.isFinite(energy)||mass<=0)
                return Result.refused("INVALID_DERIVED_MOTION");
            matches++;min=Math.min(min,closing);max=Math.max(max,closing);
            minEnergy=Math.min(minEnergy,energy);maxEnergy=Math.max(maxEnergy,energy);
        }
        return matches==0?Result.refused("NO_MATCHING_PRESTEP_POSE"):
                new Result(true,"MATCHED_CANDIDATE_INTERVAL",matches,min,max,minEnergy,maxEnergy);
    }
    private static void finite(Vector v){
        if(v==null||!Double.isFinite(v.x())||!Double.isFinite(v.y())||!Double.isFinite(v.z()))
            throw new IllegalArgumentException("Finite immutable vector required");
    }
    private static Vector3d vector(Vector v){return new Vector3d(v.x(),v.y(),v.z());}
    private static double length(Vector v){return vector(v).length();}
    private static Vector3d rotate(Body b,Vector v){return b.orientation().quaternion().transform(vector(v));}
}
