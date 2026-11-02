package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.RcsActuatorLease;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets="dev.devce.rocketnautics.content.blocks.RCSThrusterBlockEntity",remap=false)
public class RcsAutonomousInputMixin {
    @Inject(method="setActive",at=@At("HEAD"),cancellable=true)
    private void ic$manualActivation(boolean value,CallbackInfo ci){if(!RcsActuatorLease.beforeNativeWrite(this))ci.cancel();}
    @Inject(method="setThrottle",at=@At("HEAD"),cancellable=true)
    private void ic$manualThrottle(float value,CallbackInfo ci){if(!RcsActuatorLease.beforeNativeWrite(this))ci.cancel();}
}
