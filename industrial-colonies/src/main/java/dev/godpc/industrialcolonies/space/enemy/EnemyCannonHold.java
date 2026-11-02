package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.SpaceflightAuthorization;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import java.util.*;

/** Explicit disarmed ownership of an NPC mounted autocannon. A scoped single
 * shot requires current targeting, conditional source/environment clearance and
 * every native stop/emission hook. No background firing or automatic resume.
 * Optional CBC references remain reflective; registration is staged only. */
public final class EnemyCannonHold implements AutoCloseable {
    private static final Map<Object,EnemyCannonHold> CANNONS=new IdentityHashMap<>();
    private static final Map<Object,EnemyCannonHold> BREECHES=new IdentityHashMap<>();
    // Keep the synchronous call attributed even if disable/claim closes and
    // removes its normal hold before native projectile world admission.
    private static final Map<Object,EnemyCannonHold> FIRING_CANNONS=new IdentityHashMap<>();
    private static final Map<Object,EnemyCannonHold> FIRING_BREECHES=new IdentityHashMap<>();
    private static boolean registered;
    private final ServerSubLevel body;
    private final NativeEnemyHull hull;
    private final BlockPos mount;
    private final Object mountEntity,cannonEntity,cannon,breech;
    private long refreshed;
    private boolean closed;
    private String reason="HELD_DISARMED";
    private FireScope firing;
    private static final class FireScope {
        final EnemyImpactAuthority authority; final EnemyProjectileProfile.Profile profile;
        boolean armingWrite; int rateWrites,shots,emissions,casings; boolean casingAdmitted; Entity projectile,casing;
        FireScope(EnemyImpactAuthority authority,EnemyProjectileProfile.Profile profile){this.authority=authority;this.profile=profile;}
    }
    public record FireResult(boolean fired,String reason,int emissions) {}
    private EnemyCannonHold(ServerSubLevel body,NativeEnemyHull hull,BlockPos mount,
            Object mountEntity,Object cannonEntity,Object cannon,Object breech) {
        this.body=body;this.hull=hull;this.mount=mount.immutable();this.mountEntity=mountEntity;
        this.cannonEntity=cannonEntity;this.cannon=cannon;this.breech=breech;
        refreshed=body.getLevel().getGameTime();
    }
    public static void register() {
        if(registered)return;registered=true;
        NeoForge.EVENT_BUS.addListener((ServerTickEvent.Pre e)->enforce(e.getServer()));
        NeoForge.EVENT_BUS.addListener((ServerStoppingEvent e)->{
            for(var hold:List.copyOf(CANNONS.values()))if(hold.body.getLevel().getServer()==e.getServer())hold.close("SERVER_STOP");
            EnemyOwnedProjectile.releaseServer(e.getServer());
            EnemySpentCasing.releaseServer(e.getServer());
        });
    }
    public static Optional<EnemyCannonHold> acquire(ServerSubLevel body,NativeEnemyHull hull,BlockPos mount) {
        if(body==null||hull==null||mount==null||!hull.belongsTo(body)||!hull.observes(mount)
                ||CANNONS.size()>=128||!EnemyTargetSelector.mayControlSource(body,hull)||SpaceflightAuthorization.automationDisabled(body))return Optional.empty();
        try {
            var frame=EnemyWeaponFrame.commission(body,hull,mount).sample();if(frame.isEmpty())return Optional.empty();
            var be=body.getLevel().getBlockEntity(mount);
            var entity=be.getClass().getMethod("getContraption").invoke(be);
            var cannon=entity.getClass().getMethod("getContraption").invoke(entity);
            var start=cannon.getClass().getMethod("getStartPos").invoke(cannon);
            var entities=(Map<?,?>)cannon.getClass().getField("presentBlockEntities").get(cannon);
            var breech=entities.get(start);
            if(breech==null||CANNONS.containsKey(cannon)||BREECHES.containsKey(breech)
                    ||((Number)breech.getClass().getMethod("getFireRate").invoke(breech)).intValue()!=0)return Optional.empty();
            var hold=new EnemyCannonHold(body,hull,mount,be,entity,cannon,breech);
            register();CANNONS.put(cannon,hold);BREECHES.put(breech,hold);return Optional.of(hold);
        }catch(ReflectiveOperationException|RuntimeException unavailable){return Optional.empty();}
    }
    public boolean refresh() {requireThread();if(!validate())return false;refreshed=body.getLevel().getGameTime();return true;}
    public boolean active(){return !closed;}
    public String reason(){return reason;}
    boolean owns(ServerSubLevel candidate,NativeEnemyHull manifest){return body==candidate&&hull==manifest&&validate();}
    boolean ownsMount(ServerSubLevel candidate,NativeEnemyHull manifest,BlockPos position){
        return mount.equals(position)&&owns(candidate,manifest);
    }
    public static void enforce(MinecraftServer server) {
        for(var hold:List.copyOf(CANNONS.values()))if(hold.body.getLevel().getServer()==server)hold.validate();
    }
    private boolean validate() {
        requireThread();if(closed)return false;
        try {
            long now=body.getLevel().getGameTime();String failure=null;
            if(now<refreshed||now-refreshed>2)failure="WATCHDOG_EXPIRED";
            else if(!EnemyTargetSelector.mayControlSource(body,hull)||SpaceflightAuthorization.automationDisabled(body))failure="AUTHORITY_OR_CONTROL_LOST";
            else if(body.getLevel().getBlockEntity(mount)!=mountEntity
                    ||mountEntity.getClass().getMethod("getContraption").invoke(mountEntity)!=cannonEntity
                    ||cannonEntity.getClass().getMethod("getContraption").invoke(cannonEntity)!=cannon)failure="CANNON_CHANGED";
            else {
                int rate=((Number)breech.getClass().getMethod("getFireRate").invoke(breech)).intValue();
                if(rate!=0&&(firing==null||firing.rateWrites!=1||rate!=1))failure="ARMED_OVERRIDE";
            }
            if(failure!=null){close(failure);return false;}return true;
        }catch(ReflectiveOperationException|RuntimeException unavailable){close("NATIVE_UNAVAILABLE");return false;}
    }
    /** Native mixin boundary: only the one synchronous admitted call may fire. */
    public static boolean beforeShot(Object cannon) {
        var hold=CANNONS.get(cannon);if(hold==null)hold=FIRING_CANNONS.get(cannon);if(hold==null)return true;
        hold.requireThread();
        if(!hold.validate()||hold.firing==null)return false;
        if(hold.firing.shots!=0||!hold.firing.authority.flight().allowed()){
            hold.close("FINITE_SHOT_REENTRY_OR_AUTHORITY_LOST");return false;
        }
        hold.firing.shots++;return true;
    }
    /** Positive manual/native arming interrupts the hold and refuses that write.
     * A later explicit manual operation is outside this autonomous ownership. */
    public static boolean beforeRate(Object breech,int rate) {
        var hold=BREECHES.get(breech);if(hold==null)hold=FIRING_BREECHES.get(breech);if(hold==null||rate==0)return true;
        hold.requireThread();
        if(hold.firing!=null&&hold.firing.armingWrite&&hold.firing.rateWrites==0&&rate==1&&hold.validate()){
            hold.firing.rateWrites++;return true;
        }
        hold.close("ARMING_OVERRIDE");return false;
    }
    /** Called only by the exact native projectile addFreshEntity boundary,
     * after shoot and before world admission. Spent casings use a different call. */
    public static boolean beforeEmission(Object cannon,Entity projectile) {
        var hold=CANNONS.get(cannon);if(hold==null)hold=FIRING_CANNONS.get(cannon);if(hold==null)return true;
        hold.requireThread();var scope=hold.firing;
        if(scope==null||scope.shots!=1||scope.emissions!=0||!hold.validate()
                ||!(projectile instanceof EnemyNativeFiringHooks hooks)||!hooks.ic$enemyProjectileGuards()
                ||!EnemyOwnedProjectile.bind(projectile,hold,scope.authority,scope.profile.lifetime())) {
            projectile.discard();hold.close("FINITE_EMISSION_REFUSED");return false;
        }
        scope.projectile=projectile;scope.emissions++;return true;
    }
    /** Only one output at the actual synchronous native casing boundary.
     * Refusal never deletes an already admitted physical item or refunds ammo. */
    public static boolean beforeCasing(Object cannon,Entity candidate) {
        var hold=CANNONS.get(cannon);if(hold==null)hold=FIRING_CANNONS.get(cannon);if(hold==null)return true;
        hold.requireThread();var scope=hold.firing;
        if(scope==null||scope.shots!=1||scope.casings!=0||!hold.validate()
                ||!scope.authority.flight().allowed()||!EnemySpentCasing.bind(candidate,hold.body,hold.hull)) {
            hold.close("FINITE_CASING_REFUSED");return false;
        }
        scope.casing=candidate;scope.casings++;return true;
    }
    public static void afterCasingAdmission(Object cannon,Entity candidate,boolean admitted) {
        var hold=CANNONS.get(cannon);if(hold==null)hold=FIRING_CANNONS.get(cannon);if(hold==null)return;
        hold.requireThread();var scope=hold.firing;
        if(scope==null||scope.casing!=candidate||scope.casings!=1||!admitted
                ||hold.body.getLevel().getEntity(candidate.getUUID())!=candidate) {
            EnemySpentCasing.admissionFailed(candidate);hold.close("FINITE_CASING_ADMISSION_FAILED");return;
        }
        scope.casingAdmitted=true;
    }
    /** Caller reserves are explicit conditional bounds, not a claim that unknown
     * future forces/traffic are impossible. Impact guards remain authoritative.
     * Failed native admission never manufactures ammunition or recoil refunds. */
    public FireResult fireOnce(ServerSubLevel target,EnemyWeaponTarget observer,
            EnemyTurretAimPlan planner,EnemyTurretAimPlan.Plan plan,
            EnemyProjectileProfile reader,EnemyProjectileProfile.Profile profile,
            EnemyImpactAuthority authority,double accelerationReserve,double angularAccelerationReserve,
            double sourceVelocityImpulseReserve,double sourceAngularImpulseReserve) {
        requireThread();
        if(firing!=null||!validate())return new FireResult(false,"HELD_OR_ALREADY_FIRING",0);
        if(!(cannon instanceof EnemyNativeFiringHooks nativeCannon)||!nativeCannon.ic$enemyShotGuard()
                ||!nativeCannon.ic$enemyEmissionGuard()||!nativeCannon.ic$enemyCasingGuard()||!(breech instanceof EnemyNativeFiringHooks nativeBreech)
                ||!nativeBreech.ic$enemyRateGuard())return new FireResult(false,"NATIVE_CANNON_GUARDS_UNAVAILABLE",0);
        if(authority==null||authority.source()!=body||authority.hull()!=hull||!authority.targets(target)
                ||!authority.flight().allowed()||profile==null||!(cannonEntity instanceof Entity ce)
                ||!profile.weapon().cannon().equals(ce.getUUID()))return new FireResult(false,"WRONG_FINITE_AUTHORITY",0);
        var clearance=EnemyProjectileCorridor.check(body,target,observer,planner,plan,reader,profile,
                accelerationReserve,angularAccelerationReserve);
        if(!clearance.clear())return new FireResult(false,clearance.reason(),0);
        var source=EnemyProjectileCorridor.sourceClearance(body,profile,sourceVelocityImpulseReserve,
                sourceAngularImpulseReserve,accelerationReserve,angularAccelerationReserve);
        if(!source.clear())return new FireResult(false,source.reason(),0);
        var type=BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.parse("createbigcannons:machine_gun_bullet")).orElse(null);
        Entity probe=type==null?null:type.create(body.getLevel());
        boolean guarded=probe instanceof EnemyNativeFiringHooks hooks&&hooks.ic$enemyProjectileGuards();
        if(probe!=null)probe.discard();
        if(!guarded)return new FireResult(false,"NATIVE_PROJECTILE_GUARDS_UNAVAILABLE",0);
        var scope=new FireScope(authority,profile);int before;
        try{before=ammunitionCount();}catch(ReflectiveOperationException|RuntimeException unavailable){return new FireResult(false,"AMMUNITION_UNAVAILABLE",0);}
        if(before<1)return new FireResult(false,"NO_AMMUNITION",0);
        firing=scope;FIRING_CANNONS.put(cannon,this);FIRING_BREECHES.put(breech,this);
        try {
            scope.armingWrite=true;
            try{breech.getClass().getMethod("setFireRate",int.class).invoke(breech,1);}finally{scope.armingWrite=false;}
            if(scope.rateWrites!=1||!Boolean.TRUE.equals(breech.getClass().getMethod("canFire").invoke(breech)))
                return new FireResult(false,"NATIVE_BREECH_NOT_READY",0);
            cannon.getClass().getMethod("fireShot",net.minecraft.server.level.ServerLevel.class,
                    Class.forName("rbasamoyai.createbigcannons.cannon_control.contraption.PitchOrientedContraptionEntity")).invoke(cannon,body.getLevel(),cannonEntity);
            Entity bullet=scope.projectile;
            if(scope.shots!=1||scope.emissions!=1||scope.casings!=1||!scope.casingAdmitted
                    ||!EnemySpentCasing.ownedBy(body,scope.casing)||bullet==null||bullet.isRemoved()
                    ||body.getLevel().getEntity(bullet.getUUID())!=bullet||ammunitionCount()!=before-1
                    ||!EnemyOwnedProjectile.beforeTick(bullet)){
                if(bullet!=null)bullet.discard();close("FINITE_EMISSION_NOT_EXACT");
                return new FireResult(false,"FINITE_EMISSION_NOT_EXACT",scope.emissions);
            }
            var muzzle=profile.weapon().muzzle();var central=profile.centralLaunchVelocity();
            if(bullet.position().distanceTo(new net.minecraft.world.phys.Vec3(muzzle.x(),muzzle.y(),muzzle.z()))>.002
                    ||bullet.getDeltaMovement().distanceTo(new net.minecraft.world.phys.Vec3(central.x(),central.y(),central.z()))>profile.physicalVelocityNoiseRadius()+1e-9){
                bullet.discard();close("FINITE_LAUNCH_OUTSIDE_PROFILE");
                return new FireResult(false,"FINITE_LAUNCH_OUTSIDE_PROFILE",scope.emissions);
            }
            return new FireResult(true,"ONE_EXACT_NATIVE_EMISSION",1);
        }catch(ReflectiveOperationException|RuntimeException unavailable){
            if(scope.projectile!=null)scope.projectile.discard();close("FINITE_NATIVE_FAILURE");
            return new FireResult(false,"FINITE_NATIVE_FAILURE",scope.emissions);
        }finally{
            try{
                breech.getClass().getMethod("setFireRate",int.class).invoke(breech,0);
                if(((Number)breech.getClass().getMethod("getFireRate").invoke(breech)).intValue()!=0)
                    throw new IllegalStateException("Native disarm did not reach zero");
            }catch(ReflectiveOperationException|RuntimeException unavailable){
                if(scope.projectile!=null)scope.projectile.discard();close("FINITE_DISARM_FAILED");
                return new FireResult(false,"FINITE_DISARM_FAILED",scope.emissions);
            }finally{
                firing=null;FIRING_CANNONS.remove(cannon,this);FIRING_BREECHES.remove(breech,this);
            }
        }
    }
    private int ammunitionCount()throws ReflectiveOperationException {
        var queue=(Deque<?>)breech.getClass().getMethod("getInputBuffer").invoke(breech);if(queue.size()>128)return -1;
        int count=0;for(Object item:queue){if(!(item instanceof ItemStack stack))return -1;count=Math.addExact(count,stack.getCount());}return count;
    }
    private void requireThread(){if(!body.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread cannon hold required");}
    @Override public void close(){close("RELEASED");}
    private void close(String why) {
        requireThread();if(closed)return;closed=true;reason=why;
        try{breech.getClass().getMethod("setFireRate",int.class).invoke(breech,0);
            CANNONS.remove(cannon,this);BREECHES.remove(breech,this);}
        catch(ReflectiveOperationException|RuntimeException unavailable){reason=why+"_STOP_FAILED";}
    }
}
