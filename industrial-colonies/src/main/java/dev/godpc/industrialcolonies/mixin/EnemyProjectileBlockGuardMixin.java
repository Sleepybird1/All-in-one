package dev.godpc.industrialcolonies.mixin;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import rbasamoyai.createbigcannons.munitions.AbstractCannonProjectile.ImpactResult;
/** Optional exact native block stop; untracked manual projectiles pass through. */
@Pseudo
@Mixin(targets="rbasamoyai.createbigcannons.munitions.autocannon.AbstractAutocannonProjectile",remap=false)
public abstract class EnemyProjectileBlockGuardMixin implements dev.godpc.industrialcolonies.space.enemy.EnemyNativeFiringHooks {
 @Unique public boolean ic$enemyBlockGuard(){return true;}
 @Inject(method="calculateBlockPenetration",at=@At("HEAD"),cancellable=true,remap=false,require=1)
 private void stop(rbasamoyai.createbigcannons.munitions.ProjectileContext context,net.minecraft.world.level.block.state.BlockState state,net.minecraft.world.phys.BlockHitResult hit,CallbackInfoReturnable<ImpactResult> cir){
  if(!dev.godpc.industrialcolonies.space.enemy.EnemyOwnedProjectile.beforeBlock((net.minecraft.world.entity.Entity)(Object)this,hit))cir.setReturnValue(new ImpactResult(ImpactResult.KinematicOutcome.STOP,true));
 }
 /** Recheck immediately before native damage, including ownership changes
  * from another callback after the initial penetration HEAD admission. */
 @org.spongepowered.asm.mixin.injection.Redirect(method="calculateBlockPenetration",at=@At(value="INVOKE",target="Lrbasamoyai/createbigcannons/base/PartialBlockDamageManager;damageBlock(Lnet/minecraft/core/BlockPos;FLnet/minecraft/world/level/block/state/BlockState;Lnet/minecraft/world/level/Level;)Z"),require=1)
 private boolean ownedDamage(rbasamoyai.createbigcannons.base.PartialBlockDamageManager manager,net.minecraft.core.BlockPos position,float amount,net.minecraft.world.level.block.state.BlockState state,net.minecraft.world.level.Level level,rbasamoyai.createbigcannons.munitions.ProjectileContext context,net.minecraft.world.level.block.state.BlockState originalState,net.minecraft.world.phys.BlockHitResult hit){
  if(!dev.godpc.industrialcolonies.space.enemy.EnemyOwnedProjectile.beforeBlock((net.minecraft.world.entity.Entity)(Object)this,hit))return false;
  return manager.damageBlock(position,amount,state,level);
 }
}
