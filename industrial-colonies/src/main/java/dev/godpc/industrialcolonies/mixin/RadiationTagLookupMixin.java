package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.RadiationTagSnapshots;
import java.util.Map;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Only the read-only resolver uses shared snapshots; external public APIs remain defensive. */
@Pseudo
@Mixin(targets = "igentuman.nr.api.binding.RadiationBindings", remap = false)
public abstract class RadiationTagLookupMixin {
    @Redirect(method = "of(Lnet/minecraft/world/item/ItemStack;)Ligentuman/nr/api/RadiationProfile;", at = @At(value = "INVOKE", target = "Ligentuman/nr/api/binding/Bindings;itemTags()Ljava/util/Map;"), require = 1)
    private static Map<?, ?> industrialColonies$itemTags() { return RadiationTagSnapshots.items(); }
    @Redirect(method = "of(Lnet/minecraft/world/level/block/state/BlockState;)Ligentuman/nr/api/RadiationProfile;", at = @At(value = "INVOKE", target = "Ligentuman/nr/api/binding/Bindings;blockTags()Ljava/util/Map;"), require = 1)
    private static Map<?, ?> industrialColonies$blockTags() { return RadiationTagSnapshots.blocks(); }
    @Redirect(method = "of(Lnet/minecraft/world/level/material/FluidState;)Ligentuman/nr/api/RadiationProfile;", at = @At(value = "INVOKE", target = "Ligentuman/nr/api/binding/Bindings;fluidTags()Ljava/util/Map;"), require = 1)
    private static Map<?, ?> industrialColonies$fluidTags() { return RadiationTagSnapshots.fluids(); }
}
