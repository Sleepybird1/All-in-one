package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.enemy.EnemyCannonHold;
import dev.godpc.industrialcolonies.space.enemy.EnemyNativeFiringHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.*;
/** Only the projectile admission (ordinal1), never the spent casing (ordinal0). */
@Pseudo
@Mixin(targets="rbasamoyai.createbigcannons.cannon_control.contraption.MountedAutocannonContraption",remap=false)
public abstract class EnemyCannonEmissionGuardMixin implements EnemyNativeFiringHooks {
 @Unique public boolean ic$enemyEmissionGuard(){return true;}
 @Redirect(method="fireShot",at=@At(value="INVOKE",target="Lnet/minecraft/server/level/ServerLevel;addFreshEntity(Lnet/minecraft/world/entity/Entity;)Z",ordinal=1),require=1)
 private boolean ownedEmission(net.minecraft.server.level.ServerLevel level,net.minecraft.world.entity.Entity candidate){return EnemyCannonHold.beforeEmission(this,candidate)&&level.addFreshEntity(candidate);}
}
