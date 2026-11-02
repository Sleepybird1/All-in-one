package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.enemy.EnemyCannonHold;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Pseudo
@Mixin(targets="rbasamoyai.createbigcannons.cannon_control.contraption.MountedAutocannonContraption",remap=false)
public class EnemyCannonShotGuardMixin implements dev.godpc.industrialcolonies.space.enemy.EnemyNativeFiringHooks {
 @Unique public boolean ic$enemyShotGuard(){return true;}
 @Inject(method="fireShot",at=@At("HEAD"),cancellable=true,require=1)
 private void held(net.minecraft.server.level.ServerLevel level,rbasamoyai.createbigcannons.cannon_control.contraption.PitchOrientedContraptionEntity entity,CallbackInfo ci){
  if(!EnemyCannonHold.beforeShot(this)){ci.cancel();}
 }
}
