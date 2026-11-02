package dev.godpc.industrialcolonies.mixin.jei;

import dev.godpc.industrialcolonies.client.jei.ExactMachineRecipeLookup;
import dev.godpc.industrialcolonies.client.jei.JeiExactMachineUsesProbe;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.library.recipes.RecipeManagerInternal;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.stream.Stream;

/** Removes ordinary ingredient consumers from a non-base machine's Uses page. */
@Mixin(value = RecipeManagerInternal.class, remap = false)
public abstract class ExactMachineRecipeLookupMixin {
    @Inject(
            method = "getRecipesStream(Lmezz/jei/api/recipe/RecipeType;"
                    + "Lmezz/jei/api/recipe/IFocusGroup;Z)Ljava/util/stream/Stream;",
            at = @At("RETURN"),
            cancellable = true
    )
    private <T> void industrialColonies$filterExactMachineUsesRecipes(
            RecipeType<T> recipeType,
            IFocusGroup focuses,
            boolean includeHidden,
            CallbackInfoReturnable<Stream<T>> cir
    ) {
        var machineUses = ExactMachineRecipeLookup.machineUses(focuses);
        if (machineUses.isEmpty()) {
            return;
        }

        var lookup = machineUses.get();
        if (lookup.includesCatalyst()) {
            try {
                JeiExactMachineUsesProbe.observeCombinedUsesFilter(lookup.machineId());
            } catch (RuntimeException | LinkageError ignored) {
                // Diagnostics must never prevent the actual lookup correction.
            }
        }

        // RecipeManagerInternal also calls this path while deciding which
        // category tabs are visible, so empty crafting/upgrade tabs disappear
        // alongside their unbound recipes.
        cir.setReturnValue(cir.getReturnValue().filter(
                candidate -> ExactMachineRecipeLookup.isBoundTo(candidate, lookup.machineId())
        ));
    }
}
