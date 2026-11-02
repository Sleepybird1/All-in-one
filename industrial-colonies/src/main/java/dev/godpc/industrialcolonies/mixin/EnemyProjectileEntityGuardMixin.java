package dev.godpc.industrialcolonies.mixin;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;import org.spongepowered.asm.mixin.injection.At;import org.spongepowered.asm.mixin.injection.Inject;import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Pseudo
@Mixin(targets="rbasamoyai.createbigcannons.munitions.AbstractCannonProjectile",remap=false)
public abstract class EnemyProjectileEntityGuardMixin implements dev.godpc.industrialcolonies.space.enemy.EnemyNativeFiringHooks {
 @Unique public boolean ic$enemyEntityGuard(){return true;}
 @Inject(method="onHitEntity",at=@At("HEAD"),cancellable=true,remap=false,require=1) private void guard(net.minecraft.world.entity.Entity victim,rbasamoyai.createbigcannons.munitions.ProjectileContext context,CallbackInfoReturnable<Boolean> cir){if(!dev.godpc.industrialcolonies.space.enemy.EnemyOwnedProjectile.beforeEntity((net.minecraft.world.entity.Entity)(Object)this))cir.setReturnValue(false);}
}
