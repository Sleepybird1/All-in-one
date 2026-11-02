package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.enemy.EnemyCannonHold;
import dev.godpc.industrialcolonies.space.enemy.EnemyNativeFiringHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.*;
/** Exact native spent-casing admission, separate from projectile ordinal1. */
@Pseudo
@Mixin(targets="rbasamoyai.createbigcannons.cannon_control.contraption.MountedAutocannonContraption",remap=false)
public abstract class EnemyCannonCasingGuardMixin implements EnemyNativeFiringHooks {
 @Unique public boolean ic$enemyCasingGuard(){return true;}
 @Redirect(method="fireShot",at=@At(value="INVOKE",target="Lnet/minecraft/server/level/ServerLevel;addFreshEntity(Lnet/minecraft/world/entity/Entity;)Z",ordinal=0),require=1)
 private boolean ownedCasing(net.minecraft.server.level.ServerLevel level,net.minecraft.world.entity.Entity candidate){
  if(!EnemyCannonHold.beforeCasing(this,candidate))return false;
  boolean admitted=level.addFreshEntity(candidate);
  EnemyCannonHold.afterCasingAdmission(this,candidate,admitted);return admitted;
 }
}
