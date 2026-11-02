package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import org.joml.Vector3d;
import java.util.*;

/** Explicit finite local retreat. No firing, route planning or automatic restart.
 * Every outward demand retains the native frame, authority and swept-hull gate. */
public final class EnemyRetreat implements AutoCloseable {
    private final ServerSubLevel source,target;
    private final NativeEnemyHull hull;
    private final EnemyFlightAdapter flight;
    private final Set<UUID> hostile;
    private final UUID targetAuthority;
    private String reason="ACTIVE";
    private EnemyRetreat(ServerSubLevel source,NativeEnemyHull hull,ServerSubLevel target,
                         Set<UUID> hostile,UUID authority,EnemyFlightAdapter flight) {
        this.source=source;this.hull=hull;this.target=target;
        this.hostile=Set.copyOf(hostile);targetAuthority=authority;this.flight=flight;
    }
    public static Optional<EnemyRetreat> start(ServerSubLevel source,NativeEnemyHull hull,
            List<BlockPos> engines,ServerSubLevel target,Set<UUID> hostile,int lifetime) {
        var choice=EnemyTargetSelector.choose(source,hull,target,hostile,Set.of(),Set.of());
        if(choice.isEmpty()||lifetime<1||lifetime>600)return Optional.empty();
        return EnemyFlightAdapter.acquire(source,hull,engines,lifetime)
                .map(flight->new EnemyRetreat(source,hull,target,hostile,choice.get().authority(),flight));
    }
    public boolean tick() {
        if(!source.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread retreat required");
        if(!active())return false;
        var choice=EnemyTargetSelector.choose(source,hull,target,hostile,Set.of(),Set.of());
        if(choice.isEmpty()||!choice.get().authority().equals(targetAuthority))return hold("TARGET_AUTHORITY_LOST");
        var clearance=EnemyCollisionGate.check(source,hull,target,.1);
        if(!clearance.clear())return hold("COLLISION_"+clearance.reason());
        try {
            var own=RigidBodyHandle.of(source);var other=RigidBodyHandle.of(target);
            if(!own.isValid()||!other.isValid())return hold("BODY_UNAVAILABLE");
            var p=source.logicalPose().transformPosition(new Vector3d(source.getMassTracker().getCenterOfMass()));
            var q=target.logicalPose().transformPosition(new Vector3d(target.getMassTracker().getCenterOfMass()));
            var velocity=new Vector3d(own.getLinearVelocity());var targetVelocity=new Vector3d(other.getLinearVelocity());
            if(!p.isFinite()||!q.isFinite()||!velocity.isFinite()||!targetVelocity.isFinite()
                    ||targetVelocity.length()>.1||velocity.length()>.2)return hold("UNSAFE_OBSERVATION");
            var outward=p.sub(q);double distance=outward.length();
            if(distance<10||distance>128)return hold("UNSAFE_RANGE");
            // Outward relative speed remains within the accepted local flight envelope.
            var demand=outward.div(distance).mul(.08).add(targetVelocity).sub(velocity).mul(2);
            if(demand.length()>.03)demand.normalize(.03);
            if(!flight.apply(new V(demand.x,demand.y,demand.z),V.ZERO))return hold("FLIGHT_"+flight.reason());
            return true;
        }catch(RuntimeException unavailable){return hold("OBSERVATION_UNAVAILABLE");}
    }
    private boolean hold(String why){reason=why;flight.close();return false;}
    public boolean active(){return reason.equals("ACTIVE")&&flight.active();}
    public String reason(){return reason.equals("ACTIVE")?flight.reason():reason;}
    @Override public void close(){hold("EXPLICIT_STOP");}
}
