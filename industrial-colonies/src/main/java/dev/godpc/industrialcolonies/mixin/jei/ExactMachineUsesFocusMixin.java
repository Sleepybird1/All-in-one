package dev.godpc.industrialcolonies.mixin.jei;

import dev.godpc.industrialcolonies.client.jei.ExactMachineRecipeLookup;
import dev.godpc.industrialcolonies.client.jei.JeiExactMachineUsesProbe;
import mezz.jei.api.ingredients.ITypedIngredient;
import mezz.jei.api.recipe.IFocus;
import mezz.jei.api.recipe.IFocusFactory;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.gui.util.FocusUtil;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;

/** Keeps JEI Uses lookups for an exact routed machine recipe-scoped. */
@Mixin(value = FocusUtil.class, remap = false)
public abstract class ExactMachineUsesFocusMixin {
    @Shadow
    @Final
    private IFocusFactory focusFactory;

    @Inject(
            method = "createFocuses(Lmezz/jei/api/ingredients/ITypedIngredient;"
                    + "Ljava/util/List;)Ljava/util/List;",
            at = @At("HEAD"),
            cancellable = true
    )
    private void industrialColonies$keepExactMachineUsesRecipeScoped(
            ITypedIngredient<?> ingredient,
            List<RecipeIngredientRole> roles,
            CallbackInfoReturnable<List<IFocus<?>>> cir
    ) {
        // JEI's Uses key supplies exactly INPUT + CATALYST. Encased-machine
        // addons also register their machines as whole-category catalysts, so
        // retaining the CATALYST focus would union every native recipe in the
        // Create category back into the otherwise exact per-recipe lookup.
        if (roles.size() != 2
                || !roles.contains(RecipeIngredientRole.INPUT)
                || !roles.contains(RecipeIngredientRole.CATALYST)
                || !ExactMachineRecipeLookup.isExactMachineItem(ingredient)) {
            return;
        }

        ItemStack stack = ingredient.getItemStack().orElse(ItemStack.EMPTY);
        try {
            JeiExactMachineUsesProbe.observeUsesFocusRewrite(stack);
        } catch (RuntimeException | LinkageError ignored) {
            // Diagnostics must never prevent the actual lookup correction.
        }

        cir.setReturnValue(List.of(
                focusFactory.createFocus(RecipeIngredientRole.INPUT, ingredient)
        ));
    }
}
