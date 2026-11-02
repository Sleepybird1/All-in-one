package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.enemy.EnemyCannonHold;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Pseudo
@Mixin(targets="rbasamoyai.createbigcannons.cannons.autocannon.breech.AbstractAutocannonBreechBlockEntity",remap=false)
public class EnemyCannonRateGuardMixin implements dev.godpc.industrialcolonies.space.enemy.EnemyNativeFiringHooks {
 @Unique public boolean ic$enemyRateGuard(){return true;}
 @Inject(method="setFireRate",at=@At("HEAD"),cancellable=true,require=1)
 private void held(int rate,CallbackInfo ci){if(!EnemyCannonHold.beforeRate(this,rate)){ci.cancel();}}
}
