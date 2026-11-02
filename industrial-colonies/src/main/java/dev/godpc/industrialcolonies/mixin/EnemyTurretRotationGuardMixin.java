package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.enemy.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
/** Only the native mount tick consumes the leased RPM; no network getter override. */
@Pseudo
@Mixin(targets="rbasamoyai.createbigcannons.cannon_control.cannon_mount.CannonMountBlockEntity",remap=false)
public class EnemyTurretRotationGuardMixin implements EnemyNativeTurretHooks {
 @Unique public boolean ic$enemyRotationReadGuard(){return true;}
 @Redirect(method="tick",at=@At(value="INVOKE",target="Lrbasamoyai/createbigcannons/cannon_control/cannon_mount/CannonMountInterfaceBlockEntity;getSpeed()F"),require=2,allow=2)
 private float leasedRotation(@Coerce Object input){
  try{return EnemyTurretLease.rotationInput(this,input,((Number)input.getClass().getMethod("getSpeed").invoke(input)).floatValue());}
  catch(ReflectiveOperationException unavailable){throw new IllegalStateException("Native turret input unavailable",unavailable);}
 }
}
