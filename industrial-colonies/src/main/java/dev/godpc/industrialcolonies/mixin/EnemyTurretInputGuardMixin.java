package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.enemy.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** Exact owned interface setter interruption; native write/maintenance remains intact. */
@Pseudo
@Mixin(targets="com.simibubi.create.content.kinetics.base.KineticBlockEntity",remap=false)
public class EnemyTurretInputGuardMixin implements EnemyNativeTurretHooks {
 @Unique public boolean ic$enemyRotationWriteGuard(){return true;}
 @Inject(method="setSpeed",at=@At("HEAD"),require=1)
 private void externalWrite(float rpm,CallbackInfo ci){EnemyTurretLease.beforeInputWrite(this);}
}
