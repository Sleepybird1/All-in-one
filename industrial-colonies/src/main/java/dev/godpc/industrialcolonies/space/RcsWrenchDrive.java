package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.content.blocks.RCSThrusterBlockEntity;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import org.joml.Matrix3d;
import org.joml.Vector3d;
import org.joml.Vector3dc;
import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Native force/torque adapter with exclusive, expiring actuator ownership.
 * Does not start navigation, claim a clear corridor, or resume after load.
 */
public final class RcsWrenchDrive implements AutoCloseable {
    private final ServerSubLevel body;
    private final List<BlockPos> engines;
    private final RcsActuatorLease lease;
    private String failure;
    private RcsWrenchDrive(ServerSubLevel body,List<BlockPos> engines,RcsActuatorLease lease){
        this.body=body;this.engines=engines.stream().map(BlockPos::immutable).toList();this.lease=lease;
    }
    public static Optional<RcsWrenchDrive> acquire(ServerSubLevel body,List<BlockPos> engines){
        return RcsActuatorLease.acquire(body,engines).map(lease->new RcsWrenchDrive(body,engines,lease));
    }
    public boolean active(){return failure==null&&lease.active();}
    public String reason(){return failure==null?lease.reason():failure;}
    /** Demands COM linear and angular acceleration in the native physical frame.
     * An infeasible wrench releases ownership instead of hiding saturation.
     */
    public Optional<RcsWrenchAllocator.Allocation> apply(V acceleration,V angularAcceleration){
        return applyWithExternalTorque(acceleration,angularAcceleration,V.ZERO);
    }
    /** Compensate a known world-frame external torque (for example leased main engines).
     * External linear thrust is intentionally not cancelled here. Callers must refresh the
     * torque estimate with their control sample; this method does not infer propulsion state.
     */
    public Optional<RcsWrenchAllocator.Allocation> applyWithExternalTorque(V acceleration,V angularAcceleration,V externalTorque){
        if(!body.getLevel().getServer().isSameThread())throw new IllegalStateException("RCS drive requires server thread");
        if(!active())return Optional.empty();
        try{
            if(!finite(acceleration)||!finite(angularAcceleration)||!finite(externalTorque))return fail("INVALID_DEMAND");
            var handle=RigidBodyHandle.of(body);
            double mass=body.getMassTracker().getMass();
            if(!handle.isValid()||!Double.isFinite(mass)||mass<=0)return fail("BODY_UNAVAILABLE");
            var pose=body.logicalPose();var center=pose.transformPosition(new Vector3d(body.getMassTracker().getCenterOfMass()));
            var rotation=new Matrix3d().rotation(pose.orientation());
            var inertia=new Matrix3d(rotation).mul(body.getMassTracker().getInertiaTensor()).mul(new Matrix3d(rotation).transpose());
            var omega=new Vector3d(handle.getAngularVelocity());
            var torque=inertia.transform(j(angularAcceleration)).add(new Vector3d(omega).cross(inertia.transform(new Vector3d(omega)))).sub(j(externalTorque));
            var jets=new ArrayList<RcsWrenchAllocator.Jet>();double scale=1;
            // Exact installed native RCS thrust law; no fuel debit exists in this path.
            double y=pose.position().y,maximum=y<=2000?12:y<5000?12+93*(y-2000)/3000:105;
            for(var p:engines){
                if(!body.getLevel().hasChunkAt(p)||!(body.getLevel().getBlockEntity(p) instanceof RCSThrusterBlockEntity))return fail("ACTUATOR_CHANGED");
                var state=body.getLevel().getBlockState(p);
                if(!state.hasProperty(BlockStateProperties.FACING))return fail("ACTUATOR_CHANGED");
                var d=state.getValue(BlockStateProperties.FACING);var local=new Vector3d(p.getX()+.5,p.getY()+.5,p.getZ()+.5);
                var origin=pose.transformPosition(new Vector3d(local));
                var point=pose.transformPosition(new Vector3d(local).add(d.getStepX()*.5,d.getStepY()*.5,d.getStepZ()*.5));
                var direction=pose.transformPosition(new Vector3d(local).add(d.getStepX(),d.getStepY(),d.getStepZ())).sub(origin).normalize();
                var arm=point.sub(center);scale=Math.max(scale,arm.length());
                jets.add(new RcsWrenchAllocator.Jet(p.toShortString(),v(direction.mul(-maximum)),v(arm)));
            }
            var allocation=RcsWrenchAllocator.allocate(jets,acceleration.mul(mass),v(torque),scale);
            if(!Double.isFinite(allocation.forceError())||!Double.isFinite(allocation.torqueError())||allocation.forceError()>.01||allocation.torqueError()>.01)return fail("INSUFFICIENT_AUTHORITY");
            if(!lease.apply(allocation.throttles()))return Optional.empty();
            return Optional.of(allocation);
        }catch(RuntimeException invalid){return fail("ACTUATOR_ERROR");}
    }
    private Optional<RcsWrenchAllocator.Allocation> fail(String why){failure=why;lease.close();return Optional.empty();}
    private static boolean finite(V x){return x!=null&&Double.isFinite(x.x())&&Double.isFinite(x.y())&&Double.isFinite(x.z());}
    private static Vector3d j(V x){return new Vector3d(x.x(),x.y(),x.z());}
    private static V v(Vector3dc x){return new V(x.x(),x.y(),x.z());}
    @Override public void close(){lease.close();}
}
