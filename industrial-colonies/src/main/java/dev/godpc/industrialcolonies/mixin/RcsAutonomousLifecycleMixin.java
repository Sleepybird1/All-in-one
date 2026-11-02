package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.RcsActuatorLease;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets="dev.devce.rocketnautics.content.blocks.AbstractThrusterBlockEntity",remap=false)
public class RcsAutonomousLifecycleMixin {
    @Inject(method="onLoad",at=@At("TAIL"))
    private void ic$clearOrphanedActivation(CallbackInfo ci){RcsActuatorLease.onNativeLoad(this);}
    @Inject(method={"onChunkUnloaded","remove"},at=@At("HEAD"))
    private void ic$releaseUnloaded(CallbackInfo ci){RcsActuatorLease.onNativeUnload(this);}
}
