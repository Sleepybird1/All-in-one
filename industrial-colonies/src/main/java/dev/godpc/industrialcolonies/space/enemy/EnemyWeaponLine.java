package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** Read-only instantaneous native block line. A clear line is NOT projectile
 * clearance or firing authority: future motion, spread and native dynamics
 * require separate qualification. No body, weapon or inventory writes. */
public final class EnemyWeaponLine {
    public record Result(boolean targetFirst, String reason) {}
    private EnemyWeaponLine() {}
    public static Result check(ServerSubLevel source, ServerSubLevel target,
            EnemyWeaponTarget observer, EnemyTurretAimPlan planner, EnemyTurretAimPlan.Plan plan) {
        if(source==null||target==null||source==target||observer==null||planner==null||plan==null
                ||source.getLevel()!=target.getLevel()||!source.getLevel().getServer().isSameThread())
            return denied("INVALID_REQUEST");
        if(!plan.observation().weapon().body().equals(source.getUniqueId())
                ||!plan.observation().authority().target().equals(target.getUniqueId())
                ||!observer.current(plan.observation())||!planner.current(plan))return denied("STALE_TARGET_OR_AIM");
        if(!plan.aligned())return denied("UNALIGNED");
        try {
            var sample=plan.observation();var p=sample.weapon().muzzle();var a=sample.weapon().axis();var q=sample.center();
            var start=new Vec3(p.x(),p.y(),p.z());double range=start.distanceTo(new Vec3(q.x(),q.y(),q.z()));
            if(!Double.isFinite(range)||range<5||range>64)return denied("UNSAFE_RANGE");
            var end=start.add(a.x()*range,a.y()*range,a.z()*range);var level=source.getLevel();
            // Refuse missing main-level chunks; native ship clips additionally
            // require the fresh, loaded authority/frame observations above.
            int steps=(int)Math.ceil(range*2);
            for(int i=0;i<=steps;i++)if(!level.hasChunkAt(BlockPos.containing(start.lerp(end,(double)i/steps))))
                return denied("UNLOADED_LINE");
            var corridor=new AABB(start,end).inflate(.25);
            if(!level.getEntitiesOfClass(LivingEntity.class,corridor,
                    e->e.getBoundingBox().inflate(.25).clip(start,end).isPresent()).isEmpty())return denied("LIVING_OBSTRUCTION");
            // Installed Sable projects ordinary Level.clip into intersecting
            // ship plots and returns the hit block in that plot. Ignore none.
            var hit=level.clip(new ClipContext(start,end,ClipContext.Block.COLLIDER,ClipContext.Fluid.ANY,
                    net.minecraft.world.phys.shapes.CollisionContext.empty()));
            if(hit.getType()!=HitResult.Type.BLOCK)return denied("NO_TARGET_BLOCK");
            if(Sable.HELPER.getContaining(level,hit.getBlockPos())!=target)return denied("NON_TARGET_OBSTRUCTION");
            if(!observer.current(sample)||!planner.current(plan))return denied("STALE_AFTER_CLIP");
            return new Result(true,"INSTANTANEOUS_TARGET_FIRST_ONLY");
        }catch(RuntimeException unavailable){return denied("CLIP_UNAVAILABLE");}
    }
    private static Result denied(String reason){return new Result(false,reason);}
}
