package dev.godpc.industrialcolonies.mixin;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;import org.spongepowered.asm.mixin.injection.At;import org.spongepowered.asm.mixin.injection.Inject;import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Pseudo
@Mixin(targets="rbasamoyai.createbigcannons.munitions.AbstractCannonProjectile",remap=false)
public abstract class EnemyProjectileTickGuardMixin implements dev.godpc.industrialcolonies.space.enemy.EnemyNativeFiringHooks {
 @Unique public boolean ic$enemyTickGuard(){return true;}
 @Inject(method="tick",at=@At("HEAD"),cancellable=true,remap=false,require=1) private void guard(CallbackInfo ci){if(!dev.godpc.industrialcolonies.space.enemy.EnemyOwnedProjectile.beforeTick((net.minecraft.world.entity.Entity)(Object)this))ci.cancel();}
}
