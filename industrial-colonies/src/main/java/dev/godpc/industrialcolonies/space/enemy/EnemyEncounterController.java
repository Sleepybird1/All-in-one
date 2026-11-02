package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import org.joml.Vector3d;
import java.util.*;

/** Explicit one-pass native encounter. Admission owns finite flight, disarmed
 * cannon and turret inputs, but does not actuate. There is no automatic start,
 * saved-phase replay, periodic spawning or production registration. Every
 * ordinary tick resamples authority, hull, frame and conditional clearance. */
public final class EnemyEncounterController implements AutoCloseable {
    public enum Phase { APPROACH, ATTACK, RETREAT, COMPLETE, HELD }
    public record Settings(double attackRange,double retreatGain,int lifetime,
            double accelerationReserve,double angularAccelerationReserve,
            double recoilVelocityReserve,double recoilAngularReserve) {
        public Settings {
            if(!Double.isFinite(attackRange)||attackRange<12||attackRange>48
                    ||!Double.isFinite(retreatGain)||retreatGain<.1||retreatGain>16
                    ||lifetime<2||lifetime>600)throw new IllegalArgumentException("Invalid local encounter limits");
            for(double v:new double[]{accelerationReserve,angularAccelerationReserve,recoilVelocityReserve,recoilAngularReserve})
                if(!Double.isFinite(v)||v<0)throw new IllegalArgumentException("Explicit finite conditional reserves required");
        }
    }
    private final ServerSubLevel source,target;
    private final NativeEnemyHull hull;
    private final Set<UUID> hostile,approvedPlayers,friendly;
    private final UUID targetAuthority;
    private final EnemyNativeFrame.Key frame;
    private final EnemyFlightAdapter flight;
    private final EnemyCannonHold cannon;
    private final EnemyTurretLease turret;
    private final EnemyWeaponTarget observer;
    private final EnemyTurretAimPlan planner;
    private final EnemyProjectileProfile profiles;
    private final Settings settings;
    private final long deadline;
    private long lastTick;
    private Phase phase=Phase.APPROACH;
    private String reason="ADMITTED";
    private double retreatStart;
    private int emissions;
    private EnemyEncounterController(ServerSubLevel source,ServerSubLevel target,NativeEnemyHull hull,
            Set<UUID> hostile,Set<UUID> approvedPlayers,Set<UUID> friendly,UUID targetAuthority,EnemyNativeFrame.Key frame,EnemyFlightAdapter flight,
            EnemyCannonHold cannon,EnemyTurretLease turret,EnemyWeaponTarget observer,
            EnemyTurretAimPlan planner,EnemyProjectileProfile profiles,Settings settings) {
        this.source=source;this.target=target;this.hull=hull;this.hostile=Set.copyOf(hostile);
        this.approvedPlayers=Set.copyOf(approvedPlayers);this.friendly=Set.copyOf(friendly);
        this.targetAuthority=targetAuthority;this.frame=frame;this.flight=flight;this.cannon=cannon;
        this.turret=turret;this.observer=observer;this.planner=planner;this.profiles=profiles;this.settings=settings;
        lastTick=source.getLevel().getGameTime();deadline=Math.addExact(lastTick,settings.lifetime());
    }
    public static Optional<EnemyEncounterController> start(ServerSubLevel source,NativeEnemyHull hull,
            List<BlockPos> engines,BlockPos mount,ServerSubLevel target,Set<UUID> hostile,Settings settings) {
        return start(source,hull,engines,mount,target,hostile,Set.of(),Set.of(),settings);
    }
    /** Trusted explicit server admission only. Owner approval is not inferred from
     * equipment, proximity or names; friendly exclusion always takes precedence.
     * These immutable sets are rechecked through native ownership every tick.
     * This overload does not establish progression eligibility or saved replay. */
    public static Optional<EnemyEncounterController> start(ServerSubLevel source,NativeEnemyHull hull,
            List<BlockPos> engines,BlockPos mount,ServerSubLevel target,Set<UUID> hostile,
            Set<UUID> approvedPlayers,Set<UUID> friendly,Settings settings) {
        if(settings==null||mount==null||source==null||target==null||hull==null
                ||!bounded(hostile)||!bounded(approvedPlayers)||!bounded(friendly))return Optional.empty();
        hostile=Set.copyOf(hostile);approvedPlayers=Set.copyOf(approvedPlayers);friendly=Set.copyOf(friendly);
        var selected=EnemyTargetSelector.choose(source,hull,target,hostile,approvedPlayers,friendly);
        var frame=EnemyNativeFrame.read(source);
        if(selected.isEmpty()||frame.isEmpty()||!EnemyNativeFrame.common(source,target)
                ||!EnemyCollisionGate.check(source,hull,target,.1).clear())return Optional.empty();
        EnemyFlightAdapter flight=null;EnemyCannonHold cannon=null;EnemyTurretLease turret=null;
        boolean admitted=false;
        try {
            var weapon=EnemyWeaponFrame.commission(source,hull,mount);
            var observer=EnemyWeaponTarget.commission(source,hull,weapon,target,hostile,approvedPlayers,friendly);
            var planner=EnemyTurretAimPlan.commission(source,hull,mount,observer);
            var profiles=EnemyProjectileProfile.commission(source,hull,mount);
            if(observer.sample().isEmpty()||profiles.sample().isEmpty())return Optional.empty();
            flight=EnemyFlightAdapter.acquire(source,hull,engines,settings.lifetime()).orElse(null);
            if(flight==null)return Optional.empty();
            cannon=EnemyCannonHold.acquire(source,hull,mount).orElse(null);
            if(cannon==null)return Optional.empty();
            turret=EnemyTurretLease.acquire(source,hull,mount,cannon,planner,settings.lifetime()).orElse(null);
            if(turret==null)return Optional.empty();
            var result=new EnemyEncounterController(source,target,hull,hostile,approvedPlayers,friendly,selected.get().authority(),
                    frame.get(),flight,cannon,turret,observer,planner,profiles,settings);
            admitted=true;return Optional.of(result);
        }catch(RuntimeException unavailable){return Optional.empty();}
        finally{if(!admitted){if(turret!=null)turret.close();if(cannon!=null)cannon.close();if(flight!=null)flight.close();}}
    }
    public boolean tick() {
        requireThread();if(!active())return false;
        long now=source.getLevel().getGameTime();
        if(now<=lastTick||now-lastTick>2||now>=deadline)return hold("ENCOUNTER_SEQUENCE_OR_LIFETIME_EXPIRED");
        lastTick=now;
        var choice=EnemyTargetSelector.choose(source,hull,target,hostile,approvedPlayers,friendly);
        if(choice.isEmpty()||!choice.get().authority().equals(targetAuthority))return hold("TARGET_AUTHORITY_LOST");
        if(!EnemyNativeFrame.read(source).filter(frame::equals).isPresent()||!EnemyNativeFrame.common(source,target))return hold("NATIVE_FRAME_CHANGED");
        if(!cannon.refresh()||!flight.active()||!turret.active())return hold("ACTUATOR_OWNERSHIP_LOST");
        var gate=EnemyCollisionGate.check(source,hull,target,.1);
        if(!gate.clear())return hold("COLLISION_"+gate.reason());
        try {
            var p=source.logicalPose().transformPosition(new Vector3d(source.getMassTracker().getCenterOfMass()));
            var q=target.logicalPose().transformPosition(new Vector3d(target.getMassTracker().getCenterOfMass()));
            var v=new Vector3d(RigidBodyHandle.of(source).getLinearVelocity());
            var w=new Vector3d(RigidBodyHandle.of(target).getLinearVelocity());
            var toward=q.sub(p);double range=toward.length();
            if(!toward.isFinite()||!v.isFinite()||!w.isFinite()||range<10||range>128||v.length()>.2||w.length()>.1)return hold("UNSAFE_MOTION");
            if(phase==Phase.APPROACH&&range<=settings.attackRange())phase=Phase.ATTACK;
            if(phase==Phase.RETREAT) {
                if(!turret.idle())return hold("TURRET_"+turret.reason());
                if(range>=retreatStart+settings.retreatGain()) {
                    phase=Phase.COMPLETE;reason="ONE_PASS_COMPLETE";release();return true;
                }
                return demand(toward,range,v,w,-.08);
            }
            var sample=observer.sample();
            if(sample.isEmpty())return hold("WEAPON_TARGET_UNAVAILABLE");
            var plan=planner.plan(sample.get());
            if(plan.isEmpty())return hold("TURRET_PLAN_UNAVAILABLE");
            if(!turret.apply(plan.get()))return hold("TURRET_"+turret.reason());
            if(phase==Phase.APPROACH)return demand(toward,range,v,w,Math.min(.08,Math.sqrt(2*.03*Math.max(0,range-settings.attackRange()))));
            // Hold translation while aiming. The one guarded emission alone
            // transitions to retreat; a failed native shot never refunds cargo.
            if(!flight.apply(V.ZERO,V.ZERO))return hold("FLIGHT_"+flight.reason());
            if(!plan.get().aligned()){reason="AIMING";return true;}
            if(!turret.idle())return hold("TURRET_STOP_BEFORE_FIRE_FAILED");
            var profile=profiles.sample();
            if(profile.isEmpty())return hold("AMMUNITION_PROFILE_UNAVAILABLE");
            var authority=EnemyImpactAuthority.commission(source,hull,target,hostile,approvedPlayers,friendly,profile.get().lifetime());
            if(authority.isEmpty())return hold("IMPACT_AUTHORITY_UNAVAILABLE");
            var shot=cannon.fireOnce(target,observer,planner,plan.get(),profiles,profile.get(),authority.get(),
                    settings.accelerationReserve(),settings.angularAccelerationReserve(),settings.recoilVelocityReserve(),settings.recoilAngularReserve());
            emissions+=shot.emissions();
            if(!shot.fired()||emissions!=1)return hold("FIRE_"+shot.reason());
            retreatStart=range;phase=Phase.RETREAT;reason="ONE_SHOT_RETREAT";
            if(!turret.idle())return hold("TURRET_STOP_FAILED");
            return true;
        }catch(RuntimeException unavailable){return hold("NATIVE_OBSERVATION_UNAVAILABLE");}
    }
    private boolean demand(Vector3d toward,double range,Vector3d v,Vector3d w,double speed) {
        var a=toward.div(range).mul(speed).add(w).sub(v).mul(2);
        if(a.length()>.03)a.normalize(.03);
        if(!flight.apply(new V(a.x,a.y,a.z),V.ZERO))return hold("FLIGHT_"+flight.reason());
        reason=phase==Phase.RETREAT?"RETREATING":"APPROACHING";return true;
    }
    private static boolean bounded(Set<UUID> authorities){
        return authorities!=null&&authorities.size()<=128&&authorities.stream().noneMatch(Objects::isNull);
    }
    private boolean hold(String why){phase=Phase.HELD;reason=why;release();return false;}
    private void release(){turret.close();cannon.close();flight.close();}
    private void requireThread(){if(!source.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread encounter required");}
    public boolean active(){return phase!=Phase.HELD&&phase!=Phase.COMPLETE;}
    public Phase phase(){return phase;}
    public String reason(){return reason;}
    public int emissions(){return emissions;}
    @Override public void close(){requireThread();if(active())hold("EXPLICIT_STOP");}
}
