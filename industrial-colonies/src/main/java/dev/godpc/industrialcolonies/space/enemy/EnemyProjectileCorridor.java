package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3d;
import java.util.*;

/** Read-only prospective environment audit, not a shot permit. Covers the full
 * dry unimpacted lifetime and all launch noise, assuming the caller's explicit
 * future acceleration reserves hold. Source self-clearance, target impact /
 * ricochet and newly appearing obstacles require separate firing qualification. */
public final class EnemyProjectileCorridor {
    public record Result(boolean clear,String reason,int ticks,int blocks,int bodies) {}
    private EnemyProjectileCorridor() {}
    public static Result check(ServerSubLevel source,ServerSubLevel target,
            EnemyWeaponTarget observer,EnemyTurretAimPlan planner,EnemyTurretAimPlan.Plan plan,
            EnemyProjectileProfile reader,EnemyProjectileProfile.Profile profile,
            double accelerationReserve,double angularAccelerationReserve) {
        if(source==null||target==null||source==target||source.getLevel()!=target.getLevel()
                ||!source.getLevel().getServer().isSameThread()||observer==null||planner==null
                ||plan==null||reader==null||profile==null||!Double.isFinite(accelerationReserve)
                ||accelerationReserve<0||accelerationReserve>10
                ||!Double.isFinite(angularAccelerationReserve)||angularAccelerationReserve<0
                ||angularAccelerationReserve>2)return deny("INVALID_REQUEST",0,0,0);
        if(!plan.aligned())return deny("UNALIGNED",0,0,0);
        if(!observer.current(plan.observation()))return deny("STALE_TARGET",0,0,0);
        if(!planner.current(plan))return deny("STALE_AIM",0,0,0);
        if(!reader.current(profile))return deny("STALE_PROFILE",0,0,0);
        if(!profile.weapon().equals(plan.observation().weapon()))return deny("PROFILE_FRAME_MISMATCH",0,0,0);
        if(!profile.weapon().body().equals(source.getUniqueId())
                ||!plan.observation().authority().target().equals(target.getUniqueId()))
            return deny("WRONG_AUTHORITIES",0,0,0);
        if(profile.quadratic())return deny("QUADRATIC_FLIGHT_UNQUALIFIED",0,0,0);
        int blocks=0,bodies=0;
        try {
            var level=source.getLevel();var muzzle=profile.weapon().muzzle();var velocity=profile.centralLaunchVelocity();
            var path=EnemyProjectileEnvelope.forecast(new EnemyProjectileEnvelope.V(muzzle.x(),muzzle.y(),muzzle.z()),
                    new EnemyProjectileEnvelope.V(velocity.x(),velocity.y(),velocity.z()),profile.gravity(),profile.drag(),
                    profile.physicalVelocityNoiseRadius(),.002,profile.lifetime());
            var corridors=new ArrayList<AABB>();AABB all=null;
            for(int i=1;i<path.size();i++) {
                var a=path.get(i-1);var b=path.get(i);
                var corridor=new AABB(vector(a.position()),vector(b.position())).inflate(b.positionRadius()+profile.collisionRadius());
                corridors.add(corridor);all=all==null?corridor:all.minmax(corridor);
            }
            if(all==null||!finite(all)||all.getXsize()>256||all.getYsize()>256||all.getZsize()>256)
                return deny("SCAN_LIMIT",profile.lifetime(),0,0);
            // Native orbital cells start above Y1000 while this dimension's
            // ordinary block-building range ends at320. Qualify the entire
            // physical flight volume inside one actual current source/target
            // cell, wholly above build height. All chunk, block/fluid, body and
            // living-entity checks below still run; this never admits arbitrary
            // out-of-height paths or a change of native reference frame.
            boolean orbitalVoid=level.dimension().location().toString().equals("rocketnautics:deep_space")
                    &&all.minY>=level.getMaxBuildHeight()&&EnemyNativeFrame.common(source,target)
                    &&EnemyNativeFrame.contains(source,all);
            double horizon=profile.lifetime()*.05;
            var container=ServerSubLevelContainer.getContainer(level);
            if(container==null)return deny("BODY_INDEX_UNAVAILABLE",profile.lifetime(),0,0);
            for(var other:container.getAllSubLevels()) {
                if(other==source||other.isRemoved())continue;
                if(++bodies>128)return deny("BODY_SCAN_LIMIT",profile.lifetime(),blocks,bodies);
                var handle=RigidBodyHandle.of(other);
                if(!handle.isValid()||!other.getPlot().getLoadedChunks().iterator().hasNext())
                    return deny("OTHER_BODY_UNAVAILABLE",profile.lifetime(),blocks,bodies);
                var bounds=other.boundingBox().toMojang();var movement=handle.getLinearVelocity();double spin=handle.getAngularVelocity().length();
                if(!finite(bounds)||!Double.isFinite(movement.length())||!Double.isFinite(spin))
                    return deny("OTHER_MOTION_INVALID",profile.lifetime(),blocks,bodies);
                var center=other.logicalPose().transformPosition(new Vector3d(other.getMassTracker().getCenterOfMass()));
                double radius=Math.sqrt(Math.pow(Math.max(Math.abs(bounds.minX-center.x),Math.abs(bounds.maxX-center.x)),2)
                        +Math.pow(Math.max(Math.abs(bounds.minY-center.y),Math.abs(bounds.maxY-center.y)),2)
                        +Math.pow(Math.max(Math.abs(bounds.minZ-center.z),Math.abs(bounds.maxZ-center.z)),2));
                if(!Double.isFinite(radius))return deny("OTHER_MASS_CENTER_INVALID",profile.lifetime(),blocks,bodies);
                double margin=.1+radius*Math.min(2,spin*horizon+.5*angularAccelerationReserve*horizon*horizon)
                        +.5*accelerationReserve*horizon*horizon;
                var swept=bounds.minmax(bounds.move(movement.x()*horizon,movement.y()*horizon,movement.z()*horizon)).inflate(margin);
                if(other!=target&&corridors.stream().anyMatch(swept::intersects))
                    return deny("FOREIGN_BODY_IN_CORRIDOR",profile.lifetime(),blocks,bodies);
                // The authorized target is the only body exempted from solid
                // collision refusal; its fluids still invalidate dry dynamics.
                if(other==target)for(var holder:other.getPlot().getLoadedChunks()) {
                    var box=other.getPlot().getBoundingBox();if(box==null)return deny("TARGET_BOUNDS_UNAVAILABLE",profile.lifetime(),blocks,bodies);
                    long volume=(long)(box.maxX()-box.minX()+1)*(box.maxY()-box.minY()+1)*(box.maxZ()-box.minZ()+1);
                    if(volume>4096)return deny("TARGET_FLUID_SCAN_LIMIT",profile.lifetime(),blocks,bodies);
                    for(var p:BlockPos.betweenClosed(box.minX(),box.minY(),box.minZ(),box.maxX(),box.maxY(),box.maxZ()))
                        if(!level.getFluidState(p).isEmpty())return deny("TARGET_FLUID_UNQUALIFIED",profile.lifetime(),blocks,bodies);
                    break;
                }
            }
            var seen=new HashSet<BlockPos>();
            for(var corridor:corridors)for(var p:BlockPos.betweenClosed(BlockPos.containing(corridor.minX,corridor.minY,corridor.minZ),
                    BlockPos.containing(corridor.maxX,corridor.maxY,corridor.maxZ))) {
                if(!seen.add(p.immutable()))continue;
                if(++blocks>65536)return deny("BLOCK_SCAN_LIMIT",profile.lifetime(),blocks,bodies);
                if((p.getY()<level.getMinBuildHeight()||p.getY()>=level.getMaxBuildHeight())&&!orbitalVoid)return deny("HEIGHT_UNQUALIFIED",profile.lifetime(),blocks,bodies);
                if(!level.hasChunkAt(p))return deny("UNLOADED_CORRIDOR",profile.lifetime(),blocks,bodies);
                if(!level.getFluidState(p).isEmpty())return deny("FLUID_IN_CORRIDOR",profile.lifetime(),blocks,bodies);
                if(!level.getBlockState(p).getCollisionShape(level,p).isEmpty())return deny("TERRAIN_IN_CORRIDOR",profile.lifetime(),blocks,bodies);
            }
            int living=0;
            for(var entity:level.getAllEntities()) {
                if(!(entity instanceof LivingEntity)||entity.isRemoved())continue;
                if(++living>128)return deny("LIVING_SCAN_LIMIT",profile.lifetime(),blocks,bodies);
                if(dev.ryanhcode.sable.Sable.HELPER.getTrackingOrVehicleSubLevel(entity)!=null)
                    return deny("LIVING_SHIP_POSITION_UNQUALIFIED",profile.lifetime(),blocks,bodies);
                var motion=entity.getDeltaMovement();
                if(!Double.isFinite(motion.length())||motion.length()>2)return deny("LIVING_MOTION_UNQUALIFIED",profile.lifetime(),blocks,bodies);
                var swept=entity.getBoundingBox().minmax(entity.getBoundingBox().move(motion.scale(profile.lifetime())))
                        .inflate(.25+.5*accelerationReserve*horizon*horizon);
                if(corridors.stream().anyMatch(swept::intersects))return deny("LIVING_IN_CORRIDOR",profile.lifetime(),blocks,bodies);
            }
            if(!reader.current(profile)||!observer.current(plan.observation())||!planner.current(plan))
                return deny("STALE_AFTER_AUDIT",profile.lifetime(),blocks,bodies);
            if(orbitalVoid&&(!EnemyNativeFrame.common(source,target)||!EnemyNativeFrame.contains(source,all)))
                return deny("ORBITAL_FRAME_CHANGED_DURING_AUDIT",profile.lifetime(),blocks,bodies);
            return new Result(true,"CONDITIONAL_ENVIRONMENT_CLEAR_ONLY",profile.lifetime(),blocks,bodies);
        }catch(RuntimeException unavailable){return deny("OBSERVATION_UNAVAILABLE",profile.lifetime(),blocks,bodies);}
    }
    /** Source is never exempted here. Explicit impulse reserves cover additional
     * linear/angular speed from firing; these remain conditional caller bounds.
     * Audit each segment against its own elapsed-time expanded source hull. */
    public static Result sourceClearance(ServerSubLevel source,EnemyProjectileProfile.Profile profile,
            double velocityImpulseReserve,double angularImpulseReserve,
            double accelerationReserve,double angularAccelerationReserve) {
        if(source==null||profile==null||!source.getLevel().getServer().isSameThread()
                ||!profile.weapon().body().equals(source.getUniqueId())
                ||!Double.isFinite(velocityImpulseReserve)||velocityImpulseReserve<0||velocityImpulseReserve>10
                ||!Double.isFinite(angularImpulseReserve)||angularImpulseReserve<0||angularImpulseReserve>2
                ||!Double.isFinite(accelerationReserve)||accelerationReserve<0||accelerationReserve>10
                ||!Double.isFinite(angularAccelerationReserve)||angularAccelerationReserve<0||angularAccelerationReserve>2)
            return deny("INVALID_SOURCE_CLEARANCE",0,0,0);
        try {
            var handle=RigidBodyHandle.of(source);var bounds=source.boundingBox().toMojang();
            var movement=handle.getLinearVelocity();double spin=handle.getAngularVelocity().length();
            if(!handle.isValid()||!finite(bounds)||!Double.isFinite(movement.length())||!Double.isFinite(spin))
                return deny("SOURCE_MOTION_UNAVAILABLE",0,0,1);
            var center=source.logicalPose().transformPosition(new Vector3d(source.getMassTracker().getCenterOfMass()));
            double radius=Math.sqrt(Math.pow(Math.max(Math.abs(bounds.minX-center.x),Math.abs(bounds.maxX-center.x)),2)
                    +Math.pow(Math.max(Math.abs(bounds.minY-center.y),Math.abs(bounds.maxY-center.y)),2)
                    +Math.pow(Math.max(Math.abs(bounds.minZ-center.z),Math.abs(bounds.maxZ-center.z)),2));
            if(!Double.isFinite(radius))return deny("SOURCE_CENTER_UNAVAILABLE",0,0,1);
            var muzzle=profile.weapon().muzzle();var velocity=profile.centralLaunchVelocity();
            var path=EnemyProjectileEnvelope.forecast(new EnemyProjectileEnvelope.V(muzzle.x(),muzzle.y(),muzzle.z()),
                    new EnemyProjectileEnvelope.V(velocity.x(),velocity.y(),velocity.z()),profile.gravity(),profile.drag(),
                    profile.physicalVelocityNoiseRadius(),.002,profile.lifetime());
            for(int i=1;i<path.size();i++) {
                double t=i*.05;
                double margin=.1+radius*Math.min(2,(spin+angularImpulseReserve)*t+.5*angularAccelerationReserve*t*t)
                        +velocityImpulseReserve*t+.5*accelerationReserve*t*t;
                var swept=bounds.minmax(bounds.move(movement.x()*t,movement.y()*t,movement.z()*t)).inflate(margin);
                var corridor=new AABB(vector(path.get(i-1).position()),vector(path.get(i).position()))
                        .inflate(path.get(i).positionRadius()+profile.collisionRadius());
                if(swept.intersects(corridor))return deny("SOURCE_IN_CORRIDOR",i,0,1);
            }
            return new Result(true,"CONDITIONAL_SOURCE_CLEAR_ONLY",profile.lifetime(),0,1);
        }catch(RuntimeException unavailable){return deny("SOURCE_OBSERVATION_UNAVAILABLE",0,0,1);}
    }
    private static Vec3 vector(EnemyProjectileEnvelope.V v){return new Vec3(v.x(),v.y(),v.z());}
    private static boolean finite(AABB b){return Double.isFinite(b.minX)&&Double.isFinite(b.minY)&&Double.isFinite(b.minZ)
            &&Double.isFinite(b.maxX)&&Double.isFinite(b.maxY)&&Double.isFinite(b.maxZ)
            &&Math.abs(b.minX)<30000000&&Math.abs(b.maxX)<30000000&&Math.abs(b.minZ)<30000000&&Math.abs(b.maxZ)<30000000;}
    private static Result deny(String reason,int ticks,int blocks,int bodies){return new Result(false,reason,ticks,blocks,bodies);}
}
