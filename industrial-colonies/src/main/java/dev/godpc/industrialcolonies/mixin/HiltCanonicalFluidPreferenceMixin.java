package dev.godpc.industrialcolonies.mixin;

import java.util.Optional;
import net.minecraft.tags.TagKey;
import dev.godpc.industrialcolonies.processing.CanonicalFluidPreference;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets = "modernmods.hilt.recipe.helper.TagPreference", remap = false)
public abstract class HiltCanonicalFluidPreferenceMixin {
    @Inject(method = "getPreference", at = @At("HEAD"), cancellable = true, require = 1, remap = false)
    private static void industrialColonies$canonicalFluid(TagKey<?> tag, CallbackInfoReturnable<Optional<?>> result) {
        var fluid = CanonicalFluidPreference.select(tag);
        if (fluid != null) result.setReturnValue(Optional.of(fluid));
    }
}
