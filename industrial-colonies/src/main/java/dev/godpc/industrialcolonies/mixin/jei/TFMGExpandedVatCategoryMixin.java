package dev.godpc.industrialcolonies.mixin.jei;

import com.drmangotea.tfmg.recipes.VatMachineRecipe;
import com.drmangotea.tfmg.recipes.jei.ChemicalVatCategory;
import com.drmangotea.tfmg.registry.TFMGGuiTextures;
import com.simibubi.create.compat.jei.category.CreateRecipeCategory;
import com.simibubi.create.content.processing.recipe.HeatCondition;
import com.simibubi.create.foundation.gui.AllGuiTextures;
import dev.godpc.industrialcolonies.ExpandedVatJeiLayout;
import dev.godpc.industrialcolonies.ExpandedVatJeiSupport;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.recipe.IFocusGroup;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.List;

/** Expanded feed layout plus exact attachment artwork for both native and expanded recipes. */
@Mixin(value = ChemicalVatCategory.class, remap = false)
public abstract class TFMGExpandedVatCategoryMixin extends CreateRecipeCategory<VatMachineRecipe> {
    @Shadow private void drawVatTypes(List<String> types, GuiGraphics graphics) { throw new AssertionError(); }
    @Shadow private void renderHeated(HeatCondition heat, GuiGraphics graphics) { throw new AssertionError(); }
    @Unique private IDrawable industrialColonies$expandedBackground;

    protected TFMGExpandedVatCategoryMixin(CreateRecipeCategory.Info<VatMachineRecipe> info) { super(info); }

    /** Override the inherited category accessor; all other Create/TFMG categories keep their backgrounds. */
    @Override public IDrawable getBackground() {
        if (industrialColonies$expandedBackground == null)
            industrialColonies$expandedBackground = ExpandedVatJeiSupport.background(super.getBackground());
        return industrialColonies$expandedBackground;
    }

    /** Native small-recipe artwork uses contains(), drawing three graphite electrodes for any count. */
    @Inject(method = "drawSprites(Ljava/util/List;Lnet/minecraft/client/gui/GuiGraphics;)V",
            at = @At("HEAD"), cancellable = true)
    private void industrialColonies$countedNativeMachines(List<String> machines, GuiGraphics graphics,
                                                        CallbackInfo callback) {
        // Keep native fallback for malformed/unknown third-party setups; do not add a render exception.
        try { ExpandedVatJeiLayout.machineAttachments(machines); }
        catch (IllegalArgumentException invalid) { return; }
        ExpandedVatJeiSupport.drawMachines(machines, graphics);
        callback.cancel();
    }

    @Inject(method = "setRecipe(Lmezz/jei/api/gui/builder/IRecipeLayoutBuilder;Lcom/drmangotea/tfmg/recipes/VatMachineRecipe;Lmezz/jei/api/recipe/IFocusGroup;)V",
            at = @At("HEAD"), cancellable = true)
    private void industrialColonies$expandedSlots(IRecipeLayoutBuilder builder, VatMachineRecipe recipe,
                                                 IFocusGroup focuses, CallbackInfo callback) {
        if (!ExpandedVatJeiSupport.expanded(recipe)) return;
        ExpandedVatJeiSupport.setRecipe(builder, recipe);
        callback.cancel();
    }

    @Inject(method = "draw(Lcom/drmangotea/tfmg/recipes/VatMachineRecipe;Lmezz/jei/api/gui/ingredient/IRecipeSlotsView;Lnet/minecraft/client/gui/GuiGraphics;DD)V",
            at = @At("HEAD"), cancellable = true)
    private void industrialColonies$expandedDrawing(VatMachineRecipe recipe, IRecipeSlotsView slots,
                                                   GuiGraphics graphics, double mouseX, double mouseY,
                                                   CallbackInfo callback) {
        if (!ExpandedVatJeiSupport.expanded(recipe)) return;
        graphics.pose().pushPose();
        try {
            graphics.pose().translate(ExpandedVatJeiLayout.VAT_X, 0, 0);
            TFMGGuiTextures.VAT.render(graphics, 0, 24);
            // Preserve native vat/heat artwork; the attachment helper honors exact mixed counts.
            drawVatTypes(recipe.allowedVatTypes, graphics);
            ExpandedVatJeiSupport.drawMachines(recipe.machines, graphics);
            renderHeated(recipe.getRequiredHeat(), graphics);
        } finally { graphics.pose().popPose(); }
        var font = Minecraft.getInstance().font;
        graphics.drawString(font, "Item feed", 4, 4, 0xFFCCCCCC, false);
        if (!recipe.getFluidIngredients().isEmpty())
            graphics.drawString(font, "Fluid feed", 4, 100, 0xFFCCCCCC, false);
        graphics.drawString(font, "Products", 268, 4, 0xFFCCCCCC, false);
        AllGuiTextures.JEI_ARROW.render(graphics, 124, 61);
        AllGuiTextures.JEI_ARROW.render(graphics, 245, 61);
        callback.cancel();
    }
}
