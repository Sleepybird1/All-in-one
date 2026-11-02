package dev.godpc.industrialcolonies.space.enemy;

import java.util.ArrayList;
import java.util.List;

/** Conditional dry, linear-drag launch envelope. This does not inspect terrain,
 * fluids, moving traffic, target rights or cannon freshness, and grants no shot.
 * Rotation preserves the launch-noise norm; each step propagates that norm
 * through the independently qualified native position/velocity recurrence. */
public final class EnemyProjectileEnvelope {
    private EnemyProjectileEnvelope() {}
    public record V(double x,double y,double z) {
        public boolean finite(){return Double.isFinite(x)&&Double.isFinite(y)&&Double.isFinite(z);}
        public V add(V other){return new V(x+other.x,y+other.y,z+other.z);}
        public V scale(double factor){return new V(x*factor,y*factor,z*factor);}
    }
    public record Step(int tick,V position,V velocity,double positionRadius,double velocityRadius) {}
    public static List<Step> forecast(V muzzle,V centralVelocity,double gravity,double drag,
            double launchNoiseRadius,double muzzleUncertainty,int ticks) {
        if(muzzle==null||centralVelocity==null||!muzzle.finite()||!centralVelocity.finite()
                ||!Double.isFinite(gravity)||Math.abs(gravity)>1
                ||!Double.isFinite(drag)||drag<0||drag>1
                ||!Double.isFinite(launchNoiseRadius)||launchNoiseRadius<0||launchNoiseRadius>4
                ||!Double.isFinite(muzzleUncertainty)||muzzleUncertainty<0||muzzleUncertainty>1
                ||ticks<1||ticks>20)throw new IllegalArgumentException("Bounded dry linear profile required");
        var result=new ArrayList<Step>();var p=muzzle;var v=centralVelocity;
        double positionRadius=muzzleUncertainty,velocityRadius=launchNoiseRadius;
        result.add(new Step(0,p,v,positionRadius,velocityRadius));
        for(int tick=1;tick<=ticks;tick++) {
            var force=v.scale(-drag).add(new V(0,gravity,0));
            p=p.add(v).add(force.scale(.5));v=v.add(force);
            positionRadius+=(1-drag*.5)*velocityRadius;velocityRadius*=1-drag;
            if(!p.finite()||!v.finite()||!Double.isFinite(positionRadius))
                throw new IllegalArgumentException("Nonfinite forecast");
            result.add(new Step(tick,p,v,positionRadius,velocityRadius));
        }
        return List.copyOf(result);
    }
}
