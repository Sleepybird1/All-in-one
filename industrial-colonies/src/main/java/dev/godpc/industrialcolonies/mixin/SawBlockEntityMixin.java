package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.AllRecipeTypes;
import com.simibubi.create.content.kinetics.saw.CuttingRecipe;
import com.simibubi.create.content.processing.recipe.ProcessingInventory;
import com.simibubi.create.foundation.blockEntity.behaviour.filtering.FilteringBehaviour;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import dev.godpc.industrialcolonies.TieredRecipeBindings;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.SingleRecipeInput;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Adds hidden machine-bound cutting types to the Saw's native RecipeFinder result. */
@Mixin(targets = "com.simibubi.create.content.kinetics.saw.SawBlockEntity")
public abstract class SawBlockEntityMixin {
    @Shadow
    public ProcessingInventory inventory;

    @Shadow
    private FilteringBehaviour filtering;

    @SuppressWarnings("unchecked")
    @Inject(method = "getRecipes", at = @At("RETURN"), cancellable = true)
    private void industrialColonies$includeMachineBoundCuttingRecipes(
            CallbackInfoReturnable<List<RecipeHolder<? extends Recipe<?>>>> callback
    ) {
        BlockEntity saw = (BlockEntity) (Object) this;
        List<RecipeHolder<? extends Recipe<?>>> recipes = callback.getReturnValue();
        if (recipes == null || saw.getLevel() == null) {
            return;
        }

        List<RecipeHolder<? extends Recipe<?>>> merged = new ArrayList<>();
        Set<net.minecraft.resources.ResourceLocation> seen = new HashSet<>();
        for (RecipeHolder<? extends Recipe<?>> recipe : recipes) {
            if (CreateRecipeStageGate.canUse(saw.getLevel(), recipe, saw)) {
                merged.add(recipe);
                seen.add(recipe.id());
            }
        }

        // SawBlockEntity's RecipeFinder predicate only recognizes the native
        // CUTTING type. Query the hidden types explicitly, then apply the same
        // output filter and automation exclusion as Create's own method.
        for (RecipeHolder<?> candidate : CreateRecipeStageGate.matchingAllowedRecipes(
                AllRecipeTypes.CUTTING,
                new SingleRecipeInput(inventory.getStackInSlot(0)),
                saw.getLevel(),
                saw)) {
            if (TieredRecipeBindings.get(candidate.value()) == null
                    || !(candidate.value() instanceof CuttingRecipe)
                    || AllRecipeTypes.shouldIgnoreInAutomation(candidate)
                    || !filtering.test(candidate.value().getResultItem(saw.getLevel().registryAccess()))
                    || !seen.add(candidate.id())) {
                continue;
            }
            merged.add((RecipeHolder<? extends Recipe<?>>) (RecipeHolder<?>) candidate);
        }
        callback.setReturnValue(merged);
    }
}
