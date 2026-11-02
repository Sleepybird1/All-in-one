package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.processing.sequenced.SequencedAssemblyRecipe;
import com.simibubi.create.content.processing.recipe.ProcessingRecipe;
import dev.godpc.industrialcolonies.CreateMachineContext;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import dev.godpc.industrialcolonies.TieredRecipeBindings;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

import java.util.List;
import java.util.function.Predicate;

/** Authorizes a Sequenced Assembly parent before Create extracts its next nested step. */
@Mixin(SequencedAssemblyRecipe.class)
public abstract class SequencedAssemblyRuntimeMixin {
    @Redirect(
            method = "getRecipe(Lnet/minecraft/world/level/Level;Lnet/minecraft/world/item/ItemStack;"
                    + "Lnet/minecraft/world/item/crafting/RecipeType;Ljava/lang/Class;)Ljava/util/Optional;",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/simibubi/create/content/processing/recipe/ProcessingRecipe;getType()"
                            + "Lnet/minecraft/world/item/crafting/RecipeType;"
            )
    )
    private static RecipeType<?> industrialColonies$matchBoundSingleStepType(
            ProcessingRecipe<?, ?> recipe,
            Level level,
            ItemStack item,
            RecipeType<?> requestedStepType,
            Class<?> requestedStepClass
    ) {
        return compatibleStepType(recipe, requestedStepType);
    }

    @Redirect(
            method = "getRecipes(Lnet/minecraft/world/level/Level;Lnet/minecraft/world/item/ItemStack;"
                    + "Lnet/minecraft/world/item/crafting/RecipeType;Ljava/lang/Class;"
                    + "Ljava/util/function/Predicate;)Ljava/util/List;",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/simibubi/create/content/processing/recipe/ProcessingRecipe;getType()"
                            + "Lnet/minecraft/world/item/crafting/RecipeType;"
            )
    )
    private static RecipeType<?> industrialColonies$matchBoundStepListType(
            ProcessingRecipe<?, ?> recipe,
            Level level,
            ItemStack item,
            RecipeType<?> requestedStepType,
            Class<?> requestedStepClass,
            Predicate<?> stepPredicate
    ) {
        return compatibleStepType(recipe, requestedStepType);
    }

    @SuppressWarnings("rawtypes")
    @Redirect(
            method = "getRecipe(Lnet/minecraft/world/level/Level;Lnet/minecraft/world/item/ItemStack;"
                    + "Lnet/minecraft/world/item/crafting/RecipeType;Ljava/lang/Class;)Ljava/util/Optional;",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/item/crafting/RecipeManager;getAllRecipesFor("
                            + "Lnet/minecraft/world/item/crafting/RecipeType;)Ljava/util/List;"
            )
    )
    private static List industrialColonies$allowedParentsForSingleStep(
            RecipeManager manager,
            RecipeType<?> ignoredType,
            Level level,
            ItemStack stack,
            RecipeType<?> requestedStepType,
            Class<?> requestedStepClass
    ) {
        return CreateRecipeStageGate.allowedSequencedAssemblies(level);
    }

    @SuppressWarnings("rawtypes")
    @Redirect(
            method = "getRecipes(Lnet/minecraft/world/level/Level;Lnet/minecraft/world/item/ItemStack;"
                    + "Lnet/minecraft/world/item/crafting/RecipeType;Ljava/lang/Class;"
                    + "Ljava/util/function/Predicate;)Ljava/util/List;",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/item/crafting/RecipeManager;getAllRecipesFor("
                            + "Lnet/minecraft/world/item/crafting/RecipeType;)Ljava/util/List;"
            )
    )
    private static List industrialColonies$allowedParentsForStepList(
            RecipeManager manager,
            RecipeType<?> ignoredType,
            Level level,
            ItemStack stack,
            RecipeType<?> requestedStepType,
            Class<?> requestedStepClass,
            Predicate<?> stepPredicate
    ) {
        return CreateRecipeStageGate.allowedSequencedAssemblies(level);
    }

    /**
     * Create asks for a native family type when resolving the next assembly
     * step. A bound Pressing, Deploying, Cutting, or Filling step advertises
     * its hidden exact-machine type, so expose the requested base type only
     * while the current processing block is the machine selected by that
     * binding.
     */
    private static RecipeType<?> compatibleStepType(
            ProcessingRecipe<?, ?> recipe,
            RecipeType<?> requestedStepType
    ) {
        RecipeType<?> actualType = recipe.getType();
        TieredRecipeBindings.Binding binding = TieredRecipeBindings.get(recipe);
        if (binding == null || binding.family() == null) {
            return actualType; // Native Create steps keep their original comparison semantics.
        }

        RecipeType<?> baseType = binding.family().baseType().getType();
        boolean machineMatches = CreateRecipeStageGate.machineMatches(
                binding, CreateMachineContext.current());
        if (baseType == requestedStepType && machineMatches) {
            return requestedStepType;
        }

        // Defensive path for a direct lookup by the hidden type: a mismatched
        // block must never gain access merely because actual == requested.
        if (actualType == requestedStepType && !machineMatches) {
            return baseType;
        }
        return actualType;
    }
}
