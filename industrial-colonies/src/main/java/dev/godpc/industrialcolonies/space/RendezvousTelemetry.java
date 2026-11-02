package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import org.joml.Vector3d;
import org.joml.Vector3dc;
import java.util.Optional;

/** Read-only native port telemetry. Never equates separate deep-space instances.
 * This supplies a common local frame; inter-instance/celestial conversion is not
 * implemented. The caller still owns target identity, collision and control gates.
 */
public final class RendezvousTelemetry {
    private RendezvousTelemetry() {}

    public static Optional<RendezvousGuidance.Port> sample(ServerSubLevel body, BlockPos port,
                                                          Direction outward, Direction up) {
        if (body==null || port==null || outward==null || up==null || body.isRemoved()
                || outward.getAxis()==up.getAxis()) return Optional.empty();
        try {
            var level=body.getLevel();
            if (!level.getServer().isSameThread() || !level.hasChunkAt(port)
                    || Sable.HELPER.getContaining(level,port)!=body) return Optional.empty();
            var handle=RigidBodyHandle.of(body);
            if (!handle.isValid()) return Optional.empty();
            var pose=body.logicalPose();
            var local=new Vector3d(port.getX()+.5,port.getY()+.5,port.getZ()+.5);
            var world=pose.transformPosition(new Vector3d(local));
            var normal=pose.transformPosition(new Vector3d(local).add(outward.getStepX(),outward.getStepY(),outward.getStepZ())).sub(world).normalize();
            var top=pose.transformPosition(new Vector3d(local).add(up.getStepX(),up.getStepY(),up.getStepZ())).sub(world).normalize();
            var center=pose.transformPosition(new Vector3d(body.getMassTracker().getCenterOfMass()));
            var omega=new Vector3d(handle.getAngularVelocity());
            var velocity=new Vector3d(omega).cross(new Vector3d(world).sub(center)).add(handle.getLinearVelocity());
            for(var v:new Vector3dc[]{world,normal,top,center,omega,velocity})
                if (!Double.isFinite(v.x()) || !Double.isFinite(v.y()) || !Double.isFinite(v.z())) return Optional.empty();
            String frame=level.dimension().location().toString();
            if (level.dimension().location().toString().equals("rocketnautics:deep_space")) {
                if (world.x<Integer.MIN_VALUE || world.x>Integer.MAX_VALUE
                        || world.z<Integer.MIN_VALUE || world.z>Integer.MAX_VALUE) return Optional.empty();
                var data=DeepSpaceData.getInstance(level.getServer());
                var instance=data.getInstanceForPos((int)Math.floor(world.x),(int)Math.floor(world.z));
                if (instance==null || instance.isCorrupted() || instance.getPosition()==null
                        || instance.getPosition().isCorrupted()
                        || !instance.boundingBox().contains(world.x,world.y,world.z)) return Optional.empty();
                frame+="/instance/"+instance.getId();
            }
            return Optional.of(new RendezvousGuidance.Port(frame,level.getGameTime()/20.0,
                    vector(world),vector(velocity),vector(normal),vector(top),vector(omega)));
        } catch (RuntimeException unavailable) {
            return Optional.empty();
        }
    }

    private static RendezvousGuidance.V vector(Vector3dc v) {
        return new RendezvousGuidance.V(v.x(),v.y(),v.z());
    }
}
