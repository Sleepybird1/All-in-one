package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.AllRecipeTypes;
import com.simibubi.create.content.kinetics.mixer.MechanicalMixerBlockEntity;
import dev.godpc.industrialcolonies.TieredRecipeBindings;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Adds custom MIXING/BASIN types to the mixer's global recipe trie. */
@Mixin(MechanicalMixerBlockEntity.class)
public abstract class MechanicalMixerBlockEntityMixin {
    @Inject(
            method = "matchStaticFilters(Lnet/minecraft/world/item/crafting/RecipeHolder;)Z",
            at = @At("HEAD"),
            cancellable = true
    )
    private void industrialColonies$recognizeTieredMixing(
            RecipeHolder<? extends Recipe<?>> holder,
            CallbackInfoReturnable<Boolean> callback
    ) {
        TieredRecipeBindings.Binding binding = TieredRecipeBindings.get(holder.value());
        if (binding != null) {
            AllRecipeTypes family = binding.family().baseType();
            callback.setReturnValue(family == AllRecipeTypes.MIXING || family == AllRecipeTypes.BASIN);
        }
    }
}
