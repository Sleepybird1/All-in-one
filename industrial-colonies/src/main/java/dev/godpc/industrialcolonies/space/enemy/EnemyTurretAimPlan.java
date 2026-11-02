package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import org.joml.Quaterniond;
import org.joml.Vector3d;
import java.util.Optional;

/** Read-only bounded pointing proposal for the qualified east-facing, upright
 * native mount. Commands require a separate exclusive actuator owner. This
 * tracks the observed center; it does not lead a projectile or permit firing. */
public final class EnemyTurretAimPlan {
    public record Plan(EnemyWeaponTarget.Sample observation,float yawRpm,float pitchRpm,
                       double errorDegrees,double desiredElevation,boolean aligned) {}
    private final ServerSubLevel source;
    private final NativeEnemyHull hull;
    private final BlockPos mount;
    private final EnemyWeaponTarget target;
    private EnemyTurretAimPlan(ServerSubLevel source,NativeEnemyHull hull,BlockPos mount,EnemyWeaponTarget target) {
        this.source=source;this.hull=hull;this.mount=mount.immutable();this.target=target;
    }
    public static EnemyTurretAimPlan commission(ServerSubLevel source,NativeEnemyHull hull,BlockPos mount,EnemyWeaponTarget target) {
        if(source==null||hull==null||mount==null||target==null||!hull.belongsTo(source)||!hull.observes(mount))
            throw new IllegalArgumentException("Bound commissioned native mount required");
        return new EnemyTurretAimPlan(source,hull,mount,target);
    }
    public Optional<Plan> plan(EnemyWeaponTarget.Sample observation) {
        if(!source.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread pointing required");
        if(observation==null||!observation.weapon().body().equals(source.getUniqueId())||!target.current(observation)
                ||!EnemyTargetSelector.mayControlSource(source,hull))return Optional.empty();
        try {
            var be=source.getLevel().getBlockEntity(mount);if(be==null)return Optional.empty();
            var state=be.getBlockState();
            if(!state.hasProperty(BlockStateProperties.HORIZONTAL_FACING)||!state.hasProperty(BlockStateProperties.VERTICAL_DIRECTION)
                    ||state.getValue(BlockStateProperties.HORIZONTAL_FACING)!=Direction.EAST
                    ||state.getValue(BlockStateProperties.VERTICAL_DIRECTION)!=Direction.DOWN)return Optional.empty();
            var entity=be.getClass().getMethod("getContraption").invoke(be);
            if(!(entity instanceof net.minecraft.world.entity.Entity e)||!e.getUUID().equals(observation.weapon().cannon()))return Optional.empty();
            double depression=((Number)entity.getClass().getMethod("maximumDepression").invoke(entity)).doubleValue();
            double elevation=((Number)entity.getClass().getMethod("maximumElevation").invoke(entity)).doubleValue();
            if(!Double.isFinite(depression)||!Double.isFinite(elevation)||depression<2||elevation<2)return Optional.empty();
            var p=observation.weapon().muzzle();var q=observation.center();var a=observation.weapon().axis();
            var delta=new Vector3d(q.x()-p.x(),q.y()-p.y(),q.z()-p.z());double range=delta.length();
            if(!delta.isFinite()||range<5||range>64)return Optional.empty();
            var inverse=new Quaterniond(source.logicalPose().orientation()).invert();
            var desired=inverse.transform(delta.div(range));var current=inverse.transform(new Vector3d(a.x(),a.y(),a.z()));
            double azimuth=Math.toDegrees(Math.atan2(desired.z,desired.x));
            double desiredPitch=Math.toDegrees(Math.asin(Math.max(-1,Math.min(1,desired.y))));
            if(Math.abs(azimuth)>60||desiredPitch<Math.max(-20,2-depression)||desiredPitch>Math.min(45,elevation-2))return Optional.empty();
            double yawError=wrap(azimuth-Math.toDegrees(Math.atan2(current.z,current.x)));
            double pitchError=desiredPitch-Math.toDegrees(Math.asin(Math.max(-1,Math.min(1,current.y))));
            double error=Math.toDegrees(Math.acos(Math.max(-1,Math.min(1,current.dot(desired)))));
            // Native mount converts RPM to 0.0375 degrees per ordinary tick.
            // The physical-axis sign is independently checked in the native fixture.
            float yaw=command(-yawError),pitch=command(pitchError);
            if(!target.current(observation))return Optional.empty();
            return Optional.of(new Plan(observation,yaw,pitch,error,desiredPitch,error<=.4));
        }catch(ReflectiveOperationException|RuntimeException unavailable){return Optional.empty();}
    }
    public boolean current(Plan expected){return expected!=null&&plan(expected.observation()).filter(expected::equals).isPresent();}
    private static float command(double degrees){return Math.abs(degrees)<=.25?0f:(float)Math.max(-16,Math.min(16,degrees/.0375));}
    private static double wrap(double degrees){return ((degrees+180)%360+360)%360-180;}
}
