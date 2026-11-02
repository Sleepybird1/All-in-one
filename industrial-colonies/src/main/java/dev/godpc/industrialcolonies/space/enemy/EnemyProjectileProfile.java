package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import java.util.*;

/** Read-only loaded machine-gun profile, not a firing permit. Refuses other
 * ammunition, magazines, obstructed barrels and unavailable optional APIs.
 * Values include the loaded dimension modifiers; fluid drag and future traffic
 * require separate corridor qualification. No projectile is created here. */
public final class EnemyProjectileProfile {
    public record Profile(EnemyWeaponFrame.Sample weapon, String material,
            String materialProperties, String dimensionProperties, int barrels,
            float speed, float spread, double gravity, double drag, boolean quadratic, boolean inheritsShipVelocity, int lifetime, double collisionRadius) {
        /** Native triangular noise is added per coordinate before speed scaling. */
        public double velocityNoisePerAxis(){return .0172275 * (double)spread * (double)speed;}
        /** Rotation preserves the Euclidean norm of raw per-axis launch noise. */
        public double physicalVelocityNoiseRadius(){return Math.sqrt(3)*velocityNoisePerAxis();}
        public dev.godpc.industrialcolonies.space.RendezvousGuidance.V centralLaunchVelocity(){
            var a=weapon.axis();var v=weapon.velocity();double factor=inheritsShipVelocity?.05:0;
            return new dev.godpc.industrialcolonies.space.RendezvousGuidance.V(a.x()*speed+v.x()*factor,a.y()*speed+v.y()*factor,a.z()*speed+v.z()*factor);
        }
    }
    private final ServerSubLevel body;
    private final EnemyWeaponFrame frame;
    private final BlockPos mount;
    private EnemyProjectileProfile(ServerSubLevel body,NativeEnemyHull hull,BlockPos mount) {
        this.body=body;this.mount=mount.immutable();frame=EnemyWeaponFrame.commission(body,hull,mount);
    }
    public static EnemyProjectileProfile commission(ServerSubLevel body,NativeEnemyHull hull,BlockPos mount) {
        return new EnemyProjectileProfile(body,hull,mount);
    }
    public Optional<Profile> sample() {
        var observed=frame.sample();if(observed.isEmpty())return Optional.empty();
        try {
            var be=body.getLevel().getBlockEntity(mount);
            var entity=call(be,"getContraption");var cannon=call(entity,"getContraption");
            var start=(BlockPos)call(cannon,"getStartPos");var facing=(Direction)call(cannon,"initialOrientation");
            var entities=(Map<?,?>)cannon.getClass().getField("presentBlockEntities").get(cannon);
            var blocks=(Map<?,?>)call(cannon,"getBlocks");var breech=entities.get(start);
            if(breech==null||!((ItemStack)call(breech,"getMagazine")).isEmpty())return Optional.empty();
            var queue=(Deque<?>)call(breech,"getInputBuffer");
            if(!(queue.peekFirst() instanceof ItemStack ammo)||ammo.isEmpty()
                    ||!BuiltInRegistries.ITEM.getKey(ammo.getItem()).toString().equals("createbigcannons:machine_gun_round")
                    ||!ItemStack.isSameItemSameComponents(ammo,new ItemStack(ammo.getItem())))return Optional.empty();
            var field=cannon.getClass().getDeclaredField("cannonMaterial");field.setAccessible(true);
            var material=field.get(cannon);var props=call(material,"properties");
            float speed=number(props,"baseSpeed").floatValue(),spread=number(props,"baseSpread").floatValue();
            float increase=number(props,"speedIncreasePerBarrel").floatValue(),reduction=number(props,"spreadReductionPerBarrel").floatValue();
            int increases=number(props,"maxSpeedIncreases").intValue(),maximum=number(props,"maxBarrelLength").intValue();
            int barrels=0;var p=start.relative(facing);
            while(entities.containsKey(p)) {
                if(++barrels>256||barrels>maximum)return Optional.empty();
                var behavior=call(entities.get(p),"cannonBehavior");
                if(!Boolean.TRUE.equals(behavior.getClass().getMethod("canLoadItem",ItemStack.class).invoke(behavior,ammo)))return Optional.empty();
                if(barrels<=increases)speed+=increase;
                spread=Math.max(spread-reduction,0f);p=p.relative(facing);
            }
            if(barrels<1||barrels+1!=blocks.size()||!Float.isFinite(speed)||speed<=0||speed>64
                    ||!Float.isFinite(spread)||spread<0||spread>16)return Optional.empty();
            var ammoApi=Class.forName("rbasamoyai.createbigcannons.munitions.autocannon.AutocannonAmmoItem");
            if(!ammoApi.isInstance(ammo.getItem()))return Optional.empty();
            var type=ammoApi.getMethod("getEntityType",ItemStack.class).invoke(ammo.getItem(),ammo);
            if(!(type instanceof net.minecraft.world.entity.EntityType<?> entityType)
                    ||!BuiltInRegistries.ENTITY_TYPE.getKey(entityType).toString().equals("createbigcannons:machine_gun_bullet"))return Optional.empty();
            var dimensions=entityType.getDimensions();
            double collisionRadius=Math.sqrt(2*dimensions.width()*dimensions.width()+dimensions.height()*dimensions.height());
            int lifetime=number(props,"projectileLifetime").intValue();
            if(lifetime<1||lifetime>20||!Double.isFinite(collisionRadius)||collisionRadius<=0||collisionRadius>1)return Optional.empty();
            var handler=Class.forName("rbasamoyai.createbigcannons.index.CBCMunitionPropertiesHandlers").getField("INERT_AUTOCANNON_PROJECTILE").get(null);
            var projectileProps=handler.getClass().getMethod("getPropertiesOf",Object.class).invoke(handler,type);
            var ballistics=call(projectileProps,"ballistics");
            var dimension=Class.forName("rbasamoyai.createbigcannons.munitions.config.DimensionMunitionPropertiesHandler")
                    .getMethod("getProperties",Level.class).invoke(null,body.getLevel());
            double gravity=number(ballistics,"gravity").doubleValue()*number(dimension,"gravityMultiplier").doubleValue();
            double drag=number(ballistics,"drag").doubleValue()*number(dimension,"dragMultiplier").doubleValue();
            if(!Double.isFinite(gravity)||Math.abs(gravity)>1||!Double.isFinite(drag)||drag<0||drag>1)return Optional.empty();
            var config=Class.forName("rbasamoyai.createbigcannons.config.CBCConfigs").getMethod("server").invoke(null);
            var compat=config.getClass().getField("compat").get(config);
            var inherit=compat.getClass().getField("sableProjectilesInheritPhysicsObjectVelocity").get(compat);
            var flag=call(inherit,"get");if(!(flag instanceof Boolean))return Optional.empty();
            if(!frame.current(observed.get()))return Optional.empty();
            return Optional.of(new Profile(observed.get(),call(material,"name").toString(),call(props,"serialize").toString(),
                    call(dimension,"serialize").toString(),barrels,speed,spread,gravity,drag,
                    Boolean.TRUE.equals(call(ballistics,"isQuadraticDrag")),Boolean.TRUE.equals(flag),lifetime,collisionRadius));
        }catch(ReflectiveOperationException|RuntimeException unavailable){return Optional.empty();}
    }
    public boolean current(Profile expected){return expected!=null&&frame.current(expected.weapon())&&sample().filter(expected::equals).isPresent();}
    private static Object call(Object object,String method)throws ReflectiveOperationException{return object.getClass().getMethod(method).invoke(object);}
    private static Number number(Object object,String method)throws ReflectiveOperationException{return (Number)call(object,method);}
}
