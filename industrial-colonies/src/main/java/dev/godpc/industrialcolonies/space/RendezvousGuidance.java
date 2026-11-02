package dev.godpc.industrialcolonies.space;

import java.util.Objects;

/** Pure guidance policy. No force, pose, inventory, docking or world writes.
 * Samples must already share one physical frame, in blocks and seconds.
 * ABORT is latched: the owner must release its actuators and require a new session.
 * This is not a celestial-frame converter or an obstacle detector.
 */
public final class RendezvousGuidance {
    public record V(double x, double y, double z) {
        public static final V ZERO = new V(0, 0, 0);
        public V add(V b) { return new V(x+b.x, y+b.y, z+b.z); }
        public V sub(V b) { return new V(x-b.x, y-b.y, z-b.z); }
        public V mul(double k) { return new V(x*k, y*k, z*k); }
        public double dot(V b) { return x*b.x+y*b.y+z*b.z; }
        public V cross(V b) { return new V(y*b.z-z*b.y, z*b.x-x*b.z, x*b.y-y*b.x); }
        public double length() { return Math.sqrt(dot(this)); }
        public boolean finite() { return Double.isFinite(x)&&Double.isFinite(y)&&Double.isFinite(z); }
        public V capped(double max) { double n=length(); return n>max ? mul(max/n) : this; }
    }
    /** Velocity is the velocity at the port, including the body's omega x lever arm. */
    public record Port(String frame, double time, V position, V velocity,
                       V outward, V up, V angularVelocity) {}
    public record Conditions(boolean authorized, boolean targetLoaded, boolean corridorClear,
                             boolean propulsionReady, boolean exclusiveControl, boolean nativeLocked,
                             boolean finalApproachAllowed) {
        public Conditions(boolean authorized,boolean targetLoaded,boolean corridorClear,boolean propulsionReady,boolean exclusiveControl,boolean nativeLocked){
            this(authorized,targetLoaded,corridorClear,propulsionReady,exclusiveControl,nativeLocked,true);
        }
    }
    public enum Phase { APPROACH, ALIGN, BRAKE, CAPTURE, READY, DOCKED, ABORT }
    public record Command(Phase phase, String reason, V acceleration, V desiredOutward,
                          V desiredUp, boolean allowCapture, double distance, double relativeSpeed) {}
    public record Limits(double separation, double stagingDistance, double maxSpeed,
                         double captureSpeed, double acceleration, double captureRadius,
                         double angleRadians, double angularSpeed, double maxAge,
                         double maxRange, double maxRelativeSpeed) {
        public Limits {
            for (double v : new double[]{separation,stagingDistance,maxSpeed,captureSpeed,
                    acceleration,captureRadius,angleRadians,angularSpeed,maxAge,maxRange,maxRelativeSpeed})
                if (!Double.isFinite(v)||v<=0) throw new IllegalArgumentException("Positive finite limits required");
            if (captureSpeed>maxSpeed || captureRadius>=stagingDistance || angleRadians>=Math.PI/2
                    || maxRelativeSpeed<maxSpeed || maxRange<=separation+stagingDistance)
                throw new IllegalArgumentException("Inconsistent guidance limits");
        }
    }
    private final Limits limits;
    private String aborted;
    private boolean finalApproach;
    private double lastTime=Double.NEGATIVE_INFINITY;

    public RendezvousGuidance(Limits limits) { this.limits=Objects.requireNonNull(limits); }

    public Command update(double now, Port ship, Port target, Conditions conditions) {
        if (aborted!=null) return stop(Phase.ABORT,aborted);
        if (conditions==null || !conditions.authorized()) return abort("CONTROL_DISABLED");
        if (!conditions.targetLoaded()) return abort("TARGET_UNLOADED");
        if (!conditions.exclusiveControl()) return abort("CONTROL_CONFLICT");
        if (!Double.isFinite(now) || now<lastTime) return abort("CLOCK_INVALID");
        lastTime=now;
        if (!valid(ship,now)||!valid(target,now)) return abort("POSE_INVALID_OR_STALE");
        if (!ship.frame().equals(target.frame())) return abort("FRAME_MISMATCH");
        // A verified native lock ends propulsion even if fuel or corridor sensors changed.
        if (conditions.nativeLocked()) return stop(Phase.DOCKED,"NATIVE_LOCK");
        if (!conditions.corridorClear()) return abort("CORRIDOR_UNVERIFIED");
        if (!conditions.propulsionReady()) return abort("PROPULSION_UNAVAILABLE");

        V offset=target.outward().mul(limits.separation());
        V goal=target.position().add(offset);
        V targetVelocity=target.velocity().add(target.angularVelocity().cross(offset));
        V relativePosition=ship.position().sub(target.position());
        V error=goal.sub(ship.position());
        V relativeVelocity=ship.velocity().sub(targetVelocity);
        double distance=error.length(), speed=relativeVelocity.length();
        if (!Double.isFinite(distance)||!Double.isFinite(speed)) return abort("NUMERIC_OVERFLOW");
        if (relativePosition.length()>limits.maxRange()) return abort("OUTSIDE_LOCAL_ENVELOPE");
        if (speed>limits.maxRelativeSpeed()) return abort("RELATIVE_SPEED_UNSAFE");
        double along=relativePosition.dot(target.outward());
        if (along<limits.separation()-limits.captureRadius()) return abort("CROSSED_CAPTURE_PLANE");
        if (target.angularVelocity().length()>limits.angularSpeed()) return abort("TARGET_ROTATION_UNSAFE");
        double facing=angle(ship.outward(),target.outward().mul(-1));
        double roll=angle(ship.up(),target.up());
        boolean aligned=facing<=limits.angleRadians() && roll<=limits.angleRadians()
                && ship.angularVelocity().sub(target.angularVelocity()).length()<=limits.angularSpeed();
        // Start braking with twice the nominal stopping distance in reserve. This
        // uses the caller's validated acceleration authority, plus stale-sample
        // allowance and one native game tick of actuator latency. It does not
        // establish obstacle clearance or recovery from an already unsafe entry.
        double closing=Math.max(0,-relativeVelocity.dot(target.outward()));
        double stopping=closing*closing/(2*limits.acceleration())
                +closing*(limits.maxAge()+.05);
        double clearance=along-limits.separation()+limits.captureRadius();
        if (closing>limits.captureSpeed() && 2*stopping>=clearance) {
            finalApproach=false;
            return new Command(Phase.BRAKE,"CLOSING_BRAKING_ENVELOPE",
                    target.outward().mul(limits.acceleration()),target.outward().mul(-1),
                    target.up(),false,distance,speed);
        }
        V lateral=relativePosition.sub(target.outward().mul(along));
        // Never continue inward after losing alignment. Close misalignment aborts;
        // farther out, hold the staging point while the attitude actuator aligns.
        if (finalApproach && !aligned && along<limits.separation()+limits.stagingDistance()/2)
            return abort("ALIGNMENT_LOST_NEAR_DOCK");
        if (!aligned) finalApproach=false;
        if (finalApproach&&!conditions.finalApproachAllowed())return abort("FINAL_CORRIDOR_UNVERIFIED");
        V staging=goal.add(target.outward().mul(limits.stagingDistance()));
        if (!finalApproach && conditions.finalApproachAllowed() && aligned && ship.position().sub(staging).length()<=limits.captureRadius()
                && speed<=limits.captureSpeed()) finalApproach=true;
        if (finalApproach && lateral.length()>limits.captureRadius()*2) return abort("LEFT_CAPTURE_CORRIDOR");
        boolean ready=finalApproach && aligned && distance<=limits.captureRadius() && speed<=limits.captureSpeed();
        Phase phase=ready?Phase.READY:finalApproach?Phase.CAPTURE:aligned?Phase.APPROACH:Phase.ALIGN;
        V aim=finalApproach?goal:staging;
        V aimOffset=aim.sub(target.position());
        V aimVelocity=target.velocity().add(target.angularVelocity().cross(aimOffset));
        V aimError=aim.sub(ship.position());
        double speedLimit=finalApproach?limits.captureSpeed():limits.maxSpeed();
        // Stopping-distance cap plus proportional approach; acceleration always bounded.
        double plannedSpeed=Math.min(speedLimit,Math.sqrt(2*limits.acceleration()*aimError.length()));
        V desired=aimVelocity.add(aimError.mul(.5).capped(plannedSpeed));
        V acceleration=desired.sub(ship.velocity()).mul(2).capped(limits.acceleration());
        if (!acceleration.finite()) return abort("NUMERIC_OVERFLOW");
        return new Command(phase,"",acceleration,target.outward().mul(-1),target.up(),ready,distance,speed);
    }
    private boolean valid(Port p,double now) {
        if (p==null || p.frame()==null || p.frame().isBlank() || !Double.isFinite(p.time())
                || now<p.time() || now-p.time()>limits.maxAge()) return false;
        for (V v:new V[]{p.position(),p.velocity(),p.outward(),p.up(),p.angularVelocity()})
            if(v==null||!v.finite()) return false;
        return Math.abs(p.outward().length()-1)<1e-6 && Math.abs(p.up().length()-1)<1e-6
                && Math.abs(p.outward().dot(p.up()))<1e-6;
    }
    private static double angle(V a,V b) { return Math.acos(Math.max(-1,Math.min(1,a.dot(b)))); }
    private Command abort(String reason) { aborted=reason; return stop(Phase.ABORT,reason); }
    private static Command stop(Phase phase,String reason) {
        return new Command(phase,reason,V.ZERO,V.ZERO,V.ZERO,false,Double.NaN,Double.NaN);
    }
}
