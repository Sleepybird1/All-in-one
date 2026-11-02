package dev.godpc.industrialcolonies.mixin.jei;

import com.simibubi.create.compat.jei.category.CreateRecipeCategory;
import dev.godpc.industrialcolonies.TieredRecipeCatalog;
import dev.godpc.industrialcolonies.client.jei.JeiExactMachineUsesProbe;
import dev.godpc.industrialcolonies.client.jei.JeiMachineVisualContext;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeIngredientRole;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Adds an unambiguous per-recipe machine cue and scopes the animation context. */
@Mixin(value = CreateRecipeCategory.class, remap = false)
public abstract class CreateRecipeCategoryMachineMixin {
    @Inject(
            method = "setRecipe(Lmezz/jei/api/gui/builder/IRecipeLayoutBuilder;"
                    + "Lnet/minecraft/world/item/crafting/RecipeHolder;"
                    + "Lmezz/jei/api/recipe/IFocusGroup;)V",
            at = @At("HEAD")
    )
    private void industrialColonies$showRequiredMachine(
            IRecipeLayoutBuilder layout,
            RecipeHolder<? extends Recipe<?>> holder,
            IFocusGroup focuses,
            CallbackInfo ci
    ) {
        Recipe<?> recipe = holder.value();
        TieredRecipeCatalog.Machine machine = JeiMachineVisualContext.machine(recipe);
        ItemStack stack = JeiMachineVisualContext.machineStack(recipe);
        if (machine == null || stack.isEmpty()) {
            return;
        }

        JeiExactMachineUsesProbe.observeLayout(recipe, machine);

        // JEI's Uses key creates an INPUT focus before its CATALYST focus. Add
        // the exact machine as a lookup-only input so pressing Uses on, for
        // example, the Copper Press resolves only recipes bound to that press.
        // This is deliberately per recipe; registering a category catalyst
        // would incorrectly expose every generic recipe in the Create category.
        layout.addInvisibleIngredients(RecipeIngredientRole.INPUT)
                .addItemStack(stack);

        layout.addSlot(RecipeIngredientRole.CATALYST, 4, 4)
                .setStandardSlotBackground()
                .addItemStack(stack)
                .setSlotName("industrial_colonies_required_machine")
                .addRichTooltipCallback((slot, tooltip) -> {
                    tooltip.add(Component.literal("Required machine: " + machine.displayName())
                            .withStyle(ChatFormatting.GOLD));
                    tooltip.add(Component.literal("This recipe runs only in this exact machine.")
                            .withStyle(ChatFormatting.DARK_GRAY));
                });
    }

    @Inject(
            method = "draw(Lnet/minecraft/world/item/crafting/RecipeHolder;"
                    + "Lmezz/jei/api/gui/ingredient/IRecipeSlotsView;"
                    + "Lnet/minecraft/client/gui/GuiGraphics;DD)V",
            at = @At("HEAD")
    )
    private void industrialColonies$beginMachineDrawing(
            RecipeHolder<? extends Recipe<?>> holder,
            IRecipeSlotsView slots,
            GuiGraphics graphics,
            double mouseX,
            double mouseY,
            CallbackInfo ci
    ) {
        JeiMachineVisualContext.push(holder.value());
    }

    @Inject(
            method = "draw(Lnet/minecraft/world/item/crafting/RecipeHolder;"
                    + "Lmezz/jei/api/gui/ingredient/IRecipeSlotsView;"
                    + "Lnet/minecraft/client/gui/GuiGraphics;DD)V",
            at = @At("RETURN")
    )
    private void industrialColonies$endMachineDrawing(
            RecipeHolder<? extends Recipe<?>> holder,
            IRecipeSlotsView slots,
            GuiGraphics graphics,
            double mouseX,
            double mouseY,
            CallbackInfo ci
    ) {
        JeiMachineVisualContext.pop();
    }
}
