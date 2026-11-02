package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.KjsGenIntegration;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Keep known processor user layouts codec-correct without rewriting any user file. */
@Mixin(targets = "com.zizazr.kjsgen.templates.UserLayoutStore", remap = false)
public abstract class KjsGenUserMachineLayoutsMixin {
    @Inject(method = "loadAll", at = @At("TAIL"))
    private static void industrialColonies$knownMachineCodecs(CallbackInfo callback) {
        KjsGenIntegration.installKnownUserMachineDefinitions();
    }
}
