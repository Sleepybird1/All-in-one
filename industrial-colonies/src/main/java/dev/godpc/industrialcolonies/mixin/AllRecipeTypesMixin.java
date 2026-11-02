package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.AllRecipeTypes;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeInput;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Optional;

/** Adds tiered family visibility and exact owner-team filtering to ordinary Create lookups. */
@Mixin(AllRecipeTypes.class)
public abstract class AllRecipeTypesMixin {
    @SuppressWarnings({"rawtypes", "unchecked"})
    @Inject(
            method = "find(Lnet/minecraft/world/item/crafting/RecipeInput;"
                    + "Lnet/minecraft/world/level/Level;)Ljava/util/Optional;",
            at = @At("HEAD"),
            cancellable = true
    )
    private void industrialColonies$findAllowedTieredRecipe(
            RecipeInput input,
            Level level,
            CallbackInfoReturnable<Optional<RecipeHolder<?>>> callback
    ) {
        Optional result = CreateRecipeStageGate.find((AllRecipeTypes) (Object) this, input, level);
        callback.setReturnValue(result);
    }
}
