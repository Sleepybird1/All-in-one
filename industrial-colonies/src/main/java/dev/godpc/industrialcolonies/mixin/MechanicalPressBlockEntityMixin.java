package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.AllRecipeTypes;
import com.simibubi.create.content.kinetics.press.MechanicalPressBlockEntity;
import dev.godpc.industrialcolonies.TieredRecipeBindings;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Adds custom COMPACTING types to the press's global recipe trie without team-specific cache data. */
@Mixin(MechanicalPressBlockEntity.class)
public abstract class MechanicalPressBlockEntityMixin {
    @Inject(
            method = "matchStaticFilters(Lnet/minecraft/world/item/crafting/RecipeHolder;)Z",
            at = @At("HEAD"),
            cancellable = true
    )
    private void industrialColonies$recognizeTieredCompacting(
            RecipeHolder<? extends Recipe<?>> holder,
            CallbackInfoReturnable<Boolean> callback
    ) {
        TieredRecipeBindings.Binding binding = TieredRecipeBindings.get(holder.value());
        if (binding != null) {
            callback.setReturnValue(binding.family().baseType() == AllRecipeTypes.COMPACTING);
        }
    }
}
