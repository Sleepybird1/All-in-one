package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3d;
import java.util.*;

/** Read-only physical frame of a disarmed mounted native autocannon.
 * Optional CBC access stays reflective. This is neither target leading nor
 * permission to aim/fire; raw Create vectors are coordinates in the ship plot.
 * Caller must acquire a fresh frame after any server tick or attachment change. */
public final class EnemyWeaponFrame {
    public record Sample(UUID body,UUID cannon,long tick,V muzzle,V axis,V velocity,String ammunition) {}
    private final ServerSubLevel body;
    private final NativeEnemyHull hull;
    private final BlockPos mount;
    private final EnemyCapabilitySampler capabilities;
    private EnemyWeaponFrame(ServerSubLevel body,NativeEnemyHull hull,BlockPos mount) {
        this.body=body;this.hull=hull;this.mount=mount.immutable();
        capabilities=EnemyCapabilitySampler.commission(body,hull,List.of(mount));
    }
    public static EnemyWeaponFrame commission(ServerSubLevel body,NativeEnemyHull hull,BlockPos mount) {
        if(body==null||hull==null||mount==null||!hull.belongsTo(body)||!hull.observes(mount))
            throw new IllegalArgumentException("Commissioned mount required");
        return new EnemyWeaponFrame(body,hull,mount);
    }
    public Optional<Sample> sample() {
        if(!body.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread frame required");
        if(!EnemyTargetSelector.mayControlSource(body,hull))return Optional.empty();
        try {
            var snapshot=capabilities.sample();if(snapshot.isEmpty())return Optional.empty();
            var component=snapshot.get().components().getFirst();
            if(!component.available()||!component.kind().equals("CANNON")||component.attachment()==null)return Optional.empty();
            var be=body.getLevel().getBlockEntity(mount);if(be==null)return Optional.empty();
            var entity=be.getClass().getMethod("getContraption").invoke(be);
            if(!(entity instanceof net.minecraft.world.entity.Entity nativeEntity)||nativeEntity.isRemoved()
                    ||!nativeEntity.getUUID().equals(component.attachment()))return Optional.empty();
            var cannon=entity.getClass().getMethod("getContraption").invoke(entity);
            if(!cannon.getClass().getName().equals("rbasamoyai.createbigcannons.cannon_control.contraption.MountedAutocannonContraption"))return Optional.empty();
            var start=(BlockPos)cannon.getClass().getMethod("getStartPos").invoke(cannon);
            var facing=(Direction)cannon.getClass().getMethod("initialOrientation").invoke(cannon);
            var blocks=(Map<?,?>)cannon.getClass().getMethod("getBlocks").invoke(cannon);
            if(start==null||facing==null||blocks.isEmpty()||blocks.size()>256)return Optional.empty();
            var breech=blocks.get(start);
            if(!(breech instanceof StructureTemplate.StructureBlockInfo info))return Optional.empty();
            for(var entry:info.state().getValues().entrySet())
                if(entry.getKey().getName().equals("handle")&&Boolean.TRUE.equals(entry.getValue()))return Optional.empty();
            var end=start;int length=0;
            while(blocks.containsKey(end)) {
                if(++length>256)return Optional.empty();end=end.relative(facing);
            }
            if(length<2||length!=blocks.size())return Optional.empty();
            var transform=entity.getClass().getMethod("toGlobalVector",Vec3.class,float.class);
            var back=(Vec3)transform.invoke(entity,Vec3.atCenterOf(BlockPos.ZERO),0f);
            var tip=(Vec3)transform.invoke(entity,Vec3.atCenterOf(end.relative(facing)),0f);
            var rawAxis=tip.subtract(back).normalize();if(rawAxis.lengthSqr()<.99)return Optional.empty();
            var rawMuzzle=tip.subtract(rawAxis.scale(1.5));
            var pose=body.logicalPose();var muzzle=pose.transformPosition(new Vector3d(rawMuzzle.x,rawMuzzle.y,rawMuzzle.z));
            var axis=pose.orientation().transform(new Vector3d(rawAxis.x,rawAxis.y,rawAxis.z)).normalize();
            var handle=RigidBodyHandle.of(body);if(!handle.isValid())return Optional.empty();
            var center=pose.transformPosition(new Vector3d(body.getMassTracker().getCenterOfMass()));
            var velocity=new Vector3d(handle.getAngularVelocity()).cross(new Vector3d(muzzle).sub(center)).add(handle.getLinearVelocity());
            if(!muzzle.isFinite()||!axis.isFinite()||!velocity.isFinite()||!capabilities.current(snapshot.get()))return Optional.empty();
            return Optional.of(new Sample(body.getUniqueId(),nativeEntity.getUUID(),body.getLevel().getGameTime(),
                    vector(muzzle),vector(axis),vector(velocity),component.contents()));
        }catch(ReflectiveOperationException|RuntimeException unavailable){return Optional.empty();}
    }
    public boolean current(Sample expected) {
        return expected!=null&&expected.tick()==body.getLevel().getGameTime()&&sample().filter(expected::equals).isPresent();
    }
    private static V vector(Vector3d v){return new V(v.x,v.y,v.z);}
}
