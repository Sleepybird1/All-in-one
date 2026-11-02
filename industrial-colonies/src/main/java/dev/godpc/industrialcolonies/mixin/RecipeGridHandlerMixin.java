package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.kinetics.crafter.RecipeGridHandler;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Prevents a mechanical crafter's regular-crafting fallback from bypassing mapped stages. */
@Mixin(RecipeGridHandler.class)
public abstract class RecipeGridHandlerMixin {
    @Inject(
            method = "isRecipeAllowed(Lnet/minecraft/world/item/crafting/RecipeHolder;"
                    + "Lnet/minecraft/world/item/crafting/CraftingInput;)Z",
            at = @At("HEAD"),
            cancellable = true
    )
    private static void industrialColonies$denyLockedRegularRecipe(
            RecipeHolder<CraftingRecipe> recipe,
            CraftingInput input,
            CallbackInfoReturnable<Boolean> callback
    ) {
        if (!CreateRecipeStageGate.canUseCurrent(recipe)) {
            callback.setReturnValue(false);
        }
    }
}
