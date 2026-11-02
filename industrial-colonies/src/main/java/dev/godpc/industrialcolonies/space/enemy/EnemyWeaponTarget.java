package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import org.joml.Vector3d;
import java.util.*;

/** Read-only same-tick physical target observation. Native velocity is reported,
 * not certified as a future trajectory. No lead, hit volume or firing authority. */
public final class EnemyWeaponTarget {
    public record Sample(EnemyWeaponFrame.Sample weapon, EnemyTargetSelector.Selection authority,
                         V center, V velocity, V angularVelocity) {}
    private final ServerSubLevel source,target;
    private final NativeEnemyHull hull;
    private final EnemyWeaponFrame weapon;
    private final Set<UUID> hostile,players,friendly;
    private EnemyWeaponTarget(ServerSubLevel source,NativeEnemyHull hull,EnemyWeaponFrame weapon,
            ServerSubLevel target,Set<UUID> hostile,Set<UUID> players,Set<UUID> friendly) {
        this.source=source;this.hull=hull;this.weapon=weapon;this.target=target;
        this.hostile=Set.copyOf(hostile);this.players=Set.copyOf(players);this.friendly=Set.copyOf(friendly);
    }
    public static EnemyWeaponTarget commission(ServerSubLevel source,NativeEnemyHull hull,
            EnemyWeaponFrame weapon,ServerSubLevel target,Set<UUID> hostile,Set<UUID> players,Set<UUID> friendly) {
        if(source==null||hull==null||weapon==null||target==null||!hull.belongsTo(source)
                ||hostile==null||players==null||friendly==null||hostile.size()>128||players.size()>128||friendly.size()>128)
            throw new IllegalArgumentException("Bounded explicit target authorities required");
        return new EnemyWeaponTarget(source,hull,weapon,target,hostile,players,friendly);
    }
    public Optional<Sample> sample() {
        if(!source.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread target required");
        var authority=EnemyTargetSelector.choose(source,hull,target,hostile,players,friendly);
        var frame=weapon.sample();
        if(authority.isEmpty()||frame.isEmpty()||!frame.get().body().equals(source.getUniqueId()))return Optional.empty();
        try {
            var handle=RigidBodyHandle.of(target);if(!handle.isValid())return Optional.empty();
            var center=target.logicalPose().transformPosition(new Vector3d(target.getMassTracker().getCenterOfMass()));
            var velocity=new Vector3d(handle.getLinearVelocity());var angular=new Vector3d(handle.getAngularVelocity());
            var muzzle=frame.get().muzzle();double range=center.distance(new Vector3d(muzzle.x(),muzzle.y(),muzzle.z()));
            if(!center.isFinite()||!velocity.isFinite()||!angular.isFinite()||!Double.isFinite(range)||range<1||range>128
                    ||!weapon.current(frame.get()))return Optional.empty();
            return Optional.of(new Sample(frame.get(),authority.get(),vector(center),vector(velocity),vector(angular)));
        }catch(RuntimeException unavailable){return Optional.empty();}
    }
    public boolean current(Sample expected) {
        return expected!=null&&expected.authority().tick()==source.getLevel().getGameTime()
                &&sample().filter(expected::equals).isPresent();
    }
    private static V vector(Vector3d value){return new V(value.x,value.y,value.z);}
}
