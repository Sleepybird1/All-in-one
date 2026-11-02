package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.transport.MekanismRangeSnapshot;
import mekanism.common.content.network.transmitter.Transmitter;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Refuse before the native pull routine can extract any source resource. */
@Pseudo
@Mixin(targets = {"mekanism.common.content.network.transmitter.MechanicalPipe",
        "mekanism.common.content.network.transmitter.PressurizedTube"}, remap = false)
public abstract class MekanismPipeTubePullRangeMixin {
    @Inject(method = "pullFromAcceptors", at = @At("HEAD"), cancellable = true)
    private void ic$holdNativePull(CallbackInfo callback) {
        var transmitter = (Transmitter<?, ?, ?>) (Object) this;
        if (!transmitter.hasTransmitterNetwork()
                || !MekanismRangeSnapshot.inspect(transmitter.getTransmitterNetwork()).allowsNewIngress()) callback.cancel();
    }
}
