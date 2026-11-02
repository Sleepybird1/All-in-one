package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.RadiationTagSnapshots;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Invalidate inside Bindings' existing lock, before its mutator can return. */
@Pseudo
@Mixin(targets = "igentuman.nr.api.binding.Bindings", remap = false)
public abstract class RadiationBindingMutationMixin {
    @Inject(method = {"putItemTag", "putBlockTag", "putFluidTag"},
            at = @At(value = "INVOKE", target = "Ljava/util/Map;put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;", shift = At.Shift.AFTER), require = 1)
    private static void industrialColonies$changedTag(CallbackInfo ci) { RadiationTagSnapshots.invalidate(); }

    @Inject(method = {"removeItemTag", "removeBlockTag", "removeFluidTag"},
            at = @At(value = "INVOKE", target = "Ljava/util/Map;remove(Ljava/lang/Object;)Ljava/lang/Object;", shift = At.Shift.AFTER), require = 1)
    private static void industrialColonies$removedTag(CallbackInfo ci) { RadiationTagSnapshots.invalidate(); }

    @Inject(method = "clear", at = @At(value = "INVOKE", target = "Ljava/util/Map;clear()V", shift = At.Shift.AFTER), require = 6)
    private static void industrialColonies$cleared(CallbackInfo ci) { RadiationTagSnapshots.invalidate(); }
}
