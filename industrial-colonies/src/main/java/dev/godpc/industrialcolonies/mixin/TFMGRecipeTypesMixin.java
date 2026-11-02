package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Optional;

/** Filters TFMG's shared exact-holder lookup inside its owned SmartBlockEntity tick. */
@Mixin(targets = "com.drmangotea.tfmg.registry.TFMGRecipeTypes", remap = false)
public abstract class TFMGRecipeTypesMixin {
    @Inject(method = "find", at = @At("RETURN"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedTFMGRecipe(
            CallbackInfoReturnable<Optional<RecipeHolder<?>>> callback
    ) {
        Optional<RecipeHolder<?>> recipe = callback.getReturnValue();
        if (recipe != null && recipe.isPresent()
                && !CreateRecipeStageGate.canUseCurrent(recipe.get())) {
            callback.setReturnValue(Optional.empty());
        }
    }
}
